---
date: "2026-10-14"
review_mode: plan
target_plan: P:/av-kit-wt/s38-capture-filmstrip-actions/docs/execution/plans/2026-10-14-capture-filmstrip-actions/implementation-plan.md
verdict: approved
findings_count: 1
round: 1
template_version: "2.2"
requested_verbosity: standard
agent: gpt-6.1-sol
---

# Critical Review: 2026-10-14-capture-filmstrip-actions

> **Review Mode**: plan
> **Verdict**: changes_required
> **Reviewer**: gpt-6.1-sol, independent OpenAI reviewer of the Anthropic-authored plan.
> **Round**: 1. No Critical findings. Four High blocking findings and one Medium non-blocking finding.

## Intent Anchor

> Session 38 delivers MEU-88 (a thumbnail menu with Copy full path, Copy image and Delete) and MEU-89 (Shift-click range selection with one batch Delete), changing only `ui/` and three hub docs, with one new main-process IPC channel for the image clipboard.

Executing this plan would deliver much of the intended feature, but it does not yet establish correct non-PNG image content, range selection from the initially selected shot, or the asserted error/scope controls. Intent achieved: **partial**.

## Scope

Reviewed only the worktree **P:/av-kit-wt/s38-capture-filmstrip-actions**, branch claude/s38-capture-filmstrip-actions. No plan, product or test files were read from the separate P:/av-kit checkout.

Primary targets: implementation-plan.md, task.md, validate-task.ps1 and plan_checks.py in docs/execution/plans/2026-10-14-capture-filmstrip-actions/. Reviewed the plan-time diff to gui-actions-index.md and meu-status.yaml, and the status of the two rendered hub files.

Canon sampled: 09-screenshot-capture.md filmstrip/menu/multi-select/HelpCard/MEU sections; 06-gui.md preload and IPC rules; Session 38 grouping and D-1–D-7; both known-issue records; the Session 30 approved peer plan, scripts and rolling plan review. Production paths traced through CaptureFilmstrip, CapturePage, capture-commands, useCaptureCatalog, capture-image, help content, main ipc/index/preload and capture-picker. Relevant IPC census, channel pins, GUI audit, capture behavior/help, queue-canon, test-id registry and Electron seam files were inspected. Installed Vitest and Playwright source was read to resolve report and keyboard semantics.

This is an unstarted plan: all 19 task rows are unchecked; new feature tests/modules and Session 38 handoffs are absent and scheduled for creation. Initial git status showed planning/hub changes only. No repository file was written. Only this report and scratch receipts under C:/Temp/av-kit were written.

## Findings

Paths in this table are relative to the worktree; plan-local basenames refer to the target plan folder.

| # | Severity | Blocking | Kind | Finding | File:Line | Recommendation | Status |
|---|---|---|---|---|---|---|---|
| F1 | High | yes | behavior | **Non-PNG Copy image can copy a blank image while satisfying the proposed tests.** RENDERER_PNG names bitmap creation, a same-size OffscreenCanvas and PNG encoding, but never draws the bitmap. AC-88.4 injects the encoder, AC-88.5 checks the PNG signature, and AC-88.12(b) checks only non-empty NativeImage and dimensions. A transparent PNG of the right size satisfies these oracles without copying the shot's pixels. Confidence: High. Violates AC-88.4/5/12 and PR-8's observable/negative-oracle contract. | implementation-plan.md:129; implementation-plan.md:181; implementation-plan.md:182; implementation-plan.md:189 | Require drawing the decoded bitmap into a 2D context before encoding. Add an Electron pixel-content oracle using a distinctive non-transparent WebP fixture and an expected bitmap; prove a same-size blank image fails. | open |
| F2 | High | yes | behavior | **The first Shift-click after automatic selection does not select a range from the current shot.** RANGE starts with a null anchor and treats Shift-click with a null anchor as a plain click. CapturePage automatically selects the newest shot without a plain click, so opening three shots and Shift-clicking the third produces no range. AC-89.2 and AC-89.9 both prime the anchor with a plain click and miss this normal entry path. Confidence: High. Violates Spec 09:796 and AC-89.2's range-selection intent. | implementation-plan.md:145; implementation-plan.md:245; implementation-plan.md:252; ui/src/renderer/src/features/capture/CapturePage.tsx:281 | When a valid current shot exists and no anchor exists, use that shot as the first Shift-click anchor. Cover initial auto-selection and selection recovery after anchor removal, preserving the fixed anchor across later Shift-clicks and dirty-confirm cancellation. | open |
| F3 | High | yes | control-defeat | **BASELINE_RED can hide an unrelated unhandled Vitest error.** mechanism: swallowed-exit-code. vitest_ok accepts any nonzero process exit whenever the known queue-canon failure is present. Installed Vitest sets exit 1 for unhandled errors but its JSON reporter discards the separate errors argument. A run with the one allowed assertion failure plus an unhandled rejection therefore has the same inspected assertions/counts as the allowed baseline; vitest_ok and floors accept it, and the full gate replaces the failing process exit with the checker exit. Confidence: High. Violates PR-4/PR-8 and the full-gate error contract supporting AC-88/89. | plan_checks.py:125; plan_checks.py:137; plan_checks.py:289; validate-task.ps1:249 | Preserve a separate unhandled-error signal and reject it before applying the single-assertion tolerance. Alternatively take the isolated token fix as an explicit prerequisite and require exit 0 thereafter. Add a negative verifier fixture containing the known failure plus an unrelated unhandled rejection. | open |
| F4 | High | yes | control-defeat | **scope does not enforce the registered repository scope.** mechanism: incomplete-scope-allowlist. It queries only FROZEN, ui/src/main, ui and docs/build-plan. Existing root pyproject.toml and uv.lock are in none of those sets. A change to either is invisible to every rejection branch, so scope can pass a Python dependency/configuration change while the full gate skips Python on its claimed unchanged-scope basis. Confidence: High. Violates PRODUCT_SCOPE, the registered Goal and PR-7/PR-8. | plan_checks.py:56; plan_checks.py:435; plan_checks.py:445; validate-task.ps1:210 | Inventory all repository changes against baseline.sha, including untracked paths, then allow only the declared product files and explicit planning/closeout paths. Reject unlisted root configuration, tests and workflow changes. Add negative fixtures for pyproject.toml and an unlisted source/test path. | open |
| F5 | Medium | no | behavior | **Row 3's main-only Green check typechecks renderer tests before their new module exists.** Row 2 writes capture-clipboard.test.ts against the new capture-clipboard.ts; row 3 creates only main/preload code, but green88-main runs the whole-project typecheck. ui/tsconfig.json includes tests, so the unresolved renderer-module import prevents this row going green until row 4's work is done. This is a false failure, not a false pass. Confidence: High. Violates PR-1/PR-4 task ordering. | task.md:37; task.md:38; task.md:39; validate-task.ps1:189; ui/tsconfig.json:15 | Keep row 3's main Vitest check and move the whole-project typecheck after renderer implementation, or provide a genuinely scoped main check. Do not add placeholder production modules merely to satisfy typechecking. | open |

### Decisive static traces

**F1:** The HTML Standard initializes OffscreenCanvas pixels to transparent black. Encoding that untouched bitmap does not copy the decoded source. The planned clipboard size/non-empty checks cannot distinguish it from the intended picture. This is a missing image-content oracle, not a request to prescribe coding style. [HTML canvas standard](https://html.spec.whatwg.org/multipage/canvas.html#the-offscreencanvas-interface)

**F2:** CapturePage:282–287 sets selectedId when null; it does not pass through chooseItem. The proposed RANGE state has no corresponding anchor initialization. The counterexample requires no dirty state, failed request or unusual input.

**F3:** Installed ui/node_modules/vitest/dist/chunks/cli-api.DVe0nWUx.js:9893–9894 sets process.exitCode = 1 for unhandled errors. Its JSON reporter, chunks/index.VByaPkjc.js:1765–1766, receives _errors and ignores it; :1747–1761 emits counts and assertions without that error list. With the usual BASELINE_RED assertion still failing, plan_checks.py:137 does not reject the nonzero exit. floors only inspects assertion failures and totals. These statements establish the false-pass by source tracing; no synthetic run or project test was executed.

**F4:** pyproject.toml and uv.lock both exist. They cannot appear in changed(base, *FROZEN), changed(base, "ui/src/main") or changed(base, "ui", "docs/build-plan"). Therefore changing those files cannot affect scope's result. The narrow-scope skip in validate-task.ps1:210–222 supplies the consequential call chain.

## Checklist Results

Manual results below were observed by **gpt-6.1-sol**, using the cited worktree file/line reads and diff. Manual checks have null exit codes; a successful file-read command is not represented as a passing product test.

### Plan Review (PR)

| Check | Result | Observed evidence |
|---|---|---|
| PR-1 Plan/task alignment | partial | Same MEUs, files and dependency order overall; F5 identifies a premature global check. |
| PR-2 Not-started confirmation | pass | 19 unchecked rows, no new product/test files or Session 38 handoffs; initial git status has no ui changes. |
| PR-3 Task contract completeness | pass | All task rows provide owner, deliverable, exact validation, dependency/context metadata and status. static reports 19 rows. |
| PR-4 Validation realism | fail | Scripts exist and argv resolve through current package scripts, including the Playwright outputFile wrapper; F3/F4 defeat asserted controls. |
| PR-5 Source-backed planning | partial | ACs and decisions have sources, but the initial null-anchor rule loses Spec 09:796 behavior (F2). |
| PR-6 Handoff/corrections readiness | pass | Both MEU handoff paths and rolling reviews are explicit. Round-2 census prerequisite is not applicable in Round 1. |
| PR-7 Scope discipline | fail | Out-of-scope rows are substantively sourced; the enforcing scope control still misses root configuration (F4). |
| PR-8 Reachability/negative oracles | fail | Production clipboard/delete paths are traceable; blank-image oracle and error/scope counterexamples remain (F1/F3/F4). |
| PR-9 Single-statement discipline | pass | Named contract table governs shared values. Repeated channel/count literals agree; no material competing contract found. |

### Docs Review (DR)

| Check | Result | Observed evidence |
|---|---|---|
| DR-1 Claim-to-state match | pass | Four specified Capture ACTION_ROWS appear after capture:delete; execution_plan changes only for MEU-88/89. |
| DR-2 Residual old terms | n/a | No rename or terminology migration. |
| DR-3 Downstream references | pass | Referenced existing helpers exist; absent feature files are explicitly scheduled. Hub reconciliation covers the three named build-plan docs. |
| DR-4 Verification robustness | fail | F1 and F3/F4 give concrete incorrect-result/false-pass cases. |
| DR-5 Evidence auditability | pass | Exact commands, preserved exits and decisive verifier output are embedded below. |
| DR-6 Cross-reference integrity | partial | Main/preload schema and GUI boundaries agree; current-shot range semantics require F2. |
| DR-7 Evidence freshness | partial | static/selftest were reproduced on this worktree. Claimed plan-time product results were not rerun; runtime evidence remains unverified. |
| DR-8 Completion vs residual risk | pass | Draft remains unstarted; this review does not certify implementation or runtime completion. |

### Adversarial checks

AV-1 failing-then-passing runtime proof is **n/a at plan time**; future tests are scheduled, not observed. AV-2/AV-4: no planned assertion bypass or new skip exemption found. AV-3: **fail**, image pixels are not asserted (F1). AV-5: **n/a**, no implementation deliverable claims completion. AV-6: **partial**, sources exist but F2 conflicts with current-shot semantics.

### Executed verifier evidence

~~~json
{"schema_version":"evidence.v1","check_id":"s38-plan-static","command":"rtk proxy python docs/execution/plans/2026-10-14-capture-filmstrip-actions/plan_checks.py static","cwd":"P:/av-kit-wt/s38-capture-filmstrip-actions","scope":"plan/task/script structure","phase":"planning","exit_code":0,"result":"pass","tested_state":"unstarted Session 38 worktree observed in Round 1","output":"PASS static: 19 rows, 18 -Check names, 21 ACs covered","fresh":true}
~~~

~~~json
{"schema_version":"evidence.v1","check_id":"s38-plan-selftest","command":"rtk proxy python docs/execution/plans/2026-10-14-capture-filmstrip-actions/plan_checks.py selftest","cwd":"P:/av-kit-wt/s38-capture-filmstrip-actions","scope":"plan-local selftest","phase":"planning","exit_code":0,"result":"pass","tested_state":"unstarted Session 38 worktree observed in Round 1","output":"PASS selftest","fresh":true}
~~~

~~~json
{"schema_version":"evidence.v1","check_id":"s38-static-adversarial-trace","procedure":"Trace the image conversion and range contracts against production selection effects, then trace Vitest unhandled-error/report handling and every scope path query. Evaluate the blank-image, initial-auto-selection, known-failure-plus-unhandled-error and root-config counterexamples without running code.","observer":"gpt-6.1-sol","cwd":"P:/av-kit-wt/s38-capture-filmstrip-actions","scope":"F1-F4","phase":"planning","exit_code":null,"result":"fail","tested_state":"Round 1 files and installed dependency source read directly","output":"Blank image satisfies planned image oracles; initial Shift-click has null anchor; Vitest JSON omits separate unhandled errors; pyproject.toml and uv.lock are outside every scope query.","fresh":true}
~~~

## Commands Executed

Every repository command used the worktree as cwd. Primary process output was routed through unfiltered rtk proxy to C:/Temp/av-kit receipts, with the child exit captured immediately before receipt reads.

- rtk proxy git status --short --branch — exit 0; branch claude/s38-capture-filmstrip-actions; planning/hub changes only.
- rtk proxy git diff -- .agent/context/meu-status.yaml .agent/context/meu-registry.md docs/BUILD_PLAN.md docs/build-plan/gui-actions-index.md — exit 0; four ACTION_ROWS and the two execution_plan/date edits. No substantive rendered-file diff. Git emitted line-ending/config-access warnings; these were retained.
- rtk proxy git show da1d111 -- ui/src/renderer/src/styles.css — exit 0; isolated light accent-cyan change #0891b2 to #0e7490.
- rtk proxy python docs/execution/plans/2026-10-14-capture-filmstrip-actions/plan_checks.py static — exit 0; exact output above.
- rtk proxy python docs/execution/plans/2026-10-14-capture-filmstrip-actions/plan_checks.py selftest — exit 0; exact output above.
- Read-only rtk proxy python -X utf8 -c file/line excerpts and rtk proxy pwsh -NoProfile -Command Get-Content reads loaded the protocol, required context/template, all targets, cited canon, peer artifacts, source/tests and dependency implementation. Read-only pathlib.exists inventories established that invoked existing tools/regression files exist and absent new feature files are scheduled.
- rtk proxy rg source sweeps covered IPC/clipboard/selection/delete/census literals, installed Vitest exit/report code, Playwright key mappings and call chain, and the review schema/ledger contract identifiers.
- The exact source-audit regex read over existing target sources returned exit 1 with empty output: no matches. This was a source inspection, not execution of validate-task.ps1.
- Bootstrap/read probes had recoverable failures: rtk cannot execute PowerShell's Get-Content as a native executable (exit 1); one Python read needed UTF-8 stdout (exit 1); an initial dependency-path search named files moved into Playwright's bundle (exit 2); one read-only path-inventory regex needed PowerShell-safe backtick encoding (exit 1). Corrected reads succeeded; none supplies a product verdict.
- A lightweight memory registry search returned only unrelated historical sessions; no memory-derived project fact was used.
- Public documentation was read statically for the requested transport/keyboard questions and image semantics: Electron contextBridge/ipcRenderer/nativeImage, structured clone, UI Events and OffscreenCanvas. No application, product test, build, generator, package manager or validate-task.ps1 mode was run.

The selftest checks regex/table helpers and two baseline-message examples. Its PASS does **not** exercise vitest-red, e2e-red, floors or scope end-to-end.

## Answers to the Author

### Q1 — TEST_AMENDMENTS

**I explicitly approve TA-1, TA-2 and TA-3 as written**, independently of the overall changes_required verdict. Adding the one IMAGE_CHANNEL makes the existing 19-entry registry 20 entries. Updating both count pins, adding that channel to the test-side list, and adding its strict-schema valid/type-failure rows are minimal consequences of Spec 09:784 and the existing census contract. IMAGE_CHANNEL has a payload and correctly does not join IPC_NO_PAYLOAD. Preserve all existing extra-key/no-side-effect and registry-equality assertions; this approval covers no other expectation changes.

### Q2 — S3 and Uint8Array

**Uint8Array is the correct expected main-side type**, not Buffer or a plain object. contextBridge supports cloneable function arguments, and invoke uses structured clone; typed arrays preserve their built-in typed-array identity. The installed Electron declarations also document structured-clone invoke semantics. A main-realm Uint8Array type check plus byteLength/signature refinements is appropriate, followed by Buffer.from with the view's offset/length for nativeImage. The signature is a format precheck, not proof of a decodable image; MAIN_IMAGE_WRITE's isEmpty check supplies that. Keep the real-Electron copy test as execution evidence; no live transport was tested here. [Electron contextBridge](https://www.electronjs.org/docs/latest/api/context-bridge#parameter--error--return-type-support), [Electron invoke](https://www.electronjs.org/docs/latest/api/ipc-renderer#ipcrendererinvokechannel-args), [structured-clone types](https://developer.mozilla.org/en-US/docs/Web/API/Web_Workers_API/Structured_clone_algorithm#supported_types)

### Q3 — S5 and the real keyboard path

**MENU_OPEN is a reasonable Electron/Chromium design; AC-88.2 alone is not the real path.** Its jsdom key events verify handler logic only. Installed Playwright maps ContextMenu to virtual key 93 and F10 to 121 and sends Input.dispatchKeyEvent with modifiers (coreBundle.js:20685, :20753, :35580–35607). AC-88.12(c) must use a focused locator's press("Shift+F10"), not dispatchEvent or direct handler invocation; that exercises the Chromium/Electron input path. Extend that runtime case to press("ContextMenu") as well, since the spec names that key. FILMSTRIP_LOOK L3 additionally checks actual host keyboard delivery.

The web event model supports keydown handling and keyboard contextmenu dispatch; preventDefault plus idempotence is sensible. Host accelerator interception cannot be ruled out by static reading, so keep S5 as a measured fallback, not an assumption that either key is unavailable. [UI Events](https://www.w3.org/TR/uievents/#event-type-keydown), [keyboard contextmenu](https://developer.mozilla.org/en-US/docs/Web/API/Element/contextmenu_event)

### Q4 — D-12 and non-selected Delete

**Yes, the planned conditional SINGLE_DELETE can preserve the editor shot and unsaved marks; no unavoidable auto-select coupling was found.** Auto-select at CapturePage:281–289 runs only when selectedId is null. The destructive reset/overlay-load effect depends on selectedId and detailRevision (:388–453), not the catalog array's identity. deleteCapture invalidates the list, but deleting a different id need not change either dependency.

The crucial change is to stop applying today's unconditional setSelectedId(null) at :1001 to the non-selected target. AC-88.10 should await deletion and catalog refresh and then assert the same aria-current shot, unsaved SVG marks and dirty dot; checking only the DELETE id would be insufficient. Do not route the menu through chooseItem or increment detailRevision for this operation. The existing main IPC wrapper throws failed IpcResults (:437–443), so decode failures can also reject normally through preload; no separate result-unwrapping channel is needed.

### Q5 — BASELINE_RED versus da1d111

**The assertion exception is narrowly identified, but the overall tolerance is not yet safe because of F3.** Filename/message matching, optional occurrence and the final floor's baseline-count cap are appropriate boundaries for the one pre-existing assertion. They do not detect Vitest's separate unhandled errors.

Taking da1d111 is not required solely to implement this feature: git show confirms it is a one-line token port, but styles.css is outside this plan's file inventory. Either repair the error signal while retaining the isolated exception, or explicitly adopt that commit as a prerequisite/baseline change and require clean exits. Do not silently cherry-pick it during execution. This review did not independently reproduce the live P:/zorivest color failure or the author's earlier test receipt.

### Q6 — vitest-red / e2e-red / floors / scope

- **vitest-red:** rejects undeclared load errors, pending/todo tests and non-assertion failures, and requires a Red name for every non-Electron AC. Its new-module exceptions are file-level: a textual AC mention in a tolerated failed-load file can stand in for a collected test. That is a staging allowance, not proof that each assertion exists. With all other AC evidence held constant, a missing test in such a file can pass Red if only its AC id remains in a comment. The final floors check normally catches the absent passing AC name.
- **e2e-red:** rejects top-level errors and requires an expect-like failure for each Electron AC title, but accepts any matching assertion message. An unrelated failed fixture-readiness expect inside an AC-titled spec can pass; it also does not reject additional per-test failures once the required Red set is present. Review the failing assertion location, not just the checker exit.
- **floors:** ordinary omission of an AC with no other matching test title is caught; the negative digit lookahead distinguishes AC-88.1 from AC-88.12. Labels/counts do not prove assertions or negative cases: a combined title can name multiple ACs while an assertion checks only one behavior. F1 is the concrete missing image-content deliverable the planned passing names would not catch.
- **BASELINE_RED:** see F3. A known assertion failure must never turn an unrelated unhandled runtime failure into Green.
- **scope:** **unsound as an exhaustive scope guarantee**, F4. Named frozen roots and UI allowlisting work, but unchecked roots remain.
- **Evidence identity limit:** validate-task.ps1:217–220 records HEAD, status paths and git diff HEAD. That diff omits new untracked files' contents. Editing a new untracked clipboard helper without changing its path leaves these fields unchanged. Do not treat this hash alone as exact tested-state identity; the plan's explicit rerun-after-code-change instruction remains necessary. Hash untracked inputs too when implementing the promised identity.

These are source-traced limits, not claims that synthetic probes were run. The two permitted verifier modes do not establish the runtime soundness of these report gates.

### Q7 — behavior-test assertion Red

**Feasible, but not yet demonstrated or certifiable.** capture-filmstrip-actions.behavior.test.ts does not exist, as expected in an unstarted plan. Importing existing CapturePage/CaptureFilmstrip is sufficient to collect against baseline, following the existing jsdom/QueryClient/browser-fixture precedent. The tests must mock collaborators, not the new menu/selection behavior.

After each open gesture, use a non-throwing query followed by an explicit expect(menu).not.toBeNull() before querying/clicking missing menu items. Otherwise Testing Library's getBy/findBy lookup failure is a setup/query error that the declared assertion-only Red checker may reject. Similarly assert range attributes explicitly after Shift-click. AC-88.10 needs its actual non-selected delete path after the menu is present; a failure at "menu exists" alone does not independently demonstrate its post-delete preservation assertion. Future Red evidence must identify the assertion and collect every intended case. No import-failure exemption should be added for this behavior file.

## Verdict

**changes_required** — F1–F4 are evidence-backed delivery/control defects. Correct image-content verification and initial range semantics, preserve unrelated Vitest failures, and enforce the full registered scope before execution. F5 is a non-blocking ordering correction worth making with the same plan correction. TA-1–TA-3 are approved.

The clipboard transport and non-selected-delete design are viable. No new product scope or additional irreversible action is requested. Runtime success, complete assertion Red and the prior baseline failure remain unobserved in this static review.

## Follow-up Actions

1. Apply /plan-corrections for F1–F4; address F5 in the same correction.
2. Update the affected ACs/tasks/scripts together. Add the pixel and initial-auto-selection cases, and negative fixtures for error and scope controls.
3. Preserve this Round 1 report. For Round 2, supply the protocol's complete blast-radius census receipt with per-hit dispositions.
4. Redispatch independent plan review. Do not begin implementation or take da1d111 implicitly.
5. Dispatcher copies this report verbatim to .agent/context/handoffs/2026-10-14-capture-filmstrip-actions-plan-critical-review.md.

**Receipt report:** C:/Temp/av-kit/dispatch/s38-plan-review-report.md


---

## Corrections Applied — 2026-10-14 (Claude Code, after Round 1)

> Author's corrections, not a review verdict. The verdict is `corrections_applied`; only the next independent pass may approve.

**Ledger note.** The ledger did not record this round. The verdict JSON gave `target_plan` repo-relative, the ledger resolves relative paths against `P:/av-kit` (the wrapper's root), and the loop was opened with the worktree's absolute path: `target-plan-mismatch`, `verdict-not-recorded`, 0/3 rounds used. The review content above is unaffected and is the basis for these corrections.

| # | Verified? | Correction | Files |
|---|---|---|---|
| F1 | Yes. `RENDERER_PNG` never drew the bitmap, and no oracle checked pixels. | `RENDERER_PNG` now has `drawImage(bitmap, 0, 0)` before `convertToBlob`. A new `SHOT_PIXELS` contract defines 8×6 red/blue fixtures, built in the run (PNG via `nativeImage` in main, WebP via `OffscreenCanvas` in the renderer), and samples the clipboard's `toBitmap()` at (1,3) and (6,3). AC-88.12(b) requires it. A new negative (f) writes a transparent same-size image first and requires the oracle to reject it. | implementation-plan.md |
| F2 | Yes. `CapturePage.tsx:281-289` sets `selectedId` without `chooseItem`, so `anchorId` stayed null. | `RANGE`: if `anchorId` is null, Shift+click anchors on the editor's current shot (whether auto-selected or chosen after the anchor's removal). It is a plain click only when both are null. AC-89.2 adds the no-click and anchor-removed cases. AC-89.9 now starts from auto-selection with no prior click. D-15 `chosen` and its User Review summary are updated. | implementation-plan.md |
| F3 | Yes. The Vitest 3.2.7 JSON reporter drops unhandled errors; the default reporter prints the `Unhandled Errors` banner and the `Errors  N error` summary. | Every Vitest run adds `--reporter=default`. `vitest`, `vitest-red` and `floors` take the text receipt and fail on `UNHANDLED`. This applies before the BASELINE_RED tolerance. The selftest now has the known failure plus an unhandled rejection, and it is caught. The `BASELINE_RED` row states the limit. No `Unhandled Error(s)/Rejection` string occurs in `ui/` outside `node_modules`, so the signal has no false-positive source. | plan_checks.py, validate-task.ps1, implementation-plan.md |
| F4 | Yes. `pyproject.toml` and `uv.lock` were invisible to every query. | `scope` now inventories every changed path since `baseline.sha`, untracked files included. Each path must be a Files Modified row or a closeout output: the plan dir, the session's handoffs and reflection, or the rendered `meu-registry.md`, `known-issues.md` or `known-issues-archive.md`. A pure `scope_violations` has selftest negatives for `pyproject.toml`, `uv.lock`, an unlisted test, a frozen path, a fifth main file and another session's handoff. `PRODUCT_SCOPE`, §6, the skip basis and H1-4 are updated. | plan_checks.py, implementation-plan.md, task.md |
| F5 | Yes. `ui/tsconfig.json` includes the tests. | `green88-main` drops the whole-project typecheck; `gate88` (row 5) typechecks. The task.md row-3 note says so. | validate-task.ps1, task.md |
| Q3 | Taken | AC-88.12(c) sends Shift+F10 **and** ContextMenu via `locator.press` (the Chromium input path), not `dispatchEvent`. | implementation-plan.md |
| Q4 | Taken | AC-88.10's negative now asserts the same `aria-current`, the drawn marks and the dirty dot after the DELETE settles and the refetch resolves. | implementation-plan.md |
| Q6 identity | Taken | The gate records a SHA-256 of each uncommitted product file's working-tree content, untracked files included, instead of a hash of `git diff HEAD`. The Validation stage text is updated. | validate-task.ps1, implementation-plan.md |
| Q7 | Taken | The behavior test's Files Modified row requires `queryBy*` plus `expect(menu).not.toBeNull()` before item use, and explicit range-attribute assertions. | implementation-plan.md |

**TA-1 to TA-3** were approved by the reviewer and are unchanged.

**Blast-radius census** (receipt `C:/Temp/av-kit/s38-census-r1.txt`, read in full; rg `-F`, both files): 10 values changed. The variants swept cover the encode chain, anchor/plain-click/auto-select, BASELINE_RED/reporter/Unhandled, scope/pyproject/skip basis, typecheck/green88-main, Shift+F10/ContextMenu/dispatchEvent, dirty dot, `git diff HEAD`/SHA-256, and SHOT_PIXELS/getSize/readImage. 35 variants in 36 sweeps: `-Check scope` errored (rc 2, read as a flag) and was re-run with `-e`. There were 95 hits at 58 unique file:line sites. 17 sites are updated: plan `:106 :120 :129 :130 :146 :160 :188 :190 :226 :246 :253 :361 :369 :482 :555` and task `:49 :76`. Three of them were surfaced only by the census: the D-15 User Review summary (`:106`), the Validation-stage identity paragraph (`:555`) and H1-4 (task `:49`). The other 41 are confirmed consistent; for example, `unchanged` hits are API-route/`deleteCapture` reuse statements, and the `may fail` hit in task row 2 is the S4 missing-module allowance.

**Verification:** `plan_checks.py static` gives PASS (19 rows, 18 -Check names, 21 ACs). `plan_checks.py selftest` gives PASS, now including the F3/F4 negatives. `lint_task_contract.py` returns OK (19 rows). `validate-task.ps1` parses. Codex wrote nothing in either checkout (git status was compared before and after; the main checkout's one change is Session 31's own commit `d0fff4e`).


---

## Recheck (2026-10-14) — second review pass, ledger round 1

**Workflow:** /plan-critical-review. **Agent:** gpt-6.1-sol (OpenAI), independent of the Anthropic author. **Current verdict: approved.** One Medium non-blocking finding; no High or Critical finding. The first pass was not recorded by the ledger. This is ledger round 1, not round 2. The historical report and author's Corrections Applied section above are preserved verbatim; this section supersedes their review status.

### Intent Anchor

> Session 38 delivers MEU-88 (a thumbnail menu with Copy full path, Copy image and Delete) and MEU-89 (Shift-click range selection with one batch Delete), changing only `ui/` and three hub docs, with one new main-process IPC channel for the image clipboard.

Executing the corrected plan delivers this intent. **Intent achieved: yes** means the plan is sufficient to proceed through its execution gates, not that the unstarted feature has already been implemented.

### Scope

All repository reads and commands used **P:/av-kit-wt/s38-capture-filmstrip-actions** as cwd or absolute worktree paths. The separate P:/av-kit checkout supplied no plan, product or test evidence.

Reviewed implementation-plan.md, task.md, plan_checks.py and validate-task.ps1 in the target plan directory; the plan-time gui-actions-index.md and meu-status.yaml diff; the canonical menu/multi-select/HelpCard/IPC sections; Session 38 grouping and D-1–D-7; both issue records; Session 30 peer plan, scripts and approved rolling review. Traced CaptureFilmstrip, CapturePage, capture-commands, catalog/image/help helpers, main IPC/preload/index and capture-picker. Sampled the specified unit/Electron tests and installed Vitest/Playwright source.

The plan is unstarted: all 19 task rows remain unchecked; scheduled new source/tests and both MEU handoffs are absent. Initial status shows only the planning, index and SSOT/rendered paths. No project tests, builds, package managers, generators, validate-task.ps1 modes or other project validators were run. The only executed plan verifier modes were the two explicitly permitted below.

### Prior Findings Recheck

References below are relative to the worktree; plan-local basenames mean docs/execution/plans/2026-10-14-capture-filmstrip-actions/.

| Finding | Result | Current evidence and reasoning |
|---|---|---|
| F1 — non-PNG pixels / blank clipboard image | **fixed** | implementation-plan.md:129 explicitly draws the bitmap before PNG encoding; :130 defines opaque red/blue pixel samples and alpha; :190 requires both formats to pass the oracle and first seeds a transparent same-size clipboard image that must fail it. Blank, swapped-color and arbitrary different sampled pixels now fail. AC-88.5 (:183) separately checks the target's encoded image URL and passed bytes. |
| F2 — initial Shift-click anchor | **fixed** | implementation-plan.md:146 uses selectedId when anchorId is null, including auto-selection and recovery after anchor deletion. :246 covers no-click and removed-anchor cases; :253 starts the Electron case without a priming click. :149 and :247 keep pending range/selection behind the existing dirty confirm and leave them unchanged on Cancel. |
| F3 — unhandled Vitest errors hidden by BASELINE_RED | **fixed** | plan_checks.py:69-90 strips ANSI, detects the installed reporter's unhandled-error banner/summary and fails closed on a missing receipt; :153-155, :175-177 and :305-307 reject it before applying the tolerance. validate-task.ps1:85,100,121,242,259-261,273 add the default reporter and pass the actual text receipt in targeted, Red, full-gate and floors calls. selftest :613-617 supplies the unhandled-rejection negative. Installed Vitest cli-api.DVe0nWUx.js:5581-5592 prints the matching banner and error type. |
| F4 — root files invisible to scope | **fixed** | plan_checks.py:456-460 now inventories repository-wide baseline diff and porcelain status including untracked files; :470-494 applies the explicit allowlist/frozen/main rules to that whole set. :618-625 checks pyproject.toml, uv.lock, an unlisted test, a frozen source, a fifth main file and another session's handoff. implementation-plan.md:120,361,369 and task.md:49 agree. |
| F5 — main-only Green prematurely typechecks renderer tests | **fixed** | validate-task.ps1:190-194 runs only main/census Vitest files; whole-project types run in gate88 through :138. task.md:76 states this sequencing explicitly. No placeholder renderer module is needed. |

These are plan-level corrections verified by source inspection. The selftest exercises helper predicates; it is not an end-to-end run of Vitest, Playwright or the gates.

### Findings

| # | Severity | Blocking | Kind | Finding | File:Line | Recommendation | Status |
|---|---|---|---|---|---|---|---|
| F6 | Medium (confidence: High) | no | behavior; subject: committable-tooling | review_check rejects the absolute target_plan required by this worktree dispatch because TARGET_PLAN is relative and the checker compares the strings directly. This is a false rejection of a valid review, not a false approval of missing product behavior. | plan_checks.py:40,583-584; task.md:52 | Resolve both target paths against the worktree root before comparing them, while continuing to reject a target in another checkout. Correct this during execution preparation; it does not require another plan-review round. | open |

F6 has a concrete effect on the check result, but cannot certify missing behavior or defeat the approval gate: it fails closed. Under the workflow's materiality gate it does not justify another review round or withholding product-plan approval.

### Checklist Results

Manual observations were made by **gpt-6.1-sol**, with null exit codes; a successful file read is not represented as a product test pass.

| Check | Result | Evidence |
|---|---|---|
| PR-1 Plan/task alignment | pass | MEU-88 precedes MEU-89; the corrected main-only Green and later full typecheck match task rows 3–5. |
| PR-2 Not-started confirmation | pass | All 19 rows unchecked; no new feature files or implementation handoffs; git status has no ui changes. |
| PR-3 Task contract completeness | pass | 19 rows supply owners, deliverables, commands, dependency/context metadata and status; static reproduced the count. |
| PR-4 Validation realism | pass | Existing tools/regression paths are present; absent new paths are explicitly scheduled. Product gates are traceable. F6 is a non-blocking false rejection, and Red reports retain the limits explained in Q6. |
| PR-5 Source-backed planning | pass | ACs trace to 09, local production/peer canon or logged research/decisions. The current-shot anchor now agrees with 09:796. |
| PR-6 Handoff/corrections readiness | pass | Both MEU handoffs are named. The full census has 95 hits at 58 unique file:line sites, independently recounted. The log identifies 17 updated sites and explicitly marks the other 41 confirmed-consistent; this gives every inventoried site an unambiguous disposition by set complement. The failed flag-like search is retained and successfully repeated with -e. No truncation found. |
| PR-7 Scope discipline | pass | The Out of Scope table is substantively grounded in the registered three-item/Shift-click scope and canon; no required work is disguised as a deferral. F4's former root-config blind spot is closed. |
| PR-8 Reachability and negative oracles | pass | Renderer gesture → real page/helper → preload → allowlisted strict IPC → main nativeImage/clipboard has named observers and negative cases. Deletion reaches the existing API command; batch sequencing, failure continuation and one invalidation have behavior assertions. |
| PR-9 Single-statement discipline | pass | Named contracts govern thresholds/sets; the literal sweep found no competing material behavior. BASELINE_RED explicitly qualifies COUNT_FLOORS' otherwise-zero failure statement. |
| DR-1 Claim-to-state match | pass | Diff adds exactly four ACTION_ROWS after capture:delete and execution_plan/date changes for MEU-88/89; rendered files have no substantive diff. |
| DR-2 Residual terminology | n/a | No rename/migration. |
| DR-3 Downstream references | pass | Scheduled new files, three hub updates and existing helper paths are accounted for. |
| DR-4 Verification robustness | pass | F1–F4's concrete counterexamples are addressed. Report parsing alone does not prove assertion semantics; Q6 records that limit. |
| DR-5 Evidence auditability | pass | Exact commands, cwd, exits and decisive permitted verifier output appear below. |
| DR-6 Architectural consistency | pass | Clipboard privilege stays in main through preload; no new backend/MCP channel or filesystem-read permission is introduced. |
| DR-7 Evidence freshness | pass | Both permitted verifier results were reproduced against the corrected worktree. No earlier product-suite result is promoted to current runtime evidence. |
| DR-8 Completion versus residual risk | pass | Approval concerns the plan. Implementation and runtime verification remain unstarted and subject to Mat's execution authorization. |

**AV checklist:** AV-1 n/a (future runtime Red/Green is scheduled, not observed); AV-2 pass (no prescribed assertion bypass); AV-3 pass at design level (explicit content/selection/side-effect observers); AV-4 pass (no new skip/only allowance); AV-5 n/a (no completed implementation claimed); AV-6 pass (source-backed criteria).

~~~json
{"schema_version":"evidence.v1","check_id":"s38-second-pass-static","command":"rtk proxy python docs/execution/plans/2026-10-14-capture-filmstrip-actions/plan_checks.py static","cwd":"P:/av-kit-wt/s38-capture-filmstrip-actions","scope":"corrected plan/task/script structure","phase":"planning","exit_code":0,"result":"pass","tested_state":"unstarted corrected Session 38 worktree, second pass / ledger round 1","output":"PASS static: 19 rows, 18 -Check names, 21 ACs covered","fresh":true}
~~~

~~~json
{"schema_version":"evidence.v1","check_id":"s38-second-pass-selftest","command":"rtk proxy python docs/execution/plans/2026-10-14-capture-filmstrip-actions/plan_checks.py selftest","cwd":"P:/av-kit-wt/s38-capture-filmstrip-actions","scope":"read-only plan-local helper selftest","phase":"planning","exit_code":0,"result":"pass","tested_state":"unstarted corrected Session 38 worktree, second pass / ledger round 1","output":"PASS selftest","fresh":true}
~~~

~~~json
{"schema_version":"evidence.v1","check_id":"s38-second-pass-static-trace","procedure":"Read the complete correction census and log, then trace F1-F5 through the corrected contracts, helper predicates, PowerShell argument wiring and existing selection/delete/IPC code. Inspect baseline counterexamples without executing product code.","observer":"gpt-6.1-sol","cwd":"P:/av-kit-wt/s38-capture-filmstrip-actions","scope":"PR/DR and prior-finding recheck","phase":"planning","exit_code":null,"result":"pass","tested_state":"corrected files read directly in the Session 38 worktree","output":"95 census hits / 58 sites match the correction log; F1-F5 fixed at plan level. One non-blocking review-check target-normalization defect remains (F6).","fresh":true}
~~~

### Answers to Q1–Q7

**Q1 — TA-1 to TA-3: explicitly approved.** Each is a minimal, source-backed consequence of IMAGE_CHANNEL and Spec 09:784-786. The strict-census pin at ipc-strict-census.test.ts:52 and both login-item pins at login-item-ipc.test.ts:50-51 must become 20. The test-side channel list and valid/type-failure tables gain the same payload-bearing channel; IPC_NO_PAYLOAD stays unchanged. Existing equality, extra-key and no-side-effect assertions remain intact. This approval covers no other expectation change.

**Q2 — S3: expect Uint8Array.** contextBridge supports cloneable function arguments; invoke uses structured clone. A built-in typed-array view is reconstructed as the corresponding typed array in the destination realm, so main should receive Uint8Array, not a plain object or a required Node Buffer. The strict type, nonempty/byte cap and PNG signature refinements are appropriate. MAIN_IMAGE_WRITE then constructs the Buffer with the view's byteOffset/byteLength and rejects an empty decode; signature alone is not proof of a decodable PNG. AC-88.12 supplies the real transport test during execution. [Electron contextBridge supported types](https://www.electronjs.org/docs/latest/api/context-bridge#parameter--error--return-type-support), [Electron invoke](https://www.electronjs.org/docs/latest/api/ipc-renderer#ipcrendererinvokechannel-args), [HTML structured cloning](https://html.spec.whatwg.org/multipage/structured-data.html#structuredserializeinternal).

**Q3 — S5: MENU_OPEN is viable; the real-input proof is AC-88.12(c).** ContextMenu is the standardized key value; Shift+F10 supplies F10 with Shift held. The installed Playwright bundle maps ContextMenu to keyCode 93 (:20753) and dispatches Chromium Input.dispatchKeyEvent with key/code/modifiers (:35580-35608). AC-88.2 by itself is jsdom behavior coverage and cannot prove Electron input routing. The corrected :190 explicitly sends both gestures with locator.press against built Electron, asserts first-item focus and Escape restoration, and avoids DOM dispatchEvent. That checks the Chromium input path; Mat's FILMSTRIP_LOOK checks physical-host delivery. Host interception is not disproved by this static review, so retain S5. [UI Events key values](https://w3c.github.io/uievents-key/#keys-ui).

**Q4 — D-12: no hidden reset coupling found.** CapturePage's auto-select effect (:281-289) returns while selectedId is non-null. Its draft/detail-loading effect resets marks only when selectedId or detailRevision changes (:388-453). A catalog refetch after deleting another id does not inherently change either. The key implementation change is to avoid today's unconditional setSelectedId(null) at :1001 for the non-selected target, and not route menu opening through chooseItem. SINGLE_DELETE requires that. AC-88.10 now waits for the DELETE and catalog refetch and checks the same aria-current thumb, unsaved SVG marks and dirty dot (:188), covering the consequential state rather than only the request id.

**Q5 — BASELINE_RED: the corrected exception is sufficiently narrow for this scope; taking da1d111 is not required.** The checker matches queue-canon.test.ts, AC-41.3 and its specific light-accent-cyan diagnostic, does not require that failure, and the full floors cap does not permit growth beyond the recorded baseline count (:93-95,324-328). F3's unhandled-error bypass is now closed before the tolerance. Source inspection confirms the external-token assertion at queue-canon.test.ts:159-180, and git show da1d111 confirms the isolated #0891b2 → #0e7490 port. This review did not rerun the failure or read the live Zorivest stylesheet. If Session 31 merges before baseline capture, rebase as planned; otherwise keep the declared exception rather than silently broadening scope. It is an explicit allowed baseline assertion, not a claim of a zero-failure raw suite.

**Q6 — the controls are useful and their material prior defects are fixed; they are not semantic test provers.**

- vitest-red (:173-222) rejects unhandled errors, undeclared collection failures, pending/todo tests and unrecognized failed assertions, then requires each non-Electron AC to be represented. A declared failed-load new-module file can satisfy coverage through an AC text mention; this staging allowance cannot establish that the assertion exists. The behavior file has no such exemption.
- e2e-red (:264-280) requires each Electron AC title to have an unexpected expect-like failure and rejects top-level errors. An unrelated fixture-readiness expect inside an AC-titled spec can satisfy that shape; additional per-test failures are not exhaustively classified. Thus a Red can pass for the wrong reason. Inspect decisive failing assertion locations in the mandated durable Red receipts; the checker exit alone is insufficient.
- floors (:302-339) catches ordinarily missing passing AC names, distinguishes AC-88.1 from AC-88.12, preserves baseline counts and skipped limits, and now rejects the unhandled-error receipt. A combined/misleading title can still name an AC whose behavior is never asserted. This known label-based limit is recorded once, not escalated into another predicate-hardening round.
- scope (:456-494) now sees all tracked differences and untracked paths and rejects an unlisted path. Root pyproject.toml/uv.lock and an unlisted source/test cannot pass through the former omission. Its explicit planning/closeout allowances are intentional.
- Full-gate Vitest wiring is consistent: --reporter=default plus JSON, the matching text receipt added through @extra at validate-task.ps1:259-260, and that same text receipt passed to floors at :273. Per-file hashes also include untracked product files (:220-231).

**Q7 — assertion Red is feasible as specified, but not yet demonstrated.** The new behavior test does not exist at plan time. Existing CapturePage/CaptureFilmstrip imports can collect against baseline, following capture-page.behavior.test.ts's QueryClient/API/browser-fixture precedent. The corrected Files Modified row (:221) requires queryBy* followed by expect(menu).not.toBeNull() before using an item, and explicit range-attribute assertions. Baseline lacks menu/range behavior, so these assertions can fail without a missing-import exemption. Their later path/copy/delete/preservation assertions must still be present and reach the actual behavior after implementation; failing only at “menu exists” does not independently prove each downstream clause. No static review can certify future tests as already Red/Green.

**Pixel-oracle limit:** the PNG and WebP fixtures intentionally share the same red/blue pattern. SHOT_PIXELS rejects blank and incorrect sampled content; it does not distinguish two different shots that happen to have identical pixels. AC-88.5's target-request and byte assertions supply that separate targeting proof. No claim is made that two sampled pixels certify every pixel in an arbitrary image.

### Commands Executed

All repository commands used the worktree cwd. RTK proxy output was redirected under C:/Temp/av-kit, with native exits preserved before reads.

| Command / observation | Exit | Decisive result |
|---|---|---|
| rtk proxy git status --short --branch | 0 | claude/s38-capture-filmstrip-actions; planning/hub/SSOT files only, no ui changes. |
| rtk proxy git diff -- .agent/context/meu-status.yaml .agent/context/meu-registry.md docs/BUILD_PLAN.md docs/build-plan/gui-actions-index.md | 0 | Four index rows; two execution_plan/date edits; no substantive rendered diff. |
| rtk proxy git show da1d111 -- ui/src/renderer/src/styles.css | 0 | Isolated one-line light accent-cyan port. |
| rtk proxy python docs/execution/plans/2026-10-14-capture-filmstrip-actions/plan_checks.py static | 0 | PASS static: 19 rows, 18 -Check names, 21 ACs covered |
| rtk proxy python docs/execution/plans/2026-10-14-capture-filmstrip-actions/plan_checks.py selftest | 0 | PASS selftest |
| rtk proxy pwsh -NoProfile -Command file/line reads, Test-Path inventory and completed-receipt census count | 0 | Existing invoked helpers/regression paths present; scheduled new files/handoffs absent; 95 hits / 58 unique sites. |
| rtk proxy rg -n source/contract sweeps and literal census | 0 on successful sweeps | Current channel pins, predicates, installed reporter output, keyboard map and Chromium dispatch traced. |

Recoverable read-command diagnostics were retained: one nested PowerShell quoting attempt failed before reading anything (exit 1); initial Playwright unbundled-path searches returned exit 2 and were corrected to the installed coreBundle.js; a bundled-source search produced oversized console output, so bounded source excerpts were read separately. Git's config-access and line-ending warnings remain in receipts. None is product-test evidence. A lightweight memory-registry search supplied no project fact used in this verdict. Public primary documentation was read statically for transport and keyboard semantics.

### Verdict and Follow-up Actions

**approved** — F1–F5 are fixed at plan level, and the plan delivers the registered menu, clipboard and batch-selection intent with the prescribed UI/hub scope. **TA-1, TA-2 and TA-3 are explicitly approved.** F6 is non-blocking and does not justify another review round.

1. Dispatcher copies this complete rolling report verbatim to the canonical worktree review path. Record this as ledger round 1 using the absolute target_plan in the frontmatter/JSON.
2. Normalize review-check target paths as described in F6 during execution preparation, preserving rejection of a different checkout.
3. Execution remains subject to Mat's existing human gate. Produce actual assertion Red/Green, real Electron transport/keyboard/pixel/delete evidence, the full scoped gate and FILMSTRIP_LOOK as planned; this review ran none of them.

**Receipt report:** C:/Temp/av-kit/dispatch/s38-plan-review-report.md


---

## Corrections Applied — 2026-10-14 (post-approval, F6)

Author: Claude Code (Opus 5.5). This section does not change the approved verdict above.

| Finding | Correction | Evidence |
|---|---|---|
| F6 (Medium, non-blocking) | `plan_checks.py` now has a pure `same_target(value, root)`. It resolves a repo-relative `target_plan` against the cwd checkout, then normalizes and case-folds both sides before comparing. `review_check` uses it. A plan path in another checkout (for example `P:/av-kit/...`) still fails. Selftest adds 4 cases: relative passes, absolute worktree path passes, `P:/av-kit` path fails, empty fails. | `python plan_checks.py selftest` → PASS selftest (rc 0). `static` → PASS: 19 rows, 18 -Check names, 21 ACs (rc 0). `review-check <this file> plan 3` → PASS plan review approved, round 1, agent gpt-6.1-sol (rc 0). |
