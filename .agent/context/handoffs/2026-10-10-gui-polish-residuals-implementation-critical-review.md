---
date: "2026-10-14"
review_mode: execution
target_plan: docs/execution/plans/2026-10-10-gui-polish-residuals/implementation-plan.md
verdict: approved
findings_count: 0
round: 2
template_version: "2.2"
requested_verbosity: standard
agent: gpt-6.1-sol
---

# Critical Review: 2026-10-10-gui-polish-residuals

> **Review Mode**: execution
> **Verdict**: changes_required

## Intent Anchor

> Session 31 delivers MEU-69 (header Console toggle state, Commands palette button) and MEU-70 (Settings trailing-section rail fix and current-section emphasis), UI only, with no change outside ui/ and the two hub docs.

**Intent achieved: partial.** The header controls and shared section emphasis are delivered, and the recorded Windows gate is bound to the reviewed code. One spacer lifecycle defect can defeat the trailing-section fix after supported Startup availability changes.

## Scope

**Target:** the approved implementation plan, both MEU-69/MEU-70 handoffs, the round-2 approved plan review (including F5), all 17 changed ui/ files, the two hub changes, the A-6 contrast data amendment, and the named execution evidence/scripts. Baseline: `06e870bcb79fc4a1b689f5ddbe3c8c5b1a718ea1`. Reviewed HEAD: `e875a59a8e1e04f80a65ef516b1e0350fc01ead2`.

**Review Type:** independent execution review, round 1, loop `s31-exec-2026-10-10-gui-polish-residuals`. Author: Claude Code / Anthropic; reviewer: Codex `gpt-6.1-sol` / OpenAI. Both handoffs correlate to this plan's MEU set; neither is omitted.

**Checklist Applied:** execution IR-1–IR-7, DR-1–DR-8, reviewer AV-1–AV-6, template checks, and E1–E6. Source/DOM lifecycle tracing and recorded runtime evidence only. No product tests, builds, installs, generators, validate-task checks, or timestamp script were run. Only the two explicitly permitted plan-local Python commands were executed.

The full baseline diff has 36 files: 17 ui/ files, the two hubs, .agent execution state/handoffs, docs/BUILD_PLAN.md's SSOT render, this plan's notes, and the explicitly user-approved A-6 contrast-matrix exception. Frozen product paths have no diff. The existing untracked `.claude/settings.local.json` is outside this work and was preserved. No repository files were written. This report is written only to `C:/Temp/av-kit/dispatch/s31-exec-review-report.md`; the dispatcher owns the verbatim canonical copy to `.agent/context/handoffs/2026-10-10-gui-polish-residuals-implementation-critical-review.md` (absent at review start).

## Findings

| # | Severity | Blocking | Kind | Finding | File:Line | Recommendation | Status |
|---|----------|----------|------|---------|-----------|----------------|--------|
| F1 | High | yes | behavior | Spacer bookkeeping resets across a section-list change while its rendered height survives. A later measurement can subtract the wrong spacer height and prevent MCP from reaching the top band. Violates AC-70.2 / AC-70.4 and TAIL_SPACER. Confidence: High; subject: deliverable; verdict contract family: AC-70. | `ui/src/renderer/src/features/settings/settings-tail-spacer.ts:84` (also :71, :96, :103, :126); caller `SettingsPage.tsx:367`; async producer `StartAtSignInControl.tsx:48` | Preserve the actual applied spacer height across effect restarts, or obtain the committed height from the spacer element. Add a regression with delayed supported Startup after a nonzero spacer, followed by a geometry change; require the correct height and final MCP reach. Rerun affected checks and WINDOWS_GATE after correction. | open |

### F1 — concrete static failure trace

`height` is component state at spacer:71. The effect depends on `sectionKeys` (:126), but initializes a new local `applied = 0` on every setup (:84). Its measurement subtracts that local value (:96) and only updates state when `next !== applied` (:103). The actual existing spacer is not reset or read.

This is reachable through the shipped call chain: `SettingsPage.tsx:236` starts `startupAvailable` false; `StartAtSignInControl.tsx:48,58-60` reports the asynchronously loaded supported state; `SettingsPage.tsx:367-369` then changes the section-key string. If IPC resolves after the first nonzero spacer commits, the effect restarts with nonzero DOM/state and zero bookkeeping. Supported Startup is explicitly within the plan (D-20 / AC-70.9), not an invented external input.

Use the plan's own valid geometry: viewport 700, true content below MCP's top 300, margin 16, committed spacer 384. After the key change, the measured tail includes that 384, while `applied` is zero: `700 - 16 - (300 + 384) = 0`. Because `next === applied`, state remains 384 and the local bookkeeping remains zero. On a subsequent single measurement with viewport 800, the hook computes `800 - 16 - (300 + 384) = 100`, instead of `800 - 16 - 300 = 484`, and commits 100. MCP then stops `800 - 300 - 100 = 400` px below main's top at maximum scroll, outside TRAIL_REACH's 0–17 px bound.

The hook does not observe the spacer or its column, so that wrong spacer write does not itself schedule a repair. Another independent measurement may repair it, but is not guaranteed. One concrete UI sequence that supplies a scroller resize without a further window-resize event on the visible scroller is: delayed supported Startup; expand Console (main is hidden at `AppShell.tsx:274`); resize the window while main is hidden; collapse Console. Main's restoration is observed, but the stale bookkeeping produces the undersized spacer on the restoration measurement. This sequence is a source-derived failure scenario, **not a reviewer-executed GUI reproduction**.

The existing AC-70.4 test (`settings-rail.test.tsx:651`) measures one effect lifetime using unsupported Startup. AC-70.9 tests supported emphasis with no ResizeObserver. The pure fixpoint test correctly subtracts the known first spacer itself. None combines retained height with an effect restart, so the recorded green suite does not disprove F1. The defect is the reset of committed measurement identity, not the approved spacer formula or observation strategy.

No Critical finding was identified. No bookkeeping-only finding gates this verdict.

## Commands Executed

All commands ran from `P:/av-kit`. Shell process output was captured under `C:/Temp/av-kit/s31-*.txt`, with `$LASTEXITCODE` captured immediately before receipt reads and propagated. Exact diffs/JSON/count evidence used unfiltered `rtk proxy`. Bounded file reads used `rtk proxy powershell -NoProfile -Command 'Get-Content -Encoding UTF8 ...'`; numbered source reads used `rtk proxy rg -n '^' <file>`. Receipt reads themselves are observations, not product-suite executions.

| Actual command / procedure | Exit | Decisive observation |
|---|---:|---|
| `rtk proxy python docs/execution/plans/2026-10-10-gui-polish-residuals/plan_checks.py static` | 0 | `PASS static: 20 task rows; scripts, plan cross-references and file targets agree` |
| `rtk proxy python docs/execution/plans/2026-10-10-gui-polish-residuals/plan_checks.py selftest` | 0 | All nine injected defects reported; complete output below. |
| `rtk proxy git status --short` | 0 | Only `?? .claude/settings.local.json`; global-ignore permission warnings retained. |
| `rtk proxy git log -7 --format=%H%x20%s` | 0 | HEAD e875a59; tested d0fff4e precedes only receipt/task/walkthrough/prompt commits. |
| `rtk proxy git diff --stat 06e870bcb79fc4a1b689f5ddbe3c8c5b1a718ea1 HEAD` | 0 | 36 files, 2383 insertions, 94 deletions; classified in Scope. |
| `rtk proxy git diff 06e870bcb79fc4a1b689f5ddbe3c8c5b1a718ea1 HEAD -- ui/src` | 0 | Eight production files: header state/palette, Settings producers/rail/spacer, and one light cyan token. |
| `rtk proxy git diff --unified=0 06e870bcb79fc4a1b689f5ddbe3c8c5b1a718ea1 HEAD -- ui/tests/unit/settings-rail.test.tsx ui/tests/e2e/settings.test.ts ui/tests/e2e/test-ids.ts` | 0 | Rail: one import plus append at baseline EOF; Settings E2E: append at EOF; test IDs: append at EOF. |
| `rtk proxy git diff 06e870bcb79fc4a1b689f5ddbe3c8c5b1a718ea1 HEAD -- ui/tests/unit/app-shell-wiring.test.ts ui/tests/unit/chrome-zorivest.test.ts ui/tests/e2e/console-chrome.test.ts docs/build-plan docs/execution/plans/2026-08-28-p10-queue-card-foundations/contrast-matrix.json` | 0 | Exactly TA-1/TA-2; Console E2E append only; two hub changes; exactly sixteen contrast ratio substitutions. |
| `rtk proxy git diff --name-only 06e870bcb79fc4a1b689f5ddbe3c8c5b1a718ea1 HEAD -- packages mcp-server tools ui/src/main openapi.committed.json` | 0 | Empty output: frozen product paths unchanged. |
| `rtk proxy git diff --name-only d0fff4e451378d689dadde8ae5092ba8607d5ce9 HEAD` | 0 | Only this plan's `review-prompt-exec.md`, `task.md`, `walkthrough.md`, `windows-gate-result.json`. |
| `rtk proxy git diff --quiet d0fff4e451378d689dadde8ae5092ba8607d5ce9 HEAD -- <complete GATED_PATHS list below>` | 0 | Empty output: no gated tracked input differs. |
| `rtk proxy rg -n -C 6 'AC-43.3\|CONTRAST_MIN\|contrast-matrix\|labelRatios\|iconRatios' ui/tests/unit/queue-primitives.test.ts` | 0 | Threshold assertions and independently computed exact matrix equality remain; negative contrast oracles remain. |
| Read all eight changed test suites, inventory every test with `rtk proxy rg -n '(^\|\s)(test\|it)\(\|test\.each\|it\.each\|\.skip\(\|\.only\(\|\.todo\(' <eight suites>` | 0 | All 89 test cases audited below; no skip/only/todo case in that inventory. |
| `rtk proxy pwsh -NoProfile -Command 'Get-FileHash ui/package-lock.json,mcp-server/package-lock.json,uv.lock,P:/.agent/model-registry.json -Algorithm SHA256 \| Format-List Path,Hash; $e = Get-Content -Raw -Encoding utf8 C:/Temp/av-kit/s31-win-e2e.json \| ConvertFrom-Json; $e.stats \| ConvertTo-Json -Compress'` | 0 | All four hashes match the receipt; raw E2E JSON: 131 expected, 0 skipped/unexpected/flaky. |
| `rtk proxy git -C P:/agentic-framework rev-parse HEAD` | 128 | Git dubious-ownership refusal. No configuration changed. |
| `rtk proxy git -c safe.directory=P:/agentic-framework -C P:/agentic-framework rev-parse HEAD` | 0 | `e387decb45e5106efbb1c55747131e7ca45918c4`, matches the receipt (command-local read exception only). |
| Read raw Windows pytest/UI/Electron receipts, raw Vitest JSON, baseline.sha, and canonical-report existence | 0 | pytest 629 passed; Vitest 774 passed / 0 failed / 0 pending / 774 total; Electron 131 passed; baseline matches; canonical report absent. |

The complete path arguments used in the quiet equivalence check were:

```text
ui packages mcp-server tests tools pyproject.toml uv.lock openapi.committed.json
docs/build-plan/06-gui.md docs/build-plan/10-queue-card-ui.md
docs/build-plan/11-page-layout.md docs/build-plan/build-priority-matrix.md
docs/build-plan/gui-actions-index.md docs/proposals
docs/execution/plans/2026-08-28-p10-queue-card-foundations
docs/execution/plans/2026-09-02-p10-queue-card-migration
docs/execution/plans/2026-09-03-p10-queue-card-dnd
docs/execution/plans/2026-09-26-p11-layout-canon/implementation-plan.md
.agent/context/grouping/2026-09-03-p11-page-layout-session-grouping.md
.agent/model-registry.local.json .agent/model-registry.local.yaml
docs/execution/plans/2026-10-10-gui-polish-residuals/validate-task.ps1
```

Other bounded reads covered the requested protocol/guardrails/profile/template, current focus/known issues and harness context, reviewer role, architecture/testing strategy, the complete plan, both handoffs, plan review, task/walkthrough/decisions/census, both validate-task scripts and plan_checks.py (read, not invoked as product validation), and sampled canon. Source searches located the actual producers and assertions rather than treating handoff text as authority. A lightweight memory search found historical other-session guidance; no historical project result is used as current evidence here. No external research was needed or performed.

### Permitted verifier output

```text
PASS static: 20 task rows; scripts, plan cross-references and file targets agree
exit: 0

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

The replacement character in the undefined-AC diagnostic is preserved from the shell rendering.

## Checklist Results

Unless a command is explicitly listed above, these are manual static observations by **gpt-6.1-sol**, exit_code **null**. Procedure: read the production owners and complete test bodies, compare the baseline diffs, trace each AC and negative oracle, and compare recorded gate stages/counts/identity to the current files. Recorded product results are identified as such, not presented as reviewer-run tests.

### Information Retrieval / Implementation Review (IR)

| Check | Result | Evidence |
|---|---|---|
| IR-1 Live runtime evidence | pass | Existing full Windows receipt and raw outputs show real Electron on built outputs; Console tests use the real shell; Settings uses the approved fetch seam while exercising real DOM/layout. No fresh reviewer runtime claimed. |
| IR-2 Stub behavioral compliance | n/a | No new persistence stub or backend collaborator introduced; test DOM/observer seams match this UI contract. |
| IR-3 Error mapping completeness | n/a | No write-adjacent route change. |
| IR-4 Fix generalization | pass | D-22 retains both no-event jump and moved-and-returned negative; SCROLL_RECHECK shares current()/click ownership; both section producers share one helper. |
| IR-5 Test rigor audit | partial | Every changed test-suite case graded below. No trivially unfailable test found; the retained-spacer/effect-restart lifecycle is missing (F1). |
| IR-6 Boundary validation coverage | n/a | New values are in-process boolean/current state and finite DOM geometry; no new REST/MCP/config/file input or settings write schema. Geometry invalids are explicitly tested. |
| IR-7 Deferral and AC coverage | partial | All six AC-69 and ten AC-70 rows appear in their owner handoffs with production/test mapping; integration ACs use mounted collaborators or Electron. No orphan deferral. Full correctness of AC-70.2/70.4 is limited by F1. |
| AC source labels and exact validation cells | pass | Sources are specified; static verifier confirms script/task cross-references. |
| BUILD_PLAN audit and post-MEU rows | pass | Two hubs reconciled; H1-7 and H2-1/2/3 remain unchecked as expected at this review boundary. No fabricated post-review completion. |

### Design / Docs Review (DR)

| Check | Result | Evidence |
|---|---|---|
| DR-1 Claim-to-state match | partial | Header/emphasis/amendments exist; spacer's claimed generality has F1. |
| DR-2 Residual old terms | pass | Settings remains the legitimate route, command and breadcrumb; old header wording occurs in amendment/history context. ConsolePanel canon now names Commands. |
| DR-3 Downstream references updated | pass | Two hubs reflect the implementation; IDs/routes/action registry stay stable. |
| DR-4 Verification robustness | partial | Distinct-current NO_SHIFT and no-observer scroll checks are meaningful; lifecycle combination behind F1 is absent. |
| DR-5 Evidence auditability | pass | Durable handoff Red/Green records plus raw Windows counts, full result JSON and current diff observations. |
| DR-6 Cross-reference integrity | pass | UI-only architecture and existing persistence/IPC retained; ST rows unchanged; A-6 exception explicitly recorded. |
| DR-7 Evidence freshness | pass | Gated diff equals tested d0fff4e; lockfiles, registry and framework identity match. CHROME_LOOK has explicit original look identities and surface-equivalence explanation, detailed in E6. |
| DR-8 Completion vs residual risk | pass | Ready-for-review SSOT and unchecked H2 retain the review boundary; this report rejects full intent achievement because F1 remains. |
| Naming / template / YAML | pass | Canonical destination derived; requested 2.2 frontmatter, round 1 and review sections populated. |

### Post-Implementation / Adversarial Review (PR / AV)

| Check | Result | Evidence |
|---|---|---|
| Evidence bundle / FAIL_TO_PASS / runnable command definitions | pass | Handoffs and walkthrough retain decisive assertion Red, later Green, repeat results and exact runner definitions. Only plan verifiers rerun here. |
| AV-1 Failing-then-passing proof | pass | AC-69.5 begins with missing aria-pressed; both AC-70.2 sizes failed aria-current at Red; D-22 moved-and-returned case failed first. Pure new module's initial import Red is disclosed, not misrepresented as behavior Red. |
| AV-2 No bypass hacks | pass | No assertion mocking/early return; observer and fetch setup are declared seams; actual UI assertions remain. |
| AV-3 Changed paths asserted | partial | Header state, emphasis and rail paths asserted; F1's delayed availability/geometry sequence not asserted. |
| AV-4 No skip/xfail masking | pass | All changed-suite tests remain ordinary cases; authoritative E2E 0 skipped/flaky. |
| AV-5 No unresolved placeholders | pass | Source reads and recorded source-audit show no product placeholder; no pending test substituted for a requirement. |
| AV-6 Source-backed criteria | pass | Plan/canon sources and D-22 explanation intact; A-3/A-4/A-5/A-6 record USER_EXPLICIT decisions. |

### IR-5 test-by-test grading

The following line lists identify every case in each changed suite. **Strong** means specific assertions on actual collaborators/state/geometry; **Adequate** means a narrower source, visibility, registration or broad-output check. No case is rated Weak. F1 is a missing lifecycle case, not a claim that the existing positive geometry test cannot fail.

| Suite | Strong cases (test start line) | Adequate cases (test start line) / limits |
|---|---|---|
| `header-toggles.test.ts` (8) | 36, 50, 135, 154, 160, 172, 181, 202 | None; panel/pressed equivalence at every transition, keyboard/mouse focus, exact names and palette navigation. |
| `settings-tail-spacer.test.ts` (6) | 26, 32, 51, 61 | 20 export/margin check; 71 registration/source check. Pure fixpoint does not exercise hook restart. |
| `settings-emphasis.test.tsx` (3) | 166, 217, 226 | None for their intended assertions; supported Startup geometry measurement is not claimed by these class/state cases. |
| `settings-rail.test.tsx` (29) | 141, 157, 166, 183, 219, 231, 258, 290, 327, 353, 389, 408, 420, 434, 454, 465, 488, 499, 574, 588, 611, 639, 713, 729, 746 | 192 layout class/presence; 206 group/order/presence; 651 strong numerical assertions but only one effect lifetime (F1); 683 rendered margin token check. |
| `chrome-zorivest.test.ts` (20) | 56, 94, 175, 186, 192, 204, 215, 253, 262, 270, 320, 328 | 18, 31, 39, 49, 66, 87, 284, 312: bounded source/token/control-presence checks. Strong runtime partners cover the changed header behavior. |
| `app-shell-wiring.test.ts` (2) | 102 | 71: navigation is concrete; clipboard length / any settings request are broad, supplemented by chrome:328 and Electron C1-5's exact payload checks. |
| `console-chrome.test.ts` (9) | 26, 47, 61, 77, 114, 177 | 34, 97 visibility/control checks; 136 class contract. No old case changed. |
| `settings.test.ts` (12) | 118, 157, 215, 229, 258, 283, 303, 328, 484, 492, 529 | 128 visibility smoke. Real geometry/current/slow-scroll assertions are strong; unpackaged launch intentionally excludes supported Startup. |

`test-ids.ts` is a registry, not an executable test suite. The separately sampled, unchanged AC-43.3 oracle is Strong: computed 80-row label matrix, minimum threshold, exact baseline equality and deliberate negative contrast mutations.

## Answers to E1–E6

### E1 — AC mapping and negative oracles

All 16 owner AC rows are present in the handoffs and have production/control plus test mappings. **No test is intrinsically unable to fail.** Regression-only cases can correctly pass on the old implementation (Ctrl+K, click lock, scroll-mt-4); this is disclosed in Red evidence and does not make them vacuous. Coverage is incomplete for the effect-restart lifecycle behind AC-70.2/70.4 (F1), so the blanket claim of satisfying every supported state cannot be approved.

| AC | Production / control owner | Test and actual negative oracle |
|---|---|---|
| AC-69.1 | Header:55-68 | header-toggles:36,50; missing/incorrect aria-pressed, variants, name or icon fails. |
| AC-69.2 | AppShell:43,49-89,257,280; Header prop | header-toggles:135,154; panel/pressed mismatch after each route or persisted launch fails. |
| AC-69.3 | Native Button plus existing shell events | header-toggles:160,172; Enter/Space failure or focus movement fails. |
| AC-69.4 | Header:70-85; existing OPEN_PALETTE_EVENT | header-toggles:181,202; old label/name, missing hint/shortcut/icon, changed adjacency or palette failure fails. |
| AC-69.5 | Built shell/header | console-chrome:177; aria-pressed first, panel lifecycle and all box axes within 0.5 px; Commands opens palette. |
| AC-69.6 | TA-1/TA-2 diff fence | validate-task.sh ta-check compares complete removed/added lists; independently verified exact diff here. |
| AC-70.1 | spacer:10,29,48 | tail-spacer:20,26,32,51,61; exact values, fixpoint and invalid fields fail on wrong arithmetic. |
| AC-70.2 | Page:369,1050; spacer hook; Rail current/recheck | settings E2E:484,492 via trailReach:453; every entry, one current and final MCP top 0–17 px. Missing restart/remeasure sequence: F1. |
| AC-70.3 | Rail:183-206 | settings-rail:574,588,611; silent observer bottom, lock preservation/release, listener-set removal fail on omissions. |
| AC-70.4 | Page spacer last child; spacer:70-126 | settings-rail:639,651,683; position/aria-hidden, zero fallback, exact height/re-measure and all rendered scroll margins. F1 escapes because effect never restarts with a retained height. |
| AC-70.5 | Rail active effect; Page current props; shared helper | emphasis:166,217; exactly one matching section and rail, precise current/idle/base tokens, no forbidden classes/aria-current. |
| AC-70.6 | shared frame base/current colors | settings E2E:529; explicitly different Download/Capture current samples, document-coordinate boxes, computed colors and >16 px gaps. |
| AC-70.7 | unchanged existing Settings/Startup behavior | Existing Settings suites plus Electron AC-58.12/A-6 and baseline diff; regressions fail normally, not waived. |
| AC-70.8 | Page literal ID; registry EOF | tail-spacer:71 plus existing AC-51.6; missing/misplaced/duplicate registration fails. |
| AC-70.9 | Page:946 and StartAtSignInControl shared frame | emphasis:226; supported Startup is uniquely current, clears, and matches another frame's token sets. |
| AC-70.10 | revealSection:46-77 | settings-rail:713,729; scroll-event case must stay one call; no-event case must be smooth then auto. |

### E2 — TEST_AMENDMENTS and old tests

**TA-1 and TA-2 are exact.** The baseline diff changes only the AC-26.4 title and `/Settings:/` → `/Commands/` in chrome-zorivest, and that regex in app-shell-wiring. Ctrl+K and all other assertions remain. Existing Settings tests are unchanged: settings-rail has only the added revealSection import above its old body plus appended cases; settings.test.ts and console-chrome.test.ts add at EOF; test-ids.ts appends at EOF. Other regression suites have no diff.

The literal statement that every other existing expectation is unchanged has **one disclosed, authorized exception**: A-6 changes sixteen values in the existing contrast-matrix.json outside TEST_AMENDMENTS. No other pre-existing assertion or matrix row changed. AC-70.7's Settings regressions remain intact; this is not a silent amendment of them.

### E3 — D-22 and click ownership

**Yes.** D-22 replaces position equality with whether any scroll event occurred, which distinguishes moved-and-returned from never-started. The listener is removed on timeout and cancellation; disconnected target is not jumped; reduced motion still uses auto directly. AC-70.10 proves both sides with exact call arrays/counts. The existing AC-58.12 and A-6 slow-scroll tests remain unchanged and passed in the recorded gate. holdUntilScrollSettles/current()/reconcile behavior is unchanged; the new recheck respects the same lock. No evidence of loss of the Session 27 fallback or click ownership was found.

### E4 — TAIL_SPACER / SCROLL_RECHECK

**Correct for a single effect lifetime, incomplete across the supported Startup lifecycle (F1).** The formula is the approved minimal tail height. One spacer sits after MCP; no gaps are inserted between sections. Only the fixed main and frames are observed, not the spacer/column. Measurements are frame-coalesced; observer, window listener and pending rAF are cleaned up. The rail's new passive listener is coalesced and removed, its pending rAF canceled, and it uses the existing at-bottom selection under the existing click lock. No direct observer loop or listener leak was found statically; recorded Electron has no reported loop failure. The required correction is to carry the rendered spacer identity through observer recreation, not to change A-2/D-9 or add inter-section space.

### E5 — A-3 / A-4 / A-5 / A-6

**A-3 is in scope and accessible on source inspection.** Only the group heading p classes change. The same heading ID still labels role=group; it is not focusable or inside a link/button, gains cursor-default/select-none and a token tint, and has no hover state or click handler. The appended test:746 asserts the inert tag, no tabindex/interactive ancestor, exact key style tokens and no hover classes. Existing group wiring remains byte-identical in the diff. The human looked and approved it.

**A-4** records the accepted external framework drift; the current registry hash and framework HEAD match attempt 4. **A-5/A-6 are minimal and correctly disclosed:** one light --color-accent-cyan token is ported, leaving light --color-accent unchanged; then exactly sixteen light Processing/Downloading cyan ratios are updated, eight label and eight advisory icon values. No test code/threshold/named set changed. At queue-primitives.test.ts:420-451, AC-43.3 still computes from the actual token CSS, requires all 80 labels >= CONTRAST_MIN, compares the complete matrix, and tests sensitivity with adverse mutations. Updated labels are 10.65–12.74, above 4.5; icons are advisory and 4.43–5.36. Re-baselining does not erase the contrast threshold oracle. A-6 is an explicit human-approved data-scope exception to the original two-hub boundary.

### E6 — authoritative gate and look provenance

**WINDOWS_GATE binding: yes.** Tested commit is `d0fff4e451378d689dadde8ae5092ba8607d5ce9`; all complete GATED_PATHS are equal to reviewed HEAD, and the only untracked file is outside that set. All seventeen ordered stages record exit 0. source-audit explicitly normalizes rg no-hits exit 1 to successful stage exit 0. Raw counts agree: pytest 629/0 with carried floor 629; Vitest 774/774/0 failed/0 pending >=748; Electron 131 expected / 0 unexpected / 0 skipped / 0 flaky >=127. Electron stage duration is 147.6 s. Three lockfile hashes match current files, as do registry hash and framework HEAD. This is a recorded complete run, not a wrapper-only pass or reviewer rerun.

**CHROME_LOOK: provenance is explicit, with a qualified identity rather than a fresh look at the exact final SHA.** walkthrough.md:138 onward records K1–K5, Mat, USER_EXPLICIT, date, dev app and large screen, quoting “K1 through K5 looks as expected” and the later heading approval. It honestly identifies the original looks as code of 9adbc3c and 3dc8fd2, and names final tested d0fff4e. Source diffs support its surface-equivalence rationale: A-3 was separately looked at; A-5 affects queue cyan while these K surfaces use unchanged --color-accent; A-6 is test data. I accept that scoped provenance as evidence of the requested surfaces; I do not claim a new human look on d0fff4e itself. It does not cover F1's supported delayed-Startup scenario.

### Durable reviewer evidence

```json
{"schema_version":"evidence.v1","check_id":"s31-exec-r1-plan-static","command":"rtk proxy python docs/execution/plans/2026-10-10-gui-polish-residuals/plan_checks.py static","cwd":"P:/av-kit","scope":"Session 31 plan-local static cross-reference verifier","phase":"review","exit_code":0,"result":"pass","tested_state":"e875a59a8e1e04f80a65ef516b1e0350fc01ead2; tracked targets unchanged","output":"PASS static: 20 task rows; scripts, plan cross-references and file targets agree","fresh":true}
{"schema_version":"evidence.v1","check_id":"s31-exec-r1-plan-selftest","command":"rtk proxy python docs/execution/plans/2026-10-10-gui-polish-residuals/plan_checks.py selftest","cwd":"P:/av-kit","scope":"Nine in-memory verifier negative fixtures","phase":"review","exit_code":0,"result":"pass","tested_state":"e875a59a8e1e04f80a65ef516b1e0350fc01ead2; tracked targets unchanged","output":"All nine injections reported; PASS selftest: every injected defect was reported","fresh":true}
{"schema_version":"evidence.v1","check_id":"s31-exec-r1-source-lifecycle","procedure":"Trace spacer state and effect-local applied across delayed supported Startup, then calculate the next height with the plan's valid geometry; compare against existing test fixtures and actual component callers.","observer":"gpt-6.1-sol","cwd":"P:/av-kit","scope":"AC-70.2/AC-70.4 TAIL_SPACER lifecycle","phase":"review","exit_code":null,"result":"fail","tested_state":"e875a59a8e1e04f80a65ef516b1e0350fc01ead2","output":"Effect restart retains height 384 but resets applied to 0; viewport 800/tail 300/margin16 computes100 instead of484; last top at max scroll400 instead of16. Static derivation, no product execution.","fresh":true}
{"schema_version":"evidence.v1","check_id":"s31-exec-r1-gate-inspection","procedure":"Compare all GATED_PATHS from tested commit to HEAD with git diff --quiet; read current status, three lockfile hashes, framework HEAD and registry hash; inspect all 17 recorded stages and raw pytest/Vitest/Electron receipts.","observer":"gpt-6.1-sol","cwd":"P:/av-kit","scope":"Recorded authoritative Windows gate identity and results","phase":"review","exit_code":null,"result":"pass","tested_state":"e875a59a8e1e04f80a65ef516b1e0350fc01ead2; gate d0fff4e451378d689dadde8ae5092ba8607d5ce9 equivalent over GATED_PATHS","output":"Gated diff exit0, no output; all17 stages exit0; pytest629/0 floor629; Vitest774/774 failed0; Electron131 expected,unexpected0,skipped0,flaky0; ui-electron147.6s; lockfile and external identities match.","fresh":true}
```

## Verdict

**changes_required** — intent achieved **partial**. One evidence-backed High behavioral finding, F1, violates the MEU-70 trailing reach/remeasurement contract (AC-70.2 / AC-70.4, structured contract family AC-70). The other reviewed behaviors and recorded passing gate are supported. The verdict is based on product behavior and its missing regression coverage, not artifact bookkeeping or a request to revisit approved plan choices.

## Follow-up Actions and Residual Risk

1. Dispatcher: validate round/target/intent/verdict, then copy this report verbatim to the canonical implementation-critical-review file and record round 1 once.
2. Author: address F1 through `/execution-corrections`. Retain actual spacer height across effect reconfiguration. Write the delayed supported-Startup plus later geometry regression first, using realistic scrollHeight that includes the committed spacer; assert the exact height, final MCP reach and cleanup.
3. Run affected unit/Electron checks, then a fresh authoritative WINDOWS_GATE after the gated code/test change. Preserve old Settings specs, D-22's two-sided fallback oracle, A-6 click lock and the already-approved amendments. Obtain current human look evidence for any changed visible surface.
4. Return for independent round 2 with the correction and bound receipts. H1-7/H2 remain the author's work; this reviewer did not alter their state or implement the fix.

Residual limits: F1 is established by source/state arithmetic and a concrete reachable lifecycle, not a newly run browser reproduction. The recorded gate tests unpackaged Electron; supported Startup is asserted separately in jsdom, without this spacer lifecycle. No general ResizeObserver-loop proof or packaged GUI pass is claimed beyond the inspected evidence. No additional out-of-contract finding is requested.

Completion-preflight was consulted for this review deliverable. The canonical task was read: implementation/H1-6 rows are checked, independent review and H2 rows remain unchecked. The requested static-only, receipts-only review overrides product-validator execution and the workflow timestamp script/final-line suggestion. This report completes the review request; it does not declare Session 31 DONE.


## Recheck (2026-10-14) — Round 2

**Review mode:** execution. **Reviewer:** Codex `gpt-6.1-sol`, class `avkit_independent_reviewer` (OpenAI); implementation author: Claude Code (Anthropic). Loop: `s31-exec-2026-10-10-gui-polish-residuals`. **Verdict: approved. Current findings_count: 0.**

### Intent Anchor

> Session 31 delivers MEU-69 (header Console toggle state, Commands palette button) and MEU-70 (Settings trailing-section rail fix and current-section emphasis), UI only, with no change outside ui/ and the two hub docs.

**Intent achieved: yes.** The retained-spacer lifecycle defect is corrected and covered by a meaningful regression. The complete corrected implementation satisfies the reviewed contract, including the explicitly disclosed A-6 data-scope amendment. No new Critical, High, Medium or Low finding survives this round.

### Round 1 findings recheck

| Finding | Prior status | Recheck result | File:line evidence |
|---|---|---|---|
| F1 — High, blocking; retained spacer loses measurement identity on effect restart (AC-70.2 / AC-70.4, TAIL_SPACER) | open | **Closed (fixed).** Applied height now survives section-key effect restarts; subsequent geometry changes subtract the committed spacer. The new mounted-page regression fails with the old local bookkeeping and asserts the corrected height and derived final reach. | `ui/src/renderer/src/features/settings/settings-tail-spacer.ts:74`, :98, :105–107, :128; `ui/tests/unit/settings-rail.test.tsx:765`, :801–818; correction `0cfa40a9790b92ac7349fd6a66e2c4f1924db5a6`. |

The former trace now gives the right answer: after the 384 px spacer is committed and supported Startup changes the key string, `applied.current` remains 384. At viewport 800, `belowLastTop = 1884 - 384 - 1200 = 300`, giving `800 - 16 - 300 = 484`. Maximum scroll is 1184 and MCP's top is 16 px. The regression supplies scrollHeight including the committed 384, delays the actual login-item promise, verifies Startup was absent and then appears, and asserts the real rendered spacer height before deriving MCP reach. That last assertion uses the production result; it is not an unconditional arithmetic pass.

The fake observer removes disconnected callbacks from its live set, so measurements after the restart reach the replacement observer rather than accidentally repairing the old effect. Recorded Red is `expected 100 to be 484` (walkthrough.md:173); the raw attempt-5 Vitest JSON names this exact test with `status: passed` and empty failureMessages. This is a static recheck plus recorded execution evidence, not a reviewer-run browser reproduction. Existing cleanup is retained at spacer:123–126.

### Findings

**None new; none open.** F1 is closed in the historical recheck table above and is not a surviving finding in this round's structured `findings: []`. No nearby-mutation escalation or new bookkeeping gate is requested.

### Scope and reviewed identity

Reviewed baseline `06e870bcb79fc4a1b689f5ddbe3c8c5b1a718ea1` → HEAD `a1d8f795e0ec92e93140ea50aba291f84b5e9087`, including the full product/test diff, both MEU handoffs, approved plan and plan-review disposition, task/walkthrough/decisions/census, Windows result, runner definitions and plan-local verifier. Both MEUs form one correlated delivery; neither handoff was omitted. Canon sampling included the two hubs, ST1–ST5, the two issue records and Session 27's A-3/A-6.

Full diff: **37 files, 2735 insertions, 94 deletions**. It contains 17 ui/ files, two hub docs, .agent state/handoffs (including the prior review), docs/BUILD_PLAN.md's SSOT render, this plan's notes, and the **explicit A-6 exception** in the earlier contrast-matrix.json. No backend/API/MCP/tools/main-process product path changed. The goal boundary is not silently broadened: A-6 is the stated human-approved data-only exception the review request expressly asks to assess.

Only untracked `.claude/settings.local.json` is present; it is unrelated and outside GATED_PATHS. No tracked working-tree change was observed. Global git-ignore permission warnings were retained in the status receipt and do not hide a tracked diff. No repository file was written. Output is exclusively `C:/Temp/av-kit/dispatch/s31-exec-review-report.md`; the dispatcher owns the verbatim copy to the canonical rolling report. The Round 1 body above remains unchanged; only frontmatter is updated and this recheck is appended.

### Commands executed and decisive output

All commands ran from `P:/av-kit`, with unfiltered `rtk proxy`, all-stream receipts under `C:/Temp/av-kit/s31-r2-*.txt`, immediate saved `$LASTEXITCODE` and propagation. Bounded file observations used `rtk proxy pwsh -NoProfile -Command 'Get-Content ...'`; source inventories used `rtk proxy rg -n ...`. The shell bootstrap also used `rtk proxy powershell` to load terminal-preflight and output-evidence-policy. Read-only PowerShell JSON selection and Get-FileHash inspected existing data; no project validator was invoked.

| Executed command / observed procedure | Exit | Result |
|---|---:|---|
| `rtk proxy git status --short` | 0 | Only `?? .claude/settings.local.json`; tracked tree unchanged. |
| `rtk proxy git log -6 --format=%H%x20%s` | 0 | HEAD a1d8f79; correction 0cfa40a; prior report 704a02e. |
| `rtk proxy git show --format=fuller 0cfa40a -- ui` | 0 | Only persistent applied-height ref and one appended regression. |
| `rtk proxy git diff --stat 06e870bcb79fc4a1b689f5ddbe3c8c5b1a718ea1 HEAD` | 0 | 37 files; scope classified above. |
| `rtk proxy git diff 06e870bcb79fc4a1b689f5ddbe3c8c5b1a718ea1 HEAD -- ui/src/renderer/src/components/layout ui/src/renderer/src/features/settings/SettingsPage.tsx ui/src/renderer/src/features/settings/StartAtSignInControl.tsx ui/src/renderer/src/styles.css docs/build-plan docs/execution/plans/2026-08-28-p10-queue-card-foundations/contrast-matrix.json` | 0 | Header/state/frame wiring, two hub edits, one token and exactly 16 ratio substitutions. Other changed production owners were read in full. |
| `rtk proxy git diff --unified=0 06e870bcb79fc4a1b689f5ddbe3c8c5b1a718ea1 HEAD -- ui/tests/unit/app-shell-wiring.test.ts ui/tests/unit/chrome-zorivest.test.ts ui/tests/unit/settings-rail.test.tsx ui/tests/e2e/settings.test.ts ui/tests/e2e/console-chrome.test.ts ui/tests/e2e/test-ids.ts` | 0 | Amendments exact; rail import at baseline :9 plus append after :517; other append sites :144, :372 and :405. |
| `rtk proxy git diff 06e870bcb79fc4a1b689f5ddbe3c8c5b1a718ea1 HEAD -- ui/tests/unit/chrome-zorivest.test.ts ui/tests/unit/app-shell-wiring.test.ts` | 0 | Exactly the approved title plus two regex substitutions; Ctrl+K and all other assertions intact. |
| `rtk proxy git diff --name-only 06e870bcb79fc4a1b689f5ddbe3c8c5b1a718ea1 HEAD -- packages mcp-server tools ui/src/main openapi.committed.json` | 0 | Empty output; frozen product paths unchanged. |
| `rtk proxy git diff --name-only 0cfa40a9790b92ac7349fd6a66e2c4f1924db5a6 HEAD` | 0 | Only this plan's review-prompt-exec.md, task.md, walkthrough.md and windows-gate-result.json. |
| `rtk proxy git diff --quiet 0cfa40a9790b92ac7349fd6a66e2c4f1924db5a6 HEAD -- <GATED_PATHS below>` | 0 | Empty output; all gated tracked inputs identical. |
| `rtk proxy git -c safe.directory=P:/agentic-framework -C P:/agentic-framework rev-parse HEAD` | 0 | e387decb45e5106efbb1c55747131e7ca45918c4; matches gate. No git configuration written. |
| `rtk proxy pwsh -NoProfile -Command 'Get-FileHash ui/package-lock.json,mcp-server/package-lock.json,uv.lock,P:/.agent/model-registry.json -Algorithm SHA256 ...'` | 0 | All four current hashes match gate; complete observed values below. |
| Read raw s31-win-vitest.json and s31-win-e2e.json with `Get-Content -Raw ... \| ConvertFrom-Json`; read pytest receipt tail | 0 | Vitest 775 passed / 775 total / 0 failed / 0 pending; Electron 131 expected / 0 unexpected / 0 skipped / 0 flaky; pytest 629 passed. Exact F1 regression is passed. |
| `rtk proxy rg -n '(^\|\s)(test\|it)\(\|test\.each\|it\.each\|\.skip\(\|\.only\(\|\.todo\(' <eight changed suites>` plus complete suite-body reads | 0 | 90 cases audited; no skip/only/todo entry. Per-case grading below. |
| `rtk proxy python docs/execution/plans/2026-10-10-gui-polish-residuals/plan_checks.py static` | 0 | PASS static: 20 task rows; scripts, plan cross-references and file targets agree. |
| `rtk proxy python docs/execution/plans/2026-10-10-gui-polish-residuals/plan_checks.py selftest` | 0 | All nine injected defects detected; complete output below. |

Complete GATED_PATHS arguments in the quiet comparison (identical to plan:137 and sh's gated list):

```text
ui packages mcp-server tests tools pyproject.toml uv.lock openapi.committed.json docs/build-plan/06-gui.md docs/build-plan/10-queue-card-ui.md docs/build-plan/11-page-layout.md docs/build-plan/build-priority-matrix.md docs/build-plan/gui-actions-index.md docs/proposals docs/execution/plans/2026-08-28-p10-queue-card-foundations docs/execution/plans/2026-09-02-p10-queue-card-migration docs/execution/plans/2026-09-03-p10-queue-card-dnd docs/execution/plans/2026-09-26-p11-layout-canon/implementation-plan.md .agent/context/grouping/2026-09-03-p11-page-layout-session-grouping.md .agent/model-registry.local.json .agent/model-registry.local.yaml docs/execution/plans/2026-10-10-gui-polish-residuals/validate-task.ps1
```

The only Python processes run were the two permitted plan-local commands. No tests, builds, npm, uv, pytest, Playwright, generators, validate-task.sh/.ps1 checks, timestamp script or closeout validator ran. Existing product results below are attributed to their receipts.

#### Permitted verifier output

```text
PASS static: 20 task rows; scripts, plan cross-references and file targets agree
exit: 0

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

### Checklist results

Manual entries below were observed by **gpt-6.1-sol**, **exit_code: null**. Procedure: read the actual production owners and all eight changed test suites, compare baseline diffs, trace positive/negative ACs and cleanup, and inspect the gate JSON/raw receipts and current input identity. “Pass” denotes this review's static/evidence result, not newly executed product tests.

| Check | Result | Evidence |
|---|---|---|
| IR-1 Live runtime evidence | pass | Fresh attempt 5 builds and runs real Electron; 131 expected and no failures/skips/flakes. Settings' declared fetch seam retains real DOM/layout; Console uses the actual shell. |
| IR-2 Stub behavioral compliance | n/a | No new persistence/backend stub. Observer/geometry seams test UI contracts. |
| IR-3 Error mapping | n/a | No route or write-adjacent API change. |
| IR-4 Fix generalization | pass | Shared applied identity survives effect recreation; both section producers share emphasis; fallback retains both sides and click ownership. |
| IR-5 Test rigor | pass | All 90 changed-suite cases graded below; F1 regression is meaningful and recorded passed. No Weak case identified. |
| IR-6 Boundary validation | n/a | No new REST/MCP/file/env/config write input. Pure geometry finite/range negatives are tested. |
| IR-7 Deferral and AC integrity | pass | All six AC-69 and ten AC-70 owner rows mapped; integration criteria use mounted collaborators/Electron. No missing or disguised deferred work. |
| DR-1 Claim/state | pass | Actual ref, appended regression, header, shared frames and rail agree with the corrected claims. |
| DR-2 Residual terms | pass | Settings is still a legitimate route/breadcrumb/palette command; old header text occurs as history/amendment data. |
| DR-3 Downstream references | pass | Both hubs updated; stable section/rail IDs and command registry retained. |
| DR-4 Verification robustness | pass | Distinct-current NO_SHIFT, silent-observer recheck, two-sided fallback and retained-spacer restart all have nonvacuous assertions. |
| DR-5 Auditability | pass | Decisive diffs, commands/exits, raw counts, identity and durable evidence are recorded here. |
| DR-6 Canon/architecture | pass | ST rows and save models untouched; no dependency-direction change; A-6 data exception explicitly disclosed. |
| DR-7 Freshness | pass | Gate 0cfa40a equals HEAD over every GATED_PATH; lockfiles, registry and external framework identities match. |
| DR-8 Completion/risk | pass | Approval covers implementation; H1-7 and H2-1/2/3 remain unchecked for dispatcher/author closeout. No Session DONE claim. |
| AV-1 Red→Green | pass | Original assertion Reds are retained; F1 correction records Red 100 vs 484 and its exact case passes in attempt 5. |
| AV-2 No bypass | pass | No assertion interception, skip or early success return. Declared observer/fetch fixtures retain real production state paths. |
| AV-3 Changed paths asserted | pass | Ref persistence is checked across actual delayed availability and later measurement; other changed paths map in E1. |
| AV-4 No masking | pass | All inventoried cases ordinary tests; raw Vitest pending 0 and Electron skipped/flaky 0. |
| AV-5 No placeholders | pass | Changed production reads and recorded source-audit are clean; no unfinished required behavior found. |
| AV-6 Source-backed criteria | pass | Plan/canon support the ACs; D-22 has source/diagnosis and A-3–A-6 are the disclosed decisions supplied in the review request. |
| Template/IR/PR artifact checks | pass | 2.2 frontmatter and round count; source labels, exact validation definitions, hub audit, handoffs and FAIL_TO_PASS are present. H2 is explicitly subsequent work. |

#### IR-5 per-test grading

Each listed number is the current test's start line in the named suite; every case is classified. Strong = specific values/state/geometry or meaningful negatives; Adequate = narrower source/token/presence/broad-output check. **No Weak cases.** A regression case passing on the original code does not make it unfailable.

| Suite (case count) | Strong cases | Adequate cases / limits |
|---|---|---|
| header-toggles.test.ts (8) | 36, 50, 135, 154, 160, 172, 181, 202 | None. |
| settings-tail-spacer.test.ts (6) | 26, 32, 51, 61 | 20 exports/margin; 71 ID/source registry. |
| settings-emphasis.test.tsx (3) | 166, 217, 226 | None; Startup state/classes are asserted, not packaged geometry. |
| settings-rail.test.tsx (30) | 141, 157, 166, 183, 219, 231, 258, 290, 327, 353, 389, 408, 420, 434, 454, 465, 488, 499, 574, 588, 611, 639, 651, 713, 729, 746, **765** | 192 layout source/classes; 206 groups/presence; 683 rendered margin tokens. :651 covers ordinary remeasurement; :765 adds restart and final-reach arithmetic using the actual rendered spacer. |
| chrome-zorivest.test.ts (20) | 56, 94, 175, 186, 192, 204, 215, 253, 262, 270, 320, 328 | 18, 31, 39, 49, 66, 87, 284, 312: source/control-presence checks with stronger runtime partners. |
| app-shell-wiring.test.ts (2) | 102 | 71: concrete navigation but broad clipboard/request checks; exact partners remain at chrome:328 and Electron C1-5. |
| console-chrome.test.ts (9) | 26, 47, 61, 77, 114, 177 | 34, 97 smoke/control visibility; 136 class contract. |
| settings.test.ts (12) | 118, 157, 215, 229, 258, 283, 303, 328, 484, 492, 529 | 128 visibility smoke. Supported Startup deliberately excluded in unpackaged Electron. |

test-ids.ts is an append-only registry, not a ninth suite. Separately sampled AC-43.3 remains Strong: independently computed matrix, 80 label threshold assertions, exact baseline equality and adverse contrast mutations.

### Answers to E1–E6

#### E1 — Every AC and negative oracle

**Yes. All 16 owner ACs map to production/control and a test that can fail. No intrinsically unfailable AC test was found.** AC-69.6 is an intentional static amendment fence, and AC-70.7 is an unchanged regression set, rather than new product behavior.

| AC | Production/control | Test and negative oracle |
|---|---|---|
| AC-69.1 | Header.tsx:55–68 | header-toggles:36,50; exact pressed state, constant name, non-ghost variants, border and icon. |
| AC-69.2 | AppShell.tsx:43,49–89,257,280 | header-toggles:135,154; panel/pressed equivalence after each route and persisted-open launch. |
| AC-69.3 | Native Button and shell toggle event | header-toggles:160,172; Enter/Space/mouse activation and retained focus. |
| AC-69.4 | Header.tsx:70–85 and OPEN_PALETTE_EVENT | header-toggles:181,202; rejects old name/text, missing hint/shortcut/icon, broken adjacency or palette opening. |
| AC-69.5 | Built shell/header | console-chrome:177; baseline-missing aria-pressed is first assertion, lifecycle and all box axes within 0.5 px. |
| AC-69.6 | TEST_AMENDMENTS fence, validate-task.sh:416–439 | Exact removed/added line lists; independent complete baseline diff confirms only the three approved pairs. |
| AC-70.1 | settings-tail-spacer.ts:10,29,48 | tail-spacer:20,26,32,51,61; 384/0/1, fixpoint and invalid-field/integer negatives. |
| AC-70.2 | SettingsPage.tsx:369,1050; spacer; rail recheck | settings Electron:484,492 via trailReach:453; every entry current, only one, MCP top within 0–17 px at max scroll at both sizes. |
| AC-70.3 | SettingsRail.tsx:183–206 | settings-rail:574,588,611; silent observer, bottom scroll, held/released ownership and listener-set removal. |
| AC-70.4 | Page's last-child spacer; corrected hook:70–130 | settings-rail:639,651,683,765; hidden placement, zero/no observer, resize and long-content zero, rendered margin, retained-height restart. |
| AC-70.5 | Rail:217–219 → Page current → both shared frame producers | emphasis:166,217; one matching current after render/click/keyboard/observer, exact current/idle/base tokens and forbidden-class negatives. |
| AC-70.6 | settings-section-frame.ts:11–29 | settings Electron:529; keys explicitly differ, document-coordinate geometry and computed colors, adjacent border-box gaps >16. |
| AC-70.7 | Existing Settings/Startup producers and unchanged rail lock | Existing Settings unit/real Electron cases, including AC-58.12 and A-6, remain unchanged and recorded passing. |
| AC-70.8 | Page literal ID; test-ids.ts EOF | tail-spacer:71 plus existing AC-51.6; missing/misplaced/duplicate registration fails. |
| AC-70.9 | Page:946 → StartAtSignInControl.tsx:83–86 | emphasis:226; supported Startup uniquely current, same tokens as page frames and clears on another selection. |
| AC-70.10 | SettingsRail.tsx:46–77 | settings-rail:713,729; exactly one smooth call after an event versus smooth+auto without one. |

Ctrl+K, the existing click lock and rendered scroll margin legitimately passed at initial Red as regression locks. The initial new-module import Red is disclosed separately and is not substituted for the behavior Reds. F1's previous lifecycle gap is now closed.

#### E2 — TEST_AMENDMENTS and unchanged tests

**TA-1 and TA-2 are applied exactly.** The baseline diff changes chrome-zorivest's title at :175 and /Settings:/ regex at :180, plus app-shell-wiring's regex at :84. Ctrl+K and all other assertions are unchanged.

settings-rail.test.tsx preserves its entire old body: one revealSection import plus appended cases (including A-3 and F1). Settings Electron, Console Electron and test IDs append only. Other pre-existing test files have no diff. The only pre-existing expectation changed beyond TA-1/TA-2 is the **explicitly user-approved A-6 contrast data amendment**, not an undisclosed Settings regression rewrite.

#### E3 — D-22 / REVEAL_FALLBACK and click lock

**Correct for the named race; both sides are proven by AC-70.10.** A scroller that moved and returned to its initial position has emitted an event; the fallback no longer jumps it back. With no event, the original hidden/throttled-window jump remains. Timeout and cancellation both remove the listener; disconnected targets are not jumped and reduced-motion uses auto directly.

The Session 27 A-6 hold/reconcile/current implementation remains unchanged. SCROLL_RECHECK observes the same clickLockUntil before changing active. The original AC-58.12 and deterministic 1.5 s A-6 scroll tests remain unchanged and are in the passing full Electron run. No regression of Session 27's jump or ownership contract was found.

#### E4 — A-2, spacer fixpoint and lifecycle

**Yes, within the declared Settings layout and inspected evidence.** One hidden spacer is after MCP only. With content extent B, last content-coordinate top T and actual spacer s, belowLastTop is (B+s)-s-T = B-T, so measurement is a fixpoint. F1 restores that s across key changes. The constant frame padding and gap-6 separation let each target leave its predecessor outside the top band; two Electron window sizes walk every entry.

The hook observes the fixed scroller and section boxes, never the spacer/column. It cancels/replaces pending frames, avoids equal-height writes, disconnects the observer and removes window resize on cleanup. Rail scroll work is passive and frame-coalesced; its listener and pending frame are removed on cleanup, with click-lock gating intact. No direct observer feedback loop or listener leak was identified. This is not a universal proof for arbitrary cyclic CSS or a newly run packaged app; the actual recorded real-Electron run passes.

#### E5 — A-3, A-5/A-6 and contrast

**A-3 is scoped, accessible and token-only.** SettingsRail.tsx:250–256 retains role=group with aria-labelledby pointing to the same inert p ID. The heading has no tabindex, handler or interactive ancestor; cursor-default/select-none, token tint and no hover treatment distinguish it from entries. settings-rail.test.tsx:746 checks the inert markup and key token/affordance negatives; unchanged wiring is independently confirmed in source/diff. The user separately looked and approved it, as recorded and supplied in this request.

**A-5 and A-6 are minimal and correctly disclosed.** One light --color-accent-cyan changes to #0e7490; --color-accent stays unchanged. Exactly 16 matrix ratio values change (eight light Processing/Downloading labels, eight advisory icons); no assertion/threshold/other matrix row is altered. At queue-primitives.test.ts:420–451 the 80 independently computed label ratios still must meet CONTRAST_MIN (4.5) and the whole matrix must match. Negative alpha/theme/label-token cases still test sensitivity. Updated labels are 10.65–12.74; the advisory icon ratios are 4.43–5.36. Rebaselining therefore retains the actual minimum-contrast oracle. A-4's framework drift is explicitly accepted and now matches the current external identity.

#### E6 — WINDOWS_GATE and CHROME_LOOK binding

**WINDOWS_GATE: yes.** Gate of record is attempt 5, tested_commit **0cfa40a9790b92ac7349fd6a66e2c4f1924db5a6**. The complete GATED_PATHS diff to reviewed HEAD is empty (exit 0), and current status has no gated dirt. All **17 stages** appear in order with exit 0; source-audit's rg no-hits exit 1 is explicitly normalized to stage 0. The runner clears ELECTRON_RUN_AS_NODE and builds the real app/harness before Electron.

Raw receipts agree with JSON: pytest **629 passed / 0 failed**, meeting carried floor **629**; Vitest **775 passed / 775 total / 0 failed / 0 pending**, above **748**; Electron **131 expected / 0 unexpected / 0 skipped / 0 flaky**, above **127**. ui-electron duration is **143.2 s**. F1's exact test is recorded passed. Current input hashes match:

```text
ui/package-lock.json       A86D9A42C6CBD98705E1720EDBD7666FED573581C07E21EA0F56379DC7332980
mcp-server/package-lock.json 62147DE51AFE855992D9BCA14364AFC03B493E8B02C478BA0F890B957DCA5095
uv.lock                    DA452C3481BC2C7B00BE49AB8DAA9747CC90CB27F17CCDD8EAE49D19063E7D20
P:/.agent/model-registry.json A7C95972C1E83885AA339873BDBF35CD5A6DAF3FB593F0D894F658BBFB80EBFA
P:/agentic-framework HEAD  e387decb45e5106efbb1c55747131e7ca45918c4
```

Node v24.19.0 and Electron 42.9.3 are recorded by the gate; I did not execute version commands. Approval relies on the observed run identity and current tracked/external file equivalence, not an invented second runtime run.

**CHROME_LOOK: qualified provenance, accepted.** walkthrough.md:138–166 records Mat, USER_EXPLICIT, 2026-10-14, dev app and large screen, K1–K5 all pass, plus the separate A-3 approval. It names original look code 9adbc3c / 3dc8fd2 and gate 0cfa40a; it does **not** claim a fresh human look at the final SHA.

Its no-new-look argument for F1 is sound for those looked-at surfaces: within one effect lifetime local storage and the ref compute identically; the changed path requires a section-list restart from supported Startup, absent in the unpackaged dev app. A-3 was itself looked at; A-5 affects the separate queue cyan token; A-6 is data. Corrected ordinary rail walking passes in Electron and supported delayed Startup is covered by the new mounted-page test. This accepts documented surface equivalence; it does not claim a packaged Startup visual check that never happened.

### Durable reviewer evidence

```json
{"schema_version":"evidence.v1","check_id":"s31-exec-r2-plan-static","command":"rtk proxy python docs/execution/plans/2026-10-10-gui-polish-residuals/plan_checks.py static","cwd":"P:/av-kit","scope":"Session 31 plan-local static verifier","phase":"review","exit_code":0,"result":"pass","tested_state":"a1d8f795e0ec92e93140ea50aba291f84b5e9087","output":"PASS static: 20 task rows; scripts, plan cross-references and file targets agree","fresh":true}
{"schema_version":"evidence.v1","check_id":"s31-exec-r2-plan-selftest","command":"rtk proxy python docs/execution/plans/2026-10-10-gui-polish-residuals/plan_checks.py selftest","cwd":"P:/av-kit","scope":"Nine in-memory negative verifier fixtures","phase":"review","exit_code":0,"result":"pass","tested_state":"a1d8f795e0ec92e93140ea50aba291f84b5e9087","output":"All nine injections reported; PASS selftest: every injected defect was reported","fresh":true}
{"schema_version":"evidence.v1","check_id":"s31-exec-r2-f1-recheck","procedure":"Compare correction 0cfa40a, trace retained state/ref through delayed supported Startup and the subsequent geometry change, read the appended regression and its exact case in the raw attempt-5 Vitest JSON.","observer":"gpt-6.1-sol","cwd":"P:/av-kit","scope":"AC-70.2/AC-70.4 spacer lifecycle correction","phase":"review","exit_code":null,"result":"pass","tested_state":"a1d8f795e0ec92e93140ea50aba291f84b5e9087","output":"F1 closed: ref retains384; belowLastTop1884-384-1200=300; viewport800 produces484; derived MCP top16. Recorded exact regression status passed, failureMessages[]. No reviewer product execution.","fresh":true}
{"schema_version":"evidence.v1","check_id":"s31-exec-r2-gate-inspection","procedure":"Compare complete GATED_PATHS from tested commit to HEAD with git diff --quiet, inspect status, current lockfile/registry hashes and framework HEAD, all17 ordered recorded stages, and raw pytest/Vitest/Electron outputs.","observer":"gpt-6.1-sol","cwd":"P:/av-kit","scope":"Authoritative attempt-5 full Windows gate freshness and results","phase":"review","exit_code":null,"result":"pass","tested_state":"a1d8f795e0ec92e93140ea50aba291f84b5e9087; gate0cfa40a9790b92ac7349fd6a66e2c4f1924db5a6 equivalent over GATED_PATHS","output":"Gated diff exit0, no output; all17 stages exit0; pytest629/0 floor629; Vitest775/775 failed0 pending0; Electron131 expected,unexpected0,skipped0,flaky0; ui-electron143.2s; current three lockfiles, registry and framework identities match.","fresh":true}
```

### Verdict

**approved — intent achieved yes; zero surviving findings.** F1 is fixed at the actual state-lifetime boundary and the regression catches the old failure. The full corrected work and bound authoritative gate support the intended header/Settings delivery. No additional correction round is needed.

### Follow-up actions and residual risk

1. Dispatcher: validate target/intent/round/verdict, copy this complete report verbatim to the canonical implementation-critical-review file and record round 2 once.
2. Author/orchestrator: finish H1-7 and the authorized H2 reflection, SSOT/issue resolution, metrics and completion checks. Carry D-22, A-3–A-6 and F1's correction into the appropriate closeout record. This reviewer edits none of those files.
3. No implementation correction is requested. No new gate/look run is requested for unchanged inputs. Future gated changes invalidate the applicable evidence as usual.

Residual limits: review is static; runtime results are inspected receipts. Supported delayed Startup has mounted-page geometry coverage rather than packaged real-Electron/human-look coverage. No universal observer-loop proof is claimed beyond the real layout, cleanup analysis and passing recorded runs. There are no unresolved material questions.

The terminal-preflight and completion-preflight skills were consulted. Canonical task state has implementation/H1-6 checked and four subsequent rows (H1-7, H2-1/2/3) unchecked; those remain author work. User-directed receipts-only/static-only scope overrides repository mutation, product-validator and timestamp-script suggestions. This completes the independent review deliverable, not the author's Session 31 closeout.
