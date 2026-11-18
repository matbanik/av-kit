---
date: "2026-11-18"
project: "2026-11-17-ui-small-fixes"
meu: "MEU-159"
status: "complete"
action_required: "VALIDATE_AND_APPROVE"
template_version: "2.2"
verbosity: "standard"
plan_source: "docs/execution/plans/2026-11-17-ui-small-fixes/implementation-plan.md"
build_plan_section: "docs/build-plan/11-page-layout.md §Downloader Advanced gap (residual) (MEU-159, matrix 11.14)"
agent: "claude-code-local (Claude Opus 5.5)"
reviewer: "codex (H1-7 execution review)"
predecessor: "2026-11-17-video-tail-frame-MEU-160-handoff.md"
---

# Handoff: 2026-11-17-ui-small-fixes-MEU-159-handoff

> **Status**: `complete`
> **Action Required**: `VALIDATE_AND_APPROVE`

---

## Scope

**MEU**: MEU-159 Downloader Advanced gap (phase 11, band P2, matrix 11.14, depends on MEU-53), registered from `DOWNLOADER-ADVANCED-PANEL-GAP` (triage D-1129).
**Build Plan Section**: `docs/build-plan/11-page-layout.md` §Downloader Advanced gap (residual), under §Downloader page layout (MEU-53).
**Predecessor**: [2026-11-17-video-tail-frame-MEU-160-handoff.md](2026-11-17-video-tail-frame-MEU-160-handoff.md), Session 93, committed as `9867e51`. Session 94 is the fourth session run of the 2026-11-17 value triage grouping (`.agent/context/grouping/2026-11-17-value-triage-session-grouping.md`), run from `9867e51`. Its other handoffs: [MEU-158](2026-11-17-ui-small-fixes-MEU-158-handoff.md) and [the preview fix](2026-11-17-ui-small-fixes-handoff.md).

- **The cause, measured first (D-1180).** Row 3 measured the unchanged build at 1280×800 and 700×650, Advanced collapsed and expanded (`us-row3-measure.txt`, one `S94-GAP` line per case). In all four cases the space is held by the empty status wrapper under the add form, `<div className="min-h-6 max-w-[var(--layout-page-max-width)]">` at `DownloaderPage.tsx:818`, 24 px high with no text, plus one 16 px row gap: `status wrapper heights: {"1280-collapsed": 24.0, "1280-expanded": 24.0, "700-collapsed": 24.0, "700-expanded": 24.0}`, `cause: the empty status wrapper`. The scrollable space below the disclosure (TAIL) read 40.5 px and the distance from the disclosure to the queue (GAP) 56 px in each case, where one gap is 16 px. The Advanced panel takes no height when collapsed, so the hypothesis held and S9 did not fire.
- **The fix (`STATUS_SLOT`, D-1177).** The wrapper gets `hidden={!addStatus && !error}`: it is hidden while both the add status and the error banner are empty, and shows as before when either has text. No class, test id or control changes.
- **The limit (D-1177).** Nothing clears either message, so the band is closed on a fresh page only: once a message has shown, the line stays with its text and the queue sits one line plus a gap lower for the rest of the session, as today (AC-159.5 guards that line).
- **Advanced unchanged.** Expanded, the panel still holds `sabr-status`, `sabr-check-btn`, `sabr-force-btn`, `sabr-clear-btn`, `cookie-browser`, `cookie-profile`, `cookie-file` and `cookie-test-btn` once each, in that order, and the visible set matches the cookie mode shown (AC-159.3, AC-159.4).
- **The README screenshot is not retaken (D-1129).**
- **Records.** MEU-159 is `ready_for_review` with this plan folder; `DOWNLOADER-ADVANCED-PANEL-GAP` is `resolved` with `meu_links: [MEU-159]`; 11 carries the `Delivered (Session 94)` note; grouping row 94 reads `executed (Session 94)`.

**What Mat sees.** On a fresh Downloader page the extra empty band between the Advanced disclosure and the queue is gone: the queue now starts one normal gap below Advanced, at full width and at 700 px, with Advanced open or closed. After an Add or a SABR or cookie action shows a message, the message line appears where it always did and stays for the session. Nothing else on the page moves or changes.

**Plan:** [implementation-plan.md](../../../docs/execution/plans/2026-11-17-ui-small-fixes/implementation-plan.md) §Single-statement contracts. **Execution authorization:** `USER_EXPLICIT`, 2026-11-17 ("orchestrate the plan creation for all sessions and proceed with execution for each"), `plan_to_exec_gate: human`; the plan review approved at round 2 (`.agent/context/handoffs/2026-11-17-ui-small-fixes-plan-critical-review.md`). Receipts named by file name alone are in the session's receipts folder (the `ui-small-fixes` folder under `RECEIPTS_DIR`).

---

## Acceptance Criteria

| AC | Type | Description | Source | Test(s) | Status |
|----|------|-------------|--------|---------|--------|
| AC-159.1 | check | Row 3 on the unchanged build at 1280×800 and 700×650, collapsed and expanded: the boxes, the scroller, the queue's top and the element that holds the space, with its height; the status text, the eight Advanced ids in DOM order, their visibility and the cookie mode | Local Canon (11 Cause row) | row 3 `us-row3-measure.txt`, `us-row3-check.txt` | ✅ the empty status wrapper, 24 px, in all four cases |
| AC-159.2 | e2e | A fresh page at 1280×800, Advanced collapsed, scrolled to the end: the status empty, its placeholders hidden, the eight ids in order and none visible, TAIL ≤ 1 px and GAP = 16 ± 1 px | Local Canon (11 Collapsed row) | `ui/tests/e2e/downloader-advanced-gap.test.ts:327` | ✅ |
| AC-159.3 | e2e | The same with Advanced expanded: each id once, in order; the visible set matches the cookie mode shown; TAIL ≤ 1 px and GAP = 16 ± 1 px; nothing clicked | Local Canon (11 Expanded and Tests rows) | `ui/tests/e2e/downloader-advanced-gap.test.ts:333` | ✅ |
| AC-159.4 | e2e | AC-159.2 and AC-159.3's checks, each on its own, at 700×650, collapsed and expanded | Session 88 RULE-1 | `ui/tests/e2e/downloader-advanced-gap.test.ts:340` | ✅ |
| AC-159.5 | e2e (guard) | An Add with the URL empty shows "URL is required" in the status wrapper where it shows today, above the queue; not cleared afterwards; no request leaves the renderer | Local Canon (11 §Downloader page layout, MEU-53) | `ui/tests/e2e/downloader-advanced-gap.test.ts:349` | ✅ passed at Red (guard) |
| AC-159.6 | check | Row 4 and the gate: the Downloader unit and layout files and the `download-queue.test.ts` and `layout-primitives.test.ts` E2E suites pass unchanged | Local Canon (11 Tests row) | row 4 `us-159-green.txt`; row 7; gate `meu-159-unit`, `e2e-download-queue`, `e2e-layout-primitives` | ✅ |
| AC-159.7 | check | Row 7: `downloader-advanced-gap.test.ts` passes 3 runs of 3, with no `flaky` and no `unhandled rejection:` line | Mat 2026-11-16 | row 7 `us-row7-gap-r1.txt` to `-r3.txt`, `us-row7-repeat.txt` | ✅ 3 of 3 |
| Downloader pins (cross-ref) | guard | `ui/tests/unit/downloader-page.test.ts:519-555` (the layout classes), `downloader-page.behavior.test.ts`, `layout-canon.test.ts`, `layout-primitives.test.ts`; `ui/tests/e2e/download-queue.test.ts` (its 700 px case at `:1574`) and `ui/tests/e2e/layout-primitives.test.ts`: no edit | Local Canon (§Test pins) | row 4; row 7; gate | ✅ |
| AC-158.1 to AC-158.14 (cross-ref) | reference | MEU-158, F1 help waits for the page: the held-request helper, F1's route scope and its take on mount; owned by `.agent/context/handoffs/2026-11-17-ui-small-fixes-MEU-158-handoff.md` (AC-158.1, AC-158.2, AC-158.3, AC-158.4, AC-158.5, AC-158.6, AC-158.7, AC-158.8, AC-158.9, AC-158.10, AC-158.11, AC-158.12, AC-158.13, AC-158.14) | Local Canon (06 Held, Once and Shared rows) | that handoff | n/a: not this handoff's |
| AC-1, AC-2, AC-3, AC-4 and AC-5 (cross-ref) | reference | The preview fix (no MEU, D-1130): the preview wrapper script, its package script and the proofs with `ELECTRON_RUN_AS_NODE` set and unset; owned by `.agent/context/handoffs/2026-11-17-ui-small-fixes-handoff.md` | Local Canon (D-1130, D-1178) | that handoff | n/a: not this handoff's |

<!-- CACHE BOUNDARY -->

---

## Evidence

### FAIL_TO_PASS

| Test | Red Output (hash/snippet) | Green Output | File:Line |
|------|---------------------------|--------------|-----------|
| AC-159.2 | `Expected: <= 1`, `Received:    40.5` (`us-159-red-e2e.txt`, `3 failed`) | Row 4: `4 passed (13.3s)` (`us-159-green-e2e.txt`) | `ui/tests/e2e/downloader-advanced-gap.test.ts:327` |
| AC-159.3 | `Expected: <= 1`, `Received:    40.5` (`us-159-red-e2e.txt`, `3 failed`) | Row 4: `4 passed (13.3s)` (`us-159-green-e2e.txt`) | `ui/tests/e2e/downloader-advanced-gap.test.ts:333` |
| AC-159.4 | `Expected: <= 1`, `Received:    40.5` (`us-159-red-e2e.txt`, `3 failed`) | Row 4: `4 passed (13.3s)` (`us-159-green-e2e.txt`) | `ui/tests/e2e/downloader-advanced-gap.test.ts:340` |

AC-159.5 passed at Red and is a guard (`us-159-red-e2e-hashes.txt`); AC-159.1, AC-159.6 and AC-159.7 are checks.

- **Row 0 baseline** (`us-baseline.txt`): `baseline: all steps exit 0`, `eol-check: 31 scope path(s), 0 problem(s)`, `baseline-scope.json 58 paths; 7 absent`. UI Vitest at base: `Test Files  142 passed (142)`, `Tests  1619 passed (1619)` (`us-base-ui.txt`).
- **Row 3 measurement** (`us-row3-measure.txt`, load 7.3 %): per case, the status box 24 px high with class `min-h-6 max-w-[var(--layout-page-max-width)]` and `"statusText":""`, `"rowGap":16`, `"TAIL":40.5`, `"GAP":56`, `"cookieMode":"none"`, and the eight `panelDomIds` in the order above, none visible collapsed. The check (`us-row3-check.txt`): `'1280-collapsed': {'line': True, 'statusEmpty': True, 'fit': True, 'domOrder': True, 'visibleByMode': True}`, the same for the other three cases, `1 passed: True probe file absent: True`. The 1280 cases ran in a 1280×800 window whose page viewport reads 1267×739; the 700 cases at 700×650.
- **Row 3a Red E2E** (`us-159-red-e2e.txt`; load 8.0 %): `3 failed`, `1 passed (14.3s)`; AC-159.2 to AC-159.4 failed on TAIL, `Expected: <= 1`, `Received:    40.5`; `red-check: 1 receipt(s), 3 required test(s), 0 problem(s)` (`us-159-red-e2e-check.txt`); `AC-159.5 guard passing at Red: True unhandled rejection: False CR in the new file: False` (`us-159-red-e2e-hashes.txt`).
- **Row 4 Green** (`us-159-green.txt`): `Test Files  4 passed (4)`, `Tests  102 passed (102)`; E2E `4 passed (13.3s)` (`us-159-green-e2e.txt`; load 5.0 %); `test-side files changed since Red: [] pin files changed since row 0: []` (`us-159-immutable.txt`).
- **Row 7** (`us-row7-repeat.txt`): `gap runs passing: [True, True, True]`; `suites clean: {'us-row7-help-search': True, 'us-row7-keyboard': True, 'us-row7-download-queue': True, 'us-row7-layout-primitives': True}`. The runs: `4 passed (13.2s)`, `4 passed (13.0s)`, `4 passed (13.2s)` (`us-row7-gap-r1.txt` to `-r3.txt`; loads 8.9 %, 8.7 %, 12.3 %); `26 passed (28.1s)` (`us-row7-download-queue.txt`); `1 passed (1.1s)` (`us-row7-layout-primitives.txt`).
- **Row 8 records** (`us-issue-resolve.txt`): `decision logs read: 104 of 104`, `register sha256 before=01b1a5b0a6645256dbf2905c9136c8b8219332f761771f711cc992757cc15159`, `target sha256 after=0583a9c0d5837e6588d53a05595363154d880fcac1fb0db8d906a1cff056a251 CRLF=0 LF=5742`, `parsed fields changed: 15`, `issue-resolve: 0 problem(s)`; `Rendered known-issues.md: 36 lines` (`us-issues-render.txt`); MEU-159 updated to `ready_for_review (updated: 2026-11-18)` (`us-status-159.txt`).
- **H1-1** (`task-unchecked.txt`): `unchecked implementation rows: []`.

### Commands Executed

```json
{"schema_version": "evidence.v1", "cwd": "P:/av-kit", "check_id": "us159-0-baseline", "command": "pwsh -NoProfile -File C:/Temp/av-kit/ui-small-fixes/run-row0.ps1 (task.md row 0's Validation cell without its uv sync step: baseline.ps1 records baseline.sha, the dirty list and hashes, the scope, line-ending and skip hashes, the cited anchors, the plan-local selftests and the base UI Vitest suite); receipts us-baseline.txt, us-base-ui.txt", "scope": "Row 0: the baseline at 9867e51 and the plan-local checkers", "phase": "static", "exit_code": 0, "result": "pass", "tested_state": "HEAD 9867e51 (baseline.sha) plus row 0", "output": "us-baseline.txt: baseline.sha 9867e51f0024a113de6a585b42b54695f1e4bccb; baseline-dirty.txt 17 paths, 5 foreign; baseline-scope.json 58 paths; 7 absent; baseline-skip-hashes.json 362 files under packages/, mcp-server/, tests/ and tools/; baseline-citations.txt 45 anchors; eol-check: 31 scope path(s), 0 problem(s); baseline: all steps exit 0. us-base-ui.txt: Test Files  142 passed (142); Tests  1619 passed (1619)."}
```

```json
{"schema_version": "evidence.v1", "cwd": "P:/av-kit", "check_id": "us159-3-measure", "command": "pwsh -NoProfile -File C:/Temp/av-kit/ui-small-fixes/run-row3.ps1 (task.md row 3's Validation cell: host-wait, the UI build, the S94-GAP probe spec copied into ui/tests/e2e and removed after, the measurement check); receipts us-row3-load.txt, us-row3-measure.txt, us-row3-check.txt", "scope": "AC-159.1 (D-1180): the gap measured on the unchanged build at 1280x800 and 700x650, collapsed and expanded", "phase": "runtime", "exit_code": 0, "result": "pass", "tested_state": "HEAD 9867e51 (baseline.sha) plus rows 0 to 3", "output": "load 7.3 %. us-row3-measure.txt: four S94-GAP lines, each with status height 24, statusClass min-h-6 max-w-[var(--layout-page-max-width)], statusText empty, rowGap 16, TAIL 40.5, GAP 56, cookieMode none and the eight panel ids in order; status wrapper heights: {\"1280-collapsed\": 24.0, \"1280-expanded\": 24.0, \"700-collapsed\": 24.0, \"700-expanded\": 24.0}; cause: the empty status wrapper. us-row3-check.txt: every case line, statusEmpty, fit, domOrder and visibleByMode True; 1 passed: True probe file absent: True."}
```

```json
{"schema_version": "evidence.v1", "cwd": "P:/av-kit", "check_id": "us159-3a-red-e2e", "command": "pwsh -NoProfile -File C:/Temp/av-kit/ui-small-fixes/run-row3a.ps1 (task.md row 3a's Validation cell: host-wait, Playwright on downloader-advanced-gap.test.ts, red-check.py --require AC-159.2 to AC-159.4, the hash check); receipts us-159-red-e2e.txt, us-159-red-e2e-check.txt, us-159-red-e2e-hashes.txt", "scope": "AC-159.2 to AC-159.4 Red in real Electron; AC-159.5 guard passes at Red", "phase": "red", "exit_code": 0, "result": "pass", "tested_state": "HEAD 9867e51 (baseline.sha) plus rows 0 to 3a", "output": "load 8.0 %. us-159-red-e2e.txt: 3 failed; 1 passed (14.3s); Expected: <= 1, Received: 40.5. us-159-red-e2e-check.txt: red-check: 1 receipt(s), 3 required test(s), 0 problem(s). us-159-red-e2e-hashes.txt: AC-159.5 guard passing at Red: True unhandled rejection: False CR in the new file: False."}
```

```json
{"schema_version": "evidence.v1", "cwd": "P:/av-kit", "check_id": "us159-4-green", "command": "pwsh -NoProfile -File C:/Temp/av-kit/ui-small-fixes/run-row4.ps1 (task.md row 4's Validation cell: the Downloader and layout unit files, typecheck, lint, host-wait, the build, Playwright on downloader-advanced-gap.test.ts, the immutability check); receipts us-159-green.txt, us-159-green-e2e.txt, us-159-immutable.txt", "scope": "AC-159.2 to AC-159.6 Green after STATUS_SLOT", "phase": "green", "exit_code": 0, "result": "pass", "tested_state": "HEAD 9867e51 (baseline.sha) plus rows 0 to 4", "output": "us-159-green.txt: Test Files  4 passed (4); Tests  102 passed (102). us-159-green-e2e.txt: 4 passed (13.3s) (load 5.0 %). us-159-immutable.txt: test-side files changed since Red: [] pin files changed since row 0: []."}
```

```json
{"schema_version": "evidence.v1", "cwd": "P:/av-kit", "check_id": "us159-7-repeats", "command": "pwsh -NoProfile -File C:/Temp/av-kit/ui-small-fixes/run-row7.ps1 (task.md row 7's Validation cell: host-wait before each run, downloader-advanced-gap.test.ts three times, download-queue.test.ts and layout-primitives.test.ts once, the repeat check); receipts us-row7-gap-r1.txt to us-row7-gap-r3.txt, us-row7-download-queue.txt, us-row7-layout-primitives.txt, us-row7-repeat.txt", "scope": "AC-159.6 and AC-159.7: three gap runs and the Downloader E2E suites", "phase": "runtime", "exit_code": 0, "result": "pass", "tested_state": "HEAD 9867e51 (baseline.sha) plus rows 0 to 7", "output": "us-row7-gap-r1.txt: 4 passed (13.2s) (load 8.9 %); us-row7-gap-r2.txt: 4 passed (13.0s) (load 8.7 %); us-row7-gap-r3.txt: 4 passed (13.2s) (load 12.3 %); us-row7-download-queue.txt: 26 passed (28.1s) (load 9.7 %); us-row7-layout-primitives.txt: 1 passed (1.1s) (load 21.4 %). us-row7-repeat.txt: gap runs passing: [True, True, True]; suites clean: {'us-row7-help-search': True, 'us-row7-keyboard': True, 'us-row7-download-queue': True, 'us-row7-layout-primitives': True}."}
```

```json
{"schema_version": "evidence.v1", "cwd": "P:/av-kit", "check_id": "us159-8-records", "command": "python C:/Temp/av-kit/ui-small-fixes/write-set.py (issue-resolve-set.json, LF); python C:/Temp/av-kit/ui-small-fixes/row8-docs.py (the 06 and 11 Delivered notes and commands.md:80, CRLF kept, and grouping row 94, LF kept, by bytes); pwsh -NoProfile -File C:/Temp/av-kit/ui-small-fixes/run-row8.ps1 (task.md row 8's Validation cell: issue-resolve.py bound to the row-0 register hash, issue_triage.py render and render --check, meu_status.py update MEU-158 and MEU-159 ready_for_review --plan, the row 8 check)", "scope": "Row 8: the three issues resolved, MEU-158 and MEU-159 ready_for_review, the Delivered notes, COMMANDS_DOC and grouping row 94", "phase": "static", "exit_code": 0, "result": "pass", "tested_state": "HEAD 9867e51 (baseline.sha) plus rows 0 to 8", "output": "us-issue-resolve.txt: decision logs read: 104 of 104; register sha256 before=01b1a5b0a6645256dbf2905c9136c8b8219332f761771f711cc992757cc15159; target sha256 after=0583a9c0d5837e6588d53a05595363154d880fcac1fb0db8d906a1cff056a251 CRLF=0 LF=5742; parsed fields changed: 15; issue-resolve: 0 problem(s). us-issues-render.txt: Rendered known-issues.md: 36 lines. us-issues-render-check.txt: OK: known-issues.md is up-to-date. us-status-158.txt and us-status-159.txt: Updated to ready_for_review (updated: 2026-11-18). us-row8-check.txt: grouping LF: True; all three issues resolved."}
```

```json
{"schema_version": "evidence.v1", "cwd": "P:/av-kit", "check_id": "us159-h1-2-session-gate", "command": "pwsh -NoProfile -File C:/Temp/av-kit/ui-small-fixes/run-rowH1-2.ps1 (task.md row H1-2's Validation cell: rtk proxy pwsh -NoProfile -File docs/execution/plans/2026-11-17-ui-small-fixes/session-gate.ps1 *> C:/Temp/av-kit/ui-small-fixes/us-gate-h1.txt); step receipts us-D6-<step>.txt and us-D6-<step>-load.txt", "scope": "H1-2: the PROFILE D6 session gate, 31 steps from identity-before to identity-after: static checks, the three targeted unit sets, host-load, the full UI Vitest suite, the preview proof, the UI build, eight Electron E2E steps (each after a host-wait at or below 50 %), the state and issue renders; py-tests, py-types, openapi, mcp-* and e2e-other skipped with their reasons", "phase": "full", "exit_code": 0, "result": "pass", "fresh": true, "snapshot": false, "tested_state": "9867e51f0024a113de6a585b42b54695f1e4bccb+0fb04e34a3879c5f491b2eb6fc42782c63314539f0e05a2bc03cb8494d11c42e", "output": "us-gate-h1.txt: every step exit=0; session-gate: all steps exit 0. identity before and after: tested_state 9867e51f0024a113de6a585b42b54695f1e4bccb+0fb04e34a3879c5f491b2eb6fc42782c63314539f0e05a2bc03cb8494d11c42e. host-load: ran at 9.3 %. us-D6-ui-tests.txt: Test Files  144 passed (144); Tests  1628 passed (1628). us-D6-preview-proof.txt: window: yes (after 17 s; window), notice: yes, notice on stdout: no, left: 0, PASS: window opened, notice as expected, nothing left. E2E: e2e-help-f1-mount 5 passed (25.4s); e2e-browse-mount 4 passed (28.1s); e2e-ctrl-o 1 passed (1.1s); e2e-help-search 3 passed (2.1s); e2e-keyboard-shortcuts 2 passed (1.9s); e2e-advanced-gap 4 passed (12.7s); e2e-download-queue 26 passed (26.4s); e2e-layout-primitives 1 passed (982ms). OK: 29 row(s); changed paths: 46 outside scope: [] other sessions plan files skipped: 4; eol-check: 31 scope path(s), 0 problem(s); check_home_path: ok files=2671 allowlisted=60 nul=31; OK: known-issues.md is up-to-date."}
```

```json
{"schema_version": "evidence.v1", "cwd": "P:/av-kit", "check_id": "us159-h1-3-h1-4-closeout-checks", "command": "python C:/Temp/av-kit/ui-small-fixes/focus-entry.py (the Session 94 entry on top of .agent/context/current-focus.md, by bytes, CRLF kept); pwsh -NoProfile -File C:/Temp/av-kit/ui-small-fixes/run-rowH1-3.ps1 (meu_status.py render --check, meu_status.py get MEU-158 and MEU-159, the ready check); pwsh -NoProfile -File C:/Temp/av-kit/ui-small-fixes/run-rowH1-4.ps1 (task.md row H1-4's skip-basis check)", "scope": "H1-3 (current focus, the state render, MEU-158 and MEU-159 ready_for_review) and H1-4 (the Python, OpenAPI and MCP skip basis)", "phase": "static", "exit_code": 0, "result": "pass", "tested_state": "the H1-2 state plus H1-3's current-focus entry (identity.py excludes current-focus.md)", "output": "focus-entry: current-focus: bytes 89795 -> 91475 CRLF 221 -> 224 bare LF 0. us-render-check.txt: Drift check passed. us-h13-check.txt: ready_for_review: {'MEU-158': True, 'MEU-159': True}. skip-basis-check.txt: packages, mcp-server, tests or tools changes since row 0: []."}
```

### Quality Gate Results

| Step | Result (receipt) |
|------|------------------|
| Gate | `session-gate: all steps exit 0` (`us-gate-h1.txt`); 31 steps, each `exit=0` |
| Identity | `tested_state 9867e51f0024a113de6a585b42b54695f1e4bccb+0fb04e34a3879c5f491b2eb6fc42782c63314539f0e05a2bc03cb8494d11c42e`, equal before and after (`us-D6-identity-before.txt`, `us-D6-identity-after.txt`) |
| Task contract | `OK: 29 row(s)`; `2 row(s) exempt (view_file): H1-5, H2-1` (`us-D6-task-contract.txt`) |
| Scope | `changed paths: 46 outside scope: [] other sessions plan files skipped: 4`; `read-never-changed files: 36 mismatch: [] baseline-dirty hash mismatch: []`; `temporary probe files present: []`; `head moved (S4): False` (`us-D6-scope-paths.txt`) |
| Line endings | `eol-check: 31 scope path(s), 0 problem(s)` (`us-D6-line-endings.txt`) |
| Home path | `check_home_path: ok files=2671 allowlisted=60 nul=31` (`us-D6-home-path.txt`) |
| Selftests | `red-check selftest: 91 fixture(s) (22 positive, 69 negative), 0 wrong: []`; `eol-check selftest: 19 case(s), 0 wrong: []`; `preview-proof selftest: 0 failure(s)` (`us-D6-red-check-selftest.txt`, `us-D6-eol-check-selftest.txt`, `us-D6-preview-proof-selftest.txt`) |
| Static | `ui-types` and `ui-lint` exit 0; `node --check ui/scripts/electron-vite-preview.mjs exit 0` (`us-D6-scripts-syntax.txt`); `7 files already formatted` (`us-D6-py-format.txt`); `All checks passed!` (`us-D6-py-lint.txt`) |
| Targeted | `meu-158-unit` `Tests  202 passed (202)`; `meu-159-unit` `Tests  102 passed (102)`; `preview-unit` `Tests  4 passed (4)` |
| Host load | `host-load: ran at 9.3 %` (`us-D6-host-load.txt`); each Electron step waited first (`us-D6-<step>-load.txt`, D-1181) |
| UI, full | `Test Files  144 passed (144)`, `Tests  1628 passed (1628)` (`us-D6-ui-tests.txt`; row 0 had 142 files and 1619 tests, and the session adds two files with nine tests: seven in `help-f1-hold.test.tsx`, two in `preview-script.test.ts`) |
| Preview proof (AC-4) | `PASS: window opened, notice as expected, nothing left`, after `window: yes (after 17 s; window)` and `notice on stdout: no` (`us-D6-preview-proof.txt`; load 7.5 %) |
| UI build | exit 0 (`us-D6-ui-build.txt`) |
| Electron E2E | `e2e-help-f1-mount` `5 passed (25.4s)` (load 7.3 %); `e2e-browse-mount` `4 passed (28.1s)` (load 7.5 %); `e2e-ctrl-o` `1 passed (1.1s)` (load 8.0 %); `e2e-help-search` `3 passed (2.1s)` (load 8.0 %); `e2e-keyboard-shortcuts` `2 passed (1.9s)` (load 8.8 %); `e2e-advanced-gap` `4 passed (12.7s)` (load 8.0 %); `e2e-download-queue` `26 passed (26.4s)` (load 8.7 %); `e2e-layout-primitives` `1 passed (982ms)` (load 8.3 %); none with a failed, flaky or `unhandled rejection:` line |
| Registers | `OK: known-issues.md is up-to-date` (`us-D6-issues-render-check.txt`); the state render's drift check passed (`us-D6-state-render.txt`) |
| Skipped | `py-tests`, `py-types`, `openapi` and `mcp-types/mcp-build/mcp-tests/mcp-audit`, each printed with its reason (every file under `packages/`, `mcp-server/`, `tests/` and `tools/` keeps its row-0 hash; S10), and `e2e-other` (only the help toggle, the Convert browse hold, the Downloader status slot and the preview script changed, and their suites run; the clipboard specs never run) (`us-gate-h1.txt`) |
| H1-1 | `unchecked implementation rows: []` (`task-unchecked.txt`) |
| H1-3 | `current-focus: bytes 89795 -> 91475 CRLF 221 -> 224 bare LF 0`; the state render's drift check passed (`us-render-check.txt`); `ready_for_review: {'MEU-158': True, 'MEU-159': True}` (`us-h13-check.txt`) |
| H1-4 | `packages, mcp-server, tests or tools changes since row 0: []` (`skip-basis-check.txt`) |
| MEU-159 in the gate | `e2e-advanced-gap` `4 passed (12.7s)`, `e2e-download-queue` `26 passed (26.4s)`, `e2e-layout-primitives` `1 passed (982ms)`; `meu-159-unit` `Tests  102 passed (102)` |

---

## Changed Files

Counts are added / removed lines against `HEAD` `9867e51` (`git diff --numstat --ignore-cr-at-eol`); a new file's count is its line count. Line endings were measured as bytes (the gate's `line-endings` step: `eol-check: 31 scope path(s), 0 problem(s)`). The whole session's change set is listed in each handoff; the rows that are MEU-159's are `DownloaderPage.tsx`, `downloader-advanced-gap.test.ts` and the 11 note.

| File | Change | Added / removed | Line endings |
|------|--------|-----------------|--------------|
| `ui/src/renderer/src/lib/shell-nav.ts` | `HELD_REQUEST` (`createHeldRequest` at `:36`), `CURRENT_ROUTE` (`currentRoute` at `:14`) | +72 / -0 | LF kept |
| `ui/src/renderer/src/features/converter/convert-commands.ts` | `BROWSE_HOLD` on one helper instance (`:356`); exports unchanged | +14 / -34 | CRLF kept |
| `ui/src/renderer/src/features/settings/settings-commands.ts` | `HELP_FEATURE_ROUTE` (`:14-22`), `HELP_HOLD` (`:25`), `takeHeldHelpToggle` (`:28`), the routed toggle (`:35-43`) | +30 / -1 | CRLF kept |
| `ui/src/renderer/src/components/help/HelpCard.tsx` | `HELP_ROUTE_SCOPE` (`:73-84`), `HELP_TAKE_ON_MOUNT` (`:89-91`), effect on `[feature]` | +25 / -3 | LF kept |
| `ui/src/renderer/src/features/downloader/DownloaderPage.tsx` | `STATUS_SLOT` at `:818` | +1 / -1 | MIXED kept; `:818` bare LF |
| `ui/scripts/electron-vite-dev.mjs` | `PREVIEW_WRAPPER`: `runElectronVite(command, notice, extra)` exported; `main()` calls it with `dev` | +16 / -5 | LF kept |
| `ui/scripts/electron-vite-preview.mjs` | `PREVIEW_WRAPPER`: `PREVIEW_NOTICE`, `previewArgs`, the entry call | new, 20 | LF |
| `ui/package.json` | `:18` `scripts.preview` | +1 / -1 | CRLF kept |
| `ui/tests/unit/dev-script.test.ts` | `PINS_NAMED`: `:64` only | +1 / -1 | LF kept |
| `ui/tests/unit/help-f1-hold.test.tsx` | AC-158.1 to AC-158.7 | new, 191 | LF |
| `ui/tests/e2e/help-f1-mount.test.ts` | AC-158.8 to AC-158.12 | new, 289 | LF |
| `ui/tests/e2e/downloader-advanced-gap.test.ts` | AC-159.2 to AC-159.5 | new, 370 | LF |
| `ui/tests/unit/preview-script.test.ts` | AC-1, AC-2 | new, 62 | LF |
| `.agent/context/meu-status.yaml` | MEU-158 and MEU-159 `ready_for_review` with this plan (`meu_status.py update`, row 8) | +10 / -10 | LF kept |
| `.agent/context/meu-registry.md`, `docs/BUILD_PLAN.md` | `meu_status.py render` | +2 / -2, +1 / -1 | LF |
| `.agent/context/known-issues.yaml` | `HELP-F1-BEFORE-LAZY-MOUNT-LOST`, `DOWNLOADER-ADVANCED-PANEL-GAP` and `UI-PREVIEW-ELECTRON-RUN-AS-NODE-SILENT` resolved (`issue-resolve.py`, row 8) | +15 / -6 | LF kept |
| `.agent/context/known-issues.md` | `issue_triage.py render` | +3 / -6 | LF |
| `docs/build-plan/06-gui.md` | the `Delivered (Session 94)` note before `## Validation Commands` (row 8) | +8 / -0 | CRLF kept |
| `docs/build-plan/11-page-layout.md` | the `Delivered (Session 94)` note before `## Supersession` (row 8) | +8 / -0 | CRLF kept |
| `.agent/docs/commands.md` | `:80`, the preview row (`COMMANDS_DOC`, row 8) | +1 / -1 | CRLF kept |
| `.agent/context/grouping/2026-11-17-value-triage-session-grouping.md` | row 94: `executed (Session 94)` and the plan folder | +1 / -1 | LF kept |
| `.agent/context/current-focus.md` | the Session 94 entry (H1-3) | +3 / -0 | CRLF kept |
| `docs/execution/plans/2026-11-17-ui-small-fixes/` | the plan (D-1181 in its YAML), task (row marks), the plan-local scripts, the row-0 records and `session-gate.ps1` | new folder | LF |
| `.agent/context/handoffs/2026-11-17-ui-small-fixes-MEU-158-handoff.md`, `-MEU-159-handoff.md`, `-handoff.md` | the three handoffs | new | LF |

**`STATUS_SLOT`.** `DownloaderPage.tsx:818` (a bare-LF line in a MIXED file, kept):

```diff
-      <div className="min-h-6 max-w-[var(--layout-page-max-width)]">
+      <div className="min-h-6 max-w-[var(--layout-page-max-width)]" hidden={!addStatus && !error}>
```

The class, the children and both test ids are unchanged.

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

No findings: the round 1 review's Findings table is empty.

### Verdict

`approved` at round 1 of 6, with 0 findings and 0 blocking, intent achieved (`.agent/context/handoffs/2026-11-17-ui-small-fixes-implementation-critical-review.md`, a byte-for-byte copy of the reviewer's report, checked with `cmp`; ledger loop `us-execution-2026-11-17-ui-small-fixes`, round 1 `recorded round 1 verdict=approved agent='codex-independent-reviewer' blocking=0 intent_achieved=yes usage=16,318,015`, `loop may close: approved with no blocking findings.`).

- **The loop.** It began with the plan's goal anchor and citable AC-1, AC-2, AC-3, AC-4, AC-5, AC-158 and AC-159, with no token budget; the OK line reads `mode=execution budget=6 tokens=off` (`us-exec-begin.txt` in the dispatch folder). Dispatch `us-exec-r1` ran with kind `execution` (timeout 2700 s); its console, `us-exec-console-r1.txt` in the dispatch folder, ends with exit 0.
- **The state.** **Intent achieved:** yes. The reviewer's own identity matched the gate's tested_state `9867e51f0024a113de6a585b42b54695f1e4bccb+0fb04e34a3879c5f491b2eb6fc42782c63314539f0e05a2bc03cb8494d11c42e` exactly (review frontmatter and §Scope); no state adjustment was needed.
- **What it accepted.**
  - Accepted STATUS_SLOT. In all four cases it is 24 px high, has empty shown text, and contains both hidden placeholders. Its table gives the boxes per case, including the 1280 window's 1267×739 viewport (§Q3).
  - Accepted the approved limit: the gap closes on a fresh page while the status is empty; once a message appears, its line remains. (§Q3, D-1177)
  - On the cookie modes: The measured fresh profiles show `none`; this is not represented as a live sweep of all cookie modes. (§Q3)
  - The registers (§Q5): the two MEU transitions, the three issue resolutions (15 authorized leaf differences and zero problems) and grouping row 94 only. Accepted D-1142's disclosed queue order and D-1181's added load checks; no decision was reopened.
  - The gate (§Q6) and the scope and fidelity (§Q7): `us-gate-h1.txt` has 31 actual step records, each exit 0; the 362 skip-basis hashes match; all 31 line-ending paths pass, with `DownloaderPage.tsx:818` still bare LF.
- **What it did not rerun.** Not claimed: a fresh reviewer Electron launch, UI build, network capture or full-suite rerun. Reviewer launches were forbidden; it accepted the saved gate and Electron proofs against the matching identity and ran targeted checks only (5 unit files, 21 tests; the selftests, line endings, both renders and the syntax checks; its fake-spawn wrapper probe; its receipt, repeat and fidelity audits).
- **Residual limits it names, carried as limits, not findings.** Residual limits are the approved fresh-empty-status behavior, the measured default-window versus viewport distinction, and reliance on the matching saved Electron proofs because reviewer launches were forbidden.
- **A format note, not a finding.** The verdict JSON's schema has no top-level `tested_state`, so the reviewer carried the value in its summary and identity evidence and in the report's frontmatter. This output-format mismatch is not a product finding.
- **H1-7a** (`review-state-check.txt`, `review-state.json`): `OK: review_mode=execution; round 1 of 6; verdict=approved; open findings=0`.
- **H1-7b** (`exec-review.txt`): `OK: approved at round 1 of 6, 0 open blocking findings`.
- **After the review**, only the three handoffs changed, to fill this report. `identity.py` excludes the handoffs, so the tested_state is unchanged (H1-6b rerun).

---

## Deferred Items

| Item | Kind | Deferred-to | Basis |
|------|------|-------------|-------|
| Retaking the README screenshot | out-of-scope | — | D-1129: only if Mat asks |
| Moving the add status inline with the Add button (the MEU-81 precedent, `11-page-layout.md:95`) | out-of-scope | — | D-1177 option B; a larger layout change |
| Clearing a shown message | out-of-scope | — | D-1177: today nothing clears it, and this session keeps that |
| Commit and push | out-of-scope | — | Only on Mat's direction (H2-5) |
| The Codex execution review | next step | H1-7 | Not part of this run; the coordinator dispatches it |

### Departures and their basis

- **Queue order.** Under D-1142 the queue is 74, 92, 93, 94, then 91, so Session 94 ran fourth, after 74 (`cba97fe`), 92 (`8280586`) and 93 (`9867e51`), and Session 91 `e2e-pointer-flakes` runs after it. The plan's Status line still gives D-1133's order (74, 91, 92, 93, 94) and says Session 94 runs last. Session 91 has not run, so the plan's §Sibling overlap rows for Session 91 (`electron-app.ts`, `electron-env.ts`, the shared E2E helpers and a renderer race fix) are vacuous: row 0 found those files at `HEAD` and the new specs copy their `HEAD` form. Session 91's plan folder and its plan-review handoff were never opened or touched, and are left out of every scope check (`other sessions plan files skipped: 4`, `us-D6-scope-paths.txt`).
- **Plan and task hashes.** The reviewed plan's sha256 is `a91c81f8f652b2436a2c04f2b1a9ebeba50a4fbd801916840994051b3a29a89c` (the coordinator's approval, the plan's Status line); the plan-review handoff cites `ecfd0ac6…`, the plan before the coordinator wrote that Status line. D-1181 (below) then added one decision to the plan's YAML, so its sha256 is now `1bd49ed579781cd13bbc3f312084e3f6d0b9005a85cc71d4e0f344c96df49b57`. `task.md`'s reviewed sha256 is `07a356d2d2cbc0c57ad74f2d1ec6b2c8c9c2ecf705c0ef3cfed13d20feaf8e94`; since then it changed only by its row marks.
- **D-1181 (execution decision, in the plan's YAML; `resolution: autonomous`, two-way).** The plan says the gate's host-load step never fails the gate, but S11 forbids an Electron step above 50 % and the plan's own `host-wait.py` exits 1 when the load is still above the limit after 10 minutes. Chosen (A, the HDP recommendation, decided under the hand-over: USER_EXPLICIT 2026-11-17, continuing USER_EXPLICIT 2026-11-15 and USER_EXPLICIT 2026-11-18 "make the decisions always the recommenations"): `session-gate.ps1` runs `host-wait.py` as its own `host-load` step and again before each of its nine Electron steps (the preview proof and the eight E2E steps), each into its own `us-D6-<step>-load.txt`; a load still above 50 % after the wait fails that step. Every wait passed at once (7.3 % to 9.3 %), so the gate ran as the plan's table says. The options not taken: B, ignoring the exit code, would run Electron above the limit; C, one host-load step only, would leave the later Electron steps unchecked. No M hit. D-1182 to D-1184 and D-1190 to D-1192 are unused.
- **How the rows ran.** Each row's Validation cell was extracted to a `.ps1` file (an environment header setting the working directory, `PYTHONIOENCODING`, `PYTHONDONTWRITEBYTECODE`, `RECEIPTS_DIR`, `TMP` and `TEMP`, then the cell) and run with `pwsh -NoProfile -File`. The one change to a cell's text: `uv run python` became `uv run --no-sync python` (no network; the brief's rule), and row 0's `uv sync` step was dropped for the same reason; the lock hashes in `us-D6-identity-before.txt` are the row-0 ones. The extraction regex was widened once, to read cells that begin with `$` as well as `rtk proxy`. The hand edits were made by scripts that wrote bytes and asserted each anchor occurred once. Before each Electron step a host wait ran with the brief's 50 % limit (the plan's `load-run.py` copy already uses 50 %, not Session 90's 60 %); every one read under 26 %. Each Electron run used a scratch `AVKIT_APP_DATA` and cleared `ELECTRON_RUN_AS_NODE`, except where `preview-proof.py` sets it for its own child.
- **Row 0's dirty list.** `baseline-dirty.txt` records 17 dirty paths at row 0, 5 of them foreign; the foreign ones carry a `#` note naming their owner, and their hashes held to the gate (`baseline-dirty hash mismatch: []`, `us-D6-scope-paths.txt`).
- **Row 3's toggle.** The measurement probe clicked the Advanced disclosure toggle three times across its four cases (to expand at 1280, to collapse before the 700 resize, to expand at 700), not once per case; each case's line records its own collapsed or expanded state, and `domOrder` and `visibleByMode` read `True` in all four (`us-row3-check.txt`).
- **The gate's own reads.** `session-gate.ps1` reads each step's exit from `$LASTEXITCODE` and its own receipt, never a `.exit` side file, and checks each E2E receipt for its passed line, any failed or flaky line and any `unhandled rejection:` line (`rejection-record lines=0` for every step, `us-gate-h1.txt`).
- **Processes.** Each proof and E2E run stopped only the processes it launched, by recorded id and creation time (`left: 0` in every preview proof). No other session's app, the IDE's avkit MCP server, ShareX or Mat's app was stopped. The clipboard specs, `capture-filmstrip-actions.test.ts` and `capture-import.test.ts` never ran.

### Execution notes

- **The decisions.** D-1180: measure before any change, at both widths and both states. D-1177: hide the empty wrapper; the band closes on a fresh page only. D-1129: no README screenshot. D-1181: the gate's load waits (Departures).
- **No stop fired.** Row 3's measurement matched the hypothesis, so S9 did not fire; no existing test failed (S5 not used).

---

## Decision Log

None.

---

## History

| Event | Date | Agent | Detail |
|-------|------|-------|--------|
| Created | 2026-11-18 | claude-code-local (Claude Opus 5.5) | Handoff after the H1-2 gate, H1-3 and H1-4 |
| Reviewed | 2026-11-18 | codex-independent-reviewer | Execution review round 1: `approved`, 0 findings, intent achieved |
| Updated | 2026-11-18 | claude-code-local (Claude Opus 5.5) | Codex Validation Report filled; H1-6, H1-6a and H1-6b rerun |
