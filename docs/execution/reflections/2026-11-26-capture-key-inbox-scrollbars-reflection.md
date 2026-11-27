---
date: "2026-11-26"
project: "2026-11-26-capture-key-inbox-scrollbars"
meus: ["MEU-165", "MEU-166", "MEU-167"]
plan_source: "docs/execution/plans/2026-11-26-capture-key-inbox-scrollbars/implementation-plan.md"
template_version: "2.0"
---

# 2026-11-26 Meta-Reflection

> **Date**: 2026-11-26. Planned and plan-reviewed on 2026-11-26; executed, reviewed and closed on 2026-11-27.
> **MEU(s) Completed**: MEU-165 Capture key in texts, MEU-166 Catalog follows the inbox folder and MEU-167 Viewport scroll bars, the three homes of 09 (§Capture key in texts, §Catalog follows the inbox folder, §Viewport scroll bars), from Mat's three Capture findings of 2026-11-26 (D-1400 to D-1402). Session 103 `capture-key-inbox-scrollbars` was the second of the four sessions of the 2026-11-26 grouping (D-1410). It ran on `main` from `e5028a3`, and `HEAD` did not move.
>
> - **The page names the saved key** (`CAPTURE_KEY_TOKEN`, `CAPTURE_KEY_SAVED`, `CAPTURE_KEY_FOLLOW`, `CAPTURE_KEY_UNCONFIRMED`, `CAPTURE_KEY_DEFAULT_READING`, D-1420 to D-1422). The empty state, five Capture help lines, the Settings startup help and quick-start step 1 hold the captureKey token in braces, which `captureKeyText` in the new capture-key.ts replaces. A save changes them with no restart, and the page follows main's hotkey status for at most 10 reads of 500 ms. With the default `F2` every text reads as at HEAD, so the AC-162 pins and the help-shots hash hold and no image is retaken.
> - **The list follows the inbox folder** (`INBOX_SCOPE`, `INBOX_SCOPE_SCAN`, `INBOX_SCOPE_BY_ID`, D-1423, D-1424). `scan_inbox` and `list_shots` return only shots directly inside the current inbox; rows of other folders are kept and come back; every by-id method answers a shot outside the inbox with the unknown-id `NotFoundError`. routes/captures.py and openapi.committed.json are byte-unchanged.
> - **The page refreshes on a saved inbox change** (`INBOX_SAVE_REFRESH`, `INBOX_SELECTION_LEFT`, `INBOX_RESULT_BOUND`, D-1425): the list is asked for at once, a selected shot that left the list is cleared, and an old folder's late result selects nothing in the new one.
> - **A zoomed view has scroll bars** (`SCROLL_BAR_GEOMETRY`, `SCROLL_BAR_OVERLAY`, `SCROLL_BAR_DRAG`, `SCROLL_BAR_LOOK`, D-1426, D-1427): drawn bars at the bottom and the right, a thumb drag through the existing clamped pan; capture-fit-map.ts and capture-zoom.ts are byte-identical and the wheel, Space+drag and middle-drag tests are unchanged.
> - **The proof of the whole.** Gate run 2 passed every step: Vitest 1,716, pytest 3,379 with nothing deselected, and the mini-air Electron run of 260 tests with no unexpected result.
>
> **Plan Source**: `docs/execution/plans/2026-11-26-capture-key-inbox-scrollbars/implementation-plan.md`

---

## Execution Trace

### Friction Log

1. **What took longer than expected?**
   - **The gate ran twice (D-1438).** Run 1 stopped at `ui-tests`: 9 tests timed out at Vitest's 5 s limit, all in six main-process test files that import only `ui/src/main/` modules, which this session does not change, while another repository's gate ran about 50 pytest workers on the same PC. The six files alone passed 99 of 99 in 551 ms (`cki-h12-diag-6files.txt`). After the other gate ended, the whole gate ran again unchanged, with no test excused, and passed (RULE-2).
   - **Two Red reruns after harness defects.** Row 5's first Green failed two tests on defects of row 4's harness, not of the product (D-1436); row 7's first Green failed on a stale Vitest transform in `ui/node_modules/.vitest-cache` and a help card left open in localStorage by the test before (D-1437, RULE-3). Each time the harness was amended, the product files were set back, and the Red row ran again; the first records are kept as `-r1`.
   - **Smaller reruns** kept their first receipts: row 3 (ruff `E501` on one docstring line) and row 9 (a `-0` pan value, now passed through `Math.max`).
   - **The H2-2 decision probe** failed twice before it read the log. The plan's `row-check.py decision-sources` loads `validate_closeout_artifacts.py` by file path, which cannot import its sibling `durable_evidence`; the selftest had injected the function, so the real call never ran before H2 (RULE-1). With `PYTHONPATH` set to `tools/`, as `python tools/validate_closeout_artifacts.py` sets it, the validator then refused three decision-log phrases that write a token in braces, Session 104's RULE-3 case again. The three phrases, two in D-1421 and one in D-1422, were reworded with the same meaning, and the probe read 28 ids (`cki-h22-decision-sources-r1.txt`, `-r2.txt`, `cki-h22-decision-sources.txt`).
   - The rows, from the receipts' modification times (local, 2026-11-27):

     | Step | Time |
     |---|---|
     | Plan review rounds 1 and 2, approved at round 2 | 2026-11-26 |
     | Baseline and row 0 | 11:08 |
     | Rows 1 to 9 (Electron Red run, Red and Green for each MEU) | 11:12 to 11:58 |
     | Row 10 Electron Green run, row 11 canon and registers | to 12:29 |
     | Gate runs 1 and 2 | 12:30 to 12:51 |
     | H1-3 to H1-6b checks | to 12:57 |
     | Execution review round 1, approved | 12:58 to 13:09 |

2. **What instructions were ambiguous?**
   - **H2-2's probe command** assumes the plan script can load the validator by path; nothing in the row says the validator needs `tools/` on the import path.

3. **What instructions were unnecessary?**
   - H2-1's `view_file` row, again: H2-2's validator reads the same template and schema.

4. **What was missing?**
   - **A real, not injected, run of every plan-local wrapper around a repo tool at row 0** (RULE-1).
   - **A host-load wait before the gate's Vitest step** on a host that other repositories' gates share (RULE-2).
   - **A Vitest cache clear and a localStorage reset in new behaviour tests** between Red and Green (RULE-3).

5. **What did you do that wasn't in the prompt?**
   - **Reworded three decision-log phrases at H2-2** so the validator reads them, with the same meaning; the earlier plan is kept as `implementation-plan.pre-h22.md` under the receipts folder.
   - **Made every hand edit with a script** that writes bytes, asserts each anchor once and keeps the file's line endings.

### Quality Signal Log

6. **Which tests caught real bugs?**
   - **AC-166.6 and the `INBOX_RESULT_BOUND` tests** pinned the case the plan review's F2 found: an old folder's crop result could select an id the clearing rule would never clear.
   - **`capture-scroll-bars.test.ts`** caught the `-0` pan value at row 9.
   - **The four Electron tests** (AC-165.10, AC-166.7, AC-167.7, AC-167.8) failed at Red in run `r20261127T161201Z-091957d` with exactly 4 unexpected results, and passed in run `r20261127T170013Z-02ecd38` (260 of 260).
   - **`test_capture_inbox_scope.py`** failed at Red with the old folder's rows listed and passed after row 3.

7. **Which tests were trivially obvious?**
   - The guard tests that pin the default readings to the HEAD strings passed at Red, as guards should.

8. **Did pyright/ruff catch anything meaningful?**
   - ruff's `E501` stopped row 3 on a docstring line, which is format, not behaviour. pyright and tsc found nothing.

### Workflow Signal Log

9. **Was the FIC useful as written?**
   - Yes. The fifteen mechanism ids gave the tests, the handoffs and both reviews one vocabulary; the execution review answered Q1 to Q7 by them with no finding.

10. **Was the handoff template right-sized?**
    - Yes for three MEUs. The template facts for MEU-166 and MEU-167 had to be corrected against the plan's text before the handoffs were filled.

11. **How many tool calls did this session take?**
    - Not counted exactly. Several hundred in the coordinator's and the executor's transcripts from plan to H2, across context compactions.

12. **Which rows were delegated, to which subagent (harness + model), and did any delegated result need rework?**
    - No task row was delegated to a subagent. One Claude Code executor fork ran rows 0 to H2-6 under the coordinator; the two Codex reviews were dispatched by the coordinator.

### Decisions Log

All are `autonomous`, decided on the HDP recommendation under Mat's hand-over of 2026-11-26, with `mandatory: none` unless named. D-1400 to D-1402 (triage) are read from `known-issues.yaml` and the grouping decisions from the grouping file, all through `--decision-source`.

- The texts, the key cap and the banner show the saved capture key, followed for at most 10 reads after a save — [D-1420](../plans/2026-11-26-capture-key-inbox-scrollbars/implementation-plan.md)
- One token and one formatter; the exported constants are the default readings, so no image is retaken — [D-1421](../plans/2026-11-26-capture-key-inbox-scrollbars/implementation-plan.md)
- Four source-scan expectations take the token form; no other expectation changes — [D-1422](../plans/2026-11-26-capture-key-inbox-scrollbars/implementation-plan.md)
- A row is in scope when its file's folder is the current inbox, with no filesystem call; other rows are kept — [D-1423](../plans/2026-11-26-capture-key-inbox-scrollbars/implementation-plan.md)
- A shot outside the inbox answers not found on every by-id method (M-5) — [D-1424](../plans/2026-11-26-capture-key-inbox-scrollbars/implementation-plan.md)
- A saved inbox change refreshes the list and clears a selection that left it (M-5) — [D-1425](../plans/2026-11-26-capture-key-inbox-scrollbars/implementation-plan.md)
- Drawn scroll bars over the frame, not a native scroll container (M-5) — [D-1426](../plans/2026-11-26-capture-key-inbox-scrollbars/implementation-plan.md)
- A thumb drag only, with the scrollbar role and no tab stop — [D-1427](../plans/2026-11-26-capture-key-inbox-scrollbars/implementation-plan.md)
- The key and inbox proofs run on the real backend in capture-settings-draft.test.ts; the bar proofs in capture-inbox.test.ts — [D-1428](../plans/2026-11-26-capture-key-inbox-scrollbars/implementation-plan.md)
- Ten paths outside the owns list that the homes force (M-8) — [D-1429](../plans/2026-11-26-capture-key-inbox-scrollbars/implementation-plan.md)
- Two mini-air runs, and the gate reuses row 10's run when the tree equals its snapshot — [D-1430](../plans/2026-11-26-capture-key-inbox-scrollbars/implementation-plan.md)
- MEU-167 stays in this session — [D-1431](../plans/2026-11-26-capture-key-inbox-scrollbars/implementation-plan.md)
- The 09 lines that change on delivery (M-8) — [D-1432](../plans/2026-11-26-capture-key-inbox-scrollbars/implementation-plan.md)
- Row 11's canon edit accepts the grouping cell `plan approved (round 2)` — [D-1433](../plans/2026-11-26-capture-key-inbox-scrollbars/implementation-plan.md)
- Row 0's free-name check counts a hyphen as part of a token — [D-1434](../plans/2026-11-26-capture-key-inbox-scrollbars/implementation-plan.md)
- The two real-backend Electron tests set the test budget that AC-151.14 sets — [D-1435](../plans/2026-11-26-capture-key-inbox-scrollbars/implementation-plan.md)
- Row 4's harness is amended and its Red run again before row 5 — [D-1436](../plans/2026-11-26-capture-key-inbox-scrollbars/implementation-plan.md)
- The stale Vitest cache is cleared, row 6's harness is amended and its Red run again — [D-1437](../plans/2026-11-26-capture-key-inbox-scrollbars/implementation-plan.md)
- The whole gate runs again, unchanged, after another repository's load ends — [D-1438](../plans/2026-11-26-capture-key-inbox-scrollbars/implementation-plan.md)

---

## Pattern Extraction

### Patterns to KEEP
1. **Make the default reading the old string.** Because every text with `F2` equals its HEAD string, the quick-start pins and the help-shots hash proved the change without a retake.
2. **Set the product back and rerun Red after a harness fix.** Both harness amendments were proved by a fresh Red, not argued.
3. **Prove a load timeout before a rerun.** The six files alone, then the whole gate unchanged, with nothing excused.
4. **Bind the Electron Red run to a snapshot** of HEAD plus the new tests, so the four new failures are the only ones.

### Patterns to DROP
1. **Decision text that writes a code token in braces.** The closeout validator reads it as an unfilled template; Session 104 wrote this rule on the same day, after this plan was drafted.

### Patterns to ADD
1. **Run each plan-local tool wrapper for real at row 0** (RULE-1).
2. **Wait for host load before the gate's test steps** (RULE-2).
3. **Clear the Vitest cache and the test's localStorage between Red and Green** (RULE-3).

### Calibration Adjustment
- **Estimated:** no token budget. Round caps of 3 (plan) and 6 (execution).
- **Actual time:** about 80 minutes of rows, 21 minutes for the two gate runs and 11 minutes for the execution review.
- **Tokens:**

  | Item | Tokens |
  |---|---|
  | Plan review, round 1 | 12,426,215 |
  | Plan review, round 2 | 10,210,239 |
  | Execution review, round 1 | 9,580,330 |
  | Total | 32,216,784 |

- **Adjusted estimate** for three renderer and service MEUs with Electron proofs: about 22M tokens for a two-round plan review and 9 to 10M for the execution review; about two hours of rows and gate when the E2E host answers and the PC is not loaded.

---

## Next Session Design Rules

```
RULE-1: A plan-local script that loads a repo tool by file path runs that call for real at row 0, not only in a selftest that injects the function, and its loader puts tools/ on sys.path.
SOURCE: Session 103 H2-2: "ModuleNotFoundError: No module named 'durable_evidence'" from row-check.py decision-sources; the selftest had passed at row 0 and in the gate.
EXAMPLE: before, row 0 runs row-check.py --selftest only; after, row 0 also runs row-check.py decision-sources on the plan as drafted.
```

```
RULE-2: The session gate checks host load before its test steps and waits until other repositories' gates have ended, so a timeout-only failure in files the session does not touch is not a first run's result.
SOURCE: Session 103 D-1438: gate run 1, "Tests  9 failed | 1707 passed (1716)", each "Test timed out in 5000ms", while about 50 pytest workers of another repository ran.
EXAMPLE: before, session-gate.ps1 starts ui-tests at once; after, it runs the wait-load check first and records the load in its receipt.
```

```
RULE-3: Between a Red row and its Green row, remove the Vitest cache entries of the new test files, and a new behaviour test that opens a help card clears localStorage in afterEach.
SOURCE: Session 103 D-1437: row 7's first Green ran a stale transform with import.meta.glob still empty, and AC-165.8 found the Settings help card already open.
EXAMPLE: before, row 7 runs vitest straight after row 6; after, row 7 first deletes the cache entries and the test file's afterEach calls localStorage.clear().
```

---

## Next Day Outline

1. **Next:** Session 106 (`app-auto-update`), then Session 105 (`entry-emphasis-and-advanced`); the prompt is at `C:/Temp/av-kit/next-session-prompt.md` (H2-6).
2. **Scaffold changes needed:** none.
3. **Patterns to bake in from today:** RULE-1 to RULE-3 here and Session 104's RULE-1 to RULE-3. A help text that names the capture key holds the captureKey token in braces; the exported help constants are the default readings; `HelpCard` has a `captureKey` prop.
4. **Codex validation scope:** the next session's own loops.
5. **Time estimate:** set by the next plan.
6. **Still open for Mat:** the commit of Session 103 (H2-5 has the draft; no push from the agent); D-1543 and D-1544, which are Mat's, for release only.

---

## Efficiency Metrics

| Metric | Value |
|--------|-------|
| Total tool calls | Not counted exactly; several hundred across context compactions |
| Time to first green test | Row 3 at 11:21, 6 minutes after row 2's Red at 11:15 |
| Tests added | 32 Vitest tests (3 in `capture-key.test.ts`, 10 in `capture-key.behavior.test.ts`, 6 in `capture-inbox-scope.behavior.test.ts`, 9 in `capture-scroll-bars.test.ts`, 4 in `capture-scroll-bars.behavior.test.ts`), 10 pytest tests (9 in `test_capture_inbox_scope.py`, 1 in `test_api_capture_inbox_scope.py`) and 4 Electron tests. Final gate: Vitest 1,716, pytest 3,379, Electron 260 |
| Codex findings | Plan review: R1 changes_required, 4 (2 High, 2 Medium); R2 approved. Execution review: R1 approved, 0 |
| Handoff Score (X/7) | 6/7. Every AC has evidence and the execution review approved at round 1; the gate needed two runs |
| Rule Adherence (%) | 100 (10 of 10 sampled rules followed) |
| Prompt→commit time | Requested 2026-11-26; planned and reviewed 2026-11-26; executed and reviewed 2026-11-27; the commit waits for Mat |

### Rules Sampled for Adherence Check

| Rule | Source | Followed? |
|------|--------|-----------|
| Independent review; no self-approval | AGENTS.md §Dual-Agent Workflow | Yes. Codex reviewed the plan and the execution; no verdict was written locally |
| Never commit, stage or push without Mat | AGENTS.md §Commits | Yes. H2-5 is a draft only |
| Red before Green, by assertion | AGENTS.md §Testing | Yes. Rows 1, 2, 4, 6 and 8 failed by assertion (`red-check` 0 problems), and rows 4 and 6 again after their harness fixes |
| No expectation edited at Green | The plan (S3) | Yes. Only the four D-1422 expectations changed, at Red |
| Keep line endings; measure in bytes | Session 70 RULE-5 | Yes. `eol-check` 0 problems over the scope paths |
| No home path in a tracked file | AGENTS.md | Yes. `check_home_path` ok |
| Never read the user's real capture inbox or app data | The plan; GUARDRAILS | Yes. Every test uses temp folders and scratch app data |
| No Electron on the dev PC | Grouping D-1411 | Yes. Every Electron run was on mini-air through `e2e_remote.py` |
| Never raise a timeout or retry to green | AGENTS.md §Testing | Yes. D-1435 sets AC-151.14's existing test budget; D-1438 reran the gate unchanged with nothing excused |
| Change no file outside the plan's paths | The plan §Files Modified | Yes. `scope-paths` 0 problems |

---

## Instruction Coverage

```yaml
schema: v1
session:
  id: "b1d467ba-37b7-49d9-84d8-77aaa1f34169"
  task_class: tdd
  outcome: success
sections:
  - id: priority_0_system_constraints_non_negotiable
    cited: true
    influence: 3
  - id: planning_contract
    cited: true
    influence: 3
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
    - .agent/docs/e2e-remote-host.md
    - .agent/schemas/reflection.v1.yaml
    - docs/execution/reflections/TEMPLATE.md
    - .agent/context/handoffs/TEMPLATE.md
    - docs/execution/reflections/2026-11-26-ytdlp-challenge-and-cookie-test-reflection.md
decisive_rules: [P0:never-commit-or-push-without-human-approval, P0:keep-line-endings, P1:red-before-green-by-assertion, P1:never-raise-a-timeout-or-retry-to-green, P1:independent-review-no-self-approval]
conflicts:
  - "S5 says to rerun a failing existing test alone once and otherwise stop, and AGENTS.md says never retry to green; the gate's nine load timeouts were rerun alone (99 of 99) and then the whole gate once, unchanged, under D-1438, disclosed and judged by the execution review."
note: "The Capture page names the saved key, lists only the chosen inbox folder and shows scroll bars on a zoomed image."
slim_candidate: ["H2-1's view_file row repeats what H2-2's validator checks.", "Sibling AC cross-reference rows in each handoff, which the validator requires but no reader uses."]
overthinking_observed: false
review_churn:
  rounds_to_approval:
    plan: 2
    execution: 1
  findings_per_round:
    - review: plan
      round: 1
      critical: 0
      high: 2
      medium: 2
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
  finding_categories: {boundary_validation: 2, contract_drift: 2}
  verdicts:
    changes_required: 1
    approved: 2
meu_work_classes: [correctness, correctness, correctness]
```

The review churn counts the ledger's recorded rounds in the session's two loops. The plan loop, `cki-plan-2026-11-26-capture-key-inbox-scrollbars`, asked for changes at round 1 (2 blocking, `intent_achieved=partial`, `usage` 12,426,215) and approved at round 2 (`intent_achieved=yes`, `usage` 10,210,239). The execution loop, `cki-execution-2026-11-26-capture-key-inbox-scrollbars`, approved at round 1 of 6 with no findings and `intent_achieved=yes` (`usage` 9,580,330).
