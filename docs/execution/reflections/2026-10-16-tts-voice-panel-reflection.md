---
date: "2026-10-17"
project: "2026-10-16-tts-voice-panel"
meus: ["MEU-75", "MEU-79"]
plan_source: "docs/execution/plans/2026-10-16-tts-voice-panel/implementation-plan.md"
template_version: "2.0"
---

# 2026-10-17 Meta-Reflection

> **Date**: 2026-10-17
> **MEU(s) Completed**: MEU-75 (tts-model-flow-gaps), MEU-79 (tts-voice-panel-layout)
> **Plan Source**: docs/execution/plans/2026-10-16-tts-voice-panel/implementation-plan.md

---

## Execution Trace

### Friction Log

1. **What took longer than expected?**
   The authoritative gate. It ran seven times: once at row 6, once at H1-2 after the row 7 hub edits, three times after the execution review R1 F1 correction, and twice after the R2 F2 correction. Post-correction attempt 1 failed only at `ui-electron`, on the known transcript-queue W2-5 timeout (`DOWNLOAD-QUEUE-DRAG-OVER-MISS`, A-2). Attempt 2 failed only at `ui-tests`, on a clock-second race in `capture-picker.test.ts` AC-40.6 that no Session 35 file touches (A-3). The first post-F2 run failed only at `ui-electron`, on a capture-inbox AC-66.14 pan-origin miss that passed 5/5 alone (A-4). Each full run takes about 25 minutes, most of it the 161-test Electron suite and the `--repeat-each=10` wave. The plan review also needed three rounds, and Mat added 20M tokens to finish it; the execution loop needed another 20M after round 2.

2. **What instructions were ambiguous?**
   `DEVICE_PROBE` said the device list comes from the runtime, but not what a runtime query that raises means. The plan's tests only covered queries that answer False. The execution review found the gap (R1 F1): a raising ONNX provider enumeration or `torch.cuda.is_available` escaped as a bare `RuntimeError`, so the catalog and a CPU load answered HTTP 500. Round 2 found a second instance (R2 F2): the lazy `from kokoro import KModel` caught only `ImportError`, so an engine that failed to initialize escaped the same way. The plan's §1 baseline rule also covered "a test failing at baseline" in general, but `session-gate.ps1` implemented it for pytest only, which A-1 (D-19) had to close at row 6.

3. **What instructions were unnecessary?**
   Each handoff restates the shared gate record and its counts, which `walkthrough.md` already holds. The F1 correction meant regenerating both handoffs for one adapter change, and the MEU-79 handoff changed only because the shared gate record moved.

4. **What was missing?**
   The plan named each runtime query but had no row for a query that throws. A FIC line per external call ("what if this raises") would have caught F1 at planning, and listing imports as external calls would have caught F2. The plan also said nothing about a gate failure in a test outside the session's files, so A-2 (re-run once) and A-3 (Mat: fix the race now) were decided during execution. The recheck prompts never asked for REVIEW-TEMPLATE's Prior Pass Summary table, which H1-7b needs to close a carried finding, so round 4 existed only to add it (A-5). Two MEU-40 tests built an inbox name from the real clock and asserted a collision against a second clock read; neither was a known issue.

5. **What did you do that wasn't in the prompt?**
   Ran W2-5 alone (4 passed) before re-running the whole gate after attempt 1, and recorded a "seen again" note on `DOWNLOAD-QUEUE-DRAG-OVER-MISS`. Swept `load_model` for other statements outside a guard during the F1 correction; the vocab resolver and the weight-file `stat` got the same `ModelLoadError` wrapping. That sweep read calls, not imports, and missed the lazy engine import that became R2 F2. Kept the round 1 gate receipts and each failed attempt's receipts in their own folders, so the reviewer can compare them. Swept `ui/tests` for other names built from the real clock under A-3 and fixed the sibling `capture-lifecycle.test.ts` AC-40.30 (a). Under A-4, ran AC-66.14 alone (5 passed) and logged `CAPTURE-ZOOM-PAN-ORIGIN-FLAKE` before the re-run.

### Quality Signal Log

6. **Which tests caught real bugs?**
   The five F1 regressions in `tests/integration/test_tts_device_resolution.py` (:563, :588, :616, :657, :681) all failed Red on the reviewed tree: a raising provider enumeration, a CPU load after that failure, a raising probe or vocab, an unreadable weight file, and the HTTP catalog and load path (`assert 500 == 200`). The F2 regression (`:730`) failed Red with `OSError: engine dependency DLL initialization failed` and covers an `OSError` and a `RuntimeError` import plus the HTTP 422. The A-3 Red probe (a forced one-second clock step) reproduced the gate's exact AC-40.6 message, so the pin is known to close the race rather than hide it. The AC-79.9 Electron geometry test failed Red on the old layout with the real widths, which is what the plan's width estimate (D-14) needed confirmed.

7. **Which tests were trivially obvious?**
   AC-79.5's default-markup pin restates the unchanged `SegmentedControl` default. It guards against a regression on the other pages, not a defect.

8. **Did pyright/ruff catch anything meaningful?**
   pyright caught one lambda-narrowing issue in a test fake (no product defect); ruff was clean throughout.

### Workflow Signal Log

9. **Was the FIC useful as written?**
   Yes for MEU-79: `VOICE_GRID`, `SEGMENT_SIZE` and `VOICE_GEOMETRY` mapped one-to-one to tests, and the measured widths held. For MEU-75 the named contracts were right but incomplete on the failure side (see Friction 2).

10. **Was the handoff template right-sized?**
    Mostly. The AC tables with cross-reference rows for the families each handoff does not own satisfied `--ac-coverage-only` without duplicate tests. The shared gate record is duplicated (Friction 3).

11. **How many tool calls did this session take?**
    Not tracked precisely; several hundred across planning, execution and closeout, with two context compactions.

12. **Which rows were delegated, to which subagent (harness + model), and did any delegated result need rework?**
    None. Every row was correctness-class or gate work, held by the coordinator (Claude Code, Opus 5.5). The plan and execution reviews went to Codex at high effort through `tools/Invoke-CodexDispatch.ps1`; that is review, not delegation.

### Decisions Log

| ID | Stage | Question | Resolution | Chosen | Source tag | Reasoning (why this; why the alternatives lost) | Human ref |
|----|-------|----------|------------|--------|------------|--------------------------------------------------|-----------|
| D-1 | grouping | When are the gated build-plan edits (matrix rows, MEU-79's 11 section, 06/gui-actions-index) written? | autonomous | After Session 30's execution review approves; the grouping writes only ungated homes and the SSOT | Local Canon | Carried from grouping §8 D-1. Its condition is now met, so row 1 wrote the 11 §TTS voice panel section and row 7 the matrix rows (plan D-18). | — |
| D-2 | grouping | Does MCP-SETUP-PROMPT join Session 31? | human | Yes, as MEU-71; Session 31 becomes P3 | Human-approved | Carried from grouping §8 D-2. No effect on Session 35's scope. | USER_EXPLICIT 2026-10-09 'All recommendations accpeted as proposed' |
| D-3 | grouping | Are the tech-debt rows MEUs? | autonomous | No; a separate debt batch | Local Canon | Carried from grouping §8 D-3. Session 35 took none of the debt rows; `DOWNLOAD-QUEUE-DRAG-OVER-MISS` stays a known issue (A-2). | — |
| D-4 | grouping | Session order | autonomous | 31 → P2 sessions 32, 33, 34 → P3 35, 36 → P4 37, 38, 39 | Local Canon | Carried from grouping §8 D-4. Session 35 ran after Sessions 33, 36 and 39 merged; its base is main 6097cf5. | — |
| D-5 | grouping | Keep TTS page work (MEU-75, MEU-79) out of the engine session? | autonomous | Yes, Session 35 after Session 33 | Local Canon | Carried from grouping §8 D-5. Session 33's MEU-77 changes to `TTSPage.tsx` and `useTtsJob.ts` were on the base, so the page work landed once. | — |
| D-6 | grouping | Where does the independent MEU scoping review run? | human | Codex scoping review on the grouping draft, not during triage | Human-approved | Carried from grouping §8 D-6. This plan's own independent review covered the two MEUs' scope. | USER_EXPLICIT 2026-10-09 'All recommendations accpeted as proposed' |
| D-7 | grouping | Repair the shared status_labels in meu-status.yaml? | autonomous | Yes: every row's labels rebuilt from its own status | Local Canon | Carried from grouping §8 D-7. H2-2 renders and checks the registry after the MEU-75 and MEU-79 status change. | — |
| D-55 | grouping | Where does MEU-71 run, now that Session 31 executed without it? | human | Its own Session 31b (MEU-71 alone), next | Human-approved | Carried from grouping §8 D-55. No effect on Session 35's scope. | USER_EXPLICIT 2026-10-16 'accept all' |
| D-56 | grouping | Who makes the packaged mcp-server dependencies present and proves MCP_ENTRY_PROBE starts? | autonomous | Left open for its owner: Session 35 does not decide it | Local Canon | Carried from grouping §8 D-56, which is still `open` there (recommended: a new MEU in Session 31b). Session 35 changes no MCP packaging, so its only decision is not to take this up; the reflection table has no `open` resolution. | — |
| D-66 | triage | What happens when the requested device is not available to the runtime? | autonomous | The PyTorch path falls back to CPU like the ONNX path, logs the downgrade and reports the real device | Local Canon | Triage decision in `TTS-MODEL-FLOW-GAPS` enrichment, consumed through the grouping and implemented as plan D-10 (`DEVICE_RESOLVE`, `LOAD_FALLBACK`). Not re-decided here. | — |
| D-68 | triage | How should the Voice panel controls be laid out? | autonomous | One aligned grid row for Model (flexes), Device (fixed) and the model action, sharing one control height | Local Canon | Triage decision in `TTS-MODEL-ROW-LAYOUT` enrichment, consumed through the grouping and implemented as plan D-14 (`VOICE_GRID`) and D-16 (`VOICE_GEOMETRY`). Not re-decided here. | — |
| D-8 | planning | Where is the plan written and executed? | autonomous | Worktree P:/av-kit-wt/s35-tts-voice-panel on branch claude/s35-tts-voice-panel | Local Canon | Isolates this session from the other open branches; D6 argv unchanged. Precedent: Session 36 and 39 D-8. The base later moved to 6097cf5 when Sessions 36 and 39 merged. | — |
| D-9 | planning | How does the runtime report which devices exist? | autonomous | DEVICE_PROBE: runtime_devices(format) in the adapter, torch flags for PyTorch, ONNX providers for ONNX; injectable | Research-backed | Each runtime's own query is the only reliable answer, and the two formats differ. Research: native reading of the installed torch 2.13.0+cpu and onnxruntime providers. Execution R1 F1 later added the raising-query case (D-21). | — |
| D-10 | planning | What happens when the requested device cannot be used? | autonomous | DEVICE_RESOLVE (unavailable → CPU, logged) and LOAD_FALLBACK (one CPU retry, logged); ModelLoadError with the cause | Spec | 03:465-467 (triage D-66). Probing first avoids a guaranteed `KModel.to('cuda')` failure on a CPU torch; the retry covers a detected but unusable GPU. | — |
| D-11 | planning | Which HTTP status does a failed model load return? | autonomous | LOAD_ERROR_HTTP: ModelLoadError → 422 with code and message | Local Canon | Same mapping as Session 33's ExtractError (MEU-76); a 500 masks the reason the user never saw. One-way (published API contract), listed under User Review Required. | — |
| D-12 | planning | How does the page learn which devices a model row can use? | autonomous | DEVICE_FIELD: a required devices field on ModelVariantOut | Spec | 03:466. The list depends on the row's format, so it belongs on the row; a separate endpoint adds a fetch and a loading state. | — |
| D-13 | planning | What does the Device select show when the stored device is not in the row's list? | autonomous | DEVICE_SELECT_VALUE: show and send auto; keep the stored setting | Research-backed | Auto is offered by every row; writing it back would turn a model switch into a hidden settings change (MEU-56 touched-set precedent). | — |
| D-14 | planning | How are the Voice panel controls laid out? | autonomous | VOICE_GRID: model row [1fr, 7rem, auto]; speed row [1fr, auto] with md presets; Format on its own row; all 36 px | Spec | Triage D-68. The width estimate showed Format in the speed row would push the slider under its 96 px floor; AC-79.9 measured the real widths and passed. | — |
| D-15 | planning | How do the Speed presets reach 36 px without changing other pages? | autonomous | SEGMENT_SIZE: an opt-in size='md' prop; default markup byte-identical | Local Canon | Changing the default would move every other page's segmented controls; follows the Button size convention. AC-79.5 pins the default markup. | — |
| D-16 | planning | How is the alignment proven? | autonomous | VOICE_GEOMETRY: Electron bounding boxes at the default window, ±0.5 px, no overflow, 96 px slider floor | Local Canon | jsdom has no layout; AC-64.6 is the precedent geometry test. | — |
| D-17 | planning | How do the Electron tests get device lists? | autonomous | E2E_DEVICE_SEAM: the existing tts-generate seam's catalog rows gain devices | Local Canon | The seam is the page's only backend in Electron; the smallest change. | — |
| D-18 | planning | When is the 11 §TTS voice panel alignment section written? | autonomous | Task row 1, before any test | Local Canon | Grouping D-1's condition is met; the spec stays ahead of the tests. | — |
| D-19 | execution | The gate fails fast at ui-tests on queue-canon AC-41.3, a baseline failure from an external Zorivest commit. How does row 6 apply the plan's baseline rule? | autonomous | Amendment A-1: session-gate.ps1 applies the plan §1 baseline rule to ui-tests as it did for py-tests | Local Canon | MEU-75 handoff Decision Log and walkthrough §Gate. The plan's rule already said baseline failures are not regressions; the script only implemented it for pytest. Narrow (one id, checked against row 0's receipt), disclosed and reversible; Session 37 A-4 is the precedent. | — |
| D-20 | execution | Playwright replaces the `Error: expect(` header when a custom message is given, so red-check cannot attribute the Electron Red. How do the AC-79 tests name the failing pair? | autonomous | No custom messages; expectNear compares an object holding the pair name and delta | Local Canon | MEU-79 handoff Decision Log. Changing red-check would weaken a reviewed gate; the bounds are unchanged. | — |
| D-21 | execution | Execution review R1 F1: a raising runtime availability query escaped as a bare RuntimeError (HTTP 500). What does a failing query do? | autonomous | The device counts as absent and `tts.device_probe_failed` is logged; load_model wraps the probe, vocab and weight-file stat in ModelLoadError | Local Canon | MEU-75 handoff Decision Log and plan §Execution Correction Notes. A device whose availability cannot be read cannot be used, which is the unavailable case DEVICE_RESOLVE already handles; failing the catalog would block a CPU load that works. 03:469 requires ModelLoadError, never a bare exception. | — |
| A-2 | execution | Post-correction gate attempt 1 failed only at ui-electron on the transcript-queue W2-5 timeout | autonomous | Re-run the whole gate with no file change; a second miss stops for Mat | Local Canon | walkthrough §A-2. A known issue (`DOWNLOAD-QUEUE-DRAG-OVER-MISS`) in a file this session never touches; W2-5 passed 4/4 alone. Same obviousness class as Session 33 A-13. | — |
| A-3 | execution | Post-correction gate attempt 2 failed only at ui-tests on a clock-second race in capture-picker AC-40.6 (second miss) | human | Fix the test race now: the two affected MEU-40 tests pin Date; scope-paths allows them; re-run the gate | Human-approved | walkthrough §A-3. Recommended was a re-run plus a new known issue; Mat chose the fix. Red forced the boundary and reproduced the gate message; no assertion changed. Attempt 3 is the gate of record. | USER_EXPLICIT 2026-10-17 'Fix the test race now' |
| D-22 | closeout | The reflection check refused the D-66 and D-68 enrichment entries in known-issues.yaml (a wrapped plain scalar, list items at their key's indent), which predate this session | autonomous | Join the wrapped scalars and indent the list items; the parsed YAML is identical | Local Canon | The closeout validator reads a bounded YAML subset (HDP-19) that refuses both shapes, so H2-2 could not reconcile the triage decisions. The repair changes form, not values (checked by comparing the parsed file before and after), in an identity-excluded file. Same class as Session 33 D-43. | — |
| D-23 | execution | Execution review R2 F2: a non-ImportError raised by the lazy kokoro.KModel import escaped load_model (HTTP 500). How is engine initialization classified? | autonomous | ImportError stays "PyTorch runtime is not bundled"; any other exception logs tts.load_failed and raises ModelLoadError("PyTorch model failed to load") from the cause | Local Canon | MEU-75 handoff Decision Log and plan §Execution Correction Notes. An installed engine that fails to start is a failed load, the same message and log as a failing constructor; 03:469 requires ModelLoadError, never a bare exception. | — |
| A-4 | execution | Post-F2 gate run 1 failed only at ui-electron on capture-inbox AC-66.14 (pan origin 92 px off) | autonomous | Log CAPTURE-ZOOM-PAN-ORIGIN-FLAKE and re-run the whole gate with no file change; a second miss stops for Mat | Local Canon | walkthrough §A-4. An earlier session's test that no Session 35 change reaches; 5/5 alone; the re-run passed (Electron 161). Cause unproven, so the test was not edited. | — |
| D-24 | execution | The ledger refused execution round 3 on its token budget (18.4M spent plus a 9.8M reserve against 21M) | human | Add 20M and pre-approve rounds up to the cap of 6 | Human-approved | Recorded with review_ledger.py continue (s35-ledger-continue.txt: 18,411,384/41,000,000, rounds 2/6). | USER_EXPLICIT 2026-10-17 'Add 20M, upt to 6 rounds pre-approved' |
| A-5 | closeout | H1-7b refused the round 3 approval: no recheck section had a Recheck Result table, so F1 and F2 stayed carried as open | autonomous | A narrow round 4 asked Codex to confirm the unchanged tree and add the Prior Pass Summary table; the implementer did not edit the reviewer's text | Local Canon | walkthrough §A-5. Closing a finding is the reviewer's act; rounds up to 6 were pre-approved. Round 4 approved (2.3M tokens) and H1-7b passed at round 4 of 6. | — |

Every grouping §8 row is carried above (D-56 is still open in the grouping). Triage D-66 and D-68 are cited from the two resolved issues' enrichment; they were consumed through the grouping, not re-decided here. The reflection check reads one `--decision-issue`: given two, it reconciles the last (D-68), so D-66 is checked only by this table.

---

## Pattern Extraction

### Patterns to KEEP
1. Red before every correction, including the review-driven ones: all five F1 regressions and the F2 regression failed on the reviewed tree before `adapter.py` changed.
2. Preserve a failed gate's receipts in their own folder, classify the failure and record an A-row before re-running (A-2, A-3, A-4).
3. Measure layout in Electron, not jsdom: the D-14 width estimate was checked against real bounding boxes (AC-79.9).

### Patterns to DROP
1. Restating the shared gate record in every handoff; one record in the walkthrough and a pointer would do.

### Patterns to ADD
1. A FIC line for every external call the contract depends on, stating what happens when it raises.
2. A plan-level rule for a gate failure in a test outside the session's files: re-run once, and a second miss goes to a human.
3. A lint or review check for tests that read the real clock twice and assert both reads agree.
4. A correction's sibling sweep lists imports as well as calls: a lazy import is a load-time operation.
5. Every recheck dispatch prompt asks for the Prior Pass Summary table, with `| Finding | Prior Status | Recheck Result |` and a plain `fixed` or `open` cell.

### Calibration Adjustment
- Estimated time: one planning day and one execution day.
- Actual time: planning 2026-10-16 (three review rounds, plus 20M added tokens); execution and closeout 2026-10-16 to 2026-10-17, four execution review rounds (approved at round 3, re-confirmed at round 4 for the recheck table, A-5), plus 20M added tokens.
- Adjusted estimate for similar MEUs: budget two review corrections and three full gate runs for any MEU that adds a runtime probe.

---

## Next Session Design Rules

```
RULE-1: Every contract that reads an external runtime or OS state says what happens when the read raises, not only when it answers no.
SOURCE: execution review R1 F1 (a raising ONNX provider enumeration escaped as HTTP 500) and R2 F2 (a failing lazy engine import escaped the same way).
EXAMPLE: "devices come from the runtime" → "devices come from the runtime; a query that raises makes that device absent, logged".
```

```
RULE-2: The plan says how a gate failure in a test outside the session's files is handled before execution starts.
SOURCE: A-2 (W2-5 timeout), A-3 (capture-picker clock race) and A-4 (capture-inbox pan origin), three unrelated misses in the post-correction gates.
EXAMPLE: no rule → "one whole-gate re-run with no file change; a second miss stops for the human".
```

```
RULE-3: When the plan's baseline rule names every suite, the gate script implements it for every suite.
SOURCE: A-1 / D-19 (ui-tests had no baseline rule; py-tests did).
EXAMPLE: py-tests baseline rule only → the same rule for py-tests and ui-tests, checked in the plan review.
```

---

## Next Day Outline

1. Target MEU(s): Session 36's successors per the 2026-10-09 grouping D-4 order (next open P3/P4 session in current-focus).
2. Scaffold changes needed: none required; consider a plan-template line for known-issue gate failures (RULE-2).
3. Patterns to bake in from today: RULE-1 to RULE-3; `DOWNLOAD-QUEUE-DRAG-OVER-MISS` is still open and needs its own fix.
4. Codex validation scope: plan review at high effort, cap 6, as here.
5. Time estimate: one planning day and one execution day.
6. Merge: Mat merges `claude/s35-tts-voice-panel`; it is based on main 6097cf5.

---

## Efficiency Metrics

| Metric | Value |
|--------|-------|
| Total tool calls | not tracked precisely (several hundred) |
| Time to first green test | MEU-75 Green on 2026-10-16, right after its Red receipts |
| Tests added | pytest: 24 in the new `test_tts_device_resolution.py` (18 planned, 5 for F1, 1 for F2) and 7 in existing files; ui Vitest +6; Electron +4 (suite 161); two MEU-40 tests clock-pinned under A-3, no assertion changed |
| Codex findings | Plan review: R1 changes_required (1 High, 2 Medium), R2 changes_required (1 procedural), R3 approved. Execution review: R1 changes_required (1 High: raising runtime query), R2 changes_required (1 High: lazy engine import), R3 approved (0), R4 approved (0; recheck table only, A-5) |
| Handoff Score (X/7) | 6/7 (the MEU-75 handoff claimed AC-75.9 before the raising-query and engine-import cases were covered) |
| Rule Adherence (%) | 92 |
| Prompt→commit time | 2026-10-16 → not committed (Mat commits) |

### Rules Sampled for Adherence Check

| Rule | Source | Followed? |
|------|--------|-----------|
| Tests before production code; Red before Green | AGENTS.md §Testing & TDD | Yes, including the R1 F1 correction |
| No test expectation change without approval | AGENTS.md §Testing & TDD | Yes; no existing assertion changed outside the plan |
| Independent review; no self-approval | AGENTS.md §Dual-Agent Workflow | Yes. Codex wrote every verdict; the implementer's section is `corrections_applied` |
| A gate failure gets an A-decision, never a silent fix | AGENTS.md §Execution Contract | Yes (A-1, A-2, A-3, A-4) |
| A second unrelated gate miss stops for the human | walkthrough A-2 | Yes; Mat ruled A-3; A-4 re-ran once and passed |
| Plan text free of brace and angle-bracket placeholders | validate_closeout_artifacts.py PLACEHOLDER | Yes |

---

## Instruction Coverage

```yaml
schema: v1
session:
  id: "session-35-tts-voice-panel-2026-10-17"
  task_class: tdd
  outcome: success
sections:
  - {id: priority_0_system_constraints_non_negotiable, cited: true, influence: 2}
  - {id: execution_contract, cited: true, influence: 3}
  - {id: testing_tdd_protocol, cited: true, influence: 3}
  - {id: windows_shell_powershell, cited: true, influence: 2}
  - {id: session_discipline, cited: true, influence: 2}
  - {id: dual_agent_workflow, cited: true, influence: 3}
  - {id: rtk_token_optimized_commands, cited: true, influence: 1}
  - {id: instruction_coverage_reflection, cited: true, influence: 2}
loaded:
  workflows: [create_plan, execution_session, execution_corrections, execution_critical_review]
  roles: [orchestrator, coder, tester]
  skills: [quality_gate, timestamp]
  refs:
    - .agent/docs/harness-profiles.md
    - .agent/context/harness.local.md
    - .agent/docs/human-decision-protocol.md
    - .agent/schemas/reflection.v1.yaml
    - .agent/context/grouping/2026-10-09-triage-residuals-session-grouping.md
    - docs/execution/plans/2026-10-16-tts-voice-panel/implementation-plan.md
    - docs/execution/plans/2026-10-16-tts-voice-panel/task.md
    - docs/execution/plans/2026-10-16-tts-voice-panel/walkthrough.md
    - docs/execution/reflections/2026-10-14-backend-robustness-reflection.md
decisive_rules:
  - P1:tests-before-production-corrections
  - P1:independent-review-no-self-approval
  - P1:gate-failure-preserve-classify-decide
  - P1:no-tolerated-failure-in-authoritative-gate
  - P1:human-approval-for-test-changes
conflicts:
  - "The system reminder asks for a Co-Authored-By trailer on commits; the user's standing rule forbids AI attribution trailers, and the user's rule wins."
  - "The zero-tolerance authoritative gate met two unrelated failures in a row (the known W2-5 timeout, A-2; a capture-picker clock race, A-3); a re-run settled the first, and the second went to Mat, who chose a test fix outside the planned scope over another re-run. After F2 a third unrelated miss (AC-66.14, A-4) was re-run once and passed."
note: "Session 35 ships runtime-truthful TTS devices with CPU fallback and a 422 load error (MEU-75) and the aligned Voice panel grid with 36 px controls (MEU-79)."
slim_candidate: ["--decision-issue takes one issue, so a session resolving two cannot reconcile both triage logs in one run", "Each handoff restates the shared gate record that walkthrough.md holds; a pointer would remove one regeneration per gate re-run", "The H1-6/6a/6b re-run after every correction repeats checks whose inputs only the gate record changed"]
overthinking_observed: false
review_churn:
  rounds_to_approval: {plan: 3, execution: 3}
  findings_per_round:
    - {review: plan, round: 1, critical: 0, high: 1, medium: 2, low: 0}
    - {review: plan, round: 2, critical: 0, high: 0, medium: 1, low: 0}
    - {review: plan, round: 3, critical: 0, high: 0, medium: 0, low: 0}
    - {review: execution, round: 1, critical: 0, high: 1, medium: 0, low: 0}
    - {review: execution, round: 2, critical: 0, high: 1, medium: 0, low: 0}
    - {review: execution, round: 3, critical: 0, high: 0, medium: 0, low: 0}
    - {review: execution, round: 4, critical: 0, high: 0, medium: 0, low: 0}
  churned_findings: 0
  finding_categories: {behavior: 3, contract_drift: 1, other: 1}
  verdicts: {changes_required: 4, approved: 4}
meu_work_classes: [correctness, mixed]
```
