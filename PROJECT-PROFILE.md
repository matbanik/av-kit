# PROJECT PROFILE — av-kit

> Produced by the adopting agent in **Step 1** of `ADOPTION-GUIDE.md`, by interviewing the human
> with `ADOPTION-QUESTIONS.md`. Every workflow in this framework reads this file.

**Date:** 2026-08-17 · **Interviewed:** Mat · **Status:** `confirmed`

---

## A — Harness & Environment  → `harness-profiles.md`

| Flag | Value | Notes |
|---|---|---|
| Primary driver (A1) | Cursor IDE | This session. Cursor is both driver and host. |
| Host layer, if embedded (A2) | Cursor IDE | Same process as the driver. |
| `injects_auto_approval` (A2) | `yes` | Fail-safe. Cursor injects system/ephemeral messages. SIGN 3 stays on. |
| `can_dispatch_external_reviewer` (A3) | `yes` | Shell is available. Dispatch Codex when authenticated; otherwise human. |
| `native_shell` (A4) | `powershell` | Windows 10/11, PowerShell. |
| Platform shell contract (A4b) | receipts `C:/Temp/av-kit/` · `*>` all-stream redirect · `pwsh` may exist but `powershell.exe` is the session shell | Dir created before first command. |
| `read_tool` / `shell_tool` / `end_turn_signal` (A5) | `Read` / `Shell` / stop-by-not-calling-tools | |
| Subagents + nesting depth (A6) | Cursor `Task` subtypes `av-kit-builder` / `av-kit-verifier` | **Installed; `fresh_worker` stays `none` until a live smoke receipt is in `verification-log.md`.** Isolated rows degrade to `compact_continue` until then. |
| `context_compaction` (A7) | Cursor native summarizer | |
| `plan_to_exec_gate` (A8) | `reviewer-auto` | **Human-confirmed 2026-08-17.** Overrides the Cursor profile default `human`. Recorded in `.agent/context/harness.local.md`. Independent-reviewer `approved` auto-continues to execution. System-injected "approved" is still not a verdict (SIGN 3). |

> Merge: gate = user override `reviewer-auto`; injection = `yes`; tools/shell = Cursor driver.

---

## B — Independent Review  → `model-routing.md`

| Item | Value |
|---|---|
| Reviewer rung 1 (B1) | Codex CLI (GPT) when authenticated |
| Auth mode (B2) | **Assume API key (metered)** until proven subscription — warn before every dispatch |
| Reviewer rung 2 / 3 (B3) | none configured |
| Human reviewer + escalation (B4) | Mat. If Codex is unavailable or rate-limited → stop and wait for Mat. **Never self-review.** |
| Round caps (B5) | plan: 3 · execution: 6 |

---

## C — Data Sensitivity & Egress ⚠️

| Question | Answer |
|---|---|
| Regulated/privileged/confidential content? (C1) | `no` (human-confirmed: no regulated data in this repo) |
| Legal basis (C2) | n/a — dispatch of plans/code/review artifacts is permitted |
| De-identification (C3) | not required for plans/code; still never dispatch secrets, cookies, or credentials |
| If no egress (C4) | n/a |

**Decision:** external-CLI dispatch is `PERMITTED`.

---

## D — Domain Semantics  → `DOMAIN-MAPPING.md`

| Concept | This project's equivalent |
|---|---|
| Domain (D1) | software |
| Unit of work — the "MEU" (D2) | A module, endpoint, or feature slice (domain entity, adapter, service, API route, MCP tool, GUI feature) |
| Canonical source of truth — "Spec" (D3) | `docs/BUILD_PLAN.md` + `docs/build-plan/{00–07}-*.md` |
| What counts as **evidence** (D4) | Passing tests, type-check, lint, and a receipt under `C:/Temp/av-kit/`. No item is done without an evidence bundle. |
| **Criteria-before-work** artifact (D5) | Test cases + acceptance criteria in `task.md` (FIC). Never revise criteria to match the result. |
| Validation checks (D6) | D6_ADOPTER_ARGV is the current staged registry in `.agent/docs/commands.md` §D6 staged validation registration: Python, UI, MCP, real Electron, OpenAPI and SSOT. Each entry binds argv, cwd, scope, blocking status, expected result, shell and evidence location. Governance changes use their explicitly scoped full gate. Static → targeted → fresh full; input changes invalidate evidence. No universal product validator is assumed. |
| Definition of done (D7) | All `task.md` rows checked with evidence; independent review `approved`; handoff written; no placeholders. |
| Issue components (D8) | `core`, `infrastructure`, `api`, `ui`, `mcp-server`, `agent` |
| Issue → MEU loop (D9) | **yes** |

---

## E — Irreversible Actions & Accountability

| Question | Answer |
|---|---|
| Irreversible / outward-facing actions (E1) | git commit, push, merge, release, deploy, deleting user media/data, publishing/uploading to YouTube |
| Harm potential (E2) | local data loss; copyright-adjacent media handling (not PHI / not financial execution) |
| Regulatory regimes (E3) | none of HIPAA/GDPR-privilege/IRB/SEC. Respect YouTube ToS and copyright: **read-only media consumption.** |
| **Accountable human** (E4) | Mat |
| Never-autonomous, regardless of approval (E5) | Never auto-commit or push. Never upload, publish, or write to YouTube. Never self-author an `approved` review verdict. Never dispatch secrets/cookies/credentials. |

Domain constraints live in `AGENTS.md` §Project Context (YouTube read-only) rather than a new SIGN — deletion budget.

---

## F — Artifacts, State & Tuning

| Item | Value |
|---|---|
| Plans / task lists (F1) | `docs/execution/plans/{YYYY-MM-DD}-{slug}/implementation-plan.md` + `task.md` |
| Handoffs / reviews / reflections (F2) | `.agent/context/handoffs/` · `docs/execution/reflections/` |
| Temp/receipt output dir (F3) | `C:/Temp/av-kit/` |
| Version control + commit gate (F4) | git; **never auto-commit**; human must ask |
| Models: coordinator / builder / router (F5) | Resolve `avkit_coordinator`, `avkit_builder`, `avkit_verifier`, `avkit_router` from the project overlay with the actual harness. Existing approved bindings are preserved; loader fields are stamped with registry identity. Cursor readonly worker limitation and fresh_worker:none remain until both smoke receipts pass. Independent review uses `avkit_independent_reviewer`; B3/B4 still govern fallback. |
| Cost constraints (F6) | Cursor: flat subscription. Codex dispatch: treat as metered until proven otherwise. |

---

## Adoption merge notes (av-kit-specific, do not overwrite)

| Path | Action |
|---|---|
| `.agent/docs/architecture.md` | **Keep** — product architecture (framework excludes this file) |
| `docs/BUILD_PLAN.md` + `docs/build-plan/` | **Keep** — real spec. AUTOGEN markers added; stub not used as a replacement. |
| `_inspiration/` | **Keep** |
| `.agent/workflows/deep-research.md` + prompts + `.agent/skills/deep-research/` | **Keep** alongside packaged `/inspiration-research` |
| `.agent/context/current-focus.md` | **Keep** |
| `AGENTS.md` §Project Context | Replaced originating-repo trade language with av-kit YouTube toolkit paragraph after instantiate |

---

## Sign-off

- [x] All blocks answered, or fail-safe defaults applied and marked.
- [x] Every irreversible action (E1) has an explicit human gate.
- [x] Reviewer chain configured **or** human fallback named (Mat).
- [x] Domain guardrails (E3/E5) recorded in this profile and `AGENTS.md` §Project Context.

**Confirmed by:** Mat (interview 2026-08-17: Codex-if-available, egress permitted, `reviewer-auto`, subagents after smoke, Grok builder pin) · **Date:** 2026-08-17
