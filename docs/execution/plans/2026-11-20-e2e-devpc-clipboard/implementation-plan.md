---
project: "2026-11-20-e2e-devpc-clipboard"
date: "2026-11-20"
source: "grouping .agent/context/grouping/2026-11-20-e2e-devpc-clipboard-session-grouping.md §3 Session 100; issues E2E-DEVPC-CLIPBOARD-SPECS (D-1299) and E2E-CLIPBOARD-PRIMER-EMPTY (D-1301, watch item)"
meus: []
status: "draft"
template_version: "2.3"
grouping_source: ".agent/context/grouping/2026-11-20-e2e-devpc-clipboard-session-grouping.md"
---

# Implementation Plan: move the dev-PC clipboard steps into the gated stage and guard every other launch against the system clipboard

> **Project**: `2026-11-20-e2e-devpc-clipboard`
> **Build Plan Section(s)**: none. Test files, E2E tooling and the run book only, no MEU (D-1302, grouping §3 Session 100 "(no MEU)").
> **Status**: said to execute (USER_EXPLICIT 2026-11-20 "continue with next prompt" and "continue and commit when the executor finishes", with USER_EXPLICIT 2026-11-18 "make the decisions always the recommenations"). `plan_to_exec_gate: human`: those messages are the execution approval once the plan review approves and no STOP item is open; the plan review returned `changes_required` at round 1 (EDC-R1-1 native paste, EDC-R1-2 Session 99's handoff in `tested_state`), both fixed by D-1331 and D-1330, and was approved at round 2 with no new findings (.agent/context/handoffs/2026-11-20-e2e-devpc-clipboard-plan-critical-review.md); no STOP item is open. Session 100 is the only session of the 2026-11-20 `e2e-devpc-clipboard` grouping (D-1302). Session 98 (`2026-11-20-e2e-clipboard-specs`, `e8207e1`) built the gated stage this plan reuses; Session 99 (`help-quick-start`) runs in parallel in the same tree and is another session's work.

---

## Goal

**Goal anchor:** no dev-PC E2E run writes or reads Mat's system clipboard. The clipboard steps of `C1-5`, `AC-71.15 (b)` and `AC-71.15 (d)` move, with their assertions unchanged, into a second gated file that runs only in the mini-air's gated stage; `W4-3` stops clicking the two MCP copy buttons; and every launch without `AVKIT_E2E_CLIPBOARD_GATED=1` replaces the main-process and renderer clipboard calls with recorders that fail the test with a named message. Six parts:

1. **The moves** (D-1305 to D-1309, `CLIPBOARD_SPLIT` in this session's form). `split-specs.py` builds four files from the `f1ba411` blobs:
   - the new `ui/tests/e2e/copy-system-clipboard.test.ts` (LF) with three tests: `C1-5 console copy writes the visible logs to the clipboard`, `AC-71.15 (b) Copy prompt fills the clipboard with the Codex setup prompt` and `AC-71.15 (d) Copy MCP config puts a non-empty app token on the clipboard`, each clipboard line copied byte for byte;
   - `console-chrome.test.ts` (CRLF) minus `C1-5`'s copy step, the test retitled;
   - `mcp-setup-prompt.test.ts` (CRLF) minus (b) and (d)'s clipboard part, two tests retitled, and `launchApp(token?)` seeding a throwaway token into the scratch app data so (e) keeps its assertion without the clipboard (D-1307);
   - `settings.test.ts` (CRLF) with `W4-3`'s `copy-mcp-btn` and `pin-mcp-btn` clicks retired (D-1308).
   `--check` proves the result, and a file-level guard skips the new file unless `AVKIT_E2E_CLIPBOARD_GATED=1`, as in Session 98's gated file.
2. **The second gated file** (D-1305). `tools/e2e_host/known-failures.json` gains a second `gated` entry. The tool, the launcher and the host scripts already take a list (`run-e2e.ps1:263-288`, `e2e_remote.py:421` `label_gated`, `:987` `gated_summary`) and do not change. `test_ac_11_known_tracked_list` changes in row 3, which names it (Session 97 RULE-1).
3. **The guard** (D-1310, D-1311, D-1313, D-1320 to D-1325, D-1331, `CLIPBOARD_GUARD`). A new preload `ui/tests/e2e/clipboard-guard.cjs` is added to every launch by `electron-app.ts` unless the gate variable is `1`. It replaces a fixed list of twenty `clipboard` names (ten writers, ten readers), found on the object or its prototype chain, with tagged recorders that never call the original, checks each replacement, and fails the launch closed (exit 70) when a name is missing or stays unreplaced (D-1320). On every `dom-ready` it replaces `navigator.clipboard`'s four methods and `execCommand('copy'|'cut'|'paste')`; it denies the two clipboard permissions, wraps `webContents.copy`, `cut`, `paste`, `pasteAndMatchStyle` and `copyImageAt`, and blocks the copy and paste chords (D-1322, D-1324, D-1331). Each recorded call is appended to the launch's guard log when it happens (D-1321). The launch helper reads that log at close and throws `CLIPBOARD_GUARD: ...` when any call was recorded, or when the log is missing, empty, failed or invalid (Session 98 RULE-1); `guard-logs.py` reads every launch's log of a run, so the verdict does not depend on how a spec closes its app (D-1321). Test code only.
4. **The static scan** (D-1312, D-1326, D-1331). A tracked Vitest test fails on any clipboard call, native copy or paste call, copy or paste chord or copy-button click in `ui/tests/e2e` outside the gated files and the guard's own files, each pattern run over the whole file text; `writer-scan.py` is its Python twin for the plan's counts (10 at `HEAD`, 8 after the split, 0 after row 4).
5. **The dev-PC run** (D-1319, `CLIPBOARD_NEVER_DEVPC`). The plan-local `flake-run.py` excludes both gated files and refuses before any run while one of the five source files still calls the clipboard or clicks a writer. Its full run has 238 tests in 30 files, with the guard on and zero recorded calls in every launch's guard log (AC-21).
6. **The acceptance run and the registers** (D-1314 to D-1316). One mini-air run through `tools/e2e_remote.py run` at the final tree, as a snapshot commit on no ref holding `HEAD` plus this session's eleven code and test paths only. The main stage runs with the guard on (only the gated stage sets the variable). The gated outcome is a receipt. `gated-count.py` applies D-1301's bar to the primer file alone. Then `E2E-DEVPC-CLIPBOARD-SPECS` is resolved through `issue-resolve.py`, `E2E-CLIPBOARD-PRIMER-EMPTY` gets the run's verification and stays open unless the tally reaches 5 of 5 (it cannot this session: two runs are counted, so at most three), and grouping row 100 is set to `executed (Session 100)`.

**The split flag** (grouping §3 "Split flag: yes"): not triggered. The flag's condition is that the launch-helper guard "cannot be proven without product code". The plan proved it at plan time on this Electron (42.11.18): a `-r` preload replaced all twenty `clipboard` functions on the same object the main process imports, the patch survived `ready`, and a `dom-ready` script replaced the renderer's methods (`D/probe/probe-result.jsonl`). The probe called no clipboard writer. If row 5 still cannot go green without a product change, that is S3, and the coordinator decides whether to ship the moves alone (D-1317).

**Why.** `E2E-DEVPC-CLIPBOARD-SPECS` (`known-issues.yaml:6103`, D-1299): every dev-PC full run overwrites Mat's clipboard about four times, twice with a JSON block that holds an API token, and Windows clipboard history can keep those entries. Session 98 moved the capture clipboard tests to a gated stage on the mini-air but left these four writers on the dev PC; two of them were missed because they write through a button, not a test-side call. `E2E-CLIPBOARD-PRIMER-EMPTY` (`:3630`, D-1301) is a watch item that closes after five gated `run` outcomes with 2 of 2 expected, counted from `r20261120T215925Z-9ac9adc`; two are counted.

**Grouping §3 Session 100** (`:64-84`):
- The clipboard steps of `C1-5`, `AC-71.15 (b)` and `(d)` and `W4-3` move into the gated stage with their assertions unchanged; the rest of each test stays in its file (D-1303). `AC-71.15 (e)` needs the token that (d) copies, so the plan names how (e) gets it without the clipboard.
- The plan picks the existing gated file or a second one and names every pin it touches.
- `electron-app.ts`, the one launch helper, gets the dev-PC guard (D-1304).
- The run book and `commands.md` name the guard.
- Acceptance: a dev-PC full run passes with the guard on and zero writes; a guard test proves a write in a non-gated launch fails with a named message and that the gated launch is not blocked; one real mini-air run at the final tree, the gated outcome a receipt; Session 98 RULE-1 for every new observation.
- Gate: no product code; no assertion change beyond the moves and the named pins; the clipboard steps never on the dev PC, and `AVKIT_E2E_CLIPBOARD_GATED` never set there; RustDesk read only by the session probe; the home path checked before and after; no host detail in a tracked file.

`:126-128` says Session 100 carries D-1302, D-1303 and D-1304 and reads D-1299 and D-1301 from the register.

**What the code shows (plan-time reads at `HEAD` `f1ba411`):**

- **The four writers** (`edc-plan-writer-scan-head.txt`, 10 hits):
  - `console-chrome.test.ts` (CRLF, 232 lines) `C1-5` (`:77`): `console-copy` click and a main-process `clipboard.readText()` (`:91-92`).
  - `mcp-setup-prompt.test.ts` (CRLF, 165 lines): `AC-71.15` (`:91`) part (b) writes a sentinel, clicks Copy prompt and reads the text back (`:106-114`); `AC-71.15` Advanced (`:126`) part (d) writes a sentinel, clicks `copy-mcp-btn` and reads the token (`:138-150`); part (e) (`:151-161`) checks no setup prompt contains that token.
  - `settings.test.ts` (CRLF, 925 lines) `W4-3`: `copy-mcp-btn` and `pin-mcp-btn` clicks (`:216-217`); both call `copyMcp`, which calls `window.api.copyMcpConfig` (`SettingsPage.tsx:533-536`), a main-process clipboard write. No assertion follows them except the test's `pageErrors` and theme checks.
- **The launch helper.** `electron-app.ts` (LF, 171 lines): `launchElectron` (`:112`) makes a scratch folder, starts `_electron.launch` with `['-r', MAIN_ERROR_WATCH, main, ...args]` and the env from `electronEnv`, and wraps `close` so it waits for the child and then runs `checkMainErrors(dir, log)` (`:86`), which deletes the folder. `electron-env.ts` (LF, 90 lines) exports `MAIN_ERROR_LOG_ENV` (`:20`) and `MAIN_ERROR_WATCH` (`:23`), the precedent for a `-r` preload with a log in the scratch folder.
- **Every spec launches through it.** `writer-scan.py` counts `_electron.launch(` outside `electron-app.ts` as a hit; there are none at `HEAD`.
- **The product's clipboard paths.** Under `AVKIT_E2E=1`, `readClipboard` returns `'pasted'` without touching the OS (`index.ts:405-409`). `pasteCaptureImage` calls `readImage` (`:441-447`), reached only by the gated capture file. The capture `copy_to_clipboard` default is false (`capture-runtime.ts:13`), every E2E fake backend returns false, and `capture-picker.ts:533-535` writes an image only when it is set. The renderer writes through `navigator.clipboard` only in `ConvertPage.tsx:972` and `DownloaderPage.tsx:931`, which no dev-PC spec clicks. `convert-copy-fast` and `convert-copy-reencode` are copy-mode radios, not writers.
- **The Electron facts** (`D/probe/probe-result.jsonl`, a scratch app, no clipboard call):
  - `process.getBuiltinModule('electron')` is undefined in a `-r` preload; `module.require('electron')` works and is the object `require('electron')` returns.
  - `clipboard` has twenty own properties, all writable, configurable and enumerable: writers `_writeFilesForTesting`, `clear`, `write`, `writeBookmark`, `writeBuffer`, `writeFindText`, `writeHTML`, `writeImage`, `writeRTF`, `writeText`; readers `availableFormats`, `has`, `read`, `readBookmark`, `readBuffer`, `readFindText`, `readHTML`, `readImage`, `readRTF`, `readText`.
  - The ESM named import, the default import, `require` and the preload's object are one object, and the patches persist after `ready`.
  - The renderer's `Clipboard.prototype` holds `read`, `readText`, `write` and `writeText` (and `onclipboardchange`); a `dom-ready` `executeJavaScript` replaced them and `Document.prototype.execCommand`.
  - ESLint forbids `require()` in `.cjs` here; `/* global process, module */` with `module.require` lints clean (`D/probe/lint-require.txt`, `lint-module-require.txt`). `main-error-watch.cjs` takes `fs` from `process.getBuiltinModule('node:fs')`.
- **The gated stage.** `run-e2e.ps1` `AvStage -Gated` sets the variable for its child (`:59`), clears it (`:61`), and the script removes it at `:255`; the request's `gated` list is read at `:263-288`. So the mini-air's main stage runs with the guard on, and only the gated stage turns it off.
- **The known list.** `known-failures.json` is LF, 7 lines: `known: []`, `skip: []`, one `gated` entry for `capture-system-clipboard.test.ts`.
- **The pin.** `test_ac_11_known_tracked_list` (`test_e2e_remote.py:1564-1576`) asserts `gated == [("mini-air", "capture-system-clipboard.test.ts")]` (`:1571-1573`). The test file is LF, 3,063 lines.
- **The run book.** `.agent/docs/e2e-remote-host.md` (LF, 341 lines) has `## The gated clipboard stage (Session 98)` at `:222`.
- **The test counts.** `HEAD` lists 239 tests in 30 files (`edc-plan-list-head.txt`); the dev-PC list without the gated file is 237. After rows 1 and 2: 243 in 32 files (the guard spec adds 1, the copy file 3 and its file 1); the dev-PC run and the mini-air main stage have 238 in 30 files; the gated stage has 5 in 2 files (2 primer, 3 copy).
- **The register.** Both issues are `open` with `meu_links: []`. Grouping row 100 (`:105`) is `approved`. `decision_sources` gives 4 ids from the grouping and 7 with the register and both issues (`edc-plan-decisions-1.txt`).
- **The parallel session.** Session 99 (`help-quick-start`) may write `ui/src`, `06-gui.md`, `build-priority-matrix.md`, `docs/BUILD_PLAN.md`, `meu-status.yaml`, `meu-registry.md`, `.agent/skills/README.md`, `current-focus.md`, `metrics.md` and `commands.md` (its folder is never read here). This plan treats those as a foreign class (D-1316). Its folder, its handoffs and its reflection are excluded from `identity.py`'s state by `PEER_PREFIXES` before any read; its tracked writes are recorded by name only, and a peer write after the gate means the gate runs again (D-1330).

## Context Tool Decision

```yaml
context_tool_decision:
  phase: planning_and_execution
  eligible_tools: []
  decision: not_applicable
  eligibility_basis: "graphify-out/ and graphify-out-research/ are absent from P:/av-kit (ls, 2026-11-20). The change is three spec files trimmed and one built by a plan-local script, one new preload, two edits to the launch helper, one Vitest file, one E2E spec, one JSON list, one test file and two docs, with every input read verbatim at plan time (the specs, the launch helper, the product clipboard paths, the tool's gated stage, an Electron probe); that is a bypass class."
  human_message_reference: null
```

## Harness, driver and reviewer route

- **Driver:** Claude Code in VS Code (`.agent/docs/harness-profiles.md`).
  - Commands run in `pwsh` from `P:/av-kit` through `rtk proxy` with the receipt pattern (`.agent/docs/commands.md`).
  - Session receipts go under `C:/Temp/av-kit/e2e-devpc-clipboard/` (`D`), with the prefix `edc`; the remote tool's receipts go under `C:/Temp/av-kit/e2e-remote/<run-id>/`.
  - Vitest, `tsc`, ESLint and Playwright run through `pwsh` with `ELECTRON_RUN_AS_NODE` removed, from `Set-Location 'P:\av-kit\ui'`.
- **The host:** reached only through `tools/e2e_remote.py` (`check`, `run`, and `release` with this session's own run id per the run book). The tool builds every `ssh` and `scp` argv with `-o BatchMode=yes -o StrictHostKeyChecking=yes` and the alias from the untracked local config. No row runs `ssh` itself, changes a known-hosts entry, reads or changes RustDesk, or touches the scheduled task beyond the tool's one `Start-ScheduledTask` per run.
- **Reviewer:** Codex through `tools/Invoke-CodexDispatch.ps1`, with `AGENT_MODEL_REGISTRY_HOME=P:/.agent` and `RECEIPTS_DIR` set (Session 82 RULE-3).
  - Plan loop `edc-plan-2026-11-20-e2e-devpc-clipboard`; execution loop `edc-execution-2026-11-20-e2e-devpc-clipboard`.
  - Caps come from `.agent/review-limits.json`: 6 rounds, turn tokens off.
- **Never** commit, stage or push without Mat's words. The snapshot commit of row 8 is an object on no ref (`SNAPSHOT_NO_REF`). The coordinator commits after the execution review, without a push.

## Handoff Set

| Scope | Canonical handoff |
|---|---|
| `E2E-DEVPC-CLIPBOARD-SPECS` and the PRIMER watch item (no MEU) | `.agent/context/handoffs/2026-11-20-e2e-devpc-clipboard-handoff.md` |

Rolling reviews:

- `.agent/context/handoffs/2026-11-20-e2e-devpc-clipboard-plan-critical-review.md`
- `.agent/context/handoffs/2026-11-20-e2e-devpc-clipboard-implementation-critical-review.md`

The handoff has no MEU in its name, following `2026-11-20-e2e-clipboard-specs-handoff.md` (Session 98, also no MEU).

## Work Packages and Context Lifecycle

| ID | Work | depends_on | context_strategy | durable_outputs |
|---|---|---|---|---|
| WP-1 | Baseline, copied checkers, selftests, the row-0 refusals (row 0) | — | shared | `baseline.*`, `D/baseline-copies/`, `D/edc-baseline-0.txt` |
| WP-2 | The guard tests' Red, then the moves' Green (rows 1 and 2) | WP-1 | shared | The two new test files, the copy file, three edited spec files |
| WP-3 | The pins' Red, then the list, run book and commands doc (rows 3 and 4) | WP-2 | shared | `test_e2e_remote.py`, `known-failures.json`, `e2e-remote-host.md`, `commands.md` |
| WP-4 | The guard's Green and the sweeps (rows 5 and 6) | WP-3 | shared | `clipboard-guard.cjs`, `electron-env.ts`, `electron-app.ts` |
| WP-5 | The dev-PC full run with the guard on (row 7) | WP-4 | shared | `D/edc-foreign-7.json`, the flake-run receipts |
| WP-6 | The snapshot, the mini-air run and the D-1301 count (row 8) | WP-5 | shared | `D/edc-snapshot-8.json`, `D/edc-gated-count-8.txt`, `C:/Temp/av-kit/e2e-remote/<run-id>/` |
| WP-7 | Registers (row 9) and the hub audit (row 10) | WP-6 | shared | Both issues updated, grouping row 100 |
| WP-8 | Closeout (H1, H2) | WP-7 | `compact_continue` | The handoff, the review, the reflection |

## User Review Required

> [!NOTE]
> **Twenty-seven briefs are settled on their recommendations under your hand-over** ('continue with next prompt', 2026-11-20, continuing 'make the decisions always the recommenations', 2026-11-18). The nine with an M item:
>
> - **D-1310 (M-3):** every E2E launch on any machine without `AVKIT_E2E_CLIPBOARD_GATED=1` now fails a test that touches the system clipboard, with a `CLIPBOARD_GUARD:` message. That is a new rule for every later spec: a spec that needs the clipboard must live in a gated file.
> - **D-1311 (M-8):** the guard also stubs the ten clipboard readers, so a dev-PC test cannot read what you copied either. The grouping named only the writers.
> - **D-1312 (M-8):** the static scan becomes a tracked Vitest test that runs in every Vitest run, beside the runtime guard; the grouping offered the scan only as the fallback.
> - **D-1314 (M-6):** D-1301's bar ("2 of 2 expected") was written for one gated file. With five gated tests in two files, a run counts only when the two capture tests both pass under outcome `run`; the three copy tests never decide PRIMER. This session can bring the tally to at most 3 of 5, so PRIMER stays open.
> - **D-1316 (M-6):** the mini-air snapshot holds `HEAD` plus this session's eleven code and test paths only, so Session 99's work in the shared tree never reaches the host; a `ui/src` anchor that Session 99 moves is recorded, not a stop.
> - **D-1322 (M-8):** in every guarded launch the guard also denies the page's two clipboard permissions (`clipboard-read`, `clipboard-sanitized-write`) and patches the page again after each reload. The grouping did not name either.
> - **D-1324 (M-3, M-8):** a guarded launch also records and blocks `webContents.copy` and `cut` and the copy chords (Ctrl+C, Ctrl+X, Ctrl+Insert, Shift+Delete). A later spec that presses one of them outside a gated file fails with `CLIPBOARD_GUARD:`; that widens the new rule beyond the grouping's writers.
> - **D-1330 (M-6):** Session 99's folder, handoffs and reflection are left out of this session's tested state before any file is read, so its untracked handoff no longer lands in a review's `tested_state`. Its tracked writes (`ui/src`, the docs, the registers) still count, as part of one digest over the tracked changes, because the suites read them. No receipt this plan publishes holds a content hash of a Session 99 file; they name its paths only. If Session 99 writes after the gate, the gate's identity check fails and the gate runs again; this session never fails, reverts or stashes Session 99's work.
> - **D-1331 (M-3, M-8):** a guarded launch also records and blocks `webContents.paste`, `pasteAndMatchStyle` and `copyImageAt`, `execCommand('paste')` and the paste chords (Ctrl+V, Ctrl+Shift+V, Shift+Insert), and the static scan refuses them. A later spec that pastes outside a gated file fails with `CLIPBOARD_GUARD:`. Proven on fakes and the scan's selftest only; nothing pastes on the dev PC. It also corrects D-1325: on Windows the Edit menu's copy, cut and paste items most likely go through these same recorders, though no run proves it.
>
> The other eighteen have no M item: a second gated file and its named pin (D-1305, M-7 checked), the moves (D-1306), the seeded token for (e) (D-1307, M-7 checked), `W4-3` without its two copy clicks (D-1308, M-7 checked), the titles (D-1309), the E2E guard spec and 238 (D-1313), the issue outcomes (D-1315), a guard failure on an unexpected test stops the row (D-1317), the run book and `commands.md` (D-1318), the runner's exclusions (D-1319), the guard's fixed name list that fails closed (D-1320), the per-launch guard logs checked without `close` (D-1321, M-3 and M-4 checked), the deterministic AC-10 (D-1323), the Edit menu left as a named residual (D-1325), the widened scan (D-1326), the token-file assertion in (e) (D-1327, M-7 checked), `C1-5`'s route and `try`/`finally` (D-1328) and the skip/only/todo literal check (D-1329).
>
> **Expert pass:** adopted (`edc100-expert-pass.txt`): F1 to F9 as D-1320 to D-1329; F10 (Pin MCP config is no longer clicked by any E2E spec) stays named in D-1308 and the handoff.
>
> **What touches your machines.**
> - The dev PC:
>   - Row 1 and row 5 run one E2E spec, `clipboard-guard.test.ts`, which launches the app and calls each clipboard function only after it has checked that exact function's guard tag (a Python check proves that before rows 1 and 5 run it). A launch whose guard cannot install exits before the app starts.
>   - Row 7 and the gate run the dev-PC full E2E with the guard on (Electron windows open and close for about 20 minutes each). The copy file and the capture clipboard file never run there.
>   - Nothing sets `AVKIT_E2E_CLIPBOARD_GATED` on the dev PC.
> - The mini-air: row 8 runs `tools/e2e_remote.py check` and one `run`, as in Session 98: a source archive is copied there and its existing task is started once, so Electron windows open on that desktop for about 25 minutes. **If you are connected through RustDesk, the clipboard stage is skipped and the run says so; if you connect during it, its result is voided.** The gated stage now also writes the Codex setup prompt and a throwaway MCP config with a scratch token to that desktop's clipboard.
> - Nothing reads or changes RustDesk's settings or service, nothing is stopped or installed, and nothing costs money.
> - Smart App Control, auto sign-in, a self-hosted runner and RustDesk's settings stay yours and are not planned (D-1216). D-1200 stays open and yours.
>
> No STOP item is held for you.

## Proposed Changes

### Single-statement contracts

| Id | Statement |
|---|---|
| `CLIPBOARD_SPLIT` | Session 98's contract in this session's form: `copy-system-clipboard.test.ts` holds exactly the three `NEW_TITLES`, its header, `mcp-setup-prompt.test.ts`'s imports and helpers byte for byte, and the file-level guard; every code line the three kept files lose is in it, except the two `W4-3` clicks (`RETIRED`). Each kept file equals its `f1ba411` blob, in CRLF checkout form (D-1286), with the named edits only. Of the four, only the new file has a `writer-scan.py` hit. |
| `CLIPBOARD_NEVER_DEVPC` | No dev-PC run in this session runs either gated file or sets `AVKIT_E2E_CLIPBOARD_GATED`. `flake-run.py` excludes both by name and refuses with exit 2 before any run while one of `OLD_CLIPBOARD`'s five files still calls the clipboard or clicks a writer. Both gated files skip themselves unless the variable is `1`, which only the gated stage sets. |
| `CLIPBOARD_GUARD` | Every `launchElectron` without `AVKIT_E2E_CLIPBOARD_GATED=1` loads `clipboard-guard.cjs`. It replaces the twenty `NAMES` of Electron's `clipboard`, found on the object or its prototype chain, with tagged recorders that never call the original, and checks each one; a missing or unreplaced name writes a `failed` line and exits 70 before the main script (D-1320). On every `dom-ready` it replaces `navigator.clipboard`'s `read`, `readText`, `write`, `writeText` and `execCommand('copy'|'cut'|'paste')`; it wraps `webContents.copy`, `cut`, `paste`, `pasteAndMatchStyle` and `copyImageAt`, blocks the copy and paste chords and denies `clipboard-read` and `clipboard-sanitized-write` (D-1322, D-1324, D-1331). Each call is appended to the launch's guard log when it happens (D-1321). At `close` the helper throws a message starting `CLIPBOARD_GUARD:` when the log records a call or a failure, or is missing, empty, has no `installed` line or holds an invalid line; `guard-logs.py` applies the same rule to every launch's log of a run, without `close` (AC-21). A gated launch gets no guard argument. |
| `PINNED_SSH`, `NAMED_REFUSAL`, `NEVER_STOP`, `ONE_LOCK`, `CHECK_AND_NAME`, `COMMIT_BOUND`, `REPORT_ONLY`, `KNOWN_NAMED`, `NO_PARTIAL` | Session 96's contracts, unchanged. This session changes no host script and no tool code. |
| `SESSION_PROBE`, `GATED_STAGE` | Session 98's contracts, unchanged. The gated stage runs both gated files in one Playwright child, between the probes. `GATED_OUTCOMES` are `run`, `skipped-connected`, `skipped-undecided`, `voided-connected-during` and `voided-undecided-during`; a gated failure exits 40. |
| `LOCAL_HOST_DETAILS` | The host alias, account, host folder and task path appear only in the untracked local config and in receipts under `C:/Temp/av-kit/`, never in a tracked file, the handoff or a commit message. |
| `KNOWN_EMPTY` | `known-failures.json` keeps `known: []`, `skip: []` and `label` `mini-air`; row 4 appends one `gated` entry after the existing one. |
| `SNAPSHOT_NO_REF` | The mini-air run's commit is `HEAD` plus the named working files, written with a temporary `GIT_INDEX_FILE` and `git commit-tree`, every git call under `GIT_OPTIONAL_LOCKS=0`. Refs, the index, `HEAD` and `git status` are byte-for-byte the same after it, and its author is the noreply identity (Session 97, unchanged). |

### The moves: `ui/tests/e2e/copy-system-clipboard.test.ts` (new, LF), `console-chrome.test.ts`, `mcp-setup-prompt.test.ts` and `settings.test.ts` (CRLF stay CRLF)

`split-specs.py` builds the four files from the `f1ba411` blobs, never from the working tree. Every edit is a named base line range whose first line is pinned (`ANCHORS`), so a different base is a setup error (exit 2).

**The new file** (7,764 bytes, LF, sha256 prefix `0b75576e`):
- a five-line header naming Session 100 and D-1305;
- `mcp-setup-prompt.test.ts` lines 1-14 (imports) and 28-84 (`launchApp`, `openSettings`, `showPrompt` and the rest), byte for byte apart from the line ending;
- the `GUARD` lines after the imports, before the first test: `test.skip(process.env.AVKIT_E2E_CLIPBOARD_GATED !== '1', GUARD_REASON)` with `GUARD_REASON` "system clipboard spec: runs only in the gated stage on the second Windows host", the same reason Session 98's file gives;
- `C1-5 console copy writes the visible logs to the clipboard`: a launch, `C1-5`'s `/settings/app` route (`console-chrome.test.ts:79-86`), so the Console opens as it does there, the console opened as in `C1-5` (`:87-89`), then the copy step `:90-93`, each line byte for byte apart from two more spaces of indent, inside a `try`/`finally` that closes the app, as the file's other tests do (D-1328). The test uses the mcp file's `launchApp`, because the console file's launch helper differs only in its scratch prefix and adds nothing the copy step reads;
- `AC-71.15 (b) Copy prompt fills the clipboard with the Codex setup prompt`: `showPrompt(page, 'codex', 'Codex', 'user')` (`mcp:99`) and (b) (`:106-114`) byte for byte;
- `AC-71.15 (d) Copy MCP config puts a non-empty app token on the clipboard`: the Advanced summary click and (d) (`:136-149`) byte for byte.

**The kept files:**

| File | Bytes after | sha256 prefix | Edits |
|---|---|---|---|
| `console-chrome.test.ts` | 10,372 | `ca33af99` | `:77` becomes one named comment line and `test('C1-5 log-to-file PUTs settings/app', ...`; `:90-93` (the copy step) removed |
| `mcp-setup-prompt.test.ts` | 7,604 | `525c4705` | `import { randomUUID } from 'node:crypto'` added and `writeFileSync` imported (`:2`); `MCP_COPY_PROMPT_BTN` and `MCP_PROMPT_STATUS` (`:10-11`), used only by (b), dropped; `launchApp(token?: string)` (`:28`) writes `${token}\n` to `mcp-token.txt` in its scratch app data when given (D-1307); `:91` retitled; (b) `:106-115` becomes one named comment; `:126-127` retitled and seeded with `const token = randomUUID()`; (d)'s clipboard part `:138-151` becomes one named comment and the (e) comment; after (e)'s loop, one added line asserts that `mcp-token.txt` still equals the seed (D-1327); `readFileSync` imported |
| `settings.test.ts` | 41,933 | `a71bf7ca` | `:216-217` (the two clicks) become one named comment (D-1308) |

`(e)` keeps its loop and its `expect(...).not.toContain(token)` lines byte for byte. Its `token` now comes from the seed, which `readOrCreateMcpToken` (`ui/src/main/index.ts:162-170`) reads from the scratch app data instead of making one; the scratch folder is the test's own `mkdtempSync`, never Mat's app data. After the loop, one added line, ``expect(readFileSync(join(appData, 'mcp-token.txt'), 'utf8')).toBe(`${token}\n`)``, proves the app read the seed and kept it, so (e) checks the token the app serves (D-1327). It is a new assertion in a moved test, named in row 2 and §Test pins (HDP `:158`); no existing assertion line changes.

`split-specs.py --write` refuses unless each kept file equals its base blob in CRLF checkout form and the new file is absent, and writes four temp files before renaming any (`NO_PARTIAL`). `--check` exits 0 only when the four tracked files equal the built ones and the invariants hold: the moved lines present, `NEW_TITLES` once each, the `GUARD` once after the imports, the renamed titles once each, no `writer-scan.py` hit in a kept file, each new test closing its app in a `finally`, the token-file line once in the kept Advanced test, the new file LF only and the kept files CRLF only. Its selftest (13 cases) refuses a changed assertion, a lost moved line, a lost route line, a test without its `try`/`finally`, a lost token-file check, a CRLF new file, an LF kept file, a writer left in a kept file, a new file without its guard, a lost title, a moved anchor and an `--out` folder that already holds a file (`edc-plan-selftest-split-specs.txt`; the built files in `edc-plan-split-out-4.txt`). `tsc` and ESLint pass on the four built files (`edc-plan-split-out-eslint.txt`).

### The second gated file: `tools/e2e_host/known-failures.json` (LF stays LF)

Row 4 appends one entry after the existing one:

```json
{"label": "mini-air", "file": "copy-system-clipboard.test.ts", "reason": "system clipboard spec; runs only when the session probe reads no remote session (D-1305)"}
```

`label_gated` (`e2e_remote.py:421`) returns the gated files in list order, the request carries them to `run-e2e.ps1` (`:263-288`), which passes them all to one `AvStage -Gated` child, and `gated_summary` (`:987`) reports their tests together. The main stage's expected specs are the commit's specs minus `skip` and `gated` (Session 98), so the main stage drops from 31 to 30 files at the final tree, with the guard spec in it. No tool or host-script byte changes; `test_s100_ac_11_*` proves the two-file path on the fake host.

### The guard: `ui/tests/e2e/clipboard-guard.cjs` (new, LF), `electron-env.ts` and `electron-app.ts` (LF stay LF)

**`clipboard-guard.cjs`**, in the shape of `main-error-watch.cjs`:
- `/* global process, module */`; `fs` from `process.getBuiltinModule('node:fs')`; Electron from `module.require('electron')`.
- `MARK = '__avkitClipboardGuard'`, `CONSOLE_TAG = '[avkit-e2e-clipboard-guard]'`, and `NAMES`, the fixed list of the twenty names the plan-time probe found (D-1320): `_writeFilesForTesting`, `availableFormats`, `clear`, `has`, `read`, `readBookmark`, `readBuffer`, `readFindText`, `readHTML`, `readImage`, `readRTF`, `readText`, `write`, `writeBookmark`, `writeBuffer`, `writeFindText`, `writeHTML`, `writeImage`, `writeRTF`, `writeText`.
- `record(log, call, kind)` appends `{"call":"<call>","kind":"write"|"read"}` to the log with `fs.appendFileSync` at the moment of the call, and pushes the call to `globalThis.__avkitClipboardGuardCalls` in main (D-1321, D-1323). The kind is `write` for a name matching `/^_?(write|clear)/`, a copy, a cut, `copyImageAt`, a copy or cut chord and the write permission, else `read`: a paste, `pasteAndMatchStyle`, a paste chord and `execCommand('paste')` read the clipboard (D-1331).
- A recorder is defined with `Object.defineProperty` as a non-enumerable own property of the object it guards and tagged `recorder[MARK] = true`. It records and never calls the original. Readers return empty values of their type: `readText`, `readHTML`, `readRTF`, `readFindText` `''`; `availableFormats` `[]`; `has` `false`; `readImage` `nativeImage.createEmpty()`; `readBuffer` and `read` an empty `Buffer` or `''`; `readBookmark` `{ title: '', url: '' }`.
- `install(electron, log)` returns `{ ok, failed }` (D-1320):
  - for each of `NAMES` it looks on `electron.clipboard` and up its prototype chain (stopping before `Object.prototype`); a name found nowhere is `missing <name>`. Any other function on that chain is replaced too;
  - it defines the tagged recorder as an own property, then checks `clipboard[name] === recorder && recorder[MARK] === true`; a name that fails the check (a non-configurable property, a getter, a frozen object) is `unreplaced <name>`;
  - only when every name is replaced and checked does it write one `{"installed":true,"names":[...]}` line, set `globalThis[MARK] = true` and register the hooks below. Otherwise it writes `{"failed":"<reasons>"}`, no `installed` line and no marker, prints `CLIPBOARD_GUARD: install failed: <reasons>` to stderr, and the preload calls `process.exit(70)`, so the launch fails closed before the app's main script runs.
- The hooks (D-1322, D-1324, D-1331), on `app.on('web-contents-created', (_e, wc) => ...)`:
  - `wc.on('dom-ready', ...)`, on every load and not once, so the page is patched again after `installSettingsSeam`'s reload: `wc.executeJavaScript('(' + rendererGuard + ')(globalThis)')`;
  - `console-message`, in both the event form and the positional form: a message that starts with `CONSOLE_TAG` is parsed and recorded as `renderer <name>`;
  - `wc.copy`, `wc.cut`, `wc.paste`, `wc.pasteAndMatchStyle` and `wc.copyImageAt` become tagged instance recorders (`webContents copy`, `webContents cut`, `webContents paste`, `webContents pasteAndMatchStyle`, `webContents copyImageAt`) that never call the original (D-1324, D-1331). `wc.replace(text)` and `wc.replaceMisspelling(text)` are left alone: they insert the text they are given and read no clipboard (D-1331);
  - `before-input-event` on `keyDown`: Control or Meta with `C` or `X`, Control with `Insert`, and Shift with `Delete` (the copy chords), and Control or Meta with `V`, with or without Shift, and Shift with `Insert` (the paste chords: Ctrl+V, Ctrl+Shift+V, Shift+Insert) are recorded (`input Control+C`, `input Control+V`, `input Shift+Insert` and the like) and `event.preventDefault()` is called, which also stops the Edit menu's accelerator. A plain `V`, `Shift+V` or `Insert` passes (D-1331);
  - once per distinct `wc.session`: `setPermissionRequestHandler` and `setPermissionCheckHandler` deny and record `clipboard-read` and `clipboard-sanitized-write` (`permission <name>`) and allow every other permission. The product sets neither handler at `f1ba411` (`ui/src`, grep), so the guard's replace none.
- `rendererGuard(g)` returns at once when `g[MARK]` is already set, so a second `dom-ready` on the same document changes nothing. Otherwise it replaces `Clipboard.prototype.read`, `readText`, `write` and `writeText` with tagged recorders that `console.log(CONSOLE_TAG + JSON)` and resolve empty, wraps `Document.prototype.execCommand` so `'copy'`, `'cut'` and `'paste'` record and return `false` (D-1331), and sets `g[MARK] = true` in the page.
- It exports `{ install, rendererGuard, NAMES, MARK, CONSOLE_TAG }`. It installs itself only when `process.versions.electron` is set and `process.type === 'browser'`, reading the log path from `AVKIT_E2E_CLIPBOARD_GUARD_LOG` and deleting that variable, so a Vitest `require` installs nothing.

**Where the logs live** (D-1321). `clipboardGuardLogPath(scratch, diag, launch)` names a launch's log. With a diag folder (`AVKIT_E2E_DIAG_DIR`) it is `<diag>/clipboard-<launch>.jsonl`, beside the `phases.jsonl` rows of the same launch id (`process.pid * 1000 + launches`, `electron-app.ts:116`), and it is kept; without one it is `<scratch>/clipboard.jsonl`, deleted with the scratch folder at close. The diag folders are known by name, so no check searches for them:
- `flake-run.py`'s `<out>/epf-<label>-<i>-diag-<inv>`, with `--out` defaulting to `C:/Temp/av-kit/e2e-devpc-clipboard/flake`, each named on its receipt's `run <i> files:` and `rerun files:` lines (row 7 and the gate);
- row 5's `D/edc-diag-5-<stamp>`;
- on the mini-air, the host's diag folder, which comes back as `<run dir>/host/diag` (row 8). The gated stage runs unguarded and writes no log.

**`electron-env.ts`** adds five exports:
- `CLIPBOARD_GUARD_WATCH = resolve(here, 'clipboard-guard.cjs')`;
- `CLIPBOARD_GUARD_LOG_ENV = 'AVKIT_E2E_CLIPBOARD_GUARD_LOG'`;
- `clipboardGuardArgs(env)`: `['-r', CLIPBOARD_GUARD_WATCH]`, or `[]` when `env.AVKIT_E2E_CLIPBOARD_GATED === '1'`;
- `clipboardGuardLogPath(scratch, diag, launch)`: the path above;
- `clipboardGuardVerdict(text: string | null): { ok: boolean; message: string }`:
  - `null`: `CLIPBOARD_GUARD: the guard log is missing`;
  - a `failed` line: `CLIPBOARD_GUARD: the guard failed to install: <reasons>`;
  - empty, or no `installed` line: `CLIPBOARD_GUARD: the guard was never installed`;
  - a line that is not a JSON object: `CLIPBOARD_GUARD: invalid guard log line <n>`;
  - one or more calls: `CLIPBOARD_GUARD: clipboard call(s) in a launch without AVKIT_E2E_CLIPBOARD_GATED=1: <call>, <call>` (in log order, e.g. `main writeText, renderer writeText, webContents copy`);
  - an `installed` line and no call: ok.

**`electron-app.ts`** (`launchElectron`, `:112`):
- `const guardArgs = clipboardGuardArgs(process.env)` and `const guardLog = clipboardGuardLogPath(dir, diag, launch)`;
- the args become `['-r', MAIN_ERROR_WATCH, ...guardArgs, main ?? DEFAULT_MAIN, ...(args ?? [])]`;
- the env gets `[CLIPBOARD_GUARD_LOG_ENV]: guardLog` only when `guardArgs` is not empty;
- in the `close` wrapper, after `waitForExit` and before `checkMainErrors` deletes the folder, the helper reads the guard log (`null` when absent) when the guard was on; then it runs `checkMainErrors` inside a `try`/`catch`; then it throws one `Error` whose message joins the guard verdict's message and the main-error message when either failed. The main-error check keeps its message.

**The verdict without `close`** (D-1321). The throw at `close` is an early signal, not the only one. Several specs swallow or race `close`: `capture-inbox.test.ts:1941` (`.close().catch`), `electron-harness.test.ts:93` and `:113`, `main-rejection-watch.test.ts:72` and `:91`, and the `closeBounded` helpers of `capture-settings-draft`, `convert-browse-mount`, `convert-queue-labels`, `downloader-advanced-gap` and `help-f1-mount`. A call recorded there would not fail its test. Because the preload appends each call when it happens, `guard-logs.py` reads the logs themselves:
- at row 5 (`--diag` on row 5's folder);
- at row 7 and the gate's `guard-logs` step (`--receipt`: every run and rerun folder the flake-run receipt names);
- at row 8 and the gate's `guard-logs-remote` step (`--diag <run dir>/host/diag`).

It fails on any `call` or `failed` line outside the AC-10 launch, on an AC-10 launch without exactly its three calls, on a finished non-gated launch without exactly one `installed` line, on an invalid line and on a log no launch names, and it counts and prints the launches without an `installed` line (AC-21). An install failure leaves a launch with a `launch-start` row and no `launch-end` row, and its `failed` line fails the check.

**Why it is safe on the dev PC.** The recorders never call the originals, so a guarded launch cannot change or read the OS clipboard, and a launch whose guard did not fully install exits 70 before the app's main script runs (D-1320). The guard spec calls each clipboard function only inside its own `evaluate`, whose first statement throws unless `Reflect.get(<that function>, '__avkitClipboardGuard') === true`: the tag of that exact function, not a global marker. So even its Red, before the guard exists, cannot write, and a partly installed guard cannot let a call through. Rows 1 and 5 check that shape with Python before they run the spec; at plan time the check passes a good spec and refuses a global-marker check, another function's tag, an unchecked call, a call outside `evaluate`, two calls under one check and fewer than three calls; since D-1331 it also counts `wc.paste`, `pasteAndMatchStyle` and `copyImageAt` as calls, refusing an unchecked `wc.paste()` or `copyImageAt()` and passing a tag-checked one (`edc-plan-shape-check.txt`, 10 of 10).

**Residual risks** (named, not closed):
- The Edit menu used with the mouse. The product sets no application menu, so Electron's default menu has `copy`, `cut`, `paste` and `pasteAndMatchStyle` role items. On Windows and Linux, Electron 42.11.18's role code (`edc-plan-electron-roles.txt`, read from the code embedded in `electron.exe`) runs each one as a call on the focused `webContents` object (`webContentsMethod: e=>e.paste()` and the like, `registerAccelerator: false`), so the instance recorders on `wc.copy`, `cut`, `paste` and `pasteAndMatchStyle` most likely catch a mouse click on the menu too. That is not run-proven: no spec clicks the menu bar, and no plan-time probe may copy or paste. On macOS these roles are native selectors that bypass the recorders. The chord block stops the menu's accelerators. `Menu.setApplicationMenu(null)` was not taken: it would change the window's menu bar, layout and accelerators in every guarded run (D-1325, corrected by D-1331).
- A renderer `execCommand('copy')` or `execCommand('paste')` between the navigation's commit and `dom-ready`, before the page is patched. The async API in that window is denied by the permission handlers, and no product path copies at page load.
- That Playwright's keyboard input reaches `before-input-event` is proven only on the unit fake. No dev-PC spec sends a copy or paste chord, and the static scan refuses one (D-1326, D-1331). The paste refusal is proven on fakes and by the scan's selftest only; no real paste or clipboard read runs on the dev PC (D-1331).
- A later product `setPermissionRequestHandler` or `setPermissionCheckHandler` on the same session would replace the guard's.
- That `app.on('web-contents-created')` registered from a `-r` preload fires for the main window is proven only at row 5, by AC-10's renderer and `webContents` calls; the plan-time probe registered it from the main script.

### The static scan: `ui/tests/unit/e2e-clipboard-guard.test.ts` (new, LF)

One Vitest file with five tests, each asserting its target's type or existence first so that before Green it fails by assertion:
- `S100 AC-5` reads every `*.ts`, `*.cjs` and `*.mjs` under `ui/tests/e2e` but the gated files that `known-failures.json` names and the guard's own two files, and fails on any hit of the `writer-scan.py` patterns. Each pattern runs over the whole file text, so a chain split across lines still matches (D-1326). A hit is:
  - a test-side `clipboard.read*`, `write*`, `clear`, `has` or `available*` call; any `navigator.clipboard`; `execCommand('copy'|'cut'|'paste')`; `webContents.copy(` or `cut(`; any `.copyImageAt(`; any `.paste(` and any `pasteAndMatchStyle` (D-1331);
  - a copy or cut chord in a `press(`: Control, Meta or ControlOrMeta with `C`, `X`, `KeyC`, `KeyX` or `Insert`, and `Shift+Delete`, any case;
  - a paste chord in a `press(`: Control, Meta or ControlOrMeta with `V` or `KeyV`, with or without Shift (`Control+V`, `Control+Shift+V`, `Shift+Control+v`), and `Shift+Insert`, any case; a plain `v`, `Shift+V`, `Insert` or `Control+Verbose` is not a hit (D-1331);
  - a click, double click, press or tap on a copy locator: a test id or a CSS `locator('...')` string holding `copy`, a test-id constant named for copy, `WRITER_IDS`, or a role, text, label or title locator whose argument holds `copy` as a word start (`/copy/i` included); or on a variable bound to such a locator;
  - `_electron.launch(` outside `electron-app.ts` and `electron-env.ts`, which are exempt from that kind only.

  It reads the gated list from the JSON, so it fails at row 1 with 10 hits, still fails after row 2 with the copy file's 8 (not yet listed), and passes after row 4. The counts were re-measured with the widened patterns and again with the paste kinds of D-1331: still 10, 8 and 0 (`edc-plan-writer-scan-head.txt`, `-split.txt`, `-after.txt`; selftest 56 of 56, `edc-plan-selftest-writer-scan.txt`). No file outside the gated ones pastes: the gated `capture-system-clipboard.test.ts` presses `Control+V` at `:559`, `:576` and `:592` and is allowed as a gated file, and `copy-system-clipboard.test.ts` holds no paste (`edc-plan-writer-scan-gated-files.txt`). `tts-generate.test.ts:384` clicks `paste-btn`, which is not a hit: under `AVKIT_E2E=1` the product's `readClipboard` returns `'pasted'` without touching the OS (`index.ts:405-409`), and the main-process `clipboard.readText` it would otherwise call is guarded. `wc.replace` and `replaceMisspelling` are not hits: they read no clipboard. A locator built by a helper function, or a test id assembled at run time, is the runtime guard's job.
- `S100 AC-6`: `clipboardGuardArgs` and `clipboardGuardLogPath`.
- `S100 AC-7`: `clipboardGuardVerdict`, each case above.
- `S100 AC-8`: `install` on fake `electron` objects whose clipboard functions throw if called, with a fake `app`, `nativeImage` and `webContents`:
  - a clipboard with every name as an own property, and one with a writer on its prototype: all replaced, checked, `installed` logged;
  - one with a name missing, and one with a name that cannot be replaced: `{ ok: false }`, a `failed` line naming it, no `installed` line and no marker;
  - the hooks: `dom-ready` registered with `on`, so a second load patches again; on a fake `wc` whose `copy`, `cut`, `paste`, `pasteAndMatchStyle` and `copyImageAt` throw if called, each replaced by a recorder with its tag checked (`Reflect.get(wc.paste, MARK) === true`), called once, logged (`webContents paste` and the others, paste as `read`) and never reaching the original; the fake's `replace` and `replaceMisspelling` left the same function objects; the seven chords (Control+C, Control+X, Control+Insert, Shift+Delete, Control+V, Control+Shift+V, Shift+Insert) recorded and prevented, and the negative oracles a plain `v`, `Shift+V` and `Insert` neither recorded nor prevented (D-1331); the two permissions denied and recorded, another allowed;
  - `rendererGuard` on a fake `g` with a fake `Clipboard.prototype` and `Document.prototype`, run twice to show it is idempotent; `execCommand('paste')` recorded and `false`, `execCommand('bold')` passed through.
- `S100 AC-9`: `electron-app.ts`'s source holds `clipboardGuardArgs(`, `clipboardGuardLogPath(` and `clipboardGuardVerdict(`, the guard-log read comes before `checkMainErrors(` in `close`, and `checkMainErrors(` sits inside a `try`.

It imports `* as env from '../e2e/electron-env'` and loads the `.cjs` through `createRequire` only after `existsSync`. It holds none of the eight literals that `AC-43.13` and `AC-44.13` forbid in `ui/tests/unit` (D-1329).

### The E2E guard spec: `ui/tests/e2e/clipboard-guard.test.ts` (new, LF)

One test, `S100 AC-10 a guarded launch records main, renderer and webContents clipboard calls and fails at close with a named message`:
- skips when `AVKIT_E2E_CLIPBOARD_GATED === '1'` (so the gated stage never runs it, and it is not in the gated list);
- launches through `launchElectron`, asserts the main marker (`app.evaluate(() => globalThis.__avkitClipboardGuard === true)`) first, then polls the renderer marker on the first window, up to 10 s;
- makes three calls, each inside its own `evaluate` whose first statement is `if (Reflect.get(<callee>, '__avkitClipboardGuard') !== true) throw ...` for that exact function (D-1320): `clipboard.writeText` in main, `navigator.clipboard.writeText` in the page, and `wc.copy()` on the first window's `webContents` in main;
- waits with `expect.poll` on `app.evaluate(() => globalThis.__avkitClipboardGuardCalls)`, bounded at 10 s, until main holds `main writeText`, `renderer writeText` and `webContents copy`, so the renderer's console message has arrived before close (D-1323);
- expects `app.close()` to reject with a message containing `CLIPBOARD_GUARD:`, `main writeText`, `renderer writeText` and `webContents copy`.

Its title and its own output never contain `CLIPBOARD_GUARD:`, so the gate's no-guard-line check over the full run reads only failures. It is in `ALLOWED_FILES` of the static scan, and `guard-logs.py` expects exactly these three calls in its launch's log. At Red it fails on the main-marker assertion; at Green it passes.

### The run book: `.agent/docs/e2e-remote-host.md` (LF stays LF)

A new `## The dev-PC clipboard guard (Session 100)` section after the Session 98 section (`:222`), and one sentence in the Session 98 section that the gated stage now runs two files. It names: `copy-system-clipboard.test.ts`; `CLIPBOARD_GUARD`, its preload and its `CLIPBOARD_GUARD:` message; that only the gated stage sets `AVKIT_E2E_CLIPBOARD_GATED`, so the mini-air's main stage runs guarded; that the readers return empty values; the static scan; and the D-1301 counting rule (only the capture file's two tests count). `test_ac_19_*` and `test_s98_ac_16_*` keep passing; `test_s100_ac_18_*` reads the new section.

### `.agent/docs/commands.md` (CRLF stays CRLF)

Two lines beside Session 98's two (D-1318): any E2E launch without `AVKIT_E2E_CLIPBOARD_GATED=1` fails a test that touches the system clipboard with `CLIPBOARD_GUARD:`; a spec that needs the clipboard belongs in a gated file named in `tools/e2e_host/known-failures.json`. Session 99 may also write this file: row 4 re-reads it first and inserts after a line it finds by text, never by number.

### The tests

| File | Cases | Row (Red, Green) |
|---|---|---|
| `ui/tests/unit/e2e-clipboard-guard.test.ts` | `S100 AC-5` to `S100 AC-9` | 1, 4 (AC-5) and 5 (AC-6 to AC-9) |
| `ui/tests/e2e/clipboard-guard.test.ts` | `S100 AC-10` | 1, 5 |
| `tests/tooling/test_e2e_remote.py` | `test_s100_ac_11_known_two_gated_files`, `test_s100_ac_11_run_carries_both_gated_files`, `test_s100_ac_18_run_book_session_100`, `test_s100_ac_18_commands_names_the_guard`; `test_ac_11_known_tracked_list` changed | 3, 4 |

`test_s100_ac_11_run_carries_both_gated_files` runs the fake host with a two-entry `gated` list and asserts the request's `gated` holds both files in order and that a passing gated report of five tests gives outcome `run`, `files` with both names and exit 0.

### Test pins

`pins-check.py` enforces this list over `tests/tooling/test_e2e_remote.py`, statement by statement (`ast`), against the row-0 copy: `MAY_CHANGE` is `{"<docstring>", "test_ac_11_known_tracked_list"}`; `NEW_NAMES` is `{"GATED_FILES_S100"}`; new functions must start with `test_s100_` or `_s100_`; nothing is removed, and no import or class is added. Its selftest passes (`edc-plan-selftest-pins-check.txt`).

| Pin | What it checks | Old value | New value |
|---|---|---|---|
| `test_e2e_remote.py:1-14` (the module docstring) | The file's description | Ends with the Session 98 sentence | **Added text (named):** one sentence before the closing `"""`: Session 100 (`docs/execution/plans/2026-11-20-e2e-devpc-clipboard`) adds the second gated file and the guard's run-book section (AC-11 and AC-18; D-1305, D-1318); each new case asserts its file or text first |
| `test_e2e_remote.py:1564-1576` (`test_ac_11_known_tracked_list`), `gated` at `:1571-1573` | The tracked list | `[("mini-air", "capture-system-clipboard.test.ts")]` | **Changed value (M-7, named; D-1305):** `[("mini-air", "capture-system-clipboard.test.ts"), ("mini-air", "copy-system-clipboard.test.ts")]`. `known == []`, `skip == []`, every reason present and `Path(m.KNOWN_FILE) == KNOWN` are unchanged |
| `GATED_FILES_S100` (new module constant) | The two gated names in order | — | `("capture-system-clipboard.test.ts", "copy-system-clipboard.test.ts")` |
| `test_e2e_remote.py` `test_s98_*` and `test_ac_*` (all others) | Session 96 and 98 behaviour | — | Unchanged and passing |
| `console-chrome.test.ts:77` title | `C1-5` | `C1-5 copy writes clipboard and log-to-file PUTs settings/app` | `C1-5 log-to-file PUTs settings/app` (D-1309); its kept assertions unchanged |
| `mcp-setup-prompt.test.ts:91` title | `AC-71.15` (a)(c) | `AC-71.15 Codex prompt carries execPath and app data, Copy prompt fills the clipboard, Claude Desktop disables scope` | `AC-71.15 Codex prompt carries execPath and app data, Claude Desktop disables scope` |
| `mcp-setup-prompt.test.ts:126` title | `AC-71.15` Advanced | `AC-71.15 Advanced starts closed and holds Copy MCP config; no setup prompt contains the token it copies` | `AC-71.15 Advanced starts closed and holds Copy MCP config; no setup prompt contains the app token` |
| `mcp-setup-prompt.test.ts:28` `launchApp` | The scratch launch | `launchApp()` | `launchApp(token?: string)` seeding `mcp-token.txt` in the scratch app data when given (D-1307); called with no argument by the other test |
| `mcp-setup-prompt.test.ts:138-151` (d) and (e) | The token's source | `const token` read from the clipboard after a `copy-mcp-btn` click | `const token = randomUUID()` before launch; (d)'s clipboard steps moved; (e)'s assertions unchanged |
| `mcp-setup-prompt.test.ts` (e), after its loop | The token (e) checks is the one the app serves | — | **Added assertion (named; D-1327, HDP `:158`, M-7 checked):** ``expect(readFileSync(join(appData, 'mcp-token.txt'), 'utf8')).toBe(`${token}\n`)``; no existing assertion line changes |
| `settings.test.ts:216-217` (`W4-3`) | Actuation without page errors | Two clicks: `copy-mcp-btn`, `pin-mcp-btn` | Removed, one named comment (D-1308). No assertion of the test changes; Copy MCP config is still clicked in the gated (d), and Pin's click is no longer actuated by any E2E spec (named in the handoff) |
| `ui/tests/unit/queue-primitives.test.ts:793` (`AC-43.13`), `queue-card.test.ts:756` (`AC-44.13`) | Among their checks, a sweep of every file under `ui/tests/unit` for the eight literals `test.skip`, `it.skip`, `describe.skip`, `test.only`, `it.only`, `describe.only`, `test.todo` and `it.todo` (`queue-primitives.test.ts:829-844`, `queue-card.test.ts:773-777`) | — | Unchanged and passing with the new unit file, which holds none of them (row 6's literal check, AC-22, D-1329); the full Vitest suite runs at row 6 and in the gate before any snapshot (Session 97 RULE-2) |
| `ui/tests/unit/e2e-harness.test.ts` | The E2E harness files | — | Unchanged and passing |

Any other existing test that fails after Green is S3. A Green that needs a test change not named here is S3 and an M-7 hit: stop.

### Plan-local files (written at plan time)

This folder already holds the files below. All are LF, the Python ones ruff-clean, and none holds a host detail or the home path.

| File | Purpose | Rows |
|---|---|---|
| `split-specs.py` | `CLIPBOARD_SPLIT`: `--out`, `--write`, `--check`, `--selftest` | 0, 1, 2, H1-2 |
| `writer-scan.py` | The static scan's Python twin, widened by D-1326: `[--expect N]`, `--root DIR`, `--gated NAME`, `--selftest` (56 cases, the paste kinds of D-1331 included) | 0, 1, 2, 4, H1-2 |
| `guard-logs.py` | The guard's verdict without `close` (D-1321, AC-21): `--diag DIR`, `--receipt FILE [--out DIR]`, `--gated NAME`, `--selftest` (19 cases) | 0, 5, 7, 8, H1-2 |
| `guard-check.py` | Both gated files skip unless the variable is `1`, from Playwright's `--list` with the variable removed: `--list OUT`, `--judge OUT` (32 files, 243 tests, the five gated tests skipped with `GUARD_REASON`), `--selftest` | 0, 2, H1-2 |
| `gated-count.py` | D-1301's count for two gated files: `--run DIR [--prior 2]`, `--selftest` | 8, H1-2 |
| `pins-check.py` | §Test pins, with its selftest | 0, 3, 4, H1-2 |
| `flake-run.py` | The dev-PC runs: `EXCLUDED` both gated files, `OLD_CLIPBOARD` five files (D-1319) | 0, 1, 2, 7, H1-2 |
| `snapshot-commit.py` | `SNAPSHOT_NO_REF`, Session 97's in logic | 0, 8, H1-2 |
| `host-details-scan.py` | `LOCAL_HOST_DETAILS`, key names only | 0, 9, H1-2, H1-6 |
| `baseline.ps1`, `session-gate.ps1` | Row 0 and the gate | 0, H1-2 |
| `identity.py`, `eol-check.py`, `red-check.py`, `host-load.ps1` | Copied from Session 98 (Session 96 RULE-3); `identity.py` adds `PEER_PREFIXES`, which drops Session 99's folder, handoffs and reflection by pathspec and by name before any read, with selftest regressions (D-1330); `red-check.py`'s `DECLARED_NEW` names `clipboardGuardArgs`, `clipboardGuardVerdict`, `CLIPBOARD_GUARD_WATCH`, `CLIPBOARD_GUARD_LOG_ENV`, `clipboardGuardLogPath`, `clipboard-guard.cjs` and `clipboard-guard` (the pytest Red of row 3 asserts `GATED_FILES_S100` by value, so it needs no entry) | 0, 1, 3, H1-2 |
| `issue-resolve.py` | Copied from Session 98; `RESOLVE_KEYS` unchanged | 9 |

Each copy changes only its scope lists, its scratch folder and its docstring's first paragraph, and its selftest passes at plan time (`edc-plan-selftest-*.txt`). Session 98's fixes are carried: the stamp `yyyyMMdd-HHmmss` (D-1285), `split-specs.py` compares the CRLF checkout form (D-1286), and ruff runs on `packages/`, `tests/` and the plan's Python (D-1287).

**No partial file.** `split-specs.py --write` writes four temp files and renames them only when all four are written. An existing `--out` file refuses, and so does an existing `snapshot-commit.py --out` (the row-0 sentinel). The known list is written by one `os.replace` from a temporary file in the same folder.

### Boundary Inventory

| Boundary | Input | Owner | Refusal |
|---|---|---|---|
| The moves | The `f1ba411` blobs of the three spec files | `split-specs.py` | `--write` refuses unless each kept file equals its base in checkout form and the new file is absent; `--check` exits 1 on any difference; exit 2 on a moved anchor (AC-1 to AC-4) |
| Dev-PC runs | The spec list | `flake-run.py` | Exit 2 before any run while an `OLD_CLIPBOARD` file has a hit; a count other than `--expect-total` fails (AC-12, AC-14) |
| The guard's launch | `process.env.AVKIT_E2E_CLIPBOARD_GATED` | `clipboardGuardArgs` | None: `1` is the only value that turns it off (AC-6) |
| The guard's install | `NAMES` on `electron.clipboard` and its prototype chain | `install` | A missing or unreplaced name: a `failed` line, no `installed` line, no marker, exit 70 before the main script (AC-8, AC-21) |
| The guard's log | `clipboardGuardLogPath`: `<diag>/clipboard-<launch>.jsonl`, else `clipboard.jsonl` in the scratch folder | `clipboardGuardVerdict` at `close` | Missing, empty, a `failed` line, no `installed` line, an invalid line, or any call: a thrown `CLIPBOARD_GUARD:` error at `close`, joined with any main-error message (AC-7, AC-9, AC-10) |
| A run's guard logs | The diag folders a flake-run receipt names, or one `--diag` folder | `guard-logs.py` | Exit 1 on a `call` or `failed` line outside the AC-10 launch, an AC-10 launch without exactly its three calls, a finished non-gated launch without exactly one `installed` line, an invalid line or an orphan log; exit 2 on a setup failure (AC-21) |
| Native copies, pastes and permissions | `wc.copy`, `cut`, `paste`, `pasteAndMatchStyle` and `copyImageAt`, a copy or paste chord, a `clipboard-read` or `clipboard-sanitized-write` request or check | `install`'s hooks | Recorded and blocked: the method never calls the original, the chord prevented, the permission denied; `wc.replace` and `replaceMisspelling` read no clipboard and are left alone; the Edit menu clicked with the mouse is a named residual, most likely caught on Windows by the same recorders (AC-8; D-1324, D-1325, D-1331) |
| The renderer's calls | `console-message` events with `CONSOLE_TAG` | `install`'s listener | An untagged message is ignored; a tagged one that is not JSON is logged as a `renderer <unparsed>` call, which fails the verdict (AC-8) |
| The static scan | Every file under `ui/tests/e2e` but the gated and guard files | `S100 AC-5`, `writer-scan.py` | A hit fails; an unreadable known list is a setup failure (exit 2 for the script) (AC-5) |
| The known list | `known-failures.json` | `load_known`, `_run` | Session 98's: 32 on a malformed `gated` entry, a missing reason, an absent file, or a file both skipped and gated (AC-11) |
| Remote run | The snapshot commit | `tools/e2e_remote.py run` | Its exit table: 20 to 24 (S10); 10, 11, 25 to 34 (S11); 40 (S12 unless a primer-only failure) |
| The D-1301 count | The run folder's `summary.json` and gated report | `gated-count.py` | Exit 1 on a missing, empty or invalid observation, a `run` outcome without a report, or a test of another file (Session 98 RULE-1) (AC-16) |
| Snapshot commit | `HEAD`, the eleven named paths | `snapshot-commit.py` | Session 97's refusals |
| Registers | `known-issues.yaml`, the grouping row | `issue-resolve.py`, `tools/issue_triage.py` | Each tool's own; a register hash other than row 0's is S4 |
| Receipts | `D/` and `C:/Temp/av-kit/e2e-remote/<run-id>/` | Each row | A receipt parsed later is written by Python (Session 95 RULE-2/3) |

**M-4: none.** No API route, OpenAPI document, MCP tool shape, backend service, persisted setting, database schema, exit code or summary key changes. The guard's preload, its env name and its log live under `ui/tests/e2e` and a launch's scratch or diag folder; exit 70 is the test preload's refusal in a test launch, not a product exit code, and `guard-logs.py` is plan-local. **No product code changes:** `ui/src`, `packages/`, `mcp-server/src` and `backend/` are untouched; `ui/src/main/index.ts` is read only. Nothing reads user data: the specs use a scratch `AVKIT_APP_DATA`, the seeded token is a fresh `randomUUID()` in that scratch folder, and the guard reads no file but its own log.

### Acceptance Criteria

The AC ids are this plan's own: there is no MEU, so they are `AC-1` to `AC-22`, as Sessions 96 and 98's were. The ids quoted from spec titles (`C1-5`, `AC-71.15`, `W4-3`, `AC-88.12`, `AC-132.23`, `AC-43.13`, `AC-44.13`) belong to their own MEUs and sessions (Session 83 RULE-1); this plan moves or names their lines and never changes an assertion. The `S100 AC-n` prefixes in test titles are this plan's.

| AC | Type | Description | Source | Negative Test |
|---|---|---|---|---|
| AC-1 | row | `CLIPBOARD_SPLIT`: after row 2, `split-specs.py --check` exits 0 and the four tracked files' SHA-256 equal the plan-time values (`0b75576e…` new, `ca33af99…`, `525c4705…`, `a71bf7ca…`; `edc-plan-split-out-4.txt`) | Grouping §3 Session 100; D-1303, D-1306, D-1328 | At rows 0 and 1, `--check` exits 1 naming the new file absent and the three kept files differing |
| AC-2 | row | The new file holds the three `NEW_TITLES` once each, the `GUARD` once after its imports, and every moved clipboard line byte for byte; `guard-check.py --list` lists 243 tests in 32 files with the five gated tests skipped with `GUARD_REASON` and every other test listed to run | D-1305, D-1309 | At row 0, `guard-check.py --list` exits 1 (one gated file, 239 tests) |
| AC-3 | row | `W4-3` loses only its two clicks, replaced by one named comment; every other line of `settings.test.ts` equals its base; `writer-scan.py` has no hit in it after row 2 | D-1308 | `writer-scan.py --expect 10` at row 0 counts `settings.test.ts:216` and `:217` |
| AC-4 | row | `AC-71.15 (e)` keeps its assertion lines byte for byte and takes its token from `launchApp(token)`'s seed; one added line asserts that `mcp-token.txt` still equals the seed after the prompts; the kept test passes in row 7's dev-PC run with no clipboard call | D-1307, D-1327 | `split-specs.py --selftest` refuses a changed assertion and a lost token-file check; at row 0 the token comes from a clipboard read (`mcp-setup-prompt.test.ts:143`, a `writer-scan.py` hit) |
| AC-5 | test | `S100 AC-5`: no clipboard call, native copy or paste call (`.paste(`, `pasteAndMatchStyle`, `.copyImageAt(`, `execCommand('paste')`), copy or paste chord (`Control+V`, `Control+Shift+V`, `Shift+Insert` and the copy chords) or copy click in `ui/tests/e2e` outside the gated files and the guard's files, each pattern over the whole file text. Its fixtures hold one source line of each paste kind, each a hit, and the negatives a plain `v`, `Shift+V`, `Insert`, `Control+Verbose`, a `paste-btn` click, `wc.replace(` and `replaceMisspelling(`, none a hit; `writer-scan.py --selftest` holds the same cases (56 of 56) | D-1312, D-1326, D-1331 | Fails by assertion at row 1 (10 hits) and after row 2 (8, the copy file not yet gated); passes after row 4. A copy of `writer-scan.py` without the paste kinds fails 12 of its 56 selftest cases (`edc-plan-writer-scan-mutant.txt`) |
| AC-6 | test | `S100 AC-6`: `clipboardGuardArgs` gives `['-r', CLIPBOARD_GUARD_WATCH]` for an unset, empty, `0` or `true` value and `[]` only for `1`; `CLIPBOARD_GUARD_WATCH` names an existing `clipboard-guard.cjs`; `clipboardGuardLogPath` gives `<diag>/clipboard-<launch>.jsonl` with a diag folder and `<scratch>/clipboard.jsonl` without one | D-1310, D-1321 | Fails by assertion at row 1 (the export is not a function) |
| AC-7 | test | `S100 AC-7`: `clipboardGuardVerdict` gives the missing, failed-install, never-installed and invalid-line messages, names each call in log order, and passes only an `installed` line with no call | D-1310, D-1320; Session 98 RULE-1 | Fails by assertion at row 1 |
| AC-8 | test | `S100 AC-8`: `install` replaces all twenty `NAMES` of a fake clipboard, own or on its prototype, with tagged recorders that never call the original, returns the empty values, and logs `installed` only after every name is checked; a fake with a name missing, and one with a name that cannot be replaced, give `{ ok: false }`, a `failed` line naming it, no `installed` line and no marker; the hooks register `dom-ready` with `on`; on a fake `wc` whose originals throw if called, they replace `wc.copy`, `cut`, `paste`, `pasteAndMatchStyle` and `copyImageAt` with recorders whose tag is checked before each is called, each call logged (`webContents paste` as `read`) and never reaching the original, and leave `wc.replace` and `replaceMisspelling` the same objects; they record and prevent the seven chords (Control+C, Control+X, Control+Insert, Shift+Delete, Control+V, Control+Shift+V, Shift+Insert) and deny and record the two clipboard permissions; `rendererGuard` replaces the four `Clipboard.prototype` methods and `execCommand('copy'|'cut'|'paste')` and is idempotent. Only fakes and tag-checked recorders run: no real paste or clipboard read on the dev PC | D-1310, D-1311, D-1320, D-1322, D-1324, D-1331 | Fails by assertion at row 1 (`clipboard-guard.cjs` does not exist). Negative oracles in the same test: a plain `v`, `Shift+V` and `Insert` are neither recorded nor prevented; `execCommand('bold')` passes through unrecorded |
| AC-9 | test | `S100 AC-9`: `electron-app.ts` calls `clipboardGuardArgs(`, `clipboardGuardLogPath(` and `clipboardGuardVerdict(`, reads the guard log before `checkMainErrors(` in `close`, and runs `checkMainErrors(` inside a `try` | D-1310, D-1321 | Fails by assertion at row 1 |
| AC-10 | row | `S100 AC-10` on the dev PC: both markers set; the three calls (main `clipboard.writeText`, renderer `navigator.clipboard.writeText`, `webContents.copy`), each after its own function's tag check, recorded and never reaching the OS clipboard; main's call list polled until all three are there (10 s); `app.close()` rejecting with `main writeText`, `renderer writeText` and `webContents copy` named. It passes at row 5, in row 7's full run and in the mini-air main stage | D-1313, D-1320, D-1323; grouping acceptance | Fails by assertion at row 1 on the main marker, before any clipboard call (`red-check.py --require 'S100 AC-10'`) |
| AC-11 | test | `test_ac_11_known_tracked_list` with the new value; `test_s100_ac_11_*` pass; `pins-check.py` exits 0 at rows 3 and 4 and in the gate | D-1305 | The three tests fail by assertion at row 3 |
| AC-12 | row | `CLIPBOARD_NEVER_DEVPC`: `flake-run.py` refuses with exit 2 before any run at rows 0 and 1; `--list-check` gives 237 at row 0 and 238 after rows 1 and 2 | D-1319 | Rows 0 and 1: exit 2, `refused before any run` |
| AC-13 | row | `npm run typecheck`, ESLint on every changed and new `ui` file with `--max-warnings 0`, the full Vitest suite (`AC-43.13` and `AC-44.13` included) and ruff in the D-1287 scope pass at row 6 and in the gate | Session 97 RULE-2; D-1287 | A check, not a Red; a failure is S3 |
| AC-14 | row | Row 7: `flake-run.py --mode full --runs 1 --no-burn --expect-total 238` passes 238 of 238 in 30 files with the guard on; the receipt holds no `CLIPBOARD_GUARD:` and no `unhandled rejection:` line; the kept `C1-5`, `AC-71.15` and `W4-3` titles and `S100 AC-10` are among the passes; `guard-logs.py --receipt` over the run's folders exits 0 (AC-21); `D/edc-foreign-7.json` records the dirty tree | Grouping acceptance; D-1313 | The row-1 E2E Red |
| AC-15 | row | Row 8, the mini-air run at the final tree: main `tests` 238, `expected` 238, `unexpected`, `flaky` and `skipped` 0, `spec_files` 30, `new` and `overlap` empty, `commit` equal to the snapshot; the gated `outcome` in `GATED_OUTCOMES` and `files` the two gated names in order; the outcome is a receipt | Grouping acceptance; D-1314 | A count other than these is S12 |
| AC-16 | row | `gated-count.py --run` on row 8's folder prints the outcome, `primer=` and `other=` and the D-1301 tally; under `run`, `other=3/3` (else S12) | D-1314; D-1301 | Its selftest refuses a missing, empty or invalid report and a test of a third file |
| AC-17 | row | `E2E-DEVPC-CLIPBOARD-SPECS` is `resolved` through `issue-resolve.py` on row 7's zero guard records and row 8's main-stage pass, quoting the gated outcome; `E2E-CLIPBOARD-PRIMER-EMPTY` gets `verification` only and stays `open` unless the tally reads `close`; every other issue keeps its row-0 form | D-1315 | `issue-resolve.py` refuses a register hash other than row 0's |
| AC-18 | test | `test_s100_ac_18_*`: the run book's Session 100 section names `copy-system-clipboard.test.ts`, `CLIPBOARD_GUARD`, `AVKIT_E2E_CLIPBOARD_GATED` and D-1301's rule; `commands.md` names the guard | D-1318 | Fail by assertion at row 3 |
| AC-19 | row | `LOCAL_HOST_DETAILS` and the home path: `host-details-scan.py` exits 0 at rows 0 and 9, in the gate and at H1-6; `tools/check_home_path.py` passes before (row 0) and after (the gate); `eol-check.py` passes at each row that writes | Grouping gate | The scan's sentinel at row 0 |
| AC-20 | row | Session 99 stays apart: its folder, handoffs and reflection (`identity.py` `PEER_PREFIXES`) are never read, hashed or bound, excluded by pathspec and by name before any content read, tracked or untracked; its possible tracked writes are recorded by name only in `baseline-scope.json` (`peer-dirty, named only`), row 0's dirty hashes, the gate's output and `D/edc-foreign-7.json`, and never failed on; a peer write after the gate means H1-2 runs again (D-1330); the commit paths are this plan's only; grouping row 100 becomes `executed (Session 100)` and no other grouping line changes | D-1316, D-1330; the brief; EDC-R1-2 | Row 9's register check fails a grouping change outside `:105`. `identity.py --selftest` (`edc-plan-selftest-identity.txt`): five untracked and then tracked peer files leave the state unchanged and are never read, while this session's own code and test inputs beside them stay bound and a change to them is seen; a copy without the two exclusions fails 23 cases (`edc-plan-identity-mutant.txt`) |
| AC-21 | row | The guard's verdict without `close`: `guard-logs.py` exits 0 on row 5's diag folder (`--diag`), on every run and rerun folder that row 7's and the gate's flake-run receipts name (`--receipt`), and on row 8's `<run dir>/host/diag` (`--diag`, the gated files without logs). No `call` or `failed` line outside the AC-10 launch; the AC-10 launch holds exactly its three calls; every finished non-gated launch has exactly one `installed` line; the launches without one are counted | D-1321 | Its selftest (19 cases, `edc-plan-selftest-guard-logs.txt`) refuses a call in another launch, a `failed` line, a missing `installed` line, an invalid line, an orphan log and an AC-10 launch with a call missing |
| AC-22 | row | No new file holds a skip, only or todo literal: row 6's check finds none of the nine forms (`test`, `it` or `describe` with `.skip`, `.only` or `.todo`) in `ui/tests/unit/e2e-clipboard-guard.test.ts` or `clipboard-guard.cjs`, and in each new E2E spec only its one file-level `test.skip(` guard (D-1305, D-1313); `AC-43.13` and `AC-44.13` pass in the full Vitest suite | D-1329 | A check, not a Red; a hit is S3 |

### Spec Sufficiency Table

| Question | Answer | Source |
|---|---|---|
| Which steps move? | The lines that write or read the system clipboard in `C1-5`, `AC-71.15 (b)` and `(d)`, with what they need to reach them | D-1303, D-1306 |
| Where do they go? | A second gated file, `copy-system-clipboard.test.ts` | D-1305 |
| How does (e) get the token? | A throwaway `randomUUID()` seeded in the scratch app data before launch | D-1307 |
| What happens to `W4-3`'s two clicks? | They leave; Copy MCP config is still clicked in the gated (d) | D-1308 |
| What does the guard cover? | The twenty `NAMES` in main, own or inherited; the four renderer `Clipboard` methods and `execCommand('copy'|'cut'|'paste')` on every load; `webContents.copy`, `cut`, `paste`, `pasteAndMatchStyle` and `copyImageAt`; the four copy chords and the three paste chords; the two clipboard permissions | D-1310, D-1311, D-1320, D-1322, D-1324, D-1331 |
| What turns the guard off? | `AVKIT_E2E_CLIPBOARD_GATED=1`, set only by the gated stage | D-1310 |
| What if the guard log is missing or bad? | The test fails with a named message | D-1310; Session 98 RULE-1 |
| What if the guard cannot install? | The launch exits 70 before the app starts, with a `failed` line | D-1320 |
| What if a spec swallows `close`? | `guard-logs.py` reads every launch's log of the run | D-1321 |
| What stays uncovered? | The Edit menu clicked with the mouse (on Windows most likely caught by the `wc` recorders, not run-proven; on macOS native); a copy or paste before the first `dom-ready` | D-1325, D-1322, D-1331 |
| Does the tool or the launcher change? | No | D-1305 |
| How does a gated run count for PRIMER? | Only the capture file's 2 of 2 under `run` | D-1314 |
| What if the guard fails an unexpected dev-PC test? | Stop the row; the coordinator rules | D-1317 |
| What reaches the mini-air? | `HEAD` plus this session's eleven code and test paths | D-1316 |
| What if Session 99 writes during the session? | Its folder, handoffs and reflection never enter the tested state; its tracked writes count in the one tracked-diff digest and are published by name only; a write after the gate means the gate runs again, never a failure of Session 99's work | D-1330 |
| Is any API or exit code changed? | No | M-4 none |

#### Files Modified

| Path | Change | Row | Line endings |
|---|---|---|---|
| `ui/tests/e2e/copy-system-clipboard.test.ts` | New: the three moved clipboard tests and the file-level guard | 2 | LF |
| `ui/tests/e2e/console-chrome.test.ts` | `C1-5`'s copy step out, retitled | 2 | CRLF (232 lines) |
| `ui/tests/e2e/mcp-setup-prompt.test.ts` | (b) and (d)'s clipboard part out, two retitles, the token seed | 2 | CRLF (165) |
| `ui/tests/e2e/settings.test.ts` | `W4-3`'s two clicks out | 2 | CRLF (925) |
| `ui/tests/e2e/clipboard-guard.cjs` | New: the guard preload (fixed `NAMES`, the hooks, exit 70) | 5 | LF |
| `ui/tests/e2e/clipboard-guard.test.ts` | New: `S100 AC-10` | 1 | LF |
| `ui/tests/e2e/electron-env.ts` | Five exports | 5 | LF (90) |
| `ui/tests/e2e/electron-app.ts` | The guard argument, env, log path and joined verdict in `launchElectron` | 5 | LF (171) |
| `ui/tests/unit/e2e-clipboard-guard.test.ts` | New: `S100 AC-5` to `AC-9` | 1 | LF |
| `tools/e2e_host/known-failures.json` | One `gated` entry appended | 4 | LF (7) |
| `tests/tooling/test_e2e_remote.py` | The docstring line, `test_ac_11`, `GATED_FILES_S100`, four `test_s100_` tests | 3 | LF (3,063) |
| `.agent/docs/e2e-remote-host.md` | The Session 100 section and one sentence | 4 | LF (341) |
| `.agent/docs/commands.md` | Two lines (D-1318); shared with Session 99, re-read first | 4 | CRLF (227) |
| `.agent/context/known-issues.yaml` | Two issues updated | 9 | LF (6,188) |
| `.agent/context/known-issues.md` | Generated by `render` | 9 | LF (36) |
| `.agent/context/grouping/2026-11-20-e2e-devpc-clipboard-session-grouping.md` | Row 100 (`:105`) only | 9 | LF (128) |
| `.agent/context/current-focus.md` | One entry; shared with Session 99, re-read first | H1-3 | CRLF (248) |
| `docs/execution/metrics.md` | One row; shared with Session 99, re-read first | H2-3 | CRLF (108) |
| The handoff, the implementation review, the reflection | New | H1-6, H1-7, H2-2 | LF |
| This plan folder | Written at plan time | — | LF |

These are the 18 paths of the gate's `mine` set, plus the closeout artifacts and this folder.

**Outside the repository** (never tracked): receipts under `D` and `C:/Temp/av-kit/e2e-remote/<run-id>/`; on the mini-air, the tool's own `bin\`, `runs\<run-id>\` and `results\<run-id>\` (with `gated\`) under its configured root, in Session 96's layout; the snapshot commit object in `.git/objects`, on no ref; each guarded launch's guard log: `<diag>/clipboard-<launch>.jsonl` in its run's diag folder (under `D` for rows 5 and 7 and the gate; on the mini-air under the tool's results, copied back to `<run-id>/host/diag`), else `clipboard.jsonl` in its own temp folder, deleted at close.

**Read, never changed** (bound in `baseline-scope.json`): `ui/tests/e2e/capture-system-clipboard.test.ts`, `main-error-watch.cjs`, `global-setup.ts`, `ui/playwright.config.ts`, `ui/vitest.config.ts`, `ui/eslint.config.js`, `ui/scripts/playwright-with-outputfile.mjs`, `ui/package.json`, `tools/e2e_remote.py`, `tools/e2e_host/run-e2e.ps1`, `host-facts.ps1`, `host-status.ps1`, `e2e-host.example.json`, `.github/workflows/ci.yml`, and `ui/src/main/index.ts` (in Session 99's class: when dirty at row 0 it is recorded as `peer-dirty, named only`, and a later change is printed by name, never failed on; D-1316, D-1330).

**Line endings** were measured with Python bytes (`edc-plan-eol.txt`). The three kept spec files, `commands.md`, `current-focus.md` and `metrics.md` are CRLF and stay CRLF. Every other scope file is LF and stays LF; every new file is LF, written as bytes. `eol-check.py` checks every scope path against its row-0 copy.

**Foreign classes.**
- The coordinator's (Session 92 RULE-3): `.agent/model-registry.local.json`, `.claude/agents/*.md`, `.cursor/agents/*.md`. Row 0 binds them by hash; a change is recorded in the handoff, is not S4, and stays out of the commit.
- Session 99's (D-1316): `ui/src/**`, `docs/build-plan/06-gui.md`, `docs/build-plan/build-priority-matrix.md`, `docs/BUILD_PLAN.md`, `.agent/context/meu-status.yaml`, `.agent/context/meu-registry.md`, `.agent/skills/README.md`, and the three shared closeout files `current-focus.md`, `metrics.md` and `commands.md`. A change by Session 99 is recorded by name, never content-hashed in a receipt this plan publishes, never S2 or S4, and only this session's own lines in the three shared files enter its commit (D-1330). Session 99's plan folder, handoffs and reflection (`PEER_PREFIXES`) are named from `git status` only, never opened, and excluded from `identity.py`'s tested state before any read. Its tracked writes still enter the tested state as part of the one tracked-diff digest, because the suites read them; a peer write after the gate fails the identity check, and the action is to run the gate again (H1-2), never to fail, revert or stash Session 99's work (D-1330).

## Out of Scope

| Item | Basis |
|---|---|
| Any product code (`ui/src`, `packages/`, `mcp-server/src`, `backend/`), including a test hook for the clipboard | Grouping §3 Gate; D-1303 (B lost) |
| An assertion, timeout or wait in any moved or kept spec | D-1303; M-7 |
| `Menu.setApplicationMenu(null)`, or any other change to the app's menu in a guarded launch | D-1325: the Edit menu clicked with the mouse stays a named residual; the chords and `webContents.copy`, `cut`, `paste` and `pasteAndMatchStyle` are guarded (D-1324, D-1331) |
| A Pin MCP config click in the gated file | D-1308: the gated (d) covers the shared `copyMcpConfig` write; adding a fourth gated test is beyond D-1303's moves |
| Closing `E2E-CLIPBOARD-PRIMER-EMPTY` | D-1301's bar of 5 cannot be met this session; D-1314 |
| Changes to `tools/e2e_remote.py`, the host scripts or the session probe | D-1305: they already take a list |
| RustDesk's settings, service or version; Smart App Control; auto sign-in; a self-hosted runner (D-1216); D-1200 | The brief's hard stops |
| The host's scheduled task, config, account or known-hosts entry | Session 96's; used unchanged |
| The ruff cleanup of `tools/` | D-1300; another session |
| `py-types`, MCP and OpenAPI suites | `packages/` and `mcp-server/` unchanged (H1-4 proves it) |
| Session 99's files and its folder | The brief |

## BUILD_PLAN.md Audit

No MEU (D-1302; grouping §3 Session 100 "(no MEU)"). `docs/BUILD_PLAN.md`, `meu-status.yaml` and `meu-registry.md` are not edited by this session. Session 99 may edit them, so row 10's hub audit does not require an unchanged hash: it checks only that `docs/BUILD_PLAN.md` names neither `e2e-devpc-clipboard` nor `copy-system-clipboard` nor `clipboard-guard`. The gate's `state-render` step (`meu_status.py render --check`) proves that nothing generated drifted.

## Verification Plan

### 1. Baseline (row 0)

`baseline.ps1`, in the shape of Session 98's, runs ten fail-fast steps:
1. `uv sync --frozen --offline --all-packages` (S7 on a held file).
2. The record:
   - `HEAD` is `f1ba411` or a descendant; `D/edc-since.txt` lists every commit since it. A commit that touches an own scope path is S2; one that touches only a shared closeout file is recorded;
   - the dirty set with both foreign classes marked, and `git worktree list`;
   - `baseline-scope.json` over §Files Modified, "Read, never changed" and the coordinator's class, with the four new test files, the handoff, the review and the reflection absent; a Session 99-class path dirty at row 0 is recorded as `peer-dirty, named only`, never hashed (D-1330);
   - `baseline-dirty-hashes.json`, except Session 99's folder, handoffs, reflection and the rest of its class, named only (D-1330);
   - the row-0 copies under `D/baseline-copies/`, `baseline-eol.json` and `baseline-skip-hashes.json` (secret names dropped before any stat, Session 83 RULE-2);
   - the S2 anchors by line and text (19, `edc-plan-anchor-probe.txt`); a `ui/src` anchor Session 99 moved is recorded, never S2;
   - the known list (one `gated` entry, no `known`, no `skip`); both issues `open` with `meu_links: []` (by key); row 100 `approved`; 30 spec files with one gated file; no graphify graph (S1); the plan, task and plan-review hashes.
3. The OS-wide probe (Session 91 RULE-1).
4. The home-path check before (S8).
5. The checkers' selftests (`guard-logs.py`'s included, D-1321) and `eol-check.py`.
6. `split-specs.py --out` into a new folder, each file's SHA-256 against its plan-time value (S9).
7. The row-0 refusals: `--check` exits 1; `writer-scan.py --expect 10`; `flake-run.py --mode full` exits 2 before any run; `--list-check` gives 237; `guard-check.py --list` exits 1.
8. The `snapshot-commit.py --out` sentinel.
9. The host-detail scan with `--allow-absent` and its sentinel.
10. Ruff on this folder's Python.

The last line is `baseline: all steps exit 0`. A step that must refuse passes only on its one exit code.

### 2. Red, then Green (rows 1 to 6)

- **Row 1, Red:** write the Vitest file and the E2E guard spec. A Python check proves every clipboard call in the guard spec (at least three) sits inside its own `evaluate` behind a tag check of that exact function (`Reflect.get(<callee>, '__avkitClipboardGuard') !== true`, then `throw`; D-1320, `edc-plan-shape-check.txt`). Then `npm run build`, `host-load.ps1`, the Vitest Red (`S100 AC-5` to `AC-9` fail by assertion) and the E2E Red (`S100 AC-10` fails on the main marker), each receipt with its `.exit`, judged by `red-check.py --require`. `writer-scan.py --expect 10`; the test files' hashes go to `D/edc-test-sha-1.json`; the dev-PC list is 238.
- **Row 2, Green, the moves:** `split-specs.py --write`, `--check`, `npm run typecheck`, ESLint on the four spec files, `writer-scan.py --expect 8`, `--list-check` 238, the Vitest files that read the E2E folder (`queue-primitives`, `queue-card`, `e2e-harness`), and `guard-check.py --list` (AC-2).
- **Row 3, Red, the pins:** the `test_s100_` tests, `GATED_FILES_S100`, the `test_ac_11` change and the docstring line; `pytest -k` fails by assertion; `red-check.py --require`; `pins-check.py`; `D/edc-test-sha-3.json`.
- **Row 4, Green, the list and the docs:** the known list, the run book, `commands.md`; `writer-scan.py` 0; `S100 AC-5` passes; the full `test_e2e_remote.py` passes; `pins-check.py` and the test hashes hold.
- **Row 5, Green, the guard:** `clipboard-guard.cjs`, `electron-env.ts`, `electron-app.ts`; ESLint and `tsc`; the unit file passes; the shape check again; `npm run build`, `host-load.ps1`, then the E2E guard spec passes with `AVKIT_E2E_DIAG_DIR` set to `D/edc-diag-5-<stamp>`, and `guard-logs.py --diag` on that folder exits 0 (AC-21).
- **Row 6, the sweeps:** the full Vitest suite (with `AC-43.13` and `AC-44.13`), the skip/only/todo literal check over the new files (AC-22, D-1329) and ruff in the D-1287 scope, before any snapshot (Session 97 RULE-2).

### 3. Dev PC and real host (rows 7 and 8)

- **Row 7:** record `git status` and the hash of every dirty path outside Session 99's class to `D/edc-foreign-7.json`, Session 99's paths by name only (D-1330); then `flake-run.py --mode full --runs 1 --no-burn --expect-total 238`; the receipt must hold no `CLIPBOARD_GUARD:` and no `unhandled rejection:` line; then `guard-logs.py --receipt` over every run and rerun folder the receipt names (AC-21; a failure is S5).
- **Row 8:**
  1. `snapshot-commit.py --out D/edc-snapshot-8.json` over the eleven code and test paths (the three edited specs, the copy file, the guard `.cjs`, the guard spec, `electron-env.ts`, `electron-app.ts`, the unit test, `known-failures.json`, `test_e2e_remote.py`), then `--verify`.
  2. `tools/e2e_remote.py check` (S10 or S11 by exit band).
  3. `tools/e2e_remote.py run <commit>`, in the background, waited on with Monitor.
  4. A Python check of `summary.json` (AC-15), writing the run folder to `D/edc-run-8-dir.txt`.
  5. `gated-count.py --run` into `D/edc-gated-count-8.txt` (AC-16).
  6. `guard-logs.py --diag <run dir>/host/diag` into `D/edc-guard-logs-8.txt` (AC-21; a failure is S12).

The stops: a busy, locked or unsigned host is S10; any other refusal is S11; a main count other than AC-15's, or a gated failure under `run` other than the primer's, is S12; a scope change after the run is S13.

### Session gate (H1-2)

`session-gate.ps1`, in the shape of Session 98's: fail-fast, later steps printed `not_run`, the last line `session-gate: all steps exit 0`.

| Stage | Steps |
|---|---|
| Identity | `identity-before` (`identity.py`, which clears `ELECTRON_RUN_AS_NODE`, Session 88 RULE-3, and drops Session 99's `PEER_PREFIXES` before any read, D-1330) |
| Static | `task-contract`; `scope-paths` (the `mine` set; Session 99's class printed, never failed); `line-endings`; `home-path`; `host-details`; `split-check`; `guard-list` (`edc-guard-list-gate-<stamp>.json`); `writer-scan` (0); `pins`; `known-list` (gated `capture` then `copy`, `known` and `skip` empty); the selftests of `red-check`, `eol-check`, `split-specs`, `writer-scan`, `gated-count`, `pins-check`, `guard-check`, `flake-run`, `guard-logs` and `snapshot-commit`; `py-format` and `py-lint` (`ruff format --check tests/tooling/test_e2e_remote.py` and the plan's Python; `ruff check packages/ tests/` and the plan's Python, D-1287); `snapshot-verify` (else S13); `test-hashes` (the newest `edc-test-sha-*.json`; S3) |
| UI static | `ui-types`, `ui-lint` (from `ui`) |
| Tests | `ui-tests` (the full Vitest suite, the sweeps included); `py-tests` (`pytest tests/ -x -q`); `canon` |
| Host load | `host-load` (Session 81 RULE-2; 50 %) |
| E2E | `ui-build`; `e2e-full` (`flake-run.py --mode full --runs 1 --no-burn --expect-total 238`; a `CLIPBOARD_GUARD:` or `unhandled rejection:` line sets code 10); `guard-logs` (`guard-logs.py --receipt` over `e2e-full`'s receipt, AC-21) |
| Registers | `issues-render-check`; `state-render`; `gated-count` (row 8's folder); `guard-logs-remote` (`guard-logs.py --diag` on row 8's `host/diag`); `remote-evidence` (238 and 238, no `new`, commit equal to the snapshot, the gated files, `tool_sha256`) |
| Identity | `identity-after`; a difference caused by a Session 99 write means the gate runs again (D-1330) |
| Skipped, with reasons | `py-types`, `mcp-types`, `mcp-tests`, `mcp-build`, `openapi`, `mcp-audit`: every file under `packages/`, `mcp-server/{src,scripts,tests}` and `native/` keeps its row-0 hash (H1-4) |

## Stop Conditions

| Id | Condition | Action |
|---|---|---|
| S1 | `graphify-out/` appears | Stop; re-plan the context tool decision |
| S2 | At row 0: <br>• `HEAD` does not descend from `f1ba411`, or a commit since it touches an own scope path; <br>• an anchor outside `ui/src` is gone or changed in meaning; <br>• the known list is not its row-0 form, or an issue is not `open`; <br>• row 100 is not `approved`; <br>• the spec count is not 30, or `writer-scan.py` does not count 10 | Stop. A line that only moved is recorded in the handoff (Session 51 RULE-3); anything else goes to the coordinator |
| S3 | A Red test fails for a setup reason or passes; a Green needs a test change §Test pins does not name (M-7); an existing test fails after Green; a new file holds a skip, only or todo literal beyond its file-level guard (AC-22); a test file's hash moves after its Red; row 5 cannot go green without product code (the grouping's split flag: the coordinator rules) | Stop; never edit a test to pass |
| S4 | `git status` lists a path outside this plan's scope, `baseline-dirty.txt` and the two foreign classes, or an own scope path that no earlier row wrote differs from `baseline-scope.json` | Stop and ask the coordinator; never commit, stash or revert another session's work |
| S5 | A dev-PC full run fails a test that its solo rerun does not clear, or holds `CLIPBOARD_GUARD:` or `unhandled rejection:`, or `guard-logs.py` fails on its folders | A finding, not a retry: stop, record the receipts, tell the coordinator (D-1317; it rules with D-1341 to D-1349). Never widen the guard's allow-list or move a test to pass |
| S6 | Codex is unavailable or the ledger refuses a round | The coordinator |
| S7 | `uv sync` fails on a held file, or the load stays above 50 % after `flake-run.py`'s ten-minute wait | Tell the coordinator; never stop a process |
| S8 | The home-path check or the host-detail scan finds a new hit | Stop; fix the file, never extend the allow-list |
| S9 | `split-specs.py --out` at row 0 differs from the plan-time hashes, or `--check` fails after row 2 | Stop: the base blobs are not what the plan measured |
| S10 | At row 8 the host refuses 20 to 24 (a lock this session did not take), or `overlap` is not empty | Record it, wait 15 minutes and run `check` again, up to 8 times; then the coordinator. Never stop a process, release another run's lock or start the task by hand |
| S11 | At row 8 any other refusal (10, 11, 25 to 31, 33, 34), or `lock_kept` | Stop and record. `release` once with this session's own run id. Never bypass or re-pin the host key (11 goes to Mat). A second S11 goes to the coordinator |
| S12 | Row 8's main counts are not AC-15's; under `run` a copy-file test fails (`other` not `3/3`), or a capture test fails with anything but `primer: clipboard image read stayed empty`; or `gated-count.py` exits 1; or `guard-logs.py` fails on `host/diag` | A finding, not a retry: stop, record the summary, tell the coordinator. A primer failure alone is recorded for row 9 under PRIMER |
| S13 | A snapshot scope file changes after row 8 | Rename row 8's `edc-*-8*` receipts with `-r1`, then snapshot and rerun row 8 once on the final files; a later change goes to the coordinator |

## Decision Log

> [!NOTE]
> D-1305 to D-1331 are this plan's twenty-seven briefs; D-1320 to D-1329 adopt the expert pass (`edc100-expert-pass.txt`, F1 to F9), and D-1330 and D-1331 answer plan review round 1 (EDC-R1-2 and EDC-R1-1). D-1332 to D-1340 stay free, and D-1341 to D-1349 are kept for execution (D-1317 routes a guard finding there). The §4a walk:
> - **M-1** (push, merge, release): none. The row-8 snapshot is a commit object on no ref, and the coordinator commits after the review with no push.
> - **M-2** (destructive): none. No assertion is deleted: the clipboard steps move byte for byte. `W4-3`'s two clicks are retired, but they carry no assertion (D-1308). No register entry is removed.
> - **M-3** (new policy): D-1310. Every E2E launch without the gate variable now fails on any clipboard call. That is a standing rule for every later spec. D-1324 widens it: a copy chord, `webContents.copy` or `cut` in a guarded launch fails too. D-1331 widens it again: `webContents.paste`, `pasteAndMatchStyle`, `copyImageAt`, `execCommand('paste')` and a paste chord fail too. D-1321 is checked and not hit: it enforces D-1310's rule and adds none.
> - **M-4** (API, MCP tool, external contract): none. No route, tool shape, exit code or summary key changes; the guard's names live in test code only. D-1321's log file and `guard-logs.py` are test tooling, and exit 70 is the test preload's own refusal (checked, not hit).
> - **M-5** (visible product change): none. No product code changes.
> - **M-6** (source conflict):
>   - D-1314: D-1301's bar says "2 of 2 expected" for a gated stage that now runs five tests in two files; the plan reads it per file.
>   - D-1316: the brief's "a snapshot of the final tree" against Session 99's work in the same tree; the plan snapshots `HEAD` plus this session's paths only.
>   - D-1330: the brief's "never read, bind, hash or commit" Session 99's folder against a `tested_state` that must cover every input the suites read; the plan excludes the peer folder, handoffs and reflection before any read, binds Session 99's tracked writes only inside the one tracked-diff digest, and publishes no content hash of them.
> - **M-7** (assertion change no row names): checked and not hit.
>   - D-1305 names `test_ac_11_known_tracked_list` and its new value in row 3 (HDP `:158`).
>   - D-1307 changes where (e)'s `token` comes from, not its assertion lines.
>   - D-1308 removes two clicks that no assertion reads.
>   - D-1327 adds one assertion line to the moved (e) test and changes none; it is named in row 2 and §Test pins (HDP `:158`).
>   - D-1328 copies `C1-5`'s route lines and wraps the moved steps in `try`/`finally`; no assertion changes.
>   - `pins-check.py` and `split-specs.py --check` stop any other change.
> - **M-8** (scope):
>   - D-1311 also guards the readers, which the grouping did not name.
>   - D-1312 makes the static scan a tracked test, where the grouping offered it only as the fallback.
>   - D-1322 also denies the page's two clipboard permissions and patches every load.
>   - D-1324 also guards `webContents.copy` and `cut` and the copy chords.
>   - D-1331 also guards the native paste path (`webContents.paste`, `pasteAndMatchStyle`, `execCommand('paste')`, the paste chords) and `copyImageAt`, which the grouping did not name.
> - **M-9** (review exit), **M-10** (human action): none. No row asks Mat to connect, disconnect or click.
> - **M-11** (waived gate): none. The copy file's skip on the dev PC is the grouping's own rule (D-1303), and the gated stage runs it.
> - **M-12** (disclosure), **M-13** (permission or trusted remote), **M-14** (headless): none. Nothing leaves Mat's machines. The seeded token is a fresh UUID in a scratch folder, never Mat's token. The host key was pinned in Session 96.
>
> So D-1310 is `mandatory: [M-3]`, D-1311, D-1312 and D-1322 are `[M-8]`, D-1324 and D-1331 are `[M-3, M-8]`, D-1314, D-1316 and D-1330 are `[M-6]`, and the other eighteen are `mandatory: none`. All twenty-seven are handed to the agent under Mat's words, and the hand-over covers M-3, M-6 and M-8 (HDP `:327-330`). `open_decisions` is empty, and there is no STOP item.
>
> **Earlier rows are not copied here.** D-1302, D-1303 and D-1304 live in the grouping's §8 (`:117-125`), with D-1200, which stays open and Mat's (M-12). D-1299 and D-1301 live in the two issues' `enrichment.decision_log`. H2-2 reads them through `--decision-source` on the grouping (this plan's `grouping_source`) and `.agent/context/known-issues.yaml`, with `--decision-issue E2E-DEVPC-CLIPBOARD-SPECS` and `--decision-issue E2E-CLIPBOARD-PRIMER-EMPTY`. `decision_sources` was probed at plan time with that list (Session 90 RULE-2): 4 ids from the grouping alone (D-1200, D-1302 to D-1304), 7 with the register and both issues (adding D-1262, D-1299 and D-1301; `edc-plan-decisions-1.txt`), and runs over this plan with them (`edc-plan-decisions-2.txt`, and after round 1 `edc-plan-decisions-4.txt`, 34 ids). Under HDP §6 the reflection's `### Decisions Log` lists only this session's own reversible autonomous choices.

```yaml
decision_log:
  - id: D-1305
    stage: planning
    question: "Do the moved clipboard steps join the existing gated file or a second one, and what changes in the tool?"
    resolution: autonomous
    class: two-way
    mandatory: none
    chosen: "A: a second gated file, ui/tests/e2e/copy-system-clipboard.test.ts, listed after capture-system-clipboard.test.ts in known-failures.json's gated list. The tool, the launcher and the host scripts stay byte for byte: label_gated, the request and AvStage -Gated already carry a list. test_ac_11_known_tracked_list's gated value changes in row 3, named with its old and new value; GATED_FILES_S100 and two test_s100_ac_11 tests prove the two-file path on the fake host."
    source_tag: Local Canon
    precedents:
      - ".agent/context/grouping/2026-11-20-e2e-devpc-clipboard-session-grouping.md:64-84 — the plan picks the existing gated file or a second one and names every pin it touches"
      - "tools/e2e_remote.py:421 label_gated, :987 gated_summary; tools/e2e_host/run-e2e.ps1:263-288 — the gated list is read and passed to one AvStage -Gated child"
      - "tests/tooling/test_e2e_remote.py:1564-1576 — the pin on the tracked list"
      - "Session 97 RULE-1 — every changed pin is named with its old and new value in the row that changes it"
    research: { engine: none, sources: [] }
    reasoning: "Handed to the agent: USER_EXPLICIT 2026-11-18 'make the decisions always the recommenations', continuing USER_EXPLICIT 2026-11-20 'continue with next prompt'. A keeps D-1301's primer count clean, because the capture file stays exactly what Session 98 measured, and it needs no tool change, because the gated stage already takes a list. M-7 is checked and not hit: the one pin that changes is named with both values in row 3. B, append the three tests to capture-system-clipboard.test.ts, mixes copy tests into the primer file, so gated_summary's per-file failures no longer tell a primer read from a copy failure, and the capture file's Session 98 hash is lost. C, a separate stage for the copy file, adds a launcher change the grouping did not ask for. D, doing nothing, keeps the four writers on the dev PC. Undo: drop the gated entry and the new file. Two-way."
  - id: D-1306
    stage: planning
    question: "Which lines move, and how is the move proved?"
    resolution: autonomous
    class: two-way
    mandatory: none
    chosen: "A: split-specs.py builds the four files from the f1ba411 blobs. Each moved clipboard line is copied byte for byte (only the line ending changes) into the new file, with the launch and navigation lines it needs to reach that state. The kept files lose only those lines, each replaced by one named comment, and keep CRLF. --check proves the four files and the invariants; its selftest refuses a changed assertion, a lost line and a wrong line ending."
    source_tag: Local Canon
    precedents:
      - ".agent/context/grouping/2026-11-20-e2e-devpc-clipboard-session-grouping.md:117-121 — D-1303: move the clipboard steps, assertions unchanged, the rest stays"
      - "docs/execution/plans/2026-11-20-e2e-clipboard-specs/split-specs.py — Session 98's split, proved the same way; D-1286 compares the CRLF checkout form"
      - "C:/Temp/av-kit/e2e-devpc-clipboard/edc-plan-split-out-4.txt — the four built files and their SHA-256; edc-plan-split-out-eslint.txt — ESLint exit 0 on all four"
    research: { engine: none, sources: [] }
    reasoning: "Handed to the agent: USER_EXPLICIT 2026-11-18 'make the decisions always the recommenations', continuing USER_EXPLICIT 2026-11-20 'continue with next prompt'. A reuses Session 98's proved method: a scripted move from pinned blobs, so the review can check every byte against the base and a different base stops the row. B, edit the files by hand and review the diff, gives no check that the moved lines are byte-identical. C, move whole tests, takes the non-clipboard assertions of C1-5 and AC-71.15 off the dev PC, against D-1303's 'the rest of each test stays'. D, doing nothing, keeps the writers. Undo: restore the three files from f1ba411 and delete the new one. Two-way."
  - id: D-1307
    stage: planning
    question: "AC-71.15 (e) checks that no setup prompt contains the token (d) copied. Where does (e) get the token once (d)'s clipboard read moves?"
    resolution: autonomous
    class: two-way
    mandatory: none
    chosen: "A: launchApp(token?) writes a fresh randomUUID() plus a newline to mcp-token.txt in the test's own scratch app data before launch; readOrCreateMcpToken reads that file, trimmed, instead of making a token. (e) keeps its loop and its not.toContain(token) lines byte for byte."
    source_tag: Local Canon
    precedents:
      - "ui/src/main/index.ts:162-170 — readOrCreateMcpToken reads mcp-token.txt trimmed when it exists, else writes a randomUUID()"
      - "ui/tests/e2e/mcp-setup-prompt.test.ts:28 launchApp (a mkdtempSync scratch AVKIT_APP_DATA); :138-151 (d) and (e)"
      - "C:/Temp/av-kit/dispatch/s100-planner-brief.md — (e) must keep its assertion without the clipboard"
    research: { engine: none, sources: [] }
    reasoning: "Handed to the agent: USER_EXPLICIT 2026-11-18 'make the decisions always the recommenations', continuing USER_EXPLICIT 2026-11-20 'continue with next prompt'. A gives (e) a token the test knows before launch, through the product's own file contract, so (e) proves the same property, that no prompt leaks the app token, with no clipboard and no product change. M-7 is checked and not hit: (e)'s assertion lines keep their bytes; only the line that assigns token changes, and the plan names it. The scratch folder is the test's own mkdtempSync, never Mat's app data, and the token is new each run. B, read the token from the scratch folder after launch, depends on when the app writes it and adds a wait. C, move (e) into the gated file too, takes a non-clipboard assertion off the dev PC. D, doing nothing, leaves (e) reading the clipboard. Undo: restore launchApp and the token line. Two-way."
  - id: D-1308
    stage: planning
    question: "W4-3 clicks Copy MCP config and Pin MCP config only to check they raise no page error. What happens to those clicks?"
    resolution: autonomous
    class: two-way
    mandatory: none
    chosen: "A: retire the two clicks from settings.test.ts, replaced by one named comment. No assertion of W4-3 changes. Copy MCP config is still clicked in the gated (d). Pin MCP config's click is then actuated by no E2E spec; that is named as a residual in the plan and the handoff."
    source_tag: Local Canon
    precedents:
      - "ui/tests/e2e/settings.test.ts:216-217 — the two clicks; no assertion reads their result"
      - "ui/src/renderer/pages/SettingsPage.tsx:533-536 — both buttons call copyMcp, which calls window.api.copyMcpConfig, a main-process clipboard write"
      - ".agent/context/grouping/2026-11-20-e2e-devpc-clipboard-session-grouping.md:117-121 — D-1303 names W4-3's steps among the moves"
    research: { engine: none, sources: [] }
    reasoning: "Handed to the agent: USER_EXPLICIT 2026-11-18 'make the decisions always the recommenations', continuing USER_EXPLICIT 2026-11-20 'continue with next prompt'. The two clicks assert nothing of their own; W4-3's page-error check covers the whole test. Copy MCP config's write is proved in the gated (d), which reads the clipboard back, so A loses only the Pin click's no-page-error coverage, which the plan names. M-7 is checked and not hit: no assertion changes. B, move both clicks into a fourth gated test, adds a test D-1303 did not name and a second token write on the mini-air for a check that reads nothing. C, keep the clicks and let the guard stub the write, would make W4-3 fail under D-1310's guard. D, doing nothing, keeps two writes per dev-PC run, one of them a token. Undo: restore the two lines. Two-way."
  - id: D-1309
    stage: planning
    question: "What are the titles of the three moved tests and the three kept tests that lose a step?"
    resolution: autonomous
    class: two-way
    mandatory: none
    chosen: "A: each moved test keeps its source id and names only its clipboard step (C1-5 console copy writes the visible logs to the clipboard; AC-71.15 (b) Copy prompt fills the clipboard with the Codex setup prompt; AC-71.15 (d) Copy MCP config puts a non-empty app token on the clipboard). Each kept title drops only the moved clause."
    source_tag: Local Canon
    precedents:
      - "ui/tests/e2e/console-chrome.test.ts:77, mcp-setup-prompt.test.ts:91 and :126 — the current titles"
      - "Session 83 RULE-1 — AC ids quoted from titles belong to their own MEUs"
    research: { engine: none, sources: [] }
    reasoning: "Handed to the agent: USER_EXPLICIT 2026-11-18 'make the decisions always the recommenations', continuing USER_EXPLICIT 2026-11-20 'continue with next prompt'. Keeping the source id lets a reader find the original AC from either half, and a title that names only what the test still does keeps the report honest. B, keep the old titles unchanged, would claim a clipboard step in a test that no longer has one. C, new ids, breaks the link to the MEU that owns the AC. D, doing nothing, is B. Undo: rename. Two-way."
  - id: D-1310
    stage: planning
    question: "How does every non-gated launch fail when a test touches the system clipboard?"
    resolution: autonomous
    class: two-way
    mandatory: [M-3]
    chosen: "A: electron-app.ts adds '-r clipboard-guard.cjs' to every launch unless AVKIT_E2E_CLIPBOARD_GATED is '1'. The preload replaces every own function of Electron's clipboard with a recorder that logs the call and never calls the original, and on each window's dom-ready replaces navigator.clipboard's four methods and execCommand('copy'|'cut'), reporting through a tagged console message. At close, before the scratch folder is deleted, the helper reads the log and throws CLIPBOARD_GUARD: naming each call; a missing, empty, never-installed or invalid log also throws. Test code only."
    source_tag: Local Canon
    precedents:
      - ".agent/context/grouping/2026-11-20-e2e-devpc-clipboard-session-grouping.md:122-125 — D-1304: the launch helper stubs the writers when the variable is not 1; test code only"
      - "ui/tests/e2e/electron-env.ts:20-23 and main-error-watch.cjs — the -r preload with a log in the launch's scratch folder"
      - "C:/Temp/av-kit/e2e-devpc-clipboard/probe/probe-result.jsonl — on Electron 42.11.18 a -r preload replaced all twenty clipboard functions on the object main imports, the patch survived ready, and dom-ready replaced the renderer's methods; no writer was called"
      - "Session 98 RULE-1 — a missing, empty or invalid observation is a non-pass"
    research: { engine: none, sources: [] }
    reasoning: "Handed to the agent: USER_EXPLICIT 2026-11-18 'make the decisions always the recommenations', continuing USER_EXPLICIT 2026-11-20 'continue with next prompt'. M-3 is hit: from now on every E2E launch without the variable fails a test that touches the clipboard, which is a rule every later spec must follow. A puts the guard in the one helper every spec uses, so no spec can bypass it, and the recorder never calls the original, so even the failing case cannot write. The grouping's split flag is not triggered: the probe proved the patch without product code. B, a test-only IPC handler in the product, changes product code (the gate forbids it). C, the static scan alone, misses product writes reached through a button, which is how Session 98 missed two writers. D, doing nothing, leaves the next missed writer on Mat's clipboard. A can miss a native copy (Chromium's Ctrl+C or a menu role) and a renderer write before dom-ready; both are named residuals. Undo: drop the guard args from electron-app.ts. Two-way."
  - id: D-1311
    stage: planning
    question: "Does the guard cover only the writers, or the readers too?"
    resolution: autonomous
    class: two-way
    mandatory: [M-8]
    chosen: "A: every own function of clipboard, readers included. A reader returns an empty value of its type and is logged as a read, so a test that reads the clipboard fails just as a write does."
    source_tag: Local Canon
    precedents:
      - "C:/Temp/av-kit/e2e-devpc-clipboard/probe/probe-result.jsonl — ten writers and ten readers, all writable own properties"
      - "known-issues.yaml E2E-DEVPC-CLIPBOARD-SPECS (D-1299) — the dev-PC runs read Mat's clipboard back after each write"
      - "ui/src/main/index.ts:405-409 — readClipboard already returns 'pasted' under AVKIT_E2E=1"
    research: { engine: none, sources: [] }
    reasoning: "Handed to the agent: USER_EXPLICIT 2026-11-18 'make the decisions always the recommenations', continuing USER_EXPLICIT 2026-11-20 'continue with next prompt'. M-8 is hit: the grouping named the writers only. A read on the dev PC returns whatever Mat copied last, which can be a password, and a test that asserts on it fails on Mat's data; guarding both closes that and keeps the rule simple: no dev-PC test touches the clipboard. B, writers only, matches the grouping's words and leaves reads of Mat's clipboard possible. C, readers return a fixed sentinel, hides a reading test instead of failing it. D, doing nothing, is B. Undo: limit the recorder to write and clear names. Two-way."
  - id: D-1312
    stage: planning
    question: "Is the static scan the fallback only, or a tracked test beside the guard?"
    resolution: autonomous
    class: two-way
    mandatory: [M-8]
    chosen: "A: a tracked Vitest test (S100 AC-5) that runs in every Vitest run and fails on any clipboard call, copy chord, copy click or direct _electron.launch( in ui/tests/e2e outside the gated files and the guard's own files, reading the gated list from known-failures.json. writer-scan.py is its Python twin for the plan's counts."
    source_tag: Local Canon
    precedents:
      - ".agent/context/grouping/2026-11-20-e2e-devpc-clipboard-session-grouping.md:122-125 — D-1304 offers the scan as the fallback when the guard cannot be proven"
      - "C:/Temp/av-kit/e2e-devpc-clipboard/edc-plan-writer-scan-head.txt — 10 hits at HEAD; -split.txt 8 after row 2; -after.txt 0"
    research: { engine: none, sources: [] }
    reasoning: "Handed to the agent: USER_EXPLICIT 2026-11-18 'make the decisions always the recommenations', continuing USER_EXPLICIT 2026-11-20 'continue with next prompt'. M-8 is hit: the grouping offered the scan only as the fallback. The runtime guard catches a write when it happens; the scan catches a new clipboard test before any E2E runs, and catches a spec that launches Electron without the helper, which the guard cannot see. It costs one Vitest file and no E2E time. B, the runtime guard alone, finds a misplaced spec only after it has launched. C, the scan as a plan-local script, stops guarding after this session. D, doing nothing, is B. Undo: delete the test. Two-way."
  - id: D-1313
    stage: planning
    question: "How is the guard proven in a real launch, and where does that test live?"
    resolution: autonomous
    class: two-way
    mandatory: none
    chosen: "A: one E2E spec, ui/tests/e2e/clipboard-guard.test.ts (S100 AC-10), in every non-gated run. It checks the main and renderer markers first, calls clipboard.writeText in main and navigator.clipboard.writeText in the page only inside an evaluate that throws unless the marker is set, and expects close to reject naming both calls. It skips when the variable is 1. The dev-PC run and the mini-air main stage therefore have 238 tests."
    source_tag: Local Canon
    precedents:
      - ".agent/context/grouping/2026-11-20-e2e-devpc-clipboard-session-grouping.md:76-80 — a guard test proves a write in a non-gated launch fails with a named message and the gated launch is not blocked"
      - "C:/Temp/av-kit/e2e-devpc-clipboard/edc-plan-list-head.txt — 239 tests in 30 files; 237 on the dev PC"
    research: { engine: none, sources: [] }
    reasoning: "Handed to the agent: USER_EXPLICIT 2026-11-18 'make the decisions always the recommenations', continuing USER_EXPLICIT 2026-11-20 'continue with next prompt'. Only a real launch proves the -r preload's web-contents-created hook reaches the main window, which the plan-time probe registered from the main script. The marker check before each call means the spec cannot write even before the guard exists. That the gated launch is not blocked is proved by the gated stage itself: the copy file's three tests read their writes back on the mini-air. B, a Vitest test with a fake Electron only, never proves the real hook. C, put the spec in the gated stage, proves nothing about the dev PC. D, doing nothing, leaves the guard unproven. Undo: delete the spec and change the expected counts back. Two-way."
  - id: D-1314
    stage: planning
    question: "D-1301 closes PRIMER after five gated run outcomes with '2 of 2 expected'. How does a run count now that the gated stage has five tests in two files?"
    resolution: autonomous
    class: two-way
    mandatory: [M-6]
    chosen: "A: count per file. A run counts toward PRIMER only when its gated outcome is run and both capture-system-clipboard tests pass; the three copy tests never decide PRIMER. Under run, a copy test failure is S12, a finding. gated-count.py applies the rule to row 8's folder, from two counted runs, so the tally can reach at most 3 of 5 and PRIMER stays open."
    source_tag: Local Canon
    precedents:
      - "known-issues.yaml E2E-CLIPBOARD-PRIMER-EMPTY (D-1301) — five gated run outcomes with 2 of 2 expected, counted from r20261120T215925Z-9ac9adc; two counted"
      - "tools/e2e_remote.py:987 gated_summary — the gated report lists each test with its file"
    research: { engine: none, sources: [] }
    reasoning: "Handed to the agent: USER_EXPLICIT 2026-11-18 'make the decisions always the recommenations', continuing USER_EXPLICIT 2026-11-20 'continue with next prompt'. M-6 is hit: D-1301's words were written for one gated file. A keeps D-1301's meaning, which is whether the capture primer reads an image, and keeps the two runs already counted valid. B, require 5 of 5 gated tests, resets the count for a reason that has nothing to do with the primer. C, count any run outcome, counts skipped stages that read nothing. D, doing nothing, leaves the bar unclear after this session. Undo: change gated-count.py's rule. Two-way."
  - id: D-1315
    stage: planning
    question: "What happens to the two issues?"
    resolution: autonomous
    class: two-way
    mandatory: none
    chosen: "A: E2E-DEVPC-CLIPBOARD-SPECS is resolved through issue-resolve.py on row 7's zero guard records and row 8's main-stage pass, quoting the gated outcome. E2E-CLIPBOARD-PRIMER-EMPTY gets row 8's verification in the same issue-resolve.py call and stays open unless gated-count.py reads close; render and render --check follow through tools/issue_triage.py."
    source_tag: Local Canon
    precedents:
      - "C:/Temp/av-kit/dispatch/s100-planner-brief.md — DEVPC resolved through issue-resolve.py after the host run; PRIMER closed only at D-1301's bar"
      - "docs/execution/plans/2026-11-20-e2e-clipboard-specs/issue-resolve.py — Session 98's resolver, copied with RESOLVE_KEYS unchanged"
    research: { engine: none, sources: [] }
    reasoning: "Handed to the agent: USER_EXPLICIT 2026-11-18 'make the decisions always the recommenations', continuing USER_EXPLICIT 2026-11-20 'continue with next prompt'. DEVPC's fix is the guard and the moves, which rows 7 and 8 prove; the gated outcome does not decide it, because a skipped stage still proves the dev PC is clean. PRIMER's bar is D-1301's. B, resolve DEVPC only after a gated run outcome, ties it to whether Mat was connected. C, close PRIMER on this run, breaks D-1301. D, doing nothing, leaves a fixed issue open. Undo: reopen through the register tool. Two-way."
  - id: D-1316
    stage: planning
    question: "Session 99 shares the working tree. What reaches the mini-air, and how are its changes treated?"
    resolution: autonomous
    class: two-way
    mandatory: [M-6]
    chosen: "A: row 8's snapshot is HEAD plus this session's eleven code and test paths only. Session 99's possible writes (ui/src, 06-gui.md, build-priority-matrix.md, BUILD_PLAN.md, meu-status.yaml, meu-registry.md, .agent/skills/README.md, current-focus.md, metrics.md, commands.md) are a foreign class: recorded by name in every dev-PC full run's receipt, never content-hashed in a receipt this plan publishes, never S2 or S4 (amended by D-1330 after plan review round 1). Its folder, handoffs and reflection are named from git status only and excluded from identity.py before any read (D-1330). The three shared closeout files are re-read before this session writes them, and only this session's lines enter its commit."
    source_tag: Local Canon
    precedents:
      - "C:/Temp/av-kit/dispatch/s100-planner-brief.md — the foreign class, the snapshot of HEAD plus this session's paths, re-read before writing the shared files"
      - "docs/execution/plans/2026-11-20-e2e-clipboard-specs/snapshot-commit.py — Session 97's SNAPSHOT_NO_REF, which takes a named path list"
      - "Session 92 RULE-3 — the coordinator's foreign class"
    research: { engine: none, sources: [] }
    reasoning: "Handed to the agent: USER_EXPLICIT 2026-11-18 'make the decisions always the recommenations', continuing USER_EXPLICIT 2026-11-20 'continue with next prompt'. M-6 is hit: 'the final tree' and 'never bind Session 99's work' conflict while both sessions write. A tests exactly what this session will commit, so the mini-air result belongs to this session. A dev-PC full run cannot exclude Session 99's ui/src changes, so it records them; if one breaks a test, S5 sends it to the coordinator. B, snapshot the whole working tree, ships Session 99's unreviewed work to the host and ties this result to it. C, wait for Session 99 to land, blocks this session on another. D, doing nothing, gives no rule for the shared tree. Undo: a wider path list. Two-way."
  - id: D-1317
    stage: planning
    question: "What if the guard fails a dev-PC test that the plan did not expect to touch the clipboard?"
    resolution: autonomous
    class: two-way
    mandatory: none
    chosen: "A: stop the row (S5) and record the receipts. The coordinator rules with D-1341 to D-1349: move that step to the gated file, or treat it as a product finding. Never widen the guard's allow-list or edit the test to pass. If the guard cannot go green at row 5 without product code, that is S3 and the grouping's split flag: the coordinator decides whether the moves ship alone."
    source_tag: Local Canon
    precedents:
      - ".agent/context/grouping/2026-11-20-e2e-devpc-clipboard-session-grouping.md:64-84 — the split flag"
      - "C:/Temp/av-kit/e2e-devpc-clipboard/edc-plan-writer-scan-head.txt — the static scan finds no test-side clipboard call beyond the ten the plan moves"
    research: { engine: none, sources: [] }
    reasoning: "Handed to the agent: USER_EXPLICIT 2026-11-18 'make the decisions always the recommenations', continuing USER_EXPLICIT 2026-11-20 'continue with next prompt'. An unexpected guard failure means a product path writes the clipboard where the plan found none; that is new information, and moving a test on the fly is an assertion change no row names (M-7). A keeps the guard honest. B, let the executor move the step, decides scope during execution. C, an allow-list, defeats the guard. D, doing nothing, is A without a route. Undo: none needed. Two-way."
  - id: D-1318
    stage: planning
    question: "Where is the guard written down for the next person?"
    resolution: autonomous
    class: two-way
    mandatory: none
    chosen: "A: a new Session 100 section in .agent/docs/e2e-remote-host.md (the copy file, CLIPBOARD_GUARD, the variable, the empty readers, the static scan, D-1301's per-file rule) and two lines in .agent/docs/commands.md beside Session 98's, inserted after a line found by text after a fresh read."
    source_tag: Local Canon
    precedents:
      - ".agent/context/grouping/2026-11-20-e2e-devpc-clipboard-session-grouping.md:64-84 — the run book and commands.md name the guard"
      - ".agent/docs/e2e-remote-host.md:222 — the Session 98 gated-stage section"
    research: { engine: none, sources: [] }
    reasoning: "Handed to the agent: USER_EXPLICIT 2026-11-18 'make the decisions always the recommenations', continuing USER_EXPLICIT 2026-11-20 'continue with next prompt'. The grouping asks for both. The run book is where the gated stage is explained; commands.md is what an agent reads before running E2E, so a short rule there prevents the next clipboard spec on the dev PC. test_s100_ac_18 pins both. B, the run book alone, misses the agent's first read. C, a new doc, adds a file to keep in sync. D, doing nothing, leaves the rule unwritten. Undo: remove the section and lines. Two-way."
  - id: D-1319
    stage: planning
    question: "How does the dev-PC runner keep both gated files off this machine?"
    resolution: autonomous
    class: two-way
    mandatory: none
    chosen: "A: flake-run.py's EXCLUDED names both gated files, and OLD_CLIPBOARD names the five source files Sessions 98 and 100 split (capture-filmstrip-actions, capture-import, console-chrome, mcp-setup-prompt, settings). It refuses with exit 2 before any run while one of them has a writer-scan hit. --list-check gives 237 at row 0 and 238 after rows 1 and 2."
    source_tag: Local Canon
    precedents:
      - "docs/execution/plans/2026-11-20-e2e-clipboard-specs/flake-run.py — CLIPBOARD_NEVER_DEVPC in Session 98's form"
      - "C:/Temp/av-kit/e2e-devpc-clipboard/edc-plan-selftest-flake-run.txt — the copy's selftest"
    research: { engine: none, sources: [] }
    reasoning: "Handed to the agent: USER_EXPLICIT 2026-11-18 'make the decisions always the recommenations', continuing USER_EXPLICIT 2026-11-20 'continue with next prompt'. The file-level guard already skips both gated files without the variable; the runner's exclusion is a second, independent wall, and its refusal stops a full run before the split lands. B, rely on the file guard alone, has one wall. C, read the exclusions from known-failures.json, makes row 1's runner depend on row 4's list. D, doing nothing, lets row 7 run the copy file at its listed skip. Undo: edit the two tuples. Two-way."
  - id: D-1320
    stage: planning
    question: "How does the guard prove that each clipboard function is replaced before a test calls it, and what happens when one is not?"
    resolution: autonomous
    class: two-way
    mandatory: none
    chosen: "A: clipboard-guard.cjs patches a fixed list of the twenty NAMES the probe found, looking each up on electron.clipboard and its prototype chain, and defines a tagged recorder (recorder.__avkitClipboardGuard === true) as an own property. It checks clipboard[name] === recorder for every name, and only then logs installed, sets the global marker and registers its hooks. A missing or unreplaced name writes a failed line, prints CLIPBOARD_GUARD: install failed, and exits 70, so the launch fails closed. Each AC-10 call site checks Reflect.get(<that function>, '__avkitClipboardGuard') before calling it. S100 AC-8 adds a fake with a writer on the prototype, one with a name missing and one with a name that cannot be replaced."
    source_tag: Local Canon
    precedents:
      - "C:/Temp/av-kit/e2e-devpc-clipboard/edc100-expert-pass.txt — F1: the plan checked only the global marker before AC-10's real writes"
      - "C:/Temp/av-kit/e2e-devpc-clipboard/probe/probe-result.jsonl — the twenty own properties on Electron 42.11.18"
      - "C:/Temp/av-kit/e2e-devpc-clipboard/edc-plan-shape-check.txt — the per-function tag check refuses a global-marker check, another function's tag and an unchecked call"
    research: { engine: none, sources: [] }
    reasoning: "Handed to the agent: USER_EXPLICIT 2026-11-18 'make the decisions always the recommenations', continuing USER_EXPLICIT 2026-11-20 'continue with next prompt'. The coordinator ruled F1 must be fixed. A makes each real call depend on the tag of the function about to be called, not on a flag set before the patch finished, and a guard that cannot patch stops the launch instead of running unguarded. M items: none; test code only, and it tightens D-1310. B, keep the global marker and own properties only, misses a writer a later Electron moves onto the prototype, and the marker can sit over a partial patch. C, check the tags in the spec only, lets every other spec run with a partial guard. D, doing nothing, keeps F1 open. Undo: restore the own-property loop. Two-way."
  - id: D-1321
    stage: planning
    question: "How does the guard's verdict reach the run when a spec swallows or races app.close()?"
    resolution: autonomous
    class: two-way
    mandatory: none
    chosen: "A: the preload appends each recorded call to its launch's log at call time. With a diag folder the log is clipboard-LAUNCH.jsonl in that folder (LAUNCH being the launch id), beside phases.jsonl (clipboardGuardLogPath, a fifth electron-env export) and is kept; without one it stays in the scratch folder. guard-logs.py reads only the folders a flake-run receipt names, or one --diag folder, and fails on any call or failed line outside the AC-10 launch and on a finished non-gated launch without exactly one installed line, counting the launches without one. It runs at rows 5, 7 and 8 (host/diag) and as the gate's guard-logs and guard-logs-remote steps. The throw at close stays as the early signal, joined with the main-error message."
    source_tag: Local Canon
    precedents:
      - "C:/Temp/av-kit/e2e-devpc-clipboard/edc100-expert-pass.txt — F2"
      - "ui/tests/e2e/electron-app.ts:157-169 — the verdict is read only in the wrapped close; capture-inbox.test.ts:1941, electron-harness.test.ts:93 and :113, main-rejection-watch.test.ts:72 and :91 and five closeBounded helpers swallow or race close"
      - "ui/tests/e2e/electron-app.ts:114-143 — diagDir, the launch id and the launch-start and launch-end phase lines"
      - "C:/Temp/av-kit/e2e-devpc-clipboard/edc-plan-selftest-guard-logs.txt — guard-logs.py selftest, 19 of 19"
    research: { engine: none, sources: [] }
    reasoning: "Handed to the agent: USER_EXPLICIT 2026-11-18 'make the decisions always the recommenations', continuing USER_EXPLICIT 2026-11-20 'continue with next prompt'. The coordinator ruled F2 must be fixed. A makes the verdict a file the gate reads, so no spec's close handling can hide a call. M items: none. M-3 is checked and not hit: it enforces D-1310's rule and adds none. M-4 is checked and not hit: a log file and a plan-local checker, no API, product exit code or summary key. B, fix each swallowing spec, edits files and assertions the plan does not own (M-7). C, a Playwright fixture that fails the test, touches every spec. D, doing nothing, lets a call in those specs pass. Undo: drop the log path and the two gate steps. Two-way."
  - id: D-1322
    stage: planning
    question: "How is the renderer patch kept in place across reloads, and the async Clipboard API before it?"
    resolution: autonomous
    class: two-way
    mandatory: [M-8]
    chosen: "A: register the renderer patch with wc.on('dom-ready'), not once, so it is applied again after installSettingsSeam reloads the page; rendererGuard returns early when the page is already marked. The guard also sets session.setPermissionRequestHandler and setPermissionCheckHandler once per guarded session, denying and recording clipboard-read and clipboard-sanitized-write and allowing every other permission, as test-only code. The window between the navigation's commit and dom-ready, where execCommand('copy') is not yet patched, is a named residual risk."
    source_tag: Local Canon
    precedents:
      - "C:/Temp/av-kit/e2e-devpc-clipboard/edc100-expert-pass.txt — F3"
      - "ui/tests/e2e/mcp-setup-prompt.test.ts:38-66 — installSettingsSeam adds an init script, then reloads the page"
      - "ui/src — no setPermissionRequestHandler or setPermissionCheckHandler at f1ba411, so the guard's handlers replace no product handler"
    research: { engine: none, sources: [] }
    reasoning: "Handed to the agent: USER_EXPLICIT 2026-11-18 'make the decisions always the recommenations', continuing USER_EXPLICIT 2026-11-20 'continue with next prompt'. M-8: the grouping named the guard's main and renderer calls; denying two permissions in every guarded launch and patching every load is wider. A closes the reload gap and covers the async API before the patch. B, once plus a check after each reload, still leaves the window. C, the permissions only, leaves execCommand after load unrecorded. D, doing nothing, keeps F3 open. Undo: once again, and drop the two handlers. Two-way."
  - id: D-1323
    stage: planning
    question: "How does AC-10 wait for the renderer call before it closes the app?"
    resolution: autonomous
    class: two-way
    mandatory: none
    chosen: "A: main keeps globalThis.__avkitClipboardGuardCalls, which record() pushes in the same call that appends to the log, and the spec polls app.evaluate of that list with expect.poll, bounded at 10 s, until it holds main writeText, renderer writeText and webContents copy; then it closes."
    source_tag: Local Canon
    precedents:
      - "C:/Temp/av-kit/e2e-devpc-clipboard/edc100-expert-pass.txt — F4: the renderer call reaches main through an asynchronous console message"
      - "Session 98 RULE-1 — a bounded wait with a named failure, never a sleep"
    research: { engine: none, sources: [] }
    reasoning: "Handed to the agent: USER_EXPLICIT 2026-11-18 'make the decisions always the recommenations', continuing USER_EXPLICIT 2026-11-20 'continue with next prompt'. A uses a list the main process holds, so close never races the console message, and a lost call fails the poll with the list printed. M items: none. B, an IPC sendSync from the dom-ready script to a handler the preload registers, adds a channel and a page-side preload. C, a fixed sleep, is a flake. D, doing nothing, keeps the race. Undo: drop the poll. Two-way."
  - id: D-1324
    stage: planning
    question: "Does the guard cover webContents.copy and cut and the copy chords?"
    resolution: autonomous
    class: two-way
    mandatory: [M-3, M-8]
    chosen: "A: on web-contents-created the guard replaces wc.copy and wc.cut with tagged recorders, and a before-input-event handler records and prevents Control or Meta with C or X, Control+Insert and Shift+Delete on keyDown, which also stops the Edit menu's accelerators. S100 AC-8 proves both on a fake; AC-10 calls wc.copy() after its tag check."
    source_tag: Local Canon
    precedents:
      - "C:/Temp/av-kit/e2e-devpc-clipboard/edc100-expert-pass.txt — F5"
      - "Electron webContents.copy and cut, and the before-input-event event with event.preventDefault"
    research: { engine: none, sources: [] }
    reasoning: "Handed to the agent: USER_EXPLICIT 2026-11-18 'make the decisions always the recommenations', continuing USER_EXPLICIT 2026-11-20 'continue with next prompt'. M-3: the standing rule now also fails a guarded launch that presses a copy chord, so a later spec that needs one must be gated. M-8: the grouping named clipboard calls, not chords or webContents methods. A closes the native paths a JS patch cannot see, except a mouse click on the menu (D-1325). B, the static scan alone, misses a chord sent through a helper. C, wrap wc.copy only, leaves the chords. D, doing nothing, keeps F5 open. Undo: drop the two hooks. Two-way."
  - id: D-1325
    stage: planning
    question: "Does the guard remove the default Edit menu in guarded launches?"
    resolution: autonomous
    class: two-way
    mandatory: none
    chosen: "A: no. The Edit menu's copy, cut, paste and pasteAndMatchStyle items clicked with the mouse stay a named residual risk (corrected by D-1331: on Windows, Electron 42.11.18 runs these roles as calls on the focused webContents object, so the D-1324 and D-1331 recorders most likely catch them, not run-proven; on macOS they are native selectors). Menu.setApplicationMenu(null) is not set, because it changes the window's menu bar, its layout and every accelerator in each guarded run; the chord block of D-1324 already stops the menu's keyboard accelerators, and no spec clicks the menu bar."
    source_tag: Local Canon
    precedents:
      - "C:/Temp/av-kit/e2e-devpc-clipboard/edc100-expert-pass.txt — F5: the default Edit menu role"
      - "ui/src/main — no setApplicationMenu at f1ba411 (only the tray's Menu.buildFromTemplate), so the window shows Electron's default menu"
    research: { engine: none, sources: [] }
    reasoning: "Handed to the agent: USER_EXPLICIT 2026-11-18 'make the decisions always the recommenations', continuing USER_EXPLICIT 2026-11-20 'continue with next prompt'. The ruling asked for setApplicationMenu(null) only if it fits with no product effect; it does not, because every guarded run would lose the menu bar the product shows, and spec layouts read that window. A keeps the run the same as the product and names the one gap. M items: none. B, setApplicationMenu(null) in the guard, changes what every dev-PC spec sees. C, replace the menu with a copy-less one, still changes the menu. D is A without the residual written down. Undo: none needed. Two-way."
  - id: D-1326
    stage: planning
    question: "How wide is the static scan, and what are the launch helpers exempt from?"
    resolution: autonomous
    class: two-way
    mandatory: none
    chosen: "A: writer-scan.py and S100 AC-5 run each pattern over the whole file text, so a chain split across lines matches; they add CSS locator strings and variables bound to a copy locator, the chords Control+KeyC, Control+Insert and Shift+Delete (with the Meta and ControlOrMeta forms), webContents.copy and cut, and role, text, label and title locators whose argument holds copy as a word start, /copy/i included. electron-app.ts and electron-env.ts are exempt from the launch kind only. Re-measured: 10 hits at f1ba411, 8 after the split, 0 after row 4; the selftest passed 39 of 39, and 56 of 56 with the paste kinds of D-1331."
    source_tag: Local Canon
    precedents:
      - "C:/Temp/av-kit/e2e-devpc-clipboard/edc100-expert-pass.txt — F6"
      - "C:/Temp/av-kit/e2e-devpc-clipboard/edc-plan-writer-scan-head.txt, -split.txt, -after.txt — 10, 8 and 0"
      - "C:/Temp/av-kit/e2e-devpc-clipboard/edc-plan-selftest-writer-scan.txt — 56 of 56 after D-1331"
    research: { engine: none, sources: [] }
    reasoning: "Handed to the agent: USER_EXPLICIT 2026-11-18 'make the decisions always the recommenations', continuing USER_EXPLICIT 2026-11-20 'continue with next prompt'. M items: none; the scan is test tooling and its counts did not move. A makes the scan match what the plan claims. B, keep it line-based, misses multi-line chains. C, a TypeScript AST scan, adds a parser for a second wall. D, doing nothing, keeps F6 open. Undo: restore the line patterns. Two-way."
  - id: D-1327
    stage: planning
    question: "Does the moved (e) test also check that the app kept the seeded token?"
    resolution: autonomous
    class: two-way
    mandatory: none
    chosen: "A: one added line after (e)'s loop, expect(readFileSync(join(appData, 'mcp-token.txt'), 'utf8')).toBe(token plus a newline), proves the app read the seed and did not replace it, so (e) checked the token the app serves. It is a new assertion in a moved test, named in row 2 and in §Test pins under HDP :158; no existing assertion line changes, and split-specs.py --check requires the line once."
    source_tag: Local Canon
    precedents:
      - "C:/Temp/av-kit/e2e-devpc-clipboard/edc100-expert-pass.txt — F7"
      - "ui/src/main/index.ts:162-170 — readOrCreateMcpToken reads mcp-token.txt trimmed and writes only when it is absent"
      - ".agent/docs/human-decision-protocol.md :158 — a new assertion is named in the row that adds it"
    research: { engine: none, sources: [] }
    reasoning: "Handed to the agent: USER_EXPLICIT 2026-11-18 'make the decisions always the recommenations', continuing USER_EXPLICIT 2026-11-20 'continue with next prompt'. M items: none. M-7 is checked and not hit: the line is new and named in the row that adds it, and no existing assertion changes. B, record it as a residual, leaves (e) able to pass against a token the app made itself. C, read the token over the app's API, adds a backend call. D, doing nothing, keeps F7 open. Undo: drop the line. Two-way."
  - id: D-1328
    stage: planning
    question: "Does the moved C1-5 step keep its route context and close the app on failure?"
    resolution: autonomous
    class: two-way
    mandatory: none
    chosen: "A: the new C1-5 test copies C1-5's /settings/app route (console-chrome.test.ts:79-86 at f1ba411) before it opens the Console, so the Console opens as it does in the source, and wraps its steps in try/finally with app.close() in the finally, as the file's other tests do. The copied lines get two more spaces of indent; split-specs.py proves them and refuses a lost route line and a test without its finally."
    source_tag: Local Canon
    precedents:
      - "C:/Temp/av-kit/e2e-devpc-clipboard/edc100-expert-pass.txt — F8"
      - "ui/tests/e2e/console-chrome.test.ts:77-101 at f1ba411 — C1-5 with its route"
      - "C:/Temp/av-kit/e2e-devpc-clipboard/edc-plan-split-out-4.txt — the built files; edc-plan-selftest-split-specs.txt — 13 cases"
    research: { engine: none, sources: [] }
    reasoning: "Handed to the agent: USER_EXPLICIT 2026-11-18 'make the decisions always the recommenations', continuing USER_EXPLICIT 2026-11-20 'continue with next prompt'. M items: none; no assertion changes, and the kept C1-5 keeps its route. B, no route, lets the Console's GET of /settings/app reach a missing backend and start in another state. C, close without finally, leaves an app open after a failed assertion. D, doing nothing, keeps F8 open. Undo: drop the route lines and the try. Two-way."
  - id: D-1329
    stage: planning
    question: "How is it proved that no new file carries a skip, only or todo literal?"
    resolution: autonomous
    class: two-way
    mandatory: none
    chosen: "A: row 6 runs a Python check that builds the nine forms (test, it or describe with .skip, .only or .todo) from parts and finds none in ui/tests/unit/e2e-clipboard-guard.test.ts or clipboard-guard.cjs, and in each new E2E spec only its one file-level test.skip( guard, which D-1305 and D-1313 require. The unit file builds any such literal it needs from parts, as AC-43.13 does."
    source_tag: Local Canon
    precedents:
      - "C:/Temp/av-kit/e2e-devpc-clipboard/edc100-expert-pass.txt — F9"
      - "ui/tests/unit/queue-primitives.test.ts:829-844 (AC-43.13) and queue-card.test.ts:773-777 (AC-44.13) — the eight literals forbidden in ui/tests/unit"
    research: { engine: none, sources: [] }
    reasoning: "Handed to the agent: USER_EXPLICIT 2026-11-18 'make the decisions always the recommenations', continuing USER_EXPLICIT 2026-11-20 'continue with next prompt'. AC-43.13 and AC-44.13 fail the full Vitest suite on such a literal anywhere in ui/tests/unit, and an .only in an E2E spec would narrow a run silently. M items: none. B, rely on the Vitest sweeps, misses the E2E files. C, an ESLint rule, changes the shared config. D, doing nothing, keeps F9 open. Undo: drop the check. Two-way."
  - id: D-1330
    stage: planning
    question: "How does this session keep Session 99's files out of tested_state and its receipts, and what do Session 99's tracked writes do to the gate?"
    resolution: autonomous
    class: two-way
    mandatory: [M-6]
    chosen: "A: identity.py gets PEER_PREFIXES (docs/execution/plans/2026-11-20-help-quick-start/, .agent/context/handoffs/2026-11-20-help-quick-start-, docs/execution/reflections/2026-11-20-help-quick-start) and drops them by git pathspec and by name before any content read, tracked or untracked; baseline.ps1 and session-gate.ps1 already name that folder only and now name the reflection prefix without a dash. Session 99's tracked writes (ui/src, the docs, the registers) still enter tested_state through the one tracked-diff digest, because the suites read them. No plan-folder file or receipt holds a content hash of a Session 99-class path that differs from HEAD: baseline-scope.json records peer-dirty, named only; the row-0 dirty hashes, the gate output and edc-foreign-7.json name those paths. A peer write after the gate fails identity-after or H1-6b, and the action is to rerun H1-2; this session never fails, reverts or stashes Session 99's work, and a test failure that Session 99's code causes is S5 to the coordinator. The identity selftest proves peer files unread and unbound, own inputs still bound; a copy without the exclusions fails 23 cases."
    source_tag: Local Canon
    precedents:
      - "C:/Temp/av-kit/edc-plan-review-round-1.md — EDC-R1-2: identity.py read Session 99's untracked handoff into tested_state"
      - "C:/Temp/av-kit/dispatch/s100-planner-brief.md — never read, bind, hash or commit Session 99's folder"
      - "C:/Temp/av-kit/e2e-devpc-clipboard/edc-plan-selftest-identity.txt — 0 failures; edc-plan-identity-mutant.txt — 23 failures without the exclusions"
      - "D-1316 — Session 99's foreign class, amended here"
    research: { engine: none, sources: [] }
    reasoning: "Handed to the agent: USER_EXPLICIT 2026-11-18 'make the decisions always the recommenations', continuing USER_EXPLICIT 2026-11-20 'continue with next prompt'. M-6: the brief says never bind Session 99's folder, and a tested_state must cover every input the suites read, which includes Session 99's ui/src writes. A takes both as far as they go: the peer folder, handoffs and reflection are never read, and its tracked writes count only inside one digest, never as a published per-file hash. B, hash and record every dirty path, publishes Session 99's content hashes in this session's receipts. C, wait for or freeze Session 99, blocks a parallel session this plan does not own. D, doing nothing, keeps the peer handoff in tested_state, which round 1 refused. Undo: drop PEER_PREFIXES and the peer-dirty marker. Two-way."
  - id: D-1331
    stage: planning
    question: "Does the guard and the static scan also cover the native paste path?"
    resolution: autonomous
    class: two-way
    mandatory: [M-3, M-8]
    chosen: "A: on web-contents-created the guard also replaces wc.paste, wc.pasteAndMatchStyle and wc.copyImageAt with tagged recorders that never call the original (paste kinds logged as read, copyImageAt as write); before-input-event also records and prevents Control or Meta with V, with or without Shift, and Shift+Insert; rendererGuard also records execCommand('paste'). wc.replace and wc.replaceMisspelling are not wrapped: they insert the given text and read no clipboard. writer-scan.py and S100 AC-5 refuse .paste(, pasteAndMatchStyle, .copyImageAt(, execCommand('paste'), Control+V, Control+Shift+V and Shift+Insert outside the gated files. The gated capture file presses Control+V three times and is allowed; no other file pastes, so the counts stay 10, 8 and 0, and the selftest passes 56 of 56 (a copy without the paste kinds fails 12). Proven on fakes and tag-checked recorders only; no real paste or clipboard read runs on the dev PC. D-1325 is corrected: Electron 42.11.18 runs the menu roles as calls on the focused webContents object outside macOS."
    source_tag: Local Canon
    precedents:
      - "C:/Temp/av-kit/edc-plan-review-round-1.md — EDC-R1-1: native paste bypassed the guard and the scans"
      - "C:/Temp/av-kit/e2e-devpc-clipboard/edc-plan-electron-roles.txt — the role table and execute in electron.exe 42.11.18"
      - "C:/Temp/av-kit/e2e-devpc-clipboard/edc-plan-writer-scan-gated-files.txt — the gated capture file's three Control+V presses"
      - "C:/Temp/av-kit/e2e-devpc-clipboard/edc-plan-selftest-writer-scan.txt — 56 of 56; edc-plan-writer-scan-mutant.txt — 12 failures without the paste kinds"
      - "D-1324 — the copy hooks this widens"
    research: { engine: none, sources: [] }
    reasoning: "Handed to the agent: USER_EXPLICIT 2026-11-18 'make the decisions always the recommenations', continuing USER_EXPLICIT 2026-11-20 'continue with next prompt'. M-3: the standing rule now also fails a guarded launch that pastes, so a later spec that needs a paste must be gated. M-8: the grouping named writers; D-1311 added the clipboard readers, and the native paste path, which reads Mat's clipboard into the page, and copyImageAt, which writes it, are further paths no grouping item named. A closes the paste path the JS patch could not see, at the same depth as D-1324. B, also add a tag-checked wc.paste call to AC-10, changes guard-logs.py's three-call contract and adds a dev-PC call for no new proof beyond the fake. C, Menu.setApplicationMenu(null), changes every guarded run (D-1325). D, doing nothing, leaves EDC-R1-1 open. Undo: drop the three recorders, the three chords and the scan kinds. Two-way."
  - id: D-1341
    stage: execution
    question: "Row 7's dev-PC full run failed AC-81.11 in capture-inbox.test.ts (F2 held by another process, expected HELD, received FAILED 0). Is it this session's, and what happens to row 7?"
    resolution: autonomous
    class: two-way
    mandatory: []
    chosen: "A (coordinator ruling under the hand-over): environmental and not this session's. RegisterHotKey(F2) returns error 1409 while ShareX, started 2026-11-20 21:18, runs on the dev PC; the five electron.exe processes are av-kit MCP servers, not the holder. Nobody stops ShareX; the coordinator asked Mat to free F2. Row 7's receipts are renamed with -r1 and the flake receipt is kept; row 8 runs as written; the F2 probe (a copy of coord/f2-probe.ps1) runs before the row-7 rerun and before H1-2, at most every 10 minutes and only while nothing else runs; on F2 free, row 7 reruns once, unchanged (Session 53 RULE-4). If F2 is still held when every row that does not need the dev-PC E2E is done, the session stops and reports. The gate's E2E step never runs against a held F2."
    source_tag: Local Canon
    precedents:
      - "C:/Temp/av-kit/e2e-devpc-clipboard/coord/f2-probe.txt — the coordinator's probe: F2 held, error 1409; ShareX running"
      - "C:/Temp/av-kit/e2e-devpc-clipboard/edc-s5-rename-r1.txt — row 7's receipts renamed with -r1"
      - "C:/Temp/av-kit/e2e-devpc-clipboard/edc-full-7-r1.txt — 237 passed, 1 failed (AC-81.11), 0 guard and 0 rejection lines"
      - "Session 53 RULE-4 — a rerun is once and unchanged"
    research: { engine: none, sources: [] }
    reasoning: "Handed to the agent: USER_EXPLICIT 2026-11-18 'make the decisions always the recommenations', continuing USER_EXPLICIT 2026-11-20 'continue with next prompt'. The coordinator ruled this under the hand-over after the S5 stop. M items: none. The failing test checks that the app reports a held F2, and another program holds F2 on this PC; no file of this session touches the hotkey path. B, stop ShareX, ends a program of Mat's that this session does not own. C, record the failure as known, hides a real product check. D, doing nothing, leaves row 7 and H1-2 unrunnable. Undo: none needed; the rerun is a fresh receipt. Two-way."
  - id: D-1342
    stage: execution
    question: "Session 99 wrote further paths during row 7 (its skill folder, tool and test) and has listed every path it will write. How does this session keep them in the Session 99 class and its own counts its own?"
    resolution: autonomous
    class: two-way
    mandatory: [M-6]
    chosen: "A (coordinator ruling under the hand-over, extended with Session 99's full list): Session 99's class gains .agent/skills/asd-ste100/, tools/help_guide_ste.py, tests/tooling/test_help_guide_ste.py, ui/tests/e2e/test-ids.ts, ui/tests/unit/failure-reason-copy.test.ts, ui/tests/unit/help-quick-start.test.tsx, ui/tests/unit/help-shots-privacy.test.ts, ui/tests/e2e/help-quick-start.test.ts, ui/tests/help-shots/, ui/playwright.help-shots.config.ts, ui/package.json and ui/tsconfig.json (ui/src/ was already in it), by name in session-gate.ps1 S99_PATHS, baseline.ps1 SESSION99_PATHS (recorded only; row 0 does not rerun) and row 7's foreign record (cmd/row7.ps1). identity.py gets PEER_UNTRACKED: Session 99's untracked files (every untracked file under ui/src/, which this session never writes, and its new skill, tool, test and help-shots files) are dropped by name before any read, never read or bound; its tracked edits stay bound by the tracked diff. Its new test files are excluded by name from this session's runs: py-tests --ignore and py-lint --extend-exclude for its Python test, ui-tests --exclude for its two new unit files, flake-run.py PEER_EXCLUDED (rows 7 and H1-2 stay at 238) and guard-check.py PEER_FILES (243 tests, 32 files). writer-scan.py prints a hit in its new E2E file as a Session 99 finding, not counted; this session's files are never set aside. Row 8's snapshot stays HEAD plus this session's eleven paths, so the mini-air proves them on HEAD's product code without Session 99's ui/src or test-ids.ts changes. The paths are never opened by this session; a gate failure traced to Session 99's work stops and reports, and a Session 99 write after the gate reruns H1-2 (D-1330). Old and new hashes: edc-d1342-hashes.txt and edc-d1342-hashes-final.txt; selftests pass (identity 0 failures, flake-run 0, guard-check 14 cases 0 wrong, writer-scan 57 of 57); ruff clean."
    source_tag: Local Canon
    precedents:
      - "D-1330 — Session 99's class and the rerun rule, widened here"
      - "C:/Temp/av-kit/e2e-devpc-clipboard/edc-d1342-hashes.txt — the scripts' old and new SHA-256"
      - "C:/Temp/av-kit/e2e-devpc-clipboard/edc-d1342-selftest-identity.txt — 11 D-1342 files unread and unbound; own inputs beside them bound"
    research: { engine: none, sources: [] }
    reasoning: "Handed to the agent: USER_EXPLICIT 2026-11-18 'make the decisions always the recommenations', continuing USER_EXPLICIT 2026-11-20 'continue with next prompt'. The coordinator ruled this under the hand-over, with Session 99's coordinator's full list of its paths. M-6: never open Session 99's files, while tested_state binds every input the suites read; A keeps D-1330's split, untracked peer files named only and tracked edits bound through the one digest, and keeps this session's counts its own by excluding Session 99's new tests by name. The cost: a change to Session 99's untracked files after the gate does not move tested_state; scope-paths names them, and the coordinator relays Session 99's writes. B, read and hash Session 99's new files, breaks the never-open rule. C, wait for Session 99 to commit, moves HEAD, which is a stop. D, doing nothing, fails scope-paths (S4) on the new paths and reads them into tested_state and receipts. Undo: drop the added names, PEER_UNTRACKED and the exclusions. Two-way."
  - id: D-1343
    stage: execution
    question: "Row 7's rerun after F2 was freed stopped in Playwright's global setup before any test: ui/out/main/index.js (built 2026-11-20 23:50, not by this session) is older than Session 99's ui/src edits. How does row 7 run, and what does the dev-PC E2E cover?"
    resolution: autonomous
    class: two-way
    mandatory: [M-6]
    chosen: "A (coordinator ruling under the hand-over, the executor's recommendation): Session 99 freezes ui/src, electron.vite.config.ts, package.json and tsconfig.json, builds nothing, writes nothing to ui/out and launches no Electron until the coordinator ends the window; its ui/src on disk is its finished state for row 7. The refused attempt started no test, so it does not spend Session 53 RULE-4's one rerun; its receipts are renamed with -r2 (edc-rename-r2.txt) and -r1 stays the F2 run. npm --prefix ui run build runs once through pwsh with ELECTRON_RUN_AS_NODE unset (edc-build-7.txt), then row 7 reruns once, unchanged. The dev-PC E2E covers HEAD plus Session 99's ui/src on disk; row 8's mini-air run covers HEAD plus this session's eleven paths. Session 99's class also gains ui/tests/unit/capture-page.test.ts, convert-page.test.ts and settings-page.test.ts (its D-1296 pinned literals AC-39.13, AC-33.18 and AC-61.16): named only in session-gate.ps1 S99_PATHS, baseline.ps1 SESSION99_PATHS (recorded only) and row 7's foreign record, never opened, bound by the tracked diff and run as usual. Old and new hashes: edc-d1343-hashes.txt."
    source_tag: Local Canon
    precedents:
      - "D-1341 — the F2 ruling; row 7 reruns once, unchanged"
      - "D-1342 — Session 99's class, widened here"
      - "C:/Temp/av-kit/e2e-devpc-clipboard/flake/epf-row7-1-20261121T063516-18388-e31174.txt — global setup refused the stale build, no test ran"
    research: { engine: none, sources: [] }
    reasoning: "Handed to the agent: USER_EXPLICIT 2026-11-18 'make the decisions always the recommenations', continuing USER_EXPLICIT 2026-11-20 'continue with next prompt'. The coordinator ruled this under the hand-over after the stop. M-6: Session 99's files are never opened; the three unit files join its class by name and stay bound through the tracked digest. A build from the frozen tree is the only way the dev-PC E2E can run before Session 99 commits; the freeze keeps the build and tested_state stable for row 7 and H1-2. B, wait for Session 99's commit, moves HEAD, which is a stop and a re-plan. C, doing nothing, leaves row 7, row 9 onward and the gate unrunnable. Undo: drop the three names; the build output is not tracked. Two-way."
open_decisions: []
```

Expert pass (fresh context): adopted (`edc100-expert-pass.txt`): F1 to F9 as D-1320 to D-1329; F10 (Pin MCP config is no longer clicked by any E2E spec) stays named in D-1308 and the handoff.

### D-1305: Do the moved steps join the existing gated file or a second one?

**I recommend A: a second gated file, `copy-system-clipboard.test.ts`, listed after the capture file.** The capture file stays what Session 98 measured, so the primer count stays clean, and the tool already takes a list, so no tool or host script changes. One pin, `test_ac_11_known_tracked_list`, changes, named with its old and new value in row 3. A can fail if the launcher treats a second file differently; `test_s100_ac_11_run_carries_both_gated_files` proves the path on the fake host and row 8 on the real one. Undo: drop the entry and the file.

- B: append the three tests to the capture file. Copy failures mix into the primer count.
- C: a separate stage for the copy file. A launcher change nobody asked for.
- D: do nothing. Four writers stay on the dev PC.

Refs: grouping `:64-84`; `e2e_remote.py:421`, `:987`; `run-e2e.ps1:263-288`; `test_e2e_remote.py:1564-1576`.

### D-1306: Which lines move, and how is the move proved?

**I recommend A: a scripted move from the `f1ba411` blobs.** Each clipboard line is copied byte for byte with the steps that reach it; the kept files lose only those lines, each replaced by a named comment, and stay CRLF. `--check` proves all four files. A can fail if a moved step needs a helper the script missed; `tsc` and ESLint on the built files passed at plan time. Undo: restore from `f1ba411`.

- B: edit by hand. No byte check.
- C: move whole tests. Non-clipboard assertions leave the dev PC.
- D: do nothing.

Refs: D-1303; Session 98's `split-specs.py`; `edc-plan-split-out-4.txt`, `edc-plan-split-out-eslint.txt`.

### D-1307: Where does (e) get the token once (d) moves?

**I recommend A: seed a fresh random token into the test's own scratch app data before launch.** The app reads `mcp-token.txt` when it exists, so (e) knows the token without the clipboard, and its assertion lines keep their bytes. The token is new each run and never Mat's. A can fail silently if the app stopped reading the file: (e) would then check a token the app never used. `index.ts:162-170` reads the file first today; the handoff names that dependency. Undo: restore `launchApp`.

- B: read the token from the scratch folder after launch. A wait on the app's write.
- C: move (e) into the gated file. A non-clipboard assertion leaves the dev PC.
- D: do nothing. (e) keeps reading the clipboard.

Refs: `index.ts:162-170`; `mcp-setup-prompt.test.ts:28`, `:138-151`.

### D-1308: What happens to `W4-3`'s two copy clicks?

**I recommend A: retire them.** They assert nothing of their own. Copy MCP config is still clicked, and its clipboard content checked, in the gated (d). Pin MCP config's click is then actuated by no E2E spec; the plan and the handoff name that. Undo: restore two lines.

- B: a fourth gated test for both clicks. A test D-1303 did not name, and another token write.
- C: keep them under the guard. `W4-3` would fail.
- D: do nothing. Two writes per dev-PC run, one a token.

Refs: `settings.test.ts:216-217`; `SettingsPage.tsx:533-536`.

### D-1309: What are the six titles?

**I recommend A: the moved tests keep their source id and name only their clipboard step; the kept titles drop only the moved clause.** Undo: rename.

- B: keep the old titles. They would claim a step the test no longer has.
- C: new ids. The link to the owning MEU is lost.
- D: do nothing. Same as B.

Refs: `console-chrome.test.ts:77`; `mcp-setup-prompt.test.ts:91`, `:126`.

### D-1310: How does a non-gated launch fail on a clipboard call? (M-3)

**I recommend A: a `-r` preload, added by the one launch helper unless the variable is `1`, that replaces every clipboard function in main and the renderer's clipboard methods with recorders, and a check at close that fails with `CLIPBOARD_GUARD:`.** Every spec launches through the helper, and the recorders never call the originals, so a guarded launch cannot touch your clipboard. **This is a new rule (M-3):** any later spec that needs the clipboard must live in a gated file. A misses a native Ctrl+C and a renderer write before the page is ready; both are named. Undo: drop the guard argument.

- B: a test hook in the product. Product code, which the gate forbids.
- C: the static scan alone. Misses a write reached through a button.
- D: do nothing. The next missed writer reaches your clipboard.

Refs: D-1304; `electron-env.ts:20-23`; `D/probe/probe-result.jsonl`; Session 98 RULE-1.

### D-1311: Writers only, or readers too? (M-8)

**I recommend A: guard the readers too.** A dev-PC test that reads the clipboard reads what you copied last. The readers return empty values and fail the test like a write. **This goes beyond the grouping, which named the writers (M-8).** Undo: limit the recorder to writer names.

- B: writers only. Reads of your clipboard stay possible.
- C: readers return a sentinel. Hides a reading test instead of failing it.
- D: do nothing. Same as B.

Refs: `D/probe/probe-result.jsonl`; D-1299.

### D-1312: Static scan as a fallback, or a tracked test? (M-8)

**I recommend A: a tracked Vitest test beside the runtime guard.** It catches a new clipboard spec before any E2E runs, and a spec that launches Electron without the helper, which the guard cannot see. **The grouping offered it only as the fallback (M-8).** Undo: delete the test.

- B: the runtime guard alone.
- C: a plan-local script. Stops guarding after this session.
- D: do nothing. Same as B.

Refs: D-1304; `edc-plan-writer-scan-head.txt`, `-split.txt`, `-after.txt`.

### D-1313: How is the guard proven in a real launch?

**I recommend A: one E2E spec in every non-gated run.** It checks the guard is in place before each call, so it cannot write even before the guard exists, and expects close to fail naming both calls. The dev-PC run and the mini-air main stage then have 238 tests. Undo: delete the spec.

- B: a Vitest test with a fake Electron only. The real hook is never proved.
- C: run it in the gated stage. Proves nothing about the dev PC.
- D: do nothing.

Refs: grouping `:76-80`; `edc-plan-list-head.txt`.

### D-1314: How does a gated run count for PRIMER now? (M-6)

**I recommend A: per file.** A run counts only when the gated outcome is `run` and both capture tests pass; the copy tests never decide PRIMER, and a copy failure is a finding. **D-1301's "2 of 2" was written for one file (M-6).** This session can reach at most 3 of 5, so PRIMER stays open. Undo: change `gated-count.py`.

- B: require all five gated tests. Resets the count for an unrelated reason.
- C: count any outcome. Counts stages that read nothing.
- D: do nothing. The bar stays unclear.

Refs: D-1301; `e2e_remote.py:987`.

### D-1315: What happens to the two issues?

**I recommend A: resolve DEVPC on rows 7 and 8; give PRIMER the run's verification and keep it open unless the tally reads close.** Undo: reopen.

- B: resolve DEVPC only after a gated `run`. Ties it to whether you were connected.
- C: close PRIMER now. Breaks D-1301.
- D: do nothing. A fixed issue stays open.

Refs: the brief; Session 98's `issue-resolve.py`.

### D-1316: What reaches the mini-air while Session 99 shares the tree? (M-6)

**I recommend A: `HEAD` plus this session's eleven code and test paths only.** Session 99's changes are recorded by name in every dev-PC full run, never content-hashed in a receipt, and never fail this session (amended by D-1330). **"The final tree" and "never bind Session 99's work" conflict while both write (M-6).** Undo: a wider path list.

- B: the whole working tree. Ships Session 99's unreviewed work to the host.
- C: wait for Session 99. Blocks this session.
- D: do nothing. No rule for the shared tree.

Refs: the brief; Session 97's `snapshot-commit.py`; Session 92 RULE-3.

### D-1317: What if the guard fails an unexpected test?

**I recommend A: stop the row; the coordinator rules with D-1341 to D-1349.** Never widen the guard or edit the test. If the guard cannot go green without product code, the coordinator decides whether the moves ship alone (the split flag). Undo: none needed.

- B: let the executor move the step. Scope decided during execution.
- C: an allow-list. Defeats the guard.
- D: do nothing. Same as A without a route.

Refs: grouping `:64-84`; `edc-plan-writer-scan-head.txt`.

### D-1318: Where is the guard written down?

**I recommend A: a Session 100 section in the run book and two lines in `commands.md`.** Undo: remove them.

- B: the run book alone. Misses the agent's first read.
- C: a new doc. Another file to keep in sync.
- D: do nothing.

Refs: grouping `:64-84`; `e2e-remote-host.md:222`.

### D-1319: How does the dev-PC runner keep both gated files off this machine?

**I recommend A: exclude both by name and refuse while a source file still has a writer.** Undo: edit the two lists.

- B: the file guard alone. One wall.
- C: read the list from `known-failures.json`. Row 1 would depend on row 4.
- D: do nothing. Row 7 would run the copy file at its skip.

Refs: Session 98's `flake-run.py`; `edc-plan-selftest-flake-run.txt`.

### D-1320: How does the guard prove each function is replaced, and what if one is not?

**I recommend A: a fixed list of the twenty names, looked up on the object and its prototype chain, each replaced by a tagged recorder and checked; "installed" only when all twenty pass, else the launch exits 70.** Each real call in AC-10 checks the tag of the exact function it is about to call. A partial patch can no longer look installed, and a guard that cannot patch stops the run instead of letting it go unguarded. Undo: restore the own-property loop.

- B: keep the global marker and own properties only. A writer moved onto the prototype slips through.
- C: check the tags only in the spec. Other specs run with a partial guard.
- D: do nothing. F1 stays open.

Refs: `edc100-expert-pass.txt` F1; `D/probe/probe-result.jsonl`; `edc-plan-shape-check.txt`.

### D-1321: How does the verdict survive a spec that swallows `close`?

**I recommend A: write each call to the launch's log when it happens, keep the logs in the run's diag folders, and let `guard-logs.py` fail the run on any call or failure line in any launch.** The throw at `close` stays as the early signal. Several specs swallow or race `close`, so the file is the verdict. Undo: drop the log path and the two gate steps.

- B: fix each swallowing spec. Edits files and assertions this plan does not own.
- C: a Playwright fixture. Touches every spec.
- D: do nothing. A call in those specs passes.

Refs: `edc100-expert-pass.txt` F2; `electron-app.ts:114-169`; `edc-plan-selftest-guard-logs.txt`.

### D-1322: How is the page patch kept across reloads? (M-8)

**I recommend A: patch on every `dom-ready`, and deny the two clipboard permissions in every guarded launch.** The settings seam reloads the page, and a one-time patch would be gone after it. **This widens the guard (M-8):** the grouping did not name the permissions. A copy through `execCommand` before the first `dom-ready` stays a named residual. Undo: `once` again, and drop the two handlers.

- B: once, plus a check after each reload. Leaves the window.
- C: the permissions only. Leaves `execCommand` after load unrecorded.
- D: do nothing. F3 stays open.

Refs: `edc100-expert-pass.txt` F3; `mcp-setup-prompt.test.ts:38-66`.

### D-1323: How does AC-10 wait for the page's call?

**I recommend A: poll the main process's call list, up to 10 s, until all three calls are there, then close.** Undo: drop the poll.

- B: a synchronous IPC from the page. Adds a channel and a page-side preload.
- C: a fixed sleep. Flaky.
- D: do nothing. Close can race the page's message.

Refs: `edc100-expert-pass.txt` F4; Session 98 RULE-1.

### D-1324: Does the guard cover `webContents.copy`, `cut` and the copy chords? (M-3, M-8)

**I recommend A: wrap `wc.copy` and `cut`, and record and block Ctrl+C, Ctrl+X, Ctrl+Insert and Shift+Delete in every guarded window.** **This widens the new rule (M-3) beyond the grouping's writers (M-8):** a later spec that presses a copy chord outside a gated file fails. Undo: drop the two hooks.

- B: the static scan alone. Misses a chord sent through a helper.
- C: wrap `wc.copy` only. Leaves the chords.
- D: do nothing. F5 stays open.

Refs: `edc100-expert-pass.txt` F5.

### D-1325: Does the guard remove the default Edit menu?

**I recommend A: no; the Edit menu clicked with the mouse stays a named residual.** Removing the menu would change the menu bar, the layout and the accelerators in every guarded run. The chord block already stops the menu's keys, and no spec clicks the menu bar. **Corrected by D-1331:** the menu's copy, cut, paste and paste-and-match-style items are not native writes on Windows; Electron 42.11.18 runs them as calls on the focused `webContents` object, so the guard's recorders most likely catch a mouse click too. No run proves it, and on macOS they stay native. Undo: none needed.

- B: `Menu.setApplicationMenu(null)` in the guard. Every dev-PC spec sees a different window.
- C: a copy-less menu. Still changes the menu.
- D: A without the residual written down.

Refs: `edc100-expert-pass.txt` F5; `ui/src/main` (no application menu).

### D-1326: How wide is the static scan?

**I recommend A: whole-file patterns, CSS and variable locators, the extra chords and `/copy/i`, with the launch helpers exempt from the launch kind only.** The counts stay 10, 8 and 0. Undo: restore the line patterns.

- B: keep it line-based. Misses multi-line chains.
- C: a TypeScript AST scan. A parser for a second wall.
- D: do nothing. F6 stays open.

Refs: `edc100-expert-pass.txt` F6; `edc-plan-writer-scan-head.txt`, `-split.txt`, `-after.txt`; `edc-plan-selftest-writer-scan.txt`.

### D-1327: Does the moved (e) check that the app kept the seeded token?

**I recommend A: one added line after (e)'s loop asserts that `mcp-token.txt` still equals the seed.** It is a new assertion, named in row 2 and §Test pins; no existing line changes. Undo: drop the line.

- B: a named residual. (e) could pass against a token the app made itself.
- C: read the token over the API. Adds a backend call.
- D: do nothing. F7 stays open.

Refs: `edc100-expert-pass.txt` F7; `index.ts:162-170`.

### D-1328: Does the moved `C1-5` keep its route and close on failure?

**I recommend A: copy `C1-5`'s `/settings/app` route and wrap the steps in `try`/`finally`.** Undo: drop the route lines and the `try`.

- B: no route. The Console starts in another state.
- C: no `finally`. A failed assertion leaves the app open.
- D: do nothing. F8 stays open.

Refs: `edc100-expert-pass.txt` F8; `console-chrome.test.ts:77-101`; `edc-plan-split-out-4.txt`.

### D-1329: How is it proved that no new file has a skip, only or todo literal?

**I recommend A: a row-6 Python check over the new files: none of the nine forms, but each E2E spec's one file-level `test.skip(` guard.** Undo: drop the check.

- B: the Vitest sweeps alone. They miss the E2E files.
- C: an ESLint rule. Changes the shared config.
- D: do nothing. F9 stays open.

Refs: `edc100-expert-pass.txt` F9; `queue-primitives.test.ts:829-844`; `queue-card.test.ts:773-777`.

### D-1330: How are Session 99's files kept out of the tested state and the receipts? (M-6)

**I recommend A: drop Session 99's folder, handoffs and reflection from `identity.py` before any read, and publish its tracked writes by name only.** Round 1 found that its untracked handoff was read into `tested_state`. Its tracked writes (`ui/src`, the docs, the registers) still count inside the one tracked-diff digest, because the suites read them. **The brief's "never bind Session 99's work" and a state that covers every suite input conflict (M-6).** If Session 99 writes after the gate, the gate's identity check fails and the gate runs again; this session never fails, reverts or stashes Session 99's work. Undo: drop `PEER_PREFIXES` and the `peer-dirty` marker.

- B: hash and record every dirty path. Publishes Session 99's content hashes in this session's receipts.
- C: wait for or freeze Session 99. Blocks a session this plan does not own.
- D: do nothing. The peer handoff stays in `tested_state`, which round 1 refused.

Refs: `edc-plan-review-round-1.md` EDC-R1-2; `edc-plan-selftest-identity.txt`; `edc-plan-identity-mutant.txt`; D-1316.

### D-1331: Do the guard and the scan cover the native paste path? (M-3, M-8)

**I recommend A: record and block `webContents.paste`, `pasteAndMatchStyle` and `copyImageAt`, `execCommand('paste')` and the paste chords (Ctrl+V, Ctrl+Shift+V, Shift+Insert), and make the scan refuse them.** `wc.replace` and `replaceMisspelling` stay unwrapped: they insert the text they are given and read no clipboard. **A later spec that pastes outside a gated file now fails (M-3), on a path the grouping did not name (M-8).** The scan counts stay 10, 8 and 0: only the gated capture file pastes. Proven on fakes and the scan's selftest; nothing pastes on the dev PC. It also corrects D-1325. Undo: drop the three recorders, the three chords and the scan kinds.

- B: A plus a tag-checked `wc.paste()` in AC-10. Changes `guard-logs.py`'s three-call contract for no new proof.
- C: `Menu.setApplicationMenu(null)`. Changes every guarded run (D-1325).
- D: do nothing. EDC-R1-1 stays open.

Refs: `edc-plan-review-round-1.md` EDC-R1-1; `edc-plan-electron-roles.txt`; `edc-plan-writer-scan-gated-files.txt`; `edc-plan-writer-scan-mutant.txt`; D-1324.

## Research References

- **Electron `clipboard`** (main and preload): the module's functions are own properties of one object shared by every import form. On 42.11.18 all twenty are writable and configurable (`D/probe/probe-result.jsonl`), so a preload can replace them before the main script runs.
- **`-r` preloads:** Node's `--require` runs a CommonJS module before the main script. `main-error-watch.cjs` is this repository's precedent. In a `.cjs` loaded this way here, `process.getBuiltinModule('electron')` is undefined and `module.require('electron')` returns the module.
- **`webContents` events:** `app.on('web-contents-created')` gives each `webContents`. `dom-ready` fires when the document is parsed. `console-message` delivers renderer console output to main, in an event-object form on current Electron and a positional form on older ones; the guard reads both.
- **`navigator.clipboard`:** the Async Clipboard API's `read`, `readText`, `write` and `writeText` live on `Clipboard.prototype`; `document.execCommand('copy'|'cut')` is the legacy path.
- **`before-input-event`:** emitted on a `webContents` before a key event reaches the page; `event.preventDefault()` stops the page's handling and the menu's accelerators for it.
- **`session.setPermissionRequestHandler` and `setPermissionCheckHandler`:** decide permission requests and checks for a session; `clipboard-read` and `clipboard-sanitized-write` are among the named permissions.
- **`webContents.copy()` and `cut()`:** run the page's native copy and cut, writing the clipboard without a JS clipboard call.
- **`webContents.paste()`, `pasteAndMatchStyle()` and `copyImageAt(x, y)`:** the first two run the page's native paste, reading the clipboard without a JS clipboard call; the third copies the image at a point to the clipboard. `replace(text)` and `replaceMisspelling(text)` insert the given text and read no clipboard (D-1331).
- **Electron 42.11.18 menu roles** (`edc-plan-electron-roles.txt`, the code embedded in `electron.exe`): `copy`, `cut`, `paste` and `pasteandmatchstyle` carry `webContentsMethod: e=>e.copy()` and the like with `registerAccelerator: false`, and `execute` calls that method on the focused `webContents` unless the platform is macOS and the role is native there (D-1331, correcting D-1325).
- **`readOrCreateMcpToken`** (`ui/src/main/index.ts:162-170`): reads `mcp-token.txt` from the app data folder, trimmed, when it exists; otherwise writes a new `randomUUID()`.

## Planning receipts

All under `C:/Temp/av-kit/e2e-devpc-clipboard/` (`D`), read-only against the repository. The mini-air was not contacted at plan time: Session 98's run proved the gated stage, and this session changes no host script. No plan-time probe called a clipboard writer or reader, ran a gated spec or set `AVKIT_E2E_CLIPBOARD_GATED`.

| Receipt | What it shows |
|---|---|
| `edc-plan-list-head.txt` | Playwright's `--list` at `HEAD`: 239 tests in 30 files |
| `edc-plan-writer-scan-head.txt`, `-split.txt`, `-after.txt`, `edc-plan-selftest-writer-scan.txt` | `writer-scan.py` with the widened patterns (D-1326): 10 hits at `HEAD`, 8 after the split (all in the copy file), 0 with both files gated, unchanged after the paste kinds of D-1331; its selftest, 56 of 56 |
| `edc-plan-writer-scan-gated-files.txt` | The scan over the two gated files themselves: the capture file's clipboard calls and its three `Control+V` presses (`:559`, `:576`, `:592`), the copy file's calls; both are gated and allowed (D-1331) |
| `edc-plan-writer-scan-mutant.txt` | A copy of `writer-scan.py` without the paste kinds: 12 of 56 selftest cases fail (D-1331, AC-5) |
| `edc-plan-electron-roles.txt` | Electron 42.11.18's menu-role table and `execute`, quoted read-only from `electron.exe` (D-1331, correcting D-1325) |
| `edc-plan-identity-mutant.txt` | A copy of `identity.py` without the two peer exclusions: 23 selftest failures, among them the peer files read and bound (D-1330, AC-20) |
| `edc-plan-split-out-2.txt`, `edc-plan-split-out-3.txt`, `edc-plan-split-out-4.txt`, `edc-plan-split-out-eslint.txt`, `edc-plan-selftest-split-specs.txt` | The four built files and their SHA-256 (`-4` is current, with D-1327 and D-1328); ESLint exit 0 on all four of `-4`; the split selftest, 13 cases |
| `edc-plan-shape-check.txt` | The rows 1 and 5 shape check on ten fixtures: a spec with three tag-checked calls passes, and so does one with a fourth, tag-checked `wc.pasteAndMatchStyle()`; the global marker, another function's tag, an unchecked call, a call outside `evaluate`, two calls under one check, an unchecked `wc.paste()`, an unchecked `wc.copyImageAt()` and two calls in all are refused (D-1320, D-1331) |
| `edc100-expert-pass.txt` | The fresh-context expert pass, F1 to F10, adopted as D-1320 to D-1329 |
| `edc-plan-anchor-probe.txt` | The S2 anchors by line and text at `HEAD` |
| `edc-plan-eol.txt`, `edc-plan-eol-selftest.txt` | Line endings by bytes for every scope file |
| `edc-plan-selftest-{eol-check,flake-run,gated-count,guard-check,guard-logs,identity,pins-check,red-check,snapshot,split-specs,writer-scan}.txt` and the other `edc-plan-*-selftest.txt` | Each plan-local checker's selftest |
| `edc-plan-ruff-check.txt`, `edc-plan-ruff-format.txt` | ruff on this folder |
| `edc-plan-task-lint.txt`, `edc-plan-host-details.txt`, `edc-plan-home-path.txt` | `lint_task_contract.py` on `task.md` (28 rows, OK); the host-detail scan of this folder and `check_home_path.py`, both with no hit |
| `edc-plan-decisions-1.txt` to `edc-plan-decisions-4.txt` | `decision_sources` probes; `-4` after plan review round 1 |
| `edc-plan-bundle-read.txt` | The Session 98 files this plan copied |
| `probe/probe-result.jsonl`, `probe/guard-probe.cjs`, `probe/main.mjs`, `probe/run-probe.ps1`, `probe/host-load.txt` | The Electron probe on a scratch app with a scratch user-data folder: marks only, no clipboard call; the load before it |
| `probe/lint-require.txt`, `probe/lint-module-require.txt` | ESLint refuses `require()` in a `.cjs` here and accepts `module.require` |

## Validation stage contract

| Stage | Checks | Where |
|---|---|---|
| Plan review | This plan and `task.md`, against both issues, grouping §3 Session 100 and §8, the s100 brief, the spec files, the launch helper, the product clipboard paths, the tool's gated stage and the planning receipts | `edc-plan-2026-11-20-e2e-devpc-clipboard` |
| Row checks | Each row's validation command | `task.md` |
| Session gate | §Session gate | H1-2 |
| Execution review | The delta from `baseline.sha` in the §Files Modified paths, the row-1, row-2, row-5, row-6, row-7 and row-8 receipts, against AC-1 to AC-22 | `edc-execution-2026-11-20-e2e-devpc-clipboard` |
