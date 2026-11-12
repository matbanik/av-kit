---
date: "2026-11-11"
project: "capture-export-copy"
meus: ["MEU-136"]
plan_source: "docs/execution/plans/2026-11-11-capture-export-copy/implementation-plan.md"
template_version: "2.0"
---

# 2026-11-11 Meta-Reflection

> **Date**: 2026-11-11 (planned in the afternoon, executed and reviewed that evening)
> **MEU(s) Completed**: MEU-136 `capture-export-copy`, the third and last session of the video stills grouping (grouping D-500 to D-505, Sessions 62 to 64). The video stills grouping is complete. `POST /api/v1/captures/{id}/export` and MCP `avkit_capture` `export` take a shot as it is shown (the annotated bake when it has saved marks, otherwise the original) and shrink it so its long edge is at most `max_edge`, never enlarging it. They encode it as PNG, JPEG or WebP at `quality` and write it into the capture inbox as a new shot with source `Export`. They only read the source's file, sidecar and bake. The 201 body gives the new shot's id, path, size and byte count. The session also ran the design's three-task description eval (grouping D-505) under Mat's D-608 A, and Mat's D-621 A accepted its two real-surface process failures as evidence for `MCP-ACTION-DESCRIPTIONS-HIDDEN-FROM-MODEL`. The session filed and resolved no issue.
> **Plan Source**: `docs/execution/plans/2026-11-11-capture-export-copy/implementation-plan.md`

---

## Execution Trace

### Friction Log

1. **What took longer than expected?**
   - **The plan review: four rounds.** All three blocking findings were about how unusual PNGs encode, and none was about the main path:
     - F1: 16-bit gray clipped to white, then a keyed 16-bit block blackened by a premultiplied resize.
     - F5: a keyed 1-bit PNG shrank to opaque grey.
     - F2: the eval checker trusted response dimensions.

     Round 1 used 9,872,742 tokens, round 2 5,087,004, round 3 6,975,453 and round 4 3,074,072. The total of 25,009,271 needed Mat's "add 50M tokens and 2 more rounds". The mode probe at plan time covered every Pillow mode unkeyed, so it missed transparency keys combined with resizing. Each correction then needed its own probe (`s64-plan-depth-probe.txt`, `s64-plan-alpha-probe-r2.txt`, `s64-plan-keynorm-probe-r3.txt`, `s64-plan-key16-probe-r3.txt`). RULE-1 adds the missing step.
   - **The eval stop (S13) at row E-4.** `eval-check.py` exited 1 with 43 PASS and 2 FAIL lines (`s64-E4-check.txt`). Also, AC-136.19's success text, "eval-check: all runs PASS", isn't a line the checker prints; it prints `eval-check: ok` (`eval-check.py:387`). D-621 went to Mat. At Mat's request an Opus subagent at xhigh weighed the options, and Mat ruled A. RULE-2 adds the missing step.
   - **Gate run 1** stopped at task-contract, because row notes sat in task.md's Status cells (`s64-gate-h1-run1.txt`). The notes moved to a separate row-notes file. Run 2 passed every step, and both receipts are kept. RULE-3 adds the missing step.

2. **What instructions were ambiguous?**
   - **AC-136.19's success line** (above). The plan quoted a checker line instead of reading it from the checker's source.
   - **The commit trailer.** The harness asks for a Co-Authored-By trailer; task H2-5 and Mat's standing rule say none. The draft has none.

3. **What instructions were unnecessary?**
   - H2-1's `view_file` row, as in Sessions 59 to 63. H2-2's check validates the reflection against the same template and schema.

4. **What was missing?**
   - **A matrix probe across mode, key, resize and format before the plan review** (RULE-1).
   - **AC text that quotes a checker's real output line** (RULE-2).
   - **A Status-cell rule.** Task Status cells hold only the bare mark (RULE-3).
   - **A dotted AC coverage check.** The handoff's AC check (`tools/validate_closeout_artifacts.py:74`, `AC_ID`) counts AC families only and reported "all 4 plan AC(s)". A dotted check written during the session found AC-135.18 missing from the handoff (`s64-H1-6a-dotted.txt`), and it was added before the review prompt (RULE-4).

5. **What did you do that wasn't in the prompt?**
   - **Consulted an independent Opus subagent at xhigh on D-621**, at Mat's request, before Mat ruled.
   - **Wrote the supplementary dotted AC check** (RULE-4).
   - **Saved each eval report from the subagent's completion notification.** The harness's subagent transcript files were empty (Departure 4).
   - **Kept every pre-edit copy** (`C:/Temp/av-kit/s64/pre-status/` and `pre-approve/`).

### Quality Signal Log

6. **Which tests caught real bugs?**
   - **Every Red failed by assertion** (Session 62 RULE-3). Row 2a had 111 failed and 148 passed (`s64-py-red-136.txt`), and row 2b had 27 failed and 145 passed (`s64-mcp-red-136.txt`). red-check found 0 problems on both.
   - **The exhaustive `Fraction` check in AC-136.2 caught a wrong clause in the test file itself.** "Orientation is kept" is false for 127×128 at edge 64, which rounds half up to 64×64. The clause became "a square stays square, no edge order flips" (Departure 1).
   - **The eval checker's decode checks** passed both real t3 JPEGs. Its selftest refused a PNG, a 16×16 JPEG and a non-image (F2's fix).
   - **The eval itself** found that, on the real surface, a model given only the one-line `avkit_capture` description skipped `image` (real-t1) and made one sheet call where two were needed (real-t2). On the meta surface, which adds each action's text, both tasks passed. This is the evidence D-608 A was designed to collect.

7. **Which tests were trivially obvious?**
   - AC-136.1's member and signature check of row 1's type-only names. It is a characterisation guard, which is its purpose.

8. **Did pyright/ruff catch anything meaningful?**
   - No. pyright had 0 errors and ruff was clean on every receipt (`s64-D6-py-types.txt`, `s64-D6-py-lint.txt`).

### Workflow Signal Log

9. **Was the FIC useful as written?**
   - Yes. Twelve mechanism ids, `EXPORT_SIZE` to `EVAL_RUN`, gave the plan, the Reds, the handoff and both reviews one contract. The execution review approved in round 1 with no finding. Session 63's three rules held: the adjacency sweep, receipt-copied counts and line-ending checks. The two pins that the plan's sweep missed moved under S9, and the handoff discloses them (Departure 9).

10. **Was the handoff template right-sized?**
    - Yes for one MEU. The cross-reference AC rows for earlier MEUs exist only for the AC check (`slim_candidate`).

11. **How many tool calls did this session take?**
    - About 879 unique tool calls in this conversation's transcript at H2-2. They cover the planning probes, the four-round plan review, execution, the eval, the execution review and closeout.

12. **Which rows were delegated, to which subagent (harness + model), and did any delegated result need rework?**
    - **No task row was delegated** to `av-kit-builder` or `av-kit-verifier`.
    - **The eval's six runs (E-3)** were six fresh Claude Code `general-purpose` subagents on Haiku, as D-608 A specifies. They are the measured subject, not delegated work.
    - **The D-621 consultation** was one Claude Code `general-purpose` subagent on Opus at xhigh, at Mat's request. It needed no rework.
    - **Codex** reviewed the plan and the execution as the independent reviewer, which isn't delegation.

### Decisions Log

| ID | Stage | Question | Resolution | Chosen | Source tag | Reasoning (why this; why the alternatives lost) | Human ref |
|----|-------|----------|------------|--------|------------|--------------------------------------------------|-----------|
| D-500 | grouping | Adopt the video stills design's slices as registered MEUs and group them? | human | Yes: MEU-133 to MEU-136, Sessions 62 to 64 | Human-approved | Mat ruled design D-1 to D-5 as recommended and said proceed to the grouping. This session executed the last slice, so the grouping is complete. | USER_EXPLICIT 2026-11-09 'all recommendations accepted, proceed' |
| D-501 | grouping | Slice to MEU mapping and dependencies | autonomous | One MEU per slice; MEU-134 and MEU-136 depend on MEU-130 | Local Canon | MEU-136 reused MEU-130's temp, lock, unique-name and register pipeline through `_crop_dest` (D-615). Two-way. | — |
| D-502 | grouping | Which slices share a session? | autonomous | S1 and S2 in Session 62; S3 and S4 alone, with the option to merge S4 into Session 63 at plan time | Local Canon | Session 63 kept S4 out (D-593), and this session ran it alone. Two-way. | — |
| D-503 | grouping | Build-plan homes, band and queue position | autonomous | MEU-133 in 08 row 8.10; MEU-134 to MEU-136 in 09 rows 9.40 to 9.42; band P2 | Local Canon | MEU-136's Delivered note went into 09 §Export copy in row 6. Two-way. | — |
| D-504 | grouping | Where do the design's planning probes run? | autonomous | Session 62's plan runs the frames probes; Session 63's plan runs the 5×5 sheet timing | Local Canon | Not touched here; this plan ran its own encode probes. Two-way. | — |
| D-505 | grouping | Where does the design's description eval run? | autonomous | Session 64's plan, after probe, frames, sheet and export exist | Local Canon | Ran in rows E-1 to E-4 under D-608 A, with the result accepted under D-621 A. Two-way. | — |
| D-608 | planning | How does the design's three-task description eval run? | human | A: six Haiku runs, the three tasks on the real surface and on the real surface plus each action's _meta text | Human-approved | The method decides what the result means and costs model tokens outside the review loop. A separates a wrong text from the hidden-text issue; B halves the cost but can't tell them apart; C leaves the tasks unproven. Two-way. | USER_EXPLICIT 2026-11-11 'accept the plan, D-608 A, execution budget 60M' |
| D-609 | planning | What happens to quality with format png? | autonomous | A: refuse it with a fixed 422 in the service, before the lock | Local Canon | A quality that does nothing would let an agent think it shrank the file; REST and MCP give one message from the service. Two-way. | — |
| D-610 | planning | What are the bounds and types of max_edge and quality? | autonomous | A: StrictInt 64 to 16383 and 1 to 100, absent allowed, null refused; target sizes past the WebP and JPEG limits refused with a fixed 422 | Research-backed | 16383 is the smallest encoder limit (`s64-probe-export.txt`), so one cap covers every format; the MCP 64.0 difference is accepted and tested. Two-way. | — |
| D-611 | planning | What does export do with a marked shot whose bake is missing, or a malformed sidecar? | autonomous | A: the existing 404 from _variant_path and crop's 422 | Local Canon | Exporting the original would drop the marks the agent asked to show; re-baking would write the source's bake. Two-way. | — |
| D-612 | planning | How is the export's stem made? | autonomous | A: the source stem filtered as import_stem filters, cut to 100, plus -export; empty gives export | Local Canon | Scanned stems can hold any character, including lone surrogates; the reviewer's unsafe-stem probes held. Two-way. | — |
| D-613 | planning | What metadata and orientation does an export keep? | autonomous | A: keep the ICC profile, drop EXIF, XMP and text, keep the stored frame | Local Canon | As crop does; AC-136.7 records CAPTURE-EXIF-SCANNED-ORIENTATION's effect without fixing it. Two-way. | — |
| D-614 | planning | How does the adapter encode, and what are its failure texts? | autonomous | A: one port method with per-mode conversion, JPEG to RGB before resize, keys made exact alpha before LANCZOS and corrected from the IHDR, fixed texts | Local Canon | Three plan-review rounds (F1, F5) shaped it; every probe in its precedents holds, and the execution review's 65,536-value and metadata probes passed. Two-way. | — |
| D-615 | planning | How does the copy name take a suffix other than .png? | autonomous | A: _crop_dest gains a keyword ext defaulting to the PNG suffix | Local Canon | One taken rule for every suffix; crop's behaviour is unchanged, which AC-136.3 checks. Two-way. | — |
| D-616 | planning | How is export wired into MCP and the audit? | autonomous | A: after sheet everywhere, the 120 s ADD_TIMEOUT_MS, pending baseline, an offline audit step after sheet that depends on crop | Local Canon | A full-size WebP at Pillow's edge took 82.53 s, past the 30 s default; --update-baseline needs Mat's words. Two-way. | — |
| D-617 | planning | Does MEU-136 add a UI action or an Electron E2E? | autonomous | A: no; this corrects D-593's reasoning | Local Canon | Neither 09 nor the grouping asks for UI; a button is new scope Mat hasn't asked for. Two-way. | — |
| D-618 | planning | What are the source member, the response and the log line? | autonomous | A: CaptureSource.Export with no register wire value; 201 with shot id, path, width, height, bytes and source_id; log with ids only | Research-backed | 09 names the shape; bytes from stat lets an agent see an export larger than it wanted; no path in the log (NO_RAW_OUTPUT). Two-way. | — |
| D-619 | planning | How does export encode a 16-bit gray source? | autonomous | A: map to 8 bits by v times 255 over 65535 rounded half up; keys become exact alpha for webp and resized png; PNG otherwise keeps I;16 | Research-backed | A direct convert clips midtones to white (plan review F1); the map matches the integer formula on all 65,536 values. Two-way. | — |
| D-620 | planning | What does export's MCP schema say about an unknown key? | autonomous | A: a fixed EXPORT_UNKNOWN_KEY for unrecognized keys only | Research-backed | A bare strict object echoes the key, which can hold a path (plan review F4); the other strict actions are raised, not changed. Two-way. | — |
| D-621 | execution | Row E-4 eval-check exits 1: real-t1 makes no image call and real-t2 one sheet call where two are needed, while all six answers are right. What does AC-136.19 accept? | human | A: amend AC-136.19 to cite the exit-1 receipt as it stands, every t3 and meta line passing, the two real-surface process lines recorded as evidence for MCP-ACTION-DESCRIPTIONS-HIDDEN-FROM-MODEL | Human-approved | B reruns until a pass with nothing changed; C changes text inside a known issue left out of scope; D blocks MEU-136 although export passed on both surfaces. An Opus subagent at xhigh, consulted at Mat's request, recommended A. Two-way. | USER_EXPLICIT 2026-11-11 'A' |

---

## Pattern Extraction

### Patterns to KEEP
1. **Measuring at plan time before writing a contract.** The 3,060,000-case `EXPORT_SIZE` probe, the 65,536-value depth probe and the 82.53 s cap probe each set a contract that execution didn't have to revisit, and the execution review approved in round 1.
2. **A human-ruled eval method with a stated reading of each outcome** (D-608 A). When the eval failed on the real surface only, the plan already said what that meant, so D-621 was a short decision, not a redesign.
3. **Pre-edit copies and byte edits for status files.** `meu_status.py update` re-wrapped MEU-137 to MEU-142 again in row 6 and was discarded (Departure 5). The diffs at H2-2 hold only MEU-136's fields and the derived Total (`s64-approve-diff.txt`).

### Patterns to DROP
1. **Quoting a checker's success line from memory in an AC.** Read the line from the checker's source (RULE-2).

### Patterns to ADD
1. **A matrix probe across mode, key, resize and format before an image-encode plan goes to review** (RULE-1).
2. **Bare marks in task Status cells, with notes in a row-notes file** (RULE-3).
3. **A dotted AC coverage check beside the validator's family check** (RULE-4).

### Calibration Adjustment
- **Estimated:** the plan opened its review loop at 3 rounds; Mat added 50M tokens and 2 rounds. Mat set execution at 60M over 6 rounds.
- **Actual time (local time, UTC-5), all 2026-11-11:**
  - The planning probes ran at 14:51. The plan review dispatched round 1 at 15:15 and approved in round 4 at 17:55.
  - Mat's "accept the plan, D-608 A, execution budget 60M" came before the 19:06 baseline. The Python Red ran at 19:26, the MCP Red at 19:31 and the Green at 19:40.
  - The eval check (E-4) ran at 19:52, and Mat's D-621 ruling followed.
  - Gate run 1 stopped at 20:13. Run 2 passed at 20:19, and the execution review returned approved at 20:46.
- **Tokens:**
  - plan review: 25,009,271 over four rounds;
  - execution review: 9,796,997 in one round of 60,000,000;
  - the eval: six Haiku runs and one Opus consultation, outside the Codex ledger.
- **Adjusted estimate for a one-MEU image-encode session across formats:** budget 4 plan rounds (about 25M) unless the RULE-1 matrix probe runs before round 1, then about 10M. Budget about 10M for execution round 1.

---

## Next Session Design Rules

```
RULE-1: A plan that encodes or converts images across formats runs, before its first review, a matrix probe over every source mode the inbox can hold × with and without a transparency key or alpha × resized and unresized × every output format, and asserts decoded pixels (alpha and stored colour on keyed and unkeyed blocks), not only that the save succeeds.
SOURCE: Plan review rounds 1 to 3. F1 (16-bit gray clipped, then a keyed block blackened by a premultiplied resize) and F5 (a keyed 1-bit PNG shrank to opaque grey) each needed a new probe; the plan-time mode probe covered modes unkeyed and unresized.
EXAMPLE: "s64-plan-mode-probe.txt: every mode resizes and encodes" becomes "mode × key × resize × format matrix: alpha and colour of a keyed block and an opaque block in each decoded output".
```

```
RULE-2: An AC that names a checker's or tool's output quotes the exact line that the checker prints, copied from its source with file:line, and states the expected exit code.
SOURCE: Row E-4 (S13). AC-136.19 said "eval-check: all runs PASS", but eval-check.py:387 prints "eval-check: ok", so the AC could not be met as written even on a full pass.
EXAMPLE: "eval-check: all runs PASS" becomes "eval-check: ok, exit 0 (eval-check.py:387)".
```

```
RULE-3: A task.md Status cell holds only its bare mark ([ ], [/], [x] or [B]). A row's receipts, counts and departures go to a separate row-notes file that the handoff cites.
SOURCE: Gate run 1 stopped at task-contract because row notes sat in the Status cells (s64-gate-h1-run1.txt); run 2 passed after they moved.
EXAMPLE: "| [x] s64-py-red-136.txt 111 failed |" becomes "| [x] |", with the receipt in C:/Temp/av-kit/s64/row-notes.md under "Row 2a".
```

```
RULE-4: Before the review prompt, a plan-local check lists every dotted AC id the plan cites (AC-N.M) and proves each has a row in the handoff's AC table, beside the validator's --ac-coverage-only check, which counts AC families only.
SOURCE: H1-6a. The validator (tools/validate_closeout_artifacts.py:74) reported "all 4 plan AC(s)"; the dotted check found AC-135.18, cited in AC-136.17 as a precedent, missing from the handoff.
EXAMPLE: "OK: all 4 plan AC(s) present" alone becomes that line plus "plan dotted ACs: 25; missing from handoff: []" (s64-H1-6a-dotted.txt).
```

---

## Next Day Outline

1. **Target:** done in the tree, not committed. MEU-136 is approved, and the video stills grouping is complete. The commit waits on Mat's words.
2. **Next session:** Session 65 `download-failure-visibility` (MEU-137 to MEU-139), the first session of the download reliability grouping. Its prompt is `C:/Temp/av-kit/session-65-prompt.md`.
3. **Scaffold changes needed:** none. The validator's family-only AC count (RULE-4) is worth raising with Mat as a tooling item.
4. **Patterns to bake in from today:** RULE-1 to RULE-4 here, plus the rules carried from Sessions 50 to 63.
5. **Codex validation scope:** Session 65's plan, then its execution.
6. **Time estimate:** set by the Session 65 plan. Its calibration is Session 50 `transcript-failure-reason` and Session 55 `download-received-quality`.

---

## Efficiency Metrics

| Metric | Value |
|--------|-------|
| Total tool calls | About 879 unique tool calls in this conversation's transcript at H2-2, from planning on |
| Time to first green test | MEU-136's Green at 2026-11-11 19:40 (UTC-5), 14 minutes after its Python Red (`s64-py-red-136.txt`, `s64-py-green-136.txt`) |
| Tests added | pytest 1999 to 2108 (+109; `s64-base-py.txt`, `s64-D6-py-tests.txt`); MCP 508 to 520 (+12; `s64-base-mcp.txt`, `s64-D6-mcp-tests.txt`) |
| Codex findings | Plan review: R1 changes_required (F1 to F4: 2 High, 2 Medium); R2 F1 partial; R3 F5 High; R4 approved (25,009,271). Execution review: R1 approved, 0 findings (9,796,997 of 60,000,000) |
| Handoff Score (X/7) | 6/7. Every AC has evidence, and the execution review approved in round 1. Gate run 1 stopped on the Status cells, and AC-135.18 was added only after the dotted check. The approval write changed `meu-status.yaml`, `meu-registry.md` and `BUILD_PLAN.md` after the gate, so `render --check` and the two status-canon UI tests ran again at H2-2 |
| Rule Adherence (%) | 89 (17 of 19 sampled rules followed in full, 2 in part) |
| Prompt→commit time | Planned and executed 2026-11-11; not committed, waiting on Mat |

### Rules Sampled for Adherence Check

| Rule | Source | Followed? |
|------|--------|-----------|
| Tests before production code; Red before Green | AGENTS.md §Testing & TDD | Yes. Rows 2a and 2b failed by assertion before row 3 |
| Independent review; no self-approval | AGENTS.md §Dual-Agent Workflow | Yes. Both canonical reviews are Codex's reports, validated under `C:/Temp/av-kit` and copied byte for byte |
| Human decisions stay human, with a brief and a do-nothing option | `.agent/docs/human-decision-protocol.md` | Yes. D-608 at the plan gate; D-621 at row E-4 with option D as the status quo |
| A raw value that can reach a log, stdout or the Console is fixed or raised | Session 50 rule | Yes. NO_RAW_OUTPUT; the export log holds ids only, and EXPORT_UNKNOWN_KEY hides caller keys (D-620) |
| Outside text gets lone-surrogate, control-character and empty regressions | Session 53 RULE-1 | Yes. `export_stem`'s tests (EXPORT_NAME) |
| Shared missing names go in a type-only row first | Session 53 RULE-2 | Yes. Row 1 |
| Handoff checks before the review prompt; every cited AC has a row | Session 54 RULE-3 | Yes. H1-6 to H1-6b and the dotted check passed before the dispatch |
| List and run the callers of anything extended | Session 55 RULE-1 | Yes. `_crop_dest`'s callers; `s64-r3-callers.txt` and the real-FFmpeg suite |
| Temps opened with xb; another writer's temp is left | Session 58 rule | Yes. AC-136.10 and .11 |
| A departure from an approved contract is recorded before the gate | Session 59 rule | Yes. Departures 1 to 9 in row notes before H1-2 |
| One integer construction for max_edge | Session 60 RULE-1 | Yes. EXPORT_SIZE |
| Check the path list before an identity run | Session 60 RULE-4 | Yes. The gate's scope-paths step and H1-6b's status listing |
| Byte-edit a status file another session may hold dirty | Session 61 RULE-5 | Yes. Rows 6 and H2-2 byte-edited MEU-136's fields and proved them with render |
| Inventory every blocking call on a deadline path | Session 62 RULE-1 | Yes. Handoff §Deadline inventory, five categories |
| Magnitude bounds tested at 1e308, a huge negative and just past the cap | Session 62 RULE-2 | Yes. AC-136.14's schema negatives |
| Each Red fails by assertion | Session 62 RULE-3 | Yes. red-check found 0 problems on both Red receipts |
| Sweep adjacency pins in every test file | Session 63 RULE-1 | Partly. Two pins outside the plan's list moved in row 2b (Departure 9) |
| Counts in handoff prose copied from the receipt | Session 63 RULE-2 | Yes. Each count names its receipt |
| Every command through RTK | AGENTS.md §RTK | Partly. Tests, gates, tools and dispatches went through `rtk proxy`; many reads and scratch scripts did not |

---

## Instruction Coverage

```yaml
schema: v1
session:
  id: "545db8e7-4bdb-459c-9833-71e9cc68366b"
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
decisive_rules: [P0:never-commit-or-push-without-human-approval, P0:human-decisions-stay-human, P0:raw-values-fixed-or-raised, P1:independent-review-no-self-approval, P1:tests-before-production-code]
conflicts:
  - "The harness asks for a Co-Authored-By trailer on commits; task H2-5 and Mat's rule say no AI attribution trailer. The draft has none."
  - "Connected docs and artifact tools offered to publish deliverables; the user's rule keeps them as local repo files."
note: "An agent exports a shot as a small PNG, JPEG or WebP copy; the video stills grouping's last session, with its description eval."
slim_candidate: ["The handoff's cross-reference AC rows for earlier MEUs exist only for the AC check.", "H2-1's view_file row repeats what H2-2's validator checks."]
overthinking_observed: false
review_churn:
  rounds_to_approval: {plan: 4, execution: 1}
  findings_per_round:
    - {review: plan, round: 1, critical: 0, high: 2, medium: 2, low: 0}
    - {review: plan, round: 2, critical: 0, high: 1, medium: 0, low: 0}
    - {review: plan, round: 3, critical: 0, high: 1, medium: 0, low: 0}
    - {review: plan, round: 4, critical: 0, high: 0, medium: 0, low: 0}
    - {review: execution, round: 1, critical: 0, high: 0, medium: 0, low: 0}
  churned_findings: 1
  finding_categories: {weak_test: 2, contract_drift: 1, boundary_validation: 1, other: 1}
  verdicts: {changes_required: 3, approved: 2}
meu_work_classes: [correctness]
```
