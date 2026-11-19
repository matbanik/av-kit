---
project: "2026-11-18-e2e-remote-host"
date: "2026-11-18"
source: "grouping .agent/context/grouping/2026-11-18-e2e-remote-host-session-grouping.md §3 Session 96; issue CI-E2E-FLEET-HOST-UNTRACKED (D-1212)"
meus: []
status: "draft"
template_version: "2.3"
grouping_source: ".agent/context/grouping/2026-11-18-e2e-remote-host-session-grouping.md"
---

# Implementation Plan: run the full E2E suite on the second Windows host through tracked tooling

> **Project**: `2026-11-18-e2e-remote-host`
> **Build Plan Section(s)**: none. This is E2E runner tooling with no MEU (triage D-1212; no product change, D-1132), as in Sessions 83, 90 and 95.
> **Status**: said to execute (USER_EXPLICIT 2026-11-18 "proceed with the next session prompt orchestration here like you did the others", with USER_EXPLICIT 2026-11-18 "There is mini-air 12 windows pc that could be used to run the E2E tests rather than running them directly on this system"). `plan_to_exec_gate: human`: those messages are the execution approval once the plan review approves and no STOP item is open; the plan review was approved at round 2 after F1 was fixed (.agent/context/handoffs/2026-11-18-e2e-remote-host-plan-critical-review.md), and no STOP item is open. Session 96 is the first of the two sessions of the 2026-11-18 E2E-host grouping; Session 97 (`e2e-host-parity`) runs its acceptance run through this session's tooling.

---

## Goal

**Goal anchor:** a coordinator on the dev PC runs `uv run python tools/e2e_remote.py run <commit>`, and the tool sends a `git archive` of that commit to the second Windows host (the mini-air) over SSH with the pinned host key, builds it there, starts the full Electron E2E suite through the host's Interactive-logon scheduled task in the signed-in desktop session, polls for `DONE`, copies `meta.txt`, `specs.txt`, `report.json` and the logs back under `C:/Temp/av-kit/e2e-remote/<run-id>/`, and writes a summary that is read from `report.json` only. It refuses, with a named reason and a non-zero exit, when nobody is signed in or only session 0 is, when the desktop is locked, when the host is busy (a `zvci` test process, another av-kit run's lock, or the task already running), when a prerequisite is missing, when the tree on the host is not the commit asked for, when the build is stale or fails, and when the report is missing or does not add up; it never stops a process, never installs anything and never registers or changes the task. Every failure in the report is either listed in the tracked `tools/e2e_host/known-failures.json` against an open issue or makes the run exit 40. The host alias, account and folder live only in an untracked local config, with a tracked example. Tests with a fake `ssh` and `scp` prove each refusal and the summary rule; the host scripts are parsed by Windows PowerShell 5.1 and run on fixture roots; one real run of HEAD on the mini-air ends with 232 tests, 228 expected and the 4 known failures named, and no other. A run book in `.agent/docs/` names the prerequisites, the reasons and the exit codes, and `CI-E2E-FLEET-HOST-UNTRACKED` is resolved through the triage tool. No product code.

**Why.** `CI-E2E-FLEET-HOST-UNTRACKED` (`known-issues.yaml:5805`, D-1212, PLAN-NEW P2). Every full E2E run happens on the dev PC, where other agent sessions load the host: gates wait on `host-load`, and the pointer flakes of Sessions 90 and 91 were load-driven. On 2026-11-18 the coordinator set the mini-air up by hand over SSH, and run `20261118-191358` passed 228 of 232 in 19 minutes with the two clipboard specs skipped by design; the four failures are host findings for Session 97 (`CAPTURE-TEXT-PIXEL-2PX-MINIAIR`, `E2E-HOVER-NO-POINTER-DEVICE`). That setup lives only in untracked scratch scripts under `C:/Temp/av-kit/fleet-research/miniair/` (`run-e2e.ps1`, `02-build.ps1`, `03-finish-deps.ps1`, `04-register-start.ps1`, `11-rerun.ps1`), with the host name, account and folder written into them. Scratch scripts drift or are lost, and the next session would redo the host fixes by hand. Mat asked for it on 2026-11-18: "There is mini-air 12 windows pc that could be used to run the E2E tests rather than running them directly on this system."

**Grouping §3 Session 96** (grouping `:72-94`): new tracked tooling that a coordinator runs on the dev PC, its home and language picked with an HDP brief; the host side adapted from `02-build.ps1`, `11-rerun.ps1` and `run-e2e.ps1`; a run book in `.agent/docs/` naming Node, the Visual C++ runtime, the release ffmpeg on the run's PATH only, the out-e2e harness build, the mtime reset and the Interactive-logon task as the signed-in user; its tests. Shape D-1215: SSH with the pinned alias, `scp` of a `git archive`, a host build, `Start-ScheduledTask` on the Interactive-logon task, polling for `DONE`, and copying `meta.txt`, `report.json` and a summary back; nothing stored. Refusals, each named with a non-zero exit: session 0 or no signed-in user; a locked desktop; a busy host (`zvci` or another av-kit run's lock); a tree whose recorded commit is not the one asked for; a stale build. Host details in an untracked local config with a tracked example. Acceptance: tests with fake `ssh`/`scp` prove each refusal and that the summary is read from `report.json`; one real run of HEAD ends with 228 of 232 expected and the 4 known failures named and no others. Gate: no product code; the clipboard specs stay skipped on that host; no host process stopped except the run's own by recorded pid; the home-path gate before and after.

**What the code shows (plan-time reads at `HEAD` `a43cdb2`):**

- **The suite and its guard.** `ui/playwright.config.ts:12-18` runs `./tests/e2e`, matching `*.test.ts` and `*.spec.ts`, with `globalSetup`, a 60 s timeout and one worker. `ui/tests/e2e/global-setup.ts` refuses a bad `AVKIT_E2E_OUT_DIR` (`:28-31`), a missing `out/main/index.js` (`:32-35`), a build older than the newest file under `ui/src` or `electron.vite.config.ts` (`:40-47`), and a missing or stale `out-e2e/renderer/primitive-harness.html` (`:48-56`). `ui/scripts/playwright-with-outputfile.mjs:11-41` sets `PLAYWRIGHT_JSON_OUTPUT_NAME` from `--outputFile`, which is how the hand launcher got `report.json`. `capture-picker.test.ts:27` runs `native/region-picker-stub/publish/avkit-region-picker-stub.exe`, which `.gitignore` keeps out of git (`native/**/publish/`) and `ui/package.json:24` builds with the .NET SDK; the dev PC's publish folder holds the exe, the dll, `deps.json`, `runtimeconfig.json` and the pdb. HEAD has 29 E2E spec files, all directly under `ui/tests/e2e/`; without the two clipboard specs (`capture-filmstrip-actions.test.ts`, `capture-import.test.ts`) that is 27, which is the number of files in both hand reports (`erh-plan-report-probe.txt`).
- **The expected count holds at HEAD.** `git diff 3e61b5b a43cdb2 -- ui native packages backend mcp-server/src` is empty, so the product the hand run measured is the product at HEAD.
- **The hand run.** `C:/Temp/av-kit/fleet-research/miniair/results/20261118-191358/report.json`: stats 228 expected, 4 unexpected, 0 flaky, 0 skipped; 232 tests walked in 27 files; 0 errors. The four unexpected are `capture-inbox.test.ts` `AC-82.6`, `AC-102.19` and `AC-102.20`, and `settings.test.ts` `AC-126.8`, read as each title's first token (the title of `AC-102.20` also holds `AC-82.6`, so a substring match would be wrong). The earlier run `20261118-185348` had 220 expected and 12 unexpected: the same four plus eight in `convert-queue-labels.test.ts` (`AC-152.21` to `AC-152.24`), `queue-cancel-paused.test.ts` (`AC-156.11`) and `queue-pause-feedback.test.ts` (`AC-155.10`, `AC-155.11`, `AC-155.15`) (`erh-plan-report-probe.txt`). That pair is the summary's fixture: the first must exit 0, the second 40.
- **The hand scripts.** `run-e2e.ps1` writes `meta.txt`, exits 96 in session 0 and 97 under LogonUI, clears `ELECTRON_RUN_AS_NODE`, puts Node and the release ffmpeg on the run's PATH, sets `AVKIT_E2E_DIAG_DIR`, skips the two clipboard specs, runs `playwright-with-outputfile.mjs` with the JSON reporter into `report.json` and writes the exit code to `DONE`. `02-build.ps1` expands `dl\src.zip`, resets every mtime to two minutes before now, and runs `uv sync --frozen --all-packages`, `npm --prefix ui ci`, the build and the harness build into `ui/out-e2e`; `03-finish-deps.ps1` runs Electron's `install.js` and builds the picker stub and `mcp-server`; `04-register-start.ps1` registered the task (Interactive, Limited, PT2H, IgnoreNew, action `powershell.exe -NoProfile -ExecutionPolicy Bypass -WindowStyle Hidden -File <root>\run-e2e.ps1`); `11-rerun.ps1` checks for busy `zvci` test processes, then runs `Start-ScheduledTask`. Each names the host folder; none is tracked.
- **Why the mtime reset exists (measured).** `git archive --format=zip` stamps every entry with the commit time as a DOS time in the dev PC's local zone and puts the full commit id in the zip comment; Windows PowerShell 5.1 `Expand-Archive` on the host reads the DOS time as host-local time. The plan-time run of this folder's `zip-time.py` on HEAD (`erh-plan-zip-time.txt`, exit 0): 2,993 entries, one DOS time, the comment is the commit id, the DOS time is the dev PC's local wall-clock reading of the commit time within 2 s, and a host at UTC−8 reads every file 10,799 s after the commit. So on the mini-air every source file sits about three hours in the future, newer than any build made after it, and `global-setup.ts:43` refuses. The hand setup's `02-build.ps1` reset fixed it; the tool keeps that reset, measures the offset it removes and records it.
- **The host now (read-only probes, `erh-plan-host-probe.txt` and `erh-plan-host-probe2.txt`, through `host-probe-run.py`).** Windows 11 Pro, Windows PowerShell 5.1.26100, Pacific time (UTC−8); the SSH session is elevated and runs in session 0; `Get-Process -IncludeUserName` sees most owners (152 of 172 in `erh-plan-host-probe3.txt`); explorer runs in session 1 for the signed-in account, `quser` shows that console session `Active`, and LogonUI is absent (unlocked); no `zvci` test process and no local `zvci` account; since 2026-11-18 21:23 an idle zorivest `Runner.Listener` runs in that session under the signed-in account, with no `Runner.Worker` (`erh-plan-runner-probe.txt`); the task exists, Ready, Interactive, Limited, PT2H, IgnoreNew, its action the hand launcher whose SHA-256 starts `5AB99494`; no `avkit-remote.lock`, no `bin\`, no `runs\`, no `results\r*`; Node v26.13.0 (the repository's `.node-version` is 26.13.0), uv, the VC++ runtime DLLs, ffmpeg and ffprobe in the release folder, and the `dotnet` runtime; 405 GB free. The host sshd's `DefaultShell` is `powershell.exe` (probe3 `ssh_shell`; `review/ro-host-probe.txt`), so every remote command runs inside an outer `powershell -c` started without `-NoProfile`: a nested script's exit reaches the dev PC only as 0 or 1 (`exit 23` arrives as 1), and a throw or parse error as 1 with no JSON line (`review/ps51-exitcodes.txt`). The probe goes on stdin as `-Command -`; the tool stages its scripts by `scp`, runs them with `-File` and decides every outcome from the JSON line. SSH stderr carries a post-quantum key-exchange warning on every call, and Windows PowerShell writes CLIXML progress records unless `$ProgressPreference` is `SilentlyContinue`; both must be tolerated.
- **The register.** The issue is `open`, its verification method names the 191358 receipts, and its `enrichment.decision_log` holds D-1212. `CAPTURE-TEXT-PIXEL-2PX-MINIAIR` (`:5846`) and `E2E-HOVER-NO-POINTER-DEVICE` (`:5886`) are `open`; they are the issues the known-failure list binds to.

## Context Tool Decision

```yaml
context_tool_decision:
  phase: planning_and_execution
  eligible_tools: []
  decision: not_applicable
  eligibility_basis: "graphify-out/ and graphify-out-research/ are absent from P:/av-kit (ls, 2026-11-18). The change is one new tool under tools/, its host scripts, its tests and one run book, with every input read verbatim at plan time (the hand scripts, global-setup.ts, the two hand reports); that is a bypass class."
  human_message_reference: null
```

## Harness, driver and reviewer route

- **Driver:** Claude Code in VS Code (`.agent/docs/harness-profiles.md`); commands run in `pwsh` from `P:/av-kit` through `rtk proxy` with the receipt pattern (`.agent/docs/commands.md`), session receipts under `C:/Temp/av-kit/e2e-remote-host/` (`D`), the tool's own receipts under `C:/Temp/av-kit/e2e-remote/<run-id>/`.
- **The host:** reached only as `ssh -o BatchMode=yes -o StrictHostKeyChecking=yes <alias>` and the same options on `scp`, with the alias from the local config; the host key is already pinned on the dev PC, and no row adds, changes or bypasses a known-hosts entry.
- **Reviewer:** Codex through `tools/Invoke-CodexDispatch.ps1` with `AGENT_MODEL_REGISTRY_HOME=P:/.agent` and `RECEIPTS_DIR` set (Session 82 RULE-3). Plan loop `erh-plan-2026-11-18-e2e-remote-host`, execution loop `erh-execution-2026-11-18-e2e-remote-host`; caps from `.agent/review-limits.json` (6 rounds, turn tokens off).
- **Never** commit, stage or push without Mat's words; the coordinator commits after the execution review, without a push (grouping §4).

## Handoff Set

| Scope | Canonical handoff |
|---|---|
| The issue (no MEU) | `.agent/context/handoffs/2026-11-18-e2e-remote-host-handoff.md` |

Rolling reviews:

- `.agent/context/handoffs/2026-11-18-e2e-remote-host-plan-critical-review.md`
- `.agent/context/handoffs/2026-11-18-e2e-remote-host-implementation-critical-review.md`

One handoff, following the no-MEU precedent `2026-11-18-eval-describe-raw-bytes-handoff.md`.

## Work Packages and Context Lifecycle

| ID | Work | depends_on | context_strategy | durable_outputs |
|---|---|---|---|---|
| WP-1 | Baseline, plan-local checkers, the local config and the host probe (row 0) | — | shared | `baseline.*`, `red-check.py`, `identity.py`, `eol-check.py`, `issue-resolve.py`, `host-load.ps1`, `D/erh-host-probe-0.txt` |
| WP-2 | The reproduction and the Red tests (row 1) | WP-1 | shared | `tests/tooling/test_e2e_remote.py`, `D/erh-zip-time.txt` |
| WP-3 | The tool and the host scripts, Green (rows 2 and 3) | WP-2 | shared | `tools/e2e_remote.py`, `tools/e2e_host/*` |
| WP-4 | The run book and the D6 row (row 4) | WP-3 | shared | `.agent/docs/e2e-remote-host.md`, `commands.md` row |
| WP-5 | A real `check` and the real run (rows 5 and 6) | WP-4 | shared | `D/erh-check-5.json`, `C:/Temp/av-kit/e2e-remote/<run-id>/` |
| WP-6 | Register, grouping row, hub audit (rows 7 and 8) | WP-5 | shared | Issue resolved, grouping row 96 |
| WP-7 | Closeout (H1, H2) | WP-6 | `compact_continue` | The handoff, the review, the reflection |

## User Review Required

> [!NOTE]
> **Five briefs are settled on their recommendations under your hand-over** ('proceed with the next session prompt orchestration here like you did the others', 2026-11-18, continuing 'make the decisions always the recommenations'). Read them if you want to overrule one before execution:
>
> - D-1221, where the tooling lives: a Python command under `tools/` with its host scripts beside it and its tests in `tests/tooling/`.
> - D-1222, where the host details live: a JSON file in your home folder's `.config/av-kit/`, outside the repository, with a tracked example holding made-up values.
> - D-1223, how much the tool may do to the host: it checks the prerequisites and names what is missing; it installs nothing and never registers or changes the task. It writes only inside its own folder on the host.
> - D-1224, what happens when the host is busy: it refuses with a named reason and stops nothing; the caller waits and runs `check` again.
> - D-1225, which failures a run may carry: a tracked list of the four known failures, each tied to an open issue; any other failure fails the run. This one sets a pass rule, so it is an M-3 item, which the hand-over covers.
>
> **What touches your machines.** The real rows (5 and 6) copy files into the tool's folder on the mini-air, rename the hand-made launcher there (its bytes are kept), and start the existing scheduled task once, so Electron windows open on that desktop for about 20 minutes. Nothing on the dev PC runs the E2E suite. Nothing costs money. Smart App Control, auto sign-in and a GitHub runner stay yours and are not planned (D-1216). No STOP item is held for you.

## Proposed Changes

### Single-statement contracts

| Id | Statement |
|---|---|
| `PINNED_SSH` | Every `ssh` and `scp` argv the tool builds carries `-o BatchMode=yes -o StrictHostKeyChecking=yes` before the host, and none carries another host-key option, an identity file, a password or a retry. |
| `NAMED_REFUSAL` | Every refusal prints `refused: <reason>` with a reason from the closed table in §Exit codes and reasons and exits with that reason's code; nothing else exits non-zero except usage (2). |
| `NEVER_STOP` | No file under `tools/e2e_host/` and no argv the tool builds stops, kills, installs, registers, unregisters, disables or changes a process, a program or a scheduled task; the tool's only action on the task is `Start-ScheduledTask`. |
| `ONE_LOCK` | A run holds `<root>\avkit-remote.lock`, created with `CreateNew`, from before its first upload until it releases it, and every host step that writes refuses unless the lock names its run id. |
| `COMMIT_BOUND` | The tree the suite runs from is the commit asked for: the zip comment, the zip's SHA-256, the tree marker and the launcher's check all name that full commit id. |
| `REPORT_ONLY` | The summary's counts and its exit come from `report.json` and `specs.txt`, never from `run.log`, `run.err` or the console. |
| `KNOWN_NAMED` | A run exits 0 only when every test that did not pass is listed in `tools/e2e_host/known-failures.json` for the configured label, and every listed issue is `open` in the register. |
| `NO_PARTIAL` | The tool never overwrites a receipt: it creates its run folder exclusively, collects into `host.incoming` and renames it, and writes each summary file to a temporary name and renames it. |
| `CHECK_AND_NAME` | `check` writes only under `<root>\bin\`, and `run` writes only under `<root>\bin\`, `<root>\runs\<run-id>\`, `<root>\results\<run-id>\`, the lock and `<root>\run-e2e.ps1` (with the hand copy renamed beside it). |
| `LOCAL_HOST_DETAILS` | The host alias, the account and the host folder appear only in the untracked local config and in receipts under `C:/Temp/av-kit/`, never in a tracked file. |

### The local config (D-1222)

Path: `--config FILE`, else the environment variable `AVKIT_E2E_HOST_CONFIG`, else `Path.home() / ".config/av-kit/e2e-host.json"` (written `<HOME>/.config/av-kit/e2e-host.json` in docs). Strict JSON object; an unknown key, a missing key or a bad value exits 2 with `config-invalid: <key>` and no `ssh` call; a missing file exits 2 with `config-missing` and the path.

| Key | Meaning | Rule | Example value (tracked `tools/e2e_host/e2e-host.example.json`) |
|---|---|---|---|
| `host` | SSH alias, pinned in the dev PC's known hosts | `^[A-Za-z0-9][A-Za-z0-9.-]{0,62}$` | `e2e-host` |
| `user` | The account signed in on the host's desktop and the task's principal | `^[A-Za-z0-9._-]{1,64}$` | `tester` |
| `label` | The host's name in `known-failures.json` | `^[a-z0-9-]{1,32}$` | `example-host` |
| `root` | The tool's folder on the host | `^[A-Za-z]:\\[A-Za-z0-9._\\-]{1,120}$`, not under `\Users\` | `C:\e2e-root` |
| `task` | The scheduled task, path and name | `^\\[A-Za-z0-9._\\-]+\\[A-Za-z0-9._-]+$` | `\example\e2e-task` |
| `node_exe` | Node on the host | as `root`, plus a space | `C:\Program Files\nodejs\node.exe` |
| `ffmpeg_bin` | Folder holding the release `ffmpeg.exe` and `ffprobe.exe`, put on the run's PATH only | as `root`, plus a space | `C:\e2e-root\ffmpeg\bin` |
| `busy_users` | Accounts whose test processes make the host busy; one missing on the host is reported (`busy_users_missing`), not refused | list of `user` values, may be empty | `["ci-runner"]` |
| `min_free_gb` | Free space needed on the host's `C:` drive | integer 5 to 1000 | `20` |
| `poll_s` | Seconds between status polls | integer 5 to 300 | `30` |
| `timeout_min` | Minutes from the task start until `poll-timeout` | integer 10 to 115, below the task's limit | `110` |

`skip_specs` is no longer a key (a config holding it exits 2): the host's skip list is tracked in `known-failures.json` (D-1225). No value may hold a quote, `$`, `;`, `|`, `&`, a backtick or a newline, because `root` reaches an `scp` path. Row 0 writes the real file from the plan-time scratch values (`C:/Temp/av-kit/e2e-remote-host/erh-host-values.json`) plus the example's other keys; the mini-air's values are never written into a tracked file (`LOCAL_HOST_DETAILS`).

### The tool: `tools/e2e_remote.py` (new, LF, standard library and PyYAML)

PyYAML is already a dev dependency (`pyproject.toml:22`); it is used only to read the register by key (Session 92 RULE-2). Subcommands:

```text
e2e_remote.py check [--config F] [--out FILE]
e2e_remote.py run COMMIT [--config F] [--receipts DIR]
e2e_remote.py collect RUN_ID [--config F] [--receipts DIR]
e2e_remote.py release RUN_ID [--config F]
e2e_remote.py summarize REPORT [--specs FILE] [--label L] [--known FILE] [--register FILE] [--out DIR]
```

**Constants and seams.** `REPO = Path(__file__).resolve().parents[1]`; `HOST_DIR = REPO / "tools/e2e_host"`; `KNOWN_FILE = HOST_DIR / "known-failures.json"`; `REGISTER = REPO / ".agent/context/known-issues.yaml"`; `STUB_DIR = REPO / "native/region-picker-stub/publish"`; `RECEIPTS = Path("C:/Temp/av-kit/e2e-remote")`; `SSH_OPTS = ["-o", "BatchMode=yes", "-o", "StrictHostKeyChecking=yes"]`; `BUILD_TIMEOUT_S = 2700`; `STEP_TIMEOUT_S = 300`. The tests replace `run_cmd(argv, timeout=...) -> Result(code, out, err)` (every `ssh`, `scp` and `git` call goes through it, with `stdin=DEVNULL`), `archive(commit, out_path)`, `sleep(s)` and `utcnow()`; `HOST_DIR`, `KNOWN_FILE`, `REGISTER`, `STUB_DIR` and `RECEIPTS` are module attributes a test can point at `tmp_path`. All output is ASCII (`ascii()` on any path or host text).

**SSH calls.** `ssh(cfg, script, *args)` runs `["ssh", *SSH_OPTS, host, "powershell.exe", "-NoProfile", "-NonInteractive", "-ExecutionPolicy", "Bypass", "-File", "<root>\\bin\\<set>\\<script>", *args]`, where every `arg` matches `^[0-9A-Za-z-]+$` (a run id, a hex id or a stage name). `scp(cfg, src, dst)` runs `["scp", *SSH_OPTS, "-r", src, dst]` with the host side written `<host>:<root with forward slashes>/...`. Exit 255 with `Host key verification failed` or `REMOTE HOST IDENTIFICATION HAS CHANGED` in stderr is `host-key-failed` (11); any other 255 is `ssh-failed` (10); neither is retried. Stderr lines that start `** WARNING: connection is not using a post-quantum` or `** This session` or `** The server may need` are dropped before any other test. The host's outer `powershell -c` flattens a script's exit to 0 or 1, so a host script's outcome is decided only by the `reason` of the last stdout line that parses as a JSON object; lines before it (CLIXML, `#< CLIXML`, profile output, blank) are ignored, and the exit is recorded, never mapped; any exit but 255 with no JSON line is `ssh-failed` with detail `no-result`.

**Staging (D-1226).** The host set is every file in `HOST_DIR` with a `.ps1` suffix plus a generated `host.json` (the config's `user`, `root`, `task`, `node_exe`, `ffmpeg_bin`, `busy_users`, `min_free_gb`), in sorted order; `<set>` is the first 12 hex digits of the SHA-256 over each name, a NUL, its bytes and a NUL. The tool writes them to `<local>/stage/bin/<set>/` and runs `scp -r <local>/stage/bin <host>:<root>/`, so the host gets `<root>\bin\<set>\` without a separate `mkdir` call (an existing `<root>\bin` is merged into; the set is content-addressed, so a second upload writes the same bytes). `check` stages into a scratch folder under its `--out` parent; `run` stages into its run folder.

**`check`.** Stage, run `host-facts.ps1`, and evaluate the facts (§Refusal order). It prints one line per fact group and `check: ok` or `refused: <reason>` with every reason found; with `--out FILE` (exclusive create) it writes `{"facts": ..., "reasons": [...], "exit": n, "set": "<set>"}`. Exit 0 or the first reason's code. It takes no lock and writes nothing on the host outside `<root>\bin\`.

**`run COMMIT`.** In order; each step appends one line to `progress.log` in the run folder, and any refusal writes `refusal.json` there:

1. `git rev-parse --verify COMMIT^{commit}` (`commit-unknown`, 26, before any `ssh`); read the commit's epoch and its `.node-version`; the run id is `r<UTC yyyyMMddTHHmmssZ>-<sha7>`.
2. `STUB_DIR` must hold `avkit-region-picker-stub.exe`, `.dll`, `.deps.json` and `.runtimeconfig.json` (`prerequisite-missing: picker-stub-local`).
3. Create `<receipts>/<run-id>/` with `mkdir(exist_ok=False)` (`receipt-exists`, 33).
4. `archive(sha, <dir>/upload/runs/<run-id>/src.zip)`: `git archive --format=zip -o ... <sha>`; the tool checks the zip comment equals the full sha (`commit-mismatch`) and records its SHA-256; it copies the stub files to `upload/runs/<run-id>/publish/` and records each SHA-256; it writes `upload/runs/<run-id>/request.json` (`run_id`, `commit`, `commit_epoch`, `zip_sha256`, `stub` name-to-hash map, `skip` (the label's skip files), `node_exe`, `ffmpeg_bin`, `user`, `created_utc`).
5. Stage the host set and run `host-facts.ps1`; any reason refuses (§Refusal order), before the lock.
6. `host-lock.ps1 -RunId <id> -Commit <sha>` (§Host scripts). From here every refusal except `poll-timeout`, `launcher-ended` and `ssh-failed` during polling ends with `host-release.ps1 -RunId <id>`.
7. `scp -r <dir>/upload/runs <host>:<root>/`.
8. `host-prepare.ps1 -RunId <id> -Stage verify`, then `extract`, then `build` (timeout `BUILD_TIMEOUT_S`), then `stale`; each stage's JSON is saved as `prepare-<stage>.json`.
9. `host-start.ps1 -RunId <id>`: re-checks busy, the session and the task, refuses `receipt-exists` (33, `host-results`) when `results\<id>\` exists, deploys the launcher, starts the task and waits up to 60 s for it to report `Running` or for `results\<id>\meta.txt` (`task-not-started`, 24).
10. Poll `host-status.ps1 -RunId <id>` every `poll_s` until `DONE` exists; each poll's busy, lock, LogonUI and session states go to `polls.jsonl`, and the summary's `overlap` lists each poll that saw LogonUI, a session not `Active`, a lock not this run's, a `busy_users` process, a `Runner.Worker`, or an own orphan outside the run tree. The run tree is verified in `evaluate`, not on the host: the lock names this run, `pid.txt`'s pid is in `user_procs` with its `created` equal to the recorded start, and the tree is that pid plus each `user_procs` entry whose `ppid` is in the tree and whose `created` is not before its parent's; only those pids are excluded. With no `pid.txt` or a start that differs, nothing is excluded. Past `timeout_min` from the start: `poll-timeout` (30), the lock is kept, and the refusal names `collect <run-id>` and `release <run-id>`. Two polls in a row with the task not `Running` and no `DONE`: `launcher-ended` (30), lock kept. A failed poll is retried at the next interval, up to 3 in a row, then `ssh-failed` with the lock kept.
11. Collect (as `collect`): `scp -r <host>:<root>/results/<id> <dir>/host.incoming`, then `scp -r <host>:<root>/runs/<id>/logs <dir>/host-logs.incoming`; on success rename them to `host` and `host-logs` (`NO_PARTIAL`); a failed copy leaves no `host` folder.
12. Map `DONE`: 95 `request-missing` (29), 96 `no-desktop-session` (20), 97 `desktop-locked` (21), 98 `commit-mismatch` (26), 99 `build-stale` (27); any other code is Playwright's and the report is read.
13. Summarize `host/report.json` with `host/specs.txt` and the expected spec set (the commit's `ui/tests/e2e/*.test.ts` and `*.spec.ts` from `git ls-tree`, without the label's `skip` files), write `summary.json` and `summary.txt`, release the lock, and exit with the summary's code.

The last stdout line is always `e2e-remote: <ok or reason> exit=<n> run=<id> receipts=<dir>`.

**`collect RUN_ID`.** For a run that timed out or lost its connection: `host-status.ps1` must show `DONE`, else `poll-timeout` again (30); then steps 11 to 13 into the existing run folder (refusing `receipt-exists` if `host` is already there).

**`release RUN_ID`.** `host-release.ps1 -RunId <id>`: the lock names the id, removed, exit 0 `released: <id>`; no lock, exit 0 `released: none`; another id, exit 23 `lock-mismatch holder=<id>`. It never removes another run's lock; a lock left by a crashed run is released only by its own id, read from the `host-locked` refusal.

**`summarize REPORT`.** Offline: reads only `REPORT` (and `--specs`), the known list and the register. It walks `suites` recursively; each spec's `file` and each test's `status` (`expected`, `unexpected`, `flaky`, `skipped`) and `title` give one row. Refusals: no file `report-missing`; not JSON or no `suites` and `stats` `report-invalid`; walked counts not equal to `stats.expected`, `unexpected`, `flaky` and `skipped` `report-inconsistent`; a non-empty `errors` list `report-errors`; with `--specs`, the report's files, `specs.txt` and the expected set not all equal `specs-mismatch` (all 31). Then the known list (§Known failures); `summary.json` holds `tests`, `expected`, `unexpected`, `flaky`, `skipped`, `spec_files`, `specs_checked`, `known`, `known_now_passing`, `new`, `skip`, `playwright_version`, `duration_ms`, `result` and `exit`, and `run` adds `run_id`, `commit`, `label`, `done`, `mtime_skew_s`, `commit_offset_s`, `zip_sha256`, `stub`, `overlap`, `busy_users_missing` and `tool_sha256` (each tracked tool file's hash at run time). Without `--out` it prints the summary only.

### Refusal order

The facts are evaluated in this order; every reason found is listed, and the exit is the first one's code:

1. `no-desktop-session` (20): no `explorer.exe` owned by `user` in a session other than 0, or that session's `quser` state is not `Active` (a disconnected session keeps explorer but renders nothing).
2. `desktop-locked` (21): `LogonUI.exe` runs in that session.
3. `host-busy` (22): a process of a `busy_users` account named `node`, `electron`, `python`, `pytest` or `vitest`; a `Runner.Worker` under any owner (the zorivest runner runs as the signed-in account); or an own orphan of `user`, an `electron` or a `node` whose command line names `<root>\runs\` (before the start every such process is an orphan; while polling, those in the verified run tree are not, step 10); detail names owner, name and pid. A `busy_users` account missing on the host goes to `busy_users_missing`, not a refusal. `host-busy-unknown` (22): `busy_users` is not empty and `Get-Process -IncludeUserName` returned no owner (the SSH session is not elevated).
4. `host-locked` (23): the lock exists and names another run (or, in `check`, any run).
5. `task-running` (24): the task's state is `Running`.
6. `prerequisite-missing` (25), with every missing id: `node` (`node_exe` absent), `node-version` (its major differs from the commit's `.node-version` major; HEAD's for `check`), `uv`, `vcruntime` (`vcruntime140_1.dll` or `msvcp140.dll` absent from `System32`), `ffmpeg`, `ffprobe`, `task` (absent), `task-principal` (its user, any `MACHINE\` prefix dropped, is not `user`), `task-logon-interactive`, `task-action` (not `powershell.exe` with `-File <root>\run-e2e.ps1`), `task-limit` (its limit is below `timeout_min` plus 5 minutes), `picker-stub-local`, `disk` (free space below `min_free_gb`).

### Exit codes and reasons

| Exit | Reasons | Where |
|---|---|---|
| 0 | `ok` (and `released`) | Every known failure named, nothing new |
| 2 | `usage`, `config-missing`, `config-invalid` | Before any `ssh` |
| 10 | `ssh-failed` | Exit 255 or no result line |
| 11 | `host-key-failed` | Exit 255 with a host-key message; never retried |
| 20 | `no-desktop-session` | Facts; `DONE` 96 |
| 21 | `desktop-locked` | Facts; `DONE` 97 |
| 22 | `host-busy`, `host-busy-unknown` | Facts; lock and start re-checks |
| 23 | `host-locked`, `lock-mismatch` | Facts; lock; release |
| 24 | `task-running`, `task-not-started` | Facts; start |
| 25 | `prerequisite-missing` (13 ids) | Facts; step 2 |
| 26 | `commit-unknown`, `commit-mismatch`, `upload-mismatch` | Step 1; step 4; prepare `verify`; `DONE` 98 |
| 27 | `build-stale` | Prepare `stale`; `DONE` 99 |
| 28 | `build-failed` | Prepare `extract` or `build`, naming the step and its log |
| 29 | `request-missing` | `DONE` 95 |
| 30 | `poll-timeout`, `launcher-ended` | Polling; `collect` |
| 31 | `report-missing`, `report-invalid`, `report-inconsistent`, `report-errors`, `specs-mismatch` | Summary |
| 32 | `known-failures-stale` | Summary |
| 33 | `receipt-exists` | Step 3; `collect`; `--out`; `host-start` (`host-results`) |
| 34 | `receipt-write-failed` | Any receipt write |
| 40 | `new-failures` | Summary |

A host script's outcome is its JSON `reason`, mapped through this table whatever its exit (the outer shell flattens exits to 0 or 1); an unknown reason is `ssh-failed` with the reason as detail, and no JSON line is `ssh-failed` `no-result`, never exit 0.

### Known failures (D-1225): `tools/e2e_host/known-failures.json` (new, LF)

```json
{
  "known": [
    {"label": "mini-air", "file": "capture-inbox.test.ts", "ac": "AC-82.6", "issue": "CAPTURE-TEXT-PIXEL-2PX-MINIAIR"},
    {"label": "mini-air", "file": "capture-inbox.test.ts", "ac": "AC-102.19", "issue": "CAPTURE-TEXT-PIXEL-2PX-MINIAIR"},
    {"label": "mini-air", "file": "capture-inbox.test.ts", "ac": "AC-102.20", "issue": "CAPTURE-TEXT-PIXEL-2PX-MINIAIR"},
    {"label": "mini-air", "file": "settings.test.ts", "ac": "AC-126.8", "issue": "E2E-HOVER-NO-POINTER-DEVICE"}
  ],
  "skip": [
    {"label": "mini-air", "file": "capture-filmstrip-actions.test.ts", "reason": "clipboard spec; grouping §3 Gate"},
    {"label": "mini-air", "file": "capture-import.test.ts", "reason": "clipboard spec; grouping §3 Gate"}
  ]
}
```

`mini-air` is the grouping's word for the host and names no alias, account or folder. A test's AC id is its title's first whitespace token when that token matches `^AC-[0-9]+(\.[0-9]+)*$`; a title without one is matched by nothing. Rules for the configured `label` only: each `known` entry must match exactly one test, else `known-failures-stale` (32) naming it (13 keys of the hand report are shared by 2 to 4 tests; the four listed are unique); a listed test that is `unexpected` is `known`; any other `unexpected`, `flaky` or `skipped` test is `new` (exit 40, each named with file and title), so a listed test that comes back flaky or skipped never passes; a listed test that is `expected` is `known_now_passing` (listed in the summary, exit 0, so Session 97 sees it and removes the entry); a listed test the report does not hold, or a listed issue that is not `open` in the register (read by key with `yaml.safe_load`), is `known-failures-stale` (32). The label's `skip` files leave the expected set and `specs.txt`, and `summary.json` records them; in `run`, a `skip` entry with no `reason` or naming no spec file of the commit is 32. Session 97 must update this file when it resolves either issue, or its own run exits 32; the run book and H2-6's prompt say so.

### Host scripts: `tools/e2e_host/` (new, ASCII, LF, Windows PowerShell 5.1)

Each starts `$ErrorActionPreference = 'Continue'` and `$ProgressPreference = 'SilentlyContinue'`, reads `$PSScriptRoot\host.json` (the launcher reads the request instead), validates its parameters (`-RunId` against `^r[0-9]{8}T[0-9]{6}Z-[0-9a-f]{7}$`, `-Commit` against `^[0-9a-f]{40}$`, `-Stage` against the four names; else exit 2 with `reason: usage`), holds no backtick and no non-ASCII byte, and prints its result as one JSON object on the last stdout line, built with `ConvertTo-Json -InputObject $o -Depth 8 -Compress` and every list as `@(...)` (Windows PowerShell 5.1 defaults to depth 2, writing deeper levels as a type name, and a pipeline unrolls a one-item array); exit 0 means `ok`, exit 1 a refusal with `reason`, exit 2 usage. The busy, desktop and task checks are one block copied into `host-facts.ps1`, `host-lock.ps1`, `host-start.ps1` and `host-status.ps1` (Windows PowerShell has no import path the bin set could rely on; AC-14 checks the four copies are identical between their marker lines `# begin busy-check` and `# end busy-check`).

| Script | Does | Writes |
|---|---|---|
| `host-facts.ps1` | Reports §Facts schema: elevation, process owners, busy processes, runner workers, own orphans, missing busy accounts, explorer sessions and owners, the user's session state, LogonUI sessions, the task's state, principal, action and limits, the lock, the launcher's hash and marker, Node's version, uv, the VC++ DLLs, ffmpeg, ffprobe, free space, the PowerShell version, the time zone offset, the UTC time and sshd's `DefaultShell` | Nothing |
| `host-lock.ps1 -RunId -Commit` | Refuses on busy, a running task or an existing lock (`host-locked` with the holder); creates `<root>\avkit-remote.lock` with `[IO.File]::Open(..., CreateNew)` holding `run_id`, `commit`, `set` and `created_utc`; re-checks busy and, if busy now, deletes its own lock and refuses | The lock |
| `host-prepare.ps1 -RunId -Stage` | Refuses unless the lock names the run. `verify`: `runs\<id>\request.json` exists (`request-missing`), the zip's and each stub file's SHA-256 equal the request's (`upload-mismatch`), and the zip comment read from its end-of-central-directory record equals the commit (`commit-mismatch`). `extract`: `Expand-Archive` into `runs\<id>\tree\` (which must not exist), then measures, over files only (folders take the extract time), `mtime_skew_s` (the newest file time minus now, seconds) and `commit_offset_s` (the newest file time minus `commit_epoch`, seconds), resets every file's and folder's time to now minus 120 s, copies `runs\<id>\publish\*` to `tree\native\region-picker-stub\publish\`, and writes `tree\.avkit-remote-tree` holding the commit. `build`: from `tree`, with `ELECTRON_RUN_AS_NODE` removed and the Node folder first on PATH, runs `uv sync --frozen --all-packages`, `npm --prefix ui ci`, `node node_modules/electron/install.js` in `ui`, `npm --prefix ui run build`, the harness build (`AVKIT_PRIMITIVE_HARNESS_BUILD=1`, `--outDir <tree>/ui/out-e2e`), and in `mcp-server` `npm ci --ignore-scripts` and `npm run build`, each by `Start-Process -Wait -PassThru -NoNewWindow` with stdout and stderr redirected to `runs\<id>\logs\build-<n>-<step>.log` and `.err` (the child's bytes; the tool reads them as UTF-8 with replacement) and judged by its `ExitCode`, never by stderr, which PS 5.1 turns into error records when merged; a non-zero step is `build-failed` naming it; then writes `tree\.avkit-remote-build` holding the commit. `stale`: the rule of `global-setup.ts:40-56` on the host tree (the newest time under `ui\src` and `electron.vite.config.ts` not newer than `ui\out\main\index.js`; `ui\out-e2e\renderer\primitive-harness.html` present and not older than its entry or the config) plus both markers equal to the commit; else `build-stale` | Only under `runs\<id>\` |
| `host-start.ps1 -RunId` | Refuses unless the lock names the run; re-checks busy, the session and a running task; refuses `receipt-exists` (`host-results`) when `results\<id>\` exists; deploys the launcher: when `<root>\run-e2e.ps1` lacks the line `# avkit-remote-launcher`, renames it to `run-e2e.hand-<first 8 hex of its SHA-256>.ps1` (or, when that name already holds the same bytes, removes the duplicate), then copies the bin set's `run-e2e.ps1` there; runs `Start-ScheduledTask` on the task and waits up to 60 s for `Running` or `results\<id>\meta.txt` | The launcher; the renamed hand copy |
| `host-status.ps1 -RunId` | Reports the task's state and last result, whether `results\<id>\DONE` exists and its code, the lock's holder, the busy, LogonUI and session states (the busy block), `pid.txt`'s pid and start, and `user_procs` | Nothing |
| `host-release.ps1 -RunId` | Removes the lock only when it names the run (`lock-mismatch` otherwise; no lock is `ok` with `none`) | Removes its own lock |
| `run-e2e.ps1` (the launcher; first comment line `# avkit-remote-launcher`) | Run by the task in the signed-in session, with no arguments: reads the lock's `run_id` (no lock: writes `results\no-lock-<UTC stamp>\DONE` = 95 and exits); when `results\<id>\` already exists writes `results\dup-<UTC stamp>\DONE` = 95 and exits; creates `results\<id>\` and writes `meta.txt` (run id, commit, user, session, start time); refuses with `DONE` 95 when `runs\<id>\request.json` is missing, 98 when `tree\.avkit-remote-tree` is missing or not the commit, 99 when `tree\.avkit-remote-build` is missing or not the commit or the stale rule fails, 96 in session 0 or a session not `Active`, 97 when LogonUI runs in its session (the commit and build checks come first, so the fixture tests reach them in any session); then removes `ELECTRON_RUN_AS_NODE`, puts the Node folder and `ffmpeg_bin` first on PATH for this process only, sets `AVKIT_E2E_DIAG_DIR` to `results\<id>\diag`, writes `specs.txt` (each `ui\tests\e2e` file matching `*.test.ts` or `*.spec.ts` not in the request's `skip`, sorted, one name per line), starts `node scripts\playwright-with-outputfile.mjs <specs> --reporter=json --outputFile=<results>\report.json` from `tree\ui` with `Start-Process -PassThru` and no `-Wait` (which returns only after the child exits), stdout to `run.log` and stderr to `run.err`, reads `$null = $p.Handle` (else `ExitCode` comes back empty), writes `pid.txt` (the pid and its `StartTime`, round-trip form) at once, then `$p.WaitForExit()`, and writes `$p.ExitCode` to `DONE.tmp` and renames it to `DONE` last, so a poll never reads a partial `DONE` | Only under `results\<id>\` |

The tool and the host scripts never stop a process. After a `poll-timeout` the run book tells the coordinator to wait, then `collect`; only the run's own processes may be stopped, and only by Mat's or the coordinator's explicit choice outside the tool (grouping §3 Gate): the tree is found from `pid.txt`'s pid by `ParentProcessId` (`Win32_Process`; Electron and its renderers descend from node), and nothing is stopped unless that pid's `CreationDate` equals the recorded `StartTime` (a pid can be reused).

**Facts schema** (pinned from `erh-plan-host-probe3.txt`; AC-15 asserts names and types): `schema` 1; `ps_version` string; `elevated` bool; `procs_total`, `owners_seen` int; `busy` list of `{user, name, pid}`; `own_orphans` list of `{user, name, pid, ppid, created}`; host-status adds `pid_file` null or `{pid, start}` and `user_procs` list of `{pid, ppid, name, created}` (every process of `user`, `created` and `start` round-trip UTC); `runner_workers` list of `{user, pid}`; `busy_users_missing` list of strings; `explorer` list of `{session, user}` (session int); `logonui_sessions` list of int; `user_session` `{id, state}` (id int or null); `task` `{exists, state, principal, logon, runlevel, action_exe, action_args, limit_min, multiple}`; `lock` null or `{run_id, commit, set, created_utc}`; `launcher` `{exists, sha256, marker}`; `node` `{exists, version}`; `uv`, `vcruntime`, `ffmpeg`, `ffprobe` bool; `free_gb` number; `tz_offset_min` int; `utc_now`, `ssh_shell` string. A list stays a JSON array with one item; `user` values keep any `MACHINE\` prefix, and the tool compares names after it.

### Host layout (D-1227)

```text
<root>\
  avkit-remote.lock                 the run's lock (JSON)
  run-e2e.ps1                       the tracked launcher (the task's action)
  run-e2e.hand-<sha8>.ps1           the hand launcher, renamed, bytes kept
  bin\<set>\                        host scripts + host.json, content-addressed
  runs\<run-id>\request.json        what the tool sent
  runs\<run-id>\src.zip, publish\   the archive and the picker stub
  runs\<run-id>\tree\               the extracted, built commit (.avkit-remote-tree, .avkit-remote-build)
  runs\<run-id>\logs\               build logs
  results\<run-id>\                 meta.txt, specs.txt, report.json, run.log, run.err, pid.txt, diag\, DONE
```

The hand setup's `dl\`, `src\`, `tools\` (which holds the release ffmpeg), `probe-appdata\`, `results\<stamp>\` and numbered scripts are read, never written. A per-run tree keeps every run's build beside its results and needs no delete; each run adds about 2 GB, and the `disk` prerequisite refuses when free space falls below `min_free_gb`. Pruning old `runs\` folders is a manual step the run book describes for Mat; the tool never deletes one.

### The tests: `tests/tooling/test_e2e_remote.py` (new, LF, pytest)

In `tests/tooling/` beside `test_check_home_path.py`, loaded by path the same way (`ROOT = Path(__file__).resolve().parents[2]`), so `py-tests` and CI's `pytest tests/` run it. Every test asserts its target file exists first (`TOOL`, or the host script, or the run book) and then loads it, so before Green each test fails by assertion and none by collection. Test names start `test_ac_<n>_`. A fixture `fake` replaces `run_cmd` with a recorder that answers `ssh` and `scp` from a script of results keyed by host script name and passes `git` to the real one; `archive` is replaced by a fixture that writes a small zip with the right comment except where a test needs the real one; `sleep` is a no-op; `HOST_DIR` points at a `tmp_path` folder of dummy `.ps1` files for the CLI tests. The ASCII-only file builds every non-ASCII string from `\u` escapes.

| Test | What it asserts |
|---|---|
| `test_ac_1_config_*` | Missing file exits 2 `config-missing` with no `ssh`; an unknown key, each missing key and each bad value (a quote in `root`, `$` in `user`, a root under `\Users\`, a host with a space, `timeout_min` 200) exit 2 naming the key; `--config` beats `AVKIT_E2E_HOST_CONFIG`, which beats the home default (monkeypatched `Path.home`); the tracked example loads clean |
| `test_ac_2_pinned_ssh_*` | Over a full fake `run`, every `ssh` and `scp` argv has `SSH_OPTS` before the host and no `StrictHostKeyChecking=no`, `accept-new`, `off`, `UserKnownHostsFile`, `-i`, `sshpass` or `Password`; exit 255 with `Host key verification failed` gives 11 after exactly one call; another 255 gives 10; a post-quantum warning on stderr with exit 0 and CLIXML lines before the JSON line give a normal result; a refusal reason with exit 0 or 1 maps by the reason; exit 1 with no JSON line gives 10 `no-result`; `run_cmd` passes `stdin=DEVNULL` |
| `test_ac_3_no_desktop_*` | Facts with no explorer for `user`, with explorer only in session 0, and with the session `Disc`, give 20 with no lock call and no upload; `DONE` 96 gives 20 |
| `test_ac_4_locked_*` | LogonUI in the user's session gives 21; `DONE` 97 gives 21 |
| `test_ac_5_busy_*` | A `busy_users` test process gives 22 naming the account and process; no owners with `busy_users` set gives 22 `host-busy-unknown`; an empty `busy_users` with no owners is not busy; a `Runner.Worker` of any owner, an `electron` of `user` and a `node` of `user` under `<root>\runs\` each give 22; a missing `busy_users` account is listed in `busy_users_missing` and does not refuse; polls from status fixtures: a healthy run (matching lock and `pid.txt`, its node, worker and electron descendants) leaves `overlap` empty, while a same-user electron outside the tree, an orphan node under another run's folder, a `Runner.Worker`, another run's lock, or a `pid.txt` start that differs (a reused pid) each land in `overlap`; a lock held by another run gives 23 naming the holder; a running task gives 24; a busy refusal from `host-lock` or `host-start` gives 22 and, after the lock, a release call; no argv the tool sent in any test holds `Stop-Process`, `taskkill`, `Stop-ScheduledTask`, `Register-ScheduledTask`, `Set-ScheduledTask`, `Unregister-ScheduledTask` or `Disable-ScheduledTask` |
| `test_ac_6_prereq_*` | Each of the 13 ids alone gives 25 naming it; three missing at once are all named; a principal `MACHINE\tester` or `tester` matches `user` `tester` |
| `test_ac_7_commit_*` | An unknown commit gives 26 `commit-unknown` with no `ssh`; a zip whose comment is not the sha gives 26 `commit-mismatch` before upload; prepare `verify` refusals `commit-mismatch` and `upload-mismatch` give 26 and a release; `DONE` 98 gives 26; `request.json` holds the full sha, the zip's SHA-256 and the stub hashes; with the real `archive`, the HEAD zip's comment equals `git rev-parse HEAD` |
| `test_ac_8_build_*` | Prepare `build` refusing at step `npm-ci` gives 28 naming the step and log; prepare `stale` gives 27; `DONE` 99 gives 27 |
| `test_ac_9_poll_*` | No `DONE` past `timeout_min` (fake clock) gives 30 `poll-timeout`, no release call, and output naming `collect <id>` and `release <id>`; two non-running polls with no `DONE` give 30 `launcher-ended`; `DONE` 95 gives 29 |
| `test_ac_10_report_only_*` | A report with 228 expected and 4 known unexpected and a `run.log` saying `232 passed` gives 228 and 4, not 232; a report whose stats disagree with its walked tests gives 31 `report-inconsistent`; non-empty `errors` gives 31; invalid JSON and a missing file give 31; `specs.txt` missing a file gives 31 `specs-mismatch` |
| `test_ac_11_known_*` | The four known unexpected exit 0 with each named; one more unexpected exits 40 naming it; a flaky and a skipped test each exit 40; a known test now expected is listed `known_now_passing` with exit 0; a listed issue `resolved` in a fixture register exits 32; a listed test missing from the report exits 32; a title `AC-102.20 AC-82.6 ...` matches only `AC-102.20`; an entry matching two tests exits 32; a listed test that comes back `flaky` or `skipped` exits 40; the label's `skip` files leave the expected set and appear in `skip`; an entry for another label is ignored |
| `test_ac_12_receipts_*` | An existing run folder gives 33 before any `ssh`; a failed `host.incoming` copy leaves no `host` folder; a write failure of `summary.json` (patched) gives 34 and leaves no `summary.json`; `check --out` on an existing file gives 33; `host-start` refusing `receipt-exists` gives 33 and a release |
| `test_ac_13_release_*` | `release` of the holder exits 0; of another id exits 23 `lock-mismatch`; with no lock exits 0 `none`; a refusal after the lock calls `host-release.ps1` with the run's id |
| `test_ac_14_host_static_*` | Every `tools/e2e_host/*.ps1` is ASCII with LF, holds no backtick, parses with no error in Windows PowerShell 5.1 (`powershell.exe -NoProfile -Command` running `[System.Management.Automation.Language.Parser]::ParseFile`, skipped only off Windows), and holds none of `Stop-Process`, `spps`, `taskkill`, the word `kill`, `.Kill(`, `Stop-Job`, `Restart-Computer`, `schtasks`, `Invoke-WebRequest`, `Set-ItemProperty`, `Stop-ScheduledTask`, `Register-ScheduledTask`, `Set-ScheduledTask`, `Unregister-ScheduledTask`, `Disable-ScheduledTask`, `Install-`, `winget`, `choco`, `msiexec`, `Set-ExecutionPolicy`, `Remove-Item -Recurse` outside the lock and duplicate-launcher lines; the busy-check block is identical in its four copies; every `ConvertTo-Json` has `-InputObject` and `-Depth`; `run-e2e.ps1`'s first comment line is `# avkit-remote-launcher`, its `Start-Process` has no `-Wait` and is followed by `.Handle`, `pid.txt` is written before `WaitForExit`, and `DONE` only by renaming `DONE.tmp`; `tools/e2e_remote.py` holds none of the host-key bypass strings of AC-2 |
| `test_ac_15_host_fixture_*` | On a `tmp_path` root with a fixture `host.json` (empty `busy_users`, a task name that does not exist), each run as the host's shell runs it, `powershell.exe -c` wrapping `powershell.exe -NoProfile -NonInteractive -ExecutionPolicy Bypass -File`, and read from its JSON line: `host-facts.ps1` matches §Facts schema in names and value types (a one-item list stays a list); `host-lock.ps1` creates the lock, a second call refuses `host-locked` naming the first; `host-release.ps1` with another id refuses `lock-mismatch`, with the holder removes it; `host-prepare.ps1 -Stage verify` with a zip whose comment is another sha refuses `commit-mismatch`; `-Stage extract` on a zip whose DOS times are three hours after now reports `mtime_skew_s` of at least 10,000 and leaves every extracted time at or before now minus 100 s; `-Stage stale` on a tree whose `ui\src` file is newer than `ui\out\main\index.js` refuses `build-stale`; the launcher copied into the root writes `DONE` 95 with no request, 98 with a tree marker for another commit, and 99 with a stale build; `host-start.ps1` with a lock for another run refuses `host-locked` before any task call. `test_ac_15_roundtrip_*` feed the real `host-facts.ps1` output on the dev PC to `evaluate` (`busy_users` a made-up account): a made-up `user` gives 20; for the current account, 20 appears exactly when the facts show no explorer of it outside session 0 or no `Active` session; the made-up account is in `busy_users_missing` and in no `host-busy`; with `elevated` false, 22 `host-busy-unknown` |
| `test_ac_19_run_book_*` | `.agent/docs/e2e-remote-host.md` names every reason and exit of the tool's `REASONS` table, every id of `PREREQ_IDS`, every config key, the five subcommands and `known-failures.json` |
| `test_ac_21_no_host_details_*` | No new tracked file of this session (the tool, the host scripts, the example, the known list, the run book, the tests) holds an IPv4 literal, `C:\Users`, `/Users/`, `.ssh\` or `.ssh/` |

AC-15's tests run real Windows PowerShell 5.1 and are skipped off Windows with a stated reason; the dev PC and CI (`windows-latest`, `.github/workflows/ci.yml:36`, `:61`) are Windows, so the gate requires them not skipped.

### The run book: `.agent/docs/e2e-remote-host.md` (new, LF)

Sections: what the tool is for (a full E2E run off the dev PC; it adds a run and does not replace the dev PC's `ui-electron`); the host prerequisites the hand setup found (Node at the `.node-version` major, the Visual C++ runtime because onnxruntime fails to load without it, uv, the sha256-checked release ffmpeg in `ffmpeg_bin` on the run's PATH only because Smart App Control allows it, the out-e2e harness build, the mtime reset and why, the Interactive-logon task for the signed-in account with Limited, PT2H and IgnoreNew and its action, a signed-in unlocked desktop, free space); the local config and its keys, with the example; the five subcommands with their outputs and receipts; the refusal order; the exit-code and reason table; the 13 prerequisite ids and what to do for each (each is Mat's or the coordinator's hand step; the tool never installs); what the tool writes on the host and what it never touches; the known-failure list and the rule for updating it; what to do after `poll-timeout`, `launcher-ended` or a crash (wait, `collect`, then `release` by the run's own id; only the run's own processes by `pid.txt`, never by name); pruning `runs\`; the hand fallback after the launcher swap, a one-line `Move-Item -Force` of `run-e2e.hand-<sha8>.ps1` back over `run-e2e.ps1` before `11-rerun.ps1` (the next tool run swaps it again); that the task's PT2H limit ends the launcher at 120 minutes with no `DONE`, so such a run stays `poll-timeout`; that the zorivest side gets no signal; the stop rule of the host-scripts note; that a repeat of the hand setup's `05-retouch-rebuild` (cause unknown) shows as `build-stale` (27, S11); and the decisions that stay Mat's (Smart App Control, auto sign-in, a GitHub runner; D-1216). It names no alias, account or folder of the real host.

### `.agent/docs/commands.md` (CRLF stays CRLF)

One row after `:205` (`ui-electron`) in the D6 table, nothing else:

```text
| ui-electron-remote | runtime | `uv run python tools/e2e_remote.py run <commit>` | Full Electron E2E suite on the second Windows host over SSH (`.agent/docs/e2e-remote-host.md`); untracked config `<HOME>/.config/av-kit/e2e-host.json`; exit 0 only when every failure is listed in `tools/e2e_host/known-failures.json`; refusals 2 to 40 named in the run book; never stops a host process; adds a run and does not replace `ui-electron` |
```

### Plan-local files (written at plan time)

This folder already holds `zip-time.py` (the AC-16 reproduction, LF), `host-probe.ps1` (the read-only probe, ASCII, LF, holding no host detail) and `host-probe-run.py` (LF; it sends the probe on stdin with the pinned options, after one first line built from the config, and writes OUT exclusively with the exit on the last line) and `host-details-scan.py` (LF; the AC-21 scan for the local config's `host`, `root`, `task` and `user`, printing key names only).

### Boundary Inventory

| Boundary | Input | Owner | Refusal |
|---|---|---|---|
| CLI argv | Subcommands and options | `main` | `usage`, 2 |
| Local config | The JSON file | `load_config` | `config-missing`, `config-invalid`, 2, no `ssh` |
| Commit | `COMMIT` | `run` step 1 | `commit-unknown`, 26 |
| SSH transport | ssh and scp exit, stderr | `ssh`, `scp` | `host-key-failed` 11, `ssh-failed` 10 |
| Host facts | `host-facts.ps1` JSON | `evaluate` | §Refusal order, 20 to 25 |
| Host lock | `avkit-remote.lock` | `host-lock.ps1`, `host-release.ps1` | `host-locked`, `lock-mismatch`, 23 |
| Upload | `request.json`, `src.zip`, stub | `host-prepare.ps1 verify` | `request-missing`, `upload-mismatch`, `commit-mismatch` |
| Host tree | Extracted files, markers | `host-prepare.ps1 extract/stale`, the launcher | `build-failed`, `build-stale`, `DONE` 98 and 99 |
| Task | State, start | `host-start.ps1`, `host-status.ps1` | `task-running`, `task-not-started`, `poll-timeout`, `launcher-ended` |
| Report | `report.json`, `specs.txt` | `summarize` | 31 |
| Known list | `known-failures.json`, the register | `summarize` | 32, 40 |
| Receipts | `C:/Temp/av-kit/e2e-remote/<run-id>/` | `run`, `collect`, `check --out` | 33, 34 |

No API route, OpenAPI document, MCP tool, UI, product test or Python package changes.

### Acceptance Criteria

Each AC has an observable, the call chain it runs through and a negative oracle. AC-1 to AC-15, AC-19 and AC-21 are pytest tests (FAIL_TO_PASS); AC-16 to AC-18, AC-20, AC-22 and AC-23 are row checks.

| AC | Type | Description | Source | Negative Test |
|---|---|---|---|---|
| AC-1 | test | The config is read from `--config`, else `AVKIT_E2E_HOST_CONFIG`, else `<HOME>/.config/av-kit/e2e-host.json`; a missing, unknown, absent or bad key exits 2 naming it with no `ssh` call; the tracked example loads clean (`main` → `load_config`) | D-1222; grouping §3 host details | Each bad case names its key; a config error that reaches `run_cmd` fails |
| AC-2 | test | Every `ssh` and `scp` argv carries the pinned options and no bypass; a host-key failure exits 11 after one call; another 255 exits 10; the post-quantum warning and CLIXML noise do not fail a call; outcomes come from the JSON `reason` only (`run` → `ssh`/`scp` → `run_cmd`) | `PINNED_SSH`; D-1215 | A retry, a missing option or a bypass string fails |
| AC-3 | test | No explorer for the user, only one in session 0, or a session not `Active` refuses 20 before any lock or upload; `DONE` 96 maps to 20 | Grouping §3 refusals; `NAMED_REFUSAL` | A lock or upload call recorded before the refusal fails |
| AC-4 | test | LogonUI in the user's session refuses 21; `DONE` 97 maps to 21 | Grouping §3 refusals | An exit other than 21 fails |
| AC-5 | test | A busy user's test process, any `Runner.Worker` or the user's own orphan refuses 22 naming it; polls record `overlap` outside the verified run tree, and a healthy run leaves it empty; hidden owners with busy users set refuse 22 `host-busy-unknown`; another run's lock refuses 23 naming the holder; a running task refuses 24; a busy re-check after the lock refuses 22 and releases; no argv stops or changes anything | D-1224; `ONE_LOCK`; `NEVER_STOP` | A stop or task-change string in any recorded argv fails |
| AC-6 | test | Each of the 13 prerequisite ids refuses 25 naming it, and several are named together | D-1223; `CHECK_AND_NAME` | A refusal that names only the first id fails |
| AC-7 | test | An unknown commit refuses 26 before any `ssh`; a zip comment, an upload hash or a tree marker that is not the commit refuses 26; the request binds the full sha, the zip hash and the stub hashes; the real HEAD archive's comment is HEAD's sha | `COMMIT_BOUND`; grouping §3 refusals | A run that reaches `host-start` with a mismatched commit fails |
| AC-8 | test | A failing build step refuses 28 naming the step and log; a stale build refuses 27; `DONE` 99 maps to 27 | Grouping §3 refusals | An exit 0 or 40 after a build refusal fails |
| AC-9 | test | No `DONE` by `timeout_min` refuses 30 and keeps the lock, naming `collect` and `release`; a task that ends with no `DONE` refuses 30 `launcher-ended`; `DONE` 95 maps to 29 | D-1230; `NEVER_STOP` | A release or a stop after a timeout fails |
| AC-10 | test | The summary's counts come from `report.json` only; a report that does not add up, has errors, is invalid or missing, or whose files differ from `specs.txt` and the expected set, refuses 31 (`summarize` → `walk`) | `REPORT_ONLY`; grouping §3 acceptance | A console line changing a count fails |
| AC-11 | test | Listed failures for the label are known (exit 0); an unlisted unexpected, flaky or skipped test exits 40 naming it; a known test now passing is listed with exit 0; a listed issue not open, a listed test absent or an entry matching two tests exits 32; a listed test back flaky or skipped exits 40; the AC id is the title's first token | D-1225; `KNOWN_NAMED` | `AC-102.20`'s title matching `AC-82.6` fails |
| AC-12 | test | An existing run folder or `--out` file refuses 33 before any `ssh`; a failed collect leaves no `host` folder; a failed summary write refuses 34 with no partial file | `NO_PARTIAL`; D-1232 | A partial `summary.json` or `host` folder fails |
| AC-13 | test | `release` removes only its own lock (0), refuses another (23 `lock-mismatch`), reports none (0); every refusal after the lock except the polling ones releases it | `ONE_LOCK` | A release of another id's lock fails |
| AC-14 | test | The host scripts are ASCII, LF, backtick-free, parse clean in Windows PowerShell 5.1, hold no stop, install or task-change token, share one busy block and JSON form, and the launcher carries its marker and writes `pid.txt` before waiting; the tool holds no host-key bypass | `NEVER_STOP`; D-1226 | Any token or parse error fails |
| AC-15 | test | On a fixture root, under an outer `powershell -c`, the host scripts report facts in the pinned schema, take and refuse the lock, release only their own, refuse a mismatched commit, measure the mtime skew and reset it, refuse a stale build, and the launcher writes `DONE` 95, 98 and 99; the real facts round-trip through `evaluate` | `COMMIT_BOUND`; `ONE_LOCK`; D-1228 | Each case asserts its reason or code; a skip on Windows fails the gate |
| AC-16 | reproduction | Measured at row 1 before the tool exists: `zip-time.py <baseline sha> D -8` exits 0 (one DOS time, the dev PC's local reading of the commit time, the comment the commit id, a host at UTC−8 reading the files about 10,800 s after the commit), and AC-15's extract test shows `Expand-Archive` keeping that offset until the reset; at row 6 the real `prepare-extract.json` records `commit_offset_s` (files only) from 10,796 to 10,804 and every tree time at or before the reset | Brief §Red first; `02-build.ps1`; `global-setup.ts:40-47` | S5 if `zip-time.py` does not exit 0; a real offset outside the range is S12 |
| AC-17 | live | A real `check` on the mini-air exits 0 with no reason, writes `D/erh-check-5.json`, and afterwards the host probe shows no lock, no tree marker under `runs\`, no `runs\`, no `results\r*`, the hand launcher's hash unchanged and `bin\` present | `CHECK_AND_NAME`; D-1223 | A reason, or a host change outside `bin\`, is S10 or S11 |
| AC-18 | live | `run <baseline sha>` on the mini-air exits 0 and its `summary.json` holds 232 tests, 228 expected, 4 unexpected (all `known`: `AC-82.6`, `AC-102.19`, `AC-102.20`, `AC-126.8`), 0 flaky, 0 skipped, 0 new, 0 `known_now_passing`, 27 spec files with `specs_checked` true, `skip` the two tracked clipboard specs, `overlap` empty, `pid.txt` present, the baseline sha as commit, and the lock released afterwards | Grouping §3 acceptance; issue verification | Any other count is S12: a finding, recorded, never retried |
| AC-19 | test | The run book names every reason, exit, prerequisite id, config key and subcommand, and the known list | Grouping §3 run book | A missing name fails |
| AC-20 | doc | `commands.md` equals its row-0 bytes with one CRLF line added after `:205`, the `ui-electron-remote` row | Brief §Run book; D-1234 | Any other byte change or an LF line fails |
| AC-21 | test + row | No new tracked file holds an IPv4 literal, `C:\Users`, `/Users/` or an `.ssh` path (test); row 5 also scans them, this plan's `implementation-plan.md` and `task.md` for the local config's `host`, `root`, `task` and the quoted, path or backtick forms of `user` and finds none | `LOCAL_HOST_DETAILS`; grouping §3 host details | One hit fails |
| AC-22 | register | `CI-E2E-FLEET-HOST-UNTRACKED` is `resolved` through `issue-resolve.py` (bound to the row-0 register hash) with a `verification` and `resolution_path` that cite the AC-17 and AC-18 receipts and Session 96; `render` and `render --check` pass; grouping row 96 (`:133`) reads `executed (Session 96)` and no other grouping line changed | Brief §Resolve; grouping §6 | A change to any other issue, key or line fails |
| AC-23 | gate | `session-gate.ps1` ends `session-gate: all steps exit 0`: home-path before (row 0) and after, ruff on the new and plan-folder Python, the test file unchanged since Red with no skip, the summaries of both hand reports, the eol check, the full `py-tests`, and the row-6 tool hashes equal to the final files | Brief §Gate | Fail-fast; later steps `not_run` |

### Spec Sufficiency Table

| Question | Answer | Source |
|---|---|---|
| What language and where? | Python under `tools/`, host scripts in `tools/e2e_host/`, tests in `tests/tooling/` | D-1221 A |
| Where do the host details live? | `<HOME>/.config/av-kit/e2e-host.json`, never tracked; a tracked example with made-up values | D-1222 A; grouping §3 |
| Does the tool install or register anything? | No: it names what is missing; it starts the existing task | D-1223 A; D-1216 |
| What if the host is busy? | Refuse with a named reason; stop nothing; the caller waits and re-runs `check` | D-1224 A; grouping §2 shared host |
| Which failures may a run carry? | Only those in `known-failures.json` for the label, each tied to an open issue | D-1225 A |
| How do scripts reach the host? | `scp -r` into a content-addressed `bin\<set>\`; `-File` with id arguments only; outcomes from the JSON line | D-1226; the host shell flattens exits |
| Why reset mtimes? | `git archive` writes dev-PC local DOS times and the host reads them as its own zone | AC-16; `zip-time.py` |
| What counts as the result? | `report.json` and `specs.txt` | `REPORT_ONLY`; grouping §3 |
| Is a dev-PC E2E run needed? | No: the product is unchanged; the skip basis covers `ui/` | D-1229 |
| What is the expected real result? | 232 tests, 228 expected, the 4 known, 27 files | `erh-plan-report-probe.txt`; `git diff 3e61b5b a43cdb2` empty for the product |

#### Files Modified

| Path | Change | Row | Line endings |
|---|---|---|---|
| `tests/tooling/test_e2e_remote.py` | New | 1 | LF |
| `tools/e2e_remote.py` | New | 2 | LF |
| `tools/e2e_host/e2e-host.example.json` | New | 2 | LF |
| `tools/e2e_host/known-failures.json` | New | 2 | LF |
| `tools/e2e_host/host-facts.ps1`, `host-lock.ps1`, `host-prepare.ps1`, `host-start.ps1`, `host-status.ps1`, `host-release.ps1`, `run-e2e.ps1` | New | 3 | LF |
| `.agent/docs/e2e-remote-host.md` | New | 4 | LF |
| `.agent/docs/commands.md` | One row after `:205` | 4 | CRLF |
| `.agent/context/known-issues.yaml` | The issue resolved | 7 | LF |
| `.agent/context/known-issues.md` | Generated by `render` | 7 | LF |
| `.agent/context/grouping/2026-11-18-e2e-remote-host-session-grouping.md` | §6 row 96 (`:133`) only | 7 | LF |
| `.agent/context/current-focus.md` | One entry | H1-3 | CRLF |
| `docs/execution/metrics.md` | One row | H2-3 | CRLF |
| The handoff, the two reviews, the reflection | New | H1-6, H1-7, H2-2 | LF |
| This plan folder's row-0 files and scripts | New | 0 to H1-2 | LF |

**Outside the repository** (never tracked): `<HOME>/.config/av-kit/e2e-host.json` (row 0); on the host, `<root>\bin\`, `<root>\runs\<run-id>\`, `<root>\results\<run-id>\`, the lock, the tracked launcher and the renamed hand launcher (rows 5 and 6); receipts under `C:/Temp/av-kit/`.

**Read, never changed** (bound in `baseline-scope.json`): `ui/tests/e2e/global-setup.ts`, `ui/playwright.config.ts`, `ui/scripts/playwright-with-outputfile.mjs`, `ui/package.json`, `.node-version`, `.gitignore`, `pyproject.toml`, `docs/BUILD_PLAN.md` (row 8); and, outside git, the hand scripts and both hand result folders under `C:/Temp/av-kit/fleet-research/miniair/` (hashed at row 0, never moved: brief §Out of scope).

**Line endings** were measured with Python bytes (`probe-eol.txt`): `current-focus.md` (233 CRLF), `metrics.md` (105 CRLF) and `commands.md` (225 CRLF) are CRLF and stay CRLF; `known-issues.yaml` (5,923 LF), `known-issues.md` and the grouping (159 LF) are LF and stay LF. New files are LF, written as bytes (Session 83 RULE-3); the host scripts are also ASCII, which Windows PowerShell 5.1 reads the same with or without a BOM.

**Foreign class** (Session 92 RULE-3): `.agent/model-registry.local.json`, `.claude/agents/*.md` and `.cursor/agents/*.md` belong to the coordinator. Row 0 binds them by hash; a change to them during the session is recorded in the handoff, is not S4, and stays out of the commit paths.

## Out of Scope

| Item | Basis |
|---|---|
| Product code (`ui/src`, `packages/`, `mcp-server/src`, `native/`) and spec edits | Brief §Out of scope; grouping §3 Gate; the skip basis (H1-4) proves it |
| The four known failures themselves | Session 97 (`e2e-host-parity`) |
| A GitHub workflow or a self-hosted runner | D-1216; grouping §1 (Mat's, M-12 class) |
| Smart App Control, auto sign-in, any stored credential | D-1216 |
| Installing anything on the host, or registering or changing the task | D-1223 A; brief §Security |
| A full E2E run on the dev PC | Brief §Out of scope; the product is unchanged (D-1229) |
| The clipboard specs on the host | Grouping §3 Gate: they stay skipped there (the tracked `skip` entries) |
| Moving or editing the hand scripts under `C:/Temp/av-kit/fleet-research/miniair/` | Brief §Out of scope |
| Pruning `runs\` on the host | Run book: a manual step for Mat |
| An MEU or a `BUILD_PLAN.md` row | D-1212; row 8 |

## BUILD_PLAN.md Audit

No MEU, so no `docs/BUILD_PLAN.md` row and no `meu-status.yaml` change (D-1212: "its own session (96), no MEU"). Row 8 checks that `docs/BUILD_PLAN.md` keeps its row-0 bytes and names neither `e2e_remote` nor `e2e-remote-host`.

## Verification Plan

### 1. Baseline (row 0)

`baseline.ps1` (task row 0 holds each item; in the shape of `2026-11-18-eval-describe-raw-bytes/baseline.ps1`) records `HEAD`, the dirty set with its hashes, `git worktree list` and the host load; `git log --oneline a43cdb2..HEAD` and the product diff since `a43cdb2`, which must be empty (S2); `baseline-scope.json`, `baseline-eol.json` and `baseline-skip-hashes.json`, the walk dropping the secret names and `.agent/fleet/hub/` before any stat (Session 83 RULE-2); byte copies of the scope files and the hashes of the hand scripts and reports; the S2 anchors (`global-setup.ts:43`, `globalSetup` and `workers: 1`, 29 spec files and 27 without the `skip` files, the three issues `open`, grouping `:133`, `commands.md:205`, the stub's four files); the local config (exclusive create; other values are S2); the host probe `D/erh-host-probe-0.txt` (a busy or locked host is recorded, not a stop); `uv sync --frozen --offline --all-packages` and the home-path check; the copied checkers, their selftests and ruff on this folder's Python (Session 82 RULE-1).

### 2. Red, then Green (rows 1 to 4)

Row 1 runs `zip-time.py` on the baseline sha (AC-16 part 1; S5 if it does not exit 0), then writes the test file and runs it: every test must fail by assertion (`red-check.py --require test_ac_1` … `--require test_ac_15`, `--require test_ac_19`, `--require test_ac_21`); the file's SHA-256 is recorded and never changes (S3). Row 2 writes the tool, the example and the known list; the tests other than AC-14, AC-15 and AC-19 must pass. Row 3 writes the seven host scripts; all but AC-19 must pass, and `summarize` must give exit 0 on the 191358 report (228 expected, 4 known) and 40 on the 185348 report (the 8 named). Row 4 writes the run book and the `commands.md` row; the whole file must pass with no skip.

### 3. Real host (rows 5 and 6)

Row 5 runs `check` (AC-17) and the probe, and the host-detail scan (AC-21 row part). Row 6 runs `run <baseline sha>` (AC-18, AC-16 part 2) and checks its `summary.json`, its `prepare-extract.json` and a probe after it (lock gone). A busy, locked or unsigned host at either row is S10 (wait and `check` again, never a finding); any other refusal is S11; a count other than the expected one is S12.

### Session gate (H1-2)

`session-gate.ps1`, in the shape of Session 95's, fail-fast, later steps printed `not_run`, last line `session-gate: all steps exit 0`:

| Stage | Steps |
|---|---|
| Identity | `identity-before` (`identity.py`, which clears `ELECTRON_RUN_AS_NODE`, Session 88 RULE-3) |
| Static | `task-contract`; `scope-paths`; `line-endings` (`eol-check.py`); `home-path` (`tools/check_home_path.py`); `red-check-selftest`, `eol-check-selftest`; `py-format` (`ruff format --check` on `tools/e2e_remote.py`, the test file and this folder's Python); `py-lint` (`ruff check packages/ tests/ tools/e2e_remote.py` and this folder's Python); `json-valid` (the example and the known list parse, and the example passes `load_config`) |
| Targeted | `erh-tests` (the test file, its hash equal to `D/erh-test-sha.txt`, no skip); `erh-summary-191358` (exit 0, 228 expected, the 4 known); `erh-summary-185348` (exit 40, the 8 new named); `erh-zip-time` (exit 0) |
| Host load | `host-load` (Session 81 RULE-2) |
| Fresh full | `py-tests` (`uv run pytest tests/ -x --tb=short -q`, because `tools/` and `tests/` change, as Session 83 ran it); `remote-evidence` (the SHA-256 of `tools/e2e_remote.py` and each `tools/e2e_host/*` file equal the `tool_sha256` in row 6's `summary.json`; else S13); `issues-render-check`; `state-render` |
| Identity | `identity-after` |
| Skipped, with reasons | `py-types` (`packages/` unchanged), `ui-types`, `ui-lint`, `ui-tests`, `ui-build`, `ui-electron`, `mcp-types`, `mcp-tests`, `mcp-build`, `openapi`, `mcp-audit`: every file under `packages/`, `ui/`, `mcp-server/{src,scripts,tests}` and `native/` keeps its row-0 hash (H1-4); the full E2E evidence is row 6's run on the mini-air of the same product |

## Stop Conditions

| Id | Condition | Action |
|---|---|---|
| S1 | `graphify-out/` appears | Stop; re-plan the context tool decision |
| S2 | A row-0 anchor is gone or changed in meaning, a commit since `a43cdb2` touches the product paths, an issue is not `open`, row 96 is not `pending`, a local config exists with other values, or the host probe shows a task, launcher or Node that differs from the plan's facts | Stop; a moved line only is fixed in the handoff (Session 51 RULE-3) |
| S3 | A Red test fails for a setup reason or passes, or Green needs a test change | Stop; never edit the test to pass |
| S4 | `git status` lists a path outside this plan's scope, `baseline-dirty.txt` and the foreign class, or a scope path no earlier row wrote differs from `baseline-scope.json` | Stop and ask Mat; never commit, stash or revert another session's work |
| S5 | `zip-time.py` at row 1 does not exit 0 | Stop and re-plan: the archive's times are not what the plan measured |
| S6 | Codex is unavailable or the ledger refuses a round | Mat |
| S7 | `uv sync` fails on a held file | Tell Mat; never stop a process |
| S8 | The home-path check finds a new hit | Stop; fix the file, never extend the allow-list |
| S9 | A skip-basis file changed (H1-4) | Stop; the skipped suites must run |
| S10 | At row 5 or 6 the host refuses 20, 21, 22, 23 (held by a run this session did not start) or 24, or row 6's `overlap` is not empty | Not a finding: record the receipt, wait 15 minutes and run `check` again, up to 8 times; still refused, tell the coordinator; an overlapped run runs once more after `check` passes, a second overlap going to the coordinator. Never stop a process, release another run's lock or start the task by hand |
| S11 | At row 5 or 6 any other refusal (10, 11, 25 to 31, 33, 34) | Stop and record. Never bypass or re-pin the host key (11 goes to Mat), install anything, or change the task; a tool fault is fixed under the same tests and the row runs again from `check` once; a second S11 at that row goes to the coordinator |
| S12 | Row 6's counts are anything but AC-18's, or AC-16's real offset is out of range | A finding, not a retry: stop, record the summary in the handoff, and tell the coordinator; no second run, no change to the known list or a test |
| S13 | `tools/e2e_remote.py` or a host script changes after row 6 | Run row 6 once more on the final files, once only (a later change goes to the coordinator); a different count is S12 |

## Decision Log

> [!NOTE]
> D-1221 to D-1225 are the five briefs the s96 brief asks for. Their §4a check: no push, merge or release (M-1); nothing destructive (M-2): the tool deletes nothing on the host but its own lock and an exact duplicate of the hand launcher, keeps a per-run tree rather than replacing one, and renames the hand launcher with its bytes kept; D-1225 sets a pass rule for a new runtime row, which is new policy (M-3) and is covered by the hand-over, which names M-3; no API, MCP tool or external contract (M-4); no product fork (M-5); no source conflict (M-6): the grouping, the issue and the brief all ask for this shape (D-1215); no existing test assertion changes (M-7); the scope is the grouping's (M-8); no review exit (M-9); no human action (M-10): the host is set up and signed in; nothing is waived (M-11): the new row adds a run and replaces no blocking check, and the clipboard skip on that host is the grouping's own rule; no disclosure (M-12): nothing leaves Mat's machines, and the host details stay untracked; no new trusted remote or permission (M-13): the host key was pinned before this session, and no settings rule changes; no headless session (M-14): the scheduled task runs a test suite, not an agent, and it was registered by the hand setup. So D-1225 is `mandatory: M-3` and the others `mandatory: none`; all five are handed to the agent under Mat's 2026-11-18 words. D-1226 to D-1234 are autonomous with `mandatory: none`: each passed the §4a list and the §4 test. `open_decisions` is empty and there is no STOP item; D-1235 to D-1240 are left free for execution.
>
> **Earlier rows are not copied here.** D-1211, D-1215, D-1216 and D-1200 live in the grouping's §8 and D-1212 in the issue's decision log. H2-2 reads them through `--decision-source` on the grouping and `.agent/context/known-issues.yaml`, with `--decision-issue CI-E2E-FLEET-HOST-UNTRACKED`. `decision_sources` was probed at plan time with the H2-2 source list, against this plan itself (Session 90 RULE-2; `erh-decision-probe.txt`). Under HDP §6 the reflection's `### Decisions Log` lists only this session's reversible autonomous choices.

```yaml
decision_log:
  - id: D-1221
    stage: planning
    question: "Where does the tracked E2E remote-host tooling live, and in what language?"
    resolution: autonomous
    class: two-way
    mandatory: none
    chosen: "A: tools/e2e_remote.py, a Python command (standard library plus PyYAML) with check, run, collect, release and summarize; its Windows PowerShell 5.1 host scripts in tools/e2e_host/; its tests in tests/tooling/test_e2e_remote.py."
    source_tag: Local Canon
    precedents:
      - "tools/check_home_path.py and tests/tooling/test_check_home_path.py — a repo tool under tools/ with its tests in tests/tooling/, loaded by path"
      - "tools/issue_triage.py, tools/meu_status.py, tools/review_ledger.py — the coordinator's own commands are Python under tools/"
      - ".agent/context/grouping/2026-11-18-e2e-remote-host-session-grouping.md:74-75 — the plan picks the home and language with an HDP brief"
      - "C:/Temp/av-kit/fleet-research/miniair/run-e2e.ps1, 02-build.ps1 — the host side is Windows PowerShell already"
    research: { engine: none, sources: [] }
    reasoning: "Handed to the agent: USER_EXPLICIT 2026-11-18 'proceed with the next session prompt orchestration here like you did the others', continuing USER_EXPLICIT 2026-11-18 'make the decisions always the recommenations'. A puts the tool where the coordinator's other commands live, so pytest in tests/tooling and CI's pytest tests/ run its tests with a fake ssh and scp, and it reads the register with the same PyYAML the triage tool uses. The host side stays Windows PowerShell 5.1, the only shell the host has. B, a Node script in ui/scripts beside playwright-with-outputfile.mjs, sits nearer the suite, but it adds a file under ui/, which voids the ui skip basis and would make the UI suites run, its tests would need a new Vitest seam for ssh, and reading the register from Node needs a YAML package the UI does not carry. C, a PowerShell module under tools/, matches the host but the repository has no PowerShell test runner (PSScriptAnalyzer and Pester are not used), so the refusals could not be proved in the gate. D, keeping the scratch scripts, is what the issue says fails: they hold the host's details, drift and are lost. Undo: delete the new files. Two-way."
  - id: D-1222
    stage: planning
    question: "Where do the host alias, account and folder live?"
    resolution: autonomous
    class: two-way
    mandatory: none
    chosen: "A: <HOME>/.config/av-kit/e2e-host.json, overridden by --config or AVKIT_E2E_HOST_CONFIG, with strict keys and value patterns; a tracked tools/e2e_host/e2e-host.example.json holds made-up values that load clean."
    source_tag: Local Canon
    precedents:
      - ".agent/context/grouping/2026-11-18-e2e-remote-host-session-grouping.md:87 — host details in an untracked local config, never in a tracked file, with a tracked example"
      - "C:/Temp/av-kit/dispatch/s96-planner-brief.md §Security — never write the home-folder path into a tracked file; write <HOME>"
      - "memory: the Codex sandbox does not see the user's git ignore and counts an untracked repo file in tested_state"
    research: { engine: none, sources: [] }
    reasoning: "Handed to the agent: USER_EXPLICIT 2026-11-18 'proceed with the next session prompt orchestration here like you did the others', continuing USER_EXPLICIT 2026-11-18 'make the decisions always the recommenations'. A keeps the file outside the repository, so no ignore rule is needed, a careless git add cannot publish it, and no reviewer's tested_state sees it; the strict keys refuse a typo before any ssh call. B, an in-repo .local.json with a .gitignore entry, is one git add -f from publishing the host's details on a public repository, needs a .gitignore edit, and shows as an untracked file to the Codex sandbox, which reads only the repository's ignore. C, environment variables only, leaves nothing to check strictly and is lost between shells. D, hard-coding the values in the tool, is what the grouping forbids. Undo: move the file. Two-way."
  - id: D-1223
    stage: planning
    question: "How much may the tool do to the host to make it ready?"
    resolution: autonomous
    class: two-way
    mandatory: none
    chosen: "A: check and name. The tool reports each missing prerequisite by a fixed id with exit 25 and installs nothing; it starts the existing task and never registers, changes or disables it; it writes only under its own root (bin, runs, results, the lock, the launcher)."
    source_tag: Local Canon
    precedents:
      - ".agent/context/grouping/2026-11-18-e2e-remote-host-session-grouping.md:45-52 and §8 D-1216 — the host decisions stay Mat's"
      - "C:/Temp/av-kit/e2e-remote-host/erh-plan-host-probe.txt — every prerequisite is already present"
      - "C:/Temp/av-kit/fleet-research/miniair/04-register-start.ps1 — the task was registered once by hand"
    research: { engine: none, sources: [] }
    reasoning: "Handed to the agent: USER_EXPLICIT 2026-11-18 'proceed with the next session prompt orchestration here like you did the others', continuing USER_EXPLICIT 2026-11-18 'make the decisions always the recommenations'. Every prerequisite is on the host now, so the tool's job is to notice when one goes missing and say which. A keeps the tool's reach to its own folder and one Start-ScheduledTask, so a fault in it cannot change the machine. B, installers in the tool, would download and install software on Mat's machine from an automated run, with Smart App Control in the way, for a one-time setup that is already done. C, registering the task when it is missing, changes the machine's scheduled tasks under the signed-in account and needs that account's session or password, which the grouping keeps out of the tool. D, assuming the host is ready, turns a missing Node or ffmpeg into a confusing Playwright failure 20 minutes later. Undo: none needed. Two-way."
  - id: D-1224
    stage: planning
    question: "What does the tool do when the shared host is busy?"
    resolution: autonomous
    class: two-way
    mandatory: none
    chosen: "A: refuse and stop nothing. The user's session must be Active (else 20); a busy user's test process, a Runner.Worker under any owner, the user's own leftover electron or node under ROOT\\runs, or hidden owners give 22; another run's lock 23, a running task 24; the lock is created with CreateNew; busy, lock and session are re-checked in the lock and start steps and on every poll, and the summary lists any overlap; a poll excludes only the run's own verified tree (matching lock, pid.txt pid with its start time, and descendants by ParentProcessId with their start times); a busy account missing on the host is reported, not refused; a stale lock is cleared only by release with its own run id."
    source_tag: Local Canon
    precedents:
      - ".agent/context/grouping/2026-11-18-e2e-remote-host-session-grouping.md:66 — the tooling refuses to start while a zvci process or another av-kit run is active, and never stops either"
      - "C:/Temp/av-kit/fleet-research/miniair/11-rerun.ps1 — the hand busy check on zvci node, electron, python, pytest and vitest"
      - "memory: kill only by recorded pid; other sessions run their own apps"
      - "C:/Temp/av-kit/e2e-remote-host/erh96-expert-pass.txt M2 to M4; erh-plan-runner-probe.txt — the zorivest Runner.Listener runs under the signed-in account, not zvci"
      - "C:/Temp/av-kit/erh-plan-review-round-1.md F1 — the suite's own electron (ui/tests/e2e/electron-app.ts:133) runs as the user, so an unscoped poll marks every run overlapped"
    research: { engine: none, sources: [] }
    reasoning: "Handed to the agent: USER_EXPLICIT 2026-11-18 'proceed with the next session prompt orchestration here like you did the others', continuing USER_EXPLICIT 2026-11-18 'make the decisions always the recommenations'. The host is shared with the zorivest runner, and the E2E suite's pointer specs flaked under load on the dev PC, so a run beside another load measures the load. A refuses at once with a reason the caller can act on, and the re-checks inside the lock and start steps close the gap between check and start. Hidden owners count as busy, because a check that cannot see the zvci account must not pass. B, waiting or queueing inside the tool, hides how long a run waited and can hold a coordinator turn for hours; the caller's wait rule (S10) is visible. C, running at a lower priority beside the other load, still shares four cores and the desktop. D, no rule, lets two runs share one desktop and one lock-free folder. The expert pass found the first rule vacuous on the host as it is: no zvci account exists and the zorivest Listener runs under the signed-in account, so Runner.Worker counts under any owner; a disconnected session keeps explorer but renders nothing, so the state must be Active; and a job can start mid-run, so each poll re-checks and the summary labels the overlap instead of leaving an unlabelled S12. Amended after plan review round 1 (F1): the suite's own electron and node run as the user, so polling excludes only the tree verified by the lock, the pid and its start time, and the descendants' start times, a pid reused or a tree not verified excluding nothing; checking in Python from raw user_procs keeps the rule fixture-tested. Undo: none needed. Two-way."
  - id: D-1225
    stage: planning
    question: "Which failures may a remote run carry and still exit 0?"
    resolution: autonomous
    class: two-way
    mandatory: M-3
    chosen: "A: only those in the tracked tools/e2e_host/known-failures.json for the host's label, keyed by spec file and the title's first AC token, each entry matching exactly one test and bound to an issue that must be open in the register (else 32); any other failed, flaky or skipped test, a listed one included, exits 40; a known test that now passes is listed and exits 0; the host's skip list is the same file's skip entries, each with a reason, recorded in the summary."
    source_tag: Local Canon
    precedents:
      - ".agent/context/grouping/2026-11-18-e2e-remote-host-session-grouping.md:88-90 — 228 of 232 expected, with the 4 known failures named and no others"
      - ".agent/context/known-issues.yaml:5846 and :5886 — CAPTURE-TEXT-PIXEL-2PX-MINIAIR and E2E-HOVER-NO-POINTER-DEVICE, open, owned by Session 97"
      - "C:/Temp/av-kit/e2e-remote-host/erh-plan-report-probe.txt — the title of AC-102.20 also holds AC-82.6"
    research: { engine: none, sources: [] }
    reasoning: "Handed to the agent: USER_EXPLICIT 2026-11-18 'proceed with the next session prompt orchestration here like you did the others', continuing USER_EXPLICIT 2026-11-18 'make the decisions always the recommenations'. This sets the pass rule of a new runtime row, which is new policy (M-3); the hand-over names M-3, so the agent decides it. A makes the exit tell a known host finding from a new failure, and binding each entry to an open issue means the list cannot outlive its reason: when Session 97 resolves an issue, the run exits 32 until the entry goes. Matching the first token avoids the AC-102.20 title that holds AC-82.6. B, the list in the local config, hides it from review and from git, so Session 97 could not change it in a commit. C, prose in the run book, cannot be checked by the tool, so every run would exit 40 and a person would compare names by eye. D, no list, makes every run exit 40 until Session 97, so the exit carries no signal. The expert pass showed 13 first-token keys of the hand report shared by 2 to 4 tests, so an entry must match exactly one; a listed test that comes back flaky or skipped is not the known failure; and a skip list in the untracked config would drop a spec out of review for the reason B is rejected, so it is tracked here. The list never makes the dev PC's ui-electron row pass; it applies only to this new row. Undo: edit one JSON file. Two-way."
  - id: D-1226
    stage: planning
    question: "How do the host scripts reach the host and run there?"
    resolution: autonomous
    class: two-way
    mandatory: none
    chosen: "scp -r of a content-addressed bin\\SET\\ folder (the .ps1 files plus a generated host.json), then powershell.exe -NoProfile -NonInteractive -ExecutionPolicy Bypass -File with id arguments only; only the plan-local probe uses stdin; every outcome is decided from the script's last JSON line, and an exit with no JSON line is ssh-failed."
    source_tag: Local Canon
    precedents:
      - "C:/Temp/av-kit/e2e-remote-host/erh-plan-host-probe3.txt and review/ps51-exitcodes.txt — sshd's DefaultShell is powershell.exe; its outer -c flattens an inner exit to 0 or 1 and a throw to 1 with no JSON line"
      - "C:/Temp/av-kit/fleet-research/miniair/04-register-start.ps1 — the task runs powershell.exe -File"
    research: { engine: none, sources: [] }
    reasoning: "Every remote command runs inside the host's outer powershell -c, so an inline script adds a quoting layer and stdin forbids multi-line blocks; -File with id arguments keeps quoting out of the command line, and since the inner exit does not survive the outer shell, the JSON line's reason carries the outcome. Content addressing makes a re-upload write the same bytes and records which script version ran. Two-way."
  - id: D-1227
    stage: planning
    question: "What is the host folder layout, how is a run named, and how does the tool live beside the hand setup?"
    resolution: autonomous
    class: two-way
    mandatory: none
    chosen: "ROOT\\avkit-remote.lock; bin\\SET\\; runs\\RUN_ID\\ (request, zip, stub, tree, logs); results\\RUN_ID\\; the tracked launcher at ROOT\\run-e2e.ps1 with the hand copy renamed to run-e2e.hand-<sha8>.ps1; run id r<UTC yyyyMMddTHHmmssZ>-<sha7>; the hand setup's dl, src, tools and results\\STAMP untouched; the run book restores the hand launcher in one line for the hand fallback."
    source_tag: Local Canon
    precedents:
      - "C:/Temp/av-kit/e2e-remote-host/erh-plan-host-probe2.txt — the task's action is ROOT\\run-e2e.ps1; no lock and no bin yet"
      - "C:/Temp/av-kit/fleet-research/miniair/run-e2e.ps1 — results\\STAMP with DONE"
    research: { engine: none, sources: [] }
    reasoning: "The task's action already points at ROOT\\run-e2e.ps1, and changing the task is out (D-1223), so the tracked launcher takes that path and the hand copy is kept by rename. A per-run tree needs no delete on the host, so no step removes data, and each result sits beside the build it came from; the disk prerequisite bounds growth. A UTC run id sorts and names its commit. The swap changes what the task runs, not its registration, and breaks the hand fallback, hence the restore line. Two-way."
  - id: D-1228
    stage: planning
    question: "How is the host tree bound to the commit, and how is the mtime skew handled?"
    resolution: autonomous
    class: two-way
    mandatory: none
    chosen: "The zip comment (read from the end-of-central-directory record on the host), the zip's and the stub's SHA-256 and two tree markers name the full commit; after Expand-Archive the tool measures mtime_skew_s and commit_offset_s over files only, resets every time to host-now minus 120 s, and records both; the picker stub is uploaded from the dev PC's publish folder with its hashes and is not bound to the commit's source, because the host has no .NET SDK to build it."
    source_tag: Local Canon
    precedents:
      - "C:/Temp/av-kit/e2e-remote-host/erh-plan-zip-time.txt — one DOS time, dev-PC local; comment is the commit id; 10,799 s for UTC-8"
      - "C:/Temp/av-kit/fleet-research/miniair/02-build.ps1 — the hand reset to now minus 2 minutes"
      - "ui/tests/e2e/capture-picker.test.ts:27; ui/package.json:24 — the stub is a gitignored .NET build"
    research: { engine: none, sources: [] }
    reasoning: "The comment is written by git archive itself, so reading it on the host binds the bytes that were extracted, not a file the tool also wrote. Measuring the offset before the reset turns the hand fix into evidence (AC-16). Uploading the stub avoids needing the .NET SDK on the host, which has only the runtime; its limit is that its hashes are recorded, not derived from the commit. Folders take the extract time, so both measures read files only. Two-way."
  - id: D-1229
    stage: planning
    question: "Which suites does the session gate run, given that tools/ and tests/ change?"
    resolution: autonomous
    class: two-way
    mandatory: none
    chosen: "The full py-tests runs; py-lint covers packages/, tests/ and the tool; the skip basis is packages/, ui/, mcp-server/{src,scripts,tests} and native/, so the UI, MCP, OpenAPI and Electron suites are skipped with that reason; no dev-PC E2E run; the gate checks that row 6's recorded tool hashes equal the final files."
    source_tag: Local Canon
    precedents:
      - "docs/execution/plans/2026-11-15-docs-path-hygiene/implementation-plan.md — a session that added a tool and its tests ran the full py-tests"
      - ".agent/docs/commands.md:197-213 — the D6 rows"
    research: { engine: none, sources: [] }
    reasoning: "A new file under tests/ joins the suite CI runs, so the suite runs here; nothing under ui/ changes, so a dev-PC E2E run would test the same product the mini-air run tests while loading the PC the tool exists to spare. The hash check keeps the real-run evidence bound to the final code. Two-way."
  - id: D-1230
    stage: planning
    question: "What are the exit codes and reason names?"
    resolution: autonomous
    class: two-way
    mandatory: none
    chosen: "The closed table in the plan's §Exit codes and reasons: 2 usage and config, 10 and 11 transport, 20 to 25 host state, 26 to 29 commit, build and request, 30 polling, 31 and 32 report and known list, 33 and 34 receipts, 40 new failures; the launcher's 95 to 99 map onto them; a host script's outcome is mapped from its JSON reason, never its exit, which the host's outer shell flattens to 0 or 1."
    source_tag: Local Canon
    precedents:
      - "C:/Temp/av-kit/fleet-research/miniair/run-e2e.ps1 — 96 for session 0, 97 for a locked desktop"
      - ".agent/docs/commands.md:208 — mcp-audit's numbered exits as a precedent for a closed table"
      - "C:/Temp/av-kit/e2e-remote-host/review/ps51-exitcodes.txt — an inner exit 23 arrives as 1"
    research: { engine: none, sources: [] }
    reasoning: "Bands let a caller tell wait-and-retry (20 to 24) from fix-the-host (25), fix-the-tool (26 to 34) and real findings (40) by number alone, which S10 to S12 rely on. Keeping 95 to 99 for the launcher keeps the hand script's 96 and 97. Two-way."
  - id: D-1231
    stage: planning
    question: "What is the measured Red, and how do the tests fail before Green?"
    resolution: autonomous
    class: two-way
    mandatory: none
    chosen: "Row 1 runs zip-time.py on the baseline sha (exit 0 required, S5) as the reproduction of the archive-time skew; then the test file, where every test asserts its target file exists first, so all 17 test ACs fail by assertion; red-check.py requires each test_ac_N; the file's hash is fixed from Red; AC-15 adds round-trip tests that feed the real host-facts.ps1 output to evaluate against the pinned facts schema."
    source_tag: Local Canon
    precedents:
      - "docs/execution/plans/2026-11-15-docs-path-hygiene/task.md row 1 — tests asserting the tool file first; red-check.py --require test_ac_N"
      - "C:/Temp/av-kit/e2e-remote-host/erh-plan-zip-time.txt — the plan-time run"
    research: { engine: none, sources: [] }
    reasoning: "The failure the tool must prevent, a build refused as stale on the host, comes from the archive's DOS times; zip-time.py measures that cause on this PC without writing to the host, and AC-15's extract test shows Expand-Archive keeping it. A Red run on the host itself would need an unguarded build there. Every test failing first on its missing target is an honest but weak Red, so the round-trip tests bind the frozen file to the real script's output, and a schema mismatch shows at row 3, where Green can still fix the script, not at row 5. Two-way."
  - id: D-1232
    stage: planning
    question: "How are receipts and loops named?"
    resolution: autonomous
    class: two-way
    mandatory: none
    chosen: "Session receipts use the erh- prefix under C:/Temp/av-kit/e2e-remote-host; the tool's receipts go to C:/Temp/av-kit/e2e-remote/RUN_ID/ (created exclusively); loops erh-plan-2026-11-18-e2e-remote-host and erh-execution-2026-11-18-e2e-remote-host."
    source_tag: Local Canon
    precedents:
      - "docs/execution/plans/2026-11-18-eval-describe-raw-bytes/task.md — edr- receipts and loop names"
    research: { engine: none, sources: [] }
    reasoning: "One prefix per session keeps receipts findable; the tool's own folder outlives the session, since Session 97 and later callers run it too. Two-way."
  - id: D-1233
    stage: planning
    question: "How is the register updated?"
    resolution: autonomous
    class: two-way
    mandatory: none
    chosen: "Session 95's issue-resolve.py, copied with RESOLVE_KEYS status, verification and resolution_path, bound to the row-0 register hash, writing through tools/issue_triage; then render and render --check; grouping row 96 only."
    source_tag: Local Canon
    precedents:
      - "docs/execution/plans/2026-11-18-eval-describe-raw-bytes/task.md row 5 — the same pattern"
      - ".agent/context/known-issues.yaml:5805 — the issue, open"
    research: { engine: none, sources: [] }
    reasoning: "The brief asks for resolution through tools/issue_triage; the copy refuses any change outside the named keys and a register another session changed. Two-way: a later triage can reopen it."
  - id: D-1234
    stage: planning
    question: "Where are the run book and the D6 row?"
    resolution: autonomous
    class: two-way
    mandatory: none
    chosen: ".agent/docs/e2e-remote-host.md, and one D6 row ui-electron-remote after ui-electron in .agent/docs/commands.md (CRLF kept)."
    source_tag: Local Canon
    precedents:
      - ".agent/docs/macos-setup.md — a host-setup run book in .agent/docs/"
      - ".agent/docs/commands.md:205 — the ui-electron row"
    research: { engine: none, sources: [] }
    reasoning: "The grouping asks for a run book in .agent/docs/; a D6 row makes the command findable where every other runner lives, and its text says it adds a run rather than replacing ui-electron. Two-way."
  - id: D-1235
    stage: execution
    question: "Row 4 stopped: the AC-21 scan (test_ac_21_no_host_details_in_new_files) read the CLIXML version string, four dotted numbers, in the test file's own AC-2 noise fixture (tests/tooling/test_e2e_remote.py:698) as an IPv4 literal. How does row 4 go on?"
    resolution: autonomous
    class: two-way
    mandatory: none
    chosen: "A: split that one string literal into two adjacent parts joined by +, so the evaluated string is byte-identical and the file no longer holds the four-number form; no assertion, regex or fixture byte at run time changes; record the old and new SHA-256 of the test file (erh-test-sha-d1235.txt) and put the new one in erh-test-sha.txt; rerun row 4; disclose it in the handoff as an S3 deviation."
    source_tag: Local Canon
    precedents:
      - "docs/execution/plans/2026-11-18-e2e-remote-host/implementation-plan.md AC-21 - no new tracked file holds an IPv4 literal (LOCAL_HOST_DETAILS)"
      - "docs/execution/plans/2026-11-18-e2e-remote-host/implementation-plan.md AC-2 - CLIXML progress noise must not fail a call"
      - "the coordinator's ruling on the executor's row-4 stop, 2026-11-19: take option A"
    research: { engine: none, sources: [] }
    reasoning: "Handed to the agent: USER_EXPLICIT 2026-11-18 'proceed with the next session prompt orchestration here like you did the others', continuing USER_EXPLICIT 2026-11-18 'make the decisions always the recommenations'. The coordinator ruled on the executor's row-4 stop. The failure is a false positive: the version string of a CLIXML header is not an address. Splitting the literal leaves the runtime string byte-identical (erh-d1235-edit.txt compares the evaluated literal before and after: byte-identical True) and changes no assertion: the scan still reads the whole file with the same regex, and the noise test still feeds the same bytes, so neither test is weaker and it is not editing a test to pass in the sense S3 guards. B, widening the scan to allow version strings, would weaken AC-21. Doing nothing leaves the session stopped with no benefit. Undo: rejoin the literal. Two-way."
  - id: D-1236
    stage: execution
    question: "Codex execution review round 1 (C:/Temp/av-kit/erh-exec-review-round-1.md) returned changes_required: F1, High and blocking against AC-2, release_lock swallows a failed final release, so run and collect exit 0 with the host lock still held; F2, Medium, summarize --out refuses only an existing summary.json and overwrites an existing summary.txt; F3, Medium, an OSError writing polls.jsonl escapes as a traceback with no named outcome. How are they handled?"
    resolution: autonomous
    class: two-way
    mandatory: none
    chosen: "Fix F1 to F3 in tools/e2e_remote.py with regression tests, no assertion weakened. F1: a failed final release is the outcome of run and collect (11 host-key-failed, never retried; 10 ssh-failed for another transport failure), with the summary already written kept, lock_kept true in refusal.json and release guidance; a refusal whose own release fails keeps its reason and exit, lists the release failure under also and sets lock_kept true. F2: summarize --out and collect refuse an existing summary.json or summary.txt with 33 before writing. F3: an OSError writing polls.jsonl is receipt-write-failed (34) with the lock kept and the collect and release hint. The exit table is unchanged and no reason is added; the run book states the new outcomes. Five tests (seven cases) are added after Red and no existing line of the test file changes (erh-fix1-test-additions.txt); erh-test-sha.txt takes the new hash and erh-test-sha-pre-fix1.txt keeps the old. S13: row 6 runs once more on the final files (-fix1 receipts), then H1-1 to H1-4 and H1-6 to H1-6b run again."
    source_tag: Local Canon
    precedents:
      - "C:/Temp/av-kit/erh-exec-review-round-1.md - Codex execution review round 1, F1 to F3"
      - "docs/execution/plans/2026-11-18-e2e-remote-host/implementation-plan.md AC-2 - a host-key failure exits 11 after one call; another 255 exits 10 (PINNED_SSH, NAMED_REFUSAL)"
      - "docs/execution/plans/2026-11-18-e2e-remote-host/implementation-plan.md AC-12 - no receipt is overwritten and a failed write is 34 (NO_PARTIAL)"
      - "docs/execution/plans/2026-11-18-e2e-remote-host/implementation-plan.md AC-13 - every refusal after the lock except the polling ones releases it (ONE_LOCK)"
      - "the coordinator's ruling on round 1, 2026-11-19: fix all three under the hand-over"
    research: { engine: none, sources: [] }
    reasoning: "Handed to the agent: USER_EXPLICIT 2026-11-18 'proceed with the next session prompt orchestration here like you did the others', continuing USER_EXPLICIT 2026-11-18 'make the decisions always the recommenations'. The coordinator ruled on Codex round 1: fix all three. F1 breaks NAMED_REFUSAL and ONE_LOCK: an unattended caller reads success while the lock stays held, and every later run refuses host-locked. F2 breaks NO_PARTIAL, and F3 ends in a traceback with no reason, exit or guidance while the task may still run. Each fix keeps the plan's exit table and adds no reason. The new tests failed by assertion before the fix (erh-fix1-red.txt: 7 failed, red-check 0 problems) and the whole file passes after it (erh-fix1-green.txt: 181 passed); the test file only gains code, so no assertion is weaker and no M-7 change is made. Doing nothing leaves a blocking High open, so the review cannot approve. Undo: revert the tool and run-book edits and the five added tests. Two-way."
open_decisions: []
```

Expert pass (fresh context): done (`C:/Temp/av-kit/e2e-remote-host/erh96-expert-pass.txt`); every point adopted.

### D-1221: Where should the remote-host tooling live, and in what language?

**I recommend A: a Python command, `tools/e2e_remote.py`, with its Windows PowerShell host scripts in `tools/e2e_host/` and its tests in `tests/tooling/`.** It sits where the coordinator's other commands are, and the normal Python test run (and CI) proves every refusal with a fake `ssh` and `scp`. The host side stays in Windows PowerShell 5.1, the only shell on the host. The cost is that a `tools/` and `tests/` change makes the full Python suite run in the gate. Undo: delete the new files.

- B: a Node script in `ui/scripts/` beside `playwright-with-outputfile.mjs`. It sits near the suite, but a file under `ui/` makes the UI suites run, its tests need a new seam for `ssh`, and reading the issue register from Node needs a YAML package the UI does not have.
- C: a PowerShell module under `tools/`. It matches the host, but the repository has no PowerShell test runner, so the refusals could not be proved in the gate.
- D: keep the scratch scripts as they are. They hold the host's details, drift and are lost, and each run is done by hand.

Refs: D-1221; D-1212; D-1215; grouping `:74-75`.

### D-1222: Where should the host's name, account and folder be kept?

**I recommend A: a JSON file in your home folder, `<HOME>/.config/av-kit/e2e-host.json`, outside the repository, with a tracked example holding made-up values.** Nothing about the real host can be committed by accident, no ignore rule is needed, and the reviewer's view of the tree never sees it. A `--config` option or an environment variable can point elsewhere. The tool refuses a typo or an unknown key before it connects. The cost is one more file to copy when the dev PC is rebuilt. Undo: move the file.

- B: a `.local.json` file inside the repository with a `.gitignore` entry. One forced `git add` would publish the host's details on a public repository, and the Codex reviewer sees untracked files that only your own git ignore hides.
- C: environment variables only. Nothing to check strictly, and they are lost between shells.
- D: write the values into the tool. The grouping forbids it, and the repository is public.

Refs: D-1222; grouping `:87`.

### D-1223: How much may the tool change on the host to get it ready?

**I recommend A: it checks and names.** It reports each missing prerequisite by a fixed name (Node, its version, uv, the Visual C++ runtime, ffmpeg, ffprobe, the task and its settings, the picker stub, free space) and stops with exit 25. It installs nothing, and it starts the scheduled task you already have but never registers or changes it. It writes only inside its own folder on the host. Everything is installed now, so the check is what keeps a later run honest. The cost is that a missing piece needs a hand step, which the run book describes. Undo: none needed.

- B: the tool installs what is missing. It would download and install software on your machine from an automated run, with Smart App Control in the way, for a setup that is already done.
- C: the tool registers the task when it is missing. It changes the machine's scheduled tasks under the signed-in account and needs that account's session or password.
- D: assume the host is ready. A missing piece then shows up as a confusing test failure 20 minutes later.

Refs: D-1223; D-1216; grouping `:45-52`.

### D-1224: What should happen when the shared host is busy?

**I recommend A: refuse with a named reason and stop nothing.** The signed-in session must be active, not merely present. A test process of the zorivest runner's account, a runner job under any account, a leftover Electron from an earlier av-kit run, another run's lock or the task already running each stop the tool with its own exit code. Each poll re-checks, leaving out only the run's own verified processes, and the summary flags an overlap. If the tool cannot see process owners it treats the host as busy. A lock left behind is cleared only by `release` with its own run id. The caller waits and runs `check` again. The cost is a wait when the host is in use. Undo: none needed.

- B: wait or queue inside the tool. It hides how long a run waited and can hold a session for hours.
- C: run at a lower priority beside the other work. It still shares four cores and the desktop, and the pointer specs flake under load.
- D: no rule. Two runs could share one desktop and one folder.

Refs: D-1224; grouping `:66`.

### D-1225: Which failures may a remote run carry and still pass?

**I recommend A: only the four known failures, listed in a tracked file, `tools/e2e_host/known-failures.json`, each tied to an issue that must still be open.** Each entry must match exactly one test. Any other failure, a flaky test or a skipped test fails the run with exit 40, and so does a listed test that comes back flaky or skipped. The two clipboard skips sit in the same file with reasons. When Session 97 fixes an issue, the run fails with exit 32 until its entry is removed, so the list cannot outlive its reason. A known test that starts passing is reported, and the run still passes. Each test is matched by its file and the AC id that starts its title, because one title holds two AC ids. This sets a pass rule, so it is an M-3 item, which your hand-over covers. It applies only to the new remote row and never to the dev PC's E2E check. Undo: edit one file.

- B: the list in the local config. Reviewers and git never see it, and Session 97 could not change it in a commit.
- C: the list as prose in the run book. The tool cannot read it, so every run fails and someone compares names by eye.
- D: no list. Every run fails until Session 97, so the result says nothing.

Refs: D-1225; D-1213; D-1214; grouping `:88-90`.

## Research References

- **Windows OpenSSH:** the server runs each command through its `DefaultShell` (`HKLM\SOFTWARE\OpenSSH`), on this host `powershell.exe` as `-c` with the joined command line, so a nested script's exit arrives as 0 or 1 (measured, `review/ps51-exitcodes.txt`); `scp` on Windows accepts drive-letter paths with forward slashes on the host side. With `StrictHostKeyChecking=yes` and `BatchMode=yes`, `ssh` refuses an unknown or changed host key with exit 255 instead of prompting (`ssh_config(5)`).
- **Windows PowerShell 5.1 `Expand-Archive`:** it sets each file's time from the entry's DOS date and time read as local time; a zip written in another zone carries that zone's wall clock (measured, `erh-plan-zip-time.txt`). `[IO.File]::Open(path, CreateNew)` throws when the file exists, which makes the lock atomic on NTFS. PS 5.1's JSON depth, array unrolling and `Start-Process` behaviour: `review/ps51-behaviour.txt`.
- **Task Scheduler:** a task with Interactive logon for an account runs only while that account is signed in and in its desktop session; `Start-ScheduledTask` starts it without changing it; `IgnoreNew` drops a second start while one runs.
- **Playwright JSON reporter:** `report.json` holds `suites` (nested, with `specs[].tests[]` and each test's `status`: `expected`, `unexpected`, `flaky`, `skipped`), `stats` with the same four counts, and `errors`.

## Planning receipts

All under `C:/Temp/av-kit/e2e-remote-host/`, read-only against the repository and the host:

| Receipt | What it shows |
|---|---|
| `plan-probe-eol.py`, `probe-eol.txt` | Line endings, line counts and sizes of the scope; grouping rows 96 and 97 at `:133-134`; D-1221 to D-1240 used only in the grouping's allotment line |
| `erh-plan-host-probe.txt`, `plan-probe-host2.ps1`, `probe-host2.txt` | The first read-only host probes: session, owners, task, tools, free space, the hand root's items, Windows 11 Pro, `Expand-Archive` present |
| `erh-plan-host-probe2.txt`, `erh-plan-host-probe2-run.txt` | The same probe through this folder's `host-probe-run.py` and the scratch config `erh-host-values.json`: exit 0, the facts in §What the code shows |
| `erh-plan-zip-time.txt` | `zip-time.py HEAD D -8`: exit 0, 2,993 entries, one DOS time, the comment the commit id, 10,799 s |
| `plan-probe-report.py`, `erh-plan-report-probe.txt` | Both hand reports: counts, 27 files, 0 errors, each failing test's file and first AC token |
| `erh-precedents.txt` | `.gitignore`, the local-config precedents, the tools listing and the D6 rows |
| `probe_decisions.py`, `erh-decision-probe.txt` | `decision_sources` on the grouping, the register with the issue, and this plan (Session 90 RULE-2) |
| `erh-plan-ruff.txt` | `ruff format --check` and `ruff check` on this folder's Python |
| `erh-plan-host-probe3.txt`, `erh-plan-runner-probe.txt` | The widened probe (sessions, `ssh_shell`, `runs`, `results_r`, missing busy accounts) and the zorivest `Runner.Listener` |
| `erh96-expert-pass.txt`, `review/` | The expert pass and its PS 5.1 and host evidence |

## Validation stage contract

| Stage | Checks | Where |
|---|---|---|
| Plan review | This plan and `task.md`, against the issue, grouping §3 Session 96 and §8, the s96 brief, the hand scripts, `global-setup.ts` and the two hand reports | `erh-plan-2026-11-18-e2e-remote-host` |
| Row checks | Each row's validation command | `task.md` |
| Session gate | §Session gate | H1-2 |
| Execution review | The delta from `baseline.sha` in the §Files Modified paths and the row-5 and row-6 receipts, against AC-1 to AC-23 | `erh-execution-2026-11-18-e2e-remote-host` |
