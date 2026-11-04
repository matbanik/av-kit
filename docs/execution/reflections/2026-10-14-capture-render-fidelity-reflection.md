---
date: "2026-10-16"
project: "capture-render-fidelity"
meus: ["MEU-82", "MEU-83", "MEU-84"]
plan_source: "docs/execution/plans/2026-10-14-capture-render-fidelity/implementation-plan.md"
template_version: "2.0"
---

# 2026-10-16 Meta-Reflection

> **Date**: 2026-10-16 (plan written 2026-10-14; execution 2026-10-16)
> **MEU(s) Completed**: MEU-82 `capture-text-baseline`, MEU-83 `capture-arrow-geometry`, MEU-84 `capture-file-variant-sync`
> **Plan Source**: `docs/execution/plans/2026-10-14-capture-render-fidelity/implementation-plan.md`

---

## Execution Trace

### Friction Log

1. **What took longer than expected?**

   The row 8 session gate, which took five attempts. None of the failures was a product regression. Each was a gap between the approved gate script and a fresh worktree:
   - **Attempt 1:** `RECEIPTS_DIR` was unset (exit 3).
   - **Attempt 2:** status cells carried notes after the `[x]` token, which `task-contract` refuses.
   - **Attempt 3:** `pytest -x` stopped at a §Baseline packaging failure (AC-24.10). The plan's own baseline rule says a baseline failure is never a regression, but its gate could not express that. This became G-1.
   - **Attempt 4:** five Electron tests needed gitignored build outputs that only the main checkout had: the picker sidecar stub and the isolated primitive harness. This became G-2.

   Smaller delays:
   - Row 0's `uv sync` failed because the worktree `.venv` was CPython 3.14 (D-22).
   - The first Codex execution dispatch stopped with `registry_not_found` before reaching Codex. `AGENT_MODEL_REGISTRY_HOME` had to be set the way the plan rounds had set it.

2. **What instructions were ambiguous?**

   - **The plan's `py-tests` step.** It ran `pytest tests/ -x` and also stated "a test failing at baseline is never counted as a regression". The two cannot both hold while the baseline has failures. G-1 resolved it in favour of the stated rule and was flagged to the execution review, which accepted it on substance.
   - **AC-83.1/83.2 "no head for the zero-length case".** `arrowheadVertices` keeps its signature and always returns three points. D-27 places the assertion where the head is drawn instead.

3. **What instructions were unnecessary?**

   Restating the shared gate evidence in all three handoffs. Each carries the same two full `evidence.v1` gate records, which `walkthrough.md` already holds. It caused no drift this time because the handoffs were generated from one script (`handoffs_common.py`), but by hand it would have been three copies to keep in sync.

4. **What was missing?**

   - **A planning-time dry run of the full gate in the fresh worktree.** It would have surfaced attempts 1–4 before the plan review approved the gate.
   - **A coloured-output fixture in `red-check.py`.** The first formal Red run was refused because Vitest's ANSI codes break `\b\d+ failed` (D-23).
   - **A dispatch preflight for `AGENT_MODEL_REGISTRY_HOME`.**

5. **What did you do that wasn't in the prompt?**

   - **AC-83 Green run 1 failures.** Two unrelated E2E tests failed (AC-60.12, AC-67.35). I ran them under `--repeat-each 20` (40/40) before calling it a flake, and recorded run 1 so the row 8 suite could watch for a repeat. It did not repeat.
   - **An extra S6 stress run for AC-84.5:** `--repeat-each 10`, 10/10.
   - **Pre-existing `ruff format` hunks.** I checked that every hunk reported in `adapter.py`, `capture.py` and `test_capture_service.py` predates the session (`git show HEAD:…` fails the same check), and left them alone under `PRODUCT_SCOPE` (D-29).

### Quality Signal Log

6. **Which tests caught real bugs?**
   - **AC-82.6, the preview-vs-bake pixel oracle (Electron).** It measured the defect directly: the preview ink sat 8 px above the bake (`hanging` baseline), and after the fix the difference is 0 px on every side.
   - **AC-83.5 and AC-83.6, the real-adapter raster oracles.** They were Red with exactly the numbers the planning probe R-3 predicted: 53 leak pixels and an edge blend of 0/641. Green passed both.
   - **AC-84.1 and AC-84.2.** The stale `annotated_path` / `sidecar_path` after a file is deleted, through the service and through the real API.
   - **AC-84.4 and AC-84.5.** Open file and Open folder named the original in the Annotated view.
   - **The row 1 census.** It found AC-65.3 (D-20) and the inherited 1 px head outline (D-21) before any code changed, so both reached the human as decisions instead of surprises.

7. **Which tests were trivially obvious?**

   - AC-82.2 and AC-82.5 pin the existing bake and pass on baseline by design. Their value is a lock on the reference the preview is compared against.
   - AC-83.7 (edge clipping) also passed on baseline. It guards the new tile code.
   - AC-84.1(d) and (e) are a negative guard and a characterisation of existing behaviour.

8. **Did pyright/ruff catch anything meaningful?**

   No. `tsc`, eslint and `ruff check` were clean on the changed files. `ruff format --check` only re-joined one call that this session wrapped; the remaining hunks predate the session.

### Workflow Signal Log

9. **Was the FIC useful as written?**

   Yes. The single-statement contracts (`SEGOE_ASCENT`, `TEXT_ANCHOR`, `ARROW_HEAD`, `SHAFT_END`, `BAKE_AA`, `RECONCILE`, `VIEWED_FILE`, `E2E_SHELL_LOG`) translated directly into tests and code:
   - Rows 3 and 7 went Green on their first run.
   - Row 5 needed four runs, but the code was unchanged across them: one flake check and one formatting re-join.
   - `GEOMETRY_FIXTURE.arrows` was computed from the plan formulas by a scratch script, independent of the product code, so the TS and Python implementations were checked against the same third source.

10. **Was the handoff template right-sized?**

    About right for three MEUs: 9, 16 and 9 AC rows. The cross-reference rows for AC families a handoff does not own (needed by `--ac-coverage-only`) are pure ceremony. They exist only so the family-level check passes.

11. **How many tool calls did this session take?**

    Not tracked precisely: several hundred across planning (three review rounds) and execution.

12. **Which rows were delegated, to which subagent (harness + model), and did any delegated result need rework?**

    No implementation rows were delegated; Claude Code (Opus 5.5) ran every row.
    - **Plan review:** Codex CLI `gpt-6.1-sol` (high). Three rounds, approved at round 3.
    - **Execution review:** the same Codex route, approved at round 1 with 0 findings and `intent_achieved: yes`. The reviewer ran its own probes: a Segoe ascent sweep of 8195 sizes and an AA-oracle blend check.

### Decisions Log

| ID | Stage | Question | Resolution | Chosen | Source tag | Reasoning (why this; why the alternatives lost) | Human ref |
|----|-------|----------|------------|--------|------------|--------------------------------------------------|-----------|
| D-1 | grouping | When are the gated build-plan edits written? | autonomous | After Session 30's execution review approves; the grouping writes only ungated homes and the SSOT | Local Canon | Grouping §8 D-1 (carried). Session 36's 09 and matrix edits ran in row 9, after that review. | — |
| D-2 | grouping | Does `MCP-SETUP-PROMPT` join Session 31? | human | Yes, as MEU-71 | Human-approved | Grouping §8 D-2 (carried); outside this session's scope. | USER_EXPLICIT 2026-10-09 'All recommendations accpeted as proposed' |
| D-3 | grouping | Are the tech-debt rows MEUs? | autonomous | No; a separate debt batch | Local Canon | Grouping §8 D-3 (carried). The pre-existing ruff format hunks found here (D-29) belong to such a batch. | — |
| D-4 | grouping | Session order | autonomous | 31 → 32, 33, 34 → 35, 36 → 37, 38, 39 | Local Canon | Grouping §8 D-4 (carried). Session 36 was planned ahead of 32–35 under plan D-9; Session 39 follows 36 for the shared bake code. | — |
| D-5 | grouping | Keep TTS page work out of the engine session? | autonomous | Yes, Session 35 after Session 33 | Local Canon | Grouping §8 D-5 (carried); outside this session's scope. | — |
| D-6 | grouping | Where does the independent MEU scoping review run? | human | Codex scoping review on the grouping draft | Human-approved | Grouping §8 D-6 (carried). | USER_EXPLICIT 2026-10-09 'All recommendations accpeted as proposed' |
| D-7 | grouping | Repair the shared status_labels in meu-status.yaml? | autonomous | Yes: every row's labels rebuilt from its own status | Local Canon | Grouping §8 D-7 (carried); the MEU-82/83/84 status updates in H1-3 and H2-2 went through `meu_status.py`, which keeps per-row labels. | — |
| D-52 | triage | How do preview, plate and bake share one text anchor? | autonomous | The SVG text on the alphabetic baseline at y + ascent from the bake's Segoe metrics, plus a preview-vs-bake pixel test | Local Canon | `CAPTURE-TEXT-BG-PREVIEW-OFFSET` enrichment; implemented as MEU-82 (AC-82.3, AC-82.6). | — |
| D-53 | triage | Where does the arrow shaft end? | human | At the back of the head, not at its tip, in bake and preview | Human-approved | `CAPTURE-BAKE-ARROW-THIN` enrichment; implemented as MEU-83 `SHAFT_END`. | USER_EXPLICIT 2026-10-03 FLATTEN_LOOK F1 'the line must start at the back of the triangle, not end at its tip' |
| D-54 | triage | How is the baked arrow anti-aliased? | autonomous | 4x supersample and LANCZOS; shaft ends at tip − head·cos(angle) with a small overlap; head size set at plan time | Local Canon | `CAPTURE-BAKE-ARROW-THIN` enrichment; refined by plan D-12, D-13 and D-14. | — |
| D-55 | triage | What should scan_inbox do with a missing annotated copy or sidecar? | autonomous | Clear the field when the file is gone | Local Canon | `CAPTURE-STALE-ANNOTATED-PATH` enrichment; refined to per-field by plan D-15. | — |
| D-65 | triage | Which file does Capture Open file open? | human | The file the viewport shows (the annotated copy in the Annotated view, the original otherwise); Open folder reveals the same file | Human-approved | `CAPTURE-OPEN-FILE-VARIANT` enrichment; implemented as MEU-84 `VIEWED_FILE`. | USER_EXPLICIT 2026-10-09 'All recommendations accpeted as proposed' |
| D-8 | planning | Where is the plan written and executed? | autonomous | A fresh worktree on `claude/s36-capture-render-fidelity` | Local Canon | Isolates the session from Session 31's uncommitted main-checkout edits (plan D-8). The fresh worktree is also why G-1 and G-2 were needed. | — |
| D-9 | planning | Plan Session 36 before Sessions 31–35 have executed? | human | Yes; the MEU-81 merge risk is recorded and the testids stay | Human-approved | No Session 31–35 MEU is a dependency of MEU-82/83/84 (plan D-9). | USER_EXPLICIT 2026-10-14 '@.agent/workflows/create-plan.md 36 capture-render-fidelity' |
| D-10 | planning | How is ascent computed in TypeScript so it equals the bake? | autonomous | `SEGOE_ASCENT`: FreeType 26.6 FT_MulFix rounding then ceil | Research-backed | R-1 matched Pillow for sizes 1–1000; the naive ceil is wrong at 38, 177, 215 and 354. The execution reviewer's 8195-size sweep found no mismatch. | — |
| D-11 | planning | Keep the hanging baseline with an offset, or switch to alphabetic? | autonomous | Alphabetic at y + ascent | Spec | 09:712; alphabetic is the baseline FreeType and Chromium place identically (plan D-11). | — |
| D-12 | planning | Arrow head length factor and angle | human | `ARROW_HEAD` (5 / 0.45), the stated default | Research-backed | The brief recommended a larger head beside thick shafts. The execution message was silent on D-12, so the default applied and TA-1/TA-2 stood. | USER_EXPLICIT 2026-10-16 'proceed' (silent on D-12, so the plan's stated default applies) |
| D-13 | planning | Shaft overlap into the head | autonomous | `ARROW_SHAFT_OVERLAP_PX = 1` | Human-approved | `SHAFT_INSIDE_HEAD` proves the corners stay inside the head for every stroke (plan D-13). | — |
| D-14 | planning | How to anti-alias the baked arrow | autonomous | `BAKE_AA`: a 4x coverage-mask tile, LANCZOS, composite | Research-backed | A full 4K canvas at 4x is about 530 MB; a mask avoids colour fringes (plan D-14). | — |
| D-15 | planning | Clear annotated_path and sidecar_path together or per field? | autonomous | Per field, saved only on change | Local Canon | A sidecar without an annotated copy still holds the marks (plan D-15). | — |
| D-16 | planning | Open file / Open folder in the Annotated view with the annotated copy missing | autonomous | Fall back to the original | Human-approved | Triage D-65 via 09:737-738 (plan D-16). | — |
| D-17 | planning | How does Electron E2E observe which file Open file asked for? | autonomous | `E2E_SHELL_LOG` in the existing main-process E2E branches | Local Canon | contextBridge freezes window.api (plan D-17). | — |
| D-18 | planning | How is the preview-vs-bake pixel comparison made without a real backend? | autonomous | `TEXT_FIXTURE` (a real bake, pinned fresh by pytest) and an in-page canvas decode | Local Canon | No new image dependency (plan D-18). | — |
| D-19 | planning | Which element carries the arrow's from/to after the shaft is shortened? | autonomous | The arrow group element keeps x1/y1/x2/y2 = from/to (TA-5, TA-6) | Local Canon | The shaft line must show the shaft end (plan D-19). | — |
| D-20 | execution | How should AC-65.3 check the stroke edit once short arrows render no shaft line? | human | TA-7: assert the rendered head polygon length (35 = 5 × 7) | Human-approved | Row 1 census S2; MEU-83 handoff. | USER_EXPLICIT 2026-10-16 'Approve TA-7 (Recommended)' |
| D-21 | execution | Remove the 1 px outline the preview head inherits from the group stroke? | human | Add to MEU-83: head polygon stroke none, new AC-83.9 | Human-approved | Found while dispositioning AC-65.3; MEU-83 handoff. | USER_EXPLICIT 2026-10-16 'Add to MEU-83 (Recommended)' |
| D-22 | execution | The worktree venv was CPython 3.14 and spacy has no cp314 wheel | autonomous | Recreate `.venv` with Python 3.12.12 and re-run row 0 unchanged | Local Canon | The interpreter the lockfile resolves for; no lockfile edit (MEU-82 handoff). | — |
| D-23 | execution | red-check.py refused the coloured Vitest receipt | autonomous | Strip ANSI CSI escapes before matching, with a positive and a negative selftest fixture | Local Canon | S3 allows a test-setup fix only; no rule was loosened (MEU-82 handoff). | — |
| D-24 | execution | The element screenshot of a fractional-origin box carries dark edge pixels | autonomous | Skip a ceil(2 × DPR) px ring | Local Canon | The mark is at least 20 px from every edge (MEU-82 handoff). | — |
| D-25 | execution | The approved gate's `pytest -x` can never pass in a fresh worktree | autonomous | G-1: run the whole suite and pass only the two §Baseline failures | Local Canon | The plan's §Baseline rule; Session 31 used the same subset rule. Accepted by the execution review (MEU-82 handoff). | — |
| D-26 | execution | Gate attempt 4 failed on gitignored Electron prerequisites | autonomous | G-2: `ui-harness-build` and `ui-picker-stub` stages before `ui-electron` | Local Canon | cloud-local §3.1 item 3; accepted by the execution review (MEU-82 handoff). | — |
| D-27 | execution | Where is the zero-length arrow's missing head asserted? | autonomous | Where it is drawn (no polygon, AC-83.4) | Local Canon | `arrowheadVertices` keeps its signature (MEU-83 handoff). | — |
| D-28 | execution | How does the AC-83.8 size spy avoid passing on a bake that skips supersampling? | autonomous | No full-canvas 4x image, and one 4x tile mask | Local Canon | Both directions are asserted (MEU-83 handoff). | — |
| D-29 | execution | Reformat the pre-existing ruff format hunks? | autonomous | No; only the lines this session added | Local Canon | They predate the session and lie outside `PRODUCT_SCOPE` (MEU-83 handoff). | — |
| D-30 | execution | Does the selection gain viewedPath beside originalPath, or replace it? | autonomous | Replace it | Local Canon | One path, so no caller can open the wrong one (MEU-84 handoff). | — |
| D-31 | execution | Which dependencies does the selection effect need? | autonomous | annotations, selected, selectedId and viewVariant | Local Canon | A refetch that drops annotated_path must update the target (MEU-84 handoff). | — |

The plan named grouping D-1, D-3, D-4 and D-6 as the ones that touch this scope. D-2, D-5 and D-7 are carried as well, because the reflection check reconciles every §8 row of the grouping. The triage decisions above are the enrichment `decision_log` entries of the four issues this session resolves.

---

## Pattern Extraction

### Patterns to KEEP
1. **Measure the defect with an oracle that compares the two renderings.** AC-82.6 read 8 px, then 0 px. A unit test of the baseline constant alone would have passed with any offset.
2. **Planning probes that transcribe the contract literally.** R-3 predicted the Red numbers for AC-83.5/83.6 exactly, which made the Red row a confirmation, not a discovery.
3. **Fixtures computed independently of the product code.** `GEOMETRY_FIXTURE` came from the plan formulas, so TS and Python could not agree on a shared mistake.
4. **Census before code.** The row 1 census raised D-20 and D-21 as decisions before any test or product file changed.

### Patterns to DROP
1. **A gate script that can only pass in the main checkout.** `-x` over a suite with known baseline failures, and Electron tests that rely on gitignored outputs, both broke in a fresh worktree.

### Patterns to ADD
1. **A planning-time dry run of the session gate in the execution worktree**, with its receipt cited in the plan before the plan review.
2. **A coloured-output fixture for every receipt parser** (`red-check.py` and any successor).
3. **A dispatch-environment preflight** in the review dispatch row: the registry home and the receipts directory.

### Calibration Adjustment
- Estimated time: one planning session plus one execution session for three small correctness MEUs.
- Actual time: planning 2026-10-14 (three review rounds); execution 2026-10-16 in one pass, with five gate attempts and one review round.
- Adjusted estimate for similar MEUs in a fresh worktree: add one gate loop unless the gate was dry-run at planning time.

---

## Next Session Design Rules

```
RULE-1: A plan whose gate runs in a fresh worktree is dry-run there before the plan review; every gitignored build output the suites need is its own stage, and the §Baseline rule is applied by the gate itself, never by -x.
SOURCE: Session 36 gate attempts 3 and 4 (G-1, G-2; D-25, D-26).
EXAMPLE: "pytest tests/ -x" → "pytest tests/ -rfE" plus a baseline-subset check; "ui-electron" → "ui-harness-build, ui-picker-stub, ui-electron".
```

```
RULE-2: Any tool that parses test receipts strips ANSI escapes first and carries a coloured-output selftest fixture.
SOURCE: D-23: red-check.py refused the first formal Red receipt because Vitest colours its summary.
EXAMPLE: "re.search(r'\b\d+ failed', text)" → "re.search(r'\b\d+ failed', ANSI_ESCAPE.sub('', text))" with fixture vitest-ansi-assertion.
```

```
RULE-3: Row commands set every environment variable they depend on (RECEIPTS_DIR, AGENT_MODEL_REGISTRY_HOME) or check it first and name it in the failure.
SOURCE: Gate attempt 1 (RECEIPTS_DIR is unset) and the first H1-7 dispatch (registry_not_found).
EXAMPLE: "pwsh -File tools/Invoke-CodexDispatch.ps1 ..." → "$env:AGENT_MODEL_REGISTRY_HOME ??= 'P:/.agent'; pwsh -File tools/Invoke-CodexDispatch.ps1 ...".
```

---

## Next Day Outline

1. **Commit and merge (Mat).** Review the H2-5 commit-message draft. Commit `claude/s36-capture-render-fidelity` and merge it to `main`. Nothing is committed yet.
2. **Tooling follow-ups to file through `/issue-triage`:**
   - The plan-review ledger wrapper refused the round 2 (procedural `changes_required` with no findings) and round 3 verdicts.
   - The dispatch preflight for `AGENT_MODEL_REGISTRY_HOME`.
   - The pre-existing `ruff format` hunks in `adapter.py`, `capture.py` and `test_capture_service.py` (debt batch, D-3).
3. **Merge risk:** Session 34's MEU-81 converts Open file / Open folder to icon buttons. The testids are unchanged, but MEU-84's handler wiring must survive the conversion.
4. **Next session per the grouping order (D-4).** Session 39 follows Session 36 for the shared bake code.
5. **Bake in RULE-1 to RULE-3.**

---

## Efficiency Metrics

| Metric | Value |
|--------|-------|
| Total tool calls | not tracked precisely (several hundred across planning and execution) |
| Time to first green test | 2026-10-16 (row 3, MEU-82 Green, first run) |
| Tests added | pytest 653 → 674 passed (+21). Vitest 800 → 815 (+15). Electron `capture-inbox.test.ts` 28 → 30 (AC-82.6, AC-84.5); full Electron suite 139 passed. `red-check.py` selftest +2 fixtures. |
| Codex findings | Plan review (Codex `gpt-6.1-sol`): R1 `changes_required` (2 High, 2 Medium, 2 Low); R2 `changes_required` (PR-6 procedural, no rated finding); R3 approved. Execution review: R1 approved, 0 findings. |
| Handoff Score (X/7) | 7/7 (execution review round 1: 0 findings, all plan ACs present) |
| Rule Adherence (%) | 95 |
| Prompt→commit time | 2026-10-14 → 2026-10-16 (review approval; commit pending the human) |

### Rules Sampled for Adherence Check

| Rule | Source | Followed? |
|------|--------|-----------|
| Tests before production code; Red before Green | AGENTS.md §Testing & TDD | Yes. Rows 2, 4 and 6 were Red with `red-check.py` attribution before any product change |
| No test expectation change without approval | AGENTS.md §Testing & TDD | Yes. Only TA-1 to TA-7 changed assertions; TA-7 was approved as D-20 |
| Independent review; no self-approval | AGENTS.md §Dual-Agent Workflow | Yes. Codex CLI reviewed both the plan and the execution; the author wrote no verdict |
| Product scope limited to the Files table | Plan `PRODUCT_SCOPE` | Yes. `scope-paths` reported 37 changed paths, none outside scope; pre-existing format hunks were left alone |
| A post-approval gate change is disclosed to the reviewer | Plan §Gate, execution-critical-review | Yes. G-1 and G-2 were named in the review prompt and accepted on substance |

---

## Instruction Coverage

```yaml
schema: v1
session:
  id: "session-36-capture-render-fidelity-2026-10-16"
  task_class: tdd
  outcome: success
sections:
  - {id: priority_0_system_constraints_non_negotiable, cited: true, influence: 3}
  - {id: planning_contract, cited: true, influence: 2}
  - {id: testing_tdd_protocol, cited: true, influence: 3}
  - {id: execution_contract, cited: true, influence: 3}
  - {id: session_discipline, cited: true, influence: 2}
  - {id: dual_agent_workflow, cited: true, influence: 3}
  - {id: rtk_token_optimized_commands, cited: true, influence: 1}
  - {id: instruction_coverage_reflection, cited: true, influence: 2}
loaded:
  workflows: [create_plan, plan_corrections, execution_session, tdd_implementation, execution_critical_review]
  roles: [orchestrator, coder, tester]
  skills: [timestamp]
  refs:
    - .agent/docs/harness-profiles.md
    - .agent/context/harness.local.md
    - .agent/docs/human-decision-protocol.md
    - .agent/docs/cloud-local-collaboration.md
    - .agent/schemas/reflection.v1.yaml
    - docs/build-plan/09-screenshot-capture.md
    - .agent/context/grouping/2026-10-09-triage-residuals-session-grouping.md
    - docs/execution/plans/2026-10-14-capture-render-fidelity/implementation-plan.md
    - docs/execution/plans/2026-10-14-capture-render-fidelity/task.md
decisive_rules:
  - P1:tests-before-production-code
  - P1:human-approval-for-test-changes
  - P1:independent-review-no-self-approval
  - P1:baseline-failures-are-not-regressions
  - P0:never-commit-or-push-without-human-approval
conflicts:
  - "The plan's py-tests step ran pytest -x while its Baseline rule says baseline failures are not regressions; resolved by G-1 and accepted by the execution review."
  - "The harness asked for a Co-Authored-By trailer on commits; the user's rule forbids AI attribution trailers, so the commit draft has none."
  - "The plan-review ledger wrapper's verdict schema needs findings for changes_required, but PR-6 procedural verdicts carry none; rounds 2 and 3 were kept in the review file only."
  - "A connected docs server asked for docs to be created there; the user's rule keeps deliverables as local repo files."
note: "S36 ships the text baseline fix, arrow geometry and AA bake, and the viewed-file open. Gate attempt 5 green; plan review approved r3, execution review r1 with 0 findings."
slim_candidate: ["The per-family AC cross-reference rows each handoff carries only so --ac-coverage-only passes"]
overthinking_observed: false
review_churn:
  rounds_to_approval: {plan: 3, execution: 1}
  findings_per_round:
    - {review: plan, round: 1, critical: 0, high: 2, medium: 2, low: 2}
    - {review: plan, round: 2, critical: 0, high: 0, medium: 0, low: 0}
    - {review: plan, round: 3, critical: 0, high: 0, medium: 0, low: 0}
    - {review: execution, round: 1, critical: 0, high: 0, medium: 0, low: 0}
  churned_findings: 0
  finding_categories: {contract_drift: 1, provenance_error: 1, weak_test: 1, other: 1, count_reconciliation: 1, stale_reference: 1}
  verdicts: {changes_required: 2, approved: 2}
meu_work_classes: [correctness, correctness, correctness]
```
