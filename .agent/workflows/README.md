# av-kit Workflows

> Relocated from AGENTS.md (2026-06-13 instruction-set-optimization slim): the Workflow Invocation table. Workflow files live in this directory.


<!-- Executor column: current_agent runs inline; external_reviewer follows model-routing.md and PROFILE B; human_gate requires direct human action. -->

| Slash Command | Workflow File | Executor |
|---|---|---|
| `/create-plan` | `.agent/workflows/create-plan.md` | current_agent (auto-dispatches `/plan-critical-review` at Step 5 **and** `/execution-critical-review` at Step 6/§6a — a standalone run owns its own execution review) |
| `/delegated-plan-creation` | `.agent/workflows/delegated-plan-creation.md` | Authorized `avkit_coordinator` on claude-p for Steps 1–4; orchestrator owns independent review. Resolve with the project overlay; no provider/model upgrade is implied. |
| `/execution-session` | `.agent/workflows/execution-session.md` | current_agent (auto-dispatches `/execution-critical-review` at Step 4c) |
| `/orchestrated-delivery` | `.agent/workflows/orchestrated-delivery.md` | current_agent |
| `/pre-build-research` | `.agent/workflows/pre-build-research.md` | current_agent |
| `/tdd-implementation` | `.agent/workflows/tdd-implementation.md` | current_agent |
| `/validation-review` | `.agent/workflows/validation-review.md` | **external_reviewer** (primary `codex_cli`; full chain in `.agent/docs/model-routing.md`) — dispatch per Step 0, do NOT self-review |
| `/plan-critical-review` | `.agent/workflows/plan-critical-review.md` | **external_reviewer** (primary `codex_cli`; full chain in `.agent/docs/model-routing.md`) — dispatch per cli-dispatch SKILL.md (auto-dispatched by `/create-plan`) |
| `/execution-critical-review` | `.agent/workflows/execution-critical-review.md` | **external_reviewer** (primary `codex_cli`; full chain in `.agent/docs/model-routing.md`) — dispatch per cli-dispatch SKILL.md (auto-dispatched by `/execution-session` §4c **and** standalone `/create-plan` §6a) |
| `/plan-corrections` | `.agent/workflows/plan-corrections.md` | current_agent |
| `/execution-corrections` | `.agent/workflows/execution-corrections.md` | current_agent |
| `/meu-handoff` | `.agent/workflows/meu-handoff.md` | current_agent |
| `/issue-triage` | `.agent/workflows/issue-triage.md` | current_agent |
| `/next-project` | `.agent/workflows/next-project.md` | current_agent |
| `/mcp-audit` | `.agent/workflows/mcp-audit.md` | current_agent (container mode is a non-authoritative subset; the authoritative run is a Windows-host stage per `.agent/docs/cloud-local-collaboration.md`; procedure in `.agent/skills/mcp-tool-audit/SKILL.md`) |
| `/session-grouping` | `.agent/workflows/session-grouping.md` | current_agent (PLANNING-only; findings/phase → MEUs → sessions; hands off to `/create-plan`; non-gating, no turn-ender) |
| `/inspiration-research` | `.agent/workflows/inspiration-research.md` | current_agent (procedure in `.agent/skills/deep-research-prompting/SKILL.md`; Step 0 Pomera MCP preflight is a HARD GATE — on failure notify the human and end the turn, never silently fall back to native search) |
| `/deep-research` | `.agent/workflows/deep-research.md` | current_agent (av-kit-kept prompt pack; see `.agent/skills/deep-research/SKILL.md`) |
| `/skill-optimize` | `.agent/workflows/skill-optimize.md` | current_agent (dispatches the cross-vendor judge per cli-dispatch; stages for human adoption — never auto-merges) |
| `/cli-dispatch` | `.agent/workflows/cli-dispatch.md` | current_agent (routes to Codex / Claude / agy per skill; independent review stays on the Codex chain) |
