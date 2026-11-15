---
date: "2026-11-14"
project: "tts-fp16-phase-guard"
meus: ["MEU-127"]
plan_source: "docs/execution/plans/2026-11-14-tts-fp16-phase-guard/implementation-plan.md"
template_version: "2.0"
---

# 2026-11-14 Meta-Reflection

> **Date**: 2026-11-14 to 2026-11-15. Planned on 2026-11-14; executed, reviewed and closed after midnight, on 2026-11-15.
> **MEU(s) Completed**: MEU-127 `svc-tts-fp16-phase-guard`, Session 73 `tts-fp16-phase-guard`, band P2, matrix row 3.18, in no grouping (D-789). It is the spike that 03 §TTS FP16 phase guard (residual) asks for, and it changes no product code.
>
> - **The cause, counted (DENOM_COUNT).** In the 12 of 149 jobs that fail today, `/decoder/decoder/generator/Div` divides 0 by 0 at 14 slots, all in frequency bin 10. Each gives a NaN phase and 1,981,200 non-finite samples in all. The 137 passing jobs have no such slot (`s73-count.json`).
> - **The guard (PHASE_GUARD, PATCH_COPY, D-793).** `IsNaN` and `Where` after the `Div` turn a NaN quotient into FP16 +0, written only into a copy: 2,490 nodes to 2,492, SHA-256 `9037c82b…6fd33` (`s73-patch.json`).
> - **The measurements.** In ONNX Runtime the guard changes exactly the 12 failing jobs and leaves 137 bit-identical (GRAPH_COMPARE). On one packaged build the original FP16 fails the same 12 as Session 52, the guarded FP16 passes 149 of 149 and INT8 passes 149 of 149 (SENTENCE_SMOKE). The 137 WAVs are byte-identical between the control and guarded runs (WAV_IDENTITY).
> - **The inputs (FRESH_INPUTS, INSTALLED_READ, D-790, D-791, D-798).** Row 0b downloaded the seven inputs at the app's pins, and each equals Session 52's cached copy. Six installed files equal it too; the installed INT8 graph is absent.
> - **The outcome (OUTCOME_BRIEF, LISTEN_FOLDER, D-797).** Mat listened to the 12 pairs and ruled "Ship guarded (Recommended)". How it ships is a plan amendment with its own Red and review. `TTS-ONNX-FP16-NONFINITE-AUDIO` stays open until it lands.
>
> **Plan Source**: `docs/execution/plans/2026-11-14-tts-fp16-phase-guard/implementation-plan.md`

---

## Execution Trace

### Friction Log

1. **What took longer than expected?**
   - **The plan review took three rounds, and two of them were caused by the gate.** Round 1 approved the plan as written with no findings (5,567,072 tokens). At the gate, Mat answered D-790 and D-791 "Download and read", against the recommendation. Amendment 1 (D-798) added row 0b and `fresh-inputs.py`, and the loop resumed.
     - Round 2 (6,510,974) found F1, High: an inherited `HF_HUB_CACHE` overrides a private `HF_HOME`, so the Hub client could copy all seven bodies from a shared cache and pass every row 0b check without downloading anything. That would have defeated Mat's ruling.
     - Round 3 (6,778,006) rechecked F1 `fixed` and approved at the cap, 3 of 3.
     RULE-2.
   - **The execution review's one finding was a privacy leak in a receipt, not in the work.** `tools/package_backend.py` prints the build's module search paths, so `s73-build.txt` and `s73-D6-package-build.txt` held the raw home prefix in five lines each, against the plan's S6. The redaction ran on the receipts only, and the tested_state did not move. Round 1 cost 10,284,202 tokens; round 2 approved at 3,365,841. RULE-1.
   - **D-800.** The F1 rescan found the same prefix in reviewer scratch files from the plan-review dispatches. The brief said four files; the scan listed five. Mat ruled to redact all of them in place. RULE-3.

2. **What instructions were ambiguous?**
   - **03's "so it no longer divides by them".** PHASE_GUARD maps the quotient after the `Div`, so the division still runs. Mat ruled the reading "so their division no longer reaches the phase" at D-793.
   - **AC-127.10's AC range.** It says 03's note names AC-127.1 to AC-127.11, but Amendment 1 added AC-127.12, so the note names all twelve (handoff note 5).
   - **The commit trailer.** The harness asks for a Co-Authored-By trailer. Task H2-5, `.agent/docs/development-lifecycle.md:454` and Mat's standing rule say there is none, so the commit draft has none.

3. **What instructions were unnecessary?**
   - H2-1's `view_file` row, as in Sessions 59 to 72. H2-2's check validates the reflection against the same template and schema.
   - The handoff's cross-family AC rows (AC-121.7, AC-121.8), which exist so the handoff check accepts the table. Here they did name the Session 52 Red that row 5 repeats, so they carried some meaning.

4. **What was missing?**
   - **A home-path scan of every cited receipt before the execution dispatch** (RULE-1). The plan's S6 named the rule, but no row checked it, and the reviewer found the leak.
   - **A real-client regression for inherited environment overrides in any download step** (RULE-2). The plan's offline selftest checked 32 cases, but none set `HF_HUB_CACHE`.
   - **A count taken from the scan receipt when a brief names files** (RULE-3).

5. **What did you do that wasn't in the prompt?**
   - **Wrote `s73-home-scan.py`** to scan the named receipts, the row scripts, the plan folder and both handoffs for the home prefix, and to redact by byte replacement with an endings check (`s73-f1-scan-before.txt`, `s73-f1-redact.txt`, `s73-f1-scan-after.txt`, `s73-d800-scan-after.txt`).
   - **Scanned the tracked files for the same prefix** (`s73-tracked-home-scan.txt`). About 24 tracked files hold it, all from the initial commit `6c11ef3`. They are outside this plan's scope and were not changed; the Session 74 prompt carries them to Mat as a decision.
   - **Wrote `s73-decision-probe-close.py`**, which runs `decision_sources` on the plan, the handoff and the register entry (`s73-closeout-decision-probe.txt`). It returns 13 ids: D-239 `triage`, D-789 to D-796 and D-798 `planning`, and D-797, D-799 and D-800 `execution`. D-336 and D-345 come from Session 52's reflection and are carried by hand.
   - **Set MEU-127 to `approved`** through `tools/meu_status.py update` and `render`, after copying the three status files to `s73/pre-approve/`. The diff (`s73/approve-diff.txt`) changes only MEU-127's entry and row, plus three rendered rows of `BUILD_PLAN.md`: Phase 3 reads Completed, P2 counts 130 of 130 and the Total reads 142 plus 1 blocked. MEU-127 was Phase 3's last open MEU, so these are derived from its status, as D-799 found for the Total row.

### Quality Signal Log

6. **Which tests caught real bugs?**
   - **The plan review's round 2 F1** caught a download step that could pass without downloading. Codex proved it with a no-network probe that copied all seven bodies from a fixture cache. The fix confines every client cache inside the private home, drops inherited HF variables before the client loads and forces each body download; two mutants that fail the real-client regression pin it (`s73-plan-fresh-mutants.txt`).
   - **The control smoke (row 5)** proved the build wasn't the variable: its failure set equals Session 52's (`equal_s52 True`), so the guarded run's 149 of 149 is the guard's doing.
   - **WAV_IDENTITY (row 8)** proved "changes nothing else" at the byte level on the packaged backend, not only in ONNX Runtime.
   - **The execution review's F1** caught the receipt leak above.

7. **Which tests were trivially obvious?**
   - The INT8 reference smoke (row 7) passed 149 of 149, as Session 52's did. It is there so the listening pairs have an INT8 half and the brief can compare speeds, which it did.

8. **Did pyright/ruff catch anything meaningful?**
   - No. The gate shows pyright `0 errors, 0 warnings, 0 informations` and ruff `All checks passed!` on the plan's scripts (`s73-D6-py-types.txt`, `s73-D6-py-lint.txt`, `s73-D6-plan-lint.txt`, `s73-D6-plan-lint-copies.txt`). ruff is narrowed to the plan's files, because `ruff check tools/` fails at baseline (Session 68 DEP-1).

### Workflow Signal Log

9. **Was the FIC useful as written?**
   - Yes. The eleven mechanism ids, from PHASE_GUARD to OUTCOME_BRIEF, gave the plan, the rows, the brief, the handoff and both reviews one vocabulary. Codex's eight execution answers each name the mechanisms they checked.
   - The spike shape held: no product Red, a control smoke as the Red of 03's Tests rule and the guarded smoke on the same build as its Green.

10. **Was the handoff template right-sized?**
    - Mostly. For a spike with no product code, the FAIL_TO_PASS table needs a sentence explaining why the Red is a control smoke. The Where values go table was the most useful section for the reviewer (`slim_candidate` for the empty product sections).

11. **How many tool calls did this session take?**
    - 574 unique tool calls in this conversation's transcript when this reflection was written. They cover planning, the three-round plan review, execution, the two-round execution review, D-800 and closeout.

12. **Which rows were delegated, to which subagent (harness + model), and did any delegated result need rework?**
    - **No task row was delegated** to `av-kit-builder` or `av-kit-verifier`.
    - **D-789, D-790, D-791 and D-793 went to Mat** at the plan gate, D-797 at row 9 and D-800 after the execution review, each as an HDP brief.
    - **Codex** reviewed the plan and the execution as the independent reviewer, which isn't delegation.

### Decisions Log

| ID | Stage | Question | Resolution | Chosen | Source tag | Reasoning (why this; why the alternatives lost) | Human ref |
|----|-------|----------|------------|--------|------------|--------------------------------------------------|-----------|
| D-239 | triage | Which model does a fresh install preselect while ONNX FP16 fails on some ordinary sentences? | human | ONNX INT8 or ONNX FP32 until the cause is known; nothing removes or disables FP16 | Human-approved | Carried from the register entry's own decision log. This session keeps FP16 offered and never preselected; the guarded graph ships only through the amendment D-797 names. Two-way. | USER_EXPLICIT 2026-11-04 'All ohter recommendations are accepted' |
| D-336 | execution | What happens to ONNX FP16, now that Session 52's spike found where it fails? | human | Keep FP16 as shipped; the issue stays open; MEU-127 takes a guarded phase computation, spike first; nothing is posted to discussion 22 | Human-approved | Carried by hand from Session 52's reflection. It set 03's Spike first, FP16 stays, Upstream and Outcome rules that this session ran under. Two-way. | USER_EXPLICIT 2026-11-07 'all recommendations accepted' |
| D-345 | closeout | Where is D-336's follow-up registered? | autonomous | MEU-127 svc-tts-fp16-phase-guard, phase 3, band P2, matrix row 3.18 | Local Canon | Carried by hand from Session 52's reflection; it is the registration this session executes. Two-way. | — |
| D-789 | planning | Does MEU-127 run alone, or join other work in a grouping? | human | One MEU in one session, no grouping | Human-approved | The spike changes no product code and its outcome is a ruling, so nothing else can share its rows. No grouping names it. Do nothing kept MEU-127 pending. Two-way. | USER_EXPLICIT 2026-11-14 plan gate, answer 'Alone (Recommended)' |
| D-790 | planning | Which model and build inputs does the spike use? | human | Download, against the recommendation: row 0b downloads the seven inputs at the app's pins, each must equal Session 52's cached copy, and rows 1 to 8 run on the downloaded bytes | Human-approved | The recommendation was the cached copies, since each already had a known hash. Mat ruled for the download; D-798 records how it runs, and S18 stops on a different file. Two-way. | USER_EXPLICIT 2026-11-14 plan gate, answers 'Download or read' and then 'Download and read' |
| D-791 | planning | Does any row read user data: the installed models, the app database or the settings file? | human | Read, against the recommendation: row 0b hashes the same seven installed files, read only, by exact path; no row reads the database or the settings file | Human-approved | The recommendation was no read, since the cached files equal the user's by hash. Mat ruled for the read; D-798 limits it to the seven files and to hashing. Two-way. | USER_EXPLICIT 2026-11-14 plan gate, answers 'Download or read' and then 'Download and read' |
| D-792 | planning | What does row 10 write to TTS-ONNX-FP16-NONFINITE-AUDIO, and how is known-issues.md refreshed? | autonomous | root_cause becomes the found cause; verification records the method and result; resolution_path and status follow D-797; known-issues.md through issue_triage.py render only | Local Canon | The register should say what the spike found, whatever ships. Closing the issue lost: the user's FP16 file is unchanged until a fix ships. triage lost: it rewrites a file outside scope. Two-way. | — |
| D-793 | planning | Which guard does the spike test, and does it meet 03's wording? | human | PHASE_GUARD, IsNaN and Where after the Div, mapping only a NaN quotient to +0; 03 read as 'so their division no longer reaches the phase' | Human-approved | The measured guard changes only the 14 NaN slots, to the value atan2 of 0 and 0 has in Annex F, fdlibm and torch. An epsilon lost: it changes passing jobs. Replacing every zero denominator lost: it breaks the right plus or minus pi over 2 answers. Two-way. | USER_EXPLICIT 2026-11-14 plan gate, answer 'PHASE_GUARD (Recommended)' |
| D-794 | planning | Which onedir and which control does execution use? | autonomous | One fresh onedir built at row 1 from HEAD, copied once per run; a control FP16 smoke on the same build whose failure set must equal Session 52's | Local Canon | A control on the same build shows that the guard, not the build, changes the result. Reusing Session 52's onedir lost: the tree has moved. One shared run folder lost: each run deletes the last one's output. Two-way. | — |
| D-795 | planning | What goes in the listening folder? | autonomous | The 12 control-failed jobs, each as a guarded FP16 and INT8 pair, numbered by job, with listen.txt | Local Canon | Only the 12 jobs sound different from today's FP16, and INT8 is the fresh-install default. All 149 lost: 137 are byte-identical to today's output. Two-way. | — |
| D-796 | planning | What does the session gate run? | autonomous | The Python static checks and suite, the task lint, scope-paths, three selftests, two renders and AC-127.6's smoke again on fresh copies; UI and MCP skipped with a reason | Local Canon | No file under ui, mcp-server or packages changes, so their suites prove nothing new. Reformatting the copied scripts lost: they would no longer diff against their sources. Two-way. | — |
| D-797 | execution | What ships from the FP16 phase guard spike, the guarded graph or nothing? | human | Ship the guarded graph through a plan amendment with its own Red and review; FP16 stays never preselected; the issue stays open until the fix lands; nothing posted upstream | Human-approved | A two-node guard fixes all 12 failing jobs and changes none of the 137 others, on the packaged build at the same speed. Ship nothing lost on those measurements. Do nothing held rows 9 and 10. Brief in closeout-decisions.md. Two-way. | USER_EXPLICIT 2026-11-15 row 9, answer 'Ship guarded (Recommended)' |
| D-798 | planning | How does the plan carry out the D-790 and D-791 ruling? | autonomous | Amendment 1: row 0b runs fresh-inputs.py with no token, a private HF_HOME holding every client cache, inherited HF variables dropped, force_download on every file; installed files hashed by exact path; stop on any difference | Local Canon | The app's own pins decide what is fetched. Equality with Session 52's copies keeps every plan-time value. Trusting HF_HOME alone lost: plan review round 2 F1 showed an inherited cache overrides it. Two-way. | — |
| D-799 | execution | Does BUILD_PLAN's Total row change break 'only MEU-127's entry and rows may change'? | autonomous | No: the Total row is rendered from the status counts, and its one change is MEU-127 moving to ready_for_review | Local Canon | S11 guards against another MEU's entry changing; a total derived from MEU-127's own status is part of its change. Hand-restoring the old total lost: render check would fail. Two-way. | — |
| D-800 | execution | What happens to the five plan-review scratch files that still hold the raw home prefix after F1? | human | Redact them in place by byte replacement, as the F1 receipts were, and the HDP sweep receipt with them | Human-approved | Redaction keeps what Codex saw and removes the only personal value. Leaving them kept the path; deleting them could not be undone. The brief said four files; the scan lists five, and the ruling covers all. s73-d800-scan-after.txt reads hits 0 over 273 files. Two-way. | USER_EXPLICIT 2026-11-15 'D-800: recommendation accepted' |

The outcome ruling is D-797, the input rulings D-790 and D-791 as carried out by D-798, and the guard D-793. Mat ruled D-790 and D-791 against the recommendation; both are recorded as ruled.

---

## Pattern Extraction

### Patterns to KEEP
1. **A control smoke on the same build as the Red, with its failure set pinned to the earlier session's** (D-794). It separated the guard's effect from the build's.
2. **Byte identity of every unchanged output, at two levels** (GRAPH_COMPARE in ONNX Runtime, WAV_IDENTITY on the packaged backend). "Changes nothing else" was measured, not argued.
3. **A listening folder of pairs, only for the jobs that change** (D-795). Mat ruled D-797 after 12 pairs, not 149 clips.
4. **Receipt-only correction when a finding is about a receipt.** Redacting the receipts and proving the tested_state unchanged kept round 2 to a 3.4M recheck.

### Patterns to DROP
1. **Naming a receipt rule (S6) in the plan without a row that checks it.** The reviewer found the leak.
2. **Counting files for a brief by memory.** The D-800 brief said four; the scan said five.

### Patterns to ADD
1. **Redact build and tool output at write time, and scan every cited receipt before the execution dispatch** (RULE-1).
2. **A real-client regression for every inherited environment override in a download step** (RULE-2).
3. **Copy every count in a brief from its scan receipt** (RULE-3).
4. **Estimate a no-product-code spike from this session's figures** (RULE-4).

### Calibration Adjustment
- **Estimated:** about 15M tokens for the first execution round and about 7.5M for each recheck (plan §User Review Required). The plan review had no token budget.
- **Actual time (local time, UTC-5):**
  - Plan review round 1 at 22:38 on 2026-11-14; round 2 at 23:55; round 3 approved at 00:07 on 2026-11-15.
  - The baseline ran at 00:13 and row 0b at 00:14. The control Red finished at 00:23:40 and the guarded Green at 00:26:27; INT8 and the WAV identity by 00:29.
  - Mat ruled D-797 by 00:32; row 10 at 00:34; the H1-2 gate passed on its first run at 00:42.
  - Execution round 1 returned at 00:58; the F1 redaction at 01:02; round 2 approved at 01:09. D-800's redaction finished at 01:12.
- **Tokens:**
  - plan review: 5,567,072, 6,510,974 and 6,778,006 over three rounds, 18,856,052 in all;
  - execution review: 10,284,202 and 3,365,841 over two rounds, 13,650,043 in all, against an estimate of about 22.5M for two rounds.
- **Adjusted estimate for a one-MEU spike with no product code:** about 6M for the first plan round, about 6.5M per amendment or recheck round, about 10M for the first execution round and about 3.5M for a receipt-only recheck (RULE-4).

---

## Next Session Design Rules

```
RULE-1: A plan whose rows save the output of a build or tool that prints environment paths (package_backend.py prints the module search paths) redacts the home prefix when the receipt is written, and H1-6 scans every receipt a record cites for the raw home prefix before the execution review dispatch.
SOURCE: Execution review round 1 F1: s73-build.txt and s73-D6-package-build.txt held the raw home prefix in five lines each, against S6.
EXAMPLE: the build row pipes its output through a redaction filter into s74-build.txt, and the pre-dispatch scan reads hits 0 before the prompt is sent.
```

```
RULE-2: A row that downloads through a client library proves at plan time, with the real client and no network, that every inherited environment variable that can redirect its cache or endpoint (HF_HUB_CACHE, HUGGINGFACE_HUB_CACHE, HF_XET_CACHE, offline and endpoint aliases) is dropped or refused, and that each body is fetched, not copied.
SOURCE: Plan review round 2 F1: an inherited HF_HUB_CACHE overrode the private HF_HOME, so the client copied all seven bodies from a shared cache and row 0b passed without a download.
EXAMPLE: the selftest sets HF_HUB_CACHE to a fixture cache holding the seven files, and the run must refuse or download all seven again.
```

```
RULE-3: A Decision Brief that counts files, rows or hits copies the number from the scan receipt it cites, and names that receipt next to the number.
SOURCE: D-800: the brief said four scratch files; s73-f1-scan-after.txt listed five.
EXAMPLE: "five files (s73-f1-scan-after.txt)" instead of "four files".
```

```
RULE-4: A one-MEU spike that changes no product code estimates about 6M for the first plan round, about 6.5M per amendment or recheck round, about 10M for the first execution round and about 3.5M for a receipt-only recheck.
SOURCE: Session 73: plan rounds 5.57M, 6.51M and 6.78M; execution rounds 10.28M and 3.37M against an estimate of 15M and 7.5M.
EXAMPLE: the D-797 amendment adds a product Red and Green, so its estimate starts from Session 72's RULE-5 figures, not these.
```

---

## Next Day Outline

1. **Target:** done, pending Mat's commit. MEU-127 is approved.
2. **Next session:** Session 74. The first candidate is the D-797 ship amendment: how the guarded graph reaches a user who picks FP16, with its own research, Red, review and listening check. The prompt is `C:/Temp/av-kit/session-74-prompt.md`.
3. **Scaffold changes needed:** none.
4. **Patterns to bake in from today:** RULE-1 to RULE-4 here, plus the rules carried from Sessions 50 to 72.
5. **Codex validation scope:** the next session's plan, then its execution.
6. **Time estimate:** set by the next session's plan; see RULE-4 and Session 72's RULE-5.
7. **Still open:**
   - **The tracked files that hold the raw home prefix.** About 24 tracked files, all from the initial commit `6c11ef3` (`s73-tracked-home-scan.txt`). They are outside this session's scope; whether to redact them is Mat's decision, carried in the Session 74 prompt.
   - **The two clipboard Electron specs**, `capture-filmstrip-actions.test.ts` and `capture-import.test.ts`, were not run, because they write the real clipboard. Running them is Mat's call.
   - **The ruff baseline in `tools/`.** Errors in `tools/issue_triage*` and `tools/meu_status*` predate Session 68 (its DEP-1).
   - **The plan's goal anchor** (`implementation-plan.md:20`) uses a gendered pronoun for Mat. It is the registered ledger anchor, so it stays verbatim; later anchors should not.

---

## Efficiency Metrics

| Metric | Value |
|--------|-------|
| Total tool calls | 574 unique tool calls in this conversation's transcript when this reflection was written, from planning on |
| Time to first green test | The guarded smoke passed at 2026-11-15 00:26:27 (UTC-5), 2 min 47 s after the control Red (`s73-smoke-control.json`, `s73-smoke-guarded.json`) |
| Tests added | None in the product suites: pytest 2781 at baseline and at the gate (`s73-base-py.txt`, `s73-D6-py-tests.txt`). The plan folder's tooling carries its own selftests: phase-guard 24 checks, fresh-inputs 32 cases, identity 0 failures |
| Codex findings | Plan review: R1 approved with 0 findings, R2 changes_required (F1 High), R3 approved (18,856,052). Execution review: R1 changes_required (F1 High), R2 approved (13,650,043) |
| Handoff Score (X/7) | 6/7. Every AC has evidence and the gate passed first time, but a cited receipt held the raw home prefix until round 1 found it |
| Rule Adherence (%) | 81 (13 of 16 sampled rules followed in full, 3 in part) |
| Prompt→commit time | Planned 2026-11-14; executed, approved and closed 2026-11-15; commit pending Mat's words |

### Rules Sampled for Adherence Check

| Rule | Source | Followed? |
|------|--------|-----------|
| No product code changes in a spike | 03 Spike first; plan S1 | Yes. H1-4 reads no_product True; no path under packages, ui, mcp-server, tools or tests changed |
| Independent review; no self-approval | AGENTS.md §Dual-Agent Workflow | Yes. Both canonical reviews are Codex's reports, validated under the receipts folder and copied byte for byte |
| Human decisions stay human, with a brief and a do-nothing option | `.agent/docs/human-decision-protocol.md` | Yes. D-789 to D-791, D-793, D-797 and D-800 record Mat's words; each brief carried a do-nothing option |
| Never ask Mat for a review budget | `.agent/review-limits.json` `token_budgets: "off"` | Yes. Each round's spend was reported, never asked |
| Tell Mat before each Codex dispatch | Session 73 prompt | Yes |
| No raw home path in receipts | Plan S6 | Partly. Two build receipts held it until execution round 1 found it (F1) |
| Ask before any read of user data | Session 70 RULE-2 | Yes. Only row 0b read the installed models, by hash, as D-791 ruled; no row read the database or the settings file |
| Nothing reaches the network but row 0b; nothing posted upstream | D-336; D-790 | Yes. Every smoke recorded the dead proxies |
| No model file in the checkout or a commit | Session 73 prompt | Yes. H1-4 reads no_onnx True |
| Keep line endings; check for lone CR | Session 70 RULE-5 | Yes. Each edit was measured in Python bytes |
| Work each edge case through the helper's code | Session 72 RULE-1 | Partly. The guard's ten-slot fixture covered every quotient class, but the download client's cache override was found by the reviewer |
| Every count in a handoff is copied from its receipt | Session 63 RULE-2 | Partly. The handoff held; the D-800 brief miscounted the files (RULE-3) |
| End a launch by its PID | Session 56 RULE-2 | Yes. smoke-leftover reads 0 backends under the gate folder |
| Review prompts carry the ledger vocabulary and literal table shapes | Session 66 RULE-4 | Yes. All five reports were accepted by the closeout parser the first time |
| Execution decisions go into the decision_log | Session 71 RULE-4 | Yes. D-797 and D-799 in the plan, D-800 in the handoff |
| Status cells hold bare marks | Session 64 RULE-3 | Yes |

---

## Instruction Coverage

```yaml
schema: v1
session:
  id: "bf19ea3d-f4fe-42a9-b464-f9668da760bd"
  task_class: research
  outcome: success
sections:
  - id: priority_0_system_constraints_non_negotiable
    cited: true
    influence: 3
  - id: planning_contract
    cited: true
    influence: 3
  - id: testing_tdd_protocol
    cited: true
    influence: 2
  - id: execution_contract
    cited: true
    influence: 3
  - id: session_discipline
    cited: true
    influence: 2
  - id: dual_agent_workflow
    cited: true
    influence: 3
  - id: commits
    cited: true
    influence: 3
  - id: validation_pipeline
    cited: true
    influence: 3
  - id: rtk_token_optimized_commands
    cited: true
    influence: 1
  - id: instruction_coverage_reflection
    cited: true
    influence: 2
loaded:
  workflows: [create_plan, plan_critical_review, execution_session, execution_critical_review]
  roles: [orchestrator, coder, tester]
  skills: []
  refs:
    - .agent/docs/human-decision-protocol.md
    - .agent/docs/harness-profiles.md
    - .agent/review-limits.json
    - .agent/schemas/review-verdict.schema.v2.json
    - .agent/schemas/reflection.v1.yaml
    - docs/execution/reflections/TEMPLATE.md
decisive_rules: [P0:human-decisions-stay-human, P0:never-commit-or-push-without-human-approval, P1:independent-review-no-self-approval, P0:no-network-or-upload-beyond-the-ruling, P0:scope-changes-go-to-mat]
conflicts:
  - "The harness asks for a Co-Authored-By trailer on commits; task H2-5, development-lifecycle.md:454 and Mat's rule say no AI attribution trailer. The commit has none."
  - "Connected docs and artifact tools offered to publish deliverables; the user's rule keeps them as local repo files."
  - "The plan recommended no download and no user-data read; Mat ruled both, so Amendment 1 reopened the approved plan review."
note: "A spike with no product code: the guard was measured on a copy, Mat ruled what ships, and the only review findings were a cache bypass and a receipt leak."
slim_candidate: ["The handoff's FAIL_TO_PASS and Changed Files sections for a spike with no product code.", "H2-1's view_file row repeats what H2-2's validator checks."]
overthinking_observed: false
review_churn:
  rounds_to_approval:
    plan: 3
    execution: 2
  findings_per_round:
    - review: plan
      round: 1
      critical: 0
      high: 0
      medium: 0
      low: 0
    - review: plan
      round: 2
      critical: 0
      high: 1
      medium: 0
      low: 0
    - review: plan
      round: 3
      critical: 0
      high: 0
      medium: 0
      low: 0
    - review: execution
      round: 1
      critical: 0
      high: 1
      medium: 0
      low: 0
    - review: execution
      round: 2
      critical: 0
      high: 0
      medium: 0
      low: 0
  churned_findings: 0
  finding_categories:
    boundary_validation: 1
    provenance_error: 1
  verdicts:
    approved: 3
    changes_required: 2
meu_work_classes: [correctness]
```
