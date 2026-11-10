---
date: "2026-11-10"
project: "gui-capture-crop-tool"
meus: ["MEU-131"]
plan_source: "docs/execution/plans/2026-11-10-gui-capture-crop-tool/implementation-plan.md"
template_version: "2.0"
---

# 2026-11-10 Meta-Reflection

> **Date**: 2026-11-10 (planned and executed the same day)
> **MEU(s) Completed**: MEU-131 `gui-capture-crop-tool`, the fourth slice of the crop design Mat asked for (design D-1, grouping D-400). The Capture page gains a Crop tool. It has 8 handles, six aspect presets with a swap, X/Y/W/H fields and nudges in original px, and modal keys. Enter, a double-click inside the box or Save as copy sends the box to Session 59's `POST /captures/{id}/crop`, and the new shot is selected and named on the status line. Crop is disabled while marks are unsaved. Under Mat's plan-gate ruling (D-528) the session files MCP-ACTION-DESCRIPTIONS-HIDDEN-FROM-MODEL.
> **Plan Source**: `docs/execution/plans/2026-11-10-gui-capture-crop-tool/implementation-plan.md`

---

## Execution Trace

### Friction Log

1. **What took longer than expected?**
   - **The plan review took three rounds and 20,798,846 tokens.**
     - Round 1 (9,708,681 tokens) returned `changes_required` with one blocking High finding and two Medium findings.
       - F1: `CROP_MIN` allowed a box the endpoint refuses (a 5×300 shot), and an 8×8 shot left no box that met both the minimum and a 16:9, 4:3 or 3:2 ratio.
       - F2: row 1's toolbar pins left contradictory Green expectations for the option-group oracle.
       - F3: `d494-check.py` accepted a crop of a crop in the wrong frame.
       - Mat raised the plan loop twice: "A: +10M, dispatch (Recommended)", then "+30M, dispatch and add 2 more rounds" (50.5M and 5 rounds).
     - Round 2 (6,561,859 tokens) returned `changes_required`. F2 and F3 were fixed. F1 was only partly fixed: after rounding, the new ratio definitions still disagreed. Swapped 4:3 on 400×10 was called infeasible though a rounded 8×10 box passed, and swapped Original on 380×608 failed the literal `fitsRatio` by a float error.
     - Round 3 (4,528,306 tokens) approved, once `CROP_RATIO` built and checked one integer box from the driving side.
   - **HEAD moved during execution (S3).** A parallel session committed 237732d, the registry's Fable 5.2 line, on top of `baseline.sha` 8f29046. Mat ruled D-524 "A: Rebase baseline (Recommended)", and the six newly committed registry lines left `baseline-dirty.txt`.
   - **Two approved contracts disagreed.** AC-131.20 says choosing Annotated cancels the crop, while `CROP_MODAL` (D-518, AC-131.21) disables Annotated while the crop is open. Row 5 kept `CROP_MODAL` (D-525) and the handoff discloses it.
   - **The execution review's recheck was refused by the ledger.**
     - Round 1 (10,867,306 tokens) approved with two non-blocking Medium findings, F1 and F2.
     - The loop's reserve rule keeps the last round's cost for the next round, so 10.87M spent and 10.87M reserved overran the 20M budget. Mat ruled "B: +10M, dispatch", and round 2 (4,244,246 tokens) approved.
   - **A parallel session's untracked file broke the evidence check after round 2.** `docs/proposals/2026-11-10-download-logic-divergence-report.md` appeared at 12:46. `identity.py` hashes every untracked file, so H1-6b refused. Mat ruled D-527 "A: Exclude it (Recommended)". The check reran with only that path left out, and the reduced state equals the gate's.

2. **What instructions were ambiguous?**
   - **AC-131.20 against `CROP_MODAL`.** D-525 above.
   - **"A toast names the new shot."** The Capture page has no toast. The status line already names a new shot after a convert-on-apply, so the crop uses it (D-516), and Mat's look accepted it.
   - **The commit trailer.** The harness asks for a Co-Authored-By trailer, but task H2-5 and Mat's standing rule say there is none. The draft has none.

3. **What instructions were unnecessary?**
   - H2-1's `view_file` row, as in Session 59. H2-2's check validates the reflection against the same template and schema.

4. **What was missing?**
   - **A keyboard path for the commit key.** `CROP_COMMIT` said "Enter (focus outside a crop field)" but didn't say where focus sits after keyboard entry. The toolbar's A-4 rule moves focus to the draw surface only for a pointer click, so after keyboard entry the next Enter reached the Crop button and closed the crop. Execution F1 found it; D-526 fixed it (RULE-1).
   - **The effects that run when a command selects a new shot.** The plan traced the commit to `setSelectedId` but not to the detail load. That load calls `setTool('select')` when the shot carries a mark, which undid the prior tool the commit had restored. Execution F2 found it (RULE-2).
   - **A probe of the geometry against the real resolver before the plan review.** The ratio, minimum and rounding rules each looked right alone, and two plan rounds went into their joint satisfiability (RULE-3).
   - **A route for another session's file in the identity check.** The plan's `identity.py` has no way to name a foreign path, so a parallel session's file stopped closeout until Mat ruled (RULE-4).

5. **What did you do that wasn't in the prompt?**
   - **Found that Claude Code doesn't pass `_meta.action_descriptions` to a model.** This came from planning D-494's live run on this session's own `avkit_capture` schema. The D-521 run tested the surface a Claude Code agent really gets. At the plan gate Mat ruled the issue registered, and it is filed as MCP-ACTION-DESCRIPTIONS-HIDDEN-FROM-MODEL (D-528), P3, with no fix planned.
   - **Left the parallel session's proposal untouched and out of this commit** (D-527). The file wasn't opened, moved or changed.
   - **Saved copies of `known-issues.yaml` and the handoff before the D-528 write**, and of `meu-status.yaml`, `meu-registry.md` and `BUILD_PLAN.md` before the approval write (Session 55 RULE-2).

### Quality Signal Log

6. **Which tests caught real bugs?**
   - **Every row's Red failed by assertion.** The geometry Red and the page Red failed on their own assertions, and `red-check.py` reported 0 problems on each receipt.
   - **The corrections' Red reproduced both execution findings.** F1's test passed its mouse half and failed its keyboard half: `expected [ { …(3) } ] to have a length of 2 but got 1`. F2's failed `the prior tool survives the copy load`. `red-check.py --require AC-131.17 --require AC-131.18` found 0 problems.
   - **The D-521 run passed with IoU 1.000.** A Haiku 5.5 agent, given only the advertised description and schema, made one `list` call and one `crop` call with `unit: "px"`. Its source was the seeded shot, and the source's bytes were unchanged.
   - **Codex's probes, not the suite, found both execution findings.** The behaviour tests opened the crop and then focused the draw surface in the test, which hid F1. No test's copy carried a saved mark, which hid F2.
   - **The plan reviewer's independent reference found plan F1.** It ran over small, odd and portrait sizes against the real `resolve_region`.

7. **Which tests were trivially obvious?**
   - AC-131.1's pin that the Crop button sits after the lock and before History. It pins the order D-509 chose, which is its purpose.

8. **Did pyright/ruff catch anything meaningful?**
   - No Python changed. `tsc --noEmit` and ESLint with `--max-warnings 0` stayed clean through every row and the corrections.

### Workflow Signal Log

9. **Was the FIC useful as written?**
   - Yes. The mechanism ids (`CROP_ENTRY`, `CROP_RATIO`, `CROP_COMMIT`, `CROP_MODAL` and the rest) let the Reds, the handoff, the review findings and D-526 name the same contract. F1 and F2 each cited the mechanism and the AC they broke.

10. **Was the handoff template right-sized?**
    - Yes for one MEU. The cross-reference AC rows for earlier MEUs exist only for the AC check (`slim_candidate`).

11. **How many tool calls did this session take?**
    - About 1,280 in this conversation's transcript at H2-2. It covers planning, the three plan rounds, execution, both execution rounds and closeout.

12. **Which rows were delegated, to which subagent (harness + model), and did any delegated result need rework?**
    - Row 7's D-521 run used one Haiku 5.5 subagent as the test subject, not as a builder. The coordinator ran every row itself. Codex reviewed the plan and the execution as the independent reviewer, which isn't delegation.

### Decisions Log

| ID | Stage | Question | Resolution | Chosen | Source tag | Reasoning (why this; why the alternatives lost) | Human ref |
|----|-------|----------|------------|--------|------------|--------------------------------------------------|-----------|
| D-400 | grouping | Adopt the crop design's slices as registered MEUs and plan the first session? | human | Yes: MEU-128 to MEU-132, Session 58 planned now | Human-approved | Mat asked for the grouping and the first plan after ruling design D-1. This session executed the fourth slice, MEU-131. | USER_EXPLICIT 2026-11-08 "create new session grouping and start the first create plan from it" |
| D-401 | grouping | Slice to MEU mapping | autonomous | One MEU per slice; MEU-130 depends on MEU-128 | Local Canon | The GUI sends its box to Session 59's endpoint, which resolves it with Session 58's `resolve_region`, so the tool's minimum is the resolver's. Two-way. | — |
| D-402 | grouping | Which slices share Session 58? | autonomous | S1 and S3 (MEU-128, MEU-129) | Local Canon | Not touched in this session. Two-way. | — |
| D-403 | grouping | Build-plan home and band | autonomous | 09 §Residuals registered 2026-11-08, matrix rows 9.35 to 9.39, band P2 | Local Canon | Row 9.38's MEU-131 now reads approved in the registry. Two-way. | — |
| D-404 | grouping | Where does MEU-131's C key come from? | autonomous | A page-scoped shortcut registry entry; else C arrives with MEU-105 and the button ships alone | Local Canon | The registry has no page-scoped letter entries, so the Crop button ships alone and C arrives with MEU-105 (D-508). Two-way. | — |
| D-405 | grouping | Where do the crop sessions sit in the queue? | autonomous | Sessions 58 to 61, after rc.2's Session 57 | Local Canon; Research-backed | Session 60 ran after Session 59 and the rc.3 release. Two-way. | — |
| D-406 | grouping | How do crop and the pending mark types meet? | autonomous | MEU-130 clips every mark type on main when it executes; a later mark type adds its own crop rule | Local Canon | The GUI sends only a box; the endpoint carries the marks, so this session adds no mark rule. Two-way. | — |
| D-508 | planning | Does the C key arrive with the crop tool, as D-404 asks the plan to check? | autonomous | No: the Crop button ships alone with the tooltip Crop and no aria-keyshortcuts; C arrives with MEU-105 | Local Canon | The registry has no page-scoped letter entries, and adding one letter here would start the pattern MEU-105 owns. Two-way. | — |
| D-509 | planning | Where does the Crop button go? | autonomous | After the lock and before the History group, as its own ToolbarIconButton outside the Annotation tool group | Local Canon | A crop isn't a mark, so it doesn't sit with the mark tools. AC-131.1 pins the place. Two-way. | — |
| D-510 | planning | How does the page hold the crop, and what ends it? | autonomous | One crop state on CapturePage in integer original px, with the aspect, swap, prior tool, drag and busy flag | Local Canon | One owner keeps the bar, the overlay and the keys in step, and a selection change or a cancel ends it in one place. Two-way. | — |
| D-511 | planning | What are the box's rounding, minimum and edge rules? | autonomous | CROP_ROUND, CROP_MIN, CROP_HANDLES, CROP_MOVE and CROP_DRAW: integers half up, 8 a side as the endpoint's minimum, Crop disabled on a smaller shot | Inferred | Plan review F1 found the first minimum let a box through that the endpoint refuses; the corrected minimum is the endpoint's own. Two-way. | — |
| D-512 | planning | How do a ratio and Shift act on a drag? | autonomous | CROP_RATIO: a preset always keeps its ratio from one integer driving-side box; under Free, Shift keeps the start ratio | Local Canon | Round 3 approved the single integer construction after two rounds on rounding. Two-way. | — |
| D-513 | planning | How do the presets and the swap place the box? | autonomous | CROP_PRESETS and CROP_SWAP: the largest box of the ratio inside the image, centred on the current box; an infeasible ratio or swap is disabled | Local Canon | A box that fits is centred where the user was working; a ratio the image can't hold at 8 px is disabled, not bent. Two-way. | — |
| D-514 | planning | How do the number fields read and apply text? | autonomous | CROP_FIELDS and CROP_NUDGE: Enter or blur applies, invalid text reverts, decimals round half up, negatives become 0 | Local Canon | The fields are whole original px, as the readout and the request are. Two-way. | — |
| D-515 | planning | Which keys does the crop take, and what does it ignore? | autonomous | CROP_MODAL: Enter commits, Esc cancels, arrows nudge, X swaps; every other key does nothing on the page while the crop is open | Local Canon | A modal tool must not let a letter or a mark tool act on a half-made crop. D-526 later sent Enter on the Crop toggle to the commit. Two-way. | — |
| D-516 | planning | What is the toast that names the new shot? | autonomous | The Capture status line, as a convert-on-apply uses it: Saved crop as display_name | Inferred | The page has no toast, and Mat's look accepted the status line. Two-way. | — |
| D-517 | planning | What does the tool show while the request runs and when it fails? | autonomous | CROP_ERRORS: Save as copy disabled with aria-busy and Cropping… while pending; an error keeps the crop open with its box | Local Canon | The user keeps the box they drew and sees the endpoint's fixed, path-free message. Two-way. | — |
| D-518 | planning | What happens to the other toolbar buttons while the crop is open? | autonomous | The tool buttons, Undo, Redo, the lock and Annotated are disabled with the reason Finish or cancel the crop first; a second click on Crop cancels | Inferred | A disabled button with a reason tells the user why; D-525 holds it over AC-131.20's Annotated sentence. Two-way. | — |
| D-519 | planning | Does MEU-132 ride with this session, and what is the split? | autonomous | No: MEU-132 stays in Session 61; the split flag moves the presets and fields to Session 60b | Local Canon | The crop tool filled the session, and the split was not needed. Two-way. | — |
| D-520 | planning | How does the Electron proof reach the crop endpoint? | autonomous | A page.route seam in capture-inbox.test.ts, as the flatten proofs do | Local Canon | The endpoint's behaviour is proven by Session 59's suite; AC-131.23 and AC-131.24 prove the GUI's request and its result. Two-way. | — |
| D-521 | planning | How is D-494's live agent run done? | human | A: one Haiku 5.5 subagent against this work tree's MCP server and a Pillow test inbox, judged by D494_RUN | Human | A weak reader tests the description hardest. The run passed with IoU 1.000 on the advertised surface, which lacks the crop text (D-528). | USER_EXPLICIT 2026-11-10 'A: Haiku 5.5 (Recommended)' |
| D-522 | planning | Does Mat look at the tool before the execution review? | human | A: row 6 launches the dev app detached on a test inbox, and Mat crops a marked shot with the handles, a preset and the fields | Human | A drag tool's feel isn't proven by tests. Mat approved, and the launch's 14 processes were stopped by recorded id. | USER_EXPLICIT 2026-11-10 'A: Look (Recommended)' |
| D-523 | planning | Where do the crop bar's icon buttons get their names? | autonomous | CROP_BUTTONS, a record apart from TOOLBAR_BUTTONS and ACTION_BUTTONS, rendered through ToolbarIconButton | Local Canon | The bar's buttons aren't toolbar tools, so they don't join the toolbar's records. Two-way. | — |
| D-524 | execution | HEAD moved from baseline.sha 8f29046 to 237732d during execution (S3). How does the session go on? | human | A: baseline.sha becomes 237732d and the six now-committed registry lines leave baseline-dirty.txt | Human-approved | The new commit touched only the model registry, which no row edits; every other baseline line kept its SHA-256. | USER_EXPLICIT 2026-11-10 'A: Rebase baseline (Recommended)' |
| D-525 | execution | AC-131.20 says choosing Annotated cancels the crop, while CROP_MODAL disables Annotated while the crop is open. Which holds? | autonomous | CROP_MODAL holds: Annotated is disabled with Finish or cancel the crop first, and AC-131.20's test asserts that | Local Canon | D-518 and AC-131.21 are the more specific rule, and a disabled button can't cancel anything. The handoff discloses it. Two-way. | — |
| D-526 | execution | Review round 1 F1: after keyboard entry, Enter reaches the Crop button and closes the crop with no POST. Fix by moving focus or by routing Enter? | autonomous | Enter on the Crop toggle commits while the crop is open; Enter on any other button stays that button's; Space still closes | Local Canon | The toggle isn't a crop field, so CROP_COMMIT's Enter applies to it. Moving focus would break A-4's keyboard rule for one button. Two-way. | — |
| D-527 | closeout | After round 2, a parallel session's untracked proposal changed the live identity and H1-6b refused. How does closeout check the evidence? | human | A: rerun H1-6b with the expected state from identity.py with only that path left out; the file stays untouched and out of this commit | Human-approved | The file isn't this session's to move. Leaving out only that path proved every Session 60 input unchanged. Doing nothing would stop closeout. | USER_EXPLICIT 2026-11-10 'A: Exclude it (Recommended)' |
| D-528 | closeout | Claude Code doesn't show a model _meta.action_descriptions, where each MCP action's text lives. Register it as a known issue? | human | A: register it as MCP-ACTION-DESCRIPTIONS-HIDDEN-FROM-MODEL, P3, open, linked to MEU-131, no fix planned | Human-approved | The session is renderer-only and changes no MCP text. Registering keeps the probe and the D-521 run's feedback for a plan of its own. | USER_EXPLICIT 2026-11-10 plan gate 'A: Register it (Recommended)' |

---

## Pattern Extraction

### Patterns to KEEP
1. **A live agent run on the surface a client really shows.** Planning D-494 on this session's own tool schema found the `_meta` gap before the run, so the run measured what a Claude Code agent gets.
2. **A selftested checker for a live run.** `d494-check.py`'s 19-case selftest, with a crop-of-a-crop negative added after plan F3, gave the run a pass rule fixed before the run.
3. **A human look launched detached, ended by recorded id** (Session 56 RULE-2). The look's 14 processes were stopped by id, and nothing else was touched.
4. **An identity check that names the one path it leaves out.** D-527 proved the reduced state equals the gate's, instead of rerunning the gate with a foreign file inside it.

### Patterns to DROP
1. **Behaviour tests that focus the draw surface themselves after opening a mode.** The test-only focus call hid F1, the keyboard path a user takes.

### Patterns to ADD
1. **Test a key after a mode opens by pointer and by keyboard entry** (RULE-1).
2. **Trace every effect that runs on a selection change a command makes** (RULE-2).
3. **Probe a joint geometry contract against the real resolver before the plan review** (RULE-3).
4. **Check the path list before rerunning an identity-bound check** (RULE-4).
5. **Budget the execution loop for the ledger's reserve** (RULE-5).

### Calibration Adjustment
- **Estimated:** the plan expected 1 to 3 plan rounds (about 10M to 24M) and 2 to 3 execution rounds (about 12M to 25M).
- **Actual time (local time, UTC-5, 2026-11-10):**
  - Plan rounds 1, 2 and 3 returned at 01:36, 08:55 and 09:13.
  - The baseline receipt is from 10:22, the geometry Red and Green from 10:27, and the page Green from 10:57.
  - Mat's look and the D-521 run checked at 11:48 and 11:49.
  - Execution round 1 returned at 12:21. The correction Red was at 12:26 and its Green at 12:27, the gate rerun ended at 12:32, and round 2 approved at 12:48.
- **Tokens:** the plan review used 20,798,846 tokens over three rounds. The execution review used 15,111,552 over two rounds (10,867,306 and 4,244,246) of a 30M budget.
- **Adjusted estimate for a one-MEU renderer tool with geometry and a live run:** a day, as planned. Budget about 21M for the plan review when it holds a joint geometry contract, about 11M for execution round 1 and about 4.5M per recheck. Open the execution loop at 26M or more, so the ledger's reserve for round 2 fits (RULE-5).

---

## Next Session Design Rules

```
RULE-1: An AC that names a key pressed straight after a mode opens has a test that opens the mode by pointer and again by keyboard (Tab to the button, Enter), with no test-only focus call between entry and the key.
SOURCE: Execution F1. The toolbar's A-4 rule moves focus to the draw surface only for a pointer click, so after keyboard entry Enter reached the Crop button and closed the crop. The behaviour tests focused the surface themselves and passed.
EXAMPLE: "click Crop; focus the surface; press Enter" -> "click Crop; press Enter (one POST); focus the Crop button; Enter to open; Enter again (a second POST)".
```

```
RULE-2: When a command selects a new item, the plan lists every effect that runs on a selection change and says what each does to the state the command just set, and a test drives a new item carrying the data each effect branches on.
SOURCE: Execution F2. The commit restored the prior tool and selected the copy, and the copy's detail load then ran setTool('select') because the copy carried a saved mark. No test's copy carried a mark.
EXAMPLE: "commitCrop restores prior and selects the copy" -> "commitCrop restores prior and selects the copy; the detail load (CapturePage.tsx:563-589) skips setTool('select') for that copy; AC-131.17's test gives the copy SAVED_RECT".
```

```
RULE-3: A geometry contract that joins rounding, a minimum and a ratio is defined from one integer construction, and the plan probes it against the real resolver over small, odd and portrait sizes, citing the receipt, before the plan review is dispatched.
SOURCE: Plan F1 took rounds 1 and 2: the first minimum let a 5×300 box through that resolve_region refuses, and the second ratio definitions disagreed after rounding on 400×10 and 380×608.
EXAMPLE: "CROP_MIN: 8 a side; CROP_RATIO: w/h within tolerance" -> "CROP_RATIO: the driving side's integer range gives min, largest and feasibility; probe over sizes 1..40 and 380×608 against resolve_region, 0 wrong".
```

```
RULE-4: Before an identity-bound check is rerun after a review, the coordinator lists the tree's changed and untracked paths against the gate's scope-paths receipt. Any path outside it goes to Mat as a brief before the check runs, with leaving that one path out by name as an option and doing nothing as another.
SOURCE: D-527. A parallel session's untracked proposal appeared after the gate, identity.py hashed it, and H1-6b refused after round 2 had approved.
EXAMPLE: "rerun H1-6b" -> "git status --porcelain -uall vs s60-scope-paths: 1 extra path (docs/proposals/...); brief to Mat before H1-6b".
```

```
RULE-5: An execution loop's opening budget covers the round 1 estimate twice plus one recheck, because the ledger reserves the last round's cost for the next round before it lets that round dispatch.
SOURCE: Round 1 cost 10,867,306 tokens of a 20M budget, so 10.87M spent plus 10.87M reserved overran it, and the round 2 dispatch was refused until Mat added 10M.
EXAMPLE: "20M, 3 rounds (round 1 about 10M)" -> "26M, 3 rounds: round 1 about 11M, the ledger's reserve about 11M, a recheck about 4.5M".
```

---

## Next Day Outline

1. **Target:** done in the tree, not committed. MEU-131 is approved and MCP-ACTION-DESCRIPTIONS-HIDDEN-FROM-MODEL is open. The commit waits on Mat's words, and the parallel session's proposal stays out of it.
2. **Next session:** Session 61 `gui-capture-image-import` (MEU-132): drop, an Import image button, a file dialog and Ctrl+V paste into the Capture inbox (grouping `:78-80`). It carries D-400. Its prompt is `C:/Temp/av-kit/session-61-prompt.md`.
3. **Scaffold changes needed:** none.
4. **Patterns to bake in from today:** RULE-1 to RULE-5 here, plus the rules carried from Sessions 50 to 59.
5. **Codex validation scope:** Session 61's plan, then its execution.
6. **Time estimate:** a day. The main-process file dialog and the paste path are the largest pieces.

---

## Efficiency Metrics

| Metric | Value |
|--------|-------|
| Total tool calls | About 1,280 in this conversation's transcript at H2-2, from planning on |
| Time to first green test | The geometry Green at 2026-11-10 10:27 (UTC-5), after its Red the same minute (`s60-red-geometry.txt`, `s60-green-geometry.txt`) |
| Tests added | Vitest 1193 → 1222 (+29 in 2 new files, 2 of them from the round 1 corrections); Electron `capture-inbox.test.ts` 43 → 45 (+2); pytest 1564 and MCP 485 unchanged |
| Codex findings | Plan review: R1 `changes_required` with F1 High blocking and F2, F3 Medium (9,708,681); R2 `changes_required`, F1 partly fixed (6,561,859); R3 approved (4,528,306). Execution review: R1 approved with F1 and F2 Medium non-blocking (10,867,306); R2 approved, both fixed, `intent_achieved: yes` (4,244,246; 15,111,552 of 30,000,000) |
| Handoff Score (X/7) | 6/7. Every AC has evidence and the gate passed on each run. The pre-handoff self-review missed the keyboard-entry Enter and the copy's tool reset (F1, F2) |
| Rule Adherence (%) | 86 (18 of 21 triggered rules followed in full, 3 in part) |
| Prompt→commit time | Planned and executed 2026-11-10; not committed, waiting on Mat |

### Rules Sampled for Adherence Check

| Rule | Source | Followed? |
|------|--------|-----------|
| Tests before production code; Red before Green | AGENTS.md §Testing & TDD | Yes. Every row's Red and the corrections' Red failed by assertion before the code changed |
| Independent review; no self-approval | AGENTS.md §Dual-Agent Workflow | Yes. The canonical reviews are Codex's reports, validated under `C:/Temp/av-kit` and copied byte for byte |
| A raw value that can reach a log, stdout or the Console is fixed in the row or raised | Session 50 rule | Yes. The status line shows the display name and the endpoint's fixed messages; no path reaches it |
| A row that edits a byte-hashed file runs that test in its own check | Session 50 rule | Yes. Row 4 put the crop ids in an additive block at the end of `test-ids.ts`, and its check ran AC-51.6 and AC-81.13 |
| Each row re-reads its lines; moved cites corrected in the handoff | Session 51 RULE-3 | Yes. The handoff's cites were moved after the corrections (`:753`, `:828`, `:892`) |
| tested_state prompts name the user git ignore and `.claude/settings.local.json` | Session 51 RULE-4 | Yes |
| Recheck cells take bare words | Session 52 RULE-1; Session 57 RULE-5 | Yes. Round 2's Recheck Result reads `fixed` |
| A loop's budget is compared with the last comparable round | Session 52 RULE-3; Session 58 RULE-4 | Partly. The 20M budget was compared with Session 59's loop, but it didn't leave room for the ledger's reserve (RULE-5) |
| Shared missing names go in a type-only row first | Session 53 RULE-2 | Yes. Row 1 |
| Handoff checks before the review prompt; every cited AC has a row | Session 54 RULE-3 | Yes. H1-6 and H1-6a passed before each dispatch |
| A cited authorization is checked with grep | Session 54 RULE-4 | Yes |
| The plan is a decision source; no braces in decision_log | Session 54 RULE-5 | Yes. The closeout probe passed with the plan, the handoff, the grouping and the register |
| List and run the callers of a shared list the plan extends | Session 55 RULE-1 | Yes. Every reader of `CaptureTool` and the toolbar records ran in row 5's Green |
| Diff a shared file's bytes after a tool rewrites it | Session 55 RULE-2 | Yes |
| UTF-8 output for every Python probe | Session 55 RULE-5 | Yes |
| A human-check row ends its own launch by recorded id | Session 56 RULE-2 | Yes. 14 processes, all this launch's |
| A system-wide resource is checked free before E2E; never stop another program | Session 57 RULE-4 | Yes. F2 was checked free before each Electron run |
| Order pins grepped when a list gains a row | Session 59 RULE-1 | Yes. Plan F2 found the toolbar oracle's semantic pins, and row 1 amended them |
| Every command through RTK | AGENTS.md §RTK | Partly. Tests, gates, tools and dispatches went through `rtk proxy`; many reads did not, and the RTK hook isn't installed on this PC |
| No branches or worktrees; never commit or push without the human | AGENTS.md §Commits | Yes. The work is on `main`, and nothing from this session is committed |
| Check every AC against current file:line and probe its contract before handoff | AGENTS.md §Pre-Handoff Self-Review | Partly. AC-131.18 was checked by pointer entry only and AC-131.17 on a copy with no marks (F1, F2) |

---

## Instruction Coverage

```yaml
schema: v1
session:
  id: "38d6417e-178d-40da-a9da-9198edfa0c54"
  task_class: tdd
  outcome: success
sections:
  - {id: priority_0_system_constraints_non_negotiable, cited: true, influence: 3}
  - {id: planning_contract, cited: true, influence: 3}
  - {id: testing_tdd_protocol, cited: true, influence: 3}
  - {id: execution_contract, cited: true, influence: 3}
  - {id: session_discipline, cited: true, influence: 2}
  - {id: dual_agent_workflow, cited: true, influence: 3}
  - {id: commits, cited: true, influence: 3}
  - {id: validation_pipeline, cited: true, influence: 3}
  - {id: rtk_token_optimized_commands, cited: true, influence: 1}
  - {id: instruction_coverage_reflection, cited: true, influence: 2}
loaded:
  workflows: [create_plan, plan_critical_review, execution_session, execution_critical_review, execution_corrections]
  roles: [orchestrator, coder, tester]
  skills: []
  refs:
    - .agent/docs/human-decision-protocol.md
    - .agent/docs/harness-profiles.md
    - .agent/schemas/review-verdict.schema.v2.json
    - .agent/schemas/reflection.v1.yaml
    - .agent/templates/REVIEW-TEMPLATE.md
    - docs/execution/reflections/TEMPLATE.md
decisive_rules: [P0:never-commit-or-push-without-human-approval, P0:human-decisions-stay-human, P0:raw-values-fixed-or-raised, P1:independent-review-no-self-approval, P1:tests-before-production-code]
conflicts:
  - "The harness asks for a Co-Authored-By trailer on commits; task H2-5 and Mat's rule say no AI attribution trailer. The draft has none."
  - "A connected docs server offered to publish deliverables; the user's rule keeps them as local repo files."
note: "The Capture page crops a shot into a new copy with handles, presets and fields, through Session 59's endpoint."
slim_candidate: ["The handoff's cross-reference AC rows for earlier MEUs exist only for the AC check."]
overthinking_observed: false
review_churn:
  rounds_to_approval: {plan: 3, execution: 1}
  findings_per_round:
    - {review: plan, round: 1, critical: 0, high: 1, medium: 2, low: 0}
    - {review: plan, round: 2, critical: 0, high: 1, medium: 0, low: 0}
    - {review: plan, round: 3, critical: 0, high: 0, medium: 0, low: 0}
    - {review: execution, round: 1, critical: 0, high: 0, medium: 2, low: 0}
    - {review: execution, round: 2, critical: 0, high: 0, medium: 0, low: 0}
  churned_findings: 1
  finding_categories: {boundary_validation: 1, contract_drift: 3, weak_test: 1}
  verdicts: {changes_required: 2, approved: 3}
meu_work_classes: [correctness]
```
