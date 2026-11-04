---
date: "2026-08-26"
review_mode: plan
target_plan: docs/execution/plans/2026-08-26-p9-capture-engine/implementation-plan.md
verdict: approved
findings_count: 0
round: 5
template_version: "2.1"
requested_verbosity: standard
agent: gpt-5.6-sol
---

# Critical Review: p9-capture-engine

> **Review Mode**: `plan`
> **Verdict**: `changes_required`

---

## Intent Anchor

Executing this plan is supposed to deliver Session 16's capture engine only: MEU-34 domain contracts, MEU-35 SQLite plus mss/Pillow infrastructure, and MEU-36 `CaptureService`, while leaving REST, MCP, GUI, and Session 8c untouched. The scope and sequencing locks are correct, but the current AC and task controls can still pass without two explicit annotation behaviors, required quality gates, independently produced review evidence, and the complete closeout bundle, so execution would not reliably deliver the full objective.

## Scope

**Primary targets**:

- `docs/execution/plans/2026-08-26-p9-capture-engine/implementation-plan.md`
- `docs/execution/plans/2026-08-26-p9-capture-engine/task.md`
- `docs/execution/plans/2026-08-26-p9-capture-engine/named-sets.json`
- `docs/execution/plans/2026-08-26-p9-capture-engine/assert-red-oracle.ps1`
- `docs/execution/plans/2026-08-26-p9-capture-engine/assert-api-tree-hash.ps1`
- `docs/execution/plans/2026-08-26-p9-capture-engine/assert-openapi-skip.ps1`
- `docs/execution/plans/2026-08-26-p9-capture-engine/assert-handoff-markers.ps1`
- `docs/execution/plans/2026-08-26-p9-capture-engine/assert-handoff-acs.ps1`

**Authority and canon sampled**:

- `docs/build-plan/09-screenshot-capture.md`
- `.agent/context/grouping/2026-08-26-p9-screenshot-capture-session-grouping.md`
- `.agent/context/meu-status.yaml`
- `.agent/context/harness.local.md`
- `ConversionJob` / `conversion_jobs` / `ConversionService`
- `SETTING_NAMESPACES` / `SETTINGS_KEY_TABLE` / `QUEUE_NAMES`
- `UnitOfWork` / `SqlAlchemyUnitOfWork` / both `FakeUnitOfWork` implementations
- `tests/integration/test_sqlite_uow.py` owners `TABLES`, `UOW_ATTRIBUTES`, and `INFRA_LAYOUT`

**Review type**: unstarted execution-plan review. **Sweeps applied**: 1-9. **Checklist applied**: PR-1 through PR-9 and DR-1 through DR-8.

No pytest, pyright, ruff, migration, repository tool, plan assertion script, or product code was executed. Evidence collection was limited to static reads, `rg`, and `Test-Path`.

---

## Findings

| # | Severity | Finding | File:Line | Recommendation | Status |
|---|----------|---------|-----------|----------------|--------|
| 1 | High | **PR-5 / PR-8 — The annotation FIC omits two explicit Spec behaviors, so all named ACs can pass while the implementation accepts invalid highlight opacity and never clamps annotation coordinates to the image.** The Spec requires highlight `opacity` in `0–1` and requires integer coordinates to be clamped to `[0,width]` / `[0,height]`. AC-34.7 validates type/color/text/negative rect size only; AC-36.9 validates sidecar/bake/empty-list behavior only; the named-set owner defines no opacity bounds. A service that accepts `opacity=2` and persists/bakes out-of-bounds coordinates therefore satisfies the current 39-AC Red/Green contract. | `docs/build-plan/09-screenshot-capture.md:269`, `docs/build-plan/09-screenshot-capture.md:274`; `implementation-plan.md:164`, `implementation-plan.md:302`; `named-sets.json` | Add single-owner opacity bounds and an explicit clamp contract, then bind them to negative assertions in AC-34.7 / AC-36.9 (or new source-backed ACs) and keep Red counts/oracles synchronized. | open |
| 2 | High | **PR-1 / PR-4 / PR-8 — The executable MEU and completion gates can pass with prohibited placeholders and unchecked type errors.** Row 3 says it runs anti-placeholder but its command never does. Rows 6 and 9 run pytest + ruff but no pyright or anti-placeholder. The plan prose lists a touched-package pyright/ruff check and an anti-placeholder scan, but no task row schedules those commands; H1-2 is pytest-only and H2-4 is closeout-only. A `TODO`/`NotImplementedError` in any new capture file, or a pyright failure in the MEU-35 adapter/database work or MEU-36 service, can therefore survive every named task validation. This violates the registered MEU-gate and no-deferral contracts. | `implementation-plan.md:389-405`; `task.md:46`, `task.md:49`, `task.md:52`, `task.md:57`, `task.md:69` | Make rows 3/6/9 run the registered scoped gate or exact equivalent test + pyright + ruff + anti-placeholder checks for each touched slice, and schedule a final touched-package quality recheck before review dispatch. | open |
| 3 | High | **PR-8 — H1-7's approval validator is not bound to an external reviewer dispatch and can false-pass a self-authored `approved` file.** The task asserts `Invoke-CodexDispatch.ps1` and the hard gate forbids implementer self-review, but the validation command only invokes `check_exec_review.py`. That tool checks `review_mode`, `target_plan`, `verdict`, `findings_count`, and round; it does not inspect `agent`, a dispatch ID, or terminal dispatch receipts. A locally authored frontmatter block with those five values passes without GPT-5.6-sol ever running. | `task.md:64`, `task.md:85`; `tools/check_exec_review.py:99-130` | Bind H1-7 to a successful `Invoke-CodexDispatch.ps1` receipt set and the resulting review artifact (including the expected reviewer identity/dispatch correlation), then run the existing frontmatter validator as the schema check. | open |
| 4 | High | **PR-4 / PR-8 — H2-4 claims to re-run the full closeout but omits three material checks, so the named completion-preflight receipt can pass with missing closeout evidence.** Its command runs handoff markers, execution-review frontmatter, and registry drift only. It does not run `assert-handoff-acs.ps1`, the reflection structural check, or the metrics-row check named in the task text. Removing an AC set from a handoff, deleting the reflection, or deleting the metrics row after their earlier rows leaves H2-4 green even though the Definition of Done requires those artifacts. | `task.md:62`, `task.md:67-69` | Add the AC-set, reflection-structure, and metrics checks to H2-4 and propagate each exit code immediately so the final receipt proves exactly what its task text claims. | open |
| 5 | Low | **PR-4 — The planned shell commands do not follow the active P0 RTK routing rule.** The task points to the output-evidence policy, but validation rows and the plan's verification examples invoke raw `pwsh`, `uv`, and `rg`. Redirects are present, so this is not a delivery-level false-pass and does not independently block approval, but the higher-priority repository instruction says every shell segment must use a verified native RTK command or `rtk proxy`. | `task.md:28`, `task.md:44-70`; `implementation-plan.md:364-405` | During `/plan-corrections`, normalize executable command segments to the active P0 RTK route while preserving exact receipts and immediate exit capture. | open |

No Critical findings were identified.

---

## Checklist Results

| Check | Result | Evidence |
|-------|--------|----------|
| PR-1 Plan/task alignment | fail | Scope/order align, but the plan's type/lint and anti-placeholder verification at `implementation-plan.md:389-405` is not scheduled in `task.md`; Finding 2. |
| PR-2 Not-started confirmation | pass | Every actionable task row is `[ ]`; `capture.py`, the capture port/adapter/service, all three new tests, all MEU-34–36 handoffs, the implementation review, and the reflection are absent. |
| PR-3 Task contract completeness | pass | Every actionable row supplies task, owner, deliverable, exact validation, dependency/context, durable output, builder-model, and status fields. |
| PR-4 Validation realism | fail | Findings 2 and 4 demonstrate quality and closeout false-passes; Finding 5 is a non-blocking routing correction. |
| PR-5 Source-backed planning | fail | Scope and most ACs are source-backed, but Finding 1 omits two explicit annotation rules from the Spec-backed FIC. |
| PR-6 Handoff/corrections readiness | pass | Three canonical MEU handoffs and one rolling implementation-review file are explicit; all handoff assertion scripts exist. Round-2+ census rules do not apply to Round 1. |
| PR-7 Scope discipline (C2) | pass | MEU-37/38/39 deferrals resolve to scheduled registry/grouping IDs; every `out-of-scope` row cites Spec, grouping, BUILD_PLAN canon, or Human-approved separation. No MEU-27 work is disguised as Session 16 work. |
| PR-8 Control reachability/totality | fail | Findings 1-4 identify concrete missing observables or named validations that false-pass materially missing behavior/evidence. The mss, queue exclusion, settings staging, OpenAPI hash, handoff-file existence, and Red-oracle controls are otherwise statically reachable and fail closed. |
| PR-9 Single-statement discipline | pass | Executable member sets, thresholds, paths, handoff names/counts, Red counts, and hub-next value are owned by `named-sets.json`. The literal census found no conflicting live spelling across multiple AC/task rows. |

### Docs Review Checks

| Check | Result | Evidence |
|-------|--------|----------|
| DR-1 Claim-to-state match | pass | Plan/task remain `draft`; no implementation or handoff completion is claimed. |
| DR-2 Residual old terms | pass | No residual Session 8c / MEU-27 or MEU-37–39 implementation row appears in Session 16. |
| DR-3 Downstream references | pass | All cited authority, grouping, schema, template, metrics, and existing-tool paths resolve; planned-new paths are inventoried as new deliverables. |
| DR-4 Verification robustness | fail | Findings 1-4. |
| DR-5 Evidence auditability | fail | Commands are concrete, but Findings 2-4 show named receipts do not prove their full claimed contract. |
| DR-6 Cross-reference integrity | pass | Scope, dependency order, settings ownership, queue exclusion, and API deferral agree across plan, task, grouping, registry, and local canon. |
| DR-7 Evidence freshness | pass | Current static file state was reproduced in Round 1; no runtime result counts were accepted. |
| DR-8 Completion vs residual risk | pass | The artifacts remain draft/unstarted and make no implementation-complete claim. |

### Required Scope Locks

| Lock | Result | Evidence |
|------|--------|----------|
| Session 16 only: MEU-34 → 35 → 36; MEU-37–39 scheduled; no MEU-27 | pass | `implementation-plan.md:5`, `implementation-plan.md:21`, `implementation-plan.md:60-69`, `implementation-plan.md:344-349`; grouping Sessions 16-18; registry MEU-34–39. |
| Never add `captures` to `QUEUE_NAMES` | pass | `implementation-plan.md:80`, `implementation-plan.md:159`, `implementation-plan.md:350`; current `queue.py:10` remains downloads/transcripts/conversions. |
| mss backend; BBox virtual desktop; `monitors[0]`; fake mss; no live-desktop ship gate | pass | Spec `:293`, `:333-340`, `:512`; `implementation-plan.md:122`, `implementation-plan.md:228`, `implementation-plan.md:245`, `implementation-plan.md:354`. |
| `SETTING_NAMESPACES` in MEU-34; `SETTINGS_KEY_TABLE` keys in MEU-36; REST in MEU-37 | pass | `implementation-plan.md:93`, `implementation-plan.md:133`, `implementation-plan.md:160`, `implementation-plan.md:305`, `implementation-plan.md:344`; current domain/service settings owners confirmed. |
| `fresh_worker: none` → `compact_continue`; no isolated rows | pass | `implementation-plan.md:56-69`; `task.md:32`, task context column. |
| create-plan §4A skipped because no GUI | pass | `implementation-plan.md:136`; `task.md:36`; `create-plan.md:245-267`. |
| OpenAPI skip uses API-tree SHA256 baseline, not git | pass | `implementation-plan.md:113`, `implementation-plan.md:394-395`; `task.md:44`, `task.md:59`; both hash scripts inspect `packages/api` and fail on missing baseline/drift. |

### Referenced-Artifact Existence

- All five plan assertion scripts, `named-sets.json`, the cited templates/schema, `tools/meu_status.py`, `tools/check_exec_review.py`, and `tools/Invoke-CodexDispatch.ps1` exist.
- `tools/validate_closeout_artifacts.py` is absent exactly as `task.md:34` states; the plan deliberately substitutes named checks.
- All missing product/test/handoff/reflection paths are explicitly inventoried as future deliverables, confirming unstarted state rather than a missing executable dependency.

---

## Commands Executed

Static evidence only, with canonical receipts under `C:/Temp/av-kit/`:

- Full and line-numbered reads of the eight review targets: `p9-implementation-plan.txt`, `p9-task.txt`, `p9-plan-numbered.txt`, `p9-task-numbered.txt`, `p9-support-a.txt`, `p9-support-b.txt`.
- Authority/canon reads and censuses: `p9-spec-numbered.txt`, `p9-grouping.txt`, `p9-meu-status.txt`, `p9-local-canon-search.txt`, `p9-local-canon-targeted.txt`.
- Sweep receipts: `p9-unstarted-test-path.txt`, `p9-task-status-census.txt`, `p9-sweep8-paths.txt`, `p9-sweep8-existence.txt`, `p9-sweep9-literals.txt`, `p9-annotation-contract-census.txt`, `p9-review-provenance-census.txt`.
- Workflow/template/exemplar evidence: `plan-review-workflow.txt`, `plan-review-template.txt`, `p9-review-peer.txt`, `p9-create-plan-4a.txt`.
- Canonical target guard: `p9-plan-review-pre-edit-guard.txt`.

No project test suite, type checker, linter, migration, generator, repository tool, plan helper script, or product command was executed.

---

## Open Questions / Assumptions

- No human product decision is required for these corrections. Findings 1-4 are resolved by the existing Spec and governance contracts.
- The mss `monitors[0]` choice is treated as locked by the supplied review instruction plus Spec's virtual-desktop coordinate contract; no alternative Pillow `ImageGrab` behavior is requested.
- The active `AGENTS.md` P0 RTK mandate is treated as higher priority than the local output-policy sentence that calls RTK optional; Finding 5 records the conflict rather than silently choosing the lower-priority wording.

## Required Follow-up

Route Findings 1-5 through `/plan-corrections`, keep all edits inside the existing plan folder/review loop, produce the required untruncated blast-radius census with per-hit dispositions, and submit the corrected plan for independent Round 2 review. Do not begin implementation under this verdict.

## Verdict

`changes_required` — four High findings demonstrate that the current named validations can pass while explicit annotation invariants are missing, required MEU quality gates are incomplete, the independent-review hard gate has no dispatch provenance, and the final closeout bundle is incomplete. The Session 16 scope, MEU order, mss/fake-desktop lock, queue exclusion, settings staging, `fresh_worker` handling, GUI skip, OpenAPI hash skip, and unstarted-state checks all pass.

## Residual Risk

This is a static plan review, not execution evidence. After correction and approval, the planned fake-mss tests, SQLite/UoW integration, Pillow bake proofs, service behavior, and closeout controls still require actual execution receipts; no runtime behavior was tested in this review.

---

## Corrections Applied — 2026-08-26 (create-plan Step 5b / plan-corrections)

**Corrector:** coordinator (not the reviewer). Verdict set to `corrections_applied` only. Independent Round 2 must re-score. Product code, tests, and `docs/build-plan/` were not modified.

**Instruction conflict (flagged, not silently picked):** `plan-corrections.md` HARD STOP says timestamp-and-stop and do not auto-chain into `/plan-critical-review`. Driving workflow is `/create-plan` Step 5b (`plan_to_exec_gate: reviewer-auto` in `.agent/context/harness.local.md`), which requires re-dispatch after the census. Re-dispatch proceeds under create-plan.

**Second conflict:** `plan-corrections.md` Write Scope lists only `implementation-plan.md` and `task.md` under `docs/execution/plans/*/`. `named-sets.json` and plan-folder `assert-*.ps1` are create-plan Step 4 artifacts (single-statement / executable owners). They were updated as plan artifacts, not as production code.

**Third conflict:** `AGENTS.md` P0 and `TASK-TEMPLATE.md` require `rtk proxy`; `.agent/docs/output-evidence-policy.md` calls RTK optional. Finding 5 + P0 win: this session prefixes executable segments with `rtk proxy`. Missing `rtk` at execution is `[B]`.

### Finding dispositions (corrector claims; not an `approved` verdict)

| # | Change | Files |
|---|--------|-------|
| 1 | Added `HIGHLIGHT_OPACITY_MIN/MAX` and `ANNOTATION_CLAMP_MIN`. New Spec-backed AC-34.13 (opacity inclusive bounds) and AC-36.14 (service clamps before bake). `RED_COUNT_34`=13, `RED_COUNT_36`=14. Domain may hold out-of-bounds ints; bake must not receive them. | named-sets.json; implementation-plan.md; task.md rows 1–2, 7–8 |
| 2 | Added `assert-meu-scoped-gate.ps1` + `assert-anti-placeholder.ps1`. Rows 3/6/9 and H1-2 run pytest + pyright + ruff + anti-placeholder/G36 from `GATE_*` / `PLACEHOLDER_PATHS_*` / `G36_TEST_PATHS_*`. Verification Plan §4/§6/§7 no longer orphaned. | named-sets.json; assert-meu-scoped-gate.ps1; assert-anti-placeholder.ps1; task.md; implementation-plan.md |
| 3 | Added `assert-exec-review-dispatch.ps1`: require a successful `Invoke-CodexDispatch` `status.json` (`DISPATCH_STATUS_SCHEMA`, `exit_code=0`, `model=REVIEWER_AGENT`) whose `prompt_temp.txt` names `EXEC_REVIEW_FILE`, plus frontmatter `agent`. Then `check_exec_review.py` as schema. Bound on H1-7 and H2-4. Residual: a forged dispatch folder can still be planted; cryptographic wrapper binding is out of scope. | named-sets.json; assert-exec-review-dispatch.ps1; task.md H1-7/H2-4 |
| 4 | H2-4 now runs handoff markers + `assert-handoff-acs.ps1` + dispatch provenance + reflection markers via `REFLECTION_FILE` + metrics via `METRICS_SLUG` + `check_exec_review.py` + `render --check`. | task.md H2-4; named-sets.json |
| 5 | Prefixed executable validation segments with `rtk proxy`. Recorded the P0 vs optional-policy conflict in Open Questions. | task.md; implementation-plan.md verification |

### Blast-radius census (Step 5c / PR-6)

Index: `C:/Temp/av-kit/census-p9-summary.txt`. Existence: `C:/Temp/av-kit/census-p9-helper-existence.txt`. Per-value receipts: `C:/Temp/av-kit/census-p9-*.txt`.

Queries: 16. `rg -F -n` over `implementation-plan.md`, `task.md`, `named-sets.json`. Old-value zero-hit (updated-gone): `RED_COUNT_34": 12`, `RED_COUNT_36": 13`, `AC-34.1–34.12`, `AC-36.1–36.13`, `rg -n "TODO`. New-value hits dispositioned below.

Blast-radius census: 16 values/variants swept, old-range literals gone, new owners present. Summary: K=8 changed owners (`RED_COUNT_34/36`, opacity, clamp, gate helpers, dispatch provenance, RTK prefix, closeout), V=16, N≈70 hits across receipts, M=all updated or confirmed-consistent, 0 stale old-range leftovers.

| Receipt | File:Line | Disposition |
|---|---|---|
| census-p9-red-count-34-old.txt | (no hit) | updated-gone |
| census-p9-red-count-34-new.txt | named-sets.json:3 | updated (owner) |
| census-p9-red-count-36-old.txt | (no hit) | updated-gone |
| census-p9-red-count-36-new.txt | named-sets.json:7 | updated (owner) |
| census-p9-ac-range-34-old.txt | (no hit) | updated-gone |
| census-p9-ac-range-36-old.txt | (no hit) | updated-gone |
| census-p9-highlight-opacity.txt | named-sets.json:41-42 | updated (owner) |
| census-p9-highlight-opacity.txt | task.md:45; implementation-plan.md:97,139,157,178,185 | updated (cite owner) |
| census-p9-annotation-clamp.txt | named-sets.json:43 | updated (owner) |
| census-p9-annotation-clamp.txt | task.md:51; implementation-plan.md:98,140,297,318,325 | updated (cite owner) |
| census-p9-ac-34-13.txt | implementation-plan.md:178,201 | updated (new AC + control binding) |
| census-p9-ac-36-14.txt | implementation-plan.md:318,340 | updated (new AC + control binding) |
| census-p9-scoped-gate.txt | task.md:46,49,52,57; implementation-plan.md:62,65,68,120,404,407 | updated |
| census-p9-dispatch-assert.txt | task.md:34,64,69; implementation-plan.md:120,418 | updated |
| census-p9-anti-placeholder-assert.txt | implementation-plan.md:120,404 | updated |
| census-p9-rtk-proxy.txt | 31 hits in plan+task+gate script | updated |
| census-p9-bare-rg-todo.txt | (no hit) | updated-gone |
| census-p9-reviewer-agent.txt | named-sets.json:98; task.md:64,85; implementation-plan.md:116 | updated |
| census-p9-helper-existence.txt | three new assert scripts | updated (Test-Path EXISTS) |

Confirmed-consistent (not stale): `AC-34.12` and `AC-36.13` remain as live AC IDs (not range ends). `opacity=2` is the AC-34.13 negative oracle, not a restated bound. G29 lock still names AC-36.13 for tmp-SQLite smoke (AC-36.14 is clamp). `check_exec_review.py --review-file` argv copies `EXEC_REVIEW_FILE` (same string as named-sets).

---

## Round 2 — 2026-08-26

**Workflow:** `/plan-critical-review` Round 2  
**Agent:** `gpt-5.6-sol`  
**Review mode:** `plan`  
**Execution performed:** none

### Intent Anchor

Executing this plan is supposed to deliver Session 16's capture engine only: MEU-34 domain contracts, MEU-35 SQLite plus fake-mss/Pillow infrastructure, and MEU-36 `CaptureService`, while leaving REST, MCP, GUI, Session 8c, and processor queues untouched. The corrected plan now carries the missing opacity/clamp contracts and most requested quality/closeout wiring, but two controls still allow materially incomplete or self-reviewed work to satisfy the named completion path, so executing it would not yet reliably deliver the governed objective.

### Scope

**Targets re-read from current disk state:**

- `docs/execution/plans/2026-08-26-p9-capture-engine/implementation-plan.md`
- `docs/execution/plans/2026-08-26-p9-capture-engine/task.md`
- `docs/execution/plans/2026-08-26-p9-capture-engine/named-sets.json`
- `docs/execution/plans/2026-08-26-p9-capture-engine/assert-red-oracle.ps1`
- `docs/execution/plans/2026-08-26-p9-capture-engine/assert-api-tree-hash.ps1`
- `docs/execution/plans/2026-08-26-p9-capture-engine/assert-openapi-skip.ps1`
- `docs/execution/plans/2026-08-26-p9-capture-engine/assert-handoff-markers.ps1`
- `docs/execution/plans/2026-08-26-p9-capture-engine/assert-handoff-acs.ps1`
- `docs/execution/plans/2026-08-26-p9-capture-engine/assert-anti-placeholder.ps1`
- `docs/execution/plans/2026-08-26-p9-capture-engine/assert-meu-scoped-gate.ps1`
- `docs/execution/plans/2026-08-26-p9-capture-engine/assert-exec-review-dispatch.ps1`

**Authority and control surfaces re-read:** `docs/build-plan/09-screenshot-capture.md`, Session 16 grouping, MEU-34–36 registry records, `.agent/context/harness.local.md`, live queue/settings owners, `tools/Invoke-CodexDispatch.ps1`, `tools/check_exec_review.py`, the Round 1 correction log, `C:/Temp/av-kit/census-p9-summary.txt`, and every `C:/Temp/av-kit/census-p9-*.txt` receipt.

Static evidence only. No pytest, pyright, ruff, migration, repository Python tool, plan assertion script, or product command was executed.

### Findings

| # | Severity | Confidence | Finding | File:Line | Recommendation | Status |
|---|----------|------------|---------|-----------|----------------|--------|
| R2-F1 | High | High | **PR-4 / PR-8 — Round 1 Finding 2 remains materially open because the new anti-placeholder/G36 owner scans only the three new capture modules/tests, not the full set of files the plan requires execution to modify.** The plan adds capture behavior to existing domain enums/settings/errors, database/UoW/storage files, service settings, and four existing test files. Those files are absent from `PLACEHOLDER_PATHS_*` / `G36_TEST_PATHS_*`. A `NotImplementedError` in an omitted modified production file or `pytest.mark.skip`/`xfail` neutralization in `test_domain.py`, `test_sqlite_uow.py`, `test_services.py`, or `test_conversion_service.py` can therefore survive rows 3/6/9 and H1-2 while the helper prints `PASS: ANTI_PLACEHOLDER`. This is the concrete no-deferral/G36 false-pass the scoped gate is required to prevent. | `named-sets.json:104-116`; `implementation-plan.md:209-215`, `implementation-plan.md:277-287`, `implementation-plan.md:349`; `assert-anti-placeholder.ps1:52-71`; `task.md:46`, `task.md:49`, `task.md:52`, `task.md:57` | Make the named placeholder and G36 sets cover every product/test file this plan modifies, or use an equivalent complete touched-file owner, then keep rows 3/6/9/H1-2 bound to it. | open |
| R2-F2 | High | High | **PR-8 — Round 1 Finding 3 remains open because dispatch success is not correlated to the current `approved` review contents.** `assert-exec-review-dispatch.ps1` accepts any recursive `status.json` whose sibling prompt merely names `EXEC_REVIEW_FILE` and whose wrapper exit/model/schema match; it does not bind the status to the review file's bytes, verdict, round, output artifact, or freshness. A legitimate reviewer dispatch that returned `changes_required` still exits successfully and leaves a reusable matching receipt. The implementer can then replace the rolling file's frontmatter with self-authored `agent: gpt-5.6-sol`, `verdict: approved`, `findings_count: 0`; the provenance helper accepts the older dispatch and `check_exec_review.py` accepts the live frontmatter. H1-7 and H2-4 therefore still false-pass the independent-review hard gate. | `assert-exec-review-dispatch.ps1:32-55`; `tools/Invoke-CodexDispatch.ps1:874-905`; `tools/check_exec_review.py:113-130`; `task.md:64`, `task.md:69` | Bind the accepted dispatch to the actual reviewer-produced artifact/current round, such as a wrapper-recorded output/review hash or another immutable dispatch-to-verdict correlation, before running the existing schema/frontmatter check. | open |
| R2-F3 | Low | High | **PR-4 — The scoped-gate helper has a one-token parameter-name typo.** `Get-NamedStringArray` declares `$Name`, but all three calls pass `-Key`, so PowerShell cannot bind the parameter and rows 3/6/9/H1-2 are not runnable as written. This is clerical under the workflow Materiality Gate because the intended correction is unambiguous; it does not independently drive the verdict. | `assert-meu-scoped-gate.ps1:18-25`, `assert-meu-scoped-gate.ps1:41-43` | Change the three calls to `-Name` or rename the function parameter to `$Key`. | open |
| R2-F4 | Low | High | **PR-9 — The reflection structural predicate is restated in two live task commands instead of being single-owned.** H2-2 and H2-4 each hard-code the same marker array while `named-sets.json` owns only `REFLECTION_FILE`; current spellings agree, so this is a clerical stale-clause risk and not a blocker. | `task.md:67`, `task.md:69`; `named-sets.json:102-103` | Single-own the reflection marker set and consume it in both rows. | open |

No Critical or Medium findings were identified.

### Prior Pass Summary

| Round 1 finding | Prior status | Round 2 result |
|---|---|---|
| F1 — opacity bounds and annotation clamp omitted | open | ✅ Fixed — AC-34.13 and AC-36.14 are source-backed and negatively bound; named values are present; Red counts are 13 and 14. |
| F2 — MEU quality/anti-placeholder gates missing | open | ❌ Partially fixed — rows 3/6/9/H1-2 invoke the new scoped gate, but R2-F1 leaves its no-deferral/G36 coverage materially incomplete; R2-F3 is a clerical invocation defect inside the helper. |
| F3 — independent review not bound to dispatch provenance | open | ❌ Still open — a prior successful `changes_required` dispatch can be reused to validate a self-authored live `approved` file (R2-F2). |
| F4 — H2-4 omitted AC/reflection/metrics checks | open | ✅ Fixed at delivery level — H2-4 now runs handoff markers, handoff ACs, dispatch/frontmatter checks, reflection/metrics checks, and registry drift. R2-F4 is only a Low single-owner note. |
| F5 — executable segments lacked RTK routing | open | ✅ Fixed — executable validation segments use `rtk proxy`; no residual bare old `rg -n "TODO` form remains. |

### Confirmed Corrections and Locks

- AC-34.13 implements the Spec line 269 inclusive highlight-opacity contract through `HIGHLIGHT_OPACITY_MIN/MAX`; AC-36.14 implements the Spec line 274 pre-bake coordinate clamp through `ANNOTATION_CLAMP_MIN` (`implementation-plan.md:178`, `implementation-plan.md:318`; `named-sets.json:41-43`).
- `RED_COUNT_34=13` and `RED_COUNT_36=14`; the Red oracle consumes those owners (`named-sets.json:3`, `named-sets.json:7`; `assert-red-oracle.ps1`).
- Rows 3/6/9 and H1-2 all invoke `assert-meu-scoped-gate.ps1` (`task.md:46`, `task.md:49`, `task.md:52`, `task.md:57`).
- H1-7 and H2-4 invoke `assert-exec-review-dispatch.ps1` before `check_exec_review.py` (`task.md:64`, `task.md:69`), although R2-F2 shows the remaining material correlation gap.
- H2-4 invokes `assert-handoff-acs.ps1` and checks the named reflection path plus metrics slug (`task.md:69`; `named-sets.json:102-103`).
- The PR-6 correction log names the summary and per-query receipts, every hit/no-hit row has a disposition, and the raw census files are present and untruncated. The live zero-hit sweep confirms no stale `AC-34.1–34.12`, `AC-36.1–36.13`, `RED_COUNT_34: 12`, or `RED_COUNT_36: 13` range/count literal remains.
- Session 16 remains MEU-34 → MEU-35 → MEU-36 only; MEU-37–39 and Session 8c remain excluded. `QUEUE_NAMES` remains downloads/transcripts/conversions only. The plan retains mss `monitors[0]` with fake mss, MEU-34 `SETTING_NS`, MEU-36 `CAPTURE_KEYS`, `compact_continue`, the §4A GUI skip, and the API-tree-hash OpenAPI skip.
- The plan is still unstarted: every actionable task row is `[ ]`; MEU-34–36 remain `pending` with `execution_plan: null`; the domain capture module/port, infrastructure capture adapter, `CaptureService`, three new capture tests, three MEU handoffs, implementation review, and reflection are absent.

### Checklist Results

| Check | Result | Evidence |
|---|---|---|
| PR-1 Plan/task alignment | pass | Both retain Session 16 MEU-34 Red/Green/gate → MEU-35 → MEU-36 → H1 review → H2 closeout. |
| PR-2 Not-started confirmation | pass | All task rows are `[ ]`; live registry status is `pending`; planned implementation/handoff/review/reflection artifacts are absent. |
| PR-3 Task contract completeness | pass | Every actionable row retains task, owner, deliverable, exact validation, dependency, context strategy, durable output, builder model, and status. |
| PR-4 Validation realism | fail | R2-F1 is a material no-deferral/G36 false-pass. R2-F3 is a non-blocking clerical helper typo. |
| PR-5 Source-backed planning | pass | AC-34.13 and AC-36.14 now trace to Spec 269/274; all other required behaviors retain allowed source labels. |
| PR-6 Handoff/corrections readiness | pass | Summary plus all `census-p9-*.txt` receipts exist; the rolling correction log dispositions every hit/no-hit site; live old-range sweep is zero-hit. |
| PR-7 Scope discipline (C2) | pass | MEU-37–39 deferrals remain scheduled in grouping/registry; out-of-scope rows retain Spec/grouping/Local Canon bases. |
| PR-8 Control reachability/totality | fail | R2-F1 leaves the quality observable incomplete; R2-F2 leaves reviewer provenance unbound to the approved artifact. |
| PR-9 Single-statement discipline | partial (Low) | Changed AC counts/ranges are single-owned and stale old ranges are gone; reflection markers remain duplicated (R2-F4). |

### Docs Review Results

| Check | Result | Evidence |
|---|---|---|
| DR-1 Claim-to-state match | partial | Most correction claims match live files; the quality/provenance claims overstate the controls identified in R2-F1/R2-F2. |
| DR-2 Residual old terms | pass | Live old-count/range sweep is empty; AC-34.12 and AC-36.13 remain only as valid individual AC IDs. |
| DR-3 Downstream references updated | pass | New AC IDs/counts/helpers are referenced consistently in plan, task, named sets, and correction census. |
| DR-4 Verification robustness | fail | R2-F1 and R2-F2 demonstrate concrete false-passes. |
| DR-5 Evidence auditability | pass | Static commands and PR-6 receipts are reproducible; no runtime claim was accepted. |
| DR-6 Cross-reference integrity | pass | Session, mss/fake, queue, settings staging, compact, GUI-skip, and OpenAPI locks remain aligned. |
| DR-7 Evidence freshness | pass | All targets and census files were re-read from live disk for Round 2. |
| DR-8 Completion vs residual risk | pass | Plan remains draft/unstarted and makes no implementation-complete claim. |

### Commands and Receipts

Only redirected static reads, `rg`, and `Test-Path` were used. Key Round 2 receipts under `C:/Temp/av-kit/`:

- `round2-workflow-policy.txt`, `round2-template-prior.txt`, `round2-peer-exemplar.txt`
- `round2-plan-head.txt`, `round2-plan-tail.txt`, `round2-task-namedsets.txt`
- `round2-helpers-existing.txt`, `round2-helpers-new.txt`, `round2-helper-semantics.txt`
- `round2-census-all.txt`, `round2-census-files.txt`, `round2-census-large-split.txt`
- `round2-authority-locks.txt`, `round2-meu-status-blocks.txt`, `round2-scope-locks-live.txt`
- `round2-unstarted-paths.txt`, `round2-task-statuses.txt`, `round2-stale-range-census.txt`
- `round2-artifact-existence.txt`, `round2-support-existence.txt`, `round2-pre-edit-guard.txt`

### Open Questions / Assumptions

- No human product decision is required. Both blocking findings concern enforcement of already-stated governance contracts.
- The dispatch finding treats wrapper exit code 0 as successful process completion, not reviewer approval; `status.json` records no binding from that success to the current rolling review bytes or verdict.
- The one-token scoped-helper mismatch is deliberately Low under the workflow's Materiality Gate and does not contribute to `changes_required`.

### Verdict

`changes_required` — R2-F1 and R2-F2 are evidence-backed High findings. The corrected plan can still pass prohibited placeholders/test neutralization in omitted touched files, and it can reuse a successful non-approval dispatch receipt to validate a self-authored `approved` review artifact. Route only these findings and the two Low corrections through `/plan-corrections`; do not begin execution on this Round 2 verdict.

### Residual Risk

This was a static plan review. After correction and approval, runtime capture behavior, fake-mss/Pillow semantics, SQLite/UoW integration, service atomicity, and the actual independent execution review still require execution receipts. No product code or tests were run or changed in Round 2.

---

## Corrections Applied — 2026-08-26 after Round 2 (create-plan Step 5b)

**Corrector:** coordinator (not the reviewer). Verdict set to `corrections_applied` only. Independent Round 3 must re-score. Product code, tests, and `docs/build-plan/` were not modified.

### Finding dispositions (corrector claims; not an `approved` verdict)

| # | Change | Files |
|---|--------|-------|
| R2-F1 | `PLACEHOLDER_PATHS_*` now lists every Files Modified production path **and** the modified test files. `G36_TEST_PATHS_*` lists every modified test file (`test_domain.py`, `test_sqlite_uow.py`, `test_services.py`, `test_conversion_service.py`, plus the three new capture test modules). Scan lists are uniqued. Live tree currently has zero TODO/FIXME/NotImplementedError and zero skip/xfail in those existing tests (static rg). | named-sets.json; assert-anti-placeholder.ps1 |
| R2-F2 | `assert-exec-review-dispatch.ps1` now requires live frontmatter `DISPATCH_ID_FIELD` and loads **that exact** `DISPATCH_DIR/<id>/status.json` (not newest-any). Prompt must name `EXEC_REVIEW_FILE`. `final.md` first `verdict:` token must equal `EXEC_REVIEW_APPROVED`. Live frontmatter must be `review_mode=implementation`, `verdict=approved`, `findings_count=0`, `agent=REVIEWER_AGENT`. A prior `changes_required` receipt cannot approve a self-authored file. H1-7 requires `-DispatchId` and that the Codex prompt demand the same id in YAML. Residual: a fully forged dispatch folder + matching `final.md` can still be planted. | assert-exec-review-dispatch.ps1; task.md H1-7; named-sets.json |
| R2-F3 | `assert-meu-scoped-gate.ps1` now calls `Get-NamedStringArray -Name`. | assert-meu-scoped-gate.ps1:41-43 |
| R2-F4 | `REFLECTION_MARKERS` is the single owner; H2-2 and H2-4 consume `@($sets.REFLECTION_MARKERS)`. Hard-coded `'Friction Log'` array is gone from `task.md`. | named-sets.json; task.md H2-2/H2-4 |

### Blast-radius census (Step 5c / PR-6)

Index: `C:/Temp/av-kit/census-p9r2-summary.txt`. JSON parse: `C:/Temp/av-kit/census-p9r2-json.txt` (`PASS: named-sets json`).

| Receipt | Result | Disposition |
|---|---|---|
| census-p9r2-placeholder-enums.txt | named-sets + plan Files Modified | updated |
| census-p9r2-g36-domain.txt | named-sets G36 + GATE_PYTEST + plan/task pytest | updated / confirmed-consistent |
| census-p9r2-g36-sqlite.txt | named-sets G36 + PLACEHOLDER_35 + GATE | updated |
| census-p9r2-dispatch-id-field.txt | named-sets, plan table, task H1-7, assert script | updated |
| census-p9r2-reflection-markers.txt | named-sets + plan table + task H2-2/H2-4 | updated |
| census-p9r2-friction-literal.txt | (no hit in plan/task) | updated-gone |
| Live rg `'Friction Log'` in task.md | no match | updated-gone |

Blast-radius census: 4 Round-2 findings corrected; placeholder/G36 sets expanded to the Files Modified union; dispatch bound to exact id + final.md verdict token; reflection markers single-owned.

---

## Round 3 — 2026-08-26 (final cap)

**Workflow:** `/plan-critical-review` Round 3  
**Agent:** `gpt-5.6-sol`  
**Review mode:** `plan`  
**Execution performed:** none

### Intent Anchor

Executing this plan is supposed to deliver Session 16's capture engine only: MEU-34 domain contracts, MEU-35 SQLite plus fake-mss/Pillow infrastructure, and MEU-36 `CaptureService`, while leaving REST, MCP, GUI, Session 8c, and processor queues untouched. Round 3 cannot reach a substantive approval decision because the mandatory PR-6 correction census is incomplete and internally reports two failed searches; under the workflow's pre-verdict exception, that evidence failure alone requires `changes_required`.

### Scope

**Targets re-read from current disk state:**

- `docs/execution/plans/2026-08-26-p9-capture-engine/implementation-plan.md`
- `docs/execution/plans/2026-08-26-p9-capture-engine/task.md`
- `docs/execution/plans/2026-08-26-p9-capture-engine/named-sets.json`
- all eight `assert-*.ps1` files in the plan folder
- this rolling Round 1/Round 2 review and correction log
- `C:/Temp/av-kit/census-p9r2-summary.txt`, every live `census-p9r2-*.txt`, and the prior `census-p9-*.txt` census

Static evidence only: redirected `Get-Content`, `rg`, and `Test-Path`. No pytest, pyright, ruff, migration, plan assertion script, repository Python tool, or other mutating command was executed.

### Pre-Verdict Procedural Gate

| # | Gate | Confidence | Evidence | Required correction | Status |
|---|------|------------|----------|---------------------|--------|
| R3-PG1 | **PR-6 correction census is not complete or auditable.** The named Round 2 census summary records `r2-gate-dash-key rc=2` and `r2-gate-dash-name rc=2`, and the corresponding receipts contain ripgrep option-parsing errors (`unrecognized flag -K`; invalid `-m` value). Those two receipts are omitted from the correction log's disposition table. In addition, all six receipt paths named by that table (`census-p9r2-placeholder-enums.txt` through `census-p9r2-friction-literal.txt`) return `False` from exact `Test-Path`; the files on disk instead have an extra `r2-` segment. The workflow requires the raw unfiltered census and a per-hit/no-hit disposition for every query before corrected content can be scored. | High | `C:/Temp/av-kit/census-p9r2-summary.txt:7-8`; `C:/Temp/av-kit/census-p9r2-r2-gate-dash-key.txt:1`; `C:/Temp/av-kit/census-p9r2-r2-gate-dash-name.txt:1`; this file `:336`, `:338-345`; `C:/Temp/av-kit/p9r3-testpath-claimed-0.txt` through `p9r3-testpath-claimed-5.txt` | Regenerate the two failed literal searches using an end-of-options delimiter such as `rg -F -n -- '-Name' ...` / `-- '-Key' ...`; ensure every indexed receipt exists at the exact path named in the correction log; then disposition every hit or zero-hit result. | open |

This is the workflow's sole non-severity path to `changes_required`. Per PR-6, no High/Medium/Low content finding is scored after this precondition fails.

### Prior Pass Summary

| Round 2 finding | Prior status | Round 3 result |
|---|---|---|
| R2-F1 — anti-placeholder/G36 path coverage incomplete | open | Not adjudicated — PR-6 pre-verdict evidence gate failed. |
| R2-F2 — execution-review dispatch not bound to approval | open | Not adjudicated — PR-6 pre-verdict evidence gate failed. |
| R2-F3 — scoped gate used `-Key` instead of `-Name` | open (Low) | Not adjudicated — the very census queries intended to prove this blast radius both failed with `rc=2`. |
| R2-F4 — reflection markers duplicated | open (Low) | Not adjudicated — PR-6 pre-verdict evidence gate failed. |

### Mode and Scope-Lock Confirmation

- The plan is still unstarted: both plan files remain `status: draft`; every actionable task row is `[ ]`; MEU-34–36 remain `pending` with `execution_plan: null`; the four new production modules, three new capture test modules, three MEU handoffs, rolling implementation review, and reflection are absent.
- The direct stale-range sweep found no live `AC-34.1–34.12` or `AC-36.1–36.13` range literal. This independent observation does not repair the incomplete PR-6 census.
- Scope locks remain stated: Session 16 is MEU-34–36 only; MEU-37–39 and Session 8c/MEU-27 remain excluded; `FORBIDDEN_QUEUE_NAME` stays outside queues; mss index 0/fake-mss, staged `SETTING_NS`/`CAPTURE_KEYS`, `compact_continue`, §4A skip, and API-tree-hash OpenAPI skip remain present.

### Checklist Results

| Check | Result | Evidence |
|---|---|---|
| PR-1 Plan/task alignment | not scored | PR-6 failed before substantive re-review. |
| PR-2 Not-started confirmation | pass | Draft frontmatter, unchecked task rows, pending/null MEU records, and absent planned implementation/closeout artifacts. |
| PR-3 Task contract completeness | not scored | PR-6 failed before substantive re-review. |
| PR-4 Validation realism | not scored | R2-F1–F3 were not adjudicated after the census precondition failed. |
| PR-5 Source-backed planning | not scored | PR-6 failed before substantive re-review. |
| PR-6 Handoff/corrections readiness | fail — procedural gate | Two indexed searches failed, their receipts are undispositioned, and the six paths named by the correction table do not exist exactly as written. |
| PR-7 Scope discipline | not scored | Scope locks were confirmed unchanged, but substantive C2 scoring stops at PR-6. |
| PR-8 Control reachability/totality | not scored | R2-F1/R2-F2 were not adjudicated after the census precondition failed. |
| PR-9 Single-statement discipline | not scored | R2-F4 was not adjudicated after the census precondition failed. |

### Commands and Receipts

Only redirected static evidence was used. Key Round 3 receipts under `C:/Temp/av-kit/`:

- Full live reads: `p9r3-implementation-plan.txt`, `p9r3-task.txt`, `p9r3-named-sets.txt`, `p9r3-assert-*.ps1.txt`, `p9r3-prior-review.txt`
- Census: `p9r3-census-file-list.txt`, `p9r3-census-read-0.txt` through `p9r3-census-read-10.txt`, `p9r3-correction-log-census.txt`
- Exact missing-path proof: `p9r3-testpath-claimed-0.txt` through `p9r3-testpath-claimed-5.txt`
- Mode/scope: `p9r3-stale-ranges.txt`, `p9r3-started-markers.txt`, `p9r3-unstarted-markers.txt`, `p9r3-meu-status-full.txt`, `p9r3-unstarted-path-0.txt` through `p9r3-unstarted-path-11.txt`, `p9r3-scope-locks.txt`
- Artifact guard/calibration: `p9r3-review-template.txt`, `p9r3-peer-exemplar.txt`, `p9r3-pre-edit-guard.txt`

### Open Questions / Assumptions

- No product-behavior decision was reached or requested. The only blocker is the workflow's objective PR-6 evidence precondition.
- The live corrected files were read as required, but their Round 2 closure claims are deliberately not converted into Round 3 pass/fail dispositions after PR-6 failed.
- This is Round 3 of 3. The plan-review round cap is reached, so no autonomous `/plan-corrections` or further review round is authorized.

### Verdict

`changes_required` — PR-6's mandatory pre-verdict census gate failed. Two Round 2 blast-radius searches terminated with `rc=2`, those failed receipts have no correction-log disposition, and the six receipt paths the log does name are absent at those exact paths. Because this is the final review round, stop at the round cap and obtain explicit human direction before any correction, execution, or additional review.

### Residual Risk

R2-F1–R2-F4 remain unadjudicated in Round 3; this verdict does not assert that the live corrections are substantively wrong. Runtime capture behavior also remains untested because the plan is unstarted and this review was intentionally static.

### Follow-Up

Human direction is required at the Round 3 cap. The minimal evidence repair is to regenerate the two failed dash-prefixed literal searches with `--`, align the correction log to receipt paths that actually exist, and disposition every query result. This reviewer made no product, test, or plan-file changes.

---

## Corrections Applied — 2026-08-26 after Round 3 (create-plan Step 5b; user chose (a))

**Corrector:** coordinator (not the reviewer). Frontmatter `verdict: corrections_applied` only. Independent Round 4 must re-score R2-F1–F4 and PR-6 against live files. Product code, tests, and `docs/build-plan/` were not modified.

**Human authorization:** USER_EXPLICIT `(a)` continue review loop (round 4+) until `approved`. create-plan Step 5d (a) wins over plan-corrections.md standalone HARD STOP at cap 3.

**Instruction conflicts (not silently picked):**

1. `plan-corrections.md` Write Scope omits `named-sets.json` and plan-folder `assert-*.ps1`. Treated as create-plan Step 4 plan artifacts, not production code.
2. AGENTS.md P0 requires `rtk proxy`; output-evidence-policy allows optional RTK. This plan follows P0.

### Finding dispositions (corrector claims; not an `approved` verdict)

| # | Change | Files |
|---|--------|-------|
| R3-PG1 / PR-6 | Regenerated blast-radius census with `rg -F -n --` for dash literals. Every receipt path named below exists (`Test-Path` True in `C:/Temp/av-kit/census-p9r4-testpath.txt`, FALSE_COUNT=0). Per-hit dispositions are in `C:/Temp/av-kit/census-p9r4-dispositions.txt` and restated in the table below. | census-p9r4-* |
| R2-F1 | `PLACEHOLDER_PATHS_*` / `G36_TEST_PATHS_*` remain the Files Modified union. `GATE_PYTEST_35` / `GATE_RUFF_35` / `GATE_PYRIGHT_35` now also cover FakeUoW tests and `storage.py` / `packages/core`. Row 5 green pytest and plan verification §2 match `GATE_PYTEST_35`. | named-sets.json; task.md:48; implementation-plan.md:395 |
| R2-F2 | Unchanged from Round 2 correction: exact `DISPATCH_DIR/<dispatch_id>/status.json` + `final.md` first verdict token = `EXEC_REVIEW_APPROVED`. Residual: a fully forged dispatch folder + matching `final.md` can still be planted. | assert-exec-review-dispatch.ps1 |
| R2-F3 | `assert-meu-scoped-gate.ps1:41-43` calls `Get-NamedStringArray -Sets $sets -Name`. Contiguous `-Key` calls exist only in `assert-anti-placeholder.ps1`, whose param is `$Key`. Dash searches used `--`. | assert-meu-scoped-gate.ps1; census-p9r4-20/21/24/25 |
| R2-F4 | `REFLECTION_MARKERS` remains the single owner; `'Friction Log'` has zero hits. | named-sets.json; task.md H2-2/H2-4; census-p9r4-05 |

### Blast-radius census (PR-6) — exact paths, Test-Path True

Index: `C:/Temp/av-kit/census-p9r4-index.txt`. Dispositions: `C:/Temp/av-kit/census-p9r4-dispositions.txt`. Test-Path: `C:/Temp/av-kit/census-p9r4-testpath.txt`.

| Receipt | rg rc / lines | Disposition summary |
|---|---|---|
| `C:/Temp/av-kit/census-p9r4-01-old-ac34-range.txt` | 1 / 0 | updated-gone hyphen `AC-34.1-34.12` |
| `C:/Temp/av-kit/census-p9r4-02-old-ac36-range.txt` | 1 / 0 | updated-gone hyphen `AC-36.1-36.13` |
| `C:/Temp/av-kit/census-p9r4-03-old-red34.txt` | 1 / 0 | updated-gone `RED_COUNT_34": 12` |
| `C:/Temp/av-kit/census-p9r4-04-old-red36.txt` | 1 / 0 | updated-gone `RED_COUNT_36": 13` |
| `C:/Temp/av-kit/census-p9r4-05-friction-literal.txt` | 1 / 0 | updated-gone `'Friction Log'` |
| `C:/Temp/av-kit/census-p9r4-06-dispatch-id-field.txt` | 0 / 6 | updated / confirmed-consistent `DISPATCH_ID_FIELD` owner + H1-7 |
| `C:/Temp/av-kit/census-p9r4-07-reflection-markers.txt` | 0 / 4 | updated / confirmed-consistent `REFLECTION_MARKERS` H2-2/H2-4 |
| `C:/Temp/av-kit/census-p9r4-08-placeholder-enums.txt` | 0 / 2 | updated PLACEHOLDER_34 + Files Modified |
| `C:/Temp/av-kit/census-p9r4-09-placeholder-storage.txt` | 0 / 3 | updated PLACEHOLDER_35 + GATE_RUFF_35 + Files Modified |
| `C:/Temp/av-kit/census-p9r4-10-g36-domain.txt` | 0 / 9 | updated / confirmed-consistent G36/PLACEHOLDER/GATE + pytest |
| `C:/Temp/av-kit/census-p9r4-11-g36-sqlite.txt` | 0 / 9 | updated GATE_PYTEST_35 + row 5 green |
| `C:/Temp/av-kit/census-p9r4-12-g36-services.txt` | 0 / 12 | updated GATE_PYTEST_35 + row 5; confirmed-consistent MEU-36 |
| `C:/Temp/av-kit/census-p9r4-13-g36-conv.txt` | 0 / 12 | same as 12 for conversion FakeUoW tests |
| `C:/Temp/av-kit/census-p9r4-14-gate-pyright-35.txt` | 0 / 1 | updated `GATE_PYRIGHT_35` includes `packages/core` |
| `C:/Temp/av-kit/census-p9r4-15-gate-pytest-35.txt` | 0 / 1 | updated `GATE_PYTEST_35` key; members in dump 26 |
| `C:/Temp/av-kit/census-p9r4-16-exec-final-md.txt` | 0 / 6 | updated `final.md` first verdict token binding |
| `C:/Temp/av-kit/census-p9r4-17-dispatch-id-yaml.txt` | 0 / 5 | updated exact `dispatch_id` folder bind |
| `C:/Temp/av-kit/census-p9r4-18-name-call.txt` | 0 / 7 | mixed: function-name substring + R2-F3 `-Name` calls + anti-placeholder `-Key` (see dispositions.txt) |
| `C:/Temp/av-kit/census-p9r4-19-key-call.txt` | 0 / 7 | confirmed-consistent `Get-FrontmatterValue -Key` and anti-placeholder `-Key` |
| `C:/Temp/av-kit/census-p9r4-20-old-gate-key-paren.txt` | 0 / 2 | confirmed-consistent anti-placeholder only; **no** scoped-gate `-Key (` |
| `C:/Temp/av-kit/census-p9r4-21-new-gate-name-paren.txt` | 0 / 3 | updated scoped-gate `-Name (` at lines 41-43 |
| `C:/Temp/av-kit/census-p9r4-22-en-dash-ac34.txt` | 1 / 0 | updated-gone en-dash `AC-34.1–34.12` |
| `C:/Temp/av-kit/census-p9r4-23-en-dash-ac36.txt` | 1 / 0 | updated-gone en-dash `AC-36.1–36.13` |
| `C:/Temp/av-kit/census-p9r4-24-get-named-key.txt` | 0 / 2 | confirmed-consistent anti-placeholder only (`rg -F -n --`) |
| `C:/Temp/av-kit/census-p9r4-25-get-named-name.txt` | 0 / 3 | updated scoped-gate `-Name` only (`rg -F -n --`) |
| `C:/Temp/av-kit/census-p9r4-26-gate-set-dump.txt` | dump | updated GATE/PLACEHOLDER/G36 member dump |

Per-hit `file:line` dispositions for every HIT line are in `C:/Temp/av-kit/census-p9r4-dispositions.txt`. Queries 18/19 include incidental substring hits (`-Name` inside `Get-NamedStringArray`); queries 20/21/24/25 are the R2-F3 blast-radius proof using `--`.

Helpers (all `Test-Path` True): `assert-red-oracle.ps1`, `assert-api-tree-hash.ps1`, `assert-openapi-skip.ps1`, `assert-handoff-markers.ps1`, `assert-handoff-acs.ps1`, `assert-anti-placeholder.ps1`, `assert-meu-scoped-gate.ps1`, `assert-exec-review-dispatch.ps1`.

Blast-radius census: PR-6 dash searches used `--`; every named receipt exists at the exact path written here; Round 2 findings remain claimed-closed pending Round 4 adjudication.

---

## Round 4 — 2026-08-26 (user-authorized continuation after cap)

**Workflow:** `/plan-critical-review` Round 4  
**Agent:** `gpt-5.6-sol`  
**Review mode:** `plan`  
**Execution performed:** none

### Intent Anchor

Executing this plan is supposed to deliver Session 16's capture engine only: MEU-34 domain contracts, MEU-35 SQLite plus fake-mss/Pillow infrastructure, and MEU-36 `CaptureService`, while leaving MEU-37–39 and Session 8c/MEU-27 untouched. Round 4 cannot reach a substantive approval decision because the mandatory PR-6 correction log does not assign every raw census HIT `file:line` its own disposition; under the workflow's pre-verdict exception, that procedural evidence failure alone requires `changes_required`.

### Scope

**Targets re-read from current disk state:**

- `docs/execution/plans/2026-08-26-p9-capture-engine/implementation-plan.md`
- `docs/execution/plans/2026-08-26-p9-capture-engine/task.md`
- `docs/execution/plans/2026-08-26-p9-capture-engine/named-sets.json`
- all eight `assert-*.ps1` files in the plan folder
- this rolling Round 1/Round 2/Round 3 review and both correction sections
- `C:/Temp/av-kit/census-p9r4-index.txt`, `census-p9r4-testpath.txt`, `census-p9r4-dispositions.txt`, and all 26 indexed `census-p9r4-*.txt` receipts

Static evidence only: redirected `Get-Content`, `rg`, and `Test-Path`. No pytest, pyright, ruff, migration, plan assertion script, repository Python tool, product code, test, or plan file was executed or modified.

### Pre-Verdict Procedural Gate

| # | Gate | Confidence | Evidence | Required correction | Status |
|---|------|------------|----------|---------------------|--------|
| R4-PG1 | **PR-6 correction log is not complete at per-HIT granularity.** All 29 exact census/index/ledger paths independently return `Test-Path=True`, and the dash-query records state `rg -F -n --`, so the Round 3 missing-path and option-parsing defects are repaired. However, the external disposition ledger assigns `assert-exec-review-dispatch.ps1:14` the disposition `updated`, while an exact `rg -F -n` for that coordinate in this rolling review returns rc=1. The same absence was reproduced for other raw HIT coordinates including `named-sets.json:129` and `named-sets.json:210`. The post-Round-3 correction table records only receipt-level summaries and explicitly delegates per-HIT dispositions to the external ledger. The user and PR-6 require every HIT `file:line` to carry a disposition in **both** the external ledger and the correction-log table. | High | `C:/Temp/av-kit/census-p9r4-06-dispatch-id-field.txt:1`; `C:/Temp/av-kit/census-p9r4-dispositions.txt:17`; this file `:475`, `:497`; `C:/Temp/av-kit/p9r4-pr6-log-coordinate-proof.txt` (exact search rc=1); `C:/Temp/av-kit/p9r4-pr6-log-coordinate-03.txt`; `C:/Temp/av-kit/p9r4-pr6-log-coordinate-04.txt` | Expand the post-Round-3 correction-log table so every HIT coordinate in queries 06–21 and 24–25 is listed with `updated` or `confirmed-consistent`; keep the existing external ledger and exact receipt paths. | open |

This is the workflow's sole non-severity path to `changes_required`. Per PR-6 and the user's Round 4 instruction, no High/Medium/Low content finding is scored after this precondition fails; frontmatter `findings_count` therefore remains `0`.

### Prior Pass Summary

| Round 2 finding | Prior status | Round 4 result |
|---|---|---|
| R2-F1 — anti-placeholder/G36 path and MEU-35 gate coverage | open | Not adjudicated — PR-6 pre-verdict evidence gate failed. |
| R2-F2 — execution-review dispatch provenance | open | Not adjudicated — PR-6 pre-verdict evidence gate failed. |
| R2-F3 — scoped gate `-Name` call shape | open (Low) | Not adjudicated — PR-6 pre-verdict evidence gate failed. |
| R2-F4 — reflection marker ownership | open (Low) | Not adjudicated — PR-6 pre-verdict evidence gate failed. |

### Mode and Scope-Lock Confirmation

- The plan remains unstarted: both plan files retain `status: draft`; every actionable task row remains `[ ]`; the four planned production capture modules, three new capture test modules, three MEU handoffs, rolling implementation review, and reflection all return `Test-Path=False`.
- Scope locks remain stated in the live plan: Session 16 is MEU-34–36 only; MEU-37–39 are not packed; Session 8c/MEU-27 must not start. This observation does not substitute for substantive re-scoring.

### Checklist Results

| Check | Result | Evidence |
|---|---|---|
| PR-1 Plan/task alignment | not scored | PR-6 failed before substantive re-review. |
| PR-2 Not-started confirmation | pass | Draft frontmatter, unchecked task rows, and absent planned implementation/closeout artifacts. |
| PR-3 Task contract completeness | not scored | PR-6 failed before substantive re-review. |
| PR-4 Validation realism | not scored | R2-F1–F3 were not adjudicated after the census precondition failed. |
| PR-5 Source-backed planning | not scored | PR-6 failed before substantive re-review. |
| PR-6 Handoff/corrections readiness | fail — procedural gate | Exact paths and dash syntax pass, but the rolling correction table omits per-HIT `file:line` dispositions that exist only in the external ledger. |
| PR-7 Scope discipline | not scored | Scope locks were observed unchanged; substantive C2 scoring stops at PR-6. |
| PR-8 Control reachability/totality | not scored | R2-F1/R2-F2 were not adjudicated after the census precondition failed. |
| PR-9 Single-statement discipline | not scored | R2-F4 was not adjudicated after the census precondition failed. |

### Commands and Receipts

Only redirected static evidence was used. Key Round 4 receipts under `C:/Temp/av-kit/`:

- Procedure/context: `p9r4-terminal-preflight.txt`, `p9r4-review-procedure.txt`, `p9r4-session-review-context.txt`
- Live targets: `p9r4-implementation-plan-head.txt`, `p9r4-implementation-plan-tail.txt`, `p9r4-task-named-sets.txt`, `p9r4-assert-helpers-01-04.txt`, `p9r4-assert-helpers-05-08.txt`
- PR-6: `p9r4-pr6-exact-testpath.txt`, `p9r4-pr6-primary-evidence.txt`, `p9r4-pr6-raw-census.txt`, `p9r4-pr6-ledger-coordinate.txt`, `p9r4-pr6-log-coordinate-proof.txt`, `p9r4-pr6-log-coordinate-01.txt` through `p9r4-pr6-log-coordinate-06.txt`
- Mode/guard: `p9r4-unstarted-testpath.txt`, `p9r4-pre-edit-guard.txt`

### Open Questions / Assumptions

- No product-behavior decision is required. The only Round 4 blocker is the objective PR-6 evidence precondition.
- The live corrected plan files and helpers were re-read as required, but their Round 2 closure claims are deliberately not converted into Round 4 pass/fail dispositions after PR-6 failed.
- The user's explicit choice `(a)` authorized Round 4 after the prior cap; it does not waive PR-6 or authorize execution on a `changes_required` verdict.

### Verdict

`changes_required` — PR-6's mandatory pre-verdict gate still fails. The exact census receipts now exist and the dash searches use `rg -F -n --`, but the post-Round-3 correction-log table does not assign every raw HIT `file:line` a disposition; those per-HIT entries exist only in `census-p9r4-dispositions.txt`. R2-F1–F4 were not re-scored.

### Residual Risk

R2-F1–R2-F4 remain unadjudicated in Round 4; this verdict does not assert that the live content corrections are substantively wrong. Runtime capture behavior remains untested because the plan is unstarted and this review was intentionally static.

### Follow-Up

Route only R4-PG1 through `/plan-corrections`: mirror every external-ledger HIT `file:line` and its disposition into the rolling post-Round-3 correction-log table, preserve the raw receipts, then resubmit for substantive re-scoring. This reviewer made no product, test, or plan-file changes.

---

## Corrections Applied — 2026-08-26 after Round 4 (create-plan Step 5b; user chose (a))

**Corrector:** coordinator (not the reviewer). Frontmatter `verdict: corrections_applied` only. Independent Round 5 must re-score R2-F1–F4 if PR-6 now passes. Product code, tests, plan files, and `docs/build-plan/` were not modified in this correction. Raw receipts are unchanged.

**R4-PG1 repair:** every HIT coordinate from queries 06–21 and 24–25 is listed below with `updated` or `confirmed-consistent`. NO-HIT queries 01–05 and 22–23 remain `updated-gone`. The external ledger `C:/Temp/av-kit/census-p9r4-dispositions.txt` is kept; this table is the rolling correction-log copy required by PR-6.

| Query | file:line | Disposition | Note |
|---|---|---|---|
| 01 | NO-HIT | updated-gone | `C:/Temp/av-kit/census-p9r4-01-old-ac34-range.txt` hyphen `AC-34.1-34.12` |
| 02 | NO-HIT | updated-gone | `C:/Temp/av-kit/census-p9r4-02-old-ac36-range.txt` hyphen `AC-36.1-36.13` |
| 03 | NO-HIT | updated-gone | `C:/Temp/av-kit/census-p9r4-03-old-red34.txt` |
| 04 | NO-HIT | updated-gone | `C:/Temp/av-kit/census-p9r4-04-old-red36.txt` |
| 05 | NO-HIT | updated-gone | `C:/Temp/av-kit/census-p9r4-05-friction-literal.txt` |
| 22 | NO-HIT | updated-gone | `C:/Temp/av-kit/census-p9r4-22-en-dash-ac34.txt` |
| 23 | NO-HIT | updated-gone | `C:/Temp/av-kit/census-p9r4-23-en-dash-ac36.txt` |
| 06 | assert-exec-review-dispatch.ps1:14 | updated | DISPATCH_ID_FIELD owner load |
| 06 | assert-exec-review-dispatch.ps1:18 | confirmed-consistent | fail-closed missing field |
| 06 | named-sets.json:104 | updated | single owner dispatch_id |
| 06 | task.md:64 | updated | H1-7 binds field + final.md token |
| 06 | task.md:85 | updated | self-review prohibition text |
| 06 | implementation-plan.md:116 | updated | named-set table |
| 07 | implementation-plan.md:118 | confirmed-consistent | named-set table |
| 07 | named-sets.json:107 | updated | REFLECTION_MARKERS owner array |
| 07 | task.md:67 | updated | H2-2 consumes REFLECTION_MARKERS |
| 07 | task.md:69 | updated | H2-4 consumes REFLECTION_MARKERS |
| 08 | implementation-plan.md:209 | confirmed-consistent | Files Modified MEU-34 |
| 08 | named-sets.json:123 | updated | PLACEHOLDER_PATHS_34 includes enums.py |
| 09 | implementation-plan.md:282 | confirmed-consistent | Files Modified MEU-35 |
| 09 | named-sets.json:138 | updated | PLACEHOLDER_PATHS_35 includes storage.py |
| 09 | named-sets.json:187 | updated | GATE_RUFF_35 includes storage.py |
| 10 | task.md:45 | confirmed-consistent | MEU-34 green pytest |
| 10 | named-sets.json:93 | confirmed-consistent | TEST_DOMAIN owner |
| 10 | named-sets.json:129 | updated | PLACEHOLDER_PATHS_34 |
| 10 | named-sets.json:152 | updated | G36_TEST_PATHS_34 |
| 10 | named-sets.json:165 | updated | GATE_PYTEST_34 |
| 10 | named-sets.json:183 | updated | GATE_RUFF_34 |
| 10 | named-sets.json:202 | updated | GATE_RUFF_ALL |
| 10 | implementation-plan.md:215 | confirmed-consistent | Files Modified |
| 10 | implementation-plan.md:390 | confirmed-consistent | verification pytest |
| 11 | task.md:48 | updated | MEU-35 green includes FakeUoW tests |
| 11 | implementation-plan.md:285 | confirmed-consistent | Files Modified |
| 11 | implementation-plan.md:395 | updated | verification pytest includes FakeUoW tests |
| 11 | named-sets.json:94 | confirmed-consistent | TEST_SQLITE owner |
| 11 | named-sets.json:141 | updated | PLACEHOLDER_PATHS_35 |
| 11 | named-sets.json:156 | updated | G36_TEST_PATHS_35 |
| 11 | named-sets.json:169 | updated | GATE_PYTEST_35 |
| 11 | named-sets.json:189 | updated | GATE_RUFF_35 |
| 11 | named-sets.json:204 | updated | GATE_RUFF_ALL |
| 12 | named-sets.json:95 | confirmed-consistent | TEST_SERVICES owner |
| 12 | named-sets.json:142 | updated | PLACEHOLDER_PATHS_35 |
| 12 | named-sets.json:157 | updated | G36_TEST_PATHS_35 |
| 12 | named-sets.json:170 | updated | GATE_PYTEST_35 |
| 12 | named-sets.json:175 | confirmed-consistent | GATE_PYTEST_36 |
| 12 | named-sets.json:190 | updated | GATE_RUFF_35 |
| 12 | named-sets.json:205 | updated | GATE_RUFF_ALL |
| 12 | implementation-plan.md:286 | confirmed-consistent | Files Modified MEU-35 |
| 12 | implementation-plan.md:395 | updated | MEU-35 verification pytest |
| 12 | implementation-plan.md:400 | confirmed-consistent | MEU-36 verification pytest |
| 12 | task.md:48 | updated | MEU-35 green pytest |
| 12 | task.md:51 | confirmed-consistent | MEU-36 green pytest |
| 13 | task.md:48 | updated | MEU-35 green pytest |
| 13 | task.md:51 | confirmed-consistent | MEU-36 green pytest |
| 13 | implementation-plan.md:287 | confirmed-consistent | Files Modified MEU-35 |
| 13 | implementation-plan.md:395 | updated | MEU-35 verification pytest |
| 13 | implementation-plan.md:400 | confirmed-consistent | MEU-36 verification pytest |
| 13 | named-sets.json:96 | confirmed-consistent | TEST_SVC_CONV owner |
| 13 | named-sets.json:143 | updated | PLACEHOLDER_PATHS_35 |
| 13 | named-sets.json:158 | updated | G36_TEST_PATHS_35 |
| 13 | named-sets.json:171 | updated | GATE_PYTEST_35 |
| 13 | named-sets.json:176 | confirmed-consistent | GATE_PYTEST_36 |
| 13 | named-sets.json:191 | updated | GATE_RUFF_35 |
| 13 | named-sets.json:206 | updated | GATE_RUFF_ALL |
| 14 | named-sets.json:210 | updated | GATE_PYRIGHT_35 includes packages/core |
| 15 | named-sets.json:167 | updated | GATE_PYTEST_35 key |
| 16 | assert-exec-review-dispatch.ps1:104 | updated | missing final.md fail-closed |
| 16 | assert-exec-review-dispatch.ps1:110 | updated | no verdict token fail-closed |
| 16 | assert-exec-review-dispatch.ps1:114 | updated | first verdict token must equal EXEC_REVIEW_APPROVED |
| 16 | task.md:64 | updated | H1-7 names final.md token |
| 16 | task.md:85 | updated | self-review prohibition |
| 16 | implementation-plan.md:116 | updated | named-set table |
| 17 | assert-exec-review-dispatch.ps1:1 | updated | comment binds dispatch_id |
| 17 | assert-exec-review-dispatch.ps1:84 | updated | status.json dispatch_id must match frontmatter |
| 17 | assert-exec-review-dispatch.ps1:85 | updated | mismatch error |
| 17 | named-sets.json:104 | updated | DISPATCH_ID_FIELD value |
| 17 | implementation-plan.md:116 | updated | named-set table |
| 18 | assert-meu-scoped-gate.ps1:18 | confirmed-consistent | function name substring Get-NamedStringArray contains -Name |
| 18 | assert-meu-scoped-gate.ps1:41 | updated | Get-NamedStringArray -Name call (R2-F3) |
| 18 | assert-meu-scoped-gate.ps1:42 | updated | Get-NamedStringArray -Name call (R2-F3) |
| 18 | assert-meu-scoped-gate.ps1:43 | updated | Get-NamedStringArray -Name call (R2-F3) |
| 18 | assert-anti-placeholder.ps1:16 | confirmed-consistent | function name substring |
| 18 | assert-anti-placeholder.ps1:55 | confirmed-consistent | -Key call; param on that helper is $Key |
| 18 | assert-anti-placeholder.ps1:56 | confirmed-consistent | -Key call; param on that helper is $Key |
| 19 | assert-exec-review-dispatch.ps1:40 | confirmed-consistent | Get-FrontmatterValue -Key |
| 19 | assert-exec-review-dispatch.ps1:41 | confirmed-consistent | Get-FrontmatterValue -Key |
| 19 | assert-exec-review-dispatch.ps1:42 | confirmed-consistent | Get-FrontmatterValue -Key |
| 19 | assert-exec-review-dispatch.ps1:43 | confirmed-consistent | Get-FrontmatterValue -Key |
| 19 | assert-exec-review-dispatch.ps1:44 | confirmed-consistent | Get-FrontmatterValue -Key $idField |
| 19 | assert-anti-placeholder.ps1:55 | confirmed-consistent | Get-NamedStringArray -Key |
| 19 | assert-anti-placeholder.ps1:56 | confirmed-consistent | Get-NamedStringArray -Key |
| 20 | assert-anti-placeholder.ps1:55 | confirmed-consistent | not the scoped-gate helper |
| 20 | assert-anti-placeholder.ps1:56 | confirmed-consistent | not the scoped-gate helper |
| 21 | assert-meu-scoped-gate.ps1:41 | updated | scoped-gate -Name ( |
| 21 | assert-meu-scoped-gate.ps1:42 | updated | scoped-gate -Name ( |
| 21 | assert-meu-scoped-gate.ps1:43 | updated | scoped-gate -Name ( |
| 24 | assert-anti-placeholder.ps1:55 | confirmed-consistent | contiguous Get-NamedStringArray -Key |
| 24 | assert-anti-placeholder.ps1:56 | confirmed-consistent | contiguous Get-NamedStringArray -Key |
| 25 | assert-meu-scoped-gate.ps1:41 | updated | contiguous Get-NamedStringArray -Name |
| 25 | assert-meu-scoped-gate.ps1:42 | updated | contiguous Get-NamedStringArray -Name |
| 25 | assert-meu-scoped-gate.ps1:43 | updated | contiguous Get-NamedStringArray -Name |
| 26 | named-sets.json GATE dump | updated | `C:/Temp/av-kit/census-p9r4-26-gate-set-dump.txt` |

Query 20 NO HIT in assert-meu-scoped-gate.ps1 (old `-Key (` gone). Query 24 NO HIT in assert-meu-scoped-gate.ps1. Query 25 NO HIT in assert-anti-placeholder.ps1.

Proof coordinates cited by Round 4 are now in this table: `assert-exec-review-dispatch.ps1:14`, `named-sets.json:129`, `named-sets.json:210`.

---

## Round 5 — 2026-08-26

**Workflow:** `/plan-critical-review` Round 5  
**Agent:** `gpt-5.6-sol`  
**Review mode:** `plan`  
**Execution performed:** none

### Intent Anchor

Executing this plan is supposed to deliver Session 16's capture engine only: MEU-34 domain contracts, MEU-35 SQLite plus fake-mss/Pillow infrastructure, and MEU-36 `CaptureService`, while leaving REST, MCP, GUI, Session 8c, MEU-27, and MEU-37–39 untouched. The post-Round-4 PR-6 correction log is now auditable, and the live plan closes R2-F1–F4 without a named validation that can false-pass missing material behavior; executing the plan would deliver the stated objective.

### Scope

Re-read from live disk:

- `docs/execution/plans/2026-08-26-p9-capture-engine/implementation-plan.md`
- `docs/execution/plans/2026-08-26-p9-capture-engine/task.md`
- `docs/execution/plans/2026-08-26-p9-capture-engine/named-sets.json`
- all eight plan-folder `assert-*.ps1` files
- this rolling review, including every prior round and every prior correction section, especially the post-Round-4 correction table
- `C:/Temp/av-kit/census-p9r4-index.txt`, `census-p9r4-testpath.txt`, `census-p9r4-dispositions.txt`, and `census-p9r4-01-old-ac34-range.txt` through `census-p9r4-26-gate-set-dump.txt`

Static evidence only: redirected `Get-Content`, `rg`, and `Test-Path`. No pytest, pyright, ruff, migration, assertion helper, repository Python tool, or product command was executed.

### Findings

No Critical, High, Medium, or Low findings remain in Round 5.

### PR-6 Pre-Verdict Gate

`pass` — all 29 exact census/index/ledger paths returned `Test-Path=True`; `census-p9r4-dispositions.txt` states dash-prefixed searches used `rg -F -n --`; and every raw HIT coordinate from queries 06–21 and 24–25 appears in the post-Round-4 correction table with `updated` or `confirmed-consistent`. The required coordinator proof is `C:/Temp/av-kit/census-p9r5-pr6-log-proof.txt`; its exact searches hit disposition rows for `assert-exec-review-dispatch.ps1:14`, `named-sets.json:129`, and `named-sets.json:210`.

### R2-F1–F4 Re-score

| Finding | Round 5 result | Live evidence |
|---|---|---|
| R2-F1 — touched-file placeholder/G36 and MEU-35 gate coverage | ✅ Fixed | `PLACEHOLDER_PATHS_34/35/36` cover every plan `Files Modified` product/test path; `G36_TEST_PATHS_*` cover every modified test. `GATE_PYTEST_35` contains `test_capture_adapter.py`, `test_sqlite_uow.py`, `test_services.py`, and `test_conversion_service.py`; task row 5 runs the same four tests. `GATE_RUFF_35` explicitly covers `ports/storage.py` plus those tests, and `GATE_PYRIGHT_35` covers both infrastructure and core. (`named-sets.json:122-212`; `implementation-plan.md:205-215`, `:272-287`, `:344-350`; `task.md:48`) |
| R2-F2 — independent dispatch correlation | ✅ Fixed | The helper reads the live `dispatch_id`, loads only `DISPATCH_DIR/<id>/status.json`, verifies schema/exit/model/id, follows that status's `final_output`, and requires the first `verdict:` token to equal `EXEC_REVIEW_APPROVED`. H1-7 explicitly requires `Invoke-CodexDispatch.ps1 -DispatchId` and the same id in review YAML. It is not a newest-any search. (`assert-exec-review-dispatch.ps1:40-44`, `:66-85`, `:102-114`; `task.md:64`, `:85`) |
| R2-F3 — scoped-gate parameter | ✅ Fixed | `Get-NamedStringArray` owns `-Name`; all three scoped-gate calls use `-Name`. Census queries 20/24 show the old scoped-gate `-Key` form absent, while 21/25 show the three live `-Name` calls. (`assert-meu-scoped-gate.ps1:18-25`, `:41-43`) |
| R2-F4 — reflection marker ownership | ✅ Fixed | `REFLECTION_MARKERS` is single-owned in `named-sets.json`; H2-2 and H2-4 consume `@($sets.REFLECTION_MARKERS)`. The exact old duplicated task literal search `rg -F -n -- "'Friction Log'"` returns no hit. The canonical JSON owner retains the template-required marker once. (`named-sets.json:107-121`; `task.md:67`, `:69`; `docs/execution/reflections/TEMPLATE.md:19`) |

### Checklist Results

| Check | Result | Evidence |
|---|---|---|
| PR-1 Plan/task alignment | pass | Both retain MEU-34 Red/Green/gate → MEU-35 → MEU-36 → H1 review → H2 closeout. |
| PR-2 Not-started confirmation | pass | All actionable task rows remain `[ ]`; twelve planned new implementation/test/handoff/review/reflection paths returned `False`. |
| PR-3 Task contract completeness | pass | Each actionable row retains task, owner, deliverable, exact validation, dependency, context strategy, durable output, builder model, and status. |
| PR-4 Validation realism | pass | R2-F1 and R2-F3 are fixed; the scoped gates cover pytest, pyright, ruff, anti-placeholder, and G36 for their named slices. |
| PR-5 Source-backed planning | pass | The source labels and Spec/Local Canon/Human-approved locks accepted in Round 2 remain unchanged. |
| PR-6 Handoff/corrections readiness | pass | Exact receipt existence, dash parsing, raw HITs, external dispositions, and post-Round-4 per-HIT correction-log dispositions all reconcile. |
| PR-7 Scope discipline (C2) | pass | Session 16 remains MEU-34–36 only; MEU-37–39 are scheduled deferrals and Session 8c / MEU-27 remains excluded. |
| PR-8 Control reachability/totality | pass | R2-F1–F3 no longer expose a demonstrated material false-pass. H1-7 names the independent dispatch and binds its id/status/final verdict to the rolling review. |
| PR-9 Single-statement discipline | pass | Reflection markers and gate/path sets are single-owned in `named-sets.json`; consumers reference the owners. |

### Docs Review Results

| Check | Result | Evidence |
|---|---|---|
| DR-1 Claim-to-state match | pass | Post-Round-4 PR-6 claims match the live correction table and receipts; plan remains unstarted. |
| DR-2 Residual old terms | pass | The old duplicated single-quoted reflection-marker literal is absent; the canonical owner is retained. |
| DR-3 Downstream references updated | pass | R2-F1–F4 owners and consumers align across plan, task, named sets, and assertion helpers. |
| DR-4 Verification robustness | pass | No rescored named control demonstrates a material false-pass. |
| DR-5 Evidence auditability | pass | Round 4 raw receipts, external ledger, live Test-Path receipt, and rolling per-HIT dispositions are reproducible. |
| DR-6 Cross-reference integrity | pass | Session scope, gate members, dispatch contract, and reflection ownership remain consistent. |
| DR-7 Evidence freshness | pass | All plan-folder files and all Round 4 receipts were re-read from current disk state. |
| DR-8 Completion vs residual risk | pass | The plan is approved for execution but no implementation-complete claim is made. |

### Commands and Receipts

Only static evidence commands were used. Key Round 5 receipts:

- `C:/Temp/av-kit/census-p9r5-pr6-log-proof.txt`
- `C:/Temp/av-kit/census-p9r5-live-testpath.txt`
- `C:/Temp/av-kit/p9r5-read-r4-06.txt` through `p9r5-read-r4-21.txt`, plus `p9r5-read-r4-24.txt` and `p9r5-read-r4-25.txt`
- `C:/Temp/av-kit/p9r5-files-modified-exact.txt`, `p9r5-named-sets-gates.txt`, `p9r5-task-relevant-rows.txt`, `p9r5-dispatch-proof.txt`
- `C:/Temp/av-kit/p9r5-old-friction-literal.txt`, `p9r5-unstarted-testpath.txt`, `p9r5-scope-locks.txt`
- one full read receipt for each of the eight `assert-*.ps1` files

### Open Questions / Assumptions

- No human product decision is required by this review.
- The documented fully forged-dispatch-folder scenario remains a residual trust-boundary risk, not a High finding: H1-7 explicitly requires an independent `Invoke-CodexDispatch.ps1 -DispatchId` run, and no named task can satisfy that instruction without the independent dispatch. This review does not invent a cryptographic attestation requirement.

### Required Follow-up

No plan correction is required. This workflow stops after recording the independent Round 5 verdict; it does not start implementation.

### Verdict

`approved` — PR-6 passes against the post-Round-4 correction table, R2-F1–F4 are closed in the live plan folder, the Session 16 scope locks remain intact, and no High/Critical delivery-level false-pass remains. `findings_count: 0`.

### Residual Risk

This is a static plan review, not runtime evidence. Capture behavior, fake-mss/Pillow semantics, SQLite/UoW integration, service atomicity, and the actual independent execution-review dispatch still require the execution receipts named by the plan. The documented forged-dispatch-folder scenario remains outside the present non-cryptographic control contract.
