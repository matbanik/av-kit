---
date: "2026-11-17"
project: "2026-11-15-docs-path-hygiene"
meus: []
plan_source: "docs/execution/plans/2026-11-15-docs-path-hygiene/implementation-plan.md"
template_version: "2.0"
---

# 2026-11-17 Meta-Reflection

> **Date**: 2026-11-17. Planned and plan-reviewed on 2026-11-15; executed, reviewed and closed on 2026-11-17.
> **MEU(s) Completed**: none (no MEU). Session 83 `docs-path-hygiene` is the ninth session of the post-rc.3 triage residuals grouping (`.agent/context/grouping/2026-11-15-post-rc3-triage-residuals-session-grouping.md` §3, row 83). It ran on `main` from `86ee8e3`.
>
> - **The install folder** (`INSTALL-FOLDER-NAME-MISMATCH`, `resolved`). `docs/build-plan/07-distribution.md:40` and `README.md:174-175` name `Programs/av-kit-ui`, the folder electron-builder really makes, and the install layout loses its `resources/extra/` level (D-811 applied, D-991, D-996). The package is not renamed and the older round-trip scripts keep their bytes (D-990).
> - **The home folder** (`TRACKED-FILES-HOLD-HOME-PATH`, `resolved`; D-817 A). The new standard-library tool `tools/check_home_path.py` refuses any tracked or untracked (not ignored) file outside `.agent/fleet/hub/` that holds the home folder's full path, in UTF-8, UTF-16 and UTF-32 and in its usual spellings, and prints `path:line` only (D-988). `tools/home_path_allowlist.txt` exempts the 60 evidence files by name and content digest (D-997). A new `home-path` D6 row runs it in every session's gate. The six live files now write `~`, `C:/Users/YOU` or the fixture user `C:/Users/avkit` (D-992), and the register scrub of `CLOSEOUT-SELFTEST-ANCESTOR-AGENT-DIR` writes `~` (D-994).
>
> **Plan Source**: `docs/execution/plans/2026-11-15-docs-path-hygiene/implementation-plan.md`

---

## Execution Trace

### Friction Log

1. **What took longer than expected?**
   - **The plan review.** It took three rounds on 2026-11-15. Round 1 found that the allow-list bound file names, not contents (R1-F1), that a byte-only matcher missed UTF-16 text (R1-F2), that the pattern matched longer user names (R1-F3) and that H1-4 compared the API folder to HEAD (R1-F4). The R1-F2 fix then classified unmarked UTF-16 with CJK text as binary and skipped it (R2-F1). Round 3 approved with 0 findings. Every finding was in the check's design, not in the doc fixes.
   - **The handoff's first validation.** H1-6 first refused with `1 plan AC(s) never appear in handoff ... AC-40`. The plan quotes the MEU-40 test title `MEU-40 AC-40.33 interactive request lifecycle` in its fixture table, and the validator reads every `AC-` token in the plan as a plan AC. The handoff's AC-15 row now names that suite and says AC-40.33 is MEU-40's criterion (RULE-1).

2. **What instructions were ambiguous?**
   - **The row-0 receipt for `ui-tests`.** The plan's gate says `py-tests` and `ui-tests` excuse only ids that row 0's receipts show failing, but row 0's listed steps ran only the two edited Vitest files. Row 0 also ran the full Vitest suite into `dph-base-ui-full.txt` (D-1084); it excused nothing.
   - **The register's date.** Row 7 asks for today's `last_checked`, while the plan's template text carries 2026-11-15. The register says 2026-11-17, the day the rows ran (D-1085).

3. **What instructions were unnecessary?**
   - H2-1's `view_file` row, because H2-2's validator reads the same template and schema (as Sessions 81 and 82 noted).

4. **What was missing?**
   - **The secret files in a whole-tree scan.** The plan's `CHECK` reads every tracked and untracked (not ignored) file. It excluded the hub but not the files no agent may open (`.mcp.json`, `mcp-token.txt`, `.claude.json`, `.env`, `.claude/settings.local.json`). Execution added the exclusion by name before any stat or read, in `CHECK`, `inventory.py` and the baseline walk (D-1081), and AC-5's third test proves it (RULE-2).
   - **A guard on an unreadable allow-list.** The plan's draft let an allow-list that exists but cannot be read raise a traceback. A `try`/`except` now exits 2 with a fixed message, which the reviewer confirmed by injection.
   - **An LF write in H2-5's cell.** The cell writes the commit draft with `pathlib.Path.write_text`, which on Windows writes CRLF. The draft was rewritten as LF bytes after the row ran (RULE-3).

5. **What did you do that wasn't in the prompt?**
   - **Generated the row wrappers** with `gen-wrapper.py`: the same five-line header (the repo folder, `ELECTRON_RUN_AS_NODE` cleared, `PYTHONIOENCODING`, `PYTHONDONTWRITEBYTECODE`, `RECEIPTS_DIR`) and the row's task cell verbatim, so no cell was retyped.
   - **Drafted the handoff with marked slots** for the gate's values and filled them from the receipts with `fill-handoff.py`, which refuses a slot left, a CR byte or the home folder.
   - **A focus-entry script** (`apply-focus.py`) that refuses unless `current-focus.md` is pure CRLF, has no Session 83 entry and the entry holds no home path, and proves the old tail unchanged.

### Quality Signal Log

6. **Which tests caught real bugs?**
   - The repository Red (row 4) is the real catch: with the allow-list in place, `CHECK` refused the tree with `found=12`, equal to the 12 live pairs counted at row 0. After the fixes it passed with `allowlisted=60`, and with an empty list it found exactly the 118 evidence lines in 60 files.
   - The 47 unit cases failed at Red only on the missing tool (`assert False` on `is_file()`). The design bugs they guard (R1-F1 to R2-F1) were found by the plan review's probes, and AC-22 and AC-23 now pin them.

7. **Which tests were trivially obvious?**
   - AC-6's usage errors and AC-4's missing allow-list are simple exit-code pins, but they carry the no-echo and no-traceback rules that keep the path out of output.

8. **Did pyright/ruff catch anything meaningful?**
   - ruff `check --fix` removed one unused import from the copied `scope-check.py` (D-1083). Every other lint, the UI typecheck and `eslint --max-warnings 0` were clean in every run.

### Workflow Signal Log

9. **Was the FIC useful as written?**
   - Yes. The names `CHECK`, `ALLOW`, `DIGEST`, `HOME_RE`, `LIVE_SET` and `EVIDENCE_SET` gave the plan, the tests, the handoff and both reviews one vocabulary. The execution review approved at round 1 with 0 findings.

10. **Was the handoff template right-sized?**
    - Mostly. The evidence records and the gate table were worth it. The AC table's Source column added little for a session whose ACs all trace to D-817 and the plan's decisions.

11. **How many tool calls did this session take?**
    - Not counted exactly. The executor's transcript ran to a few hundred calls, rows 0 to H2-5, across one context compaction. Planning, the review dispatches and H1-7 ran in the coordinator's session.

12. **Which rows were delegated, to which subagent (harness + model), and did any delegated result need rework?**
    - The coordinator (Claude Code) delegated rows 0 to H1-6b and H2-1 to H2-5 to one executor subagent (Claude Code, Claude Opus 5.5). It ran the plan and execution review dispatches and H1-7 itself.
    - No row went to `av-kit-builder`, `av-kit-verifier` or `av-kit-peer-reviewer`; the optional §5a expert pass was not used. No delegated result needed rework after the review.
    - Codex reviewed the plan and the execution as the independent reviewer. That is not delegation.

### Decisions Log

- Run `tools/check_home_path.py` as a new `home-path` D6 row in every session's gate, not in CI — [D-988](../plans/2026-11-15-docs-path-hygiene/implementation-plan.md)
- Allow-list later evidence that holds the path by name, never this session's own files — [D-989](../plans/2026-11-15-docs-path-hygiene/implementation-plan.md)
- Leave the install round-trip scripts unchanged — [D-990](../plans/2026-11-15-docs-path-hygiene/implementation-plan.md)
- Give the README's hand-written MCP config the real install folder too — [D-991](../plans/2026-11-15-docs-path-hygiene/implementation-plan.md)
- Write `~`, `C:/Users/YOU` or `C:/Users/avkit` in place of the home folder, by file kind — [D-992](../plans/2026-11-15-docs-path-hygiene/implementation-plan.md)
- Fix a further live doc file found at row 0, but stop on a test, source, config or script file — [D-993](../plans/2026-11-15-docs-path-hygiene/implementation-plan.md)
- Change the register through a plan-local `issue-resolve.py` with a `--scrub` mode — [D-994](../plans/2026-11-15-docs-path-hygiene/implementation-plan.md)
- The gate's steps, the `dph-` receipt and loop names, and content-bound baselines — [D-995](../plans/2026-11-15-docs-path-hygiene/implementation-plan.md)
- The install layout loses its `resources/extra/` level — [D-996](../plans/2026-11-15-docs-path-hygiene/implementation-plan.md)
- Bind each allow-list entry to a content digest of its file — [D-997](../plans/2026-11-15-docs-path-hygiene/implementation-plan.md)
- `red-check.py` takes the D-919 pytest header form — [D-1080](../../../.agent/context/handoffs/2026-11-15-docs-path-hygiene-handoff.md)
- `CHECK`, `inventory.py` and the baseline walk never open the secret files — [D-1081](../../../.agent/context/handoffs/2026-11-15-docs-path-hygiene-handoff.md)
- AC-22's PNG fixture is found at line 4 — [D-1082](../../../.agent/context/handoffs/2026-11-15-docs-path-hygiene-handoff.md)
- Plan scripts are ruff-formatted, with E501 accepted — [D-1083](../../../.agent/context/handoffs/2026-11-15-docs-path-hygiene-handoff.md)
- Row 0 also records the full Vitest suite for the gate's excuse rule — [D-1084](../../../.agent/context/handoffs/2026-11-15-docs-path-hygiene-handoff.md)
- The register's dates are the day the rows ran — [D-1085](../../../.agent/context/handoffs/2026-11-15-docs-path-hygiene-handoff.md)
- The tests start `CHECK` with `sys.executable` — [D-1086](../../../.agent/context/handoffs/2026-11-15-docs-path-hygiene-handoff.md)

---

## Pattern Extraction

### Patterns to KEEP
1. **A repository Red and Green for a gate check.** Running `CHECK` on the real tree before and after the fixes (rows 4, 9 and 10), with an empty-list negative that must equal the evidence count, proved the check finds what it should and nothing else.
2. **Bind an exemption to content, not a name** (D-997). The plan review's R1-F1 showed a name-only allow-list lets new paths into old evidence; the digest makes any change visible.
3. **Fill the handoff's gate values from the receipts by script.** No count in the handoff was typed by hand, and the script refused a CR byte or the home folder.

### Patterns to DROP
1. **Quoting another MEU's AC-bearing test title in a plan without saying so.** The validator reads it as a plan AC.

### Patterns to ADD
1. **Say in the plan when an `AC-` token belongs to another MEU** (RULE-1).
2. **Exclude the secret files in any tool that walks the whole tree, from plan time** (RULE-2).
3. **Write LF files in task cells with bytes, not `write_text`** (RULE-3).

### Calibration Adjustment
- **Estimated:** no token budget. The plan set round caps of 3 (plan) and 6 (execution).
- **Actual time** (local time, from the receipts' mtimes):
  - On 2026-11-15, the plan review ran three rounds, dispatched at 14:59, 15:14 and 15:25, and approved at round 3.
  - On 2026-11-17:
    - Row 0's baseline (with the base Python and Vitest suites) ended at 02:16.
    - Rows 1 to 10 ran from 02:18 to 02:23: Red, Green, the allow-list, the repository Red, the doc and test edits, both register calls, the D6 row and the repository Green.
    - The H1-2 gate ran from 02:26 to 02:32 and passed on its first run.
    - H1-3 to H1-6b ended at about 02:35.
    - The execution review ran from 02:36 to 02:48 and approved at round 1.
- **Tokens:** plan review 5,807,652, 5,131,298 and 4,985,917 (rounds 1 to 3); execution review 7,185,149.
- **Adjusted estimate** for a tooling session with a new gate check: plan three rounds when the check's matching rules are new, about 5 to 7M tokens per review round, and about 6 minutes per full gate run when the host is quiet.

---

## Next Session Design Rules

```
RULE-1: When a plan quotes a test title or text that holds another MEU's AC id (such as "AC-40.33"), it says so next to the quote, and the handoff's AC table names it in the row that uses it.
SOURCE: Session 83 H1-6: validate_closeout_artifacts.py refused "1 plan AC(s) never appear in handoff ... AC-40", because the plan quoted the MEU-40 suite title in its fixture table.
EXAMPLE: before, the plan's fixture table quoted `MEU-40 AC-40.33 interactive request lifecycle` with no note; after, the plan marks it as MEU-40's criterion and the handoff's AC-15 row names the suite.
```

```
RULE-2: Any plan tool that reads every tracked or untracked file drops the secret file names (.mcp.json, mcp-token.txt, .claude.json, .env, .env.*, .claude/settings.local.json) and .agent/fleet/hub/ before any stat or read, and a test proves no read reached them.
SOURCE: Session 83 D-1081: the approved plan's CHECK excluded the hub only; the exclusion and AC-5's patched-reader test were added at execution.
EXAMPLE: before, "scan tracked and untracked files outside .agent/fleet/hub"; after, "outside .agent/fleet/hub and the secret names, never opened", with a reader that fails the test on a secret path.
```

```
RULE-3: A task cell that writes an LF file on Windows writes bytes (write_bytes, or open with newline="\n"), never pathlib.Path.write_text, and the row checks the CR count.
SOURCE: Session 83 H2-5: the cell's write_text wrote the commit draft with CRLF on Windows; it was rewritten as LF bytes and checked to 0 CR.
EXAMPLE: before, Path(p).write_text(chr(10).join(lines), encoding='utf-8'); after, Path(p).write_bytes(chr(10).join(lines).encode('utf-8')) and a 0-CR check.
```

---

## Next Day Outline

1. **Next:** Session 88 `queue-pause-feedback`, after the coordinator commits Session 83. The coordinator writes its start prompt.
2. **Scaffold changes needed:** none. Every later session's gate now runs the `home-path` D6 row; a new evidence file that holds the home folder fails it, so later sessions write `~` or "the home folder" from the start.
3. **Patterns to bake in from today:** RULE-1 to RULE-3 here, Session 82's RULE-1 to RULE-3 and the carried rules in the start prompt.
4. **Codex validation scope:** each session's own plan and execution loops.
5. **Time estimate:** set by each session's plan.
6. **Still open for Mat:**
   - The commit of Session 83, with no push from the agent.
   - The plan's Status line changed after the plan review approved (the handoff gives both hashes).

---

## Efficiency Metrics

| Metric | Value |
|--------|-------|
| Total tool calls | A few hundred in the executor's transcript, rows 0 to H2-5; not counted exactly |
| Time to first green test | Row 2 at 02:19 on 2026-11-17, about a minute after row 1's Red |
| Tests added | 47 Python cases in `tests/tooling/test_check_home_path.py` (3082 passed in the gate against the row-0 3035); UI unit tests unchanged at 1578 in 137 files, with two fixture files edited |
| Codex findings | Plan review: R1 changes_required (2 High, 2 Medium), R2 changes_required (1 High), R3 approved with 0 open. Execution review: R1 approved, 0 findings |
| Handoff Score (X/7) | 7/7. Every AC has evidence, the gate passed on its first run, and the execution review approved at round 1 with 0 findings |
| Rule Adherence (%) | 100 (10 of 10 sampled rules followed) |
| Prompt→commit time | Planned 2026-11-15; executed, approved and closed 2026-11-17; the coordinator commits without a push |

### Rules Sampled for Adherence Check

| Rule | Source | Followed? |
|------|--------|-----------|
| Independent review; no self-approval | AGENTS.md §Dual-Agent Workflow | Yes. Codex reviewed the plan and the execution; the executor never dispatched or wrote a verdict |
| The executor never commits, stages or pushes | The executor brief; AGENTS.md §Commits | Yes. H2-5 is a draft and a path list only |
| Red before Green | AGENTS.md §Testing | Yes. Row 1 failed by assertion before row 2, and the repository Red (row 4) before the fixes |
| Keep line endings; measure in Python bytes | Session 70 RULE-5 | Yes. `SKILL.md`, `06-gui.md`, `07-distribution.md`, `commands.md`, `current-focus.md` and `metrics.md` stayed CRLF; the other edited files and every new file are LF |
| No home-folder path in any file or receipt | The executor brief; D-817 | Yes. `CHECK` passes on the tree with the review, handoff and reflection in it |
| Never open the secret files | The executor brief | Yes. The tools drop them by name before any read (D-1081) |
| Change the register only through `tools/issue_triage*` and `issue-resolve.py` | The executor brief | Yes. Rows 7 and 10 |
| Evidence files keep their bytes | The plan's goal anchor | Yes. All 60 digests match; the reviewer recomputed them |
| Unset `ELECTRON_RUN_AS_NODE` before identity and Electron steps | Session 85 RULE-2 | Yes. Every wrapper clears it in its header |
| Leave other sessions' files alone | The executor brief | Yes. `baseline-dirty-hashes checked: 0` and `scope-check: ok` |

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
  workflows: [execution_session, issue_triage]
  roles: [orchestrator, coder, tester]
  skills: []
  refs:
    - .agent/docs/human-decision-protocol.md
    - .agent/schemas/reflection.v1.yaml
    - docs/execution/reflections/TEMPLATE.md
    - .agent/context/handoffs/TEMPLATE.md
    - docs/execution/reflections/2026-11-15-ready-handshake-reflection.md
    - .agent/context/handoffs/2026-11-15-docs-path-hygiene-plan-critical-review.md
    - .agent/context/handoffs/2026-11-15-docs-path-hygiene-implementation-critical-review.md
decisive_rules: [P0:never-commit-or-push-without-human-approval, P0:no-home-folder-path-in-files, P0:never-open-secret-files, P0:keep-line-endings, P1:red-before-green]
conflicts:
  - "The plan's CHECK scans every untracked file, which would open the secret files the brief forbids; execution excluded them by name (D-1081)."
  - "The plan quotes the MEU-40 test title AC-40.33, which the handoff validator counts as a plan AC; the handoff's AC-15 row names it."
note: "A tooling session: the plan review needed three rounds on the check's matching rules, then the gate passed first time and execution approved at round 1."
slim_candidate: ["H2-1's view_file row repeats what H2-2's validator checks.", "The handoff AC table's Source column when every AC traces to one ruling."]
overthinking_observed: false
review_churn:
  rounds_to_approval:
    plan: 3
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
      high: 1
      medium: 0
      low: 0
    - review: plan
      round: 3
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
    boundary_validation: 2
    fix_generalization_miss: 1
    contract_drift: 1
    other: 1
  verdicts:
    changes_required: 2
    approved: 2
meu_work_classes: []
```

The review churn counts the ledger's recorded rounds in the two loops, `dph-plan-2026-11-15-docs-path-hygiene` and `dph-execution-2026-11-15-docs-path-hygiene`. R1-F2 and R1-F3 are boundary validation, R2-F1 is a miss in R1-F2's fix, R1-F4 is contract drift in H1-4's baseline, and R1-F1 (a control defeat: the allow-list bound names, not contents) is `other`. No finding recurred.
