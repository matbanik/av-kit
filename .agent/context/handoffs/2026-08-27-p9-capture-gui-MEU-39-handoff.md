---
date: "2026-08-27"
project: "p9-capture-gui"
meu: "MEU-39"
status: "complete"
action_required: "VALIDATE_AND_APPROVE"
template_version: "2.1"
verbosity: "standard"
plan_source: "docs/execution/plans/2026-08-27-p9-capture-gui/implementation-plan.md"
build_plan_section: "bp09sCapturePage"
agent: "cursor-grok"
reviewer: "gpt-5.6-sol"
predecessor: "2026-08-27-p9-capture-api-mcp-MEU-38-handoff.md"
---

# Handoff: 2026-08-27-p9-capture-gui-MEU-39-handoff

> **Status**: `complete`
> **Action Required**: `VALIDATE_AND_APPROVE`

---

## Scope

**MEU**: MEU-39 — Capture GUI: lazy `/capture`, NavRail 5th primary after Convert (`nav-capture`, Camera, Ctrl+5 navigate-only), filmstrip + annotate viewport, F2 overlay, tray + close-to-tray, Settings Capture G23 card, Wave 9 E2E. REST/MCP unchanged (`ROUTE_COUNT_AFTER=71`, `ACTION_INDEX_AFTER=67`). Session 8c / MEU-27 stays human-gated.
**Build Plan Section**: `docs/build-plan/09-screenshot-capture.md` §GUI; `docs/build-plan/06-gui.md` Wave 9
**Predecessor**: MEU-38 Capture REST + MCP

---

## Acceptance Criteria

| AC | Type | Description | Source | Test(s) | Status |
|----|------|-------------|--------|---------|--------|
| AC-39.1 | integration | Lazy `CAPTURE_HOME`; no static `CapturePage` import; Downloader eager; Convert lazy | Spec 463 | `capture-page.test.ts` AC-39.1 | ✅ |
| AC-39.2 | integration | 5th primary after Convert; Camera / Ctrl+5; rail + Ctrl+5 navigate-only | Spec 89, 464; RULE-3 | `capture-page.test.ts` AC-39.2; W9-2 | ✅ |
| AC-39.3 | integration | Catalog `{ items }`; queryKey captures; poll 1000/5000; inbox-changed; no processor/SSE | Spec 125–131 | `capture-page.test.ts` AC-39.3 | ✅ |
| AC-39.4 | integration | Inbox Browse `show-directory-dialog`; PUT `/settings/capture` on G23 Save only | Spec 115–123; G23 | `capture-page.test.ts` AC-39.4; `capture-page.behavior.test.ts` dirty Save PUT | ✅ |
| AC-39.5 | integration | Hotkey recorder + in-use banner; `globalShortcut`; no Python `keyboard` | Spec 119–121 | `capture-page.test.ts` AC-39.5 | ✅ |
| AC-39.6 | integration | Capture region IPC `capture-region`; not FastAPI bbox; no renderer `desktopCapturer` | Spec 121, 176–177 | `capture-page.test.ts` AC-39.6 | ✅ |
| AC-39.7 | integration | Filmstrip newest-first blob thumbs; viewport selected image; no `file://`; no `open-path` on thumb | Spec 125–129, 470 | `capture-page.test.ts` AC-39.7; `capture-page.behavior.test.ts` viewport blob img | ✅ |
| AC-39.8 | unit | Four viewport tools + undo/redo + visible vectors + Text Enter/Esc; overlay HTML/script has no annotation tools | Spec 133–146 | `capture-page.test.ts` AC-39.8; `capture-page.behavior.test.ts` marks + text draft | ✅ |
| AC-39.9 | integration | Annotate Zod `.strict()` POST; no renderer `writeFileSync` | Spec 142 | `capture-page.test.ts` AC-39.9 | ✅ |
| AC-39.10 | integration | Dirty-thumb G20 portal; no `window.confirm` | Spec 144; G20 | `capture-page.test.ts` AC-39.10; W9-4 | ✅ |
| AC-39.11 | integration | Delete G20 then `DELETE /captures/{id}` | Spec 148–150; G20 | `capture-page.test.ts` AC-39.11; W9-4 | ✅ |
| AC-39.12 | integration | Open file/folder existing IPC; disabled without selection | Spec GUI notes | `capture-page.test.ts` AC-39.12; W9-5 | ✅ |
| AC-39.13 | integration | Empty `Press F2 or Capture region`; HelpCard `capture`; G26 ARIA + collapse key | Spec 111–113, 466; G26 | `capture-page.test.ts` AC-39.13 | ✅ |
| AC-39.14 | integration | Palette ids + AppShell `CAPTURE_EVENTS` + two rAF; `capture:open_folder` palette yes | G11; Spec 467–468 | `capture-page.test.ts` AC-39.14; W9-6 | ✅ |
| AC-39.15 | integration | Settings Capture card G23 explicit Save; Capture page Save PUTs; `capturePutSchema`; no `schedulePut` | Spec 474; G23 | `capture-page.test.ts` AC-39.15; `capture-page.behavior.test.ts` `capture-page-save` | ✅ |
| AC-39.16 | integration | Tray labels; Open inbox uses `showItemInFolder`; Quit sets quit intent then `app.quit` | Spec 164–165 | `capture-page.test.ts` AC-39.16; `capture-main.behavior.test.ts` tray | ✅ |
| AC-39.17 | integration | Close-to-tray hide only when not quitting; settings poll applies `close_to_tray` | Spec 165–166 | `capture-page.test.ts` AC-39.17; `capture-main.behavior.test.ts` applyCaptureRuntime | ✅ |
| AC-39.18 | integration | `globalShortcut.register` / unregister; settings poll reregisters hotkey; no Python hook | Spec 167 | `capture-page.test.ts` AC-39.18; `capture-main.behavior.test.ts` applyCaptureRuntime | ✅ |
| AC-39.19 | unit | Overlay flags; display under cursor; `getSources` before `.show(` | Spec 168, 185–186 | `capture-page.test.ts` AC-39.19 | ✅ |
| AC-39.20 | unit | Overlay Enter/Escape; preload Zod `.strict()`; vite overlay + `[name].js` | Spec 168, 183 | `capture-page.test.ts` AC-39.20 | ✅ |
| AC-39.21 | integration | Local `yyyy-MM-dd_HH-mm-ss` PNG then POST register hotkey/gui | Spec 169 | `capture-page.test.ts` AC-39.21 | ✅ |
| AC-39.22 | integration | Black/empty raw `toBitmap()` pixels; PNG container rejected; no write | Spec 187 | `capture-page.test.ts` AC-39.22; `capture-main.behavior.test.ts` inspectNativeImagePixels | ✅ |
| AC-39.23 | integration | `fs.watch` skips `annotated.png`; IPC inbox-changed; no SSE | Spec 170 | `capture-page.test.ts` AC-39.23 | ✅ |
| AC-39.24 | integration | Interactive poll 500ms; complete/cancel; no renderer import | Spec 171 | `capture-page.test.ts` AC-39.24 | ✅ |
| AC-39.25 | integration | Preload allowlist + PRELOAD_LOCK; overlay preload no `fs`/`desktopCapturer` | Spec 173–181; G27 | `capture-page.test.ts` AC-39.25 | ✅ |
| AC-39.26 | integration | Wave 9 written+wired; census; cumulative **41**; 10 Playwright passed | Spec 471, 516 | `capture-page.test.ts` AC-39.26; `capture-inbox.test.ts` W9-1…W9-6 | ✅ |
| AC-39.27 | integration | Wave0 + shell + e2e-wiring include `nav-capture` and keep `nav-convert` | 06-gui Wave 0 | `capture-page.test.ts` AC-39.27; `launch.test.ts` | ✅ |
| AC-39.28 | unit | G30–G36; §4A region `primary`/`md`, tools outline/active-primary `md`; overlay build oracle; no API/MCP edits | G30–G36; G8 | `capture-page.test.ts` AC-39.28; `capture-page.behavior.test.ts` variants | ✅ |
| AC-39.29 | unit | `parseOverlayRect` rejects extra/NaN/sub-min edge | Boundary Input Contract | `capture-page.test.ts` AC-39.29 | ✅ |
| AC-39.30 | integration | Complete/cancel `.strict()`; 404; no `shot_id`; `captures.py` untouched | MEU-37 | `capture-page.test.ts` AC-39.30 | ✅ |

<!-- CACHE BOUNDARY -->
<!-- Content above this line is stable across revision passes (KV cache prefix). -->
<!-- Content below this line changes between passes (evidence, results, corrections). -->

---

## Evidence

### FAIL_TO_PASS

| Test | Red Output (hash/snippet) | Green Output | File:Line |
|------|--------------------------|--------------|-----------|
| AC-39.1–AC-39.30 (30 distinct Vitest titles) | `PASS: RED_ORACLE ui MEU-39 AC-39 count=30`; `C:/Temp/av-kit/fail-to-pass-meu-39-ui.json` | 232 passed (34 files) | `ui/tests/unit/capture-page.test.ts`; `capture-page.behavior.test.ts`; `capture-main.behavior.test.ts`; `C:/Temp/av-kit/ui-verify.txt` |

### Commands Executed

| Command | Exit Code | Key Output |
|---------|-----------|------------|
| `assert-red-oracle.ps1 -Kind ui -Meu 39` | 0 | `PASS: RED_ORACLE ui MEU-39 AC-39 count=30` |
| UI tsc + vitest + eslint + `npm run build` + overlay outputs | 0 | 232 passed (34 files); `out/preload/overlay.js` + `out/renderer/overlay.html` (`C:/Temp/av-kit/ui-verify.txt`; copy `C:/Temp/av-kit/p9-gui-exec-r2-ui-gate.txt`) |
| MEU_SCOPED_GATE (row 4) | 0 | `PASS: MEU-39 MEU_SCOPED_GATE` (`C:/Temp/av-kit/handoff-meu-39.txt`) |
| `assert-e2e-control-census.ps1` | 0 | `PASS: E2E_CONTROL_CENSUS` (`C:/Temp/av-kit/e2e-control-census.txt`; copy `p9-gui-exec-r2-e2e-census.txt`) |
| `npx playwright test launch.test.ts capture-inbox.test.ts` | 0 | 10 passed (W9-1…W9-6 + wave0) in 58.1s (`C:/Temp/av-kit/e2e-wave9.txt`; copy `p9-gui-exec-r2-e2e.txt`) |
| OpenAPI `--check` (H1-2/H1-4) | 0 | `C:/Temp/av-kit/openapi-check.txt` |
| anti-placeholder / G36 (post-correction) | 0 | `PASS: anti-placeholder`; `PASS: G36` (`C:/Temp/av-kit/p9-gui-exec-r2-anti-placeholder.txt`; `p9-gui-exec-r2-g36.txt`) |
| `SSOT_READY` + `render --check` (H1-3) | 0 | `PASS: SSOT_READY`; drift check passed |

### Quality Gate Results

```
tsc --noEmit: pass
vitest: 232 passed (34 files) (C:/Temp/av-kit/ui-verify.txt)
eslint src/ tests/ --max-warnings 0: pass
npm run build: pass; OVERLAY_BUILD_ORACLE pass
Playwright Wave 9 + wave0: 10 passed (C:/Temp/av-kit/e2e-wave9.txt)
E2E_CONTROL_CENSUS: PASS
RED_ORACLE ui MEU-39: PASS count=30 (immutable capture-page.test.ts titles)
anti-placeholder / G36: PASS (p9-gui-exec-r2-anti-placeholder.txt / p9-gui-exec-r2-g36.txt)
IPC census: 17 channels (unchanged; settings apply is GET poll, not a new channel)
```

---

## Changed Files

| File | Action | Lines | Summary |
|------|--------|-------|---------|
| `ui/src/renderer/src/features/capture/` | new | 8 files | Page, filmstrip, viewport, catalog, commands, help, annotate Zod, settings hook |
| `ui/src/main/overlay-rect.ts` | new | schema | `parseOverlayRect` `.strict()` min edge 8 |
| `ui/src/main/capture-overlay.ts` | new | overlay | freeze `getSources` before `show`; black-frame policy |
| `ui/src/main/capture-hotkey.ts` | new | hotkey | `globalShortcut.register` / unregister |
| `ui/src/main/capture-tray.ts` | new | tray | Show / Capture region / Open inbox / Quit |
| `ui/src/main/capture-inbox-watch.ts` | new | watch | `fs.watch`; skip `annotated.png` |
| `ui/src/main/capture-register.ts` | new | register | local timestamp PNG POST; complete/cancel `.strict()` |
| `ui/src/main/overlay-preload.ts` | new | preload | Zod `.strict()` rect bridge |
| `ui/src/renderer/overlay.html` + `src/overlay.ts` | new | overlay UI | Enter/Escape; no annotation tools |
| `ui/electron.vite.config.ts` | modified | preload/renderer | second preload `overlay`; `[name].js`; `overlay.html` |
| `ui/src/renderer/src/router.tsx` | modified | capture route | lazy `/capture`; no static CapturePage import |
| `ui/src/renderer/src/components/layout/NavRail.tsx` | modified | primary | Capture 5th; Lucide `Camera`; Ctrl+5 |
| `ui/src/renderer/src/components/layout/AppShell.tsx` | modified | keys/events | Ctrl+5 navigate-only; `CAPTURE_EVENTS` + two rAF |
| `ui/src/renderer/src/registry/commandRegistry.ts` | modified | palette | `nav:capture`; `capture:region/save/open_folder` |
| `ui/src/main/ipc.ts` / `preload.ts` / `index.ts` | modified | IPC + boot | `capture-region`, `get-hotkey-status`; tray/hotkey/watch; close-to-tray |
| `ui/src/renderer/src/features/settings/` | modified | capture ns | `capturePutSchema`; Settings card G23; debounce exclude |
| `ui/src/renderer/src/features/capture/CaptureViewport.tsx` | modified | image + SVG | `imageUrl`; visible `capture-annotation`; text draft; tools `md` outline/primary |
| `ui/src/renderer/src/features/capture/CapturePage.tsx` | modified | F1/F2/F5 | blob viewport; `capture-page-save`; `downRef`; auto-select newest; region `primary`/`md` |
| `ui/src/renderer/src/features/capture/CaptureFilmstrip.tsx` | modified | AC-39.7 | `fetchAuthorizedBlob(\`/captures/${item.id}/image\`)` + `createObjectURL` / `revokeObjectURL` |
| `ui/src/renderer/src/features/capture/capture-image.ts` | new | blob | authenticated GET image → object URL |
| `ui/src/main/capture-pixels.ts` | new | F3 | `toBitmap()` raw pixels; PNG container throws |
| `ui/src/main/capture-runtime.ts` | new | F2 | GET `/settings/capture`; `applyCaptureRuntime` hotkey + watch hooks |
| `ui/src/main/capture-overlay.ts` | modified | F3 | freeze + crop via `inspectNativeImagePixels`; no `toPNG()` sampling |
| `ui/src/main/capture-tray.ts` | modified | F6 | `shell.showItemInFolder`; no `openPath` |
| `ui/src/main/index.ts` | modified | F2 | poll GET capture settings 1s; no hard-coded `closeToTray=true` / `registerCaptureHotkey('F2'` |
| `ui/tests/unit/capture-page.behavior.test.ts` | new | F4 | runtime F1/F2/F5; reuses AC-39.* IDs |
| `ui/tests/unit/capture-main.behavior.test.ts` | new | F4 | pixels, `applyCaptureRuntime`, tray `showItemInFolder` |
| `ui/tests/e2e/capture-inbox.test.ts` | modified | W9-3/4 | page Save click; selected `capture-viewport-image` |
| `docs/build-plan/06-gui.md` | modified | Wave 9 | cumulative **41** |
| `docs/build-plan/gui-actions-index.md` | modified | palette | `capture:open_folder` yes |

```diff
 const captureRoute = createRoute({
   getParentRoute: () => rootRoute,
   path: '/capture',
   pendingComponent: ModuleSkeleton,
   component: lazyRouteComponent(() => import('./features/capture/CapturePage'), 'CapturePage'),
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
| — | — | exec r1 `changes_required` F1–F6; corrections applied; awaiting r2 | — | — | open |

### Verdict

`pending` — Round 1 `changes_required`; corrections applied; Round 2 dispatch next

---

## Corrections Applied (2026-08-27)

**Findings resolved**: 6/6 (exec review Round 1 `changes_required`)

| # | Finding | Fix Applied | Verification |
|---|---------|-------------|--------------|
| F1 | Viewport never showed selected image or visible vectors; Text committed literal `"Text"` | `CaptureViewport` `imageUrl` + SVG marks (`CaptureViewport.tsx:204-216`, `53-107`); Text draft Enter/Esc (`CaptureViewport.tsx:217-236`; `CapturePage.tsx:424-444`); `downRef` so same-tick mouseup commits (`CapturePage.tsx:45`, `445-492`); authenticated blob `fetchCaptureImageObjectUrl` (`capture-image.ts:15-20`; `CapturePage.tsx:77-107`); filmstrip `fetchAuthorizedBlob(\`/captures/${item.id}/image\`)` (`CaptureFilmstrip.tsx:45-54`) | `capture-page.behavior.test.ts` AC-39.7/39.8: blob `capture-viewport-image`, visible `data-annotation-type="arrow"`, text `"Hello"` / Esc cancel. Unique AC-39 titles stay 30. W9-4 expects `capture-viewport-image` |
| F2 | Page had no Save; main hard-coded tray/inbox/clipboard/F2 | `capture-page-save` G23 (`CapturePage.tsx:361-374`); `fetchCaptureRuntime` GET `${apiBase}/settings/capture` (`capture-runtime.ts:65-76`); `applyCaptureRuntime` reregisters hotkey + restarts watch (`capture-runtime.ts:51-62`; `index.ts:454-503` poll 1000ms). No `const closeToTray = true`; no `registerCaptureHotkey('F2'` | `capture-page.behavior.test.ts` AC-39.4/15: dirty PUT `{ inbox_dir, hotkey }`. `capture-main.behavior.test.ts` applyCaptureRuntime + `/settings/capture` |
| F3 | Black-frame sampled PNG bytes via `toPNG()` | `inspectNativeImagePixels` uses `toBitmap()`; PNG container throws (`capture-pixels.ts:7-45`). Overlay freeze + crop both inspect before write (`capture-overlay.ts:74`, `157-162`). No `isBlackOrEmptyBitmap(Buffer.from(thumbnail.toPNG` | `capture-main.behavior.test.ts` AC-39.22: black true, lit false, PNG throws, overlay must not call `toPNG()` for sampling |
| F4 | Source-grep tests false-passed F1–F3 | Added runtime `capture-page.behavior.test.ts` + `capture-main.behavior.test.ts`. Did **not** neutralize `capture-page.test.ts` AC-39.* assertions | 232 passed (34 files) vs prior 225 (32). Extra RTL reuses AC-39 IDs |
| F5 | §4A variants/sizes | Region `primary`/`md` (`CapturePage.tsx:250-251`); tools `outline`/`md`, active `primary` (`CaptureViewport.tsx:33-35`, `132-167`); Undo/Redo `ghost`/`sm` (`168-172`); annotate Save `primary`/`md` (`262-263`); Delete `destructive`/`sm` (`275-277`) | `capture-page.behavior.test.ts` AC-39.28 `h-9` + `aria-pressed` |
| F6 | Tray Open inbox used `openPath` | `shell.showItemInFolder(opts.inboxDir())` (`capture-tray.ts:29`); no `openPath` in tray file | `capture-main.behavior.test.ts` AC-39.16; `capture-page.test.ts` AC-39.12 still requires `openPath` on the **page** open-file path **and** `showItemInFolder` |

---

## Deferred Items

None. Session 8c / MEU-27 remains human-gated by plan lock, not a deferral of MEU-39 scope.

---

## History

| Event | Date | Agent | Detail |
|-------|------|-------|--------|
| Created | 2026-08-27 | cursor-grok | Initial MEU-39 handoff |
| Submitted for review | 2026-08-27 | cursor-grok | Dispatch `/execution-critical-review` Round 1 |
| Exec r1 | 2026-08-27 | gpt-5.6-sol | `changes_required` F1–F6 |
| Corrections | 2026-08-27 | cursor-grok | F1–F6 fixed; 232 Vitest; 10 Playwright; re-dispatch Round 2 |
| Exec r2 | 2026-08-27 | gpt-5.6-sol | `approved`; findings_count 0 |
