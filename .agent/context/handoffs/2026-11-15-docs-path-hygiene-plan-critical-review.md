---
date: "2026-11-15"
review_mode: "plan"
target_plan: "docs/execution/plans/2026-11-15-docs-path-hygiene/implementation-plan.md"
verdict: "approved"
findings_count: 5
template_version: "2.2"
requested_verbosity: "standard"
agent: "codex-independent-reviewer"
loop_id: "dph-plan-2026-11-15-docs-path-hygiene"
round: 3
---

# Critical Review: docs-path-hygiene

> **Review Mode**: plan
> **Verdict**: approved

## Scope

**Intent anchor:** av-kit's tracked text names the install folder the installer really uses (`Programs/av-kit-ui`), and a gate check, `tools/check_home_path.py`, fails when a file outside today's allow-listed evidence holds the home folder's full path; the six live files that hold it today are fixed, and every evidence file keeps its bytes.

Round 3 rechecks the complete working-tree plan/task, focusing on R2-F1 and the five-view decoder. Claude Code/Anthropic authored the plan; this reviewer is independent Codex/OpenAI. Applied PR-1–PR-9 and the Materiality Gate. Intent achieved means that executing the specified plan would deliver the objective; implementation has not begun.

The original Findings table and round-2 recheck are retained below as history. Their old status cells and line references are superseded by the round-3 summary. `findings_count: 5` is cumulative; there are no current open substantive findings and no new High or Critical finding. Eight helpers and the three new CHECK/ALLOW/test deliverables remain scheduled, absent files. No existing plan-local script can therefore be executed or certified.

Only C:/Temp/av-kit was written. No repository edit, product suite, dependency operation or network request ran. Secret paths, fleet/hub and pr-dph-sed.txt were excluded from reads. Probes are independent transcriptions of plan semantics, not implementations of its deliverables. The coordinator owns copying this report to the canonical location.

## Findings

| # | Severity | Blocking | Kind | Finding | File:Line | Recommendation | Status |
|---|---|---|---|---|---|---|---|
| R1-F1 | High | yes | control-defeat | **ALLOW binds filenames, not evidence contents.** mechanism: task-row-completion-predicate. Appending another home path to an already allow-listed proof leaves CHECK passing, the ALLOW hash unchanged, AC-8's evidence path set unchanged and AC-20's empty-list negative still failing as expected. Thus all those rows can pass while evidence bytes changed and new exposure was admitted. BASE covers edited live files; S4 covers currently dirty paths, not every clean evidence file or later sessions. Violates AC-8's bounded EVIDENCE_SET contract and the explicit Q3 content-binding requirement. | docs/execution/plans/2026-11-15-docs-path-hygiene/implementation-plan.md:145; implementation-plan.md:270; implementation-plan.md:336; task.md:51 | Persist each evidence path with its row-0/row-3 content digest and have production CHECK verify that binding before exempting it. Prove that an appended instance and a non-path byte edit are refused with unchanged ALLOW. Explicitly cover preservation of every EVIDENCE_SET file. | open |
| R1-F2 | High | yes | behavior | **The byte-only matcher silently misses ordinary UTF-16 text.** The exact AC-1 home path encoded as UTF-16LE or UTF-16BE has no match under HOME_RE; outside ALLOW, a file containing only that text produces neither found nor stale and therefore passes. The current AC-1–AC-7 fixtures do not require an encoding variant. This defeats the gate's central privacy behavior for a new text file, even though every listed ASCII/UTF-8 example passes. Violates AC-1. | docs/execution/plans/2026-11-15-docs-path-hygiene/implementation-plan.md:137; implementation-plan.md:138; implementation-plan.md:263 | Define supported text encodings and scan decoded text or equivalent encoded patterns, including BOM-marked UTF-16LE/BE; preserve correct line numbering and sanitized diagnostics. Add a negative-oracle fixture outside ALLOW that currently false-passes. Define the treatment of other encodings explicitly. | open |
| R1-F3 | Medium | no | behavior | **HOME_RE also matches different, longer usernames.** The final ASCII-only guard accepts the home prefix in synthetic usernames fixture.other, fixture-other and fixtureé. Both Windows and POSIX boundary definitions have this weakness. A harmless reference to a different user's folder can therefore refuse the maintainer's gate. This contradicts the stated longer-username exclusion; existing AC-2 only tests fixtures. | docs/execution/plans/2026-11-15-docs-path-hygiene/implementation-plan.md:142; implementation-plan.md:143; implementation-plan.md:264 | Specify path-component boundaries and add dot, hyphen and non-ASCII suffix negatives, alongside bare-home and punctuation-terminated positives. | open |
| R1-F4 | Medium | no | behavior | **H1-4 still compares API changes to HEAD.** baseline.sha is the row-0 HEAD, so an uncommitted Session 82 edit to packages/api/src/avkit_api/cli.py makes this command exit 1 even when Session 83 changed no API bytes. H1-5 depends on it. This is the allowed queue state, not unexpected concurrent drift. | docs/execution/plans/2026-11-15-docs-path-hygiene/task.md:65; implementation-plan.md:400 | Compare the API path/content inventory at execution start with its current inventory, or prove its row-0 dirty content remains unchanged. Do not require committing sibling work to make this skip check pass. | open |

## Recheck (round 2)

### Prior Pass Summary

| Finding | Prior Status | Recheck Result |
|---|---|---|
| R1-F1 | open | fixed |
| R1-F2 | open | fixed |
| R1-F3 | open | fixed |
| R1-F4 | open | fixed |

R1-F1: D-997, DIGEST and production CHECK now bind every ALLOW entry to row-0 content; appended instances and other non-EOL edits are refused. AC-23 tests both and pruning (implementation-plan.md:125,154–161,282,297,351–352; task.md:49,51).

R1-F2: the former byte-only matcher is replaced by decoding; BOM-marked UTF-16LE/BE and UTF-32 plus the specified ASCII-heavy unmarked UTF-16 fixture now reach HOME_RE. AC-22 adds the missing encoding oracles and line/output checks (implementation-plan.md:140–145,296; task.md:48–49). R2-F1 concerns the newly introduced binary classifier, rather than a failure to match decoded UTF-16 characters.

R1-F3: B and AC-2 now exclude the cited dot, hyphen, underscore and Unicode username suffixes, while AC-1 covers punctuation-terminated bare homes (implementation-plan.md:152,275–281). All cited cases pass the transcription. Residual boundary ambiguity is recorded below without escalating this fixed finding.

R1-F4: H1-4 now checks paths differing from baseline.sha against baseline-dirty-hashes.json; unchanged sibling API content passes, and new or edited API content fails (task.md:65; implementation-plan.md:419,455). This permits Sessions 75–82's uncommitted edits.

### New Findings

| # | Severity | Blocking | Kind | Finding | File:Line | Recommendation | Status |
|---|---|---|---|---|---|---|---|
| R2-F1 | High | yes | behavior | **The new binary classifier silently discards valid mixed-language UTF-16 text.** A new file outside ALLOW containing `日本語の記録\nsecond\nC:/Users/fixture/a`, encoded as unmarked UTF-16LE or UTF-16BE, has NUL bytes but fewer than 90% NULs in either byte lane. Step 2a calls it binary and skips it. The modeled CHECK therefore exits 0 with binary=1 despite the full home path on line 3. Explicit decoding yields the path and HOME_RE matches it. All planned AC-22 fixtures can still pass because their unmarked UTF-16 example is ASCII-heavy. This violates AC-1's detection contract; AC-22 is the associated new encoding criterion, cited through AC-1 because AC-22 is not registered in this loop. The concrete new failure is decoder classification excluding text before matching, not the old byte-regex defect. | docs/execution/plans/2026-11-15-docs-path-hygiene/implementation-plan.md:142; implementation-plan.md:296; task.md:49 | Revise the unmarked-UTF-16 detection/fallback so ordinary mixed-language UTF-16 text reaches HOME_RE instead of silently passing as binary. Add this LE/BE fixture outside ALLOW to AC-22, expecting found at :3 and exit 1; preserve the PNG binary negative and sanitized output. | open |

## Recheck (round 3)

### Prior Pass Summary

| Finding | Prior Status | Recheck Result |
|---|---|---|
| R1-F1 | fixed | fixed |
| R1-F2 | fixed | fixed |
| R1-F3 | fixed | fixed |
| R1-F4 | fixed | fixed |
| R2-F1 | open | fixed |

R2-F1: step 2a no longer classifies an unmarked NUL file as binary or skips it. It scans all five views, with independent decoded-line numbering and `(path, line)` deduplication (implementation-plan.md:140–145). AC-1 expressly covers encodings regardless of surrounding content; AC-22 now requires the round-2 mixed-language fixture in UTF-16LE/BE with LF/CRLF, plus unmarked UTF-32BE and PNG negatives/positives (implementation-plan.md:275,296). All six independently modeled mixed-language cases report line 3. This fixes the concrete AC-1 failure; AC-22 is the associated unregistered criterion. AC-20 uses `nul=<k>` (implementation-plan.md:294). D-988 alone is refined; D-998 stays free (implementation-plan.md:477,487–496).

R1-F1 remains fixed by DIGEST/production CHECK and AC-23's appended-path/non-path-byte/prune negatives, cited through registered AC-8 (implementation-plan.md:125,154–161,282,297). R1-F2's decoding, R1-F3's boundary and R1-F4's content-bound API skip remain intact (implementation-plan.md:140–152; task.md:65). This review found no new materially different failure on those surfaces.

### New Findings

| # | Severity | Blocking | Kind | Finding | File:Line | Recommendation | Status |
|---|---|---|---|---|---|---|---|

None. The AC-22 PNG delimiter ordinal is a clerical note below, not a new substantive finding or a reason for another round.

## Q1 — Goal and proof coverage

Accepted: AC-13/14 and row 5 correct Programs/av-kit-ui and the resources layout; AC-10–18 cover the six live files. AC-1/22 cover decoding, AC-8/23 bind today's evidence by path and normalized content digest, AC-19 wires CHECK into D6, and AC-20/21 prove repo Green, the empty-list negative and frozen ALLOW through closeout (implementation-plan.md:275–297; task.md:51–59,63,78).

No goal clause remains without an AC and a proving row. Evidence files are never edited; D-997's CRLF-to-LF digest normalization is the clone-compatibility exception accepted in round 2, while local evidence bytes remain untouched. No new substantive rejection.

## Q2 — CHECK design

Accepted: HOME_RE retains Windows slash variants, JSON-escaped backslashes, case-insensitive drive/Git Bash forms, file:/// drive paths, case-sensitive POSIX homes, punctuation-terminated bare homes and tilde exclusion (implementation-plan.md:146–153,275–281). The model passes 240 combinations of the 12 positive forms, ten BOM/no-BOM encodings and LF/CRLF, plus the six mixed-language cases. All 31 current NUL files have zero matches across the five views; total inventory remains 130 lines in 66 files. Different decoded views number their own lines; duplicate `(path, line)` pairs collapse and different line numbers survive. Malformed wide text does not throw in the model.

Accepted privacy contract: decoded text is used only for matching; output is relative path/line or fixed diagnostics/counts. AC-3/6/22 require stdout/stderr privacy and suppressed bad arguments; no new printing path is introduced by decoding (implementation-plan.md:133,157,162–167,277,280,296). Actual exception/output handling still needs implementation verification.

Clerical note, implementation-plan.md:296: a path **after the fourth LF** is on line **5**, not 4. To retain the intended `:4` PNG fixture, place it after three LF delimiters. The existing planner measurement does exactly that (`r2-measure.py:59`, `r2-measure.txt:7`); the governing step 2a line-number rule is unambiguous. This is an ordinal typo under the Materiality Gate.

The previously reported residual limits are now explicit in D-988 and Out of Scope: percent-encoded separators, longer usernames with whitespace/apostrophes, and non-ASCII homes in cp1252/Latin-1 (implementation-plan.md:397,496). They are accepted disclosed limits, not newly rediscovered blockers. No substantive five-view defect was demonstrated.

## Q3 — ALLOW and evidence fidelity

Accepted: sorted exact path/digest entries bind ALLOW to row-0 EVIDENCE_SET content; production CHECK refuses appended instances and non-EOL edits while the path remains. Removing every instance makes the entry stale; --prune only deletes stale/missing entries and never refreshes a digest (implementation-plan.md:123–127,154–161,282,297,351–353). The model retains the round-2 exempt/changed/changed/exempt/stale/stale outcomes. All 60 current evidence files remain NUL-free, so the new decoder neither expands nor prunes their set.

Own-file classification still precedes evidence classification, excludes PLAN and this session's handoffs/reviews, and fails S7; the new reflection is outside frozen ALLOW and the final repeat catches it too (implementation-plan.md:127,349,470; task.md:78). A later session cannot append a home path to a listed evidence file without failing the unchanged digest. No new ALLOW rejection.

## Q4 — Live fixes and fidelity

Accepted: current bytes still show twelve live pairs in the named six files. CRLF edit targets are .agent/skills/git-workflow/SKILL.md, docs/build-plan/06-gui.md, docs/build-plan/07-distribution.md and .agent/docs/commands.md; README, the inspiration example, both UI tests and YAML are LF. BASE records post-Session-82 content and edit-check requires exact content-bound replacements, unchanged other lines and original endings, including GUI widths and README JSON (implementation-plan.md:171–194,358–369; task.md:36,54–57).

D-996's layout agrees with electron-builder.yml:32–35,52–53 and mcp-setup-prompt.ts:35: backend, ffmpeg and mcp-server are directly under resources/. The modeled README replacement parses, uses Programs/av-kit-ui for both paths and keeps av-kit.exe. No new live-fix or packaging-path defect found. edit-check is future work, not a checked implementation.

## Q5 — Order, gate and registers

Accepted: row 0 records path/content baselines after earlier sessions, and S4 protects sibling dirty content. H1-4 compares each baseline-differing API path to its row-0 recorded bytes, preserving an unchanged uncommitted Session 82 edit (implementation-plan.md:371–385,417–425; task.md:42,65). No clean-tree prerequisite is introduced. CHECK is explicitly called by this session gate and the added D6 row; current inventory supports the intended six-file repo Red (implementation-plan.md:248–256,438–456).

Registers go through the copied issue_triage model adapter with --scrub, hash preconditions, held Windows handle and exact parsed-difference restrictions, then render/render --check; no direct register edit is scheduled (implementation-plan.md:230–246; task.md:56,60). D-988–D-997 serve the goal and honor the supplied rulings; no additional M hit requiring Mat was identified. Execution authorization is supplied by the review packet after approval; commits remain unauthorized. Preserve the previously noted identity.py copy caution about binding files CHECK reads; it is not a new finding.

## Checklist Results

These are plan-readiness observations, not completed implementation tests. Manual observer: codex-independent-reviewer; manual exits are null. The original round-2 failed results above describe the historical round, not this verdict.

| Check | Result | Procedure / command | Exit | Evidence |
|---|---|---|---|---|
| PR-1 Plan/task alignment | pass | Compare the whole working-tree plan and task, including rows 0–10, H1/H2 and step-2a references. | null | Same scope and order; unchanged task.md delegates decoding to the revised plan. |
| PR-2 Not started | pass | Inspect task statuses and probe scheduled helper/product paths. | null | All implementation rows unchecked; eight scheduled helpers and three new deliverables absent. |
| PR-3 Task contract | pass | Inspect task owners, deliverables, validation and dependencies. | null | Helpers are explicitly scheduled before callers; no materially missing executable. |
| PR-4 Validation realism | pass | Trace AC-1/AC-22 and AC-8/AC-23 through CHECK, inventory, edit-check, repo Red/Green and final repeats. | null | Five-way scan has concrete negative oracles; AC-22 PNG delimiter ordinal is a nonblocking typo. |
| PR-5 Sources/HDP | pass | Compare grouping Session 83/D-813–D-817, issue D-811, HDP sections 4a/5/5a/6, expert pass and D-988–D-997. | null | Supplied rulings honored; no additional mandatory-human hit identified; D-998 unused. |
| PR-6 Corrections readiness | pass | Trace R1-F1–R1-F4 and R2-F1 into current contracts, ACs and task rows. | null | All five prior findings fixed; new mixed-language fixture is expressly required by AC-22 through AC-1. |
| PR-7 Scope discipline | pass | Compare exclusions with D-811/D-817/D-988/D-990 and the Session 77 boundary. | null | Evidence stays untouched; residual encoding/URL/name limits are disclosed rather than hidden. |
| PR-8 Reachability and negative oracles | pass | Trace task row 8 and H1-2 home-path to production CHECK, plus AC-9/20/21 and content-bound ALLOW. | null | Named gate calls CHECK; repo Red and empty-ALLOW negatives prevent vacuous success; no new false-pass demonstrated. |
| PR-9 Named contracts | pass | Compare single-statement contracts, five-view rule, AC references and task references. | null | One governing decoder definition; no materially ambiguous competing behavior. |
| DR Live fixes and order | pass | Compare live-file bytes/EOLs, packaging config, MCP packaged path, README replacement, BASE and H1-4. | null | Twelve live pairs in six files; correct install/resources paths; content baselines accept unchanged sibling work. |
| AV-1–AV-6 planned verification | pass | Inspect assertion Reds, immutable Green expectations, observable negatives, no-skip requirements and source tags. | null | Appropriate plan-level test design; actual Red/Green execution remains future work. |
| Independent five-view design probes | pass | Scratch probes-r3.py (full command below) | 0 | 240 encoding fixtures and six mixed-language fixtures report line 3; duplicate suppression works; 31 repository NUL files yield zero hits; total inventory remains 130 lines in 66 files. These are semantic-model observations, not execution of an implemented CHECK. |
| Product suites / implemented CHECK | n/a | Not run under the read-only packet | null | Not run: read-only plan review; CHECK and plan-local helpers do not exist yet. No pytest, vitest, npm, uv sync/lock or network request. |

### Independent probe evidence

Scratch exit 0 means the observations completed. It is not an execution result for the nonexistent CHECK. Secret paths and the hub were excluded from the working-tree read. The current permitted census contains 2,302 unmarked UTF-8 files, one marked file and 31 NUL files; the plan's older 2,299-text-file count is a dated planning snapshot. The differences add no home-path hits. Task content is byte-identical to round 2.

```json
{"schema_version": "evidence.v1", "check_id": "dph-plan-design-probes-r3", "command": "$env:PYTHONDONTWRITEBYTECODE='1'; $env:PYTHONIOENCODING='utf-8'; $env:RECEIPTS_DIR='C:/Temp/av-kit'; rtk proxy python C:/Temp/av-kit/docs-path-hygiene/review/probes-r3.py *> C:/Temp/av-kit/docs-path-hygiene/review/probes-r3.txt; $dphExit=$LASTEXITCODE; Get-Content -Encoding utf8 C:/Temp/av-kit/docs-path-hygiene/review/probes-r3.txt; exit $dphExit", "cwd": "P:/av-kit", "scope": "round-3 decoder/HOME_RE/ALLOW semantic probes and permitted current live/evidence/NUL files", "phase": "static", "exit_code": 0, "result": "pass", "tested_state": "implementation-plan.md-sha256:9b73511c0643cadd932371c0171098b558b4e8feb7f6f01159380721f41ff2b5;task.md-sha256:5e68fa49571cd6ec1367d7a7e65fc8b20a240bc2966fc43b0458813813860612", "output": "HOME_RE: AC-1 positives=12/12; AC-2 negatives=10/10; AC-7 positives=2/2 negatives=5/5\nEncoding matrix: 240/240 windows-form/BOM/no-BOM/LF/CRLF fixtures found at line 3\nR2-F1: unmarked mixed-language UTF-16LE/BE and UTF-32BE, LF/CRLF=6/6 found at line 3\nPNG: no-path passes (nul=1); after 3 LF bytes found :4; after 4 LF bytes found :5 (AC-22 prose off by one)\nDuplicate suppression: same path:1 in UTF-8 and UTF-16LE printed once; a second decoded line retained\nMalformed sequences: all four wide decoders tolerate odd/truncated/unpaired tails without exception\nOutput model: only path:line/counts; decoded content and fixture home absent (implementation still pending)\nALLOW digest model: {\"LF-only\": \"exempt\", \"appended\": \"changed\", \"missing\": \"stale\", \"other-edit\": \"changed\", \"removed\": \"stale\", \"unchanged\": \"exempt\"}\nPermitted working-tree scan: kinds={\"marked\": 1, \"nul\": 31, \"utf-8\": 2302}; NUL files=31; NUL hits=0; total hit lines=130; hit files=66\nLive/evidence: 12 live pairs in six files; all 60 evidence files NUL-free; appending content changes every bound digest\nEdit fidelity: four live edit targets CRLF; README replacement JSON parses with both paths under Programs/av-kit-ui\nNot started: eight scheduled helpers and three new deliverables absent; task.md byte-identical to round 2\nReviewed state={\"implementation-plan.md\": \"9b73511c0643cadd932371c0171098b558b4e8feb7f6f01159380721f41ff2b5\", \"task.md\": \"5e68fa49571cd6ec1367d7a7e65fc8b20a240bc2966fc43b0458813813860612\"}\nProbe assertions complete; scratch exit 0 is model validation, not implemented CHECK approval", "fresh": true}
```

### Artifact validation and concurrent state

The repository parser reads this as round 3, approved, with zero open blocking findings; the verdict validates against the repository v2 schema. The final hash comparison found two concurrent Session 78 plan-file edits, which were checked with the same five-view model and contain no home-path hits. The reviewed target, all six live files, all 60 evidence files and all 31 NUL files remain at their probed content. No concurrent content was edited by this reviewer.

```json
{"schema_version": "evidence.v1", "check_id": "dph-review-artifacts-r3", "command": "$env:PYTHONDONTWRITEBYTECODE='1'; $env:PYTHONIOENCODING='utf-8'; $env:RECEIPTS_DIR='C:/Temp/av-kit'; rtk proxy python C:/Temp/av-kit/docs-path-hygiene/review/validate-r3.py *> C:/Temp/av-kit/docs-path-hygiene/review/validate-r3.txt; $dphExit=$LASTEXITCODE; Get-Content -Encoding utf8 C:/Temp/av-kit/docs-path-hygiene/review/validate-r3.txt; exit $dphExit", "cwd": "P:/av-kit", "scope": "round-3 rolling review, verdict schema and reviewed-file content stability", "phase": "static", "exit_code": 0, "result": "pass", "tested_state": "implementation-plan.md-sha256:9b73511c0643cadd932371c0171098b558b4e8feb7f6f01159380721f41ff2b5;task.md-sha256:5e68fa49571cd6ec1367d7a7e65fc8b20a240bc2966fc43b0458813813860612", "output": "PASS: verdict JSON validates against repository review-verdict.schema.v2.json\nPASS: repository rolling-review parser: {\"open_findings\": 0, \"review_mode\": \"plan\", \"rounds\": 3, \"target_plan\": \"docs/execution/plans/2026-11-15-docs-path-hygiene/implementation-plan.md\", \"verdict\": \"approved\"}\nPASS: history preserved, two recheck sections, exact prior-status headers, whole goal anchor and approval checklist consistency\nPASS: 2332 permitted working-tree files byte-identical; 2 concurrent Session 78 plan edits have no home-path hits\nConcurrent changed paths: [\"docs/execution/plans/2026-11-15-e2e-harness-hardening/implementation-plan.md\", \"docs/execution/plans/2026-11-15-e2e-harness-hardening/task.md\"]\nPASS: target plan/task, all six live files, 60 evidence files and 31 NUL files remain byte-identical\nPASS: report contains no full real home path\nReview artifacts complete; implementation remains unstarted; no ledger mutation performed", "fresh": true}
```

## Verdict

**approved** — R2-F1 is fixed, R1-F1–R1-F4 remain fixed, and no new evidence-backed High or Critical delivery defect was found. Executing the specified plan would satisfy the goal within its disclosed residual limits. Keep the AC-22 ordinal correction as a clerical note; it does not require another review round. Actual CHECK behavior, helpers and full-gate results remain for execution review. The report is C:/Temp/av-kit/dph-plan-review-round-3.md; the repository remains read-only for this reviewer.
