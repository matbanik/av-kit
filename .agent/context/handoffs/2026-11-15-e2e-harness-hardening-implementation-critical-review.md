---
date: "2026-11-16"
review_mode: "execution"
target_plan: "docs/execution/plans/2026-11-15-e2e-harness-hardening/implementation-plan.md"
verdict: "approved"
findings_count: 0
template_version: "2.2"
requested_verbosity: "standard"
agent: "codex-independent-reviewer"
loop_id: "ehh-execution-2026-11-15-e2e-harness-hardening"
round: 1
---

# Critical Review: 2026-11-15-e2e-harness-hardening

> **Review Mode:** `execution`  
> **Verdict:** `approved` — intent achieved; no findings.

## Intent Anchor

every Electron E2E launch goes through one helper that drops `ELECTRON_RUN_AS_NODE` from the environment it passes and fails the test when the main process throws an uncaught exception; Vitest installs the Electron binary once, before any worker starts; and Capture's AC-97.4 hint tests fail when the Save or Region chord is wrong.

**Intent achieved: yes.**

## Scope

Independent Codex review of Anthropic/Claude Code's Session 78 implementation, with no MEU. HEAD and `baseline.sha` are `ebe68e4a3b934379622a8983debb47dec85e22dc` on `main`. Reviewed the execution workflow, plan, task, evidence handoff, all scoped UI test/config diffs, all eight new files whole, register/grouping/focus deltas, relevant main-process and installed-library source, plan-local launch/gate/ownership/oracle scripts and saved receipts. Applied IR/DR/AV checks to delivered behavior, assertion strength, migration fidelity and evidence.

Approved plan decisions remain fixed. Assessed D-942, D-943 and D-1031 independently; accepted Mat's disclosed D-1030 and D-1032–D-1034 rulings. Sessions 80–83 and their plan reviews are outside scope. This approval covers H1 implementation; the coordinator's collection of the review and H2 remain subsequent work.

Reviewer writes were confined to `C:/Temp/av-kit`. No repository edit, stage, commit, stash, revert, branch, worktree, build, suite run, installer invocation, Electron launch or network request occurred. The coordinator copies this report to its canonical destination.

## Findings

| # | Severity | Blocking | Kind | Finding | File:Line | Recommendation | Status |
|---|---|---|---|---|---|---|---|

## Q1 — One launch path

Accepted `ENV_DROP_FLAG`, `ONE_LAUNCH_PATH`, `SITE_MIGRATION` and `SCRATCH_PROFILE` (AC-1, AC-2, AC-9, AC-19). `electron-env.ts:26–35` copies base, sets the E2E flag, merges extra, deletes `ELECTRON_RUN_AS_NODE` after that merge, then removes undefined values. Independent direct-source probes confirmed caller override precedence, deletion from both inputs and nonmutation.

`ui/tests/e2e/electron-app.ts:69–78` checks the caller's scratch profile before allocating its log or launching, and contains the sole launcher. The independently rerun site checker reports **21 BASE sites in 20 files, site-check: ok**. All caller variables and their order remain, including `AVKIT_E2E_API_BASE`, backend delay, picker path/`stubEnv`, and startup `extraEnv`. The primitive harness retains `main`; all other sites keep the default main. No original site spreads `process.env` after its explicit overrides; removing that spread therefore loses no required precedence. The picker subprocess retains its separate spread, and `launchWithAppData` remains exported.

Missing, empty, temp-root and outside-temp profiles are refused. Existing callers use fresh scratch folders, except the intentional same-scratch relaunch. No migrated site selects the normal profile. This accepts the approved caller-controlled, lexical scratch-path boundary, without claiming symlink hardening.

## Q2 — Main-process error watch

Accepted `MAIN_ERROR_WATCH`, `CLOSE_CHECK` and `NEW_FAILURE_RULE` (AC-3–AC-8). The launcher passes `-r` before main; the installed Playwright launch implementation prepends its own loader without removing that preload. `main-error-watch.cjs:7–25` creates the channel before app code, hides its environment key, and appends complete records synchronously. The independent VM probe executed the actual preload with in-memory collaborators: empty initial channel, hidden key, two retained records including a non-Error throw, complete stack and two stderr markers. There is no late stderr-listener dependency or buffered append to lose on exit.

At `electron-app.ts:84–94`, the child is captured before Playwright disposal; close is memoized and awaits original close, bounded process exit, then log inspection. Missing logs fail; malformed lines are retained as failures rather than discarded. The startup-throw fixture throws on the first tick before launch resolves. The recorded five-test Green and final full gate prove post-launch/startup errors reject close and the no-error control closes cleanly. Cleanup catches in the two intentional-error tests follow explicit error assertions; the existing held-app cleanup also has a propagating close on its successful path. No passing migrated test was found to bypass the close check.

Cleanup is performed on launch rejection and whenever completed close reaches log inspection, including a detected error. It is **not an unconditional cleanup guarantee** if original close rejects/hangs or a test terminates before close; those paths already fail the test. This is a limitation of the approved close sequence, not a demonstrated false pass. The five-second exit wait alone deliberately does not fail. Unhandled rejections remain the approved separate issue. The disclosed row-3 defect was in the new helper, and capturing the child before close correctly fixes it under `NEW_FAILURE_RULE`; no product-error allow-list was introduced.

## Q3 — Install once

Accepted `INSTALL_ONCE` (AC-12, AC-13). `ui/vitest.config.ts:16` wires the global setup. `global-setup.ts:25–44` uses real Node `createRequire`, bypassing Vite's alias, calls the package synchronously, validates the binary, provides its path and returns void. Installed `electron/index.js:25–48` invokes the synchronous installer only when needed; `install.js:16–18` also exits immediately when installed. Vitest's installed global-setup implementation awaits setup before worker execution.

Tests cover a found binary, require failure, missing binary, the config hook, void return, exactly one provide call and receipt by the worker. Independent injected calls passed success/failure cases and counted one require; none invoked the installer or network. The recorded real worker `inject` pass corroborates ordering. The installed tree was not moved or deleted to reproduce extraction contention, as approved in the plan.

## Q4 — Capture hints

Accepted `HINT_VALUES` (AC-14–AC-16). `capture-page.test.ts:630–646` compares actual Save/Region source values with registry chords and extends the Region slice through its title. `capture-page.behavior.test.ts:3449–3458` mounts Save by drawing, then checks both rendered controls with `expectBoundHint`; `helpers/bound-hint.ts:15–19` asserts exact ARIA and visible chord text from the registry. Both controls have independent assertions, so a Region-only wrong value cannot pass merely because Save is correct.

Observed receipts: old test on the Ctrl+O mutant **1 passed**; new source/rendered tests **2 assertion failures**, including `Control+O` versus `Control+S`; restored real source **2 passed**. The reviewer replayed the Red oracle against the original receipt and child exit 1: zero problems.

Current `CapturePage.tsx` SHA-256 is `85a51cb73ed853163813f2695970622b3cfb47688a196bd092d719bc9a354446`, identical to row 0. It has no Git diff. Strictly, its CRLF working bytes are not identical to the raw LF Git blob; after CRLF normalization they are byte-identical. No mutant or substantive product edit remains.

## Q5 — Harness scripts and evidence

Accepted process ownership, D-943 and D-1030 scope (AC-10, AC-18). `owned-procs.ps1:51–90` requires recorded parent identity/history to admit descendants. Its stop boundary at `:154–174` opens and holds the process handle, compares creation time at CIM resolution, and kills only that verified object with `Kill($false)`. Unproven same-path processes are listed without stopping. Independently rerun pure selftest: **26/26**, including PID replacement, historical reuse, unreadable/exited candidates and unrelated same-path apps; it starts no real process.

`e2e-run.ps1:16–23` correctly disables positional binding so remaining bare spec paths reach `Files`, not `MinPassed`; the saved D-943 probe demonstrates all task forms and the old conversion failure. D-942 changes only an obsolete comment token. D-1031's negative lookbehind distinguishes quoted `_electron.launch` source from an actual `electron.launch:` failure; the independent **38-fixture** oracle selftest retains timeout/launch/setup rejection, and all original Red groups pass the checker with nonzero child exits. These decisions are sound.

DEBUG is set only in flag child commands, with parent resets before/after; nonflag argv does not set it. The saved guard probe refuses synthetic `bad option` on both script paths. The original flag negative has **4 bad-option lines and 4 failed tests**. The passing flag receipt has **187 `pw:browser` lines, 9 passed, zero `bad option` lines**.

`ehh-gate-h1.txt` records every required step in order, exit 0, and ends `session-gate: all steps exit 0`: type/lint/static checks, 35 register tests, **132 unit files / 1540 tests**, three required builds, render checks, **208 Electron tests**, flag run and matching before/after identity. Both runtime steps report zero leftover owned Electron processes. The earlier attempt preserves **207 passed / 1 failed**, AC-97.7 expected count 1/received 0, followed by `not_run` for flag/identity. The BASE-spec probe separately records **3 failed / 17 passed** for that same flake. No changed assertion, skip or swallowed watch failure conceals it; D-1032's repeat ran the whole gate after registration.

## Q6 — Register and documents

Accepted AC-17. Parsed comparison against HEAD independently confirms exactly the four intended existing records changed to resolved, exactly the three disclosed open issues were added, and `CAPTURE-E2E-LAUNCH-TEARDOWN-HANG` is unchanged. The resolution receipt starts with row-0 register hash `3144717371df89f2b8463f98810dd4bcabeab5b46786ce0606e1cc334cf1481f` and ends `issue-resolve: 0 problem(s)`; the three add receipts name the intended tools/results. This supports historical tool use; the reviewer did not rerun writes.

Independent `issue_triage.py render --check` exits 0: **known-issues.md is up-to-date**. The grouping diff changes only section 6 row 78. Its reconstruction and final byte comparison substantiate the disclosed edit-order deviation. The new current-focus entry accurately names the delivered contracts, repeat, open issues and review/H2 next step. D-1032 accounts for the third addition; the unit total increases by one after row 8 because the rendered hint test is added in row 10. No behavioral/document fidelity defect was found.

## Q7 — Safety and fidelity

Accepted within reviewed scope. All **28 saved row-0 byte copies** match `baseline-scope.json`. The 20 migrated files retain their original line endings; the three modified unit files, config and focus remain CRLF; register/grouping remain LF; all eight new UI files are LF. Independent scope check: **36 paths, 0 moved, scope-check: ok**. Independent untouched check confirms no content changes under product/Python/MCP/tools roots, including the restored Capture source. No newly introduced home-folder path or personal email was found in reviewed additions/new files; pre-existing register text was not mistaken for a new addition.

**tested_state:** `ebe68e4a3b934379622a8983debb47dec85e22dc+454558a34705e83897c7ef7a5cb1a4a15d6fa329e1c9e57ab25be8175fac510e`.

This is the plan's actual `identity.py --state-only` result from the existing project interpreter with `ELECTRON_RUN_AS_NODE` unset. It **does not differ from the gate**. A process-local `core.excludesFile` referencing a scratch file reproduced only the disclosed `.claude/settings.local.json` exclusion while preserving inherited Git settings. The unadjusted sandbox would enumerate that extra path because the host ignore is unreadable; the secret was never opened or hashed, and no secret-inclusive state was calculated. No repository/global Git configuration changed.

The execution record, unchanged HEAD and scoped state support the claim that this implementation remains uncommitted; they are not a forensic proof of every historical filesystem operation. The reviewer performed no repository mutation. The temporary row-0 write and Capture mutations are disclosed and restored, with matching current hashes. No new build, Vitest, Playwright, Electron, baseline or writing issue command was run for review.

## Checklist Results

Commands below ran from `P:/av-kit`, through `rtk proxy`, with bytecode disabled and TMP/TEMP under `C:/Temp/av-kit/e2e-harness-hardening/exec-review/tmp`. `probe-env.ps1` applies the process-local Git exclusion described above. Full suite results are inspected author evidence, not reviewer reruns.

| Check | Result | Command/procedure | Exit | Decisive evidence |
|---|---|---|---|---|
| IR-1 / AC-5–AC-8, AC-10, AC-18 | pass | Manual inspection of original gate and per-step runtime receipts; observer `codex-independent-reviewer` | null | 208 full-suite and 9 flag tests passed; all five new harness tests ran; zero bad-option lines |
| IR-4 / AC-9 migration | pass | `rtk proxy .venv/Scripts/python.exe docs/execution/plans/2026-11-15-e2e-harness-hardening/site-check.py` | 0 | 21 sites in 20 files, all main/env/order/line-ending rules pass |
| IR-5 / direct helper probes | pass | `rtk proxy node C:/Temp/av-kit/e2e-harness-hardening/exec-review/helpers.mjs` | 0 | Env/scratch/parser/install injected cases and actual preload VM checks pass; no Electron or installer |
| AV-1 / Red validity | pass | `rtk proxy .venv/Scripts/python.exe C:/Temp/av-kit/e2e-harness-hardening/exec-review/audit.py` | 0 | All five Red groups accepted with child exit 1; actual assertion diagnostics inspected |
| Red oracle regression fixtures | pass | `rtk proxy .venv/Scripts/python.exe docs/execution/plans/2026-11-15-e2e-harness-hardening/red-check.py --selftest` | 0 | 38 fixtures, 0 wrong |
| Site oracle regression fixtures | pass | `rtk proxy .venv/Scripts/python.exe docs/execution/plans/2026-11-15-e2e-harness-hardening/site-check.py --selftest` | 0 | 13 fixtures, 0 wrong |
| Scope oracle regression fixtures | pass | `rtk proxy .venv/Scripts/python.exe docs/execution/plans/2026-11-15-e2e-harness-hardening/scope-check.py --selftest` | 0 | 6/6 |
| Process ownership regression fixtures | pass | `rtk proxy pwsh -NoProfile -File docs/execution/plans/2026-11-15-e2e-harness-hardening/owned-procs.ps1 -Selftest` | 0 | 26/26; no real process started |
| Current scope / product preservation | pass | Individual `scope-check.py --before-row 13`, `untouched-check.py`, `mutation.py status` children in `run-static.ps1` | 0 each | Scope clean; untouched clean; Capture hash equals row 0 |
| Register render | pass | `rtk proxy .venv/Scripts/python.exe tools/issue_triage.py render --check` | 0 | OK: known-issues.md is up-to-date |
| DR / safety / line endings | pass | `rtk proxy .venv/Scripts/python.exe C:/Temp/av-kit/e2e-harness-hardening/exec-review/audit.py` | 0 | 28 baseline copies verified; 4 changed and 3 added records; one grouping row; no new home path/email |
| Freshness | pass | `rtk proxy .venv/Scripts/python.exe docs/execution/plans/2026-11-15-e2e-harness-hardening/identity.py --state-only` | 0 | Exact match to gate before/after identity |
| Extra untouched checker selftest | n/a | `rtk proxy .venv/Scripts/python.exe docs/execution/plans/2026-11-15-e2e-harness-hardening/untouched-check.py --selftest` | 1 | Its isolated scratch Git commit subprocess exited 128; checker captures no underlying diagnostic. Existing gate records 6/6; independent live untouched check passes. No repository commit occurred. |
| IR-2, IR-3, IR-6 product stubs/API/write boundaries | n/a | Scope inspection | null | No product/API/MCP change |

The static runner's overall exit was **1** solely for that extra scratch selftest; it is not represented as a passing wrapper. No repeated product suite was needed because current inputs match the passing full gate.

### Assertion strength (IR-5)

| Tests reviewed | Rating | Basis |
|---|---|---|
| Helper unit AC-1, AC-3, AC-4, AC-19 | Strong | Exact env/nonmutation, real subprocess alive/dead comparison, complete stack records and refused profiles |
| Helper unit AC-2; named layout AC-51.7 change | Adequate | Approved source-wiring checks; complemented by site oracle and real Electron gate |
| Five Electron harness tests: AC-5, AC-6, both AC-7 cases, AC-8 | Strong | Actual app/profile observations; startup and later exception rejection; clean-close control |
| Install AC-12 and AC-13 | Strong | Injected success/errors, return/provide contract and actual worker receipt |
| Capture source and rendered AC-97.4 | Strong | Registry values, exact ARIA, mounted Save and visible hints; mutation failure evidence |
| Twenty migrated E2E files | Preserved | Assertion bodies unchanged; only launch plumbing/imports and D-942 comment differ; full suite ran under watch |

AV-2–AV-6 and IR-7 pass by source/diff/receipt inspection: no assertion neutralization, new skip/only/fixme, placeholder, unapproved expectation change or silently omitted session AC. All AC-1–AC-19 appear in the handoff. Approved exclusions remain disclosed issues, not missing goal work.

### Durable reviewer evidence

```json
{"schema_version":"evidence.v1","check_id":"ehh-review-source-probes","command":"rtk proxy node C:/Temp/av-kit/e2e-harness-hardening/exec-review/helpers.mjs","cwd":"P:/av-kit","scope":"ENV_DROP_FLAG, SCRATCH_PROFILE, log parser, INSTALL_ONCE injected cases and actual preload in isolated VM","phase":"targeted","exit_code":0,"result":"pass","tested_state":"ebe68e4a3b934379622a8983debb47dec85e22dc+454558a34705e83897c7ef7a5cb1a4a15d6fa329e1c9e57ab25be8175fac510e","output":"helper probes: env merge/drop/nonmutation, scratch refusals, malformed-log retention, install injection success/errors: pass; no installer invoked. preload VM probe: empty channel, hidden log env, two synchronous records, full stack, non-Error retention: pass; no Electron process started","fresh":true}
```

```json
{"schema_version":"evidence.v1","check_id":"ehh-review-receipt-and-byte-audit","command":"rtk proxy .venv/Scripts/python.exe C:/Temp/av-kit/e2e-harness-hardening/exec-review/audit.py","cwd":"P:/av-kit","scope":"Original Red receipts, full-gate summaries, restored Capture bytes, register/grouping changes, baseline hashes, line endings and scoped new-text privacy","phase":"targeted","exit_code":0,"result":"pass","tested_state":"ebe68e4a3b934379622a8983debb47dec85e22dc+454558a34705e83897c7ef7a5cb1a4a15d6fa329e1c9e57ab25be8175fac510e","output":"Five Red groups: zero oracle problems, child exits 1. Full Electron 208 passed; flag 9 passed, 187 pw:browser lines, 0 bad-option lines. Exactly 4 resolved records changed and 3 open records added; teardown-hang unchanged. 28 row-0 byte copies match manifest; eight new UI files LF. Only grouping section 6 row 78 changed. Capture row-0 hash restored and CRLF-normalized HEAD equality true. No newly introduced home-path or personal-email matches.","fresh":true}
```

## Verdict

`approved` — the delivered implementation achieves the registered goal, with no evidence-backed High/Critical defect and no findings. Keep the disclosed rejection/dev/flake issues and failure-path cleanup limits visible. This review authorizes no push and makes no claim that H2 or commit has occurred.
