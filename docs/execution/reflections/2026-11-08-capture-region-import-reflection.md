---
date: "2026-11-08"
project: "capture-region-import"
meus: ["MEU-128", "MEU-129"]
plan_source: "docs/execution/plans/2026-11-08-capture-region-import/implementation-plan.md"
template_version: "2.0"
---

# 2026-11-08 Meta-Reflection

> **Date**: 2026-11-08 (planned), executed 2026-11-09
> **MEU(s) Completed**: MEU-128 `capture-region-view` and MEU-129 `capture-image-import`, the first two slices of the crop design Mat asked for (design D-1, grouping D-400). Session 58 files CAPTURE-EXIF-SCANNED-ORIENTATION (D-424) for the scan and register paths that the import's upright copy doesn't cover
> **Plan Source**: `docs/execution/plans/2026-11-08-capture-region-import/implementation-plan.md`

---

## Execution Trace

### Friction Log

1. **What took longer than expected?**
   - **The plan review took three rounds and 19,334,552 tokens.**
     - Round 1 (5,717,501 tokens) returned `changes_required` with three findings:
       - F1, High and blocking: a truncated JPEG passed `verify()`, and `probe` then refused it with the path in its message after the copy was published.
       - F2, Medium: `x + width` overflowed for 1e308.
       - F3, Medium: D-425's 15 MiB option promised whole-image readback that an upright PNG could exceed.
     - Round 2 (10,436,779 tokens) approved, but the approval couldn't pass the approved-state gate. The coordinator's recheck prompt had prescribed a layout with no `New Findings` table, and the parser counts a recheck section without one as one open finding.
     - Round 3 (3,180,272 tokens) approved again with the table in place.
     - Mat tripled the plan budget and added two rounds before the D-425 and D-426 briefs.
   - **Execution waited a day on Sessions 56 and 57.** Mat ruled to "push and wait we will complete 56 and 57 first", and execution began after rc.2's e0c1d0b landed.
   - **The execution review needed a second round.** Round 1 (7,847,133 tokens) found F1 and F2, both High and blocking. Round 2 (3,872,291 tokens) closed both as `fixed`, with no new finding.

2. **What instructions were ambiguous?**
   - **The commit trailer.** The harness asks for a Co-Authored-By trailer. Task H2-5 and Mat's standing rule say there is none. The draft has none.
   - **Where a review's corrections section may hold a table.** The closeout parser reads round 1 as the text up to the first `## Recheck` heading. A findings-like table in `## Corrections Applied` would therefore be read as round-1 findings. The corrections section uses bullets for that reason (RULE-3).

3. **What instructions were unnecessary?**
   - H2-1's `view_file` row, again. H2-2's check validates the reflection against the same template and schema.

4. **What was missing?**
   - **A rule that a write path which cleans up on failure must own what it cleans up.** D-418 specified "remove the temporary file" without saying the call must have created it. `_import_dest` didn't count a leftover `NAME.avkit-tmp` as taken, so a failed first write deleted another writer's file (execution F1, RULE-1).
   - **A sweep of every filesystem call on an outside path, not just the read.** The plan mapped the `OSError` from `read_bytes`. `exists`, `is_file`, `stat` and `resolve` ran outside that `try`, so a denied folder returned 500 with the path in the Console (execution F2, RULE-2).
   - **Carrying a plan-time exception finding to every call site of the same library call.** The plan's corrections receipt (`s58-corrections-verify2.txt`) showed that a damaged PNG IDAT raises `SyntaxError`, and `inspect_import` catches `Exception` for that reason. The new `view` still caught only `UnidentifiedImageError` and `OSError` (execution F2, RULE-2).

5. **What did you do that wasn't in the prompt?**
   - **Mapped `_variant_path`'s `is_file`** through a new `_is_file` that reads a denied lookup as missing. It was found by the sibling sweep after F2, outside the finding's own lines, and disclosed in the corrections section.
   - **Left `read_image`'s unguarded `read_bytes` unchanged and said so.** It predates this session, and RETURN_UNCHANGED requires that a request without the new fields behaves as today. The round-2 reviewer accepted it within scope.
   - **Corrected the handoffs' source anchors that the corrections moved, and their stale "31 changed paths".** Round 2 noted both as not findings.
   - **Saved copies of `meu-status.yaml`, `meu-registry.md` and `BUILD_PLAN.md` before H2-2's status write** (Session 55 RULE-2). The diff afterwards showed only MEU-128's and MEU-129's records and the P2 totals.

### Quality Signal Log

6. **Which tests caught real bugs?**
   - **The row Reds all failed by assertion.** MEU-128's Python Red failed 28 of 29, and its MCP Red failed 6. MEU-129's Python Red failed 29 of 30, and its MCP Red failed 2. `red-check.py` reported 0 problems on each receipt.
   - **The 11 correction Reds reproduced each review defect before the fix** (`s58-fix-r1-red.txt`):
     - `shot.png` was chosen over `shot_2.png`;
     - the race returned 201 over the other writer's file;
     - the other writer's file was deleted after a replace or commit failure;
     - each of the five import faults returned 500, not 422;
     - the broken-chunk view raised `SyntaxError`;
     - the second read raised the path-bearing `PermissionError`.
   - **AC-129.11 through the real `build_services`** proves no marker reaches the ring, stdout, stderr or `console.log`. The new metadata cases assert the same for their marker.

7. **Which tests were trivially obvious?**
   - AC-128.24, MCP `image` with no region keeps today's one-item shape. It pins behaviour that already held, which is its purpose (D-412).

8. **Did pyright/ruff catch anything meaningful?**
   - pyright refused `Image.LANCZOS` in row 3, and the code took the file's existing `Image.Resampling.LANCZOS`. That was a spelling, not a defect. `ruff format --check` lists 23 files that predate this work, and the gate runs `ruff check`, not the formatter.

### Workflow Signal Log

9. **Was the FIC useful as written?**
   - Yes. The 17 mechanism ids let the Reds, both handoffs, all five review prompts and the corrections section name the same contract. Both review rounds cited findings by those ids.

10. **Was the handoff template right-sized?**
    - Yes for two MEUs sharing one gate. The cross-reference AC rows remain filler for the AC check (`slim_candidate`).

11. **How many tool calls did this session take?**
    - About 1,870 in this conversation's transcript at H2-2. That count also covers Session 59's plan, the Session 56 tracking update and two pushes, which ran in the same conversation.

12. **Which rows were delegated, to which subagent (harness + model), and did any delegated result need rework?**
    - None. The coordinator ran every row. Codex reviewed the plan and the execution as the independent reviewer, which isn't delegation.

### Decisions Log

| ID | Stage | Question | Resolution | Chosen | Source tag | Reasoning (why this; why the alternatives lost) | Human ref |
|----|-------|----------|------------|--------|------------|--------------------------------------------------|-----------|
| D-400 | grouping | Adopt the crop design's slices as registered MEUs and plan the first session? | human | Yes: MEU-128 to MEU-132, Session 58 planned now | Human-approved | Mat asked for the grouping and the first plan after ruling design D-1. This session executed the first two slices. | USER_EXPLICIT 2026-11-08 "create new session grouping and start the first create plan from it" |
| D-401 | grouping | Slice to MEU mapping | autonomous | One MEU per slice; MEU-130 depends on MEU-128 | Local Canon | The crop and the region view must resolve a box the same way. D-407 put REGION_RESOLVE in the domain so MEU-130 reuses it. Two-way. | — |
| D-402 | grouping | Which slices share Session 58? | autonomous | S1 and S3 (MEU-128, MEU-129) | Local Canon | They edit the same route, schema, MCP tool, registry and OpenAPI files. One gate and one OpenAPI regeneration served both. Two-way. | — |
| D-403 | grouping | Build-plan home and band | autonomous | 09 §Residuals registered 2026-11-08, matrix rows 9.35 to 9.39, band P2 | Local Canon | Earlier capture residuals live the same way in 09. Rows 9.35 and 9.36 now read approved. Two-way. | — |
| D-404 | grouping | Where does MEU-131's C key come from? | autonomous | A page-scoped shortcut registry entry; else C arrives with MEU-105 and the button ships alone | Local Canon | Tool letters belong to MEU-105. Not touched in this session. Two-way. | — |
| D-405 | grouping | Where do the crop sessions sit in the queue? | autonomous | Sessions 58 to 61, after rc.2's Session 57 | Local Canon; Research-backed | Crop is new capability, not a release fix. Execution began after e0c1d0b landed, as Mat confirmed. Two-way. | — |
| D-406 | grouping | How do crop and the pending mark types meet? | autonomous | MEU-130 clips every mark type on main when it executes; a later mark type adds its own crop rule | Local Canon | The two groups share no renderer file before Session 60. Not touched in this session. Two-way. | — |
| D-407 | planning | Where does the region contract live, and what does each bad region return? | autonomous | REGION_RESOLVE and REGION_ERRORS: pure functions in domain/capture.py raising ValidationError with fixed messages in a fixed order; unit defaults to px | Research-backed | MEU-130's crop needs the same rules, and the domain already holds CAPTURE_MIN_EDGE_PX. FastAPI bounds would swap the messages for Pydantic's. Two-way. | — |
| D-408 | planning | How are fractions rounded near a whole pixel? | autonomous | Round each product to 9 places before floor or ceil | Local Canon | Without it 0.1 plus 0.2 of 1000 gives 301. Nine places moves a product by at most 5e-10. Decimal arithmetic lost: no gain for JSON floats. Two-way. | — |
| D-409 | planning | How is a view scaled and resampled? | autonomous | VIEW_SCALE: a region fits max_edge, upscaled at most 4x; max_edge alone only shrinks; Lanczos | Research-backed | It keeps the detail a model keeps at a cost the caller picks, and the cap stops blur posing as detail. Two-way. | — |
| D-410 | planning | What does the adapter return for a view, and what if the file changed? | autonomous | VIEW_FORMAT and RETURN_UNCHANGED: keep the format, return the file's bytes for a whole frame at scale 1, refuse a size mismatch with ConflictError | Local Canon | Keeping the format keeps a JPEG small and the media type right. Execution F2 extended the refusal to every decode and read fault. Two-way. | — |
| D-411 | planning | How does the API report the frame? | autonomous | FRAME_HEADERS: five X-Capture headers on every 200, documented in the route's responses | Local Canon | Headers keep the body an image, so every client keeps working. Two-way. | — |
| D-412 | planning | How does MCP give the agent the frame? | autonomous | FRAME_ITEM: a JSON text item before the image when all five headers parse, else the image alone | Research-backed | An agent can't read headers through MCP. Requiring all five keeps older shapes unchanged, so no existing test changed. Two-way. | — |
| D-413 | planning | How are the new query keys kept off POST rows? | autonomous | QUERY_GET_ONLY: withQuery runs only for GET rows | Local Canon | POST capture region would otherwise send x, y, width and height in the query too. AC-128.19 pins it. Two-way. | — |
| D-414 | planning | Does the Import source need a wire map entry or a migration? | autonomous | IMPORT_SOURCE: CaptureSource.Import by name; no wire entry, no migration | Local Canon | Import doesn't use register's lowercase wire values, and the column is a string. Two-way. | — |
| D-415 | planning | What is the import request's shape? | autonomous | IMPORT_MODE: POST /captures mode import with path, and MCP capture mode import | Local Canon | MCP capture already maps POST /captures by mode, so the action index stays at 70 rows. Two-way. | — |
| D-416 | planning | In what order is an import path checked, and what do refusals say? | autonomous | IMPORT_ACCEPT: absolute, exists, regular file, suffix, size, annotated copy, read, inspect; fixed messages; 422 | Research-backed | Cheap checks first, fixed messages keep the path out. Execution F2 put every check after the absolute test inside one OSError mapping. Two-way. | — |
| D-417 | planning | How is an import's content checked and turned upright? | autonomous | inspect_import: bomb warnings as errors, a pixel limit, verify, a full load, then EXIF orientation; write_upright_png | Research-backed | Verify alone passes a truncated JPEG (plan review F1). An upright copy saves every later reader a rotation. Two-way. | — |
| D-418 | planning | How is the copy written so a failure leaves no half state? | autonomous | IMPORT_COPY: under CAPTURE_FILE_LOCK write NAME.avkit-tmp, replace, probe, register; on failure remove what this call wrote and raise a fixed 503 | Local Canon | The lock keeps a scan and a second import out. Execution F1 made the temporary file exclusive, so the cleanup removes only what this call created. Two-way. | — |
| D-419 | planning | What does importing a file already in the inbox root do? | autonomous | IMPORT_IN_PLACE: return the existing row with its source kept; register an Import row when none exists; never copy | Local Canon | The call stays idempotent and the inbox gains no duplicates. Two-way. | — |
| D-420 | planning | How is the copy named? | autonomous | IMPORT_NAME: the sanitized stem, then _2, _3 against files and rows | Local Canon | A person finds the shot by its old name. Execution F1 added names whose temporary file exists. Two-way. | — |
| D-421 | planning | Where are the new values written, and does the Console see them? | autonomous | Where values go: no new log line; refusals hold no path; AC-129.11 proves it through build_services | Local Canon | Import takes outside text, so Session 50 RULE-1 has a real target. Execution F2 found the gap the rule names, and the fix closed it. | — |
| D-422 | planning | In what order do the rows add the shared names? | autonomous | Row 1 adds the region constants, ViewFrame and the stubs; rows 2 and 4 fail by assertion | Local Canon | Session 53 RULE-2. Every Red failed by assertion. Two-way. | — |
| D-423 | planning | Which checks does the session gate run? | autonomous | Session 55's shape; the region-import module, then the capture inbox E2E; no package build | Local Canon | The inbox page reads the image route and the source value, so one targeted E2E proves the built app. Two-way. | — |
| D-424 | planning | Scanned and registered files keep their EXIF frame. Fix, file or leave? | autonomous | File CAPTURE-EXIF-SCANNED-ORIENTATION, linked to MEU-129; fix only the import path here | Local Canon | Changing the scan path rewrites stored frames no AC covers. Leaving it unrecorded hides a defect the plan found. Two-way. | — |
| D-425 | planning | What is the import size cap? | human | IMPORT_MAX_BYTES 50,000,000, as recommended | Human-approved | 50 MB takes any phone photo or 8K screenshot. 15 MiB refuses large photos a region view could serve, and doing nothing lets a 400 MB file into memory. Two-way: one constant. | USER_EXPLICIT 2026-11-08 'all recommendations accepted' |
| D-426 | planning | Are the view defaults 1568, 64 to 2576 and 4x right? | human | As the design has them: max_edge 1568 by default, 64 to 2576, at most 4x | Human-approved | 1568 is a cost choice under the 2576 px models keep, and an agent passes 2576 for more. Doing nothing returns a 30 by 20 region at 30 by 20. Two-way: four constants. | USER_EXPLICIT 2026-11-08 'all recommendations accepted' |
| D-427 | planning | Are the crop docs committed before execution? | human | Yes: one exact-scope docs commit of Stage A's seven files, without a push; committed as 75617379, pushed separately on Mat's direction | Human-approved | It gave row 0 a clean baseline and kept the session commit to this session's work. Doing nothing still worked but mixed registration with code. | USER_EXPLICIT 2026-11-08 'all recommendations accepted' |

---

## Pattern Extraction

### Patterns to KEEP
1. **Mechanism ids across the plan, the Reds, the handoffs and every review prompt.** Both execution rounds and the corrections section cited the same 17 ids.
2. **Red-first corrections.** The 11 correction cases failed on the defects the review named before any product line changed. The round-2 reviewer matched each Red diagnostic to the current assertions.
3. **A sibling sweep after each finding, written into the corrections section with what was left and why.** It found `_variant_path` and recorded `read_image` as out of scope. The reviewer accepted both.
4. **Save, write, diff for every tool that rewrites a shared file** (Session 55 RULE-2). The status write's diff held only this session's lines.

### Patterns to DROP
1. **A recheck prompt that prescribes a layout without checking it against the validator.** Plan round 2's approval needed a third round only because the layout had no `New Findings` table.

### Patterns to ADD
1. **Exclusive creation for any temporary file a failure path removes** (RULE-1).
2. **Map every filesystem call on an outside path, and carry a plan-time exception finding to every call site of that library call** (RULE-2).
3. **Corrections sections in bullets, never a table** (RULE-3).
4. **Budget a recheck round at about half the first round** (RULE-4).

### Calibration Adjustment
- **Estimated time:** the plan put Session 58 at a day, and Mat set 60M tokens and 6 rounds for the execution loop.
- **Actual time:**
  - Planning ran 2026-11-08T13:22Z to 18:02Z, through three plan review rounds.
  - Execution ran from Mat's "proceed with execution" at 2026-11-09T16:24Z. The baseline receipt is from 17:07Z, the first Green from 17:17Z and the first full gate around 17:30Z. Round 2's approval came at 18:13Z.
  - The plan review cost 19,334,552 tokens over three rounds. The execution review cost 11,719,424 over two rounds, which is 20% of its budget.
- **Adjusted estimate for a two-MEU session that takes outside files:** a day, as planned. Budget 8M for the first execution round and 4M per recheck. A 60M execution budget was about five times what the loop used.

---

## Next Session Design Rules

```
RULE-1: A plan step that writes a temporary file and removes it on failure creates it exclusively (open "xb"), counts a name whose temporary file exists as taken, and has a test that leaves another writer's temporary file in place and checks its bytes survive.
SOURCE: Execution F1 (High): _import_dest ignored NAME.avkit-tmp, write_bytes truncated it, and the except branch unlinked it; four cases in test_ac_129_9_keeps_a_temporary_file_it_did_not_write now cover none, race, replace and commit.
EXAMPLE: "on failure, remove the temporary file" → "create NAME.avkit-tmp with open('xb'); tmp is set only after that open succeeds; on failure remove tmp only if this call set it".
```

```
RULE-2: When a path comes from outside, the plan puts every filesystem call on it (exists, is_file, stat, resolve, open, read) inside the error mapping, and any exception class found at plan time for one call site of a library function is carried to every other call site of it.
SOURCE: Execution F2 (High): exists, is_file, stat and resolve ran outside the read's try, and view caught only UnidentifiedImageError and OSError although the plan's own receipt showed a damaged IDAT raises SyntaxError.
EXAMPLE: "map read_bytes's OSError to 422" → "map OSError from the whole check-and-read sequence; grep every Image.open in the delta and give each the catch inspect_import has".
```

```
RULE-3: An author's Corrections Applied section in a review file uses bullets, with no table, and every Recheck section the reviewer writes carries its own New Findings table.
SOURCE: The closeout parser reads round 1 as the text up to the first Recheck heading and counts a recheck section without a findings table as one open finding; plan round 2's approval needed a third round for that reason.
EXAMPLE: "| F1 | Confirmed | ... |" in Corrections → "- **F1 confirmed.** ..."; recheck prompt → "a ### New Findings table, empty if none".
```

```
RULE-4: An execution loop's brief budgets a recheck round at about half its first round and compares the whole budget with the last loop of the same shape.
SOURCE: Session 58's execution round 1 cost 7,847,133 and its recheck 3,872,291; the 60M budget was about five times the 11.7M used.
EXAMPLE: "60M, 6 rounds" → "first round 8M, each recheck 4M; 24M covers four rounds".
```

---

## Next Day Outline

1. **Target:** done in the tree, not committed. MEU-128 and MEU-129 are approved and CAPTURE-EXIF-SCANNED-ORIENTATION is open. The commit waits on Mat's words, and Session 57's e0c1d0b is still unpushed.
2. **Next session:** Session 59 `capture-crop-copy` (MEU-130), whose plan Mat approved (D-499 A). It runs only on Mat's words. Its prompt is `C:/Temp/av-kit/session-59-prompt.md`.
3. **Scaffold changes needed:** none.
4. **Patterns to bake in from today:** RULE-1 to RULE-4 here, plus the rules carried from Sessions 50 to 55. MEU-130 writes a new file from a crop, so RULE-1 and RULE-2 apply directly.
5. **Codex validation scope:** Session 59's execution.
6. **Time estimate:** a day. The mark carry is the batch's largest piece.

---

## Efficiency Metrics

| Metric | Value |
|--------|-------|
| Total tool calls | About 1,870 in this conversation's transcript at H2-2, including Session 59's planning |
| Time to first green test | Python Green for MEU-128 at 2026-11-09T17:17Z after its Red at 17:10Z (`s58-py-red-128.txt`, `s58-py-green-128.txt`) |
| Tests added | pytest 1357 → 1427 (+70: 31 for AC-128, 39 for AC-129, 11 of them for review round 1); MCP 470 → 479 (+9); Vitest 1183 → 1183; region-import module 45 of 45; Electron capture inbox 43 of 43 |
| Codex findings | Plan review: R1 `changes_required` with F1 High blocking and F2 and F3 Medium (5,717,501); R2 approved (10,436,779); R3 approved (3,180,272). Execution review: R1 `changes_required` with F1 and F2 High blocking (7,847,133); R2 approved, both fixed, `intent_achieved: yes` (3,872,291 of 60,000,000) |
| Handoff Score (X/7) | 6/7. Every AC has evidence and the gate passed on each run. Two source anchors and one count went stale after the corrections and were fixed after round 2 noted them |
| Rule Adherence (%) | 89 (16 of 18 triggered rules followed in full, 2 in part) |
| Prompt→commit time | Planned 2026-11-08 and executed 2026-11-09; not committed, waiting on Mat |

### Rules Sampled for Adherence Check

| Rule | Source | Followed? |
|------|--------|-----------|
| Tests before production code; Red before Green | AGENTS.md §Testing & TDD | Yes. Every row Red and all 11 correction Reds failed by assertion before the code changed |
| Independent review; no self-approval | AGENTS.md §Dual-Agent Workflow | Yes. Both canonical reviews are Codex's reports, validated under `C:/Temp/av-kit` and copied byte for byte; the author set only `corrections_applied` |
| A raw value that can reach a log, stdout or the Console is fixed in the row or raised | Session 50 rule; the brief | Partly. D-421 stated where values go and AC-129.11 proved it, but the metadata lookups outside the read's try leaked a path until execution F2 |
| tested_state prompts name the user git ignore and `.claude/settings.local.json` | Session 51 RULE-4 | Yes. Both execution prompts name them |
| The recheck prompt gives the literal Prior Pass Summary table | Session 52 RULE-1 | Yes. Execution round 2's prompt gave it, with bare-word cells |
| A loop's budget is compared with the last comparable round | Session 52 RULE-3 | Yes. Mat set 60M with the comparison in front of them |
| Shared missing names go in a type-only row first | Session 53 RULE-2 | Yes. Row 1 (D-422) |
| A recheck prompt names prior findings by the review's own ids | Session 53 RULE-3 | Yes. F1 and F2 |
| A row editing core runs test_domain | Session 54 RULE-1 | Yes. Rows 1, 2 and 5 ran `tests/unit/test_domain.py` |
| A real-stack marker test with a positive control | Session 54 RULE-2 | Yes. AC-129.11 through `build_services` |
| Handoff checks before the review prompt; every cited AC has a row | Session 54 RULE-3 | Yes. H1-6, H1-6a and H1-6b passed before each dispatch |
| A cited authorization is checked with grep | Session 54 RULE-4 | Yes. Mat's rulings are quoted where they stand in the plan's Coordinator Record |
| The decision probe names the plan; decision_log slots are words | Session 54 RULE-5 | Yes |
| List and run the callers of a shared function the plan extends | Session 55 RULE-1 | Yes. `read_image`'s variant checks moved into `_variant_path`, and its existing tests ran in row 3 |
| Diff a shared file's bytes after a tool rewrites it | Session 55 RULE-2 | Yes. The H2-2 status write |
| UTF-8 output for every Python probe | Session 55 RULE-5 | Yes |
| Every command through RTK | AGENTS.md §RTK | Partly. Tests, gates, tools and dispatches went through `rtk proxy`; many reads did not, and the RTK hook isn't installed on this PC |
| No branches or worktrees; never commit or push without the human | AGENTS.md §Commits | Yes. The work is on `main`, and nothing from this session is committed |
| Preserve line endings | memory; the AC-51.6 byte hash | Yes. The service, adapter and adapter test stay CRLF; the new module is LF; the round-2 reviewer counted them |

---

## Instruction Coverage

```yaml
schema: v1
session:
  id: "587c3a88-e5a3-4425-acee-849c15ed8922"
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
note: "An agent views any region of a shot at a size it picks with the frame reported, and imports any local image as a new upright shot without touching the source."
slim_candidate: ["The handoff's cross-reference AC rows for earlier MEUs exist only for the AC check."]
overthinking_observed: false
review_churn:
  rounds_to_approval: {plan: 3, execution: 2}
  findings_per_round:
    - {review: plan, round: 1, critical: 0, high: 1, medium: 2, low: 0}
    - {review: plan, round: 2, critical: 0, high: 0, medium: 0, low: 0}
    - {review: plan, round: 3, critical: 0, high: 0, medium: 0, low: 0}
    - {review: execution, round: 1, critical: 0, high: 2, medium: 0, low: 0}
    - {review: execution, round: 2, critical: 0, high: 0, medium: 0, low: 0}
  churned_findings: 0
  finding_categories: {boundary_validation: 3, claim_to_state_drift: 1, fix_generalization_miss: 1}
  verdicts: {changes_required: 2, approved: 3}
meu_work_classes: [correctness, correctness]
```
