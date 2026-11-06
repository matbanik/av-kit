---
date: "2026-11-05"
review_mode: "plan"
target_plan: "docs/execution/plans/2026-11-05-closeout-register-grammar/implementation-plan.md"
verdict: "changes_required"
findings_count: 2
template_version: "2.2"
requested_verbosity: "standard"
agent: "codex-independent-reviewer"
loop_id: "s49b-plan-2026-11-05-closeout-register-grammar"
round: 1
---

# Critical Review: closeout-register-grammar

> **Review Mode:** `plan`
> **Verdict:** `changes_required`

## Scope

**Intent anchor:** Session 49b makes the closeout check read `known-issues.yaml` exactly as `model.save` writes it, for every issue a session names, so Sessions 50 to 57 close without an extract.

**Intent achieved:** `partial`, as plan readiness. The proposed format works for today's complete register, but not every model-valid nested sequence; the rewrite can silently discard a concurrent register edit.

**Target:** working-tree plan, task and `register-rewrite.py`, on `main`, HEAD `19001ca7ee19e4cdd2bf293782d69216bec5d7a9`. **Review Type:** independent plan review, ledger round 1; class `avkit_independent_reviewer`. Claude Code / Anthropic authored the work; Codex / OpenAI did not. **Checklist Applied:** PR-1 through PR-9, with the user's materiality and paperwork exclusions.

Accepted as given: D-274, D-280, the D-285 human gate, scheduled helper creation, the token-calibration flag and squashed history. No approval of D-285's wording is supplied here. All writes were confined to `C:/Temp/av-kit`; no pytest, session gate, repository-writing command, commit or push ran. No prohibited secret or fleet-hub file was opened.

Reviewed SHA-256: plan `acafc382e0ec375e4fbf1be432a105c9d1222221f1e84b4ab257685d9a5741d4`; task `a1ee5d10f37905757300ea48d9dc9451a56fa7c2bef780e1de9b15d227948afa`; rewrite script `48e0cb142f0d4e23de194a0b56e4f53fe1edf6e5e9167684a3d79db1c919ce8f`. The real register remained at `900b2cb05e7266fad83f329e555f1da135f6268da39662a80dc35f60a12d8fe4` throughout the probes.

Output preflight: `rtk proxy python -B C:/Temp/av-kit/s49b-review-output-check.py`, exit 0. The verdict validates against the repository v2 schema; report metadata, complete intent, Q1–Q8 and PR-1–PR-9 agree; all three reviewed files and the register retain the hashes above. Completion-preflight was consulted for the review artifact; the implementation task remains intentionally unstarted under the user's read-only boundary.

## Findings

| # | Severity | Blocking | Kind | Finding | File:Line | Recommendation | Status |
|---|---|---|---|---|---|---|---|
| F1 | High | yes | control-defeat | Confidence: High. `--expect-sha256` checks before loading; nothing protects the subsequent read/write interval. A concurrent save after `model.load` is overwritten, and the comparison against the stale in-memory original reports success. A temp-register probe inserted another writer's valid note immediately before the planned save: the note disappeared, yet the exact rewrite entrypoint exited 0 with `parsed fields changed: 0 (planned 0)` and `register-rewrite: 0 problem(s)`. S4's between-row checks cannot detect an edit overwritten within an allowed writing row. This defeats AC-9's value-preserving reformat for another session using the shared register. mechanism: task-row-completion-predicate | `docs/execution/plans/2026-11-05-closeout-register-grammar/register-rewrite.py:252`, `:257`, `:277`; `task.md:36` | Protect the expected-hash read through replacement with an actual exclusive-write mechanism, and stage/validate output before replacing the register. Cover rows 4, 5 and 7; demonstrate that an intervening writer is refused or preserved. Rechecking a hash without protecting the final replacement still leaves a race. | open |
| F2 | High | yes | behavior | Confidence: High. The proposed `increase_indent(indentless=False)` does not prevent PyYAML's compact nested-sequence form. A schema-valid decision value containing `[["alpha", "beta"], ["gamma"]]` is emitted as `- - alpha` followed by an indented `- beta`. Both the whole-file grammar and `issue_decision_log` refuse it as unexpected indentation. `validate_strict` accepts the value and `model.load` reads it back equal. A later session recording such a value still cannot close against the saved register. This contradicts AC-1's every-sequence grammar contract. | `docs/execution/plans/2026-11-05-closeout-register-grammar/implementation-plan.md:106`, `:213` | Extend the writer design and AC-1 regression to a sequence inside a sequence in a decision item. Emit a supported noncompact or single-line flow representation while preserving parsed values and keeping D-282's reader strict. Include the string/key limitations in Q2 when completing the writer's edge policy. | open |

## Checklist Results

### Information Retrieval (IR)

Manual observations throughout this report have observer `codex-independent-reviewer` and `exit_code: null`.

| Check | Result | Procedure | Exit | Evidence |
|---|---|---|---|---|
| Target and unstarted state | pass | Read the three targets; inspect scoped Git status and handoff existence | null | Plan folder is untracked; implementation rows are unchecked; implementation handoff is absent. |
| Sources and scope | pass | Look up the tracking issue by ID; compare grouping 49b/§8, HDP §6 and Session 49 H2-2 | null | D-279/D-274 are the issue's two triage decisions; no MEU is introduced; done-proof source set agrees. |

### Design Review (DR): Q1–Q8

**Q1 — Delivery. Accepted for today's register; incomplete for future writer input (F2).** All normal CLI writers use `model.save`: add, deep verify, discover, promote, dismiss and migrate. The separate `triage.py` dump writes only triage output. The targeted writer/caller census found no second active register serializer. Tests and other consumers found in the sweep use parsed data or the model; no register-layout text expectation was found. Rendered Markdown was byte-equivalent after the proposed rewording, after text newline normalization. A hand edit can still reintroduce indentless/wrapped YAML or placeholder-shaped decision text; D-282 intentionally does not make arbitrary hand-written YAML acceptable. No extract should be needed for the current 67 logs after the intended changes, provided F1 is fixed.

**Q2 — Writer. Partly accepted; F2 blocks its claimed closure over sequences.** I independently implemented the described dumper only in a temp probe, without modifying `model.py`. Indentation, disabled aliases, huge width, literal multiline strings, the two-newline double-quote rule and PyYAML's tab/CRLF/trailing-space fallback reproduce the advertised register output. Dates, datetimes, ints, floats, booleans and null as decision metadata passed grammar, reader and model round-trip checks. Numeric, boolean, null and date mapping keys passed too. A list containing mappings with nested string lists passed.

Three limits remain: a sequence containing sequences fails as F2 demonstrates; empty or multiline mapping keys are emitted with explicit `?`/`:` key notation, which the grammar refuses; U+0085, U+2028 and U+2029 in strings produce quoted scalars split by the reader's `splitlines()` and are refused. U+0085 also loads back as a space rather than the original character. These keys/characters are not present in the measured register and the Unicode normalization is also reproducible with today's writer, so they are recorded here without separate blocking findings. They warrant an explicit writer edge policy, not a claim that every possible model-valid value was tested. Preserve D-282; quoting these special strings is possible without loosening the reader.

**Q3 — Strict reader. Accepted.** Keeping the bounded grammar and placeholder refusal is consistent with D-282. On the proposed current-register output, the unchanged reader returns every expected `(id, stage)` pair: 61 logs after reformat, with exactly six placeholder-only refusals; all 67 after reword. F2 requires a writer correction, not a reader relaxation.

**Q4 — Repeatable flag. Accepted as designed.** Append preserves command order; reading each issue separately preserves labels and per-issue repeated-ID checks; the existing aggregate stage check must remain across the merged entries. The existing absent-issue exception must propagate for each issue, and the no-register-source refusal remains. All changed-signature callers found are in the validator; existing selftest arms reach them via argparse. The usage docstring, CLI help and protocol paragraph are the documentation needing changed semantics. The two task templates' one-flag examples remain valid. Today's CLI independently exited 0 for missing-first-decision, duplicate-flag and absent-first-issue cases, proving the proposed AC-4/5/6 negative fixtures can distinguish the current defect. The single-flag control exited 0. These are Red feasibility probes, not Green certification of unwritten code.

**Q5 — Rewrite and wording. Parsed comparison accepted; concurrent safety rejected (F1).** A deliberately mutated saved title caused exit 1 with its exact parsed path; a wrong expected hash caused exit 1 before saving. All current string-keyed parsed values are compared, with scalar types checked, and the actual target is read back. The 61/67 counts are correct; full input hashing plus iteration over every loaded log makes hard-coded count assertions unnecessary. Against the prototype, reformat changed zero parsed fields and reword changed exactly 15. No remaining log was refused as a placeholder. The actual reader also scans raw decision text, complementing `_strings`' value scan.

Each rewording preserves the recorded meaning, subject to Mat's D-285 ruling:

| Rewording numbers | Decision/field | Meaning assessment |
|---|---|---|
| 1 | D-15 chosen | Capture ID, inbox, stem, timestamp form, backup/revert and settings behavior preserved. |
| 2–3 | D-42 chosen; D-44 chosen | Voice-ID filename and job-ID cancellation path preserved. |
| 4–6 | D-47 chosen, precedents[1], reasoning | Dollar-brace environment expansion and main-process token boundary preserved in each field. |
| 7–9 | D-49 question, chosen, reasoning | Expansion question, app-data token-file location, prompt-only supersession and env-var reasoning preserved. |
| 10–11 | D-52 chosen; D-53 chosen | Result-line values, backup filename, UTC timestamp, merge and conditional restart preserved. |
| 12–13 | D-57 precedents[0]; D-58 chosen | Home-folder fallback and dependency-health result/error semantics preserved. |
| 14–15 | D-72 chosen; D-227 precedents[1] | Pinned SHA lookup and `a:` stream-index construction preserved. |

**Q6 — Red tests and guards. Accepted except F1.** Old-save probes show unindented lists refused and long spaced strings wrapped, while round-trip equality holds; AC-1/2 can fail by assertion as planned. AC-4/5/6 currently produce the incorrect exit 0; AC-3/7 are sensible positive guards. The copied `red-check.py` inspects actual assertion diagnostics and requires each selected test's failure, including the digit-boundary protection. The selftest is genuinely reached by `test_evidence_contract_real_cli_selftests` (`tests/tooling/test_framework_adoption.py:167–171`). The scheduled Session-49-shaped gate propagates blocking failures and compares identities. No additional material false pass was demonstrated in those rows. F1 is a concrete false pass in rows 4/5, not a predicate-format objection.

**Q7 — Done-proof. Accepted.** Task row 6 is Session 49's H2-2 reflection-validation command with the extract source replaced by the register and the two issue selections combined; reflection, template, schema, plan, handoffs and grouping remain the same. Today's exact command exits 1 on FFMPEG-LIBDVDCSS-BUNDLED's nested-list YAML, matching row 0's expected diagnostic. Against the reworded prototype, the unchanged single-issue CLI passes both source sets, reconciling 24 and 27 decisions against the existing 28 reflection rows. Their union is the intended combined proof after the flag implementation; no future combined Green run is claimed. The whole-register rewrite check and AC-4 distinguish this proof from accidentally checking only the last issue.

**Q8 — Order and safety. Partly accepted; F1 blocks.** Rows are ordered Red → writer/flag Green → reformat → reword → done-proof → resolution. Expected hashes reject edits completed before the check, but S4 and a pre-load hash do not provide atomicity against an edit during a write row. Moreover, validation currently follows the live save, so a detected bad serialization has already replaced the register; staging first is needed to make S5's “last good save” assurance true. Row 7's specified status/verification/resolution fields passed `validate_strict` in a temp-data probe. Rewording leaves the Markdown render unchanged; resolution is expected to move this issue to archived in triage output and change rendered status/counts. Triage output keeps its existing serializer. No task row commits, pushes, publishes or performs another outward action; H2-5 only prepares a message.

### Plan Review (PR)

| Check | Result | Procedure/evidence |
|---|---|---|
| PR-1 Plan/task alignment | pass | Compared work packages and rows 0–7/H1/H2: same changes and order. |
| PR-2 Not started | pass | Unchecked rows, untracked plan folder, no implementation handoff. |
| PR-3 Task contract | pass | Read rows: owners, deliverables, exact commands and dependencies are specified. |
| PR-4 Validation realism | fail | Writer probe demonstrates F2; future nested sequences are absent from the proposed test inventory. |
| PR-5 Source-backed planning | pass | Compared Mat's request, issue D-274/D-279, grouping and HDP §6 with the FIC. |
| PR-6 Corrections readiness | pass | Read named handoff/review targets and task dependencies; first round has no correction census due. |
| PR-7 Scope discipline | pass | Reviewed out-of-scope table: strict reader and triage-output exclusions are justified; Session 50's MEUs are named. |
| PR-8 Reachability and negative oracles | fail | Actual rewrite entrypoint loses a concurrent edit and returns success (F1). |
| PR-9 Shared predicates | pass | Compared named REGISTER/REWRITE/DONE_PROOF and task references; no material delivery failure from repetition. |

Post-implementation certification: `n/a`. Product test/build gates were not run, as requested.

### Durable observations

```json
{"schema_version":"evidence.v1","check_id":"s49b-plan-r1-writer","command":"rtk proxy python -B C:/Temp/av-kit/s49b-review-probe.py","cwd":"P:/av-kit","scope":"planned dumper in memory, actual register loaded read-only, temp targets only","phase":"static","exit_code":0,"result":"fail","tested_state":"HEAD 19001ca; plan/task/script hashes in Scope; register sha256 900b2cb05e7266fad83f329e555f1da135f6268da39662a80dc35f60a12d8fe4; PyYAML 6.0.3","output":"Probe completed, but writer contract failed: nested-sequence equal=True; whole grammar Refuse unexpected indentation before '- beta'; issue reader Refuse same. Empty/multiline keys and Unicode line separators also refused; U+0085 equal=False. Current-register reformat: 61 of 67 logs, 0 parsed changes, exit 0; reword: 67 of 67, exactly 15 changes, exit 0. REGISTER_UNCHANGED True.","fresh":true}
```

```json
{"schema_version":"evidence.v1","check_id":"s49b-plan-r1-controls","command":"rtk proxy python -B C:/Temp/av-kit/s49b-review-controls.py","cwd":"P:/av-kit","scope":"real validator CLI on temp fixtures and read-only Session 49 reflection; rewrite entrypoint with REGISTER and --target both under C:/Temp/av-kit","phase":"static","exit_code":0,"result":"fail","tested_state":"Same reviewed inputs as writer observation","output":"Probe completed, but safety contract failed: RACE_REWRITE_EXIT 0; RACE_CONCURRENT_VALUE_SURVIVED False; parsed fields changed: 0 (planned 0); register-rewrite: 0 problem(s). Mutated saved title: exit 1 with .issues[0].title diff. Wrong expected hash: exit 1, nothing written. AC4/5/6 today: exit 0; AC7 single: exit 0. Actual DONE_PROOF today: exit 1, second issue not valid YAML. Prototype per-issue done proofs: exit 0, 24 and 27 decisions. ROW7_VALIDATE_STRICT pass; REGISTER_UNCHANGED True.","fresh":true}
```

```json
{"schema_version":"evidence.v1","check_id":"s49b-plan-r1-source-review","procedure":"Compare the working-tree plan/task/script with save/load/strict validation, every register-writing CLI branch and migrate, reader/reconciliation/argparse/selftest call chains, the named planning receipts, HDP §6, grouping §6/§8 and Session 49's closing artifacts; assess all 15 before/after replacements.","observer":"codex-independent-reviewer","cwd":"P:/av-kit","scope":"Q1-Q8; PR-1 through PR-9 within the explicit review exclusions","phase":"static","exit_code":null,"result":"pass","tested_state":"HEAD 19001ca; working-tree target hashes in Scope","output":"All active normal register writers route through model.save; the separate triage dump does not write the register. All changed-signature callers found are internal to the validator. Wording preserves meaning in all 15 fields, pending Mat's ruling. Source set and planned Red reasons match the actual validator. No repository mutation or product-suite execution.","fresh":true}
```

## Verdict

`changes_required` — two evidence-backed High findings: the rewrite can falsely certify a lost concurrent edit (AC-9), and the proposed writer still emits nested sequences the unchanged reader refuses (AC-1). Correct those plan behaviors and their negative probes. The normal register format, repeatable-flag semantics, all 15 wording replacements and Session 49 done-proof are otherwise accepted.

Residual risk: arbitrary hand edits can bypass the writer; unusual model-valid keys and Unicode line separators need the explicit policy described in Q2. Current-register prototype results do not certify the unwritten production changes or full gate. The reviewer stops here; the coordinator saves this report to the canonical rolling path and records the verdict.


---

<!-- Round 2, appended by the coordinator from C:/Temp/av-kit/s49b-plan-review-round-2.md, unedited -->

---
date: "2026-11-05"
review_mode: "plan"
target_plan: "docs/execution/plans/2026-11-05-closeout-register-grammar/implementation-plan.md"
verdict: "approved"
findings_count: 0
template_version: "2.2"
requested_verbosity: "standard"
agent: "codex-independent-reviewer"
loop_id: "s49b-plan-2026-11-05-closeout-register-grammar"
round: 2
---

# Critical Review: closeout-register-grammar

> **Review Mode:** `plan`
> **Verdict:** `approved`

## Scope

**Intent anchor:** Session 49b makes the closeout check read `known-issues.yaml` exactly as `model.save` writes it, for every issue a session names, so Sessions 50 to 57 close without an extract.

**Intent achieved:** `yes`, as plan readiness. Executing the revised plan delivers the stated register and repeatable-flag path. This is not certification of unwritten implementation or its future full gate.

**Target:** the working-tree plan, task and `register-rewrite.py`, on `main`, HEAD `19001ca7ee19e4cdd2bf293782d69216bec5d7a9`. **Review Type:** independent review, ledger round 2; class `avkit_independent_reviewer`, Codex/OpenAI reviewing Claude Code/Anthropic's plan. **Checklist Applied:** PR-1–PR-9 and Q1–Q8, subject to Mat's explicit substance-only scope and given exclusions.

Read the round-1 report first; carried forward its unchanged Q3/Q4/Q7 and wording acceptance, checking interactions with the corrections. Looked up the tracking issue by ID, including D-279/D-274. D-274, D-280 and the D-285 human gate remain given. No repository writes, pytest, session gate, commits, pushes, dispatches, or prohibited secret/fleet-hub reads occurred. All scripts and generated files are under `C:/Temp/av-kit`; Python ran with `-B`. The implementation remains unstarted.

Reviewed SHA-256: plan `2b9f7407c2a2baea39aedc322380ce47bd31c13618adf433bfdcf2eeb77fab32`; task `c0fa72875856137e644bd4ebc05d5f36912203f7d7e34a3e627c782d64e753b8`; rewrite `292809d02bbcc99c540c304d7af053a51af8b8287dcc4317a71b6f237c09abf1`; register `900b2cb05e7266fad83f329e555f1da135f6268da39662a80dc35f60a12d8fe4`.

## Findings

No new blocking finding. Both prior High findings are closed:

| Prior finding | Recheck | Evidence and current location |
|---|---|---|
| F1 — concurrent edit overwritten, AC-9; mechanism: task-row-completion-predicate | fixed | `register-rewrite.py:188` opens with read/write access and only `FILE_SHARE_READ`; `:332` holds that handle around the complete rewrite; `:341` hashes its first read. `:378` saves the stage, `:381`–`:394` validate it, and `:395`–`:398` write/read back through the handle. Independent temp-copy probes refused a pre-existing writer, a wrong hash and a changed staged `.version`; the latter left the register copy untouched. A subprocess attempting `open('w')` mid-run received `PermissionError`, while the successful rewrite retained exactly the staged bytes. Row 7 now uses this same protected path (`task.md:50`), bound to row 5's hash. |
| F2 — compact nested sequence refused, AC-1 | fixed | `implementation-plan.md:107` requires the noncompact emitter override, now covered by AC-1 (`:233`). The revised dumper passes the actual grammar and issue reader for nested sequences, three levels of lists, empty inner lists and mappings inside nested lists, with equal parsed values. The adjacent Unicode separator/key policy is explicit at `:110`–`:115` and AC-2 (`:234`); probes preserve U+0085/U+2028/U+2029 and refuse empty/multiline keys before opening the destination. |

These are plan corrections supported by executable temp probes; production `model.save` has intentionally not been edited yet.

## Checklist Results

Manual observations have observer `codex-independent-reviewer` and `exit_code: null`.

### Information Retrieval (IR)

| Check | Result | Procedure | Evidence |
|---|---|---|---|
| Target/state | pass | Read working-tree plan/task/script; inspect Git status and current production writer/argparse | Correct branch/HEAD; unchecked implementation rows; production behavior still reproduces Red. Unrelated untracked paths were left alone. |
| Source/intent | pass | Compare issue by ID, grouping 49b/§6/§8, HDP §6, Session 49 H2-2 and closing artifacts | Scope and source set match Mat's request; no MEU or new outward action. |

### Design Review (DR): Q1–Q8

**Q1 — Delivery: accepted.** All normal register-writing CLI branches and migration route through `model.save` (`tools/issue_triage.py:143,159,163,286,307,330`; `tools/issue_triage/migrate.py:233`). `triage.py:65` writes a different file. The writer/caller sweep and unchanged round-1 consumer review identify no register-text-layout dependency requiring preservation. The revised output is byte-identical to the measured prototype and retains parsed values. Normal subsequent saves retain that format. Arbitrary hand edits or a new bypass writer can still reintroduce unsupported YAML or placeholder text; this plan intentionally does not make all hand-written YAML acceptable. See Q2's bounded residual limit.

**Q2 — Writer: accepted for the register and specified edge set.** Indentation, disabled aliases, effectively unbounded width, literal multiline values and the two-newline rule conform to the strict reader. The noncompact sequence override closes F2. Independent probes passed dates/datetimes, ints, floats, booleans/null, scalar mapping keys, nested lists and maps, CR/tab/trailing spaces, trailing newlines and the three Unicode separators. Each reads back equal and its decision is read. Key refusals preserve existing destination bytes; the pre-open round-trip check protects against value normalization.

This is not a universal guarantee over arbitrary extra metadata keys: a 128-character string key (`'x' * 128`) is accepted by `validate_strict`, loads back equal, but PyYAML emits explicit `? key` notation and the bounded grammar refuses it. None occurs in the measured register; fixed schema keys are short. Record this as a residual on the already-reviewed key-policy surface, not a new High delivery defect or a request for another round of nearby key mutations (Materiality Gate #4). A future need for such keys should extend the writer's refusal/representation policy. The unchanged reader should remain strict.

**Q3 — Reader strictness: accepted, unchanged.** D-282 is appropriate. The real reader returns the entire expected ID/stage list for each successfully read log. Reformat reads 61 of 67, with only the six explicitly allowed placeholder refusals; reword and resolve read all 67. No reader relaxation is needed for this register.

**Q4 — Repeatable flag: accepted, unchanged.** Append preserves order; every selected issue must be read and labeled separately, duplicate flags are Usage/2, and an absent issue must refuse even when another exists. Per-issue repeated-ID checks and aggregate stage agreement remain necessary. The call chain is argparse → `check_reflection` → `check_decisions_log` → `decision_sources` → `issue_decision_log`; the changed-signature callers found are internal to the validator. The usage/help and protocol paragraph are scheduled; both task templates' single-flag examples remain valid. Independently repeated the old CLI's incorrect exit 0 for AC-4/5/6 fixtures and its correct single-flag exit 0. No Green result is claimed for the unwritten append implementation.

**Q5 — Rewrite/wording: accepted.** The script loads retained original bytes and the staged file, compares parsed paths/types and planned changes, checks the full grammar and every log, and then writes the stage through the held handle. A staged `.version` mutation returned 1 before changing the register copy; wrong hashes likewise refused. The valid chain changed exactly 0, 15 and 3 fields. The 61/67 counts are correct. Every log was checked; no placeholder remained after reword.

The same 15 replacements retain round-1 acceptance of meaning and completeness, subject to Mat's D-285 ruling:

| Numbers | Record | Meaning retained |
|---|---|---|
| 1 | D-15 chosen | Capture ID, inbox/stem/timestamp, backup/revert and settings |
| 2–3 | D-42/D-44 chosen | Voice filename and cancellation job ID |
| 4–6 | D-47 chosen, precedents[1], reasoning | Dollar-brace expansion and main-process token boundary |
| 7–9 | D-49 question, chosen, reasoning | Expansion question, app-data token file, prompt-only supersession and reasoning |
| 10–11 | D-52/D-53 chosen | Result values, backup filename/timestamp, merge and conditional restart |
| 12–13 | D-57 precedents[0], D-58 chosen | Home-folder fallback and dependency-health/error semantics |
| 14–15 | D-72 chosen, D-227 precedents[1] | Pinned SHA lookup and `a:` stream-index construction |

**Q6 — Red/guards: accepted, with one stale note.** The current writer fails the intended indentation/wrapping contract; unchanged CLI fixtures reproduce AC-4/5/6's incorrect success. Each can fail by assertion as required and become Green after its owning change. The expanded writer cases exercise F2 directly. `red-check.py` inspects failure diagnostics and accepts additional legitimate assertion failures; its required-name matching does not confuse AC-1 with AC-10. The full-suite peer actually invokes the validator selftest (`test_framework_adoption.py:167`–`:171`). The described gate propagates failures and checks identity; no additional material false pass was demonstrated.

Clerical correction: `implementation-plan.md:235,318` and `task.md:42` call AC-3 a passing Red guard, but its expanded edge set now includes U+0085. Today's writer loads `a\x85b` back as `a b`, so that AC-3 case also fails in Red. Keep its equality assertion; describe this as an additional intended Red. Row 1's checker does not require AC-3 to pass, so this stale label neither blocks the workflow nor weakens its required Red proofs.

**Q7 — Done-proof: accepted.** Row 6 preserves Session 49 H2-2's reflection/template/schema/plan/two-handoff/grouping inputs, replaces the extract with the register, and combines the two issue flags. The exact current command, independently rerun with `-B`, exits 1 on FFMPEG-LIBDVDCSS-BUNDLED's invalid-YAML log: row 0's intended reason. Against the temp rewritten register, the unchanged single-flag CLI passes both individual source sets, reconciling 24 and 27 decisions against the existing 28 rows. These are compatibility probes; row 6 must still supply the combined Green proof after append is implemented. AC-4 prevents a last-flag-only false proof.

**Q8 — Order/safety: accepted.** Red → writer/flag Green → reformat → reword → done-proof → resolution is coherent. S4 plus mandatory expected hashes handles changes between rows, and the held deny-write handle handles the within-row lost-update case. Row 7's three-field resolve passes `validate_strict`. Rewording leaves rendered Markdown unchanged. In temp triage output, resolving the issue moves it from actionable to archived: 42→41 actionable, 64→65 archived, 6 deferred unchanged. This matches the intended records change. Triage output retains its existing serializer. No row commits/pushes or authorizes another irreversible outward action; the human execution/wording gate remains.

### Plan Review (PR)

| Check | Result | Procedure/evidence |
|---|---|---|
| PR-1 Plan/task alignment | pass | Compared work packages, ACs, rows and S4/S5: same scope, changes and dependency order. |
| PR-2 Not started | pass | Read unchecked rows and reproduced unchanged production writer/flag behavior. |
| PR-3 Task contract | pass | Owners, deliverables, validations and dependencies are specified. |
| PR-4 Validation realism | pass | Real temp-copy rewrite, writer-edge and CLI probes support the corrected plan; future Green checks are not presented as executed. |
| PR-5 Source-backed planning | pass | Compared Mat's request with issue/grouping/HDP and FIC sources. |
| PR-6 Corrections readiness | pass | Both findings are traceably corrected; handoff and independent-review targets exist as planned destinations. Procedural census/paperwork gating is outside Mat's explicit substance-only review. |
| PR-7 Scope discipline | pass | Strict-reader and separate triage serializer exclusions are justified; Session 50's MEUs are named. |
| PR-8 Reachability/negative oracles | pass | Actual rewrite entrypoint refuses wrong hash, occupied handle and staged value change; subprocess writer cannot defeat the held handle. Required CLI negatives reproduce today's defect. |
| PR-9 Shared predicates | pass | Named register/rewrite/done-proof contracts agree across rows; no material behavioral ambiguity. |
| Post-implementation certification | n/a | No product suite/session gate or unwritten implementation certification was requested or run. |

### Durable observations

```json
{"schema_version":"evidence.v1","check_id":"s49b-plan-r2-rewrite-writer","command":"rtk proxy python -B C:/Temp/av-kit/s49b-r2-probe.py","cwd":"P:/av-kit","scope":"actual rewrite entrypoint with REGISTER and SCRATCH redirected to temp; proposed writer in memory","phase":"static","exit_code":0,"result":"pass","tested_state":"HEAD 19001ca; target/register SHA-256 values in Scope; Python -B","output":"Wrong hash and pre-existing writer refused. Staged .version mutation: exit 1, parsed differences ['.version'], register copy unchanged. Concurrent subprocess writer: exit 1 PermissionError. Valid reformat/reword/resolve: exit 0 each, parsed fields changed 0/15/3; decision logs read 61/67, 67/67, 67/67. Reformat bytes identical to prototype. Nested lists/maps, separator strings, dates/datetimes/numbers/bools/null and scalar keys passed grammar, reader and equality. Invalid keys refused before writing. ALL_PROBES_PASS; REAL_REGISTER_AND_PLAN_UNCHANGED.","fresh":true}
```

```json
{"schema_version":"evidence.v1","check_id":"s49b-plan-r2-compatibility","command":"rtk proxy python -B C:/Temp/av-kit/s49b-r2-extra.py","cwd":"P:/av-kit","scope":"read-only Session 49 validator CLI; temp register renders/triage; residual writer and AC-3 observations","phase":"static","exit_code":0,"result":"pass","tested_state":"Same target/register state as Scope","output":"Current exact DONE_PROOF exit 1: issue FFMPEG-LIBDVDCSS-BUNDLED decision_log item 1 is not valid YAML, mixes a mapping and a sequence. Temp-register single-issue compatibility checks exit 0: 24 and 27 decisions reconciled against 28 rows. Reword Markdown unchanged=True. Resolved issue moves actionable to archived (42/64 to 41/65); deferred stays 6. Residual 128-character key round-trips equal but explicit ? key fails grammar. Old U+0085 round-trip=False ('a b'). EXTRA_PROBES_PASS_REAL_REGISTER_UNCHANGED.","fresh":true}
```

```json
{"schema_version":"evidence.v1","check_id":"s49b-plan-r2-cli-red-feasibility","command":"rtk proxy python -B C:/Temp/av-kit/s49b-r2-flags.py","cwd":"P:/av-kit","scope":"actual validator CLI on temp fixtures from its selftest constants","phase":"static","exit_code":0,"result":"pass","tested_state":"HEAD 19001ca; unchanged production validator","output":"AC4 missing first decision: old CLI exit 0; AC5 duplicate issue flags: old CLI exit 0; AC6 absent first issue: old CLI exit 0; AC7 single control: exit 0. RED_FEASIBILITY_CONFIRMED; NO_GREEN_CLI_CLAIM.","fresh":true}
```

## Verdict

`approved` — F1 and F2 are fixed, and no new evidence-backed High/Critical delivery failure was found. Proceed to Mat's existing execution/wording gate. Preserve AC-3's equality assertion despite the stale Red label, and retain the long-key residual above without expanding this bounded round into another key-policy correction cycle. Execution review must verify the real writer, repeatable CLI, combined row-6 proof and fresh full gate.

Output preflight: `rtk proxy python -B C:/Temp/av-kit/s49b-r2-output-check.py`, exit 0: v2 verdict schema, report metadata/intent/Q1–Q8/PR-1–PR-9 and evidence blocks agree; reviewed plan/task/script and register hashes are unchanged. The canonical task still has 25 unstarted rows, as expected for this plan-only review.

This complete report is saved only to `C:/Temp/av-kit/s49b-plan-review-round-2.md`; the coordinator owns copying it to the canonical rolling review and recording the verdict. Completion-preflight is applied to this review artifact and its evidence, within the user's read-only boundary; it does not authorize executing the reviewed task.
