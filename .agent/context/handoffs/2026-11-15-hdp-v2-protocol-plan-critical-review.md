---
date: "2026-11-15"
review_mode: "plan"
target_plan: "docs/execution/plans/2026-11-15-hdp-v2-protocol/implementation-plan.md"
verdict: "approved"
findings_count: 0
template_version: "2.2"
requested_verbosity: "standard"
agent: "codex-independent-reviewer"
loop_id: "hdp-plan-2026-11-15-hdp-v2-protocol"
round: 3
---

> **Current assessment (round 3): approved.** F1, F2 and F3 are fixed; no new findings. The round-1 and round-2 assessments below are retained as history and are superseded by **Recheck (round 3)**. Frontmatter describes round 3.

# Critical Review: 2026-11-15-hdp-v2-protocol

> **Review Mode:** `plan`
> **Verdict:** `changes_required`

> **Rolling report:** Round 1 below is historical and retained in full. The current assessment is in **Recheck (round 2)**: F1 and F2 are fixed; F3 is the sole current blocking finding. Frontmatter describes round 2.

## Scope

**Intent anchor:** av-kit's Human Decision Protocol, `AGENTS.md`, the four templates and every workflow, doc and skill that cites the protocol follow upstream HD1: the agent decides before it asks, a brief leads with a plain-words recommendation and keeps a do-nothing option, §4a names what is always the human's, and each decision is recorded once, in the log of the stage that made it.

**Intent assessment: partial, as a plan.** The proposed document changes serve that goal. The start gate can reject the intended prerequisite port, and the oracle can certify a protocol missing the actual mandatory-human criteria. Those are execution and substantive verification defects, rather than formatting objections.

Claude Code/Anthropic authored the plan; Codex, class `avkit_independent_reviewer`, independently reviewed it. Scope included the whole implementation plan and task, all four existing plan-local scripts, live protocol/AGENTS/guardrails, affected template and inventory surfaces, upstream `a73d6df`, Zorivest HD1 precedents, Session 84's corrected port checker, and Session 86/87 dependency contracts. PR-1–PR-9 and applicable DR checks were applied through the Materiality Gate.

Only `C:/Temp/av-kit` was written. No repository file, live ledger, dependency environment, or upstream repository was changed. No network, pytest, uv, npm, baseline script or product suite ran. Identity ran only its synthetic selftest; it did not enumerate real untracked-file contents. Protected secret/configuration paths were not opened. The coordinator owns copying this report and recording the verdict. Existing execution authorization and the no-commit boundary are accepted.

## Findings

| # | Severity | Blocking | Kind | Finding | File:Line | Recommendation | Status |
|---|---|---|---|---|---|---|---|
| F1 | High | yes | behavior | **S2 rejects the intended Session 84 port.** Confidence: High. `FIELD_CHECK` and `EXAMPLE_CHECK` are Session 84's named planning contracts, not identifiers its port writes into `VALIDATOR`. Its corrected `port-check.py` instead requires `decision_field_text`, `_NON_TEXT_SCALAR`, `_quoted_scalar_text` and `grouping_row_problems`. The Session 84 positive port fixture passes its own shape checker with no problems, but Session 85's exact marker predicate reports both required names missing and returns 12 even assuming the reflection exists. Thus row 0 stops before collecting `EVIDENCE`, preventing AC-9 and every dependent implementation row after a correctly landed prerequisite. Violates **AC-9** through its unreachable EVIDENCE prerequisite; S2 is the immediate faulty contract. | `docs/execution/plans/2026-11-15-hdp-v2-protocol/baseline.ps1:42`; `implementation-plan.md:371`; Session 84 `port-check.py:52` | Replace the planning-label presence test with the prerequisite's actual port-shape/behavior contract. Reuse its corrected read-only port checker and retain the successful fresh selftest/tests and closeout requirement. Prove that the intended corrected port passes while an unported or partially ported fixture fails. Update S2's prose to match. | open |
| F2 | High | yes | control-defeat | **ORACLE can certify a protocol without the human-only decision rules.** Confidence: High. `mechanism: task-row-completion-predicate`. C3 checks the M-row numbers and a bag of source/note markers, but never the fourteen criteria or their row-to-source associations. Its positive fixture literally uses `M-7 / item 7 / src`, and similarly for every M row. An independent probe retained the real live BASE §2 sweep/commands and §4 body, used those empty M criteria, and obtained zero failures from C1–C11. C11 also accepted a missing validator paragraph when all twenty topics pointed to the opening record-once sentence and one passing pending-check arm. A coder can therefore obtain the promised green row/gate while §4a names none of the actual human-owned decisions; this materially defeats the goal and **AC-6**, with the second probe also exposing AC-9's unbound topic semantics. | `docs/execution/plans/2026-11-15-hdp-v2-protocol/hdp-check.py:533`; `hdp-check.py:662`; `hdp-check.py:743` | Strengthen the existing oracle: bind each M row to its planned adapted criterion and source, and plant a fault that removes a criterion while preserving its ID. Bind C11 topics to the actual required clauses and appropriate evidence selectors rather than arbitrary implementer-supplied substrings. Use a substantive positive protocol fixture. Keep the existing oracle and rows; no new review machinery is needed. | open |

## Q1 — Goal

**Accepted:** AC-1–10/row 1 cover the protocol; AC-11/row 3 cover AGENTS; AC-13/row 2 cover templates; AC-14–16/rows 5–6 cover callers. Brief v2 retains the recommendation, plain words, failure/undo explanation and do-nothing option. The proposed stage logs and reflection links implement record-once.

**Not accepted:** green checks do not yet prove the §4a clause of the goal (F2), and F1 can prevent all implementation. No additional product scope or MEU is needed.

## Q2 — Upstream and av-kit adaptations

**Accepted:** the eight-section structure, retained §4 obviousness test, av-kit sweep/receipt/search surfaces, hdp-only mode, fourteen upstream M criteria, adapted §5d/§5e references, unsuffixed SIGN 3, and Session 86 exclusions are coherent. The cited AGENTS anchors/sections exist; harness-profiles and GUARDRAILS supply the identified local surfaces. The M-3 exception is intentionally absent here. Renaming §7/§8 does not displace a discovered live citation.

**Implementation note:** when keeping §3's angles table, make the old “Run 2–3 queries per decision” instruction apply to web research when needed. Leaving it unconditional would conflict with the new reuse/local-measurement research rule. This is a bounded wording clarification, not another blocker.

## Q3 — Records and the Session 84 binding

**Accepted:** the optional `mandatory:` field preserves existing records and is honestly described as unchecked. The proposed reflection link list/`None.`, stage-log fields/pending refusal, same-stage check, source classification and bounded grammar match the intended record-once port. Passing the plan, handoff and declared grouping at H2-2 is correct. VALIDATOR remains read-only.

**Not accepted as proof:** C11 checks independent substring membership, not whether the evidence proves its named topic. The independent probe mapped all topics to one sentence and one arm and passed (F2). Extend the existing binding to Session 84's corrected grouping-row field/pending checks; the proposed “Each plan, handoff and issue entry” sentence omits grouping rows. Keep the scalar description accurate after comment stripping/unquoting changes. New landed behavior cannot be discovered by the current closed twenty-topic list alone; inspect the corrected prerequisite before finalizing §6. These amendments fit row 1 and D-850 without editing VALIDATOR or adding scope.

## Q4 — AGENTS.md and the repin

**Accepted:** replacing the old sentence in place preserves the hard-gate qualification and the do-nothing requirement while delegating the detailed recording rule to the protocol. The specified edit stays on line 27; the unchanged line/block counts and byte budget are plausible and explicitly checked. Updating only the work-tree-byte digest is consistent with `verify_adoption.py` and the earlier repin precedent. No omitted obligation requires an additional AGENTS rule.

## Q5 — Inventory and templates

**Accepted:** the live citation/stale-instruction sweep and source inspection support the edited/no-edit inventory. No additional omitted live file requiring a record-once or Brief v2 change was established. The four template changes preserve their consumers: task H2-2 changes prose while retaining columns/commands, handoff retains the accepted comment/YAML frame, and reflection changes only the decision body whose reconciliation Session 84 removes. Byte-identical twins are checked.

The saved plan-time lint receipts report passing template/task lint. This review inspected the relevant linter/parser contracts; it does not claim a fresh lint or post-edit template pass. Recheck after implementation as already planned. Other sessions' plans and historical artifacts are correctly outside the rewrite inventory.

## Q6 — Cross-session dependencies

**Not accepted:** S2's identifier predicate falsely rejects the prerequisite's intended output (F1). Fresh prerequisite selftest/tests are valuable but cannot help because the faulty marker check precedes them. A reflection's existence alone is also not proof of a completed prerequisite; use its actual completed port/closeout contract.

**Accepted:** Session 86's §4a M-3/M-5/M-6/M-8 rows, exact plain M-3 note, §6 overturn paragraph and Open decisions bullet are all explicit outputs here. Session 87's HEAD comparison is compatible with I15: only the `Topic too broad` row of `inspiration-research.md` changes. S3 checks EDITED against BASE rather than incorrectly requiring a clean whole tree; S4 preserves prior sessions' dirty contents and VALIDATOR.

## Q7 — Checks and safety

**Accepted:** the live oracle returns the expected preimplementation Red: 131 failures; C5–C10 pass. The oracle's 36 planted faults pass, identity selftest passes, and scope selftest passes after a process-only scratch signing override. C6 measures all 28 EDITED files and preserves the actual bare-LF line content in model-delegation. Scope checks catch dirty-content changes, new outside paths, VALIDATOR changes and moved HEAD. Planned write destinations fit EDITED, plan-local/closeout outputs and temp; AC-18 does not authorize modifying VALIDATOR.

**Not accepted:** the positive specimen is not substantive for §4a, and the existing faults do not expose that omission (F2). No further exhaustive regex or formatting mutations are requested. The ordinary scope selftest initially stopped at its scratch commit (exit 128); rerunning with process-local `commit.gpgsign=false` exercised all assertions. That reviewer-environment limitation is not reported as a product or plan blocker.

## Checklist Results

| Check | Result | Procedure / command | Exit | Evidence |
|---|---|---|---|---|
| PR-1, PR-3, PR-5–7, PR-9 | pass | Manual plan/task/source/dependency comparison by codex-independent-reviewer | null | Same ordered work, source-tagged ACs, bounded governance scope, named corrections/handoffs and legitimate later-session ownership. No material contradictory duplicate contract established. |
| PR-2 | pass | Read canonical task and inspect target outputs | null | Implementation rows remain pending; scripts are planning verifiers, not completed implementation. |
| PR-4 / S2 | fail | `rtk proxy python C:/Temp/av-kit/s85-review-probe.py` | 0 | Positive corrected S84 fixture: shape problems `[]`; missing S85 markers `['EXAMPLE_CHECK', 'FIELD_CHECK']`; S2 result `12`. Probe process completion is separate from the simulated gate result. |
| PR-8 / AC-6, AC-9; DR-4 | fail | Same independent in-memory probe | 0 | Placeholder M criteria and absent validator paragraph: `{'C1': 0, 'C2': 0, 'C3': 0, 'C4': 0, 'C5': 0, 'C6': 0, 'C7': 0, 'C8': 0, 'C9': 0, 'C10': 0, 'C11': 0}`. |
| Oracle planted faults | pass | `rtk proxy python docs/execution/plans/2026-11-15-hdp-v2-protocol/hdp-check.py --selftest` | 0 | All-green tree accepted; existing 36 faults refused; `hdp-check selftest: 0 failures`. |
| Real-tree baseline and endings | pass | `rtk proxy python docs/execution/plans/2026-11-15-hdp-v2-protocol/hdp-check.py --eol-snapshot C:/Temp/av-kit/hdp85/review/eol-baseline.json`, then `--eol-baseline` with that path | 0 / 1 | 28 files, 28 CRLF, model-delegation mixed; expected live Red 131 failures and C5–C10 ok. |
| Scope / identity selftests | pass | `scope-check.py --selftest`; `identity.py --selftest`, each through `rtk proxy python` with bytecode disabled and TMP/TEMP under temp | 0 / 0 | Scope: eight checks, 0 failures with scratch signing disabled in the process; identity: bound mutations invalidate, closeout outputs preserve identity, 0 failures. |
| Product suites / actual post-edit gates | n/a | Not run during this read-only plan review | null | Execution evidence remains the implementer's responsibility. |

```json
{"schema_version":"evidence.v1","check_id":"s85-substance-probes","command":"rtk proxy python C:/Temp/av-kit/s85-review-probe.py","cwd":"P:/av-kit","scope":"Session 85 S2, C3 and C11; corrected Session 84 positive port fixture; in-memory protocol with actual live BASE sweep and obviousness section","phase":"targeted","exit_code":0,"result":"fail","tested_state":"review-round-1-working-tree-2026-11-15; synthetic fixtures; no implementation certification","output":"S84 positive port fixture shape problems: []; S85 S2 required markers missing: ['EXAMPLE_CHECK', 'FIELD_CHECK']; S85 S2 result with reflection present: 12. C3 with real BASE section 4 but placeholder M criteria: []; M-7 row: | M-7 | item 7 | src |. C11 with no validator paragraph and all topics mapped to the same record-once sentence: []. All C1-C11 returned zero failures.","fresh":true}
```

Probe source and receipts are retained under `C:/Temp/av-kit/s85-review-probe.py` and `C:/Temp/av-kit/hdp85/review/`; decisive observations are embedded above. Upstream was read with a command-local `safe.directory` override following the sandbox ownership refusal; no git configuration was saved. All Python probes used `PYTHONDONTWRITEBYTECODE=1`.

## Verdict

`changes_required` — fix F1's unreachable prerequisite transition and F2's demonstrated false pass for missing human-only rules. Preserve the accepted substantive port, existing authorization, sequential session boundaries and uncommitted closeout. No human decision or new review apparatus is needed to make these corrections.

## Recheck (round 2)

**Date:** 2026-11-15. **Reviewer:** codex-independent-reviewer, class `avkit_independent_reviewer` (OpenAI); author: Claude Code (Anthropic). **Current verdict:** `changes_required`. **Intent assessment:** partial as an executable plan: the document design serves the goal, but a newly added required selftest fails against the corrected prerequisite.

### Prior Pass Summary

| Finding | Prior Status | Recheck Result |
|---|---|---|
| F1 | open | fixed |
| F2 | open | fixed |

### New Findings

| # | Severity | Blocking | Kind | Finding | File:Line | Recommendation | Status |
|---|---|---|---|---|---|---|---|
| F3 | High | yes | behavior | **The new prerequisite selftest stops a valid sequential port.** Confidence: High. Session 84's current `PORTED` fixture implements YAML escape decoding and passes its own `shape_problems`. Session 85's new selftest still removes the former two-line `def _quoted_scalar_text(raw): return None` stub by exact string replacement. That stub no longer exists, so the mutation changes nothing: the supposedly missing-function specimen is accepted, and the explicit unchanged-fixture assertion raises. The real command exits 1 before reaching the task/artifact arms. `baseline.ps1` invokes this selftest fail-fast, and the full session gate requires it too. Thus even after Session 84 closes correctly, row 0 cannot finish and AC-19 cannot pass; Session 85 and its dependent sessions stop. This is a new cross-session fixture incompatibility introduced by F1's correction, not a further variant of F2's false-pass probe. Violates **AC-19**. | `docs/execution/plans/2026-11-15-hdp-v2-protocol/s84-landed.py:105`; `s84-landed.py:113`; `baseline.ps1:73`; Session 84 `port-check.py:290`; `implementation-plan.md:308` | Remove or rename the named function independently of its implementation body, retaining the assertion that the fault actually changed the specimen. Run the existing 12-arm selftest against Session 84's current checker and keep the baseline/full-gate wiring. No validator edit or new gate is needed. | open |

### Confirmed fixes

- **F1:** `s84-landed.py:81` calls Session 84's own `port.run(root / VALIDATOR)`; `:83` checks its task statuses and `:85` its closeout artifacts. `baseline.ps1:39` invokes that gate. The obsolete `FIELD_CHECK`/`EXAMPLE_CHECK` label test is gone. In the executed selftest, the prerequisite's current positive fixture is accepted; the pre-port source and the other three half-ports are refused. This fixes the original false rejection. F3 separately prevents the new selftest itself from completing.
- **F2:** `hdp-check.py:220` defines fourteen row-specific criterion/source contracts; `:664` checks the criterion and Source cells separately; `:264` rejects upstream-only anchors. C11 (`:854`) reads fixed clauses/selectors from `TOPICS` (`:414`), not implementer-supplied evidence strings. All 46 selftest arms pass. Independent replay with the actual live BASE sweep and obviousness section accepts the substantive positive, refuses the old placeholder-M specimen with 42 failures, and refuses the old one-clause/one-arm binding with 47 failures.

### Q1 — Goal

**Accepted:** the decide-before-asking rule, recommendation-led plain brief with the C/do-nothing option, adapted M-list, and record-once stage logs each have an implementation row and AC family (AC-1–10/row 1, AC-11/row 3, AC-13/row 2, AC-14–16/rows 5–6). The revised oracle now rejects the demonstrated missing mandatory-human rules. Q1's research qualification is corrected: the 2–3-query instruction applies when web research is needed.

**Not accepted:** execution readiness until F3 is fixed. No missing product scope or additional MEU was established.

### Q2 — Upstream and av-kit adaptations

**Accepted:** comparison with the supplied upstream protocol and the actual `a73d6df` AGENTS/template/create-plan/model-delegation hunks supports the proposed port. Local sweep and receipt commands, Pomera ladder, hdp-only mode, local gate references and the five-note adaptation preserve the operative HD1 rules. The AGENTS sections/anchor, GUARDRAILS SIGN 3 and harness permission source exist. The §5a/hand-over omissions belong to Session 86; they are intentional. The live citation census still establishes no §7/§8 caller that renumbering would strand.

**Not accepted:** no additional upstream-loss finding was established.

### Q3 — Records and BINDING

**Accepted:** the corrected `S6_VALIDATOR` paragraph now names grouping Question/Reasoning checks, ruled Chosen/pending checks, comment stripping and quoted hashes. Its 24 fixed topics bind each described check to passing selftest arms/test prefixes; a drop requires the clause and all its evidence to be absent, and partial evidence stops under S2. The plan, handoff and declared grouping are supplied at H2-2. Reflection links/`None.` and optional, unchecked `mandatory:` accurately preserve the intended reader contract. VALIDATOR remains read-only here.

**Note, non-blocking:** Session 84 now also decodes YAML double-quoted escapes before blank/pending checks. Consider stating that explicitly in §6 when implementing the paragraph. Its current silence is not a blocking contract defect. The actual landed evidence must still be collected after Session 84 closes; this recheck does not certify its implementation.

### Q4 — AGENTS.md and the repin

**Accepted:** an in-memory application of `AGENTS_OLD` → `AGENTS_NEW` to the real file yields exactly **126 lines, 126 CRLF endings and 17,891 bytes**. The hard-gate qualification and do-nothing option remain. C7 checks the work-tree-byte digest repin; keeping `after_blocks` unchanged fits an in-place replacement. No old obligation is materially lost.

**Not accepted:** no additional AGENTS defect was established; no repository file was edited to obtain these measurements.

### Q5 — Inventory and templates

**Accepted:** the rechecked live call sites align with I8–I23, including old reflection reconciliation and old brief wording. No newly omitted live caller was established. The proposed four template changes preserve task columns/commands and the handoff YAML frame, while Session 84 removes reflection reconciliation first. Twin equality and line endings are checked. Saved task/template lint receipts pass; these are inspected planning evidence, not fresh post-edit results.

**Not accepted:** no template-delivery defect was established. Post-edit lint/closeout verification remains required during implementation, as the plan states.

### Q6 — Cross-session dependencies

**Accepted:** the production S2 check delegates to Session 84's checker, including its corrected escape-decoding probes, rather than inventing Session 84 identifiers. It also requires all recognized task statuses `[x]` and both closeout artifacts before collecting fresh EVIDENCE. Session 86's §4a rows, plain M-3 note, §6 overturn paragraph and Open decisions bullet are planned outputs. I15 changes only the `Topic too broad` row, matching Session 87's binding.

**Not accepted:** the separate S2 selftest is pinned to Session 84's former function body (F3). The prerequisite correction therefore breaks the sequential execution even though the actual port checker follows that correction correctly.

### Q7 — Checks and safety

**Accepted:** ORACLE, scope and identity selftests pass. The live oracle still returns the expected preimplementation Red: **132 failures**, with C5–C10 passing and C11 refusing the absent implementation binding. The ending snapshot covers all 28 EDITED files and the mixed model-delegation file. Scope selftests refuse outside edits, dirty-path content changes, VALIDATOR changes and moved HEAD; signing is disabled only for scratch-fixture commits. Identity ran only its synthetic selftest, avoiding real untracked configuration contents. Planned write destinations remain inside EDITED, plan-local/closeout paths or temp; AC-18 still protects VALIDATOR.

**Not accepted:** `s84-landed.py --selftest` exits 1 (F3); the claimed current 12-arm pass cannot be reproduced. No additional regex/completeness mutations are requested.

### Recheck evidence

All Python commands used `PYTHONDONTWRITEBYTECODE=1` and `PYTHONIOENCODING=utf-8`. Scratch-using selftests used TMP/TEMP `C:/Temp/av-kit/hdp85/review`. No network request, pytest, uv, npm, baseline execution or product suite ran. All reviewer writes stayed under `C:/Temp/av-kit`; protected paths were not opened. No canonical report or ledger was changed.

| Check | Result | Command or observed procedure | Exit | Decisive observation |
|---|---|---|---|---|
| PR-1/2/3/5/7/9; plan substance | pass | codex-independent-reviewer compared the current complete plan/task, upstream hunks, live inventory and adjacent-session contracts | null | Same scope/order, unstarted implementation, sourced ACs and valid later-session ownership; no new material document-contract ambiguity established. |
| F2 / PR-8 substantive oracle | pass | `rtk proxy python docs/execution/plans/2026-11-15-hdp-v2-protocol/hdp-check.py --selftest` | 0 | `all-green tree: 0 failure(s)`; F35–F41 refused; real drop accepted; `hdp-check selftest: 0 failures`. |
| F2 independent replay; Q4 size | pass | `rtk proxy python C:/Temp/av-kit/hdp85/review/r2-probes.py` | 0 | Correct protocol using live BASE sections: `[]`; placeholder M rows: 42 failures; one-clause/one-arm: 47 failures; AGENTS: 126 lines / 17,891 bytes / 126 CRLF. |
| F1 gate correction; F3 new selftest incompatibility | fail | `rtk proxy python docs/execution/plans/2026-11-15-hdp-v2-protocol/s84-landed.py --selftest` | 1 | Positive port accepted; `MISS half-port without _quoted_scalar_text refused: accepted`; `AssertionError: selftest fixture lacks _quoted_scalar_text in PORTED`. |
| Scope selftest | pass | `rtk proxy python docs/execution/plans/2026-11-15-hdp-v2-protocol/scope-check.py --selftest` | 0 | Eight observed checks; `scope-check selftest: 0 failure(s)`. |
| Identity synthetic selftest | pass | `rtk proxy python docs/execution/plans/2026-11-15-hdp-v2-protocol/identity.py --selftest` | 0 | Bound mutations invalidate prior state; closeout artifacts preserve it; `identity selftest: 0 failure(s)`. |
| Live Red and CRLF baseline | pass | `hdp-check.py --eol-snapshot C:/Temp/av-kit/hdp85/review/r2-eol.json`, then `--eol-baseline` with that path, both through `rtk proxy python` | 0 / 1 | 28 files, 28 CRLF, model-delegation mixed; expected 132 failures; C5–C10 ok. This is baseline observation, not a full Green pass. |
| Post-edit gates / product execution | n/a | Not run in this read-only plan recheck | null | Implementer's execution evidence is still pending. |

```json
{"schema_version":"evidence.v1","check_id":"s85-r2-prerequisite-selftest","command":"rtk proxy python docs/execution/plans/2026-11-15-hdp-v2-protocol/s84-landed.py --selftest","cwd":"P:/av-kit","scope":"Session 85 prerequisite gate selftest against Session 84's corrected port-check.py PORTED fixture","phase":"targeted","exit_code":1,"result":"fail","tested_state":"round-2-working-tree; s84-landed.py sha256 25fc80a2cf9c5334b75b570029d7c459a9cd999bb9b63a903d6db734507300d7; current prerequisite fixture implements YAML escape decoding","output":"ok port-check PORTED fixture passes: accepted; ok port-check PRE_PORT fixture refused: refused; MISS half-port without _quoted_scalar_text refused: accepted; other three half-ports refused; AssertionError: selftest fixture lacks _quoted_scalar_text in PORTED at s84-landed.py:114. Exact stub replacement at :105 leaves PORTED unchanged. Baseline invokes the selftest fail-fast at baseline.ps1:73.","fresh":true}
```

```json
{"schema_version":"evidence.v1","check_id":"s85-r2-original-false-passes-refused","command":"rtk proxy python C:/Temp/av-kit/hdp85/review/r2-probes.py","cwd":"P:/av-kit","scope":"C3 and C11 prior false-pass replay with actual live BASE sweep and section 4; AGENTS replacement measured in memory","phase":"targeted","exit_code":0,"result":"pass","tested_state":"round-2-working-tree; hdp-check.py sha256 fedc4c71a70bcc456da5497b2833d16082703260c8fa78f23461afb231125916; synthetic fixtures only","output":"C3 substantive positive with live BASE sweep and section 4: []; C3 prior placeholder-M exploit refused: 42 failures; C11 prior one-clause/one-arm exploit refused: 47 failures; planned AGENTS replacement: lines 126 bytes 17891 CRLF 126; 14 M-row contracts; 24 fixed section-6 topics; repository writes: none.","fresh":true}
```

Receipts and probe source remain under `C:/Temp/av-kit/hdp85/review/` with `r2-` prefixes. An initial run caught a transient syntax error while Session 84's checker was being edited; the subsequent stable failure above supersedes that observation. No finding is raised for that transient edit state.

### Verdict

`changes_required` — **F1 and F2 are fixed; F3 is the sole current blocker.** Repair the new selftest's stale function-body mutation and rerun it against the corrected Session 84 checker. Preserve the approved defaults, document scope, read-only VALIDATOR boundary, sequential session order and uncommitted closeout. No new human decision is needed for that correction. The coordinator saves this complete rolling report to the canonical destination and records the round-2 verdict.


## Recheck (round 3)

**Date:** 2026-11-15. **Reviewer:** codex-independent-reviewer, class `avkit_independent_reviewer` (OpenAI); plan author: Claude Code (Anthropic). **Current verdict:** `approved`. **Intent assessment:** yes, as an execution plan. The plan serves the registered goal; this approval does not certify implementation that has not run.

### Prior Pass Summary

| Finding | Prior Status | Recheck Result |
|---|---|---|
| F1 | fixed | fixed |
| F2 | fixed | fixed |
| F3 | open | fixed |

### New Findings

| # | Severity | Blocking | Kind | Finding | File:Line | Recommendation | Status |
|---|---|---|---|---|---|---|---|

None. This final recheck found no concrete failure introduced or exposed by the F3 correction.

### Confirmed fix and review boundary

F3 is fixed at `docs/execution/plans/2026-11-15-hdp-v2-protocol/s84-landed.py:92–145`. `_def_span` locates the named top-level function with `ast`; `_rename_def` changes its name independently of its body, and `_edit_def` confines call replacements to the named function. Each of the four half-port specimens must differ from `PORTED` before it is checked. This removes the obsolete exact-body dependency while retaining the negative assertions. Session 84's current `_quoted_scalar_text` has the multi-line YAML escape decoder that exposed F3, and all twelve arms now complete successfully against that current fixture. `baseline.ps1:73` still invokes the selftest through fail-fast `Invoke-Step`; the planned full session gate also retains it.

This is the final permitted round and a bounded correction recheck. The round-2 accepted substantive assessments remain accepted; this pass independently inspected the correction, reread the plan/task and gate wiring, and reran the two required selftests. It did not repeat all round-1/2 sweeps or claim fresh implementation evidence. No materially different failure was established.

### Q1 — Goal

**Accepted:** the prior mapping remains sound: AC-1–10/row 1 establish the protocol, AC-11/row 3 align AGENTS, AC-13/row 2 update the four template families, and AC-14–16/rows 5–6 update live callers. Recommendation-led plain words, the do-nothing option, the mandatory-human list and stage-local record-once rules remain explicit. The corrected required selftest no longer prevents executing those rows.

**Not accepted:** no new omission established. Approval is of the plan, not a claim that the live rules have already changed.

### Q2 — Upstream and av-kit adaptations

**Accepted:** carry forward the round-2 upstream comparison: local sweep/research commands, hdp-only mode, av-kit M-row sources and local gate references preserve the scoped HD1 rules. Session 86 still owns the stated expert-pass/hand-over additions. The F3 correction changes no protocol wording or citation inventory.

**Not accepted:** no new loss or contradictory adaptation established; the upstream comparison was not rerun in this bounded pass.

### Q3 — Records and BINDING

**Accepted:** the fixed `S6_VALIDATOR`/24-topic BINDING approach still covers grouping fields, pending choices, comment stripping and quoted hashes, reflection link lists, source grammar and optional unchecked `mandatory:`. Fresh landed `EVIDENCE` remains required before binding. Partial evidence stops under S2; VALIDATOR stays read-only. The hdp-check selftest again accepts the substantive positive and real drop, and refuses the one-clause and failed-evidence faults.

**Not accepted:** no new record-shape discrepancy exposed by this correction. No landed-validator behavior is certified by these synthetic selftests.

### Q4 — AGENTS.md and repin

**Accepted:** the in-place sentence replacement, unchanged line/block count, byte cap and work-tree-byte digest repin remain the reviewed approach. The correction touches none of these contracts; the oracle again refuses the old sentence, extra line and stale pin faults.

**Not accepted:** no new dropped obligation or size failure established. The earlier measured size is historical evidence, not a fresh measurement here.

### Q5 — Inventory and templates

**Accepted:** the round-2 edited/no-edit inventory and template-consumer assessment stand. This correction adds no live protocol caller and changes no template. The repeated oracle selftest accepts its all-green fixture and refuses stale-template, twin and handoff-shape faults.

**Not accepted:** no additional omitted file established. Actual post-edit lint/closeout results remain execution obligations; they were not run in this review.

### Q6 — Cross-session dependencies

**Accepted:** S2 still uses Session 84's own port checker, all-done task statuses and both closeout artifacts, followed by fresh behavior receipts. The repaired selftest accepts the current positive fixture and refuses the pre-port and all four half-ports. Session 86's named M rows, exact M-3 note, overturn paragraph and Open decisions bullet remain specified. Session 87's `Topic too broad`-only edit boundary is unchanged.

**Not accepted:** no new cross-session incompatibility established. Passing this selftest does not mean Session 84 is already closed; the real S2 gate remains required before execution.

### Q7 — Checks and safety

**Accepted:** independent reruns produced 12/12 s84-landed arms and 46/46 hdp-check arms with zero failures and exits 0. The CRLF rule, EDITED scope and AC-18 read-only VALIDATOR boundary remain unchanged. The AST helper is used for synthetic selftest text only and introduces no repository write.

**Not accepted:** no new concrete safety or false-pass failure established. No pytest, uv, npm, network request, baseline execution or product gate ran. Python bytecode was disabled, TMP/TEMP were under `C:/Temp/av-kit/hdp85/review`, and all writes stayed under `C:/Temp/av-kit`. Protected paths were not opened. Completion-preflight was consulted for artifact checks; pending implementation rows belong to the author, outside this read-only review's authority.

### Recheck evidence

| Check | Result | Command or procedure | Exit | Decisive observation |
|---|---|---|---|---|
| F3 / AC-19 | pass | `rtk proxy python docs/execution/plans/2026-11-15-hdp-v2-protocol/s84-landed.py --selftest` | 0 | Positive port accepted; PRE_PORT and all four changed half-ports refused; completed/open/blocked/absent task cases and present/missing artifact cases behaved as expected; `s84-landed selftest: 0 failures`. |
| F2 regression / ORACLE | pass | `rtk proxy python docs/execution/plans/2026-11-15-hdp-v2-protocol/hdp-check.py --selftest` | 0 | `all-green tree: 0 failure(s)`; all 46 arms successful, including F35–F41 and the fixed plan-quote check; `hdp-check selftest: 0 failures`. |
| PR-1–PR-9 / bounded correction inspection | pass | codex-independent-reviewer reread current plan/task and inspected AST mutation helpers, current prerequisite fixture and baseline/full-gate wiring against historical F3 | null | Correction removes the stale-body dependency, preserves changed-fixture assertions and remains wired to required checks; no new material failure established. Previously accepted source/scope checks carried forward. |
| Actual landed prerequisite, post-edit template lint and full execution gate | n/a | Outside this read-only plan recheck | null | Required during execution; not represented as passed by this review. |

```json
{"schema_version":"evidence.v1","check_id":"s85-r3-prerequisite-selftest","command":"rtk proxy python docs/execution/plans/2026-11-15-hdp-v2-protocol/s84-landed.py --selftest","cwd":"P:/av-kit","scope":"F3 correction against current Session 84 port-check.py PORTED fixture","phase":"targeted","exit_code":0,"result":"pass","tested_state":"s84-landed.py sha256 4bcc84a6131103b2a7d82113e5bed4a737cf9edbe37759fab50bd12b49a44946; current prerequisite multi-line YAML decoder fixture; synthetic selftest only","output":"12 arms successful. PORTED accepted; PRE_PORT refused; missing _quoted_scalar_text, upstream _unquote, restored DECISIONS_LOG_HEADERS and skipped grouping_row_problems half-ports refused. All task/artifact arms complete. s84-landed selftest: 0 failures.","fresh":true}
```

```json
{"schema_version":"evidence.v1","check_id":"s85-r3-oracle-selftest","command":"rtk proxy python docs/execution/plans/2026-11-15-hdp-v2-protocol/hdp-check.py --selftest","cwd":"P:/av-kit","scope":"ORACLE synthetic positive and negative fixtures, including prior F2 faults","phase":"targeted","exit_code":0,"result":"pass","tested_state":"hdp-check.py sha256 fedc4c71a70bcc456da5497b2833d16082703260c8fa78f23461afb231125916; synthetic selftest only","output":"all-green tree: 0 failure(s); 46 successful arms; M criterion/source faults, one-clause binding, failed receipt selectors and unknown topic refused; hdp-check selftest: 0 failures.","fresh":true}
```

Unfiltered receipts: `C:/Temp/av-kit/hdp85/review/r3-s84-selftest.txt` and `r3-hdp-selftest.txt`. Decisive output and preserved exits are embedded above.

### Verdict

`approved` — F1, F2 and F3 are fixed. The plan is ready for the authorized sequential execution after Session 84 closes. Execution remains uncommitted, with a commit-message draft. The coordinator copies this complete rolling report to the canonical path and records the round-3 verdict; this reviewer changes neither repository files nor the ledger.
