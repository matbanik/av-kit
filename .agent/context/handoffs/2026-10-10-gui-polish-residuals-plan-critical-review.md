---
date: "2026-10-10"
review_mode: plan
target_plan: docs/execution/plans/2026-10-10-gui-polish-residuals/implementation-plan.md
verdict: approved
findings_count: 1
round: 2
template_version: "2.2"
requested_verbosity: standard
agent: gpt-6.1-sol
---

# Critical Review: 2026-10-10-gui-polish-residuals

> **Review Mode:** `plan`  
> **Verdict:** `changes_required`  
> **Reviewer:** Codex, `gpt-6.1-sol`, class `avkit_independent_reviewer`; author Claude Code / Anthropic. I did not author or edit the plan.

## Intent Anchor

> Session 31 delivers MEU-69 (header Console toggle state, Commands palette button) and MEU-70 (Settings trailing-section rail fix and current-section emphasis), UI only, with no change outside ui/ and the two hub docs.

**Intent achieved:** partial. The header contract is workable, and the rail/spacer design has a real production path, but executing the plan exactly cannot complete the staged MEU-70 gate and does not deliver emphasis for the supported Startup section.

## Findings

| F1 | High | yes | behavior | The rail-only Green gate runs AC-70.5 before emphasis is implemented. Row 5 writes AC-70.5 into settings-rail.test.tsx; green70-rail runs that entire suite via REGSET at row 6, while ACTIVE_SOURCE and SECTION_EMPHASIS are deferred to dependent row 7. The required data-current and emphasis assertions therefore cannot pass at row 6. | `docs/execution/plans/2026-10-10-gui-polish-residuals/validate-task.sh:391; task.md:42-44; implementation-plan.md:221` | Separate or select the rail/spacer ACs and unchanged regression cases for green70-rail, then run AC-70.5 after row 7. Preserve all assertions and the rail-before-emphasis order. | open |
| F2 | High | yes | behavior | The supported Startup section has no planned emphasis producer. SettingsPage renders StartAtSignInControl directly, and that component owns its own startup section instead of using SettingsSectionFrame. The plan only adds current to SettingsSectionFrame and omits StartAtSignInControl from its strict Files Modified inventory. When startup becomes the rail's active key, the right panel has no matching data-current section or emphasis. | `docs/execution/plans/2026-10-10-gui-polish-residuals/implementation-plan.md:128-129,247-257; ui/src/renderer/src/features/settings/SettingsPage.tsx:934; ui/src/renderer/src/features/settings/StartAtSignInControl.tsx:79-83` | Plan a UI-only current-state and shared emphasis path for StartAtSignInControl, include every required source file in PRODUCT_SCOPE, and add a supported-login-item integration case that activates Startup and checks the same single-current and reserved-geometry invariants. | open |
| F3 | Medium | no | behavior | NO_SHIFT compares a scroll round-trip rather than geometry under different current sections. Scrolling back to the top normally makes Download current again, so both snapshots can match even if Capture's heading and downstream content move while Capture is current. This is a verification-quality gap; the specified always-reserved geometry and human K5 check remain sound independent safeguards. | `docs/execution/plans/2026-10-10-gui-polish-residuals/implementation-plan.md:131,222` | Compare document-relative heading geometry while Capture is still current, correcting viewport coordinates with main.scrollTop and main's origin, and assert the two samples have different active keys. Keep the 0.5 px tolerance and an explicit state-dependent geometry negative. | open |
| F4 | Low | no | clerical | The local GATE request restates the COUNT_FLOORS literals and DEFAULT_WINDOW dimensions instead of referring to the named contracts. The current copies agree; only the plan/script floor copies are bound by plan_checks.py, so this is clerical duplication under PR-9. | `docs/execution/plans/2026-10-10-gui-polish-residuals/local-requests.md:115,123; implementation-plan.md:125,135` | Reference COUNT_FLOORS and DEFAULT_WINDOW in the durable request; retain the plan as the prose definition and the statically bound script literals as executable copies. | open |

**Confidence:** High for F1–F4. **Subjects:** F1 committable-tooling; F2–F3 deliverable; F4 review-scaffolding. **Violated contracts:** F1 — AC-70.5, task rows 5→6→7, PR-1/PR-4; F2 — AC-70.5, ACTIVE_SOURCE, SECTION_EMPHASIS, and 11-page-layout.md:142; F3 — the strength of AC-70.6's geometry measurement; F4 — PR-9. The structured ledger citations for F1/F2 are `AC-70`, the registered prefix; the precise subcriteria are named here and in the findings.

There are **two blocking High findings**, no Critical findings. F3 is a nonblocking Medium verification-quality issue: the prescribed reserved geometry and the independently required K5 human observation remain safeguards. F4 is clerical and does not affect this verdict. No control-defeat mechanism finding is asserted.

### Decisive static traces

- **F1:** task.md:42 writes all AC-70.1–70.6 assertions before production changes. Plan:256 places AC-70.5 in `settings-rail.test.tsx`. The `REGSET` array includes that file (`validate-task.sh:291`), and `green70-rail` executes the entire array without a title filter (`:391`). Row 6 is explicitly rail/spacer only; dependent row 7 first implements current reporting and emphasis. An unchanged AC-70.5 starts by requiring one `data-current` section, so it still fails before row 7. This is a semantic dependency defect despite the structurally acyclic task graph; it is not a test result obtained by running the suite.
- **F2:** `SettingsPage.tsx:934` mounts `StartAtSignInControl` directly. `StartAtSignInControl.tsx:79-83` owns `<section data-testid="start-at-sign-in-panel" data-settings-section="startup" ...>` with its own class string. It neither uses `SettingsSectionFrame` nor accepts a current prop. The plan modifies only the page's frame and rail, while its strict Files Modified inventory excludes this component. The rail includes Startup when available (`SettingsPage.tsx:362`), so selecting that live key ends the emphasis chain with no producer. The existing supported fixture (`settings-rail.test.tsx:218-227`) verifies the panel/entry/caption, not the new emphasis; the default fixture and unpackaged Electron seam omit Startup.
- **F3:** `NO_SHIFT` samples at scroll top, activates Capture by scrolling, returns to scroll top, then samples. The existing observer makes Download current again there (`settings.test.ts:250-254` explicitly expects that). A state-dependent extra 4 px top padding on Capture can move its heading and downstream content while Capture is current, then disappear when Download is current; both final snapshot sets are equal. Required class tokens can still be present. The comparison is useful for persistent damage after a round-trip, but does not measure the transient invariant it claims.
- **F4:** `local-requests.md:115` repeats 748/127 and `:123` repeats 1280×800. These agree today with `COUNT_FLOORS` / `DEFAULT_WINDOW`; `plan_checks.py` binds the executable floor copies, not this request prose. Collapse the prose copies to named references.

## Scope

**Targets:** `implementation-plan.md`, `task.md`, `validate-task.sh`, `validate-task.ps1`, `plan_checks.py`, `human-gate-decision.md`, `human-review-decision.md`, `local-requests.md`, and the invoked `review-prompt-plan.md`, all in the Session 31 plan folder.

**Canon sampled:** both specified GUI hub sections, ST1–ST5, the Session 31 grouping and D-1–D-7, both issue records, Session 27 R4/A-6, and the approved Session 29 peer plan, scripts and round-2 review. Production and test reads cover the requested Header/AppShell/Button and Settings files, Console/Settings unit and Electron tests, test IDs, router and console palette registry; the additional Startup component is necessary to test the universal section claim.

**Reviewed state:** HEAD `3e654999a7f1dd01f7c96abcaa2ce1032150d3c8`. All 20 task rows are `[ ]`; baseline.sha, walkthrough.md, both MEU handoffs and all three declared new product files are absent. The canonical Session 31 review does not exist; this is **round 1**, with no earlier findings to recheck. The ledger read reports zero recorded rounds and includes AC-69/AC-70 in its citable set.

**Write scope:** only `C:/Temp/av-kit/dispatch/s31-plan-review-report.md`. The dispatcher must copy this report verbatim to `.agent/context/handoffs/2026-10-10-gui-polish-residuals-plan-critical-review.md`. No repository files were written. Existing untracked `.claude/settings.local.json` was left untouched; git also emitted permission warnings for the user's global ignore file.

The quoted goal's product boundary is interpreted consistently with `PRODUCT_SCOPE`: UI product edits and the two hub docs, with the required plan/review/SSOT closeout artifacts separately enumerated. No backend, MCP, API/OpenAPI or main-process behavior change is planned.

## Commands Executed

Every shell process used unfiltered `rtk proxy`, all-stream receipts under `C:/Temp/av-kit/`, immediate `$LASTEXITCODE` capture and propagation. Commands below are actual commands executed; numbered file reads and existence checks were performed through PowerShell read-only loops.

| Command / observed procedure | Exit | Decisive result |
|---|---:|---|
| `rtk proxy python docs/execution/plans/2026-10-10-gui-polish-residuals/plan_checks.py static` | 0 | PASS static; 20 rows |
| `rtk proxy python docs/execution/plans/2026-10-10-gui-polish-residuals/plan_checks.py selftest` | 0 | Every injected defect detected |
| `rtk proxy git status --short` | 0 | Only the pre-existing untracked settings.local.json; global-ignore permission warnings retained |
| `rtk proxy git log -3 --format=%H:%s` | 0 | HEAD 3e654999…; plan/prompt commits 5be3f7a / 2ea8901 |
| `rtk proxy git log -4 --format=%h:%s -- ui/src/renderer/src/features/settings/SettingsRail.tsx ui/src/renderer/src/features/settings/StartAtSignInControl.tsx` | 0 | Latest rail change is 407db19, A-6 click-lock fix |
| `rtk proxy rg -n -C 7 'section\|data-settings-section\|start-at-sign-in-panel\|onAvailabilityChange\|return' ui/src/renderer/src/features/settings/StartAtSignInControl.tsx` | 0 | Separately owned Startup section at 79–83 |
| `rtk proxy rg -n -A 10 'id: .*MEU-(19\|26\|58\|67\|69\|70)' .agent/context/meu-status.yaml` | 0 | Relevant MEUs registered; MEU-69/70 pending |
| `rtk proxy rg -n '1280\|800\|1000\|748\|127\|16\|24\|0\\.5\|40 %\|40%\|border-l-2\|-mx-3\|Settings:\|AC-70.5' docs/execution/plans/2026-10-10-gui-polish-residuals/implementation-plan.md docs/execution/plans/2026-10-10-gui-polish-residuals/task.md docs/execution/plans/2026-10-10-gui-polish-residuals/local-requests.md` | 0 | Repeated-literal census retained unfiltered; F4 current copies agree |
| Manual numbered UTF-8 reads; regex extraction of invoked repo paths followed by `Test-Path -LiteralPath`; observer gpt-6.1-sol | null | Executables/configs/fixtures exist; missing product files are declared new; missing handoffs/gate/reflection are future deliverables |

The protocol bootstrap read completed with exit 0. Two subsequent child-PowerShell read commands initially failed with exit 1 because the outer shell expanded the child variables; rerunning those read-only loops with literal single-quoted child scripts completed with exit 0. A vocabulary-path search used an incorrect filename and returned exit 2; a read of the ledger's actual vocabulary path resolved it. These are read-command errors, not project validation failures.

No tests, builds, npm, uv, pytest, Playwright, generators, validate-task.sh checks, or timestamp script were run. The only Python executions were the two explicitly permitted verifier commands.

### Verifier output (current independent observation)

```text
$ rtk proxy python docs/execution/plans/2026-10-10-gui-polish-residuals/plan_checks.py static
PASS static: 20 task rows; scripts, plan cross-references and file targets agree
exit: 0

$ rtk proxy python docs/execution/plans/2026-10-10-gui-polish-residuals/plan_checks.py selftest
PASS selftest duplicate row id: ["duplicate row ids: ['0', '0', '1', '2', '3', '4', '5', '6', '7', '8', '9', 'H1-1', 'H1-2', 'H1-3', 'H1-4', 'H1-5', 'H1-6', 'H1-7', 'H2-1', 'H2-2', 'H2-3']"]
PASS selftest unknown check: ["task.md invokes validate-task.sh 'no-such-check', not a case label"]
PASS selftest swapped stage: ["stage order differs: sh=['npm-ci', 'mcp-npm-ci', 'py-lint', 'py-types', 'ui-types', 'ui-lint', 'mcp-types', 'py-tests', 'ui-tests', 'ui-build', 'ui-harness-build', 'mcp-build', 'mcp-tests', 'openapi', 'state-render', 'ui-electron', 'source-audit'] ps1=['npm-ci', 'mcp-npm-ci', 'py-types', 'py-lint', 'ui-types', 'ui-lint', 'mcp-types', 'py-tests', 'ui-tests', 'ui-build', 'ui-harness-build', 'mcp-build', 'mcp-tests', 'openapi', 'state-render', 'ui-electron', 'source-audit']"]
PASS selftest undefined AC: ['task.md references AC-70.99, which has no definition site (AC table row, decision_log id, ### heading, or grouping �8 row)']
PASS selftest changed floor: ["COUNT_FLOORS differ: plan=('748', '127') sh=('700', '127')"]
PASS selftest missing goal anchor: ['review-prompt-plan.md does not contain the ledger goal anchor (INTENT_BINDING)']
PASS selftest missing modify target: ["Files Modified 'modify' row names a missing file: ui/no/such/file.ts"]
PASS selftest: every injected defect was reported
exit: 0
```

The replacement character in the undefined-AC line is retained from the Windows receipt. These passes establish structural checks and their named negative fixtures, not product correctness or acceptance of this plan.

```json
{"schema_version":"evidence.v1","check_id":"plan-static","command":"rtk proxy python docs/execution/plans/2026-10-10-gui-polish-residuals/plan_checks.py static","cwd":"P:/av-kit","scope":"Session 31 plan-local verifier","phase":"planning","exit_code":0,"result":"pass","tested_state":"3e654999a7f1dd01f7c96abcaa2ce1032150d3c8; tracked review targets unmodified","output":"PASS static: 20 task rows; scripts, plan cross-references and file targets agree","fresh":true}
{"schema_version":"evidence.v1","check_id":"plan-selftest","command":"rtk proxy python docs/execution/plans/2026-10-10-gui-polish-residuals/plan_checks.py selftest","cwd":"P:/av-kit","scope":"Seven in-memory negative fixtures","phase":"planning","exit_code":0,"result":"pass","tested_state":"3e654999a7f1dd01f7c96abcaa2ce1032150d3c8; tracked review targets unmodified","output":"PASS duplicate row id / unknown check / swapped stage / undefined AC / changed floor / missing goal anchor / missing modify target; PASS selftest: every injected defect was reported","fresh":true}
{"schema_version":"evidence.v1","check_id":"manual-plan-review","procedure":"Read both FICs, all task rows and invoked plan-local files; trace REGSET selection, production active-state ownership including supported Startup, geometry contracts and cited canon; compare PR-1..PR-9 and DR-1..DR-8 as tabulated below.","observer":"gpt-6.1-sol","cwd":"P:/av-kit","scope":"Session 31 plan and sampled canon","phase":"planning","exit_code":null,"result":"fail","tested_state":"3e654999a7f1dd01f7c96abcaa2ce1032150d3c8; tracked review targets unmodified","output":"Two High delivery defects: row 6 selects AC-70.5 before row 7 implements it; Startup's separately owned section lacks the planned current/emphasis path. Nonblocking geometry measurement and literal-duplication notes are F3/F4.","fresh":true}
```

## Checklist Results

The following PR/DR entries are **manual static observations**, observer `gpt-6.1-sol`, exit `null`. Procedures are the numbered file/call-chain comparisons described above, not unexecuted product commands.

| Check | Result | Evidence |
|---|---|---|
| PR-1 Plan/task alignment | fail | AC-70.5 is written before row 6, selected by its gate, and implemented only in dependent row 7 (F1). |
| PR-2 Not-started confirmation | pass | 20 task rows remain unchecked; the new product files and execution artifacts are absent; no prior canonical review exists. |
| PR-3 Task contract completeness | pass | All 20 rows provide the required fields and preserved-exit receipt commands; structural dependencies resolve. |
| PR-4 Validation realism | fail | green70-rail cannot pass its future emphasis assertions at the prescribed stage (F1). |
| PR-5 Source-backed planning | pass | The behavior has Spec, Local Canon, Research-backed or Human-approved bases; TA-1 and TA-2 correct the two stale label expectations. |
| PR-6 Handoff/corrections readiness | pass | Both MEU handoffs and one rolling review per mode are explicit. This is round 1; the resubmission census gate is not applicable. |
| PR-7 Scope discipline | pass | The sole product deferral is Session 30's real MEU-67. Other exclusions are supported; product edits are constrained to UI and the two hubs, with normal governance closeout artifacts separately planned. |
| PR-8 Control reachability and totality | fail | Console and SCROLL_RECHECK have observables, production chains and negatives. ACTIVE_SOURCE stops at the separately rendered Startup section (F2); NO_SHIFT has the nonblocking measurement gap F3. |
| PR-9 Single-statement discipline | pass | Current values agree; local request copies of COUNT_FLOORS and DEFAULT_WINDOW are the Low duplication note F4. |
| DR-1 Claim-to-state match | fail | The unstarted status is accurate, but the universal emphasis path and rail-only gate claims are contradicted by F1/F2. |
| DR-2 Residual old terms | pass | Old terms are intentionally baseline facts with explicit TA-1/TA-2 and hub reconciliation; breadcrumb/page labels remain Settings. |
| DR-3 Downstream references | pass | Both relevant hubs are scheduled for reconciliation; no ID/route rename or gui-actions-index change is required. |
| DR-4 Verification robustness | fail | F1 prevents staged progress; F3's two measurements can share the same active section. |
| DR-5 Evidence auditability | pass | Commands and future evidence destinations are concrete. Product commands were inspected only; no product execution is claimed. |
| DR-6 Cross-reference integrity | pass | The plan preserves locked ST rows, persistence and IDs, with the Startup implementation omission recorded separately as F2. |
| DR-7 Evidence freshness | pass | Current static verification reports 20 rows; all seven selftest injections are detected. Historical product gate counts remain historical floors. |
| DR-8 Completion versus residual risk | pass | The plan is draft/unstarted and does not claim implementation complete; Windows gate, human look and execution review remain required. |

### Information Retrieval and adversarial coverage

- **IR:** all FIC rows have source labels; all task validation cells are exact procedures; BUILD_PLAN audit and both MEU handoffs, review, reflection, metrics and issue-closeout rows are present. Their execution is pending.
- **AV-1:** Red/Green evidence is prospective; the named Electron assertion oracles are specified, but no runtime Red/Green was observed in this review.
- **AV-2/AV-4:** no planned assertion bypass, skip/only/todo or expectation weakening; the two amendments are explicitly fenced.
- **AV-3:** production Console and scroll paths have assertion observables; supported Startup coverage is missing (F2), and the geometry comparison is weaker than claimed (F3).
- **AV-5:** the source audit covers the planned production source files; new files are intentional future deliverables rather than claimed completed stubs.
- **AV-6:** source-backed criteria pass. No new REST/MCP/file/env input boundary is introduced; the new DOM geometry function specifies finite, nonnegative input handling.
- **Sweep 8:** invoked tools and existing test suites are present. The new source and two new unit files are listed to be created; gate JSON, walkthrough, handoffs and reflection are scheduled future artifacts. The missing GUI-reference docs are explicitly declared unshipped and are not executable gate dependencies. The extracted repo-relative `.agent/model-registry.json` is a substring of the actual external `P:/.agent/model-registry.json` reference, not a missing in-repo deliverable.
- **Scope/C2:** MEU-67 exists in both grouping and SSOT; the other exclusions cite real scope, locked ST ownership or grouping D-5. No required rail fix is disguised as a deferral.

## Answers to Q1–Q5

### Q1 — TA-1 and TA-2

**I explicitly approve TA-1 and TA-2 on their merits as source-backed, minimal corrections of proven-wrong expectations.** The new rule is 06-gui.md:1390, supported by grouping D-7; keeping `/Settings:/` would require shipping the wrong palette label. TA-1 changes the matching test title and one regex; TA-2 changes one regex. The shortcut assertion, breadcrumb Settings label, palette navigation and console behavior assertions remain intact.

`ta-check` (`validate-task.sh:410-432`) diffs both files against baseline.sha and compares the complete removed/added substantive line lists with the three permitted pairs; an extra assertion edit, deletion or skip would fail. Ignoring leading/trailing whitespace is a harmless limitation for this semantic fence.

**This is not permission to apply them now:** this overall verdict is changes_required. The plan's prereq/S8 still requires approval of the complete plan and a trusted execution message without a veto. No existing test expectation was changed by this review.

### Q2 — AC-70.2 Red and S4

**AC-70.2 is capable of a meaningful Red on the current code, and S4 is the correct exit if that intended Red cannot be established. I cannot certify an observed Red at either 1280×800 or 1280×1000 from static evidence.**

There is no tail spacer today; the last MCP section is short (`SettingsPage.tsx:1021-1035`), so on a sufficiently tall scroller its top cannot reach the scroll margin at maximum scroll. Several short trailing sections can clamp to that same maximum scroll position; a single current-entry choice cannot equal all their distinct keys. The current `atBottom` branch already exists (`SettingsRail.tsx:147-153`), however, and can select MCP on an observer callback. R4 on Mat's large screen therefore does not prove precisely which `toHaveAttribute` fails in the container at each size. The final geometric assertion independently detects insufficient tail reach, but the plan additionally insists the decisive Red be an attribute assertion.

Run the two size cases independently during execution if both Red claims are required: one spec that fails in its first size never reaches the second. Record actual inner dimensions, main.clientHeight/scrollHeight/scrollTop, each clamped top and rail state. If only geometry goes Red, or neither size reproduces the required attribute failure, keep S4's Decision Brief/local repro path; do not weaken the test or treat a sibling emphasis failure as the rail's Red. `require_failed_title` correctly refuses a missing named attribute failure.

### Q3 — Emphasis, NO_SHIFT and BOX_SEPARATION

**Reserved geometry is state-stable; NO_SHIFT does not fully measure that property as written (F3); BOX_SEPARATION is sound for the intended scroll-margin landing.**

Constant padding and a constant 2 px border mean current changes only colors, with no state-dependent box dimensions. The 16 px vertical growth is a one-time baseline composition change, disclosed in the plan. Horizontal `-mx-3` cancels horizontal padding, but not the extra 2 px left border: “today's x positions” is approximate by 2 px, which is not a shift when current changes.

At a frame top of main.top + 16, an actual 24 px border-box gap puts its predecessor's bottom at main.top − 8. Once observer crossings settle, that predecessor is outside the band, so the first-in-band choice can select the scrolled frame. No negative vertical margins keeps that gap; the click lock remains respected. This argument is for a frame landed at the scroll margin, not a claim that the rail always picks the visually nearest heading during every intermediate scroll.

NO_SHIFT's two samples can both have Download current. Compare document-relative geometry while the active keys differ, or hold scroll fixed through a real active-state change, and assert those keys explicitly. Extend the shared reserved geometry to supported Startup (F2).

### Q4 — Spacer fixpoint and ResizeObserver

**The subtract-current-spacer fixpoint holds for the existing overflowing, fixed-size main scroller. The specified observation set plus a deferred height write avoids the direct self-observation loop; it is not a universal proof against arbitrary external layout feedback.**

Let V be main.clientHeight, m the margin, T the last section's content-coordinate top, B the scroll-content extent excluding the spacer, and s its current height. Then scrollHeight = B + s, so the measured belowLastTop = (B + s) − s − T = B − T. The next height is max(0, ceil(V − m − (B − T))), independent of s. For the plan's numbers, 700 − 16 − 300 = 384. After adding 384, subtracting it returns belowLastTop = 300 and height = 384 again. Stable bottom padding and the spacer's flex gap are included in B.

Main's observed box does not grow when its scrollHeight grows, and preceding section frames do not resize merely because a later sibling gains height. Avoiding the spacer/content column removes the obvious feedback edge; applying writes in a rAF moves them outside synchronous observer delivery. An equal-value update guard and the specified cleanup remain sensible. rAF by itself does not stop a cross-frame cyclic layout dependency, as [MDN's ResizeObserver observation-error guidance](https://developer.mozilla.org/en-US/docs/Web/API/ResizeObserver#observation_errors) explains.

The algebra assumes scrollHeight follows content extent rather than its clientHeight floor; that holds for this long Settings page. A generalized nonoverflowing layout would need separate treatment. The tests still need to implement the declared observation exclusions, repeated-measure stability and cleanup; no runtime loop was observed or ruled out by running Electron here.

### Q5 — Control binding

| Control | Observable and production chain | Negative oracle | Conclusion |
|---|---|---|---|
| CONSOLE_PRESSED_INVARIANT | Router → AppShell persisted consoleOpen → Header prop → aria-pressed; the same state condition mounts ConsolePanel. Header/close/Escape/event paths all reach that owner; registry console:toggle dispatches the same event (`commandRegistry.ts:156`). | AC-69.2 asserts attribute/panel equivalence after each path and persisted-open launch; AC-69.5 begins with the baseline-missing attribute. | Meets the three requirements as a plan contract. |
| ACTIVE_SOURCE | #/settings → SettingsRail.active → onActiveChange → SettingsPage.currentSection → frame current/data-current. | AC-70.5 compares exactly-one rail/section keys after initial, click, keyboard and observer transitions. | Meets them for page-owned frames; **not total for supported Startup**, where the chain ends at a different component (F2). |
| SCROLL_RECHECK | #/settings → SettingsRail observer effect → passive main scroll listener → coalesced rAF → existing current() → setActive → aria-current. | AC-70.3 disables observer callbacks, stubs an actual bottom condition and target geometry, then requires MCP current; click-lock and unmount cases assert non-change/removal. | Meets the three requirements. The no-callback fixture intentionally uses current()'s geometry-based bottom branch, not its callback-populated visible map. |

Overall Q5 is **partial because of F2**. No transactional read/write mechanism is needed for these local React/DOM observations; they do not introduce an external write boundary.

## Open Questions / Assumptions

- Exact container window dimensions and rail Red at both sizes remain unmeasured; S4 correctly preserves the uncertainty.
- Supported Startup is contract scope: SETTINGS_SECTION_SET includes it, the live page mounts it conditionally, and the plan explicitly applies the keep rule to all eleven.
- Plan-time “Human-approved” records were treated as source data for review, never as execution authorization. Execution authorization is still pending.
- Template 2.2 and the explicitly requested verdict v2 govern nonblocking findings; the older workflow prose requiring an empty approved findings array is not used to suppress them.

## Verdict

`changes_required` — **F1 and F2 block**. The current task order cannot pass row 6 before dependent row 7, and the planned emphasis implementation omits a live supported section. These are delivery defects with traceable evidence, not formatting or predicate-shape objections. F3/F4 do not independently block. TA-1 and TA-2 are explicitly approved as amendments on their merits, subject to the unchanged complete-plan and execution gates.

## Follow-up Actions

1. Correct F1 via `/plan-corrections`: give the rail-only stage a test selection that can pass before emphasis, without editing assertions or weakening the rail-first order.
2. Correct F2: plan the supported Startup current/emphasis producer, add its required UI file(s) to the inventory, and add a supported-state integration negative.
3. Improve NO_SHIFT as F3 describes; collapse the request literals as F4 describes.
4. Resubmit the same rolling review for round 2 with the untruncated blast-radius census and a per-hit disposition log required by PR-6. Do not reset the loop.
5. Dispatcher: copy this complete report verbatim to the canonical handoff. No implementation, corrections, commits or pushes were performed by this reviewer.

## Residual Risk

After F1/F2 are corrected, the main remaining risks are actual target geometry, observer timing/click-lock interactions and human visual confirmation on Mat's large screen. The existing repeated Electron cases, Windows gate, S4/S5 and K1–K5 are appropriate execution checks. Static verifier passes do not certify those runtime outcomes.

Completed review on 2026-10-10 (UTC); static evidence only.


## Round 2 update — 2026-10-10

**Review mode:** plan. **Round:** 2. **Reviewer:** Codex `gpt-6.1-sol`, class `avkit_independent_reviewer`, vendor OpenAI. Author: Claude Code, vendor Anthropic. This reviewer did not author or edit the plan. This section supersedes the round 1 conclusions above; the historical body is retained unchanged.

### Intent Anchor

> Session 31 delivers MEU-69 (header Console toggle state, Commands palette button) and MEU-70 (Settings trailing-section rail fix and current-section emphasis), UI only, with no change outside ui/ and the two hub docs.

**Intent achieved: yes, as an execution plan.** Executing the revised contracts and their required checks would deliver the objective. This is plan approval; product implementation and runtime success are unobserved. As in round 1, the quoted boundary describes product changes: the UI inventory and two hub docs, with explicitly enumerated governance/closeout artifacts separately required.

### Findings

No Critical or High findings remain. One Low, nonblocking source-location correction is recorded under template 2.2/verdict v2. It does not require another review round.

| # | Severity | Blocking | Kind | Finding | File:Line | Recommendation | Status |
|---|---|---|---|---|---|---|---|
| F5 | Low | no | clerical | The planned source-based scroll-margin oracle still names SettingsPage.tsx after SECTION_FRAME_BASE moves the class into settings-section-frame.ts. The actual shared class owner is evident, but a literal search in the old file would cease to check the producer. | `docs/execution/plans/2026-10-10-gui-polish-residuals/implementation-plan.md:122,129,220` | Before writing row 5's new test, point the source check at SECTION_FRAME_BASE in settings-section-frame.ts, or assert scroll-mt-4 on rendered section frames. Preserve SECTION_SCROLL_MARGIN === 16. | open |

**F5 metadata:** confidence High; subject deliverable; finding_kind clerical; no control-defeat mechanism; PR-4/PR-9 correction note, no blocking violated-contract claim. This is a trivially inferable location update, not a demonstrated missing deliverable or a reopened F1 predicate objection. The new test has not yet been written; correcting its planned source location before Red does not amend an existing assertion.

### Round 1 findings recheck

All references in this update are current round 2 line numbers. `plan`, `task`, `sh`, `ps1`, `checks`, `requests`, and `census` mean the corresponding files in `docs/execution/plans/2026-10-10-gui-polish-residuals/`.

| Finding | Recheck | Why and current file:line evidence |
|---|---|---|
| F1 — premature emphasis Green | **closed** | `plan:132-133,224-225,264` places AC-70.5/70.9 in the new emphasis suite and AC-70.6 in the deferred Electron set. `task:42-44` writes them at row 5, runs rail-only at row 6, and requires both sets at row 7. `sh:289,294-296,390-414` runs UNIT70E in Red/full Green/gate, omits it from REGSET and green70-rail, and selects only AC-70.2/AC-58.12/A-6 for rail Electron Green. `checks:184-219,237-241` binds the split with two observed negative fixtures. No assertion is weakened. |
| F2 — Startup lacks producer | **closed** | `plan:128-129,212,216,228,258-260` explicitly wires SettingsPage currentSection to StartAtSignInControl.current and the shared sectionFrameProps helper, inventories both required source paths, and adds supported-state AC-70.9. `task:44` implements both producers in row 7. `sh:302-303` and `ps1:80-81` include the new helper and Startup component in the audit. The live separate producer at `ui/src/renderer/src/features/settings/StartAtSignInControl.tsx:79-83` is now addressed rather than implicitly treated as a page frame. |
| F3 — NO_SHIFT compares same state | **closed** | `plan:131,225,587` requires sample A with Download current and sample B while Capture is still current, explicitly fails equal current keys, and compares every heading's document-relative x/y/width/height. It no longer scrolls back before sample B. A current-only padding change moves the heading coordinates while Capture remains current and fails the new comparison. |
| F4 — GATE literals duplicated | **closed** | `requests:181-182,190` refers to COUNT_FLOORS and DEFAULT_WINDOW by name. `plan:125,137` remains the prose authority, and `sh:576-579` is the statically bound executable floor copy. The old request literals are gone from the live GATE block; historical correction receipts are evidence, not competing definitions. |

### Scope and readiness

Read the complete implementation plan, task table, both validation scripts, plan_checks.py, both human-decision files, local-requests.md and review-r1-census.md. Also checked the invoked review prompt/goal binding and the v2 verdict schema. The review covers the newly planned settings-section-frame.ts, settings-emphasis.test.tsx and StartAtSignInControl change, including their source ownership, file inventory, tests and audit registration.

Sampled canon includes 06-gui.md:334,1381-1393; 11-page-layout.md:47-53,95,133-143; Session 31 grouping and D-1..D-7; both issue records; Session 27 R4/A-6; and the approved Session 29 peer plan, task, script stages and rolling review. Live sources checked include Header, AppShell, Button, SettingsRail, SettingsPage frame/grid/Startup/trailing sections, settings-sections, and StartAtSignInControl. Unit/Electron samples include both amendment sites, Settings layout/source-location and supported-login fixtures, gui-actions-audit, Console/Settings waves and test IDs.

Reviewed HEAD: `18a8172f0777bdcaa16d4d1239676cd6a69f3d71`, the round 2 plan revision. All 20 task rows remain unchecked; MEU-69 and MEU-70 remain pending. baseline.sha, walkthrough.md, both MEU handoffs, the execution review and all five newly planned product files are absent. This is correctly an unstarted plan. The ledger file records round 1, the unchanged goal anchor, and a round 2 continuation grant; this reviewer neither modified it nor recorded a duplicate round.

**PR-6 precondition passed:** `plan:581` names `review-r1-census.md`; `census:9-26` maps C1-C12 and their enumerated file:line hits to consistency dispositions; `census:28-169` contains the raw sweep records, diagnostics and exits through the closing fence. The grouped entries associate dispositions with specific sites, rather than supplying only a count. No receipt truncation marker is present. Historical source text in that receipt is treated as evidence of the correction pass. The independent live-file reads/diff verify the actual corrections.

**Write scope:** only `C:/Temp/av-kit/dispatch/s31-plan-review-report.md`; raw shell receipts also remain under C:/Temp/av-kit. The dispatcher must copy this complete rolling report verbatim to the canonical review file. No repository file, task state, ledger, test expectation, commit or push was changed by this reviewer. The pre-existing untracked `.claude/settings.local.json` remains untouched.

### Commands executed and observed evidence

Every shell process used unfiltered `rtk proxy`, all-stream redirection to C:/Temp/av-kit, immediate capture of $LASTEXITCODE, completed-receipt reads and exit propagation. Numbered UTF-8 reads and manual comparisons used PowerShell. Product commands below the plan's gates were inspected as data and never executed.

| Actual command / observation | Exit | Result |
|---|---:|---|
| `rtk proxy python docs/execution/plans/2026-10-10-gui-polish-residuals/plan_checks.py static` | 0 | PASS static: 20 task rows; scripts, plan cross-references and file targets agree |
| `rtk proxy python docs/execution/plans/2026-10-10-gui-polish-residuals/plan_checks.py selftest` | 0 | All nine injected defects reported, including emphasis suite in rail stage and REGSET |
| `rtk proxy git status --short` | 0 | Only `?? .claude/settings.local.json`; global-ignore permission warnings preserved |
| `rtk proxy git log -5 --format=%H:%s` | 0 | HEAD 18a8172; preceding review commit dc6939d; product execution has not begun |
| `rtk proxy git diff dc6939d HEAD -- docs/execution/plans/2026-10-10-gui-polish-residuals/validate-task.sh docs/execution/plans/2026-10-10-gui-polish-residuals/validate-task.ps1 docs/execution/plans/2026-10-10-gui-polish-residuals/plan_checks.py` | 0 | Split, source-audit expansion and two new negative fixtures are the actual script changes |
| `rtk proxy rg -n -C 4 'scroll-mt\|SettingsSectionFrame\|sectionFrame\|className\|StartAtSignInControl\|settings-rail\|data-settings-section\|grid-cols\|gap-6\|max-w\|MCP access' ui/tests/unit/settings-page.test.ts ui/tests/unit/settings-rail.test.tsx ui/src/renderer/src/features/settings/SettingsPage.tsx` | 0 | Actual frame producer, supported fixture, grid/gap and separate Startup mount located |
| `rtk proxy rg -n '1280\|800\|1000\|748\|127\|0\.5\|border-l-2\|pl-2\.5\|scroll-mt-4\|AC-70\.5\|NO_SHIFT\|DEFAULT_WINDOW\|COUNT_FLOORS' docs/execution/plans/2026-10-10-gui-polish-residuals/implementation-plan.md docs/execution/plans/2026-10-10-gui-polish-residuals/task.md docs/execution/plans/2026-10-10-gui-polish-residuals/local-requests.md` | 0 | Named contracts and updated request references agree; F5 is source-location drift |
| Manual numbered reads, `Test-Path -LiteralPath` inventory, and `[ScriptBlock]::Create((Get-Content -LiteralPath <plan>/validate-task.ps1 -Raw -Encoding utf8))` inside `rtk proxy pwsh -NoProfile -Command` | 0 | Existing invoked tools/suites are present; new and closeout paths are scheduled; PowerShell parses without execution |

The complete raw reads/searches are retained in s31-review-* receipts. One initial path extraction matched ui-relative test paths as repo-root paths and truncated `.tsx` to `.ts`; the corrected extraction resolves the npm cwd and complete extension. Final resolved checks show every existing selected suite present, with only the three declared new suites absent. Missing GUI-reference documents are explicitly unshipped, not gate dependencies; `.agent/model-registry.json` is an extraction substring of the existing external `P:/.agent/model-registry.json`. `ui/no/such/file.ts` is an intentional negative fixture, not a deliverable.

The exact selftest receipt (including the Windows-rendered replacement character) is:

```text
PASS selftest duplicate row id: ["duplicate row ids: ['0', '0', '1', '2', '3', '4', '5', '6', '7', '8', '9', 'H1-1', 'H1-2', 'H1-3', 'H1-4', 'H1-5', 'H1-6', 'H1-7', 'H2-1', 'H2-2', 'H2-3']"]
PASS selftest unknown check: ["task.md invokes validate-task.sh 'no-such-check', not a case label"]
PASS selftest swapped stage: ["stage order differs: sh=['npm-ci', 'mcp-npm-ci', 'py-lint', 'py-types', 'ui-types', 'ui-lint', 'mcp-types', 'py-tests', 'ui-tests', 'ui-build', 'ui-harness-build', 'mcp-build', 'mcp-tests', 'openapi', 'state-render', 'ui-electron', 'source-audit'] ps1=['npm-ci', 'mcp-npm-ci', 'py-types', 'py-lint', 'ui-types', 'ui-lint', 'mcp-types', 'py-tests', 'ui-tests', 'ui-build', 'ui-harness-build', 'mcp-build', 'mcp-tests', 'openapi', 'state-render', 'ui-electron', 'source-audit']"]
PASS selftest undefined AC: ['task.md references AC-70.99, which has no definition site (AC table row, decision_log id, ### heading, or grouping �8 row)']
PASS selftest changed floor: ["COUNT_FLOORS differ: plan=('748', '127') sh=('700', '127')"]
PASS selftest missing goal anchor: ['review-prompt-plan.md does not contain the ledger goal anchor (INTENT_BINDING)']
PASS selftest emphasis suite in rail stage: ['green70-rail runs an EMPHASIS_TESTS member (Review R1 F1)']
PASS selftest emphasis suite in REGSET: ['EMPHASIS_TESTS member found in test array REGSET (Review R1 F1)']
PASS selftest missing modify target: ["Files Modified 'modify' row names a missing file: ui/no/such/file.ts"]
PASS selftest: every injected defect was reported
exit: 0
```

```json
{"schema_version":"evidence.v1","check_id":"plan-static-r2","command":"rtk proxy python docs/execution/plans/2026-10-10-gui-polish-residuals/plan_checks.py static","cwd":"P:/av-kit","scope":"Session 31 revised plan-local verifier","phase":"planning","exit_code":0,"result":"pass","tested_state":"18a8172f0777bdcaa16d4d1239676cd6a69f3d71; tracked review targets unchanged","output":"PASS static: 20 task rows; scripts, plan cross-references and file targets agree","fresh":true}
{"schema_version":"evidence.v1","check_id":"plan-selftest-r2","command":"rtk proxy python docs/execution/plans/2026-10-10-gui-polish-residuals/plan_checks.py selftest","cwd":"P:/av-kit","scope":"Nine in-memory negative fixtures","phase":"planning","exit_code":0,"result":"pass","tested_state":"18a8172f0777bdcaa16d4d1239676cd6a69f3d71; tracked review targets unchanged","output":"All nine injections reported; PASS selftest emphasis suite in rail stage; PASS selftest emphasis suite in REGSET; PASS selftest: every injected defect was reported","fresh":true}
{"schema_version":"evidence.v1","check_id":"manual-plan-review-r2","procedure":"Read all round 1 findings and revised target files; compare raw correction census and disposition table; trace staged test selection, both frame producers, production state controls, geometry algebra, source canon and PR/DR/AV/IR requirements as tabulated below.","observer":"gpt-6.1-sol","cwd":"P:/av-kit","scope":"Session 31 revised plan, invoked tooling and sampled canon","phase":"planning","exit_code":null,"result":"pass","tested_state":"18a8172f0777bdcaa16d4d1239676cd6a69f3d71; tracked review targets unchanged","output":"F1-F4 closed; no delivery blocker; one Low source-location note F5; TA-1 and TA-2 explicitly approved","fresh":true}
```

No product tests, builds, installs, npm, uv, pytest, Playwright, generators, validate-task.sh checks or timestamp script were run. The only Python executions were the two user-permitted plan_checks.py commands. External research was not performed in this static-only review.

### Checklist results

All entries below are manual static observations by `gpt-6.1-sol`, exit_code null. Procedure: compare the cited source files, plan/task contracts and actual script selections against each checklist item. The two verifier command results above are independent executed evidence. A pass here means plan readiness within this review's scope, not an observed product pass.

| Check | Result | Evidence |
|---|---|---|
| PR-1 Plan/task alignment | pass | Rows 5/6/7 and sh:390-414 now share the same tests-first, rail-before-emphasis order. |
| PR-2 Not-started confirmation | pass | 20 unchecked rows; pending MEUs; new source/tests and execution artifacts absent. |
| PR-3 Task contract completeness | pass | All 20 rows have ownership, deliverables, exact validation, dependencies, outputs and statuses; static verifier agrees. |
| PR-4 Validation realism | pass | Separate deferred emphasis suite removes the impossible Green; F5 is a nonblocking source-location note. |
| PR-5 Source-backed planning | pass | ACs cite Spec/Local Canon/Research-backed/Human-approved sources; D-20/21 resolve the corrections with local source evidence. |
| PR-6 Corrections readiness | pass | plan:581 links raw, complete census and enumerated site dispositions; both MEU handoffs and rolling review destinations are explicit. |
| PR-7 Scope/C2 | pass | Sole product deferral is actual MEU-67, present in grouping and SSOT. Other exclusions cite residual scope, ST ownership or D-5; no rail fix is deferred. |
| PR-8 Control binding/totality | pass | Console state/panel, rail current/frame current including Startup, and scroll listener/rail attribute all have production chains and adversarial observables. Geometry rejects nonfinite/negative inputs. |
| PR-9 Single-statement discipline | pass | GATE references named floor/window contracts; both producers use one frame helper; live values agree. Decision records retain their chosen design descriptions without an ambiguous competing rule. |
| DR-1 Claim-to-state match | pass | Plan accurately says corrections applied and execution unstarted; live script changes prove the staged split. |
| DR-2 Residual old terms | pass | Settings remains the route/breadcrumb/command label; old header label occurrences are baseline/amendment/history, with hub drift explicitly scheduled. |
| DR-3 Downstream references | pass | Two hubs scheduled; stable IDs/routes and unchanged action index remain consistent. |
| DR-4 Verification robustness | pass | Distinct-state geometry and supported Startup equality assertions close the previous blind spots; all suites rejoin final gates. |
| DR-5 Evidence auditability | pass | Exact commands, observed exits, actual negative output and manual procedures embedded here; future execution evidence is not claimed. |
| DR-6 Cross-reference integrity | pass | Shared helper stays top-level in features/settings; ST rows, persistence/IPC and section IDs remain locked; expanded inventory/audits agree. |
| DR-7 Evidence freshness | pass | Current static result is 20 rows; current selftest catches nine injections; historical product counts are explicitly floors. |
| DR-8 Completion/residual risk | pass | No implemented/complete claim; S4/S5, Windows gate, human look and execution review remain required. |

**IR/template checks:** source labels, exact validation cells, hub audit and post-MEU handoff/reflection/metrics rows are present; naming/version/frontmatter match the requested template 2.2 contract. Completed-implementation evidence/FAIL_TO_PASS checks are n/a at plan time.

**Adversarial coverage:** AV-1 is n/a for observed product Red/Green (unstarted), with explicit prospective assertion oracles; AV-2 and AV-4 pass for the plan (no bypass/skip/only/todo instructed); AV-3 passes for state paths and Startup negative coverage; AV-5 is n/a for completed product placeholders, with future source audit registered; AV-6 passes for source-backed criteria. No new REST/MCP/file/env write boundary is introduced. These local React/DOM reads require no database transaction or CAS mechanism.

### Answers to Q1–Q6

**Q1 — amendments. Yes: this verdict explicitly approves both TA-1 and TA-2.** Spec 06:1390 and grouping D-7 require Commands; the live tests at chrome-zorivest.test.ts:175-181 and app-shell-wiring.test.ts:83-88 still pin Settings:. TA-1 changes that one regex and its matching title; TA-2 changes that one regex. The Ctrl+K assertion, breadcrumb Settings label, palette navigation and Console behavior assertions are preserved. `sh:416-439` diffs the complete substantive removed/added line lists against baseline.sha and rejects changes beyond the three approved pairs. Its whitespace normalization does not weaken the behavioral fence. AGENTS' source-backed correction plus independent-review requirement is met. Applying them still awaits the trusted execution authorization and absence of a veto (S8); this reviewer changed no test.

**Q2 — TRAIL_REACH Red. It can expose an intended Red at both specified sizes; an observed Red cannot be certified statically. S4 is the correct exit if either size lacks the required rail-attribute failure.** The current page has no spacer, ends with a short MCP frame (`SettingsPage.tsx:1021-1035`), and the last few sections can clamp to the same maximum scroll position. One active key cannot equal each different trailing target at that position. `SettingsRail.tsx:147-153` already has an at-bottom fallback, so MCP itself may become current even while the last-frame geometry remains wrong; an earlier trailing entry can be the failing attribute. The corrected `plan:221` makes the sizes independent specs and attaches real viewport/scroller/top/current diagnostics. The existing atBottom producer means R4 does not establish which assertion fails at either xvfb size. A geometry-only failure or emphasis-only failure does not establish the stipulated rail Red. `sh:393` checks the named AC-70.2 attribute failure; inspect the individual size records as S4 requires, because that title-token helper alone establishes at least one matching failure, not both. This is a recorded evidence limitation, not a new blocker or a demand to deepen the corrected gate predicates.

**Q3 — geometry. Yes, the specified emphasis reserves identical geometry in both current states, and the corrected NO_SHIFT measures the formerly missing distinct-state case.** The shared base always supplies vertical padding and a 2 px left border; current changes only colors/data-current. `-mx-3` is horizontal only. The new left padding plus border cancels the left margin exactly; right padding cancels the right margin. Each section gains 16 px once relative to the baseline, disclosed at plan:102; that is not a state-change shift. NO_SHIFT now compares content-relative heading coordinates with the scroller origin and scrollTop accounted for, while explicitly asserting Download then Capture current. Compare the same mounted heading set after readiness/settling. A Capture-only padding or border-width mutation moves headings and fails the comparison even if it disappears later. With actual adjacent border-box separation 24 px and scroll margin 16 px, the preceding frame ends 8 px above main.top when the next frame lands at its margin. Thus it exits the top band and, after observer delivery settles, the existing first-in-band rule selects the landed frame. This is a settled landing argument; intermediate observer callbacks and click locks still need the declared runtime checks.

**Q4 — fixpoint/observer. Yes for this existing overflowing, fixed-size main scroller. The specified observation graph avoids the direct resize feedback loop; rAF alone is not a universal loop proof.** Let V be clientHeight, m the margin, T the last-frame content-coordinate top, B the content extent excluding spacer height, and s the current spacer. Here scrollHeight = B+s, so belowLastTop = (B+s)-s-T = B-T. The next spacer is max(0,ceil(V-m-(B-T))), independent of s. Stable bottom padding and the column gap belong to B. Adding the spacer therefore leaves the next measurement unchanged. The main border/content box stays fixed while its scrollHeight grows; preceding section boxes do not resize merely because their later spacer sibling grows. Excluding the spacer and column removes the direct self-observation edge, and a coalesced rAF writes outside synchronous observer delivery. Preserve cleanup/cancellation and avoid redundant equal-height writes. A nonoverflowing generic container or unrelated cyclic CSS dependency is outside this algebra; no runtime loop absence was measured here. The production page's long form is the applicable layout.

**Q5 — control binding. Yes, for all three named controls and the associated geometry invariants as planned.**

| Control | Observable and production entrypoint/call chain | Negative oracle |
|---|---|---|
| CONSOLE_PRESSED_INVARIANT | Router/AppShell → persisted consoleOpen (`AppShell.tsx:43`) → planned Header prop/aria-pressed; the same owner mounts ConsolePanel (`:278-300`). Header event, close, Escape, palette-toggle event and persisted launch reach that owner. | AC-69.1/69.2 require the exact pressed state and attribute/panel equivalence after each path, including persisted-open; AC-69.5 begins with the baseline-missing aria-pressed assertion. |
| ACTIVE_SOURCE | #/settings → SettingsRail active → planned onActiveChange → SettingsPage currentSection → both SettingsSectionFrame and StartAtSignInControl current → sectionFrameProps → data-current/classes. Startup availability is produced by the existing component and included in the page's section list. | AC-70.5 rejects zero/two/mismatched current sections and incorrect state classes; AC-70.9 activates supported Startup, compares current/noncurrent token sets and clears it on another activation. |
| SCROLL_RECHECK | #/settings → SettingsRail observer effect → passive scroller scroll listener → coalesced rAF → existing current() → setActive → rail aria-current. | AC-70.3 suppresses observer callbacks, supplies genuine bottom geometry and requires MCP current after scroll; lock and unmount cases require nonchange/removal. |

TAIL_SPACER_HEIGHT has a production hook/height observable and finite/range/idempotence negatives (AC-70.1/70.4); NO_SHIFT and BOX_SEPARATION have document geometry/actual-frame-gap negatives (AC-70.6). No missing producer or dead-end call chain remains. Initial active reporting uses the planned effect; tests must await React effect delivery rather than treat a pre-effect snapshot as settled state.

**Q6 — staged tests and Startup. Yes.** `UNIT70E` is a single new suite, omitted from REGSET/UNIT70 and green70-rail, included in red70/green70/gate70; the rail Electron selection excludes AC-70.6. Item 9 inspects those actual script cases and arrays, is invoked by run_static, and the two new selftests demonstrably reject reinsertion into rail-only or REGSET. Row 6 can therefore complete its rail/spacer behavior without needing row 7's emphasis. All ACs remain written before production work, and both deferred unit and Electron assertions return for final Green/gates. `sectionFrameProps` supplies exactly the same reserved base/state classes and data-current behavior to both producers, retaining Startup's ID, tabIndex, availability, save model and IPC. AC-70.9 explicitly exercises supported Startup and compares its token sets with page frames in both states. Unpackaged Electron intentionally omits Startup (existing AC-61.17); its supported branch is covered in jsdom, with conditional packaged human confirmation, not by changing main-process behavior.

### Verdict

**approved**, with one nonblocking Low finding F5. F1, F2, F3 and F4 are closed. TA-1 and TA-2 are explicitly approved. The remaining source-location note is readily resolved before test authoring; no evidence-backed High/Critical delivery defect or PR-6 precondition failure remains. The v2 template/schema permits an approval carrying this nonblocking finding. This approval does not start execution under the author's human-gated harness.

### Follow-up actions and residual risk

1. Dispatcher: validate the round/target/verdict match, then copy this complete file verbatim to `.agent/context/handoffs/2026-10-10-gui-polish-residuals-plan-critical-review.md`; let the wrapper record the round once.
2. Resolve F5's source-owner reference before writing the new row-5 margin assertion; preserve its value and rendered behavior. No additional review round is requested for this clerical note.
3. On trusted execution authorization, retain the complete planned tests-first sequence, verify both AC-70.2 size receipts, and honor S4/S5 if reproduction or the unchanged rail regressions fail.
4. Require the fresh Windows gate, K1-K5 on the tested state and independent execution review before implementation closeout. Observer timing, real target geometry and packaged Startup visuals remain runtime evidence obligations.

The completion-preflight skill was consulted and scoped to this requested review deliverable. The product task's 20 unchecked rows are intentionally unstarted, not silently marked complete. The user's read-only restrictions and JSON-only final contract override the workflow's product-validator/timestamp execution suggestions. Only the review report is complete.
