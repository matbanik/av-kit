---
date: "2026-11-15"
review_mode: "plan"
target_plan: "docs/execution/plans/2026-11-15-e2e-harness-hardening/implementation-plan.md"
verdict: "approved"
findings_count: 0
template_version: "2.2"
requested_verbosity: "standard"
agent: "codex-independent-reviewer"
loop_id: "ehh-plan-2026-11-15-e2e-harness-hardening"
round: 3
---

# Critical Review: 2026-11-15-e2e-harness-hardening

> **Review Mode:** plan
> **Verdict:** approved

The original Findings table and round-1/round-2 assessments below are retained as history. **Current result: approved; zero open findings.** See **Recheck (round 3)**: R2-F1 is fixed, and R1-F2 and R1-F4 remain fixed. Historical open statuses and changes_required verdicts describe those earlier states only. Frontmatter describes round 3.

## Scope

**Intent anchor:** every Electron E2E launch goes through one helper that drops `ELECTRON_RUN_AS_NODE` from the environment it passes and fails the test when the main process throws an uncaught exception; Vitest installs the Electron binary once, before any worker starts; and Capture's AC-97.4 hint tests fail when the Save or Region chord is wrong.

Reviewed the working-tree implementation-plan.md, task.md and all eleven plan-local scripts; the launch blocks and close paths in the twenty E2E files; relevant main-process/profile code, hint components/tests, installed Electron/Playwright/Vitest sources, CI, grouping Session 78 and its issue records. Applied PR-1–PR-9 and the Materiality Gate. Claude Code/Anthropic authored the plan; this reviewer is Codex and did not author it.

This is a fresh ledger round 1. Findings retain the earlier unrecorded report's R1-F2 identifier for the unresolved ownership correction; R1-F4 is new. No Recheck section is applicable. Repository files remained read-only. No product suite, npm command, uv operation, network request or real process termination was performed. Scratch scripts and outputs are under C:/Temp/av-kit/e2e-harness-hardening/review.

## Findings

| # | Severity | Blocking | Kind | Finding | File:Line | Recommendation | Status |
|---|---|---|---|---|---|---|---|
| R1-F2 | High | yes | behavior | **Ownership is forgotten across a PID reuser's exit, allowing an unrelated Electron process to be stopped.** `Update-OwnedSet` retains old owned PID identities indefinitely but checks for a reuser only in the current snapshot. In the independent three-snapshot fixture, owned PID 105 exits; unrelated PID 105 starts child 106; while the reuser is alive, 106 is correctly excluded. Once the reuser exits, 106 is attributed to the original owned 105 and selected for termination. `Stop-OwnedElectron` then stops that unrelated same-binary process. This can interrupt Mat's or another session's app during a long suite and violates **AC-10**. Confidence: High; reproduced by pure functions with no real process actions. | docs/execution/plans/2026-11-15-e2e-harness-hardening/owned-procs.ps1:27; owned-procs.ps1:29; owned-procs.ps1:33; owned-procs.ps1:89 | Bind parent attribution to process lifetimes across snapshots, preserving observed PID-reuse history and refusing ambiguous ancestry. Preserve already proven descendants. Add the three-snapshot reuser-exits/child-survives negative; do not infer ownership from a historical PID plus the absence of a current reuser. | open |
| R1-F4 | High | yes | behavior | **The new harness tests launch against the normal app profile and can terminate an existing development backend.** Row 2 directs the new tests to call `launchElectron()` without an app-data override; `ONE_LAUNCH_PATH` supplies only the error-log variable, and `ENV_DROP_FLAG` adds only `AVKIT_E2E`. Unlike all twenty existing site files, the new default-main tests therefore fall back to the normal app-data folder when the parent has no override. `AVKIT_E2E` bypasses the instance lock; boot still reads the normal token/profile, evaluates the existing backend with `lockHeld: true`, and calls `process.kill` for `reap_then_spawn`. A pure-source probe with another development backend on the same Python image/profile returns that decision and its foreign PID. Normal launch/close also writes profile state outside the session scratch directory. This violates **AC-10**'s only-own-process rule, independently of the cleanup script. Confidence: High. | docs/execution/plans/2026-11-15-e2e-harness-hardening/task.md:53; implementation-plan.md:140; implementation-plan.md:224; ui/src/main/index.ts:149; ui/src/main/index.ts:221; ui/src/main/index.ts:258; ui/src/main/live-identity.ts:74 | Give each new real-main test a fresh `AVKIT_APP_DATA` under the session's scratch directory, including the intentional-error cases; preserve migrated callers' existing overrides. Isolate the startup fixture's Electron userData/session storage too. Add an oracle for scratch profile selection so no new harness case can reach the normal profile or a backend it did not launch. No product-code change is needed. | open |

## Earlier unrecorded observations

| Observation | Current assessment | Evidence |
|---|---|---|
| Earlier R1-F1: startup exception missed | fixed in the plan | Per-launch log exists from preload startup; CLOSE_CHECK reads it after close; AC-7 has startup and post-launch cases (implementation-plan.md:140–156,226). The supplied startup receipt contains a full first-tick error record. |
| Earlier R1-F2: path/time-only cleanup | partial | The old broad selector is removed and unrelated same-path apps are excluded by the supplied seven fixtures. R1-F2 above demonstrates that ancestry remains unsafe after a PID reuser exits. |
| Earlier R1-F3: stack lines dropped | fixed in the plan | MAIN_ERROR_WATCH records full `{name,message,stack}`; `mainErrorRecords` retains parsed stacks or raw malformed lines; AC-3/4 and AC-7 assert frames (implementation-plan.md:147–156,222–226). |

These are assessments of corrected plan contracts, not claims that the future helper has already passed runtime tests.

## Q1 — Goal and proving rows

Accepted: ONE_LAUNCH_PATH and SITE_MIGRATION have AC-2/9 and rows 4–6; ENV_DROP_FLAG has AC-1/5/18 and rows 1–3/6; MAIN_ERROR_WATCH and CLOSE_CHECK have AC-3/4/6/7/8 and rows 1–3. INSTALL_ONCE has AC-12/13 and rows 7/8; HINT_VALUES has AC-14/15/16 and rows 9–11. Each goal clause has a producer, observable and negative case. NEW_FAILURE_RULE retains the stop/register rule and forbids skipping or expected failures.

Not accepted: safe execution of that contract. Both AC-10 defects can disrupt an app/backend outside this run even if the intended harness assertions pass. Intent is therefore partial pending these corrections.

## Q2 — Helper, log lifecycle and teardown

Accepted: installed Playwright prepends its loader and accepts the following `-r` preload before initializing main (coreBundle.js:45675–45780). The supplied startup receipt shows the watch loaded, the log variable hidden from main, a complete first-tick stack and subsequent window creation. The planned fixture keeps its window alive until close instead of auto-quitting before assertions. Per-launch folders avoid cross-launch log mixing; rejected launches remove their folder; a missing log fails closed; malformed records are retained; memoized close prevents a second close from erasing the first error. Reading after close covers startup and shutdown errors without relying on late stderr listeners.

The original close remains first; the added process-exit wait is bounded at five seconds and cannot itself hang indefinitely. This does not prove the older close/launch hang is gone: keeping CAPTURE-E2E-LAUNCH-TEARDOWN-HANG unchanged and MONITORING is appropriate. NEW_FAILURE_RULE fixes helper defects and registers/stops on product or deliberate-main-throw failures. The rejection probe supports tracking promise rejections separately.

Not accepted: ownership cleanup (R1-F2) and the new tests' profile selection (R1-F4). The latter also applies to setup of the intentional startup-error fixture. No additional concrete error-channel defect was demonstrated.

## Q3 — INSTALL_ONCE

Accepted: `createRequire` bypasses the Vite alias; the installed Electron index synchronously invokes install.js when path.txt or the executable is missing (index.js:25–52). Vitest awaits global setup before its worker pool and calls setup with the project, accepting an undefined return (index.1TqnEahn.js:6555–6570). The default wrapper calls `ensureElectronBinary()` without forwarding project, provides the path, and returns nothing. AC-12 checks success, require failure, nonexistent path, return value and provide call. AC-13's `inject` observes this run's setup rather than merely importing it in a worker.

When installation fails offline, the setup throws before workers and names the recovery command. CI's existing serial install after `npm ci --ignore-scripts` stays compatible; setup finds the already-installed binary. D-937 and D-939 implement the supplied hand-over and expert-pass corrections; neither introduces another mandatory-human category outside the allowed set. No rejection on this surface. No binary was removed or installation attempted during review.

## Q4 — Red/Green, hints and run discipline

Accepted: missing modules are asserted before dynamic import, avoiding collection-only Reds; red-check requires failed selected assertions and rejects launch/time-out/setup failures. Its 36 fixtures pass. The startup and post-launch AC-7 cases exercise distinct timing. HINT_VALUES checks registry-derived source values and rendered controls; the source Region slice includes the complete title, and the behavior setup dirties the overlay to mount Save. The Ctrl+O mutant changes Save and both Region hints; old-test Green followed by both new-test Reds establishes the regression oracle. mutation.py preserves bytes and timestamps on restore; its scratch selftest passes.

Vitest commands run from pwsh using `npm --prefix ui`; npm executes the package script in ui, consistent with commands.md:193, so a literal extra `Set-Location ui` is unnecessary. Electron wrappers clear the flag except the two deliberate flag cases. D-941 limits one repeat to the named MONITORING teardown/clipboard signatures and requires both runs to be retained. No blanket retry or skip is prescribed. Actual product Red/Green runs remain future execution evidence, not reviewer results.

Not accepted: the new E2E test setup's unisolated default main (R1-F4).

## Q5 — Order, baselines, scope and registers

Accepted: baseline-sites.json records the live row-0 count; site-check derives values/order/spreads/EOLs from BASE. An in-memory projection of all 21 current sites passes; a simulated Session 75 append through `launchApp` also passes. The six sibling anchors are currently unique, and all eight scheduled new files are absent. untouched-check compares content maps, allowing sibling changes present before row 0. scope-check's before-row predicate detects a scoped edit before its writer row; its six fixtures pass. CRLF is preserved by byte-aware edits/checks, including the temporary mutant. No clean-tree or equality-to-HEAD baseline is required.

The register update is restricted to approved issue fields and bound to the row-0 hash under a held Windows handle; new entries/rendering use issue_triage tools. The D-936 rebind is an explicit stopped path, not an excuse to overwrite concurrent register content. Session 75–77 work and Session 87 closeout are not this review's changes. Supplied authorization permits execution after approval; commits remain unapproved for Session 78.

Not accepted: R1-F4 makes rows 3/6/the gate reach normal profile files and potentially stop a foreign backend; R1-F2 makes cleanup select a foreign Electron descendant. The path/content checks cannot prevent either runtime effect.

## Checklist Results

Manual observations below were performed by codex-independent-reviewer; their exit codes are null. These evaluate plan readiness.

| Check | Result | Procedure | Exit | Evidence |
|---|---|---|---|---|
| PR-1 Plan/task alignment | pass | Compare whole plan/task and row dependencies. | null | Same four issues, helper → migration → install → hints → register order, and H1/H2 closeout. |
| PR-2 Not started | pass | Inspect task statuses and eight declared new paths. | null | Implementation rows unchecked; all eight new deliverables absent. |
| PR-3 Runnable task contract | pass | Read every task row and all plan-local scripts. | null | Named scripts exist; product helpers/tests are explicitly scheduled before use. |
| PR-4 Validation realism | fail | Trace launch setup and process cleanup into actual app/ownership source; run the two probes below. | null | AC-10 unsafe in both cleanup ancestry and new default-main tests. |
| PR-5 Sources/HDP | pass | Compare grouping/issue scope, D-933–D-941, expert receipt and HDP §4a/5/5a/6. | null | Named assertion changes and handed-over defaults are supported; no additional policy objection. |
| PR-6 Corrections readiness | pass | Inspect rolling review paths and correction loop; assess supplied unrecorded observations. | null | F1/F3 corrected in plan; F2 remains actionable; no recorded earlier round or round-2 census gate applies. |
| PR-7 Scope discipline | pass | Compare stated exclusions with grouping and decisions. | null | Dev symptom/rejections get issues; real product errors stop for Mat; no hidden MEU deferral. Runtime isolation defect is reported separately. |
| PR-8 Reachability/negative oracles | fail | Trace ownership selection to Stop-Process and no-override launch to boot/process.kill. | null | Supplied ownership fixtures pass while the additional three-snapshot negative fails; default profile reaches a foreign backend. |
| PR-9 Named contracts | pass | Compare canonical contracts with AC and row references. | null | No materially ambiguous competing behavior found. |
| Product suites | n/a | Not run under the read-only review packet. | null | No pytest, Vitest, npm, install/build or network execution. |

### Probe and evidence records

Reviewed content identity: implementation-plan.md SHA-256 `3a6127161431fd4cd834442a800894acb4053559a36cebd0010fb7cdd07ba19a`; task.md `b0e65456251d939323ecf347ea8a95380260601e286551b613fc1a22a24699bd`; owned-procs.ps1 `b95b08e508e8e066adc21855921e8f1460e4f320ed08ae04b66469cd050d0d32`. The static receipt embeds all thirteen plan-folder file hashes.

```json
{"schema_version":"evidence.v1","check_id":"ownership-reuser-exits","command":"rtk proxy pwsh -NoProfile -File C:/Temp/av-kit/e2e-harness-hardening/review/owned-reuse-probe.ps1","cwd":"P:/av-kit","scope":"pure Update-OwnedSet/Select-OwnedLeftovers fixture; no process actions","phase":"static","exit_code":1,"result":"fail","tested_state":"owned-procs.ps1-sha256:b95b08e508e8e066adc21855921e8f1460e4f320ed08ae04b66469cd050d0d32","output":"while unrelated reuser is alive: selected=\nafter unrelated reuser exits: selected=106\nexpected: unrelated child 106 is never owned or selected; no real process was started or stopped\nAC-10 ownership safety: FAIL","fresh":true}
```

```json
{"schema_version":"evidence.v1","check_id":"default-profile-foreign-backend","command":"rtk proxy node --experimental-strip-types C:/Temp/av-kit/e2e-harness-hardening/review/default-profile-probe.mjs","cwd":"P:/av-kit","scope":"isolated defaultAppData function and pure evaluateLiveIdentity with synthetic environment/descriptor","phase":"static","exit_code":1,"result":"fail","tested_state":"plan-sha256:3a6127161431fd4cd834442a800894acb4053559a36cebd0010fb7cdd07ba19a;working-tree ui/src/main/index.ts and live-identity.ts","output":"planned no-override test launch appData=<HOME>/AppData/Local/av-kit\nexisting other-session development backend: {\"decision\":\"reap_then_spawn\",\"signalPid\":424242}\nboot lines 258-260 signal signalPid for reap_then_spawn; no process or user profile was accessed by this probe\nAC-10 only-owned-process safety: FAIL","fresh":true}
```

```json
{"schema_version":"evidence.v1","check_id":"projected-migration-and-content-baselines","command":"rtk proxy python C:/Temp/av-kit/e2e-harness-hardening/review/static-probes.py","cwd":"P:/av-kit","scope":"in-memory migration through real site-check; live anchors/new paths; pure content/S2 checks","phase":"static","exit_code":0,"result":"pass","tested_state":"plan-sha256:3a6127161431fd4cd834442a800894acb4053559a36cebd0010fb7cdd07ba19a;task-sha256:b0e65456251d939323ecf347ea8a95380260601e286551b613fc1a22a24699bd","output":"projected current-site migration: 21 sites / 20 files preserve all args/env/spreads/endings\nsynthetic uncommitted sibling append in BASE: accepted without HEAD comparison\nrow-0 sibling anchors: 6/6 unique; planned new deliverables: 8/8 absent\ncontent-bound skip and S2 negatives: unchanged sibling passes; later edit refused before writer row\nstatic probes: PASS; projected migration is a model, not implemented product verification","fresh":true}
```

The projected migration also updates the old `_electron` mention in download-queue.test.ts's diagnostic comment to satisfy the contract's source census; no test body or assertion is changed by that model. Scratch probe setup was corrected before its passing run; these are model observations, not future implementation passes.

| Executed command (each through rtk proxy, receipt redirected under review/) | Exit | Decisive output |
|---|---|---|
| `python docs/execution/plans/2026-11-15-e2e-harness-hardening/site-check.py --selftest` | 0 | `site-check selftest: 13 fixture(s), 0 wrong: []` |
| `python docs/execution/plans/2026-11-15-e2e-harness-hardening/scope-check.py --selftest` | 0 | `scope-check selftest: 6 of 6 passed` |
| `python docs/execution/plans/2026-11-15-e2e-harness-hardening/red-check.py --selftest` | 0 | `red-check selftest: 36 fixture(s) (11 positive, 25 negative), 0 wrong: []` |
| `python docs/execution/plans/2026-11-15-e2e-harness-hardening/mutation.py --selftest` | 0 | `mutation selftest: 0 failure(s) []` |
| `pwsh -NoProfile -File docs/execution/plans/2026-11-15-e2e-harness-hardening/owned-procs.ps1 -Selftest` | 0 | `owned-procs selftest: 7 of 7 passed` |

Python probes used PYTHONDONTWRITEBYTECODE=1; scratch temporary directories were directed under the assigned review directory. identity.py and issue-resolve.py were source-reviewed, not run against the real tree/register.

Artifact validation (`rtk proxy python C:/Temp/av-kit/e2e-harness-hardening/review/validate-artifacts.py`, exit 0) validated the JSON against the repository v2 schema and parsed this report as plan / changes_required / round 1 / two open blocking findings. It confirmed all thirteen plan-folder files still match their probed hashes. The profile-source hashes are ui/src/main/index.ts `f05fe07dbc76ea43dbed089e51ab464bc95a04543878fcd475c627e2f3840241` and ui/src/main/live-identity.ts `25d411f4dccb722c316b34b19fcd2aafe65b96e04e219b94074567f519dd7cf3`. No ledger mutation was performed.

## Verdict

**changes_required** — two evidence-backed High safety defects violate AC-10. Correct ownership across PID reuse and isolate the new harness tests before execution. Earlier startup-loss and stack-loss findings are fixed in the plan; the earlier ownership finding remains partial. No additional blocking issue was found in INSTALL_ONCE, HINT_VALUES, migration preservation or content-bound sibling baselines. The coordinator should copy this complete report to the canonical review path; this reviewer has not edited it or the ledger.


## Recheck (round 2)

**Date:** 2026-11-15. **Reviewer:** codex-independent-reviewer (Codex, class avkit_independent_reviewer). Claude Code/Anthropic remains the plan author. Reviewed the working-tree plan/task and plan-local scripts. No repository file or ledger state was edited.

**Intent anchor:** every Electron E2E launch goes through one helper that drops `ELECTRON_RUN_AS_NODE` from the environment it passes and fails the test when the main process throws an uncaught exception; Vitest installs the Electron binary once, before any worker starts; and Capture's AC-97.4 hint tests fail when the Save or Region chord is wrong.

### Prior Pass Summary

| Finding | Prior Status | Recheck Result |
|---|---|---|
| R1-F2 | open | fixed |
| R1-F4 | open | fixed |

### Confirmed Fixes

- **R1-F2 fixed:** `owned-procs.ps1:40–62` retains PID identity history and last-alive times. `:70–71` updates history, and `:79` admits only proven children. The supplied four-snapshot reuser-exits case is now refused (`:214–215`); the independent selftest passed 17/17. Equal creation timestamps are refused (`:53`), and children whose unpinned parent was last seen before their start are refused (`:57`). This can leave genuine but unprovable orphans running, explicitly listed by `:152–153`; it does not transfer ownership to another app. `Invoke-OwnedRun` opens the root handle at `:122` and retains its Process object through the last snapshot. Root pinning supports the history rule while that function runs.
- **R1-F4 fixed:** `implementation-plan.md:150–155` requires the caller's own scratch override before allocation or launch. `task.md:53` assigns a separate fresh folder to each new E2E case and checks both profile paths. AC-19 (`implementation-plan.md:245`) specifies invalid-path negatives and the profile-path oracle; it is discussed here without using the unregistered id as a ledger violation. The startup fixture sets userData/sessionData inside its folder before ready and exits 3 without the override (`implementation-plan.md:193`). Existing caller overrides remain unchanged under SITE_MIGRATION. This closes the demonstrated route into the normal profile and foreign backend. Runtime Green remains execution work.

### New Findings

| # | Severity | Blocking | Kind | Finding | File:Line | Recommendation | Status |
|---|---|---|---|---|---|---|---|
| R2-F1 | High | yes | behavior | **A correctly proven owned process can be replaced before the PID-only stop.** Cleanup checks `(pid, creation time)` from a CIM snapshot, then calls `Stop-Process -Id` without holding a handle to that selected process. If it exits and the PID is reused in between, another app is terminated. The independent synthetic probe of the actual function selected owned identity `120 / 639303336020000000` and stopped unrelated replacement `120 / 639303336070000000` (`owned=False`). The root handle pins only the launcher, not these candidates. Violates **AC-10**. Confidence: High. This is a distinct termination-identity failure after correct ancestry classification, not a reopening of R1-F2's corrected classification rule. | docs/execution/plans/2026-11-15-e2e-harness-hardening/owned-procs.ps1:146; owned-procs.ps1:150 | Acquire a candidate handle, verify its creation time through that handle and keep it through handle-based termination. Refuse exited/unproven candidates. A fresh snapshot followed by another PID-only stop still races. Add an exit/reuse interleaving at this boundary. | open |

### Q1 — Goal

Accepted: ONE_LAUNCH_PATH, SITE_MIGRATION and ENV_DROP_FLAG have AC-1/2/5/9/18 and rows 1–6; MAIN_ERROR_WATCH/CLOSE_CHECK have AC-3/4/6/7/8/10 and startup plus after-launch tests; INSTALL_ONCE has AC-12/13 and rows 7–8; HINT_VALUES has AC-14/15/16 and rows 9–11. If those behavior rows pass, the three stated goal clauses are covered. Safe execution is still blocked by R2-F1 under AC-10. No goal deliverable was silently dropped.

### Q2 — Helper, ancestry and scratch guard

Accepted: installed Playwright prepends its own loader before the supplied `-r` watch (`coreBundle.js:45698`), initializes main before returning (`:45780`), and the supplied startup log probe supports this order. The file channel retains startup and full-stack records; memoized close adds a bounded five-second exit wait after the original close. The prior teardown hang stays MONITORING. NEW_FAILURE_RULE fixes helper faults and registers/stops for other main-process faults without skipping a spec.

Accepted: strict creation-time ordering and conservative last-alive checks fail closed for clock-resolution ties and first-seen orphans. The root handle is retained while snapshots are attributed. SCRATCH_PROFILE rejects missing/empty/root/outside paths before launch; every new case has a fresh profile and an oracle for userData/sessionData, while migrated caller environments are preserved. Not accepted: root pinning does not protect the later candidate stop (R2-F1).

### Q3 — INSTALL_ONCE

Accepted: Electron's installed index invokes `install.js` synchronously on a missing path/binary (`index.js:25–52`); `createRequire` bypasses Vite's electron stub. Vitest awaits global setup before `pool.runTests` (`cli-api.De07GUeT.js:12869–12871`). `setup(project)` returns undefined and provides the path; AC-12 checks the wrapper and error paths, and AC-13 reads this run's injected value. Present binary, missing binary and offline install failure follow the planned paths; CI's own serial install after `npm ci --ignore-scripts` remains compatible. No new defect demonstrated. No install or binary removal was attempted.

### Q4 — Tests and run discipline

Accepted: the missing-module Reds assert existence before dynamic import; red-check requires the named assertion failures. Its 36 fixtures passed again. The hint source assertions use registry chords, and the rendered test dirties the overlay to mount Save; the Ctrl+O mutant must pass the old test and fail both new tests, then restore bytes/mtime. The scratch mutation selftest passed. Commands run Vitest in pwsh with `npm --prefix ui`, which gives the package script ui as cwd. Electron wrappers clear the flag except deliberate flag runs. D-941 confines one repeat to the named MONITORING signatures and retains both attempts. Product Red/Green runs were not executed by this reviewer.

### Q5 — Order, baselines, scope and registers

Accepted: row 0 derives launch counts, shared anchors and BASE copies from the execution-start content, accommodating Session 75's appended test and uncommitted Sessions 75–77 work. The in-memory 21-site migration and synthetic sibling append passed the real site-check; 13 site fixtures and 6 scope fixtures passed. Byte-aware checks preserve CRLF. untouched-check compares content maps, not clean-tree/HEAD equality. issue-resolve retains a writer-excluding register handle and checks the expected row-0 hash before restricted field updates; additions/rendering use issue_triage. No new register or file-write defect was demonstrated. Not accepted: cleanup may affect a process outside this session despite those file checks (R2-F1). Session 78 remains uncommitted, as authorized.

### Checklist Results

Manual observations were made by codex-independent-reviewer, with null exit codes; command rows show their preserved native exit.

| Check | Result | Procedure or command | Exit | Evidence |
|---|---|---|---|---|
| PR-1–PR-3 | pass | Read the full revised plan/task; inspect scheduled paths. | null | Aligned goal/row order; all eight new product/test paths absent; implementation unchecked. |
| PR-4 / PR-8 | fail | Run r2-owned-probes.ps1; trace selection to Stop-Process. | 1 | Correct owned selection can terminate the unowned replacement; R2-F1. |
| PR-5 | pass | Read HDP sections 4a/5/5a/6, D-933–D-941 and supplied expert/rejection evidence. | null | Handed-over defaults carried out; no additional mandatory-human category demonstrated. |
| PR-6 | pass | Compare both prior findings to revised source, task rows and four-snapshot fixtures. | null | Both named prior failures fixed; complete rolling report retains original ids/evidence. Paperwork is not a delivery finding. |
| PR-7 / PR-9 | pass | Compare named contracts, scope and exclusions with grouping and issue records. | null | No hidden required work or materially ambiguous behavior found. |
| Ownership selftest | pass | `rtk proxy pwsh -NoProfile -File docs/execution/plans/2026-11-15-e2e-harness-hardening/owned-procs.ps1 -Selftest` | 0 | 17 of 17 passed. |
| Migration, row-0 anchors and sibling content | pass | `rtk proxy python C:/Temp/av-kit/e2e-harness-hardening/review/static-probes.py` | 0 | 21 sites / 20 files projected; 6 anchors unique; 8 paths absent; synthetic sibling append and later-change negative pass. |
| Parser / source-preservation fixtures | pass | Run plan-local `red-check.py`, `site-check.py`, `scope-check.py`, `mutation.py`, each with `--selftest`, via `rtk proxy python`. | 0 | 36 red fixtures; 13 site fixtures; 6 scope fixtures; zero mutation failures. Individual receipts retain each native exit. |
| Product runtime and network | n/a | Not run under read-only review scope. | null | No product suite, install, network request or real process termination. |

### Probe evidence

Current content: implementation-plan.md SHA-256 `6c6727481ea4eac491c280852cd8d4824565f505eae3a0a5abec47171a3a05de`; task.md `0e13c5786ea413d4b7fca722cbdf74ee162c16ee32ad9870a016713be56a02fa`; owned-procs.ps1 `cd2f1623a5314a6282216a26dd92bf015f12b8d781a2b246bc436e7dd7f4e314`. The round-2 static receipt records all thirteen plan-folder identities. Older hashes above belong to round 1 only.

```json
{"schema_version":"evidence.v1","check_id":"stop-candidate-pid-reuse","command":"rtk proxy pwsh -NoProfile -File C:/Temp/av-kit/e2e-harness-hardening/review/r2-owned-probes.ps1","cwd":"P:/av-kit","scope":"Actual Stop-OwnedElectron with mocked process snapshot and stop; no real process action","phase":"static","exit_code":1,"result":"fail","tested_state":"owned-procs.ps1-sha256:cd2f1623a5314a6282216a26dd92bf015f12b8d781a2b246bc436e7dd7f4e314","output":"parent exits before child first seen: owned child count=0\nequal creation stamp: owned child count=0\nsynthetic-stop-race: left running pid=120 path=P:\\av-kit\\ui\\node_modules\\electron\\dist\\electron.exe; launched by this run, stopping it\nsynthetic-stop-race: 1 leftover electron.exe launched by this run (1 processes recorded)\nselected original=120|639303336020000000; stopped current=120|639303336070000000; owned=False\nAC-10 stop identity: FAIL (synthetic interleaving; no real process action)","fresh":true}
```

The negative probe substitutes the OS boundary only. It demonstrates an allowed exit/PID-reuse interleaving against the real cleanup function; it does not claim that a foreign app was actually killed on this host. Last-alive and equal-time cases in the same probe both returned zero owned children. Python fixture/model runs used PYTHONDONTWRITEBYTECODE=1 and scratch temp directories. Baseline, full session-gate, identity collection over the real tree and issue-resolve mutations were not executed.

### Verdict

**changes_required** — R1-F2 and R1-F4 are fixed. R2-F1 is a new High AC-10 safety defect at the stop boundary. Preserve the revised ancestry and scratch-profile design; bind each termination to its checked process identity before execution. INSTALL_ONCE, HINT_VALUES, helper error capture and content-bound migration remain accepted. The coordinator saves this complete rolling report to the canonical path after validation; this reviewer has written only under C:/Temp/av-kit.

## Recheck (round 3)

**Date:** 2026-11-15. **Reviewer:** codex-independent-reviewer (Codex, class avkit_independent_reviewer). Claude Code/Anthropic authored the plan; this reviewer did not. This is the final permitted plan round. The review applied PR-1 to PR-9 and the Materiality Gate to delivery and safety, without paperwork findings.

**Intent anchor:** every Electron E2E launch goes through one helper that drops `ELECTRON_RUN_AS_NODE` from the environment it passes and fails the test when the main process throws an uncaught exception; Vitest installs the Electron binary once, before any worker starts; and Capture's AC-97.4 hint tests fail when the Save or Region chord is wrong.

Reviewed the complete current plan/task, revised ownership script and its callers, relevant installed Electron/Playwright/Vitest sources, Capture hint/profile code, grouping Session 78 and issue records, and the supplied expert/startup/rejection/stop evidence. Compared all thirteen plan-folder hashes with round 2: only implementation-plan.md, task.md and owned-procs.ps1 changed. Re-ran the plan-local pure fixtures and in-memory migration model. No repository or ledger file was edited; no product suite, npm/uv operation, install, network request, real Electron launch or real process termination was performed. Scratch fixtures and reports were written only under C:/Temp/av-kit.

### Prior Pass Summary

| Finding | Prior Status | Recheck Result |
|---|---|---|
| R1-F2 | fixed | fixed |
| R1-F4 | fixed | fixed |
| R2-F1 | open | fixed |

### Confirmed Fixes

- **R2-F1 fixed — AC-10:** `owned-procs.ps1:154-175` opens each selected candidate through the injectable opener, touches `.Handle`, reads `.StartTime` from that object, compares both creation times at whole-microsecond resolution, and calls that object's `Kill($false)` only on equality. The same object remains held through termination and is disposed in `finally`. A replacement acquired before the handle opens is refused by its start time; after the handle opens, the original process identity remains pinned. Open/read/kill failures return `gone`; unequal times return `mismatch`. `Stop-OwnedElectron` uses this function at `:185` and lists every outcome other than `stopped` as not stopped (`:186-195`). The real opener is `Process.GetProcessById` (`:177`); there is no Stop-Process call. This closes the demonstrated snapshot-to-PID-only-stop race.
- **R1-F2 remains fixed — AC-10:** history, last-alive proof and strict parent/child creation ordering remain in `owned-procs.ps1:44-89`. The four-snapshot negative still refuses child 106 after its unrelated PID-reusing parent exits (`:253-257`); ambiguous children stay unowned and are listed, rather than killed.
- **R1-F4 remains fixed — AC-10:** SCRATCH_PROFILE still checks the caller's own override before allocation/launch (`implementation-plan.md:150-155`). `task.md:53` requires every new real-main test to use its own fresh folder and check userData/sessionData. The startup fixture sets both paths within that folder and refuses a missing override (`implementation-plan.md:193`). This removes the demonstrated default-profile route into another app's backend (`ui/src/main/index.ts:221-260`). The additional scratch-profile AC remains unregistered; this assessment cites registered AC-10 for process safety.

The ownership selftest independently passed **26/26**, including a replacement started five seconds later, exits at the open/read/kill boundaries, the one-microsecond mismatch, sub-microsecond normalization, disposal and the PID-only negative. The supplied mutant receipt fails precisely the replacement and one-microsecond tests (24/26). The supplied real pwsh-sleeper receipt reports mismatch with the sleeper alive, then stopped on the correct identity, then gone; it was inspected, not rerun by this reviewer.

### New Findings

| # | Severity | Blocking | Kind | Finding | File:Line | Recommendation | Status |
|---|---|---|---|---|---|---|---|

No new delivery or safety defect demonstrated. No remaining finding blocks approval.

### Q1 — Goal and proving rows

Accepted: ONE_LAUNCH_PATH/SITE_MIGRATION have AC-2/9 and rows 4-6; ENV_DROP_FLAG has AC-1/5/18 and rows 1-3/6; MAIN_ERROR_WATCH/CLOSE_CHECK have AC-3/4/6/7/8, including startup and shutdown coverage; INSTALL_ONCE has AC-12/13 and rows 7-8; HINT_VALUES has AC-14/15/16 and rows 9-11. Each clause has a producer, observable and negative case. AC-10 now has a safe stop boundary. No clause remains rejected. This approves the plan's ability to achieve the goal; runtime implementation remains future work.

### Q2 — Helper, teardown and failure rule

Accepted: installed Playwright prepends its own loader (`coreBundle.js:45698`) before the planned second `-r`, and initializes main before returning (`:45780`). The supplied startup probe supports the preload/log order. The log starts before main, retains complete stacks and malformed records, and is checked after original close plus a bounded five-second process-exit wait. Memoized close preserves the first result; missing logs fail closed. Removing the uncaught-exception dialog addresses the identified dialog hang without claiming all teardown hangs are solved; CAPTURE-E2E-LAUNCH-TEARDOWN-HANG stays MONITORING.

Accepted: the migration preserves each site's main/env values; the capture-picker subprocess keeps its spread. NEW_FAILURE_RULE fixes helper faults and registers/stops on other newly exposed main-process faults, including deliberate throws, without skips or expected failures. Scratch-profile and ancestry protections remain intact. No additional rejection on this surface.

### Q3 — INSTALL_ONCE

Accepted: `setup(project)` returns nothing, invokes `ensureElectronBinary()` without forwarding project, and provides the resulting path. Vitest awaits setup before `pool.runTests` (`cli-api.De07GUeT.js:12869-12871`); its setup-return contract matches the plan (`index.1TqnEahn.js:6567-6569`). `createRequire` reaches the real Electron package despite the Vite alias. That package synchronously installs on missing path/binary (`electron/index.js:25-52`). Present binary succeeds, absent binary installs serially, and offline failure throws before workers with the recovery command. AC-13 injects this run's provided value. CI's existing install after `npm ci --ignore-scripts` remains compatible. D-937/D-939 carry out the supplied hand-over; no additional mandatory-human category was demonstrated. No installation was attempted during review.

### Q4 — Tests, Red/Green and run discipline

Accepted: new-module tests assert existence before dynamic import; red-check requires the named assertion failures and rejects setup/launch/timeout failures (36/36 fixtures). The hint source slice includes the complete Region title, and the rendered test dirties the overlay to mount Save, then compares both controls against registry chords. The Ctrl+O mutant must pass the old test and fail both new tests, then restore bytes and mtime; mutation fixtures pass. No test expectation is changed during Green.

Vitest commands execute from pwsh with `npm --prefix ui`, which sets the package script cwd to ui. Electron wrappers clear the flag except deliberate flag negatives/positives. D-941 allows one repeat only for the two named MONITORING signatures and retains both attempts. No additional rejection. Product Red/Green and full suites were deliberately not run in this review.

### Q5 — Order, content baselines and registers

Accepted: row-0 BASE copies, baseline-sites.json, sibling anchors and untouched/scope manifests bind to execution-start content, accommodating uncommitted Sessions 75-77. The current 21-site/20-file migration model and synthetic Session 75 append pass the real checker; all six anchors are unique and eight scheduled new files are absent. Site fixtures reject altered main/env values and CRLF conversion; scope fixtures reject premature sibling changes and an unrestored mutant. No clean-tree or equality-to-HEAD requirement is imposed on sibling baselines.

Accepted: issue-resolve holds the writer-excluding register handle, checks the bound row-0 hash and restricts fields before replacing content; issue additions/rendering use issue_triage. Session 87 and sibling work remain outside this session's edits. Runtime cleanup now acts only on the verified owned object, with ambiguous processes left alone. No demonstrated out-of-scope write or remaining safety defect. Existing user execution authorization remains valid; Session 78 commits remain unauthorized and the planned closeout leaves a commit-message draft.

### Checklist Results

Manual observations were made by codex-independent-reviewer; null exits denote manual procedures, not commands.

| Check | Result | Procedure or command | Exit | Evidence |
|---|---|---|---|---|
| PR-1 to PR-3 | pass | Compare the full revised plan/task, row dependencies and scheduled paths. | null | Same goal/order; implementation unchecked; eight new deliverables absent. |
| PR-4 / PR-8; R2-F1 | pass | Trace Stop-OwnedElectron to Invoke-VerifiedStop and real opener; run owned-procs.ps1 -Selftest via rtk proxy pwsh. | 0 | 26/26; replacement/microsecond negatives refuse without kill; same object checked/killed/disposed. |
| PR-5 | pass | Compare grouping/issue scope, HDP sections 4a/5/5a/6, D-933 to D-941 and supplied expert/rejection receipts. | null | Handed-over defaults implemented consistently; no new policy objection. |
| PR-6; prior-fix regression check | pass | Compare R1-F2/R1-F4 against current history/profile contracts and R2-F1 against the new stop path. | null | All three fixed; original ids and historical tables preserved. |
| PR-7 / PR-9 | pass | Compare named contracts, exclusions and proving rows. | null | No required goal work omitted or materially ambiguous live contract found. |
| Current migration/content model | pass | rtk proxy python C:/Temp/av-kit/e2e-harness-hardening/review/static-probes.py | 0 | 21 sites/20 files; six anchors; eight absent paths; sibling-append positive and later-change negative pass. |
| Parser/source fixtures | pass | Run red-check.py, site-check.py, scope-check.py, mutation.py and identity.py with --selftest through rtk proxy python. | 0 | 36 red; 13 site; 6 scope; zero mutation/identity failures; separate preserved exits. |
| Untouched-file fixture logic | pass | Run r3-diagnose-untouched.py with process-local commit.gpgsign=false and the approved author/committer environment; repository config unchanged. | 0 | 6/6, including sibling changes before row 0. |
| Unmodified scratch Git selftest in this sandbox | n/a | Initial direct selftest and diagnostic wrapper. | 128 | Scratch commit could not access the configured signing key; diagnostic: No private key found for <HOME>/.ssh/id_ed25519_signing; fatal: failed to write commit object. Isolated fixture run above passes. No host-execution defect inferred. |
| Product suites / network / real stop | n/a | Not run under this review's read-only scope. | null | No pytest, Vitest, npm/uv operation, network or real process termination. |

### Current evidence and limits

Current content hashes: implementation-plan.md `6c9bbc8adf965599f8e3a47d26a5b67fb614b07dff1fc8b7a7fa85f9830a143a`; task.md `49b5f1f611bff38dbe2d812961c151841626a4857157762be243d05cb23be0cb`; owned-procs.ps1 `d4ff2318051b5557274f44e25ab2c3a2240bd0d25dd58514305882354bab7f00`. The static model receipt lists all thirteen plan-folder hashes; round-2 hashes above are historical.

```json
{"schema_version":"evidence.v1","cwd":"P:/av-kit","phase":"static","exit_code":0,"result":"pass","fresh":true,"check_id":"round3-verified-stop-and-ancestry","command":"rtk proxy pwsh -NoProfile -File docs/execution/plans/2026-11-15-e2e-harness-hardening/owned-procs.ps1 -Selftest","scope":"pure ancestry and injectable stop fixtures; no real process actions","tested_state":"owned-procs.ps1-sha256:d4ff2318051b5557274f44e25ab2c3a2240bd0d25dd58514305882354bab7f00","output":"owned-procs selftest: 26 of 26 passed; later replacement and one-microsecond mismatch refuse; original object kill(False) then dispose; exits handled without foreign termination"}
```

```json
{"schema_version":"evidence.v1","cwd":"P:/av-kit","phase":"static","exit_code":0,"result":"pass","fresh":true,"check_id":"round3-migration-and-content-baselines","command":"rtk proxy python C:/Temp/av-kit/e2e-harness-hardening/review/static-probes.py","scope":"in-memory migration and content checks only","tested_state":"plan-sha256:6c9bbc8adf965599f8e3a47d26a5b67fb614b07dff1fc8b7a7fa85f9830a143a;task-sha256:49b5f1f611bff38dbe2d812961c151841626a4857157762be243d05cb23be0cb","output":"21 sites / 20 files preserve args/env/spreads/endings; synthetic uncommitted sibling append accepted without HEAD comparison; 6/6 unique anchors; 8/8 new paths absent; unchanged sibling passes; later change refused; static probes: PASS"}
```

All Python probes used PYTHONDONTWRITEBYTECODE=1. The initial untouched fixture failed on a scratch commit because the sandbox lacks signing-key access (native Git exit 128); an attempted global-config isolation also failed at scratch init (128). No successful result is attributed to either attempt. The passing rerun used only process-local `GIT_CONFIG_COUNT=1`, `GIT_CONFIG_KEY_0=commit.gpgsign`, `GIT_CONFIG_VALUE_0=false` for the disposable fixture and the approved author/committer identity. It changed no Git configuration file and made no av-kit commit. The actual pure compare/content negatives also pass independently in static-probes.py.

### Verdict

**approved** — R2-F1 is fixed; R1-F2 and R1-F4 remain fixed. There is no evidence-backed High/Critical delivery or safety defect left. Executing the plan can achieve all three goal clauses. Runtime Green/full-gate evidence and independent execution review remain required by the plan; this verdict is not an implementation pass. The coordinator may save this complete rolling report to the canonical path after validation; this reviewer has written only under C:/Temp/av-kit and has not changed the ledger.
