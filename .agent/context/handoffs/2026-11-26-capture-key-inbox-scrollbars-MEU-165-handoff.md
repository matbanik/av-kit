---
date: "2026-11-27"
project: "2026-11-26-capture-key-inbox-scrollbars"
meu: "MEU-165"
status: "complete"
action_required: "VALIDATE_AND_APPROVE"
template_version: "2.2"
verbosity: "standard"
plan_source: "docs/execution/plans/2026-11-26-capture-key-inbox-scrollbars/implementation-plan.md"
build_plan_section: "docs/build-plan/09-screenshot-capture.md §Capture key in texts (MEU-165, matrix 9.48)"
agent: "claude-code-local (Claude Opus 5.5)"
reviewer: "codex (H1-7 execution review)"
predecessor: "2026-11-26-ytdlp-challenge-and-cookie-test-MEU-170-handoff.md"
---

# Handoff: 2026-11-26-capture-key-inbox-scrollbars-MEU-165-handoff

> **Status**: `complete`
> **Action Required**: `VALIDATE_AND_APPROVE`

---

## Scope

**MEU**: MEU-165 Capture key in texts (phase 9, matrix 9.48), from `CAPTURE-HOTKEY-TEXT-HARDCODED`, grouped as Session 103 with MEU-166 and MEU-167 (grouping D-1410 to D-1413). This handoff is the first of three: MEU-165 → [MEU-166](2026-11-26-capture-key-inbox-scrollbars-MEU-166-handoff.md) → [MEU-167](2026-11-26-capture-key-inbox-scrollbars-MEU-167-handoff.md). It also carries the session's shared records and departures.
**Build Plan Section**: `docs/build-plan/09-screenshot-capture.md` §Capture key in texts, with its `Delivered (Session 103)` note (row 11).
**Predecessor**: [2026-11-26-ytdlp-challenge-and-cookie-test-MEU-170-handoff.md](2026-11-26-ytdlp-challenge-and-cookie-test-MEU-170-handoff.md). Session 103 ran from `e5028a3` (`baseline.sha`), and `HEAD` did not move.

- **One formatter (`CAPTURE_KEY_TOKEN`, D-1421).** `features/capture/capture-key.ts` holds `CAPTURE_KEY_DEFAULT` (`F2`) and `captureKeyText(text, key)`, which replaces every `{captureKey}` and gives the default for a blank key. The eight texts of the Capture empty state, the Capture help, the Settings startup help and the Capture quick start hold the token.
- **The default reading (`CAPTURE_KEY_DEFAULT_READING`, D-1421).** The exported constants `CAPTURE_HELP_SECTIONS`, `SETTINGS_HELP_SECTIONS` and `QUICK_START.capture` are the readings with `F2`, equal to the strings at `HEAD`; `captureHelpSections(key)`, `settingsHelpSections(key)` and `quickStartPage(feature, key)` give the rest. No help image is retaken: the E2E comparison and the shots hash use the default reading.
- **The saved key (`CAPTURE_KEY_SAVED`, `CAPTURE_KEY_FOLLOW`, `CAPTURE_KEY_UNCONFIRMED`, D-1420).** The texts name the saved `capture.hotkey`, never the draft. After a save the page reads main's hotkey status every 500 ms, at most 10 times; the key cap shows only when the status names the saved key as registered, and an unconfirmed end or a refused read shows `<key> is saved, but av-kit cannot confirm it works. Restart av-kit if <key> does nothing.`
- **Records.** MEU-165 is `ready_for_review`; `CAPTURE-HOTKEY-TEXT-HARDCODED` is resolved; 09 §Capture key in texts carries the Delivered note, and the empty-state line names the key set in `capture.hotkey`.

**What Mat sees.** After the capture key is changed in Capture or Settings and saved, the Capture page's empty state, its help card, its quick start and the Settings startup help name the new key at once, with no restart. With the default key every text reads as before. If av-kit cannot confirm that the new key works, the page says so instead of showing a key cap.

**Plan:** [implementation-plan.md](../../../docs/execution/plans/2026-11-26-capture-key-inbox-scrollbars/implementation-plan.md) §Single-statement contracts. **Execution authorization:** `USER_EXPLICIT`, 2026-11-26 ("drafts stand, go for 104 after the reviews finish and then execute rest as you see fit. Use HDP for decisions and pick recommendations as expect and do not stop for human decisions on techincal metters that are settled as primary recommendation for any of the 4 executions."); the same words approve the four named expectation changes of D-1422 (M-7). The plan review approved at round 2 of loop `cki-plan-2026-11-26-capture-key-inbox-scrollbars` (`.agent/context/handoffs/2026-11-26-capture-key-inbox-scrollbars-plan-critical-review.md`). Receipts named by file name alone are in the session's receipts folder (the `2026-11-26-capture-key-inbox-scrollbars` folder under `RECEIPTS_DIR`); the mini-air run folders are under its `e2e-remote` folder.

---

## Acceptance Criteria

| AC | Type | Description | Source | Test(s) | Status |
|----|------|-------------|--------|---------|--------|
| AC-165.1 | unit | `captureKeyText` replaces every token, keeps a text with no token, gives `F2` as `CAPTURE_KEY_DEFAULT`, shows a chord as given, and gives the default for a blank key | Spec (09 §Capture key in texts, One source); `CAPTURE_KEY_TOKEN` | `ui/tests/unit/capture-key.test.ts:49` | ✅ |
| AC-165.2 | unit | Only `capture-key.ts`, `useCaptureSettings.ts` and `registry/shortcuts.ts` hold the literal `F2` under `ui/src/renderer/src`; the eight texts hold `{captureKey}` | Spec (One source) | `ui/tests/unit/capture-key.behavior.test.ts:71` | ✅ |
| AC-165.3 | unit (guard) | The exported constants hold no token and equal the `HEAD` strings; topic ids, order and count unchanged | Spec (Default); `CAPTURE_KEY_DEFAULT_READING` | `ui/tests/unit/capture-key.behavior.test.ts:90` | ✅ (passed at Red: guard) |
| AC-165.4 | unit | `captureHelpSections('F9')`, `settingsHelpSections('F9')` and `quickStartPage('capture', 'F9')` name `F9`; a feature with no token returns the same object | Spec (Set key); `CAPTURE_KEY_DEFAULT_READING` | `ui/tests/unit/capture-key.test.ts:61` | ✅ |
| AC-165.5 | unit | With the saved key `F9`, registered, the empty state, the key cap and the open help card name `F9` | Spec (Set key) | `ui/tests/unit/capture-key.behavior.test.ts:287` | ✅ |
| AC-165.6 | unit | A draft changes nothing; after Save the texts follow with no remount; the cap waits for a matching status; 10 follow reads end in the unconfirmed notice; a refused read shows it at once; an unmount stops the reads | Spec (Change); `CAPTURE_KEY_SAVED`; `CAPTURE_KEY_FOLLOW` (D-1420); `CAPTURE_KEY_UNCONFIRMED` | `ui/tests/unit/capture-key.behavior.test.ts:312`, `:330`, `:344`, `:353` | ✅ |
| AC-165.7 | unit | The in-use banner names the saved key `F9`, not the draft `F10`, and no key cap shows | Local Canon (`CapturePage.tsx` banner template); D-1420 | `ui/tests/unit/capture-key.behavior.test.ts:363` | ✅ |
| AC-165.8 | unit | The Settings startup help ends `so F9 still works.` with the saved key `F9`; with the default key it ends `so F2 still works.` | Spec (Set key) | `ui/tests/unit/capture-key.behavior.test.ts:389`; guard `:398` | ✅ |
| AC-165.9 | tooling | `help_guide_ste.py` passes the token texts; `validateQuickStart` passes the Capture page with `F9` and `Ctrl+Shift+F12`; `test_help_guide_ste.py` passes unchanged | Spec (Help rules) | `ui/tests/unit/capture-key.test.ts:90`; `cki-row7-ste.txt`: `help-guide-ste: 0 problems`; `cki-row7-ste-pytest.txt`: `4 passed in 0.09s` | ✅ |
| AC-165.10 | integration | Electron on mini-air, real backend: a key saved in the page shows `F9` in the empty state and the help card with no restart, from an empty temp inbox | Spec (Tests row) | `ui/tests/e2e/capture-settings-draft.test.ts:337`; Red run `r20261127T161201Z-091957d`, Green run `r20261127T170013Z-02ecd38` | ✅ |
| AC-39.13 (cross-ref) | named change | D-1422: the source scan of the Capture page takes the token form (the empty-state regex and the two topic titles); not a criterion of MEU-165, and changed by name only | Local Canon; D-1422 | `ui/tests/unit/capture-page.test.ts:112`, `:117`, `:328` | ✅ (failed at Red as named) |
| AC-61.16 (cross-ref) | named change | D-1422: the Settings help scan looks for `{captureKey}` in place of `F2`; changed by name only | Local Canon; D-1422 | `ui/tests/unit/settings-page.test.ts:771` | ✅ (failed at Red as named) |
| AC-57 (cross-ref) | pin | §Test pins: the key cap, the banner and the empty state at the default key (AC-57.2, AC-57.3, AC-57.9) are unchanged and pass | Local Canon | `ui/tests/unit/capture-page.behavior.test.ts:1265`, `:1279`, `:1460`; gate `guards`, `ui-tests` | ✅ |
| AC-162 (cross-ref) | pin | §Test pins: the help texts, the steps hash and the STE facts (AC-162.6, AC-162.7, AC-162.9) are unchanged and pass on the default reading | Local Canon | `ui/tests/unit/help-quick-start.test.tsx`; gate `guards`, `ui-tests` | ✅ |
| AC-7 (cross-ref) | pin | §Test pins: the E2E pointer helpers are unchanged; the new E2E tests use them | Local Canon | `ui/tests/unit/e2e-pointer.test.ts`; gate `guards` | ✅ |
| AC-93 (cross-ref) | pin | §Test pins: the block order of `test-ids.ts` (AC-93.6) is unchanged; the new block is at the end | Local Canon | `ui/tests/unit/gui-actions-audit.test.ts`; gate `guards` | ✅ |
| AC-96 (cross-ref) | pin | §Test pins: AC-96.11 on the same block order is unchanged | Local Canon | `ui/tests/unit/gui-actions-audit.test.ts`; gate `guards` | ✅ |
| AC-151 (cross-ref) | pin | §Test pins: AC-151.14, the settings draft E2E test, keeps its lines; the new tests are added lines | Local Canon | `ui/tests/e2e/capture-settings-draft.test.ts`; gate `guards` | ✅ |
| AC-166 (cross-ref) | sibling | This plan's AC-166 criteria belong to MEU-166; that handoff carries their Red and Green evidence, and this handoff claims none of them | the plan | see the MEU-166 handoff | cross-ref |
| AC-167 (cross-ref) | sibling | This plan's AC-167 criteria belong to MEU-167; that handoff carries their Red and Green evidence, and this handoff claims none of them | the plan | see the MEU-167 handoff | cross-ref |

<!-- CACHE BOUNDARY -->

---

## Evidence

### FAIL_TO_PASS

Red is row 6 (`cki-row6-red.txt`: `Tests  13 failed | 61 passed (74)`; `cki-row6-red-check.txt`: `red-check: 1 receipt(s), runner vitest, 10 required test(s), 0 allowed pass(es), 0 step target(s), 0 problem(s)`); Green is row 7 (`cki-row7-green.txt`: `Tests  13 passed (13)`). The Electron test failed at row 1 and passed at row 10.

| Test | Red Output (hash/snippet) | Green Output | File:Line |
|------|---------------------------|--------------|-----------|
| AC-165.1 | `capture-key.ts exists: expected undefined to be type of 'function'` | Row 7: `Tests  13 passed (13)` | `ui/tests/unit/capture-key.test.ts:49` |
| AC-165.4 | `captureHelpSections is exported` failed | Row 7 | `ui/tests/unit/capture-key.test.ts:61` |
| AC-165.9 | `quickStartPage is exported` failed | Row 7 | `ui/tests/unit/capture-key.test.ts:90` |
| AC-165.2 | `expected [ …(6) ] to deeply equal [ …(3) ]` | Row 7 | `ui/tests/unit/capture-key.behavior.test.ts:71` |
| AC-165.5 | `expected 'Press F2 or Capture region' to be 'Press F9 or Capture region'` | Row 7 | `ui/tests/unit/capture-key.behavior.test.ts:287` |
| AC-165.6 (four tests) | `expected 'Press F2 or Capture region' to be 'Press F9 or Capture region'` and the follow reads absent | Row 7 | `ui/tests/unit/capture-key.behavior.test.ts:312`, `:330`, `:344`, `:353` |
| AC-165.7 | the banner follows the draft `F10` | Row 7 | `ui/tests/unit/capture-key.behavior.test.ts:363` |
| AC-165.8 | `/so F9 still works\.$/` not matched | Row 7 | `ui/tests/unit/capture-key.behavior.test.ts:389` |
| AC-39.13 (named change, D-1422) | the token-form regex finds the literal `F2` | Row 7 | `ui/tests/unit/capture-page.test.ts:328` |
| AC-61.16 (named change, D-1422) | `{captureKey}` not in the Settings help file | Row 7 | `ui/tests/unit/settings-page.test.ts:771` |
| AC-165.10 | Row 1 run `r20261127T161201Z-091957d`: one of the 4 new failures, on an expectation (`cki-run-1.txt`: `result: new-failures exit=40`) | Row 10 run `r20261127T170013Z-02ecd38`: `summary: tests=260 expected=260 unexpected=0` | `ui/tests/e2e/capture-settings-draft.test.ts:337` |

Guard AC-165.3 (`:90`) and guard AC-165.8 (`:398`) passed at Red. The §Test pins were not changed (gate `guards`: `row-check guards: 0 problem(s)`), except the four lines that D-1422 names, listed under Changed Files.

### Commands Executed

```json
{"schema_version": "evidence.v1", "cwd": "P:/av-kit", "check_id": "cki-0-baseline", "command": "pwsh -NoProfile -File C:/Temp/av-kit/2026-11-26-capture-key-inbox-scrollbars/run-row.ps1 0 (task.md row 0's Validation cell, written by row-cmd.py); receipts C:/Temp/av-kit/2026-11-26-capture-key-inbox-scrollbars/cki-row0*.txt, cki-base-*.txt", "scope": "Row 0: the baseline at e5028a3, the scope, line-ending and pin records, the free-id check, the plan-local selftests and the base suites", "phase": "static", "exit_code": 0, "result": "pass", "tested_state": "HEAD e5028a3 (baseline.sha) plus rows 0 to 0", "output": "cki-base-py.txt: 3358 passed, 37 warnings in 317.40s (0:05:17). cki-base-ui.txt: Tests  1684 passed (1684). cki-row0-row-check-selftest.txt: 77 case(s), 0 wrong"}
```

```json
{"schema_version": "evidence.v1", "cwd": "P:/av-kit", "check_id": "cki-1-red-e2e", "command": "pwsh -NoProfile -File C:/Temp/av-kit/2026-11-26-capture-key-inbox-scrollbars/run-row.ps1 1 (task.md row 1's Validation cell); receipt C:/Temp/av-kit/2026-11-26-capture-key-inbox-scrollbars/cki-run-1.txt", "scope": "Row 1: the Electron Red run on mini-air, HEAD plus the two E2E files (AC-165.10, AC-166.7, AC-167.7, AC-167.8)", "phase": "red", "exit_code": 0, "result": "pass", "tested_state": "HEAD e5028a3 (baseline.sha) plus rows 0 to 1", "output": "cki-run-1.txt: summary: tests=260 expected=256 unexpected=4; result: new-failures exit=40; refused: new-failures: 4 new: AC-167.7, AC-167.8, AC-165.10, AC-166.7"}
```

```json
{"schema_version": "evidence.v1", "cwd": "P:/av-kit", "check_id": "cki-6-7-capture-key", "command": "pwsh -NoProfile -File C:/Temp/av-kit/2026-11-26-capture-key-inbox-scrollbars/run-row.ps1 6, then 7; receipts C:/Temp/av-kit/2026-11-26-capture-key-inbox-scrollbars/cki-row6*.txt, cki-row7*.txt", "scope": "AC-165.1 to AC-165.9 Red then Green, with the four named expectation changes (D-1422)", "phase": "green", "exit_code": 0, "result": "pass", "tested_state": "HEAD e5028a3 (baseline.sha) plus rows 0 to 7", "output": "cki-row6-red.txt: Tests  13 failed | 61 passed (74). cki-row6-red-check.txt: 10 required test(s), 0 problem(s). cki-row7-green.txt: Tests  13 passed (13). cki-row7-ste.txt: help-guide-ste: 0 problems. cki-row7-ste-pytest.txt: 4 passed in 0.09s"}
```

```json
{"schema_version": "evidence.v1", "cwd": "P:/av-kit", "check_id": "cki-10-green-e2e", "command": "pwsh -NoProfile -File C:/Temp/av-kit/2026-11-26-capture-key-inbox-scrollbars/run-row.ps1 10 (task.md row 10's Validation cell); receipts C:/Temp/av-kit/2026-11-26-capture-key-inbox-scrollbars/cki-run-10.txt, cki-row10-red-recheck.txt, cki-row10-remote-ok.txt", "scope": "Row 10: the Electron Green run on mini-air of every changed path under ui/ and packages/", "phase": "runtime", "exit_code": 0, "result": "pass", "tested_state": "HEAD e5028a3 (baseline.sha) plus rows 0 to 10", "output": "cki-run-10.txt: summary: tests=260 expected=260 unexpected=0 flaky=0 skipped=0 spec_files=34; result: ok exit=0. cki-row10-red-recheck.txt: remote-red: run r20261127T161201Z-091957d; tests 260; new 4; 0 problem(s). cki-row10-remote-ok.txt: remote-ok: run r20261127T170013Z-02ecd38; tests 260; 0 problem(s)"}
```

```json
{"schema_version": "evidence.v1", "cwd": "P:/av-kit", "check_id": "cki-11-canon-register", "command": "pwsh -NoProfile -File C:/Temp/av-kit/2026-11-26-capture-key-inbox-scrollbars/run-row.ps1 11 (task.md row 11's Validation cell); receipts C:/Temp/av-kit/2026-11-26-capture-key-inbox-scrollbars/cki-row11-*.txt", "scope": "Row 11: the 09 lines and Delivered notes, the grouping row, the three issues resolved, MEU-165 to MEU-167 ready_for_review", "phase": "static", "exit_code": 0, "result": "pass", "tested_state": "HEAD e5028a3 (baseline.sha) plus rows 0 to 11", "output": "cki-row11-canon.txt: row-check canon: 0 problem(s). cki-row11-issue.txt: issue-resolve: 0 problem(s). cki-row11-issues-check.txt: OK: known-issues.md is up-to-date. cki-row11-render-check.txt: Drift check passed — SSOT loaded (174 MEUs, 12 phases). cki-row11-guards.txt: row-check guards: 0 problem(s)"}
```

```json
{"schema_version": "evidence.v1", "cwd": "P:/av-kit", "check_id": "cki-h1-2-gate", "command": "$env:ELECTRON_RUN_AS_NODE=$null; rtk proxy pwsh -NoProfile -File docs/execution/plans/2026-11-26-capture-key-inbox-scrollbars/session-gate.ps1 *> C:/Temp/av-kit/2026-11-26-capture-key-inbox-scrollbars/cki-gate-h1.txt (task.md row H1-2's Validation cell); step receipts C:/Temp/av-kit/2026-11-26-capture-key-inbox-scrollbars/cki-D6-*.txt", "scope": "H1-2: the registered verification plan: identity before and after; static; openapi; targeted py-inbox and ui-capture; fresh full with nothing excused (ui-tests, py-tests, ui-build, state-render, issues-render); e2e-remote bound to row 10's run", "phase": "full", "exit_code": 0, "result": "pass", "tested_state": "e5028a3ad45fa033c388dea46658ff282fbd7364+937ef42b857984acb234116d46866c6f400165b024ddc6e8e943398619c92a78", "fresh": true, "snapshot": false, "output": "cki-gate-h1.txt: tested_state before=e5028a3ad45fa033c388dea46658ff282fbd7364+937ef42b857984acb234116d46866c6f400165b024ddc6e8e943398619c92a78 after=e5028a3ad45fa033c388dea46658ff282fbd7364+937ef42b857984acb234116d46866c6f400165b024ddc6e8e943398619c92a78; session-gate: all steps exit 0. cki-D6-py-tests.txt: 3379 passed, 37 warnings in 413.82s (0:06:53). cki-D6-ui-tests.txt: Tests  1716 passed (1716). cki-D6-e2e-remote.txt: row-check remote-fresh: 0 problem(s)"}
```

```json
{"schema_version": "evidence.v1", "cwd": "P:/av-kit", "check_id": "cki-h1-2-recheck", "command": "uv run python docs/execution/plans/2026-11-26-capture-key-inbox-scrollbars/identity.py --state-only with ELECTRON_RUN_AS_NODE unset; receipt C:/Temp/av-kit/2026-11-26-capture-key-inbox-scrollbars/cki-identity-recheck-h1-2.txt", "scope": "H1-2: the gate's tested_state re-derived after the gate process exited", "phase": "static", "exit_code": 0, "result": "pass", "tested_state": "e5028a3ad45fa033c388dea46658ff282fbd7364+937ef42b857984acb234116d46866c6f400165b024ddc6e8e943398619c92a78", "output": "cki-identity-recheck-h1-2.txt: tested_state e5028a3ad45fa033c388dea46658ff282fbd7364+937ef42b857984acb234116d46866c6f400165b024ddc6e8e943398619c92a78, equal to the gate's tested_state"}
```

```json
{"schema_version": "evidence.v1", "cwd": "P:/av-kit", "check_id": "cki-h1-3-focus", "command": "python of the H1-3 focus script (a byte write that keeps the file's line endings), then pwsh -NoProfile -File C:/Temp/av-kit/2026-11-26-capture-key-inbox-scrollbars/run-row.ps1 H1-3; receipts C:/Temp/av-kit/2026-11-26-capture-key-inbox-scrollbars/cki-render-check.txt, cki-h13-*.txt", "scope": "H1-3: MEU-165, MEU-166 and MEU-167 ready_for_review from row 11 with no new status write; the Session 103 entry on top of current-focus.md", "phase": "static", "exit_code": 0, "result": "pass", "tested_state": "e5028a3ad45fa033c388dea46658ff282fbd7364+937ef42b857984acb234116d46866c6f400165b024ddc6e8e943398619c92a78", "output": "cki-render-check.txt: ✅ Drift check passed — SSOT loaded (174 MEUs, 12 phases), rendered regions match on-disk content. cki-h13-check.txt: not ready_for_review: []"}
```

```json
{"schema_version": "evidence.v1", "cwd": "P:/av-kit", "check_id": "cki-h1-4-no-deselect", "command": "pwsh -NoProfile -File C:/Temp/av-kit/2026-11-26-capture-key-inbox-scrollbars/run-row.ps1 H1-4; receipts C:/Temp/av-kit/2026-11-26-capture-key-inbox-scrollbars/cki-h14-openapi.txt, cki-no-deselect.txt", "scope": "H1-4: the OpenAPI drift gate on the final tree; the gate's py-tests step holds no --deselect and its receipt ends passed", "phase": "static", "exit_code": 0, "result": "pass", "tested_state": "e5028a3ad45fa033c388dea46658ff282fbd7364+937ef42b857984acb234116d46866c6f400165b024ddc6e8e943398619c92a78", "output": "cki-h14-openapi.txt: no output: export_openapi.py --check found the committed document current. cki-no-deselect.txt: deselect in gate code: [] summary: 3379 passed, 37 warnings in 413.82s (0:06:53)"}
```

```json
{"schema_version": "evidence.v1", "cwd": "P:/av-kit", "check_id": "cki-h1-5-sources", "command": "view_file of .agent/context/handoffs/TEMPLATE.md, the MEU-168 handoff and the newest handoff by mtime, with sha256 into C:/Temp/av-kit/2026-11-26-capture-key-inbox-scrollbars/cki-h15-source-read.txt", "scope": "H1-5: the template and the precedent read before this handoff", "phase": "static", "exit_code": 0, "result": "pass", "tested_state": "e5028a3ad45fa033c388dea46658ff282fbd7364+937ef42b857984acb234116d46866c6f400165b024ddc6e8e943398619c92a78", "output": "cki-h15-source-read.txt: 1e013a15c3cecfc3c290b051a6e1e6c0ed07ad661f14a936fe786a92d06702be TEMPLATE.md; a3b3533993a92ec80199df332edc4b09cc1dc4cf9effafc2f6a9a826f3915d95 2026-11-26-ytdlp-challenge-and-cookie-test-MEU-168-handoff.md; a3b3533993a92ec80199df332edc4b09cc1dc4cf9effafc2f6a9a826f3915d95 2026-11-26-ytdlp-challenge-and-cookie-test-MEU-168-handoff.md; newest *-handoff.md by mtime (this session's own excluded): 2026-11-26-ytdlp-challenge-and-cookie-test-MEU-168-handoff.md"}
```

### Quality Gate Results

The gate ran twice. Run 1 stopped at ui-tests with `Tests  9 failed | 1707 passed (1716)`, each failure `Error: Test timed out in 5000ms.`, in six main-process files this session does not change, while another repository's gate loaded the PC; the six files pass alone (`Tests  99 passed (99)`, `cki-h12-diag-6files.txt`). Under D-1438 run 1's receipts are kept as `cki-gate-h1-r1.txt` and `cki-D6-*-r1.txt`, and the whole gate ran again, unchanged, once that load had ended. Run 2 (`cki-gate-h1.txt`): `tested_state before=e5028a3ad45fa033c388dea46658ff282fbd7364+937ef42b857984acb234116d46866c6f400165b024ddc6e8e943398619c92a78 after=e5028a3ad45fa033c388dea46658ff282fbd7364+937ef42b857984acb234116d46866c6f400165b024ddc6e8e943398619c92a78`, 28 steps each exit 0, last line `session-gate: all steps exit 0`. Skipped by the gate's own rules: `electron-devpc reason=D-1411 (E2E runs on mini-air; the e2e-remote step)`; `mcp-tests reason=no MCP file changed (mcp-server/ is read-only, bound by scope-paths)`.

| Step | Stage | Result | Decisive line | Receipt |
|------|-------|--------|---------------|---------|
| identity-before | identity | exit 0 | `tested_state e5028a3ad45fa033c388dea46658ff282fbd7364+937ef42b857984acb234116d46866c6f400165b024ddc6e8e943398619c92a78` | `cki-D6-identity-before.txt` |
| ui-types | static | exit 0 | `tsc --noEmit: no diagnostics` | `cki-D6-ui-types.txt` |
| ui-lint | static | exit 0 | `eslint src/ tests/ --max-warnings 0: no diagnostics` | `cki-D6-ui-lint.txt` |
| py-types | static | exit 0 | `0 errors, 0 warnings, 0 informations` | `cki-D6-py-types.txt` |
| py-lint | static | exit 0 | `All checks passed!` | `cki-D6-py-lint.txt` |
| py-format | static | exit 0 | `10 files already formatted` | `cki-D6-py-format.txt` |
| task-contract | static | exit 0 | `OK: 29 row(s); 10-column table (with builder_model); 27 row(s) fully checked: backticked, exit-code re-raised, receipt under RECEIPTS_DIR; dependencies resolve and are acyclic; 2 row(s) exempt (view_file): H1-5, H2-1` | `cki-D6-task-contract.txt` |
| scope-paths | static | exit 0 | `row-check scope-paths: 0 problem(s)` | `cki-D6-scope-paths.txt` |
| line-endings | static | exit 0 | `eol-check: 42 scope path(s), 0 problem(s)` | `cki-D6-line-endings.txt` |
| home-path | static | exit 0 | `check_home_path: ok files=3058 allowlisted=60 nul=45` | `cki-D6-home-path.txt` |
| guards | static | exit 0 | `row-check guards: 0 problem(s)` | `cki-D6-guards.txt` |
| canon | static | exit 0 | `row-check canon: 0 problem(s)` | `cki-D6-canon.txt` |
| ste-lint | static | exit 0 | `help-guide-ste: 0 problems` | `cki-D6-ste-lint.txt` |
| openapi | static | exit 0 | `export_openapi.py --check openapi.committed.json: no output` | `cki-D6-openapi.txt` |
| row-check-selftest | static | exit 0 | `row-check selftest: 77 case(s), 0 wrong []` | `cki-D6-row-check-selftest.txt` |
| red-check-selftest | static | exit 0 | `red-check selftest: 131 fixture(s) (38 positive, 93 negative), 0 wrong: []` | `cki-D6-red-check-selftest.txt` |
| eol-check-selftest | static | exit 0 | `eol-check selftest: 24 case(s), 0 wrong: []` | `cki-D6-eol-check-selftest.txt` |
| identity-selftest | static | exit 0 | `identity selftest: 0 failure(s)` | `cki-D6-identity-selftest.txt` |
| snapshot-selftest | static | exit 0 | `snapshot-commit selftest: 0 failure(s)` | `cki-D6-snapshot-selftest.txt` |
| py-inbox | targeted | exit 0 | `109 passed in 11.00s` | `cki-D6-py-inbox.txt` |
| ui-capture | targeted | exit 0 | `Tests  353 passed (353)` | `cki-D6-ui-capture.txt` |
| ui-tests | full | exit 0 | `Tests  1716 passed (1716)` | `cki-D6-ui-tests.txt` |
| py-tests | full | exit 0 | `3379 passed, 37 warnings in 413.82s (0:06:53)` | `cki-D6-py-tests.txt` |
| ui-build | full | exit 0 | `✓ built in 6.38s` | `cki-D6-ui-build.txt` |
| e2e-remote | full | exit 0 | `row-check remote-fresh: 0 problem(s)` | `cki-D6-e2e-remote.txt` |
| state-render | full | exit 0 | `✅ Drift check passed — SSOT loaded (174 MEUs, 12 phases), rendered regions match on-disk content` | `cki-D6-state-render.txt` |
| issues-render | full | exit 0 | `OK: known-issues.md is up-to-date` | `cki-D6-issues-render.txt` |
| identity-after | identity | exit 0 | `tested_state e5028a3ad45fa033c388dea46658ff282fbd7364+937ef42b857984acb234116d46866c6f400165b024ddc6e8e943398619c92a78` | `cki-D6-identity-after.txt` |

H1-4 (`cki-no-deselect.txt`): `deselect in gate code: [] summary: 3379 passed, 37 warnings in 413.82s (0:06:53)`.

---

## Changed Files

Counts are added / removed lines against `HEAD` `e5028a3` (`git diff --numstat --ignore-cr-at-eol HEAD`); a new file's count is its line count. Line endings were measured as bytes by the gate's `line-endings` step (`eol-check: 42 scope path(s), 0 problem(s)`).

| File | Change | Added / removed |
|------|--------|-----------------|
| `ui/src/renderer/src/features/capture/capture-key.ts` | `CAPTURE_KEY_DEFAULT` and `captureKeyText` | new, 15 |
| `ui/src/renderer/src/features/capture/useCaptureSettings.ts` | the hook returns `saved`, the saved settings | +7 / -0 |
| `ui/src/renderer/src/features/capture/CapturePage.tsx` | the texts from the saved key, the status follow and the unconfirmed notice (also MEU-166's refresh) | +170 / -14 |
| `ui/src/renderer/src/features/capture/capture-help-content.ts` | the token texts and `captureHelpSections` | +20 / -6 |
| `ui/src/renderer/src/features/settings/settings-help-content.ts` | the startup topic's token and `settingsHelpSections` | +16 / -2 |
| `ui/src/renderer/src/features/settings/SettingsPage.tsx` | the help card from the saved key | +2 / -2 |
| `ui/src/renderer/src/components/help/HelpCard.tsx` | takes the per-key page | +8 / -3 |
| `ui/src/renderer/src/components/help/quick-start.ts` | `quickStartPage(feature, key)`; `QUICK_START.capture` is the default reading | +25 / -1 |
| `ui/src/renderer/src/components/help/quick-start.json` | step 1 holds `{captureKey}` | +1 / -1 |
| `ui/tests/unit/capture-key.test.ts` | AC-165.1, AC-165.4, AC-165.9 | new, 96 |
| `ui/tests/unit/capture-key.behavior.test.ts` | AC-165.2, guard AC-165.3, AC-165.5 to AC-165.8 | new, 404 |
| `ui/tests/unit/capture-page.test.ts` | D-1422: `:112` `'When {captureKey} is in use'`, `:117` `'Close to tray keeps {captureKey}'`, `:328` `/Press \{captureKey\} or Capture region/` | +3 / -3 |
| `ui/tests/unit/settings-page.test.ts` | D-1422: `:771` `expect(help).toContain('{captureKey}')` | +1 / -1 |
| `ui/tests/e2e/help-quick-start.test.ts` | `:136` the stored steps read through `captureKeyText` with the default key; the expected value is unchanged (D-1422) | +5 / -1 |
| `ui/tests/help-shots/help-shots.shots.ts` | `:64` to `:68` `stepsHash` hashes the default reading; the hash is unchanged (D-1422) | +5 / -1 |
| `ui/tests/e2e/capture-settings-draft.test.ts` | AC-165.10 at `:337` (and MEU-166's AC-166.7) as added lines | +223 / -2 |
| `docs/build-plan/09-screenshot-capture.md` | the empty-state line, the scope sentence, three table rows, the Pan gestures row and the three Delivered notes (row 11) | +25 / -6 |
| `.agent/context/known-issues.yaml`, `.agent/context/known-issues.md` | the three issues resolved, then rendered | +15 / -15; +3 / -6 |
| `.agent/context/meu-status.yaml`, `.agent/context/meu-registry.md`, `docs/BUILD_PLAN.md` | MEU-165 to MEU-167 `ready_for_review`, then rendered | +15 / -15; +3 / -3; +1 / -1 |
| `.agent/context/grouping/2026-11-26-ui-findings-and-auto-update-session-grouping.md` | row 103 reads `executed (Session 103)` | +1 / -1 |
| `.agent/context/current-focus.md` | the Session 103 entry on top (H1-3) | +3 / -0 |

The `-2` of `capture-settings-draft.test.ts` is its two `import` lines (`node:fs`, `node:path`), re-added with more names, which `row-check.py guards` allows. The plan folder's own scripts are new and untracked with the plan. Nothing is committed or staged.

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
| Picking up a key changed outside the Capture page (the MCP settings tool, another window) before the page reads its settings again | out-of-scope | — | Plan §Out of Scope; register an issue if Mat reports it |
| README text and the default key | out-of-scope | — | D-1400 ("README text and code defaults keep `F2`") |
| Retaking help images | out-of-scope | Session 105 retakes by script for its own change | D-1421 (the default reading) |
| IPC, preload and MCP tool changes | out-of-scope | — | The grouping gate |
| Commit and push | out-of-scope | — | Only on Mat's direction (H2) |

### Departures and their basis

These cover the whole session; the MEU-166 and MEU-167 handoffs list only their own.

- **Execution decisions D-1433 to D-1438** (autonomous, in the plan's YAML; every reasoning starts with Mat's hand-over). D-1433: row 11's canon edit accepts the grouping cell `plan approved (round 2)`. D-1434: the free-name check of row 0 counts a hyphen as part of a token. D-1435: AC-165.10 and AC-166.7 set the 240 s test budget that AC-151.14 sets. D-1436: row 4's test harness was amended and row 4's Red run again. D-1437: stale Vitest transforms were removed, row 6's harness clears `localStorage`, and row 6's Red run again. D-1438: the first H1-2 run's timeouts (below).
- **Scripts.** The plan-local scripts were copied from Session 104's folder and adapted; `session-gate.ps1` was written at row 0. `py-lint` also covers the plan folder's Python.
- **Row 0's lint** was run again alone, after its first run printed the `RECEIPTS_DIR` fail-closed note.
- **Row 1** added test-local helpers and imports to the two E2E files, as added lines. AC-167.8 sets the theme by the root `dark` class.
- **Row 2's census test** reads the method-list receipt only when it exists. **Row 3** fixed one ruff docstring line.
- **Row 5 (MEU-166).** The hook returns `saved`, and the page keeps the pending inbox until a list answer.
- **Row 6** fixed the jsdom URL of the new behaviour test.
- **The follow design (D-1420).** While the status names another key, the banner and the key cap stay hidden.
- **Row 7** widened the `help-shots.shots.ts` span to `:64` to `:68` (three added lines and the hash call), with the expected hash unchanged.
- **Rows 8 and 9 (MEU-167).** The module API, `value` rounded in the module, the `ViewportScrollBar` anchor for the source scan, the `capture-fit-map.ts` LF sha256 pin, `aria-controls` through `useId`, and a thumb that stops its mouse, click and `lostpointercapture` events; row 9 fixed a `-0` from the clamped share in `capture-scroll-bars.ts`.
- **Row 11.** The grouping edit went into `canon-edit.py`'s `EDITS`, because row 11's command has no grouping step; the `EDITS` strings were written at 96 columns and set by `ruff format`. `crlf.py` wrote `known-issues.yaml` and `known-issues.md` as CRLF on disk, by design; the `HEAD` blobs are LF.
- **The gate ran twice (D-1438).** See Quality Gate Results. No test was excused, deselected or given a longer timeout.
- **How the rows ran.** Each row ran through `run-row.ps1`, written from `task.md` by `row-cmd.py`, with `ELECTRON_RUN_AS_NODE` cleared. No Electron ran on the dev PC; the E2E ran on mini-air only, through `e2e_remote.py`. No user data was read: every launch used scratch app data and temp inbox folders.
- **current-focus.md** keeps CRLF on disk, as the H1-3 cell says; the H1-3 script keeps the file's own endings, and the `HEAD` blob is LF.

---

## Decision Log

None.

---

## History

| Event | Date | Agent | Detail |
|-------|------|-------|--------|
| Created | 2026-11-27 | claude-code-local (Claude Opus 5.5) | Handoff after the H1-2 gate, H1-3, H1-4 and H1-5 |
