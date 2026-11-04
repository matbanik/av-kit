---
date: "2026-08-20"
review_mode: "plan"
target_plan: "docs/execution/plans/2026-08-20-p6-gui-console-polish/implementation-plan.md"
verdict: "approved"
findings_count: 0
template_version: "2.1"
requested_verbosity: "standard"
agent: "Codex GPT-5.6"
round: 3
review_round: 3
---

# Critical Review: p6-gui-console-polish

> **Review Mode**: `plan`
> **Verdict**: `changes_required`

---

## Scope

**Target**: `docs/execution/plans/2026-08-20-p6-gui-console-polish/implementation-plan.md`; `task.md`; `assert-red-oracle.ps1`; `assert-handoff-markers.ps1`; `assert-e2e-control-census.ps1`  
**Supporting evidence**: `docs/build-plan/06-gui.md`; `docs/build-plan/gui-actions-index.md`; current `AppShell.tsx`, `ConsolePanel.tsx`, MEU-26 unit/E2E tests, test-id registry, MEU SSOT/grouping, and referenced executable/template existence  
**Review Type**: Round 1 plan review  
**Checklist Applied**: IR + DR + PR (plan-mode PR-1 through PR-9)

No product, test, spec, task, or plan file was modified.

---

## Findings

Executing the plan is intended to deliver one MEU-27 console-polish insert: Zorivest-style header-left expand/collapse with mounted 40% restore, contained viewport scrolling, exact exclusive level buttons, and black/`#33ff00` console output, without starting MEU-21–25. As written, execution could ship the product behavior while two required verification/documentation deliverables materially false-pass or remain contradictory.

| # | Severity | Confidence | Finding | File:Line | Recommendation | Status |
|---|----------|------------|---------|-----------|----------------|--------|
| 1 | High | High | **PR-4/PR-8/PR-9 — `E2E_CONTROL_CENSUS` can pass without the required outcome assertions.** C1-3 searches `w-full` and `min-w-[320px]` anywhere in the case block; the current C1-3 title already contains both literals, so deleting both geometry assertions would not trip those checks. C1-7 requires only an INFO click plus the words `DEBUG`/`INFO`, with no assertion against `console-output`. C1-8 requires only `overflow-auto` and `--color-console-bg`, with no binding to `console-output`, no foreground-token check, and no `h-screen` check. This is a demonstrated false-pass for materially missing E2E deliverables, and the weaker `E2E_CASE_ORACLES` spelling conflicts with `E2E_CASES`. | `assert-e2e-control-census.ps1:172`; `assert-e2e-control-census.ps1:217`; `assert-e2e-control-census.ps1:222`; `implementation-plan.md:107`; `implementation-plan.md:110`; `task.md:43` | Bind C1-3 geometry assertions to `console-panel` after the corresponding click; bind C1-7 to positive/negative `console-output` text after INFO selection; bind C1-8 to the live output/AppShell classes and both theme variables. Keep one canonical executable statement of each case oracle. | open |
| 2 | High | High | **PR-1/PR-4/DR-2/DR-6 — the planned spec amendment leaves the action index's filter contract stale while its validator passes.** The goal explicitly says the action index must match the new filter contract, but row 5 and `SPEC_AMEND_MARKERS` update/check only `console:collapse` in that index. The live canonical row remains `console:filter | Level dropdown`; all row-5 checks can pass with that contradiction untouched. This materially misdocuments the exclusive-button deliverable. | `implementation-plan.md:21`; `implementation-plan.md:149`; `task.md:44`; `docs/build-plan/gui-actions-index.md:64` | Add the `console:filter` row to the planned action-index edits and bind validation to that exact row requiring exclusive exact-level buttons and rejecting dropdown wording. | open |
| 3 | Medium | High | **PR-4 — the Red validation error branch violates the mandatory immediate exit-code capture rule.** After `assert-red-oracle.ps1`, row 2 runs `Get-Content` before saving the oracle's `$LASTEXITCODE`, then exits using the ambient value. The P0 command contract requires capture before any other command. | `task.md:41` | Save the oracle result immediately (for example, `$oracleCode=$LASTEXITCODE`) and use that captured value after reading the receipt. | open |
| 4 | Low | High | **PR-9 — drawer geometry is restated inside `COLLAPSE_SEMANTIC` immediately before its named owner.** The literal `w-[40%] min-w-[320px] max-w-[500px]` is defined in both rows, creating a clerical stale-clause seam. | `implementation-plan.md:94`; `implementation-plan.md:95` | Make `COLLAPSE_SEMANTIC` reference `CONSOLE_DRAWER_GEOM` without restating its value. | open |

---

## Checklist Results

### Information Retrieval (IR)

| Check | Result | Evidence |
|-------|--------|----------|
| All AC have source labels | pass | AC-27.1–27.10 each have an allowed source classification at `implementation-plan.md:174-183`. |
| Validation cells are exact commands | fail | Commands are concrete, but task row 2 violates immediate exit capture and row 4's census materially false-passes missing outcome assertions. |
| BUILD_PLAN audit row present | pass | The plan contains a dedicated audit and SSOT binding sequence at `implementation-plan.md:289-295` and task rows 7/H1-3. |
| Post-MEU rows present (handoff, reflection, metrics) | pass | H1 handoff/review and H2 reflection/metrics/closeout rows are present and ordered after implementation. |

### Design Review (DR)

| Check | Result | Evidence |
|-------|--------|----------|
| Naming convention followed | pass | Folder, MEU-27 slug, handoff, review, reflection, and receipt names are consistent. |
| Template version present | pass | Plan is v2.0 and task is v2.1; required frontmatter is present. |
| YAML frontmatter well-formed | pass | Both Markdown targets have bounded, parseable frontmatter. |
| Canonical docs remain internally consistent | fail | `gui-actions-index.md:64` remains a Level dropdown, and no planned row/check changes it to the Human-approved button contract. |

### Plan Readiness (PR)

| Check | Result | Evidence |
|-------|--------|----------|
| PR-1 Plan/task alignment | fail | Core implementation scope/order align, but the goal's action-index filter amendment is absent from task row 5 and its validator. |
| PR-2 Not-started confirmation | pass | All 20 task rows are unchecked; `console-polish.test.ts` and the MEU-27 handoff are absent; current code/tests still show MEU-26 behavior. Git evidence was unavailable because this directory has no `.git` metadata. |
| PR-3 Task contract completeness | pass | All 20 actionable rows contain task, owner, deliverable, validation, dependency/context fields, and status. |
| PR-4 Validation realism | fail | Findings 1–3 identify two material false-pass surfaces and one P0 exit-propagation defect. |
| PR-5 Source-backed planning | pass | Product behaviors are tagged Human-approved, Local Canon, Spec, or named governance rules. |
| PR-6 Handoff/corrections readiness | pass | One canonical MEU handoff and one rolling implementation-review path are explicit; Round 1 has no correction-census precondition. |
| PR-7 Scope discipline | pass | Deferred MEU-21–23 rows exist in SSOT/grouping; MEU-21–25 remain outside this insert; no FastAPI/MCP implementation is introduced. |
| PR-8 Control reachability/totality | fail | The production chains are mostly named, but the required E2E negative oracles are not bound to the observable for C1-3/C1-7/C1-8. |
| PR-9 Single-statement discipline | fail | `E2E_CASES` and the weaker `E2E_CASE_ORACLES` materially diverge; drawer geometry is also duplicated clerically. |

---

## Commands Executed

- Numbered full reads of the plan and all three PowerShell oracle scripts.
- `rg` live-state/spec/test census over the console section, action index, current UI code, MEU-26 unit/E2E tests, registry, current focus, SSOT, and grouping.
- Explicit `Test-Path` inventory of referenced tools/templates/current/new artifacts.
- Structural task census: `20` actionable rows, `20` unchecked, `0` malformed column rows, no MEU-27 handoff.
- PowerShell parser check: `0` parse errors for all three reviewed scripts.
- Repeated-literal and deferred-MEU census.

All command output was redirected to canonical receipts under `C:/Temp/av-kit/`. Git status could not run because `P:/av-kit` is not a Git worktree.

---

## Open Questions / Assumptions

- The Human-approved product contract in the review request is authoritative and supersedes the cited MEU-26/spec behavior.
- No Human product decision is outstanding. Findings are correctable through `/plan-corrections` without widening scope or starting MEU-21–25.

---

## Verdict

`changes_required` — Findings 1 and 2 are evidence-backed High defects: the E2E census can certify materially absent outcome coverage, and the canonical action index can remain on the obsolete dropdown contract while the spec-amend gate passes. The Red oracle's distinct-test mapping and the SSOT render-before-`--check` ordering are otherwise sound in this round.

### Required Follow-up

1. Route fixes through `/plan-corrections`; do not edit product code.
2. Bind C1-3, C1-7, and C1-8 to their live observables and consolidate the executable oracle statement.
3. Add and validate the `console:filter` action-index amendment.
4. Preserve the Red oracle exit code immediately and remove the clerical drawer-geometry restatement.

### Residual Risk

After these corrections, the principal remaining execution risk is runtime Electron availability. The plan already handles that as an evidence-gated E2E run blocker while requiring the tests to remain written and wired.

---

## Corrections Applied — 2026-08-20 (Round 1 → re-review)

Implementor corrections only. Verdict remains `corrections_applied` until an independent reviewer writes `approved`.

| # | Status | Change |
|---|--------|--------|
| 1 | updated | `E2E_CASES` now requires `console-panel` bound to `w-full` / `min-w-[320px]` after the matching clicks; C1-7 binds `console-output` to INFO present / DEBUG oracle; C1-8 binds `console-output` to both theme vars + `overflow-auto` and `app-shell` to `h-screen`. `E2E_CASE_ORACLES` is an alias of `E2E_CASES`. Census script gained `Test-BoundNearLiteral` + title-only false-pass self-tests. |
| 2 | updated | `SPEC_AMEND_MARKERS` + task row 5 now require the `console:filter` row to contain `exclusive exact-level buttons` and reject `dropdown`. |
| 3 | updated | Task row 2 captures `$oracleCode=$LASTEXITCODE` immediately after `assert-red-oracle.ps1`. |
| 4 | updated | `COLLAPSE_SEMANTIC` and lock 4 reference `CONSOLE_DRAWER_GEOM` without restating the width literal. Owner remains the named-set row. |

Blast-radius census: 4 values (`CONSOLE_DRAWER_GEOM` literal, `Level dropdown`, `exclusive exact-level buttons`, `$oracleCode`). Geometry literal now only at the named-set owner. `Level dropdown` remains only as the SUPERSEDED_26 stale label. Filter marker present in plan + task row 5. `$oracleCode` present once in task row 2.

Receipts: `C:/Temp/av-kit/census-geom.txt`, `census-dropdown.txt`, `census-filter.txt`, `census-oracle.txt`.

---

## Round 2 Review — 2026-08-20

> **Review Mode**: `plan`  
> **Round**: 2  
> **Verdict**: `changes_required`

### Intent Anchor

Executing this plan is intended to deliver the MEU-27 console-polish insert while preserving the approved scope boundary around MEU-21–25. Round 2 cannot determine whether the corrected plan would deliver that objective because the mandatory PR-6 correction-census evidence is not dispositioned per hit.

### PR-6 Procedural Gate

`changes_required` — the four named census receipts exist and contain raw `rtk proxy` output without a visible truncation marker, but the correction log does not assign every receipt hit an explicit `updated` or `confirmed-consistent` disposition. The table at lines 124–127 assigns status to the four prior findings, while the census paragraph at line 129 gives aggregate value-level summaries only; neither maps the eight receipt hits individually. In addition, `census-oracle.txt` emits `41:` without the source path, so that hit is not auditable as a receipt `file:line` identity. This is the Round-2 PR-6 pre-verdict procedural exception, not a severity-rated finding; `findings_count` is therefore `0`.

Receipt hit inventory observed before the gate closed:

| Receipt | Raw hits | Per-hit dispositions in correction log |
|---------|----------|----------------------------------------|
| `C:/Temp/av-kit/census-geom.txt` | 2 | missing |
| `C:/Temp/av-kit/census-dropdown.txt` | 2 | missing |
| `C:/Temp/av-kit/census-filter.txt` | 3 | missing |
| `C:/Temp/av-kit/census-oracle.txt` | 1 | missing; source path omitted |

Per workflow, corrected plan/task/script content and PR-1 through PR-5, PR-7 through PR-9, and DR checks were not reviewed this round.

### Scope and Commands

- Read the existing rolling review before evaluating Round 2.
- Read all four named census receipts verbatim and recorded existence, byte length, line count, and raw contents in `C:/Temp/av-kit/round2-census-inspection.txt`.
- Located the correction-log status rows and census summary at rolling-review lines 118–131 in `C:/Temp/av-kit/round2-correction-log-lines.txt`.
- Enforced the Pre-Edit Guard in `C:/Temp/av-kit/round2-preedit-guard.txt`; the derived and authorized canonical paths matched exactly.

### Required Follow-up

Re-run or preserve each untruncated raw census with source `file:line` identities, then add a correction-log row for every hit with exactly one disposition: `updated` or `confirmed-consistent`. Re-submit the same rolling review for Round 3; do not start implementation.

### Verdict

`changes_required` — PR-6 failed before substantive review because the correction log does not disposition every raw census hit. No corrected-content finding is made in Round 2.

### Residual Risk

The four claimed Round 1 corrections and the remaining PR/DR checklist are unassessed in this round by mandatory workflow design.

---

## Corrections Applied — 2026-08-20 (Round 2 PR-6 census)

Implementor only. Verdict is `corrections_applied` until an independent reviewer writes `approved`.

Re-ran all four untruncated `rtk proxy rg -F -n` sweeps against **both** plan files so every hit has a `file:line` identity. Receipts overwritten in place: `C:/Temp/av-kit/census-geom.txt`, `census-dropdown.txt`, `census-filter.txt`, `census-oracle.txt`.

| Receipt | file:line | Disposition | Why |
|---------|-----------|-------------|-----|
| `census-geom.txt` | `implementation-plan.md:95` | confirmed-consistent | Sole remaining width literal; this is the `CONSOLE_DRAWER_GEOM` named-set owner. Lock 4 / `COLLAPSE_SEMANTIC` no longer restate it (old r1 hit at `:75` is gone). |
| `census-dropdown.txt` | `implementation-plan.md:21` | confirmed-consistent | Goal prose names the **old** widget being replaced ("Level dropdown" → exclusive buttons). Not a second owner of the action-index label. |
| `census-dropdown.txt` | `implementation-plan.md:105` | confirmed-consistent | `SUPERSEDED_26` intentionally quotes the stale `console:filter` label `Level dropdown`. |
| `census-filter.txt` | `implementation-plan.md:21` | confirmed-consistent | Goal already uses the new phrase `exclusive exact-level buttons`. |
| `census-filter.txt` | `implementation-plan.md:149` | updated | `SPEC_AMEND_MARKERS` requires that exact phrase on the `console:filter` row and rejects `dropdown`. |
| `census-filter.txt` | `task.md:44` | updated | Row 5 validator binds the same `console:filter` phrase and rejects `dropdown`. |
| `census-oracle.txt` | `task.md:41` | updated | `$oracleCode=$LASTEXITCODE` captured immediately after `assert-red-oracle.ps1`. Path is now present (both files were searched). |

Blast-radius census: 4 values, 7 raw hits, 3 updated, 4 confirmed-consistent. Zero undispositioned hits.

Round 1 content corrections (E2E bind, filter amend, oracle capture, geometry owner) are unchanged and still on disk.

---

## Round 3 Review — 2026-08-20

> **Review Mode**: `plan`  
> **Round**: 3 (plan-review cap)  
> **Verdict**: `approved`

### Intent Anchor

Executing this plan is intended to deliver the MEU-27 console-polish insert: a single Zorivest-style header-left expand/collapse toggle, mounted 40% restore behavior, viewport-contained console scrolling, exclusive exact-level buttons, and black/`#33ff00` output, while leaving MEU-21–25 unstarted. The corrected plan and task table now provide a coherent, source-backed TDD and verification path to that objective.

### Findings

No blocking findings. The fresh PR-6 census is complete and dispositioned, and substantive review found no `High` or `Critical` defect under the Materiality Gate.

### Non-Blocking Correction Notes

1. **Low — predicate-shape residual (PR-4/PR-8):** C1-7's executable census binds `console-output` to INFO/DEBUG literals and accepts `toContainText`, `toHaveText`, or `not.toContainText`, but it does not require INFO to use a positive matcher and DEBUG to use a negative matcher specifically (`assert-e2e-control-census.ps1:269-272`). This is a residual predicate-shape risk on the already-corrected Round 1 surface, not a new materially different delivery failure; per the no-nearby-mutation and predicate-cap rules it does not block approval.
2. **Low — clerical inventory wording (PR-1):** the `Files Modified` summary for `gui-actions-index.md` mentions only the collapse persist key (`implementation-plan.md:226`), while the Goal, WP-27e, `SPEC_AMEND_MARKERS`, and task row 5 all explicitly include the filter-label amendment (`implementation-plan.md:21,55,149`; `task.md:44`). The executable contract is unambiguous; the one-line summary can be expanded during a later clerical cleanup.

### PR-6 Procedural Gate

`pass` — all four named receipts were re-run untruncated with `rtk proxy rg -F -n` against both plan files. They contain seven raw, path-qualified hits, and the Round 2 correction table assigns every one exactly one allowed disposition.

| Receipt | Fresh raw hits | Disposition coverage |
|---------|----------------|----------------------|
| `C:/Temp/av-kit/census-geom.txt` | `implementation-plan.md:95` | 1/1 `confirmed-consistent` |
| `C:/Temp/av-kit/census-dropdown.txt` | `implementation-plan.md:21,105` | 2/2 `confirmed-consistent` |
| `C:/Temp/av-kit/census-filter.txt` | `implementation-plan.md:21,149`; `task.md:44` | 3/3 (`confirmed-consistent`, `updated`, `updated`) |
| `C:/Temp/av-kit/census-oracle.txt` | `task.md:41` | 1/1 `updated` |

### Checklist Results

#### Information Retrieval (IR)

| Check | Result | Evidence |
|-------|--------|----------|
| All AC have source labels | pass | AC-27.1–27.10 each carry an allowed source basis at `implementation-plan.md:174-183`. |
| Validation cells are exact commands | pass | All 20 task rows provide concrete receipt-backed commands; the Round 1 Red exit-capture defect is corrected at `task.md:41`. |
| BUILD_PLAN audit row present | pass | The hub/SSOT audit and exact validation are present at `implementation-plan.md:290-295` and `task.md:46,51`. |
| Post-MEU rows present | pass | H1 handoff/review and H2 reflection/metrics/closeout rows are explicit at `task.md:48-63`. |

#### Design Review (DR)

| Check | Result | Evidence |
|-------|--------|----------|
| DR-1 Claim-to-state match | pass | The correction log matches the corrected plan/task/script lines and all seven fresh census hits. |
| DR-2 Residual old terms | pass | `Level dropdown` remains only in Goal replacement prose and the named `SUPERSEDED_26` inventory (`implementation-plan.md:21,105`). |
| DR-3 Downstream references | pass | WP-27e, `SPEC_AMEND_MARKERS`, task row 5, and the file inventory all route the canonical spec/action-index amendments. |
| DR-4 Verification robustness | pass with note | Round 1 material false-passes are closed; the remaining C1-7 polarity-shape note is capped as Low above. |
| DR-5 Evidence auditability | pass | Census, parser, structure, and live-state commands have reproducible receipts under `C:/Temp/av-kit/`. |
| DR-6 Cross-reference integrity | pass | Named sets, ACs, work packages, task rows, and superseded MEU-26 contracts agree on the new behavior. |
| DR-7 Evidence freshness | pass | Fresh census totals are 1 + 2 + 3 + 1 = 7 and match the correction log exactly. |
| DR-8 Completion vs residual risk | pass | The plan is explicitly unstarted; no implementation-complete claim or implementation handoff exists. |

#### Plan Readiness (PR)

| Check | Result | Evidence |
|-------|--------|----------|
| PR-1 Plan/task alignment | pass with note | Scope, order, deliverables, and validation align; only the clerical file-summary wording noted above is abbreviated. |
| PR-2 Not-started confirmation | pass | All 20 actionable task rows are unchecked; `console-polish.test.ts`, the MEU-27 handoff, and the reflection are absent; live code/tests/spec remain at MEU-26 behavior. |
| PR-3 Task contract completeness | pass | All 20 actionable rows include task, owner, deliverable, validation, dependency/context, durable outputs, and status. |
| PR-4 Validation realism | pass with note | Corrected Red, spec-amend, E2E, MEU, and closeout checks are specific enough to prevent materially missing deliverables; the capped C1-7 polarity note remains. |
| PR-5 Source-backed planning | pass | Every product rule is tagged Human-approved, Spec, Local Canon, or a named governance rule. |
| PR-6 Handoff/corrections readiness | pass | Canonical handoff/review paths are explicit and the seven-hit correction census is complete. |
| PR-7 Scope discipline | pass | Deferred MEU-21–23 rows cite scheduled MEUs; other exclusions cite the Human-approved supersession, current focus/grouping, or unchanged locked spec. |
| PR-8 Control reachability/totality | pass with note | Production observables and caller chains are explicit at `implementation-plan.md:185-195`; corrected E2E cases bind the material controls, subject to the capped polarity note. |
| PR-9 Single-statement discipline | pass | Drawer geometry has one literal owner at `implementation-plan.md:95`; `E2E_CASE_ORACLES` aliases `E2E_CASES`; other repeated contracts reference named sets. |

### Commands Executed

- Read the review workflow, template, complete rolling review, plan, task, and all three oracle scripts.
- Re-ran all four exact, unfiltered correction censuses into the user-named receipt paths; seven path-qualified hits reproduced with zero undispositioned hits.
- Ran a live spec/code/test/SSOT census confirming MEU-26 behavior remains in place and MEU-27 implementation has not started.
- Parsed all three PowerShell oracle scripts with `System.Management.Automation.Language.Parser`: `0` errors each.
- Counted `20` actionable task rows, all `20` unchecked, and verified the new MEU-27 test, handoff, and reflection do not yet exist.
- Enforced the canonical review handoff pre-edit guard at `C:/Temp/av-kit/round3-preedit-guard.txt`.

### Open Questions / Assumptions

- No product decision remains open. The Human-approved 2026-08-20 behavior is treated as the authorized supersession of the cited MEU-26/spec behavior.
- Approval authorizes the plan as review-ready only. Per the user's explicit instruction for this Round 3 review, MEU-21–25 and MEU-27 execution were not started.

### Verdict

`approved` — PR-6 passes, all four Round 1 corrections are present, the plan/task/oracles align, and no evidence-backed `High` or `Critical` defect remains. The two surviving notes are Low clerical/predicate-shape items and therefore do not contribute to `findings_count`, which remains `0` for the approved verdict.

### Follow-up

- Stop at this completed Round 3 review. Do not start MEU-21–25 or apply plan/product edits in this workflow.
- If execution is later authorized in a separate user-directed step, follow the approved task table from row 1 and preserve the TDD/review gates.

### Residual Risk

The main runtime risk remains Electron availability for the real Playwright run, already handled by the plan's evidence-gated `[B]` rule without allowing test omission. The C1-7 matcher-polarity predicate note above is a small auditability risk, not a demonstrated reason the plan would fail to deliver the requested console behavior.
