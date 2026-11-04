---
date: "2026-08-21"
project: "p6-gui-settings-help"
meu: "MEU-23"
status: "complete"
action_required: "VALIDATE_AND_APPROVE"
template_version: "2.1"
verbosity: "standard"
plan_source: "docs/execution/plans/2026-08-21-p6-gui-settings-help/implementation-plan.md"
build_plan_section: "bp06s5"
agent: "cursor-grok"
reviewer: "gpt-5.6-sol"
predecessor: "2026-08-20-p6-gui-tts-models-MEU-22-handoff.md"
---

# Handoff: 2026-08-21-p6-gui-settings-help-MEU-23-handoff

> **Status**: `complete`
> **Action Required**: `VALIDATE_AND_APPROVE`

---

## Scope

**MEU**: MEU-23 — Settings page at `/settings` (`SETTINGS_HOME`), namespace cards + debounced `LEAF_PUT`, browse/apply/deps/`SETUP_READINESS`/`FFMPEG_READINESS`/`MCP_STATUS`, shared `HelpCard` + four `HELP_MODULES`, `HELP_PALETTE_DELIVER` + `settings:check_deps`, bidirectional `gui-actions-index` audit, Wave 4/6 E2E with `installSettingsSeam`. No MEU-24–25. No FastAPI/MCP rewrites. Chrome not rewound.
**Build Plan Section**: `docs/build-plan/06-gui.md` §Settings + §Help
**Predecessor**: MEU-22 TTS; Settings models Browse deferred from MEU-22

---

## Acceptance Criteria

| AC | Type | Description | Source | Test(s) | Status |
|----|------|-------------|--------|---------|--------|
| AC-23.1 | integration | `SETTINGS_HOME` at `#/settings` with populated section cards | Spec 898, 1105 | `settings-page.test.ts` AC-23.1; W4-1 | ✅ |
| AC-23.2 | integration | `BROWSE_DOWNLOAD_PATH` + downloader leaves via `LEAF_PUT` | Spec 909–921; index 31 | `settings-page.test.ts` AC-23.2; W4-3 | ✅ |
| AC-23.3 | integration | `APPLY_DEFAULTS` POST without quality body | index 30; Spec 1031 | `settings-page.test.ts` AC-23.3; W4-3 | ✅ |
| AC-23.4 | integration | `BROWSE_FFMPEG` → `{ ffmpeg_path }` | index 60; Spec 913 | `settings-page.test.ts` AC-23.4; W4-3 | ✅ |
| AC-23.5 | integration | `COOKIE_VISIBILITY` + `BROWSE_COOKIE_FILE` | Spec 915–918; index 61 | `settings-page.test.ts` AC-23.5 | ✅ |
| AC-23.6 | integration | Transcript leaves + `BROWSE_TRANSCRIPT_DIR` | Spec 924–936; index 62 | `settings-page.test.ts` AC-23.6; W4-3 | ✅ |
| AC-23.7 | integration | TTS settings + `chunk_max_chars` + models browse | Spec 938–946; index 63 | `settings-page.test.ts` AC-23.7; W4-3 | ✅ |
| AC-23.8 | integration | `APP_LEAVES` on console card | Spec 949–953 | `settings-page.test.ts` AC-23.8 | ✅ |
| AC-23.9 | integration | Theme buttons PUT `/settings/ui` `{ theme }` | Spec 957–960 | `settings-page.test.ts` AC-23.9; W4-3 | ✅ |
| AC-23.10 | integration | `CHECK_DEPS` + `DEPS_GET` | Spec 963–967; index 57 | `settings-page.test.ts` AC-23.10; W4-3 | ✅ |
| AC-23.11 | integration | `SETUP_READINESS` + `FFMPEG_READINESS` four rows | Spec 1022; lock 7 | `settings-page.test.ts` AC-23.11 | ✅ |
| AC-23.12 | integration | MCP card + `MCP_STATUS` masked yes/no | Spec 1023; index 58–59 | `settings-page.test.ts` AC-23.12; W4-3 | ✅ |
| AC-23.13 | integration | Debounced `LEAF_PUT` (`DEBOUNCE_MS` 300) | Local Canon; Spec 975 | `settings-page.test.ts` AC-23.13 | ✅ |
| AC-23.14 | unit | `ERROR_SURFACE` strict schema extra leaf | Spec 975; G15 | `settings-page.test.ts` AC-23.14 | ✅ |
| AC-23.15 | unit | `HelpCard` ARIA + `HELP_COLLAPSE_KEY` | G26 | `help-card.test.ts` AC-23.15; W6-1 | ✅ |
| AC-23.16 | unit | Four `HELP_MODULES` minimum topics | Spec 299–304 | `help-card.test.ts` AC-23.16 | ✅ |
| AC-23.17 | integration | `help:toggle` + `HELP_PALETTE_DELIVER` | index 72; G11 | `help-card.test.ts` AC-23.17; W6-1 | ✅ |
| AC-23.18 | unit | `AUDIT_PALETTE` registry ids | index 290 | `gui-actions-audit.test.ts` AC-23.18 | ✅ |
| AC-23.19 | unit | `AUDIT_TESTIDS` Phase 6 testids | index 74 | `gui-actions-audit.test.ts` AC-23.19 | ✅ |
| AC-23.20 | unit | `AUDIT_REST_IPC` OpenAPI/preload resolve | index 76 | `gui-actions-audit.test.ts` AC-23.20 | ✅ |
| AC-23.21 | integration | Wave 4 E2E Red→Green + census (23 ids + seam) | Spec 1105; E2 | `settings.test.ts` W4-1…W4-3; census | ✅ |
| AC-23.22 | integration | Wave 6 E2E Red→Green help-card + search | Spec 1107 | `help-search.spec.ts` W6-1…W6-2; census | ✅ |

<!-- CACHE BOUNDARY -->
<!-- Content above this line is stable across revision passes (KV cache prefix). -->
<!-- Content below this line changes between passes (evidence, results, corrections). -->

---

## Evidence

### FAIL_TO_PASS

| Test | Red Output (hash/snippet) | Green Output | File:Line |
|------|--------------------------|--------------|-----------|
| AC-23.1–23.20 UI | `PASS: RED_ORACLE ui` — 20 distinct failed JSON tests | 20 passed; full suite 161 passed | `C:/Temp/av-kit/fail-to-pass-meu-23-ui.txt`; `ui-green-meu-23.txt` |
| Wave 4/6 E2E | E2E_RED: 4 failed (help-card missing; W4-2/W4-3 controls) | 41 passed (5 MEU-23 + 36 prior waves); `PASS: E2E_CONTROL_CENSUS` | `C:/Temp/av-kit/e2e-red-meu-23.txt`; `e2e-wave4-wave6.txt`; `e2e-control-census.txt` |

### Commands Executed

| Command | Exit Code | Key Output |
|---------|-----------|------------|
| UI Red + `assert-red-oracle.ps1 -Kind ui` | 0 | `PASS: RED_ORACLE ui` / 20 failed JSON tests |
| UI Green tsc/vitest/eslint/build | 0 | `Tests  161 passed`; electron-vite build |
| `assert-e2e-control-census.ps1` | 0 | `PASS: E2E_CONTROL_CENSUS enforced=23` |
| Playwright waves 0–7 incl. settings + help-search | 0 | 41 passed (`e2e-wave4-wave6.txt`) |
| E2E_RED (pre-Green) | 1 | 4 failed — expected before implementation |

### Quality Gate Results

```
tsc: 0 errors
eslint: 0 warnings (max-warnings 0)
vitest: 161 passed
anti-placeholder: 0 matches (settings + help + ipc)
G36 skip/only: 0 matches
npm run build: ok
E2E_CONTROL_CENSUS: PASS (23 ids)
RED_ORACLE ui: PASS (20 distinct AC-23.1–23.20)
Playwright MEU-23 waves: 5 passed (W4-1…W4-3, W6-1…W6-2)
Playwright full regression: 41 passed
```

---

## Changed Files

| File | Action | Lines | Summary |
|------|--------|-------|---------|
| `ui/src/renderer/src/features/settings/*` | new/modify | — | `SettingsPage`, hooks, schemas, commands, help content |
| `ui/src/renderer/src/components/help/HelpCard.tsx` | new | — | ARIA disclosure + search filter + collapse key |
| `ui/src/renderer/src/features/*/downloader-help-content.ts` (etc.) | new | — | four help modules |
| `ui/src/renderer/src/features/downloader/DownloaderPage.tsx` | modified | — | mount `HelpCard` |
| `ui/src/renderer/src/features/transcript/TranscriptPage.tsx` | modified | — | mount `HelpCard` |
| `ui/src/renderer/src/features/tts/TTSPage.tsx` | modified | — | mount `HelpCard` |
| `ui/src/renderer/src/router.tsx` | modified | — | `/settings` → `SettingsPage` |
| `ui/src/renderer/src/registry/commandRegistry.ts` | modified | — | `settings:check_deps`, `help:toggle` |
| `ui/src/renderer/src/components/layout/AppShell.tsx` | modified | — | palette listeners settings/help |
| `ui/src/main/ipc.ts` | modified | — | `get-setup-readiness` + `get-mcp-access-status` |
| `ui/src/main/preload.ts` | modified | — | expose readiness + MCP status |
| `ui/src/main/index.ts` | modified | — | readiness probe deps; AVKIT_E2E dir/file dialog stubs |
| `ui/src/renderer/src/env.d.ts` | modified | — | IPC typing for new channels |
| `ui/tests/unit/settings-page.test.ts` | new | — | AC-23.1–23.14 |
| `ui/tests/unit/help-card.test.ts` | new | — | AC-23.15–23.17 |
| `ui/tests/unit/gui-actions-audit.test.ts` | new | — | AC-23.18–23.20 |
| `ui/tests/e2e/settings.test.ts` | new | — | W4-1…W4-3 + `installSettingsSeam` |
| `ui/tests/e2e/help-search.spec.ts` | new | — | W6-1…W6-2 |
| `ui/tests/e2e/test-ids.ts` | modified | — | WAVE4 + WAVE6 ids |

```diff
 case 'get-setup-readiness': {
+  const status = await deps.probeSetupReadiness?.()
+  if (status === undefined) {
+    return { ok: false, error: 'setup readiness probe unavailable' }
+  }
+  return { ok: true, value: status }
+}
+case 'get-mcp-access-status': {
+  const token = (await deps.readMcpToken?.()) ?? ''
+  return { ok: true, value: { tokenPresent: token.trim().length > 0 } }
 }
```

```diff
-  component: SettingsChrome,
+  component: SettingsPage,
   path: '/settings',
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
| — | — | pending independent review | — | — | open |

### Verdict

`changes_required` on r1 → corrections applied; awaiting r2 `approved`

---

## Corrections Applied (2026-08-21)

**Findings resolved**: 6/6 from r1 (F1–F6) + boot `randomUUID` restore

| # | Finding | Fix Applied | Verification |
|---|---------|-------------|--------------|
| F1 | Missing leaves | Full DOWNLOADER/TRANSCRIPT/TTS leaf controls | Vitest + E2E |
| F2 | SETUP_READINESS producers | `setup-readiness.ts` + readiness links | unit + UI |
| F3 | check_deps recursion | AppShell listener removed | AC-23.10 |
| F4 | help:toggle | HelpCard local event + navigate | AC-23.17 |
| F5 | ERROR_SURFACE immediate | `runSettingsAction` / putNow | handlers |
| F6 | Weak tests | Behavioral + W4-3 asserts | 164 Vitest; Wave4/6 5/5 |
| boot | randomUUID missing | import restored in main index | E2E r3 |

---

## Deferred Items

| Item | Target MEU | Basis |
|------|------------|-------|
| PyInstaller / NSIS distribution | MEU-24/25 | grouping Session 12 |
| Session 11 grouping ✅ complete mark | H2 after exec `approved` | `GROUPING_DONE_MARK` |

---

## Residual Risk

- Live yt-dlp/FFmpeg probe never exercised in E2E (by design; `installSettingsSeam` fail-closed).
- Setup readiness write-probe uses app-data models path; exotic permission layouts may differ from CI sandbox.
