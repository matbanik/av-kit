# Human review route decision

## Direct user authorization

Source: `USER_EXPLICIT` (Claude Code web session, 2026-09-29)

Exact user message:

> run the independent review with fable 5.1 high agent which is approved by human

The message authorizes this reviewer route for this project:

- target plan: `docs/execution/plans/2026-09-29-human-decision-protocol-adoption/implementation-plan.md`
- scope: the `/execution-critical-review` loop (cap 6 rounds) of this project. The plan was
  written and implemented in one pass, so this single loop reviews both.
- dispatch mechanism: Claude Code `Agent` tool, fresh subagent context, `model: fable` (Fable 5.1)
- reasoning effort: `high`. The dispatch prompt requests it; the `Agent` tool has no effort
  parameter, so nothing enforces it mechanically. This limitation is recorded here.
- author vendor: `anthropic` (Claude Code main session)
- reviewer vendor: `anthropic` (Fable 5.1)

## Conflict surfaced

`AGENTS.md` §Dual-Agent Workflow requires the independent machine reviewer to be vendor-distinct
from the author, with PROFILE B4 (Mat) as the fallback. This route is same-vendor. Per `AGENTS.md`
§PRIORITY 0, explicit user authorization governs. The conflict is recorded here rather than
resolved silently. Precedent for the same exception:
`docs/execution/plans/2026-09-28-p11-transcript-tts/human-review-decision.md`.

## Independence preserved

- The reviewer runs in a separate subagent context. It did not author the plan or the
  implementation, and it receives only the review protocol, the target paths and the handoff.
- The author never writes, edits or paraphrases the verdict. The reviewer writes the rolling
  review file directly. The author reads it back and checks target, mode and round before
  trusting it (`GUARDRAILS.md` SIGN 3).
- The standing registry, project overlay and routing policy are unchanged. This exception
  covers this project only.

This authorization selects a reviewer. It is not a verdict, and it does not authorize merge,
release or deploy.
