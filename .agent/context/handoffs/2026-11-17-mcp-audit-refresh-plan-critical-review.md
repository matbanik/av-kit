---
date: "2026-11-18"
review_mode: "plan"
target_plan: "docs/execution/plans/2026-11-17-mcp-audit-refresh/implementation-plan.md"
verdict: "approved"
findings_count: 0
template_version: "2.2"
requested_verbosity: "standard"
agent: "codex-independent-reviewer"
loop_id: "mar-plan-2026-11-17-mcp-audit-refresh"
round: 1
---

# Critical Review: mcp-audit-refresh

> **Review Mode:** plan
> **Verdict:** approved

## Scope

**Intent anchor:** in container mode the audit runner samples each census network proof up to three times, about 5 s apart, and a proof holds when any sample is blocked, so one lucky fetch no longer turns an environment failure into a counted one; `.agent/workflows/mcp-audit.md` says so in one note; `avkit_capture`'s top-level tool description is a real one, built from its existing per-action text with the sentences every action repeats removed and the two facts the Session 64 eval missed first (call `image` to view a frame or sheet; call `sheet` again over a narrower span to zoom), under 4,096 characters, while `_meta.action_descriptions`, every input schema and the other seven tool descriptions stay byte-identical (D-1134 A); the three Session 64 eval tasks pass on the new description; and one authoritative Windows audit run with clean cleanup and no regression records, as Mat ruled (D-1159 A), the five served actions that `BASELINE_PENDING` holds (`avkit_convert.probe`, `avkit_capture.crop`, `.frames`, `.sheet` and `.export`) into the committed baseline and report, with `BASELINE_PENDING` emptied in the same change; no file under `packages/`, `tools/`, `ui/` or `tests/` changes, and no API route or OpenAPI document changes. Tests and scripts prove each part; there is no manual check.

Reviewed the whole working-tree implementation plan, task and six plan-local supporting files; grouping §§1–8, the three issue records and HDP decisions; the cited audit runner, census, classifier, discovery, backend, coverage tests, description registration and existing action text; the workflow/build-plan requirements; Session 64's prompts, harness and checker; and the expert-pass receipt. Applied PR-1 through PR-9 and the Materiality Gate. Claude Code/Anthropic authored the plan; Codex/OpenAI independently reviewed it.

The plan has 15 ACs and 26 unstarted task rows. The three proposed product/test files and implementation handoff are absent as expected. Scheduled helper copies have source files and explicit creation rows. Row 0 rebinds citations, content hashes, dirty state, register state and description pins to the actual execution tree after Sessions 74 and 91; a moved HEAD alone is not a defect.

Only `C:/Temp/av-kit` was written. No pytest, Vitest, npm, uv sync/lock, audit, application/backend launch or network request ran. The description probe registered an in-memory server without connecting a transport. Forbidden files were not opened. The coordinator publishes the report canonically and records the verdict in the ledger.

## Findings

| # | Severity | Blocking | Kind | Finding | File:Line | Recommendation | Status |
|---|---|---|---|---|---|---|---|

## Q1 — Goal and acceptance coverage

Accepted: AC-1–6/rows 1–2 cover sampling and the workflow note; AC-7–10/rows 3–4 cover the exact candidate and unchanged surrounding surface; AC-11/row 5 is the original eval; AC-12–14/rows 6–7 require the one authoritative update, its report and the empty pending list; AC-15/row 8 and H1-4 cover registers and excluded directories. The runner actually writes both baseline and report (`run.ts:583–642`). There is no human behavior-check row.

The successful path delivers the entire anchor. D-1161/D-1162 are accepted as the supplied authorized fallback outcomes: they explicitly record unmet ACs and retain follow-up issues, rather than establishing a successful eval or baseline update. This approval assesses an executable plan, not an already completed implementation or a guarantee that the external run will pass. No blocking omission found.

## Q2 — Census sampling and Red

Accepted: `NETWORK_PROOF_SAMPLE`, `PROBES_SEAM` and `NETWORK_PROOF_GATHER` preserve the first fetch and URL selection, introduce only between-sample sleeps, and stop at the first blocked sample (plan:114–118). Extract remains the negation of exit 0, cancel requires exit 3 plus its wall, and compile requires the adapter's retryable-caption exit 3 (`run.ts:353–407`). Each URL retains the existing all-URLs requirement; the false value still satisfies `census.ts:25,39,48`. Authoritative mode continues to tolerate nothing (`classify.ts:204–214`).

The one-sample extraction makes names/imports available before Red; seven assertions fail on missing retries while six guards pass. Fake probes count calls and exact 5000 ms sleeps without network or wall-clock delays. The production entrypoint is explicitly wired to the tested gatherer, and AC-68.2 continues scanning every audit script. The nested note describes the actual three probe meanings. No stronger new extract-signature requirement is invented. Actual Red/Green execution remains required; none was run during review.

## Q3 — Description and existing test pins

Accepted: the checked-in candidate is 3,989 UTF-8 bytes, 3,981 characters and 14 lines, with the exact lead, four marker lines and nine ordered action lines. Independent tracing against the currently registered capture `_meta` found no missing sentence. The seven SHA-256 pins match the current built surface. Mat's ruling specifies the transformation; D-1157 pins its concrete output byte-for-byte in the expected file.

`desc-check.mjs:41–88` reaches the advertised `tools/list` schema and compares all eight metadata maps and schemas by JSON serialization, capture's exact expected text, and the other seven description strings. Unit guards additionally pin `captureDescriptions`; its byte-preserving refactor is required explicitly. Today's 145-character description is rejected with exit 1 for the intended two reasons. The four coverage edits are exactly the named pending declaration/comment, pending helper fixture, sheet test and export test (plan:153–168; task:55). Their assertion changes implement the authorized baseline transition and preserve the negative helper case. No additional assertion change is authorized.

## Q4 — One baseline update and D-1161

Accepted: row 7 makes one authoritative `--update-baseline` call with the absolute committed baseline/report paths, after dependency preparation and a fresh build. It captures the audit exit immediately, checks its pre-update deltas and checks the resulting baseline against the row-0 copy. The checker requires exactly the five pending additions, plain pass entries, unchanged old entries, no removal/finding and current commit (`baseline-diff.py:30–103`). The summary must report clean cleanup, discovery and all steps. The existing writer independently enforces authoritative Windows, cleanup and no regression (`classify.ts:171–196`).

Independent probes using the actual 70-entry baseline accept the authorized 75-entry fixture and reject a missing pending action, changed/removed old action, sixth addition and added issue field. Emptying `BASELINE_PENDING` and the four-test Red/Green are in the same change.

D-1161's concrete task command restores baseline, report and coverage test using `Copy-Item`, then compares their complete bytes with all three row-0 copies before continuing (task:56). A failed comparison stops. A non-clean run is never repaired by hand or retried until green; one infrastructure retry is allowed only without a summary. The original baseline issue stays open and new audit findings are registered. No blocker found in that action.

## Q5 — Eval fairness and D-1162

Accepted: `eval-rerun.py:55–92,104–151` reuses the original opening/tasks, media, answer key and `check_run`; drops the metadata-only section at CUT; rejects an old build lacking the lead facts; and produces fresh, separate task roots. Three sequential fresh Haiku agents, with at most one infrastructure retry per task and no retry of completed misses, bound the number of paid runs. The 0.5–2 million tokens is an estimate, not a measured spend or enforced token ceiling; actual spend is recorded at execution.

Replaying the saved Session 64 evidence reproduced precisely t1 fail (no image), t2 fail (one sheet) and t3 pass, with unchanged media. D-1162 retains the specified description, saves the failed measurements, registers one follow-up and records AC-11 unmet. It cannot tune the candidate or accept a completed failed run as a passing eval.

Non-blocking wording correction: the plan calls the eval backend fake (plan:37,320,425; task:36). The unchanged harness actually calls the isolated real `spawnBackend` (`eval-harness.ts:30,78–85,99–107`). Its allowlist and local media keep this acceptance check appropriate; the mistaken adjective does not alter the commands or expose user data.

## Q6 — Scope, network and records

Accepted: row 0 pins the execution tree, including excluded-directory hashes; S4/S12, H1-2's scope check and H1-4 prohibit unrelated source/API/OpenAPI changes. Shared registers are reread after prior-session commits. The audit starts its own backend with fresh tokens and explicit scratch app-data (`backend.ts:108–155`), checks path isolation before lifecycle work, and requires clean cleanup. `AUDIT_TMP` and the absolute output path stay under the session scratch directory. The eval also uses a fresh scratch backend and allowlisted local operations; the authoritative audit alone intentionally fetches external media/model data during execution.

The issue resolver is the existing tool-backed staged adapter with expected register hash and an exclusive Windows handle, adapted to preserve `meu_links`; add/render go through `tools/issue_triage*`. D-1161 leaves the baseline issue untouched and open; D-1162 replaces the measured text-visibility gap with a distinct eval-miss issue; otherwise all three original issues close. The supplied handed decisions do not introduce another demonstrated mandatory-human action: no unrelated test rewrite, contract change, disclosure or permission expansion is required.

Non-blocking record correction: task:77–78 contains success-only commit/next-session wording. If either authorized fallback occurs, substitute the recorded outcome rather than claiming three eval passes, an empty pending list or 75 recorded actions. The authoritative outcome is already specified accurately in rows 5, 7, 8 and H1-6; this is stale conditional closeout prose, not a missing implementation deliverable.

## Checklist Results

Source observations below were performed by `codex-independent-reviewer`, with null exits. They do not represent product-test passes.

| Check | Result | Command / procedure | Exit | Evidence |
|---|---|---|---|---|
| PR-1 Plan/task alignment | pass | Read both complete files; map AC-1–15 to rows 0–8/H1/H2 | null | Same scope, ordering, success conditions and authorized fallbacks. |
| PR-2 Not started | pass | Run the read-only inventory probe | 0 | 26 unchecked rows; three new product/test files and handoff absent. |
| PR-3 Task contracts | pass | Inspect task owners, deliverables, exact commands and helper creation rows | null | Existing helper sources; future files explicitly scheduled. |
| PR-4 Validation realism | pass | Inspect all six supporting files and their callers; run checker selftests, current-description rejection and independent contract probes | null | Exact text, schema/metadata pins, original eval oracle and baseline guards reach their observables. |
| PR-5 Sources and decisions | pass | Compare grouping, issue records, HDP §§4a/5/5a/6 and expert-pass receipt | null | Mat's D-1134/D-1159 carried out; handed choices keep supplied scope. |
| PR-6 Corrections readiness | pass | Inspect target, rolling handoff/review paths and current review round | null | First round; no prior correction census applies. |
| PR-7 Scope discipline | pass | Trace every exclusion to grouping/ruling/current code | null | No hidden required product work or invented deferred MEU. |
| PR-8 Control reachability | pass | Trace runAudit → gatherer → probes → tolerance, tools/list → description checker, and run outputs → baseline checks/restore | null | Positive and negative observables are concrete; no demonstrated material false pass. |
| PR-9 Named contracts | pass | Compare single-statement contracts with ACs and task references | null | No competing live behavior definition found. |
| Checker selftests | pass | `rtk proxy pwsh -NoProfile -Command` running the three plan-local `--selftest` entrypoints | 0 | baseline-diff, eval-rerun and desc-check each report ok; all child exits checked. |
| Registered description record | pass | `node docs/execution/plans/2026-11-17-mcp-audit-refresh/desc-check.mjs --record C:/Temp/av-kit/mcp-audit-refresh/review/description-before.json` | 0 | Eight tools recorded; capture 145 characters. |
| Old-description negative oracle | pass | `rtk proxy node docs/execution/plans/2026-11-17-mcp-audit-refresh/desc-check.mjs --baseline C:/Temp/av-kit/mcp-audit-refresh/review/description-before.json --expected docs/execution/plans/2026-11-17-mcp-audit-refresh/capture-description.expected.txt` | 1 | Intended rejection: differs from expected; still row-0 text. |
| Original eval reproduced | pass | `python -B docs/execution/plans/2026-11-17-mcp-audit-refresh/eval-rerun.py --session64` | 0 | Saved runs reproduce fail/fail/pass; this is not the new Haiku rerun. |
| Independent contract probes | pass | `rtk proxy python -B C:/Temp/av-kit/mcp-audit-refresh/review/inspect_contracts.py` | 0 | Candidate trace/pins, inventory and five baseline mutation negatives; 0 failures. |
| Product suites, new Haiku runs and authoritative audit | n/a | Reserved for execution; prohibited in this review | null | No runtime execution approval is claimed. |

### Durable evidence

The tested state below identifies the eight files currently in the target plan folder, using SHA-256 of their sorted path/hash mapping: `5a5d0be88fd73f265972f6eeb8a30d940e2e97879f54493506c5a51674ae96da`. Product-source conclusions are the cited manual working-tree observations.

```json
{"schema_version":"evidence.v1","check_id":"mar-r1-contracts","command":"rtk proxy python -B C:/Temp/av-kit/mcp-audit-refresh/review/inspect_contracts.py","cwd":"P:/av-kit","scope":"unstarted Session 92 plan; current registered description record; current committed baseline","phase":"plan-review","exit_code":0,"result":"pass","tested_state":"5a5d0be88fd73f265972f6eeb8a30d940e2e97879f54493506c5a51674ae96da","output":"15 ACs; 26 unstarted task rows; candidate 3989 UTF-8 bytes / 3981 characters / 14 lines; DESC_TRACE missing sentences []; seven SHA-256 pin errors []; baseline 70 entries, five pending keys; positive fixture 70 -> 75 plain passes; missing, changed, removed, extra and issue-bearing baseline mutations rejected; review probes: 0 failure(s)","fresh":true}
```

```json
{"schema_version":"evidence.v1","check_id":"mar-r1-description-negative","command":"rtk proxy node docs/execution/plans/2026-11-17-mcp-audit-refresh/desc-check.mjs --baseline C:/Temp/av-kit/mcp-audit-refresh/review/description-before.json --expected docs/execution/plans/2026-11-17-mcp-audit-refresh/capture-description.expected.txt","cwd":"P:/av-kit","scope":"current built registered tool surface; no connected transport","phase":"plan-review","exit_code":1,"result":"pass","tested_state":"5a5d0be88fd73f265972f6eeb8a30d940e2e97879f54493506c5a51674ae96da","output":"avkit_capture description: 145 chars (limit 4096), equals expected: false; FAIL avkit_capture: description differs from the expected file; FAIL avkit_capture: description is still the row-0 text; desc-check: 2 problem(s). Expected nonzero negative oracle.","fresh":true}
```

```json
{"schema_version":"evidence.v1","check_id":"mar-r1-session64-replay","command":"python -B docs/execution/plans/2026-11-17-mcp-audit-refresh/eval-rerun.py --session64","cwd":"P:/av-kit","scope":"saved Session 64 ledgers/reports/media; no model run or backend launch","phase":"plan-review","exit_code":0,"result":"pass","tested_state":"5a5d0be88fd73f265972f6eeb8a30d940e2e97879f54493506c5a51674ae96da","output":"run s64-real-t1: fail (successful image calls: 0); run s64-real-t2: fail (successful sheet calls: 1, needs 2); run s64-real-t3: pass (JPEG 444076 bytes, 1920x1080, source unchanged); session 64 real result reproduced: True","fresh":true}
```

## Verdict

**approved** — no evidence-backed High/Critical delivery defect or material false-passing gate was found. The plan can deliver the stated intent, with the supplied D-1161/D-1162 outcomes honestly recorded when applicable. The two wording notes above are non-blocking. Unit Red/Green, the new Haiku acceptance runs and the authoritative Windows audit remain execution obligations. Existing execution authorization is accepted; this reviewer makes no repository change, starts no execution and performs no commit.
