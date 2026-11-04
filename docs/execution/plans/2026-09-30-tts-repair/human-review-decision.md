# Human review route decision

## Direct user authorization

Source: `USER_EXPLICIT`, trusted user chat channel (Claude Code web session), 2026-09-30.

The user asked: "create-plan tts-repair for Session 27". The Codex CLI is not installed in this container (`which codex` finds nothing). So the planner asked, before drafting, "Who should do the independent plan review (and later the execution review) for Session 27 tts-repair?" The user chose:

> Fable 5.1 subagent (Recommended)

The option text shown to the user:

> Same route you authorized for Sessions 25 and 26: a separate-context Agent subagent on Fable 5.1, 'high' effort stated in the prompt. It's the same vendor, which I'll disclose in human-review-decision.md. Covers plan review (3-round cap) and execution review (6-round cap).

## Scope of this authorization

| Field | Value |
|---|---|
| Plan review target | `docs/execution/plans/2026-09-30-tts-repair/implementation-plan.md` and `task.md` (plus the plan-local scripts they invoke) |
| Plan review file | `.agent/context/handoffs/2026-09-30-tts-repair-plan-critical-review.md`, cap 3 rounds (PROFILE B5) |
| Execution review file | `.agent/context/handoffs/2026-09-30-tts-repair-implementation-critical-review.md`, cap 6 rounds (PROFILE B5). The option text covers both reviews. |
| Driver / author | Claude Code (web). Vendor: Anthropic. |
| Reviewer | Agent-tool subagent, `model: fable` (Fable 5.1, `claude-fable-5-1`). Vendor: Anthropic. |
| Requested reasoning effort | `high`. **Limit:** the Agent tool has no per-call effort parameter, so "high" is stated in the dispatch prompt but not enforced by the harness. |

## Deviation disclosure

- This is a **same-vendor** review. It departs from PROFILE B1/B4 and AGENTS §Dual-Agent Workflow ("vendor-distinct"). The user's explicit choice governs under the host hierarchy (CLAUDE.md). The conflict is recorded here, not resolved silently.
- **How independence is kept:** the reviewer runs in a separate subagent context and did not write the plan. It writes the verdict file itself. The author only dispatches, reads back and corrects. The author never edits findings and never writes `approved`.
- This scoped exception does not change the shared model registry, the project overlay or the standing routing policy.
- A reviewer `approved` authorizes nothing further. Claude Code resolves to `plan_to_exec_gate: human` (`.agent/context/harness.local.md` §Claude Code), so execution still needs a direct user message. Commit, push, merge and release remain separate human decisions.
