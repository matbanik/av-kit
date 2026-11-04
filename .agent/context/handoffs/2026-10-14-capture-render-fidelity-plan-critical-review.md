---
date: "2026-10-14"
review_mode: "plan"
target_plan: "docs/execution/plans/2026-10-14-capture-render-fidelity/implementation-plan.md"
loop_id: "s36-plan-2026-10-14-capture-render-fidelity"
round: 3
verdict: "approved"
findings_count: 0
blocking_findings_count: 0
procedural_gate_count: 0
prior_findings_pending_recheck: 0
resolved_findings_count: 6
template_version: "2.2"
requested_verbosity: "standard"
agent: "codex-gpt-6.1-sol"
intent_anchor: "Session 36 makes capture rendering faithful: MEU-82 aligns the text preview baseline with the baked PNG, MEU-83 fixes arrow shaft/head geometry and anti-aliases the baked head, MEU-84 reconciles the annotated path and makes Open file/folder target the viewed file, all within PRODUCT_SCOPE."
intent_achieved: "yes"
---

# Critical Review: 2026-10-14-capture-render-fidelity

> **Review Mode**: `plan`
> **Verdict**: `changes_required` — two High blocking findings; two Medium and two Low non-blocking findings. No Critical findings.

## Intent Anchor

Session 36 makes capture rendering faithful: MEU-82 aligns the text preview baseline with the baked PNG, MEU-83 fixes arrow shaft/head geometry and anti-aliases the baked head, MEU-84 reconciles the annotated path and makes Open file/folder target the viewed file, all within PRODUCT_SCOPE.

**Would executing this plan deliver that objective? Partially.** The MEU mapping, text-baseline calculation, per-field reconciliation and viewed-path plumbing address the stated defects. As written, however, MEU-83 prescribes a raster algorithm that fails its own immutable acceptance rules (F1), and the final freshness check can accept a full-gate record after relevant config inputs change (F2).

## Scope

**Target**: `docs/execution/plans/2026-10-14-capture-render-fidelity/{implementation-plan.md,task.md,session-gate.ps1,identity.py,red-check.py}`.

**Review Type**: independent, directly invoked plan review; author `claude-code-local`, reviewer `codex-gpt-6.1-sol`. The existing ledger has no recorded rounds, a three-round budget, the supplied goal, and AC families `AC-35/39/59/66/67/82/83/84`. This report does not record its own approval or mutate the ledger.

**Checklist Applied**: PR-1 through PR-9, DR-1 through DR-8 where applicable, and AV-1 through AV-6 adapted to an unstarted plan. The round-2 corrections-census precondition is not applicable.

**State**: HEAD `78610200ea2e7efd52318ea95c3e48b6df4993ba`; no tracked diff before review. All 26 task rows are unchecked; no baseline, walkthrough or MEU-82/83/84 implementation handoff exists. `task.md` frontmatter `in_progress` therefore describes planning, not evidence of implementation.

Read and cross-checked the current build-plan sections (09:356–373, 706–738, 825–863), Session 36 grouping and carry-forward decisions, SSOT prerequisite/deferral rows, four known-issue records, capture renderer/commands/image-loading sources, bake adapter, `scan_inbox`, relevant existing test expectations, D6 registration, review protocol/template and latest peer review. PROFILE, GUARDRAILS, focus, known issues, harness overrides, architecture and testing strategy were consulted. Actual reviewer shell is PowerShell on Windows; the Cursor overrides do not replace the independent Codex reviewer role.

Only the canonical report was added to the repository. Scratch probes wrote beneath the receipts root; product code, tests and plan-local tooling were unchanged. No product suite, installation, build or Electron application was run during planning review.

## Findings

| # | Severity | Blocking | Kind | Finding | File:Line | Recommendation | Status |
|---|----------|----------|------|---------|-----------|----------------|--------|
| F1 | High | yes | behavior | **The mandated arrow raster and its acceptance oracles disagree.** Confidence: High; subject: deliverable; violates **AC-83** (AC-83.5–83.7), PR-4. A literal scratch transcription of `BAKE_AA` on Pillow 12.3.0 produced 117 nonwhite pixels outside the horizontal head grown by 1 px; the diagonal shaft had 34 pixels at least 1 px inside its edge whose channels differed from the mark by more than 8; a clipped horizontal tip at `(119,60)` had maximum column coverage 41/255, so no pixel in that tip column equalled the mark colour. These are consequences of the specified sampling/coordinate convention and LANCZOS coverage, even with the shaft correctly shortened. Row 5 cannot satisfy both the algorithm and these frozen assertions. | `implementation-plan.md:123`, `:124`, `:125`, `:201`, `:202`, `:203`; `task.md:44`, `:45` | Resolve the raster-coordinate convention and AA-aware oracles in planning. Distinguish actual shaft leakage from small filter halos; define a justified interior tolerance and clipped-tip coverage requirement. Re-prove the chosen rules with a positive literal-algorithm fixture and a negative full-length-shaft fixture before freezing tests. | fixed (corrections round 1) |
| F2 | High | yes | control-defeat | **Final evidence can remain green after an untested build/config change.** Confidence: High; subject: committable-tooling; `mechanism: task-row-completion-predicate`; violates **AC-82** (fresh bake/fixture proof), PR-8 and the plan's validation-stage contract. `tested_state()` excludes both lockfiles, `ui/tsconfig.json`, and `ui/electron.vite.config.ts`; its `--state-only` branch also skips the separate font/lock hashes. In a scratch work tree using the real HEAD/index, changing each of those four files left the state unchanged; the actual durable-evidence predicate then accepted a synthetic historical full record against that unchanged expected state. A positive control adding a selected source file changed the state. H1-6b checks only the state string, so it cannot detect those mutations or trigger H1-2 again. | `identity.py:17`, `:28`, `:40`, `:43`; `implementation-plan.md:562`, `:564`; `task.md:60`; `session-gate.ps1:96` | Bind the state used by H1-6b to the selected code/tests, shared configs, command manifest, lockfiles, actual font and live runtime/dependency/environment identity required by D6. Recompute the same complete identity at gate boundaries and reuse checks; prove a config mutation refuses historical evidence. | fixed (corrections round 1) |
| F3 | Medium | no | control-defeat | **`red-check.py` accepts setup failures without a defect assertion.** Confidence: High; subject: committable-tooling; `mechanism: task-row-completion-predicate`. A receipt containing only `1 failed`, `Error: electron.launch: Process failed to launch!` and a test-title occurrence of `viewedFilePath` exits 0. A click timeout with `assert ` in source context also exits 0. The checker searches the whole receipt for a token, rather than attributing the actual failure to an assertion or missing declared export. An unrelated ImportError control is correctly refused. This defeats the promised S3 Red classification, although the separate Green/full runs still prevent these launch failures from certifying the finished product. | `red-check.py:32`, `:33`, `:45`, `:48`; `task.md:32`; `implementation-plan.md:333`, `:392` | Classify the actual failed-test diagnostics and retain each child exit; reject launch/timeouts and unrelated setup errors even when source text names a new helper or assertion. Add positive assertion/new-export and negative launch/timeout receipts to the plan-local verifier's probes. | fixed (corrections round 1) |
| F4 | Medium | no | behavior | **The full runner executes a behavioral suite before all static checks have passed.** Confidence: High; subject: committable-tooling. `py-tests` runs before `ui-types`, `ui-lint`, and `task-contract`. Thus a UI static failure occurs after a full behavioral stage has already run, contrary to the staged contract and the required `not_run` treatment of later stages. This is a sequencing defect, not a demonstrated false-pass. | `session-gate.ps1:21`, `:23`, `:24`, `:25`, `:31`; `implementation-plan.md:560`; `.agent/docs/commands.md:220` | Run the complete selected static set first, then affected checks, then the fresh full/runtime stages. Preserve fail-fast behavior and explicitly report later stages as not run. | fixed (corrections round 1) |
| F5 | Low | no | clerical | **The administrative output inventory omits required files.** Confidence: High; subject: deliverable. H1-3 updates current focus and renders MEU state; the renderer writes `.agent/context/meu-registry.md`. H2 changes known-issues YAML, whose canonical procedure regenerates `.agent/context/known-issues.md`. None of those three paths is in the Files Modified inventory or `scope-paths` allow-list. The required files are plainly inferable, so this is clerical; a later gate rerun would otherwise report them outside scope. | `implementation-plan.md:282`, `:363`; `session-gate.ps1:51`, `:84`; `task.md:55`, `:67`; `tools/meu_status/render.py:30` | Add the three administrative paths to both inventories and explicitly regenerate the known-issues Markdown after issue updates. Keep the product scope unchanged. | fixed (corrections round 1) |
| F6 | Low | no | clerical | **`ARROW_HEAD` values are restated outside their named definition.** Confidence: High; subject: deliverable; PR-9. Factor/angle values are repeated in User Review, D-12 chosen, the brief and option table, despite the single-statement rule. No current disagreement exists. | `implementation-plan.md:95`, `:118`, `:450`, `:530`, `:535` | Keep `ARROW_HEAD` at line 118 canonical; reference that name for the chosen values elsewhere, retaining distinct alternative values only where needed for the decision comparison. | fixed (corrections round 1) |

F2 and F3 use the registered mechanism for a task row's completion predicate; they are different manoeuvres against that control. Only F2 is blocking. F1 concerns the deliverable contract itself, not review scaffolding. F3–F6 do not gate approval under the Materiality Gate.

## Checklist Results

### Plan Review (PR)

| Check | Result | Command / procedure | Exit | Evidence |
|---|---|---|---|---|
| PR-1 Plan/task alignment | pass | Manually compare three MEU AC tables, Files Modified tables, WP order and task rows 0–H2-5; observer `codex-gpt-6.1-sol` | null | MEU-82 → MEU-83 → MEU-84; handoffs before review, reflection/metrics after approval. |
| PR-2 Not-started confirmation | pass | `rtk proxy P:/av-kit/.venv/Scripts/python.exe -B -X utf8 C:/Temp/av-kit/s36-review-inventory.py` | 0 | 26/26 unchecked; zero completed; no baseline, walkthrough or implementation handoff. |
| PR-3 Task contract completeness | pass | `rtk proxy P:/av-kit/.venv/Scripts/python.exe -B tools/lint_task_contract.py --allowed-builder-classes avkit_builder,avkit_coordinator,avkit_verifier --task docs/execution/plans/2026-10-14-capture-render-fidelity/task.md` | 0 | 26 rows; 10 columns; 24 shell rows checked; 2 view-file exemptions; dependencies acyclic. |
| PR-4 Validation realism | fail | Literal raster and receipt probes in `s36-review-probes.py`, plus manual task/command inspection; observer `codex-gpt-6.1-sol` | null | F1: three prescribed arrow oracles fail the prescribed algorithm. F3/F4 are additional non-blocking quality issues. |
| PR-5 Source-backed planning | pass | Manually cross-check 09 specification, grouping, issue decision logs and plan AC source columns; observer `codex-gpt-6.1-sol` | null | Baseline, AA, per-field reconcile, viewed targets and planned test amendments have source backing. D-12 is explicitly left for the execution message/default, not represented as a received approval. |
| PR-6 Handoff/corrections readiness | pass | Inspect Handoff Set, H1/H2 dependencies and existing loop; observer `codex-gpt-6.1-sol` | null | Three explicit MEU handoffs; independent vendor route; rolling review; corrections available. Round-2 census precondition n/a. |
| PR-7 Scope discipline | pass | Inventory probe plus manual comparison of each Out of Scope Basis with 09 and grouping; observer `codex-gpt-6.1-sol` | null | MEU-81/85/86 are registered pending deferral targets; all five exclusions have substantive source backing. Administrative inventory note F5 does not hide product work. |
| PR-8 Control reachability/totality | fail | `rtk proxy P:/av-kit/.venv/Scripts/python.exe -B -X utf8 C:/Temp/av-kit/s36-review-probes.py` | 0 | Probe completion succeeded; observations show a false-passing freshness control (F2) and permissive Red classification (F3). Exit 0 is not a product gate pass. |
| PR-9 Single-statement discipline | partial | Inventory literal/name census and manual comparison; observer `codex-gpt-6.1-sol` | null | Named contracts mostly centralize the rules; F6 records the repeated head-value cluster once. |
| Referenced-artifact existence | pass | Inventory probe, resolving npm paths relative to `ui` and comparing absent files with Files Modified | 0 | 37 normalized code/test/tool/config/fixture references: 28 exist, 9 scheduled creations, no unexplained missing executable. |

### Information Retrieval (IR)

| Check | Result | Procedure | Exit | Evidence |
|---|---|---|---|---|
| All AC have source labels | pass | Inspect every AC source cell and corresponding named contract; observer `codex-gpt-6.1-sol` | null | AC-82.1–6, AC-83.1–8, AC-84.1–6 all identify a spec, canon or recorded decision. |
| Validation cells are exact commands | pass | Task linter above plus manual argv/cwd inspection | 0 | Exact executable cells and two explicit source-read cells; semantic defects recorded separately. |
| BUILD_PLAN audit row present | pass | Inspect task row 9 and plan audit; observer `codex-gpt-6.1-sol` | null | Phase 9, matrix 9.15–9.17 and Arrow/Text/Head documentation edits are assigned. Some numeric source line refs have drifted; section/row names make the targets clear. |
| Post-MEU rows present | pass | Inspect H1-3 through H2-5; observer `codex-gpt-6.1-sol` | null | Registry, issue status, handoffs, review, reflection, metrics and commit draft are explicit. |

### Design / Docs Review (DR)

| Check | Result | Procedure | Exit | Evidence |
|---|---|---|---|---|
| Template naming / version / frontmatter | pass | Inspect target frontmatter, paths and v2.2 review template; observer `codex-gpt-6.1-sol` | null | Canonical date/slug, per-MEU handoffs, rolling review; template versions present; no YAML syntax ambiguity. |
| DR-1 Claim-to-state match | pass | Compare draft planning claims with unchecked rows and absent implementation artifacts; observer `codex-gpt-6.1-sol` | null | Plan does not claim implemented product behavior. |
| DR-2 Residual old terms / DR-3 rename references | n/a | No completed rename or migration is under review | null | Intentional legacy constants and proposed amendments are distinguished in the plan. |
| DR-4 Verification robustness | fail | Raster, identity and Red probes | 0 | Probe process succeeds while demonstrating F1–F3; does not certify their predicates. |
| DR-5 Evidence auditability | pass | Compare command receipts and exact probe results pasted below; observer `codex-gpt-6.1-sol` | null | Decisive values and failure/control distinctions are preserved here. |
| DR-6 Cross-reference integrity | partial | Compare scope tables with renderer output targets and script allow-list; observer `codex-gpt-6.1-sol` | null | F5: three administrative paths omitted; product/spec mapping is otherwise coherent. |
| DR-7 Evidence freshness | fail | Input-mutation probe and manual H1-6b call-chain trace | 0 | F2: changed inputs retain expected state and historical evidence is accepted. |
| DR-8 Completion vs residual risk | pass | Inspect this review's outcome and limitations; observer `codex-gpt-6.1-sol` | null | Plan remains unstarted; no implementation-complete or runtime-pass claim. |

### Post-Implementation / Adversarial Checks

Implementation evidence-bundle and FAIL_TO_PASS-table completion are **n/a** for an unstarted plan. AV-1 is a planned Red/Green contract, with F3 on its checker; AV-2/3/4 are planned assertion/no-skip requirements, with F1 preventing meaningful Green as presently specified. AV-5 has no completed implementation to scan. AV-6 source tracing passes. Runtime text pixel equivalence, real Electron shell logging, reconciliation and full-suite regression outcomes remain **not run**, not inferred from this review.

### Durable Observations

All records refer to review inputs at HEAD plus SHA-256 of the five target-file hashes, excluding this newly written report. Commands used all-stream receipts and preserved process exits. The scratch mutation and raster fixtures are adversarial review probes, not fabricated product evidence.

```json
{"schema_version":"evidence.v1","check_id":"s36-review-inventory","command":"rtk proxy P:/av-kit/.venv/Scripts/python.exe -B -X utf8 C:/Temp/av-kit/s36-review-inventory.py","cwd":"P:/av-kit/.claude/worktrees/s36-capture-render-fidelity","scope":"plan references, task state, SSOT prerequisites and literal census","phase":"static","exit_code":0,"result":"pass","tested_state":"78610200ea2e7efd52318ea95c3e48b6df4993ba+2f81f66b2c2e3d0ba6a3dc72401dd5d28f08aa64ceff30e90d339bdf3260fa10","output":"37 references: 28 existing, 9 explicitly planned creations, unexplained_missing=[]; 26/26 task rows unchecked; no baseline, walkthrough or implementation handoff; MEU-39/59/67 approved; MEU-82/83/84 pending; MEU-81/85/86 registered pending."}
```

```json
{"schema_version":"evidence.v1","check_id":"s36-review-task-contract","command":"rtk proxy P:/av-kit/.venv/Scripts/python.exe -B tools/lint_task_contract.py --allowed-builder-classes avkit_builder,avkit_coordinator,avkit_verifier --task docs/execution/plans/2026-10-14-capture-render-fidelity/task.md","cwd":"P:/av-kit/.claude/worktrees/s36-capture-render-fidelity","scope":"task-table structure and dependencies","phase":"static","exit_code":0,"result":"pass","tested_state":"78610200ea2e7efd52318ea95c3e48b6df4993ba+2f81f66b2c2e3d0ba6a3dc72401dd5d28f08aa64ceff30e90d339bdf3260fa10","output":"OK: 26 row(s); 10-column table (with builder_model); 24 row(s) fully checked: backticked, exit-code re-raised, receipt under RECEIPTS_DIR; dependencies resolve and are acyclic; 2 row(s) exempt (view_file): H1-5, H2-1"}
```

```json
{"schema_version":"evidence.v1","check_id":"s36-review-adversarial-probes","command":"rtk proxy P:/av-kit/.venv/Scripts/python.exe -B -X utf8 C:/Temp/av-kit/s36-review-probes.py","cwd":"P:/av-kit/.claude/worktrees/s36-capture-render-fidelity","scope":"plan-local identity and Red controls; literal BAKE_AA consistency on Pillow 12.3.0","phase":"targeted","exit_code":0,"result":"pass","tested_state":"78610200ea2e7efd52318ea95c3e48b6df4993ba+2f81f66b2c2e3d0ba6a3dc72401dd5d28f08aa64ceff30e90d339bdf3260fa10","output":"Probe execution completed and demonstrated defects, not product success. uv.lock, ui/package-lock.json, ui/tsconfig.json and ui/electron.vite.config.ts each changed bytes while state_unchanged=true. Actual evidence_problems(require_full=True, expected_state=current_state) accepted the synthetic historical full record: problems=[]. Selected-source positive mutation was detected. red-check CLI: assertion control exit 0, unrelated ImportError control exit 1, pure Electron launch failure with a new-helper name exit 0, locator timeout with source-context assert exit 0. Literal BAKE_AA: clipped-tip column maximum coverage=41/255; horizontal head exterior violating pixels=117; diagonal interior violations=34; blended edge fraction=0.4872611464968153."}
```

For F1, the scratch probe uses the plan's exact `head=max(10,5*stroke)`, angle `.45`, `back=head*cos(.45)-1`, clipped outward-rounded tile with `stroke/2+2` padding, `L` mask, point mapping `4*(p-origin)+1.5`, width `4*stroke`, and LANCZOS resize. Head-exterior classification uses pixel centres `(x+.5,y+.5)` and perpendicular distance greater than 1 px beyond either sloped side, with x beyond the base. The first exterior mismatch `(146,32)` has coverage 3, producing `(255,252,252)` on white for red rather than exact white. The diagonal case excludes shaft end regions; `(171,30)` is 1.980 px from the shaft centreline (at least 1 px inside a width-6 shaft), coverage 227, yielding `(28,28,255)` for blue, outside the allowed 8-channel tolerance. The clipped-tip example is `(20,60)→(119,60)`, stroke 3, on 120×120 white; its tip column contains no fully coloured pixel. This transcribes a prescribed algorithm; it is not a test of future production code.

For F3, the accepted negative fixture is exactly:

```text
1 failed
Error: electron.launch: Process failed to launch!
  at test('AC-84.5 viewedFilePath opens the selected image')
```

Observed CLI output: `red-check: 1 receipt(s), 0 problem(s)`, exit 0. No assertion ran and no missing-export diagnostic exists in that fixture.

```json
{"schema_version":"evidence.v1","check_id":"s36-review-ascent","command":"rtk proxy P:/av-kit/.venv/Scripts/python.exe -B -X utf8 -c \"import math; from PIL import ImageFont; from pathlib import Path; mismatches=[]; font='C:/Windows/Fonts/segoeui.ttf'; print('font_exists',Path(font).is_file()); [mismatches.append(s) for s in range(1,1001) if ImageFont.truetype(font,s).getmetrics()[0] != math.ceil(((2210*s*2048+0x8000)>>16)/64)]; print('SEGOE_ASCENT sizes=1..1000 mismatches=',mismatches)\"","cwd":"P:/av-kit/.claude/worktrees/s36-capture-render-fidelity","scope":"local Segoe font and proposed ascent arithmetic","phase":"targeted","exit_code":0,"result":"pass","tested_state":"78610200ea2e7efd52318ea95c3e48b6df4993ba+2f81f66b2c2e3d0ba6a3dc72401dd5d28f08aa64ceff30e90d339bdf3260fa10","output":"font_exists True; SEGOE_ASCENT sizes=1..1000 mismatches= []"}
```

Python `ast.parse` accepted both local Python tools; PowerShell's parser accepted `session-gate.ps1` with zero errors. These are syntax observations only. The unfiltered test-expectation census found the six planned amendment sites; comparisons of unchanged before/after endpoints and unrelated shell uses do not introduce an additional contradiction. No actual test assertions were edited.

Review input SHA-256 values:

| File | SHA-256 |
|---|---|
| implementation-plan.md | `0d6c0f8e52c08b540b4f0d7050dfa97fd7a4d773929679d5d2afbe6ef6d859e9` |
| task.md | `afcbd2cdd455bf235885d67a458e40ad3f5c5dfd4a0cf8fd34400a8b0137e0ed` |
| identity.py | `64bc9d8ced2de86b7db7c6b20e7c658ab10ece13e3ac9d6d921f63fa5bd10b86` |
| red-check.py | `0b36f58db6efa3dc9f5872f3b4c8f52160531fcaeb2181129ff6f75b8856dc2a` |
| session-gate.ps1 | `a07f1d1e3874862e0312d1fe3e9ddeb7faf156a19794e3a3580fbeccadcd2a75` |

## Verdict

`changes_required` — **intent achieved: partial**. F1 prevents MEU-83's prescribed Green, and F2 demonstrably false-passes the final evidence freshness check. Resolve those in `/plan-corrections`, address the non-blocking notes in the same correction where practical, then resubmit in this rolling report with the required raw blast-radius census and per-hit dispositions.

**Open assumptions:** D-12 remains the explicit execution-message preference; this review evaluates its documented recommended default. The local font/ascent result supports MEU-82's arithmetic, but Chromium-vs-Pillow pixels still require the planned Electron test. No new human decision is requested by this review.

**Residual risk:** No implementation or real Electron behavior is certified. The raster probe follows the algorithm literally; corrected raster/oracle choices require their own decisive positive and negative fixtures. The independent execution review and authoritative full gate remain required after implementation. Review caps and existing findings were preserved; this report does not imply an execution transition.

**Follow-up:** `/plan-corrections`; stop at this review boundary. No fixes, commits or pushes were performed.

## Corrections Applied — 2026-10-14

Author: the plan author (Claude, Anthropic), via plan-corrections. This is not a review verdict. The frontmatter `verdict: corrections_applied` only marks that round-1 findings were addressed. Approval needs an independent re-review (round 2) or Mat as the fallback reviewer.

| Finding | Correction | Proof |
|---|---|---|
| F1 | The plan now states `PIXEL_CENTRE` (pixel `(x, y)` is sampled at mark coordinate `(x, y)`, which is Pillow's convention) and `AA_LIMITS` (halo 3 px, tolerance 8). `ARROW_TIP_ORACLE` separates a leak (coverage ≥ 0.5 more than 1 px outside the head) from the filter halo. `EDGE_ORACLE`'s interior starts 1.5 px inside the edge. AC-83.7 probes `(111, 60)`, 8 px behind the clipped tip. `BAKE_AA` pads by `stroke/2 + 4`. AC-83.5 adds a monkeypatched full-shaft negative control. | R-3, [`aa-oracle-probe.py`](../../../docs/execution/plans/2026-10-14-capture-render-fidelity/aa-oracle-probe.py) exit 0: positive 0 leak pixels, halo deviation 0, edge blend 0.5117, interior deviation 4. Full-shaft negative: 58 leak pixels. Baseline: 53 leak pixels, blend 0.0. Clipped probe `(255,0,0)`. |
| F2 | `tested_state` hashes the whole work tree minus the post-gate project artifacts, plus the live runtime (Python, node, installed electron and @playwright/test, the `segoeui.ttf` SHA, `ELECTRON_RUN_AS_NODE`). `--state-only` is the same value. The gate compares it before and after. H1-6b re-derives it live. | R-4, `identity.py --selftest` exit 0. Each of the lockfiles, `ui/tsconfig.json`, `ui/electron.vite.config.ts`, `.agent/docs/commands.md`, `session-gate.ps1` and a source file changes the state and makes `evidence_problems(require_full=True)` refuse the earlier record. An untracked file and a runtime change are detected. Artifact edits leave the state unchanged. |
| F3 | Red rows write `<receipt>.exit`. `red-check.py` needs a non-zero exit, a failing summary and a diagnostic line that attributes the failure. It refuses launch, timeout, unrelated-import and setup failures. | R-5, `red-check.py --selftest` exit 0, 9 fixtures, 0 wrong. The review's launch and timeout receipts are refused. |
| F4 | `session-gate.ps1` runs identity, all static checks (including `SCOPE_CHECK`), full, runtime, then identity. Every later step prints `not_run`. | Plan §4; the script parses with 0 errors. |
| F5 | `meu-registry.md`, `current-focus.md` and `known-issues.md` were added to Files Modified and to the `scope-paths` allow-list. H2-2 runs `issue_triage.py render --check`. | `lint_task_contract.py` exit 0 |
| F6 | `ARROW_HEAD` is referenced by name at User Review, the D-12 `chosen`, the brief and the option table. | Census: "factor 5" 0 hits; `0.45` only in the definition and its derivation. |

Blast-radius census: 9 values changed, 18 variants swept, 27 sites found, 21 updated, 6 confirmed consistent. The receipts are `C:/Temp/av-kit/census-s36r1-*.txt`, and the plan §Round 1 Review Corrections has the detail.

Next: round 2 needs a ledger continuation. The review ledger refuses round 2 because round 1 spent 10,357,875 of the 10,500,000-token budget. Only a named human can grant more (`review_ledger.py continue`).

## Recheck (2026-10-14) — Round 2

**Workflow:** `/plan-critical-review`, independent recheck; **Agent:** `codex-gpt-6.1-sol`; **Verdict:** `changes_required` under the explicit PR-6 pre-verdict procedural exception.

### Intent Anchor

Session 36 makes capture rendering faithful: MEU-82 aligns the text preview baseline with the baked PNG, MEU-83 fixes arrow shaft/head geometry and anti-aliases the baked head, MEU-84 reconciles the annotated path and makes Open file/folder target the viewed file, all within PRODUCT_SCOPE.

**Intent achieved: partial.** Readiness to achieve the complete goal is not established this round: PR-6 prevents substantive re-review until the correction census has per-hit dispositions. The fresh probes below support the reported corrections but do not constitute approval of the corrected plan or implementation.

### Findings / Pre-Verdict Prerequisite

**PR-6 fails: the raw census is present, but its correction log does not assign each `file:line` a disposition.** The reviewer independently read all 18 `census-s36r1-*.txt` receipts and extracted 27 hit records at 22 distinct locations, with no truncation marker. `implementation-plan.md:567–578` supplies totals, blanket classifications ("21 were updated (every new-value hit)"), and three grouped explanations for the six old-value hits. Neither that section nor the author's correction table names each hit's `file:line` with `updated` or `confirmed-consistent`. For example, the receipts inventory `task.md:41`, `:44`, `:47`, `:50`, `:54`, `:60`, `:67` and `implementation-plan.md:205`; the correction log contains no per-location disposition rows for them.

The violated procedural contract is `.agent/workflows/plan-critical-review.md` **PR-6**, backed by `.agent/workflows/plan-corrections.md:191–193`: "record each hit in the correction log marked `updated` or `confirmed-consistent`." PR-6 explicitly distinguishes the raw receipt from the per-hit correction log and requires `changes_required` naming this prerequisite alone, without reviewing corrected content. This is **not a severity-rated finding** and is not counted as another delivery defect or recurring control-defeat mechanism. Frontmatter therefore reports zero new severity-rated findings, one procedural gate, and six prior findings awaiting independent disposition.

**Follow-up:** Use `/plan-corrections` to add the receipt-to-`file:line` disposition mapping for every hit, including each old-value hit's reason. Preserve the complete raw receipts. Then resubmit this same rolling report within the existing loop and its limits. The reviewer has not supplied the corrector's missing dispositions on their behalf.

### Scope and Review State

Assigned targets remain `implementation-plan.md`, `task.md`, `session-gate.ps1`, `identity.py`, `red-check.py`, and `aa-oracle-probe.py` in `docs/execution/plans/2026-10-14-capture-render-fidelity/`. This round assessed the submission prerequisite and ran the three explicitly requested planning probes. Substantive F1–F6 closure and correction-induced regression review are **not assessed**, as required by PR-6. Reading or executing a probe is not a finding that its complete contract is correct.

Unstarted state was independently confirmed: 26 unchecked task rows, no `baseline.sha`, no `walkthrough.md`, and no MEU-82/83/84 implementation handoff. The live ledger contains round 1 plus a round-2 token continuation granted to Mat at `2026-10-14T23:26:46-04:00`; the earlier correction note about missing continuation is historical. This direct review did not change or reset the ledger, manufacture usage, or authorize execution.

### Prior Pass Summary

| Finding | Author's disposition | Independent round-2 result / resolved? |
|---|---|---|
| F1 — raster/oracle disagreement | Fixed | **Not independently closed; pending PR-6.** Fresh R-3 reproduces the reported positive and negative metrics, including zero positive leaks, 58 full-shaft leaks and 53 baseline leaks. |
| F2 — incomplete freshness identity | Fixed | **Not independently closed; pending PR-6.** R-4 fails in the inherited signing environment, then passes with signing disabled only for its disposable scratch-repository fixture; all seven named file mutations refuse historical evidence. |
| F3 — setup failures accepted as Red | Fixed | **Not independently closed; pending PR-6.** Fresh R-5 reports 9 fixtures, 0 wrong; both original launch/timeout fixtures are refused. |
| F4 — static/full stage order | Fixed | **Not assessed; pending PR-6.** No new approval of gate ordering or execution of the product gate. |
| F5 — omitted administrative paths | Fixed | **Not assessed; pending PR-6.** No new approval of the inventory or allow-list. |
| F6 — repeated head constants | Fixed | **Not assessed; pending PR-6.** No new approval of the literal census or single-statement discipline. |

### Confirmed Observations

The user's requested receipts were re-run with `P:/av-kit/.venv/Scripts/python.exe`, rather than trusted from the author's pasted output. These are planning probes only. Commands below ran from `P:/av-kit/.claude/worktrees/s36-capture-render-fidelity`, through `rtk proxy`, with all streams redirected under `C:/Temp/av-kit`, immediate exit capture, receipt read-back and exit propagation. No product suite, build, dependency installation, or Electron launch was performed.

R-4's first run exited 1 because its temporary repository inherits `commit.gpgsign=true`. An instrumented diagnostic run printed the child Git exit 128 and `error: No private key found for "C:/Users/Mat/.ssh/id_ed25519_signing"?` / `fatal: failed to write commit object`. The retry used process-local `GIT_CONFIG_COUNT=1`, `GIT_CONFIG_KEY_0=commit.gpgsign`, `GIT_CONFIG_VALUE_0=false` and `TMP=TEMP=C:/Temp/av-kit`. No repository/global Git configuration was changed and no project commit was created. The qualified retry proves the selftest's fixtures, not its portability in the unchanged inherited environment. This observation is retained as requested probe evidence, not an additional finding past the procedural gate.

### Checklist Results

| Check | Result | Command / procedure | Exit | Evidence |
|---|---|---|---|---|
| PR-6 resubmission prerequisite | fail | Manually read all 18 named census receipts and compare every extracted location with plan §Round 1 Review Corrections and report §Corrections Applied; observer `codex-gpt-6.1-sol` | null | Raw hits exist; correction log has aggregate classifications and grouped reasons, without per-`file:line` dispositions. |
| PR-2 not-started confirmation | pass | `rtk proxy P:/av-kit/.venv/Scripts/python.exe -B -X utf8 C:/Temp/av-kit/s36-r2-observations.py` | 0 | 26 unchecked; baseline/walkthrough absent; implementation handoff list empty. |
| Requested R-3 | pass | `rtk proxy P:/av-kit/.venv/Scripts/python.exe -B -X utf8 docs/execution/plans/2026-10-14-capture-render-fidelity/aa-oracle-probe.py --pad 4` | 0 | Positive metrics reproduced; both tip negatives and baseline edge negative refused. |
| Requested R-4, inherited environment | fail | `rtk proxy P:/av-kit/.venv/Scripts/python.exe -B -X utf8 docs/execution/plans/2026-10-14-capture-render-fidelity/identity.py --selftest` | 1 | Temporary fixture commit failed, Git exit 128; no mutation assertions ran. |
| Requested R-4, isolated scratch-signing retry | pass | Process-local signing override described above, followed by the same exact R-4 argv | 0 | 0 selftest failures; seven historical-evidence refusals, untracked/runtime changes detected, artifact changes excluded. |
| Requested R-5 | pass | `rtk proxy P:/av-kit/.venv/Scripts/python.exe -B -X utf8 docs/execution/plans/2026-10-14-capture-render-fidelity/red-check.py --selftest` | 0 | 9 fixtures, 0 wrong. |
| PR-1, PR-3–5, PR-7–9; substantive DR checks | n/a | Not assessed after failed PR-6 precondition | null | No substantive findings or resolved statuses inferred from passing probe processes. |
| Implementation/runtime certification | n/a | Not run during this plan review | null | Plan remains unstarted. |

### Durable Evidence

Review input identity below is HEAD plus SHA-256 of the sorted six target-file SHA-256 map. It identifies this planning observation scope; it is **not** the product D6 identity. All six hashes were independently collected before editing this report. The review report is excluded from that scope.

```json
{"schema_version":"evidence.v1","check_id":"s36-r2-census-inventory","command":"rtk proxy P:/av-kit/.venv/Scripts/python.exe -B -X utf8 C:/Temp/av-kit/s36-r2-observations.py","cwd":"P:/av-kit/.claude/worktrees/s36-capture-render-fidelity","scope":"18 correction census receipts; six target-file hashes; task/readiness inventory","phase":"static","exit_code":0,"result":"pass","tested_state":"78610200ea2e7efd52318ea95c3e48b6df4993ba+db03a072e9d93a234e97a4e006b57eb8f6a51895205b63334ee60432e82a91d6","output":"18 receipts; 27 hit records; 22 unique locations; truncation=False for every receipt. 26 unchecked tasks; baseline.sha=False; walkthrough.md=False; implementation handoffs=[]. Extraction succeeds; manual PR-6 comparison fails because correction log has no per-location disposition mapping.","fresh":true}
```

```json
{"schema_version":"evidence.v1","check_id":"s36-r2-R3","command":"rtk proxy P:/av-kit/.venv/Scripts/python.exe -B -X utf8 docs/execution/plans/2026-10-14-capture-render-fidelity/aa-oracle-probe.py --pad 4","cwd":"P:/av-kit/.claude/worktrees/s36-capture-render-fidelity","scope":"requested literal-AA planning calibration and negative fixtures","phase":"targeted","exit_code":0,"result":"pass","tested_state":"78610200ea2e7efd52318ea95c3e48b6df4993ba+db03a072e9d93a234e97a4e006b57eb8f6a51895205b63334ee60432e82a91d6","output":"positive: halo_max_dev=0, leak_pixels=0, edge_pixels=641, blend_fraction=0.5117, interior_max_dev=4, outside_tile_changed=0. full_aa: halo_max_dev=255, leak_pixels=58. baseline: halo_max_dev=255, leak_pixels=53, blend_fraction=0.0. Clipped probe_d=8, probe_pixel=(255,0,0), outside_image_unchanged=True. All seven printed verdict booleans=True; pad_extra=4.0.","fresh":true}
```

```json
{"schema_version":"evidence.v1","check_id":"s36-r2-R4-inherited","command":"rtk proxy P:/av-kit/.venv/Scripts/python.exe -B -X utf8 docs/execution/plans/2026-10-14-capture-render-fidelity/identity.py --selftest","cwd":"P:/av-kit/.claude/worktrees/s36-capture-render-fidelity","scope":"requested identity selftest with inherited Git signing configuration","phase":"targeted","exit_code":1,"result":"fail","tested_state":"78610200ea2e7efd52318ea95c3e48b6df4993ba+db03a072e9d93a234e97a4e006b57eb8f6a51895205b63334ee60432e82a91d6","output":"CalledProcessError at identity.py:109: git -c user.email=s@t -c user.name=s commit -qm base returned exit 128. No mutation assertions ran.","fresh":true}
```

```json
{"schema_version":"evidence.v1","check_id":"s36-r2-R4-scratch-retry","command":"$env:RECEIPTS_DIR='C:/Temp/av-kit'; $env:TMP='C:/Temp/av-kit'; $env:TEMP='C:/Temp/av-kit'; $env:GIT_CONFIG_COUNT='1'; $env:GIT_CONFIG_KEY_0='commit.gpgsign'; $env:GIT_CONFIG_VALUE_0='false'; rtk proxy P:/av-kit/.venv/Scripts/python.exe -B -X utf8 docs/execution/plans/2026-10-14-capture-render-fidelity/identity.py --selftest","cwd":"P:/av-kit/.claude/worktrees/s36-capture-render-fidelity","scope":"identity selftest with process-local unsigned disposable Git fixture","phase":"targeted","exit_code":0,"result":"pass","tested_state":"78610200ea2e7efd52318ea95c3e48b6df4993ba+db03a072e9d93a234e97a4e006b57eb8f6a51895205b63334ee60432e82a91d6","output":"uv.lock, ui/package-lock.json, ui/tsconfig.json, ui/electron.vite.config.ts, .agent/docs/commands.md, plan session-gate.ps1 and packages/x.py: state_changed=True historical_refused=True for each. Untracked test and runtime node version: state_changed=True. Walkthrough, handoff and build-plan artifact edits: state_unchanged=True. identity selftest: 0 failure(s).","fresh":true}
```

```json
{"schema_version":"evidence.v1","check_id":"s36-r2-R5","command":"rtk proxy P:/av-kit/.venv/Scripts/python.exe -B -X utf8 docs/execution/plans/2026-10-14-capture-render-fidelity/red-check.py --selftest","cwd":"P:/av-kit/.claude/worktrees/s36-capture-render-fidelity","scope":"requested Red-proof positive and negative fixtures","phase":"targeted","exit_code":0,"result":"pass","tested_state":"78610200ea2e7efd52318ea95c3e48b6df4993ba+db03a072e9d93a234e97a4e006b57eb8f6a51895205b63334ee60432e82a91d6","output":"pytest-assertion, pytest-new-export, vitest-new-export, playwright-assertion: pass as expected. electron-launch, locator-timeout, unrelated-import, passing-run, no-exit-file: refused as expected. red-check selftest: 9 fixture(s), 0 wrong: [].","fresh":true}
```

### Verdict

`changes_required` — **PR-6 procedural prerequisite only; intent achieved: partial.** This is the workflow's explicit pre-severity exception, not a new claim that the corrected product design is defective. F1–F6 remain pending independent recheck, and no conclusion is issued on new defects or regressions. Passing the three requested probes cannot bypass the prerequisite or prove the whole plan achieves the registered goal.

**Residual risk:** Corrected plan/tooling semantics and all implementation/runtime behavior remain uncertified. The inherited-signing R-4 failure and qualified successful retry are both disclosed. Only this canonical review file changed in the repository; the plan, scripts, tests, product files and ledger were preserved. No project commit or push occurred. The next action is correction of the census log followed by authorized resubmission; no fixes or execution were chained from this review.

🕐 Completed: 2026-10-14 23:30 (EDT)

## Corrections Applied — 2026-10-14 (round 2)

Author: the plan author (Claude, Anthropic), via plan-corrections. This is not a review verdict. `corrections_applied` only marks that the round-2 procedural gate was addressed. F1–F6 still await independent closure.

| Item | Correction | Proof |
|---|---|---|
| PR-6: no per-hit dispositions | New plan-local [`census-r1.py`](../../../docs/execution/plans/2026-10-14-capture-render-fidelity/census-r1.py) re-runs the same 18 variants with `rtk proxy rg -F -n`. It writes one raw receipt per variant to `C:/Temp/av-kit/census-s36r2-<variant>.txt`, and the round-1 `census-s36r1-*` receipts are unchanged. It renders one plan table row per hit (variant, value, `file:line`, `updated` or `confirmed-consistent`, reason) from content-anchored rules. `--check` fails on an unmatched hit, an ambiguous hit, an unused rule, or a table that differs from the receipts. The table quotes no search term, so it never matches itself. | `census-r1.py --check` exit 0 on three repeat runs: 33 hits, 21 updated, 12 confirmed-consistent, 6 variants with no hit. The 6 hits beyond round 1's 27 are the round-1 correction log's own rows. rg output order varied between runs, so the hits are sorted. |
| R-4 portability (an observation, not a finding) | `identity.py --selftest` makes its scratch commit with `-c commit.gpgsign=false`, so inherited signing cannot abort it. | Exit 0 with a missing signing key forced via `GIT_CONFIG_*` (`commit.gpgsign=true`, `gpg.format=ssh`, absent key). A control copy without the override fails with git exit 128 in the same setup, which reproduces the review's failure. |

Also re-verified: `lint_task_contract.py` exit 0 (26 rows), R-3 exit 0, R-5 exit 0.

Ledger note: the wrapper's schema check refused round 2's `final.json` (`findings: [] should be non-empty`). PR-6 says a procedural gate carries no severity-rated finding, so the verdict schema and the workflow conflict. As a result, round 2 was not recorded in the ledger, which still shows 1 of 3 rounds and 10,357,875 tokens. The next dispatch is the third Codex review and is labelled round 3. It is the last round under the cap.

## Recheck (2026-10-14) — Round 3

**Workflow:** `/plan-critical-review`; **Agent:** `codex-gpt-6.1-sol`, independent of author `claude-code-local` (Anthropic); **Verdict:** `approved`. **Current counts:** zero new findings, zero blocking findings, zero procedural gates; F1–F6 independently resolved. Earlier verdicts and author correction notes above are historical.

### Intent Anchor

Session 36 makes capture rendering faithful: MEU-82 aligns the text preview baseline with the baked PNG, MEU-83 fixes arrow shaft/head geometry and anti-aliases the baked head, MEU-84 reconciles the annotated path and makes Open file/folder target the viewed file, all within PRODUCT_SCOPE.

**Would executing this plan deliver that objective? Yes.** The corrected raster now satisfies its defined positive oracles while rejecting the two defective drawings. The text-baseline and viewed-file changes retain concrete production entrypoints, tests and negative cases. Required product changes, test amendments, scope constraints and prerequisites are accounted for. This is approval of the unstarted plan's readiness, not certification of implemented behavior.

### Findings

**No new Critical, High, Medium or Low findings. No blocking finding remains.** The original F1–F6 rows are independently dispositioned below. Residual limits of planning probes and heuristic evidence checks are disclosed once below; they do not establish a new, materially different delivery failure or justify another review round.

### Scope and Review State

Reviewed all seven assigned files in `docs/execution/plans/2026-10-14-capture-render-fidelity/`: `implementation-plan.md`, `task.md`, `session-gate.ps1`, `identity.py`, `red-check.py`, `aa-oracle-probe.py`, and `census-r1.py`. Cross-checked the existing rolling report and template, latest peer plan review (`2026-10-02-capture-flatten-backup-plan-critical-review.md`), build-plan 09's geometry/MEU-82–84/deferral/dependency sections, Session 36 grouping and carry-forward decisions, SSOT prerequisites and deferred MEUs, D6 commands and input-identity policy, architecture/testing rules, and relevant renderer, command, main-process, adapter and service source paths. No additional implementation handoff was discovered.

HEAD remains `78610200ea2e7efd52318ea95c3e48b6df4993ba`. All 26 task rows are unchecked. `baseline.sha`, `walkthrough.md` and all three MEU implementation handoffs are absent. SSOT has MEU-39/59/67 approved and MEU-82/83/84 pending; the plan is unstarted. The report and plan folder were already untracked before this review; that is preserved, not treated as newly created work by this reviewer.

This is the **third actual review and the last under the three-round cap**. The existing ledger was read: it still contains only recorded round 1 and Mat's token continuation. Round 2's wrapper rejection explains the discrepancy. This report and its verdict use round 3 as explicitly requested; the ledger was not reset, renumbered, recorded into, or otherwise modified. No additional round is implied by the ledger's missing round-2 entry. The collecting orchestrator must preserve this actual-review history when validating/recording the verdict; the reviewer does not manufacture a ledger receipt.

### PR-6 — Verified Before Substantive Recheck

Ran `python docs/execution/plans/2026-10-14-capture-render-fidelity/census-r1.py --check` first: exit 0, `census-r1 check: 33 hit(s), 0 problem(s)`. Then independently read all 18 newly generated `C:/Temp/av-kit/census-s36r2-*.txt` receipts, including the six empty ones, and compared each raw hit with the disposition table at `implementation-plan.md:570–609`. An independent extractor, separate from `census-r1.py`, found **33 raw hit records and exactly 33 matching per-hit dispositions, with no missing/extra mapping or truncation marker**. The table records 21 updated and 12 confirmed-consistent hits, with explicit reasons for retained old terms. Thus **PR-6 passes**, and the substantive recheck was performed in this round.

`census-r1.py --check` runs only sweeps and writes scratch receipts; it does not take the script's `--write` branch. The rules bind variant, file and content anchor; a missing, duplicate or unused rule and a stale rendered table are refusal paths. The six hits added since round 1 are correction-log references, each explicitly dispositioned. No substantive review result was inferred from the author's `corrections_applied` status.

### Prior Pass Summary — Independent F1–F6 Dispositions

| Finding | Resolved? | Independent observation and current references |
|---|---|---|
| F1 — mandated raster and acceptance oracles disagree | **Yes** | Read `BAKE_AA`, `PIXEL_CENTRE`, `AA_LIMITS`, both oracles and AC-83.5–83.7 (`implementation-plan.md:123–127`, `:201–205`), then traced the literal probe against those rules. Fresh R-3 with the required parent-workspace Python and `--pad 4` exits 0: positive leaks 0, halo deviation 0, edge blends 0.5117 over 641 pixels, interior deviation 4 (within tolerance 8), unchanged pixels outside the tile. The AA/full-shaft negative has 58 leaks, baseline has 53 leaks and edge blend 0.0; both are refused. Clipped probe `(111,60)` is `(255,0,0)` and a wholly external tile is unchanged. The new oracle still detects the actual shaft defect rather than merely accepting both drawings. |
| F2 — stale evidence survives relevant config changes | **Yes** | `identity.py:74–84` binds the worktree diff/untracked files and live runtime object; `main` computes the same state before choosing full or `--state-only` output (`:166–172`). H1-6b (`task.md:60`) re-derives that state, and the actual gate compares before/after (`session-gate.ps1:113–120`). Fresh R-4 exits 0: all seven named file mutations change the state and refuse historical evidence through the real `durable_evidence.evidence_problems` predicate; untracked/runtime changes are detected; intended artifact edits are excluded. The round-2 signing correction at `identity.py:111` also passes with inherited signing enabled and an explicitly absent key. |
| F3 — setup failures accepted as intended Red | **Yes, for the reported failure modes** | Read `red-check.py:69–92` and the `.exit` capture in task rows 2/4/6 (`task.md:41`, `:44`, `:47`). Fresh R-5 exits 0, 9 fixtures, 0 wrong. The exact reported Electron-launch and locator-timeout fixtures are refused despite their helper/assertion text; assertion/new-export positives pass, while unrelated import, zero exit and absent exit-file negatives are refused. Receipt parsing remains a heuristic; see residual limits below. |
| F4 — behavioral suite precedes all static checks | **Yes** | All eight static steps precede `py-tests` in the live `$steps` table (`session-gate.ps1:78–96`), consistent with plan §4. A scratch harness retained that table and the actual execution/fail-fast loop, replacing only root/baseline/receipt setup and stubbing every native command. Success traversed all 18 steps. Injected `ui-types` failure propagated exit 23, executed only the first five steps, and marked all 13 later steps `not_run`. A changed ending identity propagated exit 1. No product command ran in these probes. |
| F5 — administrative outputs missing from inventory/allow-list | **Yes** | Independently compared each of `.agent/context/meu-registry.md`, `current-focus.md`, and `known-issues.md`: all three are present in the Files Modified table (`implementation-plan.md:292–295`) and the gate allow-list (`session-gate.ps1:62–65`). H2-2 (`task.md:67`) explicitly regenerates both derived documents and checks them. The task-contract linter exits 0 for all 26 rows. |
| F6 — head constants restated at multiple decision sites | **Yes** | User Review, D-12 chosen/recommendation/options now reference `ARROW_HEAD`. Fresh old/new-term census and independent text inspection find `factor 5` zero times and `0.45` only at the single definition (`implementation-plan.md:118`) and its explicitly mathematical `SHAFT_INSIDE_HEAD` derivation (`:121`). The alternative's old constants are an option, not another live definition. |

### Regression and Contract Recheck

The correction-sensitive call chains remain reachable: `AnnotationMark` in `CaptureViewport.tsx` renders the text/arrow geometry; `CaptureAdapter._apply` dispatches arrows to `_apply_arrow`; `GET /captures` reaches `list_shots` → `scan_inbox` under the existing capture-file lock/uow; the page selection effect feeds `capture-commands`, which is called by both buttons and the palette; the existing main-process E2E branches can log the same IPC targets used by real `shell` calls. AC-82.6 compares preview pixels with a committed real-bake fixture pinned fresh by pytest, and AC-84.5 observes the main-process shell log. The plan schedules creation of those test fixtures/helpers before their dependent commands. No producer ends at a test-only substitute for the behavior it promises to verify.

Reviewed the widened identity exclusions against the documented post-gate artifacts, the script stage list and fail-fast exits, the revised Red receipt sidecars, admin allow-list additions, AA padding/oracle changes and census rules. Four Python tools parse; PowerShell reports zero syntax errors. The selected static/full/runtime commands match the registered Python/UI D6 scope; MCP/API product changes are outside this plan. Shortened arrow endpoints preserve the old inspectable `<g>` endpoint attributes through TA-5/TA-6, while zero-length and short arrows retain explicit cases. The text plate, rect/highlight and bake-format behavior remain frozen by `PRODUCT_SCOPE` and `SCOPE_CHECK`.

Referenced-path screening found existing executables or explicitly scheduled creations. UI task argv run with `npm --prefix ui`, so their `tests/unit/...` and `tests/e2e/...` paths resolve under `ui/`; they are not absent root-level executables. The new fixture writer, geometry/PNG fixtures, test modules, viewed-file helper, E2E shell module and closeout artifacts are declared deliverables. The GUI reference documents explicitly recorded as not shipped are not claimed as executable gates. Out-of-scope items match 09's Segoe/arrow/scan contracts and named deferrals; MEU-81/85/86 are real pending SSOT rows. No newly missing required deliverable, impossible sequencing, scope expansion or demonstrated false-green final product gate was found.

### Checklist Results

Manual rows were observed by `codex-gpt-6.1-sol` against the current seven input files and supporting local canon; their exits are null. Command rows used `rtk proxy`, redirected all streams beneath `C:/Temp/av-kit`, captured the child exit immediately, read the completed receipt, then propagated that exit.

| Check | Result | Command / procedure | Exit | Evidence |
|---|---|---|---|---|
| PR-6 correction prerequisite | pass | Census command and independent raw/table comparison described above | 0 / null | 18 receipts, 33 hits, 33 dispositions; missing/extra empty; no truncation. |
| PR-1 scope/order alignment; PR-3 task contract | pass | Read both complete documents; run `rtk proxy P:/av-kit/.venv/Scripts/python.exe -B -X utf8 tools/lint_task_contract.py --allowed-builder-classes avkit_builder,avkit_coordinator,avkit_verifier --task docs/execution/plans/2026-10-14-capture-render-fidelity/task.md` | 0 / null | 26 rows; 24 checked command cells, 2 source-read exemptions; dependencies resolve and are acyclic. |
| PR-2 unstarted confirmation | pass | `rtk proxy python -B -X utf8 C:/Temp/av-kit/s36r3-observe.py`; manual SSOT/source comparison | 0 / null | 26 unchecked; baseline/walkthrough absent; no implementation handoff; prerequisites approved and target MEUs pending. |
| PR-4 executable/oracle realism; PR-8 control chains | pass | Fresh R-3/R-4/R-5, scratch gate-control probe, and production-call-chain inspection | 0 / null | Original counterexamples refused; positives pass; static failure and changed identity refuse the gate. |
| PR-5 source traceability; PR-7 scope discipline | pass | Compare FIC/Out of Scope with build-plan 09, grouping, SSOT, and current code | null | All three MEU contracts retained; deferrals exist; scope exclusions follow cited canon. |
| PR-9 single-statement recheck | pass | Fresh census and independent inspection of definition/decision sites | 0 / null | F6 fixed; no conflicting live value found. |
| DR-1/2/3/6 claim, old-term and cross-reference integrity | pass | Compare correction claims with current files, receipt hits, scheduled outputs and references | null | Both correction rounds are reflected in live file state; history remains identified as history. |
| DR-4/5/7 robustness, reproducibility, freshness | pass | Independently execute named probes and compare decisive outputs | 0 / null | R-3/R-4/R-5 counts reproduced; no reliance on pasted author counts. |
| DR-8 truthful limits | pass | Compare verdict with unstarted task state and residual statement | null | Approval concerns plan readiness; implementation and runtime certification remain future work. |
| AV-1/3/4/6, adapted to planning | pass | Inspect FIC Red/Green sequencing, adversary assertions, no-skip contract and source labels | null | Planned AC-level assertions and intended Reds exist; planning probe positive/negative evidence reproduced. Actual product TDD not yet run. |
| AV-2/5, adapted to planning | pass | Read all plan-local tools and planned negative controls | null | The full-shaft monkeypatch intentionally supplies a defective collaborator to an oracle that must reject it; it does not neutralize a test. Future product files are inventoried, not falsely claimed complete. |
| Product full D6 / real Electron | n/a | Not run during this plan-only review | null | No installation, build, product suite or application launch. |

### Durable Evidence

Planning observation identity is HEAD plus SHA-256 of the sorted seven-target filename/hash map collected by the independent observer. It is **not** the future product D6 state. The report is outside that hash scope. Scratch scripts are observational scaffolding, not new plan deliverables.

```json
{"schema_version":"evidence.v1","check_id":"s36-r3-census","command":"rtk proxy python docs/execution/plans/2026-10-14-capture-render-fidelity/census-r1.py --check","cwd":"P:/av-kit/.claude/worktrees/s36-capture-render-fidelity","scope":"round-1 correction census and current per-hit plan table","phase":"static","exit_code":0,"result":"pass","tested_state":"78610200ea2e7efd52318ea95c3e48b6df4993ba+eddbeedf4ada7eca6a36ea2fd6dd469a32132c00669c5fa1ccce1ddb77108ba2","output":"census-r1 check: 33 hit(s), 0 problem(s)","fresh":true}
```

```json
{"schema_version":"evidence.v1","check_id":"s36-r3-independent-inventory","command":"rtk proxy python -B -X utf8 C:/Temp/av-kit/s36r3-observe.py","cwd":"P:/av-kit/.claude/worktrees/s36-capture-render-fidelity","scope":"independent receipt/table mapping, seven input hashes, readiness, Python syntax, F5/F6 inspection and referenced-path screening","phase":"static","exit_code":0,"result":"pass","tested_state":"78610200ea2e7efd52318ea95c3e48b6df4993ba+eddbeedf4ada7eca6a36ea2fd6dd469a32132c00669c5fa1ccce1ddb77108ba2","output":"18 raw receipts, 33 raw hits, 33 dispositions, missing=[], extra=[], truncation=False throughout. 26 tasks, 26 unchecked; baseline.sha=False, walkthrough.md=False, implementation_handoffs=[]. Four Python syntax checks pass. Three F5 administrative paths have plan_inventory=True and gate_allowed=True. F6 factor phrase=0; numeric angle only on lines 118 and 121. Absent referenced paths were manually classified as scheduled deliverables, UI-relative paths or explicitly unshipped documentation; SSOT statuses were separately read from the real YAML, since the scratch script's indentation-specific SSOT extractor returned not matched.","fresh":true}
```

```json
{"schema_version":"evidence.v1","check_id":"s36-r3-R3","command":"rtk proxy P:/av-kit/.venv/Scripts/python.exe -B docs/execution/plans/2026-10-14-capture-render-fidelity/aa-oracle-probe.py --pad 4","cwd":"P:/av-kit/.claude/worktrees/s36-capture-render-fidelity","scope":"literal BAKE_AA positive, full-shaft/baseline negatives, clipped/external tiles","phase":"targeted","exit_code":0,"result":"pass","tested_state":"78610200ea2e7efd52318ea95c3e48b6df4993ba+eddbeedf4ada7eca6a36ea2fd6dd469a32132c00669c5fa1ccce1ddb77108ba2","output":"positive: halo_max_dev=0, leak_pixels=0, edge_pixels=641, blend_fraction=0.5117, interior_max_dev=4, outside_tile_changed=0. full_aa: halo_max_dev=255, leak_pixels=58. baseline: halo_max_dev=255, leak_pixels=53, blend_fraction=0.0. Clipped tile=(14,47,120,74), probe_d=8, probe_pixel=(255,0,0), outside_image_unchanged=True. All seven verdict booleans=True; pad_extra=4.0.","fresh":true}
```

```json
{"schema_version":"evidence.v1","check_id":"s36-r3-R4","command":"rtk proxy python -B docs/execution/plans/2026-10-14-capture-render-fidelity/identity.py --selftest","cwd":"P:/av-kit/.claude/worktrees/s36-capture-render-fidelity","scope":"identity binding and historical-evidence refusal with inherited Git configuration","phase":"targeted","exit_code":0,"result":"pass","tested_state":"78610200ea2e7efd52318ea95c3e48b6df4993ba+eddbeedf4ada7eca6a36ea2fd6dd469a32132c00669c5fa1ccce1ddb77108ba2","output":"uv.lock, ui/package-lock.json, ui/tsconfig.json, ui/electron.vite.config.ts, .agent/docs/commands.md, session-gate.ps1 and packages/x.py each state_changed=True historical_refused=True. Untracked test and runtime node version each state_changed=True. Walkthrough, handoff and build-plan artifacts each state_unchanged=True. identity selftest: 0 failure(s).","fresh":true}
```

```json
{"schema_version":"evidence.v1","check_id":"s36-r3-R4-signing","command":"$env:TMP='C:/Temp/av-kit'; $env:TEMP='C:/Temp/av-kit'; $env:GIT_CONFIG_COUNT='3'; $env:GIT_CONFIG_KEY_0='commit.gpgsign'; $env:GIT_CONFIG_VALUE_0='true'; $env:GIT_CONFIG_KEY_1='gpg.format'; $env:GIT_CONFIG_VALUE_1='ssh'; $env:GIT_CONFIG_KEY_2='user.signingkey'; $env:GIT_CONFIG_VALUE_2='C:/Temp/av-kit/s36r3-intentionally-absent-signing-key'; rtk proxy P:/av-kit/.venv/Scripts/python.exe -B -X utf8 docs/execution/plans/2026-10-14-capture-render-fidelity/identity.py --selftest","cwd":"P:/av-kit/.claude/worktrees/s36-capture-render-fidelity","scope":"round-2 fix: disposable fixture commit with inherited signing and missing key","phase":"targeted","exit_code":0,"result":"pass","tested_state":"78610200ea2e7efd52318ea95c3e48b6df4993ba+eddbeedf4ada7eca6a36ea2fd6dd469a32132c00669c5fa1ccce1ddb77108ba2","output":"All seven bound file mutations changed state and refused historical evidence; untracked/runtime changes detected; all three artifact exclusions held; identity selftest: 0 failure(s). No project/global Git configuration changed and no project commit was created.","fresh":true}
```

```json
{"schema_version":"evidence.v1","check_id":"s36-r3-R5","command":"rtk proxy python -B docs/execution/plans/2026-10-14-capture-render-fidelity/red-check.py --selftest","cwd":"P:/av-kit/.claude/worktrees/s36-capture-render-fidelity","scope":"Red attribution positive and negative fixtures","phase":"targeted","exit_code":0,"result":"pass","tested_state":"78610200ea2e7efd52318ea95c3e48b6df4993ba+eddbeedf4ada7eca6a36ea2fd6dd469a32132c00669c5fa1ccce1ddb77108ba2","output":"pytest-assertion, pytest-new-export, vitest-new-export and playwright-assertion pass as expected. electron-launch, locator-timeout, unrelated-import, passing-run and no-exit-file refused as expected. red-check selftest: 9 fixture(s), 0 wrong: [].","fresh":true}
```

```json
{"schema_version":"evidence.v1","check_id":"s36-r3-gate-control","command":"rtk proxy pwsh -NoProfile -File C:/Temp/av-kit/s36r3-gate-control.ps1","cwd":"P:/av-kit/.claude/worktrees/s36-capture-render-fidelity","scope":"PowerShell syntax and actual gate table/loop under stubbed native commands","phase":"targeted","exit_code":0,"result":"pass","tested_state":"78610200ea2e7efd52318ea95c3e48b6df4993ba+eddbeedf4ada7eca6a36ea2fd6dd469a32132c00669c5fa1ccce1ddb77108ba2","output":"PowerShell parse errors=0. all-success: exit=0 calls=18 not_run=0. static-failure at ui-types: exit=23 calls=5 not_run=13; no behavioral command invoked. identity-mismatch: exit=1 calls=18. gate-control failures=0; all native commands stubbed; no product suite ran.","fresh":true}
```

```json
{"schema_version":"evidence.v1","check_id":"s36-r3-task-contract","command":"$env:RECEIPTS_DIR='C:/Temp/av-kit'; rtk proxy P:/av-kit/.venv/Scripts/python.exe -B -X utf8 tools/lint_task_contract.py --allowed-builder-classes avkit_builder,avkit_coordinator,avkit_verifier --task docs/execution/plans/2026-10-14-capture-render-fidelity/task.md","cwd":"P:/av-kit/.claude/worktrees/s36-capture-render-fidelity","scope":"unstarted task table and dependency graph","phase":"static","exit_code":0,"result":"pass","tested_state":"78610200ea2e7efd52318ea95c3e48b6df4993ba+eddbeedf4ada7eca6a36ea2fd6dd469a32132c00669c5fa1ccce1ddb77108ba2","output":"OK: 26 row(s); 10-column table (with builder_model); 24 row(s) fully checked: backticked, exit-code re-raised, receipt under RECEIPTS_DIR; dependencies resolve and are acyclic; 2 row(s) exempt (view_file): H1-5, H2-1.","fresh":true}
```

One reviewer scratch-observer attempt exited 1 while printing Unicode through Python's inherited cp1252 output encoding; the explicit `-X utf8` rerun above completed. The earlier SSOT regex extraction was not relied on as status evidence: actual SSOT rows were read and their approved/pending values are recorded above. These were reviewer-scaffolding limitations, not failed plan gates or product defects.

### Verdict and Follow-up

`approved` — **intent achieved: yes, at plan-review scope**. PR-6 passes and F1–F6 are resolved by current file state plus independently reproduced evidence. No new blocking regression was demonstrated. Frontmatter records round 3 and the current zero finding/gate counts; the two `## Recheck` headings preserve all three actual review rounds.

**Residual risk:** The AA probe transcribes the proposed algorithm; it does not test future production code. Real Chromium/Pillow text agreement, missing-file reconciliation and shell targets still require the planned tests and authoritative full D6. The Red checker uses a receipt-wide attribution flag rather than structured per-test failure objects (`red-check.py:82–90`), so its passing selftest is evidence for the reported fixtures, not a proof of every possible mixed-failure log. Identity selftests exercise the hash/refusal mechanism with synthetic runtime values; live dependency/environment identity and freshness must still be established during execution. These limits do not reopen the fixed surfaces through nearby predicate variants in this final round.

**Next:** The collecting agent validates this verdict against the existing loop/target/goal and preserves the disclosed round-history discrepancy. Execution remains behind the plan's **human** gate: wait for Mat's explicit execution message; apply D-12's documented default only as part of that authorized execution. No fourth plan review, fixes, implementation, commit or push was performed or authorized here. Only this canonical report was edited in the repository; scratch observations and mocked receipts stayed under `C:/Temp/av-kit` (the selftests use disposable temporary fixture repositories).

### Report Closeout Verification

Completion-preflight was applied within this explicitly review-only scope: the canonical `task.md` was read, its 26 unchecked implementation rows remain unchanged, the required rolling report exists, its current verdict is explicit, and its actual review count is three. Completing this review does not complete those implementation rows or authorize their execution.

```json
{"schema_version":"evidence.v1","check_id":"s36-r3-report-state","command":"rtk proxy P:/av-kit/.venv/Scripts/python.exe -B -X utf8 tools/validate_closeout_artifacts.py --review .agent/context/handoffs/2026-10-14-capture-render-fidelity-plan-critical-review.md --review-state-only --expected-review-mode plan --expected-target-plan docs/execution/plans/2026-10-14-capture-render-fidelity/implementation-plan.md --max-review-rounds 3 --output C:/Temp/av-kit/s36r3-review-state.json","cwd":"P:/av-kit/.claude/worktrees/s36-capture-render-fidelity","scope":"rolling report mode/target/verdict/count parsing; not ledger approval recording","phase":"static","exit_code":0,"result":"pass","tested_state":"78610200ea2e7efd52318ea95c3e48b6df4993ba+eddbeedf4ada7eca6a36ea2fd6dd469a32132c00669c5fa1ccce1ddb77108ba2","output":"OK: review_mode=plan; round 3 of 3; verdict=approved; open findings=0; state receipt written. Parsed target equals the assigned implementation-plan.md.","fresh":true}
```

```json
{"schema_version":"evidence.v1","check_id":"s36-r3-report-evidence","command":"rtk proxy P:/av-kit/.venv/Scripts/python.exe -B -X utf8 tools/durable_evidence.py .agent/context/handoffs/2026-10-14-capture-render-fidelity-plan-critical-review.md","cwd":"P:/av-kit/.claude/worktrees/s36-capture-render-fidelity","scope":"durable evidence record structure in the rolling report","phase":"static","exit_code":0,"result":"pass","tested_state":"78610200ea2e7efd52318ea95c3e48b6df4993ba+eddbeedf4ada7eca6a36ea2fd6dd469a32132c00669c5fa1ccce1ddb77108ba2","output":"OK: durable evidence records. Independent final observation re-derived the same seven-target planning input state; all 26 implementation tasks remain unchecked.","fresh":true}
```
