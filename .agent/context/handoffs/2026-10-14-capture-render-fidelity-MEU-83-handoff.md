---
date: "2026-10-16"
project: "capture-render-fidelity"
meu: "MEU-83"
status: "complete"
action_required: "VALIDATE_AND_APPROVE"
template_version: "2.2"
verbosity: "standard"
plan_source: "docs/execution/plans/2026-10-14-capture-render-fidelity/implementation-plan.md"
build_plan_section: "bp09"
agent: "claude-code-local (Claude Opus 5.5)"
reviewer: "Codex gpt-6.1-sol via local dispatch"
predecessor: ".agent/context/handoffs/2026-10-14-capture-render-fidelity-MEU-82-handoff.md"
---

# Handoff: 2026-10-14-capture-render-fidelity-MEU-83-handoff

> **Status**: `complete`
> **Action Required**: `VALIDATE_AND_APPROVE`

---

## Scope

**MEU**: MEU-83 — `capture-arrow-geometry`. The arrow shaft ends inside the head, and the bake is anti-aliased.

The arrow now draws the same way in the preview and the bake, and the bake is anti-aliased:
- **Head (D-12 default, `ARROW_HEAD`):** `head = max(10, 5 × stroke)` at `0.45` rad, up from `4 ×` / `0.40`. The execution message was silent on D-12, so the plan default applies ([walkthrough.md](../../../docs/execution/plans/2026-10-14-capture-render-fidelity/walkthrough.md) §Execution message). The plan's D-12 `human_message_reference` still reads "pending"; the reflection records the default.
- **Shaft (D-13, `SHAFT_END`):** the shaft ends at the back of the head plus `ARROW_SHAFT_OVERLAP_PX = 1`, so its flat cap no longer pokes through the tip. An arrow shorter than that draws only the head.
- **Bake (D-14, `BAKE_AA`):** each arrow is drawn into an `L` mask at `SUPERSAMPLE = 4` on its own clipped tile, downscaled with LANCZOS and composited in the mark colour.
- **Preview head outline (D-21, AC-83.9, human-approved 2026-10-16):** the head polygon has `stroke="none"`, so it no longer inherits a 1 px outline from the group stroke.

**Test amendments applied:** TA-1, TA-2 (head values and `ARROW_CASES`), TA-5, TA-6 (read from/to on the arrow `<g>`) and TA-7 (D-20, human-approved: AC-65.3 asserts the head length 35). No other assertion changed. `PRODUCT_SCOPE` holds: the gate's `scope-ast` reports `frozen adapter functions changed: []`.

---

## Acceptance Criteria

| AC | Type | Description | Source | Test(s) | Status |
|----|------|-------------|--------|---------|--------|
| AC-83.1 | unit | TS `ARROW_HEAD`, `ARROW_SHAFT_OVERLAP_PX`; `arrowheadVertices` and `arrowShaftEnd` reproduce every `ARROW_CASES` entry to 1e-9 (TA-1) | Spec 09:721, 09:723; D-12, D-13 | `ui/tests/unit/capture-arrow-head.test.ts` `AC-83.1 …` (2); TA-1 `AC-59.2 …` | ✅ |
| AC-83.2 | unit | Python `ARROWHEAD_*`, `ARROW_SHAFT_OVERLAP_PX`, `arrowhead_vertices`, `arrow_shaft_end` reproduce `ARROW_CASES` (TA-2) | Spec 09:721 | `tests/unit/test_capture_adapter.py::test_ac_83_2_python_arrow_geometry_reproduces_arrow_cases`; TA-2 `::test_ac_59_2_shared_arrowhead_vertices` | ✅ |
| AC-83.3 | unit | `SHAFT_INSIDE_HEAD` in TS and Python; an end at the tip puts the corners outside | D-13 | `capture-arrow-head.test.ts` `AC-83.3 …`; `test_capture_adapter.py::test_ac_83_3_shaft_corners_inside_head` | ✅ |
| AC-83.4 | integration | The arrow `<g>` keeps `x1/y1/x2/y2 = from/to` (TA-5); `<line>` ends at `arrowShaftEnd`; `<polygon>` = `arrowHeadPoints`; the short case has no `<line>`, the zero-length case no `<polygon>`; Electron AC-66.14 reads the `<g>` (TA-6) | Spec 09:721; D-19 | `ui/tests/unit/capture-page.behavior.test.ts` `AC-83.4 …`; TA-5 `AC-66.11 …`; TA-6 `ui/tests/e2e/capture-inbox.test.ts` `AC-66.14 …` | ✅ |
| AC-83.5 | integration | `ARROW_TIP_ORACLE` on the real adapter; the negative control (shaft end patched to `to`) fails | Spec 09:724 | `test_capture_adapter.py::test_ac_83_5_arrow_tip_oracle` | ✅ |
| AC-83.6 | integration | `EDGE_ORACLE` on the real adapter (blend fraction ≥ 0.4) | Spec 09:722, 09:724; D-14 | `test_capture_adapter.py::test_ac_83_6_edge_oracle` | ✅ |
| AC-83.7 | integration | An arrow past the image edge bakes inside the clipped tile, `(111, 60)` is the mark colour; a tile wholly outside bakes to the original | D-14; plan review F1 | `test_capture_adapter.py::test_ac_83_7_arrow_tile_clipped_to_image` | ✅ |
| AC-83.8 | unit | `_apply_arrow` still calls `draw.line`/`draw.polygon` (AC-35.13), uses `LANCZOS` and `SUPERSAMPLE`, never a full-canvas × `SUPERSAMPLE` image | Spec 09:722; AC-35.13 | `test_capture_adapter.py::test_ac_83_8_apply_arrow_supersamples_the_tile_only`; `::test_ac_35_13_arrow_uses_line_and_polygon` (unchanged) | ✅ |
| AC-83.9 | integration | The head `<polygon>` has `stroke="none"`; the `<g>` keeps `stroke` | Human-approved 2026-10-16 D-21 | `capture-page.behavior.test.ts` `AC-83.9 …` | ✅ |
| AC-35 (cross-ref) | regression | AC-35.13 source check stays green without amendment | Local Canon | `test_capture_adapter.py::test_ac_35_13_arrow_uses_line_and_polygon` | ✅ |
| AC-59 (cross-ref) | regression | AC-59.2 head vertices, amended by TA-1/TA-2 (AC-59.19 is MEU-82's TA-3/TA-4) | plan `TEST_AMENDMENTS` | `capture-arrow-head.test.ts` `AC-59.2 …`; `test_capture_adapter.py::test_ac_59_2_shared_arrowhead_vertices` | ✅ |
| AC-65 (cross-ref) | regression | AC-65.3 stroke edit, amended by TA-7 (head length 35 = 5 × 7) | Human-approved D-20 | `capture-page.behavior.test.ts` `AC-65.3 options keep their behavior …` | ✅ |
| AC-66 (cross-ref) | regression | AC-66.11 (TA-5) and AC-66.14 (TA-6) read from/to on the arrow `<g>`; values unchanged | D-19 | `capture-page.behavior.test.ts` `AC-66.11 ZOOM_EXAMPLE …`; `capture-inbox.test.ts` `AC-66.14 …` | ✅ |
| AC-67 (cross-ref) | regression | The AC-67.1 flatten byte oracle bakes through the same adapter and follows the new drawing without change | plan MEU-83 | `tests/e2e/test_api_capture_flatten.py::test_ac_67_1_flatten_png_with_backup` | ✅ |
| AC-82 (cross-ref) | — | Owned by MEU-82 | plan MEU-82 | [MEU-82 handoff](2026-10-14-capture-render-fidelity-MEU-82-handoff.md) | see MEU-82 |
| AC-39, AC-84 (cross-ref) | — | Owned by MEU-84 (AC-39.12 amended by AC-84.4) | plan MEU-84 | [MEU-84 handoff](2026-10-14-capture-render-fidelity-MEU-84-handoff.md) | see MEU-84 |

<!-- CACHE BOUNDARY -->

---

## Evidence

### FAIL_TO_PASS

| Test | Red Output (hash/snippet) | Green Output | File:Line |
|------|--------------------------|--------------|-----------|
| AC-59.2 pytest (TA-2) | `assert (88.947…, 4.673…) == approx((86.49…, 6.52…))` (the 4 / 0.40 head) | pass | `tests/unit/test_capture_adapter.py:572` |
| AC-83.2 | `assert (4, 0.4, 10) == (5, 0.45, 10)` | pass | `test_capture_adapter.py:665` |
| AC-83.3 pytest | `AttributeError: … has no attribute 'arrow_shaft_end'` (declared new) | pass | `test_capture_adapter.py:701` |
| AC-83.5 | `assert 53 == 0` (53 leak pixels, as planning R-3 predicted) | pass; negative control fails as required | `test_capture_adapter.py:728` |
| AC-83.6 | `assert (0 / 641) >= 0.4` (blend fraction 0.0) | pass | `test_capture_adapter.py:755` |
| AC-83.8 | `assert 'Image.Resampling.LANCZOS' in '…'` | pass | `test_capture_adapter.py:809` |
| AC-59.2 Vitest (TA-1) | `expected 88.94726807196538 to be close to 86.49329346470985` | pass | `ui/tests/unit/capture-arrow-head.test.ts:38` |
| AC-83.1 | `expected 4 to be 5` | pass | `capture-arrow-head.test.ts:56` |
| AC-83.3 Vitest | `TypeError: mod.arrowShaftEnd is not a function` (declared new) | pass | `capture-arrow-head.test.ts:91` |
| AC-83.4 | `line x2: expected 12.50670653529015 to be less than or equal to 1e-9` | pass | `ui/tests/unit/capture-page.behavior.test.ts:932` |
| AC-83.9 | `expected null to be 'none'` | pass | `capture-page.behavior.test.ts:978` |
| AC-65.3 (TA-7) | `expected 27.999999999999996 to be close to 35` | pass | `capture-page.behavior.test.ts:1503` |
| AC-83.7, AC-66.11 (TA-5) | pass on baseline: the adapter already clips, and the `<g>` already carries `x2/y2`; AC-83.7 guards the tile code | pass | `test_capture_adapter.py:790`; `capture-page.behavior.test.ts:1903` |

Every Red and Green receipt and its decisive lines are in [walkthrough.md](../../../docs/execution/plans/2026-10-14-capture-render-fidelity/walkthrough.md) (§MEU-83 Red, §MEU-83 Green). Row 5 run 1 had two unrelated Electron failures (AC-60.12, AC-67.35) that passed alone 3/3 and 40/40 under `--repeat-each 20`; the full suite passed in row 5 runs 2 and 4, row 8 and H1-2 (S6 clear).

### Commands Executed

```json
{"schema_version":"evidence.v1","check_id":"s36-83-red","command":"RECEIPTS_DIR=C:/Temp/av-kit pwsh: task.md row 4 command, verbatim","cwd":"P:/av-kit/.claude/worktrees/s36-capture-render-fidelity","scope":"MEU-83 Red: pytest (TA-2, AC-83.2, 83.3, 83.5, 83.6, 83.7, 83.8), Vitest (TA-1, TA-5, TA-7, AC-83.1, 83.3, 83.4, 83.9), red-check","phase":"red","exit_code":0,"result":"pass","tested_state":"HEAD 534beb1 plus MEU-82 Green and the row 4 tests and ARROW_CASES fixture","output":"pytest 6 failed, 1 passed, 16 deselected | Vitest Test Files 2 failed (2), Tests 6 failed | 86 passed (92) | red-check: 2 receipt(s), 0 problem(s)","fresh":true}
```

```json
{"schema_version":"evidence.v1","check_id":"s36-83-green","command":"RECEIPTS_DIR=C:/Temp/av-kit pwsh: task.md row 5 command, verbatim","cwd":"P:/av-kit/.claude/worktrees/s36-capture-render-fidelity","scope":"MEU-83 Green (run 4): pytest (adapter, bake fixture, test_api_capture_flatten, test_api_captures), Vitest, 3 builds, Electron capture-inbox","phase":"green","exit_code":0,"result":"pass","tested_state":"HEAD 534beb1 plus MEU-82 and MEU-83 product changes","output":"pytest 63 passed, 1 warning | Vitest Test Files 4 passed (4), Tests 132 passed (132) | 3 x built in | Electron 29 passed","fresh":true}
```

```json
{"schema_version":"evidence.v1","check_id":"s36-83-green-e2e-repeat20","command":"RECEIPTS_DIR=C:/Temp/av-kit rtk proxy npm --prefix ui run test:e2e -- tests/e2e/capture-inbox.test.ts --grep \"AC-60.12|AC-67.35\" --repeat-each 20","cwd":"P:/av-kit/.claude/worktrees/s36-capture-render-fidelity","scope":"S6 stress of the two tests that failed once in row 5 run 1","phase":"runtime","exit_code":0,"result":"pass","tested_state":"HEAD 534beb1 plus MEU-82 and MEU-83 product changes","output":"40 passed","fresh":true}
```

```json
{"schema_version":"evidence.v1","check_id":"s36-gate-row8","command":"$env:ELECTRON_RUN_AS_NODE=$null; RECEIPTS_DIR=C:/Temp/av-kit rtk proxy pwsh -NoProfile -File docs/execution/plans/2026-10-14-capture-render-fidelity/session-gate.ps1 (task.md row 8, verbatim)","cwd":"P:/av-kit/.claude/worktrees/s36-capture-render-fidelity","scope":"D6 session gate (attempt 5): identity, py-types, py-lint, py-lint-tools, ui-types, ui-lint, task-contract, scope-ast, scope-paths, py-tests (baseline rule G-1), ui-tests, ui-build, ui-harness-build, ui-picker-stub (G-2), openapi, state-render, ui-electron, e2e-repeat, identity-npm, identity-after","phase":"full","exit_code":0,"result":"pass","tested_state":"534beb174e2be1a97fc0cd248f53b4b8cdc83e49+53752bff3673103ed7b022f1acc53376c3170362093ec3896b34747ff49615d4","output":"session-gate: all steps exit 0 | py-tests 2 failed, 674 passed; baseline rule failed=2 outside_baseline=[] errors=0 | ui-tests 85 files, 815 tests passed | ui-electron 139 passed (2.8m) | e2e-repeat 20 passed (34.3s) | scope-ast frozen adapter functions changed: [] | scope-paths changed paths: 33 outside scope: [] | tested_state before == after","fresh":true}
```

```json
{"schema_version":"evidence.v1","check_id":"s36-gate-h1-2","command":"$env:ELECTRON_RUN_AS_NODE=$null; RECEIPTS_DIR=C:/Temp/av-kit rtk proxy pwsh -NoProfile -File docs/execution/plans/2026-10-14-capture-render-fidelity/session-gate.ps1 *> C:/Temp/av-kit/s36-gate-h1.txt (task.md H1-2, verbatim)","cwd":"P:/av-kit/.claude/worktrees/s36-capture-render-fidelity","scope":"D6 session gate re-run at H1-2, the same steps as row 8","phase":"full","exit_code":0,"result":"pass","tested_state":"534beb174e2be1a97fc0cd248f53b4b8cdc83e49+53752bff3673103ed7b022f1acc53376c3170362093ec3896b34747ff49615d4","output":"session-gate: all steps exit 0 | py-tests 2 failed, 674 passed, 1 warning; baseline rule failed=2 outside_baseline=[] errors=0 | ui-tests 85 files, 815 tests passed | ui-electron 139 passed (2.5m) | e2e-repeat 20 passed (37.7s) | scope-ast frozen adapter functions changed: [] | scope-paths changed paths: 37 outside scope: [] | identity-npm @playwright/test@1.62.1, electron@42.9.3 | tested_state before == after","fresh":true}
```

### Quality Gate Results

The shared gate is `session-gate.ps1`, run at row 8 (attempt 5) and again at H1-2. Both runs printed the same `tested_state`. The handoffs and every row 9 hub file are project artifacts (`identity.py` `PROJECT_ARTIFACTS`), so H1-6b re-derives that state from the live tree.

**Two gate changes were made after plan approval**, both to the plan-local script only, with no test, assertion or product change. They are recorded in [walkthrough.md](../../../docs/execution/plans/2026-10-14-capture-render-fidelity/walkthrough.md) §Gate and in the MEU-82 handoff Decision Log (D-25, D-26), and they are named in the execution review prompt:
- **G-1:** `py-tests` runs without `-x` and applies the plan's §Baseline rule. Pytest exit 1 passes only when every `FAILED` id is one of the two §Baseline packaging tests (`AC-24.10`, `AC-25.10`, which need the gitignored PyInstaller tree and ffmpeg) and nothing errors.
- **G-2:** the Electron suite's gitignored prerequisites become stages: `ui-harness-build` (AC-51.7) and `ui-picker-stub` (`capture-picker.test.ts`).

| Step | Stage | Exit | Decisive line (H1-2) |
|---|---|---|---|
| identity-before | identity | 0 | `tested_state 534beb1…+53752bff…15d4` |
| py-types, py-lint, py-lint-tools, ui-types, ui-lint, task-contract | static | 0 | `All checks passed!` (ruff) |
| scope-ast | static | 0 | `frozen adapter functions changed: []` |
| scope-paths | static | 0 | `changed paths: 37 outside scope: []` |
| py-tests | full | 1 → 0 (G-1) | `2 failed, 674 passed, 1 warning`; `baseline rule: failed=2 outside_baseline=[] errors=0` |
| ui-tests | full | 0 | `Test Files 85 passed (85)`, `Tests 815 passed (815)` |
| ui-build, ui-harness-build, ui-picker-stub | full | 0 | — |
| openapi | full | 0 | — |
| state-render | full | 0 | `Drift check passed — SSOT loaded (91 MEUs, 12 phases)` |
| ui-electron | runtime | 0 | `139 passed (2.5m)` |
| e2e-repeat | runtime | 0 | `20 passed (37.7s)` (AC-82.6 and AC-84.5, `--repeat-each=10`) |
| identity-npm | identity | 0 | `@playwright/test@1.62.1`, `electron@42.9.3` |
| identity-after | identity | 0 | `tested_state before == after` |


---

## Changed Files

| File | Action | Summary |
|------|--------|---------|
| `ui/src/renderer/src/features/capture/capture-arrow-head.ts` | modified | `ARROW_HEAD` 5 / 0.45, `ARROW_SHAFT_OVERLAP_PX = 1`, `arrowShaftEnd` |
| `ui/src/renderer/src/features/capture/CaptureViewport.tsx` | modified | `<line>` to `arrowShaftEnd` (none when `null`); head `<polygon stroke="none">` (D-21) |
| `packages/infrastructure/src/avkit_infra/capture/adapter.py` | modified | `ARROWHEAD_*`, `ARROW_SHAFT_OVERLAP_PX`, `SUPERSAMPLE`, `ARROW_TILE_PAD_PX`, `arrow_shaft_end`, `_apply_arrow` through `BAKE_AA` |
| `ui/tests/e2e/fixtures/capture-geometry.json` | modified | `ARROW_CASES` (`arrows`; sha256 `2078b80c…`) |
| `ui/tests/unit/capture-arrow-head.test.ts` | modified | AC-83.1, AC-83.3, TA-1 |
| `ui/tests/unit/capture-page.behavior.test.ts` | modified | AC-83.4, AC-83.9, TA-5, TA-7 |
| `ui/tests/e2e/capture-inbox.test.ts` | modified | TA-6 |
| `tests/unit/test_capture_adapter.py` | modified | AC-83.2, AC-83.3, AC-83.5–83.8, TA-2 |

Shared by all three MEUs (listed here and in each handoff):

| File | Action | Summary |
|------|--------|---------|
| `docs/build-plan/09-screenshot-capture.md` | modified (row 9) | `:366` Arrow row, `:367` Text row, `:723` Head row |
| `docs/build-plan/build-priority-matrix.md` | modified (row 9) | rows 9.15–9.17 |
| `.agent/context/meu-status.yaml`, `docs/BUILD_PLAN.md`, `.agent/context/meu-registry.md` | modified (row 9, H1-3) | Phase 9 note, `last_updated`, MEU-82/83/84 status and `execution_plan`; the rendered regions |
| `docs/execution/plans/2026-10-14-capture-render-fidelity/session-gate.ps1` | modified (G-1, G-2) | the gate changes above |
| `docs/execution/plans/2026-10-14-capture-render-fidelity/red-check.py` | modified (row 2, S3) | strips ANSI CSI escapes before matching; two selftest fixtures |
| `docs/execution/plans/2026-10-14-capture-render-fidelity/implementation-plan.md`, `task.md`, `walkthrough.md`, `human-gate-decision.md`, `baseline.sha` | modified/new | D-20/D-21 (TA-7, AC-83.9), row status, durable evidence |

---

## Codex Validation Report

_Left blank for reviewer agent. Reviewer fills this section during `/validation-review`._

### Recheck Protocol

1. Read Scope + AC table
2. Verify each AC against Evidence section (file:line, not memory)
3. Independently probe the claimed behavior and compare decisive output
4. Verify the full gate is fresh and matches current D6 inputs; rerun if changed or unproven
5. Record findings below

### Findings

| # | Severity | Finding | File:Line | Recommendation | Status |
|---|----------|---------|-----------|----------------|--------|

### Verdict

_pending_

---

## Corrections Applied

None yet. The execution review has not run.

## Deferred Items

None.

---

## Decision Log

```yaml
decision_log:
  - id: D-20
    stage: execution
    question: "How should AC-65.3 check the stroke edit once short arrows render no shaft line?"
    resolution: human
    class: two-way
    chosen: "TA-7: assert the rendered head polygon length (35 = factor 5 x stroke 7)"
    source_tag: Human-approved
    precedents: ["2026-10-02-capture-flatten-backup/human-gate-decision.md:73-85 (A-3/TA-8 at the same S2 stop)", "TA-5/TA-6 (move shaft reads to an element that keeps the value)"]
    research: { engine: tavily+exa, sources: ["https://testing-library.com/docs/react-testing-library/intro"] }
    reasoning: "Row-1 census S2 (AC-65.3). Brief and options in walkthrough.md Decision S2 (row 1)."
    human_message_reference: "USER_EXPLICIT 2026-10-16 'Approve TA-7 (Recommended)'"
  - id: D-21
    stage: execution
    question: "Should MEU-83 also remove the 1 px outline the preview head inherits from the group stroke?"
    resolution: human
    class: product-preference
    chosen: "Add to MEU-83: head polygon stroke none, new AC-83.9; the group keeps stroke"
    source_tag: Human-approved
    precedents: [".agent/workflows/tdd-implementation.md:23 (authorized scope changes fold into plan/task/review)"]
    research: { engine: tavily+exa, sources: ["https://developer.mozilla.org/en-US/docs/Web/SVG/Reference/Attribute/stroke-width"] }
    reasoning: "Found while dispositioning AC-65.3. Brief in walkthrough.md Decision S2 (row 1)."
    human_message_reference: "USER_EXPLICIT 2026-10-16 'Add to MEU-83 (Recommended)'"
  - id: D-27
    stage: execution
    question: "AC-83.1/83.2 say the zero-length case has no head, but arrowheadVertices keeps its signature; where is the missing head asserted?"
    resolution: autonomous
    class: two-way
    chosen: "The unit tests assert the legacy from-to shaft (arrowShaftEnd returns to); the missing head is asserted where it is drawn (no polygon, AC-83.4; the bake already skips it)"
    source_tag: Local Canon
    precedents: ["adapter.py _apply_arrow skips the head at zero length", "implementation-plan.md AC-83.4 zero-length case"]
    research: { engine: none, sources: [] }
    reasoning: "Changing the vertex helpers' signatures was outside the plan. Asserting at the render and bake keeps the contract observable without a new API."
  - id: D-28
    stage: execution
    question: "How does the AC-83.8 size spy avoid passing on a bake that skips supersampling?"
    resolution: autonomous
    class: two-way
    chosen: "Assert no created image is at least SUPERSAMPLE times the canvas in both axes, and that a mask of SUPERSAMPLE times the BAKE_AA tile is created"
    source_tag: Local Canon
    precedents: ["implementation-plan.md AC-83.8 and BAKE_AA step 2"]
    research: { engine: none, sources: [] }
    reasoning: "The negative half alone is satisfied by drawing at 1x; the positive half pins the tile supersample the plan specifies."
  - id: D-29
    stage: execution
    question: "ruff format --check reports hunks in adapter.py, capture.py and test_capture_service.py; are they reformatted?"
    resolution: autonomous
    class: two-way
    chosen: "No; only the lines this session added are formatted, and the pre-existing hunks stay"
    source_tag: Local Canon
    precedents: ["git show HEAD versions fail the same format check", "plan PRODUCT_SCOPE and the scope-ast frozen functions"]
    research: { engine: none, sources: [] }
    reasoning: "Reformatting older code would widen the diff past PRODUCT_SCOPE and could touch frozen adapter functions. The gate runs ruff check, not format --check."
```

---

## History

| Event | Date | Agent | Detail |
|-------|------|-------|--------|
| Created | 2026-10-16 | claude-code-local (Claude Opus 5.5) | Initial MEU-83 handoff after the row 8 gate and the H1-2 re-run |
