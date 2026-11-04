---
date: "2026-08-19"
review_mode: "plan"
target_plan: "docs/execution/plans/2026-08-19-p2-external-adapters/implementation-plan.md"
verdict: "approved"
findings_count: 0
template_version: "2.1"
requested_verbosity: "standard"
agent: "GPT-5.6-sol (Codex)"
review_round: 4
---

# Critical Review: p2-external-adapters

> **Review Mode**: `plan`
> **Verdict**: `changes_required`
> **Round**: 1

---

## Intent Anchor

Executing this plan is supposed to deliver the Session 3 implementations of frozen `YouTubePort`, `TranscriptPort`, `TTSPort`, and `ModelCatalogPort` for MEU-6, MEU-7, and MEU-9, with mocked external-library tests and independently reviewed closeout evidence. As written, it would not reliably deliver that objective because the TTS contract leaves the three seeded ONNX variants without an inference path and the review/closeout controls can materially false-pass.

## Findings

| # | Severity | Confidence | Finding | File:Line | Recommendation | Status |
|---|----------|------------|---------|-----------|----------------|--------|
| 1 | High | High | **MEU-9 has no executable ONNX load/generate contract.** The plan seeds one PyTorch plus three ONNX variants, but its only inference dependency and mock surface is `kokoro.KPipeline`; AC-9.4 tests device choice and a missing file, not format dispatch or successful generation for each seeded format. Upstream `KPipeline` constructs a PyTorch `KModel`; it is not an ONNX loader. Thus all listed ACs can pass while `TTSPort.load_model` cannot load three of four catalog variants, violating PR-4/PR-5/PR-8 and `02-infrastructure.md` lines 208–213, 406. | `implementation-plan.md:21,98,187,322-329,351`; `packages/core/src/avkit_core/ports/tts.py:17`; [upstream KPipeline](https://github.com/hexgrad/kokoro/blob/main/kokoro/pipeline.py); [upstream KModel](https://github.com/hexgrad/kokoro/blob/main/kokoro/model.py) | Define a source-backed PyTorch/ONNX engine split, required dependencies/providers, per-format load observables, and positive/negative tests for every `SEED_VARIANT_IDS` member. Preserve the frozen port; do not narrow it to PyTorch implicitly. | open |
| 2 | High | High | **`sideload()` cannot construct the frozen return type from the planned mapping.** The lock maps filenames only to an id/path/downloaded flag, while `ModelVariant` also requires `name`, `format`, `precision`, and `size_bytes`. Those values currently exist in the Session 2 seed catalog, but the plan neither defines a canonical adapter-owned catalog nor a parity oracle; a coder must invent values or couple the adapter to database internals. This violates PR-4/PR-5 and the spec-sufficiency gate. | `implementation-plan.md:98,192,315-316,331`; `packages/core/src/avkit_core/domain/tts.py:161-179`; `packages/infrastructure/src/avkit_infra/database/engine.py:23-28` | Add one canonical `ModelVariant` metadata map, define on-disk `size_bytes` behavior, and test exact parity with the four seeded rows without importing/opening the database adapter. | open |
| 3 | High | High | **The independent-review approval gate accepts a stale earlier approval.** H1-7 uses `Select-String ... 'verdict: approved' -Quiet`, so a rolling file containing an old `approved` followed by a current `changes_required` passes. It also does not bind `review_mode`, `target_plan`, latest round, or `findings_count`. The synthetic receipt `C:/Temp/av-kit/review-falsepass-review.txt` reproduced `latest verdict: changes_required` with predicate `True`. This violates the independent-review hard gate and PR-8. | `task.md:65` | Replace the any-match grep with a target-bound parser/state receipt that validates the latest round, expected execution review mode/plan, round cap, verdict, and findings consistency. | open |
| 4 | High | High | **The final closeout/SSOT control can pass with materially missing artifacts and stale rendered state.** H2-4 checks only for any `verdict: approved`; it does not recheck the three handoffs, AC coverage, reflection markers/schema, metrics row, or MEU render drift. H2-2 changes YAML to `approved`, but `meu_status.py update` only saves YAML and the plan never renders/checks after that transition. `C:/Temp/av-kit/review-falsepass-closeout.txt` reproduced the H2-4 predicate passing with handoff, reflection, and metrics all absent. This violates PR-4/PR-8 and DR-4/DR-6/DR-8. | `task.md:68,70`; `tools/meu_status.py:129-156`; `implementation-plan.md:470-473` | After the approved status updates, run `meu_status.py render` then `render --check`; make H2-4 re-run every named handoff, AC, reflection, metrics, target-bound review, and drift receipt it claims to aggregate. | open |
| 5 | High | High | **The per-MEU evidence gate is aggregate and can false-pass two incomplete handoffs.** H1-6 checks only generic markers per file; H1-6a unions all AC ids across the glob. One handoff can contain every AC while the other two contain marker-only shells, yet both gates pass even though the plan requires one complete evidence handoff per MEU. This is a demonstrated predicate-shape path to materially missing deliverables under PR-4/PR-8. | `task.md:62-63`; `implementation-plan.md:40-48,450-453` | Bind AC-6.* to the MEU-6 handoff, AC-7.* to MEU-7, and AC-9.* to MEU-9; require each file's own changed-files, commands, and FAIL_TO_PASS evidence rather than aggregate presence. | open |
| 6 | Low | High | **`TooManyRequests` is a stale/nonexistent upstream exception name.** The allowed `youtube-transcript-api>=1.0` range currently exposes `RequestBlocked` and `IpBlocked`, not a `TooManyRequests` class. Because the plan also names HTTP 429-class handling, the intended correction is inferable and clerical under the Materiality Gate, but leaving the name invites a fake test double or collection failure. | `implementation-plan.md:182,283`; [upstream errors](https://github.com/jdepoix/youtube-transcript-api/blob/master/youtube_transcript_api/_errors.py) | Remove the nonexistent class name and specify the actual upstream exception/status chain used for 429, with a test built from a real supported exception shape. | open |
| 7 | Low | High | **The concrete TTS adapter name is inconsistent.** The canonical build plan says `KokoroAdapter`, while production-entrypoint prose says `TTSAdapter` and the file inventory says `TTSAdapter / KokoroAdapter`. This is clerical but can split imports/tests. | `implementation-plan.md:198,354`; `docs/build-plan/02-infrastructure.md:38` | Choose canonical `KokoroAdapter` (or explicitly source a deliberate alias) and use it in ACs, tests, and entrypoint prose. | open |
| 8 | Low | High | **Named predicates are still restated in multiple live command bodies.** The MEU tuple/status and scan/approval predicates are copied across plan and task commands despite the PR-9 named-set section; later edits can drift. This is clerical because the current intended spelling is inferable. | `implementation-plan.md:75-120,461,467,473`; `task.md:52,54,59,65,68,70,93` | Put each executable predicate in one named helper/receipt owner and have task rows invoke it; keep exact commands without duplicating the predicate body. | open |

## Scope

**Target**: `docs/execution/plans/2026-08-19-p2-external-adapters/implementation-plan.md`; `docs/execution/plans/2026-08-19-p2-external-adapters/task.md`  
**Review Type**: plan review, Round 1  
**Checklist Applied**: workflow PR-1–PR-9, workflow DR-1–DR-8, template IR/DR/PR, referenced-artifact existence, repeated-literal census, SSOT/control reachability  
**Canonical authority sampled**: frozen `packages/core/src/avkit_core/ports/{youtube,transcript,tts,models}.py`; domain DTOs/errors; `docs/build-plan/02-infrastructure.md`; Session 3 grouping; `meu-status.yaml`; Session 2 RULE-1–3  
**Out of scope**: implementation fixes, product tests, product code, plan/task edits, other handoffs

## Commands Executed

- `rtk proxy rg -n "^" <target>` for both plan files → `C:/Temp/av-kit/p2-plan-numbered.txt`, `C:/Temp/av-kit/p2-task-numbered.txt`.
- `rtk proxy rg -n "^" packages/core/src/avkit_core/ports/{youtube,transcript,tts,models}.py` and targeted domain/spec/grouping/status sweeps → `C:/Temp/av-kit/review-ports-*.txt`, `review-domain-*.txt`, `review-build-plan.txt`, `review-grouping.txt`, `review-meu-status.txt`.
- `rtk proxy pwsh ... Test-Path ...` for not-started state and referenced artifacts → `C:/Temp/av-kit/review-not-started.txt`, `review-artifact-existence.txt`. Planned adapter/tests/handoffs are absent; required existing tools/templates/ports exist; the plan correctly identifies `tools/validate_closeout_artifacts.py` and `packages/api/` as absent.
- `rtk proxy pwsh ... Select-String ...` synthetic latest-verdict probe → `C:/Temp/av-kit/review-falsepass-review.txt` (`changes_required` latest, predicate `True`).
- `rtk proxy pwsh ...` synthetic missing-closeout probe → `C:/Temp/av-kit/review-falsepass-closeout.txt` (all three artifacts absent, predicate `True`).
- Exact baseline scans → `C:/Temp/av-kit/review-scan-baseline-summary.txt`: placeholder, soundfile, and core-infra scans are clean. The archive scan reports the planned `youtube/` path absent before implementation, which is expected and inventoried.
- `SCAN_ADAPTER_LIBS` filter probe → `C:/Temp/av-kit/review-scan-logic.txt`: allowed `yt_dlp` under `youtube/` is excluded from violations; the same import under `transcript/` remains a hit. The requested SCAN_SOUNDFILE split is therefore correctly expressed.
- `rtk proxy rg -n -F ... <plan-folder>` repeated-literal census → `C:/Temp/av-kit/review-repeated-literals.txt`.
- `rtk proxy git status --short` → `C:/Temp/av-kit/review-git-status.txt`, confirming the supplied repository is not a git work tree; no diff claim was used.

## Checklist Results

### Information Retrieval (IR)

| Check | Result | Evidence |
|-------|--------|----------|
| All AC have source labels | pass | Every written AC row has a source; Findings 1–2 identify required behaviors for which ACs are missing. |
| Validation cells are exact commands | fail | H1-7 and H2-4 are exact syntax but materially false-pass; row 14 relies on extra prose-linked commands. |
| BUILD_PLAN audit row present | pass | Task 15 and H1-3 exist; approved-state render/check is missing (Finding 4). |
| Post-MEU rows present (handoff, reflection, metrics) | pass | H1/H2 rows exist, but Findings 3–5 block their control integrity. |

### Design Review (DR — template)

| Check | Result | Evidence |
|-------|--------|----------|
| Naming convention followed | fail | `KokoroAdapter` / `TTSAdapter` drift (Finding 7). |
| Template version present | pass | Plan `2.0`; task `2.1`; both frontmatters present. |
| YAML frontmatter well-formed | pass | Required project/source/MEU/status keys are readable and aligned. |

### Post-Implementation Review (PR — template)

| Check | Result | Evidence |
|-------|--------|----------|
| Evidence bundle complete | n/a | Plan is confirmed unstarted; future evidence controls are reviewed under workflow PR-4/PR-8. |
| FAIL_TO_PASS table present | pass | Red-phase rows and named receipt paths exist for all three MEUs. |
| Commands independently runnable | fail | Approval/closeout predicates are runnable but do not prove their claimed deliverables; `TooManyRequests` is not an upstream class. |
| Anti-placeholder scan clean | pass | Current baseline is clean; planned new trees do not exist yet. |

### Workflow Plan Review (PR-1–PR-9)

| Check | Result | Evidence |
|-------|--------|----------|
| PR-1 Plan/task alignment | pass | Same MEU-6 → MEU-7 → MEU-9 scope and order. |
| PR-2 Not-started confirmation | pass | All planned source/test/handoff paths absent; all task rows unchecked. |
| PR-3 Task contract completeness | pass | Rows have task, owner, deliverable, validation, dependency/context, and status columns. |
| PR-4 Validation realism | fail | Findings 1–5 show missing coverage and concrete false-pass controls. |
| PR-5 Source-backed planning | fail | ONNX execution and sideload metadata are unresolved despite frozen/canonical types. |
| PR-6 Handoff/corrections readiness | fail | Three paths are explicit, but their aggregate AC oracle does not prove per-MEU completeness. Round-2 census gate is not applicable yet. |
| PR-7 Scope discipline (C2) | pass | Deferred MEU-10–23 ids exist in SSOT/grouping; out-of-scope rows cite real local/spec bases. No invented MEU id found. |
| PR-8 Control reachability/totality | fail | Findings 1, 3, 4, and 5 demonstrate dead/unbound or vacuous controls. |
| PR-9 Single-statement discipline | fail | Repeated live predicate bodies remain (Finding 8, Low). |

### Workflow Docs Review (DR-1–DR-8)

| Check | Result | Evidence |
|-------|--------|----------|
| DR-1 Claim-to-state match | pass | Draft/unstarted claims match file state. |
| DR-2 Residual old terms | fail | Stale `TooManyRequests` and adapter-name variants remain (Findings 6–7, Low). |
| DR-3 Downstream references updated | pass | Session 3 grouping/current-focus/MEU ids align; execution-time hub changes are planned. |
| DR-4 Verification robustness | fail | Findings 3–5 demonstrate regressions/missing artifacts the checks would miss. |
| DR-5 Evidence auditability | pass | Commands and C:/Temp receipts are reproducible; false-pass receipts are named above. |
| DR-6 Cross-reference integrity | fail | Approved YAML can drift from rendered registry/BUILD_PLAN (Finding 4). |
| DR-7 Evidence freshness | pass | Review probes were executed 2026-08-19; no stale handoff claim was relied upon. |
| DR-8 Completion vs residual risk | pass | The artifacts remain `draft`; no implementation-complete claim is made. |

## Open Questions / Assumptions

- No human product decision is required to correct this round: the frozen ports and canonical four-variant catalog already decide the scope.
- The upstream findings are relevant to the plan's unbounded dependency floors (`youtube-transcript-api>=1.0` and unpinned `kokoro`). If the correction pins different APIs, it must cite and test those exact versions.
- `tools/validate_closeout_artifacts.py` is genuinely absent and is not itself a finding; the blocking issue is that the replacement predicates do not provide equivalent target binding or structural coverage.

## Out-of-Contract Observations

None.

## Follow-Up Actions

1. Run `/plan-corrections` against Findings 1–8; do not begin implementation.
2. Add source-backed, format-total MEU-9 contracts and tests for PyTorch and every ONNX seed.
3. Define canonical sideload metadata compatible with the frozen `ModelVariant` constructor and Session 2 seed catalog.
4. Replace the H1-7, H1-6/H1-6a, H2-2, and H2-4 false-pass predicates with latest-round/target-bound and per-artifact/per-MEU oracles.
5. Remove the stale transcript exception name, canonicalize the adapter class name, and consolidate repeated predicates.

## Residual Risk

YouTube selector/cookie/SABR boundaries, the SCAN_SOUNDFILE split, allowed `yt_dlp` placement under `youtube/`, and the Session 3 grouping lock are well represented. They must be rechecked after corrections because the required blast-radius census is a Round-2 pre-verdict gate.

## Verdict

`changes_required` — five evidence-backed High findings show that executing the plan can leave required MEU-9 variants unusable and can cross the independent-review/closeout gates with stale or missing evidence. Corrections must proceed through `/plan-corrections`; this review does not modify the targets.

---

## Corrections Applied — 2026-08-19 11:51 (EDT)

Orchestrator `/plan-corrections` Round 1. **This agent does not set `approved`.** Frontmatter `verdict` is `corrections_applied` pending independent Round 2.

### Plan summary

Session 3 remains MEU-6 + MEU-7 + MEU-9. Frozen ports unchanged. Added source-backed ONNX engine split, adapter-owned `CATALOG_METADATA`, and non-false-pass closeout predicates.

### Changes

| Finding | Status | Change |
|---------|--------|--------|
| 1 High ONNX load/generate | updated | Named `ENGINE_BY_FORMAT`, `ONNX_RUNTIME_DEP`, `ONNX_PROVIDERS_AUTO`. AC-9.4/9.6 require per-`SEED_VARIANT_IDS` mocked `InferenceSession` + `session.run`. Class `KokoroAdapter`. |
| 2 High sideload DTO | updated | `CATALOG_METADATA` four-row map + `model_manager/catalog.py`; `size_bytes` from `stat()`; no DB import (AC-9.10). |
| 3 High stale `verdict: approved` | updated | `LATEST_EXEC_VERDICT`: last `^verdict:` / `^review_mode:` lines; reject `plan` mode and `changes_required`. |
| 4 High H2-4/SSOT render | updated | `SSOT_APPROVED` chains `render` + `render --check`. `CLOSEOUT_GATE` re-runs handoffs, per-MEU ACs, latest verdict, reflection/metrics, drift check. |
| 5 High aggregate AC union | updated | `PER_MEU_HANDOFF_AC` binds AC-6.* / AC-7.* / AC-9.* to the matching handoff file. |
| 6 Low `TooManyRequests` | updated | `RETRYABLE_TRANSCRIPT_ERRORS` = `RequestBlocked`, `IpBlocked` only. Remaining `TooManyRequests` strings are explicit “do not use” notes. |
| 7 Low adapter name | updated | Canonical `KokoroAdapter`. Remaining `TTSAdapter` is a negative oracle in AC-9.1. |
| 8 Low predicate duplication | confirmed-consistent | TASK-TEMPLATE still requires exact validation commands; named receipts in Verification Plan §6/§7 are the owners. Task rows copy those receipts rather than a weaker grep. |

### Blast-radius census

K=7 values, receipts under `C:/Temp/av-kit/census-*-old.txt` (this round): `too-many-requests`, `tts-adapter-class`, `ac-union`, `stale-verdict-grep`, `engine-split`, `catalog-metadata`, `onnxruntime`.

- `PASS: complete AC set` / any-match `verdict: approved` Quiet grep: **old absent** (good).
- `ENGINE_BY_FORMAT` / `CATALOG_METADATA` / `onnxruntime`: **new present** at named-set, AC, task, and scan sites.
- `TooManyRequests` / `TTSAdapter`: **confirmed-consistent** as prohibition/negative-oracle wording only.

Cross-doc sweep: plan + task only (allowed correction writes). No product code.

### Verification

Static `rg` census only. Product pytest not run (SIGN 1 — plan not independently `approved`).

🕐 2026-08-19 11:51 (EDT)

---

## Recheck — Round 2 (2026-08-19)

**Workflow**: `/plan-critical-review` Round 2  
**Agent**: GPT-5.6-sol (Codex), independent reviewer

### Intent Anchor

Executing this plan is intended to deliver the Session 3 MEU-6, MEU-7, and MEU-9 external adapters behind the frozen core ports, including format-total Kokoro/ONNX model handling and independently enforced evidence closeout. Whether the corrected plan would deliver that objective was not evaluated this round because the mandatory PR-6 correction-census precondition failed first.

### PR-6 Correction-Census Pre-Verdict Gate

`fail` — the correction census is undispositioned. The correction log cites only the wildcard `C:/Temp/av-kit/census-*-old.txt` and summarizes categories/counts (`:162-170`), but it does not assign `updated` or `confirmed-consistent` to each raw census `file:line` hit. The exact audit receipt `C:/Temp/av-kit/round2-pr6-audit.txt` reports `RAW_RECEIPT_REFS=1` and `PER_HIT_DISPOSITION_LINES=0`; `C:/Temp/av-kit/round2-census-raw-selected.txt` confirms that the named raw receipts contain multiple concrete plan/task hits requiring individual disposition.

Per PR-6 and the Verdict Rule's sole procedural exception, this is a pre-verdict gate rather than a severity-rated finding. Round 2 therefore stops before corrected-content review: Findings 1–8, including High Findings 1–5 (`ENGINE_BY_FORMAT`/ONNX ACs, `CATALOG_METADATA`, `LATEST_EXEC_VERDICT`, `CLOSEOUT_GATE`/SSOT render, and `PER_MEU_HANDOFF_AC`), remain **not rechecked this round**, and their false-pass predicates were not probed.

### Commands Executed

- `rtk proxy pwsh ... Get-ChildItem C:/Temp/av-kit/census-*.txt` → `C:/Temp/av-kit/round2-census-inventory.txt` (receipt inventory and line counts).
- Full reads of the seven correction-named raw receipts → `C:/Temp/av-kit/round2-census-raw-selected.txt` (untruncated selected receipt content).
- Correction-section audit for explicit receipt references and per-hit dispositions → `C:/Temp/av-kit/round2-pr6-audit.txt` (`RAW_RECEIPT_REFS=1`; `PER_HIT_DISPOSITION_LINES=0`).
- Canonical-path pre-edit guard → `C:/Temp/av-kit/round2-pre-edit-guard.txt` (pass).

### Findings

No severity-rated findings were assessed. `findings_count: 0` records the workflow-defined PR-6 procedural exception, not approval of any Round 1 finding.

### Checklist Results

| Check | Result | Evidence |
|-------|--------|----------|
| PR-6 Handoff/corrections readiness | fail | Raw census hits lack the required per-hit `updated` / `confirmed-consistent` correction-log dispositions. |
| PR-1–PR-5, PR-7–PR-9 | not evaluated | PR-6 requires stopping before corrected-content review. |
| DR-1–DR-8 | not evaluated | PR-6 requires stopping before corrected-content review. |

### Open Questions / Assumptions

None. The missing per-hit dispositions are directly reproducible from the rolling handoff and named receipts.

### Follow-Up Action

Run `/plan-corrections` Step 5c again and append an auditable correction log that names the raw old/new census receipts and assigns every receipt `file:line` hit either `updated` or `confirmed-consistent`. Then submit Round 3 for the substantive recheck and requested false-pass probes.

### Residual Risk

All eight Round 1 findings remain substantively unverified in Round 2. No inference should be drawn from the correction summaries until the PR-6 evidence chain is complete.

### Verdict

`changes_required` — PR-6's correction-census pre-verdict gate failed because the raw hits have no per-hit dispositions in the correction log. This is the workflow's procedural exception to the normal High/Critical blocking threshold.

---

## Corrections Applied — PR-6 per-hit census — 2026-08-19 11:58 (EDT)

Step 5c resubmission for Round 3. Named receipts (untruncated):

- Old: `C:/Temp/av-kit/census-too-many-requests-old.txt`, `census-tts-adapter-class-old.txt`, `census-ac-union-old.txt`, `census-stale-verdict-grep-old.txt`, `census-engine-split-old.txt`, `census-catalog-metadata-old.txt`, `census-onnxruntime-old.txt`
- New: `C:/Temp/av-kit/census-per-meu-ac-new.txt`, `census-latest-verdict-new.txt`, `census-closeout-gate-new.txt`, `census-kokoro-adapter-new.txt`, `census-scan-core-new.txt`
- Round-2 auditor copy: `C:/Temp/av-kit/round2-census-raw-selected.txt`

`[rtk]` header lines in those receipts are not plan/task hits.

### Per-hit dispositions (`file:line`)

| Receipt | file:line | Disposition |
|---------|-----------|-------------|
| census-too-many-requests-old | implementation-plan.md:104 | confirmed-consistent — prohibition note, not a catch target |
| census-too-many-requests-old | implementation-plan.md:216 | confirmed-consistent — “Do not reference `TooManyRequests`” |
| census-tts-adapter-class-old | implementation-plan.md:341 | confirmed-consistent — negative oracle (`TTSAdapter` must not be the public class) |
| census-ac-union-old | _(no plan/task hits)_ | confirmed-consistent — old `PASS: complete AC set` union grep removed |
| census-stale-verdict-grep-old | _(no plan/task hits)_ | confirmed-consistent — any-match `verdict: approved` Quiet grep removed |
| census-engine-split-old | task.md:49 | updated — `ENGINE_BY_FORMAT` on MEU-9 implement row |
| census-engine-split-old | implementation-plan.md:100 | updated — named set definition |
| census-engine-split-old | implementation-plan.md:214 | updated — engine-split lock |
| census-engine-split-old | implementation-plan.md:344 | updated — AC-9.4 |
| census-engine-split-old | implementation-plan.md:363 | updated — sufficiency row |
| census-catalog-metadata-old | task.md:51 | updated — catalog.py row |
| census-catalog-metadata-old | implementation-plan.md:103 | updated — named set |
| census-catalog-metadata-old | implementation-plan.md:165 | updated — define-once table |
| census-catalog-metadata-old | implementation-plan.md:215 | updated — sideload lock |
| census-catalog-metadata-old | implementation-plan.md:350 | updated — AC-9.10 |
| census-catalog-metadata-old | implementation-plan.md:364 | updated — sufficiency |
| census-catalog-metadata-old | implementation-plan.md:377 | updated — files-modified |
| census-onnxruntime-old | task.md:48 | updated — mock InferenceSession |
| census-onnxruntime-old | task.md:49 | updated — dep pin |
| census-onnxruntime-old | implementation-plan.md:21 | updated — Goal engine split |
| census-onnxruntime-old | implementation-plan.md:100 | updated — ENGINE_BY_FORMAT |
| census-onnxruntime-old | implementation-plan.md:101 | updated — ONNX_RUNTIME_DEP |
| census-onnxruntime-old | implementation-plan.md:102 | updated — ONNX_PROVIDERS_AUTO |
| census-onnxruntime-old | implementation-plan.md:202 | updated — Device Auto |
| census-onnxruntime-old | implementation-plan.md:214 | updated — engine lock |
| census-onnxruntime-old | implementation-plan.md:218 | updated — SCAN_ADAPTER_LIBS |
| census-onnxruntime-old | implementation-plan.md:352 | updated — AC-9.12 |
| census-onnxruntime-old | implementation-plan.md:363 | updated — sufficiency |
| census-onnxruntime-old | implementation-plan.md:372 | updated — pyproject |
| census-onnxruntime-old | implementation-plan.md:379 | updated — tests file |
| census-onnxruntime-old | implementation-plan.md:461 | updated — SCAN_ADAPTER_LIBS command |
| census-onnxruntime-old | implementation-plan.md:535 | updated — research URL |
| census-per-meu-ac-new | task.md:63 | updated — H1-6a `PER_MEU_HANDOFF_AC` |
| census-per-meu-ac-new | implementation-plan.md:481 | updated — named receipt body |
| census-latest-verdict-new | implementation-plan.md:484 | updated — `LATEST_EXEC_VERDICT` definition |
| census-latest-verdict-new | implementation-plan.md:510 | updated — CLOSEOUT_GATE references it |
| census-latest-verdict-new | task.md:70 | updated — H2-4 inlines last-`^verdict:` parser |
| census-closeout-gate-new | task.md:70 | updated — H2-4 `CLOSEOUT_GATE` |
| census-closeout-gate-new | implementation-plan.md:510 | updated — named gate |
| census-kokoro-adapter-new | task.md:49 | updated |
| census-kokoro-adapter-new | implementation-plan.md:21 | updated |
| census-kokoro-adapter-new | implementation-plan.md:80 | updated — `TTS_ADAPTER_CLASS` |
| census-kokoro-adapter-new | implementation-plan.md:213 | updated — entrypoints |
| census-kokoro-adapter-new | implementation-plan.md:217 | updated — class lock |
| census-kokoro-adapter-new | implementation-plan.md:341 | updated — AC-9.1 |
| census-kokoro-adapter-new | implementation-plan.md:375 | updated — files-modified |
| census-scan-core-new | implementation-plan.md:119 | updated — `SCAN_CORE_INFRA_ARGS` includes onnxruntime |
| _(companion)_ | implementation-plan.md:447 | updated — SCAN_CORE command body matches named args (same `-e onnxruntime`) |

H1-7 (`task.md:65`) inlines the same last-`^verdict:` / last-`^review_mode:` parser as `LATEST_EXEC_VERDICT` without repeating the name token — **confirmed-consistent** with Finding 3.

Blast-radius census: K=12 receipts swept, V includes TooManyRequests / TTSAdapter / ENGINE_BY_FORMAT / CATALOG_METADATA / onnxruntime / per-MEU AC / LATEST_EXEC_VERDICT / CLOSEOUT_GATE / KokoroAdapter / SCAN_CORE. N hits listed above; all marked `updated` or `confirmed-consistent`. No leftover old union grep or Quiet `verdict: approved` any-match.

Frontmatter `verdict` set to `corrections_applied` for Round 3. This agent does not set `approved`.

🕐 2026-08-19 11:58 (EDT)

---

## Recheck — Round 3 (2026-08-19)

**Workflow**: `/plan-critical-review` Round 3 (round cap = 3)  
**Agent**: GPT-5.6-sol (Codex), independent reviewer

### Intent Anchor

Executing this plan is intended to deliver the Session 3 MEU-6, MEU-7, and MEU-9 external adapters behind the frozen core ports, including working PyTorch and ONNX Kokoro generation and an independently enforced evidence closeout. As corrected, it still would not reliably deliver that objective: the ONNX inference path omits required token/style inputs, and the execution-review predicate can approve a review that is not target-bound or has nonzero findings.

### PR-6 Correction-Census Pre-Verdict Gate

`pass` — all 12 named raw receipts exist and are untruncated. The exact audit at `C:/Temp/av-kit/review-r3-pr6-audit.txt` found 45 unique raw receipt/file/line hit pairs, 45 logged pairs, zero missing dispositions, and zero truncation markers. The two old-pattern no-hit receipts are explicitly dispositioned as confirmed-consistent.

### Findings

| # | Severity | Confidence | Finding | File:Line | Recommendation | Status |
|---|----------|------------|---------|-----------|----------------|--------|
| 1 | High | High | **The ONNX load/generate contract still omits the inputs needed to execute the cited graph.** `HF_FILE_MAP` downloads only the three `.onnx` model files. The engine lock says an optional quiet `KPipeline(model=False)` performs G2P and then calls `session.run(input_ids, style, speed)`, but it never defines phoneme-to-token-id conversion or the source/lifecycle of the length-indexed voice/style vector. The cited ONNX model card requires token IDs plus a style vector loaded from a voice asset; upstream quiet `KPipeline` yields phonemes and no audio. Therefore AC-9.4/9.6 can pass with mocked, invented arrays while real ONNX generation remains impossible. Original Finding 1 remains open under PR-4/PR-5/PR-8. | `implementation-plan.md:100,156-163,214,344,346,348-350`; [ONNX model card](https://huggingface.co/onnx-community/Kokoro-82M-ONNX/blob/main/README.md); [upstream KPipeline](https://github.com/hexgrad/kokoro/blob/main/kokoro/pipeline.py) | Define one source-backed ONNX preprocessing/resource contract: tokenizer/vocabulary, voice/style asset mapping and acquisition/offline behavior, tensor shapes/dtypes, and failure mapping. Add negative oracles for missing/mismatched tokenizer/style assets and positive generation for every ONNX seed without fabricated adapter inputs. | open |
| 2 | High | High | **`LATEST_EXEC_VERDICT` fixes stale ordering but remains non-target-bound and findings-inconsistent.** The parser now rejects an earlier `approved` followed by current `changes_required`, but it only looks for the project slug anywhere and never parses `target_plan`, `findings_count`, or the expected review round. The exact probe at `C:/Temp/av-kit/review-r3-falsepass-probes.txt` shows `False` for stale-approved/current-changes-required (fixed), but `True` for a wrong `target_plan` whose body merely mentions the slug and `True` for `approved` with `findings_count: 2`. H1-7 and H2-4 both embed this predicate, so the independent-review hard gate can still materially false-pass. Original Finding 3 remains open under PR-4/PR-8. | `implementation-plan.md:484-487,510`; `task.md:65,70` | Parse the latest YAML frontmatter as structured data and require the exact implementation-review mode, exact target plan/project binding, `verdict == approved`, `findings_count == 0`, and a valid latest `review_round` within the execution cap. Reuse that single parser in H1-7 and H2-4. | open |

### Prior Finding Recheck

| Round 1 finding | Round 3 result | Evidence |
|-----------------|----------------|----------|
| 1 High — ONNX load/generate | ❌ Still open | Model dispatch exists, but tokenization and voice/style resources remain undefined; Finding 1 above. |
| 2 High — sideload DTO | ✅ Fixed | `CATALOG_METADATA` exactly supplies `name`, `format`, `precision`, and Session 2 catalog sizes; AC-9.10 uses `stat()` for existing files and prohibits DB imports (`implementation-plan.md:103,165-172,215,350,377`). |
| 3 High — stale review approval | ❌ Partially fixed, still open | Last-verdict ordering rejects the requested stale case, but wrong-target and nonzero-findings approvals still pass; Finding 2 above. |
| 4 High — closeout missing artifacts / SSOT drift | ✅ Fixed for the requested predicate | `CLOSEOUT_GATE` requires exactly three handoffs, per-MEU ACs, reflection markers, metrics slug, latest review, and `render --check`; the missing-artifact probe returns `False`. H2-2 runs `SSOT_APPROVED`, render, and render-check before H2-4 (`task.md:68,70`). |
| 5 High — aggregate AC union | ✅ Fixed | The union counterexample now reports MEU-7 and MEU-9 missing their own ACs and returns `False`; `PER_MEU_HANDOFF_AC` binds each file to its own prefix (`implementation-plan.md:478-481`; `task.md:63`). |
| 6 Low — stale transcript exception | ✅ Fixed | Remaining `TooManyRequests` occurrences are prohibition/explanation text only (`implementation-plan.md:104,216`). |
| 7 Low — adapter name drift | ✅ Fixed | `KokoroAdapter` is canonical; `TTSAdapter` remains only as a negative oracle (`implementation-plan.md:80,217,341`). |
| 8 Low — repeated predicates | ✅ Non-blocking / confirmed-consistent | Named owners exist; task validation cells retain exact executable commands as required by the task template. No materially ambiguous live spelling was found. |

### Requested False-Pass Probes

Receipt: `C:/Temp/av-kit/review-r3-falsepass-probes.txt`.

| Predicate | Adversary case | Result |
|-----------|----------------|--------|
| `LATEST_EXEC_VERDICT` | old `approved`, latest `changes_required` | rejected (`False`) |
| `LATEST_EXEC_VERDICT` | wrong target; slug only in body | **false-pass (`True`)** |
| `LATEST_EXEC_VERDICT` | `approved` with `findings_count: 2` | **false-pass (`True`)** |
| `CLOSEOUT_GATE` | handoffs/reflection/metrics absent | rejected (`False`) |
| `PER_MEU_HANDOFF_AC` | all ACs in MEU-6; MEU-7/9 marker shells | rejected (`False`); missing AC-7.1 and AC-9.1 reported |

### Scope and Commands Executed

- Reviewed the updated `implementation-plan.md`, `task.md`, full rolling review thread, frozen TTS/model ports, `ModelVariant`, Session 2 seed catalog, and cited infrastructure spec.
- Read the full `/plan-critical-review` workflow including PR-6, reviewer role, review template, harness override, project profile, context, guardrails, and output-evidence policy.
- PR-6 raw receipt audit → `C:/Temp/av-kit/review-r3-pr6-raw-receipts.txt` and `review-r3-pr6-audit.txt`.
- Exact line-numbered targets → `C:/Temp/av-kit/review-r3-plan-raw.txt`, `review-r3-task-raw.txt`, and `review-r3-thread-raw.txt`.
- Requested predicate probes → `C:/Temp/av-kit/review-r3-falsepass-probes.txt`.
- Not-started / referenced-artifact checks → `C:/Temp/av-kit/review-r3-readiness.txt` and `review-r3-referenced-artifacts.txt`: all planned adapters/tests/handoffs are absent; existing tools/templates/regression tests exist; all task rows remain unchecked.
- Deferred-MEU census → `C:/Temp/av-kit/review-r3-scope-ids.txt`: MEU-10–23 are registered and grouped.
- `rtk git status --short` → `C:/Temp/av-kit/review-r3-git-status.txt` returned 128 because the supplied tree is not a Git worktree; no diff claim was used.
- Primary-source verification: ONNX Community model card and upstream `hexgrad/kokoro` `KPipeline` implementation. Product pytest/pyright/ruff were not run because the plan remains unapproved and explicitly forbids them before approval.

### Checklist Results

| Check | Result | Evidence |
|-------|--------|----------|
| PR-1 Plan/task alignment | pass | Same MEU-6 → MEU-7 → MEU-9 order and outputs. |
| PR-2 Not-started confirmation | pass | Planned code/tests/handoffs absent; 29 unchecked task markers. |
| PR-3 Task contract completeness | pass | Every executable row has task, owner, deliverable, validation, dependency/context, and status. |
| PR-4 Validation realism | fail | Findings 1–2 demonstrate material runtime/review false-passes. |
| PR-5 Source-backed planning | fail | ONNX token/style resource behavior remains unstated despite the cited primary source. |
| PR-6 Handoff/corrections readiness | pass | 45/45 per-hit disposition audit; three MEU handoff paths explicit. |
| PR-7 Scope discipline (C2) | pass | Deferred MEU-10–23 ids exist; out-of-scope rows cite local/spec authority. |
| PR-8 Control reachability/totality | fail | ONNX inputs have no producer/resource chain; review approval is not target/findings bound. |
| PR-9 Single-statement discipline | pass | No materially divergent live predicate spelling; exact task commands remain auditable. |
| DR-1 Claim-to-state match | pass | `draft`/unstarted claims match disk state. |
| DR-2 Residual old terms | pass | Prior exception/class strings survive only as explicit negative wording. |
| DR-3 Downstream references updated | pass | Plan/task/grouping/MEU ids align. |
| DR-4 Verification robustness | fail | The latest-review gate misses wrong-target and nonzero-finding approvals. |
| DR-5 Evidence auditability | pass | Exact commands and receipts are named above. |
| DR-6 Cross-reference integrity | pass | Corrected SSOT render chain and deferred MEUs align with canon. |
| DR-7 Evidence freshness | pass | Round 3 receipts were reproduced on 2026-08-19. |
| DR-8 Completion vs residual risk | pass | Targets remain `draft`; no implementation-complete claim. |

### Adversarial Verification Checklist

| Check | Result | Evidence |
|-------|--------|----------|
| AV-1 Failing-then-passing proof | planned | Dedicated Red rows and receipts exist for each MEU; execution has not begun. |
| AV-2 No bypass hacks | planned | G36 rule and scan are present. |
| AV-3 Changed paths asserted | fail at plan level | ONNX token/style production is not asserted; Finding 1. |
| AV-4 No skipped/xfail masking | planned | `SCAN_G36` is exact and task-bound. |
| AV-5 No unresolved placeholders | planned | `SCAN_PLACEHOLDER` is exact and task-bound. |
| AV-6 Source-backed criteria | fail | The ONNX preprocessing/resource seam remains unsourced and underspecified. |

### Open Questions / Assumptions

- No product-scope decision is required to recognize the two blockers. A correction must choose and source an executable ONNX preprocessing/resource design (raw ONNX Runtime with explicit tokenizer/voice assets, or a compatible source-backed wrapper) and bind the review parser to the actual YAML contract.
- The repository is not a Git worktree, so review evidence is file-state and receipt based.

### Follow-Up Actions

1. **HARD STOP:** the plan-review round cap of 3 has been reached with `changes_required`; do not autonomously run `/plan-corrections` or begin execution.
2. Await explicit human direction on whether to run another correction/review cycle or revise scope.
3. If directed, correct only the two blocking findings above and preserve the already-fixed Findings 2, 4, and 5.

### Residual Risk

The requested missing-artifact and per-MEU-union predicates now fail closed, and stale earlier approval is no longer accepted when a later `changes_required` line exists. Execution remains unsafe because ONNX generation inputs are not constructible from the planned assets and the independent-review gate can still accept an approval for the wrong target or with unresolved findings.

### Verdict

`changes_required` — two evidence-backed High findings remain. This is Round 3, so the workflow round cap is reached and requires explicit human direction before any further correction or execution work.

---

## Corrections Applied — Round 3 High findings — USER_EXPLICIT 2026-08-19

**Workflow**: `/plan-corrections` after human choices (hybrid ONNX preprocess; `tools/check_exec_review.py`).  
**Verdict**: `corrections_applied` (not `approved`). Post-cap re-review still requires explicit human authorization.

### Findings addressed

| Round 3 # | Correction | Files |
|-----------|------------|-------|
| 1 High ONNX token/style | Named set `ONNX_PREPROCESS`: quiet `KPipeline(model=False)` G2P; `ONNX_VOCAB_FILE` (`config.json` `vocab`); pad-0 `int64` ids; style from hexgrad `voices/{id}.pt` at `len(phonemes)-1`; `session.run(input_ids, style, speed)`. AC-9.4/9.6 expanded; **AC-9.13** missing-asset/`>510` negatives. No `kokoro-onnx`. No community `.bin` voices. Tests must capture adapter-built run kwargs. | `implementation-plan.md`; `task.md` rows 9–10 |
| 2 High review gate | `CHECK_EXEC_REVIEW` = `tools/check_exec_review.py` parses **first YAML frontmatter only**. Exact `target_plan`, `review_mode=implementation`, `verdict=approved`, `findings_count==0`, `round` or `review_round` in 1..6. H1-7 and H2-4 call the same command. `--self-test` covers the two Round 3 false-pass fixtures. Body slug / last-`^verdict:` greps removed. | `tools/check_exec_review.py`; plan Verification Plan §6; `task.md` H1-7/H2-4; `.agent/docs/commands.md` |

Prior Round 1 Findings 2, 4, 5 remain fixed (untouched this pass).

### Blast-radius census

Receipts: `C:/Temp/av-kit/census-slug-old.txt`, `census-last-verdict-old.txt`, `census-select-approved-old.txt`, `census-check-exec-new.txt`, `census-onnx-preprocess-new.txt`, `census-ac913-new.txt`. Self-test: `C:/Temp/av-kit/exec-review-selftest.txt` → `PASS: check_exec_review self-test`.

| Value | Old sweep | New sweep | Disposition |
|-------|-----------|-----------|-------------|
| `target slug missing` | 0 hits in plan/task | — | confirmed-consistent (removed) |
| last-`^verdict:` body parser in H1-7/H2-4 | 0 live command hits | prohibition prose only in `LATEST_EXEC_VERDICT` | confirmed-consistent |
| any-match `verdict: approved` Select-String | 0 hits | — | confirmed-consistent (removed) |
| `check_exec_review.py` | — | plan named set + Files Modified + §6 command + H1-7 + H2-4 | updated |
| `ONNX_PREPROCESS` | — | named set + lock + AC-9.4/9.6 + sufficiency + rows 9–10 | updated |
| `AC-9.13` | — | plan AC row + task rows 9–10 | updated |

Blast-radius census: 6 values changed, 6 variants swept, old greps clean, new sites listed above.

### PR-6 per-hit census — 2026-08-19 12:52 (EDT)

Human authorized post-cap review continuation. Each raw `file:line` from the named receipts is dispositioned here (not a bare count).

**`census-check-exec-new.txt` (`check_exec_review.py`)**

| file:line | Disposition |
|-----------|-------------|
| `task.md:65` | updated — H1-7 validation is `CHECK_EXEC_REVIEW` |
| `task.md:70` | updated — H2-4 chains `check_exec_review.py` after structural closeout |
| `implementation-plan.md:108` | updated — named set `CHECK_EXEC_REVIEW` |
| `implementation-plan.md:391` | updated — Files Modified lists the tool |
| `implementation-plan.md:499` | updated — `LATEST_EXEC_VERDICT` exact command |
| `implementation-plan.md:532` | updated — Open Questions cites the tool |
| `implementation-plan.md:553` | updated — research/human lock citation |

**`census-onnx-preprocess-new.txt` (`ONNX_PREPROCESS`)**

| file:line | Disposition |
|-----------|-------------|
| `task.md:48` | updated — row 9 Red mocks `ONNX_PREPROCESS` kwargs |
| `task.md:49` | updated — row 10 Green implements `ONNX_PREPROCESS` |
| `implementation-plan.md:75` | updated — User Review Required records the lock |
| `implementation-plan.md:102` | updated — `ENGINE_BY_FORMAT` plus preprocess |
| `implementation-plan.md:107` | updated — named set owner |
| `implementation-plan.md:224` | updated — Implementation lock (full pipeline) |
| `implementation-plan.md:354` | updated — AC-9.4 quiet pipeline allowed |
| `implementation-plan.md:356` | updated — AC-9.6 captured run kwargs |
| `implementation-plan.md:374` | updated — sufficiency table |
| `implementation-plan.md:390` | updated — test file summary |
| `implementation-plan.md:540` | updated — Open Questions promotion |

**`census-ac913-new.txt` (`AC-9.13`)**

| file:line | Disposition |
|-----------|-------------|
| `task.md:48` | updated — Red row includes AC-9.13 |
| `task.md:49` | updated — Green row includes AC-9.13 |
| `implementation-plan.md:363` | updated — missing vocab/voice/`>510` AC |

**Old-pattern no-hit receipts (confirmed-consistent)**

| Receipt | Hits | Disposition |
|---------|------|-------------|
| `census-slug-old.txt` | 0 (banner only) | confirmed-consistent — `target slug missing` removed from live commands |
| `census-last-verdict-old.txt` | 0 (banner only) | confirmed-consistent — no live last-`^verdict:` parser |
| `census-select-approved-old.txt` | 0 (banner only) | confirmed-consistent — no any-match `verdict: approved` grep |

Self-test receipt `C:/Temp/av-kit/exec-review-selftest.txt`: `PASS: check_exec_review self-test`.


### Not done

- Independent plan `approved` (cap 3 already used; needs human-authorized Round 4).
- Product adapters / pytest (SIGN 1).
- Session 4 / `p3-services`.

🕐 2026-08-19 (EDT) — timestamp skill applied at chat close.

---

## Recheck — Round 4 (2026-08-19, USER_EXPLICIT post-cap continuation)

**Workflow**: `/plan-critical-review` Round 4  
**Agent**: GPT-5.6-sol (Codex), independent reviewer  
**Review Mode**: `plan`

### Intent Anchor

Executing this plan is intended to deliver the Session 3 MEU-6, MEU-7, and MEU-9 external adapters behind the frozen core ports, including a constructible PyTorch/ONNX Kokoro generation path and a target-bound independent execution-review gate. The Round 4 question is whether the two Round 3 High failures still prevent that objective; no new nearby predicate-shape requirement is material unless it demonstrates a different delivery failure.

### PR-6 Correction-Census Pre-Verdict Gate

`pass` — all six named `C:/Temp/av-kit/census-*.txt` receipts exist and were read in full. The three new-value receipts contain 21 unique raw `receipt + file:line` hits, and the appended correction table contains the same 21 unique dispositions with zero missing or extra entries. Each of the three old-pattern receipts contains zero non-banner hits and has one `confirmed-consistent` disposition row. Evidence: `C:/Temp/av-kit/round4-pr6-inventory.txt`, `round4-pr6-raw-receipts.txt`, and `round4-pr6-reconciliation.json`.

### Findings

No severity-rated findings. Under the Verdict Rule, the structured finding set is empty for an `approved` verdict.

### Round 3 High-Finding Recheck

| Round 3 finding | Round 4 result | Substantive evidence |
|-----------------|----------------|----------------------|
| 1 High — ONNX inputs had no producer/resource chain | ✅ Fixed | `ONNX_PREPROCESS` now defines quiet `KPipeline(model=False)` G2P, `hexgrad/Kokoro-82M` `config.json` `vocab`, `voices/{voice_id}.pt`, drop-unknown vocab ids, pad-0 `int64` input, `pack[len(phonemes)-1]` float32 style, float32 `[speed]`, and `session.run(None, {input_ids, style, speed})` (`implementation-plan.md:105-107,224`). AC-9.6 requires the adapter-built feed to be captured and asserted, including `"ab"` → `[[0,1,2,0]]` and the style index (`implementation-plan.md:356`); task 9 repeats the capture obligation (`task.md:48`). AC-9.13 covers missing vocab/voice assets and the 510-token boundary (`implementation-plan.md:363`; `task.md:48-49`). The local witness produced `int64 [1,4]`, float32 style `[1,256]`, and float32 speed `[1]`: `C:/Temp/av-kit/round4-onnx-preprocess-witness.json`. |
| 2 High — execution review could accept wrong target/nonzero findings | ✅ Fixed | `parse_first_frontmatter` returns only the first YAML block (`tools/check_exec_review.py:42-58`); `check_review` then requires exact mode, exact `target_plan`, `approved`, `findings_count == 0`, and a round in `1..max_round` (`tools/check_exec_review.py:94-131`). The required `uv run python tools/check_exec_review.py --self-test` passed. Standalone wrong-target/body-slug and `approved` + `findings_count: 2` fixtures each returned exit 1 (`C:/Temp/av-kit/round4-exec-review-adversary-probes.txt`). H1-7 and H2-4 both invoke this helper (`task.md:65,70`); no last-`^verdict:` or body-slug gate remains. |

Round 1 Findings 2, 4, and 5 remain fixed and were not disturbed by these corrections. The former Low exception-name, adapter-name, and predicate-duplication notes remain resolved/non-blocking; no competing live behavior was demonstrated.

### Primary-Source Cross-Check for ONNX Preprocessing

- Upstream [`KPipeline`](https://github.com/hexgrad/kokoro/blob/main/kokoro/pipeline.py) documents quiet `model=False`, yields no audio on that path, downloads `voices/{voice}.pt` in `load_single_voice`, and selects `pack[len(ps)-1]` in `infer`.
- Upstream [`KModel`](https://github.com/hexgrad/kokoro/blob/main/kokoro/model.py) loads `config.json` `vocab`, drops unknown phoneme characters, and constructs a padded `torch.LongTensor([[0, *input_ids, 0]])`.
- The official [ONNX model card](https://huggingface.co/onnx-community/Kokoro-82M-ONNX) uses the `input_ids`, `style`, and `speed` feed names, a `(1, <=512)` padded token input, a `(1,256)` style vector, and float32 speed. The plan deliberately sources the compatible style pack from hexgrad rather than the community `.bin` voice bundle, as human-approved.

These sources and the explicit AC assertions make the planned production chain constructible; the tests cannot satisfy AC-9.6 by fabricating the feed inside `session.run`.

### Checklist Results

#### Plan Review (PR-1 through PR-9)

| Check | Result | Evidence |
|-------|--------|----------|
| PR-1 Plan/task alignment | pass | Both targets retain MEU-6 → MEU-7 → MEU-9. Plan AC-9.6/9.13 and task rows 9–10 carry the same ONNX preprocess/test obligations; H1-7/H2-4 use the same parser. |
| PR-2 Not-started confirmation | pass | 28 executable task rows are unchecked, with zero checked or in-progress rows. Planned adapters, integration tests, MEU handoffs, implementation review, and reflection are absent. The review helper exists because it was an authorized Round 3 plan-correction target. Evidence: `round4-readiness.json`. |
| PR-3 Task contract completeness | pass | Executable rows retain task, owner, deliverable, exact validation, dependencies, context strategy, durable output, and status. |
| PR-4 Validation realism | pass | The ONNX feed is asserted at the adapter boundary, and both reproduced execution-review false passes now exit 1. No materially missing deliverable can pass the corrected gates demonstrated this round. |
| PR-5 Source-backed planning | pass | The hybrid was human-approved and is bound to upstream Kokoro/ONNX behavior plus the local frozen port/spec. |
| PR-6 Handoff/corrections readiness | pass | 21/21 new raw hits dispositioned; three zero-hit old receipts explicitly dispositioned; three MEU handoffs remain explicit. |
| PR-7 Scope discipline / C2 | pass | Corrections affect only the MEU-9 preprocessing contract and execution-review helper; MEU-10–23 deferrals and Session 3 scope are unchanged. |
| PR-8 Control reachability/totality | pass | `KokoroAdapter.generate` now has a traceable producer chain to all three `session.run` inputs and negative asset/token oracles; the review gate is bound to its first-frontmatter target and zero-finding state. |
| PR-9 Single-statement discipline | pass | Named owners remain canonical. Per the Materiality Gate, no predicate-shape or nearby-mutation escalation was reopened. |

#### Docs Review (DR-1 through DR-8)

| Check | Result | Evidence |
|-------|--------|----------|
| DR-1 Claim-to-state match | pass | Correction claims match current plan/task/tool state and reproduced receipts. |
| DR-2 Residual old terms | pass | All three named old-pattern receipts are zero-hit apart from the RTK banner. |
| DR-3 Downstream references updated | pass | Plan Verification §6 and task H1-7/H2-4 call `tools/check_exec_review.py`; task rows 9–10 schedule AC-9.13 and feed capture. |
| DR-4 Verification robustness | pass | The exact two Round 3 false-pass witnesses are rejected; the ONNX test contract asserts adapter-built values, dtypes, shapes, and asset failures. |
| DR-5 Evidence auditability | pass | Raw census receipts, exact per-hit dispositions, self-test output, standalone probes, and the ONNX witness are named and reproducible. |
| DR-6 Cross-reference integrity | pass | Plan, task, frozen ports, local spec, and upstream input contract agree on this session's deliverables. |
| DR-7 Evidence freshness | pass | Round 4 reread current targets and reran the parser/self-test/probes on 2026-08-19. |
| DR-8 Completion vs residual risk | pass | This approves planning readiness only; all execution rows remain unchecked and no implementation-complete claim is made. |

#### Adversarial Verification (AV-1 through AV-6)

| Check | Result | Evidence |
|-------|--------|----------|
| AV-1 Failing-then-passing proof | planned | Each MEU retains Red-before-Green rows and named FAIL_TO_PASS receipts; execution is unstarted. |
| AV-2 No bypass hacks | planned | G36 scan remains task-bound. |
| AV-3 Changed paths asserted | pass at plan level | AC-9.6 requires assertions on the adapter-built ONNX feed, not mere execution of the mock. |
| AV-4 No skipped/xfail masking | planned | `SCAN_G36` remains exact. |
| AV-5 No unresolved placeholders | planned | `SCAN_PLACEHOLDER` remains exact. |
| AV-6 Source-backed criteria | pass | The new ONNX criteria are Human-approved and tied to primary Kokoro/ONNX sources. |

### Scope and Commands Executed

Reviewed the current `implementation-plan.md`, `task.md`, `tools/check_exec_review.py`, full rolling thread, plan-review workflow (including PR-6, Materiality, and Verdict Rule), relevant local TTS/model canon, role contracts, review template, and the latest peer plan-review exemplar.

- Fully read and reconciled the six named census receipts plus `exec-review-selftest.txt`.
- Ran `uv run python tools/check_exec_review.py --self-test` exactly as requested → pass.
- Ran standalone wrong-target/body-slug and approved/nonzero-findings fixtures through the helper's CLI entrypoint → exit 1 for each.
- Ran a deterministic ONNX feed witness for the locked phonemes/vocab/pack inputs → expected keys, values, dtypes, and shapes.
- Ran static task/output/tool readiness checks. No product pytest, pyright, ruff, build, git, or implementation command was run.

### Open Questions / Assumptions

None. The Round 3 product choices were supplied by `USER_EXPLICIT`, and this review did not infer a different ONNX library, voice bundle, or review predicate.

### Residual Risk

This remains a static pre-execution approval. Real Kokoro, ONNX Runtime provider, Hugging Face cache, yt-dlp, and transcript behavior must still be proven by the planned Red/Green and integration receipts. That ordinary execution risk is not a demonstrated plan failure.

### Verdict

`approved` — PR-6 passes; the ONNX contract now produces every required `session.run` input from named assets and requires assertions on adapter-built kwargs; the first-frontmatter review parser rejects both Round 3 false-pass cases with exit 1. No evidence-backed High/Critical finding remains, so the Verdict Rule requires approval.
