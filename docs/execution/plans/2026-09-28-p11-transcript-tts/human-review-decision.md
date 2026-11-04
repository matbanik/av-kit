# Human review route decision

## Direct user authorization

Source: `USER_EXPLICIT` (Claude Code web session, 2026-09-28, sent mid-turn while `/create-plan` was running)

Exact user message:

> For reviewer instead of doing codex cli dispatch since we are in web claude code platform use subagent to fable 5.1 high model

This message authorizes the reviewer route for this project:

- target plan: `docs/execution/plans/2026-09-28-p11-transcript-tts/implementation-plan.md`
- scope: the `/plan-critical-review` loop (cap 3 rounds) and, because the message names the reviewer role without restricting it to planning, the `/execution-critical-review` loop (cap 6 rounds) of this same project
- dispatch mechanism: Claude Code `Agent` tool, fresh subagent context, `model: fable` (Fable 5.1)
- reasoning effort: `high`, requested in the dispatch prompt; the `Agent` tool has no effort parameter, so this cannot be enforced mechanically and is recorded as a limitation
- author vendor: `anthropic` (Claude Code main session)
- reviewer vendor: `anthropic` (Fable 5.1)

## Conflict surfaced

`AGENTS.md` §Dual-Agent Workflow requires the independent machine reviewer to be vendor-distinct from the author, with PROFILE B4 (Mat) as the fallback. This route is same-vendor. Per `AGENTS.md` §PRIORITY 0, explicit user authorization governs; the conflict is recorded here rather than silently resolved. This matches the precedent of `docs/execution/plans/2026-09-26-p11-queue-pages/human-review-decision.md` (same-vendor Codex exception).

## Independence preserved

- The reviewer runs in a separate subagent context with no authorship of the plan or implementation, and receives only the review protocol, target paths and a corrections summary.
- The author never writes, edits, or paraphrases the verdict. The reviewer writes the rolling review file directly; the author reads it back and validates target, mode and round before trusting it (`GUARDRAILS.md` SIGN 3).
- The standing registry, project overlay, and routing policy are unchanged. This is a scoped exception for this project only.

This authorization selects a reviewer. It is not a plan or implementation verdict, and it does not authorize execution, commit, push, merge, release, or deploy. Under the Claude Code driver `plan_to_exec_gate: human`, execution still needs a separate direct user message after an `approved` plan verdict.
