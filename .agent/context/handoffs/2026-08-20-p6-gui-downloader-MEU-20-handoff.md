---
date: "2026-08-20"
project: "p6-gui-downloader"
meu: "MEU-20"
status: "complete"
action_required: "VALIDATE_AND_APPROVE"
template_version: "2.1"
verbosity: "standard"
plan_source: "docs/execution/plans/2026-08-20-p6-gui-downloader/implementation-plan.md"
build_plan_section: "bp06s2"
agent: "cursor-grok-4.6"
reviewer: "gpt-5.6-sol"
predecessor: "2026-08-19-p6-gui-shell-MEU-19-handoff.md"
---

# Handoff: 2026-08-20-p6-gui-downloader-MEU-20-handoff

> **Status**: `complete`
> **Action Required**: `VALIDATE_AND_APPROVE`

---

## Scope

**MEU**: MEU-20 — Downloader page at `/` (`DOWNLOADER_HOME`), Query poll of `{ items, processor }`, TanStack Table, SABR/cookie/queue chrome, `PALETTE_DELIVER` on AppShell, Wave 1 E2E. No MEU-21–25. No FastAPI/MCP rewrites.
**Build Plan Section**: `docs/build-plan/06-gui.md` §Downloader
**Predecessor**: MEU-19 shell

---

## Acceptance Criteria

| AC | Type | Description | Source | Test(s) | Status |
|----|------|-------------|--------|---------|--------|
| AC-20.1 | integration | `DOWNLOADER_HOME` at `/` | Spec 352–353 | `downloader-page.test.ts` AC-20.1; `launch.test.ts` | ✅ |
| AC-20.2 | unit | `QUALITY_WIRE` / `AUDIO_WIRE` defaults | Spec 439–441 | `downloader-page.test.ts` AC-20.2 | ✅ |
| AC-20.3 | integration | `CREATE_BODY` only | Spec 549 | `downloader-page.test.ts` AC-20.3 | ✅ |
| AC-20.4 | integration | `LIST_ENVELOPE` + `QUERY_KEY` | Spec 571–589 | `downloader-page.test.ts` AC-20.4 | ✅ |
| AC-20.5 | unit | Query v5 poll cadence | Spec 582–584 | `downloader-page.test.ts` AC-20.5 | ✅ |
| AC-20.6 | integration | SABR GET/POST | Spec 404–432 | `downloader-page.test.ts` AC-20.6 | ✅ |
| AC-20.7 | unit | SABR quality/audio wires | Spec 420–424 | `downloader-page.test.ts` AC-20.7 | ✅ |
| AC-20.8 | integration | Cookie PUT leaves + test paths | lock 4 | `downloader-page.test.ts` AC-20.8 | ✅ |
| AC-20.9 | integration | `ENABLED_WHEN` | Spec 503–519 | `downloader-page.test.ts` AC-20.9 | ✅ |
| AC-20.10 | unit | `REORDER_BODY` permutation | Spec 514–517 | `downloader-page.test.ts` AC-20.10 | ✅ |
| AC-20.11 | integration | Summary + processor label | Spec 521–544 | `downloader-page.test.ts` AC-20.11 | ✅ |
| AC-20.12 | integration | `ERROR_SURFACE` | G15 | `downloader-page.test.ts` AC-20.12 | ✅ |
| AC-20.13 | integration | `PALETTE_DELIVER` | G11 | `downloader-page.test.ts` AC-20.13 | ✅ |
| AC-20.14 | integration | Local download actions | index 21–29 | `downloader-page.test.ts` AC-20.14 | ✅ |
| AC-20.15 | integration | Open file/folder IPC | MEU-19 | `downloader-page.test.ts` AC-20.15 | ✅ |
| AC-20.16 | integration | Wave 1 E2E written+wired | Spec 1100; E2 | `download-queue.test.ts`; census | ✅ |
| AC-20.17 | integration | Wave0 home is downloader | lock 2 | `downloader-page.test.ts` AC-20.17; `launch.test.ts` | ✅ |
| AC-20.18 | unit | Hide audio/cookie chrome | UX2 | `downloader-page.test.ts` AC-20.18 | ✅ |
| AC-20.19 | unit | Tokens / G30 / TABLE_PIN | G30–G32 | `downloader-page.test.ts` AC-20.19 | ✅ |
| AC-20.20 | unit | G36 / anti-placeholder | G36 | `downloader-page.test.ts` AC-20.20 | ✅ |
| AC-20.21 | integration | Create `items` invalidate | downloads.py 71–83 | `downloader-page.test.ts` AC-20.21 | ✅ |
| AC-20.22 | integration | OpenAPI `--check`; no API/MCP edits | G8 | `downloader-page.test.ts` AC-20.22 | ✅ |

<!-- CACHE BOUNDARY -->
<!-- Content above this line is stable across revision passes (KV cache prefix). -->
<!-- Content below this line changes between passes (evidence, results, corrections). -->

---

## Evidence

### FAIL_TO_PASS

| Test | Red Output (hash/snippet) | Green Output | File:Line |
|------|--------------------------|--------------|-----------|
| AC-20.1–20.22 UI | `PASS: RED_ORACLE ui` — 22 distinct failed JSON tests | 51 passed (20 files) | `C:/Temp/av-kit/fail-to-pass-meu-20-ui.txt`; `ui-green-meu-20.txt` |
| Wave 1 E2E | census + Playwright not present in Red | 16 passed; `PASS: E2E_CONTROL_CENSUS` | `C:/Temp/av-kit/e2e-wave1.txt` |

### Commands Executed

| Command | Exit Code | Key Output |
|---------|-----------|------------|
| UI Red + `assert-red-oracle.ps1 -Kind ui` | 0 | `PASS: RED_ORACLE ui` / `PASS: FAIL_TO_PASS red` |
| UI Green tsc/vitest/eslint/build | 0 | `Tests  51 passed`; electron-vite build |
| `assert-e2e-control-census.ps1` + Playwright wave 0/1/5/7 | 0 | 16 passed |
| H1-2 UI verify (`ui-verify.txt`) | 0 | tsc/eslint clean; 51 vitest |
| H1-2 Python `REGRESSION_TESTS` | 0 | 298 passed (`pytest-p6-regression.txt`) |
| H1-4 OpenAPI `--check` | 0 | `openapi-check.txt` |
| Row-4 anti-placeholder / G36 | 0 | no TODO/FIXME/skip/only hits |

### Quality Gate Results

```
tsc --noEmit: 0 errors
eslint src/ tests/: 0 errors
vitest: 51 passed
playwright wave0/1/5/7: 16 passed
pytest REGRESSION_TESTS: 298 passed
OpenAPI --check: pass
anti-placeholder / G36: clean
```

---

## Changed Files

| File | Action | Lines | Summary |
|------|--------|-------|---------|
| `ui/src/renderer/src/features/downloader/*` | new | — | Page, table, hook, commands, cookies, SABR, options |
| `ui/src/renderer/src/router.tsx` | modified | — | `/` → `DownloaderPage` |
| `ui/src/renderer/src/components/layout/AppShell.tsx` | modified | — | `PALETTE_DELIVER` listeners |
| `ui/src/renderer/src/registry/commandRegistry.ts` | modified | — | `DOWNLOAD_PALETTE_IDS` |
| `ui/src/renderer/src/styles.css` | modified | — | Dracula-adjacent tokens + status colors |
| `ui/src/renderer/src/components/ui/Button.tsx` | new | — | G34 variants/sizes |
| `ui/src/main/index.ts` | modified | — | Preload `.mjs`/`.js` resolve |
| `ui/electron.vite.config.ts` | modified | — | CJS preload so `window.api` loads |
| `ui/package.json` | modified | — | `TABLE_PIN` `@tanstack/react-table ^8.21.0` |
| `ui/tests/unit/downloader-page.test.ts` | new | — | AC-20.1–20.22 |
| `ui/tests/e2e/download-queue.test.ts` | new | — | W1-1…W1-6 + `E2E_SEAM` |

```diff
-  component: ShellHome,
+  component: DownloaderPage,
```

```diff
+    "@tanstack/react-table": "^8.21.0",
```

---

## Codex Validation Report

_Left blank for reviewer agent. Reviewer fills this section during `/validation-review`._

### Recheck Protocol

1. Read Scope + AC table
2. Verify each AC against Evidence section (file:line, not memory)
3. Run all Commands Executed and compare output
4. Run Quality Gate commands independently
5. Record findings below

### Findings

| # | Severity | Finding | File:Line | Recommendation | Status |
|---|----------|---------|-----------|----------------|--------|
| 1 | — | — | — | — | — |

### Verdict

`approved` — Codex exec r2 (`findings_count: 0`). Rolling review: `.agent/context/handoffs/2026-08-20-p6-gui-downloader-implementation-critical-review.md`.

---

## Corrections Applied (2026-08-20)

**Findings resolved**: 5/5 (Codex exec r2 `approved`)

| # | Finding | Fix Applied | Verification |
|---|---------|-------------|--------------|
| F1 | Optimistic `pending-*` cache + create-envelope overwrite | Add uses `postDownloadCreate` then GET list envelope via `replaceQueueFromList`. Blank URL errors; rejected POST does not invent rows. | `downloader-page.behavior.test.ts`; `C:/Temp/av-kit/ui-green-meu-20-r2.txt` 60 passed |
| F2 | Missing Quality/Size columns | `DownloadListItem` includes `quality`/`file_size`; table headers Status/Title/Quality/Size/Progress/Speed; `formatFileSize`. | behavior table test + Wave 1 snapshot headers |
| F3 | SABR only invalidated sabr query | `invalidateDownloadsAndSabr` invalidates `QUERY_KEY` and `['downloads','sabr']`. | forceSabr spy test |
| F4 | Weak CREATE/cookie/palette/E2E seam | Rendered behavior tests; W1-4 calls `page.route` and asserts exact CREATE_BODY keys; in-page fetch stub; `apiFetch` uses `window.fetch` and skips hung IPC when `__e2eSeamInstalled`. | census + `e2e-wave1-r2.txt` 16 passed |
| F5 | Cookie test schema optional fields | Discriminated `COOKIE_TEST_BODY` by mode; negative tests. | AC-20.8 + behavior negatives |

---

## Deferred Items

| Item | Reason | Deferred-to MEU (scheduled) | Follow-up |
|------|--------|-----------------------------|-----------|
| Transcript page | Session 9 | MEU-21 | grouping Session 9 |
| TTS page | Session 10 | MEU-22 | grouping Session 10 |
| Settings / apply-defaults / theme toggle | Session 11 | MEU-23 | grouping Session 11 |

---

## History

| Event | Date | Agent | Detail |
|-------|------|-------|--------|
| Created | 2026-08-20 | cursor-grok-4.6 | Initial handoff after Red/Green/Wave 1 |
| Submitted for review | 2026-08-20 | cursor-grok-4.6 | Awaiting Codex execution review |
