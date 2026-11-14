---
date: "2026-11-14"
project: "2026-11-14-review-limits-no-token-budget"
meu: "none"
status: "complete"
action_required: "VALIDATE_AND_APPROVE"
template_version: "2.2"
verbosity: "standard"
plan_source: "docs/execution/plans/2026-11-14-review-limits-no-token-budget/implementation-plan.md"
build_plan_section: "non-product tooling and governance prose (review limits)"
agent: "claude-code-local (Claude Opus 5.5)"
reviewer: "codex (H1-7 execution review)"
predecessor: "none"
---

# Handoff: 2026-11-14-review-limits-no-token-budget-handoff

> **Status**: `complete`
> **Action Required**: `VALIDATE_AND_APPROVE`

---

## Scope

**MEU**: none. This is a tooling and governance session with no MEU. It ports the review-limits change from `P:/agentic-framework` commit `6dd76b7` into `tools/review_ledger.py`, so that review loops stop on their round caps and never on token spend. Every round's token usage is still recorded and shown.
**Build Plan Section**: none; this is non-product tooling and prose.
**Predecessor**: none.

- **The limits file (AC-1, D-730, D-731).** `.agent/review-limits.json` is new (schema `review-limits/1`).
  - `token_budgets` is `"off"`.
  - `rounds` are plan 3, execution 6, discovery 2, handoff 3 and multi-handoff 3.
  - The `tokens` map equals `TOKEN_BUDGETS`, so turning budgets back on restores today's numbers.
- **Resolution (AC-2, AC-3, AC-9, AC-10, AC-11).** `begin` resolves the loop's limits in this order:
  1. the repo file (the constants when it is absent);
  2. a `review_limits` frontmatter block in `--ac-file`, for plan and execution loops only, which must equal `task.md`'s block;
  3. `--round-budget` and `--token-budget N|off`, which may only tighten.

  A malformed file or block fails closed (exit 3). A `loosened` block is refused (exit 1), because this repo has no `tools/run_parameters.py` (D-733); the refusal names `continue`. The OK line prints `tokens=` and `source=`, and the ledger records `limits_source`.
- **The token stop (AC-4 to AC-8).** A loop whose `token_budget` is `"off"` has no `tokens` stop, whatever its usage. It still stops at its round cap.
  - `state` prints `off (N spent, not budgeted)` and a `limits:` line.
  - `continue --tokens` on such a loop is refused and leaves the ledger unchanged; `continue --rounds` still works.
  - A ledger written before the change loads and says `(pre-review-limits ledger)`. The survey loaded all 93 live ledgers.
  - A bad `token_budget` or an unknown `limits_source` key fails closed.
- **Selftest and wrapper (AC-12, AC-13).**
  - The ledger selftest went from 105 to 126 arms, with 0 failures, and every earlier arm is still there.
  - `Invoke-CodexDispatch.ps1 -GateOnly` gates a loop with no token budget.
  - `Test-CliDispatch.ps1` shows only the two baseline FAILs that D-739 names.
- **Prose and templates (AC-14, AC-15).**
  - The 22 inventory lines (P1 to P22) and the four `begin` examples now name where each cap comes from.
  - `AGENTS.md` keeps 126 lines (17,861 bytes).
  - Both plan templates are v2.3 with a commented `review_limits` block, and the task template's cap note names `review_ledger.py state`.
- **Added at execution.** D-742: the `.agent/templates/` twins of both templates were re-synced. D-743, Mat's ruling: the 2026-09-26 rule map's `AGENTS.md` pin was updated (see the execution notes).

Not ported, per the plan: `run_parameters.py`, credits and `instantiate.py`. Nothing ships; these are repository tools and prose.

**Plan:** [implementation-plan.md](../../../docs/execution/plans/2026-11-14-review-limits-no-token-budget/implementation-plan.md). **Execution authorization:** `USER_EXPLICIT`, 2026-11-14, "proceed as recommended". Mat gave it after the plan review approved in round 2. It ratified D-737 (the execution loop opens with no `--token-budget`) and D-739.

---

## Acceptance Criteria

| AC | Type | Description | Source | Test(s) | Status |
|----|------|-------------|--------|---------|--------|
| AC-1 | unit | `LIMITS_FILE` holds the approved values, its `tokens` map equals `TOKEN_BUDGETS`, and `read_repo_limits` accepts it | Human-approved (D-730, D-731) | `tests/tooling/test_review_limits.py:222`, `:234` | ✅ |
| AC-2 | integration | `begin` under an `off` file writes `round_budget`, `token_budget` `"off"` and `limits_source.repo` for all five modes; with no file it uses the constants | Spec (UPSTREAM AC-5) | `tests/tooling/test_review_limits.py:245` (5 cases), `:262` (5 cases) (CLI by subprocess) | ✅ |
| AC-3 | integration | A malformed `LIMITS_FILE` makes `begin` exit 3 and write no ledger | Spec (UPSTREAM AC-6) | `tests/tooling/test_review_limits.py:309` (8 cases) (CLI by subprocess) | ✅ |
| AC-4 | unit | An `OFF` ledger has no `tokens` stop up to 10^12, and the readout says `off (` and `not budgeted`; a budget of 1 still stops | Spec (UPSTREAM AC-10) | `tests/tooling/test_review_limits.py:321` (4 cases), `:331` | ✅ |
| AC-5 | integration | `state` prints `off (0 spent, not budgeted)` and a `limits:` line naming the repo file; a legacy ledger says `(pre-review-limits ledger)` | Spec (UPSTREAM AC-10) | `tests/tooling/test_review_limits.py:341`, `:354` (CLI by subprocess) | ✅ |
| AC-6 | integration | `continue --tokens 1` on an `OFF` loop exits 1 with the ledger bytes unchanged; `continue --rounds 1` raises the cap | Spec (UPSTREAM AC-11) | `tests/tooling/test_review_limits.py:367`, `:377` (CLI by subprocess) | ✅ |
| AC-7 | unit | An `OFF` loop still stops at its round cap | Human-approved (D-730) | `tests/tooling/test_review_limits.py:391` | ✅ |
| AC-8 | integration | `state` exits 3 on a bad `token_budget` or an unknown `limits_source` key; an integer budget with no source loads | Spec (UPSTREAM AC-12) | `tests/tooling/test_review_limits.py:406` (6 cases), `:413`, `:422` (CLI by subprocess); `ledger-survey.py` on 93 live ledgers (row 8) | ✅ |
| AC-9 | integration | A plan block applies to plan and execution loops, `repo` with equal values is accepted, discovery ignores it; a malformed block exits 3 and a block that differs from `task.md` exits 1 | Spec (UPSTREAM AC-7, AC-8) | `tests/tooling/test_review_limits.py:436` (2 cases), `:449`, `:458`, `:474` (4 cases), `:487` (CLI by subprocess) | ✅ |
| AC-10 | integration | A `loosened` block is refused with exit 1 and the D-733 message naming `continue`, with no ledger written | Local Canon (D-733) | `tests/tooling/test_review_limits.py:503` (CLI by subprocess) | ✅ |
| AC-11 | integration | Flags only tighten; loosening is refused; bad values are argparse exit 2 | Spec (UPSTREAM AC-9) | `tests/tooling/test_review_limits.py:519`, `:527`, `:537`, `:545`, `:558` (3 cases) (CLI by subprocess) | ✅ |
| AC-12 | unit | `review_ledger.py selftest` exits 0 with 0 failures, keeps every earlier arm, and has the upstream `limits-*` arms and `limits-loosened-without-run-parameters` | Local Canon (V31) | `tools/review_ledger.py selftest` and `selftest-arms-check.py --before selftest-arms-before.txt` (row 4) | ✅ |
| AC-13 | integration | `-GateOnly` against a plan loop under the new ledger exits 0 and prints `dispatch kind 'plan'` and `-GateOnly: gate result`; `dispatch-check.py` accepts the `Test-CliDispatch.ps1` receipt | Local Canon (`Invoke-CodexDispatch.ps1:474`) | Row 8 (`rl-gate-begin`, `rl-gate-only`, `rl-dispatch`, `rl-dispatch-check`); `dispatch-check.py --selftest` (row 0) | ✅ |
| AC-14 | unit | No inventory phrase remains; each line and the four `begin` examples name `.agent/review-limits.json` or `review_limits`; `AGENTS.md` ≤ 126 lines and < 20,000 bytes | Local Canon (single-statement rule; AGENTS size limits) | `prose-check.py --rows P1-P22 --begin-examples --agents-size` (row 6); `prose-check.py --selftest` (row 0) | ✅ |
| AC-15 | unit | Both templates are v2.3 with the commented block and the cap note; `lint_task_contract.py` and the closeout selftest still pass | Local Canon (D-734) | `prose-check.py --templates`, `lint_task_contract.py`, `validate_closeout_artifacts.py --selftest` (row 7) | ✅ |

<!-- CACHE BOUNDARY -->

---

## Evidence

### FAIL_TO_PASS

| Test | Red Output (hash/snippet) | Green Output | File:Line |
|------|---------------------------|--------------|-----------|
| AC-1 | `review-limits.json does not exist` | pass | `test_review_limits.py:222` |
| AC-2 | `assert 'tokens=off' in "OK: opened loop 'loop-plan' mode=plan budget=3 tokens=10,500,000..."` | pass | `test_review_limits.py:245` |
| AC-3 | `assert 0 == 3`: the old `begin` ignored the file and opened the loop | pass | `test_review_limits.py:309` |
| AC-4, AC-7 | `the ledger has no review-limits path` (the module had no `resolve_limits`) | pass | `test_review_limits.py:321`, `:391` |
| AC-5 | `assert 'off (0 spent, not budgeted)' in ...` | pass | `test_review_limits.py:341` |
| AC-6 | `continue --tokens 1`: `assert 0 == 1` | pass | `test_review_limits.py:367` |
| AC-8 to AC-11 | each refused value opened a loop or loaded (`assert 0 == 3`, `assert 0 == 1`, `assert 0 == 2`) | pass | `test_review_limits.py:406-558` |

Row 1's Red was 49 failed and 6 passed. `red-check.py` required `test_ac_1`, `test_ac_2`, `test_ac_3`, `test_ac_4`, `test_ac_5`, `test_ac_6`, `test_ac_9`, `test_ac_10` and `test_ac_11`, and found 0 problems. Every failure block carries an assertion diagnostic. The six that passed in Red are negatives that already held: AC-2's no-file cases, AC-4's numeric-budget case and AC-8's integer-budget case.

Receipts:
- `C:/Temp/av-kit/rl/rl-baseline.txt` and `rl-base-py.txt`;
- `rl-red.txt` (with `.exit`), `rl-red-check.txt`, `rl-begin-green.txt` and `rl-green.txt`;
- `rl-selftest.txt`, `rl-arms-check.txt` and `rl-tooling.txt`;
- `rl-prose-workflows.txt`, `rl-prose-workflows-first.txt`, `rl-prose.txt`, `rl-templates.txt`, `rl-task-lint.txt` and `rl-closeout-selftest.txt`;
- `rl-existing-ledgers.txt`, `rl-gate-begin.txt`, `rl-gate-only.txt`, `rl-dispatch.txt` and `rl-dispatch-check.txt`;
- `rl-fa-check.txt`, plus the gate's `rl-gate-h1.txt` and `rl-D6-<id>.txt`;
- `rl-render-check.txt`, `openapi-check.txt` and `task-unchecked.txt`.

**Execution notes.** Each is a deviation from a row's command as written, or from the plan. None changes a check.

- Row 0: `baseline.ps1` checks that the ledger is HEAD's by reading the CRLF work-tree copy as LF, because the blob is LF under `text=auto`. The two raw hashes differ (`8e9e7aa3…` with 2,576 CRLF and 0 bare LF, against the blob's `2601b915…`), and the check prints `ledger equals HEAD (CRLF read as LF): True`.
- Row 1: the cell says AC-7 passes in Red by design. It failed instead, because the test first asserts `hasattr(module, "resolve_limits")` (`test_review_limits.py:391`), and the old ledger had no such function. AC-7 isn't among red-check's `--require` ids, so the row's check is unchanged. AC-7's behaviour assertions ran in Green.
- Rows 1 to 3: the tests' `output()` helper prefixes each child line with `child| ` (`test_review_limits.py:177`), so an assertion diagnostic shows the child's own output.
- Row 4: the tooling suite inherits TMP; under the user's TMP the closeout validator selftest fails 5 arms (RC1 ECN-2, C:/Users/Mat/.agent ancestor; receipt C:/Temp/av-kit/rl/rl-tooling-usertmp is the first run). Rerun with TMP/TEMP=C:/Temp/av-kit/rl/tmp, as row 0's base suite ran: 184 passed.
- Row 5: its command passes --begin-examples, which checks all four examples, including SKILL.md (row 6's edit). First run: 1 problem (SKILL.md only; P1-P11 and the three workflow examples ok). Rerun after row 6's edits.
- Row 7: the first run omitted the row environment that task.md line 30 sets (RECEIPTS_DIR=C:/Temp/av-kit), so lint_task_contract.py failed closed (exit 3, "RECEIPTS_DIR is unset"). The second run passed a TMP mangled by a shell quoting error, and the closeout selftest failed the same 5 grouping arms as row 4. The third run used RECEIPTS_DIR=C:/Temp/av-kit and TMP/TEMP=C:/Temp/av-kit/rl/tmp: prose-check 0 problems, lint OK (25 rows), selftest 219 arms, 0 failures.
- H1-2: the first gate run stopped at tools-lint: 9 E501 lines (over 100 columns) in the new tests/tooling/test_review_limits.py. Rows 1 to 4 ran pytest but never ruff. Fixed with `ruff format` on that file only, which reflows lines and changes no logic. The file went from 531 to 562 lines, and ruff check on tools/review_ledger.py and tests/tooling/ is then clean. The gate was rerun from the start.
- H1-2, second gate run: every step through dispatch-check exited 0; py-tests exited 1 with 4 failures outside the row 0 baseline, all in tests/tooling/test_framework_adoption.py (test_review_pipeline_governance_static_oracles[none], test_governance_preservation_and_routing_inventory[history], two test_registry_contract_generic_class_census cases). Each says "REFUSE: template copies differ: PLAN": docs/execution/plans/2026-09-26-framework-update-adoption/checks/verify_adoption.py:153-157 requires docs/execution/plans/{PLAN,TASK}-TEMPLATE.md to equal .agent/templates/{PLAN,TASK}-TEMPLATE.md byte for byte, and row 7 changed only the first pair. The plan's Files Modified missed the twins. D-742 (autonomous, Local Canon: 2026-09-29-human-decision-protocol-adoption plan :38 re-synced the twins, D-6, AC-8; 2026-09-26 plan :76 "keep .agent/templates/ copies synchronized"): copy both templates into .agent/templates/ byte for byte, add them to Files Modified and to the gate's scope-paths allowed set, and rerun the gate from the start. state-render, closeout-selftest and identity-after were not_run in that run.
- H1-2, after D-742: tests/tooling/test_framework_adoption.py still failed the same 4 tests at the next oracle, "REFUSE: rule map identity mismatch: AGENTS.md" (verify_adoption.py:213-221): rule-preservation.md:183 pins AGENTS.md's postimage_sha256 (41b91b52...), and row 6's P20 edit changed AGENTS.md. A probe with only that pin set to the new hash passed 91 of 91 (rl-fa-check.txt); the rule map was restored byte for byte (sha256 3611e6a5...) and the decision went to Mat, as the three earlier pin changes had (2026-09-30 A-2, MEU-98 D-132, 2026-10-29). Mat chose "Update the pin (Recommended)" (D-743): the pin is now 11309a09..., rule-preservation.md is in Files Modified and the gate's allowed set, and the gate was rerun from the start.

### Commands Executed

```json
{"schema_version": "evidence.v1", "check_id": "rl-row0-baseline", "command": "$env:ELECTRON_RUN_AS_NODE=$null; rtk proxy pwsh -NoProfile -File docs/execution/plans/2026-11-14-review-limits-no-token-budget/baseline.ps1 *> C:/Temp/av-kit/rl/rl-baseline.txt (task.md row 0 Validation cell, verbatim, from P:/av-kit)", "cwd": "P:/av-kit", "scope": "Row 0: baseline.sha and baseline-dirty.txt, the ledger equal to HEAD's, the selftest's 105 arm names, uv sync, the base Python suite with TMP and TEMP outside the home folder, Test-CliDispatch with dispatch-check --exact-baseline, and the five plan-local selftests", "phase": "red", "exit_code": 0, "result": "pass", "tested_state": "HEAD 1abf669 (baseline.sha) plus the plan folder", "output": "baseline.sha 1abf6698c2112e42deb8c298ec04c9f439cc63c3; baseline-dirty.txt 13 paths; ledger equals HEAD (CRLF read as LF): True; selftest arms before: 105; base suite 49 failed, 2559 passed in 161.69s, every failure a test_review_limits.py id (row 1's file, written before the baseline ran); dispatch receipt Total 31 PASS 29 FAIL 2 SKIP 0, exit 1, FAIL names ['placeholder receipts dir refused', 'refusal created no placeholder dir']; dispatch-check selftest: 0 failure(s); baseline: all steps exit 0"}
```

```json
{"schema_version": "evidence.v1", "check_id": "rl-row1-red", "command": "rtk proxy uv run pytest tests/tooling/test_review_limits.py --tb=short -q *> C:/Temp/av-kit/rl/rl-red.txt; then red-check.py --require test_ac_1 --require test_ac_2 --require test_ac_3 --require test_ac_4 --require test_ac_5 --require test_ac_6 --require test_ac_9 --require test_ac_10 --require test_ac_11 (task.md row 1 Validation cell, verbatim, from P:/av-kit)", "cwd": "P:/av-kit", "scope": "Red: AC-1 to AC-11 against the unchanged ledger and no limits file", "phase": "red", "exit_code": 0, "result": "pass", "tested_state": "HEAD 1abf669 plus row 1", "output": "49 failed, 6 passed in 20.66s (child exit 1, rl-red.txt.exit). red-check: 1 receipt(s), 9 required test(s), 0 problem(s). The row exits 0 because red-check confirms decisive failures."}
```

```json
{"schema_version": "evidence.v1", "check_id": "rl-row2-begin-green", "command": "rtk proxy uv run pytest tests/tooling/test_review_limits.py -k \"test_ac_2_ or test_ac_3_ or test_ac_8_ or test_ac_9_ or test_ac_10_ or test_ac_11_\" --tb=short -q *> C:/Temp/av-kit/rl/rl-begin-green.txt (task.md row 2 Validation cell, verbatim, from P:/av-kit)", "cwd": "P:/av-kit", "scope": "Green for the limits path through begin: AC-2, AC-3 and AC-8 to AC-11", "phase": "green", "exit_code": 0, "result": "pass", "tested_state": "HEAD 1abf669 plus rows 1 to 2", "output": "43 passed, 12 deselected in 3.87s"}
```

```json
{"schema_version": "evidence.v1", "check_id": "rl-row3-green", "command": "rtk proxy uv run pytest tests/tooling/test_review_limits.py --tb=short -q *> C:/Temp/av-kit/rl/rl-green.txt (task.md row 3 Validation cell, verbatim, from P:/av-kit)", "cwd": "P:/av-kit", "scope": "Green for the token stop and the limits file: AC-1 to AC-11", "phase": "green", "exit_code": 0, "result": "pass", "tested_state": "HEAD 1abf669 plus rows 1 to 3", "output": "55 passed in 4.82s"}
```

```json
{"schema_version": "evidence.v1", "check_id": "rl-row4-selftest", "command": "rtk proxy uv run python tools/review_ledger.py selftest *> C:/Temp/av-kit/rl/rl-selftest.txt; then selftest-arms-check.py --before docs/execution/plans/2026-11-14-review-limits-no-token-budget/selftest-arms-before.txt; then the tooling suite with TMP and TEMP at C:/Temp/av-kit/rl/tmp (task.md row 4 Validation cell, verbatim, from P:/av-kit), with the temp folder of RC1 ECN-2", "cwd": "P:/av-kit", "scope": "AC-12: the ledger selftest keeps every earlier arm and adds the limits arms; the tooling suite runs it again", "phase": "green", "exit_code": 0, "result": "pass", "tested_state": "HEAD 1abf669 plus rows 1 to 4", "output": "RESULT: 126 arm(s), 0 failure(s) [62 must-OK arms, so the tool is not refusing everything]; arms: 126 in the receipt, 105 before, 21 required new; selftest-arms-check: 0 problem(s); tooling suite 184 passed in 55.12s"}
```

```json
{"schema_version": "evidence.v1", "check_id": "rl-row5-6-prose", "command": "rtk proxy uv run python docs/execution/plans/2026-11-14-review-limits-no-token-budget/prose-check.py --rows P1-P11 --begin-examples *> C:/Temp/av-kit/rl/rl-prose-workflows.txt (row 5, rerun after row 6); rtk proxy uv run python docs/execution/plans/2026-11-14-review-limits-no-token-budget/prose-check.py --rows P1-P22 --begin-examples --agents-size *> C:/Temp/av-kit/rl/rl-prose.txt (row 6) (task.md row 5 and 6 Validation cell, verbatim, from P:/av-kit)", "cwd": "P:/av-kit", "scope": "AC-14: the 22 inventory lines, the four begin examples and AGENTS.md's size", "phase": "green", "exit_code": 0, "result": "pass", "tested_state": "HEAD 1abf669 plus rows 1 to 6", "output": "row 5 first run: 1 problem, SKILL.md:282 only (row 6's edit); after row 6: prose-check: 0 problem(s). Row 6: ok AGENTS.md 126 lines, 17861 bytes; prose-check: 0 problem(s)"}
```

```json
{"schema_version": "evidence.v1", "check_id": "rl-row7-templates", "command": "$env:RECEIPTS_DIR='C:/Temp/av-kit'; TMP and TEMP at C:/Temp/av-kit/rl/tmp; rtk proxy uv run python docs/execution/plans/2026-11-14-review-limits-no-token-budget/prose-check.py --rows P1-P22 --begin-examples --agents-size --templates *> C:/Temp/av-kit/rl/rl-templates.txt; then lint_task_contract.py on this task.md; then validate_closeout_artifacts.py --selftest (task.md row 7 Validation cell, verbatim, from P:/av-kit)", "cwd": "P:/av-kit", "scope": "AC-15: both templates v2.3 with the commented block and the cap note, the create-plan §4 paragraph, the task contract and the closeout selftest", "phase": "green", "exit_code": 0, "result": "pass", "tested_state": "HEAD 1abf669 plus rows 1 to 7", "output": "ok templates v2.3, commented block, cap note, create-plan §4 paragraph; prose-check: 0 problem(s); OK: 25 row(s), 23 fully checked, 2 exempt (view_file): H1-5, H2-1; RESULT: 219 arm(s), 0 failure(s) [67 must-OK arms]"}
```

```json
{"schema_version": "evidence.v1", "check_id": "rl-row8-loops-wrapper", "command": "rtk proxy uv run python docs/execution/plans/2026-11-14-review-limits-no-token-budget/ledger-survey.py *> C:/Temp/av-kit/rl/rl-existing-ledgers.txt; begin rl-gate-probe with RECEIPTS_DIR=C:/Temp/av-kit/rl/gate *> rl-gate-begin.txt; Invoke-CodexDispatch.ps1 -LoopId rl-gate-probe -Kind plan -GateOnly *> rl-gate-only.txt; Test-CliDispatch.ps1 *> rl-dispatch.txt with its exit saved; dispatch-check.py *> rl-dispatch-check.txt (task.md row 8 Validation cell, verbatim, from P:/av-kit)", "cwd": "P:/av-kit", "scope": "AC-8 at runtime and AC-13: every live ledger loads under the new ledger, and the wrapper gates a loop with no token budget", "phase": "green", "exit_code": 0, "result": "pass", "tested_state": "HEAD 1abf669 plus rows 1 to 7", "output": "ledger-survey: 93 ledger(s), 93 loaded, 0 failed; 93 pre-review-limits. OK: opened loop 'rl-gate-probe' mode=plan budget=3 tokens=off producer='claude-opus' source=repo:0e4aa4f0ef28. [ledger] OK: round 1 permitted mode=plan (0/3 used, no stop active); [kind] dispatch kind 'plan', timeout 1800s.; [ledger] -GateOnly: gate result 'permitted'. Exiting without dispatching. dispatch receipt: Total 31 PASS 29 FAIL 2 SKIP 0; exit 1; FAIL names ['placeholder receipts dir refused', 'refusal created no placeholder dir']; dispatch-check: 0 problem(s)"}
```

```json
{"schema_version": "evidence.v1", "check_id": "rl-gate-h1-2", "command": "$env:ELECTRON_RUN_AS_NODE=$null; rtk proxy pwsh -NoProfile -File docs/execution/plans/2026-11-14-review-limits-no-token-budget/session-gate.ps1 *> C:/Temp/av-kit/rl/rl-gate-h1.txt; $code=$LASTEXITCODE; Select-String -Path C:/Temp/av-kit/rl/rl-gate-h1.txt -Pattern ' exit=','not_run','tested_state','_sha256 ','outside scope','mismatch','session-gate:'; exit $code", "cwd": "P:/av-kit", "scope": "H1-2, the registered D6 gate on the whole tree after rows 0 to 8 and the D-742 and D-743 additions (third run): identity, every static check, the targeted ledger, limits and dispatch checks, the full Python suite, the render and the closeout selftest, then the identity again", "phase": "full", "exit_code": 0, "result": "pass", "fresh": true, "snapshot": false, "tested_state": "1abf6698c2112e42deb8c298ec04c9f439cc63c3+b55be148dc4a727660214d7c3caa47f9501e2c31d835f31da4d352f900a8466a", "output": "py-lint All checks passed!; tools-lint All checks passed!; task-contract OK: 25 row(s), 23 fully checked, 2 exempt (view_file): H1-5, H2-1; scope-paths changed paths: 33 outside scope: [] head moved (S4): False; prose-check 0 problem(s); red-check selftest: 36 fixture(s), 0 wrong; ledger-selftest RESULT: 126 arm(s), 0 failure(s); arms-check 0 problem(s); review-limits-tests 55 passed; dispatch-tests Total 31 PASS 29 FAIL 2 (exit 1, saved for dispatch-check); dispatch-check: 0 problem(s); py-tests 2608 passed in 177.49s; state-render drift check passed (143 MEUs); closeout-selftest RESULT: 219 arm(s), 0 failure(s); tested_state before and after identical. Baseline failures excused: none in py-tests; the dispatch pair by dispatch-check (D-739). session-gate: all steps exit 0"}
```

```json
{"schema_version": "evidence.v1", "check_id": "rl-h1-3-render", "command": "rtk proxy uv run python tools/meu_status.py render --check *> C:/Temp/av-kit/rl/rl-render-check.txt", "cwd": "P:/av-kit", "scope": "H1-3: rendered state regions after the current focus was updated. No MEU status changes in this session", "phase": "static", "exit_code": 0, "result": "pass", "tested_state": "1abf6698c2112e42deb8c298ec04c9f439cc63c3+b55be148dc4a727660214d7c3caa47f9501e2c31d835f31da4d352f900a8466a", "output": "Drift check passed - SSOT loaded (143 MEUs, 12 phases), rendered regions match on-disk content"}
```

```json
{"schema_version": "evidence.v1", "check_id": "rl-h1-4-openapi", "command": "rtk proxy uv run python -c '<task.md row H1-4: packages/api diff against baseline.sha plus untracked files>' *> C:/Temp/av-kit/rl/openapi-check.txt", "cwd": "P:/av-kit", "scope": "H1-4: the basis for skipping the OpenAPI check", "phase": "static", "exit_code": 0, "result": "pass", "tested_state": "1abf6698c2112e42deb8c298ec04c9f439cc63c3+b55be148dc4a727660214d7c3caa47f9501e2c31d835f31da4d352f900a8466a", "output": "packages/api changes: []"}
```

### Quality Gate Results

`rl-gate-h1-2` is the fresh full record, and its last line is:

> session-gate: all steps exit 0

- **Static:** `py-lint`, `tools-lint`, `task-contract` (25 rows, 23 fully checked, H1-5 and H2-1 exempt as `view_file`), `scope-paths` (33 changed paths, none outside scope, HEAD still `1abf669`), `prose-check` (0 problems) and `red-check-selftest` (36 fixtures, 0 wrong) all exit 0.
- **Targeted:** `ledger-selftest` (126 arms, 0 failures), `arms-check` (0 problems), `review-limits-tests` (55 passed) and `dispatch-check` (0 problems) exit 0. `dispatch-tests` exits 1 on exactly the D-739 pair, which `dispatch-check` accepts.
- **Suites:** `py-tests`: 2608 passed in 177.49s. That is the baseline's 2559 plus the 49 `test_review_limits.py` cases that failed at baseline; the other 6 of its 55 cases passed at baseline. No baseline failure needed excusing.
- **State:** `state-render` (143 MEUs) and `closeout-selftest` (219 arms, 0 failures) exit 0.
- **Skipped, each printed with its reason:**
  - `py-types`: nothing under `packages/` changes.
  - `ui-types`, `ui-lint`, `ui-tests`, `ui-build` and `ui-electron`: nothing under `ui/` changes.
  - `mcp-types`, `mcp-build`, `mcp-tests` and `mcp-audit`: no MCP change.
  - `openapi`: no `packages/api` change (H1-4).
  - `build-record`: no build.
- **Identity:** `tested_state` is `1abf6698c2112e42deb8c298ec04c9f439cc63c3+b55be148dc4a727660214d7c3caa47f9501e2c31d835f31da4d352f900a8466a`, the same before and after.
  - The gate set `TMP` and `TEMP` to `C:/Temp/av-kit/rl/tmp` (RC1 ECN-2) and cleared `ELECTRON_RUN_AS_NODE`.
  - H1-3 and H1-4 were rerun after the gate. A recompute with `ELECTRON_RUN_AS_NODE` cleared, as H1-6b runs it, gives the same state.
  - A recompute with the variable still set gives a different hash (`…a5cf93e0`), because its value is one of the bound inputs.
- **Earlier runs:**
  - Run 1 stopped at `tools-lint`.
  - Run 2 stopped at `py-tests`.
  - Its rerun after D-742 still failed four `test_framework_adoption.py` tests, until D-743.
  - Each fix is in the execution notes above, and each run restarted from the beginning.

---

## Changed Files

| File | Action | Summary |
|------|--------|---------|
| `tools/review_ledger.py` | modified | The port: `LIMITS_FILE`, `OFF`, `RUN_PARAMETERS`; `read_repo_limits` (`:305`), `_looser` (`:338`), `load_plan_limits` (`:359`), `resolve_limits` with the D-733 refusal (`:465-520`); `load_ledger` checks `token_budget` and `limits_source`; `tokens_spent` (`:761`), `stops`, `stop_readout`, `continue` and `state` handle `"off"`; `_count_arg` and `_budget_arg` (`:2948-2955`); 21 selftest arms. +549/−24 lines; CRLF kept |
| `.agent/review-limits.json` | new | `token_budgets: "off"`; rounds 3/6/2/3/3; the tokens map. LF |
| `tests/tooling/test_review_limits.py` | new | AC-1 to AC-11: 26 test functions, 55 cases. LF; `ruff format` applied (execution note H1-2) |
| `docs/execution/plans/PLAN-TEMPLATE.md`, `TASK-TEMPLATE.md` | modified | v2.3, the commented `review_limits` block, and the task template's cap note. CRLF kept |
| `.agent/templates/PLAN-TEMPLATE.md`, `TASK-TEMPLATE.md` | modified | Byte copies of the two above (D-742) |
| `docs/execution/plans/2026-09-26-framework-update-adoption/rule-preservation.md` | modified | `counts."AGENTS.md".postimage_sha256` set to `11309a09…` (D-743) |
| `.agent/workflows/create-plan.md`, `delegated-plan-creation.md`, `execution-session.md`, `validation-review.md` | modified | P1 to P11, the `begin` examples, and the §4 Review limits paragraph. CRLF kept |
| `.agent/docs/development-lifecycle.md`, `issue-lifecycle-guide.md`, `model-routing.md`, `.agent/skills/cli-dispatch/SKILL.md` | modified | P12 to P19 and P22, and the skill's `begin` example. CRLF kept |
| `AGENTS.md`, `PROJECT-PROFILE.md` | modified | P20, P21: one line each. CRLF kept |
| `.agent/context/current-focus.md` | modified | This session's entry on top, and the line that Session 71 is committed (`1abf669`). CRLF kept |
| Plan folder: `baseline.ps1`, `baseline.sha`, `baseline-dirty.txt`, `identity.py`, `red-check.py`, `selftest-arms-check.py`, `selftest-arms-before.txt`, `prose-check.py`, `dispatch-check.py`, `ledger-survey.py`, `session-gate.ps1`, `task.md`, and the Files Modified rows added in `implementation-plan.md` | new or modified | The plan's scripts and records |

```diff
+{
+  "schema": "review-limits/1",
+  "token_budgets": "off",
+  "rounds": {"plan": 3, "execution": 6, "discovery": 2, "handoff": 3, "multi-handoff": 3},
+  "tokens": {"plan": 10500000, "execution": 21000000, "discovery": 7000000, "handoff": 10500000, "multi-handoff": 10500000}
+}
```

```diff
-def tokens_spent(ledger: dict) -> tuple[int, int, int]:
+def tokens_spent(ledger: dict) -> tuple[int, int, int | str]:
 ...
-    base = ledger.get("token_budget") or TOKEN_BUDGETS[ledger["review_mode"]]
+    # An absent key is a ledger older than the token budget; load_ledger refuses 0 or null.
+    base = ledger.get("token_budget", TOKEN_BUDGETS[ledger["review_mode"]])
+    if base == "off":
+        return spent, measured[-1] if measured else 0, "off"
     budget = base + sum(g.get("tokens") or 0 for g in ledger.get("grants", []))
```

```diff
+        if block["basis"] == "loosened":
+            if not RUN_PARAMETERS.is_file():
+                raise Refuse(
+                    "review_limits basis 'loosened' needs tools/run_parameters.py, which "
+                    "this repo does not have; a plan may only keep or tighten "
+                    ".agent/review-limits.json, and more rounds come from review_ledger.py "
+                    "continue"
+                )
```

```diff
+def _count_arg(text: str) -> int:
+    if not re.fullmatch(r"[0-9]+", text) or int(text) < 1:
+        raise argparse.ArgumentTypeError(f"must be an integer >= 1 (got {text!r})")
+    return int(text)
+
+
+def _budget_arg(text: str) -> int | str:
+    return "off" if text == "off" else _count_arg(text)
```

```diff
--- AGENTS.md
-- Initial ledger caps: plan 3, execution 6; preserve kind/target/intent/...
+- Initial ledger caps come from .agent/review-limits.json (plan 3, execution 6; token budgets off); preserve kind/target/intent/...
--- PROJECT-PROFILE.md
-| Round caps (B5) | plan: 3 · execution: 6 |
+| Round caps (B5) | plan: 3 · execution: 6 · token budgets: off (.agent/review-limits.json) |
--- docs/execution/plans/2026-09-26-framework-update-adoption/rule-preservation.md
-      "postimage_sha256": "41b91b52b50f89936b54546aee44c21307ad942af5690b66bca2a598390bd787"
+      "postimage_sha256": "11309a09724cf0ab36b47c1a329e122d6721d2bceae6179f502be77f094ef7ad"
```

```diff
--- docs/execution/plans/PLAN-TEMPLATE.md (TASK-TEMPLATE.md and both .agent/templates/ twins alike)
-template_version: "2.2"
+template_version: "2.3"
+# review_limits:            # optional (v2.3): equal in plan and task; absent = .agent/review-limits.json
+#   schema: review-limits/1
+#   plan_rounds: 3          # integer >= 1, at most rounds.plan
+#   execution_rounds: 6     # integer >= 1, at most rounds.execution
+#   plan_tokens: off        # integer >= 1 or off; a number tightens off
+#   execution_tokens: off
+#   basis: tightened        # repo (every value equal) | tightened (none looser)
 ---
```

---

## Codex Validation Report

_Left blank for reviewer agent. Reviewer fills this section during `/validation-review`._

### Recheck Protocol

1. Read Scope + AC table
2. Verify each AC against Evidence section (file:line, not memory)
3. Independently probe the claimed behavior and compare decisive output
4. Verify the full gate is fresh and matches current D6 inputs; rerun if changed or unproven
5. Record findings below

### Findings

| # | Severity | Finding | File:Line | Recommendation | Status |
|---|----------|---------|-----------|----------------|--------|

### Verdict

Round 1 (loop `rl-execution-2026-11-14-review-limits-no-token-budget`, opened with `budget=6 tokens=off`): `approved`, intent achieved, 0 findings. The ledger recorded the round's usage (10,962,278 tokens) with no token stop, and `state` shows it. That is the goal at work on its own review. The reviewer confirmed the tested state after leaving out `.claude/settings.local.json` (Session 51 RULE-4). It also disclosed one stray receipt written to `C:/Temp/av-kit/review-bootstrap.txt`, outside its designated folder. The canonical review is the reviewer's round-1 file, copied byte for byte. The review-state and approved-state checks passed on that canonical copy (`review-state-check.txt`, `exec-review.txt`: approved at round 1 of 6, 0 open blocking findings).

---

## Deferred Items

| Item | Kind | Deferred-to | Basis |
|------|------|-------------|-------|
| `Test-CliDispatch.ps1` placeholder-dir fixture pair ("placeholder receipts dir refused", "refusal created no placeholder dir") | out-of-scope | — | D-739 (Mat): the plan stays as approved; `dispatch-check.py` allows only this pair; closeout registers the defect as a known issue for its own session |
| Commit and push | out-of-scope | — | The commit waits for Mat's direction (H2-5) |

---

## Decision Log

```yaml
decision_log:
  - id: D-742
    stage: execution
    question: "The gate's py-tests found the .agent/templates/ twins of PLAN-TEMPLATE.md and TASK-TEMPLATE.md out of step with row 7's v2.3 templates (verify_adoption.py:153-157). Re-sync them, or leave the plan's Files Modified as written?"
    resolution: autonomous
    class: two-way
    chosen: "Copy both templates into .agent/templates/ byte for byte and add the twins to Files Modified and the gate's scope-paths list"
    source_tag: Local Canon
    precedents: ["docs/execution/plans/2026-09-29-human-decision-protocol-adoption/implementation-plan.md:38 — twins re-synced (D-6); :54 AC-8 twin templates byte-identical to .agent/templates/*", "docs/execution/plans/2026-09-26-framework-update-adoption/implementation-plan.md:76 — keep .agent/templates/ copies synchronized for compatibility"]
    research: { engine: none, sources: [] }
    reasoning: "The twins exist to equal the runtime templates, and an existing test binds them. Leaving them would fail four governance tests or turn AC-15's templates back to v2.2. The copy is reversible and adds no behaviour."
  - id: D-743
    stage: execution
    question: "After D-742 the same four tests failed on the 2026-09-26 rule map's AGENTS.md pin (verify_adoption.py:213-221), which row 6's P20 edit changed. Update the pin, own commit, revert P20, or stop?"
    resolution: human
    class: governance-value
    chosen: "Update the pin: counts.\"AGENTS.md\".postimage_sha256 set to the new hash, in Files Modified and in this session's commit"
    source_tag: Human-approved
    precedents: ["docs/execution/plans/2026-09-30-tts-repair/human-gate-decision.md A-2 — the same pin updated on Mat's words", ".agent/context/handoffs/2026-10-26-tts-sideload-load-MEU-98-handoff.md D-132 — the same pin updated on Mat's words, own commit c34866b", "docs/execution/plans/2026-10-29-capture-editor-repair/human-gate-decision.md D-175 — a census pin updated as a follow-on of the change that caused it"]
    research: { engine: none, sources: [] }
    reasoning: "A probe with only the pin changed passed all 91 test_framework_adoption tests, and the file was restored before asking. Reverting P20 would fail AC-14. Stopping would leave the gate red. This session's own edit caused the drift, so the pin goes in its commit."
    human_message_reference: "USER_EXPLICIT 2026-11-14 'Update the pin (Recommended)'"
```

---

## History

| Event | Date | Agent | Detail |
|-------|------|-------|--------|
| Created | 2026-11-14 | claude-code-local (Claude Opus 5.5) | Initial handoff after H1-2 |
| Reviewed | 2026-11-14 | codex-independent-reviewer | Execution review round 1: approved, 0 findings |
