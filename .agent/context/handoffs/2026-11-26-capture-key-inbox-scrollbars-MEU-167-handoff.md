---
date: "2026-11-27"
project: "2026-11-26-capture-key-inbox-scrollbars"
meu: "MEU-167"
status: "complete"
action_required: "VALIDATE_AND_APPROVE"
template_version: "2.2"
verbosity: "standard"
plan_source: "docs/execution/plans/2026-11-26-capture-key-inbox-scrollbars/implementation-plan.md"
build_plan_section: "docs/build-plan/09-screenshot-capture.md §Viewport scroll bars (MEU-167, matrix 9.50)"
agent: "claude-code-local (Claude Opus 5.5)"
reviewer: "codex (H1-7 execution review)"
predecessor: "2026-11-26-capture-key-inbox-scrollbars-MEU-166-handoff.md"
---

# Handoff: 2026-11-26-capture-key-inbox-scrollbars-MEU-167-handoff

> **Status**: `complete`
> **Action Required**: `VALIDATE_AND_APPROVE`

---

## Scope

**MEU**: MEU-167 Viewport scroll bars (phase 9, matrix 9.50), from `CAPTURE-ZOOM-NO-SCROLLBARS` (triage D-1402), grouped as Session 103 with MEU-165 and MEU-166. This handoff is the last of three: [MEU-165](2026-11-26-capture-key-inbox-scrollbars-MEU-165-handoff.md) → [MEU-166](2026-11-26-capture-key-inbox-scrollbars-MEU-166-handoff.md) → MEU-167. The shared records, the session-wide departures and the full gate table are in the MEU-165 handoff.
**Build Plan Section**: `docs/build-plan/09-screenshot-capture.md` §Viewport scroll bars, with its `Delivered (Session 103)` note (row 11).
**Predecessor**: [2026-11-26-capture-key-inbox-scrollbars-MEU-166-handoff.md](2026-11-26-capture-key-inbox-scrollbars-MEU-166-handoff.md). Session 103 ran from `e5028a3` (`baseline.sha`), and `HEAD` did not move.

- **Geometry (`SCROLL_BAR_GEOMETRY`).** New pure module `ui/src/renderer/src/features/capture/capture-scroll-bars.ts` gives, per axis, whether the bar shows, the track length, the thumb length and offset, the value 0 to 100, and the pan change for a thumb drag. A bar shows when the view is zoomed (`scale`) and the image is longer than the frame on that axis; the bar is 10 px thick (`SCROLL_BAR_THICKNESS`), and the thumb is the visible share of the track, at least 24 px (`SCROLL_THUMB_MIN`).
- **Overlay (`SCROLL_BAR_OVERLAY`, D-1426).** The bars are absolutely positioned children of the viewport surface in `CaptureViewport.tsx`, drawn from the view transform; the frame stays `overflow-hidden` and `capture-fit-map.ts` does not change. The test ids `capture-scrollbar-x`, `capture-scrollbar-y`, `capture-scrollbar-x-thumb` and `capture-scrollbar-y-thumb` are a new `// MEU-167 viewport scroll bar IDs.` block at the end of `ui/tests/e2e/test-ids.ts`.
- **Drag (`SCROLL_BAR_DRAG`, D-1427).** Only a thumb takes pointer input; its drag pans through the existing clamped `panBy` and never reaches the draw surface, so it makes no mark, history entry or colour sample. No track click, keyboard control or wheel scrolling (D-1427).
- **Look (`SCROLL_BAR_LOOK`, D-1427).** Theme tokens only (a `--color-fg-muted` thumb with a 1 px `--color-bg` edge on a transparent track), no geometry transition, and the `scrollbar` role with `aria-orientation`, `aria-valuemin` 0, `aria-valuemax` 100, `aria-valuenow`, `aria-controls` and the names "Horizontal scroll" and "Vertical scroll"; a bar is not a tab stop.
- **Records.** MEU-167 is `ready_for_review`; 09 §Viewport scroll bars carries the Delivered note, and the Pan gestures row of §Viewport zoom no longer says "with no scrollbars".

**What Mat sees.** When a shot is zoomed in past the viewport, thin scroll bars show along the bottom and the right edge of the Capture viewport, and their thumbs show where the visible part is. Dragging a thumb moves the image. When the image fits, the bars are gone.

**Plan:** [implementation-plan.md](../../../docs/execution/plans/2026-11-26-capture-key-inbox-scrollbars/implementation-plan.md) §Single-statement contracts. **Execution authorization:** `USER_EXPLICIT`, 2026-11-26 ("drafts stand, go for 104 after the reviews finish and then execute rest as you see fit. Use HDP for decisions and pick recommendations as expect and do not stop for human decisions on techincal metters that are settled as primary recommendation for any of the 4 executions."). The plan review approved at round 2 of loop `cki-plan-2026-11-26-capture-key-inbox-scrollbars`. Receipts named by file name alone are in the session's receipts folder (the `2026-11-26-capture-key-inbox-scrollbars` folder under `RECEIPTS_DIR`).

---

## Acceptance Criteria

| AC | Type | Description | Source | Test(s) | Status |
|----|------|-------------|--------|---------|--------|
| AC-167.1 | unit | For `C` 400, `K` 1600, `T` 400 the thumb is 100 long; at pan offset 0 it sits at 0, at `C - K` at `T - thumb`, half-way in the middle; the value runs 0 to 100. For `K` 40000 the thumb is `SCROLL_THUMB_MIN`; the thumb is never longer than the track | Spec (09 §Viewport scroll bars: Bars); `SCROLL_BAR_GEOMETRY`; Research-backed | `ui/tests/unit/capture-scroll-bars.test.ts:39`, `:51`, `:58` | ✅ |
| AC-167.2 | unit | In `fit` neither bar shows; in `scale` with `K` at most `C` neither shows; with one axis larger only that bar shows, on the full frame length; with both larger both show and each track is shorter by `SCROLL_BAR_THICKNESS` | Spec (Bars) | `ui/tests/unit/capture-scroll-bars.test.ts:84`, `:90`, `:103` | ✅ |
| AC-167.3 | unit | A thumb drag of `d` px gives a pan change of `-d * (K - C) / (T - thumb)`; a drag of the whole free track reaches the end exactly; after the clamp the offset stays within `C - K` to 0, over a table of cases; a thumb as long as the track gives 0 | Spec (Move); `SCROLL_BAR_GEOMETRY` | `ui/tests/unit/capture-scroll-bars.test.ts:111`, `:123`, `:163` | ✅ |
| AC-167.4 | unit | Zoomed past the frame, both bars and thumbs exist under their test ids with `role="scrollbar"`, `aria-orientation`, `aria-valuemin` 0, `aria-valuemax` 100, an integer `aria-valuenow` equal to the geometry, `aria-controls` and a name; neither is a tab stop; at Fit no bar is in the document | Research-backed (WAI-ARIA `scrollbar`); `SCROLL_BAR_LOOK` | `ui/tests/unit/capture-scroll-bars.behavior.test.ts:241`, `:273` | ✅ |
| AC-167.5 | unit | A `userEvent` drag of the vertical thumb by 30 px moves the view by the geometry's amount on that axis only, and adds no mark, history entry or colour sample | Spec (Move); `SCROLL_BAR_DRAG` | `ui/tests/unit/capture-scroll-bars.behavior.test.ts:285` | ✅ |
| AC-167.6 | unit | A source scan: no hex or `rgb(` colour and no transition class in the bars; the track is `pointer-events-none` and the thumb takes pointer events; the frame keeps `overflow-hidden`; `capture-fit-map.ts` is byte-identical to the baseline | Local Canon (G32, G33); Spec (Look; Replaces) | `ui/tests/unit/capture-scroll-bars.behavior.test.ts:309` | ✅ |
| AC-167.7 | integration | Electron on mini-air, `AC-167.7 scroll bars show the view and a thumb drag moves it`: on a zoomed shot both bars show with thumb lengths within 1 px; a 40 px vertical drag moves the image by the geometry's amount and leaves the horizontal offset; a drag far past the end stops at `aria-valuenow` 100; after Fit both bars are gone | Spec (Tests row); grouping acceptance direction | `ui/tests/e2e/capture-inbox.test.ts:3734`; Red run `r20261127T161201Z-091957d`, Green run `r20261127T170013Z-02ecd38` | ✅ |
| AC-167.8 | integration | Electron on mini-air, `AC-167.8 the scroll bar thumb is seen in both themes`: in the dark and the light theme the contrast of the thumb's fill against its edge, read as sRGB bytes through a 1 by 1 canvas, is at least 3 | Local Canon (G32); Research-backed (WCAG 2.1 SC 1.4.11) | `ui/tests/e2e/capture-inbox.test.ts:3796`; the same runs | ✅ |
| AC-165 (cross-ref) | sibling | This plan's AC-165 criteria belong to MEU-165; that handoff carries their Red and Green evidence, and this handoff claims none of them | the plan | see the MEU-165 handoff | cross-ref |
| AC-166 (cross-ref) | sibling | This plan's AC-166 criteria belong to MEU-166; that handoff carries their Red and Green evidence, and this handoff claims none of them | the plan | see the MEU-166 handoff | cross-ref |
| AC-39 (cross-ref) | named change | AC-39.13's token-form change (D-1422) belongs to MEU-165; not a criterion of MEU-167 | the plan; D-1422 | see the MEU-165 handoff | cross-ref |
| AC-61 (cross-ref) | named change | AC-61.16's token-form change (D-1422) belongs to MEU-165; not a criterion of MEU-167 | the plan; D-1422 | see the MEU-165 handoff | cross-ref |
| AC-57 (cross-ref) | pin | §Test pins: the Capture page behaviour pins (AC-57.2, AC-57.3, AC-57.9) are unchanged and pass | Local Canon | gate `guards`, `ui-tests` | ✅ |
| AC-162 (cross-ref) | pin | §Test pins: the quick-start pins are unchanged and pass | Local Canon | gate `guards`, `ui-tests` | ✅ |
| AC-7 (cross-ref) | pin | §Test pins: the E2E pointer helpers are unchanged; AC-167.8 uses them as they are | Local Canon | gate `guards` | ✅ |
| AC-93 (cross-ref) | pin | §Test pins: the block order of `test-ids.ts` (AC-93.6) is unchanged; the scroll-bar ids are a new block at the end | Local Canon | gate `guards` | ✅ |
| AC-96 (cross-ref) | pin | §Test pins: AC-96.11 on the same block order is unchanged | Local Canon | gate `guards` | ✅ |
| AC-151 (cross-ref) | pin | §Test pins: AC-151.14 keeps its lines | Local Canon | gate `guards` | ✅ |

<!-- CACHE BOUNDARY -->

---

## Evidence

### FAIL_TO_PASS

Red is row 8 (`cki-row8-red.txt`: `Tests  13 failed (13)`; `cki-row8-red-check.txt`: `6 required test(s), 0 problem(s)`), Green row 9 (`cki-row9-green.txt`: `Tests  13 passed (13)`). The Electron tests failed at row 1 and passed at row 10.

| Test | Red Output (hash/snippet) | Green Output | File:Line |
|------|---------------------------|--------------|-----------|
| AC-167.1 to AC-167.3 (9 tests) | `capture-scroll-bars.ts exists: expected undefined to be type of 'function'` | Row 9: `Tests  13 passed (13)` | `ui/tests/unit/capture-scroll-bars.test.ts:39` to `:163` |
| AC-167.4 | `capture-scrollbar-x rendered: expected null not to be null` | Row 9 | `ui/tests/unit/capture-scroll-bars.behavior.test.ts:241`, `:273` |
| AC-167.5 | `capture-scrollbar-y-thumb rendered` | Row 9 | `ui/tests/unit/capture-scroll-bars.behavior.test.ts:285` |
| AC-167.6 | `capture-scroll-bars.ts exists: expected false to be true` | Row 9 | `ui/tests/unit/capture-scroll-bars.behavior.test.ts:309` |
| AC-167.7, AC-167.8 | Row 1 run `r20261127T161201Z-091957d`: two of the 4 new failures, on an expectation (`cki-run-1.txt`: `result: new-failures exit=40`) | Row 10 run `r20261127T170013Z-02ecd38`: `summary: tests=260 expected=260 unexpected=0` | `ui/tests/e2e/capture-inbox.test.ts:3734`, `:3796` |

Row 9's first Green run failed on a `-0` pan against `0`; the module's share now goes through `Math.max`, which turns `-0` into `+0` (`capture-scroll-bars.ts:23`), and the row passed.

### Commands Executed

```json
{"schema_version": "evidence.v1", "cwd": "P:/av-kit", "check_id": "cki-8-9-scroll-bars", "command": "pwsh -NoProfile -File C:/Temp/av-kit/2026-11-26-capture-key-inbox-scrollbars/run-row.ps1 8, then 9; receipts C:/Temp/av-kit/2026-11-26-capture-key-inbox-scrollbars/cki-row8*.txt, cki-row9*.txt", "scope": "AC-167.1 to AC-167.6 Red then Green", "phase": "green", "exit_code": 0, "result": "pass", "tested_state": "HEAD e5028a3 (baseline.sha) plus rows 0 to 9", "output": "cki-row8-red.txt: Tests  13 failed (13). cki-row8-red-check.txt: 6 required test(s), 0 problem(s). cki-row9-green.txt: Tests  13 passed (13)"}
```

```json
{"schema_version": "evidence.v1", "cwd": "P:/av-kit", "check_id": "cki-1-10-e2e", "command": "pwsh -NoProfile -File C:/Temp/av-kit/2026-11-26-capture-key-inbox-scrollbars/run-row.ps1 1, then 10; receipts C:/Temp/av-kit/2026-11-26-capture-key-inbox-scrollbars/cki-run-1.txt, cki-run-10.txt, cki-row10-remote-ok.txt", "scope": "AC-167.7 and AC-167.8 Red at row 1 and Green at row 10 on mini-air", "phase": "runtime", "exit_code": 0, "result": "pass", "tested_state": "HEAD e5028a3 (baseline.sha) plus rows 0 to 10", "output": "cki-run-1.txt: summary: tests=260 expected=256 unexpected=4; result: new-failures exit=40. cki-run-10.txt: summary: tests=260 expected=260 unexpected=0 flaky=0 skipped=0 spec_files=34; result: ok exit=0. cki-row10-remote-ok.txt: remote-ok: run r20261127T170013Z-02ecd38; tests 260; 0 problem(s)"}
```

```json
{"schema_version": "evidence.v1", "cwd": "P:/av-kit", "check_id": "cki-11-canon-register", "command": "pwsh -NoProfile -File C:/Temp/av-kit/2026-11-26-capture-key-inbox-scrollbars/run-row.ps1 11; receipts C:/Temp/av-kit/2026-11-26-capture-key-inbox-scrollbars/cki-row11-*.txt", "scope": "Row 11: the 09 Delivered note, MEU-167 ready_for_review", "phase": "static", "exit_code": 0, "result": "pass", "tested_state": "HEAD e5028a3 (baseline.sha) plus rows 0 to 11", "output": "cki-row11-canon.txt: row-check canon: 0 problem(s). cki-row11-status-MEU-167.txt: ready_for_review"}
```

```json
{"schema_version": "evidence.v1", "cwd": "P:/av-kit", "check_id": "cki-h1-2-gate", "command": "$env:ELECTRON_RUN_AS_NODE=$null; rtk proxy pwsh -NoProfile -File docs/execution/plans/2026-11-26-capture-key-inbox-scrollbars/session-gate.ps1 *> C:/Temp/av-kit/2026-11-26-capture-key-inbox-scrollbars/cki-gate-h1.txt (task.md row H1-2's Validation cell); step receipts C:/Temp/av-kit/2026-11-26-capture-key-inbox-scrollbars/cki-D6-*.txt", "scope": "H1-2: the registered verification plan, as in the MEU-165 handoff", "phase": "full", "exit_code": 0, "result": "pass", "tested_state": "e5028a3ad45fa033c388dea46658ff282fbd7364+937ef42b857984acb234116d46866c6f400165b024ddc6e8e943398619c92a78", "fresh": true, "snapshot": false, "output": "cki-gate-h1.txt: tested_state before=e5028a3ad45fa033c388dea46658ff282fbd7364+937ef42b857984acb234116d46866c6f400165b024ddc6e8e943398619c92a78 after=e5028a3ad45fa033c388dea46658ff282fbd7364+937ef42b857984acb234116d46866c6f400165b024ddc6e8e943398619c92a78; session-gate: all steps exit 0. cki-D6-ui-capture.txt: Tests  353 passed (353). cki-D6-ui-tests.txt: Tests  1716 passed (1716). cki-D6-ui-build.txt: ✓ built in 6.38s. cki-D6-e2e-remote.txt: row-check remote-fresh: 0 problem(s)"}
```

### Quality Gate Results

The gate ran twice. Run 1 stopped at ui-tests with `Tests  9 failed | 1707 passed (1716)`, each failure `Error: Test timed out in 5000ms.`, in six main-process files this session does not change, while another repository's gate loaded the PC; the six files pass alone (`Tests  99 passed (99)`, `cki-h12-diag-6files.txt`). Under D-1438 run 1's receipts are kept as `cki-gate-h1-r1.txt` and `cki-D6-*-r1.txt`, and the whole gate ran again, unchanged, once that load had ended. Run 2 (`cki-gate-h1.txt`): `tested_state before=e5028a3ad45fa033c388dea46658ff282fbd7364+937ef42b857984acb234116d46866c6f400165b024ddc6e8e943398619c92a78 after=e5028a3ad45fa033c388dea46658ff282fbd7364+937ef42b857984acb234116d46866c6f400165b024ddc6e8e943398619c92a78`, 28 steps each exit 0, last line `session-gate: all steps exit 0`. Skipped by the gate's own rules: `electron-devpc reason=D-1411 (E2E runs on mini-air; the e2e-remote step)`; `mcp-tests reason=no MCP file changed (mcp-server/ is read-only, bound by scope-paths)`. The full table is in the MEU-165 handoff; the steps that bear on MEU-167:

| Step | Stage | Result | Decisive line | Receipt |
|------|-------|--------|---------------|---------|
| ui-types | static | exit 0 | `tsc --noEmit: no diagnostics` | `cki-D6-ui-types.txt` |
| ui-lint | static | exit 0 | `eslint src/ tests/ --max-warnings 0: no diagnostics` | `cki-D6-ui-lint.txt` |
| guards | static | exit 0 | `row-check guards: 0 problem(s)` | `cki-D6-guards.txt` |
| ui-capture | targeted | exit 0 | `Tests  353 passed (353)` | `cki-D6-ui-capture.txt` |
| ui-tests | full | exit 0 | `Tests  1716 passed (1716)` | `cki-D6-ui-tests.txt` |
| ui-build | full | exit 0 | `✓ built in 6.38s` | `cki-D6-ui-build.txt` |
| e2e-remote | full | exit 0 | `row-check remote-fresh: 0 problem(s)` | `cki-D6-e2e-remote.txt` |
| state-render | full | exit 0 | `✅ Drift check passed — SSOT loaded (174 MEUs, 12 phases), rendered regions match on-disk content` | `cki-D6-state-render.txt` |
| identity-after | identity | exit 0 | `tested_state e5028a3ad45fa033c388dea46658ff282fbd7364+937ef42b857984acb234116d46866c6f400165b024ddc6e8e943398619c92a78` | `cki-D6-identity-after.txt` |

---

## Changed Files

Counts are added / removed lines against `HEAD` `e5028a3` (`git diff --numstat --ignore-cr-at-eol HEAD`); a new file's count is its line count.

| File | Change | Added / removed |
|------|--------|-----------------|
| `ui/src/renderer/src/features/capture/capture-scroll-bars.ts` | the geometry module | new, 66 |
| `ui/src/renderer/src/features/capture/CaptureViewport.tsx` | the two overlay bars and the thumb drag | +132 / -1 |
| `ui/tests/unit/capture-scroll-bars.test.ts` | AC-167.1 to AC-167.3 | new, 171 |
| `ui/tests/unit/capture-scroll-bars.behavior.test.ts` | AC-167.4 to AC-167.6 | new, 334 |
| `ui/tests/e2e/capture-inbox.test.ts` | AC-167.7 and AC-167.8 as added lines | +129 / -0 |
| `ui/tests/e2e/test-ids.ts` | the scroll-bar ids, a new block at the end | +5 / -0 |
| The shared records | see the MEU-165 handoff's Changed Files | |

Nothing is committed or staged.

---

## Codex Validation Report

### Recheck Protocol

1. Read Scope + AC table
2. Verify each AC against Evidence section (file:line, not memory)
3. Independently probe the claimed behavior and compare decisive output
4. Verify the full gate is fresh and matches current D6 inputs; rerun if changed or unproven
5. Record findings below

### Findings

| # | Severity | Blocking | Kind | Finding | File:Line | Recommendation | Status |
|---|----------|----------|------|---------|-----------|----------------|--------|

### Verdict

Pending: the H1-7 execution review.

---

## Deferred Items

| Item | Kind | Deferred-to | Basis |
|------|------|-------------|-------|
| Keyboard control of the bars, a click on the track to page, and wheel scrolling | out-of-scope | — | D-1427; every wheel event zooms |
| A native scroll container for the viewport | out-of-scope | — | D-1426 |
| Commit and push | out-of-scope | — | Only on Mat's direction (H2) |

### Departures and their basis

- **Row 9.** The first Green run failed on a `-0` pan; the module's share goes through `Math.max`, and the row ran again.
- **D-1431.** MEU-167 stayed in this session, as the plan chose.
- The session-wide departures, D-1433 to D-1438, are in the MEU-165 handoff.

---

## Decision Log

None.

---

## History

| Event | Date | Agent | Detail |
|-------|------|-------|--------|
| Created | 2026-11-27 | claude-code-local (Claude Opus 5.5) | Handoff after the H1-2 gate, H1-3, H1-4 and H1-5 |
