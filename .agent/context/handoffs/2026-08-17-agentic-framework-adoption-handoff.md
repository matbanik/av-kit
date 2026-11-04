---
date: "2026-08-17"
project: "agentic-framework-adoption"
meu: "none"
status: "complete"
action_required: "VALIDATE_AND_APPROVE"
template_version: "2.1"
verbosity: "standard"
plan_source: "PROJECT-PROFILE.md"
build_plan_section: "governance-adoption"
agent: "cursor-grok-4.6"
reviewer: "pending-human"
predecessor: "none"
---

# Handoff: 2026-08-17-agentic-framework-adoption-handoff

> **Status**: `complete`
> **Action Required**: `VALIDATE_AND_APPROVE`

---

## Scope

**MEU**: none — framework adoption (non-product)
**Build Plan Section**: n/a (governance)
**Predecessor**: none

---

## Acceptance Criteria

| AC | Type | Description | Source | Evidence | Status |
|----|------|-------------|--------|----------|--------|
| AC-1 | docs | `PROJECT-PROFILE.md` records Blocks A–F | Spec (`ADOPTION-GUIDE.md` Step 1) | `PROJECT-PROFILE.md` | ✅ |
| AC-2 | docs | Framework core copied, instantiated, agent files renamed | Spec (Step 2–2b) | `instantiate-apply.txt`; `.cursor/agents/av-kit-builder.md` | ✅ |
| AC-3 | docs | Harness override + reviewer chain recorded | Spec (Step 3–4) | `.agent/context/harness.local.md` | ✅ |
| AC-4 | docs | Issue→MEU loop smokes | Spec (Step 4b) | `adopt-validate.txt` (`stats` exit 0, render filled `BUILD_PLAN.md`) | ✅ |
| AC-5 | docs | av-kit product files preserved | Human-approved merge notes | `architecture.md`, `_inspiration/`, `docs/build-plan/`, `/deep-research` | ✅ |

---

## What was done

Copied `p:\agentic-framework\core\` into av-kit, ran `instantiate.py` with `framework.vars`, and wired adopter edits from the 2026-08-17 interview:

- Independent review: Codex when authenticated, else Mat. Never self-review.
- Egress: plans/code/review artifacts permitted.
- `plan_to_exec_gate: reviewer-auto` (overrides Cursor default `human`).
- Subagents installed; `fresh_worker: none` until smoke.
- Builder pin: `cursor-grok-4.6-high`. Verifier pin: `composer-2.5-fast`.

Preserved av-kit architecture, build-plan specs, inspiration files, and the existing `/deep-research` prompt pack. Replaced originating-repo trade language in `AGENTS.md`. Restored av-kit `testing-strategy.md` (framework copy was TUI/Go). Added AUTOGEN markers to `docs/BUILD_PLAN.md` and a phase-order `build-priority-matrix.md` so `/create-plan` has a Spec path.

## How to start a plan

1. Read `PROJECT-PROFILE.md` and `.agent/context/harness.local.md`.
2. Optional: `/session-grouping` on a phase spec to register MEUs.
3. `/create-plan` — writes `docs/execution/plans/{YYYY-MM-DD}-{slug}/implementation-plan.md` + `task.md` from the templates already in that folder.
4. Step 5 auto-dispatches `/plan-critical-review` to Codex. On `approved`, this repo **auto-continues into execution** (`reviewer-auto`). If Codex is down, the agent must stop and wait for Mat.

## Not done / follow-ups

- Subagent smoke receipts (verifier then builder) — required before `fresh_worker` is flipped.
- Codex CLI auth not verified in this session.
- `tools/validate_codebase.py` does not exist; quality gate is pytest/pyright/ruff.
- RTK is optional; workflow examples that say `rtk proxy` drop that prefix when `rtk` is absent.
- `emerging-standards.md` still contains originating-repo TUI/trading rows; the adoption filter at the top is in force.
- No product packages yet (`packages/`, `ui/`, `mcp-server/`).

## Files added or replaced (high signal)

- `PROJECT-PROFILE.md`, `framework.vars`, `CLAUDE.md`
- `.agent/` workflows, skills, docs, roles, schemas, templates (framework)
- `.cursor/agents/av-kit-builder.md`, `av-kit-verifier.md`
- `.claude/agents/` (same pair; Claude Code unused as driver)
- `tools/issue_triage*`, `tools/meu_status*`, `tools/Invoke-CodexDispatch.*`
- `docs/execution/plans/{PLAN,TASK}-TEMPLATE.md`
- `docs/execution/reflections/TEMPLATE.md`
- `.agent/docs/output-evidence-policy.md`
- `.agent/context/harness.local.md`
- `docs/build-plan/build-priority-matrix.md`

## Next session should

1. Human skim `PROJECT-PROFILE.md` + this handoff.
2. Run `/create-plan` for Phase 1 domain (or `/session-grouping` first).
3. After first mechanical row exists, smoke `av-kit-verifier` then `av-kit-builder`.
