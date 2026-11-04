# Human review route decision

## Direct user authorization

Source: `USER_EXPLICIT`, trusted user chat channel (Claude Code web session), 2026-10-10.

The user asked: "/create-plan for Session 31 as per session grouping". The Codex CLI is not installed in this container (`which codex` finds nothing). So before drafting, the planner asked: "Codex CLI isn't installed in this container. Who should do the independent plan review (and later the execution review) for Session 31 gui-polish-residuals?" The options offered were a Fable 5.1 subagent (the Sessions 25–29 route) or Mat reviewing by hand. The user answered with their own text instead:

> create prompt for local subaget to cli dispatch the review to codex gpt-6.1-sol high model

Read plainly: an agent on Mat's Windows machine (`P:/av-kit`), where Codex is installed, dispatches the review to the Codex CLI on model `gpt-6.1-sol` at `high` reasoning effort. This plan ships the prompt and the exact procedure ([local-requests.md](local-requests.md) §PLAN_REVIEW, [review-prompt-plan.md](review-prompt-plan.md)).

## Scope of this authorization

| Field | Value |
|---|---|
| Plan review target | `docs/execution/plans/2026-10-10-gui-polish-residuals/implementation-plan.md` and `task.md`, plus the plan-local files they invoke |
| Plan review file | `.agent/context/handoffs/2026-10-10-gui-polish-residuals-plan-critical-review.md`, cap 3 rounds (PROFILE B5) |
| Execution review file | `.agent/context/handoffs/2026-10-10-gui-polish-residuals-implementation-critical-review.md`, cap 6 rounds (PROFILE B5). The question asked covered both reviews, and the answer named no exception. |
| Driver / author | Claude Code (web). Vendor: Anthropic. |
| Dispatcher | A local agent on Mat's machine. It runs `tools/Invoke-CodexDispatch.ps1`, then copies the reviewer's report to the canonical file **verbatim**, records the ledger round, and commits and pushes only the review file. It never edits findings and never writes a verdict (plan-critical-review §Write Scope). |
| Reviewer | Codex CLI, class `avkit_independent_reviewer`. Vendor: OpenAI. |
| Model | `gpt-6.1-sol`, passed as `-Model gpt-6.1-sol`. |
| Requested reasoning effort | `high` (`-ReasoningEffort high`). That is the class's `effort_default`, and the dispatch skill's tier for contract surfaces (`cli-dispatch/SKILL.md` §Reviewer Effort Policy). |
| Ledger | Loops `s31-plan-2026-10-10-gui-polish-residuals` (mode `plan`) and `s31-exec-2026-10-10-gui-polish-residuals` (mode `execution`), under `C:/Temp/av-kit/review-ledger/`. |

## Deviation disclosure

- **Model pin.** The project overlay binds `avkit_independent_reviewer` on `codex-cli` to `gpt-5.6-sol` (`.agent/model-registry.local.yaml:41-44`). The user named `gpt-6.1-sol`, so the dispatch passes `-Model gpt-6.1-sol` explicitly. The wrapper supports that override (`tools/Invoke-CodexDispatch.ps1:14-19`) and passes it to `Resolve-AgentModel` as `-Slug` (`:619-621`). That resolver lives in `P:/.agent`, outside this repo, so the planner could not confirm it accepts this slug for the class. If it refuses, the local agent stops and reports; nobody edits the registry to make it pass. AGENTS §Dual-Agent Workflow says "no snapshot pins in active callers". This scoped, user-directed pin applies to this plan's two review loops only. The overlay and the shared registry are **not** edited, and the conflict is recorded here rather than resolved silently.
- **Billing.** PROFILE B2 says to assume API-key (metered) auth until it is proven to be a subscription, and to warn before every dispatch. The request in [local-requests.md](local-requests.md) carries that warning and asks the local agent to report the auth mode `codex login status` shows.
- **Not a same-vendor route.** Sessions 25–29 used a user-authorized same-vendor subagent. This route returns to the PROFILE B1 reviewer: Codex is vendor-distinct from the author.
- **What approval does not authorize.** A reviewer `approved` authorizes nothing further. Claude Code resolves to `plan_to_exec_gate: human` (`.agent/context/harness.local.md` §Claude Code), so execution still needs a direct user message. Commit, push, merge and release remain separate human decisions. The local agent's push of the review file is part of this request; it carries no other change.

## History

- **Plan loop `s31-plan-2026-10-10-gui-polish-residuals`** (mode `plan`, budget 3 rounds):
  - Attempt before round 1: refused before dispatch (INTENT_BINDING; no round used). Fixed by `2ea8901`.
  - `3e65499` cherry-picked `306b07e` (A-13/A-14) from the Session 30 branch. It revalidated the overlay against shared registry `a7c95972` and binds `avkit_independent_reviewer` to `gpt-6.1-sol`, so the explicit `-Model gpt-6.1-sol` pin now matches the overlay rather than overriding it. Without it the dispatch failed with `overlay_not_validated`.
  - Round 1: `changes_required` (F1, F2 High blocking; F3 Medium; F4 Low), report `dc6939d`. Tokens 9,601,777 of 10,500,000.
  - Round 2: needed a token grant. Mat authorized `continue --tokens 9000000` in chat; the local dispatcher ran it, recorded `--by Mat` at 2026-10-10T21:21:08-04:00 (budget 19,500,000). Dispatch needed `AGENT_MODEL_REGISTRY_HOME=P:/.agent` (otherwise `registry_not_found`). Verdict `approved`, 0 blocking, `intent_achieved: yes`, one Low non-blocking F5; report `31a7058`. Tokens 18,210,635 of 19,500,000. The loop may close: 2 of 3 rounds used.
- **Execution loop**: a new loop with `--review-mode execution` and its own id, opened at H1-7 ([local-requests.md](local-requests.md) §EXEC_REVIEW). Its token budget is sized at `begin` for 3 high-effort rounds, so no mid-loop `continue` is needed.
