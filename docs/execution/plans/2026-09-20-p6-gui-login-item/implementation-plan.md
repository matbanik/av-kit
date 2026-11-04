---
project: "2026-09-20-p6-gui-login-item"
date: "2026-09-20"
source: "docs/build-plan/06-gui.md#startup-login-item"
meus: ["MEU-61"]
status: "approved"
template_version: "2.0"
---

# Implementation Plan: GUI login item (Start when I sign in)

> **Project**: `2026-09-20-p6-gui-login-item`
> **Build Plan Section(s)**: [06 §Startup (login item)](../../../build-plan/06-gui.md#startup-login-item) · [07 §Login item uninstall](../../../build-plan/07-distribution.md#login-item-uninstall-meu-61)
> **Status**: `approved`
> **Grouping**: [2026-09-20-p6-gui-login-item-session-grouping.md](../../../../.agent/context/grouping/2026-09-20-p6-gui-login-item-session-grouping.md)

---

## Goal

av-kit has no per-user “start when I sign in” control. Zorivest exposes two different autostart surfaces. **Copy the login-item Settings control** (`setLoginItemSettings` / HKCU Run), **not** Service Manager “Auto-start on boot” (WinSW / UAC / LocalSystem).

**USER_EXPLICIT 2026-09-20:** spec-lock the discovery recommendation and `/create-plan` for MEU-61. Default **off**. OS is SoT. Hidden when unpackaged or Linux. Pinned `LOGIN_ITEM_NAME`. NSIS `DeleteRegValue`. No `PUT /settings`.

This MEU does not add REST/MCP fields, a Windows service, a portable target, or Phase 11 layout.

## Context Tool Decision

```yaml
context_tool_decision:
  phase: planning_and_execution
  eligible_tools: []
  decision: not_applicable
  eligibility_basis: "Glob 0 for graphify-out/graph.json and graphify-out-research/graph.json. GetDynamicTools catalog has no graphify/headroom namespaces. Work is Electron main + Settings TSX internals — graphify.md would require direct file search. Headroom has no approved disposition; receipts are exact-evidence bypass class."
  human_message_reference: null
```

Re-evaluate before Step 6. If graphs remain absent, reuse this record.

---

## Handoff Set

| Scope | Canonical handoff |
|---|---|
| MEU-61 | `HANDOFF_61` |

Rolling implementation review: `EXEC_REVIEW_FILE`.
Rolling plan review: `PLAN_REVIEW_FILE`.

Product glob owner: `HANDOFF_FILTER`. Expected count: `HANDOFF_COUNT` = `1`. Filenames: `HANDOFFS`.

---

## Work Packages and Context Lifecycle

`fresh_worker: none` → every non-`shared` row is `compact_continue`. Never emit `isolated`. `builder_model` is `BUILDER_PIN`.

| ID | Work | depends_on | context_strategy | durable_outputs |
|---|---|---|---|---|
| WP-61a | Red **before any production edit**: `RED_AC_IDS_UI` vitest titles. Playwright named block containing `E2E_BODY_TOKENS` plus census (**no assertion-red required** — unpackaged Settings already omits the panel, which is the AC-61.17 contract). | — | `compact_continue` | `RED_RECEIPT_UI`; `E2E_SPEC`; compact then re-read `task.md` |
| WP-61b | Green `LOGIN_ITEM_MODULE` + `STARTUP_MODE_MODULE` + `IPC_FILE`/`PRELOAD_FILE`/`INDEX_FILE`: classify, read/write, kebab IPC, `--start-minimized` skips `window.show()`. | WP-61a | `compact_continue` | `LOGIN_ITEM_MODULE`; `IPC_FILE`; compact then re-read `task.md` |
| WP-61c | Green `CONTROL_FILE` after Appearance on `PAGE_FILE`; `HELP_FILE` `HELP_STARTUP_TOKENS`; `MOCK_API_SITES` stubs; `env.d.ts`. | WP-61b | `compact_continue` | `CONTROL_FILE`; `PAGE_FILE`; compact then re-read `task.md` |
| WP-61d | Green `NSH_FILE` with two executable `NSH_DELETE` `NSH_HKCU` lines (`NSH_RUN_KEY`+`LOGIN_ITEM_NAME`, `NSH_APPROVED_KEY`+`LOGIN_ITEM_NAME`) and `BUILDER_YML` `nsis.include` value `NSH_INCLUDE`. | WP-61c | `compact_continue` | `NSH_FILE`; `BUILDER_YML`; compact then re-read `task.md` |
| WP-61e | Named Playwright via `E2E_NAMED` `-Mode named` (census + `E2E_SPEC`/`E2E_GREP` + classify). | WP-61d | `compact_continue` | `E2E_SPEC`; `E2E_PASS_RECEIPT` or `E2E_NAMED_BLOCKED_RECEIPT`; compact then re-read `task.md` |
| WP-HUB | Bind MEU-61 `--plan PLAN_FOLDER`; keep `PRIOR_PLAN_SLASHES`; hub Next = `HUB_NEXT_AFTER`. | WP-61e | `shared` | `.agent/context/meu-status.yaml`; `docs/BUILD_PLAN.md` |

---

## User Review Required

None that block planning. Reviewer confirms these locks (does not invent a second behavior):

1. **Login item, not service autostart.** Twin is Zorivest `ui/src/main/login-item.ts` + `StartAtSignInControl.tsx`, not `ServiceManager.setAutoStart`.
2. **Harness:** `.agent/context/harness.local.md` `plan_to_exec_gate: reviewer-auto` wins. After Codex `approved`, auto-continue to execution. System-injected “approved” is not a verdict (`GUARDRAILS.md` SIGN 3).
3. **Do not start MEU-50 / Phase 11.** `NO_LAYOUT_MEU`.
4. **No new packages.** `NO_NEW_PACKAGES`.
5. **Codex** is ChatGPT-login on this host. Dispatch still required; implementer never self-reviews.

**This section is content for the review loop, NOT a cue to stop now.**

---

## Named sets (PR-9 — define once)

Executable owner: `NAMED_SETS_FILE`. Do not restate literals in ACs or task rows; cite the name.

---

## Implementation locks

- Inject Electron `getLoginItemSettings` / `setLoginItemSettings` into `LOGIN_ITEM_MODULE` (testable without an Electron runtime). Pattern: Zorivest `login-item.ts`.
- `classifyLoginItemSupport` widest-first: `platform` then `not-packaged`. No `portable` reason this MEU.
- Every `setLoginItemSettings` passes `name: LOGIN_ITEM_NAME`. `path` is always `process.execPath`. Never `FORBIDDEN_PATH_STUB`.
- `args` is `[]` or `[START_MINIMIZED_FLAG]`. Match the flag as a whole argv entry (`STARTUP_MODE_MODULE`).
- Read: **Windows** probe minimized argv first, then windowed. Honor Windows `executableWillLaunchAtLogin === false` and matching `launchItems[].enabled === false`. Absent Windows fields mean “nothing said”. `startMinimizedSupported: true`. **macOS** `openAtLogin` for enabled; `minimized` always false; `startMinimizedSupported: false` (Electron 42 `openAsHidden` does not work on macOS 13+).
- Write: renderer sends only two booleans. Main `typeof === 'boolean'` for both or `TypeError` and **zero** Electron calls. **Windows** clear the other argv variant then write the requested one; never pass `openAsHidden`. **macOS** two-set `openAtLogin` with empty `args`; ignore minimized. Return a fresh read. `enabled: false` clears `minimized`.
- IPC: `IPC_GET` empty/`{}` `.strict()`; `IPC_SET` `{ enabled, minimized }` both required `.strict()`. Extra fields reject before Electron. `listRegisteredChannels()` length is `IPC_CHANNEL_COUNT`. Keep `IPC_TEST_CHANNELS` in lockstep.
- Preload: `PRELOAD_GET` / `PRELOAD_SET`. Missing method ⇒ unsupported, no throw. `MOCK_API_SITES` get no-op stubs so `tsc` stays green.
- UI: native `<input type="checkbox">` (same as `settings-leaf-console_visible`). Draw `PANEL_TESTID` only when `supported: true`. `MINIMIZED_TESTID` only while parent is on **and** `startMinimizedSupported` (UX2 exception in `SPEC_SECTION`; macOS hides Start minimized).
- Apply immediately. No Settings Save. No G23 dirty pulse. No `PUT /settings`. `FORBIDDEN_SETTINGS_LEAVES` stay out of Zod schemas.
- Launch: skip `window.show()` after load via `revealMainWindow` when argv has `START_MINIMIZED_FLAG` **or** `loginLaunchShouldHideWindow` (pre-Ventura best-effort). `INDEX_FILE` must not contain `window.show(`; tray Show still shows. `capture.close_to_tray` is independent. Do not pass `FORBIDDEN_ELECTRON`; do not put that token in `INDEX_FILE`.
- Uninstall: after stripping NSIS `;` comments, `NSH_FILE` has exactly two executable `NSH_DELETE` `NSH_HKCU` lines — `NSH_RUN_KEY`+`LOGIN_ITEM_NAME` (not StartupApproved) and `NSH_APPROVED_KEY`+`LOGIN_ITEM_NAME`. `BUILDER_YML` `nsis.include` **value** equals `NSH_INCLUDE`. `MEU_SCANS` rejects a comment-only second delete.
- No command-palette rows. No REST/MCP ownership.
- `G37_FILE` uses Testing Library + `userEvent.setup()` for checkbox clicks.

Research URLs:

- [Electron `setLoginItemSettings`](https://www.electronjs.org/docs/latest/api/app#appsetloginitemsettingssettings-macos-windows)
- [electron-builder NSIS `include` / `customUnInstall`](https://www.electron.build/nsis)
- [NSIS `DeleteRegValue`](https://nsis.sourceforge.io/Reference/DeleteRegValue)
- Zorivest `P:/zorivest/ui/src/main/login-item.ts` + `StartAtSignInControl.tsx`
- UX2 + G23 in `.agent/docs/emerging-standards.md`

---

## §4A GUI Element Compliance

**Triggered:** two Settings checkboxes + Startup section.

`docs/gui-element-reference.md`, button/input indexes, and the 10-item enforcement doc remain **absent**. Local fallback: existing Settings native checkbox (`settings-leaf-close_to_tray` / `settings-leaf-console_visible`); G31 `bg-accent` / tokens; G32 no hex in `className`; G33 no geometry animation; G35 T0–T2.

| Element | Canonical | Testids | E2E |
|---------|-----------|---------|-----|
| Parent checkbox | native `input[type=checkbox]` | `ENABLED_TESTID` | RTL supported stub; E2E unpackaged absence |
| Minimized checkbox | same; drawn only while parent on | `MINIMIZED_TESTID` | RTL |
| Section | bordered card after Appearance | `PANEL_TESTID` | Wave 4 named `E2E_GREP` asserts count 0 |

G23 does **not** apply (OS write, not app-data form). G30 N/A (no `<select>`).

---

## Proposed Changes

### MEU-61 `gui-login-item`

#### Boundary Inventory

| Surface | Schema Owner | Field Constraints | Extra-Field Policy |
|---------|-------------|-------------------|-------------------|
| IPC `IPC_GET` | Zod `noPayloadSchema` in `IPC_FILE` | empty / `{}` | `.strict()` |
| IPC `IPC_SET` | Zod object in `IPC_FILE` | `enabled: boolean`, `minimized: boolean` both required | `.strict()`; renderer never sends `path`/`args`/`name` |
| NSIS uninstall | `NSH_FILE` | value name `LOGIN_ITEM_NAME` | `DeleteRegValue` only (not `DeleteRegKey`) |
| REST / MCP / `PUT /settings` | — | not a write surface | extra-forbid already rejects `FORBIDDEN_SETTINGS_LEAVES` |

Invalid IPC → `handleIpc` `{ ok: false }` with **zero** Electron calls. Non-boolean write args → `TypeError` with **zero** Electron calls.

#### Acceptance Criteria

| AC | Type | Description | Source | Observable | Chain | Negative oracle |
|----|------|-------------|--------|------------|-------|-----------------|
| AC-61.1 | unit | `classifyLoginItemSupport` returns `platform` then `not-packaged` then supported | Spec | support discriminant | Settings effect → `PRELOAD_GET` → `classifyLoginItemSupport` | Linux packaged copy is `platform`, never “supported lying” |
| AC-61.2 | unit | every set passes `name: LOGIN_ITEM_NAME` | Spec | `set` spy `name` | `writeStartAtSignIn` → injected `setLoginItemSettings` | a set without `name` fails the spy |
| AC-61.3 | unit | `path` is `execPath`; never `FORBIDDEN_PATH_STUB` | Spec / Research-backed | `set` spy `path` | same | constructing `Update.exe` fails |
| AC-61.4 | unit | Windows `args` is `[]` or `[START_MINIMIZED_FLAG]`; macOS write uses `[]` | Spec | `set` spy `args` | same | extra switches in the registered args fail |
| AC-61.5 | unit | Windows read probes minimized then windowed; Windows approval fields disable; macOS `openAtLogin` is enabled with `minimized: false` even if a fake `openAsHidden` is true | Spec / Research-backed | `enabled` / `minimized` / `startMinimizedSupported` | `readStartAtSignIn` → injected `get` | `openAtLogin: true` with `executableWillLaunchAtLogin: false` must read **off**; darwin must not report minimized |
| AC-61.6 | unit | Windows write clears the other argv and never passes `openAsHidden`; macOS write ignores minimized and never passes `openAsHidden`; off clears minimized | Spec | two `set` calls + returned state | `writeStartAtSignIn` | leaving the other argv registered fails; darwin `openAsHidden` on set fails |
| AC-61.7 | unit | non-boolean args throw `TypeError` and do not call Electron | Spec | throw + `set` call count 0 | `writeStartAtSignIn` | a coerced `"true"` string that still calls Electron fails |
| AC-61.8 | unit | `IPC_GET` empty/strict; `IPC_SET` both booleans required | Spec | `handleIpc.ok` | renderer invoke → `handleIpc` Zod | missing `minimized` is reject, not windowed default |
| AC-61.9 | unit | extra IPC fields reject before Electron | Spec | `handleIpc.ok` + side-effect 0 | same | `{ enabled, minimized, path }` must not reach `set` |
| AC-61.10 | unit | unsupported write returns unsupported state without throw | Spec | returned `supported: false` | `writeStartAtSignIn` on `platform`/`not-packaged` | a throw from unsupported write fails |
| AC-61.11 | unit | default off: no OS entry ⇒ `enabled: false` | Human-approved | `enabled` | `readStartAtSignIn` | first packaged launch registering a login item fails |
| AC-61.12 | unit | panel hidden when unsupported; shown when `supported: true` | Spec | `PANEL_TESTID` presence | `CONTROL_FILE` → `PAGE_FILE` | unpackaged stub that still draws the panel fails |
| AC-61.13 | unit | `MINIMIZED_TESTID` only while parent on **and** `startMinimizedSupported` | Spec / UX2 exception | checkbox presence | `CONTROL_FILE` | drawing minimized while parent is off, or on macOS (`startMinimizedSupported: false`) while parent is on, fails |
| AC-61.14 | unit | checkbox click does not `PUT /settings`; schemas omit `FORBIDDEN_SETTINGS_LEAVES` | Spec | fetch spy + schema source | `CONTROL_FILE` apply → IPC only | a PUT containing `open_at_login` fails |
| AC-61.15 | unit | `revealMainWindow` skips `show()` for argv `START_MINIMIZED_FLAG` or hide-from-login; `INDEX_FILE` has no `window.show(` and wires `revealMainWindow(window, process.argv, loginLaunchShouldHideWindow(`; tray Show still shows; no `FORBIDDEN_ELECTRON` in `INDEX_FILE` | Spec | show spy / source | `STARTUP_MODE_MODULE`; `INDEX_FILE` load path; `capture-tray.ts` unchanged | unguarded `window.show()` in `INDEX_FILE` or missing tray `show()` fails |
| AC-61.16 | unit | `HELP_FILE` section `HELP_ID` contains `HELP_STARTUP_TOKENS` | Spec | help body | HelpCard mount | missing “Task Manager” token fails |
| AC-61.17 | integration | Wave 4 unpackaged E2E: `PANEL_TESTID` count 0 | Spec | Playwright locator count | `E2E_SPEC` named `E2E_GREP` | a visible Startup panel in unpackaged Electron fails |
| AC-61.18 | unit | After stripping NSIS `;` comments, `NSH_FILE` has exactly two executable `NSH_DELETE` `NSH_HKCU` lines: `NSH_RUN_KEY`+`LOGIN_ITEM_NAME` (not StartupApproved) and `NSH_APPROVED_KEY`+`LOGIN_ITEM_NAME`. `BUILDER_YML` `nsis.include` value equals `NSH_INCLUDE`. | Spec / Research-backed | executable NSIS lines + YAML mapping | NSIS uninstall + `MEU_SCANS` negative fixture | comment-only StartupApproved plus one real Run delete fails; `include` only in a YAML comment or non-`nsis` mapping fails |
| AC-61.19 | unit | `listRegisteredChannels()` equals production+test copies at `IPC_CHANNEL_COUNT` including `IPC_GET` and `IPC_SET` | Spec / Local Canon | channel list | `IPC_FILE` + `IPC_TEST_CHANNELS` + `ipc-strict-census` | length 17 after this MEU fails |
| AC-61.20 | unit | preload keys include `PRELOAD_GET`/`PRELOAD_SET`; omitting get at runtime yields unsupported, no throw | Spec | keys + RTL | `PRELOAD_FILE` + `CONTROL_FILE` | missing method throwing in `useEffect` fails |
| AC-61.21 | unit | `ACTIONS_INDEX` contains `ACTION_IDS`; audit still resolves kebab IPC | Spec / Local Canon | index rows | `gui-actions-audit.test.ts` | dropping `settings:login_item` fails |
| AC-61.22 | unit | argv match is whole-token; a path containing the flag letters does not count | Spec | `argvHasFlag` | `STARTUP_MODE_MODULE` | substring `C:\start-minimized-tools\av-kit.exe` counting as minimized fails |

#### Spec Sufficiency Table

| Behavior | Classification | Resolution |
|----------|---------------|------------|
| Login item vs Windows service | Spec + Human-approved | `SPEC_SECTION`; USER_EXPLICIT 2026-09-20 |
| OS is SoT; no settings keys | Spec | `SPEC_SECTION` “Not a settings key” |
| macOS+Windows only; hide unpackaged | Spec + Research-backed | Electron docs platform note |
| Pinned `LOGIN_ITEM_NAME` | Spec | equals electron-builder `appId` |
| No Squirrel `Update.exe` | Spec + Research-backed | NSIS layout; Electron docs stub is Squirrel-only |
| Windows StartupApproved | Spec + Research-backed | Electron `executableWillLaunchAtLogin` / `launchItems` |
| Default off | Human-approved | USER_EXPLICIT 2026-09-20 |
| Hide minimized while parent off | Spec (UX2 exception) | `SPEC_SECTION` |
| G23 N/A | Spec | immediate OS write |
| NSIS `DeleteRegValue` both keys | Spec + Research-backed | `SPEC_UNINSTALL`; NSIS docs |
| No portable reason | Spec | 07 NSIS-only (C2) |
| E2E absence in unpackaged | Spec | Wave 4 |
| IPC kebab + `.strict()` | Local Canon | `IPC_FILE` family of `get-setup-readiness` |

#### Files Modified

| File | Action | Summary |
|------|--------|---------|
| `LOGIN_ITEM_MODULE` | new | classify / read / write |
| `STARTUP_MODE_MODULE` | new | `START_MINIMIZED_FLAG` whole-token |
| `IPC_FILE` | modify | channels, Zod, handlers |
| `PRELOAD_FILE` | modify | `PRELOAD_GET` / `PRELOAD_SET` |
| `INDEX_FILE` | modify | skip `window.show()` when minimized |
| `ENV_DTS` | modify | Window.api methods |
| `CONTROL_FILE` | new | Startup card |
| `PAGE_FILE` | modify | mount after Appearance |
| `HELP_FILE` | modify | `HELP_ID` section |
| `BUILDER_YML` | modify | `nsis.include` |
| `NSH_FILE` | new | `customUnInstall` with two executable `DeleteRegValue HKCU` lines |
| `ui/tests/unit/login-item-nsh.test.ts` | new | AC-61.18 executable deletes + comment-token negative fixture |
| `IPC_TEST_CHANNELS` | modify | two channels; `IPC_CHANNEL_COUNT` |
| `ui/tests/unit/ipc-strict-census.test.ts` | modify | length + payloads |
| `UI_TEST_FILES` | new/modify | Red/Green |
| `MOCK_API_SITES` | modify | no-op stubs |
| `ui/tests/e2e/test-ids.ts` | modify | `PANEL_TESTID`, `ENABLED_TESTID`, `MINIMIZED_TESTID` |
| `E2E_SPEC` | modify | named `E2E_GREP` |
| `ACTIONS_INDEX` | already specified | keep `ACTION_IDS` |

---

## Out of Scope

| Item | Kind | Deferred-to MEU | Basis |
|------|------|-----------------|-------|
| Windows service / WinSW / UAC / LocalSystem / “Auto-start on boot” | out-of-scope | — | `docs/build-plan/06-gui.md` Dependencies “**not** service-install”; `07-distribution.md` forbidden row MEU-61 |
| Portable `portable` refusal enum | out-of-scope | — | `07-distribution.md` Electron packaging is NSIS-only; `SPEC_SECTION` “no portable target in this MEU” |
| Command-palette rows for the login item | out-of-scope | — | `SPEC_SECTION` “Out of this card” |
| REST/MCP ownership of login-item state | out-of-scope | — | `SPEC_SECTION` OS is SoT; no settings keys |
| `openAsHidden` as Start minimized | out-of-scope | — | Electron 42: unavailable on macOS 13+; Windows does not honor it as this tray path. macOS still offers Start at sign in without Start minimized |
| Settings rail composition | deferred | MEU-58 | scheduled in `meu-status.yaml`; mockup §05 **keep** ids; `NO_LAYOUT_MEU` |
| Live packaged Run-key mutation in the agent sandbox | out-of-scope | — | `SPEC_SECTION` E2E: packaged VM proof stays Phase 7 clean-machine `[B]` |
| Linux login-item control | out-of-scope | — | Electron API documented macOS+Windows only |

---

## BUILD_PLAN.md Audit

This project **does** update hub narrative (MEU-61 residual; Next stays MEU-50). AUTOGEN tables come from `meu_status.py render` — do not hand-edit them. `HUB_CHECK` fails unless exactly one `Next:` remainder starts with `HUB_NEXT_AFTER`, every `PRIOR_PLAN_SLASHES` entry remains in `meu-status.yaml`, and `PLAN_FOLDER` is bound.

```powershell
rtk proxy pwsh -NoProfile -File docs/execution/plans/2026-09-20-p6-gui-login-item/assert-hub-next.ps1 *> C:/Temp/av-kit/build-plan-audit.txt; $code=$LASTEXITCODE; Get-Content C:/Temp/av-kit/build-plan-audit.txt; exit $code
```

---

## Verification Plan

### 1. Red UI oracle
```powershell
rtk proxy npm --prefix ui run test -- --reporter=json --outputFile=C:/Temp/av-kit/fail-to-pass-meu-61-ui.json *> C:/Temp/av-kit/fail-to-pass-meu-61-ui.txt; $code=$LASTEXITCODE; if ($code -eq 0) { Write-Error 'UI Red unexpectedly green'; exit 1 }; rtk proxy pwsh -NoProfile -File docs/execution/plans/2026-09-20-p6-gui-login-item/assert-red-oracle.ps1 -Kind ui -Receipt C:/Temp/av-kit/fail-to-pass-meu-61-ui.txt -JsonReceipt C:/Temp/av-kit/fail-to-pass-meu-61-ui.json; exit $LASTEXITCODE
```

### 2. Named E2E census + classify
```powershell
rtk proxy pwsh -NoProfile -File docs/execution/plans/2026-09-20-p6-gui-login-item/assert-e2e-named.ps1 -Mode named *> C:/Temp/av-kit/meu61-e2e-named-run.txt; $code=$LASTEXITCODE; Get-Content C:/Temp/av-kit/meu61-e2e-named-run.txt | Select-Object -Last 40; exit $code
```

### 3. MEU-61 gate
```powershell
rtk proxy pwsh -NoProfile -File docs/execution/plans/2026-09-20-p6-gui-login-item/assert-meu-gate.ps1 *> C:/Temp/av-kit/meu61-gate.txt; $code=$LASTEXITCODE; Get-Content C:/Temp/av-kit/meu61-gate.txt | Select-Object -Last 40; exit $code
```

### N. OpenAPI Drift Check

Skip unless `packages/api/` is modified. Expected skip basis: this MEU is Electron + Settings + NSIS only.

```powershell
rtk proxy uv run python tools/export_openapi.py --check openapi.committed.json *> C:/Temp/av-kit/openapi-check.txt; $code=$LASTEXITCODE; Get-Content C:/Temp/av-kit/openapi-check.txt; exit $code
```

---

## Open Questions

None. Default-off, UX2 hide-minimized, G23 N/A, no portable enum, and login-item-not-service are already source-backed in `SPEC_SECTION`.

---

## Stop conditions

- Plan-review round cap 3 without `approved` → HARD STOP.
- Execution-review round cap 6 without `approved` → HARD STOP.
- All CLI reviewer rungs unavailable → HARD STOP; never self-review.
- Do not git commit without an explicit human message.

---

## Research References

- https://www.electronjs.org/docs/latest/api/app
- https://www.electron.build/nsis
- https://nsis.sourceforge.io/Reference/DeleteRegValue
- `P:/zorivest/ui/src/main/login-item.ts`
- `P:/zorivest/ui/src/renderer/src/features/settings/StartAtSignInControl.tsx`
- `.agent/docs/emerging-standards.md` UX2, G23, G36, G37
