---
date: "2026-11-05"
project: "2026-11-05-closeout-register-grammar"
meu: "none"
status: "complete"
action_required: "VALIDATE_AND_APPROVE"
template_version: "2.2"
verbosity: "standard"
plan_source: "docs/execution/plans/2026-11-05-closeout-register-grammar/implementation-plan.md"
build_plan_section: "non-product tooling (CLOSEOUT-CHECK-REFUSES-REGISTER)"
agent: "claude-code-local (Claude Opus 5.5)"
reviewer: "codex (H1-7 execution review)"
predecessor: "none"
---

# Handoff: 2026-11-05-closeout-register-grammar-handoff

> **Status**: `complete`
> **Action Required**: `VALIDATE_AND_APPROVE`

---

## Scope

**MEU**: none (D-280). This is a tooling session tracked by `CLOSEOUT-CHECK-REFUSES-REGISTER` (P3). The closeout check now reads `.agent/context/known-issues.yaml` exactly as `model.save` writes it, for every issue a session names.
**Build Plan Section**: none, a non-product tooling fix. Scope is grouping §3 Session 49b (`.agent/context/grouping/2026-11-04-rc2-triage-residuals-session-grouping.md:145`).
**Predecessor**: none. The single non-MEU handoff follows `2026-09-26-framework-update-adoption`.

- **The writer (row 2, D-281).** `model.save` dumps through `_SsotDumper` (`tools/issue_triage/model.py:316`). Every sequence is indented under its key. A sequence that is itself a sequence item starts on its own line under its dash, and no value is written as an anchor or alias. `width=10**9` stops wrapping. A string holding U+0085, U+2028 or U+2029, ending in two newlines, or that is a lone newline, is double-quoted (the lone newline after review F1). Any other multi-line string is a literal block. An empty or multi-line mapping key raises `IssueTriageError`. `save` renders the text first and writes it only if it loads back equal to the data, so a refused save leaves the file as it was.
- **The reader (row 3, D-283).** `--decision-issue` is `action="append"`. `decision_sources` reads each named issue in the order given, each under its own label `issue <ID>`, and checks repeated IDs per issue and stage agreement across every source (`tools/validate_closeout_artifacts.py:1554`). A repeated or empty ID is `Usage`, exit 2 (`:2064-2071`). A named issue the source doesn't hold is still refused, even beside one it does. The selftest gains four arms, and the protocol paragraph says the flag repeats once per issue (`.agent/docs/human-decision-protocol.md:201-221`).
- **The register (rows 4, 5 and 7, D-284, D-285).** `register-rewrite.py` held a deny-write handle on the register for each run and was bound to the expected hash each time. It staged each save and checked it before writing. The reformat changed 0 parsed fields. The reword changed exactly the 15 planned fields, after which 67 of 67 decision logs read. The resolve changed `status`, `verification` and `resolution_path` of this issue only.
- **The proof (row 6, AC-11).** Session 49's reflection check, rerun against the register with both `--decision-issue` flags and no extract, exits 0 and reconciles 28 decisions. Row 0 saw the same command exit 1.

The reader's grammar, `check_yaml_subset` and `PLACEHOLDER` don't change (D-282). Nothing ships: these are repository tools.

**Plan:** [implementation-plan.md](../../../docs/execution/plans/2026-11-05-closeout-register-grammar/implementation-plan.md). **Execution authorization:** `USER_EXPLICIT`, 2026-11-05, "go-ahead", given after the plan review approved in round 2 and Mat read §Rewording at the plan gate (D-285).

---

## Acceptance Criteria

| AC | Type | Description | Source | Test(s) | Status |
|----|------|-------------|--------|---------|--------|
| AC-1 | unit | `model.save` writes every sequence indented, nested sequences in the noncompact form, and the whole file passes `check_yaml_subset`; `issue_decision_log` reads nested lists inside a decision item | Local Canon (`CLOSEOUT-CHECK-REFUSES-REGISTER`; D-274) | `tests/tooling/test_closeout_register_grammar.py:83` | ✅ |
| AC-2 | unit | No wrapping; a multi-line value is a literal block; the edge strings and a shared list pass the grammar; an empty or multi-line key raises and leaves the file | Local Canon (same; D-281) | `tests/tooling/test_closeout_register_grammar.py:124`, `:132`, `:141` (9 cases), `:154`, `:165` (2 cases) | ✅ |
| AC-3 | unit | What `save` writes loads back equal, for every AC-2 edge string and seven plain ones | Local Canon (D-281) | `tests/tooling/test_closeout_register_grammar.py:183` (16 cases) | ✅ |
| AC-4 | integration | With the flag repeated, a reflection missing the first-named issue's decision is refused | Local Canon (HDP §6) | `tests/tooling/test_closeout_register_grammar.py:239` (CLI by subprocess) | ✅ |
| AC-5 | integration | Repeating one ID is `Usage`, exit 2 | Local Canon (D-283) | `tests/tooling/test_closeout_register_grammar.py:246` (CLI by subprocess) | ✅ |
| AC-6 | integration | A named issue absent from the source is refused beside a present one | Local Canon (D-283) | `tests/tooling/test_closeout_register_grammar.py:253` (CLI by subprocess) | ✅ |
| AC-7 | integration | Every decision present passes with several flags; a single flag behaves as before | Local Canon (HDP §6) | `tests/tooling/test_closeout_register_grammar.py:260` (CLI by subprocess) | ✅ |
| AC-8 | unit | The validator's `--selftest` gains arms for AC-4, AC-5 and AC-6 and reports 0 failures | Local Canon (`test_evidence_contract_real_cli_selftests`) | `tools/validate_closeout_artifacts.py:3984-4047`; `tests/tooling/test_framework_adoption.py::test_evidence_contract_real_cli_selftests` | ✅ |
| AC-9 | integration | `REWRITE --mode reformat` saves the register with no parsed difference; the file passes the grammar; 61 logs read | Human-approved (D-274; Mat's brief) | `register-rewrite.py --mode reformat` (row 4, `s49b-reformat.txt`) | ✅ |
| AC-10 | integration | `REWRITE --mode reword` changes exactly the 15 planned fields; 67 of 67 logs read; none matches `PLACEHOLDER` | Human-approved (D-274; D-285) | `register-rewrite.py --mode reword` (row 5, `s49b-reword.txt`) | ✅ |
| AC-11 | integration | `DONE_PROOF` exits 0 against the register as written | Human-approved (Mat's brief) | Session 49's reflection check, task row 6 (`s49b-done-proof.txt`) | ✅ |

<!-- CACHE BOUNDARY -->

---

## Evidence

### FAIL_TO_PASS

| Test | Red Output (hash/snippet) | Green Output | File:Line |
|------|---------------------------|--------------|-----------|
| AC-1, AC-2 (13 cases) | `assert 'mixes a mapping and a sequence…' is None` and the other grammar refusals; the 300-character value wrapped; `&id001` written; `DID NOT RAISE` for the two keys | pass | `test_closeout_register_grammar.py:83-175` |
| AC-3 `[U+0085]` | `assert {… 'a b' …} == {… 'a\x85b' …}`: today's writer loads U+0085 back as a space | pass | `test_closeout_register_grammar.py:183` |
| AC-2 `[newline-only]` (review F1) | `assert "known-issues.yaml is not valid YAML: line 20: '...' is not a 'key: value' line." is None`: a lone newline as the file's last value was written `|2+` and closed with `...` | pass | `test_closeout_register_grammar.py:141` |
| AC-4 | `assert (0, False) == (1, True)`: only the last flag was read | pass | `test_closeout_register_grammar.py:239` |
| AC-5 | `assert (0, False) == (2, True)` | pass | `test_closeout_register_grammar.py:246` |
| AC-6 | `assert (0, False) == (1, True)`: the absent issue wasn't the last flag | pass | `test_closeout_register_grammar.py:253` |
| AC-11 | `REFUSE: issue FFMPEG-LIBDVDCSS-BUNDLED decision_log item 1 is not valid YAML: line 9: … mixes a mapping and a sequence at one indentation.` (exit 1) | `OK: … 28 recorded decision(s) reconciled against 28 Decisions Log row(s)` (exit 0) | task rows 0 and 6 |

Row 1's Red is 18 failed and 15 passed. AC-7 and every AC-3 case but U+0085 pass in Red by design: they guard behaviour that already holds. `red-check.py` required `test_ac_1`, `test_ac_2`, `test_ac_4`, `test_ac_5` and `test_ac_6` and found 0 problems. Every failure block carries only an assertion diagnostic. The review-F1 correction added one case to `EDGE_STRINGS`; its own Red is `s49b-f1-red`, below.

Receipts: `C:/Temp/av-kit/s49b-baseline.txt`, `s49b-base-py.txt`, `s49b-done-proof-red.txt`, `s49b-red.txt` (with `.exit`), `s49b-red-check.txt`, `s49b-save-green.txt`, `s49b-flag-green.txt`, `s49b-selftest.txt`, `s49b-reformat.txt`, `s49b-reword.txt`, `s49b-reword-render.txt`, `s49b-done-proof.txt`, `s49b-resolve.txt`, `s49b-r7-render.txt`, `s49b-r7-issues.txt`, `s49b-r7-status.txt`, `s49b-empty-id.txt`, `s49b-f1-red.txt` (with `.exit` and `.txt.exit`), `s49b-f1-red-check.txt`, `s49b-f1-green.txt`, `s49b-f1-register-same.txt`, the gate's `s49b-gate-h1.txt` and `s49b-D6-<id>.txt`, `drift-check.txt`, `openapi-check.txt` and `task-unchecked.txt`.

**Execution note, row 3's temp folder.** Row 3's command, run as written under the default temp folder, failed: `tests/tooling/test_framework_adoption.py::test_evidence_contract_real_cli_selftests` saw 5 of 219 selftest arms fail. All five are `grouping-*-declared-*` arms whose plan resolved its root to `C:\Users\Mat`, which is `CLOSEOUT-SELFTEST-ANCESTOR-AGENT-DIR` (open, P3). That issue has measured the same five arms since 2026-11-04. None of them is a `decision-issue-` arm. Row 3 was rerun with `TMP` and `TEMP` at `C:/Temp/av-kit/s49b/tmp`, which row 0 and the gate already set under RC1 ECN-2. The rerun passed, and it is the receipt above. The row's command doesn't set the temp folder, so this is a deviation from it as written, not a change to any check.

### Commands Executed

```json
{"schema_version": "evidence.v1", "check_id": "s49b-row0-baseline", "command": "$env:ELECTRON_RUN_AS_NODE=$null; rtk proxy pwsh -NoProfile -File docs/execution/plans/2026-11-05-closeout-register-grammar/baseline.ps1 *> C:/Temp/av-kit/s49b-baseline.txt (task.md row 0 Validation cell, verbatim, from P:/av-kit)", "cwd": "P:/av-kit", "scope": "Row 0: baseline.sha and baseline-dirty.txt, the register hash, uv sync, the base Python suite with TMP and TEMP outside the home folder, the done-proof's Red, and both plan-local selftests", "phase": "red", "exit_code": 0, "result": "pass", "tested_state": "HEAD 19001ca (baseline.sha) plus the plan folder", "output": "baseline.sha 19001ca7ee19e4cdd2bf293782d69216bec5d7a9; baseline-dirty.txt 8 paths; register sha256 900b2cb05e7266fad83f329e555f1da135f6268da39662a80dc35f60a12d8fe4; base suite 1193 passed in 113.04s; REFUSE: issue FFMPEG-LIBDVDCSS-BUNDLED decision_log item 1 is not valid YAML ... mixes a mapping and a sequence at one indentation; done-proof red exit=1; red-check selftest: 36 fixture(s), 0 wrong; identity selftest: 0 failure(s); baseline: all steps exit 0"}
```

```json
{"schema_version": "evidence.v1", "check_id": "s49b-row1-red", "command": "rtk proxy uv run pytest tests/tooling/test_closeout_register_grammar.py --tb=short -q *> C:/Temp/av-kit/s49b-red.txt; then red-check.py --require test_ac_1 --require test_ac_2 --require test_ac_4 --require test_ac_5 --require test_ac_6 (task.md row 1 Validation cell, verbatim, from P:/av-kit)", "cwd": "P:/av-kit", "scope": "Red: AC-1 to AC-7 against the unchanged model.save and validator", "phase": "red", "exit_code": 0, "result": "pass", "tested_state": "HEAD 19001ca plus row 1", "output": "18 failed, 15 passed in 9.06s (child exit 1). red-check: 1 receipt(s), 5 required test(s), 0 problem(s). The row exits 0 because red-check confirms decisive failures."}
```

```json
{"schema_version": "evidence.v1", "check_id": "s49b-row2-save-green", "command": "rtk proxy uv run pytest tests/tooling/test_closeout_register_grammar.py -k \"test_ac_1_ or test_ac_2_ or test_ac_3_\" --tb=short -q *> C:/Temp/av-kit/s49b-save-green.txt (task.md row 2 Validation cell, verbatim, from P:/av-kit)", "cwd": "P:/av-kit", "scope": "Green for the writer: AC-1 to AC-3 after model.save changed", "phase": "green", "exit_code": 0, "result": "pass", "tested_state": "HEAD 19001ca plus rows 1 to 3", "output": "29 passed, 4 deselected in 0.20s"}
```

```json
{"schema_version": "evidence.v1", "check_id": "s49b-row3-flag-green", "command": "$env:TMP='C:\\Temp\\av-kit\\s49b\\tmp'; $env:TEMP=$env:TMP; rtk proxy uv run pytest tests/tooling/ --tb=short -q *> C:/Temp/av-kit/s49b-flag-green.txt; then rtk proxy uv run python tools/validate_closeout_artifacts.py --selftest *> C:/Temp/av-kit/s49b-selftest.txt and Select-String ' 0 failure' (task.md row 3 Validation cell, with the temp folder of RC1 ECN-2, from P:/av-kit)", "cwd": "P:/av-kit", "scope": "Green for the reader: every tooling test and the validator's selftest after --decision-issue became repeatable", "phase": "green", "exit_code": 0, "result": "pass", "tested_state": "HEAD 19001ca plus rows 1 to 3", "output": "124 passed in 63.72s. RESULT: 219 arm(s), 0 failure(s) [67 must-OK arms, so the tool is not refusing everything]. New arms ok: decision-issue-repeated-reconciled-ok 0/OK, decision-issue-repeated-first-issue-read 1/REFUSE, decision-issue-same-id-twice-is-usage 2/USAGE, decision-issue-absent-beside-present-refused 1/REFUSE"}
```

```json
{"schema_version": "evidence.v1", "check_id": "s49b-row3-empty-id", "command": "pwsh -NoProfile -File C:/Temp/av-kit/s49b/empty-id.ps1: runs rtk proxy uv run python tools/validate_closeout_artifacts.py --reflection docs/execution/reflections/2026-11-04-rc2-fetch-uninstall-reflection.md --reflection-template docs/execution/reflections/TEMPLATE.md --decision-source .agent/context/known-issues.yaml --decision-issue \"\" --decision-issue FFMPEG-LIBDVDCSS-BUNDLED *> C:/Temp/av-kit/s49b-empty-id.txt, then exits 0 only when the child exits 2 and the receipt starts with the USAGE message", "cwd": "P:/av-kit", "scope": "Boundary Inventory: an empty --decision-issue value is Usage", "phase": "green", "exit_code": 0, "result": "pass", "tested_state": "19001ca7ee19e4cdd2bf293782d69216bec5d7a9+a04ad6195a865a83207dde0324a7845eca25b019e0f75e0cfb45f8925b3ffc13", "output": "USAGE: --decision-issue needs an issue ID; an empty value names no issue. child exit=2 usage-message=True"}
```

```json
{"schema_version": "evidence.v1", "check_id": "s49b-row4-reformat", "command": "rtk proxy uv run python docs/execution/plans/2026-11-05-closeout-register-grammar/register-rewrite.py --mode reformat --expect-sha256 900b2cb05e7266fad83f329e555f1da135f6268da39662a80dc35f60a12d8fe4 *> C:/Temp/av-kit/s49b-reformat.txt (task.md row 4 Validation cell, verbatim, from P:/av-kit)", "cwd": "P:/av-kit", "scope": "AC-9: the register saved once through the new save, layout only", "phase": "green", "exit_code": 0, "result": "pass", "tested_state": "HEAD 19001ca plus rows 1 to 4", "output": "decision logs read: 61 of 67; refused by the placeholder test only, as planned: CAPTURE-FLATTEN-WITH-BACKUP, CONVERT-EXTRACT-STREAM-INDEX-MISMATCH, MCP-SETUP-PROMPT, MCP-TTS-GENERATE-SYNCHRONOUS, QUEUE-PILL-TOKEN-DRIFT, TTS-VOICE-PACK-LAZY-FETCH; register sha256 before=900b2cb0...; target sha256 after=730780dde6c51e257689aa4112ddbc6d9647884962d00e4f88aaae321fe10c91 CRLF=0 LF=4092; parsed fields changed: 0 (planned 0); register-rewrite: 0 problem(s)"}
```

```json
{"schema_version": "evidence.v1", "check_id": "s49b-row5-reword", "command": "$sha from s49b-reformat.txt; rtk proxy uv run python docs/execution/plans/2026-11-05-closeout-register-grammar/register-rewrite.py --mode reword --expect-sha256 $sha *> C:/Temp/av-kit/s49b-reword.txt; then rtk proxy uv run python tools/issue_triage.py render --check (task.md row 5 Validation cell, verbatim, from P:/av-kit)", "cwd": "P:/av-kit", "scope": "AC-10: the 15 planned fields reworded, bound to row 4's hash; known-issues.md unchanged", "phase": "green", "exit_code": 0, "result": "pass", "tested_state": "HEAD 19001ca plus rows 1 to 5", "output": "decision logs read: 67 of 67; register sha256 before=730780dd...; target sha256 after=d727584646ea62f4fc79f76c669e5c8dc886a086f97c777ecd82edfef4629c0a CRLF=0 LF=4092; parsed fields changed: 15 (planned 15); register-rewrite: 0 problem(s); OK: known-issues.md is up-to-date"}
```

```json
{"schema_version": "evidence.v1", "check_id": "s49b-row6-done-proof", "command": "rtk proxy uv run python tools/validate_closeout_artifacts.py --reflection docs/execution/reflections/2026-11-04-rc2-fetch-uninstall-reflection.md --reflection-template docs/execution/reflections/TEMPLATE.md --reflection-schema .agent/schemas/reflection.v1.yaml --decision-source <Session 49 plan, both handoffs, the grouping> --decision-source .agent/context/known-issues.yaml --decision-issue UNINSTALL-LEAVES-INSTALLER-COPY --decision-issue FFMPEG-LIBDVDCSS-BUNDLED *> C:/Temp/av-kit/s49b-done-proof.txt (task.md row 6 Validation cell, verbatim, from P:/av-kit)", "cwd": "P:/av-kit", "scope": "AC-11: Session 49's reflection check against the register as save wrote it, both issues in one run, no extract", "phase": "green", "exit_code": 0, "result": "pass", "tested_state": "HEAD 19001ca plus rows 1 to 5", "output": "OK: all 15 template section(s) present; all 7 required schema field(s) emitted; 4 design rule(s), all sourced; 28 recorded decision(s) reconciled against 28 Decisions Log row(s)"}
```

```json
{"schema_version": "evidence.v1", "check_id": "s49b-row7-records", "command": "register-rewrite.py --mode resolve --set-file C:/Temp/av-kit/s49b-resolve.json --expect-sha256 <row 5 after> *> C:/Temp/av-kit/s49b-resolve.txt; issue_triage.py render; issue_triage.py triage --output .agent/context/triage-output.yaml; then pwsh -NoProfile -File row7-check.ps1 (task.md row 7 Validation cell, verbatim, from P:/av-kit)", "cwd": "P:/av-kit", "scope": "Row 7: this issue resolved, the issue renders and triage output regenerated, grouping §6 row 49b updated, the hub a no-op", "phase": "static", "exit_code": 0, "result": "pass", "tested_state": "HEAD 19001ca plus rows 1 to 7", "output": "register sha256 before=d7275846...; target sha256 after=9a4a33c2715815fff9febbde08ef869031a0c34ad8a79532d39d9f4d768e4de9 CRLF=0 LF=4094; parsed fields changed: 3 (planned 3); register-rewrite: 0 problem(s). Drift check passed (126 MEUs). Issue renders match. resolved [('D-279', 'triage'), ('D-274', 'triage')]"}
```

```json
{"schema_version": "evidence.v1", "check_id": "s49b-f1-red", "command": "rtk proxy uv run pytest tests/tooling/test_closeout_register_grammar.py --tb=short -q > C:/Temp/av-kit/s49b-f1-red.txt 2>&1 (child exit 1, recorded in s49b-f1-red.exit and s49b-f1-red.txt.exit); then rtk proxy uv run python docs/execution/plans/2026-11-05-closeout-register-grammar/red-check.py --require test_ac_2_edge_string_passes_the_grammar C:/Temp/av-kit/s49b-f1-red.txt > C:/Temp/av-kit/s49b-f1-red-check.txt 2>&1", "cwd": "P:/av-kit", "scope": "Review F1 Red: the newline-only edge string added to EDGE_STRINGS, before model.py changed", "phase": "red", "exit_code": 0, "result": "pass", "tested_state": "HEAD 19001ca plus rows 1 to 7 and the new test case", "output": "1 failed, 34 passed in 11.69s: test_ac_2_edge_string_passes_the_grammar[newline-only] assert \"known-issues.yaml is not valid YAML: line 20: '...' is not a 'key: value' line.\" is None, with the file ending `reasoning: |2+` then `...`. red-check: 1 receipt(s), 1 required test(s), 0 problem(s)"}
```

```json
{"schema_version": "evidence.v1", "check_id": "s49b-f1-green", "command": "rtk proxy uv run pytest tests/tooling/test_closeout_register_grammar.py --tb=short -q > C:/Temp/av-kit/s49b-f1-green.txt 2>&1; then rtk proxy uv run python -B C:/Temp/av-kit/s49b/f1-register-same.py > C:/Temp/av-kit/s49b-f1-register-same.txt 2>&1", "cwd": "P:/av-kit", "scope": "Review F1 Green: _represent_str double-quotes a newline-only value; today's register re-saved through the changed save is byte-identical, so the register needs no rewrite", "phase": "green", "exit_code": 0, "result": "pass", "tested_state": "19001ca7ee19e4cdd2bf293782d69216bec5d7a9+90629cd735535f484952c458fc8670bc08ae6899aad520899c3002d93b826e4e", "output": "35 passed in 6.26s. register sha256 9a4a33c2715815fff9febbde08ef869031a0c34ad8a79532d39d9f4d768e4de9; re-saved sha256 9a4a33c2715815fff9febbde08ef869031a0c34ad8a79532d39d9f4d768e4de9; identical True"}
```

```json
{"schema_version": "evidence.v1", "check_id": "s49b-gate-h1-2", "command": "$env:ELECTRON_RUN_AS_NODE=$null; rtk proxy pwsh -NoProfile -File docs/execution/plans/2026-11-05-closeout-register-grammar/session-gate.ps1 *> C:/Temp/av-kit/s49b-gate-h1.txt; $code=$LASTEXITCODE; Select-String -Path C:/Temp/av-kit/s49b-gate-h1.txt -Pattern ' exit=','not_run','tested_state','_sha256 ','outside scope','mismatch','session-gate:'; exit $code", "cwd": "P:/av-kit", "scope": "H1-2, the registered D6 gate on the whole tree after rows 0 to 7 and the review-F1 correction (rerun after it): identity, every static check, the full Python suite with the validator's selftest, both renders, then the identity again", "phase": "full", "exit_code": 0, "result": "pass", "fresh": true, "snapshot": false, "tested_state": "19001ca7ee19e4cdd2bf293782d69216bec5d7a9+90629cd735535f484952c458fc8670bc08ae6899aad520899c3002d93b826e4e", "output": "py-lint all checks passed; tools-lint all checks passed; task-contract OK: 24 row(s), 22 fully checked, 2 exempt (view_file): H1-5, H2-1; scope-paths changed paths: 21 outside scope: [] head moved (S4): False; red-check selftest: 36 fixture(s), 0 wrong; py-tests 1228 passed in 116.40s; state-render drift check passed (126 MEUs); issues-render OK: known-issues.md is up-to-date; tested_state before and after identical. Baseline failures excused: none. session-gate: all steps exit 0"}
```

```json
{"schema_version": "evidence.v1", "check_id": "s49b-h1-3-render", "command": "rtk proxy uv run python tools/meu_status.py render --check *> C:/Temp/av-kit/drift-check.txt", "cwd": "P:/av-kit", "scope": "H1-3: rendered state regions after the current focus was updated. No MEU status changes in this session", "phase": "static", "exit_code": 0, "result": "pass", "tested_state": "19001ca7ee19e4cdd2bf293782d69216bec5d7a9+90629cd735535f484952c458fc8670bc08ae6899aad520899c3002d93b826e4e", "output": "Drift check passed - SSOT loaded (126 MEUs, 12 phases), rendered regions match on-disk content"}
```

```json
{"schema_version": "evidence.v1", "check_id": "s49b-h1-4-openapi", "command": "rtk proxy uv run python -c '<task.md row H1-4: packages/api diff against baseline.sha plus untracked files>' *> C:/Temp/av-kit/openapi-check.txt", "cwd": "P:/av-kit", "scope": "H1-4: the basis for skipping the OpenAPI check", "phase": "static", "exit_code": 0, "result": "pass", "tested_state": "19001ca7ee19e4cdd2bf293782d69216bec5d7a9+90629cd735535f484952c458fc8670bc08ae6899aad520899c3002d93b826e4e", "output": "packages/api changes: []"}
```

### Quality Gate Results

`s49b-gate-h1-2` is the fresh full record, and its last line is:

> session-gate: all steps exit 0

- **Static:** `py-lint`, `tools-lint`, `task-contract` (24 rows, 22 fully checked, H1-5 and H2-1 exempt as `view_file`), `scope-paths` (21 changed paths, none outside scope, HEAD still `19001ca`) and `red-check-selftest` (36 fixtures, 0 wrong) all exit 0.
- **Suites:** `py-tests` 1228 passed in 116.40s. That is the baseline's 1193 plus this session's 35. Before the review-F1 correction the same gate passed with 1226. Baseline failures excused: none, because row 0 saw no failure.
- **State:** `state-render` and `issues-render` exit 0.
- **Skipped, each printed with its reason:** `py-types` (nothing under `packages/` changes); `ui-types`, `ui-lint`, `ui-tests`, `ui-build` and `ui-electron` (nothing under `ui/` changes, and no UI test reads these files); `mcp-types`, `mcp-build`, `mcp-tests` and `mcp-audit` (no MCP change); `openapi` (no `packages/api` change, H1-4); `build-record` (no build).
- **Identity:** `tested_state` `19001ca7ee19e4cdd2bf293782d69216bec5d7a9+90629cd735535f484952c458fc8670bc08ae6899aad520899c3002d93b826e4e`, the same before and after. The gate set `TMP` and `TEMP` to `C:/Temp/av-kit/s49b/tmp` (RC1 ECN-2) and cleared `ELECTRON_RUN_AS_NODE`. H1-3 and H1-4 were rerun after the gate, and a recompute gives the same state. Round 1 of the review saw the state before the F1 correction, ending `a04ad619`.
- **Lint and format on the three changed Python files:** `ruff check` passed and `ruff format --check` reported "3 files already formatted".

---

## Changed Files

| File | Action | Summary |
|------|--------|---------|
| `tools/issue_triage/model.py` | modified | `_LINE_SEPARATORS`, `_SsotDumper`, `_represent_str` (a lone newline double-quoted after review F1, `:336-344`) and `_represent_dict` (`:310-360`); `save` renders, checks the text loads back equal, then writes (`:383-407`). CRLF kept |
| `tools/validate_closeout_artifacts.py` | modified | Usage line; `Sequence` import; `decision_sources` over every named issue; signatures of `check_decisions_log` and `check_reflection`; the run() checks for an empty or repeated ID; argparse `append`; four selftest arms. CRLF kept |
| `tests/tooling/test_closeout_register_grammar.py` | new | AC-1 to AC-7, 35 cases. CRLF, like its peer |
| `.agent/docs/human-decision-protocol.md` | modified | `:201` usage shows `ID ...`; `:218-221` the flag repeats once per issue, each must be present, and naming one twice is a usage error. CRLF kept |
| `.agent/context/known-issues.yaml` | modified | Rows 4, 5 and 7 through `model.save`: every line re-laid once, 15 fields reworded, this issue resolved. LF |
| `.agent/context/known-issues.md`, `triage-output.yaml` | modified | Rendered and regenerated in row 7. The render moves this issue from active to resolved. The triage output picks up the 15 rewordings |
| `.agent/context/grouping/2026-11-04-rc2-triage-residuals-session-grouping.md` | modified | §6 row 49b: status `executed`, the plan folder. CRLF kept |
| `.agent/context/current-focus.md` | modified | Session 49b entry on top. CRLF kept |
| Plan folder: `baseline.ps1`, `baseline.sha`, `baseline-dirty.txt`, `identity.py`, `red-check.py`, `register-rewrite.py`, `session-gate.ps1`, `task.md` | new or modified | The plan's scripts and records |

```diff
-    with ssot_path.open("w", encoding="utf-8", newline="\n") as f:
-        f.write("# Known Issues SSOT — managed by tools/issue_triage.py\n")
-        yaml.dump(data, f, default_flow_style=False, allow_unicode=True, sort_keys=False, width=200)
+    text = "# Known Issues SSOT — managed by tools/issue_triage.py\n" + yaml.dump(
+        data, Dumper=_SsotDumper, default_flow_style=False, allow_unicode=True,
+        sort_keys=False, width=10**9,
+    )
+    if yaml.safe_load(text) != data:
+        raise IssueTriageError("The rendered SSOT does not load back equal to the data; not saved")
+    ...
+    with ssot_path.open("w", encoding="utf-8", newline="\n") as f:
+        f.write(text)
```

```diff
-def decision_sources(paths: list[str], issue: str | None) -> dict[str, tuple[str, str]]:
+def decision_sources(paths: list[str], issues: Sequence[str]) -> dict[str, tuple[str, str]]:
 ...
-                default_stage, label = "triage", f"issue {issue}"
-                entries = issue_decision_log(text, name, issue)
+                reads = [
+                    ("triage", f"issue {issue}", issue_decision_log(text, name, issue))
+                    for issue in issues
+                ]
 ...
-        refuse_repeated_ids(entries, label)
-        for decision_id, stage in entries:
+        for default_stage, label, entries in reads:
+            refuse_repeated_ids(entries, label)
+            for decision_id, stage in entries:
```

```diff
+        issues = args.decision_issue or []
+        if any(not issue.strip() for issue in issues):
+            raise Usage("--decision-issue needs an issue ID; an empty value names no issue.")
+        repeated = sorted({issue for issue in issues if issues.count(issue) > 1})
+        if repeated:
+            raise Usage(f"--decision-issue {', '.join(repeated)} is given more than once; ...")
 ...
     p.add_argument(
         "--decision-issue",
+        action="append",
+        default=None,
```

---

## Codex Validation Report

### Recheck Protocol

1. Read Scope + AC table
2. Verify each AC against Evidence section (file:line, not memory)
3. Independently probe the claimed behavior and compare decisive output
4. Verify the full gate is fresh and matches current D6 inputs; rerun if changed or unproven
5. Record findings below

### Findings

| # | Severity | Finding | File:Line | Recommendation | Status |
|---|----------|---------|-----------|----------------|--------|
| F1 | Medium (non-blocking) | Round 1: a string that is a lone newline, as the file's last value, was written keep-chomped and closed with `...`, which `check_yaml_subset` refuses (AC-1) | `tools/issue_triage/model.py:339` | Double-quote it and add a regression with it last | fixed: Mat chose to fix it now; Red `s49b-f1-red`, Green `s49b-f1-green`, gate rerun |

### Verdict

Round 1 (loop `s49b-execution-2026-11-05-closeout-register-grammar`): `approved`, intent achieved, 0 blocking findings, one non-blocking finding F1. Mat directed the F1 fix ("Fix it now", 2026-11-05, D-289). The fix changed `tools/issue_triage/model.py`. Round 2 reviewed the correction on the new tested state: `approved`, F1 fixed, no new findings. Round 3 confirmed that the tested state was unchanged and reissued the three rounds as one rolling report (D-290): `approved`, intent achieved, 0 findings. The canonical review is the reviewer's round-3 file, copied byte for byte after the review-state and approved-state checks passed on it (`review-state-check.txt`, `exec-review.txt`: approved at round 3 of 6, 0 open blocking findings).

---

## Deferred Items

| Item | Kind | Deferred-to | Basis |
|------|------|-------------|-------|
| `CLOSEOUT-SELFTEST-ANCESTOR-AGENT-DIR` | out-of-scope | — | Open P3 issue; gates run with the temp folder outside the home folder (RC1 ECN-2). This session's execution note shows the five arms it names, unchanged |
| Commit and push | out-of-scope | — | The commit waits for Mat's direction (H2-5) |

---

## Decision Log

```yaml
decision_log:
  - id: D-289
    stage: execution
    question: "Is review F1, a lone newline written last in the register, fixed now or registered as a known issue?"
    resolution: human
    class: two-way
    chosen: "Fixed now: _represent_str double-quotes a value that is exactly one newline, with a regression case written last"
    source_tag: Human-approved
    precedents: ["tools/issue_triage/model.py:336-344 — the string representer the fix extends", "tests/tooling/test_closeout_register_grammar.py:28 — the new edge string"]
    research: { engine: none, sources: [] }
    reasoning: "The brief offered fixing it now, registering a known issue, and doing nothing. No value in today's register triggers it, so doing nothing was real, but the next save that ends on a lone newline would refuse the closeout check this session exists to unblock. The fix is one condition, and re-saving today's register through it is byte-identical."
    human_message_reference: "USER_EXPLICIT 2026-11-05 'Fix it now'"
  - id: D-290
    stage: execution
    question: "How does round 2's standalone report reach the canonical rolling review?"
    resolution: autonomous
    class: two-way
    chosen: "The reviewer reissued the complete rolling report in round 3: round 1's body unchanged and one Recheck section per later round, each with its own Findings table. It was validated in C:/Temp/av-kit before being copied byte for byte"
    source_tag: Local Canon
    precedents: [".agent/workflows/execution-critical-review.md:25 — the orchestrator copies the complete rolling report after validating it and never edits findings", "tools/validate_closeout_artifacts.py:562 — a Recheck section without its own Findings table counts against approval", ".agent/context/handoffs/REVIEW-TEMPLATE.md:108 — one Recheck section per round, in this file"]
    research: { engine: none, sources: [] }
    reasoning: "Appending round 2 as written put its Findings table outside its Recheck section, and H1-7b refused it. Restructuring it myself would have edited the reviewer's findings. A third round cost 931,893 tokens; the canonical file went back to round 1's bytes in the meantime."
```

---

## History

| Event | Date | Agent | Detail |
|-------|------|-------|--------|
| Created | 2026-11-05 | claude-code-local (Claude Opus 5.5) | Initial handoff after H1-2 |
| Review round 1 | 2026-11-05 | codex-independent-reviewer | `approved`, F1 non-blocking |
| F1 corrected | 2026-11-05 | claude-code-local (Claude Opus 5.5) | Lone newline double-quoted; Red, Green and the gate rerun; for round 2 |
| Review round 2 | 2026-11-05 | codex-independent-reviewer | `approved`, F1 fixed, no new findings |
| Review round 3 | 2026-11-05 | codex-independent-reviewer | `approved`, tested state unchanged; the complete rolling report (D-290) |
