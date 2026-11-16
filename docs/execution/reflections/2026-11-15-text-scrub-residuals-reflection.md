---
date: "2026-11-15"
project: "2026-11-15-text-scrub-residuals"
meus: ["MEU-147", "MEU-148"]
plan_source: "docs/execution/plans/2026-11-15-text-scrub-residuals/implementation-plan.md"
template_version: "2.0"
---

# 2026-11-15 Meta-Reflection

> **Date**: 2026-11-15. Planned and plan-reviewed in the afternoon; executed, reviewed and closed late in the evening.
> **MEU(s) Completed**: MEU-147 and MEU-148, Session 77 `text-scrub-residuals`, the third session of the post-rc.3 triage residuals grouping (`.agent/context/grouping/2026-11-15-post-rc3-triage-residuals-session-grouping.md`, row 77).
>
> - **MEU-147 (`TRANSCRIPT-UNCLEANED-TITLE-FALLBACKS`).** D-360's title cleaner moved unchanged into the domain as `clean_text` and the YouTube adapter imports it (TEXT_CLEAN_SHARED, D-922). A transcript channel named from its extract title, and a transcript title taken from the caption port, now go through it; a value that cleans to nothing takes the playlist or video ID (CHANNEL_FALLBACK_CLEAN, RESULT_TITLE_CLEAN, D-923). The transcript domain types gain no guard (CLEAN_AT_ENTRY, D-924).
> - **MEU-148 (`CONSOLE-HOME-SCRUB-SHORT-FORM`).** On Windows `scrub_home` and the split-aware download scrub also turn the home folder's 8.3 short form into `~` (Mat's D-337; SHORT_FORM_SCRUB, SHORT_FORM_SPLIT, D-925). `home_forms` reads the short form once per home value through `short_path_name` over `GetShortPathNameW`, cached under a lock, and a failed lookup keeps the long-form-only result (SHORT_FORM_LOOKUP, SHORT_FORM_CACHE, SHORT_PATH_API, SHORT_PATH_NAME; D-926, D-927).
>
> **Plan Source**: `docs/execution/plans/2026-11-15-text-scrub-residuals/implementation-plan.md`

---

## Execution Trace

### Friction Log

1. **What took longer than expected?**
   - **The plan review took 2 rounds.** Round 1's R1-F1 (High, blocking): AC-148.1 accepted an always-empty `short_path_name`, so the gate could pass with the native lookup missing. D-927 split the native load into `_short_path_api`, ran the real helper over a fake callable (AC-148.8, AC-148.9), and added the plan-local empty-lookup mutant that every AC-148.8 test must fail. Round 2 approved.
   - **Gate attempt 1** (`tsr-gate-h1-attempt1.txt`) stopped at `meu-148-mutant-check`: `no readable child exit code in tsr-D6-meu-148-mutant.txt.exit`. The mutant had failed as required; the gate's MustFail block never wrote the `.exit` file that red-check reads. One line in `session-gate.ps1` fixed it, and the second run passed (`session-gate: all steps exit 0`). The cost was one full gate, about ten minutes.
   - **Row 2's first Green** read `2 failed, 33 passed in 1.15s` (`tsr-147-green-attempt1.txt`): the test's own `_front` helper split the raw Markdown on `\n` only, and the file reads back with CRLF on Windows. The fix was in the helper.

2. **What instructions were ambiguous?**
   - **DECLARED_NEW.** §Verification Plan 1 kept it at the selftest names; task row 0 added `clean_text`, `home_forms` and `short_path_name`. D-928 followed the task row, the stricter reading.
   - **The S4 and scope steps** named no script. D-929 wrote a plan-local `scope-check.py` from Session 76's, without its HEAD-move rule, because the brief fixes HEAD at `ab761dd`.

3. **What instructions were unnecessary?**
   - H1-4's OpenAPI row, again: the plan cannot touch `packages/api`.
   - H2-1's `view_file` row: H2-2's check validates the reflection against the same template and schema.

4. **What was missing?**
   - **A dry run of the gate's must-fail path at plan time.** The plan specified the mutant and its red-check, but nothing ran the gate's MustFail branch before H1-2 (RULE-1).
   - **A format check of the files the plan edits.** `adapter.py` and `services/download.py` were not ruff-formatted at HEAD, so the gate's `py-format` step would have failed on lines this plan does not change (D-930, RULE-3).

5. **What did you do that wasn't in the prompt?**
   - **A `.ps1` wrapper per row** (`run-row<n>.ps1`, `run-h1-<n>.ps1`) in the receipts folder, each running its Validation cell after the row environment.
   - **`_SHORT_FORMS_LOCK`** in `health.py`, beyond the plan text, so "looked up at most once per process" holds when logging threads scrub at the same time. The reviewer's 16-thread probes confirmed one lookup.
   - **A final line-ending check** over 20 files (`tsr-eol-final.txt`: `line-ending drift: []`).
   - **The Codex Validation Report.** Both handoffs' reports were filled from the canonical review after H1-7b, and H1-6, H1-6a and H1-6b passed again.

### Quality Signal Log

6. **Which tests caught real bugs?**
   - **The Reds** failed for the stated reasons: `19 failed in 0.24s` (`tsr-147-red.txt`) and `18 failed in 0.26s` (`tsr-148-red.txt`), each by assertion on the absent names; red-check reported 0 problems for 5 and 9 required families.
   - **The empty-lookup mutant** is the check that R1-F1 asked for: under it the two AC-148.8 tests fail by assertion (`2 failed, 16 deselected`, `tsr-148-mutant.txt`), so a broken native producer cannot pass the gate.
   - **AC-147.4 and AC-147.5's front-matter reads** caught the CRLF read-back on Windows, a test-helper bug and not a product one.

7. **Which tests were trivially obvious?**
   - AC-148.1's real native lookup: this PC's home folder has no distinct short form (`tsr-148-real-lookup.txt`: distinct short form False), so it proves only that the call does not break. The reviewer rated it Adequate; AC-148.8 carries the success proof.

8. **Did pyright/ruff catch anything meaningful?**
   - No finding changed delivered behaviour. `ruff format` found the two pre-existing unformatted files (D-930); the gate reads `All checks passed!`, `7 files already formatted` and `0 errors, 0 warnings, 0 informations`.

### Workflow Signal Log

9. **Was the FIC useful as written?**
   - Yes. The mechanism ids (TEXT_CLEAN_SHARED to SHORT_FORM_SPLIT), D-922 to D-927 and the 15 ACs gave the rows, the handoffs and both reviews one vocabulary. The execution review approved at round 1 with 0 findings.

10. **Was the handoff template right-sized?**
    - Yes for two MEUs. The cross-reference rows let each handoff cite AC-122 and AC-119.10 without owning them. The Departures list ran to eleven bullets, each a disclosed deviation.

11. **How many tool calls did this session take?**
    - About 280 in the executor's transcript, from row 0 to H2-6. Planning, both review dispatches and H1-7 ran in the coordinator's session.

12. **Which rows were delegated, to which subagent (harness + model), and did any delegated result need rework?**
    - The coordinator (Claude Code) delegated rows 0 to H1-6b and H2-1 to H2-6 to one executor subagent (Claude Code, Claude Opus 5.5), and ran H1-7 to H1-7b itself.
    - No row went to `av-kit-builder`, `av-kit-verifier` or `av-kit-peer-reviewer`. No delegated result needed rework.
    - Codex reviewed the plan and the execution as the independent reviewer, which isn't delegation.

### Decisions Log

- Move D-360's cleaner unchanged into the domain as `clean_text`; the adapter imports it — [D-922](../plans/2026-11-15-text-scrub-residuals/implementation-plan.md)
- A channel name that cleans to nothing takes the playlist or video ID — [D-923](../plans/2026-11-15-text-scrub-residuals/implementation-plan.md)
- Clean at the two service entry points; the transcript domain types gain no guard — [D-924](../plans/2026-11-15-text-scrub-residuals/implementation-plan.md)
- The split-aware download scrub applies its pattern to each home form — [D-925](../plans/2026-11-15-text-scrub-residuals/implementation-plan.md)
- A `SHORT_FORM_LOOKUP` flag, one replaceable `short_path_name`, and `home_forms` caching each lookup, an empty one included — [D-926](../plans/2026-11-15-text-scrub-residuals/implementation-plan.md)
- Split the native load into `_short_path_api`, prove the real helper over a fake callable, and require the empty-lookup mutant to fail — [D-927](../plans/2026-11-15-text-scrub-residuals/implementation-plan.md)
- DECLARED_NEW follows task row 0 and gains the three new names — [D-928](../plans/2026-11-15-text-scrub-residuals/implementation-plan.md)
- A plan-local `scope-check.py` for S4, scope paths and line endings, with HEAD fixed at `baseline.sha` — [D-929](../plans/2026-11-15-text-scrub-residuals/implementation-plan.md)
- `ruff format` the two pre-existing unformatted files, six layout-only hunks — [D-930](../plans/2026-11-15-text-scrub-residuals/implementation-plan.md)

---

## Pattern Extraction

### Patterns to KEEP
1. **A mutant that the proof must fail.** R1-F1 showed that a fake-only test cannot see a broken producer. The plan-local empty-lookup plugin turned "the real helper works" into a must-fail gate step.
2. **Moving shared logic unchanged.** `clean_text` kept D-360's executable body; the reviewer's AST comparison proved it identical, so MEU-122's tests stayed valid unedited.
3. **Synthetic short-form fixtures.** Every MEU-148 test builds its 8.3 alias in the test, and the real lookup runs only over a temp folder, so no tracked file or receipt names the real home folder in either form.

### Patterns to DROP
1. **Writing a test file into the tree while the base suite runs.** The MEU-147 test file landed during row 0's suite; it had already collected, but the file had to be moved out and put back at row 1. Stage new tests outside the tree until row 0 is done (RULE-2).

### Patterns to ADD
1. Dry-run each gate step that inverts an exit (MustFail) at plan time, against the receipt shape the next step reads (RULE-1).
2. Stage new test files outside the tree until row 0's base suite has finished (RULE-2).
3. Run `ruff format --check` on every Python file the plan edits at plan time, and record a needed format pass as a plan decision (RULE-3).

### Calibration Adjustment
- **Estimated:** no token budget. The round caps were 3 for the plan review and 6 for the execution review.
- **Actual time** (local time, from the receipts' mtimes):
  - Plan review: round 1 dispatched at 14:39 and returned at 14:48; round 2 from 14:53 to 14:59, approved.
  - Execution: row 0's baseline at 22:49; MEU-147 Red at 22:50 and Green at 22:52; MEU-148 Red at 22:53 and Green at 22:54; row 5 at 22:57; gate attempt 1 stopped at 23:01; the passing gate at 23:11; H1-3 at 23:12.
  - Execution review: dispatched at 23:17, round 1 approved at 23:31; H1-7a and H1-7b at 23:32.
- **Tokens (ledger usage):** plan review 5,390,806 then 4,411,684 (9,802,490 in all); execution review 6,678,084 in one round.
- **Adjusted estimate for a two-MEU service-layer session:** about 5M tokens per plan round and 7M per clean execution round; about 9 minutes per full gate (Python 527.72s here, against 297.28s at row 0, from the gate's parallel steps on a busy machine).

---

## Next Session Design Rules

```
RULE-1: When a gate step inverts a child's exit (MustFail), the plan dry-runs that step at plan time and checks that it leaves every sidecar the next step reads (the .exit file red-check needs).
SOURCE: Session 77 gate attempt 1: meu-148-mutant failed as required, but session-gate.ps1's MustFail block wrote no tsr-D6-meu-148-mutant.txt.exit, so meu-148-mutant-check stopped the gate ("no readable child exit code"), and a second full gate run was needed.
EXAMPLE: before, the MustFail block turned exit 1 into a pass and wrote nothing; after, it runs Set-Content "$receipt.exit" $code first, as the plain steps do.
```

```
RULE-2: New test files are staged outside the tree until row 0's base suite has finished; they are placed at their Red row.
SOURCE: Session 77 row 0: the MEU-147 test file was written while the base suite ran; baseline-scope.json recorded it absent and the suite had already collected, but it was moved to the receipts folder's staged folder and restored at row 1 after the S4 check.
EXAMPLE: before, the test was written into tests/unit during row 0; after, it is written to the receipts folder's staged folder and copied in at row 1.
```

```
RULE-3: At plan time, run ruff format --check on every Python file the plan edits; if one is not formatted at HEAD, record the format pass as a plan decision with its hunk count.
SOURCE: Session 77 D-930: adapter.py and services/download.py were two and four layout hunks away from ruff format at HEAD, so the gate's py-format step would fail on lines the plan does not change; the decision was taken in execution.
EXAMPLE: before, the plan's py-format step assumed the files were formatted; after, the plan names the six layout hunks and the decision that applies them.
```

---

## Next Day Outline

1. **Target:** Session 78 `e2e-harness-hardening`, the next row of the grouping. Its prompt is `C:/Temp/av-kit/session-78-prompt.md`.
2. **Before it starts:** the coordinator commits Session 77, as Mat directs, before Session 78's row 0. The draft is `C:/Temp/av-kit/text-scrub-residuals/tsr-commit-draft.txt`.
3. **Scaffold changes needed:** none in product code. RULE-1 belongs in the session-gate template's MustFail block.
4. **Patterns to bake in from today:** RULE-1 to RULE-3, plus Session 76's RULE-3 (a HEAD move after the gate means a second gate run) and Session 75's RULE-1 (an empty New Findings table keeps its header).
5. **Codex validation scope:** each next session's plan and execution, scoped to intent, not process paperwork.
6. **Time estimate:** set by Session 78's plan.
7. **Still open from this session, for triage:**
   - a lone surrogate in a transcript's text (`result.text`) fails the same raw write (plan §Out of Scope);
   - the first short-path lookup runs under the cache lock with no timeout, so a concurrent scrub waits for it (the reviewer's residual risk);
   - a new 8.3 alias that appears after an empty result was cached is not seen until restart (an approved exclusion).

---

## Efficiency Metrics

| Metric | Value |
|--------|-------|
| Total tool calls | About 280 in the executor's transcript, from row 0 to H2-6 |
| Time to first green test | MEU-147 Green at 22:52, two minutes after its Red (`tsr-147-red.txt` 19 failed; `tsr-147-green.txt` 35 passed) |
| Tests added | 37: 19 MEU-147 and 18 MEU-148 test cases. Python went from 2945 at row 0 (`tsr-base-py.txt`) to 2982 at the gate (`tsr-D6-py-tests.txt`) |
| Codex findings | Plan review: R1-F1 High, fixed by D-927, approved at round 2 of 3. Execution review: approved at round 1 of 6 with 0 findings |
| Handoff Score (X/7) | 6/7. Every AC has evidence and the execution review approved at round 1 with 0 findings; one point is lost to the gate-script defect that cost a second gate run |
| Rule Adherence (%) | 92 (11 of 12 sampled rules followed in full, 1 in part) |
| Prompt→commit time | Planned, executed, approved and closed 2026-11-15. Not committed; the coordinator commits on Mat's direction |

### Rules Sampled for Adherence Check

| Rule | Source | Followed? |
|------|--------|-----------|
| Independent review; no self-approval | AGENTS.md §Dual-Agent Workflow | Yes. Codex reviewed the plan and the execution; the executor stopped before H1-7 |
| The executor never commits, stages or pushes | The executor brief; AGENTS.md §Commits | Yes. H2-5 is a draft only |
| Red before Green | AGENTS.md §Testing | Yes. Rows 1 and 3 failed by assertion before rows 2 and 4 |
| Keep line endings; measure in Python bytes | Session 70 RULE-5 | Yes. `tsr-eol-final.txt`: 20 files, no drift; the five CRLF product and doc files stay CRLF |
| No home path in either form in a tracked file or a quoted receipt | The executor brief (MEU-148) | Yes. The short-form fixtures are synthetic, and the real lookup is recorded as a boolean only; the reviewer's privacy audit over 28 files passed |
| Tests use `tmp_path` only | The executor brief | Yes |
| MEU status and issues change only through the tools | The executor brief | Yes. `issue-resolve.py` and `meu_status.py` wrote every register change |
| Unset `ELECTRON_RUN_AS_NODE` before identity and Electron steps | Session 85 RULE-2 | Yes. Every wrapper sets it to `$null` |
| Run HDP v2 on a decision and record it once | HDP §6 | Yes. D-928 to D-930 are in the plan YAML only; the handoffs' Decision Log is `None.` |
| Never edit `tools/validate_closeout_artifacts.py` | The executor brief | Yes |
| HEAD stays at `ab761dd` | The executor brief | Yes. HEAD equals origin/main at every check |
| New files written only when their row starts | Plan row order | Partly. The MEU-147 test file was written during row 0 and moved out until row 1 |

---

## Instruction Coverage

```yaml
schema: v1
session:
  id: "a3707a5b-24b9-4989-a528-bc4ea719a8a8"
  task_class: tdd
  outcome: success
sections:
  - id: priority_0_system_constraints_non_negotiable
    cited: true
    influence: 3
  - id: planning_contract
    cited: true
    influence: 2
  - id: testing_tdd_protocol
    cited: true
    influence: 3
  - id: execution_contract
    cited: true
    influence: 3
  - id: session_discipline
    cited: true
    influence: 2
  - id: dual_agent_workflow
    cited: true
    influence: 3
  - id: commits
    cited: true
    influence: 3
  - id: validation_pipeline
    cited: true
    influence: 3
  - id: rtk_token_optimized_commands
    cited: true
    influence: 1
  - id: instruction_coverage_reflection
    cited: true
    influence: 2
loaded:
  workflows: [execution_session]
  roles: [orchestrator, coder, tester]
  skills: []
  refs:
    - .agent/docs/human-decision-protocol.md
    - .agent/schemas/reflection.v1.yaml
    - docs/execution/reflections/TEMPLATE.md
    - .agent/context/handoffs/TEMPLATE.md
    - .agent/context/handoffs/2026-11-14-capture-shapes-steps-MEU-106-handoff.md
    - .agent/context/handoffs/2026-11-14-capture-shapes-steps-MEU-107-handoff.md
decisive_rules: [P0:never-commit-or-push-without-human-approval, P0:keep-line-endings, P0:no-home-path-in-tracked-files, P1:independent-review-no-self-approval, P1:red-before-green]
conflicts:
  - "Plan §Verification Plan 1 kept DECLARED_NEW at the selftest names while task row 0 added clean_text, home_forms and short_path_name; D-928 followed the task row."
  - "The plan's Status line 15 was edited by the coordinator after plan approval to carry Mat's authorizing words; disclosed in both handoffs."
note: "Two scrub residuals on the service layer; the plan review took 2 rounds for a mutant-proof gap, and the execution review approved at round 1."
slim_candidate: ["H1-4's OpenAPI row in a session that cannot touch packages/api.", "H2-1's view_file row repeats what H2-2's validator checks."]
overthinking_observed: false
review_churn:
  rounds_to_approval:
    plan: 2
    execution: 1
  findings_per_round:
    - review: plan
      round: 1
      critical: 0
      high: 1
      medium: 0
      low: 0
    - review: plan
      round: 2
      critical: 0
      high: 0
      medium: 0
      low: 0
    - review: execution
      round: 1
      critical: 0
      high: 0
      medium: 0
      low: 0
  churned_findings: 0
  finding_categories:
    weak_test: 1
  verdicts:
    changes_required: 1
    approved: 2
meu_work_classes: [correctness, correctness]
```

The review churn counts the ledger's recorded rounds. R1-F1's kind was `control-defeat`; it is bucketed as `weak_test`, because the defect was a test that could not see a broken producer. The gate's first attempt and row 2's first Green came from the rows, not from a reviewer, so they are not findings here.
