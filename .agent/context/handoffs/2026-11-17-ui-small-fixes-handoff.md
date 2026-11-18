---
date: "2026-11-18"
project: "2026-11-17-ui-small-fixes"
meu: "none"
status: "complete"
action_required: "VALIDATE_AND_APPROVE"
template_version: "2.2"
verbosity: "standard"
plan_source: "docs/execution/plans/2026-11-17-ui-small-fixes/implementation-plan.md"
build_plan_section: "none (preview script; no MEU, D-1130)"
agent: "claude-code-local (Claude Opus 5.5)"
reviewer: "codex (H1-7 execution review)"
predecessor: "2026-11-17-video-tail-frame-MEU-160-handoff.md"
---

# Handoff: 2026-11-17-ui-small-fixes-handoff

> **Status**: `complete`
> **Action Required**: `VALIDATE_AND_APPROVE`

---

## Scope

**MEU**: none. The preview fix is test and tooling debt with no MEU (D-1130), from `UI-PREVIEW-ELECTRON-RUN-AS-NODE-SILENT`; it follows the Session 90 dev-script contract (`ui/scripts/electron-vite-dev.mjs`).
**Build Plan Section**: none.
**Predecessor**: [2026-11-17-video-tail-frame-MEU-160-handoff.md](2026-11-17-video-tail-frame-MEU-160-handoff.md), Session 93, committed as `9867e51`. Session 94 is the fourth session run of the 2026-11-17 value triage grouping (`.agent/context/grouping/2026-11-17-value-triage-session-grouping.md`), run from `9867e51`. Its other handoffs: [MEU-158](2026-11-17-ui-small-fixes-MEU-158-handoff.md) and [MEU-159](2026-11-17-ui-small-fixes-MEU-159-handoff.md).

- **The defect, reproduced (AC-3).** At base, `npm run preview` with `ELECTRON_RUN_AS_NODE` set opened no window and exited 1 (the proof's own expectation of a window failed; `--expect-notice no`), while the same proof with the variable unset opened a window. Electron runs as plain Node when that variable is set, and the old `electron-vite preview` script passed it through, as `dev` did before Session 90.
- **The fix (`PREVIEW_WRAPPER`, D-1178).** `electron-vite-dev.mjs` exports `runElectronVite(command, notice, extra)`, the body of its old `main()` with the subcommand, the notice and the error prefix as parameters; `main()` calls it with `dev`. The new `ui/scripts/electron-vite-preview.mjs` calls it with `preview` and `PREVIEW_NOTICE`, so it removes the variable, writes `electron-vite-preview: cleared ELECTRON_RUN_AS_NODE` to stderr when it did, and exits with the child's code. `ui/package.json:18` runs it.
- **One named pin (`PINS_NAMED`).** `ui/tests/unit/dev-script.test.ts:64` changes its expected preview script; nothing else in an existing test changes.
- **The docs (`COMMANDS_DOC`).** `.agent/docs/commands.md:80` gives the preview row the dev row's form.
- **Records.** `UI-PREVIEW-ELECTRON-RUN-AS-NODE-SILENT` is `resolved` (no `meu_links`).

**What Mat sees.** `npm --prefix ui run preview` now opens the app window even in a shell where `ELECTRON_RUN_AS_NODE` is set (such as the IDE's terminal), and says so on one stderr line; with the variable unset it opens as before, with no extra line. `npm run dev` behaves as it did after Session 90.

**Plan:** [implementation-plan.md](../../../docs/execution/plans/2026-11-17-ui-small-fixes/implementation-plan.md) §Single-statement contracts. **Execution authorization:** `USER_EXPLICIT`, 2026-11-17 ("orchestrate the plan creation for all sessions and proceed with execution for each"), `plan_to_exec_gate: human`; the plan review approved at round 2 (`.agent/context/handoffs/2026-11-17-ui-small-fixes-plan-critical-review.md`). Receipts named by file name alone are in the session's receipts folder (the `ui-small-fixes` folder under `RECEIPTS_DIR`).

---

## Acceptance Criteria

| AC | Type | Description | Source | Test(s) | Status |
|----|------|-------------|--------|---------|--------|
| AC-1 | unit | `preview-script.test.ts`: the script exists; `PREVIEW_NOTICE` is `'electron-vite-preview: cleared ELECTRON_RUN_AS_NODE'`; `previewArgs(['--x'])` is the electron-vite bin, `'preview'`, `'--x'`, with `devArgs([])[0]`'s bin; `runElectronVite` is exported by the dev module; importing both spawns nothing | Local Canon (D-1130; the Session 90 dev contract) | `ui/tests/unit/preview-script.test.ts:43` | ✅ |
| AC-2 | unit | `ui/package.json` `scripts.preview` is `'node ./scripts/electron-vite-preview.mjs'` and `scripts.dev` is unchanged | Local Canon (D-1130) | `ui/tests/unit/preview-script.test.ts:57` | ✅ |
| AC-3 | check | Row 5, base: `preview-proof.py --launch preview --run-as-node set --expect window --expect-notice no` exits 1 with no window and nothing left; `--run-as-node unset` exits 0 with a window | Local Canon (`UI-PREVIEW-ELECTRON-RUN-AS-NODE-SILENT`) | row 5 `us-prev-base-set.txt`, `us-prev-base-unset.txt`, `us-prev-base-check.txt` | ✅ set exit 1, unset exit 0 |
| AC-4 | check | Row 6 and the gate: `--run-as-node set --expect-notice yes` exits 0 (a window, the notice in the child's stderr log, not on stdout alone); `--run-as-node unset --expect-notice no` exits 0 | Local Canon (D-1130) | row 6 `us-prev-proof-set.txt`, `us-prev-proof-unset.txt`; gate `preview-proof` | ✅ |
| AC-5 | check | Row 6: `dev-script.test.ts` passes with the named pin; `--launch dev --run-as-node set --expect window --expect-notice yes` exits 0 | Local Canon (Session 90 dev contract) | row 6 `us-prev-green.txt`, `us-prev-proof-dev.txt` | ✅ |
| The dev-script pin (cross-ref, quoted) | guard | `ui/tests/unit/dev-script.test.ts:64`, in the test titled "AC-14 devArgs, isEntry, exitCodeFor and the package scripts" (`:41`); `AC-14` there is Session 90's id (`2026-11-17-test-run-reliability`), not a criterion of this plan. Its one named edit is `PINS_NAMED` (Changed Files); `:30` and the rest of `:41-…` (`devEnv`, `devArgs`, `isEntry`, `exitCodeFor`, `scripts.dev`) are unchanged | Local Canon (§Test pins; D-1178) | row 5 Red, row 6 Green (`us-prev-green.txt`); gate `preview-unit` | ✅ |
| AC-158.1 to AC-158.14 (cross-ref) | reference | MEU-158, F1 help waits for the page: the held-request helper, F1's route scope and its take on mount; owned by `.agent/context/handoffs/2026-11-17-ui-small-fixes-MEU-158-handoff.md` (AC-158.1, AC-158.2, AC-158.3, AC-158.4, AC-158.5, AC-158.6, AC-158.7, AC-158.8, AC-158.9, AC-158.10, AC-158.11, AC-158.12, AC-158.13, AC-158.14) | Local Canon (06 Held, Once and Shared rows) | that handoff | n/a: not this handoff's |
| AC-159.1 to AC-159.7 (cross-ref) | reference | MEU-159, the Downloader Advanced gap: the measured cause and the hidden empty status wrapper; owned by `.agent/context/handoffs/2026-11-17-ui-small-fixes-MEU-159-handoff.md` (AC-159.1, AC-159.2, AC-159.3, AC-159.4, AC-159.5, AC-159.6, AC-159.7) | Local Canon (11 Cause, Collapsed and Expanded rows) | that handoff | n/a: not this handoff's |

<!-- CACHE BOUNDARY -->

---

## Evidence

### FAIL_TO_PASS

| Test | Red Output (hash/snippet) | Green Output | File:Line |
|------|---------------------------|--------------|-----------|
| AC-1 | `AssertionError: expected false to be true` (`us-prev-red.txt`, `Tests  3 failed | 1 passed (4)`) | Row 6: `Tests  4 passed (4)` (`us-prev-green.txt`) | `ui/tests/unit/preview-script.test.ts:43` |
| AC-2 | `expected 'electron-vite preview' to be 'node ./scripts/electron-vite-preview.…` (`us-prev-red.txt`) | Row 6: `Tests  4 passed (4)` (`us-prev-green.txt`) | `ui/tests/unit/preview-script.test.ts:57` |
| The named pin (`PINS_NAMED`) | `expected 'electron-vite preview' to be 'node ./scripts/electron-vite-preview.…` (`us-prev-red.txt`) | Row 6: `Tests  4 passed (4)` (`us-prev-green.txt`) | `ui/tests/unit/dev-script.test.ts:64` (the test at `:41`) |

AC-3, AC-4 and AC-5 are checks (the proofs below).

- **Row 0 baseline** (`us-baseline.txt`): `baseline: all steps exit 0`, `eol-check: 31 scope path(s), 0 problem(s)`, `baseline-scope.json 58 paths; 7 absent`. UI Vitest at base: `Test Files  142 passed (142)`, `Tests  1619 passed (1619)` (`us-base-ui.txt`).
- **Row 5 Red** (`us-prev-red.txt`): `Test Files  2 failed (2)`, `Tests  3 failed | 1 passed (4)`; `red-check: 1 receipt(s), 2 required test(s), 0 problem(s)` (`us-prev-red-check.txt`); `pin-file lines changed since row 0: [64] named edit only: True CR in the new file: False` (`us-prev-red-hashes.txt`).
- **Row 5 base proofs, AC-3** (load 6.7 %). Set: `window: no (after 11 s; root exited)`, `notice: no`, `left: 0`, `FAIL: no window opened`, exit 1 (`us-prev-base-set.txt`). Unset: `window: yes (after 18 s; window)`, `left: 0`, `PASS: window opened, notice as expected, nothing left`, exit 0 (`us-prev-base-unset.txt`). `AC-3 base, set: exit 1 no window, nothing left: True ; unset: exit 0 window, nothing left: True` (`us-prev-base-check.txt`). So S8 did not fire: the base reproduced the defect and the proof can see a window.
- **Row 6 Green, AC-4 and AC-5** (load 4.4 %). `Test Files  2 passed (2)`, `Tests  4 passed (4)` (`us-prev-green.txt`). Preview set: `window: yes (after 20 s; window)`, `notice: yes`, `notice on stdout: no`, `left: 0`, `PASS: window opened, notice as expected, nothing left` (`us-prev-proof-set.txt`). Preview unset: `window: yes (after 19 s; window)`, `notice: no`, `PASS: window opened, notice as expected, nothing left` (`us-prev-proof-unset.txt`). Dev set: `window: yes (after 16 s; window)`, `notice: yes`, `PASS: window opened, notice as expected, nothing left` (`us-prev-proof-dev.txt`). `test-side files changed since Red: []` (`us-prev-immutable.txt`).
- **The gate's AC-4 run** (`us-D6-preview-proof.txt`; load 7.5 %): `window: yes (after 17 s; window)`, `notice: yes`, `notice on stdout: no`, `left: 0`, `PASS: window opened, notice as expected, nothing left`.
- **Row 8 records** (`us-issue-resolve.txt`): `decision logs read: 104 of 104`, `register sha256 before=01b1a5b0a6645256dbf2905c9136c8b8219332f761771f711cc992757cc15159`, `target sha256 after=0583a9c0d5837e6588d53a05595363154d880fcac1fb0db8d906a1cff056a251 CRLF=0 LF=5742`, `parsed fields changed: 15`, `issue-resolve: 0 problem(s)`; `Rendered known-issues.md: 36 lines` (`us-issues-render.txt`); the commands row updated (`us-row8-check.txt`).
- **H1-1** (`task-unchecked.txt`): `unchecked implementation rows: []`.

### Commands Executed

```json
{"schema_version": "evidence.v1", "cwd": "P:/av-kit", "check_id": "usprev-0-baseline", "command": "pwsh -NoProfile -File C:/Temp/av-kit/ui-small-fixes/run-row0.ps1 (task.md row 0's Validation cell without its uv sync step: baseline.ps1 records baseline.sha, the dirty list and hashes, the scope, line-ending and skip hashes, the cited anchors, the plan-local selftests and the base UI Vitest suite); receipts us-baseline.txt, us-base-ui.txt", "scope": "Row 0: the baseline at 9867e51 and the plan-local checkers", "phase": "static", "exit_code": 0, "result": "pass", "tested_state": "HEAD 9867e51 (baseline.sha) plus row 0", "output": "us-baseline.txt: baseline.sha 9867e51f0024a113de6a585b42b54695f1e4bccb; baseline-dirty.txt 17 paths, 5 foreign; baseline-scope.json 58 paths; 7 absent; baseline-skip-hashes.json 362 files under packages/, mcp-server/, tests/ and tools/; baseline-citations.txt 45 anchors; eol-check: 31 scope path(s), 0 problem(s); baseline: all steps exit 0. us-base-ui.txt: Test Files  142 passed (142); Tests  1619 passed (1619)."}
```

```json
{"schema_version": "evidence.v1", "cwd": "P:/av-kit", "check_id": "usprev-5-red", "command": "pwsh -NoProfile -File C:/Temp/av-kit/ui-small-fixes/run-row5.ps1 (task.md row 5's Validation cell: Vitest on preview-script.test.ts and dev-script.test.ts, red-check.py --require AC-1 and AC-2, the hash check, host-wait, then preview-proof.py --launch preview with ELECTRON_RUN_AS_NODE set and unset, the base check); receipts us-prev-red.txt, us-prev-red-check.txt, us-prev-red-hashes.txt, us-prev-base-set.txt, us-prev-base-unset.txt, us-prev-base-check.txt", "scope": "AC-1 and AC-2 Red with the named pin edited; AC-3, the defect reproduced at base", "phase": "red", "exit_code": 0, "result": "pass", "tested_state": "HEAD 9867e51 (baseline.sha) plus rows 0 to 5", "output": "us-prev-red.txt: Test Files  2 failed (2); Tests  3 failed | 1 passed (4); AC-1 AssertionError: expected false to be true; AC-2 and dev-script.test.ts:64 expected 'electron-vite preview' to be 'node ./scripts/electron-vite-preview.... us-prev-red-check.txt: red-check: 1 receipt(s), 2 required test(s), 0 problem(s). us-prev-red-hashes.txt: pin-file lines changed since row 0: [64] named edit only: True CR in the new file: False. Load 6.7 %. us-prev-base-set.txt: window: no (after 11 s; root exited), notice: no, left: 0, FAIL: no window opened (exit 1). us-prev-base-unset.txt: window: yes (after 18 s; window), left: 0, PASS: window opened, notice as expected, nothing left. us-prev-base-check.txt: AC-3 base, set: exit 1 no window, nothing left: True ; unset: exit 0 window, nothing left: True."}
```

```json
{"schema_version": "evidence.v1", "cwd": "P:/av-kit", "check_id": "usprev-6-green", "command": "pwsh -NoProfile -File C:/Temp/av-kit/ui-small-fixes/run-row6.ps1 (task.md row 6's Validation cell: Vitest on the two files, node --check, host-wait, preview-proof.py --launch preview set and unset and --launch dev set, the immutability check); receipts us-prev-green.txt, us-prev-proof-set.txt, us-prev-proof-unset.txt, us-prev-proof-dev.txt, us-prev-immutable.txt", "scope": "AC-1, AC-2, AC-4 and AC-5 after PREVIEW_WRAPPER", "phase": "green", "exit_code": 0, "result": "pass", "tested_state": "HEAD 9867e51 (baseline.sha) plus rows 0 to 6", "output": "us-prev-green.txt: Test Files  2 passed (2); Tests  4 passed (4). Load 4.4 %. us-prev-proof-set.txt: window: yes (after 20 s; window), notice: yes, notice on stdout: no, left: 0, PASS: window opened, notice as expected, nothing left. us-prev-proof-unset.txt: window: yes (after 19 s; window), notice: no, PASS: window opened, notice as expected, nothing left. us-prev-proof-dev.txt: window: yes (after 16 s; window), notice: yes, PASS: window opened, notice as expected, nothing left. us-prev-immutable.txt: test-side files changed since Red: []."}
```

```json
{"schema_version": "evidence.v1", "cwd": "P:/av-kit", "check_id": "usprev-8-records", "command": "python C:/Temp/av-kit/ui-small-fixes/write-set.py (issue-resolve-set.json, LF); python C:/Temp/av-kit/ui-small-fixes/row8-docs.py (the 06 and 11 Delivered notes and commands.md:80, CRLF kept, and grouping row 94, LF kept, by bytes); pwsh -NoProfile -File C:/Temp/av-kit/ui-small-fixes/run-row8.ps1 (task.md row 8's Validation cell: issue-resolve.py bound to the row-0 register hash, issue_triage.py render and render --check, meu_status.py update MEU-158 and MEU-159 ready_for_review --plan, the row 8 check)", "scope": "Row 8: the three issues resolved, MEU-158 and MEU-159 ready_for_review, the Delivered notes, COMMANDS_DOC and grouping row 94", "phase": "static", "exit_code": 0, "result": "pass", "tested_state": "HEAD 9867e51 (baseline.sha) plus rows 0 to 8", "output": "us-issue-resolve.txt: decision logs read: 104 of 104; register sha256 before=01b1a5b0a6645256dbf2905c9136c8b8219332f761771f711cc992757cc15159; target sha256 after=0583a9c0d5837e6588d53a05595363154d880fcac1fb0db8d906a1cff056a251 CRLF=0 LF=5742; parsed fields changed: 15; issue-resolve: 0 problem(s). us-issues-render.txt: Rendered known-issues.md: 36 lines. us-issues-render-check.txt: OK: known-issues.md is up-to-date. us-status-158.txt and us-status-159.txt: Updated to ready_for_review (updated: 2026-11-18). us-row8-check.txt: grouping LF: True; all three issues resolved."}
```

```json
{"schema_version": "evidence.v1", "cwd": "P:/av-kit", "check_id": "usprev-h1-2-session-gate", "command": "pwsh -NoProfile -File C:/Temp/av-kit/ui-small-fixes/run-rowH1-2.ps1 (task.md row H1-2's Validation cell: rtk proxy pwsh -NoProfile -File docs/execution/plans/2026-11-17-ui-small-fixes/session-gate.ps1 *> C:/Temp/av-kit/ui-small-fixes/us-gate-h1.txt); step receipts us-D6-<step>.txt and us-D6-<step>-load.txt", "scope": "H1-2: the PROFILE D6 session gate, 31 steps from identity-before to identity-after: static checks, the three targeted unit sets, host-load, the full UI Vitest suite, the preview proof, the UI build, eight Electron E2E steps (each after a host-wait at or below 50 %), the state and issue renders; py-tests, py-types, openapi, mcp-* and e2e-other skipped with their reasons", "phase": "full", "exit_code": 0, "result": "pass", "fresh": true, "snapshot": false, "tested_state": "9867e51f0024a113de6a585b42b54695f1e4bccb+0fb04e34a3879c5f491b2eb6fc42782c63314539f0e05a2bc03cb8494d11c42e", "output": "us-gate-h1.txt: every step exit=0; session-gate: all steps exit 0. identity before and after: tested_state 9867e51f0024a113de6a585b42b54695f1e4bccb+0fb04e34a3879c5f491b2eb6fc42782c63314539f0e05a2bc03cb8494d11c42e. host-load: ran at 9.3 %. us-D6-ui-tests.txt: Test Files  144 passed (144); Tests  1628 passed (1628). us-D6-preview-proof.txt: window: yes (after 17 s; window), notice: yes, notice on stdout: no, left: 0, PASS: window opened, notice as expected, nothing left. E2E: e2e-help-f1-mount 5 passed (25.4s); e2e-browse-mount 4 passed (28.1s); e2e-ctrl-o 1 passed (1.1s); e2e-help-search 3 passed (2.1s); e2e-keyboard-shortcuts 2 passed (1.9s); e2e-advanced-gap 4 passed (12.7s); e2e-download-queue 26 passed (26.4s); e2e-layout-primitives 1 passed (982ms). OK: 29 row(s); changed paths: 46 outside scope: [] other sessions plan files skipped: 4; eol-check: 31 scope path(s), 0 problem(s); check_home_path: ok files=2671 allowlisted=60 nul=31; OK: known-issues.md is up-to-date."}
```

```json
{"schema_version": "evidence.v1", "cwd": "P:/av-kit", "check_id": "usprev-h1-3-h1-4-closeout-checks", "command": "python C:/Temp/av-kit/ui-small-fixes/focus-entry.py (the Session 94 entry on top of .agent/context/current-focus.md, by bytes, CRLF kept); pwsh -NoProfile -File C:/Temp/av-kit/ui-small-fixes/run-rowH1-3.ps1 (meu_status.py render --check, meu_status.py get MEU-158 and MEU-159, the ready check); pwsh -NoProfile -File C:/Temp/av-kit/ui-small-fixes/run-rowH1-4.ps1 (task.md row H1-4's skip-basis check)", "scope": "H1-3 (current focus, the state render, MEU-158 and MEU-159 ready_for_review) and H1-4 (the Python, OpenAPI and MCP skip basis)", "phase": "static", "exit_code": 0, "result": "pass", "tested_state": "the H1-2 state plus H1-3's current-focus entry (identity.py excludes current-focus.md)", "output": "focus-entry: current-focus: bytes 89795 -> 91475 CRLF 221 -> 224 bare LF 0. us-render-check.txt: Drift check passed. us-h13-check.txt: ready_for_review: {'MEU-158': True, 'MEU-159': True}. skip-basis-check.txt: packages, mcp-server, tests or tools changes since row 0: []."}
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
| Preview in the gate | `preview-proof` `PASS: window opened, notice as expected, nothing left`; `preview-unit` `Tests  4 passed (4)`; `scripts-syntax` `node --check ui/scripts/electron-vite-preview.mjs exit 0` |

---

## Changed Files

Counts are added / removed lines against `HEAD` `9867e51` (`git diff --numstat --ignore-cr-at-eol`); a new file's count is its line count. Line endings were measured as bytes (the gate's `line-endings` step: `eol-check: 31 scope path(s), 0 problem(s)`). The whole session's change set is listed in each handoff; the rows that are the preview fix's are the two scripts, `ui/package.json`, `dev-script.test.ts`, `preview-script.test.ts` and `commands.md`.

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

**`PINS_NAMED`.** The one changed expectation, `ui/tests/unit/dev-script.test.ts:64`, in the test at `:41` (cross-ref row above); `:63`, the dev script's, is unchanged:

| Line | Old | New |
|------|-----|-----|
| `:64` | `    expect(pkg.scripts.preview).toBe('electron-vite preview')` | `    expect(pkg.scripts.preview).toBe('node ./scripts/electron-vite-preview.mjs')` |

**`ui/package.json:18`** (CRLF kept): old `    "preview": "electron-vite preview",`; new `    "preview": "node ./scripts/electron-vite-preview.mjs",`.

**`PREVIEW_WRAPPER`.** `ui/scripts/electron-vite-dev.mjs` (LF):

```diff
+const electronViteBin = resolve(ui, 'node_modules/electron-vite/bin/electron-vite.js')
-  return [resolve(ui, 'node_modules/electron-vite/bin/electron-vite.js'), 'dev', ...extra]
+  return [electronViteBin, 'dev', ...extra]
-function main() {
+export function runElectronVite(command, notice, extra) {
-  if (cleared) process.stderr.write(DEV_NOTICE + '\n')
-  const child = spawn(process.execPath, devArgs(process.argv.slice(2)), { stdio: 'inherit', env, cwd: ui })
+  if (cleared) process.stderr.write(notice + '\n')
+  const child = spawn(process.execPath, [electronViteBin, command, ...extra], { stdio: 'inherit', env, cwd: ui })
-    process.stderr.write('electron-vite-dev: could not start electron-vite: ' + String(error) + '\n')
+    process.stderr.write('electron-vite-' + command + ': could not start electron-vite: ' + String(error) + '\n')
+function main() {
+  runElectronVite('dev', DEV_NOTICE, process.argv.slice(2))
+}
```

The new `ui/scripts/electron-vite-preview.mjs` (20 lines, LF) exports `PREVIEW_NOTICE` and `previewArgs(extra)`, imports `isEntry` and `runElectronVite` from `./electron-vite-dev.mjs`, and ends `if (isEntry(process.argv[1], import.meta.url)) runElectronVite('preview', PREVIEW_NOTICE, process.argv.slice(2))`.

**`COMMANDS_DOC`.** `.agent/docs/commands.md:80` (CRLF kept): the preview row's "**Silent**, as `dev` was. Tracked as `UI-PREVIEW-ELECTRON-RUN-AS-NODE-SILENT`." becomes "Clears it itself since Session 94: `ui/scripts/electron-vite-preview.mjs` removes the variable, prints `electron-vite-preview: cleared ELECTRON_RUN_AS_NODE` and starts `electron-vite preview`, so the window opens.", in the dev row's form.

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
  - Accepted PREVIEW_WRAPPER, COMMANDS_DOC, PINS_NAMED and SERVICES_KEPT. (§Q4)
  - Its own fake-spawn probe (no real child) exercised set/unset modes, argument values including a space, cwd, inherited stdio, parent preservation, notice presence/absence, SIGTERM, exit 7 and spawn-error exit 1. (§Q4)
  - Omitting the unused `devEnv` import from the preview module preserves behavior because the shared runner calls it. (§Q4; the departure above)
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
| A new MEU for the preview script | out-of-scope | — | D-1130: test and tooling debt with no MEU |
| Commit and push | out-of-scope | — | Only on Mat's direction (H2-5) |
| The Codex execution review | next step | H1-7 | Not part of this run; the coordinator dispatches it |

### Departures and their basis

- **Queue order.** Under D-1142 the queue is 74, 92, 93, 94, then 91, so Session 94 ran fourth, after 74 (`cba97fe`), 92 (`8280586`) and 93 (`9867e51`), and Session 91 `e2e-pointer-flakes` runs after it. The plan's Status line still gives D-1133's order (74, 91, 92, 93, 94) and says Session 94 runs last. Session 91 has not run, so the plan's §Sibling overlap rows for Session 91 (`electron-app.ts`, `electron-env.ts`, the shared E2E helpers and a renderer race fix) are vacuous: row 0 found those files at `HEAD` and the new specs copy their `HEAD` form. Session 91's plan folder and its plan-review handoff were never opened or touched, and are left out of every scope check (`other sessions plan files skipped: 4`, `us-D6-scope-paths.txt`).
- **Plan and task hashes.** The reviewed plan's sha256 is `a91c81f8f652b2436a2c04f2b1a9ebeba50a4fbd801916840994051b3a29a89c` (the coordinator's approval, the plan's Status line); the plan-review handoff cites `ecfd0ac6…`, the plan before the coordinator wrote that Status line. D-1181 (below) then added one decision to the plan's YAML, so its sha256 is now `1bd49ed579781cd13bbc3f312084e3f6d0b9005a85cc71d4e0f344c96df49b57`. `task.md`'s reviewed sha256 is `07a356d2d2cbc0c57ad74f2d1ec6b2c8c9c2ecf705c0ef3cfed13d20feaf8e94`; since then it changed only by its row marks.
- **D-1181 (execution decision, in the plan's YAML; `resolution: autonomous`, two-way).** The plan says the gate's host-load step never fails the gate, but S11 forbids an Electron step above 50 % and the plan's own `host-wait.py` exits 1 when the load is still above the limit after 10 minutes. Chosen (A, the HDP recommendation, decided under the hand-over: USER_EXPLICIT 2026-11-17, continuing USER_EXPLICIT 2026-11-15 and USER_EXPLICIT 2026-11-18 "make the decisions always the recommenations"): `session-gate.ps1` runs `host-wait.py` as its own `host-load` step and again before each of its nine Electron steps (the preview proof and the eight E2E steps), each into its own `us-D6-<step>-load.txt`; a load still above 50 % after the wait fails that step. Every wait passed at once (7.3 % to 9.3 %), so the gate ran as the plan's table says. The options not taken: B, ignoring the exit code, would run Electron above the limit; C, one host-load step only, would leave the later Electron steps unchecked. No M hit. D-1182 to D-1184 and D-1190 to D-1192 are unused.
- **How the rows ran.** Each row's Validation cell was extracted to a `.ps1` file (an environment header setting the working directory, `PYTHONIOENCODING`, `PYTHONDONTWRITEBYTECODE`, `RECEIPTS_DIR`, `TMP` and `TEMP`, then the cell) and run with `pwsh -NoProfile -File`. The one change to a cell's text: `uv run python` became `uv run --no-sync python` (no network; the brief's rule), and row 0's `uv sync` step was dropped for the same reason; the lock hashes in `us-D6-identity-before.txt` are the row-0 ones. The extraction regex was widened once, to read cells that begin with `$` as well as `rtk proxy`. The hand edits were made by scripts that wrote bytes and asserted each anchor occurred once. Before each Electron step a host wait ran with the brief's 50 % limit (the plan's `load-run.py` copy already uses 50 %, not Session 90's 60 %); every one read under 26 %. Each Electron run used a scratch `AVKIT_APP_DATA` and cleared `ELECTRON_RUN_AS_NODE`, except where `preview-proof.py` sets it for its own child.
- **Row 0's dirty list.** `baseline-dirty.txt` records 17 dirty paths at row 0, 5 of them foreign; the foreign ones carry a `#` note naming their owner, and their hashes held to the gate (`baseline-dirty hash mismatch: []`, `us-D6-scope-paths.txt`).
- **The preview script's imports.** The plan's `PREVIEW_WRAPPER` says the preview script imports `devEnv`, `isEntry` and `runElectronVite`. It imports `isEntry` and `runElectronVite` only: `runElectronVite` calls `devEnv` itself, so the preview module has no use for it, and an unused import fails `ui-lint` (`--max-warnings 0`). The behaviour is the plan's, and AC-1 and the three proofs pass.
- **The gate's own reads.** `session-gate.ps1` reads each step's exit from `$LASTEXITCODE` and its own receipt, never a `.exit` side file, and checks each E2E receipt for its passed line, any failed or flaky line and any `unhandled rejection:` line (`rejection-record lines=0` for every step, `us-gate-h1.txt`).
- **Processes.** Each proof and E2E run stopped only the processes it launched, by recorded id and creation time (`left: 0` in every preview proof). No other session's app, the IDE's avkit MCP server, ShareX or Mat's app was stopped. The clipboard specs, `capture-filmstrip-actions.test.ts` and `capture-import.test.ts` never ran.

### Execution notes

- **The decisions.** D-1130: the preview fix has no MEU and follows the dev contract. D-1178: one shared `runElectronVite`, one named pin and the commands row. D-1181: the gate's load waits (Departures).
- **No stop fired.** AC-3's base proof reproduced the defect (S8 not hit); no existing test other than the named pin changed or failed.

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
