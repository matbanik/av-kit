---
date: "2026-11-14"
review_mode: "plan"
target_plan: "docs/execution/plans/2026-11-14-capture-shapes-steps/implementation-plan.md"
verdict: "approved"
findings_count: 0
template_version: "2.2"
requested_verbosity: "standard"
agent: "codex-independent-reviewer"
loop_id: "s72-plan-canonical-2026-11-14-capture-shapes-steps"
round: 2
---

# Critical Review: 2026-11-14-capture-shapes-steps

> **Review Mode:** `plan`
> **Verdict:** `approved`

> **Rolling report:** The Scope, Q1–Q10, Checklist Results, Probe Evidence and first Verdict below preserve round 1 as historical observations. Only its Findings statuses and current frontmatter/banner have been updated. The current assessment, evidence and verdict are in **Recheck (Round 2)**. Historical failing checks are not round-2 results.

## Scope

**Intent anchor:** Session 72 adds the last three marks of the capture annotation synthesis.

**Intent assessment: partial, as a plan.** The design covers all four goal bullets and the specification's rule rows. Two Duplicate defects prevent delivering the stated behavior: its chosen translation does not satisfy its box-edge contract, and duplicating a step can create a number rejected by every input boundary. Two additional hit-test defects are non-blocking Medium findings.

Codex independently reviewed Claude Code/Anthropic's working-tree plan, task and seven supporting scripts, against the relevant domain, service, adapter, API, MCP, UI, test and specification sources. HEAD was independently observed as `5db36236dbdff78bc846bd4586206897c7e9be94`. Git status showed only the nine untracked plan files and the disclosed sandbox-only `.claude/settings.local.json` ignore discrepancy. That settings file was not opened.

Accepted as given: the source request, carried decisions through D-766, D-676's ellipse crop rule, approved STYLE_* and MEU-143 contracts, the exclusions, autonomous D-767–D-778 choices as choices, and pending D-779–D-782 human rulings. Their proposed behavior was still checked. The draft Status and band mismatch are not findings. Execution remains unauthorized.

No repository file was edited. No product suite, build, baseline, session gate, pyright or assert-never script was run. No network, clipboard, user inbox, app database, user settings, divergence-report content or installed avkit MCP server was accessed. All writes were under `C:/Temp/av-kit`. Arithmetic transcriptions below are identified as such; they are not claimed as TypeScript executions.

## Findings

| # | Severity | Blocking | Kind | Finding | File:Line | Recommendation | Status |
|---|---|---|---|---|---|---|---|
| F1 | High | yes | behavior | **DUPLICATE clamps a box's origin, not the whole copy (confidence: High; violates AC-106).** AC-106.24 and its edge matrix require a right-edge mark to move down only and a filling mark to copy in place. The prescribed `duplicateMark = translateBody(mark, 10, 10, W, H)` does neither for box marks: today's non-arrow branch clamps only x/y. On a 100×80 image, rect `(89,20,10,10)` becomes `(99,30,10,10)`, with its far edge at 109; a filling closed rect `(0,0,99,79)` becomes `(10,10,99,79)`. Following this recipe moves copies off-image, including an ellipse's curve, and cannot pass the required edge assertions. | `docs/execution/plans/2026-11-14-capture-shapes-steps/implementation-plan.md:218`; `:358`; `:385`; `ui/src/renderer/src/features/capture/capture-hit-test.ts:289` | Define Duplicate's bounded translation using the complete mark extent and its existing coordinate convention. Preserve dimensions and other fields; clamp the delta before translating. This can be local to `duplicateMark` without reopening approved drag behavior. Keep explicit right/bottom/filling cases for rect, ellipse and filled box marks in AC-106.24. | fixed |
| F2 | High | yes | behavior | **DUPLICATE can append an unsaveable step 1000 (confidence: High; violates AC-107).** STEP_TYPE/STEP_API cap numbers at 999, while STEP_PLACE/`nextStepNumber` use maximum plus one. DUPLICATE unconditionally gives a copied step that next number; only placing with the Step tool has a stated exhaustion guard. With a valid step 999 already present, copying any selected step therefore appends 1000. STEP_ZOD/STEP_API then refuse saving the annotation list. AC-107.21 tests only 1,2→3 and AC-106.25 has no exhausted-number case, so all listed tests can miss this failure. | `docs/execution/plans/2026-11-14-capture-shapes-steps/implementation-plan.md:203`; `:214`; `:218`; `:463` | Specify the exhausted-number outcome for step duplication. Reuse the existing 999 stop before appending/history mutation, retain the selection and mark list, and expose the stated status. Add a real Ctrl+D test with an existing 999, including a different selected step, plus normal max-plus-one/Undo coverage. | fixed |
| F3 | Medium | no | behavior | **ELLIPSE_HIT's normalized radius is not distance to the outline (confidence: High; AC-106.13).** For box `(10,10,200,20)` at 1:1, the right tip is `(210,20)`. At `(260,20)`, 50 CSS px outside it, the planned formula returns 5, so the 10 px threshold selects the ellipse. A user can select or move it from visibly empty space, or have it intercept a mark beneath it. The single 60×40 test does not expose this aspect-ratio error. | `docs/execution/plans/2026-11-14-capture-shapes-steps/implementation-plan.md:199`; `:374` | Use a bounded CSS-distance test for the ellipse outline, retaining the specified degenerate fallback. Add elongated horizontal/vertical cases, including misses beyond the major-axis tips and zoomed cases. | fixed |
| F4 | Medium | no | behavior | **HEAD_PREVIEW/HEAD_BAKE change heads without changing arrow hit geometry (confidence: High; AC-106.10).** The existing `hitArrowBody` always tests the old end-head triangle. No planned hit change or AC covers the newly drawn start head or removal of that triangle. For `(100,100)→(300,100)`, stroke 20 at 1:1, `(160,125)` lies in the new start head but the current predicate misses it. For `head: none`, `(240,125)` still hits the old, invisible end head. Thus some visible head area cannot select the both arrow, while empty space selects a line. | `docs/execution/plans/2026-11-14-capture-shapes-steps/implementation-plan.md:196`; `:371`; `:508`; `ui/src/renderer/src/features/capture/capture-hit-test.ts:105` | Make arrow head hit triangles follow the same head choice as rendering: neither for None, end for End, both for Both. Add positive start-head and negative removed-head cases at a supported thicker stroke. Preserve the existing shaft and endpoint-handle contracts. | fixed |

## Q1 — Goal and end-to-end paths

**Accepted:** Every goal bullet and every rule of 09 §Line and ellipse / §Step mark has named work and AC coverage. The API/MCP trace is strict `stepAnn`/arrow/rect union (**STEP_MCP**) → `AnnotationIn`/`StepAnnotationIn` (**STEP_API**) → `_annotations_from_in`'s explicit fields and step branch → domain checks → `_clamp_annotation` (**STEP_CLAMP**) → `_annotation_to_wire` and sidecar (**DEFAULT_OMIT**, **STEP_WIRE**). Read-back uses `_annotation_from_wire`; crop calls `clip_mark`, preserving heads (**HEAD_CLIP**), applying the closed ellipse rule (**ELLIPSE_CLIP**) and half-open step anchor rule (**STEP_CLIP**). The adapter dispatch then reaches `_apply_arrow`, `_apply_rect` and `_apply_step` (**HEAD_BAKE**, **ELLIPSE_BAKE**, **STEP_BAKE**). AC-106.5/.6/.8/.15–.17/.29 and AC-107.3–.10/.20/.22/.23 cover those links. The integration trace uses None, while Both is covered by separate schema, geometry, wire/crop and bake cases.

The UI trace is Arrow → Head None / Box → Ellipse (**SHAPE_OPTIONS**) → pick-aware `createDrawnMark` (**DEFAULT_OMIT**) → **HEAD_PREVIEW** / **ELLIPSE_PREVIEW**. Step button (**STEP_TOOL**) → the post-ARMED_EDIT pointer-down branch (**STEP_PLACE**) → history and **LOCK_SELECTS** → **STEP_PREVIEW**; two presses create 1 and 2. Selecting the second step and Ctrl+D reaches the page through the real registry handler and **DUPLICATE**, producing step 3 and selecting it. AC-106.18–.25/.28 and AC-107.11/.13/.14/.18/.21/.24 cover the components. The combined second-step Ctrl+D path is composition of these cases, not a single promised Electron test.

**Not accepted:** The edge and exhaustion outcomes in that UI duplication path: F1/F2. The goal needs corrections, not narrower scope.

## Q2 — HEAD_FIELD, SHAPE_FIELD and DEFAULT_OMIT

**Accepted:** Adding last fields preserves old positional constructors. Missing wire keys receive defaults; explicit defaults remain accepted, while non-default fields survive conversion. Conditional serialization preserves existing sidecar key order and avoids introducing default bytes. The API uses per-field `exclude_if`, preserving unrelated output such as `bg_color: None`; it does not call for global `exclude_none` or `exclude_defaults`.

An independent Pydantic 2.14.1 in-memory variant confirmed missing/explicit-default omission, non-default retention and preservation of an unrelated null. Empty, control, lone-surrogate, wrong-case, integer and null heads were refused. Production HTTP refusal text is sanitized by `packages/api/src/avkit_api/errors.py`; the plan's new domain messages are constant field-level text. Literal validation alone is not claimed to sanitize raw Pydantic diagnostics.

Production `clip_mark` on a frozen arrow subtype carrying the proposed last `head` field preserved all three head values for inside/straddling/dropped cases. `_clip_arrow` uses `replace`, as HEAD_CLIP says. No delivery defect found in these contracts.

## Q3 — Head geometry, ellipse rendering, hit testing and crop

**Accepted:** Reusing `arrow_shaft_end` for End and swapped endpoints for the start triangle can preserve existing End bytes. Both needs the mirrored pullback and a null shaft on overlap; the shared `arrow_both` fixture and the existing `arrows` short/zero cases provide parity oracles. AC-106.8 plus AC-106.30 bind the base End/Rect hashes. Preserve the legacy End null-shaft and zero-length behavior when implementing the span helper.

`draw.ellipse` over the rect box, the SVG ellipse branch and eight existing box handles are compatible with the requested representation. `resizeBox` spreads the mark, so `shape` already survives. ELLIPSE_CLIP's inequalities implement D-676 exactly, including touching the closed far edges, and the matrix distinguishes dropping an ellipse from clipping a rect.

**Not accepted:** ELLIPSE_HIT as an outline-distance formula (F3), and leaving the arrow's head hit triangles unchanged (F4). These are additional behavior observations; neither independently gates this verdict.

## Q4 — Step boundaries and exhaustive cases

**Accepted:** STEP_TYPE/STEP_API/STEP_MCP/STEP_ZOD state the same integer/range/color rules; strict object schemas and STEP_WIRE's exact keys reject extras. Domain bool rejection must remain explicit. The wire, API and clamp have scheduled branches, and constant step-extra-key text avoids echoing an arbitrary key. The text-anchor clip rule and nonnegative input constraints are distinct and correctly named.

The assert-never script checks an unchanged scratch copy first, then requires exactly the missing Step-to-Never diagnostic after removing the branch. Its source supports the domain match and route if-chain claims. It was read, not run, as requested. The OpenAPI delta selftest passed eight fixtures; its structural comparison admits the new union members and `step` discriminator mappings and refuses unrelated base-schema drift. API/domain behavior tests remain responsible for the contents of the newly added schema.

**Not accepted:** Allowing DUPLICATE to synthesize a number outside those otherwise consistent boundaries (F2).

## Q5 — STEP_BAKE, STEP_CENTRE and STEP_PREVIEW

**Accepted:** Radius, digit-dependent font size, rounded 0.355 baseline offset, `ms` anchor and tolerance are precise. An independent in-memory Pillow probe passed all 12 size/number pairs, with worst ink-box offsets 3.5 px horizontally and 0.5 px vertically; all digit ink stayed in the disc. This corroborates the supplied receipt using the same exclusive-edge ink-box convention.

The 0.179 luminance decision is sound, and the TS mirror can use the same sRGB conversion and named-color resolution. **Clerical correction:** AC-107.9 says red `#FF0000` gets white, but its relative luminance is 0.2126, so STEP_BAKE's stated formula gives black. Correct that expectation before writing the immutable tests; retain the formula.

**Verification limit:** AC-107.11/.12 check SVG attributes and formula parity. They do not measure browser ink centering. The existing Segoe UI family and middle anchor make the design plausible, but neither those checks nor my Pillow probe establishes the actual preview tolerance. S16 must use a real measured preview check if it is relied upon; no browser measurement was run in this review. I found no demonstrated preview-centering failure to rate as a blocker.

## Q6 — STEP_STYLE and moved pins

**Accepted:** The two leaves, defaults, integer range and partial strict UI payload fit the existing settings service and STYLE_STORE path. Appending them after Lock preserves the nine contiguous MEU-105 leaves. Row 2 explicitly moves AC-36.12, AC-38.6, AC-105.2, AC-143.2, AC-130.6 and the clamp kinds with their data. The MCP slices retaining the original nine leaves remain valid. The big-integer parser/service outcomes are explicitly pinned by AC-107.15 and are not reopened.

The defaults/leaves/range tables, `styleToolFor`/`styleToolOfMark`, focus-id set and size scrub have named edits and tests for optimism, failed refetch, selected-mark history and no PUT. Inserting the Step option rule after the existing rules preserves their priority; making AC-65.1's option table and AC-105.6's style mapping required Reds is appropriate. The type checker forces the extended records to stay complete. No additional delivery defect found here.

## Q7 — Controls, placement, labels and Lock

**Accepted:** The two contextual segmented controls and one Step button meet the fewest-controls/no-new-letter route pending D-781. Picks are local mount state; selected-mark changes are one undo step with no settings PUT. `LetterTool` preserves the eight existing letter mappings and their registry slice.

The Step placement branch follows ARMED_EDIT and Text, preserving a press on the selected badge as a move under Lock. Max-plus-one handles gaps and derives from the current history list after Undo; the placement limit is explicit. Disc radius in image pixels plus CSS padding gives sensible hit size across zoom. Step labels use their numbers; Line/Ellipse labels require per-kind counts at the viewport caller, which is within the listed modified files. No additional finding beyond the duplication exhaustion in F2.

## Q8 — DUPLICATE routing, focus and bounds

**Accepted:** A page-scoped, stateful, `palette: false` Ctrl+D entry fits `buildShortcutMap`, and the chord is presently unreserved. The published state, real shortcut-handler test harness, page `historyOwnsFocus` check and gesture guard cover fields, confirmations, modals and active gestures. Consuming Ctrl+D from a field without copying is an explicit chosen outcome, consistent with the existing Ctrl-chord handler; S14 addresses an actual Electron menu conflict. The chord/audit pin migration is scheduled before Green and the documentation audit follows row 5.

**Not accepted:** Reusing anchor-only `translateBody` as if it bounded every box (F1), or assigning an unbounded next step number (F2). These are product failures independent of the sound registry route.

## Q9 — Red rules and test selection

**Accepted:** The staged declarations provide the new modules/helpers before their behavior Reds, and row 2 supplies schemas, settings data and fixture keys. The 71-fixture Red checker selftest passed, including required-title boundaries, missing-name rejection and Electron launch-failure rejection. The id-length selftest passed four cases. Must-pass guards, AC-107.13 and AC-81.13 are excluded from `--require` and get dedicated checks. The changed AC-65.1 and AC-105.6 table expectations have genuine later behavior changes to make them Red.

The escaped-dot/trailing-space Vitest filters distinguish AC-106.10 from AC-106.1. The Python guard substrings distinguish .30/.28 from .3/.2. The Playwright patterns identify the two declared future titles within this spec; these future tests were not executed or collected. Assertions before locator actions and explicit exception/length checks address setup-vs-behavior failures.

**Clerical staging correction:** AC-106.16 is listed as a required Red, although HEAD_CLIP is intentionally unchanged and row 1 already adds `head`. The independent nine-case clip probe passes on that shape. Move this preservation check to the must-pass set; do not manufacture a failure or weaken `_clip_arrow`. Also correct the red/white expectation noted in Q5 before tests become immutable. The exact helper signatures mention an undefined `CropBox`; align their call/return adapters with the existing five-coordinate, `(mark, carry)` crop convention when writing the stubs. These are locally inferable plan corrections, not separate High findings.

## Q10 — Help, records, identity, scope and safety

**Accepted:** SHAPES_HELP describes the intended controls, step numbering, Duplicate and inherited modifiers. Its new sentences and moved resize pin have ACs. The actions-index rows name actual proposed controls/command; the audit and chord pins move in the stated rows. Row 6 checks both MEUs' `ready_for_review` state and row 48's executed Session 72 link, with its band following the pending D-779 ruling. Independent approval precedes their later approved state.

New files are explicitly LF; existing CRLF files have byte-preserving instructions and measured anchors. The id additions are below the existing hash boundary, with AC-81.13 run separately. Files Modified, project files and the scope set include the moved pins, fixture, helper modules and reused harnesses. I found no required missing executable: all seven plan-local scripts exist, and future modules/tests are inventoried.

The identity selftest passed. It binds code/tests/config, fixture and spec changes, new scripts, tracked/untracked state and runtime/font/binary identities, excluding the named closeout outputs. It was run only in its scratch-fixture mode; the real-tree identity was deliberately not run. Rulings/queue/shapes/bakes source inspection supports their stated baseline checks. The supplied baseline dry-run is not execution authorization. No material false-pass was demonstrated in these predicates.

The gate stops on the first failing step, checks nonempty matching identities, and runs only `capture-inbox.test.ts` for runtime. Clipboard-writing Electron specs are expressly excluded. In-memory/fake stores and the existing seam support the planned isolation. The plan forbids live audit/MCP servers, user-data reads and network access; the relevant test seams use recording fakes. No forbidden row or test action was identified in this review. This is source inspection, not a fresh certification of future test bodies.

## Checklist Results

The manual observer for source checks is `codex-independent-reviewer`; their exit code is null.

| Check | Result | Procedure / command | Exit | Evidence |
|---|---|---|---|---|
| PR-1 Plan/task alignment | fail | Compare DUPLICATE and the edge matrix against row 4's prescribed helper and AC-106.24 | null | F1: the prescribed helper cannot produce the declared edge outcomes. |
| PR-2 Not started | pass | `rtk proxy git status --porcelain --untracked-files=all`; read task states | 0 | Only nine plan files and the disclosed ignored-file discrepancy; all implementation rows unchecked. |
| PR-3 Task contract | pass | Inspect rows 0–6, H1 and H2 | null | Owners, deliverables, validations, dependencies and states are present. |
| PR-4 Validation realism | partial | Trace ACs, required Reds, guards and helper arithmetic | null | Edge assertions expose F1; step duplication lacks the F2 negative case; Q9 names inferable staging corrections. |
| PR-5 Sources | pass | Compare FIC/decision sources with 09 and grouping §9.8 | null | Sources and carried/pending decisions are distinguished. |
| PR-6 Review/corrections readiness | pass | Inspect Handoff Set and H1/H2 boundaries | null | Separate MEU handoffs and a rolling independent execution review are named. Round-2 census is not applicable. |
| PR-7 Scope | pass | Compare exclusions with user instructions, spec rows and D-676 | null | No missing required feature was disguised as an exclusion. |
| PR-8 Reachability/totality | partial | Trace production paths and synthesize step duplication with maximum 999 | null | F2 reaches an invalid outgoing mark; no ledger/control-defeat finding is asserted. |
| PR-9 Single statements | pass | Inspect named contracts against repeated matrices/ACs | null | Named definitions govern; Q5/Q9 identify inferable stale expectations rather than unresolved competing product rules. |
| IR / source retrieval | pass | Read plan/task by section and relevant production/test callers | null | Both entry-to-output traces were checked; no secret/data path was opened. |
| DR / artifact metadata | pass | Compare this report with REVIEW-TEMPLATE v2.2 and latest peer | null | Target, loop, round, independent author, findings and evidence are explicit. |
| Forbidden execution checks | n/a | Not run under the read-only review instruction | null | No product suites, build, baseline, gate or pyright execution claimed. |

## Probe Evidence

Commands ran from `P:/av-kit` with `PYTHONDONTWRITEBYTECODE=1` and UTF-8 output. Selftest TMP/TEMP pointed inside `C:/Temp/av-kit/s72/review/tmp`. Full receipts and scratch source are under `C:/Temp/av-kit/s72/review/`; decisive observations are embedded here.

```json
{"schema_version":"evidence.v1","check_id":"s72-review-selftests","command":"rtk proxy P:/av-kit/.venv/Scripts/python.exe C:/Temp/av-kit/s72/review/run-selftests.py","cwd":"P:/av-kit","scope":"red-check.py, identity.py, id-length.py and openapi-delta.py --selftest only","phase":"targeted","exit_code":0,"result":"pass","tested_state":"plan-review at HEAD 5db36236dbdff78bc846bd4586206897c7e9be94; scratch fixtures only","output":"red-check: 71 fixtures, 0 wrong; identity: 0 failures; id-length: 4 cases, 0 wrong; openapi-delta: 8 cases, 0 wrong. No product suite ran.","fresh":true}
```

```json
{"schema_version":"evidence.v1","check_id":"s72-review-default-omit","command":"rtk proxy P:/av-kit/.venv/Scripts/python.exe C:/Temp/av-kit/s72/review/default-probe.py","cwd":"P:/av-kit","scope":"in-memory Pydantic 2.14.1 model variant","phase":"targeted","exit_code":0,"result":"pass","tested_state":"in-memory model, no app resources","output":"Missing/explicit default head omitted; both retained; unrelated bg_color null preserved. Empty, control, surrogate, case, int and null cases refused.","fresh":true}
```

```json
{"schema_version":"evidence.v1","check_id":"s72-review-geometry-counterexamples","command":"rtk proxy P:/av-kit/.venv/Scripts/python.exe C:/Temp/av-kit/s72/review/probes.py","cwd":"P:/av-kit","scope":"source-faithful Python arithmetic transcriptions plus production arrowhead_vertices and clip_mark on in-memory values","phase":"targeted","exit_code":0,"result":"pass","tested_state":"plan formulas and production helpers at HEAD 5db36236dbdff78bc846bd4586206897c7e9be94","output":"Counterexamples reproduced: rect (89,20,10,10) copies to (99,30,10,10), far x=109 on width 100; filling (0,0,99,79) copies to (10,10,99,79); max 999 plus one is 1000. Ellipse point 50 px beyond tip has metric 5 <= 10. New start-head point is inside its triangle but current hit=false; removed end-head point has current hit=true. Red luminance 0.2126 selects black. Nine HEAD_CLIP cases preserve heads. These are not TS runtime executions.","fresh":true}
```

```json
{"schema_version":"evidence.v1","check_id":"s72-review-step-ink","command":"rtk proxy P:/av-kit/.venv/Scripts/python.exe C:/Temp/av-kit/s72/review/badge-probe.py","cwd":"P:/av-kit","scope":"12 STEP_BAKE size/number pairs, in-memory Pillow masks using _load_font","phase":"targeted","exit_code":0,"result":"pass","tested_state":"local Segoe UI font and proposed layout formulas","output":"12 pairs pass ink containment and tolerance. Worst exclusive-edge ink-box offset dx=3.5 px, dy=0.5 px. Browser preview was not measured.","fresh":true}
```

## Verdict

`changes_required` — resolve High findings F1 and F2 through plan corrections, preserving the requested scope and approved prior behavior. F3/F4 are non-blocking Medium behavior findings. Correct the locally inferable Q5/Q9 expectations before freezing tests. No Critical finding, review-cap exhaustion or reviewer-unavailability condition was found.

This report is the complete round-1 artifact for coordinator validation and byte-for-byte canonical saving. It does not grant execution approval or authorize repository edits.


## Recheck (Round 2)

**Date:** 2026-11-14. **Workflow:** `/plan-critical-review`. **Agent:** `codex-independent-reviewer` (Codex; independent of Claude Code/Anthropic).

**Intent anchor:** Session 72 adds the last three marks of the capture annotation synthesis.

**Intent assessment: yes, as a plan.** Executing the corrected plan delivers Line/Both heads, Ellipse, numbered Step placement and bounded Ctrl+D duplication. F1–F4 are fixed in the planning contract. No new substantive finding was demonstrated. The pending human gate and D-779–D-782 remain as given; this plan approval does not supply execution authorization.

### Prior Pass Summary

| Finding | Prior Status | Recheck Result |
|---|---|---|
| F1 | open | fixed |
| F2 | open | fixed |
| F3 | open | fixed |
| F4 | open | fixed |

### New Findings

| # | Severity | Blocking | Kind | Finding | File:Line | Recommendation | Status |
|---|---|---|---|---|---|---|---|
| None | — | no | — | None | — | — | fixed |

### R1 — Duplicate bounds and matrix

**Fixed.** `implementation-plan.md:219` defines the delta from the far extent, rather than calling the origin-only box translation. Independent arithmetic reproduced all **25 expanded matrix cases** (`:355–371`), including the first ordinary rect and the 24 edge cases owned by AC-106.24 (`:398`). Closed rect/ellipse bounds of W−1/H−1 agree with `_clip_rect` (`packages/core/src/avkit_core/domain/capture.py:516`) and Pillow's inclusive rectangle (`packages/infrastructure/src/avkit_infra/capture/adapter.py:868`). Filled-box bounds W/H agree with `_clip_half_open` (`domain/capture.py:497`). The arrow endpoint and text/step anchor conventions preserve their existing coordinate contracts; they do not promise to contain every glyph, badge pixel or arrowhead vertex. D-676's closed ellipse-crop rule is preserved separately.

For an initially bounded mark, each coordinate extent stays bounded, each delta is in [0,10], and dimensions do not change. The rule preserves an already overflowing mark on an exhausted axis rather than repairing approved drag/import behavior by shifting it left or resizing it. That is consistent with the explicit no-left/no-up/no-resize choice. AC-106.24's right-edge rect and filling-box exact assertions fail against the old origin-only clamp: `(99,30,10,10)` and `(10,10,99,79)` are rejected copies. No additional family-bound defect was found.

### R2 — Step 999 stop, selection and history

**Fixed.** The DUPLICATE contract (`implementation-plan.md:219`) now stops before appending or applying history, retains the list and selected mark, and sets `Step numbers stop at 999`. The same limit and status govern STEP_PLACE (`:215`); D-774 (`:885`) and D-777 (`:931`) agree. It guards on the maximum in the whole list, not the selected step's number. AC-107.21 (`:476`) covers both selecting step 5 beside 999 and selecting 999 itself, unchanged Undo, unchanged list/selection, the status and `defaultPrevented`, plus normal 1,2→3/Undo/reuse and rect copying beside 999.

The shortcut remains enabled with a valid selection at exhaustion. `createShortcutHandler` calls `preventDefault()` before `entry.action()` (`ui/src/renderer/src/registry/shortcuts.ts:244–251`), so returning early in the page listener still consumes Ctrl+D. Not calling `applyHistory` also avoids its past push, future clearing and selection-related work (`CapturePage.tsx:830`). Source inspection establishes plan feasibility; no runtime keyboard/history pass is claimed.

### R3 — Ellipse distance and Red behavior

**Fixed.** The polyline at `implementation-plan.md:200` approximates CSS distance correctly for AC-106.13 (`:387`). Independent transcription checked **14 press points**, compared with a 32,768-chord reference. Maximum observed difference was **0.005930 CSS px**. With A=max(a,b), the interpolation error is at most Aπ²/(2N²); N≥64 and N≥πA give a global bound π/128 ≈ **0.024544 px**. The nondegenerate cases are about 2 px or more clear of the 10 px threshold. The 1×1 fallback intentionally uses the box predicate.

**Not every parameter case is Red against today's box-outline hit.** The new large-ellipse corner is: the old predicate measures 1 px and hits `(11,11)`, while the ellipse distance is about **29.834 px** and misses. The other listed points already produce the expected Boolean result with the box predicate; the wide/tall misses are valuable negatives against the discarded normalized-radius formula. This satisfies the actual row-3 contract: each required **AC title** needs at least one assertion-failing block (`task.md:46`; `red-check.py:294–303`). It does not require every preservation variant to fail. Retain those passing variants and report only actual failed ids in FAIL_TO_PASS (`task.md:103`). No actual Vitest Red run was permitted or claimed.

| Representative case | Proposed CSS distance | Expected | Old box |
|---|---:|---|---|
| large corner `(11,11)` | 29.834087 | miss | hit |
| wide tip +5 / +12 / +50 | 5 / 12 / 50 | hit / miss / miss | same |
| tall tip +5 / +12 / +50 | 5.001492 / 12.001347 / 50.001268 | hit / miss / miss | same |
| scale 2, 12 inside | 11.995671 | miss | miss |
| scale 0.5, 8 / 12 inside | 7.994070 / 11.994070 | hit / miss | same |

### R4 — Head hit triangles and existing pins

**Fixed.** HEAD_HIT (`implementation-plan.md:197`) uses the existing end triangle only for End/Both and the reversed-endpoint triangle additionally for Both. The whole shaft test and selected endpoint path remain unchanged. Independent geometry gives end-base x≈209.9553, start-base x≈190.0447 and y≈56.5034/143.4966 at stroke 20. Thus `(240,125)` hits End/Both only; `(160,125)` hits Both only; `(200,125)` misses all; `(297,100)` still hits the shaft for None. None's removed end head and Both's start head create genuine assertion Reds under AC-106.10 (`:384`); End is intentionally a preservation variant.

The test now lives in the pure `capture-shapes.test.ts` inventory (`:538`, `:700`), row 3 includes that file and `--require AC-106.10`, and row 4 explicitly implements HEAD_HIT (`task.md:92–93`). The legacy arrow pins keep omitted-head/default-End semantics, the same radii, shaft predicate and endpoint priority (`ui/tests/unit/capture-hit-test.test.ts:49–122`, `:179–193`). Source inspection finds no conflict; these tests were not executed.

### R5 — Contrast, guards, clip signatures and preview

**Correct, with one clerical remnant.** AC-107.9 (`implementation-plan.md:464`) now expects black for red (0.2126 > 0.179) and white for blue (0.0722). AC-106.16 is a guard (`:390`, `:676`) and is absent from row 3's required Red set. The separate Python loop (`task.md:92`) runs `.16`, `.30` and `.28` over their two inventoried unit files, captures each exit and requires a positive passed count. Under the stipulated test naming, each `-k` substring selects its intended id, not .1/.3/.2 or neighboring numbered ACs. The UI guard loop is precisely .14/.31/.27/.29; the escaped-dot, trailing-space filters, AC-107.13 and AC-81.13 filters remain distinct.

The clip signatures at `implementation-plan.md:375` and `:456` match `clip_mark(mark,left,top,width,height)`, returning `(mark-or-None, MarkCarry)`; the staging call at `:657` is correct and `CropBox` is gone. **Clerical note:** `task.md:91` still prints `_clip_step(mark, box)` and `task.md:53` abbreviates its stub as `None`. Read both as the canonical five-coordinate call and `(None,"dropped")` specified at `implementation-plan.md:633` and `:657`. The type check would catch the stale call; it does not conceal a missing implementation deliverable.

STEP_CENTRE (`:209`), AC-107.10–.12 (`:465–467`), AC-107.24 (`:479`) and S16 (`:754`) now distinguish measured bake centering, shared preview attributes and the real Electron horizontal `getBBox()` measurement. Circle `cx` and SVG text box coordinates are comparable in their shared local SVG frame. S16 names the measured checks. Vertical preview centering remains the explicitly stated shared-baseline assumption, not a claimed browser measurement. No browser check was run in this review.

### R6 — Correction consistency

**No new substantive defect found.** The AC tables remain **34 MEU-106 + 30 MEU-107**. HEAD_HIT is present in the mechanism contract, modified-file entry, pure test home, row-3 required Reds, row-4 deliverables and row-5 MEU-106 note check. HEAD_CLIP is consistently a guard. DUPLICATE's matrix, ACs and D-777 agree; the 999 rule also agrees with D-774. The task command contains **45 distinct required Red titles**, with no duplicates; the HEAD_HIT/HEAD_CLIP swap is correct. Test homes and dependency order still provide the names/data before behavior tests. The stale task clip shorthand above is the only residual correction inconsistency observed. No scope, count or delivery gap warrants another plan round.

### Round-2 Checklist Results

| Check | Result | Procedure / command | Exit | Evidence |
|---|---|---|---|---|
| R1 / F1 | pass | Independent arithmetic transcription of DUPLICATE and comparison with clipping/bake conventions | 0 | 25 expanded matrix cases match; old origin-only clamp fails exact edge assertions. |
| R2 / F2 | pass | Manually trace the new stop and AC-107.21 through shortcut and history sources; observer codex-independent-reviewer | null | Selection/list/history/status and prevented default are covered; non-step duplication remains enabled. |
| R3 / F3 | pass | Independent CSS-distance transcription versus 32,768-chord reference | 0 | 14 points match; max observed error 0.005930 px; large-corner is a genuine old-box assertion failure. |
| R4 / F4 | pass | Independent head-triangle transcription and manual legacy-pin inspection | 0 | None/Both new assertions distinguish old behavior; default End and endpoint path remain the same. |
| R5 / test routing | pass | Parse row 3 and compare intended names, filters and guard homes; manual contrast/signature/preview review | 0 | 45 unique required titles; per-id Python guards and four UI guards are correctly separated. |
| R6 / consistency | pass | Manually compare mechanisms, AC counts, test inventories, task rows and D-774/D-777; observer codex-independent-reviewer | null | 34+30 ACs; no new substantive inconsistency; stale task clip shorthand is clerical. |
| Unstarted/read-only scope | pass | Read canonical task statuses; independently inspect git HEAD and status | 0 | HEAD 5db36236dbdff78bc846bd4586206897c7e9be94; only disclosed untracked plan/report/settings-ignore discrepancy; no product edit. |
| Product suites, backend, builds, baseline, session gate, pyright and assert-never probe | n/a | Not run under the explicit review instruction | null | This is plan/source review with scratch arithmetic only. |

```json
{"schema_version":"evidence.v1","check_id":"s72-round2-arithmetic-and-selection","command":"rtk proxy .venv/Scripts/python.exe C:/Temp/av-kit/s72/review/recheck-r2.py","cwd":"P:/av-kit","scope":"DUPLICATE matrix, ELLIPSE_HIT points, HEAD_HIT triangles and row-3 title selection","phase":"targeted","exit_code":0,"result":"pass","tested_state":"working-tree Session 72 plan/task at HEAD 5db36236dbdff78bc846bd4586206897c7e9be94; arithmetic transcriptions only","output":"DUPLICATE PASS 25 expanded matrix cases. ELLIPSE PASS 14 points; max reference error 0.005930 px; only large-corner differs from old box predicate. HEAD PASS: end/none/both truth tables agree. ROW3 PASS 45 unique --require titles; HEAD_HIT required and HEAD_CLIP excluded; test_ac_106_16, test_ac_106_30 and test_ac_107_28 select their intended prefixes. No product tests run.","fresh":true}
```

All round-2 writes are under `C:/Temp/av-kit`; repository files remain untouched. No forbidden source, user data, network, system clipboard or installed app server was accessed. The supplied correction receipts were not represented as independently rerun product checks. Completion-preflight was consulted for artifact readiness; its implementation-completion requirements do not authorize executing this unstarted plan.

### Verdict

`approved` — F1, F2, F3 and F4 are fixed as planning defects. There are no new High/Critical findings and no unresolved blocker. Keep the clip-call shorthand correction and the distinction between Red and preservation variants as clerical implementation guidance. The coordinator may validate and save this complete rolling report byte for byte to the canonical path. Mat's explicit execution gate remains pending.
