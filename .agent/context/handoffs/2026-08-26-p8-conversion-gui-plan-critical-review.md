---
date: "2026-08-26"
review_mode: "plan"
target_plan: "docs/execution/plans/2026-08-26-p8-conversion-gui/implementation-plan.md"
verdict: "approved"
findings_count: 0
template_version: "2.1"
requested_verbosity: "standard"
agent: "gpt-5.6-sol"
round: 3
---

# Critical Review: p8-conversion-gui

> **Review Mode**: `plan`
> **Verdict**: `approved`

## Intent Anchor

Executing this plan is supposed to deliver MEU-33: a lazy, shell-reachable Convert page with the Downloader-shaped queue, Settings Convert card, safe AppShell command delivery, and Wave 8 Electron E2E proof, without starting MEU-27, adding Downloader-to-Convert, or rewriting REST/MCP. As written, the plan would deliver much of the GUI, but the blocking findings below leave required route, control-binding, settings-feedback, navigation-safety, and closeout contracts unproved or explicitly omitted.

## Findings

| # | Severity | Confidence | Finding | File:Line | Recommendation | Status |
|---|----------|------------|---------|-----------|----------------|--------|
| F1 | High | High | **The route lock contradicts both GUI authorities.** The plan deliberately interprets “lazy like Transcript/TTS” as the current eager `createRoute` plus static import pattern. The Phase 8 SSOT says “lazy `/convert`,” and the Phase 6 GUI SSOT repeats that requirement. Executing the stated lock therefore omits a required deliverable rather than resolving a merely clerical naming difference. Violates PR-5 and PR-8. | `docs/execution/plans/2026-08-26-p8-conversion-gui/implementation-plan.md:104`; `docs/build-plan/08-video-conversion.md:521`; `docs/build-plan/06-gui.md:912` | Replace the eager-route lock with a real TanStack lazy route for `/convert`, retaining Downloader as the eager default, and add a source-backed assertion that proves the Convert module is route-loaded rather than statically imported. | open |
| F2 | High | High | **Wave 8 can false-pass materially incomplete E2E coverage.** `WAVE8_TESTIDS` plus `WAVE8_EXTRA_TESTIDS` enumerate 49 controls, but the script only requires registry text for most of them. Runtime same-expression bindings cover a small subset: page/dropzone, six W8-3 controls, browse/add/row, and four processor buttons. Cut/Extract controls, five presets, Advanced, GPU refresh, output/skip, reorder, reset/remove/clear confirms, open actions, Settings leaves, and others may be absent from the Electron test while the census passes. E2 requires presence, interactivity, and visual behavior for every created/modified interactive element; the p6 Downloader canon binds its full extra-control set in W1-3 and state controls in W1-5. Violates E2, PR-4, and PR-8. | `docs/execution/plans/2026-08-26-p8-conversion-gui/named-sets.json:123`; `docs/execution/plans/2026-08-26-p8-conversion-gui/assert-e2e-control-census.ps1:50`; `.agent/docs/emerging-standards.md:1167`; `docs/execution/plans/2026-08-20-p6-gui-downloader/assert-e2e-control-census.ps1:51` | Make the Wave 8 cases and census bind every named interactive control to an appropriate same-expression visual and interaction/state oracle. Registration in `test-ids.ts` is necessary but not sufficient. | open |
| F3 | High | High | **G11 RULE-3 has no NavRail negative oracle.** AC-33.2 proves only that `Ctrl+4` does not fire `convert:add`; W8-2 requires `convert-page` visibility plus the text `nav-convert`, not a bound click. An implementation that makes the NavRail Convert click both navigate and POST on the same tick can satisfy every stated check. This is the exact carry-forward risk: “Convert GUI must not sync-dispatch convert on the same tick as rail navigation.” Violates PR-8 and Session 14 RULE-3. | `docs/execution/plans/2026-08-26-p8-conversion-gui/implementation-plan.md:218`; `docs/execution/plans/2026-08-26-p8-conversion-gui/assert-e2e-control-census.ps1:96`; `docs/execution/reflections/2026-08-26-p8-conversion-api-mcp-reflection.md:102` | Name the production chain `NavRail` click → `onNavigate` → `navigateShell(CONVERT_HOME)` only. Add a bound click oracle that reaches `convert-page` and a request-count negative asserting zero conversion POSTs on the navigation tick. Keep delayed delivery only for explicit `convert:*` commands. | open |
| F4 | High | High | **Mandatory G23 Settings work is disguised as out of scope (C2 SKIP).** The Settings Convert card persists data via debounced PUT, yet the plan says not to create the absent form-guard surface and marks it out of scope. G23 makes dirty detection and visual save feedback L1/L2 mandatory for every persisted form; only L3 is list-detail-only. “Files absent” and “uses debounce” are not an evidence-backed exception. Violates PR-5 and PR-7/C2. | `docs/execution/plans/2026-08-26-p8-conversion-gui/implementation-plan.md:122`; `docs/execution/plans/2026-08-26-p8-conversion-gui/implementation-plan.md:160`; `docs/execution/plans/2026-08-26-p8-conversion-gui/implementation-plan.md:313`; `.agent/docs/emerging-standards.md:678` | Put G23 L1/L2 and their tests into AC-33.16 for the persisted Settings card; keep only L3 as N/A. If the av-kit debounce architecture needs a materially different feedback contract, obtain and cite a valid `Human-approved` exception instead of treating absent files as authority. | open |
| F5 | High | High | **The final closeout row is a demonstrated false-passing gate.** H2-4 says it re-runs handoff, review, reflection, metrics, and drift checks, but its command checks only handoff markers, execution-review verdict, and `render --check`. It does not run the handoff AC script, reflection markers, or metrics assertion, and it never writes its declared `C:/Temp/av-kit/closeout-check.txt`. Missing/deleted reflection or metrics artifacts can therefore pass the final completion-preflight row. Violates PR-4 and DR-4. | `docs/execution/plans/2026-08-26-p8-conversion-gui/task.md:64`; `docs/execution/plans/2026-08-26-p8-conversion-gui/named-sets.json:204` | Make H2-4 execute the named handoff marker and AC scripts, `CHECK_EXEC_REVIEW`, reflection-marker check, metrics check, and drift check, then capture the combined result at the declared closeout receipt. `tools/validate_closeout_artifacts.py` remains correctly absent. | open |
| F6 | Medium | High | **The Help criterion does not cover the cited G26 contract.** The plan requires topic text and adds `converter` to the shared union, but it does not require the three-section/equivalent content structure, authoritative learn-more support, dismiss/re-show behavior, or `aria-labelledby`. The current shared `HelpCard` lacks those latter surfaces, so reuse alone does not close the gap. | `docs/execution/plans/2026-08-26-p8-conversion-gui/implementation-plan.md:124`; `docs/execution/plans/2026-08-26-p8-conversion-gui/implementation-plan.md:234`; `ui/src/renderer/src/components/help/HelpCard.tsx:13`; `.agent/docs/emerging-standards.md:888` | Expand AC-33.18 and the files/tasks to cover the G26-equivalent content, persistence/re-show, accessibility, and authoritative-link contract, or cite a source-backed av-kit-specific exception. | open |
| F7 | Medium | High | **G33-G35 are mapped in prose but absent from the test contract.** AC-33.23 names only G30-G32 and G36; the task validations do not prove canonical motion tokens, button variant/size mappings, or the assigned feedback tiers. This leaves the §4A table advisory rather than TDD-enforced. | `docs/execution/plans/2026-08-26-p8-conversion-gui/implementation-plan.md:154`; `docs/execution/plans/2026-08-26-p8-conversion-gui/implementation-plan.md:165`; `docs/execution/plans/2026-08-26-p8-conversion-gui/implementation-plan.md:239` | Extend AC-33.23 (or split it) so Red tests and the MEU gate prove G33 duration/easing, G34 variant/size mapping, and G35 feedback-tier behavior for the planned controls. | open |
| F8 | Low | High | **PR-9 named-set ownership is restated inside scripts.** `assert-handoff-markers.ps1` claims marker names come from `named-sets.json` but hard-codes the seven markers. The E2E census likewise hard-codes `W8-1`–`W8-6` and repeated test IDs instead of consuming `E2E_CASES` and named control groupings. Current spellings agree, so this is clerical rather than blocking. | `docs/execution/plans/2026-08-26-p8-conversion-gui/assert-handoff-markers.ps1:1`; `docs/execution/plans/2026-08-26-p8-conversion-gui/assert-handoff-markers.ps1:23`; `docs/execution/plans/2026-08-26-p8-conversion-gui/assert-e2e-control-census.ps1:81`; `docs/execution/plans/2026-08-26-p8-conversion-gui/named-sets.json:177` | Read `HANDOFF_BUNDLE_MARKERS` and `E2E_CASES` from `named-sets.json`; add named per-case control groups if the E2E fix needs subsets. | open |
| F9 | Low | High | **The task frontmatter says `in_progress` although implementation is unstarted.** Every task row is unchecked and all correlated production/handoff/reflection artifacts are absent, so plan mode is still correct; the status is clerical drift. | `docs/execution/plans/2026-08-26-p8-conversion-gui/task.md:5`; `.agent/context/grouping/2026-08-24-p8-video-conversion-session-grouping.md:20`; `.agent/context/meu-status.yaml:898` | Set the task status to the project’s not-started planning value during `/plan-corrections`. | open |

## Scope

**Targets reviewed:** the full `docs/execution/plans/2026-08-26-p8-conversion-gui/` folder named by the user: `implementation-plan.md`, `task.md`, `named-sets.json`, and all four assertion scripts.

**Authority reviewed:** Phase 8 Convert Page and GUI notes; Phase 6 Wave 8, shell/nav/help, and GUI shipping gate; all `convert:*` action-index rows; Session 15 grouping; p6 Downloader local canon; Session 14 RULE-1/2/3; G11, G20, G23, G26, G30-G35, and E2; current harness override.

**Scope lock applied:** MEU-33 only. MEU-27/Session 8c, Downloader-to-Convert, REST rewrites, and MCP rewrites were not required. The absence of `docs/gui-element-reference.md`, GUI indexes, `.agent/docs/gui-standards-enforcement.md`, and `tools/validate_closeout_artifacts.py` was confirmed and was not itself treated as a finding.

## Commands Executed

Only permitted static review operations were used: redirected `Get-Content` reads, `Test-Path`, and redirected `rg` sweeps. No pytest, Vitest, Playwright, npm test, product build, or mutation command ran.

Key receipts:

- `C:/Temp/av-kit/p8-plan-1-200.txt`, `p8-plan-211-300.txt`, `p8-plan-301-386.txt`
- `C:/Temp/av-kit/p8-task-1-45.txt`, `p8-task-46-82.txt`
- `C:/Temp/av-kit/p8-named-sets.txt`, `p8-task-assert-scripts.txt`
- `C:/Temp/av-kit/auth-08-511-590.txt`, `auth-06-wave8.txt`, `auth-session14-reflection.txt`
- `C:/Temp/av-kit/sweep8-existence.txt`, `not-started-artifacts.txt`, `c2-meu-state.txt`
- `C:/Temp/av-kit/pr9-script-literals.txt`, `g23-census.txt`, `closeout-falsepass-census.txt`

## Checklist Results

### Information Retrieval (IR)

| Check | Result | Evidence |
|-------|--------|----------|
| All AC have source labels | pass | AC-33.1 through AC-33.24 have allowed source bases. F4 is a source-resolution conflict, not a blank label. |
| Validation cells are exact commands | fail | Most are exact and runnable, but H2-4 does not validate its claimed reflection/metrics surfaces or create its declared receipt (F5). |
| BUILD_PLAN audit row present | pass | Plan lines 319-325 and task row 5 bind MEU-33, preserve prior Phase 8 plans, and update Hub Next. |
| Post-MEU rows present | pass | H1 handoff/review and H2 reflection/metrics rows exist in dependency order. |
| Referenced artifacts exist or are scheduled | pass | Existing tools/templates were confirmed; Convert product/E2E/handoff artifacts are absent but explicitly scheduled. The absent generic closeout validator is not invoked. |

### Design / Documentation Review (DR)

| Check | Result | Evidence |
|-------|--------|----------|
| Scope and naming convention | pass | Plan folder, MEU-33 slug, handoff, reflection, and rolling execution-review names are coherent. |
| Template/frontmatter well formed | partial | Plan/task template versions exist; task `status: in_progress` conflicts with the unstarted state (F9). |
| Claim-to-authority match | fail | Eager route lock contradicts both lazy-route authorities (F1); G23 is incorrectly scoped away (F4). |
| GUI §4A mapping | partial | Absent indexes are handled by the documented fallback, but G26 and G33-G35 are not fully carried into testable ACs (F6-F7). |
| Closeout verification robustness | fail | H2-4 false-passes missing reflection/metrics and lacks its declared combined receipt (F5). |

### Plan Review (PR)

| Check | Result | Evidence |
|-------|--------|----------|
| PR-1 Plan/task alignment | pass | Both describe MEU-33 Red → Green → Wave 8 → handoff → SSOT → review → H2. |
| PR-2 Not-started confirmation | pass | All task rows are `[ ]`; Convert source, Wave 8 E2E, MEU handoff, execution review, and reflection are absent. F9 is clerical only. |
| PR-3 Task contract completeness | pass | Every executable row provides task, owner, deliverable, exact validation, dependency, context strategy, durable output, and status. |
| PR-4 Validation realism | fail | Wave 8 and final closeout can false-pass materially missing deliverables (F2, F5). |
| PR-5 Source-backed planning | fail | F1 and F4 contradict explicit authority; F6-F7 incompletely carry cited standards. |
| PR-6 Handoff/corrections readiness | pass | Single-MEU handoff and rolling execution-review paths are explicit. Round 1 has no correction-census precondition. |
| PR-7 C2 scope discipline | fail | MEU-27 is validly deferred and named deferrals are supported, but mandatory G23 L1/L2 work is mislabeled out of scope (F4). |
| PR-8 Control reachability/totality | fail | NavRail RULE-3 lacks a bound negative oracle, and E2E control coverage is materially incomplete (F2-F3). |
| PR-9 Single-statement discipline | fail | Marker, case, and test-ID clusters are repeated in scripts (F8, Low). |
| Wave 8 written and wired | fail | File/task wiring is planned, but the census does not bind every interactive control as E2 requires (F2). |
| G11 RULE-3 | fail | Palette/AppShell architecture is otherwise traceable, but NavRail click → zero same-tick POST is unproved (F3). |
| Empty reorder never `PUT []` | pass | Boundary inventory, `REORDER_BODY`, AC-33.12, and its negative oracle all require a full nonempty permutation and zero fetch for `[]`. |
| REST/MCP preservation | pass | AC-33.24 and task scope prohibit API/MCP edits and retain the Session 14 counts. |

## Open Questions / Assumptions

- No human decision is required to identify the current blockers. G23 may require a human-approved exception only if `/plan-corrections` determines that the mandated L1/L2 feedback is materially incompatible with av-kit’s debounced auto-save contract.
- The route finding treats the Phase 8 and Phase 6 uses of “lazy” as literal because both are explicit and Phase 6 separately defines non-Downloader routes as lazy-loaded.
- No requirement was added for Downloader-to-Convert, Session 8c, or REST/MCP rewrites.

## Verdict

`changes_required` — F1-F5 are evidence-backed High findings that would omit required deliverables or allow materially incomplete work to pass. Route fixes through `/plan-corrections`; do not begin execution on this round-1 verdict.

## Residual Risk

After the blockers are corrected, recheck the entire affected clusters rather than only edited lines: lazy routing, every Wave 8 control binding, all NavRail/shortcut/palette delivery paths, Settings persistence feedback, and the complete H2 closeout command. Round 2 must also satisfy the workflow’s blast-radius receipt plus per-hit disposition precondition before content re-review.

## Corrections Applied — 2026-08-26 (create-plan Step 5b / plan-corrections, after Round 1)

**Corrector:** coordinator (not the reviewer). Verdict set to `corrections_applied` only. Independent Round 2 must re-score. Product code, tests, and `docs/build-plan/` were not modified.

**Instruction conflicts (flagged, not silently picked):**

1. `plan-corrections.md` HARD STOP says timestamp-and-stop and do not auto-chain into `/plan-critical-review`. Driving workflow is `/create-plan` Step 5b with `.agent/context/harness.local.md` `plan_to_exec_gate: reviewer-auto`, which requires re-dispatch after the census. Re-dispatch proceeds under create-plan.
2. `named-sets.json` and `assert-*.ps1` are not listed in `plan-corrections.md` Write Scope; they are create-plan Step 4 plan-folder artifacts and were updated because F2/F5/F8 cannot be closed without them.
3. `docs/execution/plans/TASK-TEMPLATE.md` still defaults `status: "in_progress"`. F9 asked for the not-started planning value; this plan's `task.md` is now `draft` to match `implementation-plan.md`. The template was not edited.

### Finding dispositions (corrector claims; not an `approved` verdict)

| # | Change | Files |
|---|--------|-------|
| F1 | Replaced eager `createRoute` lock with `LAZY_CONVERT_ROUTE` (`lazyRouteComponent`, no static `ConvertPage` import; Downloader stays eager). AC-33.1 proves router source. | named-sets.json; implementation-plan.md; task.md row 2 |
| F2 | Census now binds every `WAVE8_TESTIDS`+`WAVE8_EXTRA_TESTIDS` id via named groups (`WAVE8_W8_1_VISIBLE`, `_W8_2_CLICK`, `_W8_3_*`, `_W8_4_*`, `_W8_5_ENABLED`) plus a totality `Test-HasBound` across `E2E_CASES`. W8-3 requires Cut/Extract/Advanced clicks and `nav-settings`. | named-sets.json; assert-e2e-control-census.ps1; AC-33.21; task.md row 3 |
| F3 | AC-33.2 names `NavRail` click → `onNavigate` → `navigateShell` only (zero same-tick `POST /conversions`). W8-2 requires `nav-convert` **click** + `WAVE8_POST_ZERO_ORACLE`. Ctrl+4 remains navigate-only. | implementation-plan.md; assert-e2e-control-census.ps1; task.md |
| F4 | Converter settings are `G23_CONVERT` L1+L2 (`FORM_GUARD_CSS`, `G23_SAVE_CLASS`, `G23_SAVE_LABEL_DIRTY`). PUT only on Save — not `schedulePut`. L3 stays N/A. Other settings namespaces remain MEU-23 debounce (out of this MEU, with basis). C2 SKIP / “files absent” withdrawn. | named-sets.json; implementation-plan.md locks/§4A/ACs/Out of Scope; task.md row 2 |
| F5 | H2-4 now runs handoff markers, `assert-handoff-acs.ps1`, reflection markers, metrics row, writes `CLOSEOUT_H24_RECEIPT`, then `CHECK_EXEC_REVIEW` and `render --check` (p6-gui-downloader pattern). | task.md H2-4; named-sets.json |
| F6 | AC-33.18 / `HELP_G26_AVKIT` = MEU-23 HelpCard ARIA + `HELP_COLLAPSE_KEY` + Spec 208–210. TaxHelpCard learnMore/dismiss is out-of-scope with Local Canon basis. `HELP_CONTENT_FILE` = `convert-help-content.ts`. | implementation-plan.md; named-sets.json |
| F7 | AC-33.23 expanded in place (still `RED_COUNT_33=24`): G33 duration tokens, G34 §4A variant/size, G35 T0/T1/T2 (Save is T2). | implementation-plan.md AC-33.23 / §4A |
| F8 | `assert-handoff-markers.ps1` reads `HANDOFF_BUNDLE_MARKERS`. Census reads `E2E_CASES` and Wave 8 named groups. | assert-*.ps1; named-sets.json |
| F9 | `task.md` frontmatter `status: "draft"`. | task.md |

### Blast-radius census (Step 5c / PR-6)

Index: `C:/Temp/av-kit/census-p8cg-index.txt`. Runner: `C:/Temp/av-kit/census-p8cg-runner.txt`. Unfiltered concat: `C:/Temp/av-kit/census-p8cg-ledger.txt`. Per-query receipts: `C:/Temp/av-kit/census-p8cg-01-old.txt` … `census-p8cg-25-new.txt`. Duplicate disposition copy: `C:/Temp/av-kit/census-p8cg-per-hit.md`.

Queries: 36. `rg -F -n` over `implementation-plan.md`, `task.md`, `named-sets.json`, `assert-e2e-control-census.ps1`, `assert-handoff-markers.ps1`. Zero-hit old/vacuous: 12 (`matching TTS/Transcript (eager import)`, invent form-guard, `do not invent them`, `G30–G32 + G36`, `status: "in_progress"`, `converter-help-content.ts`, `files absent; Convert is a queue`, hardcoded `foreach ($caseId in @('W8-1'`, hardcoded `'Acceptance Criteria',`, `createRoute`, `Zorivest form-guard.css`). Remaining hits dispositioned below. Sweep files were not truncated.

**09-old** still matches `task.md:64` because the repaired H2-4 cats `exec-review.txt` and `drift-check.txt` *after* writing `closeout-check.txt`. That is the p6-gui-downloader pattern, not the false-pass (which never wrote `closeout-check.txt` and never ran AC/reflection/metrics).

**19-old `schedulePut`:** five remaining hits are negatives / out-of-scope for other namespaces — confirmed-consistent.

Blast-radius census: 36 queries, plan+task+named-sets+two assert scripts, 12 updated-gone, remaining sites updated or confirmed-consistent as tabled.


| Receipt | File:Line | Disposition |
|---|---|---|
| census-p8cg-01-old.txt | (no hit) | updated-gone |
| census-p8cg-01-new.txt | `docs/execution/plans/2026-08-26-p8-conversion-gui/named-sets.json:178` | confirmed-consistent (named-set owner) |
| census-p8cg-01-new.txt | `docs/execution/plans/2026-08-26-p8-conversion-gui/implementation-plan.md:57` | updated |
| census-p8cg-01-new.txt | `docs/execution/plans/2026-08-26-p8-conversion-gui/implementation-plan.md:93` | updated |
| census-p8cg-01-new.txt | `docs/execution/plans/2026-08-26-p8-conversion-gui/implementation-plan.md:105` | updated |
| census-p8cg-01-new.txt | `docs/execution/plans/2026-08-26-p8-conversion-gui/implementation-plan.md:219` | updated |
| census-p8cg-01-new.txt | `docs/execution/plans/2026-08-26-p8-conversion-gui/implementation-plan.md:274` | updated |
| census-p8cg-01-new.txt | `docs/execution/plans/2026-08-26-p8-conversion-gui/implementation-plan.md:375` | updated |
| census-p8cg-01-new.txt | `docs/execution/plans/2026-08-26-p8-conversion-gui/task.md:45` | updated |
| census-p8cg-02-old.txt | (no hit) | updated-gone |
| census-p8cg-02b-old.txt | (no hit) | updated-gone |
| census-p8cg-02-new.txt | `docs/execution/plans/2026-08-26-p8-conversion-gui/named-sets.json:179` | confirmed-consistent (named-set owner) |
| census-p8cg-02-new.txt | `docs/execution/plans/2026-08-26-p8-conversion-gui/task.md:45` | updated |
| census-p8cg-02-new.txt | `docs/execution/plans/2026-08-26-p8-conversion-gui/implementation-plan.md:57` | updated |
| census-p8cg-02-new.txt | `docs/execution/plans/2026-08-26-p8-conversion-gui/implementation-plan.md:93` | updated |
| census-p8cg-02-new.txt | `docs/execution/plans/2026-08-26-p8-conversion-gui/implementation-plan.md:123` | updated |
| census-p8cg-02-new.txt | `docs/execution/plans/2026-08-26-p8-conversion-gui/implementation-plan.md:161` | updated |
| census-p8cg-02-new.txt | `docs/execution/plans/2026-08-26-p8-conversion-gui/implementation-plan.md:234` | updated |
| census-p8cg-02-new.txt | `docs/execution/plans/2026-08-26-p8-conversion-gui/implementation-plan.md:241` | updated |
| census-p8cg-02-new.txt | `docs/execution/plans/2026-08-26-p8-conversion-gui/implementation-plan.md:270` | updated |
| census-p8cg-03-old.txt | (no hit) | updated-gone |
| census-p8cg-03-new.txt | `docs/execution/plans/2026-08-26-p8-conversion-gui/implementation-plan.md:241` | updated |
| census-p8cg-04-old.txt | (no hit) | updated-gone |
| census-p8cg-04-new.txt | `docs/execution/plans/2026-08-26-p8-conversion-gui/implementation-plan.md:6` | updated |
| census-p8cg-04-new.txt | `docs/execution/plans/2026-08-26-p8-conversion-gui/task.md:5` | updated |
| census-p8cg-05-old.txt | (no hit) | updated-gone |
| census-p8cg-05-new.txt | `docs/execution/plans/2026-08-26-p8-conversion-gui/named-sets.json:231` | confirmed-consistent (named-set owner) |
| census-p8cg-05-new.txt | `docs/execution/plans/2026-08-26-p8-conversion-gui/implementation-plan.md:94` | updated |
| census-p8cg-05-new.txt | `docs/execution/plans/2026-08-26-p8-conversion-gui/implementation-plan.md:125` | updated |
| census-p8cg-06-old.txt | (no hit) | updated-gone |
| census-p8cg-06-new.txt | `docs/execution/plans/2026-08-26-p8-conversion-gui/named-sets.json:180` | confirmed-consistent (named-set owner) |
| census-p8cg-06-new.txt | `docs/execution/plans/2026-08-26-p8-conversion-gui/implementation-plan.md:57` | updated |
| census-p8cg-06-new.txt | `docs/execution/plans/2026-08-26-p8-conversion-gui/implementation-plan.md:93` | updated |
| census-p8cg-06-new.txt | `docs/execution/plans/2026-08-26-p8-conversion-gui/implementation-plan.md:123` | updated |
| census-p8cg-06-new.txt | `docs/execution/plans/2026-08-26-p8-conversion-gui/implementation-plan.md:161` | updated |
| census-p8cg-06-new.txt | `docs/execution/plans/2026-08-26-p8-conversion-gui/implementation-plan.md:234` | updated |
| census-p8cg-06-new.txt | `docs/execution/plans/2026-08-26-p8-conversion-gui/implementation-plan.md:257` | updated |
| census-p8cg-06-new.txt | `docs/execution/plans/2026-08-26-p8-conversion-gui/implementation-plan.md:318` | updated |
| census-p8cg-06-new.txt | `docs/execution/plans/2026-08-26-p8-conversion-gui/implementation-plan.md:378` | updated |
| census-p8cg-06-new.txt | `docs/execution/plans/2026-08-26-p8-conversion-gui/task.md:45` | updated |
| census-p8cg-07-old.txt | (no hit) | updated-gone |
| census-p8cg-07-new.txt | `docs/execution/plans/2026-08-26-p8-conversion-gui/named-sets.json:262` | confirmed-consistent (named-set owner) |
| census-p8cg-07-new.txt | `docs/execution/plans/2026-08-26-p8-conversion-gui/assert-e2e-control-census.ps1:2` | updated |
| census-p8cg-07-new.txt | `docs/execution/plans/2026-08-26-p8-conversion-gui/assert-e2e-control-census.ps1:70` | updated |
| census-p8cg-07-new.txt | `docs/execution/plans/2026-08-26-p8-conversion-gui/assert-e2e-control-census.ps1:72` | updated |
| census-p8cg-07-new.txt | `docs/execution/plans/2026-08-26-p8-conversion-gui/assert-e2e-control-census.ps1:108` | updated |
| census-p8cg-07-new.txt | `docs/execution/plans/2026-08-26-p8-conversion-gui/assert-e2e-control-census.ps1:155` | updated |
| census-p8cg-07-new.txt | `docs/execution/plans/2026-08-26-p8-conversion-gui/task.md:46` | updated |
| census-p8cg-07-new.txt | `docs/execution/plans/2026-08-26-p8-conversion-gui/implementation-plan.md:58` | updated |
| census-p8cg-07-new.txt | `docs/execution/plans/2026-08-26-p8-conversion-gui/implementation-plan.md:91` | updated |
| census-p8cg-07-new.txt | `docs/execution/plans/2026-08-26-p8-conversion-gui/implementation-plan.md:154` | updated |
| census-p8cg-07-new.txt | `docs/execution/plans/2026-08-26-p8-conversion-gui/implementation-plan.md:239` | updated |
| census-p8cg-08-old.txt | (no hit) | updated-gone |
| census-p8cg-08-new.txt | `docs/execution/plans/2026-08-26-p8-conversion-gui/assert-handoff-markers.ps1:1` | updated |
| census-p8cg-08-new.txt | `docs/execution/plans/2026-08-26-p8-conversion-gui/assert-handoff-markers.ps1:23` | updated |
| census-p8cg-08-new.txt | `docs/execution/plans/2026-08-26-p8-conversion-gui/assert-handoff-markers.ps1:25` | updated |
| census-p8cg-08-new.txt | `docs/execution/plans/2026-08-26-p8-conversion-gui/named-sets.json:291` | confirmed-consistent (named-set owner) |
| census-p8cg-09-old.txt | `docs/execution/plans/2026-08-26-p8-conversion-gui/task.md:64` | confirmed-consistent (H2-4 still cats exec-review+drift after writing closeout-check.txt; false-pass path is gone) |
| census-p8cg-09-new.txt | `docs/execution/plans/2026-08-26-p8-conversion-gui/task.md:64` | updated |
| census-p8cg-10-old.txt | (no hit) | updated-gone |
| census-p8cg-10-new.txt | `docs/execution/plans/2026-08-26-p8-conversion-gui/named-sets.json:178` | confirmed-consistent (named-set owner) |
| census-p8cg-10-new.txt | `docs/execution/plans/2026-08-26-p8-conversion-gui/implementation-plan.md:105` | updated |
| census-p8cg-10-new.txt | `docs/execution/plans/2026-08-26-p8-conversion-gui/implementation-plan.md:219` | updated |
| census-p8cg-10-new.txt | `docs/execution/plans/2026-08-26-p8-conversion-gui/implementation-plan.md:258` | updated |
| census-p8cg-10-new.txt | `docs/execution/plans/2026-08-26-p8-conversion-gui/implementation-plan.md:375` | updated |
| census-p8cg-10-new.txt | `docs/execution/plans/2026-08-26-p8-conversion-gui/implementation-plan.md:387` | updated |
| census-p8cg-11-new.txt | `docs/execution/plans/2026-08-26-p8-conversion-gui/assert-e2e-control-census.ps1:36` | updated |
| census-p8cg-11-new.txt | `docs/execution/plans/2026-08-26-p8-conversion-gui/assert-e2e-control-census.ps1:40` | updated |
| census-p8cg-11-new.txt | `docs/execution/plans/2026-08-26-p8-conversion-gui/assert-e2e-control-census.ps1:44` | updated |
| census-p8cg-11-new.txt | `docs/execution/plans/2026-08-26-p8-conversion-gui/named-sets.json:237` | confirmed-consistent (named-set owner) |
| census-p8cg-11-new.txt | `docs/execution/plans/2026-08-26-p8-conversion-gui/task.md:46` | updated |
| census-p8cg-11-new.txt | `docs/execution/plans/2026-08-26-p8-conversion-gui/implementation-plan.md:91` | updated |
| census-p8cg-12-new.txt | `docs/execution/plans/2026-08-26-p8-conversion-gui/implementation-plan.md:220` | updated |
| census-p8cg-13-new.txt | `docs/execution/plans/2026-08-26-p8-conversion-gui/named-sets.json:180` | confirmed-consistent (named-set owner) |
| census-p8cg-13-new.txt | `docs/execution/plans/2026-08-26-p8-conversion-gui/named-sets.json:181` | confirmed-consistent (named-set owner) |
| census-p8cg-14-new.txt | `docs/execution/plans/2026-08-26-p8-conversion-gui/task.md:45` | updated |
| census-p8cg-14-new.txt | `docs/execution/plans/2026-08-26-p8-conversion-gui/implementation-plan.md:57` | updated |
| census-p8cg-14-new.txt | `docs/execution/plans/2026-08-26-p8-conversion-gui/implementation-plan.md:94` | updated |
| census-p8cg-14-new.txt | `docs/execution/plans/2026-08-26-p8-conversion-gui/implementation-plan.md:125` | updated |
| census-p8cg-14-new.txt | `docs/execution/plans/2026-08-26-p8-conversion-gui/implementation-plan.md:162` | updated |
| census-p8cg-14-new.txt | `docs/execution/plans/2026-08-26-p8-conversion-gui/implementation-plan.md:236` | updated |
| census-p8cg-14-new.txt | `docs/execution/plans/2026-08-26-p8-conversion-gui/named-sets.json:184` | confirmed-consistent (named-set owner) |
| census-p8cg-15-new.txt | `docs/execution/plans/2026-08-26-p8-conversion-gui/implementation-plan.md:241` | updated |
| census-p8cg-16-new.txt | `docs/execution/plans/2026-08-26-p8-conversion-gui/assert-e2e-control-census.ps1:127` | updated |
| census-p8cg-16-new.txt | `docs/execution/plans/2026-08-26-p8-conversion-gui/named-sets.json:185` | confirmed-consistent (named-set owner) |
| census-p8cg-16-new.txt | `docs/execution/plans/2026-08-26-p8-conversion-gui/implementation-plan.md:239` | updated |
| census-p8cg-17-new.txt | `docs/execution/plans/2026-08-26-p8-conversion-gui/named-sets.json:244` | confirmed-consistent (named-set owner) |
| census-p8cg-17-new.txt | `docs/execution/plans/2026-08-26-p8-conversion-gui/task.md:64` | updated |
| census-p8cg-18-new.txt | `docs/execution/plans/2026-08-26-p8-conversion-gui/task.md:57` | updated |
| census-p8cg-18-new.txt | `docs/execution/plans/2026-08-26-p8-conversion-gui/task.md:64` | updated |
| census-p8cg-19-old.txt | `docs/execution/plans/2026-08-26-p8-conversion-gui/named-sets.json:180` | confirmed-consistent (negative: converter must not use schedulePut; other namespaces stay MEU-23) |
| census-p8cg-19-old.txt | `docs/execution/plans/2026-08-26-p8-conversion-gui/implementation-plan.md:123` | confirmed-consistent (negative: converter must not use schedulePut; other namespaces stay MEU-23) |
| census-p8cg-19-old.txt | `docs/execution/plans/2026-08-26-p8-conversion-gui/implementation-plan.md:234` | confirmed-consistent (negative: converter must not use schedulePut; other namespaces stay MEU-23) |
| census-p8cg-19-old.txt | `docs/execution/plans/2026-08-26-p8-conversion-gui/implementation-plan.md:257` | confirmed-consistent (negative: converter must not use schedulePut; other namespaces stay MEU-23) |
| census-p8cg-19-old.txt | `docs/execution/plans/2026-08-26-p8-conversion-gui/implementation-plan.md:318` | confirmed-consistent (negative: converter must not use schedulePut; other namespaces stay MEU-23) |
| census-p8cg-20-new.txt | `docs/execution/plans/2026-08-26-p8-conversion-gui/assert-e2e-control-census.ps1:123` | updated |
| census-p8cg-20-new.txt | `docs/execution/plans/2026-08-26-p8-conversion-gui/named-sets.json:233` | confirmed-consistent (named-set owner) |
| census-p8cg-20-new.txt | `docs/execution/plans/2026-08-26-p8-conversion-gui/task.md:46` | updated |
| census-p8cg-21-new.txt | `docs/execution/plans/2026-08-26-p8-conversion-gui/named-sets.json:180` | confirmed-consistent (named-set owner) |
| census-p8cg-21-new.txt | `docs/execution/plans/2026-08-26-p8-conversion-gui/named-sets.json:182` | confirmed-consistent (named-set owner) |
| census-p8cg-22-old.txt | (no hit) | updated-gone |
| census-p8cg-23-new.txt | `docs/execution/plans/2026-08-26-p8-conversion-gui/named-sets.json:184` | confirmed-consistent (named-set owner) |
| census-p8cg-23-new.txt | `docs/execution/plans/2026-08-26-p8-conversion-gui/implementation-plan.md:125` | updated |
| census-p8cg-23-new.txt | `docs/execution/plans/2026-08-26-p8-conversion-gui/implementation-plan.md:162` | updated |
| census-p8cg-23-new.txt | `docs/execution/plans/2026-08-26-p8-conversion-gui/implementation-plan.md:236` | updated |
| census-p8cg-23-new.txt | `docs/execution/plans/2026-08-26-p8-conversion-gui/implementation-plan.md:317` | updated |
| census-p8cg-24-new.txt | `docs/execution/plans/2026-08-26-p8-conversion-gui/implementation-plan.md:57` | updated |
| census-p8cg-24-new.txt | `docs/execution/plans/2026-08-26-p8-conversion-gui/task.md:45` | updated |
| census-p8cg-25-new.txt | `docs/execution/plans/2026-08-26-p8-conversion-gui/named-sets.json:181` | confirmed-consistent (named-set owner) |
| census-p8cg-25-new.txt | `docs/execution/plans/2026-08-26-p8-conversion-gui/implementation-plan.md:93` | updated |
| census-p8cg-25-new.txt | `docs/execution/plans/2026-08-26-p8-conversion-gui/implementation-plan.md:123` | updated |
| census-p8cg-25-new.txt | `docs/execution/plans/2026-08-26-p8-conversion-gui/implementation-plan.md:182` | updated |
| census-p8cg-25-new.txt | `docs/execution/plans/2026-08-26-p8-conversion-gui/implementation-plan.md:234` | updated |
| census-p8cg-25-new.txt | `docs/execution/plans/2026-08-26-p8-conversion-gui/implementation-plan.md:270` | updated |

row_count=114

---

## Round 2 Recheck — 2026-08-26

**Workflow:** `/plan-critical-review` Round 2  
**Agent:** `gpt-5.6-sol`  
**Review mode:** `plan`

### Intent Anchor

Executing this plan is supposed to deliver MEU-33: a lazy, shell-reachable Convert page with the Downloader-shaped queue, Settings Convert card, safe AppShell command delivery, and Wave 8 Electron E2E proof, while preserving the Session 15 scope lock. The corrected plan now carries the route, navigation-safety, G23, HelpCard, closeout, and source-traceability contracts, but it would still allow materially noninteractive Wave 8 controls to pass its mandatory E2 gate.

### Prior Pass Summary

| Finding | Prior Status | Round 2 Result |
|---------|--------------|----------------|
| F1 — lazy `/convert` | open | ✅ Fixed — `LAZY_CONVERT_ROUTE` requires `lazyRouteComponent`; `router.tsx` may not statically import `ConvertPage`; Downloader stays eager (`implementation-plan.md:105`, AC-33.1 at `:219`). |
| F2 — Wave 8 control totality | open | ❌ Still open — all IDs are registered/bound somewhere, but many interactive controls need only a visual assertion, so inert controls still pass E2 (R2-F1). |
| F3 — G11 RULE-3 rail oracle | open | ✅ Fixed — AC-33.2 names `NavRail` click → `onNavigate(CONVERT_HOME)` → `navigateShell` only and W8-2 binds the click plus zero POST (`implementation-plan.md:220`; `assert-e2e-control-census.ps1:121-124`). |
| F4 — G23 C2 SKIP | open | ✅ Fixed — converter persistence is `G23_CONVERT` L1+L2, explicit Save only, with L3 correctly N/A (`implementation-plan.md:123-124`, `:161`, `:234-235`). |
| F5 — H2-4 false-pass | open | ✅ Fixed — H2-4 runs handoff markers, AC coverage, reflection/metrics, independent review, and `render --check`, with the structural receipt at `CLOSEOUT_H24_RECEIPT` (`task.md:64`). |
| F6 — HelpCard/G26 basis | open | ✅ Fixed — `HELP_G26_AVKIT` uses the shipped MEU-23 HelpCard ARIA/collapse contract plus Spec 208-210 topics; TaxHelpCard-only behavior is source-backed out of scope (`implementation-plan.md:125`, `:236`, `:317`). |
| F7 — G33-G35 test contract | open | ✅ Fixed — AC-33.23 now covers G30-G35 plus G36 without changing `RED_COUNT_33=24` (`implementation-plan.md:241`; `named-sets.json:11-12`). |
| F8 — named-set consumption | open | ✅ Fixed for the cited scripts — handoff markers consume `HANDOFF_BUNDLE_MARKERS`; the Wave 8 census consumes `E2E_CASES` and named groups (`assert-handoff-markers.ps1:8-30`; `assert-e2e-control-census.ps1:64-70`, `:118-158`). |
| F9 — unstarted status | open | ✅ Fixed — plan and task frontmatter are `draft`, every task row remains `[ ]`, and the MEU-33 implementation handoff is absent (`implementation-plan.md:6`; `task.md:5`). |

### Findings

| # | Severity | Confidence | Finding | File:Line | Recommendation | Status |
|---|----------|------------|---------|-----------|----------------|--------|
| R2-F1 | High | High | **Round 1 F2 remains materially open: Wave 8 totality treats visibility as a substitute for interactivity.** `WAVE8_W8_3_VISIBLE` includes interactive presets, fields, Save, and row actions, while the census accepts any one of visual, enabled, click, fill, or focus as total coverage. Several controls therefore have no interaction binding: for example all five `convert-preset-*` chips, `convert-cut-in/out`, `convert-extract-first/all`, `convert-gpu-refresh`, output/skip fields, Settings leaves/Browse, and all confirm/cancel buttons are only required to be visible. A `convert-preset-balanced` button whose click does nothing, a cut field that cannot be filled, or a confirmation button with no handler can satisfy the script and the planned Wave 8 gate. E2 explicitly requires each changed interactive element's presence, interactivity, and visual behavior; this is a demonstrated false-pass and violates E2, PR-4, and PR-8. | `docs/execution/plans/2026-08-26-p8-conversion-gui/named-sets.json:185`; `docs/execution/plans/2026-08-26-p8-conversion-gui/named-sets.json:219`; `docs/execution/plans/2026-08-26-p8-conversion-gui/named-sets.json:222`; `docs/execution/plans/2026-08-26-p8-conversion-gui/named-sets.json:238`; `docs/execution/plans/2026-08-26-p8-conversion-gui/assert-e2e-control-census.ps1:101`; `docs/execution/plans/2026-08-26-p8-conversion-gui/assert-e2e-control-census.ps1:127`; `docs/execution/plans/2026-08-26-p8-conversion-gui/assert-e2e-control-census.ps1:152`; `.agent/docs/emerging-standards.md:1167` | Add named per-case interaction groups for every interactive Wave 8 ID and make the census require the appropriate click/fill/change or enabled/focus assertion plus an observable outcome. Keep the visual groups, but do not let a visual assertion alone satisfy interactive-control totality. | open |

### Scope and Commands

**Targets re-read:** `implementation-plan.md`, `task.md`, `named-sets.json`, and all four named assertion scripts in `docs/execution/plans/2026-08-26-p8-conversion-gui/`.

**Authority re-read:** Phase 8 Convert Page and GUI notes; Phase 6 lazy-route, Wave 8, and GUI shipping gate; all `convert:*` action-index rows; Session 15 grouping; Downloader E2E/H2-4 local canon; Settings HelpCard AC-23.15 local canon; Session 14 RULE-1/2/3; G11, G20, G23, G26, G30-G35, and E2.

Only redirected static reads, `Test-Path`, `ConvertFrom-Json` over the plan's JSON, and `rg` sweeps were used. No pytest, Vitest, Playwright, npm test/build, OpenAPI export, or `tools/*.py` execution ran.

Key Round 2 receipts:

- `C:/Temp/av-kit/review-r2-pr6-verify.txt`
- `C:/Temp/av-kit/review-r2-plan-1-200.txt`, `review-r2-plan-201-eof.txt`, `review-r2-task.txt`
- `C:/Temp/av-kit/review-r2-named-sets.txt`, `review-r2-e2e-census-script.txt`
- `C:/Temp/av-kit/review-r2-auth08.txt`, `review-r2-auth06.txt`, `review-r2-emerging-standards.txt`
- `C:/Temp/av-kit/review-r2-e2-interaction-gap.txt`, `review-r2-artifact-existence.txt`, `review-r2-call-chain.txt`

### Checklist Results

#### Information Retrieval (IR)

| Check | Result | Evidence |
|-------|--------|----------|
| All AC have allowed source labels | pass | AC-33.1 through AC-33.24 each cite Spec, Local Canon, Research-backed authority, or a named emerging standard. |
| Validation cells are exact commands | pass | Task rows contain concrete redirected commands and preserve `$LASTEXITCODE`; every invoked existing tool/script/template was found or is explicitly scheduled. R2-F1 concerns a demonstrated false-pass, not command syntax. |
| BUILD_PLAN audit row present | pass | `implementation-plan.md:324-330` and task rows 5/H1-3/H2-2 preserve Phase 8 plan links, bind MEU-33, and defer grouping completion until post-review H2. |
| Post-MEU rows present | pass | H1 handoff/review and H2 reflection/metrics/closeout rows remain in dependency order (`task.md:50-65`). |
| Referenced artifacts exist or are scheduled | pass | Existing validation tools/templates are present. Convert source, Wave 8 spec, handoff, reflection, and execution-review files are explicitly scheduled. The intentionally absent generic closeout validator is not invoked. |

#### Design / Documentation Review (DR)

| Check | Result | Evidence |
|-------|--------|----------|
| Naming and template/frontmatter | pass | Plan/task use the correct slug, MEU-33, template versions, and `draft` state. |
| Claim-to-authority match | pass | Lazy route, single rail item, Downloader-shaped flow, Settings converter, HelpCard, and scope deferrals match the cited Phase 6/8 and local authorities. |
| Correction claim-to-state match | partial | F1 and F3-F9 match current disk state; F2's claim of complete interactive totality does not (R2-F1). |
| Verification robustness | fail | Wave 8 can pass with inert interactive controls (R2-F1). H2-4's corrected closeout chain passes this review. |
| Evidence freshness | pass | PR-6 raw receipts and both disposition copies reconcile. The prose says 12 zero-hit queries, but the index and tables consistently prove 11; this is clerical only. |
| Completion vs residual risk | pass | Plan remains `draft`; no implementation-complete claim or correlated work handoff exists. |

#### Plan Review (PR)

| Check | Result | Evidence |
|-------|--------|----------|
| PR-1 Plan/task alignment | pass | Both describe MEU-33 Red → Green → Wave 8 → handoff → SSOT → independent review → H2. |
| PR-2 Not-started confirmation | pass | All task rows are `[ ]`; Session 15 is not started and no MEU-33 handoff exists. |
| PR-3 Task contract completeness | pass | Every executable row provides task, owner, deliverable, exact validation, dependency, context strategy, durable output, and status. |
| PR-4 Validation realism | fail | The Wave 8 census false-passes materially missing interactivity (R2-F1). |
| PR-5 Source-backed planning | pass | Corrected route/G23/Help contracts and all ACs carry allowed sources. |
| PR-6 Corrections census | pass | 36 query receipts exist; 103 raw hits + 11 zero-hit receipts produce 114 rows in each disposition copy; all ledger payloads exactly match the per-query receipts. |
| PR-7 C2 scope discipline | pass | MEU-27 exists and is `ready_for_review`; Phase 8 named deferrals, REST/MCP preservation, G23 L3 N/A, HelpCard local canon, and other exclusions have concrete bases. No C2 SKIP remains. |
| PR-8 Control reachability/totality | fail | G11/RULE-3 reachability is fixed, but E2 control totality is not exhaustive on interactivity (R2-F1). |
| PR-9 Single-statement discipline | partial | Cited marker/case groups now have named owners. Non-blocking restatements remain: `G23_CONVERT` repeats `G23_SAVE_CLASS`, and H2-2/H2-4 repeat `REFLECTION_MARKERS`; their spellings agree, so this is clerical. |
| Wave 8 E2 written and wired | fail | File/task wiring is explicit, but the mandatory per-interactive-element E2 contract can still false-pass (R2-F1). |
| G11 Session 14 RULE-3 | pass | AC-33.2 and W8-2 bind NavRail click to navigation-only and assert zero same-tick conversion POSTs. Off-route palette delivery remains delayed and AppShell-owned. |
| H2-4 closeout | pass | Handoff markers + AC set + reflection/metrics + independent execution review + drift check are all in the final row. |
| REST/MCP and scope lock | pass | No Downloader→Convert, MEU-27 execution, API rewrite, or MCP rewrite is required; `ROUTE_COUNT_AFTER=61` and `ACTION_INDEX_AFTER=59` remain named. |

### Non-Blocking Correction Notes

- Blast-radius prose at the prior section says 12 zero-hit queries; the index and 114-row arithmetic prove 11. Correct the prose count only.
- PR-9 would be cleaner if `G23_CONVERT` referenced `G23_SAVE_CLASS`/`G23_SAVE_LABEL_DIRTY` without repeating their literals, and H2 checks consumed `REFLECTION_MARKERS`. Current spellings agree, so neither note blocks.

### Open Questions / Assumptions

- No human product decision is required. The remaining issue is enforcement of the already-stated E2 contract.
- The interaction-gap receipt names representative controls from the plan's own §4A/input/button inventory; the blocking demonstration does not depend on requiring a particular Playwright syntax.

### Verdict

`changes_required` — one evidence-backed High finding remains. The plan's Wave 8 gate can approve a GUI whose named presets, inputs, Settings controls, or confirmation buttons render but do not work. Route only R2-F1 through `/plan-corrections`; do not begin execution on this Round 2 verdict.

### Residual Risk

After R2-F1 is corrected, Round 3 should re-run PR-6 first, then verify that every Wave 8 interactive ID has both the appropriate interaction/state binding and an observable outcome. The remaining route, G11 RULE-3, G23, HelpCard, closeout, C2, and REST/MCP scope surfaces are currently ready and should not be escalated through nearby predicate mutations.

## Corrections Applied — 2026-08-26 after Round 2 (R2-F1)

**Corrector:** coordinator (not the reviewer). Verdict set to `corrections_applied` only. Independent Round 3 must re-score. Product code, tests, and `docs/build-plan/` were not modified. This is plan-review round cap 3.

**Clerical (Round 2 non-blocking):** prior census prose said 12 zero-hit queries; the index/table arithmetic is 11. No plan-file change required for that count.

### Finding dispositions (corrector claims; not an `approved` verdict)

| # | Change | Files |
|---|--------|-------|
| R2-F1 | Visibility no longer satisfies interactive Wave 8 IDs. Named `WAVE8_VISUAL_ONLY` (page/queue/summary/processor/gpu-chip/settings section). Every other WAVE8 testid must match `WAVE8_INTERACT_BIND` (click/fill/enabled/focus/checked/value). Added `WAVE8_W8_3_PRESET_CLICK`, `WAVE8_W8_3_FILL`, `WAVE8_W8_3_TOGGLE_CLICK`, `WAVE8_W8_3_ADVANCED_CLICK`, `WAVE8_W8_3_SETTINGS_INTERACT`. W8-4 confirms require **click**. W8-6 dropzone requires `toBeFocused`. Task clicks include Compress. Visual groups remain. | named-sets.json; assert-e2e-control-census.ps1; AC-33.21; task.md row 3 |
| PR-9 note | `G23_CONVERT` now cites `G23_SAVE_CLASS` / `G23_SAVE_LABEL_DIRTY` instead of repeating their literals. | named-sets.json |

### Blast-radius census (Step 5c / PR-6)

Index: `C:/Temp/av-kit/census-p8cg-r3-index.txt`. Runner: `C:/Temp/av-kit/census-p8cg-r3-runner.txt`. Unfiltered concat: `C:/Temp/av-kit/census-p8cg-r3-ledger.txt`. Per-query receipts: `C:/Temp/av-kit/census-p8cg-r3-01-old.txt` … `census-p8cg-r3-14-new.txt`. Duplicate disposition copy: `C:/Temp/av-kit/census-p8cg-r3-per-hit.md`.

Queries: 20. `rg -F -n` over implementation-plan.md, task.md, named-sets.json, both Wave 8/handoff assert scripts. Zero-hit old: 6. Remaining hits dispositioned below. Sweep files were not truncated.

Blast-radius census: 20 queries, 6 updated-gone, remaining sites updated or confirmed-consistent as tabled.


| Receipt | File:Line | Disposition |
|---|---|---|
| census-p8cg-r3-01-old.txt | (no hit) | updated-gone |
| census-p8cg-r3-01-new.txt | `docs/execution/plans/2026-08-26-p8-conversion-gui/assert-e2e-control-census.ps1:171` | updated |
| census-p8cg-r3-02-old.txt | (no hit) | updated-gone |
| census-p8cg-r3-02-new.txt | `docs/execution/plans/2026-08-26-p8-conversion-gui/assert-e2e-control-census.ps1:162` | updated |
| census-p8cg-r3-02-new.txt | `docs/execution/plans/2026-08-26-p8-conversion-gui/task.md:46` | updated |
| census-p8cg-r3-02-new.txt | `docs/execution/plans/2026-08-26-p8-conversion-gui/named-sets.json:235` | confirmed-consistent (named-set owner) |
| census-p8cg-r3-02-new.txt | `docs/execution/plans/2026-08-26-p8-conversion-gui/implementation-plan.md:91` | updated |
| census-p8cg-r3-02-new.txt | `docs/execution/plans/2026-08-26-p8-conversion-gui/implementation-plan.md:239` | updated |
| census-p8cg-r3-03-new.txt | `docs/execution/plans/2026-08-26-p8-conversion-gui/assert-e2e-control-census.ps1:103` | updated |
| census-p8cg-r3-03-new.txt | `docs/execution/plans/2026-08-26-p8-conversion-gui/assert-e2e-control-census.ps1:105` | updated |
| census-p8cg-r3-03-new.txt | `docs/execution/plans/2026-08-26-p8-conversion-gui/named-sets.json:262` | confirmed-consistent (named-set owner) |
| census-p8cg-r3-03-new.txt | `docs/execution/plans/2026-08-26-p8-conversion-gui/task.md:46` | updated |
| census-p8cg-r3-03-new.txt | `docs/execution/plans/2026-08-26-p8-conversion-gui/implementation-plan.md:91` | updated |
| census-p8cg-r3-03-new.txt | `docs/execution/plans/2026-08-26-p8-conversion-gui/implementation-plan.md:239` | updated |
| census-p8cg-r3-04-new.txt | `docs/execution/plans/2026-08-26-p8-conversion-gui/assert-e2e-control-census.ps1:133` | updated |
| census-p8cg-r3-04-new.txt | `docs/execution/plans/2026-08-26-p8-conversion-gui/named-sets.json:244` | confirmed-consistent (named-set owner) |
| census-p8cg-r3-04-new.txt | `docs/execution/plans/2026-08-26-p8-conversion-gui/task.md:46` | updated |
| census-p8cg-r3-04-new.txt | `docs/execution/plans/2026-08-26-p8-conversion-gui/implementation-plan.md:239` | updated |
| census-p8cg-r3-05-new.txt | `docs/execution/plans/2026-08-26-p8-conversion-gui/assert-e2e-control-census.ps1:134` | updated |
| census-p8cg-r3-05-new.txt | `docs/execution/plans/2026-08-26-p8-conversion-gui/task.md:46` | updated |
| census-p8cg-r3-05-new.txt | `docs/execution/plans/2026-08-26-p8-conversion-gui/named-sets.json:251` | confirmed-consistent (named-set owner) |
| census-p8cg-r3-05-new.txt | `docs/execution/plans/2026-08-26-p8-conversion-gui/implementation-plan.md:239` | updated |
| census-p8cg-r3-06-new.txt | `docs/execution/plans/2026-08-26-p8-conversion-gui/assert-e2e-control-census.ps1:135` | updated |
| census-p8cg-r3-06-new.txt | `docs/execution/plans/2026-08-26-p8-conversion-gui/implementation-plan.md:239` | updated |
| census-p8cg-r3-06-new.txt | `docs/execution/plans/2026-08-26-p8-conversion-gui/named-sets.json:252` | confirmed-consistent (named-set owner) |
| census-p8cg-r3-06-new.txt | `docs/execution/plans/2026-08-26-p8-conversion-gui/task.md:46` | updated |
| census-p8cg-r3-07-new.txt | `docs/execution/plans/2026-08-26-p8-conversion-gui/assert-e2e-control-census.ps1:139` | updated |
| census-p8cg-r3-07-new.txt | `docs/execution/plans/2026-08-26-p8-conversion-gui/named-sets.json:253` | confirmed-consistent (named-set owner) |
| census-p8cg-r3-07-new.txt | `docs/execution/plans/2026-08-26-p8-conversion-gui/implementation-plan.md:239` | updated |
| census-p8cg-r3-07-new.txt | `docs/execution/plans/2026-08-26-p8-conversion-gui/task.md:46` | updated |
| census-p8cg-r3-08-new.txt | `docs/execution/plans/2026-08-26-p8-conversion-gui/assert-e2e-control-census.ps1:143` | updated |
| census-p8cg-r3-08-new.txt | `docs/execution/plans/2026-08-26-p8-conversion-gui/named-sets.json:254` | confirmed-consistent (named-set owner) |
| census-p8cg-r3-08-new.txt | `docs/execution/plans/2026-08-26-p8-conversion-gui/implementation-plan.md:239` | updated |
| census-p8cg-r3-08-new.txt | `docs/execution/plans/2026-08-26-p8-conversion-gui/task.md:46` | updated |
| census-p8cg-r3-09-old.txt | (no hit) | updated-gone |
| census-p8cg-r3-09-new.txt | `docs/execution/plans/2026-08-26-p8-conversion-gui/assert-e2e-control-census.ps1:150` | updated |
| census-p8cg-r3-10-old.txt | (no hit) | updated-gone |
| census-p8cg-r3-10-new.txt | `docs/execution/plans/2026-08-26-p8-conversion-gui/assert-e2e-control-census.ps1:157` | updated |
| census-p8cg-r3-11-old.txt | (no hit) | updated-gone |
| census-p8cg-r3-11-new.txt | `docs/execution/plans/2026-08-26-p8-conversion-gui/named-sets.json:180` | confirmed-consistent (named-set owner) |
| census-p8cg-r3-12-new.txt | `docs/execution/plans/2026-08-26-p8-conversion-gui/named-sets.json:129` | confirmed-consistent (testid already named; TASK_CLICKS now includes compress) |
| census-p8cg-r3-12-new.txt | `docs/execution/plans/2026-08-26-p8-conversion-gui/named-sets.json:186` | confirmed-consistent (testid already named; TASK_CLICKS now includes compress) |
| census-p8cg-r3-12-new.txt | `docs/execution/plans/2026-08-26-p8-conversion-gui/named-sets.json:234` | confirmed-consistent (named-set owner) |
| census-p8cg-r3-12-new.txt | `docs/execution/plans/2026-08-26-p8-conversion-gui/implementation-plan.md:221` | confirmed-consistent (testid already named; TASK_CLICKS now includes compress) |
| census-p8cg-r3-13-old.txt | (no hit) | updated-gone |
| census-p8cg-r3-13-new.txt | `docs/execution/plans/2026-08-26-p8-conversion-gui/implementation-plan.md:239` | updated |
| census-p8cg-r3-14-new.txt | `docs/execution/plans/2026-08-26-p8-conversion-gui/assert-e2e-control-census.ps1:132` | updated |
| census-p8cg-r3-14-new.txt | `docs/execution/plans/2026-08-26-p8-conversion-gui/named-sets.json:234` | confirmed-consistent (named-set owner) |

row_count=48

## Round 3 — 2026-08-26 (cap)

**Workflow:** `/plan-critical-review` Round 3  
**Agent:** `gpt-5.6-sol`  
**Review mode:** `plan`  
**Execution performed:** none

### Intent Anchor

Executing this plan is supposed to deliver MEU-33: a lazy, shell-reachable Convert page with a Downloader-shaped queue, Settings Convert card, safe AppShell command delivery, and written-and-wired Wave 8 Electron E2E proof, without starting MEU-27, adding Downloader-to-Convert, or rewriting REST/MCP. The corrected plan now provides a non-vacuous Wave 8 interaction contract for that objective, and no new High or Critical issue remains.

### Scope

**Targets re-read from current disk state:**

- `docs/execution/plans/2026-08-26-p8-conversion-gui/implementation-plan.md`
- `docs/execution/plans/2026-08-26-p8-conversion-gui/task.md`
- `docs/execution/plans/2026-08-26-p8-conversion-gui/named-sets.json`
- `docs/execution/plans/2026-08-26-p8-conversion-gui/assert-red-oracle.ps1`
- `docs/execution/plans/2026-08-26-p8-conversion-gui/assert-handoff-markers.ps1`
- `docs/execution/plans/2026-08-26-p8-conversion-gui/assert-handoff-acs.ps1`
- `docs/execution/plans/2026-08-26-p8-conversion-gui/assert-e2e-control-census.ps1`

**Authority and control surfaces re-read:** Phase 8 Convert GUI notes and named deferrals; Phase 6 Wave 8; E2; G11; Session 14 RULE-3; Session 15 grouping; current MEU-27 record; harness override; current PR-6 correction log and all indexed Round 3 census receipts.

Static review only. No pytest, Vitest, Playwright, npm test/build, OpenAPI export, repository Python tool, or plan assertion script was executed.

### Findings

No Critical, High, Medium, or Low findings.

### Prior Pass Summary

| Finding | Prior Status | Round 3 Result |
|---------|--------------|----------------|
| R2-F1 — Wave 8 visibility could satisfy interactive controls | open | ✅ Fixed — 51 distinct Wave 8 IDs are partitioned into the exact 7-item `WAVE8_VISUAL_ONLY` set and 44 interaction-required IDs. The totality loop requires every non-visual ID to match `WAVE8_INTERACT_BIND`; the task/preset/GPU/extract/settings/confirm/fill/focus groups match the correction contract. |

### Confirmed Fixes

- `WAVE8_VISUAL_ONLY` is exactly `convert-page`, `convert-queue`, `convert-queue-row`, `convert-queue-summary`, `convert-processor`, `convert-gpu-chip`, and `convert-settings` (`named-sets.json:235-242`).
- Every other `WAVE8_TESTIDS` + `WAVE8_EXTRA_TESTIDS` entry is covered by the all-case interaction totality branch using `WAVE8_INTERACT_BIND` (`assert-e2e-control-census.ps1:161-174`).
- Task clicks include Compress/Cut/Extract/Advanced; preset, GPU refresh, extract/skip, and Settings interaction groups are explicit; cut in/out and output directory require `fill`; W8-4 destructive controls and all confirm/cancel controls require `click`; W8-6 requires `convert-dropzone` to be focused (`named-sets.json:234-270`; `assert-e2e-control-census.ps1:130-159`).
- W8-2 still binds `nav-convert` click to the Convert page and a zero-conversion-POST oracle, preserving G11 and Session 14 RULE-3 (`assert-e2e-control-census.ps1:125-128`; `implementation-plan.md:220`).

### Checklist Results

#### Information Retrieval (IR)

| Check | Result | Evidence |
|-------|--------|----------|
| All AC have allowed source labels | pass | AC-33.1 through AC-33.24 retain Spec, Local Canon, Research-backed, or named emerging-standard sources. |
| Validation cells are exact commands | pass | Task rows retain redirected, exit-preserving commands; referenced existing scripts/tools/templates were found, while planned deliverables are explicitly scheduled. |
| BUILD_PLAN audit row present | pass | `implementation-plan.md:324-330` and task rows 5/H1-3/H2-2 preserve the MEU-33 bind, prior Phase 8 links, hub Next, and post-review grouping update. |
| Post-MEU rows present | pass | H1 handoff/review and H2 reflection/metrics/closeout remain ordered after implementation rows (`task.md:50-65`). |
| Referenced artifacts exist or are scheduled | pass | All current plan scripts, authority docs, templates, schema, dispatch/check tools, and OpenAPI snapshot exist. Convert production/E2E/handoff/reflection/review outputs are absent because work is unstarted and are listed in the files/tasks inventory. `tools/validate_closeout_artifacts.py` remains intentionally absent and uninvoked. |

#### Design / Documentation Review (DR)

| Check | Result | Evidence |
|-------|--------|----------|
| Naming, template, and YAML frontmatter | pass | Plan/task retain the p8-conversion-gui slug, MEU-33, `draft` status, and required template versions. |
| Correction claim-to-state match | pass | The current named sets, task row 3, AC-33.21, and E2E census script implement the stated Round 2 correction. |
| Residual old terms | pass | Six indexed old queries are zero-hit receipts with `updated-gone` dispositions. |
| Downstream references updated | pass | The corrected Wave 8 names appear consistently in the plan, task, named owner, and executable census. |
| Verification robustness | pass | Interactive IDs cannot satisfy totality through visibility alone; each must bind an enabled/disabled/click/fill/focus/checked/value method on the same locator expression. |
| Evidence auditability and freshness | pass | PR-6 reconciles 20 receipts, 42 raw hits, 6 zero-hit receipts, and 48 dispositions with zero errors. |
| Completion vs residual risk | pass | Plan remains `draft`, all task rows are unchecked, and no MEU-33 implementation handoff, reflection, E2E file, or implementation review exists. |

#### Plan Review (PR)

| Check | Result | Evidence |
|-------|--------|----------|
| PR-1 Plan/task alignment | pass | Both retain MEU-33 Red → Green → Wave 8 → handoff → SSOT → independent review → H2. |
| PR-2 Not-started confirmation | pass | All task rows are `[ ]`; planned Convert production/E2E/closeout artifacts are absent. |
| PR-3 Task contract completeness | pass | Every executable row includes owner, deliverable, exact validation, dependency, context strategy, durable output, and status. |
| PR-4 Validation realism | pass | The corrected Wave 8 gate rejects the materially inert-control implementation described by R2-F1. |
| PR-5 Source-backed planning | pass | Wave 8, route, Settings, palette, Help, and scope locks retain allowed sources. |
| PR-6 Corrections census | pass | Index, ledger, runner, all 20 per-query receipts, and both disposition copies exist and reconcile: 42 hit rows + 6 zero-hit rows = 48 allowed dispositions; no truncation or missing ledger header. |
| PR-7 C2 scope discipline | pass | MEU-27 remains scheduled and `ready_for_review`; Phase 8 named deferrals and Session 15 REST/MCP exclusions retain concrete source bases. No C2 SKIP is introduced. |
| PR-8 Control reachability and totality | pass | Wave 8 names an observable interaction for all 44 non-visual IDs, keeps visual oracles for the 7 visual-only IDs, binds W8-2 navigation to the zero-POST negative, and preserves the AppShell production chain. |
| PR-9 Single-statement discipline | partial (Low note) | G23 save literals and route/action counts are now single-owned. H2-2/H2-4 still restate `REFLECTION_MARKERS` literals, but the spellings agree and this is clerical under the Materiality Gate. |
| Wave 8 E2 written and wired | pass | The file/task wiring is explicit; presence/visual groups remain, and interaction/state totality can no longer be satisfied by visibility alone. |
| G11 Session 14 RULE-3 | pass | NavRail/Ctrl+4 remain navigation-only; W8-2 binds the rail click and zero same-tick conversion POSTs; palette commands remain AppShell-owned and delayed. |
| H2-4 closeout | pass | Handoff markers + AC set + reflection/metrics + independent execution review + drift check remain in the final closeout row. |
| REST/MCP and scope lock | pass | No Downloader→Convert, MEU-27 execution, REST rewrite, MCP rewrite, or §4A index creation is introduced; `ROUTE_COUNT_AFTER=61` and `ACTION_INDEX_AFTER=59` remain single-owned. |

### Non-Blocking Correction Note

- H2-2 and H2-4 still spell out the `REFLECTION_MARKERS` array owned by `named-sets.json`. The literals agree, so this is a clerical PR-9 stale-clause risk and does not contribute to the verdict.

### Commands and Receipts

- PR-6 reconciliation: `C:/Temp/av-kit/r3-pr6-reconcile.txt` (`entries=20`, `raw_hits=42`, `zero_hit_receipts=6`, `disposition_rows=48`, `ledger_headers=20`, `errors=0`).
- Wave 8 static audit: `C:/Temp/av-kit/r3-wave8-static-audit.txt` (`51` distinct IDs, `7` visual-only, `44` interaction-required, `8` required groups, `errors=0`).
- Full target reads: `r3-plan-001-200.txt`, `r3-plan-201-eof.txt`, `r3-task-full.txt`, `r3-named-001-180.txt`, `r3-named-181-eof.txt`, `r3-e2e-census-script-full.txt`, and `r3-other-scripts-full.txt` under `C:/Temp/av-kit/`.
- Authority/existence/C2/PR-9 receipts: `r3-authority-ranges.txt`, `r3-artifact-existence.txt`, `r3-meu27-record.txt`, `r3-pr9-g23-literals.txt`, `r3-pr9-reflection-literals.txt`, and `r3-pr9-count-literals.txt`.
- Canonical write-target guard: `C:/Temp/av-kit/r3-pre-edit-guard.txt`.

### Open Questions / Assumptions

- No human product decision is required.
- This was a static plan review. Runtime Electron behavior remains for execution evidence and the independent implementation review; that ordinary execution risk is not a defect in the corrected plan contract.

### Verdict

`approved` — R2-F1 is closed. The corrected Wave 8 census distinguishes visual-only elements from interactive controls, requires all 44 interactive IDs to bind a real interaction/state method, and preserves the named per-case click/fill/focus and zero-POST oracles. PR-6 passed before content review, prior closed findings did not regress, and no new High or Critical finding remains.

### Residual Risk

The Wave 8 file does not yet exist because implementation is unstarted. Execution must still produce the E2E file and receipts, run or evidence-gate Electron according to `E2E_SANDBOX`, and pass the independent execution review. No additional plan-correction round is required.

### Follow-Up

Round 3 is the plan-review cap and ends with approval. No `/plan-corrections` action is required. This reviewer made no product, test, or plan-file changes.

