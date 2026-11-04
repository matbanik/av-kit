---
date: "2026-09-03"
project: "p10-queue-card-migration"
meus: ["MEU-45", "MEU-46", "MEU-47"]
plan_source: "docs/execution/plans/2026-09-02-p10-queue-card-migration/implementation-plan.md"
template_version: "2.0"
---

# 2026-09-03 Meta-Reflection

> **Date**: 2026-09-03
> **MEU(s) Completed**: MEU-45 (convert queue migration), MEU-46 (downloader queue migration), MEU-47 (selection + bulk model)
> **Plan Source**: `docs/execution/plans/2026-09-02-p10-queue-card-migration/implementation-plan.md`

---

## Execution Trace

### Friction Log

1. **What took longer than expected?**

   The execution review, and not because the code was weak — because two of the three rounds
   were spent on things other than the software.

   - **Round 1** returned `changes_required` with 6 findings against a fully green gate
     (428 vitest, 178 mount checks, 73 Playwright). Five were real. That round was worth
     every minute.
   - **Round 3** existed solely because my round-2 prompt forgot one line. The plan's own
     gate, `assert-exec-review-dispatch.ps1:164-172`, requires the **dispatch's final
     output** — the `-o final.md` message, which only a dispatched CLI can write — to state
     `verdict:` in machine-readable form, so that an `approved` review file can never be
     hand-authored by the implementer. The round-1 prompt asked for that line. I rewrote the
     prompt from scratch for round 2 and dropped it. The reviewer wrote "Approved —
     `findings_count: 0`" in prose, the gate refused it, and the only honest remedy was
     another ~5-minute dispatch. I will not hand-edit `final.md`; that is precisely the
     forgery the gate exists to prevent.

   Secondary: I read the rolling review file at 12:52 and drew a conclusion from it while the
   dispatch was still writing (`final.md`, `receipt.txt` and `status.json` all landed at
   12:55). The content I read was correct, but the inference "the review is done" was not.

2. **What instructions were ambiguous?**

   Nothing in AGENTS.md/GUARDRAILS.md read ambiguously this session. The ambiguity was in
   this plan's own artifacts: three task rows (22, H1-2, H1-4) name
   `tools/run-meu-gate.ps1` as their validation command, and that file has never existed in
   the repo or in git history. The rows are satisfiable — the task's execution note
   authorises running the four verification-plan commands directly, and `MEU_GATE` in
   `named-sets.json:517-519` is the authoritative list — but a reader following the
   validation column alone hits a dead path. Disclosed as R1-D; the reviewer independently
   judged it clerical debt rather than a missing validator.

3. **What instructions were unnecessary?**

   None were unnecessary, but the `Efficiency Metrics` table below is now three consecutive
   reflections with the same three uninstrumented rows. That is a template problem, not a
   session problem — see `slim_candidate`.

4. **What was missing?**

   **A binding link between a review gate and the prompt that must satisfy it.** The gate
   script and the reviewer prompt are authored separately, by hand, with nothing checking
   that the prompt asks for what the gate demands. That gap cost a full review round. The
   same gap would cost a round again next session, for a different gate, unless the prompt
   is generated from the gate's requirements or the gate's requirements are restated in a
   prompt template.

   Also missing: any check that a `named-sets.json` entry's `value` is actually supported by
   its `source`. The single-statement rule guarantees a set is stated **once**; it guarantees
   nothing about that statement being **true**. `G32_RULE.value` claimed "Interactive targets
   are at least 44x44 CSS px" while its cited source, `.agent/docs/emerging-standards.md:1098`,
   defines G32 as "CSS Variable Tokens Only (No Raw Hex in className)". A transcription defect
   at plan time became a High finding at review time and consumed reviewer attention that
   should have gone to the software.

5. **What did you do that wasn't in the prompt?**

   - **Proved every regression genuinely Red by reverting its fix.** Not required by any row;
     without it, "I added a test for that" is an unfalsifiable claim. Receipts:
     `r2-sel-red.txt` (F1, 2 failed / 6 passed), `redcheck.txt` (F2/F3/F6, 2 failed each
     across both pages), `f4-red.txt` (F4).
   - **Instructed the round-2 reviewer to re-derive Finding 5 independently and to re-raise it
     if a hit-target rule genuinely binds.** I had concluded the finding was invalid; asking
     the reviewer to accept my reasoning would have converted an independent review into a
     rubber stamp on my own judgement. It re-derived it from source and reached the same
     conclusion, citing `10-queue-card-ui.md:244` and `Button.tsx:23-25` — evidence I had not
     put in front of it.
   - **Mirrored all three page-level regressions onto the downloader**, which
     `BULK_CONTROL_E2E_OBLIGATION` requires but no round-1 finding named.

### Quality Signal Log

6. **Which tests caught real bugs?**

   Honest answer: **none of the 428 pre-review tests caught any of the five real defects.**
   The gate was green and false-green. The reviewer caught them by reading the code against
   the frozen contracts. The tests that matter are the six regressions written *after* the
   findings, and their value is proven only by the revert-and-fail receipts above.

   The one test that carried real signal did so by breaking: `AC-47.8` failed the moment the
   Finding 2 fix landed, because it had been chaining three bulk verbs off a single
   `queue-select-all` tick — which only worked while `moveSelected` was wrongly keeping the
   selection alive. A test passing for the wrong reason is worse than a missing test, and the
   only reason it surfaced is that the fix was applied before the test was re-read.

7. **Which tests were trivially obvious?**

   Parts of the mount-completeness census. 178 checks is thorough, but a large share assert
   that a testid string appears in a file — real coverage against silent deletion, near-zero
   coverage against wrong behaviour. Every one of the five defects lived in a file whose
   mount checks were green.

8. **Did pyright/ruff catch anything meaningful?**

   Not applicable and worth stating plainly: this project touched no Python. TypeScript's
   `typecheck` and ESLint were clean at every gate and caught **nothing** — all five defects
   were type-correct, lint-clean and semantically wrong. Static analysis contributed zero
   findings this session.

### Workflow Signal Log

9. **Was the FIC useful as written?**

   Useful, but it repeated the exact failure the previous reflection named. Foundations closed
   with: *"the single execution finding existed because an invariant AC enumerated its
   producers instead of its violation shapes."* This session, **AC-45.1** and **AC-47.1** did
   the same thing. AC-45.1 said the meta line "filters placeholder segments" — it named the
   behaviour, not the shape of its violation, and the implementation filtered only the
   page-owned tail, so a Skipped row rendered `— · Compress · Balanced`: a placeholder
   standing in front of the very facts it substitutes for. AC-47.1 said selection "prunes
   vanished ids" — the code pruned the derived projection while the backing `Set` and the
   anchor kept the dead id. Both ACs were testable as written and both were tested; the tests
   asserted the producer, not the violation.

   The carry-forward rule was written down and did not change behaviour. That is the finding.

10. **Was the handoff template right-sized?**

    Yes. Three MEU handoffs plus one rolling review file, all passing
    `assert-handoff-markers.ps1` (3 × 7 markers) and `assert-handoff-acs.ps1` (52 ACs). The
    rolling-review convention proved its worth under three rounds: the reviewer appended
    `## Round 2` and `## Round 3` to one file and could read its own prior reasoning, which is
    how it was able to close each round-1 finding by number.

11. **How many tool calls did this session take?**

    Not instrumented in this harness. Third consecutive reflection with that answer.

12. **Which rows were delegated, to which subagent (harness + model), and did any delegated
    result need rework?**

    Claude Code coordinator (Opus 5) with `.claude/agents/` subagents (Sonnet), both routes
    probed live and recorded in `.agent/skills/subagent-delegation/verification-log.md`.

    - **`av-kit-verifier` (readonly)** — every verbose gate run: the MEU gate, the
      post-correction re-run, the Playwright suite. No rework needed, and the point of the
      route is that ~440 lines of vitest output never entered the coordinator context.
    - **`av-kit-builder` (write)** — the `npx --prefix ui vitest run` → `npm --prefix ui run
      test` correction across 14 plan-artifact occurrences. No rework; coordinator
      independently confirmed 0 remaining broken forms and intact column counts.

    One delegated result **did** need scrutiny: the verifier's first probe reported 17 files /
    67 tests failed. That was correct reporting of a broken command, not a bad subagent — the
    coordinator's `npx --prefix ui` invocation left cwd at the repo root, so vitest ignored
    `ui/vitest.config` and swept in Playwright specs. The delegation surfaced a coordinator
    error. That is the route working.

---

## Pattern Extraction

### Patterns to KEEP

- **Revert-and-fail as the proof a regression is real.** Six regressions, six receipts. It
  converts "I added a test" from a claim into evidence, and it is cheap.
- **Scoping the reviewer to substance and saying so explicitly.** The round-2 prompt opened
  with "Do not spend the review on artifact formatting… A finding whose only content is
  'section X is thin' is noise." All three rounds returned software findings only.
- **Asking the reviewer to re-derive a conclusion I had already reached.** Finding 5 is the
  case: I believed it invalid, and the correct move was to hand the reviewer the question, not
  the answer.
- **The rolling one-file-per-target review convention.** Three rounds of continuity in one
  file is why round 2 could close six findings by number.

### Patterns to DROP

- **Treating a written artifact as the completion signal for a dispatch.** The review file is
  written *during* the run. `status.json` is written last, by the wrapper, after the child
  exits. Watch the sentinel, not the payload.
- **Rewriting a reviewer prompt from scratch each round.** Round 2's prompt was better prose
  than round 1's and was missing a required output clause. The gate-facing parts of the prompt
  are not the creative part.

### Patterns to ADD

- **Diff the new prompt against the previous round's prompt for dropped output requirements
  before dispatching.** A three-second check that would have saved a round.
- **At plan time, open every `named-sets.json` `source` and confirm it supports its `value`.**
  Not "does the source exist" — "does the source say this".

### Calibration Adjustment

I was well calibrated on the code and badly calibrated on the harness. I predicted round 2
would approve, and it did, with zero findings. I did not predict that an approved review would
fail its own approval gate. **Green software plus an approving reviewer is still not `DONE`**;
the machine-checked artifacts are a third thing, and they fail independently of both.

The other calibration miss: I trusted a frozen named set because it was frozen. Freezing a
value prevents *drift*, not *error*. A frozen wrong value is more dangerous than an unfrozen
one, because every AC that cites it inherits the error and the single-statement rule guarantees
nobody will restate it in a form that might disagree.

---

## Next Session Design Rules

```
RULE-1: Before dispatching review round N, diff the new prompt against round N-1's prompt
        and confirm every machine-checked output requirement survived. If a gate script
        validates the dispatch, read that script's assertions first and satisfy each one
        explicitly in the prompt.
SOURCE: Round 2 returned `approved`/0 findings and still failed
        `assert-exec-review-dispatch.ps1` because the prompt never asked for a `verdict:`
        line in the dispatch final output. Cost: one full extra review round.
EXAMPLE: before → round-2 prompt specifies only the review file's YAML frontmatter;
         after  → prompt carries a "Part 2 — your final message" section restating the
                  gate's `(?im)^\s*verdict:` requirement verbatim.
```

```
RULE-2: Wait on the dispatch wrapper's `status.json`, never on the artifact the reviewer is
        writing. Treat any conclusion drawn from a mid-write artifact as provisional until
        the sentinel exists.
SOURCE: The rolling review file read complete and correct at 12:52; `final.md`,
        `receipt.txt` and `status.json` landed at 12:55, and the gate run in between failed
        on a file that simply did not exist yet.
EXAMPLE: before → `until [ -f .../final.md ]`, or reading the review file and inferring;
         after  → `until [ -f .../status.json ]`, then read `exit_code` from it.
```

```
RULE-3: A named set is not trustworthy because it is frozen. At plan time, open each entry's
        `source` at the cited line and confirm the source text supports the `value`. Record
        the check, and on any mismatch correct the set against the source and note the defect
        in the entry.
SOURCE: `G32_RULE.value` asserted a 44x44 hit-target rule; `emerging-standards.md:1098`
        defines G32 as the no-raw-hex token rule. Nine ACs cited the set. The defect
        produced a High execution finding that was not a code defect at all, and would have
        contradicted the frozen `G34_RULE` button sizes had it been "fixed".
EXAMPLE: before → `{"value": "Interactive targets are at least 44x44 CSS px",
                    "source": ".agent/docs/emerging-standards.md:1098"}`;
         after  → value quoted verbatim from that line, plus a `note` recording the
                  transcription defect and its blast radius.
```

---

## Next Day Outline

1. **Target MEU(s)** — MEU-48/49 (Phase 10 remainder) per `meu-registry.md`; MEU-45/46/47 are
   `✅ approved` and rendered.
2. **Scaffold changes needed** — none for the queue surface; `use-queue-selection`,
   `use-queue-bulk`, `run-bulk`, `bulk-reorder` and the bare/reconciling command split are in
   place and reviewed. Reuse them rather than re-deriving.
3. **Patterns to bake in from today** — RULE-1 through RULE-3; AC violation-shape phrasing
   (Q9), which is now a two-session-old unfixed carry-forward and should be enforced in the
   FIC step, not remembered.
4. **Codex validation scope** — one round should suffice if RULE-1 and RULE-3 hold; budget two.
5. **Time estimate** — not estimated; time is not a session constraint under §Session
   Discipline.
6. **Open at exit** — the working tree is **uncommitted** by policy; H2-5 prepares a commit
   message only. `E2E-SANDBOX` residual risk stands: the reviewer's independent Electron launch
   died in the GPU subprocess (`GPU process isn't usable`, exit `2147483651`), so the 73-pass
   Playwright result rests on the coordinator's receipt with `ELECTRON_RUN_AS_NODE` unset.

---

## Efficiency Metrics

| Metric | Value |
|--------|-------|
| Total tool calls | Not instrumented in this harness (see `slim_candidate`) |
| Time to first green test | Not instrumented |
| Tests added | **86** — vitest 366 → **438** (+72, 43 → 54 files) and Playwright 59 → **73** (+14), measured against the `p10-queue-card-foundations` exit counts |
| Codex findings | Plan review: 3 rounds, round 1 = 9 findings (8 High, 1 Medium), `approved` at round 3 with 0. Execution review: round 1 = 6 (5 High, 1 Medium) of which **1 was invalid**; round 2 = **0, `approved`**; round 3 = 0, `approved` (gate-format re-dispatch, not a software round) |
| Handoff Score (X/7) | 7/7 — three MEU handoffs, `assert-handoff-markers.ps1` 3 × 7 markers and `assert-handoff-acs.ps1` 52 ACs both passing |
| Rule Adherence (%) | 6/7 sampled = **86%** (see table) |
| Prompt→commit time | N/A — **uncommitted**; human approval required before any `git commit` |

### Rules Sampled for Adherence Check

| Rule | Source | Followed? |
|------|--------|-----------|
| Tests first, implementation after — Red evidence saved before Green | AGENTS.md §Testing & TDD Protocol | Yes — and for the six corrections, proven by reverting each fix: `r2-sel-red.txt`, `redcheck.txt`, `f4-red.txt` |
| Never modify or neutralize tests to make them pass | AGENTS.md §Testing & TDD Protocol / G36 | Yes — one `AC-47.8` **setup** change, assertions byte-identical, disclosed as R1-B; reviewer independently confirmed against the round-1 source snapshot |
| Self-review prohibition — implementing agent never authors its own verdict | AGENTS.md §Execution Contract | Yes — all three execution rounds authored by `gpt-5.6-sol` via `Invoke-CodexDispatch.ps1`; `final.md` never hand-edited, which is why round 3 was dispatched instead |
| Never auto-commit | AGENTS.md §Commits | Yes — nothing committed; H2-5 prepares a message only |
| Windows P0 redirect-to-file, capture exit code, never pipe long-running processes | AGENTS.md §PRIORITY 0 | Yes — every gate wrote to `C:/Temp/av-kit/`; all three ~15-20 min dispatches backgrounded to receipts |
| Every plan task carries an **exact** validation command | AGENTS.md §Roles & Workflows | **No** — rows 22, H1-2 and H1-4 name `tools/run-meu-gate.ps1`, which does not exist. The rows were satisfied from the `MEU_GATE` named set, but the validation column is wrong on disk and was marked `[x]` before anyone tried to run it as written |
| Closeout artifacts written from template + peer exemplar, never from memory | AGENTS.md §Session Discipline | Yes — `C:/Temp/av-kit/reflection-source-read-p10-queue-card-migration.txt`; template, schema and the foundations peer reflection re-read after compaction |

---

## Instruction Coverage

```yaml
schema: v1
session:
  id: "b60e1d43-1039-4a09-854e-a5bb1d6e10c4"
  task_class: tdd
  outcome: success
sections:
  - id: execution_contract
    cited: true
    influence: 3
  - id: testing_tdd_protocol
    cited: true
    influence: 3
  - id: dual_agent_workflow
    cited: true
    influence: 3
  - id: priority_0_system_constraints_non_negotiable
    cited: true
    influence: 3
  - id: commits
    cited: true
    influence: 3
  - id: session_discipline
    cited: true
    influence: 2
  - id: pre_handoff_self_review_mandatory
    cited: true
    influence: 2
  - id: artifact_naming_convention
    cited: true
    influence: 2
  - id: windows_shell_powershell
    cited: true
    influence: 2
  - id: validation_pipeline
    cited: true
    influence: 2
  - id: roles_workflows
    cited: true
    influence: 2
  - id: testing_requirements
    cited: true
    influence: 1
  - id: code_quality
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
    - subagent_delegation
    - completion_preflight
    - terminal_preflight
  refs:
    - AGENTS.md
    - GUARDRAILS.md
    - docs/execution/plans/2026-09-02-p10-queue-card-migration/task.md
    - docs/execution/plans/2026-09-02-p10-queue-card-migration/named-sets.json
    - docs/execution/plans/2026-09-02-p10-queue-card-migration/assert-exec-review-dispatch.ps1
    - docs/execution/reflections/TEMPLATE.md
    - .agent/schemas/reflection.v1.yaml
    - docs/execution/reflections/2026-08-28-p10-queue-card-foundations-reflection.md
    - .agent/docs/emerging-standards.md
review_churn:
  rounds_to_approval:
    plan: 3
    execution: 3
  findings_per_round:
    - { round: 1, critical: 0, high: 5, medium: 1, low: 0 }
    - { round: 2, critical: 0, high: 0, medium: 0, low: 0 }
    - { round: 3, critical: 0, high: 0, medium: 0, low: 0 }
  churned_findings: 1
  finding_categories:
    claim_to_state_drift: 2
    contract_drift: 2
    provenance_error: 1
    other: 1
  verdicts:
    changes_required: 1
    approved: 2
meu_work_classes:
  - mixed
  - mechanical
  - correctness
decisive_rules:
  - "P1:independent-review-never-self-authored"
  - "P0:tests-first-red-before-green"
  - "P0:never-modify-tests-to-pass"
  - "P0:never-auto-commit"
  - "P0:windows-redirect-to-file"
conflicts:
  - "`assert-exec-review-dispatch.ps1:164-172` requires the dispatch's final output to carry a `verdict:` line, but nothing in `cli-dispatch/SKILL.md`, the workflow docs, or any prompt template states that requirement. The gate and the prompt that must satisfy it are authored independently by hand. This is a rule gap that cost one review round, not a finding against either artifact."
  - "AGENTS.md §Roles & Workflows requires every plan task to carry `validation` as exact commands, but nothing verifies at plan time that the named command resolves. `tools/run-meu-gate.ps1` is named by three rows, has never existed, and all three rows reached `[x]`. The evidence-first completion rule checks that evidence exists, not that the registered command is the one that produced it."
  - "`.agent/context/harness.local.md` declared `plan_to_exec_gate: reviewer-auto` in a yaml block that read as project-wide, while this session ran on Claude Code (`human`). SIGN 1 resolves toward the driving harness so nothing broke, but the same conflict was logged in the previous session's reflection and left standing. **Closed this session** by adding a `## Per-driver overrides` section: the yaml header is now explicitly the Cursor override, and a `### Claude Code` block records the `fresh_worker` flip and states that `plan_to_exec_gate` is deliberately NOT overridden there. The lesson worth keeping is that a flag file with no driver scope is a latent conflict on every harness but the one that wrote it."
  - "The single-statement rule (`named-sets.json`) is stated as a correctness mechanism but only guarantees non-duplication. It has no source-verification obligation attached, so a transcription defect in a frozen value propagates silently to every citing AC — exactly what `G32_RULE` did across nine ACs."
slim_candidate:
  - "Efficiency Metrics — 'Total tool calls', 'Time to first green test' and 'Prompt→commit time' are uninstrumented in every current harness. This is the THIRD consecutive reflection filling three of seven rows with 'not instrumented'. Delete them or instrument them; repeating the request without acting on it is the waste."
  - "Next Day Outline — overlaps `current-focus.md`, which is the file actually read at session start. Second consecutive reflection flagging it. Keep one."
overthinking_observed: false
note: "Five type-correct, lint-clean, fully-tested defects survived a green 428-test gate and were all caught by a human-style read of code against frozen contracts. The gate measures mounting, not meaning."
```

> **De-flatter note:** the three `influence: 0` entries are honest — `planning_contract` never
> applied (this session began inside an already-approved plan), `architecture` was fixed by the
> plan and never opened, and no MCP tool was invoked on any row. The Rule Adherence table
> contains a genuine **No**: three task rows carry a validation command that does not exist and
> were nonetheless marked `[x]`, by me, before anyone attempted to run them as written. The
> reviewer judged it clerical, and it is — but "clerical" is how a validation column becomes
> decorative. The headline result (0 findings at round 2) is also less flattering than it looks:
> round 1 found five real defects behind a fully green gate, which means the gate I built and
> ran is not yet capable of catching the class of defect this project produces.
