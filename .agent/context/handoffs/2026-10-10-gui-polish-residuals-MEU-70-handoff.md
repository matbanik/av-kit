---
date: "2026-10-11"
project: "gui-polish-residuals"
meu: "MEU-70"
status: "complete"
action_required: "VALIDATE_AND_APPROVE"
template_version: "2.2"
verbosity: "standard"
plan_source: "docs/execution/plans/2026-10-10-gui-polish-residuals/implementation-plan.md"
build_plan_section: "bp11"
agent: "claude-code-web (Claude Opus 5.5)"
reviewer: "Codex gpt-6.1-sol via local dispatch (human-review-decision.md)"
predecessor: "2026-10-10-gui-polish-residuals-MEU-69-handoff.md"
---

# Handoff: 2026-10-10-gui-polish-residuals-MEU-70-handoff

> **Status**: `complete`
> **Action Required**: `VALIDATE_AND_APPROVE`

---

## Scope

**MEU**: MEU-70 — `gui-settings-section-emphasis`, rail fix first (spec "Verify first", ST3), then the emphasis.
- **Rail fix (row 6).** `TAIL_SPACER`: a measured bottom spacer (`settings-tail-spacer.ts`) lets the last section scroll up to `SECTION_SCROLL_MARGIN` (16 px) below `main`'s top, so every section can reach the rail's top band (Human-approved D-9; `TAIL_SPACER_HEIGHT`, D-16). `SCROLL_RECHECK`: the rail also runs its existing `current()` on scroll, once per frame and never during a click lock (D-17). This fixes R4: on a tall window the rail stuck on Capture.
- **D-22 (execution correction).** The longer reveal exposed a race in `revealSection`'s A-3 fallback (the existing AC-58.12 Electron spec failed 5/5): it jumped back to a clicked section after the user scrolled to the top. `REVEAL_FALLBACK` now completes a smooth reveal only if the scroller emitted no scroll event. AC-70.10 covers both sides; AC-58.12 is unchanged.
- **Emphasis (row 7).** `ACTIVE_SOURCE`: `SettingsRail` reports its active entry (`onActiveChange`); `SettingsPage` passes `current` to all ten `SettingsSectionFrame` usages and to `StartAtSignInControl` (Startup). `SECTION_EMPHASIS`: one helper, `sectionFrameProps` in `settings-section-frame.ts`, gives every frame `SECTION_FRAME_BASE` (constant padding and a 2 px left border) and swaps only colours for the current one (`bg-bg-elevated/40`, `border-accent`) plus `data-current="true"`. Frames never carry `aria-current`.

**Build Plan Section**: `docs/build-plan/11-page-layout.md` §Settings section emphasis (residual) (11:133-143, matrix 11.12); ST3 (11:49)
**Predecessor**: [MEU-69 handoff](2026-10-10-gui-polish-residuals-MEU-69-handoff.md) (no shared file).

---

## Acceptance Criteria

| AC | Type | Description | Source | Test(s) | Status |
|----|------|-------------|--------|---------|--------|
| AC-70.1 | unit | `tailSpacerHeight` worked examples (384, 0, 1), the fixpoint, fail-closed inputs, integer ≥ 0; `SECTION_SCROLL_MARGIN === 16` | D-16 | `ui/tests/unit/settings-tail-spacer.test.ts:20,26,32,51,61` | ✅ |
| AC-70.2 | integration | Electron `TRAIL_REACH` as two independent specs: every section becomes current after its own scroll; at max scroll MCP is current and its top within 17 px of `main`'s top; diagnostics attached | Spec 11:141; Human-approved D-9; RULE-2 | `ui/tests/e2e/settings.test.ts:484` `AC-70.2 DEFAULT_WINDOW…`, `:492` `AC-70.2 TALL_WINDOW…` | ✅ |
| AC-70.3 | integration | `SCROLL_RECHECK`: a bottom scroll with no observer callback makes MCP current; a scroll during a click lock leaves the clicked entry; the listener is removed on unmount | D-17; ST3, A-6 | `ui/tests/unit/settings-rail.test.tsx:574,588,611` | ✅ |
| AC-70.4 | integration | `TAIL_SPACER`: hidden last child after `mcp-access-card`, `0px` without ResizeObserver, `tailSpacerHeight(...)` with it and re-measured; every rendered frame carries `scroll-mt-4` (F5) | D-9, D-16; Review R2 F5 | `settings-rail.test.tsx:639,651,683,765` | ✅ |
| AC-70.5 | integration | `ACTIVE_SOURCE` + `SECTION_EMPHASIS`: exactly one `data-current` section equal to the rail's `aria-current` entry after render, click, keyboard and observer; state tokens; every frame carries `SECTION_FRAME_BASE`; no `aria-current`, `transition-all`, raw hex or negative vertical margin on a frame | Spec 11:142; D-14, D-15 | `ui/tests/unit/settings-emphasis.test.tsx:166,217` | ✅ |
| AC-70.6 | integration | Electron `NO_SHIFT` in document coordinates between Download-current and Capture-current samples (keys asserted different), ≤ 0.5 px; one `data-current`; background differs; border not transparent; `BOX_SEPARATION` > 16 px | Spec 11:142; D-14; Review R1 F3 | `settings.test.ts:529` `AC-70.6 …` | ✅ |
| AC-70.7 | integration | Regression: every existing MEU-58 / A-6 / MEU-61 / MEU-62 Settings spec passes unchanged | ST3, A-6 | `gate70`: Vitest REGSET (incl. `settings-rail`, `settings-page`), Electron `settings.test.ts` (12 passed: W4-1–W4-3, AC-61.17, three AC-58.12, AC-62.15, A-6 and the new specs) | ✅ |
| AC-70.8 | unit | `settings-tail-spacer` registered in the MEU-70 block at the end of `test-ids.ts` and used literally | AC-51.6 | `settings-tail-spacer.test.ts:71` | ✅ |
| AC-70.9 | integration | Supported Startup: activating it makes `start-at-sign-in-panel` the only current section; its tokens equal a page frame's in the same state; another entry clears it | Spec 11:142; D-20; Review R1 F2 | `settings-emphasis.test.tsx:226` | ✅ |
| AC-70.10 | integration | `REVEAL_FALLBACK` (added in execution, D-22): no fallback jump after a scroll event, even back at the start; the A-3 jump without any scroll event is kept | A-3; D-22 | `settings-rail.test.tsx:713,729`; AC-58.12 Electron unchanged | ✅ |

### Other plan AC references (not owned by MEU-70)

| AC | Owner | Status in MEU-70 |
|----|-------|------------------|
| AC-69.x | MEU-69 handoff | ✅ |
| AC-58.x, AC-61.x, AC-62.x | existing Settings suites | pass unchanged (AC-70.7) |
| AC-50.x | existing layout-canon suite (ST rows and mockup lock) | untouched; row 9 edits only the residual section |
| AC-51.6, AC-41.3 | existing suites | declared env-bound Vitest members (container only) |
| AC-26.x | existing chrome suite | untouched by MEU-70 (TA-1 belongs to MEU-69) |

<!-- CACHE BOUNDARY -->

---

## Evidence

### FAIL_TO_PASS

| Test | Red Output (hash/snippet) | Green Output | File:Line |
|------|--------------------------|--------------|-----------|
| Electron AC-70.2 DEFAULT_WINDOW | `toHaveAttribute` on `settings-rail-console`: Console clamped at max scroll (top 28 px), rail on MCP | pass | `settings.test.ts:484` |
| Electron AC-70.2 TALL_WINDOW | `toHaveAttribute` on `settings-rail-console`: Console stuck at 228 px, rail on Capture (R4) | pass | `settings.test.ts:492` |
| Electron AC-70.6 | first `toHaveAttribute('data-current', 'true')` failed | pass | `settings.test.ts:529` |
| Vitest AC-70.3 (×2) | `expected null to be 'location'`; `expected 0 to be greater than 0` | pass | `settings-rail.test.tsx:574,611` |
| Vitest AC-70.4 (×2) | `expected null not to be null`; `expected 0 to be greater than 0` | pass | `settings-rail.test.tsx:639,651` |
| Vitest AC-70.5 (×2) | `initial: data-current sections: expected … to have a length of 1 but got +0`; `settings-section-frame.ts exports SECTION_FRAME_BASE: expected null not to be null` | pass | `settings-emphasis.test.tsx:166,217` |
| Vitest AC-70.9 | `startup current: data-current sections: … got +0` | pass | `settings-emphasis.test.tsx:226` |
| Vitest AC-70.1, AC-70.8 | suite load `Cannot find module …/settings-tail-spacer` (the declared new module) | pass | `settings-tail-spacer.test.ts` |
| Vitest AC-70.10 | `expected [ { behavior: 'smooth', … }, … ] to have a length of 1 but got 2` (on the unchanged A-3 fallback) | pass | `settings-rail.test.tsx:713` |
| Electron AC-58.12 (existing, unchanged) | after row 6 without D-22: `settings-rail-download` `aria-current` Expected "location", Received "" (5/5) | pass | `settings.test.ts:229` |

Regression locks that passed at Red: AC-70.3 click-lock case (A-6 already holds the entry) and AC-70.4 rendered `scroll-mt-4` (F5). Details: [walkthrough.md](../../../docs/execution/plans/2026-10-10-gui-polish-residuals/walkthrough.md) §MEU-70 Red, §MEU-70 rail fix, §MEU-70 emphasis, §MEU-70 gate.

### Commands Executed

```json
{"schema_version":"evidence.v1","check_id":"s31-70-red","command":"bash docs/execution/plans/2026-10-10-gui-polish-residuals/validate-task.sh red70","cwd":"/home/user/av-kit","scope":"UNIT70 + UNIT70E Vitest, fresh build, Electron settings -g AC-70, require_failed_title AC-70.2 toHaveAttribute","phase":"targeted","exit_code":0,"result":"pass","tested_state":"MEU-69 complete (da68877) + MEU-70 tests and test id only; no MEU-70 production edit","output":"PASS AC-70 RED: 7 failing AC-70 assertions, 22 passing; other failing: [] | PASS AC-70 E2E RED: 3 failing AC-70 specs | PASS AC-70.2 RED on toHaveAttribute: ['AC-70.2 DEFAULT_WINDOW …', 'AC-70.2 TALL_WINDOW …']","fresh":true}
```

```json
{"schema_version":"evidence.v1","check_id":"s31-70-green-rail","command":"bash docs/execution/plans/2026-10-10-gui-polish-residuals/validate-task.sh green70-rail","cwd":"/home/user/av-kit","scope":"RAIL_STAGE_TESTS: settings-tail-spacer + REGSET Vitest; build; Electron settings -g AC-70.2|AC-58.12|A-6","phase":"targeted","exit_code":0,"result":"pass","tested_state":"row 6 (spacer, SCROLL_RECHECK, REVEAL_FALLBACK)","output":"PASS s31-70-green-rail: 85 passed of 86, env-bound tolerated: ['MEU-51 shared layout primitives AC-51.6 '] | PASS s31-70-green-rail-build | PASS s31-70-green-rail-e2e: 6 passed, env-bound tolerated: []","fresh":true}
```

```json
{"schema_version":"evidence.v1","check_id":"s31-70-green","command":"bash docs/execution/plans/2026-10-10-gui-polish-residuals/validate-task.sh green70","cwd":"/home/user/av-kit","scope":"UNIT69 + UNIT70 + EMPHASIS_TESTS + REGSET Vitest; build; Electron settings -g AC-70","phase":"targeted","exit_code":0,"result":"pass","tested_state":"row 7 (ACTIVE_SOURCE, SECTION_EMPHASIS)","output":"PASS s31-70-green: 96 passed of 97, env-bound tolerated: ['MEU-51 shared layout primitives AC-51.6 '] | PASS s31-70-green-build | PASS s31-70-green-e2e: 3 passed, env-bound tolerated: []","fresh":true}
```

```json
{"schema_version":"evidence.v1","check_id":"s31-70-gate","command":"bash docs/execution/plans/2026-10-10-gui-polish-residuals/validate-task.sh gate70","cwd":"/home/user/av-kit","scope":"ui typecheck, lint, UNIT69+UNIT70+UNIT70E+REGHDR+REGSET Vitest, ui build, harness build, Electron settings.test.ts, Electron console-chrome + command-palette-nav, repeat-each=20 over REPEAT_GREP","phase":"targeted","exit_code":0,"result":"pass","tested_state":"MEU-70 final working tree (c4d7953 + the AC-70.6 border poll)","output":"PASS s31-70-typecheck | PASS s31-70-lint | PASS s31-70-vitest: 188 passed of 189, env-bound tolerated: ['MEU-51 shared layout primitives AC-51.6 '] | PASS s31-70-build | PASS s31-70-harness-build | PASS s31-70-e2e: 12 passed, env-bound tolerated: [] | PASS s31-70-e2e-header: 12 passed, env-bound tolerated: [] | PASS repeat-each=20 70-settings (stats expected 140, unexpected 0, flaky 0)","fresh":true}
```

The first `gate70` run passed every stage except the repeat: 139 expected / **1 unexpected** / 0 flaky. The failure was AC-70.6 run 1 of 20: `expect(received).not.toContain(expected)`, with the left border colour read as `rgba(0, 0, 0, 0)`. The spec polled until the background colour differed, then read the border colour once. Both colours transition over `--duration-fast`, so that single read could land on the transition's first frame. The border read now polls like the background, with the assertion unchanged. The rerun above is the gate of record (140/0/0). The authoritative full gate is `WINDOWS_GATE` (H1-6).

### Quality Gate Results

```
ui typecheck: 0 errors
ui lint: 0
Vitest UNIT69 + UNIT70 + EMPHASIS_TESTS + REGHDR + REGSET: 188/189 (AC-51.6 env-bound)
ui build + harness build: pass
Electron settings.test.ts: 12 passed; console-chrome + command-palette-nav: 12 passed
repeat-each=20 (AC-69|AC-70|AC-58.12|A-6|C1-): 140 expected, 0 unexpected, 0 flaky
source audit (PREFIX_AUDIT): run over the full AUDIT_SRC in pregate (H1-2)
```

---

## Changed Files

| File | Action | Lines | Summary |
|------|--------|-------|---------|
| `ui/src/renderer/src/features/settings/settings-tail-spacer.ts` | new | 1–131 | `SECTION_SCROLL_MARGIN`, `tailSpacerHeight`, `belowLastTop`, `useTailSpacer` (applied height kept across effect restarts: execution review R1 F1) |
| `ui/src/renderer/src/features/settings/settings-section-frame.ts` | new | 1–30 | `SECTION_FRAME_BASE`, `sectionFrameProps` |
| `ui/src/renderer/src/features/settings/SettingsRail.tsx` | modified | +43/−5 | `SCROLL_RECHECK`, `onActiveChange`, `REVEAL_FALLBACK` |
| `ui/src/renderer/src/features/settings/SettingsPage.tsx` | modified | +23/−8 | `currentSection`, `current` on every frame, `sectionFrameProps` in `SettingsSectionFrame`, the spacer |
| `ui/src/renderer/src/features/settings/StartAtSignInControl.tsx` | modified | +5/−2 | optional `current`; spreads `sectionFrameProps` |
| `ui/tests/e2e/test-ids.ts` | modified | +3 | MEU-70 block |
| `ui/tests/unit/settings-tail-spacer.test.ts` | new | 1–82 | AC-70.1, AC-70.8 |
| `ui/tests/unit/settings-emphasis.test.tsx` | new | 1–250 | AC-70.5, AC-70.9 |
| `ui/tests/unit/settings-rail.test.tsx` | modified (append + `revealSection` import) | +303 | AC-70.3, AC-70.4, AC-70.10; A-3 heading case; R1 F1 spacer-restart case |
| `ui/tests/e2e/settings.test.ts` | modified (append only) | +213 | `windowSettled`, AC-70.2 ×2, AC-70.6 |

```diff
 const timer = window.setTimeout(() => {
-    const now = scroller !== null ? scroller.scrollTop : window.scrollY
-    if (now === start && target.isConnected) {
+    source.removeEventListener('scroll', onScroll)
+    if (!scrolled && target.isConnected) {
       target.scrollIntoView({ behavior: 'auto', block: 'start' })
```

```diff
+    const scrollSource: HTMLElement | Window = scroller ?? window
+    let frame = 0
+    function onScroll(): void {
+      if (frame !== 0) return
+      frame = window.requestAnimationFrame(() => {
+        frame = 0
+        if (Date.now() < clickLockUntil.current) return
+        const key = current()
+        if (key !== undefined) setActive(key)
+      })
+    }
+    scrollSource.addEventListener('scroll', onScroll, { passive: true })
```

```diff
-      className="flex scroll-mt-4 flex-col gap-3 outline-none"
+      {...sectionFrameProps(current)}
```

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
  - id: D-22
    stage: execution
    question: "The spacer made the existing AC-58.12 Electron spec fail deterministically (5/5): after a click on MCP access and a scroll back to the top, the page jumped back to MCP. How is it fixed?"
    resolution: autonomous
    class: two-way
    chosen: "Fix the latent race in revealSection's A-3 fallback: complete a smooth reveal only if the scroller emitted no scroll event (REVEAL_FALLBACK); add AC-70.10; AC-58.12 unchanged"
    source_tag: Local Canon
    precedents: ["docs/execution/plans/2026-09-30-tts-repair/human-gate-decision.md A-3 — the fallback exists for a smooth scroll a hidden/throttled window drops entirely", "docs/execution/plans/2026-09-30-tts-repair/human-gate-decision.md A-6 — the rail's click-path timing was fixed in product code, with AC-58.12 unchanged", "AGENTS §Testing & TDD — never weaken an existing assertion to get Green"]
    research: { engine: none, sources: [] }
    reasoning: "With the spacer, MCP enters the viewport earlier in its smooth scroll, so AC-58.12 scrolls back to 0 before the 450 ms fallback fires, and 'scrollTop equals its start' mistook 'moved and came back' for 'never moved'. Changing AC-58.12 would weaken an existing assertion and dropping the spacer would reverse D-9, so the only legitimate fix is detecting 'never started' by the absence of any scroll event, which keeps the A-3 jump. Recorded in implementation-plan.md §Execution Correction Notes."
```

---

## History

| Event | Date | Agent | Detail |
|-------|------|-------|--------|
| Created | 2026-10-11 | claude-code-web | Initial handoff after gate70 |
| Corrected | 2026-10-14 | claude-code | Execution review R1 F1: `useTailSpacer` keeps the applied spacer height in a ref across effect restarts; appended regression `settings-rail.test.tsx:765` |
