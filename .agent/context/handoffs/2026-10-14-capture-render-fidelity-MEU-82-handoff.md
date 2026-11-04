---
date: "2026-10-16"
project: "capture-render-fidelity"
meu: "MEU-82"
status: "complete"
action_required: "VALIDATE_AND_APPROVE"
template_version: "2.2"
verbosity: "standard"
plan_source: "docs/execution/plans/2026-10-14-capture-render-fidelity/implementation-plan.md"
build_plan_section: "bp09"
agent: "claude-code-local (Claude Opus 5.5)"
reviewer: "Codex gpt-6.1-sol via local dispatch"
predecessor: ".agent/context/handoffs/2026-10-10-gui-polish-residuals-MEU-70-handoff.md"
---

# Handoff: 2026-10-14-capture-render-fidelity-MEU-82-handoff

> **Status**: `complete`
> **Action Required**: `VALIDATE_AND_APPROVE`

---

## Scope

**MEU**: MEU-82 — `capture-text-baseline`. The preview text sits on the bake's baseline.

The SVG preview of a text mark now sits on the bake's baseline. The preview used `dominant-baseline="hanging"` at `y`, so Chromium put the ink about 8 px above where the bake (Pillow `anchor="la"`) draws it. The preview now uses `alphabetic` at `y + ascent(font_size)`, where the ascent is the FreeType 26.6 rounding of Segoe UI's `2210/2048` (`SEGOE_ASCENT`, D-10). That is the same metric Pillow's `getmetrics()` returns for the bake. The plate box, hit test and bake are unchanged.

**Plan:** [implementation-plan.md](../../../docs/execution/plans/2026-10-14-capture-render-fidelity/implementation-plan.md) §MEU-82. **Execution authorization:** `USER_EXPLICIT` 2026-10-16 "proceed" ([walkthrough.md](../../../docs/execution/plans/2026-10-14-capture-render-fidelity/walkthrough.md) §Execution message).

**Test amendments applied (approved in the plan):** TA-3 (`capture-text-metrics.test.ts` AC-59.19, `'hanging'` → `'alphabetic'`) and TA-4 (`capture-page.behavior.test.ts` AC-59.19: `'alphabetic'` and the new `y` = `ann.y + ascent`; the plate assertions stay). No other test assertion changed.

This handoff also carries the session's shared gate record and the two gate-change decisions (D-25, D-26), since the gate covers all three MEUs.

---

## Acceptance Criteria

| AC | Type | Description | Source | Test(s) | Status |
|----|------|-------------|--------|---------|--------|
| AC-82.1 | unit | `segoeAscentPx(size)` equals `GEOMETRY_FIXTURE.segoe_ascent` for every size; `SEGOE_UNITS` exported; the naive `ceil(size*2210/2048)` differs at 38 | Spec 09:713; D-10 | `ui/tests/unit/capture-text-metrics.test.ts` `AC-82.1 …` (2) | ✅ |
| AC-82.2 | unit | Pillow `getmetrics()[0]` equals the fixture for every size; `la`−`ls` bottom equals the ascent; an off-by-one fixture fails the comparator | Spec 09:712; D-10 | `tests/unit/test_capture_text_metrics.py::test_ac_82_2_pillow_ascent_matches_geometry_fixture`, `::test_ac_82_2_comparator_detects_a_fixture_edited_by_one` (38, 177, 215, 354), `::test_ac_82_2_la_to_ls_offset_is_the_ascent` | ✅ |
| AC-82.3 | unit | `SVG_DOMINANT_BASELINE === 'alphabetic'`; `svgTextBaselineY` returns `y + segoeAscentPx(font_size)` (TA-3) | Spec 09:712; D-11 | `capture-text-metrics.test.ts` `AC-82.3 …`; TA-3 `AC-59.19 TEXT_MODULE …` | ✅ |
| AC-82.4 | integration | A loaded `Hi` mark at (10, 20), size 16, renders `<text y="38" dominant-baseline="alphabetic">` and plate (10, 26, 15, 12) (TA-4); a click in the plate selects it | Spec 09:712; `TEXT_ANCHOR` | `ui/tests/unit/capture-page.behavior.test.ts` `AC-82.4 …`; TA-4 `AC-59.19 SVG text uses start/alphabetic …` | ✅ |
| AC-82.5 | integration | The committed `capture-fidelity-annotated.png` equals a fresh real-adapter bake of `TEXT_FIXTURE_MARK`; the original is 240×120 white RGB; a bake at `y + 1` differs | D-18 | `tests/unit/test_capture_bake_fixture.py::test_ac_82_5_committed_annotated_png_equals_a_fresh_bake`, `::test_ac_82_5_bake_one_px_lower_differs`, `::test_ac_82_5_writer_reproduces_the_committed_pngs` | ✅ |
| AC-82.6 | integration | Electron `TEXT_PIXEL_ORACLE`: preview ink and plate match the baked PNG within 1 px at 100% | Spec 09:713; triage D-52 | `ui/tests/e2e/capture-inbox.test.ts` `AC-82.6 TEXT_PIXEL_ORACLE …` (also in the gate's `e2e-repeat`, 10×) | ✅ |
| AC-59 (cross-ref) | regression | AC-59.19 text anchors, amended by TA-3 and TA-4; AC-59.2 arrow head is MEU-83's TA-1/TA-2 | plan `TEST_AMENDMENTS` | `capture-text-metrics.test.ts` `AC-59.19 …`; `capture-page.behavior.test.ts` `AC-59.19 …` | ✅ |
| AC-35, AC-65, AC-66, AC-67, AC-83 (cross-ref) | — | Owned by MEU-83 (AC-35.13 source check, AC-65.3 TA-7, AC-66.11/66.14 TA-5/TA-6, the AC-67.1 flatten byte oracle, AC-83.1–83.9) | plan MEU-83 | [MEU-83 handoff](2026-10-14-capture-render-fidelity-MEU-83-handoff.md) | see MEU-83 |
| AC-39, AC-84 (cross-ref) | — | Owned by MEU-84 (AC-39.12 amended by AC-84.4, AC-84.1–84.6) | plan MEU-84 | [MEU-84 handoff](2026-10-14-capture-render-fidelity-MEU-84-handoff.md) | see MEU-84 |

<!-- CACHE BOUNDARY -->

---

## Evidence

### FAIL_TO_PASS

| Test | Red Output (hash/snippet) | Green Output | File:Line |
|------|--------------------------|--------------|-----------|
| AC-59.19 TEXT_MODULE (TA-3), AC-82.3 | `AssertionError: expected 'hanging' to be 'alphabetic'` | pass | `ui/tests/unit/capture-text-metrics.test.ts:12`, `:43` |
| AC-82.1 (2) | `expected undefined to be 2048`; `TypeError: mod.segoeAscentPx is not a function` (declared new) | pass | `capture-text-metrics.test.ts:22`, `:34` |
| AC-59.19 viewport (TA-4) | `AssertionError: expected 'hanging' to be 'alphabetic'` | pass | `ui/tests/unit/capture-page.behavior.test.ts:2017` |
| AC-82.4 | `AssertionError: expected '20' to be '38'` | pass | `capture-page.behavior.test.ts:889` |
| AC-82.6 | `expect(received).toBeLessThanOrEqual(expected)`, `Received: 8` (preview ink 8 px above the bake) | pass: ink 0 px on every side, plates ≤ 1 px | `ui/tests/e2e/capture-inbox.test.ts:1747` |
| AC-82.2, AC-82.5 (9) | green by design: they pin the existing bake (`9 passed` in row 2) | pass | `tests/unit/test_capture_text_metrics.py`, `tests/unit/test_capture_bake_fixture.py` |

Every Red and Green receipt and its decisive lines are in [walkthrough.md](../../../docs/execution/plans/2026-10-14-capture-render-fidelity/walkthrough.md) (§MEU-82 Red, §MEU-82 Green). 

### Commands Executed

```json
{"schema_version":"evidence.v1","check_id":"s36-82-red","command":"RECEIPTS_DIR=C:/Temp/av-kit pwsh: task.md row 2 command, verbatim","cwd":"P:/av-kit/.claude/worktrees/s36-capture-render-fidelity","scope":"MEU-82 Red: pin pytest (AC-82.2, AC-82.5), Vitest (AC-59.19 TA-3/TA-4, AC-82.1, AC-82.3, AC-82.4), build, Electron AC-82.6, red-check","phase":"red","exit_code":0,"result":"pass","tested_state":"HEAD 534beb1 baseline product code plus the row 2 tests and fixtures","output":"pin 9 passed | Vitest Tests 6 failed | 84 passed (90) | build OK | Electron 1 failed (AC-82.6, Received: 8) | red-check: 2 receipt(s), 0 problem(s)","fresh":true}
```

```json
{"schema_version":"evidence.v1","check_id":"s36-82-green","command":"RECEIPTS_DIR=C:/Temp/av-kit pwsh: task.md row 3 command, verbatim","cwd":"P:/av-kit/.claude/worktrees/s36-capture-render-fidelity","scope":"MEU-82 Green: Vitest (capture-text-metrics, capture-page.behavior, capture-page, capture-hit-test), pytest (text metrics, bake fixture, adapter), build, Electron capture-inbox","phase":"green","exit_code":0,"result":"pass","tested_state":"HEAD 534beb1 plus the MEU-82 product change","output":"Vitest Test Files 4 passed (4), Tests 130 passed (130) | pytest 26 passed | build OK | Electron 29 passed","fresh":true}
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
| `ui/src/renderer/src/features/capture/capture-segoe-metrics.ts` | modified | `SEGOE_UI_UNITS_PER_EM = 2048`, `SEGOE_UI_ASCENDER = 2210` (`SEGOE_UNITS`) |
| `ui/src/renderer/src/features/capture/capture-text-metrics.ts` | modified | `SVG_DOMINANT_BASELINE = 'alphabetic'`; `segoeAscentPx`; `svgTextBaselineY` |
| `ui/src/renderer/src/features/capture/CaptureViewport.tsx` | modified | text `y` from `svgTextBaselineY` (the arrow changes are MEU-83's) |
| `tools/capture_bake_fixture.py` | new | `TEXT_FIXTURE` writer (`--out DIR`); the bake helper MEU-83's tests reuse |
| `ui/tests/e2e/fixtures/capture-geometry.json` | new | `GEOMETRY_FIXTURE.segoe_ascent` (MEU-83 adds `arrows`) |
| `ui/tests/e2e/fixtures/capture-fidelity-original.png`, `capture-fidelity-annotated.png` | new | `TEXT_FIXTURE` PNGs, written by the tool |
| `ui/tests/unit/capture-text-metrics.test.ts` | modified | AC-82.1, AC-82.3, TA-3 |
| `ui/tests/unit/capture-page.behavior.test.ts` | modified | AC-82.4, TA-4 |
| `tests/unit/test_capture_text_metrics.py` | new | AC-82.2 |
| `tests/unit/test_capture_bake_fixture.py` | new | AC-82.5 |
| `ui/tests/e2e/capture-inbox.test.ts` | modified | AC-82.6 (`installFidelitySeam`, `fidelityBoxes`) |

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
  - id: D-22
    stage: execution
    question: "Row 0 failed at uv sync because the worktree venv was CPython 3.14 and spacy has no cp314 wheel; how is the environment fixed?"
    resolution: autonomous
    class: two-way
    chosen: "Recreate the worktree .venv with uv venv --clear --python 3.12.12 and re-run row 0 unchanged"
    source_tag: Local Canon
    precedents: ["uv.lock resolves for CPython 3.12.12", "walkthrough.md Execution message"]
    research: { engine: none, sources: [] }
    reasoning: "The lockfile already names the interpreter; recreating the venv changes no lockfile, pyproject or test. identity.py binds the python version, so the gate records it."
  - id: D-23
    stage: execution
    question: "red-check.py refused the coloured Vitest receipt (no failing-run summary); what changes under S3?"
    resolution: autonomous
    class: two-way
    chosen: "Strip ANSI CSI escapes before matching (ANSI_ESCAPE), add a positive and a negative selftest fixture, then re-prove Red"
    source_tag: Local Canon
    precedents: ["plan Stop Conditions S3 (fix the test setup only, then re-prove Red)"]
    research: { engine: none, sources: [] }
    reasoning: "The digit in the coloured summary follows an escape letter, so the word-boundary regex never matched. Stripping escapes loosens no rule; the negative fixture (a locator timeout) is still refused. Selftest 11 fixtures, 0 wrong."
  - id: D-24
    stage: execution
    question: "Playwright's element screenshot of a fractional-origin image box rounds outward and carries dark edge pixels; how does AC-82.6 read the ink?"
    resolution: autonomous
    class: two-way
    chosen: "The scan skips a ceil(2 x DPR) px ring; the mark is at least 20 px from every edge"
    source_tag: Local Canon
    precedents: ["walkthrough.md MEU-82 Red, test-setup correction 1"]
    research: { engine: none, sources: [] }
    reasoning: "This is a test-setup fix made before the formal Red run, so no assertion changed. Without it the ink box covered the whole frame on the dry run."
  - id: D-25
    stage: execution
    question: "The approved gate ran pytest with -x, which can never pass in a fresh worktree because two baseline packaging tests need the gitignored pack tree and ffmpeg; what does the gate do?"
    resolution: autonomous
    class: two-way
    chosen: "G-1: py-tests runs the whole suite with -rfE and passes pytest exit 1 only when every FAILED id is one of the two Baseline ids and nothing errors"
    source_tag: Local Canon
    precedents: ["implementation-plan.md Baseline rule (a test failing at baseline is never counted as a regression)", "Session 31 gui-polish-residuals validate-task pytest_env_ok subset rule"]
    research: { engine: none, sources: [] }
    reasoning: "It applies the plan's own baseline rule instead of a stricter one the plan did not intend. Building the 341 MB pack tree is out of scope, and copying the main checkout's build would pass without proving anything. Flagged for the execution review."
  - id: D-26
    stage: execution
    question: "Gate attempt 4 failed 5 Electron tests on gitignored prerequisites a fresh worktree lacks (the picker stub and the isolated primitive harness); what does the gate do?"
    resolution: autonomous
    class: two-way
    chosen: "G-2: add ui-harness-build and ui-picker-stub stages before ui-electron"
    source_tag: Local Canon
    precedents: ["Session 31 validate-task.ps1 ui-harness-build stage", ".agent/docs/cloud-local-collaboration.md section 3.1 item 3 (every E2E build artifact is a stage)", "capture-picker.test.ts error names build:picker-stub"]
    research: { engine: none, sources: [] }
    reasoning: "Both stages write only gitignored paths that identity.py does not hash. The five tests passed alone after the builds (5 passed). Flagged for the execution review."
```

---

## History

| Event | Date | Agent | Detail |
|-------|------|-------|--------|
| Created | 2026-10-16 | claude-code-local (Claude Opus 5.5) | Initial MEU-82 handoff after the row 8 gate and the H1-2 re-run |
