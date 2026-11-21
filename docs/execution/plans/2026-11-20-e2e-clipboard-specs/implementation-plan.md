---
project: "2026-11-20-e2e-clipboard-specs"
date: "2026-11-20"
source: "grouping .agent/context/grouping/2026-11-20-e2e-clipboard-specs-session-grouping.md §3 Session 98; issues E2E-CLIPBOARD-SPECS-UNGATED (D-1261) and E2E-CLIPBOARD-PRIMER-EMPTY (D-1262)"
meus: []
status: "draft"
template_version: "2.3"
grouping_source: ".agent/context/grouping/2026-11-20-e2e-clipboard-specs-session-grouping.md"
---

# Implementation Plan: split the system-clipboard specs into one file and run it on the second Windows host only when no remote session is connected

> **Project**: `2026-11-20-e2e-clipboard-specs`
> **Build Plan Section(s)**: none. Test files and E2E tooling only, no MEU (D-1261, grouping §3 Session 98 "(no MEU)").
> **Status**: said to execute (USER_EXPLICIT 2026-11-20 "continue orchestrating the next prompt session and the session after if there is any", with USER_EXPLICIT 2026-11-18 "make the decisions always the recommenations"). `plan_to_exec_gate: human`: those messages are the execution approval once the plan review approves and no STOP item is open; the plan review was approved at round 1 with no findings (.agent/context/handoffs/2026-11-20-e2e-clipboard-specs-plan-critical-review.md), and no STOP item is open. Session 98 is the only session of the 2026-11-20 grouping; Session 96 (`2026-11-18-e2e-remote-host`, `2c41c70`) built the remote-run tool and Session 97 (`2026-11-19-e2e-host-parity`, `82a0724`) emptied its known list.

---

## Goal

**Goal anchor:** the five capture E2E tests that only share a file with a clipboard test run again in every full run on both hosts, and the two tests that use the system clipboard run on the second Windows host (the mini-air) only when a probe before and after them reads no remote-desktop session; otherwise the run reports them skipped or voided with a named reason. The tests never run on the dev PC. Six parts:

1. **The split** (D-1268, `CLIPBOARD_SPLIT`). `AC-88.12 (a)(b)(f)` (Copy full path and Copy image) leaves `ui/tests/e2e/capture-filmstrip-actions.test.ts` and `AC-132.23` (Ctrl+V paste) leaves `ui/tests/e2e/capture-import.test.ts`; both move, with the helpers only they use, into the new `ui/tests/e2e/capture-system-clipboard.test.ts`. Their bodies keep every byte (only the line ending of the filmstrip lines moves from CRLF to LF). The five others, `AC-88.12 (c)`, `AC-88.12 (d)(e)`, `AC-89.9`, `AC-89.15` and `AC-132.22`, stay where they are, byte for byte. `split-specs.py` builds all three files from the `b59207b` bytes, with a file-level guard after the new file's imports that skips it unless `AVKIT_E2E_CLIPBOARD_GATED=1` (D-1282), and `--check` proves the result.
2. **The dev PC** (D-1276, `CLIPBOARD_NEVER_DEVPC`). The plan-local `flake-run.py` excludes only the new file, and refuses before any run while either old file still calls the clipboard. Its full run has 237 tests in 29 files, the five rejoined ones among them. The new file also guards itself in tracked code: it skips unless `AVKIT_E2E_CLIPBOARD_GATED=1`, which only the mini-air's gated stage sets, so a plain `npm run test:e2e` lists its two tests as skipped and never runs them (D-1282, `guard-check.py`).
3. **The probe** (D-1269 to D-1271, D-1273, `SESSION_PROBE`). One PowerShell block, the same bytes in `host-facts.ps1`, `host-status.ps1` and `run-e2e.ps1`, reads the RustDesk processes' command-line switches, `rdpclip.exe` and `qwinsta`, and returns `none`, `connected` or `undecided` with a named reason. `tools/e2e_remote.py check` prints it as a `session-probe:` line, and each run poll records it.
4. **The gated stage** (D-1271, D-1272, `GATED_STAGE`). `run-e2e.ps1` runs the main specs first, then probes. Only when the probe reads `none` does it run the gated file in `results\<run-id>\gated\`, and it probes again after. The tool reports a `gated` object with one of five outcomes. A gated failure exits 40, apart from the main stage's `new` list. A session that connects during the stage (seen by the after-probe or a poll) voids the result.
5. **The known list and its pin** (D-1272, D-1275). `tools/e2e_host/known-failures.json` drops its two `skip` entries and gains one `gated` entry for the new file. `tests/tooling/test_e2e_remote.py::test_ac_11_known_tracked_list` changes in row 3, which names it. `pins-check.py` proves that no other existing statement of that file changes.
6. **The acceptance run and the registers** (D-1277 to D-1280). One mini-air run (and a second, row 8b, only when the gating probe cannot read the host; D-1280) through `tools/e2e_remote.py run` at the final tree, as a snapshot commit on no ref (`SNAPSHOT_NO_REF`). The main stage has 237 tests, all expected. The gated outcome is a receipt, not a pass condition. Then `E2E-CLIPBOARD-SPECS-UNGATED` is resolved when row 8's `probe-check.py --judge-gate` says resolve (D-1280), `E2E-CLIPBOARD-PRIMER-EMPTY` gets that run's verification and stays open, a new low issue records the two dev-PC specs that also write the clipboard, and grouping row 98 is set.

**The split flag** (grouping `:84`, D-1274) is decided by evidence at row 7a. The flag reads `fallback` when the probe cannot read the host (the elevated `check` returns `undecided-probe-failed` or `undecided-unreadable`) or when a fake-host test of rows 3 to 5 cannot go green without a test change. In that case the split ships alone: the tool, the host scripts and the run book keep their row-0 bytes, the `test_s98_` tests are dropped, the new file stays skipped on the mini-air with its current reason, and `E2E-CLIPBOARD-SPECS-UNGATED` stays open with its verification updated. Otherwise the flag reads `probe` and the plan runs as written. The flag is provisional (D-1280): the elevated `check` reads from session 0, while the probe that gates the stage runs in the scheduled task at run level Limited in the desktop session (`.agent/docs/e2e-remote-host.md:53`) and may read less. Row 8's `probe-check.py --judge-gate` reads the gating probes. When either returns `undecided-probe-failed` or `undecided-unreadable` it exits 3, and row 8b flips the flag to `fallback` (trigger `limited-unreadable`), reverts as row 7a's fallback does, and reruns the mini-air run once in that form.

**Why.** `E2E-CLIPBOARD-SPECS-UNGATED` (`known-issues.yaml:6037`, medium, TECH-DEBT P3, D-1261): every full run on both hosts excludes the two files by name. Two of their seven tests touch the clipboard, so the other five have run in no gate since Session 91, and the two clipboard tests have no host at all. `E2E-CLIPBOARD-PRIMER-EMPTY` (`:3628`, low, MONITORING P4, D-1262) is a watch item: AC-88.12's primer read an empty clipboard once, and the issue can neither recur nor close while AC-88.12 never runs. The dev PC is Mat's working desktop, and Session 57 RULE-4 keeps every clipboard test off it. The mini-air is a second desktop, but RustDesk syncs its clipboard with whoever is connected, so a clipboard test there may run only when nobody is connected.

**Grouping §3 Session 98** (`:64-84`):
- The new file is named in the plan. The mini-air list and the dev-PC exclusion name only it.
- `test_ac_11_known_tracked_list` changes in a row that names it.
- The tool and its host scripts probe before and after the clipboard file, and the run book changes.
- The acceptance direction:
  - the five pass in a dev-PC full run;
  - fake-host tests prove each probe outcome, and a session that connects during the stage voids it;
  - one real mini-air run, in which the clipboard file passes or is reported skipped with the probe's reason.
- If AC-88.12 runs and its primer fails, PRIMER-EMPTY's own rule applies.
- The gate: no product code; no assertion change beyond the named pin; RustDesk read only by the probe, never changed or stopped; the clipboard tests never on the dev PC; the home path checked before and after; no host detail in a tracked file.

`:131` says Session 98 carries D-1265, D-1266 and D-1267, and reads D-1261 and D-1262 from the register.

**What the code shows (plan-time reads at `HEAD` `b59207b`):**

- **The two spec files.**
  - `capture-filmstrip-actions.test.ts` is CRLF, 17,530 bytes, 388 lines. It holds five tests: `AC-88.12 (a)(b)(f)` (`:242-268`), `(c)` (`:269-285`), `(d)(e)` (`:286-309`), `AC-89.9` (`:314-352`) and `AC-89.15` (`:353-389`). Only (a)(b)(f) uses `ClipboardProbe`, `readClipboardImage`, `readSettledClipboardImage`, `passesShotPixels` and `primeTransparentClipboard` (`:164-217`, `plan-deps.txt`).
  - `capture-import.test.ts` is LF, 15,284 bytes, 425 lines. It holds `AC-132.22` (`:238-282`) and `AC-132.23` (`:337-426`). Only AC-132.23 uses `PASTED_NAME`, `pngs`, `registerBody`, `SavedClipboard`, `readClipboard`, `restoreClipboard` and `describeFormats`.
  - The shared helpers (`CaptureItem`, `launchApp`, `installSeam`, `openCapture`, `startBackend`, `launch` and the rest) are used by both kinds, so the new file carries its own copy and the old files keep theirs.
  - `CLIPBOARD_CALL` (`\bclipboard\.(read|write|clear|available)[A-Za-z]*\(`) matches only inside the two moving tests and their helpers.
  - `split-specs.py --out` builds three files: the new file at 23,156 bytes (LF, with the D-1282 guard), the filmstrip file at 13,709 (CRLF) and the import file at 9,166 (LF). Their SHA-256 prefixes are `f848f6b4`, `02699784` and `e6a28e77` (`plan-split-out-3.txt`; before the guard the new file was 22,828 bytes, `7d751cc6`, `plan-split-out-2.txt`). `tsc` and ESLint pass on them (`plan-eslint-3.txt`), and a planted change fails (`plan-eslint-neg-3.txt`). At `HEAD`, `guard-check.py --list` lists 239 tests in 29 files, none skipped, and exits 1 (`plan-guard-list-head.txt`). Its judge passes a scratch list of the built files with the variable unset (two skipped, `plan-guard-judge-unset.txt`) and fails it with the variable set (`plan-guard-judge-set.txt`).
- **The dev-PC runner.** Session 91's `flake-run.py`, copied into this folder, excludes by file name: `EXCLUDED` (`:161`) is now only `capture-system-clipboard.test.ts`. `OLD_CLIPBOARD` (`:164`) refuses with exit 2 before any run while either old file matches `CLIPBOARD_CALL`; at `HEAD` it does (`plan-flake-guard-head.txt`). `--list-check` counts 239 tests in 29 files at `HEAD`, and 237 after the split, because the new file's 2 tests are excluded.
- **The known list.** `tools/e2e_host/known-failures.json` is LF, 261 bytes: `known: []` and two `skip` entries (label `mini-air`, the two old files, reason "clipboard spec; grouping §3 Gate").
- **The tool** (`tools/e2e_remote.py`, LF, 49,889 bytes, 1,396 lines):
  - `REASONS` (`:51`) maps 33 reasons to exits: 31 is `report-missing`, 32 `known-failures-stale`, 40 `new-failures`.
  - `load_known` (`:391`) requires a `known` and a `skip` list. `label_skip` (`:406`).
  - `fact_lines` (`:574`) prints `check`'s fact lines. `host_call` (`:635`).
  - `_poll` (`:941`) writes one record per poll into `polls.jsonl`.
  - `_collect_and_summarize` (`:1045`) sets the expected specs to the commit's specs minus the label's `skip`.
  - `_run` (`:1115`) refuses a `skip` entry with no reason or a file absent from the commit (32).
  - The request (`:1158`) carries `skip` to the host. `_check` (`:1268`).
- **The launcher.** `tools/e2e_host/run-e2e.ps1` is LF and ASCII, 6,784 bytes, 120 lines. It lists the specs minus `request.skip` and starts Playwright with the only `Start-Process` (`:114`). It writes `pid.txt` (`:116`), then `WaitForExit` (`:117`), and `AvDone` writes `DONE` through `DONE.tmp` (`:120`).
  - `test_ac_14_host_static_launcher` (`test_e2e_remote.py:1803`) pins exactly one `Start-Process` line, with `-PassThru` and no `-Wait`, then `.Handle`, then `pid.txt` before `WaitForExit`.
  - `test_ac_14_host_static_bytes` (`:1767`) requires ASCII and LF, with no backtick and no word from `HOST_BANNED` (`:107`; `Stop-Process`, `kill`, `Set-ItemProperty`, `schtasks` and the rest). Each `ConvertTo-Json` line must carry `-InputObject`, `-Depth 8` and `-Compress`.
  - `test_ac_14_host_static_busy_block` (`:1795`) holds the `# begin busy-check` block identical in `BUSY_COPIES` (`:46`). That is the precedent for one block copied into several scripts.
  - `test_ac_15_host_fixture_facts_schema` (`:1960`) checks the facts keys with `in`, so a new key does not break it.
- **The host status.** `host-status.ps1` (LF, 11,492 bytes, 268 lines) reports `pid_file` from `results\<run-id>\pid.txt`. The tool's run tree (`:530`) uses it for the run's own processes.
- **The pin.** `test_ac_11_known_tracked_list` (`test_e2e_remote.py:1561-1572`) asserts `known == []`, then the two `skip` tuples (`:1567-1568`), then every reason present, then `Path(m.KNOWN_FILE) == KNOWN`. The test file is LF, 84,900 bytes, 2,305 lines.
- **The run book** (`.agent/docs/e2e-remote-host.md`, LF, 16,280 bytes, 259 lines):
  - "## What the tool writes on the host" (`:173`) and "## The known-failure list" (`:189`).
  - `:204` says Session 97 owns the list's last entries.
  - `test_ac_19_run_book_names_everything` (`:2249`) requires every reason with its code, every prerequisite id, every config key, `e2e_remote.py <sub>`, `known-failures.json` and "Session 97".
- **The RustDesk signal.** RustDesk's source, read at plan time into `D/rustdesk-src/`:
  - Each incoming connection starts the connection manager as a separate process with `--cm`. `start_ipc` (`src/server/connection.rs:4709`) builds `--cm` (`:4729`) and spawns it through `run_as_user` (`:4763`); `--cm-no-ui` (`:4754`) is the Linux headless form.
  - `src/core_main.rs` names `--cm` "call connection manager to establish connections" (`:629`), `--tray` (`:347`), `--service` (`:360`) and `--server` (`:364`).
  - The connection manager is the process that holds the clipboard sync for the session, so its presence is the signal. `qwinsta`'s `rdp-tcp#<n>` Active row and `rdpclip.exe` are the RDP equivalents.
- **The mini-air now.** `plan-session-probe-miniair-1.txt`, 2026-11-20T18:09:36Z, read-only through `-EncodedCommand`; it read only process and session state:
  - elevated, in session 0 over SSH, 170 processes, RustDesk 1.4.5+63;
  - `--service` in session 0 as SYSTEM;
  - `--server` in the console session as SYSTEM, a child of the service;
  - `--tray` as the desktop user;
  - every command line readable; no `--cm`; the console Active; no RDP listener.
  - The planned classifier reads `none`, `no-remote-session`. **Mat was not connected at plan time**, so the connected case rests on the fake-host tests and the documented signal above (s98 brief).
- **The dev PC now** (`plan-session-probe-devpc.txt`; not elevated, session 1, 549 processes):
  - the service and its child have unreadable command lines (session 0, and its direct child by `ParentProcessId`);
  - `--tray` is readable;
  - one readable RustDesk process has no switch at all (the open main window);
  - `rdp-tcp` is listening, but no session is Active.
  - The planned classifier reads `undecided`, `undecided-rustdesk-other` here. The dev PC is recorded, never judged (`probe-check.py --local`).
- **The other dev-PC clipboard writers.** `ui/tests/e2e/console-chrome.test.ts` `C1-5` (`:77`) and `mcp-setup-prompt.test.ts` `AC-71.15` (`:91`) read and write the main-process clipboard and run in every dev-PC full run. Session 57 RULE-4 covers them too, but no issue records them (D-1277).
- **The register.** Both issues are `open` with `meu_links: []` (`plan-issues.txt`). Grouping row 98 (`:108`) is `pending`. D-1268 to D-1287 were free at plan time; D-1268 to D-1283 are now this plan's, D-1284 is free, and D-1285 to D-1287 are kept for execution.

## Context Tool Decision

```yaml
context_tool_decision:
  phase: planning_and_execution
  eligible_tools: []
  decision: not_applicable
  eligibility_basis: "graphify-out/ and graphify-out-research/ are absent from P:/av-kit (ls, 2026-11-20). The change is two spec files split into three, one Python tool, three host scripts, one JSON list, one test file and one run book, with every input read verbatim at plan time (the spec files, the tool, the host scripts, the tests, RustDesk's source, both hosts' process state); that is a bypass class."
  human_message_reference: null
```

## Harness, driver and reviewer route

- **Driver:** Claude Code in VS Code (`.agent/docs/harness-profiles.md`).
  - Commands run in `pwsh` from `P:/av-kit` through `rtk proxy` with the receipt pattern (`.agent/docs/commands.md`).
  - Session receipts go under `C:/Temp/av-kit/e2e-clipboard-specs/` (`D`), and the remote tool's receipts under `C:/Temp/av-kit/e2e-remote/<run-id>/`.
  - Vitest, `tsc`, ESLint and Playwright run through `pwsh` with `ELECTRON_RUN_AS_NODE` removed, Vitest from `Set-Location 'P:\av-kit\ui'`.
- **The host:** reached only through `tools/e2e_remote.py` (`check`, `run`, `summarize`, and `release` with this session's own run id per the run book).
  - The tool builds every `ssh` and `scp` argv with `-o BatchMode=yes -o StrictHostKeyChecking=yes` and the alias from the untracked local config.
  - No row runs `ssh` itself, adds or changes a known-hosts entry, reads or changes RustDesk's settings, or touches the scheduled task beyond the tool's one `Start-ScheduledTask` per run.
- **Reviewer:** Codex through `tools/Invoke-CodexDispatch.ps1`, with `AGENT_MODEL_REGISTRY_HOME=P:/.agent` and `RECEIPTS_DIR` set (Session 82 RULE-3).
  - Plan loop `ecs-plan-2026-11-20-e2e-clipboard-specs`; execution loop `ecs-execution-2026-11-20-e2e-clipboard-specs`.
  - Caps come from `.agent/review-limits.json`: 6 rounds, turn tokens off.
- **Never** commit, stage or push without Mat's words.
  - The snapshot commit of row 8 is an object on no ref (`SNAPSHOT_NO_REF`): it moves no branch and stages nothing.
  - The coordinator commits after the execution review, without a push.

## Handoff Set

| Scope | Canonical handoff |
|---|---|
| Both issues (no MEU) | `.agent/context/handoffs/2026-11-20-e2e-clipboard-specs-handoff.md` |

Rolling reviews:

- `.agent/context/handoffs/2026-11-20-e2e-clipboard-specs-plan-critical-review.md`
- `.agent/context/handoffs/2026-11-20-e2e-clipboard-specs-implementation-critical-review.md`

The handoff has no MEU in its name, following `2026-11-18-e2e-remote-host-handoff.md` (Session 96, also no MEU).

## Work Packages and Context Lifecycle

| ID | Work | depends_on | context_strategy | durable_outputs |
|---|---|---|---|---|
| WP-1 | Baseline, copied checkers, selftests, the row-0 refusals, the OS-wide probe (row 0) | — | shared | `baseline.*`, `D/baseline-copies/`, `D/ecs-baseline-0.txt` |
| WP-2 | The split: Red and Green (rows 1 and 2) | WP-1 | shared | The new spec file, the two edited spec files |
| WP-3 | The probe and the gated stage: Red, tool Green, host Green (rows 3 to 5) | WP-1 | shared | `test_e2e_remote.py`, `tools/e2e_remote.py`, the three host scripts |
| WP-4 | The run book, the known list and the commands doc (row 6) | WP-3 | shared | `e2e-remote-host.md`, `known-failures.json`, `commands.md` |
| WP-5 | The split flag, then the dev-PC full run (rows 7a and 7b) | WP-2, WP-4 | shared | `D/ecs-split-flag.txt`, the flake-run receipts |
| WP-6 | The snapshot and the mini-air run (row 8, and row 8b after a flip) | WP-5 | shared | `D/ecs-snapshot-8.json` (or `-8b`), `D/ecs-judge-gate-8.txt`, `C:/Temp/av-kit/e2e-remote/<run-id>/` |
| WP-7 | Registers (row 9) | WP-6 | shared | Both issues updated, the new issue, grouping row 98 |
| WP-8 | Closeout (H1, H2) | WP-7 | `compact_continue` | The handoff, the review, the reflection |

## User Review Required

> [!NOTE]
> **Sixteen briefs are settled on their recommendations under your hand-over** ('continue orchestrating the next prompt session and the session after if there is any', 2026-11-20, continuing 'make the decisions always the recommenations', 2026-11-18). The five with an M item:
>
> - **D-1273 (M-6):** the plan read the mini-air with one read-only command sent as `-EncodedCommand` over the pinned alias, not by copying a probe script into a folder there as the brief described. Nothing was written on the host.
> - **D-1274 (M-6):** the split flag is decided at row 7a, not at planning. The split ships alone if the elevated probe cannot read the mini-air's RustDesk processes or a fake-host test cannot go green. Row 8 can still flip it once if the probe that gates the run cannot read them (D-1280).
> - **D-1277 (M-8):** `C1-5` (console copy) and `AC-71.15` (Copy prompt) also write your clipboard in every dev-PC full run. A new low issue records them, and nothing else changes. Doing nothing stays an option.
> - **D-1279 (M-6):** the mini-air runs a snapshot commit on no branch; your branch, index and status stay untouched. The clipboard outcome (ran, skipped or voided) is a receipt, not a pass rule.
> - **D-1282 (M-8):** the clipboard file skips itself unless the mini-air's gated stage sets `AVKIT_E2E_CLIPBOARD_GATED=1`, so a plain `npm run test:e2e` on your PC lists its two tests as skipped and never runs them. `.agent/docs/commands.md` gains two lines saying so; that file is beyond the grouping's list.
>
> The other eleven have no M item: the split by file (D-1268), the probe-gated second stage (D-1269), `--cm` or an RDP session as connected, with anything unreadable skipping (D-1270), one probe block in three host scripts (D-1271), a `gated` list and summary object with no exit-code change (D-1272, M-4 checked), the named `test_ac_11` pin (D-1275, M-7 checked), the dev-PC guard and 237 tests (D-1276), the issue outcomes (D-1278), the gating probe judged at row 8 with `E2E-CLIPBOARD-SPECS-UNGATED` resolved only on a named outcome (D-1280), the `--cm` start time in the summary with the stale-`--cm` risk named (D-1281, M-10 checked), and the honest void wording with the expert pass's low items (D-1283, M-4 checked).
>
> **What touches your machines.**
> - The dev PC:
>   - Row 7b and the gate run the dev-PC full E2E (Electron windows open and close for about 20 minutes each).
>   - The clipboard file never runs there, and neither old file can run while it still uses the clipboard.
>   - `probe-check.py --local` runs the read-only probe block on the dev PC at rows 5 and the gate; it lists processes and sessions and writes one JSON receipt under `D`.
> - The mini-air:
>   - Rows 7a and 8 (and 8b, only after a flip) run `tools/e2e_remote.py check`. As every check does, it copies the session's host scripts into the tool's `bin\` folder on the mini-air, under the configured root.
>   - Row 8 copies a source archive there and starts its existing task once (row 8b, only after a flip, once more), so Electron windows open on that desktop for about 25 minutes.
>   - **If you are connected to the mini-air through RustDesk during row 8, the clipboard tests do not run, and the run says so.** If you connect while they run, their result is voided. Voiding discards the result; it cannot undo what the tests already wrote to that clipboard, and AC-88.12 leaves an image there (D-1283).
> - Nothing reads or changes RustDesk's settings or service, and nothing is stopped or installed.
> - Nothing costs money.
> - Smart App Control, auto sign-in, a self-hosted runner and RustDesk's own settings stay yours and are not planned (D-1216).
>
> No STOP item is held for you.

## Proposed Changes

### Single-statement contracts

| Id | Statement |
|---|---|
| `CLIPBOARD_SPLIT` | `capture-system-clipboard.test.ts` holds exactly `AC-88.12 (a)(b)(f)` and `AC-132.23`, each test and each block it needs equal to its `b59207b` bytes after CRLF to LF. The two old files equal their `b59207b` bytes minus the named blocks plus one named comment line each, with their own line endings. Of the three, only the new file matches `CLIPBOARD_CALL`. Its header, imports and the file-level guard (D-1282) are its only other lines. |
| `CLIPBOARD_NEVER_DEVPC` | No dev-PC run in this session runs `capture-system-clipboard.test.ts`. `flake-run.py` excludes it by name, and refuses with exit 2 before any run while either old file matches `CLIPBOARD_CALL`. In tracked code the new file skips itself unless `AVKIT_E2E_CLIPBOARD_GATED=1`, which only the gated stage sets, and `guard-check.py --list` proves it from Playwright's list (D-1282). |
| `SESSION_PROBE` | One block between `# begin session-probe` and `# end session-probe`, byte-identical in `host-facts.ps1`, `host-status.ps1` and `run-e2e.ps1`. It reads only process, session and file-version state, and returns `{state, reason, rustdesk_version, procs, utc}`. The state is in `none`, `connected` or `undecided`, the reason is in that state's closed list, and no account name, address or folder is returned. |
| `GATED_STAGE` | `run-e2e.ps1` runs the gated files only after the main stage, only when the probe before them reads `none`, and in `results\<run-id>\gated\`. It probes again after them. The tool's `gated` object holds one outcome of `GATED_OUTCOMES`; `run` is reported only when the before probe, the after probe and every poll taken during the stage read `none`. |
| `PINNED_SSH`, `NAMED_REFUSAL`, `NEVER_STOP`, `ONE_LOCK`, `CHECK_AND_NAME`, `COMMIT_BOUND`, `REPORT_ONLY`, `KNOWN_NAMED`, `NO_PARTIAL` | Session 96's contracts (`2026-11-18-e2e-remote-host/implementation-plan.md` §Single-statement contracts), unchanged. The probe adds no `ssh` call, no process stop and no second lock. A probe failure is a named `undecided` reason, never a silent `none`. |
| `LOCAL_HOST_DETAILS` | The host alias, account, host folder and task path appear only in the untracked local config and in receipts under `C:/Temp/av-kit/`, never in a tracked file, the handoff or a commit message. |
| `KNOWN_EMPTY` | `known-failures.json` keeps `known: []` and `label` `mini-air` through the session. Row 6 changes only its `skip` and `gated` lists, as §The known list names. |
| `SNAPSHOT_NO_REF` | The mini-air run's commit is `HEAD` plus the named working files, written with a temporary `GIT_INDEX_FILE` and `git commit-tree`, every git call under `GIT_OPTIONAL_LOCKS=0`. Every ref, the index, `HEAD` and `git status` are byte-for-byte the same after it, and its author is the noreply identity (Session 97's contract, unchanged). |

### The split: `ui/tests/e2e/capture-system-clipboard.test.ts` (new, LF), `capture-filmstrip-actions.test.ts` (CRLF stays CRLF), `capture-import.test.ts` (LF stays LF)

`split-specs.py` builds all three files from the `b59207b` blobs (`git show`), never from the working tree. A block is one top-level declaration or `test(` call, with the comment lines right above it, up to the line before the next block.

- **The new file** (LF, 23,156 bytes at plan time):
  - the six-line `NEW_HEADER` comment (Session 98, D-1268, D-1269: the two tests, where they came from, why the file never runs on the dev PC, and that `known-failures.json` names how it runs on the mini-air);
  - the import lines both sources need;
  - the `GUARD` lines after the imports (D-1282): a comment naming D-1282 and a file-level `test.skip(process.env.AVKIT_E2E_CLIPBOARD_GATED !== '1', '<GUARD_REASON>')`, whose reason is "system clipboard spec: runs only in the gated stage on the second Windows host";
  - the filmstrip blocks: `CaptureItem`, `ImageFixture`, `SeamState`, `SHOT_W`, `SHOT_H`, `sampleShot`, `launchApp`, `buildFixtures`, `installSeam`, `ClipboardProbe`, `readClipboardImage`, `readSettledClipboardImage`, `passesShotPixels`, `primeTransparentClipboard`, `SHOT_A`, `SHOT_B`, `SHOT_C`, `openCapture` and the test `AC-88.12 (a)(b)(f)`;
  - the import blocks: `NOT_AN_IMAGE`, `PASTED_NAME`, `CaptureRow`, `Backend`, `startBackend`, `Harness`, `launch`, `pngs`, `slashes`, `registerBodies`, `registerBody`, `toastMessage`, `SavedClipboard`, `readClipboard`, `restoreClipboard`, `describeFormats` and the test `AC-132.23`.

  Every block equals its source block after CRLF to LF, so no assertion, timeout or wait changes. The names the two sources share do not collide: the filmstrip's `launchApp` and the import file's `launch` are different names. `tsc` and ESLint pass on the built file (`plan-eslint-3.txt`).
- **The filmstrip file** (CRLF, 17,530 to 13,709 bytes): the base minus `ClipboardProbe`, `readClipboardImage`, `readSettledClipboardImage`, `passesShotPixels`, `primeTransparentClipboard` and the test `AC-88.12 (a)(b)(f)`. One comment line is added right after the line `// Copy image oracle (SHOT_PIXELS) reads real decoded pixels back from the main-process clipboard.`:

  ```
  // Session 98 (D-1268): AC-88.12 (a)(b)(f) and its clipboard oracle moved to capture-system-clipboard.test.ts.
  ```

  It keeps `AC-88.12 (c)`, `AC-88.12 (d)(e)`, `AC-89.9` and `AC-89.15`.
- **The import file** (LF, 15,284 to 9,166 bytes): the base minus `PASTED_NAME`, `pngs`, `registerBody`, `SavedClipboard`, `readClipboard`, `restoreClipboard`, `describeFormats` and the test `AC-132.23`, and minus the import names only they used. One line is added inside the header comment, right after ` * and fails on any difference (S13). The formats before and after are printed for the receipt.`:

  ```
   * Session 98 (D-1268): AC-132.23 and its clipboard helpers moved to capture-system-clipboard.test.ts.
  ```

  It keeps `AC-132.22`. (`S13` in that quoted comment is the spec's own label, not this plan's stop condition.)

**How the files are written.** `--write` refuses unless both old files still equal their base blobs and the new file is absent. It writes all three to temporary files first, then renames them (`NO_PARTIAL`). `--check` rebuilds the three files and compares bytes and invariants:
- every moved block equals its base block;
- the old files equal the base minus the named removals, plus the named lines;
- each moved title is in the new file once, and each kept title in its old file once;
- only the new file matches `CLIPBOARD_CALL`;
- each file has its one line-ending kind.

`--selftest` proves that a changed assertion, a changed block, a CRLF new file, a clipboard call left in an old file and a new file without its guard are each refused (6 cases, `plan-split-selftest-3.txt`). At `HEAD` `--check` exits 1 with three problems (`plan-split-check-red-3.txt`).

### The session probe: one block in `tools/e2e_host/host-facts.ps1`, `host-status.ps1` and `run-e2e.ps1` (LF, ASCII)

The block is the same bytes in all three scripts, from `# begin session-probe` to `# end session-probe`, each marker a whole line. It follows the `# begin busy-check` precedent (`BUSY_COPIES`, `test_e2e_remote.py:46`). It defines three functions.

**`AvProbeFacts`** does the live reads, each inside `try`; any read error sets `error`:
- `Get-CimInstance Win32_Process` for `rustdesk.exe` and `rdpclip.exe`: name, pid, parent pid, session id, whether the command line is readable, and the command line reduced to its `--` switches (every other word becomes `<arg>`, so no path or id is kept);
- the session id of the RustDesk service's own process;
- the `FileVersion` of the first readable `rustdesk.exe` image;
- `qwinsta.exe`'s rows reduced to the session name (`console`, `services`, `rdp-tcp#<n>`, `rdp-tcp`, otherwise `<other>`), the id and the state.

**`AvProbeClassify`** is a pure function of those facts. It takes the first rule that matches:

| Order | Facts | State | Reason |
|---|---|---|---|
| 1 | A read failed | `undecided` | `undecided-probe-failed` |
| 2 | A RustDesk process whose switches contain `--cm` or `--cm-no-ui` | `connected` | `connected-rustdesk-cm` |
| 3 | An `rdpclip.exe` process, or a `qwinsta` row `rdp-tcp#<n>` in state `Active` | `connected` | `connected-rdp` |
| 4 | A RustDesk process whose command line is unreadable and that is neither the session-0 service process nor its direct child (by `ParentProcessId`) | `undecided` | `undecided-unreadable` |
| 5 | A readable RustDesk process whose switches are not exactly one of `--service`, `--server` or `--tray` (no switch at all counts) | `undecided` | `undecided-rustdesk-other` |
| 6 | Otherwise | `none` | `no-remote-session` |

**`AvSessionProbe`** returns `[ordered]@{ state; reason; rustdesk_version; procs; utc }`. `procs` holds `{name, session, switches, readable, started}` only (`started` is the process's `CreationDate` as UTC, D-1281); owners, pids and command lines are not returned.

**Why these signals** (D-1270). RustDesk starts its connection manager as its own process with `--cm` for every incoming connection, through `run_as_user` (`src/server/connection.rs:4709`, `:4729`, `:4763`). On Linux the headless form is `--cm-no-ui` (`:4754`). `src/core_main.rs:629` names it "call connection manager to establish connections". The service, server and tray processes (`--service`, `--server`, `--tray`, `:360`, `:364`, `:347`) run whether or not anyone is connected. Mat's plan-time view of the mini-air shows exactly those three, with nothing connected.

The two `undecided` reasons that rest on the unknown make the probe fail safe: a RustDesk window open on the host without a connection reads `undecided-rustdesk-other` and skips the stage. The exemption in rule 4 covers the processes a desktop-level reader cannot see into. On the dev PC (`plan-session-probe-devpc.txt`), not elevated, those are the session-0 service and its child; `--tray` stays readable there, and so does a `--cm` started as the desktop user.

**Known risk.** The probe reads moments, not a stream. A connection that opens and closes between two readings is missed: the gated stage's readings are its before probe, every poll (at the config's `poll_s`, 5 to 300 seconds) and its after probe, so the gap is up to `poll_s` plus about six seconds per poll. The run book names this, and these:
- **The reader.** `check` reads elevated from session 0; the gating probe reads with the task's Limited token in the desktop session. The two can differ, so row 8's `--judge-gate` decides (H1, D-1280).
- **A stale `--cm`.** RustDesk keeps a closed connection's tab in its `--cm` window until someone closes it, so `connected-rustdesk-cm` can stick and skip every later gated stage. `gated.detail` names each proc's start time, so a stale one is visible; no row asks Mat to connect or disconnect to measure it (M1, D-1281).
- **The clipboard during a void.** A connection that opens during the stage is seen only at the next poll or the after probe. By then the tests may already have written that desktop's clipboard, which RustDesk can sync to the remote side, and AC-88.12 leaves an image there after the stage. The void discards the result; it cannot undo that write (M3, D-1283).
- **The scope.** The probe sees RustDesk and RDP only: AnyDesk, TeamViewer, Chrome Remote Desktop and VNC read `none`. An `rdpclip.exe` left in a disconnected RDP session reads `connected-rdp` until logoff, and `qwinsta`'s state words are read in English (L1, D-1283).

### The gated stage: `tools/e2e_host/run-e2e.ps1` (LF stays LF)

At `HEAD` the launcher lists every `*.test.ts` and `*.spec.ts` not in `request.skip` into `specs.txt` (`:109`), and starts Playwright with its only `Start-Process` (`:114`). Then it writes `pid.txt` (`:116`), waits (`:117`), and `AvDone` writes `DONE` through `DONE.tmp` (`:120`).

After the change:

- **The probe block.** It sits after the launcher's helper functions.
- **`AvStage([string]$Dir, [string[]]$Specs)`** holds the one `Start-Process` line, unchanged in its switches (`-PassThru`, no `-Wait`). It then has `$null = $p.Handle`, writes `pid.txt` in `$Dir`, waits, and returns the exit code. With `-Gated` (the gated stage only) it sets `$env:AVKIT_E2E_CLIPBOARD_GATED='1'` before `Start-Process` and `$null` after; the main stage never sets it (D-1282). Every internal call is piped to `$null` or assigned, so the function returns one int (L3, D-1283). `report.json`, `run.log` and `run.err` go to `$Dir`, and `AVKIT_E2E_DIAG_DIR` stays `results\<run-id>\diag`.
- **The main stage** lists the specs minus `request.skip` and minus `request.gated` into `specs.txt`, writes `main` to `stage.txt`, and calls `AvStage` on `results\<run-id>\`.
- **The gated stage**, when `request.gated` names at least one file:
  1. `AvSessionProbe` writes `probe-before.json`.
  2. If its state is `none`: write `gated` to `stage.txt`; `AvStage` runs `results\<run-id>\gated\`, with its own `specs.txt`, `report.json`, `run.log`, `run.err` and `pid.txt`; then `AvSessionProbe` writes `probe-after.json`.
  3. If its state is anything else, nothing more runs.

  `meta.txt` gains `gated_exit=` (empty when the stage did not run), `probe_before=<state>/<reason>` and `probe_after=<state>/<reason>`.
- **`DONE`** carries the main stage's exit. The gated result is judged by the tool from the files, never from the exit code. A probe call that throws is caught and written as `undecided-probe-failed`, so the launcher always reaches `AvDone`.

The static tests keep holding:
- exactly one `Start-Process` line, with `-PassThru` and no `-Wait`;
- `.Handle` after it;
- `pid.txt` before `WaitForExit`;
- `DONE.tmp` and its rename;
- `ELECTRON_RUN_AS_NODE` and `AVKIT_E2E_DIAG_DIR`;
- ASCII, LF, no backtick, no `HOST_BANNED` word;
- every `ConvertTo-Json` line with `-InputObject`, `-Depth 8` and `-Compress`.

The stale-build case writes no `pid.txt` (`launcher_99`), because the probe runs only after the main stage.

### The host status: `tools/e2e_host/host-status.ps1` (LF stays LF)

`host-status.ps1` gains the probe block and two keys:
- `session_probe`: the `AvSessionProbe` object, taken at every status call;
- `stage`: the text of `results\<run-id>\stage.txt`, or `null`.

When the stage is `gated`, `pid_file` reads `results\<run-id>\gated\pid.txt`, so the tool's run tree (`tools/e2e_remote.py:530`) follows the stage that is running. Otherwise it reads `results\<run-id>\pid.txt`, as now. `host-facts.ps1` gains the block and one key, `session_probe`, and still writes nothing.

### The tool: `tools/e2e_remote.py` (LF stays LF)

`REASONS` (`:51`) and every exit code are unchanged (D-1272, M-4 none). The changes:

- **`load_known`** (`:391`): an optional `gated` list of `{label, file, reason}` objects. A missing key is `[]`. A non-list, an entry missing a field, or an entry that is not an object is refused as now (`known-failures-stale`, 32). A new sibling of `label_skip` (`:406`), `label_gated`, returns the label's gated files.
- **`_run`** (`:1115`): validates gated entries as it validates skip entries (a reason, a file present in the commit; 32 otherwise). A file named in both `skip` and `gated` for the label is also 32. The request (`:1158`) gains `"gated": [...]`.
- **`fact_lines`** (`:574`): one more line, `session-probe: state=<s> reason=<r> rustdesk=<version or ->`, from the facts' `session_probe`. `check` prints it whatever the state; it is a fact, not a refusal.
- **`_poll`** (`:941`): each `polls.jsonl` record gains `session_probe` (`{state, reason}`) and `stage`. The sleep stays `cfg["poll_s"]`.
- **`_collect_and_summarize`** (`:1045`):
  - The main stage's expected specs are the commit's specs minus the label's `skip` and `gated` files. Its counts, `known` and `new` are computed as now.
  - When the label has gated files, the summary gains `gated: {outcome, reason, files, probe_before, probe_after, counts, new, detail, voided_failures}`.
    - The outcome is one of `GATED_OUTCOMES` (`run`, `skipped-connected`, `skipped-undecided`, `voided-connected-during`, `voided-undecided-during`).
    - `skipped-*` comes from the before probe. `voided-*-during` comes from an after probe, or a poll taken while `stage` was `gated`, that is not `none`. When readings differ, `connected` wins over `undecided`.
    - `new` lists every failing test of the gated report when the outcome is `run`. The `known` list is matched against the main stage only.
    - `detail` lists each RustDesk and `rdpclip.exe` proc of the before probe (and of the after probe when there is one) as `<name> <switches> session=N started=<UTC> age_s=<seconds>`, so a stale `--cm` behind a `skipped-connected` is visible (D-1281).
    - `voided_failures` lists the failing tests of the gated report when the outcome is `voided-*`; it never enters `new` or the exit code (L2, D-1283).
  - Exit: a non-empty `gated.new` exits 40 (`new-failures`), as a main-stage failure does. `skipped-*` and `voided-*` add nothing to the exit.
  - A missing `probe-before.json`, or a `none` before probe with no `gated\report.json`, is 31 (`report-missing`).
- **New names:** `PROBE_STATES` (`none`, `connected`, `undecided`), `GATED_OUTCOMES` and `gated_outcome(before, after, polls)`, a pure function the tests call.
- **`summarize`** stays a main-stage reading of one report; it does not read the gated folder.

### The known list: `tools/e2e_host/known-failures.json` (LF stays LF)

Under the probe (row 6), the label's two `skip` entries go and one `gated` entry comes:

```json
{
  "known": [],
  "skip": [],
  "gated": [
    {"label": "mini-air", "file": "capture-system-clipboard.test.ts", "reason": "system clipboard spec; runs only when the session probe reads no remote session (D-1269)"}
  ]
}
```

Under the fallback (row 7a, D-1274), there is one `skip` entry and no `gated` key:

```json
{
  "known": [],
  "skip": [
    {"label": "mini-air", "file": "capture-system-clipboard.test.ts", "reason": "clipboard spec; grouping §3 Gate"}
  ]
}
```

Both forms are written by a row Python command that checks the row-0 hash first, and both are LF with one final LF.

The grouping's rule that "skip entries name only the clipboard-only file" is met in both forms. Under the probe, `skip` is empty and `gated` names only the new file, so no skip entry names anything else. A skipped file would never run, which is why the probe form uses `gated`. Under the fallback, the one skip entry names only the new file. D-1272 records the check (mandatory: none).

### The run book: `.agent/docs/e2e-remote-host.md` (LF stays LF)

Under the probe, the run book changes in four places.
- **"## What the tool writes on the host"** (`:173`) adds `stage.txt`, `probe-before.json`, `probe-after.json` and the `gated\` folder with its five files.
- **"## The known-failure list"** (`:189`) keeps its Session 97 sentence and adds the `gated` list.
- **A new section, "## The gated clipboard stage (Session 98)"**, placed before "## After poll-timeout" (`:207`). It covers:
  - the probe's states and reasons, and the rule order;
  - the five outcomes and their exits;
  - the `session-probe:` line of `check`;
  - the polls' fields;
  - that a connection during the stage voids its result;
  - the known risk of a short connection between two readings;
  - that a stale RustDesk `--cm` window can skip the stage until it is closed, with `gated.detail` showing its start time (D-1281);
  - that a void discards the result but cannot undo what the tests wrote to that desktop's clipboard (D-1283);
  - that the probe only reads, and never changes RustDesk or stops a process.
- **"## Known risks"** (`:254`) gains that risk in one line, and one line each for the risks of D-1281 (a stale `--cm`) and D-1283 (the clipboard during a void; RustDesk and RDP only; an `rdpclip.exe` in a disconnected RDP session; the English `qwinsta` words).

Under the fallback, the run book gains only a short "## The clipboard spec file (Session 98)" section: the new file is skipped on the mini-air with its reason, and the probe was not shipped, with the named trigger. `test_ac_19_run_book_names_everything` holds in both forms, because every existing line stays.

### The tests

**Edited: `tests/tooling/test_e2e_remote.py`** (LF; row 3). The docstring gains one Session 98 line. `test_ac_11_known_tracked_list` changes as §Test pins names. New constants `PROBE_COPIES`, `PROBE_STATES_T` and `GATED_OUTCOMES_T` are added, then these new tests, every one named `test_s98_*` (helpers `_s98_*`):

| Test | AC | What it proves |
|---|---|---|
| `test_s98_ac_5_gated_schema` | AC-5 | `load_known` takes the probe form and returns `label_gated == ['capture-system-clipboard.test.ts']`. Parametrised refusals: `gated` not a list, an entry without `reason`, an entry not an object, the same file in `skip` and `gated` → 32 through `_run` with a fake host. The request sent to the fake host carries `gated` |
| `test_s98_ac_6_probe_block_identical` | AC-6 | The block exists once in each of `PROBE_COPIES` and is byte-identical; it defines the three functions; each script stays ASCII and LF |
| `test_s98_ac_6_classify_reasons` | AC-6 | Under real Windows PowerShell 5.1, `AvProbeClassify` on fixture facts returns each of the six reasons by the rule order, including the exemptions (the session-0 service and its direct child unreadable → `none`; a grandchild unreadable → `undecided-unreadable`; `--tray` plus `--cm` → `connected-rustdesk-cm`; an empty switch → `undecided-rustdesk-other`) |
| `test_s98_ac_7_gated_run_passes` | AC-7 | A fake host with `none` before, after and in every poll, and a passing gated report → `gated.outcome == 'run'`, exit 0 |
| `test_s98_ac_7_gated_failure_exits_40` | AC-7 | The same with one failing gated test → `gated.new` names it, exit 40, the main stage's `new` empty |
| `test_s98_ac_7_launcher_stages` | AC-7 | `run-e2e.ps1` in a HostRoot with the stubbed probe (`none`, `none`): the main `specs.txt` lacks the gated file, `gated\specs.txt` holds only it, `stage.txt` ends `gated`, `meta.txt` holds the probe lines, `DONE` carries the main exit; the gate variable is seen only in the gated stage (D-1282) |
| `test_s98_ac_7_missing_probe_before_31` | AC-7 | No `probe-before.json` → 31 `report-missing` |
| `test_s98_ac_8_skipped_connected` | AC-8 | Before `connected-rustdesk-cm` → `skipped-connected`, exit 0; the launcher with that stub writes no `gated\` folder; `gated.detail` carries the `--cm` proc's `started` (D-1281) |
| `test_s98_ac_9_skipped_undecided` | AC-9 | Before `undecided-unreadable` → `skipped-undecided`, exit 0 |
| `test_s98_ac_10_voided_after` | AC-10 | Before `none`, after `connected-rustdesk-cm`, a failing gated report → `voided-connected-during`, exit 0, `gated.new` empty, and `gated.voided_failures` names the failing test (D-1283) |
| `test_s98_ac_10_voided_poll` | AC-10 | Before and after `none`, one poll with `stage: gated` and `undecided-rustdesk-other` → `voided-undecided-during`; with one `connected` and one `undecided` poll → `voided-connected-during` |
| `test_s98_ac_10_launcher_after` | AC-10 | The launcher with the stub (`none`, `connected`) writes `probe-after.json` with `connected` |
| `test_s98_ac_12_check_prints_probe` | AC-12 | `check` against a fake host prints exactly one `session-probe:` line with the state, reason and version; `probe-check.py --judge` logic is mirrored by its own selftest |
| `test_s98_ac_12_polls_record_probe` | AC-12 | Every `polls.jsonl` record of a fake run holds `session_probe` and `stage` |
| `test_s98_ac_16_run_book_session_98` | AC-16 | The run book names `GATED_OUTCOMES`, `PROBE_STATES`, every reason of the probe, `stage.txt`, `probe-before.json`, `probe-after.json` and "Session 98" |
| `test_s98_ac_7_launcher_main_exit` | AC-7 | `run-e2e.ps1` in a HostRoot whose fake main stage exits non-zero: `DONE` holds exactly that exit, and the launcher's own exit equals it (L3, D-1283) |
| `test_s98_ac_20_clipboard_file_guard` | AC-20 | The launcher's gated branch sets `AVKIT_E2E_CLIPBOARD_GATED` to `'1'` before its `Start-Process`, and the main branch does not; `capture-system-clipboard.test.ts` holds the guard line once, after its imports, with `GUARD_REASON` (D-1282) |

The launcher test seam:
1. Copy `run-e2e.ps1` into a HostRoot made by `_tree(..., stale=False)` (`:2088`).
2. Insert, right after `# end session-probe\n`, a stub `function AvSessionProbe` that returns the next line of `probe-seq.txt` as an object. PowerShell takes the later definition.
3. Add a fake `ui\scripts\playwright-with-outputfile.mjs` that writes a report and exits.

The tracked script is never changed by a test. The launcher tests run real `powershell.exe` and need the dev-PC desktop unlocked, as `test_ac_15` does.

**No change** to any spec file beyond the split and the new file's guard (D-1282), and no new Vitest. The split's proof is `split-specs.py --check`, `tsc`, ESLint and the dev-PC full run (AC-1 to AC-4).

### Test pins

`pins-check.py` enforces this list over `tests/tooling/test_e2e_remote.py`. It works statement by statement (`ast`) against the row-0 copy:
- `MAY_CHANGE` is `{"<docstring>", "test_ac_11_known_tracked_list"}`;
- `NEW_NAMES` is `{"PROBE_COPIES", "PROBE_STATES_T", "GATED_OUTCOMES_T"}`;
- new functions must start with `test_s98_` or `_s98_`;
- nothing is removed, and no import or class is added.

Its selftest has 13 cases (`plan-selftest-pins-check.txt`).

The spec guard is pinned outside this file: `split-specs.py --check` requires the `GUARD` lines once in the new file, after its imports, and `guard-check.py` proves from Playwright's own list that the two tests are skipped with `GUARD_REASON` when the variable is unset (AC-20, D-1282).

| Pin | What it checks | After this change |
|---|---|---|
| `test_e2e_remote.py:1-11` (the module docstring, "The second-host E2E tool (Session 96, …") | The file's description | **Added text (named):** one sentence before the closing `"""`, saying that Session 98 adds the gated clipboard stage and the session probe (AC-5 to AC-12 and AC-16; D-1269 to D-1272), and that each new case asserts its new name with `hasattr` first, so before Green it fails by assertion |
| `test_e2e_remote.py:1561-1572` (`test_ac_11_known_tracked_list`), the `skip` tuples at `:1567-1568` | The tracked list's entries | **Changed value (M-7, named; D-1275).** The probe form: `skip == []` and `gated == [("mini-air", "capture-system-clipboard.test.ts")]`, each with a reason. The fallback form (row 7a): `skip == [("mini-air", "capture-system-clipboard.test.ts")]`, no `gated`. `known == []` and `Path(m.KNOWN_FILE) == KNOWN` are unchanged |
| `test_e2e_remote.py:1767-1841` (`test_ac_14_*`) | The host scripts' static rules | Unchanged and passing: the block uses no banned word, no backtick, LF ASCII; the launcher keeps one `Start-Process` |
| `test_e2e_remote.py:1960` (`test_ac_15_host_fixture_facts_schema`) | The facts keys | Unchanged; `session_probe` is an extra key and the test checks with `in` |
| `test_e2e_remote.py:2249`, `:2266` (`test_ac_19_*`) | The run book | Unchanged; every line they read stays |
| `test_e2e_remote.py:2285` (`test_ac_21_*`) | Host details | Unchanged |

Any other existing test that fails after Green is S3. A Green that needs a test change not named here is S3, and an M-7 hit: stop.

### Plan-local files (written at plan time)

This folder already holds the files below. All are LF, the Python ones ruff-clean, and none holds a host detail.

| File | Purpose | Rows |
|---|---|---|
| `split-specs.py` | `CLIPBOARD_SPLIT`: `--out`, `--write`, `--check`, `--selftest` | 0, 1, 2, 7a, H1-2 |
| `probe-check.py` | `SESSION_PROBE`: `--block` (identical in the three copies), `--local OUT` (the block on the dev PC through `-EncodedCommand`, recorded, not judged), `--judge RECEIPT` (the split flag: 0 probe, 3 fallback, 1 malformed), `--judge-gate SUMMARY` (the gating probes in row 8's `summary.json`: 0 confirmed with `ungated: resolve` or `ungated: open`, 3 flip to the fallback, 1 malformed; D-1280), `--selftest` (28 cases) | 0, 5, 7a, 8, H1-2 |
| `guard-check.py` | `CLIPBOARD_NEVER_DEVPC` in tracked code (D-1282): `--list OUT` (Playwright `--list` through `npm run test:e2e`, with `AVKIT_E2E_CLIPBOARD_GATED` and `ELECTRON_RUN_AS_NODE` removed; it runs no test), `--judge OUT` (30 files, 239 tests, the two clipboard tests skipped with `GUARD_REASON`, every other test listed to run), `--selftest` (8 cases) | 0, 2, H1-2 |
| `pins-check.py` | §Test pins, with its selftest | 0, 3, 7a, H1-2 |
| `snapshot-commit.py` | `SNAPSHOT_NO_REF`, copied from Session 97 unchanged in logic | 0, 8, H1-2 |
| `host-details-scan.py` | `LOCAL_HOST_DETAILS` over this session's tracked files, printing key names only | 0, 9, H1-2, H1-6 |
| `baseline.ps1`, `session-gate.ps1` | Row 0 and the gate | 0, H1-2 |
| `flake-run.py` | The dev-PC runs, `EXCLUDED` and `OLD_CLIPBOARD` (D-1276) | 0, 1, 2, 7b, H1-2 |
| `identity.py`, `eol-check.py`, `red-check.py`, `host-load.ps1` | Copied from Session 97 (Session 96 RULE-3); `red-check.py`'s `DECLARED_NEW` names `label_gated`, `gated_outcome`, `GATED_OUTCOMES` and `PROBE_STATES` | 0, 3, H1-2 |
| `issue-resolve.py` | Copied from Session 97; `RESOLVE_KEYS` unchanged | 9 |

Each copy changes only its scope lists, its scratch folder and its docstring's first paragraph, and its selftest passes at plan time (`plan-selftest-*.txt`).

**No partial file.** `split-specs.py --write` writes three temporary files and renames them only when all three are written. An existing `--out` folder file refuses, and so does an existing `snapshot-commit.py --out` (row-0 sentinel, Session 96 RULE-2). The known list is written by one `os.replace` from a temporary file in the same folder.

### Boundary Inventory

| Boundary | Input | Owner | Refusal |
|---|---|---|---|
| The split | The `b59207b` blobs of the two old files | `split-specs.py` | `--write` refuses unless both old files equal their base blobs and the new file is absent; `--check` exits 1 on any byte or invariant difference; exit 2 on a missing block (AC-1, AC-2) |
| Dev-PC runs | The spec list | `flake-run.py` | Exit 2 before any run while either old file matches `CLIPBOARD_CALL`; `--expect-total` other than the count is a failure (AC-4) |
| The known list | `known-failures.json` | `load_known`, `_run` | 32 on a malformed `gated` entry, a missing reason, an absent file, or a file in both `skip` and `gated` (AC-5) |
| The probe | Process, session and version state on the host | The probe block | No refusal: any read error is `undecided-probe-failed`, which skips the stage (AC-6) |
| The gated result | `probe-before.json`, `gated\report.json`, `probe-after.json`, the polls | `_collect_and_summarize` | 31 when an expected file is missing; 40 on a gated failure under `run`; otherwise the outcome is reported (AC-7 to AC-10) |
| The split flag | `check`'s `session-probe:` line | `probe-check.py --judge` | Exit 3 → the fallback (AC-18); exit 1 → S11 |
| The gating probe | Row 8's `summary.json` `gated.probe_before` and `gated.probe_after` | `probe-check.py --judge-gate` | Exit 3 → row 8b flips the flag to the fallback (AC-18); exit 1 → S11 (D-1280) |
| The dev-PC guard | Playwright's `--list` report with the gate variable removed | `guard-check.py --list` | Exit 1 when the two clipboard tests are not skipped with `GUARD_REASON` or a count differs; exit 2 on a setup failure (AC-20, D-1282) |
| Remote run | The snapshot commit | `tools/e2e_remote.py run` | Its exit table: 20 to 24 (S10), 25 to 34 and 10, 11 (S11), 40 (S12 unless only gated and a primer failure), 32 a stale known list |
| Snapshot commit | `HEAD`, the named working paths | `snapshot-commit.py` | Session 97's refusals (AC-13) |
| Registers | `known-issues.yaml`, the grouping row | `issue-resolve.py`, `tools/issue_triage.py` | Each tool's own refusals; a hash other than row 0's is S4 |
| Receipts | `D/` and `C:/Temp/av-kit/e2e-remote/<run-id>/` | Each row | A receipt parsed later is written by Python (Session 95 RULE-2/3) |

**M-4: none.** No API route, OpenAPI document, MCP tool shape, backend service, persisted setting, database schema or exit code changes. The tool's summary gains one key, `gated`, which only this session's tests and the run book read. The host scripts' JSON gains `session_probe` and `stage`, which only the tool reads. No product code changes: `ui/src`, `packages/`, `mcp-server/src` and `backend/` are untouched. Nothing reads user data: the specs use a scratch `AVKIT_APP_DATA` and the fake E2E backend, and the probe reads no file under a user folder.

### Acceptance Criteria

The AC ids are this plan's own: there is no MEU, so they are `AC-1` to `AC-20`, as Session 96's were. The AC ids quoted from spec titles (`AC-88.12`, `AC-89.9`, `AC-89.15`, `AC-132.22`, `AC-132.23`, `C1-5`, `AC-71.15`) belong to MEU-88, MEU-89, MEU-132 and Session 78 (Session 83 RULE-1). This plan moves or names their lines and never changes them.

| AC | Type | Description | Source | Negative Test |
|---|---|---|---|---|
| AC-1 | row | `CLIPBOARD_SPLIT`: after row 2, `split-specs.py --check` exits 0, and the three tracked files' SHA-256 equal the plan-time values (`f848f6b4…`, `02699784…`, `e6a28e77…`; `plan-split-out-3.txt`) | Grouping §3 Session 98; D-1268 | At rows 0 and 1, `--check` exits 1 naming three problems (the new file absent, both old files still holding the moved tests; `plan-split-check-red-3.txt`) |
| AC-2 | row | Each moved block equals its `b59207b` block after CRLF to LF. The new file holds the two moved titles once each, and the old files the five kept titles once each. Of the three, only the new file matches `CLIPBOARD_CALL`. The new file holds the `GUARD` lines once, after its imports (D-1282). The filmstrip file is CRLF only, and the other two LF only | D-1268; M-7 (no assertion changes) | `split-specs.py --selftest` refuses a changed assertion, a changed block, a CRLF new file, a clipboard call left in an old file and a new file without its guard (6 cases, `plan-split-selftest-3.txt`) |
| AC-3 | row | `npm run typecheck` and ESLint on the three spec files exit 0 through `pwsh` from `ui` at row 2 and in the gate (`ui-types`, `ui-lint`) | D-1268 | At plan time the built import file with one planted unused constant, linted through stdin, fails ESLint (`plan-eslint-neg-3.txt`); the tracked file is never written |
| AC-4 | row | `CLIPBOARD_NEVER_DEVPC`: at row 7b, `flake-run.py --mode full --runs 1 --no-burn --expect-total 237` passes 237 of 237 in 29 files, the five kept titles among them and the new file not run. `--list-check` gives 239 at row 0 and 237 after row 2 | Grouping §3 "the five pass in a dev-PC full run"; D-1276 | At row 1 `flake-run.py --mode full` exits 2 before any run (`OLD_CLIPBOARD`: both old files still call the clipboard; `plan-flake-guard-head.txt`) |
| AC-5 | test | `test_s98_ac_5_gated_schema`: the probe form of the list loads; `label_gated` returns the new file; a malformed `gated` (not a list, no reason, not an object) and a file in both `skip` and `gated` each exit 32 through `_run`; the request carries `gated` | D-1272 | Fails by assertion at row 3 (`label_gated` absent) |
| AC-6 | test | `SESSION_PROBE`: `test_s98_ac_6_probe_block_identical` (one block, the same bytes, in the three copies, defining the three functions) and `test_s98_ac_6_classify_reasons` (under PS 5.1, each of the six reasons by the rule order, the exemptions included). `probe-check.py --block` exits 0 after row 5 | D-1270; D-1271 | Fails by assertion at row 3 (no block). `probe-check.py --block` exits 1 at row 0 with three problems (`plan-probe-block-red.txt`) |
| AC-7 | test | `GATED_STAGE`, outcome `run`: a passing gated report gives `run` and exit 0; a failing one gives exit 40 with `gated.new` naming it; the launcher writes the stage files in order; a missing `probe-before.json` is 31 | D-1269; D-1272 | Fails by assertion at row 3 (`GATED_OUTCOMES` absent; the launcher writes no `stage.txt`) |
| AC-8 | test | Before `connected-rustdesk-cm`: outcome `skipped-connected`, exit 0, the launcher writes no `gated\` folder, and `gated.detail` names the `--cm` proc with its `started` | D-1269; D-1281 | Fails by assertion at row 3 |
| AC-9 | test | Before `undecided-unreadable`: outcome `skipped-undecided`, exit 0 | D-1270 | Fails by assertion at row 3 |
| AC-10 | test | A session during the stage voids it: an after probe of `connected` gives `voided-connected-during`, exit 0, with `gated.new` empty even when the report failed; a stage-gated poll of `undecided` gives `voided-undecided-during`; `connected` wins when both appear; the launcher writes the after probe; a voided report's failures are listed in `gated.voided_failures`, outside `new` and the exit code | Grouping §3 "a session that connects during the stage voids it"; D-1272; D-1283 | Fails by assertion at row 3 |
| AC-11 | row | `pins-check.py` exits 0 at rows 3 and 7a and in the gate: only the docstring and `test_ac_11_known_tracked_list` change among the row-0 statements, and every new statement is a `test_s98_`/`_s98_` function or a `NEW_NAMES` assignment. The test file's hash recorded at row 3 (`ecs-test-sha-3.json`; under the fallback, `ecs-test-sha-7.json`) holds to the gate | M-7; D-1275 | `pins-check.py --selftest` (13 cases: a changed unnamed test, a removed test, an added import, an unprefixed function, a CRLF flip each fail; `plan-selftest-pins-check.txt`) |
| AC-12 | test | `test_s98_ac_12_check_prints_probe` and `test_s98_ac_12_polls_record_probe`. At row 7a, `D/ecs-check-7.txt` holds exactly one `session-probe:` line, which `probe-check.py --judge` reads. At row 5, `probe-check.py --local` writes a dev-PC probe with a valid state and reason | D-1271; D-1273 | Fails by assertion at row 3. `probe-check.py --selftest` refuses a receipt with no line, two lines, or a state or reason outside the lists, and `--judge-gate` judges the five outcomes, the fallback reasons before and after, and malformed objects (28 cases) |
| AC-13 | row | `SNAPSHOT_NO_REF`: `snapshot-commit.py --out D/ecs-snapshot-8.json` over §Files Modified's code and test paths and the known list; `--verify` exits 0 at row 8 and in the gate; the guards (index bytes, `for-each-ref`, `HEAD`'s target, `status --porcelain=v1 -z`) are equal before and after; the author is the noreply identity | D-1279 | Row 0's sentinel at the `--out` path refuses with exit 1 and keeps its bytes; the selftest's negative cases (Session 97's) each refuse |
| AC-14 | row | The mini-air run (row 8, or row 8b after a flip; D-1280), `tools/e2e_remote.py run <snapshot>`: the main stage has `tests` 237, `expected` 237, `unexpected` 0, `flaky` 0, `skipped` 0, `spec_files` 29, `new` `[]`, `overlap` `[]`, and the commit equal to the snapshot. Under the probe, `gated.outcome` is one of `GATED_OUTCOMES` and `gated.files` is the new file; under the fallback, `skip` names only the new file. Exit 0, or 40 with only gated failures. The gated outcome and reason are a receipt (D-1279) | Grouping §3 "one real mini-air run"; D-1279 | Row 8's Python check exits 1 on any other main count; the gate's `remote-evidence` reads the same `summary.json` |
| AC-15 | row | Under the probe, `E2E-CLIPBOARD-SPECS-UNGATED` is `resolved` through `issue-resolve.py` only when row 8's `probe-check.py --judge-gate` prints `ungated: resolve` (`D/ecs-judge-gate-8.txt`), with verification naming the row-8 run id, the main counts, the gated outcome and, for `skipped-connected`, `gated.detail`. Otherwise it stays `open`, with that verification citing `ecs-judge-gate-8.txt` and the reason (`skipped-undecided`, `voided-undecided-during`), or `ecs-flip-8b.txt` after a flip, or the fallback trigger. `E2E-CLIPBOARD-PRIMER-EMPTY` stays `open` with its verification updated by the row-8 gated outcome, and gets that run's receipts when AC-88.12's primer failed there | D-1278; D-1280; PRIMER-EMPTY's own rule | `issue-resolve.py` refuses a key outside `RESOLVE_KEYS` or an issue not named; a register hash other than row 0's stops the row (S4) |
| AC-16 | test | `test_s98_ac_16_run_book_session_98`; `test_ac_19_*` still pass. Under the fallback, the short Session 98 section names the trigger, and `test_ac_19_*` passes | D-1271; D-1274 | Fails by assertion at row 3 (no Session 98 text) |
| AC-17 | row | `LOCAL_HOST_DETAILS`: `host-details-scan.py` over this session's new and edited tracked files, this plan folder and the handoff exits 0 at row 9, in the gate and at H1-6; `tools/check_home_path.py` shows no new hit before (row 0) and after (gate) | Brief §Security; Session 96 AC-21 | At row 0 a scan of a scratch file holding the config's alias exits 1, printing the key name only |
| AC-18 | row | The split flag is decided by evidence at row 7a and written to `D/ecs-split-flag.txt`. `probe` when `probe-check.py --judge D/ecs-check-7.txt` exits 0 and rows 3 to 5 went green with no unnamed test change. `fallback` when the judge exits 3 or a fake-host test cannot go green. Under the fallback: the tool and the three host scripts equal their row-0 copies, the `test_s98_` tests and `NEW_NAMES` are removed, `test_ac_11` takes its fallback value, and the known list and run book take their fallback forms. The flag is provisional: row 8's `probe-check.py --judge-gate` exit 3 flips it at row 8b (trigger `limited-unreadable`), which reverts as row 7a's fallback does and reruns the mini-air run once in the fallback form | Grouping `:84`; D-1274; D-1280 | `probe-check.py --selftest` judges `undecided-probe-failed` and `undecided-unreadable` as exit 3, and `--judge-gate` its limited-before, failed-before and limited-after cases as exit 3; the gate's `known-list` step fails a list that does not match the recorded flag |
| AC-19 | row | `E2E-DEVPC-CLIPBOARD-SPECS` is added (low, `ui`, TECH-DEBT, P4) through `add_issue` and `save` in `tools/issue_triage/model.py`, the code `issue_triage.py add` runs (its CLI has no category flag): `C1-5` (`console-chrome.test.ts:77`) and `AC-71.15` (`mcp-setup-prompt.test.ts:91`) write the main-process clipboard in every dev-PC full run. Grouping row 98 (`:108`) is set to `executed (Session 98)` with this plan's folder. `issue_triage.py render --check` exits 0 | D-1277 | `add_issue` refuses an id that exists (`DuplicateIdError`); the row checks that the two spec files keep their row-0 hashes |
| AC-20 | row | `CLIPBOARD_NEVER_DEVPC` in tracked code: the new file skips itself unless `AVKIT_E2E_CLIPBOARD_GATED=1`, which only `AvStage -Gated` sets; `guard-check.py --list` exits 0 at row 2 and in the gate's `guard-list` step (239 listed in 30 files, the two clipboard tests skipped with `GUARD_REASON`, none run); `test_s98_ac_20_clipboard_file_guard` passes; `.agent/docs/commands.md` names the guard in two lines (row 6) | Expert pass M2; D-1282 | At row 0 `guard-check.py --list` exits 1 (`plan-guard-list-head.txt`); `--judge` fails a list made with the variable set (`plan-guard-judge-set.txt`, 4 problems); its selftest's 8 cases |

### Spec Sufficiency Table

| Question | Answer | Source |
|---|---|---|
| Which tests move? | The two that call the system clipboard, with the blocks only they use; the five others stay | D-1268; `plan-deps.txt` |
| Where may the clipboard tests run? | Only on the mini-air, only in the gated stage, never on the dev PC | Session 57 RULE-4; grouping §3; D-1269, D-1276, D-1282 |
| What is a remote session? | A RustDesk `--cm` process or an RDP session; anything unreadable or unknown is undecided | D-1270; RustDesk source |
| What does undecided do? | Skips the stage, like connected | D-1270 |
| What if someone connects during the stage? | Its result is voided and reported | D-1272; grouping §3 |
| How does a gated failure count? | Exit 40, in `gated.new`, apart from the main `new` | D-1272 |
| Does an exit code or API change? | No | D-1272; M-4 none |
| What if the probe cannot read the host? | The split ships alone, and the file stays skipped there | D-1274; grouping `:84` |
| Which existing test changes? | Only `test_ac_11_known_tracked_list` and the test file's docstring | D-1275 |
| How does the mini-air run uncommitted work? | A commit on no ref, built with a temporary index | D-1279 |
| Is the gated outcome a pass condition? | No; a receipt. A primer failure feeds PRIMER-EMPTY | D-1278, D-1279 |
| The other dev-PC clipboard writers? | A new issue only | D-1277 |
| Which probe reading decides? | The launcher's own, at run level Limited in the desktop session, judged at row 8; row 7a's elevated reading is provisional | D-1280 |

#### Files Modified

| Path | Change | Row | Line endings |
|---|---|---|---|
| `ui/tests/e2e/capture-system-clipboard.test.ts` | New: the two clipboard tests and their blocks, and the file-level guard (D-1282) | 2 | LF |
| `ui/tests/e2e/capture-filmstrip-actions.test.ts` | `AC-88.12 (a)(b)(f)` and five helpers out; one comment line in | 2 | CRLF (388 lines) |
| `ui/tests/e2e/capture-import.test.ts` | `AC-132.23` and seven helpers out; one comment line in | 2 | LF (425) |
| `tests/tooling/test_e2e_remote.py` | The docstring line, `test_ac_11`, the `test_s98_` tests and three constants | 3 (7a under the fallback) | LF (2,305) |
| `tools/e2e_remote.py` | `gated` (with `detail` and `voided_failures`, D-1281, D-1283), the outcomes, the probe line, the polls | 4 | LF (1,396) |
| `tools/e2e_host/host-facts.ps1` | The probe block, `session_probe` | 5 | LF (281) |
| `tools/e2e_host/host-status.ps1` | The probe block, `session_probe`, `stage`, the gated `pid_file` | 5 | LF (268) |
| `tools/e2e_host/run-e2e.ps1` | The probe block (procs with `started`), `AvStage` (with `-Gated`, D-1282), the gated stage | 5 | LF (120) |
| `tools/e2e_host/known-failures.json` | The probe form (row 6) or the fallback form (row 7a) | 6, 7a | LF (7) |
| `.agent/docs/e2e-remote-host.md` | The Session 98 section and three edits, or the fallback section | 6, 7a | LF (259) |
| `.agent/docs/commands.md` | Two lines naming the clipboard file's guard (D-1282) | 6 | CRLF (226) |
| `.agent/context/known-issues.yaml` | Two issues updated, one added | 9 | LF (6,079) |
| `.agent/context/known-issues.md` | Generated by `render` | 9 | LF (35) |
| `.agent/context/grouping/2026-11-20-e2e-clipboard-specs-session-grouping.md` | Row 98 (`:108`) only | 9 | LF (131) |
| `.agent/context/current-focus.md` | One entry | H1-3 | CRLF (242) |
| `docs/execution/metrics.md` | One row | H2-3 | CRLF (107) |
| The handoff, the implementation review, the reflection | New | H1-6, H1-7, H2-2 | LF |
| This plan folder | Written at plan time; `split-specs.py` docstring only after that | — | LF |

**Outside the repository** (never tracked):
- receipts under `D` and `C:/Temp/av-kit/e2e-remote/<run-id>/`;
- on the mini-air, the tool's own `bin\`, `runs\<run-id>\` and `results\<run-id>\` (with `gated\`) under its configured root, in Session 96's layout; nothing else there is touched;
- the snapshot commit object in `.git/objects`, on no ref.

**Read, never changed** (bound in `baseline-scope.json`): `ui/tests/e2e/console-chrome.test.ts` (CRLF, 232), `ui/tests/e2e/mcp-setup-prompt.test.ts` (CRLF, 165), `ui/tests/e2e/electron-app.ts`, `electron-env.ts`, `global-setup.ts`, `ui/playwright.config.ts`, `ui/scripts/playwright-with-outputfile.mjs`, `ui/package.json`, `tools/e2e_host/host-lock.ps1`, `host-prepare.ps1`, `host-release.ps1`, `host-start.ps1`, `e2e-host.example.json`, `docs/BUILD_PLAN.md`, `.github/workflows/ci.yml`.

**Line endings** were measured with Python bytes (`plan-eol.txt`, and again for this table). `capture-filmstrip-actions.test.ts`, `current-focus.md` and `metrics.md` are CRLF and stay CRLF. Every other scope file is LF and stays LF. The new spec file is LF (the moved CRLF lines become LF), written as bytes (Session 83 RULE-3). `eol-check.py` checks every scope path against its row-0 copy.

**Foreign class** (Session 92 RULE-3): `.agent/model-registry.local.json`, `.claude/agents/*.md` and `.cursor/agents/*.md` belong to the coordinator. Row 0 binds them by hash. A change during the session is recorded in the handoff; it is not S4, and stays out of the commit paths.

## Out of Scope

| Item | Basis |
|---|---|
| Any product code (`ui/src`, `packages/`, `mcp-server/src`, `backend/`) | Grouping §3 Gate |
| An assertion, timeout or wait in any moved or kept spec | D-1268; M-7 |
| `C1-5` and `AC-71.15` on the dev PC | D-1277: a new issue only |
| Closing `E2E-CLIPBOARD-PRIMER-EMPTY` | Its own rule needs repeated gated passes; D-1278 |
| RustDesk's settings, service, clipboard option or version on either host; stopping or starting any RustDesk process | Brief hard stops; D-1216 |
| Smart App Control, auto sign-in, a self-hosted runner, any workflow or runner change | D-1216; brief |
| The host's scheduled task, config, account or known-hosts entry | Session 96's; the tool uses them unchanged |
| A probe that blocks a connection, or holds the desktop during the stage | D-1269: the probe reads, it does not prevent |
| Linux or macOS hosts (`--cm-no-ui`) | Named in the classifier for completeness; no such host exists |
| `py-types`, MCP and OpenAPI suites | `packages/` and `mcp-server/` unchanged (H1-4 proves it) |

## BUILD_PLAN.md Audit

No MEU (D-1261; grouping §3 Session 98 "(no MEU)"). `docs/BUILD_PLAN.md`, `meu-status.yaml` and `meu-registry.md` are not edited; `docs/BUILD_PLAN.md` is in "Read, never changed". The gate's `state-render` step (`meu_status.py render --check`) proves that nothing generated drifted.

## Verification Plan

### 1. Baseline (row 0)

`baseline.ps1`, in the shape of Session 97's, runs ten fail-fast steps:
1. `uv sync --frozen --offline --all-packages` (S7 on a held file).
2. The record:
   - `HEAD` must be `b59207b` (S2);
   - the dirty set with the foreign class marked, and `git worktree list`;
   - every commit since `b59207b` and the scope diff since it, which must be empty;
   - `baseline-scope.json` over §Files Modified, "Read, never changed" and the foreign class, with the new spec file, the handoff, the implementation review and the reflection absent;
   - `baseline-dirty-hashes.json`;
   - the row-0 copies under `D/baseline-copies/`;
   - `baseline-eol.json`;
   - `baseline-skip-hashes.json` over `packages/`, `mcp-server/{src,scripts,tests}` and `native/`, with the secret names dropped before any stat (Session 83 RULE-2);
   - the 30 S2 anchors (§What the code shows);
   - the known list (two `skip`, no `known`, no `gated`);
   - both issues `open` with `meu_links: []` (`yaml.safe_load`, by key);
   - row 98 `pending`;
   - 29 spec files;
   - the clipboard calls of the four clipboard spec files, and no fifth E2E file calling the clipboard (D-1277);
   - no graphify graph (S1);
   - the plan, task and plan-review hashes.
3. The OS-wide probe (Session 91 RULE-1: `host-load.ps1` and every Electron and node process).
4. The home-path check before (S8).
5. The plan checkers' selftests, and `eol-check.py`.
6. `split-specs.py --out` into a new folder, each file's SHA-256 against its plan-time value (S9).
7. The row-0 refusals:
   - `split-specs.py --check` exits 1;
   - `probe-check.py --block` exits 1;
   - `flake-run.py --mode full` exits 2 before any run;
   - `--list-check` gives 239;
   - `guard-check.py --list` exits 1 (no guarded file yet; D-1282).
8. The `snapshot-commit.py --out` sentinel.
9. The host-detail scan and its sentinel.
10. Ruff on this folder's Python.

The last line is `baseline: all steps exit 0`.

### 2. Red, then Green (rows 1 to 7a)

**The split goes first** (rows 1 and 2):
- Row 1 records its Red: `--check` exits 1, the dev-PC guard exits 2, and the list is 239.
- Row 2 writes the split. Then `--check` exits 0, `tsc` and ESLint pass, the list is 237, and the Vitest files that read the E2E folder (`queue-primitives`, `queue-card`, `e2e-harness`) pass, and `guard-check.py --list` exits 0 (AC-20).

**The tool goes next.**
- Row 3 writes the Red tests. Every `test_s98_` test fails by assertion, and `red-check.py --require` proves it for each AC prefix. `pins-check.py` exits 0, and the test file's hash is recorded.
- Row 4 is the tool Green: AC-5, AC-7 to AC-10 and AC-12 pass, except the launcher cases.
- Row 5 is the host Green: AC-6 and the launcher cases pass; `probe-check.py --block` exits 0 and `--local` records the dev PC.
- Row 6 writes the run book, the probe form of the list and the two `commands.md` lines (D-1282). AC-11 and AC-16 pass, and the full `test_e2e_remote.py` passes.

**Row 7a** runs `check` against the mini-air and judges the split flag (D-1274), provisionally: row 8's `--judge-gate` can flip it (D-1280). Under the fallback it reverts the probe work as AC-18 names, and the full tool tests pass again.

**Row 7b** first runs the full Vitest and the gate's `ruff format --check` and `ruff check` argv, so a failure there shows before the snapshot (L4, D-1283); then the dev-PC full run (AC-4).

### 3. Real host (rows 8 and 8b)

1. `snapshot-commit.py --out D/ecs-snapshot-8.json` over the §Files Modified code and test paths and the known list, then `--verify`.
2. `tools/e2e_remote.py check`.
3. `tools/e2e_remote.py run <commit>`, in the background, waited on with Monitor.
4. A Python check of `summary.json` (AC-14).
5. `probe-check.py --judge-gate` on that `summary.json` (D-1280). Exit 3 sends the session to row 8b, which flips the flag to the fallback (trigger `limited-unreadable`), reverts as row 7a would, and runs steps 1 to 4 once more in the fallback form.

The stops:
- a busy, locked or unsigned host is S10;
- any other refusal, or a `--judge-gate` exit 1, is S11;
- a main count other than AC-14's, or a gated failure other than the primer, is S12;
- a scope change after the last run (row 8, or 8b after a flip) is S13.

### Session gate (H1-2)

`session-gate.ps1`, in the shape of Session 97's: fail-fast, later steps printed `not_run`, and the last line `session-gate: all steps exit 0`.

| Stage | Steps |
|---|---|
| Identity | `identity-before` (`identity.py`, which clears `ELECTRON_RUN_AS_NODE`, Session 88 RULE-3) |
| Static | `task-contract`; `scope-paths`; `line-endings` (`eol-check.py`); `home-path`; `host-details`; `split-check`; `guard-list`; `pins`; `probe-block`, `probe-local` and `gate-judge` (skipped under the fallback); `known-list` (the form the split flag names); the selftests of `red-check`, `eol-check`, `split-specs`, `probe-check`, `pins-check`, `guard-check` and `snapshot-commit`; `py-format` and `py-lint` (`ruff` on the tool, its tests and this folder's Python; `ruff check tools/ tests/`); `snapshot-verify` (else S13); `test-hashes` (S3) |
| UI static | `ui-types`, `ui-lint` (from `ui`) |
| Tests | `ui-tests` (Vitest, the full suite); `py-tests` (`pytest tests/ -x -q`); `canon` (`layout-canon`, `queue-canon`) |
| Host load | `host-load` (Session 81 RULE-2; 50 %) |
| E2E | `ui-build`; `e2e-full` (`flake-run.py --mode full --runs 1 --no-burn --expect-total 237`: the new file excluded, an unrecorded failure rerun once alone, a second failure or any `unhandled rejection:` line stops) |
| Registers | `issues-render-check`; `state-render`; `remote-evidence` (row 8's `summary.json`, or row 8b's after a flip: 237 and 237, no `new`, commit equal to the snapshot, the gated object by the flag, the tool and host-file hashes equal to `tool_sha256`) |
| Identity | `identity-after` |
| Skipped, with reasons | `py-types`, `mcp-types`, `mcp-tests`, `mcp-build`, `openapi`, `mcp-audit`: every file under `packages/`, `mcp-server/{src,scripts,tests}` and `native/` keeps its row-0 hash (H1-4) |

## Stop Conditions

| Id | Condition | Action |
|---|---|---|
| S1 | `graphify-out/` appears | Stop; re-plan the context tool decision |
| S2 | Any of these at row 0: <br>• `HEAD` is not `b59207b`, or a commit since it touches a scope path; <br>• a row-0 anchor is gone or changed in meaning; <br>• the known list is not its row-0 form, or an issue is not `open`; <br>• row 98 is not `pending`; <br>• the spec count is not 29, or an E2E file other than the four named calls the clipboard | Stop. A line that only moved is recorded in the handoff (Session 51 RULE-3); anything else goes to the coordinator |
| S3 | Any of these: <br>• a Red test fails for a setup reason, or passes; <br>• a Green needs a test change §Test pins does not name (M-7); <br>• an existing test fails after Green; <br>• a test file's hash moves after its Red outside the named fallback | Stop; never edit a test to pass |
| S4 | `git status` lists a path outside this plan's scope, `baseline-dirty.txt` and the foreign class, or a scope path that no earlier row wrote differs from `baseline-scope.json` | Stop and ask the coordinator; never commit, stash or revert another session's work |
| S5 | A dev-PC full run fails a test that its solo rerun does not clear, or holds `unhandled rejection:`. `flake-run.py` prints Session 91's labels, `S5` and `S10`, for these | A finding, not a retry: stop, record the receipts, tell the coordinator. A failure of one of the five rejoined tests is recorded under `E2E-CLIPBOARD-SPECS-UNGATED`'s verification |
| S6 | Codex is unavailable or the ledger refuses a round | The coordinator |
| S7 | `uv sync` fails on a held file, or the dev PC's load stays above 50 % after `flake-run.py`'s ten-minute wait (it prints Session 91's `S8`) | Tell the coordinator; never stop a process |
| S8 | The home-path check or the host-detail scan finds a new hit | Stop; fix the file, never extend the allow-list |
| S9 | `split-specs.py --out` at row 0 differs from the plan-time hashes, or `--check` fails after row 2 | Stop: the base blobs are not what the plan measured |
| S10 | At row 7a, 8 or 8b the host refuses 20, 21, 22, 23 (a lock this session did not take) or 24, or the run's `overlap` is not empty | Not a finding: record it, wait 15 minutes and run `check` again, up to 8 times. If it is still refused, tell the coordinator. Never stop a process, release another run's lock or start the task by hand |
| S11 | At row 7a, 8 or 8b, any other refusal (10, 11, 25 to 31, 33, 34), the final release keeps the lock (`lock_kept`), or `probe-check.py --judge` or `--judge-gate` exits 1 | Stop and record. Run `release` once with this session's own run id. Never bypass or re-pin the host key (11 goes to Mat), install anything or change the task. A second S11 goes to the coordinator |
| S12 | Row 8's (or 8b's) main counts are not AC-14's, or a gated test under outcome `run` fails with anything but AC-88.12's `primer: clipboard image read stayed empty` | A finding, not a retry: stop, record the summary in the handoff, tell the coordinator; no change to the known list or a test. A primer failure alone is not S12: row 9 adds its receipts to `E2E-CLIPBOARD-PRIMER-EMPTY` |
| S13 | A snapshot scope file changes after row 8 (or 8b after a flip) | Rename that row's `ecs-*-8*` receipts (8b included) with `-r1`, then snapshot and rerun whichever of rows 8 and 8b ran last once more on the final files, once only; a later change goes to the coordinator |

## Decision Log

> [!NOTE]
> D-1268 to D-1283 are this plan's sixteen briefs; D-1280 to D-1283 adopt the expert pass (`ecs98-expert-pass.txt`). The §4a walk:
> - **M-1** (push, merge, release): none. The row-8 snapshot is a commit object on no ref, and the coordinator commits after the review with no push.
> - **M-2** (destructive): none. No spec test is deleted: two move byte for byte. The known list loses two `skip` entries whose file is split, and no register entry is removed.
> - **M-3** (new policy): none. The gated outcome follows the grouping's own rule (D-1267).
> - **M-4** (API, MCP tool, external contract): none. `REASONS` and every exit code are unchanged; the summary gains a `gated` object beside the main fields. The grouping's "skip entries name only the clipboard-only file" is met: `skip` is empty under the probe and names only the new file under the fallback (D-1272). D-1281 and D-1283 add `detail` and `voided_failures` to that object, which only this session's checks read; no exit code changes (checked, not hit).
> - **M-5** (visible product change): none. No product code changes.
> - **M-6** (source conflict): D-1273 reads the mini-air with one encoded command instead of the brief's copied script; D-1274 decides the split flag at row 7a instead of at plan time; D-1279 builds a commit object while the rule says not to commit.
> - **M-7** (assertion change no row names): checked and not hit. D-1275 names the one test and its new assertion in row 3 (HDP `:158`), and `pins-check.py` stops any other change. D-1282 adds the guard line to the new file, outside every test body and moved block, named by AC-20 (checked, not hit).
> - **M-8** (scope): D-1277 adds a register entry beyond the grouping's two issues. D-1282 edits `.agent/docs/commands.md`, a file beyond the grouping's list, and adds the guard line to the split's new file.
> - **M-9** (review exit), **M-10** (human action): none. The mini-air is set up and signed in; no row asks Mat to connect or disconnect. D-1281 checked: proving the `--cm` lifetime with a real connect and disconnect cycle would be a human action, so the plan names the risk instead, and a stale skip is a finding.
> - **M-11** (waived gate): none. The new file's skip or void on the mini-air is the grouping's own rule (D-1267), and the dev-PC exclusion is Session 57 RULE-4; no test is skipped that the grouping wants run. D-1282 checked: the guard skips the file only where it must never run, and the gated stage sets the variable.
> - **M-12** (disclosure), **M-13** (permission or trusted remote), **M-14** (headless): none. Nothing leaves Mat's machines; the host key was pinned in Session 96; host details stay in the untracked config.
>
> So D-1273, D-1274 and D-1279 are `mandatory: [M-6]`, D-1277 and D-1282 are `[M-8]`, and the other eleven are `mandatory: none`. All sixteen are handed to the agent under Mat's words, and the hand-over covers M-6 and M-8 (HDP `:327-330`). `open_decisions` is empty, and there is no STOP item. D-1284 stays free, and D-1285 to D-1287 are kept for execution.
>
> **Earlier rows are not copied here.** D-1265, D-1266 and D-1267 live in the grouping's §8 (`:124-126`), with D-1200, which stays open and Mat's (M-12). D-1261 and D-1262 live in the two issues' `enrichment.decision_log`. H2-2 reads them through `--decision-source` on the grouping (this plan's `grouping_source`) and `.agent/context/known-issues.yaml`, with `--decision-issue E2E-CLIPBOARD-SPECS-UNGATED` and `--decision-issue E2E-CLIPBOARD-PRIMER-EMPTY`. `decision_sources` was probed at plan time with that list (Session 90 RULE-2): 4 ids from the grouping alone (D-1200, D-1265 to D-1267), 6 with the register and both issues (`ecs-plan-decisions-1.txt`), a third run over this plan with them (`ecs-plan-decisions-2.txt`), and a fourth after the expert pass added D-1280 to D-1283 (`ecs-plan-decisions-3.txt`). Under HDP §6 the reflection's `### Decisions Log` lists only this session's own reversible autonomous choices.

```yaml
decision_log:
  - id: D-1268
    stage: planning
    question: "How do the five capture tests that only share a file with a clipboard test rejoin every full run?"
    resolution: autonomous
    class: two-way
    mandatory: none
    chosen: "A: split-specs.py moves AC-88.12 (a)(b)(f) and AC-132.23, with the helpers only they use, into the new ui/tests/e2e/capture-system-clipboard.test.ts (LF). Each moved block keeps every byte except the filmstrip lines' CRLF, which becomes LF. The new file carries its own copy of the shared helpers. The five others stay in their files byte for byte, and split-specs.py --check proves all three files against the b59207b blobs."
    source_tag: Local Canon
    precedents:
      - ".agent/context/grouping/2026-11-20-e2e-clipboard-specs-session-grouping.md:69-73 — D-1266: one clipboard-only file, assertions unchanged; the five stay where they are"
      - "C:/Temp/av-kit/e2e-clipboard-specs/plan-deps.txt — which helpers each test uses; CLIPBOARD_CALL matches only inside the two moving tests and their helpers"
      - "C:/Temp/av-kit/e2e-clipboard-specs/plan-split-out-2.txt — the three built files and their SHA-256; plan-eslint-2.txt: tsc and ESLint pass on them"
      - "C:/Temp/av-kit/e2e-clipboard-specs/plan-split-selftest-2.txt — the selftest refuses a changed assertion, a dropped block and a CRLF new file"
    research: { engine: none, sources: [] }
    reasoning: "Handed to the agent: USER_EXPLICIT 2026-11-18 'make the decisions always the recommenations', continuing USER_EXPLICIT 2026-11-20 'continue orchestrating the next prompt session and the session after if there is any'. D-1266 chose a split by file; this brief settles its form. A moves whole test blocks and their private helpers, so every assertion keeps its bytes and only the new file calls the clipboard, which the dev-PC guard and the mini-air list can check by file name. B, a shared helper module imported by both kinds of file, edits the kept helpers in the two old files, so they no longer equal b59207b, and touches more lines than the move needs. C, keep the files and filter the two tests by title, leaves clipboard calls in files that run on the dev PC and makes every runner depend on a title filter. D, doing nothing, leaves five tests in no gate. No assertion changes (M-7: none). Undo: restore the two files from b59207b and delete the new one. Two-way."
  - id: D-1269
    stage: planning
    question: "When do the two clipboard tests run on the mini-air?"
    resolution: autonomous
    class: two-way
    mandatory: none
    chosen: "A: in a second stage of run-e2e.ps1, after the main specs. The stage runs only when the session probe before it reads none, and a second probe runs right after it. A connected or undecided probe before skips the stage with the probe's reason; a connected or undecided probe after, or a poll during the stage, voids its result."
    source_tag: Local Canon
    precedents:
      - ".agent/context/grouping/2026-11-20-e2e-clipboard-specs-session-grouping.md:126 — D-1267: on the mini-air only, with a probe before and after"
      - ".agent/context/grouping/2026-11-20-e2e-clipboard-specs-session-grouping.md:76-80 — each probe outcome proved by a fake host; a session during the run voids the result"
      - "C:/Temp/av-kit/dispatch/s98-planner-brief.md:46 — a separate stage or a second invocation, so the probe runs right before and right after the file"
      - "tools/e2e_host/run-e2e.ps1:109-120 — one spec list, one Start-Process, pid.txt, then DONE"
    research: { engine: none, sources: [] }
    reasoning: "Handed to the agent: USER_EXPLICIT 2026-11-18 'make the decisions always the recommenations', continuing USER_EXPLICIT 2026-11-20 'continue orchestrating the next prompt session and the session after if there is any'. A puts the probes right before and right after the clipboard file, as D-1267 asks, and keeps the main stage's 237 tests independent of any session: Mat connecting never costs the main run. B, a second scheduled-task run started by the tool, needs a second lock window and changes Session 96's one-task-per-run contract. C, the clipboard file inside the main stage with probes at the run's start and end, would void it for a session that came and went twenty minutes away from the clipboard tests, and cannot say which. D, doing nothing, keeps the file skipped and the issue open. Undo: remove the stage block and the gated list. Two-way."
  - id: D-1270
    stage: planning
    question: "What does the probe read, and which readings count as connected, undecided or none?"
    resolution: autonomous
    class: two-way
    mandatory: none
    chosen: "A: three reads only: Win32_Process for the RustDesk processes (command line, session id, parent), the rdpclip.exe process, and qwinsta's session table. The rule order: a failed read is undecided-probe-failed; a --cm or --cm-no-ui process is connected-rustdesk-cm; rdpclip.exe or an Active rdp-tcp#n row is connected-rdp; an unreadable RustDesk command line other than the session-0 service and its direct child is undecided-unreadable; a readable switch that is not exactly --service, --server or --tray is undecided-rustdesk-other; otherwise none, no-remote-session."
    source_tag: Local Canon
    precedents:
      - "C:/Temp/av-kit/e2e-clipboard-specs/rustdesk-src/src_server_connection.rs:4709, :4729, :4763, :4754 — start_ipc spawns the connection manager with --cm through run_as_user for each incoming connection; --cm-no-ui is the headless form"
      - "C:/Temp/av-kit/e2e-clipboard-specs/rustdesk-src/src_core_main.rs:347, :360, :364, :629 — --tray, --service, --server; --cm is the connection manager"
      - "C:/Temp/av-kit/e2e-clipboard-specs/plan-session-probe-miniair-1.txt — the idle mini-air: service, server and tray readable, no --cm, the console Active, no RDP; reads none"
      - "C:/Temp/av-kit/e2e-clipboard-specs/plan-session-probe-devpc.txt — unelevated: the service and its child unreadable and exempt, a switchless main window reads undecided-rustdesk-other"
      - "C:/Temp/av-kit/dispatch/s98-planner-brief.md:44 — read only process and connection state; no file under the host's user folders"
    research: { engine: none, sources: [] }
    reasoning: "Handed to the agent: USER_EXPLICIT 2026-11-18 'make the decisions always the recommenations', continuing USER_EXPLICIT 2026-11-20 'continue orchestrating the next prompt session and the session after if there is any'. RustDesk starts the connection manager, a separate --cm process, for each incoming connection, and that process holds the session's clipboard sync, so its presence is the direct signal; rdpclip and an Active rdp-tcp row are the RDP equivalents. Every reading the rule does not recognise is undecided, and undecided skips the stage, so the probe fails closed: a newer RustDesk with a new switch skips, never runs. B, the RustDesk processes' established TCP connections, also counts the rendezvous and relay keep-alives that exist with nobody connected; telling them apart needs RustDesk's server settings, which live in its config, a file the brief forbids reading. C, Windows session state alone, misses RustDesk: it attaches to the console session, which reads Active whether or not anyone is connected. D, doing nothing, gives no probe, and the split ships alone. The connected case was not seen at plan time because Mat was not connected; it rests on RustDesk's source and the fake-host tests, and row 7a falls back when the host cannot be read (D-1274). Undo: change the classify function in the one block. Two-way."
  - id: D-1271
    stage: planning
    question: "Where does the probe live, and how do the launcher, the host status and the tool carry it?"
    resolution: autonomous
    class: two-way
    mandatory: none
    chosen: "A: one block between '# begin session-probe' and '# end session-probe', byte-identical in host-facts.ps1, host-status.ps1 and run-e2e.ps1, defining three functions. run-e2e.ps1 keeps its one Start-Process inside AvStage, writes stage.txt, probe-before.json and probe-after.json, and runs the gated file in its own gated folder under the run's results with its own pid.txt. host-status.ps1 reports the stage and the gated pid. check prints one session-probe line, and each poll records the probe."
    source_tag: Local Canon
    precedents:
      - "tests/tooling/test_e2e_remote.py:46 — BUSY_COPIES; :1795 holds the busy-check block identical in each copy"
      - "tests/tooling/test_e2e_remote.py:1803 — exactly one Start-Process, -PassThru, no -Wait, then .Handle and pid.txt"
      - "tools/e2e_remote.py:574 — fact_lines prints check's facts; :941 — _poll writes one record per poll"
      - "tools/e2e_host/host-status.ps1 — pid_file from the run's pid.txt feeds the tool's run tree"
    research: { engine: none, sources: [] }
    reasoning: "Handed to the agent: USER_EXPLICIT 2026-11-18 'make the decisions always the recommenations', continuing USER_EXPLICIT 2026-11-20 'continue orchestrating the next prompt session and the session after if there is any'. Session 96 already keeps the busy check as one block copied into several scripts, with a test holding the copies identical; A reuses that, so check, the polls and the launcher read the same classifier. The gated stage gets its own folder and pid, so the main report is never overwritten and the run tree sees the run's processes in either stage; the one Start-Process line keeps its switches, so test_ac_14_host_static_launcher passes unchanged. B, a fourth script dot-sourced by the three, adds a file to the copied set and a load-order failure to each script. C, a probe run from the dev PC over ssh between the stages, cannot work: the launcher runs inside one scheduled task with no callback. D, doing nothing, gives no probe. Undo: remove the block from the three scripts. Two-way."
  - id: D-1272
    stage: planning
    question: "How do the known list and the tool's summary carry the gated file and its outcome?"
    resolution: autonomous
    class: two-way
    mandatory: none
    chosen: "A: known-failures.json drops its two skip entries and gains a gated list of {label, file, reason} naming only the new file for the mini-air. load_known and label_gated check it, and _run refuses a malformed entry or a file in both lists with 32. The summary gains a gated object {files, outcome, reason, before, after, new}, with the outcome one of run, skipped-connected, skipped-undecided, voided-connected-during and voided-undecided-during. A gated failure under run exits 40, as any new failure does, and a missing probe-before.json is 31. The main stage's counts and new list keep their meaning."
    source_tag: Local Canon
    precedents:
      - ".agent/context/grouping/2026-11-20-e2e-clipboard-specs-session-grouping.md:71 — the mini-air skip entries name only the clipboard-only file"
      - "tools/e2e_remote.py:51 — REASONS: 31 report-missing, 32 known-failures-stale, 40 new-failures"
      - "tools/e2e_remote.py:391, :406, :1045, :1115 — load_known, label_skip, the expected specs minus skip, and _run's refusals"
      - "tests/tooling/test_e2e_remote.py:1561-1572 — the pin on the list's entries"
    research: { engine: none, sources: [] }
    reasoning: "Handed to the agent: USER_EXPLICIT 2026-11-18 'make the decisions always the recommenations', continuing USER_EXPLICIT 2026-11-20 'continue orchestrating the next prompt session and the session after if there is any'. The grouping asks that skip entries name only the clipboard-only file; under A skip is empty and gated names only that file, so the rule is met. M-4 is checked and not hit: no reason, exit code, API or MCP tool is added or renumbered. A keeps the main stage's 237 and its new list as Session 96 defined them, so a gated skip or void never reads as a main failure, and a real gated failure still exits 40. B, keep the file in skip and let the launcher run skipped files when the probe allows, overloads skip: a reader cannot tell a file that never runs from one that runs gated. C, fold the gated result into the main counts, makes the main totals depend on whether Mat was connected. D, doing nothing, keeps the file skipped. Undo: remove the gated list and object. Two-way."
  - id: D-1273
    stage: planning
    question: "How does the plan read the mini-air's process state, when the brief says to copy a probe script into a folder under the configured root?"
    resolution: autonomous
    class: source-conflict
    mandatory: [M-6]
    chosen: "A: one read-only PowerShell command, the planned probe body, sent through the pinned alias with BatchMode and StrictHostKeyChecking as -EncodedCommand. It wrote nothing on the host and read only process and session state; its output is plan-session-probe-miniair-1.txt."
    source_tag: Local Canon
    precedents:
      - "C:/Temp/av-kit/dispatch/s98-planner-brief.md:45 — copy a probe script into a folder you own under the configured root and run it through the pinned alias"
      - "C:/Temp/av-kit/e2e-clipboard-specs/plan-session-probe.ps1 — the command that was encoded; no write, no Stop, no Set"
      - "C:/Temp/av-kit/e2e-clipboard-specs/plan-session-probe-miniair-1.txt — 2026-11-20T18:09:36Z, elevated, 170 processes, every RustDesk command line readable"
    research: { engine: none, sources: [] }
    reasoning: "Handed to the agent: USER_EXPLICIT 2026-11-18 'make the decisions always the recommenations', continuing USER_EXPLICIT 2026-11-20 'continue orchestrating the next prompt session and the session after if there is any'. The brief's copied-script wording keeps the probe read-only and inside a folder this session owns. A meets that purpose more strictly: nothing was written on the host, so there is no folder to own and nothing to clean up. B, copy the script into a session folder and run it, writes a file the session must then leave or remove, for the same reading. C, read through tools/e2e_remote.py check, needs this plan's tool change, which does not exist at plan time. D, no plan-time read, leaves the classifier untested on the host's real process tree. Departing from the brief's wording is M-6, which the hand-over covers. Undo: none needed; nothing was written. Two-way."
  - id: D-1274
    stage: planning
    question: "The connected case could not be seen at plan time. When does the split ship alone, and what does the fallback hold?"
    resolution: autonomous
    class: source-conflict
    mandatory: [M-6]
    chosen: "A: decide the split flag at row 7a by evidence. It is fallback when probe-check.py --judge on the elevated check exits 3 (undecided-probe-failed or undecided-unreadable on the mini-air), or when a fake-host test of rows 3 to 5 cannot go green without an unnamed test change; otherwise it is probe. The fallback restores the tool and the three host scripts to their row-0 copies, removes the test_s98_ tests and NEW_NAMES, sets test_ac_11 to one skip entry for the new file, writes the fallback known list and a short Session 98 run-book section naming the trigger, and leaves UNGATED open. The flag is provisional: row 8's probe-check.py --judge-gate can flip it to fallback at row 8b (D-1280)."
    source_tag: Local Canon
    precedents:
      - ".agent/context/grouping/2026-11-20-e2e-clipboard-specs-session-grouping.md:84 — split flag: if no probe can be proven on the host, the split ships alone"
      - ".agent/context/grouping/2026-11-20-e2e-clipboard-specs-session-grouping.md:126 — D-1267: if the plan cannot prove such a probe, the file stays skipped"
      - "C:/Temp/av-kit/dispatch/s98-planner-brief.md:45, :47 — record that the connected case could not be seen; the fallback has its own ACs"
      - "C:/Temp/av-kit/e2e-clipboard-specs/plan-session-probe-miniair-1.txt — the elevated probe reads every RustDesk command line on the mini-air"
    research: { engine: none, sources: [] }
    reasoning: "Handed to the agent: USER_EXPLICIT 2026-11-18 'make the decisions always the recommenations', continuing USER_EXPLICIT 2026-11-20 'continue orchestrating the next prompt session and the session after if there is any'. Plan time proved what can be proved without Mat: the elevated probe reads every RustDesk command line on the mini-air and classifies the idle host as none, and RustDesk's source names --cm as the per-connection manager. Only a real connection can show the connected reading itself. A treats the probe as proven when the host is readable and the fake-host tests pass, and keeps the fallback ready with its own ACs. That reads the flag by its purpose, never to ship a probe that cannot read the host; deciding at row 7a rather than at plan time departs from the brief's order (M-6), which the hand-over covers. B, fallback now because the connected case was not seen, ships no probe although every readable part is proven, and leaves the clipboard tests with no host. C, ask Mat to connect during planning, is a human action (M-10) that the brief does not require. D, doing nothing, leaves the flag undecided at execution. Undo: the coordinator can force the fallback before execution. Two-way."
  - id: D-1275
    stage: planning
    question: "test_ac_11_known_tracked_list pins the two skip entries this session removes. What may change in tests/tooling/test_e2e_remote.py?"
    resolution: autonomous
    class: two-way
    mandatory: none
    chosen: "A: only the module docstring (:1-11, named added text) and test_ac_11_known_tracked_list (:1561-1572): known [], skip [], gated the new file with its reason, KNOWN_FILE unchanged; under the fallback, skip names the new file only. Every new statement is a test_s98_ or _s98_ function or a NEW_NAMES assignment. pins-check.py refuses any other change to a row-0 statement, an added import, an unprefixed function and a line-ending flip."
    source_tag: Local Canon
    precedents:
      - ".agent/context/grouping/2026-11-20-e2e-clipboard-specs-session-grouping.md:71 — test_ac_11_known_tracked_list changes in a plan row that names it"
      - ".agent/docs/human-decision-protocol.md:158 — M-7 is a hit only when no approved plan row names the test and the new assertion"
      - "tests/tooling/test_e2e_remote.py:1561-1572 — known == [], the two skip tuples at :1567-1568, every reason present, KNOWN_FILE"
      - "C:/Temp/av-kit/e2e-clipboard-specs/plan-selftest-pins-check.txt — 13 cases"
      - "docs/execution/plans/2026-11-19-e2e-host-parity/implementation-plan.md — D-1255: named pins with old and new values"
    research: { engine: none, sources: [] }
    reasoning: "Handed to the agent: USER_EXPLICIT 2026-11-18 'make the decisions always the recommenations', continuing USER_EXPLICIT 2026-11-20 'continue orchestrating the next prompt session and the session after if there is any'. The grouping names this pin and asks that a row name its change; row 3 names the test and its new assertion, so the change is not an M-7 hit (HDP :158), and the M-7 check is named here. An M-7 hit would fall outside the hand-over (HDP :329), so pins-check.py turns any other change to an existing statement into a row stop (S3). B, keep the test and the skip entries, contradicts D-1266. C, delete the test and write a new one, removes a test and its KNOWN_FILE assertion. D, doing nothing, leaves the test failing after row 6. Undo: restore the test's row-0 lines. Two-way."
  - id: D-1276
    stage: planning
    question: "How does the dev-PC full run include the five tests and never the clipboard file?"
    resolution: autonomous
    class: two-way
    mandatory: none
    chosen: "A: the plan-local flake-run.py from Session 91, with EXCLUDED holding only capture-system-clipboard.test.ts and an OLD_CLIPBOARD guard that exits 2 before any run while either old file matches CLIPBOARD_CALL; the full run expects 237 tests in 29 files."
    source_tag: Local Canon
    precedents:
      - "docs/execution/plans/2026-11-20-e2e-clipboard-specs/flake-run.py:161, :164 — EXCLUDED and OLD_CLIPBOARD"
      - "C:/Temp/av-kit/e2e-clipboard-specs/plan-flake-guard-head.txt — at HEAD the guard refuses: both old files call the clipboard"
      - ".agent/context/grouping/2026-11-20-e2e-clipboard-specs-session-grouping.md:46 — Session 57 RULE-4: Mat uses that clipboard"
      - "C:/Temp/av-kit/dispatch/s98-planner-brief.md:63 — before the split, a dev-PC run of either old file is forbidden"
    research: { engine: none, sources: [] }
    reasoning: "Handed to the agent: USER_EXPLICIT 2026-11-18 'make the decisions always the recommenations', continuing USER_EXPLICIT 2026-11-20 'continue orchestrating the next prompt session and the session after if there is any'. Session 57 RULE-4 keeps clipboard tests off Mat's desktop. A keeps Session 91's exclusion by file name and adds a guard that reads the files instead of trusting the row order, so a missed split cannot start a clipboard test. 237 is HEAD's 239 minus the two moved tests. B, a title filter for the two tests, depends on Playwright's grep and has no guard if a title changes. C, keep excluding the old files, never proves the five on the dev PC, which the grouping's acceptance asks. D, doing nothing, keeps the five out of every gate. Undo: restore EXCLUDED's two names. Two-way."
  - id: D-1277
    stage: planning
    question: "Two other specs in every dev-PC full run, C1-5 and AC-71.15, also write the main-process clipboard. What does this session do about them?"
    resolution: autonomous
    class: two-way
    mandatory: [M-8]
    chosen: "A: record them as a new issue, E2E-DEVPC-CLIPBOARD-SPECS (low, ui, TECH-DEBT), through the issue_triage model's add_issue at row 9 (the CLI has no category flag), with both file and line references and Session 57 RULE-4; neither spec changes."
    source_tag: Local Canon
    precedents:
      - "ui/tests/e2e/console-chrome.test.ts:77 — C1-5 reads and writes the clipboard"
      - "ui/tests/e2e/mcp-setup-prompt.test.ts:91 — AC-71.15 reads the clipboard after Copy prompt"
      - ".agent/context/grouping/2026-11-20-e2e-clipboard-specs-session-grouping.md:46 — Session 57 RULE-4"
      - "C:/Temp/av-kit/e2e-clipboard-specs/plan-issues.txt — the id is free"
    research: { engine: none, sources: [] }
    reasoning: "Handed to the agent: USER_EXPLICIT 2026-11-18 'make the decisions always the recommenations', continuing USER_EXPLICIT 2026-11-20 'continue orchestrating the next prompt session and the session after if there is any'. Both specs write the clipboard in every dev-PC full run, this session's gate included, so Session 57 RULE-4 is not met today by tests this grouping did not size. A makes the finding durable for the next triage without widening the code scope. B, move both into a gated file now, edits specs outside the grouping's scope. C, exclude them from this session's dev-PC runs, drops tests from the gate (M-11) with no plan for them. D, doing nothing, leaves the finding in this plan only; it stays a real option, since no ruling demands the issue. A register entry beyond the grouping's two issues is a scope change (M-8), which the hand-over covers. Undo: remove the entry through issue_triage.py. Two-way."
  - id: D-1278
    stage: planning
    question: "What happens to the two issues after the mini-air run?"
    resolution: autonomous
    class: two-way
    mandatory: none
    chosen: "A: under the probe, E2E-CLIPBOARD-SPECS-UNGATED is resolved through issue-resolve.py when row 8's probe-check.py --judge-gate prints ungated: resolve (D-1280), with verification naming the row-8 run id, the main counts and the gated outcome; otherwise, and under the fallback, it stays open with that verification, citing ecs-judge-gate-8.txt and the reason, ecs-flip-8b.txt after a flip, or the trigger. E2E-CLIPBOARD-PRIMER-EMPTY stays open either way, with its verification updated by the gated outcome, and gets the run's receipts if AC-88.12's primer failed."
    source_tag: Local Canon
    precedents:
      - ".agent/context/known-issues.yaml:6037 — E2E-CLIPBOARD-SPECS-UNGATED, D-1261"
      - ".agent/context/known-issues.yaml:3628 — E2E-CLIPBOARD-PRIMER-EMPTY: close only after AC-88.12 has passed in repeated gated runs"
      - ".agent/context/grouping/2026-11-20-e2e-clipboard-specs-session-grouping.md:80 — if AC-88.12 runs and its primer fails, the issue's own rule applies"
    research: { engine: none, sources: [] }
    reasoning: "Handed to the agent: USER_EXPLICIT 2026-11-18 'make the decisions always the recommenations', continuing USER_EXPLICIT 2026-11-20 'continue orchestrating the next prompt session and the session after if there is any'. UNGATED's defect is that the five tests are excluded and the clipboard tests have no host. Under the probe, the change fixes both, and a skipped gated outcome on the acceptance run is the gate working, not the defect. PRIMER-EMPTY's own rule asks for repeated gated passes, which one run cannot give. B, resolve UNGATED only if the outcome is run, ties the issue's state to whether Mat was connected that hour. D-1280 takes the part of B that matters: a skipped-undecided or voided-undecided-during, which a reader the session never measured can produce, keeps UNGATED open. C, close PRIMER-EMPTY on one pass, breaks its rule. D, doing nothing, leaves both open with stale verification. Undo: reopen through issue_triage.py. Two-way."
  - id: D-1279
    stage: planning
    question: "The mini-air run needs a commit at the final tree, and this session may not commit. How does it run, and what is its pass rule?"
    resolution: autonomous
    class: source-conflict
    mandatory: [M-6]
    chosen: "A: snapshot-commit.py, copied from Session 97, builds a commit object on no ref from HEAD plus the scope files with a temporary GIT_INDEX_FILE and the noreply identity. It refuses unless the index, every ref, HEAD's target and the status are byte-equal before and after. One tools/e2e_remote.py run takes that commit. AC-14's main counts are the pass rule; the gated outcome and its reason are a receipt."
    source_tag: Local Canon
    precedents:
      - "docs/execution/plans/2026-11-19-e2e-host-parity/implementation-plan.md — D-1247: the same snapshot, its guards and its selftest"
      - "C:/Temp/av-kit/e2e-clipboard-specs/plan-selftest-snapshot.txt — the guards hold on a repository copy; each negative case refuses"
      - "AGENTS.md:98-100 — never auto-commit or push; main only"
      - "C:/Temp/av-kit/dispatch/s98-planner-brief.md:52 — either outcome is a receipt, not a retry until green"
    research: { engine: none, sources: [] }
    reasoning: "Handed to the agent: USER_EXPLICIT 2026-11-18 'make the decisions always the recommenations', continuing USER_EXPLICIT 2026-11-20 'continue orchestrating the next prompt session and the session after if there is any'. The run must test the final files, and the tool archives a commit. A gives it one without staging, moving a branch or touching the index; the object is reachable from no ref, so no push can carry it, and git prunes it later. The rule against committing protects Mat's branch and index, and A leaves both byte-equal and proves it, so it keeps the rule's purpose while departing from its letter (M-6), which the hand-over covers. Making the gated outcome a pass rule would require Mat to stay disconnected and would retry until it ran, which the brief rules out. B, run at HEAD, tests the old files. C, wait for the coordinator's commit, puts the run after the issues are resolved. D, doing nothing, fails the grouping's acceptance. Undo: none needed; the object is unreferenced. Two-way."
  - id: D-1280
    stage: planning
    question: "Row 7a judges the split flag from the elevated check in session 0, but the probe that gates the clipboard stage runs in the scheduled task at run level Limited in the desktop session. Which reading decides the flag and the outcome of E2E-CLIPBOARD-SPECS-UNGATED?"
    resolution: autonomous
    class: two-way
    mandatory: none
    chosen: "A: row 7a's judge stays, as a provisional flag. Row 8 runs probe-check.py --judge-gate on the run's summary.json, which reads the launcher's own gated.probe_before and gated.probe_after. Exit 3 (either probe reads undecided-probe-failed or undecided-unreadable) sends the session to row 8b: it copies the flag to ecs-split-flag-7a.txt, writes fallback with the trigger limited-unreadable, reverts exactly as row 7a's fallback does, and reruns the mini-air run once in that form. Exit 1 is S11. E2E-CLIPBOARD-SPECS-UNGATED is resolved only when the judge prints ungated: resolve (outcome run, skipped-connected or voided-connected-during); skipped-undecided and voided-undecided-during keep it open, with the verification citing ecs-judge-gate-8.txt and the reason, as a finding."
    source_tag: Local Canon
    precedents:
      - "C:/Temp/av-kit/e2e-clipboard-specs/ecs98-expert-pass.txt — H1: the reader that sets the split flag is not the reader that gates the run"
      - ".agent/docs/e2e-remote-host.md:53 — the task runs Interactive, at run level Limited, in the signed-in account's desktop session"
      - "docs/execution/plans/2026-11-20-e2e-clipboard-specs/probe-check.py — --judge-gate: exit 3 on a fallback reason, ungated: resolve or ungated: open on exit 0, exit 1 when malformed; 28 selftest cases (plan-selftest-probe-check-2.txt)"
    research: { engine: none, sources: [] }
    reasoning: "Handed to the agent: USER_EXPLICIT 2026-11-18 'make the decisions always the recommenations', continuing USER_EXPLICIT 2026-11-20 'continue orchestrating the next prompt session and the session after if there is any'. H1 holds: check reads the mini-air over ssh, elevated, where every command line is readable, so undecided-unreadable cannot fire there and the row-7a judge is close to certain to say probe. The probe that decides whether the clipboard tests run reads with the task's Limited token, a view nobody has observed. A keeps row 7a as the cheap early judge, lets the deciding reader overturn it once into the fallback form D-1274 already defines, and stops counting a skip the deciding reader could not explain as the gate working. It amends D-1278. B, a plan-time Limited probe of the mini-air, needs a host write or a task run, which this plan may not do. C, keep D-1278's whatever-the-outcome rule, could mark the issue resolved while no host runs the two tests. D, doing nothing, ships a probe whose deciding reader was never judged. Undo: the flag is a scratch file, and the issue reopens through issue_triage.py. Two-way."
  - id: D-1281
    stage: planning
    question: "A RustDesk --cm process can outlive the connection it served, so connected-rustdesk-cm may stick and skip every later gated stage. What does the plan do about it?"
    resolution: autonomous
    class: two-way
    mandatory: none
    chosen: "A: each proc the probe returns carries started, its CreationDate as UTC, and the summary's gated object gains detail: one line per RustDesk or rdpclip.exe proc of the before and after probes, 'NAME SWITCHES session=N started=UTC age_s=SECONDS', so a skip behind an old --cm is visible in summary.json and in row 9's verification. The risk is named in the plan's known risk, in the run book's gated section and Known risks, and in one line of the new issue's notes. No row asks Mat to connect and disconnect; a stale skip is a finding for a later session, not a retry."
    source_tag: Local Canon
    precedents:
      - "C:/Temp/av-kit/e2e-clipboard-specs/ecs98-expert-pass.txt — M1: a --cm process can outlive the connection"
      - "C:/Temp/av-kit/e2e-clipboard-specs/rustdesk-src/server_model.dart:717-741 — a closed client stays in _clients marked disconnected; :164-168 the window closes only when _clients is empty"
      - "C:/Temp/av-kit/e2e-clipboard-specs/rustdesk-src/src_server_connection.rs:4709 — start_ipc reuses an existing cm endpoint"
    research: { engine: none, sources: [] }
    reasoning: "Handed to the agent: USER_EXPLICIT 2026-11-18 'make the decisions always the recommenations', continuing USER_EXPLICIT 2026-11-20 'continue orchestrating the next prompt session and the session after if there is any'. M1 holds by RustDesk's own source: the cm keeps a disconnected client's tab until someone closes it, and with allow-hide-cm nobody sees it, so rule 2 can read connected long after the connection ended. That fails closed: the stage skips and never runs the clipboard tests under a live session, but it can starve the stage. A makes the cause visible in every summary for one field, and the plan stays read-only on the host. B, ask Mat to connect and disconnect once and record the probe before, during and after, would prove the cm lifetime, but it is a human action (M-10, checked) that the hand-over does not ask for. C, treat a --cm older than a threshold as no session, fails open: a long live connection would run the tests under it. D, doing nothing, leaves a stale skip unexplained. Undo: drop the field and the lines. Two-way."
  - id: D-1282
    stage: planning
    question: "The dev-PC guard on the clipboard file is plan-local. After the split, the canonical npm run test:e2e and the flake-run.py copies in earlier plan folders would run the new file on the dev PC. How is it kept off the dev PC in tracked code?"
    resolution: autonomous
    class: two-way
    mandatory: [M-8]
    chosen: "A: split-specs.py writes a file-level guard after the new file's imports, a comment naming D-1282 and test.skip(process.env.AVKIT_E2E_CLIPBOARD_GATED !== '1', GUARD_REASON), and run-e2e.ps1's AvStage -Gated sets AVKIT_E2E_CLIPBOARD_GATED=1 for the gated stage only. guard-check.py proves from Playwright's own --list, which runs no test, that the two tests are listed skipped with that reason: it exits 1 at row 0, and 0 at row 2 and in the gate's guard-list step. test_s98_ac_20_clipboard_file_guard pins the launcher side and the guard line, .agent/docs/commands.md gains two lines naming the guard (row 6, CRLF kept), and AC-20 tracks it."
    source_tag: Local Canon
    precedents:
      - "C:/Temp/av-kit/e2e-clipboard-specs/ecs98-expert-pass.txt — M2: the dev-PC guard is plan-local"
      - ".agent/docs/commands.md:67 — the canonical ui-electron command; :205 the ui test:e2e row"
      - "docs/execution/plans/2026-11-20-e2e-clipboard-specs/guard-check.py — --list, --judge and an 8-case selftest (plan-selftest-guard-check.txt)"
      - "C:/Temp/av-kit/e2e-clipboard-specs/plan-guard-judge-unset.txt — a scratch list of the built files: 239 listed, the two skipped; plan-guard-judge-set.txt with the variable set: 4 problems"
    research: { engine: none, sources: [] }
    reasoning: "Handed to the agent: USER_EXPLICIT 2026-11-18 'make the decisions always the recommenations', continuing USER_EXPLICIT 2026-11-20 'continue orchestrating the next prompt session and the session after if there is any'. M2 holds: after the split the new file's name is in no exclusion list, so the canonical command and a flake-run.py copied from an earlier plan would run it on the dev PC, which Session 57 RULE-4 forbids. A puts the guard in the file itself, so every runner that does not set the variable skips it, and the one place that must run it sets it by name. The guard is one statement outside every test body and moved block, so no assertion changes (M-7 checked), and it skips the file only where it must never run (M-11 checked). The guard line and the commands.md lines go beyond the grouping's byte-for-byte split and its file list, a scope change (M-8) that the hand-over covers. B, a testIgnore in playwright.config.ts unless the variable is set, changes a shared config and hides the file from --list, so no check could see the guard work. C, only the commands.md lines, leaves every runner able to run the file. D, doing nothing, ships the gap the split opens. Undo: remove the guard lines, the -Gated switch and the two doc lines. Two-way."
  - id: D-1283
    stage: planning
    question: "The expert pass's other items: a void cannot undo a clipboard write, the probe sees RustDesk and RDP only, a void hides real gated failures, AvStage's return value can be polluted, and the full Vitest and the ruff steps first run after the snapshot. What does the plan take?"
    resolution: autonomous
    class: two-way
    mandatory: none
    chosen: "A: the void is worded honestly in the User Review, the run book and the plan's known risk: voiding discards the result and cannot undo what the tests already wrote to the host clipboard, and AC-88.12 leaves an image there (M3). The run book's Known risks names the RustDesk and RDP-only scope, an rdpclip.exe in a disconnected RDP session reading connected-rdp until logoff, and the English qwinsta state words (L1). gated.voided_failures lists a voided report's failures, outside new and the exit code (L2). AvStage pipes every internal call to $null, and test_s98_ac_7_launcher_main_exit asserts the exact DONE value and the launcher's exit when the main stage exits non-zero (L3). Row 7b runs the full Vitest and the gate's ruff format --check and ruff check argv before the dev-PC full run and the snapshot (L4)."
    source_tag: Local Canon
    precedents:
      - "C:/Temp/av-kit/e2e-clipboard-specs/ecs98-expert-pass.txt — M3, L1, L2, L3 and L4"
      - "ui/tests/e2e/capture-filmstrip-actions.test.ts:242-267 — AC-88.12 (a)(b)(f) primes an image and does not restore the clipboard"
      - "docs/execution/plans/2026-11-20-e2e-clipboard-specs/session-gate.ps1 — the py-format and py-lint argv that row 7b mirrors"
    research: { engine: none, sources: [] }
    reasoning: "Handed to the agent: USER_EXPLICIT 2026-11-18 'make the decisions always the recommenations', continuing USER_EXPLICIT 2026-11-20 'continue orchestrating the next prompt session and the session after if there is any'. Each item is cheap and makes a statement true or a failure visible earlier, and none changes a test body or a host setting. The gated object gains a field that only this session's checks read (M-4 checked). B, restore the clipboard after AC-88.12, changes a moved test's body, which the split's byte rule and M-7 forbid. C, read the RDP session state by number through the WTS API, changes the probe's classifier with no non-English host to prove it. D, doing nothing, leaves the User Review implying that a void protects the clipboard, voided failures untraced, and a late Vitest or ruff failure able to force a second 40-minute host run. Undo: drop the field, the test and the lines. Two-way."
  - id: D-1284
    stage: execution
    question: "The execution review round 1 (ECS-R1-1, High, AC-7) found that when the before probe reads none and probe-after.json is missing, empty or has no probe state, gated_outcome returns run with the reason no-remote-session and exit 0, and the launcher copy still reaches DONE 0 when it cannot write the after probe. How does the gated stage treat a missing or invalid after probe?"
    resolution: autonomous
    class: two-way
    mandatory: none
    chosen: "A: fail closed with the existing outcome voided-undecided-during. gated_outcome reads a missing after probe as undecided with the reason after-probe-missing, and one with no valid probe state (empty, unreadable or an unknown state) as undecided with after-probe-invalid; a connected reading from a gated poll still wins, an earlier undecided poll keeps its reason, and no sixth outcome or new refusal is added; the main stage's summary is unchanged. AvProbeWrite in run-e2e.ps1 writes with Set-Content -ErrorAction Stop inside try/catch, logs probe-write-failed and the file name in meta.txt on failure, and continues to DONE as before; the session-probe block is unchanged in all three scripts. The run book names both reasons under voided-undecided-during. Four new test_s98_r1fix tests are the Red (ecs-red-r1fix.txt) with the test file hash in ecs-test-sha-r1fix.json; S13 renames row 8's receipts with -r1 and reruns row 8 once on the final files (run r20261120T230628Z-ef4842e on snapshot ef4842e; r1 was r20261120T215925Z-9ac9adc, same outcome). Two follow-ups under the same ruling: the gate's test-hashes step (docs/execution/plans/2026-11-20-e2e-clipboard-specs/session-gate.ps1:161-164 and :170) reads ecs-test-sha-r1fix.json when it exists and ecs-test-sha-3.json otherwise (sha256 1c59822b to 6d997732; the fifth plan-local script change after approval; ecs-test-sha-3.json untouched); and issue-resolve.py replaces only the verification of E2E-CLIPBOARD-SPECS-UNGATED (stays resolved) and E2E-CLIPBOARD-PRIMER-EMPTY (stays open) to cite the rerun and name r1 as superseded under S13."
    source_tag: Local Canon
    precedents:
      - "C:/Temp/av-kit/ecs-exec-review-round-1.md — ECS-R1-1: a missing or empty after probe gives outcome run, no-remote-session, exit 0"
      - "C:/Temp/av-kit/e2e-clipboard-specs/ecs-red-check-r1fix.txt — red-check: 1 receipt(s), 3 required test(s), 0 problem(s); ecs-red-r1fix.txt: 6 failed, by assertion"
      - "C:/Temp/av-kit/e2e-clipboard-specs/ecs-green-r1fix.txt — 211 passed"
      - "C:/Temp/av-kit/e2e-clipboard-specs/ecs-probe-block-r1fix.txt — probe-check: 3 copies, 0 problem(s)"
      - "C:/Temp/av-kit/e2e-clipboard-specs/ecs-pins-r1fix.txt — pins-check: 0 problem(s); new test_s98_ and _s98_ only"
      - "C:/Temp/av-kit/e2e-clipboard-specs/ecs-test-hashes-r1fix-proof.txt — ecs-test-sha-3.json equal: False, ecs-test-sha-r1fix.json equal: True"
      - "C:/Temp/av-kit/e2e-clipboard-specs/ecs-test-hashes-fix-r1fix.txt — session-gate.ps1 sha256 before and after; the kept copy session-gate.ps1.pre-r1fix; the diff in ecs-test-hashes-diff-r1fix.txt"
      - "C:/Temp/av-kit/e2e-clipboard-specs/ecs-run-8-check.txt — run folder r20261120T230628Z-ef4842e, tests 237 expected 237, gated outcome run; ecs-judge-gate-8.txt: ungated: resolve"
      - "C:/Temp/av-kit/e2e-clipboard-specs/ecs-issue-resolve-r1fix.txt — parsed fields changed: 4, verification only; ecs-register-check-r1fix.txt: other issues changed: []"
    research: { engine: none, sources: [] }
    reasoning: "Handed to the agent: USER_EXPLICIT 2026-11-18 'make the decisions always the recommenations', continuing USER_EXPLICIT 2026-11-20 'continue orchestrating the next prompt session and the session after if there is any'. The coordinator ruled A on the review's finding and found no M item: no existing assertion weakens (no test asserted that a missing after probe is run) and no product code changes. A stage whose after probe cannot be read has no proof that no remote session started during it, so run would accept a result the plan says to void (D-1269, D-1283). B, a new refusal for a missing after probe, would fail the whole run for a gated-stage fault and change the exit bands. C, a sixth outcome, changes the closed outcome list every reader and test names. D, doing nothing, keeps a fail-open path in the stage that guards the clipboard tests. The gate record follows because the named test change moves the file's hash after its row-3 Red; overwriting ecs-test-sha-3.json would rewrite a Red receipt. The registers follow because the commit binds the rerun's tree and the receipt names they cite now hold the rerun. Undo: restore the three lines of gated_outcome, AvProbeWrite's write line, the run book row, line 170 and the comment of session-gate.ps1 from session-gate.ps1.pre-r1fix, and the register from known-issues.yaml.pre-r1fix."
  - id: D-1285
    stage: execution
    question: "Row 0's first run stamped its flake-run labels from baseline.ps1:41 with a capital T, which flake-run.py refuses (--label takes lower-case letters, digits and hyphens), so list-0 failed and flake-guard-before passed only on that argument refusal (exit 2). How is row 0 run?"
    resolution: autonomous
    class: two-way
    mandatory: none
    chosen: "A: change baseline.ps1:41 alone to the stamp yyyyMMdd-HHmmss (sha256 34fd2fc0 to 58efb180), keep the first run's receipts and run row 0 again in full; disclosed in the handoff as the second plan-local script change after approval, naming the vacuous flake-guard-before pass of the first run."
    source_tag: Local Canon
    precedents:
      - "C:/Temp/av-kit/e2e-clipboard-specs/ecs-baseline-0-run1.txt — the first run: flake-run.py: error: --label takes lower-case letters, digits and hyphens; flake-guard-before exit=0 (the tool exited 2; 2 expected)"
      - "C:/Temp/av-kit/e2e-clipboard-specs/ecs-baseline-fix-hashes.txt — line 41 only, old and new sha256"
      - "C:/Temp/av-kit/e2e-clipboard-specs/ecs-guard-red-1.txt — row 1's real refusal: flake-run: refused before any run: capture-filmstrip-actions.test.ts still calls the system clipboard (Session 57 RULE-4)"
    research: { engine: none, sources: [] }
    reasoning: "Handed to the agent: USER_EXPLICIT 2026-11-18 'make the decisions always the recommenations', continuing USER_EXPLICIT 2026-11-20 'continue orchestrating the next prompt session and the session after if there is any'. The coordinator ruled A on the HDP recommendation. The label check is the runner's own input rule, and the stamp is the only wrong byte; the guard's real refusal is proved at row 1. No test, gate step or tracked file changes (M-7 and M-11 checked, not hit). B, loosening the label rule in flake-run.py, changes a runner every row uses. D, doing nothing, leaves row 0 unable to pass. Undo: restore line 41."
  - id: D-1286
    stage: execution
    question: "Row 2's first write refused: capture-filmstrip-actions.test.ts is not its b59207b blob. With core.autocrlf true and text=auto, the working file is the LF blob in CRLF form, and cmd_write compared raw bytes. How is row 2 run?"
    resolution: autonomous
    class: two-way
    mandatory: none
    chosen: "A: replace only the comparison loop of split-specs.py cmd_write, so the filmstrip blob is compared in its CRLF checkout form and the import blob as it is (sha256 0aa62b23 to 9290df18); ruff format, ruff check and the 7-case selftest pass; row 2 runs again in full; disclosed as the third plan-local script change after approval."
    source_tag: Local Canon
    precedents:
      - "C:/Temp/av-kit/e2e-clipboard-specs/ecs-split-write-2-run1.txt — split-specs: refused: ui/tests/e2e/capture-filmstrip-actions.test.ts is not its b59207b blob"
      - "C:/Temp/av-kit/e2e-clipboard-specs/ecs-split-fix2-hashes.txt — old and new sha256, the cause"
      - "C:/Temp/av-kit/e2e-clipboard-specs/ecs-split-fix2-selftest.txt — split-specs selftest: ok (7 cases)"
      - "C:/Temp/av-kit/e2e-clipboard-specs/ecs-split-check-2.txt — split-specs check: ok (0 problem(s))"
    research: { engine: none, sources: [] }
    reasoning: "Handed to the agent: USER_EXPLICIT 2026-11-18 'make the decisions always the recommenations', continuing USER_EXPLICIT 2026-11-20 'continue orchestrating the next prompt session and the session after if there is any'. The coordinator ruled A on the HDP recommendation. Only cmd_write reads the working files before it writes; --check reads the files after the write, --out writes a fresh folder and the selftest builds from text in memory, so none of them saw the checkout form. The written bytes are unchanged, and row 2's --check proves the three plan-time hashes. No test or gate step changes (M-7 and M-11 checked, not hit). D, doing nothing, leaves row 2 unable to write. Undo: restore the loop."
  - id: D-1287
    stage: execution
    question: "Row 7b's ruff check of tools/ and tests/ exited 1 on 10 errors (I001 x7, E501 x3) in seven files this session never changed, under tools/issue_triage* and tools/meu_status*. What does the gate lint?"
    resolution: autonomous
    class: two-way
    mandatory: none
    chosen: "A: session-gate.ps1:261 and the task.md row-7b ruff check argv lint packages/, tools/e2e_remote.py, tests/ and the plan's Python: CI's scope (.github/workflows/ci.yml:53, ruff check packages/ tests/ tools/deps_report.py) plus the one changed tool. Row 7b reruns from its ruff step only; the 10 pre-existing errors are a handoff follow-up for the next triage, with no issue registered and no fix here. Disclosed as the fourth plan-local script change after approval."
    source_tag: Local Canon
    precedents:
      - "C:/Temp/av-kit/e2e-clipboard-specs/ecs-ruff-7b-run1.txt — the first ruff check, exit 1"
      - "C:/Temp/av-kit/e2e-clipboard-specs/ecs-ruff-7b-preexisting.txt — the 10 errors are in seven unchanged files; this session's Python, the plan folder and tests/: All checks passed!"
      - ".github/workflows/ci.yml:53 — CI lints packages/ tests/ tools/deps_report.py"
      - "C:/Temp/av-kit/e2e-clipboard-specs/ecs-lint-scope-fix-7b.txt — session-gate.ps1 431d6774 to 1c59822b, task.md 04d0e9d2 to 75f0ccd6; the one-line diffs in ecs-lint-scope-diff-7b.txt"
      - "C:/Temp/av-kit/e2e-clipboard-specs/ecs-row7b-evidence.txt — the ruff-only rerun: All checks passed!"
    research: { engine: none, sources: [] }
    reasoning: "Handed to the agent: USER_EXPLICIT 2026-11-18 'make the decisions always the recommenations', continuing USER_EXPLICIT 2026-11-20 'continue orchestrating the next prompt session and the session after if there is any'. The coordinator ruled A on the HDP recommendation and found no M item. CI has never linted tools/ as a whole, so A holds the gate to CI's scope plus the tool this session changes. The full E2E of row 7b passed on the same tree and H1-2 reruns everything. B, fixing the seven files, edits tools/ files no row names (a scope change). D, doing nothing, leaves a gate that cannot pass. Undo: restore line 261 of docs/execution/plans/2026-11-20-e2e-clipboard-specs/session-gate.ps1 and the row-7b argv from the kept copies session-gate.ps1.pre-lint-scope and task.md.pre-lint-scope."
open_decisions: []
```

Expert pass (fresh context): adopted. `C:/Temp/av-kit/e2e-clipboard-specs/ecs98-expert-pass.txt` (H1, M1 to M3, L1 to L4) is taken through D-1280 to D-1283; its confirmed items need no change.

### D-1268: How do the five tests rejoin every full run?

**I recommend A: move the two clipboard tests, byte for byte, into one new clipboard-only file.** The five others stay where they are, unchanged, and only the new file calls the clipboard, so the dev PC and the mini-air can tell the files apart by name. A can fail if a moved test needs a helper the plan missed; `split-specs.py --check` and `tsc` catch that at row 2. Undo: restore the two files from `b59207b`.

- B: a shared helper module. The kept files change beyond the move.
- C: filter the two tests by title. Clipboard calls stay in files that run on the dev PC.
- D: do nothing. Five tests stay in no gate.

Refs: D-1266; grouping `:69-73`; `plan-split-out-2.txt`.

### D-1269: When do the clipboard tests run on the mini-air?

**I recommend A: in a second stage after the main specs, between a probe before and a probe after.** The main run's 237 tests never depend on whether you are connected. A connected or undecided probe before skips the stage with its reason; one after, or a poll during it, voids the result. A can fail if a session comes and goes between two reads; the polls narrow that gap. Undo: remove the stage.

- B: a second task run. It changes Session 96's one-task-per-run contract.
- C: inside the main stage, probed at the run's ends. A session far from the clipboard tests would void them.
- D: do nothing. The file stays skipped.

Refs: D-1267; grouping `:76-80`; `run-e2e.ps1:109-120`.

### D-1270: What counts as a connected session?

**I recommend A: a RustDesk connection-manager process (`--cm`), or an RDP session (`rdpclip.exe`, an Active `rdp-tcp` row).** RustDesk starts `--cm` for every incoming connection, and it holds the clipboard sync. Anything unreadable or unrecognised is undecided, and undecided skips, so the probe fails closed. A can fail if RustDesk changes how it starts the manager; an unknown switch then reads undecided. The connected case was not seen at plan time, because you were not connected. Undo: change one function.

- B: RustDesk's network connections. Idle relay links look like sessions, and telling them apart needs its config, which is off limits.
- C: Windows session state alone. RustDesk uses the console session, which is always Active.
- D: do nothing. No probe; the split ships alone.

Refs: RustDesk `connection.rs:4709-4763`, `core_main.rs:629`; `plan-session-probe-miniair-1.txt`.

### D-1271: Where does the probe live?

**I recommend A: one identical block in the three host scripts, as Session 96's busy check is.** `check`, the polls and the launcher then read the same rule, and a test holds the copies equal. The gated stage has its own folder and pid, and the launcher keeps its one `Start-Process`. A can fail if a copy drifts; `test_s98_ac_6_probe_block_identical` fails then. Undo: remove the block.

- B: a fourth script loaded by the three. One more file to copy and a load-order failure.
- C: a probe from the dev PC between stages. The launcher has no callback.
- D: do nothing.

Refs: `test_e2e_remote.py:46`, `:1795`, `:1803`.

### D-1272: How does the tool report the gated file?

**I recommend A: a `gated` list in `known-failures.json` and a `gated` object in the summary, with five named outcomes.** `skip` is empty, so no skip entry names anything but the new file, as the grouping asks. A gated failure exits 40; no reason or exit code changes (M-4: none). A can fail if a reader takes a skipped outcome for a pass; the outcome names the reason. Undo: remove the list and the object.

- B: keep `skip` and run skipped files when the probe allows. A reader cannot tell never-run from gated.
- C: fold the gated result into the main counts. The totals would depend on whether you were connected.
- D: do nothing.

Refs: grouping `:71`; `e2e_remote.py:51`, `:1115`.

### D-1273: How did the plan read the mini-air?

**I recommend A, as done: one read-only command sent over the pinned alias as `-EncodedCommand`.** The brief said to copy a probe script into a folder under the configured root; A wrote nothing on the host, which keeps that rule's purpose more strictly. A can fail only if the command had written something; it has no write, stop or set. Undo: none needed. This departs from the brief's wording (M-6), which your hand-over covers.

- B: copy the script and run it. A file to leave or clean up, for the same reading.
- C: read through `check`. The tool change does not exist at plan time.
- D: do nothing. The classifier is untested on the real host.

Refs: s98 brief `:45`; `plan-session-probe-miniair-1.txt`.

### D-1274: When does the split ship alone?

**I recommend A: decide at row 7a, by evidence.** It is the fallback if the elevated probe cannot read the mini-air's RustDesk processes, or if a fake-host test cannot go green. Plan time proved the host is readable and the idle host reads `none`; only a real connection can show `connected`. The fallback keeps the tool and host scripts at their current bytes and the clipboard file skipped. A can fail if the probe misreads a real connection; undecided fails closed, and the issue's verification records each outcome. Undo: force the fallback before execution. Deciding at execution, not at planning, departs from the brief's order (M-6), which your hand-over covers.

- B: fall back now. No probe ships, although every readable part is proven.
- C: ask you to connect during planning. A human action the brief does not require.
- D: do nothing. The flag stays undecided.

Refs: grouping `:84`, `:126`; s98 brief `:45`, `:47`.

### D-1275: May the pinned list test change?

**I recommend A: only `test_ac_11_known_tracked_list` and the docstring change, and row 3 names both.** The test pins the two skip entries this session removes; naming it in a row is what the grouping asks, so this is not an M-7 hit. `pins-check.py` stops any other change to an existing statement. A can fail if a later row edits another test; the check stops the row. Undo: restore the lines.

- B: keep the old pins. That contradicts D-1266.
- C: delete and rewrite the test. A test and its `KNOWN_FILE` assertion are lost.
- D: do nothing. The test fails after row 6.

Refs: grouping `:71`; HDP `:158`; `test_e2e_remote.py:1561-1572`.

### D-1276: How does the dev PC stay clipboard-free?

**I recommend A: exclude only the new file, and refuse to start while either old file still calls the clipboard.** The guard reads the files, so a missed split cannot start a clipboard test on your desktop. 237 tests run. A can fail if a clipboard call takes a form the pattern misses; the five kept tests read none. Undo: restore the two names.

- B: a title filter. No guard if a title changes.
- C: keep excluding both old files. The five never run on the dev PC.
- D: do nothing.

Refs: grouping `:46`; `flake-run.py:161`, `:164`; `plan-flake-guard-head.txt`.

### D-1277: What about the two other dev-PC clipboard tests?

**I recommend A: record them as a new low issue, `E2E-DEVPC-CLIPBOARD-SPECS`, and change nothing else.** `C1-5` (console copy) and `AC-71.15` (Copy prompt) write your clipboard in every dev-PC full run, this session's included. A keeps the finding for the next triage. A can fail if the issue is never grouped; it is TECH-DEBT in the register. Undo: remove the entry. A register entry beyond the grouping's two issues is a scope change (M-8), which your hand-over covers.

- B: move both into a gated file now. Specs outside this grouping's scope.
- C: exclude them from this session's runs. Tests leave the gate with no plan (M-11).
- D: do nothing. The finding stays in this plan only.

Refs: `console-chrome.test.ts:77`; `mcp-setup-prompt.test.ts:91`.

### D-1278: What happens to the two issues?

**I recommend A: resolve `E2E-CLIPBOARD-SPECS-UNGATED` if the probe ships and the gating probe's judge says resolve (D-1280); keep `E2E-CLIPBOARD-PRIMER-EMPTY` open either way.** A skip for a named connection is the gate working; a skip because the gating reader could not decide is not, and keeps the issue open (D-1280). PRIMER-EMPTY's own rule wants repeated gated passes, which one run cannot give. A can fail if the gated stage never runs in later gates; PRIMER-EMPTY stays open to watch that. Undo: reopen.

- B: resolve UNGATED only if the stage ran. The issue would depend on whether you were connected that hour. D-1280 keeps the part of B that matters: an undecided skip stays open.
- C: close PRIMER-EMPTY on one pass. Its rule says repeated.
- D: do nothing. Both stay open with stale verification.

Refs: `known-issues.yaml:6037`, `:3628`.

### D-1279: How does the mini-air test the uncommitted final tree?

**I recommend A: a snapshot commit object on no branch, built with a temporary index, as in Session 97.** Your branch, index and status stay byte-equal, which the script checks before and after. The main counts are the pass rule; the clipboard outcome is a receipt. A can fail if the scope changes after the run; row 8 then runs once more. Undo: none needed. Making a commit object while the rule says not to commit departs from its letter (M-6), which your hand-over covers.

- B: run at the current commit. It tests the old files.
- C: wait for the coordinator's commit. The run comes after the issues are resolved.
- D: do nothing. The grouping's acceptance fails.

Refs: D-1247; s98 brief `:52`.

### D-1280: Which probe reading decides the flag and the issue?

**I recommend A: keep row 7a's judge as a provisional flag, judge the launcher's own probes at row 8, and resolve `E2E-CLIPBOARD-SPECS-UNGATED` only on a named outcome.** Row 7a reads the mini-air elevated, from session 0. The probe that decides whether the clipboard tests run sits in the scheduled task, at run level Limited in your desktop session (`.agent/docs/e2e-remote-host.md:53`), a view nobody has observed. `probe-check.py --judge-gate` reads that view in row 8's `summary.json`. If it could not read the host, row 8b flips the flag to the fallback (trigger `limited-unreadable`), reverts as row 7a would, and reruns the mini-air once. The issue is resolved on `run`, `skipped-connected` or `voided-connected-during`; an undecided skip or void keeps it open as a finding. A can fail if the Limited reader reads `undecided` for a reason the probe names but cannot clear; the issue then stays open with the receipt. Undo: the flag is a scratch file, and the issue reopens.

- B: probe the mini-air at run level Limited at plan time. That needs a host write or a task run, which this plan may not do.
- C: keep "whatever the gated outcome". The register could say resolved while no host runs the tests.
- D: do nothing. The deciding reader is never judged.

Refs: expert pass H1; `probe-check.py --judge-gate`.

### D-1281: What about a RustDesk `--cm` window left open after a connection?

**I recommend A: record each process's start time, show it in the summary, and name the risk.** RustDesk keeps a closed connection's tab in its `--cm` window until someone closes it, so the probe can keep reading "connected" and skip the clipboard tests on every later run. The summary's `gated.detail` shows each RustDesk process's start time and age, so a stale one is visible, and the plan, the run book and the new issue name the risk. A can fail by leaving a stale window to skip runs until someone reads the detail; it only ever skips, and never runs the tests under a live session. Undo: drop the field.

- B: ask you to connect and disconnect once to measure it. A human action this plan does not ask for (M-10).
- C: ignore a `--cm` older than some age. It would run the tests under a long live connection.
- D: do nothing. A stale skip stays unexplained.

Refs: expert pass M1; RustDesk `server_model.dart:717-741`.

### D-1282: How does the clipboard file stay off your PC in tracked code?

**I recommend A: the new file skips itself unless `AVKIT_E2E_CLIPBOARD_GATED=1`, and only the mini-air's gated stage sets it.** After the split, the file's new name is in no exclusion list, so `npm run test:e2e` or an older plan's `flake-run.py` would run it on your PC. The guard is one line after the imports, outside every test. `guard-check.py` proves from Playwright's own list, which runs no test, that the two tests show as skipped, and `.agent/docs/commands.md` gains two lines saying so. A can fail if someone sets the variable on the dev PC; `commands.md` says never to. Undo: remove the line, the switch and the two doc lines. Editing `commands.md` and adding a line to the split file go beyond the grouping's list (M-8), which your hand-over covers.

- B: a `testIgnore` in `playwright.config.ts`. A shared config change that hides the file from the list, so nothing could check it.
- C: only the two `commands.md` lines. Every runner could still run the file.
- D: do nothing. The split opens the gap.

Refs: expert pass M2; `commands.md:67`, `:205`.

### D-1283: What happens to the expert pass's other items?

**I recommend A: word the void honestly, name the probe's scope, keep voided failures, harden `AvStage`, and run the full Vitest and ruff before the snapshot.** A connection during the stage voids the result, but it cannot undo what the tests already wrote to that desktop's clipboard, and AC-88.12 leaves an image there; the User Review and the run book say so. The run book names that only RustDesk and RDP are detected, that an `rdpclip.exe` left in a disconnected RDP session reads connected until logoff, and that `qwinsta` is read in English. `gated.voided_failures` keeps a voided report's failures without changing the exit. `AvStage` pipes its internal calls to `$null`, and a test checks the exact main exit. Row 7b runs the full Vitest and the gate's ruff steps first. A can fail if a void hides a regression; `voided_failures` shows it. Undo: drop the field, the test and the lines.

- B: restore the clipboard after AC-88.12. That changes a moved test (M-7).
- C: read RDP session states by number. A classifier change with no host to prove it.
- D: do nothing. The User Review overstates what a void protects.

Refs: expert pass M3, L1 to L4; `capture-filmstrip-actions.test.ts:242-267`.

## Research References

- **RustDesk** (source read at plan time into `D/rustdesk-src/`): `start_ipc` in `src/server/connection.rs` builds `--cm` and spawns it through `run_as_user` for each incoming connection; `--cm-no-ui` is the Linux headless form. `src/core_main.rs` handles `--tray`, `--service`, `--server` and `--cm`, the last commented "call connection manager to establish connections". The mini-air runs 1.4.5+63.
- **Windows sessions:** `qwinsta` lists sessions by name, id and state; an RDP session is `rdp-tcp#<n>` and Active while connected, and `rdp-tcp` alone is the listener. `rdpclip.exe` runs in an RDP session to sync its clipboard.
- **`Win32_Process.CommandLine`:** an unelevated caller gets `$null` for processes of other users and session 0; an elevated one reads them all. The mini-air's SSH session is elevated (`plan-session-probe-miniair-1.txt`), the dev PC's shell is not (`plan-session-probe-devpc.txt`).
- **PowerShell functions:** a later `function` definition of the same name replaces the earlier one in the same scope, which is the launcher test's seam for `AvSessionProbe`.

## Planning receipts

All under `C:/Temp/av-kit/e2e-clipboard-specs/`, read-only against the repository. The mini-air was read once through the alias in the local config, writing nothing there.

| Receipt | What it shows |
|---|---|
| `plan-deps.txt`, `plan-split-out*.txt`, `plan-split-selftest*.txt`, `plan-split-check-red.txt`, `plan-split-check-red-3.txt` | Each test's helpers; the three built files and their hashes (`plan-split-out-3.txt` after the D-1282 guard); the split selftest (6 cases in `-3`); `--check` red at `HEAD` |
| `plan-eslint*.txt`, `plan-eslint-neg.txt`, `plan-eslint-neg-3.txt` | `tsc` and ESLint on the built files; the planted unused constant fails |
| `plan-flake-guard-head.txt`, `plan-flake-selftest.txt` | `OLD_CLIPBOARD` refuses at `HEAD`; the runner's own checks |
| `plan-session-probe.ps1`, `plan-session-probe-miniair-1.txt`, `plan-session-probe-devpc.txt` | The read-only probe and both hosts' process and session state |
| `rustdesk-src/` | The RustDesk source files the signal rests on |
| `plan-probe-block-red.txt`, `plan-selftest-probe-check.txt` | `probe-check.py --block` red at `HEAD`; its selftest (15 cases; 28 after D-1280, `plan-selftest-probe-check-2.txt`) |
| `plan-guard-list-head.txt`, `plan-guard-judge-unset.txt`, `plan-guard-judge-set.txt`, `plan-selftest-guard-check.txt` | `guard-check.py --list` at `HEAD` (239 tests in 29 files, none skipped: exit 1); the judge on a scratch list of the built files with the variable unset (ok, two skipped) and set (4 problems); its 8-case selftest |
| `plan-selftest-{eol-check,identity,pins-check,red-check,snapshot,split-specs}.txt` | Each plan-local checker's selftest (pins-check 13 cases, split-specs 6) |
| `plan-issues.txt`, `plan-name-search.txt`, `plan-eol.txt` | Both issues open, the new id free; the new file's name unused; line endings by bytes |
| `plan-ruff-*.txt` | ruff on this folder |
| `ecs-plan-decisions-1.txt` to `ecs-plan-decisions-3.txt` | `decision_sources` probes |
| `ecs98-expert-pass.txt` | The fresh-context expert pass (H1, M1 to M3, L1 to L4), adopted through D-1280 to D-1283 |

## Validation stage contract

| Stage | Checks | Where |
|---|---|---|
| Plan review | This plan and `task.md`, against both issues, grouping §3 Session 98 and §8, the s98 brief, the spec files, the tool, the host scripts, RustDesk's source and the planning receipts | `ecs-plan-2026-11-20-e2e-clipboard-specs` |
| Row checks | Each row's validation command | `task.md` |
| Session gate | §Session gate | H1-2 |
| Execution review | The delta from `baseline.sha` in the §Files Modified paths, the row-2, row-7a, row-7b, row-8 and row-8b receipts, against AC-1 to AC-20 | `ecs-execution-2026-11-20-e2e-clipboard-specs` |
