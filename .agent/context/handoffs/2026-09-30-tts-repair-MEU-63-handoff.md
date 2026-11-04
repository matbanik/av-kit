---
date: "2026-09-30"
project: "tts-repair"
meu: "MEU-63"
status: "complete"
action_required: "VALIDATE_AND_APPROVE"
template_version: "2.2"
verbosity: "standard"
plan_source: "docs/execution/plans/2026-09-30-tts-repair/implementation-plan.md"
build_plan_section: "bp11"
agent: "claude-code-web (Claude Opus 5.5)"
reviewer: "claude-fable-5-1-subagent (user-authorized, human-review-decision.md)"
predecessor: ".agent/context/handoffs/2026-09-30-tts-repair-MEU-62-handoff.md"
---

# Handoff: 2026-09-30-tts-repair-MEU-63-handoff

> **Status**: `complete`
> **Action Required**: `VALIDATE_AND_APPROVE`

---

## Scope

**MEU**: MEU-63 — `gui-tts-model-manager`. The Voice section's hidden "Manage" disclosure is replaced by an always-visible model block:
- a `model-select` picker listing every catalog variant with its state;
- one state-driven Get / Load / Unload button (`MODEL_ACTION`) and the device select, in one `model-row`;
- the MEU-62 readiness chips, each with a Get for a missing asset;
- download progress under the row.

"Model details" (`model-manage-toggle`) now discloses only the loaded-model details. The run bar shows `job.error_message` for a `Failed` job (`RUN_BAR_ERROR`), which closes the "Failed with no reason" half of LOCAL_REPRO R1.
**Build Plan Section**: `docs/build-plan/11-page-layout.md` §TTS model manager (residual), 11:107–111
**Predecessor**: MEU-62 (asset rows, `postDownloadAsset`, `tts-assets.ts`). D-18 = A (keep MEU-63 as scoped; walkthrough §LOCAL_REPRO R2).

---

## Acceptance Criteria

| AC | Type | Description | Source | Test(s) | Status |
|----|------|-------------|--------|---------|--------|
| AC-63.1 | integration | `model-select` lists every variant with `— not downloaded` / `— downloading N%` / `— downloaded` / `— loaded`. Default selection: the loaded variant → the first downloaded → the first. `device-select` is in `model-row`. | Human-approved 11:107; Local Canon G30 | `ui/tests/unit/tts-page.behavior.test.ts` `AC-63.1 model picker lists…`, `AC-63.1 default selection falls back…` | ✅ |
| AC-63.2 | integration | One primary button whose label and `data-testid` follow `MODEL_ACTION`: Get → `POST /models/download {variant_id}`, Load → `POST /models/load {variant_id, device}`, Unload → `POST /models/unload`. It reads "Getting…" while its variant downloads, and is disabled during any download. | Human-approved 11:108 | `AC-63.2 one state-driven action…`, `AC-63.2 the action is disabled while any download runs…` | ✅ |
| AC-63.3 | integration | `tts-asset-chip-<asset>` chips beside the picker come from `/health/dependencies`. A missing asset has a Get → `POST /models/download {asset}`. `download-progress(-bar)` sits under the row for variant or asset downloads. | Spec 11:109 | `AC-63.3 readiness chips beside the picker…` | ✅ |
| AC-63.4 | unit | `resolveRunBarSlot({error, status, jobError})` is `'error'` exactly when `RUN_BAR_ERROR` is set; a client error wins; an empty message or a non-Failed status never selects it | Spec 11:110 | `ui/tests/unit/tts-run-bar.test.ts` (4 × AC-63.4) | ✅ |
| AC-63.5 | integration | A Failed job's `error_message` shows in `error-banner`; a Done job with a stale message shows none | Spec 11:110; Local Canon G25 | `AC-63.5 a Failed job shows…` (jsdom); `ui/tests/e2e/tts-generate.test.ts` `AC-63.5 …` (Electron seam) | ✅ |
| AC-63.6 | integration | Test-ID migration as planned. Electron flow: select a not-downloaded variant → Get → progress → Load → Unload; the ledger shows each POST once, in order; a click on the disabled button adds nothing. | Spec 11:111 | `tts-generate.test.ts` `AC-63.6 picker flow…`; TA-4 in `W2-5` | ✅ |

### Other plan AC references (not owned by MEU-63)

Listed so no AC is silently dropped (C4):

| AC | Owner | Status in MEU-63 |
|----|-------|------------------|
| AC-62.x | MEU-62 handoff | ✅ approved-pending (predecessor); MEU-63 consumes `tts-assets.ts` and `postDownloadAsset` |
| AC-64.x | MEU-64 handoff | ⏳ rows 10–12 |
| AC-56.x | existing TTS page tests | AC-56.3 amended by **TA-3** only (single `model-row`, `model-select` → `model-get-btn`); the AC-56.6 Electron specs pass unchanged (`model-manager` still hidden until `model-manage-toggle`) |
| AC-2.x, AC-41.x, AC-50.x | existing suites | untouched by MEU-63; AC-41.3 is a declared env-bound Vitest member |
| AC-9.x | existing TTS model integration tests (AC-9.12 `huggingface_hub` confinement, AC-9.13 ONNX generate) | backend only; covered in the MEU-62 handoff, untouched by MEU-63 |

<!-- CACHE BOUNDARY -->

---

## Evidence

### FAIL_TO_PASS

| Test | Red Output (hash/snippet) | Green Output | File:Line |
|------|--------------------------|--------------|-----------|
| Vitest AC-63.4 | `AssertionError: expected 'output' to be 'error'` | pass | `ui/tests/unit/tts-run-bar.test.ts:6` |
| Vitest AC-63.1–63.3, 63.5 | `TestingLibraryElementError: Unable to find an element by: [data-testid="model-select"]` (AC-63.1 ×2, 63.2b); `Found multiple elements by: [data-testid="model-row"]` (AC-63.2a); `… "tts-asset-chip-tts_onnx_vocab"` (AC-63.3); `… "error-banner"` (AC-63.5) | pass | `ui/tests/unit/tts-page.behavior.test.ts:455-580` |
| Vitest AC-56.3 (TA-3) | `expected [ <div …(2)>…(3)</div>, …(1) ] to have a length of 1 but got 2` | pass | `tts-page.behavior.test.ts:276` |
| Electron AC-63.6 | `expect(locator).toContainText(expected) failed Locator: getByTestId('tts-asset-chip-tts_onnx_vocab') … element(s) not found` | pass | `ui/tests/e2e/tts-generate.test.ts:527` |
| Electron AC-63.5 | `expect(locator).toHaveText(expected) failed Locator: getByTestId('error-banner') Expected: "tts asset missing: tts_spacy_model"` | pass | `ui/tests/e2e/tts-generate.test.ts:566` |

Every Red failure is an assertion or a missing element. There are no suite-load or setup errors: `vitest_red` refuses collection errors, and `electron_red` refuses top-level errors. The six non-`AC-63.4` Vitest failures are the new MEU-63 specs plus the TA-3 site. The helper counts only messages containing "expected"/"assert" as decisive, so it lists element-not-found failures as "other". Each was inspected in `s27-63-red-vitest.json` (quoted above).

### Commands Executed

```json
{"schema_version":"evidence.v1","check_id":"s27-63-red","command":"bash docs/execution/plans/2026-09-30-tts-repair/validate-task.sh red63","cwd":"/home/user/av-kit","scope":"MEU-63 Vitest (UNIT63 + tts-run-bar.test.ts) and Electron tts-generate -g AC-63","phase":"targeted","exit_code":0,"result":"pass","tested_state":"607c801 (MEU-62) + MEU-63 tests and ids only; no MEU-63 production edit","output":"PASS AC-63 RED: 1 failing AC-63 assertions, 36 passing; other failing: [AC-56.3, AC-63.1 x2, AC-63.2 x2, AC-63.3, AC-63.5] | PASS AC-63 E2E RED: 2 failing AC-63 specs","fresh":true}
```

```json
{"schema_version":"evidence.v1","check_id":"s27-63-green","command":"bash docs/execution/plans/2026-09-30-tts-repair/validate-task.sh green63","cwd":"/home/user/av-kit","scope":"UNIT63 + REGTTS Vitest","phase":"targeted","exit_code":0,"result":"pass","tested_state":"d62d4a7 (MEU-63 final tree)","output":"PASS s27-63-green: 89 passed of 90, env-bound tolerated: ['MEU-51 shared layout primitives AC-51.6 ']","fresh":true}
```

```json
{"schema_version":"evidence.v1","check_id":"s27-63-gate","command":"bash docs/execution/plans/2026-09-30-tts-repair/validate-task.sh gate63","cwd":"/home/user/av-kit","scope":"ui typecheck, lint (--max-warnings 0), UNIT63+REGTTS Vitest, ui build, Electron tts-generate, repeat-each=20","phase":"targeted","exit_code":0,"result":"pass","tested_state":"d62d4a7 (MEU-63 final tree; gate started on the identical working tree)","output":"PASS s27-63-typecheck | PASS s27-63-lint | PASS s27-63-vitest: 89 passed of 90, env-bound tolerated: AC-51.6 | PASS s27-63-build | PASS s27-63-e2e: 12 passed, env-bound tolerated: [] | PASS repeat-each=20 63-tts","fresh":true}
```

The authoritative full gate is `WINDOWS_GATE` (H1-6).

### Quality Gate Results

```
ui typecheck: 0 errors
ui lint (eslint --max-warnings 0): 0
Vitest UNIT63 + REGTTS: 89/90 (AC-51.6 env-bound)
ui build: pass
Electron tts-generate: 12 passed; repeat-each=20: 240/240
```

---

## Changed Files

| File | Action | Lines | Summary |
|------|--------|-------|---------|
| `ui/src/renderer/src/features/tts/TTSPage.tsx` | modified | +170/−127 | model block (picker row, one action button, progress, chips, "Model details" panel); `RUN_BAR_ERROR` banner text; refetches the catalog and readiness rows when a download ends |
| `ui/src/renderer/src/features/tts/tts-controls.ts` | modified | +66 | `ModelAction`, `resolveModelAction`, `modelStateSuffix`, `defaultModelSelection` |
| `ui/src/renderer/src/features/tts/tts-run-bar.ts` | modified | +22/−4 | `runBarError` (`RUN_BAR_ERROR`); `resolveRunBarSlot` takes `jobError` |
| `ui/src/renderer/src/features/tts/useTtsJob.ts` | modified | +10 | `useTtsDependencies` (key shared with Settings); `DownloadRuntime.asset` |
| `ui/src/renderer/src/features/tts/tts-commands.ts` | modified | +2 | `postDownload` also refreshes `models/available` |
| `ui/tests/unit/tts-run-bar.test.ts` | new | 1–27 | AC-63.4 |
| `ui/tests/unit/tts-page.behavior.test.ts` | modified | — | setup-only harness routes; TA-3; AC-63.1/63.2/63.3/63.5 |
| `ui/tests/e2e/tts-generate.test.ts` | modified | — | setup-only seam state; TA-4 (W2-5); AC-63.6, AC-63.5 |
| `ui/tests/e2e/test-ids.ts` | modified | — | MEU-63 block (`MODEL_SELECT`, `TTS_ASSET_CHIP_*`), in the MEU-62 commit |

```tsx
// tts-controls.ts — MODEL_ACTION from the existing predicates
export function resolveModelAction(input: {
  isDownloaded: boolean
  loadedVariantId: string | null
  rowId: string
  runtimeState: string
}): { action: ModelAction; enabled: boolean } {
  const idle = input.runtimeState !== 'Downloading'
  if (input.loadedVariantId !== null && input.loadedVariantId === input.rowId) {
    return { action: 'unload', enabled: idle }
  }
  if (loadEnabled(input)) {
    return { action: 'load', enabled: idle }
  }
  return { action: 'get', enabled: getEnabled(input) }
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
  - id: D-19
    stage: execution
    question: "What does the kept `model-manager` test id mark once the picker and actions are no longer inside Manage?"
    resolution: autonomous
    class: two-way
    chosen: "`model-manager` is the 'Model details' panel (hidden until `model-manage-toggle`), holding `loaded-model-details`; the panel is a direct child of the model block, beside the picker row and the chips"
    source_tag: Local Canon
    precedents: ["implementation-plan.md §Test-ID migration (model-manager keep; loaded-model-details move into the disclosure)", "ui/tests/e2e/tts-generate.test.ts AC-56.6 — model-manager hidden until the toggle, visible after Unload"]
    research: { engine: none, sources: [] }
    reasoning: "It keeps every AC-56.6 Electron expectation unamended (hidden → toggle → visible), and the AC-63.3 jsdom check places the chips in the same block. The Disclosure primitive wraps its panel in its own section element, so the page renders the same native-button pattern (aria-controls/aria-expanded/hidden) inline, keeping the panel inside the model block."
  - id: D-27
    stage: execution
    question: "Where does the MODEL_ACTION → data-testid map live?"
    resolution: autonomous
    class: two-way
    chosen: "`MODEL_ACTION_TEST_IDS` is a constant in TTSPage.tsx; `resolveModelAction` stays pure in tts-controls.ts"
    source_tag: Local Canon
    precedents: ["ui/tests/unit/tts-page.test.ts AC-22.22 — every registered TTS id must appear in TTSPage.tsx"]
    research: { engine: none, sources: [] }
    reasoning: "The pinned source test reads TTSPage.tsx for `unload-btn`. Keeping the literal ids there satisfies it without an unplanned test amendment."
  - id: D-28
    stage: execution
    question: "How do the picker's `downloaded` state and the chips refresh after a background download ends?"
    resolution: autonomous
    class: two-way
    chosen: "TTSPage watches the runtime state; on Downloading → anything else it invalidates `models/available` and `health/dependencies`. `postDownload` also invalidates `models/available`."
    source_tag: Local Canon
    precedents: ["ui/src/renderer/src/features/tts/useTtsJob.ts useDownloadRuntime — 1 s poll while Downloading", "MEU-62 postDownloadAsset — invalidates runtime + dependencies"]
    research: { engine: none, sources: [] }
    reasoning: "The download worker runs after the 202, so only the runtime transition marks completion. Without the refresh, Get would stay on screen after a finished download until a manual reload."
```

---

## History

| Event | Date | Agent | Detail |
|-------|------|-------|--------|
| Created | 2026-09-30 | claude-code-web | Initial handoff after gate63 |
