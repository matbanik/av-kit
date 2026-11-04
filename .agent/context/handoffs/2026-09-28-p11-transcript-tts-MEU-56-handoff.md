---
date: "2026-09-28"
project: "2026-09-28-p11-transcript-tts"
meu: "MEU-56"
status: "complete"
action_required: "VALIDATE_AND_APPROVE"
template_version: "2.2"
verbosity: "standard"
plan_source: "docs/execution/plans/2026-09-28-p11-transcript-tts/implementation-plan.md"
build_plan_section: "bp11 TTS page layout"
agent: "Claude Code (claude-opus-5-5)"
reviewer: "Fable 5.1 subagent (pending, H1-7)"
predecessor: "2026-09-28-p11-transcript-tts-MEU-55-handoff.md"
---

# Handoff: 2026-09-28-p11-transcript-tts-MEU-56-handoff

> **Status**: `complete` · **Action Required**: `VALIDATE_AND_APPROVE`

---

## Scope

**MEU**: MEU-56 — `gui-tts-layout`. The page is now a capped two-column grid (Text | Voice) that stacks text-first below 880 px, with a static run bar below it.

- **Text panel**: header with Load file and Paste; an 11-row resizable textarea; a stats footer; the `Cleanup · n of 11 steps` disclosure containing the humanized pipeline and side-by-side previews.
- **Voice panel**: the loaded-model `StatusChip`; the Manage disclosure (device, Unload, model rows, full details); Language; a one-line-per-voice `VOICE_LISTBOX`; the speed slider plus a native-radio preset segment; the native Format select.
- **Run bar**: output path, Browse, Generate, Cancel, the status pill, and the `RUN_BAR_SLOT` (error → segment progress → last output).

The inherited closed-MEU-48 AC is met: segment and download progress use the shared `ProgressBar`, and the page has no local bar and no `width:` style.

**Build Plan Section**: [Phase 11 TTS page layout](../../../docs/build-plan/11-page-layout.md#tts-page-layout) (TT1–TT7; Supersession "Closed MEU-48 TTS AC"); [Session 25 plan](../../../docs/execution/plans/2026-09-28-p11-transcript-tts/implementation-plan.md).

**Predecessor**: [MEU-55 handoff](2026-09-28-p11-transcript-tts-MEU-55-handoff.md).

**Boundary inventory**:
- Settings leaves (`input_text`, `voice`, `speed`, `output_format`, `output_path`, `device`) still go through `putSettings`, with the same keys and the same debounce.
- Prepare still sends `{ text, enabled_steps }` with raw step ids.
- Generate, Cancel and the model download/load/unload commands, plus the openPath/showItemInFolder/readTextFile/readClipboardText/showDirectoryDialog IPC, are unchanged.
- No API, IPC or persisted-mutation change. `git status -- packages/api` is empty.

---

## Acceptance Criteria

| AC | Type | Description | Source | Test(s) | Status |
|---|---|---|---|---|---|
| AC-56.1 | unit | `CLEANUP_LABELS` is an exhaustive `Record<PrepareStep,string>`; checkbox values stay raw step ids; labels are humanized. | Spec TT2; mockup §02 | `tts-page.behavior.test.ts:179` | ✅ |
| AC-56.2 | integration | Capped two-column grid (`minmax(0,1.45fr) minmax(300px,1fr)` ≥ 880 px, stacked below). Text panel labels the 11-row `resize-y` textarea. The Cleanup disclosure starts closed, its count tracks the steps, its toggle issues no request, and the hidden panel stays out of the tab order. Previews sit side by side; prepare keys are `{enabled_steps,text}`. | Spec canon §TTS; TT2; mockup §02/§04/§05 rows 1–10 | behavior `:195`; Electron `tts-generate.test.ts:407,429` | ✅ |
| AC-56.3 | integration | `loaded-model` chip shows `{catalog name} · {device}` (success) or `No model loaded` (warning). Manage starts closed; `loaded-model-details` keeps the full string; the model rows keep the get/load index rule; device PUTs `device`. A late status refetch updates the chip and never closes Manage (RULE-2). | Spec TT3; mockup §02/§05 rows 11–15; RULE-2 | behavior `:230`; Electron `:429` | ✅ |
| AC-56.4 | integration | `VOICE_LISTBOX`: role listbox/option, `aria-selected`, roving tabIndex. Arrows/Home/End move focus only; click/Enter/Space always PUT `voice` once, even when that voice is already selected. Speed slider keeps 0.5/2/0.1 with the `Speed x.x×` label; preset radios `speed-preset-*` PUT `speed`. Format stays a native select (MP3/WAV). No voice preview (TT6). Hydration never overwrites a user's earlier choice (RULE-2). | Spec TT1, TT6; mockup §02/§05 rows 16–21; UX1; G30; plan-review OQ-1 → A | behavior `:260,290,310`; Electron `:453` | ✅ |
| AC-56.5 | integration | Static run bar below the grid (not sticky). `RUN_BAR_SLOT`: error replaces the slot; while `RUN_ACTIVE`, the shared `ProgressBar` (`segment-progress-bar`) is shown with `Segments d/t · preview · hash`; when idle, `last-output` shows the path or `No output yet` (TT5). Open file and Open folder are mounted iff `OUTPUT_ACTIONABLE` (TT4). | Spec Supersession (MEU-48), TT4, TT5, TT7 | behavior `:334,362,375,401`; Electron `:479` | ✅ |
| AC-56.6 | integration | Real Electron wave: grid columns at the default size and stacked at 760 px; Cleanup count and panel; Manage and unload with the chip update; voice/preset/format PUT ledger; run-bar transitions idle → progress (`aria-valuenow` 50) → done output with open IPC → error. TA-6/TA-7 applied; all W2 tests stay active. | Local Canon AGENTS §Testing Requirements; E2 | `tts-generate.test.ts:407,429,453,479`; W2-1..W2-6 | ✅ |

<!-- CACHE BOUNDARY -->
<!-- Content above this line is stable across revision passes (KV cache prefix). -->
<!-- Content below this line changes between passes (evidence, results, corrections). -->

---

## Evidence

### FAIL_TO_PASS

| Test | Red Output (hash/snippet) | Green Output | File:Line |
|---|---|---|---|
| AC-56.1 | `expected [] to deeply equal [ 'all_caps', … ]` | pass | `tts-page.behavior.test.ts:179` |
| AC-56.2 | `Unable to find … role "region" and name "Text"` | pass | `:195` |
| AC-56.3 | `expected 'Loaded: kokoro-v1.0-onnx-fp16 (cuda) …' to be 'ONNX FP16 · cuda'` | pass | `:230` |
| AC-56.4 ×3 | `expected null to be 'listbox'`; `Unable to find … text: Speed 1.0×` / `Speed 0.8×` | pass | `:260,290,310` |
| AC-56.5 ×3 | `tts-run-bar.ts exists: expected [] to have a length of 1`; `Unable to find … segment-progress-bar`; `expected null to be 'alert'` | pass | `:334,375,401` |
| AC-56.6 Electron ×4 | `stats.unexpected = 4`, each an `expect(` failure | pass | `tts-generate.test.ts:407-479` |

`:362` (configured output makes the open buttons actionable while idle) passed in Red by design. It is today's behavior, which `OUTPUT_ACTIONABLE` preserves; its negative half (buttons absent when not actionable) is at `:334`.

**Setup-only test repairs made after Red** (no assertion was changed):
- The `tts-run-bar` import became `import.meta.glob`. A dynamic import of a missing module fails at collection under Vite; this follows the `queue-header-row.test.tsx` precedent.
- The new AC-56.6 locator became `getByLabel('Numbers', { exact: true })`, because substring matching also resolved "Page numbers".

### Commands Executed

| Command | Exit Code | Key Output |
|---|---|---|
| `bash …/validate-task.sh red-56` | 0 | `PASS AC-56 RED: 5 failing AC-56 assertions, 1 passing` (10 collected; 9 failed by assertion/element-not-found) |
| `bash …/validate-task.sh e2e-red-56` | 0 | `PASS AC-56 E2E RED: 4 failing AC-56 specs` |
| `bash …/validate-task.sh green-56` | 0 | `PASS s25-56-green-vitest: 74 passed, env-bound tolerated: [AC-51.6, AC-41.3]` |
| `bash …/validate-task.sh e2e-56` | 0 | `10 passed (1.5m)` (W2-5 35.3 s; W2-4 10.3 s) |
| `bash …/validate-task.sh static` | 0 | typecheck and lint pass, 0 warnings |
| `bash …/validate-task.sh amendments` | 0 | `PASS amendment guard` |

```json
{"schema_version":"evidence.v1","check_id":"s25-56-green","command":"bash docs/execution/plans/2026-09-28-p11-transcript-tts/validate-task.sh green-56","cwd":"/home/user/av-kit","scope":"UNIT56 + REG56 (tts-page.behavior, tts-page, layout-primitives, queue-primitives, help-card, queue-canon)","phase":"targeted","exit_code":0,"result":"pass","tested_state":"536494e + MEU-56 edits","output":"PASS s25-56-green-vitest: 74 passed, env-bound tolerated: ['MEU-51 shared layout primitives AC-51.6 ', 'Phase 10 queue-card canon (MEU-41) AC-41']","fresh":true}
```

```json
{"schema_version":"evidence.v1","check_id":"s25-56-e2e","command":"bash docs/execution/plans/2026-09-28-p11-transcript-tts/validate-task.sh e2e-56","cwd":"/home/user/av-kit","scope":"fresh ui build; real Electron under xvfb-run, ELECTRON_DISABLE_SANDBOX=1: tts-generate.test.ts","phase":"targeted","exit_code":0,"result":"pass","tested_state":"536494e + MEU-56 edits (after the exact-label locator repair)","output":"10 passed (1.5m) … PASS s25-56-e2e","fresh":true}
```

### Quality Gate Results

```
tsc --noEmit: 0 errors
eslint src/ tests/ --max-warnings 0: 0 problems
vitest (targeted MEU-56 set): 74 passed; 2 ENV_BOUND_TESTS tolerated with proven signatures
playwright (tts-generate): 10 passed
```

**Pre-existing flake**: the tooling check recorded one intermittent failure of TTS W2-4 (a hydration race). With `touched`-leaf hydration (AC-56.4, RULE-2), W2-4 has passed in both runs since. Two runs are not proof the flake is gone; the pre-gate and `WINDOWS_GATE` runs add evidence.

### WINDOWS_GATE (authoritative D6 fresh full gate)

Mat ran `validate-task.ps1 -Check windows-gate` in `P:/av-kit` on `7dab4d1` (clean tree, Node v24.19.0, `electron@42.9.3`, lockfile `A86D9A42…`). All 9 stages exited 0: npm-ci, ui-types, ui-lint, ui-tests, ui-build, ui-harness-build, ui-electron, source-audit, width-audit. Vitest 630/630, including AC-51.6 and AC-41.3 on Windows. Electron: 103 expected, 0 unexpected, 0 flaky, including AC-49.26 and the four capture-picker specs. `validate-task.sh windows-gate-check` then passed in the container against HEAD `e71395d`, with no code change since the tested commit.

```json
{"schema_version":"evidence.v1","check_id":"s25-windows-gate","command":"pwsh -NoProfile -File docs/execution/plans/2026-09-28-p11-transcript-tts/validate-task.ps1 -Check windows-gate; then bash docs/execution/plans/2026-09-28-p11-transcript-tts/validate-task.sh windows-gate-check","cwd":"P:/av-kit (Windows) / /home/user/av-kit (check)","scope":"PROFILE D6 UI fresh full gate: npm ci, typecheck, lint, full Vitest, build, isolated harness build, full real Electron, source and width audit","phase":"full","exit_code":0,"result":"pass","tested_state":"7dab4d153c60103de1d24257deaed4b52dcb9e16 (code-identical to e71395d)","output":"PASS windows gate @ 7dab4d153c60103de1d24257deaed4b52dcb9e16: vitest {'passed': 630, 'failed': 0, 'total': 630} e2e {'expected': 103, 'unexpected': 0, 'skipped': 0, 'flaky': 0}","fresh":true}
```

**Round 1 rerun (after `9fb0153`).** On `c315640` the first run failed at `ui-electron`: Capture W9-3 hit a 60 s test timeout plus a worker-teardown timeout, the test had no code overlap with this session, and the result was not pushed. Its `error-context.md` was lost to later single-spec reruns (see walkthrough). After a quiet-machine check, the second run passed all 9 stages: Vitest 631/631, Electron 103 expected, 0 unexpected, 0 flaky, with W9-3 at 22.5 s. It was pushed as `692b483`, and `windows-gate-check` passed against that HEAD. `692b483` differs from the tested commit only in the result file.

```json
{"schema_version":"evidence.v1","check_id":"s25-windows-gate-r1","command":"pwsh -NoProfile -File docs/execution/plans/2026-09-28-p11-transcript-tts/validate-task.ps1 -Check windows-gate; then bash docs/execution/plans/2026-09-28-p11-transcript-tts/validate-task.sh windows-gate-check","cwd":"P:/av-kit (Windows) / /home/user/av-kit (check)","scope":"PROFILE D6 UI fresh full gate after the Round 1 fix","phase":"full","exit_code":0,"result":"pass","tested_state":"c315640d05cc7ddf8293c8f0b64733c209bb0028 (code-identical to 692b483)","output":"PASS windows gate @ c315640d05cc7ddf8293c8f0b64733c209bb0028: vitest {'passed': 631, 'failed': 0, 'total': 631} e2e {'expected': 103, 'unexpected': 0, 'skipped': 0, 'flaky': 0}","fresh":true}
```

---

## Changed Files

| File | Action | Summary |
|---|---|---|
| `ui/src/renderer/src/features/tts/TTSPage.tsx` | modified | Grid, panels, disclosures, `VOICE_LISTBOX`, preset segment, run bar with `RUN_BAR_SLOT`; hydration skips user-touched leaves |
| `ui/src/renderer/src/features/tts/tts-prepare.ts` | modified | `CLEANUP_LABELS` |
| `ui/src/renderer/src/features/tts/tts-run-bar.ts` | new | `resolveRunBarSlot` (error → progress via `cancelEnabled` → output) |
| `ui/tests/unit/tts-page.behavior.test.ts` | new | AC-56.1–AC-56.5 |
| `ui/tests/e2e/tts-generate.test.ts` | modified | AC-56.6 cases; TA-6, TA-7 |
| `ui/tests/e2e/test-ids.ts` | modified | 8 additive IDs appended at the end |
| `ui/tests/unit/layout-primitives.test.ts` | modified | TA-1 (TTS half) |

```diff
-    if (typeof data.input_text === 'string') {
+    const fresh = (leaf: HydratedLeaf): boolean => !touched.current.has(leaf)
+    if (typeof data.input_text === 'string' && fresh('input_text')) {
       setText(data.input_text)
```

### TEST_AMENDMENTS applied (before → after)

| TA | Class | File:test | Before | After |
|---|---|---|---|---|
| TA-1 | D | `layout-primitives.test.ts` AC-51.7 | `['tts','TTSPage']` in the forbidden-import list | Removed; new assertion that `TTSPage` imports `Disclosure`, `SegmentedControl` and `StatusChip`. Capture and Settings stay forbidden. |
| TA-6 | A, B | `tts-generate.test.ts` W2-3 | `cleanup-pipeline`, `preview-cleanup-btn`, `model-manager` visible with no interaction; `segment-progress` `toBeAttached` at idle | Opens `cleanup-toggle` and `model-manage-toggle` first; at idle asserts `last-output` attached with `No output yet` (`RUN_BAR_SLOT`/TT5) |
| TA-7 | A, B | W2-4 | `preview-cleanup-btn` clicked directly; `last-output` visible right after Generate | Opens `cleanup-toggle` first. After Generate, asserts `segment-progress`, moves the seam job to Done with `page.evaluate` (the W2-5 pattern), then asserts `last-output`. The ledger assertions are unchanged. |
| TA-7 | A, B | W2-5 | `segment-progress` visible before Generate; `preview-cleanup-btn` and `model-get-btn` clicked directly | `cleanup-toggle` is opened before preview and `model-manage-toggle` before `model-get-btn`. `segment-progress` is asserted right after Generate (while `RUN_ACTIVE`). The ledger block at `:350-375` is byte-identical. |

---

## Codex Validation Report

The independent review is in `.agent/context/handoffs/2026-09-28-p11-transcript-tts-implementation-critical-review.md`, written by the Fable 5.1 subagent (`claude-fable-5-1-subagent`). Round 1 was `changes_required` (1 Medium, 1 Low; see Corrections Applied). Round 2 was `approved` with 0 blocking findings and one Low (F3). `validate-task.sh review-check … execution 6` passes. This section cites the reviewer's file; the coordinator authored no verdict.

---

## Deferred Items

None. F3 (see the MEU-55 handoff) concerns the Transcript page only.

---

## History

| Event | Date | Agent | Detail |
|---|---|---|---|
| Created | 2026-09-28 | Claude Code | MEU-56 Red → Green → targeted gate |
| Windows gate | 2026-09-28 | Mat (local agent) | `c315640`: run 1 W9-3 hang (not pushed); run 2 passed, result `692b483` |
| Approved | 2026-09-28 | claude-fable-5-1-subagent | Execution review Round 2 `approved`; MEU-56 set to `approved` in H2-2 |
