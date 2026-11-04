---
date: "2026-08-27"
review_mode: "plan"
target_plan: "docs/execution/plans/2026-08-27-p9-capture-native-picker/implementation-plan.md"
verdict: "changes_required"
findings_count: 5
round: 10
template_version: "2.1"
requested_verbosity: "standard"
agent: "GPT-5.6-sol (Codex)"
---

# Critical Review: 2026-08-27-p9-capture-native-picker

> **Review Mode**: `plan`
> **Verdict**: `changes_required`

---

## Intent Anchor

Executing this plan is supposed to revise the Phase 9/7 SSOTs, replace MEU-39's Chromium overlay with a self-contained .NET 8 WinForms region-picker sidecar, delete the old overlay with no fallback, and leave the Python `mss`, REST, and MCP surfaces unchanged. As written, it cannot reliably deliver that objective because several required controls can false-pass or are not connected to a production path.

## Scope

**Targets**:

- `docs/execution/plans/2026-08-27-p9-capture-native-picker/implementation-plan.md`
- `docs/execution/plans/2026-08-27-p9-capture-native-picker/task.md`

**Canonical sources checked**:

- `docs/build-plan/09-screenshot-capture.md` (Electron OS surface, named deferrals, ShareX map)
- `docs/build-plan/07-distribution.md` (Capture packaging, `extraResources`, exit checklist)
- `.agent/context/meu-status.yaml` and `.agent/context/meu-registry.md`
- Current MEU-39 production call chain in `ui/src/main/capture-overlay.ts`, `ui/src/main/index.ts`, `ui/src/main/capture-register.ts`, and `ui/src/main/capture-pixels.ts`
- Current packaging entrypoints in `ui/package.json`, `ui/electron-builder.yml`, and `ui/electron.vite.config.ts`

**Review Type**: plan review, first pass

**Checklist Applied**: PR-1 through PR-9 and DR-1 through DR-8, with explicit PR-7 scope-basis, PR-8 control-binding/totality, and PR-9 single-statement sweeps.

**Out of scope for this review**: relitigating the two 2026-08-27 USER_EXPLICIT decisions; modifying the plan/task/product files; reviewing implementation that does not yet exist.

---

## Findings

| # | Severity | Finding | File:Line | Recommendation | Status |
|---|----------|---------|-----------|----------------|--------|
| 1 | High | **PR-8 demonstrated vacuity: the H1 unchecked-row gate matches no task rows.** Running the planned regex against the current task reports `plannedPredicateCount: 0`, while the correct table-row census reports 22 unchecked rows (`C:/Temp/av-kit/native-picker-h1-vacuity.json`). This gate would allow review/closeout to start with every implementation row still open. | `task.md:45` | Replace the predicate with one that matches the actual backticked status cell and add a self-test/negative oracle proving one synthetic or current unchecked row makes the command fail. | open |
| 2 | High | **Sweep 8: the required closeout validator does not exist and is not scheduled for creation.** `Test-Path tools/validate_closeout_artifacts.py` is false (`C:/Temp/av-kit/native-picker-artifact-existence.json`), yet H1-6, H1-6a, H1-7, H2-2, and H2-4 depend on it. The Files Modified inventory does not create it, so the continuous closeout and approval gates are impossible to execute. | `task.md:50`; `task.md:53`; `task.md:56`; `task.md:58`; `implementation-plan.md:195` | Either schedule and validate creation of the executable before H1-6, or replace every dependent row with existing, exact structural/approval checks that are on disk. | open |
| 3 | High | **PR-8 control binding is missing for the native picker itself.** AC-40.1–40.4 validate pure `RectMath` and static program/config contracts, while task row 4 separately asks `RegionForm` to implement release/Enter/Esc, minimum-edge, clamp, crop, and exit mapping. No required test seam or call-chain assertion proves the production form event handlers call those controls. Because the manual smoke may become `[B]`, xunit can be green while `RegionForm` ignores the tested math or maps the wrong outcome. | `implementation-plan.md:159`; `implementation-plan.md:162`; `task.md:37`; `task.md:38` | Name the production event-handler/controller call chain and add negative integration tests through a testable picker controller/state machine proving below-min release cancels, out-of-bounds drag clamps before crop, Enter/release confirm, and Esc cancel map to the declared process outcomes. | open |
| 4 | High | **The clean packaging call chain does not invoke `build:picker`.** AC-40.10 adds a standalone script, an `extraResources` mapping, and one manual publish receipt, but the plan never changes the existing `dist` entrypoint (`electron-builder --win nsis --x64`) to build the sidecar. A one-time working-tree publish can make review green while a clean `npm run dist` has no `native/region-picker/publish` payload or packages stale output. | `implementation-plan.md:168`; `implementation-plan.md:217`; `task.md:39`; `ui/package.json:15` | Bind `build:picker` into the production packaging entrypoint (`predist` or an explicit composed dist script) and add a clean-path negative oracle that deletes/uses an empty publish directory, runs the registered packaging preparation, and proves the expected executable is the resource input. | open |
| 5 | High | **The claimed temp-to-inbox atomicity mechanism is not atomic and has no watcher-race oracle.** The plan calls `copy-bytes-then-unlink` an atomicity resolution, but Node explicitly makes no atomicity guarantee for copy operations. AC-40.6 observes writes/fetches only, so `fs.watch`/filmstrip code can observe a partially written final filename. `Spec (this plan)` is also circular rather than an allowed source basis. | `implementation-plan.md:164`; `implementation-plan.md:193` | Stage the copy under a non-final name inside the inbox filesystem, then publish the completed file with an appropriate same-filesystem atomic rename; add an adversarial watcher oracle that the final name is not observable before completion. Cite the mechanism as Local Canon/Research-backed rather than `Spec (this plan)`. | open |
| 6 | High | **Both RED validations unconditionally exit 0.** The commands discard the test exit code and cannot distinguish the required failing test from an unexpectedly green suite, absent tests, or an unrelated compile/setup failure. This materially false-passes the mandatory FAIL_TO_PASS proof even though row 77 calls the receipt evidence. | `task.md:37`; `task.md:40`; `task.md:77` | Capture the test exit code, require it to be nonzero, and validate the expected failing test/assertion signature from the unfiltered receipt; fail the row if the suite is green or fails for an unrelated reason. | open |
| 7 | Low | **PR-9 repeated threshold literal.** The 8-pixel minimum is restated as `8 px`, `PICKER_MIN_EDGE_PX (8)`, and `min-edge 8` across the revision table, normative helper contract, AC, and task row. | `implementation-plan.md:113`; `implementation-plan.md:128`; `implementation-plan.md:160`; `task.md:38` | Define `PICKER_MIN_EDGE_PX = 8` once in the normative contract and reference the named threshold elsewhere. | open |
| 8 | Low | **PR-9 repeated exit-code enumeration.** The `0/2/1-or-other` mapping is restated in the normative contract, boundary table, multiple ACs, and task row, creating avoidable drift. | `implementation-plan.md:128`; `implementation-plan.md:143`; `implementation-plan.md:162`; `implementation-plan.md:163`; `task.md:38` | Name the helper outcome/exit-code contract once and reference it from ACs/tasks; keep adversary examples without restating the full mapping. | open |

No Critical findings were identified.

### Non-blocking correction notes

- The plan/task call the driver `Claude Code` and pin `opus-5`, while `.agent/context/harness.local.md` names Cursor and the task template's Cursor builder catalog. Because every row is `shared`/`compact_continue`, this is clerical rather than blocking; align the labels during correction.
- AC-40.15's source label `P1 gates` should be `Local Canon (AGENTS.md P1 / registered UI gates)` to satisfy the allowed source taxonomy.
- The cited Electron issue supports the black/gray transparency failure, but not the plan's exact `~5%` figure in the reviewed text. Remove the percentage or cite evidence that actually quantifies it.

---

## Commands Executed

All shell output was redirected under `C:/Temp/av-kit/` and `$LASTEXITCODE` was captured before receipt reads.

- Line-numbered reads of both review targets: `C:/Temp/av-kit/native-picker-plan-task-lines.txt` and `native-picker-plan-first-task-tail.txt`
- Canonical-source reads: `C:/Temp/av-kit/native-picker-canonical-lines.txt`
- Artifact/executable existence sweep: `C:/Temp/av-kit/native-picker-artifact-existence.json`
- Overlay deletion-target existence sweep: `C:/Temp/av-kit/native-picker-overlay-targets.json`
- Exact H1 vacuity comparison: `C:/Temp/av-kit/native-picker-h1-vacuity.json`
- Scope-basis census: `C:/Temp/av-kit/native-picker-scope-bases.txt`
- Production call-chain and packaging reads: `C:/Temp/av-kit/native-picker-callchain-search.txt` and `native-picker-source-trace.txt`
- Pre-edit canonical-path guard: `C:/Temp/av-kit/native-picker-pre-edit-guard.json`
- `git status --short` was attempted and failed because this workspace has no `.git` metadata; direct artifact state was used for PR-2 instead.

Primary-source checks:

- Electron issue #40515 confirms black/gray transparent windows on affected Windows systems with hardware acceleration.
- Microsoft Learn confirms WinForms trimming is disabled/incompatible, .NET 8 self-contained publishing must be explicit, and the current `ms-screenclip` response flow requires MSIX identity.
- Node.js filesystem documentation states that copy operations have no atomicity guarantee.

---

## Checklist Results

### Plan Review (PR)

| Check | Result | Evidence |
|-------|--------|----------|
| PR-1 Plan/task alignment | pass | Both artifacts describe MEU-40, WP/task order, native helper, total overlay deletion, SSOT revision, and the same handoff/review paths. |
| PR-2 Not-started confirmation | pass with evidence limitation | All 22 task rows are unchecked; native picker/new TS files and correlated implementation handoffs are absent; all eight old overlay targets still exist. `.git` metadata is absent, so diff history could not be inspected. |
| PR-3 Task contract completeness | pass | Every executable row has Task, Owner, Deliverable, Validation, dependency, lifecycle, durable output, and Status cells. |
| PR-4 Validation realism | fail | Findings 1, 2, 4, and 6 demonstrate false-passing or impossible validation paths. |
| PR-5 Source-backed planning | fail | Most ACs are correctly tagged, but `Spec (this plan)` is circular for atomicity and `P1 gates` is not an allowed source label. |
| PR-6 Handoff/corrections readiness | pass | First pass; canonical MEU handoff and rolling implementation-review paths are explicit. Corrections should run via `/plan-corrections`. |
| PR-7 Scope discipline | pass with correction note | No deferred rows exist. The no-fallback decision is USER_EXPLICIT; macOS/Linux and annotation exclusions match named canon; Python `mss`, REST, and MCP exclusions match the Phase 9 SSOT and approved MEU-35/37/38 records; WGC and `ms-screenclip` bases are source-backed. If cold-start acceptance was not explicit in the toolchain option text, the warm-daemon row needs a corrected Research-backed or Human-approved citation. |
| PR-8 Control reachability and totality | fail | Findings 1, 3, 4, 5, and 6 demonstrate missing production chains, missing negative oracles, or concrete false-pass controls. Open-world exit codes themselves are correctly specified to fail closed. |
| PR-9 Single-statement discipline | fail (clerical) | Findings 7 and 8 identify the repeated threshold and exit-code clusters. No materially conflicting spelling was found. |

### Documentation Review (DR)

| Check | Result | Evidence |
|-------|--------|----------|
| DR-1 Claim-to-state match | n/a | This is an unstarted plan, not a completed-change handoff. |
| DR-2 Residual old terms | pass for plan mode | The current old terms/paths exist as expected and the plan inventories their SSOT rewrite/deletion. |
| DR-3 Downstream references updated | pass in scope | Both governing build-plan files, hub audit, registry, Vite inputs, package metadata, builder resources, tests, and old overlay files are named. |
| DR-4 Verification robustness | fail | Findings 1, 3, 4, 5, and 6 can miss material regressions or missing deliverables. |
| DR-5 Evidence auditability | fail | Most commands are reproducible, but the central closeout executable is absent and RED receipts are not outcome-specific. |
| DR-6 Cross-reference integrity | pass subject to corrections | Proposed SSOT changes consistently preserve the Python/REST/MCP boundaries and replace only the Electron overlay/grab slot. |
| DR-7 Evidence freshness | n/a | No prior plan-review handoff or implementation evidence exists. |
| DR-8 Completion vs residual risk | pass | Neither target claims implementation completion. |

### Template Contract

| Check | Result | Evidence |
|-------|--------|----------|
| All AC have allowed source labels | fail | AC-40.15 says `P1 gates`; use `Local Canon`. |
| Validation cells are exact commands | fail | H2-4 is a placeholder description; Findings 1/2/6 cover material failures. |
| BUILD_PLAN audit row present | pass | Task row 8 and plan audit section are present. |
| Post-MEU rows present | pass | H1 handoff/review and H2 reflection/metrics/commit-draft rows are present and sequenced. |
| Naming and YAML frontmatter | pass | Folder/target/handoff naming is consistent and both YAML blocks parse structurally by inspection. |

---

## Open Questions / Assumptions

- The two USER_EXPLICIT decisions supplied with the review request were accepted as governing facts and were not reopened.
- This is treated as first-pass review because the canonical plan-review and implementation-review files were absent before this write.
- Not-started status is based on direct filesystem state because the provided workspace has no `.git` directory.
- The plan's `~5%` Electron incidence figure was treated as non-blocking because the architectural decision is independently USER_EXPLICIT and the linked issue supports the defect class, not the exact percentage.

## Follow-up Actions

Route corrections through `/plan-corrections` and, in the same correction pass:

1. Repair the H1 unchecked-row and RED-phase gates with demonstrated negative oracles.
2. Resolve the absent closeout-validator dependency before H1-6.
3. Bind native form events to tested controller/math/outcome controls.
4. Bind sidecar publish into the clean packaging entrypoint.
5. Replace copy-to-final with a real atomic publication mechanism and watcher-race test.
6. Deduplicate the threshold and exit-code contracts; align source/harness labels.

## Residual Risk

Even after plan correction, real WinForms behavior across DPI/multi-monitor configurations and packaged clean-machine execution will still require implementation-time automated coverage plus the planned live/packaged verification. Those are execution risks, not reasons to broaden the Python, REST, or MCP scope.

---

## Verdict

`changes_required` — six evidence-backed High findings show that executing the current plan can false-pass incomplete work, cannot run its mandatory closeout validator, can ship an unbuilt/stale sidecar, and does not bind key native/atomicity controls to production behavior. The Human-approved C# WinForms and delete-entirely decisions are correctly carried through; corrections should preserve them.

---

## Round 2 — Corrections Re-Review

### Intent Anchor

Executing this plan is intended to replace the Chromium capture overlay with a packaged .NET 8 WinForms region-picker sidecar while preserving the existing Python, REST, and MCP boundaries and proving deletion, packaging, publication, and closeout controls. Round 2 cannot determine whether the corrected plan would deliver that objective because the resubmission is missing the mandatory correction blast-radius evidence required before substantive re-review.

### Pre-Verdict Procedural Gate

`changes_required` under PR-6's procedural exception. The resubmission does not name an untruncated blast-radius census receipt for the Round 1 corrections, and it does not provide a correction log that assigns every census `file:line` hit an `updated` or `confirmed-consistent` disposition. The exact-path receipt search found only task-row verification receipts and the Round 2 prompt after the Round 1 review; no native-picker correction census or disposition log exists in that evidence set (`C:/Temp/av-kit/round2-native-picker-receipt-index.txt`). The plan-folder/review search likewise found no correction census or disposition record (`C:/Temp/av-kit/round2-pr6-census-search.txt`).

This is not a severity-rated finding. `.agent/workflows/plan-critical-review.md:256` and `:287-291` require a Round 2 `changes_required` verdict naming this precondition alone and prohibit review of the corrected content when the census is missing, truncated, or undispositioned.

### Round 1 Finding Resolution

The statuses below mean procedurally unresolved, not that the corrected text was found defective. Content adjudication was not permitted after the PR-6 gate failed.

| Finding | Round 2 status | File:line evidence |
|---------|----------------|--------------------|
| F1 — vacuous H1 unchecked-row gate | `unresolved` | Not adjudicated; required correction evidence absent per `.agent/workflows/plan-critical-review.md:256`. |
| F2 — phantom closeout validator | `unresolved` | Not adjudicated; required correction evidence absent per `.agent/workflows/plan-critical-review.md:256`. |
| F3 — no native control binding | `unresolved` | Not adjudicated; required correction evidence absent per `.agent/workflows/plan-critical-review.md:256`. |
| F4 — packaging entrypoint omits picker build | `unresolved` | Not adjudicated; required correction evidence absent per `.agent/workflows/plan-critical-review.md:256`. |
| F5 — non-atomic publication and circular source | `unresolved` | Not adjudicated; required correction evidence absent per `.agent/workflows/plan-critical-review.md:256`. |
| F6 — RED rows can exit green | `unresolved` | Not adjudicated; required correction evidence absent per `.agent/workflows/plan-critical-review.md:256`. |
| F7 — repeated minimum-edge threshold | `unresolved` | Not adjudicated; required correction evidence absent per `.agent/workflows/plan-critical-review.md:256`. |
| F8 — repeated exit-code mapping | `unresolved` | Not adjudicated; required correction evidence absent per `.agent/workflows/plan-critical-review.md:256`. |

### New Findings

No new severity-ranked findings were assessed. PR-6 is a pre-verdict procedural gate rather than a severity-rated finding, and the workflow forbids substantive corrected-content review after it fails.

### Checklist Verdicts

#### Plan Review (PR)

| Check | Result | Evidence |
|-------|--------|----------|
| PR-1 Plan/task alignment | not assessed | Substantive review stopped at PR-6. |
| PR-2 Not-started confirmation | not assessed | Substantive review stopped at PR-6. |
| PR-3 Task contract completeness | not assessed | Substantive review stopped at PR-6. |
| PR-4 Validation realism | not assessed | Gate semantics, AC totality, executable existence, and false-pass probes were not adjudicated this round. |
| PR-5 Source-backed planning | not assessed | Substantive review stopped at PR-6. |
| PR-6 Handoff/corrections readiness | **fail — pre-verdict gate** | No native-picker correction census receipt or per-hit disposition log was named or found; see `C:/Temp/av-kit/round2-native-picker-receipt-index.txt` and `C:/Temp/av-kit/round2-pr6-census-search.txt`. |
| PR-7 Scope discipline | not assessed | Out-of-scope bases were not re-adjudicated after the PR-6 stop. |
| PR-8 Control reachability and totality | not assessed | Control binding and negative-oracle claims were not re-adjudicated after the PR-6 stop. |
| PR-9 Single-statement discipline | not assessed | Named-set and repeated-literal claims were not re-adjudicated after the PR-6 stop. |

#### Documentation Review (DR)

| Check | Result | Evidence |
|-------|--------|----------|
| DR-1 Claim-to-state match | not assessed | Substantive review stopped at PR-6. |
| DR-2 Residual old terms | not assessed | Substantive review stopped at PR-6. |
| DR-3 Downstream references updated | not assessed | Substantive review stopped at PR-6. |
| DR-4 Verification robustness | not assessed | Substantive review stopped at PR-6. |
| DR-5 Evidence auditability | **fail** | The correction evidence needed to audit Round 2 is absent. |
| DR-6 Cross-reference integrity | not assessed | Substantive review stopped at PR-6. |
| DR-7 Evidence freshness | **fail** | No current native-picker blast-radius census and per-hit disposition log support the correction claims. |
| DR-8 Completion vs residual risk | pass | This Round 2 section does not claim the corrected plan is complete or approved. |

### Commands Executed

All command output was redirected to `C:/Temp/av-kit/`, with exit codes captured before receipt reads.

- Plan-folder and rolling-review inventory: `C:/Temp/av-kit/round2-inventory.txt`
- Resubmission census/log keyword sweep: `C:/Temp/av-kit/round2-pr6-census-search.txt`
- Correction-workflow and receipt-location check: `C:/Temp/av-kit/round2-pr6-location-check.txt`
- Candidate generic Round 2 receipt read, rejected as unrelated because it targets `p9-capture-gui`: `C:/Temp/av-kit/round2-pr6-evidence-read.txt`
- Exact native-picker receipt index after Round 1: `C:/Temp/av-kit/round2-native-picker-receipt-index.txt`
- Rolling review and PR-6 rule read: `C:/Temp/av-kit/round2-review-file-and-pr6-rule.txt`
- Canonical pre-edit target guard: `C:/Temp/av-kit/round2-pre-edit-guard.json`

### Follow-up Actions

1. Run the correction blast-radius census for every literal, term, count, set, threshold, and predicate changed for F1-F8, including declared semantic variants and both old/new forms where applicable.
2. Save the complete, untruncated raw census receipt under `C:/Temp/av-kit/`.
3. Append a correction log to this rolling review file that names the receipt and assigns every census `file:line` hit an `updated` or `confirmed-consistent` disposition; a summary count alone is insufficient.
4. Re-dispatch Round 2 after the PR-6 evidence is present. The next reviewer must then perform the requested F1-F8 recheck, AC_COUNT/AC_IDS totality check, executable-existence sweep, PR-7/PR-8/PR-9 analysis, and gate false-pass probes.

### Residual Risk

The correction claims remain unverified. This verdict makes no substantive statement about whether F1-F8 are fixed or whether the corrected gates can false-pass; it records only that the evidence required to begin that determination is missing.

### Verdict

`changes_required` — Round 2 fails the mandatory PR-6 blast-radius-census precondition. Findings count is zero because this is the workflow's procedural exception, not a severity-rated content finding.

---

## Round 2 Corrections — Blast-Radius Census & Disposition Log

> Implementor-authored evidence appended to satisfy the Round 2 pre-verdict PR-6 gate.
> This section makes no verdict claim; it supplies the census and correction log that
> Round 2 Follow-up Actions 1–3 require before content review may resume.

### Census receipt

- **Receipt (complete, untruncated):** `C:/Temp/av-kit/census-p9-native-picker-round1-corrections.txt` — 922 lines, script exit `0`.
- **Sweep script (re-runnable):** `docs/execution/plans/2026-08-27-p9-capture-native-picker/census-round1-corrections.ps1`
- **Method:** `rg -F -n --no-heading --with-filename` (fixed-string, so regex metacharacters in a value cannot silently change what was searched). No `head`, `tail`, `Select-Object`, or `Where-Object` appears anywhere in the sweep or in the receipt.
- **Coverage:** 64 declared values × 2 scopes = **128 sweeps**. Scope `PAIR` = `implementation-plan.md` + `task.md` (the pair Step 5c mandates); scope `FOLDER` = every file in the plan folder, because `named-sets.json` and the `assert-*.ps1` gates are themselves part of the correction and must agree with the prose. `FOLDER` is a superset of `PAIR`, so the log below enumerates `FOLDER` hits; the receipt carries both.
- **Directions:** every changed literal, term, count, set, threshold, and predicate was swept in **both** directions — the *old* form (to find sites the correction missed) and the *new* form (to confirm the edit landed). Declared semantic variants are listed as separate values, because a fixed-string sweep cannot find a prose, set-literal, or predicate spelling of the same rule.
- **Exit codes:** worst `rg` exit code across all 128 sweeps = `0`. No sweep returned `>1`, so no sweep failed to execute. `rc=1` on an *old*-form sweep is the intended result (stale text fully removed).
- **Total hits dispositioned below: 262** — every `file:line` in the receipt's `FOLDER` scope.

### Disposition key

- `updated` — the line was written or rewritten by the round-1 correction pass.
- `confirmed-consistent` — the line was not changed by the correction pass and was read at its cited location to confirm it agrees with the corrected rule. Every `confirmed-consistent` hit that is not a census-declaration line carries an explicit justification.

### Old-form sweeps returning no match (stale text removed)

These values returned `rc=1` in the `PAIR` scope: the pre-correction text no longer exists in
the plan or task file. Their only `FOLDER` hits are the census declaration table itself.

| Finding | Old form swept | PAIR result |
|---|---|---|
| F1 | `\| .[ ].$` | `rc=1` no match |
| F1 | `unchecked=` | `rc=1` no match |
| F2 | `validate_closeout_artifacts` | `rc=1` no match |
| F2 | `--review-state-only` | `rc=1` no match |
| F2 | `--approved-state-only` | `rc=1` no match |
| F4 | `dotnet publish native/region-picker` | `rc=1` no match |
| F4 | `run one real publish` | `rc=1` no match |
| F5 | `os.tmpdir` | `rc=1` no match |
| F5 | `temp-file lifecycle` | `rc=1` no match |
| F5 | `Spec (this plan)` | `rc=1` no match |
| F6 | `exit 0` (red` | `rc=1` no match |
| F6 | `end `exit 0`` | `rc=1` no match |
| F7 | `min-edge 8` | `rc=1` no match |
| F7 | `8 px` | `rc=1` no match |
| F7 | `8-pixel` | `rc=1` no match |
| F8 | `argv -> exit 1` | `rc=1` no match |
| F8 | `cancel -> 2` | `rc=1` no match |
| F8 | `confirm -> 0` | `rc=1` no match |
| X1-builder-model | `opus-5` | `rc=1` no match |
| X1-builder-model | `sonnet-5` | `rc=1` no match |
| X2-openapi | `git status --porcelain packages/api` | `rc=1` no match |
| X2-openapi | `OpenAPI Drift Check` | `rc=1` no match |
| X4-harness | `Harness: Claude Code` | `rc=1` no match |

### Full per-hit disposition table

| Finding | Dir | Value | file:line | Disposition | Note |
|---|---|---|---|---|---|
| F1 | old | `\| .[ ].$` | `census-round1-corrections.ps1:25` | `confirmed-consistent` | census declaration table (the sweep's own input list), not a plan assertion |
| F1 | old | `unchecked=` | `census-round1-corrections.ps1:26` | `confirmed-consistent` | census declaration table (the sweep's own input list), not a plan assertion |
| F1 | new | `assert-task-rows.ps1` | `assert-closeout.ps1:19` | `updated` | file created by the correction pass |
| F1 | new | `assert-task-rows.ps1` | `assert-oracle-selftests.ps1:7` | `updated` | file created by the correction pass |
| F1 | new | `assert-task-rows.ps1` | `task.md:52` | `updated` | line written or rewritten by the correction pass |
| F1 | new | `assert-task-rows.ps1` | `implementation-plan.md:102` | `updated` | line written or rewritten by the correction pass |
| F1 | new | `assert-task-rows.ps1` | `implementation-plan.md:281` | `updated` | line written or rewritten by the correction pass |
| F1 | new | `assert-task-rows.ps1` | `census-round1-corrections.ps1:27` | `confirmed-consistent` | census declaration table (the sweep's own input list), not a plan assertion |
| F1 | new | `TASK_ROW_GATE` | `assert-closeout.ps1:19` | `updated` | file created by the correction pass |
| F1 | new | `TASK_ROW_GATE` | `assert-oracle-selftests.ps1:7` | `updated` | file created by the correction pass |
| F1 | new | `TASK_ROW_GATE` | `census-round1-corrections.ps1:28` | `confirmed-consistent` | census declaration table (the sweep's own input list), not a plan assertion |
| F1 | new | `TASK_ROW_GATE` | `assert-task-rows.ps1:52` | `updated` | file created by the correction pass |
| F1 | new | `TASK_ROW_GATE` | `assert-task-rows.ps1:62` | `updated` | file created by the correction pass |
| F1 | new | `TASK_ROW_GATE` | `assert-task-rows.ps1:67` | `updated` | file created by the correction pass |
| F1 | new | `TASK_ROW_GATE` | `assert-task-rows.ps1:70` | `updated` | file created by the correction pass |
| F1 | new | `TASK_ROW_GATE` | `implementation-plan.md:102` | `updated` | line written or rewritten by the correction pass |
| F2 | old | `validate_closeout_artifacts` | `assert-closeout.ps1:3` | `confirmed-consistent` | header comment recording that the phantom validator was replaced; line 3 is a `#` comment, and every path actually invoked (L18-32) is on disk |
| F2 | old | `validate_closeout_artifacts` | `census-round1-corrections.ps1:30` | `confirmed-consistent` | census declaration table (the sweep's own input list), not a plan assertion |
| F2 | old | `--review-state-only` | `census-round1-corrections.ps1:31` | `confirmed-consistent` | census declaration table (the sweep's own input list), not a plan assertion |
| F2 | old | `--approved-state-only` | `census-round1-corrections.ps1:32` | `confirmed-consistent` | census declaration table (the sweep's own input list), not a plan assertion |
| F2 | new | `assert-closeout.ps1` | `census-round1-corrections.ps1:33` | `confirmed-consistent` | census declaration table (the sweep's own input list), not a plan assertion |
| F2 | new | `assert-closeout.ps1` | `implementation-plan.md:109` | `updated` | line written or rewritten by the correction pass |
| F2 | new | `assert-closeout.ps1` | `implementation-plan.md:281` | `updated` | line written or rewritten by the correction pass |
| F2 | new | `assert-closeout.ps1` | `task.md:65` | `updated` | line written or rewritten by the correction pass |
| F2 | new | `check_exec_review.py` | `task.md:60` | `updated` | line written or rewritten by the correction pass |
| F2 | new | `check_exec_review.py` | `implementation-plan.md:108` | `updated` | line written or rewritten by the correction pass |
| F2 | new | `check_exec_review.py` | `census-round1-corrections.ps1:34` | `confirmed-consistent` | census declaration table (the sweep's own input list), not a plan assertion |
| F2 | new | `check_exec_review.py` | `assert-closeout.ps1:27` | `updated` | file created by the correction pass |
| F2 | new | `check_exec_review.py` | `assert-closeout.ps1:32` | `updated` | file created by the correction pass |
| F2 | new | `assert-handoff-markers.ps1` | `task.md:57` | `updated` | line written or rewritten by the correction pass |
| F2 | new | `assert-handoff-markers.ps1` | `implementation-plan.md:107` | `updated` | line written or rewritten by the correction pass |
| F2 | new | `assert-handoff-markers.ps1` | `implementation-plan.md:281` | `updated` | line written or rewritten by the correction pass |
| F2 | new | `assert-handoff-markers.ps1` | `census-round1-corrections.ps1:35` | `confirmed-consistent` | census declaration table (the sweep's own input list), not a plan assertion |
| F2 | new | `assert-handoff-markers.ps1` | `assert-closeout.ps1:23` | `updated` | file created by the correction pass |
| F2 | new | `assert-handoff-acs.ps1` | `task.md:58` | `updated` | line written or rewritten by the correction pass |
| F2 | new | `assert-handoff-acs.ps1` | `implementation-plan.md:107` | `updated` | line written or rewritten by the correction pass |
| F2 | new | `assert-handoff-acs.ps1` | `implementation-plan.md:281` | `updated` | line written or rewritten by the correction pass |
| F2 | new | `assert-handoff-acs.ps1` | `census-round1-corrections.ps1:36` | `confirmed-consistent` | census declaration table (the sweep's own input list), not a plan assertion |
| F2 | new | `assert-handoff-acs.ps1` | `assert-closeout.ps1:24` | `updated` | file created by the correction pass |
| F2 | new | `assert-exec-review-dispatch.ps1` | `assert-closeout.ps1:25` | `updated` | file created by the correction pass |
| F2 | new | `assert-exec-review-dispatch.ps1` | `task.md:60` | `updated` | line written or rewritten by the correction pass |
| F2 | new | `assert-exec-review-dispatch.ps1` | `task.md:82` | `updated` | line written or rewritten by the correction pass |
| F2 | new | `assert-exec-review-dispatch.ps1` | `implementation-plan.md:108` | `updated` | line written or rewritten by the correction pass |
| F2 | new | `assert-exec-review-dispatch.ps1` | `implementation-plan.md:281` | `updated` | line written or rewritten by the correction pass |
| F2 | new | `assert-exec-review-dispatch.ps1` | `census-round1-corrections.ps1:37` | `confirmed-consistent` | census declaration table (the sweep's own input list), not a plan assertion |
| F3 | new | `PickerController` | `task.md:43` | `updated` | line written or rewritten by the correction pass |
| F3 | new | `PickerController` | `task.md:44` | `updated` | line written or rewritten by the correction pass |
| F3 | new | `PickerController` | `named-sets.json:26` | `updated` | line written or rewritten by the correction pass |
| F3 | new | `PickerController` | `named-sets.json:61` | `updated` | line written or rewritten by the correction pass |
| F3 | new | `PickerController` | `implementation-plan.md:171` | `updated` | line written or rewritten by the correction pass |
| F3 | new | `PickerController` | `implementation-plan.md:215` | `updated` | line written or rewritten by the correction pass |
| F3 | new | `PickerController` | `implementation-plan.md:216` | `updated` | line written or rewritten by the correction pass |
| F3 | new | `PickerController` | `implementation-plan.md:260` | `updated` | line written or rewritten by the correction pass |
| F3 | new | `PickerController` | `implementation-plan.md:261` | `updated` | line written or rewritten by the correction pass |
| F3 | new | `PickerController` | `implementation-plan.md:265` | `updated` | line written or rewritten by the correction pass |
| F3 | new | `PickerController` | `census-round1-corrections.ps1:39` | `confirmed-consistent` | census declaration table (the sweep's own input list), not a plan assertion |
| F3 | new | `PickerController` | `assert-picker-binding.ps1:3` | `updated` | file created by the correction pass |
| F3 | new | `PickerController` | `assert-picker-binding.ps1:39` | `updated` | file created by the correction pass |
| F3 | new | `RectMath` | `task.md:43` | `updated` | line written or rewritten by the correction pass |
| F3 | new | `RectMath` | `task.md:44` | `updated` | line written or rewritten by the correction pass |
| F3 | new | `RectMath` | `assert-picker-binding.ps1:87` | `updated` | file created by the correction pass |
| F3 | new | `RectMath` | `assert-picker-binding.ps1:88` | `updated` | file created by the correction pass |
| F3 | new | `RectMath` | `named-sets.json:27` | `updated` | line written or rewritten by the correction pass |
| F3 | new | `RectMath` | `named-sets.json:60` | `updated` | line written or rewritten by the correction pass |
| F3 | new | `RectMath` | `implementation-plan.md:171` | `updated` | line written or rewritten by the correction pass |
| F3 | new | `RectMath` | `implementation-plan.md:211` | `updated` | line written or rewritten by the correction pass |
| F3 | new | `RectMath` | `implementation-plan.md:212` | `updated` | line written or rewritten by the correction pass |
| F3 | new | `RectMath` | `implementation-plan.md:213` | `updated` | line written or rewritten by the correction pass |
| F3 | new | `RectMath` | `implementation-plan.md:215` | `updated` | line written or rewritten by the correction pass |
| F3 | new | `RectMath` | `implementation-plan.md:216` | `updated` | line written or rewritten by the correction pass |
| F3 | new | `RectMath` | `implementation-plan.md:261` | `updated` | line written or rewritten by the correction pass |
| F3 | new | `RectMath` | `implementation-plan.md:262` | `updated` | line written or rewritten by the correction pass |
| F3 | new | `RectMath` | `implementation-plan.md:264` | `updated` | line written or rewritten by the correction pass |
| F3 | new | `RectMath` | `census-round1-corrections.ps1:40` | `confirmed-consistent` | census declaration table (the sweep's own input list), not a plan assertion |
| F3 | new | `Program.Run` | `task.md:43` | `updated` | line written or rewritten by the correction pass |
| F3 | new | `Program.Run` | `implementation-plan.md:215` | `updated` | line written or rewritten by the correction pass |
| F3 | new | `Program.Run` | `implementation-plan.md:266` | `updated` | line written or rewritten by the correction pass |
| F3 | new | `Program.Run` | `census-round1-corrections.ps1:41` | `confirmed-consistent` | census declaration table (the sweep's own input list), not a plan assertion |
| F3 | new | `IPickerDialog` | `task.md:43` | `updated` | line written or rewritten by the correction pass |
| F3 | new | `IPickerDialog` | `task.md:44` | `updated` | line written or rewritten by the correction pass |
| F3 | new | `IPickerDialog` | `implementation-plan.md:215` | `updated` | line written or rewritten by the correction pass |
| F3 | new | `IPickerDialog` | `implementation-plan.md:259` | `updated` | line written or rewritten by the correction pass |
| F3 | new | `IPickerDialog` | `census-round1-corrections.ps1:42` | `confirmed-consistent` | census declaration table (the sweep's own input list), not a plan assertion |
| F3 | new | `assert-picker-binding.ps1` | `task.md:45` | `updated` | line written or rewritten by the correction pass |
| F3 | new | `assert-picker-binding.ps1` | `implementation-plan.md:105` | `updated` | line written or rewritten by the correction pass |
| F3 | new | `assert-picker-binding.ps1` | `implementation-plan.md:216` | `updated` | line written or rewritten by the correction pass |
| F3 | new | `assert-picker-binding.ps1` | `implementation-plan.md:281` | `updated` | line written or rewritten by the correction pass |
| F3 | new | `assert-picker-binding.ps1` | `implementation-plan.md:348` | `updated` | line written or rewritten by the correction pass |
| F3 | new | `assert-picker-binding.ps1` | `census-round1-corrections.ps1:43` | `confirmed-consistent` | census declaration table (the sweep's own input list), not a plan assertion |
| F3 | new | `assert-picker-binding.ps1` | `assert-oracle-selftests.ps1:11` | `updated` | file created by the correction pass |
| F3 | new | `assert-picker-binding.ps1` | `assert-closeout.ps1:21` | `updated` | file created by the correction pass |
| F3 | new | `AC-40.16` | `task.md:43` | `updated` | line written or rewritten by the correction pass |
| F3 | new | `AC-40.16` | `named-sets.json:89` | `updated` | line written or rewritten by the correction pass |
| F3 | new | `AC-40.16` | `implementation-plan.md:215` | `updated` | line written or rewritten by the correction pass |
| F3 | new | `AC-40.16` | `implementation-plan.md:265` | `updated` | line written or rewritten by the correction pass |
| F3 | new | `AC-40.16` | `implementation-plan.md:266` | `updated` | line written or rewritten by the correction pass |
| F3 | new | `AC-40.16` | `census-round1-corrections.ps1:44` | `confirmed-consistent` | census declaration table (the sweep's own input list), not a plan assertion |
| F3 | new | `AC-40.17` | `task.md:45` | `updated` | line written or rewritten by the correction pass |
| F3 | new | `AC-40.17` | `named-sets.json:90` | `updated` | line written or rewritten by the correction pass |
| F3 | new | `AC-40.17` | `implementation-plan.md:216` | `updated` | line written or rewritten by the correction pass |
| F3 | new | `AC-40.17` | `census-round1-corrections.ps1:45` | `confirmed-consistent` | census declaration table (the sweep's own input list), not a plan assertion |
| F3 | new | `AC-40.17` | `assert-picker-binding.ps1:1` | `updated` | file created by the correction pass |
| F4 | old | `dotnet publish native/region-picker` | `census-round1-corrections.ps1:47` | `confirmed-consistent` | census declaration table (the sweep's own input list), not a plan assertion |
| F4 | old | `run one real publish` | `census-round1-corrections.ps1:48` | `confirmed-consistent` | census declaration table (the sweep's own input list), not a plan assertion |
| F4 | new | `assert-packaging-clean.ps1` | `task.md:46` | `updated` | line written or rewritten by the correction pass |
| F4 | new | `assert-packaging-clean.ps1` | `implementation-plan.md:106` | `updated` | line written or rewritten by the correction pass |
| F4 | new | `assert-packaging-clean.ps1` | `implementation-plan.md:222` | `updated` | line written or rewritten by the correction pass |
| F4 | new | `assert-packaging-clean.ps1` | `implementation-plan.md:281` | `updated` | line written or rewritten by the correction pass |
| F4 | new | `assert-packaging-clean.ps1` | `implementation-plan.md:327` | `updated` | line written or rewritten by the correction pass |
| F4 | new | `assert-packaging-clean.ps1` | `census-round1-corrections.ps1:49` | `confirmed-consistent` | census declaration table (the sweep's own input list), not a plan assertion |
| F4 | new | `assert-packaging-clean.ps1` | `assert-closeout.ps1:22` | `updated` | file created by the correction pass |
| F4 | new | `build:picker` | `task.md:46` | `updated` | line written or rewritten by the correction pass |
| F4 | new | `build:picker` | `named-sets.json:19` | `updated` | line written or rewritten by the correction pass |
| F4 | new | `build:picker` | `implementation-plan.md:222` | `updated` | line written or rewritten by the correction pass |
| F4 | new | `build:picker` | `implementation-plan.md:275` | `updated` | line written or rewritten by the correction pass |
| F4 | new | `build:picker` | `census-round1-corrections.ps1:50` | `confirmed-consistent` | census declaration table (the sweep's own input list), not a plan assertion |
| F4 | new | `build:picker` | `assert-packaging-clean.ps1:20` | `updated` | file created by the correction pass |
| F4 | new | `PICKER_DIST_SCRIPT` | `named-sets.json:20` | `updated` | line written or rewritten by the correction pass |
| F4 | new | `PICKER_DIST_SCRIPT` | `census-round1-corrections.ps1:51` | `confirmed-consistent` | census declaration table (the sweep's own input list), not a plan assertion |
| F4 | new | `PICKER_DIST_SCRIPT` | `assert-packaging-clean.ps1:14` | `updated` | file created by the correction pass |
| F5 | old | `copyFile` | `implementation-plan.md:218` | `confirmed-consistent` | deliberate negative oracle - AC-40.6 fails if a spy sees `writeFile`/`copyFile` target the final name; this is the inverse of the removed non-atomic copy, not a surviving instance of it |
| F5 | old | `copyFile` | `implementation-plan.md:381` | `confirmed-consistent` | the Research-backed Node `fs` citation that justifies `renameSync`; naming the rejected API is the point of the source line |
| F5 | old | `copyFile` | `census-round1-corrections.ps1:53` | `confirmed-consistent` | census declaration table (the sweep's own input list), not a plan assertion |
| F5 | old | `os.tmpdir` | `census-round1-corrections.ps1:54` | `confirmed-consistent` | census declaration table (the sweep's own input list), not a plan assertion |
| F5 | old | `temp-file lifecycle` | `census-round1-corrections.ps1:55` | `confirmed-consistent` | census declaration table (the sweep's own input list), not a plan assertion |
| F5 | old | `Spec (this plan)` | `census-round1-corrections.ps1:56` | `confirmed-consistent` | census declaration table (the sweep's own input list), not a plan assertion |
| F5 | new | `renameSync` | `task.md:48` | `updated` | line written or rewritten by the correction pass |
| F5 | new | `renameSync` | `implementation-plan.md:176` | `updated` | line written or rewritten by the correction pass |
| F5 | new | `renameSync` | `implementation-plan.md:218` | `updated` | line written or rewritten by the correction pass |
| F5 | new | `renameSync` | `implementation-plan.md:247` | `updated` | line written or rewritten by the correction pass |
| F5 | new | `renameSync` | `implementation-plan.md:381` | `updated` | line written or rewritten by the correction pass |
| F5 | new | `renameSync` | `census-round1-corrections.ps1:57` | `confirmed-consistent` | census declaration table (the sweep's own input list), not a plan assertion |
| F5 | new | `PICKER_STAGING_PREFIX` | `task.md:48` | `updated` | line written or rewritten by the correction pass |
| F5 | new | `PICKER_STAGING_PREFIX` | `named-sets.json:23` | `updated` | line written or rewritten by the correction pass |
| F5 | new | `PICKER_STAGING_PREFIX` | `implementation-plan.md:174` | `updated` | line written or rewritten by the correction pass |
| F5 | new | `PICKER_STAGING_PREFIX` | `implementation-plan.md:273` | `updated` | line written or rewritten by the correction pass |
| F5 | new | `PICKER_STAGING_PREFIX` | `census-round1-corrections.ps1:58` | `confirmed-consistent` | census declaration table (the sweep's own input list), not a plan assertion |
| F5 | new | `.avkit-staging-` | `named-sets.json:23` | `updated` | line written or rewritten by the correction pass |
| F5 | new | `.avkit-staging-` | `census-round1-corrections.ps1:59` | `confirmed-consistent` | census declaration table (the sweep's own input list), not a plan assertion |
| F5 | new | `shouldNotifyInboxChange` | `task.md:47` | `updated` | line written or rewritten by the correction pass |
| F5 | new | `shouldNotifyInboxChange` | `task.md:48` | `updated` | line written or rewritten by the correction pass |
| F5 | new | `shouldNotifyInboxChange` | `implementation-plan.md:218` | `updated` | line written or rewritten by the correction pass |
| F5 | new | `shouldNotifyInboxChange` | `implementation-plan.md:273` | `updated` | line written or rewritten by the correction pass |
| F5 | new | `shouldNotifyInboxChange` | `census-round1-corrections.ps1:60` | `confirmed-consistent` | census declaration table (the sweep's own input list), not a plan assertion |
| F6 | old | `exit 0` (red` | `census-round1-corrections.ps1:62` | `confirmed-consistent` | census declaration table (the sweep's own input list), not a plan assertion |
| F6 | old | `end `exit 0`` | `census-round1-corrections.ps1:63` | `confirmed-consistent` | census declaration table (the sweep's own input list), not a plan assertion |
| F6 | new | `assert-red-oracle.ps1` | `task.md:43` | `updated` | line written or rewritten by the correction pass |
| F6 | new | `assert-red-oracle.ps1` | `task.md:47` | `updated` | line written or rewritten by the correction pass |
| F6 | new | `assert-red-oracle.ps1` | `task.md:85` | `updated` | line written or rewritten by the correction pass |
| F6 | new | `assert-red-oracle.ps1` | `implementation-plan.md:103` | `updated` | line written or rewritten by the correction pass |
| F6 | new | `assert-red-oracle.ps1` | `implementation-plan.md:281` | `updated` | line written or rewritten by the correction pass |
| F6 | new | `assert-red-oracle.ps1` | `implementation-plan.md:320` | `updated` | line written or rewritten by the correction pass |
| F6 | new | `assert-red-oracle.ps1` | `census-round1-corrections.ps1:64` | `confirmed-consistent` | census declaration table (the sweep's own input list), not a plan assertion |
| F6 | new | `assert-red-oracle.ps1` | `assert-oracle-selftests.ps1:8` | `updated` | file created by the correction pass |
| F6 | new | `assert-red-oracle.ps1` | `assert-oracle-selftests.ps1:9` | `updated` | file created by the correction pass |
| F6 | new | `-Suite dotnet` | `task.md:43` | `updated` | line written or rewritten by the correction pass |
| F6 | new | `-Suite dotnet` | `census-round1-corrections.ps1:65` | `confirmed-consistent` | census declaration table (the sweep's own input list), not a plan assertion |
| F6 | new | `-Suite vitest` | `task.md:47` | `updated` | line written or rewritten by the correction pass |
| F6 | new | `-Suite vitest` | `census-round1-corrections.ps1:66` | `confirmed-consistent` | census declaration table (the sweep's own input list), not a plan assertion |
| F6 | new | `RED_DOTNET_SIGNATURES` | `named-sets.json:59` | `updated` | line written or rewritten by the correction pass |
| F6 | new | `RED_DOTNET_SIGNATURES` | `census-round1-corrections.ps1:67` | `confirmed-consistent` | census declaration table (the sweep's own input list), not a plan assertion |
| F6 | new | `RED_DOTNET_SIGNATURES` | `assert-red-oracle.ps1:16` | `updated` | file created by the correction pass |
| F6 | new | `RED_VITEST_SIGNATURES` | `named-sets.json:66` | `updated` | line written or rewritten by the correction pass |
| F6 | new | `RED_VITEST_SIGNATURES` | `census-round1-corrections.ps1:68` | `confirmed-consistent` | census declaration table (the sweep's own input list), not a plan assertion |
| F6 | new | `RED_VITEST_SIGNATURES` | `assert-red-oracle.ps1:19` | `updated` | file created by the correction pass |
| F7 | old | `min-edge 8` | `census-round1-corrections.ps1:70` | `confirmed-consistent` | census declaration table (the sweep's own input list), not a plan assertion |
| F7 | old | `minimum edge` | `implementation-plan.md:141` | `confirmed-consistent` | prose names the constant (`minimum edge PICKER_MIN_EDGE_PX`); no numeric literal is duplicated at this site |
| F7 | old | `minimum edge` | `census-round1-corrections.ps1:71` | `confirmed-consistent` | census declaration table (the sweep's own input list), not a plan assertion |
| F7 | old | `8 px` | `census-round1-corrections.ps1:72` | `confirmed-consistent` | census declaration table (the sweep's own input list), not a plan assertion |
| F7 | old | `8-pixel` | `census-round1-corrections.ps1:73` | `confirmed-consistent` | census declaration table (the sweep's own input list), not a plan assertion |
| F7 | new | `PICKER_MIN_EDGE_PX` | `task.md:41` | `updated` | line written or rewritten by the correction pass |
| F7 | new | `PICKER_MIN_EDGE_PX` | `task.md:44` | `updated` | line written or rewritten by the correction pass |
| F7 | new | `PICKER_MIN_EDGE_PX` | `named-sets.json:11` | `updated` | line written or rewritten by the correction pass |
| F7 | new | `PICKER_MIN_EDGE_PX` | `implementation-plan.md:141` | `updated` | line written or rewritten by the correction pass |
| F7 | new | `PICKER_MIN_EDGE_PX` | `implementation-plan.md:156` | `updated` | line written or rewritten by the correction pass |
| F7 | new | `PICKER_MIN_EDGE_PX` | `implementation-plan.md:157` | `updated` | line written or rewritten by the correction pass |
| F7 | new | `PICKER_MIN_EDGE_PX` | `implementation-plan.md:159` | `updated` | line written or rewritten by the correction pass |
| F7 | new | `PICKER_MIN_EDGE_PX` | `implementation-plan.md:206` | `updated` | line written or rewritten by the correction pass |
| F7 | new | `PICKER_MIN_EDGE_PX` | `implementation-plan.md:212` | `updated` | line written or rewritten by the correction pass |
| F7 | new | `PICKER_MIN_EDGE_PX` | `census-round1-corrections.ps1:74` | `confirmed-consistent` | census declaration table (the sweep's own input list), not a plan assertion |
| F8 | old | `argv -> exit 1` | `census-round1-corrections.ps1:76` | `confirmed-consistent` | census declaration table (the sweep's own input list), not a plan assertion |
| F8 | old | `cancel -> 2` | `census-round1-corrections.ps1:77` | `confirmed-consistent` | census declaration table (the sweep's own input list), not a plan assertion |
| F8 | old | `confirm -> 0` | `census-round1-corrections.ps1:78` | `confirmed-consistent` | census declaration table (the sweep's own input list), not a plan assertion |
| F8 | new | `PICKER_EXIT_CONFIRM` | `census-round1-corrections.ps1:79` | `confirmed-consistent` | census declaration table (the sweep's own input list), not a plan assertion |
| F8 | new | `PICKER_EXIT_CONFIRM` | `implementation-plan.md:157` | `updated` | line written or rewritten by the correction pass |
| F8 | new | `PICKER_EXIT_CONFIRM` | `implementation-plan.md:175` | `updated` | line written or rewritten by the correction pass |
| F8 | new | `PICKER_EXIT_CONFIRM` | `implementation-plan.md:215` | `updated` | line written or rewritten by the correction pass |
| F8 | new | `PICKER_EXIT_CONFIRM` | `implementation-plan.md:217` | `updated` | line written or rewritten by the correction pass |
| F8 | new | `PICKER_EXIT_CONFIRM` | `named-sets.json:12` | `updated` | line written or rewritten by the correction pass |
| F8 | new | `PICKER_EXIT_CANCEL` | `named-sets.json:14` | `updated` | line written or rewritten by the correction pass |
| F8 | new | `PICKER_EXIT_CANCEL` | `implementation-plan.md:159` | `updated` | line written or rewritten by the correction pass |
| F8 | new | `PICKER_EXIT_CANCEL` | `implementation-plan.md:217` | `updated` | line written or rewritten by the correction pass |
| F8 | new | `PICKER_EXIT_CANCEL` | `implementation-plan.md:220` | `updated` | line written or rewritten by the correction pass |
| F8 | new | `PICKER_EXIT_CANCEL` | `census-round1-corrections.ps1:80` | `confirmed-consistent` | census declaration table (the sweep's own input list), not a plan assertion |
| F8 | new | `PICKER_EXIT_ERROR` | `named-sets.json:13` | `updated` | line written or rewritten by the correction pass |
| F8 | new | `PICKER_EXIT_ERROR` | `implementation-plan.md:158` | `updated` | line written or rewritten by the correction pass |
| F8 | new | `PICKER_EXIT_ERROR` | `implementation-plan.md:214` | `updated` | line written or rewritten by the correction pass |
| F8 | new | `PICKER_EXIT_ERROR` | `implementation-plan.md:217` | `updated` | line written or rewritten by the correction pass |
| F8 | new | `PICKER_EXIT_ERROR` | `census-round1-corrections.ps1:81` | `confirmed-consistent` | census declaration table (the sweep's own input list), not a plan assertion |
| F8 | new | `PICKER_EXIT_*` | `task.md:41` | `updated` | line written or rewritten by the correction pass |
| F8 | new | `PICKER_EXIT_*` | `task.md:44` | `updated` | line written or rewritten by the correction pass |
| F8 | new | `PICKER_EXIT_*` | `task.md:48` | `updated` | line written or rewritten by the correction pass |
| F8 | new | `PICKER_EXIT_*` | `implementation-plan.md:166` | `updated` | line written or rewritten by the correction pass |
| F8 | new | `PICKER_EXIT_*` | `implementation-plan.md:206` | `updated` | line written or rewritten by the correction pass |
| F8 | new | `PICKER_EXIT_*` | `implementation-plan.md:214` | `updated` | line written or rewritten by the correction pass |
| F8 | new | `PICKER_EXIT_*` | `implementation-plan.md:215` | `updated` | line written or rewritten by the correction pass |
| F8 | new | `PICKER_EXIT_*` | `implementation-plan.md:259` | `updated` | line written or rewritten by the correction pass |
| F8 | new | `PICKER_EXIT_*` | `implementation-plan.md:266` | `updated` | line written or rewritten by the correction pass |
| F8 | new | `PICKER_EXIT_*` | `census-round1-corrections.ps1:82` | `confirmed-consistent` | census declaration table (the sweep's own input list), not a plan assertion |
| X1-builder-model | old | `opus-5` | `census-round1-corrections.ps1:85` | `confirmed-consistent` | census declaration table (the sweep's own input list), not a plan assertion |
| X1-builder-model | old | `sonnet-5` | `census-round1-corrections.ps1:86` | `confirmed-consistent` | census declaration table (the sweep's own input list), not a plan assertion |
| X2-openapi | old | `git status --porcelain packages/api` | `census-round1-corrections.ps1:87` | `confirmed-consistent` | census declaration table (the sweep's own input list), not a plan assertion |
| X2-openapi | old | `OpenAPI Drift Check` | `census-round1-corrections.ps1:88` | `confirmed-consistent` | census declaration table (the sweep's own input list), not a plan assertion |
| X2-openapi | new | `export_openapi.py --check openapi.committed.json` | `task.md:55` | `updated` | line written or rewritten by the correction pass |
| X2-openapi | new | `export_openapi.py --check openapi.committed.json` | `census-round1-corrections.ps1:89` | `confirmed-consistent` | census declaration table (the sweep's own input list), not a plan assertion |
| X2-openapi | new | `export_openapi.py --check openapi.committed.json` | `implementation-plan.md:365` | `updated` | line written or rewritten by the correction pass |
| X3-ac-totality | new | `AC_COUNT` | `task.md:58` | `updated` | line written or rewritten by the correction pass |
| X3-ac-totality | new | `AC_COUNT` | `named-sets.json:72` | `updated` | line written or rewritten by the correction pass |
| X3-ac-totality | new | `AC_COUNT` | `implementation-plan.md:107` | `updated` | line written or rewritten by the correction pass |
| X3-ac-totality | new | `AC_COUNT` | `census-round1-corrections.ps1:90` | `confirmed-consistent` | census declaration table (the sweep's own input list), not a plan assertion |
| X3-ac-totality | new | `AC_COUNT` | `assert-handoff-acs.ps1:2` | `updated` | file created by the correction pass |
| X3-ac-totality | new | `AC_COUNT` | `assert-handoff-acs.ps1:9` | `updated` | file created by the correction pass |
| X3-ac-totality | new | `AC_COUNT` | `assert-handoff-acs.ps1:17` | `updated` | file created by the correction pass |
| X3-ac-totality | new | `AC_IDS` | `task.md:58` | `updated` | line written or rewritten by the correction pass |
| X3-ac-totality | new | `AC_IDS` | `named-sets.json:73` | `updated` | line written or rewritten by the correction pass |
| X3-ac-totality | new | `AC_IDS` | `census-round1-corrections.ps1:91` | `confirmed-consistent` | census declaration table (the sweep's own input list), not a plan assertion |
| X3-ac-totality | new | `AC_IDS` | `assert-handoff-acs.ps1:3` | `updated` | file created by the correction pass |
| X3-ac-totality | new | `AC_IDS` | `assert-handoff-acs.ps1:10` | `updated` | file created by the correction pass |
| X3-ac-totality | new | `AC_IDS` | `assert-handoff-acs.ps1:21` | `updated` | file created by the correction pass |
| X4-harness | old | `Harness: Claude Code` | `census-round1-corrections.ps1:92` | `confirmed-consistent` | census declaration table (the sweep's own input list), not a plan assertion |
| X4-harness | new | `plan_to_exec_gate` | `task.md:32` | `updated` | line written or rewritten by the correction pass |
| X4-harness | new | `plan_to_exec_gate` | `implementation-plan.md:84` | `updated` | line written or rewritten by the correction pass |
| X4-harness | new | `plan_to_exec_gate` | `implementation-plan.md:85` | `updated` | line written or rewritten by the correction pass |
| X4-harness | new | `plan_to_exec_gate` | `census-round1-corrections.ps1:93` | `confirmed-consistent` | census declaration table (the sweep's own input list), not a plan assertion |
| X5-row-ids | new | `\| 4a \|` | `task.md:45` | `updated` | line written or rewritten by the correction pass |
| X5-row-ids | new | `\| 4a \|` | `task.md:46` | `updated` | line written or rewritten by the correction pass |
| X5-row-ids | new | `\| 4a \|` | `census-round1-corrections.ps1:94` | `confirmed-consistent` | census declaration table (the sweep's own input list), not a plan assertion |
| X5-row-ids | new | `\| 4a \|` | `assert-task-rows.ps1:33` | `updated` | file created by the correction pass |
| X5-row-ids | new | `\| 0 \|` | `task.md:40` | `updated` | line written or rewritten by the correction pass |
| X5-row-ids | new | `\| 0 \|` | `task.md:41` | `updated` | line written or rewritten by the correction pass |
| X5-row-ids | new | `\| 0 \|` | `census-round1-corrections.ps1:95` | `confirmed-consistent` | census declaration table (the sweep's own input list), not a plan assertion |
| X6-selftests | new | `assert-oracle-selftests.ps1` | `task.md:40` | `updated` | line written or rewritten by the correction pass |
| X6-selftests | new | `assert-oracle-selftests.ps1` | `implementation-plan.md:97` | `updated` | line written or rewritten by the correction pass |
| X6-selftests | new | `assert-oracle-selftests.ps1` | `implementation-plan.md:281` | `updated` | line written or rewritten by the correction pass |
| X6-selftests | new | `assert-oracle-selftests.ps1` | `implementation-plan.md:317` | `updated` | line written or rewritten by the correction pass |
| X6-selftests | new | `assert-oracle-selftests.ps1` | `census-round1-corrections.ps1:96` | `confirmed-consistent` | census declaration table (the sweep's own input list), not a plan assertion |
| X6-selftests | new | `assert-oracle-selftests.ps1` | `assert-closeout.ps1:18` | `updated` | file created by the correction pass |
| X6-selftests | new | `-SelfTest` | `task.md:40` | `updated` | line written or rewritten by the correction pass |
| X6-selftests | new | `-SelfTest` | `task.md:80` | `updated` | line written or rewritten by the correction pass |
| X6-selftests | new | `-SelfTest` | `implementation-plan.md:97` | `updated` | line written or rewritten by the correction pass |
| X6-selftests | new | `-SelfTest` | `implementation-plan.md:216` | `updated` | line written or rewritten by the correction pass |
| X6-selftests | new | `-SelfTest` | `implementation-plan.md:221` | `updated` | line written or rewritten by the correction pass |
| X6-selftests | new | `-SelfTest` | `implementation-plan.md:281` | `updated` | line written or rewritten by the correction pass |
| X6-selftests | new | `-SelfTest` | `census-round1-corrections.ps1:97` | `confirmed-consistent` | census declaration table (the sweep's own input list), not a plan assertion |
| X6-selftests | new | `-SelfTest` | `assert-task-rows.ps1:2` | `updated` | file created by the correction pass |
| X6-selftests | new | `-SelfTest` | `assert-picker-binding.ps1:5` | `updated` | file created by the correction pass |
| X6-selftests | new | `-SelfTest` | `assert-overlay-deleted.ps1:2` | `confirmed-consistent` | pre-existing gate the correction did not touch; verified to use the same convention |
| X6-selftests | new | `-SelfTest` | `assert-oracle-selftests.ps1:7` | `updated` | file created by the correction pass |
| X6-selftests | new | `-SelfTest` | `assert-oracle-selftests.ps1:8` | `updated` | file created by the correction pass |
| X6-selftests | new | `-SelfTest` | `assert-oracle-selftests.ps1:9` | `updated` | file created by the correction pass |
| X6-selftests | new | `-SelfTest` | `assert-oracle-selftests.ps1:10` | `updated` | file created by the correction pass |
| X6-selftests | new | `-SelfTest` | `assert-oracle-selftests.ps1:11` | `updated` | file created by the correction pass |

**Rows in table: 262** — equal to the receipt's `FOLDER`-scope hit count. No hit is omitted, grouped away, or replaced by a summary count.

### The four `confirmed-consistent` hits that survive an *old*-form sweep

A surviving old-form hit is exactly the case PR-6 exists to catch, so each is justified individually rather than counted:

- `validate_closeout_artifacts` matched at `assert-closeout.ps1:3` — header comment recording that the phantom validator was replaced; line 3 is a `#` comment, and every path actually invoked (L18-32) is on disk.
- `copyFile` matched at `implementation-plan.md:218` — deliberate negative oracle - AC-40.6 fails if a spy sees `writeFile`/`copyFile` target the final name; this is the inverse of the removed non-atomic copy, not a surviving instance of it.
- `copyFile` matched at `implementation-plan.md:381` — the Research-backed Node `fs` citation that justifies `renameSync`; naming the rejected API is the point of the source line.
- `minimum edge` matched at `implementation-plan.md:141` — prose names the constant (`minimum edge PICKER_MIN_EDGE_PX`); no numeric literal is duplicated at this site.

No other old-form value matched anywhere in the plan pair.

---

## Round 3 — Corrections Re-Review

### Intent Anchor

Executing this plan is supposed to replace the Chromium capture overlay with a packaged .NET 8 WinForms region-picker sidecar, bind the tested native controls and clean packaging path to production, publish completed PNGs atomically, and preserve the existing Python, REST, and MCP boundaries. The current plan still cannot deliver that objective through its own task sequence: the closeout row gate is unsatisfiable when scheduled, and the native-binding and packaging controls accept concrete production paths that omit the required behavior.

### PR-6 Evidence Adjudication

The Round 2 pre-verdict gate is satisfied. The supplied receipt exists, has 922 lines, ends with `64 x 2 scopes = 128 sweeps` and worst exit code `0`, and a fresh rerun also produced 922 lines and exit `0`. The two receipts have the same complete line multiset; only `rg` traversal order differs. Exact reconciliation found 262 `FOLDER` hits, 262 correction-log rows, zero invalid dispositions, and zero multiset delta. The four non-declaration hits surviving old-form sweeps reproduce exactly as documented: `assert-closeout.ps1:3`, `implementation-plan.md:218`, `implementation-plan.md:381`, and `implementation-plan.md:141`.

That evidence is sufficient to clear PR-6's procedural stop and permits substantive review in this round. It does not make the census complete by assertion: Round 3 Finding N5 records a concrete under-declaration (`BINDING_HANDLERS` and the `_controller.` / `BINDING_DELEGATION_TOKEN` predicate added for F3 were not declared among the 64 values), as the user directed for an under-declared changed set.

### Round 1 Finding Resolution

| Finding | Disposition | Current-file evidence |
|---------|-------------|-----------------------|
| F1 — vacuous H1 unchecked-row gate | `partially_resolved` | `assert-task-rows.ps1:12-21` now recognizes numeric, suffixed (`4a`), H1, and H2 rows; `:24-56` has a valid synthetic oracle, and the live run reports 24/24 rows open. However, `task.md:52` schedules the zero-open check at H1-1 while H1-1 and every later row are necessarily open; `assert-closeout.ps1:19` repeats it at H2-4 while H2-4/H2-5 remain open. The probe records 13 and 2 unavoidable open rows respectively. See N1. |
| F2 — phantom closeout validator | `resolved` | `assert-closeout.ps1:18-32` invokes only on-disk `assert-*.ps1`, `tools/check_exec_review.py`, and `tools/meu_status.py`; the executable audit confirmed every invoked real path exists. No invocation of the phantom Python validator survives. |
| F3 — no native control binding | `partially_resolved` | The plan now defines `RegionForm -> PickerController -> RectMath` and `Program.Run(args, IPickerDialog)` (`implementation-plan.md:171`, `:215-216`) with xunit work in `task.md:43-45`. But `assert-picker-binding.ps1:17-33` requires only an arbitrary `_controller.` token per handler, and `:77-90` never proves `Main -> Run -> RegionForm`. The exact probe shows all handlers incorrectly calling `BeginDrag` still pass. See N2. |
| F4 — packaging entrypoint omits picker build | `partially_resolved` | AC-40.10 and task row 5 now require `dist` composition (`implementation-plan.md:222`; `task.md:46`), and the gate checks both resource strings. But `assert-packaging-clean.ps1:33-35` uses substring containment and `:46-60` rebuilds by invoking `$buildScript` directly at line 55, never `$distScript`. `echo build:picker && electron-builder ...` passes the predicate while omitting the build. See N3. |
| F5 — non-atomic copy and circular source | `resolved` | `implementation-plan.md:173-184`, `:218`, and `:247` stage inside the inbox, inspect the staged file, publish only through same-directory `renameSync`, ignore staging names, and use Research-backed rather than circular sourcing. Official Node documentation confirms copy has no atomicity guarantee; Microsoft documents cross-volume move as the case that falls back to copy/delete. |
| F6 — RED rows end green | `resolved` | `task.md:43`, `:47`, and `:85` preserve the suite code, pass it to `assert-red-oracle.ps1`, and exit with the gate code. `assert-red-oracle.ps1:22-34` rejects green, absent/empty, and missing-signature receipts; `:37-55` self-tests those failures. Both suite self-tests passed in Round 3. |
| F7 — repeated minimum-edge threshold | `resolved` | The normative value is defined under `PICKER_MIN_EDGE_PX` at `implementation-plan.md:150-160`, mirrored by the executable owner at `named-sets.json:11`, and AC/task prose references the name. No conflicting live value was found. |
| F8 — repeated exit-code mapping | `resolved` | The normative `PICKER_EXIT_*` table is at `implementation-plan.md:150-160`, mirrored at `named-sets.json:12-14`; AC/task prose refers to the constant names and the open-world fallback fails closed. No conflicting mapping was found. |

### Round 3 Findings

| # | Severity | Finding | File:Line | Required correction |
|---|----------|---------|-----------|---------------------|
| N1 | High | **PR-4 / PR-8 — the corrected task-row gate deadlocks the declared sequence.** H1-1 cannot prove zero open rows before completing itself or the 12 later rows; H2-4 cannot prove zero open rows before completing itself and H2-5. Evidence-first rules prohibit pre-marking either row complete. This is a new, materially different F1 correction failure: non-vacuous but unsatisfiable. | `task.md:52`, `task.md:61-66`; `assert-task-rows.ps1:59-70`; `assert-closeout.ps1:18-22`; `C:/Temp/av-kit/review-r3-adversarial-probes.json` | Make H1-1 validate an explicit predecessor set (implementation rows only), excluding the current/future rows. Put the final all-row completion check after all task work or give it an explicit, self-tested allowance for the currently executing final row; never require a row's own `[x]` before its validation succeeds. |
| N2 | High | **PR-8 — `PICKER_BINDING` still false-passes a dead production chain.** The gate accepts any `_controller.` call in each named handler, not the required method mapping, and performs no `Program.Main -> Program.Run -> RegionForm/IPickerDialog` reachability check. A form where MouseMove, MouseUp, and KeyDown all call `BeginDrag` passes, while release/Enter/Esc cannot produce the tested outcomes; an unused tested `Run` seam also passes. | `implementation-plan.md:171`, `implementation-plan.md:215-216`; `assert-picker-binding.ps1:17-33`, `assert-picker-binding.ps1:77-90`; `C:/Temp/av-kit/review-r3-adversarial-probes.json` | Bind each handler to its required controller method and bind the executable entrypoint to `Run` with the real dialog. Add negative self-tests for wrong-method delegation and an unused `Run` seam, not only a missing `_controller.` token. |
| N3 | High | **PR-4 / PR-8 — `PACKAGING_CLEAN_PATH` does not execute the production packaging path it claims to prove.** It string-searches `dist` for `build:picker`, deletes the publish directory, then runs `build:picker` directly. The demonstrated `dist = "echo build:picker && electron-builder ..."` passes both the substring predicate and direct rebuild while clean `npm run dist` still omits the sidecar build. | `implementation-plan.md:222`; `task.md:46`; `assert-packaging-clean.ps1:20-37`, `assert-packaging-clean.ps1:46-60`; `C:/Temp/av-kit/review-r3-adversarial-probes.json` | After emptying the publish directory, invoke the actual production `dist` entrypoint (or a structurally registered packaging-prep entrypoint that `dist` invokes and the gate itself executes). Reject comments/echo/substrings that do not execute the build. |
| N4 | High | **PR-4 / PR-8 — mandatory real-Electron Playwright coverage is omitted, and the manual smoke has no validation evidence path.** Project canon requires a Playwright test under `ui/tests/e2e/` for runtime GUI behavior; no-display may block the run, but the test must still be written and wired. The plan instead preserves an `AVKIT_E2E` no-spawn short-circuit, schedules only xunit/vitest, and relies on an eyeballed smoke whose task validation/durable outputs contain only typecheck/lint receipts. Thus the F2/IPC -> real Electron -> picker/register/refresh path can be missing while every scheduled automated gate passes. | `AGENTS.md:241`; `.agent/docs/testing-strategy.md:47-48`; `implementation-plan.md:223`, `implementation-plan.md:356-359`; `task.md:47-50`; Files Modified `implementation-plan.md:249-281` | Add and wire a real-Electron Playwright test under `ui/tests/e2e/` that exercises the capture trigger through the production Electron path (using a deterministic sidecar fixture/env override where needed) and asserts publication/register/refresh. If Electron cannot launch, retain the test and record the run as `[B]` with the required receipt/follow-up. Add the smoke/latency disposition to row 9's durable evidence. |
| N5 | Low | **PR-6 census coverage is under-declared for the F3 correction.** The correction introduced the executable `BINDING_HANDLERS` set and `_controller.` / `BINDING_DELEGATION_TOKEN` predicate, but none is a declared census value. The 262-row ledger is complete for the declared values, not for every changed predicate/set claimed by the evidence header. | `named-sets.json:28-45`; `assert-picker-binding.ps1:11-15`; `census-round1-corrections.ps1:23-98`; `C:/Temp/av-kit/review-r3-pr6-coverage.txt` | Add old/new sweeps for the exact binding set and predicate names/values, then append per-hit dispositions to the existing log. This is clerical/evidence coverage and is not independently blocking. |
| N6 | Low | **PR-3 / PR-4 exact-command paths are not literal executables.** `PLAN/...` is documented as an abbreviation, but PowerShell does not expand it; `Test-Path PLAN/assert-oracle-selftests.ps1` is false. Rows 8 and H1-2 also reference another section instead of containing a directly runnable command. The intended real files exist, so this is clerical under the Materiality Gate. | `task.md:35-36`, `task.md:40`, `task.md:43`, `task.md:45-48`, `task.md:49`, `task.md:52-65`; `C:/Temp/av-kit/review-r3-executable-audit.txt` | Replace every `PLAN/...` token with the real repo-relative plan-folder path (or define an executable variable inside each command), and inline the exact row 8/H1-2 commands. |
| N7 | Low | **PR-7 labeling defect: the warm-process row is `deferred` without a registered MEU-ID.** Its research-backed basis substantively excludes it from the current contract, so this is not disguised missing work and does not block; however, `filed from row 9 if measured` is not a MEU present in `meu-status.yaml`. | `implementation-plan.md:287-295` | Relabel it `out-of-scope` on the existing basis, or name a real registered MEU if it is genuinely deferred. |

No Critical findings were identified.

### Checklist Verdicts

| Check | Result | Evidence |
|-------|--------|----------|
| PR-1 Plan/task alignment | pass | Both artifacts describe MEU-40, WP/task order, WinForms sidecar, overlay deletion, atomic publication, packaging, and the same handoff/review paths. |
| PR-2 Not-started confirmation | pass | All 24 actionable rows are unchecked; `native/region-picker`, `native/region-picker-tests`, `capture-picker.ts`, the MEU handoff, and implementation-review handoff are absent; all eight old overlay files remain. |
| PR-3 Task contract completeness | pass with Low note | Every actionable row has task, owner, deliverable, validation, dependencies/context, durable outputs, builder model, and status. N6 covers command literalness. |
| PR-4 Validation realism | **fail** | N1, N3, and N4 demonstrate an impossible gate, a packaging false-pass, and omitted mandatory E2E evidence. |
| PR-5 Source-backed planning | pass | All 17 ACs use allowed `Spec`, `Local Canon`, `Research-backed`, or `Human-approved` bases; the F5 circular source was removed. |
| PR-6 Handoff/corrections readiness | pass pre-verdict; Low coverage finding | The 922-line receipt and 262-row ledger reconcile exactly. N5 records the under-declared binding set/predicate as a substantive Low finding per the Round 3 prompt, not another procedural stop. |
| PR-7 Scope discipline | pass with Low note | macOS/Linux, annotation, Python/MCP, REST/MCP, WGC, and Snipping Tool rows have real bases. N7 is a labeling defect, not disguised current-scope work. |
| PR-8 Control reachability and totality | **fail** | N1-N4 provide concrete deadlock/dead-end/false-pass scenarios. Exit-code open-world classification and F5 publication fail closed. |
| PR-9 Single-statement discipline | pass | F7/F8 values agree between the single normative contract and executable named-set mirror; all other prose uses names and no materially conflicting spelling remains. |
| DR-1 Claim-to-state match | **fail** | The F1/F3/F4 correction claims overstate what the current gates prove; N1-N3 show the mismatch. |
| DR-2 Residual old terms | pass | Exactly four non-declaration old-form hits survive, each for the documented consistent reason; no other old form remains in the plan pair. |
| DR-3 Downstream references updated | pass in plan scope | Specs, registry, Vite inputs, package/builder config, old overlay files, tests, hub audit, handoff, review, reflection, and metrics are inventoried. |
| DR-4 Verification robustness | **fail** | N1-N4 show controls that cannot run in sequence or can miss material regressions/deliverables. |
| DR-5 Evidence auditability | pass with Low notes | Receipts, scripts, paths, counts, and probes are reproducible; N5/N6 identify the remaining census/command-form defects. |
| DR-6 Cross-reference integrity | pass | The plan consistently keeps Python `mss`, REST, and MCP surfaces unchanged while revising only the Electron/native picker slot. |
| DR-7 Evidence freshness | pass | The census rerun reproduced 922 lines/exit 0; AC table vs `AC_COUNT`/`AC_IDS` is 17/17 with zero delta; receipt/log is 262/262 with zero delta. |
| DR-8 Completion vs residual risk | pass | The target remains draft/unstarted and does not claim implementation completion. |

### Commands Executed

All shell work used redirected receipts under `C:/Temp/av-kit/` with exit codes captured before receipt reads. Key evidence:

- PR-6 rerun/reconciliation: `review-r3-census-reproduced.txt`, `review-r3-census-multiset.txt`, `review-r3-pr6-log-audit.txt`, `review-r3-pr6-coverage.txt`.
- Gate reads and self-tests: `review-r3-gates-a.txt`, `review-r3-gates-b.txt`, `review-r3-oracle-selftests.txt`, `review-r3-task-row-live.txt`.
- Adversarial counterexamples: `review-r3-adversarial-probes.json`.
- AC/executable/not-started audits: `review-r3-ac-totality.json`, `review-r3-executable-audit.txt`, `review-r3-not-started.txt`.
- Scope/E2E canon: `review-r3-pr7-bases.txt`, `review-r3-e2e-canon.txt`.
- Primary-source check: official Node `fs` documentation (`copyFile` atomicity disclaimer; `renameSync`) and Microsoft `MoveFileEx` documentation (cross-volume copy fallback).

`assert-packaging-clean.ps1` was not run without `-SkipBuild`, as required. No implementation, product, test, plan, or other handoff file was modified.

### Follow-up Actions

Because Round 3 is the plan-review cap, these are correction requirements for human-directed next steps, not an autonomous Round 4 loop:

1. Repair the H1/H2 task-row sequence so predecessor completeness is provable without requiring the current/future rows to be closed.
2. Make `PICKER_BINDING` method-specific and bind `Main -> Run -> real RegionForm`; add the two adversarial self-tests from N2.
3. Make the clean-path oracle execute the production packaging entrypoint, not `build:picker` directly plus a substring test.
4. Add/wire the mandatory real-Electron Playwright capture-path test and evidence-gate row 9's live-smoke/latency disposition.
5. Correct the Low PR-6 census, exact-command, and PR-7 labeling defects in N5-N7.

### Open Questions / Assumptions

No product decision is needed to state these defects or their required outcomes. The existing Human-approved decisions (C# WinForms and delete the Chromium overlay entirely) remain governing and are not reopened. Because this is the third-round cap, any correction/resubmission requires explicit human direction.

### Residual Risk

After correction, actual WinForms behavior across DPI/multi-monitor configurations and packaged clean-machine execution will still require the planned xunit/vitest, real-Electron Playwright, packaging, and live/CI receipts. Those are execution risks; they do not justify weakening the current plan gates or expanding Python, REST, or MCP scope.

### Verdict

`changes_required` — PR-6's procedural evidence is sufficient and F2/F5/F6/F7/F8 are resolved, but four evidence-backed High findings remain: the F1 correction deadlocks the task sequence, F3's control-binding gate accepts a nonfunctional production chain, F4's packaging gate never exercises the production `dist` path, and mandatory real-Electron Playwright coverage is omitted. Round 3 is the cap, so this verdict is a **HARD STOP requiring human direction**; no autonomous correction or further review round is authorized.

---

## Round 3 Corrections — Blast-Radius Census & Disposition Log

> Implementor-authored evidence appended under explicit human direction
> (`USER_EXPLICIT`: "continue until approved") after the Round 3 `changes_required`
> HARD STOP. This section makes no verdict claim; it supplies the PR-6 census and
> per-hit correction log that a Round 4 review requires before content review resumes.

### What was corrected (Round 3 findings N1–N7)

| # | Finding | Correction landed |
|---|---|---|
| N1 | Task-row gate deadlocks (demanded zero open rows while the row running it is open) | `assert-task-rows.ps1` now proves **predecessor completeness** via a mandatory `-Through <rowId>`; the boundary row and its successors may be open. All vacuity guards kept (zero matched rows, unknown boundary id, empty predecessor set each fail), plus self-test **T3**, which proves an open boundary/successor does *not* block. |
| N2 | `PICKER_BINDING` was token-presence, so a production chain that never reaches the tested seam passed | `BINDING_HANDLER_METHODS` maps each handler to **its own** controller method (`OnMouseDown`→`BeginDrag`, `OnMouseMove`→`UpdateDrag`, `OnMouseUp`→`EndDrag`, `OnKeyDown`→`KeyDown`), and `Main` must reach `Run(… new RegionForm(…))` in one statement. Both reviewer probes are now self-tests: **B2** (all four handlers calling `BeginDrag`) and **E2** (a `Run` seam `Main` never calls). |
| N3 | Packaging gate matched substrings and rebuilt via `build:picker` directly, never the production `dist` path | `assert-packaging-clean.ps1` splits each script body on `&&` and requires the **exact** segments `npm run dist:prep` (in `dist`) and `npm run build:picker` (in `dist:prep`); the clean rebuild now executes the production `npm --prefix ui run dist:prep`. Self-tests **P1** (`echo dist:prep && …`), **P2** (hollow prep), **P3** (uncomposed `dist`), **P4** (missing script). |
| N4 | Mandatory real-Electron Playwright coverage omitted; row 9's live smoke had no durable evidence | New **AC-40.18** (real-Electron capture path: F2/IPC → real spawn → pixel guard → rename publication → register → filmstrip, plus the cancel and all-black negatives) and **AC-40.19** (wiring + smoke disposition); new task rows **7a** and **9**; two new gates, `assert-e2e-wired.ps1` and `assert-smoke-disposition.ps1`. A no-UI console stub (`native/region-picker-stub`) makes the sidecar leg deterministic and display-free. The repo-wide `AVKIT_E2E` short-circuit is made **conditional** on `AVKIT_REGION_PICKER_PATH` rather than deleted, because all ten existing E2E specs depend on it. |
| N5 | Round-3 census / disposition log not yet produced | This section, backed by `census-round3-corrections.ps1` (below). |
| N6 | H1-2's "validation" was prose, and the Verification Plan section list was duplicated | `run-verification-plan.ps1` is now the **single executable owner** of the 13-section list; the plan links to it and names only receipts. Every `PLAN/` abbreviation was replaced with the literal folder path, and row 8's command was inlined. |
| N7 | Warm-process row labeled `deferred` without a registered MEU-ID | Relabeled `out-of-scope` / `—` on the existing Research-backed basis; row 9's measured `LATENCY_MS` is the trigger for proposing a *new* MEU from evidence. |

### Census receipt

- **Receipt (complete, untruncated):** `C:/Temp/av-kit/census-p9-native-picker-round3-corrections.txt` — 1,082 lines, script exit `0`.
- **Sweep script (re-runnable):** `docs/execution/plans/2026-08-27-p9-capture-native-picker/census-round3-corrections.ps1`
- **Method:** `rg -F -n --no-heading --with-filename` (fixed-string, so regex metacharacters in a value cannot silently change what was searched). No `head`, `tail`, `Select-Object`, or `Where-Object` appears anywhere in the sweep or in the receipt.
- **Coverage:** 72 declared values × 2 scopes = **144 sweeps**. Scope `PAIR` = `implementation-plan.md` + `task.md`; scope `FOLDER` = every file in the plan folder, because `named-sets.json`, the `assert-*.ps1` gates, and `run-verification-plan.ps1` are themselves part of the correction and must agree with the prose. `FOLDER` is a superset of `PAIR`, so the log below enumerates `FOLDER` hits; the receipt carries both.
- **Directions:** every changed literal, term, count, set, threshold, and predicate was swept in **three** declared directions — `old` (find sites the correction missed), `new` (confirm the edit landed), and `carry` (a value not changed this round but load-bearing for a round-3 rule, swept so the corrected rule is confirmed against every existing site).
- **Exit codes:** worst `rg` exit code across all 144 sweeps = `0`; no sweep returned `>1`, so none failed to execute.
- **Self-enforcing:** the sweep script **exits 3** if any `old` form survives outside a census declaration table or the declared retained-mention allowlist. The run above exits `0` with `STALE SITES: 0`, and that stale path is not hypothetical: the first run exited `3` on `task.md:50` — a false positive, because `npm --prefix ui run build:picker` is a prefix of the N4 stub command `npm --prefix ui run build:picker-stub`. The old value was narrowed to the exact removed source line `npm --prefix ui run $buildScript` and the rerun is clean.
- **Total hits dispositioned below: 485** — every `file:line` in the receipt's `FOLDER` scope.

### Disposition key

- `updated` — the line was written by the round-3 correction pass. For a `new`-direction value this is provable rather than asserted: the value did not exist anywhere before this pass, so any occurrence outside a census declaration table is necessarily on a line the pass wrote.
- `confirmed-consistent` — the line was not changed by the correction pass and was read at its cited location to confirm it agrees with the corrected rule. Three cases, each carrying its justification in the table: census declaration lines (the sweep's own input list), `carry` values (pre-existing and still correct), and the one declared **retained mention** below.

### Old-form sweeps (stale text removed)

| Finding | Old form swept | PAIR result |
|---|---|---|
| N1 | `zero unchecked rows` | `rc=1` no match |
| N1 | `no unchecked rows remain` | `rc=1` no match |
| N1 | `every row is closed` | `rc=1` no match |
| N2 | `BINDING_HANDLERS` | `rc=1` no match |
| N2 | `BINDING_TOKEN` | `rc=1` no match |
| N3 | `PICKER_DIST_REQUIRED_TOKEN` | `rc=1` no match |
| N3 | `npm --prefix ui run $buildScript` | `rc=1` no match |
| N6 | `PLAN/` | `rc=1` no match |
| N6 | `Exact commands from implementation-plan.md` | `rc=1` no match |
| N7 | `deferred` | `rc=0` 1 hit(s) — see retained-mention note |
| X7-ac-count | `"AC_COUNT": 17` | `rc=1` no match |
| X7-ac-count | `17 ACs` | `rc=1` no match |

**Retained mention (the single non-zero `old` result).** `implementation-plan.md:295` still
contains the word `deferred`, deliberately: the Out-of-Scope row explains *why* the warm-process
row is labeled `out-of-scope` rather than `deferred` (no registered MEU-ID exists). Quoting the
rejected label is finding N7's resolution, not a residue of it. It is declared in the sweep
script's `$RetainedMentions` allowlist, so the gate does not silently tolerate it.

### Gate self-test and inventory receipts (re-run after the corrections)

| Receipt | Result |
|---|---|
| `C:/Temp/av-kit/oracle-selftests.txt` | `PASS: ORACLE_SELFTESTS 8 gates proven non-vacuous` — exit `0`. T1–T5 (task rows), red oracle × 2, overlay deletion, B1–B3/E1–E2 (binding), P1–P4 (packaging), S1–S3/G1–G2 (E2E wiring), D1–D5 (smoke disposition). |
| `C:/Temp/av-kit/verification-plan-inventory.txt` | `PASS: VERIFICATION_PLAN inventory (13 sections, every gate script present)` — exit `0`. |
| `C:/Temp/av-kit/census-p9-native-picker-round3-corrections.txt` | `STALE SITES: 0` — exit `0`, 1,082 lines. |

> One defect was found *by* re-running the oracles rather than by inspection: `Get-TaskRows`
> returned `,@($out.ToArray())`, which the `@(...)` call sites collected as a single nested
> array, so self-test **T1** saw `rows=1` instead of `4` and failed. The comma-wrap was removed
> and the suite is green. The gate was never trusted while it was red.

### Per-hit disposition log (485 rows, nothing dropped)

| Finding | Dir | Value | Site (`file:line`) | Disposition | Justification |
|---|---|---|---|---|---|
| N1 | old | `zero unchecked rows` | `census-round3-corrections.ps1:47` | `confirmed-consistent` | census declaration table (the sweep's own input list), not a plan assertion |
| N1 | old | `no unchecked rows remain` | `census-round3-corrections.ps1:48` | `confirmed-consistent` | census declaration table (the sweep's own input list), not a plan assertion |
| N1 | old | `every row is closed` | `census-round3-corrections.ps1:49` | `confirmed-consistent` | census declaration table (the sweep's own input list), not a plan assertion |
| N1 | new | `-Through` | `task.md:54` | `updated` | the value did not exist before the round-3 pass, so this line was written by that pass |
| N1 | new | `-Through` | `task.md:67` | `updated` | the value did not exist before the round-3 pass, so this line was written by that pass |
| N1 | new | `-Through` | `task.md:83` | `updated` | the value did not exist before the round-3 pass, so this line was written by that pass |
| N1 | new | `-Through` | `census-round3-corrections.ps1:50` | `confirmed-consistent` | census declaration table (the sweep's own input list), not a plan assertion |
| N1 | new | `-Through` | `census-round3-corrections.ps1:51` | `confirmed-consistent` | census declaration table (the sweep's own input list), not a plan assertion |
| N1 | new | `-Through` | `census-round3-corrections.ps1:52` | `confirmed-consistent` | census declaration table (the sweep's own input list), not a plan assertion |
| N1 | new | `-Through` | `assert-task-rows.ps1:8` | `updated` | the value did not exist before the round-3 pass, so this line was written by that pass |
| N1 | new | `-Through` | `assert-task-rows.ps1:10` | `updated` | the value did not exist before the round-3 pass, so this line was written by that pass |
| N1 | new | `-Through` | `assert-task-rows.ps1:132` | `updated` | the value did not exist before the round-3 pass, so this line was written by that pass |
| N1 | new | `-Through` | `assert-closeout.ps1:21` | `updated` | the value did not exist before the round-3 pass, so this line was written by that pass |
| N1 | new | `-Through H1-1` | `task.md:54` | `updated` | the value did not exist before the round-3 pass, so this line was written by that pass |
| N1 | new | `-Through H1-1` | `census-round3-corrections.ps1:51` | `confirmed-consistent` | census declaration table (the sweep's own input list), not a plan assertion |
| N1 | new | `-Through H2-4` | `task.md:67` | `updated` | the value did not exist before the round-3 pass, so this line was written by that pass |
| N1 | new | `-Through H2-4` | `census-round3-corrections.ps1:52` | `confirmed-consistent` | census declaration table (the sweep's own input list), not a plan assertion |
| N1 | new | `ROW_BOUNDARY_H1` | `named-sets.json:107` | `updated` | the value did not exist before the round-3 pass, so this line was written by that pass |
| N1 | new | `ROW_BOUNDARY_H1` | `census-round3-corrections.ps1:53` | `confirmed-consistent` | census declaration table (the sweep's own input list), not a plan assertion |
| N1 | new | `ROW_BOUNDARY_CLOSEOUT` | `named-sets.json:108` | `updated` | the value did not exist before the round-3 pass, so this line was written by that pass |
| N1 | new | `ROW_BOUNDARY_CLOSEOUT` | `census-round3-corrections.ps1:54` | `confirmed-consistent` | census declaration table (the sweep's own input list), not a plan assertion |
| N1 | new | `ROW_BOUNDARY_CLOSEOUT` | `assert-closeout.ps1:21` | `updated` | the value did not exist before the round-3 pass, so this line was written by that pass |
| N1 | new | `Measure-Predecessors` | `census-round3-corrections.ps1:55` | `confirmed-consistent` | census declaration table (the sweep's own input list), not a plan assertion |
| N1 | new | `Measure-Predecessors` | `assert-task-rows.ps1:45` | `updated` | the value did not exist before the round-3 pass, so this line was written by that pass |
| N1 | new | `Measure-Predecessors` | `assert-task-rows.ps1:97` | `updated` | the value did not exist before the round-3 pass, so this line was written by that pass |
| N1 | new | `Measure-Predecessors` | `assert-task-rows.ps1:112` | `updated` | the value did not exist before the round-3 pass, so this line was written by that pass |
| N1 | new | `Measure-Predecessors` | `assert-task-rows.ps1:117` | `updated` | the value did not exist before the round-3 pass, so this line was written by that pass |
| N1 | new | `Measure-Predecessors` | `assert-task-rows.ps1:121` | `updated` | the value did not exist before the round-3 pass, so this line was written by that pass |
| N1 | new | `Measure-Predecessors` | `assert-task-rows.ps1:136` | `updated` | the value did not exist before the round-3 pass, so this line was written by that pass |
| N1 | new | `openRequired` | `census-round3-corrections.ps1:56` | `confirmed-consistent` | census declaration table (the sweep's own input list), not a plan assertion |
| N1 | new | `openRequired` | `assert-task-rows.ps1:44` | `updated` | the value did not exist before the round-3 pass, so this line was written by that pass |
| N1 | new | `openRequired` | `assert-task-rows.ps1:54` | `updated` | the value did not exist before the round-3 pass, so this line was written by that pass |
| N1 | new | `openRequired` | `assert-task-rows.ps1:59` | `updated` | the value did not exist before the round-3 pass, so this line was written by that pass |
| N1 | new | `openRequired` | `assert-task-rows.ps1:60` | `updated` | the value did not exist before the round-3 pass, so this line was written by that pass |
| N1 | new | `openRequired` | `assert-task-rows.ps1:100` | `updated` | the value did not exist before the round-3 pass, so this line was written by that pass |
| N1 | new | `openRequired` | `assert-task-rows.ps1:113` | `updated` | the value did not exist before the round-3 pass, so this line was written by that pass |
| N1 | new | `openRequired` | `assert-task-rows.ps1:149` | `updated` | the value did not exist before the round-3 pass, so this line was written by that pass |
| N1 | new | `openRequired` | `assert-task-rows.ps1:151` | `updated` | the value did not exist before the round-3 pass, so this line was written by that pass |
| N1 | new | `predecessor completeness` | `task.md:83` | `updated` | the value did not exist before the round-3 pass, so this line was written by that pass |
| N1 | new | `predecessor completeness` | `census-round3-corrections.ps1:57` | `confirmed-consistent` | census declaration table (the sweep's own input list), not a plan assertion |
| N1 | carry | `assert-task-rows.ps1` | `assert-closeout.ps1:21` | `confirmed-consistent` | pre-existing value, read at the cited line: it agrees with the corrected round-3 rule |
| N1 | carry | `assert-task-rows.ps1` | `task.md:54` | `confirmed-consistent` | pre-existing value, read at the cited line: it agrees with the corrected round-3 rule |
| N1 | carry | `assert-task-rows.ps1` | `task.md:83` | `confirmed-consistent` | pre-existing value, read at the cited line: it agrees with the corrected round-3 rule |
| N1 | carry | `assert-task-rows.ps1` | `assert-oracle-selftests.ps1:7` | `confirmed-consistent` | pre-existing value, read at the cited line: it agrees with the corrected round-3 rule |
| N1 | carry | `assert-task-rows.ps1` | `census-round1-corrections.ps1:27` | `confirmed-consistent` | census declaration table (the sweep's own input list), not a plan assertion |
| N1 | carry | `assert-task-rows.ps1` | `implementation-plan.md:102` | `confirmed-consistent` | pre-existing value, read at the cited line: it agrees with the corrected round-3 rule |
| N1 | carry | `assert-task-rows.ps1` | `implementation-plan.md:285` | `confirmed-consistent` | pre-existing value, read at the cited line: it agrees with the corrected round-3 rule |
| N1 | carry | `assert-task-rows.ps1` | `census-round3-corrections.ps1:58` | `confirmed-consistent` | census declaration table (the sweep's own input list), not a plan assertion |
| N1 | carry | `TASK_ROW_GATE` | `implementation-plan.md:102` | `confirmed-consistent` | pre-existing value, read at the cited line: it agrees with the corrected round-3 rule |
| N1 | carry | `TASK_ROW_GATE` | `census-round3-corrections.ps1:59` | `confirmed-consistent` | census declaration table (the sweep's own input list), not a plan assertion |
| N1 | carry | `TASK_ROW_GATE` | `census-round1-corrections.ps1:28` | `confirmed-consistent` | census declaration table (the sweep's own input list), not a plan assertion |
| N1 | carry | `TASK_ROW_GATE` | `assert-task-rows.ps1:124` | `confirmed-consistent` | pre-existing value, read at the cited line: it agrees with the corrected round-3 rule |
| N1 | carry | `TASK_ROW_GATE` | `assert-task-rows.ps1:132` | `confirmed-consistent` | pre-existing value, read at the cited line: it agrees with the corrected round-3 rule |
| N1 | carry | `TASK_ROW_GATE` | `assert-task-rows.ps1:138` | `confirmed-consistent` | pre-existing value, read at the cited line: it agrees with the corrected round-3 rule |
| N1 | carry | `TASK_ROW_GATE` | `assert-task-rows.ps1:142` | `confirmed-consistent` | pre-existing value, read at the cited line: it agrees with the corrected round-3 rule |
| N1 | carry | `TASK_ROW_GATE` | `assert-task-rows.ps1:146` | `confirmed-consistent` | pre-existing value, read at the cited line: it agrees with the corrected round-3 rule |
| N1 | carry | `TASK_ROW_GATE` | `assert-task-rows.ps1:151` | `confirmed-consistent` | pre-existing value, read at the cited line: it agrees with the corrected round-3 rule |
| N1 | carry | `TASK_ROW_GATE` | `assert-task-rows.ps1:154` | `confirmed-consistent` | pre-existing value, read at the cited line: it agrees with the corrected round-3 rule |
| N1 | carry | `TASK_ROW_GATE` | `assert-oracle-selftests.ps1:7` | `confirmed-consistent` | pre-existing value, read at the cited line: it agrees with the corrected round-3 rule |
| N1 | carry | `TASK_ROW_GATE` | `assert-closeout.ps1:21` | `confirmed-consistent` | pre-existing value, read at the cited line: it agrees with the corrected round-3 rule |
| N2 | old | `BINDING_HANDLERS` | `census-round3-corrections.ps1:62` | `confirmed-consistent` | census declaration table (the sweep's own input list), not a plan assertion |
| N2 | old | `BINDING_TOKEN` | `census-round3-corrections.ps1:63` | `confirmed-consistent` | census declaration table (the sweep's own input list), not a plan assertion |
| N2 | new | `BINDING_HANDLER_METHODS` | `named-sets.json:33` | `updated` | the value did not exist before the round-3 pass, so this line was written by that pass |
| N2 | new | `BINDING_HANDLER_METHODS` | `implementation-plan.md:216` | `updated` | the value did not exist before the round-3 pass, so this line was written by that pass |
| N2 | new | `BINDING_HANDLER_METHODS` | `census-round3-corrections.ps1:64` | `confirmed-consistent` | census declaration table (the sweep's own input list), not a plan assertion |
| N2 | new | `BINDING_HANDLER_METHODS` | `assert-picker-binding.ps1:9` | `updated` | the value did not exist before the round-3 pass, so this line was written by that pass |
| N2 | new | `BINDING_HANDLER_METHODS` | `assert-picker-binding.ps1:20` | `updated` | the value did not exist before the round-3 pass, so this line was written by that pass |
| N2 | new | `BINDING_HANDLER_METHODS` | `assert-picker-binding.ps1:38` | `updated` | the value did not exist before the round-3 pass, so this line was written by that pass |
| N2 | new | `BINDING_DELEGATION_TOKEN` | `named-sets.json:39` | `updated` | the value did not exist before the round-3 pass, so this line was written by that pass |
| N2 | new | `BINDING_DELEGATION_TOKEN` | `census-round3-corrections.ps1:65` | `confirmed-consistent` | census declaration table (the sweep's own input list), not a plan assertion |
| N2 | new | `BINDING_DELEGATION_TOKEN` | `assert-picker-binding.ps1:21` | `updated` | the value did not exist before the round-3 pass, so this line was written by that pass |
| N2 | new | `BINDING_ENTRY_METHOD` | `named-sets.json:40` | `updated` | the value did not exist before the round-3 pass, so this line was written by that pass |
| N2 | new | `BINDING_ENTRY_METHOD` | `census-round3-corrections.ps1:66` | `confirmed-consistent` | census declaration table (the sweep's own input list), not a plan assertion |
| N2 | new | `BINDING_ENTRY_METHOD` | `assert-picker-binding.ps1:22` | `updated` | the value did not exist before the round-3 pass, so this line was written by that pass |
| N2 | new | `BINDING_ENTRY_CALLS` | `assert-picker-binding.ps1:23` | `updated` | the value did not exist before the round-3 pass, so this line was written by that pass |
| N2 | new | `BINDING_ENTRY_CALLS` | `named-sets.json:41` | `updated` | the value did not exist before the round-3 pass, so this line was written by that pass |
| N2 | new | `BINDING_ENTRY_CALLS` | `census-round3-corrections.ps1:67` | `confirmed-consistent` | census declaration table (the sweep's own input list), not a plan assertion |
| N2 | new | `Get-MethodBody` | `census-round3-corrections.ps1:68` | `confirmed-consistent` | census declaration table (the sweep's own input list), not a plan assertion |
| N2 | new | `Get-MethodBody` | `assert-picker-binding.ps1:25` | `updated` | the value did not exist before the round-3 pass, so this line was written by that pass |
| N2 | new | `Get-MethodBody` | `assert-picker-binding.ps1:42` | `updated` | the value did not exist before the round-3 pass, so this line was written by that pass |
| N2 | new | `Get-MethodBody` | `assert-picker-binding.ps1:58` | `updated` | the value did not exist before the round-3 pass, so this line was written by that pass |
| N2 | new | `Test-Entrypoint` | `census-round3-corrections.ps1:69` | `confirmed-consistent` | census declaration table (the sweep's own input list), not a plan assertion |
| N2 | new | `Test-Entrypoint` | `assert-picker-binding.ps1:56` | `updated` | the value did not exist before the round-3 pass, so this line was written by that pass |
| N2 | new | `Test-Entrypoint` | `assert-picker-binding.ps1:121` | `updated` | the value did not exist before the round-3 pass, so this line was written by that pass |
| N2 | new | `Test-Entrypoint` | `assert-picker-binding.ps1:122` | `updated` | the value did not exist before the round-3 pass, so this line was written by that pass |
| N2 | new | `Test-Entrypoint` | `assert-picker-binding.ps1:127` | `updated` | the value did not exist before the round-3 pass, so this line was written by that pass |
| N2 | new | `Test-Entrypoint` | `assert-picker-binding.ps1:133` | `updated` | the value did not exist before the round-3 pass, so this line was written by that pass |
| N2 | new | `Test-Entrypoint` | `assert-picker-binding.ps1:154` | `updated` | the value did not exist before the round-3 pass, so this line was written by that pass |
| N2 | new | `_controller.` | `named-sets.json:39` | `updated` | the value did not exist before the round-3 pass, so this line was written by that pass |
| N2 | new | `_controller.` | `census-round3-corrections.ps1:70` | `confirmed-consistent` | census declaration table (the sweep's own input list), not a plan assertion |
| N2 | new | `_controller.` | `assert-picker-binding.ps1:10` | `updated` | the value did not exist before the round-3 pass, so this line was written by that pass |
| N2 | new | `_controller.` | `assert-picker-binding.ps1:77` | `updated` | the value did not exist before the round-3 pass, so this line was written by that pass |
| N2 | new | `_controller.` | `assert-picker-binding.ps1:80` | `updated` | the value did not exist before the round-3 pass, so this line was written by that pass |
| N2 | new | `_controller.` | `assert-picker-binding.ps1:83` | `updated` | the value did not exist before the round-3 pass, so this line was written by that pass |
| N2 | new | `_controller.` | `assert-picker-binding.ps1:86` | `updated` | the value did not exist before the round-3 pass, so this line was written by that pass |
| N2 | new | `_controller.` | `assert-picker-binding.ps1:95` | `updated` | the value did not exist before the round-3 pass, so this line was written by that pass |
| N2 | new | `_controller.` | `assert-picker-binding.ps1:102` | `updated` | the value did not exist before the round-3 pass, so this line was written by that pass |
| N2 | new | `new RegionForm(` | `task.md:45` | `updated` | the value did not exist before the round-3 pass, so this line was written by that pass |
| N2 | new | `new RegionForm(` | `task.md:46` | `updated` | the value did not exist before the round-3 pass, so this line was written by that pass |
| N2 | new | `new RegionForm(` | `named-sets.json:43` | `updated` | the value did not exist before the round-3 pass, so this line was written by that pass |
| N2 | new | `new RegionForm(` | `implementation-plan.md:216` | `updated` | the value did not exist before the round-3 pass, so this line was written by that pass |
| N2 | new | `new RegionForm(` | `implementation-plan.md:339` | `updated` | the value did not exist before the round-3 pass, so this line was written by that pass |
| N2 | new | `new RegionForm(` | `census-round3-corrections.ps1:71` | `confirmed-consistent` | census declaration table (the sweep's own input list), not a plan assertion |
| N2 | new | `new RegionForm(` | `assert-picker-binding.ps1:11` | `updated` | the value did not exist before the round-3 pass, so this line was written by that pass |
| N2 | new | `new RegionForm(` | `assert-picker-binding.ps1:67` | `updated` | the value did not exist before the round-3 pass, so this line was written by that pass |
| N2 | new | `new RegionForm(` | `assert-picker-binding.ps1:117` | `updated` | the value did not exist before the round-3 pass, so this line was written by that pass |
| N2 | new | `new RegionForm(` | `assert-picker-binding.ps1:126` | `updated` | the value did not exist before the round-3 pass, so this line was written by that pass |
| N2 | new | `new RegionForm(` | `assert-picker-binding.ps1:132` | `updated` | the value did not exist before the round-3 pass, so this line was written by that pass |
| N2 | new | `new RegionForm(` | `assert-picker-binding.ps1:170` | `updated` | the value did not exist before the round-3 pass, so this line was written by that pass |
| N2 | carry | `assert-picker-binding.ps1` | `task.md:46` | `confirmed-consistent` | pre-existing value, read at the cited line: it agrees with the corrected round-3 rule |
| N2 | carry | `assert-picker-binding.ps1` | `run-verification-plan.ps1:26` | `confirmed-consistent` | pre-existing value, read at the cited line: it agrees with the corrected round-3 rule |
| N2 | carry | `assert-picker-binding.ps1` | `implementation-plan.md:105` | `confirmed-consistent` | pre-existing value, read at the cited line: it agrees with the corrected round-3 rule |
| N2 | carry | `assert-picker-binding.ps1` | `implementation-plan.md:216` | `confirmed-consistent` | pre-existing value, read at the cited line: it agrees with the corrected round-3 rule |
| N2 | carry | `assert-picker-binding.ps1` | `implementation-plan.md:285` | `confirmed-consistent` | pre-existing value, read at the cited line: it agrees with the corrected round-3 rule |
| N2 | carry | `assert-picker-binding.ps1` | `implementation-plan.md:339` | `confirmed-consistent` | pre-existing value, read at the cited line: it agrees with the corrected round-3 rule |
| N2 | carry | `assert-picker-binding.ps1` | `census-round3-corrections.ps1:72` | `confirmed-consistent` | census declaration table (the sweep's own input list), not a plan assertion |
| N2 | carry | `assert-picker-binding.ps1` | `census-round1-corrections.ps1:43` | `confirmed-consistent` | census declaration table (the sweep's own input list), not a plan assertion |
| N2 | carry | `assert-picker-binding.ps1` | `assert-oracle-selftests.ps1:11` | `confirmed-consistent` | pre-existing value, read at the cited line: it agrees with the corrected round-3 rule |
| N2 | carry | `assert-picker-binding.ps1` | `assert-closeout.ps1:23` | `confirmed-consistent` | pre-existing value, read at the cited line: it agrees with the corrected round-3 rule |
| N2 | carry | `AC-40.17` | `task.md:46` | `confirmed-consistent` | pre-existing value, read at the cited line: it agrees with the corrected round-3 rule |
| N2 | carry | `AC-40.17` | `named-sets.json:128` | `confirmed-consistent` | pre-existing value, read at the cited line: it agrees with the corrected round-3 rule |
| N2 | carry | `AC-40.17` | `implementation-plan.md:216` | `confirmed-consistent` | pre-existing value, read at the cited line: it agrees with the corrected round-3 rule |
| N2 | carry | `AC-40.17` | `implementation-plan.md:339` | `confirmed-consistent` | pre-existing value, read at the cited line: it agrees with the corrected round-3 rule |
| N2 | carry | `AC-40.17` | `census-round3-corrections.ps1:73` | `confirmed-consistent` | census declaration table (the sweep's own input list), not a plan assertion |
| N2 | carry | `AC-40.17` | `census-round1-corrections.ps1:45` | `confirmed-consistent` | census declaration table (the sweep's own input list), not a plan assertion |
| N2 | carry | `AC-40.17` | `assert-picker-binding.ps1:1` | `confirmed-consistent` | pre-existing value, read at the cited line: it agrees with the corrected round-3 rule |
| N3 | old | `PICKER_DIST_REQUIRED_TOKEN` | `census-round3-corrections.ps1:76` | `confirmed-consistent` | census declaration table (the sweep's own input list), not a plan assertion |
| N3 | old | `npm --prefix ui run $buildScript` | `census-round3-corrections.ps1:80` | `confirmed-consistent` | census declaration table (the sweep's own input list), not a plan assertion |
| N3 | new | `npm --prefix ui run $prepScript` | `census-round3-corrections.ps1:81` | `confirmed-consistent` | census declaration table (the sweep's own input list), not a plan assertion |
| N3 | new | `npm --prefix ui run $prepScript` | `assert-packaging-clean.ps1:128` | `updated` | the value did not exist before the round-3 pass, so this line was written by that pass |
| N3 | new | `PICKER_PREP_SCRIPT` | `named-sets.json:20` | `updated` | the value did not exist before the round-3 pass, so this line was written by that pass |
| N3 | new | `PICKER_PREP_SCRIPT` | `census-round3-corrections.ps1:82` | `confirmed-consistent` | census declaration table (the sweep's own input list), not a plan assertion |
| N3 | new | `PICKER_PREP_SCRIPT` | `assert-packaging-clean.ps1:22` | `updated` | the value did not exist before the round-3 pass, so this line was written by that pass |
| N3 | new | `PICKER_DIST_REQUIRED_SEGMENT` | `named-sets.json:22` | `updated` | the value did not exist before the round-3 pass, so this line was written by that pass |
| N3 | new | `PICKER_DIST_REQUIRED_SEGMENT` | `census-round3-corrections.ps1:83` | `confirmed-consistent` | census declaration table (the sweep's own input list), not a plan assertion |
| N3 | new | `PICKER_DIST_REQUIRED_SEGMENT` | `assert-packaging-clean.ps1:24` | `updated` | the value did not exist before the round-3 pass, so this line was written by that pass |
| N3 | new | `PICKER_PREP_REQUIRED_SEGMENT` | `named-sets.json:23` | `updated` | the value did not exist before the round-3 pass, so this line was written by that pass |
| N3 | new | `PICKER_PREP_REQUIRED_SEGMENT` | `census-round3-corrections.ps1:84` | `confirmed-consistent` | census declaration table (the sweep's own input list), not a plan assertion |
| N3 | new | `PICKER_PREP_REQUIRED_SEGMENT` | `assert-packaging-clean.ps1:25` | `updated` | the value did not exist before the round-3 pass, so this line was written by that pass |
| N3 | new | `PICKER_SEGMENT_SEPARATOR` | `named-sets.json:24` | `updated` | the value did not exist before the round-3 pass, so this line was written by that pass |
| N3 | new | `PICKER_SEGMENT_SEPARATOR` | `census-round3-corrections.ps1:85` | `confirmed-consistent` | census declaration table (the sweep's own input list), not a plan assertion |
| N3 | new | `PICKER_SEGMENT_SEPARATOR` | `assert-packaging-clean.ps1:26` | `updated` | the value did not exist before the round-3 pass, so this line was written by that pass |
| N3 | new | `dist:prep` | `task.md:47` | `updated` | the value did not exist before the round-3 pass, so this line was written by that pass |
| N3 | new | `dist:prep` | `named-sets.json:20` | `updated` | the value did not exist before the round-3 pass, so this line was written by that pass |
| N3 | new | `dist:prep` | `named-sets.json:22` | `updated` | the value did not exist before the round-3 pass, so this line was written by that pass |
| N3 | new | `dist:prep` | `implementation-plan.md:222` | `updated` | the value did not exist before the round-3 pass, so this line was written by that pass |
| N3 | new | `dist:prep` | `implementation-plan.md:277` | `updated` | the value did not exist before the round-3 pass, so this line was written by that pass |
| N3 | new | `dist:prep` | `implementation-plan.md:334` | `updated` | the value did not exist before the round-3 pass, so this line was written by that pass |
| N3 | new | `dist:prep` | `census-round3-corrections.ps1:86` | `confirmed-consistent` | census declaration table (the sweep's own input list), not a plan assertion |
| N3 | new | `dist:prep` | `census-round3-corrections.ps1:87` | `confirmed-consistent` | census declaration table (the sweep's own input list), not a plan assertion |
| N3 | new | `dist:prep` | `assert-packaging-clean.ps1:10` | `updated` | the value did not exist before the round-3 pass, so this line was written by that pass |
| N3 | new | `dist:prep` | `assert-packaging-clean.ps1:14` | `updated` | the value did not exist before the round-3 pass, so this line was written by that pass |
| N3 | new | `dist:prep` | `assert-packaging-clean.ps1:57` | `updated` | the value did not exist before the round-3 pass, so this line was written by that pass |
| N3 | new | `dist:prep` | `assert-packaging-clean.ps1:58` | `updated` | the value did not exist before the round-3 pass, so this line was written by that pass |
| N3 | new | `dist:prep` | `assert-packaging-clean.ps1:66` | `updated` | the value did not exist before the round-3 pass, so this line was written by that pass |
| N3 | new | `dist:prep` | `assert-packaging-clean.ps1:67` | `updated` | the value did not exist before the round-3 pass, so this line was written by that pass |
| N3 | new | `dist:prep` | `assert-packaging-clean.ps1:70` | `updated` | the value did not exist before the round-3 pass, so this line was written by that pass |
| N3 | new | `dist:prep` | `assert-packaging-clean.ps1:76` | `updated` | the value did not exist before the round-3 pass, so this line was written by that pass |
| N3 | new | `dist:prep` | `assert-packaging-clean.ps1:77` | `updated` | the value did not exist before the round-3 pass, so this line was written by that pass |
| N3 | new | `dist:prep` | `assert-packaging-clean.ps1:80` | `updated` | the value did not exist before the round-3 pass, so this line was written by that pass |
| N3 | new | `dist:prep` | `assert-packaging-clean.ps1:86` | `updated` | the value did not exist before the round-3 pass, so this line was written by that pass |
| N3 | new | `dist:prep` | `assert-packaging-clean.ps1:94` | `updated` | the value did not exist before the round-3 pass, so this line was written by that pass |
| N3 | new | `dist:prep` | `assert-packaging-clean.ps1:96` | `updated` | the value did not exist before the round-3 pass, so this line was written by that pass |
| N3 | new | `dist:prep` | `assert-packaging-clean.ps1:103` | `updated` | the value did not exist before the round-3 pass, so this line was written by that pass |
| N3 | new | `npm run dist:prep` | `task.md:47` | `updated` | the value did not exist before the round-3 pass, so this line was written by that pass |
| N3 | new | `npm run dist:prep` | `named-sets.json:22` | `updated` | the value did not exist before the round-3 pass, so this line was written by that pass |
| N3 | new | `npm run dist:prep` | `implementation-plan.md:222` | `updated` | the value did not exist before the round-3 pass, so this line was written by that pass |
| N3 | new | `npm run dist:prep` | `implementation-plan.md:277` | `updated` | the value did not exist before the round-3 pass, so this line was written by that pass |
| N3 | new | `npm run dist:prep` | `census-round3-corrections.ps1:87` | `confirmed-consistent` | census declaration table (the sweep's own input list), not a plan assertion |
| N3 | new | `npm run dist:prep` | `assert-packaging-clean.ps1:10` | `updated` | the value did not exist before the round-3 pass, so this line was written by that pass |
| N3 | new | `npm run dist:prep` | `assert-packaging-clean.ps1:58` | `updated` | the value did not exist before the round-3 pass, so this line was written by that pass |
| N3 | new | `npm run dist:prep` | `assert-packaging-clean.ps1:77` | `updated` | the value did not exist before the round-3 pass, so this line was written by that pass |
| N3 | new | `npm run dist:prep` | `assert-packaging-clean.ps1:94` | `updated` | the value did not exist before the round-3 pass, so this line was written by that pass |
| N3 | new | `Get-Segments` | `census-round3-corrections.ps1:88` | `confirmed-consistent` | census declaration table (the sweep's own input list), not a plan assertion |
| N3 | new | `Get-Segments` | `assert-packaging-clean.ps1:32` | `updated` | the value did not exist before the round-3 pass, so this line was written by that pass |
| N3 | new | `Get-Segments` | `assert-packaging-clean.ps1:43` | `updated` | the value did not exist before the round-3 pass, so this line was written by that pass |
| N3 | new | `Get-Segments` | `assert-packaging-clean.ps1:47` | `updated` | the value did not exist before the round-3 pass, so this line was written by that pass |
| N3 | carry | `assert-packaging-clean.ps1` | `task.md:47` | `confirmed-consistent` | pre-existing value, read at the cited line: it agrees with the corrected round-3 rule |
| N3 | carry | `assert-packaging-clean.ps1` | `run-verification-plan.ps1:21` | `confirmed-consistent` | pre-existing value, read at the cited line: it agrees with the corrected round-3 rule |
| N3 | carry | `assert-packaging-clean.ps1` | `implementation-plan.md:106` | `confirmed-consistent` | pre-existing value, read at the cited line: it agrees with the corrected round-3 rule |
| N3 | carry | `assert-packaging-clean.ps1` | `implementation-plan.md:222` | `confirmed-consistent` | pre-existing value, read at the cited line: it agrees with the corrected round-3 rule |
| N3 | carry | `assert-packaging-clean.ps1` | `implementation-plan.md:285` | `confirmed-consistent` | pre-existing value, read at the cited line: it agrees with the corrected round-3 rule |
| N3 | carry | `assert-packaging-clean.ps1` | `implementation-plan.md:334` | `confirmed-consistent` | pre-existing value, read at the cited line: it agrees with the corrected round-3 rule |
| N3 | carry | `assert-packaging-clean.ps1` | `census-round3-corrections.ps1:89` | `confirmed-consistent` | census declaration table (the sweep's own input list), not a plan assertion |
| N3 | carry | `assert-packaging-clean.ps1` | `census-round1-corrections.ps1:49` | `confirmed-consistent` | census declaration table (the sweep's own input list), not a plan assertion |
| N3 | carry | `assert-packaging-clean.ps1` | `assert-oracle-selftests.ps1:12` | `confirmed-consistent` | pre-existing value, read at the cited line: it agrees with the corrected round-3 rule |
| N3 | carry | `assert-packaging-clean.ps1` | `assert-closeout.ps1:24` | `confirmed-consistent` | pre-existing value, read at the cited line: it agrees with the corrected round-3 rule |
| N3 | carry | `build:picker` | `task.md:47` | `confirmed-consistent` | pre-existing value, read at the cited line: it agrees with the corrected round-3 rule |
| N3 | carry | `build:picker` | `task.md:48` | `confirmed-consistent` | pre-existing value, read at the cited line: it agrees with the corrected round-3 rule |
| N3 | carry | `build:picker` | `task.md:50` | `confirmed-consistent` | pre-existing value, read at the cited line: it agrees with the corrected round-3 rule |
| N3 | carry | `build:picker` | `named-sets.json:19` | `confirmed-consistent` | pre-existing value, read at the cited line: it agrees with the corrected round-3 rule |
| N3 | carry | `build:picker` | `named-sets.json:23` | `confirmed-consistent` | pre-existing value, read at the cited line: it agrees with the corrected round-3 rule |
| N3 | carry | `build:picker` | `named-sets.json:74` | `confirmed-consistent` | pre-existing value, read at the cited line: it agrees with the corrected round-3 rule |
| N3 | carry | `build:picker` | `implementation-plan.md:222` | `confirmed-consistent` | pre-existing value, read at the cited line: it agrees with the corrected round-3 rule |
| N3 | carry | `build:picker` | `implementation-plan.md:225` | `confirmed-consistent` | pre-existing value, read at the cited line: it agrees with the corrected round-3 rule |
| N3 | carry | `build:picker` | `implementation-plan.md:277` | `confirmed-consistent` | pre-existing value, read at the cited line: it agrees with the corrected round-3 rule |
| N3 | carry | `build:picker` | `census-round3-corrections.ps1:78` | `confirmed-consistent` | census declaration table (the sweep's own input list), not a plan assertion |
| N3 | carry | `build:picker` | `census-round3-corrections.ps1:79` | `confirmed-consistent` | census declaration table (the sweep's own input list), not a plan assertion |
| N3 | carry | `build:picker` | `census-round3-corrections.ps1:90` | `confirmed-consistent` | census declaration table (the sweep's own input list), not a plan assertion |
| N3 | carry | `build:picker` | `census-round3-corrections.ps1:104` | `confirmed-consistent` | census declaration table (the sweep's own input list), not a plan assertion |
| N3 | carry | `build:picker` | `census-round1-corrections.ps1:50` | `confirmed-consistent` | census declaration table (the sweep's own input list), not a plan assertion |
| N3 | carry | `build:picker` | `assert-packaging-clean.ps1:3` | `confirmed-consistent` | pre-existing value, read at the cited line: it agrees with the corrected round-3 rule |
| N3 | carry | `build:picker` | `assert-packaging-clean.ps1:5` | `confirmed-consistent` | pre-existing value, read at the cited line: it agrees with the corrected round-3 rule |
| N3 | carry | `build:picker` | `assert-packaging-clean.ps1:6` | `confirmed-consistent` | pre-existing value, read at the cited line: it agrees with the corrected round-3 rule |
| N3 | carry | `build:picker` | `assert-packaging-clean.ps1:10` | `confirmed-consistent` | pre-existing value, read at the cited line: it agrees with the corrected round-3 rule |
| N3 | carry | `build:picker` | `assert-packaging-clean.ps1:56` | `confirmed-consistent` | pre-existing value, read at the cited line: it agrees with the corrected round-3 rule |
| N3 | carry | `build:picker` | `assert-packaging-clean.ps1:57` | `confirmed-consistent` | pre-existing value, read at the cited line: it agrees with the corrected round-3 rule |
| N3 | carry | `build:picker` | `assert-packaging-clean.ps1:65` | `confirmed-consistent` | pre-existing value, read at the cited line: it agrees with the corrected round-3 rule |
| N3 | carry | `build:picker` | `assert-packaging-clean.ps1:66` | `confirmed-consistent` | pre-existing value, read at the cited line: it agrees with the corrected round-3 rule |
| N3 | carry | `build:picker` | `assert-packaging-clean.ps1:75` | `confirmed-consistent` | pre-existing value, read at the cited line: it agrees with the corrected round-3 rule |
| N3 | carry | `build:picker` | `assert-packaging-clean.ps1:76` | `confirmed-consistent` | pre-existing value, read at the cited line: it agrees with the corrected round-3 rule |
| N3 | carry | `build:picker` | `assert-packaging-clean.ps1:85` | `confirmed-consistent` | pre-existing value, read at the cited line: it agrees with the corrected round-3 rule |
| N3 | carry | `build:picker` | `assert-packaging-clean.ps1:86` | `confirmed-consistent` | pre-existing value, read at the cited line: it agrees with the corrected round-3 rule |
| N3 | carry | `build:picker` | `assert-packaging-clean.ps1:96` | `confirmed-consistent` | pre-existing value, read at the cited line: it agrees with the corrected round-3 rule |
| N3 | carry | `build:picker` | `assert-packaging-clean.ps1:103` | `confirmed-consistent` | pre-existing value, read at the cited line: it agrees with the corrected round-3 rule |
| N3 | carry | `AC-40.10` | `task.md:47` | `confirmed-consistent` | pre-existing value, read at the cited line: it agrees with the corrected round-3 rule |
| N3 | carry | `AC-40.10` | `named-sets.json:121` | `confirmed-consistent` | pre-existing value, read at the cited line: it agrees with the corrected round-3 rule |
| N3 | carry | `AC-40.10` | `implementation-plan.md:222` | `confirmed-consistent` | pre-existing value, read at the cited line: it agrees with the corrected round-3 rule |
| N3 | carry | `AC-40.10` | `implementation-plan.md:334` | `confirmed-consistent` | pre-existing value, read at the cited line: it agrees with the corrected round-3 rule |
| N3 | carry | `AC-40.10` | `census-round3-corrections.ps1:91` | `confirmed-consistent` | census declaration table (the sweep's own input list), not a plan assertion |
| N3 | carry | `AC-40.10` | `assert-packaging-clean.ps1:1` | `confirmed-consistent` | pre-existing value, read at the cited line: it agrees with the corrected round-3 rule |
| N4 | new | `assert-e2e-wired.ps1` | `task.md:50` | `updated` | the value did not exist before the round-3 pass, so this line was written by that pass |
| N4 | new | `assert-e2e-wired.ps1` | `task.md:86` | `updated` | the value did not exist before the round-3 pass, so this line was written by that pass |
| N4 | new | `assert-e2e-wired.ps1` | `run-verification-plan.ps1:29` | `updated` | the value did not exist before the round-3 pass, so this line was written by that pass |
| N4 | new | `assert-e2e-wired.ps1` | `implementation-plan.md:223` | `updated` | the value did not exist before the round-3 pass, so this line was written by that pass |
| N4 | new | `assert-e2e-wired.ps1` | `implementation-plan.md:225` | `updated` | the value did not exist before the round-3 pass, so this line was written by that pass |
| N4 | new | `assert-e2e-wired.ps1` | `implementation-plan.md:285` | `updated` | the value did not exist before the round-3 pass, so this line was written by that pass |
| N4 | new | `assert-e2e-wired.ps1` | `implementation-plan.md:343` | `updated` | the value did not exist before the round-3 pass, so this line was written by that pass |
| N4 | new | `assert-e2e-wired.ps1` | `census-round3-corrections.ps1:94` | `confirmed-consistent` | census declaration table (the sweep's own input list), not a plan assertion |
| N4 | new | `assert-e2e-wired.ps1` | `assert-oracle-selftests.ps1:13` | `updated` | the value did not exist before the round-3 pass, so this line was written by that pass |
| N4 | new | `assert-e2e-wired.ps1` | `assert-closeout.ps1:25` | `updated` | the value did not exist before the round-3 pass, so this line was written by that pass |
| N4 | new | `assert-smoke-disposition.ps1` | `task.md:52` | `updated` | the value did not exist before the round-3 pass, so this line was written by that pass |
| N4 | new | `assert-smoke-disposition.ps1` | `task.md:86` | `updated` | the value did not exist before the round-3 pass, so this line was written by that pass |
| N4 | new | `assert-smoke-disposition.ps1` | `run-verification-plan.ps1:9` | `updated` | the value did not exist before the round-3 pass, so this line was written by that pass |
| N4 | new | `assert-smoke-disposition.ps1` | `run-verification-plan.ps1:31` | `updated` | the value did not exist before the round-3 pass, so this line was written by that pass |
| N4 | new | `assert-smoke-disposition.ps1` | `implementation-plan.md:225` | `updated` | the value did not exist before the round-3 pass, so this line was written by that pass |
| N4 | new | `assert-smoke-disposition.ps1` | `implementation-plan.md:285` | `updated` | the value did not exist before the round-3 pass, so this line was written by that pass |
| N4 | new | `assert-smoke-disposition.ps1` | `implementation-plan.md:345` | `updated` | the value did not exist before the round-3 pass, so this line was written by that pass |
| N4 | new | `assert-smoke-disposition.ps1` | `census-round3-corrections.ps1:95` | `confirmed-consistent` | census declaration table (the sweep's own input list), not a plan assertion |
| N4 | new | `assert-smoke-disposition.ps1` | `assert-oracle-selftests.ps1:14` | `updated` | the value did not exist before the round-3 pass, so this line was written by that pass |
| N4 | new | `assert-smoke-disposition.ps1` | `assert-closeout.ps1:26` | `updated` | the value did not exist before the round-3 pass, so this line was written by that pass |
| N4 | new | `AC-40.18` | `task.md:48` | `updated` | the value did not exist before the round-3 pass, so this line was written by that pass |
| N4 | new | `AC-40.18` | `task.md:50` | `updated` | the value did not exist before the round-3 pass, so this line was written by that pass |
| N4 | new | `AC-40.18` | `named-sets.json:84` | `updated` | the value did not exist before the round-3 pass, so this line was written by that pass |
| N4 | new | `AC-40.18` | `named-sets.json:129` | `updated` | the value did not exist before the round-3 pass, so this line was written by that pass |
| N4 | new | `AC-40.18` | `implementation-plan.md:223` | `updated` | the value did not exist before the round-3 pass, so this line was written by that pass |
| N4 | new | `AC-40.18` | `implementation-plan.md:224` | `updated` | the value did not exist before the round-3 pass, so this line was written by that pass |
| N4 | new | `AC-40.18` | `implementation-plan.md:281` | `updated` | the value did not exist before the round-3 pass, so this line was written by that pass |
| N4 | new | `AC-40.18` | `implementation-plan.md:344` | `updated` | the value did not exist before the round-3 pass, so this line was written by that pass |
| N4 | new | `AC-40.18` | `census-round3-corrections.ps1:96` | `confirmed-consistent` | census declaration table (the sweep's own input list), not a plan assertion |
| N4 | new | `AC-40.18` | `assert-e2e-wired.ps1:65` | `updated` | the value did not exist before the round-3 pass, so this line was written by that pass |
| N4 | new | `AC-40.19` | `assert-e2e-wired.ps1:1` | `updated` | the value did not exist before the round-3 pass, so this line was written by that pass |
| N4 | new | `AC-40.19` | `assert-smoke-disposition.ps1:1` | `updated` | the value did not exist before the round-3 pass, so this line was written by that pass |
| N4 | new | `AC-40.19` | `task.md:50` | `updated` | the value did not exist before the round-3 pass, so this line was written by that pass |
| N4 | new | `AC-40.19` | `task.md:52` | `updated` | the value did not exist before the round-3 pass, so this line was written by that pass |
| N4 | new | `AC-40.19` | `implementation-plan.md:225` | `updated` | the value did not exist before the round-3 pass, so this line was written by that pass |
| N4 | new | `AC-40.19` | `implementation-plan.md:343` | `updated` | the value did not exist before the round-3 pass, so this line was written by that pass |
| N4 | new | `AC-40.19` | `implementation-plan.md:345` | `updated` | the value did not exist before the round-3 pass, so this line was written by that pass |
| N4 | new | `AC-40.19` | `named-sets.json:130` | `updated` | the value did not exist before the round-3 pass, so this line was written by that pass |
| N4 | new | `AC-40.19` | `census-round3-corrections.ps1:97` | `confirmed-consistent` | census declaration table (the sweep's own input list), not a plan assertion |
| N4 | new | `E2E_WIRED` | `run-verification-plan.ps1:29` | `updated` | the value did not exist before the round-3 pass, so this line was written by that pass |
| N4 | new | `E2E_WIRED` | `implementation-plan.md:225` | `updated` | the value did not exist before the round-3 pass, so this line was written by that pass |
| N4 | new | `E2E_WIRED` | `census-round3-corrections.ps1:98` | `confirmed-consistent` | census declaration table (the sweep's own input list), not a plan assertion |
| N4 | new | `E2E_WIRED` | `assert-oracle-selftests.ps1:13` | `updated` | the value did not exist before the round-3 pass, so this line was written by that pass |
| N4 | new | `E2E_WIRED` | `assert-e2e-wired.ps1:96` | `updated` | the value did not exist before the round-3 pass, so this line was written by that pass |
| N4 | new | `E2E_WIRED` | `assert-e2e-wired.ps1:137` | `updated` | the value did not exist before the round-3 pass, so this line was written by that pass |
| N4 | new | `E2E_WIRED` | `assert-closeout.ps1:25` | `updated` | the value did not exist before the round-3 pass, so this line was written by that pass |
| N4 | new | `SMOKE_DISPOSITION` | `run-verification-plan.ps1:31` | `updated` | the value did not exist before the round-3 pass, so this line was written by that pass |
| N4 | new | `SMOKE_DISPOSITION` | `named-sets.json:87` | `updated` | the value did not exist before the round-3 pass, so this line was written by that pass |
| N4 | new | `SMOKE_DISPOSITION` | `named-sets.json:88` | `updated` | the value did not exist before the round-3 pass, so this line was written by that pass |
| N4 | new | `SMOKE_DISPOSITION` | `implementation-plan.md:225` | `updated` | the value did not exist before the round-3 pass, so this line was written by that pass |
| N4 | new | `SMOKE_DISPOSITION` | `census-round3-corrections.ps1:99` | `confirmed-consistent` | census declaration table (the sweep's own input list), not a plan assertion |
| N4 | new | `SMOKE_DISPOSITION` | `census-round3-corrections.ps1:107` | `confirmed-consistent` | census declaration table (the sweep's own input list), not a plan assertion |
| N4 | new | `SMOKE_DISPOSITION` | `assert-smoke-disposition.ps1:8` | `updated` | the value did not exist before the round-3 pass, so this line was written by that pass |
| N4 | new | `SMOKE_DISPOSITION` | `assert-smoke-disposition.ps1:18` | `updated` | the value did not exist before the round-3 pass, so this line was written by that pass |
| N4 | new | `SMOKE_DISPOSITION` | `assert-smoke-disposition.ps1:19` | `updated` | the value did not exist before the round-3 pass, so this line was written by that pass |
| N4 | new | `SMOKE_DISPOSITION` | `assert-smoke-disposition.ps1:73` | `updated` | the value did not exist before the round-3 pass, so this line was written by that pass |
| N4 | new | `SMOKE_DISPOSITION` | `assert-smoke-disposition.ps1:77` | `updated` | the value did not exist before the round-3 pass, so this line was written by that pass |
| N4 | new | `SMOKE_DISPOSITION` | `assert-smoke-disposition.ps1:80` | `updated` | the value did not exist before the round-3 pass, so this line was written by that pass |
| N4 | new | `SMOKE_DISPOSITION` | `assert-oracle-selftests.ps1:14` | `updated` | the value did not exist before the round-3 pass, so this line was written by that pass |
| N4 | new | `SMOKE_DISPOSITION` | `assert-closeout.ps1:26` | `updated` | the value did not exist before the round-3 pass, so this line was written by that pass |
| N4 | new | `E2E_SPEC_FILE` | `named-sets.json:68` | `updated` | the value did not exist before the round-3 pass, so this line was written by that pass |
| N4 | new | `E2E_SPEC_FILE` | `census-round3-corrections.ps1:100` | `confirmed-consistent` | census declaration table (the sweep's own input list), not a plan assertion |
| N4 | new | `E2E_SPEC_FILE` | `assert-e2e-wired.ps1:24` | `updated` | the value did not exist before the round-3 pass, so this line was written by that pass |
| N4 | new | `ui/tests/e2e/capture-picker.test.ts` | `task.md:48` | `updated` | the value did not exist before the round-3 pass, so this line was written by that pass |
| N4 | new | `ui/tests/e2e/capture-picker.test.ts` | `named-sets.json:68` | `updated` | the value did not exist before the round-3 pass, so this line was written by that pass |
| N4 | new | `ui/tests/e2e/capture-picker.test.ts` | `implementation-plan.md:224` | `updated` | the value did not exist before the round-3 pass, so this line was written by that pass |
| N4 | new | `ui/tests/e2e/capture-picker.test.ts` | `implementation-plan.md:281` | `updated` | the value did not exist before the round-3 pass, so this line was written by that pass |
| N4 | new | `ui/tests/e2e/capture-picker.test.ts` | `census-round3-corrections.ps1:101` | `confirmed-consistent` | census declaration table (the sweep's own input list), not a plan assertion |
| N4 | new | `E2E_STUB_PROJECT_DIR` | `named-sets.json:72` | `updated` | the value did not exist before the round-3 pass, so this line was written by that pass |
| N4 | new | `E2E_STUB_PROJECT_DIR` | `census-round3-corrections.ps1:102` | `confirmed-consistent` | census declaration table (the sweep's own input list), not a plan assertion |
| N4 | new | `E2E_STUB_PROJECT_DIR` | `assert-e2e-wired.ps1:33` | `updated` | the value did not exist before the round-3 pass, so this line was written by that pass |
| N4 | new | `native/region-picker-stub` | `task.md:48` | `updated` | the value did not exist before the round-3 pass, so this line was written by that pass |
| N4 | new | `native/region-picker-stub` | `named-sets.json:72` | `updated` | the value did not exist before the round-3 pass, so this line was written by that pass |
| N4 | new | `native/region-picker-stub` | `named-sets.json:73` | `updated` | the value did not exist before the round-3 pass, so this line was written by that pass |
| N4 | new | `native/region-picker-stub` | `implementation-plan.md:282` | `updated` | the value did not exist before the round-3 pass, so this line was written by that pass |
| N4 | new | `native/region-picker-stub` | `census-round3-corrections.ps1:103` | `confirmed-consistent` | census declaration table (the sweep's own input list), not a plan assertion |
| N4 | new | `build:picker-stub` | `task.md:48` | `updated` | the value did not exist before the round-3 pass, so this line was written by that pass |
| N4 | new | `build:picker-stub` | `task.md:50` | `updated` | the value did not exist before the round-3 pass, so this line was written by that pass |
| N4 | new | `build:picker-stub` | `named-sets.json:74` | `updated` | the value did not exist before the round-3 pass, so this line was written by that pass |
| N4 | new | `build:picker-stub` | `implementation-plan.md:225` | `updated` | the value did not exist before the round-3 pass, so this line was written by that pass |
| N4 | new | `build:picker-stub` | `implementation-plan.md:277` | `updated` | the value did not exist before the round-3 pass, so this line was written by that pass |
| N4 | new | `build:picker-stub` | `census-round3-corrections.ps1:79` | `confirmed-consistent` | census declaration table (the sweep's own input list), not a plan assertion |
| N4 | new | `build:picker-stub` | `census-round3-corrections.ps1:104` | `confirmed-consistent` | census declaration table (the sweep's own input list), not a plan assertion |
| N4 | new | `test:e2e` | `task.md:48` | `updated` | the value did not exist before the round-3 pass, so this line was written by that pass |
| N4 | new | `test:e2e` | `task.md:50` | `updated` | the value did not exist before the round-3 pass, so this line was written by that pass |
| N4 | new | `test:e2e` | `named-sets.json:71` | `updated` | the value did not exist before the round-3 pass, so this line was written by that pass |
| N4 | new | `test:e2e` | `implementation-plan.md:225` | `updated` | the value did not exist before the round-3 pass, so this line was written by that pass |
| N4 | new | `test:e2e` | `implementation-plan.md:277` | `updated` | the value did not exist before the round-3 pass, so this line was written by that pass |
| N4 | new | `test:e2e` | `implementation-plan.md:344` | `updated` | the value did not exist before the round-3 pass, so this line was written by that pass |
| N4 | new | `test:e2e` | `census-round3-corrections.ps1:105` | `confirmed-consistent` | census declaration table (the sweep's own input list), not a plan assertion |
| N4 | new | `test:e2e` | `assert-e2e-wired.ps1:12` | `updated` | the value did not exist before the round-3 pass, so this line was written by that pass |
| N4 | new | `test:e2e` | `assert-e2e-wired.ps1:120` | `updated` | the value did not exist before the round-3 pass, so this line was written by that pass |
| N4 | new | `E2E_SHORTCIRCUIT_ENV` | `assert-e2e-wired.ps1:30` | `updated` | the value did not exist before the round-3 pass, so this line was written by that pass |
| N4 | new | `E2E_SHORTCIRCUIT_ENV` | `census-round3-corrections.ps1:106` | `confirmed-consistent` | census declaration table (the sweep's own input list), not a plan assertion |
| N4 | new | `E2E_SHORTCIRCUIT_ENV` | `named-sets.json:86` | `updated` | the value did not exist before the round-3 pass, so this line was written by that pass |
| N4 | new | `SMOKE_DISPOSITION_FILE` | `named-sets.json:87` | `updated` | the value did not exist before the round-3 pass, so this line was written by that pass |
| N4 | new | `SMOKE_DISPOSITION_FILE` | `census-round3-corrections.ps1:107` | `confirmed-consistent` | census declaration table (the sweep's own input list), not a plan assertion |
| N4 | new | `SMOKE_DISPOSITION_FILE` | `assert-smoke-disposition.ps1:8` | `updated` | the value did not exist before the round-3 pass, so this line was written by that pass |
| N4 | new | `SMOKE_DISPOSITION_FILE` | `assert-smoke-disposition.ps1:18` | `updated` | the value did not exist before the round-3 pass, so this line was written by that pass |
| N4 | new | `SMOKE_DISPOSITION_FILE` | `assert-smoke-disposition.ps1:77` | `updated` | the value did not exist before the round-3 pass, so this line was written by that pass |
| N4 | new | `LATENCY_MS` | `task.md:52` | `updated` | the value did not exist before the round-3 pass, so this line was written by that pass |
| N4 | new | `LATENCY_MS` | `named-sets.json:89` | `updated` | the value did not exist before the round-3 pass, so this line was written by that pass |
| N4 | new | `LATENCY_MS` | `implementation-plan.md:225` | `updated` | the value did not exist before the round-3 pass, so this line was written by that pass |
| N4 | new | `LATENCY_MS` | `implementation-plan.md:295` | `updated` | the value did not exist before the round-3 pass, so this line was written by that pass |
| N4 | new | `LATENCY_MS` | `implementation-plan.md:345` | `updated` | the value did not exist before the round-3 pass, so this line was written by that pass |
| N4 | new | `LATENCY_MS` | `census-round3-corrections.ps1:108` | `confirmed-consistent` | census declaration table (the sweep's own input list), not a plan assertion |
| N4 | new | `LATENCY_MS` | `assert-smoke-disposition.ps1:9` | `updated` | the value did not exist before the round-3 pass, so this line was written by that pass |
| N4 | new | `LATENCY_MS` | `assert-smoke-disposition.ps1:40` | `updated` | the value did not exist before the round-3 pass, so this line was written by that pass |
| N4 | new | `LATENCY_MS` | `assert-smoke-disposition.ps1:41` | `updated` | the value did not exist before the round-3 pass, so this line was written by that pass |
| N4 | new | `LATENCY_MS` | `assert-smoke-disposition.ps1:49` | `updated` | the value did not exist before the round-3 pass, so this line was written by that pass |
| N4 | new | `LATENCY_MS` | `assert-smoke-disposition.ps1:53` | `updated` | the value did not exist before the round-3 pass, so this line was written by that pass |
| N4 | new | `LATENCY_MS` | `assert-smoke-disposition.ps1:58` | `updated` | the value did not exist before the round-3 pass, so this line was written by that pass |
| N4 | new | `LATENCY_MS` | `assert-smoke-disposition.ps1:62` | `updated` | the value did not exist before the round-3 pass, so this line was written by that pass |
| N4 | new | `LATENCY_MS` | `assert-smoke-disposition.ps1:66` | `updated` | the value did not exist before the round-3 pass, so this line was written by that pass |
| N4 | new | `LATENCY_MS` | `assert-smoke-disposition.ps1:70` | `updated` | the value did not exist before the round-3 pass, so this line was written by that pass |
| N4 | new | `BLOCKED=` | `task.md:86` | `updated` | the value did not exist before the round-3 pass, so this line was written by that pass |
| N4 | new | `BLOCKED=` | `named-sets.json:90` | `updated` | the value did not exist before the round-3 pass, so this line was written by that pass |
| N4 | new | `BLOCKED=` | `implementation-plan.md:225` | `updated` | the value did not exist before the round-3 pass, so this line was written by that pass |
| N4 | new | `BLOCKED=` | `implementation-plan.md:345` | `updated` | the value did not exist before the round-3 pass, so this line was written by that pass |
| N4 | new | `BLOCKED=` | `census-round3-corrections.ps1:109` | `confirmed-consistent` | census declaration table (the sweep's own input list), not a plan assertion |
| N4 | new | `BLOCKED=` | `assert-smoke-disposition.ps1:9` | `updated` | the value did not exist before the round-3 pass, so this line was written by that pass |
| N4 | new | `BLOCKED=` | `assert-smoke-disposition.ps1:10` | `updated` | the value did not exist before the round-3 pass, so this line was written by that pass |
| N4 | new | `BLOCKED=` | `assert-smoke-disposition.ps1:11` | `updated` | the value did not exist before the round-3 pass, so this line was written by that pass |
| N4 | new | `BLOCKED=` | `assert-smoke-disposition.ps1:43` | `updated` | the value did not exist before the round-3 pass, so this line was written by that pass |
| N4 | new | `BLOCKED=` | `assert-smoke-disposition.ps1:49` | `updated` | the value did not exist before the round-3 pass, so this line was written by that pass |
| N4 | new | `BLOCKED=` | `assert-smoke-disposition.ps1:53` | `updated` | the value did not exist before the round-3 pass, so this line was written by that pass |
| N4 | new | `BLOCKED=` | `assert-smoke-disposition.ps1:58` | `updated` | the value did not exist before the round-3 pass, so this line was written by that pass |
| N4 | new | `BLOCKED=` | `assert-smoke-disposition.ps1:62` | `updated` | the value did not exist before the round-3 pass, so this line was written by that pass |
| N4 | new | `BLOCKED=` | `assert-smoke-disposition.ps1:66` | `updated` | the value did not exist before the round-3 pass, so this line was written by that pass |
| N4 | carry | `AVKIT_E2E` | `task.md:49` | `confirmed-consistent` | pre-existing value, read at the cited line: it agrees with the corrected round-3 rule |
| N4 | carry | `AVKIT_E2E` | `task.md:50` | `confirmed-consistent` | pre-existing value, read at the cited line: it agrees with the corrected round-3 rule |
| N4 | carry | `AVKIT_E2E` | `named-sets.json:86` | `confirmed-consistent` | pre-existing value, read at the cited line: it agrees with the corrected round-3 rule |
| N4 | carry | `AVKIT_E2E` | `implementation-plan.md:223` | `confirmed-consistent` | pre-existing value, read at the cited line: it agrees with the corrected round-3 rule |
| N4 | carry | `AVKIT_E2E` | `implementation-plan.md:343` | `confirmed-consistent` | pre-existing value, read at the cited line: it agrees with the corrected round-3 rule |
| N4 | carry | `AVKIT_E2E` | `census-round3-corrections.ps1:110` | `confirmed-consistent` | census declaration table (the sweep's own input list), not a plan assertion |
| N4 | carry | `AVKIT_E2E` | `assert-e2e-wired.ps1:4` | `confirmed-consistent` | pre-existing value, read at the cited line: it agrees with the corrected round-3 rule |
| N4 | carry | `AVKIT_E2E` | `assert-e2e-wired.ps1:13` | `confirmed-consistent` | pre-existing value, read at the cited line: it agrees with the corrected round-3 rule |
| N4 | carry | `AVKIT_E2E` | `assert-e2e-wired.ps1:67` | `confirmed-consistent` | pre-existing value, read at the cited line: it agrees with the corrected round-3 rule |
| N4 | carry | `AVKIT_E2E` | `assert-e2e-wired.ps1:84` | `confirmed-consistent` | pre-existing value, read at the cited line: it agrees with the corrected round-3 rule |
| N4 | carry | `AVKIT_E2E` | `assert-e2e-wired.ps1:88` | `confirmed-consistent` | pre-existing value, read at the cited line: it agrees with the corrected round-3 rule |
| N4 | carry | `AVKIT_REGION_PICKER_PATH` | `task.md:49` | `confirmed-consistent` | pre-existing value, read at the cited line: it agrees with the corrected round-3 rule |
| N4 | carry | `AVKIT_REGION_PICKER_PATH` | `task.md:50` | `confirmed-consistent` | pre-existing value, read at the cited line: it agrees with the corrected round-3 rule |
| N4 | carry | `AVKIT_REGION_PICKER_PATH` | `named-sets.json:28` | `confirmed-consistent` | pre-existing value, read at the cited line: it agrees with the corrected round-3 rule |
| N4 | carry | `AVKIT_REGION_PICKER_PATH` | `named-sets.json:83` | `confirmed-consistent` | pre-existing value, read at the cited line: it agrees with the corrected round-3 rule |
| N4 | carry | `AVKIT_REGION_PICKER_PATH` | `implementation-plan.md:169` | `confirmed-consistent` | pre-existing value, read at the cited line: it agrees with the corrected round-3 rule |
| N4 | carry | `AVKIT_REGION_PICKER_PATH` | `implementation-plan.md:223` | `confirmed-consistent` | pre-existing value, read at the cited line: it agrees with the corrected round-3 rule |
| N4 | carry | `AVKIT_REGION_PICKER_PATH` | `implementation-plan.md:224` | `confirmed-consistent` | pre-existing value, read at the cited line: it agrees with the corrected round-3 rule |
| N4 | carry | `AVKIT_REGION_PICKER_PATH` | `census-round3-corrections.ps1:111` | `confirmed-consistent` | census declaration table (the sweep's own input list), not a plan assertion |
| N4 | carry | `AVKIT_REGION_PICKER_PATH` | `assert-e2e-wired.ps1:14` | `confirmed-consistent` | pre-existing value, read at the cited line: it agrees with the corrected round-3 rule |
| N4 | carry | `AVKIT_REGION_PICKER_PATH` | `assert-e2e-wired.ps1:67` | `confirmed-consistent` | pre-existing value, read at the cited line: it agrees with the corrected round-3 rule |
| N4 | carry | `AVKIT_REGION_PICKER_PATH` | `assert-e2e-wired.ps1:77` | `confirmed-consistent` | pre-existing value, read at the cited line: it agrees with the corrected round-3 rule |
| N4 | carry | `AVKIT_REGION_PICKER_PATH` | `assert-e2e-wired.ps1:84` | `confirmed-consistent` | pre-existing value, read at the cited line: it agrees with the corrected round-3 rule |
| N5 | new | `census-round3-corrections.ps1` | `census-round3-corrections.ps1:36` | `confirmed-consistent` | census declaration table (the sweep's own input list), not a plan assertion |
| N5 | new | `census-round3-corrections.ps1` | `census-round3-corrections.ps1:114` | `confirmed-consistent` | census declaration table (the sweep's own input list), not a plan assertion |
| N5 | carry | `census-round1-corrections.ps1` | `census-round3-corrections.ps1:3` | `confirmed-consistent` | census declaration table (the sweep's own input list), not a plan assertion |
| N5 | carry | `census-round1-corrections.ps1` | `census-round3-corrections.ps1:36` | `confirmed-consistent` | census declaration table (the sweep's own input list), not a plan assertion |
| N5 | carry | `census-round1-corrections.ps1` | `census-round3-corrections.ps1:115` | `confirmed-consistent` | census declaration table (the sweep's own input list), not a plan assertion |
| N6 | old | `PLAN/` | `census-round3-corrections.ps1:118` | `confirmed-consistent` | census declaration table (the sweep's own input list), not a plan assertion |
| N6 | old | `Exact commands from implementation-plan.md` | `census-round3-corrections.ps1:119` | `confirmed-consistent` | census declaration table (the sweep's own input list), not a plan assertion |
| N6 | new | `run-verification-plan.ps1` | `census-round3-corrections.ps1:21` | `confirmed-consistent` | census declaration table (the sweep's own input list), not a plan assertion |
| N6 | new | `run-verification-plan.ps1` | `census-round3-corrections.ps1:120` | `confirmed-consistent` | census declaration table (the sweep's own input list), not a plan assertion |
| N6 | new | `run-verification-plan.ps1` | `implementation-plan.md:286` | `updated` | the value did not exist before the round-3 pass, so this line was written by that pass |
| N6 | new | `run-verification-plan.ps1` | `implementation-plan.md:321` | `updated` | the value did not exist before the round-3 pass, so this line was written by that pass |
| N6 | new | `run-verification-plan.ps1` | `implementation-plan.md:327` | `updated` | the value did not exist before the round-3 pass, so this line was written by that pass |
| N6 | new | `run-verification-plan.ps1` | `task.md:41` | `updated` | the value did not exist before the round-3 pass, so this line was written by that pass |
| N6 | new | `run-verification-plan.ps1` | `task.md:55` | `updated` | the value did not exist before the round-3 pass, so this line was written by that pass |
| N6 | new | `VERIFICATION_PLAN` | `run-verification-plan.ps1:44` | `updated` | the value did not exist before the round-3 pass, so this line was written by that pass |
| N6 | new | `VERIFICATION_PLAN` | `run-verification-plan.ps1:47` | `updated` | the value did not exist before the round-3 pass, so this line was written by that pass |
| N6 | new | `VERIFICATION_PLAN` | `run-verification-plan.ps1:68` | `updated` | the value did not exist before the round-3 pass, so this line was written by that pass |
| N6 | new | `VERIFICATION_PLAN` | `run-verification-plan.ps1:71` | `updated` | the value did not exist before the round-3 pass, so this line was written by that pass |
| N6 | new | `VERIFICATION_PLAN` | `census-round3-corrections.ps1:121` | `confirmed-consistent` | census declaration table (the sweep's own input list), not a plan assertion |
| N6 | carry | `docs/execution/plans/2026-08-27-p9-capture-native-picker/` | `task.md:3` | `confirmed-consistent` | pre-existing value, read at the cited line: it agrees with the corrected round-3 rule |
| N6 | carry | `docs/execution/plans/2026-08-27-p9-capture-native-picker/` | `task.md:40` | `confirmed-consistent` | pre-existing value, read at the cited line: it agrees with the corrected round-3 rule |
| N6 | carry | `docs/execution/plans/2026-08-27-p9-capture-native-picker/` | `task.md:41` | `confirmed-consistent` | pre-existing value, read at the cited line: it agrees with the corrected round-3 rule |
| N6 | carry | `docs/execution/plans/2026-08-27-p9-capture-native-picker/` | `task.md:44` | `confirmed-consistent` | pre-existing value, read at the cited line: it agrees with the corrected round-3 rule |
| N6 | carry | `docs/execution/plans/2026-08-27-p9-capture-native-picker/` | `task.md:46` | `confirmed-consistent` | pre-existing value, read at the cited line: it agrees with the corrected round-3 rule |
| N6 | carry | `docs/execution/plans/2026-08-27-p9-capture-native-picker/` | `task.md:47` | `confirmed-consistent` | pre-existing value, read at the cited line: it agrees with the corrected round-3 rule |
| N6 | carry | `docs/execution/plans/2026-08-27-p9-capture-native-picker/` | `task.md:48` | `confirmed-consistent` | pre-existing value, read at the cited line: it agrees with the corrected round-3 rule |
| N6 | carry | `docs/execution/plans/2026-08-27-p9-capture-native-picker/` | `task.md:49` | `confirmed-consistent` | pre-existing value, read at the cited line: it agrees with the corrected round-3 rule |
| N6 | carry | `docs/execution/plans/2026-08-27-p9-capture-native-picker/` | `task.md:50` | `confirmed-consistent` | pre-existing value, read at the cited line: it agrees with the corrected round-3 rule |
| N6 | carry | `docs/execution/plans/2026-08-27-p9-capture-native-picker/` | `task.md:52` | `confirmed-consistent` | pre-existing value, read at the cited line: it agrees with the corrected round-3 rule |
| N6 | carry | `docs/execution/plans/2026-08-27-p9-capture-native-picker/` | `task.md:54` | `confirmed-consistent` | pre-existing value, read at the cited line: it agrees with the corrected round-3 rule |
| N6 | carry | `docs/execution/plans/2026-08-27-p9-capture-native-picker/` | `task.md:55` | `confirmed-consistent` | pre-existing value, read at the cited line: it agrees with the corrected round-3 rule |
| N6 | carry | `docs/execution/plans/2026-08-27-p9-capture-native-picker/` | `task.md:59` | `confirmed-consistent` | pre-existing value, read at the cited line: it agrees with the corrected round-3 rule |
| N6 | carry | `docs/execution/plans/2026-08-27-p9-capture-native-picker/` | `task.md:60` | `confirmed-consistent` | pre-existing value, read at the cited line: it agrees with the corrected round-3 rule |
| N6 | carry | `docs/execution/plans/2026-08-27-p9-capture-native-picker/` | `task.md:62` | `confirmed-consistent` | pre-existing value, read at the cited line: it agrees with the corrected round-3 rule |
| N6 | carry | `docs/execution/plans/2026-08-27-p9-capture-native-picker/` | `task.md:65` | `confirmed-consistent` | pre-existing value, read at the cited line: it agrees with the corrected round-3 rule |
| N6 | carry | `docs/execution/plans/2026-08-27-p9-capture-native-picker/` | `task.md:66` | `confirmed-consistent` | pre-existing value, read at the cited line: it agrees with the corrected round-3 rule |
| N6 | carry | `docs/execution/plans/2026-08-27-p9-capture-native-picker/` | `task.md:67` | `confirmed-consistent` | pre-existing value, read at the cited line: it agrees with the corrected round-3 rule |
| N6 | carry | `docs/execution/plans/2026-08-27-p9-capture-native-picker/` | `named-sets.json:3` | `confirmed-consistent` | pre-existing value, read at the cited line: it agrees with the corrected round-3 rule |
| N6 | carry | `docs/execution/plans/2026-08-27-p9-capture-native-picker/` | `named-sets.json:4` | `confirmed-consistent` | pre-existing value, read at the cited line: it agrees with the corrected round-3 rule |
| N6 | carry | `docs/execution/plans/2026-08-27-p9-capture-native-picker/` | `named-sets.json:5` | `confirmed-consistent` | pre-existing value, read at the cited line: it agrees with the corrected round-3 rule |
| N6 | carry | `docs/execution/plans/2026-08-27-p9-capture-native-picker/` | `named-sets.json:149` | `confirmed-consistent` | pre-existing value, read at the cited line: it agrees with the corrected round-3 rule |
| N6 | carry | `docs/execution/plans/2026-08-27-p9-capture-native-picker/` | `named-sets.json:167` | `confirmed-consistent` | pre-existing value, read at the cited line: it agrees with the corrected round-3 rule |
| N6 | carry | `docs/execution/plans/2026-08-27-p9-capture-native-picker/` | `implementation-plan.md:327` | `confirmed-consistent` | pre-existing value, read at the cited line: it agrees with the corrected round-3 rule |
| N6 | carry | `docs/execution/plans/2026-08-27-p9-capture-native-picker/` | `census-round3-corrections.ps1:122` | `confirmed-consistent` | census declaration table (the sweep's own input list), not a plan assertion |
| N7 | old | `deferred` | `implementation-plan.md:295` | `confirmed-consistent` | retained mention - N7 itself: the Out-of-Scope row explains WHY the row is labeled out-of-scope rather than `deferred` (no registered MEU-ID). Quoting the rejected label is the finding, not a residue of it. |
| N7 | old | `deferred` | `census-round3-corrections.ps1:41` | `confirmed-consistent` | census declaration table (the sweep's own input list), not a plan assertion |
| N7 | old | `deferred` | `census-round3-corrections.ps1:124` | `confirmed-consistent` | census declaration table (the sweep's own input list), not a plan assertion |
| N7 | old | `deferred` | `census-round3-corrections.ps1:125` | `confirmed-consistent` | census declaration table (the sweep's own input list), not a plan assertion |
| N7 | new | `out-of-scope` | `implementation-plan.md:294` | `updated` | the value did not exist before the round-3 pass, so this line was written by that pass |
| N7 | new | `out-of-scope` | `implementation-plan.md:295` | `updated` | the value did not exist before the round-3 pass, so this line was written by that pass |
| N7 | new | `out-of-scope` | `implementation-plan.md:296` | `updated` | the value did not exist before the round-3 pass, so this line was written by that pass |
| N7 | new | `out-of-scope` | `implementation-plan.md:297` | `updated` | the value did not exist before the round-3 pass, so this line was written by that pass |
| N7 | new | `out-of-scope` | `implementation-plan.md:298` | `updated` | the value did not exist before the round-3 pass, so this line was written by that pass |
| N7 | new | `out-of-scope` | `implementation-plan.md:299` | `updated` | the value did not exist before the round-3 pass, so this line was written by that pass |
| N7 | new | `out-of-scope` | `implementation-plan.md:300` | `updated` | the value did not exist before the round-3 pass, so this line was written by that pass |
| N7 | new | `out-of-scope` | `implementation-plan.md:301` | `updated` | the value did not exist before the round-3 pass, so this line was written by that pass |
| N7 | new | `out-of-scope` | `census-round3-corrections.ps1:41` | `confirmed-consistent` | census declaration table (the sweep's own input list), not a plan assertion |
| N7 | new | `out-of-scope` | `census-round3-corrections.ps1:124` | `confirmed-consistent` | census declaration table (the sweep's own input list), not a plan assertion |
| N7 | new | `out-of-scope` | `census-round3-corrections.ps1:126` | `confirmed-consistent` | census declaration table (the sweep's own input list), not a plan assertion |
| X7-ac-count | old | `"AC_COUNT": 17` | `census-round3-corrections.ps1:129` | `confirmed-consistent` | census declaration table (the sweep's own input list), not a plan assertion |
| X7-ac-count | old | `17 ACs` | `census-round3-corrections.ps1:130` | `confirmed-consistent` | census declaration table (the sweep's own input list), not a plan assertion |
| X7-ac-count | new | `"AC_COUNT": 19` | `named-sets.json:110` | `updated` | the value did not exist before the round-3 pass, so this line was written by that pass |
| X7-ac-count | new | `"AC_COUNT": 19` | `census-round3-corrections.ps1:131` | `confirmed-consistent` | census declaration table (the sweep's own input list), not a plan assertion |
| X7-ac-count | carry | `AC_COUNT` | `task.md:60` | `confirmed-consistent` | pre-existing value, read at the cited line: it agrees with the corrected round-3 rule |
| X7-ac-count | carry | `AC_COUNT` | `named-sets.json:110` | `confirmed-consistent` | pre-existing value, read at the cited line: it agrees with the corrected round-3 rule |
| X7-ac-count | carry | `AC_COUNT` | `implementation-plan.md:107` | `confirmed-consistent` | pre-existing value, read at the cited line: it agrees with the corrected round-3 rule |
| X7-ac-count | carry | `AC_COUNT` | `census-round3-corrections.ps1:129` | `confirmed-consistent` | census declaration table (the sweep's own input list), not a plan assertion |
| X7-ac-count | carry | `AC_COUNT` | `census-round3-corrections.ps1:131` | `confirmed-consistent` | census declaration table (the sweep's own input list), not a plan assertion |
| X7-ac-count | carry | `AC_COUNT` | `census-round3-corrections.ps1:132` | `confirmed-consistent` | census declaration table (the sweep's own input list), not a plan assertion |
| X7-ac-count | carry | `AC_COUNT` | `census-round1-corrections.ps1:90` | `confirmed-consistent` | census declaration table (the sweep's own input list), not a plan assertion |
| X7-ac-count | carry | `AC_COUNT` | `assert-handoff-acs.ps1:2` | `confirmed-consistent` | pre-existing value, read at the cited line: it agrees with the corrected round-3 rule |
| X7-ac-count | carry | `AC_COUNT` | `assert-handoff-acs.ps1:9` | `confirmed-consistent` | pre-existing value, read at the cited line: it agrees with the corrected round-3 rule |
| X7-ac-count | carry | `AC_COUNT` | `assert-handoff-acs.ps1:17` | `confirmed-consistent` | pre-existing value, read at the cited line: it agrees with the corrected round-3 rule |
| X7-ac-count | carry | `AC_IDS` | `task.md:60` | `confirmed-consistent` | pre-existing value, read at the cited line: it agrees with the corrected round-3 rule |
| X7-ac-count | carry | `AC_IDS` | `named-sets.json:111` | `confirmed-consistent` | pre-existing value, read at the cited line: it agrees with the corrected round-3 rule |
| X7-ac-count | carry | `AC_IDS` | `census-round3-corrections.ps1:133` | `confirmed-consistent` | census declaration table (the sweep's own input list), not a plan assertion |
| X7-ac-count | carry | `AC_IDS` | `census-round1-corrections.ps1:91` | `confirmed-consistent` | census declaration table (the sweep's own input list), not a plan assertion |
| X7-ac-count | carry | `AC_IDS` | `assert-handoff-acs.ps1:3` | `confirmed-consistent` | pre-existing value, read at the cited line: it agrees with the corrected round-3 rule |
| X7-ac-count | carry | `AC_IDS` | `assert-handoff-acs.ps1:10` | `confirmed-consistent` | pre-existing value, read at the cited line: it agrees with the corrected round-3 rule |
| X7-ac-count | carry | `AC_IDS` | `assert-handoff-acs.ps1:21` | `confirmed-consistent` | pre-existing value, read at the cited line: it agrees with the corrected round-3 rule |
| X8-selftests | carry | `assert-oracle-selftests.ps1` | `task.md:40` | `confirmed-consistent` | pre-existing value, read at the cited line: it agrees with the corrected round-3 rule |
| X8-selftests | carry | `assert-oracle-selftests.ps1` | `run-verification-plan.ps1:19` | `confirmed-consistent` | pre-existing value, read at the cited line: it agrees with the corrected round-3 rule |
| X8-selftests | carry | `assert-oracle-selftests.ps1` | `implementation-plan.md:97` | `confirmed-consistent` | pre-existing value, read at the cited line: it agrees with the corrected round-3 rule |
| X8-selftests | carry | `assert-oracle-selftests.ps1` | `implementation-plan.md:285` | `confirmed-consistent` | pre-existing value, read at the cited line: it agrees with the corrected round-3 rule |
| X8-selftests | carry | `assert-oracle-selftests.ps1` | `implementation-plan.md:332` | `confirmed-consistent` | pre-existing value, read at the cited line: it agrees with the corrected round-3 rule |
| X8-selftests | carry | `assert-oracle-selftests.ps1` | `census-round3-corrections.ps1:134` | `confirmed-consistent` | census declaration table (the sweep's own input list), not a plan assertion |
| X8-selftests | carry | `assert-oracle-selftests.ps1` | `census-round1-corrections.ps1:96` | `confirmed-consistent` | census declaration table (the sweep's own input list), not a plan assertion |
| X8-selftests | carry | `assert-oracle-selftests.ps1` | `assert-closeout.ps1:18` | `confirmed-consistent` | pre-existing value, read at the cited line: it agrees with the corrected round-3 rule |
| X8-selftests | carry | `-SelfTest` | `task.md:40` | `confirmed-consistent` | pre-existing value, read at the cited line: it agrees with the corrected round-3 rule |
| X8-selftests | carry | `-SelfTest` | `task.md:41` | `confirmed-consistent` | pre-existing value, read at the cited line: it agrees with the corrected round-3 rule |
| X8-selftests | carry | `-SelfTest` | `task.md:82` | `confirmed-consistent` | pre-existing value, read at the cited line: it agrees with the corrected round-3 rule |
| X8-selftests | carry | `-SelfTest` | `implementation-plan.md:97` | `confirmed-consistent` | pre-existing value, read at the cited line: it agrees with the corrected round-3 rule |
| X8-selftests | carry | `-SelfTest` | `implementation-plan.md:216` | `confirmed-consistent` | pre-existing value, read at the cited line: it agrees with the corrected round-3 rule |
| X8-selftests | carry | `-SelfTest` | `implementation-plan.md:221` | `confirmed-consistent` | pre-existing value, read at the cited line: it agrees with the corrected round-3 rule |
| X8-selftests | carry | `-SelfTest` | `implementation-plan.md:225` | `confirmed-consistent` | pre-existing value, read at the cited line: it agrees with the corrected round-3 rule |
| X8-selftests | carry | `-SelfTest` | `implementation-plan.md:285` | `confirmed-consistent` | pre-existing value, read at the cited line: it agrees with the corrected round-3 rule |
| X8-selftests | carry | `-SelfTest` | `implementation-plan.md:286` | `confirmed-consistent` | pre-existing value, read at the cited line: it agrees with the corrected round-3 rule |
| X8-selftests | carry | `-SelfTest` | `implementation-plan.md:323` | `confirmed-consistent` | pre-existing value, read at the cited line: it agrees with the corrected round-3 rule |
| X8-selftests | carry | `-SelfTest` | `census-round3-corrections.ps1:135` | `confirmed-consistent` | census declaration table (the sweep's own input list), not a plan assertion |
| X8-selftests | carry | `-SelfTest` | `census-round1-corrections.ps1:97` | `confirmed-consistent` | census declaration table (the sweep's own input list), not a plan assertion |
| X8-selftests | carry | `-SelfTest` | `assert-task-rows.ps1:11` | `confirmed-consistent` | pre-existing value, read at the cited line: it agrees with the corrected round-3 rule |
| X8-selftests | carry | `-SelfTest` | `assert-picker-binding.ps1:14` | `confirmed-consistent` | pre-existing value, read at the cited line: it agrees with the corrected round-3 rule |
| X8-selftests | carry | `-SelfTest` | `assert-overlay-deleted.ps1:2` | `confirmed-consistent` | pre-existing value, read at the cited line: it agrees with the corrected round-3 rule |
| X8-selftests | carry | `-SelfTest` | `assert-oracle-selftests.ps1:7` | `confirmed-consistent` | pre-existing value, read at the cited line: it agrees with the corrected round-3 rule |
| X8-selftests | carry | `-SelfTest` | `assert-oracle-selftests.ps1:8` | `confirmed-consistent` | pre-existing value, read at the cited line: it agrees with the corrected round-3 rule |
| X8-selftests | carry | `-SelfTest` | `assert-oracle-selftests.ps1:9` | `confirmed-consistent` | pre-existing value, read at the cited line: it agrees with the corrected round-3 rule |
| X8-selftests | carry | `-SelfTest` | `assert-oracle-selftests.ps1:10` | `confirmed-consistent` | pre-existing value, read at the cited line: it agrees with the corrected round-3 rule |
| X8-selftests | carry | `-SelfTest` | `assert-oracle-selftests.ps1:11` | `confirmed-consistent` | pre-existing value, read at the cited line: it agrees with the corrected round-3 rule |
| X8-selftests | carry | `-SelfTest` | `assert-oracle-selftests.ps1:12` | `confirmed-consistent` | pre-existing value, read at the cited line: it agrees with the corrected round-3 rule |
| X8-selftests | carry | `-SelfTest` | `assert-oracle-selftests.ps1:13` | `confirmed-consistent` | pre-existing value, read at the cited line: it agrees with the corrected round-3 rule |
| X8-selftests | carry | `-SelfTest` | `assert-oracle-selftests.ps1:14` | `confirmed-consistent` | pre-existing value, read at the cited line: it agrees with the corrected round-3 rule |
| X8-selftests | carry | `-SelfTest` | `assert-e2e-wired.ps1:18` | `confirmed-consistent` | pre-existing value, read at the cited line: it agrees with the corrected round-3 rule |

## Round 4 — Corrections Re-Review

### Intent Anchor

Executing this plan is supposed to replace the Chromium capture overlay with a packaged .NET 8 WinForms picker, preserve the tested Electron/Python/API boundaries, and prove the real F2-to-publish path before implementation closeout. The current plan is not yet approvable: four scheduled controls accept concrete states in which predecessor work, native control binding, the capture-specific Electron E2E, or smoke-blocker evidence is materially absent.

### PR-6 Evidence Adjudication

PR-6 is sufficient and content review proceeds in this round. The supplied unfiltered receipt has 1,082 lines; the extra line is the RTK banner. A fresh run produced 1,081 substantive lines, exit `0`, `72 x 2 scopes = 144 sweeps`, 485 `FOLDER` dispositions, worst `rg` exit `0`, and `STALE SITES: 0`. The rolling correction log contains exactly 485 per-hit rows: 235 `updated`, 250 `confirmed-consistent`, no stale disposition, and the one declared retained `deferred` mention at `implementation-plan.md:295`. No changed literal, set, threshold, or predicate was found outside the declared census coverage.

### Round 3 Finding Adjudication

| Finding | Disposition | Current-file evidence |
|---------|-------------|-----------------------|
| N1 — task-row deadlock | `partially_resolved` | Predecessor scoping and the comma-wrap fix are correct: `assert-task-rows.ps1:40-41`, `:96-124`, and `:131-154` make `-Through` mandatory, allow an open boundary/successor, and reject unknown/empty boundaries. However, `:23`, `:36`, and `:54` define unfinished work only as the literal `` `[ ]` ``. The documented in-progress state at `task.md:75` is therefore treated as closed; the valid probe reports `in_progress_matches_open=False`. See R4-1. No other `ToArray()`/comma-wrap idiom exists in the target scripts. |
| N2 — method-specific binding and entrypoint reachability | `partially_resolved` | The handler map at `named-sets.json:33-38`, mapped-method check at `assert-picker-binding.ps1:37-47`, and B2/E2 self-tests at `:100-105` and `:131-135` resolve the two Round 3 counterexamples. But the gate still searches raw source text: comment-only mapped calls and an unreachable `if (false) { Run(... new RegionForm(...)); }` both pass. See R4-2. |
| N3 — production packaging path | `resolved` | `named-sets.json:19-24` owns the exact segments; `assert-packaging-clean.ps1:32-51` compares normalized `&&` segments rather than substrings, P1-P4 at `:63-97` reject the reported cases, and `:119-145` rebuilds through `npm --prefix ui run dist:prep`. The self-test passed. The destructive live build was not run. |
| N4 — real-Electron E2E and smoke evidence | `partially_resolved` | AC-40.18/19 now exist at `implementation-plan.md:224-225`; task rows 6/7a/9 schedule the spec, stub, real-Electron run, and smoke disposition (`task.md:48`, `:50`, `:52`). The controls themselves remain materially false-passing: marker-only E2E content and a nonexistent blocker receipt are accepted. See R4-3 and R4-4. |
| N5 — correction census | `resolved` | `census-round3-corrections.ps1:44-136` declares 72 values and `:168-241` enforces both scopes, per-hit dispositions, stale-site failure, and `rg` error propagation. The rerun and rolling 485-row log reconcile. |
| N6 — executable verification owner | `resolved` | `run-verification-plan.ps1:18-31` is the single executable 13-section inventory; `:34-48` checks scheduled gate-file existence, and `:51-72` executes each section with per-section receipts and first-failure propagation. `task.md:55` invokes it literally. Its self-test passed with all 13 sections present. |
| N7 — warm-process scope label | `resolved` | `implementation-plan.md:295` now uses `out-of-scope` / `—` and retains the Research-backed spawn-per-invocation basis plus the measured-latency trigger for proposing a new MEU. No unscheduled deferral is claimed. |

### Round 1 Regression Check

| Finding | Disposition | Current-file evidence |
|---------|-------------|-----------------------|
| F2 — phantom closeout validator | `resolved; not regressed` | `assert-closeout.ps1:10-59` invokes only on-disk plan gates plus existing `tools/check_exec_review.py` and `tools/meu_status.py`; the old validator survives only in the explanatory comment at `:2-3`, never as an invocation. |
| F5 — non-atomic publication | `resolved; not regressed` | `implementation-plan.md:173-184` still requires an in-inbox staging path, pixel guard, same-directory `renameSync`, staging-name suppression, and unlink/no-register on every non-confirm path. |
| F6 — RED rows end green | `resolved; not regressed` | Both RED oracle self-tests passed through `assert-oracle-selftests.ps1:8-9`; task rows 3 and 6 preserve the suite code, invoke `assert-red-oracle.ps1`, and exit with the gate code (`task.md:44`, `:48`). |
| F7 — repeated minimum edge | `resolved; not regressed` | The normative value is at `implementation-plan.md:154-160`, mirrored once for execution at `named-sets.json:11`; downstream AC/task text uses `PICKER_MIN_EDGE_PX`. |
| F8 — repeated exit mapping | `resolved; not regressed` | The normative open-world table remains at `implementation-plan.md:154-160`, mirrored at `named-sets.json:12-14`; AC/task text uses `PICKER_EXIT_*`, and unrecognized exit codes fail closed. |

### Round 4 Findings

| # | Severity | Finding | File:Line | Required correction |
|---|----------|---------|-----------|---------------------|
| R4-1 | High | **PR-4 / PR-8 — predecessor completeness accepts an in-progress or malformed predecessor as closed.** The gate records only whether a row contains `` `[ ]` `` and fails only when that boolean is true. A predecessor with the task legend's `` `[/]` `` state produces `in_progress_matches_open=False`, so H1-1/H2-4 can pass while required work is still in progress; any unrecognized status has the same shape. This violates the stated closed set `[x]` or `[B]`. | `assert-task-rows.ps1:20-23`, `assert-task-rows.ps1:33-38`, `assert-task-rows.ps1:52-60`, `assert-task-rows.ps1:149-154`; `task.md:70-77`; `C:/Temp/av-kit/r4-task-status-probe-valid.txt` | Parse and validate the status cell positively: every predecessor must be exactly `[x]` or `[B]`; `[ ]`, `[/]`, missing, duplicate, or unknown status must fail. Add self-tests for `[/]` and an invalid status. |
| R4-2 | High | **PR-8 — `PICKER_BINDING` still accepts a materially dead production path.** `Get-MethodBody` slices raw text and `Test-Binding`/`Test-Entrypoint` use `IndexOf`/regex presence. The demonstrated form contains each mapped `_controller.<method>(` only in a comment, and the demonstrated `Main` contains `Run(args, new RegionForm())` only inside `if (false)`; both return success. The xunit seam tests can remain green while real mouse/keyboard input or the shipped entrypoint never reaches them. | `assert-picker-binding.ps1:25-32`, `assert-picker-binding.ps1:35-69`, `assert-picker-binding.ps1:149-170`; `implementation-plan.md:215-216`; `C:/Temp/av-kit/r4-adversarial-probes-valid.txt` | Replace raw token presence with a syntax-aware or compiled/test-driven binding proof that rejects comments and unreachable/dead calls. Add the two demonstrated fixtures as negative self-tests and bind the real `Main`/handler path to an executable observable. |
| R4-3 | High | **PR-8 — `E2E_WIRED` accepts no capture E2E at all.** `Test-SpecBody` requires only the strings `AC-40.18` and `AVKIT_REGION_PICKER_PATH`; a file containing those two comments passes. Discoverability is inferred from directory/name strings, `test:e2e` is a substring check, `build:picker-stub` only has to be a script name, and the stub only has to be a directory. With the 11 existing Electron specs still running, a comment-only capture file plus hollow stub build can satisfy row 7a while no confirm/cancel/all-black assertion exists. The short-circuit guard likewise accepts `if (AVKIT_E2E) ... // AVKIT_REGION_PICKER_PATH`. | `assert-e2e-wired.ps1:36-59`, `assert-e2e-wired.ps1:100-137`; `implementation-plan.md:224-225`; `task.md:48-50`; `C:/Temp/av-kit/r4-adversarial-probes-valid.txt` | Make the control prove capture-specific test discovery/execution and required confirm/cancel/all-black assertions, validate the actual Playwright `testMatch`, reject comment-only guards, require the stub project files, and require a non-hollow build script. A capture-specific reporter/receipt or grep-free executable manifest may satisfy this. |
| R4-4 | High | **PR-8 / `[B]` contract — `SMOKE_DISPOSITION` accepts fabricated evidence.** The gate validates only nonempty strings; it never checks that `RECEIPT` exists, contains the reproduced command/error, or that a blocked disposition links a follow-up. The exact input `LATENCY_MS=`, `BLOCKED=yes`, `REASON=fabricated external blocker`, `RECEIPT=C:/Temp/av-kit/does-not-exist.txt` returns success. Row 9 and closeout can therefore close on no smoke evidence. | `assert-smoke-disposition.ps1:21-45`, `assert-smoke-disposition.ps1:77-80`; `task.md:52`, `task.md:86`; `C:/Temp/av-kit/r4-adversarial-probes-valid.txt` | Require `Test-Path` and a nonempty receipt, encode/check the allowed `[B]` class plus linked follow-up, and bind measured `LATENCY_MS` or the blocker to that receipt. Add nonexistent/empty receipt and missing-follow-up self-tests. |

No Critical, Medium, or Low findings were identified.

### PR-7 Scope-Basis Verdict

| Out-of-scope item(s) | Verdict | Basis checked |
|----------------------|---------|---------------|
| Chromium fallback | pass | Human-approved delete-entirely basis at `implementation-plan.md:294`. |
| Warm process | pass | Research-backed spawn-per-invocation basis and evidence-triggered future proposal at `implementation-plan.md:295`; no fake deferred MEU. |
| macOS/Linux; in-picker annotation | pass | Canonical named deferrals at `docs/build-plan/09-screenshot-capture.md:478-485`. |
| Python `mss` / MCP bbox | pass | Separate bbox/mss contract at `docs/build-plan/09-screenshot-capture.md:293`, `:333-340`, and `:409`. |
| REST/MCP route or schema changes | pass | MEU-37 and MEU-38 are `approved` at `.agent/context/meu-status.yaml:998-1035`; this plan keeps those bodies unchanged. |
| WGC; Snipping Tool protocol | pass | GDI ShareX map at `docs/build-plan/09-screenshot-capture.md:569-576` and unpackaged NSIS basis at `docs/build-plan/07-distribution.md:177-180`. |

### Checklist Verdicts

| Check | Result | Evidence |
|-------|--------|----------|
| PR-1 Plan/task alignment | pass | Both artifacts describe MEU-40 in the same WP/task order, with the same helper, overlay deletion, publication, E2E, handoff, review, and closeout outputs. |
| PR-2 Not-started confirmation | pass | `native/region-picker`, `region-picker-tests`, stub, `capture-picker.ts`, capture E2E, MEU handoff, and implementation review are absent; all 26 actionable task rows are open. |
| PR-3 Task contract completeness | pass | Every actionable row has task, owner, deliverable, executable validation, dependencies, context strategy, durable outputs, builder model, and status. All task-named scripts/tools and `rtk`/`pwsh`/`dotnet`/`npm`/`uv` exist. |
| PR-4 Validation realism | **fail** | R4-1, R4-3, and R4-4 demonstrate materially unfinished or absent evidence that passes scheduled validation. |
| PR-5 Source-backed planning | pass | All 19 ACs use Spec, Local Canon, Research-backed, or Human-approved bases; no new unsourced product behavior was found. |
| PR-6 Handoff/corrections readiness | pass | The 1,082-line supplied receipt, fresh 144-sweep rerun, and 485-row per-hit log are complete and reconciled. |
| PR-7 Scope discipline | pass | Every row has a verified source basis; no `deferred` row lacks a registered MEU, and no current contract work is disguised as out of scope. |
| PR-8 Control reachability and totality | **fail** | R4-1 through R4-4 provide concrete false-pass inputs. Exit-code classification and same-directory publication otherwise remain exhaustive/atomic. |
| PR-9 Single-statement discipline | pass | Named thresholds, exit sets, binding map, package segments, row boundaries, paths, and AC set have one normative definition plus their executable named-set mirror; no materially conflicting live spelling was found. The Verification runner is the sole executable section owner. |
| DR-1 Claim-to-state match | **fail** | N1/N2/N4 correction claims overstate what their current predicates prove. |
| DR-2 Residual old terms | pass | Old forms survive only in census declaration tables and N7's single allowlisted explanation; the self-enforcing rerun reports zero stale sites. |
| DR-3 Downstream references updated | pass | Plan/task, named sets, all new gates, verification runner, packaging, E2E/stub, handoff/review/reflection, specs, registry, and hub audit are inventoried consistently. |
| DR-4 Verification robustness | **fail** | The four High findings each permit a materially missing deliverable/evidence path to pass. |
| DR-5 Evidence auditability | pass | Receipts, exact paths, rerunnable scripts, 19/19 AC set, executable inventory, and adversarial probes are reproducible. |
| DR-6 Cross-reference integrity | pass | The plan consistently revises only the Electron/native picker slot while retaining Python `mss`, approved REST/MCP, filmstrip, and annotation boundaries. |
| DR-7 Evidence freshness | pass | Fresh runs reproduce eight oracle suites passing, the 13-section inventory, 72x2 census, 485 dispositions, and exact AC membership: 19 actual, `AC_COUNT=19`, 19 `AC_IDS`, no missing/extra IDs. |
| DR-8 Completion vs residual risk | pass | The project remains draft/unstarted and makes no implementation-complete claim. |

### Commands Executed

All commands used RTK routing and redirected all streams to `C:/Temp/av-kit/`; exit codes were captured before receipt reads. Key receipts: `r4-census-rerun.txt`, `r4-census-integrity.txt`, `r4-oracle-selftests.txt`, `r4-verification-inventory.txt`, `r4-adversarial-probes-valid.txt`, `r4-task-status-probe-valid.txt`, `r4-ac-totality.txt`, `r4-executable-audit.txt`, `r4-pr7-bases.txt`, `r4-pr7-more.txt`, and `r4-pr9-sweep.txt`. `assert-packaging-clean.ps1` was not run without `-SkipBuild`; no implementation/live gate was run against absent planned files.

### Follow-up Actions

1. Make task predecessor status fail closed unless exactly `[x]` or `[B]`, with `[/]`/invalid self-tests.
2. Replace raw-source native binding presence with a proof that comments and unreachable calls cannot satisfy.
3. Bind the E2E gate to actual capture-specific Playwright tests, stub project/build semantics, and executed test evidence.
4. Bind smoke disposition to an existing nonempty receipt and the complete `[B]` reason/follow-up contract.
5. Re-run the full oracle suite, verification inventory, and a correction census covering every changed predicate before Round 5.

### Open Questions / Assumptions

No product decision is required. The Human-approved C# WinForms/no-fallback decisions and the post-cap `continue until approved` direction remain governing; the latter authorizes another correction/review round, not execution or approval by fiat.

### Residual Risk

After these controls are corrected, real multi-monitor/DPI WinForms behavior, clean self-contained packaging, and Electron launch remain execution-time risks to be resolved by the planned xunit, clean packaging, real-Electron Playwright, and live-smoke receipts. Those risks do not excuse the current false-passing closeout controls.

### Verdict

`changes_required` — PR-6 is sufficient; N3/N5/N6/N7 and F2/F5/F6/F7/F8 are resolved without regression; AC membership is exactly 19. Four evidence-backed High findings remain because the task-row, native-binding, capture-E2E, and smoke-evidence gates each accept a concrete materially incomplete state. Continue through `/plan-corrections`, then return to this same rolling file for Round 5; do not enter execution.

---

## Round 4 Corrections — Blast-Radius Census & Disposition Log

> Implementor-authored evidence appended under explicit human direction
> (`USER_EXPLICIT`: "continue until approved"). This section makes no verdict claim; it
> supplies the PR-6 census and per-hit correction log that Round 5 requires before content
> review resumes. All four Round 4 High findings were treated as blocking.

### What was corrected (Round 4 findings R4-1 – R4-4)

| # | Finding | Correction landed |
|---|---------|-------------------|
| R4-1 | Predecessor status was the single boolean "the line contains `` `[ ]` ``", so `` `[/]` ``, a missing cell, a malformed cell, or any unknown marker counted as **closed** | `assert-task-rows.ps1` now parses the status **positively** from the row's *last* cell (row 7a's prose legitimately contains an inline `` `[B]` ``, so a whole-line scan is ambiguous by construction). That cell must hold **exactly one** status-shaped token and nothing else; `closed = [x] \| [B]`, `open = [ ] \| [/]`, everything else is `invalid`. An invalid row **anywhere** in the table fails the gate, before the predecessor-boundary check. New self-tests: **T6** (`[/]` predecessor blocks), **T7** (unknown marker), **T8** (missing / unterminated marker), **T9** (duplicate or decorated cell), **T10** (row 7a's inline `[B]` in prose is *not* read as a status), **T11** (a malformed successor still fails). |
| R4-2 | `PICKER_BINDING` sliced raw text, so a mapped call appearing only in a comment, and a `Main` whose `Run(args, new RegionForm())` sat inside `if (false)`, both passed | Split into a hardened static **pre-check** and an **executed** proof. Static: `Remove-CommentsAndLiterals` strips `//`, `/* */`, and both string-literal forms before any scan; `Test-DeadCode` rejects every `BINDING_DEADCODE_FORMS` marker outright; `Get-TopLevelStatements` now *discards* nested block text rather than merely not splitting it, so a conditionally-nested `Run` can no longer be read as a top-level statement. Executed: new **AC-40.20** — `BindingReachabilityTests.cs` parses the production syntax tree with Roslyn and asserts each handler→controller edge and the unconditional `Main`→`Run(…, new RegionForm(…))` edge, counting neither comments nor dead-code regions. Task row 4a runs it (`--filter FullyQualifiedName~BindingReachabilityTests` → `C:/Temp/av-kit/dotnet-binding.txt`) and the gate fails unless that receipt shows `Failed: 0` and `Passed >=` the named-test count — a zero-match filter exits `0`, so the count is asserted explicitly. New self-tests: **B4/B4b/B4c** (line-comment, block-comment, string-literal calls), **B5/B5b** (dead-code and conditionally-nested entrypoints), **E3** (a *legitimate* `if (args.Length == 0) { PrintUsage(); return 1; }` guard must still pass — proving the stricter rule is not over-strict), **R1** (zero/short filter match), **R2** (absent receipt), **R3** (`Failed: 1`). |
| R4-3 | `E2E_WIRED` required only the strings `AC-40.18` and `AVKIT_REGION_PICKER_PATH`, so a two-comment file passed and nothing proved the capture spec ever *ran* | The gate now has two modes. `-Mode Wired`: `Remove-TsComments` (string literals preserved, so test titles survive) strips comments before every check; each `E2E_REQUIRED_CASES` title must appear as a real `test("…")` declaration; the override must be named outside comments; the short-circuit guard is checked on comment-stripped source; `test:e2e:capture` must carry every `E2E_CAPTURE_REQUIRED_SEGMENTS` segment, `build:picker-stub` must contain `dotnet publish`, and `E2E_STUB_PROJECT_FILE` must exist on disk. `-Mode Executed`: the run emits a Playwright **JSON report** to `E2E_EXECUTED_RECEIPT` via `PLAYWRIGHT_JSON_OUTPUT_NAME` (console stream still redirected to `C:/Temp/av-kit/` per P0, so the JSON stays unpolluted); `Get-ReportedSpecs` flattens the report tree recursively and `Test-ExecutedReport` requires `stats.unexpected`/`skipped`/`flaky` all `0`, `stats.expected >=` the case count, and every required case present, `ok`, all statuses `expected`, and attributed to the capture spec's own file. New self-tests: **S4** (comment-only markers), **S5** (missing case), **G3** (comment guard), **X1–X6** (missing case, failing, skipped, empty/non-JSON, wrong spec file, short run). |
| R4-4 | `SMOKE_DISPOSITION` validated only non-empty strings — the reviewer's exact input (`BLOCKED=yes`, `RECEIPT=C:/Temp/av-kit/does-not-exist.txt`) returned success | `Test-Disposition` now requires the `RECEIPT` to **exist** (`Test-Path`) and be non-empty. `BLOCKED=no` additionally requires an integer `LATENCY_MS >= 1` **whose value literally appears inside that receipt** — the latency is measured, not asserted. `BLOCKED=yes` requires a non-empty `REASON`, a `CLASS` drawn from `SMOKE_BLOCKED_CLASSES` (`external-error` / `missing-dependency` / `human-decision` — the AGENTS.md `[B]` triad, so subjective classes are rejected by construction), and a `FOLLOWUP` matching `SMOKE_FOLLOWUP_PATTERN`. Row 9 now produces a measurement receipt (`C:/Temp/av-kit/live-smoke.txt`) alongside the disposition. New self-tests: **D6** (the reviewer's nonexistent-receipt input), **D7** (empty receipt), **D8** (subjective class `out-of-scope`), **D9/D9b** (missing / free-text follow-up), **D10** (latency absent from the receipt). |

Collateral, in the same pass: `AC_COUNT` 19 → **20** (AC-40.20 added) with `AC_IDS` extended; the
Verification Plan grew 13 → **16** scheduled sections (`5b` BINDING_RUNTIME, `5c` PICKER_BINDING,
`9a` E2E_WIRED-Wired, `9b` UI_E2E, `9c` E2E_CAPTURE_RUN, `9d` E2E_EXECUTED, `10` SMOKE_DISPOSITION),
and `run-verification-plan.ps1` gained per-step environment support so §9c can set
`PLAYWRIGHT_JSON_OUTPUT_NAME`. The three native project files were renamed to match their
published exe basenames (`avkit-region-picker.csproj`, `avkit-region-picker-tests.csproj`,
`avkit-region-picker-stub.csproj`), closing a latent drift between `PICKER_EXE_REL` /
`E2E_STUB_EXE_REL` and the plan's file table.

### Census receipt

- **Receipt (complete, untruncated):** `C:/Temp/av-kit/census-p9-native-picker-round4-corrections.txt` — 1,572 lines, script exit `0`.
- **Sweep script (re-runnable):** `docs/execution/plans/2026-08-27-p9-capture-native-picker/census-round4-corrections.ps1`
- **Method:** `rg -F -n --no-heading --with-filename` (fixed-string, so regex metacharacters in a value cannot silently change what was searched). No `head`, `tail`, `Select-Object`, or `Where-Object` appears anywhere in the sweep or in the receipt.
- **Coverage:** 109 declared values × 2 scopes = **218 sweeps**. Scope `PAIR` = `implementation-plan.md` + `task.md`; scope `FOLDER` = every file in the plan folder, because `named-sets.json`, the `assert-*.ps1` gates, and `run-verification-plan.ps1` are themselves part of the correction and must agree with the prose. `FOLDER` is a superset of `PAIR`, so the log below enumerates `FOLDER` hits; the receipt carries both.
- **Directions:** every changed literal, term, count, set, threshold, and predicate was swept in **three** declared directions — `old`, `new`, and `carry` — with the same contract as the Round 3 census.
- **Exit codes:** worst `rg` exit code across all 218 sweeps = `0`; no sweep returned `>1`, so none failed to execute.
- **Self-enforcing:** the sweep script **exits 3** if any `old` form survives outside a census declaration table or the declared retained-mention allowlist. This run exits `0` with `STALE SITES: 0`.
- **Total hits dispositioned below: 724** — every `file:line` in the receipt's `FOLDER` scope (244 `updated`, 480 `confirmed-consistent`, 0 stale).

### Old-form sweeps (stale text removed)

| Finding | Old form swept | PAIR result |
|---|---|---|
| R4-1 | `OpenPattern` | `rc=1` no match |
| R4-1 | `Test-Open` | `rc=1` no match |
| R4-1 | `openAll` | `rc=1` no match |
| R4-3 | `AvKit.RegionPicker.Stub.csproj` | `rc=1` no match |
| X-ac-count | `"AC_COUNT": 19` | `rc=1` no match |
| X-ac-count | `19 ACs` | `rc=1` no match |
| X-sections | `13 sections` | `rc=1` no match |
| X-sections | `13-section` | `rc=1` no match |
| X-sections | `\| 5b \| `assert-picker-binding.ps1` \|` | `rc=1` no match |
| X-sections | `\| 9a \| `assert-e2e-wired.ps1` \|` | `rc=1` no match |
| X-csproj | `AvKit.RegionPicker.csproj` | `rc=1` no match |
| X-csproj | `AvKit.RegionPicker.Tests.csproj` | `rc=1` no match |

Every `old` form is gone from both scopes. The Round 3 retained mention (`deferred` at
`implementation-plan.md`) is not a Round 4 value and is therefore not re-swept here; it is
unchanged and still allowlisted in `census-round3-corrections.ps1`.

### Gate self-test and inventory receipts (re-run after the corrections)

| Receipt | Result |
|---|---|
| `C:/Temp/av-kit/oracle-selftests.txt` | `PASS: ORACLE_SELFTESTS 8 gates proven non-vacuous` — exit `0`. Task rows T1–T11; red oracle × 2; overlay deletion; binding B1–B3, B4/B4b/B4c, B5/B5b, E1–E3, R1–R3; packaging P1–P4; E2E wiring S1–S5, G1–G3, X1–X6; smoke disposition D1–D10. |
| `C:/Temp/av-kit/verification-plan-inventory.txt` | `PASS: VERIFICATION_PLAN inventory (16 sections, every gate script present)` — exit `0`. |
| `C:/Temp/av-kit/census-p9-native-picker-round4-corrections.txt` | `STALE SITES: 0` — exit `0`, 1,572 lines. |

> One defect was found *by* re-running the oracles rather than by inspection: the first
> `Get-TopLevelStatements` tracked brace depth but still appended nested characters, so
> `if (args.Length > 99) { Run(args, new RegionForm()); } return 1;` collapsed into one
> depth-0 statement containing both required tokens and self-test **B5b** failed. Nested
> text is now dropped entirely, and positive self-test **E3** was added so the stricter
> rule is proven not to reject a legitimate argument guard. The gate was never trusted
> while it was red.

### Per-hit disposition log (724 rows, nothing dropped)

| Finding | Dir | Value | Site (`file:line`) | Disposition | Justification |
|---|---|---|---|---|---|
| R4-1 | old | `OpenPattern` | `census-round4-corrections.ps1:51` | `confirmed-consistent` | census declaration table (the sweep's own input list), not a plan assertion |
| R4-1 | old | `Test-Open` | `census-round4-corrections.ps1:52` | `confirmed-consistent` | census declaration table (the sweep's own input list), not a plan assertion |
| R4-1 | old | `openAll` | `census-round4-corrections.ps1:53` | `confirmed-consistent` | census declaration table (the sweep's own input list), not a plan assertion |
| R4-1 | new | `Get-RowStatus` | `census-round4-corrections.ps1:54` | `confirmed-consistent` | census declaration table (the sweep's own input list), not a plan assertion |
| R4-1 | new | `Get-RowStatus` | `assert-task-rows.ps1:46` | `updated` | the value did not exist before the round-4 pass, so this line was written by that pass |
| R4-1 | new | `Get-RowStatus` | `assert-task-rows.ps1:85` | `updated` | the value did not exist before the round-4 pass, so this line was written by that pass |
| R4-1 | new | `Get-RowStatus` | `assert-task-rows.ps1:187` | `updated` | the value did not exist before the round-4 pass, so this line was written by that pass |
| R4-1 | new | `Get-RowStatus` | `assert-task-rows.ps1:201` | `updated` | the value did not exist before the round-4 pass, so this line was written by that pass |
| R4-1 | new | `Get-RowStatus` | `assert-task-rows.ps1:203` | `updated` | the value did not exist before the round-4 pass, so this line was written by that pass |
| R4-1 | new | `Get-RowStatus` | `assert-task-rows.ps1:207` | `updated` | the value did not exist before the round-4 pass, so this line was written by that pass |
| R4-1 | new | `Get-RowStatus` | `assert-task-rows.ps1:209` | `updated` | the value did not exist before the round-4 pass, so this line was written by that pass |
| R4-1 | new | `Get-RowStatus` | `assert-task-rows.ps1:213` | `updated` | the value did not exist before the round-4 pass, so this line was written by that pass |
| R4-1 | new | `Get-RowStatus` | `assert-task-rows.ps1:215` | `updated` | the value did not exist before the round-4 pass, so this line was written by that pass |
| R4-1 | new | `Get-RowStatus` | `assert-task-rows.ps1:220` | `updated` | the value did not exist before the round-4 pass, so this line was written by that pass |
| R4-1 | new | `StatusCellPattern` | `census-round4-corrections.ps1:55` | `confirmed-consistent` | census declaration table (the sweep's own input list), not a plan assertion |
| R4-1 | new | `StatusCellPattern` | `assert-task-rows.ps1:42` | `updated` | the value did not exist before the round-4 pass, so this line was written by that pass |
| R4-1 | new | `StatusCellPattern` | `assert-task-rows.ps1:66` | `updated` | the value did not exist before the round-4 pass, so this line was written by that pass |
| R4-1 | new | `StatusTokenPattern` | `census-round4-corrections.ps1:56` | `confirmed-consistent` | census declaration table (the sweep's own input list), not a plan assertion |
| R4-1 | new | `StatusTokenPattern` | `assert-task-rows.ps1:40` | `updated` | the value did not exist before the round-4 pass, so this line was written by that pass |
| R4-1 | new | `StatusTokenPattern` | `assert-task-rows.ps1:59` | `updated` | the value did not exist before the round-4 pass, so this line was written by that pass |
| R4-1 | new | `RowIdPattern` | `assert-task-rows.ps1:38` | `updated` | the value did not exist before the round-4 pass, so this line was written by that pass |
| R4-1 | new | `RowIdPattern` | `assert-task-rows.ps1:83` | `updated` | the value did not exist before the round-4 pass, so this line was written by that pass |
| R4-1 | new | `RowIdPattern` | `census-round4-corrections.ps1:57` | `confirmed-consistent` | census declaration table (the sweep's own input list), not a plan assertion |
| R4-1 | new | `ClosedMarkers` | `census-round4-corrections.ps1:58` | `confirmed-consistent` | census declaration table (the sweep's own input list), not a plan assertion |
| R4-1 | new | `ClosedMarkers` | `assert-task-rows.ps1:43` | `updated` | the value did not exist before the round-4 pass, so this line was written by that pass |
| R4-1 | new | `ClosedMarkers` | `assert-task-rows.ps1:71` | `updated` | the value did not exist before the round-4 pass, so this line was written by that pass |
| R4-1 | new | `invalidAll` | `census-round4-corrections.ps1:59` | `confirmed-consistent` | census declaration table (the sweep's own input list), not a plan assertion |
| R4-1 | new | `invalidAll` | `assert-task-rows.ps1:100` | `updated` | the value did not exist before the round-4 pass, so this line was written by that pass |
| R4-1 | new | `invalidAll` | `assert-task-rows.ps1:111` | `updated` | the value did not exist before the round-4 pass, so this line was written by that pass |
| R4-1 | new | `invalidAll` | `assert-task-rows.ps1:117` | `updated` | the value did not exist before the round-4 pass, so this line was written by that pass |
| R4-1 | new | `invalidAll` | `assert-task-rows.ps1:119` | `updated` | the value did not exist before the round-4 pass, so this line was written by that pass |
| R4-1 | new | `invalidAll` | `assert-task-rows.ps1:174` | `updated` | the value did not exist before the round-4 pass, so this line was written by that pass |
| R4-1 | new | `invalidAll` | `assert-task-rows.ps1:233` | `updated` | the value did not exist before the round-4 pass, so this line was written by that pass |
| R4-1 | new | `invalidAll` | `assert-task-rows.ps1:252` | `updated` | the value did not exist before the round-4 pass, so this line was written by that pass |
| R4-1 | new | `invalidAll` | `assert-task-rows.ps1:254` | `updated` | the value did not exist before the round-4 pass, so this line was written by that pass |
| R4-1 | new | `invalidLines` | `census-round4-corrections.ps1:60` | `confirmed-consistent` | census declaration table (the sweep's own input list), not a plan assertion |
| R4-1 | new | `invalidLines` | `assert-task-rows.ps1:119` | `updated` | the value did not exist before the round-4 pass, so this line was written by that pass |
| R4-1 | new | `invalidLines` | `assert-task-rows.ps1:253` | `updated` | the value did not exist before the round-4 pass, so this line was written by that pass |
| R4-1 | new | `parsed positively` | `task.md:84` | `updated` | the value did not exist before the round-4 pass, so this line was written by that pass |
| R4-1 | new | `parsed positively` | `census-round4-corrections.ps1:61` | `confirmed-consistent` | census declaration table (the sweep's own input list), not a plan assertion |
| R4-1 | carry | `assert-task-rows.ps1` | `task.md:54` | `confirmed-consistent` | pre-existing value, read at the cited line: it agrees with the corrected round-4 rule |
| R4-1 | carry | `assert-task-rows.ps1` | `task.md:83` | `confirmed-consistent` | pre-existing value, read at the cited line: it agrees with the corrected round-4 rule |
| R4-1 | carry | `assert-task-rows.ps1` | `implementation-plan.md:102` | `confirmed-consistent` | pre-existing value, read at the cited line: it agrees with the corrected round-4 rule |
| R4-1 | carry | `assert-task-rows.ps1` | `implementation-plan.md:289` | `confirmed-consistent` | pre-existing value, read at the cited line: it agrees with the corrected round-4 rule |
| R4-1 | carry | `assert-task-rows.ps1` | `census-round4-corrections.ps1:50` | `confirmed-consistent` | census declaration table (the sweep's own input list), not a plan assertion |
| R4-1 | carry | `assert-task-rows.ps1` | `census-round4-corrections.ps1:62` | `confirmed-consistent` | census declaration table (the sweep's own input list), not a plan assertion |
| R4-1 | carry | `assert-task-rows.ps1` | `census-round3-corrections.ps1:58` | `confirmed-consistent` | census declaration table (the sweep's own input list), not a plan assertion |
| R4-1 | carry | `assert-task-rows.ps1` | `census-round1-corrections.ps1:27` | `confirmed-consistent` | census declaration table (the sweep's own input list), not a plan assertion |
| R4-1 | carry | `assert-task-rows.ps1` | `assert-oracle-selftests.ps1:7` | `confirmed-consistent` | pre-existing value, read at the cited line: it agrees with the corrected round-4 rule |
| R4-1 | carry | `assert-task-rows.ps1` | `assert-closeout.ps1:21` | `confirmed-consistent` | pre-existing value, read at the cited line: it agrees with the corrected round-4 rule |
| R4-1 | carry | `TASK_ROW_GATE` | `implementation-plan.md:102` | `confirmed-consistent` | pre-existing value, read at the cited line: it agrees with the corrected round-4 rule |
| R4-1 | carry | `TASK_ROW_GATE` | `census-round4-corrections.ps1:63` | `confirmed-consistent` | census declaration table (the sweep's own input list), not a plan assertion |
| R4-1 | carry | `TASK_ROW_GATE` | `census-round3-corrections.ps1:59` | `confirmed-consistent` | census declaration table (the sweep's own input list), not a plan assertion |
| R4-1 | carry | `TASK_ROW_GATE` | `census-round1-corrections.ps1:28` | `confirmed-consistent` | census declaration table (the sweep's own input list), not a plan assertion |
| R4-1 | carry | `TASK_ROW_GATE` | `assert-task-rows.ps1:235` | `confirmed-consistent` | pre-existing value, read at the cited line: it agrees with the corrected round-4 rule |
| R4-1 | carry | `TASK_ROW_GATE` | `assert-task-rows.ps1:243` | `confirmed-consistent` | pre-existing value, read at the cited line: it agrees with the corrected round-4 rule |
| R4-1 | carry | `TASK_ROW_GATE` | `assert-task-rows.ps1:249` | `confirmed-consistent` | pre-existing value, read at the cited line: it agrees with the corrected round-4 rule |
| R4-1 | carry | `TASK_ROW_GATE` | `assert-task-rows.ps1:254` | `confirmed-consistent` | pre-existing value, read at the cited line: it agrees with the corrected round-4 rule |
| R4-1 | carry | `TASK_ROW_GATE` | `assert-task-rows.ps1:258` | `confirmed-consistent` | pre-existing value, read at the cited line: it agrees with the corrected round-4 rule |
| R4-1 | carry | `TASK_ROW_GATE` | `assert-task-rows.ps1:262` | `confirmed-consistent` | pre-existing value, read at the cited line: it agrees with the corrected round-4 rule |
| R4-1 | carry | `TASK_ROW_GATE` | `assert-task-rows.ps1:267` | `confirmed-consistent` | pre-existing value, read at the cited line: it agrees with the corrected round-4 rule |
| R4-1 | carry | `TASK_ROW_GATE` | `assert-task-rows.ps1:270` | `confirmed-consistent` | pre-existing value, read at the cited line: it agrees with the corrected round-4 rule |
| R4-1 | carry | `TASK_ROW_GATE` | `assert-oracle-selftests.ps1:7` | `confirmed-consistent` | pre-existing value, read at the cited line: it agrees with the corrected round-4 rule |
| R4-1 | carry | `TASK_ROW_GATE` | `assert-closeout.ps1:21` | `confirmed-consistent` | pre-existing value, read at the cited line: it agrees with the corrected round-4 rule |
| R4-1 | carry | `Measure-Predecessors` | `census-round4-corrections.ps1:64` | `confirmed-consistent` | census declaration table (the sweep's own input list), not a plan assertion |
| R4-1 | carry | `Measure-Predecessors` | `census-round3-corrections.ps1:55` | `confirmed-consistent` | census declaration table (the sweep's own input list), not a plan assertion |
| R4-1 | carry | `Measure-Predecessors` | `assert-task-rows.ps1:101` | `confirmed-consistent` | pre-existing value, read at the cited line: it agrees with the corrected round-4 rule |
| R4-1 | carry | `Measure-Predecessors` | `assert-task-rows.ps1:156` | `confirmed-consistent` | pre-existing value, read at the cited line: it agrees with the corrected round-4 rule |
| R4-1 | carry | `Measure-Predecessors` | `assert-task-rows.ps1:171` | `confirmed-consistent` | pre-existing value, read at the cited line: it agrees with the corrected round-4 rule |
| R4-1 | carry | `Measure-Predecessors` | `assert-task-rows.ps1:177` | `confirmed-consistent` | pre-existing value, read at the cited line: it agrees with the corrected round-4 rule |
| R4-1 | carry | `Measure-Predecessors` | `assert-task-rows.ps1:181` | `confirmed-consistent` | pre-existing value, read at the cited line: it agrees with the corrected round-4 rule |
| R4-1 | carry | `Measure-Predecessors` | `assert-task-rows.ps1:197` | `confirmed-consistent` | pre-existing value, read at the cited line: it agrees with the corrected round-4 rule |
| R4-1 | carry | `Measure-Predecessors` | `assert-task-rows.ps1:232` | `confirmed-consistent` | pre-existing value, read at the cited line: it agrees with the corrected round-4 rule |
| R4-1 | carry | `Measure-Predecessors` | `assert-task-rows.ps1:247` | `confirmed-consistent` | pre-existing value, read at the cited line: it agrees with the corrected round-4 rule |
| R4-1 | carry | `-Through` | `task.md:54` | `confirmed-consistent` | pre-existing value, read at the cited line: it agrees with the corrected round-4 rule |
| R4-1 | carry | `-Through` | `task.md:67` | `confirmed-consistent` | pre-existing value, read at the cited line: it agrees with the corrected round-4 rule |
| R4-1 | carry | `-Through` | `task.md:83` | `confirmed-consistent` | pre-existing value, read at the cited line: it agrees with the corrected round-4 rule |
| R4-1 | carry | `-Through` | `census-round4-corrections.ps1:65` | `confirmed-consistent` | census declaration table (the sweep's own input list), not a plan assertion |
| R4-1 | carry | `-Through` | `census-round3-corrections.ps1:50` | `confirmed-consistent` | census declaration table (the sweep's own input list), not a plan assertion |
| R4-1 | carry | `-Through` | `census-round3-corrections.ps1:51` | `confirmed-consistent` | census declaration table (the sweep's own input list), not a plan assertion |
| R4-1 | carry | `-Through` | `census-round3-corrections.ps1:52` | `confirmed-consistent` | census declaration table (the sweep's own input list), not a plan assertion |
| R4-1 | carry | `-Through` | `assert-task-rows.ps1:12` | `confirmed-consistent` | pre-existing value, read at the cited line: it agrees with the corrected round-4 rule |
| R4-1 | carry | `-Through` | `assert-task-rows.ps1:14` | `confirmed-consistent` | pre-existing value, read at the cited line: it agrees with the corrected round-4 rule |
| R4-1 | carry | `-Through` | `assert-task-rows.ps1:243` | `confirmed-consistent` | pre-existing value, read at the cited line: it agrees with the corrected round-4 rule |
| R4-1 | carry | `-Through` | `assert-closeout.ps1:21` | `confirmed-consistent` | pre-existing value, read at the cited line: it agrees with the corrected round-4 rule |
| R4-2 | new | `BINDING_DEADCODE_FORMS` | `named-sets.json:56` | `updated` | the value did not exist before the round-4 pass, so this line was written by that pass |
| R4-2 | new | `BINDING_DEADCODE_FORMS` | `implementation-plan.md:218` | `updated` | the value did not exist before the round-4 pass, so this line was written by that pass |
| R4-2 | new | `BINDING_DEADCODE_FORMS` | `census-round4-corrections.ps1:68` | `confirmed-consistent` | census declaration table (the sweep's own input list), not a plan assertion |
| R4-2 | new | `BINDING_DEADCODE_FORMS` | `assert-picker-binding.ps1:33` | `updated` | the value did not exist before the round-4 pass, so this line was written by that pass |
| R4-2 | new | `BINDING_RUNTIME_TEST_FILE` | `named-sets.json:65` | `updated` | the value did not exist before the round-4 pass, so this line was written by that pass |
| R4-2 | new | `BINDING_RUNTIME_TEST_FILE` | `census-round4-corrections.ps1:69` | `confirmed-consistent` | census declaration table (the sweep's own input list), not a plan assertion |
| R4-2 | new | `BINDING_RUNTIME_TEST_FILE` | `assert-picker-binding.ps1:16` | `updated` | the value did not exist before the round-4 pass, so this line was written by that pass |
| R4-2 | new | `BINDING_RUNTIME_TEST_FILE` | `assert-picker-binding.ps1:36` | `updated` | the value did not exist before the round-4 pass, so this line was written by that pass |
| R4-2 | new | `BINDING_RUNTIME_TEST_NAMES` | `named-sets.json:66` | `updated` | the value did not exist before the round-4 pass, so this line was written by that pass |
| R4-2 | new | `BINDING_RUNTIME_TEST_NAMES` | `implementation-plan.md:219` | `updated` | the value did not exist before the round-4 pass, so this line was written by that pass |
| R4-2 | new | `BINDING_RUNTIME_TEST_NAMES` | `census-round4-corrections.ps1:70` | `confirmed-consistent` | census declaration table (the sweep's own input list), not a plan assertion |
| R4-2 | new | `BINDING_RUNTIME_TEST_NAMES` | `assert-picker-binding.ps1:37` | `updated` | the value did not exist before the round-4 pass, so this line was written by that pass |
| R4-2 | new | `BINDING_RUNTIME_FILTER` | `run-verification-plan.ps1:33` | `updated` | the value did not exist before the round-4 pass, so this line was written by that pass |
| R4-2 | new | `BINDING_RUNTIME_FILTER` | `named-sets.json:71` | `updated` | the value did not exist before the round-4 pass, so this line was written by that pass |
| R4-2 | new | `BINDING_RUNTIME_FILTER` | `implementation-plan.md:219` | `updated` | the value did not exist before the round-4 pass, so this line was written by that pass |
| R4-2 | new | `BINDING_RUNTIME_FILTER` | `census-round4-corrections.ps1:71` | `confirmed-consistent` | census declaration table (the sweep's own input list), not a plan assertion |
| R4-2 | new | `BINDING_RUNTIME_RECEIPT` | `run-verification-plan.ps1:33` | `updated` | the value did not exist before the round-4 pass, so this line was written by that pass |
| R4-2 | new | `BINDING_RUNTIME_RECEIPT` | `named-sets.json:72` | `updated` | the value did not exist before the round-4 pass, so this line was written by that pass |
| R4-2 | new | `BINDING_RUNTIME_RECEIPT` | `implementation-plan.md:219` | `updated` | the value did not exist before the round-4 pass, so this line was written by that pass |
| R4-2 | new | `BINDING_RUNTIME_RECEIPT` | `census-round4-corrections.ps1:72` | `confirmed-consistent` | census declaration table (the sweep's own input list), not a plan assertion |
| R4-2 | new | `BINDING_RUNTIME_RECEIPT` | `assert-picker-binding.ps1:38` | `updated` | the value did not exist before the round-4 pass, so this line was written by that pass |
| R4-2 | new | `BINDING_RUNTIME_RECEIPT` | `assert-picker-binding.ps1:359` | `updated` | the value did not exist before the round-4 pass, so this line was written by that pass |
| R4-2 | new | `BINDING_RUNTIME` | `run-verification-plan.ps1:12` | `updated` | the value did not exist before the round-4 pass, so this line was written by that pass |
| R4-2 | new | `BINDING_RUNTIME` | `run-verification-plan.ps1:33` | `updated` | the value did not exist before the round-4 pass, so this line was written by that pass |
| R4-2 | new | `BINDING_RUNTIME` | `named-sets.json:65` | `updated` | the value did not exist before the round-4 pass, so this line was written by that pass |
| R4-2 | new | `BINDING_RUNTIME` | `named-sets.json:66` | `updated` | the value did not exist before the round-4 pass, so this line was written by that pass |
| R4-2 | new | `BINDING_RUNTIME` | `named-sets.json:71` | `updated` | the value did not exist before the round-4 pass, so this line was written by that pass |
| R4-2 | new | `BINDING_RUNTIME` | `named-sets.json:72` | `updated` | the value did not exist before the round-4 pass, so this line was written by that pass |
| R4-2 | new | `BINDING_RUNTIME` | `implementation-plan.md:219` | `updated` | the value did not exist before the round-4 pass, so this line was written by that pass |
| R4-2 | new | `BINDING_RUNTIME` | `census-round4-corrections.ps1:69` | `confirmed-consistent` | census declaration table (the sweep's own input list), not a plan assertion |
| R4-2 | new | `BINDING_RUNTIME` | `census-round4-corrections.ps1:70` | `confirmed-consistent` | census declaration table (the sweep's own input list), not a plan assertion |
| R4-2 | new | `BINDING_RUNTIME` | `census-round4-corrections.ps1:71` | `confirmed-consistent` | census declaration table (the sweep's own input list), not a plan assertion |
| R4-2 | new | `BINDING_RUNTIME` | `census-round4-corrections.ps1:72` | `confirmed-consistent` | census declaration table (the sweep's own input list), not a plan assertion |
| R4-2 | new | `BINDING_RUNTIME` | `census-round4-corrections.ps1:73` | `confirmed-consistent` | census declaration table (the sweep's own input list), not a plan assertion |
| R4-2 | new | `BINDING_RUNTIME` | `assert-picker-binding.ps1:16` | `updated` | the value did not exist before the round-4 pass, so this line was written by that pass |
| R4-2 | new | `BINDING_RUNTIME` | `assert-picker-binding.ps1:36` | `updated` | the value did not exist before the round-4 pass, so this line was written by that pass |
| R4-2 | new | `BINDING_RUNTIME` | `assert-picker-binding.ps1:37` | `updated` | the value did not exist before the round-4 pass, so this line was written by that pass |
| R4-2 | new | `BINDING_RUNTIME` | `assert-picker-binding.ps1:38` | `updated` | the value did not exist before the round-4 pass, so this line was written by that pass |
| R4-2 | new | `BINDING_RUNTIME` | `assert-picker-binding.ps1:359` | `updated` | the value did not exist before the round-4 pass, so this line was written by that pass |
| R4-2 | new | `BindingReachabilityTests` | `task.md:44` | `updated` | the value did not exist before the round-4 pass, so this line was written by that pass |
| R4-2 | new | `BindingReachabilityTests` | `task.md:46` | `updated` | the value did not exist before the round-4 pass, so this line was written by that pass |
| R4-2 | new | `BindingReachabilityTests` | `named-sets.json:65` | `updated` | the value did not exist before the round-4 pass, so this line was written by that pass |
| R4-2 | new | `BindingReachabilityTests` | `named-sets.json:71` | `updated` | the value did not exist before the round-4 pass, so this line was written by that pass |
| R4-2 | new | `BindingReachabilityTests` | `implementation-plan.md:219` | `updated` | the value did not exist before the round-4 pass, so this line was written by that pass |
| R4-2 | new | `BindingReachabilityTests` | `implementation-plan.md:272` | `updated` | the value did not exist before the round-4 pass, so this line was written by that pass |
| R4-2 | new | `BindingReachabilityTests` | `implementation-plan.md:343` | `updated` | the value did not exist before the round-4 pass, so this line was written by that pass |
| R4-2 | new | `BindingReachabilityTests` | `census-round4-corrections.ps1:74` | `confirmed-consistent` | census declaration table (the sweep's own input list), not a plan assertion |
| R4-2 | new | `Microsoft.CodeAnalysis.CSharp` | `implementation-plan.md:219` | `updated` | the value did not exist before the round-4 pass, so this line was written by that pass |
| R4-2 | new | `Microsoft.CodeAnalysis.CSharp` | `implementation-plan.md:268` | `updated` | the value did not exist before the round-4 pass, so this line was written by that pass |
| R4-2 | new | `Microsoft.CodeAnalysis.CSharp` | `census-round4-corrections.ps1:75` | `confirmed-consistent` | census declaration table (the sweep's own input list), not a plan assertion |
| R4-2 | new | `Remove-CommentsAndLiterals` | `census-round4-corrections.ps1:76` | `confirmed-consistent` | census declaration table (the sweep's own input list), not a plan assertion |
| R4-2 | new | `Remove-CommentsAndLiterals` | `assert-picker-binding.ps1:49` | `updated` | the value did not exist before the round-4 pass, so this line was written by that pass |
| R4-2 | new | `Remove-CommentsAndLiterals` | `assert-picker-binding.ps1:155` | `updated` | the value did not exist before the round-4 pass, so this line was written by that pass |
| R4-2 | new | `Remove-CommentsAndLiterals` | `assert-picker-binding.ps1:171` | `updated` | the value did not exist before the round-4 pass, so this line was written by that pass |
| R4-2 | new | `Remove-CommentsAndLiterals` | `assert-picker-binding.ps1:341` | `updated` | the value did not exist before the round-4 pass, so this line was written by that pass |
| R4-2 | new | `Remove-CommentsAndLiterals` | `assert-picker-binding.ps1:345` | `updated` | the value did not exist before the round-4 pass, so this line was written by that pass |
| R4-2 | new | `Remove-CommentsAndLiterals` | `assert-picker-binding.ps1:352` | `updated` | the value did not exist before the round-4 pass, so this line was written by that pass |
| R4-2 | new | `Get-TopLevelStatements` | `census-round4-corrections.ps1:77` | `confirmed-consistent` | census declaration table (the sweep's own input list), not a plan assertion |
| R4-2 | new | `Get-TopLevelStatements` | `assert-picker-binding.ps1:135` | `updated` | the value did not exist before the round-4 pass, so this line was written by that pass |
| R4-2 | new | `Get-TopLevelStatements` | `assert-picker-binding.ps1:176` | `updated` | the value did not exist before the round-4 pass, so this line was written by that pass |
| R4-2 | new | `Test-DeadCode` | `census-round4-corrections.ps1:78` | `confirmed-consistent` | census declaration table (the sweep's own input list), not a plan assertion |
| R4-2 | new | `Test-DeadCode` | `assert-picker-binding.ps1:103` | `updated` | the value did not exist before the round-4 pass, so this line was written by that pass |
| R4-2 | new | `Test-DeadCode` | `assert-picker-binding.ps1:156` | `updated` | the value did not exist before the round-4 pass, so this line was written by that pass |
| R4-2 | new | `Test-DeadCode` | `assert-picker-binding.ps1:172` | `updated` | the value did not exist before the round-4 pass, so this line was written by that pass |
| R4-2 | new | `Test-RuntimeReceipt` | `census-round4-corrections.ps1:79` | `confirmed-consistent` | census declaration table (the sweep's own input list), not a plan assertion |
| R4-2 | new | `Test-RuntimeReceipt` | `assert-picker-binding.ps1:189` | `updated` | the value did not exist before the round-4 pass, so this line was written by that pass |
| R4-2 | new | `Test-RuntimeReceipt` | `assert-picker-binding.ps1:310` | `updated` | the value did not exist before the round-4 pass, so this line was written by that pass |
| R4-2 | new | `Test-RuntimeReceipt` | `assert-picker-binding.ps1:311` | `updated` | the value did not exist before the round-4 pass, so this line was written by that pass |
| R4-2 | new | `Test-RuntimeReceipt` | `assert-picker-binding.ps1:313` | `updated` | the value did not exist before the round-4 pass, so this line was written by that pass |
| R4-2 | new | `Test-RuntimeReceipt` | `assert-picker-binding.ps1:316` | `updated` | the value did not exist before the round-4 pass, so this line was written by that pass |
| R4-2 | new | `Test-RuntimeReceipt` | `assert-picker-binding.ps1:319` | `updated` | the value did not exist before the round-4 pass, so this line was written by that pass |
| R4-2 | new | `Test-RuntimeReceipt` | `assert-picker-binding.ps1:361` | `updated` | the value did not exist before the round-4 pass, so this line was written by that pass |
| R4-2 | new | `dotnet-binding.txt` | `task.md:46` | `updated` | the value did not exist before the round-4 pass, so this line was written by that pass |
| R4-2 | new | `dotnet-binding.txt` | `named-sets.json:72` | `updated` | the value did not exist before the round-4 pass, so this line was written by that pass |
| R4-2 | new | `dotnet-binding.txt` | `implementation-plan.md:343` | `updated` | the value did not exist before the round-4 pass, so this line was written by that pass |
| R4-2 | new | `dotnet-binding.txt` | `census-round4-corrections.ps1:80` | `confirmed-consistent` | census declaration table (the sweep's own input list), not a plan assertion |
| R4-2 | new | `AC-40.20` | `task.md:44` | `updated` | the value did not exist before the round-4 pass, so this line was written by that pass |
| R4-2 | new | `AC-40.20` | `task.md:46` | `updated` | the value did not exist before the round-4 pass, so this line was written by that pass |
| R4-2 | new | `AC-40.20` | `named-sets.json:172` | `updated` | the value did not exist before the round-4 pass, so this line was written by that pass |
| R4-2 | new | `AC-40.20` | `implementation-plan.md:218` | `updated` | the value did not exist before the round-4 pass, so this line was written by that pass |
| R4-2 | new | `AC-40.20` | `implementation-plan.md:219` | `updated` | the value did not exist before the round-4 pass, so this line was written by that pass |
| R4-2 | new | `AC-40.20` | `implementation-plan.md:268` | `updated` | the value did not exist before the round-4 pass, so this line was written by that pass |
| R4-2 | new | `AC-40.20` | `implementation-plan.md:272` | `updated` | the value did not exist before the round-4 pass, so this line was written by that pass |
| R4-2 | new | `AC-40.20` | `implementation-plan.md:343` | `updated` | the value did not exist before the round-4 pass, so this line was written by that pass |
| R4-2 | new | `AC-40.20` | `implementation-plan.md:344` | `updated` | the value did not exist before the round-4 pass, so this line was written by that pass |
| R4-2 | new | `AC-40.20` | `census-round4-corrections.ps1:81` | `confirmed-consistent` | census declaration table (the sweep's own input list), not a plan assertion |
| R4-2 | new | `AC-40.20` | `assert-picker-binding.ps1:2` | `updated` | the value did not exist before the round-4 pass, so this line was written by that pass |
| R4-2 | carry | `assert-picker-binding.ps1` | `task.md:46` | `confirmed-consistent` | pre-existing value, read at the cited line: it agrees with the corrected round-4 rule |
| R4-2 | carry | `assert-picker-binding.ps1` | `run-verification-plan.ps1:34` | `confirmed-consistent` | pre-existing value, read at the cited line: it agrees with the corrected round-4 rule |
| R4-2 | carry | `assert-picker-binding.ps1` | `implementation-plan.md:105` | `confirmed-consistent` | pre-existing value, read at the cited line: it agrees with the corrected round-4 rule |
| R4-2 | carry | `assert-picker-binding.ps1` | `implementation-plan.md:218` | `confirmed-consistent` | pre-existing value, read at the cited line: it agrees with the corrected round-4 rule |
| R4-2 | carry | `assert-picker-binding.ps1` | `implementation-plan.md:219` | `confirmed-consistent` | pre-existing value, read at the cited line: it agrees with the corrected round-4 rule |
| R4-2 | carry | `assert-picker-binding.ps1` | `implementation-plan.md:289` | `confirmed-consistent` | pre-existing value, read at the cited line: it agrees with the corrected round-4 rule |
| R4-2 | carry | `assert-picker-binding.ps1` | `implementation-plan.md:344` | `confirmed-consistent` | pre-existing value, read at the cited line: it agrees with the corrected round-4 rule |
| R4-2 | carry | `assert-picker-binding.ps1` | `census-round4-corrections.ps1:82` | `confirmed-consistent` | census declaration table (the sweep's own input list), not a plan assertion |
| R4-2 | carry | `assert-picker-binding.ps1` | `census-round4-corrections.ps1:152` | `confirmed-consistent` | census declaration table (the sweep's own input list), not a plan assertion |
| R4-2 | carry | `assert-picker-binding.ps1` | `census-round3-corrections.ps1:72` | `confirmed-consistent` | census declaration table (the sweep's own input list), not a plan assertion |
| R4-2 | carry | `assert-picker-binding.ps1` | `census-round1-corrections.ps1:43` | `confirmed-consistent` | census declaration table (the sweep's own input list), not a plan assertion |
| R4-2 | carry | `assert-picker-binding.ps1` | `assert-oracle-selftests.ps1:11` | `confirmed-consistent` | pre-existing value, read at the cited line: it agrees with the corrected round-4 rule |
| R4-2 | carry | `assert-picker-binding.ps1` | `assert-closeout.ps1:23` | `confirmed-consistent` | pre-existing value, read at the cited line: it agrees with the corrected round-4 rule |
| R4-2 | carry | `PICKER_BINDING` | `run-verification-plan.ps1:13` | `confirmed-consistent` | pre-existing value, read at the cited line: it agrees with the corrected round-4 rule |
| R4-2 | carry | `PICKER_BINDING` | `run-verification-plan.ps1:34` | `confirmed-consistent` | pre-existing value, read at the cited line: it agrees with the corrected round-4 rule |
| R4-2 | carry | `PICKER_BINDING` | `implementation-plan.md:105` | `confirmed-consistent` | pre-existing value, read at the cited line: it agrees with the corrected round-4 rule |
| R4-2 | carry | `PICKER_BINDING` | `implementation-plan.md:173` | `confirmed-consistent` | pre-existing value, read at the cited line: it agrees with the corrected round-4 rule |
| R4-2 | carry | `PICKER_BINDING` | `implementation-plan.md:218` | `confirmed-consistent` | pre-existing value, read at the cited line: it agrees with the corrected round-4 rule |
| R4-2 | carry | `PICKER_BINDING` | `census-round4-corrections.ps1:83` | `confirmed-consistent` | census declaration table (the sweep's own input list), not a plan assertion |
| R4-2 | carry | `PICKER_BINDING` | `assert-picker-binding.ps1:323` | `confirmed-consistent` | pre-existing value, read at the cited line: it agrees with the corrected round-4 rule |
| R4-2 | carry | `PICKER_BINDING` | `assert-picker-binding.ps1:364` | `confirmed-consistent` | pre-existing value, read at the cited line: it agrees with the corrected round-4 rule |
| R4-2 | carry | `PICKER_BINDING` | `assert-oracle-selftests.ps1:11` | `confirmed-consistent` | pre-existing value, read at the cited line: it agrees with the corrected round-4 rule |
| R4-2 | carry | `PICKER_BINDING` | `assert-closeout.ps1:23` | `confirmed-consistent` | pre-existing value, read at the cited line: it agrees with the corrected round-4 rule |
| R4-2 | carry | `BINDING_HANDLER_METHODS` | `named-sets.json:33` | `confirmed-consistent` | pre-existing value, read at the cited line: it agrees with the corrected round-4 rule |
| R4-2 | carry | `BINDING_HANDLER_METHODS` | `implementation-plan.md:218` | `confirmed-consistent` | pre-existing value, read at the cited line: it agrees with the corrected round-4 rule |
| R4-2 | carry | `BINDING_HANDLER_METHODS` | `census-round4-corrections.ps1:84` | `confirmed-consistent` | census declaration table (the sweep's own input list), not a plan assertion |
| R4-2 | carry | `BINDING_HANDLER_METHODS` | `census-round3-corrections.ps1:64` | `confirmed-consistent` | census declaration table (the sweep's own input list), not a plan assertion |
| R4-2 | carry | `BINDING_HANDLER_METHODS` | `assert-picker-binding.ps1:40` | `confirmed-consistent` | pre-existing value, read at the cited line: it agrees with the corrected round-4 rule |
| R4-2 | carry | `BINDING_ENTRY_METHOD` | `named-sets.json:40` | `confirmed-consistent` | pre-existing value, read at the cited line: it agrees with the corrected round-4 rule |
| R4-2 | carry | `BINDING_ENTRY_METHOD` | `census-round4-corrections.ps1:85` | `confirmed-consistent` | census declaration table (the sweep's own input list), not a plan assertion |
| R4-2 | carry | `BINDING_ENTRY_METHOD` | `census-round3-corrections.ps1:66` | `confirmed-consistent` | census declaration table (the sweep's own input list), not a plan assertion |
| R4-2 | carry | `BINDING_ENTRY_METHOD` | `assert-picker-binding.ps1:31` | `confirmed-consistent` | pre-existing value, read at the cited line: it agrees with the corrected round-4 rule |
| R4-2 | carry | `Get-MethodBody` | `census-round4-corrections.ps1:86` | `confirmed-consistent` | census declaration table (the sweep's own input list), not a plan assertion |
| R4-2 | carry | `Get-MethodBody` | `census-round3-corrections.ps1:68` | `confirmed-consistent` | census declaration table (the sweep's own input list), not a plan assertion |
| R4-2 | carry | `Get-MethodBody` | `assert-picker-binding.ps1:115` | `confirmed-consistent` | pre-existing value, read at the cited line: it agrees with the corrected round-4 rule |
| R4-2 | carry | `Get-MethodBody` | `assert-picker-binding.ps1:159` | `confirmed-consistent` | pre-existing value, read at the cited line: it agrees with the corrected round-4 rule |
| R4-2 | carry | `Get-MethodBody` | `assert-picker-binding.ps1:174` | `confirmed-consistent` | pre-existing value, read at the cited line: it agrees with the corrected round-4 rule |
| R4-2 | carry | `Test-Entrypoint` | `census-round4-corrections.ps1:87` | `confirmed-consistent` | census declaration table (the sweep's own input list), not a plan assertion |
| R4-2 | carry | `Test-Entrypoint` | `census-round3-corrections.ps1:69` | `confirmed-consistent` | census declaration table (the sweep's own input list), not a plan assertion |
| R4-2 | carry | `Test-Entrypoint` | `assert-picker-binding.ps1:169` | `confirmed-consistent` | pre-existing value, read at the cited line: it agrees with the corrected round-4 rule |
| R4-2 | carry | `Test-Entrypoint` | `assert-picker-binding.ps1:225` | `confirmed-consistent` | pre-existing value, read at the cited line: it agrees with the corrected round-4 rule |
| R4-2 | carry | `Test-Entrypoint` | `assert-picker-binding.ps1:226` | `confirmed-consistent` | pre-existing value, read at the cited line: it agrees with the corrected round-4 rule |
| R4-2 | carry | `Test-Entrypoint` | `assert-picker-binding.ps1:266` | `confirmed-consistent` | pre-existing value, read at the cited line: it agrees with the corrected round-4 rule |
| R4-2 | carry | `Test-Entrypoint` | `assert-picker-binding.ps1:271` | `confirmed-consistent` | pre-existing value, read at the cited line: it agrees with the corrected round-4 rule |
| R4-2 | carry | `Test-Entrypoint` | `assert-picker-binding.ps1:275` | `confirmed-consistent` | pre-existing value, read at the cited line: it agrees with the corrected round-4 rule |
| R4-2 | carry | `Test-Entrypoint` | `assert-picker-binding.ps1:288` | `confirmed-consistent` | pre-existing value, read at the cited line: it agrees with the corrected round-4 rule |
| R4-2 | carry | `Test-Entrypoint` | `assert-picker-binding.ps1:304` | `confirmed-consistent` | pre-existing value, read at the cited line: it agrees with the corrected round-4 rule |
| R4-2 | carry | `Test-Entrypoint` | `assert-picker-binding.ps1:305` | `confirmed-consistent` | pre-existing value, read at the cited line: it agrees with the corrected round-4 rule |
| R4-2 | carry | `Test-Entrypoint` | `assert-picker-binding.ps1:337` | `confirmed-consistent` | pre-existing value, read at the cited line: it agrees with the corrected round-4 rule |
| R4-2 | carry | `AC-40.17` | `task.md:46` | `confirmed-consistent` | pre-existing value, read at the cited line: it agrees with the corrected round-4 rule |
| R4-2 | carry | `AC-40.17` | `named-sets.json:169` | `confirmed-consistent` | pre-existing value, read at the cited line: it agrees with the corrected round-4 rule |
| R4-2 | carry | `AC-40.17` | `implementation-plan.md:218` | `confirmed-consistent` | pre-existing value, read at the cited line: it agrees with the corrected round-4 rule |
| R4-2 | carry | `AC-40.17` | `implementation-plan.md:344` | `confirmed-consistent` | pre-existing value, read at the cited line: it agrees with the corrected round-4 rule |
| R4-2 | carry | `AC-40.17` | `census-round4-corrections.ps1:88` | `confirmed-consistent` | census declaration table (the sweep's own input list), not a plan assertion |
| R4-2 | carry | `AC-40.17` | `census-round3-corrections.ps1:73` | `confirmed-consistent` | census declaration table (the sweep's own input list), not a plan assertion |
| R4-2 | carry | `AC-40.17` | `census-round1-corrections.ps1:45` | `confirmed-consistent` | census declaration table (the sweep's own input list), not a plan assertion |
| R4-2 | carry | `AC-40.17` | `assert-picker-binding.ps1:1` | `confirmed-consistent` | pre-existing value, read at the cited line: it agrees with the corrected round-4 rule |
| R4-2 | carry | `PICKER_TESTS_DIR` | `census-round4-corrections.ps1:89` | `confirmed-consistent` | census declaration table (the sweep's own input list), not a plan assertion |
| R4-2 | carry | `PICKER_TESTS_DIR` | `run-verification-plan.ps1:27` | `confirmed-consistent` | pre-existing value, read at the cited line: it agrees with the corrected round-4 rule |
| R4-2 | carry | `PICKER_TESTS_DIR` | `run-verification-plan.ps1:33` | `confirmed-consistent` | pre-existing value, read at the cited line: it agrees with the corrected round-4 rule |
| R4-2 | carry | `PICKER_TESTS_DIR` | `named-sets.json:18` | `confirmed-consistent` | pre-existing value, read at the cited line: it agrees with the corrected round-4 rule |
| R4-3 | new | `E2E_CAPTURE_SCRIPT` | `run-verification-plan.ps1:39` | `updated` | the value did not exist before the round-4 pass, so this line was written by that pass |
| R4-3 | new | `E2E_CAPTURE_SCRIPT` | `named-sets.json:89` | `updated` | the value did not exist before the round-4 pass, so this line was written by that pass |
| R4-3 | new | `E2E_CAPTURE_SCRIPT` | `census-round4-corrections.ps1:92` | `confirmed-consistent` | census declaration table (the sweep's own input list), not a plan assertion |
| R4-3 | new | `E2E_CAPTURE_SCRIPT` | `assert-e2e-wired.ps1:31` | `updated` | the value did not exist before the round-4 pass, so this line was written by that pass |
| R4-3 | new | `E2E_CAPTURE_REQUIRED_SEGMENTS` | `named-sets.json:90` | `updated` | the value did not exist before the round-4 pass, so this line was written by that pass |
| R4-3 | new | `E2E_CAPTURE_REQUIRED_SEGMENTS` | `implementation-plan.md:228` | `updated` | the value did not exist before the round-4 pass, so this line was written by that pass |
| R4-3 | new | `E2E_CAPTURE_REQUIRED_SEGMENTS` | `census-round4-corrections.ps1:93` | `confirmed-consistent` | census declaration table (the sweep's own input list), not a plan assertion |
| R4-3 | new | `E2E_CAPTURE_REQUIRED_SEGMENTS` | `assert-e2e-wired.ps1:32` | `updated` | the value did not exist before the round-4 pass, so this line was written by that pass |
| R4-3 | new | `E2E_REQUIRED_CASES` | `task.md:48` | `updated` | the value did not exist before the round-4 pass, so this line was written by that pass |
| R4-3 | new | `E2E_REQUIRED_CASES` | `task.md:50` | `updated` | the value did not exist before the round-4 pass, so this line was written by that pass |
| R4-3 | new | `E2E_REQUIRED_CASES` | `named-sets.json:97` | `updated` | the value did not exist before the round-4 pass, so this line was written by that pass |
| R4-3 | new | `E2E_REQUIRED_CASES` | `implementation-plan.md:227` | `updated` | the value did not exist before the round-4 pass, so this line was written by that pass |
| R4-3 | new | `E2E_REQUIRED_CASES` | `implementation-plan.md:228` | `updated` | the value did not exist before the round-4 pass, so this line was written by that pass |
| R4-3 | new | `E2E_REQUIRED_CASES` | `census-round4-corrections.ps1:94` | `confirmed-consistent` | census declaration table (the sweep's own input list), not a plan assertion |
| R4-3 | new | `E2E_REQUIRED_CASES` | `assert-e2e-wired.ps1:13` | `updated` | the value did not exist before the round-4 pass, so this line was written by that pass |
| R4-3 | new | `E2E_REQUIRED_CASES` | `assert-e2e-wired.ps1:34` | `updated` | the value did not exist before the round-4 pass, so this line was written by that pass |
| R4-3 | new | `E2E_EXECUTED_RECEIPT` | `run-verification-plan.ps1:39` | `updated` | the value did not exist before the round-4 pass, so this line was written by that pass |
| R4-3 | new | `E2E_EXECUTED_RECEIPT` | `named-sets.json:96` | `updated` | the value did not exist before the round-4 pass, so this line was written by that pass |
| R4-3 | new | `E2E_EXECUTED_RECEIPT` | `implementation-plan.md:227` | `updated` | the value did not exist before the round-4 pass, so this line was written by that pass |
| R4-3 | new | `E2E_EXECUTED_RECEIPT` | `census-round4-corrections.ps1:95` | `confirmed-consistent` | census declaration table (the sweep's own input list), not a plan assertion |
| R4-3 | new | `E2E_EXECUTED_RECEIPT` | `assert-e2e-wired.ps1:33` | `updated` | the value did not exist before the round-4 pass, so this line was written by that pass |
| R4-3 | new | `E2E_EXECUTED_RECEIPT` | `assert-e2e-wired.ps1:280` | `updated` | the value did not exist before the round-4 pass, so this line was written by that pass |
| R4-3 | new | `E2E_JSON_ENV` | `run-verification-plan.ps1:39` | `updated` | the value did not exist before the round-4 pass, so this line was written by that pass |
| R4-3 | new | `E2E_JSON_ENV` | `named-sets.json:95` | `updated` | the value did not exist before the round-4 pass, so this line was written by that pass |
| R4-3 | new | `E2E_JSON_ENV` | `census-round4-corrections.ps1:96` | `confirmed-consistent` | census declaration table (the sweep's own input list), not a plan assertion |
| R4-3 | new | `E2E_STUB_PROJECT_FILE` | `named-sets.json:105` | `updated` | the value did not exist before the round-4 pass, so this line was written by that pass |
| R4-3 | new | `E2E_STUB_PROJECT_FILE` | `implementation-plan.md:228` | `updated` | the value did not exist before the round-4 pass, so this line was written by that pass |
| R4-3 | new | `E2E_STUB_PROJECT_FILE` | `implementation-plan.md:286` | `updated` | the value did not exist before the round-4 pass, so this line was written by that pass |
| R4-3 | new | `E2E_STUB_PROJECT_FILE` | `census-round4-corrections.ps1:97` | `confirmed-consistent` | census declaration table (the sweep's own input list), not a plan assertion |
| R4-3 | new | `E2E_STUB_PROJECT_FILE` | `assert-e2e-wired.ps1:41` | `updated` | the value did not exist before the round-4 pass, so this line was written by that pass |
| R4-3 | new | `E2E_STUB_BUILD_REQUIRED_SEGMENT` | `named-sets.json:106` | `updated` | the value did not exist before the round-4 pass, so this line was written by that pass |
| R4-3 | new | `E2E_STUB_BUILD_REQUIRED_SEGMENT` | `census-round4-corrections.ps1:98` | `confirmed-consistent` | census declaration table (the sweep's own input list), not a plan assertion |
| R4-3 | new | `E2E_STUB_BUILD_REQUIRED_SEGMENT` | `assert-e2e-wired.ps1:43` | `updated` | the value did not exist before the round-4 pass, so this line was written by that pass |
| R4-3 | new | `E2E_EXECUTED` | `run-verification-plan.ps1:15` | `updated` | the value did not exist before the round-4 pass, so this line was written by that pass |
| R4-3 | new | `E2E_EXECUTED` | `run-verification-plan.ps1:39` | `updated` | the value did not exist before the round-4 pass, so this line was written by that pass |
| R4-3 | new | `E2E_EXECUTED` | `run-verification-plan.ps1:40` | `updated` | the value did not exist before the round-4 pass, so this line was written by that pass |
| R4-3 | new | `E2E_EXECUTED` | `named-sets.json:96` | `updated` | the value did not exist before the round-4 pass, so this line was written by that pass |
| R4-3 | new | `E2E_EXECUTED` | `implementation-plan.md:227` | `updated` | the value did not exist before the round-4 pass, so this line was written by that pass |
| R4-3 | new | `E2E_EXECUTED` | `census-round4-corrections.ps1:95` | `confirmed-consistent` | census declaration table (the sweep's own input list), not a plan assertion |
| R4-3 | new | `E2E_EXECUTED` | `census-round4-corrections.ps1:99` | `confirmed-consistent` | census declaration table (the sweep's own input list), not a plan assertion |
| R4-3 | new | `E2E_EXECUTED` | `assert-e2e-wired.ps1:33` | `updated` | the value did not exist before the round-4 pass, so this line was written by that pass |
| R4-3 | new | `E2E_EXECUTED` | `assert-e2e-wired.ps1:280` | `updated` | the value did not exist before the round-4 pass, so this line was written by that pass |
| R4-3 | new | `E2E_EXECUTED` | `assert-e2e-wired.ps1:284` | `updated` | the value did not exist before the round-4 pass, so this line was written by that pass |
| R4-3 | new | `E2E_EXECUTED` | `assert-closeout.ps1:28` | `updated` | the value did not exist before the round-4 pass, so this line was written by that pass |
| R4-3 | new | `E2E_CAPTURE_RUN` | `run-verification-plan.ps1:14` | `updated` | the value did not exist before the round-4 pass, so this line was written by that pass |
| R4-3 | new | `E2E_CAPTURE_RUN` | `run-verification-plan.ps1:39` | `updated` | the value did not exist before the round-4 pass, so this line was written by that pass |
| R4-3 | new | `E2E_CAPTURE_RUN` | `census-round4-corrections.ps1:100` | `confirmed-consistent` | census declaration table (the sweep's own input list), not a plan assertion |
| R4-3 | new | `test:e2e:capture` | `task.md:48` | `updated` | the value did not exist before the round-4 pass, so this line was written by that pass |
| R4-3 | new | `test:e2e:capture` | `task.md:50` | `updated` | the value did not exist before the round-4 pass, so this line was written by that pass |
| R4-3 | new | `test:e2e:capture` | `named-sets.json:89` | `updated` | the value did not exist before the round-4 pass, so this line was written by that pass |
| R4-3 | new | `test:e2e:capture` | `implementation-plan.md:227` | `updated` | the value did not exist before the round-4 pass, so this line was written by that pass |
| R4-3 | new | `test:e2e:capture` | `implementation-plan.md:228` | `updated` | the value did not exist before the round-4 pass, so this line was written by that pass |
| R4-3 | new | `test:e2e:capture` | `implementation-plan.md:281` | `updated` | the value did not exist before the round-4 pass, so this line was written by that pass |
| R4-3 | new | `test:e2e:capture` | `implementation-plan.md:350` | `updated` | the value did not exist before the round-4 pass, so this line was written by that pass |
| R4-3 | new | `test:e2e:capture` | `census-round4-corrections.ps1:101` | `confirmed-consistent` | census declaration table (the sweep's own input list), not a plan assertion |
| R4-3 | new | `PLAYWRIGHT_JSON_OUTPUT_NAME` | `task.md:50` | `updated` | the value did not exist before the round-4 pass, so this line was written by that pass |
| R4-3 | new | `PLAYWRIGHT_JSON_OUTPUT_NAME` | `named-sets.json:95` | `updated` | the value did not exist before the round-4 pass, so this line was written by that pass |
| R4-3 | new | `PLAYWRIGHT_JSON_OUTPUT_NAME` | `implementation-plan.md:227` | `updated` | the value did not exist before the round-4 pass, so this line was written by that pass |
| R4-3 | new | `PLAYWRIGHT_JSON_OUTPUT_NAME` | `implementation-plan.md:350` | `updated` | the value did not exist before the round-4 pass, so this line was written by that pass |
| R4-3 | new | `PLAYWRIGHT_JSON_OUTPUT_NAME` | `census-round4-corrections.ps1:102` | `confirmed-consistent` | census declaration table (the sweep's own input list), not a plan assertion |
| R4-3 | new | `--reporter=json` | `task.md:48` | `updated` | the value did not exist before the round-4 pass, so this line was written by that pass |
| R4-3 | new | `--reporter=json` | `named-sets.json:93` | `updated` | the value did not exist before the round-4 pass, so this line was written by that pass |
| R4-3 | new | `--reporter=json` | `implementation-plan.md:281` | `updated` | the value did not exist before the round-4 pass, so this line was written by that pass |
| R4-3 | new | `--reporter=json` | `census-round4-corrections.ps1:103` | `confirmed-consistent` | census declaration table (the sweep's own input list), not a plan assertion |
| R4-3 | new | `e2e-capture-results.json` | `task.md:50` | `updated` | the value did not exist before the round-4 pass, so this line was written by that pass |
| R4-3 | new | `e2e-capture-results.json` | `named-sets.json:96` | `updated` | the value did not exist before the round-4 pass, so this line was written by that pass |
| R4-3 | new | `e2e-capture-results.json` | `implementation-plan.md:350` | `updated` | the value did not exist before the round-4 pass, so this line was written by that pass |
| R4-3 | new | `e2e-capture-results.json` | `census-round4-corrections.ps1:104` | `confirmed-consistent` | census declaration table (the sweep's own input list), not a plan assertion |
| R4-3 | new | `-Mode Wired` | `task.md:50` | `updated` | the value did not exist before the round-4 pass, so this line was written by that pass |
| R4-3 | new | `-Mode Wired` | `task.md:87` | `updated` | the value did not exist before the round-4 pass, so this line was written by that pass |
| R4-3 | new | `-Mode Wired` | `implementation-plan.md:228` | `updated` | the value did not exist before the round-4 pass, so this line was written by that pass |
| R4-3 | new | `-Mode Wired` | `implementation-plan.md:348` | `updated` | the value did not exist before the round-4 pass, so this line was written by that pass |
| R4-3 | new | `-Mode Wired` | `census-round4-corrections.ps1:105` | `confirmed-consistent` | census declaration table (the sweep's own input list), not a plan assertion |
| R4-3 | new | `-Mode Wired` | `assert-e2e-wired.ps1:13` | `updated` | the value did not exist before the round-4 pass, so this line was written by that pass |
| R4-3 | new | `-Mode Executed` | `assert-e2e-wired.ps1:17` | `updated` | the value did not exist before the round-4 pass, so this line was written by that pass |
| R4-3 | new | `-Mode Executed` | `census-round4-corrections.ps1:106` | `confirmed-consistent` | census declaration table (the sweep's own input list), not a plan assertion |
| R4-3 | new | `-Mode Executed` | `implementation-plan.md:227` | `updated` | the value did not exist before the round-4 pass, so this line was written by that pass |
| R4-3 | new | `-Mode Executed` | `implementation-plan.md:228` | `updated` | the value did not exist before the round-4 pass, so this line was written by that pass |
| R4-3 | new | `-Mode Executed` | `implementation-plan.md:351` | `updated` | the value did not exist before the round-4 pass, so this line was written by that pass |
| R4-3 | new | `-Mode Executed` | `task.md:50` | `updated` | the value did not exist before the round-4 pass, so this line was written by that pass |
| R4-3 | new | `Remove-TsComments` | `census-round4-corrections.ps1:107` | `confirmed-consistent` | census declaration table (the sweep's own input list), not a plan assertion |
| R4-3 | new | `Remove-TsComments` | `assert-e2e-wired.ps1:47` | `updated` | the value did not exist before the round-4 pass, so this line was written by that pass |
| R4-3 | new | `Remove-TsComments` | `assert-e2e-wired.ps1:94` | `updated` | the value did not exist before the round-4 pass, so this line was written by that pass |
| R4-3 | new | `Remove-TsComments` | `assert-e2e-wired.ps1:115` | `updated` | the value did not exist before the round-4 pass, so this line was written by that pass |
| R4-3 | new | `Get-ReportedSpecs` | `census-round4-corrections.ps1:108` | `confirmed-consistent` | census declaration table (the sweep's own input list), not a plan assertion |
| R4-3 | new | `Get-ReportedSpecs` | `assert-e2e-wired.ps1:127` | `updated` | the value did not exist before the round-4 pass, so this line was written by that pass |
| R4-3 | new | `Get-ReportedSpecs` | `assert-e2e-wired.ps1:149` | `updated` | the value did not exist before the round-4 pass, so this line was written by that pass |
| R4-3 | new | `Get-ReportedSpecs` | `assert-e2e-wired.ps1:168` | `updated` | the value did not exist before the round-4 pass, so this line was written by that pass |
| R4-3 | new | `Test-ExecutedReport` | `census-round4-corrections.ps1:109` | `confirmed-consistent` | census declaration table (the sweep's own input list), not a plan assertion |
| R4-3 | new | `Test-ExecutedReport` | `assert-e2e-wired.ps1:155` | `updated` | the value did not exist before the round-4 pass, so this line was written by that pass |
| R4-3 | new | `Test-ExecutedReport` | `assert-e2e-wired.ps1:238` | `updated` | the value did not exist before the round-4 pass, so this line was written by that pass |
| R4-3 | new | `Test-ExecutedReport` | `assert-e2e-wired.ps1:243` | `updated` | the value did not exist before the round-4 pass, so this line was written by that pass |
| R4-3 | new | `Test-ExecutedReport` | `assert-e2e-wired.ps1:248` | `updated` | the value did not exist before the round-4 pass, so this line was written by that pass |
| R4-3 | new | `Test-ExecutedReport` | `assert-e2e-wired.ps1:253` | `updated` | the value did not exist before the round-4 pass, so this line was written by that pass |
| R4-3 | new | `Test-ExecutedReport` | `assert-e2e-wired.ps1:257` | `updated` | the value did not exist before the round-4 pass, so this line was written by that pass |
| R4-3 | new | `Test-ExecutedReport` | `assert-e2e-wired.ps1:260` | `updated` | the value did not exist before the round-4 pass, so this line was written by that pass |
| R4-3 | new | `Test-ExecutedReport` | `assert-e2e-wired.ps1:265` | `updated` | the value did not exist before the round-4 pass, so this line was written by that pass |
| R4-3 | new | `Test-ExecutedReport` | `assert-e2e-wired.ps1:270` | `updated` | the value did not exist before the round-4 pass, so this line was written by that pass |
| R4-3 | new | `Test-ExecutedReport` | `assert-e2e-wired.ps1:282` | `updated` | the value did not exist before the round-4 pass, so this line was written by that pass |
| R4-3 | new | `avkit-region-picker-stub.csproj` | `task.md:48` | `updated` | the value did not exist before the round-4 pass, so this line was written by that pass |
| R4-3 | new | `avkit-region-picker-stub.csproj` | `named-sets.json:105` | `updated` | the value did not exist before the round-4 pass, so this line was written by that pass |
| R4-3 | new | `avkit-region-picker-stub.csproj` | `implementation-plan.md:286` | `updated` | the value did not exist before the round-4 pass, so this line was written by that pass |
| R4-3 | new | `avkit-region-picker-stub.csproj` | `census-round4-corrections.ps1:110` | `confirmed-consistent` | census declaration table (the sweep's own input list), not a plan assertion |
| R4-3 | old | `AvKit.RegionPicker.Stub.csproj` | `census-round4-corrections.ps1:111` | `confirmed-consistent` | census declaration table (the sweep's own input list), not a plan assertion |
| R4-3 | carry | `assert-e2e-wired.ps1` | `task.md:50` | `confirmed-consistent` | pre-existing value, read at the cited line: it agrees with the corrected round-4 rule |
| R4-3 | carry | `assert-e2e-wired.ps1` | `task.md:87` | `confirmed-consistent` | pre-existing value, read at the cited line: it agrees with the corrected round-4 rule |
| R4-3 | carry | `assert-e2e-wired.ps1` | `run-verification-plan.ps1:37` | `confirmed-consistent` | pre-existing value, read at the cited line: it agrees with the corrected round-4 rule |
| R4-3 | carry | `assert-e2e-wired.ps1` | `run-verification-plan.ps1:40` | `confirmed-consistent` | pre-existing value, read at the cited line: it agrees with the corrected round-4 rule |
| R4-3 | carry | `assert-e2e-wired.ps1` | `implementation-plan.md:107` | `confirmed-consistent` | pre-existing value, read at the cited line: it agrees with the corrected round-4 rule |
| R4-3 | carry | `assert-e2e-wired.ps1` | `implementation-plan.md:226` | `confirmed-consistent` | pre-existing value, read at the cited line: it agrees with the corrected round-4 rule |
| R4-3 | carry | `assert-e2e-wired.ps1` | `implementation-plan.md:227` | `confirmed-consistent` | pre-existing value, read at the cited line: it agrees with the corrected round-4 rule |
| R4-3 | carry | `assert-e2e-wired.ps1` | `implementation-plan.md:228` | `confirmed-consistent` | pre-existing value, read at the cited line: it agrees with the corrected round-4 rule |
| R4-3 | carry | `assert-e2e-wired.ps1` | `implementation-plan.md:289` | `confirmed-consistent` | pre-existing value, read at the cited line: it agrees with the corrected round-4 rule |
| R4-3 | carry | `assert-e2e-wired.ps1` | `implementation-plan.md:348` | `confirmed-consistent` | pre-existing value, read at the cited line: it agrees with the corrected round-4 rule |
| R4-3 | carry | `assert-e2e-wired.ps1` | `implementation-plan.md:351` | `confirmed-consistent` | pre-existing value, read at the cited line: it agrees with the corrected round-4 rule |
| R4-3 | carry | `assert-e2e-wired.ps1` | `census-round4-corrections.ps1:112` | `confirmed-consistent` | census declaration table (the sweep's own input list), not a plan assertion |
| R4-3 | carry | `assert-e2e-wired.ps1` | `census-round4-corrections.ps1:153` | `confirmed-consistent` | census declaration table (the sweep's own input list), not a plan assertion |
| R4-3 | carry | `assert-e2e-wired.ps1` | `census-round3-corrections.ps1:94` | `confirmed-consistent` | census declaration table (the sweep's own input list), not a plan assertion |
| R4-3 | carry | `assert-e2e-wired.ps1` | `assert-oracle-selftests.ps1:13` | `confirmed-consistent` | pre-existing value, read at the cited line: it agrees with the corrected round-4 rule |
| R4-3 | carry | `assert-e2e-wired.ps1` | `assert-closeout.ps1:25` | `confirmed-consistent` | pre-existing value, read at the cited line: it agrees with the corrected round-4 rule |
| R4-3 | carry | `assert-e2e-wired.ps1` | `assert-closeout.ps1:28` | `confirmed-consistent` | pre-existing value, read at the cited line: it agrees with the corrected round-4 rule |
| R4-3 | carry | `E2E_WIRED` | `run-verification-plan.ps1:37` | `confirmed-consistent` | pre-existing value, read at the cited line: it agrees with the corrected round-4 rule |
| R4-3 | carry | `E2E_WIRED` | `implementation-plan.md:107` | `confirmed-consistent` | pre-existing value, read at the cited line: it agrees with the corrected round-4 rule |
| R4-3 | carry | `E2E_WIRED` | `implementation-plan.md:228` | `confirmed-consistent` | pre-existing value, read at the cited line: it agrees with the corrected round-4 rule |
| R4-3 | carry | `E2E_WIRED` | `census-round4-corrections.ps1:113` | `confirmed-consistent` | census declaration table (the sweep's own input list), not a plan assertion |
| R4-3 | carry | `E2E_WIRED` | `census-round3-corrections.ps1:98` | `confirmed-consistent` | census declaration table (the sweep's own input list), not a plan assertion |
| R4-3 | carry | `E2E_WIRED` | `assert-oracle-selftests.ps1:13` | `confirmed-consistent` | pre-existing value, read at the cited line: it agrees with the corrected round-4 rule |
| R4-3 | carry | `E2E_WIRED` | `assert-e2e-wired.ps1:274` | `confirmed-consistent` | pre-existing value, read at the cited line: it agrees with the corrected round-4 rule |
| R4-3 | carry | `E2E_WIRED` | `assert-e2e-wired.ps1:340` | `confirmed-consistent` | pre-existing value, read at the cited line: it agrees with the corrected round-4 rule |
| R4-3 | carry | `E2E_WIRED` | `assert-closeout.ps1:25` | `confirmed-consistent` | pre-existing value, read at the cited line: it agrees with the corrected round-4 rule |
| R4-3 | carry | `E2E_SPEC_FILE` | `named-sets.json:85` | `confirmed-consistent` | pre-existing value, read at the cited line: it agrees with the corrected round-4 rule |
| R4-3 | carry | `E2E_SPEC_FILE` | `census-round4-corrections.ps1:114` | `confirmed-consistent` | census declaration table (the sweep's own input list), not a plan assertion |
| R4-3 | carry | `E2E_SPEC_FILE` | `census-round3-corrections.ps1:100` | `confirmed-consistent` | census declaration table (the sweep's own input list), not a plan assertion |
| R4-3 | carry | `E2E_SPEC_FILE` | `assert-e2e-wired.ps1:27` | `confirmed-consistent` | pre-existing value, read at the cited line: it agrees with the corrected round-4 rule |
| R4-3 | carry | `ui/tests/e2e/capture-picker.test.ts` | `task.md:48` | `confirmed-consistent` | pre-existing value, read at the cited line: it agrees with the corrected round-4 rule |
| R4-3 | carry | `ui/tests/e2e/capture-picker.test.ts` | `named-sets.json:85` | `confirmed-consistent` | pre-existing value, read at the cited line: it agrees with the corrected round-4 rule |
| R4-3 | carry | `ui/tests/e2e/capture-picker.test.ts` | `implementation-plan.md:227` | `confirmed-consistent` | pre-existing value, read at the cited line: it agrees with the corrected round-4 rule |
| R4-3 | carry | `ui/tests/e2e/capture-picker.test.ts` | `implementation-plan.md:285` | `confirmed-consistent` | pre-existing value, read at the cited line: it agrees with the corrected round-4 rule |
| R4-3 | carry | `ui/tests/e2e/capture-picker.test.ts` | `census-round4-corrections.ps1:115` | `confirmed-consistent` | census declaration table (the sweep's own input list), not a plan assertion |
| R4-3 | carry | `ui/tests/e2e/capture-picker.test.ts` | `census-round3-corrections.ps1:101` | `confirmed-consistent` | census declaration table (the sweep's own input list), not a plan assertion |
| R4-3 | carry | `build:picker-stub` | `task.md:48` | `confirmed-consistent` | pre-existing value, read at the cited line: it agrees with the corrected round-4 rule |
| R4-3 | carry | `build:picker-stub` | `task.md:50` | `confirmed-consistent` | pre-existing value, read at the cited line: it agrees with the corrected round-4 rule |
| R4-3 | carry | `build:picker-stub` | `named-sets.json:104` | `confirmed-consistent` | pre-existing value, read at the cited line: it agrees with the corrected round-4 rule |
| R4-3 | carry | `build:picker-stub` | `implementation-plan.md:228` | `confirmed-consistent` | pre-existing value, read at the cited line: it agrees with the corrected round-4 rule |
| R4-3 | carry | `build:picker-stub` | `implementation-plan.md:281` | `confirmed-consistent` | pre-existing value, read at the cited line: it agrees with the corrected round-4 rule |
| R4-3 | carry | `build:picker-stub` | `census-round4-corrections.ps1:116` | `confirmed-consistent` | census declaration table (the sweep's own input list), not a plan assertion |
| R4-3 | carry | `build:picker-stub` | `census-round3-corrections.ps1:79` | `confirmed-consistent` | census declaration table (the sweep's own input list), not a plan assertion |
| R4-3 | carry | `build:picker-stub` | `census-round3-corrections.ps1:104` | `confirmed-consistent` | census declaration table (the sweep's own input list), not a plan assertion |
| R4-3 | carry | `native/region-picker-stub` | `task.md:48` | `confirmed-consistent` | pre-existing value, read at the cited line: it agrees with the corrected round-4 rule |
| R4-3 | carry | `native/region-picker-stub` | `named-sets.json:102` | `confirmed-consistent` | pre-existing value, read at the cited line: it agrees with the corrected round-4 rule |
| R4-3 | carry | `native/region-picker-stub` | `named-sets.json:103` | `confirmed-consistent` | pre-existing value, read at the cited line: it agrees with the corrected round-4 rule |
| R4-3 | carry | `native/region-picker-stub` | `named-sets.json:105` | `confirmed-consistent` | pre-existing value, read at the cited line: it agrees with the corrected round-4 rule |
| R4-3 | carry | `native/region-picker-stub` | `implementation-plan.md:286` | `confirmed-consistent` | pre-existing value, read at the cited line: it agrees with the corrected round-4 rule |
| R4-3 | carry | `native/region-picker-stub` | `census-round4-corrections.ps1:117` | `confirmed-consistent` | census declaration table (the sweep's own input list), not a plan assertion |
| R4-3 | carry | `native/region-picker-stub` | `census-round3-corrections.ps1:103` | `confirmed-consistent` | census declaration table (the sweep's own input list), not a plan assertion |
| R4-3 | carry | `AVKIT_REGION_PICKER_PATH` | `task.md:49` | `confirmed-consistent` | pre-existing value, read at the cited line: it agrees with the corrected round-4 rule |
| R4-3 | carry | `AVKIT_REGION_PICKER_PATH` | `task.md:50` | `confirmed-consistent` | pre-existing value, read at the cited line: it agrees with the corrected round-4 rule |
| R4-3 | carry | `AVKIT_REGION_PICKER_PATH` | `named-sets.json:28` | `confirmed-consistent` | pre-existing value, read at the cited line: it agrees with the corrected round-4 rule |
| R4-3 | carry | `AVKIT_REGION_PICKER_PATH` | `named-sets.json:115` | `confirmed-consistent` | pre-existing value, read at the cited line: it agrees with the corrected round-4 rule |
| R4-3 | carry | `AVKIT_REGION_PICKER_PATH` | `implementation-plan.md:171` | `confirmed-consistent` | pre-existing value, read at the cited line: it agrees with the corrected round-4 rule |
| R4-3 | carry | `AVKIT_REGION_PICKER_PATH` | `implementation-plan.md:226` | `confirmed-consistent` | pre-existing value, read at the cited line: it agrees with the corrected round-4 rule |
| R4-3 | carry | `AVKIT_REGION_PICKER_PATH` | `implementation-plan.md:227` | `confirmed-consistent` | pre-existing value, read at the cited line: it agrees with the corrected round-4 rule |
| R4-3 | carry | `AVKIT_REGION_PICKER_PATH` | `implementation-plan.md:228` | `confirmed-consistent` | pre-existing value, read at the cited line: it agrees with the corrected round-4 rule |
| R4-3 | carry | `AVKIT_REGION_PICKER_PATH` | `census-round4-corrections.ps1:118` | `confirmed-consistent` | census declaration table (the sweep's own input list), not a plan assertion |
| R4-3 | carry | `AVKIT_REGION_PICKER_PATH` | `census-round3-corrections.ps1:111` | `confirmed-consistent` | census declaration table (the sweep's own input list), not a plan assertion |
| R4-3 | carry | `AVKIT_REGION_PICKER_PATH` | `assert-e2e-wired.ps1:11` | `confirmed-consistent` | pre-existing value, read at the cited line: it agrees with the corrected round-4 rule |
| R4-3 | carry | `AVKIT_REGION_PICKER_PATH` | `assert-e2e-wired.ps1:112` | `confirmed-consistent` | pre-existing value, read at the cited line: it agrees with the corrected round-4 rule |
| R4-3 | carry | `AVKIT_REGION_PICKER_PATH` | `assert-e2e-wired.ps1:192` | `confirmed-consistent` | pre-existing value, read at the cited line: it agrees with the corrected round-4 rule |
| R4-3 | carry | `AVKIT_REGION_PICKER_PATH` | `assert-e2e-wired.ps1:201` | `confirmed-consistent` | pre-existing value, read at the cited line: it agrees with the corrected round-4 rule |
| R4-3 | carry | `AVKIT_REGION_PICKER_PATH` | `assert-e2e-wired.ps1:208` | `confirmed-consistent` | pre-existing value, read at the cited line: it agrees with the corrected round-4 rule |
| R4-3 | carry | `AVKIT_REGION_PICKER_PATH` | `assert-e2e-wired.ps1:218` | `confirmed-consistent` | pre-existing value, read at the cited line: it agrees with the corrected round-4 rule |
| R4-3 | carry | `AVKIT_REGION_PICKER_PATH` | `assert-e2e-wired.ps1:230` | `confirmed-consistent` | pre-existing value, read at the cited line: it agrees with the corrected round-4 rule |
| R4-3 | carry | `AVKIT_E2E` | `task.md:49` | `confirmed-consistent` | pre-existing value, read at the cited line: it agrees with the corrected round-4 rule |
| R4-3 | carry | `AVKIT_E2E` | `task.md:50` | `confirmed-consistent` | pre-existing value, read at the cited line: it agrees with the corrected round-4 rule |
| R4-3 | carry | `AVKIT_E2E` | `named-sets.json:118` | `confirmed-consistent` | pre-existing value, read at the cited line: it agrees with the corrected round-4 rule |
| R4-3 | carry | `AVKIT_E2E` | `implementation-plan.md:226` | `confirmed-consistent` | pre-existing value, read at the cited line: it agrees with the corrected round-4 rule |
| R4-3 | carry | `AVKIT_E2E` | `implementation-plan.md:228` | `confirmed-consistent` | pre-existing value, read at the cited line: it agrees with the corrected round-4 rule |
| R4-3 | carry | `AVKIT_E2E` | `implementation-plan.md:348` | `confirmed-consistent` | pre-existing value, read at the cited line: it agrees with the corrected round-4 rule |
| R4-3 | carry | `AVKIT_E2E` | `census-round4-corrections.ps1:119` | `confirmed-consistent` | census declaration table (the sweep's own input list), not a plan assertion |
| R4-3 | carry | `AVKIT_E2E` | `census-round3-corrections.ps1:110` | `confirmed-consistent` | census declaration table (the sweep's own input list), not a plan assertion |
| R4-3 | carry | `AVKIT_E2E` | `assert-e2e-wired.ps1:4` | `confirmed-consistent` | pre-existing value, read at the cited line: it agrees with the corrected round-4 rule |
| R4-3 | carry | `AVKIT_E2E` | `assert-e2e-wired.ps1:218` | `confirmed-consistent` | pre-existing value, read at the cited line: it agrees with the corrected round-4 rule |
| R4-3 | carry | `AVKIT_E2E` | `assert-e2e-wired.ps1:222` | `confirmed-consistent` | pre-existing value, read at the cited line: it agrees with the corrected round-4 rule |
| R4-3 | carry | `AVKIT_E2E` | `assert-e2e-wired.ps1:230` | `confirmed-consistent` | pre-existing value, read at the cited line: it agrees with the corrected round-4 rule |
| R4-3 | carry | `AC-40.18` | `task.md:48` | `confirmed-consistent` | pre-existing value, read at the cited line: it agrees with the corrected round-4 rule |
| R4-3 | carry | `AC-40.18` | `task.md:50` | `confirmed-consistent` | pre-existing value, read at the cited line: it agrees with the corrected round-4 rule |
| R4-3 | carry | `AC-40.18` | `named-sets.json:116` | `confirmed-consistent` | pre-existing value, read at the cited line: it agrees with the corrected round-4 rule |
| R4-3 | carry | `AC-40.18` | `named-sets.json:170` | `confirmed-consistent` | pre-existing value, read at the cited line: it agrees with the corrected round-4 rule |
| R4-3 | carry | `AC-40.18` | `implementation-plan.md:226` | `confirmed-consistent` | pre-existing value, read at the cited line: it agrees with the corrected round-4 rule |
| R4-3 | carry | `AC-40.18` | `implementation-plan.md:227` | `confirmed-consistent` | pre-existing value, read at the cited line: it agrees with the corrected round-4 rule |
| R4-3 | carry | `AC-40.18` | `implementation-plan.md:228` | `confirmed-consistent` | pre-existing value, read at the cited line: it agrees with the corrected round-4 rule |
| R4-3 | carry | `AC-40.18` | `implementation-plan.md:281` | `confirmed-consistent` | pre-existing value, read at the cited line: it agrees with the corrected round-4 rule |
| R4-3 | carry | `AC-40.18` | `implementation-plan.md:285` | `confirmed-consistent` | pre-existing value, read at the cited line: it agrees with the corrected round-4 rule |
| R4-3 | carry | `AC-40.18` | `implementation-plan.md:350` | `confirmed-consistent` | pre-existing value, read at the cited line: it agrees with the corrected round-4 rule |
| R4-3 | carry | `AC-40.18` | `implementation-plan.md:351` | `confirmed-consistent` | pre-existing value, read at the cited line: it agrees with the corrected round-4 rule |
| R4-3 | carry | `AC-40.18` | `census-round4-corrections.ps1:120` | `confirmed-consistent` | census declaration table (the sweep's own input list), not a plan assertion |
| R4-3 | carry | `AC-40.18` | `census-round3-corrections.ps1:96` | `confirmed-consistent` | census declaration table (the sweep's own input list), not a plan assertion |
| R4-3 | carry | `AC-40.18` | `assert-e2e-wired.ps1:1` | `confirmed-consistent` | pre-existing value, read at the cited line: it agrees with the corrected round-4 rule |
| R4-3 | carry | `AC-40.18` | `assert-e2e-wired.ps1:191` | `confirmed-consistent` | pre-existing value, read at the cited line: it agrees with the corrected round-4 rule |
| R4-3 | carry | `AC-40.18` | `assert-e2e-wired.ps1:208` | `confirmed-consistent` | pre-existing value, read at the cited line: it agrees with the corrected round-4 rule |
| R4-4 | new | `SMOKE_BLOCKED_CLASSES` | `task.md:52` | `updated` | the value did not exist before the round-4 pass, so this line was written by that pass |
| R4-4 | new | `SMOKE_BLOCKED_CLASSES` | `named-sets.json:128` | `updated` | the value did not exist before the round-4 pass, so this line was written by that pass |
| R4-4 | new | `SMOKE_BLOCKED_CLASSES` | `implementation-plan.md:228` | `updated` | the value did not exist before the round-4 pass, so this line was written by that pass |
| R4-4 | new | `SMOKE_BLOCKED_CLASSES` | `census-round4-corrections.ps1:123` | `confirmed-consistent` | census declaration table (the sweep's own input list), not a plan assertion |
| R4-4 | new | `SMOKE_BLOCKED_CLASSES` | `assert-smoke-disposition.ps1:10` | `updated` | the value did not exist before the round-4 pass, so this line was written by that pass |
| R4-4 | new | `SMOKE_BLOCKED_CLASSES` | `assert-smoke-disposition.ps1:19` | `updated` | the value did not exist before the round-4 pass, so this line was written by that pass |
| R4-4 | new | `SMOKE_BLOCKED_CLASSES` | `assert-smoke-disposition.ps1:29` | `updated` | the value did not exist before the round-4 pass, so this line was written by that pass |
| R4-4 | new | `SMOKE_FOLLOWUP_PATTERN` | `named-sets.json:133` | `updated` | the value did not exist before the round-4 pass, so this line was written by that pass |
| R4-4 | new | `SMOKE_FOLLOWUP_PATTERN` | `implementation-plan.md:228` | `updated` | the value did not exist before the round-4 pass, so this line was written by that pass |
| R4-4 | new | `SMOKE_FOLLOWUP_PATTERN` | `census-round4-corrections.ps1:124` | `confirmed-consistent` | census declaration table (the sweep's own input list), not a plan assertion |
| R4-4 | new | `SMOKE_FOLLOWUP_PATTERN` | `assert-smoke-disposition.ps1:30` | `updated` | the value did not exist before the round-4 pass, so this line was written by that pass |
| R4-4 | new | `SMOKE_LATENCY_KEY` | `named-sets.json:134` | `updated` | the value did not exist before the round-4 pass, so this line was written by that pass |
| R4-4 | new | `SMOKE_LATENCY_KEY` | `census-round4-corrections.ps1:125` | `confirmed-consistent` | census declaration table (the sweep's own input list), not a plan assertion |
| R4-4 | new | `SMOKE_LATENCY_KEY` | `assert-smoke-disposition.ps1:31` | `updated` | the value did not exist before the round-4 pass, so this line was written by that pass |
| R4-4 | new | `CLASS=` | `named-sets.json:125` | `updated` | the value did not exist before the round-4 pass, so this line was written by that pass |
| R4-4 | new | `CLASS=` | `census-round4-corrections.ps1:126` | `confirmed-consistent` | census declaration table (the sweep's own input list), not a plan assertion |
| R4-4 | new | `CLASS=` | `assert-smoke-disposition.ps1:19` | `updated` | the value did not exist before the round-4 pass, so this line was written by that pass |
| R4-4 | new | `CLASS=` | `assert-smoke-disposition.ps1:91` | `updated` | the value did not exist before the round-4 pass, so this line was written by that pass |
| R4-4 | new | `CLASS=` | `assert-smoke-disposition.ps1:95` | `updated` | the value did not exist before the round-4 pass, so this line was written by that pass |
| R4-4 | new | `CLASS=` | `assert-smoke-disposition.ps1:100` | `updated` | the value did not exist before the round-4 pass, so this line was written by that pass |
| R4-4 | new | `CLASS=` | `assert-smoke-disposition.ps1:104` | `updated` | the value did not exist before the round-4 pass, so this line was written by that pass |
| R4-4 | new | `CLASS=` | `assert-smoke-disposition.ps1:108` | `updated` | the value did not exist before the round-4 pass, so this line was written by that pass |
| R4-4 | new | `CLASS=` | `assert-smoke-disposition.ps1:117` | `updated` | the value did not exist before the round-4 pass, so this line was written by that pass |
| R4-4 | new | `CLASS=` | `assert-smoke-disposition.ps1:121` | `updated` | the value did not exist before the round-4 pass, so this line was written by that pass |
| R4-4 | new | `CLASS=` | `assert-smoke-disposition.ps1:125` | `updated` | the value did not exist before the round-4 pass, so this line was written by that pass |
| R4-4 | new | `CLASS=` | `assert-smoke-disposition.ps1:129` | `updated` | the value did not exist before the round-4 pass, so this line was written by that pass |
| R4-4 | new | `CLASS=` | `assert-smoke-disposition.ps1:132` | `updated` | the value did not exist before the round-4 pass, so this line was written by that pass |
| R4-4 | new | `CLASS=` | `assert-smoke-disposition.ps1:136` | `updated` | the value did not exist before the round-4 pass, so this line was written by that pass |
| R4-4 | new | `FOLLOWUP=` | `named-sets.json:126` | `updated` | the value did not exist before the round-4 pass, so this line was written by that pass |
| R4-4 | new | `FOLLOWUP=` | `census-round4-corrections.ps1:127` | `confirmed-consistent` | census declaration table (the sweep's own input list), not a plan assertion |
| R4-4 | new | `FOLLOWUP=` | `assert-smoke-disposition.ps1:20` | `updated` | the value did not exist before the round-4 pass, so this line was written by that pass |
| R4-4 | new | `FOLLOWUP=` | `assert-smoke-disposition.ps1:91` | `updated` | the value did not exist before the round-4 pass, so this line was written by that pass |
| R4-4 | new | `FOLLOWUP=` | `assert-smoke-disposition.ps1:95` | `updated` | the value did not exist before the round-4 pass, so this line was written by that pass |
| R4-4 | new | `FOLLOWUP=` | `assert-smoke-disposition.ps1:100` | `updated` | the value did not exist before the round-4 pass, so this line was written by that pass |
| R4-4 | new | `FOLLOWUP=` | `assert-smoke-disposition.ps1:104` | `updated` | the value did not exist before the round-4 pass, so this line was written by that pass |
| R4-4 | new | `FOLLOWUP=` | `assert-smoke-disposition.ps1:108` | `updated` | the value did not exist before the round-4 pass, so this line was written by that pass |
| R4-4 | new | `FOLLOWUP=` | `assert-smoke-disposition.ps1:117` | `updated` | the value did not exist before the round-4 pass, so this line was written by that pass |
| R4-4 | new | `FOLLOWUP=` | `assert-smoke-disposition.ps1:121` | `updated` | the value did not exist before the round-4 pass, so this line was written by that pass |
| R4-4 | new | `FOLLOWUP=` | `assert-smoke-disposition.ps1:125` | `updated` | the value did not exist before the round-4 pass, so this line was written by that pass |
| R4-4 | new | `FOLLOWUP=` | `assert-smoke-disposition.ps1:129` | `updated` | the value did not exist before the round-4 pass, so this line was written by that pass |
| R4-4 | new | `FOLLOWUP=` | `assert-smoke-disposition.ps1:132` | `updated` | the value did not exist before the round-4 pass, so this line was written by that pass |
| R4-4 | new | `FOLLOWUP=` | `assert-smoke-disposition.ps1:136` | `updated` | the value did not exist before the round-4 pass, so this line was written by that pass |
| R4-4 | new | `live-smoke.txt` | `task.md:52` | `updated` | the value did not exist before the round-4 pass, so this line was written by that pass |
| R4-4 | new | `live-smoke.txt` | `implementation-plan.md:346` | `updated` | the value did not exist before the round-4 pass, so this line was written by that pass |
| R4-4 | new | `live-smoke.txt` | `census-round4-corrections.ps1:128` | `confirmed-consistent` | census declaration table (the sweep's own input list), not a plan assertion |
| R4-4 | new | `live-smoke.txt` | `assert-smoke-disposition.ps1:21` | `updated` | the value did not exist before the round-4 pass, so this line was written by that pass |
| R4-4 | new | `live-smoke.txt` | `assert-smoke-disposition.ps1:85` | `updated` | the value did not exist before the round-4 pass, so this line was written by that pass |
| R4-4 | new | `external-error` | `task.md:87` | `updated` | the value did not exist before the round-4 pass, so this line was written by that pass |
| R4-4 | new | `external-error` | `named-sets.json:129` | `updated` | the value did not exist before the round-4 pass, so this line was written by that pass |
| R4-4 | new | `external-error` | `implementation-plan.md:228` | `updated` | the value did not exist before the round-4 pass, so this line was written by that pass |
| R4-4 | new | `external-error` | `census-round4-corrections.ps1:129` | `confirmed-consistent` | census declaration table (the sweep's own input list), not a plan assertion |
| R4-4 | new | `missing-dependency` | `task.md:87` | `updated` | the value did not exist before the round-4 pass, so this line was written by that pass |
| R4-4 | new | `missing-dependency` | `named-sets.json:130` | `updated` | the value did not exist before the round-4 pass, so this line was written by that pass |
| R4-4 | new | `missing-dependency` | `implementation-plan.md:228` | `updated` | the value did not exist before the round-4 pass, so this line was written by that pass |
| R4-4 | new | `missing-dependency` | `census-round4-corrections.ps1:130` | `confirmed-consistent` | census declaration table (the sweep's own input list), not a plan assertion |
| R4-4 | new | `missing-dependency` | `assert-smoke-disposition.ps1:95` | `updated` | the value did not exist before the round-4 pass, so this line was written by that pass |
| R4-4 | new | `missing-dependency` | `assert-smoke-disposition.ps1:104` | `updated` | the value did not exist before the round-4 pass, so this line was written by that pass |
| R4-4 | new | `missing-dependency` | `assert-smoke-disposition.ps1:117` | `updated` | the value did not exist before the round-4 pass, so this line was written by that pass |
| R4-4 | new | `missing-dependency` | `assert-smoke-disposition.ps1:121` | `updated` | the value did not exist before the round-4 pass, so this line was written by that pass |
| R4-4 | new | `missing-dependency` | `assert-smoke-disposition.ps1:129` | `updated` | the value did not exist before the round-4 pass, so this line was written by that pass |
| R4-4 | new | `missing-dependency` | `assert-smoke-disposition.ps1:132` | `updated` | the value did not exist before the round-4 pass, so this line was written by that pass |
| R4-4 | new | `human-decision` | `task.md:87` | `updated` | the value did not exist before the round-4 pass, so this line was written by that pass |
| R4-4 | new | `human-decision` | `task.md:88` | `updated` | the value did not exist before the round-4 pass, so this line was written by that pass |
| R4-4 | new | `human-decision` | `named-sets.json:131` | `updated` | the value did not exist before the round-4 pass, so this line was written by that pass |
| R4-4 | new | `human-decision` | `implementation-plan.md:228` | `updated` | the value did not exist before the round-4 pass, so this line was written by that pass |
| R4-4 | new | `human-decision` | `census-round4-corrections.ps1:131` | `confirmed-consistent` | census declaration table (the sweep's own input list), not a plan assertion |
| R4-4 | carry | `assert-smoke-disposition.ps1` | `task.md:52` | `confirmed-consistent` | pre-existing value, read at the cited line: it agrees with the corrected round-4 rule |
| R4-4 | carry | `assert-smoke-disposition.ps1` | `task.md:87` | `confirmed-consistent` | pre-existing value, read at the cited line: it agrees with the corrected round-4 rule |
| R4-4 | carry | `assert-smoke-disposition.ps1` | `run-verification-plan.ps1:9` | `confirmed-consistent` | pre-existing value, read at the cited line: it agrees with the corrected round-4 rule |
| R4-4 | carry | `assert-smoke-disposition.ps1` | `run-verification-plan.ps1:41` | `confirmed-consistent` | pre-existing value, read at the cited line: it agrees with the corrected round-4 rule |
| R4-4 | carry | `assert-smoke-disposition.ps1` | `implementation-plan.md:108` | `confirmed-consistent` | pre-existing value, read at the cited line: it agrees with the corrected round-4 rule |
| R4-4 | carry | `assert-smoke-disposition.ps1` | `implementation-plan.md:228` | `confirmed-consistent` | pre-existing value, read at the cited line: it agrees with the corrected round-4 rule |
| R4-4 | carry | `assert-smoke-disposition.ps1` | `implementation-plan.md:289` | `confirmed-consistent` | pre-existing value, read at the cited line: it agrees with the corrected round-4 rule |
| R4-4 | carry | `assert-smoke-disposition.ps1` | `implementation-plan.md:352` | `confirmed-consistent` | pre-existing value, read at the cited line: it agrees with the corrected round-4 rule |
| R4-4 | carry | `assert-smoke-disposition.ps1` | `census-round4-corrections.ps1:132` | `confirmed-consistent` | census declaration table (the sweep's own input list), not a plan assertion |
| R4-4 | carry | `assert-smoke-disposition.ps1` | `census-round3-corrections.ps1:95` | `confirmed-consistent` | census declaration table (the sweep's own input list), not a plan assertion |
| R4-4 | carry | `assert-smoke-disposition.ps1` | `assert-oracle-selftests.ps1:14` | `confirmed-consistent` | pre-existing value, read at the cited line: it agrees with the corrected round-4 rule |
| R4-4 | carry | `assert-smoke-disposition.ps1` | `assert-closeout.ps1:29` | `confirmed-consistent` | pre-existing value, read at the cited line: it agrees with the corrected round-4 rule |
| R4-4 | carry | `SMOKE_DISPOSITION` | `run-verification-plan.ps1:41` | `confirmed-consistent` | pre-existing value, read at the cited line: it agrees with the corrected round-4 rule |
| R4-4 | carry | `SMOKE_DISPOSITION` | `named-sets.json:119` | `confirmed-consistent` | pre-existing value, read at the cited line: it agrees with the corrected round-4 rule |
| R4-4 | carry | `SMOKE_DISPOSITION` | `named-sets.json:120` | `confirmed-consistent` | pre-existing value, read at the cited line: it agrees with the corrected round-4 rule |
| R4-4 | carry | `SMOKE_DISPOSITION` | `implementation-plan.md:108` | `confirmed-consistent` | pre-existing value, read at the cited line: it agrees with the corrected round-4 rule |
| R4-4 | carry | `SMOKE_DISPOSITION` | `implementation-plan.md:228` | `confirmed-consistent` | pre-existing value, read at the cited line: it agrees with the corrected round-4 rule |
| R4-4 | carry | `SMOKE_DISPOSITION` | `census-round4-corrections.ps1:133` | `confirmed-consistent` | census declaration table (the sweep's own input list), not a plan assertion |
| R4-4 | carry | `SMOKE_DISPOSITION` | `census-round4-corrections.ps1:134` | `confirmed-consistent` | census declaration table (the sweep's own input list), not a plan assertion |
| R4-4 | carry | `SMOKE_DISPOSITION` | `census-round3-corrections.ps1:99` | `confirmed-consistent` | census declaration table (the sweep's own input list), not a plan assertion |
| R4-4 | carry | `SMOKE_DISPOSITION` | `census-round3-corrections.ps1:107` | `confirmed-consistent` | census declaration table (the sweep's own input list), not a plan assertion |
| R4-4 | carry | `SMOKE_DISPOSITION` | `assert-smoke-disposition.ps1:14` | `confirmed-consistent` | pre-existing value, read at the cited line: it agrees with the corrected round-4 rule |
| R4-4 | carry | `SMOKE_DISPOSITION` | `assert-smoke-disposition.ps1:27` | `confirmed-consistent` | pre-existing value, read at the cited line: it agrees with the corrected round-4 rule |
| R4-4 | carry | `SMOKE_DISPOSITION` | `assert-smoke-disposition.ps1:28` | `confirmed-consistent` | pre-existing value, read at the cited line: it agrees with the corrected round-4 rule |
| R4-4 | carry | `SMOKE_DISPOSITION` | `assert-smoke-disposition.ps1:140` | `confirmed-consistent` | pre-existing value, read at the cited line: it agrees with the corrected round-4 rule |
| R4-4 | carry | `SMOKE_DISPOSITION` | `assert-smoke-disposition.ps1:147` | `confirmed-consistent` | pre-existing value, read at the cited line: it agrees with the corrected round-4 rule |
| R4-4 | carry | `SMOKE_DISPOSITION` | `assert-smoke-disposition.ps1:150` | `confirmed-consistent` | pre-existing value, read at the cited line: it agrees with the corrected round-4 rule |
| R4-4 | carry | `SMOKE_DISPOSITION` | `assert-oracle-selftests.ps1:14` | `confirmed-consistent` | pre-existing value, read at the cited line: it agrees with the corrected round-4 rule |
| R4-4 | carry | `SMOKE_DISPOSITION` | `assert-closeout.ps1:29` | `confirmed-consistent` | pre-existing value, read at the cited line: it agrees with the corrected round-4 rule |
| R4-4 | carry | `SMOKE_DISPOSITION_FILE` | `named-sets.json:119` | `confirmed-consistent` | pre-existing value, read at the cited line: it agrees with the corrected round-4 rule |
| R4-4 | carry | `SMOKE_DISPOSITION_FILE` | `census-round4-corrections.ps1:134` | `confirmed-consistent` | census declaration table (the sweep's own input list), not a plan assertion |
| R4-4 | carry | `SMOKE_DISPOSITION_FILE` | `census-round3-corrections.ps1:107` | `confirmed-consistent` | census declaration table (the sweep's own input list), not a plan assertion |
| R4-4 | carry | `SMOKE_DISPOSITION_FILE` | `assert-smoke-disposition.ps1:14` | `confirmed-consistent` | pre-existing value, read at the cited line: it agrees with the corrected round-4 rule |
| R4-4 | carry | `SMOKE_DISPOSITION_FILE` | `assert-smoke-disposition.ps1:27` | `confirmed-consistent` | pre-existing value, read at the cited line: it agrees with the corrected round-4 rule |
| R4-4 | carry | `SMOKE_DISPOSITION_FILE` | `assert-smoke-disposition.ps1:147` | `confirmed-consistent` | pre-existing value, read at the cited line: it agrees with the corrected round-4 rule |
| R4-4 | carry | `Test-Disposition` | `census-round4-corrections.ps1:135` | `confirmed-consistent` | census declaration table (the sweep's own input list), not a plan assertion |
| R4-4 | carry | `Test-Disposition` | `assert-smoke-disposition.ps1:33` | `confirmed-consistent` | pre-existing value, read at the cited line: it agrees with the corrected round-4 rule |
| R4-4 | carry | `Test-Disposition` | `assert-smoke-disposition.ps1:92` | `confirmed-consistent` | pre-existing value, read at the cited line: it agrees with the corrected round-4 rule |
| R4-4 | carry | `Test-Disposition` | `assert-smoke-disposition.ps1:96` | `confirmed-consistent` | pre-existing value, read at the cited line: it agrees with the corrected round-4 rule |
| R4-4 | carry | `Test-Disposition` | `assert-smoke-disposition.ps1:100` | `confirmed-consistent` | pre-existing value, read at the cited line: it agrees with the corrected round-4 rule |
| R4-4 | carry | `Test-Disposition` | `assert-smoke-disposition.ps1:104` | `confirmed-consistent` | pre-existing value, read at the cited line: it agrees with the corrected round-4 rule |
| R4-4 | carry | `Test-Disposition` | `assert-smoke-disposition.ps1:108` | `confirmed-consistent` | pre-existing value, read at the cited line: it agrees with the corrected round-4 rule |
| R4-4 | carry | `Test-Disposition` | `assert-smoke-disposition.ps1:112` | `confirmed-consistent` | pre-existing value, read at the cited line: it agrees with the corrected round-4 rule |
| R4-4 | carry | `Test-Disposition` | `assert-smoke-disposition.ps1:113` | `confirmed-consistent` | pre-existing value, read at the cited line: it agrees with the corrected round-4 rule |
| R4-4 | carry | `Test-Disposition` | `assert-smoke-disposition.ps1:117` | `confirmed-consistent` | pre-existing value, read at the cited line: it agrees with the corrected round-4 rule |
| R4-4 | carry | `Test-Disposition` | `assert-smoke-disposition.ps1:121` | `confirmed-consistent` | pre-existing value, read at the cited line: it agrees with the corrected round-4 rule |
| R4-4 | carry | `Test-Disposition` | `assert-smoke-disposition.ps1:125` | `confirmed-consistent` | pre-existing value, read at the cited line: it agrees with the corrected round-4 rule |
| R4-4 | carry | `Test-Disposition` | `assert-smoke-disposition.ps1:129` | `confirmed-consistent` | pre-existing value, read at the cited line: it agrees with the corrected round-4 rule |
| R4-4 | carry | `Test-Disposition` | `assert-smoke-disposition.ps1:132` | `confirmed-consistent` | pre-existing value, read at the cited line: it agrees with the corrected round-4 rule |
| R4-4 | carry | `Test-Disposition` | `assert-smoke-disposition.ps1:136` | `confirmed-consistent` | pre-existing value, read at the cited line: it agrees with the corrected round-4 rule |
| R4-4 | carry | `Test-Disposition` | `assert-smoke-disposition.ps1:148` | `confirmed-consistent` | pre-existing value, read at the cited line: it agrees with the corrected round-4 rule |
| R4-4 | carry | `LATENCY_MS` | `task.md:52` | `confirmed-consistent` | pre-existing value, read at the cited line: it agrees with the corrected round-4 rule |
| R4-4 | carry | `LATENCY_MS` | `named-sets.json:121` | `confirmed-consistent` | pre-existing value, read at the cited line: it agrees with the corrected round-4 rule |
| R4-4 | carry | `LATENCY_MS` | `named-sets.json:134` | `confirmed-consistent` | pre-existing value, read at the cited line: it agrees with the corrected round-4 rule |
| R4-4 | carry | `LATENCY_MS` | `implementation-plan.md:228` | `confirmed-consistent` | pre-existing value, read at the cited line: it agrees with the corrected round-4 rule |
| R4-4 | carry | `LATENCY_MS` | `implementation-plan.md:299` | `confirmed-consistent` | pre-existing value, read at the cited line: it agrees with the corrected round-4 rule |
| R4-4 | carry | `LATENCY_MS` | `implementation-plan.md:352` | `confirmed-consistent` | pre-existing value, read at the cited line: it agrees with the corrected round-4 rule |
| R4-4 | carry | `LATENCY_MS` | `census-round4-corrections.ps1:136` | `confirmed-consistent` | census declaration table (the sweep's own input list), not a plan assertion |
| R4-4 | carry | `LATENCY_MS` | `census-round3-corrections.ps1:108` | `confirmed-consistent` | census declaration table (the sweep's own input list), not a plan assertion |
| R4-4 | carry | `LATENCY_MS` | `assert-smoke-disposition.ps1:8` | `confirmed-consistent` | pre-existing value, read at the cited line: it agrees with the corrected round-4 rule |
| R4-4 | carry | `LATENCY_MS` | `assert-smoke-disposition.ps1:11` | `confirmed-consistent` | pre-existing value, read at the cited line: it agrees with the corrected round-4 rule |
| R4-4 | carry | `LATENCY_MS` | `assert-smoke-disposition.ps1:15` | `confirmed-consistent` | pre-existing value, read at the cited line: it agrees with the corrected round-4 rule |
| R4-4 | carry | `LATENCY_MS` | `assert-smoke-disposition.ps1:91` | `confirmed-consistent` | pre-existing value, read at the cited line: it agrees with the corrected round-4 rule |
| R4-4 | carry | `LATENCY_MS` | `assert-smoke-disposition.ps1:95` | `confirmed-consistent` | pre-existing value, read at the cited line: it agrees with the corrected round-4 rule |
| R4-4 | carry | `LATENCY_MS` | `assert-smoke-disposition.ps1:100` | `confirmed-consistent` | pre-existing value, read at the cited line: it agrees with the corrected round-4 rule |
| R4-4 | carry | `LATENCY_MS` | `assert-smoke-disposition.ps1:104` | `confirmed-consistent` | pre-existing value, read at the cited line: it agrees with the corrected round-4 rule |
| R4-4 | carry | `LATENCY_MS` | `assert-smoke-disposition.ps1:108` | `confirmed-consistent` | pre-existing value, read at the cited line: it agrees with the corrected round-4 rule |
| R4-4 | carry | `LATENCY_MS` | `assert-smoke-disposition.ps1:112` | `confirmed-consistent` | pre-existing value, read at the cited line: it agrees with the corrected round-4 rule |
| R4-4 | carry | `LATENCY_MS` | `assert-smoke-disposition.ps1:117` | `confirmed-consistent` | pre-existing value, read at the cited line: it agrees with the corrected round-4 rule |
| R4-4 | carry | `LATENCY_MS` | `assert-smoke-disposition.ps1:121` | `confirmed-consistent` | pre-existing value, read at the cited line: it agrees with the corrected round-4 rule |
| R4-4 | carry | `LATENCY_MS` | `assert-smoke-disposition.ps1:125` | `confirmed-consistent` | pre-existing value, read at the cited line: it agrees with the corrected round-4 rule |
| R4-4 | carry | `LATENCY_MS` | `assert-smoke-disposition.ps1:129` | `confirmed-consistent` | pre-existing value, read at the cited line: it agrees with the corrected round-4 rule |
| R4-4 | carry | `LATENCY_MS` | `assert-smoke-disposition.ps1:132` | `confirmed-consistent` | pre-existing value, read at the cited line: it agrees with the corrected round-4 rule |
| R4-4 | carry | `LATENCY_MS` | `assert-smoke-disposition.ps1:136` | `confirmed-consistent` | pre-existing value, read at the cited line: it agrees with the corrected round-4 rule |
| R4-4 | carry | `BLOCKED=` | `task.md:87` | `confirmed-consistent` | pre-existing value, read at the cited line: it agrees with the corrected round-4 rule |
| R4-4 | carry | `BLOCKED=` | `named-sets.json:122` | `confirmed-consistent` | pre-existing value, read at the cited line: it agrees with the corrected round-4 rule |
| R4-4 | carry | `BLOCKED=` | `implementation-plan.md:228` | `confirmed-consistent` | pre-existing value, read at the cited line: it agrees with the corrected round-4 rule |
| R4-4 | carry | `BLOCKED=` | `implementation-plan.md:352` | `confirmed-consistent` | pre-existing value, read at the cited line: it agrees with the corrected round-4 rule |
| R4-4 | carry | `BLOCKED=` | `census-round4-corrections.ps1:137` | `confirmed-consistent` | census declaration table (the sweep's own input list), not a plan assertion |
| R4-4 | carry | `BLOCKED=` | `census-round3-corrections.ps1:109` | `confirmed-consistent` | census declaration table (the sweep's own input list), not a plan assertion |
| R4-4 | carry | `BLOCKED=` | `assert-smoke-disposition.ps1:7` | `confirmed-consistent` | pre-existing value, read at the cited line: it agrees with the corrected round-4 rule |
| R4-4 | carry | `BLOCKED=` | `assert-smoke-disposition.ps1:9` | `confirmed-consistent` | pre-existing value, read at the cited line: it agrees with the corrected round-4 rule |
| R4-4 | carry | `BLOCKED=` | `assert-smoke-disposition.ps1:10` | `confirmed-consistent` | pre-existing value, read at the cited line: it agrees with the corrected round-4 rule |
| R4-4 | carry | `BLOCKED=` | `assert-smoke-disposition.ps1:15` | `confirmed-consistent` | pre-existing value, read at the cited line: it agrees with the corrected round-4 rule |
| R4-4 | carry | `BLOCKED=` | `assert-smoke-disposition.ps1:16` | `confirmed-consistent` | pre-existing value, read at the cited line: it agrees with the corrected round-4 rule |
| R4-4 | carry | `BLOCKED=` | `assert-smoke-disposition.ps1:17` | `confirmed-consistent` | pre-existing value, read at the cited line: it agrees with the corrected round-4 rule |
| R4-4 | carry | `BLOCKED=` | `assert-smoke-disposition.ps1:18` | `confirmed-consistent` | pre-existing value, read at the cited line: it agrees with the corrected round-4 rule |
| R4-4 | carry | `BLOCKED=` | `assert-smoke-disposition.ps1:19` | `confirmed-consistent` | pre-existing value, read at the cited line: it agrees with the corrected round-4 rule |
| R4-4 | carry | `BLOCKED=` | `assert-smoke-disposition.ps1:20` | `confirmed-consistent` | pre-existing value, read at the cited line: it agrees with the corrected round-4 rule |
| R4-4 | carry | `BLOCKED=` | `assert-smoke-disposition.ps1:67` | `confirmed-consistent` | pre-existing value, read at the cited line: it agrees with the corrected round-4 rule |
| R4-4 | carry | `BLOCKED=` | `assert-smoke-disposition.ps1:70` | `confirmed-consistent` | pre-existing value, read at the cited line: it agrees with the corrected round-4 rule |
| R4-4 | carry | `BLOCKED=` | `assert-smoke-disposition.ps1:73` | `confirmed-consistent` | pre-existing value, read at the cited line: it agrees with the corrected round-4 rule |
| R4-4 | carry | `BLOCKED=` | `assert-smoke-disposition.ps1:91` | `confirmed-consistent` | pre-existing value, read at the cited line: it agrees with the corrected round-4 rule |
| R4-4 | carry | `BLOCKED=` | `assert-smoke-disposition.ps1:95` | `confirmed-consistent` | pre-existing value, read at the cited line: it agrees with the corrected round-4 rule |
| R4-4 | carry | `BLOCKED=` | `assert-smoke-disposition.ps1:100` | `confirmed-consistent` | pre-existing value, read at the cited line: it agrees with the corrected round-4 rule |
| R4-4 | carry | `BLOCKED=` | `assert-smoke-disposition.ps1:104` | `confirmed-consistent` | pre-existing value, read at the cited line: it agrees with the corrected round-4 rule |
| R4-4 | carry | `BLOCKED=` | `assert-smoke-disposition.ps1:108` | `confirmed-consistent` | pre-existing value, read at the cited line: it agrees with the corrected round-4 rule |
| R4-4 | carry | `BLOCKED=` | `assert-smoke-disposition.ps1:117` | `confirmed-consistent` | pre-existing value, read at the cited line: it agrees with the corrected round-4 rule |
| R4-4 | carry | `BLOCKED=` | `assert-smoke-disposition.ps1:121` | `confirmed-consistent` | pre-existing value, read at the cited line: it agrees with the corrected round-4 rule |
| R4-4 | carry | `BLOCKED=` | `assert-smoke-disposition.ps1:125` | `confirmed-consistent` | pre-existing value, read at the cited line: it agrees with the corrected round-4 rule |
| R4-4 | carry | `BLOCKED=` | `assert-smoke-disposition.ps1:129` | `confirmed-consistent` | pre-existing value, read at the cited line: it agrees with the corrected round-4 rule |
| R4-4 | carry | `BLOCKED=` | `assert-smoke-disposition.ps1:132` | `confirmed-consistent` | pre-existing value, read at the cited line: it agrees with the corrected round-4 rule |
| R4-4 | carry | `BLOCKED=` | `assert-smoke-disposition.ps1:136` | `confirmed-consistent` | pre-existing value, read at the cited line: it agrees with the corrected round-4 rule |
| R4-4 | carry | `live-smoke-disposition.txt` | `task.md:52` | `confirmed-consistent` | pre-existing value, read at the cited line: it agrees with the corrected round-4 rule |
| R4-4 | carry | `live-smoke-disposition.txt` | `named-sets.json:119` | `confirmed-consistent` | pre-existing value, read at the cited line: it agrees with the corrected round-4 rule |
| R4-4 | carry | `live-smoke-disposition.txt` | `implementation-plan.md:346` | `confirmed-consistent` | pre-existing value, read at the cited line: it agrees with the corrected round-4 rule |
| R4-4 | carry | `live-smoke-disposition.txt` | `census-round4-corrections.ps1:138` | `confirmed-consistent` | census declaration table (the sweep's own input list), not a plan assertion |
| R4-4 | carry | `AC-40.19` | `task.md:50` | `confirmed-consistent` | pre-existing value, read at the cited line: it agrees with the corrected round-4 rule |
| R4-4 | carry | `AC-40.19` | `task.md:52` | `confirmed-consistent` | pre-existing value, read at the cited line: it agrees with the corrected round-4 rule |
| R4-4 | carry | `AC-40.19` | `named-sets.json:171` | `confirmed-consistent` | pre-existing value, read at the cited line: it agrees with the corrected round-4 rule |
| R4-4 | carry | `AC-40.19` | `implementation-plan.md:228` | `confirmed-consistent` | pre-existing value, read at the cited line: it agrees with the corrected round-4 rule |
| R4-4 | carry | `AC-40.19` | `implementation-plan.md:348` | `confirmed-consistent` | pre-existing value, read at the cited line: it agrees with the corrected round-4 rule |
| R4-4 | carry | `AC-40.19` | `implementation-plan.md:352` | `confirmed-consistent` | pre-existing value, read at the cited line: it agrees with the corrected round-4 rule |
| R4-4 | carry | `AC-40.19` | `census-round4-corrections.ps1:139` | `confirmed-consistent` | census declaration table (the sweep's own input list), not a plan assertion |
| R4-4 | carry | `AC-40.19` | `census-round3-corrections.ps1:97` | `confirmed-consistent` | census declaration table (the sweep's own input list), not a plan assertion |
| R4-4 | carry | `AC-40.19` | `assert-smoke-disposition.ps1:1` | `confirmed-consistent` | pre-existing value, read at the cited line: it agrees with the corrected round-4 rule |
| R4-4 | carry | `AC-40.19` | `assert-e2e-wired.ps1:1` | `confirmed-consistent` | pre-existing value, read at the cited line: it agrees with the corrected round-4 rule |
| X-ac-count | old | `"AC_COUNT": 19` | `census-round4-corrections.ps1:142` | `confirmed-consistent` | census declaration table (the sweep's own input list), not a plan assertion |
| X-ac-count | old | `"AC_COUNT": 19` | `census-round3-corrections.ps1:131` | `confirmed-consistent` | census declaration table (the sweep's own input list), not a plan assertion |
| X-ac-count | old | `19 ACs` | `census-round4-corrections.ps1:143` | `confirmed-consistent` | census declaration table (the sweep's own input list), not a plan assertion |
| X-ac-count | new | `"AC_COUNT": 20` | `named-sets.json:151` | `updated` | the value did not exist before the round-4 pass, so this line was written by that pass |
| X-ac-count | new | `"AC_COUNT": 20` | `census-round4-corrections.ps1:144` | `confirmed-consistent` | census declaration table (the sweep's own input list), not a plan assertion |
| X-ac-count | carry | `AC_COUNT` | `task.md:60` | `confirmed-consistent` | pre-existing value, read at the cited line: it agrees with the corrected round-4 rule |
| X-ac-count | carry | `AC_COUNT` | `named-sets.json:151` | `confirmed-consistent` | pre-existing value, read at the cited line: it agrees with the corrected round-4 rule |
| X-ac-count | carry | `AC_COUNT` | `implementation-plan.md:109` | `confirmed-consistent` | pre-existing value, read at the cited line: it agrees with the corrected round-4 rule |
| X-ac-count | carry | `AC_COUNT` | `census-round4-corrections.ps1:142` | `confirmed-consistent` | census declaration table (the sweep's own input list), not a plan assertion |
| X-ac-count | carry | `AC_COUNT` | `census-round4-corrections.ps1:144` | `confirmed-consistent` | census declaration table (the sweep's own input list), not a plan assertion |
| X-ac-count | carry | `AC_COUNT` | `census-round4-corrections.ps1:145` | `confirmed-consistent` | census declaration table (the sweep's own input list), not a plan assertion |
| X-ac-count | carry | `AC_COUNT` | `census-round3-corrections.ps1:129` | `confirmed-consistent` | census declaration table (the sweep's own input list), not a plan assertion |
| X-ac-count | carry | `AC_COUNT` | `census-round3-corrections.ps1:131` | `confirmed-consistent` | census declaration table (the sweep's own input list), not a plan assertion |
| X-ac-count | carry | `AC_COUNT` | `census-round3-corrections.ps1:132` | `confirmed-consistent` | census declaration table (the sweep's own input list), not a plan assertion |
| X-ac-count | carry | `AC_COUNT` | `census-round1-corrections.ps1:90` | `confirmed-consistent` | census declaration table (the sweep's own input list), not a plan assertion |
| X-ac-count | carry | `AC_COUNT` | `assert-handoff-acs.ps1:2` | `confirmed-consistent` | pre-existing value, read at the cited line: it agrees with the corrected round-4 rule |
| X-ac-count | carry | `AC_COUNT` | `assert-handoff-acs.ps1:9` | `confirmed-consistent` | pre-existing value, read at the cited line: it agrees with the corrected round-4 rule |
| X-ac-count | carry | `AC_COUNT` | `assert-handoff-acs.ps1:17` | `confirmed-consistent` | pre-existing value, read at the cited line: it agrees with the corrected round-4 rule |
| X-ac-count | carry | `AC_IDS` | `task.md:60` | `confirmed-consistent` | pre-existing value, read at the cited line: it agrees with the corrected round-4 rule |
| X-ac-count | carry | `AC_IDS` | `named-sets.json:152` | `confirmed-consistent` | pre-existing value, read at the cited line: it agrees with the corrected round-4 rule |
| X-ac-count | carry | `AC_IDS` | `census-round4-corrections.ps1:146` | `confirmed-consistent` | census declaration table (the sweep's own input list), not a plan assertion |
| X-ac-count | carry | `AC_IDS` | `census-round3-corrections.ps1:133` | `confirmed-consistent` | census declaration table (the sweep's own input list), not a plan assertion |
| X-ac-count | carry | `AC_IDS` | `census-round1-corrections.ps1:91` | `confirmed-consistent` | census declaration table (the sweep's own input list), not a plan assertion |
| X-ac-count | carry | `AC_IDS` | `assert-handoff-acs.ps1:3` | `confirmed-consistent` | pre-existing value, read at the cited line: it agrees with the corrected round-4 rule |
| X-ac-count | carry | `AC_IDS` | `assert-handoff-acs.ps1:10` | `confirmed-consistent` | pre-existing value, read at the cited line: it agrees with the corrected round-4 rule |
| X-ac-count | carry | `AC_IDS` | `assert-handoff-acs.ps1:21` | `confirmed-consistent` | pre-existing value, read at the cited line: it agrees with the corrected round-4 rule |
| X-ac-count | carry | `assert-handoff-acs.ps1` | `task.md:60` | `confirmed-consistent` | pre-existing value, read at the cited line: it agrees with the corrected round-4 rule |
| X-ac-count | carry | `assert-handoff-acs.ps1` | `implementation-plan.md:109` | `confirmed-consistent` | pre-existing value, read at the cited line: it agrees with the corrected round-4 rule |
| X-ac-count | carry | `assert-handoff-acs.ps1` | `implementation-plan.md:289` | `confirmed-consistent` | pre-existing value, read at the cited line: it agrees with the corrected round-4 rule |
| X-ac-count | carry | `assert-handoff-acs.ps1` | `census-round4-corrections.ps1:147` | `confirmed-consistent` | census declaration table (the sweep's own input list), not a plan assertion |
| X-ac-count | carry | `assert-handoff-acs.ps1` | `census-round1-corrections.ps1:36` | `confirmed-consistent` | census declaration table (the sweep's own input list), not a plan assertion |
| X-ac-count | carry | `assert-handoff-acs.ps1` | `assert-closeout.ps1:31` | `confirmed-consistent` | pre-existing value, read at the cited line: it agrees with the corrected round-4 rule |
| X-sections | old | `13 sections` | `census-round4-corrections.ps1:150` | `confirmed-consistent` | census declaration table (the sweep's own input list), not a plan assertion |
| X-sections | old | `13-section` | `census-round4-corrections.ps1:151` | `confirmed-consistent` | census declaration table (the sweep's own input list), not a plan assertion |
| X-sections | old | `\| 5b \| `assert-picker-binding.ps1` \|` | `census-round4-corrections.ps1:152` | `confirmed-consistent` | census declaration table (the sweep's own input list), not a plan assertion |
| X-sections | old | `\| 9a \| `assert-e2e-wired.ps1` \|` | `census-round4-corrections.ps1:153` | `confirmed-consistent` | census declaration table (the sweep's own input list), not a plan assertion |
| X-sections | new | `16 sections` | `census-round4-corrections.ps1:154` | `confirmed-consistent` | census declaration table (the sweep's own input list), not a plan assertion |
| X-sections | new | `id = '5c'` | `run-verification-plan.ps1:34` | `updated` | the value did not exist before the round-4 pass, so this line was written by that pass |
| X-sections | new | `id = '9c'` | `run-verification-plan.ps1:39` | `updated` | the value did not exist before the round-4 pass, so this line was written by that pass |
| X-sections | new | `id = '9d'` | `run-verification-plan.ps1:40` | `updated` | the value did not exist before the round-4 pass, so this line was written by that pass |
| X-sections | carry | `run-verification-plan.ps1` | `task.md:41` | `confirmed-consistent` | pre-existing value, read at the cited line: it agrees with the corrected round-4 rule |
| X-sections | carry | `run-verification-plan.ps1` | `task.md:55` | `confirmed-consistent` | pre-existing value, read at the cited line: it agrees with the corrected round-4 rule |
| X-sections | carry | `run-verification-plan.ps1` | `implementation-plan.md:290` | `confirmed-consistent` | pre-existing value, read at the cited line: it agrees with the corrected round-4 rule |
| X-sections | carry | `run-verification-plan.ps1` | `implementation-plan.md:325` | `confirmed-consistent` | pre-existing value, read at the cited line: it agrees with the corrected round-4 rule |
| X-sections | carry | `run-verification-plan.ps1` | `implementation-plan.md:331` | `confirmed-consistent` | pre-existing value, read at the cited line: it agrees with the corrected round-4 rule |
| X-sections | carry | `run-verification-plan.ps1` | `census-round4-corrections.ps1:22` | `confirmed-consistent` | census declaration table (the sweep's own input list), not a plan assertion |
| X-sections | carry | `run-verification-plan.ps1` | `census-round4-corrections.ps1:158` | `confirmed-consistent` | census declaration table (the sweep's own input list), not a plan assertion |
| X-sections | carry | `run-verification-plan.ps1` | `census-round3-corrections.ps1:21` | `confirmed-consistent` | census declaration table (the sweep's own input list), not a plan assertion |
| X-sections | carry | `run-verification-plan.ps1` | `census-round3-corrections.ps1:120` | `confirmed-consistent` | census declaration table (the sweep's own input list), not a plan assertion |
| X-sections | carry | `VERIFICATION_PLAN` | `run-verification-plan.ps1:54` | `confirmed-consistent` | pre-existing value, read at the cited line: it agrees with the corrected round-4 rule |
| X-sections | carry | `VERIFICATION_PLAN` | `run-verification-plan.ps1:57` | `confirmed-consistent` | pre-existing value, read at the cited line: it agrees with the corrected round-4 rule |
| X-sections | carry | `VERIFICATION_PLAN` | `run-verification-plan.ps1:82` | `confirmed-consistent` | pre-existing value, read at the cited line: it agrees with the corrected round-4 rule |
| X-sections | carry | `VERIFICATION_PLAN` | `run-verification-plan.ps1:85` | `confirmed-consistent` | pre-existing value, read at the cited line: it agrees with the corrected round-4 rule |
| X-sections | carry | `VERIFICATION_PLAN` | `census-round4-corrections.ps1:159` | `confirmed-consistent` | census declaration table (the sweep's own input list), not a plan assertion |
| X-sections | carry | `VERIFICATION_PLAN` | `census-round3-corrections.ps1:121` | `confirmed-consistent` | census declaration table (the sweep's own input list), not a plan assertion |
| X-csproj | old | `AvKit.RegionPicker.csproj` | `census-round4-corrections.ps1:162` | `confirmed-consistent` | census declaration table (the sweep's own input list), not a plan assertion |
| X-csproj | old | `AvKit.RegionPicker.Tests.csproj` | `census-round4-corrections.ps1:163` | `confirmed-consistent` | census declaration table (the sweep's own input list), not a plan assertion |
| X-csproj | new | `avkit-region-picker.csproj` | `implementation-plan.md:262` | `updated` | the value did not exist before the round-4 pass, so this line was written by that pass |
| X-csproj | new | `avkit-region-picker.csproj` | `census-round4-corrections.ps1:164` | `confirmed-consistent` | census declaration table (the sweep's own input list), not a plan assertion |
| X-csproj | new | `avkit-region-picker-tests.csproj` | `implementation-plan.md:268` | `updated` | the value did not exist before the round-4 pass, so this line was written by that pass |
| X-csproj | new | `avkit-region-picker-tests.csproj` | `census-round4-corrections.ps1:165` | `confirmed-consistent` | census declaration table (the sweep's own input list), not a plan assertion |
| X-csproj | carry | `PICKER_EXE_REL` | `named-sets.json:15` | `confirmed-consistent` | pre-existing value, read at the cited line: it agrees with the corrected round-4 rule |
| X-csproj | carry | `PICKER_EXE_REL` | `implementation-plan.md:262` | `confirmed-consistent` | pre-existing value, read at the cited line: it agrees with the corrected round-4 rule |
| X-csproj | carry | `PICKER_EXE_REL` | `census-round4-corrections.ps1:166` | `confirmed-consistent` | census declaration table (the sweep's own input list), not a plan assertion |
| X-csproj | carry | `PICKER_EXE_REL` | `assert-packaging-clean.ps1:28` | `confirmed-consistent` | pre-existing value, read at the cited line: it agrees with the corrected round-4 rule |
| X-csproj | carry | `avkit-region-picker-stub.exe` | `named-sets.json:103` | `confirmed-consistent` | pre-existing value, read at the cited line: it agrees with the corrected round-4 rule |
| X-csproj | carry | `avkit-region-picker-stub.exe` | `census-round4-corrections.ps1:167` | `confirmed-consistent` | census declaration table (the sweep's own input list), not a plan assertion |
| X-census | new | `census-round4-corrections.ps1` | `census-round4-corrections.ps1:39` | `confirmed-consistent` | census declaration table (the sweep's own input list), not a plan assertion |
| X-census | new | `census-round4-corrections.ps1` | `census-round4-corrections.ps1:170` | `confirmed-consistent` | census declaration table (the sweep's own input list), not a plan assertion |
| X-census | carry | `census-round3-corrections.ps1` | `census-round4-corrections.ps1:3` | `confirmed-consistent` | census declaration table (the sweep's own input list), not a plan assertion |
| X-census | carry | `census-round3-corrections.ps1` | `census-round4-corrections.ps1:38` | `confirmed-consistent` | census declaration table (the sweep's own input list), not a plan assertion |
| X-census | carry | `census-round3-corrections.ps1` | `census-round4-corrections.ps1:171` | `confirmed-consistent` | census declaration table (the sweep's own input list), not a plan assertion |
| X-census | carry | `census-round3-corrections.ps1` | `census-round3-corrections.ps1:36` | `confirmed-consistent` | census declaration table (the sweep's own input list), not a plan assertion |
| X-census | carry | `census-round3-corrections.ps1` | `census-round3-corrections.ps1:114` | `confirmed-consistent` | census declaration table (the sweep's own input list), not a plan assertion |
| X-selftests | carry | `assert-oracle-selftests.ps1` | `task.md:40` | `confirmed-consistent` | pre-existing value, read at the cited line: it agrees with the corrected round-4 rule |
| X-selftests | carry | `assert-oracle-selftests.ps1` | `run-verification-plan.ps1:26` | `confirmed-consistent` | pre-existing value, read at the cited line: it agrees with the corrected round-4 rule |
| X-selftests | carry | `assert-oracle-selftests.ps1` | `implementation-plan.md:97` | `confirmed-consistent` | pre-existing value, read at the cited line: it agrees with the corrected round-4 rule |
| X-selftests | carry | `assert-oracle-selftests.ps1` | `implementation-plan.md:289` | `confirmed-consistent` | pre-existing value, read at the cited line: it agrees with the corrected round-4 rule |
| X-selftests | carry | `assert-oracle-selftests.ps1` | `implementation-plan.md:336` | `confirmed-consistent` | pre-existing value, read at the cited line: it agrees with the corrected round-4 rule |
| X-selftests | carry | `assert-oracle-selftests.ps1` | `census-round4-corrections.ps1:172` | `confirmed-consistent` | census declaration table (the sweep's own input list), not a plan assertion |
| X-selftests | carry | `assert-oracle-selftests.ps1` | `census-round3-corrections.ps1:134` | `confirmed-consistent` | census declaration table (the sweep's own input list), not a plan assertion |
| X-selftests | carry | `assert-oracle-selftests.ps1` | `census-round1-corrections.ps1:96` | `confirmed-consistent` | census declaration table (the sweep's own input list), not a plan assertion |
| X-selftests | carry | `assert-oracle-selftests.ps1` | `assert-closeout.ps1:18` | `confirmed-consistent` | pre-existing value, read at the cited line: it agrees with the corrected round-4 rule |
| X-selftests | carry | `-SelfTest` | `task.md:40` | `confirmed-consistent` | pre-existing value, read at the cited line: it agrees with the corrected round-4 rule |
| X-selftests | carry | `-SelfTest` | `task.md:41` | `confirmed-consistent` | pre-existing value, read at the cited line: it agrees with the corrected round-4 rule |
| X-selftests | carry | `-SelfTest` | `task.md:82` | `confirmed-consistent` | pre-existing value, read at the cited line: it agrees with the corrected round-4 rule |
| X-selftests | carry | `-SelfTest` | `implementation-plan.md:97` | `confirmed-consistent` | pre-existing value, read at the cited line: it agrees with the corrected round-4 rule |
| X-selftests | carry | `-SelfTest` | `implementation-plan.md:218` | `confirmed-consistent` | pre-existing value, read at the cited line: it agrees with the corrected round-4 rule |
| X-selftests | carry | `-SelfTest` | `implementation-plan.md:224` | `confirmed-consistent` | pre-existing value, read at the cited line: it agrees with the corrected round-4 rule |
| X-selftests | carry | `-SelfTest` | `implementation-plan.md:228` | `confirmed-consistent` | pre-existing value, read at the cited line: it agrees with the corrected round-4 rule |
| X-selftests | carry | `-SelfTest` | `implementation-plan.md:289` | `confirmed-consistent` | pre-existing value, read at the cited line: it agrees with the corrected round-4 rule |
| X-selftests | carry | `-SelfTest` | `implementation-plan.md:290` | `confirmed-consistent` | pre-existing value, read at the cited line: it agrees with the corrected round-4 rule |
| X-selftests | carry | `-SelfTest` | `implementation-plan.md:327` | `confirmed-consistent` | pre-existing value, read at the cited line: it agrees with the corrected round-4 rule |
| X-selftests | carry | `-SelfTest` | `census-round4-corrections.ps1:173` | `confirmed-consistent` | census declaration table (the sweep's own input list), not a plan assertion |
| X-selftests | carry | `-SelfTest` | `census-round3-corrections.ps1:135` | `confirmed-consistent` | census declaration table (the sweep's own input list), not a plan assertion |

| X-selftests | carry | `-SelfTest` | `census-round1-corrections.ps1:97` | `confirmed-consistent` | census declaration table (the sweep's own input list), not a plan assertion |
| X-selftests | carry | `-SelfTest` | `assert-task-rows.ps1:27` | `confirmed-consistent` | pre-existing value, read at the cited line: it agrees with the corrected round-4 rule |
| X-selftests | carry | `-SelfTest` | `assert-picker-binding.ps1:21` | `confirmed-consistent` | pre-existing value, read at the cited line: it agrees with the corrected round-4 rule |
| X-selftests | carry | `-SelfTest` | `assert-overlay-deleted.ps1:2` | `confirmed-consistent` | pre-existing value, read at the cited line: it agrees with the corrected round-4 rule |
| X-selftests | carry | `-SelfTest` | `assert-oracle-selftests.ps1:7` | `confirmed-consistent` | pre-existing value, read at the cited line: it agrees with the corrected round-4 rule |
| X-selftests | carry | `-SelfTest` | `assert-oracle-selftests.ps1:8` | `confirmed-consistent` | pre-existing value, read at the cited line: it agrees with the corrected round-4 rule |
| X-selftests | carry | `-SelfTest` | `assert-oracle-selftests.ps1:9` | `confirmed-consistent` | pre-existing value, read at the cited line: it agrees with the corrected round-4 rule |
| X-selftests | carry | `-SelfTest` | `assert-oracle-selftests.ps1:10` | `confirmed-consistent` | pre-existing value, read at the cited line: it agrees with the corrected round-4 rule |
| X-selftests | carry | `-SelfTest` | `assert-oracle-selftests.ps1:11` | `confirmed-consistent` | pre-existing value, read at the cited line: it agrees with the corrected round-4 rule |
| X-selftests | carry | `-SelfTest` | `assert-oracle-selftests.ps1:12` | `confirmed-consistent` | pre-existing value, read at the cited line: it agrees with the corrected round-4 rule |
| X-selftests | carry | `-SelfTest` | `assert-oracle-selftests.ps1:13` | `confirmed-consistent` | pre-existing value, read at the cited line: it agrees with the corrected round-4 rule |
| X-selftests | carry | `-SelfTest` | `assert-oracle-selftests.ps1:14` | `confirmed-consistent` | pre-existing value, read at the cited line: it agrees with the corrected round-4 rule |
| X-selftests | carry | `-SelfTest` | `assert-e2e-wired.ps1:21` | `confirmed-consistent` | pre-existing value, read at the cited line: it agrees with the corrected round-4 rule |

---

## Round 5 — Corrections Re-Review

### Intent Anchor

Executing this plan is supposed to replace the Chromium capture overlay with a packaged .NET 8 WinForms picker while preserving the Electron/Python/API boundaries and proving the real F2-to-publish path before closeout. The current plan remains unstarted and is not yet approvable: one Round 4 finding is resolved, three are only partially resolved, and three additional High defects let material work false-pass or make a declared valid `[B]` state impossible to close.

### PR-6 Evidence Adjudication

PR-6 is sufficient, so content review proceeded in this round. The supplied receipt exists and has 1,572 lines; a fresh run has 1,571 substantive lines (the supplied extra line is the RTK wrapper banner), exits `0`, reports `109 x 2 = 218` sweeps, 724 FOLDER dispositions, worst `rg` exit `0`, and `STALE SITES: 0`. The fresh generated log and the rolling log are the same 724-row multiset (hit order differs only because `rg` enumeration order differs): 244 `updated`, 480 `confirmed-consistent`, 0 stale. The declared values cover the changed status predicate, binding/runtime proof, E2E execution/report contract, smoke disposition, AC count, 16-section inventory, and csproj renames; no under-declared changed value was identified.

### Round 4 Finding Adjudication

| Finding | Disposition | Current-file evidence |
|---|---|---|
| R4-1 — predecessor status completeness | `resolved` | `assert-task-rows.ps1:37-74` parses only the last cell; `:101-121` carries `invalidAll`; live mode rejects invalid rows before the boundary/open checks at `:242-268`. T6-T11 cover `[/]`, unknown, missing, duplicate/decorated, inline-prose `[B]`, and malformed successors at `:184-235`. The aggregate self-test passed. |
| R4-2 — production binding/reachability | `partially_resolved` | Comments/literals and the demonstrated nested/dead probes are rejected (`assert-picker-binding.ps1:49-111`, `:132-185`, B4-B5b at `:242-272`), and E3 passes at `:292-306`. However AC-40.20 still defines reachability as syntax-tree invocation presence (`implementation-plan.md:219`), and the live gate binds the suite only by three identifiers plus aggregate pass count (`assert-picker-binding.ps1:188-199`, `:350-362`). The concrete program `return 1; return Run(args, new RegionForm());` contains no declared dead-code form yet has the required top-level Roslyn invocation; both advertised controls accept a shipped entrypoint that can never launch the form. |
| R4-3 — capture E2E execution | `partially_resolved` | Comment-only/missing case reports now fail (`assert-e2e-wired.ps1:86-107`, `:155-183`, X1-X6 at `:235-274`), and `-Mode Executed` checks the JSON at `:278-285`. But Wired mode validates package scripts by substring only (`:315-329`): `echo playwright test tests/e2e/capture-picker.test.ts --reporter=json` and `echo dotnet publish` satisfy it. Neither task row 7a nor the runner deletes or freshness-binds `E2E_EXECUTED_RECEIPT` before the run (`task.md:50`; `run-verification-plan.ps1:37-40`), so the echo-only run exits 0 and §9d can accept a stale prior JSON report. |
| R4-4 — smoke evidence binding | `partially_resolved` | The exact nonexistent/empty receipt, subjective class, missing/free-text follow-up, and absent latency probes now fail (`assert-smoke-disposition.ps1:50-76`, D6-D10 at `:115-138`). But the receipt is not bound to the live-smoke command or evidence type. `LATENCY_MS=8`, `BLOCKED=no`, `RECEIPT=C:/Temp/av-kit/round5-oracle-selftests.txt` passes because that unrelated nonempty receipt contains the digit `8`; the blocked branch likewise accepts any unrelated nonempty receipt and only regex-validates a follow-up-shaped string, not an actual linked task. This still violates `task.md:87`'s command/error and linked-follow-up contract. |

### N-Series and F-Series Regression Check

| Finding | Disposition | Current-file evidence |
|---|---|---|
| N3 — production packaging path | `resolved; not regressed` | Exact `&&` segments remain enforced at `assert-packaging-clean.ps1:32-51`; P1-P4 remain at `:63-97`; the live clean-path production prep remains at `:119-145`. Self-test passed; the destructive non-`-SkipBuild` live gate was not run. |
| N5 — correction census | `resolved; not regressed` | `census-round4-corrections.ps1:48-174` declares 109 values and `:206-279` performs both scopes, dispositions every FOLDER hit, propagates `rg` errors, and exits 3 on stale sites. Fresh 218-sweep reconciliation passed. |
| N6 — executable verification owner | `resolved; not regressed` | `run-verification-plan.ps1:25-41` owns exactly 16 scheduled sections; `:44-58` inventories gate existence; `:64-85` executes and propagates the first failure. The 16-section inventory self-test passed. The new `[B]` contradiction below is a separate scheduling defect, not regression to the old prose-only owner. |
| N7 — warm-process label | `resolved; not regressed` | `implementation-plan.md:299` remains `out-of-scope` with no fake deferred MEU and retains the measurement-triggered future proposal. |
| F2 — phantom closeout validator | `resolved; not regressed` | `assert-closeout.ps1:10-62` invokes only on-disk plan gates and existing tools. R5-3 concerns the strength of the reflection predicate, not a missing executable. |
| F5 — publication atomicity | `resolved; not regressed` | `implementation-plan.md:175-186` retains in-inbox staging, pixel guard, same-directory `renameSync`, staging suppression, and unlink/no-register on every non-confirm path. |
| F6 — RED rows end green | `resolved; not regressed` | Task rows 3 and 6 still capture the suite code and exit with the oracle code (`task.md:44`, `:48`); both RED oracle self-tests passed. |
| F7 — repeated minimum edge | `resolved; not regressed` | The only numeric definition remains `implementation-plan.md:158` plus its executable mirror `named-sets.json:11`; downstream text uses `PICKER_MIN_EDGE_PX`. |
| F8 — repeated exit mapping | `resolved; not regressed` | The normative open-world table remains `implementation-plan.md:159-162` plus `named-sets.json:12-14`; downstream text uses `PICKER_EXIT_*`, and unknown codes fail closed. |

### Remaining and New Findings

| # | Severity | Finding and concrete failure scenario | File:Line | Required correction |
|---|---|---|---|---|
| R4-2-R5 | High | **PR-8 — AC-40.20 still confuses syntax presence with reachability.** A compiled `Main` containing `return 1; return Run(args, new RegionForm());` (CS0162 warning, not an error) has the required top-level invocation, contains none of `BINDING_DEADCODE_FORMS`, and can satisfy the planned Roslyn assertions while the form is unreachable. Three trivially passing methods with the required identifiers also satisfy the live name/count binding. | `implementation-plan.md:219`; `named-sets.json:56-72`; `assert-picker-binding.ps1:103-111`, `:169-199`, `:350-364`; `C:/Temp/av-kit/round5-adversarial-simulations.json` | Make AC-40.20 analyze control flow, not only syntax presence (e.g. Roslyn CFG/dataflow or a strictly validated terminal-return body), and bind each named test to a substantive negative fixture. Add the after-unconditional-return program as a failing oracle. |
| R4-3-R5 | High | **PR-4 / PR-8 — echo-only scripts plus a stale JSON report still close the real-Electron gate.** The two exact echo bodies above satisfy all substring checks, both npm scripts exit 0, and the runner never removes or freshness-binds the separate JSON artifact; §9d then accepts an earlier valid report. Wiring and execution can therefore pass with no current capture test or stub build. | `assert-e2e-wired.ps1:308-329`; `task.md:50`; `run-verification-plan.ps1:37-40`, `:64-79`; `C:/Temp/av-kit/round5-adversarial-simulations.json` | Validate executable script segments (not substring presence), reject `echo`/chained hollow forms, delete or uniquely name the JSON output before §9c, and require the report to be newly created by that run (run id or pre/post timestamp/hash binding). Add the echo+stale-report fixture. |
| R4-4-R5 | High | **PR-8 / `[B]` evidence — unrelated or stale files still authenticate smoke completion.** An existing oracle receipt containing `8` passes as an 8 ms unblocked smoke; a blocked disposition can point to any nonempty file and any regex-shaped but nonexistent follow-up id. No live-smoke command, error output, evidence class, freshness, or follow-up target is verified. | `assert-smoke-disposition.ps1:33-78`; `task.md:52`, `:87`; `C:/Temp/av-kit/round5-adversarial-simulations.json` | Bind the receipt to the row-9 smoke command/run and required content. For external-error/missing-dependency require the command and error signature in that receipt; for all blocked cases resolve `FOLLOWUP` to an actual registered issue/MEU artifact. Add unrelated/stale receipt fixtures. |
| R5-1 | High | **PR-4 — the BUILD_PLAN audit cannot fail.** The exact row-8 validation exits 0 while today's hub still has four overlay references. It only serializes matches and has no stale/new predicate; H1-2 and closeout do not check `docs/BUILD_PLAN.md`. Row 8 can be marked complete with the hub untouched. | `task.md:51`; `implementation-plan.md:309-318`; `C:/Temp/av-kit/round5-build-plan-audit-exact.json` | Define the allowed final hub wording and fail on stale `overlay`/`desktopCapturer` matches or absence of the native picker wording. Add the audit to the registered verification/closeout path and a stale-hub negative oracle. |
| R5-2 | High | **PR-1 / sequencing — the declared E2E `[B]` path cannot reach DONE.** Row 7a permits `[B]` when Electron cannot launch without a display, and predecessor completeness treats `[B]` as closed. H1-2 then unconditionally reruns UI E2E and capture sections 9b-9d and propagates the same failure. Thus a valid evidence-gated blocker can never pass the required H1 gate, contradicting the task's own definition of done. | `implementation-plan.md:227`, `:346-351`; `task.md:50`, `:55`, `:87`; `run-verification-plan.ps1:37-41`, `:76-83` | Either remove `[B]` eligibility and state that no-display is a hard external stop, or add a machine-checked E2E disposition that lets H1 re-run Wired while conditionally accepting the documented external blocker for Executed, with receipt and real follow-up validation. |
| R5-3 | High | **PR-4 / DR-4 — reflection closeout accepts a 69-byte skeleton.** H2-2 and closeout check only four substring markers from `REFLECTION_MARKERS`; the mandatory completion-preflight contract requires the full marker set, size >2,000 bytes, and substantive sections. The four-line body in the adversarial receipt passes the plan gate while missing nine required pattern groups and every substantive answer; no independent review occurs after H2. | `task.md:64-67`; `named-sets.json:193-200`; `assert-closeout.ps1:42-57`; `.agent/skills/completion-preflight/SKILL.md:86`, `:151-156`; `C:/Temp/av-kit/round5-adversarial-simulations.json` | Make H2-2/closeout invoke the canonical completion-preflight reflection marker set and enforce its >2,000-byte/substantive-placeholder checks. Add a four-marker skeleton negative oracle. |

No Critical, Medium, or Low findings were identified.

### Checklist Verdicts

| Check | Result | Evidence |
|---|---|---|
| PR-1 Plan/task alignment | **fail** | Scope/order otherwise align, but R5-2 makes the task's `[B]` contract incompatible with the sole verification runner. |
| PR-2 Not-started confirmation | pass | `native/region-picker*`, `capture-picker.ts`, capture E2E, MEU handoff, and implementation review are absent; the Chromium overlay files remain present. No product work has started. |
| PR-3 Task contract completeness | pass | Every actionable row has task, owner, deliverable, exact validation, dependency, context strategy, durable outputs, builder model, and status. `rtk`, `pwsh`, `dotnet`, `npm`, `uv`, and `python` resolve; every cited gate/tool executable exists. |
| PR-4 Validation realism | **fail** | R4-3-R5, R5-1, R5-2, and R5-3 demonstrate real false-pass or impossible validation paths. |
| PR-5 Source-backed planning | pass | All 20 ACs use allowed source labels; no new unsourced product behavior was found. |
| PR-6 Handoff/corrections readiness | pass | Supplied/fresh census, 218 sweeps, and the reconciled 724-row disposition multiset are complete and untruncated. |
| PR-7 Scope discipline | pass | Human-approved no-fallback, Research-backed warm-process exclusion, canonical platform/annotation deferrals, separate `mss`/bbox contract, approved MEU-37/38, GDI map, and NSIS basis all verify (`implementation-plan.md:298-305`; current canon receipts). |
| PR-8 Control reachability and totality | **fail** | R4-2-R5, R4-3-R5, and R4-4-R5 supply concrete materially absent observables/evidence that pass. Publication and exit-code classification remain atomic/fail-closed. |
| PR-9 Single-statement discipline | pass | Exact sweeps found one numeric minimum definition, one normative exit table plus named executable mirrors, and named owners for ACs, E2E cases, binding tests, smoke classes, and section inventory. No conflicting live spelling exists. |
| DR-1 Claim-to-state match | **fail** | R4-2/R4-3/R4-4 correction claims overstate what the current controls prove. |
| DR-2 Residual old terms | pass | Fresh census exits 0 with `STALE SITES: 0`; old forms survive only in declaration/history contexts. |
| DR-3 Downstream references updated | pass | Plan/task, named sets, all gates, runner, file inventory, csproj names, E2E/stub paths, handoff/review/reflection, registry, and hub audit are inventoried. |
| DR-4 Verification robustness | **fail** | All six findings demonstrate a missing observable, stale/unrelated evidence acceptance, impossible blocker path, or skeletal closeout false-pass. |
| DR-5 Evidence auditability | pass | Commands, fixed paths, counts, raw census, self-tests, and adversarial inputs are reproducible; robustness failures are separately recorded under DR-4. |
| DR-6 Cross-reference integrity | **fail** | R5-2 contradicts `[B]` closure semantics across AC/task/runner. Other Python/REST/MCP/filmstrip boundaries remain consistent. |
| DR-7 Evidence freshness | pass | Fresh runs reproduce 8 oracle gate families, 16 sections, 109x2 sweeps, 724 dispositions, and exact AC membership: 20 actual = `AC_COUNT` 20 = 20 `AC_IDS`. |
| DR-8 Completion vs residual risk | pass | Plan/task remain draft/unstarted and make no implementation-complete claim. |

### Commands Executed

All shell commands used RTK routing and redirected all process streams under `C:/Temp/av-kit/`; exit codes were captured before receipt reads. Key Round 5 receipts: `round5-oracle-selftests.txt`, `round5-verification-inventory.txt`, `round5-census-rerun.txt`, `round5-census-integrity.txt`, `round5-census-diff.txt`, `round5-ac-executable-audit.json`, `round5-not-started.json`, `round5-pr7-bases.txt`, `round5-pr9-sweep.txt`, `round5-build-plan-audit-exact.json`, and `round5-adversarial-simulations.json`. `assert-packaging-clean.ps1` was not run without `-SkipBuild`; no live/product gate was run against the intentionally absent implementation.

### Follow-up Actions

1. Make the binding proof control-flow-aware and add the after-return negative fixture.
2. Make capture/stub scripts executable-segment checks and freshness-bind the JSON report.
3. Bind smoke evidence to the actual command/error and resolve follow-up ids to real artifacts.
4. Replace the BUILD_PLAN report-only audit with a failing predicate in verification/closeout.
5. Reconcile row 7a's no-display `[B]` path with H1's verification runner.
6. Enforce the canonical reflection structural/substantive quality contract in H2/closeout.
7. Re-run all self-tests, the 16-section inventory, AC/executable audits, and a correction census covering every changed predicate before Round 6.

### Residual Risk

After these controls are corrected, real multi-monitor/DPI WinForms behavior, clean self-contained packaging, Electron launch, and live perceptual latency remain execution-time risks for the planned xunit, clean packaging, real-Electron Playwright, and smoke receipts. Those risks do not excuse the current controls accepting unreachable code, stale/unrelated evidence, stale hub text, or skeletal closeout artifacts.

### Verdict

`changes_required` — PR-6 is sufficient; R4-1 is resolved; N3/N5/N6/N7 and F2/F5/F6/F7/F8 remain resolved; AC membership is exactly 20 and every named executable exists. Six evidence-backed High issues remain: three Round 4 corrections are partial, the BUILD_PLAN audit cannot fail, the declared E2E `[B]` path cannot reach closeout, and the reflection gate accepts a noncompliant skeleton. Do not enter execution.

---

## Round 5 Corrections — Blast-Radius Census & Disposition Log

> Implementor-authored evidence appended under explicit human direction
> (`USER_EXPLICIT`: "continue until approved"). This section makes no verdict claim; it
> supplies the PR-6 census and per-hit correction log that Round 6 requires before content
> review resumes. All six Round 5 findings were treated as blocking, and were corrected in
> the order the Round 5 Follow-up Actions list gives them.

### What was corrected (Round 5 findings R4-2-R5, R4-3-R5, R4-4-R5, R5-1, R5-2, R5-3)

| # | Finding | Correction landed |
|---|---------|-------------------|
| R4-2-R5 | The hardened binding gate still equated *syntactic presence* with *reachability*: `return 1; return Run(args, new RegionForm());` is CS0162 (a **warning**), so the seam is top-level yet never executes; and the statement flush split on every `}`, so an object initializer or lambda body was minced into fake top-level statements. The Roslyn suite could also be four empty methods with the right names. | Three changes. (1) `Get-TopLevelStatements` flushes a fragment at `}` **only when the fragment is led by a `BINDING_BLOCK_KEYWORDS` word** (`if`/`else`/`for`/`foreach`/`while`/`do`/`switch`/`try`/`catch`/`finally`/`using`/`lock`/`fixed`/`unsafe`/`checked`/`unchecked`), so expression fragments — object initializers, lambdas, collection initializers — are never split at a brace. (2) `BINDING_TERMINAL_FORMS` marks the statements after which control cannot continue (`return`, `throw`, `goto`); any required entry call appearing **after** a terminal form at depth 0 is rejected as unreachable, which is exactly the reviewer's CS0162 input. **[Reconciled in round 6 - correction-log defect]** this row as first written also listed `Environment.Exit(` among the round-5 terminal forms. That was false: round 5 shipped `return`/`throw`/`goto` only, which is why round-6 finding R6-1 could still terminate the seam through `Environment.Exit(`. `Environment.Exit(`, `Environment.FailFast(` and label-form terminators were added in **round 6**, not round 5; the sentence above now states what round 5 actually landed. (3) `BINDING_RUNTIME_REQUIRED_ANCHORS` / `BINDING_RUNTIME_TEST_ANCHORS` require each named Roslyn test to carry its own fixture anchor, so a file of four correctly-named empty methods fails. |
| R4-3-R5 | An npm script satisfied its "required segment" check by *containing* the command as a substring, so `echo "playwright test"` passed; and `-Mode Executed` accepted any JSON report on disk, including a green one left by an earlier run. | (1) `Test-ScriptSegment` splits a script on `SCRIPT_SEGMENT_SPLIT_PATTERN`, strips `SCRIPT_ALLOWED_PREFIXES` (`cross-env`, `npx`, env assignments) from each segment, and requires a segment that **starts with** the head command and carries every required token. A segment whose head is in `SCRIPT_HOLLOW_HEADS` (`echo`, `printf`, `rem`, `:`, `true`) is not evidence. (2) New single owner `arm-run.ps1` **deletes the artifact and writes a stamp** before the producing step (`RUN_STAMPS`); `Test-ArtifactFresh` fails with "the step was never armed" when the stamp is absent and "stale receipt" when the artifact predates it. Wired as Verification Plan §`9a1 ARM_E2E_CAPTURE` and as the first command of task rows 7a and 9. |
| R4-4-R5 | `SMOKE_DISPOSITION` still had four holes: any readable file satisfied `RECEIPT`; the receipt was never tied to the row's command; `LATENCY_MS=8` passed against any file containing an `8`; and a `[B]` needed no reproduced error and no *registered* follow-up. | `assert-smoke-disposition.ps1` was rewritten against `lib-disposition.ps1`. `RECEIPT` must **be** `SMOKE_RECEIPT_FILE` (slash-normalised compare) — an unrelated file is not evidence; it must be **fresh** relative to the arming stamp; and it must contain every `SMOKE_RECEIPT_REQUIRED_MARKERS` command signature. `BLOCKED=no` requires the latency as an **anchored measurement line** driven by `SMOKE_LATENCY_RECEIPT_KEY` (`picker_startup_ms=<n>` on its own line), not a bare substring. `BLOCKED=yes` in an `SMOKE_ERROR_SIGNATURE_CLASSES` class requires an `ERROR_SIGNATURE` present **verbatim** in the receipt, and `Resolve-Followup` fails unless the `FOLLOWUP` id actually appears in one of `FOLLOWUP_SOURCES`. New oracles: **D11/D11b** (unrelated receipt; latency only in prose), **D12** (no command signature), **D13** (stale receipt), **D14/D14b** (missing / unreproduced error signature), **D15** (unregistered follow-up). |
| R5-1 | The BUILD_PLAN.md audit was report-only — it printed a match count and task row 8 could close while changing nothing. That is the AGENTS.md §Pre-Handoff Self-Review item-4 failure verbatim. | New gate `assert-build-plan-hub.ps1` (**AC-40.21**), the single owner. No line of `HUB_FILE` may match a `HUB_FORBIDDEN_TOKENS` term (`desktopCapturer`, `overlay`, OrdinalIgnoreCase) unless that same line also names a `HUB_REQUIRED_TOKENS` term, and the hub must name the replacement at least once. **Today's hub fails it** — four bare `overlay` lines (32, 93, 111, 143), zero `region picker`; live run exit `1`. Oracle **H0** pins three of those four line texts verbatim so the non-vacuity proof survives the fix; **H1** bare `desktopCapturer`, **H2** capitalised `Overlay`, **H3** no replacement term, **H4** empty all rejected; **H5** a reconciled hub accepted. Wired as Verification Plan §`8a`, re-run by `assert-closeout.ps1`, and the plan's prose section is now "BUILD_PLAN.md Hub Reconciliation" carrying the predicate instead of the old match-count command. |
| R5-2 | Row 7a may take an evidenced no-display `[B]`, but H1's runner failed hard on the very condition the row is allowed to be blocked by — so that `[B]` path was unreachable, and two steps could each disposition the same capture E2E. | `-Mode Executed` (§`9d`) is the **single disposition point**. Steps `9b`/`9c` carry `dispositionedBy = 9d`; the runner defers their nonzero exits and adjudicates after the loop, excusing them **only** when 9d itself passed **and** the disposition it validated records `BLOCKED=yes` — which `Test-BlockedEvidence` only accepts with an objective class, a reproduced `ERROR_SIGNATURE`, a resolvable `FOLLOWUP`, and the pinned fresh receipt. With `BLOCKED=no`, 9d demands a fresh green report, so a red run still fails the runner. Task row 7a's two run steps deliberately do **not** exit early, and taking that `[B]` now includes **registering `E2E-SANDBOX-NODISPLAY` in `.agent/context/known-issues.md`** — it is referenced across the build plan today but registered nowhere, so an unregistered id fails `Resolve-Followup`. |
| R5-3 | The closeout gate checked four hand-picked substrings (`REFLECTION_MARKERS`) inlined in `assert-closeout.ps1`; a file of four headings passed — precisely the "writing closeout artifacts from memory" failure AGENTS.md calls a quality violation equivalent to shipping code without tests. | New gate `assert-reflection-quality.ps1` (**AC-40.22**) owns the canonical contract from `.agent/skills/completion-preflight/SKILL.md` §Closeout Artifact Quality Check: all nine `REFLECTION_PATTERNS` section groups; every pattern that is a bare YAML key (`sections:`, `loaded:`, `decisive_rules:`) must own a non-empty, more-indented child block; no `REFLECTION_PLACEHOLDER_FORMS` survivor; and at least `REFLECTION_MIN_BYTES` of prose once headings, list bullets, fences and rules are excluded. `REFLECTION_MARKERS` is **deleted** from `named-sets.json` and the inline loop is **deleted** from `assert-closeout.ps1`, leaving one owner (PR-9). Oracles **F0** (complete reflection accepted), **F1** (the four-marker skeleton), **F2/F2b** (headings-only; structure complete but prose-free), **F3/F3b** (hollow `sections:` / `decisive_rules:`), **F4** (`_Answer here_`), **F5** (no coverage block), **F6** (no design-rules section), **F7** (empty). |

Collateral, in the same pass: `AC_COUNT` 20 → **22** (AC-40.21 hub, AC-40.22 reflection) with
`AC_IDS` extended; the Verification Plan grew 16 → **18** scheduled sections (`8a` BUILD_PLAN_HUB,
`9a1` ARM_E2E_CAPTURE); task row H1-2 now enumerates all eighteen and states the `dispositionedBy`
rule; and **PR-9** was applied to the shared disposition logic — `Get-DispositionMap`,
`Test-DispositionMarkers`, `Resolve-Followup`, `Test-BlockedEvidence` and `Test-ArtifactFresh`
now live once, in `lib-disposition.ps1`, dot-sourced by the smoke gate, the E2E gate and the
runner instead of being restated in each.

### Census receipt

- **Receipt (complete, untruncated):** `C:/Temp/av-kit/census-round5.txt` — 1,616 lines, script exit `0`.
- **Sweep script (re-runnable):** `docs/execution/plans/2026-08-27-p9-capture-native-picker/census-round5-corrections.ps1`
- **Method:** `rg -F -n --no-heading --with-filename` (fixed-string, so regex metacharacters in a value cannot silently change what was searched). No `head`, `tail`, `Select-Object`, or `Where-Object` appears anywhere in the sweep or in the receipt.
- **Coverage:** 107 declared values × 2 scopes = **214 sweeps**. Scope `PAIR` = `implementation-plan.md` + `task.md`; scope `FOLDER` = every file in the plan folder, because `named-sets.json`, `lib-disposition.ps1`, `arm-run.ps1`, the `assert-*.ps1` gates and `run-verification-plan.ps1` are themselves part of the correction and must agree with the prose. `FOLDER` is a superset of `PAIR`, so the log below enumerates `FOLDER` hits; the receipt carries both.
- **Directions:** every changed literal, term, count, set, threshold and predicate was swept in **three** declared directions — `old`, `new`, `carry` — with the same contract as the Round 3 and Round 4 censuses.
- **Exit codes:** worst `rg` exit code across all 214 sweeps = `0`; no sweep returned `>1`, so none failed to execute.
- **Self-enforcing:** the sweep script **exits 3** if any `old` form survives outside a census declaration table or the declared retained-mention allowlist. This run exits `0` with `STALE SITES: 0`.
- **Total hits dispositioned below: 755** — every `file:line` in the receipt's `FOLDER` scope (292 `updated`, 463 `confirmed-consistent`, 0 stale).

### Old-form sweeps (stale text removed)

| Finding | Old form swept | PAIR result |
|---|---|---|
| R5-1 | `build-plan-audit.json` | `rc=1` no match |
| R5-1 | the old `## BUILD_PLAN.md Audit` heading | `rc=1` no match |
| R5-1 | the report-only `desktopCapturer` / `overlay` / `region-picker` alternation | `rc=1` no match |
| R5-1 | `If zero stale matches` | `rc=1` no match |
| R5-3 | `REFLECTION_MARKERS` | `rc=0`, **2 hits, both allowlisted retained mentions** — `implementation-plan.md:111` (gate table) and `:236` (AC-40.22), which name the *retired* list to state what was deleted and why. The executable loop is gone from `assert-closeout.ps1`; `named-sets.json` returns `rc=1`. |
| X-ac-count | `"AC_COUNT": 20` | `rc=1` no match |
| X-ac-count | `20 ACs` | `rc=1` no match |
| X-sections | `16 sections` | `rc=1` no match |
| X-sections | `16-section` | `rc=1` no match |
| X-sections | `sections 0-6, 8, 9, 10` (task row H1-2's old enumeration) | `rc=1` no match |

Every `old` form is gone from both scopes except the two declared `REFLECTION_MARKERS`
retained mentions above, which the sweep script allowlists by `value + file` and justifies
inline. The Round 3 retained mention (`deferred`) and the Round 4 values are not Round 5
values and are not re-swept here; they remain allowlisted in their own census scripts.

### Gate self-test, inventory and audit receipts (re-run after the corrections)

| Receipt | Result |
|---|---|
| `C:/Temp/av-kit/r6-oracles.txt` | `PASS: ORACLE_SELFTESTS 11 gates proven non-vacuous` — exit `0`. Task rows T1–T11; red oracle × 2; overlay deletion; binding B1–B5b / E1–E3 / R1–R3 plus the new post-terminal and block-keyword oracles; packaging P1–P4; E2E wiring S1–S5, G1–G3, X1–X6; smoke disposition D1–D15; **RUN_ARM** A1–A3; **BUILD_PLAN_HUB** H0–H5; **REFLECTION_QUALITY** F0–F7. |
| `C:/Temp/av-kit/r6-vplan.txt` | `PASS: VERIFICATION_PLAN inventory (18 sections, every gate script present)` — exit `0`. |
| `C:/Temp/av-kit/r6-taskrows.txt` | `PASS: TASK_ROW_GATE self-test` (T1–T11) — exit `0`. |
| `C:/Temp/av-kit/r6-hub-live.txt` | **exit `1` — expected and required.** The live hub gate fails on today's `docs/BUILD_PLAN.md`, proving R5-1's predicate is non-vacuous *before* the edit. Task row 8 cannot close as a no-op. |
| `C:/Temp/av-kit/r6-ac-audit.txt` | `RESULT: PASS` — exit `0`. 22 plan AC rows; id set equals `AC_IDS` (the table is grouped by delivery layer, so numeric order is not required); **0 ACs unreachable** — every AC is named by a task row or a plan gate/verification row outside the AC table. This audit found and closed one real gap: AC-40.22 was declared but scheduled nowhere, so task row H2-2's deliverable now cites it. |
| `C:/Temp/av-kit/r6-exec-audit.txt` | `rows missing an executable-receipt token: 0` — exit `0`. All 26 task rows redirect every stream to `C:/Temp/av-kit/`, capture `$LASTEXITCODE` into a variable immediately, and exit with a captured code. The RED rows (3, 6) exit with the red **oracle's** verdict (`exit $gate`), not the deliberately-nonzero test run — the audit accepts any exit whose variable was assigned from `$LASTEXITCODE` on that row. |
| `C:/Temp/av-kit/census-round5.txt` | `STALE SITES: 0` — exit `0`, 1,616 lines. |

> `assert-handoff-acs.ps1` exits `1` at this point, solely on `missing`
> `.agent/context/handoffs/2026-08-27-p9-capture-native-picker-MEU-40-handoff.md`. That is an
> **execution-phase** artifact that does not exist during planning; the plan-side totality
> check (plan exposes N ACs equal to `AC_COUNT`, ids equal to `AC_IDS`) runs *before* the
> handoff-existence check and passed, and the same fact is proven independently by the AC
> audit receipt above.

### Per-hit disposition log (755 rows, nothing dropped)

| Finding | Dir | Value | Site (`file:line`) | Disposition | Justification |
|---|---|---|---|---|---|
| R4-2-R5 | new | `BINDING_BLOCK_KEYWORDS` | `named-sets.json:102` | `updated` | the value did not exist in this folder before the round-5 pass, so this line was written by that pass |
| R4-2-R5 | new | `BINDING_BLOCK_KEYWORDS` | `implementation-plan.md:221` | `updated` | the value did not exist in this folder before the round-5 pass, so this line was written by that pass |
| R4-2-R5 | new | `BINDING_BLOCK_KEYWORDS` | `census-round5-corrections.ps1:56` | `confirmed-consistent` | census declaration table (the sweep's own input list), not a plan assertion |
| R4-2-R5 | new | `BINDING_BLOCK_KEYWORDS` | `assert-picker-binding.ps1:38` | `updated` | the value did not exist in this folder before the round-5 pass, so this line was written by that pass |
| R4-2-R5 | new | `BINDING_TERMINAL_FORMS` | `named-sets.json:97` | `updated` | the value did not exist in this folder before the round-5 pass, so this line was written by that pass |
| R4-2-R5 | new | `BINDING_TERMINAL_FORMS` | `implementation-plan.md:221` | `updated` | the value did not exist in this folder before the round-5 pass, so this line was written by that pass |
| R4-2-R5 | new | `BINDING_TERMINAL_FORMS` | `census-round5-corrections.ps1:57` | `confirmed-consistent` | census declaration table (the sweep's own input list), not a plan assertion |
| R4-2-R5 | new | `BINDING_TERMINAL_FORMS` | `assert-picker-binding.ps1:18` | `updated` | the value did not exist in this folder before the round-5 pass, so this line was written by that pass |
| R4-2-R5 | new | `BINDING_TERMINAL_FORMS` | `assert-picker-binding.ps1:37` | `updated` | the value did not exist in this folder before the round-5 pass, so this line was written by that pass |
| R4-2-R5 | new | `BINDING_RUNTIME_REQUIRED_ANCHORS` | `named-sets.json:127` | `updated` | the value did not exist in this folder before the round-5 pass, so this line was written by that pass |
| R4-2-R5 | new | `BINDING_RUNTIME_REQUIRED_ANCHORS` | `implementation-plan.md:222` | `updated` | the value did not exist in this folder before the round-5 pass, so this line was written by that pass |
| R4-2-R5 | new | `BINDING_RUNTIME_REQUIRED_ANCHORS` | `census-round5-corrections.ps1:58` | `confirmed-consistent` | census declaration table (the sweep's own input list), not a plan assertion |
| R4-2-R5 | new | `BINDING_RUNTIME_REQUIRED_ANCHORS` | `assert-picker-binding.ps1:44` | `updated` | the value did not exist in this folder before the round-5 pass, so this line was written by that pass |
| R4-2-R5 | new | `BINDING_RUNTIME_TEST_ANCHORS` | `named-sets.json:132` | `updated` | the value did not exist in this folder before the round-5 pass, so this line was written by that pass |
| R4-2-R5 | new | `BINDING_RUNTIME_TEST_ANCHORS` | `implementation-plan.md:222` | `updated` | the value did not exist in this folder before the round-5 pass, so this line was written by that pass |
| R4-2-R5 | new | `BINDING_RUNTIME_TEST_ANCHORS` | `census-round5-corrections.ps1:59` | `confirmed-consistent` | census declaration table (the sweep's own input list), not a plan assertion |
| R4-2-R5 | new | `BINDING_RUNTIME_TEST_ANCHORS` | `assert-picker-binding.ps1:46` | `updated` | the value did not exist in this folder before the round-5 pass, so this line was written by that pass |
| R4-2-R5 | carry | `BINDING_DEADCODE_FORMS` | `named-sets.json:88` | `confirmed-consistent` | pre-existing value, read at the cited line: it agrees with the corrected round-5 rule |
| R4-2-R5 | carry | `BINDING_DEADCODE_FORMS` | `implementation-plan.md:221` | `confirmed-consistent` | pre-existing value, read at the cited line: it agrees with the corrected round-5 rule |
| R4-2-R5 | carry | `BINDING_DEADCODE_FORMS` | `census-round5-corrections.ps1:60` | `confirmed-consistent` | census declaration table (the sweep's own input list), not a plan assertion |
| R4-2-R5 | carry | `BINDING_DEADCODE_FORMS` | `census-round4-corrections.ps1:68` | `confirmed-consistent` | census declaration table (the sweep's own input list), not a plan assertion |
| R4-2-R5 | carry | `BINDING_DEADCODE_FORMS` | `assert-picker-binding.ps1:36` | `confirmed-consistent` | pre-existing value, read at the cited line: it agrees with the corrected round-5 rule |
| R4-2-R5 | carry | `Get-TopLevelStatements` | `census-round5-corrections.ps1:61` | `confirmed-consistent` | census declaration table (the sweep's own input list), not a plan assertion |
| R4-2-R5 | carry | `Get-TopLevelStatements` | `census-round4-corrections.ps1:77` | `confirmed-consistent` | census declaration table (the sweep's own input list), not a plan assertion |
| R4-2-R5 | carry | `Get-TopLevelStatements` | `assert-picker-binding.ps1:16` | `confirmed-consistent` | pre-existing value, read at the cited line: it agrees with the corrected round-5 rule |
| R4-2-R5 | carry | `Get-TopLevelStatements` | `assert-picker-binding.ps1:183` | `confirmed-consistent` | pre-existing value, read at the cited line: it agrees with the corrected round-5 rule |
| R4-2-R5 | carry | `Get-TopLevelStatements` | `assert-picker-binding.ps1:246` | `confirmed-consistent` | pre-existing value, read at the cited line: it agrees with the corrected round-5 rule |
| R4-2-R5 | carry | `Test-DeadCode` | `census-round5-corrections.ps1:62` | `confirmed-consistent` | census declaration table (the sweep's own input list), not a plan assertion |
| R4-2-R5 | carry | `Test-DeadCode` | `census-round4-corrections.ps1:78` | `confirmed-consistent` | census declaration table (the sweep's own input list), not a plan assertion |
| R4-2-R5 | carry | `Test-DeadCode` | `assert-picker-binding.ps1:135` | `confirmed-consistent` | pre-existing value, read at the cited line: it agrees with the corrected round-5 rule |
| R4-2-R5 | carry | `Test-DeadCode` | `assert-picker-binding.ps1:226` | `confirmed-consistent` | pre-existing value, read at the cited line: it agrees with the corrected round-5 rule |
| R4-2-R5 | carry | `Test-DeadCode` | `assert-picker-binding.ps1:242` | `confirmed-consistent` | pre-existing value, read at the cited line: it agrees with the corrected round-5 rule |
| R4-2-R5 | carry | `Test-RuntimeReceipt` | `census-round5-corrections.ps1:63` | `confirmed-consistent` | census declaration table (the sweep's own input list), not a plan assertion |
| R4-2-R5 | carry | `Test-RuntimeReceipt` | `census-round4-corrections.ps1:79` | `confirmed-consistent` | census declaration table (the sweep's own input list), not a plan assertion |
| R4-2-R5 | carry | `Test-RuntimeReceipt` | `assert-picker-binding.ps1:292` | `confirmed-consistent` | pre-existing value, read at the cited line: it agrees with the corrected round-5 rule |
| R4-2-R5 | carry | `Test-RuntimeReceipt` | `assert-picker-binding.ps1:523` | `confirmed-consistent` | pre-existing value, read at the cited line: it agrees with the corrected round-5 rule |
| R4-2-R5 | carry | `Test-RuntimeReceipt` | `assert-picker-binding.ps1:524` | `confirmed-consistent` | pre-existing value, read at the cited line: it agrees with the corrected round-5 rule |
| R4-2-R5 | carry | `Test-RuntimeReceipt` | `assert-picker-binding.ps1:526` | `confirmed-consistent` | pre-existing value, read at the cited line: it agrees with the corrected round-5 rule |
| R4-2-R5 | carry | `Test-RuntimeReceipt` | `assert-picker-binding.ps1:529` | `confirmed-consistent` | pre-existing value, read at the cited line: it agrees with the corrected round-5 rule |
| R4-2-R5 | carry | `Test-RuntimeReceipt` | `assert-picker-binding.ps1:532` | `confirmed-consistent` | pre-existing value, read at the cited line: it agrees with the corrected round-5 rule |
| R4-2-R5 | carry | `Test-RuntimeReceipt` | `assert-picker-binding.ps1:536` | `confirmed-consistent` | pre-existing value, read at the cited line: it agrees with the corrected round-5 rule |
| R4-2-R5 | carry | `Test-RuntimeReceipt` | `assert-picker-binding.ps1:573` | `confirmed-consistent` | pre-existing value, read at the cited line: it agrees with the corrected round-5 rule |
| R4-2-R5 | carry | `Microsoft.CodeAnalysis.CSharp` | `named-sets.json:128` | `confirmed-consistent` | pre-existing value, read at the cited line: it agrees with the corrected round-5 rule |
| R4-2-R5 | carry | `Microsoft.CodeAnalysis.CSharp` | `implementation-plan.md:222` | `confirmed-consistent` | pre-existing value, read at the cited line: it agrees with the corrected round-5 rule |
| R4-2-R5 | carry | `Microsoft.CodeAnalysis.CSharp` | `implementation-plan.md:273` | `confirmed-consistent` | pre-existing value, read at the cited line: it agrees with the corrected round-5 rule |
| R4-2-R5 | carry | `Microsoft.CodeAnalysis.CSharp` | `census-round5-corrections.ps1:64` | `confirmed-consistent` | census declaration table (the sweep's own input list), not a plan assertion |
| R4-2-R5 | carry | `Microsoft.CodeAnalysis.CSharp` | `census-round4-corrections.ps1:75` | `confirmed-consistent` | census declaration table (the sweep's own input list), not a plan assertion |
| R4-2-R5 | carry | `Microsoft.CodeAnalysis.CSharp` | `assert-picker-binding.ps1:462` | `confirmed-consistent` | pre-existing value, read at the cited line: it agrees with the corrected round-5 rule |
| R4-2-R5 | carry | `Microsoft.CodeAnalysis.CSharp` | `assert-picker-binding.ps1:463` | `confirmed-consistent` | pre-existing value, read at the cited line: it agrees with the corrected round-5 rule |
| R4-2-R5 | carry | `BINDING_RUNTIME_FILTER` | `run-verification-plan.ps1:46` | `confirmed-consistent` | pre-existing value, read at the cited line: it agrees with the corrected round-5 rule |
| R4-2-R5 | carry | `BINDING_RUNTIME_FILTER` | `named-sets.json:152` | `confirmed-consistent` | pre-existing value, read at the cited line: it agrees with the corrected round-5 rule |
| R4-2-R5 | carry | `BINDING_RUNTIME_FILTER` | `implementation-plan.md:222` | `confirmed-consistent` | pre-existing value, read at the cited line: it agrees with the corrected round-5 rule |
| R4-2-R5 | carry | `BINDING_RUNTIME_FILTER` | `census-round5-corrections.ps1:65` | `confirmed-consistent` | census declaration table (the sweep's own input list), not a plan assertion |
| R4-2-R5 | carry | `BINDING_RUNTIME_FILTER` | `census-round4-corrections.ps1:71` | `confirmed-consistent` | census declaration table (the sweep's own input list), not a plan assertion |
| R4-2-R5 | carry | `BINDING_RUNTIME_RECEIPT` | `run-verification-plan.ps1:46` | `confirmed-consistent` | pre-existing value, read at the cited line: it agrees with the corrected round-5 rule |
| R4-2-R5 | carry | `BINDING_RUNTIME_RECEIPT` | `named-sets.json:153` | `confirmed-consistent` | pre-existing value, read at the cited line: it agrees with the corrected round-5 rule |
| R4-2-R5 | carry | `BINDING_RUNTIME_RECEIPT` | `implementation-plan.md:222` | `confirmed-consistent` | pre-existing value, read at the cited line: it agrees with the corrected round-5 rule |
| R4-2-R5 | carry | `BINDING_RUNTIME_RECEIPT` | `census-round5-corrections.ps1:66` | `confirmed-consistent` | census declaration table (the sweep's own input list), not a plan assertion |
| R4-2-R5 | carry | `BINDING_RUNTIME_RECEIPT` | `census-round4-corrections.ps1:72` | `confirmed-consistent` | census declaration table (the sweep's own input list), not a plan assertion |
| R4-2-R5 | carry | `BINDING_RUNTIME_RECEIPT` | `assert-picker-binding.ps1:43` | `confirmed-consistent` | pre-existing value, read at the cited line: it agrees with the corrected round-5 rule |
| R4-2-R5 | carry | `BINDING_RUNTIME_RECEIPT` | `assert-picker-binding.ps1:571` | `confirmed-consistent` | pre-existing value, read at the cited line: it agrees with the corrected round-5 rule |
| R4-2-R5 | carry | `assert-picker-binding.ps1` | `task.md:46` | `confirmed-consistent` | pre-existing value, read at the cited line: it agrees with the corrected round-5 rule |
| R4-2-R5 | carry | `assert-picker-binding.ps1` | `run-verification-plan.ps1:47` | `confirmed-consistent` | pre-existing value, read at the cited line: it agrees with the corrected round-5 rule |
| R4-2-R5 | carry | `assert-picker-binding.ps1` | `implementation-plan.md:105` | `confirmed-consistent` | pre-existing value, read at the cited line: it agrees with the corrected round-5 rule |
| R4-2-R5 | carry | `assert-picker-binding.ps1` | `implementation-plan.md:221` | `confirmed-consistent` | pre-existing value, read at the cited line: it agrees with the corrected round-5 rule |
| R4-2-R5 | carry | `assert-picker-binding.ps1` | `implementation-plan.md:222` | `confirmed-consistent` | pre-existing value, read at the cited line: it agrees with the corrected round-5 rule |
| R4-2-R5 | carry | `assert-picker-binding.ps1` | `implementation-plan.md:295` | `confirmed-consistent` | pre-existing value, read at the cited line: it agrees with the corrected round-5 rule |
| R4-2-R5 | carry | `assert-picker-binding.ps1` | `implementation-plan.md:366` | `confirmed-consistent` | pre-existing value, read at the cited line: it agrees with the corrected round-5 rule |
| R4-2-R5 | carry | `assert-picker-binding.ps1` | `census-round5-corrections.ps1:67` | `confirmed-consistent` | census declaration table (the sweep's own input list), not a plan assertion |
| R4-2-R5 | carry | `assert-picker-binding.ps1` | `census-round4-corrections.ps1:82` | `confirmed-consistent` | census declaration table (the sweep's own input list), not a plan assertion |
| R4-2-R5 | carry | `assert-picker-binding.ps1` | `census-round4-corrections.ps1:152` | `confirmed-consistent` | census declaration table (the sweep's own input list), not a plan assertion |
| R4-2-R5 | carry | `assert-picker-binding.ps1` | `census-round3-corrections.ps1:72` | `confirmed-consistent` | census declaration table (the sweep's own input list), not a plan assertion |
| R4-2-R5 | carry | `assert-picker-binding.ps1` | `census-round1-corrections.ps1:43` | `confirmed-consistent` | census declaration table (the sweep's own input list), not a plan assertion |
| R4-2-R5 | carry | `assert-picker-binding.ps1` | `assert-oracle-selftests.ps1:11` | `confirmed-consistent` | pre-existing value, read at the cited line: it agrees with the corrected round-5 rule |
| R4-2-R5 | carry | `assert-picker-binding.ps1` | `assert-closeout.ps1:23` | `confirmed-consistent` | pre-existing value, read at the cited line: it agrees with the corrected round-5 rule |
| R4-2-R5 | carry | `AC-40.17` | `task.md:46` | `confirmed-consistent` | pre-existing value, read at the cited line: it agrees with the corrected round-5 rule |
| R4-2-R5 | carry | `AC-40.17` | `named-sets.json:279` | `confirmed-consistent` | pre-existing value, read at the cited line: it agrees with the corrected round-5 rule |
| R4-2-R5 | carry | `AC-40.17` | `implementation-plan.md:221` | `confirmed-consistent` | pre-existing value, read at the cited line: it agrees with the corrected round-5 rule |
| R4-2-R5 | carry | `AC-40.17` | `implementation-plan.md:366` | `confirmed-consistent` | pre-existing value, read at the cited line: it agrees with the corrected round-5 rule |
| R4-2-R5 | carry | `AC-40.17` | `census-round5-corrections.ps1:68` | `confirmed-consistent` | census declaration table (the sweep's own input list), not a plan assertion |
| R4-2-R5 | carry | `AC-40.17` | `census-round4-corrections.ps1:88` | `confirmed-consistent` | census declaration table (the sweep's own input list), not a plan assertion |
| R4-2-R5 | carry | `AC-40.17` | `census-round3-corrections.ps1:73` | `confirmed-consistent` | census declaration table (the sweep's own input list), not a plan assertion |
| R4-2-R5 | carry | `AC-40.17` | `census-round1-corrections.ps1:45` | `confirmed-consistent` | census declaration table (the sweep's own input list), not a plan assertion |
| R4-2-R5 | carry | `AC-40.17` | `assert-picker-binding.ps1:1` | `confirmed-consistent` | pre-existing value, read at the cited line: it agrees with the corrected round-5 rule |
| R4-2-R5 | carry | `AC-40.20` | `task.md:44` | `confirmed-consistent` | pre-existing value, read at the cited line: it agrees with the corrected round-5 rule |
| R4-2-R5 | carry | `AC-40.20` | `task.md:46` | `confirmed-consistent` | pre-existing value, read at the cited line: it agrees with the corrected round-5 rule |
| R4-2-R5 | carry | `AC-40.20` | `named-sets.json:282` | `confirmed-consistent` | pre-existing value, read at the cited line: it agrees with the corrected round-5 rule |
| R4-2-R5 | carry | `AC-40.20` | `implementation-plan.md:221` | `confirmed-consistent` | pre-existing value, read at the cited line: it agrees with the corrected round-5 rule |
| R4-2-R5 | carry | `AC-40.20` | `implementation-plan.md:222` | `confirmed-consistent` | pre-existing value, read at the cited line: it agrees with the corrected round-5 rule |
| R4-2-R5 | carry | `AC-40.20` | `implementation-plan.md:273` | `confirmed-consistent` | pre-existing value, read at the cited line: it agrees with the corrected round-5 rule |
| R4-2-R5 | carry | `AC-40.20` | `implementation-plan.md:277` | `confirmed-consistent` | pre-existing value, read at the cited line: it agrees with the corrected round-5 rule |
| R4-2-R5 | carry | `AC-40.20` | `implementation-plan.md:365` | `confirmed-consistent` | pre-existing value, read at the cited line: it agrees with the corrected round-5 rule |
| R4-2-R5 | carry | `AC-40.20` | `implementation-plan.md:366` | `confirmed-consistent` | pre-existing value, read at the cited line: it agrees with the corrected round-5 rule |
| R4-2-R5 | carry | `AC-40.20` | `census-round5-corrections.ps1:69` | `confirmed-consistent` | census declaration table (the sweep's own input list), not a plan assertion |
| R4-2-R5 | carry | `AC-40.20` | `census-round4-corrections.ps1:81` | `confirmed-consistent` | census declaration table (the sweep's own input list), not a plan assertion |
| R4-2-R5 | carry | `AC-40.20` | `assert-picker-binding.ps1:2` | `confirmed-consistent` | pre-existing value, read at the cited line: it agrees with the corrected round-5 rule |
| R4-3-R5 | new | `SCRIPT_SEGMENT_SPLIT_PATTERN` | `named-sets.json:25` | `updated` | the value did not exist in this folder before the round-5 pass, so this line was written by that pass |
| R4-3-R5 | new | `SCRIPT_SEGMENT_SPLIT_PATTERN` | `census-round5-corrections.ps1:72` | `confirmed-consistent` | census declaration table (the sweep's own input list), not a plan assertion |
| R4-3-R5 | new | `SCRIPT_SEGMENT_SPLIT_PATTERN` | `assert-e2e-wired.ps1:45` | `updated` | the value did not exist in this folder before the round-5 pass, so this line was written by that pass |
| R4-3-R5 | new | `SCRIPT_ALLOWED_PREFIXES` | `named-sets.json:26` | `updated` | the value did not exist in this folder before the round-5 pass, so this line was written by that pass |
| R4-3-R5 | new | `SCRIPT_ALLOWED_PREFIXES` | `implementation-plan.md:231` | `updated` | the value did not exist in this folder before the round-5 pass, so this line was written by that pass |
| R4-3-R5 | new | `SCRIPT_ALLOWED_PREFIXES` | `census-round5-corrections.ps1:73` | `confirmed-consistent` | census declaration table (the sweep's own input list), not a plan assertion |
| R4-3-R5 | new | `SCRIPT_ALLOWED_PREFIXES` | `assert-e2e-wired.ps1:46` | `updated` | the value did not exist in this folder before the round-5 pass, so this line was written by that pass |
| R4-3-R5 | new | `SCRIPT_HOLLOW_HEADS` | `named-sets.json:30` | `updated` | the value did not exist in this folder before the round-5 pass, so this line was written by that pass |
| R4-3-R5 | new | `SCRIPT_HOLLOW_HEADS` | `implementation-plan.md:231` | `updated` | the value did not exist in this folder before the round-5 pass, so this line was written by that pass |
| R4-3-R5 | new | `SCRIPT_HOLLOW_HEADS` | `census-round5-corrections.ps1:74` | `confirmed-consistent` | census declaration table (the sweep's own input list), not a plan assertion |
| R4-3-R5 | new | `SCRIPT_HOLLOW_HEADS` | `assert-e2e-wired.ps1:47` | `updated` | the value did not exist in this folder before the round-5 pass, so this line was written by that pass |
| R4-3-R5 | new | `Test-ScriptSegment` | `census-round5-corrections.ps1:75` | `confirmed-consistent` | census declaration table (the sweep's own input list), not a plan assertion |
| R4-3-R5 | new | `Test-ScriptSegment` | `assert-e2e-wired.ps1:121` | `updated` | the value did not exist in this folder before the round-5 pass, so this line was written by that pass |
| R4-3-R5 | new | `Test-ScriptSegment` | `assert-e2e-wired.ps1:341` | `updated` | the value did not exist in this folder before the round-5 pass, so this line was written by that pass |
| R4-3-R5 | new | `Test-ScriptSegment` | `assert-e2e-wired.ps1:342` | `updated` | the value did not exist in this folder before the round-5 pass, so this line was written by that pass |
| R4-3-R5 | new | `Test-ScriptSegment` | `assert-e2e-wired.ps1:345` | `updated` | the value did not exist in this folder before the round-5 pass, so this line was written by that pass |
| R4-3-R5 | new | `Test-ScriptSegment` | `assert-e2e-wired.ps1:348` | `updated` | the value did not exist in this folder before the round-5 pass, so this line was written by that pass |
| R4-3-R5 | new | `Test-ScriptSegment` | `assert-e2e-wired.ps1:352` | `updated` | the value did not exist in this folder before the round-5 pass, so this line was written by that pass |
| R4-3-R5 | new | `Test-ScriptSegment` | `assert-e2e-wired.ps1:356` | `updated` | the value did not exist in this folder before the round-5 pass, so this line was written by that pass |
| R4-3-R5 | new | `Test-ScriptSegment` | `assert-e2e-wired.ps1:361` | `updated` | the value did not exist in this folder before the round-5 pass, so this line was written by that pass |
| R4-3-R5 | new | `Test-ScriptSegment` | `assert-e2e-wired.ps1:474` | `updated` | the value did not exist in this folder before the round-5 pass, so this line was written by that pass |
| R4-3-R5 | new | `Test-ScriptSegment` | `assert-e2e-wired.ps1:476` | `updated` | the value did not exist in this folder before the round-5 pass, so this line was written by that pass |
| R4-3-R5 | new | `Test-ScriptSegment` | `assert-e2e-wired.ps1:478` | `updated` | the value did not exist in this folder before the round-5 pass, so this line was written by that pass |
| R4-3-R5 | new | `RUN_STAMPS` | `named-sets.json:42` | `updated` | the value did not exist in this folder before the round-5 pass, so this line was written by that pass |
| R4-3-R5 | new | `RUN_STAMPS` | `implementation-plan.md:230` | `updated` | the value did not exist in this folder before the round-5 pass, so this line was written by that pass |
| R4-3-R5 | new | `RUN_STAMPS` | `implementation-plan.md:297` | `updated` | the value did not exist in this folder before the round-5 pass, so this line was written by that pass |
| R4-3-R5 | new | `RUN_STAMPS` | `census-round5-corrections.ps1:76` | `confirmed-consistent` | census declaration table (the sweep's own input list), not a plan assertion |
| R4-3-R5 | new | `RUN_STAMPS` | `assert-smoke-disposition.ps1:48` | `updated` | the value did not exist in this folder before the round-5 pass, so this line was written by that pass |
| R4-3-R5 | new | `RUN_STAMPS` | `assert-e2e-wired.ps1:55` | `updated` | the value did not exist in this folder before the round-5 pass, so this line was written by that pass |
| R4-3-R5 | new | `RUN_STAMPS` | `arm-run.ps1:5` | `updated` | the value did not exist in this folder before the round-5 pass, so this line was written by that pass |
| R4-3-R5 | new | `RUN_STAMPS` | `arm-run.ps1:17` | `updated` | the value did not exist in this folder before the round-5 pass, so this line was written by that pass |
| R4-3-R5 | new | `RUN_STAMPS` | `arm-run.ps1:19` | `updated` | the value did not exist in this folder before the round-5 pass, so this line was written by that pass |
| R4-3-R5 | new | `arm-run.ps1` | `task.md:50` | `updated` | the value did not exist in this folder before the round-5 pass, so this line was written by that pass |
| R4-3-R5 | new | `arm-run.ps1` | `task.md:52` | `updated` | the value did not exist in this folder before the round-5 pass, so this line was written by that pass |
| R4-3-R5 | new | `arm-run.ps1` | `run-verification-plan.ps1:52` | `updated` | the value did not exist in this folder before the round-5 pass, so this line was written by that pass |
| R4-3-R5 | new | `arm-run.ps1` | `lib-disposition.ps1:96` | `updated` | the value did not exist in this folder before the round-5 pass, so this line was written by that pass |
| R4-3-R5 | new | `arm-run.ps1` | `implementation-plan.md:109` | `updated` | the value did not exist in this folder before the round-5 pass, so this line was written by that pass |
| R4-3-R5 | new | `arm-run.ps1` | `implementation-plan.md:230` | `updated` | the value did not exist in this folder before the round-5 pass, so this line was written by that pass |
| R4-3-R5 | new | `arm-run.ps1` | `implementation-plan.md:297` | `updated` | the value did not exist in this folder before the round-5 pass, so this line was written by that pass |
| R4-3-R5 | new | `arm-run.ps1` | `implementation-plan.md:368` | `updated` | the value did not exist in this folder before the round-5 pass, so this line was written by that pass |
| R4-3-R5 | new | `arm-run.ps1` | `implementation-plan.md:372` | `updated` | the value did not exist in this folder before the round-5 pass, so this line was written by that pass |
| R4-3-R5 | new | `arm-run.ps1` | `census-round5-corrections.ps1:20` | `confirmed-consistent` | census declaration table (the sweep's own input list), not a plan assertion |
| R4-3-R5 | new | `arm-run.ps1` | `census-round5-corrections.ps1:77` | `confirmed-consistent` | census declaration table (the sweep's own input list), not a plan assertion |
| R4-3-R5 | new | `arm-run.ps1` | `assert-smoke-disposition.ps1:14` | `updated` | the value did not exist in this folder before the round-5 pass, so this line was written by that pass |
| R4-3-R5 | new | `arm-run.ps1` | `assert-oracle-selftests.ps1:17` | `updated` | the value did not exist in this folder before the round-5 pass, so this line was written by that pass |
| R4-3-R5 | new | `Test-ArtifactFresh` | `lib-disposition.ps1:101` | `updated` | the value did not exist in this folder before the round-5 pass, so this line was written by that pass |
| R4-3-R5 | new | `Test-ArtifactFresh` | `implementation-plan.md:296` | `updated` | the value did not exist in this folder before the round-5 pass, so this line was written by that pass |
| R4-3-R5 | new | `Test-ArtifactFresh` | `census-round5-corrections.ps1:78` | `confirmed-consistent` | census declaration table (the sweep's own input list), not a plan assertion |
| R4-3-R5 | new | `Test-ArtifactFresh` | `assert-smoke-disposition.ps1:78` | `updated` | the value did not exist in this folder before the round-5 pass, so this line was written by that pass |
| R4-3-R5 | new | `Test-ArtifactFresh` | `assert-e2e-wired.ps1:401` | `updated` | the value did not exist in this folder before the round-5 pass, so this line was written by that pass |
| R4-3-R5 | new | `Test-ArtifactFresh` | `assert-e2e-wired.ps1:406` | `updated` | the value did not exist in this folder before the round-5 pass, so this line was written by that pass |
| R4-3-R5 | new | `Test-ArtifactFresh` | `assert-e2e-wired.ps1:439` | `updated` | the value did not exist in this folder before the round-5 pass, so this line was written by that pass |
| R4-3-R5 | new | `Test-ArtifactFresh` | `arm-run.ps1:34` | `updated` | the value did not exist in this folder before the round-5 pass, so this line was written by that pass |
| R4-3-R5 | new | `Test-ArtifactFresh` | `arm-run.ps1:39` | `updated` | the value did not exist in this folder before the round-5 pass, so this line was written by that pass |
| R4-3-R5 | new | `Test-ArtifactFresh` | `arm-run.ps1:40` | `updated` | the value did not exist in this folder before the round-5 pass, so this line was written by that pass |
| R4-3-R5 | new | `Test-ArtifactFresh` | `arm-run.ps1:44` | `updated` | the value did not exist in this folder before the round-5 pass, so this line was written by that pass |
| R4-3-R5 | new | `ARM_E2E_CAPTURE` | `run-verification-plan.ps1:20` | `updated` | the value did not exist in this folder before the round-5 pass, so this line was written by that pass |
| R4-3-R5 | new | `ARM_E2E_CAPTURE` | `run-verification-plan.ps1:52` | `updated` | the value did not exist in this folder before the round-5 pass, so this line was written by that pass |
| R4-3-R5 | new | `ARM_E2E_CAPTURE` | `census-round5-corrections.ps1:79` | `confirmed-consistent` | census declaration table (the sweep's own input list), not a plan assertion |
| R4-3-R5 | new | `RUN_ARM` | `implementation-plan.md:109` | `updated` | the value did not exist in this folder before the round-5 pass, so this line was written by that pass |
| R4-3-R5 | new | `RUN_ARM` | `census-round5-corrections.ps1:80` | `confirmed-consistent` | census declaration table (the sweep's own input list), not a plan assertion |
| R4-3-R5 | new | `RUN_ARM` | `assert-oracle-selftests.ps1:17` | `updated` | the value did not exist in this folder before the round-5 pass, so this line was written by that pass |
| R4-3-R5 | new | `RUN_ARM` | `arm-run.ps1:48` | `updated` | the value did not exist in this folder before the round-5 pass, so this line was written by that pass |
| R4-3-R5 | new | `RUN_ARM` | `arm-run.ps1:52` | `updated` | the value did not exist in this folder before the round-5 pass, so this line was written by that pass |
| R4-3-R5 | new | `arm-e2e-capture.txt` | `task.md:50` | `updated` | the value did not exist in this folder before the round-5 pass, so this line was written by that pass |
| R4-3-R5 | new | `arm-e2e-capture.txt` | `run-verification-plan.ps1:52` | `updated` | the value did not exist in this folder before the round-5 pass, so this line was written by that pass |
| R4-3-R5 | new | `arm-e2e-capture.txt` | `implementation-plan.md:372` | `updated` | the value did not exist in this folder before the round-5 pass, so this line was written by that pass |
| R4-3-R5 | new | `arm-e2e-capture.txt` | `census-round5-corrections.ps1:81` | `confirmed-consistent` | census declaration table (the sweep's own input list), not a plan assertion |
| R4-3-R5 | new | `arm-live-smoke.txt` | `task.md:52` | `updated` | the value did not exist in this folder before the round-5 pass, so this line was written by that pass |
| R4-3-R5 | new | `arm-live-smoke.txt` | `census-round5-corrections.ps1:82` | `confirmed-consistent` | census declaration table (the sweep's own input list), not a plan assertion |
| R4-3-R5 | carry | `E2E_CAPTURE_REQUIRED_SEGMENTS` | `named-sets.json:179` | `confirmed-consistent` | pre-existing value, read at the cited line: it agrees with the corrected round-5 rule |
| R4-3-R5 | carry | `E2E_CAPTURE_REQUIRED_SEGMENTS` | `implementation-plan.md:231` | `confirmed-consistent` | pre-existing value, read at the cited line: it agrees with the corrected round-5 rule |
| R4-3-R5 | carry | `E2E_CAPTURE_REQUIRED_SEGMENTS` | `census-round5-corrections.ps1:83` | `confirmed-consistent` | census declaration table (the sweep's own input list), not a plan assertion |
| R4-3-R5 | carry | `E2E_CAPTURE_REQUIRED_SEGMENTS` | `census-round4-corrections.ps1:93` | `confirmed-consistent` | census declaration table (the sweep's own input list), not a plan assertion |
| R4-3-R5 | carry | `E2E_CAPTURE_REQUIRED_SEGMENTS` | `assert-e2e-wired.ps1:32` | `confirmed-consistent` | pre-existing value, read at the cited line: it agrees with the corrected round-5 rule |
| R4-3-R5 | carry | `E2E_STUB_BUILD_REQUIRED_SEGMENT` | `named-sets.json:206` | `confirmed-consistent` | pre-existing value, read at the cited line: it agrees with the corrected round-5 rule |
| R4-3-R5 | carry | `E2E_STUB_BUILD_REQUIRED_SEGMENT` | `census-round5-corrections.ps1:84` | `confirmed-consistent` | census declaration table (the sweep's own input list), not a plan assertion |
| R4-3-R5 | carry | `E2E_STUB_BUILD_REQUIRED_SEGMENT` | `census-round4-corrections.ps1:98` | `confirmed-consistent` | census declaration table (the sweep's own input list), not a plan assertion |
| R4-3-R5 | carry | `E2E_STUB_BUILD_REQUIRED_SEGMENT` | `assert-e2e-wired.ps1:43` | `confirmed-consistent` | pre-existing value, read at the cited line: it agrees with the corrected round-5 rule |
| R4-3-R5 | carry | `PICKER_DIST_REQUIRED_SEGMENT` | `named-sets.json:22` | `confirmed-consistent` | pre-existing value, read at the cited line: it agrees with the corrected round-5 rule |
| R4-3-R5 | carry | `PICKER_DIST_REQUIRED_SEGMENT` | `census-round5-corrections.ps1:85` | `confirmed-consistent` | census declaration table (the sweep's own input list), not a plan assertion |
| R4-3-R5 | carry | `PICKER_DIST_REQUIRED_SEGMENT` | `census-round3-corrections.ps1:83` | `confirmed-consistent` | census declaration table (the sweep's own input list), not a plan assertion |
| R4-3-R5 | carry | `PICKER_DIST_REQUIRED_SEGMENT` | `assert-packaging-clean.ps1:24` | `confirmed-consistent` | pre-existing value, read at the cited line: it agrees with the corrected round-5 rule |
| R4-3-R5 | carry | `PICKER_PREP_REQUIRED_SEGMENT` | `named-sets.json:23` | `confirmed-consistent` | pre-existing value, read at the cited line: it agrees with the corrected round-5 rule |
| R4-3-R5 | carry | `PICKER_PREP_REQUIRED_SEGMENT` | `census-round5-corrections.ps1:86` | `confirmed-consistent` | census declaration table (the sweep's own input list), not a plan assertion |
| R4-3-R5 | carry | `PICKER_PREP_REQUIRED_SEGMENT` | `census-round3-corrections.ps1:84` | `confirmed-consistent` | census declaration table (the sweep's own input list), not a plan assertion |
| R4-3-R5 | carry | `PICKER_PREP_REQUIRED_SEGMENT` | `assert-packaging-clean.ps1:25` | `confirmed-consistent` | pre-existing value, read at the cited line: it agrees with the corrected round-5 rule |
| R4-3-R5 | carry | `E2E_EXECUTED_RECEIPT` | `run-verification-plan.ps1:54` | `confirmed-consistent` | pre-existing value, read at the cited line: it agrees with the corrected round-5 rule |
| R4-3-R5 | carry | `E2E_EXECUTED_RECEIPT` | `named-sets.json:186` | `confirmed-consistent` | pre-existing value, read at the cited line: it agrees with the corrected round-5 rule |
| R4-3-R5 | carry | `E2E_EXECUTED_RECEIPT` | `implementation-plan.md:230` | `confirmed-consistent` | pre-existing value, read at the cited line: it agrees with the corrected round-5 rule |
| R4-3-R5 | carry | `E2E_EXECUTED_RECEIPT` | `implementation-plan.md:372` | `confirmed-consistent` | pre-existing value, read at the cited line: it agrees with the corrected round-5 rule |
| R4-3-R5 | carry | `E2E_EXECUTED_RECEIPT` | `census-round5-corrections.ps1:87` | `confirmed-consistent` | census declaration table (the sweep's own input list), not a plan assertion |
| R4-3-R5 | carry | `E2E_EXECUTED_RECEIPT` | `census-round4-corrections.ps1:95` | `confirmed-consistent` | census declaration table (the sweep's own input list), not a plan assertion |
| R4-3-R5 | carry | `E2E_EXECUTED_RECEIPT` | `assert-e2e-wired.ps1:33` | `confirmed-consistent` | pre-existing value, read at the cited line: it agrees with the corrected round-5 rule |
| R4-3-R5 | carry | `E2E_EXECUTED_RECEIPT` | `assert-e2e-wired.ps1:440` | `confirmed-consistent` | pre-existing value, read at the cited line: it agrees with the corrected round-5 rule |
| R4-3-R5 | carry | `PLAYWRIGHT_JSON_OUTPUT_NAME` | `task.md:50` | `confirmed-consistent` | pre-existing value, read at the cited line: it agrees with the corrected round-5 rule |
| R4-3-R5 | carry | `PLAYWRIGHT_JSON_OUTPUT_NAME` | `named-sets.json:185` | `confirmed-consistent` | pre-existing value, read at the cited line: it agrees with the corrected round-5 rule |
| R4-3-R5 | carry | `PLAYWRIGHT_JSON_OUTPUT_NAME` | `implementation-plan.md:230` | `confirmed-consistent` | pre-existing value, read at the cited line: it agrees with the corrected round-5 rule |
| R4-3-R5 | carry | `PLAYWRIGHT_JSON_OUTPUT_NAME` | `implementation-plan.md:374` | `confirmed-consistent` | pre-existing value, read at the cited line: it agrees with the corrected round-5 rule |
| R4-3-R5 | carry | `PLAYWRIGHT_JSON_OUTPUT_NAME` | `census-round5-corrections.ps1:88` | `confirmed-consistent` | census declaration table (the sweep's own input list), not a plan assertion |
| R4-3-R5 | carry | `PLAYWRIGHT_JSON_OUTPUT_NAME` | `census-round4-corrections.ps1:102` | `confirmed-consistent` | census declaration table (the sweep's own input list), not a plan assertion |
| R4-3-R5 | carry | `assert-e2e-wired.ps1` | `task.md:50` | `confirmed-consistent` | pre-existing value, read at the cited line: it agrees with the corrected round-5 rule |
| R4-3-R5 | carry | `assert-e2e-wired.ps1` | `task.md:87` | `confirmed-consistent` | pre-existing value, read at the cited line: it agrees with the corrected round-5 rule |
| R4-3-R5 | carry | `assert-e2e-wired.ps1` | `run-verification-plan.ps1:51` | `confirmed-consistent` | pre-existing value, read at the cited line: it agrees with the corrected round-5 rule |
| R4-3-R5 | carry | `assert-e2e-wired.ps1` | `run-verification-plan.ps1:55` | `confirmed-consistent` | pre-existing value, read at the cited line: it agrees with the corrected round-5 rule |
| R4-3-R5 | carry | `assert-e2e-wired.ps1` | `implementation-plan.md:107` | `confirmed-consistent` | pre-existing value, read at the cited line: it agrees with the corrected round-5 rule |
| R4-3-R5 | carry | `assert-e2e-wired.ps1` | `implementation-plan.md:229` | `confirmed-consistent` | pre-existing value, read at the cited line: it agrees with the corrected round-5 rule |
| R4-3-R5 | carry | `assert-e2e-wired.ps1` | `implementation-plan.md:230` | `confirmed-consistent` | pre-existing value, read at the cited line: it agrees with the corrected round-5 rule |
| R4-3-R5 | carry | `assert-e2e-wired.ps1` | `implementation-plan.md:231` | `confirmed-consistent` | pre-existing value, read at the cited line: it agrees with the corrected round-5 rule |
| R4-3-R5 | carry | `assert-e2e-wired.ps1` | `implementation-plan.md:295` | `confirmed-consistent` | pre-existing value, read at the cited line: it agrees with the corrected round-5 rule |
| R4-3-R5 | carry | `assert-e2e-wired.ps1` | `implementation-plan.md:371` | `confirmed-consistent` | pre-existing value, read at the cited line: it agrees with the corrected round-5 rule |
| R4-3-R5 | carry | `assert-e2e-wired.ps1` | `implementation-plan.md:375` | `confirmed-consistent` | pre-existing value, read at the cited line: it agrees with the corrected round-5 rule |
| R4-3-R5 | carry | `assert-e2e-wired.ps1` | `census-round5-corrections.ps1:89` | `confirmed-consistent` | census declaration table (the sweep's own input list), not a plan assertion |
| R4-3-R5 | carry | `assert-e2e-wired.ps1` | `census-round4-corrections.ps1:112` | `confirmed-consistent` | census declaration table (the sweep's own input list), not a plan assertion |
| R4-3-R5 | carry | `assert-e2e-wired.ps1` | `census-round4-corrections.ps1:153` | `confirmed-consistent` | census declaration table (the sweep's own input list), not a plan assertion |
| R4-3-R5 | carry | `assert-e2e-wired.ps1` | `census-round3-corrections.ps1:94` | `confirmed-consistent` | census declaration table (the sweep's own input list), not a plan assertion |
| R4-3-R5 | carry | `assert-e2e-wired.ps1` | `assert-oracle-selftests.ps1:13` | `confirmed-consistent` | pre-existing value, read at the cited line: it agrees with the corrected round-5 rule |
| R4-3-R5 | carry | `assert-e2e-wired.ps1` | `assert-closeout.ps1:25` | `confirmed-consistent` | pre-existing value, read at the cited line: it agrees with the corrected round-5 rule |
| R4-3-R5 | carry | `assert-e2e-wired.ps1` | `assert-closeout.ps1:28` | `confirmed-consistent` | pre-existing value, read at the cited line: it agrees with the corrected round-5 rule |
| R4-3-R5 | carry | `AC-40.18` | `task.md:48` | `confirmed-consistent` | pre-existing value, read at the cited line: it agrees with the corrected round-5 rule |
| R4-3-R5 | carry | `AC-40.18` | `task.md:50` | `confirmed-consistent` | pre-existing value, read at the cited line: it agrees with the corrected round-5 rule |
| R4-3-R5 | carry | `AC-40.18` | `named-sets.json:216` | `confirmed-consistent` | pre-existing value, read at the cited line: it agrees with the corrected round-5 rule |
| R4-3-R5 | carry | `AC-40.18` | `named-sets.json:280` | `confirmed-consistent` | pre-existing value, read at the cited line: it agrees with the corrected round-5 rule |
| R4-3-R5 | carry | `AC-40.18` | `implementation-plan.md:229` | `confirmed-consistent` | pre-existing value, read at the cited line: it agrees with the corrected round-5 rule |
| R4-3-R5 | carry | `AC-40.18` | `implementation-plan.md:230` | `confirmed-consistent` | pre-existing value, read at the cited line: it agrees with the corrected round-5 rule |
| R4-3-R5 | carry | `AC-40.18` | `implementation-plan.md:231` | `confirmed-consistent` | pre-existing value, read at the cited line: it agrees with the corrected round-5 rule |
| R4-3-R5 | carry | `AC-40.18` | `implementation-plan.md:286` | `confirmed-consistent` | pre-existing value, read at the cited line: it agrees with the corrected round-5 rule |
| R4-3-R5 | carry | `AC-40.18` | `implementation-plan.md:290` | `confirmed-consistent` | pre-existing value, read at the cited line: it agrees with the corrected round-5 rule |
| R4-3-R5 | carry | `AC-40.18` | `implementation-plan.md:374` | `confirmed-consistent` | pre-existing value, read at the cited line: it agrees with the corrected round-5 rule |
| R4-3-R5 | carry | `AC-40.18` | `implementation-plan.md:375` | `confirmed-consistent` | pre-existing value, read at the cited line: it agrees with the corrected round-5 rule |
| R4-3-R5 | carry | `AC-40.18` | `census-round5-corrections.ps1:90` | `confirmed-consistent` | census declaration table (the sweep's own input list), not a plan assertion |
| R4-3-R5 | carry | `AC-40.18` | `census-round4-corrections.ps1:120` | `confirmed-consistent` | census declaration table (the sweep's own input list), not a plan assertion |
| R4-3-R5 | carry | `AC-40.18` | `census-round3-corrections.ps1:96` | `confirmed-consistent` | census declaration table (the sweep's own input list), not a plan assertion |
| R4-3-R5 | carry | `AC-40.18` | `assert-e2e-wired.ps1:1` | `confirmed-consistent` | pre-existing value, read at the cited line: it agrees with the corrected round-5 rule |
| R4-3-R5 | carry | `AC-40.18` | `assert-e2e-wired.ps1:256` | `confirmed-consistent` | pre-existing value, read at the cited line: it agrees with the corrected round-5 rule |
| R4-3-R5 | carry | `AC-40.18` | `assert-e2e-wired.ps1:273` | `confirmed-consistent` | pre-existing value, read at the cited line: it agrees with the corrected round-5 rule |
| R4-4-R5 | new | `SMOKE_RECEIPT_FILE` | `named-sets.json:229` | `updated` | the value did not exist in this folder before the round-5 pass, so this line was written by that pass |
| R4-4-R5 | new | `SMOKE_RECEIPT_FILE` | `implementation-plan.md:231` | `updated` | the value did not exist in this folder before the round-5 pass, so this line was written by that pass |
| R4-4-R5 | new | `SMOKE_RECEIPT_FILE` | `implementation-plan.md:376` | `updated` | the value did not exist in this folder before the round-5 pass, so this line was written by that pass |
| R4-4-R5 | new | `SMOKE_RECEIPT_FILE` | `census-round5-corrections.ps1:93` | `confirmed-consistent` | census declaration table (the sweep's own input list), not a plan assertion |
| R4-4-R5 | new | `SMOKE_RECEIPT_FILE` | `assert-smoke-disposition.ps1:13` | `updated` | the value did not exist in this folder before the round-5 pass, so this line was written by that pass |
| R4-4-R5 | new | `SMOKE_RECEIPT_FILE` | `assert-smoke-disposition.ps1:31` | `updated` | the value did not exist in this folder before the round-5 pass, so this line was written by that pass |
| R4-4-R5 | new | `SMOKE_RECEIPT_FILE` | `assert-smoke-disposition.ps1:45` | `updated` | the value did not exist in this folder before the round-5 pass, so this line was written by that pass |
| R4-4-R5 | new | `SMOKE_RECEIPT_REQUIRED_MARKERS` | `named-sets.json:230` | `updated` | the value did not exist in this folder before the round-5 pass, so this line was written by that pass |
| R4-4-R5 | new | `SMOKE_RECEIPT_REQUIRED_MARKERS` | `implementation-plan.md:231` | `updated` | the value did not exist in this folder before the round-5 pass, so this line was written by that pass |
| R4-4-R5 | new | `SMOKE_RECEIPT_REQUIRED_MARKERS` | `census-round5-corrections.ps1:94` | `confirmed-consistent` | census declaration table (the sweep's own input list), not a plan assertion |
| R4-4-R5 | new | `SMOKE_RECEIPT_REQUIRED_MARKERS` | `assert-smoke-disposition.ps1:15` | `updated` | the value did not exist in this folder before the round-5 pass, so this line was written by that pass |
| R4-4-R5 | new | `SMOKE_RECEIPT_REQUIRED_MARKERS` | `assert-smoke-disposition.ps1:46` | `updated` | the value did not exist in this folder before the round-5 pass, so this line was written by that pass |
| R4-4-R5 | new | `SMOKE_LATENCY_RECEIPT_KEY` | `named-sets.json:233` | `updated` | the value did not exist in this folder before the round-5 pass, so this line was written by that pass |
| R4-4-R5 | new | `SMOKE_LATENCY_RECEIPT_KEY` | `census-round5-corrections.ps1:95` | `confirmed-consistent` | census declaration table (the sweep's own input list), not a plan assertion |
| R4-4-R5 | new | `SMOKE_LATENCY_RECEIPT_KEY` | `assert-smoke-disposition.ps1:47` | `updated` | the value did not exist in this folder before the round-5 pass, so this line was written by that pass |
| R4-4-R5 | new | `SMOKE_ERROR_SIGNATURE_CLASSES` | `named-sets.json:239` | `updated` | the value did not exist in this folder before the round-5 pass, so this line was written by that pass |
| R4-4-R5 | new | `SMOKE_ERROR_SIGNATURE_CLASSES` | `census-round5-corrections.ps1:96` | `confirmed-consistent` | census declaration table (the sweep's own input list), not a plan assertion |
| R4-4-R5 | new | `SMOKE_ERROR_SIGNATURE_CLASSES` | `assert-smoke-disposition.ps1:41` | `updated` | the value did not exist in this folder before the round-5 pass, so this line was written by that pass |
| R4-4-R5 | new | `SMOKE_ERROR_SIGNATURE_CLASSES` | `assert-e2e-wired.ps1:52` | `updated` | the value did not exist in this folder before the round-5 pass, so this line was written by that pass |
| R4-4-R5 | new | `ERROR_SIGNATURE` | `task.md:50` | `updated` | the value did not exist in this folder before the round-5 pass, so this line was written by that pass |
| R4-4-R5 | new | `ERROR_SIGNATURE` | `task.md:52` | `updated` | the value did not exist in this folder before the round-5 pass, so this line was written by that pass |
| R4-4-R5 | new | `ERROR_SIGNATURE` | `named-sets.json:194` | `updated` | the value did not exist in this folder before the round-5 pass, so this line was written by that pass |
| R4-4-R5 | new | `ERROR_SIGNATURE` | `named-sets.json:227` | `updated` | the value did not exist in this folder before the round-5 pass, so this line was written by that pass |
| R4-4-R5 | new | `ERROR_SIGNATURE` | `named-sets.json:239` | `updated` | the value did not exist in this folder before the round-5 pass, so this line was written by that pass |
| R4-4-R5 | new | `ERROR_SIGNATURE` | `lib-disposition.ps1:84` | `updated` | the value did not exist in this folder before the round-5 pass, so this line was written by that pass |
| R4-4-R5 | new | `ERROR_SIGNATURE` | `lib-disposition.ps1:86` | `updated` | the value did not exist in this folder before the round-5 pass, so this line was written by that pass |
| R4-4-R5 | new | `ERROR_SIGNATURE` | `lib-disposition.ps1:89` | `updated` | the value did not exist in this folder before the round-5 pass, so this line was written by that pass |
| R4-4-R5 | new | `ERROR_SIGNATURE` | `implementation-plan.md:108` | `updated` | the value did not exist in this folder before the round-5 pass, so this line was written by that pass |
| R4-4-R5 | new | `ERROR_SIGNATURE` | `implementation-plan.md:231` | `updated` | the value did not exist in this folder before the round-5 pass, so this line was written by that pass |
| R4-4-R5 | new | `ERROR_SIGNATURE` | `implementation-plan.md:296` | `updated` | the value did not exist in this folder before the round-5 pass, so this line was written by that pass |
| R4-4-R5 | new | `ERROR_SIGNATURE` | `implementation-plan.md:374` | `updated` | the value did not exist in this folder before the round-5 pass, so this line was written by that pass |
| R4-4-R5 | new | `ERROR_SIGNATURE` | `implementation-plan.md:375` | `updated` | the value did not exist in this folder before the round-5 pass, so this line was written by that pass |
| R4-4-R5 | new | `ERROR_SIGNATURE` | `census-round5-corrections.ps1:96` | `confirmed-consistent` | census declaration table (the sweep's own input list), not a plan assertion |
| R4-4-R5 | new | `ERROR_SIGNATURE` | `census-round5-corrections.ps1:97` | `confirmed-consistent` | census declaration table (the sweep's own input list), not a plan assertion |
| R4-4-R5 | new | `ERROR_SIGNATURE` | `assert-smoke-disposition.ps1:19` | `updated` | the value did not exist in this folder before the round-5 pass, so this line was written by that pass |
| R4-4-R5 | new | `ERROR_SIGNATURE` | `assert-smoke-disposition.ps1:29` | `updated` | the value did not exist in this folder before the round-5 pass, so this line was written by that pass |
| R4-4-R5 | new | `ERROR_SIGNATURE` | `assert-smoke-disposition.ps1:41` | `updated` | the value did not exist in this folder before the round-5 pass, so this line was written by that pass |
| R4-4-R5 | new | `ERROR_SIGNATURE` | `assert-smoke-disposition.ps1:137` | `updated` | the value did not exist in this folder before the round-5 pass, so this line was written by that pass |
| R4-4-R5 | new | `ERROR_SIGNATURE` | `assert-smoke-disposition.ps1:141` | `updated` | the value did not exist in this folder before the round-5 pass, so this line was written by that pass |
| R4-4-R5 | new | `ERROR_SIGNATURE` | `assert-smoke-disposition.ps1:146` | `updated` | the value did not exist in this folder before the round-5 pass, so this line was written by that pass |
| R4-4-R5 | new | `ERROR_SIGNATURE` | `assert-smoke-disposition.ps1:150` | `updated` | the value did not exist in this folder before the round-5 pass, so this line was written by that pass |
| R4-4-R5 | new | `ERROR_SIGNATURE` | `assert-smoke-disposition.ps1:154` | `updated` | the value did not exist in this folder before the round-5 pass, so this line was written by that pass |
| R4-4-R5 | new | `ERROR_SIGNATURE` | `assert-smoke-disposition.ps1:163` | `updated` | the value did not exist in this folder before the round-5 pass, so this line was written by that pass |
| R4-4-R5 | new | `ERROR_SIGNATURE` | `assert-smoke-disposition.ps1:167` | `updated` | the value did not exist in this folder before the round-5 pass, so this line was written by that pass |
| R4-4-R5 | new | `ERROR_SIGNATURE` | `assert-smoke-disposition.ps1:171` | `updated` | the value did not exist in this folder before the round-5 pass, so this line was written by that pass |
| R4-4-R5 | new | `ERROR_SIGNATURE` | `assert-smoke-disposition.ps1:175` | `updated` | the value did not exist in this folder before the round-5 pass, so this line was written by that pass |
| R4-4-R5 | new | `ERROR_SIGNATURE` | `assert-smoke-disposition.ps1:178` | `updated` | the value did not exist in this folder before the round-5 pass, so this line was written by that pass |
| R4-4-R5 | new | `ERROR_SIGNATURE` | `assert-smoke-disposition.ps1:182` | `updated` | the value did not exist in this folder before the round-5 pass, so this line was written by that pass |
| R4-4-R5 | new | `ERROR_SIGNATURE` | `assert-smoke-disposition.ps1:189` | `updated` | the value did not exist in this folder before the round-5 pass, so this line was written by that pass |
| R4-4-R5 | new | `ERROR_SIGNATURE` | `assert-smoke-disposition.ps1:196` | `updated` | the value did not exist in this folder before the round-5 pass, so this line was written by that pass |
| R4-4-R5 | new | `ERROR_SIGNATURE` | `assert-smoke-disposition.ps1:213` | `updated` | the value did not exist in this folder before the round-5 pass, so this line was written by that pass |
| R4-4-R5 | new | `ERROR_SIGNATURE` | `assert-smoke-disposition.ps1:214` | `updated` | the value did not exist in this folder before the round-5 pass, so this line was written by that pass |
| R4-4-R5 | new | `ERROR_SIGNATURE` | `assert-smoke-disposition.ps1:217` | `updated` | the value did not exist in this folder before the round-5 pass, so this line was written by that pass |
| R4-4-R5 | new | `ERROR_SIGNATURE` | `assert-smoke-disposition.ps1:218` | `updated` | the value did not exist in this folder before the round-5 pass, so this line was written by that pass |
| R4-4-R5 | new | `ERROR_SIGNATURE` | `assert-smoke-disposition.ps1:221` | `updated` | the value did not exist in this folder before the round-5 pass, so this line was written by that pass |
| R4-4-R5 | new | `ERROR_SIGNATURE` | `assert-e2e-wired.ps1:52` | `updated` | the value did not exist in this folder before the round-5 pass, so this line was written by that pass |
| R4-4-R5 | new | `ERROR_SIGNATURE` | `assert-e2e-wired.ps1:374` | `updated` | the value did not exist in this folder before the round-5 pass, so this line was written by that pass |
| R4-4-R5 | new | `ERROR_SIGNATURE` | `assert-e2e-wired.ps1:388` | `updated` | the value did not exist in this folder before the round-5 pass, so this line was written by that pass |
| R4-4-R5 | new | `picker_startup_ms` | `task.md:52` | `updated` | the value did not exist in this folder before the round-5 pass, so this line was written by that pass |
| R4-4-R5 | new | `picker_startup_ms` | `named-sets.json:233` | `updated` | the value did not exist in this folder before the round-5 pass, so this line was written by that pass |
| R4-4-R5 | new | `picker_startup_ms` | `implementation-plan.md:108` | `updated` | the value did not exist in this folder before the round-5 pass, so this line was written by that pass |
| R4-4-R5 | new | `picker_startup_ms` | `implementation-plan.md:231` | `updated` | the value did not exist in this folder before the round-5 pass, so this line was written by that pass |
| R4-4-R5 | new | `picker_startup_ms` | `implementation-plan.md:376` | `updated` | the value did not exist in this folder before the round-5 pass, so this line was written by that pass |
| R4-4-R5 | new | `picker_startup_ms` | `census-round5-corrections.ps1:98` | `confirmed-consistent` | census declaration table (the sweep's own input list), not a plan assertion |
| R4-4-R5 | new | `picker_startup_ms` | `assert-smoke-disposition.ps1:17` | `updated` | the value did not exist in this folder before the round-5 pass, so this line was written by that pass |
| R4-4-R5 | new | `picker_startup_ms` | `assert-smoke-disposition.ps1:24` | `updated` | the value did not exist in this folder before the round-5 pass, so this line was written by that pass |
| R4-4-R5 | new | `picker_startup_ms` | `assert-smoke-disposition.ps1:120` | `updated` | the value did not exist in this folder before the round-5 pass, so this line was written by that pass |
| R4-4-R5 | new | `picker_startup_ms` | `assert-smoke-disposition.ps1:200` | `updated` | the value did not exist in this folder before the round-5 pass, so this line was written by that pass |
| R4-4-R5 | new | `picker_startup_ms` | `assert-smoke-disposition.ps1:206` | `updated` | the value did not exist in this folder before the round-5 pass, so this line was written by that pass |
| R4-4-R5 | new | `FOLLOWUP_SOURCES` | `task.md:50` | `updated` | the value did not exist in this folder before the round-5 pass, so this line was written by that pass |
| R4-4-R5 | new | `FOLLOWUP_SOURCES` | `task.md:52` | `updated` | the value did not exist in this folder before the round-5 pass, so this line was written by that pass |
| R4-4-R5 | new | `FOLLOWUP_SOURCES` | `named-sets.json:52` | `updated` | the value did not exist in this folder before the round-5 pass, so this line was written by that pass |
| R4-4-R5 | new | `FOLLOWUP_SOURCES` | `implementation-plan.md:231` | `updated` | the value did not exist in this folder before the round-5 pass, so this line was written by that pass |
| R4-4-R5 | new | `FOLLOWUP_SOURCES` | `implementation-plan.md:293` | `updated` | the value did not exist in this folder before the round-5 pass, so this line was written by that pass |
| R4-4-R5 | new | `FOLLOWUP_SOURCES` | `implementation-plan.md:296` | `updated` | the value did not exist in this folder before the round-5 pass, so this line was written by that pass |
| R4-4-R5 | new | `FOLLOWUP_SOURCES` | `implementation-plan.md:375` | `updated` | the value did not exist in this folder before the round-5 pass, so this line was written by that pass |
| R4-4-R5 | new | `FOLLOWUP_SOURCES` | `census-round5-corrections.ps1:99` | `confirmed-consistent` | census declaration table (the sweep's own input list), not a plan assertion |
| R4-4-R5 | new | `FOLLOWUP_SOURCES` | `assert-smoke-disposition.ps1:28` | `updated` | the value did not exist in this folder before the round-5 pass, so this line was written by that pass |
| R4-4-R5 | new | `FOLLOWUP_SOURCES` | `assert-smoke-disposition.ps1:43` | `updated` | the value did not exist in this folder before the round-5 pass, so this line was written by that pass |
| R4-4-R5 | new | `FOLLOWUP_SOURCES` | `assert-e2e-wired.ps1:54` | `updated` | the value did not exist in this folder before the round-5 pass, so this line was written by that pass |
| R4-4-R5 | new | `Resolve-Followup` | `lib-disposition.ps1:38` | `updated` | the value did not exist in this folder before the round-5 pass, so this line was written by that pass |
| R4-4-R5 | new | `Resolve-Followup` | `lib-disposition.ps1:73` | `updated` | the value did not exist in this folder before the round-5 pass, so this line was written by that pass |
| R4-4-R5 | new | `Resolve-Followup` | `census-round5-corrections.ps1:100` | `confirmed-consistent` | census declaration table (the sweep's own input list), not a plan assertion |
| R4-4-R5 | new | `Test-BlockedEvidence` | `lib-disposition.ps1:54` | `updated` | the value did not exist in this folder before the round-5 pass, so this line was written by that pass |
| R4-4-R5 | new | `Test-BlockedEvidence` | `implementation-plan.md:231` | `updated` | the value did not exist in this folder before the round-5 pass, so this line was written by that pass |
| R4-4-R5 | new | `Test-BlockedEvidence` | `implementation-plan.md:296` | `updated` | the value did not exist in this folder before the round-5 pass, so this line was written by that pass |
| R4-4-R5 | new | `Test-BlockedEvidence` | `census-round5-corrections.ps1:101` | `confirmed-consistent` | census declaration table (the sweep's own input list), not a plan assertion |
| R4-4-R5 | new | `Test-BlockedEvidence` | `assert-smoke-disposition.ps1:18` | `updated` | the value did not exist in this folder before the round-5 pass, so this line was written by that pass |
| R4-4-R5 | new | `Test-BlockedEvidence` | `assert-smoke-disposition.ps1:99` | `updated` | the value did not exist in this folder before the round-5 pass, so this line was written by that pass |
| R4-4-R5 | new | `Test-BlockedEvidence` | `assert-e2e-wired.ps1:376` | `updated` | the value did not exist in this folder before the round-5 pass, so this line was written by that pass |
| R4-4-R5 | new | `Test-BlockedEvidence` | `assert-e2e-wired.ps1:379` | `updated` | the value did not exist in this folder before the round-5 pass, so this line was written by that pass |
| R4-4-R5 | new | `Test-BlockedEvidence` | `assert-e2e-wired.ps1:383` | `updated` | the value did not exist in this folder before the round-5 pass, so this line was written by that pass |
| R4-4-R5 | new | `Test-BlockedEvidence` | `assert-e2e-wired.ps1:388` | `updated` | the value did not exist in this folder before the round-5 pass, so this line was written by that pass |
| R4-4-R5 | new | `Test-BlockedEvidence` | `assert-e2e-wired.ps1:392` | `updated` | the value did not exist in this folder before the round-5 pass, so this line was written by that pass |
| R4-4-R5 | new | `Test-BlockedEvidence` | `assert-e2e-wired.ps1:432` | `updated` | the value did not exist in this folder before the round-5 pass, so this line was written by that pass |
| R4-4-R5 | new | `E2E-SANDBOX-NODISPLAY` | `task.md:50` | `updated` | the value did not exist in this folder before the round-5 pass, so this line was written by that pass |
| R4-4-R5 | new | `E2E-SANDBOX-NODISPLAY` | `task.md:87` | `updated` | the value did not exist in this folder before the round-5 pass, so this line was written by that pass |
| R4-4-R5 | new | `E2E-SANDBOX-NODISPLAY` | `implementation-plan.md:293` | `updated` | the value did not exist in this folder before the round-5 pass, so this line was written by that pass |
| R4-4-R5 | new | `E2E-SANDBOX-NODISPLAY` | `census-round5-corrections.ps1:102` | `confirmed-consistent` | census declaration table (the sweep's own input list), not a plan assertion |
| R4-4-R5 | new | `E2E-SANDBOX-NODISPLAY` | `assert-smoke-disposition.ps1:126` | `updated` | the value did not exist in this folder before the round-5 pass, so this line was written by that pass |
| R4-4-R5 | new | `E2E-SANDBOX-NODISPLAY` | `assert-smoke-disposition.ps1:141` | `updated` | the value did not exist in this folder before the round-5 pass, so this line was written by that pass |
| R4-4-R5 | new | `E2E-SANDBOX-NODISPLAY` | `assert-smoke-disposition.ps1:150` | `updated` | the value did not exist in this folder before the round-5 pass, so this line was written by that pass |
| R4-4-R5 | new | `E2E-SANDBOX-NODISPLAY` | `assert-smoke-disposition.ps1:163` | `updated` | the value did not exist in this folder before the round-5 pass, so this line was written by that pass |
| R4-4-R5 | new | `E2E-SANDBOX-NODISPLAY` | `assert-smoke-disposition.ps1:167` | `updated` | the value did not exist in this folder before the round-5 pass, so this line was written by that pass |
| R4-4-R5 | new | `E2E-SANDBOX-NODISPLAY` | `assert-smoke-disposition.ps1:213` | `updated` | the value did not exist in this folder before the round-5 pass, so this line was written by that pass |
| R4-4-R5 | new | `E2E-SANDBOX-NODISPLAY` | `assert-smoke-disposition.ps1:217` | `updated` | the value did not exist in this folder before the round-5 pass, so this line was written by that pass |
| R4-4-R5 | new | `E2E-SANDBOX-NODISPLAY` | `assert-e2e-wired.ps1:372` | `updated` | the value did not exist in this folder before the round-5 pass, so this line was written by that pass |
| R4-4-R5 | new | `E2E-SANDBOX-NODISPLAY` | `assert-e2e-wired.ps1:374` | `updated` | the value did not exist in this folder before the round-5 pass, so this line was written by that pass |
| R4-4-R5 | new | `E2E-SANDBOX-NODISPLAY` | `assert-e2e-wired.ps1:383` | `updated` | the value did not exist in this folder before the round-5 pass, so this line was written by that pass |
| R4-4-R5 | carry | `SMOKE_DISPOSITION_FILE` | `named-sets.json:219` | `confirmed-consistent` | pre-existing value, read at the cited line: it agrees with the corrected round-5 rule |
| R4-4-R5 | carry | `SMOKE_DISPOSITION_FILE` | `census-round5-corrections.ps1:103` | `confirmed-consistent` | census declaration table (the sweep's own input list), not a plan assertion |
| R4-4-R5 | carry | `SMOKE_DISPOSITION_FILE` | `census-round4-corrections.ps1:134` | `confirmed-consistent` | census declaration table (the sweep's own input list), not a plan assertion |
| R4-4-R5 | carry | `SMOKE_DISPOSITION_FILE` | `census-round3-corrections.ps1:107` | `confirmed-consistent` | census declaration table (the sweep's own input list), not a plan assertion |
| R4-4-R5 | carry | `SMOKE_DISPOSITION_FILE` | `assert-smoke-disposition.ps1:22` | `confirmed-consistent` | pre-existing value, read at the cited line: it agrees with the corrected round-5 rule |
| R4-4-R5 | carry | `SMOKE_DISPOSITION_FILE` | `assert-smoke-disposition.ps1:38` | `confirmed-consistent` | pre-existing value, read at the cited line: it agrees with the corrected round-5 rule |
| R4-4-R5 | carry | `SMOKE_DISPOSITION_FILE` | `assert-smoke-disposition.ps1:232` | `confirmed-consistent` | pre-existing value, read at the cited line: it agrees with the corrected round-5 rule |
| R4-4-R5 | carry | `SMOKE_DISPOSITION_MARKERS` | `assert-smoke-disposition.ps1:39` | `confirmed-consistent` | pre-existing value, read at the cited line: it agrees with the corrected round-5 rule |
| R4-4-R5 | carry | `SMOKE_DISPOSITION_MARKERS` | `census-round5-corrections.ps1:104` | `confirmed-consistent` | census declaration table (the sweep's own input list), not a plan assertion |
| R4-4-R5 | carry | `SMOKE_DISPOSITION_MARKERS` | `named-sets.json:220` | `confirmed-consistent` | pre-existing value, read at the cited line: it agrees with the corrected round-5 rule |
| R4-4-R5 | carry | `SMOKE_BLOCKED_CLASSES` | `assert-e2e-wired.ps1:51` | `confirmed-consistent` | pre-existing value, read at the cited line: it agrees with the corrected round-5 rule |
| R4-4-R5 | carry | `SMOKE_BLOCKED_CLASSES` | `assert-smoke-disposition.ps1:27` | `confirmed-consistent` | pre-existing value, read at the cited line: it agrees with the corrected round-5 rule |
| R4-4-R5 | carry | `SMOKE_BLOCKED_CLASSES` | `assert-smoke-disposition.ps1:40` | `confirmed-consistent` | pre-existing value, read at the cited line: it agrees with the corrected round-5 rule |
| R4-4-R5 | carry | `SMOKE_BLOCKED_CLASSES` | `census-round4-corrections.ps1:123` | `confirmed-consistent` | census declaration table (the sweep's own input list), not a plan assertion |
| R4-4-R5 | carry | `SMOKE_BLOCKED_CLASSES` | `implementation-plan.md:231` | `confirmed-consistent` | pre-existing value, read at the cited line: it agrees with the corrected round-5 rule |
| R4-4-R5 | carry | `SMOKE_BLOCKED_CLASSES` | `census-round5-corrections.ps1:105` | `confirmed-consistent` | census declaration table (the sweep's own input list), not a plan assertion |
| R4-4-R5 | carry | `SMOKE_BLOCKED_CLASSES` | `named-sets.json:234` | `confirmed-consistent` | pre-existing value, read at the cited line: it agrees with the corrected round-5 rule |
| R4-4-R5 | carry | `SMOKE_BLOCKED_CLASSES` | `task.md:50` | `confirmed-consistent` | pre-existing value, read at the cited line: it agrees with the corrected round-5 rule |
| R4-4-R5 | carry | `SMOKE_FOLLOWUP_PATTERN` | `named-sets.json:243` | `confirmed-consistent` | pre-existing value, read at the cited line: it agrees with the corrected round-5 rule |
| R4-4-R5 | carry | `SMOKE_FOLLOWUP_PATTERN` | `implementation-plan.md:231` | `confirmed-consistent` | pre-existing value, read at the cited line: it agrees with the corrected round-5 rule |
| R4-4-R5 | carry | `SMOKE_FOLLOWUP_PATTERN` | `census-round5-corrections.ps1:106` | `confirmed-consistent` | census declaration table (the sweep's own input list), not a plan assertion |
| R4-4-R5 | carry | `SMOKE_FOLLOWUP_PATTERN` | `census-round4-corrections.ps1:124` | `confirmed-consistent` | census declaration table (the sweep's own input list), not a plan assertion |
| R4-4-R5 | carry | `SMOKE_FOLLOWUP_PATTERN` | `assert-smoke-disposition.ps1:42` | `confirmed-consistent` | pre-existing value, read at the cited line: it agrees with the corrected round-5 rule |
| R4-4-R5 | carry | `SMOKE_FOLLOWUP_PATTERN` | `assert-e2e-wired.ps1:53` | `confirmed-consistent` | pre-existing value, read at the cited line: it agrees with the corrected round-5 rule |
| R4-4-R5 | carry | `SMOKE_LATENCY_KEY` | `named-sets.json:244` | `confirmed-consistent` | pre-existing value, read at the cited line: it agrees with the corrected round-5 rule |
| R4-4-R5 | carry | `SMOKE_LATENCY_KEY` | `census-round5-corrections.ps1:107` | `confirmed-consistent` | census declaration table (the sweep's own input list), not a plan assertion |
| R4-4-R5 | carry | `SMOKE_LATENCY_KEY` | `census-round4-corrections.ps1:125` | `confirmed-consistent` | census declaration table (the sweep's own input list), not a plan assertion |
| R4-4-R5 | carry | `SMOKE_LATENCY_KEY` | `assert-smoke-disposition.ps1:44` | `confirmed-consistent` | pre-existing value, read at the cited line: it agrees with the corrected round-5 rule |
| R4-4-R5 | carry | `LATENCY_MS` | `task.md:52` | `confirmed-consistent` | pre-existing value, read at the cited line: it agrees with the corrected round-5 rule |
| R4-4-R5 | carry | `LATENCY_MS` | `named-sets.json:221` | `confirmed-consistent` | pre-existing value, read at the cited line: it agrees with the corrected round-5 rule |
| R4-4-R5 | carry | `LATENCY_MS` | `named-sets.json:244` | `confirmed-consistent` | pre-existing value, read at the cited line: it agrees with the corrected round-5 rule |
| R4-4-R5 | carry | `LATENCY_MS` | `implementation-plan.md:231` | `confirmed-consistent` | pre-existing value, read at the cited line: it agrees with the corrected round-5 rule |
| R4-4-R5 | carry | `LATENCY_MS` | `implementation-plan.md:307` | `confirmed-consistent` | pre-existing value, read at the cited line: it agrees with the corrected round-5 rule |
| R4-4-R5 | carry | `LATENCY_MS` | `implementation-plan.md:376` | `confirmed-consistent` | pre-existing value, read at the cited line: it agrees with the corrected round-5 rule |
| R4-4-R5 | carry | `LATENCY_MS` | `census-round5-corrections.ps1:108` | `confirmed-consistent` | census declaration table (the sweep's own input list), not a plan assertion |
| R4-4-R5 | carry | `LATENCY_MS` | `census-round4-corrections.ps1:136` | `confirmed-consistent` | census declaration table (the sweep's own input list), not a plan assertion |
| R4-4-R5 | carry | `LATENCY_MS` | `census-round3-corrections.ps1:108` | `confirmed-consistent` | census declaration table (the sweep's own input list), not a plan assertion |
| R4-4-R5 | carry | `LATENCY_MS` | `assert-smoke-disposition.ps1:9` | `confirmed-consistent` | pre-existing value, read at the cited line: it agrees with the corrected round-5 rule |
| R4-4-R5 | carry | `LATENCY_MS` | `assert-smoke-disposition.ps1:23` | `confirmed-consistent` | pre-existing value, read at the cited line: it agrees with the corrected round-5 rule |
| R4-4-R5 | carry | `LATENCY_MS` | `assert-smoke-disposition.ps1:137` | `confirmed-consistent` | pre-existing value, read at the cited line: it agrees with the corrected round-5 rule |
| R4-4-R5 | carry | `LATENCY_MS` | `assert-smoke-disposition.ps1:141` | `confirmed-consistent` | pre-existing value, read at the cited line: it agrees with the corrected round-5 rule |
| R4-4-R5 | carry | `LATENCY_MS` | `assert-smoke-disposition.ps1:146` | `confirmed-consistent` | pre-existing value, read at the cited line: it agrees with the corrected round-5 rule |
| R4-4-R5 | carry | `LATENCY_MS` | `assert-smoke-disposition.ps1:150` | `confirmed-consistent` | pre-existing value, read at the cited line: it agrees with the corrected round-5 rule |
| R4-4-R5 | carry | `LATENCY_MS` | `assert-smoke-disposition.ps1:154` | `confirmed-consistent` | pre-existing value, read at the cited line: it agrees with the corrected round-5 rule |
| R4-4-R5 | carry | `LATENCY_MS` | `assert-smoke-disposition.ps1:158` | `confirmed-consistent` | pre-existing value, read at the cited line: it agrees with the corrected round-5 rule |
| R4-4-R5 | carry | `LATENCY_MS` | `assert-smoke-disposition.ps1:163` | `confirmed-consistent` | pre-existing value, read at the cited line: it agrees with the corrected round-5 rule |
| R4-4-R5 | carry | `LATENCY_MS` | `assert-smoke-disposition.ps1:167` | `confirmed-consistent` | pre-existing value, read at the cited line: it agrees with the corrected round-5 rule |
| R4-4-R5 | carry | `LATENCY_MS` | `assert-smoke-disposition.ps1:171` | `confirmed-consistent` | pre-existing value, read at the cited line: it agrees with the corrected round-5 rule |
| R4-4-R5 | carry | `LATENCY_MS` | `assert-smoke-disposition.ps1:175` | `confirmed-consistent` | pre-existing value, read at the cited line: it agrees with the corrected round-5 rule |
| R4-4-R5 | carry | `LATENCY_MS` | `assert-smoke-disposition.ps1:178` | `confirmed-consistent` | pre-existing value, read at the cited line: it agrees with the corrected round-5 rule |
| R4-4-R5 | carry | `LATENCY_MS` | `assert-smoke-disposition.ps1:182` | `confirmed-consistent` | pre-existing value, read at the cited line: it agrees with the corrected round-5 rule |
| R4-4-R5 | carry | `LATENCY_MS` | `assert-smoke-disposition.ps1:187` | `confirmed-consistent` | pre-existing value, read at the cited line: it agrees with the corrected round-5 rule |
| R4-4-R5 | carry | `LATENCY_MS` | `assert-smoke-disposition.ps1:189` | `confirmed-consistent` | pre-existing value, read at the cited line: it agrees with the corrected round-5 rule |
| R4-4-R5 | carry | `LATENCY_MS` | `assert-smoke-disposition.ps1:196` | `confirmed-consistent` | pre-existing value, read at the cited line: it agrees with the corrected round-5 rule |
| R4-4-R5 | carry | `LATENCY_MS` | `assert-smoke-disposition.ps1:213` | `confirmed-consistent` | pre-existing value, read at the cited line: it agrees with the corrected round-5 rule |
| R4-4-R5 | carry | `LATENCY_MS` | `assert-smoke-disposition.ps1:217` | `confirmed-consistent` | pre-existing value, read at the cited line: it agrees with the corrected round-5 rule |
| R4-4-R5 | carry | `LATENCY_MS` | `assert-smoke-disposition.ps1:221` | `confirmed-consistent` | pre-existing value, read at the cited line: it agrees with the corrected round-5 rule |
| R4-4-R5 | carry | `live-smoke.txt` | `task.md:52` | `confirmed-consistent` | pre-existing value, read at the cited line: it agrees with the corrected round-5 rule |
| R4-4-R5 | carry | `live-smoke.txt` | `named-sets.json:48` | `confirmed-consistent` | pre-existing value, read at the cited line: it agrees with the corrected round-5 rule |
| R4-4-R5 | carry | `live-smoke.txt` | `named-sets.json:229` | `confirmed-consistent` | pre-existing value, read at the cited line: it agrees with the corrected round-5 rule |
| R4-4-R5 | carry | `live-smoke.txt` | `implementation-plan.md:368` | `confirmed-consistent` | pre-existing value, read at the cited line: it agrees with the corrected round-5 rule |
| R4-4-R5 | carry | `live-smoke.txt` | `census-round5-corrections.ps1:82` | `confirmed-consistent` | census declaration table (the sweep's own input list), not a plan assertion |
| R4-4-R5 | carry | `live-smoke.txt` | `census-round5-corrections.ps1:109` | `confirmed-consistent` | census declaration table (the sweep's own input list), not a plan assertion |
| R4-4-R5 | carry | `live-smoke.txt` | `census-round4-corrections.ps1:128` | `confirmed-consistent` | census declaration table (the sweep's own input list), not a plan assertion |
| R4-4-R5 | carry | `live-smoke.txt` | `assert-smoke-disposition.ps1:31` | `confirmed-consistent` | pre-existing value, read at the cited line: it agrees with the corrected round-5 rule |
| R4-4-R5 | carry | `live-smoke.txt` | `assert-smoke-disposition.ps1:109` | `confirmed-consistent` | pre-existing value, read at the cited line: it agrees with the corrected round-5 rule |
| R4-4-R5 | carry | `live-smoke.txt` | `assert-smoke-disposition.ps1:193` | `confirmed-consistent` | pre-existing value, read at the cited line: it agrees with the corrected round-5 rule |
| R4-4-R5 | carry | `assert-smoke-disposition.ps1` | `task.md:52` | `confirmed-consistent` | pre-existing value, read at the cited line: it agrees with the corrected round-5 rule |
| R4-4-R5 | carry | `assert-smoke-disposition.ps1` | `task.md:87` | `confirmed-consistent` | pre-existing value, read at the cited line: it agrees with the corrected round-5 rule |
| R4-4-R5 | carry | `assert-smoke-disposition.ps1` | `run-verification-plan.ps1:9` | `confirmed-consistent` | pre-existing value, read at the cited line: it agrees with the corrected round-5 rule |
| R4-4-R5 | carry | `assert-smoke-disposition.ps1` | `run-verification-plan.ps1:56` | `confirmed-consistent` | pre-existing value, read at the cited line: it agrees with the corrected round-5 rule |
| R4-4-R5 | carry | `assert-smoke-disposition.ps1` | `implementation-plan.md:108` | `confirmed-consistent` | pre-existing value, read at the cited line: it agrees with the corrected round-5 rule |
| R4-4-R5 | carry | `assert-smoke-disposition.ps1` | `implementation-plan.md:231` | `confirmed-consistent` | pre-existing value, read at the cited line: it agrees with the corrected round-5 rule |
| R4-4-R5 | carry | `assert-smoke-disposition.ps1` | `implementation-plan.md:295` | `confirmed-consistent` | pre-existing value, read at the cited line: it agrees with the corrected round-5 rule |
| R4-4-R5 | carry | `assert-smoke-disposition.ps1` | `implementation-plan.md:376` | `confirmed-consistent` | pre-existing value, read at the cited line: it agrees with the corrected round-5 rule |
| R4-4-R5 | carry | `assert-smoke-disposition.ps1` | `census-round5-corrections.ps1:110` | `confirmed-consistent` | census declaration table (the sweep's own input list), not a plan assertion |
| R4-4-R5 | carry | `assert-smoke-disposition.ps1` | `census-round4-corrections.ps1:132` | `confirmed-consistent` | census declaration table (the sweep's own input list), not a plan assertion |
| R4-4-R5 | carry | `assert-smoke-disposition.ps1` | `census-round3-corrections.ps1:95` | `confirmed-consistent` | census declaration table (the sweep's own input list), not a plan assertion |
| R4-4-R5 | carry | `assert-smoke-disposition.ps1` | `assert-oracle-selftests.ps1:14` | `confirmed-consistent` | pre-existing value, read at the cited line: it agrees with the corrected round-5 rule |
| R4-4-R5 | carry | `assert-smoke-disposition.ps1` | `assert-closeout.ps1:29` | `confirmed-consistent` | pre-existing value, read at the cited line: it agrees with the corrected round-5 rule |
| R4-4-R5 | carry | `AC-40.19` | `task.md:50` | `confirmed-consistent` | pre-existing value, read at the cited line: it agrees with the corrected round-5 rule |
| R4-4-R5 | carry | `AC-40.19` | `task.md:52` | `confirmed-consistent` | pre-existing value, read at the cited line: it agrees with the corrected round-5 rule |
| R4-4-R5 | carry | `AC-40.19` | `named-sets.json:281` | `confirmed-consistent` | pre-existing value, read at the cited line: it agrees with the corrected round-5 rule |
| R4-4-R5 | carry | `AC-40.19` | `implementation-plan.md:231` | `confirmed-consistent` | pre-existing value, read at the cited line: it agrees with the corrected round-5 rule |
| R4-4-R5 | carry | `AC-40.19` | `implementation-plan.md:371` | `confirmed-consistent` | pre-existing value, read at the cited line: it agrees with the corrected round-5 rule |
| R4-4-R5 | carry | `AC-40.19` | `implementation-plan.md:376` | `confirmed-consistent` | pre-existing value, read at the cited line: it agrees with the corrected round-5 rule |
| R4-4-R5 | carry | `AC-40.19` | `census-round5-corrections.ps1:111` | `confirmed-consistent` | census declaration table (the sweep's own input list), not a plan assertion |
| R4-4-R5 | carry | `AC-40.19` | `census-round4-corrections.ps1:139` | `confirmed-consistent` | census declaration table (the sweep's own input list), not a plan assertion |
| R4-4-R5 | carry | `AC-40.19` | `census-round3-corrections.ps1:97` | `confirmed-consistent` | census declaration table (the sweep's own input list), not a plan assertion |
| R4-4-R5 | carry | `AC-40.19` | `assert-smoke-disposition.ps1:1` | `confirmed-consistent` | pre-existing value, read at the cited line: it agrees with the corrected round-5 rule |
| R4-4-R5 | carry | `AC-40.19` | `assert-e2e-wired.ps1:1` | `confirmed-consistent` | pre-existing value, read at the cited line: it agrees with the corrected round-5 rule |
| R5-1 | old | `build-plan-audit.json` | `census-round5-corrections.ps1:114` | `confirmed-consistent` | census declaration table (the sweep's own input list), not a plan assertion |
| R5-1 | old | `## BUILD_PLAN.md Audit` | `census-round5-corrections.ps1:115` | `confirmed-consistent` | census declaration table (the sweep's own input list), not a plan assertion |
| R5-1 | old | `desktopCapturer\|overlay\|region-picker` | `census-round5-corrections.ps1:116` | `confirmed-consistent` | census declaration table (the sweep's own input list), not a plan assertion |
| R5-1 | old | `If zero stale matches` | `census-round5-corrections.ps1:117` | `confirmed-consistent` | census declaration table (the sweep's own input list), not a plan assertion |
| R5-1 | new | `assert-build-plan-hub.ps1` | `task.md:51` | `updated` | the value did not exist in this folder before the round-5 pass, so this line was written by that pass |
| R5-1 | new | `assert-build-plan-hub.ps1` | `run-verification-plan.ps1:50` | `updated` | the value did not exist in this folder before the round-5 pass, so this line was written by that pass |
| R5-1 | new | `assert-build-plan-hub.ps1` | `implementation-plan.md:110` | `updated` | the value did not exist in this folder before the round-5 pass, so this line was written by that pass |
| R5-1 | new | `assert-build-plan-hub.ps1` | `implementation-plan.md:235` | `updated` | the value did not exist in this folder before the round-5 pass, so this line was written by that pass |
| R5-1 | new | `assert-build-plan-hub.ps1` | `implementation-plan.md:292` | `updated` | the value did not exist in this folder before the round-5 pass, so this line was written by that pass |
| R5-1 | new | `assert-build-plan-hub.ps1` | `implementation-plan.md:295` | `updated` | the value did not exist in this folder before the round-5 pass, so this line was written by that pass |
| R5-1 | new | `assert-build-plan-hub.ps1` | `implementation-plan.md:339` | `updated` | the value did not exist in this folder before the round-5 pass, so this line was written by that pass |
| R5-1 | new | `assert-build-plan-hub.ps1` | `implementation-plan.md:370` | `updated` | the value did not exist in this folder before the round-5 pass, so this line was written by that pass |
| R5-1 | new | `assert-build-plan-hub.ps1` | `census-round5-corrections.ps1:118` | `confirmed-consistent` | census declaration table (the sweep's own input list), not a plan assertion |
| R5-1 | new | `assert-build-plan-hub.ps1` | `assert-oracle-selftests.ps1:18` | `updated` | the value did not exist in this folder before the round-5 pass, so this line was written by that pass |
| R5-1 | new | `assert-build-plan-hub.ps1` | `assert-closeout.ps1:32` | `updated` | the value did not exist in this folder before the round-5 pass, so this line was written by that pass |
| R5-1 | new | `BUILD_PLAN_HUB` | `run-verification-plan.ps1:19` | `updated` | the value did not exist in this folder before the round-5 pass, so this line was written by that pass |
| R5-1 | new | `BUILD_PLAN_HUB` | `run-verification-plan.ps1:50` | `updated` | the value did not exist in this folder before the round-5 pass, so this line was written by that pass |
| R5-1 | new | `BUILD_PLAN_HUB` | `implementation-plan.md:110` | `updated` | the value did not exist in this folder before the round-5 pass, so this line was written by that pass |
| R5-1 | new | `BUILD_PLAN_HUB` | `implementation-plan.md:235` | `updated` | the value did not exist in this folder before the round-5 pass, so this line was written by that pass |
| R5-1 | new | `BUILD_PLAN_HUB` | `census-round5-corrections.ps1:119` | `confirmed-consistent` | census declaration table (the sweep's own input list), not a plan assertion |
| R5-1 | new | `BUILD_PLAN_HUB` | `census-round5-corrections.ps1:169` | `confirmed-consistent` | census declaration table (the sweep's own input list), not a plan assertion |
| R5-1 | new | `BUILD_PLAN_HUB` | `assert-oracle-selftests.ps1:18` | `updated` | the value did not exist in this folder before the round-5 pass, so this line was written by that pass |
| R5-1 | new | `BUILD_PLAN_HUB` | `assert-closeout.ps1:32` | `updated` | the value did not exist in this folder before the round-5 pass, so this line was written by that pass |
| R5-1 | new | `BUILD_PLAN_HUB` | `assert-build-plan-hub.ps1:95` | `updated` | the value did not exist in this folder before the round-5 pass, so this line was written by that pass |
| R5-1 | new | `BUILD_PLAN_HUB` | `assert-build-plan-hub.ps1:103` | `updated` | the value did not exist in this folder before the round-5 pass, so this line was written by that pass |
| R5-1 | new | `HUB_FILE` | `named-sets.json:166` | `updated` | the value did not exist in this folder before the round-5 pass, so this line was written by that pass |
| R5-1 | new | `HUB_FILE` | `implementation-plan.md:235` | `updated` | the value did not exist in this folder before the round-5 pass, so this line was written by that pass |
| R5-1 | new | `HUB_FILE` | `implementation-plan.md:326` | `updated` | the value did not exist in this folder before the round-5 pass, so this line was written by that pass |
| R5-1 | new | `HUB_FILE` | `census-round5-corrections.ps1:120` | `confirmed-consistent` | census declaration table (the sweep's own input list), not a plan assertion |
| R5-1 | new | `HUB_FILE` | `assert-build-plan-hub.ps1:29` | `updated` | the value did not exist in this folder before the round-5 pass, so this line was written by that pass |
| R5-1 | new | `HUB_FILE` | `assert-build-plan-hub.ps1:100` | `updated` | the value did not exist in this folder before the round-5 pass, so this line was written by that pass |
| R5-1 | new | `HUB_FORBIDDEN_TOKENS` | `named-sets.json:167` | `updated` | the value did not exist in this folder before the round-5 pass, so this line was written by that pass |
| R5-1 | new | `HUB_FORBIDDEN_TOKENS` | `implementation-plan.md:235` | `updated` | the value did not exist in this folder before the round-5 pass, so this line was written by that pass |
| R5-1 | new | `HUB_FORBIDDEN_TOKENS` | `implementation-plan.md:326` | `updated` | the value did not exist in this folder before the round-5 pass, so this line was written by that pass |
| R5-1 | new | `HUB_FORBIDDEN_TOKENS` | `census-round5-corrections.ps1:121` | `confirmed-consistent` | census declaration table (the sweep's own input list), not a plan assertion |
| R5-1 | new | `HUB_FORBIDDEN_TOKENS` | `assert-build-plan-hub.ps1:11` | `updated` | the value did not exist in this folder before the round-5 pass, so this line was written by that pass |
| R5-1 | new | `HUB_FORBIDDEN_TOKENS` | `assert-build-plan-hub.ps1:30` | `updated` | the value did not exist in this folder before the round-5 pass, so this line was written by that pass |
| R5-1 | new | `HUB_REQUIRED_TOKENS` | `named-sets.json:171` | `updated` | the value did not exist in this folder before the round-5 pass, so this line was written by that pass |
| R5-1 | new | `HUB_REQUIRED_TOKENS` | `implementation-plan.md:235` | `updated` | the value did not exist in this folder before the round-5 pass, so this line was written by that pass |
| R5-1 | new | `HUB_REQUIRED_TOKENS` | `implementation-plan.md:328` | `updated` | the value did not exist in this folder before the round-5 pass, so this line was written by that pass |
| R5-1 | new | `HUB_REQUIRED_TOKENS` | `implementation-plan.md:330` | `updated` | the value did not exist in this folder before the round-5 pass, so this line was written by that pass |
| R5-1 | new | `HUB_REQUIRED_TOKENS` | `census-round5-corrections.ps1:122` | `confirmed-consistent` | census declaration table (the sweep's own input list), not a plan assertion |
| R5-1 | new | `HUB_REQUIRED_TOKENS` | `assert-build-plan-hub.ps1:14` | `updated` | the value did not exist in this folder before the round-5 pass, so this line was written by that pass |
| R5-1 | new | `HUB_REQUIRED_TOKENS` | `assert-build-plan-hub.ps1:31` | `updated` | the value did not exist in this folder before the round-5 pass, so this line was written by that pass |
| R5-1 | new | `Test-Hub` | `assert-build-plan-hub.ps1:33` | `updated` | the value did not exist in this folder before the round-5 pass, so this line was written by that pass |
| R5-1 | new | `Test-Hub` | `assert-build-plan-hub.ps1:66` | `updated` | the value did not exist in this folder before the round-5 pass, so this line was written by that pass |
| R5-1 | new | `Test-Hub` | `assert-build-plan-hub.ps1:70` | `updated` | the value did not exist in this folder before the round-5 pass, so this line was written by that pass |
| R5-1 | new | `Test-Hub` | `assert-build-plan-hub.ps1:74` | `updated` | the value did not exist in this folder before the round-5 pass, so this line was written by that pass |
| R5-1 | new | `Test-Hub` | `assert-build-plan-hub.ps1:78` | `updated` | the value did not exist in this folder before the round-5 pass, so this line was written by that pass |
| R5-1 | new | `Test-Hub` | `assert-build-plan-hub.ps1:82` | `updated` | the value did not exist in this folder before the round-5 pass, so this line was written by that pass |
| R5-1 | new | `Test-Hub` | `assert-build-plan-hub.ps1:92` | `updated` | the value did not exist in this folder before the round-5 pass, so this line was written by that pass |
| R5-1 | new | `Test-Hub` | `assert-build-plan-hub.ps1:101` | `updated` | the value did not exist in this folder before the round-5 pass, so this line was written by that pass |
| R5-1 | new | `Test-Hub` | `census-round5-corrections.ps1:123` | `confirmed-consistent` | census declaration table (the sweep's own input list), not a plan assertion |
| R5-1 | new | `build-plan-hub.txt` | `task.md:51` | `updated` | the value did not exist in this folder before the round-5 pass, so this line was written by that pass |
| R5-1 | new | `build-plan-hub.txt` | `run-verification-plan.ps1:50` | `updated` | the value did not exist in this folder before the round-5 pass, so this line was written by that pass |
| R5-1 | new | `build-plan-hub.txt` | `implementation-plan.md:339` | `updated` | the value did not exist in this folder before the round-5 pass, so this line was written by that pass |
| R5-1 | new | `build-plan-hub.txt` | `implementation-plan.md:370` | `updated` | the value did not exist in this folder before the round-5 pass, so this line was written by that pass |
| R5-1 | new | `build-plan-hub.txt` | `census-round5-corrections.ps1:124` | `confirmed-consistent` | census declaration table (the sweep's own input list), not a plan assertion |
| R5-1 | new | `AC-40.21` | `task.md:51` | `updated` | the value did not exist in this folder before the round-5 pass, so this line was written by that pass |
| R5-1 | new | `AC-40.21` | `named-sets.json:283` | `updated` | the value did not exist in this folder before the round-5 pass, so this line was written by that pass |
| R5-1 | new | `AC-40.21` | `implementation-plan.md:235` | `updated` | the value did not exist in this folder before the round-5 pass, so this line was written by that pass |
| R5-1 | new | `AC-40.21` | `implementation-plan.md:292` | `updated` | the value did not exist in this folder before the round-5 pass, so this line was written by that pass |
| R5-1 | new | `AC-40.21` | `implementation-plan.md:324` | `updated` | the value did not exist in this folder before the round-5 pass, so this line was written by that pass |
| R5-1 | new | `AC-40.21` | `implementation-plan.md:370` | `updated` | the value did not exist in this folder before the round-5 pass, so this line was written by that pass |
| R5-1 | new | `AC-40.21` | `census-round5-corrections.ps1:125` | `confirmed-consistent` | census declaration table (the sweep's own input list), not a plan assertion |
| R5-1 | new | `AC-40.21` | `assert-build-plan-hub.ps1:1` | `updated` | the value did not exist in this folder before the round-5 pass, so this line was written by that pass |
| R5-1 | carry | `docs/BUILD_PLAN.md` | `task.md:51` | `confirmed-consistent` | pre-existing value, read at the cited line: it agrees with the corrected round-5 rule |
| R5-1 | carry | `docs/BUILD_PLAN.md` | `named-sets.json:166` | `confirmed-consistent` | pre-existing value, read at the cited line: it agrees with the corrected round-5 rule |
| R5-1 | carry | `docs/BUILD_PLAN.md` | `implementation-plan.md:292` | `confirmed-consistent` | pre-existing value, read at the cited line: it agrees with the corrected round-5 rule |
| R5-1 | carry | `docs/BUILD_PLAN.md` | `implementation-plan.md:319` | `confirmed-consistent` | pre-existing value, read at the cited line: it agrees with the corrected round-5 rule |
| R5-1 | carry | `docs/BUILD_PLAN.md` | `census-round5-corrections.ps1:126` | `confirmed-consistent` | census declaration table (the sweep's own input list), not a plan assertion |
| R5-1 | carry | `docs/BUILD_PLAN.md` | `assert-build-plan-hub.ps1:5` | `confirmed-consistent` | pre-existing value, read at the cited line: it agrees with the corrected round-5 rule |
| R5-1 | carry | `assert-closeout.ps1` | `task.md:67` | `confirmed-consistent` | pre-existing value, read at the cited line: it agrees with the corrected round-5 rule |
| R5-1 | carry | `assert-closeout.ps1` | `implementation-plan.md:114` | `confirmed-consistent` | pre-existing value, read at the cited line: it agrees with the corrected round-5 rule |
| R5-1 | carry | `assert-closeout.ps1` | `implementation-plan.md:236` | `confirmed-consistent` | pre-existing value, read at the cited line: it agrees with the corrected round-5 rule |
| R5-1 | carry | `assert-closeout.ps1` | `implementation-plan.md:295` | `confirmed-consistent` | pre-existing value, read at the cited line: it agrees with the corrected round-5 rule |
| R5-1 | carry | `assert-closeout.ps1` | `implementation-plan.md:324` | `confirmed-consistent` | pre-existing value, read at the cited line: it agrees with the corrected round-5 rule |
| R5-1 | carry | `assert-closeout.ps1` | `census-round5-corrections.ps1:46` | `confirmed-consistent` | census declaration table (the sweep's own input list), not a plan assertion |
| R5-1 | carry | `assert-closeout.ps1` | `census-round5-corrections.ps1:127` | `confirmed-consistent` | census declaration table (the sweep's own input list), not a plan assertion |
| R5-1 | carry | `assert-closeout.ps1` | `census-round1-corrections.ps1:33` | `confirmed-consistent` | census declaration table (the sweep's own input list), not a plan assertion |
| R5-1 | carry | `assert-closeout.ps1` | `assert-reflection-quality.ps1:4` | `confirmed-consistent` | pre-existing value, read at the cited line: it agrees with the corrected round-5 rule |
| R5-1 | carry | `assert-closeout.ps1` | `assert-reflection-quality.ps1:7` | `confirmed-consistent` | pre-existing value, read at the cited line: it agrees with the corrected round-5 rule |
| R5-2 | new | `dispositionedBy` | `task.md:55` | `updated` | the value did not exist in this folder before the round-5 pass, so this line was written by that pass |
| R5-2 | new | `dispositionedBy` | `run-verification-plan.ps1:22` | `updated` | the value did not exist in this folder before the round-5 pass, so this line was written by that pass |
| R5-2 | new | `dispositionedBy` | `run-verification-plan.ps1:53` | `updated` | the value did not exist in this folder before the round-5 pass, so this line was written by that pass |
| R5-2 | new | `dispositionedBy` | `run-verification-plan.ps1:54` | `updated` | the value did not exist in this folder before the round-5 pass, so this line was written by that pass |
| R5-2 | new | `dispositionedBy` | `run-verification-plan.ps1:97` | `updated` | the value did not exist in this folder before the round-5 pass, so this line was written by that pass |
| R5-2 | new | `dispositionedBy` | `run-verification-plan.ps1:110` | `updated` | the value did not exist in this folder before the round-5 pass, so this line was written by that pass |
| R5-2 | new | `dispositionedBy` | `implementation-plan.md:373` | `updated` | the value did not exist in this folder before the round-5 pass, so this line was written by that pass |
| R5-2 | new | `dispositionedBy` | `implementation-plan.md:374` | `updated` | the value did not exist in this folder before the round-5 pass, so this line was written by that pass |
| R5-2 | new | `dispositionedBy` | `census-round5-corrections.ps1:130` | `confirmed-consistent` | census declaration table (the sweep's own input list), not a plan assertion |
| R5-2 | new | `E2E_BLOCKED_RECEIPT` | `run-verification-plan.ps1:54` | `updated` | the value did not exist in this folder before the round-5 pass, so this line was written by that pass |
| R5-2 | new | `E2E_BLOCKED_RECEIPT` | `named-sets.json:196` | `updated` | the value did not exist in this folder before the round-5 pass, so this line was written by that pass |
| R5-2 | new | `E2E_BLOCKED_RECEIPT` | `implementation-plan.md:374` | `updated` | the value did not exist in this folder before the round-5 pass, so this line was written by that pass |
| R5-2 | new | `E2E_BLOCKED_RECEIPT` | `implementation-plan.md:375` | `updated` | the value did not exist in this folder before the round-5 pass, so this line was written by that pass |
| R5-2 | new | `E2E_BLOCKED_RECEIPT` | `census-round5-corrections.ps1:131` | `confirmed-consistent` | census declaration table (the sweep's own input list), not a plan assertion |
| R5-2 | new | `E2E_BLOCKED_RECEIPT` | `assert-e2e-wired.ps1:50` | `updated` | the value did not exist in this folder before the round-5 pass, so this line was written by that pass |
| R5-2 | new | `18 scheduled sections` | `task.md:55` | `updated` | the value did not exist in this folder before the round-5 pass, so this line was written by that pass |
| R5-2 | new | `18 scheduled sections` | `census-round5-corrections.ps1:132` | `confirmed-consistent` | census declaration table (the sweep's own input list), not a plan assertion |
| R5-2 | new | `18 scheduled sections` | `census-round5-corrections.ps1:169` | `confirmed-consistent` | census declaration table (the sweep's own input list), not a plan assertion |
| R5-2 | carry | `E2E_DISPOSITION_FILE` | `run-verification-plan.ps1:105` | `confirmed-consistent` | pre-existing value, read at the cited line: it agrees with the corrected round-5 rule |
| R5-2 | carry | `E2E_DISPOSITION_FILE` | `named-sets.json:187` | `confirmed-consistent` | pre-existing value, read at the cited line: it agrees with the corrected round-5 rule |
| R5-2 | carry | `E2E_DISPOSITION_FILE` | `implementation-plan.md:375` | `confirmed-consistent` | pre-existing value, read at the cited line: it agrees with the corrected round-5 rule |
| R5-2 | carry | `E2E_DISPOSITION_FILE` | `census-round5-corrections.ps1:133` | `confirmed-consistent` | census declaration table (the sweep's own input list), not a plan assertion |
| R5-2 | carry | `E2E_DISPOSITION_FILE` | `assert-e2e-wired.ps1:48` | `confirmed-consistent` | pre-existing value, read at the cited line: it agrees with the corrected round-5 rule |
| R5-2 | carry | `E2E_DISPOSITION_FILE` | `assert-e2e-wired.ps1:421` | `confirmed-consistent` | pre-existing value, read at the cited line: it agrees with the corrected round-5 rule |
| R5-2 | carry | `E2E_DISPOSITION_MARKERS` | `named-sets.json:188` | `confirmed-consistent` | pre-existing value, read at the cited line: it agrees with the corrected round-5 rule |
| R5-2 | carry | `E2E_DISPOSITION_MARKERS` | `census-round5-corrections.ps1:134` | `confirmed-consistent` | census declaration table (the sweep's own input list), not a plan assertion |
| R5-2 | carry | `E2E_DISPOSITION_MARKERS` | `assert-e2e-wired.ps1:49` | `confirmed-consistent` | pre-existing value, read at the cited line: it agrees with the corrected round-5 rule |
| R5-2 | carry | `-Mode Executed` | `task.md:50` | `confirmed-consistent` | pre-existing value, read at the cited line: it agrees with the corrected round-5 rule |
| R5-2 | carry | `-Mode Executed` | `implementation-plan.md:230` | `confirmed-consistent` | pre-existing value, read at the cited line: it agrees with the corrected round-5 rule |
| R5-2 | carry | `-Mode Executed` | `implementation-plan.md:231` | `confirmed-consistent` | pre-existing value, read at the cited line: it agrees with the corrected round-5 rule |
| R5-2 | carry | `-Mode Executed` | `implementation-plan.md:375` | `confirmed-consistent` | pre-existing value, read at the cited line: it agrees with the corrected round-5 rule |
| R5-2 | carry | `-Mode Executed` | `census-round5-corrections.ps1:135` | `confirmed-consistent` | census declaration table (the sweep's own input list), not a plan assertion |
| R5-2 | carry | `-Mode Executed` | `census-round4-corrections.ps1:106` | `confirmed-consistent` | census declaration table (the sweep's own input list), not a plan assertion |
| R5-2 | carry | `-Mode Executed` | `assert-e2e-wired.ps1:17` | `confirmed-consistent` | pre-existing value, read at the cited line: it agrees with the corrected round-5 rule |
| R5-2 | carry | `-Mode Wired` | `task.md:50` | `confirmed-consistent` | pre-existing value, read at the cited line: it agrees with the corrected round-5 rule |
| R5-2 | carry | `-Mode Wired` | `task.md:87` | `confirmed-consistent` | pre-existing value, read at the cited line: it agrees with the corrected round-5 rule |
| R5-2 | carry | `-Mode Wired` | `implementation-plan.md:231` | `confirmed-consistent` | pre-existing value, read at the cited line: it agrees with the corrected round-5 rule |
| R5-2 | carry | `-Mode Wired` | `implementation-plan.md:371` | `confirmed-consistent` | pre-existing value, read at the cited line: it agrees with the corrected round-5 rule |
| R5-2 | carry | `-Mode Wired` | `census-round5-corrections.ps1:136` | `confirmed-consistent` | census declaration table (the sweep's own input list), not a plan assertion |
| R5-2 | carry | `-Mode Wired` | `census-round4-corrections.ps1:105` | `confirmed-consistent` | census declaration table (the sweep's own input list), not a plan assertion |
| R5-2 | carry | `-Mode Wired` | `assert-e2e-wired.ps1:13` | `confirmed-consistent` | pre-existing value, read at the cited line: it agrees with the corrected round-5 rule |
| R5-2 | carry | `run-verification-plan.ps1` | `task.md:41` | `confirmed-consistent` | pre-existing value, read at the cited line: it agrees with the corrected round-5 rule |
| R5-2 | carry | `run-verification-plan.ps1` | `task.md:55` | `confirmed-consistent` | pre-existing value, read at the cited line: it agrees with the corrected round-5 rule |
| R5-2 | carry | `run-verification-plan.ps1` | `implementation-plan.md:298` | `confirmed-consistent` | pre-existing value, read at the cited line: it agrees with the corrected round-5 rule |
| R5-2 | carry | `run-verification-plan.ps1` | `implementation-plan.md:347` | `confirmed-consistent` | pre-existing value, read at the cited line: it agrees with the corrected round-5 rule |
| R5-2 | carry | `run-verification-plan.ps1` | `implementation-plan.md:353` | `confirmed-consistent` | pre-existing value, read at the cited line: it agrees with the corrected round-5 rule |
| R5-2 | carry | `run-verification-plan.ps1` | `census-round5-corrections.ps1:21` | `confirmed-consistent` | census declaration table (the sweep's own input list), not a plan assertion |
| R5-2 | carry | `run-verification-plan.ps1` | `census-round5-corrections.ps1:137` | `confirmed-consistent` | census declaration table (the sweep's own input list), not a plan assertion |
| R5-2 | carry | `run-verification-plan.ps1` | `census-round4-corrections.ps1:22` | `confirmed-consistent` | census declaration table (the sweep's own input list), not a plan assertion |
| R5-2 | carry | `run-verification-plan.ps1` | `census-round4-corrections.ps1:158` | `confirmed-consistent` | census declaration table (the sweep's own input list), not a plan assertion |
| R5-2 | carry | `run-verification-plan.ps1` | `census-round3-corrections.ps1:21` | `confirmed-consistent` | census declaration table (the sweep's own input list), not a plan assertion |
| R5-2 | carry | `run-verification-plan.ps1` | `census-round3-corrections.ps1:120` | `confirmed-consistent` | census declaration table (the sweep's own input list), not a plan assertion |
| R5-2 | carry | `run-verification-plan.ps1` | `arm-run.ps1:5` | `confirmed-consistent` | pre-existing value, read at the cited line: it agrees with the corrected round-5 rule |
| R5-2 | carry | `VERIFICATION_PLAN` | `run-verification-plan.ps1:69` | `confirmed-consistent` | pre-existing value, read at the cited line: it agrees with the corrected round-5 rule |
| R5-2 | carry | `VERIFICATION_PLAN` | `run-verification-plan.ps1:72` | `confirmed-consistent` | pre-existing value, read at the cited line: it agrees with the corrected round-5 rule |
| R5-2 | carry | `VERIFICATION_PLAN` | `run-verification-plan.ps1:121` | `confirmed-consistent` | pre-existing value, read at the cited line: it agrees with the corrected round-5 rule |
| R5-2 | carry | `VERIFICATION_PLAN` | `run-verification-plan.ps1:124` | `confirmed-consistent` | pre-existing value, read at the cited line: it agrees with the corrected round-5 rule |
| R5-2 | carry | `VERIFICATION_PLAN` | `census-round5-corrections.ps1:138` | `confirmed-consistent` | census declaration table (the sweep's own input list), not a plan assertion |
| R5-2 | carry | `VERIFICATION_PLAN` | `census-round4-corrections.ps1:159` | `confirmed-consistent` | census declaration table (the sweep's own input list), not a plan assertion |
| R5-2 | carry | `VERIFICATION_PLAN` | `census-round3-corrections.ps1:121` | `confirmed-consistent` | census declaration table (the sweep's own input list), not a plan assertion |
| R5-3 | old | `REFLECTION_MARKERS` | `implementation-plan.md:111` | `confirmed-consistent` | retained mention - round-5 finding R5-3 itself: the gate table row and AC-40.22 name the RETIRED list to state what was deleted and why. Quoting the retired key is the finding, not a residue of it. |
| R5-3 | old | `REFLECTION_MARKERS` | `implementation-plan.md:236` | `confirmed-consistent` | retained mention - round-5 finding R5-3 itself: the gate table row and AC-40.22 name the RETIRED list to state what was deleted and why. Quoting the retired key is the finding, not a residue of it. |
| R5-3 | old | `REFLECTION_MARKERS` | `census-round5-corrections.ps1:44` | `confirmed-consistent` | census declaration table (the sweep's own input list), not a plan assertion |
| R5-3 | old | `REFLECTION_MARKERS` | `census-round5-corrections.ps1:45` | `confirmed-consistent` | census declaration table (the sweep's own input list), not a plan assertion |
| R5-3 | old | `REFLECTION_MARKERS` | `census-round5-corrections.ps1:46` | `confirmed-consistent` | census declaration table (the sweep's own input list), not a plan assertion |
| R5-3 | old | `REFLECTION_MARKERS` | `census-round5-corrections.ps1:141` | `confirmed-consistent` | census declaration table (the sweep's own input list), not a plan assertion |
| R5-3 | old | `REFLECTION_MARKERS` | `assert-reflection-quality.ps1:4` | `confirmed-consistent` | retained mention - header comment plus self-test oracle F1, which reconstructs the four-heading skeleton the retired list accepted and asserts it is now REJECTED. The name appears only as the negative oracle's subject. |
| R5-3 | old | `REFLECTION_MARKERS` | `assert-reflection-quality.ps1:140` | `confirmed-consistent` | retained mention - header comment plus self-test oracle F1, which reconstructs the four-heading skeleton the retired list accepted and asserts it is now REJECTED. The name appears only as the negative oracle's subject. |
| R5-3 | new | `assert-reflection-quality.ps1` | `task.md:65` | `updated` | the value did not exist in this folder before the round-5 pass, so this line was written by that pass |
| R5-3 | new | `assert-reflection-quality.ps1` | `implementation-plan.md:111` | `updated` | the value did not exist in this folder before the round-5 pass, so this line was written by that pass |
| R5-3 | new | `assert-reflection-quality.ps1` | `implementation-plan.md:236` | `updated` | the value did not exist in this folder before the round-5 pass, so this line was written by that pass |
| R5-3 | new | `assert-reflection-quality.ps1` | `implementation-plan.md:295` | `updated` | the value did not exist in this folder before the round-5 pass, so this line was written by that pass |
| R5-3 | new | `assert-reflection-quality.ps1` | `census-round5-corrections.ps1:45` | `confirmed-consistent` | census declaration table (the sweep's own input list), not a plan assertion |
| R5-3 | new | `assert-reflection-quality.ps1` | `census-round5-corrections.ps1:142` | `confirmed-consistent` | census declaration table (the sweep's own input list), not a plan assertion |
| R5-3 | new | `assert-reflection-quality.ps1` | `assert-oracle-selftests.ps1:19` | `updated` | the value did not exist in this folder before the round-5 pass, so this line was written by that pass |
| R5-3 | new | `assert-reflection-quality.ps1` | `assert-closeout.ps1:46` | `updated` | the value did not exist in this folder before the round-5 pass, so this line was written by that pass |
| R5-3 | new | `assert-reflection-quality.ps1` | `assert-closeout.ps1:49` | `updated` | the value did not exist in this folder before the round-5 pass, so this line was written by that pass |
| R5-3 | new | `REFLECTION_QUALITY` | `implementation-plan.md:111` | `updated` | the value did not exist in this folder before the round-5 pass, so this line was written by that pass |
| R5-3 | new | `REFLECTION_QUALITY` | `implementation-plan.md:236` | `updated` | the value did not exist in this folder before the round-5 pass, so this line was written by that pass |
| R5-3 | new | `REFLECTION_QUALITY` | `census-round5-corrections.ps1:143` | `confirmed-consistent` | census declaration table (the sweep's own input list), not a plan assertion |
| R5-3 | new | `REFLECTION_QUALITY` | `assert-reflection-quality.ps1:184` | `updated` | the value did not exist in this folder before the round-5 pass, so this line was written by that pass |
| R5-3 | new | `REFLECTION_QUALITY` | `assert-reflection-quality.ps1:191` | `updated` | the value did not exist in this folder before the round-5 pass, so this line was written by that pass |
| R5-3 | new | `REFLECTION_QUALITY` | `assert-oracle-selftests.ps1:19` | `updated` | the value did not exist in this folder before the round-5 pass, so this line was written by that pass |
| R5-3 | new | `REFLECTION_QUALITY` | `assert-closeout.ps1:49` | `updated` | the value did not exist in this folder before the round-5 pass, so this line was written by that pass |
| R5-3 | new | `REFLECTION_PATTERNS` | `named-sets.json:308` | `updated` | the value did not exist in this folder before the round-5 pass, so this line was written by that pass |
| R5-3 | new | `REFLECTION_PATTERNS` | `implementation-plan.md:236` | `updated` | the value did not exist in this folder before the round-5 pass, so this line was written by that pass |
| R5-3 | new | `REFLECTION_PATTERNS` | `census-round5-corrections.ps1:144` | `confirmed-consistent` | census declaration table (the sweep's own input list), not a plan assertion |
| R5-3 | new | `REFLECTION_PATTERNS` | `assert-reflection-quality.ps1:11` | `updated` | the value did not exist in this folder before the round-5 pass, so this line was written by that pass |
| R5-3 | new | `REFLECTION_PATTERNS` | `assert-reflection-quality.ps1:30` | `updated` | the value did not exist in this folder before the round-5 pass, so this line was written by that pass |
| R5-3 | new | `REFLECTION_MIN_BYTES` | `task.md:65` | `updated` | the value did not exist in this folder before the round-5 pass, so this line was written by that pass |
| R5-3 | new | `REFLECTION_MIN_BYTES` | `named-sets.json:319` | `updated` | the value did not exist in this folder before the round-5 pass, so this line was written by that pass |
| R5-3 | new | `REFLECTION_MIN_BYTES` | `implementation-plan.md:236` | `updated` | the value did not exist in this folder before the round-5 pass, so this line was written by that pass |
| R5-3 | new | `REFLECTION_MIN_BYTES` | `census-round5-corrections.ps1:145` | `confirmed-consistent` | census declaration table (the sweep's own input list), not a plan assertion |
| R5-3 | new | `REFLECTION_MIN_BYTES` | `assert-reflection-quality.ps1:14` | `updated` | the value did not exist in this folder before the round-5 pass, so this line was written by that pass |
| R5-3 | new | `REFLECTION_MIN_BYTES` | `assert-reflection-quality.ps1:31` | `updated` | the value did not exist in this folder before the round-5 pass, so this line was written by that pass |
| R5-3 | new | `REFLECTION_PLACEHOLDER_FORMS` | `named-sets.json:320` | `updated` | the value did not exist in this folder before the round-5 pass, so this line was written by that pass |
| R5-3 | new | `REFLECTION_PLACEHOLDER_FORMS` | `implementation-plan.md:236` | `updated` | the value did not exist in this folder before the round-5 pass, so this line was written by that pass |
| R5-3 | new | `REFLECTION_PLACEHOLDER_FORMS` | `census-round5-corrections.ps1:146` | `confirmed-consistent` | census declaration table (the sweep's own input list), not a plan assertion |
| R5-3 | new | `REFLECTION_PLACEHOLDER_FORMS` | `assert-reflection-quality.ps1:16` | `updated` | the value did not exist in this folder before the round-5 pass, so this line was written by that pass |
| R5-3 | new | `REFLECTION_PLACEHOLDER_FORMS` | `assert-reflection-quality.ps1:32` | `updated` | the value did not exist in this folder before the round-5 pass, so this line was written by that pass |
| R5-3 | new | `Get-ProseBytes` | `census-round5-corrections.ps1:147` | `confirmed-consistent` | census declaration table (the sweep's own input list), not a plan assertion |
| R5-3 | new | `Get-ProseBytes` | `assert-reflection-quality.ps1:36` | `updated` | the value did not exist in this folder before the round-5 pass, so this line was written by that pass |
| R5-3 | new | `Get-ProseBytes` | `assert-reflection-quality.ps1:93` | `updated` | the value did not exist in this folder before the round-5 pass, so this line was written by that pass |
| R5-3 | new | `Test-NonEmptyYamlKey` | `census-round5-corrections.ps1:148` | `confirmed-consistent` | census declaration table (the sweep's own input list), not a plan assertion |
| R5-3 | new | `Test-NonEmptyYamlKey` | `assert-reflection-quality.ps1:52` | `updated` | the value did not exist in this folder before the round-5 pass, so this line was written by that pass |
| R5-3 | new | `Test-NonEmptyYamlKey` | `assert-reflection-quality.ps1:84` | `updated` | the value did not exist in this folder before the round-5 pass, so this line was written by that pass |
| R5-3 | new | `ssot-approved.txt` | `task.md:65` | `updated` | the value did not exist in this folder before the round-5 pass, so this line was written by that pass |
| R5-3 | new | `ssot-approved.txt` | `census-round5-corrections.ps1:149` | `confirmed-consistent` | census declaration table (the sweep's own input list), not a plan assertion |
| R5-3 | new | `AC-40.22` | `task.md:65` | `updated` | the value did not exist in this folder before the round-5 pass, so this line was written by that pass |
| R5-3 | new | `AC-40.22` | `named-sets.json:284` | `updated` | the value did not exist in this folder before the round-5 pass, so this line was written by that pass |
| R5-3 | new | `AC-40.22` | `implementation-plan.md:236` | `updated` | the value did not exist in this folder before the round-5 pass, so this line was written by that pass |
| R5-3 | new | `AC-40.22` | `census-round5-corrections.ps1:44` | `confirmed-consistent` | census declaration table (the sweep's own input list), not a plan assertion |
| R5-3 | new | `AC-40.22` | `census-round5-corrections.ps1:150` | `confirmed-consistent` | census declaration table (the sweep's own input list), not a plan assertion |
| R5-3 | new | `AC-40.22` | `assert-reflection-quality.ps1:1` | `updated` | the value did not exist in this folder before the round-5 pass, so this line was written by that pass |
| R5-3 | carry | `REFLECTION_FILE` | `named-sets.json:305` | `confirmed-consistent` | pre-existing value, read at the cited line: it agrees with the corrected round-5 rule |
| R5-3 | carry | `REFLECTION_FILE` | `census-round5-corrections.ps1:151` | `confirmed-consistent` | census declaration table (the sweep's own input list), not a plan assertion |
| R5-3 | carry | `REFLECTION_FILE` | `assert-reflection-quality.ps1:33` | `confirmed-consistent` | pre-existing value, read at the cited line: it agrees with the corrected round-5 rule |
| R5-3 | carry | `REFLECTION_FILE` | `assert-reflection-quality.ps1:188` | `confirmed-consistent` | pre-existing value, read at the cited line: it agrees with the corrected round-5 rule |
| R5-3 | carry | `REFLECTION_SCHEMA` | `named-sets.json:307` | `confirmed-consistent` | pre-existing value, read at the cited line: it agrees with the corrected round-5 rule |
| R5-3 | carry | `REFLECTION_SCHEMA` | `census-round5-corrections.ps1:152` | `confirmed-consistent` | census declaration table (the sweep's own input list), not a plan assertion |
| R5-3 | carry | `reflection-structure.txt` | `task.md:65` | `confirmed-consistent` | pre-existing value, read at the cited line: it agrees with the corrected round-5 rule |
| R5-3 | carry | `reflection-structure.txt` | `census-round5-corrections.ps1:153` | `confirmed-consistent` | census declaration table (the sweep's own input list), not a plan assertion |
| R5-3 | carry | `completion-preflight` | `task.md:65` | `confirmed-consistent` | pre-existing value, read at the cited line: it agrees with the corrected round-5 rule |
| R5-3 | carry | `completion-preflight` | `task.md:67` | `confirmed-consistent` | pre-existing value, read at the cited line: it agrees with the corrected round-5 rule |
| R5-3 | carry | `completion-preflight` | `implementation-plan.md:236` | `confirmed-consistent` | pre-existing value, read at the cited line: it agrees with the corrected round-5 rule |
| R5-3 | carry | `completion-preflight` | `census-round5-corrections.ps1:140` | `confirmed-consistent` | census declaration table (the sweep's own input list), not a plan assertion |
| R5-3 | carry | `completion-preflight` | `census-round5-corrections.ps1:154` | `confirmed-consistent` | census declaration table (the sweep's own input list), not a plan assertion |
| R5-3 | carry | `completion-preflight` | `assert-reflection-quality.ps1:9` | `confirmed-consistent` | pre-existing value, read at the cited line: it agrees with the corrected round-5 rule |
| PR-9 | new | `lib-disposition.ps1` | `run-verification-plan.ps1:34` | `updated` | the value did not exist in this folder before the round-5 pass, so this line was written by that pass |
| PR-9 | new | `lib-disposition.ps1` | `implementation-plan.md:296` | `updated` | the value did not exist in this folder before the round-5 pass, so this line was written by that pass |
| PR-9 | new | `lib-disposition.ps1` | `census-round5-corrections.ps1:20` | `confirmed-consistent` | census declaration table (the sweep's own input list), not a plan assertion |
| PR-9 | new | `lib-disposition.ps1` | `census-round5-corrections.ps1:157` | `confirmed-consistent` | census declaration table (the sweep's own input list), not a plan assertion |
| PR-9 | new | `lib-disposition.ps1` | `assert-smoke-disposition.ps1:37` | `updated` | the value did not exist in this folder before the round-5 pass, so this line was written by that pass |
| PR-9 | new | `lib-disposition.ps1` | `assert-e2e-wired.ps1:56` | `updated` | the value did not exist in this folder before the round-5 pass, so this line was written by that pass |
| PR-9 | new | `lib-disposition.ps1` | `arm-run.ps1:15` | `updated` | the value did not exist in this folder before the round-5 pass, so this line was written by that pass |
| PR-9 | new | `Get-DispositionMap` | `run-verification-plan.ps1:107` | `updated` | the value did not exist in this folder before the round-5 pass, so this line was written by that pass |
| PR-9 | new | `Get-DispositionMap` | `lib-disposition.ps1:13` | `updated` | the value did not exist in this folder before the round-5 pass, so this line was written by that pass |
| PR-9 | new | `Get-DispositionMap` | `lib-disposition.ps1:50` | `updated` | the value did not exist in this folder before the round-5 pass, so this line was written by that pass |
| PR-9 | new | `Get-DispositionMap` | `census-round5-corrections.ps1:158` | `confirmed-consistent` | census declaration table (the sweep's own input list), not a plan assertion |
| PR-9 | new | `Get-DispositionMap` | `assert-smoke-disposition.ps1:67` | `updated` | the value did not exist in this folder before the round-5 pass, so this line was written by that pass |
| PR-9 | new | `Get-DispositionMap` | `assert-e2e-wired.ps1:376` | `updated` | the value did not exist in this folder before the round-5 pass, so this line was written by that pass |
| PR-9 | new | `Get-DispositionMap` | `assert-e2e-wired.ps1:379` | `updated` | the value did not exist in this folder before the round-5 pass, so this line was written by that pass |
| PR-9 | new | `Get-DispositionMap` | `assert-e2e-wired.ps1:383` | `updated` | the value did not exist in this folder before the round-5 pass, so this line was written by that pass |
| PR-9 | new | `Get-DispositionMap` | `assert-e2e-wired.ps1:388` | `updated` | the value did not exist in this folder before the round-5 pass, so this line was written by that pass |
| PR-9 | new | `Get-DispositionMap` | `assert-e2e-wired.ps1:392` | `updated` | the value did not exist in this folder before the round-5 pass, so this line was written by that pass |
| PR-9 | new | `Get-DispositionMap` | `assert-e2e-wired.ps1:426` | `updated` | the value did not exist in this folder before the round-5 pass, so this line was written by that pass |
| PR-9 | new | `Test-DispositionMarkers` | `lib-disposition.ps1:28` | `updated` | the value did not exist in this folder before the round-5 pass, so this line was written by that pass |
| PR-9 | new | `Test-DispositionMarkers` | `census-round5-corrections.ps1:159` | `confirmed-consistent` | census declaration table (the sweep's own input list), not a plan assertion |
| PR-9 | new | `Test-DispositionMarkers` | `assert-smoke-disposition.ps1:65` | `updated` | the value did not exist in this folder before the round-5 pass, so this line was written by that pass |
| PR-9 | new | `Test-DispositionMarkers` | `assert-e2e-wired.ps1:424` | `updated` | the value did not exist in this folder before the round-5 pass, so this line was written by that pass |
| X-ac-count | old | `"AC_COUNT": 20` | `census-round5-corrections.ps1:162` | `confirmed-consistent` | census declaration table (the sweep's own input list), not a plan assertion |
| X-ac-count | old | `"AC_COUNT": 20` | `census-round4-corrections.ps1:144` | `confirmed-consistent` | census declaration table (the sweep's own input list), not a plan assertion |
| X-ac-count | old | `20 ACs` | `census-round5-corrections.ps1:163` | `confirmed-consistent` | census declaration table (the sweep's own input list), not a plan assertion |
| X-ac-count | new | `"AC_COUNT": 22` | `named-sets.json:261` | `updated` | the value did not exist in this folder before the round-5 pass, so this line was written by that pass |
| X-ac-count | new | `"AC_COUNT": 22` | `census-round5-corrections.ps1:164` | `confirmed-consistent` | census declaration table (the sweep's own input list), not a plan assertion |
| X-ac-count | carry | `AC_COUNT` | `task.md:60` | `confirmed-consistent` | pre-existing value, read at the cited line: it agrees with the corrected round-5 rule |
| X-ac-count | carry | `AC_COUNT` | `named-sets.json:261` | `confirmed-consistent` | pre-existing value, read at the cited line: it agrees with the corrected round-5 rule |
| X-ac-count | carry | `AC_COUNT` | `implementation-plan.md:112` | `confirmed-consistent` | pre-existing value, read at the cited line: it agrees with the corrected round-5 rule |
| X-ac-count | carry | `AC_COUNT` | `census-round5-corrections.ps1:162` | `confirmed-consistent` | census declaration table (the sweep's own input list), not a plan assertion |
| X-ac-count | carry | `AC_COUNT` | `census-round5-corrections.ps1:164` | `confirmed-consistent` | census declaration table (the sweep's own input list), not a plan assertion |
| X-ac-count | carry | `AC_COUNT` | `census-round5-corrections.ps1:165` | `confirmed-consistent` | census declaration table (the sweep's own input list), not a plan assertion |
| X-ac-count | carry | `AC_COUNT` | `census-round4-corrections.ps1:142` | `confirmed-consistent` | census declaration table (the sweep's own input list), not a plan assertion |
| X-ac-count | carry | `AC_COUNT` | `census-round4-corrections.ps1:144` | `confirmed-consistent` | census declaration table (the sweep's own input list), not a plan assertion |
| X-ac-count | carry | `AC_COUNT` | `census-round4-corrections.ps1:145` | `confirmed-consistent` | census declaration table (the sweep's own input list), not a plan assertion |
| X-ac-count | carry | `AC_COUNT` | `census-round3-corrections.ps1:129` | `confirmed-consistent` | census declaration table (the sweep's own input list), not a plan assertion |
| X-ac-count | carry | `AC_COUNT` | `census-round3-corrections.ps1:131` | `confirmed-consistent` | census declaration table (the sweep's own input list), not a plan assertion |
| X-ac-count | carry | `AC_COUNT` | `census-round3-corrections.ps1:132` | `confirmed-consistent` | census declaration table (the sweep's own input list), not a plan assertion |
| X-ac-count | carry | `AC_COUNT` | `census-round1-corrections.ps1:90` | `confirmed-consistent` | census declaration table (the sweep's own input list), not a plan assertion |
| X-ac-count | carry | `AC_COUNT` | `assert-handoff-acs.ps1:2` | `confirmed-consistent` | pre-existing value, read at the cited line: it agrees with the corrected round-5 rule |
| X-ac-count | carry | `AC_COUNT` | `assert-handoff-acs.ps1:9` | `confirmed-consistent` | pre-existing value, read at the cited line: it agrees with the corrected round-5 rule |
| X-ac-count | carry | `AC_COUNT` | `assert-handoff-acs.ps1:17` | `confirmed-consistent` | pre-existing value, read at the cited line: it agrees with the corrected round-5 rule |
| X-ac-count | carry | `AC_IDS` | `assert-handoff-acs.ps1:3` | `confirmed-consistent` | pre-existing value, read at the cited line: it agrees with the corrected round-5 rule |
| X-ac-count | carry | `AC_IDS` | `assert-handoff-acs.ps1:10` | `confirmed-consistent` | pre-existing value, read at the cited line: it agrees with the corrected round-5 rule |
| X-ac-count | carry | `AC_IDS` | `assert-handoff-acs.ps1:21` | `confirmed-consistent` | pre-existing value, read at the cited line: it agrees with the corrected round-5 rule |
| X-ac-count | carry | `AC_IDS` | `census-round1-corrections.ps1:91` | `confirmed-consistent` | census declaration table (the sweep's own input list), not a plan assertion |
| X-ac-count | carry | `AC_IDS` | `task.md:60` | `confirmed-consistent` | pre-existing value, read at the cited line: it agrees with the corrected round-5 rule |
| X-ac-count | carry | `AC_IDS` | `named-sets.json:262` | `confirmed-consistent` | pre-existing value, read at the cited line: it agrees with the corrected round-5 rule |
| X-ac-count | carry | `AC_IDS` | `census-round5-corrections.ps1:166` | `confirmed-consistent` | census declaration table (the sweep's own input list), not a plan assertion |
| X-ac-count | carry | `AC_IDS` | `census-round3-corrections.ps1:133` | `confirmed-consistent` | census declaration table (the sweep's own input list), not a plan assertion |
| X-ac-count | carry | `AC_IDS` | `census-round4-corrections.ps1:146` | `confirmed-consistent` | census declaration table (the sweep's own input list), not a plan assertion |
| X-ac-count | carry | `assert-handoff-acs.ps1` | `task.md:60` | `confirmed-consistent` | pre-existing value, read at the cited line: it agrees with the corrected round-5 rule |
| X-ac-count | carry | `assert-handoff-acs.ps1` | `implementation-plan.md:112` | `confirmed-consistent` | pre-existing value, read at the cited line: it agrees with the corrected round-5 rule |
| X-ac-count | carry | `assert-handoff-acs.ps1` | `implementation-plan.md:295` | `confirmed-consistent` | pre-existing value, read at the cited line: it agrees with the corrected round-5 rule |
| X-ac-count | carry | `assert-handoff-acs.ps1` | `census-round5-corrections.ps1:167` | `confirmed-consistent` | census declaration table (the sweep's own input list), not a plan assertion |
| X-ac-count | carry | `assert-handoff-acs.ps1` | `census-round4-corrections.ps1:147` | `confirmed-consistent` | census declaration table (the sweep's own input list), not a plan assertion |
| X-ac-count | carry | `assert-handoff-acs.ps1` | `census-round1-corrections.ps1:36` | `confirmed-consistent` | census declaration table (the sweep's own input list), not a plan assertion |
| X-ac-count | carry | `assert-handoff-acs.ps1` | `assert-closeout.ps1:34` | `confirmed-consistent` | pre-existing value, read at the cited line: it agrees with the corrected round-5 rule |
| X-sections | old | `16 sections` | `census-round5-corrections.ps1:170` | `confirmed-consistent` | census declaration table (the sweep's own input list), not a plan assertion |
| X-sections | old | `16 sections` | `census-round4-corrections.ps1:154` | `confirmed-consistent` | census declaration table (the sweep's own input list), not a plan assertion |
| X-sections | old | `16-section` | `census-round5-corrections.ps1:171` | `confirmed-consistent` | census declaration table (the sweep's own input list), not a plan assertion |
| X-sections | old | `sections 0-6, 8, 9, 10` | `census-round5-corrections.ps1:172` | `confirmed-consistent` | census declaration table (the sweep's own input list), not a plan assertion |
| X-sections | new | `id = '8a'` | `run-verification-plan.ps1:50` | `updated` | the value did not exist in this folder before the round-5 pass, so this line was written by that pass |
| X-sections | new | `id = '8a'` | `census-round5-corrections.ps1:173` | `confirmed-consistent` | census declaration table (the sweep's own input list), not a plan assertion |
| X-sections | new | `id = '9a1'` | `run-verification-plan.ps1:52` | `updated` | the value did not exist in this folder before the round-5 pass, so this line was written by that pass |
| X-sections | new | `id = '9a1'` | `census-round5-corrections.ps1:174` | `confirmed-consistent` | census declaration table (the sweep's own input list), not a plan assertion |
| X-census | new | `census-round5-corrections.ps1` | `census-round5-corrections.ps1:39` | `confirmed-consistent` | census declaration table (the sweep's own input list), not a plan assertion |
| X-census | new | `census-round5-corrections.ps1` | `census-round5-corrections.ps1:177` | `confirmed-consistent` | census declaration table (the sweep's own input list), not a plan assertion |
| X-census | carry | `census-round4-corrections.ps1` | `census-round5-corrections.ps1:38` | `confirmed-consistent` | census declaration table (the sweep's own input list), not a plan assertion |
| X-census | carry | `census-round4-corrections.ps1` | `census-round5-corrections.ps1:178` | `confirmed-consistent` | census declaration table (the sweep's own input list), not a plan assertion |
| X-census | carry | `census-round4-corrections.ps1` | `census-round4-corrections.ps1:39` | `confirmed-consistent` | census declaration table (the sweep's own input list), not a plan assertion |
| X-census | carry | `census-round4-corrections.ps1` | `census-round4-corrections.ps1:170` | `confirmed-consistent` | census declaration table (the sweep's own input list), not a plan assertion |
| X-selftests | carry | `assert-oracle-selftests.ps1` | `task.md:40` | `confirmed-consistent` | pre-existing value, read at the cited line: it agrees with the corrected round-5 rule |
| X-selftests | carry | `assert-oracle-selftests.ps1` | `run-verification-plan.ps1:39` | `confirmed-consistent` | pre-existing value, read at the cited line: it agrees with the corrected round-5 rule |
| X-selftests | carry | `assert-oracle-selftests.ps1` | `implementation-plan.md:97` | `confirmed-consistent` | pre-existing value, read at the cited line: it agrees with the corrected round-5 rule |
| X-selftests | carry | `assert-oracle-selftests.ps1` | `implementation-plan.md:295` | `confirmed-consistent` | pre-existing value, read at the cited line: it agrees with the corrected round-5 rule |
| X-selftests | carry | `assert-oracle-selftests.ps1` | `implementation-plan.md:358` | `confirmed-consistent` | pre-existing value, read at the cited line: it agrees with the corrected round-5 rule |
| X-selftests | carry | `assert-oracle-selftests.ps1` | `census-round5-corrections.ps1:179` | `confirmed-consistent` | census declaration table (the sweep's own input list), not a plan assertion |
| X-selftests | carry | `assert-oracle-selftests.ps1` | `census-round4-corrections.ps1:172` | `confirmed-consistent` | census declaration table (the sweep's own input list), not a plan assertion |
| X-selftests | carry | `assert-oracle-selftests.ps1` | `census-round3-corrections.ps1:134` | `confirmed-consistent` | census declaration table (the sweep's own input list), not a plan assertion |
| X-selftests | carry | `assert-oracle-selftests.ps1` | `census-round1-corrections.ps1:96` | `confirmed-consistent` | census declaration table (the sweep's own input list), not a plan assertion |
| X-selftests | carry | `assert-oracle-selftests.ps1` | `assert-closeout.ps1:18` | `confirmed-consistent` | pre-existing value, read at the cited line: it agrees with the corrected round-5 rule |
| X-selftests | carry | `-SelfTest` | `task.md:40` | `confirmed-consistent` | pre-existing value, read at the cited line: it agrees with the corrected round-5 rule |
| X-selftests | carry | `-SelfTest` | `task.md:41` | `confirmed-consistent` | pre-existing value, read at the cited line: it agrees with the corrected round-5 rule |
| X-selftests | carry | `-SelfTest` | `task.md:82` | `confirmed-consistent` | pre-existing value, read at the cited line: it agrees with the corrected round-5 rule |
| X-selftests | carry | `-SelfTest` | `implementation-plan.md:97` | `confirmed-consistent` | pre-existing value, read at the cited line: it agrees with the corrected round-5 rule |
| X-selftests | carry | `-SelfTest` | `implementation-plan.md:221` | `confirmed-consistent` | pre-existing value, read at the cited line: it agrees with the corrected round-5 rule |
| X-selftests | carry | `-SelfTest` | `implementation-plan.md:227` | `confirmed-consistent` | pre-existing value, read at the cited line: it agrees with the corrected round-5 rule |
| X-selftests | carry | `-SelfTest` | `implementation-plan.md:231` | `confirmed-consistent` | pre-existing value, read at the cited line: it agrees with the corrected round-5 rule |
| X-selftests | carry | `-SelfTest` | `implementation-plan.md:295` | `confirmed-consistent` | pre-existing value, read at the cited line: it agrees with the corrected round-5 rule |
| X-selftests | carry | `-SelfTest` | `implementation-plan.md:297` | `confirmed-consistent` | pre-existing value, read at the cited line: it agrees with the corrected round-5 rule |
| X-selftests | carry | `-SelfTest` | `implementation-plan.md:298` | `confirmed-consistent` | pre-existing value, read at the cited line: it agrees with the corrected round-5 rule |
| X-selftests | carry | `-SelfTest` | `implementation-plan.md:349` | `confirmed-consistent` | pre-existing value, read at the cited line: it agrees with the corrected round-5 rule |
| X-selftests | carry | `-SelfTest` | `assert-overlay-deleted.ps1:2` | `confirmed-consistent` | pre-existing value, read at the cited line: it agrees with the corrected round-5 rule |
| X-selftests | carry | `-SelfTest` | `assert-oracle-selftests.ps1:7` | `confirmed-consistent` | pre-existing value, read at the cited line: it agrees with the corrected round-5 rule |
| X-selftests | carry | `-SelfTest` | `assert-oracle-selftests.ps1:8` | `confirmed-consistent` | pre-existing value, read at the cited line: it agrees with the corrected round-5 rule |
| X-selftests | carry | `-SelfTest` | `assert-oracle-selftests.ps1:9` | `confirmed-consistent` | pre-existing value, read at the cited line: it agrees with the corrected round-5 rule |
| X-selftests | carry | `-SelfTest` | `assert-oracle-selftests.ps1:10` | `confirmed-consistent` | pre-existing value, read at the cited line: it agrees with the corrected round-5 rule |
| X-selftests | carry | `-SelfTest` | `assert-oracle-selftests.ps1:11` | `confirmed-consistent` | pre-existing value, read at the cited line: it agrees with the corrected round-5 rule |
| X-selftests | carry | `-SelfTest` | `assert-oracle-selftests.ps1:12` | `confirmed-consistent` | pre-existing value, read at the cited line: it agrees with the corrected round-5 rule |
| X-selftests | carry | `-SelfTest` | `assert-oracle-selftests.ps1:13` | `confirmed-consistent` | pre-existing value, read at the cited line: it agrees with the corrected round-5 rule |
| X-selftests | carry | `-SelfTest` | `assert-oracle-selftests.ps1:14` | `confirmed-consistent` | pre-existing value, read at the cited line: it agrees with the corrected round-5 rule |
| X-selftests | carry | `-SelfTest` | `assert-oracle-selftests.ps1:17` | `confirmed-consistent` | pre-existing value, read at the cited line: it agrees with the corrected round-5 rule |
| X-selftests | carry | `-SelfTest` | `assert-oracle-selftests.ps1:18` | `confirmed-consistent` | pre-existing value, read at the cited line: it agrees with the corrected round-5 rule |
| X-selftests | carry | `-SelfTest` | `assert-oracle-selftests.ps1:19` | `confirmed-consistent` | pre-existing value, read at the cited line: it agrees with the corrected round-5 rule |
| X-selftests | carry | `-SelfTest` | `census-round5-corrections.ps1:180` | `confirmed-consistent` | census declaration table (the sweep's own input list), not a plan assertion |
| X-selftests | carry | `-SelfTest` | `assert-e2e-wired.ps1:21` | `confirmed-consistent` | pre-existing value, read at the cited line: it agrees with the corrected round-5 rule |
| X-selftests | carry | `-SelfTest` | `assert-picker-binding.ps1:24` | `confirmed-consistent` | pre-existing value, read at the cited line: it agrees with the corrected round-5 rule |
| X-selftests | carry | `-SelfTest` | `census-round4-corrections.ps1:173` | `confirmed-consistent` | census declaration table (the sweep's own input list), not a plan assertion |
| X-selftests | carry | `-SelfTest` | `census-round1-corrections.ps1:97` | `confirmed-consistent` | census declaration table (the sweep's own input list), not a plan assertion |
| X-selftests | carry | `-SelfTest` | `assert-task-rows.ps1:27` | `confirmed-consistent` | pre-existing value, read at the cited line: it agrees with the corrected round-5 rule |
| X-selftests | carry | `-SelfTest` | `census-round3-corrections.ps1:135` | `confirmed-consistent` | census declaration table (the sweep's own input list), not a plan assertion |

---

## Round 6 — Corrections Re-Review

### Intent Anchor

Executing this plan is supposed to replace the Chromium capture overlay with a packaged .NET 8
WinForms picker while preserving the existing Electron/Python/API boundaries and proving the real
F2-to-publish path before closeout. The plan remains unstarted and is not yet approvable: the
Round-5 corrections close the exact stale-report and unrelated-file cases, but five current
controls still accept materially missing deliverables or hide a real failing step.

### PR-6 Evidence Adjudication

PR-6 is sufficient, so content review proceeded. `C:/Temp/av-kit/census-round5.txt` and a fresh
rerun are both 1,616 lines; the rerun exits `0`, reports `107 x 2 = 214` sweeps, 755 FOLDER
dispositions, worst `rg` exit `0`, and `STALE SITES: 0`. The rolling correction log contains
exactly 755 hit rows: 292 `updated` and 463 `confirmed-consistent`. The sweep uses `rg -F`; its
execution path at `census-round5-corrections.ps1:202-232` has no truncating output filter and exits
`3` on a surviving old form. The three retained `REFLECTION_MARKERS` references are historical or
negative-oracle text, not an executable owner. This is enough to satisfy the round-2+ procedural
gate. A content mismatch remains reviewable rather than procedural: the correction log says
`Environment.Exit(` was added to `BINDING_TERMINAL_FORMS` (rolling file line 2255), while the
executable set is actually `return`, `throw`, `goto` (`named-sets.json:97-100`).

### Per-Finding Resolution and Regression Check

| Finding | Disposition | Current-file evidence |
|---|---|---|
| R4-2-R5 — binding reachability / Roslyn anchoring | `partially_resolved` | The exact post-`return` input and four empty test methods now fail (`assert-picker-binding.ps1:239-301`, B6/B7 at `:377-410`, `:496-518`), and guard/lambda/switch-expression/local-function/interpolated-string probes do not create false positives. However the terminal recognizer is only a start-of-statement string list (`:211-219`), so `Environment.Exit(1); return Run(...)`, `Environment.FailFast(...); return Run(...)`, and `stop: return 1; return Run(...)` all pass; executable receipt: `C:/Temp/av-kit/r6-review-adversarial-functions-valid.txt`. The claimed `Environment.Exit(` correction is absent from `named-sets.json:97-100`. |
| R4-3-R5 — executable segments / fresh E2E report | `resolved` | Hollow `echo` segments are rejected by `assert-e2e-wired.ps1:121-149`; the report is deleted and stamped by `arm-run.ps1:25-30`; §9a1 precedes §9c (`run-verification-plan.ps1:51-55`); and `BLOCKED=no` requires a fresh green report (`assert-e2e-wired.ps1:437-443`). Re-arming after production deletes the report, while equal filesystem timestamps remain safe because arming deleted the prior artifact. A token-boundary weakness (`playwright test-does-nothing`, `dotnet publisher`) remains a predicate-shape correction note, but cannot itself produce the fresh green report required on the non-blocked path. |
| R4-4-R5 — smoke command/run/follow-up binding | `partially_resolved` | Exact receipt path, freshness, command marker, anchored latency, reproduced error, and registered follow-up checks are present (`assert-smoke-disposition.ps1:71-100`; `lib-disposition.ps1:38-92`). But task row 9's validation arms and immediately calls the gate without launching `npm --prefix ui run dev` (`task.md:52`), while the gate treats marker text as producer identity. A fresh two-line file containing only that command text and `picker_startup_ms=8` passes with no process run; receipt: `C:/Temp/av-kit/r6-review-smoke-synthetic-valid.txt`. |
| R5-1 — BUILD_PLAN hub predicate | `partially_resolved` | The live hub now fails as required and the gate is scheduled and closed out (`assert-build-plan-hub.ps1:99-103`; `run-verification-plan.ps1:50`; `assert-closeout.ps1:30-32`). But `Test-Hub` skips all forbidden-token checks as soon as any required token occurs on the same line (`assert-build-plan-hub.ps1:39-47`). Appending `region picker` to each otherwise unchanged stale `overlay` / `desktopCapturer` line passes; executable receipt: `C:/Temp/av-kit/r6-review-adversarial-functions-valid.txt`. |
| R5-2 — single E2E disposition point | `partially_resolved` | An evidenced capture blocker can now reach DONE, but both §9b and §9c are deferred to §9d (`run-verification-plan.ps1:53-55`), and the post-loop logic excuses every deferred failure whenever §9d passes and the one disposition says `BLOCKED=yes` (`:102-117`). Therefore a no-display blocker evidenced by §9c also hides an unrelated regression in the full §9b suite; executable simulation: `C:/Temp/av-kit/r6-review-runner-inverse-canonical.txt` (`9b=23`, `9c=17`, `9d=0` -> final exit `0`). |
| R5-3 — reflection canonical contract | `partially_resolved` | The four-heading skeleton, empty YAML keys, listed placeholders, and global prose shortage now fail (`assert-reflection-quality.ps1:73-97`, F1-F7 at `:140-181`), and closeout has one owner (`assert-closeout.ps1:45-49`). The canonical rule requires all 11 template sections to have substantive answers (`completion-preflight/SKILL.md:155`); the gate checks nine broad patterns and one global character count (`named-sets.json:308-324`; `assert-reflection-quality.ps1:35-49`). A 2,100-character filler block plus incomplete template content and surviving `___` / `_Target MEU(s)_` placeholders passes; executable receipt: `C:/Temp/av-kit/r6-review-adversarial-functions-valid.txt`. |
| R4-1 | `resolved; not regressed` | Positive last-cell status parsing and T1-T11 remain in `assert-task-rows.ps1`; the aggregate self-test passed. |
| N3 / N5 / N6 / N7 | `resolved; not regressed` | N3 exact packaging composition and clean-path oracle remain; N5's new 214-sweep census passes; N6's single executable runner now inventories 18 on-disk sections; N7 remains an evidence-triggered `out-of-scope` proposal with no fake deferred MEU (`implementation-plan.md:307`). R5-2's cross-step adjudication defect is new logic, not regression to N6's old prose-only owner. |
| F2 / F5 / F6 / F7 / F8 | `resolved; not regressed` | Closeout invokes only existing scripts/tools and now calls both new gates (`assert-closeout.ps1:28-49`); publication atomicity remains at `implementation-plan.md:178-189`; RED rows still exit with the oracle code (`task.md:44`, `:48`); minimum edge and exit mappings remain single named definitions (`named-sets.json:11-14`). |

### Findings

| # | Severity | Finding and concrete failure scenario | File:Line | Required correction |
|---|---|---|---|---|
| R6-1 | High | **PR-8 / DR-1 — the promised entrypoint reachability correction is incomplete and misreported.** `Environment.Exit(1)` and `Environment.FailFast(...)` terminate the process, and a labelled `return` terminates linear flow, yet all three may precede the required seam and pass `PICKER_BINDING`. This ships a helper whose advertised production entrypoint never opens the picker. | `named-sets.json:97-100`; `assert-picker-binding.ps1:211-219`, `:239-264`; rolling correction log `:2255` | Make the executed Roslyn proof establish reachability rather than relying on an open-ended terminal-string census; at minimum reject process-terminating calls and labelled terminal statements. Add the three counterexamples as negative oracles and make the correction log match the executable set. |
| R6-2 | High | **PR-4 / PR-8 — smoke completion still has no production command.** Row 9's exact validation never runs the dev command; `Test-Disposition` accepts any post-stamp file carrying two expected strings. The row can close without Electron starting, F2 firing, a drag occurring, a PNG publishing, or the filmstrip refreshing. | `task.md:52`; `assert-smoke-disposition.ps1:71-96`; `arm-run.ps1:25-30` | Add an executable smoke producer/wrapper that arms, launches the declared command, records a unique run identity and measurement, and produces the canonical receipt; bind the gate to that producer. Add the marker-only receipt as a failing oracle. |
| R6-3 | High | **PR-4 / DR-6 — the hub gate permits a cosmetic non-reconciliation.** Its same-line exemption is semantic-free: appending `region picker` to an unchanged line that still states `F2 region overlay` or `desktopCapturer freeze + crop` passes, leaving the hub contradictory after the architecture change. | `assert-build-plan-hub.ps1:33-55`; `implementation-plan.md:317-336`; `task.md:51` | Define and assert the allowed final hub rows or require explicit replacement/retirement semantics while rejecting stale current-state phrases. Add the cosmetic-suffix fixture as a negative oracle. |
| R6-4 | High | **PR-1 / PR-8 — one capture blocker can hide a different full-suite regression.** §9d validates only `E2E_BLOCKED_RECEIPT` from §9c, but the runner uses that result to excuse §9b too. A real §9b regression plus an independently valid §9c no-display blocker yields runner exit `0`. | `run-verification-plan.ps1:53-55`, `:102-117`; `task.md:55` | Keep §9b blocking, or require a separately validated, cause-bound disposition for every deferred step using that step's own receipt/error signature. Add the mixed-cause `9b != 0`, `9c != 0`, `9d = 0` oracle. |
| R6-5 | High | **PR-4 / DR-4 — reflection validation does not enforce the cited canonical contract.** A single repeated filler string supplies the global length while required template sections remain absent or placeholder-filled. This passes the last machine gate after independent review and allows noncompliant institutional memory to close DONE. | `.agent/skills/completion-preflight/SKILL.md:155`; `docs/execution/reflections/TEMPLATE.md:17-137`; `named-sets.json:308-324`; `assert-reflection-quality.ps1:35-97` | Enforce every canonical template section and substantive content per section, expand placeholder detection to the template's surviving forms (`___`, brace placeholders, italic prompts, empty defaults), and reject repeated/padded filler. Add the demonstrated padded-incomplete fixture. |

No Critical or Medium findings were identified. The `Test-ScriptSegment` head check should also
use a token boundary (`playwright test-does-nothing` and `dotnet publisher` currently match), but
this is non-blocking predicate-shape cleanup because the required run/report or hard build step
still prevents that input alone from closing the deliverable.

### Checklist Verdicts

| Check | Result | Evidence |
|---|---|---|
| PR-1 Plan/task alignment | **fail** | R6-4 makes the runner's result weaker than task row H1-2's “all blocking checks pass”; R6-2 leaves the row-9 producer outside its exact validation. |
| PR-2 Not-started confirmation | pass | `native/region-picker*`, `capture-picker.ts`, the capture E2E, MEU handoff, and implementation review are absent; all eight Chromium overlay files remain. |
| PR-3 Task contract completeness | pass | All 26 actionable rows retain task/owner/deliverable/validation/status fields. `rtk`, `pwsh`, `dotnet`, `npm`, `uv`, and `python` resolve, and every referenced `.ps1`/`.py` executable exists. |
| PR-4 Validation realism | **fail** | R6-2 through R6-5 demonstrate a missing producer, cosmetic reconciliation, cross-step failure masking, and incomplete closeout acceptance. |
| PR-5 Source-backed planning | pass | All 22 AC rows use allowed source labels; no new unsourced product behavior was found. |
| PR-6 Handoff/corrections readiness | pass | Complete 1,616-line receipt, 214 sweeps, and 755 per-hit dispositions reproduced; content mismatch is adjudicated under R6-1. |
| PR-7 Scope discipline | pass | No-fallback is Human-approved; warm process is evidence-triggered `out-of-scope`; platform/annotation deferrals are present in `09-screenshot-capture.md:478-484`; `mss`/bbox, MEU-37/38, GDI map, and NSIS bases are present in current canon. No disguised contract work or unscheduled `deferred` row was found. |
| PR-8 Control reachability / totality | **fail** | R6-1, R6-2, and R6-4 provide concrete missing reachability/producer/cause bindings. AC totality itself passes: 22 plan rows = `AC_COUNT` 22 = 22 unique `AC_IDS`, with zero unreachable ACs. |
| PR-9 Single-statement discipline | pass | Each shared disposition/freshness helper has exactly one owner in `lib-disposition.ps1`; hub/reflection/script predicates each have one owner; the retired reflection list has no executable owner; the fresh census reports zero stale sites. |
| DR-1 Claim-to-state match | **fail** | The Round-5 correction log claims `Environment.Exit(` is terminal, but the executable set contains `goto` instead; R6-2/R6-3/R6-5 also overstate what the controls prove. |
| DR-2 Residual old terms | pass | The fresh census reports `STALE SITES: 0`; retained old terms are declaration/history/oracle contexts. |
| DR-3 Downstream references updated | pass | Plan/task/named sets/gates/runner/closeout use the 22-AC and 18-section model consistently; AC-40.22 is reachable from H2-2. |
| DR-4 Verification robustness | **fail** | Five executable failure scenarios pass materially missing work or mask a real failing step. |
| DR-5 Evidence auditability | pass | Supplied receipts reproduce, all counterexamples are captured under `C:/Temp/av-kit/`, and no destructive packaging run was performed. |
| DR-6 Cross-reference integrity | **fail** | R6-3 can leave the canonical hub contradictory; R6-5 diverges from the completion-preflight contract it cites. |
| DR-7 Evidence freshness | pass | Fresh runs reproduce 11 oracle families, 18 sections, 214 sweeps, 755 dispositions, and exact 22-AC membership. |
| DR-8 Completion vs residual risk | pass | Plan/task remain draft/unstarted and make no implementation-complete claim. |

### Commands Executed

All shell commands used RTK routing and redirected all streams to `C:/Temp/av-kit/`; exit codes
were captured before receipt reads. Key Round-6 receipts are `r6-review-census-rerun.txt`,
`r6-review-oracles-rerun.txt`, `r6-review-vplan-rerun.txt`, `r6-review-hub-live.txt`,
`r6-review-ac-exec-receipts.txt`, `r6-review-executables-notstarted.txt`,
`r6-review-adversarial-functions-valid.txt`, `r6-review-smoke-synthetic-valid.txt`, and
`r6-review-runner-inverse-canonical.txt`. `assert-packaging-clean.ps1` was not run without
`-SelfTest`/`-SkipBuild`; no product implementation gate was run against missing planned files.

### Follow-up Actions

1. Replace the entrypoint terminal-string heuristic with a reachability proof that rejects the
   three demonstrated terminating predecessors; reconcile the correction log.
2. Give row 9 a real smoke producer and bind the receipt to that invocation/run identity.
3. Reject cosmetic hub suffixes and require final-state or explicit replacement semantics.
4. Bind each deferred E2E failure to its own receipt/cause; do not let §9c excuse unrelated §9b.
5. Enforce all canonical reflection sections and per-section substance; add the padded fixture.
6. Add the non-blocking command-head token boundary, rerun all self-tests, the 18-section
   inventory, AC/executable audits, and a correction census for every changed predicate.

### Residual Risk

After the five controls are corrected, real multi-monitor/DPI WinForms behavior, clean
self-contained packaging, Electron launch, same-directory publication on the target filesystem,
and perceptual startup latency remain execution-time risks for xunit, packaging, Playwright, and
the live smoke. The arming scheme's timestamp comparison is adequate against stale artifacts
because arming deletes the prior file; it does not need a stricter-than equality check for the
same-timestamp case. None of these execution-time risks justify the current false passes.

### Verdict

`changes_required` — PR-6 is sufficient; R4-3-R5 is resolved; R4-1, N3/N5/N6/N7, and
F2/F5/F6/F7/F8 remain resolved; the AC set is exactly 22 and every validation executable exists.
Five evidence-backed High findings remain: incomplete entrypoint reachability, a smoke gate with
no producer, cosmetic hub reconciliation, cross-step E2E failure masking, and a reflection gate
weaker than its cited canonical contract. Do not enter execution.

---

## Round 6 Corrections — Implementor Response (PR-6 census + per-finding disposition)

> **Author:** implementing agent (Claude Opus 5, Claude Code). This section is a **correction
> log, not a verdict** — the self-review prohibition in AGENTS.md §Execution Contract stands, and
> no `approved` verdict is authored here. All five Round 6 blocking findings and the one
> non-blocking finding were treated as blocking and corrected in the order the Round 6 Follow-up
> Actions list gives them. The plan remains in PLANNING; no production code, no C# file, and no
> deletion of the Chromium overlay path has been written.

### What was corrected (Round 6 findings R6-1 … R6-5 + NB-1)

| # | Finding | Correction landed |
|---|---------|-------------------|
| R6-1 | The entrypoint binding gate proved *presence*, not *reachability*: `Environment.Exit(0);`, `Environment.FailFast(null);`, and a label-form terminator each kill the seam while leaving the required call textually top-level and after no listed terminal form. | `BINDING_TERMINAL_FORMS` extended to `return`, `throw`, `goto`, `Environment.Exit(`, `Environment.FailFast(`, plus label-form terminators; the textual predicate is now backed by a **real control-flow proof** rather than trusted alone. Three new Roslyn tests are pinned by `BINDING_RUNTIME_TEST_ANCHORS`: `EntryPoint_Seam_Is_Reachable_By_ControlFlowAnalysis` (`CSharpCompilation.Create` → `GetSemanticModel` → `AnalyzeControlFlow(...).StartPointIsReachable` must be `true`), `Production_Sources_Report_No_Unreachable_Code` (`GetDiagnostics` must contain no `CS0162`), and `Terminating_Predecessors_Make_The_Seam_Unreachable` (a negative fixture carrying `Environment.Exit(`, `Environment.FailFast(` and a `stop:` label must be rejected). Anchors are required per test, so four correctly-named empty methods still fail. |
| R6-2 | **Row 9 armed and judged, but nothing ever ran.** The chain was `typecheck → lint → arm-run.ps1 -Name live-smoke → assert-smoke-disposition.ps1`. Every binding the gate enforces was therefore satisfiable by *typing* a two-line receipt — the reviewer passed the row by hand. | New producer `run-live-smoke.ps1` (`SMOKE_PRODUCER`), the row's launch step and the missing half of the producer/judge pair. It arms the run, reads the per-run `run_id` the stamp minted, exports it as `AVKIT_SMOKE_RUN_ID`, writes the receipt header (command signature + `smoke_run_id=<id>`), and launches `SMOKE_COMMAND` with **all** streams appended to `SMOKE_RECEIPT_FILE`. `arm-run.ps1` now mints that GUID (`run_id=` in the stamp; new oracle **A4**), `lib-disposition.ps1` gains the single owner `Get-RunId`, and `assert-smoke-disposition.ps1` requires the receipt to carry `smoke_run_id=<this run's id>` in anchored form. Row 9's validation chain and artifact list were rewired to the producer. |
| R6-2 (scope) | — | The run-id requirement is deliberately scoped to the **`BLOCKED=no`** path. Demanding a producer receipt on the blocked path would re-create the R5-2 defect in reverse by making the `[B]` route unreachable — the very condition a `[B]` is allowed for is the app failing to launch. Oracle **D18** pins that: `BLOCKED=yes` with a complete evidence bundle and **no** run id is still excused. |
| R6-3 | Hub reconciliation accepted a cosmetic suffix — appending a word to a `desktopCapturer`/`overlay` line satisfied the predicate without the line being rewritten. | `HUB_REQUIRED_LINES` now pins the reconciled line texts **verbatim** (oracles **H6**/**H7**), so a suffixed original fails and only a real rewrite passes. The live gate correctly **still exits 1** today (`docs/BUILD_PLAN.md` is edited during EXECUTION, not planning): `hub does not carry the required reconciled line verbatim - a cosmetic edit is not a rewrite`. That failure is the gate working, and it is what task row 8 must clear. |
| R6-4 | §9c's deferred failure could be excused by an adjudication that only proved *some* disposition was blocked — one step's `[B]` masked an unrelated step's red run. | `Resolve-DeferredExcuse` in `lib-disposition.ps1` binds **each** deferred step to its own receipt and cause; a step is excused only when the disposition that names *that* step records an evidenced `BLOCKED=yes`. Oracles **J1–J6** cover cross-step masking, missing binding, and the positive path. |
| R6-5 | The reflection gate restated a section list that lives in `docs/execution/reflections/TEMPLATE.md`, so the two could drift (a PR-9 duplicated-ownership defect). | `assert-reflection-quality.ps1` now **derives** its required-section contract from the template at run time; the template is the single owner. Oracles **F0–F9**, including a padded fixture that is structurally complete but prose-thin. |
| NB-1 (non-blocking) | `Test-ScriptSegment` matched the head command with a bare `StartsWith`, so `playwright test-does-nothing …` counted as `playwright test`. | The head must now be followed by whitespace or end-of-segment (an anchored `[regex]::Escape($Head)` followed by `(\s|$)`). New oracle **S6e** pins the impostor. |

### Correction-log reconciliation (Follow-up Action 1, second clause)

The Round 5 correction-log row for **R4-2-R5** claimed `Environment.Exit(` was among the terminal
forms landed in round 5. It was not — round 5 shipped `return`/`throw`/`goto`, which is precisely
why R6-1 was still exploitable. That row has been corrected in place above, with the false claim
named rather than quietly deleted.

### Evidence (P0 redirect pattern; every receipt under `C:/Temp/av-kit/`)

| Gate | Result |
|---|---|
| `run-live-smoke.ps1 -SelfTest` | `PASS: SMOKE_PRODUCER self-test (S1 header satisfies every gate marker, S2 command head is not hollow, S3 run-id line matches the gate's anchored form, S4 SMOKE_PRODUCER names this file, S5 arming step present)` |
| `arm-run.ps1 -SelfTest` | `PASS: RUN_ARM self-test (A1 deleted artifact, A3 stale artifact rejected; A2 fresh artifact accepted; A4 stamp carries a run id)` |
| `assert-smoke-disposition.ps1 -SelfTest` | `PASS: SMOKE_DISPOSITION self-test (… D15 unregistered follow-up, D16 hand-authored receipt, D17 foreign run id all rejected; D18 blocked path stays reachable without a producer run id)` |
| `assert-e2e-wired.ps1 -SelfTest` | `PASS: E2E_WIRED self-test (… S6e head-prefix impostor …)` |
| `assert-oracle-selftests.ps1` | `PASS: ORACLE_SELFTESTS 13 gates proven non-vacuous` (exit 0) |
| `assert-verification-plan.ps1` | `PASS: VERIFICATION_PLAN inventory (18 sections, every gate script present)` |
| `assert-task-rows.ps1` | `PASS: TASK_ROW_GATE self-test (T1…T11)` |
| `assert-build-plan-hub.ps1` (live) | exit `1` **by design** — the hub is reconciled during EXECUTION (task row 8), and R6-3's verbatim-line requirement is what makes that row real work. |

`SMOKE_DISPOSITION` gained three oracles this round: **D16** (the reviewer's exact hand-authored
two-line receipt → rejected), **D17** (a receipt bearing a foreign run id → rejected), **D18**
(the positive `[B]`-reachability case above).

### PR-6 blast-radius census

`census-round6-corrections.ps1` (self-enforcing; `exit 3` on any stale site) sweeps every value
this round changed, in three directions (`old` / `new` / `carry`) across two scopes (PAIR =
plan + task, FOLDER = the whole plan folder), logging one disposition row per hit.

```
CENSUS COMPLETE - values swept: 89 x 2 scopes = 178 sweeps
disposition rows (FOLDER scope, one per hit): 665
disposition log written to: C:/Temp/av-kit/census-p9-native-picker-round6-disposition.md
worst rg exit code: 0  (0/1 are normal; >1 would be an IO error)
STALE SITES: 0
census_exit=0
```

Receipt: `C:/Temp/av-kit/census-p9-native-picker-round6.txt`.
Per-hit log: `C:/Temp/av-kit/census-p9-native-picker-round6-disposition.md`.

Two census findings were fixed rather than argued away:

1. The `old`-direction sweep for `arm-run.ps1 -Name live-smoke` flagged `run-live-smoke.ps1:4` —
   the producer's own header, which quotes the defective chain. Retained with the justification
   that *stating* the old chain is finding R6-2 itself, not a residue of it; the sweep was not
   weakened.
2. `A1–A3` / `D1–D15` were first declared with ASCII hyphens while the documents use en dashes,
   which would have made those sweeps vacuous. Corrected to en-dash forms, after which the
   `A1–A3` sweep found a real site (`implementation-plan.md` line 300) and it was rewritten to
   cite `A1`/`A2`/`A3` individually.

### Plan deltas this round

- **New file:** `run-live-smoke.ps1` (`SMOKE_PRODUCER`).
- **New AC:** `AC-40.23` — Electron main emits `smoke_run_id=<AVKIT_SMOKE_RUN_ID>` at startup and
  `picker_startup_ms=<n>` when the picker window appears (source label: `Local Canon`).
  `AC_COUNT` / `AC_IDS` updated to **23**; the AC-count gate agrees.
- **New gate-table rows:** `SMOKE_PRODUCER`, `VERIFICATION_ADJUDICATION`. The oracle battery is
  now **13 gates**.
- **Modified:** `arm-run.ps1` (run-id minting), `lib-disposition.ps1` (`Get-RunId`),
  `assert-smoke-disposition.ps1` (run-identity binding, D16–D18), `assert-e2e-wired.ps1` (S6e),
  `task.md` row 9 (producer + rationale), `implementation-plan.md` (14 anchored edits).

### Why no extra "row 9 must call the producer" gate was added

The binding is already enforced dynamically: removing the producer from row 9 leaves **no fresh
receipt at all**, so `SMOKE_DISPOSITION` fails on freshness before it ever reaches the run-id
check. A static grep asserting that row 9's text mentions the producer would be a weaker,
type-able restatement of a check the runtime already makes — exactly the PR-9 duplicated-ownership
pattern this plan has been removing.

### Requested next action

Round 7 review of the corrected plan pair. The implementing agent has not authored and will not
author a verdict; execution remains blocked pending an external `approved` **and** a fresh
`USER_EXPLICIT` instruction (Claude Code is `plan_to_exec_gate == human`).

## Round 7 — Corrections Re-Review

### Intent Anchor

Executing this plan is supposed to revise the Phase 9/7 SSOTs, replace the Chromium F2 overlay
with a packaged .NET 8 WinForms region-picker sidecar, delete the old overlay with no fallback,
and preserve the Python `mss`, REST, and MCP surfaces. The current plan still cannot reliably
prove that objective: three correction-era controls accept materially missing or contradictory
deliverables.

### PR-6 Evidence Adjudication

PR-6 is **sufficient; substantive review proceeded**. Re-running
`census-round6-corrections.ps1` produced 89 declared values across PAIR and FOLDER scopes (178
fixed-string sweeps), 665 FOLDER dispositions, `STALE SITES: 0`, and exit 0
(`C:/Temp/av-kit/round7-census-rerun.txt`). The unfiltered receipt has 1,388 lines; the linked
disposition log has 667 lines (two headers plus one row for each of the 665 hits). The script uses
`rg -F`, treats rc 0/1 correctly, rejects undeclared surviving `old` sites with exit 3, and records
the two corrected census defects and the justified retained producer-header mention
(`census-round6-corrections.ps1:6-30`, `:47-54`, `:196-225`, `:242-269`; rolling log
`:3242-3269`). The rolling correction section links both raw and disposition receipts and gives a
per-finding correction account (`:3197-3216`).

### Round 6 Finding Dispositions and Regression Check

| Finding | Disposition | Current file evidence |
|---|---|---|
| R6-1 | `partially_resolved` | The terminal census now covers `Environment.Exit(` / `Environment.FailFast(` and labels, while legitimate guarded exits remain accepted (`named-sets.json:97-103`; `assert-picker-binding.ps1:225-247`, `:439-459`, `:479-492`). However, `Test-RuntimeSuite` retains strings and accepts anchors by substring (`assert-picker-binding.ps1:67-69`, `:294-315`). The Round-7 decoy probe supplied seven passing xunit methods containing the required words only in strings/trivial assertions and was accepted without one Roslyn call (`C:/Temp/av-kit/round7-adversarial-probes.txt`). |
| R6-2 | `unresolved` | The producer exists and launches the declared command (`run-live-smoke.ps1:84-114`), but it writes `smoke_run_id=<id>` itself before launch (`:97-100`), while AC-40.23 says that line proves Electron emitted it and is never hand-written (`implementation-plan.md:239`). The gate merely searches for that line (`assert-smoke-disposition.ps1:104-120`). A hand-authored receipt using the readable current stamp id passed the real predicate in the Round-7 probe. Task row 7 assigns no AC-40.23 implementation and row 9 is tester-owned with deliverable AC-40.15/40.19 only (`task.md:49`, `:52`). |
| R6-3 | `resolved` | All four current hub replacements are pinned verbatim (`named-sets.json:371-375`), every additional forbidden-token line is still scanned, and the only exemption requires both replacement and retirement language (`assert-build-plan-hub.ps1:40-82`). H6/H7 reject cosmetic and unframed coexistence (`:105-115`); the live hub still fails as required. |
| R6-4 | `partially_resolved` | Both deferred steps declare their own receipt and J6 checks that totality (`run-verification-plan.ps1:59-61`, `:98-103`). But `Resolve-DeferredExcuse` only asks whether the blocker signature occurs anywhere in the receipt (`lib-disposition.ps1:107-126`). A 9b receipt containing both the display signature and an unrelated HTTP regression was excused by the Round-7 probe. |
| R6-5 | `resolved` | Required headings are derived from the canonical template; missing template/no headings fail closed; every derived section has a per-section floor, plus placeholder, filler, and Instruction Coverage checks (`assert-reflection-quality.ps1:57-77`, `:146-203`). F0-F9 passed. Editing the canonical template intentionally changes the canonical contract; that is not drift between two owners. |
| NB-1 | `resolved` | The head command now requires whitespace/end-of-segment and S6e rejects `playwright test-does-nothing` (`assert-e2e-wired.ps1:121-151`, `:362-365`). |
| R4-1 | `resolved; not regressed` | Positive last-cell task-status parsing remains non-vacuous; T1-T11 passed in the 13-gate oracle battery. All 26 executable task rows remain `[ ]`. |
| R4-3-R5 | `resolved; not regressed` | Arming still deletes the artifact, stamps it, and mints a fresh id; A1-A4 passed (`arm-run.ps1:25-55`). Re-arming invalidates a prior receipt/id. |
| N3 / N5 / N6 / N7 | `resolved; not regressed` | Exact packaging composition remains in task row 5; the Round-6 census is complete; the single runner inventories exactly 18 scheduled sections while the manual smoke producer remains deliberately outside that schedule (`run-verification-plan.ps1:44-63`, `:110-124`); the latency follow-up remains evidence-triggered `out-of-scope`, not a fake deferred MEU (`implementation-plan.md:306-317`). |
| F1-F8 | `resolved; not regressed at their original contracts` | The task-row, production handler/controller, clean packaging, same-directory rename, RED-oracle, named threshold, and named exit-code corrections remain (`task.md:44-50`; `implementation-plan.md:180-191`; `named-sets.json:11-24`). F2 specifically invokes only existing gates/tools and includes the current reflection/smoke checks (`assert-closeout.ps1:10-60`). R7-1 is a later executed-reachability proof defect, not a return to F3's original absence of a handler/controller seam. |

### New Findings

| # | Severity | Confidence | Finding | Evidence and concrete failure scenario |
|---|---|---|---|---|
| R7-1 | High | High | **PR-8 / DR-4 — the “executed Roslyn proof” is still a substring proof.** The production plan requires genuine semantic control-flow analysis, but the source gate keeps string literals and checks only `IndexOf` anchors inside named method bodies. | `assert-picker-binding.ps1:67-69`, `:294-315`; `named-sets.json:122-174`; AC-40.20 at `implementation-plan.md:224`. The reproduced decoy has seven green xunit methods whose bodies contain the anchor words in strings plus `Assert.True(true)` / `Assert.False(false)` / an empty-array assertion. `Test-RuntimeSuite` returned success despite no `CSharpCompilation`, semantic model, or control-flow invocation (`C:/Temp/av-kit/round7-adversarial-probes.txt`). Thus an unreachable shipped seam plus a hollow seven-test suite can pass §5b/§5c. |
| R7-2 | High | High | **PR-1 / PR-8 / PR-9 / DR-1 — AC-40.23 has two conflicting producers, no first-painted-frame call chain, and no implementation task.** | The wrapper pre-seeds the exact `smoke_run_id` line before starting npm (`run-live-smoke.ps1:97-108`); the gate cannot distinguish it from app output (`assert-smoke-disposition.ps1:104-120`); AC-40.23 claims Electron owns the line and that it is unforgeable (`implementation-plan.md:239`). The helper contract exposes exit/PNG only, not a first-painted readiness signal (`implementation-plan.md:169-178`), and task row 7 does not implement either smoke marker (`task.md:49`). Reading the current id from the stamp and typing command + matching id + latency after arming passed the predicate without producer or app (`round7-adversarial-probes.txt`). Therefore deleting the producer from row 9 is not dynamically detected once a receipt is supplied, and BLOCKED=yes is even less bound because it omits the id check. |
| R7-3 | High | High | **PR-8 / DR-4 — per-step signature presence still launders mixed-cause failures.** | `Resolve-DeferredExcuse` returns success when the disposition signature appears anywhere in the failing step receipt (`lib-disposition.ps1:107-126`). Section 9b is the full E2E suite and is deferred to 9d (`run-verification-plan.ps1:59-61`). A receipt containing both `Missing X server` and an unrelated `POST /captures` 500 was excused in the reproduced probe. J1 only covers a receipt with no blocker signature (`run-verification-plan.ps1:78-85`), so one real blocker still masks an additional regression in the same run. |

No Critical findings were identified.

### Checklist Verdicts

| Check | Verdict | Evidence |
|---|---|---|
| PR-1 Plan/task alignment | **fail** | AC-40.23 is a product instrumentation requirement but has no coder task; row 9 only consumes evidence (R7-2). |
| PR-2 Not-started confirmation | pass | `Program.cs`, `BindingReachabilityTests.cs`, the new E2E spec, and `capture-picker.ts` are absent; old overlay files remain; all 26 executable task rows are open (`C:/Temp/av-kit/round7-not-started.txt`, `round7-task-status.txt`). |
| PR-3 Task contract completeness | pass | Every executable row has task, owner, deliverable, exact validation, dependencies, outputs, and status. |
| PR-4 Validation realism | **fail** | R7-1 through R7-3 are reproduced material false-passes. |
| PR-5 Source-backed planning | pass | Product decisions and added acceptance rules use Spec, Local Canon, Research-backed, or Human-approved labels. |
| PR-6 Corrections readiness | pass | Complete rerunnable census plus 665 per-hit dispositions and correction log, adjudicated above. |
| PR-7 Scope discipline | pass | No `deferred` row lacks a registered MEU. Each `out-of-scope` row has a real Human-approved, build-plan, approved-MEU, or Research-backed basis (`implementation-plan.md:306-317`); the warm-process item is explicitly evidence-triggered rather than pre-deferred. |
| PR-8 Reachability / totality | **fail** | R7-1 lacks semantic proof, R7-2 lacks a unique observable producer/call chain, and R7-3 is not total over multiple causes in one receipt. Closed-world helper outcomes and open-world unknown exits otherwise fail closed. |
| PR-9 Single-statement discipline | **fail (material)** | Named sets own ordinary constants, but `smoke_run_id` has two live emitters with conflicting evidence meaning (wrapper header vs. claimed Electron observable), so no single owner governs the predicate (R7-2). |
| DR-1 Claim-to-state match | **fail** | AC-40.23's “app emitted/unforgeable” claim contradicts `run-live-smoke.ps1:97-100`; the runner's “one blocker never launders another regression” claim is disproved by R7-3. |
| DR-2 Residual old terms | pass | Round-6 fixed-string census reports zero undeclared stale sites. |
| DR-3 Downstream references | pass | Spec, hub, registry, package, Vite, overlay deletion, tests, handoff, reflection, and review surfaces remain inventoried. |
| DR-4 Verification robustness | **fail** | Three reproduced false-pass inputs can close materially missing reachability, smoke, or regression evidence. |
| DR-5 Evidence auditability | pass | Commands, receipts, named files, and all task validation executables are reproducible; every referenced script/tool and `rtk`/`pwsh`/`npm`/`dotnet`/`uv` exists (`round7-task-executable-audit.txt`). |
| DR-6 Cross-reference integrity | **fail** | AC-40.23, the wrapper, the gate, and task ownership disagree; 9b's prose overstates the resolver's cause totality. |
| DR-7 Evidence freshness | pass | The 13-gate battery and 18-section inventory were rerun; the expected live hub failure was reproduced. AC set is exactly 23 unique rows = `AC_COUNT` 23 = 23 `AC_IDS` (`round7-ac-audit.txt`). |
| DR-8 Completion vs residual risk | pass | The artifacts remain draft/open and make no implementation-complete claim. |

AC totality is mechanically consistent: 23 unique AC rows exactly equal `AC_COUNT` and `AC_IDS`.
All ACs map through task ranges or Verification Plan sections; AC-40.23 reaches §10, but its
absence from an implementation row is the delivery defect in R7-2 rather than a count mismatch.
All validation executables in `task.md` exist. The prompt's shorthand
`assert-verification-plan.ps1` does not exist, but the plan correctly and consistently uses the
existing `run-verification-plan.ps1`; this is not a plan finding.

### Commands and Evidence

- PR-6 census rerun: `C:/Temp/av-kit/round7-census-rerun.txt`.
- Gate reruns (13 oracle gates, producer, smoke, E2E wiring, 18-section inventory, expected hub
  exit 1): `C:/Temp/av-kit/round7-gate-reruns.txt` and `round7-arm-selftest.txt`.
- Adversarial false-pass probes: `C:/Temp/av-kit/round7-adversarial-probes.txt`.
- AC/count/reachability census: `C:/Temp/av-kit/round7-ac-audit.txt`.
- Executable/path audit and not-started proof: `C:/Temp/av-kit/round7-task-executable-audit.txt`,
  `round7-not-started.txt`, and `round7-task-status.txt`.

### Follow-up Actions

1. Replace substring anchoring for AC-40.20 with a structural Roslyn-test gate or another
   executed oracle that proves the named methods actually invoke the semantic APIs and assert on
   their returned control-flow/diagnostic values; add the reproduced string-decoy suite as a
   negative oracle.
2. Give AC-40.23 an implementable producer chain and coder-owned RED/GREEN task. Use distinct
   wrapper-started and app/helper-ready markers; do not pre-seed the app-owned marker. Define how
   first-painted readiness crosses from WinForms to Electron (or revise the metric to an actually
   observable event), bind row 9 statically to `SMOKE_PRODUCER`, and reject a hand-written current-id
   receipt on both success and blocked paths while preserving real launch-failure evidence.
3. Make deferred-step adjudication total over all failures in each receipt. The simplest safe fix
   is to keep 9b blocking; otherwise give 9b its own structured report/disposition and prove every
   unexpected failure is attributable to the evidenced blocker. Add the mixed blocker + unrelated
   regression probe as an oracle.

### Residual Risk

After these plan defects are corrected, real multi-monitor/PerMonitorV2 behavior, GDI capture,
self-contained packaging, real Electron launch, and perceptual cold-start latency remain
execution-time risks. They are not reasons to broaden scope or withhold approval once the plan's
controls genuinely prove their stated contracts.

### Verdict

`changes_required` — three High, evidence-backed findings remain. The architecture and scope are
coherent, PR-6 is satisfied, and R6-3/R6-5/NB-1 are resolved, but the reachability suite, smoke
identity/latency chain, and deferred E2E adjudication can still false-pass materially missing work.

---

## Round 7 Corrections — Implementor Response (PR-6 census + per-finding disposition)

> **Author:** implementing agent (Claude Opus 5, Claude Code). This section is a **correction
> log, not a verdict** — the self-review prohibition in AGENTS.md §Execution Contract stands and
> no `approved` verdict is authored here. All three Round 7 findings were treated as blocking and
> corrected in the order the Round 7 Follow-up Actions list gives them. The plan remains in
> PLANNING: no production code, no C# file, and no deletion of the Chromium overlay path has been
> written.

### What was corrected (Round 7 findings R7-1, R7-2, R7-3)

| # | Finding | Correction landed |
|---|---------|-------------------|
| R7-1 | AC-40.20's reachability suite was anchored by substring against a comment-stripped but **literal-preserving** body, so seven correctly-named methods whose entire substance was one quoted string passed the gate. The reviewer built that decoy and it went green. | The anchor set is **split by what each anchor must prove**. Fixture anchors (`"if (false)"`, `"return 1;"`, source paths) *are* string literals, so they keep the literal-preserving view; the new `BINDING_RUNTIME_INVOCATION_ANCHORS` are matched against `Remove-CommentsAndLiterals`, so a quoted `CSharpSyntaxTree.ParseText(` no longer counts — the rejection reads *"outside string literals - quoting the API is not calling it"*. Bodies are now located from the method **signature** (`Get-TestBody`) rather than a name substring, and `Test-AssertsOnAnalysis` adds a dataflow-lite check: every `Assert.*` argument must be an invocation anchor or a name transitively derived from one, so running the analysis and then asserting an unrelated value is rejected. Oracles **B10** (the reviewer's seven-method quoted-API decoy, generated by looping `BINDING_RUNTIME_TEST_NAMES`), **B11** (`Assert.Empty(new int[0])` after a real `GetDiagnostics()` call), **B12** (an emptied invocation-anchor set fails rather than passing vacuously). |
| R7-2 | Two false passes in the smoke-identity chain: the arming stamp **disclosed the run id in plaintext**, so a receipt could be typed from it; and `smoke_run_id` had two possible writers, so the wrapper's own line was read as proof the *app* ran. AC-40.23 also had no owning implementation row. | The stamp now stores **only** `RUN_ID_HASH_KEY` (`run_id_sha256`) and the raw id leaves `arm-run.ps1` on stdout under `-EmitId`, so no file discloses the value a receipt must carry (`Get-Sha256Hex`, `Test-RunIdMatchesStamp`; oracles **A4** stamp carries *this* id's hash, **A5** stamp discloses no plaintext id). The single key became two with **one owner each** — `SMOKE_WRAPPER_RUN_ID_KEY` written by the producer, `SMOKE_APP_RUN_ID_KEY` written only by Electron (producer oracles **S6**/**S7** prove the producer never writes the app-owned marker and that the two are distinct). `BLOCKED=no` requires both with equal ids; **both** paths require the wrapper marker to hash-match this run's stamp, which is what finally binds the `[B]` path to a real launch attempt. Readiness became observable: `PICKER_READY_MARKER` is written from the picker form's first-shown handler, and `AC-40.24` gates it with an eighth Roslyn test, `Ready_Marker_Is_Written_From_The_First_Shown_Handler` — a marker relocated into `Main`'s prologue times nothing and now fails a gate rather than the reviewer's eye. `TASK_ROW_REQUIRED_TOKENS`/`Test-RowTokens` bind row 9 to its producer statically (**T12**/**T12b**), and AC-40.23 gained its owning implementation row. Oracles **D19–D22** each assert the rejection **message**, so a check that moves elsewhere cannot leave the oracle green. |
| R7-3 | Deferred-step adjudication proved the blocker signature appeared **somewhere** in the receipt. A receipt carrying both the no-display blocker *and* an unrelated `expected 200, received 500` regression was therefore excused — one evidenced `[B]` masked an independent failure. | Adjudication is now **total in both directions**. `Resolve-DeferredExcuse` walks every failure-**cause** line matched by `E2E_FAILURE_CAUSE_PATTERNS` and refuses the excuse unless *each* carries the dispositioned signature (**J7** — the reviewer's exact mixed receipt, refused, with a pattern-less baseline call in the same oracle proving the parameter is what changes the verdict). The converse hole is closed too: a receipt that admits to failures via `E2E_FAILURE_INDICATOR_PATTERNS` while exposing **no** attributable cause is refused rather than trusted (**J9**). **J8** pins the boundary that keeps the evidenced `[B]` reachable — a `3 failed` summary is a count, not a cause, so a genuinely blocked run stays excusable; treating it as a cause would re-create the R5-2 defect. **J10** fails when either pattern set is empty. |

### Divergence on Follow-up Action 3 (recorded, not silent)

Action 3 offered two fixes and ranked *"keep 9b blocking"* first. This plan takes the **second**
option, and the reason is a design decision rather than an omission — it is now recorded in three
places (the runner header, the plan's §9b row, and `task.md` row H1-2) rather than left implicit:

Making 9b block unconditionally does not remove the excuse, it **relocates it upward to an
unadjudicated one**. On a display-less runner the E2E fails, H1-2 fails, and the row closes with a
prose `[B]` that no gate inspects. AGENTS.md already fixes the *outcome* — an un-run E2E in the
sandbox is `[B]` + CI follow-up, not a completion blocker — so the only open question is **where**
the excuse is adjudicated. A per-step excuse bound to a fresh receipt, a dispositioned signature,
and now cause totality is a strictly stronger place than a sentence in a task row. The mixed
blocker + unrelated-regression probe that Action 3 asked for was added as oracle **J7** either way.

### Evidence (P0 redirect pattern; every receipt under `C:/Temp/av-kit/`)

| Gate | Result |
|---|---|
| `assert-picker-binding.ps1 -SelfTest` | `PASS: PICKER_BINDING self-test (B1 … B9/B9b flow-blind suite, B10 quoted-API decoy, B11 analysis-without-derived-assertion, B12 empty invocation-anchor set, E1 no-RegionForm, E2 no-Run rejected; E3 guard-block, E4 lambda-block, E5 valid suite, B8d guarded-exit accepted; R1 zero-match, R2 failing, R3 empty, R4 short-match rejected)` |
| `run-verification-plan.ps1 -SelfTest` | `PASS: VERIFICATION_ADJUDICATION self-test (J1 … J7 mixed blocker+regression receipt refused where the pattern-less baseline excuses it; J8 blocked receipt with a "3 failed" summary still excused; J9 unattributable receipt refused; J10 pattern sets non-empty)` |
| `assert-smoke-disposition.ps1 -SelfTest` | `PASS: SMOKE_DISPOSITION self-test (… D19 receipt typed from the value the stamp discloses, D20 wrapper marker without the app-owned one, D21 app marker from another run, D22 unbound [B] receipt all rejected; D18 a real launch failure with the producer's header stays excusable)` |
| `arm-run.ps1 -SelfTest` | `PASS: RUN_ARM self-test (A1 deleted artifact, A3 stale artifact rejected; A2 fresh artifact accepted; A4 stamp carries THIS id's hash; A5 stamp discloses no plaintext id)` |
| `run-live-smoke.ps1 -SelfTest` | `PASS: SMOKE_PRODUCER self-test (S1 … S6 this script never writes the app-owned marker, S7 the two markers are distinct)` |
| `assert-task-rows.ps1 -SelfTest` | `PASS: TASK_ROW_GATE self-test (T1 … T12/T12b producer-token binding enforced, missing row not vacuous)` |
| `assert-oracle-selftests.ps1` | `PASS: ORACLE_SELFTESTS 13 gates proven non-vacuous` (exit 0) — receipt `C:/Temp/av-kit/r7-oracles.txt` |
| `run-verification-plan.ps1` inventory | `PASS: VERIFICATION_PLAN inventory (18 sections, every gate script present)` |
| `assert-build-plan-hub.ps1` (live) | exit `1` **by design** — the hub is reconciled during EXECUTION (task row 8). |

### PR-6 blast-radius census

`census-round7-corrections.ps1` (self-enforcing; `exit 3` on any stale site) sweeps every value
this round changed, in three directions (`old` / `new` / `carry`) across two scopes (PAIR =
plan + task, FOLDER = the whole plan folder), logging one disposition row per hit.

```
CENSUS COMPLETE - values swept: 86 x 2 scopes = 172 sweeps
disposition rows (FOLDER scope, one per hit): 665
disposition log written to: C:/Temp/av-kit/census-p9-native-picker-round7-disposition.md
worst rg exit code: 0  (0/1 are normal; >1 would be an IO error)
STALE SITES: 0
EXIT=0
```

Receipt: `C:/Temp/av-kit/census-round7.txt`. Per-hit log:
`C:/Temp/av-kit/census-p9-native-picker-round7-disposition.md`. A vacuity audit over the receipt
(`C:/Temp/av-kit/r7-vacuity.txt`) confirms **zero** FOLDER-scope sweeps returned no match, so no
declared value was swept for a string that does not exist.

The census's first run **failed with `STALE SITES: 4`, and the stale text was real, not a
declaration artifact.** The R7-2 correction had updated the `SMOKE_DISPOSITION` gate row but left
**AC-40.19** still asserting the superseded single-key scheme in the present tense — *"on the
`BLOCKED=no` path must carry `smoke_run_id=<this run's id>`"* — together with an oracle roster
frozen at `D1–D18, A1–A4` and a producer roster at `S1–S5`. All three were rewritten to the
two-key hash-bound scheme and the current rosters (`D1–D22`, `A1–A5`, `S1–S7`), and the round-6
sentence in the gate row was re-tensed so it reads as history rather than as a live requirement.
The two remaining `old`-form hits are the `run-live-smoke.ps1` and `assert-smoke-disposition.ps1`
headers, which *quote* the retired key to state the defect they close; both are declared in
`$RetainedMentions` with that justification rather than the sweep being weakened. As in round 6,
the oracle-roster values were first declared with ASCII hyphens while the documents use en dashes,
which would have made those sweeps vacuous — corrected to en-dash forms, after which they found
the stale roster above.

### Plan deltas this round

- **New AC:** `AC-40.24` — the readiness marker is written from the picker form's first-shown
  handler and is provably reachable there (source label: `Local Canon`). `AC_COUNT` / `AC_IDS`
  updated to **24**; the AC-count gate agrees.
- **New named sets:** `BINDING_RUNTIME_INVOCATION_ANCHORS`, `E2E_FAILURE_INDICATOR_PATTERNS`,
  `TASK_ROW_REQUIRED_TOKENS`, `SMOKE_WRAPPER_RUN_ID_KEY`, `SMOKE_APP_RUN_ID_KEY`,
  `RUN_ID_HASH_KEY`, `PICKER_READY_MARKER` — `named-sets.json` is now **136 keys**.
- **New reachability test pinned by the gate:** `Ready_Marker_Is_Written_From_The_First_Shown_Handler`
  (eighth member of `BINDING_RUNTIME_TEST_NAMES`); the gate's receipt fixtures moved 7 → 8.
- **Modified:** `assert-picker-binding.ps1` (`Get-TestBody`, `Get-CallArgs`,
  `Test-AssertsOnAnalysis`, rewritten `Test-RuntimeSuite`, B10–B12), `lib-disposition.ps1`
  (`Resolve-DeferredExcuse` cause totality + unattributability), `run-verification-plan.ps1`
  (J7–J10 + the recorded 9b design decision), `arm-run.ps1` (hash-only stamp, `-EmitId`, A5),
  `run-live-smoke.ps1` (two markers, S6/S7), `assert-smoke-disposition.ps1` (D19–D22),
  `assert-task-rows.ps1` (`Test-RowTokens`, T12/T12b), `task.md` (rows 3, 9, H1-2),
  `implementation-plan.md` (gate rows, §9b/§9c, AC-40.19, AC-40.24).
- **New file:** `census-round7-corrections.ps1`.

### Requested next action

Round 8 review of the corrected plan pair. The implementing agent has not authored and will not
author a verdict; execution remains blocked pending an external `approved` **and** a fresh
`USER_EXPLICIT` instruction (Claude Code is `plan_to_exec_gate == human`).

---

## Round 8 — Corrections Re-Review

### Intent Anchor

Executing this plan is supposed to revise the Phase 9/7 SSOTs, replace the Chromium F2 overlay
with a packaged .NET 8 WinForms region-picker sidecar, delete the old overlay with no fallback,
and preserve the Python `mss`, REST, and MCP surfaces. The current plan still cannot reliably
prove that objective: four correction-era controls accept materially missing execution evidence,
semantic tests, producer binding, or unrelated E2E regressions.

### PR-6 Evidence Adjudication

PR-6 is **sufficient; substantive review proceeded**. Re-running
`census-round7-corrections.ps1` from the repository root produced the complete 1,351-line receipt,
86 declared values across PAIR and FOLDER scopes (172 fixed-string sweeps), 665 FOLDER-scope
disposition rows, `STALE SITES: 0`, and exit 0 (`C:/Temp/av-kit/round8-census-rerun.txt`). The
separate disposition log contains exactly 189 `updated` plus 476 `confirmed-consistent` rows and
zero other dispositions. `r7-vacuity.txt` reports zero FOLDER-scope zero-hit values. The only
`head|tail|Select-Object|Where-Object` scan hit in the census script is its own line declaring that
the receipt is untruncated, not a truncation operator (`census-round7-corrections.ps1:226`). The
rolling correction log supplies the per-finding account and links both receipts (`rolling review
file:3415-3478`). The first-run AC-40.19 defect is genuinely corrected: the live AC now requires
the wrapper/app two-key hash-bound scheme and the current D1-D22/A1-A5/S1-S7 rosters
(`implementation-plan.md:235`); no other AC row states the retired single-key scheme.

### Round 7 Finding Dispositions and Regression Check

| Finding | Disposition | Current file evidence |
|---|---|---|
| R7-1 | `partially_resolved` | B10 now rejects the all-quoted API decoy, B11 rejects a real analysis followed by an unrelated constant assertion, and B12 prevents an empty invocation set (`assert-picker-binding.ps1:370-405`, `:707-732`). However, non-literal semantic anchors remain in the literal-preserving set, and the dataflow-lite rule accepts any assertion mentioning any derived local (`named-sets.json:142-182`; `assert-picker-binding.ps1:321-364`). The Round-8 weak-suite probe is accepted; R8-1. |
| R7-2 | `partially_resolved` | AC-40.23 now has RED/GREEN ownership in task rows 6/7, AC-40.24 has C# ownership in rows 3/4, success requires distinct equal wrapper/app markers, and blocked evidence requires the wrapper marker (`task.md:44-49`, `:52`; `assert-smoke-disposition.ps1:129-167`). But `arm-run.ps1 -EmitId` exposes the nonce to any caller, and `Test-RowTokens` searches all row prose instead of the Validation cell (`arm-run.ps1:7-10`, `:77-84`; `assert-task-rows.ps1:108-127`). Both bypasses are reproduced in R8-2/R8-3. AC-40.24's gate also accepts a reachable prologue marker with a quoted `Shown` fixture; R8-1. |
| R7-3 | `partially_resolved` | The resolver now checks every line matched by `E2E_FAILURE_CAUSE_PATTERNS`, refuses indicator-only opaque receipts, and retains per-step receipt binding (`lib-disposition.ps1:107-156`; `run-verification-plan.ps1:234-257`). The declared patterns are not total over real failure forms; an unmatched `FAIL ... exited with code 137` rides beside the matched blocker and is excused; R8-4. |
| R6-1 | `partially_resolved; no static regression` | `BINDING_TERMINAL_FORMS` still covers return/throw/goto/Exit/FailFast, label stripping remains live, and B8/B8b/B8c plus B8d pass (`named-sets.json:98-104`; `assert-picker-binding.ps1:227-249`, `:530-550`). The anchor split did not weaken this static predicate, but R8-1 means the executed Roslyn proof can still be hollow. |
| R6-2 / R6-4 | `partially_resolved` | The producer launch and per-step receipt binding remain intact (`run-live-smoke.ps1:115-160`; `run-verification-plan.ps1:82-85`, `:248-257`). R8-2/R8-3 defeat the claimed producer evidence; R8-4 defeats cause totality. |
| R6-3 / R6-5 / NB-1 | `resolved; not regressed` | Hub required lines/retirement framing, template-derived reflection sections, and exact executable-head matching all remain in the 13-gate oracle battery. The live hub still fails as required before execution. |
| R4-1 / R4-3-R5 / N-series / F-series | `resolved at their original contracts; not regressed` | Positive task-status parsing, artifact deletion/freshness, exact packaging composition, same-directory publication, RED gating, 18-section inventory, source-backed scope, and existing gate/tool paths remain present. All 26 actionable rows are open and the planned product/helper/E2E/handoff files remain absent (`C:/Temp/av-kit/r8-not-started.txt`; `round8-oracle-selftests.txt`). The four current findings are later control failures, not reversions to those original omissions. |

### 9b Divergence Adjudication

The plan's choice to keep section 9b machine-dispositioned rather than unconditionally blocking is
**accepted on its merits**. A display-less runner can produce the same evidenced launch signature
in 9b and 9c; binding each failed section to its own fresh receipt and one 9d disposition is
stronger than failing H1-2 and closing it later with unchecked prose. T12/T12b's intended static
row-to-producer check and the dynamic freshness/identity check are complementary, not duplicate
owners: one governs what the task orders, the other what the receipt proves. R8-3 is that the
static check reads the wrong cell scope, and R8-4 is that the selected per-step adjudicator is not
yet total. Neither defect requires making 9b unconditionally blocking. Once those defects are
fixed, the valid no-display `[B]` remains reachable while an unrelated regression remains fatal.

### New Findings

| # | Severity | Confidence | Finding | Evidence and concrete failure scenario |
|---|---|---|---|---|
| R8-1 | High | High | **PR-8 / DR-4 — the split Roslyn anchors and derived-name rule still accept materially hollow AC-40.17/40.20/40.24 tests.** | `BINDING_RUNTIME_TEST_ANCHORS` leaves code-semantic tokens such as `InvocationExpressionSyntax` and `ReturnStatementSyntax` in the literal-preserving set (`named-sets.json:142-182`), while `Test-AssertsOnAnalysis` accepts an assertion that merely mentions any derived local (`assert-picker-binding.ps1:321-364`, `:375-405`). The probe replaces the handler test with a real parse plus `const string quotedType = "InvocationExpressionSyntax"; Assert.NotEmpty(nodes);`, which proves only that the file has syntax nodes. It also leaves `Shown` in a string and selects any reachable statement containing `PICKER_READY_MARKER`, so a `Main`-prologue marker passes without being inside a Shown/paint registration or after a painted frame. The real `Test-RuntimeSuite` accepts the modified eight-test suite (`C:/Temp/av-kit/round8-adversarial-probes.txt`: `BYPASS picker_runtime_suite=accepted`). This contradicts AC-40.20/40.24's stated negative oracles (`implementation-plan.md:226`, `:242`). The five-pass local assignment model can also reject a legitimate collection/field/helper flow it does not model; that over-constraint is non-blocking, but confirms this is not a semantic dataflow proof. |
| R8-2 | High | High | **PR-8 / DR-1 — the hash-bound identity can still be obtained and hand-written without launching the producer or app.** | `-EmitId` is a public switch and prints `RUN_ID <raw id>` to stdout (`arm-run.ps1:7-10`, `:77-84`); nothing restricts callers to `run-live-smoke.ps1`. Once an operator runs that command, the smoke gate checks only that the typed wrapper id hashes to the stamp, the typed app id equals it, and the typed latency line matches (`assert-smoke-disposition.ps1:129-163`). The gate's own positive fixture is a manually written receipt (`:182-213`). The Round-8 probe confirms `arm_emit_id_public=True` and that a hand-typed command/wrapper/app/latency receipt is accepted. Hashing prevents guessing and arming twice invalidates the prior id, but it does not prevent using the supported plaintext-output path. |
| R8-3 | High | High | **PR-4 / PR-8 — T12/T12b do not bind row 9's Validation command to the producer.** | `Test-RowTokens` searches `row.text`, the entire Markdown row (`assert-task-rows.ps1:108-125`). Current row 9 names `run-live-smoke.ps1` repeatedly in its Task prose as well as Validation (`task.md:52`). Replacing only Validation with `npm --prefix ui run dev, then type the receipt` therefore retains a prose token and passes. The actual function returned `task_validation_cell_errors=0` for that adversarial row (`C:/Temp/av-kit/round8-adversarial-probes.txt`). T12 tests only a row from which the token is absent everywhere (`assert-task-rows.ps1:261-283`), so it misses the exact validation-cell drift it claims to prevent. |
| R8-4 | High | High | **PR-8 / DR-4 — cause-pattern totality still launders an unrelated failure whose line shape is unrecognized.** | The cause set recognizes selected `Error:`, assertion-error, expected/received, timeout, and unhandled-exception forms; the indicator set recognizes only numeric failed summaries (`named-sets.json:441-450`). Once at least one recognized cause exists, `Resolve-DeferredExcuse` never asks whether other unmatched failure lines remain (`lib-disposition.ps1:134-156`). A receipt containing the dispositioned `Error: browserType.launch: Missing X server or $DISPLAY` plus `FAIL ui/tests/e2e/capture-picker.test.ts: application exited with code 137` and no numeric summary is excused by the real resolver (`C:/Temp/av-kit/round8-cause-bypass.txt`; `round8-adversarial-probes.txt`: `BYPASS deferred_mixed_receipt=excused`). Blocking 9b would reject this input, but so would a genuinely total structured/per-failure adjudicator; the chosen design need not be abandoned. |

No Critical findings were identified.

### AC, Executable, Scope, and Single-Statement Audits

- The plan contains exactly 24 unique AC rows; `AC_COUNT = 24`, `AC_IDS` contains 24 entries,
  and the set difference is zero (`C:/Temp/av-kit/r8-ac-totality.txt`). AC-40.23 is owned by
  task rows 6/7; AC-40.24 by rows 3/4. Every other AC reaches an implementation/spec/closeout row
  through an explicit id or range and at least one verification section where applicable.
- `pwsh`, `dotnet`, `npm`, and `uv` resolve on PATH. Every existing script/tool/template named by
  task validation exists; planned product/test files are absent but are scheduled deliverables
  (`C:/Temp/av-kit/r8-executables-paths.txt`, `r8-not-started.txt`).
- PR-7 bases are substantive: the build plan contains the Windows-first macOS/Linux and
  in-overlay-annotation deferrals, the FastAPI/`mss` boundary, the ShareX GDI source map, and NSIS
  distribution basis; MEU-37/38 exist in the SSOT. The warm-process row is evidence-triggered
  `out-of-scope`, not an unscheduled deferred MEU.
- AC-40.19, task row 9, the smoke gate, and named sets agree on the two-key scheme. The retired
  `smoke_run_id=` occurrences survive only in defect-history headers/census declarations and are
  justified by the retained-mention allowlist. No other repeated-literal cluster has two live,
  materially different contracts. T12 static instruction binding and dynamic receipt binding do
  not violate PR-9 single ownership.

### Checklist Verdicts

| Check | Verdict | Evidence |
|---|---|---|
| PR-1 Plan/task alignment | pass | Both artifacts retain MEU-40 in the same WP/task order, with spec, helper, Electron integration, overlay deletion, packaging, E2E/smoke, hub, handoff/review, and closeout outputs. AC-40.23/40.24 now have coder rows. |
| PR-2 Not-started confirmation | pass | Native helper/test/stub, `capture-picker.ts`, the new E2E spec, implementation handoff, and implementation review are absent; all task rows remain open. |
| PR-3 Task contract completeness | pass | Every actionable row carries Task, Owner, Deliverable, exact Validation, dependencies, context strategy, durable outputs, builder model, and Status. |
| PR-4 Validation realism | **fail** | R8-1, R8-3, and R8-4 demonstrate false-passing validation; R8-2 defeats the smoke evidence path. |
| PR-5 Source-backed planning | pass | AC and scope decisions use Spec, Local Canon, Research-backed, or Human-approved bases. |
| PR-6 Corrections readiness | pass | Complete untruncated 172-sweep receipt, 665 per-hit dispositions, correction log, and zero-vacuity audit. |
| PR-7 Scope discipline | pass | Every out-of-scope row has a real Human-approved, build-plan, approved-MEU, or Research-backed basis; no `deferred` row lacks a registered MEU. |
| PR-8 Control reachability / totality | **fail** | R8-1 can close hollow semantic/readiness tests, R8-2/R8-3 can close a hand-authored smoke path, and R8-4 excuses an unmatched independent E2E failure. Closed/open-world exit mapping and same-directory rename atomicity otherwise remain explicit. |
| PR-9 Single-statement discipline | pass | Named sets remain the executable owners of constants/sets; current plan/task uses are consistent. Static row-order binding and dynamic receipt provenance are distinct controls, not competing definitions. |
| DR-1 Claim-to-state match | **fail** | The correction log's smoke proof claim overstates a public `-EmitId` path, and the readiness gate does not establish its claimed handler/paint ancestry. |
| DR-2 Residual old terms | pass | The rerun reports zero undeclared stale sites; retired single-key/old-roster mentions are historical declarations or allowlisted defect text. |
| DR-3 Downstream references | pass | Spec/hub/registry/package/Vite/deletion/tests/handoff/reflection/review surfaces remain inventoried. |
| DR-4 Verification robustness | **fail** | Four concrete probes false-pass current controls. |
| DR-5 Evidence auditability | pass | Review and planned commands name reproducible receipts and executable paths; the defects concern verdict semantics, not missing evidence locations. |
| DR-6 Cross-reference integrity | **fail** | The prose says readiness is handler/paint-bound and every E2E cause is adjudicated, while the executable anchor/pattern sets permit counterexamples. |
| DR-7 Evidence freshness | pass | Census, 13-gate oracle battery, 18-section inventory, executable audit, AC count, and expected live hub failure were reproduced from current disk state. |
| DR-8 Completion vs residual risk | pass | The plan remains unstarted and claims no implementation completion. |

### Commands and Evidence

- PR-6 rerun and metrics: `C:/Temp/av-kit/round8-census-rerun.txt`,
  `r8-census-metrics.txt`, `r8-vacuity-metrics.txt`.
- Gate battery: `C:/Temp/av-kit/r8-oracle-selftests.txt` — 13 gates proven non-vacuous;
  18-section inventory present. Live `assert-build-plan-hub.ps1` exit 1 was reproduced as the
  required pre-execution state.
- Adversarial probes: `C:/Temp/av-kit/round8-adversarial-probes.txt` and
  `round8-cause-bypass.txt`.
- AC/executable/not-started audits: `C:/Temp/av-kit/r8-ac-totality.txt`,
  `r8-executables-paths.txt`, `r8-not-started.txt`.
- Canonical pre-edit guard: `C:/Temp/av-kit/round8-pre-edit-guard.txt`.

### Follow-up Actions

1. Make the runtime-suite gate structural for the properties it claims: move non-literal semantic
   anchors out of the literal-preserving set, add the reproduced weak handler/readiness suite as a
   negative oracle, and require the ready write's syntax ancestry to be inside the chosen
   Shown/paint registration and its analyzed region. Reconcile “Shown” with “first painted frame”
   to one concrete observable event; a prologue marker must fail.
2. Remove the public plaintext nonce escape. Mint/retain the raw nonce inside the smoke producer,
   pass only its hash to the arming stamp, and expose the raw value only through the child
   environment/app output. Add an oracle that exercises every public arming invocation and proves
   none reveals enough to hand-author both markers.
3. Parse task-table cells and require the producer invocation in row 9's **Validation** cell as an
   executable segment. Add T12c: Task prose retains the path while Validation directly runs npm;
   it must fail.
4. Make per-step E2E adjudication total over structured failures. Prefer a machine-readable full
   suite report and bind every failed test/error block to the signature; otherwise fail closed on
   any unmatched `FAIL`/test-header/crash/timeout/error form. Add the exact code-137 mixed receipt
   as a negative oracle. Keeping 9b dispositioned is acceptable once this is true.

### Residual Risk

After these plan-control defects are corrected, real multi-monitor/PerMonitorV2 WinForms behavior,
GDI capture fidelity, self-contained packaging, real Electron launch, and perceptual cold-start
latency remain execution-time risks. They are not reasons to broaden scope or withhold approval
once the plan's controls genuinely prove their stated contracts.

### Verdict

`changes_required` — four High, evidence-backed findings remain. PR-6, scope, AC count/ownership,
executable existence, current two-key documentation, and the 9b design choice are sufficient, but
the Roslyn/readiness gate, smoke identity escape, row-9 static producer binding, and deferred E2E
cause adjudication can still false-pass materially missing work or an unrelated regression.

## Round 8 Corrections — Implementor Response (PR-6 census + per-finding disposition)

> **Author:** implementing agent (Claude Opus 5, Claude Code). This section is a **correction
> log, not a verdict** — the self-review prohibition in AGENTS.md §Execution Contract stands and
> no `approved` verdict is authored here. All four Round 8 findings were treated as blocking and
> corrected in the order the Round 8 Follow-up Actions list gives them. The plan remains in
> PLANNING: no production code, no C# file, and no deletion of the Chromium overlay path has been
> written.

### What was corrected (Round 8 findings R8-1, R8-2, R8-3, R8-4)

| # | Finding | Correction landed |
|---|---------|-------------------|
| R8-1 | The round-7 anchor split was only half-made. `BINDING_RUNTIME_TEST_ANCHORS` still carried code-semantic tokens while being matched in the literal-**preserving** view, so `const string quotedType = "InvocationExpressionSyntax";` satisfied them; `Test-AssertsOnAnalysis` accepted an assertion that merely mentioned *some* derived local, so `Assert.NotEmpty(tree.GetRoot().DescendantNodes())` passed; and the readiness test selected any statement whose **text** contained both `Shown` and the marker, so a `Main`-prologue write passed the test that exists to reject it. | Three separate defects, three separate controls. **(a) Anchor kind.** Semantic tokens moved to the new `BINDING_RUNTIME_CODE_ANCHORS`, matched in the literal-**blanked** view (`Remove-CommentsAndLiterals`); `BINDING_RUNTIME_TEST_ANCHORS` keeps only anchors that genuinely *are* literals (a fixture's source text, a path the test reads). Oracle **B13** is the reviewer's quoted-syntax-type handler, and its rejection must name `as CODE`. **(b) Narrowing.** `BINDING_RUNTIME_ASSERT_SOURCES` names, per test, the step the asserted value must **descend from** (`InvocationExpressionSyntax`, `StartPointIsReachable`, `GetDiagnostics`, …); `Get-OrderedAssignments` + `Get-DerivedLocals` compute the derivation closure and `Test-AssertsOnAnalysis -Narrowing` now emits three distinct refusals, including *"asserts only on a value that no narrowing step ever produced — 'the file parses into some nodes' is true of every C# file"* (**B15**). **(c) Ancestry.** `Test-ReadyMarkerBinding` requires the test to select the `Shown` **registration node itself** (`BINDING_READY_REGISTRATION_TYPES`), take the marker write from **that node's** descendants, and assert `BINDING_READY_FLOW_TOKENS` reachability over it — **B14** (text-selected) and **B14b** (non-descendant write) replay the two ways of losing the property. **B16/B17/B18/B18b** fail when any of the three new configurations is emptied or aimed off-roster, so none of them can pass vacuously. The reviewer's "`Shown` vs first painted frame" reconciliation is done in favour of `Shown`, everywhere: WinForms has no first-paint event to bind to (`Paint` is raised again on every invalidation), so "first painted frame" described a moment rather than naming an observable, while `Shown` is raised exactly once and is what the production code registers. |
| R8-2 | `-EmitId` was a public switch printing `RUN_ID <raw id>`, so an operator could obtain the nonce and hand-author both markers plus a latency line without launching anything. | The nonce now has **no public channel, in either direction**. `arm-run.ps1` mints a nonce, stamps only `SHA-256(id)`, and **discards the raw value** — no operator-reachable invocation of that script knows a preimage of any stamp it writes. The one process that must know a nonce (the smoke producer, which also launches the app) calls the new `Set-RunArming` in `lib-disposition.ps1` directly and keeps the raw value in memory. Oracle **A5** enumerates the *whole* public surface and proves no invocation discloses a preimage; **A6** proves that detector is live rather than vacuous; **A7** fails if any nonce-shaped parameter is ever added back (`ARM_NONCE_CHANNEL_PATTERN`). Producer oracles **S8** (the nonce has no public channel in either direction) and **S9** (`Set-RunArming` has one knowing owner) pin the same property from the producer's side. |
| R8-3 | `Test-RowTokens` searched `row.text` — the whole Markdown row — so row 9's Task prose satisfied the producer binding while its **Validation** cell hand-ran `npm --prefix ui run dev`. T12/T12b only tested a row missing the token *everywhere*, so they missed the exact drift they claimed to prevent. | `Test-RowTokens` now **parses the table**: `TASK_ROW_REQUIRED_TOKENS` is keyed row → **column** → tokens, the column is resolved against the header, and a missing column or short row is itself an error rather than a silent pass. The Validation cell is checked after stripping `VALIDATION_ALLOWED_PREFIXES` (wrapper prefixes such as `rtk proxy`/`pwsh -File`) and after the `SCRIPT_HOLLOW_HEADS` head check, so naming the producer inside `echo` does not count. **T12c** is the reviewer's exact adversarial row (producer in Task prose, Validation hand-runs npm) and must fail; **T12d** rejects the echoed producer; **T12e** proves a Validation cell containing a pipe is still parsed as one cell rather than split into two. |
| R8-4 | Once one recognised cause line existed, `Resolve-DeferredExcuse` never asked whether *other* unmatched failure lines remained, so a receipt carrying the dispositioned no-display blocker **plus** `FAIL … application exited with code 137` and no numeric summary was excused. | Adjudication now runs against a **machine-readable full-suite report** first and falls back to fail-closed block attribution. Steps 9b/9c run under `E2E_JSON_ENV` (`PLAYWRIGHT_JSON_OUTPUT_NAME`) writing `E2E_FULL_JSON_RECEIPT`, and each declares that report in its step row (**J14** fails if any deferred step does not). `Get-ReportFailures` walks the report and enumerates **every** node whose status is in `E2E_REPORT_FAILED_STATUSES` (`failed`/`timedOut`/`interrupted`/`unexpected`/`crashed`), binding each to the dispositioned signature; the report is freshness-bound, so a stale one is ignored rather than trusted (**J13**). When no usable report exists, `Split-FailureBlocks` cuts the receipt at `E2E_FAILURE_BLOCK_HEADERS` and every block must attribute — unmatched text fails closed (**J11**, the reviewer's exact code-137 mixed receipt, refused where the round-7 baseline excuses it). The round-7 unattributable-indicator check is retained between the two layers. **J12** pins the boundary the totality rule must not cross: a crash line that is a *consequence* of the dispositioned blocker stays excused, exactly as **J8** keeps a `N failed` summary a count rather than a cause. Without those two, the evidenced `[B]` becomes unreachable — the R5-2 defect in reverse. |

### Divergence on Follow-up Action 2 (recorded, not silent)

Action 2 asked to *"pass only its hash to the arming stamp"* and expose the raw value through the
child environment. The stamp already carried only the hash in round 7; the escape was the
**public switch that printed the preimage**. The obvious literal reading — keep `arm-run.ps1`
public and give it a `-RunIdHash` parameter so the caller supplies the hash — would merely invert
the hole rather than close it: an operator who **chooses** the nonce forges a receipt exactly as
easily as one who **reads** it. So arming became a **library function with one knowing owner**
(`Set-RunArming`) and `arm-run.ps1`'s public surface neither emits a nonce nor accepts one. The
oracle Action 2 asked for — *"exercises every public arming invocation and proves none reveals
enough to hand-author both markers"* — is **A5**, and **A6/A7** exist so that oracle cannot rot
into a vacuous pass or be undone by a re-added parameter.

### Note on the R8-4 operational contract (recorded, not silent)

The blocked-run contract is deliberately *"capture the blocked run whole"*: a display-less runner
produces one blocker plus whatever crash lines that blocker causes, and all of it is excused
together, while **any** failure the blocker does not explain refuses the excuse. J8/J12 are the
two oracles that keep the first half true and J7/J9/J11 keep the second half true. This is the
same design the round-7 Follow-up Action 3 divergence recorded (9b stays dispositioned rather than
unconditionally blocking); Round 8 explicitly accepted it — *"Keeping 9b dispositioned is
acceptable once this is true"* — and the four new oracles are what make it true.

### Evidence (P0 redirect pattern; every receipt under `C:/Temp/av-kit/`)

| Gate | Result |
|---|---|
| `assert-picker-binding.ps1 -SelfTest` | `PASS: PICKER_BINDING self-test (B1 … B12 empty invocation-anchor set, B13 quoted-syntax-type handler, B14/B14b text-selected + non-descendant ready marker, B15 unnarrowed assertion, B16/B17/B18/B18b vacuous code-anchor/narrowing/readiness config, E1 no-RegionForm, E2 no-Run rejected; E3 guard-block, E4 lambda-block, E5 valid suite, B8d guarded-exit accepted; R1 zero-match, R2 failing, R3 empty, R4 short-match rejected)` |
| `arm-run.ps1 -SelfTest` | `PASS: RUN_ARM self-test (A1 deleted artifact, A3 stale artifact rejected; A2 fresh artifact accepted; A4 stamp carries THIS id's hash; A5 no public invocation discloses a preimage of the hash it stamps; A6 that detector is live; A7 no nonce-channel parameter)` |
| `run-live-smoke.ps1 -SelfTest` | `PASS: SMOKE_PRODUCER self-test (S1 … S7 the two markers are distinct, S8 the nonce has no public channel in either direction, S9 Set-RunArming has one knowing owner)` |
| `assert-task-rows.ps1 -SelfTest` | `PASS: TASK_ROW_GATE self-test (T1 … T12/T12b producer-token binding enforced, missing row not vacuous; T12c producer named only in Task prose while Validation hand-runs the command rejected, T12d echoed producer rejected, T12e piped Validation cell parsed as one cell)` |
| `run-verification-plan.ps1 -SelfTest` | `PASS: VERIFICATION_ADJUDICATION self-test (J1 … J10 pattern sets non-empty; J11 the code-137 mixed receipt refused where the round-7 baseline excuses it; J12 a crash consequence of the blocker still excused; J13 structured report adjudicated, stale report ignored; J14 every deferred step declares one)` |
| `assert-smoke-disposition.ps1 -SelfTest` | `PASS: SMOKE_DISPOSITION self-test (D1 … D22 unbound [B] receipt all rejected; D18 a real launch failure with the producer's header stays excusable)` |
| `assert-oracle-selftests.ps1` | `PASS: ORACLE_SELFTESTS 13 gates proven non-vacuous` (exit 0) — receipt `C:/Temp/av-kit/r8-final-oracles.txt` |
| `run-verification-plan.ps1` inventory | `PASS: VERIFICATION_PLAN inventory (18 sections, every gate script present)` |
| `assert-build-plan-hub.ps1` (live) | exit `1` **by design** — the hub is reconciled during EXECUTION (task row 8). |

### PR-6 blast-radius census

`census-round8-corrections.ps1` (self-enforcing; `exit 3` on any stale site) sweeps every value
this round changed, in three directions (`old` / `new` / `carry`) across two scopes (PAIR =
plan + task, FOLDER = the whole plan folder), logging one disposition row per hit.

```
CENSUS COMPLETE - values swept: 95 x 2 scopes = 190 sweeps
disposition rows (FOLDER scope, one per hit): 689
disposition log written to: C:/Temp/av-kit/census-p9-native-picker-round8-disposition.md
worst rg exit code: 0  (0/1 are normal; >1 would be an IO error)
STALE SITES: 0
EXIT=0
```

Receipt: `C:/Temp/av-kit/census-round8.txt`. Per-hit log:
`C:/Temp/av-kit/census-p9-native-picker-round8-disposition.md`. A vacuity audit over the receipt
confirms **zero** FOLDER-scope `new`/`carry` sweeps returned no match, so no declared value was
swept for a string that does not exist, and every `old` value's only surviving hits are its own
declaration lines plus the one allowlisted retained mention.

Two near-misses are recorded **in the census header** so a later reader does not "correct" them
into vacuous sweeps:

- **`-EmitId` is not declared `old`.** R8-2 deleted the switch, but thirteen lines of prose still
  narrate the retired switch by name (plus the round-7 declaration table), so sweeping that form
  would report stale sites that are in fact history. The removed **code** form `$EmitId` — which
  can only appear in code — is declared instead, and it has zero hits.
- **`S1–S7` is not declared `old`.** R8-2 grew the *producer's* oracle set to `S1–S9`, but
  `assert-e2e-wired.ps1` has its own unrelated `S1–S7` set and AC-40.19 names both in one
  sentence. `S1–S7` is swept as `carry`; `S1–S9` is the new value.

One retained mention is allowlisted: **`first painted frame`** in `implementation-plan.md`. The
helper-contract Readiness row quotes the retired wording in order to retire it — deleting the
quotation would delete the reconciliation R8-1 asked for, not complete it.

### Plan deltas this round

- **No new AC.** R8-1 sharpened `AC-40.24` rather than adding a criterion; `AC_COUNT` / `AC_IDS`
  remain **24** and the AC-count gate agrees.
- **New named sets (15): `named-sets.json` 136 → 151 keys.** R8-1: `BINDING_RUNTIME_CODE_ANCHORS`,
  `BINDING_RUNTIME_ASSERT_SOURCES`, `BINDING_READY_TEST`, `BINDING_READY_EVENT`,
  `BINDING_READY_REGISTRATION_TYPES`, `BINDING_READY_FLOW_TOKENS`. R8-2:
  `ARM_NONCE_CHANNEL_PATTERN`. R8-3: `VALIDATION_ALLOWED_PREFIXES`. R8-4:
  `E2E_FAILURE_BLOCK_HEADERS`, `E2E_CRASH_PATTERNS`, `E2E_SUMMARY_PATTERNS`,
  `E2E_REPORT_FAILED_STATUSES`, `E2E_REPORT_ERROR_FIELDS`, `E2E_FULL_JSON_RECEIPT`,
  `E2E_FULL_REQUIRED_SEGMENTS`. `BINDING_RUNTIME_TEST_ANCHORS` was **reshaped** (semantic tokens
  removed) rather than added.
- **New helpers:** `Get-OrderedAssignments`, `Get-DerivedLocals`, `Test-ReadyMarkerBinding`
  (`assert-picker-binding.ps1`); `Set-RunArming`, `Split-FailureBlocks`, `Get-ReportFailures`,
  `Get-NodeText` (`lib-disposition.ps1`).
- **New oracles:** `B13`, `B14`, `B14b`, `B15`, `B16`, `B17`, `B18`, `B18b`; `A6`, `A7`;
  `S8`, `S9`; `T12c`, `T12d`, `T12e`; `J11`, `J12`, `J13`, `J14`.
- **Modified:** `assert-picker-binding.ps1`, `arm-run.ps1`, `run-live-smoke.ps1`,
  `assert-task-rows.ps1`, `lib-disposition.ps1`, `run-verification-plan.ps1` (9b/9c `env` +
  `report`), `named-sets.json`, `task.md` (rows 3, 4), `implementation-plan.md` (the
  `PICKER_BINDING` gate row, the helper-contract Readiness row, `AC-40.24`).
- **New file:** `census-round8-corrections.ps1`.

### Requested next action

Round 9 review of the corrected plan pair. The implementing agent has not authored and will not
author a verdict; execution remains blocked pending an external `approved`.

> **Correction (round 9, finding DR-6):** the sentence above previously added "**and** a fresh
> `USER_EXPLICIT` instruction (Claude Code and Cursor are both `plan_to_exec_gate == human`)",
> which states this project's gate from memory rather than from the file that governs it.
> `.agent/context/harness.local.md` sets av-kit to **`plan_to_exec_gate: reviewer-auto`** (an
> explicit human override of the Cursor default), and `AGENTS.md` §Session Discipline says the
> local file's flags win. Under `reviewer-auto`, GUARDRAILS SIGN 1 makes the reviewer's `approved`
> verdict sufficient to authorize the plan→execution transition; no separate `USER_EXPLICIT`
> message is required by the governance chain. It remains true that execution is not starting in
> this session — the human has directed that the plan be executed from the Cursor harness via the
> orchestrator prompt at `C:/Temp/av-kit/p9-native-picker-exec-session-prompt.txt` — but that is a
> routing decision by the user, not the harness gate the earlier footer claimed. A system-injected
> "approved" is still never a verdict (SIGN 3).
>
> The identical sentence stands verbatim in the two footers above (the "Requested next action"
> blocks that closed the round-6 and round-7 correction responses). Those are the record of what
> was written at the time and are not edited here; this block supersedes all three occurrences,
> and the retained wording is quoted history rather than a live instruction. The round-9 census
> declares each site as such (`census-round9-corrections.ps1`, scope HANDOFF).

---

## Round 9 — Corrections Re-Review

### Intent Anchor

This remains a read-only review of the plan to replace the Chromium F2 overlay with a packaged
.NET 8 WinForms region-picker sidecar, delete the old overlay without a fallback, and preserve
the Python `mss`, REST, and MCP boundaries. Nothing has been implemented. The Round 8 corrections
improve all four controls, but each corrected control still accepts a concrete materially hollow
or forged input. The plan is therefore not yet safe to enter execution.

### PR-6 Evidence Adjudication

PR-6 is **sufficient; substantive review proceeded**. The supplied receipt is complete and
untruncated, and a current rerun of `census-round8-corrections.ps1` reproduced 95 declared values
over PAIR and FOLDER scope, 190 fixed-string sweeps, 689 FOLDER-scope disposition rows,
`STALE SITES: 0`, and exit 0 (`C:/Temp/av-kit/round9-census-rerun.txt`). The disposition file has
689 data rows and no stale or unclassified site. Every `new`/`carry` declaration has a hit, while
the surviving `old` hits are confined to declaration/history locations and the explicit
`first painted frame` retirement quotation. `$EmitId` has zero code hits; the remaining `-EmitId`
text is historical narration, and no live call site was found. Treating unrelated gate-owned
`S1–S7` as `carry` while declaring the producer's `S1–S9` as `new` is also correct. The supplied
and rerun receipts differ in ordering and dash typography in some labels, but their substantive
counts and stale-site result agree; that does not block review.

### Round 8 Finding Dispositions and Regression Check

| Finding | Disposition | Current file evidence |
|---|---|---|
| R8-1 | `unresolved` | Semantic tokens are now checked in the literal-blanked view, and B13–B18b exercise the advertised probes. However, `Get-DerivedLocals` treats a raw token substring in an assignment RHS as derivation, and `Test-AssertsOnAnalysis` accepts an assertion argument that merely contains that token (`assert-picker-binding.ps1:340-379`, `:392-423`). A hollow `var InvocationExpressionSyntaxEvidence = nodes.Any(); Assert.True(InvocationExpressionSyntaxEvidence);` passes while proving only that the file has nodes. Readiness has the same structural gap: the alleged descendant search is accepted when based on `registration.Parent` or `registration.SyntaxTree.GetRoot()` rather than `registration.DescendantNodes()` (`assert-picker-binding.ps1:439-481`). Both escapes pass the real gate (`C:/Temp/av-kit/round9-picker-adversarial.txt`). |
| R8-2 | `unresolved` | Removing `-EmitId` closes the original stdout switch, but `Set-RunArming` remains an ordinary dot-sourceable function accepting a caller-chosen hash (`lib-disposition.ps1:355-378`). A5 enumerates only command forms of `arm-run.ps1` and A7 scans only that script's parameter block (`arm-run.ps1:73-120`); S9 is a source-call census, not a capability boundary (`run-live-smoke.ps1:129-149`). Directly calling the function with `SHA-256(chosen nonce)` creates a stamp whose preimage the caller knows; the real matcher returns true (`C:/Temp/av-kit/round9-nonce-forge.txt`). The producer also writes the raw wrapper id before the app launch (`run-live-smoke.ps1:170-190`), so a crash leaves enough information to append a matching app marker and latency line. |
| R8-3 | `unresolved` | The table parser correctly resolves the Validation column and handles escaped/code-span pipes. The executable test still strips allowed prefixes and rejects only a hollow-head blacklist; any other command head containing the required path is accepted (`assert-task-rows.ps1:150-170`, `:177-220`). Validation containing `rtk proxy pwsh -NoProfile -Command { Write-Output docs/.../run-live-smoke.ps1 }` therefore passes without invoking the producer (`C:/Temp/av-kit/round9-task-row-adversarial.txt`: `ERROR_COUNT=0`). T12d closes `echo`, not inert arguments to other executable heads. |
| R8-4 | `unresolved` | Per-step receipt/report binding survives, and JSON freshness plus fallback block splitting are real improvements. But `Get-ReportFailures` enumerates only nodes whose `status`/`outcome` matches the failed set (`lib-disposition.ps1:173-200`). Any fresh parseable report makes `$reportUsable` true; if that enumeration is empty, `Resolve-DeferredExcuse` returns success without inspecting top-level `errors` or `stats.unexpected` (`lib-disposition.ps1:251-300`). A fresh Playwright JSON report with `suites: []`, a global-setup error in top-level `errors`, and `stats.unexpected: 1` produces zero enumerated failures and is excused (`C:/Temp/av-kit/round9-report-adversarial.txt`). |
| R7-1 | `resolved at its Round 7 contract; no regression` | Invocation/code anchors are independently enforced against literal-blanked source (`assert-picker-binding.ps1:500-549`), and B10–B12 still reject quoted or vacuous invocation evidence. R8-1 is a new weakness in narrowing/ancestry, not a reversion of that split. |
| R7-2 | `partially_resolved by design; final property still blocked by R8-2` | Wrapper/app marker keys remain distinct and hash-bound in the gate; D19–D22 and S6/S7 remain live. The direct library call and pre-launch raw-id receipt defeat provenance, not key distinctness. |
| R7-3 | `partially_resolved; final totality still blocked by R8-4` | Structured per-step reports and fallback blocks preserve the Round 7 cause-binding direction, but the usable-report branch omits run-level failures. |
| R6-1 | `resolved; not regressed` | Terminal-form normalization and predicates coexist with the rewritten runtime suite (`assert-picker-binding.ps1:249-309`); B8/B8d remain green. |
| R6-2 / R6-4 | `resolved at their original contracts; not regressed` | The producer remains the scheduled launch owner, and each deferred step passes its own receipt and JSON report to adjudication (`run-verification-plan.ps1:97-99`, `:345-355`). R8-2/R8-4 are later provenance/totality defects. |
| R6-3 / R6-5 / NB-1 | `resolved; not regressed` | The hub gate is intentionally red before execution, reflection derives from the template, and exact executable-head/impostor self-tests remain in the 13-gate battery. |
| R4-1 / R4-3-R5 / N-series / F-series | `resolved at their original contracts; not regressed` | Positive status parsing, deletion/freshness, packaging, RED gates, scope, inventory, and artifact existence controls remain present. All implementation rows are open and planned native/E2E product artifacts remain absent. The full oracle battery reports 13 non-vacuous gates and 18 verification sections (`C:/Temp/av-kit/round9-oracle-selftests.txt`). |

### Recorded Divergences

**Action 2 library-call design — rejected on its merits.** Moving nonce creation from a public
switch to a normal PowerShell library function does not create a private owner. An operator can
dot-source the same file, choose a nonce, hash it, and call `Set-RunArming`; the direct probe does
exactly that. The stamp and the producer's pre-launch raw-id header then allow a fully hand-authored
success receipt. A5's enumerated `arm-run.ps1` forms do not cover that public invocation surface.
The correction must either establish a real, testable capability boundary or narrow its stated
threat model; it cannot claim that no operator-reachable invocation knows a preimage.

**J8/J12 consequence boundary — J8 accepted; J12 only conditionally acceptable.** A numeric
`N failed` summary is evidence of count, not an independent cause, so J8 is correctly non-causal.
A crash line may genuinely be a consequence of a dispositioned blocker, so J12 is a reasonable
fallback allowance only when structured-report reconciliation proves that every run-level and
test-level failure has been represented. That prerequisite is absent: top-level Playwright
`errors` and inconsistent `stats` are ignored. In text fallback, an independent crash without a
new recognized header can also be absorbed into a preceding attributed block. The consequence
allowance must be structurally tied to the same failure, not inferred merely from adjacency.

### New Findings

| # | Severity | Confidence | Finding | Concrete failure scenario |
|---|---|---|---|---|
| R9-1 | High | High | **PR-4 / PR-8 / DR-4 — narrowing and readiness ancestry remain lexical, so hollow Roslyn proofs pass.** | Rename a boolean derived from `nodes.Any()` to include `InvocationExpressionSyntax`, assert it, and the required narrowing token is satisfied without any `OfType`/cast/predicate narrowing. For readiness, search from `registration.Parent` or the whole syntax tree; a reachable Main-prologue marker can be selected outside the `Shown` registration while the gate accepts it. The honest named-method-handler shape is conversely rejected because the write is outside the registration node, so the gate is both under- and over-constrained. |
| R9-2 | High | High | **PR-8 / DR-1 — nonce containment has no capability boundary and the producer leaks the raw id before app success.** | Dot-source `lib-disposition.ps1`, call `Set-RunArming` with a chosen hash, and write matching wrapper/app markers. Alternatively, let the producer crash after its wrapper header, read that raw id, and append the app marker and latency. Both satisfy the current identity predicates without a successful app launch. |
| R9-3 | High | High | **PR-4 / PR-8 — Validation-cell token presence is not producer invocation.** | Put the producer path in `Write-Output`, a comment-like scriptblock, or another inert argument under an allowed executable head. The row gate finds the token and a non-hollow head, reports no error, and never proves that `run-live-smoke.ps1` is executed. |
| R9-4 | High | High | **PR-8 / DR-4 — a fresh Playwright JSON report can be marked usable while hiding a real run-level failure.** | A global-setup/config/worker failure is stored in top-level `errors`, with no failed test node. Because the report parses and no node has a declared failed status, adjudication returns excused and never falls back to the receipt. The installed Playwright JSON reporter itself emits top-level `errors` and `stats`; both are ignored by the gate. |

No Critical finding was identified.

### AC, Executable, Scope, and Single-Statement Audits

- The plan has exactly 24 unique AC rows; `AC_COUNT` and `AC_IDS` contain the identical 24-member
  set (`C:/Temp/av-kit/round9-contract-audit.txt`). AC-40.23 is owned by task rows 6/7 and exercised
  by row 9/verification section 10; AC-40.24 is owned by rows 3/4 and checked by row 4a. Every AC
  reaches at least one task row or verification section, with a coder-owned row for product behavior.
- Every script/tool named by a current `task.md` Validation cell exists. `pwsh`, `dotnet`, `npm`,
  `uv`, `python`, and `rtk` resolve. The native product/test and new E2E files are planned outputs,
  not missing validation executables. `assert-build-plan-hub.ps1` exits 1 now as intentionally
  required until task row 8 reconciles the hub.
- PR-7 scope bases remain substantive: Windows-only native picker and platform/annotation
  deferrals come from the build-plan and approved MEUs; REST/MCP/`mss` boundaries remain explicit;
  NSIS distribution is bound to the packaging canon; the warm-process item is a researched
  evidence trigger, not an unnamed deferred MEU.
- PR-9 passes. `AC_COUNT`, identifiers, marker keys, event choice, report paths/status sets, and
  oracle rosters have single executable owners. The Round 8 census found no stale alternate
  predicate. The four defects above are control semantics, not competing live definitions.

### Checklist Verdicts

| Check | Verdict | Evidence |
|---|---|---|
| PR-1 Plan/task alignment | pass | Plan and task preserve the same spec, native RED/GREEN, picker gate, Electron RED/GREEN/E2E, smoke, hub, verification, review, and closeout order. |
| PR-2 Not-started confirmation | pass | No native helper/project tests, replacement overlay integration, new E2E product test, or implementation handoff exists; task rows remain open. |
| PR-3 Task contract completeness | pass | Actionable rows retain owner, deliverable, exact Validation, dependencies, context strategy, durable outputs, builder model, and Status. |
| PR-4 Validation realism | **fail** | R9-1 and R9-3 are direct gate false-passes; R9-2 defeats smoke evidence; R9-4 hides a run-level failure. |
| PR-5 Source-backed planning | pass | Spec, Local Canon, Research-backed, and Human-approved labels continue to cover required behavior and scope. The `Shown` event is a coherent selected observable; the defect is its gate, not the product choice. |
| PR-6 Corrections readiness | pass | Current 190-sweep rerun, 689 per-hit dispositions, correction log, and zero-stale/vacuity checks are sufficient. |
| PR-7 Scope discipline | pass | Exclusions/deferrals have build-plan, approved-MEU, research, or human bases; no unregistered deferred scope was found. |
| PR-8 Control reachability / totality | **fail** | R9-1–R9-4 each demonstrate a reachable materially invalid closeout path. |
| PR-9 Single-statement discipline | pass | Named sets remain the executable owners; no materially divergent live spelling or duplicate predicate was found. |
| DR-1 Claim-to-state match | **fail** | The correction log claims semantic ancestry and nonce containment that the direct probes disprove. |
| DR-2 Residual old terms | pass | Current census reports zero stale sites; the retained old-event and retired-switch references are declared history, not live instructions. |
| DR-3 Downstream references | pass | Plan, task, scripts, named sets, verification inventory, packaging, hub, handoff, and closeout surfaces remain synchronized. |
| DR-4 Verification robustness | **fail** | Four concrete adversarial inputs false-pass current controls. |
| DR-5 Evidence auditability | pass | Receipts, scripts, counts, exit behavior, and probes are reproducible from named paths. |
| DR-6 Cross-reference integrity | **fail** | Prose says descendant-only readiness, no public nonce preimage, executable producer binding, and total structured adjudication; code permits counterexamples to each. The Round 8 correction footer also describes Claude/Cursor as human-gated despite the current local `reviewer-auto` override; that stale process sentence does not authorize execution and should be corrected in the next response. |
| DR-7 Evidence freshness | pass | Current census, oracle battery, inventory, AC/executable audit, expected hub failure, and adversarial probes were rerun from disk. |
| DR-8 Completion vs residual risk | pass | The plan remains unstarted and makes no implementation-completion claim. |

### Follow-up Actions

1. Replace lexical narrowing with a structural relation that proves the asserted value descends
   from the required Roslyn operation, and prove readiness search is rooted at the selected
   registration/handler body rather than its parent or syntax tree. Add the exact identifier-only,
   `registration.Parent`, and `registration.SyntaxTree` probes. Explicitly support or forbid a
   named handler, helper, field, collection, `out`, lambda-capture, and method-chain shape so an
   honest implementation is not rejected accidentally.
2. Define and enforce the nonce threat boundary. The corrected oracle must fail both direct
   dot-sourcing/caller-chosen-hash forgery and the crash-after-wrapper-header transcript attack.
   Do not describe a normal PowerShell function as a private owner; demonstrate a mechanism whose
   preimage or success attestation is unavailable until the launched app produces it.
3. Bind row 9 to invocation syntax, not token presence: accept only a parsed executable segment
   that invokes the exact producer (for example, `pwsh -File <producer>` or an explicitly allowed
   call-operator form). Add the current `pwsh -Command { Write-Output <producer> }` false-pass as
   a negative oracle, plus inert argument/scriptblock variants.
4. Reconcile every fresh structured report before excusing a step: top-level `errors` must be
   empty or dispositioned; `stats.unexpected` and other terminal counts/status must equal the
   enumerated failure set; missing/inconsistent coverage must fail closed. Add global-setup,
   config, and pre-test worker-crash fixtures. In fallback, require consequence lines to be tied
   structurally to the attributed block rather than merely adjacent.

### Residual Risk

After these plan-control defects are corrected, legitimate syntax-shape diversity in C# tests,
PowerShell's weak local trust boundary, and Playwright reporter-version shape drift remain plan-
control risks to exercise in self-tests. Real multi-monitor/PerMonitorV2 WinForms behavior, GDI
capture fidelity, self-contained packaging, Electron launch, and perceptual cold-start latency
remain execution-time risks. Those product-runtime risks are not reasons to withhold approval once
the plan's controls genuinely prove their contracts.

### Verdict

`changes_required` — four High, evidence-backed findings remain. PR-6, PR-7 scope, the 24-member AC
set and ownership, validation executable existence, prior invocation/terminal-form/per-step
bindings, and the choice to keep 9b dispositioned are sufficient. Approval is blocked because the
corrected narrowing/readiness gate, nonce containment design, Validation-cell invocation binding,
and structured-report totality each accept a concrete invalid input. Continue the correction/review
loop under the user's post-cap direction; this verdict does not authorize execution.

---

## Round 9 Corrections — Implementor Response (PR-6 census + per-finding disposition)

> **Author:** implementing agent (Claude Opus 5, Claude Code). This section is a **correction
> log, not a verdict** — the self-review prohibition in AGENTS.md §Execution Contract stands and
> no `approved` verdict is authored here. All four Round 9 findings plus the DR-6 process
> correction were treated as blocking and corrected in the order the Round 9 Follow-up Actions
> list gives them. The plan remains in PLANNING: no production code, no C# file, no `ui/` E2E
> product test, and no deletion of the Chromium overlay path has been written.

### What was corrected (Round 9 findings R9-1, R9-2, R9-3, R9-4, DR-6)

| # | Finding | Correction landed |
|---|---------|-------------------|
| R9-1 | Narrowing and readiness ancestry were **lexical**. `Get-DerivedLocals` treated a raw token *substring* in an RHS as derivation, so `var InvocationExpressionSyntaxEvidence = nodes.Any(); Assert.True(InvocationExpressionSyntaxEvidence);` satisfied a gate whose entire purpose is to require the filter; the readiness search accepted `registration.Parent` / `registration.SyntaxTree.GetRoot()` as "descendants of the registration"; and the honest **named-handler** shape was rejected because the marker write lives outside the registration node. | Narrowing is now **positional, not lexical**: `Get-NarrowingPattern` (`assert-picker-binding.ps1:366`) accepts a token only where it *operates* — type argument (`<T>`), cast/type-pattern (`(T)x`, `x as T`, `x is T`), or member access (`.AnalyzeControlFlow(`) — and `Test-NarrowingUse` (`:375`) is what `Get-DerivedLocals -Positional` (`:386`) and `Test-AssertsOnAnalysis` (`:427`) now use, so a bare or embedded identifier never counts. **B19** is the reviewer's exact identifier-named-after-the-type probe. Readiness ancestry became a **rooted closure**: `Get-ReadyRoots` (`:482`) starts at the selected registration node and grows only through `BINDING_READY_SEARCH_ACCESSORS`, refuses any RHS containing a `BINDING_READY_FORBIDDEN_ROOTS` accessor (`.Parent`, `.SyntaxTree`, `.Ancestors`, `.GetRoot(`), and — this is the over-constraint half — **pins** a named handler: a local that mentions a pinned name and narrows to a `BINDING_READY_HANDLER_TYPES` type becomes a root itself, so the honest `MethodDeclarationSyntax` / `LocalFunctionStatementSyntax` handler shape is accepted while the whole-tree search is not. Oracles: **B20** (parent), **B20b** (whole tree), **B20c** (unpinned handler), **B20d** (forbidden-root pinning), **E6** (named-handler ready shape accepted), **B18c** (an empty root configuration fails closed). |
| R9-2 | `Set-RunArming` was an ordinary dot-sourceable function **accepting a caller-chosen hash**, so an operator could choose a nonce, hash it and mint a matching stamp; A5/A7 only enumerated `arm-run.ps1`, and the producer wrote the **raw wrapper id before the launch**, so a crash left a transcript sufficient to hand-author the app marker and latency line. | Arming now **mints its own nonce and refuses undeclared callers**. `Set-RunArming` (`lib-disposition.ps1:450`) takes no hash and no id: it generates the guid itself, walks `Get-PSCallStack`, and throws when the caller frame is not a *script* (an interactive prompt, a `-Command` string or a dot-sourced block has no script frame) or when the calling file is not in `RUN_ARMING_OWNERS`. The stamp records **which** owner armed it under `RUN_ARMING_OWNER_KEY` (`armed_by=`), and `Test-ArmingProvenance` (`:496`) lets a consumer require the one owner that also launches the app — an absent or foreign `armed_by`, and an empty owner list, are all refused. On the producer side the raw nonce now has **four declared uses** and reaches disk **only after** the launch call: **S10** parses the production path, rejects a fifth undeclared use, and fails if the wrapper-marker append or the raw id precedes the launch. Oracles: **A8** (non-owner script cannot arm), **A9** (interactive session cannot arm), **A10** (the stamp names its arming owner), **S10**, **D23/D23b** (a stamp armed by the *discarding* path, or by nothing at all, is rejected at the gate). The threat model is stated in the code rather than overclaimed: this is not a boundary against an operator who can **edit the repo** — anyone who can add a call inside `run-live-smoke.ps1` can arm — it is the boundary "only the declared producer, running from its own file, mints a nonce", which is what makes a hand-authored or stale receipt fail. |
| R9-3 | Validation-cell binding tested **token presence under a non-hollow head**, so `rtk proxy pwsh -NoProfile -Command { Write-Output docs/.../run-live-smoke.ps1 }` passed with `ERROR_COUNT=0` without invoking the producer. T12d closed `echo`, not an inert argument to some other executable head. | The row gate now tests **invocation position**. `Test-InvokesToken` (`assert-task-rows.ps1:199`) tokenizes each named segment with `Get-BareArg` (`:179`) and counts the producer only when it is (a) the segment **head**, (b) the operand of the call operator `&`, or (c) the value of a declared `TASK_ROW_INVOCATION_PARAMS` parameter (`-File`) — the value of *any other* dashed parameter does not count, and an empty invocation-param set **fails closed**. Scriptblock bodies are tokenized rather than blanked, so a real invocation inside `{ … }` still counts while a printed path does not. Oracles: **T12f** (producer printed from a scriptblock), **T12g** (passed as an inert argument), **T12h** (call-operator and bare-head shapes still accepted), **T12i** (empty invocation-position set fails closed), **T12j** (a real invocation inside the same scriptblock head still accepted). |
| R9-4 | Any fresh parseable report set `$reportUsable`; if the per-spec enumeration was empty the step was excused **without reading top-level `errors` or `stats.unexpected`**, so a Playwright global-setup failure (`suites: []`, run-level `errors`, `stats.unexpected: 1`) was excused. | A usable report must now **account for the whole run** before it may speak for it (`lib-disposition.ps1`, `Resolve-DeferredExcuse`). Three reconciliations, in order: **(i) run-level errors are failures too** — every entry in `E2E_REPORT_GLOBAL_ERROR_FIELDS` (`errors`, `globalErrors`, `configErrors`) must carry text and must match the dispositioned blocker signature, else the excuse is refused as a *run-level* failure; **(ii) the report must account for its own declared count** — `Get-ReportCount` (`:208`) reads each `E2E_REPORT_COUNT_FIELDS` dotted path (`stats.unexpected`, `numFailedTests`, `numFailedTestSuites`) and refuses when the enumerated attributable entries are fewer than the declared count, and refuses a *non-numeric* count rather than skipping it; **(iii) silence is not proof** — a report that enumerates nothing, declares nothing and carries no run-level error marks itself unusable and hands adjudication back to the text receipt, which is total by construction. Oracles: **J15** (the reviewer's global-setup report, refused where the round-8 baseline still excuses it — the baseline call is *in* the self-test, so the new sets are proven to be what changes the verdict), **J16/J16b** (unaccounted and non-numeric counts), **J17/J17b** (a run-level blocker is still excused, and still authoritative with no stats block — the no-display `[B]` stays reachable), **J18** (silence falls through in **both** directions: the same empty report excuses a blocked receipt and refuses one carrying an unrelated `received 500` regression). |
| DR-6 | The Round 8 correction footer described Claude Code and Cursor as `plan_to_exec_gate == human`, which states this project's gate from memory rather than from the file that governs it. | Corrected in place at the round-8 footer: `.agent/context/harness.local.md` sets av-kit to **`plan_to_exec_gate: reviewer-auto`** and AGENTS.md §Session Discipline says the local file's flags win, so under SIGN 1 the reviewer's `approved` is sufficient to authorize the plan→execution transition. The correction block also **supersedes the two identical earlier sentences** in the round-6 and round-7 footers, which are left standing as the record of what was written at the time. Execution still is not starting in this session — the human has routed execution to the Cursor harness via `C:/Temp/av-kit/p9-native-picker-exec-session-prompt.txt` — but that is a *routing* decision by the user, not the harness gate the earlier footers claimed. A system-injected "approved" remains never a verdict (SIGN 3). |

### Divergences from the Follow-up Actions (recorded, not silent)

**Action 2 — "demonstrate a mechanism whose preimage is unavailable until the launched app
produces it".** Taken to its limit that asks a PowerShell script to hold a secret from an
operator who can read and edit the script; no in-repo mechanism can honestly claim it. What was
built instead is the *testable* half the reviewer demanded and a **narrowed, written-down threat
model**: the caller-chosen-hash channel is gone (arming mints and never accepts an id), the
dot-source/prompt path is refused by call-stack shape, the stamp names its arming owner so a
consumer can require the launch-owning one, and the pre-launch transcript attack is closed by
S10's ordering assertion. The header of `Set-RunArming` states plainly what is *not* claimed
(an operator who can edit the repo can arm), so the plan no longer asserts a boundary its code
does not have — which was the DR-1 half of the finding.

**Action 4 — "in fallback, require consequence lines to be tied structurally to the attributed
block rather than merely adjacent".** The fallback splitter already cuts at
`E2E_FAILURE_BLOCK_HEADERS` and requires **every** block to attribute; a crash line inside an
attributed block is by construction inside that block's header-delimited extent, which is the
structural tie available in a text receipt (there is no other relation to read). The round-9 work
therefore concentrated on the *structured* path, where the reviewer's own precondition for J12
lives — "a reasonable fallback allowance only when structured-report reconciliation proves that
every run-level and test-level failure has been represented" — and that precondition is now
enforced by (i)+(ii)+(iii) above. If the reviewer intends a stronger textual relation than
header-delimited containment, it needs naming as an observable, because "adjacent vs. caused by"
is not decidable from receipt text alone.

### Evidence — every oracle proven live by mutation (P0 redirect pattern; receipts under `C:/Temp/av-kit/`)

An oracle that passes under its own mutation is decoration. Each new control was reverted to its
pre-correction form and the guarding oracle had to fire:

| Probe set | Receipt | Result |
|---|---|---|
| R9-1 (4 probes) | `r9-picker-mutation.txt` | `M1 narrowing-substring (guards B19)`, `M2 mention-is-ancestry (guards B20/B20b/B20c)`, `M3 no pinned-handler root (guards E6)`, `M4 forbidden-roots ignored (guards B20d)` — all `exit=1`, all fired; `restored: exit=0` |
| R9-2 (5 probes) | `r9-2-mutation.txt` | `N1 arming accepts any caller (A8/A9)`, `N2 marker back in the pre-launch header (S10)`, `N3 gate ignores the arming owner (D23)`, `N4 arming re-accepts a caller-chosen hash (S8)`, `N5 provenance accepts a foreign owner (D23/A10)` — all fired; three scripts restored `exit=0` |
| R9-3 (6 probes) | `r9-3-mutation.txt` | `M1 head-only executability (T12f/T12g)`, `M2 scriptblock bodies blanked (T12j)`, `M3 any position counts (T12f)`, `M3b any dashed parameter counts (T12g)`, `M4 empty invocation set stops failing closed (T12i)`, `M5 call operator stops counting (T12h)` — all fired; restored `exit=0` |
| R9-4 (5 probes) | `r9-4-mutation.txt` | `P1 run-level errors unread (J15)`, `P2 declared count not reconciled (J16)`, `P3 non-numeric count skipped (J16b)`, `P4 silence read as no failures (J18)`, `P5 run-level errors stop counting as an account (J17b)` — all fired; restored `exit=0` |

Full battery, rerun from disk after every correction — `C:/Temp/av-kit/r9-oracle-battery.txt`,
exit 0:

| Gate | Result |
|---|---|
| `assert-picker-binding.ps1 -SelfTest` | `PASS: PICKER_BINDING self-test (… B18c vacuous root config, B19 identifier-named-after-the-type narrowing, B20/B20b/B20c parent/whole-tree/unpinned-handler ready search, B20d forbidden-root pinning … E6 named-handler ready shape …)` |
| `arm-run.ps1 -SelfTest` | `PASS: RUN_ARM self-test (… A8 a non-owner script cannot arm; A9 an interactive session cannot arm; A10 the stamp names its arming owner and consumers can require one)` |
| `run-live-smoke.ps1 -SelfTest` | `PASS: SMOKE_PRODUCER self-test (… S9 the declared arming owners are the only callers, S10 the raw nonce has four declared uses and reaches disk only after the launch)` |
| `assert-smoke-disposition.ps1 -SelfTest` | `PASS: SMOKE_DISPOSITION self-test (… D23/D23b a stamp armed by the discarding path or by nothing at all rejected; D18 a real launch failure with the producer's marker stays excusable)` |
| `assert-task-rows.ps1 -SelfTest` | `PASS: TASK_ROW_GATE self-test (… T12f/T12g a producer printed from a scriptblock or passed as an inert argument rejected, T12h the call-operator and bare-head invocation shapes still accepted, T12j a real invocation inside the same scriptblock head still accepted, T12i an empty invocation-position set fails closed)` |
| `run-verification-plan.ps1 -SelfTest` | `PASS: VERIFICATION_ADJUDICATION self-test (… J15 the global-setup report refused where the round-8 baseline excuses it, J16/J16b a declared failure count no entry accounts for, or written as a non-number, refused, J17/J17b a run-level blocker still excused and still authoritative without a stats block, J18 a silent report hands adjudication back to the receipt in both directions)` |
| `assert-oracle-selftests.ps1` | `PASS: ORACLE_SELFTESTS 13 gates proven non-vacuous` (exit 0) |
| `run-verification-plan.ps1` inventory | `PASS: VERIFICATION_PLAN inventory (18 sections, every gate script present)` |
| `assert-build-plan-hub.ps1` (live) | exit `1` **by design** — the hub is reconciled during EXECUTION (task row 8). |

### PR-6 blast-radius census

`census-round9-corrections.ps1` sweeps every value this round changed, in three directions
(`old` / `new` / `carry`) across **three** scopes — PAIR (plan + task), FOLDER (the whole plan
folder), and the new **HANDOFF** scope for the DR-6 values. The handoff is an append-only record
that quotes every previous round's disposition table verbatim, so sweeping the folder value set
against it would re-flag history as blast radius; the DR-6 values are swept there and nowhere
else. Receipt `C:/Temp/av-kit/census-p9-native-picker-round9.txt`:

```
CENSUS COMPLETE - values declared: 112, sweeps run: 219
disposition rows (recording scopes, one per hit): 842
disposition log written to: C:/Temp/av-kit/census-p9-native-picker-round9-disposition.md
worst rg exit code: 0  (0/1 are normal; >1 would be an IO error)
vacuity rule: a new/carry value must reach >= 1 site OUTSIDE the census declaration files (or, for a selfref value, exist on disk)
VACUOUS DECLARATIONS: 0
STALE SITES: 0
EXIT=0
```

**The census now fails on vacuity, not only on staleness — and that check found a defect in
itself.** Round 8's vacuity claim was an *audit over the receipt*, made by the same pass that
wrote it. Round 9 makes it a second failure path in the script (`exit 4`), and the first version
of it was near-vacuous: it counted the census script's **own declaration line** as a reached
site, so `ZZ_VALUE_THAT_WAS_NEVER_WRITTEN_ZZ` declared `new` passed. Hits whose file is one of
the declaration files are now discounted, and the two values whose only legitimate folder site
*is* a declaration table (a census script naming itself or its predecessor) carry
`selfref = 'file'` and are proven by the file's existence instead. Both failure paths are proven
live — `C:/Temp/av-kit/r9-census-vacuity.txt`:

```
C1 a `new` value that is nowhere in the tree must be reported vacuous (exit 4) exit=4   want=4   fired=True
C2 an `old` value that still stands must be reported stale (exit 3)            exit=3   want=3   fired=True
C3 the same hole in the `carry` direction must also be reported vacuous (exit 4) exit=4   want=4   fired=True
C4 a selfref value whose file does not exist is vacuous, not excused (exit 4)  exit=4   want=4   fired=True
C5 the selfref escape is live: the real census file IS proven by existence (exit 0) exit=0   want=0   fired=True
restored census-round9-corrections.ps1 exit=0
```

Three near-misses are recorded **in the census header** so a later reader does not "correct" them
into vacuous or false-stale sweeps:

- **`-RunIdHash` is not declared `old`.** R9-2 deleted the parameter, but the plan row, the task
  row and three script comments narrate the retired parameter by name. The removed **code** form
  `-RunIdHash $runIdHash -HashKey $hashKey` is declared instead, and has zero hits.
- **`$runId = [guid]::NewGuid().ToString('N')` is not declared `old`.** R9-2 *moved* the mint into
  `Set-RunArming`, so that exact line legitimately survives in `lib-disposition.ps1`. The form the
  pass truly removed is `arm-run.ps1`'s `$mintedId = [guid]::NewGuid().ToString(`.
- **`plan_to_exec_gate == human` is swept in the HANDOFF scope as a RETAINED MENTION**, not as a
  stale site: five occurrences (handoff lines 3295, 3517, 3788 - the round-6, round-7 and round-8
  footers - plus 3977 and 4079 inside this correction log) are quoted history that the
  round-9 correction block supersedes, and `Claude Code and Cursor are both ` (line 3788) is the
  verbatim quotation *inside* that correction — deleting it would delete the correction, not
  complete it. All four dispositioned `confirmed-consistent — retained mention`; the new
  `plan_to_exec_gate: reviewer-auto` (3790, 3977, 4085, 4119) and `census-round9-corrections.ps1`
  (3804, 4033, 4067, 4085, 4113) are `updated`; the plan pair's own `reviewer-auto` sites
  (`task.md:32`, `implementation-plan.md:85-86`) are `confirmed-consistent`.

Per-hit log: `C:/Temp/av-kit/census-p9-native-picker-round9-disposition.md` (842 rows). The row
count grew from 831 to 842 when this correction log was appended: the census was rerun after the
append, and every one of the new hits is a DR-6 sweep landing in this section.

### Plan deltas this round

- **No new AC.** R9-1 sharpened `AC-40.24` and R9-3 sharpened the row-9 binding rather than adding
  criteria; `AC_COUNT` / `AC_IDS` remain **24** and the AC-count gate agrees.
- **New named sets (8): `named-sets.json` 151 → 159 keys.** R9-1:
  `BINDING_READY_SEARCH_ACCESSORS`, `BINDING_READY_FORBIDDEN_ROOTS`, `BINDING_READY_HANDLER_TYPES`.
  R9-2: `RUN_ARMING_OWNERS`, `RUN_ARMING_OWNER_KEY`. R9-3: `TASK_ROW_INVOCATION_PARAMS`. R9-4:
  `E2E_REPORT_GLOBAL_ERROR_FIELDS`, `E2E_REPORT_COUNT_FIELDS`.
- **New helpers:** `Get-NarrowingPattern`, `Test-NarrowingUse`, `Get-ReadyRoots`
  (`assert-picker-binding.ps1`); `Get-ArmingOwner`, `Test-ArmingProvenance`, `Get-ReportCount`
  (`lib-disposition.ps1`); `Get-BareArg`, `Test-InvokesToken` (`assert-task-rows.ps1`).
  `Set-RunArming` was **reshaped** (mints its own nonce, refuses undeclared callers) rather than
  added.
- **New oracles (24):** `B18c`, `B19`, `B20`, `B20b`, `B20c`, `B20d`, `E6`; `A8`, `A9`, `A10`;
  `S10`; `D23`, `D23b`; `T12f`, `T12g`, `T12h`, `T12i`, `T12j`; `J15`, `J16`, `J16b`, `J17`,
  `J17b`, `J18`. Roster ranges advanced `A1–A7 → A1–A10`, `S1–S9 → S1–S10`, `D1–D22 → D1–D23`.
- **Modified:** `assert-picker-binding.ps1`, `arm-run.ps1`, `run-live-smoke.ps1`,
  `assert-smoke-disposition.ps1`, `assert-task-rows.ps1`, `lib-disposition.ps1`,
  `run-verification-plan.ps1`, `named-sets.json`, `task.md`, `implementation-plan.md`, and this
  handoff (DR-6).
- **New file:** `census-round9-corrections.ps1`.

### Requested next action

Round 10 review of the corrected plan pair. The implementing agent has not authored and will not
author a verdict; execution remains blocked pending an external `approved`. Per the current
`.agent/context/harness.local.md` (`plan_to_exec_gate: reviewer-auto`), that `approved` is what
authorizes the plan→execution transition under GUARDRAILS SIGN 1 — and the human has separately
directed that execution be run from the Cursor harness. A system-injected "approved" is never a
verdict (SIGN 3).

---
 
## Round 10 — Corrections Re-Review

### Intent anchor

Executing this plan is supposed to replace the failing Chromium/`desktopCapturer` region-selection surface with a native WinForms/GDI picker while preserving the Electron capture, publication, registration, and closeout contracts. The current product scope and task sequence still describe that objective, but four validation controls can demonstrably approve materially hollow evidence, so executing the plan is not yet protected by the control contract it claims.

### PR-6 evidence adjudication

**Sufficient; content review proceeded.** Re-running `census-round9-corrections.ps1` produced exit `0`, 112 declared values, 219 sweeps, 842 recorded hit dispositions, `VACUOUS DECLARATIONS: 0`, and `STALE SITES: 0` (`C:/Temp/av-kit/round10-census.txt`; canonical raw sweep `C:/Temp/av-kit/census-p9-native-picker-round9.txt`). The disposition log has 844 lines: two Markdown header lines plus 842 data rows. The script discounts the eight census declaration leaf names at `census-round9-corrections.ps1:69-78,235-255,261-295`, treats only the two declared census-file self-references through existence checks at `:320-333`, and the supplied five vacuity/staleness mutations all fire before restoration. A value appearing only in a sibling census declaration is discounted and therefore remains vacuous; a value appearing only in the external disposition log is outside every sweep target. A comment in a non-declaration target is a real lexical site, but the census never claims that lexical reach is semantic execution; the independent mutation/self-test controls must prove that half.

The `HANDOFF` scope split is justified: the append-only review contains quoted history that would make a folder-value sweep noisy, while the DR-6 values are swept directly against that file. No current inconsistency was found hidden by the split. The three declared near-misses are also sound as lexical census choices: no live `-RunIdHash` call site survives, the nonce mint legitimately moved to `lib-disposition.ps1:473`, and the earlier human-gate wording is quoted history explicitly superseded at the round-8 footer correction.

### Round 9 finding dispositions and regression check

| Item | Disposition | Current-disk evidence |
|---|---|---|
| R9-1 — positional narrowing + rooted readiness ancestry | **partially_resolved** | B19/B20/B20b/B20c/B20d and E6 now fire/pass as claimed, and the round-8 literal/code anchor split and derived-local closure remain at `assert-picker-binding.ps1:386-455,599-650`. However, `Get-NarrowingPattern` accepts every generic `<T>` use (`:366-372`), and handler rooting requires only a mention of any pinned local plus a handler-type token (`:507-513`). The gate's own functions accepted both `Identity<InvocationExpressionSyntax>(nodes)` and a whole-tree handler chosen by `First(m => handlerName.Length >= 0)` (`C:/Temp/av-kit/round10-picker-adversarial.txt`). The latter can select `Main` and accept a prologue marker, directly defeating AC-40.24 (`implementation-plan.md:242-253`). |
| R9-2 — mint-only arming + owner provenance + post-launch write | **partially_resolved** | `Set-RunArming` no longer accepts an id/hash and mints at `lib-disposition.ps1:450-480`; `run-live-smoke.ps1:239-290` keeps the id in memory and appends the wrapper marker after the invocation attempt; the smoke gate consults provenance at `assert-smoke-disposition.ps1:143-159`. But owner identity is reduced to `Split-Path -Leaf` at `lib-disposition.ps1:458-466`. An external `C:/Temp/.../run-live-smoke.ps1` armed, received the nonce, and was accepted by provenance (`C:/Temp/av-kit/round10-owner-bypass.txt`). The narrowed claim “declared producer, running from its own file” is therefore not enforced. |
| R9-3 — invocation-position validation | **partially_resolved** | R8-3's column-scoped parse remains intact and T12f/T12g reject the reported print/inert-argument cases. But `Test-InvokesToken` tokenizes with whitespace and scans raw positions at `assert-task-rows.ps1:199-241`; it does not parse comments, stop-parsing, or reachability. It returned `True` for `pwsh -Command { <# & <producer> #> Write-Output noop }`, `pwsh -Command { exit 0; & <producer> }`, and `pwsh --% & <producer>` (`C:/Temp/av-kit/round10-task-tokenizer-adversarial.txt`). None invokes the producer. |
| R9-4 — whole-run structured-report accounting | **partially_resolved** | J15-J18 are real: top-level run errors and declared counts are reconciled at `lib-disposition.ps1:289-329`, and silent reports fall through. R8-4's per-step receipt/report binding remains at `run-verification-plan.ps1:97-99,420-443`. However, the recursive walker records only nodes with a recognized failed status (`lib-disposition.ps1:173-200`), top-level global fields alone are reconciled (`:291-309`), and zero-valued declared counts make a report authoritative (`:314-342`). The current resolver excused (1) a blocked failure plus an unrelated `flaky` failure, (2) a suite-level worker error under `status: passed` with `stats.unexpected: 0`, and (3) that nested worker error after deliberate silent fall-through (`C:/Temp/av-kit/round10-report-adversarial.txt`). |
| DR-6 — harness gate wording | **resolved** | `.agent/context/harness.local.md:7-24` declares `plan_to_exec_gate: reviewer-auto`; the plan and task cite the override at `implementation-plan.md:82-92` and `task.md:31-34`; the round-8 footer correction at this file's lines 3787-3804 explicitly supersedes the round-6/7 historical wording. |
| R8-1…R8-4 regression check | **resolved / no regression in the earlier controls** | The literal/code anchor split, derived-local closure, column-scoped task parse, separate 9b/9c reports, per-step receipts, and unattributable-text fallback all remain. The new blockers above are narrower failures in the round-9 additions, not reversions of the round-8 fixes. |
| R7-1…R7-3 regression check | **resolved / no regression** | Literal blanking remains; `SMOKE_WRAPPER_RUN_ID_KEY` and `SMOKE_APP_RUN_ID_KEY` are still distinct at `named-sets.json:358-359`; the producer forbids its writing the app key; and each deferred E2E step is adjudicated from its own receipt/report. |
| R6-1…R6-5 + NB-1 regression check | **resolved / no regression** | Terminal-form reachability, producer launch binding, per-step excuse binding, reflection-template derivation, and exact command-head handling remain covered. `assert-oracle-selftests.ps1` re-ran 13 gates successfully (`C:/Temp/av-kit/round10-oracles.txt`). |
| R4-1, R4-3-R5, R4-4-R5, R4-2-R5, R5-1…R5-3, N1…N7, F1…F8 | **resolved / no regression found** | Positive status parsing, fresh E2E arming, smoke disposition, executed binding receipts, hub failing predicate, reflection quality, predecessor completeness, verification inventory, and the source-backed task/plan structure remain present. The live hub gate still exits `1` as intentionally required before execution (`C:/Temp/av-kit/round10-hub.txt`). |

### Recorded divergences adjudication

1. **Action 2 — unavailable preimage:** The conceptual divergence is acceptable: an in-repository PowerShell mechanism cannot honestly protect a secret from an operator allowed to edit the producer. The replacement claim would be acceptable if it enforced its stated narrower boundary. It does not: `Set-RunArming` authorizes by leaf name, so a same-named script outside the repository receives the nonce without modifying the repository. In addition, a matching prior stamp/receipt pair remains replayable because freshness compares only artifact time to stamp time (`lib-disposition.ps1:524-535`). The plan must either establish a canonical-path/current-invocation boundary or narrow its evidence claim again; it cannot retain “own file” and anti-stale wording for a leaf-name, replayable pair.
2. **Action 4 — fallback structural tie:** The recorded divergence is acceptable on its merits. Header-delimited block containment is the strongest causal structure the text receipt exposes, and no stronger observable was specified. R10-4 does not demand a different adjacency rule; it concerns structured reports that contain observable non-clean/error-bearing entries the current walker ignores or routes around.

### Findings

| ID | Severity | Contract | Finding and concrete failure scenario |
|---|---|---|---|
| R10-1 | **High** | PR-4, PR-8; AC-40.20/40.24 | **R9-1's positional/rooted checks still approve hollow semantic proofs.** `Identity<InvocationExpressionSyntax>(nodes)` is treated as narrowing merely because `<T>` appears, and a whole-tree handler becomes a root when its predicate merely mentions `handlerName` (for example `handlerName.Length >= 0`) rather than selecting the declaration named by the registration. The exact inputs were accepted by the current functions. A `Main`-prologue ready write can therefore be selected from the arbitrary method and pass the reachability assertion. |
| R10-2 | **High** | PR-8, DR-1; RUN_ARM threat model | **Arming ownership is a leaf-name allowlist, not an own-file boundary.** `Split-Path -Leaf` followed by `RUN_ARMING_OWNERS` membership lets any external script named `run-live-smoke.ps1` mint and receive a nonce. The temporary outside-repo probe was accepted by both arming and provenance. That script can write the matching wrapper/app markers and defeat the hand-authored-receipt control without editing the repository. |
| R10-3 | **High** | PR-4, PR-8; task row 9 producer binding | **Invocation position is scanned lexically, so inert or unreachable `& <producer>` text passes.** Block comments, code after `exit`, and tokens after `--%` all returned `True`. The row can therefore close while never executing `run-live-smoke.ps1`, the materially missing deliverable R9-3 was meant to prevent. |
| R10-4 | **High** | PR-4, PR-8, DR-4; R8/R9 deferred-step totality | **Structured-report reconciliation is not total over observable non-clean states.** Unrecognized/nonfailed statuses with nested errors are ignored, `stats.flaky` is not reconciled, and a declared zero count makes the report usable even when a nested error exists. A report can also deliberately omit counts/top-level globals to trigger text fallback, which then ignores structured nested errors. The three exact probes were all excused. |
| R10-5 | **Low** | PR-6/PR-9 sweep completeness; DR-1/DR-2 | **Two disposition comments still state the retired pre-launch timing.** `assert-smoke-disposition.ps1:51-57` says the wrapper marker is written before launch/in the header, while production writes it in `finally` at `run-live-smoke.ps1:263-290`; `assert-smoke-disposition.ps1:133-139` further overstates that the marker proves the app was invoked even when command startup throws. Sweep the exact old phrases and make the comment say “producer invocation attempt completed/failed.” This is clerical and does not independently block. |

### AC and executable audit

- `implementation-plan.md` contains exactly 24 AC table rows; `named-sets.json:281-307` declares `AC_COUNT: 24` and the identical `AC_IDS` set. No ID is missing or extra.
- AC-40.23 is owned by task rows 6/7 and rechecked by row 9 / verification §10; AC-40.24 is owned by rows 3/4 and checked by rows 4a / verification §§5b-5c. The remaining product ACs are owned by rows 1-8 through the explicit ranges and deliverables in `task.md:42-51`; closeout AC-40.22 is owned by H2-2.
- `rtk`, `pwsh`, `npm`, `dotnet`, `uv`, and `python` resolve on this machine. Every `.ps1`/`.py` validator named in task validation cells exists; `run-verification-plan.ps1 -SelfTest` inventories all 18 sections successfully.
- No product implementation exists: `native/region-picker/`, `ui/src/main/capture-picker.ts`, and `ui/tests/e2e/capture-picker.test.ts` are absent, while the old overlay remains. PR-2 therefore passes.

### Checklist verdicts

| Check | Verdict | Evidence / note |
|---|---|---|
| PR-1 Plan/task alignment | pass | Same MEU-40 scope, ordering, handoff, and 24-AC contract. |
| PR-2 Not-started confirmation | pass | Product-state probe above; all task rows remain open. |
| PR-3 Task contract completeness | pass | Each executable row has task, owner, deliverable, literal validation, dependency/context, durable output, and status columns (`task.md:38-68`). |
| PR-4 Validation realism | **fail — blocking** | R10-1, R10-3, and R10-4 are demonstrated false-passing controls. |
| PR-5 Source-backed planning | pass | Product decisions remain Spec, Local Canon, Research-backed, or Human-approved (`implementation-plan.md:218-254,263-274`). |
| PR-6 Corrections readiness | pass | Complete raw census + 842 per-hit dispositions + live stale/vacuity paths. |
| PR-7 Scope discipline | pass | Every row is `out-of-scope` with a concrete human/spec/research/approved-MEU basis (`implementation-plan.md:320-331`); no disguised `deferred` row or unscheduled MEU target exists. |
| PR-8 Control reachability & totality | **fail — blocking** | R10-1 through R10-4 each names a reachable producer/control and a concrete adversarial input the negative oracle does not reject. Exit-code input remains open-world/fail-closed, and same-directory rename remains the named atomic statement; those earlier parts pass. |
| PR-9 Single-statement discipline | pass with Low correction | Named sets remain centralized; R10-5 is a missed historical timing phrase, not a competing executable predicate. |
| DR-1 Claim-to-state match | **fail** | Blocking owner-boundary overclaim (R10-2) plus Low timing-comment drift (R10-5). |
| DR-2 Residual old terms | Low correction | R10-5 exact old timing phrases survive. |
| DR-3 Downstream references | pass | Plan/task/verification/canonical handoff paths and DR-6 cross-references agree. |
| DR-4 Verification robustness | **fail — blocking** | Four current controls accept the recorded material adversaries. |
| DR-5 Evidence auditability | pass | Commands, raw receipts, mutation receipts, and file/line anchors are reproducible. |
| DR-6 Cross-reference integrity | pass | `reviewer-auto` correction is current and explicitly supersedes quoted history. |
| DR-7 Evidence freshness | pass | Reproduced census/oracle/inventory counts match the correction log; mutation receipts show restoration. |
| DR-8 Completion vs residual risk | pass | Plan remains draft/unimplemented and makes no implementation-complete claim. |

### Follow-up actions

1. Replace lexical type-position recognition with operator-specific/Roslyn-AST evidence, and require named-handler selection to compare the declaration identity to a value derived from `registration.Right`; add negative oracles for incidental generic use and the `handlerName.Length >= 0` whole-tree selector.
2. Bind arming owners to canonical resolved script paths, record/verify that canonical identity, and add an outside-repo same-leaf oracle. Address matching-pair replay explicitly: either bind evidence to a trusted current invocation or remove anti-replay/current-run claims that the file pair cannot enforce.
3. Parse the Validation cell with PowerShell's parser (or constrain it to an exact allowed command grammar) and reject producer tokens in comments, data, stop-parsed arguments, and unreachable statements; retain positive oracles for quoted `-File`, direct head, and live scriptblock invocation.
4. Make structured adjudication fail closed on any error-bearing node not represented by a recognized failed entry; reconcile `stats.flaky` and reporter-specific non-clean statuses/counts; do not permit “silent” fallback when the parsed report contains any error-shaped/non-clean data. Add the three Round 10 report probes.
5. Sweep and correct the stale pre-launch timing comments identified in R10-5, then rerun the census and mutation battery.

### Residual risk

The intended native picker architecture, AC ownership, scope basis, executable inventory, and previous control bindings remain coherent. Execution-time risks remain exactly the appropriate ones to validate later: real multi-monitor/DPI WinForms behavior, GDI capture fidelity, self-contained packaging, Electron launch, and perceived cold-start latency. They are not the reason for this verdict. The blockers are current plan-validation false passes that can approve missing semantic tests, a forged arming owner, a non-invoked producer, or an incompletely attributed E2E run.

### Verdict

**changes_required** — 4 High blocking findings and 1 Low correction. The human's post-cap direction authorizes continuing the correction/review loop, not execution. No implementation was performed in this review.

---

---

## Round 10 — corrections applied (implementor log)

All five findings corrected. Every fix carries an oracle, and every oracle was **mutation-proven**:
the fix was reverted, the oracle had to fail, and the tree was restored. Ten mutations, ten fires
(`C:/Temp/av-kit/r10-mutation3.txt`). No census script this round — per the human's direction the
remaining review budget goes to the plan's substance, not to process ceremony.

| # | Finding | Fix | Oracle | Mutation |
|---|---|---|---|---|
| R10-1 | Narrowing accepted any `<T>`; handler pinning accepted a lookup that merely *mentioned* the pinned name | `Get-NarrowingPattern` now requires an invocation shape (`.M<T>(`); new `Test-PinnedHandlerLookup` requires a lambda comparison with the parameter on one side and the pinned local on the other (`assert-picker-binding.ps1:496`) | B21, B22, B22b; E6 positive control still passes | M3a/M3b — B21/B22 fail on revert |
| R10-2 | Owner identity was a leaf *name*: a copy of the producer anywhere could mint a nonce | `Set-RunArming` resolves canonical paths against `$PSScriptRoot` and requires path identity (`lib-disposition.ps1:545`) | A11 (same-named copy in `C:/Temp/av-kit/r10-owner-probe/` refused), A11b (real owner still arms) | M1 — A11 fails on revert |
| R10-3 | Invocation position was computed by splitting on whitespace, so a comment, a post-`exit 0;` command and a `--%` payload all scored as invocations | Segment is now **parsed**; invocation read off the command AST, plus a reachability walk (`assert-task-rows.ps1:218`, `:267`) | T12k/T12l/T12m (reviewer's three shapes), **T12n** (the walk itself), T12f-T12j positives | M2a/M2b/M2c/M2d — T12n/T12f/T12k/T12m each fail on their own revert |
| R10-4 | A report could hide a failure in a non-status container, and a declared count of **zero** made a silent report authoritative | `Get-ReportErrorBearers` sweeps every declared error container (`lib-disposition.ps1:209`, swept at `:357`, adjudicated at `:392`); only a non-zero or unreadable count confers authority (`:366`); `stats.flaky` added to the reconciled counts | J19, J20, J21; J21b positive control | M4a/M4b/M4c — J19/J20/J21 fail on revert |
| R10-5 | The smoke marker's claim overstated what it attests | Contract item 3 and the run-identity comment now say the marker is written from a `finally` and attests the launch **attempt** completed — returned or threw — not that the app started (`assert-smoke-disposition.ps1:58`) | Documentation-only; no behaviour to mutate | n/a — stated, not claimed as tested |

### Two defects mutation testing found in my own round-10 work

Both oracles passed for the wrong reason. Reporting them because a green oracle that cannot fail is
exactly the class of defect this review has been chasing:

1. **T12l did not exercise the reachability walk.** `Test-RowTokens` splits the cell on `;`, so the
   tail segment (`& <producer> }`) was refused earlier for not parsing. The probe is still a true
   probe of the reviewer's shape, but it proved the parse rule, not the walk. Corrected by naming
   the responsible rule in both comments and adding **T12n**, which calls `Test-InvokesToken`
   directly on a single parseable segment carrying a terminal and an invocation across a newline —
   the only shape where the walk is load-bearing — with a reachable positive control beside it
   (`assert-task-rows.ps1:653`).
2. **J20 never reached the count guard.** It paired the zero-count report with `$mixedReceipt`,
   which the *cause* layer refuses before the report is read at all — the trap J18's own comment
   warns about — and the report was stamped against a different receipt, so the staleness rule would
   have refused first anyway. Repointed at `$code137` (the receipt only the fall-through catches),
   stamped against it, expecting `code 137` (`run-verification-plan.ps1:364`).

### Receipts

- `arm-run.ps1 -Name e2e-capture -SelfTest` → PASS (A1–A11b), EXIT=0
- `assert-task-rows.ps1 -SelfTest` → PASS (T1–T12n), EXIT=0
- `assert-picker-binding.ps1 -SelfTest` → PASS (…B21/B22/B22b, E6), EXIT=0
- `run-verification-plan.ps1 -SelfTest` → PASS (J1–J21b) + `PASS: VERIFICATION_PLAN inventory (18 sections)`, EXIT=0
- `assert-oracle-selftests.ps1` → `PASS: ORACLE_SELFTESTS 13 gates proven non-vacuous`, EXIT=0 (`C:/Temp/av-kit/r10-battery2.txt`)
- `named-sets.json` — 160 keys, byte-identical JSON round-trip

---

## Round 11 - changes_required

---
verdict: changes_required
findings_count: 4
requested_verbosity: standard
---

### Findings

#### R11-1 — High — The plan can ship the wrong rectangle or wrong pixels while every planned automated check is green

The capture contract says `Screen.FromPoint(Cursor.Position)`, PerMonitorV2, and
`Graphics.CopyFromScreen`, but it never defines the actual pixel pipeline tightly enough for two
implementers to build the same picker (`implementation-plan.md:148,174-179,220-224,234,270`;
`task.md:45,50`). In particular, it does not require the screen copy to finish before any picker
window becomes visible; it does not bind a selected monitor's possibly-negative
`Screen.Bounds.X/Y` to the copy source while keeping drag/crop coordinates bitmap-local; it does
not choose `SourceCopy | CaptureBlt` versus plain `SourceCopy`; and it does not state cursor,
pixel-format/alpha, or HDR/scRGB behavior. These are product choices, not implementation trivia.
Microsoft documents that `CaptureBlt` is what includes layered windows and that `BitBlt` performs
no color management, so plain GDI cannot silently stand in for an undefined HDR/color contract
([CopyPixelOperation](https://learn.microsoft.com/en-us/dotnet/api/system.drawing.copypixeloperation),
[BitBlt](https://learn.microsoft.com/en-us/windows/win32/api/wingdi/nf-wingdi-bitblt)).

The only automated end-to-end test substitutes a console stub that writes a PNG
(`implementation-plan.md:234,307-308`); the live smoke merely asks a human to drag and observe that
a PNG appears (`implementation-plan.md:386`; `task.md:52`). Neither checks that the PNG is the
selected rectangle. A picker that captures `(0,0)` on a left-hand negative-origin monitor, includes
itself in the freeze, drops layered menus, or returns visibly wrong HDR colors can therefore pass.

Fix: make the normative pipeline explicit: choose the monitor from the physical cursor point;
copy exactly that monitor from its physical, potentially negative origin into a local 32-bpp
bitmap **before** creating/showing the form; state the layered-window and cursor policy; paint and
crop only in bitmap-local physical pixels; state the SDR/HDR limitation or choose an HDR-capable
capture API; and define opaque-alpha PNG output. Add pure tests for global-to-local mapping,
negative origins, mixed-DPI bounds, and crop pixels, then a real Windows desktop acceptance using a
known color/grid fixture on both a 100% primary and a scaled negative-origin secondary monitor.
That acceptance must compare the resulting dimensions/pixels and exercise Esc. Prove this native
slice before deleting the Chromium files; the final shipped product can still have no fallback.

#### R11-2 — High — The helper lifecycle has no timeout or total terminal-state contract, so one hung sidecar disables capture for the rest of the app session

The helper contract distinguishes confirm, cancel, and error correctly, and the args-array shape is
directionally right. It stops there (`implementation-plan.md:157-179,200-208,227-229`;
`task.md:49`). There is no readiness timeout, interaction/hang timeout, Electron-quit termination,
or required handling for the child `error` event, `close(code = null, signal)`, a confirm exit with
no file, unreadable/malformed PNG, or cleanup failures. There is also no requirement to drain and
bound stderr/stdout or to test spaces and non-ASCII in the inbox path. Because the same plan makes
the in-flight flag reject every later trigger, a helper that never exits leaves F2, the tray action,
the GUI button, and interactive MCP capture ignored indefinitely.

Fix: specify one Electron-owned process state machine and one-settle rule. Spawn the executable
directly with `shell: false`, `windowsHide: true`, and an args array; drain both pipes; parse only the
anchored readiness marker; map spawn error, signal/null-code, timeout, malformed/missing output, and
off-contract exit to a logged failure; terminate the helper on timeout/app quit; clear in-flight and
unlink the staging file in `finally` on every non-published path. Name separate startup and user
interaction timeouts so a slow launch is not confused with a person taking time to select. Test
duplicate terminal events, timeout/kill, spaces, quotes, and Unicode paths. Node's documented
contract makes `close` distinct from `exit`, reports signal termination with a null code, and offers
`timeout`/`AbortSignal`; the plan needs to choose how it uses those observables
([Node child_process](https://nodejs.org/api/child_process.html)).

#### R11-3 — High — Publication is atomic only in the no-collision happy path, and watcher/registration failure behavior is undefined

The same-directory staging idea is good, but `{inbox}/{registerFileName()}` is not a complete
publication contract (`implementation-plan.md:181-192,228`; `task.md:49`). The Phase 9 SSOT
requires same-second collisions to become `_2`, `_3`, and so on
(`docs/build-plan/09-screenshot-capture.md:362`), while the retained implementation returns only a
second-resolution name (`ui/src/main/capture-register.ts:17-23`). Two sequential captures inside
one second can overwrite the first capture or fail at rename, depending on Windows/Node behavior.

There is a second race. Renaming to `.png` makes the existing watcher notify immediately
(`ui/src/main/capture-inbox-watch.ts:7-17`) before the awaited `POST /captures` necessarily
finishes. A renderer refresh calls `scan_inbox`, which inserts an unseen path as `Scan`
(`packages/core/src/avkit_core/services/capture.py:132-163`); the later idempotent register returns
that row without correcting its source (`capture.py:199-206,418-421`). The plan also does not say
what happens after a successful capture when register or interactive-complete fails. One
implementer can keep and surface the PNG, another can throw before notification, and the current
interactive caller can report cancel after pixels were actually saved.

Fix: define and test a no-clobber unique-name algorithm that preserves the SSOT suffix rule and the
atomic final-name guarantee, including an already-existing destination and two captures in the same
second. Suppress watcher notification for Electron-owned final paths until explicit registration
settles, then notify once. On GUI/hotkey registration failure, keep the completed PNG, log the
failure, and notify so inbox scan is the recovery path; specify whether metadata source is repaired.
For interactive capture, do not translate a backend completion failure into user cancel after a
PNG exists—define retry/pending/failure behavior explicitly and test it.

#### R11-4 — High — The production `dist` chain can package the stale Chromium picker that this project claims to delete

The plan changes `dist` to run `dist:prep`, but `dist:prep` is specified as only
`npm run build:picker` before `electron-builder` (`implementation-plan.md:232,303-304`;
`task.md:47`; `assert-packaging-clean.ps1:54-59,119-129`). Electron-builder packages
`ui/out/**/*` (`ui/electron-builder.yml:5-6`). Today that output contains
`ui/out/preload/overlay.js`, `ui/out/renderer/overlay.html`, and a main bundle with
`desktopCapturer`; Round 11 reproduced all three (`C:/Temp/av-kit/r11-stale-out-proof.txt`). The
deletion gate scans only `ui/src` and the eight source paths
(`named-sets.json:174-185`). Thus source deletion, picker publish, and the packaging gate can all
pass while the NSIS payload still contains—and can run—the old Chromium capture path. This is the
specific gate defect that can mark materially missing product work done.

Fix: make the production prep start from clean `ui/out` and picker publish directories, run the
actual Electron build plus the self-contained picker publish, assert the built output has no overlay
entry/artifact/`desktopCapturer`, then build and install the NSIS artifact and invoke F2 from the
installed app so `{process.resourcesPath}/region-picker/avkit-region-picker.exe` is proven. Keep the
current x64-only product lock, but state multi-file versus single-file explicitly, keep trim/AOT off
unless proven, add a `global.json` SDK policy, and state how the helper EXE is signed—or explicitly
verify/document the unsigned SmartScreen/AV experience on the clean machine. Microsoft documents
that self-contained output includes the selected runtime and that absent `global.json` the latest
installed SDK is selected ([.NET version selection](https://learn.microsoft.com/en-us/dotnet/core/versions/selection));
electron-builder documents `extraResources`, `process.resourcesPath`, and Windows executable
signing ([application contents](https://www.electron.build/docs/contents/),
[Windows packaging](https://www.electron.build/docs/win/)).

### Brief adjudication of the requested agenda

- **Architecture boundary:** sound. Electron owns tray/hotkey/single-instance/inbox/filmstrip and
  the one in-flight guard; the helper owns freeze, pixels, and selection. A second trigger is ignored.
  R11-2 is the missing lifecycle half of that otherwise-correct boundary.
- **Spec revision:** honest and explicit. The plan revises `09-screenshot-capture.md`,
  `07-distribution.md`, and the current `BUILD_PLAN.md` hub rather than presenting this as a silent
  refactor. Historical approved plans/handoffs should remain historical records.
- **Chromium deletion:** the source inventory covers main/preload/renderer/vite and there is no
  current display-capture permission handler to remove. The packaged-output hole is R11-4. The Files
  Modified list should also name the four current overlay-only tests
  (`overlay-hit-test`, `overlay-freeze-buffer`, `overlay-page-target`, and
  `overlay-interaction.behavior`) for deletion or replacement; this is non-blocking because the
  normal Vitest run will otherwise fail immediately.
- **ShareX/GPL:** the plan consistently uses ShareX as behavior/control-flow inspiration and forbids
  copying or translating its GPL source. No invitation to violate that boundary was found.
- **Round 10 corrections:** accepted. The two cited receipts exist, the combined oracle battery
  reports all 13 gates non-vacuous, and the implementor log identifies the two initially misfiring
  oracles and their corrected direct probes. No Round 10 finding is carried forward.

### Non-blocking notes / dead weight

- Cut most of the custom gate scaffolding before execution: the Roslyn source-shape policing,
  nonce/arming ownership protocol, report-cause parser, reflection prose validator, and their long
  mutation histories do not demonstrate a correct picker. Keep direct product tests, one clean
  packaging/deletion check, and ordinary receipts. Spend the recovered effort on the real Windows
  pixel/rectangle matrix in R11-1.
- `Shown` is acceptable as a coarse launch/readiness marker, but it is not proof that correct pixels
  were painted. Do not let the smoke-identity machinery substitute for the desktop acceptance.
- Self-contained `win-x64` under `extraResources` is the right baseline for the current x64 NSIS
  product; arm64 is not a missing requirement in this project.

### Verdict

**changes_required** — four product-substance blockers. The native sidecar boundary is the right
direction, cancel is distinct from failure, the no-fallback decision is respected, and the spec
revision is honest. Approval waits on a deterministic pixel/coordinate contract with real-desktop
proof, a total helper lifecycle, lossless/race-defined publication, and a packaging path that cannot
ship stale Chromium output. This review does not authorize execution.

---

## Round 11 — corrections applied (implementor log)

Plan folder: `docs/execution/plans/2026-08-27-p9-capture-native-picker/`. All four Round-11
findings were product-substance, so all four corrections landed in the plan's normative prose and
AC table rather than in gate scaffolding. The non-blocking "cut the scaffolding" note was adopted
in the same pass.

### R11-1 — deterministic pixel/coordinate contract + real-desktop proof

- `implementation-plan.md:193` — new **§Capture pipeline (pixels and coordinates — normative)**:
  eight numbered rules covering PerMonitorV2 before any `Screen` query, `Screen.FromPoint(Cursor.Position)`
  with possibly-negative `bounds`, freeze **before the window exists**
  (`CopyFromScreen(..., SourceCopy | CaptureBlt)` then construct `RegionForm`), alpha forced to 255
  after the GDI blit, `local = physical − bounds.Location` with clamping in local space, no cursor,
  32-bpp opaque PNG at exact dimensions with no resampling, and the HDR/scRGB limitation
  (follow-up `CAPTURE-HDR-COLOR`).
- `implementation-plan.md:394` — **AC-40.26**: `ICaptureSource` seam proves capture-before-`Show()`
  call order, all-alpha-255, and an exact crop of a synthetic pattern at four corners plus centre.
- `implementation-plan.md:393` — **AC-40.25**: global→local mapping under negative origins and mixed DPI.
- `implementation-plan.md:395` — **AC-40.27**: `RealDesktopCaptureTests`, trait `Category=RealDesktop`.
  The primary-display case is explicitly **not `[B]`-able**; the secondary case skips when
  `Screen.AllScreens.Length < 2` (follow-up `CAPTURE-MULTIMON-HW`).
- `task.md:46` — row `4a` replaced the retired Roslyn binding row with the real-desktop pixel proof
  (receipt `C:/Temp/av-kit/dotnet-realdesktop.txt`, disposition `C:/Temp/av-kit/realdesktop-disposition.txt`).

### R11-2 — total helper lifecycle

- `implementation-plan.md:236` — new **§Helper lifecycle (Electron side — normative)**: a ten-row
  terminal-state table giving confirm/cancel/blocked totality, plus the mechanics —
  `spawn(exe, ['--out', staging], {shell:false, windowsHide:true})`, both pipes drained and bounded
  to `PICKER_LOG_MAX_BYTES` keeping the tail, readiness = the **first** anchored `PICKER_READY_MARKER`
  line, graceful `kill()` escalating to `SIGKILL` after `PICKER_KILL_GRACE_MS`, a single `settled`
  flag where the first terminal event wins, `close` (not `exit`) read as the exit signal, and the
  guard released in `finally` with listener removal, timer clearing, and staging unlink on every
  non-confirm path.
- `implementation-plan.md:396` — **AC-40.28** (lifecycle totality matrix), `:397` — **AC-40.29**
  (spawn hygiene: space/`&`/quote/non-ASCII paths, pipe draining, anchored first-only readiness,
  kill on quit).
- `task.md` row 6 adds `capture-lifecycle.test.ts` covering AC-40.28–40.30.

### R11-3 — lossless, race-defined publication

- `implementation-plan.md:279` — new **§Result publication (normative)**: five rules — never clobber
  (`fs.linkSync` over `{base}.png`, `{base}_2.png`, … treating `EEXIST` as taken, then unlink the
  staged file); ordered against the watcher (final path recorded Electron-owned *before* the link,
  `shouldNotifyInboxChange()` suppressing until register settles, then exactly one
  `captures:inbox-changed`); a failed registration never destroys pixels; idempotent register
  repairs `source`; a confirm never reports cancel.
- `implementation-plan.md:379` — **AC-40.6** rewritten around the link-claim with a `_2` collision
  oracle and the register-failure case; `:398` — **AC-40.30** (`_3` collision, non-`EEXIST` not
  swallowed, watcher suppression, register-failure keeps the file); `:399` — **AC-40.31**
  (`capture.py` `source` repair).
- `task.md:49-50` — new rows `6a` (RED Python, requires a nonzero exit) and `6b` (GREEN Python).
- The "Atomicity of staging→inbox publication" design row became a **Losslessness** row explaining
  the `rename` → `link`+`unlink` change.

### R11-4 — packaging cannot ship stale Chromium output

- `implementation-plan.md:317` — new **§Packaging and output cleanliness (normative)**: `dist:prep`
  = clean `DIST_CLEAN_DIRS` → `electron-vite build` → `dotnet publish -c Release -r win-x64
  --self-contained true -p:PublishSingleFile=false`; `dist` = `dist:prep && electron-builder --win
  nsis --x64`; the deletion gate scans `ui/src` **and** `ui/out`; `global.json` pins `8.0.4xx`
  with `rollForward: latestFeature`; path resolution proven from an **installed** app; the helper
  ships unsigned (follow-up `DIST-CODE-SIGNING`). Cites the reviewer's stale-output proof
  `C:/Temp/av-kit/r11-stale-out-proof.txt`.
- `implementation-plan.md:382-383` — **AC-40.9** (`OVERLAY_SCAN_ROOTS` + `OVERLAY_FORBIDDEN_NAME_PATTERN`,
  O1–O4) and **AC-40.10** (ordered `PICKER_PREP_REQUIRED_SEGMENTS` / `PICKER_PUBLISH_REQUIRED_SEGMENTS`,
  `global.json`, P1–P7); `:400` — **AC-40.32** (installed-app proof, follow-up `DIST-INSTALLER-SANDBOX`).
- `task.md:57` — new row `9a` (`npm --prefix ui run dist` then `assert-packaging-clean.ps1 -Installed`);
  `ui/package.json` gains `clean:out`.

### Sequencing correction (from the R11-4 discussion, not a separate finding)

`implementation-plan.md:564` — **§Sequencing**: §1, §1b and §3 must be green and the human smoke
recorded **before** the overlay deletion lands. `task.md:53-54` splits this into row `7b` (live
smoke, a human step) and row `7c` (delete the Chromium path *and* the stale `ui/out`). Because the
human chose no fallback, the rollback position is "the sidecar is proven working on this machine",
not "git still has the old files".

### Scaffolding retirement (non-blocking note, adopted)

`implementation-plan.md:114` records it: ~3,700 lines and four gates deleted —
`assert-picker-binding.ps1` (1,256 lines of Roslyn source-shape policing), `assert-smoke-disposition.ps1`,
`run-live-smoke.ps1`, `assert-reflection-quality.ps1`, and eight `census-round*` scripts;
`lib-disposition.ps1` 628 → 112 lines. The gate layer went ~8,300 → ~4,600 lines of PowerShell and
13 → 9 gates. ACs **AC-40.17**, **AC-40.20** (Roslyn), **AC-40.22** (prose validator) and
**AC-40.23** (run-nonce) were retired; `implementation-plan.md:415` records why —
*none of them asserted a fact about the shipped capture feature*. The AC roster is now 28 rows,
matching `named-sets.json` `AC_COUNT`.

Row `9`'s stale reference to the smoke step was repointed to row `7b` in the same pass
(`implementation-plan.md:555`).

### Verification of the corrections themselves

| Check | Command | Result |
|---|---|---|
| All gates non-vacuous | `pwsh -File …/assert-oracle-selftests.ps1` | `PASS: ORACLE_SELFTESTS 9 gates proven non-vacuous` (exit 0) |
| Task-row gate self-test | `pwsh -File …/assert-task-rows.ps1 -SelfTest` | exit 0 (T1–T12n) |
| Verification-plan self-test | `pwsh -File …/run-verification-plan.ps1 -SelfTest` | `PASS: VERIFICATION_PLAN self-test (18 sections, J1-J6 deferral oracles)` |
| Task-row gate live | `pwsh -File …/assert-task-rows.ps1 -Through 9a` | exit 1, `17 of 17 rows before "9a" still open` — correct pre-execution state; the producer-binding check (which runs independently of `-Through`) passed |
| AC roster ↔ named sets | `grep -cE '^\| AC-40\.[0-9]+ \|'` vs `AC_COUNT` | 28 = 28 |
| `named-sets.json` canonical | Python round-trip | byte-identical, 121 keys |

`TASK_ROW_REQUIRED_TOKENS` was repopulated after the trim emptied it (its only entry had bound row 9
to the deleted `run-live-smoke.ps1`, and the gate's fail-closed vacuity guard correctly refused the
empty set). It now binds row `4a` → `dotnet`, row `7a` → `arm-run.ps1` + `assert-e2e-wired.ps1`,
row `7c` → `assert-overlay-deleted.ps1`, row `9a` → `assert-packaging-clean.ps1` — the four rows
where losing the producer would let missing product work close the row.

No production code, no C# files, and no overlay deletion were touched. This log does not authorize execution.

---

## Round 12 - changes_required

### Per-finding disposition

- **R11-1 — closed.** The normative pipeline now determines the PNG bytes: process-wide PerMonitorV2 awareness precedes screen access, the selected display may have a negative physical origin, `CopyFromScreen` runs before the picker exists with `SourceCopy | CaptureBlt`, alpha is forced opaque, crop math is local and clamped, and output pixels map exactly back to desktop pixels; HDR/scRGB is honestly bounded as a known limitation rather than left ambiguous (`implementation-plan.md:193-234`). AC-40.25/26 cover hostile coordinates, ordering, alpha, dimensions, and pattern pixels, while AC-40.27 requires a real `ScreenCaptureSource` primary-display pixel comparison that cannot be marked `[B]` (`implementation-plan.md:393-395`). Executed as written, this is a real pixel contract rather than a `CopyFromScreen` formality.

- **R11-2 — closed.** The Electron-side machine now has terminal handling for absent readiness, interaction hang, spawn error, signal termination, off-contract exit, exit-0-without-file, explicit error/cancel, and app quit; cleanup releases the one-in-flight guard in `finally`, and AC-40.28/29 require exactly-one settlement plus timeout, kill, pipe, path, and cleanup cases (`implementation-plan.md:236-277`, `implementation-plan.md:396-397`). Node guarantees `close` follows `exit` or a spawn `error`, so a hypothetical `close`-before-`exit` sequence is not an uncovered platform state. A hung sidecar therefore cannot disable capture for the remainder of the Electron session.

- **R11-3 — partially closed.** The hard-link name claim closes overwrite loss, suffix collisions, and keep-on-register-failure recovery (`implementation-plan.md:279-315`). The publication/request race is not total, however. Exact-path watcher suppression only lasts "until registration settles" (`implementation-plan.md:296-300`), while Node documents that an `fs.watch` callback may provide `filename === null`; a null-name event cannot match the owned path, and AC-40.30 tests only an event delivered *before* registration returns, not a null or delayed event delivered after suppression is removed (`implementation-plan.md:398`; [Node `fs.watch` caveats](https://nodejs.org/api/fs.html#filename-argument)). More seriously, the retained interactive caller still catches a failed `completeCaptureRequest` after the PNG was published and calls `cancelCaptureRequest` (`ui/src/main/index.ts:543-560`); AC-40.8 tests blocked-before-publication only and the plan leaves this call-site shape unchanged (`implementation-plan.md:381`, `implementation-plan.md:455`). A user can therefore confirm and keep valid pixels while the request visible to the requester becomes `Canceled`, the exact product failure R11-3 required the plan to eliminate.

- **R11-4 — partially closed.** Cleaning `ui/out` and the picker publish directory before both builds closes the demonstrated stale-Chromium-input class (`implementation-plan.md:317-345`). The installed proof is disconnected from the artifact the production build actually creates: `electron-builder.yml` sets `directories.output: dist` (`ui/electron-builder.yml:3-4`), but `NSIS_OUTPUT_DIR` is `ui/release` (`named-sets.json:290`), and the gate selects the newest EXE from that unrelated directory without tying it to the just-finished `dist` run (`assert-packaging-clean.ps1:231-235`). On the current tree `ui/dist` contains the installer and `ui/release` is absent, so row 9a cannot pass as written; if a stale `ui/release` later exists, it can inspect the wrong installer. The gate then launches the helper directly (`assert-packaging-clean.ps1:240-251`) rather than invoking F2 through the installed Electron app, so `{process.resourcesPath}` resolution in the shipped call chain remains unproved despite AC-40.32's claim (`implementation-plan.md:400`). An installed user can still receive "helper missing" from F2 even while the helper binary itself is runnable.

### New findings

None beyond the unresolved product portions of R11-3 and R11-4 above.

### Non-blocking notes

- Clarify the lifecycle prose so `exit` is observed but result classification waits for `close`; the current sentence both routes `exit` through settlement and says only `close` is read (`implementation-plan.md:269-273`).
- Replace the surviving "rename publication" wording in AC-40.18/task row 7a with the normative hard-link claim; the direct publication tests already forbid `renameSync` (`implementation-plan.md:385`; `task.md:52`).
- The no-fallback sequencing is sound: row 7 rewires the live path while the old files still exist, row 7b proves native behavior on the machine, and only row 7c deletes Chromium; post-delete tests and installer proof follow (`task.md:51-57`).
- More scaffolding can still be cut: the hub prose validator and closeout/task-row aggregation do not prove capture behavior; retain the direct pixel/lifecycle/publication tests, overlay scan, and a corrected installed-app smoke.

### Verdict

**changes_required**

---

## Round 12 — corrections applied (implementor log)

R11-1 and R11-2 were accepted closed and are untouched. The two partial closures are addressed
below, together with the three non-blocking wording notes. Every change is in the plan, the task
table, `named-sets.json`, or `assert-packaging-clean.ps1` — no production code was written.

### R11-3 remainder → R12-1 (watcher totality) and R12-2 (cancel after publish)

**R12-1 — the notification no longer depends on watcher timing or event content.**
`implementation-plan.md:279` rule 2 now states the reason path suppression cannot be total: Node
permits `fs.watch` to deliver `filename === null`, and a delayed event for an owned path can
arrive after suppression is lifted; neither can be matched against a path. The handler therefore
compares the inbox's **PNG set** against the last emitted set and notifies only on a difference.
An Electron-owned path enters the known set at publication time — before the link — so its
arrival by any route at any time is never a difference. `filename === null` degrades to a rescan
that finds nothing new. This is idempotence rather than timing, which is the only shape that
survives an event source guaranteeing neither content nor delivery time.
- `implementation-plan.md:461` — **AC-40.30** grew from three cases to five: (d) a null-filename
  event delivered both before and after registration settles, (e) a delayed event naming the
  claimed path after suppression is lifted. Both drive the decision function directly with a
  synthetic listing, so neither depends on real `fs.watch` timing. The negative column names the
  failure: a path-matching-only suppression emits a spurious second refresh in both.
- `implementation-plan.md:521` — `capture-inbox-watch.ts` is re-specified as a pure function over
  **listings**, not over event names.

**R12-2 — a published capture can no longer cancel its own request.** This was the sharper of the
two, and the reviewer was right that the plan had frozen it in place: the Files Modified row for
`ui/src/main/index.ts` said "call sites unchanged in shape", so the defect at
`ui/src/main/index.ts:543-560` would have shipped. Confirmed by reading it — one `try` wraps the
whole body and its `catch` calls `cancelCaptureRequest(row.id)`, so a `completeCaptureRequest`
that fails *after* publication tells the waiting agent `Canceled` while the PNG sits in the inbox.
- `implementation-plan.md:279` rule 5 now carries the fix normatively: the `try` splits at the
  publication boundary. Pre-publication failures may cancel (nothing was produced). Once
  `dest !== null`, **no failure path may cancel** — a failing complete is logged with the inbox
  path and the request is left pending for the existing recovery path. Cancel stays reachable
  only for a genuine `PICKER_EXIT_CANCEL`.
- `implementation-plan.md:464` — **new AC-40.33**, three cases: (a) publish succeeds + complete
  rejects ⇒ `cancelCaptureRequest` never called; (b) a real cancel ⇒ called exactly once; (c) a
  throw before anything is produced ⇒ cancel still allowed. The negative column names both
  failure directions, so "stop cancelling entirely" fails (b) and (c).
- `implementation-plan.md:520` — the Files Modified row for `index.ts` now says the interactive
  call site **changes**, explicitly superseding the frozen-shape note.
- `task.md` row 7 carries the split as GREEN work; row 6 adds
  `ui/tests/unit/capture-interactive.test.ts` as RED.

### R11-4 remainder → R12-3 (the installed proof could not have run, and proved the wrong thing)

Both halves confirmed by reading the files. `ui/electron-builder.yml:3-4` sets
`directories.output: dist`; `named-sets.json` said `NSIS_OUTPUT_DIR: "ui/release"`. On this tree
`ui/dist` holds the installer and `ui/release` does not exist, so row 9a would have failed with
"missing NSIS_OUTPUT_DIR" on every run. And `assert-packaging-clean.ps1` launched the installed
*helper*, never the installed *Electron app*, so `{process.resourcesPath}` resolution was unproved.

Three corrections, each with its own oracle:

| # | Correction | Oracle |
|---|---|---|
| 1 | `NSIS_OUTPUT_DIR` → `ui/dist`, and the gate now derives the expected value from `directories.output` in `ui/electron-builder.yml` and fails on disagreement (`Test-NsisOutputDir`) | **P8** feeds the gate the exact pair that shipped (`ui/release` vs `output: dist`) and requires rejection; **P8b** an absent `directories.output`; **P8c** the agreeing pair accepted |
| 2 | The installer must postdate this run's arm stamp. Row 9a runs `arm-run.ps1 -Name packaging-installed` before `npm run dist`; the gate calls `Test-ArtifactFresh` on the chosen `.exe` | **P10** a stale installer rejected; **P10b** a freshly built one accepted |
| 3 | The installed `av-kit.exe` answers `PICKER_PATH_PROBE_FLAG` (`--avkit-picker-path`) by running its real `resolvePickerExePath()`, printing `PICKER_PATH=<resolved>` and quitting without a window. The gate requires that path to exist and to sit under the install prefix (`Test-ProbeOutput`) | **P9** a dev-tree answer rejected; **P9b** no probe line; **P9c** a resolved path that does not exist; **P9d** the correct answer accepted |

Anchors: `implementation-plan.md:317` (§Packaging, three new normative clauses),
`implementation-plan.md:446` (AC-40.10 gains the output-dir equality),
`implementation-plan.md:463` (AC-40.32 rewritten as three distinct proofs),
`implementation-plan.md:605` (verification §2b), `task.md` row 9a (arm step added to the command).

Scope kept honest: the probe proves the **shipped resolver under the shipped layout**, not a full
F2 GUI drive from inside the installed app. That remains follow-up `DIST-INSTALLER-SANDBOX`, and
the human live smoke (row 7b) covers the GUI end on the dev tree. AC-40.32 says exactly that
rather than claiming more.

### Non-blocking notes

- **`exit` vs `close`** — `implementation-plan.md:269` now says it precisely: `exit` is observed
  and its code/signal recorded, but classification waits for `close`; `close` is guaranteed to
  follow `exit` or a spawn `error`, and the interaction timeout still covers the impossible case.
- **Surviving "rename" wording** — replaced in AC-40.18 (`the linkSync name-claim publishes …`)
  and in `task.md` row 7a (`link-claim publication -> register -> filmstrip refresh`).
- **More scaffolding to cut** — noted and declined for now, deliberately. The hub check and the
  task-row/closeout aggregation are already written, green, and cost nothing at execution time;
  the expensive scaffolding (~3,700 lines, four gates) was already deleted in round 11. Cutting
  further would be churn against the plan rather than work on the product, which is the opposite
  of the human's direction. Recorded here as a decision, not an oversight.

### Verification

| Check | Result |
|---|---|
| `assert-oracle-selftests.ps1` | `PASS: ORACLE_SELFTESTS 9 gates proven non-vacuous` (exit 0) |
| `assert-packaging-clean.ps1 -SelfTest` | exit 0 — P1–P7 plus the new P8/P8b/P9/P9b/P9c/P10 rejections and P8c/P9d/P10b acceptances |
| `assert-task-rows.ps1 -Through 9a` (live) | exit 1, `17 of 17 rows before "9a" still open` — correct pre-execution state; producer binding passed |
| AC roster ↔ `AC_COUNT` | 29 = 29 |
| `named-sets.json` | byte-identical round-trip, 125 keys, `RUN_STAMPS` = `e2e-capture`, `packaging-installed` |

No production code, no C# files, and no overlay deletion were touched. This log does not authorize execution.

---

## Round 13 - changes_required

### Per-finding disposition

- **R12-1 — partially closed (Medium).** Comparing PNG sets closes the null-filename and delayed-event cases, but the state machine is still not total: the plan does not say how the first baseline is seeded, how a pre-link owned-path reservation is rolled back when `linkSync` fails or the file is deleted, or how overlapping rescans atomically compare-and-advance the last-emitted set. A non-Electron PNG arriving while registration is in flight can therefore cause a refresh that also exposes the owned PNG before settlement and is followed by the mandatory post-settlement refresh; a phantom reservation can instead delay a later real file with that name. Electron-originated captures are serialized by the single-picker guard, but “exactly one refresh” remains underdetermined for external/concurrent inbox changes (`implementation-plan.md:298-316`, `implementation-plan.md:461`).

- **R12-2 — partially closed (High).** Splitting the `try` correctly prevents a published PNG from being mislabeled `Canceled`, but “leave the request pending for the existing recovery path” is not a recovery path. The poll reads the same Pending row every 500 ms and invokes the picker again once `capturing` clears; `scan_inbox` can recover the PNG as a shot but cannot complete or associate the request, which merely becomes `Expired` after its 120-second TTL. A user can therefore confirm once, keep the pixels, then be prompted to capture repeatedly while the requesting agent never receives the completed shot. The plan must retain and retry completion for the same `{requestId, path}` without reopening the picker, or define another terminal, discoverable recovery outcome (`implementation-plan.md:338-345`, `implementation-plan.md:464`; `ui/src/main/capture-register.ts:123-130`; `packages/core/src/avkit_core/services/capture.py:271-292`).

- **R12-3 — closed.** The output directory is now bound to `directories.output`, row 9a arms before `dist`, the chosen root installer must postdate that stamp, and the installed app executes the shared production resolver and must return an existing helper path under the install prefix (`implementation-plan.md:383-409`, `assert-packaging-clean.ps1:355-392`, `task.md:57`). With `--win nsis --x64`, the non-recursive root `*.exe` selection excludes `win-unpacked` and the `.blockmap`; the current output shape has one root installer. The probe does not drive F2, but together with the real entrypoint/spawn tests it proves the fragile packaged-layout seam. Shipping this local diagnostic flag is acceptable.

### New findings

None beyond the unresolved product portions of R12-1 and R12-2 above.

### Non-blocking notes

- No other current caller has the publish-then-request-completion shape: GUI IPC and hotkey/tray call `captureRegionFromGui` directly; only the interactive poll calls `completeCaptureRequest`/`cancelCaptureRequest` (`ui/src/main/index.ts:389-400`, `ui/src/main/index.ts:463-481`, `ui/src/main/index.ts:532-568`).
- A full F2 drive from the silently installed app remains useful follow-up coverage, but the resolver probe plus entrypoint/spawn tests are sufficient for this plan's packaged-path claim.

### Verdict

**changes_required**

---

## Round 13 — corrections applied (implementor log)

R12-3 was accepted closed and is untouched. Both remaining partial closures were confirmed against
the real code before anything was written, and both reviewer descriptions were accurate. No
production code, no C# files, no overlay deletion.

### R12-2 (High) — "leave the request pending" replaced with an actual recovery path

The reviewer was right that the round-12 correction stopped one lie and started a stall. Reading the
code confirms the whole failure chain, and it is worse than the finding stated:

- `ui/src/main/capture-register.ts:119-133` — `startInteractivePoll` hands `rows[0]` to the same
  handler every `POLL_REQUEST_MS`, so a row that stays Pending **reopens the picker on the next
  tick**. The user who already confirmed a region is asked to select one again, twice a second.
- `packages/core/src/avkit_core/services/capture.py:271-292` — `expire_stale_requests()` flips the
  row to `Expired` after `REQUEST_TTL_S` = 120 s, and
  `packages/core/src/avkit_core/domain/capture.py:41-43` shows `Expired` is **terminal** (empty
  transition set), so completion after that point is impossible, not merely late.
- `capture.py:221-235` — `request_interactive` refuses a second request while one is Pending. The
  agent cannot even retry until the TTL burns down. That was not in the finding and makes it worse.

Correction at `implementation-plan.md:315-345` (rule 5), with `ui/src/main/capture-register.ts`
added to Files Modified as the owner:

| Element | Behavior |
|---|---|
| Completion journal | Session-scoped `Map<requestId, { path, attempts, nextAttemptAt }>`, written the moment publication succeeds, before the first `completeCaptureRequest` |
| Consulted **before** the picker | The poll handler checks the journal first; a journalled Pending row is **retried**, and the picker is not invoked. This is what ends the re-prompt loop |
| Idempotent by construction | `complete_request` resolves the shot by path via `_upsert_shot` (`capture.py:237-260`, `:410-430`), so replaying `{requestId, path}` cannot duplicate a shot, and a lost *response* just leaves the row non-Pending, which drops the entry |
| Bounded, then terminal and visible | Backoff 1/2/4/8 s capped at 15 s instead of every 500 ms; stops when the row leaves Pending; if it leaves Pending uncompleted the entry is dropped and the user is notified **once** with the inbox path |
| Honest bound, stated in the plan | The journal is in memory: a main-process restart inside the 120 s window loses the retry. The PNG still stands and still reaches the filmstrip via `scan_inbox`; only the request expires. Persisting it would need a schema change in a project whose one Python change is AC-40.31 |

`implementation-plan.md:464` — **AC-40.33** grew from three cases to five: (d) the same Pending row
handed back ⇒ the picker is **not** invoked, complete is retried with the same `{requestId, path}`,
and the journal entry is dropped on success; (e) the row leaves Pending without completing ⇒ no
further retries and exactly one user notification naming the path. The negative column names the two
failure directions: no journal fails (d) — the picker reopens every 500 ms for a capture already
taken; retrying forever with no terminal notification fails (e) — the pixels exist and nobody is
told. `task.md` row 7 carries the journal as GREEN work.

### R12-1 (Medium) — the three named holes, plus the bound that makes the rest proportionate

All three were real and are now specified at `implementation-plan.md:298-321` (rule 2):

- **Baseline seeding** — the watcher lists the inbox once at start and adopts that listing
  **without notifying**; an empty initial set would fire a refresh at every app start.
- **Reservation rollback** — the owned-path entry goes in immediately before *each* `linkSync`
  candidate and comes out the moment that candidate throws (`EEXIST` or otherwise), in the same
  `finally` that disposes of staging. Only the candidate the link actually created stays reserved,
  released at settlement. This is the phantom-reservation case the reviewer named: an abandoned
  `_2` would otherwise swallow a genuinely new file that later takes that name.
- **Serialized rescans** — an event arriving mid-rescan sets a run-once-more flag rather than
  starting a second pass, so listing, comparison and advance of the last-emitted set are atomic
  with respect to each other.

`implementation-plan.md:461` — **AC-40.30** grew from five cases to seven: (f) a first listing over a
non-empty inbox emits nothing; (g) a reservation released after a failed `linkSync` candidate means a
later listing containing that name **does** notify.

On the reviewer's open question — *does a refresh triggered by an external PNG mid-registration
expose the owned PNG before settlement?* — **yes**, and the answer reframes the finding's severity in
both directions. `GET /captures` runs `scan_inbox()` (`capture.py:178-182`), which upserts every
inbox PNG as `source = scan`, and the filmstrip re-queries it every 5 s — every 1 s while a request
is pending (`ui/src/renderer/src/features/capture/useCaptureCatalog.ts:46-48`, `:75`). So:

- The watcher is an **accelerator, not the only route**. A missed notification costs a few seconds
  of latency; a spurious one costs one extra GET. No correctness rides on it, which is why the three
  fixes above are the right size and nothing heavier is warranted.
- But the poll *can* beat registration, and `_upsert_shot` returns the existing row unchanged when
  the file size matches (`capture.py:418-421`) — so the capture keeps `source = scan` permanently.
  That is not a watcher problem and no amount of suppression fixes it; it is exactly what rule 4's
  `source` repair (AC-40.31) exists for. Rule 2 now says so, so the two are read together.

### Verification

| Check | Result |
|---|---|
| `assert-oracle-selftests.ps1` | `PASS: ORACLE_SELFTESTS 9 gates proven non-vacuous` (exit 0) |
| `assert-task-rows.ps1 -Through 9a` (live) | exit 1, `17 of 17 rows before "9a" still open` — correct pre-execution state; producer binding passed |
| AC roster ↔ `AC_COUNT` | 29 = 29 (both new cases extend existing ACs; no AC added) |
| `named-sets.json` | untouched this round |

This log does not authorize execution.

---

## Round 14 - changes_required

### Per-finding disposition

- **R12-1 — partially closed (Medium).** Baseline seeding, serialized rescans, and rollback of a reservation for a failed candidate close the three named holes, and the watcher is correctly framed as an accelerator because `GET /captures` runs `scan_inbox()` on the filmstrip poll. The remaining same-second collision is not total: the plan inserts each candidate before `linkSync` and removes it on `EEXIST`, but does not require the reservation state to be separate from the last-emitted set or restore prior membership (`implementation-plan.md:311-329`). For a second capture in the same second, reserving the already-known base name and then deleting it after `EEXIST` can make the next listing rediscover that first PNG, producing an extra `captures:inbox-changed`/GET after the `_2` capture's required refresh. AC-40.30(g) covers a genuinely new later file, not an `EEXIST` candidate that was already in the baseline (`implementation-plan.md:529`). The `source` repair itself is correctly on the path that matters: `register_shot` still calls `_upsert_shot`, and AC-40.31 explicitly replaces the equal-size early return with a persisted source update (`implementation-plan.md:349-353`, `implementation-plan.md:530`).

- **R12-2 — open (High).** The journal closes the repeated-picker loop when the same Pending row is returned, and the 1/2/4/8/15-second schedule gives a reasonable number of retries inside the existing 120-second request window. The live poll still cannot tell the states needed by the recovery, however: `listPendingRequests()` returns `[]` both for a successful response with no Pending row and for every non-OK or thrown backend request (`ui/src/main/capture-register.ts:83-97`), while rule 5 requires retries through a backend restart and a different terminal action when the row truly leaves Pending (`implementation-plan.md:389-405`). Treating `[]` as terminal drops the journal during the backend restart and the agent never receives the shot; ignoring `[]` preserves retries but makes expiry and its one-time notification unreachable. AC-40.33(e)'s mocked "row leaves Pending" does not prove that production call chain because the production endpoint returns only Pending rows (`implementation-plan.md:532`). The plan needs an explicit success/error/terminal-status distinction (for example, a status-preserving poll/query) and tests for transport failure versus successful Pending, Completed, and Expired observations. Its terminal user notice must also name an actual Windows-visible notification surface; a callback count or renderer-only invalidation is not discoverable when the user is not looking at the app.

### New findings

None beyond the unresolved product portions of R12-1 and R12-2 above.

### Non-blocking notes

- The one-Pending-request service invariant makes `rows[0]` adequate; a second legitimate Pending row cannot be created through `request_interactive` (`packages/core/src/avkit_core/services/capture.py:220-235`).
- Losing the in-memory journal on an Electron main-process restart is acceptable as an explicit shipping bound for this MEU, but register a durable-recovery follow-up so the limitation is not lost.

### Verdict

**changes_required**

---

## Round 14 — corrections applied (implementor log)

Both findings were verified against the code before anything was written, and both were right. The
R12-2 one in particular was a real hole in my design, not a wording gap: the recovery I specified
could not be implemented on top of the poll it was built on.

### R12-2 (High) — the poll could not tell "gone" from "unreachable", and "notified" meant nothing

Two distinct defects, both confirmed by reading:

**1. `[]` is ambiguous.** `ui/src/main/capture-register.ts:83-97` returns `[]` for a backend that is
not ready, a non-OK status, a thrown fetch, and a genuinely empty pending list — four different
facts, one value. My journal used "the row is no longer Pending" as its terminal signal, so a
backend restart (the exact failure the retry exists for) would have looked terminal and dropped the
entry. Treating `[]` as non-terminal instead would have made expiry unreachable. The reviewer's
framing is exact.

Fixed at `implementation-plan.md:395-410` — and it needs no backend change, because
`GET /captures/requests` already takes an **optional** status filter and returns every row with its
status (`packages/api/src/avkit_api/routes/captures.py:164-173`). The poll now queries it
**unfiltered** and returns `{ kind: 'ok', rows } | { kind: 'unavailable', reason }`:

| Observation | Journal action |
|---|---|
| `unavailable` (not ready / non-OK / thrown / unparseable) | **Never terminal** — entry stays, backoff continues. This is the backend restart |
| `ok`, id reads `Pending` | Retry when its backoff is due |
| `ok`, id reads `Completed` | Drop **silently** — an earlier call landed and only its response was lost |
| `ok`, id reads `Cancelled` / `Expired` | Terminal → drop + one OS notice |
| `ok`, id absent from the listing | Terminal → drop + one OS notice (a listing that succeeded and lacks the row means it is gone) |

The picker's trigger is derived by filtering `rows` to the first `Pending` one, so its behavior is
unchanged. AC-40.33 grew from five cases to eight (`implementation-plan.md:532`): (f) `unavailable`
across several ticks ⇒ the entry survives and the retry succeeds when the backend answers; (g) an
observed `Completed` ⇒ dropped silently, no notice, no second complete call; (h) `ok` without the
id ⇒ terminal. The negative column now names today's `listPendingRequests` explicitly as the
implementation that fails (f) and (g).

**2. "the user is notified" had nothing behind it.** The reviewer was right to push on this. The
phrase appears three times in §Result publication, and the only `notify` callback in the capture
path is `notifyInboxChanged(window)` (`capture-register.ts:100-114`, `capture-overlay.ts:180-182`)
— a renderer IPC refresh. There is no `Notification` anywhere in `ui/src/main`. A user whose window
is closed to tray, which is the state a hotkey capture is taken from, sees nothing at all.

New **§User-visible notification (normative)** at `implementation-plan.md:346-364`, with
`ui/src/main/notify-user.ts` added to Files Modified. Every "the user is notified" in the plan now
resolves to one `notifyUser({ title, body, path })` helper: `app.setAppUserModelId('com.avkit.app')`
at startup matching `ui/electron-builder.yml:1` (Windows silently drops toasts from a process with
no AUMID, so omitting it is the failure that looks like working code); `Notification.isSupported()`
⇒ a toast whose `click` runs `shell.showItemInFolder(path)`, so the notice is actionable and not
merely informative; tray-balloon fallback through the `Tray` that already exists
(`capture-tray.ts:10`); `appendStdoutLog` on both branches; injectable for vitest and suppressed
under `AVKIT_E2E`. AC-40.30(c) and AC-40.33(e) now assert the **OS** surface by name, so routing a
terminal notice through `notifyInboxChanged` fails.

### R12-1 (Medium) — one set was doing two jobs

Confirmed and fixed at `implementation-plan.md:311-329`. Reservations now live in a **separate**
set from the last-emitted set; the decision is `current \ (lastEmitted ∪ reserved)`; releasing a
reservation removes only from the reservation set and **never** removes a name from history; a
completed pass advances the last-emitted set to the full current listing. The reviewer's same-second
case is the proof it matters: B reserving `{base}.png`, taking `EEXIST` and releasing would, under
one shared set, delete A's already-announced name and make A look new on the next listing.

AC-40.30 gained case (h): A settles at `{base}.png` and is announced; B reserves it, takes `EEXIST`,
releases, settles at `{base}_2.png` ⇒ exactly one further `captures:inbox-changed`, and
`{base}.png` is never re-announced. The negative names the single-set implementation.

### Non-blocking notes accepted

- **`rows[0]` is adequate** — agreed, and the invariant is `request_interactive`'s conflict guard
  (`capture.py:220-235`). No change; the round-14 poll change preserves the same first-Pending
  derivation.
- **Register the restart bound as a follow-up** — done. New Out of Scope row at
  `implementation-plan.md:673` states the bound and its reason (associating a shot with an already
  `Expired` request needs a schema change in a project whose one Python change is AC-40.31), and
  registers `CAPTURE-JOURNAL-VOLATILE` in `.agent/context/known-issues.md`; the Files Modified row
  for that file is now unconditional and `task.md` row 7 carries the registration.

### One thing the reviewer did not raise, corrected anyway

The Out of Scope row on picker latency still promised that "Row 9 records the measured `LATENCY_MS`
in the smoke disposition" — but `LATENCY_MS` and the smoke disposition died with the four gates
deleted in round 11, so an executor would have been chasing a field that does not exist. Corrected
at `implementation-plan.md:672` to point at the human live smoke (row 7b) and the handoff, rather
than resurrecting the deleted gates.

### Verification

| Check | Result |
|---|---|
| `assert-oracle-selftests.ps1` | `PASS: ORACLE_SELFTESTS 9 gates proven non-vacuous` (exit 0) |
| `assert-task-rows.ps1 -Through 9a` (live) | exit 1, `17 of 17 rows before "9a" still open` — correct pre-execution state; producer binding passed |
| AC roster ↔ `AC_COUNT` | 29 = 29 (all new cases extend existing ACs) |
| `named-sets.json` | untouched |

This log does not authorize execution.

---
 
## Round 15 - changes_required
 
Intent anchor: executing this plan must leave a Windows user with a native region capture that
publishes exactly once, and leave an interactive caller with an honest terminal request result
without asking the user to capture the same pixels again.
 
### Per-finding disposition
 
- **R12-1 — closed.** Reservations and emitted history are now separate sets; the decision is
  `current \ (lastEmitted ∪ reserved)`, a failed candidate releases only its reservation, and a
  completed rescan advances history to the full current listing
  (`docs/execution/plans/2026-08-27-p9-capture-native-picker/implementation-plan.md:325-343`).
  AC-40.30(h) exercises the exact same-second sequence and requires only B's one new refresh while
  A's settled name remains historical (`implementation-plan.md:581`). Under the plan's
  single-publisher flow, the algebra is total and preserves exactly one refresh per owned capture.
 
- **R12-2 — partially closed (High).** The calling-agent state machine is now complete: an
  unfiltered successful listing preserves the real `Pending`/`Completed`/`Cancelled`/`Expired`
  state, `unavailable` never terminates the journal, `Completed` drops silently, and the other
  terminal outcomes notify once without reopening the picker
  (`docs/execution/plans/2026-08-27-p9-capture-native-picker/implementation-plan.md:432-458`,
  `implementation-plan.md:584`). The remaining user-visible branch is not reachable as promised
  in an unpackaged Windows dev run. The plan unconditionally sets `com.avkit.app`, then chooses a
  toast whenever `Notification.isSupported()` is true and uses the tray balloon only when it is
  false (`implementation-plan.md:360-380`). Electron's Windows notification contract requires a
  matching Start Menu shortcut with an AppUserModelID and ToastActivatorCLSID; its documented dev
  bootstrap instead pins `electron.exe` and uses `app.setAppUserModelId(process.execPath)`
  (https://www.electronjs.org/docs/latest/tutorial/notifications). `isSupported()` reports OS
  capability, not whether that shortcut identity exists. Consequently, a register failure or
  terminal journal outcome in the dev app can take the toast branch, have Windows silently discard
  it, and never reach the tray fallback: the PNG survives, but the user sees none of the promised
  notice. The NSIS-installed path has the matching `appId` AUMID
  (`ui/electron-builder.yml:1`; https://www.electron.build/nsis/); the plan still needs a dev-safe
  branch (for example, use the retained tray balloon there) and an assertion that exercises that
  branch.
 
### New findings
 
None beyond the remaining R12-2 product behavior above.
 
### Non-blocking notes
 
- The unfiltered poll does not widen trust—it stays on the authenticated local API—but it reads an
  unbounded historical table every 500 ms (`implementation-plan.md:441-444`;
  `packages/infrastructure/src/avkit_infra/database/repositories.py:474-478`); track a bounded
  status/id lookup if interactive-request volume becomes material.
- The prose calling completion replay "idempotent" is imprecise: the backend rejects a transition
  from an already-Completed row (`implementation-plan.md:428-431`;
  `packages/core/src/avkit_core/services/capture.py:245-252`), but the new Completed observation
  prevents that replay, so the shipped state machine is not broken by the wording.
 
### Verdict
 
**changes_required**

---

## Round 15 — corrections applied (implementor log)

R12-1 accepted closed, untouched. One remaining branch on R12-2, plus both non-blocking notes.

### R12-2 remainder — the toast branch was unreachable in a dev run

The finding is right and the distinction is the whole point: a Windows toast is delivered against a
**shortcut identity** — a Start Menu shortcut carrying an AppUserModelID and a ToastActivatorCLSID —
and `Notification.isSupported()` reports OS capability, not whether that identity exists. An
unpackaged run has no such shortcut, so setting `com.avkit.app` and taking the toast branch yields a
call that succeeds and a notification Windows discards, with the tray fallback never reached. I had
written the AUMID line believing it was sufficient; it is necessary and not sufficient.

Corrected at `implementation-plan.md:368-393` — the surface is now chosen by **`app.isPackaged`**,
not by `isSupported()`:

| Configuration | Behavior |
|---|---|
| Packaged (`app.isPackaged === true`) — what a user has | `setAppUserModelId()` with `appId` from `ui/electron-builder.yml:1`, which is the AUMID electron-builder writes into the NSIS Start Menu shortcut, so the identity matches. `Notification` with a `click` running `shell.showItemInFolder(path)`; tray balloon if `isSupported()` is false |
| Unpackaged (dev, Playwright) | **No AUMID is claimed** — an identity no shortcut backs is what makes the toast vanish — and the toast branch is not taken at all. Tray balloon, which needs no shortcut identity; parentless `dialog.showMessageBox` if the tray does not exist yet |
| Both | `appendStdoutLog` always |

The plan also now states the honest limit rather than over-promising: Windows can drop a
notification for reasons no API reports (Focus Assist, notification-centre policy, and on Win10+ a
tray balloon may itself be routed through the notification centre), so the log line is the one
receipt the plan can promise, and a *visible* notice is claimed only for the packaged app.

AC-40.30(c) now asserts the branch in both directions (`implementation-plan.md:527`): with
`app.isPackaged === false` a register failure must take the tray-balloon branch and never construct
a `Notification`; with it true, the toast branch. The negative names the shipped-in-round-14 shape —
branching on `isSupported()` shows a dev user nothing.

### Non-blocking notes — both taken

**1. Don't read the whole request history twice a second.** Correct, and easy to make strictly
better: the poll keeps the existing `?status=pending` filter for the **ordinary** tick and drops the
filter **only while the journal is non-empty**, a state measured in seconds
(`implementation-plan.md:447-453`). The discriminated `{ kind }` result applies to both shapes; only
the filter changes. The unfiltered walk over
`packages/infrastructure/src/avkit_infra/database/repositories.py:474-478` is now confined to the
rare recovery case it exists for.

**2. "Idempotent" was too loose.** Also correct. Replaying `{requestId, path}` cannot create a
second *shot* (`_upsert_shot` resolves by path), but the *request* transition is not idempotent —
completing an already-`Completed` row raises `ConflictError` (`capture.py:245-252`;
`CAPTURE_REQUEST_TRANSITIONS[Completed]` is empty). Reworded at `implementation-plan.md:428-437`,
and turned into a robustness rule rather than only a correction: a **409 from `complete` is treated
as terminal-success**, since it proves the row already left Pending, so the entry is dropped
silently instead of retrying into a loop. New AC-40.33(i) with the negative — treating a 409 as
retryable burns the backoff and then notifies the user about a capture that in fact succeeded.

### Verification

| Check | Result |
|---|---|
| `assert-oracle-selftests.ps1` | `PASS: ORACLE_SELFTESTS 9 gates proven non-vacuous` (exit 0) |
| `assert-task-rows.ps1 -Through 9a` (live) | exit 1, `17 of 17 rows before "9a" still open` — correct pre-execution state; producer binding passed |
| AC roster ↔ `AC_COUNT` | 29 = 29 |
| `named-sets.json` | untouched |

This log does not authorize execution.

---

## Round 16 - changes_required

Intent anchor: executing this plan must leave a Windows user with a native region capture that
publishes exactly once, and leave an interactive caller with an honest terminal request result
without asking the user to capture the same pixels again.

### Per-finding disposition

- **R12-2 — partially closed.** The previously open notification branch is closed: the packaged
  path uses `ui/electron-builder.yml:1`'s `appId`, which electron-builder defines as the Windows
  NSIS AUMID and writes to its Start Menu shortcut, while the unpackaged path avoids the unsupported
  toast identity and the plan honestly makes the log—not a tray balloon—a delivery guarantee
  (`docs/execution/plans/2026-08-27-p9-capture-native-picker/implementation-plan.md:368-395`).
  R12-2 is not fully closed because the new blanket 409 rule can silently discard a journal entry
  whose request actually became `Cancelled` or `Expired`, leaving the calling agent without the
  capture and the user without the terminal-failure notice (`implementation-plan.md:443-452`).

### New findings

- **R16-1 — High — a 409 is not evidence that completion succeeded.** The plan treats every 409
  from `complete` as terminal-success and AC-40.33(i) requires a silent drop
  (`implementation-plan.md:443-452`, `implementation-plan.md:610`), but the backend emits the same
  409 for every non-Pending state. It calls `expire_stale_requests()` before reading and validating
  the request transition, so a user who confirms near or after the 120-second TTL can save the PNG,
  have that very completion call flip the row to `Expired`, receive 409, and then have Electron
  silently discard the journal while the calling agent observes `Expired`
  (`packages/core/src/avkit_core/services/capture.py:237-252`). A concurrent cancellation has the
  same false-success result. Treat 409 as a trigger to reconcile the actual row status through the
  existing discriminated listing: `Completed` drops silently; `Cancelled`, `Expired`, or absent
  drops with the existing notice; `unavailable` retains the journal until the status is knowable.

### Non-blocking notes

- The filtered/unfiltered switch does not reintroduce `{ kind }` ambiguity: both query shapes use
  the same `ok`/`unavailable` result and only the journal-present query drops the status filter
  (`implementation-plan.md:453-477`).
- `implementation-plan.md:666` still summarizes the request GET as always unfiltered; that stale
  inventory wording is non-blocking because the normative algorithm at lines 465-470 is explicit.
- A Win10+ tray balloon is not guaranteed visible, but the plan now says exactly that and promises
  only the log for an unpackaged run (`implementation-plan.md:382-392`).

### Verdict

**changes_required**

---

## Round 16 — corrections applied (implementor log)

One finding, and it was mine: the blanket 409 rule I added in round 15 as "belt and braces" was the
only thing that got worse between rounds. The reviewer caught it in the round that introduced it.

### R16-1 (High) — a 409 is a trigger to reconcile, not a verdict

Confirmed exactly as described. `complete_request` calls `expire_stale_requests()` **before** it
validates the transition (`packages/core/src/avkit_core/services/capture.py:237-252`), and the
backend raises the same `ConflictError` for every non-Pending state. So a user who confirms near the
120 s TTL can have that very completion call expire the row and answer 409 — and under the round-15
rule Electron would have read that as success, discarded the journal silently, and left the calling
agent seeing `Expired` with the PNG sitting unclaimed in the inbox and the user told nothing. A
concurrent cancel produces the same false success. That is the precise failure this whole section
exists to prevent, reintroduced by the shortcut I took to avoid a retry loop.

Corrected at `implementation-plan.md:443-458`. A 409 now **triggers a reconciling read** of the
row's actual status through the discriminated listing, and that status decides:

| Reconciled status | Journal action |
|---|---|
| `Completed` | Drop silently — the earlier call did land |
| `Cancelled` / `Expired` / absent | Drop **with** the terminal notice naming the inbox path |
| `unavailable` | Keep the entry until the status is knowable |

What the 409 still buys — the thing I wanted from it — is that the entry is never retried into a
loop against a row that has already left Pending. It just no longer decides *which* terminal
outcome occurred, which it never had the information to do.

AC-40.33(i) is rewritten to the reconciling shape (`implementation-plan.md:610`), and its negative
now names both failure directions: retrying a 409 loops against a non-Pending row; treating it as
terminal-**success** is the round-16 bug, where a near-TTL confirm is expired by its own completion
call and nobody is told.

### Non-blocking notes

- **Stale inventory wording** — fixed. The Files Modified row for `capture-register.ts` said the
  request GET is always unfiltered; it now states the actual algorithm (filtered ordinarily,
  unfiltered only while the journal is non-empty, 409 reconciled against that listing), matching the
  normative text.
- **`{ kind }` ambiguity** — agreed, none introduced; both query shapes share the same result type.
- **Win10+ tray balloon visibility** — agreed, and the plan already promises only the log for an
  unpackaged run.

### Verification

| Check | Result |
|---|---|
| `assert-oracle-selftests.ps1` | `PASS: ORACLE_SELFTESTS 9 gates proven non-vacuous` (exit 0) |
| `assert-task-rows.ps1 -Through 9a` (live) | exit 1, `17 of 17 rows before "9a" still open` — correct pre-execution state; producer binding passed |
| AC roster ↔ `AC_COUNT` | 29 = 29 |
| `named-sets.json` | untouched |

This log does not authorize execution.

---

## Round 17 - approved

### Per-finding disposition

- **R16-1 — closed.** A 409 now triggers a fresh discriminated listing instead of deciding the outcome: `Completed` drops silently; `Cancelled`, `Expired`, or absent drops with the terminal notice naming the inbox path; and `unavailable` preserves the journal until status is knowable (`implementation-plan.md:443-462`). AC-40.33(i) requires both false directions to fail, so neither a retry loop nor a silent false-success can ship (`implementation-plan.md:620`).

### New findings

None.

### Non-blocking notes

- The same listing also reconciles a lost success response as `Completed`, while other completion failures keep the journal until a successful read proves a terminal state.
- The accepted in-memory restart bound remains unchanged; it is already explicit and tracked, not a regression from the round-16 correction.

### Verdict

**approved**
