---
date: "2026-09-28"
project: "p11-capture-settings"
meus: ["MEU-57", "MEU-58"]
plan_source: "docs/execution/plans/2026-09-28-p11-capture-settings/implementation-plan.md"
template_version: "2.0"
---

# 2026-09-28 Meta-Reflection — Phase 11 Capture and Settings pages (Phase 11 exit)

> **MEUs Completed**: MEU-57, MEU-58
> **Plan Source**: docs/execution/plans/2026-09-28-p11-capture-settings/implementation-plan.md

## Execution Trace

### Friction Log

1. **What took longer than expected?** The authoritative Windows gate. It took seven attempts to get one clean run. Session 26's product code caused none of the six failures:
   - Attempt 1: a framework-adoption test was pinned to the live sibling repo `P:/agentic-framework`, which had moved (A11, then A11-W).
   - Attempt 3: MEU-49 pointer drags raced layout (A12).
   - A12 repeat check: a keyboard drag was cancelled by the post-launch window resize (A13).
   - Attempt 4: `test_ac_12_7` released a held download before the second contender called `download()` (A14). The gate JSON also carried stale counts from the previous run (A15).
   - Attempt 5: the drop read dnd-kit's stale committed `over` (A16).
   - Attempt 6: the shared `P:/.agent` registry was edited for another project, so av-kit's overlay became stale (A17).

   Each round trip ran through Mat's local agent, which accounts for most of the wall-clock time.
2. **What instructions were ambiguous?**
   - The review route, as in Session 25. The workflow dispatches through the Codex CLI, which the web platform lacks. The user directed a Fable 5.1 subagent, recorded in `human-review-decision.md`.
   - Whether H1-6 remains `[x]` once a later code correction invalidates the gate. H1-7's rule ("re-run `WINDOWS_GATE` after any code correction") covered it, and the row prose was updated after review finding R2-3.
3. **What instructions were unnecessary?** Repeating the full gate evidence in both MEU handoffs, carried over from Session 25's slim candidate. This time the gate re-ran six times after the handoffs were written, and the handoffs were deliberately left pointing at the walkthrough.
4. **What was missing?**
   - A plan-time repeat-run requirement for timing-sensitive E2E specs. Single passes hid 1-in-5 and 1-in-100 races that surfaced only on the zero-tolerance Windows gate.
   - An environment-drift check before an authoritative gate: sibling repos and the machine-level registry at `P:/.agent` are inputs to `tests/tooling`.
   - A rule that gate scripts must never report a stage's counts unless that stage ran in the same run (A15).
   - AC-57.7's key-scope clause: the plan specified focus on open, but not that editor keys must stay inert while the strip holds focus. Execution review Round 1 found it.
5. **What did you do that wasn't in the prompt?**
   - Wrote the split container pre-gate plus Windows gate scripts and the `windows-gate-check` binder, reusing Session 25's pattern.
   - Proved each Windows-only race mechanism with a temporary container probe before proposing a fix: a same-task release reproduced the attempt 5 PUT body exactly, a 0.5 s late contender reproduced `0 == 1`, and a resize timeline probe showed the 1280×800 → 1280×773 shift.
   - Filed `TOOLING-SHARED-REGISTRY-COUPLING`.
   - Triaged five manual-test product issues reported by Mat. None traced to Session 26; filing them is left to the user.

### Quality Signal Log

6. **Which tests caught real bugs?**
   - The Round 1 reviewer's keyboard probe, turned into `AC-57.7 while the {dirty,delete} confirm strip owns focus, Delete and arrows leave the selected mark alone`. It was Red on `1663b0b` (a mark deleted behind the prompt) and Green after `1356c59`.
   - The AC-58.3 lock-reconcile and AC-58.6 accessible-name/segment tests, both Red on the pre-fix source.
   - The zero-tolerance Windows gate itself, which exposed four latent test races in older MEUs (MEU-49 ×3, MEU-12 ×1) that single container passes never showed.
7. **Which tests were trivially obvious?** The pure-table unit tests (`SETTINGS_SECTION_SET`, `SAVE_MODE_CAPTIONS`, hint and copy sources) and the source audits. They certify shape, not behaviour. The Round 1 reviewer also rated the original AC-58.6 an honest invariant test that passed on the pre-change page. The correction added a discriminating assertion.
8. **Did pyright/ruff catch anything meaningful?** Yes, once. Pyright flagged a real pre-existing typing error at `captures.py:78` (from MEU-60), fixed under the human-approved A8. Ruff found nothing. In the TypeScript pass, typecheck and ESLint stayed clean.

### Workflow Signal Log

9. **Was the FIC useful as written?** Yes. The single-statement contracts (`CAPTURE_OVERLAY_DIRTY`, `CONFIRM_EXCLUSIVITY`, `READINESS_COUNT`, `SETTINGS_SECTION_SET`, `COMPOSITION_LOCK`) gave the reviewer exact oracles. The one blocking finding cited AC-57.7 directly. `MIGRATION_CENSUS` found two unlisted contradictions (TM-11 and TM-12) before any code was written.
10. **Was the handoff template right-sized?** The AC tables and the "Referenced existing contracts" table, which was needed so the AC-coverage regex saw referenced ACs, supported review well. The duplicated gate record is still the compression opportunity.
11. **How many tool calls did this session take?** Not reliably instrumented across several context compactions and a container restart. No estimate is given. Commands and outcomes are retained in the walkthrough and receipts.
12. **Which rows were delegated, to which subagent (harness + model), and did any delegated result need rework?**
    - No `av-kit-builder` or `av-kit-verifier` delegation.
    - Independent review ran in fresh Claude Code `Agent` subagents with `model: fable` at high effort: plan review in 2 rounds, execution review in 2.
    - A read-only Explore subagent triaged Mat's manual-test issues. Its key claims were spot-checked and held.
    - `WINDOWS_GATE` and the A11/A17 edits were human-run steps on Mat's machine, executed by his local agent. None needed rework.

### Decisions Log

| ID | Stage | Question | Resolution | Chosen | Source tag | Reasoning (why this; why the alternatives lost) | Human ref |
|----|-------|----------|------------|--------|------------|--------------------------------------------------|-----------|
| D-1 | planning | Which independent reviewer replaces the Codex CLI route on the web platform? | human | Fable 5.1 Agent subagent at high effort | Human-approved | The Codex CLI is absent in the web container; a separate-context subagent keeps independence, and the same-vendor exception is recorded in human-review-decision.md | USER_EXPLICIT 2026-09-28: use subagent to fable 5.1 high model |
| D-2 | execution | Where does the authoritative Phase 11 exit gate run? | human | Split: container pre-gate plus WINDOWS_GATE on Mat's host | Human-approved | RTK, the Windows region-picker stub and Windows-bound tests exist only there; Session 25 precedent; a container-only gate would have to tolerate failures | USER_EXPLICIT 2026-09-29: Split like Session 25 (Recommended) |
| D-3 | execution | Accept the OQ-1 to OQ-5 recommendations and execute after Session 25? | human | Accept all five | Human-approved | Session 25 was approved so SEQUENCING_GATE passed; each OQ had a recommended option grounded in the Phase 11 canon | USER_EXPLICIT 2026-09-29: I'm good with your recommendations |
| D-4 | execution | Approve the two census-found test migrations TM-11 and TM-12? | human | Approve TM-11 + TM-12 | Human-approved | CP1 and CP5 made two capture assertions unreachable; setup-only migrations keep every assertion instead of weakening MEU-39/59 contracts | USER_EXPLICIT 2026-09-29: Approve TM-11 + TM-12 (Recommended) |
| D-5 | execution | Fix the pre-existing pyright error at captures.py:78 in this session? | human | Fix it here (A8) | Human-approved | The zero-tolerance py-types stage would stay red otherwise; typing-only model_validate keeps payload and OpenAPI identical | USER_EXPLICIT 2026-09-29: Fix it here (Recommended) |
| D-6 | execution | How should test_framework_adoption handle a sibling repo that moved (attempt 1)? | human | Self-contained fixture git repo (A11) | Human-approved | Pinning or resetting P:/agentic-framework mutates another repo and rots again; a fixture keeps assertions and removes the machine coupling | USER_EXPLICIT 2026-09-29: Give me message for local agent for B |
| D-7 | execution | Widen A11 to the migrated_tree fixture when source_state also hashes source_path files? | human | Widen A11 (A11-W) | Human-approved | The narrow change left 4 failures; seeding the fixture repo per source_path keeps assertions and lets refusal cases reach their real rule | USER_EXPLICIT 2026-09-29 via Mat's local-agent chat: go with your recommendation |
| D-8 | execution | How to handle the AC-49.26 Windows drag race (attempt 3)? | human | Harden grabRow/dragOver helpers (A12) | Human-approved | Rerunning would leave a ~20% race in the suite; helper-only settle waits change no assertion | USER_EXPLICIT 2026-09-29: Harden helpers (Recommended) |
| D-9 | execution | How to handle the AC-49.27 keyboard drag cancelled by the post-launch resize? | human | windowSettled wait (A13) | Human-approved | A probe proved the launch resize; accepting a 1% flake would keep the zero-tolerance gate unreliable | USER_EXPLICIT 2026-09-29: Add window-settle wait (Recommended) |
| D-10 | execution | How to handle the test_ac_12_7 contention race (attempt 4)? | human | Join contenders before release (A14) | Human-approved | A delayed-contender probe reproduced 0 == 1; the service lock is correct, so only the test ordering changes | USER_EXPLICIT 2026-09-29: Reorder test (Recommended) |
| D-11 | execution | How to handle AC-49.25 dropping one row short (attempt 5)? | human | Wait for the committed over announcement (A16) | Human-approved | A same-task release probe reproduced the exact PUT body; waiting for dnd-kit's committed state is deterministic, geometry alone is not | USER_EXPLICIT 2026-09-29: Wait for committed over (Recommended) |
| D-12 | execution | How to handle the stale registry overlay after the shared P:/.agent change (attempt 6)? | human | Revalidate only validated_against (A17) | Human-approved | The resolver's freshness guard worked as designed; reverting P:/.agent would undo another project's work and a fixture rewrite is larger | USER_EXPLICIT 2026-09-30: Revalidate overlay (Recommended) |
| D-13 | execution | Which baseline should the container doc-test leg compare against after A11? | autonomous | 7613beb, the Windows-verified A11 commit (A10-R) | Local Canon | The old 1f9b035 baseline passed two path-escape tests for the wrong reason; WINDOWS_GATE stays authoritative with zero tolerance | — |
| D-14 | execution | Should the Windows gate script ever report counts for a stage that did not run? | autonomous | No; clear receipts first and read only ran stages (A15) | Local Canon | Attempt 4 reported attempt 3's stale counts; recorded evidence must describe the run it came from | — |
| D-15 | execution | Keep Save overlay, Open and Delete inside the editor key scope after the confirm-strip fix? | autonomous | Keep them; exclude only the confirm strip | Local Canon | The existing toolbar buttons share that scope and the mockup places the actions there; only the strip is modal-like under AC-57.7; Round 2 accepted it | — |
| D-16 | closeout | How does POST_REVIEW_STATE handle an empty MEU queue? | autonomous | Accept next = none only with stats Pending 0 and explicit No pending MEU text (A18) | Local Canon | All 61 MEUs are complete; inventing a next MEU would be false, and the check stays fail-closed with adversarial self-tests | — |
| D-17 | closeout | How to land the branch on main when main has moved on? | autonomous | Merge main into the branch, then fast-forward main | Local Canon | A rebase would rewrite 32 commits including Mat's gate results and break every cited SHA; a merge keeps the evidence chain and still lets main fast-forward | USER_EXPLICIT 2026-09-30: fast-forward changes to main |

---

## Pattern Extraction

### Patterns to KEEP

1. Split gate plus a commit-bound `windows-gate-check`, carried from Session 25. It correctly refused every stale or partial result: attempts 1, 3, 4, 5 and 6, and the result that went stale after `1356c59`.
2. Reproduce a Windows-only race mechanism in the container, with a targeted probe (same-task release, delayed contender, event timeline), before asking for approval of a test change. Every approved amendment carried proof, not "flake".
3. Ask for approval for each test change with verbatim option text, and quote it in `human-gate-decision.md` (A11, A11-W, A12, A13, A14, A16, A17).

### Patterns to DROP

1. Running the authoritative gate straight after a code or test change without a targeted repeat run. The repeat checks added from A12 onward (100×, then the full suite ×2) caught races before the gate instead of in it.
2. Letting a test read live machine-level state (sibling repos, `P:/.agent`) inside the zero-tolerance gate without a drift preflight.

### Patterns to ADD

1. Before an authoritative gate, run a preflight that records the sibling repo HEADs and the registry hash, and compares them with the values the tests pin.
2. For drag-and-drop E2E specs, wait for the library's committed state (announcement or `aria-pressed`) rather than geometry alone. Plan a `--repeat-each` gate for any spec that drives pointer or keyboard sensors.
3. Gate scripts delete their per-stage receipts at the start and report counts only for stages that ran.

### Calibration Adjustment

- Estimated time: not recorded; no retrospective number is invented.
- Actual scope: two MEUs and one approved API typing fix. 44 Vitest and 7 Electron cases were added (631 → 675, 103 → 110). The work took 2 plan and 2 execution review rounds, 7 Windows gate attempts, and 8 human-approved amendments to tests and tooling outside the MEUs (A11, A11-W, A12–A14, A16, A17 plus A15).
- Adjusted estimate for similar sessions: when the authoritative gate runs on a remote human-operated host, budget several gate round trips. Front-load the repeat and preflight checks above.

## Next Session Design Rules

```text
RULE-1: A drag test releases only after the drag library has committed the target, never on geometry alone.
SOURCE: WINDOWS_GATE attempt 5, AC-49.25 dropped one row short on dnd-kit's stale committed `over` (A16).
EXAMPLE: dragOver ends by waiting for the live region "moved to position N of M" before mouse.up.
```

```text
RULE-2: Preflight external inputs before an authoritative gate: sibling repo HEADs, registry hashes, window/display state.
SOURCE: attempts 1 and 6 failed on P:/agentic-framework and P:/.agent drift unrelated to the session's code.
EXAMPLE: record `git -C P:/agentic-framework rev-parse HEAD` and sha256(P:/.agent/model-registry.json), compare with pinned values, stop if different.
```

```text
RULE-3: A modal-like strip that takes focus must also be excluded from every global key handler's scope, and the Red pass must test keys, not just clicks.
SOURCE: execution Round 1 Finding 1 (Delete/arrows edited marks behind the AC-57.7 confirm strip).
EXAMPLE: annotationOwnsFocus() returns false inside [data-testid="capture-confirm-strip"]; a test dispatches Delete and ArrowRight with focus on Cancel.
```

## Next Day Outline

1. Phase 11 is complete. The next MEU comes from `uv run python tools/meu_status.py next` (see the hub Next line).
2. Triage Mat's five manual-test issues (TTS no audio: spaCy `en_core_web_sm` missing and ONNX vocab unwired; hidden `error_message`; ffmpeg resolution divergence; TTS voice-select layout jump; model-flow gaps). Confirm with the user before filing them as known issues or MEUs.
3. Consider `TOOLING-SHARED-REGISTRY-COUPLING`: give `test_framework_adoption.py` a fixture registry home.
4. Carry forward the three design rules above into any plan that touches drag and drop, focus-taking strips, or the Windows gate.
5. Non-blocking review residuals: rail-lock bottom-rule timing under xvfb (R2-2, pre-existing); focus lands on `body` after strip Cancel/Confirm (Round 1 observation 1).
6. Pre-existing Settings readiness behaviour, kept by ST7 and recorded here for triage: before dependencies load, readiness rows can show "no" labels and the FFmpeg Fix link. Only the count, dot and chip were gated.

## Efficiency Metrics

| Metric | Value |
|--------|-------|
| Total tool calls | Not reliably instrumented across the continued session |
| Time to first green test | Not measured; Red and Green receipts are retained |
| Tests added | 44 Vitest and 7 Electron; final Windows gate 675 / 110 at `cb864f3` |
| Codex findings | Plan: R1 3 High + 3 Medium + 1 Low, R2 1 Medium + 5 Low (approved). Execution: R1 1 Medium (blocking) + 3 Low, R2 3 Low (approved). Reviewer: Fable 5.1 subagent, not Codex |
| Handoff Score (X/7) | 7/7 sections populated in each MEU handoff |
| Rule Adherence (%) | 5/6 sampled rules below; no exhaustive percentage claimed |
| Prompt→commit time | Not measured |

### Rules Sampled for Adherence Check

| Rule | Source | Followed? |
|------|--------|-----------|
| Write tests before production corrections and keep frozen assertions | Testing & TDD Protocol | Yes. The 4 Round 1 regression tests were Red on `1663b0b`, and A12–A16 touched no assertion (reviewer grep confirmed) |
| Independent reviewer authors approval | Execution Contract | Yes; both verdicts were written by fresh Fable subagents |
| A human approves every test-expectation or out-of-scope test change | Human Approval Gate | Yes; A11, A11-W, A12, A13, A14, A16 and A17 quote the user in `human-gate-decision.md` |
| Never label a failing test a flake without a root cause | Execution Contract | Yes; every Windows failure got a proven mechanism before a change |
| RTK redirect with all-stream receipts | Priority 0 | Partly; `rtk` is absent in the container, so plain redirects into `$RECEIPTS_DIR` with immediate exit capture were used. Mat's host used RTK |
| Continue through H2 after approval without an intermediate stop | Execution Contract | Yes |

## Instruction Coverage

```yaml
schema: v1
session:
  id: "session-26-p11-capture-settings-2026-09-28"
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
  workflows: [create_plan, execution_critical_review, execution_corrections]
  roles: [orchestrator, coder, tester]
  skills: []
  refs:
    - .agent/docs/harness-profiles.md
    - .agent/context/harness.local.md
    - .agent/schemas/reflection.v1.yaml
    - docs/build-plan/11-page-layout.md
    - docs/execution/plans/2026-09-28-p11-capture-settings/implementation-plan.md
    - docs/execution/plans/2026-09-28-p11-capture-settings/task.md
    - docs/execution/plans/2026-09-28-p11-capture-settings/human-review-decision.md
    - docs/execution/plans/2026-09-28-p11-capture-settings/human-gate-decision.md
decisive_rules:
  - P1:tests-before-production-corrections
  - P1:independent-review-no-self-approval
  - P1:human-approval-for-test-changes
  - P1:no-tolerated-failure-in-authoritative-gate
  - P1:flake-is-not-a-root-cause
conflicts:
  - "The review workflow dispatches through the Codex CLI, which is absent on the web platform; the user directed a same-vendor Fable 5.1 subagent route, recorded in human-review-decision.md."
  - "The zero-tolerance gate depends on machine-level state (P:/agentic-framework, P:/.agent) outside the session's scope; each drift needed its own human-approved amendment (A11, A17)."
  - "The Priority 0 RTK receipt contract assumes rtk, which the container lacks; receipts used plain redirects with immediate exit capture."
note: "Session 26 closes Phase 11: execution Round 2 approved after one AC-57.7 key-scope correction; authoritative Windows gate attempt 7 passed 675 Vitest / 110 Electron at cb864f3 after six environment or legacy-test-race failures, each root-caused and fixed under explicit approval."
slim_candidate: ["Repeated project-wide full-gate evidence in every MEU handoff; one canonical record in the walkthrough plus references would do"]
overthinking_observed: false
review_churn:
  rounds_to_approval: {plan: 2, execution: 2}
  findings_per_round:
    - {review: plan, round: 1, critical: 0, high: 3, medium: 3, low: 1}
    - {review: plan, round: 2, critical: 0, high: 0, medium: 1, low: 5}
    - {review: execution, round: 1, critical: 0, high: 0, medium: 1, low: 3}
    - {review: execution, round: 2, critical: 0, high: 0, medium: 0, low: 3}
  churned_findings: 0
  finding_categories: {contract_drift: 4, weak_test: 3, claim_to_state_drift: 1, back_compat_break: 1, provenance_error: 1, other: 2}
  verdicts: {changes_required: 2, approved: 2}
meu_work_classes: [mixed, mixed]
```
