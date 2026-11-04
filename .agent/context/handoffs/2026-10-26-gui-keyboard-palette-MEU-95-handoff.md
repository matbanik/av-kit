---
date: "2026-10-26"
project: "gui-keyboard-palette"
meu: "MEU-95"
status: "complete"
action_required: "VALIDATE_AND_APPROVE"
template_version: "2.2"
verbosity: "standard"
plan_source: "docs/execution/plans/2026-10-26-gui-keyboard-palette/implementation-plan.md"
build_plan_section: "bp06"
agent: "claude-code-local (Claude Opus 5.5)"
reviewer: "codex (H1-7 execution review)"
predecessor: "none"
---

# Handoff: 2026-10-26-gui-keyboard-palette-MEU-95-handoff

> **Status**: `complete`
> **Action Required**: `VALIDATE_AND_APPROVE`

---

## Scope

**MEU**: MEU-95, `gui-shortcut-binding`. AppShell's keyboard shortcuts come from the command registry, and no chord is bound outside it.
**Build Plan Section**: [06 §Shortcut binding (residual)](../../../docs/build-plan/06-gui.md#shortcut-binding-residual).
**Predecessor**: none. The [MEU-96 handoff](2026-10-26-gui-keyboard-palette-MEU-96-handoff.md) and the [MEU-97 handoff](2026-10-26-gui-keyboard-palette-MEU-97-handoff.md) are the same plan's other MEUs.

Before this MEU, AppShell's `keydown` listener hard-coded `Ctrl+4`, `Ctrl+5` and `Ctrl+B`. The registry's `shortcut` strings were display text only, and the rail showed no chord when expanded.

- **`CHORD_FORMAT`.** `registry/shortcuts.ts` (new) exports `normalizeChord`, `chordFromEvent` and `ariaKeyshortcuts`. `Meta` and `Cmd` count as `Ctrl`, and a trailing `+` is the key `Plus`.
- **`RESERVED_CHORDS`.** The Electron default-menu accelerators, Capture's `F2` and zoom keys, `Ctrl+K` and `Enter`. No registry entry may take one.
- **`SHORTCUT_MAP`.** `buildShortcutMap` keys each entry as `chord@page`. It throws on an invalid or reserved chord, on a duplicate, and on a chord used both globally and on a page.
- **`SHORTCUT_HANDLER`.** `createShortcutHandler` ignores repeats, IME composition and bare modifiers. It stands down while any `aria-modal` other than the palette is open. It looks up the page key first, then the global key, and runs a `stateful` entry only when its page publishes it enabled. It fires from text fields.
- **`SHELL_WIRING`.** AppShell's one `window` `keydown` listener calls the handler after the Ctrl+K and palette-Escape cases. The hard-coded `'4'`, `'5'` and Ctrl+B branches are gone.
- **`NAV_HINTS`.** Every `NavRail` item has `title="<label> (<chord>)"` and `aria-keyshortcuts` in both rail states.

**Plan:** [implementation-plan.md](../../../docs/execution/plans/2026-10-26-gui-keyboard-palette/implementation-plan.md) §MEU-95. **Execution authorization:** `USER_EXPLICIT`, 2026-10-26, "appon reviewer approval start executing it", met by the round 3 plan approval ([walkthrough.md](../../../docs/execution/plans/2026-10-26-gui-keyboard-palette/walkthrough.md) §Execution message).

---

## Acceptance Criteria

| AC | Type | Description | Source | Test(s) | Status |
|----|------|-------------|--------|---------|--------|
| AC-95.1 | unit | `CHORD_FORMAT`: `normalizeChord` canonical forms and `null` cases (`'Ctrl+Ctrl+A'`, `'Hyper+A'`); `chordFromEvent`; `ariaKeyshortcuts('Ctrl+Shift+D')` is `'Control+Shift+D'` | 06 "Registry-driven" | `ui/tests/unit/shortcuts.test.ts` `AC-95.1 …` | ✅ |
| AC-95.2 | unit | `SHORTCUT_MAP` throws for a duplicate, global plus page, reserved and invalid chord; the same chord on two pages builds; the real registry builds; `RESERVED_CHORDS` members are fixed points | 06 "Tests" | `shortcuts.test.ts` `AC-95.2 …` | ✅ |
| AC-95.3 | unit | Dispatch: every registry chord runs only its own action and is prevented; `Ctrl+Q` is not | 06 "Tests" | `shortcuts.test.ts` `AC-95.3 …` | ✅ |
| AC-95.4 | unit | Guards: repeat, composing, a non-palette modal, the open palette closed first, a `stateful` entry not enabled | `SHORTCUT_HANDLER` | `shortcuts.test.ts` `AC-95.4 …` | ✅ |
| AC-95.5 | unit | Text fields: `Ctrl+2` fires from an input and a textarea; `Ctrl+A` and `Enter` keep their defaults; no field editing chord in the map | 06 "Text fields" | `shortcuts.test.ts` `AC-95.5 …` | ✅ |
| AC-95.6 | unit | `SHELL_WIRING`: the nav chords set the hash, `Ctrl+B` flips the rail, `Ctrl+K` opens the palette; AppShell source uses `createShortcutHandler` with no hard-coded `'4'`/`'5'` branch | 06 "Registry-driven" | `ui/tests/unit/app-shell-wiring.test.ts` `AC-95.6 …` | ✅ |
| AC-95.7 | unit | `NAV_HINTS`: each rail item's chord equals the registry's, with `aria-keyshortcuts` and a `title` naming the chord, expanded and collapsed | 06 "Hints" | `shortcuts.test.ts` `AC-95.7 …` | ✅ |
| AC-95.8 | integration | Electron: from Downloader, the nav chords reach each route and its root test id; `Ctrl+B` collapses and restores the rail; `Ctrl+3` works from `url-input` | 06 "Tests" | `ui/tests/e2e/keyboard-shortcuts.test.ts` `AC-95.8 …` | ✅ |
| AC-96 (cross-ref) | — | Owned by the MEU-96 handoff (palette curation and the rider) | plan §MEU-96 | [MEU-96 handoff](2026-10-26-gui-keyboard-palette-MEU-96-handoff.md) | see MEU-96 |
| AC-97 (cross-ref) | — | Owned by the MEU-97 handoff (common shortcuts) | plan §MEU-97 | [MEU-97 handoff](2026-10-26-gui-keyboard-palette-MEU-97-handoff.md) | see MEU-97 |
| AC-19 (cross-ref) | regression | AC-19.17: `handleGlobalShortcut` keeps its Ctrl+K contract after `SHELL_WIRING` | `SHELL_WIRING` | `ui/tests/unit/command-palette.test.ts`, `app-shell-wiring.test.ts` (gate `ui-tests`) | ✅ |
| AC-33 (cross-ref) | regression | TA-4 amends AC-33.2: the `Ctrl+4` check reads AppShell's `createShortcutHandler` and the registry's `navigateShell('/convert')`; AC-33.13 (no `apiFetch` in the registry) stays green | `TEST_AMENDMENTS` TA-4 | `ui/tests/unit/convert-page.test.ts` | ✅ |
| AC-39 (cross-ref) | regression | TA-3 amends AC-39.2 the same way for `Ctrl+5` and `/capture` | `TEST_AMENDMENTS` TA-3 | `ui/tests/unit/capture-page.test.ts` | ✅ |
| AC-20, AC-21, AC-22 (cross-ref) | regression | AC-20.13, AC-21.13, AC-22.19: the registry source never contains `apiFetch` | `APPEARANCE` | `downloader-page.test.ts`, `transcript-page.test.ts`, `tts-page.test.ts` (gate `ui-tests`) | ✅ |
| AC-23 (cross-ref) | regression | AC-23.18 to AC-23.20 GUI actions audit; the rider is in the MEU-96 handoff | `CLIPBOARD_RIDER` | `ui/tests/unit/gui-actions-audit.test.ts` (gate `ui-tests`) | ✅ |
| AC-45, AC-46 (cross-ref) | regression | AC-45.4a and AC-46.1a pin the feature palette ids and event keys | `CONFIRM_ROUTE` | `convert-commands.test.ts`, `download-commands.test.ts` (gate `ui-tests`) | ✅ |
| AC-59 (cross-ref) | regression | AC-59.12's annotation seam, which AC-97.8 reuses | plan §MEU-97 | `ui/tests/e2e/capture-inbox.test.ts` (gate `ui-electron`) | ✅ |
| AC-60 (cross-ref) | regression | AC-60.10's save refusals hold: `CAPTURE_SAVE_ROUTE` leaves `saveAnnotations` and its gate unchanged (the AC-97.11 harness, MEU-97 handoff) | `CAPTURE_SAVE_ROUTE` | `ui/tests/unit/capture-page.behavior.test.ts` (gate `ui-tests`) | ✅ |
| AC-24, AC-25 (cross-ref) | regression | Packaging tests in the gate's `py-tests`. AC-25.7 fails at baseline (`PACKAGING-MCP-SNIPPET-TOKEN-STALE`), so it is excused; AC-24.10 and AC-25.10 passed at baseline and are not excused | §Verification Plan baseline rule | `session-gate.ps1` `py-tests` | baseline rule |

<!-- CACHE BOUNDARY -->

---

## Evidence

### FAIL_TO_PASS

| Test | Red Output (hash/snippet) | Green Output | File:Line |
|------|--------------------------|--------------|-----------|
| AC-95.1 to AC-95.5 | `AssertionError: registry/shortcuts.ts exists: expected false to be true` | pass | `shortcuts.test.ts` |
| AC-95.6 | `AssertionError: Ctrl+2: expected '#/' to be '#/transcript'` | pass | `app-shell-wiring.test.ts` |
| AC-95.7 | `AssertionError: nav:downloader collapsed=false: expected '' to contain 'Ctrl+1'` | pass | `shortcuts.test.ts` |
| AC-95.8 | `Error: expect(page).toHaveURL(expected) failed`, received `…index.html#/` after `Control+2` | pass | `keyboard-shortcuts.test.ts` |

Every receipt and its decisive lines are in [walkthrough.md](../../../docs/execution/plans/2026-10-26-gui-keyboard-palette/walkthrough.md): §Baseline (row 0), §MEU-95 Red (row 2), §MEU-95 Green (row 3), §Gate (row 8) and §Hub (row 9).

### Commands Executed

```json
{"schema_version":"evidence.v1","check_id":"s41-95-red","command":"pwsh -NoProfile -File C:/Temp/av-kit/s41-row-2.ps1 (task.md row 2 Validation cell, verbatim, from P:/av-kit)","cwd":"P:/av-kit","scope":"MEU-95 Red: shortcuts.test.ts, the AC-95.6 app-shell test, TA-3/TA-4, the baseline renderer build, keyboard-shortcuts.test.ts, red-check.py","phase":"red","exit_code":0,"result":"pass","tested_state":"HEAD bb481ec plus row 1 canon edits and the row 2 tests; ui/src unchanged since baseline.sha","output":"Vitest 7 failed, 2 skipped (9), every failure an AssertionError | Electron 1 failed: AC-95.8 toHaveURL received #/ after Control+2 | red-check: 2 receipt(s), 3 required test(s), 0 problem(s) | row 2 exit=0","fresh":true}
```

```json
{"schema_version":"evidence.v1","check_id":"s41-95-green-run1","command":"pwsh -NoProfile -File C:/Temp/av-kit/s41-row-3.ps1 (task.md row 3, verbatim)","cwd":"P:/av-kit","scope":"MEU-95 Green run 1: the row 3 Vitest set, build, the row 3 Electron specs","phase":"green","exit_code":1,"result":"fail","tested_state":"HEAD bb481ec plus rows 1-2 and the MEU-95 implementation","output":"Vitest 105 passed | Electron 1 failed, 64 passed: capture-inbox.test.ts:689 AC-57.10 Test timeout of 60000ms exceeded, no assertion failure; alone 3/3 passed (1.3s, 955ms, 6.4s)","fresh":true}
```

```json
{"schema_version":"evidence.v1","check_id":"s41-95-green","command":"pwsh -NoProfile -File C:/Temp/av-kit/s41-row-3.ps1 (task.md row 3, verbatim, unchanged rerun)","cwd":"P:/av-kit","scope":"MEU-95 Green: the row 3 Vitest set, build, the row 3 Electron specs whole, the ui/src snapshot","phase":"green","exit_code":0,"result":"pass","tested_state":"HEAD bb481ec plus rows 1-2 and the MEU-95 implementation","output":"Vitest 9 files, 105 tests passed | built in 5.12s | Electron 65 passed (6.5m), AC-95.8 included | row 3 ui/src files: 165 | row 3 exit=0","fresh":true}
```

```json
{"schema_version": "evidence.v1", "check_id": "s41-gate-h1-2", "command": "$env:ELECTRON_RUN_AS_NODE=$null; rtk proxy pwsh -NoProfile -File docs/execution/plans/2026-10-26-gui-keyboard-palette/session-gate.ps1 *> C:/Temp/av-kit/s41-gate-h1.txt; $code=$LASTEXITCODE; Select-String -Path C:/Temp/av-kit/s41-gate-h1.txt -Pattern ' exit=','not_run','tested_state','_sha256 ','outside scope','PRODUCT_SCOPE'; exit $code", "cwd": "P:/av-kit", "scope": "H1-2 fresh full session gate after row 9 (INPUT_IDENTITY): static, py/ui/mcp tests, builds, openapi, state-render, ui-electron, e2e-repeat, identity before/npm/after", "phase": "full", "exit_code": 0, "result": "pass", "tested_state": "bb481ec7d46fdb45b47e533fc2ab83e47e31e227+f07e5ce8b9bb5c630abdfed1d301c89ab53de7b76f91087f4803840639409e7c", "output": "identity-before exit=0 | py-types, py-lint, ui-types, ui-lint, mcp-types, task-contract, scope-paths exit=0 | py-tests baseline rule: failed=5 outside_baseline=[] errors=0 (932 passed) | ui-tests Test Files 106 passed (106), Tests 1082 passed (1082) | mcp-build exit=0 | mcp-tests Test Files 31 passed (31), Tests 446 passed (446) | ui-build, ui-harness-build, ui-picker-stub, openapi exit=0 | state-render Drift check passed | ui-electron 178 passed (4.1m) | e2e-repeat 70 passed (1.1m) | identity-npm, identity-after exit=0 | tested_state before=bb481ec7d46fdb45b47e533fc2ab83e47e31e227+f07e5ce8b9bb5c630abdfed1d301c89ab53de7b76f91087f4803840639409e7c after=bb481ec7d46fdb45b47e533fc2ab83e47e31e227+f07e5ce8b9bb5c630abdfed1d301c89ab53de7b76f91087f4803840639409e7c | session-gate: all steps exit 0", "fresh": true}
```

```json
{"schema_version": "evidence.v1", "check_id": "s41-h1-3-render", "command": "rtk proxy uv run python tools/meu_status.py render --check *> C:/Temp/av-kit/drift-check.txt; $code=$LASTEXITCODE; Get-Content C:/Temp/av-kit/drift-check.txt; exit $code", "cwd": "P:/av-kit", "scope": "H1-3 SSOT render check after row 9's status writes", "phase": "static", "exit_code": 0, "result": "pass", "tested_state": "bb481ec7d46fdb45b47e533fc2ab83e47e31e227+f07e5ce8b9bb5c630abdfed1d301c89ab53de7b76f91087f4803840639409e7c", "output": "Drift check passed — SSOT loaded (98 MEUs, 12 phases), rendered regions match on-disk content", "fresh": true}
```

```json
{"schema_version": "evidence.v1", "check_id": "s41-h1-4-openapi", "command": "rtk proxy uv run python -c \"import json,pathlib,subprocess,sys; b=pathlib.Path('docs/execution/plans/2026-10-26-gui-keyboard-palette/baseline.sha').read_text().strip(); old=json.loads(subprocess.run(['git','show',b+':openapi.committed.json'],capture_output=True,text=True,check=True).stdout)['components']['schemas']; new=json.loads(pathlib.Path('openapi.committed.json').read_text(encoding='utf-8'))['components']['schemas']; added=sorted(set(new)-set(old)); removed=sorted(set(old)-set(new)); changed=sorted(k for k in set(old)&set(new) if old[k]!=new[k]); print('added:',added,'removed:',removed,'changed:',changed); sys.exit(0 if not added and not removed and not changed else 1)\" *> C:/Temp/av-kit/openapi-check.txt; $code=$LASTEXITCODE; Get-Content C:/Temp/av-kit/openapi-check.txt,C:/Temp/av-kit/s41-D6-openapi.txt; exit $code", "cwd": "P:/av-kit", "scope": "H1-4 OpenAPI: committed schemas against baseline.sha, plus the H1-2 openapi receipt", "phase": "static", "exit_code": 0, "result": "pass", "tested_state": "bb481ec7d46fdb45b47e533fc2ab83e47e31e227+f07e5ce8b9bb5c630abdfed1d301c89ab53de7b76f91087f4803840639409e7c", "output": "added: [] removed: [] changed: [] | H1-2 openapi stage=full exit=0", "fresh": true}
```

### Quality Gate Results

The H1-2 fresh gate is the session's full record. Row 9 changed bound inputs after row 8, so the record is H1-2, not row 8 (`INPUT_IDENTITY`). Every step exited 0. py-tests exited 1, as the plan's baseline rule allows: its 5 failures are all in the baseline set (`outside_baseline=[]`), AC-25.7 among them (`PACKAGING-MCP-SNIPPET-TOKEN-STALE`). The other step counts:

- ui Vitest: 106 files, 1082 passed.
- MCP Vitest: 31 files, 446 passed.
- Electron: 178 passed (4.1m); the e2e repeat: 70 passed (1.1m).
- `state-render`: drift check passed.
- Identity: `tested_state` `bb481ec7d46fdb45b47e533fc2ab83e47e31e227+f07e5ce8b9bb5c630abdfed1d301c89ab53de7b76f91087f4803840639409e7c` was the same before and after.

Row 8 run 4 passed whole on the pre-row-9 tree (state `c30c9b…`). It is kept as prose, not as a full record, because row 9 then changed bound inputs. Runs 1 to 3 failed and are recorded in the MEU-97 handoff (EC-4, EC-5 and the AC-60.11 waiting fix). H1-3: render check exit 0. H1-4: no OpenAPI schema added, removed or changed.

---

## Changed Files

| File | Action | Summary |
|------|--------|---------|
| `ui/src/renderer/src/registry/shortcuts.ts` | new | `SHELL_PAGE`, `CHORD_FORMAT`, `RESERVED_CHORDS`, `SHORTCUT_MAP`, `SHORTCUT_HANDLER` (MEU-96 and MEU-97 add to it) |
| `ui/src/renderer/src/registry/commandRegistry.ts` | modified | `CommandRegistryEntry` gains the `AVAILABILITY` fields; nav chords as `shortcut` strings |
| `ui/src/renderer/src/components/layout/AppShell.tsx` | modified | `SHELL_WIRING` |
| `ui/src/renderer/src/components/layout/NavRail.tsx` | modified | `NAV_HINTS` |
| `ui/tests/unit/shortcuts.test.ts` | new | AC-95.1 to AC-95.5, AC-95.7 |
| `ui/tests/unit/app-shell-wiring.test.ts` | modified | AC-95.6 |
| `ui/tests/unit/capture-page.test.ts`, `convert-page.test.ts` | modified | TA-3, TA-4 |
| `ui/tests/e2e/keyboard-shortcuts.test.ts` | new | AC-95.8 |

```diff
+  // Every registry chord, bound once (SHELL_WIRING). A stateful chord fires only
+  // while its page publishes it enabled (COMMAND_STATE); no record fails closed.
+  const shortcutHandler = useMemo(
+    () =>
+      createShortcutHandler({
+        commands: listCommands(),
+        getPage: currentShellPage,
+        getState: getCommandState,
+        isPaletteOpen: () => paletteOpenRef.current,
+        closePalette: () => {
+          setPaletteOpen(false)
+        },
+      }),
+    [],
+  )
@@
-      if ((event.ctrlKey || event.metaKey) && event.key === '4') {
-        event.preventDefault()
-        navigateShell('/convert')
-        return
-      }
-      if ((event.ctrlKey || event.metaKey) && event.key === '5') {
-        event.preventDefault()
-        navigateShell('/capture')
+      if (shortcutHandler(event)) {
         return
```

All three MEUs share the plan folder and the hub files in the plan's §Hub and state files table (rows 1 and 9, H1-3 and H2).

---

## Codex Validation Report

Pending: the H1-7 Codex execution review. The verdict is recorded in `2026-10-26-gui-keyboard-palette-implementation-critical-review.md`.

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
  - id: D-153
    stage: execution
    question: "Row 0's S1 tree check stopped on this plan's own untracked plan-review file under .agent/context/handoffs/. Is that file ours?"
    resolution: human
    class: governance-value
    chosen: "Treat it as ours: the S1 check admits .agent/context/handoffs/2026-10-26-gui-keyboard-palette-*, the prefix session-gate.ps1 already allows (EC-1)"
    source_tag: Human-approved
    precedents: ["session-gate.ps1:78 - the scope allow-list already holds the handoff prefix", "implementation-plan.md Handoff Set - names the rolling plan review file"]
    research: { engine: none, sources: [] }
    reasoning: "Mat ruled 'Treat it as ours, continue (Recommended)' on 2026-10-26. The file is the plan's own round 1-3 review, which the plan names, so stopping on it guarded nothing. Treating it as foreign would have blocked execution."
  - id: D-154
    stage: execution
    question: "Four test_framework_adoption.py tests fail on HEAD bb481ec. Does the gate count them as regressions?"
    resolution: autonomous
    class: two-way
    chosen: "No: session-gate.ps1 excuses the four ids, each only when the row 0 receipt shows it FAILED (EC-2)"
    source_tag: Local Canon
    precedents: ["implementation-plan.md Verification Plan section 1 - a test failing at baseline is never counted as a regression", "2026-10-24-gui-theme-path-fields walkthrough EC-1 - the same excuse for AC-25.7"]
    research: { engine: none, sources: [] }
    reasoning: "Each fails with 'REFUSE: rule map identity mismatch: AGENTS.md' because commit bb481ec edited AGENTS.md after the adoption manifest recorded it. Neither file is in PRODUCT_SCOPE. Excusing only the ids the baseline receipt shows FAILED applies the plan's own rule, and it can be reversed by removing the four ids."
```

---

## History

| Event | Date | Agent | Detail |
|-------|------|-------|--------|
| Created | 2026-10-26 | claude-code-local (Claude Opus 5.5) | Initial MEU-95 handoff after H1-2 |
