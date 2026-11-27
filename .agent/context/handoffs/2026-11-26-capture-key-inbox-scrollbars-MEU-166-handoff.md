---
date: "2026-11-27"
project: "2026-11-26-capture-key-inbox-scrollbars"
meu: "MEU-166"
status: "complete"
action_required: "VALIDATE_AND_APPROVE"
template_version: "2.2"
verbosity: "standard"
plan_source: "docs/execution/plans/2026-11-26-capture-key-inbox-scrollbars/implementation-plan.md"
build_plan_section: "docs/build-plan/09-screenshot-capture.md §Catalog follows the inbox folder (MEU-166, matrix 9.49)"
agent: "claude-code-local (Claude Opus 5.5)"
reviewer: "codex (H1-7 execution review)"
predecessor: "2026-11-26-capture-key-inbox-scrollbars-MEU-165-handoff.md"
---

# Handoff: 2026-11-26-capture-key-inbox-scrollbars-MEU-166-handoff

> **Status**: `complete`
> **Action Required**: `VALIDATE_AND_APPROVE`

---

## Scope

**MEU**: MEU-166 Catalog follows the inbox folder (phase 9, matrix 9.49), from `CAPTURE-INBOX-CHANGE-KEEPS-OLD-SHOTS`, grouped as Session 103 with MEU-165 and MEU-167. This handoff is the second of three: [MEU-165](2026-11-26-capture-key-inbox-scrollbars-MEU-165-handoff.md) → MEU-166 → [MEU-167](2026-11-26-capture-key-inbox-scrollbars-MEU-167-handoff.md). The shared records, the session-wide departures and the full gate table are in the MEU-165 handoff.
**Build Plan Section**: `docs/build-plan/09-screenshot-capture.md` §Catalog follows the inbox folder, with its `Delivered (Session 103)` note (row 11).
**Predecessor**: [2026-11-26-capture-key-inbox-scrollbars-MEU-165-handoff.md](2026-11-26-capture-key-inbox-scrollbars-MEU-165-handoff.md). Session 103 ran from `e5028a3` (`baseline.sha`), and `HEAD` did not move.

- **Scope (`INBOX_SCOPE`, `INBOX_SCOPE_SCAN`, D-1423).** In `packages/core/src/avkit_core/services/capture.py` a row is in scope when its `original_path.parent` equals the current resolved inbox, with no filesystem call. `scan_inbox()` and `list_shots()` return only rows in scope. Neither scan loop probes, prunes or saves a row out of scope: the first loop checks a resolved file's parent before its probe, so a file link in A to a cataloged B image never reaches B's row.
- **Rows kept.** Rows of other folders are kept with every field unchanged, and no file is created, changed or deleted in a folder the user left. Back on that folder its rows return with the same ids and marks, and the prune resumes there.
- **By id (`INBOX_SCOPE_BY_ID`, D-1424).** Every public `CaptureService` method that takes a shot id answers a shot outside the current inbox with the same `NotFoundError` as an unknown id, and writes nothing. The routes map it to the existing 404; no route, schema or OpenAPI document changes.
- **The page (`INBOX_SAVE_REFRESH`, `INBOX_SELECTION_LEFT`, `INBOX_RESULT_BOUND`, D-1425).** A settings save that changes `inbox_dir` asks for the list at once. A selection that a list answer held and a later answer lacks is cleared with the delete path's resets; the page then opens the newest shot or shows the empty state. A crop result or a not-found from the old folder does not touch the new list.
- **Records.** MEU-166 is `ready_for_review`; `CAPTURE-INBOX-CHANGE-KEEPS-OLD-SHOTS` is resolved; 09 §Catalog follows the inbox folder carries the Delivered note, and its `scan_inbox`, `list_shots` and `get_shot` rows name the current inbox.

**What Mat sees.** When the inbox folder is changed in Capture or Settings and saved, the Capture filmstrip shows only the shots of the new folder at once, and the old folder's shots leave. Changing back shows the old shots again with their marks. No file of the old folder is deleted or moved.

**Plan:** [implementation-plan.md](../../../docs/execution/plans/2026-11-26-capture-key-inbox-scrollbars/implementation-plan.md) §Single-statement contracts. **Execution authorization:** `USER_EXPLICIT`, 2026-11-26 ("drafts stand, go for 104 after the reviews finish and then execute rest as you see fit. Use HDP for decisions and pick recommendations as expect and do not stop for human decisions on techincal metters that are settled as primary recommendation for any of the 4 executions."). The plan review approved at round 2 of loop `cki-plan-2026-11-26-capture-key-inbox-scrollbars`. Receipts named by file name alone are in the session's receipts folder (the `2026-11-26-capture-key-inbox-scrollbars` folder under `RECEIPTS_DIR`).

---

## Acceptance Criteria

| AC | Type | Description | Source | Test(s) | Status |
|----|------|-------------|--------|---------|--------|
| AC-166.1 | unit | With inbox A the scan and the list return A's two shots; with B, B's one; back on A, A's two with the same ids and the saved mark still linked; a file in `A/sub` is never listed | Spec (09 §Catalog follows the inbox folder: Scope, Rows kept); `INBOX_SCOPE`, `INBOX_SCOPE_SCAN` | `tests/unit/test_capture_inbox_scope.py:147`, `:156`; `:172` (passed at Red: guard) | ✅ |
| AC-166.2 | unit | With inbox B, a deleted A original keeps its row unchanged and nothing in A is written; back on A the prune runs; a file link in A to a B image is neither probed nor saved in either loop | Spec (Rows kept); D-1423; round-1 review F4 | `tests/unit/test_capture_inbox_scope.py:180`, `:209`; `:194` (passed at Red: guard) | ✅ |
| AC-166.3 | unit | Every public id-taking `CaptureService` method raises the unknown-id `NotFoundError` for an A shot with inbox B and writes nothing; the method list equals the class's; on A the calls still work | Spec (By id); D-1424; `INBOX_SCOPE_BY_ID` | `tests/unit/test_capture_inbox_scope.py:267`; census `:282` and guard `:291` (passed at Red) | ✅ |
| AC-166.4 | integration | Real stack: after `PUT` A then B, `GET /captures` lists only B's shot with the same key sets; `GET /captures/{A id}` and a write route answer 404 with the unknown-id body; A's file stays; back on A the id answers 200 | Spec (Scope; Tests); the grouping gate | `tests/e2e/test_api_capture_inbox_scope.py:66` | ✅ |
| AC-166.5 | unit | A save that changes `inbox_dir` is followed at once by one more `GET /captures`; a key-only save makes none | Spec (Refresh); `INBOX_SAVE_REFRESH` | `ui/tests/unit/capture-inbox-scope.behavior.test.ts:408`; guard `:421` | ✅ |
| AC-166.6 | unit | With a2 open, a list of b1 only makes b1 current; an empty list shows the empty state; no detail read of a2 and no capture error follow; a selection no list has held is kept within one inbox | Spec (Refresh); D-1425; `INBOX_SELECTION_LEFT` | `ui/tests/unit/capture-inbox-scope.behavior.test.ts:436`; guard `:475` | ✅ |
| AC-166.7 | integration | Electron on mini-air, real backend: inbox A shows two items; after a save of B one item with B's name, current, and no error line; back on A two items; A's files stay on disk | Spec (Tests row); grouping acceptance direction | `ui/tests/e2e/capture-settings-draft.test.ts:407`; Red run `r20261127T161201Z-091957d`, Green run `r20261127T170013Z-02ecd38` | ✅ |
| AC-166.8 | unit | With held responses: a crop result or a 404 detail read from the old inbox, released after the new list, leaves b1 current with no error event, no error line and no crop notice | Round-1 review F2; D-1425; `INBOX_SELECTION_LEFT`; `INBOX_RESULT_BOUND` | `ui/tests/unit/capture-inbox-scope.behavior.test.ts:498`; guard `:543` | ✅ |
| AC-165 (cross-ref) | sibling | This plan's AC-165 criteria belong to MEU-165; that handoff carries their Red and Green evidence, and this handoff claims none of them | the plan | see the MEU-165 handoff | cross-ref |
| AC-167 (cross-ref) | sibling | This plan's AC-167 criteria belong to MEU-167; that handoff carries their Red and Green evidence, and this handoff claims none of them | the plan | see the MEU-167 handoff | cross-ref |
| AC-39 (cross-ref) | named change | AC-39.13's token-form change (D-1422) belongs to MEU-165; not a criterion of MEU-166 | the plan; D-1422 | see the MEU-165 handoff | cross-ref |
| AC-61 (cross-ref) | named change | AC-61.16's token-form change (D-1422) belongs to MEU-165; not a criterion of MEU-166 | the plan; D-1422 | see the MEU-165 handoff | cross-ref |
| AC-57 (cross-ref) | pin | §Test pins: the Capture page behaviour pins (AC-57.2, AC-57.3, AC-57.9) are unchanged and pass | Local Canon | gate `guards`, `ui-tests` | ✅ |
| AC-162 (cross-ref) | pin | §Test pins: the quick-start pins are unchanged and pass | Local Canon | gate `guards`, `ui-tests` | ✅ |
| AC-7 (cross-ref) | pin | §Test pins: the E2E pointer helpers are unchanged | Local Canon | gate `guards` | ✅ |
| AC-93 (cross-ref) | pin | §Test pins: the block order of `test-ids.ts` (AC-93.6) is unchanged | Local Canon | gate `guards` | ✅ |
| AC-96 (cross-ref) | pin | §Test pins: AC-96.11 on the same block order is unchanged | Local Canon | gate `guards` | ✅ |
| AC-151 (cross-ref) | pin | §Test pins: AC-151.14 keeps its lines; AC-166.7 is added lines in the same file | Local Canon | `ui/tests/e2e/capture-settings-draft.test.ts`; gate `guards` | ✅ |

<!-- CACHE BOUNDARY -->

---

## Evidence

### FAIL_TO_PASS

Red for the service is row 2 (`cki-row2-red.txt`: `17 failed, 4 passed in 7.91s`; `cki-row2-red-check.txt`: `red-check: 1 receipt(s), runner pytest, 6 required test(s), 4 allowed pass(es), 0 step target(s), 0 problem(s)`), Green row 3 (`cki-row3-green.txt`: `21 passed in 26.68s`). Red for the page is row 4 (`cki-row4-red.txt`: `Tests  3 failed | 3 passed (6)`; `cki-row4-red-check.txt`: `3 required test(s), 0 allowed pass(es), 0 problem(s)`), Green row 5 (`cki-row5-green.txt`: `Tests  6 passed (6)`). The Electron test failed at row 1 and passed at row 10.

| Test | Red Output (hash/snippet) | Green Output | File:Line |
|------|---------------------------|--------------|-----------|
| AC-166.1 `test_ac_166_1_list_follows_inbox` | `inbox B scans only B` | Row 3: `21 passed in 26.68s` | `tests/unit/test_capture_inbox_scope.py:147` |
| AC-166.1 `test_ac_166_1_change_back_restores_rows` | `back on A the list is A's two rows with the same ids` | Row 3 | `tests/unit/test_capture_inbox_scope.py:156` |
| AC-166.2 `test_ac_166_2_scan_leaves_other_folder_rows` | `inbox B's scan leaves A's row as it was` | Row 3 | `tests/unit/test_capture_inbox_scope.py:180` |
| AC-166.2 `test_ac_166_2_linked_file_is_not_probed` | `neither scan loop probes B's file through the A link` | Row 3 | `tests/unit/test_capture_inbox_scope.py:209` |
| AC-166.3 `test_ac_166_3_by_id_outside_inbox_is_not_found` (one case per method) | the A shot is answered while the inbox is B | Row 3 | `tests/unit/test_capture_inbox_scope.py:267` |
| AC-166.4 `test_ac_166_4_api_list_follows_inbox` | `inbox B lists only B's shot` | Row 3 | `tests/e2e/test_api_capture_inbox_scope.py:66` |
| AC-166.5 | `one more GET /captures after the save: expected [] to have a length of 1 but got +0` | Row 5: `Tests  6 passed (6)` | `ui/tests/unit/capture-inbox-scope.behavior.test.ts:408` |
| AC-166.6 | `b1 is the current filmstrip item: expected '' to contain 'b-1.png'` | Row 5 | `ui/tests/unit/capture-inbox-scope.behavior.test.ts:436` |
| AC-166.8 | `expected '' to contain 'b-1.png'` | Row 5 | `ui/tests/unit/capture-inbox-scope.behavior.test.ts:498` |
| AC-166.7 | Row 1 run `r20261127T161201Z-091957d`: one of the 4 new failures, on an expectation (`cki-run-1.txt`: `result: new-failures exit=40`) | Row 10 run `r20261127T170013Z-02ecd38`: `summary: tests=260 expected=260 unexpected=0` | `ui/tests/e2e/capture-settings-draft.test.ts:407` |

`test_ac_166_1_subfolder_is_not_listed` (`:172`), `test_ac_166_2_prune_resumes_in_scope` (`:194`), `test_ac_166_3_by_id_census` (`:282`) and `test_ac_166_3_by_id_inside_inbox_still_works` (`:291`) passed at Red and are guards, the 4 allowed passes of `cki-row2-red-check.txt`. The page guards `:421`, `:475` and `:543` passed at Red. Row 4's Red was run again after its harness was amended (D-1436); its first record is kept as `-r1`.

### Commands Executed

```json
{"schema_version": "evidence.v1", "cwd": "P:/av-kit", "check_id": "cki-2-3-service", "command": "pwsh -NoProfile -File C:/Temp/av-kit/2026-11-26-capture-key-inbox-scrollbars/run-row.ps1 2, then 3; receipts C:/Temp/av-kit/2026-11-26-capture-key-inbox-scrollbars/cki-row2*.txt, cki-row3*.txt", "scope": "AC-166.1 to AC-166.4 Red then Green", "phase": "green", "exit_code": 0, "result": "pass", "tested_state": "HEAD e5028a3 (baseline.sha) plus rows 0 to 3", "output": "cki-row2-red.txt: 17 failed, 4 passed in 7.91s. cki-row2-red-check.txt: 6 required test(s), 4 allowed pass(es), 0 problem(s). cki-row3-green.txt: 21 passed in 26.68s"}
```

```json
{"schema_version": "evidence.v1", "cwd": "P:/av-kit", "check_id": "cki-4-5-page", "command": "pwsh -NoProfile -File C:/Temp/av-kit/2026-11-26-capture-key-inbox-scrollbars/run-row.ps1 4, then 5; receipts C:/Temp/av-kit/2026-11-26-capture-key-inbox-scrollbars/cki-row4*.txt, cki-row5*.txt", "scope": "AC-166.5, AC-166.6 and AC-166.8 Red then Green", "phase": "green", "exit_code": 0, "result": "pass", "tested_state": "HEAD e5028a3 (baseline.sha) plus rows 0 to 5", "output": "cki-row4-red.txt: Tests  3 failed | 3 passed (6). cki-row4-red-check.txt: 3 required test(s), 0 problem(s). cki-row5-green.txt: Tests  6 passed (6)"}
```

```json
{"schema_version": "evidence.v1", "cwd": "P:/av-kit", "check_id": "cki-1-10-e2e", "command": "pwsh -NoProfile -File C:/Temp/av-kit/2026-11-26-capture-key-inbox-scrollbars/run-row.ps1 1, then 10; receipts C:/Temp/av-kit/2026-11-26-capture-key-inbox-scrollbars/cki-run-1.txt, cki-run-10.txt, cki-row10-remote-ok.txt", "scope": "AC-166.7 Red at row 1 and Green at row 10 on mini-air", "phase": "runtime", "exit_code": 0, "result": "pass", "tested_state": "HEAD e5028a3 (baseline.sha) plus rows 0 to 10", "output": "cki-run-1.txt: summary: tests=260 expected=256 unexpected=4; result: new-failures exit=40. cki-run-10.txt: summary: tests=260 expected=260 unexpected=0; result: ok exit=0. cki-row10-remote-ok.txt: remote-ok: run r20261127T170013Z-02ecd38; tests 260; 0 problem(s)"}
```

```json
{"schema_version": "evidence.v1", "cwd": "P:/av-kit", "check_id": "cki-11-canon-register", "command": "pwsh -NoProfile -File C:/Temp/av-kit/2026-11-26-capture-key-inbox-scrollbars/run-row.ps1 11; receipts C:/Temp/av-kit/2026-11-26-capture-key-inbox-scrollbars/cki-row11-*.txt", "scope": "Row 11: the 09 lines and Delivered notes, CAPTURE-INBOX-CHANGE-KEEPS-OLD-SHOTS resolved, MEU-166 ready_for_review", "phase": "static", "exit_code": 0, "result": "pass", "tested_state": "HEAD e5028a3 (baseline.sha) plus rows 0 to 11", "output": "cki-row11-canon.txt: row-check canon: 0 problem(s). cki-row11-issue.txt: issue-resolve: 0 problem(s). cki-row11-status-MEU-166.txt: ready_for_review"}
```

```json
{"schema_version": "evidence.v1", "cwd": "P:/av-kit", "check_id": "cki-h1-2-gate", "command": "$env:ELECTRON_RUN_AS_NODE=$null; rtk proxy pwsh -NoProfile -File docs/execution/plans/2026-11-26-capture-key-inbox-scrollbars/session-gate.ps1 *> C:/Temp/av-kit/2026-11-26-capture-key-inbox-scrollbars/cki-gate-h1.txt (task.md row H1-2's Validation cell); step receipts C:/Temp/av-kit/2026-11-26-capture-key-inbox-scrollbars/cki-D6-*.txt", "scope": "H1-2: the registered verification plan, as in the MEU-165 handoff", "phase": "full", "exit_code": 0, "result": "pass", "tested_state": "e5028a3ad45fa033c388dea46658ff282fbd7364+937ef42b857984acb234116d46866c6f400165b024ddc6e8e943398619c92a78", "fresh": true, "snapshot": false, "output": "cki-gate-h1.txt: tested_state before=e5028a3ad45fa033c388dea46658ff282fbd7364+937ef42b857984acb234116d46866c6f400165b024ddc6e8e943398619c92a78 after=e5028a3ad45fa033c388dea46658ff282fbd7364+937ef42b857984acb234116d46866c6f400165b024ddc6e8e943398619c92a78; session-gate: all steps exit 0. cki-D6-py-inbox.txt: 109 passed in 11.00s. cki-D6-ui-capture.txt: Tests  353 passed (353). cki-D6-py-tests.txt: 3379 passed, 37 warnings in 413.82s (0:06:53). cki-D6-ui-tests.txt: Tests  1716 passed (1716). cki-D6-openapi.txt: export_openapi.py --check openapi.committed.json: no output"}
```

```json
{"schema_version": "evidence.v1", "cwd": "P:/av-kit", "check_id": "cki-h1-4-no-deselect", "command": "pwsh -NoProfile -File C:/Temp/av-kit/2026-11-26-capture-key-inbox-scrollbars/run-row.ps1 H1-4; receipts C:/Temp/av-kit/2026-11-26-capture-key-inbox-scrollbars/cki-h14-openapi.txt, cki-no-deselect.txt", "scope": "H1-4: the API document is unchanged (D-1424 changes no route or schema); nothing deselected", "phase": "static", "exit_code": 0, "result": "pass", "tested_state": "e5028a3ad45fa033c388dea46658ff282fbd7364+937ef42b857984acb234116d46866c6f400165b024ddc6e8e943398619c92a78", "output": "cki-h14-openapi.txt: no output: export_openapi.py --check found the committed document current. cki-no-deselect.txt: deselect in gate code: [] summary: 3379 passed, 37 warnings in 413.82s (0:06:53)"}
```

### Quality Gate Results

The gate ran twice. Run 1 stopped at ui-tests with `Tests  9 failed | 1707 passed (1716)`, each failure `Error: Test timed out in 5000ms.`, in six main-process files this session does not change, while another repository's gate loaded the PC; the six files pass alone (`Tests  99 passed (99)`, `cki-h12-diag-6files.txt`). Under D-1438 run 1's receipts are kept as `cki-gate-h1-r1.txt` and `cki-D6-*-r1.txt`, and the whole gate ran again, unchanged, once that load had ended. Run 2 (`cki-gate-h1.txt`): `tested_state before=e5028a3ad45fa033c388dea46658ff282fbd7364+937ef42b857984acb234116d46866c6f400165b024ddc6e8e943398619c92a78 after=e5028a3ad45fa033c388dea46658ff282fbd7364+937ef42b857984acb234116d46866c6f400165b024ddc6e8e943398619c92a78`, 28 steps each exit 0, last line `session-gate: all steps exit 0`. Skipped by the gate's own rules: `electron-devpc reason=D-1411 (E2E runs on mini-air; the e2e-remote step)`; `mcp-tests reason=no MCP file changed (mcp-server/ is read-only, bound by scope-paths)`. The full table is in the MEU-165 handoff; the steps that bear on MEU-166:

| Step | Stage | Result | Decisive line | Receipt |
|------|-------|--------|---------------|---------|
| py-types | static | exit 0 | `0 errors, 0 warnings, 0 informations` | `cki-D6-py-types.txt` |
| py-lint | static | exit 0 | `All checks passed!` | `cki-D6-py-lint.txt` |
| py-format | static | exit 0 | `10 files already formatted` | `cki-D6-py-format.txt` |
| py-inbox | targeted | exit 0 | `109 passed in 11.00s` | `cki-D6-py-inbox.txt` |
| ui-capture | targeted | exit 0 | `Tests  353 passed (353)` | `cki-D6-ui-capture.txt` |
| openapi | static | exit 0 | `export_openapi.py --check openapi.committed.json: no output` | `cki-D6-openapi.txt` |
| py-tests | full | exit 0 | `3379 passed, 37 warnings in 413.82s (0:06:53)` | `cki-D6-py-tests.txt` |
| ui-tests | full | exit 0 | `Tests  1716 passed (1716)` | `cki-D6-ui-tests.txt` |
| issues-render | full | exit 0 | `OK: known-issues.md is up-to-date` | `cki-D6-issues-render.txt` |
| state-render | full | exit 0 | `✅ Drift check passed — SSOT loaded (174 MEUs, 12 phases), rendered regions match on-disk content` | `cki-D6-state-render.txt` |
| identity-after | identity | exit 0 | `tested_state e5028a3ad45fa033c388dea46658ff282fbd7364+937ef42b857984acb234116d46866c6f400165b024ddc6e8e943398619c92a78` | `cki-D6-identity-after.txt` |

---

## Changed Files

Counts are added / removed lines against `HEAD` `e5028a3` (`git diff --numstat --ignore-cr-at-eol HEAD`); a new file's count is its line count.

| File | Change | Added / removed |
|------|--------|-----------------|
| `packages/core/src/avkit_core/services/capture.py` | the scope test, both scan loops, the list and every by-id method | +28 / -21 |
| `tests/unit/test_capture_inbox_scope.py` | AC-166.1 to AC-166.3 | new, 305 |
| `tests/e2e/test_api_capture_inbox_scope.py` | AC-166.4 | new, 113 |
| `ui/tests/unit/capture-inbox-scope.behavior.test.ts` | AC-166.5, AC-166.6, AC-166.8 and their guards | new, 553 |
| `ui/src/renderer/src/features/capture/CapturePage.tsx` | the refresh on a saved inbox change, the cleared selection and the bound results (with MEU-165's texts) | +170 / -14 |
| `ui/src/renderer/src/features/capture/useCaptureSettings.ts` | the hook returns `saved` (shared with MEU-165) | +7 / -0 |
| `ui/tests/e2e/capture-settings-draft.test.ts` | AC-166.7 at `:407` (with MEU-165's AC-165.10) as added lines | +223 / -2 |
| The shared records | see the MEU-165 handoff's Changed Files | |

`routes/captures.py`, `useCaptureCatalog.ts` and `openapi.committed.json` did not change. Nothing is committed or staged.

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
| A prompt to save unsaved marks before the inbox change clears the selection | out-of-scope | — | D-1425; the delete path has no such prompt either |
| Deleting or moving the rows or files of a folder the user left | out-of-scope | — | Rows kept row; D-1401 |
| A by-id answer other than "not found" for a shot outside the inbox | out-of-scope | — | D-1424 |
| The `GET /captures` reply shape | out-of-scope | — | The grouping gate |
| Commit and push | out-of-scope | — | Only on Mat's direction (H2) |

### Departures and their basis

- **D-1436.** Row 5's first Green run failed AC-166.5 and AC-166.6 on two defects of the row 4 test harness, not of the product: AC-166.5 now counts list requests from the index of the inbox `PUT`, and `releaseList` ends the hold before it answers. The harness was amended, row 4's Red run again and re-recorded, then row 5 ran.
- **Row 3.** Its first run stopped at ruff E501 on one docstring line in `capture.py`; the line was shortened and the row ran again.
- **D-1435.** AC-166.7 calls `test.setTimeout(240_000)` first, as AC-151.14 does; each `expect` keeps its own bounded timeout.
- The session-wide departures, D-1433 to D-1438, are in the MEU-165 handoff.

---

## Decision Log

None.

---

## History

| Event | Date | Agent | Detail |
|-------|------|-------|--------|
| Created | 2026-11-27 | claude-code-local (Claude Opus 5.5) | Handoff after the H1-2 gate, H1-3, H1-4 and H1-5 |
