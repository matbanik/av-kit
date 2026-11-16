---
date: "2026-11-15"
project: "2026-11-15-tts-page-polish"
meu: "MEU-150"
status: "complete"
action_required: "VALIDATE_AND_APPROVE"
template_version: "2.2"
verbosity: "standard"
plan_source: "docs/execution/plans/2026-11-15-tts-page-polish/implementation-plan.md"
build_plan_section: "bp03"
agent: "claude-code-local (Claude Opus 5.5)"
reviewer: "codex (H1-7 execution review)"
predecessor: "none (first MEU of Session 80)"
---

# Handoff: 2026-11-15-tts-page-polish-MEU-150-handoff

> **Status**: `complete`
> **Action Required**: `VALIDATE_AND_APPROVE`

---

## Scope

**MEU**: MEU-150 `svc-tts-output-names-progress` (issues `TTS-AUDIO-RANDOM-FILE-NAMES` and `TTS-SEGMENTS-LABEL-IS-PROGRESS-SCALE`, triage D-807). The TTS run bar shows a job's progress as a floored percentage and is labelled `Generation progress`, and the output names that rc.3 F5 shipped are pinned by guard tests.
**Build Plan Section**: [03 §TTS output names and progress (residual)](../../../docs/build-plan/03-service-layer.md#tts-output-names-progress-residual) (matrix 3.24), with the Delivered (Session 80) note at the end of that section.
**Successor**: MEU-149 (same session; `2026-11-15-tts-page-polish-MEU-149-handoff.md`).

- **NAME_SCHEME_KEPT (D-955, handed over).** The names were already fixed when the issue reached this session. Mat ruled the scheme in the rc.3 retest on 2026-11-09 ("first 3 words from the Text with dash followed by voice", "Lowercase slug (Recommended)"), and F5 shipped it as `output_stem(text, voice)` (`packages/core/src/avkit_core/domain/tts.py:369`). The 03 home section's `<job id>.wav` and `<job id>.mp3` wording was already out of date when the section was registered on 2026-11-15: it was copied from the issue's 2026-11-03 text, six days after F5. No Python product file changed. `domain/tts.py` and `services/tts.py` keep their row-0 bytes (H1-4, `readonly-check.txt`).
- **The guard tests (D-957, D-958).** `tests/unit/test_tts_output_name.py` gains AC-150.4 to AC-150.7. They lock in the safe-name rule (`NAME_SAFE_GUARD`), `speech` for text with no word, the collision rule (`NAME_COLLISION_GUARD`, `_free_paths` at `packages/core/src/avkit_core/services/tts.py:84`) and the legacy-file rule (`LEGACY_OUTPUT_KEPT`, the uuid4 job ID at `services/tts.py:257`). They passed when written: `tpp-150-guards.txt` reads `23 passed in 1.32s`.
- **PROGRESS_PERCENT (D-959, D-963).** `progressLabel` (`ui/src/renderer/src/features/tts/tts-controls.ts:38`) prints the 1000-step progress scale as a floored percentage, clamped to 0 to 100, and `0%` when the total is 0 or less or a value is not finite. `progressFraction` (`:52`) is that number over 100. The run bar prints `progressLabel` where it printed `Segments 250/1000` (`ui/src/renderer/src/features/tts/TTSPage.tsx:742`).
- **PROGRESS_ARIA (D-959, D-963).** The bar is labelled `Generation progress` and takes `progressFraction` as its value (`TTSPage.tsx:737-738`), so its `aria-valuenow` equals the label's number; at 999 of 1000 both say 99. `ProgressBar.tsx` is unchanged, and the test ids `segment-progress` and `segment-progress-bar` stay, because `ui/tests/e2e/tts-generate.test.ts` reads them.
- **API_SHAPE_UNCHANGED (D-962).** The API's `segments_done` and `segments_total` names stay. The gate's `openapi` step ran `export_openapi.py --check`, and H1-4 found no path under `packages/` or `mcp-server/` changed from its row-0 content.
- **Spec text and records (rows 6 and 7).** The 03 Delivered (Session 80) note; the two 06 wireframe strings and the `:1228` example; both issues resolved through the plan's `issue-resolve.py` (`tpp-issue-resolve.txt`: `issue-resolve: 0 problem(s)`); MEU-150 `ready_for_review` (`tpp-status-150.txt`).

**Residual risk for triage (plan §Out of Scope, D-957).** `_free_paths` checks that the WAV and MP3 names are free and then writes; it does not reserve the name with an exclusive create, as downloads do (`MP3_RESERVE`). The TTS service runs one job at a time, so no job of its own can take the name in between. Another program that creates the same name between the check and the write can still be overwritten. It is named here for the next triage.

**Plan:** [implementation-plan.md](../../../docs/execution/plans/2026-11-15-tts-page-polish/implementation-plan.md) §MEU-150. **Execution authorization:** `USER_EXPLICIT`, 2026-11-15, "proceed with planning and execution for P:\av-kit\.agent\context\grouping\2026-11-15-post-rc3-triage-residuals-session-grouping.md like we did here. But use the new HDP process. Continue orchestrating the sessions." The plan review approved at round 1 ([plan-critical-review.md](2026-11-15-tts-page-polish-plan-critical-review.md)); `plan_to_exec_gate: human`. The coordinator wrote these words into the plan's Status line (line 15) before row 0. That is a plan-text edit made after the plan was approved, so the reviewed plan hash no longer holds; line 15 is the only line that differs. It is disclosed here.

**Receipts.** A receipt named by its file name alone is in the session's receipts folder (`RECEIPTS_DIR`, the plan's `tts-page-polish` folder under it). Full paths appear only in the evidence records' `command` fields.

---

## Acceptance Criteria

| AC | Type | Description | Source | Test(s) | Status |
|----|------|-------------|--------|---------|--------|
| AC-150.1 | unit | `progressLabel` gives a floored percentage, clamped to 0 to 100, and `0%` for a total of 0 or less or a non-finite value; `progressFraction` gives the same number over 100 | Local Canon (03 §TTS output names and progress: Progress label; D-959, D-963) | `ui/tests/unit/tts-page.test.ts:429` | ✅ |
| AC-150.2 | unit | A Generating job at 250 of 1000 shows `25%`, then the preview and the hash, with neither `Segments` nor `/1000`; 0 of 1000 shows `0%`; the changed AC-56.5 (2 of 8) shows `25%` | Local Canon (03 Progress label; D-959) | `ui/tests/unit/tts-page.behavior.test.ts:469` | ✅ |
| AC-150.3 | unit | The bar has `aria-label="Generation progress"` and `role="progressbar"`, nothing is labelled `Segment progress`, and at 999 of 1000 `aria-valuenow` is `99` with the text `99%` | Local Canon (D-959, D-963) | `ui/tests/unit/tts-page.behavior.test.ts:490` | ✅ |
| AC-150.4 | unit | Text with reserved or control characters, `..\..\x`, a device name, or a trailing dot or space gives a stem with none of them, no `.`, no space and no device-name base; a generate from `..\..\escape` writes into `stack.root` | Local Canon (03 Safe; D-612); Research-backed (Microsoft Learn, "Naming files, paths, and namespaces"; D-958) | `tests/unit/test_tts_output_name.py:122` | ✅ |
| AC-150.5 | unit | A generate from forbidden characters only writes `speech-am_eric.mp3` | Local Canon (rc.3 F5) | `tests/unit/test_tts_output_name.py:136` | ✅ |
| AC-150.6 | unit | With the user's own `hello-world-again-am_eric.mp3`, or a lone `.wav` of that stem, a generate writes `-2` and the user's file keeps its bytes | Local Canon (03 Name; D-666; D-957) | `tests/unit/test_tts_output_name.py:143` | ✅ |
| AC-150.7 | unit | A legacy `<uuid4>.mp3` keeps its name and bytes; the new job's `id` is a version-4 UUID and its `output_path` is the stem-named file | Local Canon (03 Job) | `tests/unit/test_tts_output_name.py:156` | ✅ |
| AC-150.8 | contract | `export_openapi.py --check openapi.committed.json` exits 0, and no path under `packages/` or `mcp-server/` changes from its row-0 content | Local Canon (03 Job; D-962) | gate step `openapi` (`tpp-D6-openapi.txt`); H1-4 `readonly-check.py` (`readonly-check.txt`) | ✅ |
| AC-150.9 | docs | 03 (CRLF, kept) holds one Delivered (Session 80) note in its home section that says the uuid wording was already out of date; the 06 wireframe's run bar and output lines and the `:1228` example are redrawn at the same length | Local Canon (D-955, D-959) | row 6 check (`tpp-row6-check.txt`) | ✅ |
| AC-56.5 (cross-ref) | changed test | `AC-56.5 generating shows the shared ProgressBar in the slot, then output on completion`: `:435` now expects `25%`, and the next line expects no `Segments`. The fixture and every other line stay; named in the plan's §Existing test assertions that change | MEU-56 | `ui/tests/unit/tts-page.behavior.test.ts:425` | ✅ |
| AC-22.10 (cross-ref) | guard | `AC-22.10 SEGMENT progress binds segments_done and segments_total` passes unchanged, because the page still reads both API fields (D-962) | MEU-22 | `ui/tests/unit/tts-page.test.ts:230` | ✅ |
| AC-149 (sibling) | sibling MEU | AC-149.1, AC-149.2, AC-149.3, AC-149.4, AC-149.5, AC-149.6, AC-149.7, AC-149.8: the status pill, evidenced in the MEU-149 handoff, which also carries the AC-22.24 (shaped on AC-45.12), AC-43.2, AC-43.3, AC-43.5 and AC-51.3 cross-references | MEU-149 | `2026-11-15-tts-page-polish-MEU-149-handoff.md` | ✅ |

<!-- CACHE BOUNDARY -->

---

## Evidence

### FAIL_TO_PASS

| Test | Red Output (hash/snippet) | Green Output | File:Line |
|------|---------------------------|--------------|-----------|
| AC-150.1 | `AssertionError: expected 'undefined' to be 'function'` (`tpp-150-red.txt`) | Row 2: pass (`tpp-150-green.txt`) | `tts-page.test.ts:429` |
| AC-150.2 | `AssertionError: expected 'Segments 0/1000 · Hello · abcdef01' to contain '0%'` | Row 2: pass | `tts-page.behavior.test.ts:469` |
| AC-150.3 | `AssertionError: expected 'Segment progress' to be 'Generation progress'` | Row 2: pass | `tts-page.behavior.test.ts:490` |
| AC-56.5 | `AssertionError: expected 'Segments 2/8 · Hello · abcdef01' to contain '25%'` | Row 2: pass | `tts-page.behavior.test.ts:425` |

- **Row 1 Red** (`tpp-150-red.txt`): `Test Files  2 failed (2)` and `Tests  4 failed | 57 passed (61)`, exit 1 (`tpp-150-red.txt.exit`). Each failure is an assertion; the new export is checked with `typeof` before it is called, so no case fails with a `TypeError`. `tpp-150-red-check.txt`: `red-check: 1 receipt(s), 4 required test(s), 0 problem(s)`.
- **PASS_TO_PASS, not FAIL_TO_PASS:** AC-150.4 to AC-150.7 guard behaviour that rc.3 shipped, so they passed when written (`tpp-150-guards.txt`: `23 passed in 1.32s`). A failure there would have been S7. AC-150.8 and AC-150.9 are checked by the gate, H1-4 and row 6, and have no Red.
- **Row 2 Green** (`tpp-150-green.txt`): `Test Files  3 passed (3)` and `Tests  65 passed (65)` over `tts-page.test.ts`, `tts-page.behavior.test.ts` and `tts-run-bar.test.ts`. `tpp-150-eol.txt`: `line-ending drift: []`.

### Commands Executed

```json
{"schema_version": "evidence.v1", "cwd": "P:/av-kit", "check_id": "tpp-0-baseline", "command": "pwsh -NoProfile -File C:/Temp/av-kit/tts-page-polish/run-row0.ps1 (task.md row 0's Validation cell: rtk proxy pwsh -NoProfile -File docs/execution/plans/2026-11-15-tts-page-polish/baseline.ps1 *> C:/Temp/av-kit/tts-page-polish/tpp-baseline.txt, with ELECTRON_RUN_AS_NODE unset); receipts tpp-baseline.txt, tpp-base-py.txt, tpp-base-ui.txt", "scope": "Row 0: baseline.sha, baseline-dirty.txt, baseline-scope.json, baseline-readonly.json and baseline-dirty-hashes.json; the row-0 copies in base/; the base Python and UI suites; the red-check, identity and dev-app-procs selftests", "phase": "static", "exit_code": 0, "result": "pass", "tested_state": "HEAD 771c279 (baseline.sha), before row 1", "output": "tpp-baseline.txt: dev-app-procs selftest: 0 failure(s); baseline: all steps exit 0. tpp-base-py.txt: 2993 passed, 37 warnings in 232.28s (0:03:52). tpp-base-ui.txt: Test Files  132 passed (132); Tests  1540 passed (1540)"}
```

```json
{"schema_version": "evidence.v1", "cwd": "P:/av-kit", "check_id": "tpp-1-red-150", "command": "pwsh -NoProfile -File C:/Temp/av-kit/tts-page-polish/run-row1.ps1 (task.md row 1's Validation cell: npm --prefix ui run test -- tests/unit/tts-page.test.ts tests/unit/tts-page.behavior.test.ts *> C:/Temp/av-kit/tts-page-polish/tpp-150-red.txt, its exit code to tpp-150-red.txt.exit, red-check.py --require AC-150.1 AC-150.2 AC-150.3 AC-56.5, then uv run pytest tests/unit/test_tts_output_name.py for the guards and the line-ending check); receipts tpp-150-red.txt, tpp-150-red-check.txt, tpp-150-guards.txt, tpp-150-red-eol.txt, tpp-s4-row1.txt", "scope": "MEU-150 Red: AC-150.1 to AC-150.3 and the changed AC-56.5 against the row-0 product code; the guards AC-150.4 to AC-150.7 written and run once, expecting a pass", "phase": "red", "exit_code": 0, "result": "pass", "tested_state": "HEAD 771c279 (baseline.sha) plus rows 0 and 1", "output": "tpp-150-red.txt: Test Files  2 failed (2); Tests  4 failed | 57 passed (61); tpp-150-red.txt.exit 1. tpp-150-red-check.txt: red-check: 1 receipt(s), 4 required test(s), 0 problem(s). tpp-150-guards.txt: 23 passed in 1.32s. tpp-150-red-eol.txt: line-ending drift: []"}
```

```json
{"schema_version": "evidence.v1", "cwd": "P:/av-kit", "check_id": "tpp-2-green-150", "command": "pwsh -NoProfile -File C:/Temp/av-kit/tts-page-polish/run-row2.ps1 (task.md row 2's Validation cell: npm --prefix ui run test -- tests/unit/tts-page.test.ts tests/unit/tts-page.behavior.test.ts tests/unit/tts-run-bar.test.ts *> C:/Temp/av-kit/tts-page-polish/tpp-150-green.txt, then the line-ending check); receipts tpp-150-green.txt, tpp-150-eol.txt, tpp-s4-row2.txt", "scope": "MEU-150 Green: PROGRESS_PERCENT and PROGRESS_ARIA in tts-controls.ts and TTSPage.tsx", "phase": "green", "exit_code": 0, "result": "pass", "tested_state": "HEAD 771c279 (baseline.sha) plus rows 0 to 2", "output": "tpp-150-green.txt: Test Files  3 passed (3); Tests  65 passed (65). tpp-150-eol.txt: line-ending drift: []"}
```

```json
{"schema_version": "evidence.v1", "cwd": "P:/av-kit", "check_id": "tpp-6-notes", "command": "pwsh -NoProfile -File C:/Temp/av-kit/tts-page-polish/run-row6.ps1 (task.md row 6's Validation cell: the row-6 check of 03 and 06) *> C:/Temp/av-kit/tts-page-polish/tpp-row6-check.txt", "scope": "Row 6: the 03 and 06 Delivered (Session 80) notes, the two 06 wireframe strings and the :1228 example, CRLF kept", "phase": "static", "exit_code": 0, "result": "pass", "tested_state": "HEAD 771c279 (baseline.sha) plus rows 0 to 6", "output": "tpp-row6-check.txt: {'03 note once in home': True, '06 note once in home': True, '06 quotes Mat': True, 'bar redrawn': True, 'output redrawn': True, 'spec redrawn': True, '03 says stale': True, '03 CRLF': True, '06 CRLF': True}"}
```

```json
{"schema_version": "evidence.v1", "cwd": "P:/av-kit", "check_id": "tpp-7-close", "command": "pwsh -NoProfile -File C:/Temp/av-kit/tts-page-polish/run-row7.ps1 (task.md row 7's Validation cell: issue-resolve.py --issue TTS-AUDIO-RANDOM-FILE-NAMES --issue TTS-SEGMENTS-LABEL-IS-PROGRESS-SCALE --issue TTS-STATUS-PILL-BELOW-AA-CONTRAST --set-file C:/Temp/av-kit/tts-page-polish/issue-resolve-set.json --expect-sha256 <row-0 hash>, issue_triage.py render and render --check, meu_status.py update MEU-150 and MEU-149 ready_for_review, meu_status.py render, then the row-7 check); receipts tpp-issue-resolve.txt, tpp-issues-render.txt, tpp-issues-render-check.txt, tpp-status-150.txt, tpp-status-149.txt, tpp-status-render.txt, tpp-row7-check.txt, tpp-s4-row7.txt", "scope": "Row 7: the three issues resolved, both MEUs ready_for_review, grouping row 80 executed", "phase": "static", "exit_code": 0, "result": "pass", "tested_state": "HEAD 771c279 (baseline.sha) plus rows 0 to 7", "output": "tpp-issue-resolve.txt: issue-resolve: 0 problem(s); tpp-issues-render.txt: Rendered known-issues.md: 54 lines; tpp-issues-render-check.txt: OK: known-issues.md is up-to-date; tpp-status-150.txt and tpp-status-149.txt: Updated MEU-150 / MEU-149 -> ready_for_review (updated: 2026-11-16); tpp-status-render.txt: Loaded 153 MEUs across 12 phases; tpp-row7-check.txt: row 80: ['| 80 | `tts-page-polish` | MEU-149, MEU-150 | P3 | executed (Session 80) | `docs/execution/plans/2026-11-15-tts-page-polish/` |'] grouping LF: True"}
```

```json
{"schema_version": "evidence.v1", "cwd": "P:/av-kit", "check_id": "tpp-h1-1-unchecked", "command": "pwsh -NoProfile -File C:/Temp/av-kit/tts-page-polish/run-h1-1.ps1 (task.md H1-1's Validation cell) *> C:/Temp/av-kit/tts-page-polish/task-unchecked.txt", "scope": "H1-1: no implementation row of task.md is unchecked", "phase": "static", "exit_code": 0, "result": "pass", "tested_state": "HEAD 771c279 (baseline.sha) plus rows 0 to 7", "output": "task-unchecked.txt: unchecked implementation rows: []"}
```

```json
{"schema_version": "evidence.v1", "cwd": "P:/av-kit", "check_id": "tpp-gate-h1-2", "command": "pwsh -NoProfile -File C:/Temp/av-kit/tts-page-polish/run-h1-2.ps1 (task.md H1-2's Validation cell: rtk proxy pwsh -NoProfile -File docs/execution/plans/2026-11-15-tts-page-polish/session-gate.ps1 *> C:/Temp/av-kit/tts-page-polish/tpp-gate-h1.txt, with ELECTRON_RUN_AS_NODE unset); receipts tpp-gate-h1.txt and the tpp-D6-*.txt step receipts", "scope": "H1-2 session gate for MEU-150 and MEU-149: identity before and after; ruff check and format, pyright, the UI typecheck and lint, the task contract, scope paths, line endings, the red-check selftest; the TTS Python and UI targeted tests; the full Python suite, OpenAPI check, the full UI suite and build, the state and issue renders; the TTS Electron E2E", "phase": "full", "fresh": true, "snapshot": false, "exit_code": 0, "result": "pass", "tested_state": "771c279624d7b99aebab6285d945ca6317605486+945866edc3525f301997037c3f7885c4b75175fc2f1621ee6307c037296c362d", "output": "tpp-gate-h1.txt: session-gate: all steps exit 0; tested_state before = after (tpp-D6-identity-before.txt, tpp-D6-identity-after.txt). py-lint All checks passed!; py-format 1 file already formatted; py-types 0 errors, 0 warnings, 0 informations; ui-types tsc --noEmit exit 0; ui-lint eslint src/ tests/ --max-warnings 0 exit 0; task-contract OK: 25 row(s), 23 fully checked, 2 view_file exempt (H1-5, H2-1); scope-paths scope-check: ok (other-session-plan 8, plan-or-closeout 16, baseline-dirty-hashes checked 3); line-endings: 17 of 17 kept; red-check-selftest 64 fixture(s) (20 positive, 44 negative), 0 wrong; tts-py-targeted 61 passed in 11.74s; tts-ui-targeted Test Files  6 passed (6), Tests  104 passed (104); py-tests (tpp-D6-py-tests.txt) 3008 passed, 37 warnings in 221.84s (0:03:41); openapi exit 0; ui-tests Test Files  133 passed (133), Tests  1547 passed (1547); ui-build exit 0; state-render Drift check passed (153 MEUs, 12 phases); issues-render OK: known-issues.md is up-to-date; ui-electron (tpp-D6-ui-electron.txt) 23 passed (37.1s). Skipped: mcp-types/mcp-build/mcp-tests/mcp-audit (no MCP change; openapi pins the API shape, AC-150.8), build-record (no build)"}
```

```json
{"schema_version": "evidence.v1", "cwd": "P:/av-kit", "check_id": "tpp-h1-3-status", "command": "pwsh -NoProfile -File C:/Temp/av-kit/tts-page-polish/run-h1-3.ps1 (task.md H1-3's Validation cell: meu_status.py render --check, meu_status.py get MEU-150 and MEU-149, then the ready_for_review check); receipts tpp-render-check.txt, tpp-h13-status-150.txt, tpp-h13-status-149.txt, tpp-h13-check.txt", "scope": "H1-3: row 7's status writes hold, with no new write after the gate; the current-focus paragraph", "phase": "static", "exit_code": 0, "result": "pass", "tested_state": "the gate's tested_state (current-focus.md is an identity artifact)", "output": "tpp-render-check.txt: Drift check passed (153 MEUs, 12 phases); tpp-h13-status-150.txt and tpp-h13-status-149.txt: status ready_for_review; tpp-h13-check.txt: MEU-150 and MEU-149 ready_for_review: True. The Session 80 paragraph heads current-focus.md, which stays CRLF (188 CRLF, 0 bare LF)"}
```

```json
{"schema_version": "evidence.v1", "cwd": "P:/av-kit", "check_id": "tpp-h1-4-readonly", "command": "pwsh -NoProfile -File C:/Temp/av-kit/tts-page-polish/run-h1-4.ps1 (task.md H1-4's Validation cell: readonly-check.py) *> C:/Temp/av-kit/tts-page-polish/readonly-check.txt", "scope": "H1-4: the nine read-only files keep their row-0 SHA-256, and no path under packages/ or mcp-server/ changed (AC-150.8, AC-149.6)", "phase": "static", "exit_code": 0, "result": "pass", "tested_state": "the gate's tested_state", "output": "readonly-check.txt: read-only openapi.committed.json, domain/tts.py, services/tts.py, ProgressBar.tsx, StatusChip.tsx, status-tokens.ts, styles.css, ui/tests/e2e/test-ids.ts and ui/tests/e2e/tts-generate.test.ts each row-0 content; packages/ and mcp-server/: 0 listed now, 0 held from row 0; readonly-check: ok"}
```

### Quality Gate Results

- **Last line** (`tpp-gate-h1.txt`): `session-gate: all steps exit 0`.
- **Identity:** tested_state `771c279624d7b99aebab6285d945ca6317605486+945866edc3525f301997037c3f7885c4b75175fc2f1621ee6307c037296c362d` before and after the gate (`tpp-D6-identity-before.txt`, `tpp-D6-identity-after.txt`).
- **Static:** ruff check `All checks passed!`; ruff format `1 file already formatted`; pyright `0 errors, 0 warnings, 0 informations`; the UI typecheck and lint exit 0 (`tpp-D6-ui-types.txt`, `tpp-D6-ui-lint.txt`); the task contract `OK: 25 row(s)`, 23 fully checked, 2 view_file exempt (H1-5, H2-1); scope paths `scope-check: ok`; line endings `line-endings: 17 of 17 kept`; the red-check selftest `64 fixture(s) (20 positive, 44 negative), 0 wrong`.
- **Targeted:** the TTS Python tests `61 passed in 11.74s` with no skip (`tpp-D6-tts-py-targeted.txt`); the TTS UI tests `Test Files  6 passed (6)` and `Tests  104 passed (104)` (`tpp-D6-tts-ui-targeted.txt`).
- **Fresh full:** the Python suite `3008 passed, 37 warnings in 221.84s (0:03:41)` (`tpp-D6-py-tests.txt`), which is the row-0 base of 2993 (`tpp-base-py.txt`) plus the 15 AC-150.4 to AC-150.7 cases; the OpenAPI check exits 0 (`tpp-D6-openapi.txt`); the UI suite `Test Files  133 passed (133)` and `Tests  1547 passed (1547)` (`tpp-D6-ui-tests.txt`), which is the row-0 base of 1540 in 132 files (`tpp-base-ui.txt`) plus the 7 new tests and the new file; the UI build exits 0; the state render `Drift check passed` (153 MEUs, 12 phases); the issue render `OK: known-issues.md is up-to-date`.
- **Runtime:** `ui/tests/e2e/tts-generate.test.ts` unchanged, `23 passed (37.1s)` (`tpp-D6-ui-electron.txt`), with `ELECTRON_RUN_AS_NODE` unset.
- **Skipped, with basis:** `mcp-types`, `mcp-build`, `mcp-tests` and `mcp-audit` (no MCP change; `openapi` pins the API shape, AC-150.8); `build-record` (no build).
- **Baseline failures excused:** 0. The gate passed on its first run; no step was rerun.
- **After the gate:** H1-3 added the current-focus paragraph, task.md rows were marked and these handoffs were written. `identity.py` excludes all three, so no product, test or tracked record changed after the gate; H1-6b checks that the expected state still equals the gate's.

---

## Changed Files

Counts are added / removed lines against the row-0 copies in the receipts folder's `base/` folder (`git diff --no-index --numstat --ignore-cr-at-eol`), not against `HEAD`, because other sessions' uncommitted work sits in the same tree. Line endings were measured as bytes (the gate's `line-endings` step).

| File | Change | Added / removed | Line endings |
|------|--------|-----------------|--------------|
| `ui/src/renderer/src/features/tts/tts-controls.ts` | MEU-150: `progressLabel` and `progressFraction`; MEU-149: `TTS_STATUS_TONE`, `STATUS_COLORS` deleted | +56 / -7 | CRLF kept |
| `ui/src/renderer/src/features/tts/TTSPage.tsx` | MEU-150: the percentage, the bar's label and value; MEU-149: the `StatusChip` pill and the blank-status default | +10 / -8 | CRLF kept |
| `tests/unit/test_tts_output_name.py` | MEU-150: AC-150.4 to AC-150.7 | +107 / -0 | LF kept |
| `ui/tests/unit/tts-page.test.ts` | AC-150.1, AC-149.1; AC-22.24 changed | +70 / -7 | CRLF kept |
| `ui/tests/unit/tts-page.behavior.test.ts` | AC-150.2, AC-150.3, AC-149.4; AC-56.5 changed | +85 / -1 | CRLF kept |
| `ui/tests/unit/queue-primitives.test.ts` | AC-43.2's census | +3 / -5 | CRLF kept |
| `ui/tests/unit/tts-pill-contrast.test.ts` | new: AC-149.5 | +155 (new) | LF |
| `docs/build-plan/03-service-layer.md` | the Delivered (Session 80) note | +9 / -0 | CRLF kept |
| `docs/build-plan/06-gui.md` | the Delivered (Session 80) note, the two wireframe strings and the `:1228` example | +10 / -3 | CRLF kept |
| `.agent/context/known-issues.yaml` | the three issues resolved (through the plan's `issue-resolve.py`) | +15 / -8 | LF kept |
| `.agent/context/known-issues.md` | the rendered issue list (`tools/issue_triage.py render`) | +3 / -6 | LF kept |
| `.agent/context/meu-status.yaml` | MEU-150 and MEU-149 `ready_for_review` (through `tools/meu_status.py`) | +10 / -10 | LF kept |
| `.agent/context/meu-registry.md` | the rendered registry | +2 / -2 | LF kept |
| `docs/BUILD_PLAN.md` | the rendered MEU status | +1 / -1 | LF kept |
| `.agent/context/grouping/2026-11-15-post-rc3-triage-residuals-session-grouping.md` | row 80 `executed (Session 80)` | +1 / -1 | LF kept |
| `.agent/context/current-focus.md` | the Session 80 paragraph (H1-3) | +3 / -0 | CRLF kept |

Plan-local files (in the plan folder): `human-check.md` (row 5, new, LF) and the row-0 records (`baseline.sha`, `baseline-dirty.txt`, `baseline-scope.json`, `baseline-readonly.json`, `baseline-dirty-hashes.json`). The plan-local scripts (`baseline.ps1`, `red-check.py`, `identity.py`, `scope-check.py`, `issue-resolve.py`, `dev-app-procs.py`, `readonly-check.py` and `session-gate.ps1`) were written at plan time and not changed in execution. These two handoffs are new. Nothing is committed or staged.

---

## Codex Validation Report

### Recheck Protocol

1. Read Scope + AC table
2. Verify each AC against Evidence section (file:line, not memory)
3. Independently probe the claimed behavior and compare decisive output
4. Verify the full gate is fresh and matches current D6 inputs; rerun if changed or unproven
5. Record findings below

### Findings

| # | Severity | Blocking | Finding | Fix | Status |
|---|----------|----------|---------|-----|--------|

### Verdict

`approved` at round 1 of 6 (ledger loop `tpp-execution-2026-11-15-tts-page-polish`), with 0 open blocking findings and `intent_achieved: yes` (`review-state-check.txt`, `exec-review.txt`; the canonical review is `2026-11-15-tts-page-polish-implementation-critical-review.md`). The first dispatch stopped on a Codex usage limit before any review and left no ledger round (S6). Mat ruled the wait (D-1050, in the plan's Decision Log), then switched the account, and round 1 ran on the unchanged HEAD and tested_state. The review grants no commit or push authorization.

---

## Deferred Items

| Item | Kind | Deferred-to | Basis |
|------|------|-------------|-------|
| Another program creating the same output name between `_free_paths`' check and the write | residual for triage | none | Plan §Out of Scope; D-957: no exclusive-create reservation |
| A name template setting, or any name scheme other than rc.3 F5 | out-of-scope | none | D-955 |
| Renaming existing uuid-named outputs | out-of-scope | none | 03 Job: "Existing output keeps its name" |
| A real segment count from the service | out-of-scope | none | D-962: the API shape stays; the home allows a percentage |
| Commit and push | out-of-scope | — | Only on Mat's explicit words (H2-5) |

### Departures and their basis

- **Status line 15.** The coordinator wrote Mat's execute words into the plan's Status line after the plan review approved it, so the reviewed plan hash (`f55c0a96…`) no longer holds. Line 15 is the only line that differs; no AC, task row or contract changed.
- **Execution decisions** (HDP v2, recorded in the plan's decision YAML; none hits an M item): D-964 (`resolution: autonomous`, `mandatory: none`): `red-check.py`'s pytest header pattern is not widened to the D-919 form, because no pytest receipt reaches `red-check.py` in this session. D-965 was reserved and not used. Per H1-6 (Session 65 RULE-2) they live in the plan YAML, so the Decision Log below is `None.`. There is no STOP item.
- **AC-150.1 has 12 label cases.** The plan's AC-150.1 lists twelve `progressLabel` inputs (six in range, two clamped, four at 0%); the task cell's prose says "eleven". The test checks all twelve the AC names, plus the four `progressFraction` cases.
- **AC-150.4 runs a generate for every unsafe text.** The plan asks for a generate from `..\..\escape`; the test runs a generate for each of its 11 unsafe texts, `..\..\escape` among them, and checks each file's parent is `stack.root`. That is a stronger check of the same rule.
- **The blank-status comment.** `TTSPage.tsx:129` gains a one-line comment above `job?.status || 'Idle'` saying why `||` and not `??` (`StatusChip` throws on a blank label).
- **Plan-local helper `s4.py`.** The S4 scope check before each row ran through a helper in the receipts folder that runs the plan's `scope-check.py`, checks that scope paths not yet written still hold their row-0 hashes, and checks `HEAD` against `baseline.sha` (`tpp-s4-row1.txt` to `tpp-s4-row7.txt`). It is not tracked.
- **The worst pair's receipt.** The row-4 Vitest receipt prints no ratios, so the worst pair comes from a read-only script that mirrors the test's model (`tpp-149-worst-pair.txt`: `pairs: 36 below 4.5: 0`). It matches the plan-time chip probe at 6.86.
- **Dates in the register.** The three issues' `resolution_path` says "on 2026-11-16" and `last_checked` is 2026-11-16, the day the rows ran; the task cell's template said "on 2026-11-15".
- **Row 5's stop.** After Mat's answer the app was still open, so a precheck (`tpp-dev-app-precheck.txt`: 14 of this launch's, 0 others) ran before `check --stop` (`tpp-dev-app-stop.txt`: 0 left, 0 others). `--stop` printed `stopped` for four process ids; it checks each process again before ending it, and the other ten had already exited after their parents ended. No process outside this launch was touched, and the avkit MCP servers were never counted.
- **Row 7's order.** Row 7's cell ends with a check that reads grouping row 80, and its register step cannot run twice, because `--expect-sha256` binds to the row-0 register hash. Row 80 was therefore edited before the cell ran; the cell then passed once (`tpp-row7-check.txt`).
- **Scratch wrappers.** Each row ran through a `run-*.ps1` wrapper in the receipts folder that sets the brief's environment (with `ELECTRON_RUN_AS_NODE` unset) and copies the task cell verbatim; each wrapper was compared with its cell. The wrappers for rows 6, 7 and H1 were written through a Python heredoc rather than the Write tool, and each was compared with its cell.
- **The launch console.** `run-row5-console.txt`, the console of the row-5 launch, was later overwritten by the row's validation run; the launch's own record (`tpp-dev-app-record.txt`, `dev-app-launch.json`) and the app log (`tpp-dev-app.txt`) are intact.
- **The first H1-6 run.** The validator refused the MEU-150 handoff once: the plan names `AC-45.12` (the precedent for AC-149.2), and that handoff did not mention it. The MEU-149 handoff passed. I added the precedent to the MEU-150 sibling row, rewrote both handoffs from their drafts and reran H1-6, which passed; `run-h1-6-console.txt` holds the passing run.

---

## Decision Log

None.

---

## History

| Event | Date | Agent | Detail |
|-------|------|-------|--------|
| Created | 2026-11-16 | claude-code-local (Claude Opus 5.5) | Initial MEU-150 handoff after the H1-2 gate, H1-3 and H1-4 |
| Reviewed | 2026-11-16 | codex-independent-reviewer | H1-7 execution review approved at round 1 of 6, 0 findings, intent achieved. An earlier dispatch had stopped on a Codex usage limit before any review (S6, D-1050) |
| Updated | 2026-11-16 | claude-code-local (Claude Opus 5.5) | Codex Validation Report filled from the canonical review (H2) |
