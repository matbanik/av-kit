---
date: "2026-11-18"
review_mode: "execution"
target_plan: "docs/execution/plans/2026-11-17-e2e-pointer-flakes/implementation-plan.md"
verdict: "approved"
findings_count: 0
template_version: "2.2"
requested_verbosity: "standard"
agent: "codex-independent-reviewer"
loop_id: "epf-execution-2026-11-17-e2e-pointer-flakes"
round: 1
---

# Critical Review: 2026-11-17-e2e-pointer-flakes

> **Review Mode:** execution. **Verdict:** approved. **Intent achieved:** yes.

## Scope

Reviewed Session 91's working-tree delta from `9fce270bff07964d76da4dee163f83fddf31fe2e`, against AC-1 through AC-15 and the referenced test families. Claude Code/Anthropic authored the work; Codex is the independent reviewer. The review covered the four modified test/harness files, four new files, three issue entries and their render, grouping row 91, current focus, plan scripts/baselines, task and handoff, with the existing configuration, harness/rejection tests and relevant main-process paths as context.

**Intent anchor:** The three Electron load flakes and the specs folded into them pass on a busy host. That means full Electron runs on a host held at a median load of at least 60 %, with zero failures in the watched specs, zero test-timeout hangs except those excused by a signature this session registered, zero unhandled rejections and zero diagnostics errors. If row 3's isolated watched runs showed zero failures, the proof is five full runs; otherwise it is three full runs plus ten repeats of the eleven watched tests under the same load, all passing.

**Current tested_state:** `9fce270bff07964d76da4dee163f83fddf31fe2e+449e4c74b025d9adf857be52f6f3e08d1d2e45c58919e4631721d82d4cc0c692`. The independent `identity.py --state-only` result exactly matches the gate and H1-6b value. There is no sandbox/global-ignore difference to reconcile. The secret local settings file was not opened.

Only scratch artifacts were written. No Electron, backend, busy children, build, installation or network request was started by this review. Fresh reviewer checks used `PYTHONDONTWRITEBYTECODE=1`, scratch TMP/TEMP, offline/no-sync uv and unset `ELECTRON_RUN_AS_NODE`.

## Findings

| # | Severity | Blocking | Kind | Finding | File:Line | Recommendation | Status |
|---|---|---|---|---|---|---|---|

## Checklist Results

| Check | Result | Observation |
|---|---|---|
| IR-1: live runtime evidence | pass | Independently recounted the bound acceptance and gate run files and parsed their phase/main logs; results below. Recorded Electron evidence was used within the requested read-only limits. |
| IR-2 / IR-3 / IR-6: product stubs, error mappings, external write schemas | n/a | No product/API/MCP change or new external write boundary. |
| IR-4: fix generalization | pass | Shared queue driver covers download and convert; capture uses the same window settling and addresses both origin tests and the named hover/drawing sites. |
| IR-5: test rigor | pass | AC-1/2/3: strong behavioral assertions, including never-settles, shield opt-out, later windows, unchanged visibility and timer shutdown. AC-6/7: adequate static checks as explicitly specified, backed by real full-suite assertions. AC-4/8/9/10: strong real-Electron assertions for phases/events, obstruction, native style bits/CDP input and opt-out. Changed existing test bodies retain their meaningful order, geometry, request and hint assertions; no weak changed test identified. |
| IR-7: coverage/deferrals | pass | All fifteen ACs have evidence. `not-reproduced` leaves the hang issue open exactly as AC-12/15 prescribe; it is not claimed fixed. |
| AV-1: failing then passing | pass | Real Red receipts validate as assertion failures; new test hashes still equal row 1; fresh unit run passes all five; AC-9 passes from row 6 and in all acceptance runs. |
| AV-2 through AV-5: bypasses, assertion coverage, skips, placeholders | pass | Source/diff inspection and fresh assert-check preserve 1,167 assertion lines and 103 test titles; no new retry, raised timeout, skip, early assertion exit or incomplete implementation. The diagnostic repeat-index spelling is assessed in Q7. |
| AV-6: sourced criteria | pass | Applied the approved FIC and decisions, including D-1150's declared residual limits. |
| State, scope and safety | pass | Independent state matches; 408 product/tool file hashes and their exact file set match baseline; grouping changes only line 163; fresh EOL and render checks pass. |

## Q1. Goal and acceptance proof

**Accepted: every goal clause is supported (AC-5, AC-11, AC-13, AC-14).** The independent `recount.py` reads the invocation/file bindings from the receipts and counts the raw Playwright success lines, checks contiguous test numbers and final passed totals, matches each watched title, parses every bound phase line, verifies each launch ends at `exit`, and checks an `install` event exists for every built-app diagnostics evaluation.

| Proof | Invocation | Passed | Watched passes | Failures / timeout hangs / rejection lines / evaluate errors |
|---|---|---|---|---|
| Full acceptance 1 | `20261118T154356-54848-b402d6` | 232/232 | 11/11 | 0 / 0 / 0 / 0 |
| Full acceptance 2 | same invocation, distinct run 2 files | 232/232 | 11/11 | 0 / 0 / 0 / 0 |
| Full acceptance 3 | same invocation, distinct run 3 files | 232/232 | 11/11 | 0 / 0 / 0 / 0 |
| Watched ×10 | `20261118T161319-47396-63fc86` | 110/110 | each of eleven titles exactly ten times | 0 / 0 / 0 / 0 |

The full acceptance sampler records 580 samples, minimum 81.6%, median 95.4%, maximum 100%; watch10 records 90 samples, minimum 89.0%, median 93.9%, maximum 99.0%. Both started 18 busy children, ended with both remaining counts zero, and excused zero hangs. The sampler's persisted aggregates and implementation establish load; individual CPU samples are not separately persisted for a second median calculation. Even the recorded minima exceed the floor.

Each full run has 234 launches, all reaching exit; 232 receive the built-app diagnostics evaluation. Watch10 has 120 launches/evaluations, all reaching exit (the hotkey test launches twice). All phase lines carry the expected run id, and all referenced main logs parse. AC-81.11 passes once per full run and ten times in watch10. Row 3's rerun has four isolated watched failures, so three full runs plus 110 watched executions is the correct proof shape. The row-0 list is 228 tests; four new Electron tests make 232.

I did not count F2-held measurements, solo reruns, or the plain gate as busy-host acceptance, and did not excuse any acceptance failure.

## Q2. Drag fix and shared helpers

**Accepted (AC-1, AC-6, AC-8, AC-11; AC-49).** `pointer-settle.ts:16`, `:36` and `:45` implement SETTLE, SETTLED_BOX and POINTER_ON as specified, with a frame bound, unchanged timeout policy and a hit-test before returning. A permanently changing read rejects; an obscured target cannot pass AC-8 until its overlay is removed.

The download diff removes only the five helper definitions and imports their needed public callers. Inspection against HEAD shows the same transform correction, transition predicate, visibility/frame/resize quiet logic, activation nudge, pressed-state wait, re-aim and live-region commitment wait. The changes to those moved bodies are selector parameterization and equivalent local handle/live-region construction (POINTER_HELPERS_SHARED). The defaults preserve download behavior.

`convert-queue.test.ts:1198` uses grabRow/dragOver with `convert-queue-row`, then releases. DRAG_DRIVER_SHARED addresses the missing activation/commit synchronization rather than weakening the final-order assertion: a missed press or uncommitted target still fails. Fresh assert-check reports 266/282/619 baseline assertion lines unchanged and 26/23/54 test titles retained, respectively. CONFIG_KEPT, EXIT_WAIT_KEPT and REJECTION_WATCH_KEPT hold. No new wait knob was introduced; `setTimeout(` decreases from eight to six because the duplicate window helper was removed.

I did not treat a wait as permission to remove a failure: all final expectations remain and a condition that never arrives fails the test.

## Q3. Capture origin and committed grab

**Accepted (AC-7, AC-11; AC-66, AC-67, AC-80, AC-81, AC-87, AC-143).** `capture-inbox.test.ts:924` uses settle over readZoom; readZoom itself waits two frames. Both AC-66.14 and AC-81.14 now use SETTLED_ZOOM for their origin/geometry reads, including later reads in those tests. The 40-pixel pan expectations are unchanged.

At `capture-inbox.test.ts:2032`, GRAB_COMMITTED waits for the actual arrow x2 to change between mouse release and `ends()`. The unchanged numeric x2 displacement and fixed x1/y assertions still distinguish a correct grab from any wrong movement. POINTER_SITES appears at the Apply and Arrow/Undo hover sites and `dragImage` uses settledBox at `:2523`; the duplicate windowSettled is removed and imported. The fresh AC-7 static test passes, and the real watched/full runs prove the affected paths. I did not infer an independently reproduced zoom failure: the rerun's observed failures were drag and Apply-hover failures, while the zoom fix is supported by the code condition, mechanism tests and required acceptance.

## Q4. Shield, phases and diagnostics

**Accepted (AC-2/3/4, AC-8/9/10/11).** `electron-app.ts:33` enables POINTER_SHIELD by default and `:142` evaluates installMainDiag only for an unspecified main entry (DIAG_DEFAULT_MAIN_ONLY). `e2e-diag.ts:90` is self-contained and hooks existing and later-created windows; `:150` applies the native shield. AC-9 checks both Windows style bits and working CDP click/hover, and AC-10 proves SHIELD_OPT_OUT. Both pass in the recorded acceptance/gate; unit AC-3 also checks later windows and the opt-out.

DIAG_DIR and PHASE_LINES are run-scoped through `AVKIT_E2E_DIAG_DIR` and `AVKIT_E2E_RUN_ID`, with exclusive fresh receipt/folder creation in flake-run.py. `electron-app.ts:150` retains EVALUATE_ERROR_KEPT_GOING: a failed evaluate is recorded and the app is returned. No such error exists in acceptance or gate logs. MAIN_DIAG leaves background throttling alone. STARTUP_MAIN bypasses the evaluation and its rejection/exception checks remain unchanged. The unchanged exit wait and checkMainErrors still run on wrapped close.

PRODUCT_UNCHANGED is independently established by the exact 408-file baseline comparison. Normal product launches do not import this test module, and an unset diagnostic directory writes no phase/main log. I did not claim keyboard isolation or a change to the normal app; neither is provided or required.

## Q5. Row 3, F2 and burn level

**Accepted (AC-5, AC-13/14; D-1152, D-1153).** Probes 1–6 record F2 held (1409); 7–8 record it free. The raw repro/drag/origin/shield10 measurement files each contain 100 passes and ten failures, all AC-81.11's pre-launch fixture failure, with no timeout hang or rejection. Row 5's plain-run exception is disclosed, not reported as an AC-81.11 pass. Those measurements do not certify acceptance.

The rerun uses new `repro-b`/`base-full-b` invocation files, the three row-0 unfixed spec copies and shield=false. The copies' hashes match baseline-scope.json and HEAD bytes. Swap-out receipts confirm the unfixed files/default; swap-back receipts confirm all four restores. Independently comparing `row3b-fixed-save` with the current files gives 4/4 byte-identical, and the restore assert/EOL receipts pass.

The fresh reproduction is 106/110, with AC-49.25, AC-49.26 and AC-67.20 twice failing; median 98.0%. Its full run is 230/232 at median 98.3%, with the disclosed unshielded AC-9 and convert-label failure, whose solo rerun passes. No hang occurs, churn remains alive until stop, and busy counts finish at zero. `epf-burn-level-b.txt` therefore correctly selects 18 children and accept-runs=3 without escalation. The executor's `row-8.ps1:11` reads that rerun file for both children and run count. I did not use the original F2-skewed failure rate to justify row 8.

## Q6. Launch hang

**Accepted (AC-12, AC-15).** Independently scanning the raw files bound to repro, base-full, drag, origin, shield10 and both row-3 rerun receipts finds no `Test timeout of`, `Worker teardown timeout` or rejection line. Acceptance and the plain gate are also clean. `epf-hang-verdict.txt` therefore supports `outcome: not-reproduced`; `epf-hang-signatures.json` is empty. No hang is excused.

The register leaves CAPTURE-E2E-LAUNCH-TEARDOWN-HANG open and appends the receipts, outcome and next diagnostic step. No MEU or split issue is required for this outcome. I accept the absence of reproduction in these runs, not a claim that an intermittent launch hang is fixed.

## Q7. The repeatEach key

**Accepted (AC-11).** `electron-app.ts:45-49` explains and constructs the existing TestInfo repeat-index property. Its only use is the numeric `repeat` metadata at `:64`; it does not set Playwright options, modify scheduling or add a test repeat. The existing checker was not changed. Reading the current repetition's identity serves PHASE_LINES, while NO_NEW_WAIT_KNOBS and CONFIG_KEPT prohibit new wait/retry/repeat configuration. The actual configuration is byte-identical and the only watched repeat is the approved flake-run CLI argument. The joined spelling avoids an overbroad textual match without hiding the prohibited behavior. I found no control defeat.

## Q8. Registers

**Accepted (AC-15).** `epf-issue-resolve.txt` records zero problems and exactly eleven changed parsed fields: status, resolution_path and the three verification fields on each pointer issue, plus the launch issue's notes. Its before/after SHA-256 values match the actual row-0/current register. The source delta confirms no other issue changed. The two resolved issues have last_checked, method, measured result and resolution_path; the hang remains open.

Fresh `issue_triage.py render --check` says known-issues.md is up-to-date. The recorded state render passes with 160 MEUs/12 phases; no MEU state changed. Independent baseline/current comparison finds only grouping line 163 changed, exactly row 91. The current-focus addition reports the same results. I did not require a MEU for a not-reproduced hang.

## Q9. Full gate and skip basis

**Accepted (AC-11, AC-13, AC-15 and PRODUCT_UNCHANGED).** `epf-gate-h1.txt` has 23 executed step records, each exit 0 with its individual receipt present, and ends `session-gate: all steps exit 0`. There are no fail-fast omissions. The identity before and after equals the independent current identity.

| Gate component | Observed evidence |
|---|---|
| Types/lint | `tsc --noEmit`; `eslint src/ tests/ --max-warnings 0`; both exit 0 |
| Task/scope/EOL/home-path | 27 task rows; outside scope []; 12 read-only hashes match; 34 EOL paths/0 problems; home-path check passes |
| Selftests | flake-run, assert-check, red-check, eol-check, identity all exit 0; Red grammar has 88 fixtures/0 wrong; EOL has 19 cases/0 wrong |
| Python script quality | Six files formatted; lint passes |
| Targeted | assert-check passes; three Vitest files/13 tests pass |
| Fresh full Vitest | 145 files, 1,633 tests pass; no baseline failures excused |
| Build | Full UI build exits 0 |
| Fresh full Electron | Raw gate file independently recounts 232/232, including all watched tests; no hang/rejection/evaluate error; 234 launches reach exit |
| Renders | Issue render and MEU/state render pass |

The gate's plain Electron median is 20.6%, after a 13.4% host-load precheck; it is the prescribed no-burn gate, separate from busy acceptance. Skip basis for py-tests, py-types, OpenAPI and mcp-* is sound: the exact baseline file set and all 408 hashes under packages, mcp-server, tools and ui/src remain equal, with no additions/removals. Plan-local Python is separately formatted/linted/selftested. I did not rerun the full gate merely to restate established matching evidence.

## Q10. Safety, fidelity and limits

**Accepted within this delta.** Fresh eol-check reports 34 scope paths and zero problems: LF files retain LF and current-focus retains CRLF. Independently enumerated nonsecret changes are confined to the declared test/harness/register/grouping/focus paths, plan folder and allowed closeout artifacts. HEAD remains the row-0 baseline on main and the index is empty. There is no repository commit, stash or git revert in the reviewed execution evidence; D-1153's disclosed temporary byte swaps were fully restored. This review made none of those operations and stopped no process.

The clipboard files are excluded by EXCLUDED and absent from the baseline list and every recounted full/watched run. All launches still pass requireScratchAppData before the single launch call, electronEnv sets AVKIT_E2E, the new tests create scratch profiles, and the unchanged main process honors the scratch data override. No new code introduces external networking or real app-data access; the fresh reviewer unit/probe runs use no network.

Added lines and new files contain no home-folder path or personal email. A pre-existing home-path reference remains at current-focus.md:31 outside this delta; it was not introduced here. No secret-named file or real app data was opened. Handoff counts, issue resolution evidence, restore evidence and current tested state agree with the receipts. The disclosed queue reorder, Session 94's higher test total and anchor moves do not weaken the proof.

Residual limits are the approved finite-run statistical proof and the unreproduced launch hang, whose issue remains open. Runtime evidence here is the existing automated Electron proof; this reviewer did not relaunch it on the shared host.

## Reviewer Commands and Durable Evidence

All commands below ran through `rtk proxy` with captured exits and all-stream receipts under `C:/Temp/av-kit`. `exec-review/run.ps1` supplies the environment described above. The unit API launcher retains the repository config/test selection, uses the runner config loader with the config's ui directory supplied as __dirname, disables test caching and sends Vite's cache directory to scratch; this prevents bundle/cache writes in the repository. Its initial loader-only setup failure was corrected in scratch before the reported passing run. The initial uv default-cache access failure was resolved by a scratch UV_CACHE_DIR. Neither was an implementation failure or Electron attempt.

```json
{"schema_version":"evidence.v1","check_id":"review-state","command":"rtk proxy pwsh -NoProfile -File C:/Temp/av-kit/e2e-pointer-flakes/exec-review/run.ps1 uv run --no-sync python docs/execution/plans/2026-11-17-e2e-pointer-flakes/identity.py --state-only","cwd":"P:/av-kit","scope":"current D6 inputs","phase":"static","exit_code":0,"result":"pass","tested_state":"9fce270bff07964d76da4dee163f83fddf31fe2e+449e4c74b025d9adf857be52f6f3e08d1d2e45c58919e4631721d82d4cc0c692","output":"Identity equals gate and H1-6b exactly."}
```

```json
{"schema_version":"evidence.v1","check_id":"review-recount","command":"rtk proxy pwsh -NoProfile -File C:/Temp/av-kit/e2e-pointer-flakes/exec-review/run.ps1 uv run --no-sync python C:/Temp/av-kit/e2e-pointer-flakes/exec-review/recount.py","cwd":"P:/av-kit","scope":"bound acceptance/watch10/gate raw run files and diagnostics","phase":"targeted","exit_code":0,"result":"pass","tested_state":"9fce270bff07964d76da4dee163f83fddf31fe2e+449e4c74b025d9adf857be52f6f3e08d1d2e45c58919e4631721d82d4cc0c692","output":"accept 1/2/3 each 232 passed and 11 watched; watch10 110 passed, each watched title ten times; gate 232 passed. All failures/hangs/rejections/evaluate-errors zero. Full acceptance min/median 81.6/95.4; watched min/median 89.0/93.9. RECOUNT PASS."}
```

```json
{"schema_version":"evidence.v1","check_id":"review-scope-audit","command":"rtk proxy pwsh -NoProfile -File C:/Temp/av-kit/e2e-pointer-flakes/exec-review/run.ps1 uv run --no-sync python C:/Temp/av-kit/e2e-pointer-flakes/exec-review/audit.py","cwd":"P:/av-kit","scope":"baseline/current scope, restores, measurements, registers and gate receipts","phase":"targeted","exit_code":0,"result":"pass","tested_state":"9fce270bff07964d76da4dee163f83fddf31fe2e+449e4c74b025d9adf857be52f6f3e08d1d2e45c58919e4631721d82d4cc0c692","output":"408 product/tool files match exact baseline set/hashes; grouping changed lines [163]; 4/4 restored files byte-identical; 2/2 new tests retain Red hashes; measurements contain zero timeout hangs/rejections; F2 probes 1-6 held, 7-8 free; delta outside scope []; gate 23 steps exit0; full Vitest 145/1633; no introduced home path/personal email. AUDIT PASS."}
```

```json
{"schema_version":"evidence.v1","check_id":"review-unit","command":"rtk proxy pwsh -NoProfile -File C:/Temp/av-kit/e2e-pointer-flakes/exec-review/run.ps1 node C:/Temp/av-kit/e2e-pointer-flakes/exec-review/unit.mjs","cwd":"P:/av-kit/ui","scope":"tests/unit/e2e-pointer.test.ts with unchanged repository config and scratch-only loader/cache handling","phase":"targeted","exit_code":0,"result":"pass","tested_state":"9fce270bff07964d76da4dee163f83fddf31fe2e+449e4c74b025d9adf857be52f6f3e08d1d2e45c58919e4631721d82d4cc0c692","output":"Vitest 5.0.5: Test Files 1 passed (1); Tests 5 passed (5)."}
```

Additional fresh commands (same environment wrapper; all exit 0): `node node_modules/typescript/bin/tsc --noEmit --project tsconfig.json` from ui; plan `assert-check.py` (1,167 assertions/103 titles retained, PASS); `eol-check.py` (34 paths/0 problems); `flake-run.py --selftest` (0 failures, no app or busy process); `red-check.py --selftest` (88 fixtures/0 wrong); `uv run --no-sync python tools/issue_triage.py render --check` (up-to-date). Source/diff comparisons were observed by codex-independent-reviewer with null manual exit; the Q sections describe the inspected behavior rather than claiming additional runtime executions.

`exec-review/final-check.py` also exits 0: the actual Red unit receipt satisfies all five required assertion failures, the actual Red E2E receipt satisfies AC-4/8/9 by assertion, and the report has the exact empty Findings table, Q1–Q10 and full intent anchor without home paths/email. Completion-preflight reread confirms rows 0–9 and H1 through H1-6b complete; review collection and H2 remain the coordinator's next work, not part of this read-only assignment. A final identity check again matches the gate exactly.

## Verdict

**approved — zero findings.** The delivered work achieves the registered intent with the required busy-host proof and matching current state. No corrections are required for this round. The coordinator may save this report to the canonical rolling review path, record the verdict and proceed with H2; the unreproduced launch issue remains open. This approval does not authorize a push.

🕐 Completed: 2026-11-18 16:49 (EST)
