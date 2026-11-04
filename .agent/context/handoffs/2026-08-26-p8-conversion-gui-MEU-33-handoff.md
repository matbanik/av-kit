---
date: "2026-08-26"
project: "p8-conversion-gui"
meu: "MEU-33"
status: "complete"
action_required: "VALIDATE_AND_APPROVE"
template_version: "2.1"
verbosity: "standard"
plan_source: "docs/execution/plans/2026-08-26-p8-conversion-gui/implementation-plan.md"
build_plan_section: "bp08sConvertPage"
agent: "cursor-grok"
reviewer: "gpt-5.6-sol"
predecessor: "2026-08-26-p8-conversion-api-mcp-MEU-32-handoff.md"
---

# Handoff: 2026-08-26-p8-conversion-gui-MEU-33-handoff

> **Status**: `complete`
> **Action Required**: `VALIDATE_AND_APPROVE`

---

## Scope

**MEU**: MEU-33 — Convert GUI: lazy `/convert`, NavRail 4th primary after TTS (`nav-convert`, Film, Ctrl+4 navigate-only), Downloader-shaped queue, presets, G23 Save, G20 portal confirms, HelpCard `converter`, Wave 8 E2E. REST/MCP unchanged (`ROUTE_COUNT_AFTER=61`, `ACTION_INDEX_AFTER=59`).
**Build Plan Section**: `docs/build-plan/08-video-conversion.md` §Convert page; `docs/build-plan/06-gui.md` Wave 8
**Predecessor**: MEU-32 `avkit_convert` MCP

---

## Acceptance Criteria

| AC | Type | Description | Source | Test(s) | Status |
|----|------|-------------|--------|---------|--------|
| AC-33.1 | integration | Lazy `CONVERT_HOME`; `lazyRouteComponent` without static `ConvertPage` import; Downloader stays eager | Spec 521; 06-gui 912 | `convert-page.test.ts` AC-33.1; `convert-queue.test.ts` W8-1 | ✅ |
| AC-33.2 | integration | 4th primary after TTS; `nav-convert` / Film / Ctrl+4; NavRail + Ctrl+4 navigate-only (zero POST) | Spec 53–57; RULE-3 | `convert-page.test.ts` AC-33.2; `convert-queue.test.ts` W8-2 | ✅ |
| AC-33.3 | unit | Task radios swap options; queue/staging unchanged | Spec 120–122 | `convert-page.test.ts` AC-33.3 | ✅ |
| AC-33.4 | unit | Five preset chips; `PRESET_WIRES` + labels; Advanced resets to catalog; saved `default_preset` hydrates Compress selection | Spec 134–157 | `convert-page.test.ts` AC-33.4; `convert-page.behavior.test.ts` AC-33.4 (GET archival → POST `preset: archival`) | ✅ |
| AC-33.5 | unit | Advanced collapsed; CQ/scale/audio/gpu wires; refresh POST; chip not a select; Advanced disclosure Compress-only | Spec 148–190 | `convert-page.test.ts` AC-33.5; `convert-page.behavior.test.ts` AC-33.5 (Cut hides `convert-advanced`) | ✅ |
| AC-33.6 | unit | Cut/Extract fields; `parseConvertTime`; invalid range skips Add POST | Spec 159–179 | `convert-page.test.ts` AC-33.6 | ✅ |
| AC-33.7 | integration | Browse `show-files-dialog` video+audio filters; drop `getPathForFile`; drop does not auto-POST | Spec 124–132 | `convert-page.test.ts` AC-33.7; `convert-page.behavior.test.ts` AC-33.7 (IPC filters); W8-4 | ✅ |
| AC-33.8 | integration | Create body discriminated union `.strict()`; extra key skips fetch | MEU-31; RULE-2 | `convert-page.test.ts` AC-33.8 | ✅ |
| AC-33.9 | integration | `{ items, processor }`; `QUERY_KEY` `["conversions"]`; poll 1000/5000 | Spec 206 | `convert-page.test.ts` AC-33.9 | ✅ |
| AC-33.10 | integration | Queue table columns; `JOB_STATUSES`; processor hidden when Idle | Spec 192–204 | `convert-page.test.ts` AC-33.10 | ✅ |
| AC-33.11 | integration | Start/Pause/Resume/Cancel/reorder + ffmpeg gate | Spec 204; MEU-20 | `convert-page.test.ts` AC-33.11 | ✅ |
| AC-33.12 | unit | Reorder full permutation; never `[]` | Session 14 RULE-1 | `convert-page.test.ts` AC-33.12 | ✅ |
| AC-33.13 | integration | Palette ids dispatch events; AppShell owns listeners; two-rAF deliver | G11; Spec 526; RULE-3 | `convert-page.test.ts` AC-33.13; W8-6 | ✅ |
| AC-33.14 | integration | G20 portal remove/clear; no `window.confirm` | G20 | `convert-page.test.ts` AC-33.14; W8-4 | ✅ |
| AC-33.15 | integration | GPU chip GET + labels; missing FFmpeg disables Add/Start | Spec 181–190 | `convert-page.test.ts` AC-33.15 | ✅ |
| AC-33.16 | integration | Settings Convert card; G23 explicit Save; no `schedulePut`; PUT only on Save with four keys | Spec 531; G23 | `convert-page.test.ts` AC-33.16; `convert-page.behavior.test.ts` AC-33.16 (0 PUT while dirty, 1 four-key PUT); W8-3 `__e2eConverterPuts` 0→1 | ✅ |
| AC-33.17 | integration | Page output/skip share converter form; persist only on Save | Spec 102; G23 | `convert-page.test.ts` AC-33.17; `convert-page.behavior.test.ts` AC-33.17 (`convert-page-save` PUT) | ✅ |
| AC-33.18 | integration | HelpCard `converter`; ARIA + collapse key; Spec 208–210 topics | Spec 524; G26 | `convert-page.test.ts` AC-33.18 | ✅ |
| AC-33.19 | integration | Open file/folder existing IPC; disabled without path | Spec 204; MEU-19 | `convert-page.test.ts` AC-33.19 | ✅ |
| AC-33.20 | integration | In-page `ApiError`; Add/Start not swallowed | G15 | `convert-page.test.ts` AC-33.20 | ✅ |
| AC-33.21 | integration | Wave 8 written+wired; census interaction totality; cumulative 35 | Spec 529; 06-gui 1138 | `convert-page.test.ts` AC-33.21; `convert-queue.test.ts` W8-1…W8-6 | ✅ |
| AC-33.22 | integration | Wave0 + shell + e2e-wiring include `nav-convert` | 06-gui Wave 0 | `convert-page.test.ts` AC-33.22; `launch.test.ts` | ✅ |
| AC-33.23 | unit | G30–G35 + G36 / anti-placeholder on converter + new IPC | G30–G36 | `convert-page.test.ts` AC-33.23 | ✅ |
| AC-33.24 | integration | OpenAPI `--check` 0; no `packages/api/` or MCP edits | G8 | `convert-page.test.ts` AC-33.24 | ✅ |

<!-- CACHE BOUNDARY -->
<!-- Content above this line is stable across revision passes (KV cache prefix). -->
<!-- Content below this line changes between passes (evidence, results, corrections). -->

---

## Evidence

### FAIL_TO_PASS

| Test | Red Output (hash/snippet) | Green Output | File:Line |
|------|--------------------------|--------------|-----------|
| AC-33.1–AC-33.24 (24 distinct Vitest titles) | `PASS: RED_ORACLE ui MEU-33 AC-33 count=24`; JSON `numFailedTests=25` (24 AC + one extra `nav:convert` gui-actions-audit fail on the same Red run) | 195 passed (31 files) after exec-r1 fixes | `C:/Temp/av-kit/fail-to-pass-meu-33-ui.json`; `C:/Temp/av-kit/ui-green-meu-33-r2.txt` |

### Commands Executed

| Command | Exit Code | Key Output |
|---------|-----------|------------|
| `assert-red-oracle.ps1 -Kind ui -Meu 33` | 0 | `PASS: RED_ORACLE ui MEU-33 AC-33 count=24` |
| UI tsc + vitest + eslint + `npm run build` | 0 | 195 passed (31 files); Vite client build (`C:/Temp/av-kit/ui-green-meu-33-r2.txt`) |
| `assert-e2e-control-census.ps1` | 0 | `PASS: E2E_CONTROL_CENSUS` |
| `npx playwright test launch.test.ts convert-queue.test.ts` | 0 | 10 passed (W8-1…W8-6 + wave0) in 1.2m (`C:/Temp/av-kit/e2e-wave8.txt` post-r1) |
| `export_openapi.py --check openapi.committed.json` | 0 | in sync |

### Quality Gate Results

```
tsc --noEmit: pass
vitest: 195 passed (31 files) (C:/Temp/av-kit/ui-green-meu-33-r2.txt)
eslint src/ tests/ --max-warnings 0: pass
npm run build: pass
Playwright Wave 8 + wave0: 10 passed (C:/Temp/av-kit/e2e-wave8.txt)
E2E_CONTROL_CENSUS: PASS
RED_ORACLE ui MEU-33: PASS count=24 (unique AC-33 titles; extra RTL cases reuse 33.4/5/7/16/17)
OpenAPI --check: pass (C:/Temp/av-kit/openapi-check-meu-33.txt)
anti-placeholder / G36: recorded in MEU_SCOPED_GATE receipt
```

---

## Changed Files

| File | Action | Lines | Summary |
|------|--------|-------|---------|
| `ui/src/renderer/src/features/converter/` | new | 12 files | Page, queue table, body Zod, commands, controls, GPU, help, presets, time, queue hook, settings hook (`ready`), `convert-filters.ts` |
| `ui/src/renderer/src/styles/form-guard.css` | new | G23 | `btn-save-dirty` pulse |
| `ui/src/renderer/src/router.tsx` | modified | 46–51 | Lazy `/convert`; no static ConvertPage import |
| `ui/src/renderer/src/components/layout/NavRail.tsx` | modified | 16 | Convert 4th primary; Lucide `Film` |
| `ui/src/renderer/src/components/layout/AppShell.tsx` | modified | 50–54, 120–175 | Ctrl+4 navigate-only; always-mounted convert listeners; `/convert` help route |
| `ui/src/renderer/src/registry/commandRegistry.ts` | modified | 101–318 | `nav:convert` Ctrl+4; convert palette dispatches events only |
| `ui/src/renderer/src/components/help/HelpCard.tsx` | modified | 14 | feature union includes `converter` |
| `ui/src/renderer/src/features/settings/SettingsPage.tsx` | modified | Convert card | G23 Save; no `schedulePut('converter')` |
| `ui/src/renderer/src/features/settings/settings-schemas.ts` | modified | 66–82 | `converterPutSchema` `.strict()` |
| `ui/src/renderer/src/features/settings/useSettingsPage.ts` | modified | DebouncedNamespace | converter excluded from debounce |
| `ui/src/main/ipc.ts` / `preload.ts` / `index.ts` | modified | new channel | `show-files-dialog` + `webUtils.getPathForFile` |
| `ui/tests/unit/convert-page.test.ts` | new | AC-33.* | 24 distinct titles (source + helper) |
| `ui/tests/unit/convert-page.behavior.test.ts` | new | RTL | Runtime F1–F4: archival POST, Compress-only Advanced, video+audio filters, G23 PUT |
| `ui/tests/e2e/convert-queue.test.ts` | new | W8-1…W8-6 | Playwright seam; W8-3 `__e2eConverterPuts` 0→1 |
| `docs/build-plan/06-gui.md` | modified | 1138 | Wave 8 cumulative **35** |

```diff
 const convertRoute = createRoute({
   getParentRoute: () => rootRoute,
   path: '/convert',
   pendingComponent: ModuleSkeleton,
   component: lazyRouteComponent(() => import('./features/converter/ConvertPage'), 'ConvertPage'),
 })
```

`packages/api/` and `mcp-server/` were not edited.

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

`pending` — implementer does not author the verdict

---

## Corrections Applied (2026-08-26)

**Findings resolved**: 4/4 (exec review Round 1 `changes_required`)

| # | Finding | Fix Applied | Verification |
|---|---------|-------------|--------------|
| F1 | Saved `converter.default_preset` ignored; Convert always started at `PRESET_DEFAULT` (`balanced`) | `ConvertPage` hydrates preset + catalog Advanced + `gpu_preference` from `converter.form` when `converter.ready` and `presetTouched` is false; chip click sets the ref | `convert-page.behavior.test.ts` AC-33.4: GET archival → archival chip `bg-accent` → Add POST `{ preset: "archival" }` |
| F2 | Browse sent only a Video filter | `convert-filters.ts` `CONVERT_DIALOG_FILTERS` Video (`mp4,mkv,mov,webm,avi,m4v`) + Audio (`mp3,wav,m4a,aac,flac,ogg,opus,wma,ac3`); Browse maps mutable `{name,extensions}` into `showFilesDialog` | `convert-page.behavior.test.ts` AC-33.7 asserts the exact IPC filter array |
| F3 | Advanced not Compress-only; Cut/Extract opened an empty card with GPU Refresh | Advanced button + card only when `kind === 'compress'`; leaving Compress closes Advanced; hidden `convert-gpu-refresh` remains for census when the card is closed | `convert-page.behavior.test.ts` AC-33.5: Cut removes `convert-advanced`; W8-3 still clicks Advanced while on Compress |
| F4 | AC-33.16/17 were source-grep only | RTL PUT/dirty assertions; W8-3 tracks `__e2eConverterPuts` (0 before Save, 1 after) and `btn-save-dirty` | `convert-page.behavior.test.ts` AC-33.16/17; W8-3; unique AC-33 title count stays 24 |

---

## Deferred Items

| Item | Reason | Deferred-to MEU (scheduled) | Follow-up |
|------|--------|-----------------------------|-----------|
| Console polish | out-of-scope; human-gated | MEU-27 | Session 8c stays pending |
| Downloader → Convert handoff | out-of-scope | — | Spec 08 ~535–541 |
| UnsavedChangesModal L3 | G23 L3 N/A this MEU | — | plan G23_CONVERT |

---

## History

| Event | Date | Agent | Detail |
|-------|------|-------|--------|
| Created | 2026-08-26 | cursor-grok | Initial MEU-33 handoff |
| Submitted for review | 2026-08-26 | cursor-grok | Dispatch `/execution-critical-review` Round 1 |
| Exec r1 | 2026-08-26 | gpt-5.6-sol | `changes_required` F1–F4 |
| Corrections | 2026-08-26 | cursor-grok | F1–F4 fixed; 195 Vitest; 10 Playwright; re-dispatch Round 2 |
| Exec r2 | 2026-08-26 | gpt-5.6-sol | `approved`; findings_count 0 |
