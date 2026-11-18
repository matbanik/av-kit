---
date: "2026-11-18"
review_mode: "plan"
target_plan: "docs/execution/plans/2026-11-17-e2e-pointer-flakes/implementation-plan.md"
verdict: "approved"
findings_count: 3
template_version: "2.2"
requested_verbosity: "standard"
agent: "codex-independent-reviewer"
loop_id: "epf-plan-2026-11-17-e2e-pointer-flakes"
round: 3
---

# Critical Review: e2e-pointer-flakes

> **Review Mode:** plan
> **Verdict:** approved

## Scope

**Intent anchor:** The three Electron load flakes and the specs folded into them pass on a busy host. That means full Electron runs on a host held at a median load of at least 60 %, with zero failures in the watched specs, zero test-timeout hangs except those excused by a signature this session registered, zero unhandled rejections and zero diagnostics errors. If row 3's isolated watched runs showed zero failures, the proof is five full runs; otherwise it is three full runs plus ten repeats of the eleven watched tests under the same load, all passing.

Reviewed the working-tree implementation-plan.md, task.md and both plan-local scripts, emphasizing F3's redesign and the paths from run creation through acceptance. Cross-checked the Session 91 grouping and three issue records, Session 90's failing-run table, expert-pass/mutation/simulation receipts, and cited Electron harness, pointer tests and installed library code. Applied PR-1–PR-9 and the Materiality Gate to delivery behavior. Claude Code/Anthropic authored the plan; Codex/OpenAI independently reviews it. Mat's stated authority, queue order and mechanism-specific continuation are accepted as supplied.

The original Findings table is retained verbatim as history. Its old open cells are not current dispositions: F1, F2 and F3 are all **fixed**; there are **zero current blocking findings**. findings_count includes the three historical findings. Current dispositions are in Recheck (round 3); Recheck (round 2) retains that round's results.

Only C:/Temp/av-kit was written. No repository file was edited, and no product suite, Electron process, busy/churn child, npm/uv operation or network request ran. The integration probe replaces Playwright Popen, load and watcher collaborators with fakes. Forbidden files were not opened. The coordinator copies this report to the canonical path and handles the ledger.

## Findings

| # | Severity | Blocking | Kind | Finding | File:Line | Recommendation | Status |
|---|---|---|---|---|---|---|---|
| F1 | High | yes | control-defeat | **A split signature excuses hangs outside the registered failure identity.** Confidence: High. Violates AC-13; mechanism: task-row-completion-predicate. Split entries contain only cause, phase and issue; file/line keys are refused. `excuse` therefore excuses any unwatched test with that phase. A probe registered one capture-close issue, supplied an unrelated `settings.test.ts:498` timeout, and obtained an excuse and verdict 0. Consequently row 8 can pass a new, unregistered hang and report it under the old issue. | `docs/execution/plans/2026-11-17-e2e-pointer-flakes/flake-run.py:648`, `:695`; `task.md:56` | Give split entries the registered file/line or equivalent stable test identity as well as phase, and enforce it when matching. Preserve the watched restriction and exact product-race matching. Add negative cases for another file and another test in the same file. | open |
| F2 | High | yes | control-defeat | **The close guard measures from launch, so a body timeout can still be excused as a close hang.** Confidence: High. Violates AC-13; mechanism: task-row-completion-predicate. `diag_summary` calls the first `launch-start` the `test_start`; it does not record the test's actual timeout clock. With setup taking 5 s, a body reaches its 60 s timeout and enters a stuck finally-close at test age 60 s, but the classifier sees only 55 s since launch and allows split. The probe returned verdict 0. Existing unwatched tests have this finally-close structure, for example `electron-harness.test.ts:31–46`. Even after F1's identity fix, a registered close signature for that same test would excuse a later body hang. | `docs/execution/plans/2026-11-17-e2e-pointer-flakes/flake-run.py:638`, `:722`; `implementation-plan.md:323` | Record the actual test timeout/deadline or an explicit already-timed-out/body-failed state at close entry, and fail closed when that information is missing. Do not infer unused test time from first launch. Add a negative case with pre-launch setup followed by body timeout and finally-close. | open |

## Q1 — Goal and acceptance coverage

Accepted: AC-5/row 3 derives the five-full versus three-full-plus-110 branch from isolated watched failures; AC-13/row 8 requires the expected full-suite total, invocation median ≥60 %, no unexcused covered failure, no rejection and no evaluate-error; AC-14 supplies 110/110 watched executions when required. Row 8 scans only its printed, invocation-bound receipt/folder pairs (task.md:58; implementation-plan.md:344–360). The independent check passes both branches and rejects foreign/missing bindings and current rejection/diagnostics errors.

F3 no longer permits an earlier attempt to establish the current hang's excuse. Nothing remains unaccepted on Q1. Actual busy-host acceptance is still execution work; the quiet final gate is additional proof, not a substitute.

## Q2 — Fix conditions and Red/Green

Accepted: SETTLE/SETTLED_BOX use repeated observations; POINTER_ON hit-tests the target/wrapper; DRAG_DRIVER_SHARED waits for pressed state and the committed-over announcement; SETTLED_ZOOM uses the zoom attributes and geometry; GRAB_COMMITTED waits for changed x2. POINTER_SITES covers the named capture reads. ASSERTIONS_KEPT, NO_NEW_WAIT_KNOBS and CONFIG_KEPT preserve the existing oracles (plan:200–225,260–270; AC-1–AC-11).

AC-6/AC-7 remain static wiring tests, and missing-module assertion Reds do not reproduce the original intermittent races. As accepted previously, D-1146 allows a quiet reproduction and relies on loaded full-suite acceptance for the integration result. No new timeout/retry or assertion weakening is planned. No new blocker on Q2.

## Q3 — Load and reproduction

Accepted: system-time deltas measure CPU load; host-load wait refuses the still-busy host with exit 2; busy children are owned through pid/parent/creation-time validation and retained handles, stopped and checked; the churn child adds short process starts and must remain alive at stop (flake-run.py:254–456,991–1083). Playwright tree termination uses its recorded pid. Row 3 includes unwatched hangs in back-off and records the chosen load and acceptance branch (task.md:51).

The floor measures the deliberately added load, the median is pooled over an invocation, and churn liveness does not measure a start rate. These stated limits remain accepted. Existing live ownership/cleanup receipts were inspected; no fresh live load/kill check is claimed here.

## Q4 — Pointer shield and diagnostics

Accepted: POINTER_SHIELD covers current and later windows, SHIELD_OPT_OUT retains diagnostics, and DIAG_DEFAULT_MAIN_ONLY preserves the special harness main. Installed Electron declarations describe mouse pass-through with retained keyboard input (ui/node_modules/electron/electron.d.ts:3332–3337). AC-9 checks native style bits and actual Playwright click/hover delivery, with the named 30,000 ms spawnSync bound; AC-10 checks opt-out (plan:424–425). MAIN_DIAG logs cover/visibility/minimize clues without disabling throttling; row 6 measures watched tests ×10 after enabling the shield (plan:244–259,302–304).

These are appropriate planned runtime checks. This review did not run the shield or Electron tests. No new defect on Q4.

## Q5 — Hang classification and excuse safety

Accepted: F1's exact split-signature identity and watched restriction remain; F2's clean test state is taken from the selected launch's last line, never from a launch-relative clock. Installed Playwright 1.64.1 still records timedOut/errors via _runWithTimeout/_failWithError while the callback may remain pending (workerProcessEntry.js:1101–1110,1130–1148). launch-end remains outside SPLIT_PHASES, so a stuck diagnostics evaluate is not a split excuse.

F3 is fixed by evidence ownership throughout the call chain: new_invocation → run_files → claim → child_env → run_playwright → diag_summary → excuse (flake-run.py:506–534,692–720,769–855,902–937,1001–1064). Foreign/missing ids, unreadable or malformed own lines, multiple repeats, a tied final launch or an unfinished earlier launch prevent an excuse. Only the final launch's last phase/state is eligible. Split with repeat other than 1 is refused (:1751–1759). Row 8 independently binds one invocation and runs 1..N.

The redesign closes the reviewed class: evidence from another invocation/run/test/repeat/earlier launch cannot substitute for this failing test's final launch under the stated producer contract. D-1150's four recorded limits remain visible (plan:778): an assertion pending through finally, dependence on phase writes, environment-carried run identity and possible worker-pid launch-id reuse. They are accepted residual limits, not newly discovered defects. The registered product-race exception and M-11 authority are judged as supplied; no policy question is reopened.

## Q6 — Scope and records

Accepted: PRODUCT_UNCHANGED and H1-4 keep product/API/tool files unchanged; allowed test changes, including the new unit file, are enumerated. Conditional MEU/build-plan edits register a product race for its own session. Row 9 uses the planned hash-bound issue adapter and tools/issue_triage* add/render operations, resolves the two pointer issues and resolves the launch issue only for in-spec (plan:362–368,445–503; task.md:59).

Every actual excuse is accumulated and printed as an individual final `excused:` line (flake-run.py:1055–1057,1084–1086), which row 8 captures for the handoff and H2-6. The real-runner fake-process probe confirmed one excuse is reported as one and captured by row 8's exact expression. No reporting defect remains. Row 0's citation re-probe and content baselines sufficiently handle Session 74 moving HEAD without touching ui/ (plan:541–574); a changed anchor triggers re-probing rather than reuse.

## Checklist Results

Manual observations below were made by codex-independent-reviewer and have null exit codes. Probe exit 0 means the asserted review cases passed; it does not certify Electron acceptance.

| Check | Result | Command / procedure | Exit | Evidence |
|---|---|---|---|---|
| PR-1 Plan/task alignment | pass | Compare AC-1–15, named contracts and rows 0–9/H1/H2 | null | Same fix order, binding rules and five-or-three-plus-ten acceptance. |
| PR-2 Not started | pass | Inspect canonical task statuses and four proposed test-side paths | null | Implementation rows unchecked; four new test-side paths absent. |
| PR-3 Task contracts | pass | Inspect owners, deliverables, validation commands and creation inventory | null | Planned future scripts have explicit creation rows; no materially missing executable. |
| PR-4 Validation realism | pass | Run actual runner with fake process; execute exact row-8 Python with scratch roots | 0 | Current body timeout fails; both acceptance branches and 11 negative/freshness cases behave as required. |
| PR-5 Source-backed planning | pass | Compare grouping §3, three issues, Session 90:101–124, expert pass and supplied authority | null | Correct 3/7 baseline, folded scope and handed decisions retained. |
| PR-6 Corrections readiness | pass | Compare F3 correction across phase producer contract, script consumers and task rows | null | Freshness redesign covers run and solo artifacts, parser/classifier and row-8 consumer. No paperwork blocker assessed. |
| PR-7 Scope discipline | pass | Trace exclusions and conditional registration against grouping and code | null | No disguised product fix or invented MEU; clipboard exclusions explicit. |
| PR-8 Reachability and fail-closed behavior | pass | Actual run → run_playwright → claim → child_env → parse_run → diag_summary → excuse → verdict, with fake Popen | 0 | Fresh registered close passes; second invocation timedOut close fails; collisions refuse before Popen. |
| PR-9 Named contracts | pass | Compare single-statement definitions with AC and task uses | null | No materially competing live predicate found. |
| Script selftests | pass | `rtk proxy python -B C:/Temp/av-kit/e2e-pointer-flakes/review/probe-round3.py` | 0 | flake-run 122 checks; assert-check 17; zero failures. |
| Row-8 invocation binding | pass | `rtk proxy python -B C:/Temp/av-kit/e2e-pointer-flakes/review/probe-row8-round3.py` | 0 | 13 checks passed against the exact task-cell code. |
| Product suites / full busy Electron runs | n/a | Reserved for execution; prohibited during this review | null | No runtime acceptance claim. |

### Independent probe evidence

Both commands ran from P:/av-kit with PYTHONDONTWRITEBYTECODE=1, PYTHONIOENCODING=utf-8 and RECEIPTS_DIR=C:/Temp/av-kit. All streams were redirected, exits captured immediately and completed receipts read.

| Probe | Decisive output |
|---|---|
| `probe-round3.py` | `flake-run selftest: exit=0, checks=122`; `assert-check selftest: exit=0, checks=17`; registered clean close: exit 0, one captured excuse; current body timeout: exit 1, no excuse; distinct folders and run ids; existing folder/receipt refused before Popen, old receipt bytes preserved. |
| `probe-row8-round3.py` | Clean five-run and three-plus-watch branches pass. Missing/doubled invocation, missing/duplicate run, foreign receipt/folder/run id, missing receipt, current rejection/evaluate-error and shared accept/watch invocation fail. Old invocation diagnostics containing evaluate-error are ignored. `13 checks passed`. |
| Author receipts inspected, not rerun | epf91-f3-mutants.txt: ten one-rule mutants killed, survivors []; epf91-sim-checks.txt: 33 ok, 0 failed. Independent results above supplement those receipts. |

The first integration-probe attempt failed its own assertion because its fake Busy did not supply the host-load signal; the corrected review harness explicitly supplies sample=75.0. No implementation changed and no busy child started. The final command's preserved exit is 0.

```json
{"schema_version": "evidence.v1", "check_id": "epf-r3-binding-probe", "command": "rtk proxy python -B C:/Temp/av-kit/e2e-pointer-flakes/review/probe-round3.py (PYTHONDONTWRITEBYTECODE=1)", "cwd": "P:/av-kit", "scope": "actual plan-local selftests and runner path with fake Playwright/load/watchers; scratch-only output", "phase": "plan-review", "exit_code": 0, "result": "pass", "tested_state": "d33b94f14ecea282a30e226e9675f4a028b626875c1624495d2c2bbfbbfa44a0", "output": "flake-run: 122 checks, 0 failures; assert-check: 17 checks, 0 failures. Registered clean close exit 0 and one reported excuse; second invocation body timeout exit 1. Fresh paths/ids; both existing-target collisions refuse before Popen.", "fresh": true}
```

```json
{"schema_version": "evidence.v1", "check_id": "epf-r3-row8-probe", "command": "rtk proxy python -B C:/Temp/av-kit/e2e-pointer-flakes/review/probe-row8-round3.py (PYTHONDONTWRITEBYTECODE=1)", "cwd": "P:/av-kit", "scope": "exact task.md row-8 Python predicate; synthetic receipts; scratch roots substituted", "phase": "plan-review", "exit_code": 0, "result": "pass", "tested_state": "d33b94f14ecea282a30e226e9675f4a028b626875c1624495d2c2bbfbbfa44a0", "output": "13 checks passed. Both branches pass; missing/doubled/foreign bindings and current errors fail; stale earlier diagnostics ignored.", "fresh": true}
```

Current four-file plan binding (SHA-256 of the sorted filename/hash mapping): `d33b94f14ecea282a30e226e9675f4a028b626875c1624495d2c2bbfbbfa44a0`.

## Recheck (round 2)

### Prior Pass Summary

| Finding | Prior Status | Recheck Result |
|---|---|---|
| F1 | open | fixed |
| F2 | open | fixed |

### Confirmed Fixes

- **F1:** split schema and excuse matcher enforce exact file/title plus phase and unwatched restriction (`flake-run.py:656,710,715`). The new negative cases cover another file, another test and a partial title (`:1287–1305`); the independent probe confirms them.
- **F2:** clean_launch reads last-phase status/errors and refuses absent or mistyped state (`flake-run.py:634–653,737–743`). Five-second pre-launch setup followed by a body timeout/finally-close is not excused (`:1307–1326`). Product-race excuses also require clean state (`:707–714`). Installed-source verification supports PHASE_LINES's timeout claim. The old first-launch test_start inference is gone.
- The bounded spawn in `task.md:48` now agrees with AC-9 and NO_NEW_WAIT_KNOBS.

### New Findings

| # | Severity | Blocking | Kind | Finding | File:Line | Recommendation | Status |
|---|---|---|---|---|---|---|---|
| F3 | High | yes | control-defeat | **Acceptance reruns reuse stale phase evidence and can excuse a current body timeout.** Confidence: High. Violates AC-13; mechanism: task-row-completion-predicate. S9 repeats row 8 using the same label `accept`. run_playwright only mkdirs `epf-accept-1-diag` with exist_ok=True; PHASE_LINES appends to its old phases.jsonl. If an earlier attempt had a legitimately registered clean close hang and some other watched failure triggered S9, that clean launch remains when the corrected acceptance runs again. diag_summary includes both attempts; excuse accepts any matching clean launch. The probe's current launch records timedOut/1 at close-start, but the old passed/0 close supplies the excuse and the real parser/classifier returns verdict 0. The same current failure in a fresh directory returns 1. This can certify an unregistered body hang as the old close signature. | `docs/execution/plans/2026-11-17-e2e-pointer-flakes/flake-run.py:803`, `:925`, `:725`, `:715`; `implementation-plan.md:232`, `:618`; `task.md:58` | Give each invocation/run a fresh diagnostic directory, or refuse an existing directory before launching, and have row 8 inspect that invocation's paths. Add a two-invocation regression: stale registered clean-close evidence must not excuse a current timedOut body/finally-close. | open |

This is a new evidence-lifetime failure across acceptance invocations, reachable through S9's prescribed rerun. It does not dispute F1's corrected exact comparison or F2's corrected current-launch state, and does not escalate the already-recorded repeat/title aggregation note. The committable acceptance script carries the defect; it is not review scaffolding. The closed vocabulary's task-row-completion-predicate mechanism is retained rather than inventing a new slug.

### Verdict

**changes_required** — F1 and F2 are fixed. F3 is an evidence-backed High finding that still lets busy-host acceptance pass a body timeout outside the registered excuse. Isolate the current invocation's phase evidence and prove the two-invocation negative case. The review does not alter the plan, record a ledger transition or claim execution completion.

## Recheck (round 3)

Date: 2026-11-18. Rechecked under Mat's supplied continuation for task-row-completion-predicate. The redesign, rather than a further predicate patch, is accepted.

### Prior Pass Summary

| Finding | Prior Status | Recheck Result |
|---|---|---|
| F1 | fixed | fixed |
| F2 | fixed | fixed |
| F3 | open | fixed |

### New Findings

| # | Severity | Blocking | Kind | Finding | File:Line | Recommendation | Status |
|---|---|---|---|---|---|---|---|

No new findings.

### F3 disposition and evidence

- Fresh invocation identity is applied to per-run receipts, diagnostics, solo reruns and the process-start file. claim creates the folder without exist_ok and the receipt with xb; either existing target raises before Playwright starts (flake-run.py:521–534,880,902–937,1001–1039). Failure after the first claim step can leave an empty new folder, but cannot launch or consume old evidence.
- child_env removes an inherited run id before setting the current one. diag_summary matches run id, bare file, integer line and exact title/describe leaf; foreign/missing ids and unreadable/malformed own records fail closed (flake-run.py:506–518,692–713,804–850).
- excuse selects only the uniquely final launch, requires earlier launches at exit and one repeat, and checks the final line's clean test status/errors before signature matching (flake-run.py:769–800). The 122-check selftest includes both invocations in one phases.jsonl, foreign-late lines, wrong identity, repeat/tie/unfinished-launch and malformed-line cases (:1521–1700).
- Row 8 requires exactly one invocation, runs 1..N, exact invocation-derived names and run ids, and distinct receipts/folders/invocations; it reads rejection/diagnostics data only through those names (task.md:58; plan:353–360). Independent execution of that exact predicate passed 13 positive/negative cases.
- The independent actual-runner probe passed a registered clean-close case, then rejected the same test's current timedOut finally-close in a second invocation. Existing-folder and existing-receipt cases stopped before fake Popen and preserved old bytes. The reporting path emitted and row 8 captured the legitimate excuse.

### Verdict

**approved** — F3 is fixed and F1/F2 remain fixed. No evidence-backed High/Critical delivery defect remains. No further correction requested in this plan-review loop. Carry out the authorized plan and obtain its real busy-host acceptance and independent execution review; this verdict does not claim those runs already passed.

## Verdict

**approved** — intent achieved for plan review: executing this plan as written would deliver the registered objective, within D-1150's explicit residual limits. Complete rolling report: C:/Temp/av-kit/epf-plan-review-round-3.md. Repository remains read-only; the coordinator owns canonical copying and ledger recording.
