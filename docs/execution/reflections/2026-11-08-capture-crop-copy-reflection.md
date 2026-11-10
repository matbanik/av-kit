---
date: "2026-11-08"
project: "capture-crop-copy"
meus: ["MEU-130"]
plan_source: "docs/execution/plans/2026-11-08-capture-crop-copy/implementation-plan.md"
template_version: "2.0"
---

# 2026-11-08 Meta-Reflection

> **Date**: 2026-11-08 (planned), executed 2026-11-09
> **MEU(s) Completed**: MEU-130 `capture-crop-copy`, the third slice of the crop design Mat asked for (design D-1, grouping D-400). An agent cuts a region of any capture into a new PNG shot with source `Crop`, carrying the source's saved marks clipped to the crop, and the source never changes. Under Mat's D-499 A the session files MCP-AUDIT-BASELINE-PENDING-CROP
> **Plan Source**: `docs/execution/plans/2026-11-08-capture-crop-copy/implementation-plan.md`

---

## Execution Trace

### Friction Log

1. **What took longer than expected?**
   - **The plan review took three rounds and 23,266,843 tokens.**
     - Round 1 (12,513,669 tokens) returned `changes_required` with one blocking High finding. The plan's zero-size shortcut dropped a zero-width or zero-height rect that crosses the crop, though the adapter draws such a rect as a line. Five non-blocking Medium findings came with it: AC-130.19's eraser oracle, AC-130.13's view oracle, an unbounded default stem, AC-130.3's sign rule and AC-130.22's ring control. Round 1 was over the 5.25M line at which the plan asks Mat, and Mat added 60M and two rounds ("add 60M tokes and 2 more rounds").
     - Round 2 (7,047,382 tokens) approved.
     - Round 3 (3,705,792 tokens) approved the amendment that row 0's S11 stop required (D-476).
   - **Row 0 stopped at S11.** Session 58's execution review changed the `.avkit-tmp` pattern this plan had copied from Session 58's plan (its F1 and F2). `baseline.ps1` checks S11 by name only, so the stop came from the brief, not the script. Mat ruled "A: plan round 3 (Recommended)", and the amendment went through plan round 3 before row 1.
   - **The first gate passed with 21 warnings.** All were Pillow 13's `DeprecationWarning` for `Image.getdata()`, from six calls in the new crop test module. The calls moved to `get_flattened_data()`, and the gate ran again on the whole tree.
   - **Execution review round 1 (8,336,600 tokens) returned `changes_required`.**
     - F1 (High, blocking): a CMYK JPEG's crop dropped its ICC profile. Row 5 set `icc = None` for CMYK, YCbCr and LAB, a departure from D-482 and AC-130.10 that it didn't record. The pre-handoff self-review held AC-130.10 to its RGB PNG case and missed it.
     - F2 (Medium, not blocking): an arrow's exact half-pixel entry rounded down in one direction, from floating-point error at the tie.
     - F1's fix amended an approved AC, so it went to Mat, who ruled D-506 A. The corrections, their Reds and the gate rerun took about 45 minutes, and round 2 (4,475,811 tokens) approved.

2. **What instructions were ambiguous?**
   - **The commit trailer.** The harness asks for a Co-Authored-By trailer. Task H2-5 and Mat's standing rule say there is none. The draft has none.
   - **"A Windows reserved name" in CROP_NAME.** The plan didn't say whether `CON.txt` counts. Windows reserves the part before the first dot, so the code reads that part, the stricter reading, and the handoff discloses it.

3. **What instructions were unnecessary?**
   - H2-1's `view_file` row, again. H2-2's check validates the reflection against the same template and schema.

4. **What was missing?**
   - **The callers of a test that pins an order.** D-492 put `crop` after `revert` in `ACTION_INDEX`. The plan listed the tests that count rows, but not AC-67.19 (`runner-fake-backend.test.ts:185`), which pinned `capture_interactive` directly after `revert`. Row 5 amended it and disclosed the test change (RULE-1).
   - **The same check for an enum's order.** Row 2 found that `test_ac_129_1_capture_source_import` asserted Import is the last `CaptureSource` member, which D-484's `Crop` breaks. The plan hadn't named it.
   - **A rule about Pillow's deprecations in new tests.** Pillow 13 warns on `getdata()`, and a new module written from older tests used it six times. The suite's warnings, not a failure, found it.
   - **A note that pytest's failure headers can outgrow red-check's split.** A long test id leaves fewer than three underscores in pytest's centred header, and `red-check.py` then reads two blocks as one. Two tests were renamed shorter (`w0` and `h0` ids, `keeps_a_temp_file_it_did_not_write`) (RULE-2).

5. **What did you do that wasn't in the prompt?**
   - **Amended two tests the plan didn't name,** AC-129.1's last-member assert (row 2) and AC-67.19's order pin (row 5), and disclosed both.
   - **Put the damaged source's bytes back before AC-130.21's follow-up list.** The list scans the inbox, and the scan's `probe` doesn't catch Pillow's `SyntaxError`, so a damaged PNG left in the inbox turns `GET /captures` into a 500. The crop's own 422 was right.
   - **Recorded that pre-existing scan behaviour as an observation, and raised it with Mat at closeout, who had it filed as `CAPTURE-SCAN-UNPROBEABLE-FILE-BREAKS-LIST` (D-507).** `probe` refuses a non-image with `InboxPathError(f"{path} is not an image")`, a path in an API message, which Session 50's rule says is fixed or raised, never left as a residual.
   - **Built the audit plan's `capture.crop` step as its own `StepSpec`.** `simpleStep`'s `args` runs synchronously and can't read the source's SHA-256 over REST first, so the step reads the hash, calls, registers the new id, and checks the source's bytes are unchanged.
   - **Saved copies of `meu-status.yaml`, `meu-registry.md`, `BUILD_PLAN.md` and `known-issues.yaml` before each tool rewrite** (Session 55 RULE-2). `meu_status.py update` re-wrapped four long notes and the top comment that commit f15626c wrote by hand; a YAML comparison shows only MEU-130's fields changed.

### Quality Signal Log

6. **Which tests caught real bugs?**
   - **Every row Red failed by assertion.** The mark-carry Red failed 72 (2 passed, the amended AC-129.1 and an untouched guard). The crop Python Red failed 35, the MCP Red 6 and the UI Red 1. `red-check.py` reported 0 problems on each receipt.
   - **AC-130.21's damaged-source case found the scan's 500** described above, outside the crop.
   - **AC-130.13's parity cases prove D-401:** a crop and a region view of the same box report the same applied box and the same pixels.
   - **Codex's probes, not the suite, found both execution findings.** A SWOP-profiled CMYK JPEG had 557168 ICC bytes before the crop and 0 after; AC-130.10 covered only an RGB PNG. An exact-rational oracle over 20000 arrows found 2 half-tie mismatches that AC-130.3's eleven cases missed.
   - **The correction Reds failed by assertion with their controls passing.** F2's forward case failed `(8, 4) != (8, 5)` and its reverse passed. F1's profile assertion failed and both plain-fallback cases passed. `red-check.py` found 0 problems on each.
   - **F1's test builds its CMYK profile in bytes** (a 320-byte ICC v2 profile with a Lab PCS and a lut16 `A2B0`), so no system profile is read.

7. **Which tests were trivially obvious?**
   - AC-130.7, that `Crop` is a `CaptureSource` member and the last one. It pins the order D-484 chose, which is its purpose.

8. **Did pyright/ruff catch anything meaningful?**
   - pyright required `Image.info`'s key type, `dict[str | tuple[int, int], object]`, in CROP_PIXELS. That was a type spelling, not a defect. ruff caught one E501 in the getdata fix. `ruff format --check` already flags `tests/unit/test_capture_service.py` at HEAD, and the gate runs `ruff check`, not the formatter.

### Workflow Signal Log

9. **Was the FIC useful as written?**
   - Yes. The 15 mechanism ids let the Reds, the handoff and the review prompts name the same contract. The plan's per-AC Red reasons matched what each Red printed.

10. **Was the handoff template right-sized?**
    - Yes for one MEU. The cross-reference AC rows (AC-16, AC-90 and the other guards) exist only for the AC check, and H1-6 refused until the two missing ones were added (`slim_candidate`).

11. **How many tool calls did this session take?**
    - About 930 in this conversation's transcript at H2-2. It covers plan round 3, execution and both execution review rounds; plan rounds 1 and 2 ran in Session 58's conversation.

12. **Which rows were delegated, to which subagent (harness + model), and did any delegated result need rework?**
    - None. The coordinator ran every row. Codex reviewed the plan and the execution as the independent reviewer, which isn't delegation.

### Decisions Log

| ID | Stage | Question | Resolution | Chosen | Source tag | Reasoning (why this; why the alternatives lost) | Human ref |
|----|-------|----------|------------|--------|------------|--------------------------------------------------|-----------|
| D-400 | grouping | Adopt the crop design's slices as registered MEUs and plan the first session? | human | Yes: MEU-128 to MEU-132, Session 58 planned now | Human-approved | Mat asked for the grouping and the first plan after ruling design D-1. This session executed the third slice, MEU-130. | USER_EXPLICIT 2026-11-08 "create new session grouping and start the first create plan from it" |
| D-401 | grouping | Slice to MEU mapping | autonomous | One MEU per slice; MEU-130 depends on MEU-128 | Local Canon | The crop calls Session 58's `resolve_region`, so a crop and a region view of the same box cut the same pixels; AC-130.13 proves it. Two-way. | — |
| D-402 | grouping | Which slices share Session 58? | autonomous | S1 and S3 (MEU-128, MEU-129) | Local Canon | The mark carry is the batch's largest piece, so MEU-130 ran alone in Session 59. Two-way. | — |
| D-403 | grouping | Build-plan home and band | autonomous | 09 §Residuals registered 2026-11-08, matrix rows 9.35 to 9.39, band P2 | Local Canon | Row 9.37's MEU-130 now reads ✅ approved in the registry. Two-way. | — |
| D-404 | grouping | Where does MEU-131's C key come from? | autonomous | A page-scoped shortcut registry entry; else C arrives with MEU-105 and the button ships alone | Local Canon | Session 60's question. Not touched in this session. Two-way. | — |
| D-405 | grouping | Where do the crop sessions sit in the queue? | autonomous | Sessions 58 to 61, after rc.2's Session 57 | Local Canon; Research-backed | Session 59 executed after Session 58's 8e79282 and the rc.3 release. Two-way. | — |
| D-406 | grouping | How do crop and the pending mark types meet? | autonomous | MEU-130 clips every mark type on main when it executes; a later mark type adds its own crop rule | Local Canon | `clip_mark` matches every `Annotation` member and ends in `assert_never`, so a member added without a crop rule is a pyright error; AC-130.6 checks every member. Two-way. | — |
| D-476 | planning | S11 at row 0: Session 58's execution changed the .avkit-tmp pattern from its plan. How does this plan meet it? | human | A: amend the plan narrowly and send it through plan-review round 3 before row 1 | Human-approved | The amendment made the temporary file exclusive, counted a name whose temporary file exists as taken, put every filesystem call inside the mapped try, and added the keeps-a-temporary-file and damaged-PNG cases. Executing the plan as approved would have repeated Session 58's F1. Round 3 approved it at 3,705,792 tokens. | USER_EXPLICIT 2026-11-09 'A: plan round 3 (Recommended)' |
| D-481 | planning | How does a crop take its box, and what does it read? | autonomous | CROP_REQUEST and CROP_READ: float fields resolved by Session 58's resolve_region; the row and sidecar read under CAPTURE_FILE_LOCK; a changed file is 409 and an unreadable one 422, neither naming a path | Local Canon | One resolver is grouping D-401. Reading outside the lock would let an annotate change the sidecar between read and write. Two-way. | — |
| D-482 | planning | How are the crop's pixels written? | autonomous | CROP_PIXELS: a new port method that cuts with no resampling, keeps the mode when PNG stores it, keeps the ICC profile and writes no EXIF, XMP or text | Local Canon | A crop is the original's pixels, so an agent reading it sees what it chose. AC-130.9 and AC-130.10 pin modes and metadata. Two-way. | — |
| D-483 | planning | How is a crop named? | autonomous | CROP_NAME: the source stem cut to 100 characters plus -crop.png, then _2 and on; a sanitized name of 1 to 80 characters; free when no inbox-root file of any shot role, temporary file or row case-folds equal | Local Canon | A person finds the crop by its source's name. Execution read a reserved name by the part before the first dot, the stricter reading. Two-way. | — |
| D-484 | planning | What source value does a crop carry? | autonomous | CaptureSource.Crop after Import, with no wire value | Local Canon | A crop doesn't go through register, so it needs no wire value; 09's "wire crop" was corrected. Two-way. | — |
| D-485 | planning | Where does mark carrying live, and how is every mark type covered? | autonomous | MARK_CARRY: a pure clip_mark in domain/capture.py with assert_never; its output is a fixed point of the service's clamp | Local Canon | A pure function tests without a service, and AC-130.5's 500 random marks prove the fixed point. Two-way. | — |
| D-486 | planning | How are box marks clipped, and which bake differences follow? | autonomous | MARK_CLIP_BOX: highlight, pixelate and eraser half-open; a rect on its inclusive outline with no zero-size shortcut; design 6.5's differences corrected | Local Canon | Plan review F1 found the shortcut dropped a crossing zero-size rect, which the adapter draws as a line. AC-130.18 asserts each corrected difference on the bake. Two-way. | — |
| D-487 | planning | How is an arrow clipped? | autonomous | MARK_CLIP_ARROW: Liang-Barsky against the closed crop, ends rounded half up and clamped, dropped when rejected or zero length | Research-backed | The eleven probe cases in AC-130.3 come from the plan-time probe. Two-way. | — |
| D-488 | planning | How is a text mark carried? | autonomous | MARK_CLIP_TEXT: kept when the anchor is inside, dropped otherwise, never clipped | Local Canon | A clipped string reads as a different word. Two-way. | — |
| D-489 | planning | What does the crop write for its marks? | autonomous | CROP_BAKE: with marks, a sidecar and a bake in the configured format, both on the row; with none, neither | Local Canon | The crop reads like any annotated shot. Two-way. | — |
| D-490 | planning | What happens when a crop fails partway? | autonomous | CROP_CLEANUP: one lock hold and one unit of work; on failure remove only what this crop created, commit no row, raise CaptureFailedError (503) | Local Canon | D-476 refined it to Session 58's corrected shape; AC-130.21's three tests prove it. Two-way. | — |
| D-491 | planning | What does a crop return? | autonomous | CROP_RESPONSE: 201 with item, source_id, requested, applied, clamped and the mark counts, and no image bytes | Local Canon | The agent learns what was cut and kept, and reads the pixels with `image` when it wants them. Two-way. | — |
| D-492 | planning | How does MCP expose crop? | autonomous | CROP_MCP: a strict avkit_capture member, a POST ACTION_INDEX row after revert, ADD_TIMEOUT_MS, not destructive, and an audit plan step | Local Canon | A crop changes no source, so it asks no confirm. Execution amended AC-67.19's order pin. Two-way. | — |
| D-493 | planning | How do the Pillow and renderer parity suites cover clipped marks? | autonomous | Four crop cases appended with REGION_SEED + 1, the fixture regenerated, the names added to the UI case lists | Local Canon | The existing cases' bytes stay the same; AC-90.8 checks the fixture reproduces. Two-way. | — |
| D-494 | planning | How is the crop description checked? | autonomous | AC-130.25 checks the markers now; a live agent run of the description is carried in Session 60's prompt | Local Canon | A live agent run needs a model and the network, which this session's rows don't allow. Session 60 builds the GUI on the same endpoint and is the next session to touch the tool. Two-way. | — |
| D-495 | planning | Which names does row 1 add? | autonomous | MarkCarry, the clip_mark stub, CropResult, the port's crop and an adapter crop that writes nothing | Local Canon | Session 53 RULE-2: every behaviour Red failed by assertion. Two-way. | — |
| D-496 | planning | Where do crop values go? | autonomous | NO_RAW_CONSOLE: no new log line; name sanitized before use; AC-130.22 proves it | Local Canon | A crop takes outside text in `name`, so Session 50 RULE-1 has a real target. Two-way. | — |
| D-497 | planning | What does the session gate run? | autonomous | Session 58's steps with crop as the runtime step; ui-electron, mcp-audit, build-record and the package build skipped with reasons | Local Canon | No renderer file changed, and the audit is a network run. Two-way. | — |
| D-498 | planning | When can this session run? | autonomous | After Session 58 closes and Session 57 is approved | Local Canon | Row 0's queue check passed: MEU-125, MEU-128 and MEU-129 approved, no Session 58 path dirty. Two-way. | — |
| D-499 | planning | How does the MCP audit baseline meet the new crop action? | human | A: BASELINE_PENDING = ['avkit_capture.crop'] in coverage.test.ts, AC-68.5 amended, and MCP-AUDIT-BASELINE-PENDING-CROP filed | Human-approved | The open caption block makes a baseline refresh impossible now. AC-130.28 proves AC-68.5 misses exactly the pending key. | USER_EXPLICIT 2026-11-09 'D-499 A' |
| D-506 | execution | Execution review round 1 F1: a CMYK JPEG's crop loses its ICC profile, and PNG can't hold CMYK or a CMYK profile. How does a crop treat a source in a mode PNG can't store? | human | A: a CMYK, YCbCr or LAB source with a profile that builds a transform converts through it to sRGB with ImageCms and carries the sRGB profile; with none, or one that builds no transform, it converts plainly and carries none | Human-approved | D-482 keeps the profile because stripping it shifts colours, and converting through the profile is how a colour-managed viewer shows the source. Dropping the profile would keep the shift; doing nothing would leave F1 open. Amends D-482, CROP_PIXELS and AC-130.10. Two-way. | USER_EXPLICIT 2026-11-09 'A: convert via profile (Recommended)' |
| D-507 | closeout | Session 59 found a pre-existing scan defect outside the crop: one inbox-root file the scan can't open breaks GET /captures, with a 422 naming its path or a 500. File it, or leave it as the handoff's observation? | human | File it: CAPTURE-SCAN-UNPROBEABLE-FILE-BREAKS-LIST, P2, open, linked to MEU-130 | Human-approved | Session 50's rule says a raw value that reaches an API message is fixed or raised, never left as a residual, and the defect predates this session and lies outside MEU-130's scope. Filing records the probe and its two failure shapes for a plan of its own. Leaving it as a handoff observation hides it from the register. Two-way. | USER_EXPLICIT 2026-11-10 'File it (Recommended)' |

---

## Pattern Extraction

### Patterns to KEEP
1. **A stop condition that names a precedent session's pattern** (S11). It caught the `.avkit-tmp` change at row 0, and one plan round fixed it before any code was written.
2. **A type-only row first** (Session 53 RULE-2). Every Red failed by assertion.
3. **Save, write, diff for every tool that rewrites a shared file** (Session 55 RULE-2). The status write's diff held only MEU-130's fields.
4. **An independent exact oracle in the review.** Codex's rational arrow oracle and its real-profile reproducer found two defects the chosen cases missed, and rerunning both after the fix gave the Green an outside check.
5. **A contract change goes to Mat, not into the fix.** F1's fix amended an approved AC, so D-506 went through the Human Decision Protocol, and round 2 checked the fix against the amended contract.

### Patterns to DROP
1. **A stop condition the baseline script checks by name only.** S11 would have passed row 0 by name; the brief found the change.

### Patterns to ADD
1. **Grep for order pins, not just counts, when a list gains a row** (RULE-1).
2. **Keep test ids short enough for red-check's header split** (RULE-2).
3. **A row that departs from an approved contract records it before the gate** (RULE-3).
4. **Exact arithmetic where a rule rounds a computed tie** (RULE-4).

### Calibration Adjustment
- **Estimated time:** a day, as Session 58's reflection put it, and Mat set 60M tokens and 6 rounds for the execution loop.
- **Actual time:**
  - Planning ran on 2026-11-08 and into 2026-11-09 through two plan rounds; row 0's S11 stop and plan round 3 came on 2026-11-09.
  - Execution's baseline receipt is from 2026-11-09 21:09 (UTC-5), the first Green from 21:29, the crop Green from 22:05, and the gate rerun ended before 22:23, when round 1 was dispatched.
  - The plan review cost 23,266,843 tokens over three rounds. The execution review cost 12,812,411 over two rounds (8,336,600 and 4,475,811), 21% of its budget.
  - Round 1 returned at 22:36. The first correction Red was at 22:38, the gate rerun ended at 23:22, and round 2 approved at 23:38.
- **Adjusted estimate for a one-MEU session with geometry and a write path:** a day, as planned. Budget 8.5M for the first execution round and 4.5M per recheck. A 60M execution budget was again about five times what the loop used; 25M would cover two rounds with room for a third.

---

## Next Session Design Rules

```
RULE-1: When a plan adds a row to an ordered list (ACTION_INDEX, an enum, an audit plan), it greps for tests that pin a neighbour's position, not only the tests that count rows, and lists each one it amends.
SOURCE: AC-67.19 pinned capture_interactive directly after revert, and AC-129.1 pinned Import as the last CaptureSource; the plan named neither, so rows 2 and 5 changed two test files the plan said were unchanged.
EXAMPLE: "ACTION_INDEX 70 -> 71 (action-index.test.ts:41)" -> "70 -> 71; order pins: runner-fake-backend.test.ts:185 (revert, then capture_interactive) becomes revert, crop, capture_interactive".
```

```
RULE-2: A test id, its parametrize ids included, stays short enough that pytest's failure header keeps at least three underscores on each side, so red-check.py splits each failure into its own block.
SOURCE: Row 2's first run counted 72 failures in 71 blocks, and row 4a's longest names did the same, until the ids were shortened (w0, h0, keeps_a_temp_file_it_did_not_write).
EXAMPLE: "test_ac_130_21_keeps_a_temporary_file_it_did_not_write[replace]" -> "test_ac_130_21_keeps_a_temp_file_it_did_not_write[replace]".
```

```
RULE-3: A row whose code departs from an approved contract (a mechanism id, an AC or a D-decision) records the departure and its reason in the handoff before the gate. If the departure changes what an AC asserts, it goes to Mat as a Decision Brief before the row closes.
SOURCE: Row 5 set icc = None for CMYK, YCbCr and LAB, against D-482 and AC-130.10, and recorded nothing. Review round 1's F1 found it, and the fix needed D-506.
EXAMPLE: "_CROP_ICC_DROP_MODES drops the profile" -> "Departure: PNG can't hold a CMYK profile, so D-482 can't hold for CMYK. Brief to Mat: convert through the profile, drop it and amend AC-130.10, or stop."
```

```
RULE-4: Geometry that rounds a computed point under a half-up rule computes it exactly (Fraction or integer cross-multiplication) when its inputs are integers, and its tests include a case whose exact answer is a half, in both directions.
SOURCE: _clip_arrow's float interpolation gave (8, 4) for an entry whose exact value is (8, 4.5), and the reversed arrow gave (8, 5). Codex's 20000-case rational oracle found it; AC-130.3's eleven chosen cases did not.
EXAMPLE: "t0 = max(t0, -p / q) as floats" -> "t0 = max(t0, Fraction(-p, q)); test_ac_130_3_arrow_half_tie_rounds_up[fwd] and [rev]".
```

---

## Next Day Outline

1. **Target:** done in the tree, not committed. MEU-130 is approved and MCP-AUDIT-BASELINE-PENDING-CROP is open. The commit waits on Mat's words.
2. **Next session:** Session 60 `gui-capture-crop-tool` (MEU-131), whose plan isn't written yet (grouping `:74`). It carries D-404 and D-494's live agent run of the `crop` description. Its prompt is `C:/Temp/av-kit/session-60-prompt.md`.
3. **Scaffold changes needed:** none.
4. **Patterns to bake in from today:** RULE-1 to RULE-4 here, plus the rules carried from Sessions 50 to 58.
5. **Codex validation scope:** Session 60's plan, then its execution.
6. **Time estimate:** a day. The canvas tool's drag and its keyboard path are the largest pieces.

---

## Efficiency Metrics

| Metric | Value |
|--------|-------|
| Total tool calls | About 930 in this conversation's transcript at H2-2, from plan round 3 on |
| Time to first green test | The mark-carry Green at 2026-11-09 21:29 (UTC-5), after its Red at 21:28 (`s59-py-red-carry.txt`, `s59-py-green-carry.txt`) |
| Tests added | pytest 1448 → 1564 (+116, all for AC-130, 5 of them from the round 1 corrections); MCP 479 → 485 (+6); Vitest 1192 → 1193 (+1); crop module 23 of 23 |
| Codex findings | Plan review: R1 `changes_required` with one High blocking finding and five Medium (12,513,669); R2 approved (7,047,382); R3 approved after D-476 (3,705,792). Execution review: R1 `changes_required` with F1 High blocking and F2 Medium (8,336,600); R2 approved, both fixed, `intent_achieved: yes` (4,475,811; 12,812,411 of 60,000,000) |
| Handoff Score (X/7) | 6/7. Every AC has evidence and the gate passed on each run. Row 5's ICC departure wasn't recorded until review round 1 found it (F1) |
| Rule Adherence (%) | 85 (17 of 20 triggered rules followed in full, 3 in part) |
| Prompt→commit time | Planned 2026-11-08 and executed 2026-11-09; not committed, waiting on Mat |

### Rules Sampled for Adherence Check

| Rule | Source | Followed? |
|------|--------|-----------|
| Tests before production code; Red before Green | AGENTS.md §Testing & TDD | Yes. Every row Red failed by assertion before the code changed |
| Independent review; no self-approval | AGENTS.md §Dual-Agent Workflow | Yes. The canonical reviews are Codex's reports, validated under `C:/Temp/av-kit` and copied byte for byte |
| A raw value that can reach a log, stdout or the Console is fixed in the row or raised | Session 50 rule; the brief | Yes for the crop: AC-130.22 proves no marker reaches the ring, stdout, stderr or `console.log`. The scan's pre-existing path message was raised with Mat at closeout and filed as `CAPTURE-SCAN-UNPROBEABLE-FILE-BREAKS-LIST` (D-507) |
| tested_state prompts name the user git ignore and `.claude/settings.local.json` | Session 51 RULE-4 | Yes |
| Each row re-reads its lines; moved cites corrected in the handoff | Session 51 RULE-3 | Yes. Row 0 recorded every anchor in `s59-anchors.txt`; the handoff corrects `registry.ts`, `capture.registered` and `capture.wrote` |
| A loop's budget is compared with the last comparable round | Session 52 RULE-3; Session 58 RULE-4 | Yes. Mat set 60M with Session 58's 11.7M in front of them |
| Shared missing names go in a type-only row first | Session 53 RULE-2 | Yes. Row 1 (D-495) |
| A row editing core runs test_domain | Session 54 RULE-1 | Yes. Rows 1, 2, 3 and 5 |
| A real-stack marker test with a positive control | Session 54 RULE-2 | Yes. AC-130.22 through `build_services` with HealthService reset first |
| Handoff checks before the review prompt; every cited AC has a row | Session 54 RULE-3 | Yes. H1-6 refused for AC-16 and AC-90, and passed once their rows were added |
| A cited authorization is checked with grep | Session 54 RULE-4 | Yes. "D-499 A" at `human-gate-decision.md:7` |
| List and run the callers of a shared function or list the plan extends | Session 55 RULE-1 | Partly. Every reader of `CaptureSource`, `ACTION_INDEX` and the baseline ran, but two order pins weren't in the plan's list (RULE-1) |
| Diff a shared file's bytes after a tool rewrites it | Session 55 RULE-2 | Yes |
| UTF-8 output for every Python probe | Session 55 RULE-5 | Yes |
| Exclusive temporary file; a name whose temporary file exists is taken | Session 58 RULE-1 | Yes. D-476 and AC-130.21's four keeps-a-temporary-file cases |
| Every filesystem call on an outside path inside the mapping | Session 58 RULE-2 | Yes. The adapter's `crop` catches `Exception` on open and decode, and AC-130.21's damaged-PNG case passes |
| Every command through RTK | AGENTS.md §RTK | Partly. Tests, gates, tools and dispatches went through `rtk proxy`; many reads did not, and the RTK hook isn't installed on this PC |
| No branches or worktrees; never commit or push without the human | AGENTS.md §Commits | Yes. The work is on `main`, and nothing from this session is committed |
| Preserve line endings | memory; the AC-51.6 byte hash | Yes. Row 0 recorded each file's endings; the parity fixture stays CRLF in the working copy and LF in git |
| Check every AC against current file:line and probe its contract before handoff | AGENTS.md §Pre-Handoff Self-Review | Partly. AC-130.10 was checked on its RGB PNG case only, and row 5's CMYK profile drop reached review (F1) |

---

## Instruction Coverage

```yaml
schema: v1
session:
  id: "f5326ab5-7f53-4338-833a-7f4451f87318"
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
  workflows: [plan_critical_review, execution_session, execution_critical_review]
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
note: "An agent cuts any region of a shot into a new PNG shot, with the source's marks clipped onto it, and the source never changes."
slim_candidate: ["The handoff's cross-reference AC rows for earlier MEUs exist only for the AC check."]
overthinking_observed: false
review_churn:
  rounds_to_approval: {plan: 2, execution: 2}
  findings_per_round:
    - {review: plan, round: 1, critical: 0, high: 1, medium: 5, low: 0}
    - {review: plan, round: 2, critical: 0, high: 0, medium: 0, low: 0}
    - {review: plan, round: 3, critical: 0, high: 0, medium: 0, low: 0}
    - {review: execution, round: 1, critical: 0, high: 1, medium: 1, low: 0}
    - {review: execution, round: 2, critical: 0, high: 0, medium: 0, low: 0}
  churned_findings: 0
  finding_categories: {boundary_validation: 3, weak_test: 3, contract_drift: 2}
  verdicts: {changes_required: 2, approved: 3}
meu_work_classes: [correctness]
```
