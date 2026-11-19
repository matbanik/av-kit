---
date: "2026-11-18"
review_mode: "plan"
target_plan: "docs/execution/plans/2026-11-18-eval-describe-raw-bytes/implementation-plan.md"
verdict: "approved"
findings_count: 0
template_version: "2.2"
requested_verbosity: "standard"
agent: "codex-independent-reviewer"
loop_id: "edr-plan-2026-11-18-eval-describe-raw-bytes"
round: 1
---

# Critical Review: eval-describe-raw-bytes

> **Review Mode:** plan
> **Verdict:** approved

## Scope

**Intent anchor:** Session 64's eval run book captures `eval-harness.ts describe` with a new script, `eval-describe.py`, that runs the harness in a subprocess and writes the MCP server's stdout bytes unchanged (a fake child proves the bytes pass through, AC-6; on the real harness the capture equals an independent `npx` read on another root and keeps its tail after CUT, AC-9); it refuses output that is not UTF-8, holds a BOM, a CR byte or cp437 mojibake, or lacks exactly one CUT line, with a non-zero exit and a named reason, using the one pattern and CUT line Session 92 wrote (`eval-rerun.py` `MOJIBAKE` and `CUT`, D-1186), not a second one, and exits 2 with a named message when that file cannot load; `eval-run.md` step 3 names the new command and a dated note says what changed and why; Session 64's task rows, plan and receipts and Session 92's files stay byte for byte; and `EVAL-HARNESS-DESCRIBE-CP437-MOJIBAKE` is resolved through the triage tool with receipts. No product code, no model call and no eval run. Tests and scripts prove each part; there is no manual check.

Reviewed the complete working-tree plan and task, both existing plan-local scripts, grouping sections 1–8, the issue and D-1196, the expert-pass receipt, the run book, relevant harness/backend and Session 92 guard code, referenced helper sources and validation paths. Applied PR-1–PR-9 and the Materiality Gate. Claude Code/Anthropic authored the plan; Codex/OpenAI independently reviews it.

The supplied execution/commit authority, D-1198/D-1199 scope and D-1201 hand-over are accepted. D-1200 remains Mat's and outside this session. No repository file was edited. Only C:/Temp/av-kit was written; no pytest, product suite, build, harness, model, package synchronization or network request ran. Forbidden files were not opened. Review observations below are automated probes or reviewer inspection; none adds a human acceptance row to execution.

## Findings

| # | Severity | Blocking | Kind | Finding | File:Line | Recommendation | Status |
|---|---|---|---|---|---|---|---|

## Q1 — Goal and acceptance coverage

Accepted: AC-1–7 cover the clean path, named refusals, shared guard, fake-child byte identity and CLI failures; AC-8 requires both historical forms to reproduce and later be refused; AC-9 adds the real harness comparison and tail; AC-10 preserves the exact run-book delta; AC-11 binds records; AC-12 resolves the issue through tooling; AC-13 binds the final gate. Task rows 0–6 and H1-2 follow those dependencies (plan:182–200; task:44–57). Every goal clause has an AC and an execution row. RAW_CAPTURE, ONE_GUARD, NAMED_REFUSAL, NO_OVERWRITE, STEP3_NAMES_SCRIPT and RECORDS_KEPT have coherent observable meanings (plan:85–94).

Nothing rejected. Approval means the plan is ready to execute; it does not certify unimplemented behavior.

## Q2 — One guard and load failures

Accepted: the proposed capture loads Session 92 by path, disables bytecode writing before loading, catches missing/spec/import/syntax failures at bootstrap and checks GUARD before starting a child. Refusals read GUARD.MOJIBAKE and GUARD.CUT at each call. AC-5's stub changes actual refusal behavior, avoiding the regex-cache identity trap; AC-7 separately exercises failed bootstrap and capture with no guard (plan:105–109,139–143).

The existing edr-check.py imports the actual guard without a second pattern (:88–112). Independent probing confirmed the source module, pattern object and unchanged Session 92 bytecode-cache metadata. A fresh isolated Python bootstrap with an unavailable spec exited 2, printed the named ASCII message and emitted no traceback. The capture script's corresponding tests remain scheduled. Nothing rejected.

## Q3 — Red first and both old redirects

Accepted: edr-old.ps1 checks that roots/receipts are unused, records PowerShell version/edition and both code-page settings, then executes E-1's all-stream redirect and step 3's merged-stderr redirect in the same fresh pwsh process. Both child exits are preserved (edr-old.ps1:20–55). edr-check.py old requires mojibake and exactly one CUT in each receipt, not merely one of them (:195–214). The PowerShell parser reports zero errors.

Task row 1 precedes script creation, asserts SCRIPT.is_file() inside every test, checks AC-1–7 assertion failures through red-check.py and records the immutable test hash. S3 rejects setup failures/passing Reds; S5 correctly stops if either redirect does not reproduce on the measured shell (plan:270–272,298–300; task:46–48).

Byte reads independently corroborated the historical premise: Session 64 is 30,806 bytes, 725 CRLF, 9 mojibake arrows, 2 mojibake dashes, no real counterparts and one CUT; Session 92 attempt 1 is 37,406 bytes, 834 CRLF and also corrupted. The roundtrip receipt reports equality after undoing cp437 decoding. Fresh reproduction is execution work. Nothing rejected.

## Q4 — Capture correctness and refusal behavior

Accepted: binary pipes and direct byte writes preserve the child stdout, with AC-6's Python child as the causal byte-identity oracle. Refusal, timeout and nonzero child exit never write OUT; forensic bytes use a separate .refused path. Preflight checks all three output paths before a child, and exclusive create prevents overwriting at write time (plan:111–122,141,193). Mixed and cp437 fixtures, malformed encoding, BOM, CR, empty output and CUT count are explicit tests (plan:126–143).

The live checker independently launches npx, compares the whole byte sequences, checks real characters and their cp437 trap, requires the convert action-notes section after CUT plus final LF, and builds three clean prompts with the expected description (edr-check.py:150–184,224–264). Its 26 self-checks passed, including rejection of changed bytes, a missing tail, mojibake and CR. AC-9 accurately limits launcher/root equality to that observation; AC-6 proves unchanged capture. Nothing rejected. The documented cp437-only pattern reach is accepted as the supplied contract.

## Q5 — Run book and preserved records

Accepted: expected_doc constructs exactly the dated note after the six-line introduction and the replacement step 3. cmd_doc compares bytes to that transformation and rebuilds the prompts (edr-check.py:140–147,267–288). An independent reversible transformation of the real run book measured 5,748 → 6,980 bytes, retained LF, four text blocks and both existing surface-reading sub-bullets, and recovered every baseline byte after undoing those two edits.

The nine RECORDS entries cover Session 64's task, plan, harness, seed and checker, its describe receipt, Session 92's guard and expected text, and backend.ts; record mode refuses missing sources, later mode compares their hashes and runs both legacy selftests (:46–56,299–317). The baseline/scope rules also protect Session 92's other tracked files and reject unrelated edits. Nothing rejected.

## Q6 — Gate, decisions and scope

Accepted: row 0 establishes content baselines and the initial home-path check; H1-2 supplies static checks, plan-folder pytest, records/doc/old-refusal checks, a fresh build and capture/direct comparison, register/render checks and before/after identities. H1-4 validates the unchanged-product basis for skipped product suites (plan:256–290; task:44,57–59). The 17 referenced current executable/source paths probed exist; nine future implementation files are absent and have explicit creation rows. No missing executable is silently presumed present.

The npm build is local tsc with output ignored by mcp-server/dist/. The harness describe path only initializes/lists the isolated local server over scratch roots; it does not invoke an eval task or model (eval-harness.ts:99–108,136–166; backend.ts:134–155). Offline sync and installed tsx are explicit prerequisites. D-1201's folder coupling is real and disclosed, with a named load failure; D-1202–1206 are reversible choices within this scope. No uncovered mandatory-human item was identified under HDP sections 4a/5/5a/6.

Issue resolution uses the copied adapter with narrowed keys, a row-0 hash and the triage model, followed by render/check and a comparison preserving other issues and grouping lines (task:53; Session 92 issue-resolve.py:231–308). S2/S4/S7–S10 retain the relevant stops. Nothing rejected.

## Checklist Results

Inspection entries are reviewer observations by codex-independent-reviewer, with null exit codes. Probe passes establish plan readiness, not execution acceptance.

| Check | Result | Command / procedure | Exit | Evidence |
|---|---|---|---|---|
| PR-1 Plan/task alignment | pass | Compare all ACs, contracts and task dependencies | null | Same script, test, live, doc, register and gate order. |
| PR-2 Not started | pass | Inspect task statuses and proposed implementation paths | null | Implementation rows unchecked; capture/tests and planned helpers absent. |
| PR-3 Task contracts and paths | pass | Inspect owners/deliverables/commands; run review_probe.py | 0 | 17 existing sources present; nine future files explicitly scheduled. |
| PR-4 Validation realism | pass | edr-check.py --selftest; review_probe.py; PowerShell parse | 0 | 26 self-checks pass; historical bytes, exact doc delta and load failure independently confirmed. |
| PR-5 Source-backed planning | pass | Compare grouping, issue, D-1201–1206 and cited code | null | Decisions serve the registered goal; no additional human gate identified. |
| PR-6 Corrections readiness | pass | Inspect canonical review/handoff targets and correction path | null | One target-bound rolling plan review; no prior-round census applies. |
| PR-7 Scope discipline | pass | Compare out-of-scope table to grouping section 3 and D-1196 | null | No omitted acceptance hidden by the tooling-only scope. |
| PR-8 Control reachability | pass | Trace CLI → guard/child → bytes; inspect negative oracles and gate calls | null | Producers and assertions are reachable; existing checker rejects concrete bad fixtures. |
| PR-9 Single-statement discipline | pass | Compare repeated refusal/record/gate descriptions with named contracts | null | Canonical contracts are identifiable; no materially conflicting live predicate. |
| AV-1–AV-6, plan application | pass | Inspect planned Red/Green, real-child seam, refusals, scope and sources | null | No oracle weakening, hidden deferral or new product contract. |
| Execution pytest/live/full gate | n/a | Reserved for the approved execution rows | null | Deliberately not run during this read-only plan review. |

```json
{"schema_version":"evidence.v1","check_id":"edr-review-checker-selftest","command":".venv/Scripts/python.exe -B docs/execution/plans/2026-11-18-eval-describe-raw-bytes/edr-check.py --selftest","cwd":"P:/av-kit","scope":"existing plan-local checker pure fixtures","phase":"targeted","exit_code":0,"result":"pass","tested_state":"working-tree-plan-round-1; implementation absent","output":"26 checks printed ok; selftest: 0 failures","fresh":true}
```

```json
{"schema_version":"evidence.v1","check_id":"edr-review-independent-probe","command":".venv/Scripts/python.exe -B C:/Temp/av-kit/eval-describe-raw-bytes/review/review_probe.py","cwd":"P:/av-kit","scope":"guard bootstrap, historical receipt bytes, exact proposed doc delta and referenced paths","phase":"targeted","exit_code":0,"result":"pass","tested_state":"working-tree-plan-round-1; implementation absent","output":"Historical S64: 30806 B, 725 CRLF, mojibake arrows 9/dashes 2, real arrows/dashes 0, CUT 1. Proposed doc 5748 -> 6980 B with exactly two edits. Guard bootstrap failure exit 2, named ASCII message, no traceback. 17 existing paths present; 9 scheduled future files absent. 13 repository file hashes and Session 92 bytecode cache unchanged. review-probe: all assertions passed","fresh":true}
```

## Verdict

**approved** — no findings and no required corrections. Executing the specified rows would deliver the registered goal. Preserve the planned Red/Green, live, records and final-gate evidence for execution review. The coordinator owns copying this complete report to its canonical path and recording the verdict; this reviewer did neither.
