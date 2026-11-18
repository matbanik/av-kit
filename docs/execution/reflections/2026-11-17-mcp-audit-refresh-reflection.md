---
date: "2026-11-18"
project: "2026-11-17-mcp-audit-refresh"
meus: []
plan_source: "docs/execution/plans/2026-11-17-mcp-audit-refresh/implementation-plan.md"
template_version: "2.0"
---

# 2026-11-18 Meta-Reflection

> **Date**: 2026-11-18. Planned on 2026-11-17; plan-reviewed, executed, reviewed and closed on 2026-11-18.
> **MEU(s) Completed**: none. Session 92 `mcp-audit-refresh` is audit and tool-description debt with no MEU (D-1155), as Sessions 78, 79 and 90 were. It is from the 2026-11-17 value-triage grouping (`.agent/context/grouping/2026-11-17-value-triage-session-grouping.md` §3, row 92). It ran on `main` from `cba97fe`, with Session 91's plan still uncommitted.
>
> - **Census proofs** (`MCP-AUDIT-CENSUS-PROBE-SINGLE-SHOT`, `resolved`). In container mode the audit tries each URL's direct fetch up to three times about 5 s apart, and a proof holds when any try is blocked. The probes moved unchanged to `mcp-server/scripts/audit/network-proof.ts` behind a test seam, and `.agent/workflows/mcp-audit.md` says so in one note (`NETWORK_PROOF_SAMPLE`, `PROBES_SEAM`, `NETWORK_PROOF_GATHER`, `FORBIDDEN_IMPORTS_KEPT`, `WORKFLOW_NOTE`; D-1156, D-1160).
> - **The `avkit_capture` description** (`MCP-ACTION-DESCRIPTIONS-HIDDEN-FROM-MODEL`, `resolved`; D-1134 A, Mat). It is built from the tool's action text: 3,981 characters in 14 lines. It leads with calling `image` to view a frame or sheet and calling `sheet` again over a narrower span to zoom, then has the four markers and one line per action. The action text, every input schema and the other seven descriptions are byte-identical (`CAPTURE_TOOL_DESCRIPTION`, `DESC_SHAPE`, `DESC_TRACE`, `DESC_PIN`; D-1157). The three Session 64 eval tasks passed on it, one fresh Haiku run each (`EVAL_RERUN`, D-1158).
> - **The baseline** (`MCP-AUDIT-BASELINE-PENDING-CROP`, `resolved`; D-1159 A, Mat). One authoritative Windows audit (104/104 pass, cleanup ok) recorded convert probe and capture crop, frames, sheet and export in the committed baseline and report, and `BASELINE_PENDING` is empty (`AUDIT_RUN`, `AUDIT_TMP`, `BASELINE_RECORD`, `PENDING_EMPTIED`).
> - **A new issue**, `EVAL-HARNESS-DESCRIBE-CP437-MOJIBAKE` (open, D-1163). Session 64's eval tooling captures the tool surface through a PowerShell redirect that decodes UTF-8 through cp437, so Session 64's own eval read a corrupted surface.
>
> **Plan Source**: `docs/execution/plans/2026-11-17-mcp-audit-refresh/implementation-plan.md`

---

## Execution Trace

### Friction Log

1. **What took longer than expected?**
   - **Row 5, the eval.** The first describe receipt and its three prompts held cp437 mojibake: every arrow and dash in the served text came through as box-drawing characters. The coordinator stopped the row before any subagent ran and ruled D-1186. The describe was re-captured as raw bytes, the plan's `eval-rerun.py prompts` gained a guard that refuses mojibake and requires the expected description verbatim, and the prompts were rebuilt. A round-trip receipt proves the defect was only the decoding (RULE-1).
   - **The handoff**, as in Sessions 74, 82 and 88 to 90. A generator script built it from the receipts and refused a quoted line that was not in its receipt, a home path, or a scratch path outside a record's `command` field.
   - The product rows were quick. From the receipts' mtimes:

     | Step | Time |
     |---|---|
     | Row 0 baseline | 08:47 |
     | Census Red | 08:52 |
     | Census Green | 08:53 |
     | Description Red | 08:54 |
     | Description Green | 08:56 |
     | Eval check | 09:09 |
     | Coverage Red | 09:11 |
     | Authoritative audit | 09:12 |
     | Gate | 09:20 |

2. **What instructions were ambiguous?**
   - **AC-15's "with neither, no issue is added."** The clause is about D-1161 and D-1162, the contingent outcomes. D-1163's tracking issue came from a separate execution decision, and it was added after row 8's check had read `issues added: []`. The handoff discloses the order.
   - **Where execution decisions go.** The brief said the handoff's Decision Log is `None.` and execution decisions go in the plan YAML. That needed one H1-6 step to append D-1163 and D-1164, so the plan's sha moved a second time after approval (`mar-plan-decisions.txt`).

3. **What instructions were unnecessary?**
   - H2-1's `view_file` row, because H2-2's validator reads the same template and schema (as in Sessions 74, 81, 82 and 88 to 90).

4. **What was missing?**
   - **A raw-bytes rule for tool output fed to a model.** Session 64's `eval-run.md` step 3 redirects native output in PowerShell, which re-decodes it through the console code page. No check in Session 64 or in this plan compared the captured surface with the served one until D-1186 added it (RULE-1).
   - **A parsed read of the register in row 8's check.** It sliced an issue's block at the first `- id: `, which also opens each nested `enrichment.decision_log` entry. So it never saw the `resolution_path` that follows the enrichment, and it failed on a correct register (D-1164, RULE-2).
   - **Coordinator-owned paths in the scope rules.** Six registry and agent-definition paths changed after row 0 through the coordinator's own work. The plan's scope check had no class for them until D-1185 (RULE-3).

5. **What did you do that wasn't in the prompt?**
   - **Ran each Validation cell verbatim from a `.ps1` file**, with the environment header (`make-row-ps1.py`), and marked rows by script (`mark-row.py`), so `task.md` stayed LF.
   - **Made every named edit with a byte-level Python script** that keeps the file's line endings. CRLF files stayed CRLF, and `eol-check` read 0 problems on 19 paths.
   - **Summed the eval spend** from the three subagents' transcript usage records, read-only, because no count had been relayed (`mar-eval-spend.txt`).
   - **Kept every superseded receipt**: the three `-attempt1` eval files and the failing `mar-row8-check.txt`.

### Quality Signal Log

6. **Which tests caught real bugs?**
   - **The three Reds were real assertion failures, not setup errors** (`red-check.py` on each):
     - census at one sample: `Tests  7 failed | 6 passed (13)`;
     - the old 145-character description: `Tests  3 failed | 2 passed (5)`;
     - coverage against the row-0 baseline: `Tests  4 failed | 14 passed (18)`.
   - **The D-1186 guard caught a real defect.** It refused the attempt-1 receipt with exit 2 (`mar-eval-prompts-guard-negative.txt`), so no Haiku run read a corrupted surface. The same defect sits unnoticed under Session 64's own eval.
   - **`desc-check.mjs` against row 0's record** is the check that proves D-1134 A's limits: `captureDescriptions`, every `_meta` map, every input schema and the other seven descriptions unchanged on the built server.

7. **Which tests were trivially obvious?**
   - AC-5's `undefined` cases (authoritative mode, no fixtures, no matching record) are short by design. They pin that the move kept the guards.

8. **Did pyright/ruff catch anything meaningful?**
   - No product issue; the MCP typecheck was clean at every row. ruff flagged only style in the session's own scratch scripts (an unused `noqa`, `re.S` against `re.DOTALL`), and those were fixed before use.

### Workflow Signal Log

9. **Was the FIC useful as written?**
   - Yes. The contract names gave the tests, the handoff and both reviews one vocabulary. Both reviews approved at round 1 with 0 findings.

10. **Was the handoff template right-sized?**
    - Yes for a no-MEU session with three parts. The Departures section carried the judgment calls (D-1163, D-1164, D-1185, D-1186, the plan's sha moves), and the reviewer cited them.

11. **How many tool calls did this session take?**
    - Not counted exactly. The executor's transcript ran to a few hundred calls, rows 0 to H2-6, across context compactions. Planning, both review dispatches, row 5's eval subagents and H1-7 to H1-7b ran in the coordinator's session.

12. **Which rows were delegated, to which subagent (harness + model), and did any delegated result need rework?**
    - The coordinator (Claude Code) delegated rows 0 to H1-6b and H2-1 to H2-6 to one executor subagent (Claude Code, Claude Opus 5.5). It ran the review dispatches and H1-7 to H1-7b itself.
    - Row 5's three eval runs were fresh general-purpose subagents with model haiku, which the coordinator spawned. They are the measurement's subjects, not delegated rows.
    - No row went to `av-kit-builder`, `av-kit-verifier` or `av-kit-peer-reviewer`. No delegated result needed rework after review.

### Decisions Log

- No MEU: the description change runs under its issue with this plan's ACs — [D-1155](../plans/2026-11-17-mcp-audit-refresh/implementation-plan.md)
- A census proof holds when any of three samples about 5 s apart is blocked, which departs from the issue's "every sample" — [D-1156](../plans/2026-11-17-mcp-audit-refresh/implementation-plan.md)
- The description's layout: lead, four markers, one line per action, each sentence traced to the action text — [D-1157](../plans/2026-11-17-mcp-audit-refresh/implementation-plan.md)
- The acceptance check is Session 64's three eval tasks, one fresh Haiku run each, on the real surface — [D-1158](../plans/2026-11-17-mcp-audit-refresh/implementation-plan.md)
- The probes and the census block move to `network-proof.ts` behind a `NetworkProbes` seam, and `AuditDeps` is unchanged — [D-1160](../plans/2026-11-17-mcp-audit-refresh/implementation-plan.md)
- If the audit had failed: restore the baseline, report and coverage test, and continue (not taken) — [D-1161](../plans/2026-11-17-mcp-audit-refresh/implementation-plan.md)
- If the eval had failed: keep the description and register the miss (not taken) — [D-1162](../plans/2026-11-17-mcp-audit-refresh/implementation-plan.md)
- Register Session 64's cp437 describe capture as its own issue — [D-1163](../plans/2026-11-17-mcp-audit-refresh/implementation-plan.md)
- Rerun row 8's check with its block boundary at the next issue, and keep the failing receipt — [D-1164](../plans/2026-11-17-mcp-audit-refresh/implementation-plan.md)

**Read from their own logs, not listed:**
- D-1159 is Mat's ruling (`Human-approved`).
- D-1131 to D-1134 are grouping §8, and D-499 is on `MCP-AUDIT-BASELINE-PENDING-CROP`.
- D-1185 (the six coordinator-owned paths) and D-1186 (the raw re-capture and the guard) are the coordinator's rulings, recorded in the handoff's Departures.

**The `decision_sources` probe was re-run at H2-2** (`mar-decision-probe.txt`), with the plan, the handoff, the grouping, the register and the two decision issues:
- it reads D-499 and D-1155 to D-1162 (planning), D-1131 to D-1134 (grouping), and D-1163 and D-1164 (execution);
- no `chosen` starts with "Pending";
- no brace slot is left in the plan's decision YAML;
- grouping §8 holds no new row since plan time.

---

## Pattern Extraction

### Patterns to KEEP
1. **Prove what the model reads, byte for byte.** The eval prompts were compared with the served surface and with Session 64's prompt text before any run, so the three passes measure the description Mat approved.
2. **Pin the unchanged parts against a row-0 record.** `desc-check.mjs` read every description, `_meta` map and schema at row 0 and compared the built server against them, which kept D-1134 A's scope exact.
3. **Keep the failing receipt next to its rerun.** `mar-row8-check.txt` and the attempt-1 eval files stayed, so the reviewer could check that each correction changed only what its decision named.

### Patterns to DROP
1. **Slicing YAML by a text marker in a check.** A nested `- id: ` broke row 8's check on a correct register.

### Patterns to ADD
1. **Captured tool output is read and written as raw bytes, and a check refuses mojibake** (RULE-1).
2. **A register check parses the YAML** (RULE-2).
3. **The plan names the coordinator-owned paths as foreign at plan time** (RULE-3).

### Calibration Adjustment
- **Estimated:** no token budget. Round caps of 3 (plan) and 6 (execution). The plan put the eval at 0.5 to 2 million tokens.
- **Actual time** (local time, from the receipts' mtimes):

  | Step | Time |
  |---|---|
  | Plan review approved at round 1 | 07:33 |
  | Row 0 | 08:47 |
  | Census rows | 08:52 to 08:53 |
  | Description rows | 08:54 to 08:56 |
  | Eval check, after the D-1186 re-capture | 09:09 |
  | Coverage Red, then the authoritative audit | 09:11 to 09:12 |
  | The H1-2 gate, first run, at an 18.2 % host load | 09:20 |
  | Execution review approved at round 1 (`mar-exec-console-r1.txt`) | 09:55 |

- **Tokens:**

  | Item | Tokens |
  |---|---|
  | Plan review, round 1 | 9,419,648 |
  | Execution review, round 1 | 20,487,519 |
  | Row 5's three Haiku eval runs | 860,003 |

- **Adjusted estimate** for a no-MEU MCP session with an authoritative audit and a model eval:
  - about 10M tokens for the plan review and 20M for the execution review;
  - about 1M tokens for three Haiku eval runs;
  - a few minutes for one authoritative audit on a quiet host.

---

## Next Session Design Rules

```
RULE-1: Any tool output that a model will read (an MCP describe, a prompt built from it) is captured as raw bytes by a script, never through a PowerShell redirect of native output, and a check compares it with the expected text and refuses mojibake before any run uses it.
SOURCE: Session 92 row 5 (D-1186, D-1163): the describe receipt captured the eval-run.md way held cp437 mojibake for every arrow and dash; Session 64's own eval had run on the same corrupted surface.
EXAMPLE: before, `node eval-harness.ts describe *> receipt.txt`; after, a Python subprocess writes stdout bytes, and the prompt builder exits 2 on a mojibake sequence or a description that differs from the expected file.
```

```
RULE-2: A plan check that reads known-issues.yaml parses it (yaml.safe_load or tools/issue_triage.model) and reads fields by key; it never cuts an issue's block at a text marker that nested entries also use.
SOURCE: Session 92 row 8 (D-1164): the check cut at the first '- id: ', which also starts each enrichment.decision_log entry, so it missed a correct resolution_path and failed.
EXAMPLE: before, blk = text[i:text.index('- id: ', i + 1)]; after, issue = {x['id']: x for x in yaml.safe_load(text)['issues']}[ID].
```

```
RULE-3: A plan whose scope check runs while a coordinator works in the same tree names the coordinator-owned paths (the model registry overlay and the agent definitions) as a foreign class at plan time, binds them by hash at row 0, and leaves them out of the commit paths.
SOURCE: Session 92 H1-2 (D-1185): six coordinator-owned paths changed after row 0, and the scope step needed a coordinator ruling to class them.
EXAMPLE: before, a changed path outside Files Modified fails the scope step; after, the plan lists `.agent/model-registry.local.json` and `.claude/agents/*`, `.cursor/agents/*` as coordinator-owned, and the step records them with their hashes.
```

---

## Next Day Outline

1. **Next:** Session 93 `video-tail-frame`, MEU-160 as the coordinator relays, from its own plan folder. The grouping's §6 row still reads `proposed` with no MEU, and this session did not open Session 93's plan. Then Session 94, and Session 91 when Mat continues its plan-review loop. The prompt is at `C:/Temp/av-kit/next-session-prompt.md` (H2-6).
2. **Scaffold changes needed:** none.
3. **Patterns to bake in from today:**
   - RULE-1 to RULE-3 here, plus Session 74's rules and those it carried, all in the start prompt.
   - The committed baseline now holds all 75 served actions, so a later authoritative run compares against every one.
4. **Codex validation scope:** each session's own plan and execution loops.
5. **Time estimate:** set by the next plan.
6. **Still open for Mat:**
   - The commit of Session 92 by the coordinator, with no push from the agent. H2-5 has the draft and the path list.
   - `EVAL-HARNESS-DESCRIBE-CP437-MOJIBAKE`, open in the register.

---

## Efficiency Metrics

| Metric | Value |
|--------|-------|
| Total tool calls | A few hundred in the executor's transcript, rows 0 to H2-6; not counted exactly |
| Time to first green test | Census Green at 08:53, one minute after Red |
| Tests added | 18 MCP Vitest tests (553 in 38 files in the gate, against 535 in 36 at row 0): 13 in `mcp-server/tests/audit/network-proof.test.ts` and 5 in `mcp-server/tests/capture-description.test.ts`; four `coverage.test.ts` tests changed as §Test pins names |
| Codex findings | Plan review: R1 approved, 0 findings. Execution review: R1 approved, 0 findings |
| Handoff Score (X/7) | 7/7. Every AC has evidence, the gate passed on its first run, and both reviews approved at round 1 with 0 findings |
| Rule Adherence (%) | 90 (9 of 10 sampled rules followed) |
| Prompt→commit time | Planned 2026-11-17; executed, approved and closed 2026-11-18; the coordinator commits without a push |

### Rules Sampled for Adherence Check

| Rule | Source | Followed? |
|------|--------|-----------|
| Independent review; no self-approval | AGENTS.md §Dual-Agent Workflow | Yes. Codex reviewed the plan and the execution, and the executor never dispatched or wrote a verdict |
| The executor never commits, stages or pushes | The executor brief; AGENTS.md §Commits | Yes. H2-5 is a draft and a path list only |
| Red before Green, by assertion | AGENTS.md §Testing | Yes. Three Reds, each passed `red-check.py` |
| Never edit a test to pass (S3); M-7 assertion changes only as named | The plan's §Test pins | Yes. `outside the named edits: []` |
| `--update-baseline` only from a clean authoritative run (BASELINE_UPDATE_RULE) | The grouping §3; D-1159 A | Yes. 104/104, cleanup ok, no regression |
| Keep line endings; measure in Python bytes | Session 70 RULE-5 | Yes. `eol-check: 19 scope path(s), 0 problem(s)` |
| No raw home path in tracked files | The executor brief; Session 83 | Yes. The gate's `home-path` step passed |
| Change the registers only through `tools/issue_triage*` and the plan scripts | The executor brief | Yes. Row 8 and D-1163 |
| Never open a secret, a token file or another session's plan folder | The executor brief | Yes. The sibling folders were recorded by path only |
| Each row's Validation cell passes as written | The plan-review approval of the plan's text | No. Row 8's check failed on its own slicing defect and was rerun with one boundary moved (D-1164, RULE-2) |

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
    - docs/execution/reflections/2026-11-17-tts-fp16-guard-ship-reflection.md
    - docs/execution/reflections/2026-11-17-test-run-reliability-reflection.md
    - .agent/workflows/mcp-audit.md
    - .agent/context/handoffs/2026-11-17-mcp-audit-refresh-plan-critical-review.md
    - .agent/context/handoffs/2026-11-17-mcp-audit-refresh-implementation-critical-review.md
decisive_rules: [P0:never-commit-or-push-without-human-approval, P0:keep-line-endings, P0:never-edit-a-test-to-pass, P1:red-before-green, P1:baseline-update-only-from-clean-authoritative-run]
conflicts:
  - "Row 8's check required the three issues' fields but sliced the YAML at a nested marker, so it failed on a correct register; resolved by D-1164."
  - "AC-15 says no issue is added without D-1161 or D-1162, while D-1163 added a tracking issue after the check; disclosed in the handoff."
note: "No-MEU MCP session; an encoding defect in reused eval tooling was caught before any eval run; round-1 approvals on both loops."
slim_candidate: ["H2-1's view_file row repeats what H2-2's validator checks.", "The handoff restates per-row receipt lines that its evidence records already carry."]
overthinking_observed: false
review_churn:
  rounds_to_approval:
    plan: 1
    execution: 1
  findings_per_round:
    - review: plan
      round: 1
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
  finding_categories: {}
  verdicts:
    approved: 2
meu_work_classes: []
```

The review churn counts the ledger's recorded rounds in the session's two loops, `mar-plan-2026-11-17-mcp-audit-refresh` and `mar-execution-2026-11-17-mcp-audit-refresh`. Both approved at round 1 with 0 findings (`usage=9,419,648` and `usage=20,487,519`).
