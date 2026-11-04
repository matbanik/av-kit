---
date: "2026-10-15"
review_mode: plan
target_plan: P:/av-kit-wt/s34-capture-chrome/docs/execution/plans/2026-10-14-capture-chrome/implementation-plan.md
verdict: approved
findings_count: 0
round: 3
template_version: "2.2"
requested_verbosity: standard
agent: gpt-6.1-sol
---

# Critical Review: 2026-10-14-capture-chrome

> **Review Mode:** plan. **Verdict:** changes_required.
> **Loop:** s34-plan-2026-10-14-capture-chrome, ledger round 1, second attempt.
> **Reviewer:** gpt-6.1-sol, Codex/OpenAI, independent of the Claude Code/Anthropic author. No Critical findings.

## Intent Anchor

> Session 34 ships MEU-80 (a themed, accessible hint on every icon-only function button, with the native-tooltip root cause probed) and MEU-81 (the Capture actions as icons with Delete red at the far right, Sample and the nudge pad removed, keyboard endpoint nudge, an unsqueezed marks row and the hotkey status inline in the header), resolving the five triaged Capture chrome issues.

**Intent achieved: partial.** The icon/action/layout design substantially addresses the five issues. Accessibility integration and demonstrated missing-deliverable false passes prevent approval. These are findings about an unstarted plan, not runtime implementation results.

## Scope

**Target:** implementation-plan.md, task.md, validate-task.ps1 and plan_checks.py in docs/execution/plans/2026-10-14-capture-chrome/. Their unqualified filenames below refer to that folder. Every repository path is relative to **P:/av-kit-wt/s34-capture-chrome**, branch claude/s34-capture-chrome.

**Review type:** /plan-critical-review, PR-1–PR-9, DR-1–DR-8 and adversarial checks. Read the protocol first, then AGENTS/GUARDRAILS/PROJECT-PROFILE and REVIEW-TEMPLATE v2.2. Sampled Session 30's approved peer plan/review and A-6/A-10, grouping, issue SSOT/triage decisions, build-plan 09/06, source inventory, keyboard paths, amended tests, fixture, registry and runner configuration.

**Observed readiness:** HEAD 78610200ea2e7efd52318ea95c3e48b6df4993ba. Git status shows only the four untracked target files, with no tracked product changes. All 21 task rows are unchecked. MEU-65/67 are approved; MEU-80/81 pending. Both new MEU handoffs are absent. Missing new primitive/test/probe files are scheduled creations; existing modify/delete targets and invoked repository tools/configs exist.

**Boundary:** static reads/searches only, plus the expressly allowed read-only static verifier. No tests/builds/installs/generators/dotnet/validate-task.ps1 cases or mutation probes ran. No repository files were written. The sole report deliverable is C:/Temp/av-kit/dispatch/s34-plan-review-report.md; the dispatcher copies it verbatim to the canonical rolling review.

## Findings

| # | Severity | Blocking | Kind | Finding | File:Line | Recommendation | Status |
|---|----------|----------|------|---------|-----------|----------------|--------|
| F1 | High | yes | behavior | **deliverable; confidence High.** TOOLTIP replaces aria-describedby with its hint ID and removes the attribute when hidden. QueueCard already supplies DndDescribedBy-0 through drag.attributes, so this contract removes keyboard-drag instructions and contradicts the unchanged drag accessibility assertion. TA-25 and the census miss that contradiction. Violates AC-80. | implementation-plan.md:127; implementation-plan.md:184; ui/src/renderer/src/components/queue/QueueCard.tsx:516; ui/tests/unit/queue-card.test.ts:1261; validate-task.ps1:179 | Compose the hint ID with existing description tokens and remove only that ID on hide. Preserve child refs and handlers. Add existing-description show/hide regression coverage and census the accessibility relationships; retain the drag-instruction invariant. | open |
| F2 | High | yes | behavior | **deliverable; confidence High.** NUDGE_TARGET makes SVG circles focusable but retains annotationOwnsFocus(), which rejects non-HTMLElement focus, and leaves their SVG ancestor aria-hidden. The proposed focused-endpoint path therefore cannot work accessibly. The reset contract also omits surface-focus reset required by AC-81.6. Violates AC-81. | implementation-plan.md:138; implementation-plan.md:284; ui/src/renderer/src/features/capture/CapturePage.tsx:102; ui/src/renderer/src/features/capture/CaptureViewport.tsx:1147 | Specify SVG-aware focus ownership, expose the interactive handles to accessibility APIs, and reset the target on surface focus. Add real Electron Tab/arrow coverage and explicit input, filmstrip and confirmation negatives while preserving single event ownership and nudge history. | open |
| F3 | High | yes | control-defeat | **committable-tooling; confidence High.** mechanism: task-row-completion-predicate. Red accepts one tagged assertion failure; Green/final gates accept aggregate counts without checking the required AC cases. Omitting AC-80.3 entirely can pass these checks while other new tests satisfy the old floors. Handoff coverage collapses dotted AC IDs to MEU prefixes. Vitest also tolerates arbitrary failures in any TA file without checking their approved disposition. Violates AC-80. | plan_checks.py:411; plan_checks.py:447; plan_checks.py:463; plan_checks.py:485; plan_checks.py:497; tools/validate_closeout_artifacts.py:74 | Bind expected AC case IDs/files to collected Red and Green results, with explicit intended-Red versus baseline-pass classifications. Require all applicable cases, reject skipped required Electron cases, and bind tolerated failures to specific approved amendments and census dispositions. Keep aggregate floors supplementary. | open |
| F4 | High | yes | control-defeat | **committable-tooling; confidence High.** mechanism: task-row-completion-predicate. root-cause accepts H1-H3/finding text and three fresh nonempty files named .png. Three one-byte files plus H1/H2/H3: tooltip-visible no — x and finding: not found satisfy the predicate without running Electron or inspecting either target. Row 2's validation calls this evaluator without requiring evidence from the probe producer. Violates AC-80. | plan_checks.py:577; validate-task.ps1:185; validate-task.ps1:195; task.md:37 | Require successful probe-run evidence bound to the baseline/build and observations for both targets under every hypothesis. Retain valid screenshots and actual inspection outcomes. Add a negative oracle rejecting placeholders and absent probe-run evidence. | open |
| F5 | High | yes | control-defeat | **committable-tooling; confidence High.** mechanism: task-row-completion-predicate. scope ignores native/ because it belongs to neither FROZEN nor PRODUCT_PREFIXES. A change to native/region-picker/Program.cs or native/region-picker-stub/Program.cs passes as zero changed product files despite PRODUCT_SCOPE. These sources and consumed doc inputs also fall outside identity, so gate-check can accept stale evidence. Violates AC-81. | plan_checks.py:53; plan_checks.py:59; plan_checks.py:304; plan_checks.py:384; implementation-plan.md:125 | Classify the complete product surface, including native/, and reject every unlisted product change. Hash consumed native/build/doc inputs or enforce their baseline equality, accounting explicitly for administrative transitions. Include an unlisted native-source change as the scope negative case. | open |
| F6 | Medium | no | behavior | **deliverable; confidence High.** HINT_TITLE_RULE coverage omits action-button title absence and wrapper DOM attributes. AC-80.8/80.9 cover toolbar/non-Capture controls; AC-81.2 does not check title. The AC-80.7 literal source guard can miss a wrapper title introduced by a spread. | implementation-plan.md:151; implementation-plan.md:219; implementation-plan.md:223; implementation-plan.md:280 | Assert title absence on actual controls and wrappers across the complete inventory, including mounted action buttons and enabled/disabled states. Keep legitimate labelled-control titles outside the assertion. | open |

### Material evidence and vocabulary mapping

The refused attempt was working notes only. Each finding above was rechecked against the current files. No prior verdict was treated as ledger state; this remains round 1.

**F1 — behavior; no mechanism.** The new contract explicitly requires describedby equality to the hint ID while shown and absence while hidden (plan:127,216–219). QueueCard passes dnd-kit attributes/listeners/ref to the actual Button (QueueCard.tsx:507–517); queue-card.test.ts:1212,1261 pins the drag instruction relationship. This is a concrete accessibility regression in AC-80.1/80.2/80.9, also violating the existing AC-49.8 invariant. TA-25 changes geometry/structure only. The census regex has handle IDs but does not reach the standalone aria-describedby assertion. Preserve the existing ID both when shown and hidden; add/remove only the tooltip ID. This is product behavior, not a gate-defeat slug.

**F2 — behavior; no mechanism.** Follow focused circle → draw-surface onKeyDown → onEditorKey(event.nativeEvent) → CapturePage.handleEditorKey → annotationOwnsFocus. The guard at CapturePage.tsx:105 rejects SVGElement focus because it requires HTMLElement. The containing SVG is aria-hidden at CaptureViewport.tsx:1149. Adding tabindex/role/label to circles alone does not expose them accessibly. AC-81.6 also requires surface focus to restore body nudge, while NUDGE_TARGET's reset list omits it. Specify both repairs and test actual focus/keys. This is the endpoint feature's production behavior.

**F3 — control-defeat → task-row-completion-predicate.** This is the catalogued control deciding whether test-writing/Green/gate task rows can be completed, defeated by substituting aggregate counts for the required case set. Concrete static counterexample: omit AC-80.3's test entirely, retain the other new cases and their passing results, and retain another AC-80 assertion failure for Red. Static checks Markdown task ranges, not collected tests; Red requires only one qualifying failure; Green never compares collected AC cases; the old count floors can still hold because other new tests outnumber deletions. The handoff check uses AC_ID = AC-(digits), so AC-80.3 is reduced to AC-80. A tooltip without Escape/hover-transfer can lack its required test without any of these evaluators detecting the omission. e2e-ok also accepts skipped required cases if other cases pass. TA_FILES permits any failing assertion in the listed files, without reading the census disposition. A setup expect failure can qualify as Red without reaching a feature assertion. This violates the AC-80 test deliverable and AGENTS Testing/TDD, PR-4/PR-8. Counterexamples were traced, not executed.

**F4 — control-defeat → task-row-completion-predicate.** This is row 2's completion predicate accepting artifact presence instead of its required on-target probe. Retain baseline.sha, supply three newer one-byte .png files, write H1/H2/H3 lines ending “tooltip-visible no — x”, and “finding: not found”. Every condition at plan_checks.py:577–593 succeeds. None requires a successful probe invocation, valid image, build/window identity or two-target observations. The producer is planned in -Check probe, but row 2's completion command invokes only -Check root-cause; the latter reads no producer evidence. This is a materially missing AC-80.12 investigation, not a demand to automate causal judgment. Map to the same completion control as F3; do not invent unbound-probe-evidence.

**F5 — control-defeat → task-row-completion-predicate.** H1-4's scope proof controls whether the renderer-only work can be completed; its classifier silently discards an actual product path. For a diff containing native/region-picker/Program.cs only, neither frozen-root check sees it, PRODUCT_PREFIXES drops it, and the allowlist comparison accepts an empty product set. The stub's Program.cs follows the same path. Both files exist and are tracked. Native sources also escape identity despite row 0 building the stub. The gate additionally consumes unhashed documents: layout-canon.test.ts:15–19 reads its prior plan, build-plan 11, grouping, meu-status and BUILD_PLAN; gui-actions-audit.test.ts reads gui-actions-index. Changing those after a gate leaves identity unchanged. Bind actual inputs and administrative transitions. This violates PRODUCT_SCOPE, the AC-81 scoped delivery and PR-7/PR-8, rather than a review-conduct detector. It maps to the same task-completion control, not a new partial-product-path-classification slug.

**F6 — behavior; no mechanism; non-blocking.** The guard's claimed complete inventory coverage is incorrect: no AC checks the seven action controls' title attributes or every wrapper's DOM title. A spread-supplied wrapper title escapes the source literal check. This is a bounded verification correction; the primitive contract already says to remove title, so it does not independently justify withholding approval.

All three control-defeat findings deliberately share the closed vocabulary's task-row-completion-predicate. The ledger owns recurrence/cap handling; this report does not reset counts, split the mechanism into new names or promise another eligible round.

## Commands Executed

All shell calls used **P:/av-kit-wt/s34-capture-chrome** as cwd and RTK proxy. Working receipts are under C:/Temp/av-kit/dispatch/. Completed receipts were read after preserving the process exit. No command used the different P:/av-kit checkout for plan/product/test reads.

Principal exact commands inside the PowerShell all-stream receipt wrapper:

| Command | Exit | Observed result |
|---|---:|---|
| rtk proxy python docs/execution/plans/2026-10-14-capture-chrome/plan_checks.py static | 0 | PASS static: 21 task rows; 17 GATE stages; scripts, constants and cross-references agree |
| rtk proxy git status --short --untracked-files=all | 0 | Only implementation-plan.md, plan_checks.py, task.md, validate-task.ps1 untracked. User-level git ignore access warnings retained. |
| rtk proxy git log -1 --format=oneline | 0 | 78610200ea2e7efd52318ea95c3e48b6df4993ba docs(closeout): Session 30 H2 — reflection, MEU-67 approved, issues resolved |
| rtk proxy git ls-files -- native/region-picker/Program.cs native/region-picker-stub/Program.cs | 0 | Both native counterexample files tracked. |
| rtk proxy rg -n -e 'ArrowLeft\|ArrowRight\|ArrowUp\|ArrowDown\|onKeyDown\|onKeyUp' ui/src/renderer/src/features/capture | 0 | Arrow nudge belongs to CapturePage; no filmstrip arrow-navigation handler. |
| rtk proxy rg -n -A 12 -- 'id: MEU-(65\|67\|80\|81\|82\|83\|88\|89)\b' .agent/context/meu-status.yaml | 0 | Approved dependencies, pending targets, registered deferred MEUs. |

Additional observed read/search groups (each completed with exit 0 unless noted):

- **bootstrap / required / context / procedures / peer-config:** Get-Content of protocol, terminal-preflight/output policy, operating instructions/context/profile/template/vocabulary/schema, reviewer/tester roles, completion-preflight and latest peer review. The first nested-shell bootstrap had a quoting ParserError (exit 1); retried with protected quoting and read the files successfully. An early combined status wrapper yielded no output and was not used as evidence; standalone status/log above supply the evidence.
- **plan / scripts and their bounded rereads:** numbered Get-Content of all four target files, all the way through implementation-plan:676, task:85, plan_checks:754 and validate-task:411.
- **canon / canon-slices / canon-a11y / peer-checks / deps:** rg/Get-Content of grouping, issues, D-49/51/64/69, build-plan 09/06, Session 30 plan/human decision file and count JSON. Peer floors are actually 773 Vitest, 133 Electron expected and 655 pytest.
- **keyboard / production / drag / tests-a / tests-b / inventory-inputs / final-source:** source and test reads establishing the paths and line references above, all seven non-Capture inventory sites, the action row, title expectations, sampling/nudge/header amendments, QueueCard snapshot/drag tests, registry/hash test, doc-reading test inputs and runner configuration.
- **existence-schema:** Test-Path of every Files Modified entry, handoffs and invoked tools/configs. Only scheduled new files/handoffs are absent. Read the exact v2 schema.
- **Memory:** a narrow MEMORY.md search was performed as required by host instructions. No historical memory fact was used in the verdict.
- **External read-only primary sources:** W3C APG tooltip, WCAG SC 1.4.13 Understanding, WAI-ARIA 1.2 and Microsoft RegisterHotKey documentation. No product runtime action.
- **Closeout:** report readback confirmed the required frontmatter, six finding rows, intent, all Q1–Q8 answers, checklist, verdict and actions. Final git status still shows only the same four untracked plan files; git diff --stat is empty (both exit 0).

The shell form was: rtk proxy <read/check> *> C:/Temp/av-kit/dispatch/<receipt>.txt; $rc=$LASTEXITCODE; Get-Content <receipt>; exit $rc. Numbered file slices used rtk proxy pwsh -NoProfile -Command with protected single-quoted child scripts.

## Checklist Results

Manual observer throughout: **gpt-6.1-sol**. Manual checks have null exit; they are file/predicate observations, not executed product tests.

### Information Retrieval (IR)

| Check | Result | Procedure / evidence | Exit |
|---|---|---|---|
| AC source labels | pass | Read AC and decision tables against triage and 09 source rules. | null |
| Exact validation commands | partial | All named cases exist; F3–F5 prevent the claimed proof. | null |
| BUILD_PLAN audit | pass | Plan:337–357 and task row 10 cover 09/11/matrix/render reconciliation. | null |
| Post-MEU deliverables | pass | Two handoffs, H1 review, H2 reflection/metrics/status and commit draft are explicit. | null |

### Plan Review (PR)

| Check | Result | Procedure / decisive evidence | Exit |
|---|---|---|---|
| PR-1 plan/task alignment | pass | Compared work packages, dependencies and task rows: 80 precedes 81, then hub/H1/review/H2. | null |
| PR-2 unstarted | pass | Git state, 21 unchecked rows, pending MEUs and absent handoffs agree. | null |
| PR-3 task contracts | pass | Read all rows for owner, deliverable, command, dependency, status and durable outputs. Static agrees. | null |
| PR-4 validation realism | fail | F3/F4 show materially missing test/probe deliverables accepted. | null |
| PR-5 source-backed planning | pass | Human decisions match SSOT; autonomous design choices have declared provenance. | null |
| PR-6 handoff/corrections readiness | pass | Both handoffs/rolling reviews explicit. Round-2 census precondition does not apply to this unconsumed round 1. | null |
| PR-7 scope discipline | partial | Exclusions/registered deferrals are sourced; F5 defeats executable scope enforcement. | null |
| PR-8 reachability/negative oracles | fail | Traced F1/F2 production paths and F3–F5 concrete evaluator counterexamples. | null |
| PR-9 repeated literals | pass | Named sets and executable copies agree, as static confirms; no materially competing live behavior found. | null |

### Docs Review (DR)

| Check | Result | Procedure / decisive evidence | Exit |
|---|---|---|---|
| DR-1 claim/state match | pass | Draft/unstarted claim agrees with observed state. | null |
| DR-2 residual terms | pass | Sample/nudge/title mentions are intentional retirement/amendment history. | null |
| DR-3 downstream references | pass | Help, hub, test-id and canon transformations are planned. | null |
| DR-4 verification robustness | fail | F3–F5 false passes; F6 bounded title-coverage gap. | null |
| DR-5 evidence auditability | partial | Commands are exact; F4 lacks producer binding. | null |
| DR-6 canon integrity | partial | Human product decisions match canon; F1/F2 conflict with retained accessibility/focus paths. | null |
| DR-7 freshness/counts | partial | Peer floors verified by read; F5 leaves consumed inputs unhashed. | null |
| DR-8 completion/residual risk | pass | Draft and this refusal assert no completed implementation. | null |

### Adversarial / post-implementation applicability

AV-1 failing-then-passing proof: **partial**, F3; only planned tests exist. AV-2 bypass prevention: **partial**, filename-wide failure tolerance remains. AV-3 assertion coverage: **partial**, useful geometry/action assertions but missing collection binding and real SVG focus path. AV-4 skipped masking: **partial**, Vitest rejects pending/todo; required Electron skips can escape. AV-5 completed-code placeholders: **n/a**, implementation unstarted. AV-6 source-backed criteria: **pass**, decisions checked. Post-implementation evidence/FAIL_TO_PASS results: **n/a** under static-only authorization.

```json
{"schema_version":"evidence.v1","check_id":"s34-plan-static-r1-second-attempt","command":"rtk proxy python docs/execution/plans/2026-10-14-capture-chrome/plan_checks.py static","cwd":"P:/av-kit-wt/s34-capture-chrome","scope":"plan-local structure/constants/references","phase":"static","exit_code":0,"result":"pass","tested_state":"HEAD 78610200ea2e7efd52318ea95c3e48b6df4993ba plus four untracked Session 34 target files","output":"PASS static: 21 task rows; 17 GATE stages; scripts, constants and cross-references agree","fresh":true}
```

```json
{"schema_version":"evidence.v1","check_id":"s34-plan-semantics-r1-second-attempt","procedure":"Read current target contracts against QueueCard descriptions and Capture SVG focus/event paths; trace evaluator counterexamples for missing AC tests, placeholder probe images and native product changes without executing them.","observer":"gpt-6.1-sol","cwd":"P:/av-kit-wt/s34-capture-chrome","scope":"F1-F6","phase":"static","exit_code":null,"result":"fail","tested_state":"same unstarted worktree","output":"Drag instruction ID would be overwritten; SVG handle fails HTMLElement focus ownership and has an aria-hidden ancestor; omitted AC test, placeholder PNG and unlisted native-source changes evade the inspected checks.","fresh":true}
```

## Answers to Q1–Q8

**Q1 — disabled wrapper accessibility and DOM cost.** Conditional tabindex avoids two sequential tab stops on enabled native buttons: the enabled child alone is tabbable; when disabled the native button is skipped and the wrapper becomes the stop. One stable span is proportionate under the existing native-disabled design and avoids changing the child hierarchy when disabled toggles. TA-25 and fixture (a) are bounded structural consequences.

It is not fully accessible as specified: preserve description tokens (F1), and explicitly define/test what the focused disabled wrapper exposes as the control's name and unavailable state. A generic focusable span with only describedby does not establish reliable screen-reader presentation of the named disabled descendant. Also test focus behavior when disabled becomes enabled. This review did not run an AT session.

aria-disabled on the actual button gives a consistent named focus target, but does not itself suppress activation. It would require guarded keyboard/click/dnd handling, disabled styling/pointer rules and changes to .disabled/toBeDisabled semantics. Existing tests alone are not a reason to reject it; retaining native activation protection and build-plan 09:685's wrapper contract is a substantive reason to keep the bounded wrapper design. Preserve activator refs, listeners and focus restoration.

**Q2 — title removal, wording and tooltip semantics.** “Name — reason” is appropriate after visible labels disappear; removing duplicate native titles is coherent. Escape dismissal, pointer transfer, focus retention and no timeout align with the [APG tooltip pattern](https://www.w3.org/WAI/ARIA/apg/patterns/tooltip/) and [SC 1.4.13](https://www.w3.org/WAI/WCAG22/Understanding/content-on-hover-or-focus.html). APG labels this pattern work in progress. The requirements apply to the custom hint, including persistence while its trigger remains active.

Title enforcement is incomplete (F6): a stray action or wrapper title can slip through. Extend DOM checks to the complete inventory, rather than globally forbidding legitimate labelled titles. Add timing negatives for focus persistence beyond grace and dismissal cancelling pending timers. Resolve focus-wins versus singleton behavior when a second control is hovered while the first remains focused. Preserve existing description IDs per [WAI-ARIA aria-describedby](https://www.w3.org/TR/wai-aria-1.2/#aria-describedby).

**Q3 — endpoint keys and conflicts.** No, there is not an AC for every relevant focus conflict. AC-81.5/81.6 cover routing/history/reset subsets, and AC-81.7 covers live gestures, but the real SVG focus path fails (F2). Add a real Electron Tab-to-handle/arrow test, surface-focus reset, shot-change reset and explicit arrow negatives for text/colour inputs, filmstrip and confirmation focus. Keep text-draft/composition exclusions and single event ownership. Existing AC-57.7 already protects confirm-strip arrows/Delete; preserve it.

The current filmstrip selects through onClick and has no arrow-navigation handler, confirmed by Capture-scoped key census and CaptureFilmstrip.tsx read. Do not invent a shot-navigation conflict. Surface keydown stops propagation after onEditorKey, while window owns other editor keys; avoid a second handler nudging twice. Space pan currently recognizes native button tags, not SVG role=button, so define handle Space/Enter behavior deliberately.

**Q4 — F2 fixture, actual path and fallback.** Sound in principle, not yet implemented or runtime certified. [RegisterHotKey](https://learn.microsoft.com/en-us/windows/win32/api/winuser/nf-winuser-registerhotkey) returns failure when the key is already registered and associates a null-window registration with the calling thread. Print HELD only after success, keep that thread alive and put startup/timeout/launch failure paths under finally. Kill and await helper exit before the free run; close the first Electron app before the second. A message loop is needed for processing hotkey messages; this holder only needs to reserve the key.

Capture main actually computes inUse = !globalShortcut.register(...) (capture-hotkey.ts:26–39). AC-81.11 reads that IPC status and tests containment, header height and viewport top across two real launches, so it proves inline/no-shift through production behavior. S4 is acceptable as a stop for a Decision Brief; AC-81.10's unit DOM assertion is not an authorized replacement for the real AC-81.11 case.

**Q5 — root-cause probe.** Recording a found main-process fix without applying it is within renderer-only PRODUCT_SCOPE and 09:686's record-if-found rule. A real bounded probe may legitimately conclude “not found.” The evaluator cannot exclude a vacuous probe (F4). Bind the successful producer run, usable artifacts, build/target identity, both controls' observations and actual inspection result. Do not attempt to infer a cause from file freshness alone.

**Q6 — test amendments and fixture repairs.** **This verdict does not approve TEST_AMENDMENTS as a set for execution.** Most changes have a minimal, source-backed basis:

- D-49: TA-1/3/5/6/9/20 replace retired pad/inspector/text-action expectations while retaining behavior.
- D-51: TA-2/4/10/16/17/19 remove sampling, update help and use equivalent hex setup; the unrelated assertions remain.
- D-64: TA-7/18 remove the reserved band in favor of conditional inline status.
- D-50: TA-21 expands the direct overflow check.
- D-48/D-69 and disclosed D-8/9/12: TA-8/11/12/14/15/22/23/24 replace native-title/reason expectations with the shared hint; TA-13/25 accommodate the wrapper.
- TA-26 follows the eight approved retirements; registry's baseline-minus-exactly-eight-lines check appropriately constrains the hash re-pin.

**FIXTURE_REPAIRS (a) is approved as the exact narrow transformation specified**, with other keys unchanged. It does not authorize further snapshot updates or accessibility changes.

Before amendment approval, fix F1 and make TA-11 focus an enabled **button**, not its nonfocusable wrapper (plan:170 versus :127). TA-15/24 must explicitly replace the old enabled-hover “no reason label” expectations (unit:2458–2460; Electron:1588–1590) with the enabled-name hint, and wait for HINT_DELAY_MS/grace rather than retaining immediate assertions.

The existing drag describedby expectation is the missing contradiction. Preserve it; do not amend away drag instructions. Row 1 is not strong enough: its regex misses that assertion, census-check permits path:* dispositions without evaluating reasons, and Red tolerates every failure in any TA file. Require accessibility relationship/ref/listener hits and specific approved dispositions.

**Q7 — verifier soundness.** Static is useful and passed, but it proves cross-file structure, not product coverage. vitest-red/e2e-red have existential tagged-assertion tests, not required-case collection or right-feature-failure proof. They can accept a setup expect failure. TA tolerance is file-wide. Green/floors allow missing required tests (F3); Electron skips are not rejected by e2e-ok/final floors. Baseline counts are correctly sourced but are supplementary sentinels.

scope handles recognized roots, but unlisted native product changes pass (F5). identity hashes current tracked/untracked nonignored bytes under its list and detects deleted entries; it omits consumed inputs and runtime environment. gate-check compares stage order/exits/count summaries and that limited identity; it does not reconcile all raw reports independently. Receipt deletion before GATE and first-failure stopping are useful. Repair the demonstrated missing-deliverable paths; arbitrary higher floors would not repair them.

**Q8 — overflow and squeeze measurement.** Yes: the 1280×800 fixture mounts the crowded state (Save, Revert, Remove plus other actions and 12 chips), tests actual scrollWidth/clientWidth, height at least 36 px rather than the observed 28 px, vertical overflow and action containment/rightmost Delete. Text-tool and open-Options variants add vertical pressure. These measure the issue, not only class-name proxies. Internal chip-list scrolling is consistent with D-50.

Use “tip box” to mean the trigger wrapper, not the portaled hint. Ensure loaded fonts/two animation frames and completed dirty/backup/selection setup. Checking visible chips/buttons are vertically contained would strengthen the existing direct measurements; no additional layout blocker found.

## Verdict

**changes_required** — five High blocking findings (F1–F5), one Medium non-blocking finding (F6), all open. Intent achieved: **partial**.

The requested icon map/order, source-backed removal scope, hotkey production path and direct geometry assertions are substantially sound. The accessibility contracts and demonstrated validation false passes prevent approval. No runtime product-suite pass, live screen-reader output or successful helper cleanup is asserted.

## Follow-up Actions

1. Correct F1–F5 through /plan-corrections; address F6 and the bounded TA-11/15/24 notes in the same change.
2. Preserve drag instructions/ref/listeners, confirmation focus isolation and nudge history; test the real focused SVG endpoint path.
3. Bind collected AC cases, probe producer evidence and the complete product/input surface to their completion predicates.
4. Preserve this loop and let the ledger decide continuation eligibility with the shared mechanism mapping. Any eligible round-2 resubmission needs the protocol's raw blast-radius census and per-hit dispositions; do not reset the loop.
5. Dispatcher: copy this report verbatim to the canonical rolling plan review. This verdict does not authorize implementation.

Completion-preflight was consulted and applied to the review deliverable: product task rows intentionally remain unstarted under the user's review-only authorization. The required JSON final response and static-only command limit take precedence over the local workflow's timestamp-script/footer instruction.

---

## Corrections Applied (2026-10-14)

> **Author:** Claude Code (plan author, coder role, running /plan-corrections). This section does not change the round 1 verdict above. The `changes_required` verdict, its findings and its answers stand as the reviewer wrote them. Plan-corrections Step 6 changes the frontmatter `verdict:` to `corrections_applied` to show the plan is ready for re-review. Only an independent `/plan-critical-review` round may set `approved`.

### Plan summary

The goal is unchanged. MEU-80 adds a themed, accessible hint to every icon-only function button and probes the root cause of the native tooltip. MEU-81 delivers the Capture action icons with Delete at the far right, removes Sample and the nudge pad, adds keyboard endpoint nudging, unsqueezes the marks row and shows the hotkey status inline. The corrections leave the product design alone. They do three things:

- make the hint primitive compose with existing ARIA, ref and listener relations instead of replacing them;
- make the endpoint handles real, reachable focus targets;
- rebuild every task-row completion predicate as a pure evaluator over raw evidence, with an executable self-test.

### Findings and dispositions

| Finding | Disposition | Where |
|---|---|---|
| F1 (High): the Tooltip replaces the trigger's `aria-describedby` and can disturb the drag handle's `DndDescribedBy`, `setActivatorNodeRef` and listeners | **Fixed.** D-25 adds `DESCRIBEDBY_COMPOSE`. The tip's id is appended to any existing `aria-describedby` and never replaces it. `cloneElement` keeps `ref` and `listeners` on the trigger. AC-80.13 proves this in isolation, and AC-80.9 proves it on the real QueueCard drag handle. TA-25 changes only the tip assertions (queue-card.test.ts :1245/:1296); :1261 and :1266 stay as written. | implementation-plan.md: D-25, AC-80.9, AC-80.13, TA-25 |
| F2 (High): the endpoint handles are SVG children under `aria-hidden`, and `annotationOwnsFocus` accepts only `HTMLElement`, so keyboard nudging cannot reach them | **Fixed.** D-26 adds `HANDLE_LAYER` and `NUDGE_TARGET`. The handles move to `capture-handle-layer`, outside the `aria-hidden` marks SVG, as focusable `role="button"` elements with names. `annotationOwnsFocus` checks `Element`, and the space-arming and key-ownership checks treat `[role=button]` as a control. AC-81.14 uses real Tab and arrow keys under Electron. AC-81.15 adds the key-ownership negatives: text inputs, the filmstrip, shot navigation and the confirmation dialog. | D-26, AC-81.14, AC-81.15, Files Modified (CapturePage.tsx, CaptureViewport.tsx) |
| F3 (High, control-defeat): Red, Green and the gate checked counts, not named AC cases | **Redesigned (shared mechanism `task-row-completion-predicate`).** D-27 adds `CASE_EVIDENCE`. `AC_CASES` names each AC's runner, file and class (`red-import`, `red`, `guard`). `eval_vitest_red`, `eval_vitest_ok`, `eval_e2e_red`, `eval_e2e_ok` and `eval_gate` read the raw JSON reports. Each AC case must be collected and must fail by `ASSERTION_FAILURE`, not at setup (`SETUP_SENTINEL`). Skips are refused. Unhandled errors are read from the text receipt. `TA_TAGS` is scoped by row and file. The tolerated failures are listed exactly: `BASELINE_RED`, and `FIXTURE_RED` (below). | D-27, §0, §3, §4, §5, plan_checks.py |
| F4 (High, control-defeat): the probe artifacts could be produced without running the probe at the baseline | **Redesigned.** D-28 adds `PROBE_RUN`. `-Check probe` requires HEAD to equal `baseline.sha` and the tree to be clean, then builds and runs `tooltip-probe.mjs --out … --run …`. The record is bound to head, `gated_clean`, `build_sha256`, exit, start and finish. `eval_probe` requires six on-target observations, PNG signatures with IHDR ≥ 320×200 and sha256, the exact walkthrough lines, and exactly one `finding:` line whose text is `not found` or longer than 10 characters. | D-28, ROOT_CAUSE_PROBE, validate-task.ps1 `probe` |
| F5 (High, control-defeat): `scope` and identity missed `native/` and unlisted product paths | **Redesigned.** D-29 freezes all 18 tracked `native/` files. `eval_scope` sorts every changed path into Files Modified, the plan folder, `ADMIN_PATHS` or frozen, and refuses anything else. `IDENTITY_SCOPE` covers every git-visible file except `IDENTITY_EXCLUDE`. The SSOT update (H1-2) is ordered before GATE (H1-3). `GATED_PATHS` is retired. | D-29, plan_checks.py `scope` / `identity` |
| F6 (Medium, non-blocking): `HINT_TITLE_RULE` coverage after ` title=` left the source-audit pattern | **Fixed.** The rendered DOM proves the rule for the control and for `{id}-tip`, both enabled and disabled, spread titles included: AC-80.4, AC-80.8, AC-80.9 and AC-81.2. Each `title=` hit in the inventory files has a disposition in the census. | AC-80.4/80.8/80.9, AC-81.2 |
| Q6 notes (TA-11/15/24) | **Amended.** TA-11 focuses the enabled button. TA-15 and TA-24 replace the enabled "no reason label" checks with two checks: the plain-name hint appears after `HINT_DELAY_MS`, and it is gone after `HINT_GRACE_MS`. | TEST_AMENDMENTS |

F3, F4 and F5 were redesigned at the mechanism level, not patched point by point. D-27 to D-29 give one evaluator family ownership of every completion predicate, and the `selftest` subcommand runs its refusals. D-30 records `BASELINE_RED`: the one failure that already exists on main `7861020` (`queue-canon.test.ts` AC-41.3) is tolerated by message only. The fix for it is Session 31's unmerged commit `da1d111`.

### Found while building the evaluators (not reviewer findings)

- **`FIXTURE_RED`.** The one case that consumes `queue-slot-baseline.json` (`queue-card-slots.test.tsx`, "AC-55.1 a card with no slot renders the exact pre-change markup") fails at row 3's Red. It fails because FIXTURE_REPAIRS (a) lands before `QueueCard.tsx` changes at row 4. That case is tolerated only at MEU-80's Red, matched by file and title, and only when it fails by assertion. Every Green run, the targeted gates and the GATE require it to pass.
- **Gate `raw_exit`.** `BASELINE_RED` makes `vitest run` exit 1, which contradicted the rule that every stage exits 0. The ui-tests stage's `exit` is now the `vitest-ok --meu 81` verdict over that stage's raw reports. `raw_exit` keeps Vitest's own exit code, and `gate-check` re-evaluates both.
- **Clean-tree exclusion.** `baseline` and `probe` refuse a dirty tree through `plan_checks.py clean`. That check ignores the plan folder and the `.agent/context/handoffs/2026-10-14-capture-chrome-` files, which hold this untracked review.

### Files changed

- `docs/execution/plans/2026-10-14-capture-chrome/implementation-plan.md`: D-25 to D-30; the `DESCRIBEDBY_COMPOSE`, `HANDLE_LAYER`, `NUDGE_TARGET`, `CASE_EVIDENCE`, `AC_CASES`, `TA_TAGS`, `PROBE_RUN`, `FIXTURE_RED` and GATE definitions; AC-80.13, AC-81.14 and AC-81.15; TA-11/15/24/25; §0, §1, §3, §4 and §5.
- `docs/execution/plans/2026-10-14-capture-chrome/task.md`: rows 1–6 and H1-2/H1-3 now cite the new predicates; row 3 names `FIXTURE_RED`.
- `docs/execution/plans/2026-10-14-capture-chrome/validate-task.ps1`:
  - `Invoke-Red` and `Invoke-Green` take `$Meu`, and green-81 re-runs `AC-8[01]`;
  - Vitest uses dual reporters (default and json);
  - the targeted gates pass `--meu --tags`, and the repeat lists pass `--ac`;
  - `probe` is bound to the baseline and a clean tree;
  - `gate` uses schema `s34-gate.v2`, runs `selftest`, and records `raw_exit`;
  - `handoff-ac` calls `handoff-cases`.
- `docs/execution/plans/2026-10-14-capture-chrome/plan_checks.py`: rewritten around pure evaluators, with new `static` checks and a 69-case `selftest`.

### Verification

| Check | Result | Receipt |
|---|---|---|
| `python plan_checks.py static` | PASS: 21 task rows; 17 GATE stages; 27 AC_CASES; scripts, constants and cross-references agree | `C:/Temp/av-kit/s34-plan-static-r2.txt` |
| `python plan_checks.py selftest` | PASS: 69 synthetic inputs; 57 refusals refused; 12 well-formed inputs passed | `C:/Temp/av-kit/s34-plan-selftest-r2.txt` |
| task-table lint | OK: 21 rows; 10-column table; every row backticked, exit-code re-raised, receipt under `RECEIPTS_DIR`; dependencies acyclic | `C:/Temp/av-kit/s34-plan-lint-r2.txt` |
| `static` mutation test (9 mutations: guard AC removed, NEW file moved, row cites a wrong TA, ps1 stage dropped, FIXTURE_RED title changed, ADMIN path changed, unknown `-Check`, unknown `PlanCheck`, TA deletion relabelled) | All 9 refused | scratchpad run; not a repo receipt |
| `validate-task.ps1` parse | Parses cleanly | n/a |

**Blast-radius census.** The census has two parts (PR-6):

- **Raw receipt:** `C:/Temp/av-kit/s34-census-r1.txt` (209 lines). It holds the unfiltered `rg`/`git` output of 11 sweeps, including each of the 18 tracked `native/` files by name.
- **Correction log:** `C:/Temp/av-kit/s34-census-r1-dispositions.md`. It gives every `file:line` in the receipt a disposition, `updated` or `confirmed-consistent`, with a reason. The script that writes it refuses if any hit is left without a disposition or any rule matches no hit.

Blast-radius census: 156 hits found, 90 updated, 66 confirmed consistent, 0 undispositioned. Per sweep: F1 25, F2 13, mechanism predicates 32, `PlanCheck` call sites 23, `native/` 18, stale `GATED_PATHS` 2, stale probe PNG names 0, F6 `title=` 31, `FIXTURE_RED` consumers 3, `raw_exit` 6, Q6 rows 3.

### Ledger state

Round 1 recorded `changes_required` (5 blocking, `intent_achieved: partial`, 8,772,429 tokens). `tools/review_ledger.py` **refuses round 2** for two reasons:

- `[tokens]`: 8,772,429 + 8,772,429 projected > 10,500,000 budget;
- `[mechanism]`: three blocking control-defeat findings (F3, F4, F5) share `task-row-completion-predicate`.

A named human must lift both stops. On 2026-10-15, Mat chose option (a) of the HARD STOP brief in chat. Claude Code recorded that choice as Mat's `continue` (`2026-10-15T00:34:11-04:00`): +9,000,000 tokens and `task-row-completion-predicate` relieved. Ledger after the continue: rounds 1/3, tokens 8,772,429/19,500,000. Round 2 is dispatched with `C:/Temp/av-kit/dispatch/s34-plan-review-prompt-r2.md`.

---

## Round 2 Review (2026-10-15)

> **Review Mode:** plan. **Verdict:** changes_required. **Intent achieved:** partial.
> **Loop:** s34-plan-2026-10-14-capture-chrome, ledger round 2.
> **Reviewer:** gpt-6.1-sol, Codex/OpenAI, independent of the Claude Code/Anthropic author. No Critical findings.

### Intent Anchor

> Session 34 ships MEU-80 (a themed, accessible hint on every icon-only function button, with the native-tooltip root cause probed) and MEU-81 (the Capture actions as icons with Delete red at the far right, Sample and the nudge pad removed, keyboard endpoint nudge, an unsqueezed marks row and the hotkey status inline in the header), resolving the five triaged Capture chrome issues.

The corrected plan substantially specifies the intended hints, action icons, removals, row geometry and inline status. Approval remains blocked by an accepted probe record without producer evidence and a new handle-positioning regression. These are plan findings; no implementation or runtime pass is claimed.

### Scope

**Target:** all four files in `docs/execution/plans/2026-10-14-capture-chrome/`: `implementation-plan.md`, `task.md`, `validate-task.ps1`, `plan_checks.py`. Unqualified target filenames below mean that folder.

**Checkout:** exclusively **P:/av-kit-wt/s34-capture-chrome**, branch `claude/s34-capture-chrome`, HEAD `78610200ea2e7efd52318ea95c3e48b6df4993ba`. Every shell command used this cwd. The different P:/av-kit checkout was not used for plan/product/test reads.

**Protocol:** read plan-critical-review first; then operating instructions/profile, round 1 plus Corrections Applied, and REVIEW-TEMPLATE v2.2. Applied PR-1–PR-9, DR-1–DR-8, the materiality gate and the round-2 census precondition. Consulted completion-preflight for the review deliverable and Session 30's peer review. The user's receipts-only write scope and JSON/static-only output requirements supersede the protocol's canonical-file write and timestamp-script/footer instructions.

**Readiness:** the four plan files and the rolling plan review are untracked; no tracked diff. All 21 task rows remain unchecked. MEU-65/67 are approved, MEU-80/81 pending; both implementation handoffs are absent. New primitive/test/probe files are scheduled creations; existing modified/deleted targets and named repository tools/configs exist.

**Evidence limit:** static file reads, searches, git observations and the two expressly permitted pure subcommands only. No product tests, builds, npm, uv, pytest, Playwright, dotnet, generators, validate-task.ps1 checks, new mutation executions or repository writes. The selftest's existing synthetic inputs ran unchanged.

### Findings

| # | Severity | Blocking | Kind | Finding | File:Line | Recommendation | Status |
|---|----------|----------|------|---------|-----------|----------------|--------|
| F4 | High | yes | control-defeat | **committable-tooling; confidence High.** mechanism: `task-row-completion-predicate`. The root-cause completion evaluator still accepts evidence without the probe producer's build/run binding. Its passing selftest supplies no build_sha256, started, finished or window bounds, and supplies six 33-byte PNG headers with no image data. Row 2 validates only root-cause, so this accepted input can complete the required investigation without an on-target probe. Violates AC-80. | docs/execution/plans/2026-10-14-capture-chrome/plan_checks.py:995; docs/execution/plans/2026-10-14-capture-chrome/plan_checks.py:1339; docs/execution/plans/2026-10-14-capture-chrome/task.md:38 | Make row 2 require successful producer evidence from -Check probe, validate the required build/run binding fields, and reject the existing metadata-free/header-only positive fixture. Preserve a genuine baseline capture record and a negative case for absent producer evidence. | open |
| F7 | High | yes | behavior | **deliverable; confidence High.** HANDLE_LAYER places the new full-size SVG under capture-draw-surface without preserving capture-zoom-content's contentStyle transform. The marks and hit tests use the zoom/pan transform, while this SVG fits image coordinates to the surface. Away from Fit, its visible/focused handles diverge from the arrow endpoints and pointer hit targets; AC-81.14 checks cy attributes and cannot detect that misalignment. Violates AC-81. | docs/execution/plans/2026-10-14-capture-chrome/implementation-plan.md:141; ui/src/renderer/src/features/capture/CaptureViewport.tsx:632; ui/src/renderer/src/features/capture/CaptureViewport.tsx:1134 | Keep the exposed handle SVG alongside the marks SVG inside capture-zoom-content, or apply the same contentStyle transform explicitly. Add real Electron bounding-box and hit-target assertions at a non-Fit zoom with pan, preserving the constant CSS handle radius. | open |

#### F4 — original producer-evidence requirement remains open

The producer wrapper now has useful baseline and clean-tree guards (`validate-task.ps1:192-213`), deletes old captures and records `build_sha256`, `started` and `finished`. That is an improvement. However, the completion path remains `task.md:38` → `validate-task.ps1:217-219` → `cmd_root_cause` (`plan_checks.py:1034-1045`). It does not require a successful producer invocation or consume those build/run fields. `eval_probe:995-1031` accepts caller-supplied head/clean assertions and observation geometry.

The **existing, executed** positive oracle is decisive: `selftest_cases:1328-1342` creates a record with only `exit`, `head`, `gated_clean` and six observations. It has no build hash, start/end or window bounds. Its six “screenshots” are copies of `_png:1216-1217`: 33 bytes containing a signature and IHDR, with no IDAT/IEND/image data. The selftest printed `ok  root-cause: well-formed: passes`. These bytes cannot be viewed as the required screen captures, yet they satisfy the very evaluator used to complete AC-80.12.

This is the still-missing producer proof from round 1, not a demand for a tamper-proof evidence system or another PNG-format refinement. Rejecting one-byte files and checking declared geometry does not close the original “investigation can be omitted” false pass. Bind the completion check to the actual baseline probe procedure and its required run metadata/captures; turn this accepted metadata-free input into a negative oracle.

**Contract:** AC-80.12, ROOT_CAUSE_PROBE/PROBE_RUN, build-plan 09:686, PR-4/PR-8. Ledger contract: **AC-80**. Keep ID **F4**, mechanism **task-row-completion-predicate**; do not reset/split recurrence.

#### F7 — the newly exposed handles must retain the image transform

The baseline nests both marks and handles under `capture-zoom-content` (`CaptureViewport.tsx:1134-1195`). Its `contentStyle` (`:632-635`) supplies `left=view.ox`, `top=view.oy`, `width=imageWidth*view.s`, `height=imageHeight*view.s`. Pointer mapping and hit testing use that same scale and offset (`:243-265`; `CapturePage.tsx:620-650`).

The new HANDLE_LAYER contract (`implementation-plan.md:141`) instead puts a full-size, inset SVG as a later child of `capture-draw-surface`, with image-sized viewBox and `preserveAspectRatio="xMidYMid meet"`. It never preserves the `capture-zoom-content` ancestor or applies `contentStyle`. That fits the handles to the surface while the arrow and hit targets remain zoomed/panned.

A concrete existing fixture supplies the counterexample: `capture-page.behavior.test.ts:1721-1748` has an 800×600 surface, a 1600×900 image, scale 2 and origin (-1000,-450). Its tail at image (700,375) belongs at surface (400,300). The proposed surface-sized SVG renders it at (350,262.5), using Fit scale 0.5 and the 75 px vertical letterbox; its radius also becomes one quarter of the intended CSS radius. The unchanged pointer hit test still expects (400,300). No runtime inference is needed to distinguish the two coordinate formulas.

AC-81.14 (`implementation-plan.md:303`) reads `cy` attributes, so it can pass while the focused circle is visibly displaced. Keep the second SVG exposed but **inside capture-zoom-content**, alongside the hidden marks SVG, or give it the identical transform. Assert real screen geometry and a grab at non-Fit zoom plus pan.

**Contract:** AC-81.6/81.14, the requirement that drag handles stay (09:698), existing arrow-handle and zoom mapping canon (09:386,643), PR-8/DR-6. Ledger contract: **AC-81**. This is a new rendering regression introduced by D-26, distinct from the fixed HTMLElement/aria-hidden focus defect.

### Recheck (2026-10-15)

**Workflow:** /plan-critical-review, round 2. **Agent:** gpt-6.1-sol.

#### Prior Pass Summary and Closure

| Item | Status | Evidence / disposition |
|---|---|---|
| F1 | closed | DESCRIBEDBY_COMPOSE and cloneElement preservation at plan:130, D-25:672-681; AC-80.9:234 and AC-80.13:238 cover the real drag handle and isolated ref/listener composition. TA-25:192 retains queue-card.test.ts:1261/:1266. Actual drag props at QueueCard.tsx:507-517 agree. |
| F2 | regressed | The original focus defect is addressed by plan:141, D-26:682-691, AC-81.6:295, AC-81.14:303 and AC-81.15:304: exposed SVG handles, Element ownership, one bubbling key path, role-button Space exclusion and surface-focus reset. The new layer placement introduces F7's coordinate regression. |
| F3 | closed | AC_CASES:136-144, named-case lookup:660-662, Red:677-716, Green:719-747, Electron:778-829 and gate:869-894 replace aggregate-only proof. Sentinels:665-674 and row/file-scoped tags:711-715/736-742/822-828 close the demonstrated missing-case, skipped-case and file-wide TA tolerance paths. Handoff coverage retains dotted IDs:962-975. Selftest exercises the principal refusals. |
| F4 | open | Producer guards added at ps1:192-213, but completion still invokes only root-cause; eval_probe:995-1031 and its passing synthetic input:1328-1342 demonstrate the absent producer proof described above. |
| F5 | closed | FROZEN:77 now includes native/; eval_scope:577-598 classifies every changed path. identity:477-491 hashes every git-visible nonexcluded path, including native sources and consumed docs. Plan:152/427 and task H1-2→H1-3 move hashed SSOT edits before GATE. Selftest refuses unlisted native/docs changes and stale identity. |
| F6 | closed | HINT_TITLE_RULE:135 now has rendered control-and-wrapper assertions: AC-80.4:229 (spread title), AC-80.8:233, AC-80.9:234 and AC-81.2:291, enabled and disabled. Legitimate labelled titles remain allowed. |
| Q6 | closed | TA-11:178 focuses the enabled child, not its non-tabbable wrapper; TA-15:182 and TA-24:191 require the enabled name hint after delay and its disappearance after grace. Current tests at capture-page.behavior.test.ts:1263/:1297 and capture-inbox.test.ts:1588-1605 substantiate those amendments. |

#### R1–R4 Answers

**R1 — Closure.** Five findings/notes are closed (F1, F3, F5, F6, Q6). F4's original producer-evidence condition remains open. F2's focus/accessibility change is specified correctly, but the correction regresses visual/hit geometry through F7. No closure is based on the Corrections Applied prose alone.

**R2 — Redesigned mechanism.** Named AC collection now refuses a missing, renamed or skipped required case; an AC-81.60 title cannot substitute for AC-81.6. Loading-file Red requires assertion failures plus a passing shared render sentinel; the declared Tooltip import failure is restricted by module and source case names. Green/gate require every applicable AC and amendment tag in its designated file; the final gate re-evaluates raw reports. These are meaningful repairs of F3.

FIXTURE_RED matches one file/title and only MEU-80 Red; ordinary Green rejects that failure. BASELINE_RED matches its file, AC and distinctive message; different failures are refused. The ui-tests stage records raw_exit and uses the evaluator verdict, so accepting that known baseline failure does not broadly swallow failures. Clean exclusions allow the intended plan/probe/review files; product edits remain refused, and probe also checks HEAD against baseline.sha. Scope covers frozen native sources and unlisted files; identity includes those git-visible bytes and consumed docs. These changes close the demonstrated F5 hole.

The remaining material false pass is **F4**. The 69 passing inputs do not establish more than their cases: the probe's positive input itself omits producer bindings and actual image content. A missing-producer/capture refusal is the important missing negative. The FIXTURE_RED-at-row-6 synthetic also has unrelated missing ACs, so its refusal alone is not an isolated proof of that exception; the explicit MEU check in the implementation supplies the substantive restriction. No new blocker is raised for that test-design detail.

The identity covers the stated git-visible surface, not arbitrary ignored build outputs, installed dependencies or runtime environment changes. Do not treat it as a runtime-environment attestation. This bounded residual was not escalated into another F5 variant.

**R3 — Regressions.** F7 is a concrete new regression. No evidence of a double focus stop was found: the old endpoint circles are moved, not duplicated; the new SVG root has no planned tabindex; each of the two controls has one tab stop. Element-based focus ownership preserves viewport containment, confirm-strip and COLOR_FOCUS_IDS exclusions. The filmstrip stays outside that viewport. Space excludes role buttons; the surface remains the single keydown owner, with existing burst/key-up history handling. AC-81.15 covers text/color, filmstrip and confirmation negatives. These are static conclusions; real Electron/screen-reader behavior remains execution work.

**R4 — Census adequacy.** The PR-6 procedural precondition **passes**: both artifacts exist, the receipt is complete, and every hit has a per-hit disposition. Independently replayed all eleven rg/git sweeps with **zero hit-set differences**, and matched all referenced tree lines plus the native file inventory. Counts: **209 receipt lines; 156 hits; 90 updated, 66 confirmed-consistent; zero missing/extra dispositions and zero tree mismatches**.

The sweep counts reproduce as 25 / 13 / 32 / 23 / 18 / 2 / 0 / 31 / 3 / 6 / 3. Reviewed the substantive reasons, not only their labels. The unchanged drag description/ref assertions, legitimate text/control titles, sole fixture consumer, old schema negative and historical GATED_PATHS mention are consistent. One reason calls surfaceFromDom's HTMLElement check a “toolbar target” (`CaptureViewport.tsx:252`); the actual currentTarget is the HTML draw surface, so retaining it is still correct.

Substantive coverage is partial: the F2 sweep never reaches `capture-zoom-content`/`contentStyle` and therefore misses the ancestor transform the move must preserve. The generic “rewritten/selftest” dispositions do not substantiate probe production (F4). These are the two delivery/evidence defects above, not a missing-census procedural refusal.

### Commands Executed

All process streams went to C:/Temp/av-kit, with native exit preserved before completed receipt readback. Commands used `rtk proxy`; nested read scripts were carried by `rtk proxy pwsh -NoProfile -Command`. No repository command ran from another checkout.

#### Executed pure checks

| Command (cwd as above) | Exit | Output |
|---|---:|---|
| `rtk proxy python docs/execution/plans/2026-10-14-capture-chrome/plan_checks.py static` | 0 | PASS static: 21 task rows; 17 GATE stages; 27 AC_CASES; scripts, constants and cross-references agree |
| `rtk proxy python docs/execution/plans/2026-10-14-capture-chrome/plan_checks.py selftest` | 0 | PASS selftest: 69 synthetic inputs; 57 refusals refused; 12 well-formed inputs passed |

Full selftest output is embedded below. It is synthetic evaluator evidence, not product coverage.

#### Git, reads and existence observations

- `git status --short --untracked-files=all`, `git log -1 --format=oneline`, `git branch --show-current`, `git diff --stat` (exit 0): five untracked review/plan files, HEAD/branch above, no tracked diff. User-level git-ignore permission warnings were retained; no repository operation failed.
- `Get-Content` read the workflow, AGENTS, GUARDRAILS, PROJECT-PROFILE, prior review/corrections, REVIEW-TEMPLATE, terminal-preflight/output-evidence policy, current-focus, known-issues, harness.local, reviewer role, harness-profiles, completion-preflight and v2 verdict schema. The four target files were read in numbered slices through plan:762, checks:1439, ps1:447 and all task rows.
- `Get-Content`/`rg -n` sampled grouping/session/dependency rows, the five issue records, 09's arrow/zoom/hint/action contracts and 06's GUI/Electron canon; production CaptureViewport/CapturePage, QueueCard, and the tests/fixtures/runner files cited above. Read Session 30's peer review.
- `rg -n -A 58 -e '^## .*D6|^### .*D6|D6_ADOPTER_ARGV' .agent/docs/commands.md` (exit 0) confirmed the registered gate commands and input-identity limits. `rg -n -A 35 -B 4 -e 'AC-41.3|PILL_TOKEN_SOURCE|light diverges' ui/tests/unit/queue-canon.test.ts` and `git show --stat --oneline da1d111 -- ui/src/renderer/src/styles.css` (exit 0) confirmed the named baseline case/message source and the existing Session 31 fix commit; no failing product run was reproduced here.
- `Test-Path` checked every Files Modified row, both absent future handoffs, tools/Invoke-CodexDispatch.ps1, meu_status.py, issue_triage.py, validate_closeout_artifacts.py, durable_evidence.py, lint_task_contract.py, export_openapi.py, openapi.committed.json, the Playwright wrapper/config, ui/tsconfig.json and reflection template/schema. All current modify/delete targets and invoked repository tools exist; absent creation targets are scheduled.
- Narrow `rg` of MEMORY.md returned no relevant history; no memory-derived fact was used.
- Incidental nonexistent-path reads/searches of ui/tsconfig.web.json, ui/tests/unit/capture-viewport-zoom.test.tsx and ui/node_modules/playwright/lib/reporters/json.js were not treated as evidence. The last reporter search exited 2; runner conclusions use existing package/config/wrapper files, and no claim about the installed reporter implementation is made. Early anchored issue/dependency searches were superseded by successful matching searches. A first census comparison normalized a literal backslash in source text; corrected it to normalize paths only, then obtained zero mismatches. None is a project-suite failure.

#### Complete census replay commands

Each command below used unfiltered output, `--path-separator /` for rg, and separate receipts `s34-r2-sweep-*.txt`. All exited 0 except the intentionally empty old-PNG-name sweep, exit 1.

```text
rtk proxy rg -n --path-separator / -e 'aria-describedby|DndDescribedBy|setActivatorNodeRef|\{\.\.\.listeners\}' ui/src/renderer ui/tests
rtk proxy rg -n --path-separator / -e 'annotationOwnsFocus|aria-hidden|spaceArmable|instanceof HTMLElement' ui/src/renderer/src/features/capture
rtk proxy rg -n --path-separator / -e '^def (cmd|eval)_' docs/execution/plans/2026-10-14-capture-chrome/plan_checks.py
rtk proxy rg -n --path-separator / -e 'PlanCheck ''|plan_checks.py" vitest-ok' docs/execution/plans/2026-10-14-capture-chrome/validate-task.ps1
rtk proxy git ls-files native
rtk proxy rg -n --path-separator / -e 'GATED_PATHS|dirty_gated|s34-gate\.v1' docs/execution/plans/2026-10-14-capture-chrome
rtk proxy rg -n --path-separator / -e 's34-probe-h(\{n\}|[1-3])\.png' docs/execution/plans/2026-10-14-capture-chrome
rtk proxy rg -n --path-separator / -e '\btitle=' ui/src/renderer/src/features/capture ui/src/renderer/src/components/queue ui/src/renderer/src/components/layout/ConsolePanel.tsx ui/src/renderer/src/features/transcript/TranscriptPage.tsx ui/src/renderer/src/features/converter/ConvertPage.tsx
rtk proxy rg -n --path-separator / -e 'queue-slot-baseline' ui/tests
rtk proxy rg -n --path-separator / -e 'raw_exit|every stage|BASELINE_RED makes' docs/execution/plans/2026-10-14-capture-chrome
rtk proxy rg -n --path-separator / -e '^\| TA-(11|15|24) ' docs/execution/plans/2026-10-14-capture-chrome/implementation-plan.md
```

A read-only PowerShell comparison split the original receipt into its 11 sweep sections and compared sorted complete output lines with those fresh receipts; every difference count was 0. A second read-only comparison matched every disposition key to its receipt hit and every path:line to Get-Content of the tree; all 156 matched. Decisive output:

```text
Raw lines: 209
Raw hits: 156; dispositions: 156; updated: 90; confirmed-consistent: 66
Undispositioned: 0; extra dispositions: 0; tree mismatches: 0
f1: original=25 fresh=25 differences=0
f2: original=13 fresh=13 differences=0
predicates: original=32 fresh=32 differences=0
callers: original=23 fresh=23 differences=0
native: original=18 fresh=18 differences=0
gated: original=2 fresh=2 differences=0
png: original=0 fresh=0 differences=0
titles: original=31 fresh=31 differences=0
fixture: original=3 fresh=3 differences=0
rawexit: original=6 fresh=6 differences=0
q6: original=3 fresh=3 differences=0
```

### Checklist Results

Manual observer: **gpt-6.1-sol**. Manual observations have null exit; they are not executed product tests.

#### Information Retrieval (IR)

| Check | Result | Procedure / evidence | Exit |
|---|---|---|---|
| AC source labels | pass | Compared decision/AC tables with grouping, five issue records and 09 canon. | null |
| Exact validation commands | partial | Commands/callers exist; F4 still false-passes a missing investigation. | null |
| BUILD_PLAN audit | pass | Plan:350-370 and task row 10 enumerate 09/11/matrix/render edits. | null |
| Post-MEU outputs | pass | Two handoffs, fresh gate, human look, independent review, reflection, metrics and commit draft are explicit. | null |

#### Plan Review (PR)

| Check | Result | Procedure / decisive evidence | Exit |
|---|---|---|---|
| PR-1 alignment | pass | Compared all 21 rows with work packages and verification stages; MEU-80 precedes MEU-81. | null |
| PR-2 unstarted | pass | Git state, unchecked rows, pending targets and absent handoffs agree. | null |
| PR-3 task contracts | pass | Read owner/deliverable/exact command/dependency/status on every row; static agrees. | null |
| PR-4 validation realism | fail | Existing root-cause positive selftest passes without required producer bindings/captures (F4). | null |
| PR-5 sources | pass | Human triage amendments and local/research design choices retain declared provenance. | null |
| PR-6 corrections/census | partial | Procedural precondition passes: 11/11 sweeps and 156/156 dispositions reproduce. F4/F7 expose substantive gaps in generic evaluator/handle-move dispositions. | null |
| PR-7 scope | pass | Exclusions/deferrals have canon/registered MEUs; scope now classifies all changed paths, including frozen native. | null |
| PR-8 reachability/oracles | fail | F4 producer proof remains missing; F7's layer leaves the production coordinate transform. Other named-case refusals are effective. | null |
| PR-9 single statements | pass | Static verifies manifest/constants/stage order; no materially competing live value found. | null |

#### Docs Review (DR)

| Check | Result | Procedure / decisive evidence | Exit |
|---|---|---|---|
| DR-1 claims/state | partial | Draft/unstarted status is accurate; F4's claimed probe closure overstates what its evaluator proves. | null |
| DR-2 residual terms | pass | Old schema/PNG/nudge/title terms are intentional history, negatives or removal contracts. | null |
| DR-3 references | pass | New paths are scheduled and registry/help/hub changes explicit. | null |
| DR-4 verification robustness | fail | F4 accepts an absent probe; AC-81.14 checks attributes rather than F7's screen alignment. | null |
| DR-5 auditability | pass | Exact scripts, raw reports, replayable census and embedded outputs; no runtime claim. | null |
| DR-6 cross-canon | fail | New handle placement conflicts with existing zoom/handle mapping, F7. | null |
| DR-7 freshness | pass | Reproduced static/selftest totals and all eleven census hit sets against this tree. | null |
| DR-8 residual/completion | pass | No implementation-complete claim; tasks remain unstarted and approval withheld. | null |

Adversarial AV-1–AV-6 were assessed as plan obligations: Red/Green production proof is future work, no skips/bypass instructions were found, source-backed ACs are present, and the missing probe/coordinate assertions are disclosed above. No execution-stage quality claim is inferred.

#### Durable evidence

```json
{"schema_version":"evidence.v1","check_id":"s34-r2-static","command":"rtk proxy python docs/execution/plans/2026-10-14-capture-chrome/plan_checks.py static","cwd":"P:/av-kit-wt/s34-capture-chrome","scope":"four plan-local review targets","phase":"static","exit_code":0,"result":"pass","tested_state":"HEAD 78610200ea2e7efd52318ea95c3e48b6df4993ba plus the untracked corrected four-file plan inspected this round","output":"PASS static: 21 task rows; 17 GATE stages; 27 AC_CASES; scripts, constants and cross-references agree","fresh":true}
{"schema_version":"evidence.v1","check_id":"s34-r2-selftest","command":"rtk proxy python docs/execution/plans/2026-10-14-capture-chrome/plan_checks.py selftest","cwd":"P:/av-kit-wt/s34-capture-chrome","scope":"existing synthetic evaluator inputs only","phase":"static","exit_code":0,"result":"pass","tested_state":"same corrected plan_checks.py read in this round","output":"PASS selftest: 69 synthetic inputs; 57 refusals refused; 12 well-formed inputs passed. The root-cause positive fixture contains no build/run binding metadata and uses six 33-byte PNG headers.","fresh":true}
```

#### Full selftest output (exit 0)

```text
ok  vitest-red 80: well-formed: passes
ok  vitest-red 80: a missing AC case: refuses � AC-80.9: 0 cases in icon-hints.test.ts carry it in their title (need 1)
ok  vitest-red 80: a skipped AC case: refuses � skipped cases: ['icon-hints.test.ts: AC-80.9: other inventory']
ok  vitest-red 80: a TypeError Red: refuses � AC-80.8 is not an assertion Red: failed 'TypeError: x is not a function'
ok  vitest-red 80: a failed SETUP_SENTINEL: refuses � icon-hints.test.ts: the first case is not a passing 'setup sentinel' (SETUP_SENTINEL)
ok  vitest-red 80: a failure with no TA tag: refuses � untolerated Red failure (S2/S3) capture-page.behavior.test.ts: AC-57.5 disabled box
ok  vitest-red 80: another row's tag: refuses � untolerated Red failure (S2/S3) capture-page.behavior.test.ts: AC-57.5 disabled box [TA-1]
ok  vitest-red 80: a tag in the wrong file: refuses � untolerated Red failure (S2/S3) queue-card.test.ts: handle [TA-8]
ok  vitest-red 80: a tagged TypeError: refuses � untolerated Red failure (S2/S3) capture-page.behavior.test.ts: AC-57.5 disabled box [TA-8]
ok  vitest-red 80: a BASELINE_RED look-alike: refuses � untolerated Red failure (S2/S3) queue-canon.test.ts: AC-41.3 accent tokens
ok  vitest-red 80: FIXTURE_RED at row 6: refuses � AC-81.1: 0 cases in capture-action-row.test.ts carry it in their title (need 1)
ok  vitest-red 80: unhandled errors: refuses � the Vitest text receipt reports unhandled errors
ok  vitest-red 80: no text receipt: refuses � the Vitest text receipt is missing (unhandled errors cannot be ruled out)
ok  vitest-red 80: exit 0: refuses � Red expected a failing run, got exit 0
ok  vitest-red 80: the red-import file loaded: refuses � tooltip.test.tsx loaded at Red: its red-import module already exists
ok  vitest-red 80: another suite fails to load: refuses � suite load error in icon-hints.test.ts: SyntaxError: Unexpected token
ok  vitest-red 80: a red-import title missing: refuses � AC-80.13: 0 cases carry it in their title in the tooltip.test.tsx source (need 1)
ok  vitest-red 81: well-formed: passes
ok  vitest-red 81: a guard failing by TypeError: refuses � AC-81.7 (guard) failed by a non-assertion: 'TypeError: cannot read'
ok  vitest-red 81: a red case passing: refuses � AC-81.1 is not an assertion Red: passed ''
ok  vitest-red 81: AC-81.6 matched by AC-81.60: refuses � AC-81.6: 0 cases in capture-action-row.test.ts carry it in their title (need 1)
ok  vitest-ok 81: well-formed (BASELINE_RED tolerated): passes
ok  vitest-ok 81: a missing tag: refuses � TA-26: 0 tagged cases in layout-primitives.test.ts, not all passed (TA_TAGS)
ok  vitest-ok 81: an AC case failed: refuses � AC-80.2 is failed
ok  vitest-ok 81: another failure: refuses � failed: x.test.ts: other
ok  vitest-ok 81: a skipped case: refuses � skipped cases: ['x.test.ts: other']
ok  vitest-ok: exit 1 with no failing case: refuses � Vitest exit 1 with no failing case (an unhandled error or a crash)
ok  vitest-ok: unhandled errors: refuses � the Vitest text receipt reports unhandled errors
ok  vitest-ok: baseline well-formed: passes
ok  e2e-red 80: well-formed: passes
ok  e2e-red 80: a TypeError Red: refuses � AC-80.10 did not fail by an expect() assertion: 'TypeError: x is undefined at expect('
ok  e2e-red 80: a skipped AC case: refuses � AC-80.11 statuses ['skipped'] (need failed, never skipped)
ok  e2e-red 80: a missing AC case: refuses � AC-80.11: 0 cases in console-chrome.test.ts carry it in their title (need 1)
ok  e2e-ok 81 with tags: well-formed: passes
ok  e2e-ok 81: a skipped spec: refuses � stats {'expected': 12, 'unexpected': 0, 'flaky': 0, 'skipped': 1} (need unexpected = flaky = skipped = 0, expe
ok  e2e-ok 81: a missing tag: refuses � TA-19: 0 tagged specs in capture-inbox.test.ts, not all expected (TA_TAGS)
ok  e2e-ok --ac: the repeated case absent: refuses � AC-80.10: 0 cases in capture-inbox.test.ts carry it in their title (need 1)
ok  scope: well-formed: passes
ok  scope: a native/ change: refuses � frozen path changed: native/region-picker-stub/Program.cs
ok  scope: an unlisted docs/ change: refuses � changed paths outside Files Modified, the plan folder and ADMIN_PATHS: ['docs/build-plan/04-rest-api.md']
ok  scope: a frozen path changed in a commit: refuses � frozen paths changed: ['tools/review_ledger.py']
ok  clean: plan files only: passes
ok  clean: a product edit: refuses � changed outside this plan's own files: ['ui/src/renderer/src/App.tsx']
ok  root-cause: well-formed: passes
ok  root-cause: a one-byte PNG: refuses � s34-probe-h1-nav-capture.png is not a PNG (signature or IHDR)
ok  root-cause: a wrong-hash PNG: refuses � s34-probe-h1-nav-capture.png does not match its recorded sha256
ok  root-cause: a 16x16 PNG: refuses � s34-probe-h1-nav-capture.png is 16x16 (need at least 320x200)
ok  root-cause: a run on another head: refuses � run exit 0 head bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb gated_clean True (need 0, baseline aaaaaaaaaaaaaaaaaa
ok  root-cause: a dirty tree at probe time: refuses � run exit 0 head aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa gated_clean False (need 0, baseline aaaaaaaaaaaaaaaaa
ok  root-cause: the cursor off target: refuses � H1 nav-capture: cursor {'x': 10, 'y': 10} is not inside the target rect {'x': 100, 'y': 200, 'width': 40, 'hei
ok  root-cause: a target with no title: refuses � H1 capture-tool-arrow: the target had no title attribute
ok  root-cause: five observations: refuses � observations [(1, 'capture-tool-arrow'), (1, 'nav-capture'), (2, 'capture-tool-arrow'), (2, 'nav-capture'), (3
ok  root-cause: a placeholder observation line: refuses � �Root cause needs exactly the 6 observation lines; found 6: ['- H1 nav-capture: tooltip-visible yes|no � s34-p
ok  root-cause: no finding line: refuses � �Root cause needs one finding: line (a cause and fix longer than 10 characters, or 'not found'); found []
ok  root-cause: a placeholder finding: refuses � �Root cause needs one finding: line (a cause and fix longer than 10 characters, or 'not found'); found ['tbd']
ok  handoff-cases: well-formed: passes
ok  handoff-cases: only AC-80: refuses � MEU-80 handoff does not name ['AC-80.1', 'AC-80.2', 'AC-80.3', 'AC-80.4', 'AC-80.5', 'AC-80.6', 'AC-80.7', 'AC
ok  handoff-cases: a range instead of ids: refuses � MEU-80 handoff does not name ['AC-80.2', 'AC-80.3', 'AC-80.4', 'AC-80.5', 'AC-80.6', 'AC-80.7', 'AC-80.8', 'AC
ok  handoff-cases: no identity: refuses � MEU-80 handoff does not quote gate-result.json identity_after 'FFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFF
ok  census: well-formed: passes
ok  census: a wildcard: refuses � �Census uses a wildcard: - ui/tests/unit/a.test.ts:* � unaffected, ids only
ok  census: an uncovered hit: refuses � 1 census hits have no disposition: ['ui/tests/unit/a.test.ts:40']
ok  census: a new-contradiction: refuses � �Census records a new-contradiction: Stop condition S2 (Decision Brief, no test edit)
ok  gate-check: well-formed: passes
ok  gate-check: a stage out of order: refuses � stages ran ['ui-electron', 'ui-tests'], expected ['ui-tests', 'ui-electron'] (schema s34-gate.v2)
ok  gate-check: the tree changed after the gate: refuses � identity mismatch: before FFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFF after FFFFFFFFFFFFF
ok  gate-check: an AC case missing from the raw report: refuses � Vitest: AC-80.1: 0 cases in tooltip.test.tsx carry it in their title (need 1)
ok  gate-check: below COUNT_FLOORS: refuses � Vitest total 10 < 773 (COUNT_FLOORS)
ok  gate-check: v1 schema: refuses � stages ran ['ui-tests', 'ui-electron'], expected ['ui-tests', 'ui-electron'] (schema s34-gate.v1)
PASS selftest: 69 synthetic inputs; 57 refusals refused; 12 well-formed inputs passed
```

### Verdict

**changes_required** — **two High blocking findings, F4 and F7**, both open. Intent achieved: **partial**. Findings and their metadata match the structured final verdict.

The ARIA/ref/listener repair, named-case evaluators, native/unlisted scope coverage, DOM title checks and Q6 amendments are substantive improvements. The remaining probe false pass and new zoom/pan handle regression prevent concluding that executing the plan as written delivers the full goal safely and testably.

### Follow-up Actions

1. Use /plan-corrections to close F4's producer-evidence requirement and F7's transformed handle placement; preserve the closed F1/F3/F5/F6/Q6 repairs.
2. For F4, replace the accepted metadata-free/header-only positive fixture with a negative; retain a real baseline probe record/captures as the execution deliverable. For F7, keep the accessible layer in the existing transformed container and prove non-Fit/panned screen alignment.
3. Census the affected producer helpers/callers and coordinate-container siblings; retain raw output and per-hit dispositions.
4. Preserve loop/round history and F4's existing mechanism slug. The ledger, not this report, determines continuation eligibility; no stop/cap is reset.
5. Dispatcher: copy **C:/Temp/av-kit/dispatch/s34-plan-review-report.md** verbatim to the canonical rolling plan review. The reviewer wrote only this receipts report and working receipts. No plan/product/test correction or execution is authorized by this verdict.

Completion-preflight was consulted for the authorized review output. All 21 product task rows intentionally remain unstarted; their execution and H1/H2 closeout were outside this review. No timestamp script was run under the user's static-only restrictions.

---

## Corrections Applied (2026-10-15)

> **Author:** Claude Code (plan author, coder role, running /plan-corrections). This section does not change the round 2 verdict above. The `changes_required` verdict, its findings and its R1–R4 answers stand as the reviewer wrote them. Plan-corrections Step 6 changes the frontmatter `verdict:` to `corrections_applied` to show the plan is ready for re-review. Only an independent `/plan-critical-review` round may set `approved`.

### Findings and dispositions

| Finding | Disposition | Where |
|---|---|---|
| F4 (High, control-defeat, mechanism `task-row-completion-predicate`): root-cause accepted a record with no producer binding, and the passing selftest used six 33-byte header-only PNGs | **Redesigned (D-31).** `-Check probe` now records `check: probe`, `build_sha256` (`ui/out/main/index.js`), `probe_sha256` (`tooltip-probe.mjs`) and `receipt_sha256` (`s34-probe-run.txt`), plus `head`, `gated_clean`, exit, `started` and `finished`. The probe prints one `PROBE-DONE <6 PNG sha256 in order>` line into its receipt. `root-cause` refuses unless: HEAD is `baseline.sha` on a clean tree; the three recorded hashes equal the files on disk now; the run lasts at most 15 minutes with zoned times; every observation `at` and every PNG mtime (±2 s) falls inside the run; every cursor lies inside its target rect and every rect inside its window; every PNG **fully decodes** (`png_decode`: chunk CRCs, IHDR first, IDAT, IEND last, inflated length = h × (1 + w × bpp)) at exactly the captured window's size, ≥ 320×200; and the receipt's `PROBE-DONE` line names exactly those PNGs. The window is the physical content rect (`screen.dipToScreenRect`) and all coordinates are physical pixels. The selftest positive is a complete, self-consistent bundle with real encoded PNGs; **round 2's metadata-free record with header-only PNGs is now a negative**, along with about 37 single-cause root-cause refusals. The binding is not tamper-proof against someone who rewrites every artefact together; the plan says so, and the reviewer reads the PNGs. | D-31 (D-28 superseded in part); `ROOT_CAUSE_PROBE` row; AC-80.12; plan_checks.py `png_decode`, `eval_probe`, `cmd_root_cause`; validate-task.ps1 `probe` |
| F4 sibling (same mechanism): every other checker that reads a record written by a separate producer | **Bound (D-31).** The audit found one split producer/record pair besides the probe: `gate-result.json`, written by `-Check gate` and read by `gate-check`, `look-check` and `handoff-cases`. `-Check gate` now records `check: gate` and the sha256 of each raw report it names (`vitest_json`, `vitest_txt`, `e2e_json`). All three readers apply one `eval_gate_binding`, re-hashing the reports on disk. Every other check runs its producer in the same invocation (census, Red, Green, the targeted gates) or reads live state. The census below lists every case. | D-31; `GATE` row; handoff-cases and look-check prose; plan_checks.py `eval_gate_binding`, `gate_report_shas`; validate-task.ps1 `gate` |
| F7 (High, behavior): `HANDLE_LAYER` sat outside `capture-zoom-content`, so away from Fit the handles left the arrow ends and shrank | **Fixed (D-32).** The handle `<svg>` is now the next sibling after the `aria-hidden` marks `<svg>`, **inside `capture-zoom-content`**, with the same `viewBox` and `preserveAspectRatio`. It therefore gets the same zoom box (`contentStyle`), and `r={handleRadius}` renders at a constant `2 × HANDLE_RADIUS_CSS` CSS px. It stays a descendant of `capture-draw-surface`, so keydown still bubbles to the one handler, and `capture-zoom-content` is `pointer-events-none` and not `aria-hidden`. AC-81.6 checks the layer's parent and the matching `viewBox`; its negative is a layer that is a direct child of the surface. AC-81.14 now runs at 100% after a real middle-drag pan of (−40, −30). It checks each handle's rendered box centre against `toClient(cx, cy)` within 1 px and its width against `2 × HANDLE_RADIUS_CSS`, does a real grab of +20 px (`x2` grows by `20 / s`), then Tab and ArrowUp ×3 with the centre still aligned and the surface not scrolled. | D-32; `NUDGE_TARGET` row; AC-81.6; AC-81.14; Files Modified; UI table; D-26 note |
| R2 note: the FIXTURE_RED-at-row-6 synthetic also has unrelated missing ACs | **Not changed (non-blocking).** The reviewer found the explicit MEU check in the implementation supplies the restriction. | n/a |

### Files changed

All in `docs/execution/plans/2026-10-14-capture-chrome/` (untracked):

- `implementation-plan.md`: D-31 and D-32 added, and D-28 marked superseded in part. Also updated: the `ROOT_CAUSE_PROBE`, `NUDGE_TARGET` and `GATE` rows, AC-80.12, AC-81.6, AC-81.14, the Files Modified CaptureViewport row, the UI table row, the handoff-cases and look-check prose, and §0 note 7.
- `plan_checks.py`:
  - added `png_decode`, a real PNG encoder and a header-only negative for the selftest, the redesigned `eval_probe` and `cmd_root_cause`, and `eval_gate_binding` and `gate_report_shas`;
  - `gate-check`, `look-check` and `handoff-cases` now apply the binding;
  - the selftest grew from 69 to 97 inputs.
- `validate-task.ps1`: `probe` writes the D-31 fields, and `gate` writes `check: gate` and the report hashes.
- `task.md`: unchanged.

### Verification

| Check | Result | Receipt |
|---|---|---|
| `python plan_checks.py static` | PASS: 21 task rows; 17 GATE stages; 27 AC_CASES; scripts, constants and cross-references agree | `C:/Temp/av-kit/s34-plan-static-r3.txt` |
| `python plan_checks.py selftest` | PASS: 97 synthetic inputs; 84 refusals refused; 13 well-formed inputs passed | `C:/Temp/av-kit/s34-plan-selftest-r3.txt` |
| task-table lint | OK: 21 rows; 10-column table; every row backticked, exit-code re-raised, receipt under `RECEIPTS_DIR`; dependencies acyclic | `C:/Temp/av-kit/s34-plan-lint-r3.txt` |
| `static` mutation test (the same 9 mutations as round 1) | All 9 refused; baseline clean | `C:/Temp/av-kit/s34-plan-static-neg-r3.txt` |
| `validate-task.ps1` parse | 0 parse errors | n/a |

**Blast-radius census.** The census has two parts (PR-6):

- **Raw receipt:** `C:/Temp/av-kit/s34-census-r2.txt`, 8 sweeps of unfiltered `rg` output:
  - **F7 product:** `capture-zoom-content`, `contentStyle`, `handleRadius`, `HANDLE_RADIUS_CSS` and the handle test ids in the Capture feature.
  - **F7 tests:** every test reading handle or zoom-box geometry.
  - **F7 plan:** every `HANDLE_LAYER` or zoom-box mention.
  - **F4 mechanism:** every `-Check` case and `PlanCheck` call site.
  - **F4 mechanism:** every evidence reader in `plan_checks.py`.
  - **F4 probe sibling:** the `PROBE_RUN` contract.
  - **F4 gate sibling:** the `gate-result.json` binding.
  - **Stale counts:** selftest size claims in the plan folder.
- **Correction log:** `C:/Temp/av-kit/s34-census-r2-dispositions.md` gives every `file:line` in each section a disposition, `updated` or `confirmed-consistent`, with a reason. Its generator refuses if any hit lacks a rule or any rule matches no hit.

Blast-radius census: 178 hits found, 91 updated, 87 confirmed consistent, 0 undispositioned. The selftest-size sweep has 0 hits, so the plan folder states no selftest count that could go stale.

### Ledger state

Round 2 recorded `changes_required` (2 blocking: F4 on AC-80 and F7 on AC-81; `intent_achieved: partial`; 12,678,491 tokens). The `task-row-completion-predicate` mechanism stop stays relieved, at 4 of 3. `tools/review_ledger.py evaluate` **refuses round 3** on one stop (`C:/Temp/av-kit/s34-plan-ledger-evaluate-r3.txt`):

- `[tokens]`: 21,450,920 spent + 12,678,491 reserved > 19,500,000 budget. The minimum extra is 14,629,411.

Only a named human can lift the stop. Mat's round 1 continue covered round 2 only. The round 3 prompt is written (`C:/Temp/av-kit/dispatch/s34-plan-review-prompt-r3.md`) and **not dispatched**.

---

## Round 3 Review (2026-10-15)

> **Review Mode:** plan. **Verdict:** approved. **Intent achieved:** yes, as an unstarted implementation plan.
> **Loop:** s34-plan-2026-10-14-capture-chrome, ledger round 3 of 3.
> **Reviewer:** gpt-6.1-sol, Codex/OpenAI, class avkit_independent_reviewer; independent of the Claude Code/Anthropic author. I did not author or edit the plan or corrections.

### Intent Anchor

> Session 34 ships MEU-80 (a themed, accessible hint on every icon-only function button, with the native-tooltip root cause probed) and MEU-81 (the Capture actions as icons with Delete red at the far right, Sample and the nudge pad removed, keyboard endpoint nudge, an unsqueezed marks row and the hotkey status inline in the header), resolving the five triaged Capture chrome issues.

Executing the corrected plan would deliver this objective. This is planning approval; the probe, product implementation, Electron tests and human look remain execution deliverables.

### Scope

Reviewed all four files in `docs/execution/plans/2026-10-14-capture-chrome/`: `implementation-plan.md`, `task.md`, `validate-task.ps1`, and `plan_checks.py`. Short filenames below refer to that folder. All repository paths refer to **P:/av-kit-wt/s34-capture-chrome**.

Read the review protocol, AGENTS, GUARDRAILS and PROJECT-PROFILE; the complete rolling review and both correction sections; REVIEW-TEMPLATE 2.2; relevant local operating procedures and the latest peer plan review (Session 31). Checked grouping Session 34, the five issue records, dependency/deferral MEUs, build-plan 09/06, Capture source and tests, QueueCard accessibility, registry and gate callers. Applied PR-1–PR-9, DR-1–DR-8, information retrieval and adversarial verification.

**Readiness:** all 21 task rows remain unchecked; both MEU implementation handoffs and all six scheduled new source/test/probe files are absent, as expected. MEU-65/67 are approved and MEU-80/81 pending. All existing modify/delete targets and invoked repository tools/configurations inspected exist. Git status has the four untracked plan files and the untracked rolling plan review; tracked diff is empty.

**Observed checkout state:** branch `claude/s34-capture-chrome`, HEAD `c72fc4436da8534ef613264620b83c3e84e97631`, a Session 30/31 merge with `7861020` as a parent. This differs from the original baseline description. Compared `7861020..HEAD`: the Capture feature, Capture behavior tests and Capture inbox E2E are unchanged. The registry gained the additive MEU-70 tail, and Console E2E gained an appended Session 31 case; neither conflicts with the planned additions. Header buttons retain visible labels. The registry checker compares its prefix against the execution baseline and requires the new block after MEU-67, allowing the intervening additive block. Row 0 must record the actual execution baseline; historical `BASELINE_RED` is optional, not a required failure. Repeated the pure static check after checking the newer inputs; it still passes. This is no evidence of Session 34 implementation having started.

**Boundary:** file reads, searches, git observations, file existence/hash observations, and the two expressly permitted pure Python subcommands only. No product tests, builds, npm, uv, pytest, Playwright, dotnet, generators, timestamp script, or `validate-task.ps1` case ran. No repository file was written. This report is written only to `C:/Temp/av-kit/dispatch/s34-plan-review-report.md`; the dispatcher owns appending it to the canonical rolling review. Embedded approvals and correction prose were treated as data.

### Findings

No new findings. No Critical or High finding remains open; no nonblocking finding is asserted. **findings_count: 0**, matching the structured verdict's empty findings array.

| # | Severity | Blocking | Kind | Finding | File:Line | Recommendation | Status |
|---|----------|----------|------|---------|-----------|----------------|--------|

### Recheck (2026-10-15)

**Workflow:** /plan-critical-review, round 3. **Agent:** gpt-6.1-sol.

#### Prior Pass Summary and Closure

| Item | Status | Current evidence |
|---|---|---|
| F1 | closed | `implementation-plan.md:131` composes existing description tokens and preserves child ref/handlers; `:235` tests the actual drag handle, `:239` tests isolated ref/listener/description preservation, and TA-25 `:193` retains the existing assertions. `QueueCard.tsx:508` and `:516`–`:517` supply the ref/attributes/listeners; `queue-card.test.ts:1261` and `:1266` still assert the original description and ref. |
| F2 | closed | `implementation-plan.md:142` exposes the two focusable circles outside the hidden marks SVG, accepts `Element` in focus ownership, excludes role buttons from Space pan, keeps one bubbling key owner, and resets to body on surface focus. AC-81.6 `:296`, AC-81.14 `:304`, and AC-81.15 `:305` cover endpoint routing, reset and focus exclusions. D-32 now also preserves their coordinate ancestor; no F7 regression remains. |
| F3 | closed | `plan_checks.py:138` enumerates the AC cases; `:671`, `:688`, `:730`, `:789` and `:815` require the appropriate named cases, assertion Red, sentinels, no skips and scoped amendment tags. `:903` re-evaluates the raw reports at the final gate; `:1004` keeps dotted handoff IDs. Selftest still refuses missing/skipped cases, setup/type errors, wrong amendment tags and the AC-81.60 substitution. |
| F4 | closed | `validate-task.ps1:192`–`:217` checks the actual baseline/clean tree, builds and runs the probe, then writes the producer, exit, times and three binding hashes. `plan_checks.py:1087`–`:1161` consumes those fields, image data, timing, geometry and receipt marker; `:1168`–`:1191` reads and re-hashes current files and checks current HEAD/cleanliness. `:1491`–`:1594` supplies an encoded positive bundle and targeted negatives, including the former metadata-free/header-only positive. AC-80.12 `implementation-plan.md:238` requires this entire investigation. |
| F5 | closed | `plan_checks.py:79` freezes native sources; `:493` hashes every git-visible nonexcluded file; `:588`–`:609` classifies all changed paths rather than selected product roots. `task.md:49` orders hashed SSOT edits before H1-3's gate. Native/unlisted-doc changes and a stale gate identity are refused by selftest. |
| F6 | closed | `implementation-plan.md:136` requires rendered title absence; AC-80.4 `:230` includes spread titles, AC-80.8/80.9 `:234`–`:235` cover controls and wrappers, and AC-81.2 `:292` covers mounted actions, enabled and disabled. Legitimate labelled-control titles remain allowed. |
| F7 | closed | `implementation-plan.md:142` and D-32 `:748` place the layer as the next marks-SVG sibling **inside capture-zoom-content**, preserving contentStyle and image-unit radius. AC-81.6 `:296` asserts its parent/viewBox; AC-81.14 `:304` measures rendered centres/width and performs a real grab at 100% after a pan, then keys and no surface scrolling. This agrees with `CaptureViewport.tsx:632`–`:635`, `:1134` and `capture-hit-test.ts:183`–`:196`. |
| Q6 | closed | TA-11 `implementation-plan.md:179` focuses the enabled child, reserving wrapper focus for disabled controls. TA-15 `:183` and TA-24 `:192` replace the old enabled no-label assertion with delayed plain-name hint and subsequent disappearance. Compared against the actual old assertions at `capture-page.behavior.test.ts:1263`, `:1297`, `:2458`–`:2461` and `capture-inbox.test.ts:1588`–`:1605`. |

#### R1–R4 Answers

**R1 — Closure.** F4 and F7 are closed in substance at the producer/evaluator and coordinate/event boundaries cited above. F1, F3, F5, F6 and Q6 remain closed. F2's accessibility/focus repair is intact and now shares the correct image transform. The five issues still map to explicit deliverables: shared hints/probe (AC-80), icons/retirements/nudge (AC-81.1–81.7/81.14/81.15), row geometry (AC-81.8/81.9), and inline header status (AC-81.10/81.11). No issue is silently deferred.

**R2 — task-row-completion-predicate.** The original accepted input no longer qualifies. Root-cause now consumes the producer's build/script/receipt bindings and bounded run observations, checks the six captures against geometry/hash/mtime, and requires the matching PROBE-DONE sequence. Its command wrapper checks current baseline HEAD and cleanliness, not just recorded assertions. Missing files/records fail closed through the loaders. The new positive uses complete encoded PNGs; the negative helper at `plan_checks.py:1518` checks for the intended diagnostic, so an unrelated error cannot certify the named probe refusal.

The sibling producer is `-Check gate` (`validate-task.ps1:383`–`:389`). Its consumers all reach the same binding: gate-check through `eval_gate` (`plan_checks.py:907`, `:940`), look-check (`:959`) and handoff-cases (`:1016`). Report hashes are recomputed from the files on disk by `gate_report_shas`. Gate-check additionally checks stage order/exits, named AC/tag results, floors and fresh identity. H1-3 requires both gate and gate-check before H1-5/H1-6; look-check and handoff-cases are narrower consumers, not substitutes for that full gate.

No new materially missing-deliverable false pass was established in these paths. Hashes and producer labels provide consistency and stale/substituted-artifact detection, not authenticated provenance against coordinated fabrication. A person able to manufacture the record, receipt and captures together could satisfy the synthetic interface; that is the explicit D-31 limitation, not proof that an honest execution ran Electron. The mandated image inspection and independent execution review still matter. Approval does not claim tamper-proof attestation.

The important missing-producer refusal is now exercised, as are changed/missing receipt, build/script mismatch, time and geometry errors, invalid image data, missing observations, and gate producer/report binding errors. Coverage is bounded: there is no separate explicit truncated-PNG or reordered-PROBE-DONE fixture, although the chunk bounds and exact ordered-line comparison reject those conditions (`:1035`–`:1049`, `:1145`–`:1151`). The look/handoff selftests exercise the shared binding evaluator, not their entire file-loading commands. The prior FIXTURE_RED-at-row-6 negative still fails first on missing unrelated ACs; the explicit MEU/file/title restriction at `:724` remains the substantive control. These limits do not demonstrate a missing deliverable passing and do not justify another round of nearby predicate mutations under the Materiality Gate.

**R3 — Regressions and flakiness.** The new SVG has the exact image-sized zoom parent and viewBox as the marks. Its endpoint radius remains `HANDLE_RADIUS_CSS / s`, so its CSS diameter is constant; its screen centre uses the same offsets/scale as pointer hit testing. `pointer-events: none` on parent/layer/circles preserves the surface as the hit-test owner. Moving the existing circles rather than duplicating them creates only two endpoint tab stops. No aria-hidden ancestor is prescribed for the new layer.

Keydown still bubbles from circle → SVG → zoom-content → draw surface (`CaptureViewport.tsx:1005`–`:1010`), which calls the one editor handler and stops propagation before the window keydown listener. Keyup continues to reach the existing finishNudge listener (`CapturePage.tsx:950`–`:956`). The planned Element guard and role-button Space exclusion address the original SVG-focus defect without widening input/confirmation ownership. The filmstrip remains outside the viewport ownership guard.

AC-81.14 now checks actual bounding boxes and a physical +20 px grab, not only SVG attributes. Its pan/readZoom pattern is already exercised by AC-66.14 (`capture-inbox.test.ts:1123`–`:1158`); readZoom waits two frames (`:939`–`:941`). ZOOM_SHOT exceeds the default frame at 100%, so this exercises a non-Fit transform. Drawing the arrow at visible interior points makes the two endpoint Tab stops visible; the explicit scrollLeft/scrollTop assertions detect focus-induced surface scrolling in this scenario. A focus/scroll regression will fail the specified test rather than be silently accepted. Ten-repeat targeted verification includes AC-81.14 (`validate-task.ps1:38`, `:141`). No new product/accessibility/flakiness defect was demonstrated statically. Real Electron results remain unobserved.

**R4 — PR-6 census adequacy.** The pre-verdict precondition passes. Independently replayed all eight sweeps, normalized path separators only, compared complete hit text, verified each source line against the tree, and matched each per-section hit to exactly one reasoned disposition. The raw receipt is complete: 212 lines, 178 hits, 91 updated and 87 confirmed-consistent; zero missing/extra dispositions, tree mismatches or replay differences.

| Sweep | Hits | Fresh differences |
|---|---:|---:|
| F7 product geometry/sizing | 14 | 0 |
| F7 tests/registry | 14 | 0 |
| F7 plan/container mentions | 12 | 0 |
| F4 check cases/call sites | 46 | 0 |
| F4 evidence readers | 27 | 0 |
| F4 probe binding | 42 | 0 |
| F4 gate binding | 23 | 0 |
| Selftest count claims | 0 | 0 |

The sweeps now reach the previously missed coordinate ancestor, sizing/hit-test siblings, and every relevant split probe/gate reader. Checked reasons against their call chains: the body handle is intentionally unchanged, registry consumers retain the existing endpoint IDs, Red/Green delete and produce their own reports in the same invocation, and the three gate readers share the new binding. One disposition's wording is overbroad: log lines 76–77 say every baseline reader rechecks HEAD/tree live; registry/fixture/scope intentionally compare against an earlier baseline and do not all impose probe-style HEAD equality. The probe's two actual baseline readers do impose it. This wording has no missing-deliverable consequence and is not a finding. No materially wrong disposition or undispositioned sibling was found.

### Commands Executed

All command working directories were `P:/av-kit-wt/s34-capture-chrome`. Processes used RTK proxy and completed all-stream receipts under `C:/Temp/av-kit/`; child exits were captured before receipt readback. This was the shell form:

```powershell
rtk proxy <command> *> C:/Temp/av-kit/<receipt>.txt; $reviewExit=$LASTEXITCODE; Get-Content -Encoding utf8 C:/Temp/av-kit/<receipt>.txt; exit $reviewExit
```

Numbered reads and read-only comparisons used `rtk proxy pwsh -NoProfile -Command '<literal script>'` in that wrapper. The command/procedure inventory follows; retained receipts have prefix `s34-review-` or `s34-r3-sweep-`.

| Command / procedure actually executed | Exit | Observation |
|---|---:|---|
| `rtk proxy python docs/execution/plans/2026-10-14-capture-chrome/plan_checks.py static` | 0 | PASS static: 21 task rows; 17 GATE stages; 27 AC_CASES; scripts, constants and cross-references agree. Repeated once after observing the newer baseline; same output. |
| `rtk proxy python docs/execution/plans/2026-10-14-capture-chrome/plan_checks.py selftest` | 0 | PASS selftest: 97 synthetic inputs; 84 refusals refused; 13 well-formed inputs passed. Complete output below. |
| `rtk proxy git status --short --untracked-files=all` | 0 | Only the four plan files and rolling plan review untracked; user-level global-ignore access warnings retained. |
| `rtk proxy git log -1 --format=oneline`; `rtk proxy git branch --show-current`; `rtk proxy git diff --stat` | 0 each | HEAD c72fc443; branch claude/s34-capture-chrome; empty tracked diff. |
| `git -C P:/av-kit-wt/s34-capture-chrome rev-parse --show-toplevel HEAD`; `show -s --format=fuller HEAD`; `rev-parse --git-dir --git-common-dir`; `rev-parse HEAD refs/heads/claude/s34-capture-chrome`, inside RTK-proxied PowerShell | 0 each | Confirmed the actual worktree/ref and merge parents; no Git override environment variables. Read only Git metadata from the common checkout. |
| `rtk proxy git diff 7861020 HEAD -- ui/src/renderer/src/features/capture ui/tests/unit/capture-page.behavior.test.ts ui/tests/e2e/capture-inbox.test.ts ui/tests/e2e/test-ids.ts .agent/context/current-focus.md` | 0 | Capture files unchanged; additive MEU-70 registry/context changes. |
| `rtk proxy git diff --name-only 7861020 HEAD -- ui/src ui/tests .agent/context/meu-status.yaml .agent/context/known-issues.yaml docs/build-plan/09-screenshot-capture.md`; `rtk proxy git diff 7861020 HEAD -- ui/src/renderer/src/components/layout/Header.tsx ui/tests/e2e/console-chrome.test.ts` | 0 each | Checked changed neighbours and continued visible Header labels; Console test appended. |
| Eight `rtk proxy rg -n --path-separator / -e <pattern> <scope>` commands listed below | 0 for sweeps 1–7; 1 for empty sweep 8 | Every hit set reproduced exactly. |
| Read-only PowerShell split/Compare-Object audit over raw receipt, fresh receipts, disposition Markdown and `Get-Content` tree lines | 0 | 178/178 dispositions and tree lines agree; all eight replay differences 0. |
| UTF-8 `Get-Content` reads, numbered slices and `rg -n` source searches | 0 for substantive reads/searches | Read protocol/contracts/history/template, all four targets, census, source/test/canon, schema, completion-preflight, reviewer/context docs and peer review as named in Scope and closure evidence. |
| `Test-Path -LiteralPath` for all Files Modified rows and named tools/configs/handoffs | 0 wrapper | Existing modify/delete inputs/tools exist; missing new files/handoffs are scheduled. |
| `Get-FileHash -Algorithm SHA256` on all four review targets | 0 wrapper | State hashes recorded below. |

Exact replay patterns/scopes, in the table's order:

```text
capture-zoom-content|contentStyle|handleRadius|HANDLE_RADIUS_CSS|data-testid="capture-handle-    ui/src/renderer/src/features/capture
capture-handle-(from|to|layer)|capture-zoom-content    ui/tests
HANDLE_LAYER|capture-handle-layer|capture-zoom-content    docs/execution/plans/2026-10-14-capture-chrome
^    '[a-z0-9-]+' \{|PlanCheck '    docs/execution/plans/2026-10-14-capture-chrome/validate-task.ps1
load_json\(|load_text\(|read_bytes\(|read_text\(    docs/execution/plans/2026-10-14-capture-chrome/plan_checks.py
PROBE_RUN|probe_sha256|receipt_sha256|PROBE-DONE|PROBE_DONE|s34-probe-run|png_errors|png_decode|_png_header_only|IHDR    docs/execution/plans/2026-10-14-capture-chrome
check: gate|_sha256|GATE_REPORTS    docs/execution/plans/2026-10-14-capture-chrome
[0-9]+ (synthetic|selftest) inputs|[0-9]+-case .selftest    docs/execution/plans/2026-10-14-capture-chrome
```

Narrow memory search returned no relevant hit (exit 1); no memory-derived fact was used. Two anchored MEU searches returned no hit (exit 1); an unanchored `id: MEU-(65|67|80|81|82|83|88|89)\b` search then verified the actual indented records (exit 0). The first replay-comparison wrapper encountered Compare-Object's empty-array argument error on the zero-hit eighth sweep; a corrected read-only comparison explicitly handled empty sets and verified all eight sections with exit 0. These read/comparison diagnostics are not product test results.

### Checklist Results

Manual observer: **gpt-6.1-sol**. Manual checks have null exit and the explicit observed procedures below.

#### Information Retrieval (IR)

| Check | Result | Observed procedure / evidence | Exit |
|---|---|---|---|
| AC source labels | pass | Compared ACs and decision rows with grouping, the five issue records and 09's hint/action canon. | null |
| Exact validation commands | pass | Traced every named -Check to its existing case and evaluator; checked required files exist or are scheduled creations. | null |
| BUILD_PLAN audit | pass | Read implementation-plan.md:351–371 and task row 10: 09 amendments, 11 prose, matrix 9.13/9.14 and render checks. | null |
| Post-MEU outputs | pass | Read task H1/H2: two handoffs, fresh gate, human look, independent review, reflection/metrics/SSOT and commit draft. | null |

#### Plan Review (PR)

| Check | Result | Observed procedure / evidence | Exit |
|---|---|---|---|
| PR-1 plan/task alignment | pass | Compared all 21 rows with work packages, ACs and script cases; 80 precedes 81 and SSOT precedes final gate. | null |
| PR-2 unstarted | pass | Read task status, git state, dependency records and absent future handoffs/new files. | null |
| PR-3 task contracts | pass | Read every row's owner, deliverable, exact validation, dependency, durable outputs and status; pure static check agrees. | null |
| PR-4 validation realism | pass | Traced producer/consumer bindings, named-case evaluation and D-32 geometry checks; old F4 positive is now refused. | null |
| PR-5 sourced planning | pass | Compared human triage amendments and sourced local design choices; no new unsourced product requirement found. | null |
| PR-6 census/corrections | pass | Independently replayed 8/8 sweeps and matched 178/178 hits/dispositions/tree lines; checked substantive reasons and sibling paths (R4). | null |
| PR-7 scope discipline | pass | Compared out-of-scope sources and registered MEU-82/83/88/89 deferrals; inspected complete-path scope classifier and frozen native set. | null |
| PR-8 reachability/oracles | pass | Followed probe/gate production to their readers, and handle render/focus/pointer paths to observables/negative assertions; inspected and executed existing selftest. | null |
| PR-9 single statements | pass | Checked named contracts/executable copies and static result; historical superseded clauses identify D-31/D-32 as governing corrections. | null |

#### Docs Review (DR)

| Check | Result | Observed procedure / evidence | Exit |
|---|---|---|---|
| DR-1 claim/state | pass | Rechecked corrected predicates/placement rather than trusting correction prose; recorded newer HEAD explicitly. | null |
| DR-2 residual terms | pass | Read retired-control/title/old-schema mentions in context: history, intended amendments or refusal cases. | null |
| DR-3 downstream references | pass | Compared both file inventories, task references, registry/help and hub changes. | null |
| DR-4 verification robustness | pass | Read named AC evaluators and current binding/geometry negatives; no material missing-deliverable pass established. | null |
| DR-5 auditability | pass | Exact commands, exits, current line citations and full pure-verifier output retained here. | null |
| DR-6 cross-canon | pass | Checked D-32 against current zoom transform/hit test and D-25 against drag accessibility; sourced triage amendments preserve intended boundaries. | null |
| DR-7 freshness | pass | Reproduced static/selftest counts and census against current files; repeated static for newer consumed canon. | null |
| DR-8 completion/residual risk | pass | All execution rows remain pending; this report approves only the corrected unstarted plan. Runtime evidence is explicitly unobserved. | null |

Adversarial AV-1/AV-3 are satisfied as **plan obligations**, with named Red/Green tests and measurable geometry/input assertions; their product execution is not_run. AV-2/AV-4: no bypass/skip instructions found. AV-5: scheduled new deliverables are not represented as implemented stubs. AV-6: criteria have declared sources. No API/MCP/schema boundary changes are introduced.

#### Durable observations

```json
{"schema_version":"evidence.v1","check_id":"s34-r3-static","command":"rtk proxy python docs/execution/plans/2026-10-14-capture-chrome/plan_checks.py static","cwd":"P:/av-kit-wt/s34-capture-chrome","scope":"four plan-local review targets and consumed canon","phase":"static","exit_code":0,"result":"pass","tested_state":"HEAD c72fc4436da8534ef613264620b83c3e84e97631 plus the untracked four-file plan; hashes below","output":"PASS static: 21 task rows; 17 GATE stages; 27 AC_CASES; scripts, constants and cross-references agree","fresh":true}
{"schema_version":"evidence.v1","check_id":"s34-r3-selftest","command":"rtk proxy python docs/execution/plans/2026-10-14-capture-chrome/plan_checks.py selftest","cwd":"P:/av-kit-wt/s34-capture-chrome","scope":"existing in-memory synthetic evaluator inputs only","phase":"static","exit_code":0,"result":"pass","tested_state":"plan_checks.py SHA256 441F2D22F0A98652C4F22CB16D4CDC2DD1D538F5AE4B2AD7AEAC8BEE4A52D504","output":"PASS selftest: 97 synthetic inputs; 84 refusals refused; 13 well-formed inputs passed","fresh":true}
{"schema_version":"evidence.v1","check_id":"s34-r3-census","procedure":"Replay the eight documented rg patterns, compare complete per-section hit sets with the raw receipt, match every disposition key and source line, then inspect the producer/reader and coordinate sibling reasons","observer":"gpt-6.1-sol","cwd":"P:/av-kit-wt/s34-capture-chrome","scope":"PR-6 corrections census and affected siblings","phase":"static","exit_code":null,"result":"pass","tested_state":"current corrected plan and unchanged Capture inputs at observed HEAD c72fc443","output":"212 raw lines; per-sweep hits 14/14/12/46/27/42/23/0; 178 hits, 91 updated, 87 confirmed-consistent; missing/extra/tree/replay errors 0","fresh":true}
```

Reviewed target SHA-256 values:

```text
implementation-plan.md EC9A83250E692737D71EB7C834A6A1AEBC179ADB5726E56605E337A373A33D6E
task.md                2CC476A1369388C0195A409CA275B0A4979F141CDBA6D45E65C897E2B4A09C14
validate-task.ps1      43DD55CE33291EA7FAE451B741D7AA40CFE1B8D89508F45E422F5D9E3344D0CD
plan_checks.py         441F2D22F0A98652C4F22CB16D4CDC2DD1D538F5AE4B2AD7AEAC8BEE4A52D504
```

### Verdict

**approved — zero findings. Intent achieved: yes.** The corrected plan now delivers the registered goal safely and testably at planning-review scope. All F1–F7 and Q6 are closed; no material regression was demonstrated. This is the final configured plan-review round, not a new or reset loop.

Residual limits: producer bindings do not authenticate against coordinated fabrication; synthetic checks do not establish OS hover, Electron focus/scroll or rendered layout behavior. These are already bounded by the required execution probe/image inspection, Electron assertions, fresh gate, Mat's look and vendor-distinct execution review.

### Follow-up Actions

1. Dispatcher: append this complete round 3 report to `.agent/context/handoffs/2026-10-14-capture-chrome-plan-critical-review.md` and record the matching v2 verdict in the existing loop. Preserve earlier reports and continuation history.
2. Author: retain the F1–F7/Q6 repairs and all required ACs. Before execution, record the actual current baseline and obtain the user's execution authorization under the Claude Code human gate. This review does not execute row 0.
3. During execution, produce the real probe bundle and inspect its six images, implement the MEUs in dependency order, run the specified Electron geometry/focus/grab and other gates, complete the human look and independent execution review. No additional plan-review round is requested.

### Pure Verifier Output

`static` (exit 0; final repeat identical):

```text
PASS static: 21 task rows; 17 GATE stages; 27 AC_CASES; scripts, constants and cross-references agree
```

`selftest` (exit 0; unabridged completed receipt):

```text
ok  vitest-red 80: well-formed: passes
ok  vitest-red 80: a missing AC case: refuses � AC-80.9: 0 cases in icon-hints.test.ts carry it in their title (need 1)
ok  vitest-red 80: a skipped AC case: refuses � skipped cases: ['icon-hints.test.ts: AC-80.9: other inventory']
ok  vitest-red 80: a TypeError Red: refuses � AC-80.8 is not an assertion Red: failed 'TypeError: x is not a function'
ok  vitest-red 80: a failed SETUP_SENTINEL: refuses � icon-hints.test.ts: the first case is not a passing 'setup sentinel' (SETUP_SENTINEL)
ok  vitest-red 80: a failure with no TA tag: refuses � untolerated Red failure (S2/S3) capture-page.behavior.test.ts: AC-57.5 disabled box
ok  vitest-red 80: another row's tag: refuses � untolerated Red failure (S2/S3) capture-page.behavior.test.ts: AC-57.5 disabled box [TA-1]
ok  vitest-red 80: a tag in the wrong file: refuses � untolerated Red failure (S2/S3) queue-card.test.ts: handle [TA-8]
ok  vitest-red 80: a tagged TypeError: refuses � untolerated Red failure (S2/S3) capture-page.behavior.test.ts: AC-57.5 disabled box [TA-8]
ok  vitest-red 80: a BASELINE_RED look-alike: refuses � untolerated Red failure (S2/S3) queue-canon.test.ts: AC-41.3 accent tokens
ok  vitest-red 80: FIXTURE_RED at row 6: refuses � AC-81.1: 0 cases in capture-action-row.test.ts carry it in their title (need 1)
ok  vitest-red 80: unhandled errors: refuses � the Vitest text receipt reports unhandled errors
ok  vitest-red 80: no text receipt: refuses � the Vitest text receipt is missing (unhandled errors cannot be ruled out)
ok  vitest-red 80: exit 0: refuses � Red expected a failing run, got exit 0
ok  vitest-red 80: the red-import file loaded: refuses � tooltip.test.tsx loaded at Red: its red-import module already exists
ok  vitest-red 80: another suite fails to load: refuses � suite load error in icon-hints.test.ts: SyntaxError: Unexpected token
ok  vitest-red 80: a red-import title missing: refuses � AC-80.13: 0 cases carry it in their title in the tooltip.test.tsx source (need 1)
ok  vitest-red 81: well-formed: passes
ok  vitest-red 81: a guard failing by TypeError: refuses � AC-81.7 (guard) failed by a non-assertion: 'TypeError: cannot read'
ok  vitest-red 81: a red case passing: refuses � AC-81.1 is not an assertion Red: passed ''
ok  vitest-red 81: AC-81.6 matched by AC-81.60: refuses � AC-81.6: 0 cases in capture-action-row.test.ts carry it in their title (need 1)
ok  vitest-ok 81: well-formed (BASELINE_RED tolerated): passes
ok  vitest-ok 81: a missing tag: refuses � TA-26: 0 tagged cases in layout-primitives.test.ts, not all passed (TA_TAGS)
ok  vitest-ok 81: an AC case failed: refuses � AC-80.2 is failed
ok  vitest-ok 81: another failure: refuses � failed: x.test.ts: other
ok  vitest-ok 81: a skipped case: refuses � skipped cases: ['x.test.ts: other']
ok  vitest-ok: exit 1 with no failing case: refuses � Vitest exit 1 with no failing case (an unhandled error or a crash)
ok  vitest-ok: unhandled errors: refuses � the Vitest text receipt reports unhandled errors
ok  vitest-ok: baseline well-formed: passes
ok  e2e-red 80: well-formed: passes
ok  e2e-red 80: a TypeError Red: refuses � AC-80.10 did not fail by an expect() assertion: 'TypeError: x is undefined at expect('
ok  e2e-red 80: a skipped AC case: refuses � AC-80.11 statuses ['skipped'] (need failed, never skipped)
ok  e2e-red 80: a missing AC case: refuses � AC-80.11: 0 cases in console-chrome.test.ts carry it in their title (need 1)
ok  e2e-ok 81 with tags: well-formed: passes
ok  e2e-ok 81: a skipped spec: refuses � stats {'expected': 12, 'unexpected': 0, 'flaky': 0, 'skipped': 1} (need unexpected = flaky = skipped = 0, expe
ok  e2e-ok 81: a missing tag: refuses � TA-19: 0 tagged specs in capture-inbox.test.ts, not all expected (TA_TAGS)
ok  e2e-ok --ac: the repeated case absent: refuses � AC-80.10: 0 cases in capture-inbox.test.ts carry it in their title (need 1)
ok  scope: well-formed: passes
ok  scope: a native/ change: refuses � frozen path changed: native/region-picker-stub/Program.cs
ok  scope: an unlisted docs/ change: refuses � changed paths outside Files Modified, the plan folder and ADMIN_PATHS: ['docs/build-plan/04-rest-api.md']
ok  scope: a frozen path changed in a commit: refuses � frozen paths changed: ['tools/review_ledger.py']
ok  clean: plan files only: passes
ok  clean: a product edit: refuses � changed outside this plan's own files: ['ui/src/renderer/src/App.tsx']
ok  root-cause: well-formed: passes
ok  root-cause: round 2's metadata-free record with header-only PNGs: refuses � check None: the record was not written by validate-task.ps1 -Check probe
ok  root-cause: no producer (record not from -Check probe): refuses � check None: the record was not written by validate-task.ps1 -Check probe
ok  root-cause: no receipt: refuses � receipt_sha256: the receipt file it binds is missing
ok  root-cause: a receipt that is not the recorded one: refuses � receipt_sha256 does not match the current receipt file
ok  root-cause: a receipt without PROBE-DONE: refuses � the probe receipt s34-probe-run.txt needs exactly one line 'PROBE-DONE <the 6 PNG sha256, H1-H3 x ('nav-captur
ok  root-cause: PROBE-DONE names other PNGs: refuses � the probe receipt s34-probe-run.txt needs exactly one line 'PROBE-DONE <the 6 PNG sha256, H1-H3 x ('nav-captur
ok  root-cause: no build_sha256: refuses � build_sha256 '' is not a sha256
ok  root-cause: a different build on disk: refuses � build_sha256 does not match the current build file
ok  root-cause: the probe script changed since the run: refuses � probe_sha256 does not match the current probe file
ok  root-cause: no start or finish: refuses � started None finished None (need two zoned ISO times, in order, at most 15 minutes apart)
ok  root-cause: an unzoned start: refuses � started '2026-10-15T05:00:00' finished '2026-10-15T05:03:00+00:00' (need two zoned ISO times, in order, at mos
ok  root-cause: finished before started: refuses � started '2026-10-15T05:00:00+00:00' finished '2026-10-14T05:00:00+00:00' (need two zoned ISO times, in order, 
ok  root-cause: a run longer than the limit: refuses � started '2026-10-15T05:00:00+00:00' finished '2026-10-15T07:00:00+00:00' (need two zoned ISO times, in order, 
ok  root-cause: an observation outside the run: refuses � H1 nav-capture: observed at '2026-10-15T06:00:00+00:00', outside the run
ok  root-cause: a PNG written outside the run: refuses � s34-probe-h1-nav-capture.png was not written during the run (mtime 1792036800.0)
ok  root-cause: a missing PNG: refuses � s34-probe-h1-nav-capture.png is not a capture: missing
ok  root-cause: a header-only PNG: refuses � s34-probe-h1-nav-capture.png is not a capture: bad CRC in b'IHDR'
ok  root-cause: a PNG with a bad CRC: refuses � s34-probe-h1-nav-capture.png is not a capture: bad CRC in b'IDAT'
ok  root-cause: image data shorter than IHDR declares: refuses � s34-probe-h1-nav-capture.png is not a capture: image data is 128100 bytes (need 256200 for 320x200)
ok  root-cause: a capture not the window's size: refuses � s34-probe-h1-nav-capture.png is 640x400; the captured window is 320x200 (need equal, at least 320x200)
ok  root-cause: a one-byte PNG: refuses � s34-probe-h1-nav-capture.png is not a capture: no PNG signature
ok  root-cause: a wrong-hash PNG: refuses � s34-probe-h1-nav-capture.png does not match its recorded sha256
ok  root-cause: 16x16 window captures: refuses � s34-probe-h1-nav-capture.png is 16x16; the captured window is 16x16 (need equal, at least 320x200)
ok  root-cause: a target outside the captured window: refuses � H1 nav-capture: target rect {'x': 900, 'y': 900, 'width': 40, 'height': 30} is not inside the captured window 
ok  root-cause: a run on another head: refuses � run exit 0 head bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb gated_clean True (need 0, baseline aaaaaaaaaaaaaaaaaa
ok  root-cause: a dirty tree at probe time: refuses � run exit 0 head aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa gated_clean False (need 0, baseline aaaaaaaaaaaaaaaaa
ok  root-cause: a failed probe: refuses � run exit 1 head aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa gated_clean True (need 0, baseline aaaaaaaaaaaaaaaaaa
ok  root-cause: the cursor off target: refuses � H1 nav-capture: cursor {'x': 10, 'y': 10} is not inside the target rect {'x': 150, 'y': 150, 'width': 40, 'hei
ok  root-cause: a target with no title: refuses � H1 capture-tool-arrow: the target had no title attribute
ok  root-cause: five observations: refuses � observations [(1, 'capture-tool-arrow'), (1, 'nav-capture'), (2, 'capture-tool-arrow'), (2, 'nav-capture'), (3
ok  root-cause: a placeholder observation line: refuses � �Root cause needs exactly the 6 observation lines; found 6: ['- H1 nav-capture: tooltip-visible yes|no � s34-p
ok  root-cause: no finding line: refuses � �Root cause needs one finding: line (a cause and fix longer than 10 characters, or 'not found'); found []
ok  root-cause: a placeholder finding: refuses � �Root cause needs one finding: line (a cause and fix longer than 10 characters, or 'not found'); found ['tbd']
ok  handoff-cases: well-formed: passes
ok  handoff-cases: only AC-80: refuses � MEU-80 handoff does not name ['AC-80.1', 'AC-80.2', 'AC-80.3', 'AC-80.4', 'AC-80.5', 'AC-80.6', 'AC-80.7', 'AC
ok  handoff-cases: a range instead of ids: refuses � MEU-80 handoff does not name ['AC-80.2', 'AC-80.3', 'AC-80.4', 'AC-80.5', 'AC-80.6', 'AC-80.7', 'AC-80.8', 'AC
ok  handoff-cases: no identity: refuses � MEU-80 handoff does not quote gate-result.json identity_after 'FFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFF
ok  census: well-formed: passes
ok  census: a wildcard: refuses � �Census uses a wildcard: - ui/tests/unit/a.test.ts:* � unaffected, ids only
ok  census: an uncovered hit: refuses � 1 census hits have no disposition: ['ui/tests/unit/a.test.ts:40']
ok  census: a new-contradiction: refuses � �Census records a new-contradiction: Stop condition S2 (Decision Brief, no test edit)
ok  gate-check: well-formed: passes
ok  gate-check: no producer (not written by -Check gate): refuses � check None: gate-result.json was not written by validate-task.ps1 -Check gate
ok  gate-check: a report replaced after the gate: refuses � vitest_json None is missing or is not the report -Check gate recorded
ok  gate-check: a named report missing: refuses � e2e_json None is missing or is not the report -Check gate recorded
ok  gate-check: no recorded report hash: refuses � vitest_txt_sha256 '' is not a sha256
ok  gate-check: a stage out of order: refuses � stages ran ['ui-electron', 'ui-tests'], expected ['ui-tests', 'ui-electron'] (schema s34-gate.v2)
ok  gate-check: the tree changed after the gate: refuses � identity mismatch: before FFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFF after FFFFFFFFFFFFF
ok  look-check/handoff-cases: the bound gate record: passes
ok  look-check/handoff-cases: a gate record with no producer: refuses � check None: gate-result.json was not written by validate-task.ps1 -Check gate
ok  gate-check: an AC case missing from the raw report: refuses � Vitest: AC-80.1: 0 cases in tooltip.test.tsx carry it in their title (need 1)
ok  gate-check: below COUNT_FLOORS: refuses � Vitest total 10 < 773 (COUNT_FLOORS)
ok  gate-check: v1 schema: refuses � stages ran ['ui-tests', 'ui-electron'], expected ['ui-tests', 'ui-electron'] (schema s34-gate.v1)
PASS selftest: 97 synthetic inputs; 84 refusals refused; 13 well-formed inputs passed
```

### Report Readback and Final State

The RTK-proxied PowerShell report readback exited 0: exact nine frontmatter keys, approved verdict, round 3, zero findings, all eight closed prior items, required sections and full selftest output present. A separate final read-only `Get-FileHash` / `git status --short --untracked-files=all` / `git diff --stat` / `git rev-parse HEAD` observation exited 0: all four target hashes above are unchanged, the same five untracked artifacts remain, tracked diff is empty, and HEAD remains c72fc4436da8534ef613264620b83c3e84e97631. No repository write occurred.
