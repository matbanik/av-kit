---
date: "2026-11-18"
project: "2026-11-17-ui-small-fixes"
meu: "MEU-158"
status: "complete"
action_required: "VALIDATE_AND_APPROVE"
template_version: "2.2"
verbosity: "standard"
plan_source: "docs/execution/plans/2026-11-17-ui-small-fixes/implementation-plan.md"
build_plan_section: "docs/build-plan/06-gui.md §F1 help waits for the page (residual) (MEU-158, matrix 6.22)"
agent: "claude-code-local (Claude Opus 5.5)"
reviewer: "codex (H1-7 execution review)"
predecessor: "2026-11-17-video-tail-frame-MEU-160-handoff.md"
---

# Handoff: 2026-11-17-ui-small-fixes-MEU-158-handoff

> **Status**: `complete`
> **Action Required**: `VALIDATE_AND_APPROVE`

---

## Scope

**MEU**: MEU-158 F1 help waits for the page (phase 6, band P2, matrix 6.22), registered from `HELP-F1-BEFORE-LAZY-MOUNT-LOST` (triage D-1128).
**Build Plan Section**: `docs/build-plan/06-gui.md` §F1 help waits for the page (residual).
**Predecessor**: [2026-11-17-video-tail-frame-MEU-160-handoff.md](2026-11-17-video-tail-frame-MEU-160-handoff.md), Session 93, committed as `9867e51`. Session 94 is the fourth session run of the 2026-11-17 value triage grouping (`.agent/context/grouping/2026-11-17-value-triage-session-grouping.md`), run from `9867e51`. Its other handoffs: [MEU-159](2026-11-17-ui-small-fixes-MEU-159-handoff.md) and [the preview fix](2026-11-17-ui-small-fixes-handoff.md).

- **One mechanism (`HELD_REQUEST`, `CURRENT_ROUTE`, D-1175).** `createHeldRequest(stillHome)` (`ui/src/renderer/src/lib/shell-nav.ts:36`) keeps one outstanding request per instance in renderer memory: a press for the key already outstanding joins it, a press for another key replaces it, a `hashchange` off its key drops it, `settle` holds a request no receiver took, and `take` clears it once. `currentRoute()` (`:14`) is the hash without `#` and query, or `'/'`.
- **Ctrl+O on the helper (`BROWSE_HOLD`, D-1175).** `convert-commands.ts:356` keeps its request in one instance, `createHeldRequest((key) => key === '/convert' && isConvertHome())`; `deliverPaletteBrowse`, `takeHeldBrowse`, `CONVERT_BROWSE_EVENT` and `isConvertHome` keep their exports and behaviour. Its unit pins passed unchanged (row 2), and `convert-browse-mount.test.ts` and the Ctrl+O test at `convert-queue.test.ts:1568` passed 20 of 20 on it (row 7).
- **F1 carries its route (`HELP_HOLD`, `HELP_ROUTE_SCOPE`, D-1176).** `HELP_COMMANDS.toggle()` (`settings-commands.ts:35-43`) begins a request for `currentRoute()`, dispatches a cancelable `av-kit:help:toggle-local` with `detail.route`, and settles it at once. A `HelpCard` whose `HELP_FEATURE_ROUTE[feature]` (`settings-commands.ts:14-22`) equals the route calls `preventDefault` and toggles; a card on another route ignores it, so the Downloader card the router still shows while Convert loads never toggles. A press no card took is held, a second press while it is held joins it, and a detail-less event toggles every card as before.
- **Take on mount (`HELP_TAKE_ON_MOUNT`).** The card adds its listener and then takes an F1 held for its own route, toggling once (`HelpCard.tsx:89-91`, `takeHeldHelpToggle` at `settings-commands.ts:28`). Under StrictMode's second effect run nothing is left to take. Leaving the route drops a held F1 (`HELP_DROP`).
- **Records.** MEU-158 is `ready_for_review` with this plan folder; `HELP-F1-BEFORE-LAZY-MOUNT-LOST` is `resolved` with `meu_links: [MEU-158]`; 06 carries the `Delivered (Session 94)` note; grouping row 94 reads `executed (Session 94)`.

**What Mat sees.** Pressing F1 right after clicking Convert or Capture, before the page has appeared, now opens that page's help panel when it appears, every time. Two quick presses open it once, not open-and-close. Pressing F1 and then leaving for another page before it appears does nothing on the next visit. The Downloader help panel no longer opens by mistake when F1 is pressed while Convert or Capture loads. F1 on a page that is already showing works as before. Ctrl+O on Convert behaves exactly as before.

**Plan:** [implementation-plan.md](../../../docs/execution/plans/2026-11-17-ui-small-fixes/implementation-plan.md) §Single-statement contracts. **Execution authorization:** `USER_EXPLICIT`, 2026-11-17 ("orchestrate the plan creation for all sessions and proceed with execution for each"), `plan_to_exec_gate: human`; the plan review approved at round 2 (`.agent/context/handoffs/2026-11-17-ui-small-fixes-plan-critical-review.md`). Receipts named by file name alone are in the session's receipts folder (the `ui-small-fixes` folder under `RECEIPTS_DIR`).

---

## Acceptance Criteria

| AC | Type | Description | Source | Test(s) | Status |
|----|------|-------------|--------|---------|--------|
| AC-158.1 | unit | `createHeldRequest(stillHome)`: `begin` returns a token and a second `begin` for the same key joins (`null`); `settle(token, true)` holds; `take` is `true` once, then `false`; `settle(token, false)` clears | Local Canon (06 Held, Once, Shared rows; `HELD_REQUEST`) | `ui/tests/unit/help-f1-hold.test.tsx:68` | ✅ |
| AC-158.2 | unit | The helper's edges: a `hashchange` off the key clears it and removes the listener; `begin` for another key replaces it; a stale `settle` holds nothing; `currentRoute()` gives `'/'` and `'/convert'` | Local Canon (06 Once row; `HELP_DROP`, `CURRENT_ROUTE`) | `ui/tests/unit/help-f1-hold.test.tsx:85` | ✅ |
| AC-158.3 | unit | F1 on `#/convert` with no card, then a StrictMode render of the converter card: expanded after one flush, and nothing left to take | Local Canon (06 Held row) | `ui/tests/unit/help-f1-hold.test.tsx:116` | ✅ |
| AC-158.4 | unit | Two F1 before the mount, then the StrictMode render: expanded (one toggle) | Local Canon (06 Once row) | `ui/tests/unit/help-f1-hold.test.tsx:125` | ✅ |
| AC-158.5 | unit | F1 on `#/convert`, the hash leaves and comes back, then the render: collapsed, nothing to take | Local Canon (06 Once row) | `ui/tests/unit/help-f1-hold.test.tsx:135` | ✅ |
| AC-158.6 | unit | `HELP_ROUTE_SCOPE`: a downloader card ignores an F1 routed to `/convert`, a converter card rendered next reads expanded, a detail-less event toggles both, and a downloader card never takes an F1 held for `/convert` | Local Canon (06 Held row); D-1176 | `ui/tests/unit/help-f1-hold.test.tsx:146` | ✅ |
| AC-158.7 | unit (guard) | A mounted converter card toggles at once and nothing is held; a second F1 collapses it | Local Canon (06 Held row) | `ui/tests/unit/help-f1-hold.test.tsx:180` | ✅ passed at Red (guard) |
| AC-158.8 | e2e | Convert's chunk held back 1 500 ms; F1 before the page mounts: Convert's help reads expanded, the Downloader key is not `'expanded'` | Local Canon (06 Tests row); D-1176 | `ui/tests/e2e/help-f1-mount.test.ts:224` | ✅ |
| AC-158.9 | e2e | The same on Capture | As AC-158.8 | `ui/tests/e2e/help-f1-mount.test.ts:236` | ✅ |
| AC-158.10 | e2e | Two F1 while Convert loads: expanded once | Local Canon (06 Once row) | `ui/tests/e2e/help-f1-mount.test.ts:248` | ✅ |
| AC-158.11 | e2e | F1 while Convert loads, then the Downloader, then Convert again: collapsed, and the Downloader key not `'expanded'` | Local Canon (06 Once row) | `ui/tests/e2e/help-f1-mount.test.ts:260` | ✅ (recorded at Red: failed) |
| AC-158.12 | e2e (guard) | F1 on the mounted Convert page toggles at once, and again | Local Canon (06 Held row) | `ui/tests/e2e/help-f1-mount.test.ts:276` | ✅ passed at Red (guard) |
| AC-158.13 | check | Row 7: each `help-f1-mount.test.ts` test 20 of 20, `convert-browse-mount.test.ts` 20 of 20 per test, the Ctrl+O test at `convert-queue.test.ts:1568` 20 of 20; `help-search.spec.ts` and `keyboard-shortcuts.test.ts` once | Mat 2026-11-16; Local Canon (06 Tests row) | row 7 `us-row7-repeat.txt`; gate `e2e-*` | ✅ 20 of 20 each |
| AC-158.14 | check | Row 2: the help, shortcut, palette and Convert unit pins pass unchanged, with their row-0 hashes | Local Canon (06 Shared row) | row 2 `us-158-green.txt`, `us-158-immutable.txt`; gate `meu-158-unit` | ✅ |
| AC-157.8 to AC-157.11 (cross-ref, quoted) | guard | Session 89's MEU-157 tests in `ui/tests/e2e/convert-browse-mount.test.ts` (Ctrl+O while the Convert chunk loads opens one picker), unedited; their titles begin `AC-157.8 ` to `AC-157.11 `, and this handoff quotes them only from `us-row7-repeat.txt`. They are not criteria of this plan | Local Canon (§Test pins; D-1175 `BROWSE_HOLD` behaviour kept) | row 7 `us-row7-browse-r20.txt`; gate `e2e-browse-mount` | ✅ 20 of 20 each |
| Help and shortcut pins (cross-ref) | guard | `ui/tests/unit/help-card.test.ts`, `convert-browse-hold.test.ts`, `convert-page.behavior.test.ts`, `convert-page.test.ts`, `convert-commands.test.ts`, `common-shortcuts.test.tsx`, `header-toggles.test.ts`, `palette-curation.test.tsx`, `gui-actions-audit.test.ts`, `capture-page.test.ts`, `shortcuts.test.ts`: no edit; `ui/tests/e2e/keyboard-shortcuts.test.ts:68` (F1 on a mounted page), `help-search.spec.ts` and the Ctrl+O test at `ui/tests/e2e/convert-queue.test.ts:1568` ("browses on Convert and is inert"): no edit | Local Canon (§Test pins) | row 2; row 7; gate `meu-158-unit`, `e2e-*` | ✅ |
| AC-159.1 to AC-159.7 (cross-ref) | reference | MEU-159, the Downloader Advanced gap: the measured cause and the hidden empty status wrapper; owned by `.agent/context/handoffs/2026-11-17-ui-small-fixes-MEU-159-handoff.md` (AC-159.1, AC-159.2, AC-159.3, AC-159.4, AC-159.5, AC-159.6, AC-159.7) | Local Canon (11 Cause, Collapsed and Expanded rows) | that handoff | n/a: not this handoff's |
| AC-1, AC-2, AC-3, AC-4 and AC-5 (cross-ref) | reference | The preview fix (no MEU, D-1130): the preview wrapper script, its package script and the proofs with `ELECTRON_RUN_AS_NODE` set and unset; owned by `.agent/context/handoffs/2026-11-17-ui-small-fixes-handoff.md` | Local Canon (D-1130, D-1178) | that handoff | n/a: not this handoff's |

<!-- CACHE BOUNDARY -->

---

## Evidence

### FAIL_TO_PASS

| Test | Red Output (hash/snippet) | Green Output | File:Line |
|------|---------------------------|--------------|-----------|
| AC-158.1 | `AssertionError: expected 'undefined' to be 'function' // Object.is equality` (`us-158-red.txt`, `Tests  6 failed | 1 passed (7)`) | Row 2: `Tests  202 passed (202)` (`us-158-green.txt`) | `ui/tests/unit/help-f1-hold.test.tsx:68` |
| AC-158.2 | `AssertionError: expected 'undefined' to be 'function' // Object.is equality` (`us-158-red.txt`, `Tests  6 failed | 1 passed (7)`) | Row 2: `Tests  202 passed (202)` (`us-158-green.txt`) | `ui/tests/unit/help-f1-hold.test.tsx:85` |
| AC-158.3 | `AssertionError: expected 'undefined' to be 'function' // Object.is equality` (`us-158-red.txt`, `Tests  6 failed | 1 passed (7)`) | Row 2: `Tests  202 passed (202)` (`us-158-green.txt`) | `ui/tests/unit/help-f1-hold.test.tsx:116` |
| AC-158.4 | `AssertionError: expected 'undefined' to be 'function' // Object.is equality` (`us-158-red.txt`, `Tests  6 failed | 1 passed (7)`) | Row 2: `Tests  202 passed (202)` (`us-158-green.txt`) | `ui/tests/unit/help-f1-hold.test.tsx:125` |
| AC-158.5 | `AssertionError: expected 'undefined' to be 'function' // Object.is equality` (`us-158-red.txt`, `Tests  6 failed | 1 passed (7)`) | Row 2: `Tests  202 passed (202)` (`us-158-green.txt`) | `ui/tests/unit/help-f1-hold.test.tsx:135` |
| AC-158.6 | `AssertionError: expected 'undefined' to be 'function' // Object.is equality` (`us-158-red.txt`, `Tests  6 failed | 1 passed (7)`) | Row 2: `Tests  202 passed (202)` (`us-158-green.txt`) | `ui/tests/unit/help-f1-hold.test.tsx:146` |
| AC-158.8 | `Expected: "true"`, `Received: "false"` (`us-158-red-e2e.txt`, `4 failed`) | Row 2: `5 passed (28.1s)` (`us-158-green-e2e.txt`) | `ui/tests/e2e/help-f1-mount.test.ts:224` |
| AC-158.9 | `Expected: "true"`, `Received: "false"` (`us-158-red-e2e.txt`, `4 failed`) | Row 2: `5 passed (28.1s)` (`us-158-green-e2e.txt`) | `ui/tests/e2e/help-f1-mount.test.ts:236` |
| AC-158.10 | `Expected: "true"`, `Received: "false"` (`us-158-red-e2e.txt`, `4 failed`) | Row 2: `5 passed (28.1s)` (`us-158-green-e2e.txt`) | `ui/tests/e2e/help-f1-mount.test.ts:248` |
| AC-158.11 (recorded at Red, not required) | `Expected: not "expanded"` (`us-158-red-e2e.txt`; `AC-158.11 at Red (recorded): False`, `us-158-red-e2e-hashes.txt`) | Row 2: `5 passed (28.1s)` (`us-158-green-e2e.txt`) | `ui/tests/e2e/help-f1-mount.test.ts:260` |

AC-158.7 and AC-158.12 passed at Red and are guards (`us-158-red-hashes.txt`, `us-158-red-e2e-hashes.txt`); AC-158.13 and AC-158.14 are checks. AC-158.1 to AC-158.6 failed by assertion on `typeof … === 'function'`, never by a missing export or a module error (Session 52 RULE-4).

- **Row 0 baseline** (`us-baseline.txt`): `baseline: all steps exit 0`, `eol-check: 31 scope path(s), 0 problem(s)`, `baseline-scope.json 58 paths; 7 absent`, `baseline-dirty.txt 17 paths, 5 foreign`. UI Vitest at base: `Test Files  142 passed (142)`, `Tests  1619 passed (1619)` (`us-base-ui.txt`).
- **Row 1 Red** (`us-158-red.txt`): `Test Files  1 failed (1)`, `Tests  6 failed | 1 passed (7)`; `red-check: 1 receipt(s), 6 required test(s), 0 problem(s)` (`us-158-red-check.txt`). The guard alone: `Tests  1 passed | 6 skipped (7)` (`us-158-red-guard.txt`); `AC-158.7 guard, 1 passed: True CR in the new file: False` (`us-158-red-hashes.txt`).
- **Row 1a chunk probe (D-1179)** (`us-1a-probe.txt`, `us-1a-probe-check.txt`; load 17.3 %, `us-1a-load.txt`). The two `S94-PROBE` lines: convert `"delayed":1,"absentAt200ms":true,"downloaderCardPresent":true,"mountedMs":1626,"mounted":true`; capture `"delayed":1,"absentAt200ms":true,"downloaderCardPresent":true,"mountedMs":1613,"mounted":true`. The check: `pages good: {'convert': True, 'capture': True}`, `Downloader card present while loading: {'convert': True, 'capture': True}`, `1 passed: True chunk errors: [] probe file absent: True copy kept: True`. So the 1 500 ms hold works on both chunks, neither page is mounted 200 ms after the click, and the Downloader card is still in the DOM while each loads, which is the case `HELP_ROUTE_SCOPE` exists for.
- **Row 1b Red E2E** (`us-158-red-e2e.txt`; load 4.1 %): `4 failed`, `1 passed (29.3s)`; AC-158.8 to AC-158.10 `Expected: "true"` / `Received: "false"`, AC-158.11 `Expected: not "expanded"`; `red-check: 1 receipt(s), 3 required test(s), 0 problem(s)` (`us-158-red-e2e-check.txt`); `AC-158.12 guard passing at Red: True AC-158.11 at Red (recorded): False unhandled rejection: False CR in the new file: False` (`us-158-red-e2e-hashes.txt`).
- **Row 2 Green** (`us-158-green.txt`): `Test Files  12 passed (12)`, `Tests  202 passed (202)`; E2E `5 passed (28.1s)` (`us-158-green-e2e.txt`; load 7.5 %); `test-side files changed since Red: [] pin files changed since row 0: []` (`us-158-immutable.txt`); `eol-check: 31 scope path(s), 0 problem(s)` (`us-158-eol.txt`); types and lint clean (`us-158-types.txt`, `us-158-lint.txt`).
- **Row 7 repeats** (`us-row7-repeat.txt`): `help-f1-mount ok counts (of 20): {'AC-158.8': 20, 'AC-158.9': 20, 'AC-158.10': 20, 'AC-158.11': 20, 'AC-158.12': 20}`; `browse-mount ok counts (of 20): {'AC-157.8': 20, 'AC-157.9': 20, 'AC-157.10': 20, 'AC-157.11': 20}`; `Ctrl+O ok count (of 20): 20`; `suites clean: {'us-row7-help-search': True, 'us-row7-keyboard': True, 'us-row7-download-queue': True, 'us-row7-layout-primitives': True}`. The runs: `100 passed (9.2m)` (`us-row7-help-r20.txt`, load 18.9 %), `80 passed (9.1m)` (`us-row7-browse-r20.txt`, load 25.3 %), `20 passed (23.0s)` (`us-row7-ctrlo-r20.txt`, load 9.2 %), `3 passed (2.3s)` (`us-row7-help-search.txt`), `2 passed (2.1s)` (`us-row7-keyboard.txt`). The `AC-157.8` to `AC-157.11` keys are Session 89's test titles (cross-ref row above).
- **Row 8 records** (`us-issue-resolve.txt`): `decision logs read: 104 of 104`, `register sha256 before=01b1a5b0a6645256dbf2905c9136c8b8219332f761771f711cc992757cc15159`, `target sha256 after=0583a9c0d5837e6588d53a05595363154d880fcac1fb0db8d906a1cff056a251 CRLF=0 LF=5742`, `parsed fields changed: 15` (the three issues' `status`, `verification` (three fields), `resolution_path` and, for the two MEU issues, `meu_links`), `issue-resolve: 0 problem(s)`; `Rendered known-issues.md: 36 lines` (`us-issues-render.txt`); MEU-158 updated to `ready_for_review (updated: 2026-11-18)` (`us-status-158.txt`).
- **H1-1** (`task-unchecked.txt`): `unchecked implementation rows: []`.

### Commands Executed

```json
{"schema_version": "evidence.v1", "cwd": "P:/av-kit", "check_id": "us158-0-baseline", "command": "pwsh -NoProfile -File C:/Temp/av-kit/ui-small-fixes/run-row0.ps1 (task.md row 0's Validation cell without its uv sync step: baseline.ps1 records baseline.sha, the dirty list and hashes, the scope, line-ending and skip hashes, the cited anchors, the plan-local selftests and the base UI Vitest suite); receipts us-baseline.txt, us-base-ui.txt", "scope": "Row 0: the baseline at 9867e51 and the plan-local checkers", "phase": "static", "exit_code": 0, "result": "pass", "tested_state": "HEAD 9867e51 (baseline.sha) plus row 0", "output": "us-baseline.txt: baseline.sha 9867e51f0024a113de6a585b42b54695f1e4bccb; baseline-dirty.txt 17 paths, 5 foreign; baseline-scope.json 58 paths; 7 absent; baseline-skip-hashes.json 362 files under packages/, mcp-server/, tests/ and tools/; baseline-citations.txt 45 anchors; eol-check: 31 scope path(s), 0 problem(s); baseline: all steps exit 0. us-base-ui.txt: Test Files  142 passed (142); Tests  1619 passed (1619)."}
```

```json
{"schema_version": "evidence.v1", "cwd": "P:/av-kit", "check_id": "us158-1-red-unit", "command": "pwsh -NoProfile -File C:/Temp/av-kit/ui-small-fixes/run-row1.ps1 (task.md row 1's Validation cell: Vitest on help-f1-hold.test.tsx, red-check.py --require AC-158.1 to AC-158.6, the AC-158.7 guard run, the hash check); receipts us-158-red.txt, us-158-red-check.txt, us-158-red-guard.txt, us-158-red-hashes.txt", "scope": "AC-158.1 to AC-158.6 Red on the unchanged renderer; AC-158.7 guard passes at Red", "phase": "red", "exit_code": 0, "result": "pass", "tested_state": "HEAD 9867e51 (baseline.sha) plus rows 0 and 1", "output": "us-158-red.txt: Test Files  1 failed (1); Tests  6 failed | 1 passed (7); AC-158.1 to AC-158.6 each AssertionError: expected 'undefined' to be 'function' // Object.is equality. us-158-red-check.txt: red-check: 1 receipt(s), 6 required test(s), 0 problem(s). us-158-red-guard.txt: Tests  1 passed | 6 skipped (7). us-158-red-hashes.txt: AC-158.7 guard, 1 passed: True CR in the new file: False."}
```

```json
{"schema_version": "evidence.v1", "cwd": "P:/av-kit", "check_id": "us158-1a-chunk-probe", "command": "pwsh -NoProfile -File C:/Temp/av-kit/ui-small-fixes/run-row1a.ps1 (task.md row 1a's Validation cell: host-wait, the UI build, the S94-PROBE spec copied into ui/tests/e2e and removed after, the probe check); receipts us-1a-load.txt, us-1a-build.txt, us-1a-probe.txt, us-1a-probe-check.txt", "scope": "Row 1a (D-1179): the ConvertPage and CapturePage chunks held back 1 500 ms, checked before any Red E2E", "phase": "runtime", "exit_code": 0, "result": "pass", "tested_state": "HEAD 9867e51 (baseline.sha) plus rows 0 to 1a", "output": "load 17.3 %. us-1a-probe.txt: S94-PROBE {\"page\":\"convert\",\"delayed\":1,\"absentAt200ms\":true,\"downloaderCardPresent\":true,\"mountedMs\":1626,\"mounted\":true ...; S94-PROBE {\"page\":\"capture\",\"delayed\":1,\"absentAt200ms\":true,\"downloaderCardPresent\":true,\"mountedMs\":1613,\"mounted\":true .... us-1a-probe-check.txt: pages good: {'convert': True, 'capture': True}; Downloader card present while loading: {'convert': True, 'capture': True}; 1 passed: True chunk errors: [] probe file absent: True copy kept: True."}
```

```json
{"schema_version": "evidence.v1", "cwd": "P:/av-kit", "check_id": "us158-1b-red-e2e", "command": "pwsh -NoProfile -File C:/Temp/av-kit/ui-small-fixes/run-row1b.ps1 (task.md row 1b's Validation cell: host-wait, the UI build, Playwright on help-f1-mount.test.ts, red-check.py --require AC-158.8 to AC-158.10, the hash check); receipts us-158-red-e2e.txt, us-158-red-e2e-check.txt, us-158-red-e2e-hashes.txt", "scope": "AC-158.8 to AC-158.10 Red in real Electron; AC-158.11 recorded; AC-158.12 guard passes at Red", "phase": "red", "exit_code": 0, "result": "pass", "tested_state": "HEAD 9867e51 (baseline.sha) plus rows 0 to 1b", "output": "load 4.1 %. us-158-red-e2e.txt: 4 failed; 1 passed (29.3s); AC-158.8 to AC-158.10 Expected: \"true\" Received: \"false\"; AC-158.11 Expected: not \"expanded\". us-158-red-e2e-check.txt: red-check: 1 receipt(s), 3 required test(s), 0 problem(s). us-158-red-e2e-hashes.txt: AC-158.12 guard passing at Red: True AC-158.11 at Red (recorded): False unhandled rejection: False CR in the new file: False."}
```

```json
{"schema_version": "evidence.v1", "cwd": "P:/av-kit", "check_id": "us158-2-green", "command": "pwsh -NoProfile -File C:/Temp/av-kit/ui-small-fixes/run-row2.ps1 (task.md row 2's Validation cell: the MEU-158 unit set, typecheck, lint, host-wait, the build, Playwright on help-f1-mount.test.ts, the immutability and eol checks); receipts us-158-green.txt, us-158-types.txt, us-158-lint.txt, us-158-green-e2e.txt, us-158-immutable.txt, us-158-eol.txt", "scope": "AC-158.1 to AC-158.12 and AC-158.14 Green after HELD_REQUEST, BROWSE_HOLD, HELP_HOLD, HELP_ROUTE_SCOPE and HELP_TAKE_ON_MOUNT", "phase": "green", "exit_code": 0, "result": "pass", "tested_state": "HEAD 9867e51 (baseline.sha) plus rows 0 to 2", "output": "us-158-green.txt: Test Files  12 passed (12); Tests  202 passed (202). us-158-green-e2e.txt: 5 passed (28.1s) (load 7.5 %). us-158-immutable.txt: test-side files changed since Red: [] pin files changed since row 0: []. us-158-eol.txt: eol-check: 31 scope path(s), 0 problem(s). Types and lint clean."}
```

```json
{"schema_version": "evidence.v1", "cwd": "P:/av-kit", "check_id": "us158-7-repeats", "command": "pwsh -NoProfile -File C:/Temp/av-kit/ui-small-fixes/run-row7.ps1 (task.md row 7's Validation cell: host-wait before each run, Playwright --repeat-each 20 on help-f1-mount.test.ts, convert-browse-mount.test.ts and the convert-queue.test.ts:1568 test, help-search.spec.ts and keyboard-shortcuts.test.ts once, the repeat check); receipts us-row7-help-r20.txt, us-row7-browse-r20.txt, us-row7-ctrlo-r20.txt, us-row7-help-search.txt, us-row7-keyboard.txt, us-row7-repeat.txt", "scope": "AC-158.13: 20 of 20 runs per test, and the help and shortcut E2E suites once", "phase": "runtime", "exit_code": 0, "result": "pass", "tested_state": "HEAD 9867e51 (baseline.sha) plus rows 0 to 7", "output": "us-row7-help-r20.txt: 100 passed (9.2m) (load 18.9 %). us-row7-browse-r20.txt: 80 passed (9.1m) (load 25.3 %). us-row7-ctrlo-r20.txt: 20 passed (23.0s) (load 9.2 %). us-row7-help-search.txt: 3 passed (2.3s). us-row7-keyboard.txt: 2 passed (2.1s). us-row7-repeat.txt: help-f1-mount ok counts (of 20): {'AC-158.8': 20, 'AC-158.9': 20, 'AC-158.10': 20, 'AC-158.11': 20, 'AC-158.12': 20}; browse-mount ok counts (of 20): {'AC-157.8': 20, 'AC-157.9': 20, 'AC-157.10': 20, 'AC-157.11': 20}; Ctrl+O ok count (of 20): 20; suites clean: {'us-row7-help-search': True, 'us-row7-keyboard': True, 'us-row7-download-queue': True, 'us-row7-layout-primitives': True}."}
```

```json
{"schema_version": "evidence.v1", "cwd": "P:/av-kit", "check_id": "us158-8-records", "command": "python C:/Temp/av-kit/ui-small-fixes/write-set.py (issue-resolve-set.json, LF); python C:/Temp/av-kit/ui-small-fixes/row8-docs.py (the 06 and 11 Delivered notes and commands.md:80, CRLF kept, and grouping row 94, LF kept, by bytes); pwsh -NoProfile -File C:/Temp/av-kit/ui-small-fixes/run-row8.ps1 (task.md row 8's Validation cell: issue-resolve.py bound to the row-0 register hash, issue_triage.py render and render --check, meu_status.py update MEU-158 and MEU-159 ready_for_review --plan, the row 8 check)", "scope": "Row 8: the three issues resolved, MEU-158 and MEU-159 ready_for_review, the Delivered notes, COMMANDS_DOC and grouping row 94", "phase": "static", "exit_code": 0, "result": "pass", "tested_state": "HEAD 9867e51 (baseline.sha) plus rows 0 to 8", "output": "us-issue-resolve.txt: decision logs read: 104 of 104; register sha256 before=01b1a5b0a6645256dbf2905c9136c8b8219332f761771f711cc992757cc15159; target sha256 after=0583a9c0d5837e6588d53a05595363154d880fcac1fb0db8d906a1cff056a251 CRLF=0 LF=5742; parsed fields changed: 15; issue-resolve: 0 problem(s). us-issues-render.txt: Rendered known-issues.md: 36 lines. us-issues-render-check.txt: OK: known-issues.md is up-to-date. us-status-158.txt and us-status-159.txt: Updated to ready_for_review (updated: 2026-11-18). us-row8-check.txt: grouping LF: True; all three issues resolved."}
```

```json
{"schema_version": "evidence.v1", "cwd": "P:/av-kit", "check_id": "us158-h1-2-session-gate", "command": "pwsh -NoProfile -File C:/Temp/av-kit/ui-small-fixes/run-rowH1-2.ps1 (task.md row H1-2's Validation cell: rtk proxy pwsh -NoProfile -File docs/execution/plans/2026-11-17-ui-small-fixes/session-gate.ps1 *> C:/Temp/av-kit/ui-small-fixes/us-gate-h1.txt); step receipts us-D6-<step>.txt and us-D6-<step>-load.txt", "scope": "H1-2: the PROFILE D6 session gate, 31 steps from identity-before to identity-after: static checks, the three targeted unit sets, host-load, the full UI Vitest suite, the preview proof, the UI build, eight Electron E2E steps (each after a host-wait at or below 50 %), the state and issue renders; py-tests, py-types, openapi, mcp-* and e2e-other skipped with their reasons", "phase": "full", "exit_code": 0, "result": "pass", "fresh": true, "snapshot": false, "tested_state": "9867e51f0024a113de6a585b42b54695f1e4bccb+0fb04e34a3879c5f491b2eb6fc42782c63314539f0e05a2bc03cb8494d11c42e", "output": "us-gate-h1.txt: every step exit=0; session-gate: all steps exit 0. identity before and after: tested_state 9867e51f0024a113de6a585b42b54695f1e4bccb+0fb04e34a3879c5f491b2eb6fc42782c63314539f0e05a2bc03cb8494d11c42e. host-load: ran at 9.3 %. us-D6-ui-tests.txt: Test Files  144 passed (144); Tests  1628 passed (1628). us-D6-preview-proof.txt: window: yes (after 17 s; window), notice: yes, notice on stdout: no, left: 0, PASS: window opened, notice as expected, nothing left. E2E: e2e-help-f1-mount 5 passed (25.4s); e2e-browse-mount 4 passed (28.1s); e2e-ctrl-o 1 passed (1.1s); e2e-help-search 3 passed (2.1s); e2e-keyboard-shortcuts 2 passed (1.9s); e2e-advanced-gap 4 passed (12.7s); e2e-download-queue 26 passed (26.4s); e2e-layout-primitives 1 passed (982ms). OK: 29 row(s); changed paths: 46 outside scope: [] other sessions plan files skipped: 4; eol-check: 31 scope path(s), 0 problem(s); check_home_path: ok files=2671 allowlisted=60 nul=31; OK: known-issues.md is up-to-date."}
```

```json
{"schema_version": "evidence.v1", "cwd": "P:/av-kit", "check_id": "us158-h1-3-h1-4-closeout-checks", "command": "python C:/Temp/av-kit/ui-small-fixes/focus-entry.py (the Session 94 entry on top of .agent/context/current-focus.md, by bytes, CRLF kept); pwsh -NoProfile -File C:/Temp/av-kit/ui-small-fixes/run-rowH1-3.ps1 (meu_status.py render --check, meu_status.py get MEU-158 and MEU-159, the ready check); pwsh -NoProfile -File C:/Temp/av-kit/ui-small-fixes/run-rowH1-4.ps1 (task.md row H1-4's skip-basis check)", "scope": "H1-3 (current focus, the state render, MEU-158 and MEU-159 ready_for_review) and H1-4 (the Python, OpenAPI and MCP skip basis)", "phase": "static", "exit_code": 0, "result": "pass", "tested_state": "the H1-2 state plus H1-3's current-focus entry (identity.py excludes current-focus.md)", "output": "focus-entry: current-focus: bytes 89795 -> 91475 CRLF 221 -> 224 bare LF 0. us-render-check.txt: Drift check passed. us-h13-check.txt: ready_for_review: {'MEU-158': True, 'MEU-159': True}. skip-basis-check.txt: packages, mcp-server, tests or tools changes since row 0: []."}
```

### Quality Gate Results

| Step | Result (receipt) |
|------|------------------|
| Gate | `session-gate: all steps exit 0` (`us-gate-h1.txt`); 31 steps, each `exit=0` |
| Identity | `tested_state 9867e51f0024a113de6a585b42b54695f1e4bccb+0fb04e34a3879c5f491b2eb6fc42782c63314539f0e05a2bc03cb8494d11c42e`, equal before and after (`us-D6-identity-before.txt`, `us-D6-identity-after.txt`) |
| Task contract | `OK: 29 row(s)`; `2 row(s) exempt (view_file): H1-5, H2-1` (`us-D6-task-contract.txt`) |
| Scope | `changed paths: 46 outside scope: [] other sessions plan files skipped: 4`; `read-never-changed files: 36 mismatch: [] baseline-dirty hash mismatch: []`; `temporary probe files present: []`; `head moved (S4): False` (`us-D6-scope-paths.txt`) |
| Line endings | `eol-check: 31 scope path(s), 0 problem(s)` (`us-D6-line-endings.txt`) |
| Home path | `check_home_path: ok files=2671 allowlisted=60 nul=31` (`us-D6-home-path.txt`) |
| Selftests | `red-check selftest: 91 fixture(s) (22 positive, 69 negative), 0 wrong: []`; `eol-check selftest: 19 case(s), 0 wrong: []`; `preview-proof selftest: 0 failure(s)` (`us-D6-red-check-selftest.txt`, `us-D6-eol-check-selftest.txt`, `us-D6-preview-proof-selftest.txt`) |
| Static | `ui-types` and `ui-lint` exit 0; `node --check ui/scripts/electron-vite-preview.mjs exit 0` (`us-D6-scripts-syntax.txt`); `7 files already formatted` (`us-D6-py-format.txt`); `All checks passed!` (`us-D6-py-lint.txt`) |
| Targeted | `meu-158-unit` `Tests  202 passed (202)`; `meu-159-unit` `Tests  102 passed (102)`; `preview-unit` `Tests  4 passed (4)` |
| Host load | `host-load: ran at 9.3 %` (`us-D6-host-load.txt`); each Electron step waited first (`us-D6-<step>-load.txt`, D-1181) |
| UI, full | `Test Files  144 passed (144)`, `Tests  1628 passed (1628)` (`us-D6-ui-tests.txt`; row 0 had 142 files and 1619 tests, and the session adds two files with nine tests: seven in `help-f1-hold.test.tsx`, two in `preview-script.test.ts`) |
| Preview proof (AC-4) | `PASS: window opened, notice as expected, nothing left`, after `window: yes (after 17 s; window)` and `notice on stdout: no` (`us-D6-preview-proof.txt`; load 7.5 %) |
| UI build | exit 0 (`us-D6-ui-build.txt`) |
| Electron E2E | `e2e-help-f1-mount` `5 passed (25.4s)` (load 7.3 %); `e2e-browse-mount` `4 passed (28.1s)` (load 7.5 %); `e2e-ctrl-o` `1 passed (1.1s)` (load 8.0 %); `e2e-help-search` `3 passed (2.1s)` (load 8.0 %); `e2e-keyboard-shortcuts` `2 passed (1.9s)` (load 8.8 %); `e2e-advanced-gap` `4 passed (12.7s)` (load 8.0 %); `e2e-download-queue` `26 passed (26.4s)` (load 8.7 %); `e2e-layout-primitives` `1 passed (982ms)` (load 8.3 %); none with a failed, flaky or `unhandled rejection:` line |
| Registers | `OK: known-issues.md is up-to-date` (`us-D6-issues-render-check.txt`); the state render's drift check passed (`us-D6-state-render.txt`) |
| Skipped | `py-tests`, `py-types`, `openapi` and `mcp-types/mcp-build/mcp-tests/mcp-audit`, each printed with its reason (every file under `packages/`, `mcp-server/`, `tests/` and `tools/` keeps its row-0 hash; S10), and `e2e-other` (only the help toggle, the Convert browse hold, the Downloader status slot and the preview script changed, and their suites run; the clipboard specs never run) (`us-gate-h1.txt`) |
| H1-1 | `unchecked implementation rows: []` (`task-unchecked.txt`) |
| H1-3 | `current-focus: bytes 89795 -> 91475 CRLF 221 -> 224 bare LF 0`; the state render's drift check passed (`us-render-check.txt`); `ready_for_review: {'MEU-158': True, 'MEU-159': True}` (`us-h13-check.txt`) |
| H1-4 | `packages, mcp-server, tests or tools changes since row 0: []` (`skip-basis-check.txt`) |
| MEU-158 in the gate | `e2e-help-f1-mount` `5 passed (25.4s)`, `e2e-browse-mount` `4 passed (28.1s)`, `e2e-ctrl-o` `1 passed (1.1s)`, `e2e-help-search` `3 passed (2.1s)`, `e2e-keyboard-shortcuts` `2 passed (1.9s)`; `meu-158-unit` `Tests  202 passed (202)` |

---

## Changed Files

Counts are added / removed lines against `HEAD` `9867e51` (`git diff --numstat --ignore-cr-at-eol`); a new file's count is its line count. Line endings were measured as bytes (the gate's `line-endings` step: `eol-check: 31 scope path(s), 0 problem(s)`). The whole session's change set is listed in each handoff; the rows that are MEU-158's are `shell-nav.ts`, `convert-commands.ts`, `settings-commands.ts`, `HelpCard.tsx`, the two new MEU-158 test files and the 06 note.

| File | Change | Added / removed | Line endings |
|------|--------|-----------------|--------------|
| `ui/src/renderer/src/lib/shell-nav.ts` | `HELD_REQUEST` (`createHeldRequest` at `:36`), `CURRENT_ROUTE` (`currentRoute` at `:14`) | +72 / -0 | LF kept |
| `ui/src/renderer/src/features/converter/convert-commands.ts` | `BROWSE_HOLD` on one helper instance (`:356`); exports unchanged | +14 / -34 | CRLF kept |
| `ui/src/renderer/src/features/settings/settings-commands.ts` | `HELP_FEATURE_ROUTE` (`:14-22`), `HELP_HOLD` (`:25`), `takeHeldHelpToggle` (`:28`), the routed toggle (`:35-43`) | +30 / -1 | CRLF kept |
| `ui/src/renderer/src/components/help/HelpCard.tsx` | `HELP_ROUTE_SCOPE` (`:73-84`), `HELP_TAKE_ON_MOUNT` (`:89-91`), effect on `[feature]` | +25 / -3 | LF kept |
| `ui/src/renderer/src/features/downloader/DownloaderPage.tsx` | `STATUS_SLOT` at `:818` | +1 / -1 | MIXED kept; `:818` bare LF |
| `ui/scripts/electron-vite-dev.mjs` | `PREVIEW_WRAPPER`: `runElectronVite(command, notice, extra)` exported; `main()` calls it with `dev` | +16 / -5 | LF kept |
| `ui/scripts/electron-vite-preview.mjs` | `PREVIEW_WRAPPER`: `PREVIEW_NOTICE`, `previewArgs`, the entry call | new, 20 | LF |
| `ui/package.json` | `:18` `scripts.preview` | +1 / -1 | CRLF kept |
| `ui/tests/unit/dev-script.test.ts` | `PINS_NAMED`: `:64` only | +1 / -1 | LF kept |
| `ui/tests/unit/help-f1-hold.test.tsx` | AC-158.1 to AC-158.7 | new, 191 | LF |
| `ui/tests/e2e/help-f1-mount.test.ts` | AC-158.8 to AC-158.12 | new, 289 | LF |
| `ui/tests/e2e/downloader-advanced-gap.test.ts` | AC-159.2 to AC-159.5 | new, 370 | LF |
| `ui/tests/unit/preview-script.test.ts` | AC-1, AC-2 | new, 62 | LF |
| `.agent/context/meu-status.yaml` | MEU-158 and MEU-159 `ready_for_review` with this plan (`meu_status.py update`, row 8) | +10 / -10 | LF kept |
| `.agent/context/meu-registry.md`, `docs/BUILD_PLAN.md` | `meu_status.py render` | +2 / -2, +1 / -1 | LF |
| `.agent/context/known-issues.yaml` | `HELP-F1-BEFORE-LAZY-MOUNT-LOST`, `DOWNLOADER-ADVANCED-PANEL-GAP` and `UI-PREVIEW-ELECTRON-RUN-AS-NODE-SILENT` resolved (`issue-resolve.py`, row 8) | +15 / -6 | LF kept |
| `.agent/context/known-issues.md` | `issue_triage.py render` | +3 / -6 | LF |
| `docs/build-plan/06-gui.md` | the `Delivered (Session 94)` note before `## Validation Commands` (row 8) | +8 / -0 | CRLF kept |
| `docs/build-plan/11-page-layout.md` | the `Delivered (Session 94)` note before `## Supersession` (row 8) | +8 / -0 | CRLF kept |
| `.agent/docs/commands.md` | `:80`, the preview row (`COMMANDS_DOC`, row 8) | +1 / -1 | CRLF kept |
| `.agent/context/grouping/2026-11-17-value-triage-session-grouping.md` | row 94: `executed (Session 94)` and the plan folder | +1 / -1 | LF kept |
| `.agent/context/current-focus.md` | the Session 94 entry (H1-3) | +3 / -0 | CRLF kept |
| `docs/execution/plans/2026-11-17-ui-small-fixes/` | the plan (D-1181 in its YAML), task (row marks), the plan-local scripts, the row-0 records and `session-gate.ps1` | new folder | LF |
| `.agent/context/handoffs/2026-11-17-ui-small-fixes-MEU-158-handoff.md`, `-MEU-159-handoff.md`, `-handoff.md` | the three handoffs | new | LF |

**The F1 path.** `settings-commands.ts` (CRLF kept; shown without the CR):

```diff
+/** HELP_HOLD (MEU-158, D-1175, D-1176): an F1 that no card on its route received, held for that route. */
+const helpHold = createHeldRequest((key) => currentRoute() === key)
-    window.dispatchEvent(new CustomEvent('av-kit:help:toggle-local'))
+    const route = currentRoute()
+    const token = helpHold.begin(route)
+    if (token === null) {
+      return
+    }
+    const unreceived = window.dispatchEvent(
+      new CustomEvent('av-kit:help:toggle-local', { cancelable: true, detail: { route } }),
+    )
+    helpHold.settle(token, unreceived)
```

`HelpCard.tsx` (LF):

```diff
-    const onToggle = () => {
+    const route = HELP_FEATURE_ROUTE[feature]
+    const onToggle = (event: Event) => {
+      const detail: unknown = event instanceof CustomEvent ? event.detail : null
+      const target =
+        typeof detail === 'object' && detail !== null && 'route' in detail ? detail.route : undefined
+      if (target !== undefined) {
+        if (target !== route) {
+          return
+        }
+        event.preventDefault()
+      }
+    if (takeHeldHelpToggle(route)) {
+      setExpanded((value) => !value)
+    }
-  }, [])
+  }, [feature])
```

`convert-commands.ts:356` (CRLF kept): `browseHold = createHeldRequest((key) => key === '/convert' && isConvertHome())`; the module variable and its own `hashchange` listener are gone, and every export stays.

Nothing is committed or staged.

---

## Codex Validation Report

### Recheck Protocol

1. Read Scope + AC table
2. Verify each AC against Evidence section (file:line, not memory)
3. Independently probe the claimed behavior and compare decisive output
4. Verify the full gate is fresh and matches current D6 inputs; rerun if changed or unproven
5. Record findings below

### Findings

| # | Severity | Blocking | Kind | Finding | File:Line | Recommendation | Status |
|---|----------|----------|------|---------|-----------|----------------|--------|

No findings: the round 1 review's Findings table is empty.

### Verdict

`approved` at round 1 of 6, with 0 findings and 0 blocking, intent achieved (`.agent/context/handoffs/2026-11-17-ui-small-fixes-implementation-critical-review.md`, a byte-for-byte copy of the reviewer's report, checked with `cmp`; ledger loop `us-execution-2026-11-17-ui-small-fixes`, round 1 `recorded round 1 verdict=approved agent='codex-independent-reviewer' blocking=0 intent_achieved=yes usage=16,318,015`, `loop may close: approved with no blocking findings.`).

- **The loop.** It began with the plan's goal anchor and citable AC-1, AC-2, AC-3, AC-4, AC-5, AC-158 and AC-159, with no token budget; the OK line reads `mode=execution budget=6 tokens=off` (`us-exec-begin.txt` in the dispatch folder). Dispatch `us-exec-r1` ran with kind `execution` (timeout 2700 s); its console, `us-exec-console-r1.txt` in the dispatch folder, ends with exit 0.
- **The state.** **Intent achieved:** yes. The reviewer's own identity matched the gate's tested_state `9867e51f0024a113de6a585b42b54695f1e4bccb+0fb04e34a3879c5f491b2eb6fc42782c63314539f0e05a2bc03cb8494d11c42e` exactly (review frontmatter and §Scope); no state adjustment was needed.
- **What it accepted.**
  - Accepted HELD_REQUEST, CURRENT_ROUTE, BROWSE_HOLD, CONVERT_BROWSE_EVENT, HELP_HOLD, HELP_PENDING_TOGGLE_KEY, HELP_FEATURE_ROUTE, HELP_ROUTE_SCOPE, HELP_TAKE_ON_MOUNT and HELP_DROP as implemented. (§Q2)
  - It recounted row 7 from the raw `ok` lines: AC-158.8, .9, .10, .11 and .12 each 20; AC-157.8, .9, .10 and .11 each 20; the Ctrl+O test 20. (§Q2; the AC-157 ids are Session 89's test titles, cross-ref row above)
  - It judged the Reds genuine: No setup/import/timeout failure substitutes for the Red. Row 1a's `ERR_UNSAFE_PORT` lines were judged disclosed, with no chunk failure (§Q2).
  - The registers (§Q5): the two MEU transitions, the three issue resolutions (15 authorized leaf differences and zero problems) and grouping row 94 only. Accepted D-1142's disclosed queue order and D-1181's added load checks; no decision was reopened.
  - The gate (§Q6) and the scope and fidelity (§Q7): `us-gate-h1.txt` has 31 actual step records, each exit 0; the 362 skip-basis hashes match; all 31 line-ending paths pass, with `DownloaderPage.tsx:818` still bare LF.
- **What it did not rerun.** Not claimed: a fresh reviewer Electron launch, UI build, network capture or full-suite rerun. Reviewer launches were forbidden; it accepted the saved gate and Electron proofs against the matching identity and ran targeted checks only (5 unit files, 21 tests; the selftests, line endings, both renders and the syntax checks; its fake-spawn wrapper probe; its receipt, repeat and fidelity audits).
- **Residual limits it names, carried as limits, not findings.** Residual limits are the approved fresh-empty-status behavior, the measured default-window versus viewport distinction, and reliance on the matching saved Electron proofs because reviewer launches were forbidden.
- **A format note, not a finding.** The verdict JSON's schema has no top-level `tested_state`, so the reviewer carried the value in its summary and identity evidence and in the report's frontmatter. This output-format mismatch is not a product finding.
- **H1-7a** (`review-state-check.txt`, `review-state.json`): `OK: review_mode=execution; round 1 of 6; verdict=approved; open findings=0`.
- **H1-7b** (`exec-review.txt`): `OK: approved at round 1 of 6, 0 open blocking findings`.
- **After the review**, only the three handoffs changed, to fill this report. `identity.py` excludes the handoffs, so the tested_state is unchanged (H1-6b rerun).

---

## Deferred Items

| Item | Kind | Deferred-to | Basis |
|------|------|-------------|-------|
| Other chords on lazy pages | out-of-scope | — | Session 89 checked every chord: only Ctrl+O and F1 fire before their page mounts |
| Preloading the Convert and Capture chunks | out-of-scope | — | It hides the race for the first visit only |
| Commit and push | out-of-scope | — | Only on Mat's direction (H2-5) |
| The Codex execution review | next step | H1-7 | Not part of this run; the coordinator dispatches it |

### Departures and their basis

- **Queue order.** Under D-1142 the queue is 74, 92, 93, 94, then 91, so Session 94 ran fourth, after 74 (`cba97fe`), 92 (`8280586`) and 93 (`9867e51`), and Session 91 `e2e-pointer-flakes` runs after it. The plan's Status line still gives D-1133's order (74, 91, 92, 93, 94) and says Session 94 runs last. Session 91 has not run, so the plan's §Sibling overlap rows for Session 91 (`electron-app.ts`, `electron-env.ts`, the shared E2E helpers and a renderer race fix) are vacuous: row 0 found those files at `HEAD` and the new specs copy their `HEAD` form. Session 91's plan folder and its plan-review handoff were never opened or touched, and are left out of every scope check (`other sessions plan files skipped: 4`, `us-D6-scope-paths.txt`).
- **Plan and task hashes.** The reviewed plan's sha256 is `a91c81f8f652b2436a2c04f2b1a9ebeba50a4fbd801916840994051b3a29a89c` (the coordinator's approval, the plan's Status line); the plan-review handoff cites `ecfd0ac6…`, the plan before the coordinator wrote that Status line. D-1181 (below) then added one decision to the plan's YAML, so its sha256 is now `1bd49ed579781cd13bbc3f312084e3f6d0b9005a85cc71d4e0f344c96df49b57`. `task.md`'s reviewed sha256 is `07a356d2d2cbc0c57ad74f2d1ec6b2c8c9c2ecf705c0ef3cfed13d20feaf8e94`; since then it changed only by its row marks.
- **D-1181 (execution decision, in the plan's YAML; `resolution: autonomous`, two-way).** The plan says the gate's host-load step never fails the gate, but S11 forbids an Electron step above 50 % and the plan's own `host-wait.py` exits 1 when the load is still above the limit after 10 minutes. Chosen (A, the HDP recommendation, decided under the hand-over: USER_EXPLICIT 2026-11-17, continuing USER_EXPLICIT 2026-11-15 and USER_EXPLICIT 2026-11-18 "make the decisions always the recommenations"): `session-gate.ps1` runs `host-wait.py` as its own `host-load` step and again before each of its nine Electron steps (the preview proof and the eight E2E steps), each into its own `us-D6-<step>-load.txt`; a load still above 50 % after the wait fails that step. Every wait passed at once (7.3 % to 9.3 %), so the gate ran as the plan's table says. The options not taken: B, ignoring the exit code, would run Electron above the limit; C, one host-load step only, would leave the later Electron steps unchecked. No M hit. D-1182 to D-1184 and D-1190 to D-1192 are unused.
- **How the rows ran.** Each row's Validation cell was extracted to a `.ps1` file (an environment header setting the working directory, `PYTHONIOENCODING`, `PYTHONDONTWRITEBYTECODE`, `RECEIPTS_DIR`, `TMP` and `TEMP`, then the cell) and run with `pwsh -NoProfile -File`. The one change to a cell's text: `uv run python` became `uv run --no-sync python` (no network; the brief's rule), and row 0's `uv sync` step was dropped for the same reason; the lock hashes in `us-D6-identity-before.txt` are the row-0 ones. The extraction regex was widened once, to read cells that begin with `$` as well as `rtk proxy`. The hand edits were made by scripts that wrote bytes and asserted each anchor occurred once. Before each Electron step a host wait ran with the brief's 50 % limit (the plan's `load-run.py` copy already uses 50 %, not Session 90's 60 %); every one read under 26 %. Each Electron run used a scratch `AVKIT_APP_DATA` and cleared `ELECTRON_RUN_AS_NODE`, except where `preview-proof.py` sets it for its own child.
- **Row 0's dirty list.** `baseline-dirty.txt` records 17 dirty paths at row 0, 5 of them foreign; the foreign ones carry a `#` note naming their owner, and their hashes held to the gate (`baseline-dirty hash mismatch: []`, `us-D6-scope-paths.txt`).
- **AC-158.7's call.** The guard calls `takeHeldHelpToggle` only when it is a function, so at Red (where the name is missing) it checks the toggle alone and passes, as the plan requires of a guard (no `typeof` assertion). After the fix the call runs and asserts `false`.
- **Row 1a's console lines.** Each probe page logged `console: Failed to load resource: net::ERR_UNSAFE_PORT` lines (`us-1a-probe.txt`), from a resource request to a port Chromium blocks, not from the held chunks: `chunk errors: []` and both pages mounted. The probe's help-card lookup was scoped to `downloader-page`, so it counts the Downloader card only.
- **The gate's own reads.** `session-gate.ps1` reads each step's exit from `$LASTEXITCODE` and its own receipt, never a `.exit` side file, and checks each E2E receipt for its passed line, any failed or flaky line and any `unhandled rejection:` line (`rejection-record lines=0` for every step, `us-gate-h1.txt`).
- **Processes.** Each proof and E2E run stopped only the processes it launched, by recorded id and creation time (`left: 0` in every preview proof). No other session's app, the IDE's avkit MCP server, ShareX or Mat's app was stopped. The clipboard specs, `capture-filmstrip-actions.test.ts` and `capture-import.test.ts` never ran.

### Execution notes

- **The decisions.** D-1175: one held-request helper serves Ctrl+O and F1. D-1176: F1 carries its route and only a card on that route takes it; a second press joins. D-1179: the chunk hold and its row-1a probe before any Electron Red. D-1181: the gate's load waits (Departures). D-1177, D-1178 and D-1180 are MEU-159's and the preview's.
- **No stop fired.** No S2 to S12 condition was met; no existing test failed (S5 not used); no expectation was edited at Green (S3).

---

## Decision Log

None.

---

## History

| Event | Date | Agent | Detail |
|-------|------|-------|--------|
| Created | 2026-11-18 | claude-code-local (Claude Opus 5.5) | Handoff after the H1-2 gate, H1-3 and H1-4 |
| Reviewed | 2026-11-18 | codex-independent-reviewer | Execution review round 1: `approved`, 0 findings, intent achieved |
| Updated | 2026-11-18 | claude-code-local (Claude Opus 5.5) | Codex Validation Report filled; H1-6, H1-6a and H1-6b rerun |
