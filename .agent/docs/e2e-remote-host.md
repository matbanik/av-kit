# E2E on the remote Windows host

`tools/e2e_remote.py` runs the full Electron E2E suite of one commit on a second Windows host
over SSH, so the dev PC can keep working while the suite opens its windows somewhere else. It
adds a run; it does not replace the dev PC's `ui-electron` row in `.agent/docs/commands.md`, and
its pass rule applies only to its own row, `ui-electron-remote`.

The grouping calls the host `mini-air`. That word is the config's `label`; it names no alias,
account or folder of the real host. Those live only in the untracked local config.

## What the tool does

`uv run python tools/e2e_remote.py run <commit>`:

1. resolves the commit, reads its `.node-version` major and its spec files, and checks the label's
   `skip` entries in `tools/e2e_host/known-failures.json`;
2. writes a `git archive` zip of the commit (the zip comment is the commit) and copies the local
   region-picker stub beside it, with a `request.json` that holds both SHA-256 values;
3. copies the host scripts and a `host.json` into a content-addressed `<root>\bin\<set>\`;
4. reads the host's facts (`host-facts.ps1`) and refuses on the first reason in the refusal
   order below;
5. takes the host lock (`host-lock.ps1`), uploads the run folder to `<root>\runs\<run-id>\`;
6. on the host, verifies the upload, extracts the tree, builds it and checks it is fresh
   (`host-prepare.ps1 -Stage verify|extract|build|stale`);
7. deploys the tracked launcher and starts the existing scheduled task once (`host-start.ps1`);
8. polls every `poll_s` seconds (`host-status.ps1`) until the launcher writes `DONE`, at most
   `timeout_min` minutes;
9. copies `results\<run-id>\` and the build logs back, writes the summary from `report.json`
   only, and releases the lock (`host-release.ps1`).

The run id is `r<UTC yyyyMMddTHHmmssZ>-<sha7>`. The tool never stops a process, never installs
anything and never registers, changes or removes the scheduled task.

## Host prerequisites

The hand setup of Session 95 found each of these; the tool checks them and installs none.

- **Node** at `node_exe`, at the major of the commit's `.node-version`.
- **The Visual C++ runtime** (x64, `vcruntime140_1.dll` and `msvcp140.dll` in System32):
  onnxruntime fails to load without it.
- **uv** on the PATH of the account the SSH session uses.
- **ffmpeg and ffprobe**: the sha256-checked release build in `ffmpeg_bin`. The launcher puts that
  folder first on the PATH of the run's own process only, because Smart App Control allows that
  build; nothing else on the host sees it.
- **The out-e2e harness build**: the tool builds `ui/out-e2e` with
  `AVKIT_PRIMITIVE_HARNESS_BUILD=1`, because `global-setup.ts` refuses a run without it.
- **The mtime reset**: after the extract, every file and folder of the tree gets the time "now
  minus 120 s". A `git archive` stamps every file with the commit time, and a host clock that is
  behind the dev PC would make the built files look older than their sources, so the stale rule
  of `global-setup.ts` would fail. The extract records `mtime_skew_s` and `commit_offset_s` in the
  summary.
- **The scheduled task** named by `task`: principal the signed-in account (`user`), logon type
  Interactive (it runs only in that account's desktop session), run level Limited, execution
  time limit PT2H, multiple instances IgnoreNew, and the action
  `powershell.exe ... -File "<root>\run-e2e.ps1"`.
- **A signed-in, unlocked desktop** of `user`, outside session 0.
- **Free space** of at least `min_free_gb` GB on the root's drive; each run adds about 2 GB.

On the dev PC the region-picker stub must be published
(`npm --prefix ui run build:picker-stub`, four files in `native/region-picker-stub/publish/`).

The host build fills the account's own uv, npm and Electron caches in its profile, as the hand
setup did; that is the only write outside `<root>`.

## The local config

`<HOME>/.config/av-kit/e2e-host.json`, never tracked; `--config PATH` overrides it. The tracked
example is `tools/e2e_host/e2e-host.example.json`.

| Key | Meaning |
|---|---|
| `host` | The SSH alias. The tool runs `ssh` and `scp` with `BatchMode=yes` and `StrictHostKeyChecking=yes`, so the alias's pinned key and identity come from the SSH config. |
| `user` | The account that is signed in on the host and that the task runs as. |
| `label` | The name the known-failure list uses for this host. |
| `root` | The tool's folder on the host; it must not be under a profile folder. |
| `task` | The scheduled task's full path, `\folder\name`. |
| `node_exe` | Node on the host. |
| `ffmpeg_bin` | The folder of the release `ffmpeg.exe` and `ffprobe.exe`. |
| `busy_users` | Accounts whose test processes mean the host is busy (the shared CI runner). |
| `min_free_gb` | The free space the `disk` prerequisite asks for (5 to 1000). |
| `poll_s` | Seconds between polls (5 to 300). |
| `timeout_min` | Minutes the tool waits for `DONE` (10 to 115). |

## The five subcommands

| Command | Does | Writes |
|---|---|---|
| `uv run python tools/e2e_remote.py check [--out FILE]` | Stages the scripts, reads the facts, prints them and every reason the facts give | `FILE` (facts, reasons, exit), when asked; nothing on the host except `bin\<set>\` |
| `uv run python tools/e2e_remote.py run <commit>` | The whole run above | `C:/Temp/av-kit/e2e-remote/<run-id>/` (or `--receipts DIR`) |
| `uv run python tools/e2e_remote.py collect <run-id>` | After `poll-timeout`, `launcher-ended` or a crash: when the host has `DONE`, copies the results back, summarizes and releases | The same run folder |
| `uv run python tools/e2e_remote.py release <run-id>` | Removes the host lock only when it names that run | Nothing locally |
| `uv run python tools/e2e_remote.py summarize <report.json> --label L [--specs F] [--known F] [--register F] [--out DIR]` | Summarizes a Playwright JSON report offline with the same rule as `run` | `DIR/summary.json` and `DIR/summary.txt` |

A run folder holds `progress.log`, `upload/` (the request, zip and stub), `facts.json`, the
`prepare-*.json` results, `polls.jsonl`, `host/` (`meta.txt`, `specs.txt`, `report.json`,
`run.log`, `run.err`, `pid.txt`, `diag/`, `DONE`), `host-logs/`, `summary.json`, `summary.txt`
and, on a refusal, `refusal.json`. The last stdout line is always
`e2e-remote: <reason> exit=<n> run=<run-id> receipts=<folder>`. The tool never overwrites a
receipt; an existing one is `receipt-exists`, and `summarize --out` and `collect` refuse when
either `summary.json` or `summary.txt` is already there. `refusal.json` records `lock_kept`:
true when the host lock is still held after the refusal.

## The refusal order

`check` and `run` read the facts and refuse on the first of: `no-desktop-session`,
`desktop-locked`, `host-busy` (a `busy_users` test process, a `Runner.Worker`, or a Node or
Electron process of `user`), `host-busy-unknown`, `host-locked`, `task-running`,
`prerequisite-missing`. Every other reason found is printed and kept in `refusal.json` under
`also`. `host-lock.ps1` and `host-start.ps1` repeat the busy, desktop and task checks on the host
just before they act.

## Exit codes and reasons

| Exit | Reason | Meaning |
|---|---|---|
| 0 | `ok` | The run passed: every failure is in the known list, or the check found nothing. |
| 0 | `released` | `release` removed the lock, or there was none. |
| 2 | `usage` | Bad arguments. |
| 2 | `config-missing` | No local config at the path. |
| 2 | `config-invalid` | A key is missing, extra, of the wrong type or out of range. |
| 10 | `ssh-failed` | `ssh` or `scp` failed, or three polls in a row failed. |
| 11 | `host-key-failed` | The host key did not match. The lock, if taken, is kept: release it once the key is checked. |
| 20 | `no-desktop-session` | `user` is not signed in outside session 0 with an Active session. |
| 21 | `desktop-locked` | LogonUI runs in that session. |
| 22 | `host-busy` | Another workload's test processes, a runner worker, or a left-over Node or Electron of `user`. |
| 22 | `host-busy-unknown` | `busy_users` is set but the SSH session cannot see process owners. |
| 23 | `host-locked` | Another run holds the lock; the detail names its `holder=`. |
| 23 | `lock-mismatch` | `release` was asked for a run that does not hold the lock. |
| 24 | `task-running` | The task is already Running. |
| 24 | `task-not-started` | The task was not Running and no `meta.txt` appeared 60 s after the start. |
| 25 | `prerequisite-missing` | The detail lists the missing ids below. |
| 26 | `commit-unknown` | The commit does not resolve in this repository. |
| 26 | `commit-mismatch` | The zip comment, the request, the lock or the tree marker names another commit (launcher `DONE` 98). |
| 26 | `upload-mismatch` | A SHA-256 on the host differs from the request, or the extract failed. |
| 27 | `build-stale` | The host tree's build is older than its sources (launcher `DONE` 99). |
| 28 | `build-failed` | A host build step exited non-zero; the detail names it and its log. |
| 29 | `request-missing` | The run's `request.json` is missing (launcher `DONE` 95), or `collect` found no run folder. |
| 30 | `poll-timeout` | No `DONE` within `timeout_min`; the lock is kept. |
| 30 | `launcher-ended` | Two polls in a row saw the task not Running and no `DONE`; the lock is kept. |
| 31 | `report-missing` | `report.json` did not come back. |
| 31 | `report-invalid` | `report.json` is not a Playwright JSON report. |
| 31 | `report-inconsistent` | The report's stats do not match the tests it holds. |
| 31 | `report-errors` | The report carries top-level errors. |
| 31 | `specs-mismatch` | The report's spec files differ from `specs.txt` or from the commit's spec files less the label's `skip`. |
| 32 | `known-failures-stale` | A known entry matches no test or more than one, its issue is not open, or a `skip` entry has no reason or names no spec file. |
| 33 | `receipt-exists` | A receipt or host results folder already exists; nothing is overwritten. |
| 34 | `receipt-write-failed` | A local receipt could not be written. While polling (`polls.jsonl`) the task may still run, so the lock is kept: `collect` or `release`. |
| 40 | `new-failures` | A test failed, was flaky or was skipped and is not in the known list; each is named. |

The launcher's own `DONE` codes 96 and 97 map to `no-desktop-session` and `desktop-locked`; any
other `DONE` is Playwright's exit code, and the summary decides the result.

## Prerequisite ids

Each is a hand step for Mat or the coordinator; the tool reports it and stops with exit 25.

| Id | Missing when | Hand step |
|---|---|---|
| `node` | `node_exe` does not exist | Install Node there, or fix `node_exe`. |
| `node-version` | Its major is not the commit's `.node-version` major | Install the matching Node. |
| `uv` | `uv.exe` is not on the SSH account's PATH | Install uv for that account. |
| `vcruntime` | `vcruntime140_1.dll` or `msvcp140.dll` is missing from System32 | Install the Visual C++ 2015-2022 x64 runtime. |
| `ffmpeg` | `ffmpeg_bin\ffmpeg.exe` is missing | Restore the sha256-checked release build. |
| `ffprobe` | `ffmpeg_bin\ffprobe.exe` is missing | The same. |
| `task` | The task does not exist | Register it by hand as described above. |
| `task-principal` | It does not run as `user` | Fix the principal by hand. |
| `task-logon-interactive` | Its logon type is not Interactive | Fix the logon type by hand. |
| `task-action` | The action is not `powershell.exe` with `-File "<root>\run-e2e.ps1"` | Fix the action by hand. |
| `task-limit` | Its time limit is under `timeout_min` + 5 minutes and not unlimited | Set PT2H, or lower `timeout_min`. |
| `picker-stub-local` | The dev PC has no published region-picker stub | `npm --prefix ui run build:picker-stub`. |
| `disk` | Free space on the root's drive is under `min_free_gb` | Prune old `runs\` folders (below). |

## What the tool writes on the host

```text
<root>\
  avkit-remote.lock                 the run's lock (JSON)
  run-e2e.ps1                       the tracked launcher (the task's action)
  run-e2e.hand-<sha8>.ps1           the hand launcher, renamed, bytes kept
  bin\<set>\                        host scripts + host.json, content-addressed
  runs\<run-id>\                    request.json, src.zip, publish\, tree\, logs\
  results\<run-id>\                 meta.txt, specs.txt, report.json, run.log, run.err, pid.txt, diag\, DONE
```

The hand setup's `dl\`, `src\`, `tools\`, `probe-appdata\`, `results\<stamp>\` and numbered
scripts are read, never written. The real app data, settings, downloads and models folders are
never touched. Outside `<root>` the only writes are the account's build caches.

## The known-failure list

`tools/e2e_host/known-failures.json` lists, per `label`, the failures a run may carry (`known`,
each with its spec file, AC id and an issue key of `.agent/context/known-issues.yaml`) and the
spec files the host leaves out (`skip`, each with a reason). A test's AC id is the first word of
its title. The rules:

- a listed test that fails is `known`;
- any other failed, flaky or skipped test is `new` (exit 40);
- a listed test that passes is `known_now_passing`: the run still exits 0, and the entry should
  be removed;
- a listed test the report does not hold, an entry that matches more than one test, or an issue
  that is not `open` is `known-failures-stale` (exit 32).

When a session resolves one of the listed issues, it must remove the entries in the same commit,
or its next run exits 32. Session 97 owns `CAPTURE-TEXT-PIXEL-2PX-MINIAIR` and
`E2E-HOVER-NO-POINTER-DEVICE`, so Session 97 updates this file when it resolves either.

## After `poll-timeout`, `launcher-ended` or a crash

The lock stays, so no other run starts. Wait, then run
`uv run python tools/e2e_remote.py collect <run-id>`: it collects once `DONE` exists and releases
the lock. To give the host back without results, run
`uv run python tools/e2e_remote.py release <run-id>` with the run's own id.

The task's PT2H limit ends the launcher at 120 minutes without writing `DONE`; such a run stays
`poll-timeout`, and only `release` frees the host.

## When the release itself fails

`run` and `collect` release the lock once at the end. If that call fails, the failure is the
outcome: exit 11 `host-key-failed` (never retried) or 10 `ssh-failed`, with the summary already
written kept as it is, `lock_kept` true in `refusal.json`, and the line naming
`uv run python tools/e2e_remote.py release <run-id>`; run it once the host answers, and after a
host-key failure only once the key is checked. When a refusal releases the lock and that release
fails, the refusal keeps its own reason and exit, the release failure is listed under `also`,
and `lock_kept` is true.

Stop rule: the tool and the host scripts never stop a process. Only the run's own processes may
be stopped, and only by Mat's or the coordinator's explicit choice outside the tool. Find them
from `results\<run-id>\pid.txt`: its pid and its `ParentProcessId` tree in `Win32_Process`
(Electron and its renderers descend from node), and stop nothing unless that pid's
`CreationDate` equals the recorded start time, because a pid can be reused. Never stop by name.

The zorivest side gets no signal from a run; its runner sees only a busy desktop while the suite
runs, and the tool refuses while one of its test processes runs.

## Pruning `runs\`

Each run keeps its tree and build under `runs\<run-id>\` (about 2 GB) and never deletes one.
When the `disk` prerequisite fails, Mat removes old `runs\<run-id>\` folders by hand, never the
one the lock names, and never `results\`.

## The hand fallback

`host-start.ps1` renames the hand launcher to `run-e2e.hand-<sha8>.ps1` before it copies the
tracked one. To run the hand setup's `11-rerun.ps1` again, first put the hand launcher back in
one line on the host:

```powershell
Move-Item -Force <root>\run-e2e.hand-<sha8>.ps1 <root>\run-e2e.ps1
```

The next tool run swaps it again.

## Known risks

- A repeat of the hand setup's `05-retouch-rebuild` (its cause is unknown) shows as `build-stale`
  (exit 27); record it, never retry it in the same session.
- Smart App Control, auto sign-in and a GitHub runner on the host stay Mat's decisions (D-1216);
  the tool assumes none of them.
