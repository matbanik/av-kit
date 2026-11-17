---
project: "2026-11-15-ready-handshake"
date: "2026-11-15"
source: "grouping .agent/context/grouping/2026-11-15-post-rc3-triage-residuals-session-grouping.md §3 Session 82; issues BACKEND-READY-BEFORE-LISTEN and GUI-READY-CHUNK-BOUNDARY (triage D-810)"
meus: ["MEU-153", "MEU-154"]
status: "draft"
template_version: "2.3"
grouping_source: ".agent/context/grouping/2026-11-15-post-rc3-triage-residuals-session-grouping.md"
---

# Implementation Plan: Listen before the ready line, and read the ready line as a line

> **Project**: `2026-11-15-ready-handshake`
> **Build Plan Section(s)**: 04 [§READY after listen (residual)](../../../build-plan/04-rest-api.md#ready-after-listen-residual) (MEU-153, matrix 4.5) and 06 [§READY line buffering (residual)](../../../build-plan/06-gui.md#ready-line-buffer-residual) (MEU-154, matrix 6.20)
> **Status**: said to execute (USER_EXPLICIT 2026-11-15 'proceed with planning and execution for P:\av-kit\.agent\context\grouping\2026-11-15-post-rc3-triage-residuals-session-grouping.md like we did here. But use the new HDP process. Continue orchestrating the sessions.'). `plan_to_exec_gate: human`; the plan review was approved at round 1 (.agent/context/handoffs/2026-11-15-ready-handshake-plan-critical-review.md).

---

## Goal

**Goal anchor:** a request sent the moment `AVKIT_READY` appears is queued by a listening socket, never refused, and the desktop app's main process reads the backend's stdout as whole lines, so a ready line split across chunks, repeated, or sent beside other lines publishes the API exactly once with the right port; the ready line's text and the descriptor stay as they are.

This is Session 82 of the post-rc.3 grouping (§3, "the two ends of one line"). Order: MEU-153, then MEU-154 (grouping §3). The grouping asks the session to record whether the first request can hit the gap; the plan-time measurement below answers that for the dev backend, and rows 1, 3 and 4 record it for the dev and the packaged backend.

**MEU-153 (`BACKEND-READY-BEFORE-LISTEN`).** `cli.py:218-232` calls `config.bind_socket()`, writes the descriptor, prints the ready line and only then calls `server.run(sockets=[sock])`. In uvicorn 0.54.0 `bind_socket()` binds without listening; `listen()` runs inside `server.run`, after the lifespan startup, when asyncio's `create_server(sock=…)` starts serving. Spec 07 already says the opposite order (`07-distribution.md:73`: "After listen, write the runtime descriptor … then print `AVKIT_READY`").

Plan-time measurement on this PC (dev backend, `ready-gap-probe.mjs`, receipts under `C:/Temp/av-kit/ready-handshake/`):

| Mode | Before the fix | With `sock.listen()` added (scratch copy of `cli.py`) |
|---|---|---|
| Node `fetch` on the ready line | 4 of 5 `ECONNREFUSED`, 1 of 5 `http 200`; the port accepted 13–37 ms after the line | 10 of 10 `http 200` |
| The app's path: the CIM live query, then `fetch` | 5 of 5 `http 200`; the query takes 452–530 ms, which hides the gap | — |
| Python `socket.create_connection` | 5 of 5 connected, after 505–524 ms: Windows retries a refused connect after about 500 ms | — |
| `SO_ACCEPTCONN` on the bound socket | 0 after `bind_socket()`, 1 after `listen()` | — |

So the desktop app's first request does not hit the gap on this PC today, because its live query runs before it publishes; any client that sends on the line does. The fix is one call, `sock.listen(config.backlog)`, before the descriptor and the line. asyncio's later `listen()` on the same socket is harmless (§Research References).

**MEU-154 (`GUI-READY-CHUNK-BOUNDARY`).** `index.ts:269-296` hands every stdout and stderr chunk to `publishIfReady` (`python-manager.ts:147`) on its own. A ready line split before its instance id is never matched, so the API is never published; a repeated ready line queries and publishes again; and a ready line on stderr publishes too. The fix adds a small line reader in `python-manager.ts`, fed by stdout only, that passes each whole line to `publishIfReady` until one publishes, then latches. The veto rule is decided below (D-977): no veto, as today, now pinned by a test.

## Context Tool Decision

```yaml
context_tool_decision:
  phase: planning_and_execution
  eligible_tools: []
  decision: not_applicable
  eligibility_basis: "graphify-out/ and graphify-out-research/ are absent from P:/av-kit (ls, 2026-11-15). The change touches main() in cli.py, three functions in python-manager.ts and one handler in index.ts, all read verbatim at plan time; that is a bypass class."
  human_message_reference: null
```

## Harness, driver and reviewer route

- **Driver:** Claude Code in the VSCode extension on Mat's Windows host (`.agent/docs/harness-profiles.md`, the Claude Code block of `.agent/context/harness.local.md`).
  - Validation goes through `rtk proxy` with the receipt pattern.
  - Receipts go under `C:/Temp/av-kit/ready-handshake/`, named `rh-*`. Pytest runs with `TMP` and `TEMP` at `C:\Temp\av-kit\ready-handshake\tmp`.
  - Every row sets `RECEIPTS_DIR=C:/Temp/av-kit` and `PYTHONIOENCODING=utf-8`, and clears `ELECTRON_RUN_AS_NODE`.
  - Vitest runs from pwsh after `Set-Location 'P:\av-kit\ui'`, never from the Bash tool. Playwright runs with `ELECTRON_RUN_AS_NODE` cleared.
  - Every backend the rows start is ended by its own pid (`taskkill /PID <pid> /T`), never by image name; other worktrees run their own apps.
- **Working directory:** `P:/av-kit` on `main`. There are no branches or worktrees. `.agent/fleet/hub` and every other worktree are left alone.
- **Cloud-local contract:** local. The measurement, the Windows connect behaviour and the packaged smoke need this PC (grouping §3 "Cloud/local: local").
- **Reviewer:** Codex through `tools/Invoke-CodexDispatch.ps1` (`avkit_independent_reviewer`), run by the coordinator, with `AGENT_MODEL_REGISTRY_HOME=P:/.agent`.
  - Ledger loops: `rh-plan-2026-11-15-ready-handshake` and `rh-execution-2026-11-15-ready-handshake`.
  - Caps come from `.agent/review-limits.json`: plan 3 rounds, execution 6, token budgets off. This plan carries no `review_limits` block.
  - Claude wrote the plan, so the reviewer comes from a different vendor. The fallback is Mat.
- **Queue:** Session 87 runs and is committed first, then Sessions 75 to 81 run before this one on `main`. Mat has not said whether each is committed after it closes, so their changes may be uncommitted when this session starts. Baselines and scope checks are path-scoped and bound to content (§Verification Plan 1). Execution waits for Mat's message (`plan_to_exec_gate: human`).
- **Never in these rows without Mat's words:** commit, push, writing an `approved` verdict, or writing into `packaging/dist/`.

## Handoff Set

| Scope | Canonical handoff |
|---|---|
| MEU-153 READY after listen | `.agent/context/handoffs/2026-11-15-ready-handshake-MEU-153-handoff.md` |
| MEU-154 READY line buffering | `.agent/context/handoffs/2026-11-15-ready-handshake-MEU-154-handoff.md` |

Rolling reviews:

- `.agent/context/handoffs/2026-11-15-ready-handshake-plan-critical-review.md`
- `.agent/context/handoffs/2026-11-15-ready-handshake-implementation-critical-review.md`

One handoff per MEU follows `2026-11-14-capture-shapes-steps`.

## Work Packages and Context Lifecycle

| ID | Work | depends_on | context_strategy | durable_outputs |
|---|---|---|---|---|
| WP-1 | Baseline and the measurement before the fix (rows 0 and 1) | — | shared | `baseline.sha`, `baseline-dirty.txt`, `baseline-dirty-hashes.json`, `baseline-scope.json`, `baseline-packaged.json`, `rh-gap-*-before.jsonl` |
| WP-2 | MEU-153: Red, Green and the dev measurement after (rows 2 and 3) | WP-1 | shared | `cli.py`, `tests/unit/test_backend_cli.py`, `tests/integration/test_backend_spawn.py` |
| WP-3 | MEU-153: the scratch packaged build, its smoke and its measurement (row 4) | WP-2 | shared | `rh-pack-*.txt`, `rh-smoke-runtime.json`, `rh-gap-packaged-after.jsonl` |
| WP-4 | MEU-154: Red, then Green (rows 5 and 6) | WP-3 | shared | `python-manager.ts`, `index.ts`, `ui/tests/unit/ready-line-buffer.test.ts`, `ui/tests/unit/ready-line-pipe.test.ts` |
| WP-5 | Spec notes, registers and status (row 7) | WP-4 | shared | 04 and 06 Delivered notes, `known-issues.yaml` and `.md`, `meu-status.yaml`, `meu-registry.md`, `BUILD_PLAN.md`, grouping §6 row 82 |
| WP-6 | Closeout (H1, H2) | WP-5 | `compact_continue` | Two handoffs, the review, the reflection |

## User Review Required

> [!NOTE]
> **Nothing here needs your ruling.** Every decision is autonomous (§Decision Log), and none hits the §4a list. There is no human check row.
>
> **What changes for you:**
>
> - The backend starts listening before it says it is ready. A tool that sends a request the moment it sees the ready line now gets an answer instead of "connection refused". The desktop app on this PC was not affected, because it runs a process check first that takes about half a second.
> - The desktop app reads the backend's ready line as a whole line, from its normal output only, and publishes the API once per backend start. A ready line that arrives in two pieces is no longer missed.
> - Nothing you see changes. The ready line, the backend file and the Console lines read as before.
>
> **Optional look (not a gate):** launch the dev app and check that the Console shows one `INFO backend published for port in AVKIT_READY` line. The MEU-154 handoff names it.

## Proposed Changes

### Single-statement contracts

- **`LISTEN_FIRST` (MEU-153, D-978):** `main()` calls `sock.listen(config.backlog)` straight after `config.bind_socket()` and before `write_descriptor` and the ready print. `server.run(sockets=[sock])` is unchanged. The module and `main()` docstrings say listen.
- **`READY_TEXT_KEPT` (MEU-153, D-978):** the printed line stays `AVKIT_READY port={n} instance={uuid4}` with `flush=True`, the port is the bound socket's, and the descriptor's fields, file names and atomic write are unchanged.
- **`READY_LINES` (MEU-154, D-979):** `createReadyLineReader(publishLine)` keeps the text after the last `\n` as a carry. `push(chunkText)` appends the chunk, takes every complete line in order, strips one trailing `\r`, skips empty lines, and calls `publishLine(line)` for each until one returns `true`.
- **`READY_ONCE` (MEU-154, D-979):** the `push` call in which `publishLine` returns `true` returns `true`. From then on the reader is latched: every later `push` returns `false`, keeps no carry and never calls `publishLine`. Atomicity: the read-then-write of the carry and the latch needs no lock, because Electron's main process runs each `data` callback to completion on one thread, and `publishIfReady` is synchronous up to `publish` (the live query is started with `void`, as today).
- **`READY_BOUND` (MEU-154, D-979):** `READY_LINE_MAX_LENGTH` is `4_096` UTF-16 code units, as `PICKER_LINE_MAX_BYTES` is compared with `.length` (`capture-picker.ts:69`). A carry longer than that is dropped and the reader marks itself discarded; the next complete line, which is the end of the long one, is dropped without `publishLine`, and the mark clears.
- **`READY_STDOUT_ONLY` (MEU-154, D-979):** `index.ts` feeds only `child.stdout` to the reader (`onReadyOutput`). `child.stderr` reaches only the log handler.
- **`READY_NO_VETO` (MEU-154, D-977):** a usable ready line from the owned child's stdout publishes whatever the live query returns, as today (`python-manager.ts:110-120`). The query still runs once per published line (AC-108.3); its result is not used to withhold.
- **`LOG_PER_CHUNK` (MEU-154, D-980):** `onChildOutput` keeps its per-chunk split into Console lines. It no longer calls `publishIfReady`.
- **`GAP_MEASURED` (MEU-153, D-981):** rows 1, 3 and 4 run `ready-gap-probe.mjs` and record, per mode, how many first requests on the ready line were refused; after the fix every first request is `http 200`.

### MEU-153: listen first

1. **`cli.py` (LF):** after `sock = config.bind_socket()` (`:218`), add `sock.listen(config.backlog)` with a one-line comment citing 07:73. Change the module docstring (`:1`) and `main()`'s docstring (`:201`) to "Bind 127.0.0.1, listen, write the descriptor, print READY_LINE, then serve." Nothing else changes.
2. **`tests/unit/test_backend_cli.py` (CRLF, kept):** append AC-153.1 and AC-153.2. Both run the real `main()` with `build_services` and `create_app` replaced (`(object(), lambda: None)` and `object()`), `uvicorn.Config.bind_socket` wrapped to keep the socket it returns, `write_descriptor` wrapped to record `SO_ACCEPTCONN` and then delegate into `tmp_path`, `print` replaced in the module (`monkeypatch.setattr(cli, "print", …, raising=False)`) to record the line and `SO_ACCEPTCONN`, and `uvicorn.Server.run` replaced by a stub that closes the sockets. No network traffic, no real server.
3. **`tests/integration/test_backend_spawn.py` (LF, kept):** append AC-153.3, five spawns that each connect as soon as the ready line appears.
4. **Measurement and packaged smoke:** rows 1, 3 and 4 (D-981, D-983).

### MEU-154: the line reader

1. **`python-manager.ts` (LF):** after `publishIfReady`, add

   ```ts
   export const READY_LINE_MAX_LENGTH = 4_096
   export function createReadyLineReader(publishLine: (line: string) => boolean): {
     push(chunkText: string): boolean
     readonly state: { pendingLength: number; discarded: boolean; published: boolean }
   }
   ```

   with the `READY_LINES`, `READY_ONCE` and `READY_BOUND` behaviour. `AVKIT_READY_LINE`, `usableReadyPort`, `confirmReadyAndPublish` and `publishIfReady` are unchanged. The comment at `:110-114` gains one line naming D-977.
2. **`index.ts` (CRLF, kept):** split the handler. `onChildOutput` keeps its log loop and its one `forwardConsoleLines(mainWindow, [item])`, and drops the `publishIfReady` call. A new `readyReader = createReadyLineReader((line) => …)` calls `publishIfReady({ chunkText: line, ownedPid, readDescriptorPid: () => readDescriptorPid(appData), queryLive: queryLiveProcess, oursExe: pythonImage, token: guiNonce, publish: publishBackendReady })`, returning `false` when `ownedPid` is `null`. A new `onReadyOutput` pushes `chunk.toString('utf8')` and, when `push` returns `true`, writes the existing published note through `appendStdoutLog` and `forwardConsoleLines(mainWindow, [note])`. Both are defined before the hookups, which read:

   ```ts
   child.stdout?.on('data', onChildOutput)
   child.stdout?.on('data', onReadyOutput)
   child.stderr?.on('data', onChildOutput)
   ```

   This keeps AC-108.4 and AC-108.6 true as written: the slice from `const onChildOutput` to `child.stdout?.on('data', onChildOutput)` still holds `publishIfReady(`, `queryLive: queryLiveProcess` and exactly two `forwardConsoleLines(mainWindow, `, and `index.ts` still has no `queryLiveProcess(` call and no `confirmReadyAndPublish`. AC-108.7 still finds the streams by the `onChildOutput` listener name.
3. **`ui/tests/unit/ready-line-buffer.test.ts` (new, LF):** AC-154.1 to AC-154.7, with synthesized chunks and the real `publishIfReady` inside `publishLine`.
4. **`ui/tests/unit/ready-line-pipe.test.ts` (new, LF):** AC-154.8, a real child process through the real `spawnOwned`.

### Boundary Inventory

| Surface | Schema Owner | Field Constraints | Extra-Field Policy |
|---|---|---|---|
| The ready line on the backend's stdout | `cli.py` (`READY_PREFIX`), read by `python-manager.ts` (`AVKIT_READY_LINE`), `test_backend_spawn.py`, `smoke_packaged_tts.py` and the MCP audit runner | Unchanged text, fields and flush (`READY_TEXT_KEPT`, AC-153.2) | Unchanged |
| `backend.json` and `backend-port.txt` | `cli.py` `write_descriptor` | Unchanged; written after listen instead of before | Unchanged |
| The main process's view of the child's stdout | `python-manager.ts` `createReadyLineReader` | Lines split on `\n`, one trailing `\r` stripped, 4 096 code units at most | A longer line is dropped (`READY_BOUND`) |

No API route, OpenAPI document, MCP tool shape, renderer state or database schema changes.

### Acceptance Criteria

Python tests are named `test_ac_153_<n>_…`, so `red-check.py --require test_ac_153_1` matches each exactly. Vitest titles start with `AC-154.<n>`.

- **Every MEU-154 test asserts the new names exist first.** The two Vitest files import the module as a namespace (`import * as pm from '../../src/main/python-manager'`) and assert `typeof pm.createReadyLineReader === 'function'` and `pm.READY_LINE_MAX_LENGTH === 4096` before any call, so Red fails by assertion, never by `TypeError` (Session 52 RULE-4).
- **The MEU-153 tests never let a refused or timed-out connect reach the receipt.** AC-153.3 catches `OSError` (which includes `TimeoutError` and `ConnectionRefusedError`) and records a boolean, so a Red fails on `assert` only and `red-check.py` does not read it as a setup failure.
- **AC-153.2 and AC-154.9 are pins.** They pass before and after the change and are not `--require`d at Red.

| AC | Type | Description | Source | Negative Test |
|----|------|-------------|--------|---------------|
| AC-153.1 | unit | `main()` with the stubs above: at the `write_descriptor` call and at the ready print, the kept socket reads `getsockopt(SOL_SOCKET, SO_ACCEPTCONN) == 1`. The test first asserts `hasattr(socket, "SO_ACCEPTCONN")`, with no skip, and that both spies ran once. | Local Canon (04 §READY after listen: Listen first; 07:73); Research-backed (plan-time `soacceptconn.txt`: 0 after bind, 1 after listen) | In Red both reads are 0 |
| AC-153.2 | unit | The same run prints exactly one line, which matches `^AVKIT_READY port=(\d+) instance=[0-9a-f-]{36}$`; its port equals the kept socket's port and the descriptor's `port`, and `flush=True` was passed. A pin: it passes in Red too. | Local Canon (04: Line unchanged; MEU-24, MEU-108) | A changed prefix, field order or port fails the match |
| AC-153.3 | integration | Five spawns of `python -m avkit_api` (each with its own `tmp_path` app-data): as soon as `_wait_ready` returns, `socket.create_connection(("127.0.0.1", port), timeout=0.25)` inside `try/except OSError` gives a boolean, and `GET /api/v1/health` with a 10 s timeout gives 200. The test asserts all five booleans are `True` and all five statuses 200, and ends each child in `finally`. | Local Canon (04: Tests, "connects as soon as the ready line appears and gets a response, repeated"); Research-backed (`py-connect-pre.txt`: before the fix a connect waits about 500 ms for Windows' retry, so 0.25 s fails) | In Red at least one connect fails; the chance that all five land after listen is about 0.2^5 on the measured rate |
| AC-153.4 | integration | The onedir backend built from this tree into the scratch dist (row 4, D-983) has none of `torch`, `kokoro`, `phonemizer` or `espeakng_loader` under `_internal`, and `tools/smoke_packaged_runtime.py --backend-dir <scratch>/avkit-backend` exits 0. | Local Canon (04: Tests, "the packaged backend smoke still passes"; MEU-141 `RUNTIME_SMOKE`) | Exit 1 or 2, or a forbidden folder, stops on S7 |
| AC-153.5 | integration | The measurement (D-981): row 1 records the dev `fetch`, dev `cim` and packaged `fetch` counts before the fix (packaged: `absent` when there is no exe); row 3 records 10 dev `fetch` runs and row 4 five packaged `fetch` runs after it, each `gap-tally.py --all-ok` exit 0 (every first request `http 200`, no error). The counts are copied into the MEU-153 handoff and 04's Delivered note. | Local Canon (grouping §3: "records whether the first request can hit the gap") | `--all-ok` exits 1 on any refused first request |
| AC-154.1 | unit | A ready line split in two at each of four points (inside `AVKIT_READY`, inside the port, inside `instance=`, inside the id), after an `INFO boot\n` line: the first `push` returns `false` and makes no live query; the second returns `true`; one publish, `http://127.0.0.1:13988/api/v1`, one query with pid 111. | Local Canon (06 §READY line buffering: Lines, Tests "a line split in two") | In Red the reader does not exist; today's per-chunk test misses the first three splits |
| AC-154.2 | unit | One chunk holding a log line, the ready line and another log line, and one chunk holding two log lines then the ready line with no trailing newline followed by `\n` in the next chunk: each publishes once with the right port, and `publishLine` sees the lines in order. | Local Canon (06: Tests, "two lines in one chunk") | A log line passed to `publishLine` after the ready line fails the order assertion |
| AC-154.3 | unit | A repeated ready line (in the same chunk, in a later chunk, and with another port): one publish with the first port, one live query, `state.published` true, and later `push` calls return `false`, keep `pendingLength` 0 and never call `publishLine`. | Local Canon (06: Once, Tests "a repeated line") | A second publish or a second query fails |
| AC-154.4 | unit | No veto: with `queryLive` returning `{ ok: false }` and `readDescriptorPid` returning `null`, and again with an image that differs from `oursExe`, a usable ready line still publishes once. | Local Canon (06: Veto; D-977; `python-manager.ts:110-114`; 07:219) | A withheld publish fails |
| AC-154.5 | unit | A 5 000-character line with no newline, then its end and `\n`, then a ready line: the long line never reaches `publishLine`, `state.discarded` is true after the first push and false after the second, and the ready line publishes. A ready line ending `\r\n` publishes with the right port and the `\r` stripped. | Local Canon (`capture-picker.ts:69`, `PICKER_LINE_MAX_BYTES` and its poison; D-979) | A long line passed on, or a carry longer than 4 096, fails |
| AC-154.6 | unit | `AVKIT_READY port=0 instance=x` and an unterminated ready line at the end of the input do not publish and make no query; a later usable ready line does. | Local Canon (AC-108.1, AC-108.2) | A query on `port=0` fails |
| AC-154.7 | unit | Source text of `index.ts`, read as UTF-8 with `\r` removed: it holds `child.stdout?.on('data', onReadyOutput)` once and no `child.stderr?.on('data', onReadyOutput)`; the text from `const onChildOutput` to `const readyReader` holds no `publishIfReady(`; the text from `const readyReader` to `child.stdout?.on('data', onChildOutput)` holds exactly one `publishIfReady(` and `createReadyLineReader(`. | Local Canon (D-979 `READY_STDOUT_ONLY`; the AC-108.4 source-slice pattern) | In Red there is no `onReadyOutput` |
| AC-154.8 | unit | A real pipe: `spawnOwned([process.execPath, '-e', script], env)` runs a script that writes `INFO boot\nAVKIT_READY port=139`, waits 80 ms, writes `88 instance=70d5efcc-856f-4f37-b90a-eb2b4c09e72e\nAVKIT_READY port=14000 instance=x\n` and exits. The test feeds `child.stdout` to a reader whose `publishLine` is the real `publishIfReady`, waits for `exit`, and asserts at least two `data` events, a first chunk that does not end in `\n`, and exactly one publish, for port 13988. | Local Canon (06: Lines, Once); `spawnOwned`'s `stdio: ['ignore','pipe','pipe']` | In Red the reader does not exist |
| AC-154.9 | E2E | The pins pass unchanged: `ui/tests/unit/ready-probe-guard.test.ts` (AC-108.1 to AC-108.6) and `ui/tests/e2e/backend-output-after-close.test.ts` (AC-108.7) after `npm run build`. | Local Canon (MEU-108 `READY_GUARD`, `LOG_AFTER_WINDOW`) | A changed slice or listener name fails one of them |

#### Spec Sufficiency Table

| Behavior | Classification | Resolution |
|----------|---------------|------------|
| When the socket listens | Local Canon | Before the descriptor and the line (07:73, 04 Listen first; D-978) |
| The ready line's text | Local Canon | Unchanged (04 Line unchanged) |
| Whether the first request can hit the gap | Research-backed | Measured: yes for a client that sends on the line, no for today's app on this PC (D-981) |
| How the packaged smoke runs without touching `packaging/dist` | Local Canon | A scratch `--distpath` build (D-983) |
| Where the line reader lives and its bound | Local Canon | `python-manager.ts`, 4 096 with a poison, the capture-picker shape (D-979) |
| Which stream feeds the reader | Local Canon | stdout only (07:73 "on stdout"; D-979) |
| Whether a failed live query vetoes a ready line | Local Canon | No veto (D-977) |
| Console log framing across chunks | Local Canon | Unchanged, out of scope (D-980) |

#### Files Modified

| File | Action | Line endings | Summary |
|------|--------|--------------|---------|
| `packages/api/src/avkit_api/cli.py` | modify | LF, kept | `sock.listen(config.backlog)`; two docstrings |
| `tests/unit/test_backend_cli.py` | modify | CRLF, kept | AC-153.1, AC-153.2 appended |
| `tests/integration/test_backend_spawn.py` | modify | LF, kept | AC-153.3 appended |
| `ui/src/main/python-manager.ts` | modify | LF, kept | `READY_LINE_MAX_LENGTH`, `createReadyLineReader`; one comment line |
| `ui/src/main/index.ts` | modify | CRLF, kept | `readyReader`, `onReadyOutput`, the stdout hookup; `onChildOutput` drops its publish |
| `ui/tests/unit/ready-line-buffer.test.ts` | new | LF | AC-154.1 to AC-154.7 |
| `ui/tests/unit/ready-line-pipe.test.ts` | new | LF | AC-154.8 |
| `docs/build-plan/04-rest-api.md` | modify | CRLF, kept | A `Delivered (Session 82)` note under §READY after listen, with the measured counts |
| `docs/build-plan/06-gui.md` | modify | CRLF, kept | A `Delivered (Session 82)` note under §READY line buffering, naming D-977 |
| `.agent/context/known-issues.yaml` | modify (tool) | LF, kept | The two issues resolved through `issue-resolve.py` |
| `.agent/context/known-issues.md` | regenerate | LF | `issue_triage.py render` |
| `.agent/context/meu-status.yaml` | modify (tool) | LF, kept | MEU-153 and MEU-154: `ready_for_review`, then `approved` (H2-2) |
| `.agent/context/meu-registry.md`, `docs/BUILD_PLAN.md` | regenerate | LF | `meu_status.py render` |
| `.agent/context/grouping/2026-11-15-post-rc3-triage-residuals-session-grouping.md` | modify | LF, kept | §6 row 82 only: `executed (Session 82)` and this plan folder |

Line endings were measured with Python bytes (`C:/Temp/av-kit/ready-handshake/rh-eol.txt`, at `HEAD` `6aaf9b0`). A CRLF file is read and written with `newline=""` from CRLF text, and the session gate checks every file in this table again. `index.ts` and `test_backend_cli.py` are the CRLF code files; an edit that writes LF lines into them fails the gate.

### Project files

- **Plan-local scripts**, all in this plan folder:
  - written at plan time: `ready-gap-probe.mjs` (the measurement; writes only under its `--root` and `--out`), `gap-tally.py` (reads one JSONL receipt; `--selftest`);
  - written in row 0: `baseline.ps1`, `red-check.py`, `identity.py`, `issue-resolve.py`;
  - written in H1-2: `session-gate.ps1`.
- **Row 0 data:** `baseline.sha`, `baseline-dirty.txt`, `baseline-dirty-hashes.json`, `baseline-scope.json`, `baseline-packaged.json`.
- **Scratch build:** `C:/Temp/av-kit/ready-handshake/pack/` (`build/`, `dist/avkit-backend/`, `dist/deno/`). Never under `packaging/`.
- **State:** `docs/execution/metrics.md` (CRLF), `.agent/context/current-focus.md` (CRLF), the two handoffs, the rolling reviews and the reflection.

### Sibling overlap

The plan binds each shared file to its content at row 0 (`baseline-scope.json`), not to `HEAD`, and changes only its own entries or lines in it.

| File | Siblings | Rule |
|---|---|---|
| `.agent/context/known-issues.yaml`, `known-issues.md` | Sessions 75 to 81 close their own issues before this one; Session 83 rewrites the lines that name the home folder after it (grouping §2 soft order) | Row 7 changes only the two issues' `status`, `verification` and `resolution_path`, names no home path, and binds to the row-0 hash (S4) |
| `meu-status.yaml`, `meu-registry.md`, `docs/BUILD_PLAN.md` | Sessions 75, 77, 80, 81 | Only MEU-153's and MEU-154's rows change, through `meu_status.py` |
| Grouping §6 table | Every session of the grouping | Only row 82 changes |
| `docs/build-plan/06-gui.md` | Sessions 80 and 81 add Delivered notes in other sections; Session 83 edits its home-path lines | Only the one note under §READY line buffering is added |
| `docs/build-plan/04-rest-api.md` | None in this grouping | Only the one note is added |
| `ui/tests/e2e/`, `ui/tests/unit/setup.ts` | Session 78 (`e2e-harness-hardening`) runs before this one | This plan edits neither; AC-154.9 runs the E2E test as it reads after Session 78 |
| `ui/tests/unit/dev-spawn.test.ts` | Session 83 | Not touched |
| `packaging/dist/` | Session 74 (TTS model assets) owns the packaging output | Never written; row 1 runs the existing exe read-only, row 4 builds into the scratch dist |
| `current-focus.md`, `metrics.md` | Every session | Read first; change only this session's lines |

No sibling session edits `cli.py`, `python-manager.ts`, `index.ts` or the two existing test files (grouping §3 file lists).

## Out of Scope

| Item | Kind | Deferred-to MEU | Basis |
|---|---|---|---|
| Line framing of Console log lines split across chunks | out-of-scope | — | D-980: neither issue names it, and the Console reads a split line as two lines today without harm |
| Polling `GET /health` after the ready line (07:219 "poll GET /health (100ms → 5s)") | out-of-scope | — | Neither issue names it; with `LISTEN_FIRST` a request on the line is queued, which is what the issue asks |
| Dropping the live query from `publishIfReady` | out-of-scope | — | D-977: it would change AC-108.3, an existing test's expectation (M-7) |
| A ready line on stderr | out-of-scope | — | The backend prints it on stdout (07:73); D-979 reads stdout only |
| Rebuilding `packaging/dist` or the installer | out-of-scope | — | Session 74 owns the packaging output; D-983 builds in scratch |
| The MCP audit runner's port wait (`mcp-server/scripts/audit/backend.ts`) | out-of-scope | — | It stays correct after the fix; no MCP change |
| MEU-144 and the TTS model assets (Session 74) | out-of-scope | — | Session brief |

## BUILD_PLAN.md Audit

MEU-153 and MEU-154 are registered (`meu-status.yaml`, `pending`, matrix 4.5 and 6.20; dependencies MEU-24 and MEU-108 are `approved`). Row 7 sets both to `ready_for_review` with this plan's `execution_plan` through `tools/meu_status.py update`, and H2-2 sets both to `approved`. `meu-registry.md` and `docs/BUILD_PLAN.md` are regenerated by `tools/meu_status.py render`, never by hand:

```powershell
rtk proxy uv run python tools/meu_status.py render --check > C:/Temp/av-kit/ready-handshake/rh-render-check.txt 2>&1; $code=$LASTEXITCODE; Get-Content C:/Temp/av-kit/ready-handshake/rh-render-check.txt; exit $code
```

## Verification Plan

> [!IMPORTANT]
> Classify every command through `.agent/docs/output-evidence-policy.md`. `rtk proxy` is used for exact evidence.

### 1. Baseline (row 0)

`baseline.ps1` follows `2026-11-15-framework-small-syncs/baseline.ps1` and does the following:

1. **Tree state.** It records `HEAD` in `baseline.sha` and `git status --porcelain --untracked-files=all` in `baseline-dirty.txt`. Sessions 75 to 81 may be listed there.
2. **Path-scoped baseline.**
   - It writes `baseline-scope.json`: for each path in §Files Modified, its SHA-256, or `absent`. The two new Vitest files must be `absent`.
   - It writes `baseline-dirty-hashes.json`: the SHA-256 of every `baseline-dirty.txt` path outside this scope, or `deleted`. S4 and the gate's `scope-paths` compare against it.
   - It checks `cli.py`, `python-manager.ts`, `index.ts`, the two existing test files, 04 and 06 against `git show HEAD:` for each. A product or test file that differs from `HEAD` is S2: an earlier session changed code this plan edits. (04 and 06 may differ only by another session's Delivered note in another section; the script prints the diff, and a change inside the two home sections is S2.)
   - It writes `baseline-packaged.json`: the SHA-256, size and mtime of `packaging/dist/avkit-backend/avkit-backend.exe`, or `absent`. Nothing under `packaging/` is written.
3. **Base receipts.** It runs `uv sync --frozen --all-packages` and the base Python suite (`rh-base-py.txt`), with `TMP` and `TEMP` at `C:\Temp\av-kit\ready-handshake\tmp`.
4. **Plan-local scripts.**
   - It copies `red-check.py` and `identity.py` from `docs/execution/plans/2026-11-15-framework-small-syncs/`, with this plan's `PLAN` and `PROJECT_ARTIFACTS` (handoffs, reflection, metrics, current focus), and `DECLARED_NEW` extended with `createReadyLineReader` and `READY_LINE_MAX_LENGTH`.
   - It copies `issue-resolve.py` from `docs/execution/plans/2026-11-15-closeout-record-once/` with `SCRATCH` at `C:/Temp/av-kit/ready-handshake/issue-resolve`.
   - It runs the `red-check.py`, `identity.py` and `gap-tally.py` selftests.

If any step fails, the row fails and nothing else runs.

### 2. Red, then Green

- **Each Red receipt holds an assertion failure, never a setup failure.** `red-check.py --require` names AC-153.1 and AC-153.3 (row 2) and AC-154.1 to AC-154.8 (row 5). Its `HARD_SETUP_FAILURE` refuses `ECONNREFUSED` and `TimeoutError` anywhere in a receipt, so AC-153.3 records connects as booleans and never names the exception in its assert line.
- **New names fail by assertion.** The Vitest tests check `typeof pm.createReadyLineReader` first.
- **Expectations stay immutable in Green.** A Green row that needs a changed expectation stops on S3.
- **Line endings.** The CRLF files are measured with Python bytes and written with `newline=""`.

### 3. The measurement (rows 1, 3 and 4)

`ready-gap-probe.mjs` starts the backend with `--token`, `--mcp-token`, `--port 0` and a fresh `--app-data`, with `HOME` and `USERPROFILE` set to a run folder under `C:/Temp/av-kit/ready-handshake/probe-runs/`. In `fetch` mode it sends `GET /api/v1/health` the moment the ready line appears; in `cim` mode it first runs the same `Get-CimInstance Win32_Process` query the app runs. It records the outcome of the first request and when the port first accepted, ends the backend by its pid tree, and deletes the run folder. `gap-tally.py` checks the count and, with `--all-ok`, that every first request was `http 200`.

| Row | Backend | Mode | Runs | Gate |
|---|---|---|---|---|
| 1 | dev (`.venv/Scripts/python.exe -m avkit_api`), before the fix | `fetch` | 5 | count only (a refused request is the measurement) |
| 1 | dev, before the fix | `cim` | 5 | count only |
| 1 | `packaging/dist/avkit-backend/avkit-backend.exe`, read-only, if `baseline-packaged.json` has it | `fetch` | 5 | count only; `absent` is recorded otherwise |
| 3 | dev, after the fix | `fetch` | 10 | `--all-ok` |
| 4 | the scratch build, after the fix | `fetch` | 5 | `--all-ok` |

### Session gate (H1-2)

`session-gate.ps1` follows the peer's shape (`2026-11-15-closeout-record-once/session-gate.ps1`):

- one receipt per step in `C:/Temp/av-kit/ready-handshake/`, named `rh-D6-<step>`;
- fail-fast, with later steps printed as `not_run`;
- the last line is `session-gate: all steps exit 0`.

| Stage | Steps |
|---|---|
| Identity | `identity.py` before and after the run; the two must match |
| Static | `py-lint` (`ruff check packages/ tests/`); `py-format` (`ruff format --check` on `cli.py`, the two test files and `gap-tally.py`); `py-types` (`pyright packages/`); `ui-types` and `ui-lint` (pwsh in `ui/`); `task-contract`; `scope-paths` (every changed path is in §Files Modified, in this plan folder, in the closeout artifacts or in `baseline-dirty.txt`, and every `baseline-dirty.txt` path outside this scope keeps its row-0 content state); `line-endings` (each §Files Modified file keeps its row-0 kind); `red-check-selftest`; `gap-tally-selftest` |
| Targeted | `meu-153-tests` (`test_backend_cli.py`, `test_backend_spawn.py`); `meu-154-tests` (`ready-line-buffer.test.ts`, `ready-line-pipe.test.ts`, `ready-probe-guard.test.ts`); `packaged-receipt` (row 4's `rh-pack-cli-sha.txt` equals the current SHA-256 of `cli.py`, so the packaged smoke and measurement tested this `cli.py`; if not, re-run row 4 first) |
| Fresh full | `py-tests` (`pytest tests/ --tb=short -q -rfE`); `ui-tests` (the full Vitest run, pwsh in `ui/`); `ui-build` (`npm run build`); `e2e-late-line` (`backend-output-after-close.test.ts`, `ELECTRON_RUN_AS_NODE` cleared); `openapi` (`export_openapi.py --check openapi.committed.json`); `state-render` (`meu_status.py render --check`); `issues-render-check` (`issue_triage.py render --check`) |
| Skipped, with reason | `mcp-*`: no MCP change; the MCP Python tests run inside `py-tests`. The rest of `test:e2e`: only the main process's output handler changed, and AC-108.7 is the E2E test that drives it. The packaged build: row 4's receipt, bound to `cli.py` by `packaged-receipt` |

`py-tests` and `ui-tests` excuse only ids that row 0's receipt shows failing.

## Stop Conditions

| ID | Condition | Action |
|---|---|---|
| S1 | A `graphify-out` graph appears | Re-decide the context tool |
| S2 | Row 0 finds a product or test file of §Files Modified changed since `HEAD`, or a change inside 04's or 06's home section | Stop. An earlier session changed code this plan edits; bring the diff to Mat |
| S3 | A Red receipt fails `red-check.py`, or a Green row needs a changed expectation | Fix the test setup; do not move to Green, and never edit an expectation in Green |
| S4 | A path outside this plan's scope and `baseline-dirty.txt` changes, or a `baseline-dirty.txt` path changes content, or `known-issues.yaml` no longer has its row-0 hash at row 7 | Stop and re-baseline with Mat; never commit, stash or revert another session's work |
| S5 | An existing test outside AC-153.2 and AC-154.9 fails after Green | Stop: that is an M-7 question (§4a), not a fix |
| S6 | Codex is unavailable or the ledger refuses | Mat |
| S7 | The scratch PyInstaller build fails, a forbidden folder appears under `_internal`, the runtime smoke exits non-zero, or the packaged `--all-ok` tally fails | Stop and bring the receipt to Mat; never fall back to `packaging/dist` |

## Decision Log

> [!NOTE]
> Every decision below is autonomous with `mandatory: none`: each passed the §4a list and the §4 test. There are no briefs, so no expert pass is needed. The grouping rows (D-813 to D-816 bear on Session 82; the probe also reads D-817) stay in the grouping file's §8 and are not copied here; H2-2 reads them through `--decision-source` on the grouping file (this plan's `grouping_source`), and the issues' D-810 through `--decision-issue` (`rh-decision-probe.txt`). The grouping's old "Carry-forward" wording (§9, "each row appears in its consuming session's reflection") is ignored under the new HDP §6: the reflection's `### Decisions Log` lists only this session's reversible autonomous choices. D-985 to D-987 were left free for execution and are now used: D-985 (the red-check pytest header) and D-986 (formatting gap-tally.py) at row 0, and D-987 (the pipe test waits for close) at row 5, each autonomous with `mandatory: none`.

```yaml
decision_log:
  - id: D-977
    stage: planning
    question: "Does a failed live process query veto a ready line that arrives on the owned child's stdout?"
    resolution: autonomous
    class: two-way
    mandatory: none
    chosen: "No veto. A usable ready line on the stdout pipe of the child the app spawned publishes the API whatever the live query returns; the query still runs once per published line, and its result is not used to withhold."
    source_tag: Local Canon
    precedents:
      - "docs/build-plan/07-distribution.md:219 — wait for backend.json whose pid equals the child we just spawned, or AVKIT_READY: the ready line on the owned pipe is the ownership proof"
      - "ui/src/main/python-manager.ts:110-114 — do not withhold publish when CIM image or pid strings disagree; that was the Windows delivery failure that left Add on backend not ready"
      - "ui/tests/unit/ready-probe-guard.test.ts AC-108.3 — a usable ready chunk queries once and publishes (Session 44, MEU-108)"
    research: { engine: none, sources: [] }
    reasoning: "06 asks for this to be decided with its evidence. The evidence is that only the app writes to and reads from the child's stdout pipe, so a line on it can come only from the process the app started, which 07 names as enough to trust it. The live query is a second opinion that has been wrong on Windows before: a CIM path that differed in case or form from the venv path withheld the publish and left the app stuck. A veto lost because it brings that failure back for no gain in ownership. Dropping the query lost because AC-108.3 expects exactly one query per published line, and changing an existing test's expectation is an M-7 question this plan avoids. Two-way: one branch in one function."
  - id: D-978
    stage: planning
    question: "Where does the backend start listening, so a request sent on the ready line is queued?"
    resolution: autonomous
    class: two-way
    mandatory: none
    chosen: "Call sock.listen(config.backlog) in main() straight after config.bind_socket() and before write_descriptor and the ready print; keep the ready line, the descriptor and server.run(sockets=[sock]) unchanged."
    source_tag: Research-backed
    precedents:
      - "docs/build-plan/07-distribution.md:73 — after listen, write the runtime descriptor atomically, then print AVKIT_READY"
      - "docs/build-plan/04-rest-api.md:448-449 — Listen first; Line unchanged"
      - ".agent/context/known-issues.yaml BACKEND-READY-BEFORE-LISTEN — candidate fix: call sock.listen() before printing the line"
    research:
      engine: local-measurement
      sources:
        - "uvicorn 0.54.0 config.py bind_socket binds and does not listen; server.py startup passes the socket to loop.create_server, which listens when it starts serving"
        - "C:/Temp/av-kit/ready-handshake/gap-fetch-pre.txt and gap-fetch-fix.txt — 4 of 5 refused before, 10 of 10 http 200 with the listen call added"
        - "C:/Temp/av-kit/ready-handshake/soacceptconn.txt — SO_ACCEPTCONN 0 after bind_socket, 1 after listen"
        - "Microsoft Learn, Winsock listen — a listen call on a socket that is already listening succeeds"
    reasoning: "The socket exists before the ready line, so listening on it then makes the kernel queue any connect that comes early, and asyncio's own listen on the same socket later is harmless. The backlog is uvicorn's own value, so nothing about the server's behaviour changes. Moving the print into a lifespan or startup hook lost because it changes when the descriptor is written and couples the line to uvicorn internals. Retrying on the client side lost because every client would need it, which is the workaround the MCP audit already carries. Two-way: one line."
  - id: D-979
    stage: planning
    question: "What shape does the main process's ready line reader take?"
    resolution: autonomous
    class: two-way
    mandatory: none
    chosen: "createReadyLineReader(publishLine) in python-manager.ts: a carry split on newline, one trailing carriage return stripped, empty lines skipped, each whole line passed to publishLine until one returns true, then latched; a carry over READY_LINE_MAX_LENGTH (4096) is dropped and the next whole line poisoned. index.ts feeds it the child's stdout only."
    source_tag: Local Canon
    precedents:
      - "ui/src/main/capture-picker.ts:69, :243 and :341-368 — PICKER_LINE_MAX_BYTES, the carry, the lineDiscarded poison and the ready latch for a child's line protocol"
      - "docs/build-plan/06-gui.md:1664-1667 — Lines; Once; Tests with synthesized chunks"
      - "docs/build-plan/07-distribution.md:73 — print AVKIT_READY on stdout"
    research: { engine: none, sources: [] }
    reasoning: "The capture picker already reads a child's line protocol this way, so the same shape keeps one pattern in the main process. Passing each whole line to the existing publishIfReady keeps the regex, the port check and the one query in one place, so the guard and the publisher cannot disagree (python-manager.ts:89). Reading stdout only follows 07, which puts the line on stdout, and removes a way for a stderr line to publish. Reading both streams lost for that reason. Buffering inside onChildOutput lost because AC-108.4 and AC-108.6 slice that handler's text, and a separate reader keeps those slices true. Two-way: internal names."
  - id: D-980
    stage: planning
    question: "Does the Console log split also become line-buffered across chunks?"
    resolution: autonomous
    class: two-way
    mandatory: none
    chosen: "No. onChildOutput keeps its per-chunk split into Console lines and only drops its publishIfReady call."
    source_tag: Local Canon
    precedents:
      - "docs/build-plan/06-gui.md:1664 — Lines is about the ready line being seen once, whole"
      - ".agent/context/known-issues.yaml GUI-READY-CHUNK-BOUNDARY — names publishIfReady and confirmReadyAndPublish only"
    research: { engine: none, sources: [] }
    reasoning: "Neither issue nor 06 names the Console framing, and a log line split in two shows as two Console lines without losing text. Buffering it would hold back the last line of every chunk until the next one, which changes when lines appear and needs its own tests. Two-way: a later MEU can add it."
  - id: D-981
    stage: planning
    question: "How does the session record whether the first request can hit the gap?"
    resolution: autonomous
    class: two-way
    mandatory: none
    chosen: "Rows 1, 3 and 4 run ready-gap-probe.mjs: before the fix, 5 dev fetch, 5 dev cim and 5 packaged fetch runs on the existing exe (read-only, or absent); after it, 10 dev fetch and 5 fetch runs on the scratch build, each checked by gap-tally.py --all-ok. The counts go into the MEU-153 handoff and 04's Delivered note."
    source_tag: Research-backed
    precedents:
      - ".agent/context/grouping/2026-11-15-post-rc3-triage-residuals-session-grouping.md:206 — the session also records whether the first request can hit the gap"
      - ".agent/context/handoffs/2026-11-03-release-rc1-MEU-108-handoff.md — Session 44 measured the READY probe on synthesized and real output"
    research:
      engine: local-measurement
      sources:
        - "C:/Temp/av-kit/ready-handshake/gap-cim-pre.txt — 5 of 5 http 200 when the CIM query runs first (452-530 ms)"
        - "C:/Temp/av-kit/ready-handshake/gap-tally-planning.txt — the planning counts"
    reasoning: "The fetch mode answers whether any client can hit the gap, and the cim mode answers whether today's app does, because it runs the same query before it publishes. The packaged runs show the same for the shipped form. Recording the before counts without a gate keeps the measurement honest, since the gap is a race; only the after counts are gated. Two-way: a scratch measurement."
  - id: D-982
    stage: planning
    question: "Which tests prove MEU-153, given that the gap is a race?"
    resolution: autonomous
    class: two-way
    mandatory: none
    chosen: "A unit test that runs the real main() with stubs and reads SO_ACCEPTCONN at the descriptor write and at the print (AC-153.1), a pin on the line's text (AC-153.2), and an integration test that connects with a 0.25 s timeout as soon as the line appears, five times, then gets health 200 (AC-153.3)."
    source_tag: Research-backed
    precedents:
      - "docs/build-plan/04-rest-api.md:448 — a test that connects as soon as the ready line appears and gets a response, repeated"
      - "tests/integration/test_backend_spawn.py:51-65 — _wait_ready, the existing spawn reader"
    research:
      engine: local-measurement
      sources:
        - "C:/Temp/av-kit/ready-handshake/py-connect-pre.txt — before the fix a Python connect on the line succeeds only after about 500 ms, when Windows retries"
        - "C:/Temp/av-kit/ready-handshake/soacceptconn.txt — the socket option tells listening from bound"
    reasoning: "The socket option makes the unit test exact: it fails every time before the fix and passes every time after, with no timing. The spawn test covers the real process; a plain connect would pass before the fix because Windows retries a refused connect after about half a second, so the 0.25 s timeout is what makes it fail. Catching OSError keeps a refused or timed-out connect out of the receipt, which red-check.py would refuse as a setup failure. Two-way: tests only."
  - id: D-983
    stage: planning
    question: "How does the packaged backend smoke run without touching packaging/dist?"
    resolution: autonomous
    class: two-way
    mandatory: none
    chosen: "Row 4 runs PyInstaller on packaging/avkit-backend.spec with --workpath and --distpath under C:/Temp/av-kit/ready-handshake/pack, copies deno.exe and LICENSE.md from packaging/deno-win64 into the scratch dist's deno folder, checks _internal for forbidden folders, runs tools/smoke_packaged_runtime.py on it and the measurement on its exe, and records cli.py's SHA-256 beside the receipts."
    source_tag: Local Canon
    precedents:
      - "docs/execution/plans/2026-11-12-youtube-client-runtime/task.md row 5 — build the onedir, copy packaging/deno-win64 to dist/deno, run smoke_packaged_runtime.py"
      - "packaging/avkit-backend.spec:18 — SPEC_DIR from SPECPATH, so the spec's sources resolve from the repository whatever the dist path"
      - "packages/api/src/avkit_api/wiring.py:124 — the bundled Deno is read from the exe's grandparent deno folder"
    research: { engine: none, sources: [] }
    reasoning: "tools/package_backend.py writes into packaging/dist and packaging/build, which Session 74 owns and which hold the exe row 1 measures. PyInstaller's own path flags build the same spec elsewhere, so this session never overwrites a shared artifact. The build includes any uncommitted sibling changes in the tree; it is a local smoke of this session's cli.py, not a release build, and the handoff says so. Two-way: scratch output only."
  - id: D-984
    stage: planning
    question: "Does MEU-154 also need a test through a real pipe, and where does it live?"
    resolution: autonomous
    class: two-way
    mandatory: none
    chosen: "Yes: ui/tests/unit/ready-line-pipe.test.ts runs the real spawnOwned on a node script that writes a ready line in two delayed writes and a repeated ready line, and asserts one publish with the first port. It sits under tests/unit because the Vitest config includes only src and tests/unit."
    source_tag: Local Canon
    precedents:
      - "ui/vitest.config.ts — include src/**/*.test.{ts,tsx} and tests/unit/**/*.test.{ts,tsx}, environment node"
      - "ui/src/main/python-manager.ts:188-194 — spawnOwned with stdout and stderr piped"
    research: { engine: none, sources: [] }
    reasoning: "The synthesized tests prove the reader; the pipe test proves that a real child's output reaches it in pieces and is still read whole, which is how the issue arises. It asserts that the first chunk ended mid-line, so it cannot pass without a real split. An E2E test of the real app lost because in E2E mode the app publishes a fixed test address, and a real launch outside E2E mode meets the single-instance lock while Mat's app runs. Two-way: one test file."
  - id: D-985
    stage: execution
    question: "Does this session's copy of red-check.py take the D-919 pytest header form?"
    resolution: autonomous
    class: two-way
    mandatory: none
    chosen: "Yes. red-check.py's PYTEST_HEADER is ^_+ (.+?) _+\\s*$, Session 76's D-919 form as Session 81 took it (D-974), with the long-title fixture and this session's boundary fixtures: the row-2 pytest Red requiring test_ac_153_1 and test_ac_153_3, a Vitest code frame that quotes createReadyLineReader read as an assertion (Session 78 RULE-2), and the negatives test_ac_153_10, AC-154.10, a missing-reader TypeError and a refused connect."
    source_tag: Local Canon
    precedents:
      - "docs/execution/plans/2026-11-15-convert-settings-drafts/implementation-plan.md D-974 — the newest copy took the D-919 form"
      - "docs/execution/plans/2026-11-15-tooling-test-hermeticity/red-check.py — the D-919 form"
      - "C:/Temp/av-kit/ready-handshake/rh-pre-red-check-selftest.txt — red-check selftest: 43 fixture(s) (14 positive, 29 negative), 0 wrong"
    research: { engine: none, sources: [] }
    reasoning: "Row 2 feeds a pytest receipt whose titles, such as test_ac_153_3_connect_on_ready_line_is_accepted_five_spawns, are long; a title wider than the terminal gets one underscore on a side, which the older ^_{3,} form would miss, so a required failure would go uncounted. Session 79 RULE-2 says a later copy takes the newest holder's form. Keeping the older form lost for that reason. Two-way: one regular expression, pinned by the selftest."
  - id: D-986
    stage: execution
    question: "Row 0's ruff format --check finds gap-tally.py, a plan-time script the gate's py-format step checks, unformatted. What happens to it?"
    resolution: autonomous
    class: two-way
    mandatory: none
    chosen: "Format it with ruff format at row 0, before any other edit: two list comprehensions are wrapped, nothing else changes, and its selftest is run again. The gate's py-format step keeps gap-tally.py."
    source_tag: Local Canon
    precedents:
      - "C:/Temp/av-kit/ready-handshake/rh-base-ruff-format.txt — 1 file would be reformatted (gap-tally.py:27 and :52), 3 files already formatted; cli.py and both test files are clean"
      - "implementation-plan.md §Session gate — py-format runs ruff format --check on cli.py, the two test files and gap-tally.py"
      - "Session 77 RULE-3 — record a pre-existing format finding at row 0 as an execution decision"
    research: { engine: none, sources: [] }
    reasoning: "The finding is in this plan's own script, not in product code, and the change is layout only. Dropping gap-tally.py from py-format lost because it would waive a gate check the plan names (an M-11 question). Leaving it would fail the gate at H1-2. The plan review bound gap-tally.py by hash (8eb4dc0d…), so the handoffs disclose the new hash. Two-way: whitespace in one script."
  - id: D-987
    stage: execution
    question: "AC-154.8 says the pipe test waits for the child's exit event. Which event does the test wait on before it reads what the reader saw?"
    resolution: autonomous
    class: two-way
    mandatory: none
    chosen: "The close event. The test keeps every assertion AC-154.8 names: exit code 0, at least two data events, a first chunk that does not end in a newline, and exactly one publish, for port 13988."
    source_tag: Spec
    precedents:
      - "Node.js child_process docs, event 'close' — emitted after a process has ended and the stdio streams of a child process have been closed; 'exit' may fire while stdio streams are still open"
      - "ui/src/main/python-manager.ts spawnOwned — stdio ['ignore', 'pipe', 'pipe'], so stdout is a pipe the parent reads after the child ends"
      - "implementation-plan.md §Acceptance Criteria AC-154.8 — the assertions the test keeps"
    research: { engine: none, sources: [] }
    reasoning: "The script writes its last chunk and ends at once, so the parent can see exit before the last data event is read; a test that waits only for exit could then count one chunk or no publish and fail for a reason unrelated to the reader. Close comes after both, so the same assertions hold with no race. Waiting for exit lost for that reason. This is a correction inside the approved criterion, not a change to what it accepts (HDP §4a M-8 note). Two-way: one event name in a new test."
```

## Research References

- **uvicorn 0.54.0** (installed in `.venv`): `Config.bind_socket()` creates and binds the socket and returns it without `listen()`; `Server.startup(sockets=…)` runs the lifespan startup first and then calls `loop.create_server(sock=…)`, and asyncio listens when the server starts serving. The gap is the lifespan startup, 13–37 ms on this PC.
- **Winsock `listen`** (Microsoft Learn): calling `listen` on a socket that is already listening succeeds. On Linux a second `listen` only updates the backlog. Either way asyncio's call after `LISTEN_FIRST` is harmless.
- **Windows connect retry:** a connect to a bound socket that is not listening is refused, and Windows retries it after about 500 ms (measured 505–524 ms, `py-connect-pre.txt`). That is why a Python client "works" before the fix and a Node `fetch` does not.
- **`SO_ACCEPTCONN`** is available in Python 3.12 on Windows and reads 0 on a bound socket, 1 on a listening one (`soacceptconn.txt`).

## Planning receipts

All under `C:/Temp/av-kit/ready-handshake/`, read-only against the repository:

| Receipt | What it shows |
|---|---|
| `gap-fetch-pre.txt`, `gap-fetch-pre.jsonl` | Dev backend, `fetch` on the line, 5 runs: 4 refused, 1 `http 200`; port accepted 13–37 ms after the line |
| `gap-cim-pre.txt`, `gap-cim-pre.jsonl` | Dev backend, the CIM query first, 5 runs: 5 `http 200` |
| `gap-fetch-fix.txt`, `gap-fetch-fix.jsonl` | A scratch copy of `cli.py` with the listen call (`fixprobe/patched_cli.py`), 10 runs: 10 `http 200` |
| `gap-tally-planning.txt`, `gap-tally-selftest.txt` | `gap-tally.py` on the three receipts above, and its selftest |
| `py-connect-pre.txt` | Python connect on the line before the fix: 5 of 5, after 505–524 ms |
| `soacceptconn.txt` | `SO_ACCEPTCONN` after bind and after listen |
| `pyinstaller-probe.txt` | PyInstaller 6.22.3 on Python 3.12.12 |
| `rh-decision-probe.txt` | `decision_sources` on the grouping alone reads D-813 to D-817; with the two issues it adds D-810 |
| `rh-eol.txt` | Line endings, sizes, SHA-256 prefixes and git state of every file in §Files Modified and of the packaged exe at `HEAD` `6aaf9b0` |
| `sweep-ready.txt` | Precedent sweep: every reader of the ready line, the capture-picker line reader, the MEU-108 pins |

## Validation stage contract

| Stage | Checks | Where |
|---|---|---|
| Plan review | This plan and `task.md`, against 04 §READY after listen, 06 §READY line buffering, 07:73 and 07:219, and the two issues | `rh-plan-2026-11-15-ready-handshake` |
| Row checks | Each row's validation command | `task.md` |
| Session gate | §Session gate | H1-2 |
| Execution review | The delta from `baseline.sha` in the §Files Modified paths, against AC-153.1 to AC-154.9 | `rh-execution-2026-11-15-ready-handshake` |
