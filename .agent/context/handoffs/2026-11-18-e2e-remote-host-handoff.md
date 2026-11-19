---
date: "2026-11-19"
project: "2026-11-18-e2e-remote-host"
meu: "none"
status: "complete"
action_required: "VALIDATE_AND_APPROVE"
template_version: "2.2"
verbosity: "standard"
plan_source: "docs/execution/plans/2026-11-18-e2e-remote-host/implementation-plan.md"
build_plan_section: "none (E2E runner tooling; no MEU, D-1212, D-1132)"
agent: "claude-code-local (Claude Opus 5.5)"
reviewer: "codex (H1-7 execution review)"
predecessor: "2026-11-18-eval-describe-raw-bytes-handoff.md"
---

# Handoff: 2026-11-18-e2e-remote-host-handoff

> **Status**: `complete`
> **Action Required**: `VALIDATE_AND_APPROVE`

---

## Scope

**MEU**: none. Session 96 is E2E runner tooling with no product change and no MEU (triage D-1212; D-1132). It closes one register issue, `CI-E2E-FLEET-HOST-UNTRACKED` (`.agent/context/known-issues.yaml:5805`), under D-1221 to D-1225, each option A.
**Build Plan Section**: none. `docs/BUILD_PLAN.md` names neither `e2e_remote` nor `e2e-remote-host`, and row 8 found it byte-identical to row 0 (`erh-hub-audit.txt`: `BUILD_PLAN.md unchanged: True references: []`).
**Predecessor**: [2026-11-18-eval-describe-raw-bytes-handoff.md](2026-11-18-eval-describe-raw-bytes-handoff.md), Session 95. This session's `HEAD` and `baseline.sha` is `a43cdb2`, the triage commit that grouped Sessions 96 and 97 (`.agent/context/grouping/2026-11-18-e2e-remote-host-session-grouping.md` §3). Session 97 (`e2e-host-parity`) runs its acceptance run through this session's tool.

- **The tool (`tools/e2e_remote.py`, new; D-1221 A).** A Python command (standard library and PyYAML, LF, ASCII, 1,396 lines after D-1236) with five subcommands: `check`, `run`, `collect`, `release` and `summarize`.
  - `run <commit>` makes a `git archive` zip of the commit, stages the host scripts by `scp` into a content-addressed `bin\` set folder, takes the host lock, uploads the zip and the region-picker stub, has the host verify, extract, reset the times and build that tree, starts the full Electron E2E suite with `Start-ScheduledTask` on the existing Interactive-logon task, polls for `DONE`, copies `meta.txt`, `specs.txt`, `report.json`, `pid.txt` and the logs back and writes `summary.json` and `summary.txt` under `C:/Temp/av-kit/e2e-remote/<run-id>/`, then releases the lock.
  - Every `ssh` and `scp` call carries `-o BatchMode=yes -o StrictHostKeyChecking=yes` and no other host-key option, identity or retry (`PINNED_SSH`). Each host script prints one JSON line, and the outcome is that line's `reason`, mapped through the closed table, because the host's outer shell flattens exits to 0 or 1 (`NAMED_REFUSAL`, D-1226, D-1230).
  - It refuses with a named reason and exit code, in the plan's §Refusal order: nobody signed in or only session 0 (20), a locked desktop (21), a busy host (22), another run's lock (23), a running task (24), any of 13 missing prerequisites, all named together (25), a commit that is not the one asked for (26), a stale build (27), a failed build step (28), a missing request (29), a poll timeout or a launcher that ended with no `DONE` (30), a report that is missing, invalid, inconsistent, has errors or names other spec files (31), a stale known list (32), an existing receipt (33), a failed receipt write (34), and any failure not in the known list (40).
  - The summary is read from `report.json` and `specs.txt` only (`REPORT_ONLY`). A run exits 0 only when every test that did not pass is listed for the configured label in `tools/e2e_host/known-failures.json` and every listed issue is `open` (`KNOWN_NAMED`, D-1225 A). The AC id is a title's first token, so `AC-102.20`'s title does not match `AC-82.6`.
  - It never stops, installs, registers or changes anything on the host; its only action on the task is `Start-ScheduledTask` (`NEVER_STOP`, D-1223 A, D-1224 A).
- **The host scripts (`tools/e2e_host/`, new; D-1226, D-1227, D-1228).** Seven Windows PowerShell 5.1 scripts (ASCII, LF, no backtick): `host-facts.ps1`, `host-lock.ps1`, `host-prepare.ps1`, `host-start.ps1`, `host-status.ps1`, `host-release.ps1` and the launcher `run-e2e.ps1`. The lock is created with `CreateNew`, and every writing step refuses unless the lock names its run id (`ONE_LOCK`). The zip comment, the zip's SHA-256 and the tree markers name the full commit, and the launcher checks it again before the suite starts (`COMMIT_BOUND`). After the extract, `host-prepare.ps1` measures how far the archive's times sit ahead of the commit, records it as `commit_offset_s` and `mtime_skew_s`, and resets every time to before the build, which is why `global-setup.ts:43` no longer refuses the tree. The tracked launcher replaces the hand launcher at `<root>\run-e2e.ps1`, and the hand copy is kept beside it, renamed with its hash prefix (`CHECK_AND_NAME`).
- **The config and the known list (D-1222 A, D-1225 A).** The host alias, account, folder and task name live only in the untracked `<HOME>/.config/av-kit/e2e-host.json` (11 keys), with the tracked `tools/e2e_host/e2e-host.example.json` (`LOCAL_HOST_DETAILS`). `tools/e2e_host/known-failures.json` lists the four known failures of the label `mini-air`, bound to `CAPTURE-TEXT-PIXEL-2PX-MINIAIR` and `E2E-HOVER-NO-POINTER-DEVICE`, and the two clipboard specs the host skips.
- **The tests (`tests/tooling/test_e2e_remote.py`, new; D-1231).** LF, ASCII, 2,310 lines, 181 tests for AC-1 to AC-15, AC-19 and AC-21 (174 at row 4, and 7 added under D-1236 after the execution review's round 1), with a fake `ssh` and `scp`; AC-14 parses each host script in Windows PowerShell 5.1, and AC-15 runs them on fixture roots under an outer `powershell -c`, as the host's shell does.
- **The run book and the D6 row (D-1234).** `.agent/docs/e2e-remote-host.md` (new, LF) names the prerequisites, every reason and exit, every prerequisite id, every config key, the five subcommands and the known list. `.agent/docs/commands.md` gains one CRLF row, `ui-electron-remote`, after `ui-electron` (`:205`).
- **Records (row 7, D-1233).** The issue is `resolved` through this plan's `issue-resolve.py`, bound to row 0's register hash; `known-issues.md` is rendered; grouping row 96 (`:133`) reads `executed (Session 96)`.
- **The review corrections (D-1236).** The execution review's round 1 found three faults in the tool; each is fixed with a regression test that failed first by assertion, and no existing assertion changed.
  - F1: a failed release at the end of `run` or `collect` was swallowed, so the command exited 0 with the lock still held. `release_lock` (`tools/e2e_remote.py:904`) now returns the refusal; `_collect_and_summarize` raises it after the summary is written (`:1108` to `:1111`), so the command exits 11 on `host-key-failed` (no retry) or 10 on another transport failure, keeps the summary, writes `refusal.json` with `lock_kept` true and prints the `release <run id>` hint (`_release_hint`, `:934`). When a refusal's own release fails, the first refusal keeps its reason and exit, the release failure is added to `also`, and `lock_kept` is true (`:1237` to `:1251`).
  - F2: `summarize --out` and `collect` refuse 33 `receipt-exists` when either `summary.json` or `summary.txt` exists, before writing anything (`SUMMARY_NAMES`, `:864`; `:1049`; `:1321`).
  - F3: an `OSError` writing `polls.jsonl` inside the poll loop refuses 34 `receipt-write-failed`, keeps the lock and prints the `collect` and `release` hints (`:981` to `:987`), where it escaped as a traceback.
  - No new reason or exit; the run book gains the section "When the release itself fails" and names `summary.txt` and `lock_kept` (`.agent/docs/e2e-remote-host.md:100`, `:217`).

**What Mat sees.**
- A coordinator can run the full E2E suite on the mini-air with one command, `uv run python tools/e2e_remote.py run <commit>`, and gets back the report, a summary that names every failure, and an exit code that says whether anything is new. The dev PC's load no longer gates that run.
- When the mini-air cannot run, the tool says why in one named line and leaves the host as it was: nobody signed in, the desktop locked, another job busy, a prerequisite missing. It never stops anything on the host.
- Nothing changes in the app: no product code.

**Edges.**
- **The host is shared.** The busy check sees the configured busy account's test processes and any runner worker, and a poll records `overlap` if one appears during the run; it does not stop them. The check found the configured busy account is not a local account on the host at row 5 and reported it (`busy_users_missing`), as the plan allows; the busy check still runs on process owners.
- **The tool binds a commit, not a working tree.** Uncommitted changes are never sent. A run of a commit whose `.node-version` major differs from the host's Node refuses 25 `node-version`.
- **Four failures are known on that host.** They are host findings for Session 97, not passes: a run exits 0 with them only while their issues are `open`. A fifth failure, or one of them back flaky, exits 40.

**Plan:** [implementation-plan.md](../../../docs/execution/plans/2026-11-18-e2e-remote-host/implementation-plan.md) §Single-statement contracts.

**Execution authorization:** `USER_EXPLICIT`, 2026-11-18: "proceed with the next session prompt orchestration here like you did the others" (`implementation-plan.md:15`). `plan_to_exec_gate: human`. The plan review approved at round 2 after F1 was fixed (`.agent/context/handoffs/2026-11-18-e2e-remote-host-plan-critical-review.md`). The coordinator wrote that approval into the plan's Status line after the review (Departures).

Receipts named by file name alone are in the session's receipts folder: the `e2e-remote-host` folder under `RECEIPTS_DIR`. The real run's receipts are in its run folder under the `e2e-remote` folder there.

---

## Acceptance Criteria

| AC | Type | Description | Source | Test(s) | Status |
|----|------|-------------|--------|---------|--------|
| AC-1 | test | The config is read from `--config`, else `AVKIT_E2E_HOST_CONFIG`, else `<HOME>/.config/av-kit/e2e-host.json`; a missing, unknown, absent or bad key exits 2 naming it with no `ssh` call; the tracked example loads clean | D-1222 | `tests/tooling/test_e2e_remote.py:553`, `:562`, `:587`, `:596`, `:604`, `:612`, `:622` | ✅ |
| AC-2 | test | Every `ssh` and `scp` argv carries the pinned options and no bypass; a host-key failure exits 11 after one call; another 255 exits 10; the post-quantum warning and CLIXML noise do not fail a call; outcomes come from the JSON `reason` only | `PINNED_SSH`; D-1215 | `test_e2e_remote.py:639`, `:666`, `:674`, `:683`, `:691`, `:704`, `:713`, `:719`, `:726`, `:733`, `:765` (D-1236) | ✅ |
| AC-3 | test | No explorer for the user, only session 0, or a session not `Active` refuses 20 before any lock or upload; `DONE` 96 maps to 20 | `NAMED_REFUSAL` | `test_e2e_remote.py:802`, `:810` | ✅ |
| AC-4 | test | LogonUI in the user's session refuses 21; `DONE` 97 maps to 21 | Grouping §3 refusals | `test_e2e_remote.py:818`, `:826`, `:832` | ✅ |
| AC-5 | test | Busy user process, `Runner.Worker` or own orphan refuses 22; `overlap` recorded while polling, empty on a healthy run; hidden owners refuse 22 `host-busy-unknown`; another lock 23; a running task 24; a busy re-check after the lock refuses 22 and releases; no argv stops or changes anything | D-1224; `ONE_LOCK`; `NEVER_STOP` | `test_e2e_remote.py:849`, `:860`, `:889`, `:897`, `:905`, `:919`, `:939`, `:953`, `:962`, `:970`, `:978` | ✅ |
| AC-6 | test | Each of the 13 prerequisite ids refuses 25 naming it, and several are named together | D-1223; `CHECK_AND_NAME` | `test_e2e_remote.py:1006`, `:1031`, `:1041`, `:1046`, `:1051` | ✅ |
| AC-7 | test | An unknown commit refuses 26 before any `ssh`; a mismatched zip comment, upload hash or tree marker refuses 26; the request binds the full sha, the zip hash and the stub hashes; the real HEAD archive's comment is HEAD's sha | `COMMIT_BOUND` | `test_e2e_remote.py:1063`, `:1070`, `:1079`, `:1091`, `:1098`, `:1122` | ✅ |
| AC-8 | test | A failing build step refuses 28 naming the step and log; a stale build refuses 27; `DONE` 99 maps to 27 | Grouping §3 refusals | `test_e2e_remote.py:1135`, `:1148`, `:1156`, `:1163` | ✅ |
| AC-9 | test | No `DONE` by `timeout_min` refuses 30 and keeps the lock, naming `collect` and `release`; a task ending with no `DONE` refuses 30 `launcher-ended`; `DONE` 95 maps to 29 | D-1230; `NEVER_STOP` | `test_e2e_remote.py:1178`, `:1192`, `:1207`, `:1215`, `:1225`, `:1233`, `:1246`, `:1256` (D-1236) | ✅ |
| AC-10 | test | The summary's counts come from `report.json` only; a report that does not add up, has errors, is invalid or missing, or whose files differ from `specs.txt` and the expected set, refuses 31 | `REPORT_ONLY` | `test_e2e_remote.py:1319`, `:1338`, `:1346`, `:1353`, `:1368`, `:1375`, `:1384`, `:1395` | ✅ |
| AC-11 | test | Listed failures are known (exit 0); an unlisted unexpected, flaky or skipped test exits 40; a known test now passing is listed with exit 0; a listed issue not open, a listed test absent or an entry matching two tests exits 32; a listed test back flaky or skipped exits 40; the AC id is the title's first token | D-1225; `KNOWN_NAMED` | `test_e2e_remote.py:1410` to `:1561` (16 tests) | ✅ |
| AC-12 | test | An existing run folder or `--out` file refuses 33 before any `ssh`; a failed collect leaves no `host` folder; a failed summary write refuses 34 with no partial file | `NO_PARTIAL`; D-1232 | `test_e2e_remote.py:1582`, `:1592`, `:1606`, `:1621`, `:1630`, `:1641`, `:1677`, `:1649`, `:1661` (D-1236) | ✅ |
| AC-13 | test | `release` removes only its own lock (0), refuses another (23 `lock-mismatch`), reports none (0); every refusal after the lock except the polling ones releases it | `ONE_LOCK` | `test_e2e_remote.py:1700`, `:1707`, `:1717`, `:1724`, `:1730`, `:1745` (D-1236) | ✅ |
| AC-14 | test | The host scripts are ASCII, LF, backtick-free, parse clean in Windows PowerShell 5.1, hold no stop, install or task-change token, share one busy block and JSON form; the launcher carries its marker and writes `pid.txt` before waiting; the tool holds no host-key bypass | `NEVER_STOP`; D-1226 | `test_e2e_remote.py:1772`, `:1800`, `:1808`, `:1825`, `:1834`, `:1846` | ✅ |
| AC-15 | test | On a fixture root, under an outer `powershell -c`, the host scripts report facts in the pinned schema, take and refuse the lock, release only their own, refuse a mismatched commit, measure and reset the mtime skew, refuse a stale build, and the launcher writes `DONE` 95, 98 and 99; the real facts round-trip through `evaluate` | `COMMIT_BOUND`; `ONE_LOCK`; D-1228 | `test_e2e_remote.py:1965` to `:2237` (15 tests) | ✅ |
| AC-16 | reproduction | `zip-time.py <baseline sha> D -8` exits 0 at row 1, before the tool exists; at row 6 the real `prepare-extract.json` records `commit_offset_s` from 10,796 to 10,804 | Brief §Red first; `global-setup.ts:40-47` | row 1 `erh-zip-time.txt`; row 6 `erh-run-6-check.txt` and `erh-run-6-fix1-check.txt`; gate `erh-zip-time` | ✅ |
| AC-17 | live | A real `check` exits 0 with no reason and writes `erh-check-5.json`; the probe after it shows the host unchanged outside `bin\` | `CHECK_AND_NAME`; D-1223 | row 5 `erh-check-5.txt`, `erh-check-5.json`, `erh-host-probe-5-check.txt` | ✅ |
| AC-18 | live | `run <baseline sha>` exits 0; its `summary.json` holds 232 tests, 228 expected, the 4 known, 0 flaky, 0 skipped, 0 new, 27 spec files, the two skipped clipboard specs, `overlap` empty, `pid.txt`, the baseline sha; the lock released afterwards | Grouping §3 acceptance | row 6 `erh-run-6.txt`, `erh-run-6-check.txt`, `erh-host-probe-6.txt`; row 6 again after D-1236 (S13) `erh-run-6-fix1.txt`, `erh-run-6-fix1-check.txt`, `erh-host-probe-6-fix1.txt`; gate `remote-evidence` | ✅ |
| AC-19 | test | The run book names every reason, exit, prerequisite id, config key and subcommand, and the known list | Grouping §3 run book | `test_e2e_remote.py:2254`, `:2271` | ✅ |
| AC-20 | doc | `commands.md` equals its row-0 bytes with one CRLF line added after `:205`, the `ui-electron-remote` row | D-1234 | row 4 `erh-commands-check.txt`, `erh-eol-4.txt` | ✅ |
| AC-21 | test + row | No new tracked file holds an IPv4 literal, a Windows or POSIX home prefix or an `.ssh` path (test); row 5 scans the new files and this plan folder for the local config's values and finds none | `LOCAL_HOST_DETAILS` | `test_e2e_remote.py:2290`, `:2301`; row 5 `erh-host-details-5.txt`; row 7 `erh-host-details-7.txt`; H1-6 `erh-host-details-h1.txt` | ✅ |
| AC-22 | register | The issue is `resolved` through `issue-resolve.py` with a `verification` and `resolution_path` citing the AC-17 and AC-18 receipts and Session 96; `render` and `render --check` pass; grouping row 96 reads `executed (Session 96)` and no other grouping line changed | Grouping §6 | row 7 `erh-issue-resolve.txt`, `erh-issues-render-check.txt`, `erh-register-check.txt` | ✅ |
| AC-23 | gate | `session-gate.ps1` ends `session-gate: all steps exit 0` | Brief §Gate | H1-2 `erh-gate-h1.txt` | ✅ |
| Red check (cross-ref) | records | Session 83's `red-check.py`, copied into this plan folder at row 0: `check_required` (`docs/execution/plans/2026-11-18-e2e-remote-host/red-check.py:284`), `--require` read at `:948`, the summary line printed at `:959`, `selftest` at `:912`; its selftest passes at row 0 and in the gate | Local Canon | row 0 `erh-baseline.txt`; row 1 `erh-red-check.txt`; gate `red-check-selftest` | ✅ |
| Issue resolve (cross-ref) | records | Session 95's `issue-resolve.py`, copied into this plan folder at row 0: `RESOLVE_KEYS` (`docs/execution/plans/2026-11-18-e2e-remote-host/issue-resolve.py:53`), `--expect-sha256` required at `:215`, `resolve` at `:230`, its last line printed at `:306` | Local Canon (D-1233) | row 7 `erh-issue-resolve.txt` | ✅ |

<!-- CACHE BOUNDARY -->

---

## Evidence

### FAIL_TO_PASS

| Test | Red Output (hash/snippet) | Green Output | File:Line |
|------|---------------------------|--------------|-----------|
| AC-1 | `AssertionError: tools/e2e_remote.py does not exist yet`, 27 tests (`erh-red.txt`, `174 failed in 9.69s`) | Row 2: `143 passed, 31 deselected in 15.05s` (`erh-green-2.txt`); row 4: `174 passed in 38.39s` (`erh-green-4.txt`) | `test_e2e_remote.py:553`, `:562`, `:587`, `:596`, `:604`, `:612`, `:622` |
| AC-2 | the same assertion, 11 tests (`erh-red.txt`) | Row 2 and row 4, as above | `test_e2e_remote.py:639` to `:733` |
| AC-3 | the same assertion, 6 tests (`erh-red.txt`) | Row 2 and row 4, as above | `test_e2e_remote.py:802`, `:810` |
| AC-4 | the same assertion, 3 tests (`erh-red.txt`) | Row 2 and row 4, as above | `test_e2e_remote.py:818`, `:826`, `:832` |
| AC-5 | the same assertion, 19 tests (`erh-red.txt`) | Row 2 and row 4, as above | `test_e2e_remote.py:849` to `:978` |
| AC-6 | the same assertion, 19 tests (`erh-red.txt`) | Row 2 and row 4, as above | `test_e2e_remote.py:1006` to `:1051` |
| AC-7 | the same assertion, 8 tests (`erh-red.txt`) | Row 2 and row 4, as above | `test_e2e_remote.py:1063` to `:1122` |
| AC-8 | the same assertion, 4 tests (`erh-red.txt`) | Row 2 and row 4, as above | `test_e2e_remote.py:1135` to `:1163` |
| AC-9 | the same assertion, 7 tests (`erh-red.txt`) | Row 2 and row 4, as above | `test_e2e_remote.py:1178` to `:1246` |
| AC-10 | the same assertion, 10 tests (`erh-red.txt`) | Row 2 and row 4, as above | `test_e2e_remote.py:1319` to `:1395` |
| AC-11 | the same assertion, 17 tests (`erh-red.txt`) | Row 2 and row 4, as above | `test_e2e_remote.py:1410` to `:1561` |
| AC-12 | the same assertion, 7 tests (`erh-red.txt`) | Row 2 and row 4, as above | `test_e2e_remote.py:1582` to `:1677` |
| AC-13 | the same assertion, 5 tests (`erh-red.txt`) | Row 2 and row 4, as above | `test_e2e_remote.py:1700` to `:1730` |
| AC-14 | 12 tests: 11 `AssertionError: tools/e2e_host/<the script> does not exist yet` lines across the seven host scripts, and the tool's line for its own host-key check (`erh-red.txt`) | Row 3: `170 passed, 4 deselected in 43.00s` (`erh-green-3.txt`); row 4 as above | `test_e2e_remote.py:1772` to `:1846` |
| AC-15 | 15 tests: 12 `AssertionError: tools/e2e_host/host-facts.ps1 does not exist yet` and 3 of the tool's line (`erh-red.txt`) | Row 3 and row 4, as above | `test_e2e_remote.py:1965` to `:2237` |
| AC-19 | the tool's line, 2 tests (`erh-red.txt`) | Row 4 as above | `test_e2e_remote.py:2254`, `:2271` |
| AC-21 | the tool's line, 2 tests (`erh-red.txt`) | Row 4 as above, after D-1235 | `test_e2e_remote.py:2290`, `:2301` |

- **Not in FAIL_TO_PASS:** AC-16 to AC-18, AC-20, AC-22 and AC-23 are checks (reproduction, live, doc, register and gate), not tests that failed at Red.
- **The Red.** Every one of the 174 tests failed by an assertion that the file under test does not exist yet, before any of it existed: `erh-red.txt` holds 174 `AssertionError` lines and ends `174 failed in 9.69s`, and `erh-red.txt.exit` reads `1`. By the file each names: `tools/e2e_remote.py` 151, `tools/e2e_host/host-facts.ps1` 16, `run-e2e.ps1` 2, and one each for `host-lock.ps1`, `host-prepare.ps1`, `host-release.ps1`, `host-start.ps1` and `host-status.ps1`. `erh-red-check.txt`: `red-check: 1 receipt(s), 17 required test(s), 0 problem(s)` (`--require` for each of AC-1 to AC-15, AC-19 and AC-21).
- **The test file from Red to Green.** Rows 2, 3 and 4 each compare the file's SHA-256 with `erh-test-sha.txt` before pytest. Rows 2 and 3 matched the row-1 hash. Row 4's first run failed one test, `test_ac_21_no_host_details_in_new_files`, on the test file's own CLIXML fixture (`erh-green-4-stop.txt`: `1 failed, 173 passed in 36.86s`); under D-1235 one literal was split and the hash receipt re-recorded (Departures). Row 4 then read `174 passed in 38.39s` (`erh-green-4.txt`).
- **Green ran with no skip.** Rows 2 to 4 refuse a `skipped` line in their receipts; row 2 deselects AC-14, AC-15, AC-19 and AC-21 by `-k` and row 3 deselects AC-19 and AC-21, as their cells name, and row 4 runs all 174.
- **The review corrections' Red and Green (D-1236).** Seven new tests (five functions, two parametrized) were added to the test file and run alone against the unfixed tool: `erh-fix1-red.txt` ends `7 failed, 174 deselected in 2.64s` (`erh-fix1-red.txt.exit` reads `1`), each by an assertion on the outcome: `assert 0 == 11` and `assert 0 == 10` after `release failed: host-key-failed` and `release failed: ssh-failed` (AC-2, `test_e2e_remote.py:765`); `assert 'uncaught OSError: fixture disk full' == 34` (AC-9, `:1256`); `assert 0 == 33` for `summarize` and for `collect` with an existing `summary.txt` (AC-12, `:1649`, `:1661`); and the missing `also refused: <the release's reason>: <its detail>` line, twice (AC-13, `:1745`). `erh-fix1-red-check.txt`: `red-check: 1 receipt(s), 5 required test(s), 0 problem(s)`. After the fix the full file passed: `181 passed in 49.43s` (`erh-fix1-green.txt`), no skip; `2 files already formatted` (`erh-fix1-fmt.txt`); `All checks passed!` (`erh-fix1-lint.txt`). `erh-fix1-test-additions.txt` cuts the six added blocks (the helper `refusal_of` at `:754` and the five tests) and finds the remainder's SHA-256 equal to the D-1235 hash: `additions only: True`.

#### Per-row evidence

**Row 0, baseline** (`erh-baseline.txt`)
- `baseline: all steps exit 0`; `anchor lines moved: none`.
- The anchors: `ui/tests/e2e/global-setup.ts:43`, `ui/playwright.config.ts:14` and `:18`, `.agent/docs/commands.md:205`, and grouping row 96 at `:133` (`one pending row: True`).
- The issues: `CI-E2E-FLEET-HOST-UNTRACKED: entries 1, status open, line 5805`; `CAPTURE-TEXT-PIXEL-2PX-MINIAIR: entries 1, status open, line 5846`; `E2E-HOVER-NO-POINTER-DEVICE: entries 1, status open, line 5886`.
- `spec files at HEAD: 29 without the skip files: 27`.
- The records: `baseline-scope.json 33 paths; 13 absent; 8 foreign class`; `baseline-dirty.txt 19 paths, 0 foreign`; `baseline-skip-hashes.json 605 files`.
- The selftests: `red-check selftest: 39 fixture(s) (13 positive, 26 negative), 0 wrong: []`; `eol-check selftest: 24 case(s), 0 wrong: []`; `identity selftest: 0 failure(s)`.
- `check_home_path: ok files=2740 allowlisted=60 nul=31` (`erh-home-before.txt`).
- The hand scripts and both hand reports: their SHA-256 values are recorded in `erh-hand-hashes.json` (7 entries).
- **No moved citation (Session 51 RULE-3).** Every row-0 anchor was where the plan cites it (`anchor lines moved: none`).

**Row 1, the reproduction and the Red**
- `erh-zip-time.txt`: `entries: 2993 distinct DOS times: 1`; `zip comment is the commit id: True`; the newest DOS time is the dev PC's local reading of the commit time, 1 s apart (`DOS time is dev-pc local time (within 2 s): True`); `seconds a host at UTC-8 reads the files after the commit: 10799`. This is the cause `global-setup.ts:43` refused on the host (AC-16, part 1).
- The Red: as above.

**Row 2, Green: the tool** (`erh-green-2.txt`, `erh-green-2-fmt.txt`, `erh-green-2-lint.txt`)
- `143 passed, 31 deselected in 15.05s`; `2 files already formatted`; `All checks passed!`.

**Row 3, Green: the host scripts and both hand reports** (`erh-green-3.txt`, `erh-sum-check.txt`)
- `170 passed, 4 deselected in 43.00s`.
- `summarize` on the two hand reports, each into a fresh folder:
  - the 19:13:58 report: `result: ok exit=0`, `232 228`, the four known (`AC-102.19`, `AC-102.20`, `AC-126.8`, `AC-82.6`; the app's own AC ids, foreign to this plan), `new 0` (`erh-sum-191358.txt`);
  - the 18:53:48 report: `result: new-failures exit=40`, `220 12`, `known 4`, eight new (`AC-152.21` to `AC-152.24`, `AC-155.10`, `AC-155.11`, `AC-155.15`, `AC-156.11`; app AC ids, foreign to this plan) (`erh-sum-185348.txt`).

**Row 4, the run book and the D6 row** (`erh-green-4.txt`, `erh-commands-check.txt`, `erh-eol-4.txt`)
- `174 passed in 38.39s` after D-1235.
- `commands.md lines: 226 -> 227`, the new row 206 starts `| ui-electron-remote |`, `crlf only: True`.
- `eol-check: 21 scope path(s), 0 problem(s)`; every new file `LF, CR 0`.

**Row 5, the real check** (`erh-check-5.txt`, `erh-check-5.json`, `erh-host-probe-5-check.txt`, `erh-host-details-5.txt`)
- `facts: ps=5.1.26100.9818 elevated=True`; `desktop: explorer=1 session=1 state=Active logonui=[]`.
- `busy: busy=0 runner_workers=0 own_orphans=0`, with `busy_users_missing` naming the configured busy account (not a local account on the host; the plan allows it and the check still reads process owners).
- `task: exists=True state=Ready logon=Interactive runlevel=Limited limit_min=120 multiple=IgnoreNew`; `lock: holder=None launcher_marker=False`.
- `prereq: node=v26.13.0 uv=True vcruntime=True ffmpeg=True ffprobe=True free_gb=406.3`; `clock: ... tz_offset_min=-480 ssh_shell_set=True`.
- `check: ok`, exit 0.
- `probe after check, missing facts: []`; `host-details-scan: files=31 grown_pairs=0 bad=0`.

**Row 6, the real run** (`erh-run-6.txt`, `erh-run-6-check.txt`, `erh-run-6-dir.txt`, `erh-host-probe-6.txt`; the run's own folder under `e2e-remote`)
- The run id is `r20261119T074154Z-a43cdb2`: the run started at 07:41:54 UTC on the baseline commit `a43cdb2`. The row ran once (`erh-row-6-start.txt` `2026-11-19T07:41:54Z`; `erh-row-6-exit.txt` `exit 0` at `2026-11-19T08:07:15Z`).
- The checks before the lock, read again by `run`: `desktop: explorer=1 session=1 state=Active logonui=[]`; `busy: busy=0 runner_workers=0 own_orphans=0`; `task: exists=True state=Ready logon=Interactive runlevel=Limited limit_min=120 multiple=IgnoreNew`; `lock: holder=None launcher_marker=False`.
- The run's `progress.log`, in order: the archive `ee393cc3…` and the staged set `89d0c364a5a3`; `locked` at 07:42:04; `prepare verify: ok`, `prepare extract: ok`, `prepare build: ok` at 07:45:36 and `prepare stale: ok`; `started` at 07:45:44; 38 polls, the last `done=1 task=Ready` at 08:07:02; `collected host and host-logs`; `summary: ok exit=0`; `released` at 08:07:10.
- `prepare-extract.json`: `files 2721`, `mtime_skew_s 95`, `commit_offset_s 10799`. The archive's times sat 10,799 s ahead of the commit on the host's clock, as row 1 measured. The tree was reset before the build, so `global-setup.ts:43` built and ran it (AC-16, part 2).
- `erh-run-6.txt`: `summary: tests=232 expected=228 unexpected=4 flaky=0 skipped=0 spec_files=27 specs_checked=True playwright=1.64.1 duration_ms=1267731`. The four `known:` lines are `capture-inbox.test.ts` `AC-82.6`, `AC-102.19` and `AC-102.20` and `settings.test.ts` `AC-126.8`, the app's own AC ids (foreign to this plan). Then the two `skip:` lines, `capture-filmstrip-actions.test.ts` and `capture-import.test.ts`, and `result: ok exit=0`, the release line, and the last line `e2e-remote: ok exit=0 run=<the run id> receipts=<the run folder>`.
- `erh-run-6-check.txt`, read from the run's `summary.json` and `prepare-extract.json`: `tests 232 expected 228 unexpected 4 flaky 0 skipped 0 known ['AC-102.19', 'AC-102.20', 'AC-126.8', 'AC-82.6'] new [] spec_files 27 specs_checked True commit_offset_s 10799 mtime_skew_s 95 overlap []`.
- `summary.json` also holds the full commit `a43cdb24f97af6f10498fa70abb5ada4b0882835`, `done 1`, `label mini-air`, `stale []`, `known_now_passing []`, the zip and stub hashes, and `tool_sha256` for the tool and its 9 host files. The run's `host/` folder holds `DONE`, `meta.txt`, `pid.txt`, `report.json`, `specs.txt` and the run logs.
- **The host after the run** (`erh-host-probe-6.txt` against `erh-host-probe-5.txt`, the read-only probe). Only these lines changed:
  - `lock=False tree_marker=True bin=True` (was `tree_marker=False`);
  - `runs=True results_r=1 hand_copies=1` (was `runs=False results_r=0 hand_copies=0`);
  - `launcher=True sha256=<the tracked launcher's hash> tracked_marker=True` (was the hand launcher's hash `5AB99494…` and `tracked_marker=False`); the new hash equals the SHA-256 of `tools/e2e_host/run-e2e.ps1`;
  - `free_gb` from 406.3 to 404.2, and the process count and time readings.
  
  The task stays `state=Ready logon=Interactive runlevel=Limited` with its action, limit and `multiple=IgnoreNew` unchanged, and the user's session stays `Active`.

**Row 6 again on the final tool (S13, after D-1236)** (`erh-run-6-fix1.txt`, `erh-run-6-fix1-check.txt`, `erh-host-probe-6-fix1.txt`; the run's own folder under `e2e-remote`)
- The tool changed after row 6, so row 6's cell ran once more on the final files, with the receipt names given a `-fix1` suffix; the first run's receipts are kept. The run id is `r20261119T084412Z-a43cdb2` (`erh-row-6-fix1-start.txt` `2026-11-19T08:44:11Z`; `erh-row-6-fix1-exit.txt` `exit 0` at `2026-11-19T09:07:59Z`). `erh-run-6-dir.txt` now names this run's folder, and the first run's folder name is kept in `erh-run-6-dir-pre-fix1.txt`.
- The run's `progress.log`: the same archive `ee393cc3…` and staged set `89d0c364a5a3` (the host scripts did not change); `locked` at 08:44:23; `prepare verify: ok`, `prepare extract: ok`, `prepare build: ok` at 08:46:17 and `prepare stale: ok`; `started` at 08:46:25; `DONE 1` and `collected host and host-logs` at 09:07:52; `summary: ok exit=0`; `released` at 09:07:54.
- `erh-run-6-fix1.txt`: `summary: tests=232 expected=228 unexpected=4 flaky=0 skipped=0 spec_files=27 specs_checked=True playwright=1.64.1 duration_ms=1277136`; the same four `known:` lines and two `skip:` lines as the first run; `result: ok exit=0`; the release line; and the last line `e2e-remote: ok exit=0 run=<the run id> receipts=<the run folder>`.
- `erh-run-6-fix1-check.txt`: `tests 232 expected 228 unexpected 4 flaky 0 skipped 0 known ['AC-102.19', 'AC-102.20', 'AC-126.8', 'AC-82.6'] new [] spec_files 27 specs_checked True commit_offset_s 10799 mtime_skew_s -3645 overlap []`. `commit_offset_s` is the first run's 10,799. `mtime_skew_s` compares the archive's fixed times with the host's clock at the extract, which read 1 h 2 min later than at the first run, so it moved from 95 to -3,645; the tree was reset before the build either way.
- `summary.json` holds the full commit `a43cdb24f97af6f10498fa70abb5ada4b0882835`, `done 1`, `label mini-air`, `stale []`, `known_now_passing []`, and `tool_sha256` for 10 files, each equal to the file's current SHA-256 (the tool's begins `e8d9638b`). The `host/` folder holds `DONE`, `diag`, `meta.txt`, `pid.txt`, `report.json`, `run.err`, `run.log` and `specs.txt`.
- **The host after the run** (`erh-host-probe-6-fix1.txt` against `erh-host-probe-6.txt`). Only these lines changed: `results_r=2` (was `1`); `free_gb` from 404.2 to 402.2; and the process count, time and load readings. The lock line, the launcher line, the task and the session are unchanged.

**Row 7, records** (`erh-issue-resolve.txt`, `erh-issues-render.txt`, `erh-issues-render-check.txt`, `erh-register-check.txt`, `erh-host-details-7.txt`)
- Before the row: `issue-resolve-set.json` was written from the receipt lines by a script in the receipts folder (`erh-row-7-set.txt`: `wrote issue-resolve-set.json 2184 B; CR 0`), and grouping row 96 at `:133` was set by bytes (`erh-row-7-grouping.txt`: `lines changed: [133] CR count: 0 bytes 14963 -> 14977`). The setter refuses a home path, a backslash or any host value of the local config.
- `decision logs read: 108 of 108`.
- `register sha256 before=2450ee1c6802051a165ee48bbf941d89b8263200e9aaa344e79f3ded9ee0c9e0`; `target sha256 after=533f5f92594ad15168827be79c0cbab1e28990e243bc00cad24d6142988a1858 CRLF=0 LF=5924`.
- `parsed fields changed: 5`: `.issues[146].resolution_path`, `.issues[146].status`, `.issues[146].verification.last_checked`, `.issues[146].verification.method` and `.issues[146].verification.result`.
- `issue-resolve: 0 problem(s)`. The register before the resolve is kept as `issue-resolve/register-before-resolve.yaml`.
- The render: `Rendered known-issues.md: 35 lines`, then `OK: known-issues.md is up-to-date`.
- `erh-register-check.txt`: `other issues changed: [] changed keys: ['resolution_path', 'status', 'verification'] issue ok: True grouping lines changed: [133] row ok: True`.
- `erh-host-details-7.txt`: `grown check: '.agent/context/known-issues.yaml' keys grown: []`, the same for `known-issues.md`, then `host-details-scan: files=32 grown_pairs=2 bad=0`.
- **After D-1236 and S13.** The register was left as row 7 wrote it. Its `verification` cites row 4's Green (`174 passed in 38.39s`), the first run `r20261119T074154Z-a43cdb2` and `erh-run-6-check.txt`, and its `resolution_path` describes the tool. Those receipts are kept, and what they say is still true; the second run gave the same counts. So no `issue-resolve.py` call was needed, and the register's hash stays `533f5f92594ad15168827be79c0cbab1e28990e243bc00cad24d6142988a1858`.

**Row 8, the hub** (`erh-hub-audit.txt`): `BUILD_PLAN.md unchanged: True references: []`.

**H1 rows**
- H1-1 (`task-unchecked.txt`): `unchecked implementation rows: []`, before the review and again after D-1236.
- H1-2, first (`erh-gate-h1.txt` then, kept with its step receipts in the receipts folder's `pre-fix1` folder): one run, stamp `20261119-031016`, `session-gate: all steps exit 0`, `tested_state` `a43cdb24f97af6f10498fa70abb5ada4b0882835+4753afb7d1c6594f006481c0cfca752dc003caeaba7e018e3b9c3d04b56fbd6b`, `174 passed in 39.97s`, `3293 passed, 37 warnings in 297.28s`, `host-load: 18 %`. It is superseded: D-1236 changed the tool, the tests and the run book, which are `identity.py` inputs.
- H1-2 after D-1236 and S13 (`erh-gate-h1.txt`): one run, stamp `20261119-040827`, `session-gate: all steps exit 0` (Quality Gate Results). The load probe before it read `cpu load: 40` (`erh-load-probe-h1.txt`), and the gate's own `host-load` step read `host-load: 24.6 %` after `waited 13 s (bar 50 %)`.
- H1-3 after D-1236 (`erh-focus-update-fix1.txt`, `erh-render-check.txt`): the Session 96 line was updated in place, not added again: `before: 97054 B CRLF 236` (the bytes H1-3 left, so no other session had written the file); `after: 97387 B CRLF 236 bare LF 0`; `line changed: 1; other lines kept: True`; `focus-update: ok`. Then the drift check passed again. H1-4 after D-1236: `skip-basis changes since row 0: []`.
- H1-3, first (`erh-focus-insert.txt`, `erh-render-check.txt`): `before: 95483 B CRLF 233`; `after: 97054 B CRLF 236 bare LF 0`; `tail kept: True`; `session 96 prefix lines: 1`; `focus-insert: ok`. Then `Drift check passed — SSOT loaded (160 MEUs, 12 phases), rendered regions match on-disk content`.
- H1-4 (`skip-basis-check.txt`): `skip-basis changes since row 0: []`.
- H1-5 (`source-read-h1-5.txt`): the template, and the newest handoff by mtime, which is the precedent itself (`2026-11-18-eval-describe-raw-bytes-handoff.md`, 56,285 B); `source-read: ok`.
- H1-6, before the handoff (`erh-d1235-yaml.txt`): `decision ids: D-1221 to D-1235 count 15`; `D-1235 parsed: ok; backslash in the new entry: none; CR 0`.
- D-1236, before the corrections (`erh-d1236-yaml.txt`): `decision ids: D-1221 to D-1236 count 16`; `D-1236 parsed: ok; backslash in the new entry: none; CR 0`.

### Commands Executed

```json
{"schema_version": "evidence.v1", "cwd": "P:/av-kit", "check_id": "erh-0-baseline", "command": "task.md row 0's Validation cell through pwsh: rtk proxy pwsh -NoProfile -File docs/execution/plans/2026-11-18-e2e-remote-host/baseline.ps1 *> C:/Temp/av-kit/e2e-remote-host/erh-baseline.txt; run twice, run 1 kept as erh-baseline-run1-ruff-e501.txt; receipts erh-baseline.txt, erh-home-before.txt, erh-hand-hashes.json", "scope": "Row 0: the baseline at a43cdb2, the anchors, the three issues, grouping row 96, the records and the plan-local selftests", "phase": "static", "exit_code": 0, "result": "pass", "tested_state": "HEAD a43cdb2 (baseline.sha) plus row 0", "output": "erh-baseline-run1-ruff-e501.txt: Found 24 errors; baseline step ruff-check-plan exit=1 (wrapped, then rerun). erh-baseline.txt: anchor lines moved: none; CI-E2E-FLEET-HOST-UNTRACKED: entries 1, status open, line 5805; CAPTURE-TEXT-PIXEL-2PX-MINIAIR: entries 1, status open, line 5846; E2E-HOVER-NO-POINTER-DEVICE: entries 1, status open, line 5886; spec files at HEAD: 29 without the skip files: 27; baseline-scope.json 33 paths; 13 absent; 8 foreign class; baseline-dirty.txt 19 paths, 0 foreign; baseline-skip-hashes.json 605 files; red-check selftest: 39 fixture(s) (13 positive, 26 negative), 0 wrong: []; eol-check selftest: 24 case(s), 0 wrong: []; identity selftest: 0 failure(s); baseline: all steps exit 0. erh-home-before.txt: check_home_path: ok files=2740 allowlisted=60 nul=31."}
```

```json
{"schema_version": "evidence.v1", "cwd": "P:/av-kit", "check_id": "erh-1-reproduction-red", "command": "pwsh -NoProfile -File C:/Temp/av-kit/e2e-remote-host/erh-row-1.ps1 (task.md row 1's Validation cell: zip-time.py on baseline.sha with offset -8, then pytest tests/tooling/test_e2e_remote.py with its exit code kept, red-check.py with --require for AC-1 to AC-15, AC-19 and AC-21, and the test file's SHA-256 recorded); receipts erh-zip-time.txt, erh-red.txt, erh-red.txt.exit, erh-red-check.txt, erh-test-sha-pre-d1235.txt", "scope": "AC-16 part 1 (the reproduction) and the Red of AC-1 to AC-15, AC-19 and AC-21 before the tool exists (D-1231)", "phase": "red", "exit_code": 0, "result": "pass", "tested_state": "HEAD a43cdb2 (baseline.sha) plus rows 0 and 1", "output": "erh-zip-time.txt: entries: 2993 distinct DOS times: 1; zip comment is the commit id: True; DOS time is dev-pc local time (within 2 s): True; seconds a host at UTC-8 reads the files after the commit: 10799. erh-red.txt: 174 AssertionError lines that the file under test does not exist yet (tools/e2e_remote.py 151, host-facts.ps1 16, run-e2e.ps1 2, one each for the other five host scripts); 174 failed in 9.69s. erh-red.txt.exit: 1. erh-red-check.txt: red-check: 1 receipt(s), 17 required test(s), 0 problem(s)."}
```

```json
{"schema_version": "evidence.v1", "cwd": "P:/av-kit", "check_id": "erh-2-3-green", "command": "pwsh -NoProfile -File C:/Temp/av-kit/e2e-remote-host/erh-row-2.ps1 (task.md row 2's cell: the test hash against erh-test-sha.txt, pytest with AC-14, AC-15, AC-19 and AC-21 deselected, ruff format --check and ruff check); pwsh -NoProfile -File C:/Temp/av-kit/e2e-remote-host/erh-row-3.ps1 (task.md row 3's cell: the test hash, pytest with AC-19 and AC-21 deselected, then tools/e2e_remote.py summarize on both hand reports into fresh folders); receipts erh-green-2.txt, erh-green-2-fmt.txt, erh-green-2-lint.txt, erh-green-3.txt, erh-sum-191358.txt, erh-sum-185348.txt, erh-sum-check.txt", "scope": "Green of the tool (row 2) and the host scripts (row 3); both hand reports summarized", "phase": "green", "exit_code": 0, "result": "pass", "tested_state": "HEAD a43cdb2 (baseline.sha) plus rows 0 to 3", "output": "erh-green-2.txt: 143 passed, 31 deselected in 15.05s. erh-green-2-fmt.txt: 2 files already formatted. erh-green-2-lint.txt: All checks passed! erh-green-3.txt: 170 passed, 4 deselected in 43.00s. erh-sum-check.txt: 191358: 232 228 ['AC-102.19', 'AC-102.20', 'AC-126.8', 'AC-82.6'] new 0; 185348: 220 12 known 4 new ['AC-152.21', 'AC-152.22', 'AC-152.23', 'AC-152.24', 'AC-155.10', 'AC-155.11', 'AC-155.15', 'AC-156.11'] (the app's own AC ids, foreign to this plan)."}
```

```json
{"schema_version": "evidence.v1", "cwd": "P:/av-kit", "check_id": "erh-4-stop", "command": "pwsh -NoProfile -File C:/Temp/av-kit/e2e-remote-host/erh-row-4.ps1 (task.md row 4's cell), first run; receipts erh-green-4-stop.txt, erh-row-4-run-stop.txt", "scope": "Row 4 first run: stopped on AC-21's scan of the test file's own CLIXML fixture; superseded by erh-4-green after D-1235", "phase": "green", "exit_code": 1, "result": "fail", "tested_state": "HEAD a43cdb2 (baseline.sha) plus rows 0 to 4, before D-1235", "output": "erh-green-4-stop.txt: test_ac_21_no_host_details_in_new_files failed on the CLIXML version string (four dotted numbers) at tests/tooling/test_e2e_remote.py:698; 1 failed, 173 passed in 36.86s."}
```

```json
{"schema_version": "evidence.v1", "cwd": "P:/av-kit", "check_id": "erh-4-green", "command": "uv run python C:/Temp/av-kit/e2e-remote-host/erh-d1235-edit.py (D-1235: the one literal split, by bytes, LF kept; ruff format --check and ruff check after); then pwsh -NoProfile -File C:/Temp/av-kit/e2e-remote-host/erh-row-4.ps1 (task.md row 4's cell unchanged: the test hash against erh-test-sha.txt, the full test file with no skip, the commands.md check, eol-check.py); receipts erh-d1235-edit.txt, erh-d1235-fmt.txt, erh-d1235-lint.txt, erh-test-sha-d1235.txt, erh-green-4.txt, erh-commands-check.txt, erh-eol-4.txt", "scope": "D-1235 and row 4: AC-1 to AC-15, AC-19, AC-21 Green with no deselection; AC-20 the D6 row; the run book", "phase": "green", "exit_code": 0, "result": "pass", "tested_state": "HEAD a43cdb2 (baseline.sha) plus rows 0 to 4", "output": "erh-d1235-edit.txt: byte-identical: True; old sha256: 0a7d58bc50813ef0ff79ea81833b3bab350fdaf013102b8627fa8d84fee3db7a; new sha256: d350a66b9c499245aae83e2d78451389462ade0aeaa12c362dad59641a2fe941; lines changed: 1; CR count: 0. erh-green-4.txt: 174 passed in 38.39s. erh-commands-check.txt: commands.md lines: 226 -> 227, row 206 starts | ui-electron-remote |, crlf only: True. erh-eol-4.txt: eol-check: 21 scope path(s), 0 problem(s)."}
```

```json
{"schema_version": "evidence.v1", "cwd": "P:/av-kit", "check_id": "erh-5-live-check", "command": "pwsh -NoProfile -File C:/Temp/av-kit/e2e-remote-host/erh-row-5.ps1 (task.md row 5's cell: tools/e2e_remote.py check --out erh-check-5.json, then the read-only host probe and host-details-scan.py on the new files and the plan folder); receipts erh-check-5.txt, erh-check-5.json, erh-host-probe-5.txt, erh-host-probe-5-check.txt, erh-host-details-5.txt", "scope": "AC-17: a real check against the second host (CHECK_AND_NAME); AC-21 row part", "phase": "runtime", "exit_code": 0, "result": "pass", "tested_state": "HEAD a43cdb2 (baseline.sha) plus rows 0 to 5", "output": "erh-check-5.txt: facts: ps=5.1.26100.9818 elevated=True; desktop: explorer=1 session=1 state=Active logonui=[]; busy: busy=0 runner_workers=0 own_orphans=0; task: exists=True state=Ready logon=Interactive runlevel=Limited limit_min=120 multiple=IgnoreNew; lock: holder=None launcher_marker=False; prereq: node=v26.13.0 uv=True vcruntime=True ffmpeg=True ffprobe=True free_gb=406.3; check: ok; exit 0. erh-host-probe-5-check.txt: probe after check, missing facts: []. erh-host-details-5.txt: host-details-scan: files=31 grown_pairs=0 bad=0."}
```

```json
{"schema_version": "evidence.v1", "cwd": "P:/av-kit", "check_id": "erh-6-live-run", "command": "pwsh -NoProfile -File C:/Temp/av-kit/e2e-remote-host/erh-row-6.ps1 (task.md row 6's cell: tools/e2e_remote.py run on baseline.sha, then the check of the run folder's summary.json and prepare-extract.json, then the read-only host probe); run once; receipts erh-run-6.txt, erh-run-6-check.txt, erh-run-6-dir.txt, erh-host-probe-6.txt, and the run folder r20261119T074154Z-a43cdb2 under C:/Temp/av-kit/e2e-remote", "scope": "AC-18 and AC-16 part 2: the full Electron E2E suite of a43cdb2 on the second host", "phase": "runtime", "exit_code": 0, "result": "pass", "tested_state": "HEAD a43cdb2 (baseline.sha) plus rows 0 to 6", "output": "erh-run-6.txt: summary: tests=232 expected=228 unexpected=4 flaky=0 skipped=0 spec_files=27 specs_checked=True playwright=1.64.1 duration_ms=1267731; known: AC-82.6, AC-102.19, AC-102.20 (capture-inbox.test.ts), AC-126.8 (settings.test.ts), the app's own ids; skip: capture-filmstrip-actions.test.ts, capture-import.test.ts; result: ok exit=0; released: r20261119T074154Z-a43cdb2; e2e-remote: ok exit=0 run=r20261119T074154Z-a43cdb2. erh-run-6-check.txt: tests 232 expected 228 unexpected 4 flaky 0 skipped 0 known ['AC-102.19', 'AC-102.20', 'AC-126.8', 'AC-82.6'] new [] spec_files 27 specs_checked True commit_offset_s 10799 mtime_skew_s 95 overlap []. erh-host-probe-6.txt: lock=False tree_marker=True bin=True; runs=True results_r=1 hand_copies=1; launcher=True tracked_marker=True, its sha256 equal to tools/e2e_host/run-e2e.ps1's."}
```

```json
{"schema_version": "evidence.v1", "cwd": "P:/av-kit", "check_id": "erh-7-8-h1-1-records", "command": "uv run python C:/Temp/av-kit/e2e-remote-host/erh-row-7-set.py and erh-row-7-grouping.py (the set file and grouping row 96, as LF bytes); pwsh -NoProfile -File C:/Temp/av-kit/e2e-remote-host/erh-row-7.ps1 (task.md row 7's cell: issue-resolve.py --expect-sha256 the row-0 register hash, issue_triage.py render and render --check, the register and grouping check, host-details-scan.py with two --grown pairs); run once; then erh-row-8.ps1 and erh-row-H1-1.ps1 (rows 8 and H1-1's cells); receipts erh-row-7-set.txt, erh-row-7-grouping.txt, erh-issue-resolve.txt, erh-issues-render.txt, erh-issues-render-check.txt, erh-register-check.txt, erh-host-details-7.txt, erh-hub-audit.txt, task-unchecked.txt", "scope": "AC-22 (the issue resolved, the render, grouping row 96), AC-21 row part, the hub (row 8) and H1-1", "phase": "static", "exit_code": 0, "result": "pass", "tested_state": "HEAD a43cdb2 (baseline.sha) plus rows 0 to 8 and H1-1", "output": "erh-issue-resolve.txt: decision logs read: 108 of 108; register sha256 before=2450ee1c6802051a165ee48bbf941d89b8263200e9aaa344e79f3ded9ee0c9e0; target sha256 after=533f5f92594ad15168827be79c0cbab1e28990e243bc00cad24d6142988a1858 CRLF=0 LF=5924; parsed fields changed: 5; issue-resolve: 0 problem(s). erh-issues-render.txt: Rendered known-issues.md: 35 lines. erh-issues-render-check.txt: OK: known-issues.md is up-to-date. erh-register-check.txt: other issues changed: [] changed keys: ['resolution_path', 'status', 'verification'] issue ok: True grouping lines changed: [133] row ok: True. erh-host-details-7.txt: host-details-scan: files=32 grown_pairs=2 bad=0. erh-hub-audit.txt: BUILD_PLAN.md unchanged: True references: []. task-unchecked.txt: unchecked implementation rows: []."}
```

```json
{"schema_version": "evidence.v1", "cwd": "P:/av-kit", "check_id": "erh-d1236-red-green", "command": "pwsh -NoProfile -File C:/Temp/av-kit/e2e-remote-host/erh-fix1-red.ps1 (pytest on the seven new tests by -k against the unfixed tool, its exit kept, then red-check.py with --require for the five new test functions); after the fix, pwsh -NoProfile -File C:/Temp/av-kit/e2e-remote-host/erh-fix1-green.ps1 (the full test file with no skip, ruff format --check and ruff check on the tool and the tests); uv run python C:/Temp/av-kit/e2e-remote-host/fix1/test-additions-only.py; uv run python C:/Temp/av-kit/e2e-remote-host/erh-d1236-yaml.py; receipts erh-fix1-red.txt, erh-fix1-red.txt.exit, erh-fix1-red-check.txt, erh-fix1-green.txt, erh-fix1-fmt.txt, erh-fix1-lint.txt, erh-fix1-test-additions.txt, erh-test-sha-pre-fix1.txt, erh-test-sha.txt, erh-d1236-yaml.txt", "scope": "D-1236: the execution review's round-1 findings F1 (AC-2, AC-13), F2 (AC-12) and F3 (AC-9), Red then Green", "phase": "green", "exit_code": 0, "result": "pass", "tested_state": "HEAD a43cdb2 (baseline.sha) plus rows 0 to 8, H1-1 to H1-6b and D-1236", "output": "erh-fix1-red.txt: 7 failed, 174 deselected in 2.64s, each by assertion (assert 0 == 11; assert 0 == 10; assert 'uncaught OSError: fixture disk full' == 34; assert 0 == 33 twice; the also refused line missing twice). erh-fix1-red-check.txt: red-check: 1 receipt(s), 5 required test(s), 0 problem(s). erh-fix1-green.txt: 181 passed in 49.43s. erh-fix1-fmt.txt: 2 files already formatted. erh-fix1-lint.txt: All checks passed! erh-fix1-test-additions.txt: remainder sha256 d350a66b9c499245aae83e2d78451389462ade0aeaa12c362dad59641a2fe941; additions only: True. erh-test-sha.txt: 565b4ee6fd0562c2728e0ab21347b5c06255dff54765d6c5c035319d0cad338a. erh-d1236-yaml.txt: decision ids: D-1221 to D-1236 count 16; D-1236 parsed: ok."}
```

```json
{"schema_version": "evidence.v1", "cwd": "P:/av-kit", "check_id": "erh-6-live-run-fix1", "command": "pwsh -NoProfile -File C:/Temp/av-kit/e2e-remote-host/erh-row-6-fix1.ps1 (task.md row 6's cell with the receipt names given a -fix1 suffix and TMP and TEMP set to the receipts folder's tmp: tools/e2e_remote.py run on baseline.sha, then the check of the run folder's summary.json and prepare-extract.json, then the read-only host probe); run once; receipts erh-run-6-fix1.txt, erh-run-6-fix1-check.txt, erh-run-6-dir.txt, erh-host-probe-6-fix1.txt, and the run folder r20261119T084412Z-a43cdb2 under C:/Temp/av-kit/e2e-remote", "scope": "S13 after D-1236: AC-18 and AC-16 part 2 again on the final tool", "phase": "runtime", "exit_code": 0, "result": "pass", "tested_state": "HEAD a43cdb2 (baseline.sha) plus rows 0 to 8 and D-1236", "output": "erh-run-6-fix1.txt: summary: tests=232 expected=228 unexpected=4 flaky=0 skipped=0 spec_files=27 specs_checked=True playwright=1.64.1 duration_ms=1277136; known: AC-82.6, AC-102.19, AC-102.20 (capture-inbox.test.ts), AC-126.8 (settings.test.ts), the app's own ids; skip: capture-filmstrip-actions.test.ts, capture-import.test.ts; result: ok exit=0; released: r20261119T084412Z-a43cdb2; e2e-remote: ok exit=0 run=r20261119T084412Z-a43cdb2. erh-run-6-fix1-check.txt: tests 232 expected 228 unexpected 4 flaky 0 skipped 0 known ['AC-102.19', 'AC-102.20', 'AC-126.8', 'AC-82.6'] new [] spec_files 27 specs_checked True commit_offset_s 10799 mtime_skew_s -3645 overlap []. erh-host-probe-6-fix1.txt against erh-host-probe-6.txt: results_r=2 (was 1), free_gb 402.2 (was 404.2); the lock, launcher, task and session lines unchanged."}
```

```json
{"schema_version": "evidence.v1", "cwd": "P:/av-kit", "check_id": "erh-h1-2-session-gate", "command": "pwsh -NoProfile -File C:/Temp/av-kit/e2e-remote-host/erh-row-H1-2.ps1 (task.md row H1-2's Validation cell: rtk proxy pwsh -NoProfile -File docs/execution/plans/2026-11-18-e2e-remote-host/session-gate.ps1 *> C:/Temp/av-kit/e2e-remote-host/erh-gate-h1.txt), one run after D-1236 and S13, stamp 20261119-040827, after a load probe read cpu load 40; step receipts erh-D6-<step>.txt; the first gate (stamp 20261119-031016) is superseded and its receipts kept in the pre-fix1 folder", "scope": "H1-2 and AC-23: the session gate from identity-before to identity-after: task-contract, scope-paths, line-endings, home-path, two selftests, py-format, py-lint, json-valid, erh-tests, erh-summary-191358, erh-summary-185348, erh-zip-time, host-load, py-tests, remote-evidence, issues-render-check and state-render", "phase": "full", "exit_code": 0, "result": "pass", "fresh": true, "snapshot": false, "tested_state": "a43cdb24f97af6f10498fa70abb5ada4b0882835+ea13c262292537db7c1df492a9c0d91be1af978e43e615fe46ce0466a01da1db", "output": "erh-gate-h1.txt: gate stamp: 20261119-040827; every run step exit=0; skipped with reasons: py-types, ui-types/ui-lint/ui-tests/ui-build/ui-electron, mcp-types/mcp-tests/mcp-build, openapi (every packages/, ui/, native/ and server file keeps its baseline-skip-hashes.json hash, H1-4) and mcp-audit (no server file changes; a network run); tested_state before and after equal; session-gate: all steps exit 0. erh-D6-task-contract.txt: OK: 26 row(s); 24 row(s) fully checked; 2 row(s) exempt (view_file): H1-5, H2-1. erh-D6-scope-paths.txt: changed paths: 38 outside scope: []; read-never-changed files: 8 mismatch: [] baseline-dirty hash mismatch: []; foreign class (coordinator, printed only): 8 changed: [] row-0 hash moved: []; head moved (S4): False. erh-D6-line-endings.txt: eol-check: 21 scope path(s), 0 problem(s). erh-D6-home-path.txt: check_home_path: ok files=2754 allowlisted=60 nul=31. erh-D6-py-format.txt: 9 files already formatted. erh-D6-py-lint.txt: All checks passed! erh-D6-json-valid.txt: example keys: 11 load_config ok, config keys match: True; known list type: dict entries: 2. erh-D6-erh-tests.txt: test_sha256 equal: True (565b4ee6fd0562c2728e0ab21347b5c06255dff54765d6c5c035319d0cad338a); 181 passed in 40.32s; skip found: False. erh-D6-erh-summary-191358.txt: tests 232 expected 228 unexpected 4, new [], summary exit 0 counts ok: True. erh-D6-erh-summary-185348.txt: tests 232 expected 220 unexpected 12, 8 new, summary exit 40 counts ok: True. erh-D6-erh-zip-time.txt: seconds a host at UTC-8 reads the files after the commit: 10799. erh-D6-host-load.txt: samples [39, 30, 15, 8, 31] mean=24.6; host-load: 24.6 %. erh-D6-py-tests.txt: 3300 passed, 37 warnings in 308.29s. erh-D6-remote-evidence.txt: run folder name: r20261119T084412Z-a43cdb2 summary exit: 0 files hashed now: 10 recorded: 10; remote-evidence mismatch: []. erh-D6-issues-render-check.txt: OK: known-issues.md is up-to-date. erh-D6-state-render.txt: Drift check passed. erh-D6-identity-after.txt: tested_state a43cdb24f97af6f10498fa70abb5ada4b0882835+ea13c262292537db7c1df492a9c0d91be1af978e43e615fe46ce0466a01da1db."}
```

```json
{"schema_version": "evidence.v1", "cwd": "P:/av-kit", "check_id": "erh-h1-3-h1-5-closeout", "command": "uv run python C:/Temp/av-kit/e2e-remote-host/erh-focus-insert.py (the Session 96 entry on top of .agent/context/current-focus.md, by bytes, CRLF kept, refused if a 'Current priority: Session 96' line exists); pwsh -NoProfile -File C:/Temp/av-kit/e2e-remote-host/erh-row-H1-3.ps1 (rtk proxy uv run python tools/meu_status.py render --check); pwsh -NoProfile -File C:/Temp/av-kit/e2e-remote-host/erh-row-H1-4.ps1 (task.md row H1-4's skip-basis check); uv run python C:/Temp/av-kit/e2e-remote-host/erh-source-read.py (H1-5); uv run python C:/Temp/av-kit/e2e-remote-host/erh-d1235-yaml.py (D-1235 into the plan's YAML); receipts erh-focus-insert.txt, erh-render-check.txt, skip-basis-check.txt, source-read-h1-5.txt, erh-d1235-yaml.txt", "scope": "H1-3 (current focus and the state render), H1-4 (the skip basis, S9), H1-5 (the template and exemplar read) and D-1235 recorded in the plan", "phase": "static", "exit_code": 0, "result": "pass", "tested_state": "the H1-2 state; current-focus.md and the plan are outside identity.py's inputs, and identity.py --state-only re-derived the same state after these steps", "output": "erh-focus-insert.txt: before: 95483 B CRLF 233; after: 97054 B CRLF 236 bare LF 0; tail kept: True; session 96 prefix lines: 1; focus-insert: ok. erh-render-check.txt: Drift check passed - SSOT loaded (160 MEUs, 12 phases), rendered regions match on-disk content. skip-basis-check.txt: skip-basis changes since row 0: []. source-read-h1-5.txt: TEMPLATE.md 6703 B; 2026-11-18-eval-describe-raw-bytes-handoff.md 56285 B (the newest by mtime and the precedent); source-read: ok. erh-d1235-yaml.txt: decision ids: D-1221 to D-1235 count 15; D-1235 parsed: ok; backslash in the new entry: none; CR 0."}
```

```json
{"schema_version": "evidence.v1", "cwd": "P:/av-kit", "check_id": "erh-h1-rerun-d1236", "command": "pwsh -NoProfile -File C:/Temp/av-kit/e2e-remote-host/erh-row-H1-1.ps1 (H1-1); uv run python C:/Temp/av-kit/e2e-remote-host/fix1/focus-update-fix1.py r20261119T084412Z-a43cdb2 (the Session 96 line updated in place, by bytes, CRLF kept, refused unless exactly one such line holds each phrase once); pwsh -NoProfile -File C:/Temp/av-kit/e2e-remote-host/erh-row-H1-3.ps1; pwsh -NoProfile -File C:/Temp/av-kit/e2e-remote-host/erh-row-H1-4.ps1; receipts task-unchecked.txt, erh-focus-update-fix1.txt, erh-render-check.txt, skip-basis-check.txt", "scope": "H1-1, H1-3 and H1-4 again after D-1236, S13 and the second gate", "phase": "static", "exit_code": 0, "result": "pass", "tested_state": "the second H1-2 state; current-focus.md is outside identity.py's inputs", "output": "task-unchecked.txt: unchecked implementation rows: []. erh-focus-update-fix1.txt: before: 97054 B CRLF 236; after: 97387 B CRLF 236 bare LF 0; line changed: 1; other lines kept: True; focus-update: ok. erh-render-check.txt: Drift check passed - SSOT loaded (160 MEUs, 12 phases), rendered regions match on-disk content. skip-basis-check.txt: skip-basis changes since row 0: []."}
```

### Quality Gate Results

| Step | Result (receipt) |
|------|------------------|
| Gate | `session-gate: all steps exit 0` (`erh-gate-h1.txt`, stamp `20261119-040827`, one run after D-1236 and S13); every run step `exit=0`. The first gate, stamp `20261119-031016`, also passed and is superseded |
| Identity | `tested_state a43cdb24f97af6f10498fa70abb5ada4b0882835+ea13c262292537db7c1df492a9c0d91be1af978e43e615fe46ce0466a01da1db`, equal before and after (`erh-D6-identity-before.txt`, `erh-D6-identity-after.txt`) |
| Task contract | `OK: 26 row(s)`; `24 row(s) fully checked`; `2 row(s) exempt (view_file): H1-5, H2-1` (`erh-D6-task-contract.txt`) |
| Scope | `changed paths: 38 outside scope: []` (36 at the first gate; the handoff and `current-focus.md` were written after it); `read-never-changed files: 8 mismatch: [] baseline-dirty hash mismatch: []`; `foreign class (coordinator, printed only): 8 changed: [] row-0 hash moved: []`; `head moved (S4): False` (`erh-D6-scope-paths.txt`) |
| Line endings | `eol-check: 21 scope path(s), 0 problem(s)` (`erh-D6-line-endings.txt`) |
| Home path | `check_home_path: ok files=2754 allowlisted=60 nul=31` (`erh-D6-home-path.txt`) |
| Selftests | red-check `39 fixture(s) (13 positive, 26 negative), 0 wrong`; eol-check `24 case(s), 0 wrong` (`erh-D6-red-check-selftest.txt`, `erh-D6-eol-check-selftest.txt`) |
| Ruff | `9 files already formatted`; `All checks passed!` (`erh-D6-py-format.txt`, `erh-D6-py-lint.txt`) |
| JSON | `example keys: 11 load_config ok, config keys match: True`; `known list type: dict entries: 2` (`erh-D6-json-valid.txt`) |
| Tests | `181 passed in 40.32s`; the test file's hash equals `erh-test-sha.txt` (the D-1236 hash `565b4ee6…`); `skip found: False` (`erh-D6-erh-tests.txt`) |
| Hand reports | 191358: `tests 232 expected 228 unexpected 4`, `new []`, `summary exit 0 counts ok: True`; 185348: `tests 232 expected 220 unexpected 12`, eight new, `summary exit 40 counts ok: True` (`erh-D6-erh-summary-191358.txt`, `erh-D6-erh-summary-185348.txt`) |
| Reproduction | `seconds a host at UTC-8 reads the files after the commit: 10799` (`erh-D6-erh-zip-time.txt`) |
| Host load | samples `[39, 30, 15, 8, 31]`, `mean=24.6`, `host-load: 24.6 %` (`erh-D6-host-load.txt`) |
| Python tests | `3300 passed, 37 warnings in 308.29s` (`erh-D6-py-tests.txt`) |
| Remote evidence | `files hashed now: 10 recorded: 10`; `remote-evidence mismatch: []`: the tool and its nine host files are the bytes the S13 run `r20261119T084412Z-a43cdb2` ran (`erh-D6-remote-evidence.txt`) |
| Registers | `OK: known-issues.md is up-to-date` (`erh-D6-issues-render-check.txt`); the state render's drift check passed (`erh-D6-state-render.txt`) |
| Skipped | `py-types`, `ui-types/ui-lint/ui-tests/ui-build/ui-electron`, `mcp-types/mcp-tests/mcp-build`, `openapi`: every file under `packages/`, `ui/`, `native/` and the server keeps its row-0 hash (H1-4), and the full E2E evidence is row 6 on the second host; `mcp-audit`: no server file changes, and it is a network run |

---

## Changed Files

Counts are added and removed lines against `HEAD` `a43cdb2` (`git diff --numstat --ignore-cr-at-eol`). A new file's count is its line count. Line endings were measured as bytes (the gate's `line-endings` step, `erh-D6-line-endings.txt`).

| File | Change | Added / removed | Line endings |
|------|--------|-----------------|--------------|
| `tools/e2e_remote.py` | new: the tool, five subcommands (row 2); the three review corrections (D-1236) | 1,396 lines | LF, ASCII |
| `tools/e2e_host/host-facts.ps1` | new (row 3) | 281 lines | LF, ASCII |
| `tools/e2e_host/host-lock.ps1` | new (row 3) | 261 lines | LF, ASCII |
| `tools/e2e_host/host-prepare.ps1` | new (row 3) | 229 lines | LF, ASCII |
| `tools/e2e_host/host-start.ps1` | new (row 3) | 274 lines | LF, ASCII |
| `tools/e2e_host/host-status.ps1` | new (row 3) | 268 lines | LF, ASCII |
| `tools/e2e_host/host-release.ps1` | new (row 3) | 77 lines | LF, ASCII |
| `tools/e2e_host/run-e2e.ps1` | new: the tracked launcher (row 3) | 120 lines | LF, ASCII |
| `tools/e2e_host/e2e-host.example.json` | new: made-up values that load clean (row 2) | 13 lines | LF, ASCII |
| `tools/e2e_host/known-failures.json` | new: the label `mini-air`, 4 known entries and 2 skipped specs (row 2) | 12 lines | LF |
| `tests/tooling/test_e2e_remote.py` | new: 174 tests for AC-1 to AC-15, AC-19 and AC-21 (row 1); one literal split under D-1235 (row 4); 7 regression tests added under D-1236 | 2,310 lines | LF, ASCII |
| `.agent/docs/e2e-remote-host.md` | new: the run book (row 4); `summary.txt`, `lock_kept` and the failed release (D-1236) | 259 lines | LF |
| `.agent/docs/commands.md` | the `ui-electron-remote` row after `:205` (row 4) | +1 / -0 | CRLF kept |
| `.agent/context/known-issues.yaml` | the issue resolved (`issue-resolve.py`, row 7) | +5 / -4 | LF kept |
| `.agent/context/known-issues.md` | `issue_triage.py render` (row 7) | +3 / -4 | LF |
| `.agent/context/grouping/2026-11-18-e2e-remote-host-session-grouping.md` | row 96 (`:133`): `executed (Session 96)` (row 7) | +1 / -1 | LF kept |
| `.agent/context/current-focus.md` | the Session 96 entry (H1-3) | +3 / -0 | CRLF kept |
| `.agent/context/handoffs/2026-11-18-e2e-remote-host-handoff.md` | this handoff (H1-6) | new | LF |
| `docs/execution/plans/2026-11-18-e2e-remote-host/` | the plan (D-1235 and D-1236 added to its YAML in execution) and task (row marks), the plan-time scripts (`zip-time.py`, `host-probe.ps1`, `host-probe-run.py`, `host-details-scan.py`), the row-0 copies (`red-check.py`, `identity.py`, `eol-check.py`, `issue-resolve.py`, `host-load.ps1`), `baseline.ps1` and its records, and `session-gate.ps1` | new folder | LF |

The plan review (`.agent/context/handoffs/2026-11-18-e2e-remote-host-plan-critical-review.md`) is untracked and part of this session's commit; this session did not write it.

**Read, never changed.** The hand scripts and both hand reports in the coordinator's research folder keep their row-0 SHA-256 values (`erh-hand-hashes.json`; the gate's `scope-paths` step). `docs/BUILD_PLAN.md` keeps its row-0 bytes (row 8).

**The foreign class** (`.agent/model-registry.local.json`, `.claude/agents/*.md`, `.cursor/agents/*.md`) belongs to the coordinator: the gate's `scope-paths` step printed `foreign class (coordinator, printed only): 8 changed: [] row-0 hash moved: []`, and this session saw no change in it.

**Outside the repository.** The untracked config `<HOME>/.config/av-kit/e2e-host.json` (11 keys). On the host, by kind only: the content-addressed script set in `bin\`; each run's folders in `runs\` and `results\` (`tree_marker=True`; `results_r=1` after row 6 and `results_r=2` after S13); the tracked launcher at the root launcher path (its SHA-256 equals `tools/e2e_host/run-e2e.ps1`'s, `tracked_marker=True`); the hand launcher renamed beside it with its kept hash prefix `5ab99494` (`hand_copies=1`); the lock taken and released (`lock=False`); and the build caches noted under Departures. Free disk fell from 406.3 to 404.2 GB, then to 402.2 GB. Nothing was stopped, installed or registered, and the task is unchanged (`erh-host-probe-6.txt` against `erh-host-probe-5.txt`; `erh-host-probe-6-fix1.txt` against `erh-host-probe-6.txt`).

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
| F1 | High | no | behavior | PINNED_SSH / NAMED_REFUSAL: `release_lock` swallowed a final release failure, so a run or collect whose host-key check or connection failed only at `host-release.ps1` exited 0 with the host lock still held (blocking at round 1). Corrected under D-1236: a retained-lock refusal with exit 11 or 10, one attempt, the summary kept, and a secondary release failure listed under `also` (`tools/e2e_remote.py:904`, `:1108`, `:1235`, `:1251`). | `tools/e2e_remote.py:908`; `tools/e2e_remote.py:1077` (round-1 lines) | Keep the regressions at `tests/tooling/test_e2e_remote.py:765` and `:1745`. | fixed |
| F2 | Medium | no | behavior | NO_PARTIAL: `summarize --out` checked only `summary.json`, so an existing `summary.txt` was overwritten. Corrected under D-1236: `SUMMARY_NAMES` holds both destinations and summarize and collect refuse 33 when either exists (`tools/e2e_remote.py:864`, `:1049`, `:1321`). | `tools/e2e_remote.py:1284`; `tools/e2e_remote.py:863` (round-1 lines) | Keep the regressions at `tests/tooling/test_e2e_remote.py:1649` and `:1661`. | fixed |
| F3 | Medium | no | behavior | NAMED_REFUSAL: an OSError on `polls.jsonl` escaped `_poll` as a traceback with exit 1. Corrected under D-1236: it maps to `receipt-write-failed` 34, keeps the lock and names collect and release (`tools/e2e_remote.py:981`). | `tools/e2e_remote.py:959`; `tools/e2e_remote.py:1200` (round-1 lines) | Keep the regression at `tests/tooling/test_e2e_remote.py:1256`. | fixed |

- **The loop.** Ledger `erh-execution-2026-11-18-e2e-remote-host`, mode execution, budget 6, tokens off, 2 of 6 rounds used, reviewer `codex-independent-reviewer`, dispatched by the coordinator (`C:/Temp/av-kit/erh-exec-begin.txt`).
  - Round 1: `changes_required`, three findings (F1 High and blocking at that round, F2 and F3 Medium and non-blocking), `intent_achieved=partial`. Verdict file `C:/Temp/av-kit/dispatch/erh-exec-r1/final.json`; report `C:/Temp/av-kit/erh-exec-review-round-1.md`; console `C:/Temp/av-kit/erh-exec-console-r1.txt`.
  - Round 2: `approved`, F1, F2 and F3 `open` to `fixed`, no new findings, `intent_achieved=yes`. Verdict file `C:/Temp/av-kit/dispatch/erh-exec-r2/final.json`; console `C:/Temp/av-kit/erh-exec-console-r2.txt`.
- **The canonical review.** `.agent/context/handoffs/2026-11-18-e2e-remote-host-implementation-critical-review.md`, rolling, at round 2; byte-identical to `C:/Temp/av-kit/erh-exec-review-round-2.md` (54,191 B, SHA-256 `d341b7a815b5ec32e37223f1ad22818be9f23e257149fed6e1e32459baeb5397`).
- **The reviewer's own checks (round 2).** Its targeted run read 181 passed (35.93 s); its ten fault probes covered final release in run and collect, cleanup under a primary refusal, poll open and write errors, and both existing summary destinations; its offline summarize of S13 reproduced 232 / 228 / 4 known with no new failure; its EOL, triage render and identity checks passed.
- **Receipts.** H1-7a: `OK: review_mode=execution; round 2 of 6; verdict=approved; open findings=0` (`review-state-check.txt`, `review-state.json`). H1-7b: `OK: approved at round 2 of 6, 0 open blocking findings` (`exec-review.txt`).

### Verdict

`approved` at round 2 of 6: F1, F2 and F3 fixed, no new findings. The reviewer's `tested_state` `a43cdb24f97af6f10498fa70abb5ada4b0882835+ea13c262292537db7c1df492a9c0d91be1af978e43e615fe46ce0466a01da1db` equals the gate 20261119-040827 value.

---

## Deferred Items

| Item | Kind | Deferred-to | Basis |
|------|------|-------------|-------|
| The four known failures on the mini-air (two register issues) | follow-up | Session 97 `e2e-host-parity` | Grouping §3; they stay `open`, and a run exits 0 with them only while they are |
| `check --out` leaves an empty staging folder beside its output file | observation | a later session | `tools/e2e_remote.py:1276` makes the stage folder with `tempfile.mkdtemp(..., dir=out.parent)` and does not remove it; row 5 left `erh-check-5.json.stage-<random>/stage/bin/<set>/`, empty, in the receipts folder. Not fixed here: the round-1 review did not raise it, and D-1236 is limited to its three findings |
| A CI runner for the host | out-of-scope | — | Plan §Out of Scope |
| Commit and push | out-of-scope | — | Only on Mat's direction (H2-5) |

### Departures and their basis

- **The plan and task hashes.** The plan's sha256 moved from the reviewed `8a301a7f…cd3` to `82548e628895e168675e97803e796903002212a34054de21592b36b200418d74` when the coordinator wrote the execution approval into the Status line; the coordinator's brief states that line is the only change after the review. At H1-6 this session added D-1235 to the plan's YAML decision log (`erh-d1235-yaml.txt`: `plan sha256 before: 82548e628895e168675e97803e796903002212a34054de21592b36b200418d74`, `plan sha256 after: 289f3476f73286950de93c2f2efbc2d9d05c92b5e42f1c97661b817096fe2b9e`). task.md was `4036d3e9…b870` at the review and has changed only by its row marks. Neither file is an `identity.py` input.
- **Row 0 ran twice.** The first run (`erh-baseline-run1-ruff-e501.txt`, kept) stopped at `baseline step ruff-check-plan exit=1`: 24 E501 lines in the plan-local copies. `red-check.py` took Session 95's wrapped body, and one line each was rewrapped in `identity.py` and `issue-resolve.py` (formatting only; their selftests pass), then row 0 ran again (`erh-ruff-wrap.txt`).
- **Test fixes before the hash.** Before the Red hash was recorded, the test file was corrected so that each test failed by its own assertion (`erh-fix-test-1.py`); no assertion was weakened, and the hash in `erh-test-sha-pre-d1235.txt` is the file as it stood at Red.
- **D-1235, an S3 exception (row 4).** Row 4's first run failed one test, `test_ac_21_no_host_details_in_new_files`, which scans every new tracked file for an IPv4 literal: it found the CLIXML version string, four dotted numbers, in the test file's own AC-2 noise fixture (`test_e2e_remote.py:698`; `erh-green-4-stop.txt`: `1 failed, 173 passed in 36.86s`). The coordinator ruled option A under Mat's hand-over (D-1235, `resolution: autonomous`, no M hit): that one string literal was split into two adjacent parts joined by `+`. `erh-d1235-edit.txt`: `byte-identical: True` (the evaluated literal before and after), `lines changed: 1`, `CR count: 0`. No assertion, regex or runtime byte changed, so neither test is weaker. The test file's hash moved from `0a7d58bc50813ef0ff79ea81833b3bab350fdaf013102b8627fa8d84fee3db7a` to `d350a66b9c499245aae83e2d78451389462ade0aeaa12c362dad59641a2fe941` (`erh-test-sha-d1235.txt`); `erh-test-sha.txt` holds the new one, and the gate's `erh-tests` step compares against it. Row 4 then passed: `174 passed in 38.39s`.
- **D-1236, the test file after Red (review corrections).** The execution review's round 1 returned `changes_required` with F1 (High, blocking, AC-2), F2 and F3 (Medium). The coordinator ruled the fix under Mat's hand-over (D-1236, `resolution: autonomous`, `class: two-way`, `mandatory: none`). The test file therefore changed after Red, for the review corrections only: seven tests and one helper were added, and no existing line changed (`erh-fix1-test-additions.txt`: `additions only: True`). Its hash moved from `d350a66b9c499245aae83e2d78451389462ade0aeaa12c362dad59641a2fe941` (kept in `erh-test-sha-pre-fix1.txt`) to `565b4ee6fd0562c2728e0ab21347b5c06255dff54765d6c5c035319d0cad338a`; `erh-test-sha.txt` holds the new one, and the gate's `erh-tests` step compares against it. The plan's sha256 moved from `289f3476f73286950de93c2f2efbc2d9d05c92b5e42f1c97661b817096fe2b9e` to `3af2eb2f4fc045771386584925851fed28dddbf2a5339e3be5696c5c69b4e7a6` when D-1236 was added to its YAML (`erh-d1236-yaml.txt`: `decision ids: D-1221 to D-1236 count 16`; `D-1236 parsed: ok`).
- **D-1236 beyond the coordinator's list.** Two choices are this session's own. First, `collect` refusing on an existing `summary.txt` has its own regression test (`test_e2e_remote.py:1661`), because `collect` writes the same two receipts as `summarize --out`. Second, a failed release at the end of `run` or `collect` prints a release-only hint (`_release_hint`, `tools/e2e_remote.py:934`) rather than the poll hint that names `collect` first: the summary is already written then, so `collect` would refuse 33 `receipt-exists`, and only `release` is the next step.
- **Host-side forms.** `host-prepare.ps1` extracts with `[IO.Compression.ZipFile]::ExtractToDirectory` and hashes with `[Security.Cryptography.SHA256]` where the plan names `Expand-Archive` and `Get-FileHash`: both are in .NET on Windows PowerShell 5.1, work under the host's outer `powershell -c`, and need no module load. The launcher prints its one JSON line (`reason: finished`, its exit and a note) as the other scripts do, though the task, not the tool, reads its outcome from `DONE`.
- **Build caches outside the root.** The host build (`npm ci`, `uv sync`) uses the host account's own package caches in its profile, as the hand setup did; nothing else is written outside the root.
- **The plan-folder bytecode.** A plan-time Python load at 01:02 left a `__pycache__` in the plan folder; it was this session's own bytecode and was deleted on the coordinator's word. Every later Python call ran with `PYTHONDONTWRITEBYTECODE=1`.
- **TMP and TEMP on rows 5 and 6.** The row wrappers set the environment header but not `TMP` and `TEMP`; rows 1 to 4 set them in their own cells, rows 5 and 6 ran with the default temporary folder. From row 7 on, the wrappers set both to the receipts folder's `tmp`.
- **Scratch scripts.** Each row's Validation cell was copied verbatim into a `.ps1` file after an environment header and run with `pwsh -NoProfile -File`. The edits rows name were made by byte-level Python scripts in the receipts folder, which keep each file's line endings.
- **The session gate's shape.** `session-gate.ps1` is Session 95's gate adapted to this plan's §Session gate. Before the run, a wiring probe compiled each of its inline Python checks and dry-ran the scope check. The gate ran once, stamp `20261119-031016`, and passed; after D-1236 and S13 it ran once more, stamp `20261119-040827`, and passed (Quality Gate Results).

### Execution notes

- **The decisions.**

  | Id | What was decided |
  |---|---|
  | D-1221 | A: `tools/e2e_remote.py` with five subcommands, its PowerShell 5.1 host scripts in `tools/e2e_host/` and its tests; handed to the agent under Mat's 2026-11-18 words. |
  | D-1222 | A: the untracked config with strict keys, overridable by `--config` or `AVKIT_E2E_HOST_CONFIG`; a tracked example. |
  | D-1223 | A: check and name; install nothing; start the existing task, never change it. |
  | D-1224 | A: refuse and stop nothing on a busy or locked host. |
  | D-1225 | A: only the tracked known list for the host's label, each entry bound to an open issue (`mandatory: M-3`, decided by its recommendation under the hand-over). |
  | D-1226 | Scripts reach the host by `scp -r` into a content-addressed set folder and run by `-File` with id arguments; outcomes from the JSON line. |
  | D-1227 | The host layout: the lock, `bin\`, `runs\`, `results\`, the tracked launcher and the renamed hand launcher; the run id form. |
  | D-1228 | The zip comment, the hashes and the tree markers bind the commit; the mtimes are measured and reset before the build. |
  | D-1229 | The gate's steps and skips. |
  | D-1230 | The closed table of exits and reasons. |
  | D-1231 | The Red: `zip-time.py` first, then the test file, each test asserting its target exists. |
  | D-1232 | The receipt folders and loop ids. |
  | D-1233 | The register is updated by `issue-resolve.py`, bound to the row-0 hash. |
  | D-1234 | The run book and the `ui-electron-remote` row. |
  | D-1235 | Execution: split the AC-2 fixture literal so AC-21's scan does not read a version string as an address; the coordinator's ruling, `resolution: autonomous`, no M hit. |
  | D-1236 | Execution: fix the execution review's round-1 findings F1 to F3 with regression tests, no assertion weakened; the coordinator's ruling under Mat's hand-over, `resolution: autonomous`, `class: two-way`, no M hit. |

- **Processes.** No process was stopped on this PC or on the host. On this PC the session started only `pwsh`, `uv`, `python`, `ssh` and `scp` children of its own rows. On the host, the tool's only action on the task was `Start-ScheduledTask` on the existing task.
- **Data.** No row read Mat's app data, settings, downloads or models, here or on the host. No model call; the only network use was `ssh` and `scp` to the configured host.

---

## Decision Log

None.

---

## History

| Event | Date | Agent | Detail |
|-------|------|-------|--------|
| Created | 2026-11-19 | claude-code-local (Claude Opus 5.5) | Handoff after rows 0 to 8, the H1-2 gate and H1-3 to H1-5 |
| Updated | 2026-11-19 | claude-code-local (Claude Opus 5.5) | The execution review's round-1 findings F1 to F3 fixed under D-1236; row 6 run again on the final tool (S13); H1-1 to H1-4 run again with a fresh gate |
| Updated | 2026-11-19 | claude-code-local (Claude Opus 5.5) | Codex Validation Report filled from the execution review (round 1 changes_required, round 2 approved); H1-6 to H1-6b run again |
