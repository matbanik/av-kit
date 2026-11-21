---
date: "2026-11-21"
project: "2026-11-20-help-quick-start"
meus: ["MEU-162"]
plan_source: "docs/execution/plans/2026-11-20-help-quick-start/implementation-plan.md"
template_version: "2.0"
---

# 2026-11-21 Meta-Reflection

> **Date**: 2026-11-20 to 2026-11-21. Planned and plan-reviewed on 2026-11-20; executed, reviewed and closed on 2026-11-21.
> **MEU(s) Completed**: MEU-162 Help quick start (phase 6, matrix 6.23), from Mat's request of 2026-11-20 to turn each page's "How it works" card into a short guide with screenshots and ASD-STE100 steps. Session 99 `help-quick-start` ran on `main` from `f1ba411`; Session 100 (`e2e-devpc-clipboard`) ran in the same tree and committed `49ab790`, on which rows 8 to 10 and the gate ran.
>
> - **The quick start** (`QUICK_START_DATA`, `CARD_QUICK_START`; D-1289 A, D-1291). Each card header reads `Quick start · N steps`; open, the card shows one intro sentence, four or five numbered steps and a light and a dark screenshot with the same numbers on the controls. The card still starts closed on a first visit, and F1 works as before.
> - **Plain topics** (`PLAIN_TOPICS`, `CONSOLE_AND_SAVE`; D-1290 A, D-1296). 31 unpinned topics are rewritten in plain words under "More about this page" as closed `<details>`; the four pinned topics are kept, and three older tests name the new words (D-1296, Mat).
> - **The screenshots** (`HELP_SHOTS_GEN`, `DEMO_STAGE`, `PRIVACY_GUARD`; D-1292, D-1294, D-1297). `npm --prefix ui run help:shots` takes 14 WebP images from the real Electron app with demo data and refuses an image that shows a home folder; a step-hash test and an Electron test catch stale images.
> - **The STE gate** (`STE_GATE`, D-1293). The ASD-STE100 skill is vendored under `.agent/skills/asd-ste100/` (MIT), and `tools/help_guide_ste.py` lints the help text in a pytest.
> - **The proof.** The final gate passed every step: Vitest 1,657 in 149 files, tooling 574, the four help E2E suites, and `help-quick-start.test.ts` 27 of 27 over three runs in row 9.
>
> **Plan Source**: `docs/execution/plans/2026-11-20-help-quick-start/implementation-plan.md`

---

## Execution Trace

### Friction Log

1. **What took longer than expected?**
   - **Waiting on the shared tree.** Session 100 changed `ui/tests/e2e/electron-app.ts`, in this plan's read-only scope, before row 1 (stop S4; Mat said "continue"). After row 7 it asked for a freeze of `ui/src`, builds and Electron launches for its own full run, so row 8 started about five hours after row 7.
   - **Row 7 stopped at S5.** Row 6's rewrite changed topic words that three older tests pinned. The row waited for Mat's ruling (D-1296) from 00:01 to 06:35.
   - **Row 8 ran four times.** The first full run failed `AC-162.4 figures` because Vitest's module cache held `help-shots.ts` as transformed before the images existed (`import.meta.glob` results are not part of the cache key); `vitest --clearCache` fixed it. The image review then found cut text, and a second review found badges over small text and half rows at the clip edges (D-1297). The review also found that Capture step 2 put the shot list below the image when it is at the left (D-1298).
   - **Three plan-local checker fixes** (a Playwright 1.64.1 error line in `red-check.py`, a colon after the AC id in `row-check.py only-failing`, and the `neg-stage` pattern), each with new self-test cases.
   - **H1 refusals.** H1-3's guard matched Session 100's mention of Session 99; H1-6 refused the phase `gate` (evidence.v1 allows `full`); H1-6a refused five AC families the plan quotes from older MEUs (`AC-23`, `AC-51`, `AC-81`, `AC-104`, `AC-158`).
   - The rows, from the receipts' modification times (local):

     | Step | Time |
     |---|---|
     | Plan review round 1, changes required | to 11-20 19:49 |
     | Plan review round 2, changes required | to 11-20 20:09 |
     | Plan review round 3, approved | to 11-20 20:17 |
     | Row 0 baseline | 11-20 23:30 |
     | Rows 1 to 6 | 11-20 23:33 to 23:56 |
     | Row 7, S5 stop (three pinned tests) | 11-21 00:01 |
     | Row 7 Green after D-1296 | 11-21 06:37 |
     | Row 8 (after Session 100's freeze) | 11-21 11:26 to 11:43 |
     | Rows 9 and 10 | 11-21 11:47 |
     | H1-2 gate, passed | 11-21 11:53 to 11:59 |
     | Execution review round 1, approved with F1 | 11-21 12:03 to 12:14 |
     | D-1295 fix, rows 8 and 9 and the gate rerun | 11-21 12:14 to 12:43 |
     | Execution review round 2, approved | 11-21 12:45 to 12:51 |

2. **What instructions were ambiguous?**
   - **"The five pinned topics".** The task text kept five; D-1290 A unpinned the Settings Console topic, so the plan and the code keep four. The handoff names this as a departure, and the commit draft says four.
   - **The `HELP_SHOTS_GEN` framing.** The plan said "scrollIntoView({ block: 'start' }) ... the union of the target boxes plus 24 px". That framing passed every assertion and still made images with cut text; D-1297 replaced it.

3. **What instructions were unnecessary?**
   - H2-1's `view_file` row, because H2-2's validator reads the same template and schema (as in Sessions 74 and 88 to 100).

4. **What was missing?**
   - **A cache step in the row that adds the images.** Any test that reads files through `import.meta.glob` can see an old list until `vitest --clearCache` (RULE-1).
   - **A check that a step's words match the page.** The STE gate checks the language and AC-162.11 checks that the target exists; neither checks where the step says the control is. Only the image review found D-1298 (RULE-2).
   - **The evidence.v1 phase list in the handoff row.** H1-6 refused `gate` (RULE-3).

5. **What did you do that wasn't in the prompt?**
   - **Reviewed all 14 images against written criteria** (numbers on the right controls, right theme, no text cut, no personal data) and recorded each in `hq-row8-review.txt` and the handoff.
   - **Kept the first image set** in the scratch `pre-review-fix` folder and every superseded row 8 receipt.
   - **Made every hand edit with a script** that writes bytes, asserts each anchor once and keeps the file's line endings.

### Quality Signal Log

6. **Which tests caught real bugs?**
   - **The plan review**, not a test: six Highs across rounds 1 and 2. F1 found steps the app cannot follow (Transcript's View compiled before Compile, Convert's controls); F2 found that the demo launch still spawned the backend and read setup readiness outside the fetch seam; F3 found the plan's STE severity names did not match the linter; F4 found a clip that could crop numbered controls; F5 found a row 7 Green that needed row 8's images; F6 found the privacy scan rejecting clean Settings images.
   - **`AC-162.4 figures`** caught the stale Vitest cache.
   - **The STE gate's Red** found three semicolons and one synonym rotation in the old topics.
   - **The pinned tests (S5)** caught the topic rewrite, as designed; Mat ruled D-1296.
   - **The execution review (F1, Medium)** found that the generator switched only the dark class, so `tts-dark.webp` and `settings-setup-dark.webp` kept white selects. The image review had missed it. D-1295 added a select-colour check to the generator; a planted copy without the theme event fails it (`hq-d1295-neg.txt`).

7. **Which tests were trivially obvious?**
   - `AC-162.4 css`, which counts the two `THEME_SHOT_CSS` rules; the Electron test (AC-162.11) proves the same theme switch on the real app.

8. **Did pyright/ruff catch anything meaningful?**
   - Ruff found format fixes in the plan-local Python and `tools/help_guide_ste.py`; no product finding. `py-types` was skipped with its H1-4 basis (no `packages/` change).

### Workflow Signal Log

9. **Was the FIC useful as written?**
   - Yes. The contract names (`QUICK_START_DATA`, `CARD_QUICK_START`, `HELP_SHOTS_GEN`, `DEMO_STAGE`, `PRIVACY_GUARD`, `STE_GATE`) gave the tests, the handoff and the reviews one vocabulary. The §Fact table let AC-162.9 prove that the plain rewrite kept each topic's facts.

10. **Was the handoff template right-sized?**
    - Mostly. The 14 image-review lines and the manifest table are long but were the only record of what the images show. The cross-ref AC rows exist only to satisfy the coverage check (slim_candidate below).

11. **How many tool calls did this session take?**
    - About 1,650 in the coordinator's transcript, planning through H2-6, across two context compactions.

12. **Which rows were delegated, to which subagent (harness + model), and did any delegated result need rework?**
    - No task row was delegated. In planning, two `Explore` subagents (Claude Code) mapped the first-run flow of the six pages, and one `av-kit-peer-reviewer` (Claude Code) gave an advisory pass on the D-1289 and D-1290 briefs. The coordinator ran rows 0 to H2-6 and the review dispatches itself. No delegated result needed rework.

### Decisions Log

All are `autonomous`, with `mandatory: none`, decided on the HDP recommendation. D-1289 and D-1290 (M-5) and D-1296 (M-7) are Mat's decisions and are read from the plan through `--decision-source`. D-1295 is the execution review's F1 fix.

- The quick start lives inside each page's existing HelpCard, as one JSON file typed in TypeScript and linted in Python — [D-1291](../plans/2026-11-20-help-quick-start/implementation-plan.md)
- A tracked Playwright generator on the real Electron app with demo stages, baked numbered badges and a privacy guard — [D-1292](../plans/2026-11-20-help-quick-start/implementation-plan.md)
- Vendor the ASD-STE100 skill byte for byte and gate the help text with `tools/help_guide_ste.py` — [D-1293](../plans/2026-11-20-help-quick-start/implementation-plan.md)
- Two drift guards: the manifest's step hash and the Electron image test — [D-1294](../plans/2026-11-20-help-quick-start/implementation-plan.md)
- The generator centres the targets, widens the clip to whole rows and labels, and moves the badge to x-16, y-16 — [D-1297](../plans/2026-11-20-help-quick-start/implementation-plan.md)
- Capture step 2 points to the shot list at the left of the image — [D-1298](../plans/2026-11-20-help-quick-start/implementation-plan.md)

- The generator switches the theme the way the app does and refuses a shot whose selects keep the other theme's colour; the 14 images are retaken — [D-1295](../plans/2026-11-20-help-quick-start/implementation-plan.md)

---

## Pattern Extraction

### Patterns to KEEP
1. **Take the screenshots from the real app with demo stages.** The images show the shipped controls, and the step hash and the Electron test fail when they go stale.
2. **Review each generated image against written criteria before the tests are trusted.** All assertions passed on images with cut text; only the review found it.
3. **A §Fact table for a plain-language rewrite.** It turned "keep the facts" into keywords a test reads.

### Patterns to DROP
1. **Cross-ref AC rows written only to pass the coverage check.** Name the foreign ids once in a single row instead.

### Patterns to ADD
1. **Clear the Vitest cache in the row that adds files a glob reads** (RULE-1).
2. **Check each step's place words against its screenshot in the generator's row** (RULE-2).
3. **Write evidence blocks with the evidence.v1 phase list** (RULE-3).

### Calibration Adjustment
- **Estimated:** no token budget. Round caps of 3 (plan) and 6 (execution).
- **Actual time:** about 25 minutes for rows 0 to 6, 17 minutes for row 8, 6 minutes for the gate; about 11 hours waiting on Mat's D-1296 ruling and Session 100's freeze.
- **Tokens:**

  | Item | Tokens |
  |---|---|
  | Plan review, round 1 | 12,410,142 |
  | Plan review, round 2 | 6,644,034 |
  | Plan review, round 3 | 2,671,687 |
  | Execution review, round 1 | 13,061,240 |
  | Execution review, round 2 | 6,374,670 |
  | Total | 41,161,773 |

- **Adjusted estimate** for a UI help change with generated images: about 12M tokens for a first plan review round and less for rechecks; about 1.5 hours of rows when no peer session shares the tree and no human stop fires.

---

## Next Session Design Rules

```
RULE-1: A row that adds or renames files read through import.meta.glob runs vitest --clearCache before its Vitest run.
SOURCE: Session 99 row 8: AC-162.4 figures failed because Vitest's cache held help-shots.ts as transformed before the WebP files existed; the cache key is the file's own text.
EXAMPLE: before, row 8 runs help:shots then npm run test; after, it runs help:shots, npx vitest --clearCache, then npm run test.
```

```
RULE-2: When a guide step says where a control is (left, below, beside), the row that takes its screenshot checks those words against the image and records the check.
SOURCE: Session 99 D-1298: Capture step 2 said the shot list is below the image; the image review found it at the left, after the STE gate and AC-162.11 had passed.
EXAMPLE: before, the image review checks numbers, theme, cut text and personal data; after, it also checks each step's place words.
```

```
RULE-3: Evidence blocks use only the evidence.v1 phases (red, green, static, targeted, full, runtime, manual); a session gate is phase full.
SOURCE: Session 99 H1-6: validate_closeout_artifacts.py refused "evidence 7: unknown phase" for phase gate.
EXAMPLE: before, the gate block reads "phase": "gate"; after, "phase": "full", "fresh": true.
```

---

## Next Day Outline

1. **Next:** the queue from `tools/meu_status.py next` and the open issues; the prompt is at `C:/Temp/av-kit/next-session-prompt.md` (H2-6).
2. **Scaffold changes needed:** none.
3. **Patterns to bake in from today:** RULE-1 to RULE-3 here, Session 100's RULE-1 to RULE-3, and the rules carried before them.
4. **Codex validation scope:** the next session's own loops.
5. **Time estimate:** set by the next plan.
6. **Still open for Mat:** the commit of Session 99 (H2-5 has the draft; no push from the agent); `help:shots` must be run again when a page's layout or a step changes, and the drift tests say when.

---

## Efficiency Metrics

| Metric | Value |
|--------|-------|
| Total tool calls | About 1,650 in the coordinator's transcript |
| Time to first green test | Row 6's STE gate at 23:55, 19 minutes after row 3's Red at 23:36 |
| Tests added | 13 Vitest tests in `help-quick-start.test.tsx` and `help-shots-privacy.test.ts`, 9 E2E tests in `help-quick-start.test.ts` and 4 pytest cases in `test_help_guide_ste.py`; four existing tests changed (AC-115.15 under D-1290 A, three under D-1296). Final gate: Vitest 1,657 in 149 files, tooling 574 |
| Codex findings | Plan review: R1 changes required, 5 High (F1 to F5); R2 changes required, 1 High (F6); R3 approved, 0. Execution review: R1 approved, 1 Medium, not blocking (F1); R2 approved, F1 fixed, 0 new |
| Handoff Score (X/7) | 7/7. Every AC has evidence, the gate passed, and the execution review approved at round 2 with F1 fixed |
| Rule Adherence (%) | 90 (9 of 10 sampled rules followed) |
| Prompt→commit time | Requested and planned 2026-11-20; executed, reviewed and closed 2026-11-21; the commit waits for Mat |

### Rules Sampled for Adherence Check

| Rule | Source | Followed? |
|------|--------|-----------|
| Independent review; no self-approval | AGENTS.md §Dual-Agent Workflow | Yes. Codex reviewed the plan and the execution; no verdict was written locally |
| Never commit, stage or push without Mat | AGENTS.md §Commits | Yes. H2-5 is a draft only |
| Red before Green, by assertion | AGENTS.md §Testing | Yes. Rows 3 to 5 failed by assertion (`red-check` 0 problems) |
| Stop and ask at a stop condition | The plan §Stop Conditions | Yes. S4 (row 1) and S5 (row 7) went to Mat |
| No expectation edited at Green | The plan (S3) | Yes. `red-unchanged` 0 problems in rows 7 to 9 and the gate |
| No home path in a tracked file or image | The plan (`PRIVACY_GUARD`) | Yes. 14 `privacy: clean`; `check_home_path` ok; the planted negative blocked |
| Keep line endings; measure in bytes | Session 70 RULE-5 | Yes. `eol-check` 0 problems over 39 paths |
| Stop processes by path, never by name | Memory: scope process kills | Yes. Each run stopped only its own launches |
| Clear `ELECTRON_RUN_AS_NODE` before any Electron launch | Memory | Yes, in every row and the gate |
| Run each Validation cell as written | The execution workflow | No. Row 8 ran four times and three plan-local checkers changed; all disclosed |

---

## Instruction Coverage

```yaml
schema: v1
session:
  id: "87b36192-5b86-4eaf-b56b-abd9ed3d8eda"
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
    - .agent/schemas/reflection.v1.yaml
    - docs/execution/reflections/TEMPLATE.md
    - .agent/context/handoffs/TEMPLATE.md
    - .agent/context/handoffs/2026-11-17-ui-small-fixes-MEU-158-handoff.md
    - docs/execution/reflections/2026-11-20-e2e-devpc-clipboard-reflection.md
    - .agent/skills/asd-ste100/SKILL.md
decisive_rules: [P0:never-commit-or-push-without-human-approval, P0:no-home-path-in-tracked-files, P0:keep-line-endings, P1:stop-conditions-go-to-the-human, P1:red-before-green-by-assertion]
conflicts:
  - "A peer session shared the tree; it changed a read-only file before row 1 (S4) and froze ui/src and Electron launches before row 8."
note: "Help cards gained a quick start with ASD-STE100 steps and generated screenshots; the image review, not a test, found cut text and a wrong place word."
slim_candidate: ["H2-1's view_file row repeats what H2-2's validator checks.", "Cross-ref AC rows exist only for the coverage check."]
overthinking_observed: false
review_churn:
  rounds_to_approval:
    plan: 3
    execution: 2
  findings_per_round:
    - review: plan
      round: 1
      critical: 0
      high: 5
      medium: 0
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
      medium: 1
      low: 0
    - review: execution
      round: 2
      critical: 0
      high: 0
      medium: 0
      low: 0
  churned_findings: 0
  finding_categories: {claim_to_state_drift: 2, boundary_validation: 2, contract_drift: 2, other: 1}
  verdicts:
    changes_required: 2
    approved: 3
meu_work_classes: [correctness]
```

The review churn counts the ledger's recorded rounds in the session's two loops. The plan loop, `hq-plan-2026-11-20-help-quick-start`, used 3 of 3 rounds: round 1 found F1 to F5 (High, blocking) with `intent_achieved=partial` (`usage` 12,410,142), round 2 found F6 (High, blocking) with `intent_achieved=partial` (`usage` 6,644,034), and round 3 approved with `intent_achieved=yes` (`usage` 2,671,687). The execution loop, `hq-execution-2026-11-20-help-quick-start`, used 2 of 6 rounds: round 1 approved with F1 (Medium, not blocking, dark images with light selects) and `intent_achieved=yes` (`usage` 13,061,240); D-1295 fixed F1, and round 2 approved with F1 fixed, no new findings and `intent_achieved=yes` (`usage` 6,374,670).
