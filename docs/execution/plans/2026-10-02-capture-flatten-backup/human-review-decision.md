# Human review route decision

## Direct user authorization

Source: `USER_EXPLICIT`, trusted user chat channel (Claude Code web session), 2026-10-02.

The user asked: "/create-plan Session 30 per session grouping". The Codex CLI is not installed in this container (`which codex` finds nothing). So before drafting, the planner asked: "Codex CLI isn't installed in this container. Who should do the independent plan review (and later the execution review) for Session 30 capture-flatten-backup?" The user chose:

> Fable 5.1 subagent (Recommended)

The option text shown to the user:

> Same route you authorized for Sessions 25–29: a separate-context Agent subagent on Fable 5.1, 'high' effort stated in the prompt. It's the same vendor, which I'll disclose in human-review-decision.md. Covers plan review (3-round cap) and execution review (6-round cap).

## Scope of this authorization

| Field | Value |
|---|---|
| Plan review target | `docs/execution/plans/2026-10-02-capture-flatten-backup/implementation-plan.md` and `task.md`, plus the plan-local files they invoke |
| Plan review file | `.agent/context/handoffs/2026-10-02-capture-flatten-backup-plan-critical-review.md`, cap 3 rounds (PROFILE B5) |
| Execution review file | `.agent/context/handoffs/2026-10-02-capture-flatten-backup-implementation-critical-review.md`, cap 6 rounds (PROFILE B5). The option text covers both reviews. |
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

## Route change for the execution review from Round 2 (2026-10-10)

Source: `USER_EXPLICIT`, trusted user chat channel (Claude Code web session), 2026-10-10. The user wrote:

> lets change reviewer from fable to opus 5.5 xhigh

| Field | Value from Round 2 |
|---|---|
| Reviewer | Agent-tool subagent, `model: opus` (Opus 5.5, `claude-opus-5-5`). Vendor: Anthropic. The review file's `agent` value is `claude-opus-5-5-subagent`. |
| Requested reasoning effort | `xhigh`. **Limit:** as before, the Agent tool has no per-call effort parameter, so "xhigh" is stated in the dispatch prompt but not enforced by the harness. |
| Rounds | The execution review continues in the same rolling file and the same 6-round cap. Round 1 (Fable 5.1, `changes_required`, `4d58a87`) stays on record, and the next round is Round 2. |
| Plan review | Unchanged: approved in Round 3 by Fable 5.1. |

**Deviation disclosure (stronger than for Fable):**
- The author is also Claude Code configured for Opus 5.5 (`claude-opus-5-5`). From Round 2, the reviewer is the **same model** as the author, not only the same vendor.
- Independence therefore rests only on the separate subagent context, the reviewer writing its own verdict file, and the author never editing findings or writing `approved`.
- This departs further from AGENTS.md §Independent review ("vendor-distinct from the author"). The user's explicit direction governs under the host hierarchy. The conflict is recorded here, not resolved silently, and it does not change the shared registry, the project overlay or the standing routing policy.

## Route change for Round 2: Codex CLI dispatched by the local agent (2026-10-10, supersedes the Opus 5.5 change)

Source: `USER_EXPLICIT`, trusted user chat channel (Claude Code web session), 2026-10-10. The user wrote:

> ok lets do this, review will need to be dispatched by local agent to codex cli gpt-6.1-sol high model

| Field | Value from Round 2 |
|---|---|
| Reviewer | Codex CLI on Mat's Windows machine, model `gpt-6.1-sol`. Vendor: OpenAI. It is dispatched by the local agent, not by this cloud session. The review file's `agent` value is `codex-cli-gpt-6.1-sol`. |
| Requested reasoning effort | `high`, set on the Codex CLI invocation. |
| Rounds | Same rolling file and the same 6-round cap. Round 1 (Fable 5.1, `changes_required`, `4d58a87`) stays on record, and the next round is Round 2. |
| Superseded | The Opus 5.5 `xhigh` route recorded above (999c5e1) never dispatched a round. |

**Independence:**
- This route is vendor-distinct from the author (Anthropic), as AGENTS.md §Independent review requires. The earlier same-vendor deviation no longer applies from Round 2.
- The reviewer writes the verdict file itself.
- Neither the cloud author nor the local agent edits findings or writes `approved`.
