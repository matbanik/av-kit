---
date: "2026-09-20"
project: "2026-09-20-p6-gui-login-item"
meu: "MEU-61"
status: "complete"
action_required: "VALIDATE_AND_APPROVE"
template_version: "2.1"
verbosity: "standard"
plan_source: "docs/execution/plans/2026-09-20-p6-gui-login-item/implementation-plan.md"
build_plan_section: "bp06s6.6"
agent: "cursor-grok-4.6-xhigh"
reviewer: "gpt-5.6-sol"
predecessor: "2026-08-21-p6-gui-settings-help-MEU-23-handoff.md"
---

# Handoff: 2026-09-20-p6-gui-login-item-MEU-61-handoff

> **Status**: `complete`
> **Action Required**: `VALIDATE_AND_APPROVE`

---

## Scope

**MEU**: MEU-61 — `gui-login-item`. Per-user Electron login item: Settings “Start av-kit when I sign in” + nested “Start minimized”. OS is source of truth (`app.setLoginItemSettings` / HKCU Run + StartupApproved). Default **off**. Hidden when unpackaged or Linux. Pinned `LOGIN_ITEM_NAME=com.avkit.app`. IPC `login-item-get` / `login-item-set`. NSIS uninstall two executable `DeleteRegValue HKCU` lines. Not a Windows service. No `PUT /settings` leaves.

**Build Plan Section**: [06 §Startup (login item)](../../../docs/build-plan/06-gui.md#startup-login-item) · [07 §Login item uninstall](../../../docs/build-plan/07-distribution.md#login-item-uninstall-meu-61) (matrix 6.6)

**Predecessor**: [`2026-08-21-p6-gui-settings-help-MEU-23-handoff.md`](2026-08-21-p6-gui-settings-help-MEU-23-handoff.md)

```yaml
context_tool_decision:
  phase: planning_and_execution
  eligible_tools: []
  decision: not_applicable
  eligibility_basis: "Glob 0 for graphify-out/graph.json and graphify-out-research/graph.json (reconfirmed at handoff). GetDynamicTools catalog has no graphify/headroom namespaces."
  human_message_reference: null
```

**Deliberately NOT in this MEU.** WinSW / UAC / LocalSystem / “Auto-start on boot”. `PUT /settings` keys `open_at_login` / `start_minimized`. Squirrel `Update.exe` stub. `openAsHidden` as Start minimized (Electron 42 unavailable on macOS 13+). Portable target. New npm packages (`auto-launch`, `node-windows`, `winsw`). Phase 11 / MEU-50 page layout. MEU-60 Capture edit stays a separate residual.

---

## Acceptance Criteria

> **AC-table integrity (control C4).** All **22** plan ACs (AC-61.1–61.22) appear below with plan Type, Source, Test(s), and status.

| AC | Type | Description | Source | Test(s) | Status |
|----|------|-------------|--------|---------|--------|
| AC-61.1 | unit | `classifyLoginItemSupport` returns `platform` then `not-packaged` then supported | Spec | `login-item.test.ts` | ✅ |
| AC-61.2 | unit | every set passes `name: LOGIN_ITEM_NAME` | Spec | `login-item.test.ts` | ✅ |
| AC-61.3 | unit | `path` is `execPath`; never `Update.exe` | Spec / Research-backed | `login-item.test.ts` | ✅ |
| AC-61.4 | unit | Windows `args` is `[]` or `[--start-minimized]`; macOS write uses `[]` | Spec | `login-item.test.ts` | ✅ |
| AC-61.5 | unit | Windows read probes minimized then windowed; approval fields disable; macOS enabled with `minimized: false` even if fake `openAsHidden` | Spec / Research-backed | `login-item.test.ts` | ✅ |
| AC-61.6 | unit | Windows write clears the other argv and never passes `openAsHidden`; macOS write ignores minimized; off clears minimized | Spec | `login-item.test.ts` | ✅ |
| AC-61.7 | unit | non-boolean args throw `TypeError` and do not call Electron | Spec | `login-item.test.ts` | ✅ |
| AC-61.8 | unit | `login-item-get` empty/strict; `login-item-set` both booleans required | Spec | `login-item-ipc.test.ts` | ✅ |
| AC-61.9 | unit | extra IPC fields reject before Electron | Spec | `login-item-ipc.test.ts` | ✅ |
| AC-61.10 | unit | unsupported write returns unsupported state without throw | Spec | `login-item.test.ts` | ✅ |
| AC-61.11 | unit | default off: no OS entry ⇒ `enabled: false` | Human-approved | `login-item.test.ts` | ✅ |
| AC-61.12 | unit | panel hidden when unsupported; shown when `supported: true` | Spec | `settings-page.test.ts` | ✅ |
| AC-61.13 | unit | `start-minimized-checkbox` only while parent on and `startMinimizedSupported` | Spec / UX2 exception | `settings-page.test.ts` | ✅ |
| AC-61.14 | unit | checkbox click does not `PUT /settings`; schemas omit forbidden leaves | Spec | `settings-page.test.ts` | ✅ |
| AC-61.15 | unit | `revealMainWindow` skips `show()` for `--start-minimized` or hide-from-login; `index.ts` has no `window.show(` and wires the helper; tray Show still shows | Spec | `login-item-ipc.test.ts`; `login-item.test.ts`; `capture-tray.ts` unchanged | ✅ |
| AC-61.16 | unit | help section `startup` contains HELP_STARTUP_TOKENS | Spec | `settings-page.test.ts` | ✅ |
| AC-61.17 | integration | Wave 4 unpackaged E2E: `start-at-sign-in-panel` count 0 | Spec | `ui/tests/e2e/settings.test.ts` | ✅ |
| AC-61.18 | unit | two executable `DeleteRegValue HKCU` lines + `nsis.include` value `build/installer.nsh` | Spec / Research-backed | `login-item-nsh.test.ts`; `assert-meu-scans.ps1` | ✅ |
| AC-61.19 | unit | `listRegisteredChannels()` length 19 including get/set | Spec / Local Canon | `login-item-ipc.test.ts`; `ipc-strict-census.test.ts` | ✅ |
| AC-61.20 | unit | preload keys `loginItemGet`/`loginItemSet`; omitting get yields unsupported, no throw | Spec | `login-item-ipc.test.ts`; `settings-page.test.ts` | ✅ |
| AC-61.21 | unit | `gui-actions-index.md` contains `settings:login_item` / `settings:start_minimized`; kebab IPC resolves | Spec / Local Canon | `gui-actions-audit.test.ts` | ✅ |
| AC-61.22 | unit | argv match is whole-token; path substring does not count | Spec | `login-item-ipc.test.ts` | ✅ |

<!-- CACHE BOUNDARY -->
<!-- Content above this line is stable across revision passes (KV cache prefix). -->
<!-- Content below this line changes between passes (evidence, results, corrections). -->

---

## Evidence

### FAIL_TO_PASS

| Test | Red Output (hash/snippet) | Green Output | File:Line |
|------|--------------------------|--------------|-----------|
| AC-61.1–.16, .18–.22 (21 UI titles; AC-61.17 is E2E census-first, not assertion-red) | `C:/Temp/av-kit/fail-to-pass-meu-61-ui.json` + `.txt`; `assert-red-oracle.ps1 -Kind ui` PASS count=21 | `C:/Temp/av-kit/meu61-vitest.txt` **552 passed** (68 files). Gate re-run `C:/Temp/av-kit/full-verify-gate.txt` PASS | `ui/tests/unit/login-item*.test.ts`; `settings-page.test.ts`; `ipc-strict-census.test.ts`; `gui-actions-audit.test.ts` |
| AC-61.17 | Census `C:/Temp/av-kit/meu61-e2e-census.txt` PASS **before** production; unpackaged Settings already omitted the panel | `C:/Temp/av-kit/meu61-e2e.txt` + `.json`; classify `-Mode named` **PASS: named E2E AC-61.17** (1 passed, 521ms); `-Mode gate` PASS | `ui/tests/e2e/settings.test.ts:200` |

### Commands Executed

| Command | Exit Code | Key Output |
|---------|-----------|------------|
| `npm --prefix ui run test` Red + `assert-red-oracle.ps1 -Kind ui` | 1 then oracle 0 | 21 AC ids in failed titles |
| `assert-e2e-census.ps1` | 0 | `PASS: E2E census` |
| `npm --prefix ui run test` Green | 0 | 552 passed |
| `assert-meu-scans.ps1` | 0 | `PASS: MEU-61 scans` |
| `npm --prefix ui run build` then `assert-e2e-named.ps1 -Mode named` | 0 | `PASS: named E2E AC-61.17` |
| `assert-meu-gate.ps1` (row 7 + H1-2) | 0 | typecheck/lint/vitest/OpenAPI/census/named-gate/scans PASS |
| `export_openapi.py --check` | 0 | no regen |
| `meu_status.py update MEU-61 ready_for_review --plan …` + `render --check` | 0 | drift check passed |
| `assert-hub-next.ps1` | 0 | `PASS: hub Next + prior plans + MEU-61 bind` |

### Quality Gate Results

```
typecheck: PASS (0 errors)
lint: PASS (eslint --max-warnings 0)
ui vitest: 552 passed (68 files)
Playwright AC-61.17: 1 passed (unpackaged panel absent)
OpenAPI --check: pass (no regen; packages/api untouched)
anti-placeholder / G36 / NO_NEW_PACKAGES / NSIS negative fixture: 0 hits
E2E classify -Mode gate: PASS
hub Next: Phase 11 page layout (MEU-50); MEU-61 does not replace MEU-50
```

---

## Changed Files

> Delta-only excerpts. Phase 10 queue-card and MEU-60 Capture files are **not** this MEU.

| File | Action | Lines | Summary |
|------|--------|-------|---------|
| `ui/src/main/login-item.ts` | new | 1–150 | classify / read / write; `LOGIN_ITEM_NAME`; Windows approval fields |
| `ui/src/main/startup-mode.ts` | new | 1–13 | `--start-minimized` whole-token; `shouldShowWindowAfterLoad` |
| `ui/src/main/ipc.ts` | modified | 36–38, 82–88, 270–280, 427–435 | channels, Zod `.strict()`, handlers, default unpackaged deps |
| `ui/src/main/preload.ts` | modified | 24–25, 70–72 | `loginItemGet` / `loginItemSet` |
| `ui/src/main/index.ts` | modified | 60, 424–432, 499–500 | live `loginItem` deps; skip `window.show()` when minimized |
| `ui/src/renderer/src/env.d.ts` | modified | 45–65 | Window.api types |
| `ui/src/renderer/src/features/settings/StartAtSignInControl.tsx` | new | 1–95 | native checkboxes; hide when unsupported; hide minimized while parent off |
| `ui/src/renderer/src/features/settings/SettingsPage.tsx` | modified | 29, 803 | mount after Appearance |
| `ui/src/renderer/src/features/settings/settings-help-content.ts` | modified | 25–27 | `id: 'startup'` + HELP_STARTUP_TOKENS |
| `ui/electron-builder.yml` | modified | 14–15 | `nsis.include: build/installer.nsh` |
| `ui/build/installer.nsh` | new | 1–4 | `customUnInstall` two `DeleteRegValue HKCU` |
| `ui/tests/unit/login-item.test.ts` | new | AC-61.1–.7,.10–.11 | Red-first classify/read/write |
| `ui/tests/unit/login-item-ipc.test.ts` | new | AC-61.8–.9,.15,.19–.20,.22 | IPC + argv + preload |
| `ui/tests/unit/login-item-nsh.test.ts` | new | AC-61.18 | executable NSIS + YAML include |
| `ui/tests/unit/settings-page.test.ts` | modified | AC-61.12–.14,.16,.20 | RTL panel + no PUT |
| `ui/tests/unit/ipc-channels.ts` | modified | 19–20, 42 | length 19; `login-item-get` no-payload |
| `ui/tests/unit/ipc-strict-census.test.ts` | modified | VALID/TYPE_FAIL | extra-field + type fail payloads |
| `ui/tests/unit/gui-actions-audit.test.ts` | modified | AC-61.21 | skip login_item in AC-23.20; own AC |
| `ui/tests/e2e/settings.test.ts` | modified | 200–206 | named AC-61.17 `toHaveCount(0)` |
| `ui/tests/e2e/test-ids.ts` | modified | 34–36 | panel + two checkboxes |
| `MOCK_API_SITES` (9 files) | modified | stubs | `loginItemGet`/`Set` no-op unsupported |
| `docs/build-plan/gui-actions-index.md` | modified | 93–94 | `settings:login_item` / `settings:start_minimized` |

```diff
 # ui/src/main/index.ts after renderer load
-  window.show()
+  if (shouldShowWindowAfterLoad(process.argv)) {
+    window.show()
+  }
```

```diff
 # ui/src/main/login-item.ts writeStartAtSignIn
+  deps.setLoginItemSettings({ openAtLogin: false, path, args: argsFor(!wanted), name: LOGIN_ITEM_NAME })
+  deps.setLoginItemSettings({ openAtLogin: enabled, path, args: argsFor(wanted), name: LOGIN_ITEM_NAME })
```

```diff
 # ui/build/installer.nsh
+!macro customUnInstall
+  DeleteRegValue HKCU "Software\Microsoft\Windows\CurrentVersion\Run" "com.avkit.app"
+  DeleteRegValue HKCU "Software\Microsoft\Windows\CurrentVersion\Explorer\StartupApproved\Run" "com.avkit.app"
+!macroend
```

---

## Codex Validation Report

_Left blank for reviewer agent. Reviewer fills this section during `/execution-critical-review`._

### Recheck Protocol

1. Read Scope + AC table
2. Verify each AC against Evidence section (file:line, not memory)
3. Run all Commands Executed and compare output
4. Run Quality Gate commands independently
5. Record findings below

### Findings

| # | Severity | Finding | File:Line | Recommendation | Status |
|---|----------|---------|-----------|----------------|--------|
| 1 | {High\|Medium\|Low} | {description} | {file:line} | {fix} | {open\|fixed} |

### Verdict

`{approved | changes_required}` — {rationale}

---

## Corrections Applied (2026-09-20)

**Findings resolved**: 2/2 from exec r1; recheck r2 still `changes_required` (macOS 13+ `openAsHidden` unavailable; AC-61.15 mutants). This pass addresses r2.

| # | Finding | Fix Applied | Verification |
|---|---------|-------------|--------------|
| 1 | High r1/r2: packaged macOS minimized not deliverable; `openAsHidden`/`wasOpenedAsHidden` unavailable on macOS 13+ (Electron 42.9.3 d.ts, issue 37228, PR 37244) | Narrowed contract: darwin stays supported for `openAtLogin`; `startMinimizedSupported: false`; never pass `openAsHidden`; Settings hides Start minimized. Spec/plan/ACs updated. | Correction Red `C:/Temp/av-kit/meu61-corr-r3-red.txt` 7 failed; Green `C:/Temp/av-kit/meu61-corr-r3-green.txt` **43 passed** |
| 2 | Medium r1/r2: AC-61.15 token-order oracle survived unguarded `window.show()` and removed hide wiring | `revealMainWindow(window, argv, hideFromLoginLaunch)` is the only show path; `index.ts` must not contain `window.show(` and must call `revealMainWindow(window, process.argv, loginLaunchShouldHideWindow(`; spy tests cover argv and hide-from-login; tray `opts.window.show()` retained | same Green receipt |

---

## Deferred Items

_None. Packaged VM proof that a live HKCU Run key appears remains the Phase 7 clean-machine `[B]` path already named in 06-gui.md; it is not an in-scope AC for this MEU._

---

## History

| Event | Date | Agent | Detail |
|-------|------|-------|--------|
| Created | 2026-09-20 | cursor-grok-4.6-xhigh | Initial handoff after Green + named E2E + gate |
| Submitted for review | 2026-09-20 | cursor-grok-4.6-xhigh | Sent to gpt-5.6-sol (dispatch `p6-gui-login-item-exec-r1`) |
| Review complete | 2026-09-20 | gpt-5.6-sol | r1 `changes_required` (2 findings) |
| Corrections applied | 2026-09-20 | cursor-grok-4.6-xhigh | Darwin `openAsHidden` + AC-61.15 show/tray assertions |
| Review complete | 2026-09-20 | gpt-5.6-sol | r2 `changes_required` (macOS 13+ fields; AC-61.15 mutants) |
| Corrections applied | 2026-09-20 | cursor-grok-4.6-xhigh | Narrow macOS: no Start minimized; `revealMainWindow` oracle |
| Review complete | 2026-09-20 | gpt-5.6-sol | r3 `approved` (dispatch `p6-gui-login-item-exec-r3`) |
