# Phase 6 residual — GUI login item · Session grouping

> **Source:** USER_EXPLICIT 2026-09-20 (`Modify the build files now and @.agent/workflows/create-plan.md` after the Zorivest autostart discovery).
> **Generated:** 2026-09-20
> **Method:** `/create-plan` for the login-item recommendation (not Zorivest Service Manager “Auto-start on boot”).
> **Origin:** av-kit Settings has no per-user login item. Zorivest has two surfaces; only `StartAtSignInControl` / `login-item.ts` (MEU-495) matches av-kit’s Electron-owned FastAPI child and NSIS per-user install.
> **Status:** Complete — MEU-61 exec review r3 `approved`.

---

## 1. MEU / scope summary

| MEU | Slug | Covers | Layer | Depends on |
|-----|------|--------|-------|------------|
| MEU-61 | `gui-login-item` | Per-user “Start av-kit when I sign in” + “Start minimized”; Electron `setLoginItemSettings`; OS is SoT; hidden unpackaged/Linux; pinned `LOGIN_ITEM_NAME`; NSIS `DeleteRegValue`; `--start-minimized` skips `window.show()` | ui main + Settings + NSIS | MEU-23, MEU-25 |

Findings → MEU:

| Finding | MEU |
|---------|-----|
| Zorivest “Auto-start on boot” is WinSW / UAC / LocalSystem | **out of scope** (06-gui not service-install; 07 forbidden row) |
| Zorivest Settings “Start when I sign in” is the login-item | MEU-61 |
| Unpackaged `electron.exe` must not enter HKCU Run | MEU-61 (`not-packaged`) |
| Task Manager can disable without deleting the Run value | MEU-61 (`executableWillLaunchAtLogin` / `launchItems[].enabled`) |
| Uninstall must not leave a dead Startup entry | MEU-61 (`installer.nsh`) |
| Portable packaged extract path | **out of scope** this MEU (07 NSIS-only; add `portable` later) |
| Phase 11 Settings rail | **deferred** to MEU-58 (keep ids) |

---

## 2. Dependency graph + critical path

```
MEU-23 (approved) ─┐
                   ├─► MEU-61
MEU-25 (approved) ─┘
```

Critical path: MEU-23 + MEU-25 → MEU-61.

Parallel: MEU-50 (Phase 11) stays independently unblocked. This session does not steal MEU-50 or MEU-58.

---

## 3. Recommended grouping — 1 session

| # | Slug | MEUs | Why grouped | Token calibration | Split? |
|---|------|------|-------------|-------------------|--------|
| 1 | `p6-gui-login-item` | MEU-61 | Single residual; same Settings page + Electron main + NSIS uninstall | Calibrate vs `p6-gui-settings-help` (one GUI settings MEU + Wave 4) | No |

---

## 4. Plan-creation pathway

`/create-plan` → `docs/execution/plans/2026-09-20-p6-gui-login-item/`

---

## 5. Prerequisite gate

Can begin after plan review `approved`: MEU-23 and MEU-25 are approved.

---

## 6. Session summary

| Session | Status | Plan folder |
|---------|--------|-------------|
| `p6-gui-login-item` | complete | `docs/execution/plans/2026-09-20-p6-gui-login-item/` |
