---
date: "2026-10-29"
review_mode: "plan"
target_plan: "docs/execution/plans/2026-10-29-capture-editor-repair/implementation-plan.md"
verdict: "approved"
findings_count: 0
template_version: "2.2"
requested_verbosity: "standard"
agent: "codex-independent-reviewer"
loop_id: "s43-plan-2026-10-29-capture-editor-repair"
round: 2
---

# Critical Review: capture-editor-repair

> **Current verdict: approved, round 2.** The original round 1 report is preserved below; the Recheck section records verified fixes and the current verdict.

> **Review Mode**: `plan`
> **Verdict**: `changes_required`

## Scope

**Intent anchor:** "Confirm the Session 43 plan gives the Capture editor Ctrl+Z / Ctrl+Y undo and redo on the canvas, eight-handle resize for box, highlight, pixelate and eraser marks, and text re-edit with corner scaling, with sound Red/Green proof before execution."

**Intent achieved:** partial. The requested features and staged proof are planned, but the focus predicate and transform boundary formulas need correction before execution.

**Target:** `docs/execution/plans/2026-10-29-capture-editor-repair/implementation-plan.md`, `docs/execution/plans/2026-10-29-capture-editor-repair/task.md`, and plan-local `session-gate.ps1`, `red-check.py`, `identity.py`.

**Review Type:** independent, read-only plan review, round 1.
**Checklist Applied:** PR-1 through PR-9, relevant IR/DR and §4A GUI checks; source-traced adversarial verification.
**Sources:** 09 §Residuals registered 2026-10-29, synthesis slices 1/2/3a, grouping §3, current Capture renderer, registry shortcuts and existing unit/Electron tests.
**Write destination:** `C:/Temp/av-kit/dispatch/s43-plan-review-r1.md`. The coordinator copies this report verbatim to `.agent/context/handoffs/2026-10-29-capture-editor-repair-plan-critical-review.md`.

No Critical finding. Three behavioral blockers and one non-blocking clerical finding follow. No repository file was edited, and no product suite, session gate, build or Electron process was run.

## Findings

| # | Severity | Blocking | Kind | Finding | File:Line | Recommendation | Status |
|---|----------|----------|------|---------|-----------|----------------|--------|
| F1 | High / High confidence | yes | behavior / deliverable | HISTORY_FOCUS delegates to annotationOwnsFocus(), which accepts toolbar buttons: it checks containment in capture-viewport and excludes only the confirm strip and COLOR_FOCUS_IDS. capture-undo is inside that viewport and is not excluded. With that button programmatically or keyboard focused, the proposed window handler therefore prevents Ctrl+Z and performs undo, contradicting AC-99.3(g), item 108 and D-164. Mouse clicks also already return focus to the surface. The specified implementation cannot pass its immutable Green expectation. **Violates: AC-99.** | docs/execution/plans/2026-10-29-capture-editor-repair/implementation-plan.md:129; docs/execution/plans/2026-10-29-capture-editor-repair/implementation-plan.md:162; docs/execution/plans/2026-10-29-capture-editor-repair/implementation-plan.md:481; ui/src/renderer/src/features/capture/CapturePage.tsx:95; ui/src/renderer/src/features/capture/CaptureViewport.tsx:785; ui/src/renderer/src/features/capture/CaptureViewport.tsx:790 | Resolve the history focus policy against 09:852, which permits noneditable Capture editor controls. Align AC-99.3(g), HISTORY_FOCUS and D-164 with that policy, or specify a separate explicit canvas-only predicate. Preserve the existing Delete/nudge focus contract. | open |
| F2 | High / High confidence | yes | behavior / deliverable | TEXT_SCALE first preserves the opposite plate corner, then independently clamps the corrected mark origin, undoing that preservation. Using the current Hi glyph metrics, text at (10,0), font_size 16 has plate (10,6,15,12). Dragging se to (40,30) requests font_size 32 and requires y=-6 to keep nw at (10,6). clampImagePoint changes y back to 0, so the returned plate starts at (10,12): the supposedly fixed corner moves 6 pixels. Larger scales produce larger jumps. This violates the fixed-corner contract underlying AC-101.1 and 09:882; the planned interior-only example misses it. **Violates: AC-101.** | docs/execution/plans/2026-10-29-capture-editor-repair/implementation-plan.md:140; docs/execution/plans/2026-10-29-capture-editor-repair/implementation-plan.md:259; ui/src/renderer/src/features/capture/capture-text-metrics.ts:40; ui/src/renderer/src/features/capture/capture-segoe-metrics.ts:47; ui/src/renderer/src/features/capture/capture-segoe-metrics.ts:80; ui/src/renderer/src/features/capture/capture-fit-map.ts:55 | Preserve the anchor-corrected origin where the existing signed-integer x/y schema permits it, rather than clamping it afterward. If origin bounds are required, define a feasible-size policy and reconcile it with the font-limit ACs. Add fixed expected coordinates for all four corners near image boundaries while retaining the 1..400 font bounds. | open |
| F3 | Medium / High confidence | yes | behavior / deliverable | TRANSFORM applies max(1, abs(R-L)) after choosing x=min(L,R), so collapsing a west handle onto the fixed east edge moves that fixed edge by one pixel. In a 100-pixel-wide image, a valid mark x=98,width=1 resized with w to x=99 returns x=99,width=1: its east edge becomes 100 instead of remaining 99, exceeding the plan's 0..W-1 bound. The equivalent north-handle defect affects height. AC-100.3 tests only the se collapse and therefore misses the asymmetric failure. **Violates: AC-100.** | docs/execution/plans/2026-10-29-capture-editor-repair/implementation-plan.md:134; docs/execution/plans/2026-10-29-capture-editor-repair/implementation-plan.md:195; docs/execution/plans/2026-10-29-capture-editor-repair/implementation-plan.md:207; docs/build-plan/09-screenshot-capture.md:866 | Apply the minimum extent to the moving edge relative to the stationary edge before normalizing, with an explicit coincident-edge policy. Add west/north collapse and last-pixel-boundary cases that assert both the stationary edge and image containment. | open |
| F4 | Low / High confidence | no | clerical / deliverable | Row 1 requires the census receipt to contain capture-page.behavior.test.ts:1505:, but that line is the no-title assertion; the hint assertion is at 1506 and neither generic line matches CENSUS_PATTERNS. The observed 284-line census contains TA-1's anchor and no TA-2 anchor, so the census-check command will reject the stated tree. TA-2's intended hint amendment itself is correct. | docs/execution/plans/2026-10-29-capture-editor-repair/task.md:41; docs/execution/plans/2026-10-29-capture-editor-repair/implementation-plan.md:141; docs/execution/plans/2026-10-29-capture-editor-repair/implementation-plan.md:142; ui/tests/unit/capture-page.behavior.test.ts:1505; ui/tests/unit/capture-page.behavior.test.ts:1506 | Include focusedHint or MEU65_TOOLBAR in the census and check TA-2 by stable assertion content instead of the stale line number. Correct the TA-2 line reference. | open |

### Boundary arithmetic behind F2 and F3

These are manual evaluations of the plan's formulas, using current source constants; they are not executed product tests.

F2: `textBackgroundBox({x:10,y:0,text:'Hi',font_size:16})` is `{x:10,y:6,width:15,height:12}`: H has glyph bounds `(0,7,11,18)`, i has `(0,6,4,18)` and starts after H's advance 11, with base size 16. The NW anchor is `(10,6)`. An SE pointer at `(40,30)` gives ratio 2 and font 32. Before translation the new plate is `(10,12,30,24)`; keeping the anchor requires mark origin `(10,-6)`. Clamping that origin yields `(10,0)`, hence NW `(10,12)`, a 6-pixel drift. This pointer and font size are otherwise valid.

F3: image width 100, original horizontal edges `L=98,R=99`, west handle at 99. The prescribed edges become `L=R=99`. Normalization followed by minimum width produces `x=99,width=1`, so the stationary east edge moves to 100, outside the stated `0..99` interval. A north handle has the same failure vertically.

## Checklist Results

### Information Retrieval (IR)

The AC tables have source labels, the BUILD_PLAN audit and H1/H2 outputs are present, and the named tools exist. New transform source/tests and implementation artifacts are explicitly scheduled. No implementation handoff or baseline exists yet; the implementation tasks remain unchecked.

TA-1 correctly updates the existing Electron Undo hint. TA-2 correctly preserves accessible names and changes only the generic hint expectation, subject to F4's stale reference/search anchor. The complete raw census is in `C:/Temp/av-kit/s43-review-census.txt`; it contains 284 lines and is not truncated on disk.

### Design / Documentation Review (DR)

The root-cause claims about missing canvas history chords, resize gestures and text re-edit match current source. Existing schemas accept positive integer fonts, while `FONT_SCRUB_MAX=400` supplies the approved scaling ceiling. Box handle coordinates and the SVG view transform use the same image-space geometry; fixed CSS size is implemented by dividing by view scale.

The preserved body-handle-before-resize ordering is compatible with the inspected AC-60 move and arrow-end cases and region move assertions. The draft replacement/no-op/empty/Escape rules preserve text-only edits and history in design. F1 corrects the false claim that `annotationOwnsFocus` excludes toolbar controls. F2/F3 require boundary oracles beyond the current interior/SE examples.

For keyboard interception, existing AC-66.13 exercises real zoom chords and checks the page zoom factor. The [Electron before-input-event documentation](https://www.electronjs.org/docs/latest/api/web-contents#event-before-input-event) documents main-process cancellation; it does not independently establish DOM renderer cancellation for Edit roles. The [default-menu documentation](https://www.electronjs.org/docs/latest/api/menu#default-menu) confirms the automatic menu. Extrapolating the local zoom result to undo/redo is an inference reserved for AC-99.7 and S4. This review makes no fresh Electron claim.

### Plan Review (PR) and §4A

- PR-1/PR-4: the specified history implementation and guard test disagree (F1); the transform formulas violate boundary invariants (F2/F3).
- PR-2/PR-3/PR-5/PR-6/PR-7: unstarted state, row ownership/dependencies, sources, handoff destinations and scoped exclusions are present.
- PR-8: the entrypoints and observables are real; the boundary negatives need strengthening as in F2/F3. Helper fixtures passing do not certify future product behavior.
- PR-9: no additional materially ambiguous repeated contract was found.
- Product scope tables and the session-gate allow-list agree. S1-S8 and decision/hub/state order are consistent apart from the focus-policy contradiction. Row 9 precedes the H1-2 input identity; H2 rechecks the suites reading approval state.
- §4A: all five GUI reference indexes are absent as the plan records. The element matrix names the changed hints, surface, draft and handles, registers additive handle IDs, and supplies planned Electron behavior assertions. No missing-index or process-paperwork blocker is raised.
- Red/Green: baseline, row3 and row5 source boundaries preserve dependency order. Dynamic imports/existence/type assertions and presence assertions are designed to yield assertion diagnostics. The checker refuses setup/action timeouts and unrelated errors. No future Red/Green outcome is represented as observed here.

### Commands and durable observations

Commands ran from `P:/av-kit`, redirected all streams under `C:/Temp/av-kit`, and preserved exits before reading receipts. Both helper self-tests used TEMP/TMP under the allowed directory and disabled bytecode. The initial `uv run` lint invocation failed with exit 2 because `C:/Users/Mat/AppData/Local/uv/cache/sdists-v9/.git` was inaccessible; the allowed linter succeeded through `.venv/Scripts/python.exe` with the required RECEIPTS_DIR. This is a reviewer-environment limitation, not a plan defect.

```json
{"schema_version": "evidence.v1", "check_id": "s43-review-1", "command": "rtk proxy python -B -X utf8 docs/execution/plans/2026-10-29-capture-editor-repair/red-check.py --selftest", "cwd": "P:/av-kit", "scope": "Red checker self-test", "phase": "static", "exit_code": 0, "result": "pass", "tested_state": "unstarted Session 43 plan; source review only", "output": "red-check selftest: 36 fixture(s) (11 positive, 25 negative), 0 wrong: []", "fresh": true}
```

```json
{"schema_version": "evidence.v1", "check_id": "s43-review-2", "command": "rtk proxy python -B -X utf8 docs/execution/plans/2026-10-29-capture-editor-repair/identity.py --selftest", "cwd": "P:/av-kit", "scope": "Identity helper self-test", "phase": "static", "exit_code": 0, "result": "pass", "tested_state": "unstarted Session 43 plan; source review only", "output": "identity selftest: 0 failure(s)", "fresh": true}
```

```json
{"schema_version": "evidence.v1", "check_id": "s43-review-3", "command": "rtk proxy .venv/Scripts/python.exe -B tools/lint_task_contract.py --allowed-builder-classes avkit_builder,avkit_coordinator,avkit_verifier --task docs/execution/plans/2026-10-29-capture-editor-repair/task.md", "cwd": "P:/av-kit", "scope": "Task contract lint", "phase": "static", "exit_code": 0, "result": "pass", "tested_state": "unstarted Session 43 plan; source review only", "output": "OK: 26 row(s); 24 fully checked; 2 view_file exemptions; dependencies resolve and are acyclic. Initial uv invocation exited 2 because the user cache was inaccessible; direct repository Python succeeded.", "fresh": true}
```

```json
{"schema_version": "evidence.v1", "check_id": "s43-review-4", "procedure": "Read task states, inspect main's git status, check baseline/handoff absence and inspect referenced scripts and targeted test files against the Files Modified inventory.", "observer": "codex-independent-reviewer", "cwd": "P:/av-kit", "scope": "Unstarted plan and referenced paths", "phase": "manual", "exit_code": null, "result": "pass", "tested_state": "unstarted Session 43 plan; source review only", "output": "Implementation rows remain unchecked; baseline.sha and the three implementation handoffs are absent. Named tools exist; capture-transform.ts and capture-transform.test.ts are explicitly scheduled new files. Given planning edits and squashed-history constraints were accepted.", "fresh": true}
```

```json
{"schema_version": "evidence.v1", "check_id": "s43-review-5", "procedure": "Trace focus from capture-viewport through annotationOwnsFocus and the window listener; evaluate the specified transform formulas against textBackgroundBox glyph metrics and image clamp; compare ACs with baseline/row3/row5 ordering.", "observer": "codex-independent-reviewer", "cwd": "P:/av-kit", "scope": "Source contracts and Red/Green feasibility", "phase": "manual", "exit_code": null, "result": "fail", "tested_state": "unstarted Session 43 plan; source review only", "output": "F1-F3 identify source-traced behavioral contradictions. Red module/presence assertions, staged renderer snapshots and observable saved-body checks are otherwise sound in design. Product tests were not run.", "fresh": true}
```

```json
{"schema_version": "evidence.v1", "check_id": "s43-review-6", "procedure": "Run the plan's complete literal CENSUS_PATTERNS search over ui/tests, tests and mcp-server/tests; inspect the untruncated receipt and TA-1/TA-2 assertions.", "observer": "codex-independent-reviewer", "cwd": "P:/av-kit", "scope": "Amendments and census", "phase": "manual", "exit_code": null, "result": "fail", "tested_state": "unstarted Session 43 plan; source review only", "output": "284 census lines. TA-1's Undo hint and TA-2's generic hint expectation require the documented amendments; accessible names remain unchanged. F4: TA-2's required census anchor is absent. Reviewed move/endpoint and region-move tests remain compatible with the proposed handle order.", "fresh": true}
```

```json
{"schema_version": "evidence.v1", "check_id": "s43-review-7", "procedure": "Compare plan/task inventories, scope-paths allow-list, S1-S8, decision log and H1/H2 ordering; inspect GUI element matrix, test IDs and existing toolbar/surface structure.", "observer": "codex-independent-reviewer", "cwd": "P:/av-kit", "scope": "Scope, stop conditions, hub writes and GUI compliance", "phase": "manual", "exit_code": null, "result": "pass", "tested_state": "unstarted Session 43 plan; source review only", "output": "Allowed product/test/hub paths agree; bound hub writes precede H1-2, and approval writes recheck state-canon suites. Missing GUI reference indexes are correctly recorded as gui-refs-not-shipped; changed interactive elements have planned Electron assertions. No scope or paperwork blocker added.", "fresh": true}
```

```json
{"schema_version": "evidence.v1", "check_id": "s43-review-8", "procedure": "Inspect AC-66.13 and keyboard propagation, then compare the cited official Electron menu and before-input-event documentation.", "observer": "codex-independent-reviewer", "cwd": "P:/av-kit", "scope": "Electron menu interception claim", "phase": "manual", "exit_code": null, "result": "not_run", "reason": "Runtime interception remains unmeasured; source evidence supports only the documented inference.", "tested_state": "unstarted Session 43 plan; source review only", "output": "AC-66.13 uses real page.keyboard zoom chords and checks pageZoomFactor=1. Applying this precedent to undo/redo remains an inference; AC-99.7 and S4 provide the required future measurement. The documented before-input-event preventDefault is a main-process API, not proof about renderer DOM cancellation: [Electron documentation](https://www.electronjs.org/docs/latest/api/web-contents#event-before-input-event). No unsupported assertion that undo interception has already been measured.", "fresh": true}
```

```json
{"schema_version": "evidence.v1", "check_id": "s43-review-9", "procedure": "Not run per dispatch", "observer": "codex-independent-reviewer", "cwd": "P:/av-kit", "scope": "Product suites, session gate, builds and Electron execution", "phase": "manual", "exit_code": null, "result": "not_run", "reason": "Product execution is prohibited by the review dispatch.", "tested_state": "unstarted Session 43 plan; source review only", "output": "Not run, as explicitly prohibited for this read-only plan review. Findings derive from source and plan formulas, not a claimed product execution.", "fresh": true}
```

## Verdict

`changes_required` — resolve F1-F3 through `/plan-corrections` before execution. F4 is non-blocking but should be corrected in the same pass. Preserve the original AC intent and add concrete edge-boundary expectations; do not weaken assertions to make the current formulas pass.

**Residual risk:** renderer Edit-role interception and actual Electron drag/re-edit behavior remain unmeasured in this plan-only review, as required by the dispatch. The planned runtime checks and S4 remain necessary.

**Completion preflight:** the assigned review is complete and the report is the only requested handoff. Product task rows remain unstarted; no implementation or H2 closeout is claimed.



## Recheck (2026-10-29) -- Round 2

**Workflow:** `/plan-critical-review`, independent read-only recheck.
**Agent:** `codex-independent-reviewer`.
**Loop:** `s43-plan-2026-10-29-capture-editor-repair`.
**Target:** `docs/execution/plans/2026-10-29-capture-editor-repair/implementation-plan.md`, `task.md`, and their plan-local tooling.
**Intent anchor:** "Confirm the Session 43 plan gives the Capture editor Ctrl+Z / Ctrl+Y undo and redo on the canvas, eight-handle resize for box, highlight, pixelate and eraser marks, and text re-edit with corner scaling, with sound Red/Green proof before execution."
**Intent achieved:** yes, as an execution plan. No implementation or runtime success is claimed.

### Findings

| # | Severity | Blocking | Kind | Finding | File:Line | Recommendation | Status |
|---|----------|----------|------|---------|-----------|----------------|--------|

No remaining blocking finding. The four prior findings are closed by the source-traced checks below. This recheck concentrates on the corrected clauses and their consequences; it does not repeat the unchanged round 1 survey.

### Prior Pass Summary

| Finding | Prior status | Evidence | Recheck result |
|---|---|---|---|
| F1 | open | Plan `:108`, `:129`, `:162`, `:481` now consistently permit history on Capture toolbar buttons and exclude `COLOR_FOCUS_IDS`; source `CapturePage.tsx:83`, `:95`, `:104`, `:107` and 09 `:852` agree. | fixed |
| F2 | open | Plan `:140`, `:252`, `:259`, `:537` preserve signed anchor-corrected origins. The exact Hi oracle follows `capture-text-metrics.ts:40` and glyph metrics `capture-segoe-metrics.ts:47`, `:80`; the schemas accept the negative y. | fixed |
| F3 | open | Plan `:109`, `:134`, `:207`, `:497` apply minimum extent to the moving edge before normalization. The west/north boundary cases retain edge 99; east/south cases retain edge 0. | fixed |
| F4 | open, non-blocking | Plan `:113`, `:141`, `:142` and task `:41` now name the actual hint assertion and search its content. The fresh complete census contains both amendment anchors. | fixed |

### Confirmed Fixes

- **F1 — focus and one command owner.** `annotationOwnsFocus()` accepts a focused toolbar button inside the viewport, excludes the confirm strip and the named colour control, and remains unchanged for Delete/nudge (`ui/src/renderer/src/features/capture/CapturePage.tsx:95`). The revised positive `capture-undo` case and negative `capture-named-color` case agree with 09 Focus (`docs/build-plan/09-screenshot-capture.md:852`). Surface keydown calls the page handler and stops non-registry propagation (`CaptureViewport.tsx:1112`); body/toolbar events use the existing window listener (`CapturePage.tsx:1044`). Reserved history chords cannot simultaneously become registry commands (`ui/src/renderer/src/registry/shortcuts.ts:130`). Editable-field, draft, composition, recording, confirm and modal guards remain in the design.
- **F2 — signed text origin preserves the opposite plate corner.** Current Hi metrics at size 16 give plate `(10,6,15,12)` for origin `(10,0)`. Scaling SE to `(40,30)` gives size 32; the unshifted plate is `(10,12,30,24)`, so origin `(10,-6)` restores plate `(10,6,30,24)`. This is the revised exact AC-101.1 oracle (`implementation-plan.md:259`). Domain `_require_int` has no nonnegative coordinate rule (`packages/core/src/avkit_core/domain/capture.py:199`, `:207`); API x/y are ints (`packages/api/src/avkit_api/schemas/captures.py:100`); zod uses `.int()` (`ui/src/renderer/src/features/capture/capture-annotate.ts:49`). The per-corner near-edge checks preserve the same invariant. Font bounds 1..400 match the positive-int renderer schema and `FONT_SCRUB_MAX` (`capture-annotate.ts:53`, `capture-scrub.ts:8`).
- **F3 — minimum size no longer shifts the stationary edge.** With horizontal edges 98 and 99, a west drag to 99 moves the west edge back to 98 before normalization, yielding `(98,1)` with stationary east edge 99. The north case is symmetric. For east/south collapse at stationary edge 0, the moving edge becomes 1. The opposite-side fallback handles a coincident moving edge at the upper bound. These calculations use the actual drawing interval (`ui/src/renderer/src/features/capture/capture-fit-map.ts:55`) and match the revised fixed numeric cases (`implementation-plan.md:207`). Crossed edges normalize with min/absolute difference, without changing other mark fields.
- **F4 — census reaches TA-2.** The current hint comparison is at `ui/tests/unit/capture-page.behavior.test.ts:1506`; its accessible-name assertion remains at `:1503`. The corrected row 1 searches `focusedHint` and `MEU65_TOOLBAR`, then checks `focusedHint(toolbarFocusTarget` instead of an incidental line number (`task.md:41`). Fresh census: 299 lines, including TA-1 at `ui/tests/e2e/capture-inbox.test.ts:1680` and TA-2 at `ui/tests/unit/capture-page.behavior.test.ts:1506`. The raw receipt is complete on disk.

### Checklist Results

#### Information Retrieval (IR)

Source labels, named new files, the BUILD_PLAN audit and H1/H2 deliverables remain present. Implementation rows are unchecked; this is still a plan review. The revised ACs remain within grouping Session 43 (`.agent/context/grouping/2026-10-29-capture-annotation-editor-session-grouping.md:66`) and 09 residuals (`docs/build-plan/09-screenshot-capture.md:845`, `:859`, `:874`).

#### Design Review (DR)

The corrected transforms satisfy the round 1 counterexamples. The hit order preserves the existing centre/body and arrow-end handling before the added resize branch (`implementation-plan.md:135`; `capture-hit-test.ts:176`). Painted preview substitution and image-space handle points use the same view mapping (`CapturePage.tsx:1300`; `CaptureViewport.tsx:502`, `:1273`). Re-edit still replaces only text, hides the original while drafting, and avoids history for unchanged/empty/cancelled edits (`implementation-plan.md:139`, `:260`, `:261`). No new contradiction introduced by the four corrections was found that prevents the stated features.

#### Plan Review (PR) and GUI section 4A

- The Red trees remain baseline, row3-ui-src.json and row5-ui-src.json respectively (`task.md:43`, `:46`, `:49`). Existence/type/presence assertions precede missing-module calls and new-element actions. `--require` checks assertion-only diagnostics for each required failing AC (`red-check.py:261`). Future actual Red and Green runs are still necessary; helper self-tests do not prove product behavior.
- The revised toolbar guard makes one AC-99.3 subcase fail on the baseline, so the old prose that the baseline satisfies that entire guard set by doing nothing (`implementation-plan.md:354`) is stale. This does not make row 2 unrunnable: AC-99.3 is not required to pass or required to fail, and its expected assertion failure is accepted by the checker. It is not a blocker.
- The unchanged product allow-list and hub ordering agree between the plan, task and `session-gate.ps1:28`. Row 9 precedes H1-2's final full identity; H2 rechecks the suites reading approval state (`task.md:53`, `:56`, `:69`). S4 still requires a human decision if Electron routing disproves the renderer design (`implementation-plan.md:430`).
- Section 4A retains the changed-element inventory, additive handle IDs, constant CSS handle size, viewport cursor checks and real Electron assertions (`implementation-plan.md:409`). The absent GUI reference indexes remain the recorded given state. No new GUI compliance blocker arose from these corrections.
- Task-contract lint passes. Execution prerequisites remain live checks: this review environment's git status warns that the global ignore file is inaccessible and exposes `.claude/settings.local.json` outside PREREQS. Row 0 must evaluate its own actual status and stop under S1 if that path is still exposed; this review neither modifies it nor grants an exception.

### Observed evidence

All commands ran from `P:/av-kit`. Receipts and reviewer artifacts were written only under `C:/Temp/av-kit`. The helper self-tests used TEMP/TMP there and disabled Python bytecode. No pytest, Vitest, session gate, build or Electron process was run.

```json
{"schema_version":"evidence.v1","check_id":"s43-r2-red-selftest","command":"rtk proxy python -B -X utf8 docs/execution/plans/2026-10-29-capture-editor-repair/red-check.py --selftest","cwd":"P:/av-kit","scope":"plan-local Red checker fixtures","phase":"static","exit_code":0,"result":"pass","tested_state":"Session 43 unstarted plan, round 2 source review","output":"red-check selftest: 36 fixture(s) (11 positive, 25 negative), 0 wrong: []","fresh":true}
```

```json
{"schema_version":"evidence.v1","check_id":"s43-r2-identity-selftest","command":"rtk proxy python -B -X utf8 docs/execution/plans/2026-10-29-capture-editor-repair/identity.py --selftest","cwd":"P:/av-kit","scope":"plan-local input identity fixtures","phase":"static","exit_code":0,"result":"pass","tested_state":"Session 43 unstarted plan, round 2 source review","output":"Bound input mutations changed state; listed closeout artifacts preserved state; identity selftest: 0 failure(s)","fresh":true}
```

```json
{"schema_version":"evidence.v1","check_id":"s43-r2-task-lint","command":"rtk proxy .venv/Scripts/python.exe -B tools/lint_task_contract.py --allowed-builder-classes avkit_builder,avkit_coordinator,avkit_verifier --task docs/execution/plans/2026-10-29-capture-editor-repair/task.md","cwd":"P:/av-kit","scope":"Session 43 task contract; RECEIPTS_DIR=C:/Temp/av-kit","phase":"static","exit_code":0,"result":"pass","tested_state":"Session 43 unstarted plan, round 2 source review","output":"OK: 26 row(s); 10-column table (with builder_model); 24 row(s) fully checked; dependencies resolve and are acyclic; 2 view_file exemptions: H1-5, H2-1","fresh":true}
```

```json
{"schema_version":"evidence.v1","check_id":"s43-r2-corrections","procedure":"Compare corrected focus clauses against annotationOwnsFocus and viewport/window event routing; evaluate the revised text anchor and moving-edge formulas using current source metrics and schemas; inspect task row 1 and run the complete literal CENSUS_PATTERNS search over ui/tests, tests and mcp-server/tests.","observer":"codex-independent-reviewer","cwd":"P:/av-kit","scope":"round 1 F1-F4 and affected Red/Green contracts","phase":"manual","exit_code":null,"result":"pass","tested_state":"Session 43 unstarted plan, round 2 source review","output":"F1-F4 fixed. Census has 299 lines and both TA anchors. Hi origin (10,0) scales to (10,-6), size 32, preserving NW plate (10,6). West/north collapse retains stationary edge 99; east/south collapse retains stationary edge 0. No remaining blocking finding.","fresh":true}
```

### Remaining Findings

None blocking. Electron Edit-role interception remains an execution measurement, not an observed fact from this review. AC-66.13 is a zoom precedent (`ui/tests/e2e/capture-inbox.test.ts:1111`); it does not independently prove undo/redo. [Electron's default-menu documentation](https://www.electronjs.org/docs/latest/api/menu#default-menu) confirms automatic menu creation, while [before-input-event](https://www.electronjs.org/docs/latest/api/web-contents#event-before-input-event) documents main-process cancellation rather than a guarantee for DOM keydown cancellation. Applying the zoom precedent to Edit roles remains an inference, gated by AC-99.7 and S4. No fresh runtime claim is made.

### Verdict

`approved` — all round 1 blockers are fixed, and the corrected plan provides the requested Session 43 behavior with staged Red/Green proof and an explicit stop if Electron routing fails measurement.

**Completion preflight:** applied to the assigned read-only review. The report is the requested deliverable; the product task rows remain unstarted. No repository file was created, edited or deleted, and no product/H2 completion is claimed.
