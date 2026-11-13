---
date: "2026-11-13"
project: "capture-copy-image"
meus: ["MEU-104"]
plan_source: "docs/execution/plans/2026-11-13-capture-copy-image/implementation-plan.md"
template_version: "2.0"
---

# 2026-11-13 Meta-Reflection

> **Date**: 2026-11-13 (planned, reviewed, executed and closed on the same day)
> **MEU(s) Completed**: MEU-104 `capture-copy-image-actions`, Session 69 `capture-copy-image`, P2, the second of the five capture annotation editor sessions (grouping row 45, D-674).
>
> **MEU-104:**
> - A new REST-only route, `POST /api/v1/captures/{id}/render`, takes the annotate body and returns the shot baked with those marks as PNG bytes. It writes no file, sidecar or row (RENDER_PORT, RENDER_BAKE, RENDER_SERVICE, RENDER_ROUTE, D-689, D-691, D-695).
> - The adapter's bake body moved into `_bake_canvas`, which bake and render share, so Copy image can't drift from Save (D-689).
> - A Copy image button after Save annotations, and canvas Ctrl+C, post the current marks, saved or not, through `postAuthorizedBlob` to render and write the PNG with `writeClipboardImage`. A text field and a non-empty selection keep native copy (COPY_BUTTON, COPY_KEY, RENDER_CLIENT, D-690, D-692, D-696, D-678).
> - The filmstrip's Copy image takes the annotated variant when the shot has saved marks (FILMSTRIP_AS_SHOWN, D-677 A).
> - The shot actions read Save annotations, Flatten into image… and Restore backup…, and a dirty Flatten offers Save and flatten, which saves before it flattens (ACTION_LABELS, SAVE_AND_FLATTEN, D-693, D-694). The help body names all of it (COPY_HELP).
>
> **Plan Source**: `docs/execution/plans/2026-11-13-capture-copy-image/implementation-plan.md`

---

## Execution Trace

### Friction Log

1. **What took longer than expected?**
   - **Two ACs that could not pass as written.** Each went to Mat as a Decision Brief (Session 59 RULE-3):
     - AC-104.7 listed control characters in a text mark among the 422 cases. annotate accepts them with 200 at `b3f3933` (`s69/probe-text.txt`), so the test could not hold its own parity rule. Mat ruled "Parity (Recommended)" (D-699). RULE-1 adds the missing check.
     - AC-104.8 put render right after annotate in the committed OpenAPI snapshot. `tools/export_openapi.py` writes it with `sort_keys=True`, so crop, export, flatten and image sit between them. Row 3's first pytest run failed on it. Mat ruled "Live + index (Recommended)" (D-700). RULE-2 adds the missing check.
   - **Two Red test-data errors that row 3 corrected** (handoff §Departures 4 and 6). Neither changed an assertion or source:
     - `VALIDATION` in `test_api_capture_render.py` lacked `"details": None`, which every sibling 422 test carries, so AC-104.7's four 422 cases failed in Green on the expected envelope alone (`s69/row3-py-try1.txt`, `5 failed, 123 passed`). RULE-3 adds the missing check.
     - AC-104.16 named `features/capture/settings-schemas.ts`; the file is `features/settings/settings-schemas.ts`. RULE-4 adds the missing check.
   - **The base Electron run** gave `1 failed`, `45 passed`: AC-81.11 `F2 held by another process`, twice (`s69-base-e2e.txt`, `s69-base-e2e-rerun.txt`). ShareX held F2, as in MEU-93 D-120. It was not running by row 3, and the gate's Electron run passed 47.
   - **Five pins missing from the plan's table** (handoff §Departures 1): `REVERT_DIRTY_TITLE`, two convert-status literals, AC-81.9's `ACTION_IDS` and `WAVE9_EXTRA_TESTIDS`. Row 1's literal sweep (Session 68 RULE-2) found them before the Red, so none surfaced as a Green failure.

2. **What instructions were ambiguous?**
   - **"Save and flatten" in 09's Labels row.** It names a confirm, which can only open if Flatten is enabled while dirty. D-693 read it that way and moved the MEU-67 and MEU-81 dirty-disabled pins (§Departures 2); the dirty confirm's lead sentence was left to execution (§Departures 3).
   - **The commit trailer.** The harness asks for a Co-Authored-By trailer. Task H2-5, `.agent/docs/development-lifecycle.md:454` and Mat's standing rule say there is none, so the commit draft has none.

3. **What instructions were unnecessary?**
   - H2-1's `view_file` row, as in Sessions 59 to 68. H2-2's check validates the reflection against the same template and schema.
   - The handoff's cross-family AC rows. They exist only so the handoff check accepts the AC table.

4. **What was missing?**
   - **A plan-time probe of the existing route an AC claims parity with** (RULE-1).
   - **A plan-time check of how a generated file orders the entry an AC pins** (RULE-2).
   - **Expected error envelopes copied from a sibling test's constant** (RULE-3).
   - **A Red-time check that every source path a test reads exists** (RULE-4).

5. **What did you do that wasn't in the prompt?**
   - **Wrote `s69/decision-probe-closeout.py`** from Session 68's. It found the same 15 decisions as the rerun plan-time probe, D-689 to D-700 and D-158 to D-160, and every source's SHA-256 was unchanged (`s69-closeout-decision-probe.txt`, `s69-plan-decision-probe.txt`; the plan-time copy is `s69/plan-decision-probe-plantime.txt`). Grouping §8 still ends at D-160 and §9.8 at D-678, so D-674, D-675, D-677 and D-678 are carried by hand.
   - **Set MEU-104 to `approved` by a counted byte replacement** (`s69/approve-104.py`), with the three status files copied first to `s69/pre-approve/`. The diff (`s69/approve-diff.txt`) holds only MEU-104's status lines, its registry row and BUILD_PLAN's counts.
   - **Probed annotate's text acceptance** (`s69/probe-text.py`) to ground the D-699 brief.

### Quality Signal Log

6. **Which tests caught real bugs?**
   - **Every Red failed by assertion** (Session 62 RULE-3): pytest `21 failed, 1 passed in 11.04s` (`s69-py-red.txt`), Vitest `17 failed | 2 passed (19)` (`s69-ui-red.txt`) and Electron `1 failed` (`s69-e2e-red.txt`). red-check reported `red-check: 3 receipt(s), 19 required test(s), 0 problem(s)` (`s69-red-check.txt`).
   - **AC-104.8's adjacency test** found that the committed snapshot is sorted, which the plan had missed (D-700).
   - **AC-104.7's parity test**, written against the plan's list, found that annotate accepts control characters (D-699).
   - **The render-equals-bake byte comparisons** (AC-104.2 to .5) prove Copy image matches Save. Codex's probe added 27 of 27 equal baseline-to-current bakes over PNG, JPEG and WebP.

7. **Which tests were trivially obvious?**
   - AC-104.1's signature pins and AC-104.23's reserved-chord pin. Both are guards, which is their purpose.

8. **Did pyright/ruff catch anything meaningful?**
   - No. pyright reported `0 errors, 0 warnings, 0 informations` and ruff `All checks passed!` on the gate (`s69-D6-py-types.txt`, `s69-D6-py-lint.txt`). Row 2 ran ruff on its new test files (Session 68 RULE-4), so row 3 had no lint-only failure.

### Workflow Signal Log

9. **Was the FIC useful as written?**
   - Yes. Eleven mechanism ids, from RENDER_PORT to COPY_HELP, gave the plan, the Reds, the handoff and both reviews one contract.
   - Two ACs carried wrong facts about existing code, the control-character status and the snapshot order. Both were caught by their own tests and changed only through Mat's rulings.

10. **Was the handoff template right-sized?**
    - For one MEU, yes. The cross-family AC rows are the one part that adds nothing (`slim_candidate`).

11. **How many tool calls did this session take?**
    - 711 unique tool calls in this conversation's transcript at H2-2. They cover the planning probes, the one-round plan review, execution, the one-round execution review and closeout.

12. **Which rows were delegated, to which subagent (harness + model), and did any delegated result need rework?**
    - **No task row was delegated** to `av-kit-builder` or `av-kit-verifier`.
    - **Both execution decisions went to Mat** as Decision Briefs through AskUserQuestion, as the prompt requires.
    - **Codex** reviewed the plan and the execution as the independent reviewer, which isn't delegation.

### Decisions Log

| ID | Stage | Question | Resolution | Chosen | Source tag | Reasoning (why this; why the alternatives lost) | Human ref |
|----|-------|----------|------------|--------|------------|--------------------------------------------------|-----------|
| D-158 | grouping | Adopt the synthesis's slices and recommendations as registered MEUs? | human | Yes: every recommendation (C-1 to C-14) and D-1 to D-3 | Human-approved | Mat accepted them all. 09 §Copy image and action names encodes the slice this session implements. | USER_EXPLICIT 2026-10-29 "all recommendations are accepted" |
| D-159 | grouping | Slice to MEU mapping | autonomous | One MEU per slice, with slice 3 split into MEU-101 (3a) and MEU-102 (3b) | Local Canon | MEU-104 is one slice and one MEU. Joining slices would hold one fix behind another's investigation. Two-way. | — |
| D-160 | grouping | Run slices 1, 2 and 3a as one session? | autonomous | Yes, Session 43 | Local Canon | Carried because the decision probe returns it; this session leaves Session 43's slicing unchanged. Two-way. | — |
| D-674 | grouping | Renumber Sessions 44 to 48? | autonomous | They run as Sessions 68 to 72 in the §4 order; §9.1 states the mapping | Local Canon | Row 45 ran as Session 69. Rewriting §6 would erase what D-240 observed. Two-way. | — |
| D-675 | grouping | Which crop rules do redact, step, head and shape take? | autonomous | Redact takes _clip_half_open; step takes the text anchor rule; head rides _clip_arrow; shape waits on D-676 | Local Canon | Carried for the annotation editor sessions. Render adds no mark type, so this session applies none of these rules. Two-way. | — |
| D-677 | grouping | After MEU-104, what does the filmstrip's Copy image copy? | human | A: the annotated variant when the shot has saved marks, else the original, the as-shown rule MEU-136's export uses | Human-approved | One label with two meanings is the ambiguity 09 rejects, and the as-shown rule is already canon for export. This session implements it as FILMSTRIP_AS_SHOWN. The do-nothing option kept variant=original. | USER_EXPLICIT 2026-11-12 "both recommendations accpeted" |
| D-678 | grouping | How does Ctrl+C reach the canvas? | autonomous | Page key handler with isEditableTarget excluded, following Session 61's PASTE_KEY; Ctrl+C stays in RESERVED_CHORDS | Local Canon | Same chord class and text-field guard as Ctrl+V; a registry entry would need the reserved list to change for one key. COPY_KEY implements it. Two-way. | — |
| D-689 | planning | What does bakes through MEU-136's path mean for render? | autonomous | The adapter's bake body after the open becomes _bake_canvas, shared by bake and render; render encodes the canvas in memory as PNG with _encode_view and returns the bytes | Local Canon | One function for the marks means render can't drift from Save. Baking to a temp file lost: it writes a file. Copying the bake loop lost: two copies of the order rule. Two-way. | — |
| D-690 | planning | Does the editor copy ever skip render? | autonomous | The Copy image button and canvas Ctrl+C always post the current marks to render, including an empty list and one equal to the saved list | Local Canon | One path is one set of tests. Fetching the annotated file when clean lost: a JPEG or WebP annotated_format would copy lossy bytes. Two-way. | — |
| D-691 | planning | Does MCP get a render action? | autonomous | No; REST_ONLY names render, and the MCP audit baseline is unchanged | Local Canon | An MCP client has no clipboard, and annotate already returns the baked file's path. A render action lost: image bytes over a text protocol for no user. Two-way. | — |
| D-692 | planning | Where does canvas Ctrl+C live? | autonomous | A branch in handleEditorKey after the history block, guarded by historyOwnsFocus, isEditableTarget, a collapsed selection and the button's enable rule; no copy event listener | Local Canon | handleEditorKey already owns the canvas chords and their early returns. A window copy listener lost: it fires for every copy in the app. A registry entry lost: D-678. Two-way. | — |
| D-693 | planning | What does the dirty-flatten confirm's Save and flatten do? | autonomous | Flatten is enabled while dirty when the marks are savable; its confirm accepts with Save and flatten, which saves, then flattens; a failed save flattens nothing; Restore backup stays disabled while dirty | Local Canon | The confirm can only open if Flatten is enabled while dirty. Keeping it disabled lost: the confirm could never show. Flattening only the saved marks lost: it drops work silently. Two-way. | — |
| D-694 | planning | Which text follows the new names? | autonomous | The action names, confirm accepts, Settings labels, titles, statuses, the help body and the spec docs; not the palette label, the API or MCP names, the settings keys or code comments | Local Canon | Every place a user reads the action's name says the same words. Renaming API or setting keys lost: it breaks clients for a label change. Two-way. | — |
| D-695 | planning | Does render cap its size, and does it lock? | autonomous | No IMAGE_MAX_BYTES cap; render_marks holds CAPTURE_FILE_LOCK while it reads the original and bakes | Local Canon | A cap would make Copy fail on a shot that Save handles. Reading without the lock lost: a torn read under a concurrent flatten. Two-way. | — |
| D-696 | planning | Where does the Copy image button sit and when is it enabled? | autonomous | capture-copy-image after capture-save and before capture-apply-image, ghost, shortcut Ctrl+C; enabled when a shot is selected, its overlay has loaded and no text draft is open | Local Canon | Next to Save it reads as acting on the same marks. Before the overlay loads the current list is empty and would copy the bare image. A filmstrip-only button lost: the row asks for one in the editor. Two-way. | — |
| D-697 | planning | How is the copy tested without the system clipboard? | autonomous | Vitest uses a recording fake for writeClipboardImage and a fake server for render; pytest compares render's bytes with bake's; Electron checks labels and the confirm only and never clicks Copy image | Local Canon | Session 57 RULE-4: no test touches the system clipboard. A live Electron copy lost: it writes Mat's clipboard. Two-way. | — |
| D-698 | planning | What is the execution review budget, and does execution start? | human | Budget 50M with the default cap of 6 rounds; execute now that the plan review has approved | Human-approved | Mat gave the budget and the execution words at the plan gate. The recommendation was 32.5M; the do-nothing option, the ledger default of 21M, was not chosen. The execution review approved in round 1 with 9,785,727 tokens. | USER_EXPLICIT 2026-11-13 '50M, execute' |
| D-699 | execution | AC-104.7 lists control characters as a 422, but annotate accepts them with 200 at b3f3933. How should AC-104.7 read? | human | Parity with annotate: a lone surrogate, empty text, an extra field and a bad type give 422 from both routes; control characters give 200 from both, and render's bytes equal annotate's PNG; no product change | Human-approved | The AC's rule is the same status as annotate. Refusing control characters in both routes lost: it changes annotate's accepted input. Leaving the AC as written, the do-nothing option, lost: its test could not pass. Two-way. | USER_EXPLICIT 2026-11-13 'Parity (Recommended)' |
| D-700 | execution | AC-104.8 puts render right after annotate in the committed snapshot, which export_openapi.py sorts. How should AC-104.8 read? | human | The adjacency pin checks the live schema and ROUTE_INDEX; the committed snapshot carries render with image/png and its entry equals the live one; the route count stays 79 | Human-approved | The live schema keeps route order, so the pin still proves render follows annotate. Dropping sort_keys lost: it reorders the whole committed file. Leaving the AC as written, the do-nothing option, lost: its test cannot pass. Two-way. | USER_EXPLICIT 2026-11-13 'Live + index (Recommended)' |

---

## Pattern Extraction

### Patterns to KEEP
1. **One shared bake body for every writer and reader of marked pixels.** `_bake_canvas` makes Copy image equal Save by construction, and the byte comparisons prove it.
2. **A literal pin sweep before the Red** (Session 68 RULE-2). It found five pins the plan's table missed, all before any test ran.
3. **Decision Briefs for AC changes found mid-row** (Session 59 RULE-3). Both changes are Mat's words in the plan's YAML, and the handoff's Decision Log stays `None.`.

### Patterns to DROP
1. **AC text that states an existing route's behaviour from reading its schema.** AC-104.7's control-character case was wrong because nobody posted one to annotate at plan time.

### Patterns to ADD
1. **Probe the existing route an AC claims parity with, case by case, at plan time** (RULE-1).
2. **Check the writer's ordering before pinning a position in a generated file** (RULE-2).
3. **Copy expected error envelopes from a sibling test's constant** (RULE-3).
4. **Check at Red time that every source path a test reads exists** (RULE-4).

### Calibration Adjustment
- **Estimated:** the plan review's ledger budget was 10,500,000 and the execution review's round 1 estimate was about 13M (D-698's recommendation of 32.5M). Mat set 50M.
- **Actual time (local time, UTC-5), 2026-11-13:**
  - Plan review round 1 approved at 10:06.
  - The baseline ran at 13:49, row 1's sweep finished at 15:08 and row 2's Red ran at 15:29.
  - Row 3's Green passed at 15:44, with D-700 ruled in between, and the H1-2 gate passed at 15:52.
  - Execution round 1 approved at 16:11.
- **Tokens:**
  - plan review: 12,764,759 over one round, above its 10,500,000 budget; the ledger let the first round run and refused a second;
  - execution review: 9,785,727 over one round, of 50,000,000.
- **Adjusted estimate for a one-MEU route plus GUI change:** budget about 13M for a plan round and about 10M to 13M for an execution round. A plan-review budget near 10.5M is too small for one round at this size.

---

## Next Session Design Rules

```
RULE-1: When an AC says a new route or field behaves like an existing one, the plan probes the existing one with every case the AC lists (posting each body through the real stack) and copies the observed status into the AC, before the plan review.
SOURCE: D-699: AC-104.7 listed control characters among annotate's 422 cases, but annotate returns 200 for them at b3f3933 (s69/probe-text.txt).
EXAMPLE: "control characters give 422 from both routes" becomes "probe: annotate returns 200 for control characters, so both routes give 200".
```

```
RULE-2: An AC that pins the position of an entry in a generated file names the generator and how it orders entries (sort_keys, insertion order), and the plan checks that the pinned order survives the writer.
SOURCE: D-700: AC-104.8 pinned render after annotate in openapi.committed.json, which tools/export_openapi.py writes with sort_keys=True.
EXAMPLE: "render follows annotate in the committed snapshot" becomes "render follows annotate in the live schema and ROUTE_INDEX; the snapshot is sorted, so it checks entry equality".
```

```
RULE-3: A Red test's expected error envelope is imported or copied from a sibling test's constant, never typed fresh, so the Green fails only on the behaviour.
SOURCE: Handoff Departures 4: VALIDATION lacked "details": None, so AC-104.7's four 422 cases failed in Green on the expected envelope alone.
EXAMPLE: "VALIDATION = a hand-written dict" becomes "VALIDATION copied from test_api_captures.py's 422 constant, with a test that the two are equal".
```

```
RULE-4: A Red row checks that every repository path a new test reads (a source file it greps, a fixture it opens) exists at the Red's commit, so the Red fails on behaviour and not on a missing file.
SOURCE: Handoff Departures 6: AC-104.16 read features/capture/settings-schemas.ts; the file is features/settings/settings-schemas.ts.
EXAMPLE: row 2's Validation cell gains "every path literal in the new tests resolves: 0 missing".
```

---

## Next Day Outline

1. **Target:** done, pending Mat's commit. MEU-104 is approved.
2. **Next session:** Session 70 `capture-text-multiline` (MEU-102, grouping row 46). The prompt is `C:/Temp/av-kit/session-70-prompt.md`.
3. **Scaffold changes needed:** none.
4. **Patterns to bake in from today:** RULE-1 to RULE-4 here, plus the rules carried from Sessions 50 to 68.
5. **Codex validation scope:** the next session's plan, then its execution.
6. **Time estimate:** set by the next session's plan; a plan-review budget near 13M per round.
7. **Still open:**
   - **The ruff baseline in `tools/`.** 10 errors in `tools/issue_triage*` and `tools/meu_status*` predate Session 68 (its DEP-1); a plan that runs `ruff check tools/` must narrow it or fix them first.
   - **ShareX and F2.** ShareX held F2 during the baseline, as in MEU-93 D-120. AC-81.11 fails while it runs.

---

## Efficiency Metrics

| Metric | Value |
|--------|-------|
| Total tool calls | 711 unique tool calls in this conversation's transcript at H2-2, from planning on |
| Time to first green test | Row 3's Green at 2026-11-13 15:44 (UTC-5), 15 minutes after row 2's Red (`s69-py-red.txt`, `s69-py-green.txt`) |
| Tests added | pytest 2435 to 2459 (+24; `s69-base-py.txt`, `s69-D6-py-tests.txt`); Vitest 1303 to 1322 (+19; `s69-base-ui.txt`, `s69-D6-ui-tests.txt`); MCP 526 to 527 (+1; `s69-base-mcp.txt`, `s69-D6-mcp-tests.txt`); Electron 46 to 47 (+1; `s69-base-e2e.txt`, `s69-D6-ui-electron.txt`) |
| Codex findings | Plan review: R1 approved with 0 findings (12,764,759). Execution review: R1 approved with 0 findings (9,785,727 of 50,000,000) |
| Handoff Score (X/7) | 7/7. Every AC has evidence, the handoff checks passed before the dispatch, and the execution review approved in round 1 with no findings |
| Rule Adherence (%) | 94 (16 of 17 sampled rules followed in full, 1 in part) |
| Prompt→commit time | Planned and executed 2026-11-13; commit pending Mat's words |

### Rules Sampled for Adherence Check

| Rule | Source | Followed? |
|------|--------|-----------|
| Tests before production code; Red before Green | AGENTS.md §Testing & TDD | Yes. Row 2's Red failed by assertion on pytest, Vitest and Electron before row 3's Green |
| Independent review; no self-approval | AGENTS.md §Dual-Agent Workflow | Yes. Both canonical reviews are Codex's reports, validated under `C:/Temp/av-kit` and copied byte for byte |
| Human decisions stay human, with a brief and a do-nothing option | `.agent/docs/human-decision-protocol.md` | Yes. D-698 to D-700 record Mat's words; each brief carried a do-nothing option |
| An AC change goes to Mat as a Decision Brief | Session 59 RULE-3 | Yes. D-699 and D-700 |
| Name every caller of anything extended | Session 55 RULE-1 | Yes. Row 1's caller sweep (`s69/sweep-r1.txt`) |
| Sweep pins by the literal text a change rewrites | Session 68 RULE-2 | Yes. Row 1 found the five pins in §Departures 1 |
| Run ruff on the Red row's new test files | Session 68 RULE-4 | Yes |
| Check Red test id lengths at plan time | Session 67 RULE-4 | Yes. `s69-r2-id-length.txt` |
| Review prompts carry the literal table shapes | Session 66 RULE-4 | Yes. Both reports were accepted by the closeout parser the first time |
| Execution decisions in the plan's YAML; handoff Decision Log `None.` | Session 65 RULE-2 | Yes |
| `## Findings` holds only the table | Session 65 RULE-3 | Yes |
| Each Red fails by assertion | Session 62 RULE-3 | Yes |
| Byte-edit a status file another session may hold dirty | Session 61 RULE-5 | Yes. The grouping row and the approval |
| If another program holds a system-wide resource a test needs, stop and ask Mat; never stop it | Session 58 RULE-4 | Partly. Nothing was stopped, but I did not ask Mat about ShareX holding F2; it had exited by row 3 |
| No test touches the system clipboard | Session 57 RULE-4 | Yes. Recording fakes in Vitest; Electron never clicks Copy image |
| No test reaches the network | Session 69 prompt | Yes |
| Tell Mat before each metered Codex dispatch | Session 69 prompt | Yes |

---

## Instruction Coverage

```yaml
schema: v1
session:
  id: "e6192193-2919-489f-8afa-050983d4edd6"
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
  workflows: [create_plan, plan_critical_review, execution_session, execution_critical_review]
  roles: [orchestrator, coder, tester]
  skills: []
  refs:
    - .agent/docs/human-decision-protocol.md
    - .agent/docs/harness-profiles.md
    - .agent/schemas/review-verdict.schema.v2.json
    - .agent/schemas/reflection.v1.yaml
    - .agent/templates/REVIEW-TEMPLATE.md
    - docs/execution/reflections/TEMPLATE.md
decisive_rules: [P0:human-decisions-stay-human, P0:no-system-clipboard-in-tests, P1:independent-review-no-self-approval, P1:tests-before-production-code, P0:never-commit-or-push-without-human-approval]
conflicts:
  - "The harness asks for a Co-Authored-By trailer on commits; task H2-5, development-lifecycle.md:454 and Mat's rule say no AI attribution trailer. The commit has none."
  - "Connected docs and artifact tools offered to publish deliverables; the user's rule keeps them as local repo files."
note: "A render route and Copy image with unsaved marks; two ACs carried wrong facts about existing code and went to Mat."
slim_candidate: ["The cross-family AC rows in the handoff exist only for the AC check.", "H2-1's view_file row repeats what H2-2's validator checks."]
overthinking_observed: false
review_churn:
  rounds_to_approval: {plan: 1, execution: 1}
  findings_per_round:
    - {review: plan, round: 1, critical: 0, high: 0, medium: 0, low: 0}
    - {review: execution, round: 1, critical: 0, high: 0, medium: 0, low: 0}
  churned_findings: 0
  finding_categories: {}
  verdicts: {approved: 2}
meu_work_classes: [correctness]
```
