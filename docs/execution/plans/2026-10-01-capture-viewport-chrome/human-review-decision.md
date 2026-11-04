# Human review route decision

## Direct user authorization

Source: `USER_EXPLICIT`, trusted user chat channel (Claude Code web session), 2026-10-01.

The user asked: "/create-plan for Session 29 (Capture viewport/chrome)". The Codex CLI is not installed in this container (`which codex` finds nothing). So before drafting, the planner asked: "Codex CLI isn't installed in this container. Who should do the independent plan review (and later the execution review) for Session 29 capture-viewport-chrome?" The user chose:

> Fable 5.1 subagent (Recommended)

The option text shown to the user:

> Same route you authorized for Sessions 25–27: a separate-context Agent subagent on Fable 5.1, 'high' effort stated in the prompt. It's the same vendor, which I'll disclose in human-review-decision.md. Covers plan review (3-round cap) and execution review (6-round cap).

## Scope of this authorization

| Field | Value |
|---|---|
| Plan review target | `docs/execution/plans/2026-10-01-capture-viewport-chrome/implementation-plan.md` and `task.md`, plus the plan-local files they invoke |
| Plan review file | `.agent/context/handoffs/2026-10-01-capture-viewport-chrome-plan-critical-review.md`, cap 3 rounds (PROFILE B5) |
| Execution review file | `.agent/context/handoffs/2026-10-01-capture-viewport-chrome-implementation-critical-review.md`, cap 6 rounds (PROFILE B5). The option text covers both reviews. |
| Driver / author | Claude Code (web). Vendor: Anthropic. |
| Reviewer | Agent-tool subagent, `model: fable` (Fable 5.1, `claude-fable-5-1`). Vendor: Anthropic. |
| Requested reasoning effort | `high`. **Limit:** the Agent tool has no per-call effort parameter, so "high" is stated in the dispatch prompt but not enforced by the harness. |

## Deviation disclosure

- **Same-vendor review.** This review departs from PROFILE B1/B4 and AGENTS §Dual-Agent Workflow, which call for a "vendor-distinct" reviewer. The user's explicit choice governs under the host hierarchy (CLAUDE.md). The conflict is recorded here rather than resolved silently.
- **How independence is kept.**
  - The reviewer runs in a separate subagent context and did not write the plan.
  - The reviewer writes the verdict file itself.
  - The author only dispatches, reads back and corrects. The author never edits findings and never writes `approved`.
- **No standing change.** This scoped exception does not change the shared model registry, the project overlay or the standing routing policy.
- **What approval does not authorize.** A reviewer `approved` authorizes nothing further. Claude Code resolves to `plan_to_exec_gate: human` (`.agent/context/harness.local.md` §Claude Code), so execution still needs a direct user message. Commit, push, merge and release remain separate human decisions.
