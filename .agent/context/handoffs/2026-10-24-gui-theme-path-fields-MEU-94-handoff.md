---
date: "2026-10-26"
project: "gui-theme-path-fields"
meu: "MEU-94"
status: "complete"
action_required: "VALIDATE_AND_APPROVE"
template_version: "2.2"
verbosity: "standard"
plan_source: "docs/execution/plans/2026-10-24-gui-theme-path-fields/implementation-plan.md"
build_plan_section: "bp06"
agent: "claude-code-local (Claude Opus 5.5)"
reviewer: "codex (H1-7 execution review)"
predecessor: "none"
---

# Handoff: 2026-10-24-gui-theme-path-fields-MEU-94-handoff

> **Status**: `complete`
> **Action Required**: `VALIDATE_AND_APPROVE`

---

## Scope

**MEU**: MEU-94, `gui-theme-reactive-selects`. Every G30 select follows the live theme, and a cold boot in Light never paints a dark select (known issue `GUI-LIGHT-THEME-SELECT-STALE-DARK`).
**Build Plan Section**: [06 §Theme-reactive selects (residual)](../../../docs/build-plan/06-gui.md#theme-reactive-selects-residual).
**Predecessor**: none. The [MEU-93 handoff](2026-10-24-gui-theme-path-fields-MEU-93-handoff.md) is the same plan's second MEU.

Before this MEU, `getG30Styles()` read `html.dark` once at render, and `THEME_CHANGED_EVENT` re-rendered only `AppShell`. So route-page selects kept their dark colours in Light, and the option menu always used a fixed light pair. `index.html` booted with `class="dark"`, and the persisted theme was applied only after an async `GET /settings/ui`.

- **`THEME_HOOK`.** `useDocumentTheme()` (`lib/theme.ts`, `useSyncExternalStore` over `THEME_CHANGED_EVENT`) is the only `classList.contains('dark')` read in the renderer.
- **`G30_STYLES`.** `g30StylesFor(theme)` and `useG30Styles()` in `SelectInput.tsx` back the select and every option. `getG30Styles`, `NATIVE_OPTION_MENU_STYLE` and ConsolePanel's copy are removed. Consumers: ConsolePanel, CaptureViewport (Named), SettingsPage (`GridSelect`, `audio_format`), and `SelectInput` itself for TTSPage and VoiceCombobox.
- **`BOOT_THEME`.** `applyDocumentTheme` mirrors the theme to `localStorage['av-kit.ui.theme']`. The new `boot-theme.ts`, which is the first import of `main.tsx`, applies `readBootTheme()` before `createRoot`.
- **`BOOT_RETRY`.** `useSyncDocumentTheme()` retries only an `ApiError` 503: at 250, 500 and 1000 ms, then every 2000 ms, while the next start is under 60 s. It logs once and returns `settled`. A deadline bounds the whole boot load by the same 60 s: when it passes with an attempt pending, the hook logs once, settles on the current document theme and ignores a late answer (EC-6, review F1).
- **`THEME_GATE`.** `AppShell` renders `RouteThemePending` (`route-theme-pending`, "Connecting...", then "Still loading…" after 3 s) in place of the route until `settled`.
- **`THEME_PROBE`.** The new e2e helper `ui/tests/e2e/theme-probe.ts` holds or answers the boot theme request and records each inserted select's colours.

**Plan:** [implementation-plan.md](../../../docs/execution/plans/2026-10-24-gui-theme-path-fields/implementation-plan.md) §MEU-94. **Execution authorization:** `USER_EXPLICIT`, 2026-10-25, "proceed" ([walkthrough.md](../../../docs/execution/plans/2026-10-24-gui-theme-path-fields/walkthrough.md) §Execution message).

**Closeout basis:** Mat's ruling **D-120** (2026-10-26, option 2, which revised that day's option 1; walkthrough §Gate ruling).
- Gate runs 1–4 stand as the gate.
- The H1-2 fresh gate and the H1-6b full-evidence check were waived and not run.
- The H1-7 Codex execution review checks this handoff and decides `approved`.

---

## Acceptance Criteria

| AC | Type | Description | Source | Test(s) | Status |
|----|------|-------------|--------|---------|--------|
| AC-94.1 | unit | `useDocumentTheme()` follows `applyDocumentTheme` without a remount; it removes its listener on unmount; one render per switch | 06 "Reactive styles"; `THEME_HOOK` | `ui/tests/unit/theme-selects.test.tsx` `AC-94.1 …` | ✅ |
| AC-94.2 | unit | `g30StylesFor` equals the two pairs. A mounted `SelectInput` and every option carry the current pair after each switch, and the caller's `width` is kept | 06 "Reactive styles", "Option menu" | `theme-selects.test.tsx` `AC-94.2 …` | ✅ |
| AC-94.3 | unit | Source: no `getG30Styles` or `NATIVE_OPTION_MENU_STYLE`; `classList.contains('dark')` only in `lib/theme.ts`; the consumers use `useG30Styles`; TA-1 and TA-2 | 06 "One copy" | `theme-selects.test.tsx` `AC-94.3 …`; `chrome-zorivest.test.ts` (TA-1); `tts-page.test.ts` (TA-2) | ✅ |
| AC-94.4 | unit | Settings: every select (at least 8) and each option carry the light pair after `applyDocumentTheme('light')`, and the dark pair after `'dark'`, without a remount | 06 "Tests"; known issue | `theme-selects.test.tsx` `AC-94.4 …` | ✅ |
| AC-94.5 | unit | `BOOT_THEME`: mirror write and read, `null` for an unset key or `'blue'`, throwing storage tolerated; `boot-theme.ts` is the first import of `main.tsx` | 06 "First paint" | `theme-selects.test.tsx` `AC-94.5 …` | ✅ |
| AC-94.6 | unit | `BOOT_RETRY` (a)–(g): 503 backoff, 500 one-shot, FETCH_FAILED 33 calls, BACKEND_NOT_READY 33 calls then `settled`, no call after unmount; (f) and (g), from EC-6: a never-answering attempt settles at 60 s with one log and a late answer ignored, and unmount clears the deadline | `BOOT_RETRY`; `lib/api.ts` | `theme-selects.test.tsx` `AC-94.6 (a)`–`(g)` | ✅ |
| AC-94.7 | integration | Electron, Settings live toggle: `THEME_COLOURS` Dark → Light → Dark without navigation | 06 "Tests"; known issue | `ui/tests/e2e/settings.test.ts` `AC-94.7 …` | ✅ |
| AC-94.8 | integration | Electron, Settings cold boot (a) stored Light with no mirror, (b) stale mirror, (c) mirror agrees, (d) the mirror persists across launches | 06 "First paint", "Tests" | `settings.test.ts` `AC-94.8 (a)`–`(d)` | ✅ |
| AC-94.9 | integration | Electron, TTS cold boot with no mirror: held, then the selects are inserted Light | 06 "Tests"; known issue | `ui/tests/e2e/tts-generate.test.ts` `AC-94.9 …` | ✅ |
| AC-94.10 | integration | Electron, Convert cold boot with a stale mirror: held, then every select is Light | 06 "Tests" | `ui/tests/e2e/convert-queue.test.ts` `AC-94.10 …` | ✅ |
| AC-94.11 | unit | `THEME_GATE`: `RouteThemePending` text and timer; the route child waits for the theme answer and first renders with no `dark` class; a 599 answer releases it after one answer; a never-answering request releases it at 60 s (EC-6) | 06 "First paint"; §Progressive Loading Strategy | `theme-selects.test.tsx` `AC-94.11 …` | ✅ |
| AC-27 (cross-ref) | regression | TA-3 (D-118) amends AC-27.10 so it bans the `SelectInput` component and its named import, not the module path ConsolePanel's `useG30Styles` import uses | D-118; EC-3 | `ui/tests/unit/console-polish.test.ts:234` | ✅ |
| AC-93 (cross-ref) | — | Owned by the MEU-93 handoff | plan §MEU-93 | [MEU-93 handoff](2026-10-24-gui-theme-path-fields-MEU-93-handoff.md) | see MEU-93 |
| AC-23, AC-33, AC-51, AC-56, AC-58, AC-64, AC-71 (cross-ref) | regression | Regressions MEU-93 names (path fields, test-ids, run bar, audit) | plan §MEU-93 | [MEU-93 handoff](2026-10-24-gui-theme-path-fields-MEU-93-handoff.md) | see MEU-93 |
| AC-24, AC-25 (cross-ref) | regression | Packaging tests run in the gate's `py-tests`. AC-25.7 fails at baseline (EC-1), so it is not a regression; AC-24.10 and AC-25.10 passed at baseline | EC-1 | `session-gate.ps1` `py-tests` | baseline rule |
| AC-67, AC-81 (cross-ref) | regression | Capture Electron tests in the gate's `ui-electron`. AC-81.11 (run 1, F2 held by ShareX), AC-67.24 (run 3) and AC-67.35 (run 4) each failed once outside this plan's code; each passed in the other runs and when run alone | walkthrough §Session gate | `ui/tests/e2e/capture-inbox.test.ts` | ⚠️ environment misses; accepted by Mat (D-120) |

<!-- CACHE BOUNDARY -->

---

## Evidence

### FAIL_TO_PASS

| Test | Red Output (hash/snippet) | Green Output | File:Line |
|------|--------------------------|--------------|-----------|
| AC-94.1, 94.2, 94.5, 94.11 | `expected 'undefined' to be 'function'` (`useDocumentTheme`, `g30StylesFor`, `readBootTheme`, `RouteThemePending`) | pass | `theme-selects.test.tsx` |
| AC-94.3 | `expected [ …(6) ] to deeply equal []` (the `getG30Styles` source scan) | pass | `theme-selects.test.tsx` |
| AC-94.4 | `after light: expected [ …(10) ] to deeply equal []` | pass | `theme-selects.test.tsx` |
| AC-94.5 | `boot-theme.ts exists: expected false to be true` | pass | `theme-selects.test.tsx` |
| AC-94.6 (a)–(e) | `expected undefined to be false` (the baseline hook returns nothing) | pass | `theme-selects.test.tsx` |
| AC-94.6 (f), AC-94.11 never-answering (EC-6) | `expected false to be true`; `expected null not to be null` (the deadline mutated out) | pass | `theme-selects.test.tsx` |
| AC-94.7 | `expectThemeColours` dark: options carry `rgb(255, 255, 255)/rgb(30, 41, 59)`, the fixed light pair | pass | `settings.test.ts:683` |
| AC-94.8 (a), (b) | `expectThemeHeld`: `route-theme-pending` shown `false` | pass | `theme-probe.ts:220` |
| AC-94.8 (c) | `documentIsDark` while held: `true` | pass | `settings.test.ts:726` |
| AC-94.8 (d) | `storedMirror` on launch 1: `null` | pass | `settings.test.ts:739` |
| AC-94.9, AC-94.10 | `expectThemeHeld`: `route-theme-pending` shown `false` | pass | `theme-probe.ts:220` |

Every receipt and its decisive lines are in [walkthrough.md](../../../docs/execution/plans/2026-10-24-gui-theme-path-fields/walkthrough.md): §MEU-94 Red (row 2), §MEU-94 Green (row 3), §Session gate (row 6) and §Gate ruling.

### Commands Executed

```json
{"schema_version":"evidence.v1","check_id":"s40-94-red","command":"python C:/Temp/av-kit/s40-run_row.py 2 (task.md row 2 Validation cell, verbatim, pwsh from P:/av-kit)","cwd":"P:/av-kit","scope":"MEU-94 Red: theme-selects.test.tsx and TA-1/TA-2 Vitest, renderer build, the three Electron specs on the baseline renderer, red-check.py","phase":"red","exit_code":0,"result":"pass","tested_state":"HEAD 7b29fcd plus row 1 canon edits and the row 2 tests; ui/src unchanged since baseline.sha","output":"Vitest Test Files 1 failed (1), Tests 15 failed (15), every failure an AssertionError | Electron 7 failed, every failure Error: expect(...) | red-check: 2 receipt(s), 5 required test(s), 0 problem(s) | row 2 exit=0","fresh":true}
```

```json
{"schema_version":"evidence.v1","check_id":"s40-94-green-run1","command":"python C:/Temp/av-kit/s40-run_row.py 3 (task.md row 3, verbatim)","cwd":"P:/av-kit","scope":"MEU-94 Green run 1: the row 3 Vitest set, build, the three Electron specs","phase":"green","exit_code":1,"result":"fail","tested_state":"HEAD 7b29fcd plus rows 1-2 and the MEU-94 implementation, before TA-3","output":"Test Files 1 failed | 9 passed (10), Tests 1 failed | 193 passed (194) | AC-27.10 console-polish.test.ts:234 expect(panel).not.toContain('SelectInput') | S2 stop, ruled D-118 A","fresh":true}
```

```json
{"schema_version":"evidence.v1","check_id":"s40-94-green","command":"python C:/Temp/av-kit/s40-run_row.py 3 (task.md row 3, verbatim)","cwd":"P:/av-kit","scope":"MEU-94 Green run 2: the row 3 Vitest set, build, settings/tts-generate/convert-queue Electron specs whole","phase":"green","exit_code":0,"result":"pass","tested_state":"HEAD 7b29fcd plus rows 1-2, the MEU-94 implementation and TA-3","output":"Vitest Test Files 10 passed (10), Tests 194 passed (194) | build built in 4.14s | Electron 60 passed (1.5m), AC-94.7 to AC-94.10 included | row 3 ui/src files: 164 | row 3 exit=0","fresh":true}
```

```json
{"schema_version":"evidence.v1","check_id":"s40-gate-run1","command":"$env:ELECTRON_RUN_AS_NODE=$null; rtk proxy pwsh -NoProfile -File docs/execution/plans/2026-10-24-gui-theme-path-fields/session-gate.ps1 *> C:/Temp/av-kit/s40-gate.txt (task.md row 6, verbatim)","cwd":"P:/av-kit","scope":"Session gate run 1: identity, static, full py/ui/mcp suites, builds, openapi, state-render, full Electron","phase":"full","exit_code":1,"result":"fail","tested_state":"7b29fcd0efcd11a1d8c5cbf4d725aaa66be84bb2+154d3f8eaacdeaea0b87c90888292fc9761058a3c60309d4d5ffcfb4a5defa48","output":"py-tests 1 failed, 936 passed (AC-25.7 only, baseline, EC-1) | ui-tests 1040 passed (1040) | mcp-tests 446 passed | ui-electron 1 failed, 170 passed (3.8m): capture-inbox.test.ts:1928 AC-81.11 Error: F2 held by another process (ShareX, RegisterHotKey lastError=1409); every AC-93/AC-94 test passed | e2e-repeat, identity-npm, identity-after not_run reason=fail-fast","fresh":true}
```

```json
{"schema_version":"evidence.v1","check_id":"s40-gate-run2","command":"$env:ELECTRON_RUN_AS_NODE=$null; rtk proxy pwsh -NoProfile -File docs/execution/plans/2026-10-24-gui-theme-path-fields/session-gate.ps1 *> C:/Temp/av-kit/s40-gate.txt (task.md row 6, verbatim; summary kept as s40-gate-run2-ac1917.txt)","cwd":"P:/av-kit","scope":"Session gate run 2, after ShareX exited","phase":"full","exit_code":1,"result":"fail","tested_state":"7b29fcd0efcd11a1d8c5cbf4d725aaa66be84bb2+154d3f8eaacdeaea0b87c90888292fc9761058a3c60309d4d5ffcfb4a5defa48","output":"py-tests 1 failed, 936 passed (AC-25.7 only) | ui-tests 1 failed | 1039 passed (1040): command-palette.test.ts AC-19.17 Error: Test timed out in 5000ms under host load; alone 3/3 passed (496, 337, 482 ms) | later steps not_run reason=fail-fast","fresh":true}
```

```json
{"schema_version":"evidence.v1","check_id":"s40-gate-run3","command":"$env:ELECTRON_RUN_AS_NODE=$null; rtk proxy pwsh -NoProfile -File docs/execution/plans/2026-10-24-gui-theme-path-fields/session-gate.ps1 *> C:/Temp/av-kit/s40-gate.txt (task.md row 6, verbatim; summary kept as s40-gate-run3.txt)","cwd":"P:/av-kit","scope":"Session gate run 3","phase":"full","exit_code":1,"result":"fail","tested_state":"7b29fcd0efcd11a1d8c5cbf4d725aaa66be84bb2+154d3f8eaacdeaea0b87c90888292fc9761058a3c60309d4d5ffcfb4a5defa48","output":"py-tests 1 failed, 936 passed (AC-25.7 only) | ui-tests 1040 passed (1040) | mcp-tests 446 passed | ui-electron 1 failed, 170 passed (6.7m): capture-inbox.test.ts:1543 AC-67.24 Test timeout of 60000ms exceeded, Worker teardown timeout; no step failed; --repeat-each=10 alone 10 passed (28.2s); every AC-93/AC-94 test passed","fresh":true}
```

```json
{"schema_version":"evidence.v1","check_id":"s40-gate-run4","command":"$env:ELECTRON_RUN_AS_NODE=$null; rtk proxy pwsh -NoProfile -File docs/execution/plans/2026-10-24-gui-theme-path-fields/session-gate.ps1 *> C:/Temp/av-kit/s40-gate.txt (task.md row 6, verbatim; summary kept as s40-gate-run4.txt)","cwd":"P:/av-kit","scope":"Session gate run 4","phase":"full","exit_code":1,"result":"fail","tested_state":"7b29fcd0efcd11a1d8c5cbf4d725aaa66be84bb2+154d3f8eaacdeaea0b87c90888292fc9761058a3c60309d4d5ffcfb4a5defa48","output":"py-tests 1 failed, 936 passed (AC-25.7 only) | ui-tests 1040 passed | mcp-tests 446 passed | static, build, openapi, state-render pass | ui-electron 1 failed, 170 passed (9.5m): capture-inbox.test.ts:1594 AC-67.35 Test timeout of 60000ms exceeded, Worker teardown timeout, while a new host session started; capture-inbox.test.ts alone 39 passed (1.2m); every AC-93/AC-94 test passed | second hang, stop","fresh":true}
```

```json
{"schema_version":"evidence.v1","check_id":"s40-gate-h1-2","command":null,"cwd":"P:/av-kit","scope":"H1-2 fresh full gate after row 7, the record this handoff would carry for review","phase":"full","exit_code":null,"result":"not_run","reason":"Waived by Mat 2026-10-26 (D-120, option 2): runs 1-4 stand as the gate, with no re-run; the Codex execution review still runs","tested_state":"not derived; row 7 and H2 changed hub and state inputs after the runs 1-4 state","output":"not run"}
```

```json
{"schema_version":"evidence.v1","check_id":"s40-hub-row7","command":"python C:/Temp/av-kit/s40-run_row.py 7 (task.md row 7, verbatim)","cwd":"P:/av-kit","scope":"Row 7 hub: the 06 Delivered notes, MEU-93/94 ready_for_review with execution_plan, render --check","phase":"static","exit_code":0,"result":"pass","tested_state":"runs 1-4 tree plus the row 7 hub writes","output":"rg: Delivered (Session 40) at 06-gui.md:1414 and :1436 | hub problems: [] | Drift check passed - SSOT loaded (98 MEUs, 12 phases) | row 7 exit=0","fresh":true}
```

```json
{"schema_version":"evidence.v1","check_id":"s40-f1-red","command":"cd ui; npx vitest run tests/unit/theme-selects.test.tsx > C:/Temp/av-kit/s40-f1-red-theme.txt (with the lib/theme.ts deadline delay mutated to 2_000_000_000, then restored byte-for-byte)","cwd":"P:/av-kit/ui","scope":"EC-6 Red: the new never-answering tests fail without the boot deadline","phase":"red","exit_code":1,"result":"fail","tested_state":"runs 1-4 tree plus row 7 and the EC-6 tests, deadline mutated out","output":"Tests 2 failed | 16 passed (18): AC-94.6 (f) AssertionError expected false to be true; AC-94.11 never answers AssertionError expected null not to be null","fresh":true}
```

```json
{"schema_version":"evidence.v1","check_id":"s40-f1-green","command":"cd ui; npx vitest run tests/unit/theme-selects.test.tsx; npm run typecheck; npx eslint --max-warnings 0 src/renderer/src/lib/theme.ts tests/unit/theme-selects.test.tsx; npx vitest run > C:/Temp/av-kit/s40-f1-ui-all.txt","cwd":"P:/av-kit/ui","scope":"EC-6 Green: theme-selects, typecheck, lint, the full UI unit suite","phase":"targeted","exit_code":0,"result":"pass","tested_state":"runs 1-4 tree plus row 7 and the EC-6 fix","output":"theme-selects Tests 18 passed (18) | tsc exit 0 | eslint exit 0 | full UI Test Files 103 passed (103), Tests 1043 passed (1043)","fresh":true}
```

```json
{"schema_version":"evidence.v1","check_id":"s40-f1-row3","command":"python C:/Temp/av-kit/s40-run_row.py 3 (task.md row 3, verbatim)","cwd":"P:/av-kit","scope":"EC-6 runtime: the row 3 Vitest set, build, settings/tts-generate/convert-queue Electron specs whole","phase":"runtime","exit_code":0,"result":"pass","tested_state":"runs 1-4 tree plus row 7 and the EC-6 fix","output":"Vitest Tests 199 passed (199) | build ok | Electron 61 passed (2.7m), AC-94.7, AC-94.8 (a)-(d), AC-94.9, AC-94.10 ok | row 3 exit=0","fresh":true}
```

### Quality Gate Results

No gate run passed whole, and Mat accepted runs 1–4 as the gate (D-120). All four ran on the same tested_state.

- Every AC-94 test passed in every run: Vitest AC-94.1–94.6 and AC-94.11, Electron AC-94.7–94.10.
- Static checks passed in every run: `py-types`, `py-lint`, `ui-types`, `ui-lint`, `mcp-types`, `task-contract`, `scope-paths` (`outside scope: []`), the builds, `openapi` and `state-render`.
- Each run's one non-baseline failure was an environment or load miss outside this plan's code: AC-81.11, AC-19.17, AC-67.24, AC-67.35.
- Never run on this tree: `e2e-repeat` (`--repeat-each=10` over AC-94/AC-93/AC-64.6), `identity-npm` and `identity-after`. Every run stopped fail-fast before them.
- H1-4 OpenAPI: `added: [] removed: [] changed: []` against `baseline.sha`.
- **After the gate:** EC-6 (review F1) changed `lib/theme.ts` and `theme-selects.test.tsx` after the runs 1–4 tree. The full UI unit suite and row 3, which includes the Electron cold-boot specs, were re-run on the fixed tree (above). The session gate was not re-run (D-120).

---

## Changed Files

| File | Action | Summary |
|------|--------|---------|
| `ui/src/renderer/src/lib/theme.ts` | modified | `useDocumentTheme`; `THEME_STORAGE_KEY`, `readBootTheme`, and the mirror in `applyDocumentTheme`; `BOOT_RETRY` in `useSyncDocumentTheme`, which returns `settled`; the EC-6 boot deadline |
| `ui/src/renderer/src/boot-theme.ts` | new | applies `readBootTheme()` at module evaluation |
| `ui/src/renderer/src/main.tsx` | modified | first import `./boot-theme` |
| `ui/src/renderer/src/components/layout/AppShell.tsx` | modified | `THEME_GATE`; exports `RouteThemePending` |
| `ui/src/renderer/src/components/ui/SelectInput.tsx` | modified | `g30StylesFor`, `useG30Styles`; `getG30Styles` and `NATIVE_OPTION_MENU_STYLE` removed |
| `ui/src/renderer/src/components/layout/ConsolePanel.tsx` | modified | the G30 copy is removed; `console-search` uses `useG30Styles()` |
| `ui/src/renderer/src/features/capture/CaptureViewport.tsx` | modified | the Named select and its options use `useG30Styles()` |
| `ui/src/renderer/src/features/settings/SettingsPage.tsx` | modified | `GridSelect` and the `audio_format` select use `useG30Styles()` (shared with MEU-93) |
| `ui/src/renderer/src/features/tts/TTSPage.tsx`, `VoiceCombobox.tsx` | modified | redundant `style` props removed (shared with MEU-93) |
| `ui/tests/unit/theme-selects.test.tsx` | new | AC-94.1–94.6, AC-94.11; EC-6 (f), (g) and the never-answering gate case |
| `ui/tests/unit/chrome-zorivest.test.ts`, `tts-page.test.ts`, `console-polish.test.ts` | modified | TA-1, TA-2, TA-3 |
| `ui/tests/e2e/theme-probe.ts` | new | `THEME_PROBE` |
| `ui/tests/e2e/settings.test.ts`, `tts-generate.test.ts`, `convert-queue.test.ts` | modified | AC-94.7–94.10; the seams' `themeProbe` option |
| `.agent/docs/emerging-standards.md`, `docs/build-plan/06-gui.md` | modified | row 1 canon (D-109), and the row 7 Delivered note |

```diff
+import './boot-theme'
+
 import { QueryClientProvider } from '@tanstack/react-query'
```

```diff
-export const NATIVE_OPTION_MENU_STYLE = G30_LIGHT
+/** G30 inline pair for a native select and its option menu in `theme`. */
+export function g30StylesFor(theme: UiTheme): { backgroundColor: string; color: string } {
+  return G30_PAIRS[theme]
+}
-export function getG30Styles(): { backgroundColor: string; color: string } {
-  const isDark =
-    typeof document !== 'undefined' && document.documentElement.classList.contains('dark')
-  return isDark ? G30_DARK : G30_LIGHT
+export function useG30Styles(): { backgroundColor: string; color: string } {
+  return g30StylesFor(useDocumentTheme())
```

Shared by both MEUs: the plan folder and the hub files in the plan's §Hub and state files table (rows 1 and 7, H1-3 and H2).

---

## Codex Validation Report

Pending: the H1-7 Codex execution review (D-120, option 2). The verdict is recorded in `2026-10-24-gui-theme-path-fields-implementation-critical-review.md`.

### Recheck Protocol

1. Read Scope + AC table
2. Verify each AC against Evidence section (file:line, not memory)
3. Independently probe the claimed behavior and compare decisive output
4. Verify the full gate is fresh and matches current D6 inputs; rerun if changed or unproven
5. Record findings below

### Findings

| # | Severity | Finding | File:Line | Recommendation | Status |
|---|----------|---------|-----------|----------------|--------|

### Verdict

_pending: H1-7 Codex execution review_

---

## Deferred Items

None.

---

## Decision Log

```yaml
decision_log:
  - id: D-118
    stage: execution
    question: "AC-27.10's not.toContain('SelectInput') fails on ConsolePanel's useG30Styles import from '../ui/SelectInput' (the one copy AC-94.3 requires). How does the check treat it?"
    resolution: human
    class: source-conflict
    chosen: "A: TA-3, the check bans the <SelectInput component and its named import, not the module path; lines 235-237 stay"
    source_tag: Human-approved
    precedents: ["MEU-27 handoff :168 - inlined getG30Styles into ConsolePanel to get past the same check", "plan 2026-08-20-p6-gui-console-polish :105, :183 - SUPERSEDED_26 bans SelectInput as the level control"]
    research: { engine: tavily, sources: ["https://eslint.org/docs/latest/rules/no-restricted-imports - restricts named imports, not path substrings"] }
    reasoning: "Mat accepted A on 2026-10-25 ('all recommendations are accepted, continue'). B added an unplanned file only to pass a substring check, and C restored the second copy that AC-94.3 and TA-1 forbid."
  - id: D-120
    stage: closeout
    question: "Session 41 builds on this tree, and no gate run passed whole because of environment misses. How does Session 40 close?"
    resolution: human
    class: governance-value
    chosen: "Option 2: gate runs 1-4 stand as the gate, no re-run; the H1-2 fresh gate and H1-6b are waived; the H1-7 Codex execution review runs and decides approved; then Mat commits"
    source_tag: Human-approved
    precedents: ["walkthrough.md Gate ruling - Mat's verbatim answer '1', then 'I changed my mind, I'd like the Option 2 with the codex review', 2026-10-26", "GUARDRAILS - explicit user authorization governs workflow ceremony"]
    research: { engine: none, sources: [] }
    reasoning: "Every AC-93/AC-94 test passed in all four runs, and each run's one other failure was an environment or load miss. A re-run would mean pausing the other sessions for a result that runs 1-4 already show. The Codex review is the only independent check of the code, so Mat kept it (option 2 was the recommendation). The ruling is recorded in task.md, the walkthrough and both handoffs."
```

---

## History

| Event | Date | Agent | Detail |
|-------|------|-------|--------|
| Created | 2026-10-26 | claude-code-local (Claude Opus 5.5) | Initial MEU-94 handoff after row 7 |
| Ruling | 2026-10-26 | Mat | D-120 option 2: no gate re-run; Codex execution review kept |
| Corrected | 2026-10-26 | claude-code-local (Claude Opus 5.5) | Review round 1 F1, EC-6: boot deadline |
