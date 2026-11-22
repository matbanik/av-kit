---
date: "2026-11-22"
review_mode: "execution"
target_plan: "docs/execution/plans/2026-11-22-tray-show-and-baseline-fixes/implementation-plan.md"
verdict: "approved"
findings_count: 0
template_version: "2.2"
requested_verbosity: "standard"
agent: "codex-independent-reviewer"
loop_id: "tsb-execution-2026-11-22-tray-show-and-baseline-fixes"
round: 1
---

# Critical Review: 2026-11-22-tray-show-and-baseline-fixes

> **Review Mode:** execution
> **Verdict:** approved

## Scope

**Target:** Session 102, MEU-164, the only session in this grouping. Reviewed the delta from `baseline.sha` (`7f34348d77be9c126e804aaf10344a921f127869`) in the plan's Files Modified paths against AC-164.1 through AC-164.9, Mat's request, 09 §Tray double-click and the two debt issues. The correlated evidence is `.agent/context/handoffs/2026-11-22-tray-show-and-baseline-fixes-MEU-164-handoff.md`.

**Review Type:** independent execution review by Codex, class `avkit_independent_reviewer`. Claude Code, vendor Anthropic, authored the plan and implementation.

**Checklist Applied:** Q1–Q7, implementation IR-1–IR-7, reviewer AV-1–AV-6 and applicable documentation consistency. Approved decisions D-1365 through D-1368 were accepted; execution decisions and disclosed departures were assessed for behavioral and verification effects.

All reviewer writes are under `C:/Temp/av-kit`. No repository file was edited. No install, sync, build, Electron/Playwright run, backend/app launch, network request or real app-data access occurred. Secret paths were not opened. Python checks used `PYTHONDONTWRITEBYTECODE=1`, scratch TMP/TEMP and cleared `ELECTRON_RUN_AS_NODE`. After the default uv cache was inaccessible, `UV_CACHE_DIR` was moved into scratch and `UV_OFFLINE=true` was set; no dependency synchronization occurred.

**Current tested_state:** `7f34348d77be9c126e804aaf10344a921f127869+e1a863c71f3d51c29aadd0c810aac7dc7e21df4f91c14e17aef0f7bbd182e70c`.

It exactly matches both gate identity receipts and the H1 recheck, and remained unchanged after independent probes. There is no sandbox identity difference to waive. `identity.py` excludes `.claude/settings.local.json` by name before hashing, so the unreadable global git ignore does not affect this result; the local-settings file was not opened.

## Intent Anchor

a double-click on the av-kit tray icon brings the main window back, exactly as the tray menu's **Show window** item does: one show function, shared by the menu item and a new `double-click` listener, restores the window if it is minimized, shows it and focuses it. The tray menu keeps its four items in order, and a single click and a right-click behave as today. Vitest and an Electron E2E on the dev PC prove it, with no manual check. The same session fixes the two pytest failures that Session 101's gate had to deselect by name: AC-130.10 compares the two ICC profiles with the header's creation date and time masked, and `plan_slug` in `tools/validate_closeout_artifacts.py` reads the slug from the plan's own folder only, so a dated TEMP folder can no longer supply one. After this session, the full pytest run passes with nothing deselected.

Intent achieved: **yes**. No evidence-backed High or Critical defect, or other substantive finding, survives review.

## Findings

| # | Severity | Blocking | Kind | Finding | File:Line | Recommendation | Status |
|---|---|---|---|---|---|---|---|

## Q1 — Goal

Accepted: every goal clause has implementation, meaningful assertions and passing evidence.

| Goal clause | AC | Source and decisive evidence |
|---|---|---|
| Double-click performs the menu's Show window action | AC-164.1, AC-164.4 | `ui/src/main/capture-tray.ts:24`, `:48`; listener identity assertion; `tsb-row5-green.txt`: 5 passed; `tsb-row6-tray.txt`: 6 passed |
| One function restores only when minimized, then shows and focuses | AC-164.2, AC-164.5 | `capture-tray.ts:16`; both unit call-order cases and real minimized-window assertions |
| Four menu items retain their order; single/right-click behavior retained | AC-164.1, AC-164.6 | Menu remains Show window, Capture region, Open inbox folder, Quit; exactly one added `double-click` listener; original context-menu registration and other callbacks retained |
| Automated Vitest and real Electron proof; no manual check | AC-164.1–AC-164.6 | Five new unit tests; hidden and minimized Electron cases pass three times each and again in the gate |
| AC-130.10 masks only creation date/time | AC-164.8, AC-130.10 | `tests/unit/test_capture_adapter.py:1655`, `:1694`; independent selection: 6 passed, 45 deselected; exhaustive byte probe passes |
| Only the plan's own folder supplies its slug | AC-164.9 | `tools/validate_closeout_artifacts.py:298`; independent 3-test module passes, including dated-TEMP CLI selftest |
| Full pytest passes without deselection | AC-164.8, AC-164.9; goal | Gate argv contains no deselect; `tsb-D6-py-tests.txt`: 3348 passed, 37 warnings in 302.45s |

AC-164.7's canon update is separately verified below. No requested behavior was dropped or replaced with a manual check.

## Q2 — Tray

Accepted: `TRAY_SHOW_SHARED` is applied literally. The menu item's `click` and `tray.on('double-click', showWindow)` receive the same function object (`ui/src/main/capture-tray.ts:16`, `:24`, `:48`). `restore()` is conditional on `isMinimized()`, and `show()` precedes `focus()`. No toggle or single/right-click listener was added.

`TRAY_E2E_HOOK` is guarded by the exact runtime check `process.env.AVKIT_E2E === '1'` (`capture-tray.ts:50`). Without that value, this module sets no global reference. With it, the hook holds the actual tray and menu in the main process only. Packaging is not a separate guard: a packaged launch explicitly given that flag would also expose it, consistent with D-1366 and D-1369. There is no renderer, preload, IPC, API or MCP exposure, and no extra retained global reference in an ordinary launch. The app already retains its tray through `registerNotifyTray`.

The unit mock records Electron's constructor, menu construction, context-menu assignment and event-listener registration. Its callback identity and ordered-call assertions are strong; the real Electron test supplies the complementary runtime proof. Capture region, inbox-folder and Quit callbacks, tooltip, notification registration and return value retain their original behavior. `ui/src/main/index.ts:594` still invokes the same function, and all 17 read-only context hashes, including index, icon and notification code, are unchanged. Login-item and the other pinned unit tests passed unchanged. No tray regression was found.

## Q3 — Electron

Accepted: both Red blocks in `tsb-row4-red.txt` identify `Error: expect(tray hook)`, expected true, received false, at `tray-double-click.test.ts:55`. These are bounded assertion-poll failures after successful launch and app-shell readiness, not launch failures, test-level timeouts or setup exceptions. The source and `red-reason` checker distinguish those cases.

`tsb-row6-tray.txt` contains six successful cases: three `AC-164.4 hidden` and three `AC-164.5 minimized`, ending `6 passed (4.4s)`. The hidden case first verifies hidden state, emits on the real Tray and asserts visible plus focused, then hides again and invokes the actual Show window menu item and asserts visible (`ui/tests/e2e/tray-double-click.test.ts:92`). The minimized case verifies minimized state before emitting and then asserts restored plus visible (`:103`). The final gate adds `2 passed (2.2s)`; startup-reveal independently passes two cases in row 6 and two in the gate. No unhandled-rejection record appears in the accepted runtime receipts.

Each launch supplies `mkdtempSync` scratch `AVKIT_APP_DATA` (`tray-double-click.test.ts:43`); the shared launch helper requires it below tmpdir, sets AVKIT_E2E, clears ELECTRON_RUN_AS_NODE and installs error/clipboard guards (`electron-app.ts:116`, `electron-env.ts:38`, `:89`). Teardown closes only that Electron application, with a fallback kill of its captured child (`tray-double-click.test.ts:26`). No global process kill or real-profile path is present.

The real Tray event is emitted from the main process; physical notification-area mouse delivery is the approved D-1366 trust boundary. I accepted matching recorded Electron evidence and did not claim a new reviewer Electron run.

## Q4 — ICC mask

Accepted: `ICC_HEADER_MASK` removes exactly the half-open slice `[24:36]`, the twelve bytes identified by ICC.1 §7.2.1 as creation date/time. Offline corroboration decoded those bytes as six big-endian unsigned shorts and matched them to the installed LittleCMS profile's `creation_date`. No external spec fetch was performed under the no-network instruction.

The helper rejects None, unequal lengths and headers shorter than 128 bytes before comparison (`tests/unit/test_capture_adapter.py:1660`). Every remaining byte participates in equality. An independent probe mutated each of all 588 bytes in a generated profile: precisely offsets 24–35 compared equal, and every other mutation compared unequal. Six missing/length/short-header guard pairs were rejected. The committed test expectations exercise each timestamp offset, all twelve together, neighboring bytes 23 and 36, byte 100, length, None and short-profile cases (`:1699`, `:1716`).

AC-130.10 still builds a nontrivial CMYK source profile, proves managed conversion differs from plain RGB conversion, asserts output mode/size, checks the masked sRGB profile and compares output pixels exactly with ImageCms's managed conversion (`:1667`). Its comparison at `:1694` is its only changed line, including unchanged decorators. Independent `named-edits` and `pins-unchanged` checks pass; the other 110 existing top-level nodes retain their row-0 source. No weakening beyond the approved twelve-byte exception was found.

## Q5 — Plan slug

Accepted: `PLAN_SLUG_PARENT_ONLY` checks the immediate parent of a `.md` plan path, otherwise the final folder, and retains the prior Usage diagnostic (`tools/validate_closeout_artifacts.py:290`). The single production caller remains `check_handoff_binding` at `:310`; canonical plans and selftest plans sit directly inside their slug folder.

Independent probes passed ten valid cases covering file/folder paths, relative/absolute paths, forward/back slashes and trailing folder slashes on Windows. Four loose paths, including a backslash path under a dated ancestor and a bare filename, were refused. The new pytest module passed all three tests, including the actual validator CLI selftest under a deliberately dated TEMP. The gate's selftest separately reports `231 arm(s), 0 failure(s) [96 must-OK arms]`.

Independent `slug-edit` and `pins-unchanged` report that only `plan_slug` changed and the other 138 existing top-level nodes retain their source. No caller regression or unrelated selftest edit was found.

## Q6 — Gate and pins

Accepted: the gate is sequential and fail-fast, captures each child exit immediately and checks input identity before/after. Its recorded 30 steps all have exit 0; it ends `session-gate: all steps exit 0`. I inspected the actual gate and individual decisive receipts, not only the handoff's summary.

| Stage | Accepted observed result |
|---|---|
| Static | UI types/lint pass; Python types: 0 errors/warnings; ruff checks pass; 16 files formatted; task contract, scope, home-path, line-ending and source-pin checks pass |
| Targeted | Debt: 9 passed, 45 deselected; closeout selftest: 231 arms, 0 failures; tray plus unit pins: 68 tests in 5 files pass |
| Full UI | 151 files, 1674 tests passed; row-0 base was 150 files, 1669 tests |
| Full Python | 3348 passed, 37 warnings; row-0 base was 3343 passed, 37 warnings; no deselection in full-run argv or summary |
| Build and runtime | UI build passes; tray Electron: 2 passed; startup-reveal: 2 passed; zero rejection-record lines |
| Host load | Full-stage sample 19.1%; Electron samples 9.5% and 8.7%; row-6 samples 16.0% and 17.0%, all below the 50% limit |
| State | Both render checks pass; before/after and independently re-derived identities match |

Targeted `-k` deselections are not the full suite. The `$pytest` base and `py-tests` step contain no `--deselect`; `tsb-no-deselect.txt` agrees with independent argv inspection. H1-4's revised scanner ignores comments and output-only lines, retaining checks of executable lines and exactly one full pytest step. Its mutation probe refuses deselection in either argv source and a missing py-tests step. The disclosed correction did not weaken this delivered gate.

The six file pins and Python-node pins pass independently. `startup-reveal` and `test_framework_adoption.py::test_evidence_contract_real_cli_selftests` retain their hashes. `row-check canon` verifies only the tray row and six-line Delivered insertion differ from row 0; the earlier residual registration visible against HEAD was already in row 0. 09 remains CRLF. `row-check register` verifies all 157 issue IDs, unrelated issues unchanged, only the three permitted fields changed for each resolved issue, and only grouping row 102 changed. Issue and MEU renders match their SSOTs. Row-7 receipts and script inspection support use of the repository's save/render tools, followed by disclosed byte-only CRLF restoration.

The skipped remainder of Electron, MCP tests and OpenAPI have the approved, applicable scope bases: only the tray app module changed; tray and startup tests cover its runtime paths; no MCP or API change exists. No missing required gate or unsound skip was found.

## Q7 — Safety and fidelity

Accepted: independent line-ending checks report `20 scope path(s), 0 problem(s)`. Byte-edit scripts require unique old text and retain expected endings; the register restoration changes endings only, with parsed register and render checks passing afterward. The gate uses undated TEMP for ordinary tests and dated TEMP for the dedicated closeout selftest, preserving the intended regression trigger. Extracting the exact Validation cells into pwsh scripts retains their commands and failure propagation.

D-1369 accurately states a runtime environment flag, with no separate build claim. D-1370 distinguishes range-end text from allocated decision IDs; the baseline records eleven such references, and the implementation still counts a separate non-range match on the same line as a use. No actual conflicting allocated ID was identified.

Independent audit observes `main`, one worktree, unchanged HEAD, no staged paths, no outside-scope non-secret changed paths, zero baseline-dirty hash mismatches and all 17 read-only context files unchanged. The gate's 43-path pre-handoff scope observation and the current allowed closeout additions are compatible with the matching identity: designated closeout outputs are intentionally excluded. Expected build outputs are gitignored. The reviewed scripts contain no session commit, stash or revert operation; nothing in the reviewed state or receipts contradicts the uncommitted handoff. This is state/receipt verification, not a claim to reconstruct every prior shell command.

The current changed/new text audit finds no literal home-folder path and no personal-email candidate; JSON source pins were decoded before scanning to avoid mistaking escaped newlines followed by pytest decorators for email addresses. Only the configured noreply identity is present. Forbidden secret files and the fleet hub were excluded before reads.

The handoff's AC table, counts, departures and full-gate identity agree with the code and receipts. H2 reflection, metrics, approval recording and commit draft correctly remain coordinator work after this review; a commit still requires Mat's authorization. No concrete safety or fidelity failure was found.

## Checklist Results

### Implementation and adversarial checks

| Check | Result | Observation |
|---|---|---|
| IR-1 runtime | pass | Real Electron hidden/minimized and startup-reveal receipts match unchanged tested inputs |
| IR-2 stubs | n/a | No new product stub or persistence implementation |
| IR-3 error mapping | n/a | No route or write boundary changes |
| IR-4 generalization | pass | ICC slice boundaries and full byte domain probed; slug file/folder and separator variants probed |
| IR-5 rigor | pass | All twelve new tests audited below, with paired cases grouped; no weak case found |
| IR-6 input boundaries | pass | Exact environment flag; slug rejects invalid folder binding; helper rejects absent/truncated data |
| IR-7 AC/deferrals | pass | All nine dotted ACs have direct proof; no silently deferred contract work |
| AV-1–AV-3 | pass | Assertion Reds, immutable Green expectations and explicit listener/state/byte assertions |
| AV-4–AV-6 | pass | No added skip/xfail, placeholder or unsourced behavior; approved decisions applied |
| Documentation consistency | pass | Canon and generated register/status surfaces match delivered behavior |

### Test rigor audit

| Test | Rating | Decisive assertions |
|---|---|---|
| Vitest AC-164.1 | Strong | Exact item order, one tray, context-menu object, sole event and callback object identity |
| Vitest AC-164.2 minimized | Strong | Exact restore/show/focus order via event and menu; unrelated actions untouched |
| Vitest AC-164.2 non-minimized | Strong | Exact show/focus order, hence no restore; unrelated actions untouched |
| Vitest AC-164.3 unset | Strong | Hook absent in ordinary launch; environment restored after test |
| Vitest AC-164.3 set | Strong | Exact created tray and menu objects exposed only with flag |
| Electron AC-164.4 hidden | Strong | Hidden preconditions, real Tray event, visible/focused result and real menu action |
| Electron AC-164.5 minimized | Strong | Minimized precondition, real event, restored/visible result |
| Pytest AC-164.8 timestamp/guard pair | Strong | Each masked byte and all twelve; neighboring/other bytes and invalid profiles |
| Pytest AC-164.9 loose/valid path pair | Strong | Usage and diagnostic for false ancestor; exact valid file/folder slug |
| Pytest AC-164.9 dated-TEMP selftest | Strong | Actual CLI exit, isolated dated TEMP and bounded subprocess |

Existing AC-130.10 remains Strong: independent managed pixels differ from unmanaged pixels and match the actual crop exactly; mode, dimensions and sRGB profile remain asserted. Unchanged pin tests are corroborating regressions, with real Electron supplying the runtime proof absent from source-text pins.

### Independent command evidence

Commands run from `P:/av-kit` through `rtk proxy`; environment used scratch TMP/TEMP, scratch offline uv cache, UTF-8 output, bytecode disabled and ELECTRON_RUN_AS_NODE unset. `review_verify.py` and `review_audit.py` reside only in the assigned scratch folder. The former records each checker command, exit and complete output in `exec-review/results.json`.

```json
{"schema_version":"evidence.v1","check_id":"review-identity","command":"rtk proxy uv run --no-sync python docs/execution/plans/2026-11-22-tray-show-and-baseline-fixes/identity.py --state-only","cwd":"P:/av-kit","scope":"current D6 input identity; repeated after probes","phase":"static","exit_code":0,"result":"pass","tested_state":"7f34348d77be9c126e804aaf10344a921f127869+e1a863c71f3d51c29aadd0c810aac7dc7e21df4f91c14e17aef0f7bbd182e70c","output":"7f34348d77be9c126e804aaf10344a921f127869+e1a863c71f3d51c29aadd0c810aac7dc7e21df4f91c14e17aef0f7bbd182e70c; identical to both full-gate identity receipts and H1 recheck"}
```

```json
{"schema_version":"evidence.v1","check_id":"review-capture-pytest","command":"rtk proxy uv run --no-sync pytest -q --tb=short -p no:cacheprovider tests/unit/test_capture_adapter.py -k \"ac_130_10 or ac_164\"","cwd":"P:/av-kit","scope":"AC-130.10 and AC-164.8","phase":"targeted","exit_code":0,"result":"pass","tested_state":"7f34348d77be9c126e804aaf10344a921f127869+e1a863c71f3d51c29aadd0c810aac7dc7e21df4f91c14e17aef0f7bbd182e70c","output":"6 passed, 45 deselected in 0.26s"}
```

```json
{"schema_version":"evidence.v1","check_id":"review-slug-pytest","command":"rtk proxy uv run --no-sync pytest -q --tb=short -p no:cacheprovider tests/tooling/test_closeout_plan_slug.py","cwd":"P:/av-kit","scope":"AC-164.9, including actual dated-TEMP CLI selftest","phase":"targeted","exit_code":0,"result":"pass","tested_state":"7f34348d77be9c126e804aaf10344a921f127869+e1a863c71f3d51c29aadd0c810aac7dc7e21df4f91c14e17aef0f7bbd182e70c","output":"3 passed in 0.35s"}
```

```json
{"schema_version":"evidence.v1","check_id":"review-contract-probes","command":"rtk proxy uv run --no-sync python C:/Temp/av-kit/2026-11-22-tray-show-and-baseline-fixes/exec-review/review_verify.py","cwd":"P:/av-kit","scope":"read-only row checks, source pins, line endings, selftests, renders, ICC byte domain and slug path variants","phase":"targeted","exit_code":0,"result":"pass","tested_state":"7f34348d77be9c126e804aaf10344a921f127869+e1a863c71f3d51c29aadd0c810aac7dc7e21df4f91c14e17aef0f7bbd182e70c","output":"pins-unchanged, named-edits --stage green, slug-edit, canon, register and red-unchanged: 0 problems each; eol-check: 20 paths, 0 problems; red-check selftest: 122 fixtures, 0 wrong; eol-check selftest: 24 cases, 0 wrong; row-check selftest: 0 wrong; issue and MEU render --check pass; slug: 10 valid cases and 4 loose paths refused; ICC: 588 individual-byte mutations, only offsets 24..35 ignored, six guards refused; final identity unchanged"}
```

```json
{"schema_version":"evidence.v1","check_id":"review-scope-evidence-audit","command":"rtk proxy python C:/Temp/av-kit/2026-11-22-tray-show-and-baseline-fixes/exec-review/review_audit.py","cwd":"P:/av-kit","scope":"current scope, unchanged context, privacy and decisive receipt comparison","phase":"static","exit_code":0,"result":"pass","tested_state":"7f34348d77be9c126e804aaf10344a921f127869+e1a863c71f3d51c29aadd0c810aac7dc7e21df4f91c14e17aef0f7bbd182e70c","output":"main; HEAD unchanged; staged paths []; one worktree; baseline dirty hash mismatches []; 17 read-only hashes unchanged; 45 non-secret changed paths, outside allowed scope []; literal home-folder matches []; non-noreply/non-example email candidates []; full Python 3348 passed, 37 warnings; UI 151 files/1674 tests passed; closeout selftest 231 arms/0 failures; one executable py-tests step and no --deselect"}
```

```json
{"schema_version":"evidence.v1","check_id":"review-recorded-full-gate","procedure":"Inspect session-gate.ps1, tsb-gate-h1.txt and the individual D6 receipts; compare their counts, command scope and identities with the handoff and independently computed current identity; inspect row-4 Red and row-6 repeated Electron receipts against the unchanged test source.","observer":"codex-independent-reviewer","cwd":"P:/av-kit","scope":"recorded fresh full gate and real Electron proof; no reviewer GUI/full-suite rerun","phase":"full","exit_code":null,"result":"pass","tested_state":"7f34348d77be9c126e804aaf10344a921f127869+e1a863c71f3d51c29aadd0c810aac7dc7e21df4f91c14e17aef0f7bbd182e70c","fresh":true,"output":"Gate: all 30 steps exit 0; 3348 pytest passed with no deselection; 1674 Vitest tests in 151 files passed; scoped Electron files 2+2 passed with zero rejection lines; row 6 adds three hidden and three minimized passes; recorded before/after states exactly equal independently derived current state."}
```

Scratch receipts alone are not the evidence: the decisive outputs and observation procedure are embedded above. Full-suite and runtime outcomes are attributed to inspected implementation receipts, while the independent commands are reported separately.

## Verdict

**approved** — the delivered work achieves the registered intent. There are no findings and no corrective implementation request.

The coordinator can validate and copy this report byte-for-byte to the canonical implementation-review path, record the verdict in the existing round-1 ledger and continue H2. This report grants no commit or push authorization. Reflection, metrics and commit draft remain post-review coordinator work.

Residual scope: Electron's native translation of a physical tray double-click is trusted as approved in D-1366; the tests drive the real Tray event and real window state. No manual check or additional host launch is required by this plan.

🕐 Completed: 2026-11-22 11:11 (EST)
