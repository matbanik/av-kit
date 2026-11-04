---
date: "2026-11-04"
project: "release-rc1"
meu: "MEU-108"
status: "complete"
action_required: "VALIDATE_AND_APPROVE"
template_version: "2.2"
verbosity: "standard"
plan_source: "docs/execution/plans/2026-11-03-release-rc1/implementation-plan.md"
build_plan_section: "bp06"
agent: "claude-code-local (Claude Opus 5.5)"
reviewer: "codex (H1-7 execution review)"
predecessor: "none"
---

# Handoff: 2026-11-03-release-rc1-MEU-108-handoff

> **Status**: `complete`
> **Action Required**: `VALIDATE_AND_APPROVE`

---

## Scope

**MEU**: MEU-108, `gui-ready-probe-guard`. The backend's output handler runs its process query only for a chunk that carries a usable `AVKIT_READY` line, and backend output after the window has gone no longer stops the main process (ECN-9).
**Build Plan Section**: [06 §Ready probe (residual)](../../../docs/build-plan/06-gui.md#ready-probe-residual).
**Predecessor**: none. The [MEU-109 handoff](2026-11-03-release-rc1-MEU-109-handoff.md), the [MEU-110 handoff](2026-11-03-release-rc1-MEU-110-handoff.md), the [MEU-111 handoff](2026-11-03-release-rc1-MEU-111-handoff.md) and the [MEU-112 handoff](2026-11-03-release-rc1-MEU-112-handoff.md) are the same plan's other MEUs.

Before this MEU, `onChildOutput` in `ui/src/main/index.ts` called `queryLiveProcess` for every chunk of backend output, before looking at the text. That query runs PowerShell synchronously on Windows, so a chatty backend blocked Electron's main process (`GUI-READY-PROBE-BLOCKS-MAIN`).

- **`READY_GUARD`.** New exported `publishIfReady` in `ui/src/main/python-manager.ts` takes the chunk and an injected `queryLive`, and returns `false` without querying unless the chunk holds a usable READY line. `usableReadyPort` and the one shared regex `AVKIT_READY_LINE` serve both the guard and `confirmReadyAndPublish`, so the two can't disagree.
- **Beyond the plan's letter.** `index.ts` now passes `readDescriptorPid` as a callback too, so the descriptor read sits behind the same guard and doesn't run for every chunk.
- **Fix generalization.** Checked 2 locations in `ui/src/main/index.ts` (every `queryLiveProcess` use). Fixed 1 instance (`:283`). Skipped 1 (`:251`, `resolveBootIdentity`: it runs once before the spawn, not on backend output, so 06's guard doesn't cover it). Verified 0 remaining unaddressed instances.
- **`LOG_AFTER_WINDOW` (ECN-9, D-209).** During H1-2 attempt 4, Mat dismissed four dialogs reading `TypeError: Object has been destroyed` at `Socket.onChildOutput`. The handler sent each line with `mainWindow?.webContents.send`. `mainWindow` is never cleared, so `?.` doesn't protect a destroyed window, and reading `webContents` from one throws. That code was in the initial commit. `forwardConsoleLines` (`python-manager.ts:133`) is now the handler's only route to the window (`index.ts:274`, `:290`). It sends nothing to a destroyed window and catches a send that throws, and the line stays in the in-memory log either way.
- **Attempt 4's two failures.** AC-66.14 hit the 60 s test timeout with no failed assertion and no pending locator, which fits `app.close()` waiting on that dialog. After the fix it passed 8 of 8 repeats in about 2 s each, which fits that explanation and doesn't prove it. AC-88.12 failed at its clipboard primer, whose read stayed empty for 5 s. It was the run's first test, before any app had closed, so the dialog doesn't explain it. It passed 8 of 8 repeats, and the cause isn't established (`E2E-CLIPBOARD-PRIMER-EMPTY`).
- **Second fix generalization (ECN-9).** Checked 6 places in `ui/src/main` that touch a window after creating it. Fixed 2 (`index.ts:274`, `:290`). Skipped 1 under D-209 (`capture-tray.ts:18`, the tray's Show window item, which only a menu click during shutdown reaches). The other 3 were already safe: `capture-inbox-watch.ts:170` checks `isDestroyed`, `index.ts:491` runs inside the window's own `close` event, and `startup-mode.ts:24` runs when the window finishes loading. Verified 0 remaining unaddressed instances.
- **What these checks don't prove.** Nobody drove an installed copy through this. An installed copy reaching it with Close to tray off is read from the code, not reproduced by hand. The unit and real-Electron cases push a line through the handler directly. No receipt records the dialog, so how many earlier gate runs showed it isn't known. The E2E suite still doesn't watch for main-process exceptions (`E2E-MAIN-PROCESS-ERRORS-UNWATCHED`).

**Plan:** [implementation-plan.md](../../../docs/execution/plans/2026-11-03-release-rc1/implementation-plan.md) §MEU-108. **Execution authorization:** `USER_EXPLICIT`, 2026-11-03, "create MIT license file / prepare whatever we need to build and publish the release rc1 candidate", and 2026-11-04, "approve tripple of the token budget and add MEU-111". Plan review approved at round 3. Mat's 2026-11-04 rulings (ECN-6) didn't change this MEU's code. Mat's report during H1-2 attempt 4 did (ECN-9).

---

## Acceptance Criteria

| AC | Type | Description | Source | Test(s) | Status |
|----|------|-------------|--------|---------|--------|
| AC-108.1 | unit | A chunk with no `AVKIT_READY` line calls `queryLive` zero times and publishes nothing. | Spec (06 §Ready probe) | `ui/tests/unit/ready-probe-guard.test.ts:32` | ✅ |
| AC-108.2 | unit | `AVKIT_READY port=0` calls `queryLive` zero times and publishes nothing. | Spec; existing `port=0` rule `python-manager.ts:98` | `ui/tests/unit/ready-probe-guard.test.ts:43` | ✅ |
| AC-108.3 | unit | A usable READY chunk calls `queryLive` once and publishes the same `apiBase` and token as `confirmReadyAndPublish`. | Local Canon 07 §PythonManager step 3 | `ui/tests/unit/ready-probe-guard.test.ts:50` | ✅ |
| AC-108.4 | unit | `index.ts` no longer calls `queryLiveProcess` outside `publishIfReady`'s injected callback in the output handler. | Spec; source-text test | `ui/tests/unit/ready-probe-guard.test.ts:72` | ✅ |
| AC-108.5 | unit | A backend line that arrives after the window is destroyed, or after its renderer is torn down, throws nothing in the main process. | Mat's report during H1-2 attempt 4 (ECN-9) | `ui/tests/unit/ready-probe-guard.test.ts:102`, `:113` | ✅ |
| AC-108.6 | unit | A live window still gets each line on `console-log-batch`, no window yet sends nothing, and the output handler reaches the window only through `forwardConsoleLines`. | Spec; source-text test | `ui/tests/unit/ready-probe-guard.test.ts:126`, `:133`, `:137` | ✅ |
| AC-108.7 | e2e | In real Electron with the window destroyed, a line through the real `onChildOutput` handler throws nothing. | Mat's report during H1-2 attempt 4 (ECN-9) | `ui/tests/e2e/backend-output-after-close.test.ts:9` (gate `ui-electron`) | ✅ |
| AC-109 (cross-ref) | — | Owned by the MEU-109 handoff (the output folder before FFmpeg starts) | plan §MEU-109 | [MEU-109 handoff](2026-11-03-release-rc1-MEU-109-handoff.md) | see MEU-109 |
| AC-110 (cross-ref) | — | Owned by the MEU-110 handoff (licence, version, build, packaged checks and release materials) | plan §MEU-110 | [MEU-110 handoff](2026-11-03-release-rc1-MEU-110-handoff.md) | see MEU-110 |
| AC-111 (cross-ref) | — | Owned by the MEU-111 handoff (the MCP image cap and the audit's two image steps) | plan §MEU-111 | [MEU-111 handoff](2026-11-03-release-rc1-MEU-111-handoff.md) | see MEU-111 |
| AC-112 (cross-ref) | — | Owned by the MEU-112 handoff (the encoder chosen for one job) | plan §MEU-112 | [MEU-112 handoff](2026-11-03-release-rc1-MEU-112-handoff.md) | see MEU-112 |
| AC-24 (cross-ref) | regression | AC-24.10: the packaged backend folder holds its exe and support tree. It passed at row 0, not failed as the plan predicted, because this tree holds the gitignored outputs; it fails only in a clean clone, and CI deselects it (plan ECN-2) | plan ECN-2 | `tests/unit/test_packaging_backend.py:212` (gate `py-tests`) | ✅ |
| AC-25 (cross-ref) | regression | AC-25.7: the MCP snippet names the app-data folder, with no token or API base, fixed in `0eb59ab` before this baseline. AC-25.10: the NSIS check script exists and fails closed; same clean-clone note as AC-24.10 | plan ECN-2 | `tests/unit/test_packaging_installer.py:64`, `:94` (gate `py-tests`) | ✅ |
| AC-68 (cross-ref) | regression | AC-68.2: the audit runner imports nothing from the server's tree. H1-2 attempt 1 failed this test on row 5b's import; the [MEU-111 handoff](2026-11-03-release-rc1-MEU-111-handoff.md) holds the correction (D-189, ECN-3). The forbidden-pattern list is unchanged | plan ECN-3 | `mcp-server/tests/audit/run-cli.test.ts` (gate `mcp-tests`) | ✅ |
| AC-71 (cross-ref) | regression | AC-71.10: Electron with `ELECTRON_RUN_AS_NODE` on the dev server entry answers `initialize` as av-kit, and the fuse pin holds in `electron-builder.yml`, which row 7 edited | plan §Verification 1 | `ui/tests/unit/mcp-spawn-electron.test.ts:76` (gate `ui-tests`) | ✅ |
| AC-72 (cross-ref) | regression | AC-72.7: `THIRD_PARTY_NOTICES.md` stays hand-curated with its LGPL appendix and FFmpeg source section; it gains one pointer line to the generated list, and its `## FFmpeg` section names the re-pinned build | plan §MEU-110 | `tests/unit/test_packaging_installer.py:207` (gate `py-tests`) | ✅ |
| AC-92 (cross-ref) | regression | AC-92.4: the MCP entry runs through the app's own exe with `ELECTRON_RUN_AS_NODE`. It is the Local Canon behind AC-110.13, which row 11 proved on the RC build | plan AC-110.13 | row 11 MCP probe, in the [MEU-110 handoff](2026-11-03-release-rc1-MEU-110-handoff.md) | ✅ |

<!-- CACHE BOUNDARY -->

---

## Evidence

### FAIL_TO_PASS

| Test | Red Output (hash/snippet) | Green Output | File:Line |
|------|---------------------------|--------------|-----------|
| AC-108.1 | `expected "vi.fn()" to be called +0 times, but got 3 times` | pass | `ready-probe-guard.test.ts:32` |
| AC-108.2 | `expected "vi.fn()" to be called +0 times, but got 1 times` | pass | `ready-probe-guard.test.ts:43` |
| AC-108.4 | `expected "vi.fn()" to be called 1 times, but got 101 times` | pass | `ready-probe-guard.test.ts:72` |
| AC-108.5 destroyed window | `AssertionError: expected 'TypeError: Object has been destroyed' to be null` | pass | `ready-probe-guard.test.ts:102` |
| AC-108.5 renderer torn down | `AssertionError: expected 'TypeError: Object has been destroyed' to be null` | pass | `ready-probe-guard.test.ts:113` |
| AC-108.7 real Electron | `thrown` held `TypeError: Object has been destroyed` twice, once for each stream with the handler | pass | `backend-output-after-close.test.ts:9` |

AC-108.3 isn't required Red: the publish it pins holds before and after the guard. `red-check.py` confirmed the required failures are assertions (`red-check: 1 receipt(s), 2 required test(s), 0 problem(s)`; AC-108.4 failed Red as well, on its 101 queries). AC-108.6 wasn't in row 9j's Red filter: it pins behaviour the fix keeps.

Receipts: Red `C:/Temp/av-kit/s44-108-red.txt`; Green `C:/Temp/av-kit/s44-108-green.txt`; `C:/Temp/av-kit/rc1/rows/row3-typecheck.txt` and `row3-lint.txt`. ECN-9: Red `C:/Temp/av-kit/rc1/s44-108-5-red-kept.txt`, `s44-108-7-red-kept.txt`, `C:/Temp/av-kit/s44-108-5-red-check.txt`; Green `C:/Temp/av-kit/s44-108-5-green-ui.txt`, `s44-108-7-green.txt`; repeats `C:/Temp/av-kit/rc1/ecn9/repeat-1.txt`; attempt 4 `C:/Temp/av-kit/rc1/attempt-4/`.

### Commands Executed

```json
{"schema_version": "evidence.v1", "check_id": "s44-108-red", "command": "pwsh -NoProfile -File row-2.ps1 (task.md row 2 Validation cell, verbatim, from P:/av-kit)", "cwd": "P:/av-kit", "scope": "MEU-108 Red: publishIfReady moved out with today's query-first behaviour, then ready-probe-guard.test.ts and red-check.py", "phase": "red", "exit_code": 0, "result": "pass", "tested_state": "HEAD 24e2735 (baseline.sha) plus row 1 and row 2's behaviour-preserving move", "output": "Tests 3 failed | 1 passed. AC-108.1 expected \"vi.fn()\" to be called +0 times, but got 3 times. AC-108.2 expected \"vi.fn()\" to be called +0 times, but got 1 times. AC-108.4 expected \"vi.fn()\" to be called 1 times, but got 101 times. red-check: 1 receipt(s), 2 required test(s), 0 problem(s). The row exits 0 because red-check confirms decisive failures."}
```

```json
{"schema_version": "evidence.v1", "check_id": "s44-108-green", "command": "pwsh -NoProfile -File row-3.ps1 (task.md row 3 Validation cell, verbatim, from P:/av-kit)", "cwd": "P:/av-kit", "scope": "MEU-108 Green: the guard, with the guard test and the suites around the publish path, typecheck and lint", "phase": "green", "exit_code": 0, "result": "pass", "tested_state": "HEAD 24e2735 plus rows 1 to 3", "output": "Test Files 2 passed (2), Tests 7 passed (7). Typecheck and lint exit 0. Expectations unchanged from Red."}
```

```json
{"schema_version": "evidence.v1", "check_id": "s44-108-5-red", "command": "pwsh -NoProfile -File row-9j.ps1 (task.md row 9j Validation cell, verbatim, from P:/av-kit)", "cwd": "P:/av-kit", "scope": "AC-108.5 and AC-108.7 Red: forwardConsoleLines moved out with today's behaviour, the unit cases, the real-Electron case and red-check.py", "phase": "red", "exit_code": 0, "result": "pass", "tested_state": "HEAD 24e2735 plus rows 1 to 9i and row 9j's behaviour-preserving move", "output": "Unit: Tests 2 failed | 7 skipped (9), both AssertionError: expected 'TypeError: Object has been destroyed' to be null. Real Electron: 1 failed, with thrown holding TypeError: Object has been destroyed twice. red-check: 2 receipt(s), 2 required test(s), 0 problem(s). The row exits 0 because red-check confirms decisive failures."}
```

```json
{"schema_version": "evidence.v1", "check_id": "s44-108-5-green", "command": "pwsh -NoProfile -File row-9k.ps1 (task.md row 9k Validation cell, verbatim, from P:/av-kit)", "cwd": "P:/av-kit", "scope": "AC-108.5 to AC-108.7 Green per D-209: the whole UI suite (RULE-1), then the real-Electron case on a fresh build", "phase": "green", "exit_code": 0, "result": "pass", "tested_state": "HEAD 24e2735 plus rows 1 to 9k", "output": "Test Files 108 passed (108). Tests 1129 passed (1129). AC-108.7 in real Electron: 1 passed."}
```

```json
{"schema_version": "evidence.v1", "check_id": "s44-108-attempt4-repeats", "command": "rtk proxy npm --prefix ui run test:e2e -- tests/e2e/capture-filmstrip-actions.test.ts tests/e2e/capture-inbox.test.ts -g 'AC-88.12 \\(a\\)\\(b\\)\\(f\\)|AC-66.14' --repeat-each=8 > C:/Temp/av-kit/rc1/ecn9/repeat-1.txt 2>&1", "cwd": "P:/av-kit", "scope": "The two tests that failed in H1-2 attempt 4, 8 repeats each, after the fix", "phase": "targeted", "exit_code": 0, "result": "pass", "tested_state": "HEAD 24e2735 plus rows 1 to 9k", "output": "16 passed (40.7s). AC-88.12 (a)(b)(f) 8 of 8, about 2.6 s each. AC-66.14 8 of 8, about 2 s each."}
```

```json
{"schema_version": "evidence.v1", "check_id": "s44-gate-h1-2-attempt1", "command": "$env:TMP='C:\\Temp\\av-kit\\rc1\\tmp'; $env:TEMP='C:\\Temp\\av-kit\\rc1\\tmp'; $env:ELECTRON_RUN_AS_NODE=$null; rtk proxy pwsh -NoProfile -File docs/execution/plans/2026-11-03-release-rc1/session-gate.ps1 *> C:/Temp/av-kit/s44-gate-h1.txt; $code=$LASTEXITCODE; Select-String -Path C:/Temp/av-kit/s44-gate-h1.txt -Pattern ' exit=','not_run','tested_state','_sha256 ','outside scope','PRODUCT_SCOPE','build_inputs','mismatch','audit rule','session-gate:'; exit $code", "cwd": "P:/av-kit", "scope": "H1-2 attempt 1, the registered D6 gate, on the tree before the ECN-3 correction", "phase": "full", "exit_code": 1, "result": "fail", "tested_state": "24e27354e35eccc0cfa7d7e76357e673a6e38c23+ab9c5df667b9ca5ae9139129a9e0075c6b774bf96f173e13d8d9fae746342ea2", "output": "mcp-tests exit=1: 1 failed, 464 passed, tests/audit/run-cli.test.ts AC-68.2, the runner tree contains none of the forbidden imports, hit mcp-server/scripts/audit/plan.ts: src/toolsets. Every earlier step exit 0, including py-tests 1100 passed. ui-build through identity-after not_run (fail-fast).", "fresh": false}
```

```json
{"schema_version": "evidence.v1", "check_id": "s44-gate-h1-2", "command": "$env:TMP='C:\\Temp\\av-kit\\rc1\\tmp'; $env:TEMP='C:\\Temp\\av-kit\\rc1\\tmp'; $env:ELECTRON_RUN_AS_NODE=$null; rtk proxy pwsh -NoProfile -File docs/execution/plans/2026-11-03-release-rc1/session-gate.ps1 *> C:/Temp/av-kit/s44-gate-h1.txt; $code=$LASTEXITCODE; Select-String -Path C:/Temp/av-kit/s44-gate-h1.txt -Pattern ' exit=','not_run','tested_state','_sha256 ','outside scope','PRODUCT_SCOPE','build_inputs','mismatch','audit rule','session-gate:'; exit $code", "cwd": "P:/av-kit", "scope": "H1-2 attempt 6, the registered D6 gate, whole tree after ECN-6, ECN-7, ECN-8, ECN-9, ECN-10 and the rebuild", "phase": "full", "exit_code": 0, "result": "pass", "tested_state": "24e27354e35eccc0cfa7d7e76357e673a6e38c23+025862f4f8e1a5c5b6d9023835d17014eabdac94e0785551cb7cc778a4bbd382", "output": "Every step exit 0 except mcp-audit exit 1, which audit-rule.py tolerated (rule exit 0). py-tests 1186 passed in 123.98s (0:02:03). ui-tests 108 files, 1138 passed. mcp-tests 34 files, 466 passed. ui-electron 182 passed (3.7m). mcp-audit authoritative: 98/99 pass, 0 discovery finding(s), cleanup ok, exit 1; the one failure is transcript.compile: no transcript fetched (transcripts_done 0, last_item_status Pending); live-rigging-snow_vol1.md 37 B. build_inputs 08ade695aadca286cd671168389227671ec1b163d81132344d38269ab2cde573, build record matches. task-contract 45 row(s). changed paths: 93 outside scope: [] head: 24e27354e35eccc0cfa7d7e76357e673a6e38c23 head moved (S4): False. baseline excused py [] ui []. tested_state before and after equal. session-gate: INCOMPLETE VERIFICATION: every other step exits 0, but the authoritative audit stays non-pass. Transcript is not verified end to end while YouTube blocks captions (YOUTUBE-CAPTIONS-IP-BLOCK).", "fresh": true}
```

```json
{"schema_version": "evidence.v1", "check_id": "s44-h1-3-render", "command": "rtk proxy uv run python tools/meu_status.py render --check *> C:/Temp/av-kit/drift-check.txt", "cwd": "P:/av-kit", "scope": "H1-3: rendered state regions against meu-status.yaml, after the current focus and the audit report were updated", "phase": "static", "exit_code": 0, "result": "pass", "tested_state": "24e27354e35eccc0cfa7d7e76357e673a6e38c23+025862f4f8e1a5c5b6d9023835d17014eabdac94e0785551cb7cc778a4bbd382", "output": "Drift check passed — SSOT loaded (112 MEUs, 12 phases), rendered regions match on-disk content The copied audit report holds no gmail-form address."}
```

```json
{"schema_version": "evidence.v1", "check_id": "s44-h1-4-openapi", "command": "rtk proxy uv run python -c '<task.md row H1-4 compare of baseline.sha and the working file>' *> C:/Temp/av-kit/openapi-check.txt", "cwd": "P:/av-kit", "scope": "H1-4: the committed OpenAPI file against baseline.sha", "phase": "static", "exit_code": 0, "result": "pass", "tested_state": "24e27354e35eccc0cfa7d7e76357e673a6e38c23+025862f4f8e1a5c5b6d9023835d17014eabdac94e0785551cb7cc778a4bbd382", "output": "info.version: 0.1.0 -> 0.1.0rc1 components and paths unchanged: True The gate's openapi step exit 0."}
```

### Quality Gate Results

`s44-gate-h1-2` is the fresh full record, and it isn't a clean pass. Its last line is:

> session-gate: INCOMPLETE VERIFICATION: every other step exits 0, but the authoritative audit stays non-pass. Transcript is not verified end to end while YouTube blocks captions (YOUTUBE-CAPTIONS-IP-BLOCK).

The gate exits 0 because D-186 tolerates exactly one state: `transcript.compile` is the only failure, it wrote a real output file, and a direct caption fetch from this machine is blocked right now. `audit-rule.py` checked all three (rule exit 0). The audit's own verdict stays non-pass (`mcp-audit authoritative: 98/99 pass, 0 discovery finding(s), cleanup ok, exit 1`), the audit report says so, and the baseline wasn't refreshed. Transcript isn't verified end to end from this machine. That run doesn't check the content of compiled output either (plan F7).

- **Static:** `py-types`, `py-lint`, `ui-types`, `ui-lint`, `mcp-types`, `task-contract` (45 row(s)), `scope-paths` (93 changed paths, none outside scope, head not moved), `build-identity-selftest`, `audit-rule-selftest`, `audit-clear-selftest`: all exit 0.
- **Suites:** `py-tests` 1186 passed in 123.98s (0:02:03); `ui-tests` 108 files, 1138 passed; `mcp-tests` 34 files, 466 passed. Baseline failures excused: none.
- **Builds and state:** `mcp-build`, `ui-build`, `ui-harness-build`, `ui-picker-stub`, `openapi`, `state-render`, `build-record` (`build_inputs 08ade695aadca286cd671168389227671ec1b163d81132344d38269ab2cde573`): all exit 0.
- **Runtime:** `ui-electron` 182 passed (3.7m); `mcp-audit-clear` exit 0; `mcp-audit` 98 of 99, 0 discovery findings, cleanup ok.
- **Identity:** `tested_state` `24e27354e35eccc0cfa7d7e76357e673a6e38c23+025862f4f8e1a5c5b6d9023835d17014eabdac94e0785551cb7cc778a4bbd382`, the same before and after. Row H1-2 set `TMP` and `TEMP` under ECN-2 (D-190).
- **Attempts:** attempt 1 (`s44-gate-h1-2-attempt1`, state `…+ab9c5df6…`) failed `mcp-tests` on AC-68.2, a defect in row 5b, with 1 failed and 464 passed. Later steps didn't run. Its receipts are archived. Attempt 2 (state `…+7eba916b…`) passed on the build from before Mat's rulings (`py-tests` 1100 passed, `ui-tests` 1111 passed, `mcp-tests` 466 passed, `ui-electron` 181 passed), and ECN-6 superseded it. Attempt 3 (state `…+f52fc9d6…`) passed on the build from before round 2's findings (`py-tests` 1186 passed, `ui-tests` 1115 passed, `mcp-tests` 466 passed, `ui-electron` 181 passed), and ECN-8 superseded it. Neither has a record here, because `durable_evidence.py --require-full` accepts a passing full record only for the state under review. Attempt 4 failed `ui-electron` with 2 failed and 179 passed, AC-88.12's clipboard primer and AC-66.14's test timeout, while Mat dismissed the main-process error dialogs that ECN-9 fixes. Later steps didn't run. Its receipts are in `C:/Temp/av-kit/rc1/attempt-4/`. Attempt 5 (state `…+08022c05…`) passed on the build from before round 3's finding (`py-tests` 1186 passed, `ui-tests` 1129 passed, `mcp-tests` 466 passed, `ui-electron` 182 passed), and ECN-10 superseded it, so it has no record here for the same reason. Its receipts are in `C:/Temp/av-kit/rc1/attempt-5/`. Attempt 6 is this run, after the fix for round 3's finding and rows 10 to 13 again.

---

## Changed Files

| File | Action | Summary |
|------|--------|---------|
| `ui/src/main/python-manager.ts` | modified | `AVKIT_READY_LINE`, `usableReadyPort`, exported `publishIfReady` and `forwardConsoleLines` |
| `ui/src/main/index.ts` | modified | The output handler calls `publishIfReady` with `queryLive` and `readDescriptorPid` as callbacks, and reaches the window only through `forwardConsoleLines` |
| `ui/tests/unit/ready-probe-guard.test.ts` | new | AC-108.1 to AC-108.6 |
| `ui/tests/e2e/backend-output-after-close.test.ts` | new | AC-108.7 |
| `docs/build-plan/06-gui.md` | modified | §Ready probe (residual) |

```diff
+  // The query runs PowerShell synchronously on Windows; backend output arrives in many chunks.
+  if (usableReadyPort(input.chunkText) === null) {
+    return false
+  }
+  const live = input.queryLive(input.ownedPid)
```

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
| — | — | None open at approval. Findings by round are in the rolling review. | — | — | — |

### Verdict

Codex approved with no findings open and `intent_achieved: yes`, at report round 4 and ledger round 2 of 6 (dispatch `s44-exec-r4b`). The reviewer's verdict and its stated limits are in `2026-11-03-release-rc1-implementation-critical-review.md`. This line only points there.

---

## Deferred Items

| Item | Kind | Deferred-to | Basis |
|------|------|-------------|-------|
| The tray's Show window item reads a window that may be gone | out-of-scope | — | D-209: only a menu click during shutdown reaches it |
| `E2E-MAIN-PROCESS-ERRORS-UNWATCHED`: the E2E suite doesn't notice a main-process exception | known-issue | `known-issues.yaml` | Filed low: this fix closes the one found, and the watcher is new test infrastructure |
| `E2E-CLIPBOARD-PRIMER-EMPTY`: AC-88.12's primer read an empty clipboard for 5 s once | known-issue | `known-issues.yaml` | Filed low: cause not established, and it didn't repeat |

---

## Decision Log

None.

---

## History

| Event | Date | Agent | Detail |
|-------|------|-------|--------|
| Created | 2026-11-04 | claude-code-local (Claude Opus 5.5) | Initial MEU-108 handoff after H1-2 |
| Amended | 2026-11-04 | claude-code-local (Claude Opus 5.5) | Gate rebound to H1-2 attempt 3 after Mat's rulings (ECN-6); this MEU's code didn't change |
| Amended | 2026-11-04 | claude-code-local (Claude Opus 5.5) | AC-108.5 to AC-108.7 and the crash fix (D-209, ECN-9); gate rebound to H1-2 attempt 5 |
| Amended | 2026-11-04 | claude-code-local (Claude Opus 5.5) | Gate rebound to H1-2 attempt 6 after round 3's finding (ECN-10); ECN-10 didn't change this MEU's code |
