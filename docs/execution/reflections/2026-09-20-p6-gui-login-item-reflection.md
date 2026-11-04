---
date: "2026-09-20"
project: "p6-gui-login-item"
meus: ["MEU-61"]
plan_source: "docs/execution/plans/2026-09-20-p6-gui-login-item/implementation-plan.md"
template_version: "2.0"
---

# 2026-09-20 Meta-Reflection

> **Date**: 2026-09-20
> **MEU(s) Completed**: MEU-61 (`gui-login-item`) — Phase 6 residual per-user Electron login item
> **Plan Source**: `docs/execution/plans/2026-09-20-p6-gui-login-item/implementation-plan.md`

---

## Execution Trace

### Friction Log

1. **What took longer than expected?**
   Execution review took three rounds. Round 1 High: darwin classified supported while minimized used Windows-only `args`. Round 1 correction used `openAsHidden` / `wasOpenedAsHidden`. Round 2 High: those fields are deprecated and unavailable on macOS 13+ in the installed Electron 42.9.3 contract. The durable fix was narrowing the spec (Start minimized is Windows-only) rather than another fake OS field.

2. **What instructions were ambiguous?**
   Plan AC-61.4–.6 originally encoded a Windows argv model for all supported platforms. Spec 06-gui.md also listed `openAsHidden` both as the macOS minimized store and as “Out of this card.” Electron types were the tie-breaker.

3. **What instructions were unnecessary?**
   Treating `FORBIDDEN_ELECTRON` (`openAsHidden`) as a global source ban. The named scan is IPC_FILE-only; `wasOpenedAsHidden` contains that substring, which forced `index.ts` to call a helper instead of naming the field.

4. **What was missing?**
   A first-pass read of `ui/node_modules/electron/electron.d.ts` LoginItemSettings before promising darwin minimized. Issue 37228 / PR 37244 already document SMAppService dropping hidden login.

5. **What did you do that wasn't in the prompt?**
   Added `startMinimizedSupported` on the supported `LoginItemState` so Settings can hide Start minimized on darwin without a second IPC channel. Extracted `revealMainWindow` so AC-61.15 can forbid `window.show(` in `index.ts`.

### Quality Signal Log

6. **Which tests caught real bugs?**
   Darwin AC-61.5 after r2 (fake `openAsHidden: true` must still read `minimized: false`). AC-61.6 darwin write `not.toHaveProperty('openAsHidden')`. AC-61.15 `revealMainWindow` spies plus `index.ts` must not match `window.show(` — reviewer-r3 mutation killed both unguarded-show and dropped-third-arg.

7. **Which tests were trivially obvious?**
   HELP_STARTUP_TOKENS greps. OpenAPI `--check` with no API change. IPC channel length 19 once the census existed.

8. **Did pyright/ruff catch anything meaningful?**
   `index.ts` needed explicit `getLoginItemSettings` / `setLoginItemSettings` parameter types (implicit any). ESLint stayed clean. Defects were Electron platform contracts, not types.

### Workflow Signal Log

9. **Was the FIC useful as written?**
   Strong on OS-as-SoT, extra-forbid IPC, NSIS two executable `DeleteRegValue HKCU` lines, unpackaged E2E absence. Weak on macOS minimized until Electron 42 types were treated as Spec.

10. **Was the handoff template right-sized?**
   C4 AC table plus Corrections Applied were what r2/r3 reopened. Stale “2/2 resolved” after r1 was correctly rejected.

11. **How many tool calls did this session take?**
   High hundreds across discovery, `/create-plan`, plan r2, TDD, exec r1–r3, and H2. Not harness-instrumented.

12. **Which rows were delegated, to which subagent (harness + model), and did any delegated result need rework?**
    None to av-kit-builder. Codex `gpt-5.6-sol` high: plan review (r1 `changes_required` PCR-1–4 / r2 `approved`) and execution review (r1 and r2 `changes_required` / r3 `approved`). Independent mutation oracles in r2/r3; implementer applied corrections.

---

## Pattern Extraction

### Patterns to KEEP
1. Independent Codex exec review with in-memory mutation of `index.ts` (unguarded `show()`, dropped hide arg) instead of trusting token presence.
2. Platform-faithful fakes: a darwin getter that ignores `args` must not reuse the Windows Run-key model.
3. When Electron types mark a field unavailable on the current OS generation, narrow the UI promise in spec + ACs rather than persisting a lying checkbox.

### Patterns to DROP
1. Advertising Start minimized on every `classifyLoginItemSupport === supported` platform.
2. Implementing a “fix” with a field the installed `electron.d.ts` already `@deprecated` / “does not work on macOS 13+”.

### Patterns to ADD
1. Login-item / autostart MEUs: read installed Electron LoginItemSettings types before writing darwin ACs.
2. Post-load window reveal: one helper owns `show()`; the boot file must not contain `window.show(`.

### Calibration Adjustment
- Estimated: one Settings checkbox MEU plus Wave 4 absence E2E
- Actual: Windows path landed first pass; macOS contract needed two correction rounds (argv lie, then openAsHidden unavailable)
- Adjusted: budget an explicit per-platform minimized AC whenever Electron documents Windows-only `path`/`args`

---

## Next Session Design Rules

```
RULE-1: Packaged darwin login items persist openAtLogin only; Start minimized is Windows argv. Do not use openAsHidden as a Settings store on Electron 42 / macOS 13+.
SOURCE: exec r2 Finding 1; electron.d.ts LoginItemSettings; issue 37228
EXAMPLE: before → darwin write openAsHidden; after → startMinimizedSupported: false and hide the checkbox
```

```
RULE-2: index.ts must not call window.show(); revealMainWindow(window, argv, hideFromLoginLaunch) is the only post-load show path.
SOURCE: exec r1/r2 Finding 2; reviewer-r3-index-mutation.txt
EXAMPLE: before → if (shouldShowWindowAfterLoad(...)) { window.show() }; after → revealMainWindow(...)
```

```
RULE-3: Hub Next stays Phase 11 MEU-50. Concurrent MEU-60 Capture dirty tests do not belong in a MEU-61 closeout.
SOURCE: HUB_NEXT_AFTER; exec r3 out-of-contract note
EXAMPLE: before → full ui vitest mixed with AC-60.*; after → focused MEU-61 43 + named AC-61.17
```

---

## Next Day Outline

1. Target MEU-50 (`p11-layout-canon`) — unique hub Next; do not reopen MEU-61 types
2. Do not mix MEU-60 Capture edit dirty tests into a MEU-61 full-suite gate
3. Bake in per-platform Electron login-item field tables for any future autostart work
4. Codex validation: layout contract; login-item focused 43 stay green
5. Human commit of MEU-61 (and separately MEU-60) when asked
6. Packaged VM HKCU Run proof remains Phase 7 clean-machine `[B]`

---

## Efficiency Metrics

| Metric | Value |
|--------|-------|
| Total tool calls | not instrumented (hundreds) |
| Time to first green test | UI Red oracle 21 then Green; darwin contract corrected after exec r1/r2 |
| Tests added | AC-61.1–61.22 plus darwin/revealMainWindow regressions; focused 43 |
| Codex findings | plan r2 0; exec r1 1 High + 1 Medium; exec r2 same two still open; exec r3 0 |
| Handoff Score (X/7) | 6/7 (r1/r2 claim/state drift on macOS minimized, corrected at r3) |
| Rule Adherence (%) | high on TDD/self-review/P0/no-commit; miss on reading Electron types before darwin Green |
| Prompt→commit time | no commit (human gate) |

### Rules Sampled for Adherence Check

| Rule | Source | Followed? |
|------|--------|-----------|
| Tests first, no skip/only/todo | AGENTS.md TDD / G36 | Yes |
| Independent review, no self-verdict | AGENTS.md Execution Contract | Yes |
| Never auto-commit | AGENTS.md Human Approval Gate | Yes |
| Windows redirect-to-file + RTK | AGENTS.md P0 | Yes |
| Electron 42 macOS 13+ openAsHidden unavailable | installed d.ts / exec r2 | After r2 only |

---

## Instruction Coverage

```yaml
schema: v1
session:
  id: "64d28ec9-61b4-4f5f-a398-3342c15cdbf9"
  task_class: tdd
  outcome: success
sections:
  - id: priority_0_system_constraints_non_negotiable
    cited: true
    influence: 3
  - id: execution_contract
    cited: true
    influence: 3
  - id: testing_tdd_protocol
    cited: true
    influence: 3
  - id: planning_contract
    cited: true
    influence: 3
  - id: dual_agent_workflow
    cited: true
    influence: 3
  - id: session_discipline
    cited: true
    influence: 2
  - id: pre_handoff_self_review_mandatory
    cited: true
    influence: 2
  - id: windows_shell_powershell
    cited: true
    influence: 2
  - id: artifact_naming_convention
    cited: true
    influence: 2
  - id: instruction_coverage_reflection
    cited: true
    influence: 2
  - id: rtk_token_optimized_commands
    cited: true
    influence: 2
  - id: validation_pipeline
    cited: true
    influence: 1
  - id: commits
    cited: true
    influence: 2
  - id: code_quality
    cited: false
    influence: 1
  - id: architecture
    cited: false
    influence: 0
loaded:
  workflows: [create_plan, execution_critical_review]
  roles: [orchestrator, coder, tester]
  skills: [cli_dispatch, completion_preflight, terminal_preflight]
  refs:
    - docs/build-plan/06-gui.md
    - docs/build-plan/07-distribution.md
    - ui/node_modules/electron/electron.d.ts
    - .agent/context/harness.local.md
decisive_rules:
  - "P0:independent-review-no-self-verdict"
  - "P1:tests-first-implementation-after"
  - "P0:never-auto-commit"
  - "P1:never-modify-or-neutralize-tests"
  - "P0:windows-redirect-every-stream"
conflicts:
  - "Plan/spec briefly promised darwin minimized via openAsHidden while Electron 42 types mark that field unavailable on macOS 13+; types + issue 37228 won and the spec was narrowed."
  - "create-plan H1→review→H2 continuous pass vs any urge to stop after dispatch; Execution Contract DONE checklist won."
note: "Graphify/Headroom stayed not_applicable (glob 0). Hub Next remains MEU-50."
slim_candidate:
  - "FORBIDDEN_ELECTRON substring that also matches wasOpenedAsHidden"
  - dual_agent_workflow
overthinking_observed: true
review_churn:
  rounds_to_approval: { plan: 2, execution: 3 }
  findings_per_round:
    - { round: 1, critical: 0, high: 1, medium: 1, low: 0 }
    - { round: 2, critical: 0, high: 1, medium: 1, low: 0 }
    - { round: 3, critical: 0, high: 0, medium: 0, low: 0 }
  churned_findings: 2
  finding_categories: { contract_drift: 1, weak_test: 1 }
  verdicts: { changes_required: 2, approved: 1 }
meu_work_classes: [correctness]
```
