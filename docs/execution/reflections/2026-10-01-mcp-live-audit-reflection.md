---
date: "2026-10-01"
project: "mcp-live-audit"
meus: ["MEU-68"]
plan_source: "docs/execution/plans/2026-10-01-mcp-live-audit/implementation-plan.md"
template_version: "2.0"
---

# 2026-10-01 Meta-Reflection

> **Date**: 2026-10-01
> **MEU(s) Completed**: MEU-68 (`mcp-live-audit`)
> **Plan Source**: docs/execution/plans/2026-10-01-mcp-live-audit/implementation-plan.md

---

## Execution Trace

### Friction Log

1. **What took longer than expected?**
   The authoritative gate took three Windows attempts, and none of them failed on the product. Attempt 1 passed but certified a transcript domain that had fetched nothing: the pause landed before item 0 on every cycle. The round-1 reviewer caught it (F1). Attempt 2 proved the fix live (`transcripts_done 1`, a 112,681 B volume). Attempt 3 followed only because Mat chose to fix the round-2 test finding (R2-1) at once. The container pregates also kept meeting new forms of YouTube's datacenter wall: the bot text, then `HTTP 403` on the media fetch. Each form needed a census proof, not a skip.

2. **What instructions were ambiguous?**
   The census rule says "signature AND environment proof", but not how strong the proof must be. `download.cancel` started with a host-only proof; round 1 called it weak (OOC-2), and A13 replaced it with a per-URL reproduction. The H2-1 reflection command also listed the shared grouping as a decision source, even though this plan's D-1…D-7 reuse the grouping's IDs with a different stage. No document warns that plan decision IDs must not collide with the grouping's §8 IDs (A14).

3. **What instructions were unnecessary?**
   Restating all 17 plan decisions in the handoff's Decision Log. The plan is already a decision source, and the restated copies only added a second place where IDs could collide.

4. **What was missing?**
   - A rule that the audit plan's observable for every lifecycle row is asserted step by step. The plan row said "poll until ≥ 1 item is terminal", and the implementation silently dropped it. Neither the plan review nor my own Part A self-review caught it; only the execution review did.
   - A check in the runner that a never-ready backend is stopped (D-19). It surfaced only as a 590 s hang.

5. **What did you do that wasn't in the prompt?**
   - Fixed a sibling defect found while verifying round 1 (S1: never-ready backend leak).
   - Restored the plan's `requeue` 409 contract (OOC-3).
   - Strengthened the `download.cancel` proof (A13).
   - Filed R3-1 as `MCP-AUDIT-CENSUS-PROBE-SINGLE-SHOT`.

### Quality Signal Log

6. **Which tests caught real bugs?**
   - `transcript-oracle.test.ts` encodes F1. It would have failed the Windows run had it existed at Red.
   - `run-cli.test.ts`, the F2 missing-baseline case.
   - `backend-spawn.test.ts`, the leak (S1).
   - The live runner itself found five product defects, all filed: `MCP-TOOLS-LIST-EMPTY-INPUT-SCHEMA`, `MCP-TTS-GENERATE-SYNCHRONOUS`, `API-UNHANDLED-ERROR-OPAQUE`, `MCP-INSTRUCTIONS-CAPTURE-REMOVE-FILES`, and `MCP-PACKAGED-ENTRY-UNREACHABLE` (candidate).
   - The census correctly refused the 403 form of the wall on `9e186da`, which is what forced A13.

7. **Which tests were trivially obvious?**
   - The neutral-stub tests that passed at Red (15 of 96). Each was paired with a failing negative, but they proved little on their own.
   - The `docs.test.ts` frontmatter shape.

8. **Did pyright/ruff catch anything meaningful?**
   Not applicable: no Python changed. `tsc -p tsconfig.scripts.json` (AC-68.17) caught nothing after the Red probe, but it now covers the runner in the D6 `mcp-types` stage.

### Workflow Signal Log

9. **Was the FIC useful as written?**
   Yes, for the oracle names (`OBSERVABLE_RULE`, `REFUSAL_ORACLE`, `CLEANUP_PREDICATE`), which made every review finding concrete. The transcript row was the exception: its observable lived only in table prose, so it could be dropped without any test noticing.

10. **Was the handoff template right-sized?**
    It was right-sized for one MEU. The AC-coverage validator reads `AC-68.x` as the single ID `AC-68`, so it proved nothing about the 18 rows; I added a separate check.

11. **How many tool calls did this session take?**
    About 400 (orchestrator), plus three reviewer subagent rounds of 43–55 calls each and one plan review.

12. **Which rows were delegated, to which subagent (harness + model), and did any delegated result need rework?**
    None of the execution rows were delegated. The plan review and the three execution reviews went to Fable 5.1 subagents (Claude Code Agent tool), the user-authorized route (H-1). No reviewer output needed rework: every finding was verified against the code before correction, and all were real.

### Decisions Log

| ID | Stage | Question | Resolution | Chosen | Source tag | Reasoning (why this; why the alternatives lost) | Human ref |
|----|-------|----------|------------|--------|------------|--------------------------------------------------|-----------|
| H-1 | planning | Codex CLI is unavailable in the cloud container; who reviews the plan and the execution? | human | Fable 5.1 subagent (Recommended) | Human-approved | Only vendor-distinct machine rung (Codex) is absent; PROFILE B4 human review costs a round trip per round. Same-vendor deviation disclosed in human-review-decision.md. | USER_EXPLICIT 2026-10-01 AskUserQuestion answer 'Fable 5.1 subagent (Recommended)' |
| H-2 | planning | Which backend does the authoritative audit hit, given destructive clear/remove and settings.set? | human | Isolated spawned backend (Recommended) | Human-approved | download.clear/convert.clear against the user's live app would wipe real queues; an isolated backend runs every action with real binaries and no user-data risk. | USER_EXPLICIT 2026-10-01 AskUserQuestion answer 'Isolated spawned backend (Recommended)' |
| H-3 | planning | MEU-68 depends on unplanned MEU-62; wait, or build now and baseline later? | human | Build now, baseline later | Human-approved | User chose parallelism over the recommended wait. D-4's intent is preserved: only the baseline waits for MEU-62 (SEQUENCING_GATE before Part B); PART_A_PATHS keeps Part A off Session 27's files. | USER_EXPLICIT 2026-10-01 AskUserQuestion answer 'Build now, baseline later' |
| H-4 | planning | Execution authorization and gate location: where does the authoritative audit run, and is execution authorized? | human | A. Split like Sessions 25 and 26: container Part A plus one Windows WINDOWS_GATE triggered by Mat; commits, pushes and the row-9 origin/main merge on claude/sweet-goodall-mu69td authorized; no PR, merge to main, release or deploy | Human-approved | The authoritative run needs Windows (capture, real downloads); the container builds and proves everything else. SIGN 1 and plan_to_exec_gate human make execution wait for the user. | USER_EXPLICIT 2026-10-01 'proceed' (human-gate-decision.md §H-4) |
| H-5 | execution | F5: does avkit_tts.cancel's failure trigger the Stop Condition for MEU-62's surface (tts.*)? | human | Ratify D-14 (Recommended) | Human-approved | The failure is the pre-existing synchronous route, not MEU-62's asset work; the reviewer judged the classification defensible and asked for one-line human ratification. | USER_EXPLICIT 2026-10-01 AskUserQuestion answer 'Ratify D-14 (Recommended)' (human-gate-decision.md §F5) |
| H-6 | execution | R2-1: fix the silent early return in coverage.test.ts now (WINDOWS_GATE attempt 3) or file it and fix later? | human | Fix now + attempt 3 | Human-approved | The user preferred a clean session over a deferred known issue; attempt 3 costs one short Windows run. | USER_EXPLICIT 2026-10-01 AskUserQuestion answer 'Fix now + attempt 3' (human-gate-decision.md §R2-1) |
| D-1 | planning | Runner language and location: mcp-server/scripts/audit.ts or tools/mcp_audit.py? | autonomous | TypeScript under mcp-server/scripts/audit/, run with tsx, typechecked through tsconfig.scripts.json | Local Canon | TS reuses the server's SDK and zero new dependencies; Python would add the mcp package to uv.lock (a GATED_PATHS change Session 27 also touches). Two-way: the runner is dev tooling, not shipped. | — |
| D-2 | planning | SDK client or MCP Inspector --cli? | autonomous | SDK Client over stdio | Research-backed | One session for 67+ calls keeps server state and stderr in one place and allows typed per-step assertions; Inspector would spawn a server per call, coerce argument types, and add an npx dependency. | — |
| D-3 | planning | How does the runner know the expected action set without importing toolsets? | autonomous | Runner reads tools/list (inputSchema action literals + _meta.action_descriptions); a Vitest test (not the runner) proves AUDIT_PLAN and the baseline cover ACTION_INDEX | Local Canon | Keeps the runner a pure IDE-equivalent client while drift between code and audit plan still breaks npm test. | — |
| D-4 | planning | What counts as a refusal for a destructive call without confirm? | autonomous | isError:true AND observable unchanged; accept handler validation_error/confirm_required or SDK 'Input validation error' text | Research-backed | Over a real client the SDK may reject before the handler, so the text varies by layer; the state check is the actual control and cannot be satisfied by any refusal that mutates. | — |
| D-5 | planning | 05 §MCP live audit names actions that do not exist (download status, settings reset/apply_defaults, health gpu/gpu_refresh); which governs? | autonomous | ACTION_INDEX governs; correct the spec text (AC-68.18) and the GUI-action-index claim | Local Canon | The audit must exercise what the server serves; inventing actions would violate 05 §What this layer must not do. | — |
| D-6 | planning | Fix the packaged-entrypoint/node_modules defect found during planning? | autonomous | No; file MCP-PACKAGED-ENTRY-UNREACHABLE as a hypothesis known issue (row 1) and add an optional non-blocking packaged probe to the Windows request | Local Canon | Packaging is Phase 7 scope and touches mcp-server/src and the installer; widening MEU-68 would break PART_A_PATHS isolation from Session 27. The probe turns the hypothesis into target evidence at no extra round trip. | — |
| D-7 | planning | Which live YouTube fixtures? | autonomous | AUDIT_FIXTURES: jNQXAC9IVRw (19 s) for the downloaded file, dQw4w9WgXcQ (backend SABR_PROBE_URL) as second queue item, @jawed one-video channel for transcripts; all overridable by flag | Research-backed | Smallest stable public media keeps the run short and read-only (PROFILE E3); a one-video channel bounds the transcript job. Overrides cover a removed video without a code change. | — |
| D-8 | planning | Spec says the container may run a 'mocked-backend subset'; what runs in the container? | autonomous | Vitest fake-backend integration (mocked) AND a container run of the real runner against a real spawned backend, labelled non-authoritative, with ENV_BOUND_AUDIT; capture seeded via REST register mode | Local Canon | Strictly more evidence than a mocked-only subset and still never authoritative; the fake backend is what makes the negative oracles (hollow, refusal_mutated) deterministic. | — |
| D-9 | planning | Where does the baseline live? | autonomous | .agent/skills/mcp-tool-audit/resources/baseline-snapshot.json | Local Canon | 05 names resources/baseline-snapshot.json without a root; the reference skill's layout resolves it. | — |
| D-10 | planning | Compute the Zorivest consolidation score? | autonomous | No; the report states consolidation n/a (8 compound tools, consolidation already done) | Local Canon | The score's ideal (13) is a Zorivest target; av-kit has no consolidation backlog. | — |
| D-11 | planning | rtk is absent in the container; how do container rows run? | autonomous | Raw invocation (unfiltered equivalent of rtk proxy) in the container; rtk proxy on Windows | Local Canon | Unfiltered output preserves exact evidence; the Windows gate keeps the RTK contract. | — |
| D-12 | execution | The real server lists an empty inputSchema for every tool; how does the audit treat a product defect it finds in discovery? | autonomous | Report it as a discovery finding (AC-68.3 unchanged), file MCP-TOOLS-LIST-EMPTY-INPUT-SCHEMA, read the action set from _meta.action_descriptions, and let the gate scripts tolerate only filed findings (FILED_FINDINGS, amendment A2) | Local Canon | Fixing mcp-server/src breaks PART_A_PATHS and Session 27 isolation; silently passing discovery would hide the exact defect class the audit exists to catch. Two-way: when the issue is fixed the finding disappears and the baseline records FIXED. | — |
| D-13 | execution | Which fixtures and step sequences make every lifecycle step's precondition deterministic against the real state machines? | autonomous | 4-video watch_videos playlist with a 3 s delay (two pause→stop cycles give Cancelled for requeue and retry; a 409 contract on Pending); three convert jobs (short, long, long), with a deferred pause that takes effect after the current job; a Big Buck Bunny download as the cancel target; REST-register capture seed (source scan) | Local Canon | A one-video channel completes before a pause lands, so the Processing/Cancelled/Failed preconditions for requeue/retry are unreachable on a fast host (the R2-3 risk). The inter-item delay gives a deterministic pause window. Two-way: the fixture flags override every URL. | — |
| D-14 | execution | TTS generate is synchronous, so a running job's id is never available to a client; how does the audit exercise avkit_tts.cancel? | autonomous | Run the REFUSAL_ORACLE on the finished job; the confirmed cancel's no-effect is a failure carrying MCP-TTS-GENERATE-SYNCHRONOUS (FILED_STEP_FAILURES), not a skip or a weakened oracle | Local Canon | Cancelling a running job is unreachable through any client, so no honest pass is possible; a REST-side workaround would hide the defect the audit exists to surface. | — |
| D-15 | execution | The row-9 merge brought MEU-62's avkit_models.download_asset; do the registry-tied test counts change from 67 to 68? | autonomous | Yes (amendment A7): AUDIT_ACTION_COUNT=68, two download_asset steps in AUDIT_PLAN, coverage.test.ts and the fake-backend discovery count move to 68; flagged for the execution reviewer | Local Canon | The expectation tracks the served surface, which the approved dependency changed; keeping 67 would make the coverage test assert a stale registry. The change is source-backed and confined to the two count assertions. | — |
| D-16 | execution | The watch_videos fixture breaks the backend adapter and the bot wall is per video; how are the transcript fixture and the network census proof made deterministic? | autonomous | Amendment A9: a Blender Studio 9-video playlist replaces watch_videos; the ENV_BOUND_AUDIT network proof is per failing step URL (NETWORK_STEP_URLS); download.cancel joins the census with the bot-wall signature and a container-host proof | Local Canon | A fixture that fails on every host is a test defect, not an env bound; a per-URL proof keeps tolerance exact where the coarse proof would either refuse a real bot wall or excuse a URL that extracted fine. Windows ran all of it live with zero skip_env. | — |
| D-17 | execution | Three container-only assumptions would break the Windows gate (CRLF frontmatter, shell-quoted uv spawn, drive-letter case in isMain); fix before the request or let the gate find them? | autonomous | Fix before the request: the docs.test.ts frontmatter regex accepts \r?\n, uv is spawned without a shell, and run.ts compares the entry path case-insensitively on win32 | Local Canon | Each is a portability defect in test or runner code, not a behavior change; the CRLF regex change widens a line-ending match without changing what it asserts and is flagged for the reviewer. Fixing first made attempt 1 pass. | — |
| D-18 | execution | transcript.compile produced a 37 B volume on Windows; was the transcript oracle sound? | autonomous | No (review F1). Restore the plan's observable: transcript.resume polls until a transcript is fetched or an item Failed, transcript.compile requires transcripts_done >= 1 and a matching Contents count, and a container-only census member covers the IP-blocked caption fetch (amendment A11); WINDOWS_GATE attempt 2 re-records the baseline | Local Canon | The first reading (no captions on live VODs) was a hypothesis; the pause landed before item 0 on every cycle, so nothing was fetched and the audit certified an empty transcript, the G25 hollow case. Restoring the approved observable costs one Windows run; accepting it would leave the transcript domain unproven. | — |
| D-19 | execution | A backend that never prints AVKIT_READY left its child process running, which held the runner open until an outer timeout; fix inside MEU-68? | autonomous | Yes: startBackendProcess stops the child (SIGTERM, then SIGKILL) before rethrowing and names its pid; spawnBackend delegates to it | Local Canon | The runner owns the processes it spawns; a hung authoritative run would cost a Windows round trip. The fix is local to the runner and covered by a cross-platform test (node as the never-ready child). | — |
| D-20 | triage | Build an MCP audit workflow? | human | Yes: execute every MCP call from the IDE against the local API; adapt the Zorivest skill | Human-approved | The user specified this behaviour directly; no fork remains. | USER_EXPLICIT 2026-09-30 'we need to create mcp audit workflow that will execute each MCP call in IDE to ensure everything works via local API as it should' |
| D-21 | triage | Home and harness | autonomous | Product MEU under Phase 5 (05-mcp-server.md), delivering .agent/workflows/mcp-audit.md + .agent/skills/mcp-tool-audit/SKILL.md + a runner that drives the built server as a real stdio client (MCP Inspector CLI or the SDK client) with a committed baseline-snapshot.json; authoritative run is a local Windows stage per cloud-local-collaboration.md | Research-backed | Precedent (MEU-23) and sources converge; two-way. | — |
| D-22 | execution | The container's YouTube wall also appears as HTTP 403 on the media fetch, outside the download.cancel census signature; how is it tolerated without weakening the census? | autonomous | Amendment A13: the signature also matches 'HTTP Error 403: Forbidden', and the proof becomes the container host AND a direct yt-dlp test fetch of download_url_c failing with the same wall (mediaFetchBlocked) | Local Canon | The census refused the new form correctly; the fix accepts it only with a per-URL reproduction, which is stronger than the previous host-only proof. Authoritative mode tolerates nothing, and attempt 3 passed download.cancel live. | — |
| G-D-2 | grouping | Residual MEUs under their original phases, or a new Phase 12? | autonomous | Original phases with `(residual)` sections (MEU-68 under Phase 5) | Local Canon | Precedent MEU-59/60/61; a new phase would split the canon. Carried from the grouping §8 D-2. | — |
| G-D-4 | grouping | Where does the MCP audit sit in the order? | autonomous | Session 28, right after the TTS repair | Local Canon | The first baseline should record a working `tts.generate` (it does: attempt 3) and serve as the regression net for Sessions 29–31. Carried from the grouping §8 D-4. | — |
| G-D-5 | grouping | Are the TECH-DEBT/DEFER rows MEUs in this batch? | autonomous | No | Local Canon | `issue-triage.md` routes TECH-DEBT to a debt batch; this session filed its own R3-1 as TECH-DEBT accordingly. Carried from the grouping §8 D-5. | — |

---

## Pattern Extraction

### Patterns to KEEP
1. Fail-closed census with a per-URL reproduction. It refused two new forms of the YouTube wall instead of passing them.
2. Verifying every reviewer finding against the code and a live probe before correcting it (F1 was confirmed in the worker loop, F2 with the fake backend).
3. A pregate on the exact request tree before every Windows attempt. It caught the 403 form before Mat spent a run on it.

### Patterns to DROP
1. A container-only cause written as a decision without a probe (D-18's "no captions"). It was a hypothesis, and it was wrong.

### Patterns to ADD
1. Every plan-table observable becomes a named assertion in a test at Red, not prose that the implementation must remember.
2. Plan decision IDs start after the consuming grouping's §8 IDs and after the source issue's enrichment IDs.
3. The gate request block is copied from the script's actual parameters (`-QuietMachineConfirmed` was dropped in attempt 2).

### Calibration Adjustment
- Estimated time: one session, with a single Windows gate.
- Actual time: one long session, three Windows gates, three execution-review rounds.
- Adjusted estimate for similar MEUs: budget two Windows gates for any live-audit or live-network MEU.

---

## Next Session Design Rules

```
RULE-1: Every observable in a plan lifecycle table has a named unit test over the step's observe() before Green.
SOURCE: review round 1 F1 (transcript item-terminal observable dropped silently).
EXAMPLE: "poll until ≥ 1 item terminal" (prose) → transcript-oracle.test.ts "resume fails while no item is terminal".
```

```
RULE-2: An environment-bound tolerance's proof reproduces the failure on the same input, never just the host.
SOURCE: OOC-2 and A13 (download.cancel host-only proof; 403 form).
EXAMPLE: envProof platform != win32 → platform != win32 AND mediaFetchBlocked(download_url_c).
```

```
RULE-3: Plan decision IDs never reuse IDs from the consuming grouping §8 or the source issue's enrichment.
SOURCE: A14 (D-1..D-7 vs grouping D-1..D-7; handoff D-20 vs issue D-20).
EXAMPLE: plan D-1..D-14 → plan D-8.. (Session 27 did this).
```

---

## Next Day Outline

1. Target: Session 29, per the grouping (Capture residuals). The MEU-68 baseline is now the regression net: run `/mcp-audit` authoritatively after any MCP-surface change.
2. Scaffold: none needed. Carry the follow-ups: `MCP-TOOLS-LIST-EMPTY-INPUT-SCHEMA` and `MCP-TTS-GENERATE-SYNCHRONOUS` (both high), `MCP-AUDIT-CENSUS-PROBE-SINGLE-SHOT` (low).
3. Patterns to bake in: RULE-1 to RULE-3.
4. Validation scope: an execution review on the same route, if the user keeps it.
5. Time estimate: one session, plus one or two Windows gates.

---

## Efficiency Metrics

| Metric | Value |
|--------|-------|
| Total tool calls | ~400 orchestrator + ~200 reviewer |
| Time to first green test | Same day (row 3, 73 unit tests) |
| Tests added | 112 audit tests (MCP suite 222 → 334 with MEU-62's merge) |
| Codex findings | Not applicable (Fable route). Plan: r1 3H/4M/2L, r2 0H/1M/4L. Execution: r1 3M/2L, r2 1M, r3 1L. |
| Handoff Score (X/7) | 6/7 (stale counts corrected after round 2) |
| Rule Adherence (%) | 90 |
| Prompt→commit time | Same day |

### Rules Sampled for Adherence Check

| Rule | Source | Followed? |
|------|--------|-----------|
| Tests first; Red assertions never edited in Green | AGENTS.md §Testing & TDD Protocol | Yes. Every correction had a Red. One not-yet-committed test was tightened together with its step before commit (round 2 judged it legitimate). |
| Independent review; the implementer never writes `approved` | AGENTS.md §Dual-Agent Workflow | Yes. The corrections set `corrections_applied`. |
| A product defect found by the audit becomes a known issue, not a fix | Plan §Stop Conditions | Yes (5 filed). |
| No silent skips or early returns in tests | AGENTS.md §Testing | No at first (R2-1); fixed under H-6. |
| Gate request matches the script's parameters | cloud-local §5.1 | No in attempt 2 (`-QuietMachineConfirmed` omitted). |

---

## Instruction Coverage

```yaml
schema: v1
session:
  id: "session-28-mcp-live-audit-2026-10-01"
  task_class: tdd
  outcome: success
sections:
  - {id: priority_0_system_constraints_non_negotiable, cited: true, influence: 2}
  - {id: execution_contract, cited: true, influence: 3}
  - {id: testing_tdd_protocol, cited: true, influence: 3}
  - {id: planning_contract, cited: true, influence: 3}
  - {id: session_discipline, cited: true, influence: 2}
  - {id: dual_agent_workflow, cited: true, influence: 3}
  - {id: instruction_coverage_reflection, cited: true, influence: 2}
loaded:
  workflows: [create_plan, plan_critical_review, execution_critical_review, execution_corrections]
  roles: [orchestrator, coder, tester]
  skills: []
  refs:
    - .agent/docs/harness-profiles.md
    - .agent/context/harness.local.md
    - .agent/docs/cloud-local-collaboration.md
    - .agent/docs/human-decision-protocol.md
    - .agent/docs/output-evidence-policy.md
    - .agent/schemas/reflection.v1.yaml
    - docs/build-plan/05-mcp-server.md
    - _inspiration/_zorivest_mcp_tool_audit_skill.md
    - docs/execution/plans/2026-10-01-mcp-live-audit/implementation-plan.md
    - docs/execution/plans/2026-10-01-mcp-live-audit/task.md
    - docs/execution/plans/2026-10-01-mcp-live-audit/human-review-decision.md
    - docs/execution/plans/2026-10-01-mcp-live-audit/human-gate-decision.md
decisive_rules:
  - P1:tests-before-production-corrections
  - P1:independent-review-no-self-approval
  - P1:no-tolerated-failure-in-authoritative-gate
  - P1:observable-not-envelope
  - P1:product-defect-to-known-issue
conflicts:
  - "The review workflow dispatches through the Codex CLI, absent on the web platform; the user directed a same-vendor Fable 5.1 subagent route (human-review-decision.md)."
  - "The Priority 0 RTK receipt contract assumes rtk, which the container lacks; container rows ran raw with immediate exit capture (D-11)."
  - "The plan's H2-1 decision sources collided on IDs (plan D-1..D-7 vs grouping §8 D-1..D-7; handoff D-20 vs issue D-20); resolved by A14, not by renumbering approved decisions."
  - "The execution-corrections workflow forbids plan/task edits, while task row H1-6 requires reopening row 11 and recording amendments; the plan's own row governed."
note: "Session 28 ships the MCP live audit: a TypeScript runner that drives the built server over stdio against an isolated backend, checks every one of 68 actions through REST or filesystem observables, proves 7 destructive refusals, cleans up and diffs a committed baseline. The authoritative Windows baseline (attempt 3, 65bfa42) has 96/97 steps passing; the one fail and 8 discovery findings are filed issues. Execution review approved in rounds 1–3; round 1's F1 caught an empty-transcript pass that attempt 1 had certified."
slim_candidate: ["Restating every plan decision in the handoff Decision Log: the plan is already a decision source, and the copies only created collision risk"]
overthinking_observed: false
review_churn:
  rounds_to_approval: {plan: 2, execution: 1}
  findings_per_round:
    - {review: plan, round: 1, critical: 0, high: 3, medium: 4, low: 2}
    - {review: plan, round: 2, critical: 0, high: 0, medium: 1, low: 4}
    - {review: execution, round: 1, critical: 0, high: 0, medium: 3, low: 2}
    - {review: execution, round: 2, critical: 0, high: 0, medium: 1, low: 0}
    - {review: execution, round: 3, critical: 0, high: 0, medium: 0, low: 1}
  churned_findings: 0
  finding_categories: {weak_test: 2, contract_drift: 2, claim_to_state_drift: 1, other: 4}
  verdicts: {changes_required: 1, approved: 4}
meu_work_classes: [correctness]
```
