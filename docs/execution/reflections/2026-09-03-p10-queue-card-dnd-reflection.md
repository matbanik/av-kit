---
date: "2026-09-16"
project: "p10-queue-card-dnd"
meus: ["MEU-49"]
plan_source: "docs/execution/plans/2026-09-03-p10-queue-card-dnd/implementation-plan.md"
template_version: "2.0"
---

# 2026-09-16 Meta-Reflection

> **Date**: 2026-09-16
> **MEU(s) Completed**: MEU-49 (`gui-queue-dnd`) — the Phase 10 exit MEU
> **Plan Source**: `docs/execution/plans/2026-09-03-p10-queue-card-dnd/implementation-plan.md`

---

## Execution Trace

### Friction Log

1. **What took longer than expected?**
   The layout defect behind AC-49.27, by a wide margin — it consumed more elapsed time than
   the drag implementation itself and spanned three sessions. The reason is worth recording
   because it was not complexity: it was **fixing the symptom's location instead of its
   cause**, twice. dnd-kit's `KeyboardSensor` scrolls-and-returns instead of moving when
   `canScrollY && clamped !== requested`. X3 correctly identified that the clamp was being
   evaluated against the page shell's `<main>` and bounded the queue into its own scroller.
   That fix was necessary, passed its own unit tests, and left AC-49.27 red — because it
   never said *which* pane yields height when the column is oversubscribed. At the flex
   default the deficit is split by content height, so the queue became the pane that
   shrank, landing at 92px, and the clamp was faithfully re-created one level below where it
   had been removed. The tell was available from the first probe and I under-read it: the
   probe reported the scroller at 92px against a rule that names ~124px, which is the defect
   stated in numbers, and I treated it as a budget question to escalate rather than as the
   answer.

2. **What instructions were ambiguous?**
   `QUEUE_SCROLL_CONTAINER_RULE` as X3 wrote it. Clauses (1)–(3) fully specified *where*
   `overflow-auto` goes and *what* must not carry it, and said nothing about which sibling
   absorbs a height deficit — so a conforming implementation could still be wrong, and was.
   A layout rule that constrains the scroller but not the flex negotiation around it is
   underspecified in the way that matters. Clause (4) now states it.

3. **What instructions were unnecessary?**
   Nothing in the plan was dead weight, and the friction came from gates rather than
   instructions — but one *carried-forward rule* was actively counterproductive and should be
   retired rather than repeated. The previous reflection's RULE-1 says to restate a dispatch
   gate's requirements verbatim in the reviewer prompt. I did that. The prompt asked for the
   `verdict:` line; the reviewer supplied a correct verdict mid-sentence; the anchored pattern
   rejected it. A rule that tells you to phrase the request more carefully cannot fix a gate
   that constrains something the reviewer chooses freely. RULE-3 below replaces it.

4. **What was missing?**
   A registered fact about the app's own default window. Three sessions of this MEU reasoned
   about geometry without anyone writing down that `1280x800` yields 739px of content
   against ~515px of controls — which is the entire defect, and is a property of the shipped
   product rather than of the test harness. It was rediscovered by reading
   `ui/src/main/index.ts` late, when it should have been an input.

5. **What did you do that wasn't in the prompt?**
   Two things, both instrumentation rather than implementation. First, when AC-49.27 stayed
   red after X4 I stopped proposing fixes and patched `Element.prototype.scrollTo` plus a
   capture-phase keydown listener in the live page, which showed `maxScroll: 0` on both
   ancestors and zero `scrollTo` calls — proving X4 had worked and the residual was a
   different bug. Second, when my first two settle attempts failed I timestamped the whole
   activation sequence rather than guessing again, which produced the measurement the fix is
   built on (Space t=134ms, announcement t=140ms, listener t=153ms). Both probes were
   deleted once they had answered their question. I should have reached for the first one
   two attempts earlier.

### Quality Signal Log

6. **Which tests caught real bugs?**
   The `QUEUE_SCROLL_CONTAINER_RULE` E2E geometry probe, decisively. It asserts the measured
   scroller height against `2 × pitch` rather than asserting that a class string is present,
   and that is the only reason X3's inversion was caught at all: every className unit test
   for X3 passed on the broken tree, because the classes *were* correct — the flex outcome
   was not. A test that measures the property the library actually reads beat four tests
   that measured the inputs I believed produced it.

7. **Which tests were trivially obvious?**
   The X3/X4 className locks in the two page unit tests. They assert string equality against
   source text and cannot fail for any reason except someone editing the string. They are
   still worth keeping — they exist so MEU-52 cannot paste the old mockup §04 string back —
   but they are guards, not tests, and this session is direct evidence that they prove
   nothing about behaviour.

8. **Did pyright/ruff catch anything meaningful?**
   No. `packages/api/` was untouched (proved by the ApiSkip gate, not asserted), and the
   TypeScript side stayed clean throughout — `tsc --noEmit` and `eslint --max-warnings 0`
   never once failed during the X4 work. All the defects this session were behavioural and
   invisible to static analysis, which is the expected division of labour rather than a
   complaint.

### Workflow Signal Log

9. **Was the FIC useful as written?**
   Yes, and specifically because several ACs were written to forbid the weaker assertion.
   AC-49.25/49.29 demand the exact sequence `[B,C,A,D]` and explicitly name `[B,A,C,D]` — the
   remove-then-insert-at-post-removal-index bug — as a result that must fail. AC-49.38's
   two-card form is the same idea: it was rewritten during plan review because the one-card
   version was unsatisfiable on a boundary row. ACs that name the specific wrong answer are
   worth several that describe the right one.

10. **Was the handoff template right-sized?**
    Yes, with one addition that earned its place. I added an `## Execution-phase corrections
    in this MEU` section between the evidence and the changed files, because X4 is a genuine
    product defect whose first fix recreated it, and burying that in a plan appendix would
    have hidden the single thing the reviewer most needed to challenge. The reviewer did
    challenge it — independently, at viewport heights from 800px down to 300px.

11. **How many tool calls did this session take?**
    Roughly 55 in the Cursor takeover segment (this session), against a project that spans
    several prior sessions. The largest single blocks were the four full Playwright runs
    (~1 minute each for the six-case subset, 10.3 minutes for the full suite) and the
    23-minute review dispatch.

12. **Which rows were delegated, to which subagent (harness + model), and did any delegated
    result need rework?**
    None in this segment. The plan assigns rows 4/4a/4b/9 to `av-kit-builder` and row 10 to
    `av-kit-verifier`, and those delegations happened in earlier sessions. This segment was
    entirely correctness-class work — a layout/library interaction defect, its diagnosis, and
    two gate corrections — which is explicitly outside the builder tier's remit. Delegating
    the X4 diagnosis would have been a mistake; delegating the closeout paperwork would have
    saved little and risked the accuracy the handoff depends on.

---

## Pattern Extraction

### Patterns to KEEP

1. **Instrument the library, do not theorise about it.** Two wrong hypotheses cost two full
   build-and-run cycles each; one probe that patched `scrollTo` and timestamped the
   activation sequence ended the question in a single run. The threshold should be: after
   **one** failed hypothesis, measure.
2. **Assert the measured property, not the inputs you think produce it.** The geometry probe
   caught what four className assertions could not.
3. **Write ACs that name the specific wrong answer.** `[B,A,C,D]` must fail is a stronger
   contract than "the order changes".
4. **Deleting the probe is part of using the probe.** Both temporary specs were removed in
   the same pass that consumed their output, so nothing `ZZPROBE`-shaped reached the review.

### Patterns to DROP

1. **Treating a numeric probe result as a budget question.** When the X3 probe returned 92px
   against a rule naming 124px, the correct next move was to ask why the queue was the pane
   that shrank. Instead it went to a human gate as a defer-or-continue decision. The number
   was not a status report; it was the diagnosis.

### Patterns to ADD

1. **Register the product's own default window as a planning input** for any layout MEU. The
   whole X3→X4 sequence is downstream of nobody writing down 1280×800 → 739px.
2. **A layout named-set must state which pane yields.** Specifying the scroller without
   specifying the flex negotiation permits a conforming implementation to be wrong.
3. **When a gate rejects a correct artifact, fix the gate in the same pass.** See RULE-3 —
   this session's X6 is the second occurrence of an incident the previous session paid a
   review round for and left in place.

### Calibration Adjustment

- Estimated time: AC-49.27 was scoped as a one-session layout fix (X3).
- Actual time: three sessions — X3, the probe/human gate, then X4 plus the diagnosis.
- Adjusted estimate for similar MEUs: when a third-party library's *internal* geometry logic
  is load-bearing (dnd-kit's clamp here), budget a dedicated instrumentation pass before the
  first fix attempt rather than after the second failure. Reading the library source is
  necessary but was not sufficient: I read `handleKeyDown` correctly and still mispredicted
  the runtime, because the flex outcome — not the clamp arithmetic — was the unknown.

---

## Next Session Design Rules

```
RULE-1: When a fix targets a third-party library's internal behaviour, instrument the
        running page before the SECOND attempt, not after the third.
SOURCE: Two failed settle hypotheses for AC-49.27 cost two build+run cycles each; the
        timestamp probe answered it in one and produced the numbers the fix is built on.
EXAMPLE: "the announcement proves the sensor attached, so one macrotask suffices" (wrong,
         twice) → measured: Space t=134ms, announcement t=140ms, listener t=153ms, so the
         announcement FOLLOWS nothing useful and the registration itself is the observable.
```

```
RULE-2: A layout named-set must state which pane absorbs a height deficit, not only where
        overflow lives. Constraining the scroller without constraining the negotiation
        around it lets a conforming implementation be wrong.
SOURCE: X3 satisfied its own clauses (1)-(3) and its className tests, and still left the
        queue at 92px because every sibling defaulted to `shrink: 1`.
EXAMPLE: "overflow-auto on a wrapper around QueueList; region flex-1 min-h-0" → "...and the
         controls pane is min-h-0 overflow-auto, the footer shrink-0, the region
         min-h-[20rem]" (clause 4).
```

```
RULE-3: When a gate rejects a CORRECT artifact, fix the GATE in the same pass. Satisfying a
        wrong gate by reshaping good output leaves it armed for the next session. A gate may
        constrain what the reviewer SAYS; it may not constrain how the reviewer TYPES it.
SOURCE: The previous reflection's own RULE-1 was the prompt-side fix for this exact gate
        ("restate the gate's `(?im)^\s*verdict:` requirement verbatim in the prompt"), and
        metrics.md:27 records the review round it cost. I FOLLOWED that rule this session —
        the dispatch prompt did ask for the verdict line — and the gate failed anyway,
        because the reviewer wrote a correct verdict mid-sentence rather than at column 0.
        That is the escalation: the prompt-side fix cannot succeed, because line position is
        the reviewer's free choice and no prompt reliably controls it. Two sessions, same
        gate, and the first fix was aimed at the wrong artifact.
EXAMPLE: before → tell the reviewer more precisely how to format the line (fails again);
         after  → widen the pattern to `(?:^|[\s.;])verdict:\s*`, and add self-test cases
                  proving the real reviewer's mid-sentence phrasing passes while a wrong
                  verdict in the same shape still fails. The forgery protection the gate
                  exists for is unchanged — it still binds the verdict to a dispatch the
                  implementer cannot write.
```

---

## Next Day Outline

1. **Target MEU(s)**: MEU-50 — authors `docs/build-plan/11-page-layout.md`, opening Phase 11.
2. **Scaffold changes needed**: none. Phase 11 has no backend work; MEU-50 is spec authoring.
3. **Patterns to bake in from today**: carry `QUEUE_SCROLL_CONTAINER_RULE` **clause 4** into
   the layout canon as a stated constraint rather than an inherited accident. MEU-52 rewrites
   these two pages, and the failure mode is silent — a queue left free to shrink still looks
   fine and simply stops responding to the keyboard. The className locks in
   `downloader-page.test.ts` / `convert-page.test.ts` and the E2E geometry probes are the
   tripwires; MEU-50 should name them.
4. **Codex validation scope**: spec-authoring review — source labelling and the ~40 open §06
   "Decisions to lock" from the six 2026-09-03 mockups.
5. **Time estimate**: one session, planning-class.
6. **Carried-forward decision closed — OQ-3: `MOUNT_GATE_SCRIPT` is NOT promoted into the
   registered MEU gate; it retires with Phase 10.** Recorded here with its basis so Phase 11
   inherits the reasoning rather than just the outcome. The script proves a *one-time
   migration property* — that every retired toolbar control has a live home in
   `RETIRED_TOOLBAR_CONTROLS`. Its scopes are literally named after Phase 10 MEUs
   (`assert-mount-completeness.ps1:522-528`) and its named-set inputs live in the *migration*
   plan folder, so promoting it would bind the permanent registry to a retiring plan
   directory. A phase-scoped gate in the permanent registry makes every future MEU pay for a
   check whose subject stopped changing, and the first Phase 11 rename would turn it into a
   false failure that the next agent "fixes" by weakening it — which is worse than not having
   it. **What survives instead is `NO_DEAD_CONTROL_RULE`**, the durable principle the script
   was one instance of, already enforced per-MEU by E2E. This MEU ran the script once,
   unmodified and in place, as a no-regression check (178 checks, `PENDING` 0). The Codex plan
   reviewer independently concurred and recorded no dissent. If Phase 11 wants it back, the
   counter-move is a one-line addition to `.agent/docs/commands.md` — nothing else changes.

---

## Efficiency Metrics

| Metric | Value |
|--------|-------|
| Total tool calls | ~55 (this session segment) |
| Time to first green test | ~4 min (X4 unit locks green on first run) |
| Tests added | 3 new unit files + 6 E2E cases + 2 geometry probes (project total: 492 vitest, 81 Playwright) |
| Codex findings | 0 (execution r1 `approved`) |
| Handoff Score (X/7) | 7/7 markers, 39/39 ACs |
| Rule Adherence (%) | 90% (4.5/5 sampled — see table) |
| Prompt→commit time | n/a — **no commit**; draft prepared, human approval required |

### Rules Sampled for Adherence Check

| Rule | Source | Followed? |
|------|--------|-----------|
| Never modify or neutralize tests to make them pass (G36) | AGENTS.md §Testing & TDD Protocol | Yes — AC-49.27's three changes are synchronisation points; every asserted value is unchanged, and the Red census asserts `no neutralized tests` |
| Self-review prohibition — implementer never authors the verdict | AGENTS.md §Execution Contract | Yes — dispatched to `gpt-5.6-sol`; `EXEC_DISPATCH_CHECK` binds the verdict to dispatch `exec-review-p10-queue-card-dnd-r1` |
| Never auto-commit | AGENTS.md §Commits | Yes — draft written to `C:/Temp/av-kit/`, nothing committed |
| Redirect every process stream to `C:/Temp/av-kit/`, capture `$LASTEXITCODE` immediately | AGENTS.md §P0 | Mostly — two mid-session status probes were run unredirected and returned empty output, which is exactly the failure mode the rule exists to prevent; both were re-run with `*>` and then worked |
| `[B]` is evidence-gated | AGENTS.md §Execution Contract | Yes — nothing was marked `[B]`; the one candidate (reviewer host cannot launch Electron) is the reviewer's environment, and the suite ran 81/81 here |

---

## Instruction Coverage

```yaml
schema: v1
session:
  id: "78afc294-c127-4515-ae79-caf78929bf56"
  task_class: "tdd"
  outcome: "success"
sections:
  - id: "priority_0_system_constraints"
    cited: true
    influence: 2
  - id: "execution_contract"
    cited: true
    influence: 3
  - id: "testing_tdd_protocol"
    cited: true
    influence: 3
  - id: "session_discipline"
    cited: true
    influence: 2
  - id: "human_approval_gate"
    cited: true
    influence: 2
  - id: "dual_agent_workflow"
    cited: true
    influence: 2
  - id: "pre_handoff_self_review"
    cited: true
    influence: 2
  - id: "planning_contract"
    cited: false
    influence: 0
  - id: "code_quality"
    cited: false
    influence: 1
loaded:
  workflows: []
  roles: []
  skills: []
  refs:
    - "docs/execution/plans/2026-09-03-p10-queue-card-dnd/implementation-plan.md"
    - "docs/execution/plans/2026-09-03-p10-queue-card-dnd/task.md"
    - "docs/execution/plans/2026-09-03-p10-queue-card-dnd/named-sets.json"
    - ".agent/context/handoffs/TEMPLATE.md"
    - "docs/execution/reflections/TEMPLATE.md"
    - ".agent/schemas/reflection.v1.yaml"
    - "ui/node_modules/@dnd-kit/core/dist/core.esm.js"
    - "ui/node_modules/@dnd-kit/sortable/dist/sortable.esm.js"
decisive_rules:
  - "P1:never-modify-tests-to-pass"
  - "P1:self-review-prohibition"
  - "P2:done-is-the-only-completion-signal"
  - "P0:never-auto-commit"
  - "P1:evidence-first-completion"
conflicts:
  - "PHASE_EXIT_ASSERTIONS required `status: complete` in meu-status.yaml, but tools/meu_status.py accepts only {approved,...} and rejects hand-edits at render --check. The gate was satisfiable only by breaking the SSOT it guards. Resolved as correction X5 by matching the tool's real vocabulary rather than widening the pattern."
  - "EXEC_DISPATCH_CHECK required a line-anchored `verdict:` in the reviewer's free-form final.md, a format no instruction ever gave the reviewer. metrics.md:27 shows session 21 paid a full re-dispatch round to this same gate and left it armed. Resolved as correction X6."
note: "Both conflicts were gates whose self-test fixtures were written to agree with the gate, so neither had ever met its real producer."
slim_candidate:
  - "Efficiency Metrics: the prior two reflections flagged `Total tool calls` / `Time to first green test` / `Prompt→commit time` as uninstrumented three sessions running. This session instrumented the first two by hand (~55 calls, ~4 min) — but hand-counting is not instrumentation and will not survive a longer session. Either wire them to the harness or delete the rows; asking a fourth time is the waste."
  - "Next Day Outline duplicates current-focus.md, which is the file actually read at session start. Flagged by the two previous reflections and still present. Keep one."
  - "The X3/X4 className locks in downloader-page.test.ts / convert-page.test.ts: they assert source strings, passed on the broken tree, and are guards rather than tests. Worth keeping as MEU-52 tripwires, but they should not be counted as behavioural coverage."
  - "dual_agent_workflow: the fallback chain is restated in three places (AGENTS.md, model-routing.md, cli-dispatch/SKILL.md) and only model-routing.md is canonical."
overthinking_observed: false
review_churn:
  rounds_to_approval: { plan: 7, execution: 1 }
  findings_per_round:
    - { round: 1, critical: 0, high: 0, medium: 0, low: 0 }
  churned_findings: 0
  finding_categories: {}
  verdicts: { approved: 1 }
meu_work_classes: ["correctness"]
```
