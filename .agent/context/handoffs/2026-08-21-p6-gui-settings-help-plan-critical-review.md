---
date: "2026-08-21"
review_mode: "plan"
target_plan: "docs/execution/plans/2026-08-21-p6-gui-settings-help/implementation-plan.md"
verdict: "approved"
findings_count: 0
template_version: "2.1"
requested_verbosity: "standard"
agent: "GPT-5.6-sol (Codex)"
---

# Critical Review: p6-gui-settings-help

> **Review Mode**: `plan`
> **Verdict**: `approved`

---

## Scope

**Target**: `docs/execution/plans/2026-08-21-p6-gui-settings-help/implementation-plan.md` and `docs/execution/plans/2026-08-21-p6-gui-settings-help/task.md`

**Review Type**: Plan review, Session 11, MEU-23 only

**Checklist Applied**: PR-1 through PR-9, with focused checks for control binding, Out of Scope basis, AC source tags, task/plan parity, E2E census reachability, MEU scope, FastAPI/MCP exclusions, and `HUB_NEXT_AFTER`

**Sampled canon and production seams**: `docs/build-plan/06-gui.md` Settings, Help, and Waves 4/6; `docs/build-plan/gui-actions-index.md` settings/help rows; Session 11 grouping; `SettingsChrome.tsx`; main IPC/preload allowlists; `SettingsPutIn`; and the `p6-gui-tts-models` peer plan shape.

### Intent Anchor

Executing this plan is supposed to replace the Settings stub with the complete MEU-23 Settings/Help surface, bind every asserted control to working production behavior, and ship the specified Wave 4/6 tests and action audits without expanding into MEU-24/25, FastAPI-router work, or MCP-tool work. As written, the plan cannot prove or produce all of that objective because setup readiness has a dead-end production chain and the mandatory E2E census can false-pass with ten named controls absent.

---

## Findings

| # | Severity | Confidence | Finding | File:Line | Recommendation | Status |
|---|----------|------------|---------|-----------|----------------|--------|
| 1 | High | High | **PR-8 control reachability/totality fails for setup readiness.** `READINESS_CHECKS` and AC-23.11 require descriptor-present, port, models-directory-writable, and FFmpeg-probe results, but the chain is only described as “IPC/backend readiness + local checks.” Current `get-backend-url` returns readiness derived from `AVKIT_READY`, `/health/dependencies` returns only yt-dlp/FFmpeg data, and the plan adds only the MCP-status IPC. No planned renderer, preload, IPC, or REST producer can observe descriptor-file presence or perform a models-directory writability check. The negative oracle tests secret exposure rather than the adversary condition—missing descriptor or unwritable models directory—so the control can be implemented as static/derived UI and still pass. | `implementation-plan.md:117`, `implementation-plan.md:269`, `implementation-plan.md:316-319`; `ui/src/main/ipc.ts:235-245`; `packages/api/src/avkit_api/schemas/health.py:31-35` | Add a named production chain for every readiness row (for example, Settings page → preload → main-process readiness IPC → descriptor/file-system probe, while retaining dependency GET for FFmpeg), inventory its files/boundary schema, and add negative tests using a missing descriptor and an unwritable/non-directory models path. Keep tokens and raw secret paths out of the renderer. | open |
| 2 | High | High | **PR-4/PR-8 demonstrated E2E validation false-pass.** The plan’s `WAVE4_EXTRA_TESTIDS` contains 14 controls and row 3 makes `E2E_CONTROL_CENSUS` the gate, but `assert-e2e-control-census.ps1` enforces only four of those 14. It omits FFmpeg/cookie/transcript/models browse, pin MCP, both theme controls, readiness, MCP access, and token-present. The script also checks only that some `W4-*` and `W6-*` title exists; it does not require the planned settings seam installation or ledger-backed actuation. Receipt `C:/Temp/av-kit/plan-review-e2e-gap.txt` reproduces `EXPECTED=14`, `ENFORCED=4`, `MISSING=10`. Row 3 can therefore be marked complete while material Wave 4 controls and its fail-closed seam proof are absent. | `implementation-plan.md:139`, `implementation-plan.md:143-151`, `implementation-plan.md:279-280`; `task.md:46`; `assert-e2e-control-census.ps1:34-53` | Make the executable census enforce the complete named Wave 4/6 contract and the production-observable actions promised by W4-3, including the fail-closed settings seam/ledger. Derive from one canonical set where practical so plan and script cannot drift. | open |
| 3 | Medium | High | **The task order does not preserve tests-first evidence for the actual E2E deliverables.** Row 1 creates 22 failing Vitest cases, row 2 implements all production ACs, and only row 3 writes the Playwright Wave 4/6 tests. Surrogate Vitest failures do not provide FAIL_TO_PASS evidence for `settings.test.ts` and `help-search.spec.ts`; this conflicts with the repository’s mandatory FIC TDD sequence (“write ALL tests FIRST”). | `task.md:44-46`; `implementation-plan.md:58-60` | Write and run the Wave 4/6 Playwright specs in the Red package before production work, saving their failing receipt separately; keep the post-Green row for census/build/full E2E verification. | open |
| 4 | Low | High | **PR-7 clerical scope label/basis defect.** “Wave 7 palette-only E2E expansion” is labeled `deferred` without a real deferred-to MEU, although Session 11 positively limits this project to Waves 4/6. The substance is evidenced as outside Session 11, so this is non-blocking under the Materiality Gate, but the current `deferred` row violates the Out of Scope contract. | `implementation-plan.md:342`; `.agent/context/grouping/2026-08-18-build-plan-session-grouping.md:237` | Relabel the row `out-of-scope` and cite Session 11’s Wave 4/6 scope, or name an existing scheduled MEU if it is genuinely deferred. | open |

---

## Checklist Results

### Information Retrieval (IR)

| Check | Result | Evidence |
|-------|--------|----------|
| All AC have source labels | pass with correction | AC-23.1–23.22 have source cells; AC-23.11’s source does not cure the missing producer/negative oracle in Finding 1. |
| Validation cells are exact commands | fail | Commands are explicit, but the E2E census has the demonstrated false-pass in Finding 2. |
| BUILD_PLAN audit row present | pass | Task row 5 binds MEU-23, preserves prior Phase 6 plan slashes, and sets `HUB_NEXT_AFTER=/create-plan p7-distribution`. |
| Post-MEU rows present | pass | Handoff, independent review, reflection, metrics, and closeout rows are present and sequenced. |

### Plan Review (PR)

| Check | Result | Evidence |
|-------|--------|----------|
| PR-1 Plan/task alignment | pass with correction | Same MEU-23 objective and outputs; E2E Red/Green ordering needs Finding 3’s correction. |
| PR-2 Not-started confirmation | pass | All task rows are unchecked, MEU-23 is `pending`, `SettingsChrome` remains a shell, and no correlated MEU-23 implementation handoff exists. Git diff evidence was unavailable because this workspace has no `.git` metadata. |
| PR-3 Task contract completeness | pass | Every executable task row supplies task, owner, deliverable, exact validation, dependency, context strategy, outputs, and status. |
| PR-4 Validation realism | fail | E2E census false-pass demonstrated in Finding 2. |
| PR-5 Source-backed planning | pass with correction | Canon/settings/index/grouping bases are generally explicit; Finding 4 corrects one scope classification. |
| PR-6 Handoff/corrections readiness | pass | One MEU handoff and one rolling implementation-review path are explicit; this is first-pass review, so no corrections census is due. |
| PR-7 Scope discipline | pass with correction | MEU-24/25 are real scheduled MEUs and FastAPI/MCP/chrome exclusions are sourced; Wave 7 row needs the non-blocking relabel in Finding 4. |
| PR-8 Control reachability/totality | fail | Setup-readiness production chain and adversary oracle are missing; E2E control/seam gate is incomplete. |
| PR-9 Single-statement discipline | pass | Reused sets and predicates are named centrally; no materially divergent duplicate contract was found. |

### Focused Scope Checks

| Check | Result | Evidence |
|-------|--------|----------|
| MEU scope | pass | Plan/task list only MEU-23; grouping and registry show MEU-24/25 as later Phase 7 work. |
| No FastAPI/MCP rewrite | pass | Plan and task explicitly prohibit edits to `packages/api/` and `mcp-server/`; Files Modified contains neither. |
| Settings/help action-index parity | pass with execution risk | Settings/help rows 56–63 and 72 are accounted for in ACs; executable E2E coverage remains incomplete per Finding 2. |
| `HUB_NEXT_AFTER` | pass | Named and validated as `/create-plan p7-distribution`, matching Session 11 grouping. |
| Referenced artifact existence | pass | All three plan-local assertion scripts, `tools/check_exec_review.py`, `tools/export_openapi.py`, `tools/meu_status.py`, and `openapi.committed.json` exist. |

---

## Commands Executed

- Full redirected reads of the workflow, review template, implementation plan, task file, named canon, production seams, and peer-plan shape.
- `rtk proxy rg` censuses for Settings/Help/action/grouping/IPC/schema/readiness contracts; receipts under `C:/Temp/av-kit/plan-review-*.txt`.
- Exact referenced-artifact existence census: `C:/Temp/av-kit/plan-review-existence.txt`.
- Wave 4 required-vs-enforced census: `C:/Temp/av-kit/plan-review-e2e-gap.txt` (`14 expected`, `4 enforced`, `10 missing`).
- `rtk git status --short` attempted with redirected receipt; unavailable because `P:/av-kit` is not a Git worktree.

---

## Open Questions / Assumptions

- No human decision is needed to resolve the blockers: the build plan already requires the four readiness outcomes and Wave 4/6 E2E. The correction needs to make those existing requirements reachable and testable, not choose new product behavior.
- Review assumes the intended “descriptor present” check is an actual file/readiness observation, not merely “the backend eventually emitted `AVKIT_READY`”; the spec names these as separate readiness facts.

## Out-of-Contract Observations

None.

## Follow-up Actions

1. Use `/plan-corrections` to add the missing setup-readiness producer and adversary oracle.
2. Correct the E2E census/seam gate so it cannot pass with the ten named Wave 4 controls absent.
3. Move the actual Playwright specs into the Red package and retain post-Green execution as verification.
4. Correct the Wave 7 Out of Scope classification/basis.
5. Re-run `/plan-critical-review` against this same rolling verdict file.

---

## Verdict

`changes_required` — two High findings meet the blocking threshold: AC-23.11 has a production-chain dead end for required readiness observations, and the task’s executable E2E gate demonstrably false-passes with ten controls from its own named contract absent. The MEU boundary, FastAPI/MCP exclusions, AC inventory, task/plan overall parity, referenced scripts, and `/create-plan p7-distribution` hub transition are otherwise correctly represented.

## Residual Risk

Until corrected, execution could ship a readiness card that guesses or hardcodes descriptor/writability state and could close Wave 4/6 with substantial control coverage and fail-closed seam evidence missing. No product, plan, task, or test file was modified during this review.

---

## Corrections Applied (Round 1 → resubmit)

| Finding | Fix | Evidence |
|---------|-----|----------|
| F1 readiness chain | Named SETUP_READINESS IPC + FFMPEG_READINESS from DEPS_GET; AC-23.11 adversary negatives (missing descriptor / non-dir models path) | plan named sets + AC-23.11 + Files Modified |
| F2 E2E census false-pass | ssert-e2e-control-census.ps1 enforces all WAVE4_TESTIDS+WAVE4_EXTRA+WAVE6 + W4-3 installSettingsSeam/__e2eSeamInstalled | census script; E2E_CONTROL_CENSUS named set |
| F3 E2E Red-before-Green | WP-23a/task row 1 author Playwright + E2E_RED fail receipt; Vitest oracle AC-23.1–20; row 3 verifies green | WP-23a–c; task rows 1–3 |
| F4 Wave 7 OOS | Relabeled out-of-scope with Session 11 Wave 4/6 basis | Out of Scope table |

Blast-radius receipt: C:/Temp/av-kit/plan-corrections-blast-r1.txt

---

## Recheck Round 2 (2026-08-21)

**Workflow**: `/plan-critical-review` Round 2

**Agent**: GPT-5.6-sol (Codex)

### Intent Anchor

Executing this plan is supposed to deliver the complete MEU-23 Settings/Help surface with production-bound readiness controls, full Wave 4/6 E2E coverage, tests authored before Green, and scope limited to the sourced Session 11 boundary. Round 2 cannot determine whether the corrected plan would deliver that objective because the mandatory correction blast-radius evidence is not auditable.

### Scope Read

The following targets were re-read in full before applying the procedural gate:

- `docs/execution/plans/2026-08-21-p6-gui-settings-help/implementation-plan.md`
- `docs/execution/plans/2026-08-21-p6-gui-settings-help/task.md`
- `docs/execution/plans/2026-08-21-p6-gui-settings-help/assert-e2e-control-census.ps1`
- `docs/execution/plans/2026-08-21-p6-gui-settings-help/assert-red-oracle.ps1`
- `C:/Temp/av-kit/plan-corrections-blast-r1.txt`

### Pre-Verdict Procedural Gate

`changes_required` — **PR-6 correction blast-radius census is missing the required per-hit audit trail.** The named receipt contains 12 bare `HIT:` labels and one `PASS:` line, but no `file:line` inventory. The correction section at lines 122–133 summarizes F1–F4 and points to the receipt, but it does not mark each receipt hit `updated` or `confirmed-consistent`. An exact disposition census found only the correction heading and receipt pointer; it found no `updated` or `confirmed-consistent` entries.

Per `plan-critical-review.md` PR-6 and the Verdict Rule, this is a pre-verdict gate rather than a severity-rated finding. Substantive corrected-content review must not proceed in this round.

### Prior Finding Status

| Finding | Round-1 status | Round-2 result |
|---------|----------------|----------------|
| F1 SETUP_READINESS / FFMPEG_READINESS production chain + adversary negatives | open | **Not assessed** — PR-6 pre-verdict gate failed |
| F2 E2E census full WAVE4+EXTRA+WAVE6 + W4-3 seam | open | **Not assessed** — PR-6 pre-verdict gate failed |
| F3 E2E authored in Red (`E2E_RED`) before Green | open | **Not assessed** — PR-6 pre-verdict gate failed |
| F4 Wave 7 out-of-scope relabel | open | **Not assessed** — PR-6 pre-verdict gate failed |

F1–F4 are neither confirmed fixed nor reopened on substance; they remain pending a compliant Round-3 resubmission.

### Checklist Results

| Check | Result | Evidence |
|-------|--------|----------|
| PR-6 Handoff/corrections readiness | **fail — procedural gate** | `C:/Temp/av-kit/plan-corrections-blast-r1.txt` lacks `file:line` hits; `C:/Temp/av-kit/round2-disposition-census.txt` contains no per-hit dispositions. |
| PR-1–PR-5, PR-7–PR-9 | not assessed | Workflow requires stopping substantive review when the Round-2 correction census is missing, truncated, or undispositioned. |
| DR-1–DR-8 | not assessed | Same pre-verdict gate. |

### Commands Executed

- Full numbered reads of the four user-named corrected targets; receipts: `C:/Temp/av-kit/round2-implementation-plan-1-220.txt`, `C:/Temp/av-kit/round2-implementation-plan-221-431.txt`, and `C:/Temp/av-kit/round2-task-and-scripts-full.txt`.
- Full read of the rolling verdict and correction receipt: `C:/Temp/av-kit/round2-review-prior-and-contracts.txt`.
- Exact disposition census across the rolling verdict, plan folder, and correction receipt: `C:/Temp/av-kit/round2-disposition-census.txt`.
- Read of `/plan-corrections` Step 5c: `C:/Temp/av-kit/plan-corrections-step5c-full.txt`.

### Follow-up Actions

1. Re-run an untruncated old/new-value and semantic-variant census across both `implementation-plan.md` and `task.md`, preserving `file:line` hits in the receipt.
2. Append a correction-log entry for every receipt hit marked exactly `updated` or `confirmed-consistent`.
3. Resubmit the same rolling file for Round 3; then re-verify F1–F4 substantively.

### Open Questions / Assumptions

None. This result is dictated by the Round-2 PR-6 procedural gate.

### Findings

No severity-rated findings were assessed this round. `findings_count: 0` reflects the current Round-2 structured findings count; the verdict is blocked by the procedural exception.

### Verdict

`changes_required` — the Round-1 correction blast-radius census is undispositioned and lacks the required `file:line` inventory, so Round 2 cannot audit the corrections and must not review their substance.

### Residual Risk

F1–F4 remain unverified. Treating their summary rows as proof would allow correction-introduced drift or missed duplicate statements to pass without an auditable census. No plan, task, script, product, or test file was modified during Round 2.

---

## Recheck Round 3 (2026-08-21)

**Workflow**: `/plan-critical-review` Round 3

**Agent**: GPT-5.6-sol (Codex)

### Intent Anchor

Executing this plan is supposed to deliver the complete MEU-23 Settings/Help surface with production-bound readiness observations, full Wave 4/6 E2E coverage and a fail-closed settings seam, E2E and Vitest evidence authored before Green, and scope limited to Session 11. The corrected plan now supplies a reachable implementation/test chain for that objective and does not retain a delivery-level blocker.

### Scope Read

The following targets were re-read in full:

- `docs/execution/plans/2026-08-21-p6-gui-settings-help/implementation-plan.md`
- `docs/execution/plans/2026-08-21-p6-gui-settings-help/task.md`
- `docs/execution/plans/2026-08-21-p6-gui-settings-help/assert-e2e-control-census.ps1`
- `docs/execution/plans/2026-08-21-p6-gui-settings-help/assert-red-oracle.ps1`
- `C:/Temp/av-kit/plan-corrections-blast-r1.txt`

Current production seams and source canon were sampled for F1/F4 at `docs/build-plan/06-gui.md:1015-1032`, `ui/src/main/ipc.ts:71-96`, `ui/src/main/ipc.ts:122-163`, `ui/src/main/index.ts:272-310`, and `.agent/context/grouping/2026-08-18-build-plan-session-grouping.md:234-237`.

### Findings

No severity-rated findings. No Critical or High findings remain.

### Prior Finding Status

| Finding | Round-3 result | Evidence |
|---------|----------------|----------|
| F1 `SETUP_READINESS` / `FFMPEG_READINESS` + adversary negatives | **closed** | The plan now defines `SetupReadinessCard` → preload `getSetupReadiness` → main `get-setup-readiness`, with descriptor/ready-port/models-write observations, while FFmpeg binds to `DEPS_GET.ffmpeg.available`; missing descriptor and regular-file models-path negatives are explicit (`implementation-plan.md:76`, `implementation-plan.md:120-121`, `implementation-plan.md:257-258`, `implementation-plan.md:276`, `implementation-plan.md:324-327`). |
| F2 full E2E census + W4-3 seam | **closed** | The executable census enumerates all 7 Wave-4 section IDs, 14 Wave-4 extra IDs, and 2 Wave-6 IDs, binds each to an assertion/actuation, and requires W4-3 to contain `installSettingsSeam` plus `__e2eSeamInstalled` outside strings (`assert-e2e-control-census.ps1:19-44`, `assert-e2e-control-census.ps1:60-95`). |
| F3 E2E Red before Green; Vitest 20 ACs | **closed** | WP-23a/task row 1 authors and runs both Playwright specs before WP-23b/task row 2 Green (`implementation-plan.md:58-60`, `implementation-plan.md:81`, `task.md:44-46`). The Red oracle maps exactly AC-23.1–23.20 to 20 distinct failed Vitest assertions; AC-23.21–23.22 remain E2E-owned (`assert-red-oracle.ps1:90-116`). |
| F4 Wave 7 out-of-scope | **closed** | The row is now `out-of-scope`, cites Session 11's Wave 4/6 boundary, and points to the existing palette E2E (`implementation-plan.md:350`; grouping file line 237; `ui/tests/e2e/command-palette-nav.spec.ts` exists). |

### PR-6 Pre-Verdict Gate

**pass** — `C:/Temp/av-kit/plan-corrections-blast-r1.txt` is an untruncated 42-line receipt. It inventories correction hits as `file:line` and assigns every hit `updated` or `confirmed-consistent`; its final line records the pass. The Round-2 procedural exception is cleared.

### Checklist Results

| Check | Result | Evidence |
|-------|--------|----------|
| PR-1 Plan/task alignment | pass | Red → Green → E2E-green order and MEU-23 deliverables agree across WP-23a–e and task rows 1–5. |
| PR-2 Not-started confirmation | pass | All executable task statuses remain `[ ]`; `SettingsPage.tsx` and the MEU-23 implementation handoff do not exist. |
| PR-3 Task contract completeness | pass | Every executable row retains task, owner, deliverable, validation, dependency, context strategy, durable outputs, and status. |
| PR-4 Validation realism | pass | The full E2E control census and exact 20-AC Vitest Red oracle remove the demonstrated false-pass from Round 1. |
| PR-5 Source-backed planning | pass | Corrected readiness, E2E, TDD, and scope rules retain Spec/Local Canon/grouping bases. |
| PR-6 Handoff/corrections readiness | pass | Canonical handoff paths are explicit and the correction census is fully dispositioned. |
| PR-7 Scope discipline | pass | Wave 7 is evidence-backed `out-of-scope`; MEU-24/25, FastAPI, MCP, and chrome exclusions retain real bases. |
| PR-8 Control reachability/totality | pass | Readiness has a named producer chain and adversary negatives; E2E has full locator binding and a W4-3 fail-closed seam gate. |
| PR-9 Single-statement discipline | pass with clerical note | Named sets remain canonical. Two phrases say the full E2E inventory is 21 IDs (`implementation-plan.md:155`, `implementation-plan.md:286`), but the enumerated sets and executable script enforce 23 (7 + 14 + 2). This is inferable count drift and cannot false-pass a missing control. |
| DR-1–DR-8 | not applicable | This is a plan resubmission, not an implementation-handoff claim; correction evidence was audited under PR-6. |

### Approval Notes

- Non-blocking clerical correction: change the two “21-id” references at `implementation-plan.md:155` and `implementation-plan.md:286` to `23-id`. Per the Materiality Gate, this does not enter the structured findings set and does not block approval because the named lists and executable census already enforce every ID.

### Commands Executed

- Full numbered reads of the four corrected plan targets, rolling review, and 42-line PR-6 receipt; receipts under `C:/Temp/av-kit/round3-*.txt`.
- Readiness-source census across build-plan, main IPC/preload/bootstrap, and renderer types: `C:/Temp/av-kit/round3-readiness-seams.txt` and `C:/Temp/av-kit/round3-f1-source.txt`.
- Static F1–F4 substance audit: `C:/Temp/av-kit/round3-substance-audit.txt` (`23` E2E IDs, W4-3 seam tokens, exact `20` Vitest AC IDs, Wave 7 relabel).
- Wave-7 basis/existence audit: `C:/Temp/av-kit/round3-f4-basis.txt`.
- Two preliminary reviewer audit commands failed because of reviewer-authored PowerShell quoting/status-regex mistakes; neither failure reflects a target artifact defect, and both checks were rerun or established by full numbered reads.

### Open Questions / Assumptions

None blocking. During implementation, execution review should confirm the main-process models-directory write probe evaluates the configured `tts.models_directory` (falling back only when unset) and returns booleans without renderer-visible paths.

### Follow-up Actions

1. Optionally correct the two clerical `21-id` references to `23-id` during execution planning hygiene.
2. Proceed under the resolved `reviewer-auto` plan-to-execution gate; this review does not perform or chain execution.

### Verdict

`approved` — PR-6 is satisfied, F1–F4 are closed on substance, and no evidence-backed High/Critical finding remains. The surviving E2E count wording is clerical and non-blocking under the workflow's Materiality Gate.

### Residual Risk

Execution must still prove the new readiness IPC against real descriptor and filesystem adversary cases and prove the Electron E2E suite green (or record a valid environment `[B]`). Those are implementation-verification obligations already represented by the plan, not missing plan work. No plan, task, script, product, or test file was modified during Round 3.
