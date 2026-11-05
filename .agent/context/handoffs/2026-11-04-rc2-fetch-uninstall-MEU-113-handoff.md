---
date: "2026-11-05"
project: "rc2-fetch-uninstall"
meu: "MEU-113"
status: "complete"
action_required: "VALIDATE_AND_APPROVE"
template_version: "2.2"
verbosity: "standard"
plan_source: "docs/execution/plans/2026-11-04-rc2-fetch-uninstall/implementation-plan.md"
build_plan_section: "bp07"
agent: "claude-code-local (Claude Opus 5.5)"
reviewer: "codex (H1-7 execution review)"
predecessor: "none"
---

# Handoff: 2026-11-04-rc2-fetch-uninstall-MEU-113-handoff

> **Status**: `complete`
> **Action Required**: `VALIDATE_AND_APPROVE`

---

## Scope

**MEU**: MEU-113, the fetch script's documented exit codes (`FETCH-FFMPEG-EXIT-CODES`). `tools/fetch_ffmpeg_windows.ps1` returns 2 for a blank URL, a malformed SHA or a missing archive, 3 for a SHA mismatch, 4 for a missing `ffmpeg.exe` or `ffprobe.exe` and 5 for a stub, and the tests assert the exact codes.
**Build Plan Section**: [07 §Fetch script exit codes (residual)](../../../docs/build-plan/07-distribution.md).
**Predecessor**: none. The [MEU-114 handoff](2026-11-04-rc2-fetch-uninstall-MEU-114-handoff.md) is the same plan's other MEU.

- **The defect.** Each refusal called `Write-Error`, which throws under `$ErrorActionPreference = 'Stop'` and exits 1, so the `exit 2` to `exit 5` lines after it never ran. Only exit 6 used `[Console]::Error.WriteLine`, and only exit 6 returned its documented code.
- **The fix (row 2).** All six `Write-Error` lines became `[Console]::Error.WriteLine(...)` with the same message. The `exit` lines didn't change. The comment that named the cmdlet beside exit 6 was reworded and moved under `$ErrorActionPreference`, where it explains every path.
- **The tests (row 1).** AC-113.1 to AC-113.5 run the script on local fixture archives through the existing `_run_fetch` with `-ExtractOnly`, and assert the exact code and the message on stderr. The two earlier tests, which only checked for a nonzero exit, now assert 2 and 3.
- **The hub (row 7).** 07 gains a Delivered note, MEU-113 is `ready_for_review` with this `execution_plan` (`approved` after the H1-7 review), and `FETCH-FFMPEG-EXIT-CODES` is resolved ("fixed in the tree, ships in rc.2").

No caller depends on exit 1. Callers read the pin or check for nonzero (plan §MEU-113). Nothing ships from this change until a new build: the installer that will carry it is MEU-125's.

**Plan:** [implementation-plan.md](../../../docs/execution/plans/2026-11-04-rc2-fetch-uninstall/implementation-plan.md) §MEU-113. **Execution authorization:** `USER_EXPLICIT`, 2026-11-05, "all recommendations are accpeted, proceed" (D-273 to D-278). The plan review approved with no findings (D-273), and D-278 starts execution on that approval.

---

## Acceptance Criteria

| AC | Type | Description | Source | Test(s) | Status |
|----|------|-------------|--------|---------|--------|
| AC-113.1 | unit | The fetch script exits 2, with its message on stderr, for a blank URL, a malformed SHA and a missing archive. | Local Canon (`FETCH-FFMPEG-EXIT-CODES`; 07 §Fetch script exit codes) | `tests/unit/test_packaging_installer.py:322` (three cases); `:136` now asserts 2 | ✅ |
| AC-113.2 | unit | It exits 3 on a SHA mismatch. | Local Canon (same) | `tests/unit/test_packaging_installer.py:336`; `:156` now asserts 3 | ✅ |
| AC-113.3 | unit | It exits 4 when the archive holds no `ffmpeg.exe` or `ffprobe.exe`. | Local Canon (same) | `tests/unit/test_packaging_installer.py:344` (a zip with only `ffprobe.exe` and `LICENSE.txt`) | ✅ |
| AC-113.4 | unit | It exits 5 for a stub of 1024 B or less. The fixture zip holds both binaries and `LICENSE.txt`, because exit 6 is checked first. | Local Canon (same) | `tests/unit/test_packaging_installer.py:352` | ✅ |
| AC-113.5 | unit | The script has no `Write-Error` left, comments included. | Local Canon (same) | `tests/unit/test_packaging_installer.py:366` | ✅ |
| AC-114 (cross-ref) | — | Owned by the MEU-114 handoff (the uninstall removes the installer copy) | plan §MEU-114 | [MEU-114 handoff](2026-11-04-rc2-fetch-uninstall-MEU-114-handoff.md) | see MEU-114 |
| AC-61 (cross-ref) | regression | AC-61.18: the two `DeleteRegValue` lines in `installer.nsh`. Owned by the MEU-114 handoff, whose AC-114.3 guards it | plan §MEU-114 | `ui/tests/unit/login-item-nsh.test.ts:27` (gate `ui-tests`) | see MEU-114 |
| AC-24 (cross-ref) | regression | AC-24.10: the packaged backend folder holds its exe and support tree. Under the baseline rule it would be excused only if row 0 had seen it fail; row 0 saw it pass, so nothing is excused | plan §Session gate | `tests/unit/test_packaging_backend.py` (gate `py-tests`) | ✅ |
| AC-25 (cross-ref) | regression | AC-25.10: the NSIS check script exists and fails closed. Same baseline rule as AC-24.10, and it passed at row 0 and in the gate. The same file holds this MEU's tests | plan §Session gate | `tests/unit/test_packaging_installer.py:94` (gate `py-tests`) | ✅ |
| AC-110 (cross-ref) | — | AC-110.9 keeps one version on every surface. The bump to `0.1.0-rc.2` is MEU-125's, so this session leaves every version at `0.1.0-rc.1` | plan §Out of Scope | `tests/unit/test_release_packaging.py` (gate `py-tests`) | deferred to MEU-125 |

<!-- CACHE BOUNDARY -->

---

## Evidence

### FAIL_TO_PASS

| Test | Red Output (hash/snippet) | Green Output | File:Line |
|------|---------------------------|--------------|-----------|
| AC-113.1 to AC-113.4 and the two earlier tests | `assert 1 == 2`, `assert 1 == 3`, `assert 1 == 4`, `assert 1 == 5`, each with `Write-Error: …fetch_ffmpeg_windows.ps1:<line>` on stderr | pass | `test_packaging_installer.py:136`, `:156`, `:322-360` |
| AC-113.5 | `assert 'Write-Error' not in …` | pass | `test_packaging_installer.py:366` |

Row 1's Red is 9 failed and 11 deselected: the three AC-113.1 cases, AC-113.2 to AC-113.5 and the two tightened tests. Every failure is the decisive assertion, and stderr shows the throw that ended the script before its `exit` line. `red-check.py` required the five AC tests and found 0 problems. Row 2's Green runs the whole file: 20 passed.

Receipts: `C:/Temp/av-kit/s49-exit-red.txt` (with `.exit`), `s49-exit-red-check.txt`, `s49-exit-green.txt`, `s49-r7-render.txt`, `s49-r7-issues.txt`, `rc2/issue-decisions.yaml`, the gate's `s49-gate-h1.txt` and `s49-D6-<id>.txt`, and `drift-check.txt` and `openapi-check.txt`.

### Commands Executed

```json
{"schema_version": "evidence.v1", "check_id": "s49-113-red", "command": "rtk proxy uv run pytest tests/unit/test_packaging_installer.py -k \"ac_113 or fetch_ffmpeg_rejects\" --tb=short -q *> C:/Temp/av-kit/s49-exit-red.txt; then red-check.py --require test_ac_113_1 .. test_ac_113_5 (task.md row 1 Validation cell, verbatim, from P:/av-kit)", "cwd": "P:/av-kit", "scope": "MEU-113 Red: AC-113.1 to AC-113.5 and the two earlier fetch tests, against the unfixed script, with red-check.py", "phase": "red", "exit_code": 0, "result": "pass", "tested_state": "HEAD 83229ea (baseline.sha) plus row 1", "output": "9 failed, 11 deselected. assert 1 == 2 / 1 == 3 / 1 == 4 / 1 == 5, each with Write-Error: ...fetch_ffmpeg_windows.ps1:<line> on stderr; assert 'Write-Error' not in the script. red-check: 1 receipt(s), 5 required test(s), 0 problem(s). The row exits 0 because red-check confirms decisive failures."}
```

```json
{"schema_version": "evidence.v1", "check_id": "s49-113-green", "command": "rtk proxy uv run pytest tests/unit/test_packaging_installer.py --tb=short -q *> C:/Temp/av-kit/s49-exit-green.txt (task.md row 2 Validation cell, verbatim, from P:/av-kit)", "cwd": "P:/av-kit", "scope": "MEU-113 Green: the whole installer test file after the six Write-Error lines became stderr writes", "phase": "green", "exit_code": 0, "result": "pass", "tested_state": "HEAD 83229ea plus rows 1 and 2", "output": "20 passed in 3.37s."}
```

```json
{"schema_version": "evidence.v1", "check_id": "s49-row7-hub", "command": "pwsh -NoProfile -File row7.ps1 (task.md row 7 Validation cell, verbatim, from P:/av-kit): meu_status.py render --check, issue_triage.py render --check, the issue statuses and issue-decisions.py", "cwd": "P:/av-kit", "scope": "Row 7 hub, shared by MEU-113 and MEU-114: the 07 Delivered notes, both MEUs ready_for_review, the two issues resolved and FFMPEG-LIBDVDCSS-BUNDLED left open, and the decision logs read back in the validator's grammar", "phase": "static", "exit_code": 0, "result": "pass", "tested_state": "HEAD 83229ea plus rows 1 to 7", "output": "Drift check passed (126 MEUs, 12 phases). Issue renders match. Statuses FETCH-FFMPEG-EXIT-CODES resolved, UNINSTALL-LEAVES-INSTALLER-COPY resolved, FFMPEG-LIBDVDCSS-BUNDLED open. UNINSTALL-LEAVES-INSTALLER-COPY: D-228 (triage). FFMPEG-LIBDVDCSS-BUNDLED: D-214 (triage), D-215 (triage), D-266 (triage), D-275 (triage). issue-decisions: 0 problem(s)."}
```

```json
{"schema_version": "evidence.v1", "check_id": "s49-gate-h1-2", "command": "$env:ELECTRON_RUN_AS_NODE=$null; rtk proxy pwsh -NoProfile -File docs/execution/plans/2026-11-04-rc2-fetch-uninstall/session-gate.ps1 *> C:/Temp/av-kit/s49-gate-h1.txt; $code=$LASTEXITCODE; Select-String -Path C:/Temp/av-kit/s49-gate-h1.txt -Pattern ' exit=','not_run','tested_state','_sha256 ','outside scope','mismatch','session-gate:'; exit $code", "cwd": "P:/av-kit", "scope": "H1-2, the registered D6 gate on the whole tree after rows 0 to 7: identity, every static check, both full suites, the UI build and the state render, then the identity again", "phase": "full", "exit_code": 0, "result": "pass", "fresh": true, "snapshot": false, "tested_state": "83229ea69b563a03d5c47d4678619c8da4c937d8+f7dcdeb0897c701333a4d083e689326190f9a902f14ef832e2f4ba1ed6f660ec", "output": "py-types 0 errors; py-lint all checks passed; ui-types and ui-lint exit 0; task-contract OK: 24 row(s), 22 fully checked, 2 exempt (view_file); scope-paths changed paths: 29 outside scope: [] head moved (S4): False; red-check selftest: 36 fixture(s), 0 wrong; py-tests 1193 passed in 110.41s; ui-tests 108 files, 1141 passed; ui-build exit 0; state-render drift check passed (126 MEUs); tested_state before and after identical. Baseline failures excused: none. session-gate: all steps exit 0"}
```

```json
{"schema_version": "evidence.v1", "check_id": "s49-h1-3-render", "command": "rtk proxy uv run python tools/meu_status.py render --check *> C:/Temp/av-kit/drift-check.txt", "cwd": "P:/av-kit", "scope": "H1-3: rendered state regions against meu-status.yaml, after the current focus was updated. No status was written here", "phase": "static", "exit_code": 0, "result": "pass", "tested_state": "83229ea69b563a03d5c47d4678619c8da4c937d8+f7dcdeb0897c701333a4d083e689326190f9a902f14ef832e2f4ba1ed6f660ec", "output": "Drift check passed - SSOT loaded (126 MEUs, 12 phases), rendered regions match on-disk content"}
```

```json
{"schema_version": "evidence.v1", "check_id": "s49-h1-4-openapi", "command": "rtk proxy uv run python -c '<task.md row H1-4: packages/api diff against baseline.sha plus untracked files>' *> C:/Temp/av-kit/openapi-check.txt", "cwd": "P:/av-kit", "scope": "H1-4: the basis for skipping the OpenAPI check", "phase": "static", "exit_code": 0, "result": "pass", "tested_state": "83229ea69b563a03d5c47d4678619c8da4c937d8+f7dcdeb0897c701333a4d083e689326190f9a902f14ef832e2f4ba1ed6f660ec", "output": "packages/api changes: []"}
```

### Quality Gate Results

`s49-gate-h1-2` is the fresh full record, and its last line is:

> session-gate: all steps exit 0

- **Static:** `py-types` (0 errors), `py-lint`, `ui-types`, `ui-lint`, `task-contract` (24 rows, 22 fully checked, H1-5 and H2-1 exempt as `view_file`), `scope-paths` (29 changed paths, none outside scope, HEAD still `83229ea`), `red-check-selftest` (36 fixtures, 0 wrong): all exit 0.
- **Suites:** `py-tests` 1193 passed in 110.41s; `ui-tests` 108 files, 1141 passed. Baseline failures excused: none, because row 0 saw neither AC-24.10 nor AC-25.10 fail.
- **Build and state:** `ui-build` and `state-render` exit 0.
- **Skipped, each printed with its reason:** `openapi` (no `packages/api` change, H1-4), `mcp-types`, `mcp-build`, `mcp-tests` (no MCP change), `mcp-audit` (no MCP change; it runs before MEU-125's version bump), `ui-electron` (no main, preload or renderer change; row 6 launched the real packaged app) and `build-record` (no full build this session).
- **Identity:** `tested_state` `83229ea69b563a03d5c47d4678619c8da4c937d8+f7dcdeb0897c701333a4d083e689326190f9a902f14ef832e2f4ba1ed6f660ec`, the same before and after. The gate set `TMP` and `TEMP` to `C:/Temp/av-kit/rc2/tmp` (RC1 ECN-2) and cleared `ELECTRON_RUN_AS_NODE`, which `identity.py` hashes. A recompute with it unset after H1-3 to H1-5 gives the same state.

---

## Changed Files

| File | Action | Summary |
|------|--------|---------|
| `tools/fetch_ffmpeg_windows.ps1` | modified | Six `Write-Error` lines become stderr writes; the comment moves under `$ErrorActionPreference`. CRLF kept |
| `tests/unit/test_packaging_installer.py` | modified | AC-113.1 to AC-113.5, and the two earlier tests assert 2 and 3. CRLF kept |
| `docs/build-plan/07-distribution.md` | modified | Delivered notes for MEU-113 and MEU-114. CRLF kept |
| `docs/BUILD_PLAN.md`, `.agent/context/meu-status.yaml`, `meu-registry.md` | modified | MEU-113 and MEU-114 `ready_for_review`, then `approved` after the H1-7 review, shared with MEU-114. `meu_status.py update` also rewrote three phase notes (phases 3, 7 and 8) and the `description` and `note` of MEU-115 to MEU-126 in its own wrapping and quoting; a parsed comparison against HEAD shows only MEU-113's and MEU-114's fields differ |
| `.agent/context/known-issues.yaml`, `known-issues.md`, `triage-output.yaml` | modified | Both issues resolved through the model API, shared with MEU-114 |
| `.agent/context/current-focus.md` | modified | Session 49 entry on top; the other session's uncommitted line is kept |
| Plan folder: `baseline.ps1`, `baseline.sha`, `baseline-dirty.txt`, `identity.py`, `red-check.py`, `issue-decisions.py`, `session-gate.ps1`, `task.md` | new or modified | The plan's scripts and records, shared with MEU-114 |

```diff
 $ErrorActionPreference = 'Stop'
+# Each refusal writes to stderr directly: the error cmdlet throws under Stop and exits 1,
+# so the documented exit code below it would never run.
 if ([string]::IsNullOrWhiteSpace($Url)) {
-    Write-Error 'FETCH_FFMPEG requires a pinned URL (AVKIT_FFMPEG_URL or -Url).'
+    [Console]::Error.WriteLine('FETCH_FFMPEG requires a pinned URL (AVKIT_FFMPEG_URL or -Url).')
     exit 2
 }
```

The other five lines follow the same pattern: the malformed SHA and the missing archive (exit 2), the mismatch (3), the missing binary (4) and the stub (5).

---

## Codex Validation Report

### Recheck Protocol

1. Read Scope + AC table
2. Verify each AC against Evidence section (file:line, not memory)
3. Independently probe the claimed behavior and compare decisive output
4. Verify the full gate is fresh and matches current D6 inputs; rerun if changed or unproven
5. Record findings below

### Findings

| # | Severity | Finding | File:Line | Recommendation | Status |
|---|----------|---------|-----------|----------------|--------|
| — | — | None. The reviewer's one clerical note, the pre-existing copy's chronology in the MEU-114 handoff's round-trip note, is corrected against `roundtrip-prepackaged.txt`. | — | — | closed |

### Verdict

Approved: Codex execution review, loop `s49-execution-2026-11-04-rc2-fetch-uninstall`, round 1 of 6, no findings, intent achieved (7,708,396 tokens). The report is `2026-11-04-rc2-fetch-uninstall-implementation-critical-review.md`.

---

## Deferred Items

| Item | Kind | Deferred-to | Basis |
|------|------|-------------|-------|
| Version bump to `0.1.0-rc.2` | deferred | MEU-125 | 07 §Second release candidate; AC-110.9 keeps one version across surfaces until then |
| A build that ships this fix | deferred | MEU-125 | The fix is in the tree only; rc.2's build carries it |
| The libdvdcss notices line | deferred | MEU-125 | D-275; `FFMPEG-LIBDVDCSS-BUNDLED` stays open |
| Commit, push, tag and upload | out-of-scope | — | D-276 committed the triage only and authorized no push; this session's commit waits for Mat's direction (H2-5) |

---

## Decision Log

None.

---

## History

| Event | Date | Agent | Detail |
|-------|------|-------|--------|
| Created | 2026-11-05 | claude-code-local (Claude Opus 5.5) | Initial MEU-113 handoff after H1-2 |
