---
date: "2026-09-02"
project: "p10-queue-card-foundations"
meus: ["MEU-41", "MEU-42", "MEU-43", "MEU-44"]
plan_source: "docs/execution/plans/2026-08-28-p10-queue-card-foundations/implementation-plan.md"
template_version: "2.0"
---

# 2026-09-02 Meta-Reflection

> **Date**: 2026-09-02
> **MEU(s) Completed**: MEU-41 (canon-queue-cards), MEU-42 (requeue-widening), MEU-43 (gui-queue-primitives), MEU-44 (gui-queue-card)
> **Plan Source**: `docs/execution/plans/2026-08-28-p10-queue-card-foundations/implementation-plan.md`

---

## Execution Trace

### Friction Log

1. **What took longer than expected?**

   The **plan** did, by a wide margin: 7 external review rounds and 8 correction passes before the
   human lifted the gate — against 2 execution-review rounds once code existed. The plan was
   doubling as a spec (MEU-41 *authors* `docs/build-plan/10-queue-card-ui.md`), so every round the
   reviewer was adjudicating product decisions, not implementation risk. Two rounds (R2, R3) were
   burned entirely on the PR-6 correction-census pre-verdict gate without any finding being
   adjudicated on its merits.

   Inside execution, the expensive item was the **MEU-43 contrast matrix**: 10 of 80 label pairings
   disagreed with the MEU-41 baseline on the first Green run. That was a genuine data defect in the
   committed baseline, not a test bug, and it took a full re-derivation to prove which side was
   wrong rather than editing the expectation.

2. **What instructions were ambiguous?**

   `.agent/docs/commands.md:20` registers `uv run ruff check packages/` as the canonical lint
   receipt, but the plan's own row-7 gate lints `packages/ tests/`. Nothing says which wins, and the
   gap silently hid 29 pre-existing `tests/` violations until the plan's stricter gate found them.
   Flagged in the MEU-42 handoff rather than silently resolved; still unresolved.

   `ruff format --check` is in no registered receipt at all. It reports 23 files repo-wide, none of
   which this session touched. Either it is part of the gate or it is not — right now it is
   ambient noise that every session has to individually decide to ignore.

3. **What instructions were unnecessary?**

   None were dead weight, but the **Efficiency Metrics** table below is unmeasurable in this harness
   (see `slim_candidate`), and the `[B]` rule's evidence list is *procedurally* satisfiable by a
   wrong diagnosis — see friction item 5.

4. **What was missing?**

   A rule that says: **before attributing a tool failure to an external dependency, reproduce it
   outside your own shell.** The `[B]` protocol demands a reproduced error, a receipt path and a
   linked follow-up. I produced all three, and the diagnosis was still wrong. The gate checks the
   *form* of the evidence, not whether the causal claim was tested.

   Also missing: the plan's H2-2 grouping gate asserted session `19` while the grouping file and
   `GROUPING_DONE_MARK` both say Session 20 — a regex that could never match. Seven plan-review
   rounds and a 526-site correction census did not catch it, because the censuses sweep *named-set
   literals* and this number was hand-written into a validation cell.

5. **What did you do that wasn't in the prompt?**

   Two unplanned diagnoses, both user-triggered:

   - **`npm run dev` produced no window.** A stale av-kit Electron instance from earlier in the day,
     hidden by close-to-tray (`ui/src/main/index.ts:463-465`), held the single-instance lock; every
     later `npm run dev` built fine, lost the lock at `index.ts:90-93`, called `app.quit()` and
     exited **0**. Silent success-shaped failure. Fixed by killing the zombie; the underlying bugs
     (`second-instance` restores a minimized window but never `show()`s a hidden one; losing the
     lock exits 0) are **not** fixed — out of this project's scope, and the user's direction was to
     stay with the plan.
   - **Retracting my own `[B]`.** `ELECTRON_RUN_AS_NODE=1` was set in my shell (inherited from the
     Cursor extension host) and spread into every launched app by `...process.env` at all 14
     `_electron.launch()` sites. `electron --version` prints `v24.18.1` with it set and `v42.9.3`
     without. With it unset and the bundle rebuilt first: **59 passed / 0 failed**. The
     "Electron 42.9.3 / playwright-core 1.62.1 incompatibility" claim was mine and was wrong;
     `task.md` H1-2a, four handoff disclosure paragraphs and the known-issue entry were all
     corrected.

### Quality Signal Log

6. **Which tests caught real bugs?**

   - `queue-primitives.test.ts` contrast matrix — caught 10 wrong values in a committed data
     baseline that a human eyeball would have accepted.
   - The reviewer's own real-stack reproduction caught the one finding that mattered: a *nonblank
     stale* blocker message survived `apply_defaults_to_pending()`, so a 360p job read
     "The requested 1080p quality is unavailable". My AC-42.12/42.14 tests covered the **blank**
     legacy shape and stopped there — I tested the case I had thought of, and the invariant had two
     shapes.
   - The two `test_r1f1_*` tests written to close it failed before the fix and pass after; the
     reviewer independently confirmed reverting either production change re-breaks its test.

7. **Which tests were trivially obvious?**

   Several MEU-43 primitive tests (`StatusBadge` renders its label, `ProgressBar` clamps 0–1) are
   near-tautological. They are cheap and they pin the prop contract the cards depend on, so they
   stay — but they are not where the defects were.

8. **Did pyright/ruff catch anything meaningful?**

   pyright: nothing this session — the domain is fully annotated and the fix was a control-flow
   change inside an already-typed function. ruff: only the 29 pre-existing `tests/` violations
   surfaced by the scope conflict in friction item 2, all formatting-class.

### Workflow Signal Log

9. **Was the FIC useful as written?**

   Yes for MEU-43/44 (52 declared Red tests, `RED_COUNT` per MEU matched the plan exactly:
   `41|8`, `42|15`, `43|13`, `44|16`). It was **insufficient** for MEU-42's central invariant:
   AC-42.12/42.14 said a blocked row "always carries the canonical reason", but every AC enumerated
   only the *blank* producer. An acceptance criterion that states an invariant should enumerate the
   ways it can be violated, not the ways it is established.

10. **Was the handoff template right-sized?**

    Yes. The "Disclosures the reviewer should check first" block above the cache boundary earned its
    keep twice: the reviewer opened round 1 by checking the disclosed Green-phase edits, and caught
    that my *dispatch prompt* understated them ("exactly one Green-phase test edit" — the MEU-42
    handoff already disclosed two). The handoff was honest; the prompt summarising it was not.

11. **How many tool calls did this session take?**

    Not instrumented in this harness and not recoverable after compaction. Ordinal facts instead:
    8 plan-correction passes, 7 plan-review dispatches, 2 execution-review dispatches, 1 context
    compaction at the ~50% checkpoint (continued, per the sanctioned turn-ender), 54 tests added.

12. **Which rows were delegated, to which subagent (harness + model), and did any delegated result need rework?**

    None. Every row ran in the coordinator (Claude Code / Opus 5). In hindsight MEU-43's contrast
    matrix re-derivation and the 624-substitution `MEU-40 → MEU-41` renumber were both
    mechanical-class and were the two best delegation candidates of the session — see RULE-3.

---

## Pattern Extraction

### Patterns to KEEP

1. **Real-stack integration tests over fakes for persisted-state invariants.** `tests/e2e/real_stack.py`
   drives route → service → domain → repository against real SQLite. The one finding of the session
   was only *findable* because the reviewer could reproduce it there; a fake repository would have
   returned whatever it was told.
2. **"Review substance, not ceremony" in the dispatch prompt.** Both execution rounds came back with
   zero process findings and one real defect. The reviewer spent round 2 running a synthetic
   120,000-row migration scale test instead of auditing my template section order.
3. **Disclosure block above the cache boundary.** It makes the reviewer's first move an audit of my
   own admissions, which is exactly where the round-1 evidence caveat surfaced.
4. **Retract loudly and everywhere.** When the `[B]` fell, correcting it meant touching `task.md`,
   four handoffs, the known-issue YAML, `current-focus.md` and the round-2 prompt. Leaving any one
   of those stale would have left a false claim in the institutional record.

### Patterns to DROP

1. **The "external cause" reflex on tool-launch failures.** A reproduced error message plus a receipt
   satisfied the `[B]` gate and I stopped investigating. Environment-shaped failures deserve
   *more* suspicion of the local environment, not less.
2. **Letting plan review adjudicate product copy.** Rounds 4–7 were largely about the wording and
   lifecycle of one `error_message` string. That is a spec question; it belongs in the build-plan
   document before the plan-review loop opens, not inside it.

### Patterns to ADD

1. **Invariant ACs must enumerate violation shapes.** For any AC of the form "X always holds",
   list the distinct ways X can be false (here: absent, blank, *stale*) and give each its own test.
2. **A cheap "does this literal exist?" pass over hand-written validation regexes** at plan-freeze
   time — the census gates only sweep named-set values, so numbers typed directly into validation
   cells are unchecked.

### Calibration Adjustment

- Estimated time: 4 MEUs, one session, plan approved same day.
- Actual time: plan phase dominated (7 review rounds / 8 correction passes over multiple days);
  execution + 2 review rounds landed in one session.
- Adjusted estimate for similar MEUs: when a plan's first MEU **authors the spec**, budget the spec
  as its own review cycle *before* the plan review, or expect ~3× the plan-review rounds.

---

## Next Session Design Rules

```
RULE-1: Before marking a tool-launch failure [B] as an external/dependency cause, reproduce it
        with a clean environment (empty or allow-listed env, fresh shell). The [B] gate checks
        the shape of the evidence, not the truth of the causal claim.
SOURCE: I filed E2E-ELECTRON-LAUNCH-FLAG as an Electron/playwright version incompatibility with a
        reproduced error, a receipt and a linked follow-up — all three gate conditions met — and it
        was wrong. The cause was ELECTRON_RUN_AS_NODE=1 in my own shell.
EXAMPLE: `[B]` "58/59 fail: electron.exe: bad option --remote-debugging-port=0, external"
         → `electron --version` with and without the var (v24.18.1 vs v42.9.3) → `[x]` 59 passed.
```

```
RULE-2: An acceptance criterion that asserts an invariant must enumerate the invariant's violation
        shapes, one test per shape — not just the producers that establish it.
SOURCE: AC-42.12/42.14 asserted "every blocked row carries the canonical reason" but tested only the
        blank shape. The stale-nonblank shape shipped and became the session's only review finding.
EXAMPLE: "blocker reason always canonical" → cases: {absent, blank/whitespace, stale-noncanonical}
         × surfaces {add, save, apply-defaults, refused-retry, upgrade}.
```

```
RULE-3: Delegate mechanical-class rows (bulk renames, data-baseline re-derivation, census sweeps) to
        av-kit-builder instead of running them in the coordinator; keep correctness-class rows inline.
SOURCE: The 624-substitution MEU-40→MEU-41 renumber and the 80-pairing contrast-matrix re-derivation
        both ran in the coordinator and consumed the context budget that later forced a compaction.
EXAMPLE: `run-correction-census.ps1` sweep + fixups → av-kit-builder; the blocker-reason fix → inline.
```

---

## Next Day Outline

1. Target MEUs: **MEU-45–47** (`p10-queue-card-migration`) — mount `QueueList`/`QueueCard` on the
   Downloader, Transcript and Conversion pages, retire `queue-table`/`queue-row`.
2. Scaffold changes needed: `PAGE_ISOLATION_RULE` must be **inverted or retired** for the migration
   plan — it currently fails the build if any page mounts these components, which is precisely what
   MEU-45–47 do. Do not silently delete it; replace it with a mount-completeness gate.
3. Patterns to bake in from today: RULE-2 for the migration's ACs (the bulk-bar and selection
   invariants have the same "enumerate violation shapes" risk); real-stack/E2E coverage for the
   page-level behaviours, not just component unit tests.
4. Codex validation scope: the page-level interaction model (one primary action per row, the sticky
   bulk bar, `Cancel queue` blast radius) and the retirement of the old table without behaviour loss.
5. Time estimate: one session for MEU-45 + MEU-46 if the isolation gate is replaced during planning;
   two if the gate replacement itself needs review.
6. Carry forward unfixed: the two Electron main-process bugs (hidden-window `second-instance`,
   exit-0 on lost single-instance lock) and the `ruff check` scope conflict.

---

## Efficiency Metrics

| Metric | Value |
|--------|-------|
| Total tool calls | Not instrumented in this harness (see `slim_candidate`) |
| Time to first green test | Not instrumented |
| Tests added | **54** — 37 vitest (`queue-canon` 8, `queue-primitives` 13, `queue-card` 16) + 17 pytest (15 `test_ac_42_*`, 2 `test_r1f1_*`) |
| Codex findings | Plan review: 7 rounds, ~20 findings, final round `changes_required` (R7-F1 High) lifted by explicit human direction. Execution review: round 1 = 1 High, round 2 = **0, `approved`** |
| Handoff Score (X/7) | 7/7 — four handoffs, all passing `assert-handoff-acs.ps1` and `assert-handoff-markers.ps1` |
| Rule Adherence (%) | 6/7 sampled = **86%** (see table) |
| Prompt→commit time | N/A — **uncommitted**; human approval required before any `git commit` |

### Rules Sampled for Adherence Check

| Rule | Source | Followed? |
|------|--------|-----------|
| Tests first, implementation after — Red evidence saved before Green | AGENTS.md §Testing & TDD Protocol | Yes — `C:/Temp/av-kit/r1f1-red.txt` (2 failed) predates every production edit |
| Never modify or neutralize tests to make them pass | AGENTS.md §Testing & TDD Protocol / G36 | Yes — one setup-order change and one SQL-mirror constant, both disclosed; no assertion, title or expected value altered |
| Self-review prohibition — implementing agent never authors its own verdict | AGENTS.md §Execution Contract | Yes — both execution rounds authored by `gpt-5.6-sol` via `Invoke-CodexDispatch.ps1` |
| Never auto-commit | AGENTS.md §Commits | Yes — nothing committed; H2-5 prepares a message only |
| `[B]` only for a *reproduced external* error with receipt + follow-up | AGENTS.md §Execution Contract | **No** — the evidence was produced but the causal claim was untested and wrong; retracted this session (RULE-1) |
| Windows P0 redirect-to-file, capture `$LASTEXITCODE`, never pipe long-running processes | AGENTS.md §PRIORITY 0 | Yes — every gate wrote to `C:/Temp/av-kit/`; the 10-minute Codex dispatch ran backgrounded to a receipt |
| Closeout artifacts written from template + peer exemplar, never from memory | AGENTS.md §Session Discipline | Yes — `C:/Temp/av-kit/reflection-source-read-p10-queue-card-foundations.txt`; template, schema and the P9 peer re-read after compaction |

---

## Instruction Coverage

```yaml
schema: v1
session:
  id: "b60e1d43-1039-4a09-854e-a5bb1d6e10c4"
  task_class: tdd
  outcome: success
sections:
  - id: testing_tdd_protocol
    cited: true
    influence: 3
  - id: execution_contract
    cited: true
    influence: 3
  - id: priority_0_system_constraints_non_negotiable
    cited: true
    influence: 3
  - id: pre_handoff_self_review_mandatory
    cited: true
    influence: 2
  - id: windows_shell_powershell
    cited: true
    influence: 2
  - id: session_discipline
    cited: true
    influence: 2
  - id: dual_agent_workflow
    cited: true
    influence: 2
  - id: commits
    cited: true
    influence: 3
  - id: artifact_naming_convention
    cited: true
    influence: 2
  - id: validation_pipeline
    cited: true
    influence: 2
  - id: code_quality
    cited: true
    influence: 1
  - id: testing_requirements
    cited: true
    influence: 1
  - id: communication_policy
    cited: true
    influence: 1
  - id: planning_contract
    cited: false
    influence: 0
  - id: architecture
    cited: false
    influence: 0
  - id: mcp_servers
    cited: false
    influence: 0
loaded:
  workflows:
    - execution_critical_review
    - execution_corrections
  roles:
    - coder
    - tester
    - orchestrator
  skills:
    - cli_dispatch
    - completion_preflight
    - terminal_preflight
  refs:
    - AGENTS.md
    - GUARDRAILS.md
    - docs/execution/plans/2026-08-28-p10-queue-card-foundations/task.md
    - docs/execution/plans/2026-08-28-p10-queue-card-foundations/named-sets.json
    - docs/execution/reflections/TEMPLATE.md
    - .agent/schemas/reflection.v1.yaml
    - docs/execution/reflections/2026-08-27-p9-capture-native-picker-reflection.md
review_churn:
  rounds_to_approval:
    plan: 7
    execution: 2
  findings_per_round:
    - { round: 1, critical: 0, high: 1, medium: 0, low: 0 }
    - { round: 2, critical: 0, high: 0, medium: 0, low: 0 }
  churned_findings: 0
  finding_categories:
    contract_drift: 1
  verdicts:
    changes_required: 1
    approved: 1
meu_work_classes:
  - mixed
  - correctness
  - mechanical
  - correctness
decisive_rules:
  - "P0:tests-first-red-before-green"
  - "P1:independent-review-never-self-authored"
  - "P0:never-modify-tests-to-pass"
  - "P0:never-auto-commit"
  - "P1:B-requires-reproduced-external-error"
conflicts:
  - "`.agent/docs/commands.md:20` registers `ruff check packages/` as canonical, but this plan's row-7 gate lints `packages/ tests/`. Nothing arbitrates; the wider gate found 29 pre-existing violations the canonical receipt never sees. Still open."
  - "`ruff format --check` belongs to no registered receipt yet reports 23 repo-wide files. Every session must independently decide to ignore it — that is a rule gap, not a finding."
  - "The `[B]` rule's evidence list (reproduced error + receipt + follow-up) is satisfiable by a confidently wrong diagnosis. It gates evidence *form*, not causal verification — RULE-1 patches this from the agent side; the rule itself still has the hole."
  - "`.agent/context/harness.local.md` declares `plan_to_exec_gate: reviewer-auto`, but this session ran on Claude Code (`human`). SIGN 1 resolves toward the driving harness, and in fact the plan never reached `approved` — round 7 returned `changes_required` and execution was authorised by explicit human direction. The local file still reads as if it were project-wide."
slim_candidate:
  - "Efficiency Metrics table — 'Total tool calls', 'Time to first green test' and 'Prompt→commit time' are uninstrumented in every current harness. Three of seven rows are filled with 'not instrumented' each time. Delete them or instrument them; this is the second consecutive reflection to say so."
  - "Next Day Outline — overlaps `current-focus.md`, which is the file actually read at session start. Keep one."
overthinking_observed: false
note: "The single execution finding existed because an invariant AC enumerated its producers instead of its violation shapes."
```

> **De-flatter note:** the three `influence: 0` entries are honest. `planning_contract` never applied
> — this session started already inside an approved plan; `architecture` was fixed by the plan and
> never consulted; no MCP tool was invoked on any row. The `[B]` row in the Rule Adherence table is a
> genuine **No**: the rule was followed procedurally and failed to prevent a false claim, which is
> more useful telemetry than a clean 7/7 would have been.
