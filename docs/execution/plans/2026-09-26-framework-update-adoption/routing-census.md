# Active routing census

Final WP-3/4/5 census of all active roots, docs, workflows, roles, skills, runtime templates, agent definitions and both wrappers. Every content match is recorded below without truncation. Historical handoffs/plans/reflections are not current dispatch inputs; the protected worker verification log is enumerated individually. Shared registry and source repository remain read-only.

Only the five avkit classes are adopted. Optional upstream routes are explicitly UNCONFIGURED before first use in the CLI documents. Runtime loader fields and catalog bindings retain their exact approved identities. No live provider probes were run. Fixture wrapper tests are provider-free. The paired lifecycle PNG was regenerated from class-based SVG and visually checked; it is not Electron certification.

## Matching lines

| Path:line | Classification | Action / reason | Complete matching line |
|---|---|---|---|
| `.agent/context/harness.local.md:25` | operational | Class-based routing, explicit configured-provider boundary, schema syntax or non-model fallback; no snapshot selects a provider. | - **fresh_worker: none** until .agent/skills/subagent-delegation/verification-log.md has a live readonly-verifier smoke **and** a builder write-route receipt. Agent defs are installed at .cursor/agents/av-kit-builder.md and av-kit-verifier.md. Isolated task.md rows degrade to compact_continue until that flip. **Still none for the Cursor driver after the 2026-09-11 smoke** — the builder write route **passed** on real work, but the readonly verifier route **cannot run at all on this Windows host**: Cursor cannot enforce the workspace_readonly sandbox policy (the Windows sandbox helper provides a network proxy, not filesystem isolation), so the shell never spawns. One of two receipts is not a pass. Practical consequence: rows pinned delegate_to: av-kit-verifier run on the coordinator under compact_continue; only writable-builder rows would become delegable if the flag ever flips. |
| `.agent/context/harness.local.md:26` | operational | Class-based routing, explicit configured-provider boundary, schema syntax or non-model fallback; no snapshot selects a provider. | - Coordinator, builder and verifier use avkit_coordinator, avkit_builder and avkit_verifier through the project overlay for cursor-task. Existing human-approved loader bindings are preserved; historical smoke receipts remain unchanged. |
| `.agent/context/harness.local.md:38` | operational | Class-based routing, explicit configured-provider boundary, schema syntax or non-model fallback; no snapshot selects a provider. | fresh_worker: Agent tool + .claude/agents/ (av-kit-builder, av-kit-verifier) |
| `.agent/context/harness.local.md:42` | operational | Class-based routing, explicit configured-provider boundary, schema syntax or non-model fallback; no snapshot selects a provider. |   a live readonly-verifier smoke and a builder write-route probe on real work, both recorded |
| `.agent/context/harness.local.md:44` | operational | Class-based routing, explicit configured-provider boundary, schema syntax or non-model fallback; no snapshot selects a provider. |   dispatch; compact_continue remains the fallback for any row a worker declines or returns |
| `.agent/context/harness.local.md:52` | operational | Class-based routing, explicit configured-provider boundary, schema syntax or non-model fallback; no snapshot selects a provider. | - Builder/router classes here are avkit_builder and avkit_router resolved for claude-code-agents; interactive coordinator remains the existing human-selected main session. The overlay does not create an unsupported coordinator worker binding. |
| `.agent/docs/agentic-methodology.md:239` | operational | Class-based routing, explicit configured-provider boundary, schema syntax or non-model fallback; no snapshot selects a provider. | The full nine-phase sequence — every step, its slash command, the convergence caps, and the human-intervention points — lives in the operational source of truth, [development-lifecycle.md](development-lifecycle.md). In brief, the cycle is **plan → plan-review → execute (TDD) → execution-review → closeout → commit**, with the primary driver (currently Claude, coordinator/builder tiers per .agent/docs/model-routing.md) on planning/execution and the external reviewer (avkit_independent_reviewer) on adversarial review. |
| `.agent/docs/agentic-methodology.md:241` | historical | Dated June 2026 MEU-243 observation/removed qualifier; current class named in surrounding passage. | > **Model-economics refinement (June 2026) — a two-beat sequence.** Not every step belongs on the frontier model, and adopting a cheaper one safely takes two moves. **Beat 1 — delegation:** a 2-week audit found mechanical findings (count reconciliation, boundary validation, token swaps) drove most of the 116 paid review rounds, so those are now **delegated to the builder tier (currently the harness-resolved class)** at low/medium effort while the coordinator class + appropriate effort stays on the *correctness* class. **Beat 2 — parity:** reviewing the builder tier's first delegated work (MEU-243, with the tier then filled by Sonnet 4.6) exposed style/methodology drift (a silent test guard, a test.skip, fireEvent vs userEvent), so the instruction set was made **model-agnostic and deterministically enforced** — eslint now *blocks* test.skip/.only (standards **G36**/**G37**), and AGENTS.md rules dropped their (Opus 4.8) qualifier. The lesson: delegation only pays off once the shared rules no longer assume *which* model is reading them. See .agent/docs/model-routing.md (canonical current routing), model-delegation.md, and the lifecycle doc's *Multi-Model Adoption → Delegation + Instruction Parity (the harness-resolved class)*. |
| `.agent/docs/agentic-methodology.md:274` | operational | Class-based routing, explicit configured-provider boundary, schema syntax or non-model fallback; no snapshot selects a provider. | The /skill-optimize loop (June 2026) makes this rigorous. Inspired by SkillOpt's "treat instructions like a trainable weight" idea but recreated natively and **on-demand**, it harvests past reflections + handoffs as a corpus, proposes only **bounded edits** (≤4 add/delete/replace ops — a deliberate "textual learning rate"), and gates each candidate through a **cross-vendor LLM judge** (builder-tier optimizer, currently the harness-resolved class, vs external-reviewer judge, avkit_independent_reviewer — see .agent/docs/model-routing.md) scored against a **held-out** slice of digests. Why these constraints matter: |
| `.agent/docs/artifact-naming.md:63` | operational | Class-based routing, explicit configured-provider boundary, schema syntax or non-model fallback; no snapshot selects a provider. |   reference and every face must have a system fallback. |
| `.agent/docs/claude-cli-fallback-lessons.md:1` | operational | Class-based routing, explicit configured-provider boundary, schema syntax or non-model fallback; no snapshot selects a provider. | # Claude CLI as Codex Fallback — Lessons Learned |
| `.agent/docs/claude-cli-fallback-lessons.md:4` | operational | Class-based routing, explicit configured-provider boundary, schema syntax or non-model fallback; no snapshot selects a provider. | > **THE PRACTICE DOCUMENTED HERE IS NOW PROHIBITED.** Using the coordinator's own vendor |
| `.agent/docs/claude-cli-fallback-lessons.md:5` | operational | Class-based routing, explicit configured-provider boundary, schema syntax or non-model fallback; no snapshot selects a provider. | > as a reviewer rung — "same-vendor self-review" — is not a permitted fallback at any |
| `.agent/docs/claude-cli-fallback-lessons.md:8` | operational | Class-based routing, explicit configured-provider boundary, schema syntax or non-model fallback; no snapshot selects a provider. | > encapsulates. Do **not** read it as a live fallback chain. |
| `.agent/docs/claude-cli-fallback-lessons.md:36` | historical | 2026-09-14 incident account; current prohibition at top excludes this old fallback. | The project requires external validation (self-review is prohibited per AGENTS.md). With Codex unavailable for 3 days, Claude CLI (Opus 4.8) was the fallback reviewer. |
| `.agent/docs/claude-cli-fallback-lessons.md:153` | historical | 2026-09-14 incident account; current prohibition at top excludes this old fallback. | 4. This follows the dispatch skill's rate-limit fallback protocol |
| `.agent/docs/commands.md:106` | operational | Class-based routing, explicit configured-provider boundary, schema syntax or non-model fallback; no snapshot selects a provider. | &#124; Subagent Delegation &#124; .agent/skills/subagent-delegation/SKILL.md &#124; In-harness subagent detection + delegation gate (Cursor .cursor/agents/, Claude Code .claude/agents/). Resolves fresh_worker, routes eligible task.md rows to av-kit-builder/av-kit-verifier, and enforces the never-delegate categories. &#124; |
| `.agent/docs/commands.md:125` | operational | Class-based routing, explicit configured-provider boundary, schema syntax or non-model fallback; no snapshot selects a provider. | - **Model & CLI routing** → .agent/docs/model-routing.md — the routed stack (3 model tiers — Coordinator/Builder/Router — + external reviewer + 2 execution modes), the independent-reviewer chain, and nesting/delegation rules. Canonical source for "which model does which task." |
| `.agent/docs/commands.md:207` | operational | Class-based routing, explicit configured-provider boundary, schema syntax or non-model fallback; no snapshot selects a provider. | &#124; task-contract &#124; static &#124; uv run python tools/lint_task_contract.py --allowed-builder-classes avkit_builder,avkit_coordinator,avkit_verifier --task TASK &#124; Replace TASK with actual plan task path before execution &#124; |
| `.agent/docs/commands.md:217` | operational | Class-based routing, explicit configured-provider boundary, schema syntax or non-model fallback; no snapshot selects a provider. | Hash actual selected source/tests, shared fixtures/config, command manifest and relevant generated inputs; observe executable/runtime identity, installed dependency versions and relevant process environment (including registry selection and Electron flag) live before and after execution and on every reuse check. A saved environment description alone cannot prove freshness. A dirty worktree cannot be identified by HEAD alone. Any unknown input disables reuse. Static failure stops targeted/full, which are explicitly not_run; input changes require affected checks and a new fresh full gate before approval. The migration verifier's stages and stage-state recompute runtime identity and, when task_path is registered, the live task validation/dependency contract excluding administrative completion cells. They are not a universal product-runner substitute. Register other external inputs explicitly in the run's manifest. |
| `.agent/docs/context-compression.md:157` | operational | Class-based routing, explicit configured-provider boundary, schema syntax or non-model fallback; no snapshot selects a provider. | 5. **Prefer delegation over compaction where possible.** A subagent's transcript never enters the coordinator's context at all — structurally better than summarizing it later. Route bulk/mechanical work to the Builder tier and review to the external reviewer (.agent/docs/model-routing.md §Delegation & nesting rules → *Token accounting*). Compaction handles what's left. |
| `.agent/docs/context-compression.md:196` | operational | Class-based routing, explicit configured-provider boundary, schema syntax or non-model fallback; no snapshot selects a provider. | - [model-routing.md](file:///P:/av-kit/.agent/docs/model-routing.md) — Delegation keeps the coordinator's context lean (the structural complement to compaction) |
| `.agent/docs/context-tool-decision-gate.md:14` | operational | Class-based routing, explicit configured-provider boundary, schema syntax or non-model fallback; no snapshot selects a provider. | &#124; Graphify &#124; graphify-out/graph.json exists and the work requires codebase architecture, dependency, impact, or file-relationship discovery. Use it as reconnaissance and verify material claims against source files. &#124; The graph is absent/stale for the target, or the work is primarily TypeScript/TSX internals where .agent/docs/graphify.md requires direct file/search fallback. &#124; |
| `.agent/docs/development-lifecycle.md:293` | operational | Class-based routing, explicit configured-provider boundary, schema syntax or non-model fallback; no snapshot selects a provider. | ### Rate Limit Fallback |
| `.agent/docs/development-lifecycle.md:295` | operational | Class-based routing, explicit configured-provider boundary, schema syntax or non-model fallback; no snapshot selects a provider. | When the configured reviewer is unavailable, ineligible or rate-limited, preserve the actual diagnostic and complete the local review package for **Mat**. PROFILE B3 has no alternate machine route. Do not prepare a web-provider submission without new explicit human direction and permitted egress; never self-review. See .agent/skills/cli-dispatch/SKILL.md §Rate-Limit Fallback Protocol. |
| `.agent/docs/development-lifecycle.md:493` | operational | Class-based routing, explicit configured-provider boundary, schema syntax or non-model fallback; no snapshot selects a provider. |         S4["Rate limit fallback"] |
| `.agent/docs/development-lifecycle.md:783` | historical | Dated June 2026 MEU-243 observation/removed qualifier; current class named in surrounding passage. | #### Beat 2 — Multi-Model Execution Parity (2026-06-16, MEU-243 review — historical: the review below refers to the builder-tier model as it was named at the time, Sonnet 4.6 <!-- model-slug-ok: historical incident record — converting would falsify which snapshot ran MEU-243 -->; the tier is now filled by the avkit_builder class) |
| `.agent/docs/development-lifecycle.md:785` | historical | Dated June 2026 MEU-243 observation/removed qualifier; current class named in surrounding passage. | Delegating to the avkit_builder class is only safe if the instruction set is **model-agnostic and deterministically enforced** — otherwise a cheaper model produces subtly different output that burns the review rounds delegation was meant to save. Reviewing Sonnet 4.6's first delegated work (MEU-243) exposed exactly this: <!-- model-slug-ok: historical incident record — MEU-243 was executed on Sonnet 4.6 --> a silent test guard (if (!dataRow) return), a test.skip(), and a fireEvent-vs-userEvent style deviation. The response followed the "deterministic over instructional, single source of truth, model-agnostic" principles: |
| `.agent/docs/development-lifecycle.md:791` | historical | Dated June 2026 MEU-243 observation/removed qualifier; current class named in surrounding passage. | &#124; **Model-agnostic AGENTS.md** &#124; "Literal instruction mode ~~(Opus 4.8)~~" <!-- model-slug-ok: historical strikethrough records the qualifier removed in June 2026 --> → "do not rely on **any model** inferring related work"; "NEVER modify **_or neutralize_** tests… silent guards… See G36" &#124; Removes model-specific branches; one rule for every model &#124; |
| `.agent/docs/development-lifecycle.md:876` | operational | Class-based routing, explicit configured-provider boundary, schema syntax or non-model fallback; no snapshot selects a provider. | &#124; Rate limit fallback &#124; Provider-agnostic &#124; Works for any CLI provider &#124; |
| `.agent/docs/emerging-standards.md:249` | operational | Class-based routing, explicit configured-provider boundary, schema syntax or non-model fallback; no snapshot selects a provider. |     """Shared filter builder (used by both list + count).""" |
| `.agent/docs/emerging-standards.md:491` | operational | Class-based routing, explicit configured-provider boundary, schema syntax or non-model fallback; no snapshot selects a provider. |   1. [ ] img-src directive explicitly listed (not relying on default-src fallback) |
| `.agent/docs/harness-profiles.md:60` | operational | Class-based routing, explicit configured-provider boundary, schema syntax or non-model fallback; no snapshot selects a provider. | &#124; can_dispatch_external_reviewer &#124; yes \&#124; no &#124; Can this harness shell out to a reviewer CLI (Codex/Gemini/headless-claude)? When no, follow the no-dispatch fallback in cli-dispatch/SKILL.md &#124; |
| `.agent/docs/harness-profiles.md:74` | operational | Class-based routing, explicit configured-provider boundary, schema syntax or non-model fallback; no snapshot selects a provider. | &#124; **Claude Code** (current primary driver; plugin in Antigravity, CLI/IDE) &#124; primary-driver &#124; human &#124; no &#124; yes &#124; powershell (Windows host) or bash (Bash tool) &#124; Read / Bash (aka run_command) / stop-by-not-calling-tools &#124; /compact (manual, at boundary) + microcompaction (automatic, compact-2026-01-12 beta); auto-compact threshold in settings.json &#124; Agent/Task tool + .claude/agents/ (model: sonnet\&#124;opus\&#124;haiku\&#124;inherit; tools allowlist; skills: preload) &#124; avkit_coordinator main session (human selected) + avkit_builder &#124; |
| `.agent/docs/harness-profiles.md:75` | operational | Class-based routing, explicit configured-provider boundary, schema syntax or non-model fallback; no snapshot selects a provider. | &#124; **Cursor IDE** (current primary driver/host) &#124; primary-driver &#124; human &#124; no &#124; yes &#124; OS-dependent (Windows → powershell) &#124; Read / Shell / stop-by-not-calling-tools &#124; native summarizer &#124; Assistant-addressable Cursor Task tool (av-kit-builder / av-kit-verifier) + .cursor/agents/ — autonomous fresh_worker (also reads .claude/agents/; .cursor/ wins conflicts). &#124; avkit_coordinator + avkit_builder; local fresh_worker override wins &#124; |
| `.agent/docs/harness-profiles.md:80` | operational | Class-based routing, explicit configured-provider boundary, schema syntax or non-model fallback; no snapshot selects a provider. | &#124; **headless claude -p** (isolated worker; not reviewer fallback) &#124; isolated-worker &#124; human *(unless the invoking script supplies direction)* &#124; no &#124; yes *(each spawn is an isolated main agent with the full Task tool + a fresh nesting-depth budget)* &#124; bash / posix-sh &#124; Read / Bash / process-exit &#124; auto-compact via SDK/config; each spawn starts with a fresh context anyway &#124; none *(each spawn is itself the fresh worker)* &#124; avkit_coordinator on claude-p only for authorized non-review work &#124; |
| `.agent/docs/macos-setup.md:262` | operational | Class-based routing, explicit configured-provider boundary, schema syntax or non-model fallback; no snapshot selects a provider. | **Fallbacks when the cask binary hangs:** |
| `.agent/docs/model-delegation.md:1` | operational | Class-based routing, explicit configured-provider boundary, schema syntax or non-model fallback; no snapshot selects a provider. | # Model Delegation Policy — Builder vs Coordinator (Harness-Conditional) |
| `.agent/docs/model-delegation.md:3` | operational | Class-based routing, explicit configured-provider boundary, schema syntax or non-model fallback; no snapshot selects a provider. | > **Canonical routing matrix:** [.agent/docs/model-routing.md](model-routing.md) is the source of truth for the full routed stack (3 model tiers — Coordinator / Builder / Router — plus an external reviewer and two execution modes) and the independent-reviewer chain. **This file is the detailed work-class taxonomy *within* the Coordinator and Builder tiers** — which specific tasks are "mechanical" (delegate) vs "correctness" (keep). |
| `.agent/docs/model-delegation.md:9` | operational | Class-based routing, explicit configured-provider boundary, schema syntax or non-model fallback; no snapshot selects a provider. | Two work classes run under one heavyweight protocol. Match the **class + effort** to the work class instead of running everything on the coordinator tier at high effort. |
| `.agent/docs/model-delegation.md:11` | operational | Class-based routing, explicit configured-provider boundary, schema syntax or non-model fallback; no snapshot selects a provider. | ## Delegate to the builder tier (low/medium effort) — the mechanical class |
| `.agent/docs/model-delegation.md:22` | operational | Class-based routing, explicit configured-provider boundary, schema syntax or non-model fallback; no snapshot selects a provider. | ## Keep on the coordinator (high/xhigh) — the correctness class |
| `.agent/docs/model-delegation.md:37` | operational | Class-based routing, explicit configured-provider boundary, schema syntax or non-model fallback; no snapshot selects a provider. |   the mechanical class to the av-kit-builder subagent and verbose validation to the |
| `.agent/docs/model-delegation.md:38` | operational | Class-based routing, explicit configured-provider boundary, schema syntax or non-model fallback; no snapshot selects a provider. |   av-kit-verifier subagent via the resolved harness's Agent/Task tool — e.g. Claude Code's |
| `.agent/docs/model-delegation.md:39` | operational | Class-based routing, explicit configured-provider boundary, schema syntax or non-model fallback; no snapshot selects a provider. |   Agent tool + .claude/agents/ (model: sonnet), <!-- model-slug-ok: harness agent-def frontmatter schema uses vendor shorthand, not capability classes --> or Cursor's assistant-addressable Task tool |
| `.agent/docs/model-delegation.md:40` | operational | Class-based routing, explicit configured-provider boundary, schema syntax or non-model fallback; no snapshot selects a provider. |   (av-kit-builder / av-kit-verifier) + .cursor/agents/ (builder class binding via registry autogen). |
| `.agent/docs/model-delegation.md:52` | operational | Class-based routing, explicit configured-provider boundary, schema syntax or non-model fallback; no snapshot selects a provider. | The 2-week audit (21 reflections, 31 reviews, 18 measured sessions) found **116 paid review rounds**, the single largest process cost — and most findings were mechanical (count reconciliation, boundary validation, variant/size swaps, raw-button→primitive). These are low-risk and downgradeable. Reserve coordinator-tier effort for correctness MEUs and the adversarial avkit_independent_reviewer; route the mechanical class to avkit_builder to cut cost and avoid overthinking. |
| `.agent/docs/model-routing.md:9` | operational | Class-based routing, explicit configured-provider boundary, schema syntax or non-model fallback; no snapshot selects a provider. | &#124; Coordinator &#124; avkit_coordinator &#124; Planning, architecture, synthesis, governance and correctness reasoning &#124; |
| `.agent/docs/model-routing.md:10` | operational | Class-based routing, explicit configured-provider boundary, schema syntax or non-model fallback; no snapshot selects a provider. | &#124; Builder &#124; avkit_builder &#124; One bounded mechanical implementation task with explicit criteria &#124; |
| `.agent/docs/model-routing.md:11` | operational | Class-based routing, explicit configured-provider boundary, schema syntax or non-model fallback; no snapshot selects a provider. | &#124; Verifier &#124; avkit_verifier &#124; Read-only evidence collection; cannot approve work &#124; |
| `.agent/docs/model-routing.md:15` | operational | Class-based routing, explicit configured-provider boundary, schema syntax or non-model fallback; no snapshot selects a provider. | The overlay is add-only: no inherited global binding is overwritten and no class inherits an upstream fallback chain. No provider, model upgrade, or worker capability is introduced. Interactive Claude Code coordinator selection remains the existing human-selected main session; the catalog has no avkit_coordinator binding on claude-code-agents. Do not translate that refusal into a substitute. |
| `.agent/docs/model-routing.md:39` | operational | Class-based routing, explicit configured-provider boundary, schema syntax or non-model fallback; no snapshot selects a provider. | Delegate mechanical tasks only when a worker is authorized. Keep correctness decisions on the coordinator, verdicts on the independent reviewer, and irreversible acts/human gates with the human. Do not promote a worker to coordinator or reviewer. Use separate worktrees for concurrent writers. Retain the documented nesting cap of five; prefer independent bounded tasks over deep nesting. See model-delegation.md and subagent-delegation/SKILL.md for dispatch and acceptance contracts. |
| `.agent/docs/triage-meu-loop.md:76` | operational | Class-based routing, explicit configured-provider boundary, schema syntax or non-model fallback; no snapshot selects a provider. | Human/coordinator gates apply for ARCH-DECISION and enrichment that needs judgment — |
| `.agent/docs/triage-meu-loop.md:77` | operational | Class-based routing, explicit configured-provider boundary, schema syntax or non-model fallback; no snapshot selects a provider. | do not delegate those to a builder subagent. |
| `.agent/docs/triage-meu-loop.md:85` | operational | Class-based routing, explicit configured-provider boundary, schema syntax or non-model fallback; no snapshot selects a provider. | Preferred input: triage-output.yaml. Fallback: read known-issues.yaml directly when |
| `.agent/docs/triage-meu-loop.md:141` | operational | Class-based routing, explicit configured-provider boundary, schema syntax or non-model fallback; no snapshot selects a provider. | on the coordinator / human gate — do not hand those to a builder subagent. |
| `.agent/docs/verification-principles.md:21` | operational | Class-based routing, explicit configured-provider boundary, schema syntax or non-model fallback; no snapshot selects a provider. | GUARDRAILS.md SIGN 1 (the read-only plan-local verifier carve-out), and **V31** is cited |
| `.agent/docs/verification-principles.md:125` | operational | Class-based routing, explicit configured-provider boundary, schema syntax or non-model fallback; no snapshot selects a provider. | GUARDRAILS.md SIGN 1 depends on this principle for its read-only-verifier carve-out: |
| `.agent/docs/verification-principles.md:126` | operational | Class-based routing, explicit configured-provider boundary, schema syntax or non-model fallback; no snapshot selects a provider. | running a plan-local verifier during planning is not entering execution, it is how a plan |
| `.agent/docs/verification-principles.md:127` | operational | Class-based routing, explicit configured-provider boundary, schema syntax or non-model fallback; no snapshot selects a provider. | proves its gates can fail. The corollary there is the important half — **if a verifier cannot |
| `.agent/model-registry.local.json:7` | binding | Approved AVKIT_CLASS_MAP catalog binding or compiled mirror; sole model identity authority. |           "slug": "claude-sonnet-5-5" |
| `.agent/model-registry.local.json:11` | binding | Approved AVKIT_CLASS_MAP catalog binding or compiled mirror; sole model identity authority. |           "slug": "cursor-grok-4.6" |
| `.agent/model-registry.local.json:32` | binding | Approved AVKIT_CLASS_MAP catalog binding or compiled mirror; sole model identity authority. |           "slug": "claude-opus-5" |
| `.agent/model-registry.local.json:36` | binding | Approved AVKIT_CLASS_MAP catalog binding or compiled mirror; sole model identity authority. |           "slug": "cursor-grok-4.6" |
| `.agent/model-registry.local.json:58` | binding | Approved AVKIT_CLASS_MAP catalog binding or compiled mirror; sole model identity authority. |           "slug": "gpt-6.1-sol" |
| `.agent/model-registry.local.json:78` | binding | Approved AVKIT_CLASS_MAP catalog binding or compiled mirror; sole model identity authority. |           "slug": "claude-haiku-5-5" |
| `.agent/model-registry.local.json:94` | binding | Approved AVKIT_CLASS_MAP catalog binding or compiled mirror; sole model identity authority. |           "slug": "claude-sonnet-5-5" |
| `.agent/model-registry.local.json:98` | binding | Approved AVKIT_CLASS_MAP catalog binding or compiled mirror; sole model identity authority. |           "slug": "composer-2.5-fast" |
| `.agent/model-registry.local.yaml:9` | binding | Approved AVKIT_CLASS_MAP catalog binding or compiled mirror; sole model identity authority. |       cursor-task: {slug: cursor-grok-4.6, effort: xhigh} |
| `.agent/model-registry.local.yaml:10` | binding | Approved AVKIT_CLASS_MAP catalog binding or compiled mirror; sole model identity authority. |       claude-p: {slug: claude-opus-5, effort: high} |
| `.agent/model-registry.local.yaml:20` | binding | Approved AVKIT_CLASS_MAP catalog binding or compiled mirror; sole model identity authority. |       cursor-task: {slug: cursor-grok-4.6, effort: xhigh} |
| `.agent/model-registry.local.yaml:21` | binding | Approved AVKIT_CLASS_MAP catalog binding or compiled mirror; sole model identity authority. |       claude-code-agents: {slug: claude-sonnet-5-5, effort: medium} |
| `.agent/model-registry.local.yaml:31` | binding | Approved AVKIT_CLASS_MAP catalog binding or compiled mirror; sole model identity authority. |       cursor-task: {slug: composer-2.5-fast, effort: medium} |
| `.agent/model-registry.local.yaml:32` | binding | Approved AVKIT_CLASS_MAP catalog binding or compiled mirror; sole model identity authority. |       claude-code-agents: {slug: claude-sonnet-5-5, effort: medium} |
| `.agent/model-registry.local.yaml:43` | binding | Approved AVKIT_CLASS_MAP catalog binding or compiled mirror; sole model identity authority. |         slug: gpt-6.1-sol |
| `.agent/model-registry.local.yaml:52` | binding | Approved AVKIT_CLASS_MAP catalog binding or compiled mirror; sole model identity authority. |       claude-code-agents: {slug: claude-haiku-5-5, effort: low} |
| `.agent/skills/cli-dispatch/SKILL.md:10` | operational | Class-based routing, explicit configured-provider boundary, schema syntax or non-model fallback; no snapshot selects a provider. | Only avkit_coordinator, avkit_builder, avkit_verifier, avkit_router and avkit_independent_reviewer are adopted local classes. Generic examples for image_generator, creative_prose, architecture_single_shot, checklist_validator, surface_orchestrator or isolated_worker describe optional upstream capabilities; they are not configured dispatch routes here. Do not execute them or choose global bindings without a separate explicit user request and a source-backed plan. Resolve every adopted caller with project P:/av-kit and a supported harness; fail before provider invocation on a resolution error. PROFILE B3 has no alternate reviewer and Mat is the fallback. Actual author identity governs vendor diversity. |
| `.agent/skills/cli-dispatch/SKILL.md:176` | operational | Class-based routing, explicit configured-provider boundary, schema syntax or non-model fallback; no snapshot selects a provider. | - Subagents do NOT guarantee token savings (they often consume more tokens due to independent context loading). They are useful primarily for keeping noisy sub-tasks out of the coordinator's main context. |
| `.agent/skills/cli-dispatch/SKILL.md:286` | operational | Class-based routing, explicit configured-provider boundary, schema syntax or non-model fallback; no snapshot selects a provider. |   --producer builder-agent          # this agent may never author a verdict in this loop |
| `.agent/skills/cli-dispatch/SKILL.md:388` | operational | Class-based routing, explicit configured-provider boundary, schema syntax or non-model fallback; no snapshot selects a provider. | ## Rate-Limit Fallback Protocol |
| `.agent/skills/cli-dispatch/SKILL.md:397` | operational | Class-based routing, explicit configured-provider boundary, schema syntax or non-model fallback; no snapshot selects a provider. | ### 2. Configured fallback |
| `.agent/skills/cli-dispatch/SKILL.md:401` | operational | Class-based routing, explicit configured-provider boundary, schema syntax or non-model fallback; no snapshot selects a provider. | ### 3. Fallback steps |
| `.agent/skills/cli-dispatch/SKILL.md:406` | operational | Class-based routing, explicit configured-provider boundary, schema syntax or non-model fallback; no snapshot selects a provider. | - **EGRESS_PRECEDENCE.** External review dispatch is mandatory unless PROFILE C1/C2/C3b or E5 forbids sending work to an external provider; then stop for B4's named human reviewer. That stop is **not** SIGN 1. Self-review remains prohibited. plan_to_exec_gate: human is a separate post-approved pause. Missing CLI (can_dispatch_external_reviewer == no) is **not** the same as forbidden egress: when dispatch was permitted but the CLI is missing, follow the rate-limit fallback below (Mat is the configured fallback; no provider web-prompt without a new explicit human instruction). When egress is forbidden, you must not prepare a provider web-prompt and must not request manual external submission. |
| `.agent/skills/cli-dispatch/SKILL.md:479` | operational | Class-based routing, explicit configured-provider boundary, schema syntax or non-model fallback; no snapshot selects a provider. | For details on model assignments and fallback reviewer rungs, refer to the canonical routing policy in [.agent/docs/model-routing.md](../../docs/model-routing.md). |
| `.agent/skills/cli-dispatch/tests/Test-CliDispatch.ps1:416` | operational | Class-based routing, explicit configured-provider boundary, schema syntax or non-model fallback; no snapshot selects a provider. |         $null = & $pyForKind $ledgerForKind begin --loop-id $execLoop --review-mode execution --producer 'builder-x' --goal-anchor $kindGoal --ac-file $kindPlan 2>&1 |
| `.agent/skills/cli-dispatch/tests/Test-CliDispatch.ps1:418` | operational | Class-based routing, explicit configured-provider boundary, schema syntax or non-model fallback; no snapshot selects a provider. |         $null = & $pyForKind $ledgerForKind begin --loop-id $planLoop --review-mode plan --producer 'builder-x' --goal-anchor $kindGoal --ac-file $kindPlan 2>&1 |
| `.agent/skills/cli-dispatch/tests/Test-OpenCodePoC.ps1:10` | unconfigured | Explicit historical provider availability probe (2026-06-01 GA references); never executed or adopted as routing. |     - Claude Opus 5 via Bedrock (anthropic.claude-opus-5) |
| `.agent/skills/cli-dispatch/tests/Test-OpenCodePoC.ps1:11` | unconfigured | Explicit historical provider availability probe (2026-06-01 GA references); never executed or adopted as routing. |     - GPT-5.5 via Bedrock (openai.gpt-5.5 - GA on Bedrock since June 1, 2026) |
| `.agent/skills/cli-dispatch/tests/Test-OpenCodePoC.ps1:45` | unconfigured | Explicit historical provider availability probe (2026-06-01 GA references); never executed or adopted as routing. | $script:BedrockClaudeModel = "amazon-bedrock/anthropic.claude-opus-5" |
| `.agent/skills/cli-dispatch/tests/Test-OpenCodePoC.ps1:46` | unconfigured | Explicit historical provider availability probe (2026-06-01 GA references); never executed or adopted as routing. | $script:BedrockClaudeModelAlt = "amazon-bedrock/us.anthropic.claude-opus-5" |
| `.agent/skills/cli-dispatch/tests/Test-OpenCodePoC.ps1:47` | unconfigured | Explicit historical provider availability probe (2026-06-01 GA references); never executed or adopted as routing. | $script:BedrockGPTModel = "amazon-bedrock/openai.gpt-5.5" |
| `.agent/skills/cli-dispatch/tests/Test-OpenCodePoC.ps1:211` | unconfigured | Explicit historical provider availability probe (2026-06-01 GA references); never executed or adopted as routing. | # --- Test 3: Bedrock Claude Opus 5 --- |
| `.agent/skills/cli-dispatch/tests/Test-OpenCodePoC.ps1:214` | unconfigured | Explicit historical provider availability probe (2026-06-01 GA references); never executed or adopted as routing. |     Write-TestHeader -Name "OpenCode CLI - Bedrock Claude Opus 5" |
| `.agent/skills/cli-dispatch/tests/Test-OpenCodePoC.ps1:222` | unconfigured | Explicit historical provider availability probe (2026-06-01 GA references); never executed or adopted as routing. |         Write-TestInfo -Msg "Trying model: $script:BedrockClaudeModel" |
| `.agent/skills/cli-dispatch/tests/Test-OpenCodePoC.ps1:259` | unconfigured | Explicit historical provider availability probe (2026-06-01 GA references); never executed or adopted as routing. | # --- Test 4: Bedrock GPT-5.5 --- |
| `.agent/skills/cli-dispatch/tests/Test-OpenCodePoC.ps1:260` | unconfigured | Explicit historical provider availability probe (2026-06-01 GA references); never executed or adopted as routing. | # HISTORICAL provider-availability probe: GPT-5.5 GA'd on Bedrock 2026-06-01, which is |
| `.agent/skills/cli-dispatch/tests/Test-OpenCodePoC.ps1:261` | unconfigured | Explicit historical provider availability probe (2026-06-01 GA references); never executed or adopted as routing. | # what this test validates. GPT-5.6-sol Bedrock availability is region-dependent (404 in |
| `.agent/skills/cli-dispatch/tests/Test-OpenCodePoC.ps1:263` | unconfigured | Explicit historical provider availability probe (2026-06-01 GA references); never executed or adopted as routing. | # "upgrade" the model ID here without first confirming GPT-5.6-sol Bedrock GA in-region. |
| `.agent/skills/cli-dispatch/tests/Test-OpenCodePoC.ps1:266` | unconfigured | Explicit historical provider availability probe (2026-06-01 GA references); never executed or adopted as routing. |     Write-TestHeader -Name "OpenCode CLI - Bedrock GPT-5.5" |
| `.agent/skills/cli-dispatch/tests/Test-OpenCodePoC.ps1:267` | unconfigured | Explicit historical provider availability probe (2026-06-01 GA references); never executed or adopted as routing. |     Write-TestInfo -Msg "GPT-5.5 GA on Amazon Bedrock since June 1, 2026 (model: openai.gpt-5.5)" |
| `.agent/skills/cli-dispatch/tests/Test-OpenCodePoC.ps1:283` | unconfigured | Explicit historical provider availability probe (2026-06-01 GA references); never executed or adopted as routing. |                     Write-TestResult -Name "Bedrock GPT-5.5" -Passed $false -Msg "Error: $(Get-Preview $content 200)" -Duration $sw.Elapsed.TotalSeconds |
| `.agent/skills/cli-dispatch/tests/Test-OpenCodePoC.ps1:285` | unconfigured | Explicit historical provider availability probe (2026-06-01 GA references); never executed or adopted as routing. |                     Write-TestResult -Name "Bedrock GPT-5.5" -Passed $true -Msg "Output received ($($content.Length) chars): $(Get-Preview $content)" -Duration $sw.Elapsed.TotalSeconds |
| `.agent/skills/cli-dispatch/tests/Test-OpenCodePoC.ps1:288` | unconfigured | Explicit historical provider availability probe (2026-06-01 GA references); never executed or adopted as routing. |                 Write-TestResult -Name "Bedrock GPT-5.5" -Passed $false -Msg "Output too short" -Duration $sw.Elapsed.TotalSeconds |
| `.agent/skills/cli-dispatch/tests/Test-OpenCodePoC.ps1:291` | unconfigured | Explicit historical provider availability probe (2026-06-01 GA references); never executed or adopted as routing. |             Write-TestResult -Name "Bedrock GPT-5.5" -Passed $false -Msg "Output file not created" -Duration $sw.Elapsed.TotalSeconds |
| `.agent/skills/cli-dispatch/tests/Test-OpenCodePoC.ps1:295` | unconfigured | Explicit historical provider availability probe (2026-06-01 GA references); never executed or adopted as routing. |         Write-TestResult -Name "Bedrock GPT-5.5" -Passed $false -Msg "Exception: $_" -Duration $sw.Elapsed.TotalSeconds |
| `.agent/skills/cli-dispatch/tests/Test-OpenCodePoC.ps1:516` | unconfigured | Explicit historical provider availability probe (2026-06-01 GA references); never executed or adopted as routing. |     Write-Host "    > Supports both Claude Opus 5 AND GPT-5.5 via Bedrock" -ForegroundColor Green |
| `.agent/skills/deep-research-prompting/SKILL.md:32` | operational | Class-based routing, explicit configured-provider boundary, schema syntax or non-model fallback; no snapshot selects a provider. | Run **before** any search in the workflow. This is a human-notify gate, not a fallback branch. |
| `.agent/skills/pre-handoff-review/SKILL.md:114` | operational | Class-based routing, explicit configured-provider boundary, schema syntax or non-model fallback; no snapshot selects a provider. | # - Changed token model: rg "HMAC&#124;REST.*token&#124;confirmation_token" docs/ |
| `.agent/skills/README.md:37` | operational | Class-based routing, explicit configured-provider boundary, schema syntax or non-model fallback; no snapshot selects a provider. | &#124; subagent-delegation/SKILL.md &#124; workflows, task.md execution &#124; fresh_worker gate + builder/verifier dispatch &#124; |
| `.agent/skills/subagent-delegation/SKILL.md:3` | operational | Class-based routing, explicit configured-provider boundary, schema syntax or non-model fallback; no snapshot selects a provider. | description: In-harness subagent detection + delegation gate for Cursor (.cursor/agents/) and Claude Code (.claude/agents/). Resolves fresh_worker from the harness profile, decides which task rows may be delegated to av-kit-builder/av-kit-verifier, and feeds outcomes back into the reflection loop. Load during PLANNING; consult before each task.md row in EXECUTION. |
| `.agent/skills/subagent-delegation/SKILL.md:13` | operational | Class-based routing, explicit configured-provider boundary, schema syntax or non-model fallback; no snapshot selects a provider. | - **Cursor** — assistant-addressable Task tool subtypes av-kit-builder / |
| `.agent/skills/subagent-delegation/SKILL.md:14` | operational | Class-based routing, explicit configured-provider boundary, schema syntax or non-model fallback; no snapshot selects a provider. |   av-kit-verifier + custom agents in .cursor/agents/ (own context window, model: |
| `.agent/skills/subagent-delegation/SKILL.md:18` | operational | Class-based routing, explicit configured-provider boundary, schema syntax or non-model fallback; no snapshot selects a provider. |   (model: sonnet&#124;opus&#124;haiku&#124;inherit&#124;<id>, a tools allowlist, skills: preload, memory). <!-- model-slug-ok: Claude Code .claude/agents/ frontmatter schema tier aliases (harness_id), not live routing pins --> |
| `.agent/skills/subagent-delegation/SKILL.md:23` | operational | Class-based routing, explicit configured-provider boundary, schema syntax or non-model fallback; no snapshot selects a provider. | delegating a decision that must stay with the coordinator or the external reviewer. |
| `.agent/skills/subagent-delegation/SKILL.md:49` | operational | Class-based routing, explicit configured-provider boundary, schema syntax or non-model fallback; no snapshot selects a provider. | &#124; Cursor (Task tool authorized) &#124; Assistant-addressable Cursor Task tool (av-kit-builder / av-kit-verifier) &#124; .cursor/agents/ &#124; avkit_builder (subject to current smoke gate); avkit_coordinator — resolve per harness in the live registry home (see .agent/docs/model-routing.md) &#124; |
| `.agent/skills/subagent-delegation/SKILL.md:59` | operational | Class-based routing, explicit configured-provider boundary, schema syntax or non-model fallback; no snapshot selects a provider. | > av-kit-builder and av-kit-verifier as assistant-addressable subtypes; orchestrator-originated |
| `.agent/skills/subagent-delegation/SKILL.md:60` | operational | Class-based routing, explicit configured-provider boundary, schema syntax or non-model fallback; no snapshot selects a provider. | > dispatch uses that route + .cursor/agents/. Proven builder class: avkit_builder |
| `.agent/skills/subagent-delegation/SKILL.md:75` | operational | Class-based routing, explicit configured-provider boundary, schema syntax or non-model fallback; no snapshot selects a provider. | &#124; Owner: coder + mechanical class (model-delegation.md) + self-contained spec **and a resolved fresh_worker** &#124; Delegate to av-kit-builder, foreground &#124; |
| `.agent/skills/subagent-delegation/SKILL.md:76` | operational | Class-based routing, explicit configured-provider boundary, schema syntax or non-model fallback; no snapshot selects a provider. | &#124; Owner: tester, or any validation whose receipt is long/verbose, **and a resolved fresh_worker** &#124; Delegate to av-kit-verifier (readonly) &#124; |
| `.agent/skills/subagent-delegation/SKILL.md:77` | operational | Class-based routing, explicit configured-provider boundary, schema syntax or non-model fallback; no snapshot selects a provider. | &#124; **Correctness class**, cross-row reasoning, or an unresolved spec gap &#124; **Never delegate** — keep inline on the coordinator &#124; |
| `.agent/skills/subagent-delegation/SKILL.md:127` | operational | Class-based routing, explicit configured-provider boundary, schema syntax or non-model fallback; no snapshot selects a provider. |   own context, not the coordinator's. |
| `.agent/skills/subagent-delegation/SKILL.md:130` | operational | Class-based routing, explicit configured-provider boundary, schema syntax or non-model fallback; no snapshot selects a provider. |   builder-class dispatches; on Claude Code use the avkit_builder class. |
| `.agent/skills/subagent-delegation/SKILL.md:132` | operational | Class-based routing, explicit configured-provider boundary, schema syntax or non-model fallback; no snapshot selects a provider. |   **sequentially, foreground**. In-harness subagents primarily **protect the coordinator's |
| `.agent/skills/subagent-delegation/verification-log.md:3` | historical | Protected dated 2026-09-02/11 worker smoke observation; immutable evidence, no capability promotion. | > Adopters: record the resolved-driver live smoke and builder write-route probe here. |
| `.agent/skills/subagent-delegation/verification-log.md:11` | historical | Protected dated 2026-09-02/11 worker smoke observation; immutable evidence, no capability promotion. | harness_version: Claude Code (Opus 5 coordinator session, 2026-09-02) |
| `.agent/skills/subagent-delegation/verification-log.md:12` | historical | Protected dated 2026-09-02/11 worker smoke observation; immutable evidence, no capability promotion. | model_rung: coordinator Opus 5 · builder .claude/agents/av-kit-builder.md (model: sonnet) · verifier .claude/agents/av-kit-verifier.md (model: sonnet) |
| `.agent/skills/subagent-delegation/verification-log.md:20` | historical | Protected dated 2026-09-02/11 worker smoke observation; immutable evidence, no capability promotion. | .claude/agents/av-kit-builder.md and .claude/agents/av-kit-verifier.md, and both were |
| `.agent/skills/subagent-delegation/verification-log.md:23` | historical | Protected dated 2026-09-02/11 worker smoke observation; immutable evidence, no capability promotion. | **Verifier probe evidence (readonly):** dispatched av-kit-verifier to run the UI unit |
| `.agent/skills/subagent-delegation/verification-log.md:26` | historical | Protected dated 2026-09-02/11 worker smoke observation; immutable evidence, no capability promotion. | route is proven end to end. Receipt: C:/Temp/av-kit/probe-verifier-vitest.txt. |
| `.agent/skills/subagent-delegation/verification-log.md:28` | historical | Protected dated 2026-09-02/11 worker smoke observation; immutable evidence, no capability promotion. | > **Probe finding — the route passed, the command it was handed did not.** The verifier |
| `.agent/skills/subagent-delegation/verification-log.md:29` | historical | Protected dated 2026-09-02/11 worker smoke observation; immutable evidence, no capability promotion. | > reported 17 files / 67 tests failed, exit 1. Coordinator re-ran the suite from ui/: |
| `.agent/skills/subagent-delegation/verification-log.md:40` | historical | Protected dated 2026-09-02/11 worker smoke observation; immutable evidence, no capability promotion. | **Builder write-route probe:** dispatched av-kit-builder with the correction that finding |
| `.agent/skills/subagent-delegation/verification-log.md:45` | historical | Protected dated 2026-09-02/11 worker smoke observation; immutable evidence, no capability promotion. | Coordinator independently confirmed: 0 remaining broken forms, 13 + 1 corrected, Playwright |
| `.agent/skills/subagent-delegation/verification-log.md:52` | historical | Protected dated 2026-09-02/11 worker smoke observation; immutable evidence, no capability promotion. | harness_version: Cursor IDE (Grok coordinator session, 2026-09-11) |
| `.agent/skills/subagent-delegation/verification-log.md:53` | historical | Protected dated 2026-09-02/11 worker smoke observation; immutable evidence, no capability promotion. | model_rung: coordinator Cursor Grok · builder dispatched at cursor-grok-4.6-xhigh · verifier dispatched at composer-2.5-fast |
| `.agent/skills/subagent-delegation/verification-log.md:58` | historical | Protected dated 2026-09-02/11 worker smoke observation; immutable evidence, no capability promotion. | **Resolution basis (not directory presence):** Cursor Task tool lists subtypes; agent defs live at .cursor/agents/av-kit-builder.md and av-kit-verifier.md. PROJECT-PROFILE.md A6 = enable after smoke. .agent/context/harness.local.md keeps fresh_worker: none until this log has **both** receipts. |
| `.agent/skills/subagent-delegation/verification-log.md:61` | historical | Protected dated 2026-09-02/11 worker smoke observation; immutable evidence, no capability promotion. | in harness.local.md was cursor-grok-4.6-high, which is **not an available slug in this |
| `.agent/skills/subagent-delegation/verification-log.md:62` | historical | Protected dated 2026-09-02/11 worker smoke observation; immutable evidence, no capability promotion. | harness**. The builder was dispatched at cursor-grok-4.6-xhigh, the nearest available 4.6 |
| `.agent/skills/subagent-delegation/verification-log.md:63` | historical | Protected dated 2026-09-02/11 worker smoke observation; immutable evidence, no capability promotion. | rung; the verifier ran at its registered pin, composer-2.5-fast. The stale slug was |
| `.agent/skills/subagent-delegation/verification-log.md:64` | historical | Protected dated 2026-09-02/11 worker smoke observation; immutable evidence, no capability promotion. | corrected repo-wide to cursor-grok-4.6-xhigh later the same day (human direction), so this |
| `.agent/skills/subagent-delegation/verification-log.md:67` | historical | Protected dated 2026-09-02/11 worker smoke observation; immutable evidence, no capability promotion. | **Verifier probe evidence (readonly): FAIL — infrastructure, not a route defect and not a |
| `.agent/skills/subagent-delegation/verification-log.md:68` | historical | Protected dated 2026-09-02/11 worker smoke observation; immutable evidence, no capability promotion. | test failure.** av-kit-verifier was dispatched to run npm --prefix ui run test and report |
| `.agent/skills/subagent-delegation/verification-log.md:79` | historical | Protected dated 2026-09-02/11 worker smoke observation; immutable evidence, no capability promotion. | No receipt was produced — C:/Temp/av-kit/probe-cursor-verifier-vitest.txt does not exist, |
| `.agent/skills/subagent-delegation/verification-log.md:82` | historical | Protected dated 2026-09-02/11 worker smoke observation; immutable evidence, no capability promotion. | delegate_to: av-kit-verifier must run on the coordinator under compact_continue until a |
| `.agent/skills/subagent-delegation/verification-log.md:83` | historical | Protected dated 2026-09-02/11 worker smoke observation; immutable evidence, no capability promotion. | sandbox backend exists. Note the asymmetry — the *writable* builder route runs fine, because |
| `.agent/skills/subagent-delegation/verification-log.md:86` | historical | Protected dated 2026-09-02/11 worker smoke observation; immutable evidence, no capability promotion. | **Builder write-route probe: PASS, on real work.** av-kit-builder was dispatched to extract |
| `.agent/skills/subagent-delegation/verification-log.md:96` | historical | Protected dated 2026-09-02/11 worker smoke observation; immutable evidence, no capability promotion. | Coordinator independently confirmed rather than accepting the report: body length **17,267** |
| `.agent/skills/subagent-delegation/verification-log.md:101` | historical | Protected dated 2026-09-02/11 worker smoke observation; immutable evidence, no capability promotion. | C:/Temp/av-kit/probe-cursor-builder-extract.txt, |
| `.agent/skills/subagent-delegation/verification-log.md:102` | historical | Protected dated 2026-09-02/11 worker smoke observation; immutable evidence, no capability promotion. | probe-cursor-builder-verify.txt, coord-verify-builder-probe.txt. |
| `.agent/skills/subagent-delegation/verification-log.md:105` | historical | Protected dated 2026-09-02/11 worker smoke observation; immutable evidence, no capability promotion. | > readonly-verifier smoke **and** a builder write-route receipt; one of the two failed, and a |
| `.agent/templates/PLAN-TEMPLATE.md:66` | operational | Class-based routing, explicit configured-provider boundary, schema syntax or non-model fallback; no snapshot selects a provider. | Task tables in task.md may include an optional **builder_model** column (10-col |
| `.agent/templates/PLAN-TEMPLATE.md:71` | operational | Class-based routing, explicit configured-provider boundary, schema syntax or non-model fallback; no snapshot selects a provider. | architecture_single_shot is reserved for its own shape and is never a builder. |
| `.agent/templates/REFLECTION-TEMPLATE.md:59` | operational | Class-based routing, explicit configured-provider boundary, schema syntax or non-model fallback; no snapshot selects a provider. |     <!-- Delegation via .agent/skills/subagent-delegation/SKILL.md (av-kit-builder / av-kit-verifier). --> |
| `.agent/templates/TASK-TEMPLATE.md:41` | operational | Class-based routing, explicit configured-provider boundary, schema syntax or non-model fallback; no snapshot selects a provider. | > **builder_model** (10-column tables). Legacy 9-column tables remain valid. |
| `.agent/templates/TASK-TEMPLATE.md:42` | operational | Class-based routing, explicit configured-provider boundary, schema syntax or non-model fallback; no snapshot selects a provider. | > builder_model names a **capability class** — avkit_builder for mechanical rows, |
| `.agent/templates/TASK-TEMPLATE.md:48` | operational | Class-based routing, explicit configured-provider boundary, schema syntax or non-model fallback; no snapshot selects a provider. | > architecture_single_shot is reserved for its own shape and is never a builder. |
| `.agent/templates/TASK-TEMPLATE.md:50` | operational | Class-based routing, explicit configured-provider boundary, schema syntax or non-model fallback; no snapshot selects a provider. | &#124; # &#124; Task &#124; Owner &#124; Deliverable &#124; Validation &#124; Depends on &#124; Context strategy &#124; Durable outputs &#124; builder_model &#124; Status &#124; |
| `.agent/templates/TASK-TEMPLATE.md:62` | operational | Class-based routing, explicit configured-provider boundary, schema syntax or non-model fallback; no snapshot selects a provider. | > adding delegate_to: av-kit-builder (or av-kit-verifier) **inside the row's Task cell** — |
| `.agent/templates/TASK-TEMPLATE.md:90` | operational | Class-based routing, explicit configured-provider boundary, schema syntax or non-model fallback; no snapshot selects a provider. | &#124; H1-5 &#124; Read the handoff template and deterministic latest peer exemplar. &#124; orchestrator &#124; Source-read receipt &#124; view_file: .agent/context/handoffs/TEMPLATE.md plus latest peer handoff &#124; H1-4 &#124; compact_continue &#124; Template/exemplar receipt; compact_continue fallback &#124; avkit_coordinator &#124; [ ] &#124; |
| `.agent/templates/TASK-TEMPLATE.md:91` | operational | Class-based routing, explicit configured-provider boundary, schema syntax or non-model fallback; no snapshot selects a provider. | &#124; H1-6 &#124; Create the complete evidence handoff. Product: .agent/context/handoffs/{date}-{project-slug}-{MEU-ID}-handoff.md per MEU. Non-product meus: []: .agent/context/handoffs/{date}-{project-slug}-handoff.md. &#124; orchestrator &#124; Canonical handoff set &#124; rtk proxy uv run python tools/validate_closeout_artifacts.py --handoff {handoff-file} --plan {plan-file} *> C:/Temp/av-kit/handoff-check.txt; $code=$LASTEXITCODE; Get-Content C:/Temp/av-kit/handoff-check.txt; exit $code &#124; H1-5 &#124; compact_continue &#124; Canonical handoff(s); compact_continue fallback &#124; avkit_coordinator &#124; [ ] &#124; |
| `.agent/templates/TASK-TEMPLATE.md:95` | operational | Class-based routing, explicit configured-provider boundary, schema syntax or non-model fallback; no snapshot selects a provider. | &#124; H1-7 &#124; Dispatch independent reviewer under EGRESS_PRECEDENCE; loop corrections within ledger limits. &#124; reviewer dispatch / coder corrections &#124; Rolling review &#124; {exact authorized dispatch command with preserved exit} &#124; H1-6b &#124; isolated &#124; Rolling review; durable findings; compact_continue fallback &#124; — &#124; [ ] &#124; |
| `.agent/templates/TASK-TEMPLATE.md:100` | operational | Class-based routing, explicit configured-provider boundary, schema syntax or non-model fallback; no snapshot selects a provider. | &#124; H2-2 &#124; Create the full reflection with review churn and Instruction Coverage YAML. &#124; orchestrator &#124; docs/execution/reflections/{date}-{project-slug}-reflection.md &#124; rtk proxy uv run python tools/validate_closeout_artifacts.py --reflection {reflection-file} --reflection-template docs/execution/reflections/TEMPLATE.md --reflection-schema .agent/schemas/reflection.v1.yaml *> C:/Temp/av-kit/reflection-check.txt; $code=$LASTEXITCODE; Get-Content C:/Temp/av-kit/reflection-check.txt; exit $code &#124; H2-1 &#124; compact_continue &#124; Reflection; compact_continue fallback &#124; avkit_coordinator &#124; [ ] &#124; |
| `.agent/templates/TASK-TEMPLATE.md:102` | operational | Class-based routing, explicit configured-provider boundary, schema syntax or non-model fallback; no snapshot selects a provider. | &#124; H2-4 &#124; Run complete closeout structural, handoff, approval, and reflection checks. &#124; tester &#124; Passing completion-preflight receipt &#124; rtk proxy uv run python tools/lint_task_contract.py --allowed-builder-classes avkit_builder,avkit_coordinator,avkit_verifier --task docs/execution/plans/{date}-{project-slug}/task.md *> C:/Temp/av-kit/closeout-preflight.txt; $code=$LASTEXITCODE; Get-Content C:/Temp/av-kit/closeout-preflight.txt; exit $code &#124; H2-3 &#124; shared &#124; Closeout receipt &#124; avkit_coordinator &#124; [ ] &#124; |
| `.agent/workflows/cli-dispatch.md:11` | operational | Class-based routing, explicit configured-provider boundary, schema syntax or non-model fallback; no snapshot selects a provider. | Only avkit_coordinator, avkit_builder, avkit_verifier, avkit_router and avkit_independent_reviewer are adopted local classes. Generic examples for image_generator, creative_prose, architecture_single_shot, checklist_validator, surface_orchestrator or isolated_worker describe optional upstream capabilities; they are not configured dispatch routes here. Do not execute them or choose global bindings without a separate explicit user request and a source-backed plan. Resolve every adopted caller with project P:/av-kit and a supported harness; fail before provider invocation on a resolution error. PROFILE B3 has no alternate reviewer and Mat is the fallback. Actual author identity governs vendor diversity. |
| `.agent/workflows/cli-dispatch.md:48` | operational | Class-based routing, explicit configured-provider boundary, schema syntax or non-model fallback; no snapshot selects a provider. |   → YES → your harness's headless builder CLI, wrapped per cli-dispatch/SKILL.md |
| `.agent/workflows/cli-dispatch.md:49` | operational | Class-based routing, explicit configured-provider boundary, schema syntax or non-model fallback; no snapshot selects a provider. |      Prefer in-harness Task → av-kit-builder when Task is available. |
| `.agent/workflows/cli-dispatch.md:50` | operational | Class-based routing, explicit configured-provider boundary, schema syntax or non-model fallback; no snapshot selects a provider. |      Never route independent review to a builder (Codex chain only). |
| `.agent/workflows/cli-dispatch.md:188` | operational | Class-based routing, explicit configured-provider boundary, schema syntax or non-model fallback; no snapshot selects a provider. | # $raw = Get-Content C:/Temp/av-kit/dispatch/coordinator-output.txt -Encoding Unicode -Raw |
| `.agent/workflows/cli-dispatch.md:233` | operational | Class-based routing, explicit configured-provider boundary, schema syntax or non-model fallback; no snapshot selects a provider. | - ❌ **Never dispatch to agy for validation verdicts** — avkit_independent_reviewer remains the reviewer; agy is for data processing / surface_orchestrator work (unconfigured here; never a reviewer fallback) |
| `.agent/workflows/cli-dispatch.md:239` | operational | Class-based routing, explicit configured-provider boundary, schema syntax or non-model fallback; no snapshot selects a provider. | - ❌ **Never use a builder-tier CLI for independent review verdicts** — Codex chain only (self-review prohibition) |
| `.agent/workflows/cli-dispatch.md:245` | operational | Class-based routing, explicit configured-provider boundary, schema syntax or non-model fallback; no snapshot selects a provider. | - ❌ **Never skip effort at the class ceiling on critical decisions** — default effort underutilizes the coordinator class's thinking capacity |
| `.agent/workflows/create-plan.md:192` | operational | Class-based routing, explicit configured-provider boundary, schema syntax or non-model fallback; no snapshot selects a provider. |   context_strategy, durable_outputs, optional builder_model (10-col), and status. |
| `.agent/workflows/create-plan.md:198` | operational | Class-based routing, explicit configured-provider boundary, schema syntax or non-model fallback; no snapshot selects a provider. |   builder_model column with class pins {avkit_builder&#124;avkit_coordinator&#124;avkit_verifier}; never auto / architecture_single_shot as builder. For every |
| `.agent/workflows/create-plan.md:311` | operational | Class-based routing, explicit configured-provider boundary, schema syntax or non-model fallback; no snapshot selects a provider. | 3. **A human.** When every machine rung is rate-limited or unavailable, the escalation is a human gate — **never** the same vendor that authored the plan. A self-review rung is PROHIBITED; see [claude-cli-fallback-lessons.md](../docs/claude-cli-fallback-lessons.md). |
| `.agent/workflows/create-plan.md:365` | operational | Class-based routing, explicit configured-provider boundary, schema syntax or non-model fallback; no snapshot selects a provider. | > **Permitted, and this is the exception that matters:** a **plan-local read-only verifier** — |
| `.agent/workflows/create-plan.md:370` | operational | Class-based routing, explicit configured-provider boundary, schema syntax or non-model fallback; no snapshot selects a provider. | > **If such a verifier cannot be run, delete it — do not strengthen it.** An unrunnable check |
| `.agent/workflows/create-plan.md:479` | operational | Class-based routing, explicit configured-provider boundary, schema syntax or non-model fallback; no snapshot selects a provider. | - Attempt the next reviewer rung (see §5a priority chain: configured vendor-distinct reviewer → Mat (PROFILE B; no second machine rung)) |
| `.agent/workflows/create-plan.md:480` | operational | Class-based routing, explicit configured-provider boundary, schema syntax or non-model fallback; no snapshot selects a provider. | - If **all rungs** rate-limited/unavailable → HARD STOP with "All reviewer rungs rate-limited. Reset at {time}." (never self-review) |
| `.agent/workflows/create-plan.md:488` | operational | Class-based routing, explicit configured-provider boundary, schema syntax or non-model fallback; no snapshot selects a provider. | > 1. Rate limit hit (all *cross-vendor* reviewer rungs; a same-vendor rung is not one) |
| `.agent/workflows/create-plan.md:566` | operational | Class-based routing, explicit configured-provider boundary, schema syntax or non-model fallback; no snapshot selects a provider. | > The Step 6 execution-review loop is an **atomic non-stop region** (same as the Step 5 plan-review loop): the only valid exits are (1) approved, (2) all reviewer rungs rate-limited, (3) reviewer asks a human-decision-required question, (4) round cap reached. |
| `.agent/workflows/delegated-plan-creation.md:166` | operational | Class-based routing, explicit configured-provider boundary, schema syntax or non-model fallback; no snapshot selects a provider. | $plannerClass = "coordinator"  # complex plans: architecture_single_shot when bound on this harness |
| `.agent/workflows/delegated-plan-creation.md:170` | operational | Class-based routing, explicit configured-provider boundary, schema syntax or non-model fallback; no snapshot selects a provider. | # Dispatch (coordinator example — swap class when architecture_single_shot is bound) |
| `.agent/workflows/delegated-plan-creation.md:357` | operational | Class-based routing, explicit configured-provider boundary, schema syntax or non-model fallback; no snapshot selects a provider. | Planner: {architecture_single_shot &#124; coordinator} @ {effort} — {turns} turns |
| `.agent/workflows/execution-session.md:97` | operational | Class-based routing, explicit configured-provider boundary, schema syntax or non-model fallback; no snapshot selects a provider. | > and result-acceptance rules for av-kit-builder/av-kit-verifier. |
| `.agent/workflows/execution-session.md:183` | operational | Class-based routing, explicit configured-provider boundary, schema syntax or non-model fallback; no snapshot selects a provider. | rtk proxy uv run python tools/review_ledger.py begin --loop-id exec-<plan-slug> --review-mode execution --producer <builder agent> --goal-anchor "<one sentence: what this execution was for>" --ac-file docs/execution/plans/<plan>/implementation-plan.md |
| `.agent/workflows/execution-session.md:220` | operational | Class-based routing, explicit configured-provider boundary, schema syntax or non-model fallback; no snapshot selects a provider. | - Rate limit mid-loop → fallback reviewer or HARD STOP with timer |
| `.agent/workflows/inspiration-research.md:155` | operational | Class-based routing, explicit configured-provider boundary, schema syntax or non-model fallback; no snapshot selects a provider. | &#124; Pomera preflight fails &#124; **Stop and notify** (Step 0). Never a silent fallback. &#124; |
| `.agent/workflows/meu-handoff.md:116` | operational | Class-based routing, explicit configured-provider boundary, schema syntax or non-model fallback; no snapshot selects a provider. | changes_required  →  ready_for_review  (coordinator fixes and resubmits) |
| `.agent/workflows/meu-handoff.md:123` | operational | Class-based routing, explicit configured-provider boundary, schema syntax or non-model fallback; no snapshot selects a provider. | Maximum 2 revision cycles (coordinator→reviewer→coordinator→reviewer) per MEU. After 2 cycles, escalate to human orchestrator with: |
| `.agent/workflows/session-grouping.md:30` | operational | Class-based routing, explicit configured-provider boundary, schema syntax or non-model fallback; no snapshot selects a provider. | 4. **Right-sized** — calibrate each session against the per-session token ceiling using **named past sessions**, not hardcoded constants (a coordinator-tier tokenizer can inflate a naive character estimate by ~20%, so measure, do not assume). |
| `.agent/workflows/session-grouping.md:40` | operational | Class-based routing, explicit configured-provider boundary, schema syntax or non-model fallback; no snapshot selects a provider. | 4. **Fallback**: if triage-output.yaml does not exist, read .agent/context/known-issues.yaml directly (the SSOT) and the source named in <source> |
| `.agent/workflows/skill-optimize.md:101` | operational | Class-based routing, explicit configured-provider boundary, schema syntax or non-model fallback; no snapshot selects a provider. | 2. **The gate is cross-vendor.** Optimizer family ≠ judge family, checked even after a fallback. |
| `.agent/workflows/validation-review.md:29` | operational | Class-based routing, explicit configured-provider boundary, schema syntax or non-model fallback; no snapshot selects a provider. | > If Codex CLI is unavailable or rate-limited, follow .agent/skills/cli-dispatch/SKILL.md §Rate-Limit Fallback Protocol. Self-review is **never** an acceptable fallback. |
| `.claude/agents/av-kit-builder.md:2` | loader | Preserved runtime loader field; local class/provenance stamp outside frontmatter. | name: av-kit-builder |
| `.claude/agents/av-kit-builder.md:3` | loader | Preserved runtime loader field; local class/provenance stamp outside frontmatter. | description: Mechanical-class executor for a single av-kit task.md row per dispatch. Use for well-specified, self-contained mechanical work (design-token swaps, count/reference reconciliation, fixture construction, doc/status sweeps, lint cleanup) that a builder-tier model can complete against an explicit spec. Not for correctness-class work, cross-row reasoning, or any decision gate. |
| `.claude/agents/av-kit-builder.md:4` | loader | Preserved runtime loader field; local class/provenance stamp outside frontmatter. | model: sonnet |
| `.claude/agents/av-kit-builder.md:8` | loader | Preserved runtime loader field; local class/provenance stamp outside frontmatter. | # av-kit-builder |
| `.claude/agents/av-kit-builder.md:10` | loader | Preserved runtime loader field; local class/provenance stamp outside frontmatter. | You are a builder subagent for the av-kit project. You execute **exactly one** task.md |
| `.claude/agents/av-kit-verifier.md:2` | loader | Preserved runtime loader field; local class/provenance stamp outside frontmatter. | name: av-kit-verifier |
| `.claude/agents/av-kit-verifier.md:3` | loader | Preserved runtime loader field; local class/provenance stamp outside frontmatter. | description: Skeptical readonly validator for a single av-kit task.md row. Use to run a row's exact validation command (tests, type-checks, lint, structural gates) in an isolated context and report counts + the receipt path without touching files. Ideal for verbose validation whose output would otherwise flood the coordinator's context. |
| `.claude/agents/av-kit-verifier.md:4` | loader | Preserved runtime loader field; local class/provenance stamp outside frontmatter. | model: sonnet |
| `.claude/agents/av-kit-verifier.md:9` | loader | Preserved runtime loader field; local class/provenance stamp outside frontmatter. | # av-kit-verifier |
| `.claude/agents/av-kit-verifier.md:11` | loader | Preserved runtime loader field; local class/provenance stamp outside frontmatter. | You are a readonly verifier subagent for the av-kit project. You validate **exactly one** |
| `.claude/agents/README.md:9` | operational | Class-based routing, explicit configured-provider boundary, schema syntax or non-model fallback; no snapshot selects a provider. |    - av-kit-builder.md → <your-slug>-builder.md |
| `.claude/agents/README.md:10` | operational | Class-based routing, explicit configured-provider boundary, schema syntax or non-model fallback; no snapshot selects a provider. |    - av-kit-verifier.md → <your-slug>-verifier.md |
| `.claude/agents/README.md:13` | operational | Class-based routing, explicit configured-provider boundary, schema syntax or non-model fallback; no snapshot selects a provider. | 3. Keep the verifier tools allowlist free of Write/Edit. Pin model: per A9 |
| `.claude/agents/README.md:14` | operational | Class-based routing, explicit configured-provider boundary, schema syntax or non-model fallback; no snapshot selects a provider. |    (sonnet is the default builder/verifier pin in this package). |
| `.cursor/agents/av-kit-builder.md:2` | loader | Preserved runtime loader field; local class/provenance stamp outside frontmatter. | name: av-kit-builder |
| `.cursor/agents/av-kit-builder.md:3` | loader | Preserved runtime loader field; local class/provenance stamp outside frontmatter. | description: Mechanical-class executor for a single av-kit task.md row per dispatch. Use for well-specified, self-contained mechanical work (design-token swaps, count/reference reconciliation, fixture construction, doc/status sweeps, lint cleanup) that a builder-tier model can complete against an explicit spec. Not for correctness-class work, cross-row reasoning, or any decision gate. |
| `.cursor/agents/av-kit-builder.md:4` | loader | Preserved runtime loader field; local class/provenance stamp outside frontmatter. | model: cursor-grok-4.6-xhigh |
| `.cursor/agents/av-kit-builder.md:8` | loader | Preserved runtime loader field; local class/provenance stamp outside frontmatter. | # av-kit-builder |
| `.cursor/agents/av-kit-builder.md:10` | loader | Preserved runtime loader field; local class/provenance stamp outside frontmatter. | You are a builder subagent for the av-kit project. You execute **exactly one** task.md |
| `.cursor/agents/av-kit-verifier.md:2` | loader | Preserved runtime loader field; local class/provenance stamp outside frontmatter. | name: av-kit-verifier |
| `.cursor/agents/av-kit-verifier.md:3` | loader | Preserved runtime loader field; local class/provenance stamp outside frontmatter. | description: Skeptical readonly validator for a single av-kit task.md row. Use to run a row's exact validation command (tests, type-checks, lint, structural gates) in an isolated context and report counts + the receipt path without touching files. Ideal for verbose validation whose output would otherwise flood the coordinator's context. |
| `.cursor/agents/av-kit-verifier.md:4` | loader | Preserved runtime loader field; local class/provenance stamp outside frontmatter. | model: composer-2.5-fast |
| `.cursor/agents/av-kit-verifier.md:9` | loader | Preserved runtime loader field; local class/provenance stamp outside frontmatter. | # av-kit-verifier |
| `.cursor/agents/av-kit-verifier.md:11` | loader | Preserved runtime loader field; local class/provenance stamp outside frontmatter. | You are a readonly verifier subagent for the av-kit project. You validate **exactly one** |
| `.cursor/agents/README.md:9` | operational | Class-based routing, explicit configured-provider boundary, schema syntax or non-model fallback; no snapshot selects a provider. |    - av-kit-builder.md → <your-slug>-builder.md |
| `.cursor/agents/README.md:10` | operational | Class-based routing, explicit configured-provider boundary, schema syntax or non-model fallback; no snapshot selects a provider. |    - av-kit-verifier.md → <your-slug>-verifier.md |
| `.cursor/agents/README.md:13` | operational | Class-based routing, explicit configured-provider boundary, schema syntax or non-model fallback; no snapshot selects a provider. | 3. Pin model: to the builder rung you proved (A9 in ADOPTION-QUESTIONS.md). |
| `docs/execution/plans/PLAN-TEMPLATE.md:66` | operational | Class-based routing, explicit configured-provider boundary, schema syntax or non-model fallback; no snapshot selects a provider. | Task tables in task.md may include an optional **builder_model** column (10-col |
| `docs/execution/plans/PLAN-TEMPLATE.md:71` | operational | Class-based routing, explicit configured-provider boundary, schema syntax or non-model fallback; no snapshot selects a provider. | architecture_single_shot is reserved for its own shape and is never a builder. |
| `docs/execution/plans/TASK-TEMPLATE.md:41` | operational | Class-based routing, explicit configured-provider boundary, schema syntax or non-model fallback; no snapshot selects a provider. | > **builder_model** (10-column tables). Legacy 9-column tables remain valid. |
| `docs/execution/plans/TASK-TEMPLATE.md:42` | operational | Class-based routing, explicit configured-provider boundary, schema syntax or non-model fallback; no snapshot selects a provider. | > builder_model names a **capability class** — avkit_builder for mechanical rows, |
| `docs/execution/plans/TASK-TEMPLATE.md:48` | operational | Class-based routing, explicit configured-provider boundary, schema syntax or non-model fallback; no snapshot selects a provider. | > architecture_single_shot is reserved for its own shape and is never a builder. |
| `docs/execution/plans/TASK-TEMPLATE.md:50` | operational | Class-based routing, explicit configured-provider boundary, schema syntax or non-model fallback; no snapshot selects a provider. | &#124; # &#124; Task &#124; Owner &#124; Deliverable &#124; Validation &#124; Depends on &#124; Context strategy &#124; Durable outputs &#124; builder_model &#124; Status &#124; |
| `docs/execution/plans/TASK-TEMPLATE.md:62` | operational | Class-based routing, explicit configured-provider boundary, schema syntax or non-model fallback; no snapshot selects a provider. | > adding delegate_to: av-kit-builder (or av-kit-verifier) **inside the row's Task cell** — |
| `docs/execution/plans/TASK-TEMPLATE.md:90` | operational | Class-based routing, explicit configured-provider boundary, schema syntax or non-model fallback; no snapshot selects a provider. | &#124; H1-5 &#124; Read the handoff template and deterministic latest peer exemplar. &#124; orchestrator &#124; Source-read receipt &#124; view_file: .agent/context/handoffs/TEMPLATE.md plus latest peer handoff &#124; H1-4 &#124; compact_continue &#124; Template/exemplar receipt; compact_continue fallback &#124; avkit_coordinator &#124; [ ] &#124; |
| `docs/execution/plans/TASK-TEMPLATE.md:91` | operational | Class-based routing, explicit configured-provider boundary, schema syntax or non-model fallback; no snapshot selects a provider. | &#124; H1-6 &#124; Create the complete evidence handoff. Product: .agent/context/handoffs/{date}-{project-slug}-{MEU-ID}-handoff.md per MEU. Non-product meus: []: .agent/context/handoffs/{date}-{project-slug}-handoff.md. &#124; orchestrator &#124; Canonical handoff set &#124; rtk proxy uv run python tools/validate_closeout_artifacts.py --handoff {handoff-file} --plan {plan-file} *> C:/Temp/av-kit/handoff-check.txt; $code=$LASTEXITCODE; Get-Content C:/Temp/av-kit/handoff-check.txt; exit $code &#124; H1-5 &#124; compact_continue &#124; Canonical handoff(s); compact_continue fallback &#124; avkit_coordinator &#124; [ ] &#124; |
| `docs/execution/plans/TASK-TEMPLATE.md:95` | operational | Class-based routing, explicit configured-provider boundary, schema syntax or non-model fallback; no snapshot selects a provider. | &#124; H1-7 &#124; Dispatch independent reviewer under EGRESS_PRECEDENCE; loop corrections within ledger limits. &#124; reviewer dispatch / coder corrections &#124; Rolling review &#124; {exact authorized dispatch command with preserved exit} &#124; H1-6b &#124; isolated &#124; Rolling review; durable findings; compact_continue fallback &#124; — &#124; [ ] &#124; |
| `docs/execution/plans/TASK-TEMPLATE.md:100` | operational | Class-based routing, explicit configured-provider boundary, schema syntax or non-model fallback; no snapshot selects a provider. | &#124; H2-2 &#124; Create the full reflection with review churn and Instruction Coverage YAML. &#124; orchestrator &#124; docs/execution/reflections/{date}-{project-slug}-reflection.md &#124; rtk proxy uv run python tools/validate_closeout_artifacts.py --reflection {reflection-file} --reflection-template docs/execution/reflections/TEMPLATE.md --reflection-schema .agent/schemas/reflection.v1.yaml *> C:/Temp/av-kit/reflection-check.txt; $code=$LASTEXITCODE; Get-Content C:/Temp/av-kit/reflection-check.txt; exit $code &#124; H2-1 &#124; compact_continue &#124; Reflection; compact_continue fallback &#124; avkit_coordinator &#124; [ ] &#124; |
| `docs/execution/plans/TASK-TEMPLATE.md:102` | operational | Class-based routing, explicit configured-provider boundary, schema syntax or non-model fallback; no snapshot selects a provider. | &#124; H2-4 &#124; Run complete closeout structural, handoff, approval, and reflection checks. &#124; tester &#124; Passing completion-preflight receipt &#124; rtk proxy uv run python tools/lint_task_contract.py --allowed-builder-classes avkit_builder,avkit_coordinator,avkit_verifier --task docs/execution/plans/{date}-{project-slug}/task.md *> C:/Temp/av-kit/closeout-preflight.txt; $code=$LASTEXITCODE; Get-Content C:/Temp/av-kit/closeout-preflight.txt; exit $code &#124; H2-3 &#124; shared &#124; Closeout receipt &#124; avkit_coordinator &#124; [ ] &#124; |
| `docs/execution/reflections/TEMPLATE.md:59` | operational | Class-based routing, explicit configured-provider boundary, schema syntax or non-model fallback; no snapshot selects a provider. |     <!-- Delegation via .agent/skills/subagent-delegation/SKILL.md (av-kit-builder / av-kit-verifier). --> |
| `GUARDRAILS.md:13` | operational | Class-based routing, explicit configured-provider boundary, schema syntax or non-model fallback; no snapshot selects a provider. | Planning may run a **plan-local read-only verifier** writing only under C:/Temp/av-kit, without repo mutation or product-suite execution. Prove its negative case. Remove unrunnable gate claims rather than refine untested prose; see .agent/docs/verification-principles.md V4. |
| `GUARDRAILS.md:17` | operational | Class-based routing, explicit configured-provider boundary, schema syntax or non-model fallback; no snapshot selects a provider. | Provenance: 2026-05-13 premature execution; 2026-06-13 review-first correction; 2026-07-13 capability split; 2026-09-07 runnable verifier. Procedure: .agent/workflows/create-plan.md Step 5. |
| `PROJECT-PROFILE.md:21` | operational | Class-based routing, explicit configured-provider boundary, schema syntax or non-model fallback; no snapshot selects a provider. | &#124; Subagents + nesting depth (A6) &#124; Cursor Task subtypes av-kit-builder / av-kit-verifier &#124; **Installed; fresh_worker stays none until a live smoke receipt is in verification-log.md.** Isolated rows degrade to compact_continue until then. &#124; |
| `PROJECT-PROFILE.md:33` | operational | Class-based routing, explicit configured-provider boundary, schema syntax or non-model fallback; no snapshot selects a provider. | &#124; Reviewer rung 1 (B1) &#124; Codex CLI (GPT) when authenticated &#124; |
| `PROJECT-PROFILE.md:35` | operational | Class-based routing, explicit configured-provider boundary, schema syntax or non-model fallback; no snapshot selects a provider. | &#124; Reviewer rung 2 / 3 (B3) &#124; none configured &#124; |
| `PROJECT-PROFILE.md:92` | operational | Class-based routing, explicit configured-provider boundary, schema syntax or non-model fallback; no snapshot selects a provider. | &#124; Models: coordinator / builder / router (F5) &#124; Resolve avkit_coordinator, avkit_builder, avkit_verifier, avkit_router from the project overlay with the actual harness. Existing approved bindings are preserved; loader fields are stamped with registry identity. Cursor readonly worker limitation and fresh_worker:none remain until both smoke receipts pass. Independent review uses avkit_independent_reviewer; B3/B4 still govern fallback. &#124; |
| `PROJECT-PROFILE.md:114` | operational | Class-based routing, explicit configured-provider boundary, schema syntax or non-model fallback; no snapshot selects a provider. | - [x] Reviewer chain configured **or** human fallback named (Mat). |
| `PROJECT-PROFILE.md:117` | operational | Class-based routing, explicit configured-provider boundary, schema syntax or non-model fallback; no snapshot selects a provider. | **Confirmed by:** Mat (interview 2026-08-17: Codex-if-available, egress permitted, reviewer-auto, subagents after smoke, Grok builder pin) · **Date:** 2026-08-17 |
| `tools/Invoke-CodexDispatch.ps1:952` | operational | Class-based routing, explicit configured-provider boundary, schema syntax or non-model fallback; no snapshot selects a provider. |         # a 400, which is loud and recoverable. What must not happen is a silent fallback: |
| `tools/Invoke-CodexDispatch.ps1:1448` | operational | Class-based routing, explicit configured-provider boundary, schema syntax or non-model fallback; no snapshot selects a provider. | Model: $Model |
| `tools/Invoke-CodexDispatch.sh:724` | operational | Class-based routing, explicit configured-provider boundary, schema syntax or non-model fallback; no snapshot selects a provider. |     # 400, which is loud and recoverable; what must not happen is a silent fallback that |
| `tools/Invoke-CodexDispatch.sh:1212` | operational | Class-based routing, explicit configured-provider boundary, schema syntax or non-model fallback; no snapshot selects a provider. | Model: $MODEL |

## Input inventory

```json
{
  "schema_version": "routing-census.v1",
  "files": [
    {
      "path": ".agent/context/handoffs/REVIEW-TEMPLATE.md",
      "sha256": "b25b1573cceea83e3e681d3992ab75d40dbe7614b735f5d59e474e9fa3fe946d"
    },
    {
      "path": ".agent/context/handoffs/TEMPLATE.md",
      "sha256": "0a92bc5ab6e05f4cffab2af40bc4255084d9254747e3c822418ad0fcfa5ed53f"
    },
    {
      "path": ".agent/context/harness.local.md",
      "sha256": "d4e3bb252d493d6e7a6671afe8dfeafd9512aa5f4f464e096ac8a459ed79bc59"
    },
    {
      "path": ".agent/docs/agentic-methodology.md",
      "sha256": "62255955b9ec84fa0ef908729cc426fc1d06f12b5ea73d7b95eacd922bc4bb6c"
    },
    {
      "path": ".agent/docs/architecture.md",
      "sha256": "16daedc18fa836af32b9a861bcad5bcaeffc9461e91a0b07b85adcd6a8ce325e"
    },
    {
      "path": ".agent/docs/artifact-naming.md",
      "sha256": "8f9fdf3d3e2b384396d1dd04b71d250b0a302c2a0a2394eaf7525fce304a3378"
    },
    {
      "path": ".agent/docs/claude-cli-fallback-lessons.md",
      "sha256": "10b800d0637391db62e5da2010733d83765642637ff01e1dd1cdf096fa211c9b"
    },
    {
      "path": ".agent/docs/code-quality.md",
      "sha256": "6c44f15c67ab3023e323759ffaed87301664cc5b598b21ec3a32d4367b4a648c"
    },
    {
      "path": ".agent/docs/commands.md",
      "sha256": "c5551522d0c712de473b50d7214b64e5e4baee81e33bf9a7916184f7428eaf34"
    },
    {
      "path": ".agent/docs/context-compression.md",
      "sha256": "7ef457b9f668a0f0dc4bb67968e4c70115fa5fc54a5dd6cc3fc7653f79052536"
    },
    {
      "path": ".agent/docs/context-tool-decision-gate.md",
      "sha256": "1c53891263c9a588fa335ce4c7fc94d392407ca5980b5cf12e3c8f941d54b28d"
    },
    {
      "path": ".agent/docs/development-lifecycle.md",
      "sha256": "7ed39d30c53df3676088882cab4d8e401f62a034739e42a3659d1aedba6b9f29"
    },
    {
      "path": ".agent/docs/diagrams/development-lifecycle-overview.svg",
      "sha256": "328cf401b04c8ecafba9a2c54d78885f52838c2d7c4b909851c6cabfd63f1a84"
    },
    {
      "path": ".agent/docs/emerging-standards.md",
      "sha256": "11599d26c8b7db5ae9e27712dd2b974b2e5e36f7137d95ba7a9f3b5b45a0530a"
    },
    {
      "path": ".agent/docs/harness-profiles.md",
      "sha256": "062a8c8b2e6a0624b0fcfbd10b01e295d9c824faecd23749d36f8ce1d3e65f78"
    },
    {
      "path": ".agent/docs/issue-lifecycle-guide.md",
      "sha256": "1b6dc48c7f5c095be5dd3072331c0d0d7ebf96c112a61462c95d4998491251e5"
    },
    {
      "path": ".agent/docs/macos-setup.md",
      "sha256": "af18c5905b2bc730b8700eb86518d8fb171a86f9244b1b06279f50d4a58b3c61"
    },
    {
      "path": ".agent/docs/model-delegation.md",
      "sha256": "a4765d10da715d6eb9ea20d9cd81dafccc918c9c59b427689fc592326a429659"
    },
    {
      "path": ".agent/docs/model-routing.md",
      "sha256": "a849ba84311804fdf161a4d6b5ea89b48273d886c7474ac49452fc0c1df1fbcf"
    },
    {
      "path": ".agent/docs/natural-writing-guide.md",
      "sha256": "142e08c5999b7dd1135dc5dcdfa9cee8d2c4c8945139cc5ad6a488d8ba61ad08"
    },
    {
      "path": ".agent/docs/output-evidence-policy.md",
      "sha256": "57d28b332d9fe438a200325cf02da595a2b269da7dd9f0aa3143219d29031de6"
    },
    {
      "path": ".agent/docs/prompt-templates.md",
      "sha256": "069ebe52045298fdb89899661f298981d73582ee0a59b0788bfc2cfa9904b2a3"
    },
    {
      "path": ".agent/docs/testing-strategy.md",
      "sha256": "899234e27037746abcdbe1e8b924a09c102bbf6448d28b26a4f2cbf235f7f412"
    },
    {
      "path": ".agent/docs/triage-meu-loop.md",
      "sha256": "832e174d55d7254d08e546a9e694154ed6723895d2f9f8296bb9afcac26132a3"
    },
    {
      "path": ".agent/docs/verification-principles.md",
      "sha256": "9140416e97a58f1f76b187b26da36f875ba2e42316447349bfc3e645902cf9b5"
    },
    {
      "path": ".agent/model-registry.local.json",
      "sha256": "017c22882acdece218501d9e7aff04cd2371f10a09d6eda4f9d1cd5a27d16186"
    },
    {
      "path": ".agent/model-registry.local.yaml",
      "sha256": "8c7da78455a1ec36e6f5b789582bc2c419962539888222bfa94f127bd241c123"
    },
    {
      "path": ".agent/roles/coder.md",
      "sha256": "669977e23e21322d4eefcbf3b72dbc3787306521db15d8a71fa3420e3b627678"
    },
    {
      "path": ".agent/roles/guardrail.md",
      "sha256": "3ecf9ef828f23455dbc206546836533ee7be3b93e496acb81862276f9adb083c"
    },
    {
      "path": ".agent/roles/orchestrator.md",
      "sha256": "2916ad08ce04ed99038abffbdc33ba2b23c655b407225f7c1d03919429df8123"
    },
    {
      "path": ".agent/roles/researcher.md",
      "sha256": "2c76490e6db0adfce191c479cd90cc8aad6bf859a304efd963591c94f4c99bc2"
    },
    {
      "path": ".agent/roles/reviewer.md",
      "sha256": "04f7c1e4dda440efe1ada74cd8dd61a28166b3ac305e84ed72bd3ace3daf3676"
    },
    {
      "path": ".agent/roles/tester.md",
      "sha256": "4311520c0d5f34ce730c32fafa953ed1ea963cdedca2efb546c6313eccac4716"
    },
    {
      "path": ".agent/skills/cli-dispatch/SKILL.md",
      "sha256": "e875799476b38da4efd5ab8e2e7b5f7f70403d173473125a3b1c418d1e92975c"
    },
    {
      "path": ".agent/skills/cli-dispatch/tests/Test-CliDispatch.ps1",
      "sha256": "b57debec4da7f819ed7c7b63cdde694160fd69e7d27724570e3b4cc88544490a"
    },
    {
      "path": ".agent/skills/cli-dispatch/tests/Test-OpenCodePoC.ps1",
      "sha256": "afa1ad752aaf9c994182337e9af268e8aba51f581c90b8feb3980367df17e7ba"
    },
    {
      "path": ".agent/skills/completion-preflight/SKILL.md",
      "sha256": "97cb1fa0600f0333ab1e4a8b314ec265026ea2e5e6a0a716e16558d3794c637b"
    },
    {
      "path": ".agent/skills/deep-research/SKILL.md",
      "sha256": "153c0fa1c2e3e6db22970376b7e939b907bba65d96822749432b281665bea3dc"
    },
    {
      "path": ".agent/skills/deep-research/skills-deep-research/SKILL.md",
      "sha256": "153c0fa1c2e3e6db22970376b7e939b907bba65d96822749432b281665bea3dc"
    },
    {
      "path": ".agent/skills/deep-research-prompting/SKILL.md",
      "sha256": "783b83cbeb2ff63288bf341d7667e41e8b3d59b1f4f26ec6650bb4ebc02431f7"
    },
    {
      "path": ".agent/skills/git-workflow/scripts/agent-commit.ps1",
      "sha256": "13f3cbcd488d198429df96a285fde679b25c350c62b3fdebb49d267656d75a0b"
    },
    {
      "path": ".agent/skills/git-workflow/SKILL.md",
      "sha256": "9fc571215ac5f37a06ba944f8b30ea1895588c2ebdb14dd687b77c024b8707e3"
    },
    {
      "path": ".agent/skills/issue-triage/SKILL.md",
      "sha256": "0f10f0afef7a569bbca3c97f279412331c191c9bea931e6fcb079a6cdf463379"
    },
    {
      "path": ".agent/skills/meu-status/SKILL.md",
      "sha256": "376fd464b7de5da43ca1fb8b315a9379f40e44ee0e6acc0c4fce2b9802b84c9e"
    },
    {
      "path": ".agent/skills/pre-handoff-review/SKILL.md",
      "sha256": "283af5cf8a10146f2c4288f120e6f91bb642e94e22bbdb297701027afd7c6394"
    },
    {
      "path": ".agent/skills/quality-gate/SKILL.md",
      "sha256": "a746b1ef5b1c2256bdae973327352b315ec87ec18e5894764d52e37b6c1ccc82"
    },
    {
      "path": ".agent/skills/README.md",
      "sha256": "b60b804882ba93625eb7d0510c4e216957c5dede745287d24dc4853c75208d67"
    },
    {
      "path": ".agent/skills/session-meta-review/SKILL.md",
      "sha256": "a8be15f0582bd13f8f1ebeed6d9b128fba5c1a7c297d603f64d973959654e6dd"
    },
    {
      "path": ".agent/skills/skill-optimizer/rubric-templates.md",
      "sha256": "102d7798706e8f8d62913cb299bbac3ab4418c0d165428bbf64951e6432d77d8"
    },
    {
      "path": ".agent/skills/skill-optimizer/SKILL.md",
      "sha256": "903d5b47e4d1848b5b9caa5d251f57008e24f9ed8907a091113c8b0b91082367"
    },
    {
      "path": ".agent/skills/subagent-delegation/SKILL.md",
      "sha256": "9e7266e419b5a7e57283af3885232dabc010510bfeaafb0ff1ac9ef7ae759639"
    },
    {
      "path": ".agent/skills/subagent-delegation/verification-log.md",
      "sha256": "0caa6a499ac2b27db5b856aefc2b7009dacf17433039eeb73599e601699dba48"
    },
    {
      "path": ".agent/skills/terminal-preflight/SKILL.md",
      "sha256": "4a471bbf2ec0c3fde1428f387261e35a8540a4e2fac5bc9a714a5c239a9fa500"
    },
    {
      "path": ".agent/skills/timestamp/SKILL.md",
      "sha256": "d7ce7f2bc74622ee5e07d7cab2e9ed0a5947ab756c67f11a892026a1bbae9c73"
    },
    {
      "path": ".agent/templates/BUILD_PLAN-STUB.md",
      "sha256": "c467d692a165e47a8ea600ab7a3e50d93587664c5f9091885b0c305321b8a24e"
    },
    {
      "path": ".agent/templates/HANDOFF-TEMPLATE.md",
      "sha256": "0a92bc5ab6e05f4cffab2af40bc4255084d9254747e3c822418ad0fcfa5ed53f"
    },
    {
      "path": ".agent/templates/PLAN-TEMPLATE.md",
      "sha256": "e9ff78e174d874acf7d58757668943217d4bf30979686bbd1ad5f625eb5995ab"
    },
    {
      "path": ".agent/templates/REFLECTION-TEMPLATE.md",
      "sha256": "8c6d75e1b0299cb6a0655167fe4619c62c4110511ab288efbae6f04b501523d6"
    },
    {
      "path": ".agent/templates/REVIEW-TEMPLATE.md",
      "sha256": "b25b1573cceea83e3e681d3992ab75d40dbe7614b735f5d59e474e9fa3fe946d"
    },
    {
      "path": ".agent/templates/TASK-TEMPLATE.md",
      "sha256": "46f90eb6311d49cde629c7a6b8896848dcb691f4645d154bff9b43b1c17aa5b6"
    },
    {
      "path": ".agent/workflows/cli-dispatch.md",
      "sha256": "583485697752d629534f51c15094a2a3e0f47e0ec577e323e23da87a46a41f97"
    },
    {
      "path": ".agent/workflows/create-plan.md",
      "sha256": "ca1a07802f003e57ff2d06cf1db701fa05d9d137704b8f8046a4ce74dc53b4c0"
    },
    {
      "path": ".agent/workflows/deep-research.md",
      "sha256": "162fc6a36a5f786c7f83a32dae164c6f034f37fd701575e4ac6abc96364cfb5d"
    },
    {
      "path": ".agent/workflows/delegated-plan-creation.md",
      "sha256": "e5efedc53c48c3ca667be9761fae23983196ad496bfa8fa7373ff1bcfe7b199f"
    },
    {
      "path": ".agent/workflows/execution-corrections.md",
      "sha256": "0ac2ea79e603e5874df6ad13b885490a687a9a8ffec86776eb8c0efeccbb31b9"
    },
    {
      "path": ".agent/workflows/execution-critical-review.md",
      "sha256": "f195a80dc059aa7a39c69d16bcf483e37bc6e5b9e6d463c585ca51811fe08a99"
    },
    {
      "path": ".agent/workflows/execution-session.md",
      "sha256": "900818657ca7315eed7a3225d384031fa3b83a41a21e2270fcc5cbfc654971f3"
    },
    {
      "path": ".agent/workflows/inspiration-research.md",
      "sha256": "56b5e493ad7fe9a4222156849651e288474c88af10a9bedb1f811cbbd987e3df"
    },
    {
      "path": ".agent/workflows/issue-triage.md",
      "sha256": "93cc90a4fffe27e36537bd1268c331e31343d58ca748b2c75023435845e9da3a"
    },
    {
      "path": ".agent/workflows/meu-handoff.md",
      "sha256": "f4334e12ad31c561ee01a570b13f81e176d29ada928997cfa59bcbbb993be98c"
    },
    {
      "path": ".agent/workflows/next-project.md",
      "sha256": "d778eb56cb6afed95cb3612a69d229adfda04b57bd93f205a7322b22bfa5c83d"
    },
    {
      "path": ".agent/workflows/orchestrated-delivery.md",
      "sha256": "65fb1442d852e84f32a1f232f6be0afb3e7ff6889f082a4840c419b15a2b3b0d"
    },
    {
      "path": ".agent/workflows/plan-corrections.md",
      "sha256": "36705f90182ad82d878aa40af488ac682ea60b03e171a18a483e264b14b145d4"
    },
    {
      "path": ".agent/workflows/plan-critical-review.md",
      "sha256": "3e645d50ef139c44950a489acffae4fcd83020cbc214ce477eac6eb2267d3d40"
    },
    {
      "path": ".agent/workflows/pre-build-research.md",
      "sha256": "ffc97ee5cc83337e2fabfb7949a21d83211b730e19f0502634af478f884328d8"
    },
    {
      "path": ".agent/workflows/prompts/deep-research/d1-chatgpt.md",
      "sha256": "f7199a9d6fe5b06bd355817a27ae433b58ffbbed6b1e5e11b2c8a9d34c8e7b83"
    },
    {
      "path": ".agent/workflows/prompts/deep-research/d2-gemini.md",
      "sha256": "72e0b8d4fc05dfdf6072c185b2909de7a63268767162776ba6b9d13fdbd73dc5"
    },
    {
      "path": ".agent/workflows/prompts/deep-research/d3-claude.md",
      "sha256": "50f19ff85842d4d1c5fa59772047de1642e3ffe5dc01c4603ac8611b404add5f"
    },
    {
      "path": ".agent/workflows/README.md",
      "sha256": "8ba4a5a247e286f7f0b707dd87d87338a5283ea299833cdb88db814be9ea26c8"
    },
    {
      "path": ".agent/workflows/session-grouping.md",
      "sha256": "0dab4e801588b4b72a912bfe78806ddfc608bbd40414df592246d27ca2942c73"
    },
    {
      "path": ".agent/workflows/session-meta-review.md",
      "sha256": "4e719fb5e58b3e34f63e27b1451e52bfdd273c72d5fd841b5b8f4cdec396c02b"
    },
    {
      "path": ".agent/workflows/skill-optimize.md",
      "sha256": "28b44aee9baa3b885d60971a4aa3bdf64715488fb03c9b0be33e8371d8e707c3"
    },
    {
      "path": ".agent/workflows/tdd-implementation.md",
      "sha256": "fad0c327e7776c71b271e6baeed6ecf58441eef7378eef104d28474889403736"
    },
    {
      "path": ".agent/workflows/validation-review.md",
      "sha256": "a6344741211121b069954b589b33d579f1d3673c61275db77f5c7333804754d3"
    },
    {
      "path": ".claude/agents/av-kit-builder.md",
      "sha256": "5c06cdde45dc919dd0cd20152cae802033aef307e81c135fd9eeb281c995a3bc"
    },
    {
      "path": ".claude/agents/av-kit-verifier.md",
      "sha256": "1286e34d52803033a26e29a3b85349220982f4c480e8862a47aca7841f21dd7e"
    },
    {
      "path": ".claude/agents/README.md",
      "sha256": "44f201923cf5790e7cbbbbb177cbef6cb619fee99f0c903826d7e9e1e6e18784"
    },
    {
      "path": ".cursor/agents/av-kit-builder.md",
      "sha256": "77d4a20a03b86ff0a9cd4ff17b5d7c1b06388dc98d55231b8feb96f5b44cee21"
    },
    {
      "path": ".cursor/agents/av-kit-verifier.md",
      "sha256": "91ca8cfad7bd84daaa7de664fe2780c0792a08d576468569c746ad2ee7e00c2d"
    },
    {
      "path": ".cursor/agents/README.md",
      "sha256": "83883e0803c5bcd433e6890a6dbeb043127ac7d492c01f54d389a864aefeb5ee"
    },
    {
      "path": "AGENTS.md",
      "sha256": "96d191fe6ef5fb6658ee92f593e98a8847dd240fed7b4a369c5bef3c9cd2f583"
    },
    {
      "path": "CLAUDE.md",
      "sha256": "ddb1451b75506273b003aed0ca515156bdb33cc2ba97fa07dea4890b4d7c98ac"
    },
    {
      "path": "docs/execution/plans/PLAN-TEMPLATE.md",
      "sha256": "e9ff78e174d874acf7d58757668943217d4bf30979686bbd1ad5f625eb5995ab"
    },
    {
      "path": "docs/execution/plans/TASK-TEMPLATE.md",
      "sha256": "46f90eb6311d49cde629c7a6b8896848dcb691f4645d154bff9b43b1c17aa5b6"
    },
    {
      "path": "docs/execution/reflections/TEMPLATE.md",
      "sha256": "8c6d75e1b0299cb6a0655167fe4619c62c4110511ab288efbae6f04b501523d6"
    },
    {
      "path": "GUARDRAILS.md",
      "sha256": "326c7322cdff8fb13f000152462de092a93e40aa00d9f1e418ecaf53a03bd8aa"
    },
    {
      "path": "PROJECT-PROFILE.md",
      "sha256": "a85dd0814bd5a34b258be93a379642093d9eee67915f5aa722530b22920d00b0"
    },
    {
      "path": "tools/Invoke-CodexDispatch.ps1",
      "sha256": "e7d085d48d067d7957b3bb784ecfe33b365d2bdeac3f922535fd0a8ffed611a0"
    },
    {
      "path": "tools/Invoke-CodexDispatch.sh",
      "sha256": "ee74fda9f6e23c0b4630aadd2bda6ba37c81cb86149fe48f65aa5b4398e3777f"
    }
  ],
  "matches": [
    {
      "path": ".agent/context/harness.local.md",
      "line": 25,
      "text_sha256": "36ff994c8d868d1efe62e1b8149a17bb340a510d47f121ae0aa2d06b321d6d12",
      "classification": "operational",
      "reason": "Class-based routing, explicit configured-provider boundary, schema syntax or non-model fallback; no snapshot selects a provider."
    },
    {
      "path": ".agent/context/harness.local.md",
      "line": 26,
      "text_sha256": "137384024694c6f130354a3122ebd039dfc631bf4237396a38d49ef40ab0ccd4",
      "classification": "operational",
      "reason": "Class-based routing, explicit configured-provider boundary, schema syntax or non-model fallback; no snapshot selects a provider."
    },
    {
      "path": ".agent/context/harness.local.md",
      "line": 38,
      "text_sha256": "af83f599a23d0a294b16bc83ce19053c73f1ee8826f1b04b4973533979dfda0a",
      "classification": "operational",
      "reason": "Class-based routing, explicit configured-provider boundary, schema syntax or non-model fallback; no snapshot selects a provider."
    },
    {
      "path": ".agent/context/harness.local.md",
      "line": 42,
      "text_sha256": "a06ec884934e39e33aac8d6fdbf1b0c145abb422009680da583035eeb0a9a63c",
      "classification": "operational",
      "reason": "Class-based routing, explicit configured-provider boundary, schema syntax or non-model fallback; no snapshot selects a provider."
    },
    {
      "path": ".agent/context/harness.local.md",
      "line": 44,
      "text_sha256": "a75164240d439f490556b095f0674a104fcfe7ee9527a8b7ea178e61619ae696",
      "classification": "operational",
      "reason": "Class-based routing, explicit configured-provider boundary, schema syntax or non-model fallback; no snapshot selects a provider."
    },
    {
      "path": ".agent/context/harness.local.md",
      "line": 52,
      "text_sha256": "3908174d65925f496f6ad816468560239502aec750f916377f9b8bdfc226145d",
      "classification": "operational",
      "reason": "Class-based routing, explicit configured-provider boundary, schema syntax or non-model fallback; no snapshot selects a provider."
    },
    {
      "path": ".agent/docs/agentic-methodology.md",
      "line": 239,
      "text_sha256": "98116c3826592fff2b03b40098d530c3328079cbf270d44bb792162850a32c8a",
      "classification": "operational",
      "reason": "Class-based routing, explicit configured-provider boundary, schema syntax or non-model fallback; no snapshot selects a provider."
    },
    {
      "path": ".agent/docs/agentic-methodology.md",
      "line": 241,
      "text_sha256": "83301a34934d676e59a2f43708c8914565aa8bc029034946003ffc8dcae09b04",
      "classification": "historical",
      "reason": "Dated June 2026 MEU-243 observation/removed qualifier; current class named in surrounding passage."
    },
    {
      "path": ".agent/docs/agentic-methodology.md",
      "line": 274,
      "text_sha256": "bf02c1716b35434e293f3b7dc3381b8ae83ce401ccbb3e1db2c1e4ce39f67ff1",
      "classification": "operational",
      "reason": "Class-based routing, explicit configured-provider boundary, schema syntax or non-model fallback; no snapshot selects a provider."
    },
    {
      "path": ".agent/docs/artifact-naming.md",
      "line": 63,
      "text_sha256": "85066a0440387bba7275f18bd955b7720c843caddc2881b985cb56f4b8ab9458",
      "classification": "operational",
      "reason": "Class-based routing, explicit configured-provider boundary, schema syntax or non-model fallback; no snapshot selects a provider."
    },
    {
      "path": ".agent/docs/claude-cli-fallback-lessons.md",
      "line": 1,
      "text_sha256": "9768b42ac824c04679474b65f575279287a5588c9f9210f60650a1ddf534af05",
      "classification": "operational",
      "reason": "Class-based routing, explicit configured-provider boundary, schema syntax or non-model fallback; no snapshot selects a provider."
    },
    {
      "path": ".agent/docs/claude-cli-fallback-lessons.md",
      "line": 4,
      "text_sha256": "d2ef515ff4e4ddb004ad43397e03df2ab3e7301330c20ac3c65790493e054320",
      "classification": "operational",
      "reason": "Class-based routing, explicit configured-provider boundary, schema syntax or non-model fallback; no snapshot selects a provider."
    },
    {
      "path": ".agent/docs/claude-cli-fallback-lessons.md",
      "line": 5,
      "text_sha256": "0233dd75db60950f954aaf80d0e99c89cc38cdc3c17b1cb5beacd291ace0cfef",
      "classification": "operational",
      "reason": "Class-based routing, explicit configured-provider boundary, schema syntax or non-model fallback; no snapshot selects a provider."
    },
    {
      "path": ".agent/docs/claude-cli-fallback-lessons.md",
      "line": 8,
      "text_sha256": "30656d4368ced2471ac9ad97551908812351deb6611945b73f64edac7bd4ce84",
      "classification": "operational",
      "reason": "Class-based routing, explicit configured-provider boundary, schema syntax or non-model fallback; no snapshot selects a provider."
    },
    {
      "path": ".agent/docs/claude-cli-fallback-lessons.md",
      "line": 36,
      "text_sha256": "d93135dd9c213d361a2aec911955be3681fab4e72f82dfe0a653d8ba37770939",
      "classification": "historical",
      "reason": "2026-09-14 incident account; current prohibition at top excludes this old fallback."
    },
    {
      "path": ".agent/docs/claude-cli-fallback-lessons.md",
      "line": 153,
      "text_sha256": "ae8d853a8665fe9052ec1fea47b4ad2c5d1d7a32a9e4b9c00dae8718ef3d62d7",
      "classification": "historical",
      "reason": "2026-09-14 incident account; current prohibition at top excludes this old fallback."
    },
    {
      "path": ".agent/docs/commands.md",
      "line": 106,
      "text_sha256": "6033ab15e45f83716f19969655831c8ba43a6469fe31d8b3d6bd90848e407376",
      "classification": "operational",
      "reason": "Class-based routing, explicit configured-provider boundary, schema syntax or non-model fallback; no snapshot selects a provider."
    },
    {
      "path": ".agent/docs/commands.md",
      "line": 125,
      "text_sha256": "5ad898ced23cff2e306bf43a7af6198793bbba0b636ee24d955386dc7630268d",
      "classification": "operational",
      "reason": "Class-based routing, explicit configured-provider boundary, schema syntax or non-model fallback; no snapshot selects a provider."
    },
    {
      "path": ".agent/docs/commands.md",
      "line": 207,
      "text_sha256": "8e6f4996b96a6e5e9053ae7185b7d21258c68950690518698061bab8cc157081",
      "classification": "operational",
      "reason": "Class-based routing, explicit configured-provider boundary, schema syntax or non-model fallback; no snapshot selects a provider."
    },
    {
      "path": ".agent/docs/commands.md",
      "line": 217,
      "text_sha256": "ad93bc0d5a7e1693ce5f99745df15344cc480cc46eeacdb72a94843bf564aed9",
      "classification": "operational",
      "reason": "Class-based routing, explicit configured-provider boundary, schema syntax or non-model fallback; no snapshot selects a provider."
    },
    {
      "path": ".agent/docs/context-compression.md",
      "line": 157,
      "text_sha256": "a136c78b9ca4335b1b81ce15cdf55b7ff2c5ea6a8a95dae44b17160d53f4a4cb",
      "classification": "operational",
      "reason": "Class-based routing, explicit configured-provider boundary, schema syntax or non-model fallback; no snapshot selects a provider."
    },
    {
      "path": ".agent/docs/context-compression.md",
      "line": 196,
      "text_sha256": "d6194bacaf5361b5ff278c0195a734c8bfae0146c69981b68f179aae18333e1a",
      "classification": "operational",
      "reason": "Class-based routing, explicit configured-provider boundary, schema syntax or non-model fallback; no snapshot selects a provider."
    },
    {
      "path": ".agent/docs/context-tool-decision-gate.md",
      "line": 14,
      "text_sha256": "4d5b5867333dd6e3547df8496db290a45955ee0e404a18528ca36802dc70ecda",
      "classification": "operational",
      "reason": "Class-based routing, explicit configured-provider boundary, schema syntax or non-model fallback; no snapshot selects a provider."
    },
    {
      "path": ".agent/docs/development-lifecycle.md",
      "line": 293,
      "text_sha256": "c77800231872cf8b466e314eb2f47f1d3bcdf569be0c75f3d378fa881ef03b00",
      "classification": "operational",
      "reason": "Class-based routing, explicit configured-provider boundary, schema syntax or non-model fallback; no snapshot selects a provider."
    },
    {
      "path": ".agent/docs/development-lifecycle.md",
      "line": 295,
      "text_sha256": "e2b4cd2736ef134cc4d43c6aad4384b03423c5880da2ed6499e7b6c1975dc585",
      "classification": "operational",
      "reason": "Class-based routing, explicit configured-provider boundary, schema syntax or non-model fallback; no snapshot selects a provider."
    },
    {
      "path": ".agent/docs/development-lifecycle.md",
      "line": 493,
      "text_sha256": "57a10f2402c1481b1184197a230a766314fa45e7f95da9e0a8b175f33f09491a",
      "classification": "operational",
      "reason": "Class-based routing, explicit configured-provider boundary, schema syntax or non-model fallback; no snapshot selects a provider."
    },
    {
      "path": ".agent/docs/development-lifecycle.md",
      "line": 783,
      "text_sha256": "1d50c60b141e39ceafe1a012b2f3d3580dcc512888e4d6535149a9fe39258cb4",
      "classification": "historical",
      "reason": "Dated June 2026 MEU-243 observation/removed qualifier; current class named in surrounding passage."
    },
    {
      "path": ".agent/docs/development-lifecycle.md",
      "line": 785,
      "text_sha256": "a18392e6eae3059e9045dd66edf8a7a205c1c177a988f83328e915bed647623b",
      "classification": "historical",
      "reason": "Dated June 2026 MEU-243 observation/removed qualifier; current class named in surrounding passage."
    },
    {
      "path": ".agent/docs/development-lifecycle.md",
      "line": 791,
      "text_sha256": "f07eae14e7f606e5e0e808eadaa88e5d217e2e1e6c226e3bb3430de16d63ad29",
      "classification": "historical",
      "reason": "Dated June 2026 MEU-243 observation/removed qualifier; current class named in surrounding passage."
    },
    {
      "path": ".agent/docs/development-lifecycle.md",
      "line": 876,
      "text_sha256": "051db55d670a322dcbf3f25ac11ab3266233b25065e544b2c0dc0c77c02c3b7d",
      "classification": "operational",
      "reason": "Class-based routing, explicit configured-provider boundary, schema syntax or non-model fallback; no snapshot selects a provider."
    },
    {
      "path": ".agent/docs/emerging-standards.md",
      "line": 249,
      "text_sha256": "ed077d67597ca639a03afb694b5e0c912b2dcd91faa1a48b641583a05908c959",
      "classification": "operational",
      "reason": "Class-based routing, explicit configured-provider boundary, schema syntax or non-model fallback; no snapshot selects a provider."
    },
    {
      "path": ".agent/docs/emerging-standards.md",
      "line": 491,
      "text_sha256": "4bdbc53295d3db22c40d71159717da6371f4a931d6dc293fe8b8e21695064f74",
      "classification": "operational",
      "reason": "Class-based routing, explicit configured-provider boundary, schema syntax or non-model fallback; no snapshot selects a provider."
    },
    {
      "path": ".agent/docs/harness-profiles.md",
      "line": 60,
      "text_sha256": "a2317f552bc5d24dddac402788c46c5331aa729b8ec47caa4352df095305e6d8",
      "classification": "operational",
      "reason": "Class-based routing, explicit configured-provider boundary, schema syntax or non-model fallback; no snapshot selects a provider."
    },
    {
      "path": ".agent/docs/harness-profiles.md",
      "line": 74,
      "text_sha256": "0845e8ac574f91c9c43a29962ea0bd5205a5ff03339aad5b241420e8e3063f52",
      "classification": "operational",
      "reason": "Class-based routing, explicit configured-provider boundary, schema syntax or non-model fallback; no snapshot selects a provider."
    },
    {
      "path": ".agent/docs/harness-profiles.md",
      "line": 75,
      "text_sha256": "003f04f06a9ba669f935a2222f4e63097be63e2ea3652eb5b207e1f1b181fa12",
      "classification": "operational",
      "reason": "Class-based routing, explicit configured-provider boundary, schema syntax or non-model fallback; no snapshot selects a provider."
    },
    {
      "path": ".agent/docs/harness-profiles.md",
      "line": 80,
      "text_sha256": "49c4518d5a50df37ce5ca1c7c07da18efda80cbf4bbd802e02d50aa829337632",
      "classification": "operational",
      "reason": "Class-based routing, explicit configured-provider boundary, schema syntax or non-model fallback; no snapshot selects a provider."
    },
    {
      "path": ".agent/docs/macos-setup.md",
      "line": 262,
      "text_sha256": "e567aa43f897e4edc0e24a06686de3cd965118166fbe89470db954182d1a11ef",
      "classification": "operational",
      "reason": "Class-based routing, explicit configured-provider boundary, schema syntax or non-model fallback; no snapshot selects a provider."
    },
    {
      "path": ".agent/docs/model-delegation.md",
      "line": 1,
      "text_sha256": "e452cca6e5f0bdb6519738ab6cc6d5dfde97ccc3c42c2fb92225db2043dcbf19",
      "classification": "operational",
      "reason": "Class-based routing, explicit configured-provider boundary, schema syntax or non-model fallback; no snapshot selects a provider."
    },
    {
      "path": ".agent/docs/model-delegation.md",
      "line": 3,
      "text_sha256": "02cced293e068ec0602425f5785dc9d995a453d63234517c91748b86404bb213",
      "classification": "operational",
      "reason": "Class-based routing, explicit configured-provider boundary, schema syntax or non-model fallback; no snapshot selects a provider."
    },
    {
      "path": ".agent/docs/model-delegation.md",
      "line": 9,
      "text_sha256": "2b5d5a9412916c0ed318e9f1b4ff5bfcda59909508c45bc77cc1274e6d62bf28",
      "classification": "operational",
      "reason": "Class-based routing, explicit configured-provider boundary, schema syntax or non-model fallback; no snapshot selects a provider."
    },
    {
      "path": ".agent/docs/model-delegation.md",
      "line": 11,
      "text_sha256": "8cdc46f53c3b1bff049f1c66555f5fe8f9359381a74178a690b2a9aa067b758c",
      "classification": "operational",
      "reason": "Class-based routing, explicit configured-provider boundary, schema syntax or non-model fallback; no snapshot selects a provider."
    },
    {
      "path": ".agent/docs/model-delegation.md",
      "line": 22,
      "text_sha256": "fcfc4ce2a6477afd64f7f4e57d3b01a3aa29042e11bc276646e6007e07dd610b",
      "classification": "operational",
      "reason": "Class-based routing, explicit configured-provider boundary, schema syntax or non-model fallback; no snapshot selects a provider."
    },
    {
      "path": ".agent/docs/model-delegation.md",
      "line": 37,
      "text_sha256": "a6dfccd82e231b057dcdd3cec28073e2d183b6721ddcb854082785f9f848a930",
      "classification": "operational",
      "reason": "Class-based routing, explicit configured-provider boundary, schema syntax or non-model fallback; no snapshot selects a provider."
    },
    {
      "path": ".agent/docs/model-delegation.md",
      "line": 38,
      "text_sha256": "a1f3d4c9561937f9752a77846904b628358bf90458235c8cdf2b59fa8f60ab52",
      "classification": "operational",
      "reason": "Class-based routing, explicit configured-provider boundary, schema syntax or non-model fallback; no snapshot selects a provider."
    },
    {
      "path": ".agent/docs/model-delegation.md",
      "line": 39,
      "text_sha256": "1d8fdfc34272d23feacc1835dff7a845340ac7d3d99c329c147d01d5ddd82198",
      "classification": "operational",
      "reason": "Class-based routing, explicit configured-provider boundary, schema syntax or non-model fallback; no snapshot selects a provider."
    },
    {
      "path": ".agent/docs/model-delegation.md",
      "line": 40,
      "text_sha256": "5273e52172ed3b1f91f552f330fe4c6914789dacc241da2f4ab7ff8d5902a772",
      "classification": "operational",
      "reason": "Class-based routing, explicit configured-provider boundary, schema syntax or non-model fallback; no snapshot selects a provider."
    },
    {
      "path": ".agent/docs/model-delegation.md",
      "line": 52,
      "text_sha256": "ea2f259ece9ccdfef0358559a28235d34e4341e93b699b402c1962fc0db0557b",
      "classification": "operational",
      "reason": "Class-based routing, explicit configured-provider boundary, schema syntax or non-model fallback; no snapshot selects a provider."
    },
    {
      "path": ".agent/docs/model-routing.md",
      "line": 9,
      "text_sha256": "6ac808604a4f5697ab26a358aae9f213d66478fb942c686738d38d9078c71280",
      "classification": "operational",
      "reason": "Class-based routing, explicit configured-provider boundary, schema syntax or non-model fallback; no snapshot selects a provider."
    },
    {
      "path": ".agent/docs/model-routing.md",
      "line": 10,
      "text_sha256": "0d430f5e762c710e1f2d251fc80841b32f73d95ba8c153422bf3be12e0e22e5e",
      "classification": "operational",
      "reason": "Class-based routing, explicit configured-provider boundary, schema syntax or non-model fallback; no snapshot selects a provider."
    },
    {
      "path": ".agent/docs/model-routing.md",
      "line": 11,
      "text_sha256": "d3751a0f42e71718c7fb959411596f9ff75172759576de79be679deaff298e27",
      "classification": "operational",
      "reason": "Class-based routing, explicit configured-provider boundary, schema syntax or non-model fallback; no snapshot selects a provider."
    },
    {
      "path": ".agent/docs/model-routing.md",
      "line": 15,
      "text_sha256": "4503f42b2a45e95c3ae822b3263e3080b26e556d58e475802d267be4db1876f2",
      "classification": "operational",
      "reason": "Class-based routing, explicit configured-provider boundary, schema syntax or non-model fallback; no snapshot selects a provider."
    },
    {
      "path": ".agent/docs/model-routing.md",
      "line": 39,
      "text_sha256": "f96d3222294a7be1ef0395f3a15fd5b7071960e6cb6cc271c30c19cbccd6c071",
      "classification": "operational",
      "reason": "Class-based routing, explicit configured-provider boundary, schema syntax or non-model fallback; no snapshot selects a provider."
    },
    {
      "path": ".agent/docs/triage-meu-loop.md",
      "line": 76,
      "text_sha256": "fe5fbe145686dba50033ae6bd7852d45a3b0649086fda00854d2480b0ed0e633",
      "classification": "operational",
      "reason": "Class-based routing, explicit configured-provider boundary, schema syntax or non-model fallback; no snapshot selects a provider."
    },
    {
      "path": ".agent/docs/triage-meu-loop.md",
      "line": 77,
      "text_sha256": "f14bb23ba0d968d3134364f06a63dd6ac8629e9b91885e7adf8535e975ffa2ae",
      "classification": "operational",
      "reason": "Class-based routing, explicit configured-provider boundary, schema syntax or non-model fallback; no snapshot selects a provider."
    },
    {
      "path": ".agent/docs/triage-meu-loop.md",
      "line": 85,
      "text_sha256": "25fa4369a611369ac3792cf2b5263836e22fe89895f04eefa023265f0abc61bb",
      "classification": "operational",
      "reason": "Class-based routing, explicit configured-provider boundary, schema syntax or non-model fallback; no snapshot selects a provider."
    },
    {
      "path": ".agent/docs/triage-meu-loop.md",
      "line": 141,
      "text_sha256": "368fdc4e267cfb2cf7af5365dc5889fe86a4972becebe445567a892e4cf66b59",
      "classification": "operational",
      "reason": "Class-based routing, explicit configured-provider boundary, schema syntax or non-model fallback; no snapshot selects a provider."
    },
    {
      "path": ".agent/docs/verification-principles.md",
      "line": 21,
      "text_sha256": "eb887a6a7686f08ca86ee51d78bc5b6d002fdd64146819d2a0e702486f253ca1",
      "classification": "operational",
      "reason": "Class-based routing, explicit configured-provider boundary, schema syntax or non-model fallback; no snapshot selects a provider."
    },
    {
      "path": ".agent/docs/verification-principles.md",
      "line": 125,
      "text_sha256": "4b5f2b6584661a5cddc3b5e385ceb3b3cac708017c17c22a29ecf57c7e4aceb8",
      "classification": "operational",
      "reason": "Class-based routing, explicit configured-provider boundary, schema syntax or non-model fallback; no snapshot selects a provider."
    },
    {
      "path": ".agent/docs/verification-principles.md",
      "line": 126,
      "text_sha256": "cfb63d3d3144ba2a776973d6e1f4cb38875f449e924a2e882e7daa743fbde445",
      "classification": "operational",
      "reason": "Class-based routing, explicit configured-provider boundary, schema syntax or non-model fallback; no snapshot selects a provider."
    },
    {
      "path": ".agent/docs/verification-principles.md",
      "line": 127,
      "text_sha256": "c0b4240f4980996ccc2043b2ecb2f979fdb9e22e34798378df4a0d0485a2df37",
      "classification": "operational",
      "reason": "Class-based routing, explicit configured-provider boundary, schema syntax or non-model fallback; no snapshot selects a provider."
    },
    {
      "path": ".agent/model-registry.local.json",
      "line": 7,
      "text_sha256": "e4d4833099bb7f583730eba2fda6081397ec86b7c1b243a1232adab768e316db",
      "classification": "binding",
      "reason": "Approved AVKIT_CLASS_MAP catalog binding or compiled mirror; sole model identity authority."
    },
    {
      "path": ".agent/model-registry.local.json",
      "line": 11,
      "text_sha256": "e4bd2698d9c68b8e70a1e743ca6bb5734fef657ba3289ba4efa57c971cedcb85",
      "classification": "binding",
      "reason": "Approved AVKIT_CLASS_MAP catalog binding or compiled mirror; sole model identity authority."
    },
    {
      "path": ".agent/model-registry.local.json",
      "line": 32,
      "text_sha256": "5579d29b448fb4568737c26ece85617dcfa04a1d0844ae3cfad969f30b71c82f",
      "classification": "binding",
      "reason": "Approved AVKIT_CLASS_MAP catalog binding or compiled mirror; sole model identity authority."
    },
    {
      "path": ".agent/model-registry.local.json",
      "line": 36,
      "text_sha256": "e4bd2698d9c68b8e70a1e743ca6bb5734fef657ba3289ba4efa57c971cedcb85",
      "classification": "binding",
      "reason": "Approved AVKIT_CLASS_MAP catalog binding or compiled mirror; sole model identity authority."
    },
    {
      "path": ".agent/model-registry.local.json",
      "line": 58,
      "text_sha256": "c9f89dbddb429903cfde1a530c40e08eef3417017aec93b7af0e01ab8cb6b9f6",
      "classification": "binding",
      "reason": "Approved AVKIT_CLASS_MAP catalog binding or compiled mirror; sole model identity authority."
    },
    {
      "path": ".agent/model-registry.local.json",
      "line": 78,
      "text_sha256": "198b41c6946181707377a9657e7ea1d8a8991f6cbc41ffdd93be32e34fdbc10a",
      "classification": "binding",
      "reason": "Approved AVKIT_CLASS_MAP catalog binding or compiled mirror; sole model identity authority."
    },
    {
      "path": ".agent/model-registry.local.json",
      "line": 94,
      "text_sha256": "e4d4833099bb7f583730eba2fda6081397ec86b7c1b243a1232adab768e316db",
      "classification": "binding",
      "reason": "Approved AVKIT_CLASS_MAP catalog binding or compiled mirror; sole model identity authority."
    },
    {
      "path": ".agent/model-registry.local.json",
      "line": 98,
      "text_sha256": "7b3d1eab9fa5373916d6a240c53e674cd4e50dca64390a50376421870bf5292a",
      "classification": "binding",
      "reason": "Approved AVKIT_CLASS_MAP catalog binding or compiled mirror; sole model identity authority."
    },
    {
      "path": ".agent/model-registry.local.yaml",
      "line": 9,
      "text_sha256": "692c1a565beb73ee34cc1759038419458c3a36f4a8a66a0660ec20f2f24be099",
      "classification": "binding",
      "reason": "Approved AVKIT_CLASS_MAP catalog binding or compiled mirror; sole model identity authority."
    },
    {
      "path": ".agent/model-registry.local.yaml",
      "line": 10,
      "text_sha256": "96f3ace229853e687718bbc63f1d76142a8defd588c9d203ad20418cf541e5b1",
      "classification": "binding",
      "reason": "Approved AVKIT_CLASS_MAP catalog binding or compiled mirror; sole model identity authority."
    },
    {
      "path": ".agent/model-registry.local.yaml",
      "line": 20,
      "text_sha256": "692c1a565beb73ee34cc1759038419458c3a36f4a8a66a0660ec20f2f24be099",
      "classification": "binding",
      "reason": "Approved AVKIT_CLASS_MAP catalog binding or compiled mirror; sole model identity authority."
    },
    {
      "path": ".agent/model-registry.local.yaml",
      "line": 21,
      "text_sha256": "a651f3f867bdf3aac06f43bcc3dccc1503d0c83b594b64d1caaf2b9378187137",
      "classification": "binding",
      "reason": "Approved AVKIT_CLASS_MAP catalog binding or compiled mirror; sole model identity authority."
    },
    {
      "path": ".agent/model-registry.local.yaml",
      "line": 31,
      "text_sha256": "54b187a89ca555f2e323a5e20508f497ae65bd6edbd7cb169e6bead8edf55aa0",
      "classification": "binding",
      "reason": "Approved AVKIT_CLASS_MAP catalog binding or compiled mirror; sole model identity authority."
    },
    {
      "path": ".agent/model-registry.local.yaml",
      "line": 32,
      "text_sha256": "a651f3f867bdf3aac06f43bcc3dccc1503d0c83b594b64d1caaf2b9378187137",
      "classification": "binding",
      "reason": "Approved AVKIT_CLASS_MAP catalog binding or compiled mirror; sole model identity authority."
    },
    {
      "path": ".agent/model-registry.local.yaml",
      "line": 43,
      "text_sha256": "7ff3fd56e0742e024c839311dfd438a39bf6e6fdf5b5a144938a58020e89ad1f",
      "classification": "binding",
      "reason": "Approved AVKIT_CLASS_MAP catalog binding or compiled mirror; sole model identity authority."
    },
    {
      "path": ".agent/model-registry.local.yaml",
      "line": 52,
      "text_sha256": "55944a7f50ea13684a4bb50c21c1b1a82cef52a1ab741e66d8be3ab38ce5163b",
      "classification": "binding",
      "reason": "Approved AVKIT_CLASS_MAP catalog binding or compiled mirror; sole model identity authority."
    },
    {
      "path": ".agent/skills/cli-dispatch/SKILL.md",
      "line": 10,
      "text_sha256": "91ce007474494b2703117b2b3ac46660cc881a2d3f4ae7ca7dcba6e85253c4eb",
      "classification": "operational",
      "reason": "Class-based routing, explicit configured-provider boundary, schema syntax or non-model fallback; no snapshot selects a provider."
    },
    {
      "path": ".agent/skills/cli-dispatch/SKILL.md",
      "line": 176,
      "text_sha256": "e9b22ad9829aed95f1b04d18818326cfb83fa7143deed330359ab910de18a4ff",
      "classification": "operational",
      "reason": "Class-based routing, explicit configured-provider boundary, schema syntax or non-model fallback; no snapshot selects a provider."
    },
    {
      "path": ".agent/skills/cli-dispatch/SKILL.md",
      "line": 286,
      "text_sha256": "9bd9b43fbdea1b7fdf9f6643fed61003352cbfbba6a8da16ceea09277817a53a",
      "classification": "operational",
      "reason": "Class-based routing, explicit configured-provider boundary, schema syntax or non-model fallback; no snapshot selects a provider."
    },
    {
      "path": ".agent/skills/cli-dispatch/SKILL.md",
      "line": 388,
      "text_sha256": "2b27a532e5de7ee7eaf1a7a355ab3a680b0c9a7472fc147d61f38dd8d7b69789",
      "classification": "operational",
      "reason": "Class-based routing, explicit configured-provider boundary, schema syntax or non-model fallback; no snapshot selects a provider."
    },
    {
      "path": ".agent/skills/cli-dispatch/SKILL.md",
      "line": 397,
      "text_sha256": "f524a6ce0f0b15ae35ca8250bd6ef8de7b82c8ef70b68247271fb09370320ca1",
      "classification": "operational",
      "reason": "Class-based routing, explicit configured-provider boundary, schema syntax or non-model fallback; no snapshot selects a provider."
    },
    {
      "path": ".agent/skills/cli-dispatch/SKILL.md",
      "line": 401,
      "text_sha256": "e0e3cd72c91490f9430e0f46493f880d262fd4dd27eccd0a4be052c24953f778",
      "classification": "operational",
      "reason": "Class-based routing, explicit configured-provider boundary, schema syntax or non-model fallback; no snapshot selects a provider."
    },
    {
      "path": ".agent/skills/cli-dispatch/SKILL.md",
      "line": 406,
      "text_sha256": "0f4d40439b24aebaee42baed6dddbb6e2afce1e3afae0ca4ad818fc967df692b",
      "classification": "operational",
      "reason": "Class-based routing, explicit configured-provider boundary, schema syntax or non-model fallback; no snapshot selects a provider."
    },
    {
      "path": ".agent/skills/cli-dispatch/SKILL.md",
      "line": 479,
      "text_sha256": "6d842767aaa7c72b9ae2e2b8203c28da93efd8cd4e0c93528020735a9b95ce55",
      "classification": "operational",
      "reason": "Class-based routing, explicit configured-provider boundary, schema syntax or non-model fallback; no snapshot selects a provider."
    },
    {
      "path": ".agent/skills/cli-dispatch/tests/Test-CliDispatch.ps1",
      "line": 416,
      "text_sha256": "5d27de2bd635dc963aeda5b011ef4baa162baf117e798ded46687b1c5415d3aa",
      "classification": "operational",
      "reason": "Class-based routing, explicit configured-provider boundary, schema syntax or non-model fallback; no snapshot selects a provider."
    },
    {
      "path": ".agent/skills/cli-dispatch/tests/Test-CliDispatch.ps1",
      "line": 418,
      "text_sha256": "e67cfd6cfe1bced7a4bc3d1972ea626fd2c4702532767ab40e3b383299a3270f",
      "classification": "operational",
      "reason": "Class-based routing, explicit configured-provider boundary, schema syntax or non-model fallback; no snapshot selects a provider."
    },
    {
      "path": ".agent/skills/cli-dispatch/tests/Test-OpenCodePoC.ps1",
      "line": 10,
      "text_sha256": "cfd74031462886bfb2b02d1f6e461c44dfba1d9c345dad42d4b0b302efddc5a3",
      "classification": "unconfigured",
      "reason": "Explicit historical provider availability probe (2026-06-01 GA references); never executed or adopted as routing."
    },
    {
      "path": ".agent/skills/cli-dispatch/tests/Test-OpenCodePoC.ps1",
      "line": 11,
      "text_sha256": "69ca37b6e275f36001d914bf5feeaad88f59effef0dd08b7034a04b5f0d644c8",
      "classification": "unconfigured",
      "reason": "Explicit historical provider availability probe (2026-06-01 GA references); never executed or adopted as routing."
    },
    {
      "path": ".agent/skills/cli-dispatch/tests/Test-OpenCodePoC.ps1",
      "line": 45,
      "text_sha256": "c985f06e04411a1817279062c00abd057bfbd5b501cea20bd25e73effdd67601",
      "classification": "unconfigured",
      "reason": "Explicit historical provider availability probe (2026-06-01 GA references); never executed or adopted as routing."
    },
    {
      "path": ".agent/skills/cli-dispatch/tests/Test-OpenCodePoC.ps1",
      "line": 46,
      "text_sha256": "0385ac6cfcc46d4ec6efef2587f93eab27b3d164c1f62b4e690db1d4964b54f2",
      "classification": "unconfigured",
      "reason": "Explicit historical provider availability probe (2026-06-01 GA references); never executed or adopted as routing."
    },
    {
      "path": ".agent/skills/cli-dispatch/tests/Test-OpenCodePoC.ps1",
      "line": 47,
      "text_sha256": "19635c36da32197c777ab0716585729d26dc6fcab8e755d81ba2b0b5aa03272f",
      "classification": "unconfigured",
      "reason": "Explicit historical provider availability probe (2026-06-01 GA references); never executed or adopted as routing."
    },
    {
      "path": ".agent/skills/cli-dispatch/tests/Test-OpenCodePoC.ps1",
      "line": 211,
      "text_sha256": "19c879b6c57d033ced0d0db39955241ded488bd2f587a1752fecd3b4777ae496",
      "classification": "unconfigured",
      "reason": "Explicit historical provider availability probe (2026-06-01 GA references); never executed or adopted as routing."
    },
    {
      "path": ".agent/skills/cli-dispatch/tests/Test-OpenCodePoC.ps1",
      "line": 214,
      "text_sha256": "8529dd5b87ac39dbc72c6bd2b1b216bd43b25cdbce358a4110191729725c1b92",
      "classification": "unconfigured",
      "reason": "Explicit historical provider availability probe (2026-06-01 GA references); never executed or adopted as routing."
    },
    {
      "path": ".agent/skills/cli-dispatch/tests/Test-OpenCodePoC.ps1",
      "line": 222,
      "text_sha256": "0f6afdfc812bd5f2651f8ab4ca7299a5b96c764298db741666803f44fbd6adbb",
      "classification": "unconfigured",
      "reason": "Explicit historical provider availability probe (2026-06-01 GA references); never executed or adopted as routing."
    },
    {
      "path": ".agent/skills/cli-dispatch/tests/Test-OpenCodePoC.ps1",
      "line": 259,
      "text_sha256": "46a5b615ac4cf487bd3aa87dd1d498139b06433973de551d55e21cda990b8d62",
      "classification": "unconfigured",
      "reason": "Explicit historical provider availability probe (2026-06-01 GA references); never executed or adopted as routing."
    },
    {
      "path": ".agent/skills/cli-dispatch/tests/Test-OpenCodePoC.ps1",
      "line": 260,
      "text_sha256": "90a8be1e1788eaa672f01b5f9073fbd8feb77afa7f5f488fda4436da08db76c0",
      "classification": "unconfigured",
      "reason": "Explicit historical provider availability probe (2026-06-01 GA references); never executed or adopted as routing."
    },
    {
      "path": ".agent/skills/cli-dispatch/tests/Test-OpenCodePoC.ps1",
      "line": 261,
      "text_sha256": "d857c935489929a3a4ae36f50c1865c8ea1db4a35cfe8232a10422c9dccbfa65",
      "classification": "unconfigured",
      "reason": "Explicit historical provider availability probe (2026-06-01 GA references); never executed or adopted as routing."
    },
    {
      "path": ".agent/skills/cli-dispatch/tests/Test-OpenCodePoC.ps1",
      "line": 263,
      "text_sha256": "067f389c6b3656b3a43e0990ffcfe75e6559a9562b9db000e2cf9b59d9b1ca28",
      "classification": "unconfigured",
      "reason": "Explicit historical provider availability probe (2026-06-01 GA references); never executed or adopted as routing."
    },
    {
      "path": ".agent/skills/cli-dispatch/tests/Test-OpenCodePoC.ps1",
      "line": 266,
      "text_sha256": "673dcd55db4ef1cb26113458f76851d02c8a8e2ba354cfc8e1f979e60f361fb5",
      "classification": "unconfigured",
      "reason": "Explicit historical provider availability probe (2026-06-01 GA references); never executed or adopted as routing."
    },
    {
      "path": ".agent/skills/cli-dispatch/tests/Test-OpenCodePoC.ps1",
      "line": 267,
      "text_sha256": "ff0f192c8e2e0271b2c78121f4f1ad7ba762a0bd0b990c90243ef8f63e48418e",
      "classification": "unconfigured",
      "reason": "Explicit historical provider availability probe (2026-06-01 GA references); never executed or adopted as routing."
    },
    {
      "path": ".agent/skills/cli-dispatch/tests/Test-OpenCodePoC.ps1",
      "line": 283,
      "text_sha256": "60761d8e17b4c7b1744fe00c7cb5ca501b0fa6f574dd1ac8655a2f4c791898a5",
      "classification": "unconfigured",
      "reason": "Explicit historical provider availability probe (2026-06-01 GA references); never executed or adopted as routing."
    },
    {
      "path": ".agent/skills/cli-dispatch/tests/Test-OpenCodePoC.ps1",
      "line": 285,
      "text_sha256": "aefb75e41b702245edbf772b75e9bd6df681e38af4519398a66890270f2ea7df",
      "classification": "unconfigured",
      "reason": "Explicit historical provider availability probe (2026-06-01 GA references); never executed or adopted as routing."
    },
    {
      "path": ".agent/skills/cli-dispatch/tests/Test-OpenCodePoC.ps1",
      "line": 288,
      "text_sha256": "16e3ad549d6a954f6263a630347b606537e78e0f5eed70fcabad404df2e2a6d6",
      "classification": "unconfigured",
      "reason": "Explicit historical provider availability probe (2026-06-01 GA references); never executed or adopted as routing."
    },
    {
      "path": ".agent/skills/cli-dispatch/tests/Test-OpenCodePoC.ps1",
      "line": 291,
      "text_sha256": "f9b369677e5b09283e05e73a4768590496f9264b6bc615e863a7b3ff7a8d4e3b",
      "classification": "unconfigured",
      "reason": "Explicit historical provider availability probe (2026-06-01 GA references); never executed or adopted as routing."
    },
    {
      "path": ".agent/skills/cli-dispatch/tests/Test-OpenCodePoC.ps1",
      "line": 295,
      "text_sha256": "5427a5c6ea799b7e352a0b03d7005ee1e1512872d07ad0f57a9c2377e4bd792e",
      "classification": "unconfigured",
      "reason": "Explicit historical provider availability probe (2026-06-01 GA references); never executed or adopted as routing."
    },
    {
      "path": ".agent/skills/cli-dispatch/tests/Test-OpenCodePoC.ps1",
      "line": 516,
      "text_sha256": "32d2e73d2ce6b1b95d3b75deaaadce73756a0063d58d6bb3618417b5020d6a7c",
      "classification": "unconfigured",
      "reason": "Explicit historical provider availability probe (2026-06-01 GA references); never executed or adopted as routing."
    },
    {
      "path": ".agent/skills/deep-research-prompting/SKILL.md",
      "line": 32,
      "text_sha256": "5d9148eb42755598671fa3566742abc890560d268b4b99b7c642b1b166aa1342",
      "classification": "operational",
      "reason": "Class-based routing, explicit configured-provider boundary, schema syntax or non-model fallback; no snapshot selects a provider."
    },
    {
      "path": ".agent/skills/pre-handoff-review/SKILL.md",
      "line": 114,
      "text_sha256": "c638c2b4bfa6bb5abbfd68be5ca4e2607e96d528b50f317bd956055651a5c2ce",
      "classification": "operational",
      "reason": "Class-based routing, explicit configured-provider boundary, schema syntax or non-model fallback; no snapshot selects a provider."
    },
    {
      "path": ".agent/skills/README.md",
      "line": 37,
      "text_sha256": "1ccff0a8ade6e5869015716a457a6570d959c1fe6ec2697bc3977a04c2fe4d66",
      "classification": "operational",
      "reason": "Class-based routing, explicit configured-provider boundary, schema syntax or non-model fallback; no snapshot selects a provider."
    },
    {
      "path": ".agent/skills/subagent-delegation/SKILL.md",
      "line": 3,
      "text_sha256": "60c9a5d489820648f3a245e133f837a46cd0ebbfc96fc9883abd1267abe4a326",
      "classification": "operational",
      "reason": "Class-based routing, explicit configured-provider boundary, schema syntax or non-model fallback; no snapshot selects a provider."
    },
    {
      "path": ".agent/skills/subagent-delegation/SKILL.md",
      "line": 13,
      "text_sha256": "54d25b0ddf102fae2ea3d93dd23903d46f88afa4347a7bcbb7e748ca1f939ff5",
      "classification": "operational",
      "reason": "Class-based routing, explicit configured-provider boundary, schema syntax or non-model fallback; no snapshot selects a provider."
    },
    {
      "path": ".agent/skills/subagent-delegation/SKILL.md",
      "line": 14,
      "text_sha256": "1e58d4203f766d098a9642316c7b6cdc9537436007eb465f8ecbebbcbb70a1e9",
      "classification": "operational",
      "reason": "Class-based routing, explicit configured-provider boundary, schema syntax or non-model fallback; no snapshot selects a provider."
    },
    {
      "path": ".agent/skills/subagent-delegation/SKILL.md",
      "line": 18,
      "text_sha256": "f38aec3d9871dbd23a52fcf3ac7bc3361c0a424a68c27f3a69a87aae9e04a682",
      "classification": "operational",
      "reason": "Class-based routing, explicit configured-provider boundary, schema syntax or non-model fallback; no snapshot selects a provider."
    },
    {
      "path": ".agent/skills/subagent-delegation/SKILL.md",
      "line": 23,
      "text_sha256": "5409cc78da5522913d44938f1702ee1474edaf778ac752a8f597517a7d03ce16",
      "classification": "operational",
      "reason": "Class-based routing, explicit configured-provider boundary, schema syntax or non-model fallback; no snapshot selects a provider."
    },
    {
      "path": ".agent/skills/subagent-delegation/SKILL.md",
      "line": 49,
      "text_sha256": "093a71b7eb60f3bbf0b50a2852aada5356be9631d0cacfbfa9d8ebbf2ef659a6",
      "classification": "operational",
      "reason": "Class-based routing, explicit configured-provider boundary, schema syntax or non-model fallback; no snapshot selects a provider."
    },
    {
      "path": ".agent/skills/subagent-delegation/SKILL.md",
      "line": 59,
      "text_sha256": "5dd4194ec751cf0c7f6577992d3890595df7194ddb6d36aec7c9ec8a7e46c2eb",
      "classification": "operational",
      "reason": "Class-based routing, explicit configured-provider boundary, schema syntax or non-model fallback; no snapshot selects a provider."
    },
    {
      "path": ".agent/skills/subagent-delegation/SKILL.md",
      "line": 60,
      "text_sha256": "8262e4ae879485063f4a9c1fac786d1e66e55bca2291cc4d5cacc693b8b30515",
      "classification": "operational",
      "reason": "Class-based routing, explicit configured-provider boundary, schema syntax or non-model fallback; no snapshot selects a provider."
    },
    {
      "path": ".agent/skills/subagent-delegation/SKILL.md",
      "line": 75,
      "text_sha256": "7ae4dd62e1c0734f7c252f6f42fb92b84465b0cb8d1db1c527dda10c7fb35f9b",
      "classification": "operational",
      "reason": "Class-based routing, explicit configured-provider boundary, schema syntax or non-model fallback; no snapshot selects a provider."
    },
    {
      "path": ".agent/skills/subagent-delegation/SKILL.md",
      "line": 76,
      "text_sha256": "04a2849c04a97d753084f6905491ace4a210923d293eb14e6ea6b9c937e4e514",
      "classification": "operational",
      "reason": "Class-based routing, explicit configured-provider boundary, schema syntax or non-model fallback; no snapshot selects a provider."
    },
    {
      "path": ".agent/skills/subagent-delegation/SKILL.md",
      "line": 77,
      "text_sha256": "823ce81310c23c9fa36f4c1b45e01f5f6d9af46c9b7da435401b7c055d05d0c2",
      "classification": "operational",
      "reason": "Class-based routing, explicit configured-provider boundary, schema syntax or non-model fallback; no snapshot selects a provider."
    },
    {
      "path": ".agent/skills/subagent-delegation/SKILL.md",
      "line": 127,
      "text_sha256": "b99bf128b075be81c1e965bc50a5f5383b7f848a6c727d575673e0d074697d37",
      "classification": "operational",
      "reason": "Class-based routing, explicit configured-provider boundary, schema syntax or non-model fallback; no snapshot selects a provider."
    },
    {
      "path": ".agent/skills/subagent-delegation/SKILL.md",
      "line": 130,
      "text_sha256": "0ec34b23bfe79207ab310957e29bc8c0241cab2f59c91b231385230447c1a12a",
      "classification": "operational",
      "reason": "Class-based routing, explicit configured-provider boundary, schema syntax or non-model fallback; no snapshot selects a provider."
    },
    {
      "path": ".agent/skills/subagent-delegation/SKILL.md",
      "line": 132,
      "text_sha256": "febd1c728ece440fde70ab4e72b01843be281fa8ecf0b8757170d4097e6268d6",
      "classification": "operational",
      "reason": "Class-based routing, explicit configured-provider boundary, schema syntax or non-model fallback; no snapshot selects a provider."
    },
    {
      "path": ".agent/skills/subagent-delegation/verification-log.md",
      "line": 3,
      "text_sha256": "3c6d889e8b7e451117d8ef25acfeb7d707b830b2c8c1c403e6e7ee110151cc6f",
      "classification": "historical",
      "reason": "Protected dated 2026-09-02/11 worker smoke observation; immutable evidence, no capability promotion."
    },
    {
      "path": ".agent/skills/subagent-delegation/verification-log.md",
      "line": 11,
      "text_sha256": "9ec2362cbd1a3d158bd3562bab12e451324fa4bf7016798ab370db66064b3c5e",
      "classification": "historical",
      "reason": "Protected dated 2026-09-02/11 worker smoke observation; immutable evidence, no capability promotion."
    },
    {
      "path": ".agent/skills/subagent-delegation/verification-log.md",
      "line": 12,
      "text_sha256": "f055c6004d064a87cfdf0551766583e61b1390c58c44e8dde3aeec0ba115a20b",
      "classification": "historical",
      "reason": "Protected dated 2026-09-02/11 worker smoke observation; immutable evidence, no capability promotion."
    },
    {
      "path": ".agent/skills/subagent-delegation/verification-log.md",
      "line": 20,
      "text_sha256": "507d661a84c3085bcfa4a66fc1df712a6af04d90846668abd379097dca6459ef",
      "classification": "historical",
      "reason": "Protected dated 2026-09-02/11 worker smoke observation; immutable evidence, no capability promotion."
    },
    {
      "path": ".agent/skills/subagent-delegation/verification-log.md",
      "line": 23,
      "text_sha256": "bef56acb41b66f6cb1b484dc08b19f7a1116743c86cd33b7d6d589d76a48b146",
      "classification": "historical",
      "reason": "Protected dated 2026-09-02/11 worker smoke observation; immutable evidence, no capability promotion."
    },
    {
      "path": ".agent/skills/subagent-delegation/verification-log.md",
      "line": 26,
      "text_sha256": "59620a9135112f0616b2b613b48a7bdd0b88125c7ef2033f3763c2fdd9e64747",
      "classification": "historical",
      "reason": "Protected dated 2026-09-02/11 worker smoke observation; immutable evidence, no capability promotion."
    },
    {
      "path": ".agent/skills/subagent-delegation/verification-log.md",
      "line": 28,
      "text_sha256": "acacc01377470d60e85fd6d72c3e67d5a777ae4f93c9ada4b229346c265a1c9e",
      "classification": "historical",
      "reason": "Protected dated 2026-09-02/11 worker smoke observation; immutable evidence, no capability promotion."
    },
    {
      "path": ".agent/skills/subagent-delegation/verification-log.md",
      "line": 29,
      "text_sha256": "516c3437caeef7f7c4b4f6ddf4884b45751066da049809f5fb80a1c93e2dbf6a",
      "classification": "historical",
      "reason": "Protected dated 2026-09-02/11 worker smoke observation; immutable evidence, no capability promotion."
    },
    {
      "path": ".agent/skills/subagent-delegation/verification-log.md",
      "line": 40,
      "text_sha256": "092e2d2e66c574da834c4bd1003888494a7e719d8eeb09b3f094ec244b5e6230",
      "classification": "historical",
      "reason": "Protected dated 2026-09-02/11 worker smoke observation; immutable evidence, no capability promotion."
    },
    {
      "path": ".agent/skills/subagent-delegation/verification-log.md",
      "line": 45,
      "text_sha256": "db9e6310f6e77ff2256bc3f586773c56396dd30b62a51e1feea3d43fef8a4148",
      "classification": "historical",
      "reason": "Protected dated 2026-09-02/11 worker smoke observation; immutable evidence, no capability promotion."
    },
    {
      "path": ".agent/skills/subagent-delegation/verification-log.md",
      "line": 52,
      "text_sha256": "4024a3f2086b84aa9a7e634f4bdd59b534cea48a81273597832eeb3c56947e24",
      "classification": "historical",
      "reason": "Protected dated 2026-09-02/11 worker smoke observation; immutable evidence, no capability promotion."
    },
    {
      "path": ".agent/skills/subagent-delegation/verification-log.md",
      "line": 53,
      "text_sha256": "104a36baaf43ed01301175ea0cf4bc4f9d130005b9c453faf7a594cfe93f144b",
      "classification": "historical",
      "reason": "Protected dated 2026-09-02/11 worker smoke observation; immutable evidence, no capability promotion."
    },
    {
      "path": ".agent/skills/subagent-delegation/verification-log.md",
      "line": 58,
      "text_sha256": "264f76daa346c752652ce0cec110097b64d55af7f9bd195ecb5163f3e988feee",
      "classification": "historical",
      "reason": "Protected dated 2026-09-02/11 worker smoke observation; immutable evidence, no capability promotion."
    },
    {
      "path": ".agent/skills/subagent-delegation/verification-log.md",
      "line": 61,
      "text_sha256": "e4be7bb3514931cba669ab73a798930cb49f522270c3c9087aa2b0f4793efdab",
      "classification": "historical",
      "reason": "Protected dated 2026-09-02/11 worker smoke observation; immutable evidence, no capability promotion."
    },
    {
      "path": ".agent/skills/subagent-delegation/verification-log.md",
      "line": 62,
      "text_sha256": "a34f112288f04eb5f8df87479a6f0f249b65dd8be0f63b7d2f0f76869f245f93",
      "classification": "historical",
      "reason": "Protected dated 2026-09-02/11 worker smoke observation; immutable evidence, no capability promotion."
    },
    {
      "path": ".agent/skills/subagent-delegation/verification-log.md",
      "line": 63,
      "text_sha256": "9a639866c6a7933fe19bb87e1938c20de72191a40563b9cc6a0644091803c643",
      "classification": "historical",
      "reason": "Protected dated 2026-09-02/11 worker smoke observation; immutable evidence, no capability promotion."
    },
    {
      "path": ".agent/skills/subagent-delegation/verification-log.md",
      "line": 64,
      "text_sha256": "0f6983da45b5bed2608f1366242e8c961c407bf34ee0218069cbfdff0245859a",
      "classification": "historical",
      "reason": "Protected dated 2026-09-02/11 worker smoke observation; immutable evidence, no capability promotion."
    },
    {
      "path": ".agent/skills/subagent-delegation/verification-log.md",
      "line": 67,
      "text_sha256": "fddc3f2dd6e045b8466ffb70b1b5ab86183bc6d49186e55a27b218d115e6c771",
      "classification": "historical",
      "reason": "Protected dated 2026-09-02/11 worker smoke observation; immutable evidence, no capability promotion."
    },
    {
      "path": ".agent/skills/subagent-delegation/verification-log.md",
      "line": 68,
      "text_sha256": "e8f7b94a80502c1884e5ef40b7c49d26105c2416df426b83ce27009cab908f83",
      "classification": "historical",
      "reason": "Protected dated 2026-09-02/11 worker smoke observation; immutable evidence, no capability promotion."
    },
    {
      "path": ".agent/skills/subagent-delegation/verification-log.md",
      "line": 79,
      "text_sha256": "fa075e2acaa01c883a157899367365b8a2020589c04a762df55cb4b8cfcb3f3d",
      "classification": "historical",
      "reason": "Protected dated 2026-09-02/11 worker smoke observation; immutable evidence, no capability promotion."
    },
    {
      "path": ".agent/skills/subagent-delegation/verification-log.md",
      "line": 82,
      "text_sha256": "6150fec934fedf2aa67569307bc5fbe1bae724616a35b473be61eb860a19bff6",
      "classification": "historical",
      "reason": "Protected dated 2026-09-02/11 worker smoke observation; immutable evidence, no capability promotion."
    },
    {
      "path": ".agent/skills/subagent-delegation/verification-log.md",
      "line": 83,
      "text_sha256": "3b40fee6fc4663cf08dccec1027fe24d15a7f7873523474a31b1bea26394ff11",
      "classification": "historical",
      "reason": "Protected dated 2026-09-02/11 worker smoke observation; immutable evidence, no capability promotion."
    },
    {
      "path": ".agent/skills/subagent-delegation/verification-log.md",
      "line": 86,
      "text_sha256": "d8adf6c16d979c4f84ca1a23475ce669aa1dbff55531020b2bf096ad6e1d3e78",
      "classification": "historical",
      "reason": "Protected dated 2026-09-02/11 worker smoke observation; immutable evidence, no capability promotion."
    },
    {
      "path": ".agent/skills/subagent-delegation/verification-log.md",
      "line": 96,
      "text_sha256": "f94559cbadb01bebefe4a60645a148cb9838a4204dfedea07b94253de19004e7",
      "classification": "historical",
      "reason": "Protected dated 2026-09-02/11 worker smoke observation; immutable evidence, no capability promotion."
    },
    {
      "path": ".agent/skills/subagent-delegation/verification-log.md",
      "line": 101,
      "text_sha256": "973801db3b5e11795c2b202e273ec8aef46853dbc2c73fd7a84a296b25dc6dda",
      "classification": "historical",
      "reason": "Protected dated 2026-09-02/11 worker smoke observation; immutable evidence, no capability promotion."
    },
    {
      "path": ".agent/skills/subagent-delegation/verification-log.md",
      "line": 102,
      "text_sha256": "59da9f3a792f1a721c6cc3759d6e1505d5fe1bb4eb4472ee6ce8e399ad66a3ea",
      "classification": "historical",
      "reason": "Protected dated 2026-09-02/11 worker smoke observation; immutable evidence, no capability promotion."
    },
    {
      "path": ".agent/skills/subagent-delegation/verification-log.md",
      "line": 105,
      "text_sha256": "5815952fa9cbf6a997ffade35b8dc5530b703d8f29adf4022ac5b3c9d355f980",
      "classification": "historical",
      "reason": "Protected dated 2026-09-02/11 worker smoke observation; immutable evidence, no capability promotion."
    },
    {
      "path": ".agent/templates/PLAN-TEMPLATE.md",
      "line": 66,
      "text_sha256": "9ddf1af8e58ee7d4dbdd82dddfb401a7b36138eba5cdae7281d97cde6849c995",
      "classification": "operational",
      "reason": "Class-based routing, explicit configured-provider boundary, schema syntax or non-model fallback; no snapshot selects a provider."
    },
    {
      "path": ".agent/templates/PLAN-TEMPLATE.md",
      "line": 71,
      "text_sha256": "862550a4d7e457e532ae60e81eac99e1dbe622da86d345f0844b851a68bb89ca",
      "classification": "operational",
      "reason": "Class-based routing, explicit configured-provider boundary, schema syntax or non-model fallback; no snapshot selects a provider."
    },
    {
      "path": ".agent/templates/REFLECTION-TEMPLATE.md",
      "line": 59,
      "text_sha256": "4b0c33651b9679013eabf15ab72f0e6b76bfb2461c7605c84c5283c66a429713",
      "classification": "operational",
      "reason": "Class-based routing, explicit configured-provider boundary, schema syntax or non-model fallback; no snapshot selects a provider."
    },
    {
      "path": ".agent/templates/TASK-TEMPLATE.md",
      "line": 41,
      "text_sha256": "4fb38e13247f3e15b2728aaefe23c24a951488fbf8c190f6746fe6d0ceada8a2",
      "classification": "operational",
      "reason": "Class-based routing, explicit configured-provider boundary, schema syntax or non-model fallback; no snapshot selects a provider."
    },
    {
      "path": ".agent/templates/TASK-TEMPLATE.md",
      "line": 42,
      "text_sha256": "423d0d3a5f3c5e9ce0f8702262cc6e52baacd76e4f08542959f4ff702966fa88",
      "classification": "operational",
      "reason": "Class-based routing, explicit configured-provider boundary, schema syntax or non-model fallback; no snapshot selects a provider."
    },
    {
      "path": ".agent/templates/TASK-TEMPLATE.md",
      "line": 48,
      "text_sha256": "6e601de15f379957473b397af9e7bd7047c362a05da429ecbfe0aad8447377df",
      "classification": "operational",
      "reason": "Class-based routing, explicit configured-provider boundary, schema syntax or non-model fallback; no snapshot selects a provider."
    },
    {
      "path": ".agent/templates/TASK-TEMPLATE.md",
      "line": 50,
      "text_sha256": "1fcd9b2ca012a2229633ec4f9187a956d382a5bbe44fa8b31aaa9d08f1b4ea17",
      "classification": "operational",
      "reason": "Class-based routing, explicit configured-provider boundary, schema syntax or non-model fallback; no snapshot selects a provider."
    },
    {
      "path": ".agent/templates/TASK-TEMPLATE.md",
      "line": 62,
      "text_sha256": "1768cd4d6435947748f5375e6e2a046ecc52b17c34eac1bdb1bf743a215eb98a",
      "classification": "operational",
      "reason": "Class-based routing, explicit configured-provider boundary, schema syntax or non-model fallback; no snapshot selects a provider."
    },
    {
      "path": ".agent/templates/TASK-TEMPLATE.md",
      "line": 90,
      "text_sha256": "cc175bc6f7e40ac4dab752b81702ae447d1a7b4c8866f97c06111327af643a53",
      "classification": "operational",
      "reason": "Class-based routing, explicit configured-provider boundary, schema syntax or non-model fallback; no snapshot selects a provider."
    },
    {
      "path": ".agent/templates/TASK-TEMPLATE.md",
      "line": 91,
      "text_sha256": "d5290d67f2bb20f5e5f6cd79566ba976004269b3997acba915d0f0a244e97230",
      "classification": "operational",
      "reason": "Class-based routing, explicit configured-provider boundary, schema syntax or non-model fallback; no snapshot selects a provider."
    },
    {
      "path": ".agent/templates/TASK-TEMPLATE.md",
      "line": 95,
      "text_sha256": "47c1272548d9369deccf8670d1d79dec2100f0c073ba31dc321acdb9482b52fb",
      "classification": "operational",
      "reason": "Class-based routing, explicit configured-provider boundary, schema syntax or non-model fallback; no snapshot selects a provider."
    },
    {
      "path": ".agent/templates/TASK-TEMPLATE.md",
      "line": 100,
      "text_sha256": "d5980f1aaf45ce490ffb7aa0daeeb077ea68b76e85734fd3b74b864ef998a260",
      "classification": "operational",
      "reason": "Class-based routing, explicit configured-provider boundary, schema syntax or non-model fallback; no snapshot selects a provider."
    },
    {
      "path": ".agent/templates/TASK-TEMPLATE.md",
      "line": 102,
      "text_sha256": "296cec867a8873667f5cffd17b44b336b7e5bdde2e3babdf55ae07509c121ef0",
      "classification": "operational",
      "reason": "Class-based routing, explicit configured-provider boundary, schema syntax or non-model fallback; no snapshot selects a provider."
    },
    {
      "path": ".agent/workflows/cli-dispatch.md",
      "line": 11,
      "text_sha256": "91ce007474494b2703117b2b3ac46660cc881a2d3f4ae7ca7dcba6e85253c4eb",
      "classification": "operational",
      "reason": "Class-based routing, explicit configured-provider boundary, schema syntax or non-model fallback; no snapshot selects a provider."
    },
    {
      "path": ".agent/workflows/cli-dispatch.md",
      "line": 48,
      "text_sha256": "15ef921ff8c2330ee943c189eec6c6c8da3a508d4154e6b93180c160c5be26ea",
      "classification": "operational",
      "reason": "Class-based routing, explicit configured-provider boundary, schema syntax or non-model fallback; no snapshot selects a provider."
    },
    {
      "path": ".agent/workflows/cli-dispatch.md",
      "line": 49,
      "text_sha256": "55d564594cbd4ce29d52bed0bdad7c80a25e401aa675cfd0c2c7b1d2c7c59fe7",
      "classification": "operational",
      "reason": "Class-based routing, explicit configured-provider boundary, schema syntax or non-model fallback; no snapshot selects a provider."
    },
    {
      "path": ".agent/workflows/cli-dispatch.md",
      "line": 50,
      "text_sha256": "6bc15b0e3f7f4ca2918de2c52b14cfe5efd989452c8463bea63228f8802077d6",
      "classification": "operational",
      "reason": "Class-based routing, explicit configured-provider boundary, schema syntax or non-model fallback; no snapshot selects a provider."
    },
    {
      "path": ".agent/workflows/cli-dispatch.md",
      "line": 188,
      "text_sha256": "ce7c44f3114bb219bec4487b4ea092104e0d35e41152751a1cadec7541ea6771",
      "classification": "operational",
      "reason": "Class-based routing, explicit configured-provider boundary, schema syntax or non-model fallback; no snapshot selects a provider."
    },
    {
      "path": ".agent/workflows/cli-dispatch.md",
      "line": 233,
      "text_sha256": "14b36d848b5bd576b11cc47ea5ad746affe81fb8cf5a744d7f74f4e477298aac",
      "classification": "operational",
      "reason": "Class-based routing, explicit configured-provider boundary, schema syntax or non-model fallback; no snapshot selects a provider."
    },
    {
      "path": ".agent/workflows/cli-dispatch.md",
      "line": 239,
      "text_sha256": "8a49da3e9f7d6e2ede7cf5686baeab88cebe966f0b8b215861afd7bb2663520a",
      "classification": "operational",
      "reason": "Class-based routing, explicit configured-provider boundary, schema syntax or non-model fallback; no snapshot selects a provider."
    },
    {
      "path": ".agent/workflows/cli-dispatch.md",
      "line": 245,
      "text_sha256": "fe3dd815229898faf40b0ed979f757d8f59da0e08c35888eede559ecab885af6",
      "classification": "operational",
      "reason": "Class-based routing, explicit configured-provider boundary, schema syntax or non-model fallback; no snapshot selects a provider."
    },
    {
      "path": ".agent/workflows/create-plan.md",
      "line": 192,
      "text_sha256": "0e0eb66be75fd3d4c2a83b6137abe29fa8e8b8489cbb84d66d44a0f03b3a2415",
      "classification": "operational",
      "reason": "Class-based routing, explicit configured-provider boundary, schema syntax or non-model fallback; no snapshot selects a provider."
    },
    {
      "path": ".agent/workflows/create-plan.md",
      "line": 198,
      "text_sha256": "2c767228ba86e406801c7c5fa22bfeaf54bc2321224c07719f0ba2578135baac",
      "classification": "operational",
      "reason": "Class-based routing, explicit configured-provider boundary, schema syntax or non-model fallback; no snapshot selects a provider."
    },
    {
      "path": ".agent/workflows/create-plan.md",
      "line": 311,
      "text_sha256": "e17ebe38683867199649521360c216249822f9759cacc15174a89b3272bafa75",
      "classification": "operational",
      "reason": "Class-based routing, explicit configured-provider boundary, schema syntax or non-model fallback; no snapshot selects a provider."
    },
    {
      "path": ".agent/workflows/create-plan.md",
      "line": 365,
      "text_sha256": "9891b4f2431d2c449f4a66299257cbc0f8b235592d5c9bcc98a9e78b0f21a129",
      "classification": "operational",
      "reason": "Class-based routing, explicit configured-provider boundary, schema syntax or non-model fallback; no snapshot selects a provider."
    },
    {
      "path": ".agent/workflows/create-plan.md",
      "line": 370,
      "text_sha256": "68411eb145d29c7948b429f614b5a040599ed473d9f75eec51c9bdf3ee616b6b",
      "classification": "operational",
      "reason": "Class-based routing, explicit configured-provider boundary, schema syntax or non-model fallback; no snapshot selects a provider."
    },
    {
      "path": ".agent/workflows/create-plan.md",
      "line": 479,
      "text_sha256": "a7606e3fe43fb89d453d30d03964d4808fd9b32ccc2e1d6a9b6626c127ad3f01",
      "classification": "operational",
      "reason": "Class-based routing, explicit configured-provider boundary, schema syntax or non-model fallback; no snapshot selects a provider."
    },
    {
      "path": ".agent/workflows/create-plan.md",
      "line": 480,
      "text_sha256": "2521a8cb93ec323fb191286d28da4943a4ce5cd1ffaea102f56105bb9213e1e0",
      "classification": "operational",
      "reason": "Class-based routing, explicit configured-provider boundary, schema syntax or non-model fallback; no snapshot selects a provider."
    },
    {
      "path": ".agent/workflows/create-plan.md",
      "line": 488,
      "text_sha256": "a23ac67ae169b522c50d05ecfe58123f4b093a3880f95ed1d95bb3afb4ca6d6a",
      "classification": "operational",
      "reason": "Class-based routing, explicit configured-provider boundary, schema syntax or non-model fallback; no snapshot selects a provider."
    },
    {
      "path": ".agent/workflows/create-plan.md",
      "line": 566,
      "text_sha256": "4f8e6cdadc12c755ffcb83753e2a1007dae2780ef552b8fbcc59449f880bdd13",
      "classification": "operational",
      "reason": "Class-based routing, explicit configured-provider boundary, schema syntax or non-model fallback; no snapshot selects a provider."
    },
    {
      "path": ".agent/workflows/delegated-plan-creation.md",
      "line": 166,
      "text_sha256": "8337687896435e94adbbdc3fabcb17b2d6d39228224a6d6568f7ecaf75a03ee4",
      "classification": "operational",
      "reason": "Class-based routing, explicit configured-provider boundary, schema syntax or non-model fallback; no snapshot selects a provider."
    },
    {
      "path": ".agent/workflows/delegated-plan-creation.md",
      "line": 170,
      "text_sha256": "c2387ff3ac7966416d28456afa6e75197c7abd2355ce4a4ba1cda96c66d19b70",
      "classification": "operational",
      "reason": "Class-based routing, explicit configured-provider boundary, schema syntax or non-model fallback; no snapshot selects a provider."
    },
    {
      "path": ".agent/workflows/delegated-plan-creation.md",
      "line": 357,
      "text_sha256": "d36ce6e4de0b46ef67bfdd054165ae7b8d35a8813c2150034dcee14c3f1ebd48",
      "classification": "operational",
      "reason": "Class-based routing, explicit configured-provider boundary, schema syntax or non-model fallback; no snapshot selects a provider."
    },
    {
      "path": ".agent/workflows/execution-session.md",
      "line": 97,
      "text_sha256": "1ad7905862bbe359667c84632ff4b2e4fb4c0ae4c877094d3678410a8ef7d2c4",
      "classification": "operational",
      "reason": "Class-based routing, explicit configured-provider boundary, schema syntax or non-model fallback; no snapshot selects a provider."
    },
    {
      "path": ".agent/workflows/execution-session.md",
      "line": 183,
      "text_sha256": "9ca29595008eacb222bfd8ced7b925607d628c3a4e8d5eb14dca3a0c5539e8f2",
      "classification": "operational",
      "reason": "Class-based routing, explicit configured-provider boundary, schema syntax or non-model fallback; no snapshot selects a provider."
    },
    {
      "path": ".agent/workflows/execution-session.md",
      "line": 220,
      "text_sha256": "0d697c67a8de59dab0d79e41530f17d12515ac0100e04e79afde5fb3a9f999bc",
      "classification": "operational",
      "reason": "Class-based routing, explicit configured-provider boundary, schema syntax or non-model fallback; no snapshot selects a provider."
    },
    {
      "path": ".agent/workflows/inspiration-research.md",
      "line": 155,
      "text_sha256": "bb1eb4465170234e8d42f99651c7658f679e6c6dac37f323d86800ee4450b07e",
      "classification": "operational",
      "reason": "Class-based routing, explicit configured-provider boundary, schema syntax or non-model fallback; no snapshot selects a provider."
    },
    {
      "path": ".agent/workflows/meu-handoff.md",
      "line": 116,
      "text_sha256": "9422472109ddc019127e34c6e8e1ed1f9ae4f9c791211e00f168574afc19a789",
      "classification": "operational",
      "reason": "Class-based routing, explicit configured-provider boundary, schema syntax or non-model fallback; no snapshot selects a provider."
    },
    {
      "path": ".agent/workflows/meu-handoff.md",
      "line": 123,
      "text_sha256": "cd72b4f0ba4b80c71d329a676b1f8c5571cc4b4daa5004df7bc123c6b27d4a6c",
      "classification": "operational",
      "reason": "Class-based routing, explicit configured-provider boundary, schema syntax or non-model fallback; no snapshot selects a provider."
    },
    {
      "path": ".agent/workflows/session-grouping.md",
      "line": 30,
      "text_sha256": "1df5cb0e77339246b46cec9713c06c583e1f3d19084eaca22240850a0acc205a",
      "classification": "operational",
      "reason": "Class-based routing, explicit configured-provider boundary, schema syntax or non-model fallback; no snapshot selects a provider."
    },
    {
      "path": ".agent/workflows/session-grouping.md",
      "line": 40,
      "text_sha256": "83a0cc48cd0b390e0e44ecc88a70a1b1eb42c2696191eaeab4d5b46e63a2b318",
      "classification": "operational",
      "reason": "Class-based routing, explicit configured-provider boundary, schema syntax or non-model fallback; no snapshot selects a provider."
    },
    {
      "path": ".agent/workflows/skill-optimize.md",
      "line": 101,
      "text_sha256": "b396d987f0f2781ab1fb9f88267544228be2515b8d837a269bd619d39060958e",
      "classification": "operational",
      "reason": "Class-based routing, explicit configured-provider boundary, schema syntax or non-model fallback; no snapshot selects a provider."
    },
    {
      "path": ".agent/workflows/validation-review.md",
      "line": 29,
      "text_sha256": "772c66d192bc6bff722d47bd5c310c09505e1eeb34807f1eafa1ca2f5c70bd92",
      "classification": "operational",
      "reason": "Class-based routing, explicit configured-provider boundary, schema syntax or non-model fallback; no snapshot selects a provider."
    },
    {
      "path": ".claude/agents/av-kit-builder.md",
      "line": 2,
      "text_sha256": "9076b5fdbddd6c50ce897f3569662dc306d9dd03d4fc6db932e1f97c1016b798",
      "classification": "loader",
      "reason": "Preserved runtime loader field; local class/provenance stamp outside frontmatter."
    },
    {
      "path": ".claude/agents/av-kit-builder.md",
      "line": 3,
      "text_sha256": "87afa2dce92ce3494d855656bafd15f6a752086b216120573f41a821ae4b2c51",
      "classification": "loader",
      "reason": "Preserved runtime loader field; local class/provenance stamp outside frontmatter."
    },
    {
      "path": ".claude/agents/av-kit-builder.md",
      "line": 4,
      "text_sha256": "13baa7b38e0a8eef16456dcb994b6c7759ee00817162f5662c2d8bccd1de6b49",
      "classification": "loader",
      "reason": "Preserved runtime loader field; local class/provenance stamp outside frontmatter."
    },
    {
      "path": ".claude/agents/av-kit-builder.md",
      "line": 8,
      "text_sha256": "075f27560a448d10a638243060990a6235ab21900ab90474b271cb36997f2f1c",
      "classification": "loader",
      "reason": "Preserved runtime loader field; local class/provenance stamp outside frontmatter."
    },
    {
      "path": ".claude/agents/av-kit-builder.md",
      "line": 10,
      "text_sha256": "ef8f2de9983c0475ff2752a8149145dcfc0acb48e362da17fff90ac70aae4ac7",
      "classification": "loader",
      "reason": "Preserved runtime loader field; local class/provenance stamp outside frontmatter."
    },
    {
      "path": ".claude/agents/av-kit-verifier.md",
      "line": 2,
      "text_sha256": "a42166246aed66ef9841823b583a2382c3b293942cc3ca748e306fbd8f338fe8",
      "classification": "loader",
      "reason": "Preserved runtime loader field; local class/provenance stamp outside frontmatter."
    },
    {
      "path": ".claude/agents/av-kit-verifier.md",
      "line": 3,
      "text_sha256": "69e92ec4531c136b44b71649619735bd1566b9ca65404e7f2c2e87be7c3ba20d",
      "classification": "loader",
      "reason": "Preserved runtime loader field; local class/provenance stamp outside frontmatter."
    },
    {
      "path": ".claude/agents/av-kit-verifier.md",
      "line": 4,
      "text_sha256": "13baa7b38e0a8eef16456dcb994b6c7759ee00817162f5662c2d8bccd1de6b49",
      "classification": "loader",
      "reason": "Preserved runtime loader field; local class/provenance stamp outside frontmatter."
    },
    {
      "path": ".claude/agents/av-kit-verifier.md",
      "line": 9,
      "text_sha256": "fab6f76eac5e3aeaa0d480e65d15f0d90bbc7af5174308f0f8e45edb4b3f60ec",
      "classification": "loader",
      "reason": "Preserved runtime loader field; local class/provenance stamp outside frontmatter."
    },
    {
      "path": ".claude/agents/av-kit-verifier.md",
      "line": 11,
      "text_sha256": "4d1288571fcb8e02d5e269f41f538c928408562ae819f91567e1ce378f7ce545",
      "classification": "loader",
      "reason": "Preserved runtime loader field; local class/provenance stamp outside frontmatter."
    },
    {
      "path": ".claude/agents/README.md",
      "line": 9,
      "text_sha256": "9a05f6fdffff3a5cbd27ae104550c30a0a7eff216f49cb182bd35411bda1a075",
      "classification": "operational",
      "reason": "Class-based routing, explicit configured-provider boundary, schema syntax or non-model fallback; no snapshot selects a provider."
    },
    {
      "path": ".claude/agents/README.md",
      "line": 10,
      "text_sha256": "e236c9affb64e0174ff7bc9cd8b9228f33fb7286312dadb7acf5f6a4a832ad07",
      "classification": "operational",
      "reason": "Class-based routing, explicit configured-provider boundary, schema syntax or non-model fallback; no snapshot selects a provider."
    },
    {
      "path": ".claude/agents/README.md",
      "line": 13,
      "text_sha256": "57c335d227768baed19beeb938066b9e0ff905ef6c4afd89985f011e5c3253ab",
      "classification": "operational",
      "reason": "Class-based routing, explicit configured-provider boundary, schema syntax or non-model fallback; no snapshot selects a provider."
    },
    {
      "path": ".claude/agents/README.md",
      "line": 14,
      "text_sha256": "171a545bf87a2eea0d39abb412950c34cffe6a508191cc191bfdaa66216c794f",
      "classification": "operational",
      "reason": "Class-based routing, explicit configured-provider boundary, schema syntax or non-model fallback; no snapshot selects a provider."
    },
    {
      "path": ".cursor/agents/av-kit-builder.md",
      "line": 2,
      "text_sha256": "9076b5fdbddd6c50ce897f3569662dc306d9dd03d4fc6db932e1f97c1016b798",
      "classification": "loader",
      "reason": "Preserved runtime loader field; local class/provenance stamp outside frontmatter."
    },
    {
      "path": ".cursor/agents/av-kit-builder.md",
      "line": 3,
      "text_sha256": "87afa2dce92ce3494d855656bafd15f6a752086b216120573f41a821ae4b2c51",
      "classification": "loader",
      "reason": "Preserved runtime loader field; local class/provenance stamp outside frontmatter."
    },
    {
      "path": ".cursor/agents/av-kit-builder.md",
      "line": 4,
      "text_sha256": "83203330150112b88d94a0fa07cca70aaf4290111e9c1442aa9460737942b4a1",
      "classification": "loader",
      "reason": "Preserved runtime loader field; local class/provenance stamp outside frontmatter."
    },
    {
      "path": ".cursor/agents/av-kit-builder.md",
      "line": 8,
      "text_sha256": "075f27560a448d10a638243060990a6235ab21900ab90474b271cb36997f2f1c",
      "classification": "loader",
      "reason": "Preserved runtime loader field; local class/provenance stamp outside frontmatter."
    },
    {
      "path": ".cursor/agents/av-kit-builder.md",
      "line": 10,
      "text_sha256": "ef8f2de9983c0475ff2752a8149145dcfc0acb48e362da17fff90ac70aae4ac7",
      "classification": "loader",
      "reason": "Preserved runtime loader field; local class/provenance stamp outside frontmatter."
    },
    {
      "path": ".cursor/agents/av-kit-verifier.md",
      "line": 2,
      "text_sha256": "a42166246aed66ef9841823b583a2382c3b293942cc3ca748e306fbd8f338fe8",
      "classification": "loader",
      "reason": "Preserved runtime loader field; local class/provenance stamp outside frontmatter."
    },
    {
      "path": ".cursor/agents/av-kit-verifier.md",
      "line": 3,
      "text_sha256": "69e92ec4531c136b44b71649619735bd1566b9ca65404e7f2c2e87be7c3ba20d",
      "classification": "loader",
      "reason": "Preserved runtime loader field; local class/provenance stamp outside frontmatter."
    },
    {
      "path": ".cursor/agents/av-kit-verifier.md",
      "line": 4,
      "text_sha256": "a559daa5bcd0de6ff8fce7244c5acb39be5fa092f57a4f6adc3c782451915bb7",
      "classification": "loader",
      "reason": "Preserved runtime loader field; local class/provenance stamp outside frontmatter."
    },
    {
      "path": ".cursor/agents/av-kit-verifier.md",
      "line": 9,
      "text_sha256": "fab6f76eac5e3aeaa0d480e65d15f0d90bbc7af5174308f0f8e45edb4b3f60ec",
      "classification": "loader",
      "reason": "Preserved runtime loader field; local class/provenance stamp outside frontmatter."
    },
    {
      "path": ".cursor/agents/av-kit-verifier.md",
      "line": 11,
      "text_sha256": "4d1288571fcb8e02d5e269f41f538c928408562ae819f91567e1ce378f7ce545",
      "classification": "loader",
      "reason": "Preserved runtime loader field; local class/provenance stamp outside frontmatter."
    },
    {
      "path": ".cursor/agents/README.md",
      "line": 9,
      "text_sha256": "9a05f6fdffff3a5cbd27ae104550c30a0a7eff216f49cb182bd35411bda1a075",
      "classification": "operational",
      "reason": "Class-based routing, explicit configured-provider boundary, schema syntax or non-model fallback; no snapshot selects a provider."
    },
    {
      "path": ".cursor/agents/README.md",
      "line": 10,
      "text_sha256": "e236c9affb64e0174ff7bc9cd8b9228f33fb7286312dadb7acf5f6a4a832ad07",
      "classification": "operational",
      "reason": "Class-based routing, explicit configured-provider boundary, schema syntax or non-model fallback; no snapshot selects a provider."
    },
    {
      "path": ".cursor/agents/README.md",
      "line": 13,
      "text_sha256": "e1687814eaf03b116b5da1ca982bfcd43b889856d3e56c7b40c2d319fbf4dbce",
      "classification": "operational",
      "reason": "Class-based routing, explicit configured-provider boundary, schema syntax or non-model fallback; no snapshot selects a provider."
    },
    {
      "path": "docs/execution/plans/PLAN-TEMPLATE.md",
      "line": 66,
      "text_sha256": "9ddf1af8e58ee7d4dbdd82dddfb401a7b36138eba5cdae7281d97cde6849c995",
      "classification": "operational",
      "reason": "Class-based routing, explicit configured-provider boundary, schema syntax or non-model fallback; no snapshot selects a provider."
    },
    {
      "path": "docs/execution/plans/PLAN-TEMPLATE.md",
      "line": 71,
      "text_sha256": "862550a4d7e457e532ae60e81eac99e1dbe622da86d345f0844b851a68bb89ca",
      "classification": "operational",
      "reason": "Class-based routing, explicit configured-provider boundary, schema syntax or non-model fallback; no snapshot selects a provider."
    },
    {
      "path": "docs/execution/plans/TASK-TEMPLATE.md",
      "line": 41,
      "text_sha256": "4fb38e13247f3e15b2728aaefe23c24a951488fbf8c190f6746fe6d0ceada8a2",
      "classification": "operational",
      "reason": "Class-based routing, explicit configured-provider boundary, schema syntax or non-model fallback; no snapshot selects a provider."
    },
    {
      "path": "docs/execution/plans/TASK-TEMPLATE.md",
      "line": 42,
      "text_sha256": "423d0d3a5f3c5e9ce0f8702262cc6e52baacd76e4f08542959f4ff702966fa88",
      "classification": "operational",
      "reason": "Class-based routing, explicit configured-provider boundary, schema syntax or non-model fallback; no snapshot selects a provider."
    },
    {
      "path": "docs/execution/plans/TASK-TEMPLATE.md",
      "line": 48,
      "text_sha256": "6e601de15f379957473b397af9e7bd7047c362a05da429ecbfe0aad8447377df",
      "classification": "operational",
      "reason": "Class-based routing, explicit configured-provider boundary, schema syntax or non-model fallback; no snapshot selects a provider."
    },
    {
      "path": "docs/execution/plans/TASK-TEMPLATE.md",
      "line": 50,
      "text_sha256": "1fcd9b2ca012a2229633ec4f9187a956d382a5bbe44fa8b31aaa9d08f1b4ea17",
      "classification": "operational",
      "reason": "Class-based routing, explicit configured-provider boundary, schema syntax or non-model fallback; no snapshot selects a provider."
    },
    {
      "path": "docs/execution/plans/TASK-TEMPLATE.md",
      "line": 62,
      "text_sha256": "1768cd4d6435947748f5375e6e2a046ecc52b17c34eac1bdb1bf743a215eb98a",
      "classification": "operational",
      "reason": "Class-based routing, explicit configured-provider boundary, schema syntax or non-model fallback; no snapshot selects a provider."
    },
    {
      "path": "docs/execution/plans/TASK-TEMPLATE.md",
      "line": 90,
      "text_sha256": "cc175bc6f7e40ac4dab752b81702ae447d1a7b4c8866f97c06111327af643a53",
      "classification": "operational",
      "reason": "Class-based routing, explicit configured-provider boundary, schema syntax or non-model fallback; no snapshot selects a provider."
    },
    {
      "path": "docs/execution/plans/TASK-TEMPLATE.md",
      "line": 91,
      "text_sha256": "d5290d67f2bb20f5e5f6cd79566ba976004269b3997acba915d0f0a244e97230",
      "classification": "operational",
      "reason": "Class-based routing, explicit configured-provider boundary, schema syntax or non-model fallback; no snapshot selects a provider."
    },
    {
      "path": "docs/execution/plans/TASK-TEMPLATE.md",
      "line": 95,
      "text_sha256": "47c1272548d9369deccf8670d1d79dec2100f0c073ba31dc321acdb9482b52fb",
      "classification": "operational",
      "reason": "Class-based routing, explicit configured-provider boundary, schema syntax or non-model fallback; no snapshot selects a provider."
    },
    {
      "path": "docs/execution/plans/TASK-TEMPLATE.md",
      "line": 100,
      "text_sha256": "d5980f1aaf45ce490ffb7aa0daeeb077ea68b76e85734fd3b74b864ef998a260",
      "classification": "operational",
      "reason": "Class-based routing, explicit configured-provider boundary, schema syntax or non-model fallback; no snapshot selects a provider."
    },
    {
      "path": "docs/execution/plans/TASK-TEMPLATE.md",
      "line": 102,
      "text_sha256": "296cec867a8873667f5cffd17b44b336b7e5bdde2e3babdf55ae07509c121ef0",
      "classification": "operational",
      "reason": "Class-based routing, explicit configured-provider boundary, schema syntax or non-model fallback; no snapshot selects a provider."
    },
    {
      "path": "docs/execution/reflections/TEMPLATE.md",
      "line": 59,
      "text_sha256": "4b0c33651b9679013eabf15ab72f0e6b76bfb2461c7605c84c5283c66a429713",
      "classification": "operational",
      "reason": "Class-based routing, explicit configured-provider boundary, schema syntax or non-model fallback; no snapshot selects a provider."
    },
    {
      "path": "GUARDRAILS.md",
      "line": 13,
      "text_sha256": "5d507c817b28344974f75b2026f36c813ed3308a893c58e2520f1029a497ceb9",
      "classification": "operational",
      "reason": "Class-based routing, explicit configured-provider boundary, schema syntax or non-model fallback; no snapshot selects a provider."
    },
    {
      "path": "GUARDRAILS.md",
      "line": 17,
      "text_sha256": "dae7d573cd1d7cd99867ab641d5a41cbf5b9cf0422b37f57a86a085555d9d314",
      "classification": "operational",
      "reason": "Class-based routing, explicit configured-provider boundary, schema syntax or non-model fallback; no snapshot selects a provider."
    },
    {
      "path": "PROJECT-PROFILE.md",
      "line": 21,
      "text_sha256": "60136fe7064dd365eef32e75940b3dbc2a0bec4200ccf403493ca4f783dcd5db",
      "classification": "operational",
      "reason": "Class-based routing, explicit configured-provider boundary, schema syntax or non-model fallback; no snapshot selects a provider."
    },
    {
      "path": "PROJECT-PROFILE.md",
      "line": 33,
      "text_sha256": "83bb4be923f5a0fa17924265002958b6ca6df29e3237116e58cef1cad379881a",
      "classification": "operational",
      "reason": "Class-based routing, explicit configured-provider boundary, schema syntax or non-model fallback; no snapshot selects a provider."
    },
    {
      "path": "PROJECT-PROFILE.md",
      "line": 35,
      "text_sha256": "4b775c200748f6f5ecf9e057f67bad5cbd0753a6fcdec0c31c92b9fd8dc6af9b",
      "classification": "operational",
      "reason": "Class-based routing, explicit configured-provider boundary, schema syntax or non-model fallback; no snapshot selects a provider."
    },
    {
      "path": "PROJECT-PROFILE.md",
      "line": 92,
      "text_sha256": "4dba5e71615594e971ce9af9fd519ec017f48cc17d3a634feca317c415c1ad80",
      "classification": "operational",
      "reason": "Class-based routing, explicit configured-provider boundary, schema syntax or non-model fallback; no snapshot selects a provider."
    },
    {
      "path": "PROJECT-PROFILE.md",
      "line": 114,
      "text_sha256": "2da7b759464f98c4e07d1c8922613d78032d3004f56c8775045d09217fa3a935",
      "classification": "operational",
      "reason": "Class-based routing, explicit configured-provider boundary, schema syntax or non-model fallback; no snapshot selects a provider."
    },
    {
      "path": "PROJECT-PROFILE.md",
      "line": 117,
      "text_sha256": "fd476e6233e9b65647feeab40a99ff0ca54d064a91828335962a61338de04e42",
      "classification": "operational",
      "reason": "Class-based routing, explicit configured-provider boundary, schema syntax or non-model fallback; no snapshot selects a provider."
    },
    {
      "path": "tools/Invoke-CodexDispatch.ps1",
      "line": 952,
      "text_sha256": "397713a77422e15a9199ed4e308ad547475dc901e9d3ebe26fc9bc8b6e1a3bb9",
      "classification": "operational",
      "reason": "Class-based routing, explicit configured-provider boundary, schema syntax or non-model fallback; no snapshot selects a provider."
    },
    {
      "path": "tools/Invoke-CodexDispatch.ps1",
      "line": 1448,
      "text_sha256": "29986d126fb26211c63c4b834a09d11e7c5638702284ded35eb94628e1b46714",
      "classification": "operational",
      "reason": "Class-based routing, explicit configured-provider boundary, schema syntax or non-model fallback; no snapshot selects a provider."
    },
    {
      "path": "tools/Invoke-CodexDispatch.sh",
      "line": 724,
      "text_sha256": "150fe6ba2e7844cbab80d6dbc9c96ed701088b3c7a5b889f63b8c1a11988d193",
      "classification": "operational",
      "reason": "Class-based routing, explicit configured-provider boundary, schema syntax or non-model fallback; no snapshot selects a provider."
    },
    {
      "path": "tools/Invoke-CodexDispatch.sh",
      "line": 1212,
      "text_sha256": "9bebbc6de6d4558da54c56957ec8afa2f5d3b698268fc2ba52c87aa615593a31",
      "classification": "operational",
      "reason": "Class-based routing, explicit configured-provider boundary, schema syntax or non-model fallback; no snapshot selects a provider."
    },
    {
      "path": ".cursor/agents/av-kit-builder.md",
      "line": 4,
      "text_sha256": "a559daa5bcd0de6ff8fce7244c5acb39be5fa092f57a4f6adc3c782451915bb7",
      "classification": "loader",
      "reason": "Preserved runtime loader field; local class/provenance stamp outside frontmatter."
    }
  ]
}
```
