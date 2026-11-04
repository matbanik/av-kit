---
date: "2026-09-20"
project: "2026-09-20-p9-capture-annotate-edit"
meu: "MEU-60"
status: "complete"
action_required: "VALIDATE_AND_APPROVE"
template_version: "2.1"
verbosity: "standard"
plan_source: "docs/execution/plans/2026-09-20-p9-capture-annotate-edit/implementation-plan.md"
build_plan_section: "bp09s9.9"
agent: "cursor-grok-4.6-xhigh"
reviewer: "gpt-5.6-sol"
predecessor: "2026-09-19-p9-capture-annotate-arrow-text-MEU-59-handoff.md"
---

# Handoff: 2026-09-20-p9-capture-annotate-edit-MEU-60-handoff

> **Status**: `complete`
> **Action Required**: `VALIDATE_AND_APPROVE`

---

## Scope

**MEU**: MEU-60 — `gui-capture-annotate-edit-until-save`. Select-mode Capture overlay editing until Save: arrow body + two CSS-constant endpoint handles, move committed text / box / highlight, compact mark list + Remove mark, Apply/Cancel color, original-image sampler, rubber-band preview, shared Save guard (button + palette `capture:save`). MEU-59 `FIT_MAP` / arrowhead / text-anchor stay. Same annotation DTO. No REST/MCP schema fork.

**Build Plan Section**: [09 §Annotation edit until Save](../../../docs/build-plan/09-screenshot-capture.md#annotation-edit-until-save) (matrix 9.9)

**Predecessor**: [`2026-09-19-p9-capture-annotate-arrow-text-MEU-59-handoff.md`](2026-09-19-p9-capture-annotate-arrow-text-MEU-59-handoff.md)

**Deliberately NOT in this MEU.** Phase 11 / MEU-50 page layout. New types (`circle`, `marker`, freehand, numbered callouts, blur). New drawing engines (`NO_NEW_PACKAGES`). Box resize, text-field drag/re-edit, OS EyeDropper, selected stroke/font/bg rewrite. In-overlay ShapeManager. GIF/video/OCR. Auto-commit. Phase 10 queue-card work stays uncommitted separately.

---

## Acceptance Criteria

> **AC-table integrity (control C4).** All **19** plan ACs (AC-60.1–60.19) appear below with plan Type, Source, Test(s), and status.

| AC | Type | Description | Source | Test(s) | Status |
|----|------|-------------|--------|---------|--------|
| AC-60.1 | unit | CSS hit radii constant across fit scales; letterbox miss; selected-arrow handles beat bodies; coincident from/to selects `to` | Spec edit hit-test | `capture-hit-test.test.ts` | ✅ |
| AC-60.2 | unit | Body translate keeps arrow delta; endpoint edit keeps the other end; box size unchanged; collapsing nonzero arrow cancels | Spec arrow/box edit | `capture-hit-test.test.ts` | ✅ |
| AC-60.3 | unit | `textBackgroundBox` plate hittable when `bg_color` is empty | Spec text edit; Local Canon `TEXT_MODULE` | `capture-hit-test.test.ts` | ✅ |
| AC-60.4 | integration | Arrow tool drag over an existing mark creates a new arrow then auto-Select; Select mode moves the targeted mark | Spec Select mode; Human-approved 2026-09-20 | `capture-page.behavior.test.ts` | ✅ |
| AC-60.5 | integration | Enter commits text; later drag moves x,y; draft pointer does not start a second draft | Spec text edit | `capture-page.behavior.test.ts` | ✅ |
| AC-60.6 | integration | Many move events coalesce to one undo restoring the start; Esc does not push history | Spec history; Local Canon `applyHistory` | `capture-page.behavior.test.ts` | ✅ |
| AC-60.7 | integration | Mark list shows all four types; click selects a covered mark; Remove mark drops that annotation only | Spec mark list | `capture-page.behavior.test.ts` | ✅ |
| AC-60.8 | integration | Well/hex update a candidate only; Apply writes `#RRGGBB`; Cancel writes nothing; named green is not dirty | Spec color; Research-backed React input | `capture-page.behavior.test.ts` | ✅ |
| AC-60.9 | unit | `SAMPLER_ORACLE` rgb → `#12ABCD`; overlay/letterbox/stale/nonopaque do not change the candidate | Spec sampler; Canvas getImageData | `capture-sample.test.ts` | ✅ |
| AC-60.10 | integration | Button and palette `capture:save` refuse when a transaction is open | Spec Save; MEU-59 overlayReady | `capture-page.behavior.test.ts` | ✅ |
| AC-60.11 | integration | Save POSTs the committed list without preview geometry; annotated view has no SVG marks | Spec Save; MEU-59 edit vs bake | `capture-page.behavior.test.ts` | ✅ |
| AC-60.12 | integration | Named Playwright: create arrow+text, drag ends and text, sample, Apply, Save, reload, annotated has no SVG | Spec Wave 9; testing-strategy E2E | `ui/tests/e2e/capture-inbox.test.ts` | ✅ |
| AC-60.13 | integration | Select uses outline/primary; color well/Apply/Cancel/Sample visible; handles only for selected arrow on original | Spec color + Select; G34 | `capture-page.behavior.test.ts` | ✅ |
| AC-60.14 | unit | Exact `UI_DEP_NAMES` / `UI_DEVDEP_NAMES` / `PY_DEP_ALLOWLIST`; `NO_NEW_PACKAGES` remain named examples | Human-approved 2026-09-19 | `assert-meu-scans.ps1` | ✅ |
| AC-60.15 | unit | HelpCard four-tools body includes `HELP_EDIT_SENTENCE` | G26; Spec edit | `capture-help-content.test.ts` | ✅ |
| AC-60.16 | integration | Arrow down+move before up draws a preview with no extra undo step; valid up appends once | Spec rubber-band | `capture-page.behavior.test.ts` | ✅ |
| AC-60.17 | unit | `NAMED_COLOR_HEX` maps every `NAMED_COLORS` name; unknown names are not coerced | Spec color mapping | `capture-color.test.ts` | ✅ |
| AC-60.18 | unit | Exact annotation DTO + MCP actions; `annotateInSchema` is `.strict()` | Spec MCP; Human-approved | `assert-meu-scans.ps1` | ✅ |
| AC-60.19 | integration | Nudge inspector body/tail/head; Delete removes only with annotation focus; Esc cancels without history | Spec keyboard; Astra keyboard access | `capture-page.behavior.test.ts` | ✅ |

<!-- CACHE BOUNDARY -->
<!-- Content above this line is stable across revision passes (KV cache prefix). -->
<!-- Content below this line changes between passes (evidence, results, corrections). -->

---

## Evidence

### FAIL_TO_PASS

| Test | Red Output (hash/snippet) | Green Output | File:Line |
|------|--------------------------|--------------|-----------|
| AC-60.1–.11, .13, .15–.17, .19 (16 UI titles) | `C:/Temp/av-kit/fail-to-pass-meu-60-ui.txt` + `.json`; `assert-red-oracle.ps1 -Kind ui` PASS count=16 | Scoped `C:/Temp/av-kit/meu60-ui-scoped.txt` **35 passed** (5 files). Exec-review correction Red `meu60-corr-red.txt` then Green `meu60-corr-green3.txt` **28** behavior passed | `ui/tests/unit/capture-*.test.ts`; `capture-page.behavior.test.ts` |
| AC-60.12 | `C:/Temp/av-kit/fail-to-pass-meu-60-e2e.txt` + `.json`; `assert-e2e-classify.ps1 -Mode red` assertion-fail | `C:/Temp/av-kit/meu60-e2e.txt` + `.json`; classify `-Mode named` **PASS: named E2E AC-60.12**; `-Mode gate` PASS | `ui/tests/e2e/capture-inbox.test.ts` |

### Commands Executed

| Command | Exit Code | Key Output |
|---------|-----------|------------|
| `npm --prefix ui run test` Red + `assert-red-oracle.ps1 -Kind ui` | 1 then oracle 0 | 16 failed titles |
| `assert-e2e-census.ps1` + Playwright `--grep AC-60.12` Red + classify `-Mode red` | 1 then classify 0 | assertion-fail Red |
| `npm --prefix ui run test` Green (editor/color/save) | 0 | 526 passed |
| Named Playwright `--grep AC-60.12` + classify `-Mode named` | 0 | `PASS: named E2E AC-60.12` |
| Exec-review r1 correction Red then Green behavior | 1 then 0 | 8 failed → 28 passed (`meu60-corr-red.txt` / `meu60-corr-green3.txt`) |
| `assert-e2e-classify.ps1 -Mode gate` | 0 | `PASS: named E2E from Green raw+JSON plus pass receipt` |

### Quality Gate Results

```
typecheck/lint: PASS
scoped MEU-60 vitest: 35 passed (5 files); behavior 28 passed after r1 corrections
full ui vitest: 3 failed / 527 passed — MEU-61 concurrent (`**41**`/`**35**` in 06-gui.md, `login-item-set`); not this MEU
mcp-server vitest: 215 passed (9 files)
pytest adapter+service+api: 59 passed
Playwright AC-60.12: 1 passed (~33s named run after r1 corrections)
OpenAPI --check: pass (no regen)
anti-placeholder / G36 / NO_NEW_PACKAGES / DTO scan: 0 hits
E2E classify -Mode gate: PASS
```

---

## Changed Files

> Delta-only excerpts. Phase 10 queue-card files are **not** this MEU.

| File | Action | Lines | Summary |
|------|--------|-------|---------|
| `ui/src/renderer/src/features/capture/capture-hit-test.ts` | new | 1–263 | `hitTestMarks`, `translateBody`, `moveEndpoint`, CSS radii, `markLabel` |
| `ui/src/renderer/src/features/capture/capture-color.ts` | new | 1+ | `NAMED_COLOR_HEX`, `normalizeHex`, `displayHex`, `hexForNamedColor` |
| `ui/src/renderer/src/features/capture/capture-sample.ts` | new | 1+ | `rgbToHex`, `sampleOriginalPixel` (epoch / opaque / in-bounds) |
| `ui/src/renderer/src/features/capture/CaptureViewport.tsx` | modified | Select/handles/list/color/sample/nudge | Select mode chrome; pointer+mouse surface; `onSurfacePointer` |
| `ui/src/renderer/src/features/capture/CapturePage.tsx` | modified | pointer machine | transient preview; `applyHistory` previous-first; sampler epoch; Save guard; baked annotated |
| `ui/src/renderer/src/features/capture/capture-commands.ts` | modified | 71+ | `setCaptureSaveAllowed` shared with palette Save |
| `ui/src/renderer/src/features/capture/capture-help-content.ts` | modified | 27 | `HELP_EDIT_SENTENCE` |
| `ui/src/renderer/src/features/capture/capture-fit-map.ts` | modified | export | `fitScaleOrigin` shared with hit-test/sampler |
| `ui/scripts/playwright-with-outputfile.mjs` | new | wrapper | maps `--outputFile` → `PLAYWRIGHT_JSON_OUTPUT_NAME` |
| `ui/playwright.config.ts` | modified | json reporter | env-gated json+list |
| `ui/package.json` | modified | `test:e2e` | points at wrapper |
| `ui/tests/unit/capture-hit-test.test.ts` | new | AC-60.1–.3 | Red-first hit/geometry |
| `ui/tests/unit/capture-color.test.ts` | new | AC-60.17 | named hex map |
| `ui/tests/unit/capture-sample.test.ts` | new | AC-60.9 | sampler oracle |
| `ui/tests/unit/capture-page.behavior.test.ts` | modified | AC-60.4–.11,.13,.16,.19 | PointerEvent polyfill + editor/color/save |
| `ui/tests/unit/capture-help-content.test.ts` | modified | AC-60.15 | Help sentence |
| `ui/tests/e2e/capture-inbox.test.ts` | modified | AC-60.12 | named edit-until-Save path |
| `ui/tests/e2e/test-ids.ts` | modified | Select/handles/nudge/color | `E2E_TESTIDS` |

```diff
 # CapturePage.tsx applyHistory
+  const previous = annotationsRef.current
   overlayEditGen.current += 1
-  setPast((stack) => [...stack, annotationsRef.current])
+  setPast((stack) => [...stack, previous])
```

```diff
 # capture-commands.ts
+export function setCaptureSaveAllowed(gate: () => boolean): void { ... }
+  if (!saveAllowed()) return false
```

```diff
 # CaptureViewport.tsx
+  capture-tool-select / capture-handle-from|to / capture-mark-list
+  capture-color-well|apply|cancel|sample / capture-nudge-body|tail|head
+  onSurfacePointer + pointer session skips synthesized mouse
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

## Corrections Applied

_None yet. First execution-review round pending._

---

## Deferred Items

| Item | Reason | Deferred-to MEU (scheduled) | Follow-up |
|------|--------|-----------------------------|-----------|
| Circle / marker / freehand / numbered callouts / blur | Named Phase 9 deferral; Human-approved 2026-09-19/20 | stays in `09-screenshot-capture.md` named deferrals (not MEU-50) | spec lift later |
| Box resize, text-field drag/re-edit, OS EyeDropper | Astra extras; Human-approved 2026-09-20 out of MEU-60 | stays named-out of MEU-60 | spec lift later |
| Phase 11 Capture page layout | Layout, not overlay edit | MEU-50 (already scheduled) | do not start here |

---

## History

| Event | Date | Agent | Detail |
|-------|------|-------|--------|
| Created | 2026-09-20 | cursor-grok-4.6-xhigh | Initial handoff after Green + named E2E + MEU-60 gate |
| Submitted for review | 2026-09-20 | cursor-grok-4.6-xhigh | Sent to gpt-5.6-sol |
