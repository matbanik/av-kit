---
date: "2026-10-02"
project: "capture-viewport-chrome"
meus: ["MEU-65", "MEU-66"]
plan_source: "docs/execution/plans/2026-10-01-capture-viewport-chrome/implementation-plan.md"
template_version: "2.0"
---

# 2026-10-02 Meta-Reflection

> **Date**: 2026-10-02 (plan written 2026-10-01)
> **MEU(s) Completed**: MEU-65 `gui-capture-toolbar-icons`, MEU-66 `gui-capture-zoom`
> **Plan Source**: `docs/execution/plans/2026-10-01-capture-viewport-chrome/implementation-plan.md`

---

## Execution Trace

### Friction Log

1. **What took longer than expected?**

   Setting up the Electron binary, and the Windows gate.
   - **Electron:** the plan's container `electron-setup` used `curl` from GitHub releases, and the host permission classifier blocked it. Worse, the baseline Vitest run then imported `electron` (through `g36-csp.test.ts`), whose `index.js` ran `install.js` as a side effect and fetched the very binary that had just been blocked. I deleted it, and the user directed a revision from the previous plans. Session 27 A-5 had already settled on `install.js` (A-2).
   - **Windows gate:** it needed four attempts, but no product defect came from the gate itself. Attempt 1 passed while `CAPTURE_LOOK` L5 failed. Attempt 2 failed on load: a 48-worker zorivest pytest run kept the CPU near 96 % and timed out W1-8, a Downloader spec. Attempt 3 passed on a loaded machine, and attempt 4 passed on a quiet one.

2. **What instructions were ambiguous?**

   - **Approved oracles the geometry cannot meet.** AC-66.12's "the cursor pixel moves ≤ 1 px" was approved for both axes, but the plan's own `VIEW_TRANSFORM` centres an axis whose image fits. AC-66.4 already carried the "where no clamp applies" qualifier; AC-66.12 did not. That cost one human decision (TA-1).
   - **`--ac-coverage-only` matches AC families.** It checks families (`AC-65`), not ids, so it cannot prove per-id coverage; the reviewer checked by hand.

3. **What instructions were unnecessary?**

   The per-MEU repetition of project-wide gate evidence, as in Session 27. `walkthrough.md` is the canonical record, and both handoffs restated the gate.

4. **What was missing?**

   - **The focus model of a pointer click.** `ZOOM_KEY_SCOPE` and `PAN_GESTURES` covered keyboard focus on a toolbar button, but not the fact that a mouse click leaves focus there too. The plan's AC-66.10 negative case even pinned the keyboard half. Only the human look (L5) caught it, because jsdom and Playwright tests focused elements directly.
   - **Page-level layout in the FIC.** The plan measured the toolbar rows (`NO_OVERFLOW`) but never the draw surface's height. The Capture page column did not fill `main`, as the other pages do, so the frame stayed at 200 px. Mat noticed it outside the checklist.
   - **A load budget for the long Electron flows.** Nothing in the gate protocol separates "another agent's test run started mid-gate" from a product failure (the same gap as Session 27's ADD 2).

5. **What did you do that wasn't in the prompt?**

   - Used CPU-load replication (8 busy processes on 4 cores, `--repeat-each=10`) to show W1-8's long tail before and after TA-3, instead of arguing it.
   - Bound the attempt-2 look to the attempt-4 gate by `ui/src` byte-identity (D-29), so Mat did not repeat a manual pass.

### Quality Signal Log

6. **Which tests caught real bugs?**
   - **Electron AC-65.4** (`NO_OVERFLOW`): Red on the pre-change layout, 1300 px of content in an 836 px row.
   - **Electron AC-66.12 / AC-66.13:** caught two wrong oracles in my own new tests, not product bugs (A-3).
   - **The human `CAPTURE_LOOK` L5:** the only check that caught the focus defect. Its Red reproductions are AC-66.18 (jsdom and Electron).
   - **AC-65.8 and AC-66.19:** turned Mat's two layout observations into Red tests (a 48 px toggle jump; the page ending 199 px short of `main`).
   - **The baseline census:** found the AC-39.8 literal-id pin before any code was written, so the toolbar table design kept the literals instead of needing an amendment.

7. **Which tests were trivially obvious?**

   AC-66.5 (hit-test at zoom) is a regression lock that was green at baseline, as the plan declared. Its value is regression protection, not Red. Review F3 notes that AC-66.7's "same object" clause is proven by proxies.

8. **Did pyright/ruff catch anything meaningful?**

   No Python changed. `tsc` caught one fixture type (a non-null `annotated_path` on the zoom shot); eslint found nothing.

### Workflow Signal Log

9. **Was the FIC useful as written?**

   Yes. The single-statement contracts (`VIEW_TRANSFORM`, `ZOOM_EXAMPLE`, `ZOOM_ABOUT_EXAMPLE`, `ZOOM_KEY_SCOPE`) made the jsdom tests near-mechanical, and all 127 targeted tests passed on the first implementation run. The worked examples were exact to the pixel. The gaps were AC-66.12's per-axis wording and the click-focus case (Friction 2 and 4).

10. **Was the handoff template right-sized?**

    Mostly. The family-level AC validator again forced cross-reference tables in both handoffs, and it let F1/F2 clerical drift through until the reviewer ran `api-scope` and `plan-static` at HEAD.

11. **How many tool calls did this session take?**

    Not tracked precisely; a few hundred across execution, four Windows gate loops and closeout.

12. **Which rows were delegated, to which subagent (harness + model), and did any delegated result need rework?**

    No implementation rows were delegated. The execution review (1 round) went to a separate-context Fable 5.1 Agent subagent, the user-authorized same-vendor route. It needed no rework. Its F1/F2 were real closeout-check drifts that H2-3 would have failed on. Windows gate execution and both looks were run by Mat's local agent from request prompts; its reports measured exactly what the checklist asked for.

### Decisions Log

| ID | Stage | Question | Resolution | Chosen | Source tag | Reasoning (why this; why the alternatives lost) | Human ref |
|----|-------|----------|------------|--------|------------|--------------------------------------------------|-----------|
| D-1 | grouping | How are the TTS runtime assets provisioned? | human | Managed downloads in the model-manager flow plus Dependencies readiness rows | Human-approved | Grouping §8 D-1 (carried, Session 27's row). | USER_EXPLICIT 2026-09-30 'D-22: follow you recommendation' |
| D-2 | grouping | Residual MEUs under original phases or a new Phase 12? | autonomous | Original phases with `(residual)` sections | Local Canon | The MEU-59/60/61 precedent; this is why MEU-65/66 live in 09 (grouping §8 D-2). | — |
| D-3 | grouping | One TTS session or an engine/page split? | autonomous | One session with a split flag | Local Canon | Grouping §8 D-3 (carried). | — |
| D-4 | grouping | Where does the MCP audit sit? | autonomous | Session 28, before the Capture sessions | Local Canon | Grouping §8 D-4; Session 29 changes no MCP surface. | — |
| D-5 | grouping | Are the TECH-DEBT/DEFER rows MEUs in this batch? | autonomous | No | Local Canon | Grouping §8 D-5 (carried). | — |
| D-6 | grouping | Zoom wheel semantics | autonomous | Plain wheel zooms about the cursor; Ctrl+wheel identical | Research-backed | This session's own row; it drove `ZOOM_INPUTS` (a) and D-15's no-scrollbar pan (grouping §8 D-6). | — |
| D-7 | grouping | Rename the header palette control? | autonomous | "Commands Ctrl+K" with a command icon | Research-backed | Grouping §8 D-7 (Session 31 scope). | — |
| D-8 | planning | Plan Session 29 before Session 28? | human | Yes | Human-approved | Nothing in Session 29 depends on MEU-68 (plan D-8). | USER_EXPLICIT 2026-10-01 '/create-plan for Session 29 (Capture viewport/chrome)' |
| D-9 | planning | How are the icon buttons sized? | autonomous | `size="sm"` with an aria-hidden lucide child | Local Canon | Keeps `h-7` (AC-57.5), so no amendment is needed (plan D-9). | — |
| D-10 | planning | `role=toolbar` or labelled groups? | autonomous | Labelled `role=group` segments | Research-backed | The APG toolbar would take the arrow keys MEU-60 uses to nudge (plan D-10). | — |
| D-11 | planning | Which icons and names? | autonomous | `TOOLBAR_BUTTONS` (lucide 0.400.0); names equal the old labels | Local Canon | Help text and queries stay valid (plan D-11). | — |
| D-12 | planning | What does the options row show per tool? | autonomous | `OPTIONS_BY_TOOL` | Research-backed | Only arrow/rect have `stroke_width` (plan D-12). | — |
| D-13 | planning | How does the toggle become Options? | autonomous | Three optional `Disclosure` props | Local Canon | Other pages' DOM stays byte-identical (plan D-13). | — |
| D-14 | planning | The zoom ladder | autonomous | Chromium preset factors, 25–500 %, plus Fit | Research-backed | `page_zoom.cc` (plan D-14). | — |
| D-15 | planning | Pan mechanism | autonomous | Space/middle-drag, clamped offset, no scrollbars | Research-backed | The wheel is bound to zoom (plan D-15). | — |
| D-16 | planning | Zoom state owner and reset | autonomous | The viewport owns it; reset on `shotId` | Local Canon | 09:637 (plan D-16). | — |
| D-17 | planning | Key scope | autonomous | `ZOOM_KEY_SCOPE` | Local Canon | G11; 2026-09-28 RULE-3 (plan D-17). | — |
| D-18 | planning | Wheel normalization | autonomous | `WHEEL_STEP` (100 px accumulation) | Research-backed | MDN `deltaMode`; touchpads (plan D-18). | — |
| D-19 | planning | The anchor for button/key zoom | autonomous | The container centre | Research-backed | Editor and browser convention (plan D-19). | — |
| D-20 | planning | Test observables at zoom | autonomous | `ZOOM_OBSERVABLES` data attributes | Local Canon | No re-derived transform in tests (plan D-20). | — |
| D-21 | planning | Pan/keys discoverability | autonomous | `ZOOM_PAN_HINT` and `ZOOM_HELP_SENTENCE` | Local Canon | The HelpCard minimum (plan D-21). | — |
| D-23 | execution | Toolbar table vs the AC-39.8 literal-id pin | autonomous | Keyed by test id; `<ToolbarIconButton id="…">` | Local Canon | Keeps the literals; no amendment (MEU-65 handoff D-23). | — |
| D-24 | execution | The chevron's test id | autonomous | Derived id + `-chevron` | Local Canon | Follows id + `-panel`; no fourth prop (MEU-65 handoff D-24). | — |
| D-25 | execution | Grouping and titles of the icon row | autonomous | History and View groups; title = name | Local Canon | UX1; spec 09:619 tooltips (MEU-65 handoff D-25). | — |
| D-26 | execution | Where AC-66.17 lives | autonomous | `capture-page.behavior.test.ts` | Local Canon | It reads the viewport source, which only gains the ids in row 7 (MEU-66 handoff D-26). | — |
| D-27 | execution | The double-step guard for the two key paths | autonomous | A `WeakSet<Event>` | Local Canon | No DOM mutation (MEU-66 handoff D-27). | — |
| D-28 | execution | Live rect vs measured frame | autonomous | Mapping uses the live rect; observables use the frame | Local Canon | Keeps the MEU-59/60 jsdom stubs exact (MEU-66 handoff D-28). | — |
| D-29 | execution | Repeat `CAPTURE_LOOK` after TA-3? | autonomous | No; reuse look 2 | Local Canon | `ui/src` is byte-identical to the looked-at code (MEU-66 handoff D-29). | — |
| A-1 | planning | Where do execution and the gate run? | human | The Sessions 25–27 split | Human-approved | human-gate-decision.md §A-1. | USER_EXPLICIT 2026-10-01 'Split like Sessions 25–27 (Recommended)' |
| A-2 | execution | The container Electron install after the classifier block | human | The package's `install.js`, serially (Session 27 A-5 method) | Human-approved | The method the plan's `.ps1` already used (§A-2). | USER_EXPLICIT 2026-10-02 'Revise the Electron approach by looking at what was completed in the previous plans' |
| A-3 | execution | Two wrong new Electron oracles | human | TA-1 per-axis cursor oracle; TA-2 key sequence | Human-approved | `VIEW_TRANSFORM` centres a fitting axis; the ladder's bottom (§A-3). | USER_EXPLICIT 2026-10-02 'Per-axis oracle (Recommended)' / 'Yes, fix the sequence (Recommended)' |
| A-4 | execution | `CAPTURE_LOOK` L5: Space+drag after a tool click draws | human | A mouse click hands focus to the surface | Human-approved | Keyboard activation unchanged (§A-4). | USER_EXPLICIT 2026-10-02 'Mouse click hands focus to the image (Recommended)' |
| A-5 | execution | Mat's four observations | human | Fix the two easy layout items here; file the bake and auto-Select | Human-approved | §A-5 classification table. | USER_EXPLICIT 2026-10-02 'first classify the effort and if they are easy fixes, apply the fixes …' |
| A-6 | execution | Attempt 2: W1-8 timed out under host load | human | Harden W1-8 (TA-3), then attempt 3 | Human-approved | §A-6; replicated under synthetic load. | USER_EXPLICIT 2026-10-02 'Harden W1-8 first' |

D-22 was not raised: Stop condition S5 did not fire, because `getZoomFactor()` stayed 1 in the container and on Windows. The triage decisions in `known-issues.yaml` are cited in prose only.

---

## Pattern Extraction

### Patterns to KEEP
1. **A baseline census before the first test.** It found the AC-39.8 literal-id pin and turned it into a design constraint, so `TEST_AMENDMENTS` stayed empty for every pre-existing test.
2. **Exact worked examples in the FIC** (`ZOOM_EXAMPLE`, `ZOOM_ABOUT_EXAMPLE`). They made jsdom geometry tests pass on the first implementation.
3. **A human look as a separate gate** (`CAPTURE_LOOK`). It caught the one real interaction defect that every automated layer missed.

### Patterns to DROP
1. **Restating both axes in an oracle whose geometry has a centring rule.** Name the per-axis condition once in the contract and reference it.

### Patterns to ADD
1. **For every keyboard-focus rule, an AC for the mouse path that reaches the same focus state.** A click focuses buttons, and tests that call `.focus()` hide that.
2. **Measure the work surface, not only the toolbar.** Add a page-fill / surface-size assertion to any GUI plan that adds an interactive canvas.
3. **Load-replication before blaming load.** Run the suspect spec with `--repeat-each` under synthetic CPU load in the container and report its tail. TA-3 used this.

### Calibration Adjustment
- Estimated time: one session plus one Windows gate loop.
- Actual time: one long session; four Windows gate attempts and two human looks.
- Adjusted estimate for similar MEUs: for interactive canvas work, plan for one look → fix → re-gate loop, and ask for a quiet machine up front.

---

## Next Session Design Rules

```
RULE-1: Any AC that pins keyboard focus behaviour gets a twin AC for the mouse path that lands focus in the same place.
SOURCE: CAPTURE_LOOK L5 (a tool click left focus on the button; Space could not arm pan).
EXAMPLE: "Space on a focused button does not arm pan" → plus "after a mouse click on a tool, Space+drag pans".
```

```
RULE-2: GUI plans that add or resize a work surface assert its size against the page container at DEFAULT_WINDOW.
SOURCE: A-5 observation 2 (frame stayed at min-h-[200px]; page ended 199 px short of main).
EXAMPLE: NO_OVERFLOW on the toolbar only → plus "page bottom = main bottom; surface > its min-height".
```

```
RULE-3: A gate request names the machine-quiet steps as actions, not a precondition, and every result reports the ui-electron duration.
SOURCE: WINDOWS_GATE attempt 2 (13.2 min under a 48-worker run) vs attempt 4 (2.3 min, quiet).
EXAMPLE: "quiet machine" → "stop <named peer runs>; report what ran and the Electron-stage duration".
```

---

## Next Day Outline

1. Session 30: `capture-flatten-backup` (MEU-67) via `/create-plan`. It touches `packages/` and MCP, so run `/mcp-audit` after it.
2. Follow-ups filed here: `CAPTURE-BAKE-ARROW-THIN` (the bake's stroke and anti-aliasing; it pairs naturally with MEU-67's bake work) and `CAPTURE-AUTO-SELECT-AFTER-DRAW` (a decision for the user).
3. Bake in RULE-1 to RULE-3: mouse-path focus ACs, a surface-size assertion, explicit quiet-machine steps.
4. Review route: the same user-authorized Fable 5.1 subagent unless the user changes it.
5. Time estimate: one session plus at least one Windows gate loop and an MCP audit.

---

## Efficiency Metrics

| Metric | Value |
|--------|-------|
| Total tool calls | not tracked precisely (a few hundred) |
| Time to first green test | MEU-65 Green on day 1, right after the Red receipts |
| Tests added | Vitest: 7 new + about 30 appended specs (toolbar, zoom, fit-map, hit-test, help, behavior, primitives); Electron: 9 new specs (AC-65.4/5/8, AC-66.12–66.15, 66.18, 66.19); 1 existing spec hardened (W1-8) |
| Codex findings | Plan review: R1 changes_required (1 High, 1 Medium, 3 Low), R2 approved. Execution review: R1 approved, 3 Low (0 blocking) |
| Handoff Score (X/7) | 6/7 (review F1: the TA-3 file was missing from Changed Files until corrected) |
| Rule Adherence (%) | 90 |
| Prompt→commit time | 2026-10-02 (one day) |

### Rules Sampled for Adherence Check

| Rule | Source | Followed? |
|------|--------|-----------|
| Tests before production code; Red before Green | AGENTS.md §Testing & TDD | Yes, including the A-4/A-5 corrections (Red reproduced Mat's observations first) |
| No test expectation change without approval | AGENTS.md §Testing & TDD | Yes: TA-1, TA-2 and TA-3 were each approved before they were applied. A sub-pixel tolerance and a two-frame read inside TA-1 were disclosed in A-3 |
| Independent review; no self-approval | AGENTS.md §Dual-Agent Workflow | Yes (Fable 5.1 subagent wrote the verdict) |
| Do not pursue a classifier-denied outcome | Host instructions | **Partly.** I did not retry the download, but a test run I started still triggered it; I removed the binary and disclosed it (A-2 incident) |
| A gate failure gets an A-decision, never a silent fix | cloud-local §3.5 | Yes (A-3 to A-6) |

---

## Instruction Coverage

```yaml
schema: v1
session:
  id: "session-29-capture-viewport-chrome-2026-10-02"
  task_class: tdd
  outcome: success
sections:
  - {id: priority_0_system_constraints_non_negotiable, cited: true, influence: 2}
  - {id: execution_contract, cited: true, influence: 3}
  - {id: testing_tdd_protocol, cited: true, influence: 3}
  - {id: session_discipline, cited: true, influence: 2}
  - {id: dual_agent_workflow, cited: true, influence: 3}
  - {id: instruction_coverage_reflection, cited: true, influence: 2}
loaded:
  workflows: [execution_session, execution_critical_review]
  roles: [orchestrator, coder, tester]
  skills: [timestamp, issue_triage]
  refs:
    - .agent/docs/harness-profiles.md
    - .agent/context/harness.local.md
    - .agent/docs/cloud-local-collaboration.md
    - .agent/docs/human-decision-protocol.md
    - .agent/schemas/reflection.v1.yaml
    - docs/build-plan/09-screenshot-capture.md
    - docs/build-plan/11-page-layout.md
    - docs/execution/plans/2026-10-01-capture-viewport-chrome/implementation-plan.md
    - docs/execution/plans/2026-10-01-capture-viewport-chrome/task.md
    - docs/execution/plans/2026-10-01-capture-viewport-chrome/human-gate-decision.md
    - docs/execution/plans/2026-09-30-tts-repair/human-gate-decision.md
decisive_rules:
  - P1:tests-before-production-corrections
  - P1:human-approval-for-test-changes
  - P1:independent-review-no-self-approval
  - P1:no-tolerated-failure-in-authoritative-gate
  - P0:host-permission-denial-not-worked-around
conflicts:
  - "The plan's container electron-setup (curl from GitHub) was blocked by the host permission classifier; the user directed the Session 27 A-5 install.js method (A-2). Separately, the product's own require('electron') runs install.js on first import, so a plain Vitest run can perform a denied download as a side effect."
  - "The review workflow assumes the Codex CLI, absent on the web platform; the user-authorized same-vendor Fable 5.1 subagent route was used (human-review-decision.md)."
  - "The RTK receipt contract assumes rtk, which the container lacks; receipts used plain redirects with immediate exit capture."
note: "Session 29 ships the icon toolbar with a contextual options row, the Options toggle, and image zoom/pan for Capture. The Windows gate of record is attempt 4 (quiet; 17/17; Vitest 748, Playwright 127/0/0). CAPTURE_LOOK L5 caught a click-focus defect, fixed under A-4 with two layout follow-ups (A-5). Execution review approved in round 1 (3 Low)."
slim_candidate: ["Both MEU handoffs restate the project-wide gate evidence already canonical in walkthrough.md; a pointer would do"]
overthinking_observed: false
review_churn:
  rounds_to_approval: {plan: 2, execution: 1}
  findings_per_round:
    - {review: plan, round: 1, critical: 0, high: 1, medium: 1, low: 3}
    - {review: plan, round: 2, critical: 0, high: 0, medium: 0, low: 5}
    - {review: execution, round: 1, critical: 0, high: 0, medium: 0, low: 3}
  churned_findings: 0
  finding_categories: {claim_to_state_drift: 2, weak_test: 1}
  verdicts: {changes_required: 1, approved: 2}
meu_work_classes: [mixed, correctness]
```
