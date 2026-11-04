---
agent: gpt-5.6-sol
review_mode: implementation
review_target: docs/execution/plans/2026-09-20-p9-capture-annotate-edit/implementation-plan.md
target_plan: docs/execution/plans/2026-09-20-p9-capture-annotate-edit/implementation-plan.md
round: 2
verdict: approved
findings_count: 0
dispatch_id: p9-capture-annotate-edit-execreview-r2
date: "2026-09-20"
---

# Execution Critical Review: MEU-60 Capture overlay edit until Save

## Intent Anchor

MEU-60 was supposed to make Capture annotations editable as a transactional draft until Save: CSS-constant arrow handles, post-create Select behavior, movable committed marks, candidate-only color and original-image sampling, focus-safe keyboard editing, and one fail-closed Save guard shared by the button and palette. The implementation establishes most of the editor machinery, but the delivered runtime does not yet satisfy that intent on several material paths.

## Findings

| # | Severity | Finding | Evidence and violated contract | Required correction | Status |
|---|---|---|---|---|---|
| 1 | High | **Rendered arrow handles are image-space, not CSS-constant, so their visible target diverges from the CSS-space hit target.** The SVG uses the natural-image `viewBox` and renders each handle with `r={5}`. That radius is scaled by `preserveAspectRatio`; `vectorEffect="non-scaling-stroke"` affects the stroke, not circle geometry. For the named E2E's 8 px image fitted into roughly 200 CSS px, the visible radius is roughly 125 CSS px, while hit-testing remains 5 CSS px. On a downscaled large screenshot the visible radius shrinks below 5 CSS px. | `ui/src/renderer/src/features/capture/CaptureViewport.tsx:687`, `ui/src/renderer/src/features/capture/CaptureViewport.tsx:698`; violates `docs/build-plan/09-screenshot-capture.md:384` and the two CSS-constant endpoint-handle intent. The current AC-60.13 test checks only presence at `ui/tests/unit/capture-page.behavior.test.ts:637`; the E2E checks one bounding box is truthy at `ui/tests/e2e/capture-inbox.test.ts:510`. | Render handle radius as `HANDLE_RADIUS_CSS / fitScale` (or in a CSS overlay) and add a rendered-size assertion at two fit scales that also proves the visible and hit targets agree. | open |
| 2 | High | **Committing text leaves the Text tool active instead of auto-switching to Select, so the required immediate post-commit drag starts another text draft rather than moving the committed label.** `onTextCommit` explicitly calls `commitSelection(..., 'text')`. Both tests conceal this by manually clicking Select before dragging. | `ui/src/renderer/src/features/capture/CapturePage.tsx:1090`, especially `:1109`; masked by `ui/tests/unit/capture-page.behavior.test.ts:522-536` and `ui/tests/e2e/capture-inbox.test.ts:528-537`. This violates the all-draw-tools post-create rule at `docs/build-plan/09-screenshot-capture.md:383` and AC-60.5's “subsequent drag moves x,y” contract. | Commit text with Select active and add a test that presses Enter and drags the committed text without an intervening Select/list click. | open |
| 3 | High | **Annotation keyboard ownership is latched, not derived from actual focus; Delete can remove a mark while an unrelated input or page control owns focus.** Every setter writes `true`, there is no `false` transition or target/ownership check, and the window-level handler prevents the key and removes the annotation whenever the stale boolean is true. | `ui/src/renderer/src/features/capture/CapturePage.tsx:143`, `:399`, `:469`, `:687-715`, `:1051`, `:1119`, `:1124`; the exhaustive setter scan found only `setAnnotationFocus(true)`. AC-60.19 requires unrelated controls to keep their keys (`implementation-plan.md:191`), while the test asserts only the positive Delete path at `ui/tests/unit/capture-page.behavior.test.ts:665-683`. | Determine ownership from `event.target`/focus containment (and clear ownership on blur/selection cancellation). Add negative tests for the hex/inbox inputs, Capture file-delete control, unrelated buttons, Backspace, and IME. | open |
| 4 | High | **The shared Save guard does not cover the complete geometry transaction.** `canSave` omits `nudgeBurstRef`; after Arrow-key `keydown`, annotations change while the one-history-entry nudge transaction remains open until `keyup`, yet button and palette Save remain allowed. The initial pointer `pressed` state is also held only in `gestureRef`; when pointer-down produces no state change, `canSaveRef` can retain the prior allowed value until a preview render. This permits POSTing geometry that Esc can still cancel. | `ui/src/renderer/src/features/capture/CapturePage.tsx:160-174`, `:491-503`, `:645-685`; violates AC-60.10 (`implementation-plan.md:182`), AC-60.19's keydown-through-keyup transaction (`:191`), and the Save rule at `docs/build-plan/09-screenshot-capture.md:394`. The AC-60.10 test covers only an open text draft (`ui/tests/unit/capture-page.behavior.test.ts:600-618`). | Make one synchronous guard predicate read shot identity plus every live transaction ref/state (`pressed`/gesture, nudge burst, text, color, sampling, saving) and use it from both entry points. Add button and palette tests during pointer-down-before-move and keydown-before-keyup. | open |
| 5 | High | **Sampler failure and nonopaque/stale pixels are silently consumed instead of being visible and fail-closed.** Blob/decode/canvas failures return or clear the buffer without surfacing an error. A rejected sample falls through to a newly created blank canvas, then the caller exits sampling unconditionally. The user sees no error and cannot retry with the next click. | `ui/src/renderer/src/features/capture/CapturePage.tsx:240-286`, `:402-438`, `:450-457`; violates `docs/build-plan/09-screenshot-capture.md:392`. `ui/tests/unit/capture-sample.test.ts:6-54` exercises only the pure return value, not visible failure or retained sampling state. | Surface a capture-status error for HTTP/decode/context/nonopaque/stale failures, leave marks/candidate unchanged, and retain or deliberately define sampling state per the source contract. Remove the blank-canvas fallback and add integration assertions. | open |
| 6 | High | **Selecting/loading an existing named-color mark does not load its color into the candidate/well, and the only named-green path opens a dirty candidate transaction.** Selection updates only index/tool/focus. Candidate dirtiness is compared to the next-mark default, not the selected mark's loaded baseline. Thus a loaded `color: "green"` mark displays the unrelated default; selecting green from the dropdown changes the candidate and blocks Save until Apply/Cancel. | `ui/src/renderer/src/features/capture/CapturePage.tsx:156-174`, `:395-400`, `:614-633`, `:1053-1058`, `:1116-1120`; violates AC-60.8 at `implementation-plan.md:180` and the named-color load rule at `docs/build-plan/09-screenshot-capture.md:391`. The test only checks the field value and never asserts DTO/history/Save cleanliness (`ui/tests/unit/capture-page.behavior.test.ts:578-598`). | Track a selected-color candidate baseline separately from the next-mark default, map named DTO values for display without mutating them, and test select/load, Apply, Cancel, history, and Save-enabled state. | open |
| 7 | Medium | **The main component test file is materially weak under IR-5: several titles claim paths that are never asserted, allowing the High defects above to stay green.** AC-60.5 inserts a manual Select; AC-60.6 never sends Esc or verifies exact one-step restoration; AC-60.7 never selects a covered list item or proves file Delete was untouched; AC-60.8 never proves “not dirty”; AC-60.10 covers only text; AC-60.11 has no live preview/failure case; AC-60.13 checks presence only; AC-60.19 omits Tail/Head exact deltas, focus-negative Delete, Esc, Backspace, and coalescing. | `ui/tests/unit/capture-page.behavior.test.ts:506-683`; IR-5 and AV-3. These gaps demonstrably false-pass Findings 1-6. | Split the broad cases into observable positive/negative assertions for each named contract, then preserve them as the Red proof for corrections. | open |

## IR-5 Test Rigor Audit

| Test file | Rating | Evidence |
|---|---|---|
| `ui/tests/unit/capture-hit-test.test.ts` | 🟢 Strong | Specific values cover CSS-space hit radii, letterbox rejection, tie priority, translation invariants, collapse, and text hit plate. It does not own rendered handle size. |
| `ui/tests/unit/capture-color.test.ts` | 🟢 Strong | Exact map, normalization, and unknown/short-value negatives. |
| `ui/tests/unit/capture-sample.test.ts` | 🟡 Adequate | Exact pixel/stale/nonopaque/out-of-bounds return values, but no UI failure-state integration. |
| `ui/tests/unit/capture-page.behavior.test.ts` | 🔴 Weak | Broad titles materially exceed assertions; see Finding 7. |
| `ui/tests/unit/capture-help-content.test.ts` | 🟢 Strong | Exact required sentence in the owned Help section. |
| `ui/tests/e2e/capture-inbox.test.ts` (AC-60.12) | 🟡 Adequate | Real Electron path and exact POST geometry/color assertions, but a fetch seam, one fit scale, manual Select after text, and no failure/guard negatives. |

## Checklist Results

| Check | Result | Evidence |
|---|---|---|
| IR-1 live runtime evidence | partial | Named real-Electron AC-60.12 passed from Green raw+JSON, but REST is intercepted by an in-renderer seam. |
| IR-2 stub behavioral compliance | n/a | No new stub/repository implementation in this UI-only MEU. |
| IR-3 error mapping completeness | n/a | No new REST write route or error mapping. |
| IR-4 fix generalization | n/a | Round 1; no prior execution-review correction set. |
| IR-5 test rigor | fail | One in-scope file is 🔴 and permits multiple material false-passes. |
| IR-6 boundary validation | pass | Same strict annotation DTO; no new type/field/action; exact scan passed. |
| IR-7 AC/deferral integrity | pass with implementation failures | All 19 AC IDs appear in the handoff and AC-60.12 is an integration E2E; no orphan deferral. Findings 1-6 show source-contract behavior still missing. |
| AV-1 FAIL_TO_PASS | pass | UI oracle reports 16 Red titles; E2E Red is an assertion failure; Green evidence is preserved. |
| AV-2 no bypass hacks | pass | MEU scan and full gate passed. |
| AV-3 changed paths asserted | fail | Component assertions do not cover the blocking paths in Findings 1-6. |
| AV-4 no skip/only masking | pass | MEU scan passed. |
| AV-5 no unresolved placeholders | pass | MEU scan passed. |
| AV-6 source-backed criteria | pass | Plan ACs cite Spec, Local Canon, Research-backed, or Human-approved sources. |

## Scope Reviewed

- Explicit seed handoff: `.agent/context/handoffs/2026-09-20-p9-capture-annotate-edit-MEU-60-handoff.md`.
- Correlated plan/task/named sets: `docs/execution/plans/2026-09-20-p9-capture-annotate-edit/` (date/slug match; `HANDOFF_COUNT` is 1, so no sibling MEU handoff expansion).
- Intent source: `docs/build-plan/09-screenshot-capture.md` §Annotation edit until Save.
- Actual current MEU-60 source/tests, working-tree status/diff, architecture/testing guidance, FAIL_TO_PASS evidence, and Green receipts.
- Uncommitted Phase 10 queue-card files and Phase 11 MEU-50 were deliberately excluded from findings as directed.
- Unrelated MEU-61 edits to `docs/build-plan/06-gui.md`, `07-distribution.md`, and `gui-actions-index.md` appeared concurrently after the initial status snapshot; this review did not assess, alter, or rely on them.

## Commands and Evidence

| Verification | Result |
|---|---|
| Registered `assert-meu-gate.ps1` rerun | exit 0; `PASS: MEU-60 gate` |
| UI Vitest (inside rerun gate) | 65 files, 526 passed |
| Capture pytest set (inside rerun gate) | 59 passed, 1 warning |
| MCP Vitest (inside rerun gate) | 9 files, 215 passed |
| OpenAPI `--check` (inside rerun gate) | exit 0; canonical receipt empty |
| `assert-handoff-markers.ps1` | `PASS: HANDOFF_MARKER_CHECK` |
| `assert-handoff-acs.ps1` | `PASS: per-MEU AC set from HANDOFFS` |
| `assert-meu-scans.ps1` | `PASS: MEU-60 scans` |
| `assert-e2e-census.ps1` | `PASS: E2E census` |
| `assert-e2e-classify.ps1 -Mode gate` | `PASS: named E2E from Green raw+JSON plus pass receipt` |
| Existing named Playwright receipt (not relaunched) | 1 passed in 33.0s; JSON expected=1, unexpected=0; named-pass receipt present |

## Open Questions / Assumptions

None blocking. The review treats the build-plan §Annotation edit until Save rules as binding intent and the named Electron receipt as valid evidence for the path it actually asserts.

## Required Follow-up

Route corrections through `/execution-corrections`. Add failing tests for each runtime scenario before changing production code, fix Findings 1-6 without changing the annotation DTO/MCP action set or Phase 10/11 files, rerun the registered gate and named Electron case, then append Round 2 to this same rolling review file.

## Verdict

`changes_required` — six evidence-backed High product/contract failures survive the Materiality Gate, and the weak component assertions are a Medium IR-5 blocker. Green gates and the named E2E are real but do not exercise these failure paths.

Residual risk: the current E2E uses a renderer fetch seam, so it does not independently prove the live API round trip; this is not the reason for the blocking verdict. Phase 10 working-tree changes were excluded.

verdict: changes_required

---

## Corrections Applied — 2026-09-20 after Round 1

Implementer (not the reviewer). Frontmatter `verdict: corrections_applied` until independent Round 2. Tests first: `C:/Temp/av-kit/meu60-corr-red.txt` (8 failed). Green: `C:/Temp/av-kit/meu60-corr-green.txt` then `meu60-corr-green3.txt` (28 behavior passed). Named Electron: `C:/Temp/av-kit/meu60-e2e.txt` + `.json`; classify `-Mode named` and `-Mode gate` PASS. Typecheck/lint PASS. Capture pytest 59. MCP 215. Scans PASS.

Full `npm --prefix ui run test` is currently **3 failed / 527 passed**: `capture-page.test.ts` `**41**`, `convert-page.test.ts` `**35**`, and `gui-actions-audit.test.ts` `login-item-set`. Those are concurrent MEU-61 planning edits to `docs/build-plan/06-gui.md` and the actions index — out of this MEU. Do not treat them as MEU-60 regressions.

| Finding | Fix | Tests |
|---------|-----|-------|
| 1 High SVG handle `r` was image-space | `useLayoutEffect` measures fit; `r={HANDLE_RADIUS_CSS / fitScale}` | AC-60.13 page: `r * s ≈ 5`; viewport two-scale 200 and 400 |
| 2 High text commit stayed on Text | `commitSelection(..., 'select')` default; AC-39.8 clicks Text before a second draft | AC-60.5 Enter then drag **without** Select click; Select `aria-pressed` |
| 3 High Delete latch | `annotationOwnsFocus()` from `document.activeElement` inside viewport, excluding hex/well/draft/font/stroke/named | AC-60.19 negatives: hex Delete, inbox Delete, Backspace, IME composing; file-delete confirm absent |
| 4 High Save missed nudge/`pressed` | `txOpen` state on pointer-down and nudge burst; `canSave` includes `!txOpen`; up/cancel always clears lock even if gesture/imageClamped is gone | AC-60.10 pointer-down-before-move and keydown-before-keyup; both button and `CAPTURE_COMMANDS.save` |
| 5 High silent sampler + blank canvas | No blank-canvas fallback. Decode original blob (`createImageBitmap` or `Image`). Failures set `capture-status` and keep sampling. 1×1 read at click | AC-60.9 behavior: status nonempty, marks/hex unchanged, `aria-pressed` stays true. Module oracle tests unchanged |
| 6 High named color vs selected baseline | `colorBaseline` from selected mark; `namedPreview` so named dropdown is not dirty; select/load writes well via `displayHex` without rewriting DTO | AC-60.8 named green keeps stroke `#12ABCD` and Save enabled; overlay `color: "green"` loads `#008000` without dirtying |
| 7 Medium IR-5 | Strengthened the High-path assertions above; two-scale handle test; sampler UI failure; Save transaction cases | `capture-page.behavior.test.ts` |

Scope lock held: no DTO/MCP fork, no MEU-50, no Phase 10 queue-card, no `NO_NEW_PACKAGES`. Plan/`task.md` were not edited.

---

## Round 2 Recheck — 2026-09-20

### Intent Anchor

MEU-60 was intended to turn Capture annotations into an editable, transactional draft until Save: CSS-constant arrow handles, automatic Select after creation, movable committed marks, candidate-only color and original-image sampling, focus-owned keyboard editing, and one fail-closed Save guard shared by the button and palette. Round 2 asks whether the corrections now deliver that behavior, with each Round 1 finding rechecked against current source and executable evidence.

### Findings

No blocking findings. All six prior High product/contract findings are fixed on their original failure paths, and the prior IR-5 weakness no longer permits those defects to false-pass. The remaining breadth gaps are recorded under Residual Risk as same-class residuals and do not meet the Materiality Gate for a new blocker.

### Prior Finding Recheck

| Finding | Prior Severity | Round 2 result | Current evidence |
|---|---|---|---|
| 1. SVG handle radius was image-space | High | ✅ Fixed | `CaptureViewport.tsx:312-344` derives `handleRadius = HANDLE_RADIUS_CSS / fitScale`; `:731-748` applies it to both endpoints. `capture-page.behavior.test.ts:843-924` proves a 5 CSS px radius at 200 and 400 px fit sizes. |
| 2. Text commit stayed in Text mode | High | ✅ Fixed | `CapturePage.tsx:449-457` defaults `commitSelection` to Select and `:1183-1203` uses that default after Enter. `capture-page.behavior.test.ts:526-541` moves the committed text without an intervening Select click and asserts Select is active. |
| 3. Delete ownership was latched | High | ✅ Fixed | `CapturePage.tsx:66-87` derives ownership from `document.activeElement` and viewport containment, excluding editable controls; `:798-804` gates Delete and nudges through it. `capture-page.behavior.test.ts:748-774` covers hex input, inbox input, Backspace, IME composition, and positive annotation-control Delete. |
| 4. Save guard missed pressed/nudge transactions | High | ✅ Fixed | `CapturePage.tsx:191-220` includes `txOpen` in `canSave`; pointer-down and nudge begin it at `:539-595` and `:741-766`, with cancel/up/keyup cleanup. `capture-page.behavior.test.ts:623-678` proves both button and `capture:save` refuse text, pointer-down-before-move, and keydown-before-keyup transactions. |
| 5. Sampler failed silently and fell back to a blank canvas | High | ✅ Fixed | `CapturePage.tsx:287-334` fail-closes authenticated blob/decode loading with visible status; `:468-507` has no blank-canvas source fallback and surfaces unavailable/context/nonopaque/read failures; `:523-531` remains in sampling until success. `capture-page.behavior.test.ts:777-792` asserts visible failure, unchanged mark/candidate, and retained sampling. |
| 6. Named-color selection lacked a clean selected-mark baseline | High | ✅ Fixed | `CapturePage.tsx:204-206` derives `colorBaseline` from the selected mark; `:449-465` loads `displayHex(mark.color)` without rewriting the DTO; `:698-720` preserves explicit Apply/Cancel. `capture-page.behavior.test.ts:582-621` proves candidate-only named preview and loading `green` as `#008000` while the SVG remains `green` and Save stays clean. |
| 7. Component tests materially false-passed Findings 1–6 | Medium | ✅ Fixed for material correction paths | The correction Red receipt has 8 failures; Green has the strengthened behavior/scale cases passing. Current independent scoped rerun: 5 files, 35 tests passed. The file is now 🟡 Adequate rather than 🔴 Weak because every corrected High path has a direct behavioral assertion. |

### IR-5 Test Rigor Audit

| Test file | Rating | Evidence |
|---|---|---|
| `ui/tests/unit/capture-hit-test.test.ts` | 🟢 Strong | Exact CSS-space hit radii, letterbox rejection, handle priority/tie, translation invariants, collapse, and text hit plate. |
| `ui/tests/unit/capture-color.test.ts` | 🟢 Strong | Exact named map, normalization, and unknown/short-value negatives. |
| `ui/tests/unit/capture-sample.test.ts` | 🟢 Strong | Exact RGB result plus nonopaque, stale-epoch, and out-of-bounds negatives; UI failure behavior is separately asserted in the component suite. |
| `ui/tests/unit/capture-page.behavior.test.ts` | 🟡 Adequate | Directly catches all six corrected High paths, including two Save entry points and focus negatives. Some broad AC subclauses remain indirect; see Residual Risk. |
| `ui/tests/unit/capture-help-content.test.ts` | 🟢 Strong | Exact required sentence in the owned Help section. |
| `ui/tests/e2e/capture-inbox.test.ts` (AC-60.12) | 🟡 Adequate | Real Electron run with exact POST geometry/color assertions and reload/annotated-view checks; renderer fetch seam remains declared. |

### Checklist Results

| Check | Result | Evidence |
|---|---|---|
| IR-1 live runtime evidence | pass with declared seam | Existing named real-Electron AC-60.12 raw+JSON: 1 passed in 32.9 s; named and gate classifiers both PASS. The renderer fetch seam remains a residual limitation, not a hidden claim. |
| IR-2 stub behavioral compliance | n/a | No new stub/repository implementation in this UI-only MEU. |
| IR-3 error mapping completeness | n/a | No new REST write route or error mapping. |
| IR-4 fix generalization | pass | Findings 1–7 were individually rechecked in current code/tests; both button/palette Save and positive/negative keyboard ownership paths are covered. Nearby variants were treated as residual, not escalated. |
| IR-5 test rigor | pass | No in-scope test file remains 🔴. Ratings are recorded above. |
| IR-6 boundary validation | pass | Same strict annotation DTO and action/type sets; `assert-meu-scans.ps1` independently PASSed. |
| IR-7 AC/deferral integrity | pass | All 19 ACs remain represented; AC-60.12 has real Electron evidence; no orphan deferral or Phase 11/MEU-50 scope theft. |
| AV-1 FAIL_TO_PASS | pass | `meu60-corr-red.txt`: 8 failed / 20 passed; `meu60-corr-green3.txt`: corrected behavior/scale suite green. |
| AV-2 no bypass hacks | pass | Exact scan PASS; no skip/only/todo or new dependency/DTO bypass. |
| AV-3 changed paths asserted | pass | Each prior High correction has a direct assertion cited in the recheck table. |
| AV-4 no skip/xfail masking | pass | Exact G36 scan PASS. |
| AV-5 no unresolved placeholders | pass | MEU-60 placeholder scan PASS. |
| AV-6 source-backed criteria | pass | Plan ACs remain tied to Spec, Local Canon, Research-backed, or Human-approved sources. |

### Scope Reviewed

- Explicit seed handoff: `.agent/context/handoffs/2026-09-20-p9-capture-annotate-edit-MEU-60-handoff.md`.
- Correlated plan/task/named sets: `docs/execution/plans/2026-09-20-p9-capture-annotate-edit/`; date/slug match and `HANDOFF_COUNT = 1`, so no sibling MEU handoff expansion applies.
- Intent source: `docs/build-plan/09-screenshot-capture.md:377-395`.
- Current MEU-60 source, every named in-scope unit test file, the AC-60.12 block, working-tree scope, Round 1 correction Red/Green evidence, and current quality receipts.
- Concurrent MEU-61 `docs/build-plan/06-gui.md`/action-index failures, Phase 10 queue-card files, and Phase 11 MEU-50 remained excluded exactly as directed.

### Commands and Evidence

| Verification | Round 2 result |
|---|---|
| Independent scoped Vitest rerun | 5 files, 35 tests passed (`C:/Temp/av-kit/review-r2-scoped-run.txt`) |
| Correction Red | 8 failed / 20 passed (`C:/Temp/av-kit/meu60-corr-red.txt`) |
| Correction Green | corrected behavior/scale suite passed (`C:/Temp/av-kit/meu60-corr-green3.txt`) |
| `assert-e2e-census.ps1` | `PASS: E2E census` |
| `assert-e2e-classify.ps1 -Mode named` | `PASS: named E2E AC-60.12` |
| `assert-e2e-classify.ps1 -Mode gate` | `PASS: named E2E from Green raw+JSON plus pass receipt` |
| Existing named Playwright raw+JSON | 1 expected, 0 unexpected, 0 flaky; 32.9 s; Electron was not relaunched |
| `assert-meu-scans.ps1` | `PASS: MEU-60 scans` |
| UI typecheck / lint receipts | exit-clean; `tsc --noEmit` and ESLint `--max-warnings 0` |
| Capture pytest receipt | 59 passed, 1 deprecation warning |
| MCP receipt | 9 files, 215 passed |
| OpenAPI check receipt | exit-clean, empty canonical output |

### Open Questions / Assumptions

None blocking. The existing AC-60.12 Electron receipt is accepted because its raw output and parseable JSON agree and both plan classifiers pass.

### Residual Risk

- The named Electron case uses a renderer fetch seam, so it does not independently prove a live API round trip.
- `capture-page.behavior.test.ts` still does not directly assert every broad AC-60.6/AC-60.19 subclause (notably idle-Escape selection clearing and exact Tail/Head nudge deltas). These are the same Round 1 test-breadth class, not new materially different failures, and are non-blocking under the no-nearby-mutation rule.
- The full UI suite was not rerun in Round 2 because the currently known three failures are explicitly attributed to concurrent MEU-61 planning and excluded from this MEU; the MEU-60 scoped suite and all owned gates are green.

### Required Follow-up

None for MEU-60 approval. The implementer may proceed with the workflow-defined H2 closeout; this reviewer did not modify product, tests, plans, or `task.md`.

### Verdict

`approved` — all six prior High runtime/contract failures are corrected and directly exercised, the prior IR-5 false-pass condition is removed for those paths, and no evidence-backed High/Critical finding survives the Materiality Gate.

verdict: approved
