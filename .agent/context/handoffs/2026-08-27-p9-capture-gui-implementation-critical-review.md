---
review_mode: implementation
target_plan: docs/execution/plans/2026-08-27-p9-capture-gui/implementation-plan.md
agent: gpt-5.6-sol
verdict: approved
findings_count: 0
round: 2
date: 2026-08-27
template_version: 2.1
dispatch_id: p9-capture-gui-exec-r2
---

# Critical Review: p9-capture-gui

> **Review Mode**: `implementation`  
> **Verdict**: `changes_required`  
> **Round**: 1  
> **Dispatch ID**: `p9-capture-gui-exec-r1`

## Intent Anchor

Session 18 is limited to MEU-39: a usable lazy `/capture` GUI with filmstrip, selected-image annotation viewport, persisted Capture settings, Electron tray/F2/region overlay, and Wave 9 evidence, while REST/MCP and Session 8c remain untouched. The shell, packaging, census, and aggregate gates are green, but the delivered Capture user loop is not complete: the viewport cannot show or visibly annotate a selected shot, Capture settings do not control Electron, and the black-frame guard cannot detect a black PNG.

## Findings

| Finding | Severity | Evidence and impact | Required correction |
|---|---|---|---|
| **F1 — The annotation viewport never renders the selected capture or visible vector overlay.** The spec requires a “selected image + vector overlay” and concrete Arrow/Box/Highlight/Text gestures (`docs/build-plan/09-screenshot-capture.md:99-104`, `docs/build-plan/09-screenshot-capture.md:133-146`; AC-39.7/39.8 at `docs/execution/plans/2026-08-27-p9-capture-gui/implementation-plan.md:190-191`). `CaptureViewportProps` has no image/item/source prop, and the non-empty viewport renders only a plain drawing `<div>` plus `sr-only` annotation labels (`ui/src/renderer/src/features/capture/CaptureViewport.tsx:6-17`, `ui/src/renderer/src/features/capture/CaptureViewport.tsx:76-98`). `CapturePage` passes `empty={items.length === 0}` rather than selected-image media (`ui/src/renderer/src/features/capture/CapturePage.tsx:332-344`), while the Text tool commits the literal string `Text` without a type/Enter/Escape workflow (`ui/src/renderer/src/features/capture/CapturePage.tsx:397-408`). A user can select a thumb and create annotation payload state, but sees a blank surface and no marks. | **High** | This breaks the central Capture review/annotate intent on valid catalog items. The independent source contract probe recorded `viewport_renders_media=false` and `viewport_accepts_selected_image=false` (`C:/Temp/av-kit/p9-gui-exec-r1-contract-probe.json`). | Add authenticated selected-image blob loading to the viewport, render the image fit-to-viewport with visible vector primitives, and implement the specified pointer/text gestures. Add runtime assertions for selected media, visible marks, text commit/cancel, and per-thumb undo/dirty behavior. |
| **F2 — Capture settings are not wired to the Capture page or Electron runtime.** The page inputs only call `settings.patchForm()` (`ui/src/renderer/src/features/capture/CapturePage.tsx:267-303`); it renders no settings Save control and never calls the hook’s available `save()` (`ui/src/renderer/src/features/capture/useCaptureSettings.ts:63-80`). More critically, Electron hard-codes `closeToTray=true`, the default inbox, clipboard false, and `F2` (`ui/src/main/index.ts:181-183`, `ui/src/main/index.ts:438-457`), and contains no `/settings/capture` read or change path. Consequently the Settings card’s PUT also cannot change the watcher directory, capture destination, clipboard behavior, registered accelerator, or close-to-tray behavior. This violates AC-39.4/39.5/39.15/39.17/39.18 (`implementation-plan.md:187-188`, `implementation-plan.md:198-201`). | **High** | Valid user edits appear accepted in renderer state/API but have no effect on the Electron-owned behavior; Capture-page edits are discarded on unmount. The independent probe recorded `page_calls_settings_save=false`, `page_has_settings_save_control=false`, `main_reads_capture_settings=false`, and `main_hardcodes_f2=true`. | Expose the G23 Save action on the Capture page, share/refetch the canonical settings state, load Capture settings before starting tray/hotkey/watch, and apply successful changes by unregistering/re-registering the hotkey, restarting the watcher, and updating capture/quit behavior. Add real main/renderer contract tests that prove each setting changes the OS surface. |
| **F3 — The black-frame guard samples PNG container bytes, so every valid PNG appears non-black.** `isBlackOrEmptyBitmap()` treats its buffer as pixel RGB (`ui/src/main/capture-overlay.ts:15-29`) but is called with `thumbnail.toPNG()` (`ui/src/main/capture-overlay.ts:89`). The first byte of every valid PNG signature is nonzero, so the loop increments immediately and returns false even for an all-black image. The cropped bitmap is not checked at all before `writeFileSync` (`ui/src/main/capture-overlay.ts:164-175`). This directly violates AC-39.22 and Spec 187 (`implementation-plan.md:205`; `docs/build-plan/09-screenshot-capture.md:187`). | **High** | Permission-blocked or black selected regions can be written and registered as successful captures, exactly the negative behavior the contract forbids. | Inspect actual raw pixel data (including alpha policy) and recheck the cropped output before any PNG write, clipboard mutation, or register POST. Add a behavioral test with a valid encoded all-black image/crop asserting no write and no POST, plus a non-black control. |
| **F4 — The scoped tests can false-pass the three behavioral defects above.** `capture-page.test.ts` labels integration ACs but mostly reads source and checks tokens; AC-39.8, AC-39.15/17/18, and AC-39.22 are examples (`ui/tests/unit/capture-page.test.ts:242-257`, `ui/tests/unit/capture-page.test.ts:325-379`, `ui/tests/unit/capture-page.test.ts:419-424`). W9-3 clicks/fills controls without asserting persistence or rendered annotation outcomes, and W9-4 clicks draw/confirm/delete controls without asserting the resulting state/request (`ui/tests/e2e/capture-inbox.test.ts:192-243`, `ui/tests/e2e/capture-inbox.test.ts:246-287`). | **Medium** | IR-5/IR-7 fail: all 30 AC IDs appear in the handoff, but integration-typed lifecycle claims are not protected by runtime/contract assertions. The suites stay green with F1-F3 present. | Keep useful source-contract checks, but add runtime assertions for the selected-image viewport, visible annotations, Capture-page Save PUT, Electron settings application, close-to-tray false, hotkey replacement, and raw-pixel black rejection. |
| **F5 — The implemented Capture controls violate the locked §4A variants/sizes.** AC-39.28 requires Capture region `primary`/`md` and the tool row to follow the plan’s `outline`/active-`primary`, `md` mapping (`implementation-plan.md:211`; §4A table). Capture region is `primary`/`sm` (`ui/src/renderer/src/features/capture/CapturePage.tsx:203-205`), while Arrow/Box/Highlight/Text are all `ghost`/`sm` (`ui/src/renderer/src/features/capture/CaptureViewport.tsx:40-54`). The current regex test checks only that `primary` occurs near `capture-region`; it never verifies `md` or the tool mapping. | **Medium** | This is a delivered UI contract mismatch, not a template issue; it weakens the intended primary/action hierarchy. | Apply the plan’s exact variants/sizes and add component assertions for every locked control, including active tool state. |
| **F6 — Tray “Open inbox folder” uses the wrong shell behavior.** The locked tray contract requires `showItemInFolder` on `inbox_dir` (AC-39.16 / dispatch focus), but `capture-tray.ts` invokes `shell.openPath()` (`ui/src/main/capture-tray.ts:27-29`). | **Medium** | The menu label exists, but its behavior differs from the established GUI action/index IPC contract (`docs/build-plan/gui-actions-index.md:72`). | Route this action through the required `showItemInFolder` behavior and add a tray callback assertion. |

## Scope

**Correlated plan:** `docs/execution/plans/2026-08-27-p9-capture-gui/implementation-plan.md` (plan review Round 4 `approved`)

**Task and named contract:**

- `docs/execution/plans/2026-08-27-p9-capture-gui/task.md`
- `docs/execution/plans/2026-08-27-p9-capture-gui/named-sets.json`

**Handoff set:**

- `.agent/context/handoffs/2026-08-27-p9-capture-gui-MEU-39-handoff.md`

**Correlation rationale:** the plan/task/grouping bind Session 18 to MEU-39 only and name one MEU handoff. Current file state was authoritative because Git availability was not assumed. Session 8c / MEU-27, `packages/api/`, and `mcp-server/` implementation changes were excluded; API/MCP were checked only through the locked 71/67 baselines.

**Implementation reviewed:** all user-named renderer Capture files, Electron overlay/hotkey/tray/watch/register/quit/preload/rect files, overlay HTML/script/build config, route/rail/AppShell/registry/HelpCard/settings/IPC/preload/index surfaces, both named Capture test files plus census, relevant build-plan/SSOT state, task/named sets, and the MEU-39 handoff.

## Commands Executed

| Verification | Result | Receipt |
|---|---|---|
| Independent UI gate: `npx tsc --noEmit`; `npx vitest run --allowOnly=false`; `npx eslint src/ tests/ --max-warnings 0`; `npm run build`; overlay output checks | pass; **225 passed (32 files)**; both overlay artifacts present | `C:/Temp/av-kit/p9-gui-exec-r1-ui-gate.txt` |
| Red oracle `assert-red-oracle.ps1 -Kind ui -Meu 39` | pass; **30** distinct AC-39 failures | `C:/Temp/av-kit/p9-gui-exec-r1-red-oracle.txt` |
| Wave 9 control census | `PASS: E2E_CONTROL_CENSUS` | `C:/Temp/av-kit/p9-gui-exec-r1-e2e-census.txt` |
| Preserved Playwright Wave 9 + Wave 0 receipt | **10 passed (56.2s)** | `C:/Temp/av-kit/e2e-wave9.txt`; summary `p9-gui-exec-r1-e2e-receipt-summary.txt` |
| OpenAPI G8 `--check` | pass; independent operation count **71** | `C:/Temp/av-kit/p9-gui-exec-r1-openapi-check.txt`; `p9-gui-exec-r1-route-count.txt` |
| MCP action-index regression | **69 passed**; ACTION_INDEX remains **67** | `C:/Temp/av-kit/p9-gui-exec-r1-mcp-action-index.txt` |
| Renderer IPC census | **17** channels | `C:/Temp/av-kit/p9-gui-exec-r1-ipc-count.txt` |
| Handoff AC census | `PASS: per-MEU AC set from HANDOFFS` | `C:/Temp/av-kit/p9-gui-exec-r1-handoff-acs.txt` |
| Capture anti-placeholder + G36 scan | clean | `C:/Temp/av-kit/p9-gui-exec-r1-anti-placeholder-g36.txt` |
| Overlay banned-term scan | no `Arrow`, `ShapeManager`, `capture-tool-arrow`, or `annotation` | `C:/Temp/av-kit/p9-gui-exec-r1-overlay-banned-terms.txt` |
| Independent viewport/settings/black-frame source contract probe | reproduced F1-F3 booleans | `C:/Temp/av-kit/p9-gui-exec-r1-contract-probe.json` |
| Review schema/self-test + frontmatter/marker checks | self-test/frontmatter/markers pass; live completion check correctly rejects non-`approved` verdict | `C:/Temp/av-kit/p9-gui-exec-r1-review-selftest.txt`; `p9-gui-exec-r1-frontmatter-check.txt`; `p9-gui-exec-r1-review-structure.txt`; `p9-gui-exec-r1-review-check.txt` |

## Checklist Results

### Implementation Review (IR)

| Check | Result | Evidence |
|---|---|---|
| IR-1 Live runtime evidence | partial | Real Electron Playwright ran with isolated `AVKIT_APP_DATA`, but route/IPC seams do not exercise live desktop capture or settings-to-main propagation. This is allowed for the desktop grab itself, not sufficient for the missing runtime contracts in F1-F3. |
| IR-2 Stub behavioral compliance | pass | No placeholder/stub hit in the scoped deliverables. |
| IR-3 Error mapping completeness | n/a | API routes were not changed or required by this MEU; OpenAPI remains 71. |
| IR-4 Fix generalization | n/a | First implementation-review round. |
| IR-5 Test rigor audit | fail (F4) | The unit file is weak for integration behavior and Wave 9 is adequate for navigation/control wiring but misses material outcomes. |
| IR-6 Boundary validation coverage | pass for delivered schemas | Annotate, Capture settings, overlay rect, complete, and cancel use strict Zod schemas; malformed rect tests execute `parseOverlayRect`. F2 is wiring/lifecycle, not an extra-field acceptance defect. |
| IR-7 Deferral and AC coverage | fail (F1-F4) | Every AC-39.1-30 ID appears in the handoff; no orphan/disguised deferral exists. Integration-typed ACs are nevertheless claimed complete without runtime evidence, and three are behaviorally false. |

### IR-5 Test Rigor Audit

| Test file | Grade | Rationale |
|---|---|---|
| `ui/tests/unit/capture-page.test.ts` | 🔴 Weak for integration claims; 🟢 strong for static locks/Zod rect | Thirty distinct titles exist, but most integration cases assert source substrings. It cannot detect missing viewport media/vectors, dead settings-to-main wiring, or PNG-container black sampling. |
| `ui/tests/e2e/capture-inbox.test.ts` | 🟡 Adequate | Real Electron proves route/rail/palette/control reachability and zero same-tick capture POSTs. Several control interactions lack outcome/request assertions, allowing F1/F2 to remain green. |

### Adversarial Verification (AV)

| Check | Result | Evidence |
|---|---|---|
| AV-1 Failing-then-passing proof | pass mechanically | Red oracle validates 30 distinct original failures; it does not prove the later runtime behavior is correct. |
| AV-2 No bypass hacks | pass | Scoped G36 scan is clean. |
| AV-3 Changed paths exercised by assertions | fail | F1-F3 are executed or source-read but not behaviorally asserted. |
| AV-4 No skipped/xfail masking | pass | No scoped skip/todo/only hit. |
| AV-5 No unresolved placeholders | pass | No scoped TODO/FIXME/NotImplementedError hit. |
| AV-6 Source-backed criteria | pass | All findings cite the approved plan/spec or explicit dispatch locks; no MEU/API/MCP expansion was introduced. |

### Passing Contract Surfaces

| Surface | Result | Evidence |
|---|---|---|
| Lazy route + rail RULE-3 | pass | Capture is lazy; Downloader eager; Convert lazy; Capture is 5th after Convert; rail/Ctrl+5 navigate only; W9-2/W9-6 zero-POST assertions pass. |
| Catalog, not queue | pass | Literal `queryKey: ['captures']`, `{ items }`, no `processor`, 1000/5000 poll, blob thumbs, and inbox-change invalidation. |
| Overlay shape boundary + packaging | pass except F3 | `getSources` precedes `win.show()`; secure transparent window flags, 8 px strict rect, shape-only overlay, dedicated preload/config/output artifacts all pass. |
| Register/complete/cancel | pass except F3 | Local timestamp, Bearer register with `hotkey`/`gui`, no `shot_id`, strict complete/cancel, and 404 handling are present. |
| Tray/quit/hotkey structure | pass except F2/F6 | Exact labels, quit intent, register/unregister, and no Python `keyboard`; settings application and folder behavior fail. |
| G20/annotate/help | pass except F1 | Portal confirms, no `window.confirm`, strict annotate payload, exact empty state, `HelpCard feature="capture"`, storage key, and eight topics are present. Visible annotation behavior fails. |
| Wave 9 / SSOT / baselines | pass | W9-1-W9-6, census 41, palette row yes, IPC 17, routes 71, actions 67, MEU-39 `ready_for_review`, all three Phase 9 plan slashes, unique Hub Next, and Session 18 pending until H2. |

## Open Questions / Assumptions

None. F1-F3 follow directly from current code paths and valid user inputs; no live desktop grab is needed to prove absent media rendering, absent settings propagation, or PNG-container sampling.

## Required Follow-up

Use `/execution-corrections` for F1-F6. Write failing behavioral tests first, preserve the 30-test Red oracle and current zero-POST rules, then rerun the complete UI gate, Wave 9 census/Playwright, OpenAPI 71, MCP action 67, IPC 17, anti-placeholder/G36, handoff AC, SSOT, and build-output checks before independent Round 2 review.

Corrections must remain inside Session 18 / MEU-39. Do not start Session 8c / MEU-27, edit `packages/api/` or `mcp-server/`, add Python `keyboard`, put annotation tools in the Electron overlay, pack Downloader/Convert into Capture, or paste/translate ShareX C#.

## Verdict

`changes_required` — F1, F2, and F3 are evidence-backed High behavioral/contract defects in the central selected-image annotation loop, Electron settings ownership, and black-frame safety policy. F4-F6 are secondary and do not independently control the verdict. The green 225-test UI suite, 10-test Playwright receipt, build/type/lint gates, Red oracle, census, OpenAPI/action/IPC baselines, and complete handoff AC list do not override these valid-input failures.

## Residual Risk

This review did not perform a live desktop grab, as requested. The shape-only overlay and build outputs were inspected, and the preserved Electron run plus independent census were used. Multi-display freeze-frame presentation and OS-level global-shortcut behavior remain runtime-sensitive areas for Round 2, but they are not additional findings here without a live isolated desktop probe.

## Recheck (2026-08-27) — Round 2

**Workflow**: `/execution-critical-review` recheck  
**Agent**: `gpt-5.6-sol`  
**Dispatch ID**: `p9-capture-gui-exec-r2`

### Intent Anchor

Session 18 is still MEU-39 only: deliver a usable lazy `/capture` GUI with authenticated filmstrip/viewport media, visible page-side annotation gestures, Save-gated Capture settings that control the Electron runtime, a shape-only 8 px region overlay, tray/hotkey/watcher ownership, and Wave 9 evidence. The corrected implementation now achieves that intent without starting Session 8c, expanding REST/MCP, adding Python `keyboard`, or moving annotation tools into the Electron overlay.

### Findings

| Finding | Severity | Evidence | Status |
|---------|----------|----------|--------|
| No surviving Round 2 finding. | — | F1–F6 are fixed, the independent gates are green, and no new evidence-backed High/Critical behavioral or contract defect survived verification. | — |

### Prior Findings Recheck (IR-4)

| Finding | Severity | Prior Status | Round 2 evidence | Recheck Result |
|---------|----------|--------------|------------------|----------------|
| **F1 — selected image, visible vectors, and Text Enter/Esc** | High | open | `CaptureViewport` accepts `imageUrl`, renders `capture-viewport-image`, emits visible SVG `capture-annotation` elements, and hosts `capture-text-draft` (`ui/src/renderer/src/features/capture/CaptureViewport.tsx:14`, `ui/src/renderer/src/features/capture/CaptureViewport.tsx:53`, `ui/src/renderer/src/features/capture/CaptureViewport.tsx:206`, `ui/src/renderer/src/features/capture/CaptureViewport.tsx:219`). `CapturePage` auto-selects the newest capture and owns the authenticated viewport blob lifecycle (`ui/src/renderer/src/features/capture/CapturePage.tsx:59`, `ui/src/renderer/src/features/capture/CapturePage.tsx:77`). Filmstrip thumbnails fetch `/captures/${item.id}/image`, create object URLs, and revoke them (`ui/src/renderer/src/features/capture/CaptureFilmstrip.tsx:45`, `ui/src/renderer/src/features/capture/CaptureFilmstrip.tsx:49`, `ui/src/renderer/src/features/capture/CaptureFilmstrip.tsx:56`). Runtime tests prove blob media, an arrow mark, `Hello` commit, and Esc cancellation (`ui/tests/unit/capture-page.behavior.test.ts:171`, `ui/tests/unit/capture-page.behavior.test.ts:208`). The overlay HTML/script banned-term sweep is clean. | **Fixed** |
| **F2 — Capture settings wired to page Save and Electron** | High | open | The page exposes dirty-only `capture-page-save` and calls `settings.save()` (`ui/src/renderer/src/features/capture/CapturePage.tsx:367`, `ui/src/renderer/src/features/capture/CapturePage.tsx:374`). Main fetches `/settings/capture`, applies changed hotkey/inbox hooks, updates close-to-tray/clipboard state, and polls every second (`ui/src/main/capture-runtime.ts:51`, `ui/src/main/capture-runtime.ts:65`, `ui/src/main/index.ts:454`, `ui/src/main/index.ts:469`, `ui/src/main/index.ts:501`). There is no `const closeToTray = true`, no `registerCaptureHotkey('F2'`, and no new settings IPC. Runtime tests prove exactly one dirty Save PUT plus hotkey/watch reconfiguration and false close-to-tray state (`ui/tests/unit/capture-page.behavior.test.ts:259`, `ui/tests/unit/capture-main.behavior.test.ts:49`). | **Fixed** |
| **F3 — black-frame guard uses raw pixels** | High | open | `inspectNativeImagePixels()` calls `toBitmap()` and rejects a PNG container passed as pixels (`ui/src/main/capture-pixels.ts:7`, `ui/src/main/capture-pixels.ts:33`, `ui/src/main/capture-pixels.ts:42`). The frozen image is inspected before the overlay is shown, and the cropped image is inspected before PNG conversion/write (`ui/src/main/capture-overlay.ts:68`, `ui/src/main/capture-overlay.ts:74`, `ui/src/main/capture-overlay.ts:130`, `ui/src/main/capture-overlay.ts:156`, `ui/src/main/capture-overlay.ts:166`). AC-39.22 proves black/lit raw buffers and the PNG-container throw (`ui/tests/unit/capture-main.behavior.test.ts:19`). | **Fixed** |
| **F4 — tests false-passed F1–F3** | Medium | open | The immutable source-contract file still has 30 distinct AC-39.* IDs; the added behavior files reuse those IDs, so the union remains AC-39.1–AC-39.30. Renderer behavior tests exercise selected media/vectors, text commit/cancel, dirty-only Save, and locked variants (`ui/tests/unit/capture-page.behavior.test.ts:171`, `ui/tests/unit/capture-page.behavior.test.ts:208`, `ui/tests/unit/capture-page.behavior.test.ts:259`, `ui/tests/unit/capture-page.behavior.test.ts:285`). Main behavior tests exercise raw pixels, runtime settings application, and tray behavior (`ui/tests/unit/capture-main.behavior.test.ts:19`, `ui/tests/unit/capture-main.behavior.test.ts:49`, `ui/tests/unit/capture-main.behavior.test.ts:95`). W9-3 clicks enabled page Save and W9-4 asserts `capture-viewport-image` (`ui/tests/e2e/capture-inbox.test.ts:227`, `ui/tests/e2e/capture-inbox.test.ts:260`). | **Fixed** |
| **F5 — locked §4A variants/sizes** | Medium | open | Capture region and annotated Save are `primary`/`md`; Delete is `destructive`/`sm` (`ui/src/renderer/src/features/capture/CapturePage.tsx:250`, `ui/src/renderer/src/features/capture/CapturePage.tsx:262`, `ui/src/renderer/src/features/capture/CapturePage.tsx:275`). Tool buttons are `md`, inactive `outline`, active `primary`, and expose `aria-pressed`; Undo/Redo remain `ghost`/`sm` (`ui/src/renderer/src/features/capture/CaptureViewport.tsx:33`, `ui/src/renderer/src/features/capture/CaptureViewport.tsx:132`, `ui/src/renderer/src/features/capture/CaptureViewport.tsx:168`). AC-39.28 asserts `h-9` and active-state transitions (`ui/tests/unit/capture-page.behavior.test.ts:285`). | **Fixed** |
| **F6 — tray Open inbox folder** | Medium | open | The tray callback uses `shell.showItemInFolder(opts.inboxDir())` and contains no `openPath` (`ui/src/main/capture-tray.ts:27`). AC-39.16 asserts both facts (`ui/tests/unit/capture-main.behavior.test.ts:95`), while AC-39.12 still finds the existing page open-file `openPath` surface. | **Fixed** |

### Commands Executed

| Verification | Result | Receipt |
|---|---|---|
| Independent UI gate: `npx tsc --noEmit`; `npx vitest run --allowOnly=false`; ESLint; Electron build; overlay output checks | pass; **232 passed (34 files)**; `out/preload/overlay.js` and `out/renderer/overlay.html` present | `C:/Temp/av-kit/p9-gui-exec-r2-ui-gate.txt`; copied to `C:/Temp/av-kit/ui-verify.txt` |
| Original Red oracle `assert-red-oracle.ps1 -Kind ui -Meu 39` | pass; **30** distinct AC-39 failures | `C:/Temp/av-kit/p9-gui-exec-r2-red-oracle.txt` |
| Current AC-ID census across immutable + behavior tests | base **30**, union **30**, last `AC-39.30` | `C:/Temp/av-kit/p9-gui-exec-r2-ac-title-census.txt` |
| Independent Wave 9 control census | `PASS: E2E_CONTROL_CENSUS` | `C:/Temp/av-kit/p9-gui-exec-r2-e2e-census.txt` |
| Preserved isolated Electron Wave 9 + Wave 0 receipt | **10 passed (58.1s)** | `C:/Temp/av-kit/e2e-wave9.txt`; re-read via `C:/Temp/av-kit/p9-gui-exec-r2-e2e-preserved.txt` |
| OpenAPI G8 `--check` plus exact operation census | pass; **71** routes | `C:/Temp/av-kit/p9-gui-exec-r2-openapi-check.txt`; `C:/Temp/av-kit/p9-gui-exec-r2-route-count.txt` |
| MCP action-index/capture/convert/M7 regression set | **96 passed**; ACTION_INDEX **67** | `C:/Temp/av-kit/p9-gui-exec-r2-mcp-action-index.txt` |
| Renderer-to-main IPC census | **17** channels | `C:/Temp/av-kit/p9-gui-exec-r2-ipc-count.txt` |
| F1–F6 plus lazy route, G20, freeze order, shape boundary, min edge, catalog, G23, HelpCard, and W9 source-order/absence sweep | all checks pass | `C:/Temp/av-kit/p9-gui-exec-r2-contract-sweep-final.txt` |
| Plan-review provenance, SSOT/grouping/handoff lines, and canonical-path pre-edit guard | pass | `C:/Temp/av-kit/p9-gui-exec-r2-plan-review-proof.txt`; `C:/Temp/av-kit/p9-gui-exec-r2-ssot-handoff-lines.txt`; `C:/Temp/av-kit/p9-gui-exec-r2-pre-edit-guard.txt` |

### Round 1 Passing-Surface Spot Checks

| Surface | Result | Evidence |
|---|---|---|
| Lazy `/capture`, RULE-3, and navigation-only W9-2/W9-6 | pass | Lazy-route source sweep passes; both compact request listeners assert `capturePostCount === 0` (`ui/tests/e2e/capture-inbox.test.ts:176`, `ui/tests/e2e/capture-inbox.test.ts:310`). |
| Catalog/blob boundary | pass | `useCaptureCatalog.ts` has no `processor`; viewport/filmstrip use authenticated object URLs; no filmstrip `file://`. |
| G20, G23, and HelpCard | pass | Capture confirms use `createPortal` with no `window.confirm`; capture settings hook has no `schedulePut`; HelpCard retains key shape ``av-kit:${feature}-help:${tabKey}:state``. |
| Overlay/tray/runtime boundary | pass | Freeze precedes `win.show()`, min edge is 8 px on both dimensions, overlay surface contains no annotation-tool terms, raw freeze/crop pixels are checked, and tray uses `showItemInFolder`. |
| Locked baselines and state | pass | IPC 17, routes 71, actions 67, MEU-39 `ready_for_review` bound without trailing slash, Phase 9 retains engine/API-MCP/GUI plan slashes, Hub `Next:` is unique and correct, and Session 18 remains pending until H2. |

### Checklist Results

| Check | Result | Evidence |
|---|---|---|
| IR-1 Live runtime evidence | pass within the declared seam | Real Electron Wave 9/0 ran 10/10 with isolated `AVKIT_APP_DATA`; renderer behavior tests exercise the corrected DOM/fetch paths. Per the approved contract, no live desktop grab was required. |
| IR-2 Stub behavioral compliance | pass | No placeholder/stub was found on the corrected paths; full UI build and runtime suites pass. |
| IR-3 Error mapping completeness | n/a | MEU-39 does not change or require edits to REST routes; OpenAPI remains 71. |
| IR-4 Fix generalization | pass | F1–F6 were checked across renderer, Electron main, behavior tests, E2E, and shared page/open-path boundaries. |
| IR-5 Test rigor audit | pass | No weak scoped test surface remains; per-file grades follow. |
| IR-6 Boundary validation coverage | pass | Existing strict Capture settings/annotation/overlay boundaries remain green; 8 px and raw-pixel negative paths are directly asserted. |
| IR-7 Deferral and AC coverage | pass | All 30 AC IDs remain represented; Session 8c is a scheduled human-gated MEU-27, not a disguised deferral; no new MEU was invented. |
| AV-1 through AV-6 | pass | Preserved Red oracle, no AC-ID/test neutralization, corrected paths asserted, no placeholder/skip bypass, and all reviewed behavior is source-backed. |

### IR-5 Test Rigor Grades

| Test file | Grade | Rationale |
|---|---|---|
| `ui/tests/unit/capture-page.test.ts` | 🟡 Adequate for static/contract locks | Exactly 30 immutable AC titles cover source, schema, census, packaging, and absence contracts; runtime-sensitive claims are now paired with behavior suites. |
| `ui/tests/unit/capture-page.behavior.test.ts` | 🟢 Strong | Renders the real component with QueryClient and mocked authenticated fetch, then value-asserts blob media, visible vectors, Text Enter/Esc, one dirty Save PUT, and control state. |
| `ui/tests/unit/capture-main.behavior.test.ts` | 🟢 Strong for corrected seams | Value-asserts raw black/lit buffers, rejects PNG-container sampling, proves hotkey/watch reapplication plus false close-to-tray state, and locks tray folder behavior. |
| `ui/tests/e2e/capture-inbox.test.ts` | 🟢 Strong for the approved Electron seam | Real Electron covers W9-1–W9-6, Save clicks an enabled dirty action, viewport media is visible, G20 flows execute, and navigation/palette POST-zero oracles are explicit. |

### Structured Result

```yaml
findings: []
summary: "Round 1 F1-F6 are fixed; independent UI, Electron, census, OpenAPI, action-index, IPC, Red-oracle, and contract sweeps pass."
```

### Open Questions / Assumptions

None. Current files and isolated receipts were authoritative because Git availability was not assumed.

### Verdict

`approved` — all six Round 1 findings are fixed with direct file evidence and materially stronger runtime regression protection. `findings_count` is 0 because no new evidence-backed High/Critical behavioral or contract finding survived the generate→verify pass.

### Follow-up and Residual Risk

No `/execution-corrections` follow-up is required. The outer orchestrator may proceed with H2 closeout for Session 18; grouping remains intentionally pending until that post-review work. This review did not modify product code, tests, plans, MEU handoffs, `packages/api/`, or `mcp-server/`, and did not start Session 8c / MEU-27. No live desktop grab was performed; multi-display presentation and OS-level global-shortcut behavior remain environment-sensitive residual risks already bounded by the approved Electron seam, not findings.
