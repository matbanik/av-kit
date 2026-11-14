---
date: "2026-11-14"
project: "capture-style-tool-flow"
meus: ["MEU-105"]
plan_source: "docs/execution/plans/2026-11-13-capture-style-tool-flow/implementation-plan.md"
template_version: "2.0"
---

# 2026-11-14 Meta-Reflection

> **Date**: 2026-11-14 (planned on 2026-11-13; plan review, execution, execution review and closeout ran into 2026-11-14)
> **MEU(s) Completed**: MEU-105 `gui-capture-style-tool-flow`, Session 71 `capture-style-tool-flow`, the fourth of the five capture annotation editor sessions (grouping row 47, D-674). Mat split the slice (D-713 "A"): Lock, the tool letters and the drawing modifiers moved to the new MEU-143 `gui-capture-tool-flow` (Session 71b, grouping row 47b). The grouping says P3 and `meu-status.yaml` says P2 for both MEUs; this session names the mismatch and changes neither (D-725).
>
> **MEU-105:**
> - Colour applies on click. A named pick commits at once (COLOR_NAMED); the hex field commits on Enter or blur when `normalizeHex` accepts its text, and refused text commits nothing and is never sent (COLOR_HEX). The colour well and the text background well preview on `input` and commit once on the native `change` (COLOR_WELL, TEXT_BG_WELL, D-718). The Apply and Cancel buttons and the colour gate are gone (COLOR_GATE_GONE). One pick, one well gesture or one drag is one undo step.
> - Arrow, Box, Highlight, Text and Pixelate each keep their own style as nine new `capture` settings leaves, with today's values as defaults (STYLE_SETTINGS, D-714 to D-716). The service and the API refuse a malformed colour, a non-integer and an out-of-range value, naming the key only (STYLE_API), and MCP's `avkit_settings` describes and accepts the leaves (STYLE_MCP, D-717).
> - One ordered write queue sends one PUT per commit in commit order, and every GET of the capture namespace keeps each style leaf a commit it did not see changed (STYLE_STORE, D-720). A snapshot of the committed leaves carries a commit made while the first GET is pending or after it failed (execution round 1 F1).
> - With a mark selected a style control restyles only that mark, as one undo step; with none selected it saves the armed tool's style and writes no undo step (STYLE_TARGET, STYLE_DRAW, STYLE_DISPLAY, D-719). A new text draft takes the text style, background included; a re-edited text mark is restyled instead (TEXT_DRAFT_STYLE, D-723).
> - Select with nothing selected shows no style field (SELECT_NO_STYLE, D-721). Pixelate block size gets the scrub handle, clamped to 2 and 100 (BLOCK_SCRUB, D-722). The help body and `gui-actions-index.md` follow (STYLE_HELP, STYLE_ACTIONS_INDEX).
>
> **Plan Source**: `docs/execution/plans/2026-11-13-capture-style-tool-flow/implementation-plan.md`

---

## Execution Trace

### Friction Log

1. **What took longer than expected?**
   - **The plan review took three rounds, all on STYLE_STORE's ordering.** Round 1 found that successive commits to one leaf were unordered, so the older PUT could be stored last (F1, High), and that an integer of hundreds of digits reached `float()` at STYLE_API (F2, Medium). Round 2 found that the failure refetch, or any refocus refetch, could answer with a value older than a newer commit and replace it in the cache (F3, High). Round 3 approved. Round 3 needed 7M more than D-726 set (D-728). RULE-1 adds the missing check.
   - **Execution round 1 returned changes_required** with 19,217,304 tokens against a 13M estimate. F1 (High, blocking): `saveCaptureToolStyle` wrote its commit into the cache only when the cache held data, so a commit made while the first GET was pending, or after it failed, drew the next mark with the default. F2 (Medium): TEXT_DRAFT_STYLE said the draft shows the background, but the draft carried only the colour and size. Both were fixed Red first (`s71-fix-r1-red.txt`: `Tests  3 failed | 26 skipped (29)`), the gate ran again, and round 2 approved. Round 2 needed more budget than D-727 set; Mat added 20M (D-729). RULE-1 and RULE-2 add the missing checks.
   - **A pin row 1's sweep did not name** (handoff §Departures 1). `capture-page.behavior.test.ts:1566` expected Select to show Color and Stroke; the sweep searched for `optionGroups`, and the line names the tool button's test id. Row 3 moved it before Green (RULE-3).
   - **AC-60.8 failed in Green on a field SELECT_NO_STYLE hides** (handoff §Departures 3). A shot that loads with marks arms Select, so the test's read of `capture-color` before the pick found nothing. Row 4 says no test file changes (S2), and S2 says to stop; the coordinator moved the check to `expect(screen.queryByTestId('capture-color')).toBeNull()` and did not stop (RULE-3).
   - **AC-105.28's guard first failed at its mid-drag read** (handoff §Departures 4). The test now reads the scrub preview the way `capture-page.behavior.test.ts` does. The first failing run's output was not kept.
   - **The held-GET test gained a line after its Red** (handoff §Departures 7). The page leaves Arrow after a draw, so `await chooseTool('arrow')` went in before the second draw. The Red failure was at the first draw's assertion, before the added line.
   - **H1-6 refused D-729 written as prose in the plan.** It moved into a `decision_log` YAML block in the handoff (HDP §6), and H1-6 passed (RULE-4).

2. **What instructions were ambiguous?**
   - **The band.** The grouping's tracker row 47 says P3; `meu-status.yaml` says P2. The Session 71 prompt said to name it and change neither, and MEU-143 takes the same pair (D-725). It stays open for Mat.
   - **D-717 against the prompt.** The prompt expected no OpenAPI or MCP change, because style is never mark JSON. The settings surfaces had to change: `SettingsPutIn` forbids extra keys and the MCP set input is strict. No mark schema, capture action or audit baseline changed. The plan names the change and its reason.
   - **The commit trailer.** The harness asks for a Co-Authored-By trailer. Task H2-5, `.agent/docs/development-lifecycle.md:454` and Mat's standing rule say there is none, so the commit draft has none.

3. **What instructions were unnecessary?**
   - H2-1's `view_file` row, as in Sessions 59 to 70. H2-2's check validates the reflection against the same template and schema.
   - The handoff's cross-family AC rows. They exist only so the handoff check accepts the AC table.

4. **What was missing?**
   - **A plan-time state matrix for an optimistic store** that includes an empty, loading and failed cache next to the ordering cases. Plan rounds 1 and 2 covered ordering; execution round 1 found the empty cache (RULE-1).
   - **One assertion per field of a "shows" contract.** TEXT_DRAFT_STYLE named the colour, the size and the background; the tests asserted the first two (RULE-2).
   - **A sweep by test id when a change hides a control** (RULE-3).
   - **A rule that an execution-stage decision goes into the handoff's YAML block when it is first written** (RULE-4).

5. **What did you do that wasn't in the prompt?**
   - **Probed the big-integer path after the gate** (`s71-bigint-probe.txt`). At the API, 401 digits gives a 422, 4300 digits gives a 422 for the cookie-byte limit, and 4301 or more gives a 400 from the body parser; no path gives a 500. It is recorded as an observation (handoff §Deferred Items); no code changed.
   - **Wrote `s71/decision-probe-closeout.py`** from Session 70's. It found 20 decisions: D-713 to D-728 `planning`, D-729 `execution` and D-158 to D-160 `grouping`, with every source unchanged (`s71-closeout-decision-probe.txt`). Grouping §8 still ends at D-160, §9.8 at D-678 and §9.9 at D-713, so D-674 and D-675 are carried by hand.
   - **Set MEU-105 to `approved` by a counted byte replacement** (`s71/approve-105.py`), with the three status files copied first to `s71/pre-approve/`. The diff (`s71/approve-diff.txt`) holds only MEU-105's status lines, its registry row and BUILD_PLAN's P2 count, 125 to 126, with the Total at 138 + 1🚫.

### Quality Signal Log

6. **Which tests caught real bugs?**
   - **Every Red failed by assertion** (Session 62 RULE-3): Vitest `Tests  28 failed | 6 passed (34)` (`s71-ui-red.txt`) and Electron `1 failed` (`s71-e2e-red.txt`), with red-check `2 receipt(s), 21 required test(s), 0 problem(s)` (`s71-red-check.txt`). The round 1 corrections' Red read `Tests  3 failed | 26 skipped (29)` with red-check `1 receipt(s), 3 required test(s), 0 problem(s)` (`s71-fix-r1-red-check.txt`).
   - **AC-105.32's held and failed first GET** proved execution F1: `before the GET answers: expected '#E0AF68' to be '#12ABCD'`.
   - **AC-105.17's Bg draft** proved execution F2: `the new draft shows the Bg: expected '' to be '#112233'`.
   - **AC-60.8's load check** found that SELECT_NO_STYLE changes what a loaded shot shows before the pick (§Departures 3).

7. **Which tests were trivially obvious?**
   - AC-105.1's signature pins and the AC-105.27, .28 and .30 guards on today's paths. They are guards, which is their purpose.

8. **Did pyright/ruff catch anything meaningful?**
   - No. pyright reported 0 errors and ruff `All checks passed!` on the gate (`s71-D6-py-types.txt`, `s71-D6-py-lint.txt`). The plan narrowed ruff to the edited files, since `ruff check tools/` fails at baseline (Session 68 DEP-1).

### Workflow Signal Log

9. **Was the FIC useful as written?**
   - Yes. Twenty mechanism ids, from STYLE_SETTINGS to STYLE_ACTIONS_INDEX, gave the plan, the Reds, the handoff and five review rounds one contract. Each review finding named the id it broke.
   - The split (D-713) kept the store and the toolbar in one session and the registry and pointer handlers in the next.

10. **Was the handoff template right-sized?**
    - For one MEU, yes. The cross-family AC rows are the one part that adds nothing (`slim_candidate`).

11. **How many tool calls did this session take?**
    - 935 unique tool calls in this conversation's transcript when this reflection was written. They cover the planning probes, the three-round plan review, execution, the two-round execution review with its corrections, and closeout.

12. **Which rows were delegated, to which subagent (harness + model), and did any delegated result need rework?**
    - **No task row was delegated** to `av-kit-builder` or `av-kit-verifier`.
    - **D-713, D-726, D-727, D-728 and D-729 went to Mat** through AskUserQuestion, as the prompt requires.
    - **Codex** reviewed the plan and the execution as the independent reviewer, which isn't delegation.

### Decisions Log

| ID | Stage | Question | Resolution | Chosen | Source tag | Reasoning (why this; why the alternatives lost) | Human ref |
|----|-------|----------|------------|--------|------------|--------------------------------------------------|-----------|
| D-158 | grouping | Adopt the synthesis's slices and recommendations as registered MEUs? | human | Yes: every recommendation (C-1 to C-14) and D-1 to D-3 | Human-approved | Mat accepted them all. 09 §Per-tool style encodes the slice this session implements. | USER_EXPLICIT 2026-10-29 "all recommendations are accepted" |
| D-159 | grouping | Slice to MEU mapping | autonomous | One MEU per slice; slice 6 is MEU-105 | Local Canon | MEU-105 is slice 6. D-713 later split its flow half into MEU-143. Two-way. | — |
| D-160 | grouping | Run slices 1, 2 and 3a as one session? | autonomous | Yes, Session 43 | Local Canon | Carried because the decision probe returns it; this session leaves Session 43's slicing unchanged. Two-way. | — |
| D-674 | grouping | Renumber Sessions 44 to 48? | autonomous | They run as Sessions 68 to 72 in the §4 order; §9.1 states the mapping | Local Canon | Row 47 ran as Session 71, and row 47b runs as Session 71b. Rewriting §6 would erase what D-240 observed. Two-way. | — |
| D-675 | grouping | Which crop rules do redact, step, head and shape take? | autonomous | Redact takes _clip_half_open; step takes the text anchor rule; head rides _clip_arrow; shape waits on D-676 | Local Canon | Carried for the annotation editor sessions. MEU-105 adds no mark type and changes no crop rule. Two-way. | — |
| D-713 | planning | Does MEU-105 split, and how? | human | A: MEU-105 keeps the Colour row, the Tool style row and the Pixelate scrub; a new MEU-143 gui-capture-tool-flow takes Lock, Letters and the rest of Modifiers for Session 71b | Human-approved | The five rows were estimated above Session 41's three-round plan cost, and the halves touch different code. The do-nothing option, one session for all five rows, was not chosen. Two-way: MEU-143 can fold back before Session 71b plans. | USER_EXPLICIT 2026-11-13 'A' |
| D-714 | planning | Where does a tool's style live? | autonomous | Nine leaves in the capture settings namespace, through SETTINGS_KEY_TABLE, the Settings API and the MCP settings toolset, read by a hook that shares the capture settings query | Local Canon | The settings path is the app's preference store, validated per key and readable by agents. One JSON string leaf lost: it hides every field from the per-key checks. Browser storage lost: it is not an app preference and an agent can't read it. Two-way. | — |
| D-715 | planning | Which tools have a style, with which fields? | autonomous | Arrow and Box: colour and stroke; Highlight: colour; Text: colour, font size and background; Pixelate: block size; Select, Smart eraser, Crop and Solid redact have none | Local Canon | A tool's style is what its options row shows. Saving the Redact mode lost: D-680 keeps it unsaved. Two-way. | — |
| D-716 | planning | What are the defaults? | autonomous | Today's single values: #E0AF68, stroke 3, font size 16, no background, block size 10 | Local Canon | A fresh install draws exactly as today. Distinct colours per tool lost: they change what every user sees with no request for it. Two-way. | — |
| D-717 | planning | Do OpenAPI and MCP change? | autonomous | Yes, for the settings path only: SettingsPutIn and the snapshot gain the nine leaves, and SETTINGS_SCHEMA and the strict set schema gain them; no mark schema, capture action or audit baseline changes | Local Canon | The prompt expected no change; the API refuses an unknown key and the MCP set would refuse a key its get returns. Leaving MCP out lost: an agent would read leaves it can't write. Two-way. | — |
| D-718 | planning | Which events commit a colour? | autonomous | A named pick; Enter or blur with valid hex text; the well's native change event after input events that only preview; an equal commit does nothing; invalid text applies nothing | Local Canon | Committing on change gives one undo step per pick. Committing on every input lost: one drag would make dozens of steps. Two-way. | — |
| D-719 | planning | What does a change restyle? | autonomous | With a mark selected, only that mark, as one undo step; with none selected and a style tool active, that tool's style, as a preference write and no undo step | Local Canon | 09 says only that mark. Also setting the tool's style on a mark restyle lost: the rule says only that mark. Two-way. | — |
| D-720 | planning | When is a tool style written, and what if the write fails? | autonomous | One PUT per commit holding only the changed leaves, sent in commit order through one shared queue, the cache updated at once, every capture GET keeping a leaf a commit it did not see changed; a failure shows Couldn't save the tool style and refetches once the queue is empty | Local Canon | Plan review F1 added the queue and F3 the GET filter. Writing the response into the cache lost: an older response could land after a newer value. Cancelling queries on each commit lost: it would cancel the Settings card's refetch. Two-way. | — |
| D-721 | planning | What does Select show with nothing selected? | autonomous | No style controls | Local Canon | With per-tool style a control there has no tool to set. Keeping Color and Stroke, the do-nothing option, lost: they would change nothing. Two-way. | — |
| D-722 | planning | How does the Pixelate scrub work? | autonomous | CaptureScrubField with a new optional min prop, min 2 and max 100, the input id kept, the handle capture-block-size-scrub, and a block burst so a drag is one undo step | Local Canon | Reusing the scrub field gives the same drag, wheel, keys and undo as Stroke and Size. A separate block scrub lost: two behaviours to keep alike. Two-way. | — |
| D-723 | planning | What does a style change do while a text draft is open? | autonomous | A new draft: it sets the text tool's style and the draft shows it; a re-edit: it restyles that mark as one undo step | Local Canon | A new draft is not a mark yet; a re-edited mark is selected. Treating both as the mark lost: a new draft has no mark. Two-way. | — |
| D-724 | planning | Which later MEUs depend on MEU-143? | autonomous | MEU-106 gains MEU-143 for its Ctrl+D registry entry; MEU-107 stays on MEU-105 only | Local Canon | A dependency names what the later MEU builds on. MEU-107 on MEU-143 too lost: it would wait on letters it doesn't use. Two-way. | — |
| D-725 | planning | Which band does MEU-143 take? | autonomous | P2 in meu-status.yaml and P3 in the grouping's row 47b, the pair MEU-105 has | Local Canon | The mismatch stays one mismatch for Mat to settle once. Choosing one band lost: it settles it for one MEU without Mat. Two-way. | — |
| D-726 | planning | What is the plan review budget? | human | About 20M: round 1 and one recheck | Human-approved | The do-nothing option was the 10.5M default, which stops before a recheck. | USER_EXPLICIT 2026-11-13 'About 20M (Recommended)' |
| D-727 | planning | What is the execution review budget, and does execution start? | human | 33M with the default cap of 6, and execute now | Human-approved | The do-nothing options were the 21M default and not executing. | USER_EXPLICIT 2026-11-14 '33M (Recommended)' and 'Execute now (Recommended)' |
| D-728 | planning | Round 3 needs more plan review budget than D-726 set. How much is added? | human | Add 7M, so the plan review budget is 27M | Human-approved | Round 3 used 7,562,519 and approved, for 24,330,246 of 27,000,000. The do-nothing option was to stop with F3's fix unchecked. | USER_EXPLICIT 2026-11-14 'Add 7M (Recommended)' |
| D-729 | execution | Execution round 2 needs more review budget than D-727 set. How much is added? | human | Add 20M, so the execution review budget is 53M | Human-approved | Mat chose 20M over the recommended 7M. Round 2 used 5,837,998 and approved, for 25,055,302 of 53,000,000. The do-nothing option was to stop with the F1 and F2 fixes unchecked. | USER_EXPLICIT 2026-11-14 'Add 20M' |

---

## Pattern Extraction

### Patterns to KEEP
1. **Split a slice at the code seam, before planning the second half** (D-713). The style half touched the settings path and the options row; the flow half touches the registry and the pointer handlers.
2. **Filter stale reads at the one shared query function** (D-720, F3). Every GET, refocus and card refetch passes through it, so one guard covers them all.
3. **Fix review findings Red first and rerun the full gate** before the recheck. Round 2 approved with no new findings.

### Patterns to DROP
1. **Testing an optimistic store only on a loaded cache.** Execution F1 lived in the empty and failed cache.
2. **Asserting part of a "shows" contract.** Execution F2 was the one field the tests didn't read.
3. **Writing an execution-stage decision into the plan's prose.** H1-6 refused it.

### Patterns to ADD
1. **List an optimistic store's cache states at plan time** (RULE-1).
2. **One assertion per field a "shows" contract names** (RULE-2).
3. **Sweep tests by the test id of any control a change hides** (RULE-3).
4. **Write an execution-stage decision as YAML in the handoff at once** (RULE-4).
5. **Budget a store with an ordering contract for three plan rounds** (RULE-5).

### Calibration Adjustment
- **Estimated:** plan review round 1 13M and about 20M in all (D-726); execution review round 1 13M and about 33M in all (D-727).
- **Actual time (local time, UTC-5):**
  - Plan review round 1 at 2026-11-13 23:28; round 3 approved at 2026-11-14 00:46.
  - The baseline ran at 01:00, the UI Red at 01:34, the UI Green at 01:56 and the H1-2 gate at 02:05.
  - Execution round 1 at 02:34; the fix Red at 02:40, the fix Green at 02:42, the gate rerun at 02:47.
  - Execution round 2 approved at 09:01.
- **Tokens:**
  - plan review: 9,956,487, 6,811,240 and 7,562,519 over three rounds, 24,330,246 of 27,000,000;
  - execution review: 19,217,304 and 5,837,998 over two rounds, 25,055,302 of 53,000,000.
- **Adjusted estimate for a one-MEU store and toolbar change across the settings path:** about 10M per plan round with three rounds, and about 20M for the first execution round with about 6M per recheck.

---

## Next Session Design Rules

```
RULE-1: A plan that adds an optimistic cache write lists, beside its ordering cases, what a commit does when the cache is empty because the first read is still pending, and when that read failed, and gives each case an AC.
SOURCE: Execution round 1 F1: saveCaptureToolStyle wrote into the cache only when it held data, so a commit during a held or failed first GET drew the next mark with the default. Plan rounds 1 and 2 had covered only ordering.
EXAMPLE: STYLE_STORE's matrix gains "first GET held" and "first GET failed" rows, as AC-105.32's two added tests do.
```

```
RULE-2: When a mechanism says a surface shows a set of fields, its test asserts each named field on that surface, not only the ones the old code already showed.
SOURCE: Execution round 1 F2: TEXT_DRAFT_STYLE named colour, size and background; the tests read colour and size, and the draft never showed the background.
EXAMPLE: "the draft shows the text style" gets three expects, one each for color, fontSize and backgroundColor.
```

```
RULE-3: When a change hides or removes a control, row 1's pin sweep searches for that control's test id and its tool's test id, not only for the function that decides the control.
SOURCE: Handoff Departures 1 and 3: SELECT_NO_STYLE hid capture-color under Select; the sweep searched optionGroups and missed capture-page.behavior.test.ts:1566 and AC-60.8's read at :723.
EXAMPLE: the sweep for SELECT_NO_STYLE adds rg "capture-color|capture-stroke|capture-tool-select" over ui/tests.
```

```
RULE-4: A decision made during execution goes straight into a decision_log YAML block in the handoff's Decision Log, with stage execution, before H1-6 runs; the plan's prose does not hold it.
SOURCE: H1-6 refused D-729 while it sat as prose in the plan; moving it to the handoff's YAML block passed (HDP section 6).
EXAMPLE: after Mat's "Add 20M", write the D-729 YAML entry in the handoff, then run H1-6.
```

```
RULE-5: A plan whose store promises an order across concurrent writes and reads budgets three plan review rounds of about 10M each, and about 20M for the first execution round.
SOURCE: Session 71: plan rounds 9.96M, 6.81M and 7.56M (F1 ordering, F3 refetch); execution round 1 19.2M against a 13M estimate.
EXAMPLE: the budget question offers "about 30M plan" and "about 26M execution: 20M plus a 6M recheck" as its recommendations.
```

---

## Next Day Outline

1. **Target:** done, pending Mat's commit. MEU-105 is approved.
2. **Next session:** Session 71b `capture-tool-flow` (MEU-143, grouping row 47b). The prompt is `C:/Temp/av-kit/session-71b-prompt.md`.
3. **Scaffold changes needed:** none.
4. **Patterns to bake in from today:** RULE-1 to RULE-5 here, plus the rules carried from Sessions 50 to 70.
5. **Codex validation scope:** the next session's plan, then its execution.
6. **Time estimate:** set by the next session's plan; see RULE-5 for a store or ordering change.
7. **Still open:**
   - **The band mismatch.** The grouping says P3 for MEU-105 and MEU-143 and `meu-status.yaml` says P2. Mat decides which is right.
   - **AC-60.12's title** still reads `typed hex, Apply` while its body presses Enter; Session 71b fixes the title.
   - **The ruff baseline in `tools/`.** Errors in `tools/issue_triage*` and `tools/meu_status*` predate Session 68 (its DEP-1).
   - **The big-integer path.** `_reject_cookie_shaped` calls `str(value)` before the range check; no API path reaches it with more than 4300 digits.

---

## Efficiency Metrics

| Metric | Value |
|--------|-------|
| Total tool calls | 935 unique tool calls in this conversation's transcript when this reflection was written, from planning on |
| Time to first green test | The UI Green at 2026-11-14 01:56 (UTC-5), 22 minutes after the UI Red (`s71-ui-red.txt`, `s71-ui-green.txt`) |
| Tests added | pytest 2480 to 2553 (+73); Vitest 1333 in 124 files to 1370 in 126 files (+37); MCP 528 to 529 (+1); Electron 49 to 50 (+1) (`s71-D6-py-tests.txt`, `s71-D6-ui-tests.txt`, `s71-D6-mcp-tests.txt`, `s71-D6-ui-electron.txt`) |
| Codex findings | Plan review: R1 changes_required (F1 High, F2 Medium), R2 changes_required (F3 High), R3 approved (24,330,246 of 27,000,000). Execution review: R1 changes_required (F1 High, F2 Medium), R2 approved with 0 findings, intent achieved (25,055,302 of 53,000,000) |
| Handoff Score (X/7) | 6/7. Every AC has evidence and the handoff checks passed before each dispatch, but execution round 1 found two defects the tests had missed |
| Rule Adherence (%) | 75 (12 of 16 sampled rules followed in full, 4 in part) |
| Prompt→commit time | Planned 2026-11-13, executed and approved 2026-11-14; commit pending Mat's words |

### Rules Sampled for Adherence Check

| Rule | Source | Followed? |
|------|--------|-----------|
| Tests before production code; Red before Green | AGENTS.md §Testing & TDD | Yes. Row 3's Red and the round 1 corrections' Red failed by assertion before their Green |
| No test file changes after the Red; stop if one must | Plan S2 | Partly. AC-60.8's check moved in Green and the coordinator did not stop (§Departures 3); the held-GET test gained a line after its Red (§Departures 7) |
| Independent review; no self-approval | AGENTS.md §Dual-Agent Workflow | Yes. Both canonical reviews are Codex's reports, validated under `C:/Temp/av-kit` and copied byte for byte |
| Human decisions stay human, with a brief and a do-nothing option | `.agent/docs/human-decision-protocol.md` | Yes. D-713 and D-726 to D-729 record Mat's words; each brief carried a do-nothing option |
| Execution decisions in YAML (HDP §6) | Session 65 RULE-2 | Partly. D-729 first went into the plan's prose; H1-6 refused it and it moved to the handoff's YAML (RULE-4) |
| Sweep pins by the literal text a change rewrites | Session 68 RULE-2 | Partly. The sweep missed the Select test-id pin and AC-60.8's read (RULE-3) |
| Name every caller of anything extended | Session 55 RULE-1 | Yes. Row 1's caller sweep (`s71-r1-pin-sweep.txt`) |
| Every path a test names exists at Red | Session 69 RULE-4 | Yes |
| Match rendered marks by content | Session 70 RULE-1 | Yes. The style tests find marks by kind and position |
| Ask Mat before any read of user data | Session 70 RULE-2 | Yes. No row read the inbox, its sidecars, the database or the settings file |
| Quote ledger defaults from `review_ledger.py` | Session 70 RULE-3 | Yes. D-726 and D-727 cite `review_ledger.py:102` |
| FAIL_TO_PASS cites only ids that failed at Red | Session 70 RULE-4 | Yes. red-check required 21 and then 3 ids, 0 problems |
| Keep line endings; check for lone CR | Session 70 RULE-5 | Yes. The status files and the handoff stay LF; 09, the grouping, `current-focus.md` and `metrics.md` stay CRLF |
| Each Red fails by assertion | Session 62 RULE-3 | Yes |
| Review prompts carry the ledger vocabulary and literal table shapes | Session 66 RULE-4 | Yes. All five reports were accepted by the closeout parser the first time |
| A test edit after Red changes no AC | Session 71 prompt | Partly. No AC text changed, but two test edits came after their Red (§Departures 3, 7) |

---

## Instruction Coverage

```yaml
schema: v1
session:
  id: "979b7352-4922-41da-b032-104d86277615"
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
decisive_rules: [P0:human-decisions-stay-human, P0:never-commit-or-push-without-human-approval, P1:independent-review-no-self-approval, P1:tests-before-production-code, P0:scope-changes-go-to-mat]
conflicts:
  - "The harness asks for a Co-Authored-By trailer on commits; task H2-5, development-lifecycle.md:454 and Mat's rule say no AI attribution trailer. The commit has none."
  - "Connected docs and artifact tools offered to publish deliverables; the user's rule keeps them as local repo files."
  - "The Session 71 prompt expected no OpenAPI or MCP change; the settings surfaces had to change for the new leaves (D-717)."
note: "Per-tool style as capture settings with an ordered write queue; three plan rounds and two execution rounds, every finding in the store or the draft style, all fixed Red first."
slim_candidate: ["The cross-family AC rows in the handoff exist only for the AC check.", "H2-1's view_file row repeats what H2-2's validator checks."]
overthinking_observed: false
review_churn:
  rounds_to_approval: {plan: 3, execution: 2}
  findings_per_round:
    - {review: plan, round: 1, critical: 0, high: 1, medium: 1, low: 0}
    - {review: plan, round: 2, critical: 0, high: 1, medium: 0, low: 0}
    - {review: plan, round: 3, critical: 0, high: 0, medium: 0, low: 0}
    - {review: execution, round: 1, critical: 0, high: 1, medium: 1, low: 0}
    - {review: execution, round: 2, critical: 0, high: 0, medium: 0, low: 0}
  churned_findings: 0
  finding_categories: {contract_drift: 1, boundary_validation: 2, fix_generalization_miss: 1, claim_to_state_drift: 1}
  verdicts: {changes_required: 3, approved: 2}
meu_work_classes: [correctness]
```
