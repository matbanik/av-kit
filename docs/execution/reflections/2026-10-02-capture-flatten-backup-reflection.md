---
date: "2026-10-11"
project: "capture-flatten-backup"
meus: ["MEU-67"]
plan_source: "docs/execution/plans/2026-10-02-capture-flatten-backup/implementation-plan.md"
template_version: "2.0"
---

# 2026-10-11 Meta-Reflection

> **Date**: 2026-10-11 (plan written 2026-10-02; execution 2026-10-03 to 2026-10-10)
> **MEU(s) Completed**: MEU-67 `capture-flatten-backup`
> **Plan Source**: `docs/execution/plans/2026-10-02-capture-flatten-backup/implementation-plan.md`

---

## Execution Trace

### Friction Log

1. **What took longer than expected?**

   The tail after the first green container pre-gate: five `LOCAL_SEQUENCE` attempts and two execution review rounds. Rows 0–10 took about a day; H1-6/H1-7 took a week. Every attempt surfaced something real, and none of it was a product regression found by the gate itself:
   - **Attempt 1:** native tooltips cannot show on a disabled `Button` (`pointer-events-none`, F1). Claude Code's local MCP scope is keyed by a case-sensitive path (F8).
   - **Attempt 2:**
     - A shared-registry hash moved (A-8).
     - Native tooltips did not show anywhere in the dev app (A-10).
     - Claude Code refused `confirm: true` because `tools/list` advertised an empty `inputSchema` (A-9). That issue had been filed as high in Session 28 and turned out to block this MEU's MCP feature.
   - **Attempt 3:** Claude Code (VS Code) declares elicitation but auto-declines every prompt, so no capture action could ever be accepted from that IDE (A-11).
   - **Attempts 3–5:** the shared registry and the agentic-framework HEAD moved twice more outside av-kit (A-12, A-13, A-14).

2. **What instructions were ambiguous?**

   - **"Create it" in `FLATTEN_SEQUENCE` step 3.** It did not say through which layer. The MEU-12 guard (no `mkdir` in services) made the obvious reading wrong, and only the full pytest run in the pre-gate caught it (A-5).
   - **A-8's scope.** It quoted "the new registry hash", while the `-AcceptDrift` switch accepts any preflight drift. That gap became review F3 and needed A-13.
   - **A-9's option text said "passthrough".** The literal reading would have changed an existing test (`m7-resource.test.ts`, which reads the registered union's `options`). I kept the registered union and rewrote only `tools/list`, and disclosed it. The reviewer judged it within intent.

3. **What instructions were unnecessary?**

   Restating project-wide gate evidence in the MEU handoff, again. `walkthrough.md` is the canonical record, and keeping the handoff in sync is what let F2 (a stale handoff) happen.

4. **What was missing?**

   - **A real-client MCP check before the look.** Every MCP test used the SDK `Client`, which is typed and elicitation-capable. Claude Code's actual behaviour (no schema → string `confirm`; auto-declined elicitation) surfaced only at F8, three attempts later.
   - **An id-format rule for anything interpolated into a human prompt or a path.** `z.string().min(1)` let agent text into the "Allow?" prompt and into the URL (review round 1 F1, High). The plan's "only the validated id is interpolated" was true and insufficient.
   - **A census of layering guards** (`test_services.py`), not only literal pins. The row-1 census pattern set did not include guard tests that forbid an implementation shape.

5. **What did you do that wasn't in the prompt?**

   - Reproduced every review High myself before fixing (F1: the prompt text and the normalised URL).
   - Ran each new Electron test against the pre-fix renderer to prove it Red (A-6, A-10), because jsdom `title` assertions had passed while the real tooltip was invisible.
   - Tested `windows-gate-check`'s drift branch on synthetic results before sending a request that depended on it (A-8, A-13).

### Quality Signal Log

6. **Which tests caught real bugs?**
   - **The full pytest run in the container pre-gate:** the AC-12.8 layering guard (A-5).
   - **`gate-cycle1`'s OpenAPI path diff:** a ruff rewrap of a route docstring had changed an existing path's description.
   - **`api-scope`:** an out-of-scope `PathRow.tsx` edit.
   - **The human look:** F1 (tooltips) and F8 (Claude Code setup, empty schema, auto-decline). No automated layer caught these.
   - **The execution reviewer's reproduction (F1 High):** prompt injection and path traversal through the capture `id`. AC-67.30 asserted the message for a benign id only.
   - **Review F4:** two rollback edges; unit negatives reproduced both (an orphan backup, a stale sidecar).

7. **Which tests were trivially obvious?**

   The AC-67.13 watcher assertions passed at Red, because `ui/src/main` was unchanged by design. Their value is a lock, not a Red. The jsdom `title`-attribute assertions for A-6 were obvious and also insufficient. The Electron hover-target and visible-label tests (AC-67.20 A-6, AC-67.35) are the ones that mean something.

8. **Did pyright/ruff catch anything meaningful?**

   Ruff's E501 drove the docstring rewrap that broke the OpenAPI path check, so it caused a regression rather than catching one. Pyright found nothing; `tsc` and eslint found nothing beyond formatting.

### Workflow Signal Log

9. **Was the FIC useful as written?**

   Yes for the API and GUI. The single-statement contracts (`FLATTEN_SEQUENCE`, `CONVERT_ON_APPLY`, `BACKUP_NAME`, `APPLY_ENABLED`, `FLATTEN_STATUS`) made the Python and jsdom tests near-mechanical, and the first Green runs passed with only setup fixes. `USER_CONFIRM` was correct but rested on an assumption that MCP clients behave like the SDK `Client`. A-9 and A-11 had to add the missing contracts.

10. **Was the handoff template right-sized?**

    Too large to keep current across 14 A-decisions. The family-level `--ac-coverage-only` check could not see that AC-67.36 was missing (review F2, observation 5).

11. **How many tool calls did this session take?**

    Not tracked precisely; several hundred in the cloud session, plus the local agent's work across five `LOCAL_SEQUENCE` attempts.

12. **Which rows were delegated, to which subagent (harness + model), and did any delegated result need rework?**

    No implementation rows were delegated.
    - **Plan review:** a separate-context Fable 5.1 Agent subagent, 3 rounds (user-authorized same-vendor route).
    - **Execution review Round 1:** the same Fable 5.1 route. It found the F1 High, a real security defect.
    - **Execution review Round 2:** Codex CLI `gpt-6.1-sol` (high), dispatched by Mat's local agent after the user changed the route. Vendor-distinct; approved with 0 findings.
    - **Local work:** Mat's local agent ran all five `LOCAL_SEQUENCE` attempts. It also authored A-11 (the dialog fallback) and A-12/A-13/A-14 (the overlay revalidations), and its own Codex pass reviewed A-11.
    - A Claude Code guide subagent researched MCP client configuration (A-7).

### Decisions Log

| ID | Stage | Question | Resolution | Chosen | Source tag | Reasoning (why this; why the alternatives lost) | Human ref |
|----|-------|----------|------------|--------|------------|--------------------------------------------------|-----------|
| D-1 | grouping | How are the TTS runtime assets provisioned? | human | Managed downloads in the model-manager flow plus Dependencies readiness rows | Human-approved | Grouping §8 D-1 (carried from triage D-22). | USER_EXPLICIT 2026-09-30 'D-22: follow you recommendation' |
| D-2 | grouping | Residual MEUs under original phases or a new Phase 12? | autonomous | Original phases with `(residual)` sections | Local Canon | Grouping §8 D-2; MEU-67 lives in 09. | — |
| D-3 | grouping | One TTS session or an engine/page split? | autonomous | One session with a split flag | Local Canon | Grouping §8 D-3 (carried). | — |
| D-4 | grouping | Where does the MCP audit sit? | autonomous | Session 28, before the Capture sessions | Local Canon | Grouping §8 D-4; its baseline was the regression net for MEU-67's two MCP actions. | — |
| D-5 | grouping | Are the TECH-DEBT/DEFER rows MEUs in this batch? | autonomous | No | Local Canon | Grouping §8 D-5. `TOOLING-SHARED-REGISTRY-COUPLING` recurred here three times (A-12, A-13, A-14). | — |
| D-6 | grouping | Zoom wheel semantics | autonomous | Plain wheel zooms about the cursor | Research-backed | Grouping §8 D-6 (Session 29 scope). | — |
| D-7 | grouping | Rename the header palette control? | autonomous | "Commands Ctrl+K" with a command icon | Research-backed | Grouping §8 D-7 (Session 31 scope). | — |
| D-8 | planning | What does flatten bake from, and how do the new bytes reach the original? | autonomous | Bake `SAVED_MARKS` into a `TMP_SUFFIX` sibling, then `os.replace` | Research-backed | Atomic replace; the sidecar is the source of truth (plan D-8). | — |
| D-9 | planning | Backup naming within one second, and which backup is newest? | autonomous | `BACKUP_NAME` with `_n`; newest by parsed (timestamp, n) | Local Canon | mtime is unreliable after copies (plan D-9). | — |
| D-10 | planning | Should Apply to image work only on PNG originals? | human | PNG in place; JPEG/WebP converted on Apply to a new PNG copy, the original untouched | Human-approved | `CONVERT_ON_APPLY` (plan D-10). | USER_EXPLICIT 2026-10-03 'D-10: create converter that will change JPEG and WEBP to PNG. … leaving the original file be.' |
| D-11 | planning | How is `capture.backup_dir` stored and validated? | autonomous | `BACKUP_DIR_RULE` (`""` → inbox default; absolute; never the inbox) | Local Canon | Follows inbox moves (plan D-11). | — |
| D-12 | planning | What does flatten do with backups off? | autonomous | Proceeds without a backup; the confirm says it cannot be undone | Local Canon | Plan D-12. | — |
| D-13 | planning | How does the GUI learn that a backup exists? | autonomous | `backup_path` on the detail, flatten and revert | Local Canon | The list shape is unchanged (plan D-13). | — |
| D-14 | planning | Does Revert consume the backup? | autonomous | Copies and keeps it; `ANNOTATED_CONSISTENCY` | Local Canon | Plan D-14. Review F4(b) tightened the no-marks branch. | — |
| D-15 | planning | Concurrent capture file safety | autonomous | `CAPTURE_FILE_LOCK` | Local Canon | Plan D-15; AC-67.14. | — |
| D-16 | planning | I/O failures during flatten and revert | autonomous | 409 `CaptureFlattenConflictError` with `FLATTEN_ROLLBACK` | Local Canon | Plan D-16. Review F4(a) closed the convert-rollback backup edge. | — |
| D-17 | planning | Where do the new settings appear? | autonomous | The Settings page Capture card only | Local Canon | Plan D-17. | — |
| D-18 | planning | Button variants and texts for Apply/Revert | autonomous | `APPLY_ENABLED` … `FLATTEN_STATUS` | Local Canon | Plan D-18. Review F5 aligned Revert to `secondary`. | — |
| D-19 | planning | Fix the MCP instruction "Files on disk are not deleted"? | autonomous | Yes: `INSTRUCTION_TEXT` | Local Canon | Resolves `MCP-INSTRUCTIONS-CAPTURE-REMOVE-FILES` (plan D-19). | — |
| D-20 | planning | Baseline update without hand-editing or tolerating anything | autonomous | `LOCAL_SEQUENCE` with `--update-baseline` and `baseline_carry.py` | Local Canon | Plan D-20; ran five times cleanly. | — |
| D-21 | planning | Electron flatten → revert against the real backend? | autonomous | Mocked REST routes with a ledger | Local Canon | The real backend is covered by contract tests and the audit (plan D-21). | — |
| D-22 | planning | The converted PNG's name; the JPEG's marks | autonomous | `[stem]-converted.png`, then `_n`; the source is never touched | Local Canon | Plan D-22. | — |
| D-23 | planning | JPEG/WebP Save overlay copies | autonomous | `ANNOTATED_FORMATS`, one sibling at a time, quality 90 | Local Canon | Plan D-23. | — |
| D-24 | planning | MCP user confirmation behaviour | autonomous | `USER_CONFIRM` over elicitation; only accept + `confirm: true` runs | Local Canon | Plan D-24. Extended by A-9 and A-11; review F1 closed the id-injection gap. | — |
| D-25 | execution | Where do `USER_CONFIRM_ACTIONS`, the timeout and messages live? | autonomous | `src/destructive.ts`; a throw is `cancel` | Local Canon | MEU-67 handoff D-25. | — |
| D-26 | execution | How does the audit require all three flatten probe fields to change? | autonomous | `destructiveStep` `confirmedEffect` | Local Canon | MEU-67 handoff D-26. | — |
| D-27 | execution | How does `FLATTEN_STATUS` detect a backup? | autonomous | Compare `backup_path` before and after | Local Canon | MEU-67 handoff D-27. | — |
| D-28 | execution | The docstring rewrap changed an OpenAPI path | autonomous | Restore the baseline docstring | Local Canon | MEU-67 handoff D-28. | — |
| A-1 | planning | Where do execution and the gate run? | human | The Sessions 25–29 split | Human-approved | human-gate-decision.md §A-1. | USER_EXPLICIT 2026-10-02 'Split like Sessions 25–29 (Recommended)' |
| A-2 | planning | Convert trigger, save formats, MCP confirmation | human | On Apply; Save overlay copy formats; ask the user via MCP | Human-approved | §A-2 (AskUserQuestion answers). | USER_EXPLICIT 2026-10-03 'On Apply to image (Recommended)' / 'Save overlay copy (Recommended)' / 'Ask the user via MCP (Recommended)' |
| A-3 | execution | Three census-found pins (TA-8) | human | Approve TA-8 | Human-approved | §A-3. | USER_EXPLICIT 2026-10-03 'Approve TA-8 (Recommended)' |
| A-4 | execution | The `bake` signature pin (TA-9) | human | Approve TA-9 | Human-approved | §A-4. | USER_EXPLICIT 2026-10-03 'Approve TA-9 (Recommended)' |
| A-5 | execution | The AC-12.8 guard vs creating the backup folder in the service | human | `ImageAnnotatePort.ensure_dir` | Human-approved | §A-5; no test expectation changed. | USER_EXPLICIT 2026-10-03 'Port method (Recommended)' |
| A-6 | execution | F1: the disabled reason never shows | human | A wrapper span carrying the title | Human-approved | §A-6. | USER_EXPLICIT 2026-10-03 'Wrapper span (Recommended)' |
| A-7 | execution | The MCP setup prompt; F8 | human | `MCP-SETUP-PROMPT` as its own MEU; F8 by hand | Human-approved | §A-7. | USER_EXPLICIT 2026-10-03 'Separate MEU, F8 by hand (Recommended)' |
| A-8 | execution | Registry drift at the attempt-2 preflight | human | Accept the new hash; `-AcceptDrift` | Human-approved | §A-8; its scope gap became F3/A-13. | USER_EXPLICIT 2026-10-04 'Accept new hash (Recommended)' |
| A-9 | execution | The empty `tools/list` schema blocks F8 | human | Fix in Session 30 (`ADVERTISED_SCHEMA`) | Human-approved | §A-9; implemented by rewriting `tools/list`, keeping the registered union. | USER_EXPLICIT 2026-10-04 'Fix in Session 30 (Recommended)' |
| A-10 | execution | No native tooltips anywhere | human | A rendered `role="tooltip"` reason | Human-approved | §A-10. | USER_EXPLICIT 2026-10-04 'Rendered tooltip (Recommended)' |
| A-11 | execution | Claude Code auto-declines elicitation | human | A Windows dialog fallback | Human-approved | §A-11 (local agent). | USER_EXPLICIT 2026-10-04 'can you just make the ammendemnts and change code now?' |
| A-12 | execution | Overlay `validated_against` stale after the registry moved | human | Revalidate (the A17 rule) | Human-approved | §A-12. | USER_EXPLICIT 2026-10-07 'go 1–2' |
| A-13 | execution | Framework HEAD and registry moved since A-8 (review F3) | human | Accept both; revalidate the overlay; `-AcceptDrift A-13` | Human-approved | §A-13. | USER_EXPLICIT 2026-10-10 'ok i'm fine with A-13' |
| A-14 | execution | The shared registry renamed models, so the overlay bindings broke | human | Follow the renames (same efforts) | Human-approved | §A-14; the fourth row (the Codex reviewer binding) is disclosed there. | USER_EXPLICIT 2026-10-10 'yes' |

The triage decisions in `known-issues.yaml` (D-14 and D-15 of `CAPTURE-FLATTEN-WITH-BACKUP`) are cited in prose only, because their ids collide with this plan's. The review-route changes are recorded in `human-review-decision.md`: Fable 5.1 for the plan review and execution Round 1; then Opus 5.5, which never ran a round; then Codex CLI `gpt-6.1-sol` from Round 2.

---

## Pattern Extraction

### Patterns to KEEP
1. **Reproduce a review High before fixing it.** F1's reproduction showed the WHATWG URL normalisation that made the traversal real, and it shaped the fix: encode every path parameter, not only capture ids.
2. **Red against the real renderer for UI affordances.** The A-6 and A-10 Electron tests were run on the pre-fix build. jsdom passed on attributes that never rendered.
3. **One A-decision per surprise, with the quote.** Fourteen decisions, none silent. Two scope gaps (A-8's wording, A-9's implementation) were disclosed and caught in review, not hidden.

### Patterns to DROP
1. **Treating the SDK `Client` as a proxy for real MCP clients.** It is typed and fully elicitation-capable, which Claude Code is not.

### Patterns to ADD
1. **A real-IDE MCP smoke step in the container pre-gate request**, before the look: register the server in the target IDE and call one destructive action with decline, then accept.
2. **An opaque-id rule** for any value interpolated into a human-facing prompt or a URL path. Put it in the FIC, with a hostile-id negative test.
3. **A census pass over guard tests** (layering, no-`mkdir`, forbidden imports), alongside literal pins, at row 1.
4. **Pin the agentic-framework HEAD and the registry hash in the plan**, and make the gate's drift acceptance name the exact inputs.

### Calibration Adjustment
- Estimated time: one session plus one Windows gate loop and an MCP audit.
- Actual time: one long cloud session over nine days; five `LOCAL_SEQUENCE` attempts; two execution review rounds.
- Adjusted estimate for similar MEUs (a new MCP destructive surface plus GUI): plan for two look → fix → re-gate loops, and one real-IDE MCP check before the first look.

---

## Next Session Design Rules

```
RULE-1: Every MCP plan that adds a user-facing confirmation or new input types includes a real-IDE smoke step (register, list tools, one destructive call: decline then accept) before FLATTEN_LOOK-style looks.
SOURCE: F8 failed three times for client behaviour the SDK Client never shows (empty schema → string confirm; auto-declined elicitation).
EXAMPLE: "AC-67.31 through the SDK Client" → plus "Claude Code VS Code: /mcp shows the server; remove a disposable shot; Decline then Accept".
```

```
RULE-2: Any id that reaches a human prompt or a URL path is validated as an opaque token at the boundary, and path parameters are always percent-encoded.
SOURCE: Execution review round 1 F1 (High): agent text in the "Allow?" prompt; `/../` traversal.
EXAMPLE: `id: z.string().min(1)` → `id: z.string().regex(OPAQUE_ID)`; `interpolatePath` → `encodeURIComponent` per segment.
```

```
RULE-3: The row-1 census includes guard tests that forbid an implementation shape (layering, mkdir, imports), not only pinned literals.
SOURCE: A-5: the AC-12.8 no-mkdir guard surfaced only in the full pre-gate run.
EXAMPLE: census patterns `bake\(` … → plus `rg -l "ast.parse|forbidden|no_direct" tests/` with a disposition per hit.
```

---

## Next Day Outline

1. **`/plan-corrections` for Session 30's open plan-text items:**
   - Review F6, the four stale plan wordings.
   - The Files Modified row for `tests/tooling/test_framework_adoption.py` (edited by A-14 in `306b07e`). Without it, `validate-task.sh api-scope` reports that file as outside scope.
2. **Follow-ups filed during this session:**
   - `MCP-SETUP-PROMPT` (medium)
   - `CAPTURE-TOOLTIPS-NOT-SHOWN` (medium)
   - `MCP-ELICITATION-VSCODE-AUTO-DECLINE`
   - `CAPTURE-BAKE-ARROW-THIN` (raised to medium)
   - the capture editor items: Eraser, Pixelate, the context menu, multi-select, the action-row icons, the banner gap, Sample original, the stale `annotated_path`
   - `TOOLING-SHARED-REGISTRY-COUPLING` (now medium, after three recurrences).
3. **Next:** Session 31 per the grouping. The 2026-10-09 triage adds Sessions 32–39.
4. **Review route:** Codex CLI via the local agent (vendor-distinct) unless the user changes it.
5. **Bake in RULE-1 to RULE-3.**

---

## Efficiency Metrics

| Metric | Value |
|--------|-------|
| Total tool calls | not tracked precisely (several hundred, cloud) |
| Time to first green test | 2026-10-03 (row 3, Python Green, the first execution day) |
| Tests added | Python: 21 AC-67 / review tests (new contract file plus appends). MCP Vitest: 26 `it` blocks in `user-confirm.test.ts` (many `it.each`), plus 15 AC-67 tests in capture/audit suites. UI Vitest: about 29 AC-67 tests. Electron: 6 AC-67 specs. |
| Codex findings | Plan review (Fable 5.1): R1 changes_required (1 High, 4 Medium, 5 Low); R2 changes_required (procedural); R3 approved. Execution review: R1 changes_required (Fable 5.1: 1 High, 1 Medium, 4 Low); R2 approved (Codex gpt-6.1-sol, 0 findings) |
| Handoff Score (X/7) | 5/7 (review F2: the handoff lagged A-11/A-12 and omitted AC-67.36; F6 plan wording) |
| Rule Adherence (%) | 85 |
| Prompt→commit time | 2026-10-02 → 2026-10-10 (review approval) |

### Rules Sampled for Adherence Check

| Rule | Source | Followed? |
|------|--------|-----------|
| Tests before production code; Red before Green | AGENTS.md §Testing & TDD | Yes, including every correction (A-5 to A-10, review F1/F4/F5) |
| No test expectation change without approval | AGENTS.md §Testing & TDD | Mostly. TA-1..TA-9 were approved. Two disclosed title-only edits under TA-1. One same-session assertion was moved to the A-6 wrapper and disclosed. A-14's expectation change was approved by Mat |
| Independent review; no self-approval | AGENTS.md §Independent review | Yes. The author never wrote a verdict. Round 2 is vendor-distinct; earlier rounds used the disclosed same-vendor route |
| Product scope limited to the Files table | Plan `PRODUCT_SCOPE` | Partly. The `PathRow.tsx` edit was caught and reverted. A-14's test edit is still missing from the table (routed to `/plan-corrections`) |
| A gate failure gets an A-decision, never a silent fix | cloud-local §3.5 | Yes (A-5 to A-14) |

---

## Instruction Coverage

```yaml
schema: v1
session:
  id: "session-30-capture-flatten-backup-2026-10-11"
  task_class: tdd
  outcome: success
sections:
  - {id: priority_0_system_constraints_non_negotiable, cited: true, influence: 3}
  - {id: execution_contract, cited: true, influence: 3}
  - {id: testing_tdd_protocol, cited: true, influence: 3}
  - {id: session_discipline, cited: true, influence: 2}
  - {id: dual_agent_workflow, cited: true, influence: 3}
  - {id: instruction_coverage_reflection, cited: true, influence: 2}
loaded:
  workflows: [create_plan, execution_session, execution_critical_review, execution_corrections]
  roles: [orchestrator, coder, tester]
  skills: [issue_triage]
  refs:
    - .agent/docs/harness-profiles.md
    - .agent/context/harness.local.md
    - .agent/docs/cloud-local-collaboration.md
    - .agent/docs/human-decision-protocol.md
    - .agent/schemas/reflection.v1.yaml
    - docs/build-plan/05-mcp-server.md
    - docs/build-plan/09-screenshot-capture.md
    - docs/build-plan/11-page-layout.md
    - docs/execution/plans/2026-10-02-capture-flatten-backup/implementation-plan.md
    - docs/execution/plans/2026-10-02-capture-flatten-backup/task.md
    - docs/execution/plans/2026-10-02-capture-flatten-backup/human-gate-decision.md
    - docs/execution/plans/2026-10-02-capture-flatten-backup/human-review-decision.md
decisive_rules:
  - P1:tests-before-production-corrections
  - P1:human-approval-for-test-changes
  - P1:independent-review-no-self-approval
  - P1:no-tolerated-failure-in-authoritative-gate
  - P0:never-delete-user-files-without-explicit-user-instruction
conflicts:
  - "The plan's FLATTEN_SEQUENCE has the service create the backup folder, while the MEU-12 guard forbids mkdir in services; resolved by A-5 (port method)."
  - "A-9's option text said 'passthrough' on a registered flat schema; doing that literally would change an existing test (m7-resource.test.ts). Implemented by rewriting tools/list instead, and disclosed."
  - "AGENTS.md requires a vendor-distinct reviewer, but the Codex CLI was absent in the container; the user-authorized same-vendor Fable route was used until Round 2 moved to Codex CLI via the local agent."
  - "The execution-corrections write scope forbids plan edits, so review F6 and the A-14 Files-table row wait for /plan-corrections."
  - "The RTK receipt contract assumes rtk, which the container lacks; receipts used plain redirects with immediate exit capture."
note: "Session 30 ships flatten-with-backup, revert, JPEG/WebP convert-on-apply, Save overlay formats and MCP flatten/revert behind user confirmation (elicitation, or a Windows dialog when the IDE auto-declines). The Windows gate of record is attempt 5 on 81fdda7 (Vitest 773, Playwright 133/0/0, pytest 655/0, audit 98/99 with the one standing tts.cancel). FLATTEN_LOOK F1–F8 pass. Execution review approved in Round 2 (Codex gpt-6.1-sol, 0 findings) after Round 1's F1 High (id injection and traversal) was fixed."
slim_candidate: ["The MEU handoff restates gate evidence and corrections that walkthrough.md already holds; keeping both in sync caused review F2"]
overthinking_observed: false
review_churn:
  rounds_to_approval: {plan: 3, execution: 2}
  findings_per_round:
    - {review: plan, round: 1, critical: 0, high: 1, medium: 4, low: 5}
    - {review: plan, round: 2, critical: 0, high: 0, medium: 0, low: 0}
    - {review: plan, round: 3, critical: 0, high: 0, medium: 0, low: 0}
    - {review: execution, round: 1, critical: 0, high: 1, medium: 1, low: 4}
    - {review: execution, round: 2, critical: 0, high: 0, medium: 0, low: 0}
  churned_findings: 0
  finding_categories: {security: 1, claim_to_state_drift: 3, missing_edge_test: 1, provenance: 1}
  verdicts: {changes_required: 3, approved: 2}
meu_work_classes: [correctness]
```
