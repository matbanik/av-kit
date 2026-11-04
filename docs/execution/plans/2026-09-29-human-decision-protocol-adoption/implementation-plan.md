---
project: "2026-09-29-human-decision-protocol-adoption"
date: "2026-09-29"
source: "matbanik/agentic-framework@4033418f66d2d2085f989e27bf2823d9c55332b6"
meus: []
status: "approved"
template_version: "2.1"
---

# Implementation Plan — Adopt the framework's Human Decision Protocol

## Goal

Adopt upstream commit `4033418` ("feat: add the human decision protocol and reconcile decision
logs at closeout") into av-kit. After adoption, a decision reaches Mat only after a precedent sweep
and web research, only if the obviousness test leaves it genuinely his, and only as a Decision
Brief that leads with a recommendation. Every decision is logged, and the closeout validator
reconciles the reflection's `### Decisions Log` with the plan, handoff, grouping §8 and
known-issue decision logs.

Non-product governance work (`meus: []`). No product code, product tests, BUILD_PLAN or OpenAPI
change. Hard gates stay where they are: the protocol governs what is presented at a stop, not
whether the stop exists.

## Scope (upstream file → local destination)

| Upstream (`core/…`) | Local | Merge |
|---|---|---|
| `.agent/docs/human-decision-protocol.md` | same | New file. Tokens instantiated; the precedent-sweep ADR row is adapted (D-2) |
| `.agent/docs/{artifact-naming,commands,context-tool-decision-gate,development-lifecycle,emerging-standards,issue-lifecycle-guide}.md` | same | Upstream hunks applied (offset only) |
| `.agent/docs/harness-profiles.md` | same | 3 hunks applied; the `web_search_tool` row was hand-merged under the local `context_compaction` row |
| `.agent/skills/{git-workflow,session-meta-review}/SKILL.md` | same | Upstream hunks applied |
| `.agent/skills/cli-dispatch/SKILL.md` | same | Hand-merged into the local §3 Fallback steps (D-5) |
| `.agent/skills/completion-preflight/SKILL.md` | same | Hand-merged; no restated heading count (D-7) |
| `.agent/workflows/{create-plan,delegated-plan-creation,inspiration-research,issue-triage,meu-handoff,next-project,plan-corrections,session-grouping,tdd-implementation}.md` | same | Upstream hunks applied (create-plan hunks 7 and 9 applied with fuzz 1 and were read back) |
| `.agent/workflows/execution-session.md` | same | 1 hunk applied, 2 hand-merged (local `rtk proxy uv run` command kept) |
| `AGENTS.md` | same | Folded into the existing gap-resolution rule (D-1) |
| `templates/{HANDOFF,PLAN,REFLECTION,TASK}-TEMPLATE.md` | `.agent/templates/*` plus twins `.agent/context/handoffs/TEMPLATE.md`, `docs/execution/plans/{PLAN,TASK}-TEMPLATE.md`, `docs/execution/reflections/TEMPLATE.md` | Applied; the TASK H2-2 hunk was hand-merged into the local `rtk proxy uv run` command; twins re-synced (D-6) |
| `tools/issue_triage/model.py` | same | Applied |
| `tools/validate_closeout_artifacts.py` | same | 12 hunks applied, 2 hand-merged; local fixes D-3, D-4, D-8 |
| `MANIFEST.md`, `UPDATE-CHECKLIST.md` | — | Package-only; not installed in adopters |

## Acceptance Criteria

| AC | Criterion | Source |
|---|---|---|
| AC-1 | `.agent/docs/human-decision-protocol.md` exists with no `{{…}}` tokens, and `AGENTS.md`, `commands.md` and `harness-profiles.md` route to it | Spec (upstream commit) |
| AC-2 | Every upstream hunk is present locally, either applied as-is or hand-merged, and the scope table records which | Spec |
| AC-3 | `validate_closeout_artifacts.py --selftest` reports 0 failures and 45 must-OK on the project's Python floor (3.11): the 174 upstream arms (the upstream MANIFEST count) plus the 3 local repeated-ID arms from Round 1 Finding 1, 177 in total | Spec + Local Canon (`pyproject.toml` `requires-python >=3.11`) |
| AC-4 | `lint_task_contract.py --selftest` and `review_ledger.py selftest` still pass | Local Canon |
| AC-5 | Ruff (check + format) and Pyright are clean on changed Python files | Local Canon (AGENTS §Code Quality) |
| AC-6 | `tests/tooling` has the same failure set before and after the change (no regression) | Local Canon |
| AC-7 | AGENTS.md stays within its size bound with no net rule growth | Local Canon (AGENTS §PRIORITY 0) |
| AC-8 | Twin templates are byte-identical to `.agent/templates/*` | Local Canon (`artifact-naming.md`) |

Negative cases, all in the 177-arm selftest: the validator refuses a handoff that lacks
`## Decision Log` (`handoff-decision-log-missing-refused`), refuses a reflection whose
Decisions Log leaves out a recorded decision (`decision-missing-from-reflection-refused`,
`grouping-decision-missing-refused`), and refuses a decision ID repeated within one source
(`handoff-decision-log-repeated-id-refused`, `plan-repeated-id-across-fences-refused`,
`grouping-repeated-id-refused`).

## Decision Log

The precedent sweep ran in this session with `grep -rn` over `.agent/`, `docs/execution/` and the
upstream scrub ledger (`UPDATE-CHECKLIST.md`). Local canon settled every decision below, so none
needed a web search. They are two-way doors and are recorded here rather than asked. The
execution-stage decisions (D-3, D-4, D-6, D-7, D-8) are recorded in the work handoff's
`## Decision Log`:
`.agent/context/handoffs/2026-09-29-human-decision-protocol-adoption-handoff.md`.

```yaml
decision_log:
  - id: D-1
    stage: planning
    question: "Where does AGENTS.md reference the protocol?"
    resolution: autonomous
    class: two-way
    chosen: "Extend the existing Communication Policy gap-resolution sentence; no new rule"
    source_tag: Local Canon
    precedents: ["AGENTS.md:10 — no net rule growth; each new rule merges into an existing one"]
    research: { engine: none, sources: ["unavailable — local canon settles placement; no external question"] }
    reasoning: "Upstream edits its Planning Contract FIC bullet. av-kit already consolidated that rule into Communication Policy, so extending it there adds no rule. A second copy in Planning Contract would duplicate it."
  - id: D-2
    stage: planning
    question: "What does the precedent-sweep table name as the ADR directory?"
    resolution: autonomous
    class: two-way
    chosen: "docs/build-plan/ and docs/BUILD_PLAN.md, noting av-kit has no ADR directory"
    source_tag: Local Canon
    precedents: ["UPDATE-CHECKLIST.md scrub ledger (upstream) — this row is the adopter-specific one"]
    research: { engine: none, sources: ["unavailable — repository layout question"] }
    reasoning: "No docs/adrs or docs/decisions directory exists. The build plan is where av-kit records phase-level design rationale. Pointing the sweep at a directory that does not exist would make it silently empty."
  - id: D-5
    stage: planning
    question: "Upstream's cli-dispatch rate-limit HARD STOP brief offers manual web submission or a timed retry. What does av-kit offer?"
    resolution: autonomous
    class: two-way
    chosen: "A brief choosing between Mat's target-bound review and a timed retry of the configured reviewer"
    source_tag: Local Canon
    precedents: [".agent/skills/cli-dispatch/SKILL.md §2 — no web-model substitution; manual provider submission needs a new explicit instruction", "PROFILE B3/B4 — no alternate reviewer; Mat is the fallback"]
    research: { engine: none, sources: ["unavailable — local routing policy"] }
    reasoning: "Offering web submission would contradict the local fallback policy. The brief format (recommendation first, default if unanswered) is adopted as-is."
```

No decision is human-gated. The upstream issues behind D-3 and D-8 (the 3.12-only syntax and the
Pyright shadowing) are worth fixing upstream as well. That is outside this repository.

## Independent Review

`avkit_independent_reviewer` (codex-cli) is not available in the cloud container that ran this
session: `codex`, `pwsh` and `rtk` are all absent. Per PROFILE B4 and GUARDRAILS SIGN 1, the
fallback is Mat. Self-review is not a substitute, so this plan stays
`pending_independent_review`. Evidence is in `task.md` §Evidence.
