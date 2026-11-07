---
project: "{YYYY-MM-DD}-{project-slug}"
source: "docs/execution/plans/{YYYY-MM-DD}-{project-slug}/implementation-plan.md"
meus: ["{MEU-ID-1}", "{MEU-ID-2}"]
status: "in_progress"
template_version: "2.2"
---

# Task — {Project Title}

> **Project:** `{YYYY-MM-DD}-{project-slug}`
> **Type:** {Infrastructure/Docs | Domain | API | GUI | MCP}
> **Estimate:** {N files changed}

## Context Tool Decision

```yaml
context_tool_decision:
  phase: planning | execution | planning_and_execution
  eligible_tools: [graphify, graphify-research, headroom]
  decision: use | accepted_loss | not_applicable
  eligibility_basis: "{specific graph/payload/scope evidence}"
  human_message_reference: "{USER_EXPLICIT date/summary; null only for not_applicable}"
```

## Task Table

> Classify every validation command through PROFILE D6 (D6_ADOPTER_ARGV) and
> `.agent/docs/output-evidence-policy.md`.
> D6 defines static/targeted/fresh full stages and complete input identity.
> Use `rtk proxy`; Python commands use the project `uv` environment. Redirect every process stream to `C:/Temp/av-kit`.
>
> **Handoff set:** product projects name one
> `.agent/context/handoffs/{date}-{project-slug}-{MEU-ID}-handoff.md` per MEU in the
> deliverable rows. Non-product `meus: []` projects name one project handoff at
> `.agent/context/handoffs/{date}-{project-slug}-handoff.md`. The rolling project
> review filename remains `{project-folder}-implementation-critical-review.md`.
>
> Column schema: **Depends on** = `depends_on`, **Context strategy** =
> `context_strategy`, **Durable outputs** = `durable_outputs`, and optional
> **`builder_model`** (10-column tables). Legacy 9-column tables remain valid.
> `builder_model` names a **capability class** — `avkit_builder` for mechanical rows,
> `avkit_coordinator` for rows needing the dependency graph, `avkit_verifier` for read-only
> validation. Never a model slug and never `auto`; resolve the class instead
> (`Resolve-AgentModel -Class avkit_builder -Harness <harness> -Project P:/av-kit`), because which snapshot
> serves a class is the live registry's business (see `.agent/docs/model-routing.md`)
> and changes without touching this plan.
> `architecture_single_shot` is reserved for its own shape and is never a builder.

| # | Task | Owner | Deliverable | Validation | Depends on | Context strategy | Durable outputs | builder_model | Status |
|---|---|---|---|---|---|---|---|---|---|
| 1 | {first implementation task} | coder | {deliverable} | `{exact command}` | — | shared | {durable repository artifact} | `avkit_builder` | `[ ]` |
| 2 | {second implementation task} | coder | {deliverable} | `{exact command}` | 1 | compact_continue | {durable path; compact then re-read task + this output} | `avkit_coordinator` | `[ ]` |
| ... | ... | ... | ... | ... | ... | ... | ... | ... | ... |

`context_strategy` must be `shared|compact_continue|isolated`. Dependencies must name
existing rows and form an acyclic graph. Every non-`shared` row must name a durable
output and lifecycle action. `isolated` is valid only with an authorized fresh-worker
capability; otherwise change it to `compact_continue` before execution.

> **Optional `delegate_to` annotation.** A row may name an in-harness subagent for delegation by
> adding `delegate_to: av-kit-builder` (or `av-kit-verifier`) **inside the row's Task cell** —
> it is prose metadata, NOT a new column and NOT a value of `context_strategy` (whose enum stays
> exactly `shared|compact_continue|isolated`). The delegation decision itself is governed by
> `.agent/skills/subagent-delegation/SKILL.md`;
> the annotation only records the intended worker when `fresh_worker` resolves.

> **Closeout is one continuous execution pass, split by the review barrier (v2.1).**
> Phase **H1** (pre-review) finishes the implementation, all artifact updates, and the
> **handoff** (the review's target). The **Execution Critical Review** is then dispatched
> and looped to `approved`. Phase **H2** (post-review) writes the reflection/metrics/session
> save — these RECORD the review outcome and therefore *cannot* be written before the review.
> "Continuous pass" means: complete H1 → dispatch → loop corrections → complete H2 **without
> stopping** (the only valid pauses are the four outcomes in `AGENTS.md` §Execution Contract:
> DONE, review cap, reviewer unavailable, human decision; compaction continues). Do
> NOT report completion or ask the user to approve between phases.
>
> **The phase-divider rows below are NOT stop points.** They mark *ordering* (H2 must record the
> review, so it follows H1), not *turn boundaries*. The boundary between any two phases is the most
> common place the agent offers a "politeness off-ramp" — these are VIOLATIONS, not courtesies:
> - ❌ "Want me to continue with the H1/H2 closeout, or handle it in a separate session?"
> - ❌ "Implementation/review complete — shall I proceed to the reflection?"
> - ❌ "This looks like a good stopping point. Let me know if you'd like me to continue."

| | **📋 Phase H1 — Pre-Review Closeout** — continuation of implementation; do not stop at this divider. | | | | | | | | |
| H1-1 | Re-read this `task.md` and prove no implementation row remains unchecked. | coder | Exact unchecked-row receipt | `rtk proxy uv run python -c "import pathlib,sys; t=pathlib.Path('docs/execution/plans/{date}-{project-slug}/task.md').read_text(encoding='utf-8'); bad=[ln for ln in t.splitlines() if ln.startswith(chr(124)) and ln.strip()[1:].split(chr(124),1)[0].strip().strip(chr(96)).isdigit() and '[ ]' in ln]; sys.exit(1 if bad else 0)" *> C:/Temp/av-kit/task-unchecked.txt; $code=$LASTEXITCODE; Get-Content C:/Temp/av-kit/task-unchecked.txt; exit $code` | `{last-task-id}` | shared | `task.md`; exact receipt | `avkit_coordinator` | `[ ]` |
| H1-2 | Run the registered verification plan. | tester | All blocking checks pass | `{exact command(s) from implementation-plan.md}` | H1-1 | shared | Durable gate observations in handoff | `avkit_coordinator` | `[ ]` |
| H1-3 | For product MEUs, update/render/check MEU status and current focus. For `meus: []`, prove the registered product-state no-op. | orchestrator | SSOT rendered or no-op receipt | `rtk proxy uv run python tools/meu_status.py render --check *> C:/Temp/av-kit/drift-check.txt; $code=$LASTEXITCODE; Get-Content C:/Temp/av-kit/drift-check.txt; exit $code` | H1-2 | shared | SSOT/no-op receipt | `avkit_coordinator` | `[ ]` |
| H1-4 | If `packages/api/` changed, check OpenAPI drift and regenerate only on detected drift; otherwise record the skip basis. | tester | OpenAPI receipt or scoped skip | `rtk proxy uv run python -c "import pathlib,sys; sys.exit(0 if not pathlib.Path('packages/api').exists() else 1)" *> C:/Temp/av-kit/openapi-check.txt; $code=$LASTEXITCODE; Get-Content C:/Temp/av-kit/openapi-check.txt; exit $code` | H1-3 | shared | OpenAPI receipt | `avkit_coordinator` | `[ ]` |
| H1-5 | Read the handoff template and deterministic latest peer exemplar. | orchestrator | Source-read receipt | `view_file: .agent/context/handoffs/TEMPLATE.md` plus latest peer handoff | H1-4 | compact_continue | Template/exemplar receipt; compact_continue fallback | `avkit_coordinator` | `[ ]` |
| H1-6 | Create the complete evidence handoff. Product: `.agent/context/handoffs/{date}-{project-slug}-{MEU-ID}-handoff.md` per MEU. Non-product `meus: []`: `.agent/context/handoffs/{date}-{project-slug}-handoff.md`. | orchestrator | Canonical handoff set | `rtk proxy uv run python tools/validate_closeout_artifacts.py --handoff {handoff-file} --plan {plan-file} *> C:/Temp/av-kit/handoff-check.txt; $code=$LASTEXITCODE; Get-Content C:/Temp/av-kit/handoff-check.txt; exit $code` | H1-5 | compact_continue | Canonical handoff(s); compact_continue fallback | `avkit_coordinator` | `[ ]` |
| H1-6a | Prove every plan AC appears in the handoff AC table. | tester | Complete target-bound AC set | `rtk proxy uv run python tools/validate_closeout_artifacts.py --plan {plan-file} --handoff {handoff-file} --ac-coverage-only *> C:/Temp/av-kit/handoff-ac-check.txt; $code=$LASTEXITCODE; Get-Content C:/Temp/av-kit/handoff-ac-check.txt; exit $code` | H1-6 | shared | AC validation receipt | `avkit_coordinator` | `[ ]` |
| H1-6b | Verify fresh full evidence against independently obtained current D6 identity; rerun D6 full if inputs changed or evidence is missing. | tester | Fresh full evidence | `rtk proxy uv run python tools/durable_evidence.py {handoff-file} --require-full --expected-state {actual-state} *> C:/Temp/av-kit/full-evidence-check.txt; $code=$LASTEXITCODE; Get-Content C:/Temp/av-kit/full-evidence-check.txt; exit $code` | H1-6a | shared | Handoff evidence.v1 full record | `avkit_coordinator` | `[ ]` |
| | **🔎 Execution Critical Review** — blocking independent-review region; the implementer never authors the verdict. | | | | | | | | |
| H1-7 | Dispatch independent reviewer under EGRESS_PRECEDENCE; loop corrections within ledger limits. | reviewer dispatch / coder corrections | Rolling review | `{exact authorized dispatch command with preserved exit}` | H1-6b | isolated | Rolling review; durable findings; compact_continue fallback | — | `[ ]` |
| H1-7a | Parse current review to target-bound state. | tester | Review state receipt | `rtk proxy uv run python tools/validate_closeout_artifacts.py --review {review-file} --review-state-only --expected-review-mode execution --expected-target-plan {plan-file} --max-review-rounds {configured-cap} --output C:/Temp/av-kit/review-state.json *> C:/Temp/av-kit/review-state-check.txt; $code=$LASTEXITCODE; Get-Content C:/Temp/av-kit/review-state-check.txt; exit $code` | H1-7 | shared | Durable review + parsed state | `avkit_coordinator` | `[ ]` |
| H1-7b | Require approved current review state and matching ledger verdict. | tester | Verified approval | `rtk proxy uv run python tools/validate_closeout_artifacts.py --review {review-file} --approved-state-only --review-state-receipt C:/Temp/av-kit/review-state.json --expected-review-mode execution --expected-target-plan {plan-file} --max-review-rounds {configured-cap} *> C:/Temp/av-kit/exec-review.txt; $code=$LASTEXITCODE; Get-Content C:/Temp/av-kit/exec-review.txt; exit $code` | H1-7a | shared | Durable approval observation | `avkit_coordinator` | `[ ]` |
| | **📋 Phase H2 — Post-Review Closeout** — continue immediately after approval; first re-read `task.md`. | | | | | | | | |
| H2-1 | Read the reflection template, schema, and deterministic latest peer exemplar. | orchestrator | Source-read receipt | `view_file: docs/execution/reflections/TEMPLATE.md`, `.agent/schemas/reflection.v1.yaml`, and latest peer reflection | H1-7b | shared | Reflection source receipt | `avkit_coordinator` | `[ ]` |
| H2-2 | Create the full reflection with review churn and Instruction Coverage YAML. | orchestrator | `docs/execution/reflections/{date}-{project-slug}-reflection.md` | `rtk proxy uv run python tools/validate_closeout_artifacts.py --reflection {reflection-file} --reflection-template docs/execution/reflections/TEMPLATE.md --reflection-schema .agent/schemas/reflection.v1.yaml --decision-source {plan-file} --decision-source {handoff-file} --decision-source {grouping-file} --decision-source .agent/context/known-issues.yaml --decision-issue {issue-id} *> C:/Temp/av-kit/reflection-check.txt; $code=$LASTEXITCODE; Get-Content C:/Temp/av-kit/reflection-check.txt; exit $code` | H2-1 | compact_continue | Reflection; compact_continue fallback | `avkit_coordinator` | `[ ]` |
| H2-3 | Append and verify the metrics row. | orchestrator | Populated metrics row | `rtk proxy uv run python -c "import pathlib,sys; p=pathlib.Path('docs/execution/metrics.md'); sys.exit(0 if p.exists() and p.read_text(encoding='utf-8').strip() else 1)" *> C:/Temp/av-kit/metrics-check.txt; $code=$LASTEXITCODE; Get-Content C:/Temp/av-kit/metrics-check.txt; exit $code` | H2-2 | shared | Metrics receipt | `avkit_coordinator` | `[ ]` |
| H2-4 | Run complete closeout structural, handoff, approval, and reflection checks. | tester | Passing completion-preflight receipt | `rtk proxy uv run python tools/lint_task_contract.py --allowed-builder-classes avkit_builder,avkit_coordinator,avkit_verifier --task docs/execution/plans/{date}-{project-slug}/task.md *> C:/Temp/av-kit/closeout-preflight.txt; $code=$LASTEXITCODE; Get-Content C:/Temp/av-kit/closeout-preflight.txt; exit $code` | H2-3 | shared | Closeout receipt | `avkit_coordinator` | `[ ]` |
| H2-5 | Prepare conventional commit-message suggestions; never commit without human approval. | orchestrator | Fresh nonempty draft | `rtk proxy uv run python -c "import pathlib; pathlib.Path('C:/Temp/av-kit/commit-draft.txt').write_text('feat: <slug>\\n', encoding='utf-8')" *> C:/Temp/av-kit/commit-draft-write.txt; $code=$LASTEXITCODE; Get-Content C:/Temp/av-kit/commit-draft.txt; exit $code` | H2-4 | shared | Commit-message draft | `avkit_coordinator` | `[ ]` |
| H2-6 | Write the next session's prompt (`.agent/workflows/execution-session.md` §6). Each human decision still open carries its Decision Brief's recommendation and do-nothing option. | orchestrator | `C:/Temp/av-kit/session-{next-n}-prompt.md` | `rtk proxy uv run python -c "import pathlib,sys; p=pathlib.Path('C:/Temp/av-kit/session-{next-n}-prompt.md'); t=p.read_text(encoding='utf-8') if p.exists() else ''; print(t[:200]); sys.exit(0 if t.startswith('Start Session') else 1)" *> C:/Temp/av-kit/next-prompt-check.txt; $code=$LASTEXITCODE; Get-Content C:/Temp/av-kit/next-prompt-check.txt; exit $code` | H2-5 | shared | Next-session prompt | `avkit_coordinator` | `[ ]` |

### Status Legend

| Symbol | Meaning |
|--------|---------|
| `[ ]` | Not started |
| `[/]` | In progress |
| `[x]` | Complete |
| `[B]` | Blocked — evidence-gated (closed reason list + pasted error; must link follow-up) |

### Evidence-First & Sequencing Rules

Evidence records follow `.agent/docs/output-evidence-policy.md`; raw receipts are working
data. Each completed row points to durable pasted observations. Update domain-specific
H1-3/H1-4 commands from PROFILE D6/D9 before execution. Replace all placeholder commands,
including the review cap, and preserve exact command status after receipt reads. No stop
hook is installed by this template; a future adapter must declare/test arming and release.


- **Evidence-first completion:** a row is `[x]` only when its deliverable exists and the handoff/walkthrough carries the evidence bundle (AGENTS.md §Execution Contract).
- **The review barrier resolves the old reflection↔review cycle:** the handoff (H1-6) is created *before* the review (it is the review's input); the reflection/metrics (H2) are created *after* `approved` so they can record the verdict. Do not create H2 artifacts during H1, and do not dispatch the review (H1-7) before the handoff exists.
- **Self-review prohibition:** the implementing agent dispatches and collects the H1-7 review; it never authors the `approved` verdict itself (AGENTS.md §Execution Contract).
- **`[B]` is evidence-gated:** valid ONLY for (a) a reproduced *external* error, (b) a missing dependency/credential/permission, or (c) a human-decision gate — each with a linked follow-up and, for (a)/(b), a row-bound `### B-<row-id>` block with command, nonzero exit and pasted decisive error as `evidence.v1`; decisions need a durable decision link. The row cites `B-<row-id>` and `follow-up [label](target)`. Subjective reasons ("too complex", "no time", "out of scope", "later") are invalid; no error artifact ⇒ not blocked ⇒ keep working (AGENTS.md §Execution Contract).
- **Dispatching the H1-7 review is a blocking step, not a turn boundary:** continue to H2 in the same pass once the `approved` verdict file lands. The only sanctioned turn-enders are DONE, review cap, reviewer unavailable, or human decision; compaction continues (AGENTS.md §Execution Contract).
