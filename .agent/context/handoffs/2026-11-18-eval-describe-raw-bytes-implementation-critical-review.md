---
date: "2026-11-18"
review_mode: "execution"
target_plan: "docs/execution/plans/2026-11-18-eval-describe-raw-bytes/implementation-plan.md"
verdict: "approved"
findings_count: 1
template_version: "2.2"
requested_verbosity: "standard"
agent: "codex-independent-reviewer"
loop_id: "edr-execution-2026-11-18-eval-describe-raw-bytes"
round: 2
tested_state: "3e61b5ba074c9434ca7ea1bea9d809da80305560+6b40c5149bf6e2f9f85afdcd4f1f1ba8e52150e6f131b66e1299985af6403224"
---

# Critical Review: 2026-11-18-eval-describe-raw-bytes

> **Review Mode:** execution
> **Verdict:** approved

## Scope

Independent Codex review of the Anthropic-authored Session 95 implementation, no MEU under D-1196. Round 2 rechecks F1 and the correction against AC-1 through AC-13. The reviewed scope remains the delta from `baseline.sha` in the plan's Files Modified paths: the script and tests, run-book delta, registers, grouping row 95, focus entry, plan-local scripts/data and handoff. Previously accepted unchanged behavior is carried forward and checked against current source, hashes and regenerated receipts. D-1201 A through D-1206 and the disclosed departures are accepted. D-1200, H2 and committing remain outside this read-only review. No repository file was edited; reviewer artifacts are under `C:/Temp/av-kit`.

**Intent anchor:** Session 64's eval run book captures `eval-harness.ts describe` with a new script, `eval-describe.py`, that runs the harness in a subprocess and writes the MCP server's stdout bytes unchanged (a fake child proves the bytes pass through, AC-6; on the real harness the capture equals an independent `npx` read on another root and keeps its tail after CUT, AC-9); it refuses output that is not UTF-8, holds a BOM, a CR byte or cp437 mojibake, or lacks exactly one CUT line, with a non-zero exit and a named reason, using the one pattern and CUT line Session 92 wrote (`eval-rerun.py` `MOJIBAKE` and `CUT`, D-1186), not a second one, and exits 2 with a named message when that file cannot load; `eval-run.md` step 3 names the new command and a dated note says what changed and why; Session 64's task rows, plan and receipts and Session 92's files stay byte for byte; and `EVAL-HARNESS-DESCRIBE-CP437-MOJIBAKE` is resolved through the triage tool with receipts. No product code, no model call and no eval run. Tests and scripts prove each part; there is no manual check.

**Intent achieved:** yes. F1 is fixed: write and close failures remove the newly created failed file, while exclusive-create failures preserve another writer's file. The normal capture, refusals, guard reuse, live equality, run-book change, records and triage resolution remain supported. No new material finding was verified.

**Tested state:** `3e61b5ba074c9434ca7ea1bea9d809da80305560+6b40c5149bf6e2f9f85afdcd4f1f1ba8e52150e6f131b66e1299985af6403224`, independently obtained with `identity.py --state-only`, ELECTRON_RUN_AS_NODE unset, before and after the review checks. It exactly equals gate run 3's before/after values. There is no tested-state discrepancy to attribute to the sandbox's global-ignore access; `.claude/settings.local.json` was not opened. The repository verdict schema forbids additional top-level properties and has no `tested_state` property, so JSON carries this requested identity in its summary and identity checklist evidence; report frontmatter carries it directly.

**Round-1 history:** the prior report returned `changes_required`, intent partial, at state `3e61b5ba074c9434ca7ea1bea9d809da80305560+6d01feb34875b1e3fc9d707e4ce43504ea2e6ea152ca1eb26b49abdaaa34d455`. Its F1 reproduction and other decisive observations are retained below as historical evidence. `findings_count: 1` counts the carried finding F1; open/blocking findings now number zero.

## Findings

| # | Severity | Blocking | Kind | Finding | File:Line | Recommendation | Status |
|---|---|---|---|---|---|---|---|
| F1 | High | no | behavior | AC-6 / RAW_CAPTURE, fixed in round 2. Round 1 injected ENOSPC after CUT: capture exited 2 but left 23,154 of the child's 36,533 bytes, and check accepted the truncated OUT. The correction routes all three writes through write_new; write/close errors now remove their failed file. Independent probes confirm all six write/close cases and preserve competing or preexisting files. | docs/execution/plans/2026-11-11-capture-export-copy/eval-describe.py:143; docs/execution/plans/2026-11-18-eval-describe-raw-bytes/test_eval_describe.py:360 | Implemented: failure cleanup after successful exclusive creation, shared across OUT and both side files, with four Red/Green regression cases. Keep these regressions. | fixed |

## Q1 — Goal

Accepted every goal clause on the current evidence. F1 no longer prevents the all-path RAW_CAPTURE claim within the approved boundary.

| Goal clause | ACs | Observation |
|---|---|---|
| Subprocess stdout bytes unchanged | AC-6 | Fake-child byte equality remains covered. Four correction regressions pass independently; six write/close probes leave no failed file. Popen uses binary pipes without a shell. |
| Clean UTF-8, BOM/CR/mojibake/CUT refusals | AC-1–4, AC-7 | Existing assertions remain byte-identical to the original 25-test version after removing only CVR imports and additions. All non-timeout cases pass locally. |
| One guard and named load failure | AC-5, AC-7 | Session 92's objects are still read through GUARD, with stub substitution, named ASCII load failure and no-launch assertions unchanged. |
| Real capture equals independent read, tail retained | AC-9 | Row-3 and regenerated gate capture/direct pairs are byte-identical: 36,533 bytes, SHA-256 6613cd4173b49d157a9232fa34ab3b057467f1a62b631441a712d30017176ccb. Stored bytes were checked without launching the harness. |
| Step 3 and dated note only | AC-10 | Exact row-0 transformation remains 6,980 bytes, LF; three prompts still build. |
| Protected records unchanged | AC-11 | Nine hashes compared, zero changed; both legacy selftests pass again. |
| Issue resolved through triage, row 95 set | AC-12 | Hash-bound resolver receipt and current parsed register agree; render --check passes. Only grouping line 118 changed. |
| Scoped gate, no product/model/eval changes | AC-13 | Run 3 has 20 executed steps, all exit 0, and matching input identity. All 770 skip-basis files remain unchanged. |

No new goal exception is accepted. The known sandbox-only timeout timing limitation is distinguished from the executor's passing full gate under Q2 and the observed-check table.

## Q2 — Capture (RAW_CAPTURE, NO_OVERWRITE)

Accepted normal binary capture and pre-launch existence checks for OUT and both side files (`eval-describe.py:157`, `:164`, `:172`). All writes now use `write_new` (`:184`, `:191`, `:195`), which opens with `xb` before entering its cleanup handler (`:145`). Failure to create therefore cannot trigger deletion of somebody else's file. Write or close failure after creation enters cleanup, unlinks the failed file and re-raises; `main` prints the unchanged ASCII OSError message and exits 2.

The new regression (`test_eval_describe.py:360`) uses real exclusive-create handles and fake-child stdout, injecting a write after CUT or a close failure. Its four cases cover OUT write/close and each side-file write. The saved Red has four assertion failures for surviving files, not setup failures; Green has 29 passes. The four cases independently pass here. A separate probe extends write and close failure to all three files: six of six remove the failed target and leave no OUT. Three competing-create cases retain the exact `other writer` bytes; three preexisting-output cases retain `held` and never reach the child command. NO_OVERWRITE remains intact. No filesystem-replacement attack outside the approved boundary is introduced as a new finding.

Failing and mojibake children still leave no OUT, and an outside-BASE root is rejected before launch. `command()` still invokes node on tsx directly and reports "build first" for missing dist (`:117`). Timeout handling is unchanged and writes no OUT.

The full reviewer pytest run reports `1 failed, 28 passed in 34.11s`: only the existing timeout test exceeds its 30-second bound (32.08 s). Round 1 had the same failure. A fresh diagnostic on this probe's own fake-child PID confirms `taskkill exit 1`, `ERROR: Access denied`. Shortening only the diagnostic probe's drain interval to 0.5 s exercises the unchanged kill fallback: capture exit 1 in 2.73 s, OUT absent. This is a reproduced sandbox timing limitation, not an implementation correction or an independent full-suite pass. The executor's matching-state full gate reports all 29 tests passed in 3.01 s. Nothing from this limitation is hidden or promoted to a passing local full run.

## Q3 — Guard (ONE_GUARD, NAMED_REFUSAL)

Accepted the approved guard design. `GUARD_PATH` identifies Session 92's unchanged file; `refusals()` reads `GUARD.MOJIBAKE` and `GUARD.CUT` on every call (`:98`, `:108`). There is no second cp437 pattern compiled anywhere in the scoped files: the test's `re.compile("ZZ")` is the deliberate stub oracle. The standard refusal branches use the closed reason names, exit 1 and `refused:`. Guard-load handling uses exit 2, the named ASCII message and no child, as the negative tests demonstrate. The approved cp437-only reach is retained. F1 concerns an I/O error after validation, not a new refusal reason.

## Q4 — Red and live evidence

Accepted AC-8's measured Red. `edr-old.ps1` records shell identity before running both redirect forms in the same `pwsh -NoProfile -File` process. The environment receipt records PowerShell 7.6.10, console code page 437 and output encoding UTF-8; both children exit 0. `edr-old-check.txt` reports 13 mojibake matches and one CUT for each receipt after RTK lines are dropped. Subsequent `check` refusals cover both and Session 64's original receipt.

The pytest Red has 25 first-assertion failures for the missing script, `25 failed in 0.35s`, preserved child exit 1, and no setup failure. The original row-1 hash is retained in `cvr1-edr-test-sha-row1.txt`. Removing only the CVR imports and new block from the current test reconstructs exactly that hash (`96a8d6b3922b325c7a00f06664182d44865209029fe48d7034898c76c58d6654`), so all original test expectations remain unchanged. The new current hash `b581bcaac200f91a6565040b2cb054c7f72300c254c62fc7a9770782636682c8` equals the CVR Red hash and the gate comparison; that replacement and preserved original are disclosed. Round 1's independent Red checker reported seven required AC families and zero problems; that unchanged-history observation is retained.

Accepted AC-9's narrow proof. Both stored capture/direct pairs match byte for byte. Independent calls to `live_findings` pass all 11 content checks for each pair. A capture truncated immediately after CUT fails both `equal-direct` and `tail-kept`; the gate's two side-file checks make its documented total 13. This validates the actual successful captures while F1 is now separately covered by write/close regressions and independent probes.


The CVR Red is additionally accepted: `4 failed, 25 passed in 4.00s`, preserved child exit 1, each failed assertion naming a surviving file. A fresh `red-check.py --require test_ac_6_capture_write_failure_leaves_no_file` reports one receipt, one required test and zero problems. `cvr1-green.txt` reports `29 passed in 4.65s`; format and lint are clean. Gate run 3 supersedes run 2 after the correction.

## Q5 — Records and doc (STEP3_NAMES_SCRIPT, RECORDS_KEPT)

Accepted AC-10 and AC-11. The diff contains only the dated note after the original line 6 and the original step-3 replacement (now line 26). Independent exact-byte comparison and `edr-check.py doc` both pass, including three prompts from Session 92's `build()`. Session 64's plan/task/harness/seed/checker/describe receipt, Session 92's guard/expected text and backend.ts all match their nine row-0 hashes. `edr-check.py records` also reruns the two selftests successfully. No protected-record change was observed or inferred from task marks.

## Q6 — Gate and registers

Accepted gate run 3, stamp `20261118-231019`, as the fresh passing run for the corrected state. All 20 steps have corresponding receipts and exit 0; meaningful counts include 29 tests, 39 Red-check fixtures, 24 EOL cases, three record checks, four doc checks, three old-receipt refusals, 13 live checks and seven formatted Python files. Independently observed input identity equals both gate identities. The first run's disclosed host-load refusal and later `not_run` steps remain recorded; run 2's passing evidence remains in `gate-run2/`, superseded by the correction. They are not confused with run 3.

`issue-resolve.py` imports tools/issue_triage's model, validates a staged copy and writes only permitted fields after its expected-hash check. The recorded pre-resolution SHA-256 `b787fe3bb1d5aa3707015f72375766c0b8ab5fba3d6186bfca1867af4faac148` equals the row-0 register hash and copy. The resolver receipt records four parsed field changes, 105/105 decision logs read and zero problems. Independent comparison again finds no other issue changed and exactly status, verification and resolution_path changed on the target. Verification cites AC-8/AC-9 receipts and Session 95; the resolution path describes the delivered fix. A fresh `render --check` passes. Grouping line 118 alone changes to `executed (Session 95)`.

The CVR's new Red hash, refreshed evidence record, moved citations and unchanged-cell reruns are disclosed and accepted. H1-6a/H1-6b receipts again show all 13 ACs and valid durable evidence. The coordinator's test-count phrase in current-focus.md is outside tested_state and keeps 233 CRLF endings. No new defect against AC-1 to AC-13 was established.

## Q7 — Safety and fidelity

Accepted scope and preservation. HEAD remains `3e61b5ba074c9434ca7ea1bea9d809da80305560`, branch main, index empty. All 770 tracked/untracked non-ignored files in packages/, tools/, ui/, tests/ and the specified MCP directories retain baseline hashes with no additions/removals. Changed paths stay within the declared plan, run book, register, grouping, focus and closeout scope. All inspected changed/new files have LF except current-focus.md, whose 233 line endings are CRLF. Its historical home-path placeholder matches are identical to row 0; no new literal home path or personal email was found in session additions/new files.

The source and receipt evidence supports isolated describe operations without a model call or eval execution. No evidence of a session commit, stash, revert, product change or access to real app data was found. This is bounded evidence from retained state, source and receipts, not a claim to have monitored every host process. No reviewer command contacted the network, launched the real harness/backend/app, opened scratch-root contents or read excluded secrets. Only fake children were launched; the timeout probe targeted its own recorded child PID. All reviewer writes stay under C:/Temp/av-kit.

The handoff's updated observations match the regenerated receipts and current state. F1 is corrected and the broader RAW_CAPTURE claim is now supported by the fault-injection tests. The handoff's note leaving the focus count to the coordinator is understood alongside the coordinator's disclosed correction to 29 tests. No formatting, naming or H2-paperwork finding is raised.

## Checklist Results

### Commands executed and observed results (round 2)

All reviewer Python commands used `PYTHONDONTWRITEBYTECODE=1`, `-B`, TMP/TEMP under `C:/Temp/av-kit/eval-describe-raw-bytes/exec-review/tmp`, ELECTRON_RUN_AS_NODE unset, offline UV and its cache under the review folder. Streams were redirected and exits preserved. No full gate or live capture was rerun. The actual full local pytest failure is recorded below, separately from the successful F1 checks and executor gate.

| Check | Result | Command / procedure | Exit | Decisive observation |
|---|---|---|---|---|
| Identity / evidence freshness | pass | `rtk proxy uv run --no-sync python -B docs/execution/plans/2026-11-18-eval-describe-raw-bytes/identity.py --state-only` (before and after) | 0 | Exact gate run-3 identity match. |
| RAW_CAPTURE F1 regressions | pass | `rtk proxy uv run --no-sync python -B -m pytest docs/execution/plans/2026-11-18-eval-describe-raw-bytes/test_eval_describe.py -p no:cacheprovider --basetemp C:/Temp/av-kit/eval-describe-raw-bytes/exec-review/pytest-round2-f1 -k capture_write_failure_leaves_no_file -q` | 0 | 4 passed, 25 deselected in 0.90s; selection is an explicitly targeted check. |
| RAW_CAPTURE / NO_OVERWRITE adversarial probe | pass | `rtk proxy uv run --no-sync python -B C:/Temp/av-kit/eval-describe-raw-bytes/exec-review/round2-probe.py` | 0 | Six write/close cleanups, three competing-create preservations, three preexisting no-child cases. |
| Full local test attempt | fail | `rtk proxy uv run --no-sync python -B -m pytest docs/execution/plans/2026-11-18-eval-describe-raw-bytes/test_eval_describe.py -p no:cacheprovider --basetemp C:/Temp/av-kit/eval-describe-raw-bytes/exec-review/pytest-round2 -q` | 1 | 28 passed, one existing timeout timing failure at 32.08 s; same sandbox restriction as round 1. |
| Timeout limitation diagnosis | pass | `rtk proxy uv run --no-sync python -B C:/Temp/av-kit/eval-describe-raw-bytes/exec-review/round2-timeout.py` | 0 | taskkill exit 1, Access denied; diagnostic-only shorter drain yields refusal in 2.73 s, no OUT. |
| IR-1 runtime receipts; IR-7 ACs; DR freshness | pass | Read all 20 run-3 step receipts and handoff; audit current state and saved captures | null | Executor full run: 29 passed; 13 live checks pass; current identity agrees. Observer: codex-independent-reviewer. |
| IR-4 fix generalization; IR-5/6 test contracts | pass | Full script/test audit, targeted regressions and independent probe | null | Shared helper covers all three destinations; original test bytes reconstructed exactly after removing CVR additions. Observer: codex-independent-reviewer. |
| DR run book / records / dependency checks | pass | `rtk proxy uv run --no-sync python -B C:/Temp/av-kit/eval-describe-raw-bytes/exec-review/round2-checks.py` | 0 | 39 Red fixtures, 24 EOL cases, guard checks, 3 records, 4 doc checks; CVR Red valid, original expectations unchanged, 20 real gate receipts. |
| Register rendering | pass | `rtk proxy uv run --no-sync python -B tools/issue_triage.py render --check` | 0 | known-issues.md is up-to-date. |
| Scope and byte preservation | pass | `rtk proxy uv run --no-sync python -B C:/Temp/av-kit/eval-describe-raw-bytes/exec-review/round2-audit.py` | 0 | 9 records and 770 skip-basis files unchanged; grouping line 118 only; exact run book; both stored pairs equal. |
| IR-2 product stubs; IR-3 HTTP mapping | n/a | No product/API change | null | No corresponding surface in scope. |

The local suite's failure is not labeled passing. It is a known environment-specific timing result, reproduced independently; approval rests on the successful changed-behavior checks plus the executor's matching-state full gate. JSON uses only pass/n/a checklist results as its approval rule requires, and explicitly declares this unavailable local timing certification.

### IR-5 assertion-strength audit

Every test in the current file was read. The original assertions remain strong and unchanged; the new four-case regression closes F1's gap. No weak test was identified. The two additional side-file close cases are independently probed through the same helper.

| Tests (all cases included) | Count | Rating | Reason |
|---|---|---|---|
| `test_ac_1_clean_passes` | 1 | Strong | Exact empty refusal list, check exit and prefix. |
| `test_ac_2_cp437_fixture_refused`, `test_ac_2_cp437_crlf_refused` | 2 | Strong | Constructed real cp437 conversion; exact reason lists and exits. |
| `test_ac_3_mixed_arrow_refused`, `test_ac_3_mixed_dash_refused` | 2 | Strong | Both mixed directions, refusal reason and exit. |
| `test_ac_4_refuses` | 7 | Strong | Seven distinct malformed inputs each require its reason and exit. |
| `test_ac_5_one_guard`, `test_ac_5_stub_guard_used` | 2 | Strong | Source/path checks plus a behavioral oracle that defeats copying. |
| `test_ac_6_capture_writes_child_bytes`, `test_ac_6_capture_never_overwrites` | 2 | Strong | Exact bytes/hash, side-file behavior; all three existing paths preserve contents and prevent child launch. |
| `test_ac_6_capture_refuses_child_exit`, `test_ac_6_capture_refuses_mojibake_child`, `test_ac_6_capture_refuses_timeout`, `test_ac_6_capture_refuses_root_outside_base` | 4 | Strong | Concrete failures, required exits/reasons, absent OUT and marker/timing assertions. Timeout timing is environment-limited here. |
| `test_ac_7_cli_usage`, `test_ac_7_cli_build_first`, `test_ac_7_guard_missing` | 5 | Strong | Three usage cases, missing build, actual module-load failure and no-child guard failure; ASCII/no-traceback checks. |
| `test_ac_6_capture_write_failure_leaves_no_file` | 4 | Strong | Real exclusive-create handles, partial write after CUT and close fault, error exit/prefix/ASCII/no-traceback checks, failed target and OUT both absent; Red proves each fails on the prior implementation. |

### Historical round-1 reviewer evidence (retained)

These four original records preserve round 1's actual observations and old state. F1's reproduction is historical, not a current failure; the round-2 checks above and below supersede its result. The prior live/doc/records checks remain corroborated by the regenerated evidence.


```json
{"schema_version":"evidence.v1","check_id":"edr-review-r1-write-exception","command":"rtk proxy uv run --no-sync python -B C:/Temp/av-kit/eval-describe-raw-bytes/exec-review/probe.py","cwd":"P:/av-kit","scope":"RAW_CAPTURE AC-6; fake child only; injected ENOSPC on OUT write","phase":"targeted","exit_code":0,"result":"pass","tested_state":"3e61b5ba074c9434ca7ea1bea9d809da80305560+6d01feb34875b1e3fc9d707e4ce43504ea2e6ea152ca1eb26b49abdaaa34d455","output":"Reproduction succeeded: write-failure capture exit: 2; error: OSError: [Errno 28] review fixture: disk full after CUT; OUT survives: True; OUT bytes: 23154 child bytes: 36533 equal: False; OUT refusals: []; truncated OUT check exit: 0; ok: 23154 bytes sha256 4d63e6ab9e06d3497d73388c65caf97f5e2d815d00000a32ea902a8ed0bdf521; REPRODUCED: write exception leaves a clean, truncated OUT accepted by check."}
```

```json
{"schema_version":"evidence.v1","check_id":"edr-review-r1-source-and-receipt-audit","command":"rtk proxy uv run --no-sync python -B C:/Temp/av-kit/eval-describe-raw-bytes/exec-review/audit.py","cwd":"P:/av-kit","scope":"AC-9 to AC-12; all baseline JSON data, protected files, skip-basis files, diffs and stored captures","phase":"targeted","exit_code":0,"result":"pass","tested_state":"3e61b5ba074c9434ca7ea1bea9d809da80305560+6d01feb34875b1e3fc9d707e4ce43504ea2e6ea152ca1eb26b49abdaaa34d455","output":"records checked 9 changed []; skip-basis files 770 changed []; branch main; staged bytes 0; grouping differing lines [118]; register other issues changed []; target keys ['resolution_path', 'status', 'verification']; status resolved; register before sha matches row0 True; row3 and gate byte equality True True True bytes 36533; row3 pass 11 failures []; gate pass 11 failures []; truncated failures ['equal-direct', 'tail-kept']; runbook expected bytes equal True; test hash equals Red True; audit: passed."}
```

```json
{"schema_version":"evidence.v1","check_id":"edr-review-r1-independent-checks","command":"rtk proxy uv run --no-sync python -B C:/Temp/av-kit/eval-describe-raw-bytes/exec-review/checks.py","cwd":"P:/av-kit","scope":"edr-check selftest, records, doc, line endings, preserved Red","phase":"targeted","exit_code":0,"result":"pass","tested_state":"3e61b5ba074c9434ca7ea1bea9d809da80305560+6d01feb34875b1e3fc9d707e4ce43504ea2e6ea152ca1eb26b49abdaaa34d455","output":"selftest exit 0: selftest: 0 failures; records exit 0: edr-check: 3 pass, 0 fail []; doc exit 0: edr-check: 4 pass, 0 fail []; line-endings exit 0: eol-check: 11 scope path(s), 0 problem(s); red exit 0: red-check: 1 receipt(s), 7 required test(s), 0 problem(s); current-focus home literals same as row0 True; Red assertion reasons 25; summary 25 failed in 0.35s; checks failed []."}
```

```json
{"schema_version":"evidence.v1","check_id":"edr-review-r1-pytest-observation","procedure":"Executed rtk proxy uv run --no-sync python -B -m pytest docs/execution/plans/2026-11-18-eval-describe-raw-bytes/test_eval_describe.py -p no:cacheprovider --basetemp C:/Temp/av-kit/eval-describe-raw-bytes/exec-review/pytest -q; read the completed pytest.txt receipt and diagnosed its timeout failure with timeout-probe.py.","observer":"codex-independent-reviewer","cwd":"P:/av-kit","scope":"All 25 fake-child tests; no real harness","phase":"targeted","exit_code":null,"result":"fail","tested_state":"3e61b5ba074c9434ca7ea1bea9d809da80305560+6d01feb34875b1e3fc9d707e4ce43504ea2e6ea152ca1eb26b49abdaaa34d455","output":"1 failed, 24 passed in 32.91s; only test_ac_6_capture_refuses_timeout fails: elapsed 32.079 seconds versus <30. Diagnostic fake-child probe: taskkill exit 1; stderr ERROR: Access denied; with drain interval shortened only in the diagnostic probe, capture exit 1 in 2.64 seconds and OUT exists False. This explains the sandbox timing limitation; no second finding is assigned."}
```

## Verdict

`approved` — intent achieved. F1 is fixed; there are no open blocking findings and no new findings. The correction preserves RAW_CAPTURE, NO_OVERWRITE, ONE_GUARD, NAMED_REFUSAL, STEP3_NAMES_SCRIPT and RECORDS_KEPT. Gate run 3 is fresh for the independently measured corrected state. The known local sandbox timeout limitation remains explicit and is not misreported as a local full-suite pass.

This approval completes the requested independent review only. H1-7 ledger publication and H2 remain with the coordinator; their pending state is expected and was not a finding. No reviewer fixes, repository writes, ledger mutations, commits or pushes occurred. The coordinator saves this complete report to the canonical rolling path.

## Recheck (round 2)

### Prior Pass Summary

| Finding | Prior Status | Recheck Result |
|---|---|---|
| F1 | open | fixed |

### Confirmed Fixes

F1: `eval-describe.py:143` adds `write_new`, and `:184`, `:191`, `:195` route stderr, refused bytes and OUT through it. Creation with `xb` precedes the cleanup handler. The new regression starts at `test_eval_describe.py:360`. The four saved Red assertions, 29-test executor Green/fresh gate, four independently passing regression cases and twelve independent fault/ownership cases demonstrate the fix without altering the original 25 test expectations.

### New Findings

| # | Severity | Blocking | Kind | Finding | File:Line | Recommendation | Status |
|---|---|---|---|---|---|---|---|

### Durable round-2 reviewer evidence

```json
{"schema_version": "evidence.v1", "cwd": "P:/av-kit", "phase": "targeted", "tested_state": "3e61b5ba074c9434ca7ea1bea9d809da80305560+6b40c5149bf6e2f9f85afdcd4f1f1ba8e52150e6f131b66e1299985af6403224", "check_id": "edr-review-r2-f1-tests", "command": "rtk proxy uv run --no-sync python -B -m pytest docs/execution/plans/2026-11-18-eval-describe-raw-bytes/test_eval_describe.py -p no:cacheprovider --basetemp C:/Temp/av-kit/eval-describe-raw-bytes/exec-review/pytest-round2-f1 -k capture_write_failure_leaves_no_file -q", "exit_code": 0, "result": "pass", "scope": "F1 regression cases only; fake children", "output": "4 passed, 25 deselected in 0.90s."}
```

```json
{"schema_version": "evidence.v1", "cwd": "P:/av-kit", "phase": "targeted", "tested_state": "3e61b5ba074c9434ca7ea1bea9d809da80305560+6b40c5149bf6e2f9f85afdcd4f1f1ba8e52150e6f131b66e1299985af6403224", "check_id": "edr-review-r2-fault-probe", "command": "rtk proxy uv run --no-sync python -B C:/Temp/av-kit/eval-describe-raw-bytes/exec-review/round2-probe.py", "exit_code": 0, "result": "pass", "scope": "AC-6 RAW_CAPTURE and NO_OVERWRITE; own Temp files and fake children", "output": "round2-probe: {'cleanup': 6, 'late_create_preserved': 3, 'preexisting_no_child': 3} all passed. Each write/close failure exits 2 with failed target absent and no OUT. All three competing creates preserve other writer bytes; all three held paths prevent reaching child command."}
```

```json
{"schema_version": "evidence.v1", "cwd": "P:/av-kit", "phase": "targeted", "tested_state": "3e61b5ba074c9434ca7ea1bea9d809da80305560+6b40c5149bf6e2f9f85afdcd4f1f1ba8e52150e6f131b66e1299985af6403224", "check_id": "edr-review-r2-audit", "command": "rtk proxy uv run --no-sync python -B C:/Temp/av-kit/eval-describe-raw-bytes/exec-review/round2-audit.py", "exit_code": 0, "result": "pass", "scope": "AC-9 to AC-12; current files, baselines, saved capture/direct pairs and diffs", "output": "9 records unchanged; 770 skip-basis files unchanged; HEAD baseline, main, index empty; 28 safe changed paths; focus 233 CRLF, remaining scope LF; grouping difference [118]; no other issue changed; target fields resolution_path/status/verification; row0 register SHA matches; row3 and run3 pairs equal, 36533 bytes SHA-256 6613cd4173b49d157a9232fa34ab3b057467f1a62b631441a712d30017176ccb; 11 content checks each pass; truncated fails equal-direct and tail-kept; run book exact; current test hash equals CVR Red."}
```

```json
{"schema_version": "evidence.v1", "cwd": "P:/av-kit", "phase": "targeted", "tested_state": "3e61b5ba074c9434ca7ea1bea9d809da80305560+6b40c5149bf6e2f9f85afdcd4f1f1ba8e52150e6f131b66e1299985af6403224", "check_id": "edr-review-r2-checks", "command": "rtk proxy uv run --no-sync python -B C:/Temp/av-kit/eval-describe-raw-bytes/exec-review/round2-checks.py", "exit_code": 0, "result": "pass", "scope": "Read-only selftests, records/doc/EOL check modes, CVR Red, original test bytes, saved full gate and current identity", "output": "Red selftest 39 fixtures 0 wrong; EOL selftest 24 cases 0 wrong; edr selftest 0 failures; records 3 pass; doc 4 pass; EOL 11 paths 0 problems; CVR Red 1 receipt 1 required test 0 problems. Original test SHA reconstructed as 96a8d6b3922b325c7a00f06664182d44865209029fe48d7034898c76c58d6654. Gate run3 20 steps exit 0, all receipts exist; review identity equals gate before/after."}
```

```json
{"schema_version": "evidence.v1", "cwd": "P:/av-kit", "phase": "targeted", "tested_state": "3e61b5ba074c9434ca7ea1bea9d809da80305560+6b40c5149bf6e2f9f85afdcd4f1f1ba8e52150e6f131b66e1299985af6403224", "check_id": "edr-review-r2-full-local-attempt", "command": "rtk proxy uv run --no-sync python -B -m pytest docs/execution/plans/2026-11-18-eval-describe-raw-bytes/test_eval_describe.py -p no:cacheprovider --basetemp C:/Temp/av-kit/eval-describe-raw-bytes/exec-review/pytest-round2 -q", "exit_code": 1, "result": "fail", "scope": "All 29 fake-child tests in reviewer sandbox", "output": "1 failed, 28 passed in 34.11s. Only test_ac_6_capture_refuses_timeout: elapsed 32.07799999997951 versus <30. No correction regression fails. Known sandbox limitation carried from round 1; not claimed as a local full-suite pass."}
```

```json
{"schema_version": "evidence.v1", "cwd": "P:/av-kit", "phase": "targeted", "tested_state": "3e61b5ba074c9434ca7ea1bea9d809da80305560+6b40c5149bf6e2f9f85afdcd4f1f1ba8e52150e6f131b66e1299985af6403224", "check_id": "edr-review-r2-timeout-limitation", "command": "rtk proxy uv run --no-sync python -B C:/Temp/av-kit/eval-describe-raw-bytes/exec-review/round2-timeout.py", "exit_code": 0, "result": "pass", "scope": "Diagnosis only, own fake-child PID, drain changed only in scratch probe", "output": "taskkill exit 1; diagnostic ERROR: Access denied. With diagnostic-only DRAIN_TIMEOUT_S=0.5: capture exit 1, elapsed 2.73 s, OUT exists False; timeout/harness-exit/empty refusal. Production timeout logic unchanged."}
```

```json
{"schema_version": "evidence.v1", "cwd": "P:/av-kit", "phase": "targeted", "tested_state": "3e61b5ba074c9434ca7ea1bea9d809da80305560+6b40c5149bf6e2f9f85afdcd4f1f1ba8e52150e6f131b66e1299985af6403224", "check_id": "edr-review-r2-identity", "command": "rtk proxy uv run --no-sync python -B docs/execution/plans/2026-11-18-eval-describe-raw-bytes/identity.py --state-only", "exit_code": 0, "result": "pass", "scope": "Independently measured D6 identity, before and after; ELECTRON_RUN_AS_NODE unset", "output": "3e61b5ba074c9434ca7ea1bea9d809da80305560+6b40c5149bf6e2f9f85afdcd4f1f1ba8e52150e6f131b66e1299985af6403224; exact match to gate run 3 before/after; no global-ignore discrepancy in tested_state."}
```

```json
{"schema_version": "evidence.v1", "cwd": "P:/av-kit", "phase": "targeted", "tested_state": "3e61b5ba074c9434ca7ea1bea9d809da80305560+6b40c5149bf6e2f9f85afdcd4f1f1ba8e52150e6f131b66e1299985af6403224", "check_id": "edr-review-r2-render", "command": "rtk proxy uv run --no-sync python -B tools/issue_triage.py render --check", "exit_code": 0, "result": "pass", "scope": "Known issue generated view", "output": "OK: known-issues.md is up-to-date."}
```

### Recheck verdict

`approved` — F1 fixed, zero new findings, goal achieved.
