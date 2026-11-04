---
agent: gpt-5.6-sol
review_mode: implementation
review_target: docs/execution/plans/2026-09-19-p9-capture-annotate-arrow-text/implementation-plan.md
target_plan: docs/execution/plans/2026-09-19-p9-capture-annotate-arrow-text/implementation-plan.md
round: 2
verdict: approved
findings_count: 0
dispatch_id: p9-capture-annotate-arrow-text-execreview-r2
date: "2026-09-19"
---

# Execution Critical Review: p9-capture-annotate-arrow-text

## Intent Anchor

MEU-59 is supposed to make Capture arrow and text overlays trustworthy in original-image pixels: SVG preview must agree with Pillow bake, Save must fail closed and visibly, and detail GET must restore the validated sidecar without data loss. It must preserve the existing four-type DTO for GUI and MCP, add no drawing dependencies, and leave circle/marker and Phase 11 work out of scope.

## Findings

No Critical findings. Four High behavioral/contract defects and one Medium integration-test false-pass survive verification.

### EXR1-1 — High — Selection can save the previous shot's annotations over the newly selected shot

**Confidence:** High  
**Violated contract:** AC-59.8; implementation lock “selecting a shot loads GET detail annotations as both draft and saved”; persistence/round-trip correctness.

`chooseItem` changes `selectedId` but leaves `annotations` and `saved` untouched (`CapturePage.tsx:177-188`). The effect then exposes that old annotation array through `setCaptureSelection` under the new id (`CapturePage.tsx:76-82`), while Save remains enabled whenever `selectedId` is non-null (`CapturePage.tsx:303-315`). Until the new detail GET completes (`CapturePage.tsx:115-150`), clicking Save posts shot A's marks to shot B. If the user draws first, `applyHistory` increments `overlayEditGen` while appending to the stale array (`CapturePage.tsx:170-175,505-559`); the new shot's eventual GET is then intentionally ignored at lines 123-125, permanently retaining A's marks in B's draft.

This is also reproducible on initial auto-selection: `selectedId` becomes non-null at `CapturePage.tsx:62-70` before detail annotations have loaded, so an immediate Save can POST the initial empty array and clear an existing sidecar. The current tests do not delay detail GET and then save/draw across a selection change.

**Required correction:** Make selection/detail hydration atomic for editing: clear or quarantine prior-shot state and disable Save/drawing until the selected id's detail has successfully loaded, or key draft/saved state by shot id. Preserve the late-GET protection without carrying annotations across ids. Add a delayed-GET regression test that proves no POST can contain another shot's marks and no pre-load empty Save can clear a sidecar.

### EXR1-2 — High — Invalid Save emits an error and then immediately clears the visible status

**Confidence:** High  
**Violated contract:** AC-59.7 (“invalid body → POST count 0 and `capture-status` nonempty”); fail-closed Save must be visible.

`saveAnnotations` correctly dispatches `av-kit:capture:error` and returns `false` when Zod parsing fails (`capture-commands.ts:69-77`). The Save button calls it inside `run` (`CapturePage.tsx:303-315`), but `run` unconditionally executes `setError(null)` after any normally resolved callback (`CapturePage.tsx:190-199`). Because `false` is not an exception, the error listener sets the status and the later `setError(null)` clears it. The operation avoids POST and leaves the saved baseline unchanged, but the required user-visible failure is lost.

The claimed test false-passes this defect: it invokes `saveAnnotations()` directly instead of clicking the page Save button and accepts `errors.length > 0 || status` (`capture-page.behavior.test.ts:327-353`). A raw event therefore satisfies the assertion even when `capture-status` ends empty in the actual button path.

**Required correction:** Propagate the failed result through the page wrapper without clearing the error, or throw a typed validation error that `run` renders. Exercise the actual Save button and assert the final `capture-status` text plus zero annotate POSTs and unchanged saved/dirty state.

### EXR1-3 — High — Malformed sidecar elements are silently dropped and returned as an empty valid list

**Confidence:** High  
**Violated contract:** AC-59.8 and `09-screenshot-capture.md:349`: malformed sidecar or unknown type must return 422, never `[]` that Save can erase.

`parse_sidecar_document` filters the sidecar array to dictionaries instead of rejecting non-object entries (`packages/core/src/avkit_core/services/capture.py:52-59`). The independent probe

```text
uv run python -c "... annotations_from_sidecar({'version':1,'annotations':[17]}) ..."
=> []
```

is captured at `C:/Temp/av-kit/review-r1-sidecar-scalar-probe.txt`. A sidecar containing `{"annotations":[17]}` therefore yields HTTP 200 with `annotations: []`; the renderer accepts it as the saved baseline and a later Save can erase the malformed evidence. The service test covers an unknown object type (`circle`) but not a non-object annotation (`test_capture_service.py:618-647`).

**Required correction:** Reject every non-object list element with `AnnotationValidationError`; do not filter. Add service and API detail tests for scalar/null/list elements and assert the 422 error-envelope shape and preservation of the current UI annotations.

### EXR1-4 — High — SVG text and its background plate do not match the Pillow bake

**Confidence:** High  
**Violated contract:** MEU intent, `09-screenshot-capture.md:355,364`, plan locks at `implementation-plan.md:90-94`, and AC-59.19.

The SVG helper invents a fixed `0.6 * font_size * character_count` width, a `font_size` height, and places the plate directly at `(x,y)` (`capture-text-metrics.ts:18-26`). The SVG text also supplies no Segoe UI/Arial font family (`CaptureViewport.tsx:98-124`). Pillow instead loads Segoe UI/Arial and uses the actual `textbbox(..., anchor="la")` (`adapter.py:77-88,283-299`). On this Windows host, the independent fixture `x=10,y=20,text="Hi",font_size=16` produced:

```text
Pillow Segoe UI bbox: (10, 26, 25, 38)
SVG helper plate:    (10, 20, 29, 36)
```

Receipt: `C:/Temp/av-kit/review-r1-text-bbox-probe.txt`. This is positional and dimensional disagreement, not allowable antialiasing variance.

The tests cannot catch it: `capture-text-metrics.test.ts:6-15` asserts only positive width/height, while `capture-page.behavior.test.ts:419-455` asserts only anchor strings and plate existence. Both pass for an arbitrary wrong bbox.

**Required correction:** Use a deterministic preview measurement/font contract that reproduces the bake bbox (including offsets), render the same font fallback, and assert exact shared fixtures for representative glyphs and font sizes. Keep the required `start`/`hanging` attributes, but do not equate their presence with visual agreement.

### EXR1-5 — Medium — The central image-space integration path can false-pass

**Confidence:** High  
**Violated rubric:** IR-1, IR-5, and AC-59.4/AC-59.12 integration evidence.

The FIT_MAP unit test is numerically strong, but the component and Electron tests never assert that the coordinates actually posted by the page are the intended original-image coordinates. The component test checks only `viewBox`/`preserveAspectRatio` (`capture-page.behavior.test.ts:291-297`); the arrow test checks only the zero-length case (`capture-page.behavior.test.ts:299-305`). The Playwright case computes image-space click locations but asserts only that one arrow and one text node exist before and after a mocked Save/reload (`capture-inbox.test.ts:353-444`); its `window.fetch` replacement stores any posted values unchanged. Container-pixel coordinates, swapped endpoints, or wrong text placement would still pass so long as two nodes reappear.

The Electron case is valuable renderer-runtime evidence, but it is not IR-1 cross-layer evidence without dependency overrides because it replaces `window.fetch` rather than exercising the FastAPI/service/sidecar path.

**Required correction:** Capture and assert the exact annotate POST payload in Playwright (arrow endpoints, text x/y, `font_size`, and `bg_color`) and add or run one real API-backed save→detail-GET round trip without a capture-service/fetch override.

## Scope Reviewed

**Correlation:** The user supplied one seed handoff and the plan's `HANDOFF_COUNT`/`HANDOFFS` declare exactly one MEU handoff, so this is a single-handoff implementation review rather than a multi-MEU expansion.

Reviewed:

- `.agent/context/handoffs/2026-09-19-p9-capture-annotate-arrow-text-MEU-59-handoff.md`
- `docs/execution/plans/2026-09-19-p9-capture-annotate-arrow-text/{implementation-plan.md,task.md,named-sets.json}`
- `docs/build-plan/09-screenshot-capture.md` §Annotation geometry (arrow + text)
- All named backend, UI, MCP, OpenAPI, and test files for MEU-59
- Current scoped diffs and untracked MEU-59 modules
- Existing H1, Red, and named Electron receipts under `C:/Temp/av-kit/`

Explicitly excluded from attribution: uncommitted Phase 10 queue-card files and Phase 11 / MEU-50 surfaces. No circle/marker or `suggest` requirement was inferred.

## IR Checklist Results

| Check | Result | Evidence |
|---|---|---|
| IR-1 Live runtime evidence | fail | Electron AC-59.12 ran and passed, but replaces `window.fetch`; API tests use a fake service. No in-scope no-override GUI→API→sidecar round trip was demonstrated. |
| IR-2 Stub behavioral compliance | pass | No new stubs; save/get behavior is implemented, though EXR1-1 and EXR1-3 expose incorrect edge behavior. |
| IR-3 Error mapping completeness | partial | Global domain mapping sends `AnnotationValidationError`/`ValidationError` to 422 and Pydantic errors to the validation envelope. New AC tests mostly assert status, not all response bodies; EXR1-3 bypasses error creation entirely. |
| IR-4 Fix generalization | partial | FIT_MAP is shared by all four GUI tools and color/type restrictions cover UI/API. Text preview/bake and selection hydration were not generalized to a true shared contract. |
| IR-5 Test rigor audit | fail | Multiple material AC tests are weak and permit the verified defects; per-file ratings follow. |
| IR-6 Boundary validation coverage | partial | UI/API schemas are strict and circle/marker return 422; the sidecar read boundary filters invalid elements instead of failing closed. |
| IR-7 Deferral and AC integrity | pass | All 20 AC ids appear in the handoff; circle/marker are source-backed exclusions; MEU-50 remains scheduled and untouched. |

### IR-5 Per-File Ratings

| Test file | Rating | Review |
|---|---|---|
| `tests/unit/test_capture_adapter.py` | Red / Weak | Arrow vertices are exact; AC-59.3 is source-string inspection and does not prove rendered order or pixels. |
| `tests/unit/test_capture_service.py` | Yellow / Adequate | Save→load and unknown type are exercised; malformed non-object entries are missing. |
| `tests/e2e/test_api_captures.py` | Yellow / Adequate | Route/schema split and 422 statuses are specific, but detail GET is backed by a fake service and does not exercise sidecar parsing. |
| `ui/tests/unit/capture-fit-map.test.ts` | Green / Strong | Exact letterbox, mapping, and resize values. |
| `ui/tests/unit/capture-arrow-head.test.ts` | Green / Strong | Exact shared numeric fixture. |
| `ui/tests/unit/capture-text-metrics.test.ts` | Red / Weak | Positive dimensions only; arbitrary wrong bbox passes. |
| `ui/tests/unit/capture-annotate.test.ts` | Green / Strong | Specific accepted/rejected values and forbidden types. |
| `ui/tests/unit/capture-page.behavior.test.ts` | Red / Weak | Save test bypasses the button and uses an event-or-status assertion; positive coordinate payload and late-GET selection race are not asserted. |
| `ui/tests/unit/capture-page.test.ts` | Red / Weak | AC-59.4 is source grep, not behavioral integration. |
| `ui/tests/unit/capture-help-content.test.ts` | Green / Strong | Exact sentence for the narrow content AC. |
| `ui/tests/e2e/capture-inbox.test.ts` | Red / Weak | Real Electron interaction, but mocked persistence and count-only reload assertions allow wrong coordinates/content to pass. |
| `mcp-server/tests/capture.test.ts` | Green / Strong | Exact example/schema assertions, forbidden action/type descriptions, and existing request-path tests. |

## Adversarial Verification Checklist

| Check | Result | Evidence |
|---|---|---|
| AV-1 FAIL_TO_PASS | pass | Preserved receipts show 7 Python failures, 15 UI failures, 1 MCP failure, and the named E2E arrow failure before Green. |
| AV-2 No bypass hacks | pass | `assert-meu-scans.ps1` passed; no skip/only/todo neutralization found. |
| AV-3 Changed paths asserted | fail | EXR1-2, EXR1-4, and EXR1-5 show assertion gaps on changed runtime paths. |
| AV-4 No skip/xfail masking | pass | Plan-local scan passed. |
| AV-5 No placeholders | pass | Plan-local placeholder scan passed. |
| AV-6 Source-backed criteria | pass | ACs trace to the Phase 9 spec, local canon, research sources, or USER_EXPLICIT locks. |

## Documentation / Evidence Checklist

| Check | Result | Evidence |
|---|---|---|
| DR-1 Claim-to-state match | fail | The handoff marks AC-59.7, AC-59.8, AC-59.12, and AC-59.19 complete despite EXR1-1 through EXR1-5. |
| DR-2 Residual forbidden terms | pass | No circle/marker schema member and no `suggest` action were found. |
| DR-3 Downstream references | pass | Plan, handoff, grouping, spec, hub-next, and named-set paths correlate. |
| DR-4 Verification robustness | fail | Green gates do not exercise the five surviving scenarios. |
| DR-5 Evidence auditability | pass | Named receipts exist, are fresh for this run date, and were independently compared. |
| DR-6 Cross-reference integrity | pass | Arrow/text scope, no-new-dependency lock, and MEU-50 exclusion agree across artifacts. |
| DR-7 Evidence freshness | pass | Independent reruns reproduce 59 pytest, 509 UI, and 215 MCP passes; OpenAPI and plan-local checks exit 0. |
| DR-8 Completion vs residual risk | pass | The handoff is `ready_for_review`, not approved; the present review supplies the blocking verdict. |

## Commands Executed

All commands used RTK routing, redirected all streams to `C:/Temp/av-kit/`, captured `$LASTEXITCODE` before receipt reads, and preserved the command exit code.

```text
rtk proxy git status --short
rtk proxy git diff --name-only
rtk proxy git diff --stat
rtk proxy git diff -- <MEU-59 tracked files>
rtk proxy rg -n ... <MEU-59 source, tests, plan, spec, and error mappings>
rtk proxy uv run pytest tests/unit/test_capture_adapter.py tests/unit/test_capture_service.py tests/e2e/test_api_captures.py --tb=short -v
rtk proxy npm --prefix ui run test
rtk proxy uv run python tools/export_openapi.py --check openapi.committed.json
rtk proxy npm --prefix mcp-server run test
rtk proxy pwsh -NoProfile -File .../assert-handoff-markers.ps1
rtk proxy pwsh -NoProfile -File .../assert-handoff-acs.ps1
rtk proxy pwsh -NoProfile -File .../assert-meu-scans.ps1
rtk proxy uv run python -c <Pillow textbbox probe>
rtk proxy uv run python -c <malformed sidecar probe>
```

Independent results:

- Python scoped suite: **59 passed**, 1 warning.
- UI Vitest: **509 passed** across 62 files.
- MCP Vitest: **215 passed** across 9 files.
- OpenAPI `--check`: exit 0.
- Handoff markers, handoff AC census, and MEU scans: PASS.
- Existing named Electron receipt: **AC-59.12 1 passed (18.8s)**; not relaunched per the supplied GPU/sandbox guidance.
- Existing `full-verify-gate.txt`: `PASS: MEU-59 gate`.

## Open Questions / Assumptions

None. The review treats arrow+text, no circle/marker, no new dependencies/types, and no Phase 11 work as fixed inputs.

## Required Follow-up

1. Route corrections through `/execution-corrections`; do not patch from this review workflow.
2. Resolve EXR1-1 through EXR1-4 with regression tests that fail on the exact scenarios above.
3. Strengthen the image-space/E2E evidence in EXR1-5, then rerun the scoped suites, OpenAPI check, MCP tests, named Electron case, handoff checks, scans, and execution review.

## Residual Risk

Arrow FIT_MAP and arrowhead code appear internally consistent, circle/marker remain excluded, the original image is not overwritten by the bake path, and all supplied/rerun gates are green. Approval is nevertheless unsafe because the current UI can overwrite a different shot's sidecar, visible invalid-Save feedback is cleared, malformed sidecars can collapse to an empty list, and text preview geometry demonstrably differs from the bake.

## Verdict

`changes_required` — the delivered implementation does not yet achieve MEU-59's fail-closed, lossless reload, and preview/bake agreement intent. EXR1-1 through EXR1-4 meet the High-severity behavioral/contract threshold; EXR1-5 is a material IR-1/IR-5 evidence gap.

verdict: changes_required

---

## Round 2 Recheck (2026-09-19)

### Intent Anchor

MEU-59 is intended to make Capture arrow and text overlays reliable in original-image coordinates: selection must hydrate before edits can be saved, invalid writes must fail visibly, sidecars must fail closed, SVG text plates must match the Pillow bake fixture, and the Electron path must prove the posted arrow/text DTO. Round 2 verifies whether the five round-1 defects were materially corrected without reopening fixed surfaces through nearby mutations.

### Findings

No Critical, High, Medium, or Low findings. EXR1-1 through EXR1-5 are fixed for their contracted scenarios, and no new materially different failure survived generate-then-verify review.

### Prior Findings Recheck

| Finding | Prior status | Recheck result | Evidence |
|---|---|---|---|
| EXR1-1 | open | Fixed | `CapturePage.tsx:116-160,317-334,526-529` clears/quarantines overlay state and gates Save/drawing on `overlayReady`; `capture-page.behavior.test.ts:381-425` covers delayed GET and 422 without POST. |
| EXR1-2 | open | Fixed | `CapturePage.tsx:317-335` calls `saveAnnotations()` outside `run()` and clears status only on success; `capture-page.behavior.test.ts:353-379` clicks `capture-save`, asserts zero annotate POSTs, and requires nonempty status. |
| EXR1-3 | open | Fixed | `capture.py:52-63` raises `AnnotationValidationError` for every non-dict annotation; `test_capture_service.py:648-659` covers scalar and `None`, and the independent scalar probe reproduced the 422-domain exception. |
| EXR1-4 | open | Fixed | `capture-text-metrics.ts:1-47` uses the Segoe `la` glyph table; `CaptureViewport.tsx:98-125` consumes the exact box and font family; the JS fixture is `(10,26,15x12)` while Pillow independently returned `(10,26,25,38)`. |
| EXR1-5 | open | Fixed | `capture-inbox.test.ts:353-440` now asserts posted arrow `[2,2] -> [6,6]` and text `{x:3,y:6,text:Note,font_size:18}` before reload; the supplied r2 Electron receipt reports 1 passed in 21.0s. |

### Scope Reviewed

- Correlated plan/task and the single MEU-59 implementation handoff.
- The five round-1 correction surfaces in core, renderer, viewport metrics, and Electron/component tests.
- Current scoped diff plus supplied `full-verify-gate-r2.txt` and `meu59-e2e-r2.txt` receipts.
- Unrelated Phase 10/11 working-tree changes were excluded from attribution.

### Commands Executed

All commands used RTK routing, redirected all process streams to `C:/Temp/av-kit/`, captured `$LASTEXITCODE` before receipt reads, and propagated the result.

```text
rtk proxy git status --short
rtk proxy git diff --name-only
rtk proxy git diff -- <round-2 correction files>
rtk proxy uv run pytest tests/unit/test_capture_adapter.py tests/unit/test_capture_service.py tests/e2e/test_api_captures.py --tb=short -q
rtk proxy npm --prefix ui run test
rtk proxy uv run python tools/export_openapi.py --check openapi.committed.json
rtk proxy uv run python -c <scalar-sidecar rejection probe>
rtk proxy uv run python -c <Pillow Hi@16 text_plate_box probe>
rtk proxy npm --prefix ui run test -- tests/unit/capture-text-metrics.test.ts
```

Independent results:

- Python scoped suite: **59 passed**, 1 warning.
- UI Vitest: **510 passed** across 62 files.
- OpenAPI `--check`: exit 0 with empty output.
- Scalar sidecar probe: rejected with `AnnotationValidationError: annotation must be an object`.
- Pillow `Hi@16`: `(10, 26, 25, 38)`; JS plate fixture: `(10, 26, 15x12)` and 1 focused test passed.
- Supplied full gate: `PASS: MEU-59 gate`.
- Supplied Electron AC-59.12 receipt: **1 passed (21.0s)**; not relaunched per review instructions.

### IR Checklist Results

| Check | Result | Evidence |
|---|---|---|
| IR-1 Live runtime evidence | pass with accepted seam | Fresh real-Electron receipt exercises the renderer and exact posted DTO; Python service/API suites separately cover backend contracts. |
| IR-2 Stub behavioral compliance | pass | No new stubs; selection, save, load, and malformed-sidecar behavior are implemented. |
| IR-3 Error mapping completeness | pass | Scalar/null sidecars raise `AnnotationValidationError`, mapped by the existing domain HTTP contract to 422; renderer keeps Save disabled on failed detail GET. |
| IR-4 Fix generalization | pass | The readiness gate covers Save and all pointer tools; strict sidecar iteration covers every non-object element; shared text metrics feed both unit and viewport assertions. |
| IR-5 Test rigor audit | pass | Corrected assertions exercise the user-visible button/status, delayed hydration, exact text plate, and exact Electron payload. Delta-file ratings follow. |
| IR-6 Boundary validation coverage | pass | Zod/Pydantic write schemas remain strict; malformed sidecar read input now fails closed. |
| IR-7 Deferral and AC integrity | pass | All ACs remain represented; circle/marker and MEU-50 exclusions are unchanged and source-backed. |

### IR-5 Delta Test Ratings

| Test file | Rating | Round-2 assessment |
|---|---|---|
| `tests/unit/test_capture_service.py` | Green / Strong | Exact scalar/null rejection assertions complement save-load coverage. |
| `ui/tests/unit/capture-page.behavior.test.ts` | Green / Strong | Exercises the actual Save button, visible status, zero POST, delayed GET, and 422 gating. |
| `ui/tests/unit/capture-text-metrics.test.ts` | Green / Strong | Exact `Hi@16` bbox fixture; arbitrary positive dimensions can no longer pass. |
| `ui/tests/e2e/capture-inbox.test.ts` | Green / Strong | Real Electron interaction now verifies exact image-space POST fields and reload nodes. |
| `tests/e2e/test_api_captures.py` | Yellow / Adequate | API schema/status checks remain specific; persistence behavior is covered in the real service suite rather than this fake-service route fixture. |

### Adversarial Verification Checklist

| Check | Result | Evidence |
|---|---|---|
| AV-1 FAIL_TO_PASS | pass | Round-1 Red receipts remain preserved; each corrected path now has a specific passing regression assertion. |
| AV-2 No bypass hacks | pass | No assertion monkeypatch, forced early return, or test-neutralizing guard was found. |
| AV-3 Changed paths asserted | pass | Each round-2 changed path is paired with a value/status/payload assertion. |
| AV-4 No skip/xfail masking | pass | No skip/only/todo marker affects the corrected tests. |
| AV-5 No placeholders | pass | No placeholder was introduced on the correction surfaces. |
| AV-6 Source-backed criteria | pass | Corrections implement the existing AC-59.7/.8/.12/.19 and plan locks without adding product behavior. |

### Open Questions / Assumptions

None.

### Residual Risk

The Electron test deliberately uses the established fetch seam rather than one continuous GUI-to-FastAPI-to-filesystem run. The exact renderer payload false-pass is now closed, backend persistence is independently exercised by the scoped Python suite, and the round-2 materiality/nearby-mutation rule accepts that declared boundary.

### Verdict

`approved` — the implementation now achieves MEU-59's contracted selection safety, visible fail-closed Save, strict sidecar parsing, deterministic `Hi@16` plate geometry, and exact image-space Electron payload behavior. No evidence-backed High or Critical defect remains.

verdict: approved
