---
date: "2026-10-15"
project: "capture-chrome"
meu: "MEU-80"
status: "complete"
action_required: "VALIDATE_AND_APPROVE"
template_version: "2.2"
verbosity: "standard"
plan_source: "docs/execution/plans/2026-10-14-capture-chrome/implementation-plan.md"
build_plan_section: "bp09"
agent: "claude-code (Claude Opus 5.5)"
reviewer: "Codex via local dispatch (H1-7 execution review)"
predecessor: "none"
---

# Handoff: 2026-10-14-capture-chrome-MEU-80-handoff

> **Status**: `complete`
> **Action Required**: `VALIDATE_AND_APPROVE`

---

## Scope

**MEU**: MEU-80 — `gui-icon-button-hints`.
- **`TOOLTIP`.** A new shared primitive, `ui/src/renderer/src/components/ui/Tooltip.tsx`. It renders a hint for icon-only controls, because native `title` tooltips are unreliable and never reach disabled Buttons (D-8, D-14).
  - **Wrapper.** It wraps its child in a `{id}-tip` span that takes the pointer and focus events. When the child is disabled, the span is the tab stop.
  - **Hint.** It portals one `role="tooltip"` `{id}-hint` to `document.body`.
  - **Rules.** It implements `HINT_TEXT`, `HINT_TIMING` (400 ms show, 120 ms grace), `TOOLTIP_PLACEMENT`, `HINT_SINGLETON`, `DESCRIBEDBY_COMPOSE` and `suppressed`, and it strips the child's `title` (`HINT_TITLE_RULE`).
- **`ICON_BUTTON`.** `ToolbarIconButton` moved out of `CaptureViewport.tsx` into `features/capture/ToolbarIconButton.tsx`. It wraps in `TOOLTIP` and takes `spec` and `reason`; the old `disabledHint`/`title` path is gone. All 12 `TOOLBAR_BUTTONS` adopt it.
- **Apply and Revert.** `CapturePage.tsx` replaces Session 30's A-10 reason label (`reasonTip`, `showReason`, `capture-*-image-reason`) with `TOOLTIP` on Apply and Revert.
- **Non-Capture controls.** The 7 non-Capture controls of `ICON_ONLY_INVENTORY` wrap in `TOOLTIP` and drop `title`: `console-close`, `bulk-toast-dismiss`, `queue-card-drag-handle`, `queue-card-kebab` (suppressed while its menu is open), `up-btn`, `down-btn` and `convert-staged-remove`.
- **Test amendments.** `TEST_AMENDMENTS` TA-8, TA-11, TA-12, TA-14, TA-15 and TA-22–TA-25 were applied as written, each tagged. `FIXTURE_REPAIRS` (a) was applied to `queue-slot-baseline.json`. TA-27 and TA-28 were added at H1-3 (`walkthrough.md` A-9; Mat chose option 1, D-37) and applied as written.
- **Root cause.** `ROOT_CAUSE_PROBE` ran (AC-80.12). The finding: no environment cause; `Button.tsx:34` `disabled:pointer-events-none` blocks hover on disabled buttons, and MEU-80's wrapper already fixes that in scope. No Decision Brief was needed.

**Build Plan Section**: `docs/build-plan/09-screenshot-capture.md` 09:682-685 (icon-button hints).
**Predecessor**: none (first MEU of Session 34). MEU-81 builds on `ToolbarIconButton` and `TOOLTIP`.

---

## Acceptance Criteria

| AC | Type | Description | Source | Test(s) | Status |
|----|------|-------------|--------|---------|--------|
| AC-80.1 | unit | A hover shows one portaled `{id}-hint` after `HINT_DELAY_MS` with `HINT_TEXT`; the focus target's `aria-describedby` gains the hint id | Spec 09:682-683 | `ui/tests/unit/tooltip.test.tsx:90` | ✅ |
| AC-80.2 | unit | Focus shows the hint at once; blur hides it and removes the hint id | Spec 09:682; APG | `tooltip.test.tsx:115` | ✅ |
| AC-80.3 | unit | Escape (not prevented), pointerdown, and the grace period dismiss; the hint itself is hoverable | `HINT_TIMING`; D-11 | `tooltip.test.tsx:143`; `capture-page.behavior.test.ts:2533` (R1 F1) | ✅ |
| AC-80.4 | unit | A disabled child gets a focusable wrapper that carries the hint id; an enabled child does not; no `title` anywhere (JSX or spread) | D-8, D-12 | `tooltip.test.tsx:228` | ✅ |
| AC-80.5 | unit | `HINT_TEXT`, `HINT_SINGLETON`, `suppressed` | D-9, D-10 | `tooltip.test.tsx:263` | ✅ |
| AC-80.6 | unit | `TOOLTIP_PLACEMENT`: centred below, clamped to 8 px, flipped above | D-10 | `tooltip.test.tsx:319` | ✅ |
| AC-80.7 | unit | Source guard on `Tooltip.tsx` (no `features/` import, hex, `transition-all` or `title=`; portal; token classes) | G32, G33; D-12 | `tooltip.test.tsx:381` | ✅ |
| AC-80.8 | unit | Capture: the 12 `TOOLBAR_BUTTONS` are wrapped, untitled and hinted, with and without a shot | Spec 09:682; D-13 | `ui/tests/unit/icon-hints.test.ts:308` | ✅ |
| AC-80.9 | unit | The non-Capture icon-only controls are wrapped, untitled and hinted by their `aria-label` | D-13 | `icon-hints.test.ts:328` | ✅ |
| AC-80.10 | integration | Electron, real hover at 1280×800: enabled Arrow and disabled Undo hints inside the window; focus and Escape | Spec 09:685 | `ui/tests/e2e/capture-inbox.test.ts:1614` | ✅ (10/10 under `--repeat-each=10`) |
| AC-80.11 | integration | Electron: hovering `console-close` shows its hint inside the window, moving away hides it; `nav-capture` shows none | D-13 | `ui/tests/e2e/console-chrome.test.ts:207` | ✅ (10/10 under `--repeat-each=10`) |
| AC-80.12 | integration | `ROOT_CAUSE_PROBE` ran on the target, bound to `baseline.sha`, the build, the probe script and the receipt; 6 observations and a finding | D-14 | `validate-task.ps1 -Check probe` then `-Check root-cause` (task row 2) | ✅ |
| AC-80.13 | unit | `DESCRIBEDBY_COMPOSE` keeps the child's `aria-describedby`, ref and handlers, enabled and disabled | `TOOLTIP` | `tooltip.test.tsx:402` | ✅ |

### Other plan AC references (not owned by MEU-80)

| AC | Owner | Status in MEU-80 |
|----|-------|------------------|
| AC-81.x | MEU-81 handoff | ⏳ rows 6–8 |
| AC-57.5, AC-65.2, AC-66.7, AC-67.20, AC-67.23, AC-67.35 | existing Capture suites | pass with TA-8, TA-11, TA-12, TA-14, TA-15, TA-22–TA-24 as written |
| AC-49.8, AC-49.9 | `queue-card.test.ts` | pass with TA-25 as written |
| AC-49.27 | `download-queue.test.ts:1351` (Electron) | failed at `GATE` run 3, passes at runs 4, 5, 7, 9, 10 and 12 with TA-27 (A-9) |
| AC-52 | `convert-queue.test.ts:1255,1297` (Electron) | one failed at `GATE` run 3; both pass at runs 4, 5, 7, 9, 10 and 12 with TA-28 (A-9) |
| AC-55.1 | `queue-card-slots` | pass after `FIXTURE_REPAIRS` (a); it was `FIXTURE_RED` at row 3 |
| AC-51.6 | `layout-primitives` | pass (Windows, CRLF checkout) |
| AC-44.7 | `queue-card` suite | pass; the labelled queue-card primary action keeps its `title` and has no tip (outside `ICON_ONLY_INVENTORY`) |
| AC-41.3 | `queue-canon.test.ts` | pass on this Windows host (it reads `P:/zorivest`'s live CSS); untouched by MEU-80 |
| AC-39.5, AC-39.28 | MEU-81 (`capture-hotkey-banner` id; action-row structure) | ⏳ rows 6–8; untouched by MEU-80 |
| AC-60.x | MEU-81 (TA-1–TA-3 amend AC-60.10, 60.13, 60.19) | ⏳ rows 6–8; pass unchanged in `gate80` |
| AC-50.1, AC-50.4 | `layout-canon.test.ts` (row 10 hub) | ⏳ row 10; pass unchanged in `gate80` |
| AC-8 | not an AC: the plan's `-g "AC-8[01]"` Playwright grep pattern (green-81) | — |

<!-- CACHE BOUNDARY -->

---

## Evidence

### FAIL_TO_PASS

| Test | Red Output (hash/snippet) | Green Output | File:Line |
|------|--------------------------|--------------|-----------|
| AC-80.1–80.7, AC-80.13 | `red-import`: `tooltip.test.tsx` fails to load on the missing `components/ui/Tooltip` only | pass | `tooltip.test.tsx:90-375` |
| AC-80.8, AC-80.9 | `TestingLibraryElementError` (no `{id}-tip`); the `icon-hints` setup sentinel passes | pass | `icon-hints.test.ts:308,328` |
| TA-8, TA-11 ×3, TA-12 ×3, TA-14, TA-15 | `AssertionError` | pass | `capture-page.behavior.test.ts:1090,1276,1314,1529,2281,2309,2426,2471,2502` |
| TA-25 ×2 | `AssertionError` | pass | `queue-card.test.ts:1226,1281` |
| AC-55.1 (`FIXTURE_RED`) | fails after `FIXTURE_REPAIRS` (a) | pass | `queue-card-slots` |
| Electron AC-80.10, AC-80.11 | `unexpected` by `expect()` | pass | `capture-inbox.test.ts:1614`; `console-chrome.test.ts:207` |

TA-22–TA-24 (`capture-inbox.test.ts:1436,1557,1579`) sit outside `-g AC-80`, so they first ran at the gate (`--tags`), where they pass. Red detail is in `task.md` §Evidence, Row 3.

### Commands Executed

```json
{"schema_version":"evidence.v1","check_id":"s34-red-80","command":"rtk proxy pwsh -NoProfile -File docs/execution/plans/2026-10-14-capture-chrome/validate-task.ps1 -Check red-80","cwd":"P:/av-kit-wt/s34-capture-chrome","scope":"vitest-red --meu 80 and e2e-red --meu 80 per CASE_EVIDENCE","phase":"red","exit_code":0,"result":"pass","tested_state":"baseline 5493b14 + MEU-80 tests, TA and FIXTURE_REPAIRS (a); no MEU-80 source","output":"PASS red-80. Vitest: 14 failed, 109 passed (red-import on Tooltip only; AssertionError on the 9 tagged cases; FIXTURE_RED). Electron: AC-80.10, AC-80.11 unexpected by expect()","fresh":true}
```

```json
{"schema_version":"evidence.v1","check_id":"s34-green-80","command":"rtk proxy pwsh -NoProfile -File docs/execution/plans/2026-10-14-capture-chrome/validate-task.ps1 -Check green-80","cwd":"P:/av-kit-wt/s34-capture-chrome","scope":"MEU-80 Vitest files and neighbours, ui build, Electron capture-inbox + console-chrome -g AC-80","phase":"targeted","exit_code":0,"result":"pass","tested_state":"MEU-80 implementation","output":"PASS green-80. Vitest: 13 files, 252/252 passed. Build OK. Electron: expected 2, unexpected = flaky = skipped = 0","fresh":true}
```

```json
{"schema_version":"evidence.v1","check_id":"s34-gate80","command":"rtk proxy pwsh -NoProfile -File docs/execution/plans/2026-10-14-capture-chrome/validate-task.ps1 -Check gate80","cwd":"P:/av-kit-wt/s34-capture-chrome","scope":"ui typecheck, lint, full Vitest --meu 80, ui and harness build, Electron --tags, --repeat-each=10 over AC-80.10 and AC-80.11","phase":"targeted","exit_code":0,"result":"pass","tested_state":"MEU-80 final working tree (baseline 5493b14 + MEU-80 diff + plan_checks.py A-1)","output":"PASS Vitest: 811/811 passed; MEU 80 cases and tags passed | PASS Electron: expected 39, unexpected = flaky = skipped = 0; named cases passed | PASS Electron: expected 10 … (AC-80.10 repeat) | PASS Electron: expected 10 … (AC-80.11 repeat) | PASS gate80","fresh":true}
```

The first `gate80` run had every product check passing (39 Electron specs, and all 10 AC-80.10 repeats) but was refused by the checker. `e2e-ok --ac` expected one spec per named case, while `--repeat-each` reports one spec per repeat. That is amendment A-1 in `walkthrough.md` §Amendments: a plan-local checker fix with three selftest cases (selftest PASS, 101 inputs). The run above is the gate of record. 
```json
{"schema_version": "evidence.v1", "check_id": "s34-gate", "command": "rtk proxy pwsh -NoProfile -File docs/execution/plans/2026-10-14-capture-chrome/validate-task.ps1 -Check gate, then -Check gate-check", "cwd": "P:/av-kit-wt/s34-capture-chrome", "scope": "GATE: the 17 D6 stages (CI installs, types, lint, pytest, full Vitest, builds, MCP tests, OpenAPI drift, state render, full Electron, source audit); gate-check applies CASE_EVIDENCE, COUNT_FLOORS and TA_LATE to the raw reports", "phase": "full", "exit_code": 0, "result": "pass", "tested_state": "304F53FCD0D7FF9B5C769E431A1390B25835D58B28BD3BDFDBFC8E6CACA3621E", "output": "PASS GATE: 17/17 stages exit 0; pytest 655 passed; Vitest 824/824; Electron expected 142, unexpected = flaky = skipped = 0 | PASS gate-check", "fresh": true}
```

The authoritative full gate is `GATE` run 12 (H1-3; `walkthrough.md` §Gate), `identity_after` `304F53FCD0D7FF9B5C769E431A1390B25835D58B28BD3BDFDBFC8E6CACA3621E`. It follows A-15, a value-identical rewrite of the plan's decision text (no product file changed), and A-16: run 11 on the same tree failed one Electron spec, AC-57.10 (`capture-inbox.test.ts:756`), intermittently (1 failure in 20 isolated repeats, then 100 of 100; archived `s34-gate-run11*`). Run 10 passed at `C694AB0D…06B1DA` (archived `s34-gate-run10*`) after A-14, the D-39 validator hardening. Run 9 passed at `396D7434…9DC103` (archived `s34-gate-run9*`) after A-13 / D-39. Run 7 passed at `A55CA7AF…AEF390` (archived `s34-gate-run7*`) after the execution review round 1 corrections (F1, F2) and A-12 (run 6 refused a duplicate AC-80.3 test title; archived `s34-gate-run6*`). Run 8 was stopped by the author after its pytest stage, because the D-39 validator hardening changed an `IDENTITY_SCOPE` file mid-run; its partial log is `s34-gate-run8-aborted.txt` and it is not a gate result. Run 5 passed at `F2A550D7…FDF8C2` (archived `s34-gate-run5*`), and run 4 passed before A-10 (a plan-local `handoff-ac` fix, D-38) changed `IDENTITY_SCOPE` files. Runs 1 to 3 failed on causes outside the product code. Their archived receipts were deleted by run 5's `s34-gate-*` cleanup (execution review R1 F2; the cleanup now spares `s34-gate-run<n>*`), so they are described from the console output read at the time: A-7 (no packaged backend in the fresh worktree, built), A-8 (no FFmpeg; the pinned download URL is dead, so the verified binaries were copied from the main checkout) and A-9 (below).

- **A-9.** Run 3 failed AC-49.27 and one AC-52 test. Each waited for any `document` keydown listener as the sign that dnd-kit's keyboard sensor was listening. A focused grip now shows its hint at once, and a visible hint listens for Escape on the document, so the wait passed before Space and ArrowDown raced the sensor (3 of 6 failed alone). TA-27 and TA-28 wait for the hint and zero the count before Space; no expected value changed. The three specs passed 30 of 30 under `--repeat-each=10`, and all pass at run 4. `plan_checks.py` gained `TA_LATE`, so `gate-check` requires both tags.

- **Execution review R1 F1.** With focus on `capture-draw-surface`, Escape did not hide a hovered toolbar hint: the surface's `onKeyDown` stops propagation at React's root, before the hint's bubbling `document` listener. `Tooltip.tsx` now listens in the capture phase, still neither preventing nor stopping the key, so the editor's own Escape runs as before. Two regressions were red first (`s34-r1f1-red.txt`) and are green (`s34-r1f1-green.txt`): `tooltip.test.tsx:201` (an editor that stops propagation; retitled `execution R1 F1: …` by A-12, since `CASE_EVIDENCE` binds AC-80.3 to the one case at line 143) and `capture-page.behavior.test.ts:2533` (the real surface; the editor still prevents its Escape). The listener counters behind TA-27 and TA-28 count `keydown` registrations in either phase, so those waits are unchanged.

- **A-13 / D-39, A-14 (session tooling, not MEU product).** After execution review round 2 approved, `review-check` still refused: `tools/validate_closeout_artifacts.py` read round 1's Findings table of the rolling review, where F1 is open and blocking, and `validate-task.ps1:432` omitted `--max-review-rounds`. Mat chose "Fix the validator". `parse_review` now judges a rolling review by its latest round: each round runs to the next `## Recheck` heading; round 1's open blocking findings are carried through every recheck until one closes them by whole id in a `Recheck result` cell that is only a closure status (closed, fixed, resolved, verified, accepted, accepted_risk or withdrawn, optionally joined by / or ,); each round's own Findings tables (heading level 2 to 6) add their open blocking rows; a round without its own Findings table counts as one more open blocking finding; and `TABLE_ROW` reads a row with a blank first cell as data, so a finding without an id counts and can never be closed. Execution review round 3 attempt 1 (its verdict refused by the ledger, A-14) found three false approvals in the first design and the author a fourth; all were fixed test-first. Nineteen rolling-review selftest scenarios, red in four passes (`s34-d39-red.txt`, `-red2.txt`, `-red3.txt`, `-red4.txt`) and green (`s34-d39-green4.txt`: 215 arms, 0 failures). `PRODUCT_SCOPE` excepts that one `tools/` file, which is listed in MEU-81's Files Modified; `plan_checks.py` checks the exception (`FROZEN_EXCEPT`, three scope cases). No product file changed; `GATE` run 10 reran because these files are in `IDENTITY_SCOPE`.

### Quality Gate Results

```
ui typecheck: 0 errors
ui lint: 0 (--max-warnings 0)
Vitest (full suite): 86 files, 811/811
ui build + harness build: pass
Electron --tags: 39 expected, 0 unexpected, 0 flaky, 0 skipped
repeat-each=10: AC-80.10 10/10, AC-80.11 10/10
plan_checks.py selftest: PASS (101 inputs: 86 refusals, 15 well-formed)
```

`GATE` run 12 (H1-3):

```
17/17 stages exit 0; pytest 655 passed; Vitest 824/824
Electron (full): 142 expected, 0 unexpected, 0 flaky, 0 skipped
plan_checks.py selftest: PASS (105 inputs: 89 refusals, 16 well-formed)
```

---

## Changed Files

| File | Action | Lines | Summary |
|------|--------|-------|---------|
| `ui/src/renderer/src/components/ui/Tooltip.tsx` | new | 1–299 | `TOOLTIP`, `hintText`, `placeHint`, `HINT_DELAY_MS`, `HINT_GRACE_MS` |
| `ui/src/renderer/src/features/capture/ToolbarIconButton.tsx` | new | 1–45 | `ICON_BUTTON`, moved from `CaptureViewport.tsx` |
| `ui/src/renderer/src/features/capture/CaptureViewport.tsx` | modified | +22/−40 | imports `ToolbarIconButton`; `spec`, `reason` |
| `ui/src/renderer/src/features/capture/CapturePage.tsx` | modified | +6/−52 | A-10 reason label replaced by `TOOLTIP` on Apply and Revert |
| `ui/src/renderer/src/components/layout/ConsolePanel.tsx` | modified | +14/−11 | `console-close` wrapped |
| `ui/src/renderer/src/components/queue/BulkResultToast.tsx` | modified | +12/−9 | `bulk-toast-dismiss` wrapped |
| `ui/src/renderer/src/components/queue/QueueCard.tsx` | modified | +17/−14 | drag handle wrapped (disabled follows `drag.disabled`) |
| `ui/src/renderer/src/components/queue/QueueCardMenu.tsx` | modified | +19/−16 | kebab wrapped, `suppressed={open}`, `title` dropped |
| `ui/src/renderer/src/features/transcript/TranscriptPage.tsx` | modified | +35/−24 | `up-btn`, `down-btn` wrapped, `title` dropped |
| `ui/src/renderer/src/features/converter/ConvertPage.tsx` | modified | +12/−9 | `convert-staged-remove` wrapped |
| `ui/tests/unit/tooltip.test.tsx` | new | 1–460 | AC-80.1–80.7, AC-80.13; the AC-80.3 editor regression (R1 F1) |
| `ui/tests/unit/icon-hints.test.ts` | new | 1–440 | AC-80.8, AC-80.9, setup sentinel |
| `ui/tests/e2e/capture-inbox.test.ts` | modified | +73/−17 | AC-80.10; TA-22–TA-24 |
| `ui/tests/e2e/console-chrome.test.ts` | modified (append only) | +32 | AC-80.11 |
| `ui/tests/e2e/test-ids.ts` | modified | +6 | MEU-80 `NEW_TESTIDS` |
| `ui/tests/unit/capture-page.behavior.test.ts` | modified | +111/−28 | TA-8, TA-11, TA-12, TA-14, TA-15; the AC-80.3 surface regression (R1 F1) |
| `ui/tests/unit/queue-card.test.ts` | modified | +11/−5 | TA-25 |
| `ui/tests/e2e/download-queue.test.ts` | modified | +14/−1 | TA-27 (A-9, D-37) |
| `ui/tests/e2e/convert-queue.test.ts` | modified | +16/−2 | TA-28 (A-9, D-37) |
| `ui/tests/unit/fixtures/queue-slot-baseline.json` | modified | 1 line | `FIXTURE_REPAIRS` (a) |
| `docs/execution/plans/2026-10-14-capture-chrome/plan_checks.py` | modified | +45/−8 (with A-9) | A-1: `e2e-ok --ac` accepts one spec per repeat; A-9: `TA_LATE` |

```diff
-      <span
-        data-testid="capture-apply-image-tip"
-        className="inline-flex"
-        title={apply.enabled ? undefined : apply.title}
-        onMouseEnter={(event) => {
-          showReason('apply', event.currentTarget)
-        }}
-        onMouseLeave={hideReason}
-      >
+      <Tooltip id="capture-apply-image" label="Apply to image" reason={apply.title} disabled={!apply.enabled}>
```

```diff
-      <button
-        ref={triggerRef}
-        ...
-        title={triggerLabel}
+      <Tooltip id={triggerTestId} label={triggerLabel} suppressed={open}>
+        <button
+          ref={triggerRef}
```

### Design notes for the reviewer

- **Press guard.** A mouse press focuses its target by default, and that focus must not show the hint. The guard keys on `mousedown`, which is the event whose default action focuses. The focus it causes consumes the guard; otherwise `mouseup` clears it. An earlier guard keyed on `pointerdown`/`pointerup` stayed set after a lone `pointerdown` and suppressed the next keyboard focus; the AC-80.9 drag handle caught it.
- **Hover against focus.** A hint shown or kept by focus (`heldByFocus`) stays until blur or Escape, not until the pointer leaves.
- **Portal.** The hint is a React descendant of the wrapper, so React's enter and leave events treat a move from the trigger into the hint as staying inside. The hint's own `onPointerEnter` and `onPointerLeave` handle the grace.
- **Focus ring.** The disabled wrapper is the tab stop, so it carries the Button focus-ring classes.

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

## Deferred Items

None.

---

## Decision Log

```yaml
decision_log:
  - id: D-33
    stage: execution
    question: "gate80's repeat step was refused ('AC-80.10: 10 cases … (need 1)') although all 10 repeats passed. Fix the checker or change the run?"
    resolution: autonomous
    class: two-way
    chosen: "Fix plan_checks.py eval_e2e_ok: for an --ac case, several hits are accepted only with one shared title and a count equal to the run's expected; every hit must be expected. Three selftest cases added. Recorded as walkthrough.md §Amendments A-1 (S7)."
    source_tag: Local Canon
    precedents: ["docs/execution/plans/2026-10-14-capture-chrome/implementation-plan.md S7 — a gate failure that is not a product defect is an A-n row and a Decision Brief", "task.md Row 1 — a plan-local checker defect fixed with a selftest positive"]
    research: { engine: none, sources: [] }
    reasoning: "Playwright --repeat-each reports each repeat as its own spec with the same title, so the one-spec assumption was wrong, not the product. The fix keeps the gate rule that every repeat ran and passed, and refuses an extra spec or a second differently titled case. Running ten separate invocations would prove the same thing at ten times the Electron launches."
  - id: D-34
    stage: execution
    question: "The first Tooltip press guard (pointerdown to pointerup) stayed set after a lone pointerdown and suppressed the next keyboard focus (AC-80.9 drag handle). What does the guard key on?"
    resolution: autonomous
    class: two-way
    chosen: "Key the guard on mousedown, the event whose default action focuses; the focus consumes it, or document mouseup clears it. A hint shown by focus is held until blur or Escape."
    source_tag: Local Canon
    precedents: ["implementation-plan.md TOOLTIP / HINT_TIMING — pointerdown hides; focus shows at once"]
    research: { engine: none, sources: [] }
    reasoning: "Focus after a press comes from mousedown's default action, not pointerdown, so a mousedown-keyed guard that the focus consumes cannot leak into a later keyboard focus. No AC changed."
```

---

## History

| Event | Date | Agent | Detail |
|-------|------|-------|--------|
| Created | 2026-10-15 | claude-code | Initial handoff after gate80 |
| Reconciled | 2026-10-15 | claude-code | H1-5: `GATE` run 5, A-7 to A-10, TA-27 and TA-28 (D-37) |
| Corrected | 2026-10-15 | claude-code | Execution review R1: F1 (Escape in the capture phase; two AC-80.3 regressions), F2 (archive cleanup; retention claims corrected); A-12 retitle; `GATE` run 7 |
| Corrected | 2026-10-15 | claude-code | A-13 / D-39: the closeout validator reads a rolling review's latest round (Mat: "Fix the validator"); `GATE` run 9 |
| Corrected | 2026-10-15 | claude-code | A-14: the D-39 parser hardened after execution review round 3 attempt 1 (exact ids, a closure-status cell, unreadable rounds refuse, blank-id rows count); `GATE` run 10 |
| Corrected | 2026-10-15 | claude-code | A-15: decision records rewritten value-identically; A-16: `GATE` run 11 failed AC-57.10 (`capture-inbox.test.ts:756`) once, intermittently; `GATE` run 12 |
