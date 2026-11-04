---
date: "2026-09-20"
review_mode: "plan"
target_plan: "docs/execution/plans/2026-09-20-p6-gui-login-item/implementation-plan.md"
agent: "gpt-5.6-sol"
verdict: "approved"
findings_count: 0
dispatch_id: "p6-gui-login-item-plan-r2"
template_version: "2.1"
requested_verbosity: "standard"
---

# Critical Review: 2026-09-20-p6-gui-login-item

> **Review Mode**: `plan`
> **Verdict**: `approved`

## Intent Anchor

Executing this plan is supposed to add a per-user, OS-backed Electron login item with an optional whole-token `--start-minimized` launch, hide the control in unsupported/unpackaged copies, clean both Windows login-item values on NSIS uninstall, and leave Phase 11 Next at MEU-50. The core product contract is represented, but two validation paths can report success while those last two material outcomes are wrong.

---

## Findings

| # | Severity | Confidence | Finding | File:Line | Recommendation | Status |
|---|----------|------------|---------|-----------|----------------|--------|
| PCR-1 | High | High | **PR-4 / PR-8 — the BUILD_PLAN audit false-passes the explicit “Next remains MEU-50” control.** Row 8 says to rewrite `HUB_NEXT_FIELD` to `HUB_NEXT_AFTER` and preserve `PRIOR_PLAN_SLASHES`, but its command only prints the count/line numbers for `MEU-61` and `p6-gui-login-item`; it has no failure condition, never reads either named set, and exits 0 with zero matches or with `Next:` changed to MEU-61. `meu_status.py render --check` only checks AUTOGEN regions, so it does not bind this narrative field. This is a demonstrated false-pass for a user-required project-state deliverable. | `docs/execution/plans/2026-09-20-p6-gui-login-item/task.md:50`; `docs/execution/plans/2026-09-20-p6-gui-login-item/implementation-plan.md:233`; `docs/execution/plans/2026-09-20-p6-gui-login-item/named-sets.json:13` | Make the row-8 validator fail unless there is exactly one `Next:` field equal to `HUB_NEXT_AFTER`, every `PRIOR_PLAN_SLASHES` entry remains present, and the MEU-61 plan binding is present. Route the check through a plan-local script that reads `named-sets.json` so the literals remain single-owned. | corrected |
| PCR-2 | High | High | **PR-4 / PR-8 — the NSIS proof is token-presence only and can pass without deleting both registry values.** The source requires two executable `DeleteRegValue` statements and `nsis.include: build/installer.nsh`. The gate merely finds each token anywhere in `installer.nsh` and the include path anywhere in YAML. For example, one real Run deletion plus the StartupApproved path in a comment satisfies every current check while leaving the dead StartupApproved entry; a misplaced include string likewise passes. AC-61.18 and row 5 therefore do not bind the observable to the uninstall call chain. | `docs/build-plan/07-distribution.md:192`; `docs/execution/plans/2026-09-20-p6-gui-login-item/implementation-plan.md:169`; `docs/execution/plans/2026-09-20-p6-gui-login-item/task.md:47`; `docs/execution/plans/2026-09-20-p6-gui-login-item/assert-meu-scans.ps1:59` | Strengthen AC-61.18 and its Red/Green test so non-comment code must contain two correctly bound `DeleteRegValue HKCU` calls—one for each required key and `LOGIN_ITEM_NAME`—and validate that `NSH_INCLUDE` is the actual `nsis.include` value. Include a negative fixture/oracle where all tokens exist but the second executable deletion is absent. | corrected |
| PCR-3 | Low | High | **PR-9 — several named literals are restated instead of single-owned.** `IPC_GET`/`IPC_SET` are repeated in `IPC_CHANNELS`; `LOGIN_ITEM_NAME` is repeated in `NSH_TOKENS`; the three test IDs are repeated in `E2E_TESTIDS`/`E2E_BODY_TOKENS`; and `E2E_GREP` is repeated in `E2E_REQUIRED_CASES` and hard-coded in both Playwright commands. Values currently agree, so this is clerical and non-blocking under the Materiality Gate, but the clusters can drift. | `docs/execution/plans/2026-09-20-p6-gui-login-item/named-sets.json:91`; `docs/execution/plans/2026-09-20-p6-gui-login-item/named-sets.json:94`; `docs/execution/plans/2026-09-20-p6-gui-login-item/named-sets.json:210`; `docs/execution/plans/2026-09-20-p6-gui-login-item/task.md:48` | Keep each literal once and derive composite arrays/commands in the owning assertion or runner script from the scalar names. | corrected |
| PCR-4 | Low | High | **DR-1 clerical drift — the E2E classifier header still names AC-60.12.** The executable logic reads `E2E_GREP`, so behavior is not affected, but the ownership comment is stale for MEU-61 / AC-61.17. | `docs/execution/plans/2026-09-20-p6-gui-login-item/assert-e2e-classify.ps1:1` | Rename the comment to AC-61.17 during `/plan-corrections`. | corrected |

---

## Scope

**Target**: `docs/execution/plans/2026-09-20-p6-gui-login-item/implementation-plan.md`, `task.md`, `named-sets.json`, all nine `assert-*.ps1` files, the MEU-61 build-plan sections, priority matrix/action index, session grouping, MEU status, current GUI/IPC/E2E integration surfaces, and BUILD_PLAN hub narrative.

**Review Type**: first-pass review of an unstarted plan.

**Checklist Applied**: IR + DR + PR-1 through PR-9.

**Out of scope**: product implementation, test implementation, plan corrections, execution review, commit/push.

---

## Checklist Results

### Information Retrieval (IR)

| Check | Result | Evidence |
|-------|--------|----------|
| All AC have source labels | pass | 22 AC-61 rows; each includes `Spec`, `Local Canon`, `Research-backed`, or `Human-approved`. |
| Validation cells are exact commands | fail | Commands are concrete and scripts exist, but PCR-1 and PCR-2 demonstrate material false-pass behavior. |
| BUILD_PLAN audit row present | fail | Row 8 exists, but its predicate does not assert `HUB_NEXT_AFTER` or `PRIOR_PLAN_SLASHES`. |
| Post-MEU rows present (handoff, reflection, metrics) | pass | H1-1 through H1-7 and H2-1 through H2-5 are ordered in `task.md`. |

### Design Review (DR)

| Check | Result | Evidence |
|-------|--------|----------|
| Naming convention followed | pass | Plan folder, plan/task files, MEU-61 handoff, and rolling review names are canonical. |
| Template version present | pass | Plan `2.0`; task/review `2.1`. |
| YAML frontmatter well-formed | pass | Plan/task frontmatter and `named-sets.json` parsed; all 119 named-set keys loaded. |
| Source/build-plan alignment | pass | Login item is separated from service/WinSW; portable is excluded by NSIS-only canon; MEU-58 retains Settings layout IDs. |
| Hub ownership | fail | The stated MEU-50 Next invariant is not bound to a failing validator (finding 1). |

### Plan Review (PR)

| Check | Result | Evidence |
|-------|--------|----------|
| PR-1 Plan/task alignment | pass | Both artifacts sequence Red → main/IPC → Settings → NSIS → named E2E → gate → hub → H1/review/H2. |
| PR-2 Not-started confirmation | pass | All 21 actionable rows are `[ ]`; MEU-61 is `pending`; no MEU-61 implementation handoff or new product modules exist. |
| PR-3 Task contract completeness | pass | All 21 actionable rows contain owner, deliverable, validation, dependency/context strategy, durable output, and status. |
| PR-4 Validation realism | fail | Hub and NSIS validators have demonstrated material false-pass cases (PCR-1 and PCR-2). |
| PR-5 Source-backed planning | pass | Product behaviors trace to the two build-plan sections, local canon, Electron/NSIS research links, or USER_EXPLICIT default-off lock. |
| PR-6 Handoff/corrections readiness | pass | Canonical MEU handoff and rolling implementation-review paths are explicit; this is round 1, so no correction census is required. |
| PR-7 Scope discipline (C2) | pass | Service/WinSW is excluded by 06/07 canon; portable by NSIS-only scope; MEU-58 is a real pending deferral; live packaged proof remains Phase 7. |
| PR-8 Control reachability/totality | fail | IPC extra-forbid, direct `TypeError`/zero Electron calls, whole-token argv, and unpackaged panel absence are adequately planned; hub and NSIS controls are not bound (PCR-1 and PCR-2). |
| PR-9 Single-statement discipline | fail (Low) | Repeated literal clusters are listed in PCR-3; current spellings agree, so this does not independently block. |

---

## Status and Evidence

- Readiness receipt: `C:/Temp/av-kit/plan-review-readiness.txt` — 21 unchecked rows, zero in-progress/complete/blocked rows; no MEU-61 handoff or new login-item modules.
- Referenced-script receipt: `C:/Temp/av-kit/plan-review-validation-script-existence.txt` — every validation `.ps1`/`.py` named by task commands exists. `tools/validate_closeout_artifacts.py` is absent exactly as declared by `ABSENT_VALIDATOR_RULE` and is not invoked.
- Parser receipt: `C:/Temp/av-kit/plan-review-script-parse.txt` — all 9 plan-local PowerShell scripts parse with zero errors.
- Current negative-E2E receipt: `C:/Temp/av-kit/plan-review-e2e-current-absence.txt` — the panel token has zero hits in today's Settings page, E2E spec, and test-id registry. Census-first for AC-61.17 is therefore intentional; no fake assertion-Red is required.
- PR-9 census: `C:/Temp/av-kit/plan-review-pr9-census.txt`.
- Hub-binding census: `C:/Temp/av-kit/plan-review-hub-binding-census.txt`; current hub receipt: `C:/Temp/av-kit/plan-review-hub-next.txt`.
- Pre-edit guard: `C:/Temp/av-kit/plan-review-pre-edit-guard.txt` — canonical review target matched exactly and did not previously exist.

### Commands Executed

```powershell
rtk proxy pwsh -NoProfile -Command '<extract task validation .ps1/.py paths; Test-Path each>'
rtk proxy pwsh -NoProfile -Command '<count task states; Test-Path MEU-61 handoff/new modules>'
rtk proxy pwsh -NoProfile -Command '<parse all assert-*.ps1 with PowerShell Parser>'
rtk proxy rg -F -n -e 'HUB_NEXT_AFTER' -e 'HUB_NEXT_FIELD' -e 'PRIOR_PLAN_SLASHES' -e 'MEU-50' docs/execution/plans/2026-09-20-p6-gui-login-item
rtk proxy rg -F -n -e 'login-item-get' -e 'login-item-set' -e 'AC-61.17' -e 'com.avkit.app' -e 'start-at-sign-in-panel' -e '--start-minimized' docs/execution/plans/2026-09-20-p6-gui-login-item/{implementation-plan.md,task.md,named-sets.json}
rtk proxy git status --short
```

All command output was redirected to exact receipts under `C:/Temp/av-kit/` before being read.

---

## Open Questions / Assumptions

- No product decision is open. The two blocking findings concern proof binding, not the selected login-item behavior.
- AC-61.17 is accepted as a negative unpackaged-absence contract that already holds; its Red phase is the written census, not an intentionally false UI assertion.

## Verdict

`changes_required` — PCR-1 and PCR-2 are evidence-backed High findings under PR-4/PR-8: each permits a green gate while a material required outcome is absent. Apply corrections through `/plan-corrections`, then append the round-2 recheck to this same file with the required blast-radius census and per-hit dispositions.

## Residual Risk

No implementation gates were run because their product inputs are intentionally uncreated. After the two blocking predicates are corrected, the remaining risk is ordinary implementation correctness covered by the 21 unit/RTL Red titles, the census-first AC-61.17 E2E, the MEU gate, and independent execution review.

---

## Corrections Applied (2026-09-20)

**Workflow**: `/plan-corrections` (inline from `/create-plan` Step 5b)
**Agent**: coordinator (not reviewer)
**Verdict**: `corrections_applied` (never `approved`)
**Index receipt**: `C:/Temp/av-kit/census-p6-gui-login-item-r2-index.txt`
**Hub static run**: `C:/Temp/av-kit/census-p6-r2-hub-next-run.txt` — `PASS: hub Next + prior plans + MEU-61 bind` (current hub already starts with `HUB_NEXT_AFTER`; the old Select-String counter is gone)

Blast-radius census: **8 values/variants** swept old+new across both plan files; folder extra-sweeps for `NSH_TOKENS` and `AC-60.12`. All 11 `assert-*.ps1` parse; `named-sets.json` parses.

### PCR-1

Row 8 / BUILD_PLAN audit now runs `assert-hub-next.ps1` (`HUB_CHECK`). The script fails unless there is exactly one `Next:`, the remainder of that field **starts with** `HUB_NEXT_AFTER` (the hub sentence shares a paragraph with `Matrix:`), every `PRIOR_PLAN_SLASHES` entry remains in `meu-status.yaml`, `PLAN_FOLDER` is bound, and `BUILD_PLAN.md` contains `MEU-61`.

### PCR-2

`assert-meu-scans.ps1` strips NSIS `;` comments, requires exactly two executable `DeleteRegValue HKCU` lines (`NSH_RUN_KEY`+`LOGIN_ITEM_NAME` without `StartupApproved`, and `NSH_APPROVED_KEY`+`LOGIN_ITEM_NAME`), and requires the YAML `nsis:` mapping `include` value to equal `NSH_INCLUDE`. Embedded negative fixtures: comment-only StartupApproved plus one real Run delete must not pass; `include` only in a YAML comment or non-`nsis` mapping must not bind. AC-61.18, 07-distribution, 06-gui uninstall, row 5, and `ui/tests/unit/login-item-nsh.test.ts` were aligned.

### PCR-3

Dropped `IPC_CHANNELS`, `NSH_TOKENS`, `E2E_TESTIDS`, and `E2E_REQUIRED_CASES`. Census derives testids from `PANEL_TESTID`/`ENABLED_TESTID`/`MINIMIZED_TESTID` and the case from `E2E_GREP`. Named Playwright commands go through `assert-e2e-named.ps1` (`E2E_NAMED`), which derives the npm spec path from `E2E_SPEC` (`ui/` prefix strip). Gate named-result delegates to `E2E_NAMED -Mode gate`.

### PCR-4

`assert-e2e-classify.ps1` header now names `E2E_GREP` / AC-61.17.

### Per-hit dispositions (plan + task)

Old-value receipts (`C:/Temp/av-kit/census-p6-r2-old-*.txt` and folder extras): **no `file:line` hits** (rtk hook line only) — `NSH_TOKENS`, `IPC_CHANNELS`, `E2E_TESTIDS`, `E2E_REQUIRED_CASES`, `AC-60.12`, `--grep AC-61.17`, `Select-String -Path docs/BUILD_PLAN.md` — **confirmed-consistent (removed)**.

| file:line | value | disposition |
|-----------|-------|-------------|
| `implementation-plan.md:236` | `HUB_CHECK` | updated |
| `task.md:50` | `HUB_CHECK` / `assert-hub-next.ps1` | updated |
| `implementation-plan.md:239` | `assert-hub-next.ps1` | updated |
| `task.md:47` | `NSH_RUN_KEY` / `NSH_APPROVED_KEY` / `nsis.include` / executable NSIS | updated |
| `implementation-plan.md:64` | `NSH_RUN_KEY` / `NSH_APPROVED_KEY` / `nsis.include` / executable NSIS | updated |
| `implementation-plan.md:103` | `NSH_RUN_KEY` / `NSH_APPROVED_KEY` / `nsis.include` / `comment-only` | updated |
| `implementation-plan.md:169` | `NSH_RUN_KEY` / `NSH_APPROVED_KEY` / `nsis.include` / `comment-only` / executable NSIS | updated |
| `implementation-plan.md:206` | `nsis.include` | confirmed-consistent |
| `implementation-plan.md:207` | executable `DeleteRegValue HKCU` | updated |
| `implementation-plan.md:208` | executable NSIS / nsh unit test | updated |
| `task.md:44` | `E2E_NAMED` | updated |
| `task.md:48` | `E2E_NAMED` / `assert-e2e-named.ps1` | updated |
| `implementation-plan.md:65` | `E2E_NAMED` | updated |
| `implementation-plan.md:253` | `assert-e2e-named.ps1` | updated |
| `implementation-plan.md:96` | `executable` (`executableWillLaunchAtLogin`) | confirmed-consistent (Electron field, not NSIS) |
| `implementation-plan.md:156` | `executable` (`executableWillLaunchAtLogin`) | confirmed-consistent (Electron field, not NSIS) |
| `implementation-plan.md:184` | `executable` (`executableWillLaunchAtLogin`) | confirmed-consistent (Electron field, not NSIS) |

Cross-doc: `docs/build-plan/07-distribution.md` Login item uninstall and `docs/build-plan/06-gui.md` Uninstall pointer now require two executable (non-comment) `DeleteRegValue HKCU` statements and the `nsis.include` **value**.

---

## Recheck — 2026-09-20 (Round 2)

**Workflow**: `/plan-critical-review` after `/plan-corrections`  
**Agent**: `gpt-5.6-sol`  
**Dispatch ID**: `p6-gui-login-item-plan-r2`

### Intent Anchor

Executing this plan is supposed to add a default-off, per-user Electron login item with whole-token `--start-minimized` handling, hide the control in unsupported or unpackaged copies, remove both Windows login-item values during NSIS uninstall, and preserve Phase 11 / MEU-50 as the hub's Next work. The corrected plan would deliver that objective without introducing a Windows service, `PUT /settings`, G23 form behavior, or MEU-50 implementation.

### PR-6 Census Gate

`pass` — the correction log names `C:/Temp/av-kit/census-p6-gui-login-item-r2-index.txt`, and every receipt named or derived by that index exists and was read in full. The nine old/folder-old receipts contain no plan-folder `file:line` hit; the nine new-value receipts contain 33 raw value-hit lines across 17 unique plan/task locations, and every location has an explicit `updated` or `confirmed-consistent` disposition in the Corrections Applied table. The separate hub static receipt exists and is logged. No indexed receipt is missing, truncated, or paired without a correction-log disposition.

### Findings

None.

### Prior Pass Summary

| Finding | Prior Status | Recheck Result |
|---------|--------------|----------------|
| PCR-1 High — hub Next false-pass | corrected | ✅ Fixed — `assert-hub-next.ps1` fails unless `Next:` occurs exactly once, its remainder starts with `HUB_NEXT_AFTER`, every `PRIOR_PLAN_SLASHES` entry remains, `PLAN_FOLDER` is bound, and the hub contains MEU-61. Task row 8 invokes this script. |
| PCR-2 High — NSIS token-presence false-pass | corrected | ✅ Fixed — `assert-meu-scans.ps1` strips `;` comments, requires exactly two bound executable `DeleteRegValue HKCU` lines, validates the actual `nsis.include` value, and contains both requested negative fixtures. AC-61.18 and task row 5 match. |
| PCR-3 Low — restated literals | corrected | ✅ Fixed — `IPC_CHANNELS`, `NSH_TOKENS`, `E2E_TESTIDS`, and `E2E_REQUIRED_CASES` have no hit in the plan folder; named Playwright execution is owned by `assert-e2e-named.ps1`. |
| PCR-4 Low — stale classifier comment | corrected | ✅ Fixed — the classifier header names `E2E_GREP / AC-61.17`; `AC-60.12` has no hit in the plan folder. |

### Confirmed Fixes

- `assert-hub-next.ps1:19-29` binds the unique `Next:` prefix to `HUB_NEXT_AFTER`; lines 31-45 bind every prior plan, `PLAN_FOLDER`, and MEU-61. `task.md:50` invokes the script rather than a `Select-String` counter. The supplied static receipt `C:/Temp/av-kit/census-p6-r2-hub-next-run.txt` reports `PASS: hub Next + prior plans + MEU-61 bind`, and the live hub sentence at `docs/BUILD_PLAN.md:72` starts with the named MEU-50 text.
- `assert-meu-scans.ps1:16-50` strips NSIS semicolon comments and requires exactly two `DeleteRegValue HKCU` lines with one Run-key and one StartupApproved-key binding to `LOGIN_ITEM_NAME`. Lines 110-142 reject a comment-only second deletion and an include found only in a comment or non-`nsis` mapping; lines 144-148 bind the live `nsis.include` value. This matches `implementation-plan.md:169`, `task.md:47`, and `docs/build-plan/07-distribution.md:192-196`.
- `assert-e2e-named.ps1:1-30` owns the named AC-61.17 Playwright route, `task.md:48` calls it, and `assert-e2e-classify.ps1:1-2` identifies AC-61.17 rather than AC-60.12.
- The unchanged locks remain aligned: login item rather than WinSW/UAC/LocalSystem (`docs/build-plan/06-gui.md:1082-1088`), default off (`06-gui.md:1108`), no Settings Save/G23/`PUT /settings` (`06-gui.md:1112`), unpackaged absence (`06-gui.md:1137`), and MEU-50 still Next (`docs/BUILD_PLAN.md:72`).

### Checklist Results

#### Plan Review (PR)

| Check | Result | Evidence |
|-------|--------|----------|
| PR-1 Plan/task alignment | pass | Plan work packages and task rows retain Red → main/IPC → Settings → NSIS → named E2E → gate → hub → H1/review/H2 ordering. |
| PR-2 Not-started confirmation | pass | Both artifacts remain `draft`; every actionable task row is `[ ]`; the four planned new product files, MEU-61 handoff, and implementation-review file are absent. |
| PR-3 Task contract completeness | pass | Every actionable row retains task, owner, deliverable, exact validation, dependency, context strategy, durable output, and status. |
| PR-4 Validation realism | pass | The two Round 1 material false-pass paths are now fail-closed in the current assertion scripts. |
| PR-5 Source-backed planning | pass | ACs and product locks remain traced to the GUI/distribution specs, local canon, research links, or the explicit default-off decision. |
| PR-6 Handoff/corrections readiness | pass | All indexed raw receipts were read in full and every raw hit location is dispositioned. |
| PR-7 Scope discipline | pass | Service/WinSW, portable behavior, REST/MCP ownership, and Phase 11 work remain excluded by cited canon; MEU-58 remains the registered layout deferral. |
| PR-8 Control reachability/totality | pass | Hub and NSIS controls now bind named observables, reachable scripts, and negative oracles; the remaining IPC/E2E controls retain their Round 1 pass. |
| PR-9 Single-statement discipline | pass | The four repeated composite sets are removed; their scalar owners remain in `named-sets.json`, and named E2E execution is centralized. |

#### Docs / Artifact Review (DR)

| Check | Result | Evidence |
|-------|--------|----------|
| DR-1 Claim-to-state match | pass | The correction log matches the current plan, task, named sets, assertion scripts, canonical specs, and hub. |
| DR-2 Residual old terms | pass | Static `rg` found no `IPC_CHANNELS`, `NSH_TOKENS`, `E2E_TESTIDS`, `E2E_REQUIRED_CASES`, or `AC-60.12` in the plan folder. |
| DR-3 Downstream references | pass | GUI, distribution, BUILD_PLAN hub, and MEU registry references agree on MEU-61 and the MEU-50 boundary. |
| DR-4 Verification robustness | pass | Current hub and NSIS validators reject the concrete Round 1 missing-deliverable cases. |
| DR-5 Evidence auditability | pass | The task-specific index, 19 indexed receipts, static-read receipts, parse receipt, and pre-edit guard remain under `C:/Temp/av-kit/`. |
| DR-6 Cross-reference integrity | pass | Plan/task/named-set names, paths, AC-61.18, and both canonical spec sections align. |
| DR-7 Evidence freshness | pass | Round 2 read current files and the supplied Round 2 census/static-run receipts. |
| DR-8 Completion vs residual risk | pass | The plan remains unstarted and makes no implementation-complete claim. |

### Scope and Commands

Reviewed `implementation-plan.md`, `task.md`, `named-sets.json`, all 11 plan-local `assert-*.ps1` files, the Round 1 review/correction log, every receipt named by the Round 2 census index, `docs/build-plan/06-gui.md` §Startup, `docs/build-plan/07-distribution.md` §Login item uninstall, the `docs/BUILD_PLAN.md` Next sentence, and the corresponding MEU registry bindings.

No product test, Vitest, Playwright, pytest, OpenAPI generator, plan script with uncreated product inputs, product implementation, or plan correction was run. Evidence commands were limited to redirected static reads, `rg`, `Test-Path`, JSON parsing, and PowerShell AST parsing. Key reviewer receipts:

- `C:/Temp/av-kit/plan-review-r2-indexed-receipt-existence.txt`
- `C:/Temp/av-kit/plan-review-r2-removed-literals.txt`
- `C:/Temp/av-kit/plan-review-r2-unstarted-paths.txt`
- `C:/Temp/av-kit/plan-review-r2-started-row-census.txt`
- `C:/Temp/av-kit/plan-review-r2-named-sets-parse.txt`
- `C:/Temp/av-kit/plan-review-r2-script-parse.txt`
- `C:/Temp/av-kit/plan-review-r2-pre-edit-guard.txt`

### Open Questions / Assumptions

None. This recheck used the user-supplied product locks as the contract and introduced no new product behavior.

### Structured Verdict JSON

```json
{
  "schema_version": "review-verdict.v1",
  "date": "2026-09-20",
  "review_mode": "plan",
  "target_plan": "docs/execution/plans/2026-09-20-p6-gui-login-item/implementation-plan.md",
  "agent": "gpt-5.6-sol",
  "dispatch_id": "p6-gui-login-item-plan-r2",
  "requested_verbosity": "standard",
  "verdict": "approved",
  "summary": "Round 2 approved with zero findings. PR-6 passes; both prior High false-pass controls are now fail-closed; both prior Low corrections are present; unchanged product and MEU-50 locks remain aligned.",
  "findings": [],
  "checklist_results": [
    {
      "check": "PR-6 Handoff/corrections readiness",
      "result": "pass",
      "evidence": "Every task-specific indexed receipt exists, was read in full, and has a matching correction-log disposition for every raw file:line location."
    },
    {
      "check": "PCR-1 hub Next correction",
      "result": "pass",
      "evidence": "The current script binds the unique Next prefix, prior plan slashes, PLAN_FOLDER, and MEU-61; task row 8 invokes it."
    },
    {
      "check": "PCR-2 NSIS correction",
      "result": "pass",
      "evidence": "The current script binds two executable HKCU deletions and nsis.include and contains both required negative fixtures."
    },
    {
      "check": "PCR-3 and PCR-4 clerical corrections",
      "result": "pass",
      "evidence": "Removed composite identifiers and AC-60.12 are absent; named E2E and the classifier use AC-61.17."
    }
  ]
}
```

### Verdict

`approved` — Round 2 has zero findings. The PR-6 census gate passes, PCR-1 through PCR-4 are fixed in current file state, and no new evidence-backed High/Critical defect or clerical correction remains.

### Residual Risk

Runtime Electron, Playwright, and NSIS behavior remains intentionally unexecuted in this plan recheck. The unstarted plan assigns those proofs to Red/Green tests, the named AC-61.17 route, the MEU gate, and independent execution review; this review approves plan readiness only and does not start MEU-61.
