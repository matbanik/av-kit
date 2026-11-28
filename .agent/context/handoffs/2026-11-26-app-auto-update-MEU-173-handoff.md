---
date: "2026-11-28"
project: "2026-11-26-app-auto-update"
meu: "MEU-173"
status: "complete"
action_required: "VALIDATE_AND_APPROVE"
template_version: "2.2"
verbosity: "standard"
plan_source: "docs/execution/plans/2026-11-26-app-auto-update/implementation-plan.md"
build_plan_section: "docs/build-plan/07-distribution.md §Update feed (MEU-173)"
agent: "claude-code-local (Claude Opus 5.5)"
reviewer: "codex (H1-7 execution review)"
predecessor: "2026-11-26-capture-key-inbox-scrollbars-MEU-167-handoff.md"
---

# Handoff: 2026-11-26-app-auto-update-MEU-173-handoff

> **Status**: `complete`
> **Action Required**: `VALIDATE_AND_APPROVE`

---

## Scope

**MEU**: MEU-173 Update feed (phase 7), from `APP-NO-IN-APP-UPDATE`, grouped as Session 106 with MEU-174. This handoff is the first of two: MEU-173 → [MEU-174](2026-11-26-app-auto-update-MEU-174-handoff.md). The session-wide records (the full gate table, the decisions, what stays Mat's) are in this handoff; the MEU-174 handoff carries the installed round trip, its three failed runs and their root cause (D-1583).
**Build Plan Section**: `docs/build-plan/07-distribution.md` §Update feed, with its `Delivered (Session 106)` note (row 18).
**Predecessor**: [2026-11-26-capture-key-inbox-scrollbars-MEU-167-handoff.md](2026-11-26-capture-key-inbox-scrollbars-MEU-167-handoff.md). Session 106 ran from `5e4ec2f` (`baseline.sha`), and `HEAD` did not move.

- **Feed block (`FEED_BLOCK`).** `ui/electron-builder.yml` has one `publish` entry: provider `github`, owner `matbanik`, repo `av-kit`, and no other key (no token).
- **No publish from a build (`DIST_NEVER_PUBLISHES`).** Every `electron-builder` call in `ui/package.json` and in the workflows carries `--publish never`, and no step that runs it is given a GitHub token. `tests/unit/test_ci_workflows.py` passes unchanged.
- **Feed files.** A build writes `latest.yml` and `av-kit-Setup-<v>.exe.blockmap` beside the installer, and `win-unpacked/resources/app-update.yml` names the GitHub feed.
- **Feed check (`FEED_CHECK`).** New `tools/check_update_feed.py` reads a build folder and ends `feed-ok` exit 0, or one reason per mismatch, exit 10 to 18 (`feed-missing` 10, `sha512-mismatch` 15, `name-mismatch` for a name with a space, and the rest). It uploads nothing.
- **Publish checklist (`FEED_CHECKLIST`).** New `docs/releases/publish-checklist-update-feed.md`: the three asset names, the feed check before the upload, the Latest and pre-release rule, the one-time manual install for rc.5 users, and the statement that the upload is Mat's. `gh release` appears only in lines marked as Mat's.
- **Records.** MEU-173 is `ready_for_review`; 07 §Update feed carries the Delivered note.

**What Mat sees.** Nothing changes in the app from MEU-173 alone. The next release build writes the two feed files beside the installer. Before uploading, Mat runs one command (`uv run python tools/check_update_feed.py <folder>`) that says `feed-ok` or names what is wrong, and the checklist lists the three files to attach.

**Plan:** [implementation-plan.md](../../../docs/execution/plans/2026-11-26-app-auto-update/implementation-plan.md) §Single-statement contracts. **Execution authorization:** `USER_EXPLICIT`, Mat: "commit 103 and go for 106". Decisions: `USER_EXPLICIT` 2026-11-18, "make the decisions always the recommenations". The plan review approved at round 3 of loop `aau-plan-2026-11-26-app-auto-update`. Receipts named by file name alone are in the session's receipts folder (the `2026-11-26-app-auto-update` folder under `RECEIPTS_DIR`).

---

## Acceptance Criteria

| AC | Type | Description | Source | Test(s) | Status |
|----|------|-------------|--------|---------|--------|
| AC-173.1 | unit | `ui/electron-builder.yml` carries `FEED_BLOCK`: one `publish` entry, provider `github`, owner `matbanik`, repo `av-kit`, no other key; a copy with another provider, a second entry or a `token` key fails | Local Canon: 07 §Update feed, Feed address row; Research-backed: R2 | `tests/unit/test_update_feed_config.py:79` | ✅ |
| AC-173.2 | unit | `DIST_NEVER_PUBLISHES`: every `electron-builder` call in `ui/package.json` and the workflows carries `--publish never`, with no GitHub token; `test_ci_workflows.py` passes unchanged | Local Canon: 07 §Update feed; PROJECT-PROFILE E5 | `tests/unit/test_update_feed_config.py:97` | ✅ |
| AC-173.3 | integration | A product-config build with `--publish never` writes `latest.yml` and the blockmap beside the installer, and `app-update.yml` names the GitHub feed; with `latest.yml` moved away the check ends `feed-missing`, exit 10 | Local Canon: 07 §Update feed, Feed files row; Research-backed: R2, R3 | row 3 build (`aau-row3-build.txt`, `aau-feed-real-3.json`) | ✅ |
| AC-173.4 | unit and integration | `FEED_CHECK` ends `feed-ok` on a correct folder and gives each mismatch its own reason and exit code; on the real build it ends `feed-ok`, and on a copy with one changed installer byte `sha512-mismatch` | Local Canon: 07 §Update feed, Check row | `tests/unit/test_check_update_feed.py:138`, `:156`, `:167`; row 3 build | ✅ |
| AC-173.5 | unit | `FEED_CHECKLIST` holds the three asset names, the check before the upload, the upload as Mat's step, the Latest and pre-release rule and the one-time manual install; no agent-run upload, release or push command | Local Canon: 07 §Update feed | `tests/unit/test_update_feed_config.py:140`, `:167` | ✅ |
| AC-174 (cross-ref) | sibling | AC-174.1 to AC-174.21 belong to MEU-174; that handoff carries their Red and Green evidence and the round trip that proves AC-174.19 and AC-174.20 (run `r20261128T062757Z-ac98b72`) | the plan | see the MEU-174 handoff | cross-ref |
| AC-61 (cross-ref) | pin | §Test pins: AC-61.18 in `login-item-nsh.test.ts` keeps its line (D-1553 names the five lines that change); MEU-174's | the plan; D-1553 | see the MEU-174 handoff | cross-ref |
| AC-114 (cross-ref) | named change | AC-114.2 and AC-114.3 change their expected `RMDir` line to `RMDir /r` (D-1553, row 13); MEU-174's | the plan; D-1553 | see the MEU-174 handoff | cross-ref |
| AC-106 (cross-ref) | named change | AC-106.5's OpenAPI delta script sets back `SettingsPutIn.update_interval` (D-1582); MEU-174's leaf | the plan; D-1582 | see the MEU-174 handoff | cross-ref |

<!-- CACHE BOUNDARY -->

---

## Evidence

### FAIL_TO_PASS

Red is row 1 (`aau-row1-red.txt`: `16 failed in 7.70s`; `aau-row1-red-check.txt`: `7 required test(s), 0 allowed pass(es), 0 step target(s), 0 problem(s)`), Green row 2 (`aau-row2-green.txt`: `75 passed in 14.47s`; `aau-row2-selftest.txt`: `check-update-feed selftest: 10/10 ok`). AC-173.3 has no Red of its own: it is a build, and its negative (`feed-missing exit=10`) ran at row 3.

| Test | Red Output (hash/snippet) | Green Output | File:Line |
|------|---------------------------|--------------|-----------|
| AC-173.1 | `AssertionError: assert ['no publish block'] == []` | Row 2: `75 passed` | `tests/unit/test_update_feed_config.py:79` |
| AC-173.2 | Row 1: failed with the 16 (`aau-row1-red.txt`) | Row 2 | `tests/unit/test_update_feed_config.py:97` |
| AC-173.4 | `test_ac_173_4_each_mismatch_has_its_reason[...]` and `test_ac_173_4_selftest_passes` failed (no `tools/check_update_feed.py`) | Row 2; selftest `10/10 ok` | `tests/unit/test_check_update_feed.py:138`, `:156`, `:167` |
| AC-173.5 | Row 1: failed with the 16 (no checklist) | Row 2 | `tests/unit/test_update_feed_config.py:140`, `:167` |

### Commands Executed

```json
{"schema_version": "evidence.v1", "cwd": "P:/av-kit", "check_id": "aau-1-2-feed-unit", "command": "task.md rows 1 and 2 Validation cells (rtk proxy uv run pytest tests/unit/test_update_feed_config.py tests/unit/test_check_update_feed.py ...); receipts C:/Temp/av-kit/2026-11-26-app-auto-update/aau-row1-*.txt, aau-row2-*.txt", "scope": "AC-173.1, AC-173.2, AC-173.4, AC-173.5 Red then Green", "phase": "green", "exit_code": 0, "result": "pass", "tested_state": "HEAD 5e4ec2f (baseline.sha) plus rows 0 to 2", "output": "aau-row1-red.txt: 16 failed in 7.70s. aau-row1-red-check.txt: 7 required test(s), 0 problem(s). aau-row2-green.txt: 75 passed in 14.47s. aau-row2-selftest.txt: check-update-feed selftest: 10/10 ok"}
```

```json
{"schema_version": "evidence.v1", "cwd": "P:/av-kit", "check_id": "aau-3-real-build", "command": "$env:ELECTRON_RUN_AS_NODE=$null; pwsh -NoProfile -File docs/execution/plans/2026-11-26-app-auto-update/build-update.ps1 (task.md row 3); receipt C:/Temp/av-kit/2026-11-26-app-auto-update/aau-row3-build.txt, aau-feed-real-3.json", "scope": "AC-173.3 and AC-173.4 on a real product-config build with --publish never", "phase": "runtime", "exit_code": 0, "result": "pass", "tested_state": "HEAD 5e4ec2f (baseline.sha) plus rows 0 to 3", "output": "aau-row3-build.txt: resources check: every extraResources target and app-update.yml is present; check-update-feed: feed-ok exit=0; latest.yml moved away: check-update-feed: feed-missing exit=10; one changed installer byte: check-update-feed: sha512-mismatch exit=15; payload av-kit-Setup-0.1.0-rc.5.exe 371756740; build-update: product-ok exit=0"}
```

```json
{"schema_version": "evidence.v1", "cwd": "P:/av-kit", "check_id": "aau-18-canon-status", "command": "task.md row 18 Validation cell in its original form (scratchpad cell-18.ps1, D-1584); receipts C:/Temp/av-kit/2026-11-26-app-auto-update/aau-row18-*.txt", "scope": "Row 18: APP-NO-IN-APP-UPDATE resolved, the 07, 06 and README texts with the pass wording, the phase 7 note (D-1581), MEU-173 and MEU-174 ready_for_review", "phase": "static", "exit_code": 0, "result": "pass", "tested_state": "HEAD 5e4ec2f (baseline.sha) plus rows 0 to 18", "output": "aau-row18-issue.txt: issue-resolve: 0 problem(s). aau-row18-issues-check.txt: OK: known-issues.md is up-to-date. aau-row18-canon-check.txt: row-check canon: 0 problem(s). aau-row18-status-check.txt: status MEU-173: ready_for_review; status MEU-174: ready_for_review; row-check status: 0 problem(s). aau-row18-render-check.txt: Drift check passed (174 MEUs, 12 phases). aau-row18-register-check.txt: register APP-NO-IN-APP-UPDATE: resolved. aau-row18-eol.txt: eol-check: 87 scope path(s), 0 problem(s)"}
```

```json
{"schema_version": "evidence.v1", "cwd": "P:/av-kit", "check_id": "aau-h1-2-gate", "command": "$env:ELECTRON_RUN_AS_NODE=$null; rtk proxy pwsh -NoProfile -File docs/execution/plans/2026-11-26-app-auto-update/session-gate.ps1 *> C:/Temp/av-kit/2026-11-26-app-auto-update/aau-gate-h1.txt (task.md row H1-2's Validation cell), run r11 after execution review round 1; step receipts C:/Temp/av-kit/2026-11-26-app-auto-update/aau-D6-*.txt", "scope": "H1-2: the registered verification plan (implementation-plan.md Verification Plan 5): identity before and after, 20 static steps, 10 fresh full steps and remote-run-2", "phase": "full", "exit_code": 0, "result": "pass", "tested_state": "5e4ec2fd9debecdfbafb4cf02e36cc5f2f88ded9+e2c303d189d33a0c08fca2736e76781cb9344b8c574cd5569f273a896fd04221", "fresh": true, "snapshot": false, "output": "aau-gate-h1.txt: tested_state before=5e4ec2fd9debecdfbafb4cf02e36cc5f2f88ded9+e2c303d189d33a0c08fca2736e76781cb9344b8c574cd5569f273a896fd04221 after=5e4ec2fd9debecdfbafb4cf02e36cc5f2f88ded9+e2c303d189d33a0c08fca2736e76781cb9344b8c574cd5569f273a896fd04221; session-gate: all steps exit 0. aau-D6-ui-tests.txt: Test Files  165 passed (165), Tests  1803 passed (1803). aau-D6-py-tests.txt: 3412 passed, 37 warnings in 482.36s (0:08:02). aau-D6-mcp-tests.txt: Tests  560 passed (560). aau-D6-mcp-audit.txt: mcp-audit authoritative: 104/104 pass, 0 discovery finding(s), cleanup ok, exit 0. aau-D6-remote-run-2.txt: remote-run-2: run r20261128T062757Z-ac98b72 ok exit=0; row-check remote-run-2: 0 problem(s)"}
```

### Quality Gate Results

Before execution review round 1, run r8 passed all 33 steps with the identity unchanged from start to end. Each earlier run's receipts are kept with an `-rN` suffix. Runs r1 to r4 stopped on this plan's own files, each fixed at its source: r1 at py-lint (long lines in `canon-edit.py`), r2 at task-contract (row 17's `[B]` form), r3 at py-tests (AC-106.5's OpenAPI delta, D-1582) and r4 at py-format (`canon-edit.py`, D-1586). Runs r5 and r6 stopped at ui-tests on the PC, not on the code: r5 on load timeouts (D-1587, ruled on by the coordinator in D-1588) and r6 on the system commit limit, which another repository's pytest run had exhausted (out-of-memory aborts and `spawn UNKNOWN`, D-1589). Every affected file passed alone (`aau-h12-untouched-iso.txt`, `aau-h12-settings-iso.txt`, `aau-h12-r6-iso.txt`), and the gate reran unchanged. Run r7 was the first to reach mcp-audit; its bare `run audit` was refused (exit 4), and the step now takes row 11's authoritative form (D-1590). No timeout was raised and no test was excused. After the round-1 corrections (D-1591, D-1592), run r9 stopped at line-endings on the coordinator's CRLF copy of the review (D-1593), run r10 stopped at mcp-audit with the display off (D-1594), and run r11 (`aau-gate-h1.txt`) passed all 33 steps (ui-tests 1803 of 1803, py-tests 3412, MCP 560 of 560, the tool audit 104 of 104; remote-run-2 bound to run `r20261128T062757Z-ac98b72`), with the identity unchanged from start to end.

| Step | Stage | Result | Decisive line | Receipt |
|------|-------|--------|---------------|---------|
| identity-before | identity | exit 0 | `tested_state 5e4ec2fd9debecdfbafb4cf02e36cc5f2f88ded9+e2c303d189d33a0c08fca2736e76781cb9344b8c574cd5569f273a896fd04221` | `aau-D6-identity-before.txt` |
| ui-types | static | exit 0 | `tsc --noEmit: no diagnostics` | `aau-D6-ui-types.txt` |
| ui-lint | static | exit 0 | `eslint src/ tests/ --max-warnings 0: no diagnostics` | `aau-D6-ui-lint.txt` |
| py-types | static | exit 0 | `0 errors, 0 warnings, 0 informations` | `aau-D6-py-types.txt` |
| py-lint | static | exit 0 | `All checks passed!` | `aau-D6-py-lint.txt` |
| py-format | static | exit 0 | `15 files already formatted` | `aau-D6-py-format.txt` |
| task-contract | static | exit 0 | `OK: 38 row(s); 10-column table (with builder_model); 36 row(s) fully checked: backticked, exit-code re-raised, receipt under RECEIPTS_DIR; dependencies resolve and are acyclic; 2 row(s) exempt (view_file): H1-5, H2-1` | `aau-D6-task-contract.txt` |
| scope-paths | static | exit 0 | `row-check scope-paths: 0 problem(s)` | `aau-D6-scope-paths.txt` |
| line-endings | static | exit 0 | `eol-check: 87 scope path(s), 0 problem(s)` | `aau-D6-line-endings.txt` |
| pins-scan | static | exit 0 | `pins-scan --check: 0 problem(s)` | `aau-D6-pins-scan.txt` |
| red-unchanged | static | exit 0 | `row-check red-unchanged: 0 problem(s)` | `aau-D6-red-unchanged.txt` |
| canon | static | exit 0 | `row-check canon: 0 problem(s)` | `aau-D6-canon.txt` |
| row-check-selftest | static | exit 0 | `row-check selftest: 22/22 ok` | `aau-D6-row-check-selftest.txt` |
| pins-scan-selftest | static | exit 0 | `pins-scan selftest: 11/11 ok` | `aau-D6-pins-scan-selftest.txt` |
| run-check-selftest | static | exit 0 | `run-check selftest: 15/15 ok` | `aau-D6-run-check-selftest.txt` |
| licence-check-selftest | static | exit 0 | `licence-check selftest: 8/8 ok` | `aau-D6-licence-check-selftest.txt` |
| red-check-selftest | static | exit 0 | `red-check selftest: 144 fixture(s) (39 positive, 105 negative), 0 wrong: []` | `aau-D6-red-check-selftest.txt` |
| eol-check-selftest | static | exit 0 | `eol-check selftest: 24 case(s), 0 wrong: []` | `aau-D6-eol-check-selftest.txt` |
| identity-selftest | static | exit 0 | `identity selftest: 0 failure(s)` | `aau-D6-identity-selftest.txt` |
| snapshot-selftest | static | exit 0 | `snapshot-commit selftest: 0 failure(s)` | `aau-D6-snapshot-selftest.txt` |
| feed-check-selftest | static | exit 0 | `check-update-feed selftest: 10/10 ok` | `aau-D6-feed-check-selftest.txt` |
| ui-tests | full | exit 0 | `Tests  1803 passed (1803)` | `aau-D6-ui-tests.txt` |
| py-tests | full | exit 0 | `3412 passed, 37 warnings in 482.36s (0:08:02)` | `aau-D6-py-tests.txt` |
| ui-build | full | exit 0 | `✓ built in 8.05s` | `aau-D6-ui-build.txt` |
| mcp-types | full | exit 0 | `tsc --noEmit && tsc -p tsconfig.scripts.json: no diagnostics` | `aau-D6-mcp-types.txt` |
| mcp-tests | full | exit 0 | `Tests  560 passed (560)` | `aau-D6-mcp-tests.txt` |
| mcp-build | full | exit 0 | `tsc -p tsconfig.json: no diagnostics` | `aau-D6-mcp-build.txt` |
| mcp-audit | full | exit 0 | `mcp-audit authoritative: 104/104 pass, 0 discovery finding(s), cleanup ok, exit 0` | `aau-D6-mcp-audit.txt` |
| openapi | full | exit 0 | `export_openapi.py --check openapi.committed.json: no difference, exit 0` | `aau-D6-openapi.txt` |
| state-render | full | exit 0 | `✅ Drift check passed — SSOT loaded (174 MEUs, 12 phases), rendered regions match on-disk content` | `aau-D6-state-render.txt` |
| issues-render | full | exit 0 | `OK: known-issues.md is up-to-date` | `aau-D6-issues-render.txt` |
| remote-run-2 | full | exit 0 | `row-check remote-run-2: 0 problem(s)` | `aau-D6-remote-run-2.txt` |
| identity-after | identity | exit 0 | `tested_state 5e4ec2fd9debecdfbafb4cf02e36cc5f2f88ded9+e2c303d189d33a0c08fca2736e76781cb9344b8c574cd5569f273a896fd04221` | `aau-D6-identity-after.txt` |

---

## Changed Files

Counts are added / removed lines against `HEAD` `5e4ec2f` (`git diff --numstat --ignore-cr-at-eol HEAD`); a new file's count is its line count. The MEU-174 files are in that handoff.

| File | Change | Added / removed |
|------|--------|-----------------|
| `ui/electron-builder.yml` | `FEED_BLOCK` | +6 / -0 |
| `ui/package.json` | the `dist` script with `--publish never`; `electron-updater` 6.8.11 (MEU-174) | +2 / -1 |
| `tools/check_update_feed.py` | `FEED_CHECK` | new, 251 |
| `docs/releases/publish-checklist-update-feed.md` | `FEED_CHECKLIST` | new, 78 |
| `tests/unit/test_update_feed_config.py` | AC-173.1, AC-173.2, AC-173.5 | new, 180 |
| `tests/unit/test_check_update_feed.py` | AC-173.4 | new, 185 |
| `docs/build-plan/07-distribution.md` | §Goal, the Auto-update row, the Delivered notes for the feed and the in-app update (D-1584) | +20 / -4 |
| `docs/build-plan/06-gui.md` | the `app.update_interval` row and the Updates section | +8 / -0 |
| `README.md` | the offline sentence and the Updates paragraph | +12 / -1 |
| `docs/BUILD_PLAN.md` | rendered from the phase 7 note (D-1581) | +2 / -2 |
| `.agent/context/meu-status.yaml` | MEU-173 and MEU-174 `ready_for_review`; the phase 7 note | +12 / -11 |
| `.agent/context/meu-registry.md` | rendered status of both MEUs | +2 / -2 |

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

### Verdict

Pending: the H1-7 execution review.

---

## Deferred Items

| Item | Kind | Deferred-to | Basis |
|------|------|-------------|-------|
| The first release that carries the feed files, and their upload | Mat's step | Mat | D-1543 and D-1544 are open and Mat's; the checklist marks the upload as Mat's |
| The one-time manual install of the next release for rc.5 users (rc.5 has no updater) | Mat's step | Mat | `FEED_CHECKLIST` |
| D-1543, trust (SHA-512 over HTTPS, no publisher signature) | open decision | Mat | Recommendation: ship it and say so in the release notes, the README and the Settings card; do nothing: hold the updater until the installer is signed |
| D-1544, the new request to GitHub | open decision | Mat | Recommendation: name it in 07 §Goal, the README and the release notes, with Never as the switch; do nothing: hold the updater back |
| Commit and push | out-of-scope | — | Only on Mat's direction (H2) |

### Departures and their basis

- **The plan's decisions.** D-1540 to D-1542 and D-1545 to D-1554 are in the plan's §Decision Log as chosen; D-1543 and D-1544 stay open (above).
- **Execution decisions, D-1555 to D-1594** (the session's `decisions.yaml` in the receipts folder, each `resolution: autonomous` under "make the decisions always the recommenations"):
  - D-1555: the E2E remote tests live in `tests/tooling/test_e2e_remote.py`, the file that exists.
  - D-1556: the plan-local scripts were copied from Session 103's adapted copies.
  - D-1557: row 0's reserved-id scan counts only a definition.
  - D-1558: three scripts left the selftest list; their long lines were fixed.
  - D-1559, D-1560: how `pins-scan.py` decides that a file enumerates a list, and what it records.
  - D-1561: the snapshot build runs in a shared clone at the snapshot commit.
  - D-1562: Windows PowerShell 5.1 one-element unrolling in the selection block.
  - D-1563: `build-update.ps1` creates the archive folder before copying the cached ffmpeg pin.
  - D-1564: `%APPDATA%/av-kit` is the fifth precondition folder.
  - D-1565: the main and install stages share one stage call.
  - D-1566: an in-process script block replaces a nested pwsh in row 5's cell.
  - D-1567: row 11's MCP run reran unchanged (560 of 560).
  - D-1568: the MCP audit runs in authoritative mode against the baseline.
  - D-1569, D-1572: two pins files the two-name scan missed are named by the plan and grow.
  - D-1570: where the new IPC channels sit in the lists.
  - D-1571: one shared `shutdownForQuit()`.
  - D-1573: `UpdatesCard.tsx` imports `GridSelect` from `SettingsPage.tsx`.
  - D-1574: `run-check.py` compares AC id sets.
  - D-1575: the updater's log lines also go to stdout.
  - D-1576: each version of the pair is packed from a generated builder config.
  - D-1577: the `lazy-val` licence override (see the MEU-174 handoff).
  - D-1578, D-1579: two spec fixes to the round-trip spec; mechanics only.
  - D-1580: row 17 is `[B]` (B-17); the gate and rows 18 and H1-3 are adapted. D-1584 later lifted it.
  - D-1581: `BUILD_PLAN.md:51` is rendered from the phase 7 note.
  - D-1582: AC-106.5's OpenAPI delta sets back `SettingsPutIn.update_interval`, as D-1600 did for the cookie shapes.
  - D-1583: the root cause of B-17 (Windows reads Start at sign-in under the AppUserModelId, still Electron's default at startup); `boot()` sets it, a unit test went Red then Green, the pair was rebuilt and one verification run passed (see the MEU-174 handoff).
  - D-1584: B-17 is lifted; row 18 and H1-3 run in their original form, the issue is resolved and both MEUs are `ready_for_review`.
  - D-1585: `row-check.py remote-run-2` expected the run's last line to say `green`; `tools/e2e_remote.py` prints `ok exit=0`, so the check now takes `ok` (selftest 22 of 22). A tooling fix before the gate reached that step, not a retry.
  - D-1586: gate run r4 failed py-format on `canon-edit.py`; `ruff format` fixed it, with its edit data unchanged.
  - D-1587: gate run r5 failed ui-tests on load timeouts, one in `settings-rail.test.tsx`, a session file; H1-2 was blocked (B-H1-2) for the coordinator.
  - D-1588: the coordinator ruled that a failure counts against the session only if the session's change could cause it; the gate reran unchanged.
  - D-1589: gate run r6 failed ui-tests because another repository's pytest run had exhausted the PC's commit limit (out-of-memory aborts and `spawn UNKNOWN`, not timeouts); the 12 affected files passed alone, and the gate reran once that run had ended.
  - D-1590: gate run r7 was the first to reach mcp-audit, and the gate's bare `run audit` was refused (exit 4); the step now takes row 11's authoritative form (D-1568), and run r8 passed.
  - D-1591: execution review round 1, F1. `hardenUpdater()` gives electron-updater a nil staging id that it never writes to `.updaterId`, and deletes `x-user-staging-id` before the library's own header merge, so a check carries no identifier (D-1544's recommended contract). A staged release then always applies; the project publishes none.
  - D-1592: execution review round 1, F2. `hardenUpdater()` sets the library's logger to null (its NoOpLogger), so the controller's sanitized line (`UPDATE_QUIET_FAILURE`) is the only log output.
  - D-1593: gate run r9 stopped at line-endings on the coordinator's CRLF copy of the round-1 review; the canonical copy took LF with its text unchanged.
  - D-1594: gate run r10 stopped at mcp-audit (93 of 104): the dev PC's display was off, so every screen grab was black and capture.capture failed; the session's change cannot cause that. Once the display was on, a capture probe was not black, and gate run r11 passed unchanged.

---

## Decision Log

None.

---

## History

| Event | Date | Agent | Detail |
|-------|------|-------|--------|
| Created | 2026-11-28 | claude-code-local (Claude Opus 5.5) | Handoff after the H1-2 gate, H1-3, H1-4 and H1-5 |
| Updated | 2026-11-28 | claude-code-local (Claude Opus 5.5) | Execution corrections round 1: F1 and F2 fixed (D-1591, D-1592), the review copy's line ends (D-1593), the display-off stop (D-1594); row 16 rebuilt at snapshot `ac98b72`, row 17 run `r20261128T062757Z-ac98b72` passed; gate run r10 stopped at the capture audit, display off; gate run r11 passed |
