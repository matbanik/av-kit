---
date: "2026-09-30"
project: "tts-repair"
meu: "MEU-64"
status: "complete"
action_required: "VALIDATE_AND_APPROVE"
template_version: "2.2"
verbosity: "standard"
plan_source: "docs/execution/plans/2026-09-30-tts-repair/implementation-plan.md"
build_plan_section: "bp11"
agent: "claude-code-web (Claude Opus 5.5)"
reviewer: "claude-fable-5-1-subagent (user-authorized, human-review-decision.md)"
predecessor: ".agent/context/handoffs/2026-09-30-tts-repair-MEU-63-handoff.md"
---

# Handoff: 2026-09-30-tts-repair-MEU-64-handoff

> **Status**: `complete`
> **Action Required**: `VALIDATE_AND_APPROVE`

---

## Scope

**MEU**: MEU-64 — `gui-tts-text-panel`.
- **Cleanup panel.** It gains **Apply cleanup**, which replaces the text with the cleaned text and persists it. The raw preview pane is removed. The cleaned preview mounts only after a successful Preview, and unmounts on any text change or Apply.
- **Voice picker.** The always-open voice listbox becomes a searchable `VoiceCombobox` (WAI-ARIA APG combobox with a listbox popup):
  - options grouped by language;
  - the language select in the popup header;
  - a selection chip.

  At the default window, Speed and Format now sit above the fold (LOCAL_REPRO R5).

**Build Plan Section**: `docs/build-plan/11-page-layout.md` §TTS text panel (residual), 11:121–125
**Predecessor**: MEU-63

---

## Acceptance Criteria

| AC | Type | Description | Source | Test(s) | Status |
|----|------|-------------|--------|---------|--------|
| AC-64.1 | integration | `apply-cleanup-btn` → `POST /tts/prepare` (text, steps, `chunk_max_chars`). On success the textarea takes `cleaned_text`, marks `input_text` touched, sends the debounced `PUT {input_text}` once, and clears the preview. It is disabled for blank text. On failure the text is unchanged, there is no PUT, and `error-banner` shows the message. | Human-approved 11:121 | `ui/tests/unit/tts-page.behavior.test.ts` `AC-64.1 Apply cleanup…`, `AC-64.1 a failed prepare…` | ✅ |
| AC-64.2 | integration | No `preview-raw`. `preview-cleaned` mounts after a successful Preview and unmounts on a text edit or Apply. | Human-approved 11:122 | `AC-64.2 the cleaned preview unmounts…`; `AC-56.2` (TA-2); `AC-64.1` | ✅ |
| AC-64.3 | unit | Preview and Apply are `secondary` buttons, never `ghost` | Local Canon G30 | `ui/tests/unit/tts-page.test.ts` `AC-64.3 …` | ✅ |
| AC-64.4 | integration | APG combobox: `voice-combobox` (`role=combobox`, `aria-expanded`, `aria-controls`, `aria-activedescendant`). Popup `voice-grid` listbox with `role=group` per language and `voice-card` options. Typing filters by id, description or language; ArrowDown/Up, Home/End and Enter select → PUT; Escape closes without a change; `voice-selected-chip`; "No voices match". | Research-backed 11:123 (APG) | `AC-64.4 …` ×2 (behavior); `ui/tests/unit/voice-combobox.test.tsx` (AC-64.4 ×6); Electron `AC-64.4 voice combobox…` | ✅ |
| AC-64.5 | integration | `language-select` in the open popup's header ANDs with the query and keeps "All". French + `am_` → 0 options and the empty state. | D-16 | `AC-64.5 …` (behavior, `voice-combobox.test.tsx`) | ✅ |
| AC-64.6 | integration | At `DEFAULT_WINDOW`, with `VOICE_CATALOG_FIXTURE` (54 voices) and the combobox closed, the bottoms of `speed-slider` and `format-select` are ≤ `innerHeight` with scroll tops at 0. The bounding-box expects come first. | Spec 11:124 | Electron `AC-64.6 Speed and Format are visible…` (`require_failed_title … toBeLessThanOrEqual` proved Red) | ✅ |

### Other plan AC references (not owned by MEU-64)

Listed so no AC is silently dropped (C4):

| AC | Owner | Status in MEU-64 |
|----|-------|------------------|
| AC-62.x | MEU-62 handoff | backend and Settings; untouched by MEU-64 |
| AC-63.x | MEU-63 handoff | the MEU-63 specs still pass. The TA-5 setup now waits on the chip, and the chip waits for the catalog (walkthrough §MEU-64). |
| AC-56.x | existing TTS page tests | TA-2 (AC-56.2), TA-5 (setup), TA-6 (AC-56.4 ×2); Electron TA-7 at W2-3, W2-5 and the AC-56.6 voice-list spec |
| AC-2.x, AC-9.x, AC-41.x, AC-50.x | existing suites | untouched by MEU-64 (AC-41.3 is env-bound; the AC-50.4 mockup lock is re-run at row 13) |

<!-- CACHE BOUNDARY -->

---

## Evidence

### FAIL_TO_PASS

| Test | Red Output (hash/snippet) | Green Output | File:Line |
|------|--------------------------|--------------|-----------|
| Electron AC-64.6 | first `expect`: the `speed-slider` bottom `toBeLessThanOrEqual(innerHeight)` fails on the unchanged layout (`require_failed_title` PASS) | pass | `ui/tests/e2e/tts-generate.test.ts:595` |
| Electron AC-64.4 | `toHaveAttribute('role', 'combobox')` — element(s) not found | pass | `ui/tests/e2e/tts-generate.test.ts:632` |
| Vitest AC-64.3 | `apply-cleanup-btn: expected -1 to be greater than -1` | pass | `ui/tests/unit/tts-page.test.ts:421` |
| Vitest AC-22.6 (TA-1) | `expected '…' not to contain 'preview-raw'` | pass | `ui/tests/unit/tts-page.test.ts:167` |
| Vitest AC-64.1/64.2/64.4/64.5 (behavior) | `Unable to find an element by: [data-testid="voice-selected-chip"]` (TA-5 setup) | pass | `tts-page.behavior.test.ts:590-710` |
| Vitest `voice-combobox.test.tsx` | `Failed to resolve import "…/VoiceCombobox"` (new-file allowance) | 7 passed | `ui/tests/unit/voice-combobox.test.tsx` |

The full disposition is in walkthrough §MEU-64 Red disposition. That section also lists the two Green-time test-setup corrections (neither changes an asserted expectation) and the chip adjustment.

### Commands Executed

```json
{"schema_version":"evidence.v1","check_id":"s27-64-red","command":"bash docs/execution/plans/2026-09-30-tts-repair/validate-task.sh red64","cwd":"/home/user/av-kit","scope":"UNIT64 Vitest (+ voice-combobox.test.tsx new), voice-fixture parity, Electron tts-generate -g AC-64, require_failed_title AC-64.6","phase":"targeted","exit_code":0,"result":"pass","tested_state":"8311060 (MEU-63) + MEU-64 tests and ids only; no MEU-64 production edit","output":"PASS AC-64 RED: 1 failing AC-64 assertions, 23 passing; other failing: [TA-5 setup x22, AC-22.6 TA-1] | PASS AC-64 E2E RED: 2 failing AC-64 specs | PASS AC-64.6 RED on toBeLessThanOrEqual","fresh":true}
```

```json
{"schema_version":"evidence.v1","check_id":"s27-64-green","command":"bash docs/execution/plans/2026-09-30-tts-repair/validate-task.sh green64","cwd":"/home/user/av-kit","scope":"UNIT64 + REGTTS Vitest","phase":"targeted","exit_code":0,"result":"pass","tested_state":"f3982a6 (MEU-64 final tree)","output":"PASS s27-64-green: 99 passed of 100, env-bound tolerated: ['MEU-51 shared layout primitives AC-51.6 ']","fresh":true}
```

```json
{"schema_version":"evidence.v1","check_id":"s27-64-gate","command":"bash docs/execution/plans/2026-09-30-tts-repair/validate-task.sh gate64","cwd":"/home/user/av-kit","scope":"ui typecheck, lint, UNIT64 + tts-run-bar + REGTTS Vitest, ui build, Electron tts-generate, repeat-each=20","phase":"targeted","exit_code":0,"result":"pass","tested_state":"f3982a6 (MEU-64 final tree)","output":"PASS s27-64-typecheck | PASS s27-64-lint | PASS s27-64-vitest: 103 passed of 104, env-bound tolerated: AC-51.6 | PASS s27-64-build | PASS s27-64-e2e: 14 passed, env-bound tolerated: [] | PASS repeat-each=20 64-tts","fresh":true}
```

The authoritative full gate is `WINDOWS_GATE` (H1-6).

### Quality Gate Results

```
ui typecheck: 0 errors
ui lint (eslint --max-warnings 0): 0
Vitest UNIT64 + tts-run-bar + REGTTS: 103/104 (AC-51.6 env-bound)
ui build: pass
Electron tts-generate: 14 passed; repeat-each=20: 280/280
```

---

## Changed Files

| File | Action | Lines | Summary |
|------|--------|-------|---------|
| `ui/src/renderer/src/features/tts/VoiceCombobox.tsx` | new | 1–284 | APG combobox + listbox popup; language groups; language select in the header; roving focus on options; the page passes its test ids |
| `ui/src/renderer/src/features/tts/tts-voices.ts` | modified | +32 | `matchVoices` (query AND language), `groupVoices` (catalog order) |
| `ui/src/renderer/src/features/tts/TTSPage.tsx` | modified | +40/−125 | Apply cleanup; conditional `preview-cleaned`; one `replaceText` path that drops a stale preview; `VoiceCombobox` replaces the language select and listbox |
| `ui/tests/e2e/test-ids.ts` | modified | +5 | MEU-64 block, appended. `PREVIEW_RAW` stays in the registry: AC-51.6 pins the registry's exact prior prefix, so ids are only appended. The element is gone from the page, and TA-1 asserts that. |
| `ui/tests/unit/voice-combobox.test.tsx` | new | 1–179 | AC-64.4/64.5 in isolation |
| `ui/tests/unit/tts-page.behavior.test.ts`, `tts-page.test.ts` | modified | — | TA-1, TA-2, TA-5, TA-6; AC-64.1–64.5 |
| `ui/tests/e2e/tts-generate.test.ts` | modified | — | `installTtsSeam(page, {voices})` (setup); TA-7 ×3; AC-64.6, AC-64.4 |

```tsx
// TTSPage.tsx — every text source goes through one path, so a stale preview never survives
function replaceText(next: string, kind: 'inline' | 'file', path: string | null): void {
  setText(next)
  setSourceKind(kind)
  setSourcePath(path)
  setPreviewCleaned(null)
  scheduleInputText(next)
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

## Deferred Items

None.

---

## Decision Log

```yaml
decision_log:
  - id: D-29
    stage: execution
    question: "The plan says the combobox matches voice_id / name / language, but VoiceOut on the wire has no `name`. What is matched, and in what order are groups and languages shown?"
    resolution: autonomous
    class: two-way
    chosen: "Match voice_id, style_description (the voice's display name, e.g. 'bella') and language. Groups and the popup's language options follow catalog order."
    source_tag: Local Canon
    precedents: ["ui/src/renderer/src/features/tts/tts-voices.ts VoiceOut (voice_id, language, gender, style_description)", "tts-page.behavior.test.ts AC-56.4 — option order af_heart, af_bella, bf_emma (catalog order)"]
    research: { engine: none, sources: [] }
    reasoning: "style_description is what the options display as the name. With catalog order, the arrow-key order, the group order and the language select all agree, and the AC-56.4 option order is unchanged. The Settings-era uniqueLanguages (sorted) stays for its existing callers."
  - id: D-30
    stage: execution
    question: "Where do the combobox's registered test ids live?"
    resolution: autonomous
    class: two-way
    chosen: "TTSPage passes `testIds` to VoiceCombobox (input, chip, list, option, language)"
    source_tag: Local Canon
    precedents: ["ui/tests/unit/tts-page.test.ts AC-22.22 — every Wave 2 id (voice-grid, language-select) must appear in TTSPage.tsx", "components/ui/Disclosure.tsx, StatusChip.tsx — testId props"]
    research: { engine: none, sources: [] }
    reasoning: "It keeps the pinned source test unamended and follows the repo's testId-prop idiom. The page stays the single owner of its registered ids."
  - id: D-31
    stage: execution
    question: "What does the selection chip show before the voice catalog loads?"
    resolution: autonomous
    class: two-way
    chosen: "'Loading voices…' until the catalog arrives; `id · description` for a catalog voice; the raw id if a stored voice is not in a loaded catalog"
    source_tag: Local Canon
    precedents: ["docs/build-plan/11-page-layout.md ST7 — never fabricate a state", "walkthrough §MEU-64 — the TA-5 setup wait raced the catalog when the chip echoed the setting"]
    research: { engine: none, sources: [] }
    reasoning: "The chip describes a catalog voice. Echoing the bare setting before the catalog loads implies a known voice, and it let the TA-5 setup pass before any data arrived."
  - id: D-32
    stage: execution
    question: "When does the voice popup close?"
    resolution: autonomous
    class: two-way
    chosen: "On Escape (in the input or on an option) or a pointer press outside the picker. Choosing a voice keeps it open. Closing resets the query and the active option."
    source_tag: Research-backed
    precedents: ["WAI-ARIA APG combobox (listbox popup) — Escape dismisses", "tts-page.behavior.test.ts AC-56.4 — several activations on the same open listbox"]
    research: { engine: none, sources: ["https://www.w3.org/WAI/ARIA/apg/patterns/combobox/"] }
    reasoning: "AC-56.4 activates several options on one open listbox, and the language select sits inside the popup, so closing on select or on blur would break both. The popup is absolutely positioned, so while it is open it overlays Speed/Format rather than pushing them down (AC-64.6 allows that)."
```

---

## History

| Event | Date | Agent | Detail |
|-------|------|-------|--------|
| Created | 2026-09-30 | claude-code-web | Initial handoff after gate64 |
