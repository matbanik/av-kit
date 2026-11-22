---
date: "2026-11-22"
review_mode: "plan"
target_plan: "docs/execution/plans/2026-11-22-tray-show-and-baseline-fixes/implementation-plan.md"
verdict: "approved"
findings_count: 0
template_version: "2.2"
requested_verbosity: "standard"
agent: "codex-independent-reviewer"
loop_id: "tsb-plan-2026-11-22-tray-show-and-baseline-fixes"
round: 2
---

# Critical Review: 2026-11-22-tray-show-and-baseline-fixes

> **Review Mode:** plan
> **Verdict:** changes_required

## Scope

**Target:** the working-tree implementation plan and task table for Session 102, MEU-164 and both debt fixes, on `main`, HEAD `7f34348`, one worktree.

**Review Type:** independent read-only review by Codex, class `avkit_independent_reviewer`. Claude Code (Anthropic) authored the plan; this reviewer did not.

**Checklist Applied:** PR-1 to PR-9 and Q1 to Q6. D-1361 to D-1368, the supplied execution authorization and scope limits are accepted as instructed. The HDP records carry reversible choices within that scope; no new commit, push, publication, spend or access to Mat's data is authorized here.

Only temporary artifacts were written. No repository file was edited; no pytest, Vitest, package manager, application, Electron test, selftest subprocess or network request ran. Only the five named planning receipts were opened. Forbidden files were not opened. The disclosed host-ignore difference was excluded from conclusions. Completion-preflight was applied to this review deliverable; implementation tasks remain unstarted.

## Intent Anchor

a double-click on the av-kit tray icon brings the main window back, exactly as the tray menu's **Show window** item does: one show function, shared by the menu item and a new `double-click` listener, restores the window if it is minimized, shows it and focuses it. The tray menu keeps its four items in order, and a single click and a right-click behave as today. Vitest and an Electron E2E on the dev PC prove it, with no manual check. The same session fixes the two pytest failures that Session 101's gate had to deselect by name: AC-130.10 compares the two ICC profiles with the header's creation date and time masked, and `plan_slug` in `tools/validate_closeout_artifacts.py` reads the slug from the plan's own folder only, so a dated TEMP folder can no longer supply one. After this session, the full pytest run passes with nothing deselected.

Intent achieved: **partial**, at the plan-specification level. The proposed product behavior and debt algorithms serve the goal, but the prescribed ICC insertion can break the existing test and prevent the required full pytest pass.

## Findings

| # | Severity | Blocking | Kind | Finding | File:Line | Recommendation | Status |
|---|---|---|---|---|---|---|---|
| F1 | High | yes | behavior | **Preserve AC-130.10's decorators when inserting the helper.** Row 0 prescribes inserting `_same_icc_ignoring_creation` immediately before `def test_ac_130_10_cmyk_icc_to_srgb`. That definition already has `parametrize("ac_id", ...)` and `unit` decorators immediately above it. Applying that insertion transfers both decorators to the helper, leaving the original test with an unresolved `ac_id` fixture. Row 1 selects only the new tests, so this can first surface in row 2's existing AC-130.10 run and stop execution under S5. An in-memory AST probe reproduced the decorator transfer. This defeats AC-130.10 and the full-pytest clause of AC-164.8/ICC_HEADER_MASK. Confidence: High. Violates: AC-130. | `docs/execution/plans/2026-11-22-tray-show-and-baseline-fixes/task.md:44`; `tests/unit/test_capture_adapter.py:1655` | Insert before the complete decorated test, using its first decorator as the boundary. Require the edited test to retain the baseline decorator list as well as its original body except the authorized comparison line. | fixed |
| F2 | Medium | no | behavior | **The prescribed ICC Red helper fails its passing guard.** Its body is `return a is not None and a == b`, which returns True for two equal 100-byte strings. AC-164.8's guard requires False for exactly that input and is explicitly required to pass at Red. The Green helper is correct, so this is a test-staging defect, not a reason to weaken its expectations. Confidence: High. | `docs/execution/plans/2026-11-22-tray-show-and-baseline-fixes/implementation-plan.md:111`; `:155`; `:166` | Keep the None/length/full-header validation in both forms; use full byte equality only in Red and the timestamp-masked equality in Green. Keep the guard assertions unchanged. | fixed |
| F3 | Medium | no | behavior | **The copied Red checker rejects the intended Electron assertion.** Row 4 specifies `expect.poll(..., { message: 'tray hook', ... }).toBe(true)`. Installed Playwright prepends that custom message, producing `Error: tray hook`. The copied checker recognizes `Error: expect(` as a JavaScript assertion and classifies `Error: tray hook` as unattributed. Renaming DECLARED_NEW and boundary fixtures does not fix that classification, so both intended Electron Reds fail the row's checker. S3 permits setup repair; the planned runtime proof remains sound. Confidence: High. | `docs/execution/plans/2026-11-22-tray-show-and-baseline-fixes/task.md:44`; `:50`; `docs/execution/plans/2026-11-21-transcript-job-resume/red-check.py:186` | Specify a compatible diagnostic, for example `message: 'expect(tray hook)'`, retaining the `tray hook` needle, or narrowly recognize this custom assertion with a checker fixture while retaining setup-error rejection. | fixed |

## Q1 — Goal coverage

Accepted: the goal is fully allocated, without a manual check or a hidden deferral.

| Goal clause | AC | Rows |
|---|---|---|
| Shared listener/menu function; restore, show, focus | AC-164.1, .2, .4, .5 | 3–6 |
| Four ordered menu items; single/right click preserved | AC-164.1, .6 | 3, 5, H1-2 |
| Hook absent normally; real Electron proof | AC-164.3–.5 | 3–6, H1-2 |
| Timestamp-only ICC differences ignored; other bytes checked | AC-164.8; existing AC-130.10 | 1, 2, H1-2 |
| Own-folder slug; selftest under dated TEMP | AC-164.9 | 1, 2, H1-2 |
| Full pytest passes without deselection | Session gate; H1-4 | H1-2, H1-4 |

Not accepted: the literal ICC insertion instruction, F1, prevents the plan as written from reliably reaching that full-pytest result. No missing goal clause or scope dispute was found.

## Q2 — Tray implementation

Accepted: TRAY_SHOW_SHARED preserves the existing menu and notification registration, keeps the literal `opts.window.show()`, and adds only one event listener (`implementation-plan.md:109`). Installed Electron types document `double-click` for `win32` (`ui/node_modules/electron/electron.d.ts:14894`). Any accompanying `click` has no application listener here, and the existing context-menu registration is unchanged. There is no new left-click/menu-opening code.

`restore()` before `show()` and `focus()` correctly handles minimized and hidden states. It does not trigger `close`; close-to-tray remains the hide path (`index.ts:503`). Startup reveal is a one-shot `ready-to-show` handler (`:526`), and the tray is created after the initial renderer load (`:594`). No conflicting persistent reveal handler was found. The four source pins remain compatible, including `login-item-ipc.test.ts:98` and the label/quit/desktopCapturer checks in `capture-page.test.ts:384` and `:557`.

TRAY_E2E_HOOK is **runtime-flag gated**, not removed from a separate production build. A packaged process launched with `AVKIT_E2E=1` would expose it in its main-process global. That global is not a renderer/preload/IPC surface; the window retains context isolation and sandboxing (`index.ts:493`). This follows the existing shell-log convention and adds no demonstrated security exposure. Correct the phrase “only the E2E build” when implementing; no new packaging requirement is imposed.

## Q3 — Tray tests and harness

Accepted: the per-file Electron mock can override the aliased stub through `importOriginal`, and mocking app-icon avoids its unsupported image `resize` call. The named planning probe reports **1 passed** with this design. Fake listeners, identity comparison and ordered call recording prove sharing and the restore sequence. Missing listener/hook assertions avoid TypeErrors. The intended poll is a matcher assertion rather than a test/action timeout, but its custom diagnostic needs the compatibility correction in F3.

Emitting on the **real Tray** from `app.evaluate` proves registration and execution against a real BrowserWindow. It deliberately trusts Electron's native notification-area event delivery, as D-1366 discloses; that is sufficient for this scoped automated proof. S8 correctly returns to planning if the real object cannot drive the listener.

`launchElectron` satisfies the launcher census (`ui/tests/unit/e2e-harness.test.ts:60`), strips ELECTRON_RUN_AS_NODE, requires scratch app data and retains main-error/clipboard guards. The proposed afterEach owns only its launched application and requires bounded close/polls. With no picker or extra window launched, `BrowserWindow.getAllWindows()[0]` identifies this app's single window; hide/minimize and state predicates are available. Focus is checked after the hidden double-click; the minimized unit case additionally pins the final focus call. No other runtime-test design defect was found.

## Q4 — ICC comparison and preservation

Accepted: ICC v2/v4 header bytes 24–35 are the creation date/time; excluding precisely those bytes preserves the substantive sRGB profile comparison. The supplied reproduction reports only byte 35 differing across 1.1 seconds. An independent in-memory Pillow/LittleCMS profile was 588 bytes, had `RGB ` colour space and an all-zero 16-byte profile ID at 84–99; no computed ID follows the timestamp in this path. The adapter still converts through ImageCms, embeds its generated sRGB profile and has its output pixels independently compared (`adapter.py:394`; `test_capture_adapter.py:1674–1685`). A different colour profile must still match every other byte to pass.

Not accepted: F1's insertion boundary and F2's claimed passing Red guard. The Green comparison passed the independent model for all 12 timestamp positions and rejected changes at 23, 36 and 100. The prescribed Red form rejected timestamp differences but accepted the prohibited short equal strings.

Per-node pins constrain existing test bodies and the one authorized assertion edit. They must also preserve decorator ownership: ordinary `ast.get_source_segment` on a FunctionDef excludes its decorators, so body-only comparison does not catch F1. Comments and whitespace between nodes are not behavior guarantees and are not separately escalated.

## Q5 — Plan slug

Accepted: PLAN_SLUG_PARENT_ONLY fixes the dated-ancestor defect while preserving the caller. The repository-wide tools/tests search found only `plan_slug` and its call in `check_handoff_binding`. The good, wrong-plan and no-AC selftest paths all place the Markdown file directly inside their dated slug folder (`validate_closeout_artifacts.py:2589`, `:2682`, `:2824`); the loose-plan arm should become USAGE (`:2847`).

The independent extracted-function probe confirmed the proposed result for those shapes, the file/folder forms and a bare filename. It also confirmed that all **111** current `implementation-plan.md` files retain their parent slug. Workflow plan paths use that same direct-folder layout. No real current caller requiring an intervening subfolder was found.

The subprocess AC sets both TEMP and TMP before launching a fresh interpreter, so tempfile caching in the pytest process cannot hide the dated-TEMP case. Its 300-second bound is reasonable for this many-arm CLI selftest; runtime was not remeasured. The supplied reproduction establishes old behavior: dated TEMP exit 1, plain TEMP exit 0. The new selftest was not run during review. Nothing material is rejected under Q5.

## Q6 — Pins, gate and registers

Accepted: the independent census across `ui/tests`, `tests` and `mcp-server/tests` found exactly the four direct tray-source pin files named by the plan. Other tray hits concern remote-session process fixtures or UI help text. Other ICC tests exercise profile preservation/orientation without changing this helper; full pytest covers them. No test pins the old 09 tray-row text or an additional plan_slug caller.

H1-2 specifies TypeScript, ESLint, full Vitest, full pytest with **no deselect**, pyright, ruff, build, both Electron files, cleared ELECTRON_RUN_AS_NODE, host-load checks, line endings and the home-path scan. Scope-based omissions of unrelated Electron specs, MCP tests and OpenAPI checks are sound. H1-4 separately checks the no-deselect gate text and passing pytest summary. The proposed script descriptions otherwise provide real checks; absent scripts are explicitly scheduled for creation and their copy sources exist.

Execution status changes use `meu_status.py update/render`, issue resolution uses the copied issue tool/model behind an exclusive Windows handle plus expected SHA-256, and rendering uses `issue_triage.py`. Existing initial registration was performed by the disclosed plan-local byte scripts (`register-meu.py`, `link-issue.py`), rather than by `meu_status.py update`; the named receipts corroborate their bounded registration edits. No claim that every initial registration was done by the status CLI is relied on. The plan's subsequent register checker limits changes to the three issues and grouping row. Nothing material is rejected under Q6.

## Checklist Results

Results below concern observed **plan readiness**, not a completed product gate.

| Check | Result | Procedure / command | Exit | Evidence |
|---|---|---|---|---|
| PR-1 Plan/task alignment | pass | Reviewer read both complete targets and compared AC/row dependencies | null | Same three fixes; debt before tray; H1 then independent review then H2 |
| PR-2 Unstarted | pass | Read task statuses, git status and planned-path inventory | null | All implementation rows unchecked; no new product/test implementation paths present |
| PR-3 Task contracts | pass | Read task table and named task-lint receipt | null | Receipt: 25 rows, acyclic dependencies; creation rows name their missing scripts |
| PR-4 Validation realism | fail | Read prescribed edits and run contract_probe.py | 0 | F1 would remove existing parametrization; F2/F3 contradict intended Red checks |
| PR-5 Source traceability | pass | Compare FIC, canon, issue decisions and HDP records | null | D-1361–D-1368 and named mechanisms cover the proposed behavior |
| PR-6 Correction readiness | pass | Read handoff/review target and correction routing | null | One handoff; existing loop retained; no recheck census due in round 1 |
| PR-7 Scope discipline | pass | Compare exclusions with user instructions and 09 tray canon | null | No requested work deferred |
| PR-8 Reachability | pass | Trace boot → startCaptureTray → shared function; adapter and closeout caller | null | Real producers and negative cases exist; no fabricated production caller |
| PR-9 Named contracts | pass | Compare repeated references to the four single-statement contracts | null | Governing behavior is identifiable; no materially ambiguous live variants |

All manual procedures were observed by `codex-independent-reviewer` with null exit code.

### Reproducible evidence

The probe file is under the review scratch directory. It reads repository sources, executes isolated in-memory contract/function forms and never invokes a suite. Exit 0 means the probe completed and exposed the reported discrepancies; it does not mean the plan passed.

```json
{"schema_version":"evidence.v1","check_id":"tsb-independent-contract-probe","command":"rtk proxy python C:/Temp/av-kit/2026-11-22-tray-show-and-baseline-fixes/review/contract_probe.py","cwd":"P:/av-kit","scope":"ICC staging and comparison; copied Red diagnostic classifier; proposed slug function","phase":"planning","exit_code":0,"result":"fail","tested_state":"main 7f34348 with Session 102 working-tree plan; isolated proposed forms, not implementation","output":"ICC Red equal 100 bytes: True; guard requires False. Inserting at the prescribed def anchor attaches both pytest decorators to _same_icc_ignoring_creation and leaves test_ac_130_10_cmyk_icc_to_srgb decorators=[]. Error: tray hook is classified unattributed. Proposed slug refuses the dated-ancestor loose plan and agrees with all 111 current real plan parents.","fresh":true}
```

```json
{"schema_version":"evidence.v1","check_id":"tsb-independent-pin-census","command":"rtk proxy rg -n -i 'capture-tray|\\bTray\\b|Show window|plan_slug|icc_profile|Always created while the app runs' ui/tests tests mcp-server/tests","cwd":"P:/av-kit","scope":"existing test dependencies","phase":"planning","exit_code":0,"result":"pass","tested_state":"main 7f34348 with Session 102 registration/plan changes","output":"Direct capture-tray source readers: app-icon.test.ts:41, capture-main.behavior.test.ts:129, capture-page.test.ts:36 and login-item-ipc.test.ts:97. Other ICC-profile tests preserve/orient/export existing profiles; no additional tray-source pin or 09 tray-row text pin appeared.","fresh":true}
```

Named planning receipts inspected: `plan-vitest-probe.txt` (1 passed), triage `repro.txt` (ICC byte 35; dated/plain TEMP exit 1/0), `register-meu.txt`, `link-issue.txt` and `tsb99-task-lint.txt`. Those are author-supplied prior observations, not newly executed reviewer tests.

## Verdict

**changes_required** because F1 would break existing AC-130.10 and prevent the required full pytest pass. Make the helper insertion decorator-aware and preserve its decorator list. F2 and F3 are non-blocking test-setup corrections within the current scope. No Critical finding, policy dispute, manual-check requirement or added product scope is raised.

The tray behavior, ICC masking algorithm and slug fix are accepted. Residual limits: native Windows notification-area dispatch is trusted, the hook follows a runtime flag, and runtime/full-gate success must still be established during execution. The coordinator may copy this complete report to the canonical review path; this reviewer did not write there.


## Recheck (round 2)

### Prior Pass Summary

| Finding | Prior Status | Recheck Result |
|---|---|---|
| F1 | open | fixed |
| F2 | open | fixed |
| F3 | open | fixed |

### New Findings

| # | Severity | Blocking | Kind | Finding | File:Line | Recommendation | Status |
|---|---|---|---|---|---|---|---|

### Confirmed Fixes

- **F1 fixed.** `implementation-plan.md:111` and `task.md:44` place the helper before the named test's first decorator and require comparing the complete decorated source, with only the profile-comparison line allowed to differ. The current test has both decorators at `tests/unit/test_capture_adapter.py:1655`. An isolated AST probe of that specified boundary left the helper undecorated and both original decorators on the test. The copied `top_level_sources` (`docs/execution/plans/2026-11-21-transcript-job-resume/row-check.py:265`) includes decorators. Its comparison accepts the one-line edit and rejects deliberate decorator loss. This closes the AC-130.10/AC-164.8 insertion defect.
- **F2 fixed.** `implementation-plan.md:111` now gives Red and Green the same None, equal-length and full-header checks. The guard and timestamp-change expectations remain unchanged (`:155`, `:166`; `task.md:32`, `:46`). The isolated prescribed forms both rejected all seven guard inputs; Red rejected all 12 individual timestamp-byte changes and the combined change, while Green accepted them. Identical full-length inputs passed both forms. Thus Red still exposes the intended masking defect and its guard passes.
- **F3 fixed.** `implementation-plan.md:154`, `:162` and `task.md:50` consistently specify `message: 'expect(tray hook)'`; row 4 retains the `tray hook` reason needle. Row 0 adds the paired positive/negative diagnostic fixtures (`task.md:44`). The extracted classifier and its actual `JS_ASSERTION` pattern (`docs/execution/plans/2026-11-21-transcript-job-resume/red-check.py:186`, `:224`) classify `Error: expect(tray hook)` as an assertion, refuse bare `Error: tray hook` as unattributed, and continue to classify a test timeout as setup failure. The checker is not broadened.

### Correction Regression Check

Both current target files were read in full. The correction script was inspected without execution. The fixes keep the accepted tray wiring, Electron proof, ICC mask, parent-only slug rule and full no-deselect pytest gate intact. No new delivery defect was found. No accepted area was reopened without new evidence.

The governing hook contract correctly says that only a launch with `AVKIT_E2E=1` exposes the main-process global (`implementation-plan.md:110`), and the commit draft uses the corrected launch wording (`task.md:73`). One stale phrase remains in the M-4 decision-log introduction (`implementation-plan.md:290`: "only in the E2E build"). This is a clerical wording note: align it with the runtime-flag contract when convenient; no separate build or product change is required.

### Recheck Checklist Results

These are plan-readiness observations. The round 1 narrative and its failed checklist/probe above are preserved as historical evidence; this section and the updated frontmatter give the current verdict.

| Check | Result | Procedure / command | Exit | Evidence |
|---|---|---|---|---|
| F1 decorator boundary and preservation | pass | Read both complete targets; isolated AST insertion and extracted decorated-source comparison | 0 | Helper has no decorators; existing test keeps both; lost decorator rejected |
| F2 intended Red and passing guard | pass | Isolated prescribed Red and Green helper forms against guard and timestamp-change cases | 0 | Seven guard cases pass at both stages; 13 time-change cases fail Red and pass Green |
| F3 diagnostic compatibility | pass | Extract actual classifier and patterns; classify corrected, bare-message and timeout diagnostics | 0 | assertion / unattributed / setup, respectively |
| Correction regression review | pass | Reviewer compared full corrected plan/task, correction script and affected source contracts | null | Scope and accepted algorithms preserved; both plan files remain LF |
| Author-supplied task lint receipt | pass | Read `tsb99-task-lint.txt`; not rerun | null | Receipt says OK, 25 rows, dependencies resolve and are acyclic |
| Product execution gates | n/a | Deliberately not run during this read-only plan review | null | Full pytest, Vitest, build and real Electron proof remain execution obligations |

Manual observations were made by `codex-independent-reviewer`. The three isolated checks above were all performed by the following command, not by product tests or the proposed future checkers:

```json
{"schema_version": "evidence.v1", "check_id": "tsb-independent-round-2-contract-probe", "command": "rtk proxy python C:/Temp/av-kit/tsb-r2-probe.py", "cwd": "P:/av-kit", "scope": "F1 decorator preservation; F2 Red/Green ICC forms; F3 actual diagnostic classifier; plan LF", "phase": "planning", "exit_code": 0, "result": "pass", "tested_state": "Round 2 working-tree implementation-plan.md and task.md; isolated prescribed forms and extracted existing functions, not implementation", "output": "F1: helper decorators=0; existing test decorators=2 unchanged; one-line comparison accepted; lost decorator rejected.\nF2 red: all seven guard cases pass; 12 individual and one combined time-byte changes give False.\nF2 green: all seven guard cases pass; 12 individual and one combined time-byte changes give True.\nF3: Error: expect(tray hook) => assertion; bare Error: tray hook => unattributed; test timeout => setup.\nBoth plan files remain LF. Probe finished; no suite, app, selftest subprocess or repository import ran.", "fresh": true}
```

No repository file was changed. Only scratch files under `C:/Temp/av-kit` were written. No pytest, Vitest, package manager, application, Electron test, selftest subprocess or network request ran. Forbidden files were not opened, and no git-status ignore difference was used as evidence. Completion-preflight was applied to the review deliverable; all 25 execution tasks remain unstarted and are outside this review's write scope.

### Verdict

**approved**. F1, F2 and F3 are fixed, with no new delivery finding. Intent achieved: **yes**, at the plan-specification level. Executing this corrected plan addresses the complete registered goal; runtime and full-gate success still need execution evidence. There is no required follow-up correction before execution. The coordinator may copy this complete rolling report to the canonical path; this reviewer did not write there.
