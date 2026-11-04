# Session Digest — 64d28ec9-61b4-4f5f-a398-3342c15cdbf9

**Date:** 2026-09-20
**Project:** p6-gui-login-item (MEU-61 per-user Start when I sign in)
**Duration:** multi-compaction session

## Decisions Made

| # | Decision | Authority | Source |
|---|----------|-----------|--------|
| 1 | Copy Zorivest Settings login item, not WinSW “Auto-start on boot” | Human-approved | USER_EXPLICIT 2026-09-20 after discovery |
| 2 | Dedicated MEU-61; OS is SoT; default off; no `PUT /settings` | Spec | 06-gui §Startup (login item) |
| 3 | Hide the panel when unpackaged or Linux (`not-packaged` / `platform`) | Spec | 06-gui; AC-61.17 |
| 4 | Darwin: `openAtLogin` only; never `openAsHidden`; no Start minimized | Codex-verified | Exec review r2/r3 Electron 42 / macOS 13+ |
| 5 | `revealMainWindow` is the only post-load `show()` path | Codex-verified | Exec review r3 AC-61.15 |
| 6 | Hub Next stays Phase 11 MEU-50; do not start it | Human-approved | USER_EXPLICIT lock |
| 7 | Commit MEU-61 only; leave queue-card / Capture dirty; do not push | Human-approved | USER_EXPLICIT this run |

## Blockers & Open Questions

Unpackaged `npm run dev` hides the Settings panel by contract. SSOT `meu-status.yaml` / AUTOGEN `BUILD_PLAN.md` stay dirty so this commit does not claim Phase 10/11 complete without that code.

## Test & Quality-Gate Outcomes

| Gate | Result | Notes |
|------|--------|-------|
| Codex plan review | Approved (r2) | r1 PCR-1–4 hub/NSIS/E2E/classifier |
| Codex exec review | Approved (r3) | r1/r2 High darwin minimized; r3 `revealMainWindow` |
| Focused vitest | 43 passed | login-item suite |
| Playwright AC-61.17 | 1 passed | unpackaged panel absence |
| Git commit | Scoped, not pushed | MEU-61 only; queue-card and leftover Capture remain dirty |

## Files Changed

### New Files
- `ui/src/main/login-item.ts` / `startup-mode.ts` — classify, set, hide-from-login-launch
- `ui/src/renderer/src/features/settings/StartAtSignInControl.tsx` — Settings checkboxes
- `ui/build/installer.nsh` — NSIS `DeleteRegValue` on uninstall
- Plan, handoff, reflection, grouping for `p6-gui-login-item`

### Modified Files
- Main IPC/preload/`index.ts`, Settings page, `06-gui.md` / `07-distribution.md`
- Surgical: `test-ids.ts`, `gui-actions-audit.test.ts`, `metrics.md`, matrix 6.6 only

## Provenance

- Conversation ID: `64d28ec9-61b4-4f5f-a398-3342c15cdbf9`
- Transcript: `C:\Users\Mat\.cursor\projects\p-av-kit\agent-transcripts\64d28ec9-61b4-4f5f-a398-3342c15cdbf9\64d28ec9-61b4-4f5f-a398-3342c15cdbf9.jsonl`
- Reflection: `docs/execution/reflections/2026-09-20-p6-gui-login-item-reflection.md`
