---
date: "2026-09-19"
project: "2026-09-19-p9-capture-annotate-arrow-text"
meu: "MEU-59"
status: "complete"
action_required: "VALIDATE_AND_APPROVE"
template_version: "2.1"
verbosity: "standard"
plan_source: "docs/execution/plans/2026-09-19-p9-capture-annotate-arrow-text/implementation-plan.md"
build_plan_section: "bp09s9.8"
agent: "cursor-grok-4.6-xhigh"
reviewer: "gpt-5.6-sol"
predecessor: "2026-08-27-p9-capture-native-picker-MEU-40-handoff.md"
---

# Handoff: 2026-09-19-p9-capture-annotate-arrow-text-MEU-59-handoff

> **Status**: `complete`
> **Action Required**: `VALIDATE_AND_APPROVE`

---

## Scope

**MEU**: MEU-59 — `gui-capture-annotate-arrow-text`. Repair the shipped Capture editor so **arrow pointer** and **text** overlays use original-image pixels (`FIT_MAP`), SVG preview matches Pillow bake (`ARROWHEAD_FORMULA`, `TEXT_ANCHOR` + optional `bg_color` plate), Save is fail-closed, GET `/{id}` reloads the sidecar into draft+saved, and MCP `annotate`/`image` keep the same DTO. Circle/marker are **not** added.

**Build Plan Section**: [09 §Annotation geometry (arrow + text)](../../../docs/build-plan/09-screenshot-capture.md) (matrix 9.8)

**Predecessor**: [`2026-08-27-p9-capture-native-picker-MEU-40-handoff.md`](2026-08-27-p9-capture-native-picker-MEU-40-handoff.md)

**Deliberately NOT in this MEU.** Phase 11 / MEU-50 page layout. New annotation types (`circle`, `marker`, freehand, numbered callouts, blur). New drawing engines (`NO_NEW_PACKAGES`: Konva/Fabric/Sharp/generative). New MCP action (`suggest`). In-overlay ShapeManager. GIF/video/OCR. Auto-commit. Phase 10 queue-card work stays uncommitted separately.

---

## Acceptance Criteria

> **AC-table integrity (control C4).** All **20** plan ACs (AC-59.1–59.20) appear below with plan Type, Source, Test(s), and status.

| AC | Type | Description | Source | Test(s) | Status |
|----|------|-------------|--------|---------|--------|
| AC-59.1 | unit | `FIT_MAP` maps 1600×900 in 800×600 at (400,300) → (800,450); letterbox y&lt;oy → null | Spec geometry; MDN object-fit | `capture-fit-map.test.ts` | ✅ |
| AC-59.2 | unit | Shared arrowhead vertices for `[0,0]→[100,0]` stroke 3 match bake and preview (head 12, angle 0.4) | Spec geometry; Local Canon | `test_capture_adapter.py::test_ac_59_2`; `capture-arrow-head.test.ts` | ✅ |
| AC-59.3 | unit | Bake `text`/`textbbox` use `anchor="la"`; `bg_color` fills that bbox first | Spec geometry; Pillow | `test_capture_adapter.py::test_ac_59_3` | ✅ |
| AC-59.4 | integration | SVG `viewBox="0 0 W H"` + `xMidYMid meet`; pointer uses `FIT_MAP`; no `devicePixelRatio` multiply | Spec geometry | `capture-page.test.ts`; `capture-page.behavior.test.ts` | ✅ |
| AC-59.5 | integration | Arrow drag commits image-pixel mark; hypot==0 creates no mark | Spec viewport tools | `capture-page.behavior.test.ts` | ✅ |
| AC-59.6 | integration | Text draft at mapped coords; Enter commits `font_size`/`bg_color`; Esc cancels; composing Enter does not commit; dirty includes nonempty draft | Spec viewport + dirty | `capture-page.behavior.test.ts` | ✅ |
| AC-59.7 | integration | Invalid annotate body → POST count 0 + status/error; success POSTs full list; original PNG unchanged | Spec annotate; Boundary | `capture-page.behavior.test.ts`; `saveAnnotations` | ✅ |
| AC-59.8 | integration | GET `/{id}` includes `annotations`; select loads draft+saved; missing sidecar `[]`; malformed/unknown 422 does not wipe to `[]` | Spec sidecar | `test_capture_service.py`; `test_api_captures.py`; `capture-page.behavior.test.ts` | ✅ |
| AC-59.9 | integration | Default original + SVG marks; annotated view loads `?variant=` and renders zero `capture-annotation` | Spec geometry | `capture-page.behavior.test.ts` | ✅ |
| AC-59.10 | unit | Color schema: `NAMED_COLORS` or `#RRGGBB` only (`chartreuse` fails) | Domain `NAMED_COLORS` | `capture-annotate.test.ts`; `test_api_captures.py` | ✅ |
| AC-59.11 | integration | `circle`/`marker` → Zod null / API 422; rect still valid | Spec named deferrals; Human-approved 2026-09-19 | `capture-annotate.test.ts`; `test_api_captures.py::test_ac_59_11` | ✅ |
| AC-59.12 | integration | Playwright title contains `AC-59.12`; arrow+text+Save+reload both marks remain | Spec Wave 9 | `ui/tests/e2e/capture-inbox.test.ts` | ✅ |
| AC-59.13 | integration | Arrow shows stroke, hides font/bg; text shows `capture-font-size` + `capture-text-bg`; G34 variants | Spec `font_size`; G34 | `capture-page.behavior.test.ts` | ✅ |
| AC-59.14 | unit | None of `NO_NEW_PACKAGES` in `ui/package.json` or Python project deps | Human-approved 2026-09-19 | `assert-meu-scans.ps1` | ✅ |
| AC-59.15 | integration | OpenAPI GET `/{id}` has `annotations`; GET `/captures` item schema does not | Spec `CaptureShotOut`; G8 | `test_api_captures.py`; `export_openapi.py --check` | ✅ |
| AC-59.16 | integration | MCP `annotate` still posts `{annotations:[arrow,text,…]}`; one example; no `suggest`; no forbidden types | Spec MCP; Astra GUI-first | `mcp-server/tests/capture.test.ts` | ✅ |
| AC-59.17 | integration | Committed `font_size` equals `capture-font-size` (not hardcoded 16) | Spec text fields | `capture-page.behavior.test.ts` | ✅ |
| AC-59.18 | unit | Same image point maps from two container sizes; stored `{from,to}` unchanged on resize | Spec zoom/resize | `capture-fit-map.test.ts` | ✅ |
| AC-59.19 | integration | SVG text `text-anchor="start"` + `dominant-baseline="hanging"`; `bg_color` sibling plate matches `TEXT_MODULE` | Spec geometry; Pillow | `capture-text-metrics.test.ts`; `capture-page.behavior.test.ts` | ✅ |
| AC-59.20 | unit | HelpCard four-tools body contains `HELP_PIXEL_SENTENCE` | G26; Spec Save/reload | `capture-help-content.test.ts` | ✅ |

<!-- CACHE BOUNDARY -->
<!-- Content above this line is stable across revision passes (KV cache prefix). -->
<!-- Content below this line changes between passes (evidence, results, corrections). -->

---

## Evidence

### FAIL_TO_PASS

| Test | Red Output (hash/snippet) | Green Output | File:Line |
|------|--------------------------|--------------|-----------|
| AC-59.2 / AC-59.3 / AC-59.8 / AC-59.10 / AC-59.11 / AC-59.15 | `C:/Temp/av-kit/fail-to-pass-meu-59-py.txt` — adapter `arrowhead_vertices` missing; text `la`/bg fail; GET detail/sidecar/circle 422 fail | pytest adapter+service+api Green (`C:/Temp/av-kit/meu59-api.txt` 43 passed; bake receipt) | `tests/unit/test_capture_adapter.py:436`; `test_capture_service.py:618`; `tests/e2e/test_api_captures.py` |
| AC-59.1, .4–.7, .9, .13, .17–.20 | `C:/Temp/av-kit/fail-to-pass-meu-59-ui.json` `numFailedTests: 15` / 492 passed of 507 | `C:/Temp/av-kit/meu59-ui-green.txt` 507 passed (62 files); sidecar/Zod add-on later 15 passed in two files | `ui/tests/unit/capture-*.test.ts` |
| AC-59.16 | MCP Red JSON + `assert-red-oracle.ps1 -Kind mcp` | `C:/Temp/av-kit/meu59-mcp.txt` 215 passed (9 files) | `mcp-server/tests/capture.test.ts:333` |
| AC-59.12 | `C:/Temp/av-kit/fail-to-pass-meu-59-e2e.txt` expected 1 arrow, received 0 (13.9s) | `C:/Temp/av-kit/meu59-e2e.txt` **1 passed (18.8s)** after FIT_MAP origin, `overlayEditGen`, `img` `draggable={false}` | `ui/tests/e2e/capture-inbox.test.ts:353` |

### Commands Executed

| Command | Exit Code | Key Output |
|---------|-----------|------------|
| pytest adapter+service+api Red + `assert-red-oracle.ps1 -Kind py` | 1 then oracle 0 | FAIL_TO_PASS py |
| `npm --prefix ui run test` Red + oracle `-Kind ui` | 1 then oracle 0 | 15 failed / 492 passed |
| `assert-e2e-census.ps1` + Playwright `--grep AC-59.12` Red | 1 | 0 arrows |
| MCP Red + oracle `-Kind mcp` | 1 then oracle 0 | AC-59.16 |
| pytest adapter Green; UI Green; API+OpenAPI; MCP Green; E2E Green | 0 | bake / 507 / 43 / `--check` / 215 / 1 passed |
| `assert-meu-gate.ps1` | 0 | `PASS: MEU-59 gate` (`C:/Temp/av-kit/meu59-gate.txt`) |

### Quality Gate Results

```
assert-meu-gate.ps1: PASS (typecheck, lint, vitest, pytest, OpenAPI --check, MCP 215, E2E census, NO_NEW_PACKAGES + G36 + placeholder)
ui vitest (H1-2): 509 passed (62 files)
ui vitest sidecar/Zod add-on: 15 passed (2 files)
mcp-server vitest: 215 passed (9 files)
pytest adapter+service+api: 59 passed
Playwright AC-59.12: 1 passed (18.8s)
anti-placeholder / G36 / konva-family: 0 hits
```

---

## Changed Files

> Delta-only excerpts. Phase 10 queue-card files are **not** this MEU.

| File | Action | Lines | Summary |
|------|--------|-------|---------|
| `packages/infrastructure/src/avkit_infra/capture/adapter.py` | modified | 50+, 259, 283 | `arrowhead_vertices`; `_apply_arrow` uses it; `_apply_text` `anchor="la"` + bg plate |
| `packages/core/src/avkit_core/services/capture.py` | modified | 112, 259 | sidecar parse; `load_shot_annotations`; unknown type 422 |
| `packages/api/src/avkit_api/schemas/captures.py` | modified | 110, 129 | `COLOR_PATTERN`; `CaptureShotDetailOut.annotations` |
| `packages/api/src/avkit_api/routes/captures.py` | modified | 74+ | GET `/{id}` returns detail + annotations |
| `openapi.committed.json` | modified | CaptureShotDetailOut | regen after `--check` drift |
| `ui/src/renderer/src/features/capture/capture-fit-map.ts` | new | 30 | `FIT_MAP` |
| `ui/src/renderer/src/features/capture/capture-arrow-head.ts` | new | 27 | `arrowHeadPoints` |
| `ui/src/renderer/src/features/capture/capture-text-metrics.ts` | new | 18 | start/hanging + bg box |
| `ui/src/renderer/src/features/capture/CaptureViewport.tsx` | modified | 105–346 | viewBox, FIT_MAP, tool fields, view toggle, img no native drag |
| `ui/src/renderer/src/features/capture/CapturePage.tsx` | modified | 115–135, 310 | GET load + `overlayEditGen`; Save only if `saveAnnotations()` true |
| `ui/src/renderer/src/features/capture/capture-commands.ts` | modified | 69 | fail-closed boolean |
| `ui/src/renderer/src/features/capture/capture-annotate.ts` | modified | color enum | `NAMED_COLORS` \| `#RRGGBB` |
| `ui/src/renderer/src/features/capture/capture-image.ts` | modified | variant | `?variant=` |
| `ui/src/renderer/src/features/capture/capture-help-content.ts` | modified | 27 | `HELP_PIXEL_SENTENCE` |
| `mcp-server/src/toolsets/capture.ts` | modified | 20–30 | arrow+text example; no new action |
| tests (py/ui/mcp/e2e) | modified/new | AC-59.* | Red-first then Green |

```diff
 # adapter.py _apply_text
-  draw.text((x, y), text, fill=...)
+  bbox = draw.textbbox((x, y), text, font=font, anchor="la")
+  if bg_color: draw.rectangle(bbox, fill=bg)
+  draw.text((x, y), text, fill=..., anchor="la")
```

```diff
 # CaptureViewport.tsx
+  viewBox={`0 0 ${W} ${H}`}
+  preserveAspectRatio="xMidYMid meet"
+  img draggable={false} pointer-events-none
```

```diff
 # CapturePage.tsx
+  GET /captures/${id} → parseAnnotateBody → setAnnotations + setSaved
+  overlayEditGen ignores late GET after local draw
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

## Corrections Applied (2026-09-19)

**Findings resolved**: 5/5 (EXR1-1 … EXR1-5) pending independent re-review.

| # | Finding | Fix Applied | Verification |
|---|---------|-------------|--------------|
| EXR1-1 | Cross-shot Save / empty Save before GET | `overlayReady` quarantine: clear draft on `selectedId` change; Save/draw disabled until detail GET succeeds | `capture-page.behavior.test.ts` delayed GET + 422 cases |
| EXR1-2 | `run()` cleared `capture-status` after invalid Save | Save no longer uses `run()`; failed `saveAnnotations()` leaves the error event | AC-59.7 clicks `capture-save` and asserts nonempty status + 0 POST |
| EXR1-3 | Sidecar filtered non-objects to `[]` | `parse_sidecar_document` raises on non-dict elements | `test_capture_service.py` scalar/`None` 422 |
| EXR1-4 | SVG plate used `0.6*font*len` at `(x,y)` | Shared Segoe `la` glyph table; plate for `Hi@16` is `(10,26,15×12)` matching Pillow `(10,26,25,38)` | `text_plate_box`; `capture-text-metrics.test.ts`; viewport plate attrs |
| EXR1-5 | E2E counted nodes only | Playwright asserts POST `from/to` `[2,2]→[6,6]`, text `{x:3,y:6,text:Note,font_size:18}` | `C:/Temp/av-kit/meu59-e2e-r2.txt` 1 passed (21.0s) |

H1-2 rerun after fixes: `C:/Temp/av-kit/full-verify-gate-r2.txt` PASS. UI vitest **510 passed**. Python scoped **59 passed**.

---

## Deferred Items

Named product deferrals (not ACs; already scheduled elsewhere or explicitly out of scope):

| Item | Reason | Deferred-to MEU (scheduled) | Follow-up |
|------|--------|-----------------------------|-----------|
| circle / marker / freehand / numbered callouts / blur | Human-approved 2026-09-19; 09 named deferrals | none — stay out of Capture annotate until a registered MEU | grouping findings table |
| Phase 11 page layout | residual must not steal unique Next | MEU-50 | `HUB_NEXT_AFTER` |

---

## History

| Event | Date | Agent | Detail |
|-------|------|-------|--------|
| Created | 2026-09-19 | cursor-grok-4.6-xhigh | MEU-59 TDD Green + FAIL_TO_PASS receipts |
| Submitted for review | 2026-09-19 | cursor-grok-4.6-xhigh | Sent to gpt-5.6-sol |
