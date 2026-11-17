---
date: "2026-11-17"
project: "2026-11-15-ready-handshake"
meu: "MEU-154"
status: "complete"
action_required: "VALIDATE_AND_APPROVE"
template_version: "2.2"
verbosity: "standard"
plan_source: "docs/execution/plans/2026-11-15-ready-handshake/implementation-plan.md"
build_plan_section: "bp06"
agent: "claude-code-local (Claude Opus 5.5)"
reviewer: "codex (H1-7 execution review)"
predecessor: "2026-11-15-ready-handshake-MEU-153-handoff.md"
---

# Handoff: 2026-11-15-ready-handshake-MEU-154-handoff

> **Status**: `complete`
> **Action Required**: `VALIDATE_AND_APPROVE`

---

## Scope

**MEU**: MEU-154 `gui-ready-line-buffer` (issue `GUI-READY-CHUNK-BOUNDARY`, triage D-810). The desktop app reads the backend's ready line whole, from stdout only, and publishes the API once. Before this, `index.ts` handed every stdout and stderr chunk to `publishIfReady` on its own, so a ready line split across two chunks was never matched, a repeated ready line published again, and a ready line on stderr published too.
**Build Plan Section**: [06 §READY line buffering (residual)](../../../docs/build-plan/06-gui.md#ready-line-buffer-residual) (matrix 6.20), with the Delivered (Session 82) note at the end of that section.
**Predecessor**: [2026-11-15-ready-handshake-MEU-153-handoff.md](2026-11-15-ready-handshake-MEU-153-handoff.md), the backend end of the same line.

- **The reader (D-979).** `python-manager.ts:174` adds `READY_LINE_MAX_LENGTH = 4_096` and `:183` `createReadyLineReader(publishLine)`. It keeps the text after the last `\n` as a carry, takes each whole line in order, strips one trailing `\r`, skips empty lines and calls `publishLine` until one returns `true` (`READY_LINES`). The `push` in which that happens returns `true`, and the reader latches: later pushes return `false`, keep no carry and never call `publishLine` (`READY_ONCE`). A carry longer than the bound is dropped and the reader marks itself discarded; the next whole line, the end of the long one, is dropped too and the mark clears (`READY_BOUND`, the `capture-picker.ts:69` shape).
- **Stdout only (D-979).** In `index.ts` `onChildOutput` (`:270`) now only logs; `readyReader` (`:281`) wraps the real `publishIfReady` with the same arguments as before, and `onReadyOutput` (`:295`) pushes each stdout chunk and writes the `INFO backend published for port in AVKIT_READY` note when the push publishes. The hookups are `child.stdout?.on('data', onChildOutput)`, `child.stdout?.on('data', onReadyOutput)` and `child.stderr?.on('data', onChildOutput)` (`:301-303`, `READY_STDOUT_ONLY`).
- **No veto (D-977).** A usable ready line from the owned child's stdout publishes whatever the live query returns, as before; the query still runs once per published line (AC-108.3) and its result does not withhold the publish (`READY_NO_VETO`).
- **The log stays per chunk (D-980).** `onChildOutput` logs each chunk's lines as before, so a log line split across chunks still shows as two Console lines; that is out of scope (`LOG_PER_CHUNK`).
- **Tests (D-982, D-984).** `ready-line-buffer.test.ts` (AC-154.1 to AC-154.7) feeds synthesized chunks to a reader whose `publishLine` is the real `publishIfReady`; `ready-line-pipe.test.ts` (AC-154.8) runs a real child through the real `spawnOwned` and splits the ready line across two writes. The MEU-108 pins pass unchanged (AC-154.9).
- **Records (row 7).** The 06 Delivered (Session 82) note naming D-977; `GUI-READY-CHUNK-BOUNDARY` resolved through `issue-resolve.py`; MEU-154 `ready_for_review` (`rh-status-154.txt`).

**Note for Mat (optional, not a gate).** If you start the dev app, its Console should show one `INFO backend published for port in AVKIT_READY` line after the backend starts. The automated checks above already prove it (AC-154.3, AC-154.8 and the E2E pin); nothing waits on this look.

**Plan:** [implementation-plan.md](../../../docs/execution/plans/2026-11-15-ready-handshake/implementation-plan.md) §MEU-154. **Execution authorization:** `USER_EXPLICIT`, 2026-11-15, as in the MEU-153 handoff (`implementation-plan.md:15`). Receipts are named as in the MEU-153 handoff: a file name alone is in the session's receipts folder (the `ready-handshake` folder under `RECEIPTS_DIR`).

---

## Acceptance Criteria

| AC | Type | Description | Source | Test(s) | Status |
|----|------|-------------|--------|---------|--------|
| AC-154.1 | unit | A ready line split in two at four points, after an `INFO boot\n` line: the first `push` returns `false` with no live query, the second `true`; one publish of `http://127.0.0.1:13988/api/v1`, one query with pid 111 | Local Canon (06 §READY line buffering: Lines, Tests) | `ui/tests/unit/ready-line-buffer.test.ts:47` | ✅ |
| AC-154.2 | unit | Two lines in one chunk, and a ready line whose `\n` comes in the next chunk: each publishes once with the right port, and `publishLine` sees the lines in order | Local Canon (06: Tests) | `ui/tests/unit/ready-line-buffer.test.ts:68` | ✅ |
| AC-154.3 | unit | A repeated ready line (same chunk, later chunk, other port): one publish with the first port, one query, `state.published` true; later pushes return `false`, keep `pendingLength` 0 and never call `publishLine` | Local Canon (06: Once) | `ui/tests/unit/ready-line-buffer.test.ts:84` | ✅ |
| AC-154.4 | unit | No veto: a failed live query with no descriptor pid, and a foreign image, still publish a usable ready line once | Local Canon (06: Veto; D-977; 07:219) | `ui/tests/unit/ready-line-buffer.test.ts:98` | ✅ |
| AC-154.5 | unit | A 5 000-character line never reaches `publishLine`; `state.discarded` is true after the first push and false after the second; the later ready line publishes; a `\r\n` ready line publishes with the `\r` stripped | Local Canon (`capture-picker.ts:69`; D-979) | `ui/tests/unit/ready-line-buffer.test.ts:111` | ✅ |
| AC-154.6 | unit | `port=0` and an unterminated ready line at the end do not publish or query; a later usable line does | Local Canon (AC-108.1, AC-108.2) | `ui/tests/unit/ready-line-buffer.test.ts:130` | ✅ |
| AC-154.7 | unit | `index.ts` source (UTF-8, `\r` removed): one stdout `onReadyOutput` hookup and no stderr one; no `publishIfReady(` in `onChildOutput`; exactly one `publishIfReady(` and one `createReadyLineReader(` from `readyReader` to the stdout hookup | Local Canon (D-979 `READY_STDOUT_ONLY`; the AC-108.4 slice pattern) | `ui/tests/unit/ready-line-buffer.test.ts:149` | ✅ |
| AC-154.8 | unit | A real pipe through `spawnOwned`: the child writes the ready line in two parts 80 ms apart, then a second ready line; at least two `data` events, a first chunk not ending in `\n`, exit code 0 and one publish, for port 13988 (the test waits for `close`, D-987) | Local Canon (06: Lines, Once; `spawnOwned`'s piped stdio) | `ui/tests/unit/ready-line-pipe.test.ts:13` | ✅ |
| AC-154.9 | E2E | The pins pass unchanged: `ready-probe-guard.test.ts` (AC-108.1 to AC-108.6) and `backend-output-after-close.test.ts` (AC-108.7) after `npm run build` | Local Canon (MEU-108 `READY_GUARD`, `LOG_AFTER_WINDOW`) | gate `meu-154-tests`, `ui-build`, `e2e-late-line` | ✅ |
| AC-108 (cross-ref) | guard | AC-108.1 `:32`, AC-108.2 `:43`, AC-108.3 `:50`, AC-108.4 `:72`, AC-108.5 `:102` and `:113`, AC-108.6 `:126`, `:133` and `:137` in `ui/tests/unit/ready-probe-guard.test.ts`; AC-108.7 at `ui/tests/e2e/backend-output-after-close.test.ts:8` | MEU-108 | as AC-154.9 | ✅ |
| AC-19 (cross-ref) | guard | The backend's CLI and spawn tests (AC-19.1 to AC-19.4) that print the line this reader reads; evidenced in the MEU-153 handoff | MEU-19 | gate `meu-153-tests` | ✅ |
| AC-153 (sibling) | sibling MEU | AC-153.1 to AC-153.5: the backend listens before the ready line; evidenced in the MEU-153 handoff | MEU-153 | `2026-11-15-ready-handshake-MEU-153-handoff.md` | ✅ |

<!-- CACHE BOUNDARY -->

---

## Evidence

### FAIL_TO_PASS

| Test | Red Output (hash/snippet) | Green Output | File:Line |
|------|---------------------------|--------------|-----------|
| AC-154.1 to AC-154.7 | `AssertionError: expected 'undefined' to be 'function' // Object.is equality` at `expectNewNames tests/unit/ready-line-buffer.test.ts:15:43` (`rh-154-red.txt`; each test first checks that `createReadyLineReader` and `READY_LINE_MAX_LENGTH` exist, and neither did) | Row 6: pass (`rh-154-green.txt`) | `ui/tests/unit/ready-line-buffer.test.ts:47` to `:149` |
| AC-154.8 | the same assertion (`rh-154-red.txt`) | Row 6: pass (`rh-154-green.txt`) | `ui/tests/unit/ready-line-pipe.test.ts:13` |

- **Row 5 Red.** `rh-154-red.txt`: `Test Files  2 failed (2)`, `Tests  8 failed (8)`, exit 1. `rh-154-red-check.txt`: `red-check: 1 receipt(s), 8 required test(s), 0 problem(s)`. AC-154.9 is a pin and was not required at Red.
- **Row 6 Green.** `rh-154-green.txt`: `Test Files  3 passed (3)`, `Tests  17 passed (17)` (the two new files and `ready-probe-guard.test.ts`); the UI typecheck and lint exit 0 (`rh-154-types.txt`, `rh-154-lint.txt`); the build `built in 4.07s` (`rh-154-build.txt`); `backend-output-after-close.test.ts` `1 passed (754ms)` (`rh-154-e2e.txt`); `rh-154-eol.txt`: `line-ending drift: []`.

### Commands Executed

```json
{"schema_version": "evidence.v1", "cwd": "P:/av-kit", "check_id": "rh-5-red-154", "command": "pwsh -NoProfile -File C:/Temp/av-kit/ready-handshake/run-row5.ps1 (task.md row 5's Validation cell, from ui/: rtk proxy npm run test -- tests/unit/ready-line-buffer.test.ts tests/unit/ready-line-pipe.test.ts *> C:/Temp/av-kit/ready-handshake/rh-154-red.txt, its exit code, red-check.py --require AC-154.1 to AC-154.8); receipts rh-154-red.txt, rh-154-red-check.txt", "scope": "MEU-154 Red: AC-154.1 to AC-154.8 against the unchanged python-manager.ts and index.ts", "phase": "red", "exit_code": 0, "result": "pass", "tested_state": "HEAD 5e5b4ba (baseline.sha) plus rows 0 to 5", "output": "rh-154-red.txt: Test Files  2 failed (2); Tests  8 failed (8); AssertionError: expected 'undefined' to be 'function' // Object.is equality; exit 1. rh-154-red-check.txt: red-check: 1 receipt(s), 8 required test(s), 0 problem(s)"}
```

```json
{"schema_version": "evidence.v1", "cwd": "P:/av-kit", "check_id": "rh-6-green-154", "command": "pwsh -NoProfile -File C:/Temp/av-kit/ready-handshake/run-row6.ps1 (task.md row 6's Validation cell, from ui/ with ELECTRON_RUN_AS_NODE unset: rtk proxy npm run test -- tests/unit/ready-line-buffer.test.ts tests/unit/ready-line-pipe.test.ts tests/unit/ready-probe-guard.test.ts *> C:/Temp/av-kit/ready-handshake/rh-154-green.txt; npm run typecheck; npm run lint; npm run build; npm run test:e2e -- tests/e2e/backend-output-after-close.test.ts; the line-ending check); receipts rh-154-green.txt, rh-154-types.txt, rh-154-lint.txt, rh-154-build.txt, rh-154-e2e.txt, rh-154-eol.txt", "scope": "MEU-154 Green: READY_LINES, READY_ONCE, READY_BOUND, READY_STDOUT_ONLY, READY_NO_VETO; the AC-154.9 pins", "phase": "green", "exit_code": 0, "result": "pass", "tested_state": "HEAD 5e5b4ba (baseline.sha) plus rows 0 to 6", "output": "rh-154-green.txt: Test Files  3 passed (3); Tests  17 passed (17). rh-154-types.txt: tsc --noEmit exit 0. rh-154-lint.txt: eslint src/ tests/ --max-warnings 0 exit 0. rh-154-build.txt: built in 4.07s. rh-154-e2e.txt: 1 passed (754ms). rh-154-eol.txt: line-ending drift: []"}
```

```json
{"schema_version": "evidence.v1", "cwd": "P:/av-kit", "check_id": "rh-7-records", "command": "pwsh -NoProfile -File C:/Temp/av-kit/ready-handshake/run-row7.ps1 (task.md row 7's Validation cell: issue-resolve.py --issue BACKEND-READY-BEFORE-LISTEN --issue GUI-READY-CHUNK-BOUNDARY --set-file C:/Temp/av-kit/ready-handshake/issue-resolve-set.json --expect-sha256 from baseline-scope.json; issue_triage.py render and render --check; meu_status.py update MEU-153 and MEU-154 ready_for_review and render; the row-7 check); receipts rh-issue-resolve.txt, rh-issues-render-check.txt, rh-status-153.txt, rh-status-154.txt, rh-row7-check.txt", "scope": "Row 7: the 04 and 06 Delivered (Session 82) notes; both issues resolved; both MEUs ready_for_review; grouping row 82 executed", "phase": "static", "exit_code": 0, "result": "pass", "tested_state": "HEAD 5e5b4ba (baseline.sha) plus rows 0 to 7", "output": "rh-issue-resolve.txt: issue-resolve: 0 problem(s). rh-issues-render-check.txt: OK: known-issues.md is up-to-date. rh-status-153.txt: Updated MEU-153 -> ready_for_review (updated: 2026-11-17). rh-status-154.txt: Updated MEU-154 -> ready_for_review (updated: 2026-11-17). rh-row7-check.txt: row 82 executed (Session 82), grouping LF: True 04/06 CRLF: [True, True] notes: [1, 1]"}
```

```json
{"schema_version": "evidence.v1", "cwd": "P:/av-kit", "check_id": "rh-gate-h1-2", "command": "pwsh -NoProfile -File C:/Temp/av-kit/ready-handshake/run-h1-2.ps1 (task.md H1-2's Validation cell: $env:ELECTRON_RUN_AS_NODE=$null; rtk proxy pwsh -NoProfile -File docs/execution/plans/2026-11-15-ready-handshake/session-gate.ps1 *> C:/Temp/av-kit/ready-handshake/rh-gate-h1.txt); one run; receipts rh-gate-h1.txt and the rh-D6-*.txt step receipts", "scope": "H1-2 session gate for MEU-153 and MEU-154: identity before and after; ruff check and format, pyright, the UI typecheck and lint, the task contract, scope paths, line endings, the red-check and gap-tally selftests; the MEU-153 and MEU-154 targeted tests and the packaged receipt; the full Python suite, the full UI suite and build, the AC-108.7 Electron E2E, the OpenAPI check, the state and issue renders", "phase": "full", "fresh": true, "snapshot": false, "exit_code": 0, "result": "pass", "tested_state": "5e5b4ba18b293d9215f79be878b0fa7b815f83b5+8a1f1b0c2d5d366ce04112662dee50a7002181195c6366ff019c3ff80eb58594", "output": "rh-gate-h1.txt: session-gate: all steps exit 0; tested_state before = after (rh-D6-identity-before.txt, rh-D6-identity-after.txt). py-lint All checks passed!; py-format 4 files already formatted; py-types 0 errors, 0 warnings, 0 informations; ui-types tsc --noEmit exit 0; ui-lint eslint src/ tests/ --max-warnings 0 exit 0; task-contract OK: 25 row(s), 23 fully checked, 2 view_file exempt (H1-5, H2-1); scope-paths changed paths: 34 outside scope: [] other sessions plan files skipped: 2, baseline-dirty hash mismatch: [] of 3, head moved (S4): False; line-endings files: 23 mismatch: []; red-check-selftest 43 fixture(s) (14 positive, 29 negative), 0 wrong: []; gap-tally-selftest ok; meu-153-tests 11 passed in 26.26s; meu-154-tests Tests  17 passed (17); packaged-receipt match; py-tests (rh-D6-py-tests.txt) 3035 passed, 37 warnings in 222.49s (0:03:42); ui-tests Test Files  137 passed (137), Tests  1578 passed (1578); ui-build built in 3.94s; e2e-late-line 1 passed (746ms); openapi exit 0; state-render Drift check passed (153 MEUs, 12 phases); issues-render-check OK: known-issues.md is up-to-date"}
```

```json
{"schema_version": "evidence.v1", "cwd": "P:/av-kit", "check_id": "rh-h1-3-h1-4", "command": "pwsh -NoProfile -File C:/Temp/av-kit/ready-handshake/run-h1-3.ps1 and C:/Temp/av-kit/ready-handshake/run-h1-4.ps1 (task.md H1-3 and H1-4's Validation cells: meu_status.py render --check, meu_status.py get MEU-153 and MEU-154, the ready_for_review check; tools/export_openapi.py --check openapi.committed.json); receipts rh-render-check.txt, rh-h13-status-153.txt, rh-h13-status-154.txt, rh-h13-check.txt, openapi-check.txt", "scope": "H1-3 and H1-4 after the gate: the render, both MEUs ready_for_review, the OpenAPI drift check", "phase": "static", "exit_code": 0, "result": "pass", "tested_state": "the H1-2 state plus H1-3's current-focus paragraph (outside identity.py's inputs)", "output": "rh-render-check.txt: Drift check passed (153 MEUs, 12 phases). rh-h13-check.txt: MEU-153 and MEU-154 ready_for_review: True. openapi-check.txt: no drift reported, exit 0"}
```

### Quality Gate Results

The gate covers both MEUs; its results are in the MEU-153 handoff. Its last line (`rh-gate-h1.txt`) is `session-gate: all steps exit 0`, at tested_state `5e5b4ba18b293d9215f79be878b0fa7b815f83b5+8a1f1b0c2d5d366ce04112662dee50a7002181195c6366ff019c3ff80eb58594`, the same before and after the gate.

---

## Changed Files

Counts are added / removed lines against the row-0 copies (`baseline-copies/` in the receipts folder; `git diff --no-index --numstat --ignore-cr-at-eol`); a new file's count is its line count. Line endings were measured as bytes (the gate's `line-endings` step).

| File | Change | Added / removed | Line endings |
|------|--------|-----------------|--------------|
| `ui/src/main/python-manager.ts` | `READY_LINE_MAX_LENGTH`, `createReadyLineReader` | +52 / -0 | LF kept |
| `ui/src/main/index.ts` | `onChildOutput` logs only; `readyReader`, `onReadyOutput`, the stdout hookup | +11 / -4 | CRLF kept |
| `ui/tests/unit/ready-line-buffer.test.ts` | new: AC-154.1 to AC-154.7 | 165 lines | LF |
| `ui/tests/unit/ready-line-pipe.test.ts` | new: AC-154.8 | 47 lines | LF |
| `docs/build-plan/06-gui.md` | the Delivered (Session 82) note | +6 / -0 | CRLF kept |
| `.agent/context/known-issues.yaml` | both issues resolved (`issue-resolve.py`) | +10 / -4 | LF kept |
| `.agent/context/known-issues.md` | `issue_triage.py render` | +3 / -5 | LF |
| `.agent/context/meu-status.yaml` | MEU-153 and MEU-154 `ready_for_review` (`meu_status.py`) | +10 / -10 | LF kept |
| `.agent/context/meu-registry.md` | `meu_status.py render` | +2 / -2 | LF |
| `docs/BUILD_PLAN.md` | `meu_status.py render` | +1 / -1 | LF |
| `.agent/context/grouping/2026-11-15-post-rc3-triage-residuals-session-grouping.md` | §6 row 82: `executed (Session 82)` | +1 / -1 | LF kept |
| `.agent/context/current-focus.md` | the Session 82 paragraph (H1-3) | +3 / -0 | CRLF kept |

```diff
   child.stdout?.on('data', onChildOutput)
+  child.stdout?.on('data', onReadyOutput)
   child.stderr?.on('data', onChildOutput)
```

The backend files are listed in the MEU-153 handoff. Nothing is committed or staged.

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

Pending: the H1-7 execution review (ledger loop `rh-execution-2026-11-15-ready-handshake`) has not run.

---

## Deferred Items

| Item | Kind | Deferred-to | Basis |
|------|------|-------------|-------|
| Console log lines split across chunks | out-of-scope | — | D-980: the log stays per chunk; only the ready line is read whole |
| The dev-app Console look | optional | Mat, if he wants | Not a gate; the automated checks prove it |
| Commit and push | out-of-scope | — | Only on Mat's explicit words (H2-5) |

### Departures and their basis

- **AC-154.8 waits for `close` (D-987).** The AC says the pipe test waits for the child's `exit` event. Node can emit `exit` before the last stdout `data` event, so the test waits for `close`, which follows both. It keeps every assertion the AC names: exit code 0, at least two `data` events, a first chunk that does not end in `\n`, and exactly one publish, for port 13988.
- **`index.ts` keeps CRLF.** The edit was made as bytes; the gate's `line-endings` step reads it as CRLF (`line-endings files: 23 mismatch: []`).
- **Shared departures.** The plan's change after its review, D-985, D-986, the row-0 helpers, Session 83's files, the issue-resolve dry run, the session gate and the scratch build are in the MEU-153 handoff.
- **Execution decisions** D-985 to D-987 are in the plan's decision YAML, each autonomous with `mandatory: none`, so the Decision Log below is `None.`.

---

## Decision Log

None.

---

## History

| Event | Date | Agent | Detail |
|-------|------|-------|--------|
| Created | 2026-11-17 | claude-code-local (Claude Opus 5.5) | Initial MEU-154 handoff after the H1-2 gate, H1-3 and H1-4 |
