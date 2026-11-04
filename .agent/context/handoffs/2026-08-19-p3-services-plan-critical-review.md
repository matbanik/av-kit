---
date: "2026-08-19"
review_mode: "plan"
target_plan: "docs/execution/plans/2026-08-19-p3-services/implementation-plan.md"
verdict: "approved"
findings_count: 0
template_version: "2.1"
requested_verbosity: "standard"
agent: "gpt-5.6-sol"
review_round: 2
---

# Critical Review: p3-services

> **Review Mode**: `plan`
> **Verdict**: `changes_required`
> **Round**: 1

---

## Intent Anchor

Executing this plan is supposed to deliver MEU-13, MEU-10, MEU-11, and MEU-12 as tested application services under `avkit_core/services/`, using only the frozen Phase 1 types/ports and the existing UoW path, without REST, MCP, GUI, or adapter rewrites. As written, it would not reliably deliver that objective: several required Phase 3 behaviors are contradicted or untestable, and two completion controls can materially false-pass.

## Findings

| # | Severity | Confidence | Finding | File:Line | Recommendation | Status |
|---|----------|------------|---------|-----------|----------------|--------|
| 1 | High | High | **The plan removes spaCy even though every controlling local source requires it.** `PREPARE_CHUNK_ALGO` replaces sentence-aware spaCy segmentation with a hand-written `.!?` splitter and then labels spaCy out of scope. Phase 3 explicitly says the `chunk` step uses spaCy; the GUI spec repeats that requirement; Phase 7 describes how to bundle or degrade only that step if the model is unavailable. The cited Phase 7 basis therefore says the opposite of the plan. This is contract work disguised as out-of-scope work, violating PR-5 and PR-7/C2; executing the plan would deliver a materially different chunker. | `implementation-plan.md:212,391,404,457,522-523`; `docs/build-plan/03-service-layer.md:303`; `docs/build-plan/06-gui.md:819`; `docs/build-plan/07-distribution.md:151` | Restore the source-required spaCy sentence-boundary contract and its dependency/error tests, or obtain an explicit human-approved change to the controlling build-plan text before planning a different algorithm. | open |
| 2 | High | High | **The single transcript transition graph cannot execute two required workflows.** `TRANSCRIPT_PARENT_TRANSITIONS` omits `Processing -> Pending`, but AC-11.11 requires crash recovery to perform that edge. `TRANSCRIPT_ITEM_TRANSITIONS` omits `Failed -> Pending`, but AC-11.5 requires retrying failed items. The plan simultaneously requires every status write to use `transition()`. A coder must either violate the one-graph rule or fail the recovery/retry ACs, violating PR-5/PR-8. | `implementation-plan.md:102-103,189,209,347,353`; `docs/build-plan/03-service-layer.md:196,245,449` | Add the source-required recovery/retry edges to the canonical named graphs, with legal/illegal edge tests; do not introduce service-local graphs or raw `replace(status=...)` bypasses. | open |
| 3 | High | High | **Required service commands can be omitted while every planned AC passes.** The clearest case is `DownloadService.reset_failed(job_id)`: the plan correctly notes the frozen repository method is bulk/no-argument and locks the entity `get -> reset_failed() -> save` path, but no AC or Red task asserts the service method, the single-row effect, or that the bulk repository method is never called. The same AC gap covers required Phase 3 getters/reorder surfaces (`DownloadService.get_queue/get_processor_state/get_sabr_status`, transcript `reorder_queue/get_queue/get_job/get_processor_state`, and `TTSService.get_status`). This violates the complete FIC/TDD contract and PR-4; Phase 4 can receive an incomplete service surface even with green tests. | `implementation-plan.md:191,287,314`; `task.md:44-55`; `docs/build-plan/03-service-layer.md:113-117,198-203,318`; `packages/core/src/avkit_core/ports/storage.py:32` | Add source-labeled ACs and Red tests for every required command. For `reset_failed(job_id)`, assert only the selected Failed row resets, missing/wrong-state errors fail closed, and the frozen bulk repository method is not called. | open |
| 4 | High | High | **The extract mutex control is bound only to download extraction, not the required shared cross-service critical section.** Phase 3 requires one mutex across both `extract_info` and `extract_video_ids`. AC-10.11's only production chain is `add_to_queue -> ExtractCoordinator`, and its adversary runs concurrent download adds; AC-11.1 does not assert that `add_channel` enters the same coordinator/lock. `TranscriptService.add_channel` could call the frozen port directly while all listed tests pass, violating PR-8. | `implementation-plan.md:204,303,343,429`; `task.md:49`; `docs/build-plan/03-service-layer.md:170-176` | Add a cross-service concurrency oracle: overlap `DownloadService.add_to_queue` with `TranscriptService.add_channel` through one injected coordinator and assert the combined fake-port in-flight maximum is one. | open |
| 5 | High | High | **`ModelDownloadRuntime.fraction` has no tested producer.** The frozen catalog port supplies `on_progress(float)`, and Phase 3 requires callbacks to update the runtime fraction. AC-12.7 and the control register observe only `.state`; they never invoke/assert the callback value or fraction bounds/updates. A worker that discards the callback and leaves `fraction=0` passes every stated oracle, violating PR-8. | `implementation-plan.md:396,432`; `docs/build-plan/03-service-layer.md:343,349`; `packages/core/src/avkit_core/ports/models.py:15-20`; `packages/core/src/avkit_core/domain/tts.py:96-109` | Bind the frozen callback to the runtime observable and test start at 0, intermediate finite fractions, success, failure, and rejection/fail-closed behavior for invalid callback values. | open |
| 6 | High | High | **The TTS progress AC cannot be implemented from the frozen callback without inventing a mapping.** AC-12.5 requires persisted integer `segments_done/segments_total`, but `TTSPort.generate` exposes only a single fraction. Neither Phase 1 nor this plan defines how that fraction becomes two segment counts. Different implementations can satisfy the words with incompatible persisted values, so the FIC is not source-sufficient and violates PR-5. | `implementation-plan.md:394`; `docs/build-plan/03-service-layer.md:315-333`; `packages/core/src/avkit_core/ports/tts.py:21-27`; `packages/core/src/avkit_core/domain/tts.py:127-128` | Resolve the frozen-port mismatch with a source-backed or human-approved mapping and exact callback-to-row assertions; do not change the frozen Protocol during this session. | open |
| 7 | High | High | **`app.log_to_file` has no legal producer through the frozen filesystem port.** Phase 3 requires append semantics while also forbidding direct `open`; Phase 1 restricts `FilesystemPort.read_text` to transcript compile and provides no append method. The plan proposes `existing + line` or a private append helper without naming a contract-valid way to obtain/append existing content, and no AC covers the behavior. Execution therefore either violates the frozen port/direct-I/O rules or fails the required append behavior. | `implementation-plan.md:218,248-252`; `docs/build-plan/03-service-layer.md:60,372-387`; `packages/core/src/avkit_core/ports/filesystem.py:11-22`; `docs/build-plan/01-domain-layer.md:478-489` | Resolve the canonical ownership seam before coding and add an AC that proves append, redaction, restart/existing-file behavior, and absence of direct file I/O in services. | open |
| 8 | High | High | **The hexagonal-boundary scan row never runs the named core-infrastructure scan.** The plan defines `SCAN_CORE_INFRA_ARGS` and the task row claims both `SCAN_PLACEHOLDER` and `SCAN_CORE_INFRA`, but its validation command executes only the placeholder scan. It can pass with `avkit_infra`, SQLAlchemy, yt-dlp, Hugging Face, soundfile, ONNX Runtime, or Kokoro imports in core, directly false-passing the stated objective and violating PR-4/PR-8. | `implementation-plan.md:21,132,187,503-504`; `task.md:57` | Execute both named scans, save both exact receipts, and fail on any disallowed core import while preserving the expected rg exit-1-clean handling. | open |
| 9 | High | High | **The final closeout can pass with MEU state and structural artifacts unverified.** H2-2 says to mark four MEUs `approved`, but its validation checks reflection markers only and never renders/checks the changed SSOT. H2-4 claims to re-run handoff, per-MEU AC, review, reflection/metrics, and drift checks, yet its command checks only the execution-review file. Thus the complete task can validate with stale MEU rendering or missing final structural receipts, violating PR-4/PR-8 and the execution DONE contract. The known absence of `validate_closeout_artifacts.py` is not the finding; the incomplete substitute is. | `implementation-plan.md:509-510`; `task.md:72-74`; `.agent/docs/commands.md:16-20` | Make H2-2 render and check the approved SSOT, and make H2-4 actually re-run every named substitute: four handoffs, per-MEU AC sets, target-bound review, reflection markers/schema, metrics, and `meu_status.py render --check`. | open |
| 10 | Low | High | **Named predicates are still restated rather than referenced.** `DOWNLOAD_TRANSITIONS`, SABR state sets, and the MEU tuple are copied into locks, ACs, open questions, and task command bodies after being declared in the named-set table. No materially divergent spelling was found, so PR-9 makes this clerical and non-blocking. | `implementation-plan.md:5,101-104,190,194-196,296,305,312,510,520`; `task.md:4,58` | Keep one canonical named owner per set and refer to the name in prose/tests wherever an exact restatement is not required for an executable command. | open |

## Scope

**Targets**: `docs/execution/plans/2026-08-19-p3-services/implementation-plan.md`; `docs/execution/plans/2026-08-19-p3-services/task.md`  
**Review Type**: unstarted plan review, Round 1  
**Checklist Applied**: workflow PR-1 through PR-9, workflow DR-1 through DR-8, template IR/DR/PR, AV-1 through AV-6, C2/C3, referenced-artifact existence, control reachability/totality, repeated-literal census, Materiality Gate  
**Authority**: `docs/build-plan/03-service-layer.md`; frozen `packages/core/src/avkit_core/{ports,domain}`; Session 4 grouping; `meu-status.yaml`; Session 3 RULE-1/2/3 carry-forward  
**Out of scope**: plan corrections, product code/tests, REST/MCP/GUI work, adapter rewrites, product quality-gate execution

## Commands Executed

- Full line-numbered static reads of the workflow, both targets, Phase 3 spec, grouping lock, task/review templates, role contracts, architecture/testing canon, frozen ports/domain types, and the latest peer plan-review exemplar. Receipts are under `C:/Temp/av-kit/` (`workflow-lines.txt`, `plan-lines.txt`, `task-lines.txt`, `phase3-lines.txt`, `core-signatures.txt`, and related bounded-read receipts).
- `rg` control/source censuses for spaCy, transitions, required command names, callbacks, mutex use, scan predicates, named-set repetition, grouping, and MEU registrations. Key receipts: `spacy-sources.txt`, `transcript-transition-plan.txt`, `service-command-census.txt`, `scan-task-census.txt`, `named-repeat-census.txt`, `grouping-s4.txt`, `meu-phase3-4.txt`.
- Static `Test-Path` inventories: `path-state.txt` and `existence-more.txt`. `avkit_core/services/`, `TEST_SERVICES`, four MEU handoffs, and the canonical review were absent before this review; scheduled existing tools/templates and regression tests exist. `tools/validate_codebase.py` and `tools/validate_closeout_artifacts.py` are absent exactly as disclosed.
- No git command and no product pytest, pyright, ruff, build, or implementation command was run.

## Checklist Results

### Information Retrieval (IR)

| Check | Result | Evidence |
|-------|--------|----------|
| All AC have source labels | fail | Existing AC rows are labeled, but Findings 3 and 7 identify required Phase 3 behaviors with no AC; Findings 1 and 6 show labels that do not support the stated behavior. |
| Validation cells are exact commands | fail | Task 18 omits `SCAN_CORE_INFRA`; H2-4 does not execute the structural checks it claims. |
| BUILD_PLAN audit row present | pass | Task 19 binds MEU-13/10/11/12 and the hub next field. |
| Post-MEU rows present | pass | H1/H2 handoff, review, reflection, metrics, and commit-draft rows exist; Finding 9 blocks their final control integrity. |

### Design Review (DR — template)

| Check | Result | Evidence |
|-------|--------|----------|
| Naming convention followed | pass | Plan folder, four MEU handoff paths, and rolling implementation-review path follow the canonical names. |
| Template version present | pass | Plan `2.0`; task `2.1`. |
| YAML frontmatter well-formed | pass | Project, source, MEUs, status, and template fields are readable and aligned. |

### Post-Implementation Review (PR — template)

| Check | Result | Evidence |
|-------|--------|----------|
| Evidence bundle complete | n/a | Execution is unstarted. Future evidence controls were reviewed statically. |
| FAIL_TO_PASS table present | pass | Dedicated Red rows and receipt paths exist for all four MEUs. |
| Commands independently runnable | fail | Existing executables exist, but Findings 8-9 show materially incomplete command predicates. |
| Anti-placeholder scan clean | planned | Services do not exist yet; the planned scan covers services but not all touched domain files. |

### Workflow Plan Review (PR-1 through PR-9)

| Check | Result | Evidence |
|-------|--------|----------|
| PR-1 Plan/task alignment | pass | Both targets use MEU-13 -> MEU-10 -> MEU-11 -> MEU-12 and exclude MEU-14+. |
| PR-2 Not-started confirmation | pass | Services, `TEST_SERVICES`, MEU handoffs, and implementation review are absent; all executable task rows are unchecked. |
| PR-3 Task contract completeness | pass | Executable rows contain task, owner, deliverable, validation, dependencies, context strategy, durable outputs, and status. |
| PR-4 Validation realism | fail | Findings 3, 8, and 9 demonstrate materially missing contracts/false-pass gates. |
| PR-5 Source-backed planning | fail | Findings 1, 2, 6, and 7 conflict with or fail to resolve controlling local canon. |
| PR-6 Handoff/corrections readiness | pass | Four explicit MEU handoff paths and one rolling review path exist in the plan. Round-2 census gate is not applicable. |
| PR-7 Scope discipline / C2 | fail | All deferred MEU ids are registered, and the MEU-14 composition-root deferrals are valid; spaCy is incorrectly relabeled out of scope (Finding 1). |
| PR-8 Control reachability/totality | fail | Findings 2, 4-9 identify missing edges, producers, observables, or materially false-passing gates. `apply_lock`, `SEQ_OWNER`, Stop, NaN rejection, and fake-driven download progress are otherwise traceable. |
| PR-9 Single-statement discipline | fail (Low) | Repeated live named-set spellings remain without a divergent behavior (Finding 10). |

### Workflow Docs Review (DR-1 through DR-8)

| Check | Result | Evidence |
|-------|--------|----------|
| DR-1 Claim-to-state match | pass | Draft/unstarted claims match disk state. |
| DR-2 Residual old terms | fail | The `no spaCy`/`Phase 7 no extra ML` wording contradicts current canon. |
| DR-3 Downstream references updated | pass | Grouping, MEU registry, plan/task scope, and MEU-14+ deferrals align. |
| DR-4 Verification robustness | fail | Findings 3-9 identify required behavior or artifacts that can escape the planned checks. |
| DR-5 Evidence auditability | pass | Static commands and canonical receipts are reproducible; known-absent validators are explicitly disclosed. |
| DR-6 Cross-reference integrity | fail | spaCy and transcript transition contracts disagree with canonical build-plan clauses. |
| DR-7 Evidence freshness | pass | Targets and authority were reread from current disk state on 2026-08-19. |
| DR-8 Completion vs residual risk | pass | No implementation-complete claim is made. |

### Adversarial Verification (AV-1 through AV-6)

| Check | Result | Evidence |
|-------|--------|----------|
| AV-1 Failing-then-passing proof | planned | Red-before-Green rows exist, but Findings 3-7 identify missing/underspecified Red oracles. |
| AV-2 No bypass hacks | planned | G36 scan exists. |
| AV-3 Changed paths exercised by assertions | fail at plan level | Transcript recovery/retry edges, shared extract locking, model fraction, and log append lack complete assertions. |
| AV-4 No skipped/xfail masking | planned | Task 17 fails on skip/xfail calls in the named test files. |
| AV-5 No unresolved placeholders | planned | Task 18 scans the services tree; coverage of touched domain files remains a non-blocking residual gap. |
| AV-6 Source-backed criteria | fail | Findings 1, 6, and 7 require source-backed resolution before tests can be a complete specification. |

## Open Questions / Assumptions

- The frozen Phase 1 Protocols win, as directed. This review therefore does not propose editing port signatures to solve TTS progress or health log append.
- The MEU-14 composition-root deferral is accepted: fakes can prove the download hook/UoW path in this session, while MEU-14 binds the real adapter callbacks. That deferral is not a finding.
- A correction can follow the existing spaCy canon without a new product decision. A different chunker, a fraction-to-segment mapping, or a new health-log ownership seam requires a source-backed canonical amendment or explicit human decision.

## Out-of-Contract Observations

None.

## Follow-Up Actions

1. Run `/plan-corrections` against Findings 1-10; do not begin execution.
2. Repair the transcript graphs and add complete Red ACs for required service commands, shared extraction, model fraction, TTS progress mapping, and log append.
3. Restore the source-required spaCy contract unless the human explicitly changes the controlling canon.
4. Bind task 18 to both scans and replace H2-4 with the complete named substitute closeout gate, including approved-state render/check.
5. On Round 2, supply the required untruncated blast-radius census plus per-hit dispositions before content re-review.

## Residual Risk

The plan correctly preserves Session 3 RULE-1/2/3, keeps `DOWNLOAD_TRANSITIONS` as the single download graph, slices `playlist_end` in the service, avoids the bulk repository `reset_failed()` in prose, validates settings extra fields/dotted UI keys, and defers only real composition wiring to MEU-14. Those surfaces still require recheck after corrections because nearby edits can disturb them. This was a static plan review; runtime behavior remains unproven by design.

## Verdict

`changes_required` — nine evidence-backed High findings show that executing the plan can deliver the wrong text-preparation behavior, hit impossible or underspecified service contracts, omit required commands/controls, import infrastructure into core undetected, and complete with stale or structurally unverified closeout state. Corrections must proceed through `/plan-corrections`; this review does not modify the targets.

---

## Corrections Applied — 2026-08-19 19:05 (EDT)

Round-1 findings 1–9 addressed in plan/task only (no product code). Finding 10 (PR-9 restatement) remains clerical/non-blocking. Frontmatter `verdict` is `corrections_applied` — this agent does not set `approved`.

| # | Action |
|---|--------|
| 1 | Restored spaCy `SPACY_MODEL` + `CHUNK_DEPENDENCY_ERROR`; removed no-spaCy Out of Scope; NSIS model file deferred MEU-25; AC-12.2 rewritten |
| 2 | `TRANSCRIPT_PARENT_TRANSITIONS` includes `Processing→Pending`; `TRANSCRIPT_ITEM_TRANSITIONS` includes `Failed→Pending` |
| 3 | Added AC-10.15/10.16, AC-11.14, AC-12.10; bound on Red/Green task rows |
| 4 | Download mutex stays AC-10.11; cross-service oracle is AC-11.15 (MEU-11 owns `add_channel`) |
| 5 | AC-12.7 binds catalog `on_progress` to `ModelDownloadRuntime.fraction` |
| 6 | Locked `TTS_PROGRESS_RESOLUTION=1000`; AC-12.5 maps frozen float callback |
| 7 | Locked `LOG_FILE_APPEND_EXCEPTION`; AC-13.10 append/redact/restart |
| 8 | Task 18 Validation runs `SCAN_PLACEHOLDER` then `SCAN_CORE_INFRA` (`anti-infra-core.txt`); args include `avkit_infra` |
| 9 | H2-2 = `SSOT_APPROVED` + render + `--check` + reflection markers; H2-4 = full `CLOSEOUT_GATE`; H1-3 = `SSOT_READY` |

### Blast-radius census

Named untruncated receipts (only these; ignore leftover `C:/Temp/av-kit/census-*` files from Sessions 1–3):

- Index: `C:/Temp/av-kit/census-p3-r2-index.json`
- File:line extract: `C:/Temp/av-kit/census-p3-r2-disposition-src.txt`
- Old (expect 0 hits): `census-prepare-chunk-algo-old.txt`, `census-no-spacy-old.txt`, `census-no-spacy-cap-old.txt`, `census-phase7-no-ml-old.txt`, `census-existing-plus-line-old.txt`, `census-import-spacy-fail-old.txt`
- New: `census-spacy-model-new.txt`, `census-chunk-dep-err-new.txt`, `census-spacy-error-class-new.txt`, `census-tts-progress-res-new.txt`, `census-log-append-exc-new.txt`, `census-ac-10-15-new.txt`, `census-ac-10-16-new.txt`, `census-ac-11-14-new.txt`, `census-ac-11-15-new.txt`, `census-ac-12-10-new.txt`, `census-ac-13-10-new.txt`, `census-parent-pending-edge-new.txt`, `census-item-failed-pending-new.txt`, `census-ssot-approved-new.txt`, `census-closeout-gate-new.txt` (re-swept after §6 name add), `census-anti-infra-core-new.txt`, `census-scan-open-new.txt`, `census-required-dl-cmds-new.txt`, `census-required-tr-cmds-new.txt`, `census-write-text-atomic-left.txt`

`[rtk]` header lines are not plan/task hits.

### Per-hit dispositions (`file:line`)

| Receipt | file:line | Disposition |
|---------|-----------|-------------|
| census-prepare-chunk-algo-old | _(no plan/task hits)_ | confirmed-consistent — `PREPARE_CHUNK_ALGO` removed |
| census-no-spacy-old | _(no plan/task hits)_ | confirmed-consistent — `no spaCy` removed |
| census-no-spacy-cap-old | _(no plan/task hits)_ | confirmed-consistent — `No spaCy` removed |
| census-phase7-no-ml-old | _(no plan/task hits)_ | confirmed-consistent — `Phase 7 no extra ML` removed |
| census-existing-plus-line-old | _(no plan/task hits)_ | confirmed-consistent — rewrite-append proposal removed |
| census-import-spacy-fail-old | _(no plan/task hits)_ | confirmed-consistent — `import spacy in core` fail-oracle removed |
| census-spacy-model-new | task.md:53 | updated — prepare implement row |
| census-spacy-model-new | implementation-plan.md:114 | updated — named set |
| census-spacy-model-new | implementation-plan.md:220 | updated — Prepare lock |
| census-spacy-model-new | implementation-plan.md:404 | updated — AC-12.2 |
| census-spacy-model-new | implementation-plan.md:418 | updated — sufficiency |
| census-spacy-model-new | implementation-plan.md:429 | updated — prepare.py files-modified |
| census-spacy-model-new | implementation-plan.md:554 | updated — open-question option A |
| census-chunk-dep-err-new | task.md:53 | updated |
| census-chunk-dep-err-new | implementation-plan.md:115 | updated — named set |
| census-chunk-dep-err-new | implementation-plan.md:220 | updated — Prepare lock |
| census-chunk-dep-err-new | implementation-plan.md:404 | updated — AC-12.2 |
| census-chunk-dep-err-new | implementation-plan.md:418 | updated — sufficiency |
| census-chunk-dep-err-new | implementation-plan.md:427 | updated — errors.py |
| census-chunk-dep-err-new | implementation-plan.md:477 | updated — MEU-25 deferral basis |
| census-chunk-dep-err-new | implementation-plan.md:554 | updated — open question |
| census-spacy-error-class-new | implementation-plan.md:115 | updated — class alias |
| census-spacy-error-class-new | implementation-plan.md:427 | updated — files-modified |
| census-tts-progress-res-new | task.md:54 | updated — TTS Red row |
| census-tts-progress-res-new | implementation-plan.md:116 | updated — named set |
| census-tts-progress-res-new | implementation-plan.md:407 | updated — AC-12.5 |
| census-tts-progress-res-new | implementation-plan.md:451 | updated — control register |
| census-log-append-exc-new | task.md:43 | updated — Health Green row |
| census-log-append-exc-new | implementation-plan.md:117 | updated — named set |
| census-log-append-exc-new | implementation-plan.md:226 | updated — lock |
| census-log-append-exc-new | implementation-plan.md:261 | updated — AC-13.10 |
| census-log-append-exc-new | implementation-plan.md:406 | updated — AC-12.4 open() note |
| census-log-append-exc-new | implementation-plan.md:524 | updated — SCAN_OPEN verification |
| census-ac-10-15-new | task.md:44 | updated — Red queue row |
| census-ac-10-15-new | implementation-plan.md:316 | updated — AC table |
| census-ac-10-15-new | implementation-plan.md:449 | updated — control register |
| census-ac-10-16-new | implementation-plan.md:317 | updated — AC table |
| census-ac-11-14-new | task.md:48 | updated — Red transcript row |
| census-ac-11-14-new | implementation-plan.md:367 | updated — AC table |
| census-ac-11-15-new | task.md:49 | updated — Green transcript row |
| census-ac-11-15-new | implementation-plan.md:312 | updated — AC-10.11 pointer |
| census-ac-11-15-new | implementation-plan.md:368 | updated — AC table |
| census-ac-11-15-new | implementation-plan.md:446 | updated — control register |
| census-ac-12-10-new | implementation-plan.md:412 | updated — AC table |
| census-ac-13-10-new | implementation-plan.md:261 | updated — AC table |
| census-ac-13-10-new | implementation-plan.md:448 | updated — control register |
| census-parent-pending-edge-new | implementation-plan.md:102 | updated — parent graph |
| census-item-failed-pending-new | implementation-plan.md:101 | confirmed-consistent — pre-existing download `Failed→{Pending}` |
| census-item-failed-pending-new | implementation-plan.md:102 | updated — parent `Failed→{Pending}` plus Processing→Pending |
| census-item-failed-pending-new | implementation-plan.md:103 | updated — item `Failed→{Pending}` |
| census-ssot-approved-new | implementation-plan.md:542 | updated — verification §6 |
| census-ssot-approved-new | task.md:72 | updated — H2-2 command |
| census-closeout-gate-new | implementation-plan.md:542 | updated — verification §6 name |
| census-closeout-gate-new | task.md:74 | updated — H2-4 `CLOSEOUT_GATE` |
| census-anti-infra-core-new | implementation-plan.md:531 | updated — SCAN_CORE_INFRA receipt |
| census-anti-infra-core-new | task.md:57 | updated — task 18 both scans |
| census-scan-open-new | implementation-plan.md:140 | updated — named args |
| census-scan-open-new | implementation-plan.md:524 | updated — verification §4 |
| census-required-dl-cmds-new | task.md:45 | updated — Green download commands |
| census-required-dl-cmds-new | implementation-plan.md:118 | updated — named set |
| census-required-dl-cmds-new | implementation-plan.md:317 | updated — AC-10.16 |
| census-required-tr-cmds-new | implementation-plan.md:119 | updated — named set |
| census-required-tr-cmds-new | implementation-plan.md:367 | updated — AC-11.14 |
| census-write-text-atomic-left | implementation-plan.md:359 | confirmed-consistent — compile `write_text_atomic` only (not console.log) |

Companion (range tokens, not exact `-F` hits): `task.md:42` `AC-13.5–13.10` covers AC-13.10; `task.md:44`/`45` `AC-10.15–10.16` covers AC-10.16; `task.md:54` `AC-12.3–12.10` covers AC-12.10.

Blast-radius census: K=26 named receipts, V= old no-spaCy/PREPARE_CHUNK/Phase-7-ML/existing+line plus new spaCy/error/progress/log/AC/transition/SSOT/CLOSEOUT/scan/command names. N hits listed above; each has `updated` or `confirmed-consistent`. Six old-pattern receipts are zero-hit and explicitly dispositioned.

🕐 2026-08-19 19:05 (EDT)

---

## Round 2 Review — 2026-08-19

### Findings

No blocking findings. Round-1 Findings 1–9 are fixed on current disk state, and no new evidence-backed High/Critical defect was found under PR-1 through PR-9, C2/C3, or the Materiality Gate.

### Intent Anchor

Executing this plan is supposed to produce MEU-13, MEU-10, MEU-11, and MEU-12 as TDD-backed application services under `avkit_core/services/`, in that order, using the frozen Phase 1 Protocol surface and existing UoW path without REST, MCP, GUI, adapter, or UoW rewrites. The corrected plan is now sufficient to deliver that objective: its 51 source-labeled ACs, Red/Green task ranges, control chains, registered deferrals, and closeout gates cover the Phase 3 service contract without pulling MEU-14+ into execution.

### Non-Blocking Correction Notes

- **Low — PR-9 carry-forward:** `DOWNLOAD_TRANSITIONS`, transcript transition names, `TTS_PROGRESS_RESOLUTION`, and the Session 4 MEU tuple still appear at multiple prose/task sites. The spellings are consistent and the named-set table remains canonical, so this is clerical and does not block approval.
- **Low — PR-6 derived metadata:** `census-p3-r2-index.json` and `census-p3-r2-disposition-src.txt` retain `hit_count: 1` / one extracted location for `CLOSEOUT_GATE`, while the authoritative named raw receipt `census-closeout-gate-new.txt` contains the two current hits (`implementation-plan.md:542`, `task.md:74`) and the correction log dispositions both at lines 232–233. The raw receipt is untruncated and fully dispositioned; the stale derived count/extract is clerical.

### Round-1 Finding Recheck

| Finding | Prior Status | Round 2 Result | Evidence |
|---------|--------------|----------------|----------|
| F1 spaCy contract/degrade path | open High | ✅ Fixed | `implementation-plan.md:114-117,220,404,418,427-429,477,554`; `task.md:53-54` |
| F2 transcript recovery/retry edges | open High | ✅ Fixed | `implementation-plan.md:101-103,197,357-365`; all writes remain bound to entity `transition()` |
| F3 missing required service commands | open High | ✅ Fixed | `implementation-plan.md:316-317,367,412`; `task.md:44-55` |
| F4 shared cross-service extract mutex | open High | ✅ Fixed | `implementation-plan.md:312,368,446`; `task.md:49` |
| F5 model-download fraction producer | open High | ✅ Fixed | `implementation-plan.md:409,452`; `task.md:54` |
| F6 frozen-float TTS progress mapping | open High | ✅ Fixed | `implementation-plan.md:116,407,451`; `task.md:54` |
| F7 append/redact/restart control | open High | ✅ Fixed | `implementation-plan.md:117,226,261,448,524-535`; `task.md:43,57` |
| F8 missing core-infrastructure scan | open High | ✅ Fixed | `implementation-plan.md:531`; `task.md:57` runs both named scans and includes `avkit_infra` |
| F9 incomplete approved-state/closeout gates | open High | ✅ Fixed | `implementation-plan.md:542`; `task.md:72,74` prove `SSOT_APPROVED`, reflection markers, four handoffs, per-MEU ACs, independent review, metrics, and `render --check` |
| F10 repeated named predicates | open Low | Non-blocking carry-forward | `plan-r2-pr9-census-v2.txt`; no divergent live spelling found |

### Scope

**Targets**: `docs/execution/plans/2026-08-19-p3-services/implementation-plan.md`; `docs/execution/plans/2026-08-19-p3-services/task.md`  
**Review Type**: unstarted plan review, Round 2  
**Checklist Applied**: PR-1 through PR-9, DR-1 through DR-8, C2/C3, PR-6 blast-radius census, referenced-artifact existence, control reachability/totality, repeated-literal census, Materiality Gate  
**Authority**: `docs/build-plan/03-service-layer.md`; frozen `packages/core/src/avkit_core/{ports,domain}` state; Session 4 grouping; `meu-status.yaml`; Session 3 RULE-1/2/3 carry-forward  
**Out of scope**: corrections, product code/tests, REST/MCP/GUI, adapter/UoW rewrites, product quality-gate execution

### Commands Executed

- Exact line-numbered reads of the workflow, review template, both targets, Phase 3 authority, grouping/registry evidence, frozen Protocol/domain surfaces, prior review/correction log, and repository governance files. Current-review receipts use the `plan-r2-*` prefix under `C:/Temp/av-kit/`.
- PR-6 audit of all 26 named raw census receipts against current plan/task literal hit sets and correction-log dispositions. Six old-pattern receipts have zero hits; every current raw `file:line` has `updated` or `confirmed-consistent` disposition.
- Static readiness and existence checks: `services_exists=false`, zero MEU execution handoffs, 31 unchecked task rows, zero checked rows; all material gate executables/templates/regression tests exist; planned services, `TEST_SERVICES`, handoffs, review, and reflection are scheduled outputs.
- Static structural audit: 31/31 task rows contain task/owner/deliverable/validation/status; 51 unique AC definitions have source labels (MEU-13: 10, MEU-10: 16, MEU-11: 15, MEU-12: 10); all referenced MEU IDs exist in `meu-status.yaml`.
- Help/version only: `uv 0.9.5`, `pytest 9.1.1`, `pyright 1.1.411`, `ruff 0.16.3`; `check_exec_review.py` accepts the planned target/mode/round flags; `meu_status.py update` supports `--plan` and `render` supports `--check`.
- No git command, product pytest, pyright, ruff, build, or implementation command was run.

### Checklist Results

#### Workflow Plan Review (PR-1 through PR-9)

| Check | Result | Evidence |
|-------|--------|----------|
| PR-1 Plan/task alignment | pass | Both frontmatters and task dependencies use MEU-13 → MEU-10 → MEU-11 → MEU-12. |
| PR-2 Not-started confirmation | pass | `avkit_core/services/` absent; zero MEU handoffs; all 31 task rows `[ ]`. |
| PR-3 Task contract completeness | pass | Static unescaped-pipe audit found 31 rows and zero missing required fields. |
| PR-4 Validation realism | pass | Planned command surfaces exist or are explicit scheduled outputs; both known-absent validators are replaced by named runnable receipts. |
| PR-5 Source-backed planning | pass | All 51 AC definitions carry a Spec/Local Canon/Research-backed/Human-approved source basis. |
| PR-6 Handoff/corrections readiness | pass | Four explicit MEU handoffs; one rolling implementation review; all 26 named raw census receipts are complete and every raw hit is dispositioned. |
| PR-7 Scope discipline / C2 | pass | Every deferred MEU is registered; out-of-scope rows cite controlling canon; MEU-14/25 deferrals retain their in-scope service/degrade halves. |
| PR-8 Control reachability/totality | pass | Corrected graphs, shared coordinator, callback producers, log append chain, both scans, and full closeout gate each name observable, production chain, and negative oracle. |
| PR-9 Single-statement discipline | pass with Low note | Repetition remains consistent; named-set owners are unambiguous. |

#### Docs Review (DR-1 through DR-8)

| Check | Result | Evidence |
|-------|--------|----------|
| DR-1 Claim-to-state match | pass | Correction claims match current plan/task lines and named raw receipts. |
| DR-2 Residual old terms | pass | Six old-pattern PR-6 receipts have zero plan/task hits. |
| DR-3 Downstream references updated | pass | Grouping and registry preserve Session 4 and register every cited deferral. |
| DR-4 Verification robustness | pass | Round-1 materially false-passing scan/closeout gates are now executable and complete for their stated deliverables. |
| DR-5 Evidence auditability | pass | Exact receipts, current line references, path checks, and help/version receipts are reproducible. |
| DR-6 Cross-reference integrity | pass | Phase 3, GUI/distribution spaCy references, frozen Protocols, and MEU-14 composition deferrals align. |
| DR-7 Evidence freshness | pass | Targets, authority, census, and disk readiness were reread on 2026-08-19 for Round 2. |
| DR-8 Completion vs residual risk | pass | The plan remains unstarted and makes no implementation-complete claim. |

### C2/C3 Results

- **C2 deferral integrity:** pass. No contract work is disguised as unscheduled out-of-scope work; every `deferred` row points to a registered MEU and every true `out-of-scope` row cites a source that omits/forbids/deferred it.
- **C3 AC coverage:** pass. All 51 AC definitions map to the MEU-specific Red/Green task ranges; integration ACs are included in the scoped services/domain plus tmp-SQLite validation path.

### Open Questions / Assumptions

None blocking. The frozen Protocols remain authoritative; MEU-14 owns real adapter callback/lifespan composition; MEU-25 owns NSIS model bundling while the Phase 3 missing-model degrade path is in scope.

### Follow-Up Actions

No plan correction is required. This review is review-only and does not begin execution, modify plan files, or touch product/test code.

### Residual Risk

This is static plan evidence, not runtime proof. Implementation must still preserve frozen Protocol signatures, produce the required FAIL_TO_PASS receipts, execute the named MEU gates, and obtain an independent implementation-review `approved` verdict. The two Low notes above do not make the execution contract ambiguous and do not create a materially false-passing gate.

### Verdict

`approved` — the PR-6 procedural gate passes on the authoritative raw receipts and correction log, Round-1 Findings 1–9 are fixed, and no evidence-backed High/Critical finding remains. Executing the corrected plan should deliver the intended Phase 3 services without pulling REST, MCP, GUI, adapters, UoW rewrites, or MEU-14+ work into this session.
