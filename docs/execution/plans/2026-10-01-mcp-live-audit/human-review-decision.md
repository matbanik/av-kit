# Human review route decision

## Direct user authorization

Source: `USER_EXPLICIT`, Claude Code web session, 2026-10-01. The answer was given in the planning turn of `/create-plan` for Session 28.

Question asked:

> Codex CLI isn't available in this cloud container. Who should do the independent plan and execution reviews for Session 28?

Option text presented:

> **Fable 5.1 subagent (Recommended)**: Same route you authorized for Sessions 25 and 26: a separate-context Agent subagent running Fable 5.1 writes the verdict. It's the same vendor as the author, so I'd record that deviation from PROFILE B1/B4 in human-review-decision.md.

The alternative offered was "Mat reviews by hand" (the PROFILE B4 fallback).

User answer, verbatim:

> Fable 5.1 subagent (Recommended)

## Scope of this authorization

| Field | Value |
|---|---|
| Plan review target | `docs/execution/plans/2026-10-01-mcp-live-audit/implementation-plan.md` and `task.md` (with `validate-task.sh`, `validate-task.ps1`, `human-gate-decision.md`) |
| Plan review file | `.agent/context/handoffs/2026-10-01-mcp-live-audit-plan-critical-review.md` (rolling, cap 3 rounds) |
| Execution review file | `.agent/context/handoffs/2026-10-01-mcp-live-audit-implementation-critical-review.md` (rolling, cap 6 rounds). The question named both plan and execution reviews. |
| Driver / author | Claude Code (web). Vendor: Anthropic. |
| Reviewer | Agent-tool subagent, `model: fable` (Fable 5.1). Vendor: Anthropic. |
| Requested reasoning effort | `high`, stated in the dispatch prompt. **Limit:** the Agent tool has no per-call effort parameter, so this is not enforced by the harness. |

## Deviation disclosure

- This is a **same-vendor** review. It departs from PROFILE B1/B4 and AGENTS §Dual-Agent Workflow ("vendor-distinct"). The user's explicit direction governs under the host hierarchy (CLAUDE.md); the conflict is surfaced here, not resolved silently.
- **Independence kept:** the reviewer runs in a separate subagent context, did not author the plan, and writes the verdict file itself. The author only dispatches, reads back, and corrects through `/plan-corrections` or `/execution-corrections`. It never edits findings and never writes `approved`.
- This scoped exception does not change the shared model registry, the project overlay or the standing routing policy.
- A reviewer `approved` authorizes nothing further. Claude Code resolves to `plan_to_exec_gate: human`, so execution needs a direct user message ([human-gate-decision.md](human-gate-decision.md)). Commit, push, merge and release remain separate human decisions.
