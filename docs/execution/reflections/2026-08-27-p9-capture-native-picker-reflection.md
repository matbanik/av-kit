---
date: "2026-08-27"
project: "p9-capture-native-picker"
meus: ["MEU-40"]
plan_source: "docs/execution/plans/2026-08-27-p9-capture-native-picker/implementation-plan.md"
template_version: "2.0"
---

# 2026-08-27 Meta-Reflection

> **Date**: 2026-08-27
> **MEU(s) Completed**: MEU-40 `native-region-picker`
> **Plan Source**: docs/execution/plans/2026-08-27-p9-capture-native-picker/implementation-plan.md

---

## Execution Trace

### Friction Log

1. **What took longer than expected?**
   Plan review, by an order of magnitude: 17 rounds to `approved` against 3 for execution. The plan
   was a **spec revision** (Phase 9 locked `overlay = BrowserWindow, grab = desktopCapturer`), so
   most rounds were not about the picker at all — they were about the plan's own gate scripts
   accepting text that merely looked like evidence. Rounds 4 and 9 in particular added negative
   oracles for comment-only E2E markers, a `dist` that echoes the build script's name, and a
   handler that delegates to the wrong controller method. Execution then ran fast *because* those
   gates existed.

2. **What instructions were ambiguous?**
   `plan_to_exec_gate`. `.agent/context/harness.local.md` sets `reviewer-auto`, but this session ran
   on Claude Code, whose profile is `human`. GUARDRAILS SIGN 1 resolves it — the flag is a property
   of the driving harness, not the project — so the reviewer's `approved` was not self-authorizing
   and I waited for "begin the execution here". Worth stating in `harness.local.md` directly.

3. **What instructions were unnecessary?**
   Nothing was inert, but the Efficiency Metrics table below asks for numbers this harness cannot
   produce (see `slim_candidate`).

4. **What was missing?**
   A rule that real-Electron evidence must be produced against a **rebuilt** bundle. `arm-run.ps1`
   proved report freshness; `global-setup.ts` proved only that `out/main/index.js` exists. That gap
   is exactly what exec review round 2 found, and nothing in the plan's 31 rows would have caught
   it. The plan's own philosophy — "text that only *looks* like evidence" — had a blind spot for
   *binaries* that only look like evidence.

5. **What did you do that wasn't in the prompt?**
   Hardened `global-setup.ts` to fail closed on a stale bundle and proved it with a negative oracle.
   The reviewer's accepted fix was narrower ("run `npm run build` before arming"); running the build
   once fixes the receipt, the guard fixes the class. Also added a self-evidencing freshness receipt
   (`src < build < capture start`) so the ordering does not have to be reconstructed from mtimes.

### Quality Signal Log

6. **Which tests caught real bugs?**
   The round-2 unit tests, all six of which were written red against shipped code. The decisive one
   drove the *production* path — real `runInteractiveTick` over real `captureRegionFromGui`, with a
   window whose `isDestroyed()` answers `false` and whose `send()` throws — and reproduced review
   finding 1 verbatim: `expected "spy" to not be called at all, but actually been called 1 times`,
   i.e. a PNG published to the inbox and its request cancelled anyway.

7. **Which tests were trivially obvious?**
   The `RectMath` normalize/clamp cases. Correct and cheap, but they never had a plausible failure
   mode; the picker's real risk lived in the Electron↔helper lifecycle, not in rectangle arithmetic.

8. **Did pyright/ruff catch anything meaningful?**
   No Python changed. `tsc --noEmit` did the equivalent work: making `Notice.path` optional produced
   38 TS2345 errors across two test files, which is precisely the signal you want — every consumer
   of a widened type surfaced at once, and each was a fixture *declaration*, not an assertion.

### Workflow Signal Log

9. **Was the FIC useful as written?**
   Yes. 29 live ACs plus 4 explicitly retired ones, each labeled `Spec` / `Local Canon` /
   `Research-backed` / `Human-approved`. AC-40.33 (a published capture is never cancelled) is what
   made review finding 1 a *contract violation* rather than a matter of taste, and the retired-AC
   set is what let the reviewer verify the overlay deletion was sanctioned scope, not silent
   narrowing.

10. **Was the handoff template right-sized?**
    Yes, and the rolling-file convention earned its keep: three review rounds and three correction
    passes in two files rather than six. The Round-2/Round-3 correction sections carry the red
    receipt quoted verbatim, which is what let round 3 be a 40-line recheck.

11. **How many tool calls did this session take?**
    Not instrumented — see `slim_candidate`. Order of magnitude: several hundred across 17 plan
    rounds, MEU-40 TDD, and 3 execution rounds.

12. **Which rows were delegated, to which subagent (harness + model), and did any delegated result need rework?**
    None. `fresh_worker: none` for this plan, so every row ran in the coordinator context.
    Independent review only: Codex GPT-5.6-sol, `FullAccess`, `model_reasoning_effort=high`, three
    dispatches under `dispatch_id: exec-review-p9-native-picker`.

---

## Pattern Extraction

### Patterns to KEEP
1. Writing the correction tests red against shipped code and quoting the failure output in the
   handoff. Round 3 could then verify a claim instead of re-deriving it.
2. Refocusing the reviewer on substance ("no findings about handoff formatting, template ordering,
   naming conventions") in the dispatch prompt. All four execution findings across three rounds
   were behavioral; none were paperwork.
3. Telling the reviewer explicitly what it had already accepted. Round 3 stayed scoped to R2-1
   instead of re-reviewing 29 ACs.

### Patterns to DROP
1. Inheriting E2E evidence across a source change. "The report is fresh" is not "the application is
   fresh", and `arm-run.ps1` only ever proved the former.
2. Reaching for `npx prettier --write` in a repo with no prettier dependency and no config. Defaults
   rewrote three files with semicolons and double quotes; recovery cost more than the formatting was
   worth, and there is no git to `checkout --`.

### Patterns to ADD
1. Any gate that consumes a **build artifact** must assert the artifact is newer than its sources,
   not merely that it exists.
2. When a fix lands at a caller because changing the callee would alter its semantics, say so in the
   handoff at `file:line`. Round 2 accepted the caller-side fix immediately because the reason
   `finalizeCapturedPng` was left alone was written down.

### Calibration Adjustment
- Estimated time: one plan review pass + one TDD session + one execution review pass
- Actual time: 17 plan rounds, one TDD session, 3 execution rounds
- Adjusted estimate for similar MEUs: a **spec revision** is not a normal MEU. Budget the plan
  review at 3–5× a normal plan when the plan must first delete a locked design, and expect most
  rounds to be about the gate scripts rather than the feature.

---

## Next Session Design Rules

```
RULE-1: Real-Electron (or any packaged-artifact) evidence is invalid unless the artifact was rebuilt after the last source change; the harness must fail closed, not the operator remember.
SOURCE: exec review round 2, R2-1
EXAMPLE: fresh Playwright report at 04:14 launching a bundle built 23:19 the night before → global-setup.ts now walks ui/src and throws
```

```
RULE-2: A published side effect is a committed state. Everything after the commit point is announcement and bookkeeping, and none of it may reject into the caller's failure path.
SOURCE: exec review round 1, finding 1
EXAMPLE: notifyInboxChanged threw after linkSync → runInteractiveTick called /cancel on a request whose PNG was on disk
```

```
RULE-3: A failure the user cannot distinguish from their own cancel is a silent failure. Carry the subprocess's own diagnosis into both the log and the notice.
SOURCE: exec review round 1, finding 2
EXAMPLE: a missing/denied helper read as "F2 does nothing" → withStderrTail folds a bounded stderr tail into every blocked reason
```

---

## Next Day Outline

1. Phase 9 capture is complete: MEU-34–40 all `approved`. `HUB_NEXT_AFTER` governs what follows.
2. No scaffold changes pending; the native picker ships as a `dotnet publish` sibling under
   `native/region-picker/publish` and is wired into `dist:prep`.
3. Bake in RULE-1 wherever a gate consumes a build artifact — the packaging gates
   (`assert-packaging-clean.ps1`) are the next candidates.
4. Codex validation scope: closed for MEU-40 at execution round 3.
5. Time estimate: n/a — awaiting Mat's direction on the next phase.

---

## Efficiency Metrics

| Metric | Value |
|--------|-------|
| Total tool calls | not instrumented; several hundred across 17 plan + 3 exec rounds |
| Time to first green test | MEU-40 red oracle and green in the same TDD pass |
| Tests added | 6 round-2 unit cases (329 vitest total, 40 files, was 323); 4 real-Electron capture cases; 59 Playwright total |
| Codex findings | plan 17 rounds; exec r1 3 (2 Medium, 1 Low), r2 1 High, r3 0 |
| Handoff Score (X/7) | 7/7 after r3 (markers, AC totality, evidence bundle, dispatch provenance) |
| Rule Adherence (%) | ~90 — P0 redirect, no self-review, no auto-commit all held; the misses were inherited E2E evidence and the prettier run |
| Prompt→commit time | no commit (human gate) |

### Rules Sampled for Adherence Check

| Rule | Source | Followed? |
|------|--------|-----------|
| Redirect every shell stream to `C:/Temp/av-kit/` | AGENTS.md §P0 | Yes |
| Never self-review; dispatch the independent reviewer | AGENTS.md §Execution Contract | Yes — 3 Codex dispatches, verdict never self-authored |
| Never auto-commit | AGENTS.md §Commits | Yes — draft only |
| Anti-premature-stop: H1 → review → H2 in one pass | AGENTS.md §Execution Contract | Yes — no pause at the phase dividers or between review rounds |
| Tests first; never modify or neutralize | AGENTS.md §TDD | Yes — 6 cases written red; only fixture *declarations* widened in green |
| Plan→execution needs a trusted signal **and** the harness gate | GUARDRAILS SIGN 1/3 | Yes — reviewer `approved` + `USER_EXPLICIT` "begin the execution here" |

---

## Instruction Coverage

```yaml
schema: v1
session:
  id: "464ffa3c-3860-4e68-9308-45db8e4e5dc0"
  task_class: tdd
  outcome: success
sections:
  - id: execution_contract
    cited: true
    influence: 3
  - id: testing_tdd_protocol
    cited: true
    influence: 3
  - id: priority_0_system_constraints_non_negotiable
    cited: true
    influence: 3
  - id: dual_agent_workflow
    cited: true
    influence: 3
  - id: planning_contract
    cited: true
    influence: 3
  - id: commits
    cited: true
    influence: 2
  - id: pre_handoff_self_review_mandatory
    cited: true
    influence: 2
  - id: windows_shell_powershell
    cited: true
    influence: 2
  - id: code_quality
    cited: true
    influence: 2
  - id: session_discipline
    cited: true
    influence: 2
  - id: testing_requirements
    cited: true
    influence: 2
  - id: communication_policy
    cited: true
    influence: 2
  - id: instruction_coverage_reflection
    cited: true
    influence: 2
  - id: artifact_naming_convention
    cited: true
    influence: 1
  - id: project_context
    cited: true
    influence: 1
  - id: rtk_token_optimized_commands
    cited: true
    influence: 1
  - id: architecture
    cited: false
    influence: 0
  - id: mcp_servers
    cited: false
    influence: 0
loaded:
  workflows:
    - create-plan
    - execution-critical-review
    - execution-corrections
  roles:
    - orchestrator
    - coder
    - tester
  skills:
    - terminal-preflight
    - cli-dispatch
    - completion-preflight
    - quality-gate
  refs:
    - AGENTS.md
    - GUARDRAILS.md
    - docs/execution/plans/2026-08-27-p9-capture-native-picker/implementation-plan.md
    - docs/execution/plans/2026-08-27-p9-capture-native-picker/task.md
    - docs/build-plan/09-screenshot-capture.md
    - .agent/schemas/reflection.v1.yaml
review_churn:
  rounds_to_approval:
    plan: 17
    execution: 3
  findings_per_round:
    - { round: 1, critical: 0, high: 0, medium: 2, low: 1 }
    - { round: 2, critical: 0, high: 1, medium: 0, low: 0 }
    - { round: 3, critical: 0, high: 0, medium: 0, low: 0 }
  churned_findings: 0
  finding_categories:
    contract_drift: 1
    boundary_validation: 1
    weak_test: 1
    other: 1
  verdicts:
    changes_required: 18
    approved: 2
meu_work_classes:
  - correctness
decisive_rules:
  - "P0:tests-first-red-before-green"
  - "P1:independent-review-never-self-authored"
  - "P1:plan-to-exec-gate-human-on-claude-code"
  - "P1:anti-premature-stop-H1-review-H2-one-pass"
  - "P0:never-auto-commit"
conflicts:
  - "harness.local.md sets plan_to_exec_gate: reviewer-auto, but this session ran on Claude Code (human-gated). SIGN 1 resolves it toward the driving harness; the local file reads as if it were project-wide."
  - "Code Quality implies consistent formatting, but the repo has no prettier dependency or config — running prettier with defaults damaged three files, and with no git there is no cheap recovery."
  - "P0 mandates a redirect-to-file shell pattern; the Bash tool mangles backslashes inside quoted heredocs, so several patch scripts needed a chr(92) workaround to express the same command."
slim_candidate:
  - "Efficiency Metrics table (tool calls / time-to-first-green / prompt-to-commit) — none of these are instrumented in this harness, so every reflection fills them with prose estimates that no one can aggregate. Either instrument them or delete the rows."
  - "Next Day Outline — duplicates current-focus.md, which is the file actually read at session start."
overthinking_observed: false
note: "Plan review took 17 rounds because the plan was a spec revision; execution took 3 because those gates then held."
```

> **De-flatter note:** the two `influence: 0` entries above are honest — `architecture` and
> `mcp_servers` were never consulted this session. The capture path's structure was already fixed by
> the plan, and no MCP tool was involved in any row.
