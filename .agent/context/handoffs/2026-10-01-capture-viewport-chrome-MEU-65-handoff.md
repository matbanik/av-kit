---
date: "2026-10-02"
project: "capture-viewport-chrome"
meu: "MEU-65"
status: "complete"
action_required: "VALIDATE_AND_APPROVE"
template_version: "2.2"
verbosity: "standard"
plan_source: "docs/execution/plans/2026-10-01-capture-viewport-chrome/implementation-plan.md"
build_plan_section: "bp09"
agent: "claude-code-web (Claude Opus 5.5)"
reviewer: "claude-fable-5-1-subagent (user-authorized, human-review-decision.md)"
predecessor: "none"
---

# Handoff: 2026-10-01-capture-viewport-chrome-MEU-65-handoff

> **Status**: `complete`
> **Action Required**: `VALIDATE_AND_APPROVE`

---

## Scope

**MEU**: MEU-65 — `gui-capture-toolbar-icons`.
- The Capture tools row becomes icon buttons. Select, Arrow, Box, Highlight, Text, Undo, Redo, Original and Annotated each show a lucide icon with `aria-label` and `title` set to the old visible name (`ICON_BUTTON_RULE`, `TOOLBAR_BUTTONS` in the new `capture-toolbar.ts`).
- The per-tool options move into a second row, `capture-chrome-options`, which shows exactly `optionGroups(tool, selected)` (`OPTIONS_BY_TOOL`). Highlight, and Select on a highlight, no longer show the Stroke field they never used.
- At the default window neither row scrolls horizontally (`NO_OVERFLOW`).
- The Capture header disclosure is an **Options** button: `secondary` fill, a leading `SlidersHorizontal` icon, and a trailing chevron that follows `aria-expanded` (`OPTIONS_TOGGLE`). The shared `Disclosure` gains three optional props with defaults equal to today (`DISCLOSURE_PROPS`).

**Build Plan Section**: `docs/build-plan/09-screenshot-capture.md` §Viewport toolbar icons and Options (09:613-623, matrix 9.10)
**Predecessor**: none (first MEU of Session 29). MEU-66 builds its zoom group into this toolbar.

---

## Acceptance Criteria

| AC | Type | Description | Source | Test(s) | Status |
|----|------|-------------|--------|---------|--------|
| AC-65.1 | unit | `TOOLBAR_BUTTONS` complete and typed (every `CaptureTool` once, unique ids, non-empty names); `optionGroups` implements `OPTIONS_BY_TOOL` for every tool × selection ∈ {none, arrow, rect, highlight, text} | Spec 09:619-620; D-11, D-12 | `ui/tests/unit/capture-toolbar.test.ts` `AC-65.1 …` (3 tests) | ✅ |
| AC-65.2 | integration | jsdom page: each toolbar button in `capture-chrome-tools` resolves once by its name, has `aria-label` = `title` = name, no text node, an `aria-hidden` svg, `h-7`, `aria-pressed` on tools and view toggles; clicking keeps the handlers (tool, undo, redo) | Spec 09:619; Local Canon AC-57.5 | `ui/tests/unit/capture-page.behavior.test.ts` `AC-65.2 toolbar buttons are icon-only…`, `AC-65.2 icon buttons keep their handlers…`, `AC-65.2 negative: with no shot…` | ✅ |
| AC-65.3 | integration | jsdom page: `capture-chrome-options` renders exactly `optionGroups` for each tool, with no option control in the tools row and no toolbar button in the options row; stroke edits a selected arrow and font size edits a selected text mark from the options row | Spec 09:620, 09:623 | `capture-page.behavior.test.ts` `AC-65.3 the options row renders exactly OPTIONS_BY_TOOL…`, `AC-65.3 options keep their behavior…`, `AC-65.3 negative: Highlight shows no Stroke…` | ✅ |
| AC-65.4 | integration | Electron: `NO_OVERFLOW` for every tool and a selected text mark at `DEFAULT_WINDOW` after `WINDOW_SETTLED` | Spec 09:621 | `ui/tests/e2e/capture-inbox.test.ts` `AC-65.4 NO_OVERFLOW at the default window…` | ✅ |
| AC-65.5 | integration | jsdom + Electron: `OPTIONS_TOGGLE` — name "Options", `btn-secondary`, leading svg, chevron `data-state` follows `aria-expanded`, the panel toggles `hidden`; the AC-57.10 save case passes unchanged | Spec 09:622; Human-approved (triage D-16) | `capture-page.behavior.test.ts` `AC-65.5 the header toggle is an Options button…`; `capture-inbox.test.ts` `AC-65.5 header Options button…`; existing `AC-57.10 header…` | ✅ |
| AC-65.6 | unit | `DISCLOSURE_PROPS`: with no new props the render is unchanged (ghost, no svg, title-only text); with `variant`/`icon`/`chevron` they render | Local Canon AC-51.1; D-13 | `ui/tests/unit/layout-primitives.test.ts` `AC-65.6 …` (2 tests); existing AC-51.1/51.5/51.7 and the TTS `Cleanup · N of 11 steps` assertions unchanged | ✅ |
| AC-65.7 | unit | `NEW_TESTIDS` MEU-65 block registered after the MEU-51 marker; the source uses the ids | Local Canon AC-51.6 | `capture-toolbar.test.ts` `AC-65.7 …`; AC-51.6 prefix hash stays green under `vitest_env_ok` | ✅ |
| AC-65.8 | integration | Electron (A-5, after `CAPTURE_LOOK`): opening Options leaves the toggle in place (≤ 1 px) on the `capture-region` row; the panel opens under it | Human-approved A-5 | `ui/tests/e2e/capture-inbox.test.ts` `AC-65.8 opening the Options panel leaves the Options toggle in place…` | ✅ |

### Other plan AC references (not owned by MEU-65)

| AC | Owner | Status in MEU-65 |
|----|-------|------------------|
| AC-66.x | MEU-66 handoff | ⏳ rows 5–8 |
| AC-57.x, AC-59.x, AC-60.x, AC-39.x | existing Capture suites | pass unchanged (`TEST_AMENDMENTS` empty; walkthrough §Census) |
| AC-51.x | existing primitive suite | pass unchanged; AC-51.6 is a declared env-bound Vitest member |
| AC-41.x | existing queue-canon suite | untouched by MEU-65; AC-41.3 is a declared env-bound Vitest member |
| AC-50.x | existing layout-canon suite (AC-50.1/50.4 lock the 11-page-layout CP rows) | untouched by MEU-65; row 9 adds only a prose sentence and re-runs `layout-canon.test.ts` |

<!-- CACHE BOUNDARY -->

---

## Evidence

### FAIL_TO_PASS

| Test | Red Output (hash/snippet) | Green Output | File:Line |
|------|--------------------------|--------------|-----------|
| Electron AC-65.4 | `tool select at innerWidth 1280: capture-chrome-tools scrollWidth` — `expect(received).toBeLessThanOrEqual(expected)`, Expected `<= 836`, Received `1300` | pass | `ui/tests/e2e/capture-inbox.test.ts` (`AC-65.4`) |
| Electron AC-65.5 | `getByRole('button', { name: 'Options', exact: true })` Expected 1, Received 0 | pass | `capture-inbox.test.ts` (`AC-65.5`) |
| Vitest AC-65.2 | `capture-tool-select: expected null to be 'Select'`; no shot: `expected 'Select' to be ''` | pass | `ui/tests/unit/capture-page.behavior.test.ts` (`AC-65.2`) |
| Vitest AC-65.3 | `Unable to find an element by: [data-testid="capture-chrome-options"]` (×2); Highlight: `expected <input …> to be null` | pass | `capture-page.behavior.test.ts` (`AC-65.3`) |
| Vitest AC-65.5 | `Unable to find an accessible element with the role "button" and name "Options"` | pass | `capture-page.behavior.test.ts` (`AC-65.5`) |
| Vitest AC-65.6 | `expected 'inline-flex items-center justify-cent…' to contain 'btn-secondary'` | pass | `ui/tests/unit/layout-primitives.test.ts` (`AC-65.6`) |
| Vitest AC-65.1, AC-65.7 | suite load `Cannot find module '…/capture-toolbar'` (the declared new module) | pass | `ui/tests/unit/capture-toolbar.test.ts` |

The default-props AC-65.6 case passed at Red. It is a regression lock (the default render must not change). Every Red failure is listed with its disposition in [walkthrough.md](../../../docs/execution/plans/2026-10-01-capture-viewport-chrome/walkthrough.md) §MEU-65 Red. No existing test failed.

### Commands Executed

```json
{"schema_version":"evidence.v1","check_id":"s29-65-red","command":"bash docs/execution/plans/2026-10-01-capture-viewport-chrome/validate-task.sh red65","cwd":"/home/user/av-kit","scope":"UNIT65 Vitest (capture-toolbar, capture-page.behavior, layout-primitives), fresh build, Electron capture-inbox -g AC-65, require_failed_title AC-65.4 toBeLessThanOrEqual","phase":"targeted","exit_code":0,"result":"pass","tested_state":"baseline c169453 + MEU-65 tests and ids only; no MEU-65 production edit","output":"PASS AC-65 RED: 4 failing AC-65 assertions, 63 passing | PASS AC-65 E2E RED: 2 failing AC-65 specs | PASS AC-65.4 RED on toBeLessThanOrEqual","fresh":true}
```

```json
{"schema_version":"evidence.v1","check_id":"s29-65-green","command":"bash docs/execution/plans/2026-10-01-capture-viewport-chrome/validate-task.sh green65","cwd":"/home/user/av-kit","scope":"UNIT65 + REGCAP Vitest","phase":"targeted","exit_code":0,"result":"pass","tested_state":"MEU-65 final working tree","output":"PASS s29-65-green: 157 passed of 158, env-bound tolerated: ['MEU-51 shared layout primitives AC-51.6 ']","fresh":true}
```

```json
{"schema_version":"evidence.v1","check_id":"s29-65-gate","command":"bash docs/execution/plans/2026-10-01-capture-viewport-chrome/validate-task.sh gate65","cwd":"/home/user/av-kit","scope":"ui typecheck, lint, UNIT65+REGCAP Vitest, ui build, harness build, Electron capture-inbox (whole file), Electron layout-primitives + tts-generate (Disclosure neighbours), repeat-each=20 over REPEAT_GREP","phase":"targeted","exit_code":0,"result":"pass","tested_state":"MEU-65 final working tree (baseline c169453 + MEU-65 diff)","output":"PASS s29-65-typecheck | PASS s29-65-lint | PASS s29-65-vitest: 157 passed of 158, env-bound tolerated: ['MEU-51 shared layout primitives AC-51.6 '] | PASS s29-65-build | PASS s29-65-harness-build | PASS s29-65-e2e: 15 passed, env-bound tolerated: [] | PASS s29-65-e2e-disclosure: 15 passed, env-bound tolerated: [] | PASS repeat-each=20 65-capture (stats expected 160, unexpected 0, flaky 0)","fresh":true}
```

The authoritative full gate is `WINDOWS_GATE` (H1-6).

### Quality Gate Results

```
ui typecheck: 0 errors
ui lint: 0
Vitest UNIT65 + REGCAP: 157/158 (AC-51.6 env-bound)
ui build + harness build: pass
Electron capture-inbox: 15 passed; Disclosure neighbours (layout-primitives, tts-generate): 15 passed
repeat-each=20 (AC-65|AC-66|AC-59.12|AC-60.12|AC-57.10): 160 expected, 0 unexpected, 0 flaky
source audit (PREFIX_AUDIT over the four MEU-65 sources): 0 hits
```

---

## Changed Files

| File | Action | Lines | Summary |
|------|--------|-------|---------|
| `ui/src/renderer/src/features/capture/capture-toolbar.ts` | new | 1–83 | `TOOLBAR_BUTTONS` (keyed by test id), `TOOL_BUTTON_IDS` (`Record<CaptureTool, …>`), `optionGroups` (`OPTIONS_BY_TOOL`, exhaustive `switch` with `assertNever`) |
| `ui/src/renderer/src/features/capture/CaptureViewport.tsx` | modified | +203/−187 | `ToolbarIconButton` (`ICON_BUTTON_RULE`); the tools row holds the tool, History and View groups; the new `capture-chrome-options` row renders the color, text or stroke group per `optionGroups`; the hex field is `w-24 font-mono` |
| `ui/src/renderer/src/features/capture/CapturePage.tsx` | modified | +5/−1 | header `Disclosure` → `OPTIONS_TOGGLE` |
| `ui/src/renderer/src/components/ui/Disclosure.tsx` | modified | +16/−3 | optional `variant` (default `ghost`), `icon`, `chevron` (id + `-chevron` wrapper with `data-state`) |
| `ui/tests/e2e/test-ids.ts` | modified | +5 | MEU-65 block after the MEU-51 marker |
| `ui/tests/unit/capture-toolbar.test.ts` | new | — | AC-65.1, AC-65.7 |
| `ui/tests/unit/capture-page.behavior.test.ts` | modified (append; `within` import) | +185/−1 | AC-65.2, AC-65.3, AC-65.5 |
| `ui/tests/unit/layout-primitives.test.ts` | modified (append) | +41 | AC-65.6 |
| `ui/tests/e2e/capture-inbox.test.ts` | modified (append + `sampleShot` optional size) | +142/−3 | `windowSettled` (copied), AC-65.4, AC-65.5 |

```diff
-        <Disclosure
-          id="capture-settings"
-          title="Settings"
+        <Disclosure
+          id="capture-settings"
+          title="Options"
+          variant="secondary"
+          icon={<SlidersHorizontal size={16} aria-hidden="true" />}
+          chevron
```

```tsx
// capture-toolbar.ts — OPTIONS_BY_TOOL
export function optionGroups(tool: CaptureTool, selected: Annotation | null): readonly OptionGroup[] {
  if (tool === 'text' || selected?.type === 'text') {
    return ['color', 'text']
  }
  return strokeApplies(tool, selected) ? ['color', 'stroke'] : ['color']
}
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

## Corrections Applied (2026-10-02, after WINDOWS_GATE attempt 1 and CAPTURE_LOOK)

**Findings resolved**: 1/1 MEU-65 item (Mat's observation 1; A-5).

| # | Finding | Fix Applied | Verification |
|---|---------|-------------|--------------|
| 1 | Opening Options moved the toggle from the header row onto its own line (Red: `toggle top` moved 48 px) | `CapturePage.tsx`: the Disclosure section is `flex min-w-0 flex-1 flex-col items-end gap-2` (was `ml-auto …`), so it never wraps; the panel opens under the toggle | AC-65.8 Electron passes; the AC-57 header specs pass unchanged |

## Deferred Items

None.

---

## Decision Log

```yaml
decision_log:
  - id: D-23
    stage: execution
    question: "How does the icon table stay single-source while AC-39.8 reads the literal tool, undo and redo ids from CaptureViewport.tsx?"
    resolution: autonomous
    class: two-way
    chosen: "TOOLBAR_BUTTONS is keyed by test id; CaptureViewport renders <ToolbarIconButton id=\"capture-tool-arrow\" …>, which looks up the icon and name, so each literal id stays in the viewport source and a typo is a type error"
    source_tag: Local Canon
    precedents: ["ui/tests/unit/capture-page.test.ts AC-39.8 — toContain('capture-tool-arrow') … over CaptureViewport.tsx", "Session 27 MEU-63 handoff D-27 — literal ids kept where a pinned source test reads them"]
    research: { engine: none, sources: [] }
    reasoning: "Rendering the buttons by iterating the table would remove the literals, so AC-39.8 would fail and need an unplanned test amendment. TEST_AMENDMENTS is empty. A key lookup keeps one table for icons and names and keeps the literals."
  - id: D-24
    stage: execution
    question: "Where does the capture-settings-chevron test id come from, given DISCLOSURE_PROPS adds only variant, icon and chevron?"
    resolution: autonomous
    class: two-way
    chosen: "Disclosure derives the wrapper id as id + `-chevron`; Capture's id is capture-settings. AC-65.7 checks the registry, the derivation and the Capture id instead of a literal in the source"
    source_tag: Local Canon
    precedents: ["implementation-plan.md DISCLOSURE_PROPS — three optional props, chevron?: boolean", "ui/src/renderer/src/components/ui/Disclosure.tsx — panel id is already derived as id + `-panel`"]
    research: { engine: none, sources: [] }
    reasoning: "A fourth prop for the chevron's test id would go beyond the planned prop set. The panel id is already derived from id, so deriving the chevron id the same way keeps the primitive's convention."
  - id: D-25
    stage: execution
    question: "How are Undo/Redo and Original/Annotated grouped in the icon row, and what title does an enabled tool carry?"
    resolution: autonomous
    class: two-way
    chosen: "role=group segments labelled History and View, next to the existing Annotation tool group; an enabled button's title is its name, a tool disabled for lack of a shot keeps NO_SHOT_HINT"
    source_tag: Local Canon
    precedents: [".agent/docs/emerging-standards.md UX1 — role=group segmented buttons", "implementation-plan.md ICON_BUTTON_RULE — title is the accessible name except the no-shot hint"]
    research: { engine: none, sources: [] }
    reasoning: "Icon-only buttons need a tooltip (spec 09:619). Labelled groups tell screen-reader users how the icons cluster, without role=toolbar's arrow-key contract (D-10)."
```

---

## History

| Event | Date | Agent | Detail |
|-------|------|-------|--------|
| Created | 2026-10-02 | claude-code-web | Initial handoff after gate65 |
