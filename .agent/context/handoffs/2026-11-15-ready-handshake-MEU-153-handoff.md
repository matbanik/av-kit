---
date: "2026-11-17"
project: "2026-11-15-ready-handshake"
meu: "MEU-153"
status: "complete"
action_required: "VALIDATE_AND_APPROVE"
template_version: "2.2"
verbosity: "standard"
plan_source: "docs/execution/plans/2026-11-15-ready-handshake/implementation-plan.md"
build_plan_section: "bp04"
agent: "claude-code-local (Claude Opus 5.5)"
reviewer: "codex (H1-7 execution review)"
predecessor: "none"
---

# Handoff: 2026-11-15-ready-handshake-MEU-153-handoff

> **Status**: `complete`
> **Action Required**: `VALIDATE_AND_APPROVE`

---

## Scope

**MEU**: MEU-153 `api-ready-after-listen` (issue `BACKEND-READY-BEFORE-LISTEN`, triage D-810). The backend listens on its socket before it writes the runtime descriptor and prints `AVKIT_READY`, so a request sent the moment the ready line appears is queued instead of refused. The ready line and the descriptor are unchanged.
**Build Plan Section**: [04 §READY after listen (residual)](../../../docs/build-plan/04-rest-api.md#ready-after-listen-residual) (matrix 4.5), with the Delivered (Session 82) note at the end of that section.
**Predecessor**: none. MEU-154 follows in the same session.

- **Listen first (D-978).** `main()` calls `sock.listen(config.backlog)` straight after `config.bind_socket()` and before `write_descriptor` and the ready print, with a one-line comment citing `07-distribution.md:73` (`cli.py:219-220`, `LISTEN_FIRST`). The module docstring (`cli.py:1`) and `main()`'s docstring now say listen. `server.run(sockets=[sock])` is unchanged; asyncio's later `listen()` on the same socket is harmless (plan §Research References).
- **Line kept (D-978).** The printed line stays `AVKIT_READY port={n} instance={uuid4}` with `flush=True`; the port is the bound socket's; the descriptor's fields, file names and atomic write are unchanged (`READY_TEXT_KEPT`, AC-153.2).
- **Tests (D-982).** AC-153.1 runs the real `main()` with stubs and reads `SO_ACCEPTCONN` at the descriptor write and at the print; AC-153.2 pins the line's text; AC-153.3 spawns the backend five times and connects as soon as the ready line appears.
- **Packaged smoke (D-983).** Row 4 built the onedir backend from this tree with PyInstaller into a scratch folder outside `packaging/`, checked `_internal` for forbidden packages, and ran `tools/smoke_packaged_runtime.py` on it. `packaging/dist/` and `packaging/build/` were not written (the existing exe still has the SHA-256, size and mtime in `baseline-packaged.json`: `rh-packaged-unchanged.txt`, `matches baseline-packaged.json: True`).
- **The measurement (D-981, `GAP_MEASURED`).** `ready-gap-probe.mjs` sends a Node `fetch` the moment the ready line appears (`fetch` mode) or after the same CIM process query the desktop app runs (`cim` mode); `gap-tally.py` counts the outcomes. The counts are in the table below.
- **Records (row 7).** The 04 Delivered (Session 82) note; `BACKEND-READY-BEFORE-LISTEN` resolved through `issue-resolve.py` (`issue-resolve: 0 problem(s)`); MEU-153 `ready_for_review` (`rh-status-153.txt`); grouping row 82 `executed (Session 82)`.

**Can the first request hit the gap?** Yes, before the fix, for any client that sends on the ready line: the dev backend refused 4 of 5 such requests and the packaged backend 5 of 5. Today's desktop app on this PC did not hit it, because its CIM live query runs before it publishes and takes longer than the gap (5 of 5 `http 200` in `cim` mode); it would hit it only on a machine where that query is faster than the startup gap. After the fix every first request was answered.

| Run | Backend | Mode | Runs | Outcomes | Port accepted after the line | Receipt |
|---|---|---|---|---|---|---|
| Row 1, before the fix | dev | `fetch` | 5 | `"http 200": 1, "ECONNREFUSED": 4`; `"refused": 4, "errors": 0` | 13–28 ms | `rh-gap-before-tally.txt` (`gap-tally dev-fetch-before`) |
| Row 1, before the fix | dev | `cim` | 5 | `"http 200": 5`; `"refused": 0, "errors": 0` | 386–427 ms | `rh-gap-before-tally.txt` (`gap-tally dev-cim-before`) |
| Row 1, before the fix | `packaging/dist` exe, read-only | `fetch` | 5 | `"ECONNREFUSED": 5`; `"refused": 5, "errors": 0` | 19–33 ms | `rh-gap-before-tally.txt` (`gap-tally packaged-before`) |
| Row 3, after the fix | dev | `fetch` | 10 | `"http 200": 10`; `"refused": 0, "errors": 0` | 21–27 ms | `rh-gap-dev-after-tally.txt` (`gap-tally dev-fetch-after`, `--all-ok`) |
| Row 4, after the fix | scratch build of this tree | `fetch` | 5 | `"http 200": 5`; `"refused": 0, "errors": 0` | 16–23 ms | `rh-gap-packaged-after-tally.txt` (`gap-tally packaged-after`, `--all-ok`) |

The "port accepted" column is `accept_after_ready_ms` (min–max) from each tally line: the time from the ready line to the first connect check that succeeded, made after the first request (in `cim` mode after the CIM query as well, so it includes that query's time).

**Scratch build.** Row 4's build used this working tree, which also held other sessions' uncommitted changes (`baseline-dirty.txt`). It is a local smoke of this tree, not a release build, and it was not copied into `packaging/`.

**Plan:** [implementation-plan.md](../../../docs/execution/plans/2026-11-15-ready-handshake/implementation-plan.md) §MEU-153. **Execution authorization:** `USER_EXPLICIT`, 2026-11-15, "proceed with planning and execution for P:\av-kit\.agent\context\grouping\2026-11-15-post-rc3-triage-residuals-session-grouping.md like we did here. But use the new HDP process. Continue orchestrating the sessions." (`plan_to_exec_gate: human`; the plan's Status line, `implementation-plan.md:15`). The plan review approved at round 1 ([plan-critical-review.md](2026-11-15-ready-handshake-plan-critical-review.md)). The plan's Status line was changed after that review, and the plan has grown since; see Departures.

**Receipts.** A receipt named by its file name alone is in the session's receipts folder (the `ready-handshake` folder under `RECEIPTS_DIR`). Full paths appear only in the evidence records' `command` fields.

---

## Acceptance Criteria

| AC | Type | Description | Source | Test(s) | Status |
|----|------|-------------|--------|---------|--------|
| AC-153.1 | unit | `main()` with stubs: at the `write_descriptor` call and at the ready print the kept socket reads `SO_ACCEPTCONN == 1`; the test first asserts `hasattr(socket, "SO_ACCEPTCONN")` and that both spies ran once | Local Canon (04 §READY after listen; 07:73); Research-backed (plan-time `SO_ACCEPTCONN` probe) | `tests/unit/test_backend_cli.py:208` | ✅ |
| AC-153.2 | unit | The same run prints exactly one line matching `^AVKIT_READY port=(\d+) instance=[0-9a-f-]{36}$`, its port equals the socket's and the descriptor's, and `flush=True` was passed (a pin: it passed in Red too) | Local Canon (04: Line unchanged; MEU-24, MEU-108) | `tests/unit/test_backend_cli.py:224` | ✅ |
| AC-153.3 | integration | Five spawns of `python -m avkit_api`: as soon as the ready line appears a 0.25 s connect succeeds and `GET /api/v1/health` returns 200, all five | Local Canon (04: Tests); Research-backed (plan-time connect probe) | `tests/integration/test_backend_spawn.py:145` | ✅ |
| AC-153.4 | integration | The onedir backend built from this tree into the scratch dist has none of `torch`, `kokoro`, `phonemizer` or `espeakng_loader` under `_internal`, and `tools/smoke_packaged_runtime.py` exits 0 on it | Local Canon (04: Tests; MEU-141 `RUNTIME_SMOKE`) | row 4: `rh-pack-check.txt`, `rh-smoke-runtime.txt`; gate `packaged-receipt` | ✅ |
| AC-153.5 | integration | The measurement: before-fix dev `fetch`, dev `cim` and packaged `fetch` counts (row 1); after the fix 10 dev and 5 packaged `fetch` runs, each `gap-tally.py --all-ok` exit 0 (rows 3 and 4); the counts are in this handoff and 04's note | Local Canon (grouping §3) | `ready-gap-probe.mjs` with `gap-tally.py`: `rh-gap-before-tally.txt`, `rh-gap-dev-after-tally.txt`, `rh-gap-packaged-after-tally.txt` | ✅ |
| AC-19 (cross-ref) | guard | AC-19.1 to AC-19.4, the existing CLI parser, descriptor and spawn tests in the same two files, pass unchanged | MEU-19 | `tests/unit/test_backend_cli.py`, `tests/integration/test_backend_spawn.py` (gate `meu-153-tests`) | ✅ |
| AC-108 (cross-ref) | guard | The MEU-108 ready-guard pins (AC-108.1 to AC-108.7) read this ready line on the GUI side; they pass unchanged and are evidenced in the MEU-154 handoff (AC-154.9) | MEU-108 | `ui/tests/unit/ready-probe-guard.test.ts`, `ui/tests/e2e/backend-output-after-close.test.ts` (gate `meu-154-tests`, `e2e-late-line`) | ✅ |
| AC-154 (sibling) | sibling MEU | AC-154.1 to AC-154.9: the GUI reads the ready line whole, from stdout only, and publishes once; evidenced in the MEU-154 handoff | MEU-154 | `2026-11-15-ready-handshake-MEU-154-handoff.md` | ✅ |

<!-- CACHE BOUNDARY -->

---

## Evidence

### FAIL_TO_PASS

| Test | Red Output (hash/snippet) | Green Output | File:Line |
|------|---------------------------|--------------|-----------|
| AC-153.1 `test_ac_153_1_socket_listens_before_descriptor_and_ready_line` | `E   assert (0, 0) == (1, 1)` (`rh-153-red.txt`) | Row 3: pass (`rh-153-green.txt`) | `tests/unit/test_backend_cli.py:208` |
| AC-153.3 `test_ac_153_3_connect_on_ready_line_is_accepted_five_spawns` | `E   AssertionError: [False, False, False, False, False]` (`rh-153-red.txt`) | Row 3: pass (`rh-153-green.txt`) | `tests/integration/test_backend_spawn.py:145` |

- **Row 2 Red.** `rh-153-red.txt`: `2 failed, 1 passed, 8 deselected in 10.48s`, exit 1 (`rh-153-red.txt.exit`). AC-153.2, the pin, is the one that passed. `rh-153-red-check.txt`: `red-check: 1 receipt(s), 2 required test(s), 0 problem(s)` (the D-919 pytest header form, D-985).
- **Row 3 Green.** `rh-153-green.txt`: `11 passed in 12.10s` (the two files whole: the AC-19 tests and AC-153.1 to AC-153.3); `rh-153-eol.txt`: `line-ending drift: []`. `rh-gap-dev-after-tally.txt`: the dev row of the table above.
- **Row 4.** `rh-pack-build.txt`: `Build complete! The results are available in:` the scratch dist; `rh-pack-check.txt`: `internal exists: True forbidden: [] deno: True cli_sha256: dba7dc4e3b22f01725e95deaf16c57492936aad90bb4e5f847c9aa5ccc046be3`; `rh-smoke-runtime.txt`: `PASS: smoke-runtime source=bundled version=2.9.8 solver=True`; `rh-gap-packaged-after-tally.txt`: the packaged row of the table above. The gate's `packaged-receipt` step checks that `cli.py` still has the SHA-256 row 4 built (`cli.py: match`).

### Commands Executed

```json
{"schema_version": "evidence.v1", "cwd": "P:/av-kit", "check_id": "rh-0-baseline", "command": "pwsh -NoProfile -File C:/Temp/av-kit/ready-handshake/run-row0.ps1 (task.md row 0's Validation cell: rtk proxy pwsh -NoProfile -File docs/execution/plans/2026-11-15-ready-handshake/baseline.ps1 *> C:/Temp/av-kit/ready-handshake/rh-baseline.txt); receipts rh-baseline.txt, rh-base-py.txt, rh-base-ui.txt, rh-base-ruff-format.txt, rh-base-ui-lint.txt", "scope": "Row 0: baseline.sha, the scope and dirty-tree hashes, the line-ending baseline, the packaged exe's hash, the row-0 file copies, the plan scripts' selftests and the base suites", "phase": "static", "exit_code": 0, "result": "pass", "tested_state": "HEAD 5e5b4ba (baseline.sha) plus row 0", "output": "rh-baseline.txt: baseline: all steps exit 0; gap-tally selftest: ok. rh-base-py.txt: 1 failed, 3031 passed, 37 warnings in 215.87s (0:03:35); the failure is test_ac_134_10_long_audio_past_the_last_frame (frame grab failed at 00:00:03.200), the registered VIDEO-REAL-FFMPEG-TAIL-FRAME-FLAKE. rh-base-ui.txt: Test Files  135 passed (135); Tests  1570 passed (1570)"}
```

```json
{"schema_version": "evidence.v1", "cwd": "P:/av-kit", "check_id": "rh-1-gap-before", "command": "pwsh -NoProfile -File C:/Temp/av-kit/ready-handshake/run-row1.ps1 (task.md row 1's Validation cell: rtk proxy node docs/execution/plans/2026-11-15-ready-handshake/ready-gap-probe.mjs --root C:/Temp/av-kit/ready-handshake/probe-runs --runs 5 --mode fetch, then --mode cim, on the dev backend, then --mode fetch on the packaging/dist exe read-only, then gap-tally.py on each); receipt rh-gap-before-tally.txt", "scope": "Row 1, D-981 GAP_MEASURED: the gap before the fix, dev fetch, dev cim and packaged fetch, five runs each", "phase": "runtime", "exit_code": 0, "result": "pass", "tested_state": "HEAD 5e5b4ba (baseline.sha) plus rows 0 to 1", "output": "rh-gap-before-tally.txt: gap-tally dev-fetch-before {\"runs\": 5, \"outcomes\": {\"http 200\": 1, \"ECONNREFUSED\": 4}, \"refused\": 4, \"errors\": 0, \"accept_after_ready_ms\": {\"min\": 13, \"max\": 28}, \"problems\": []}; gap-tally dev-cim-before {\"runs\": 5, \"outcomes\": {\"http 200\": 5}, \"refused\": 0, \"errors\": 0, \"accept_after_ready_ms\": {\"min\": 386, \"max\": 427}, \"problems\": []}; gap-tally packaged-before {\"runs\": 5, \"outcomes\": {\"ECONNREFUSED\": 5}, \"refused\": 5, \"errors\": 0, \"accept_after_ready_ms\": {\"min\": 19, \"max\": 33}, \"problems\": []}; tally exits: [0, 0, 0]"}
```

```json
{"schema_version": "evidence.v1", "cwd": "P:/av-kit", "check_id": "rh-2-red-153", "command": "pwsh -NoProfile -File C:/Temp/av-kit/ready-handshake/run-row2.ps1 (task.md row 2's Validation cell: rtk proxy uv run pytest tests/unit/test_backend_cli.py tests/integration/test_backend_spawn.py -k ac_153 --tb=short -q *> C:/Temp/av-kit/ready-handshake/rh-153-red.txt, its exit code, red-check.py --require test_ac_153_1 --require test_ac_153_3); receipts rh-153-red.txt, rh-153-red.txt.exit, rh-153-red-check.txt", "scope": "MEU-153 Red: AC-153.1 and AC-153.3 against the unchanged cli.py; AC-153.2 is a pin", "phase": "red", "exit_code": 0, "result": "pass", "tested_state": "HEAD 5e5b4ba (baseline.sha) plus rows 0 to 2", "output": "rh-153-red.txt: E   assert (0, 0) == (1, 1); E   AssertionError: [False, False, False, False, False]; 2 failed, 1 passed, 8 deselected in 10.48s; exit 1. rh-153-red-check.txt: red-check: 1 receipt(s), 2 required test(s), 0 problem(s)"}
```

```json
{"schema_version": "evidence.v1", "cwd": "P:/av-kit", "check_id": "rh-3-green-153", "command": "pwsh -NoProfile -File C:/Temp/av-kit/ready-handshake/run-row3.ps1 (task.md row 3's Validation cell: rtk proxy uv run pytest tests/unit/test_backend_cli.py tests/integration/test_backend_spawn.py --tb=short -q *> C:/Temp/av-kit/ready-handshake/rh-153-green.txt; ready-gap-probe.mjs --runs 10 --mode fetch on the dev backend and gap-tally.py --runs 10 --all-ok; the line-ending check); receipts rh-153-green.txt, rh-gap-dev-after-tally.txt, rh-153-eol.txt", "scope": "MEU-153 Green: LISTEN_FIRST and READY_TEXT_KEPT in cli.py; the dev gap after the fix", "phase": "green", "exit_code": 0, "result": "pass", "tested_state": "HEAD 5e5b4ba (baseline.sha) plus rows 0 to 3", "output": "rh-153-green.txt: 11 passed in 12.10s. rh-gap-dev-after-tally.txt: gap-tally dev-fetch-after {\"runs\": 10, \"outcomes\": {\"http 200\": 10}, \"refused\": 0, \"errors\": 0, \"accept_after_ready_ms\": {\"min\": 21, \"max\": 27}, \"problems\": []}. rh-153-eol.txt: line-ending drift: []"}
```

```json
{"schema_version": "evidence.v1", "cwd": "P:/av-kit", "check_id": "rh-4-packaged", "command": "pwsh -NoProfile -File C:/Temp/av-kit/ready-handshake/run-row4.ps1 (task.md row 4's Validation cell: rtk proxy uv run --offline --no-sync python -m PyInstaller --noconfirm --workpath C:/Temp/av-kit/ready-handshake/pack/build --distpath C:/Temp/av-kit/ready-handshake/pack/dist; the _internal and cli.py hash check; tools/smoke_packaged_runtime.py --backend-dir C:/Temp/av-kit/ready-handshake/pack/dist/avkit-backend; ready-gap-probe.mjs --runs 5 --mode fetch on that build and gap-tally.py --runs 5 --all-ok); receipts rh-pack-build.txt, rh-pack-check.txt, rh-pack-cli-sha.txt, rh-smoke-runtime.txt, rh-gap-packaged-after-tally.txt", "scope": "MEU-153 AC-153.4 and the packaged half of AC-153.5: a scratch onedir build of this tree, outside packaging/", "phase": "runtime", "exit_code": 0, "result": "pass", "tested_state": "HEAD 5e5b4ba (baseline.sha) plus rows 0 to 4", "output": "rh-pack-build.txt: Build complete! rh-pack-check.txt: internal exists: True forbidden: [] deno: True cli_sha256: dba7dc4e3b22f01725e95deaf16c57492936aad90bb4e5f847c9aa5ccc046be3. rh-smoke-runtime.txt: PASS: smoke-runtime source=bundled version=2.9.8 solver=True. rh-gap-packaged-after-tally.txt: gap-tally packaged-after {\"runs\": 5, \"outcomes\": {\"http 200\": 5}, \"refused\": 0, \"errors\": 0, \"accept_after_ready_ms\": {\"min\": 16, \"max\": 23}, \"problems\": []}"}
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

- **Last line** (`rh-gate-h1.txt`): `session-gate: all steps exit 0`. One run; nothing was rerun.
- **Identity:** tested_state `5e5b4ba18b293d9215f79be878b0fa7b815f83b5+8a1f1b0c2d5d366ce04112662dee50a7002181195c6366ff019c3ff80eb58594` before and after the gate (`rh-D6-identity-before.txt`, `rh-D6-identity-after.txt`).
- **Static:** ruff check `All checks passed!`; ruff format `4 files already formatted` (`cli.py`, the two test files, `gap-tally.py`); pyright `0 errors, 0 warnings, 0 informations`; the UI typecheck and lint exit 0 (`rh-D6-ui-types.txt`, `rh-D6-ui-lint.txt`); the task contract `OK: 25 row(s)`, 23 fully checked, 2 view_file exempt (H1-5, H2-1); scope paths `changed paths: 34 outside scope: [] other sessions plan files skipped: 2`, `baseline-dirty hash mismatch: [] of 3`, `head moved (S4): False`; line endings `line-endings files: 23 mismatch: []`; the red-check selftest `43 fixture(s) (14 positive, 29 negative), 0 wrong: []`; `gap-tally selftest: ok`.
- **Targeted:** MEU-153 `11 passed in 26.26s` (`rh-D6-meu-153-tests.txt`); MEU-154 `Tests  17 passed (17)` (`rh-D6-meu-154-tests.txt`); the packaged receipt `cli.py` SHA-256 `dba7dc4e3b22f01725e95deaf16c57492936aad90bb4e5f847c9aa5ccc046be3` recorded and current, `packaged-receipt: match`.
- **Fresh full:** the Python suite `3035 passed, 37 warnings in 222.49s (0:03:42)` (`rh-D6-py-tests.txt`); the UI suite `Test Files  137 passed (137)` and `Tests  1578 passed (1578)` (`rh-D6-ui-tests.txt`); the UI build `built in 3.94s`; `backend-output-after-close.test.ts` `1 passed (746ms)` (`rh-D6-e2e-late-line.txt`); the OpenAPI check exit 0; the state render `Drift check passed` (153 MEUs, 12 phases); the issue render `OK: known-issues.md is up-to-date`.
- **Skipped, with basis** (`rh-gate-h1.txt`): `mcp-types`, `mcp-build`, `mcp-tests`, `mcp-audit` ("no MCP change; the MCP Python tests run inside py-tests"); `test:e2e-rest` ("only the main process output handler changed, and AC-108.7 (e2e-late-line) is the E2E test that drives it"); `packaged-build` ("row 4 receipt, bound to cli.py by packaged-receipt").
- **Baseline failures excused:** the gate excuses a Python failure only when `rh-base-py.txt` shows it failed; that receipt shows one, `test_ac_134_10_long_audio_past_the_last_frame` (`1 failed, 3031 passed, 37 warnings in 215.87s`), the registered `VIDEO-REAL-FFMPEG-TAIL-FRAME-FLAKE`. In the gate it passed, and nothing failed. The UI suite excuses nothing.
- **Processes:** the gate's two pwsh processes were recorded by pid and creation time and had exited when it ended; a snapshot before and after showed two new processes, both another project's Python, which were not touched (`h1-2-procs-compare.txt`).
- **After the gate:** H1-3 added the current-focus paragraph, H1-4 ran the OpenAPI check (`openapi-check.txt`, exit 0), `task.md` rows were marked and these handoffs were written. `identity.py` excludes all of these, so no product, test or tracked record changed after the gate; H1-6b checks that the expected state still equals the gate's.

---

## Changed Files

Counts are added / removed lines against the row-0 copies (`baseline-copies/` in the receipts folder; `git diff --no-index --numstat --ignore-cr-at-eol`), not against `HEAD`, because other sessions' uncommitted work sits in the same tree. Line endings were measured as bytes (the gate's `line-endings` step).

| File | Change | Added / removed | Line endings |
|------|--------|-----------------|--------------|
| `packages/api/src/avkit_api/cli.py` | `sock.listen(config.backlog)` and its comment; the two docstrings | +4 / -2 | LF kept |
| `tests/unit/test_backend_cli.py` | AC-153.1 and AC-153.2 appended, with their stubs | +97 / -0 | CRLF kept |
| `tests/integration/test_backend_spawn.py` | AC-153.3 appended | +38 / -0 | LF kept |
| `docs/build-plan/04-rest-api.md` | the Delivered (Session 82) note | +6 / -0 | CRLF kept |

```diff
     sock = config.bind_socket()
+    # Listen before the descriptor and the ready line (07-distribution.md:73).
+    sock.listen(config.backlog)
     bound_port = int(sock.getsockname()[1])
```

The shared records (`known-issues.yaml` and `.md`, `meu-status.yaml`, `meu-registry.md`, `BUILD_PLAN.md`, the grouping file, `current-focus.md`) and MEU-154's files are listed in the MEU-154 handoff. Nothing is committed or staged.

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
| Commit and push | out-of-scope | — | Only on Mat's explicit words (H2-5) |

### Departures and their basis

- **The plan changed after its review.** The plan review approved `implementation-plan.md` at SHA-256 `34f17319305813137d2174ead2b6520779304564b00316d66d438d7ff23a49cf` (round 1). The coordinator then edited its Status line to record Mat's execute words (`implementation-plan.md:15`; 503 lines, SHA-256 starting `c06351b282ee`), so the reviewed hash no longer holds. During execution the plan grew by three execution decisions in its YAML, D-985 to D-987 (now 545 lines, SHA-256 `27325855657dced8e4a03067fd9cca8e7d8e4d896f60797a252656151f72d62a`). No AC, contract or file list changed. The H1-7 review covers both changes.
- **`red-check.py` takes the D-919 header (D-985).** Row 0 wrote this plan's `red-check.py` with Session 76's `^_+ (.+?) _+\s*$` pytest header and this session's boundary fixtures; the gate's selftest reads `43 fixture(s) (14 positive, 29 negative), 0 wrong: []`.
- **`gap-tally.py` formatted at row 0 (D-986).** Row 0's `ruff format --check` found the plan-time `gap-tally.py` unformatted; it was formatted before any other edit (two list comprehensions wrapped), its SHA-256 changed from `8eb4dc0d…` to `49c3f0ed…`, and its selftest ran again (`gap-tally selftest: ok`). The change is formatting only.
- **Row 0 helpers and extra receipts.** `make-copies.py`, a session helper, wrote the plan's `red-check.py`, `identity.py` and `issue-resolve.py` from their sources (each replacement must match once), and `baseline.ps1` then ran. Row 0 also kept receipts the row does not name: `rh-base-ui.txt`, `rh-base-ruff-format.txt`, `rh-base-ui-lint.txt`, `baseline-eol.json` (the line-ending baseline the gate reads) and `baseline-copies/` (the row-0 copies the Changed Files counts use).
- **Another session's files.** Session 83 (`docs-path-hygiene`) had three untracked files in the tree at row 0. They are bound by hash in `baseline-dirty-hashes.json`, and the gate found them unchanged (`baseline-dirty hash mismatch: [] of 3`); its plan folder is skipped (`other sessions plan files skipped: 2`). Nothing of it was opened for writing.
- **Row 2 docstrings.** After AC-153.1 to AC-153.3 were appended, their docstrings were shortened and the files formatted with `ruff format`, before the Red run (`rh-153-red.txt` was written after the last edit to either file).
- **Issue-resolve dry run.** Before row 7 wrote the register, `issue-resolve.py` ran with `--target` on a scratch copy of `known-issues.yaml` (`rh-issue-resolve-dry.txt`: `issue-resolve: 0 problem(s)`); the real run then matched (`rh-issue-resolve.txt`).
- **The session gate.** `session-gate.ps1` was written in this session on the peer shape. It runs the UI steps from `ui/` with `npm run`, and adds count checks to `meu-153-tests` (`11 passed`), `meu-154-tests` (`Tests  17 passed (17)`) and `e2e-late-line` (`1 passed`), so a run that skips tests fails. Its definitions and fast steps were dry-run first (`rh-gate-dry.txt`, exit 0).
- **The scratch build** included other sessions' uncommitted changes in the tree; it is a local smoke of this tree, not a release build (Scope).
- **Execution decisions** D-985 to D-987 are in the plan's decision YAML, each autonomous with `mandatory: none`, so the Decision Log below is `None.`. D-987 (AC-154.8 waits for `close`) is in the MEU-154 handoff.

---

## Decision Log

None.

---

## History

| Event | Date | Agent | Detail |
|-------|------|-------|--------|
| Created | 2026-11-17 | claude-code-local (Claude Opus 5.5) | Initial MEU-153 handoff after the H1-2 gate, H1-3 and H1-4 |
