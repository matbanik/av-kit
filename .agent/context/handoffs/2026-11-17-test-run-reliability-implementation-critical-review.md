---
date: "2026-11-17"
review_mode: "execution"
target_plan: "docs/execution/plans/2026-11-17-test-run-reliability/implementation-plan.md"
verdict: "approved"
findings_count: 0
template_version: "2.2"
requested_verbosity: "standard"
agent: "codex-independent-reviewer"
loop_id: "trr-execution-2026-11-17-test-run-reliability"
round: 1
tested_state: "79e3fa58501db96e5cce4796c5146963a00748c2+598a3a2bcdee031b522500a4189c78915d4795f7c84ef9d22c6b15feb80feca8"
---

# Critical Review: 2026-11-17-test-run-reliability

> **Review Mode:** execution
> **Verdict:** approved

## Scope

Session 90, no MEU, the final session of the post-Session-88 triage grouping. Codex independently reviewed the Anthropic-authored implementation against AC-1 to AC-17, within the declared delta from `baseline.sha` (`79e3fa58501db96e5cce4796c5146963a00748c2`). Read the workflow, plan/task, evidence handoff, implementation diffs, all three new test files, relevant unchanged callers, plan-local scripts/baselines, issue/document deltas and execution receipts. Applied IR-1/4/5/7 and substantive DR claim/evidence checks; API write-boundary checks are inapplicable because no such boundary changes. Approved D-1115 to D-1120 were respected; D-1122 and D-1123 were assessed below.

**Intent anchor:** the two Python integration tests that failed under load wait on their workers' signals with a 60-second bound (`WORKER_WAIT_S`), so they pass with a worker slowed past 5 s and three times in a row on a host loaded to at least 85 %, and a plain run of the three files that reach those waits (the two, and `test_tts_voice_packs.py`, which reuses the TTS file's `Stack`) takes no more than 30 s longer than at row 0; every E2E Electron main process records an unhandled promise rejection and fails its close with the rejection's stack, as it already does for an uncaught exception, and still prints a warning line on stderr; `npm --prefix ui run dev` removes `ELECTRON_RUN_AS_NODE` itself and opens a window when the terminal sets it; no file under `ui/src/`, `packages/`, `mcp-server/` or `tools/` changes, and no API route, OpenAPI document or MCP tool changes; scripts and tests prove all three, with no manual check.

**Intent achieved:** yes. No evidence-backed behavioral defect or session-caused regression established. Reviewer writes are confined to `C:/Temp/av-kit`. No suites, Electron apps, backend, dev app, CPU burners, installs, builds or network requests were started by this review. The coordinator publishes this report and performs the remaining H2 work.

## Findings

| # | Severity | Blocking | Kind | Finding | File:Line | Recommendation | Status |
|---|---|---|---|---|---|---|---|

## Q1 — Goal

Accepted all goal clauses within the approved scope, with AC-12 interpreted together with the plan's explicit S5 exception. No unproved in-scope goal clause found.

| Goal clause | AC and decisive evidence |
|---|---|
| Slowed workers pass with a 60 s bound | AC-1/2: `trr-py-red.txt` has the two intended assertion failures at row-0 YouTube `:940` and TTS `:260`; both plugin logs show actual delayed calls; Green is `2 passed in 33.58s`. AC-3 independently passes against the baseline bytes. |
| Three passes at at least 85% load | AC-5: three receipts each show `74 passed`; `trr-load-run.txt` reports load before runs 100%, 13 during-run samples all 100%, and both cleanup counts zero. |
| Plain three-file run within baseline +30 s | AC-4: baseline 10.1 s wall time, Green 9.2 s, limit 40.1 s; both have 74 passes. The gate's same three files pass in 8.18 s pytest time. |
| Rejection recorded, close fails with stack, warning retained | AC-6/7/9 and guards AC-8/10/11: saved unit and real-Electron Green evidence; independent replay of the shipped watch/close code also verifies rejection recording before and during close, one record per event, stack text and the warning substring. |
| Plain npm dev opens with variable set | AC-13/14 unit evidence and AC-15/16 automated window proofs discriminate base set/unset and fixed set/unset. Gate repeats fixed set successfully. |
| Product/API/OpenAPI/MCP untouched | Independent comparison finds all 221 baseline skip hashes unchanged, no additions/removals, no `ui/src/` or OpenAPI document delta, and all 11 read-never-changed paths intact. |
| Automated proof and register/docs fidelity | All behavior proof is in tests/scripts, without a human-check row. AC-17's exact register delta and a fresh `render --check` pass are verified. |

## Q2 — Python waits

Accepted WORKER_WAIT, WAITS_NAMED, WAIT_SIGNALS_KEPT and TIME_GUARD. The diff contains only each three-line constant block and the twelve planned bound substitutions. `WORKER_WAIT_S` is defined once in each file, used eleven times in TTS and once in YouTube. The only changed assertion lines are row-0 TTS `:955`, `:963`, `:977`, `:984`, each changing only its bound; no other expected value changes. The defaults reused by unchanged `test_tts_voice_packs.py:249` and `:320` are included in the timed and loaded runs.

A hung worker still fails: `test_youtube_adapter.py:942` bounds the join and `:943` requires Done; `test_tts_assets.py:180` returns the still-Downloading state after its deadline and `:263` requires Idle. An isolated execution of that shipped method with an advancing synthetic clock returned Downloading at approximately 60 s and failed the unchanged Idle assertion. This is a probe of deadline logic, not a fresh real-time 60 s worker run. Native event/join waits remain bounded; the pre-existing HTTP/state polls retain their existing small polling interval. Multiple waits in one test can still accumulate several minutes, as D-1115 discloses; the plan does not promise a 60 s whole-test timeout.

The load script measures non-idle CPU time from GetSystemTimes, starts the sampler after reaching the threshold, runs the exact three files, and stops its recorded launcher/interpreter handles in `finally`. Interpreter ownership is checked through a held handle before accepting it. The saved run reports 24 launchers, 24 verified interpreters and zero left. Its ownership/arithmetic/negative-verdict selftests pass independently without starting burners. Both test files remain CRLF.

## Q3 — Rejection watch

Accepted REJECTION_WATCH, REJECTION_WARNING_LINE, MAIN_REJECTION_MARKER, REJECTION_FAILS_CLOSE and EXCEPTION_WATCH_KEPT. `main-error-watch.cjs:28` adds one persistent event listener; `:37` appends the rejection record synchronously before `:38` writes the warning. It neither installs a second exception path nor rethrows the rejection. The exception listener and its three-field record remain unchanged. `electron-env.ts:16` exports the marker; its parser still preserves every nonempty record. The shared launcher preloads the watch before main and checks records after the existing close/exit wait (`electron-app.ts:79`, `:90`).

The listener replaces the native warning suppressed by installing an unhandledRejection listener; it does not preserve the native warning's entire byte sequence. It preserves exactly the `UnhandledPromiseRejectionWarning: Error: <message>` substring required by unchanged `capture-inbox.test.ts:403`. That file is byte-identical to baseline, hash `f3643be0c89e32b9736f1e3ea0253be238d4d8399dd72db98e74c5e33effe7c3`.

Saved Red: AC-6/7 fail by the missing-marker assertion, AC-9 fails with count 0, and AC-8/10/11 pass. Saved Green: the two unit files give 8 passes; the two Electron files give 8 passes. All new test hashes still equal their Red hashes. Independently replaying the actual source verifies Error, string, null, undefined, number, boolean and Symbol reasons, unchanged exception shape, one record per event, memoized close, and rejection failure with stack when the event occurs inside close itself. This uses a fake Electron application and in-memory filesystem; real-Electron behavior is supported by the saved matching-state receipts.

No launch/close delay was added: absent an event, the new listener does no append or stderr write; close retains its existing I/O and lifecycle. There is no new timer, polling, retry, process launch or exit-wait change. No concrete mechanism linking this delta to row 5's pointer failures or teardown stall was established.

## Q4 — Dev script

Accepted DEV_ENV_CLEARED, DEV_NOTICE, DEV_ARGS, DEV_SIGNALS, DEV_ENTRY_ONLY, DEV_SCRIPT, DEV_PROOF and PREVIEW_REGISTERED. `electron-vite-dev.mjs:19` copies the environment and removes all case variants only from that copy. The entry starts the installed electron-vite bin through the current Node executable with `dev`, extra arguments, inherited stdio and the UI cwd (`:58`). The caller's environment is preserved; notice is conditional. `isEntry` prevents spawning on import.

On Windows, Ctrl+C and SIGBREAK listeners keep the wrapper alive while the console delivers the signals to its child; SIGTERM is forwarded once. Exit uses `exitCodeFor` and never re-raises a signal on the wrapper. Independent in-memory entry execution verified the real spawn options, argument ordering, notice, import behavior, signal handlers, numeric/signal exit mapping and spawn-error diagnostic/exit. It started no real child. `ui/package.json` changes only line 16; preview remains unchanged.

| Automated proof receipt | Window | Notice | Left | Outcome |
|---|---|---|---|---|
| `trr-dev-base-set.txt` | no; root exited after 5 s | no | 0 | exit 1, intended base failure |
| `trr-dev-base-unset.txt` | yes, 29 s | no | 0 | pass |
| `trr-dev-set.txt` | yes, 16 s | yes | 0 | pass |
| `trr-dev-unset.txt` | yes, 16 s | no | 0 | pass |
| `trr-D6-dev-proof-set.txt` | yes, 16 s | yes | 0 | pass |

The proof requires a visible, titled Chrome_WidgetWin_1 belonging to the recorded launch, not an arbitrary window. Immutable pid/creation-time records, root-parent/start checks, post-enumeration identity confirmation and cleanup ownership refusal are present. Independent selftests exercise the previously rejected reused-pid histories, including a swap during window enumeration. Current set/unset records contain 19/15 unique identities; current logs contain one/zero notice lines respectively. Source, synthetic ownership tests and saved cleanup receipts support the safety conclusion; no reviewer live launch/kill test was performed.

## Q5 — Gate, pins and scope

The gate has all 27 required steps, each recorded exit 0, with no baseline failure excuse used. The actual step receipts agree: Python 3087 passes, UI unit 1619 passes in 142 files, targeted unit 10 passes, targeted Python 74 passes, successful build, and full Electron 226 passes. Independent recount requires 226 unique sequential result numbers and actual test result lines, not just a passing summary. The gate has no failed/flaky outcome and zero `unhandled rejection:` failure lines. The deliberate rejection probes still exercise and catch their expected close failures inside their passing tests; zero failure lines is the plan's measure of unexpected rejections.

**D-1122:** an additional full attempt was permissible but unnecessary under S5. It preserved all earlier evidence and changed no expectation or watch behavior. The extra attempts did not weaken a check.

**D-1123 / AC-12:** accepted under the explicit rule already present in task row 5 and S5 (`implementation-plan.md:367`): an Electron failure without a rejection record is rerun once alone, and only a repeat stops. Attempt 3 has two clean 226-pass runs and one 225-pass/1-fail run whose failing spec passes its allowed lone rerun. These are three complete full runs with all failures resolved by the approved rule, not three clean initial passes. The initial failure and runner exit 1 remain visible. No expectation, timeout or retry configuration was changed to obtain acceptance. The clean final gate provides additional independent-in-time suite evidence.

| Initial failure | Diagnostic and allowed rerun |
|---|---|
| Attempt 1 run 3, Convert `:1182` | Drag sent the last-position order rather than third-position order; lone rerun 1 passed (1.4 s total). |
| Attempt 2 run 1, Capture `:1601`, `:1658` | Pointer hints absent; both passed the selected rerun. |
| Attempt 2 run 1, Capture `:2001`, `:3496` | Arrow drag did not move endpoint; box drag produced no mark; both passed the selected rerun. |
| Attempt 2 run 1, Downloader `:1319` | Drag live region stayed at position 1; passed selected rerun. The filter ran six tests, including all five failing specs, with six passes. |
| Attempt 3 run 3, Capture `:1948` | 60 s test timeout plus 60 s worker teardown timeout, matching the registered launch/teardown family; lone rerun 1 passed (9.0 s total, 8.4 s test). |

All seven full runs across attempts retain zero rejection failure lines; none of the seven distinct failing specs failed again in its allowed rerun. The first six diagnostics concern real-pointer interaction before close. The last has no rejection/exception diagnostic or assertion failure; the host sampler records substantial concurrent load (77 samples, median 54%, maximum 100%, 15 at least 85%). Source inspection finds no new work in a no-rejection launch/close that explains these failures, and every affected spec also passes the final gate. This supports the disclosed host/interaction-flake explanation; it does not experimentally prove load was the sole cause. No session-caused AC-49/AC-81 regression is established.

S10 was not bypassed: no rejection failure was rerun away or allowlisted. S13 is independently confirmed by the 221-file hash comparison. The named suite-wide close condition and four bound substitutions are the only changes to existing expectations. Pyright, OpenAPI and MCP skips are justified by unchanged inputs; no fresh pass of those skipped suites is claimed. Extracted row scripts, the load probes, and `uv run --no-sync` do not invalidate this evidence. The disclosed plan Status/decision-log amendments are not product input changes; executable scripts and other D6 inputs are bound by the matching identity.

## Q6 — Registers and docs

Accepted AC-17 and COMMANDS_DOC. Independent parsed comparison verifies exactly the three named issues changed, with only status/verification/resolution_path (nine fields); no meu_links were added. The one new preview issue is open, low, ui, discovered 2026-11-17. `trr-issue-resolve.txt` shows the expected baseline hash, nine permitted differences, 97 decision logs read and zero problems; add/render receipts match the delivered bytes. A fresh offline `uv run --no-sync python tools/issue_triage.py render --check` exits 0.

Only grouping section 6 row 90 (`:125`) changes. `commands.md:78` accurately describes automatic dev clearing and notice; `:80` accurately identifies preview's remaining gap. CRLF is retained. No claim that preview was fixed is accepted or needed.

## Q7 — Safety and fidelity

The current identity, derived with ELECTRON_RUN_AS_NODE unset, is exactly:

`79e3fa58501db96e5cce4796c5146963a00748c2+598a3a2bcdee031b522500a4189c78915d4795f7c84ef9d22c6b15feb80feca8`

It equals both gate identities and the supplied expected value. There is no identity discrepancy to attribute to shell or global-ignore differences. The sandbox-only untracked `.claude/settings.local.json` was excluded by name before any read/stat and was never opened. All 21 existing baseline copies match their recorded hashes. Every session delta is within the declared files, plan folder or closeout artifacts. HEAD remains the baseline on main; nothing is staged. This reviewer made no repository writes, commit, stash, revert, process termination or network request.

Independent eol-check reports 19 paths and zero problems: CRLF in both Python files, package.json, commands.md and current-focus; LF in harness/new files. A scoped scan finds no full home path or personal mailbox in changed/new files, without printing addresses or opening secret paths. The gate's wider recorded home-path check also passes. No prohibited secret or fleet file was read.

Network scope is explicit: the changed Python tests use fakes; new rejection tests use Node/Electron and the existing loopback E2E setup. Full E2E also contains unchanged real-backend tests. Dev proofs run the actual app/backend and local Vite server; D-1120 expressly makes no network-free claim for those proofs. They start no download/transcript/TTS action. This review therefore does not certify historical dev launches as socket-free or prove absence of every possible outbound startup request. That was not a goal clause or an approved new behavior requirement.

The handoff's substantive results agree with the underlying receipts and current state. The remaining H1-7 review-collection rows and H2 rows are coordinator work after this verdict, not missing implementation behavior; this report does not claim Session 90 closeout or commit has already completed.

## Test rigor

| Test/family inspected | Rating | Basis |
|---|---|---|
| Python changed waits and reused voice-pack default | Strong | Existing final-state/storage assertions retained; deterministic delayed-worker Red/Green, plain timing and sustained-load runs. |
| Rejection unit AC-6 | Strong | Exact one-record shape, original stack/location, process survival and warning. |
| Rejection unit AC-7 | Strong | Exact non-Error record values. |
| Rejection unit AC-8 | Strong | Exact legacy exception keys and stderr marker. |
| Dev unit AC-13 | Adequate | Exact sanitized result/notice and base key count; base value preservation is additionally confirmed by source/probe. |
| Dev unit AC-14 | Strong | Actual bin existence, argument ordering, entry guard, explicit exit matrix and package scripts. Signal wiring additionally probed against actual entry code. |
| Electron AC-9 | Strong | Exactly one rejection, live child and close failure containing rejection stack. |
| Electron AC-10 | Strong | Handled rejection leaves no record; clean close required. |
| Electron AC-11 | Strong | Real stderr compatibility substring; expected rejection close caught intentionally. |
| Unchanged harness/capture pins | Strong | Exception, startup, close, isolation and warning assertions remain intact; matching real-Electron evidence. |

No weak or vacuous new test established. Synthetic reviewer probes supplement the saved real runs; they are not substitutes for Electron/window evidence.

## Checklist Results

Commands below ran with PYTHONDONTWRITEBYTECODE=1, TMP/TEMP under `C:/Temp/av-kit/test-run-reliability/exec-review/tmp`, and ELECTRON_RUN_AS_NODE unset. Their complete receipts and probe sources are under `C:/Temp/av-kit/test-run-reliability/exec-review`; initial identity receipt is `C:/Temp/av-kit/trr-review-state.txt`.

| Check | Result | Command or procedure | Exit | Decisive observation |
|---|---|---|---|---|
| Current identity | pass | `rtk proxy .venv/Scripts/python.exe docs/execution/plans/2026-11-17-test-run-reliability/identity.py --state-only` | 0 | Exact match to both full-gate identities, value above. |
| Scope, pins, line endings, negative checks | pass | `rtk proxy .venv/Scripts/python.exe C:/Temp/av-kit/test-run-reliability/exec-review/python-audit.py` | 0 | 221 unchanged skip hashes; 11 unchanged read-only files; all 3 new tests retain Red hashes; five selftests pass; wait/eol checks pass; four Red receipts verified; synthetic hang fails. |
| Watch/close/dev behavior | pass | `rtk proxy node --experimental-vm-modules C:/Temp/av-kit/test-run-reliability/exec-review/behavior-probe.mjs` | 0 | 18 checks pass, including shutdown rejection, stack, memoized close, actual entry signal/spawn/error paths; no real app launched. |
| Full-run and proof recount | pass | `rtk proxy .venv/Scripts/python.exe C:/Temp/av-kit/test-run-reliability/exec-review/count-audit.py` | 0 | All eight inspected full receipts have 226 unique sequential results; final gate 226/226; row-5 initial failures retained; all zero rejection failure lines. |
| Register render | pass | `rtk proxy uv run --no-sync python tools/issue_triage.py render --check` | 0 | `OK: known-issues.md is up-to-date`; UV_OFFLINE=true. |
| AC-1 to AC-17 / saved runtime gate | pass | Codex manually compared current diffs/ACs with actual Red, Green, load, dev-proof, rerun and all D6 step receipts. | null | 3087 Python, 1619 UI unit and 226 Electron passes; dev proof and all 27 gate steps pass; AC-12 accepted with the expressly permitted S5 rerun. |
| API schema/write-boundary changes | n/a | No changed route, product schema or MCP input surface. | null | No such implementation change. |

```json
{"schema_version":"evidence.v1","check_id":"trr-review-python-audit","command":"rtk proxy .venv/Scripts/python.exe C:/Temp/av-kit/test-run-reliability/exec-review/python-audit.py","cwd":"P:/av-kit","scope":"AC-1 to AC-5, AC-17, unchanged pins and scope","phase":"targeted","exit_code":0,"result":"pass","tested_state":"79e3fa58501db96e5cce4796c5146963a00748c2+598a3a2bcdee031b522500a4189c78915d4795f7c84ef9d22c6b15feb80feca8","output":"221 unchanged baseline skip files; 11 read-never-changed paths unchanged; new tests retain all 3 Red hashes; wait-check PASS; eol-check 19 paths, 0 problems; red-check 76 fixtures, 0 wrong; load/dev selftests 0 failures; isolated hung worker returns Downloading at approximately 60 synthetic seconds and fails Idle assertion; exact 3-issue/9-field update plus preview addition."}
```

```json
{"schema_version":"evidence.v1","check_id":"trr-review-behavior-probe","command":"rtk proxy node --experimental-vm-modules C:/Temp/av-kit/test-run-reliability/exec-review/behavior-probe.mjs","cwd":"P:/av-kit","scope":"REJECTION_WATCH, REJECTION_WARNING_LINE, REJECTION_FAILS_CLOSE, EXCEPTION_WATCH_KEPT and dev wrapper entry","phase":"targeted","exit_code":0,"result":"pass","tested_state":"79e3fa58501db96e5cce4796c5146963a00748c2+598a3a2bcdee031b522500a4189c78915d4795f7c84ef9d22c6b15feb80feca8","output":"18 checks passed. Actual source records one rejection per event; Error and non-Error reasons retained; uncaught exception shape unchanged; actual close code rejects with stack before/during close and is memoized once; wrapper import starts nothing; actual entry passes sanitized env/args/cwd, ignores SIGINT/SIGBREAK, forwards SIGTERM, maps exits and reports spawn errors. In-memory collaborators; no Electron/backend/dev app/network started."}
```

## Verdict

`approved` — the delivered work achieves the registered intent. Zero findings and no required corrections. D-1123 is accepted as the plan's pre-existing S5 exception, with the failed initial full run preserved and disclosed; approval does not relabel it a clean first-pass run. Runtime confidence comes from the saved full gate at the independently matching state, strengthened by the isolated probes and independent recount.

The coordinator may collect this verdict and continue authorized closeout. Commit authorization remains with the coordinator's existing user direction; this review performs no commit or push. Residuals are the disclosed intermittent pointer/launch-teardown flakes and registered preview gap. The JSON schema has no top-level tested_state member; the exact value is preserved in this report and the verdict checklist evidence without adding a schema-invalid field.

🕐 Completed: 2026-11-17 19:00 (EST)
