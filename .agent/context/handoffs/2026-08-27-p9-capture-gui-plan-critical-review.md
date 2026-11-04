---
date: "2026-08-27"
review_mode: "plan"
target_plan: "docs/execution/plans/2026-08-27-p9-capture-gui/implementation-plan.md"
verdict: "approved"
findings_count: 0
round: 4
template_version: "2.1"
requested_verbosity: "standard"
agent: "gpt-5.6-sol"
dispatch_id: "p9-capture-gui-plan-r4"
---

# Critical Review: p9-capture-gui

> **Review Mode**: `plan`
> **Verdict**: `changes_required` (Round 1)

## Intent Anchor

Executing this plan is supposed to deliver Session 18 / MEU-39 only: a lazy `/capture` page with the fifth rail item, filmstrip, four annotation tools, Settings Capture card, tray, F2 global shortcut, region-overlay `BrowserWindow`, inbox watcher, interactive-request poll, and Wave 9 E2E, while leaving MEU-27, FastAPI, MCP, the 71-route count, and the 67-action count untouched. As written, the scope is correct, but four unresolved production/control-chain defects mean execution would not reliably deliver the Electron OS surface or prove its required negative behavior.

## Findings

| # | Severity | Confidence | Finding | File:Line | Recommendation | Status |
|---|----------|------------|---------|-----------|----------------|--------|
| 1 | High | High | **The mandatory Boundary Input Contract is incomplete on the highest-risk renderer/main/write path.** The overlay rectangle row calls a preload return shape its “Schema Owner,” gives extra fields `n/a`, and constrains only minimum width/height; a preload return type is not a Zod schema or validator. The main process then crops, writes a PNG, and registers it. The inventory also omits the interactive `POST /captures/requests/{id}/complete` body/path and cancel write surface even though AC-39.24 requires both. This violates `AGENTS.md`'s mandatory schema-owner/extra-field rules and PR-8: malformed/extra/non-finite overlay coordinates or an invalid completion body have no named fail-closed producer or negative oracle. | `AGENTS.md:218`; `AGENTS.md:220`; `AGENTS.md:223`; `AGENTS.md:225`; `implementation-plan.md:161`; `implementation-plan.md:167`; `implementation-plan.md:205`; `packages/api/src/avkit_api/schemas/captures.py:47`; `packages/api/src/avkit_api/routes/captures.py:185` | Add a strict named Zod validator for the overlay result (finite integer coordinates, minimum edge, display-bound normalization, extra forbid) before crop/write. Inventory complete/cancel separately, including `{id}`, body owner, constraints, error mapping, and adversarial tests that prove no write/POST occurs on invalid input. | open |
| 2 | High | High | **The separate overlay window has no complete build-artifact call chain.** The plan lists “Overlay HTML/preload” as unnamed new files, but neither appears in `PAGE_FILES`/`MAIN_FILES`, the task's durable outputs, or an exact Files Modified path. Current electron-vite config emits only one preload entry and one renderer HTML entry; the plan does not schedule that config for modification. A correct-looking new preload/HTML pair can therefore remain unbundled while `npm run build` passes, leaving the production `BrowserWindow` with no loadable overlay/preload asset. This is a demonstrated PR-4/PR-8 and Sweep-8 material gap, not a clerical path typo. | `implementation-plan.md:58`; `implementation-plan.md:200`; `implementation-plan.md:260`; `implementation-plan.md:277`; `task.md:45`; `named-sets.json:280`; `named-sets.json:290`; `ui/electron.vite.config.ts:18`; `ui/electron.vite.config.ts:22`; `ui/electron.vite.config.ts:32`; `ui/electron.vite.config.ts:53` | Choose and state one buildable architecture. Either name dedicated overlay HTML/preload files and add them as electron-vite inputs (including config in Files Modified/validation), or explicitly define an inline/data-URL design with a production-built isolated preload branch. Add an existence/load oracle against the actual emitted asset path. | open |
| 3 | High | High | **Close-to-tray and Tray Quit are independently specified but not jointly reachable.** `CLOSE_TO_TRAY_TRUE` unconditionally prevents a window close and hides it, while the tray menu's Quit action calls the quit path. Electron quit closes windows; without a named quit-intent/bypass producer, the same close handler can prevent the explicit Quit. Separate tests that assert “close hides” and “Quit calls app.quit” can both pass while the runtime process never exits. This is the PR-8 dead-end between AC-39.16 and AC-39.17. | `docs/build-plan/09-screenshot-capture.md:164`; `docs/build-plan/09-screenshot-capture.md:165`; `named-sets.json:135`; `named-sets.json:136`; `named-sets.json:137`; `implementation-plan.md:197`; `implementation-plan.md:198` | Name the quit-intent mechanism (for example, a flag set by tray/app-menu Quit or `before-quit`) and make the close handler bypass `preventDefault()` when that intent is active. Add a cross-control negative oracle proving user-close hides but explicit Quit exits even when `close_to_tray=true`. | open |
| 4 | High | High | **`WAVE9_POST_ZERO_ORACLE` can false-pass without a capture-POST counter.** `Assert-PostZero` checks only that a case block contains the unrelated text fragments `/captures`, `POST`, and any `toBe(0)`/`toEqual(0)`. A W9-2/W9-6 test containing a string such as `'/captures POST'` plus `expect(0).toBe(0)` satisfies the helper while no route handler counts POSTs and navigation/palette may still trigger one. That concrete vacuity defeats the negative oracle for AC-39.2/39.14 and violates the workflow's PR-8 materiality test. | `.agent/workflows/plan-critical-review.md:258`; `named-sets.json:200`; `implementation-plan.md:183`; `implementation-plan.md:195`; `implementation-plan.md:207`; `assert-e2e-control-census.ps1:34`; `assert-e2e-control-census.ps1:43`; `assert-e2e-control-census.ps1:130`; `assert-e2e-control-census.ps1:154` | Bind the helper to a named Playwright request counter that increments only for `POST /captures`, require the same counter expression to be asserted as zero after the triggering click, and add a helper self-test that rejects unrelated strings and constant-zero assertions. | open |
| 5 | Low | High | **The execution-review round cap is canonically named but restated as literal `6` in multiple live task/plan commands.** `EXEC_REVIEW_MAX_ROUND` owns the threshold, while H1-7, H2-4, and the stop conditions hardcode it. This is one PR-9 stale-literal cluster and is clerical; it does not block independently. | `named-sets.json:311`; `implementation-plan.md:352`; `task.md:59`; `task.md:64` | Resolve the command argument and prose from `EXEC_REVIEW_MAX_ROUND`, leaving the integer only in `named-sets.json`. | open |

## Scope

**Targets reviewed**:

- `docs/execution/plans/2026-08-27-p9-capture-gui/implementation-plan.md`
- `docs/execution/plans/2026-08-27-p9-capture-gui/task.md`
- `docs/execution/plans/2026-08-27-p9-capture-gui/named-sets.json`
- all five named assertion scripts in the review prompt

**Authority and live state reviewed**: Phase 9 Capture Page, Electron OS surface, GUI implementation notes, named deferrals, MEU-39 and settings/annotation contracts; Phase 6 Wave 9; `gui-actions-index.md`; Session 18 grouping; MEU status/registry; G11/G20/G23/G26/G27/G30–G36; the approved p8 conversion-GUI analog; current Electron entrypoints/preload/main layout; and the live capture REST schemas/routes used by the GUI.

**Out of scope**: product execution, product tests, type checks, lint, Playwright, OpenAPI export, modifying product/test/spec/plan files, MEU-27, API/MCP changes, commit, merge, release, or deploy.

## Commands Executed

Static evidence only. Every successful shell read/census wrote all process streams to a receipt under `C:/Temp/av-kit/` and captured exit status before receipt consumption.

- Line-numbered `rg -n "^"` reads for the plan, task, named sets, assertion scripts, and primary authority.
- Targeted `rg -n` censuses for G-rules, MEU/grouping state, live capture schemas/routes, Electron build inputs, action/count locks, and repeated literals.
- `Test-Path` censuses for all prompt-named targets, invoked tools/templates/configs, planned product outputs, handoffs, review artifacts, and reflection outputs.
- Sweep 8 exact path extraction for `tools/`/`scripts/` references and Sweep 9 fixed-string census for routes, endpoints, timing names, counts, and review caps.
- Full reads of the review workflow/template, reviewer/orchestrator/tester roles, harness override, project profile, current focus, known issues, guardrails, architecture, testing strategy, and the most recent peer plan-review exemplar.

No pytest, vitest, npm test, Playwright, product test suite, type check, lint, build, OpenAPI export, or plan-local assertion script was run. Several malformed PowerShell/ripgrep read wrappers returned only parse/path errors; each affected static read was rerun successfully, and no repository state changed.

## Checklist Results

### Plan Review (PR-1 through PR-9)

| Check | Result | Evidence |
|-------|--------|----------|
| PR-1 Plan/task alignment | pass | Both files lock Session 18 / MEU-39, order Red → Green → Wave 9 → gate/handoff → hub → independent review → H2, and exclude MEU-27/API/MCP work. |
| PR-2 Not-started confirmation | pass | MEU-39 is `pending`, every task row is unchecked, and all planned Capture source/E2E/handoff/review/reflection outputs are absent. `task.md`'s `in_progress` frontmatter denotes planning state; no implementation evidence exists. |
| PR-3 Task contract completeness | pass | Every actionable row has task, owner, deliverable, exact validation, dependency, context strategy, durable output, builder model, and status. |
| PR-4 Validation realism | fail | Findings 2 and 4 show an unproduced runtime asset chain and a concrete false-passing negative-oracle gate. |
| PR-5 Source-backed planning | pass | Product behavior is tied to Phase 9, GUI canon, approved prior MEUs, or identified primary research; no additional unsourced product choice was found. |
| PR-6 Handoff/corrections readiness | pass | One MEU handoff and rolling plan/implementation review paths are explicit. Round-2 blast-radius evidence is not applicable in Round 1. |
| PR-7 Scope discipline (C2) | pass | MEU-27 exists and is separately scheduled; all `out-of-scope` rows cite Phase 9 named deferrals, approved prior MEUs, grouping, or a named local canon. No API/MCP rewrite is packed. |
| PR-8 Control reachability/totality | fail | Findings 1–4 identify missing validators/producers, an overlay build dead end, an unreachable Quit interaction, and a demonstrated vacuous negative oracle. |
| PR-9 Single-statement discipline | fail (non-blocking) | Finding 5 records the execution-review-cap restatement cluster. Other material sets and thresholds are owned by `named-sets.json`. |

### Docs Review (DR-1 through DR-8)

| Check | Result | Evidence |
|-------|--------|----------|
| DR-1 Claim-to-state match | pass | Static state confirms MEU-39 is unstarted, MEU-37/38 are approved, and the planned Capture files do not yet exist. |
| DR-2 Residual old terms | pass | No live plan target restores a four-item rail, Convert as fifth, API-owned F2, Python keyboard hook, SSE, or in-overlay annotation tools. |
| DR-3 Downstream references | fail | Finding 2 shows the overlay assets have no exact build-config/output reference. |
| DR-4 Verification robustness | fail | Findings 1, 3, and 4 identify invalid-input, lifecycle, and negative-oracle regressions the planned gates can false-pass. |
| DR-5 Evidence auditability | pass | All prompt-named assertion scripts and relied-on tools/templates exist; absent product artifacts are scheduled outputs. `tools/validate_closeout_artifacts.py` is absent exactly as documented and is not invoked. |
| DR-6 Cross-reference integrity | fail | The plan's dedicated overlay artifact claim does not reconcile with the current single-entry electron-vite build or the named Files Modified inventory. |
| DR-7 Evidence freshness | pass | Counts, MEU/grouping state, source schemas/routes, Electron config, and all review targets were read from current disk state. |
| DR-8 Completion vs residual risk | pass | The plan remains draft/unstarted and makes no implementation-complete claim. |

## Sweep Results

| Sweep | Result |
|-------|--------|
| 1 Plan-task consistency | pass |
| 2 Status readiness | pass — unstarted |
| 3 Role/ownership consistency | pass |
| 4 Validation specificity | fail — Findings 2 and 4 |
| 5 Dependency/order correctness | fail — overlay build producer/config is missing (Finding 2) |
| 6 Source traceability | pass |
| 7 Scope discipline | pass |
| 8 Referenced-artifact existence | fail materially — existing invoked tools/templates exist, but the required overlay HTML/preload have neither exact planned paths nor a build producer (Finding 2) |
| 9 Repeated literals | fail, Low only — Finding 5 |

## Open Questions / Assumptions

- No human product decision is required. The overlay packaging choice is an implementation-architecture gap that can be resolved from the current electron-vite structure and Electron canon during `/plan-corrections`.
- Static evidence is authoritative for this round. Runtime correctness was intentionally not tested.

## Verdict

`changes_required` — Findings 1–4 are evidence-backed High-severity delivery/control defects under the Boundary Input Contract and PR-8. The plan omits strict validation on a renderer-to-write boundary, has no complete build producer for the dedicated overlay assets, leaves explicit Quit vulnerable to the close-to-tray handler, and contains a demonstrated false-passing POST-zero oracle. Finding 5 is clerical and non-blocking.

## Required Follow-up

Route corrections through `/plan-corrections`, update only plan-folder artifacts, and return for Round 2 with the required untruncated blast-radius census plus per-hit disposition log. Do not begin product TDD while this verdict remains `changes_required`.

## Residual Risk

This was a static plan review. A corrected plan can establish execution readiness, but the Electron overlay, tray/hotkey lifecycle, OS capture behavior, request polling, and real Wave 9 controls will still require the execution receipts and independent implementation review named by the plan.

---

## Corrections Applied — 2026-08-27 (Round 1 → Round 2)

Corrector: implementer (not a reviewer). Verdict set to `corrections_applied` only. Independent Round 2 review still required.

Blast-radius census receipt: `C:/Temp/av-kit/plan-r1-blast-radius.txt` (untruncated). Values changed: 5. Old `--max-round 6` / `max round 6` hits in the plan folder: **0** (good). New named-set owners present in plan + task + named-sets + assert script.

| # | Disposition | What changed | Census |
|---|-------------|--------------|--------|
| 1 | **updated** | Boundary inventory now names `OVERLAY_RECT_SCHEMA` (Zod `.strict()` in preload + main), `COMPLETE_BODY`, `CANCEL_BODY`. Added AC-39.29 / AC-39.30. `RED_COUNT_39` = 30. | F1 hits all cite the named schemas; no leftover “schema owner = preload return type” row |
| 2 | **updated** | Locked `OVERLAY_FILES` + `ELECTRON_VITE_CONFIG`: second preload/HTML, `PRELOAD_ENTRY_FILE_NAMES`=`[name].js`, `OVERLAY_BUILD_ORACLE` (`ui/out/preload/overlay.js` + `ui/out/renderer/overlay.html`). Green / H1-2 / row 4 validate `Test-Path` after build. | F2 hits name exact paths; unnamed “Overlay HTML/preload” row removed |
| 3 | **updated** | Named `QUIT_INTENT`. AC-39.16/39.17 jointly: close hides iff `close_to_tray` AND NOT `QUIT_INTENT`; Quit sets the flag then `app.quit`. | F3 hits use `QUIT_INTENT`; `CLOSE_TO_TRAY_TRUE` no longer unconditional preventDefault |
| 4 | **updated** | `WAVE9_REGISTER_POST` + `WAVE9_POST_COUNTER`. `Assert-PostZero` requires `page.on('request')` + `expect(capturePostCount).toBe(0)` and self-tests against `expect(0).toBe(0)` / bare `'/captures POST'`. | F4 helper + W9-2/W9-6; vacuous self-test present |
| 5 | **updated** | H1-7 / H2-4 load `--max-round` from `EXEC_REVIEW_MAX_ROUND`. Stop conditions cite `PLAN_REVIEW_MAX_ROUND` / `EXEC_REVIEW_MAX_ROUND`. | F5 old literal `6` in plan folder: 0 matches |

Finding status for Round 2 reviewer: 1–5 **resolved in plan artifacts** (not yet independently re-verified).

## Round 2 — 2026-08-27

### Intent Anchor

Executing this plan is intended to deliver the Session 18 / MEU-39 Capture GUI and its Electron OS surfaces with source-backed boundaries, reachable lifecycle controls, packaged overlay assets, and non-vacuous static/E2E control oracles. Round 2 must first establish an auditable one-to-one relationship between the corrector's blast-radius census hits and correction-log dispositions before the corrected content can be independently adjudicated.

### Scope

**Declared review targets**:

- `docs/execution/plans/2026-08-27-p9-capture-gui/implementation-plan.md`
- `docs/execution/plans/2026-08-27-p9-capture-gui/task.md`
- `docs/execution/plans/2026-08-27-p9-capture-gui/named-sets.json`
- all five `assert-*.ps1` files in that plan folder

**Round 2 scope reached**: the existing review's `Corrections Applied` section and the raw correction census at `C:/Temp/av-kit/plan-r1-blast-radius.txt`. Per PR-6's pre-verdict rule, corrected-content review of the declared targets was not performed after the procedural gate failed.

**Out of scope**: product execution; pytest, vitest, npm test, Playwright, builds, lint, type checks; and edits to product code, tests, plan files, or any file other than this rolling review handoff.

### Commands Executed

Static evidence only; all shell output was redirected to `C:/Temp/av-kit/` and exit status was captured before receipt reads.

- Read `.agent/workflows/plan-critical-review.md`, `.agent/context/handoffs/REVIEW-TEMPLATE.md`, the required role contracts, harness/project context, and this rolling review file.
- `rg -n -A 220 "^## Corrections Applied"` against this review file.
- Full read of `C:/Temp/av-kit/plan-r1-blast-radius.txt`.
- `Test-Path` plus exact-string comparison for the canonical pre-edit guard.

No pytest, vitest, npm test, Playwright, plan-local assertion script, build, lint, or type-check command was run.

### Procedural Pre-Verdict Gate

| # | Gate | Evidence | Required correction | Status |
|---|------|----------|---------------------|--------|
| P-1 | **PR-6 blast-radius dispositions are not per hit.** The named raw receipt exists and is untruncated, but the correction log assigns one `updated` disposition to each Round 1 finding group rather than assigning `updated` or `confirmed-consistent` to every raw census `file:line` hit. The workflow explicitly requires the correction log to disposition each hit; a grouped summary is not the required one-to-one audit trail. | Correction log groups: this file lines 124–132. Raw inventory: `C:/Temp/av-kit/plan-r1-blast-radius.txt`. | Add a correction-log row for every raw receipt `file:line` hit with an explicit `updated` or `confirmed-consistent` disposition. Preserve the zero-hit F5 result and the untruncated raw receipt, then dispatch the next review round. | open |

### Findings

No severity-rated Round 2 findings were adjudicated. P-1 is the workflow's Round 2 procedural exception: it requires `changes_required` before severity assignment and prohibits review of the corrected content in this round. The five Round 1 findings table remains intact above; the corrector's resolution claims are not independently re-verified by this round.

### Checklist Results

#### Plan Review (PR-1 through PR-9)

| Check | Result | Evidence |
|-------|--------|----------|
| PR-1 Plan/task alignment | not evaluated | Corrected-content review stopped at the PR-6 pre-verdict gate. Round 1 result remains recorded above. |
| PR-2 Not-started confirmation | not evaluated | Corrected-content review stopped at the PR-6 pre-verdict gate. Round 1 result remains recorded above. |
| PR-3 Task contract completeness | not evaluated | Corrected-content review stopped at the PR-6 pre-verdict gate. Round 1 result remains recorded above. |
| PR-4 Validation realism | not evaluated | Findings 1–4 were not independently re-verified after the procedural failure. |
| PR-5 Source-backed planning | not evaluated | Corrected-content review stopped at the PR-6 pre-verdict gate. |
| PR-6 Handoff/corrections readiness | **fail — procedural** | Receipt present and untruncated; per-hit `file:line` dispositions absent from the correction log. |
| PR-7 Scope discipline (C2) | not evaluated | Corrected-content review stopped at the PR-6 pre-verdict gate. |
| PR-8 Control reachability/totality | not evaluated | Findings 1–4 were not independently re-verified after the procedural failure. |
| PR-9 Single-statement discipline | not evaluated | Finding 5 was not independently re-verified after the procedural failure. |

#### Docs Review (DR-1 through DR-8)

DR-1 through DR-8 were not re-evaluated in Round 2 because PR-6 failed before corrected-content review. The Round 1 results remain preserved above.

### Open Questions / Assumptions

- No open product question was evaluated. The only current blocker is the missing per-hit correction-log disposition trail.
- `findings_count: 1` counts the single procedural blocker P-1; it is intentionally not assigned a severity under the workflow's PR-6 exception.

### Verdict

`changes_required` — the Round 2 PR-6 pre-verdict gate failed. The receipt is present and untruncated, but the correction log does not disposition every census `file:line` hit. Per the workflow, this is the only issue adjudicated this round; Findings 1–5 remain unconfirmed rather than newly open or independently resolved.

### Residual Risk

Because corrected-content review was procedurally barred, the claimed fixes for the Boundary Input Contract, overlay build chain, `QUIT_INTENT`, `WAVE9_POST_ZERO_ORACLE`, and `EXEC_REVIEW_MAX_ROUND` have not received independent Round 2 verification. Their delivery risk remains the Round 1 risk until a compliant census disposition log permits a substantive recheck.

### Follow-Up

Route P-1 through `/plan-corrections`, updating only the correction evidence/log as needed. Do not treat this verdict as authorization to execute the plan.

---

## Corrections Applied — 2026-08-27 (Round 2 → Round 3)

Corrector: implementer (not a reviewer). Verdict `corrections_applied` only.

P-1 (PR-6): one-to-one dispositions for every raw census `file:line` in `C:/Temp/av-kit/plan-r1-blast-radius.txt`. Duplicate copy: `C:/Temp/av-kit/plan-r1-per-hit-dispositions.md`.

Counts: 47 raw hits + 1 F5 zero-hit row. Named-set definition hits = **updated**. Plan/task/assert citations of those names = **confirmed-consistent**. F5 old `--max-round 6` = 0 hits (**confirmed-consistent** absence).

| Family | File:Line | Disposition | Why |
|---------|-----------|-------------|-----|
| F1 | `docs/execution/plans/2026-08-27-p9-capture-gui/named-sets.json:23` | **updated** | Canonical named-set owner or RED_AC_IDS membership. |
| F1 | `docs/execution/plans/2026-08-27-p9-capture-gui/named-sets.json:132` | **updated** | Canonical named-set owner or RED_AC_IDS membership. |
| F1 | `docs/execution/plans/2026-08-27-p9-capture-gui/named-sets.json:142` | **updated** | Canonical named-set owner or RED_AC_IDS membership. |
| F1 | `docs/execution/plans/2026-08-27-p9-capture-gui/named-sets.json:144` | **updated** | Canonical named-set owner or RED_AC_IDS membership. |
| F1 | `docs/execution/plans/2026-08-27-p9-capture-gui/implementation-plan.md:167` | **confirmed-consistent** | Cites the named owner; no second product contract. |
| F1 | `docs/execution/plans/2026-08-27-p9-capture-gui/implementation-plan.md:168` | **confirmed-consistent** | Cites the named owner; no second product contract. |
| F1 | `docs/execution/plans/2026-08-27-p9-capture-gui/implementation-plan.md:169` | **confirmed-consistent** | Cites the named owner; no second product contract. |
| F1 | `docs/execution/plans/2026-08-27-p9-capture-gui/implementation-plan.md:203` | **confirmed-consistent** | Cites the named owner; no second product contract. |
| F1 | `docs/execution/plans/2026-08-27-p9-capture-gui/implementation-plan.md:207` | **confirmed-consistent** | Cites the named owner; no second product contract. |
| F1 | `docs/execution/plans/2026-08-27-p9-capture-gui/implementation-plan.md:212` | **confirmed-consistent** | Cites the named owner; no second product contract. |
| F1 | `docs/execution/plans/2026-08-27-p9-capture-gui/implementation-plan.md:213` | **confirmed-consistent** | Cites the named owner; no second product contract. |
| F1 | `docs/execution/plans/2026-08-27-p9-capture-gui/implementation-plan.md:267` | **confirmed-consistent** | Cites the named owner; no second product contract. |
| F2 | `docs/execution/plans/2026-08-27-p9-capture-gui/task.md:45` | **confirmed-consistent** | Cites the named owner; no second product contract. |
| F2 | `docs/execution/plans/2026-08-27-p9-capture-gui/task.md:47` | **confirmed-consistent** | Cites the named owner; no second product contract. |
| F2 | `docs/execution/plans/2026-08-27-p9-capture-gui/task.md:52` | **confirmed-consistent** | Cites the named owner; no second product contract. |
| F2 | `docs/execution/plans/2026-08-27-p9-capture-gui/named-sets.json:133` | **updated** | Canonical named-set owner or RED_AC_IDS membership. |
| F2 | `docs/execution/plans/2026-08-27-p9-capture-gui/named-sets.json:136` | **updated** | Canonical named-set owner or RED_AC_IDS membership. |
| F2 | `docs/execution/plans/2026-08-27-p9-capture-gui/named-sets.json:137` | **updated** | Canonical named-set owner or RED_AC_IDS membership. |
| F2 | `docs/execution/plans/2026-08-27-p9-capture-gui/named-sets.json:138` | **updated** | Canonical named-set owner or RED_AC_IDS membership. |
| F2 | `docs/execution/plans/2026-08-27-p9-capture-gui/named-sets.json:139` | **updated** | Canonical named-set owner or RED_AC_IDS membership. |
| F2 | `docs/execution/plans/2026-08-27-p9-capture-gui/named-sets.json:140` | **updated** | Canonical named-set owner or RED_AC_IDS membership. |
| F2 | `docs/execution/plans/2026-08-27-p9-capture-gui/named-sets.json:320` | **updated** | Canonical named-set owner or RED_AC_IDS membership. |
| F2 | `docs/execution/plans/2026-08-27-p9-capture-gui/named-sets.json:355` | **updated** | Canonical named-set owner or RED_AC_IDS membership. |
| F2 | `docs/execution/plans/2026-08-27-p9-capture-gui/implementation-plan.md:58` | **confirmed-consistent** | Cites the named owner; no second product contract. |
| F2 | `docs/execution/plans/2026-08-27-p9-capture-gui/implementation-plan.md:203` | **confirmed-consistent** | Cites the named owner; no second product contract. |
| F2 | `docs/execution/plans/2026-08-27-p9-capture-gui/implementation-plan.md:211` | **confirmed-consistent** | Cites the named owner; no second product contract. |
| F2 | `docs/execution/plans/2026-08-27-p9-capture-gui/implementation-plan.md:232` | **confirmed-consistent** | Cites the named owner; no second product contract. |
| F2 | `docs/execution/plans/2026-08-27-p9-capture-gui/implementation-plan.md:265` | **confirmed-consistent** | Cites the named owner; no second product contract. |
| F2 | `docs/execution/plans/2026-08-27-p9-capture-gui/implementation-plan.md:268` | **confirmed-consistent** | Cites the named owner; no second product contract. |
| F2 | `docs/execution/plans/2026-08-27-p9-capture-gui/implementation-plan.md:339` | **confirmed-consistent** | Cites the named owner; no second product contract. |
| F3 | `docs/execution/plans/2026-08-27-p9-capture-gui/task.md:45` | **confirmed-consistent** | Cites the named owner; no second product contract. |
| F3 | `docs/execution/plans/2026-08-27-p9-capture-gui/named-sets.json:146` | **updated** | Canonical named-set owner or RED_AC_IDS membership. |
| F3 | `docs/execution/plans/2026-08-27-p9-capture-gui/named-sets.json:152` | **updated** | Canonical named-set owner or RED_AC_IDS membership. |
| F3 | `docs/execution/plans/2026-08-27-p9-capture-gui/implementation-plan.md:199` | **confirmed-consistent** | Cites the named owner; no second product contract. |
| F3 | `docs/execution/plans/2026-08-27-p9-capture-gui/implementation-plan.md:200` | **confirmed-consistent** | Cites the named owner; no second product contract. |
| F3 | `docs/execution/plans/2026-08-27-p9-capture-gui/implementation-plan.md:264` | **confirmed-consistent** | Cites the named owner; no second product contract. |
| F4 | `docs/execution/plans/2026-08-27-p9-capture-gui/named-sets.json:216` | **updated** | Canonical named-set owner or RED_AC_IDS membership. |
| F4 | `docs/execution/plans/2026-08-27-p9-capture-gui/named-sets.json:217` | **updated** | Canonical named-set owner or RED_AC_IDS membership. |
| F4 | `docs/execution/plans/2026-08-27-p9-capture-gui/named-sets.json:218` | **updated** | Canonical named-set owner or RED_AC_IDS membership. |
| F4 | `docs/execution/plans/2026-08-27-p9-capture-gui/implementation-plan.md:209` | **confirmed-consistent** | Cites the named owner; no second product contract. |
| F4 | `docs/execution/plans/2026-08-27-p9-capture-gui/assert-e2e-control-census.ps1:45` | **confirmed-consistent** | Cites the named owner; no second product contract. |
| F4 | `docs/execution/plans/2026-08-27-p9-capture-gui/assert-e2e-control-census.ps1:47` | **confirmed-consistent** | Cites the named owner; no second product contract. |
| F4 | `docs/execution/plans/2026-08-27-p9-capture-gui/assert-e2e-control-census.ps1:56` | **confirmed-consistent** | Cites the named owner; no second product contract. |
| F4 | `docs/execution/plans/2026-08-27-p9-capture-gui/assert-e2e-control-census.ps1:58` | **confirmed-consistent** | Cites the named owner; no second product contract. |
| F4 | `docs/execution/plans/2026-08-27-p9-capture-gui/assert-e2e-control-census.ps1:60` | **confirmed-consistent** | Cites the named owner; no second product contract. |
| F4 | `docs/execution/plans/2026-08-27-p9-capture-gui/assert-e2e-control-census.ps1:148` | **confirmed-consistent** | Cites the named owner; no second product contract. |
| F4 | `docs/execution/plans/2026-08-27-p9-capture-gui/assert-e2e-control-census.ps1:171` | **confirmed-consistent** | Cites the named owner; no second product contract. |
| F5 | (none) | **confirmed-consistent** | Old `--max-round 6` / `max round 6` had 0 hits in the plan folder. |

---

## Round 3 — 2026-08-27

### Intent Anchor

Executing this plan is intended to deliver Session 18 / MEU-39: the Capture GUI and its Electron OS surfaces, with strict renderer/main/write boundaries, buildable overlay assets, reachable tray/quit behavior, and non-vacuous Wave 9 negative controls. The Round 3 question is whether the corrected live plan would deliver and prove that objective; one original control-gate defect remains materially unresolved.

### Findings

| # | Severity | Confidence | Finding | File:Line | Recommendation | Status |
|---|----------|------------|---------|-----------|----------------|--------|
| 1 | High | High | **Round 1 Finding 4 remains open: `WAVE9_POST_ZERO_ORACLE` still false-passes without a capture-POST counter.** `WAVE9_REGISTER_POST` requires the Playwright listener to increment `capturePostCount` only for method `POST` and pathname exactly `/api/v1/captures`, but `Test-PostZero` checks only that the block contains the counter name, `page.on('request'`, the route literal, and `expect(capturePostCount).toBe(0)`. A W9 case with `let capturePostCount = 0; page.on('request', () => {}); '/api/v1/captures'; expect(capturePostCount).toBe(0)` passes this helper while navigation/palette may issue a real POST. The new self-test rejects only the prior constant-zero example, not this no-op-listener counterexample. This is the original demonstrated PR-4/PR-8 false-pass, not a new predicate-shape refinement. | `named-sets.json:217-218`; `implementation-plan.md:209`; `assert-e2e-control-census.ps1:34-42`; `assert-e2e-control-census.ps1:45-60`; `assert-e2e-control-census.ps1:148`; `assert-e2e-control-census.ps1:171` | Make the gate prove that the listener callback increments `WAVE9_POST_COUNTER` behind both exact method and exact pathname predicates, and add a helper self-test that rejects a no-op listener plus unrelated route literal. Alternatively, generate/use one canonical executable listener helper so the cases cannot restate a weaker listener. | open |

### Scope

**Targets reviewed**:

- `docs/execution/plans/2026-08-27-p9-capture-gui/implementation-plan.md`
- `docs/execution/plans/2026-08-27-p9-capture-gui/task.md`
- `docs/execution/plans/2026-08-27-p9-capture-gui/named-sets.json`
- all five `assert-*.ps1` files in that folder
- Round 2 correction evidence: `C:/Temp/av-kit/plan-r1-blast-radius.txt`, `C:/Temp/av-kit/plan-r1-per-hit-dispositions.md`, and this file's per-hit correction table

**Out of scope**: product execution; pytest, vitest, npm, Playwright, builds, lint, type checks; and edits to product code, tests, plan files, or any file other than this rolling review handoff.

### Commands Executed

Static evidence only. Every substantive shell read/census wrote all process streams to `C:/Temp/av-kit/` and captured exit status before receipt consumption.

- Full/line-numbered reads of the review workflow/template, required role and harness contracts, rolling review, plan, task, named sets, all five assertion scripts, live capture schema/route authority, and `ui/electron.vite.config.ts`.
- PR-6 family-qualified comparison of raw census hits against both disposition copies.
- Exact state/existence census for task rows, planned outputs, invoked tools, templates, and config.
- AC/named-set cardinality and JSON parse checks; MEU-27 scope evidence; exact old `--max-round 6` census.

No plan-local assertion script, pytest, vitest, npm command, Playwright, build, lint, type check, or product test was run.

### PR-6 Procedural Gate

`pass` — the raw receipt is present and untruncated. The family-qualified comparison produced 47 raw unique keys and 47 unique disposition keys in each copy, with zero differences: F1 = 12, F2 = 18, F3 = 6, F4 = 11. F5 has a preserved heading, zero old-literal hits, and an explicit `confirmed-consistent` zero-hit row. Round 2 blocker P-1 is resolved.

### Round 1 Finding Recheck

| Round 1 finding | Recheck result | Live evidence |
|---|---|---|
| 1 — Boundary Input Contract | fixed | `implementation-plan.md:161-170,203,207,212-213` and `named-sets.json:132,141-145` name strict overlay, complete, and cancel boundaries with fail-closed negative oracles; live API models inherit `extra="forbid"`. |
| 2 — Overlay build chain | fixed | `implementation-plan.md:58,232,265-268,339`, `task.md:45,47,52`, and `named-sets.json:133-140,316-320` name both source assets, the electron-vite change, deterministic outputs, and post-build existence oracles. |
| 3 — Close-to-tray vs Quit | fixed | `implementation-plan.md:199-200,264` and `named-sets.json:146,152` bind tray/app-menu Quit and `before-quit` to `QUIT_INTENT`, with the close handler bypass and a joint negative oracle. |
| 4 — POST-zero oracle | **still open** | Finding 1 above demonstrates that `assert-e2e-control-census.ps1:34-42` never verifies the increment or either request predicate required by `named-sets.json:217`. |
| 5 — literal review cap | fixed | `EXEC_REVIEW_MAX_ROUND` owns `6` at `named-sets.json:336`; task/plan commands resolve the named value, and exact `--max-round 6` census across all declared targets returned zero hits. |

### Checklist Results

#### Plan Review (PR-1 through PR-9)

| Check | Result | Evidence |
|-------|--------|----------|
| PR-1 Plan/task alignment | pass | Both retain Session 18 / MEU-39 and the same Red → Green → Wave 9 → H1 → independent review → H2 order. |
| PR-2 Not-started confirmation | pass | 18 actionable task rows are unchecked, zero are checked, and sampled planned product/E2E/handoff/review/reflection outputs are absent. |
| PR-3 Task contract completeness | pass | All actionable rows retain owner, deliverable, exact validation, dependency, context strategy, durable output, and status columns. |
| PR-4 Validation realism | **fail** | Finding 1 demonstrates that the required Wave 9 negative gate can pass without observing capture POSTs. |
| PR-5 Source-backed planning | pass | All 30 unique AC rows remain source-labeled; strict boundary additions cite the Boundary Input Contract and existing MEU-37 schemas. |
| PR-6 Handoff/corrections readiness | pass | One-to-one 47-hit dispositions plus the F5 zero-hit disposition were independently reproduced with no differences. |
| PR-7 Scope discipline (C2) | pass | MEU-27 exists as a separately scheduled Session 8c item; named Phase 9 deferrals and approved MEU-37/38 boundaries remain evidenced. |
| PR-8 Control reachability/totality | **fail** | The POST-zero gate does not bind its observable to a producer: no required counter increment or method/path guard is checked. |
| PR-9 Single-statement discipline | pass | Round 1's review-cap literal cluster is resolved to `EXEC_REVIEW_MAX_ROUND`; no material conflicting live spelling was found. |

#### Docs Review (DR-1 through DR-8)

| Check | Result | Evidence |
|-------|--------|----------|
| DR-1 Claim-to-state match | pass | Fix claims 1–3 and 5 match live artifacts; fix claim 4 does not and is retained as the finding. |
| DR-2 Residual old terms | pass | No old literal review cap or removed overlay/quit contract was found in the declared targets. |
| DR-3 Downstream references | pass | Overlay inputs, outputs, config, task rows, and build oracles are mutually named. |
| DR-4 Verification robustness | **fail** | The no-op-listener counterexample is accepted by the static Wave 9 gate. |
| DR-5 Evidence auditability | pass | All declared targets and required existing tools/templates/config exist; PR-6 receipts reconcile exactly. |
| DR-6 Cross-reference integrity | pass | Boundary, overlay packaging, and quit-intent corrections agree across plan/task/named sets. |
| DR-7 Evidence freshness | pass | Counts, paths, current electron-vite inputs, API schema ownership, and target contents were reproduced from live disk state. |
| DR-8 Completion vs residual risk | pass | The plan remains draft/unstarted and makes no implementation-complete claim. |

### Open Questions / Assumptions

- No product decision is required. The remaining defect is a static control-gate implementation gap within the plan folder.
- Git history/diff evidence is unavailable because `P:/av-kit` has no `.git` directory in this workspace; current file state and exact receipts are the review authority.

### Verdict

`changes_required` — PR-6 passes and Round 1 findings 1–3 and 5 are independently resolved, but Round 1 finding 4 remains an evidence-backed High-severity PR-4/PR-8 false-pass. Executing the plan can produce Wave 9 cases whose mandated zero-POST gate passes without counting POST requests.

### Plan-Review Cap HARD STOP

Round 3 of 3 is complete with `changes_required`. The plan-review cap has been reached. Stop the review/correction loop and wait for direct human direction; do not autonomously run `/plan-corrections`, begin product TDD, or treat this verdict as execution authorization.

### Residual Risk

Until the static gate rejects a no-op request listener, navigation and palette actions may regress into capture creation while the plan's required zero-POST evidence still reports success. Electron overlay, tray/hotkey, watcher, and request-poll behavior also remain implementation-time risks requiring the planned runtime receipts and independent execution review.

---

## Corrections Applied — 2026-08-27 (Round 3 → Round 4)

Corrector: implementer (not a reviewer). Verdict `corrections_applied` only. Human authorized `(a) continue review loop` after the Round 3 cap.

Round 3 Finding 1 (R1 F4): `Test-PostZero` now requires the compact listener assembled from `WAVE9_POST_COUNTER`, `WAVE9_POST_METHOD`, and `WAVE9_CAPTURE_POST_PATH` (increment is inside both `req.method()` and `.pathname ===` predicates) plus `expect(WAVE9_POST_COUNTER).toBe(0)`. Self-tests reject `expect(0).toBe(0)`, the Round 3 no-op `page.on('request', () => {})` counterexample, increment-without-predicates, and `url().includes(path)`. Helper self-tests ran; script then exited 1 on missing `ui/tests/e2e/capture-inbox.test.ts` (expected; MEU-39 unstarted). Receipt: `C:/Temp/av-kit/e2e-control-census-r3-selftest.txt`.

PR-6 census: `C:/Temp/av-kit/plan-r3-blast-radius.txt` (untruncated). Duplicate: `C:/Temp/av-kit/plan-r3-per-hit-dispositions.md`. Counts: 61 raw hits + 2 zero-hit families (`WAVE9_REGISTER_POST_SNIPPET`, old `bare '/captures POST'` owner phrase).

| Family | File:Line | Disposition | Why |
|---------|-----------|-------------|-----|
| `WAVE9_POST_ZERO_ORACLE` | `docs/execution/plans/2026-08-27-p9-capture-gui/task.md:46` | **confirmed-consistent** | Cites WAVE9_POST_ZERO_ORACLE by name; no second listener contract. |
| `WAVE9_POST_ZERO_ORACLE` | `docs/execution/plans/2026-08-27-p9-capture-gui/plan-review-r2-prompt.txt:35` | **confirmed-consistent** | Historical Round 2 prompt; not a live contract. |
| `WAVE9_POST_ZERO_ORACLE` | `docs/execution/plans/2026-08-27-p9-capture-gui/named-sets.json:220` | **updated** | Canonical named-set owner rewritten for the compact listener contract. |
| `WAVE9_POST_ZERO_ORACLE` | `docs/execution/plans/2026-08-27-p9-capture-gui/implementation-plan.md:209` | **updated** | AC-39.26 now names WAVE9_POST_METHOD and WAVE9_CAPTURE_POST_PATH in the oracle assembly. |
| `WAVE9_POST_ZERO_ORACLE` | `docs/execution/plans/2026-08-27-p9-capture-gui/assert-e2e-control-census.ps1:62` | **updated** | Helper now requires assembled method+pathname increment snippet; self-tests reject no-op/includes/unconditional. |
| `WAVE9_POST_ZERO_ORACLE` | `docs/execution/plans/2026-08-27-p9-capture-gui/assert-e2e-control-census.ps1:82` | **updated** | Helper now requires assembled method+pathname increment snippet; self-tests reject no-op/includes/unconditional. |
| `WAVE9_POST_ZERO_ORACLE` | `docs/execution/plans/2026-08-27-p9-capture-gui/assert-e2e-control-census.ps1:87` | **updated** | Helper now requires assembled method+pathname increment snippet; self-tests reject no-op/includes/unconditional. |
| `WAVE9_POST_ZERO_ORACLE` | `docs/execution/plans/2026-08-27-p9-capture-gui/assert-e2e-control-census.ps1:92` | **updated** | Helper now requires assembled method+pathname increment snippet; self-tests reject no-op/includes/unconditional. |
| `WAVE9_POST_ZERO_ORACLE` | `docs/execution/plans/2026-08-27-p9-capture-gui/assert-e2e-control-census.ps1:97` | **updated** | Helper now requires assembled method+pathname increment snippet; self-tests reject no-op/includes/unconditional. |
| `WAVE9_POST_ZERO_ORACLE` | `docs/execution/plans/2026-08-27-p9-capture-gui/assert-e2e-control-census.ps1:102` | **updated** | Helper now requires assembled method+pathname increment snippet; self-tests reject no-op/includes/unconditional. |
| `WAVE9_POST_ZERO_ORACLE` | `docs/execution/plans/2026-08-27-p9-capture-gui/assert-e2e-control-census.ps1:114` | **updated** | Helper now requires assembled method+pathname increment snippet; self-tests reject no-op/includes/unconditional. |
| `WAVE9_REGISTER_POST` | `docs/execution/plans/2026-08-27-p9-capture-gui/named-sets.json:219` | **updated** | Canonical named-set owner rewritten for the compact listener contract. |
| `WAVE9_REGISTER_POST` | `docs/execution/plans/2026-08-27-p9-capture-gui/named-sets.json:220` | **updated** | Canonical named-set owner rewritten for the compact listener contract. |
| `WAVE9_REGISTER_POST` | `docs/execution/plans/2026-08-27-p9-capture-gui/implementation-plan.md:209` | **updated** | AC-39.26 now names WAVE9_POST_METHOD and WAVE9_CAPTURE_POST_PATH in the oracle assembly. |
| `WAVE9_REGISTER_POST` | `docs/execution/plans/2026-08-27-p9-capture-gui/assert-e2e-control-census.ps1:62` | **updated** | Helper now requires assembled method+pathname increment snippet; self-tests reject no-op/includes/unconditional. |
| `WAVE9_POST_COUNTER` | `docs/execution/plans/2026-08-27-p9-capture-gui/named-sets.json:216` | **updated** | Canonical named-set owner rewritten for the compact listener contract. |
| `WAVE9_POST_COUNTER` | `docs/execution/plans/2026-08-27-p9-capture-gui/named-sets.json:219` | **updated** | Canonical named-set owner rewritten for the compact listener contract. |
| `WAVE9_POST_COUNTER` | `docs/execution/plans/2026-08-27-p9-capture-gui/named-sets.json:220` | **updated** | Canonical named-set owner rewritten for the compact listener contract. |
| `WAVE9_POST_COUNTER` | `docs/execution/plans/2026-08-27-p9-capture-gui/implementation-plan.md:209` | **updated** | AC-39.26 now names WAVE9_POST_METHOD and WAVE9_CAPTURE_POST_PATH in the oracle assembly. |
| `WAVE9_POST_COUNTER` | `docs/execution/plans/2026-08-27-p9-capture-gui/assert-e2e-control-census.ps1:62` | **updated** | Helper now requires assembled method+pathname increment snippet; self-tests reject no-op/includes/unconditional. |
| `WAVE9_POST_COUNTER` | `docs/execution/plans/2026-08-27-p9-capture-gui/assert-e2e-control-census.ps1:73` | **updated** | Helper now requires assembled method+pathname increment snippet; self-tests reject no-op/includes/unconditional. |
| `WAVE9_POST_METHOD` | `docs/execution/plans/2026-08-27-p9-capture-gui/named-sets.json:217` | **updated** | Canonical named-set owner rewritten for the compact listener contract. |
| `WAVE9_POST_METHOD` | `docs/execution/plans/2026-08-27-p9-capture-gui/named-sets.json:219` | **updated** | Canonical named-set owner rewritten for the compact listener contract. |
| `WAVE9_POST_METHOD` | `docs/execution/plans/2026-08-27-p9-capture-gui/named-sets.json:220` | **updated** | Canonical named-set owner rewritten for the compact listener contract. |
| `WAVE9_POST_METHOD` | `docs/execution/plans/2026-08-27-p9-capture-gui/implementation-plan.md:209` | **updated** | AC-39.26 now names WAVE9_POST_METHOD and WAVE9_CAPTURE_POST_PATH in the oracle assembly. |
| `WAVE9_POST_METHOD` | `docs/execution/plans/2026-08-27-p9-capture-gui/assert-e2e-control-census.ps1:74` | **updated** | Helper now requires assembled method+pathname increment snippet; self-tests reject no-op/includes/unconditional. |
| `WAVE9_CAPTURE_POST_PATH` | `docs/execution/plans/2026-08-27-p9-capture-gui/named-sets.json:218` | **updated** | Canonical named-set owner rewritten for the compact listener contract. |
| `WAVE9_CAPTURE_POST_PATH` | `docs/execution/plans/2026-08-27-p9-capture-gui/named-sets.json:219` | **updated** | Canonical named-set owner rewritten for the compact listener contract. |
| `WAVE9_CAPTURE_POST_PATH` | `docs/execution/plans/2026-08-27-p9-capture-gui/named-sets.json:220` | **updated** | Canonical named-set owner rewritten for the compact listener contract. |
| `WAVE9_CAPTURE_POST_PATH` | `docs/execution/plans/2026-08-27-p9-capture-gui/implementation-plan.md:209` | **updated** | AC-39.26 now names WAVE9_POST_METHOD and WAVE9_CAPTURE_POST_PATH in the oracle assembly. |
| `WAVE9_CAPTURE_POST_PATH` | `docs/execution/plans/2026-08-27-p9-capture-gui/assert-e2e-control-census.ps1:75` | **updated** | Helper now requires assembled method+pathname increment snippet; self-tests reject no-op/includes/unconditional. |
| `/api/v1/captures` | `docs/execution/plans/2026-08-27-p9-capture-gui/named-sets.json:218` | **updated** | Canonical named-set owner rewritten for the compact listener contract. |
| `capturePostCount` | `docs/execution/plans/2026-08-27-p9-capture-gui/named-sets.json:216` | **updated** | Canonical named-set owner rewritten for the compact listener contract. |
| `page.on('request'` | `docs/execution/plans/2026-08-27-p9-capture-gui/assert-e2e-control-census.ps1:45` | **updated** | Helper now requires assembled method+pathname increment snippet; self-tests reject no-op/includes/unconditional. |
| `page.on('request'` | `docs/execution/plans/2026-08-27-p9-capture-gui/assert-e2e-control-census.ps1:85` | **updated** | Helper now requires assembled method+pathname increment snippet; self-tests reject no-op/includes/unconditional. |
| `page.on('request'` | `docs/execution/plans/2026-08-27-p9-capture-gui/assert-e2e-control-census.ps1:90` | **updated** | Helper now requires assembled method+pathname increment snippet; self-tests reject no-op/includes/unconditional. |
| `page.on('request'` | `docs/execution/plans/2026-08-27-p9-capture-gui/assert-e2e-control-census.ps1:95` | **updated** | Helper now requires assembled method+pathname increment snippet; self-tests reject no-op/includes/unconditional. |
| `page.on('request'` | `docs/execution/plans/2026-08-27-p9-capture-gui/assert-e2e-control-census.ps1:106` | **updated** | Helper now requires assembled method+pathname increment snippet; self-tests reject no-op/includes/unconditional. |
| `page.on('request'` | `docs/execution/plans/2026-08-27-p9-capture-gui/named-sets.json:219` | **updated** | Canonical named-set owner rewritten for the compact listener contract. |
| `page.on('request'` | `docs/execution/plans/2026-08-27-p9-capture-gui/named-sets.json:220` | **updated** | Canonical named-set owner rewritten for the compact listener contract. |
| `expect(0).toBe(0)` | `docs/execution/plans/2026-08-27-p9-capture-gui/plan-review-r2-prompt.txt:35` | **confirmed-consistent** | Historical Round 2 prompt; not a live contract. |
| `expect(0).toBe(0)` | `docs/execution/plans/2026-08-27-p9-capture-gui/named-sets.json:220` | **updated** | Canonical named-set owner rewritten for the compact listener contract. |
| `expect(0).toBe(0)` | `docs/execution/plans/2026-08-27-p9-capture-gui/assert-e2e-control-census.ps1:56` | **updated** | Helper now requires assembled method+pathname increment snippet; self-tests reject no-op/includes/unconditional. |
| `expect(0).toBe(0)` | `docs/execution/plans/2026-08-27-p9-capture-gui/assert-e2e-control-census.ps1:80` | **updated** | Helper now requires assembled method+pathname increment snippet; self-tests reject no-op/includes/unconditional. |
| `expect(0).toBe(0)` | `docs/execution/plans/2026-08-27-p9-capture-gui/assert-e2e-control-census.ps1:82` | **updated** | Helper now requires assembled method+pathname increment snippet; self-tests reject no-op/includes/unconditional. |
| `Test-PostZero` | `docs/execution/plans/2026-08-27-p9-capture-gui/assert-e2e-control-census.ps1:48` | **updated** | Helper now requires assembled method+pathname increment snippet; self-tests reject no-op/includes/unconditional. |
| `Test-PostZero` | `docs/execution/plans/2026-08-27-p9-capture-gui/assert-e2e-control-census.ps1:61` | **updated** | Helper now requires assembled method+pathname increment snippet; self-tests reject no-op/includes/unconditional. |
| `Test-PostZero` | `docs/execution/plans/2026-08-27-p9-capture-gui/assert-e2e-control-census.ps1:81` | **updated** | Helper now requires assembled method+pathname increment snippet; self-tests reject no-op/includes/unconditional. |
| `Test-PostZero` | `docs/execution/plans/2026-08-27-p9-capture-gui/assert-e2e-control-census.ps1:86` | **updated** | Helper now requires assembled method+pathname increment snippet; self-tests reject no-op/includes/unconditional. |
| `Test-PostZero` | `docs/execution/plans/2026-08-27-p9-capture-gui/assert-e2e-control-census.ps1:91` | **updated** | Helper now requires assembled method+pathname increment snippet; self-tests reject no-op/includes/unconditional. |
| `Test-PostZero` | `docs/execution/plans/2026-08-27-p9-capture-gui/assert-e2e-control-census.ps1:96` | **updated** | Helper now requires assembled method+pathname increment snippet; self-tests reject no-op/includes/unconditional. |
| `Test-PostZero` | `docs/execution/plans/2026-08-27-p9-capture-gui/assert-e2e-control-census.ps1:101` | **updated** | Helper now requires assembled method+pathname increment snippet; self-tests reject no-op/includes/unconditional. |
| `Test-PostZero` | `docs/execution/plans/2026-08-27-p9-capture-gui/assert-e2e-control-census.ps1:113` | **updated** | Helper now requires assembled method+pathname increment snippet; self-tests reject no-op/includes/unconditional. |
| `Assert-PostZero` | `docs/execution/plans/2026-08-27-p9-capture-gui/plan-review-r2-prompt.txt:35` | **confirmed-consistent** | Historical Round 2 prompt; not a live contract. |
| `Assert-PostZero` | `docs/execution/plans/2026-08-27-p9-capture-gui/named-sets.json:219` | **updated** | Canonical named-set owner rewritten for the compact listener contract. |
| `Assert-PostZero` | `docs/execution/plans/2026-08-27-p9-capture-gui/assert-e2e-control-census.ps1:60` | **updated** | Helper now requires assembled method+pathname increment snippet; self-tests reject no-op/includes/unconditional. |
| `Assert-PostZero` | `docs/execution/plans/2026-08-27-p9-capture-gui/assert-e2e-control-census.ps1:202` | **updated** | Helper now requires assembled method+pathname increment snippet; self-tests reject no-op/includes/unconditional. |
| `Assert-PostZero` | `docs/execution/plans/2026-08-27-p9-capture-gui/assert-e2e-control-census.ps1:225` | **updated** | Helper now requires assembled method+pathname increment snippet; self-tests reject no-op/includes/unconditional. |
| `url().includes` | `docs/execution/plans/2026-08-27-p9-capture-gui/named-sets.json:220` | **updated** | Canonical named-set owner rewritten for the compact listener contract. |
| `url().includes` | `docs/execution/plans/2026-08-27-p9-capture-gui/assert-e2e-control-census.ps1:95` | **updated** | Helper now requires assembled method+pathname increment snippet; self-tests reject no-op/includes/unconditional. |
| `url().includes` | `docs/execution/plans/2026-08-27-p9-capture-gui/assert-e2e-control-census.ps1:97` | **updated** | Helper now requires assembled method+pathname increment snippet; self-tests reject no-op/includes/unconditional. |
| `WAVE9_REGISTER_POST_SNIPPET` | (none) | **confirmed-consistent** | Old or unused name has 0 hits in the plan folder. |
| `bare '/captures POST'` | (none) | **confirmed-consistent** | Old or unused name has 0 hits in the plan folder. |

---

## Round 4 — 2026-08-27

### Intent Anchor

Executing this plan is intended to deliver Session 18 / MEU-39: the Capture GUI and its Electron OS surfaces, with strict renderer/main/write boundaries, buildable overlay assets, reachable tray/quit behavior, and Wave 9 controls that prove navigation and palette actions do not create captures. Round 4 asks whether the human-authorized post-cap correction closes the sole remaining false-pass without weakening the accepted plan contract; it does.

### Findings

No blocking findings. Round 3 Finding 1 (Round 1 Finding 4) is independently resolved, and no new materially different delivery defect was found in the declared targets.

### Scope

**Targets reviewed**:

- `docs/execution/plans/2026-08-27-p9-capture-gui/implementation-plan.md`
- `docs/execution/plans/2026-08-27-p9-capture-gui/task.md`
- `docs/execution/plans/2026-08-27-p9-capture-gui/named-sets.json`
- all five `assert-*.ps1` files in that folder
- Round 4 correction evidence: `C:/Temp/av-kit/plan-r3-blast-radius.txt`, `C:/Temp/av-kit/plan-r3-per-hit-dispositions.md`, and `## Corrections Applied — 2026-08-27 (Round 3 → Round 4)` above

**Out of scope**: product execution; pytest, vitest, npm test, Playwright, builds, lint, type checks; and edits to product code, tests, plan files, or any file other than this rolling review handoff.

### Commands Executed

Static evidence only. Every substantive shell read/census wrote all process streams to `C:/Temp/av-kit/` and captured exit status before receipt consumption.

- Full line-numbered reads of the plan, task, named sets, all five assertion helpers, prior review rounds, review workflow/template, reviewer contract, and session governance context.
- `Test-Path` readiness and referenced-artifact censuses for planned outputs, invoked tools, templates, configuration, source canon, and rolling artifacts.
- Machine comparison of the Round 3 raw blast-radius receipt against both disposition copies.
- Permitted execution of `assert-e2e-control-census.ps1`; it passed all helper self-tests and then exited at the expected unstarted-plan check for missing `ui/tests/e2e/capture-inbox.test.ts`.
- Isolated replay of the exact Round 3 no-op counterexample against the live `Test-PostZero` function and live named-set values.

No pytest, vitest, npm test, Playwright, build, lint, type check, OpenAPI export, or other plan-local helper was run.

### PR-6 Procedural Gate

`pass` — `C:/Temp/av-kit/plan-r3-blast-radius.txt` is present and untruncated. Independent comparison found 61 raw hits plus 2 zero-hit families, 63 unique keys, and zero duplicates. The duplicate disposition file and the correction table above each contain the same 63 unique keys with zero raw/disposition or copy-to-copy differences.

### Round 3 Finding Recheck

| Round 3 finding | Recheck result | Live evidence |
|---|---|---|
| 1 — `WAVE9_POST_ZERO_ORACLE` accepts a no-op listener | **fixed** | `assert-e2e-control-census.ps1:38-58` assembles and requires the exact compact listener: `req.method() === WAVE9_POST_METHOD`, exact `new URL(req.url()).pathname === WAVE9_CAPTURE_POST_PATH`, counter increment inside both predicates, and `expect(WAVE9_POST_COUNTER).toBe(0)`. Lines 80–115 reject constant-zero, the exact Round 3 no-op, unconditional increment, and `url().includes(path)`, then accept canonical single-line and multiline forms. The isolated replay receipt `C:/Temp/av-kit/r4-exact-noop-replay.txt` reports `PASS: exact Round 3 no-op counterexample rejected`; the full-helper receipt reaches only the later expected missing-E2E boundary. |

Round 1 Findings 1–3 and 5 remain resolved as independently recorded in Round 3; the Round 4 correction does not alter those surfaces.

### Checklist Results

#### Plan Review (PR-1 through PR-9)

| Check | Result | Evidence |
|-------|--------|----------|
| PR-1 Plan/task alignment | pass | Both retain Session 18 / MEU-39 and the same Red → Green → Wave 9 → H1 → independent review → H2 order. |
| PR-2 Not-started confirmation | pass | All 18 actionable task rows remain `[ ]`; planned Capture source, E2E, MEU handoff, implementation review, and reflection outputs are absent. |
| PR-3 Task contract completeness | pass | Every actionable row retains owner, deliverable, exact validation, dependency, context strategy, durable output, builder model, and status. |
| PR-4 Validation realism | pass | The remaining Wave 9 negative oracle now requires the actual counter producer and exact method/path predicates; the exact prior false-pass is rejected. |
| PR-5 Source-backed planning | pass | All 30 ACs remain source-labeled; no unsourced product behavior was introduced by the correction. |
| PR-6 Handoff/corrections readiness | pass | The 61-hit receipt plus 2 zero-hit families reconcile one-to-one with both 63-row disposition copies. |
| PR-7 Scope discipline (C2) | pass | MEU-27 remains separately scheduled; named Phase 9 deferrals and approved MEU-37/38 boundaries remain intact. |
| PR-8 Control reachability/totality | pass | `Test-PostZero` binds the zero assertion to a counter incremented only for exact `POST /api/v1/captures`; the no-op, unconditional, and suffix-matching variants fail. |
| PR-9 Single-statement discipline | pass | The listener contract is owned by named-set values and assembled by the sole helper; no materially conflicting live spelling was found. |

#### Docs Review (DR-1 through DR-8)

| Check | Result | Evidence |
|-------|--------|----------|
| DR-1 Claim-to-state match | pass | The Round 4 correction claim matches the live helper, named sets, plan AC, and replay receipts. |
| DR-2 Residual old terms | pass | The old weak owner phrase and `WAVE9_REGISTER_POST_SNIPPET` have preserved zero-hit dispositions; historical prompt text is explicitly non-live. |
| DR-3 Downstream references | pass | Plan, task, named sets, and helper consistently cite the strengthened oracle contract. |
| DR-4 Verification robustness | pass | The exact Round 3 no-op and all three additional weak forms are rejected before the helper reaches product-file checks. |
| DR-5 Evidence auditability | pass | Static receipts are named, untruncated where required, and independently reproducible. |
| DR-6 Cross-reference integrity | pass | The corrected oracle agrees across AC-39.26, `WAVE9_REGISTER_POST`, `WAVE9_POST_ZERO_ORACLE`, and `Assert-PostZero`. |
| DR-7 Evidence freshness | pass | Targets, helper behavior, task state, artifact existence, and PR-6 evidence were reproduced from current disk state in Round 4. |
| DR-8 Completion vs residual risk | pass | The plan remains unstarted and makes no implementation-complete claim. |

### Open Questions / Assumptions

- No product decision remains open for plan approval.
- The helper deliberately requires the canonical compact listener form. Alternative listener syntax may be rejected even if semantically equivalent; under the workflow Materiality Gate this is a non-blocking implementation constraint, not a demonstrated false-pass.

### Verdict

`approved` — `findings_count: 0`. The authorized Round 4 correction closes the sole remaining High-severity PR-4/PR-8 defect: the exact Round 3 no-op listener can no longer satisfy `Test-PostZero`, and the helper also rejects increment-without-predicates and `url().includes(path)`. PR-6 evidence is complete and reconciles exactly. Executing the plan would deliver the stated MEU-39 objective as a plan contract.

### Follow-Up

Proceed only through the governing plan-to-execution transition. This review does not itself execute product work, tests, commits, merges, releases, or deploys.

### Residual Risk

Approval establishes plan readiness, not runtime correctness. Electron overlay packaging, tray/hotkey lifecycle, OS capture behavior, watcher/poll behavior, and real Wave 9 interactions still require the plan's Red/Green receipts, permitted E2E execution or evidence-gated `[B]`, and independent implementation review.
