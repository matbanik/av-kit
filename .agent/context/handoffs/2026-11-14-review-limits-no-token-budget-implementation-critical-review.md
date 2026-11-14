---
date: "2026-11-14"
review_mode: "execution"
target_plan: "docs/execution/plans/2026-11-14-review-limits-no-token-budget/implementation-plan.md"
verdict: "approved"
findings_count: 0
template_version: "2.2"
requested_verbosity: "standard"
agent: "codex-independent-reviewer"
loop_id: "rl-execution-2026-11-14-review-limits-no-token-budget"
round: 1
---

# Critical Review: 2026-11-14-review-limits-no-token-budget

> **Review Mode:** `execution`
> **Verdict:** `approved`

## Scope

**Intent anchor:** Review loops in av-kit stop on their round caps and never on token spend, while every round's token usage is still recorded and shown.

**Intent achieved: yes.** Newly opened default loops have no token stop, retain round-cap enforcement, and persist and display measured usage. Existing numeric-budget loops keep their original effective caps. No material defect was found.

Codex (`codex-independent-reviewer`, class `avkit_independent_reviewer`) reviewed Claude Code/Anthropic's uncommitted work independently. The target is the complete supplied tooling/governance delta on `main`, HEAD `1abf6698c2112e42deb8c298ec04c9f439cc63c3`, including the new tests, plan-local scripts, handoff, plan review, D-742's template twins and D-743's pin. No MEU or product behavior is claimed. Decisions D-730 through D-743, the dispatch baseline exception and H2 ordering were accepted as instructed; their implementation was checked.

The repository and live ledgers were not modified. Independent commands used `PYTHONDONTWRITEBYTECODE=1`, `python -B`, and scratch TMP/TEMP/RECEIPTS_DIR under `C:/Temp/av-kit/rl/exec-review`. UV cache was redirected there with offline mode after the initial invocation refused access to the normal cache. Git's upstream ownership check was resolved with a per-command `safe.directory`, without changing configuration. No network, full suite, session gate, dispatcher, install, commit or push ran during this review.

Reviewer operation disclosure: the initial instruction-read receipt was mistakenly written to `C:/Temp/av-kit/review-bootstrap.txt`. This was disclosed during the review; subsequent artifacts use the designated review folder and this explicitly requested report path. The initial unadjusted identity invocation yielded the documented sandbox ignore-file mismatch; the authoritative recomputation below excludes the named secret path and matches exactly. No secret content was inspected or reproduced in review output.

## Findings

| # | Severity | Blocking | Kind | Finding | File:Line | Recommendation | Status |
|---|----------|----------|------|---------|-----------|----------------|--------|

## Answers to Q1–Q10

### Q1 — Goal

**Accepted.** Independent scratch CLI loops exercised all five modes through `begin`, `evaluate`, actual `record --usage-receipt`, `stops()` and `state`. Each round recorded **1,000,000,000,000 tokens**, with `unmeasured=false`; every usage appeared in state. No `tokens` stop occurred. The round after each cap was refused: plan 3, execution 6, discovery 2, handoff 3, multi-handoff 3. AC-4/AC-7 and the existing usage selftests cover the parts, and the independent probe verified their composition. No goal clause remains unproved.

### Q2 — LEDGER against UPSTREAM

**Accepted.** Read UPSTREAM `6dd76b7` and the complete LEDGER diff. Sixteen relevant reader/helper/token/parser functions are executable-AST identical to UPSTREAM, including `tokens_spent`, `_count_arg` and `_budget_arg`. The allowlist addition, loading refusals, guarded token stop, readout, begin, continue and state hunks are present in their intended functions. The D-733 refusal occurs in `resolve_limits` before `save_ledger`. No absent framework dependency is reached for allowed blocks. Both the AC-6 test and independent probes confirmed an off-loop token grant leaves ledger bytes unchanged, including a mixed `--rounds 1 --tokens 1` request.

### Q3 — LIMITS_FILE and PLAN_BLOCK

**Accepted within the declared strict block grammar.** The 55-case CLI/unit run proves all five modes' file defaults, no-file numeric defaults, eight malformed files, contradicted/malformed blocks, plan/task disagreement, D-733 refusal, tightening flags and invalid arguments. Loosening flags and blocks write no ledger. Plan/execution alone consume PLAN_BLOCK; discovery ignores it, with the same mode guard excluding handoff modes. As specified in Boundary Inventory, equality is required when the sibling task carries a block. Repository byte hash, plan carrier and applied flags are recorded accurately in `limits_source` and printed separately. No additional YAML syntax support was assumed.

### Q4 — Existing loops

**Accepted.** The supplied survey receipt proves 93/93 pre-change ledgers loaded. Independently copied the current 94 files: the same 93 historical ledgers plus this execution loop. Every copy's `state` exited 0. For each historical ledger, HEAD's old implementation and the new implementation computed identical `rounds_allowed` and complete `tokens_spent` tuples. The current census includes 40 ledgers with grants, 39 with token grants and one with mechanism reliefs. Live bytes remained unchanged. `ledger-survey.py` reads LIVE, replaces only its separate SURVEY copies, and invokes state with the copies' RECEIPTS_DIR; it does not operate on live ledgers.

### Q5 — Wrapper

**Accepted.** `cmd_evaluate` retains its exact successful `mode=` line and exit semantics. The begin line retains mode/budget/tokens fields and adds source metadata. The wrapper's mode extraction and exit mapping at `tools/Invoke-CodexDispatch.ps1:436–488` remain compatible. `rl-gate-only.txt` actually reaches `round 1 permitted mode=plan`, `dispatch kind 'plan'` and `-GateOnly: gate result 'permitted'`. This proves AC-13's gate path; it is not represented as a new reviewer dispatch.

### Q6 — Tests and selftest

**Accepted.** Independently ran **55 tests** and **126 selftest arms**, both clean. All 105 baseline arm names remain; all 76 literal prior arm call ASTs are unchanged, and the 21 required new arms are present. The two mocked loosening arms use an inert RUN_PARAMETERS file to reach their intended checks; the distinct missing-file arm actually proves D-733. AC-4 uses usage up to 10^12; AC-6 compares complete bytes after refusal; AC-3/AC-9/AC-10/AC-11 assert no refused ledger exists. CLI fixtures copy the tool, schema and vocabulary into their own root; only AC-1 deliberately reads the real LIMITS_FILE. The actual Red receipt passes the nine required test-id checks with assertion diagnostics, not setup failures. The disclosed AC-7 Red departure does not remove its Green behavior assertions.

`dispatch-check.py --selftest` passes. Independently checked all three actual dispatch receipts against the exact approved pair and rejected a third FAIL even after consistently recounting Total/FAIL. Empty startup, wrong exit and inconsistent-count cases are also refused. The fresh gate proves the final formatted tests and template/pin corrections together.

### Q7 — INVENTORY and templates

**Accepted.** Re-read the prose diff and independently ran all P1–P22, four begin examples, AGENTS size and template checks: zero problems. The live Markdown sweep found no residual fixed-cap/old TOKEN_BUDGETS-source phrases; the historical SVG was excluded from that conclusion. New instructions name defaults and the limits file/block/state; named-human `continue --rounds` remains the cap-growth path. Both the actual flat frontmatter reader and `load_plan_limits` ignore the commented template block. AGENTS has **126 lines / 17,861 bytes**. All 17 modified files retain CRLF; the new LIMITS_FILE and tests are LF. Historical records were not treated as current rules.

### Q8 — D-742 and D-743

**Accepted.** Both `.agent/templates/` twins equal the corresponding `docs/execution/plans/` bytes. Today's AGENTS SHA-256 is `11309a09724cf0ab36b47c1a329e122d6721d2bceae6179f502be77f094ef7ad`, exactly the new pin. Replacing only the old hash in HEAD's rule map produces today's entire rule map. Neither addition exceeds its Decision Log scope.

### Q9 — Freshness and evidence

**Accepted.** With ELECTRON_RUN_AS_NODE unset and a scratch, process-scoped Git ignore containing only `/.claude/settings.local.json`, the permitted identity command produces exactly:

`1abf6698c2112e42deb8c298ec04c9f439cc63c3+b55be148dc4a727660214d7c3caa47f9501e2c31d835f31da4d352f900a8466a`

It matches the handoff's fresh full record and both gate identity receipts. Substantive output/count/exit claims in the evidence.v1 records match the named baseline, Red/Green, selftest, prose/template, survey, gate-only, dispatch, D-743 and final-gate receipts. The full gate contains 16 recorded step exits and ends `session-gate: all steps exit 0`; only the explicitly handled dispatch suite has exit 1. The baseline has exactly 49 FAILED ids, all from this test file: **2559 + 49 = 2608**. The other six new-file cases already passed at baseline. No fresh independent full-suite run is claimed or needed for unchanged, matching evidence.

### Q10 — Safety and scope

**Accepted.** Introduced ledger tests use tmp_path and isolated copies. Selftests redirect their ledger roots into temporary directories and restore their globals; no reviewed probe changes a live ledger. The survey's only deletion is its named scratch-copy directory. Baseline dependency synchronization and dispatch-suite user-temp behavior are explicit existing validation operations; those were inspected, not executed by this reviewer, and are not claimed to be side-effect-free. No added product/API/UI/MCP surface requires the skipped product checks: package types, UI, MCP, OpenAPI and build skips are appropriate. The full Python/tooling and wrapper evidence still covers the changed tooling. Commit/push and H2 remain with the coordinator and Mat.

## Checklist Results

| Check | Result | Procedure / command | Exit | Evidence |
|---|---|---|---|---|
| IR-1 Runtime | pass | Scratch CLI begin/evaluate/record/state/continue for all five modes | 0 | Real JSON writes and receipts; 10^12 per round; round caps preserved |
| IR-2 Stub compliance | n/a | No product stubs introduced | null | Real CLI and filesystem behavior used |
| IR-3 HTTP mapping | n/a | No HTTP route changes | null | Tooling-only delta |
| IR-4 Generalization | pass | Compare all five modes and every existing ledger copy | 0 | Same off behavior and historical effective caps |
| IR-5 Test rigor | pass | Read all tests; run permitted file; audit prior/new selftest arms | 0 | 55 tests, 126 arms; per-test grades below |
| IR-6 Boundaries | pass | CLI malformed-file/block/flag and refusal-before-write assertions | 0 | Eight file cases, malformed blocks, mismatch, loosening, bad args |
| IR-7 Coverage/deferrals | pass | Compare AC-1–AC-15, source request, decisions and handoff evidence | null | All ACs covered; approved exclusions and H2 ordering retained |
| DR-1–DR-8 Claims/freshness | pass | Source/diff/receipt audit and reconciled identity | 0 | Matching full gate; verified twins, pin, endings and prose |
| AV-1–AV-6 | pass | Assertion Red/Green audit, fixture isolation and source-backed criteria | null | No implementation bypass, masked test or required scope cut |

Manual observations were made by `codex-independent-reviewer`. IR-7/AV observations compare current files and decisive outputs rather than treating artifact wording as proof.

### IR-5 per-test grades

Names below are the suffixes after `test_ac_<n>_` in `tests/tooling/test_review_limits.py`. Parameterized cases inherit the indicated grade.

| AC | Test | Grade | Basis |
|---|---|---|---|
| 1 | repo_limits_file_holds_the_approved_values | Strong | Actual file equality, parser acceptance, constants and LF |
| 1 | a_changed_copy_fails_the_equality_check | Adequate | Equality-oracle control only; not relied on as implementation evidence |
| 2 | begin_reads_the_repo_file | Strong | All modes, persisted limits and exact repo hash |
| 2 | no_repo_file_uses_the_constants | Strong | All modes, constants source and numeric budget |
| 3 | malformed_repo_file_fails_closed | Strong | Eight malformed inputs, exit 3 and no write |
| 4 | off_ledger_has_no_tokens_stop | Strong | Four usage levels and readout semantics |
| 4 | a_numeric_budget_still_stops | Strong | Numeric control still raises token stop |
| 5 | state_says_not_budgeted_and_names_the_repo_file | Strong | Real CLI display and hash |
| 5 | a_legacy_ledger_says_so | Strong | Source-absent persisted shape loads and identifies legacy |
| 6 | continue_tokens_on_an_off_loop_is_refused | Strong | Exit/message plus complete byte equality |
| 6 | continue_rounds_on_an_off_loop_raises_the_cap | Strong | Persisted off budget; state shows 0/4 |
| 7 | off_loop_stops_at_the_round_cap | Strong | Exact cap and one-below boundary |
| 8 | bad_token_budget_fails_closed | Strong | Six invalid persisted values rejected |
| 8 | unknown_limits_source_key_fails_closed | Strong | Unknown provenance key rejected |
| 8 | integer_budget_without_source_loads | Adequate | Legacy positive loading control; independent old/new comparison adds cap proof |
| 9 | tightened_block_applies_to_plan_and_execution | Strong | Distinct mode budgets and persisted carrier |
| 9 | repo_basis_with_equal_values_is_accepted | Adequate | Positive equal-values branch and output |
| 9 | discovery_ignores_the_block | Strong | Persisted discovery cap and absent plan provenance |
| 9 | malformed_block_fails_closed | Strong | Four malformed/contradicted cases, exit 3, no write |
| 9 | block_that_differs_from_task_is_refused | Strong | Real differing carriers, message, exit and no write |
| 10 | loosened_block_is_refused_and_names_continue | Strong | Absent dependency, precise refusal, no subprocess traceback or ledger |
| 11 | round_flag_tightens | Adequate | Correct begin cap and applied-flag output |
| 11 | token_flag_tightens_off | Strong | Persisted numeric budget and exact flag provenance |
| 11 | round_flag_loosening_is_refused | Strong | Refusal and no write |
| 11 | token_off_flag_under_an_on_file_is_refused | Strong | Numeric-to-off loosening refused without write |
| 11 | bad_flag_values_are_usage_errors | Strong | Three argparse exit-2 cases and no ledger |

### Durable reviewer evidence

All commands below ran from `P:/av-kit` with the scratch environment described above. The tested state is the reconciled full state quoted in Q9.

```json
{"schema_version":"evidence.v1","check_id":"review-r1-pytest","command":"rtk proxy uv run --no-sync python -B -m pytest tests/tooling/test_review_limits.py -p no:cacheprovider --basetemp=C:/Temp/av-kit/rl/exec-review/pt -q","cwd":"P:/av-kit","scope":"only tests/tooling/test_review_limits.py","phase":"targeted","exit_code":0,"result":"pass","tested_state":"1abf6698c2112e42deb8c298ec04c9f439cc63c3+b55be148dc4a727660214d7c3caa47f9501e2c31d835f31da4d352f900a8466a","output":"55 passed in 5.68s"}
```

```json
{"schema_version":"evidence.v1","check_id":"review-r1-ledger-selftest","command":"rtk proxy uv run --no-sync python -B tools/review_ledger.py selftest","cwd":"P:/av-kit","scope":"ledger selftest; scratch-only writes","phase":"targeted","exit_code":0,"result":"pass","tested_state":"1abf6698c2112e42deb8c298ec04c9f439cc63c3+b55be148dc4a727660214d7c3caa47f9501e2c31d835f31da4d352f900a8466a","output":"RESULT: 126 arm(s), 0 failure(s) [62 must-OK arms, so the tool is not refusing everything]"}
```

```json
{"schema_version":"evidence.v1","check_id":"review-r1-cli-and-legacy-probes","command":"rtk proxy uv run --no-sync python -B C:/Temp/av-kit/rl/exec-review/probe.py","cwd":"P:/av-kit","scope":"all five modes on scratch repo copy; state only on copies of live ledgers; template/hash/line-ending reads","phase":"targeted","exit_code":0,"result":"pass","tested_state":"1abf6698c2112e42deb8c298ec04c9f439cc63c3+b55be148dc4a727660214d7c3caa47f9501e2c31d835f31da4d352f900a8466a","output":"All five modes: 10^12 usage per recorded round; no tokens stop; round cap refuses; mixed continuation refuses with identical bytes; round-only grant permits. 94 ledger copies loaded; all 93 historical effective caps identical under old/new implementations. Twins match; AGENTS hash matches; rule map differs only by pin; all 17 modified files CRLF. independent probes: all assertions passed"}
```

```json
{"schema_version":"evidence.v1","check_id":"review-r1-source-evidence-audit","command":"rtk proxy uv run --no-sync python -B C:/Temp/av-kit/rl/exec-review/audit.py","cwd":"P:/av-kit","scope":"UPSTREAM AST comparison, prior selftest arms, named receipt claims, baseline arithmetic, gate identity, dispatch negative fixture and actual frontmatter reader","phase":"targeted","exit_code":0,"result":"pass","tested_state":"1abf6698c2112e42deb8c298ec04c9f439cc63c3+b55be148dc4a727660214d7c3caa47f9501e2c31d835f31da4d352f900a8466a","output":"16 relevant functions executable-AST identical to UPSTREAM. 76 prior literal arm calls unchanged; 105 baseline names retained; 21 required additions. Named receipts agree; 2559+49=2608. All 16 gate step exits and before/after state verified. All three dispatch receipts have exact approved pair; consistently recounted unexpected failure refused. Actual flat frontmatter ignores commented block. source/evidence audit: all assertions passed"}
```

Other independently executed checks: `red-check.py` with all nine required ids reported zero problems; its selftest passed 36 fixtures. `prose-check.py --rows P1-P22 --begin-examples --agents-size --templates` and its selftest reported zero problems/failures. `dispatch-check.py --selftest` reported zero failures. These commands used `rtk proxy uv run --no-sync python -B` and exited 0. Scratch receipts and probe sources are retained in the designated review folder; decisive results are embedded above.

## Verdict

**approved** — zero findings. The delivered work achieves the registered goal, with real assertion-based Red/Green evidence, independent end-to-end scratch probes, preserved legacy caps and a fresh full gate bound to the reviewed inputs.

No correction or additional review round is required by this report. The coordinator owns canonical report placement, live ledger recording and H2. Approval here neither performs nor judges the later commit/push.

Residual limits: review used the declared strict frontmatter grammar and the matching recorded full gate. The known dispatch fixture pair remains accepted under D-739. No independent full-suite run, model dispatch or product-runtime pass is claimed.
