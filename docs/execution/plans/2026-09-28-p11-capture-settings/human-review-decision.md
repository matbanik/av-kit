# Human review route decision

## Direct user authorization

Source: `USER_EXPLICIT`, trusted user chat channel, 2026-09-28.

Exact user message:

> create plan for Session 26, p11-capture-settings - as per session grouping files
> For reviewer instead of doing codex cli dispatch since we are in web Claude code platform use subagent to fable 5.1 high model

## Scope of this authorization

This message authorizes independent review of `2026-09-28-p11-capture-settings` by a separate-context subagent running Fable 5.1, instead of the PROFILE B1 Codex CLI rung.

| Field | Value |
|---|---|
| Plan review target | `docs/execution/plans/2026-09-28-p11-capture-settings/implementation-plan.md` and `task.md` |
| Plan review file | `.agent/context/handoffs/2026-09-28-p11-capture-settings-plan-critical-review.md` (cap 3 rounds) |
| Execution review file | `.agent/context/handoffs/2026-09-28-p11-capture-settings-implementation-critical-review.md` (cap 6 rounds). The user said "for reviewer" without limiting it to the plan, so H1-6 uses the same route unless the user says otherwise. |
| Driver / author | Claude Code (web), model `claude-opus-5-5`. Vendor: Anthropic. |
| Reviewer | Agent-tool subagent, `model: fable` (Fable 5.1, `claude-fable-5-1`). Vendor: Anthropic. |
| Requested reasoning effort | `high`. **Limit:** the Agent tool exposes no per-call effort parameter, so "high" is stated in the dispatch prompt but not enforced by the harness. |

## Deviation disclosure

- This is a **same-vendor** review. It departs from PROFILE B1/B4 and AGENTS §Dual-Agent Workflow ("vendor-distinct"). The user's explicit direction governs under the host hierarchy (CLAUDE.md), and the conflict is surfaced here rather than resolved silently.
- **Independence kept:** the reviewer runs in a separate subagent context, did not author the plan, and writes the verdict itself. The author only dispatches, reads back and corrects. It never edits findings or writes `approved`.
- This scoped exception does not change the shared model registry, the project overlay or the standing routing policy.
- A reviewer `approved` authorizes nothing further. Claude Code resolves to `plan_to_exec_gate: human`, so execution still needs a direct user message. Commit, push, merge and release remain separate human decisions.
