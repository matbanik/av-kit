---
date: "2026-10-01"
review_mode: "execution"
target_plan: "docs/execution/plans/2026-10-01-mcp-live-audit/implementation-plan.md"
round: 3
verdict: "approved"
findings_count: 1
template_version: "2.2"
requested_verbosity: "standard"
agent: "claude-fable-5-1-subagent"
---

# Critical Review: 2026-10-01-mcp-live-audit (Session 28, MEU-68)

> **Review Mode**: `execution`
> **Verdict**: `approved` — round 3 (2026-10-01): R2-1 and F5 verified closed, A13 verified fail-closed (static probes on the real function plus a live container run), attempt-3 authoritative evidence (`65bfa42` / `d9e2497`, HEAD `01f1cc9`) re-derived; one new non-blocking Low (R3-1). Round 2 was `approved` (F1–F4, S1 resolved; R2-1 Medium, F5 human); round 1 was `approved` with correction notes (3 Medium, 2 Low).

---

## Intent Anchor

MEU-68 was to deliver a runner that drives the **built** MCP server (`mcp-server/dist/index.js`) over stdio exactly as an IDE client does, against an **isolated spawned backend** (H-2), executes every compound-tool action (68 since the MEU-62 merge), passes each step only on an independent REST/filesystem observable (G25), proves every destructive action is refused without `confirm`, cleans up, diffs a committed baseline, and writes a report; plus the `/mcp-audit` workflow and `mcp-tool-audit` skill, the first authoritative Windows baseline and report, and the 05 spec-hub reconciliation. **Does the delivered work achieve this?** Yes: the runner, tests, docs, Windows baseline and report exist and behave as claimed under fresh verification (`intent_achieved: yes`). The one material oracle gap found (F1: the transcript lifecycle never proves an item was fetched) narrows what the authoritative baseline certifies for one domain but does not break any AC's stated contract; it is recorded as a non-blocking Medium with a concrete fix. No registered goal sentence was supplied to this reviewer; the anchor above restates the plan's §Goal items 1–4.

---

## Scope

**Target**: `.agent/context/handoffs/2026-10-01-mcp-live-audit-MEU-68-handoff.md` (sole work handoff of the project; the plan's Handoff Set names one MEU handoff, so no expansion applies). Correlation: date `2026-10-01` + slug `mcp-live-audit` in both the handoff frontmatter (`plan_source`) and the plan folder.
**Secondary**: `docs/execution/plans/2026-10-01-mcp-live-audit/{implementation-plan.md (incl. §Execution amendments A1–A10, Decision Log), task.md, walkthrough.md, validate-task.sh, validate-task.ps1, human-gate-decision.md, human-review-decision.md, windows-gate-result.json, mcp-audit-summary.json, windows-gate-baseline.json, container-audit-summary.json, pregate-audit-summary.json, mcp-test-floor.json}`.
**Implementation**: `mcp-server/scripts/audit/*.ts` + both JSON schemas, `mcp-server/tests/audit/*`, `mcp-server/tsconfig.scripts.json`, `mcp-server/package.json`.
**Docs**: `.agent/workflows/mcp-audit.md`, `.agent/skills/mcp-tool-audit/SKILL.md`, `docs/build-plan/05-mcp-server.md` §MCP live audit, `.agent/docs/commands.md` D6 `mcp-audit` row, `.agent/context/MCP/mcp-tool-audit-report.md`, `.agent/skills/mcp-tool-audit/resources/baseline-snapshot.json`.
**SSOT**: `.agent/context/known-issues.yaml` (5 issues filed this session), `.agent/context/meu-status.yaml` (MEU-68 `ready_for_review`).
**Tree**: branch `claude/sweet-goodall-mu69td`, HEAD `6c21d54`; full diff `0e18fbd..HEAD` (60 files, +13,977/−31). `GATED_PATHS` unchanged since the Windows tested commit `8345599` (`git diff --stat 8345599 HEAD -- mcp-server packages pyproject.toml uv.lock …/validate-task.ps1` is empty).
**Review Type**: execution review. **Checklist Applied**: IR + DR (docs are in scope: AC-68.16/68.18 and the handoff cites build-plan edits as evidence).
**Reviewer route**: user-authorized Fable 5.1 subagent (`human-review-decision.md`); the reviewer did not author this work and wrote only this file.

---

## Findings

| # | Severity | Blocking | Kind | Finding | File:Line | Recommendation | Status |
|---|----------|----------|------|---------|-----------|----------------|--------|
| F1 | Medium | no | behavior | **Transcript lifecycle oracle never asserts that any item was fetched; the authoritative run certified an empty transcript.** The plan's `AUDIT_PLAN` transcript row requires "`resume` → poll until ≥ 1 item is terminal → `stop`" with observable "an item terminal per REST". The implementation drops that step: `transcriptControl` only polls the parent job `status`, and `transcript.compile` passes on "a non-empty file inside the root". `services/transcript.py:415-420` checks `_pause` at the top of **every** iteration including index 0, so `Processing → Paused` does **not** imply a fetch. `compile_channel` (`transcript.py:300-308`) emits only `Done` items and `_volume_markdown` writes just `# <name>\n\n## Contents\n` when there are none — which is exactly the 37 B `live-rigging-snow_vol1.md` the Windows run produced (`mcp-audit-summary.json` step `transcript.compile`, 18 ms). So `transcripts_done` was 0 at compile time and the whole 18/18 transcript domain passed with zero transcripts fetched: the G25 "returns 200 and produces nothing" class the audit exists to catch. D-18's stated cause ("live-stream VODs evidently carry no fetchable captions") is a hypothesis; the alternative (pause landed before item 0 on each of the three `start` → `pause` cycles, 31 ms → 1.6 s apart) is at least as consistent with the timings. The REST row already exposes `transcripts_done` and `last_item_status` (`routes/transcripts.py:36-53`), so the plan's observable was cheap. Quiet narrowing of an approved single-statement contract (AGENTS §Communication Policy) without an amendment. | `mcp-server/scripts/audit/plan.ts:1037-1048` (transcriptControl sequence), `:1049-1063` (compile observable); plan `implementation-plan.md:163`; evidence `docs/execution/plans/2026-10-01-mcp-live-audit/mcp-audit-summary.json` (`transcript.compile` 37 B) | (a) Before `transcript.stop`, poll `GET /transcripts/{id}` until `transcripts_done >= 1` or `last_item_status` is terminal (plan observable), recorded as its own step or folded into `transcript.resume`'s observable; (b) make `transcript.compile` require at least one `## <title>` section (or `transcripts_done >= 1`), so an empty volume is `hollow`; (c) record `transcripts_done`/`last_item_status` in the step detail; (d) either amend the plan row (A11) with the human's ratification or restore the step. Note: `plan.ts` is under `GATED_PATHS`, so the fix reopens `WINDOWS_GATE` (attempt 2) per H1-6; alternatively file it as a known issue against the audit and take it in the next MCP session — the human decides. | open |
| F2 | Medium | no | behavior | **`--baseline <missing> --update-baseline` (without `--no-baseline`) treats a missing baseline as empty, spawns the backend, and on win32 writes a brand-new baseline at the mistyped path.** `BASELINE_UPDATE_RULE` says "A missing baseline file is an error (exit 4) unless the run passes `--no-baseline`" and AC-68.10 says a missing/malformed baseline is "never treated as empty". The first branch at `run.ts:286` is guarded by `!options.updateBaseline`, so the replace-baseline path (the workflow's step 3 "replacing the baseline adds `--update-baseline`") loses the check. Reproduced with the fake backend: `--mode container --baseline <missing> --update-baseline --discovery-only` → launcher called once, exit **2** (not 4), 0 deltas; `--mode authoritative` with `platform: "win32"` → exit **1** and the missing file is **created** (`schema: mcp-audit-baseline.v1`, `recorded_commit: 6c21d54…`); control without `--update-baseline` → exit 4 as specified. Impact: a replacement run with a wrong `--baseline` path reports no `REGRESSION` (nothing to compare), writes a stray baseline, and exits as if clean apart from findings. The committed gate path is unaffected (`validate-task.ps1` passes `--no-baseline --update-baseline` with the repo path, and `findings-check` would reject a stray copy), which is why this is not blocking. `run-cli.test.ts:62` covers only the flag-absence case. | `mcp-server/scripts/audit/run.ts:286-291`; `run-cli.test.ts:62-64` | Make the existence check unconditional: `if (!noBaseline && baseline && !existsSync(baseline)) throw new BaselineError(...)` before `launcher(root)` (exit 4, no spawn), then parse when present; add a `run-cli`/runner test "`--update-baseline` with a missing `--baseline` is exit 4 and never launches". `run.ts` is `GATED_PATHS` (same gate note as F1). | open |
| F3 | Medium | no | test-coverage / claim | **AC-68.5's second clause ("the committed baseline's entries equal `AUDIT_ACTION_SET` once it exists") has no automated check on the committed file, and the handoff's cited evidence does not perform it.** The handoff AC-68.5 row cites "`windows-gate-check` (baseline = 68 entries)"; `windows_gate_assert` counts distinct `(tool, action)` pairs in the **summary steps** (`validate-task.sh:261-263`) and checks only the baseline **header** (`:265-267`); `findings-check` checks equality with the gate copy and issue ids, not `ACTION_INDEX`. `coverage.test.ts:52-64` exercises `baselineCoverage()` on synthetic entries only. Reviewer verified the fact independently: baseline entries ⊖ `ACTION_INDEX` = ∅ both ways (68/68), so the delivered state is correct; the gap is that the plan's Out-of-Scope row relies on "AC-68.5 makes the omission a test failure in Session 30", which holds for `AUDIT_PLAN` coverage but not for the baseline file. Citation does not support the claim (Materiality Gate #6), so this stays Medium rather than clerical. | handoff `…-MEU-68-handoff.md:45`; `docs/execution/plans/2026-10-01-mcp-live-audit/validate-task.sh:261-267`; `mcp-server/tests/audit/coverage.test.ts:52-64` | Add to `coverage.test.ts`: when `.agent/skills/mcp-tool-audit/resources/baseline-snapshot.json` exists, `parseBaseline` it and assert `baselineCoverage(entries, ACTION_SET)` is `{missing: [], extra: []}` (and `findings[]`/non-pass entries carry `issue`). Correct the handoff's AC-68.5 evidence cell to name that test. Test-only change (not `GATED_PATHS`… note `mcp-server/**` **is** in `GATED_PATHS`; a test-only edit still reopens the gate by the letter of §3.4 — the human may accept a test-only exception or batch it with F1/F2). | open |
| F4 | Low | no | clerical / auditability | **`windows-gate-check`'s per-action census is last-step-wins, not worst-of.** `v = {(tool, action): verdict for x in steps}` lets a later passing step of the same action overwrite an earlier failure, whereas the runner's `aggregate()` (`run.ts:206-215`) and the baseline use worst-of. Demonstrated on scratch copies: forcing `download.add.a` or `models.status` to `fail` still yields `PASS windows gate … non-pass ['avkit_tts.cancel']`; forcing `download.get.done` (last step of `get`) is reported. Not a false-pass of the pipeline (the baseline records worst-of and `findings-check` demands a filed issue for every non-pass entry, verified by negative probes), and the three must-pass actions are single-step, so Materiality Gate #5 applies. Also `windows-gate-result.json` `audit.actions: 96` is a step count labelled "actions" (not read by any check). | `docs/execution/plans/2026-10-01-mcp-live-audit/validate-task.sh:261,276`; `validate-task.ps1:120` | Aggregate with the runner's `WORST` order in the gate script (`fail < blocked < skip_env < pass`) and rename `audit.actions` → `audit.steps`. Plan-folder scripts only (`validate-task.ps1` is `GATED_PATHS`; the `.sh` is not). | open |
| F5 | Low | no | governance observation | **Stop Condition read narrowly.** Plan §Stop Conditions: "The authoritative run finds a `fail` in MEU-62's surface (`tts.*`, `models.*` runtime assets). That reopens MEU-62 through a Decision Brief; it is not filed as a new issue against a closed MEU." The one authoritative failure is `avkit_tts.cancel`; the author classified it autonomously (D-14) as the pre-existing synchronous `POST /tts/generate` route (`routes/tts.py:54-69`, confirmed), not MEU-62's asset work, and filed `MCP-TTS-GENERATE-SYNCHRONOUS` (high) instead of stopping. The classification is defensible and disclosed in the handoff (§Deferred Items, reviewer flag 4), but the literal trigger (`tts.*`) was met and the protocol says stop. | `implementation-plan.md:304`; handoff Decision Log D-14 | One-line human ratification of D-14's classification in the reflection or `human-gate-decision.md` (no code change). | open |

### Judgement on the seven flagged expectation changes

| # | Change | Verdict | Evidence |
|---|---|---|---|
| 1 | A7 / D-15: 67 → 68 in `coverage.test.ts` and the fake-backend discovery count | **Legitimate, source-backed.** The expectation tracks the served registry; the merge `76465a0` brought `avkit_models.download_asset` (`mcp-server/src/toolsets/registry.ts:120`). Reviewer-parsed `ACTION_INDEX` = 68 rows; `AUDIT_PLAN` covers all 68 and calls nothing outside them (`coverage.test.ts` green; `planKeys ⊖ ACTION_SET = ∅` both ways in the Windows summary). Confined to the two count assertions as stated. | `registry.ts:120`; probe output "ACTION_INDEX rows 68 … summary-ACTION_INDEX set() ACTION_INDEX-summary set()" |
| 2 | D-17: `docs.test.ts` frontmatter regex `\r?\n` | **Legitimate; not a weakening.** `/^---\r?\n[\s\S]*?description:[\s\S]*?\r?\n---\r?\n/` still requires an opening fence at byte 0, a `description:` key, and a closing fence; only the line terminator is widened. `.gitattributes text=auto` makes the Windows checkout CRLF. | `mcp-server/tests/audit/docs.test.ts:46` |
| 3 | A3: AC-68.1 negative oracle (token_missing → isolation refused, exit 3) fixed before Red | **Legitimate correction of mechanism, logged pre-Red.** `tools/list` needs no token; the first tool call is the isolation snapshot (`run.ts:isolate`, `settings.get`), which surfaces `token_missing`. The test proves `initialized: true`, `isolation.ok: false`, `/token_missing/`, exit 3 and **zero** lifecycle mutations against the real `dist/index.js`. The fake needs `noTokenFile` because the server falls back to `{app_data}/mcp-token.txt` (`config.ts:156-178`) — an honest fixture repair, not an expectation edit. | `runner-fake-backend.test.ts:79-95`; fresh run green |
| 4 | A8 / D-14: `tts.cancel` runs `REFUSAL_ORACLE` on a finished job and fails `confirmed_no_effect` under `FILED_STEP_FAILURES` | **Legitimate as to the oracle; governance note F5.** Source confirmed: `routes/tts.py:54-69` calls `tts.generate(...)` inline and returns the finished job; `mcp-server/src/client.ts:14` `DEFAULT_TIMEOUT_MS = 30_000`; pregate attempt 1 recorded `fetch_failed` at 30,005 ms. The oracle is intact: both refusals held (`isError: true`, `changed: false`) and the confirmed call's no-effect is reported as `fail`, not skipped. The tolerance is script-side and exact on `(tool.action, reason, issue-id)`: a regression to `refusal_missing`, `refusal_mutated` or `confirmed_error` is **not** tolerated (`audit_container_assert`, `validate-task.sh:171-173`), and `findings-check` demands the issue id exist (negative probes `fc_issue_removed`, `fc_bogus_issue` → FAIL). | summary `tts.cancel` refusal record; probes below |
| 5 | A2 / D-12: discovery findings tolerated only via `FILED_FINDINGS` | **Legitimate.** `FILED_FINDINGS` maps only `schema_not_advertised`; `missing_tool`, `unexpected_tool`, `schema_meta_disagree`, `removed_action`, `ghost_action` stay untolerated (`classify.ts:60-108`; `validate-task.sh:138-141`). The baseline carries the 8 findings with `issue`, and removing one `issue` fails `findings-check` (probe). Source: SDK 1.30.0 `normalizeObjectSchema` drops the Zod union; the real server lists `{"type":"object","properties":{}}` for all 8 tools (fresh fake-backend run exits 1 on exactly these findings). AC-68.3 unchanged. | `classify.ts:79-91`; `known-issues.yaml` `MCP-TOOLS-LIST-EMPTY-INPUT-SCHEMA` (open, high) |
| 6 | A9 / D-16: transcript fixture swap; per-URL network proof; `download.cancel` census member | **Legitimate; fail-closed.** The proof is granted only when **every** failing step's own URL also fails a direct `yt_dlp` extract; an unmapped step id yields `url === undefined` → not tolerated (`run.ts:451-461`). Authoritative mode tolerates nothing (`countedFailures`; `windows_gate_assert` rejects `skip_env`, probe). Windows ran all network steps live with 0 `skip_env`. The `download.cancel` member's env proof is platform-only (weaker than the per-URL proof; see OOC-2) but container-only. | `census.ts:22-39`; pregate summary (2 × `download.add` skip_env with `env_bound` all true) |
| 7 | A10: `${RESOURCES}` → `$RESOURCES` in D-6's precedent | **Clerical; faithful enough.** `docs/distribution/mcp.json.example` literally uses `"${RESOURCES}/mcp-server/index.js"`; the prose at §User Review Required keeps the literal; only the YAML precedent string was de-braced for the closeout validator. | `mcp.json.example:5` |

### Tolerance masking analysis

- **`ENV_BOUND_AUDIT`**: `applyTolerance` requires member **and** signature **and** env proof, container mode only; `countedFailures` counts `skip_env`/`blocked` in authoritative mode; `windows_gate_assert` rejects any `skip_env` (probe `skip_env` → FAIL). Cannot mask an authoritative failure.
- **`MEU62_PENDING_TOLERANCE`**: off (MEU-62 `approved` by JSON parse; neither pregate nor Windows used it). `meu_status_is` failure fails closed (`fail` exits the script).
- **`FILED_FINDINGS`** / **`FILED_STEP_FAILURES`**: exact-match, issue-bound, script-side; `findings-check` enforces `BASELINE_ANNOTATION_RULE` (status edit → FAIL, probe) and an existing issue id for every non-pass entry and finding (probes). `windows_gate_assert` itself does not inspect discovery findings, but every finding lands in the baseline and is checked there.
- **Residual holes found**: F1 (oracle gap, not a tolerance), F2 (baseline branch), F4 (gate printout only).

### Out-of-Contract Observations (non-blocking)

1. `tts.cancel` can now pass only through a `Done → Cancelled` transition, which would itself be a state-machine defect; the plan already says the step is rewritten when `MCP-TTS-GENERATE-SYNCHRONOUS` is fixed — tie that rewrite to the issue's `verification`.
2. `avkit_download.cancel`'s census env proof is `platform !== "win32"` only (the walkthrough's attempt-3 reproduction is the actual proof); acceptable because container-only and the signature is the job's own bot-wall `error_message`, but it is weaker than the per-URL rule the same amendment introduced.
3. The plan's transcript row called for the 409 conflict contract on **both** `requeue` and `retry` (on a Done job); the implementation pins `retry` on Pending only (`transcript.retry.conflict`); `requeue`'s conflict path is unexercised.
4. Plan AC-68.13 prose still says "8 tools, 67 actions" (the report and tests say 68) — clerical, plan text only.
5. The real runner always provisions `mcp-token.txt`, so the AC-68.1 token-missing negative is reachable only through the fake's `noTokenFile`; informational.

---

## Checklist Results

### Commands executed (fresh, this review)

```json
{"schema_version":"evidence.v1","check_id":"rev-mcp-types","command":"npm --prefix mcp-server run typecheck","cwd":"/home/user/av-kit","scope":"src + scripts (tsconfig.scripts.json)","phase":"static","exit_code":0,"result":"pass","tested_state":"6c21d54 clean","output":"tsc --noEmit && tsc -p tsconfig.scripts.json | TYPECHECK_EXIT=0","fresh":true}
```
```json
{"schema_version":"evidence.v1","check_id":"rev-mcp-build","command":"npm --prefix mcp-server run build","cwd":"/home/user/av-kit","scope":"dist/ for the fake-backend suite","phase":"static","exit_code":0,"result":"pass","tested_state":"6c21d54 clean","output":"BUILD_EXIT=0","fresh":true}
```
```json
{"schema_version":"evidence.v1","check_id":"rev-mcp-tests","command":"npm --prefix mcp-server test","cwd":"/home/user/av-kit","scope":"full MCP Vitest incl. tests/audit (96)","phase":"full","exit_code":0,"result":"pass","tested_state":"6c21d54 clean","output":"Test Files 20 passed (20) | Tests 318 passed (318) | runner-fake-backend 7 tests 4118ms (real dist/index.js over stdio) | Duration 6.43s","fresh":true}
```
```json
{"schema_version":"evidence.v1","check_id":"rev-validate-task","command":"RECEIPTS_DIR=<scratchpad>/receipts/review bash docs/execution/plans/2026-10-01-mcp-live-audit/validate-task.sh {task-state,windows-gate-check,findings-check,scope b,docs,api-scope}","cwd":"/home/user/av-kit","scope":"H1 gates on the final tree","phase":"static","exit_code":0,"result":"pass","tested_state":"6c21d54","output":"PASS task-state: 12 rows done | PASS windows gate @ 8345599d0c22b63c85bc070b7ad9d930048d5c7c: mcp_tests {'passed': 318, 'failed': 0, 'total': 318}; audit 68 actions, non-pass ['avkit_tts.cancel'] | PASS findings: 1 non-pass, all filed | PASS scope b: 60 changed paths, all allowed; PASS AC-68.2 | PASS green: 7 passed; PASS docs | PASS api-scope: no packages/ change vs 0e18fbd…","fresh":true}
```
```json
{"schema_version":"evidence.v1","check_id":"rev-closeout-validator","command":"uv run python tools/validate_closeout_artifacts.py --handoff .agent/context/handoffs/2026-10-01-mcp-live-audit-MEU-68-handoff.md --plan docs/execution/plans/2026-10-01-mcp-live-audit/implementation-plan.md","cwd":"/home/user/av-kit","scope":"handoff structure + AC coverage","phase":"static","exit_code":0,"result":"pass","tested_state":"6c21d54","output":"OK: required sections present; 18 AC row(s); 22 decision(s) logged; durable evidence present; plan_source binds; all 1 plan AC(s) present (validator reads AC-68.x as one id) | reviewer grep: handoff rows AC-68.1…AC-68.18 all present (18 distinct), plan rows 18","fresh":true}
```
```json
{"schema_version":"evidence.v1","check_id":"rev-evidence-crosscheck","command":"python3 (reviewer script) over mcp-audit-summary.json, windows-gate-baseline.json, baseline-snapshot.json, windows-gate-result.json, registry.ts; npx tsx schemacheck.ts (runner's own validate()/parseBaseline)","cwd":"/home/user/av-kit","scope":"AC-68.4/5/7/13/14/15 authoritative evidence","phase":"targeted","exit_code":0,"result":"pass","tested_state":"39de635 files at 6c21d54","output":"mode authoritative, commit 8345599…, counts {pass 95, fail 1, skip_env 0, blocked 0, total 96}, 68 distinct actions, discovery 8/68 with 8 × schema_not_advertised, cleanup all true, isolation 6 keys under C:\\Users\\Mat\\AppData\\Local\\Temp\\avkit-mcp-audit-Gwz8AY\\out | pass-without-observable: [] | 7 refusal records: all omit/false isError=true changed=false; 6 confirmed changed=true, tts.cancel confirmed changed=false | deltas 68 × NEW | summary/container/pregate summary schema errors: [] | both baselines parseBaseline OK | baseline 68 entries (67 pass, 1 fail) ⊖ ACTION_INDEX(68) = ∅ both ways | gate→committed baseline diff = 9 added `issue` lines only | committed summary sha256 == windows-gate-result.audit.summary_sha256 (7A9868F3…1D8E) | redaction scan over all committed outputs: 0 hits","fresh":true}
```
```json
{"schema_version":"evidence.v1","check_id":"rev-gate-negatives","command":"scratch copy of validate-task.sh (PLAN and committed-baseline path redirected to scratchpad copies; repo untouched) with mutated JSON per case","cwd":"/home/user/av-kit","scope":"AC-68.15 negative cases + F4","phase":"targeted","exit_code":0,"result":"pass","tested_state":"6c21d54","output":"windows-gate-check: none → PASS; audit_exit3 → FAIL mcp-audit exit 3; mode_container → FAIL summary mode/commit; cleanup_false → FAIL cleanup; ttsgen_fail → FAIL must-pass [('avkit_tts','generate')]; baseline_commit → FAIL gate baseline header; stage_missing → FAIL stages; summary_commit → FAIL; skip_env → FAIL skip_env not allowed | findings-check: none → PASS; fc_issue_removed → FAIL non-pass without issue ['avkit_tts.cancel']; fc_status_changed → FAIL BASELINE_ANNOTATION_RULE; fc_finding_issue_removed → FAIL ['finding schema_not_advertised:avkit_download']; fc_bogus_issue → FAIL | F4: lastwins_add_a_fail → PASS non-pass ['avkit_tts.cancel'] (masked in printout); lastwins_models_status_fail → PASS (masked); lastwins_get_done_fail → PASS non-pass ['avkit_download.get','avkit_tts.cancel']","fresh":true}
```
```json
{"schema_version":"evidence.v1","check_id":"rev-baseline-branch-probe","command":"npx tsx <scratchpad>/bl-probe/probe.mts (runAudit with fakeLauncher, discovery-only)","cwd":"/home/user/av-kit/mcp-server","scope":"F2 (BASELINE_UPDATE_RULE missing-file branch)","phase":"targeted","exit_code":0,"result":"fail (defect reproduced)","tested_state":"6c21d54","output":"parseCli ok: noBaseline=false updateBaseline=true baseline exists=false | container+update-baseline+missing-file: exit 2, launcher calls 1, deltas 0 | authoritative(win32 override)+update-baseline+missing-file: exit 1, baseline file now exists: true (schema mcp-audit-baseline.v1, recorded_commit 6c21d54…) | control: container --baseline <missing> (no update): exit 4","fresh":true}
```
```json
{"schema_version":"evidence.v1","check_id":"rev-source-reads","command":"sed/grep over packages/core/src/avkit_core/services/transcript.py:298-345,405-430; packages/api/src/avkit_api/routes/transcripts.py:25-53, routes/tts.py:50-72; mcp-server/src/client.ts:10-20; avkit_infra/tts/assets.py:60-140,215-245; avkit_infra/model_manager/{manager,vocab}.py (hf_hub_download local_dir=models_dir)","cwd":"/home/user/av-kit","scope":"F1, A8, isolation of model/asset writes","phase":"static","exit_code":0,"result":"pass","tested_state":"6c21d54","output":"compile_channel emits only Done items; empty volume = heading + '## Contents' (≈37 B) | pause checked at loop index 0 before any fetch | REST row carries transcripts_done/last_item_status | POST /tts/generate synchronous; MCP DEFAULT_TIMEOUT_MS 30_000 | assets live under tts.models_directory (isolated); spaCy readiness via sys.path under models_dir, never pip; hf_hub_download uses local_dir under the isolated models dir","fresh":true}
```

### Implementation Review (IR)

| # | Check | Result | Evidence |
|---|---|---|---|
| IR-1 | Live runtime evidence | pass | `runner-fake-backend.test.ts` drives the real `dist/index.js` over SDK stdio (7 tests, fresh green); container run against a real spawned `avkit_api` (`pregate-audit-summary.json`, 77/96, exit 1 tolerated exactly as documented); authoritative Windows run bound to `8345599` with summary sha match. |
| IR-2 | Stub behavioural compliance | pass | `fake-backend.ts` honours save→get (201 then 200), 404 after DELETE, `vanishDownloadOnGet`/`hollowDownloadAdd`/`ignoreSettingKeys`/`noTokenFile` switches each drive one negative oracle; `backend.json` written like `write_descriptor`. |
| IR-3 | Error mapping completeness | n/a | No API/route change (`api-scope` PASS; `packages/` untouched). |
| IR-4 | Fix generalization | pass | D-17 portability fixes applied to all three sites (regex, `uv` spawn without shell, win32 path case); A9 per-URL proof applied to every `NETWORK_STEP_URLS` member. |
| IR-5 | Test rigor audit | pass (no 🔴) | `classify` 🟢 (exact verdict/reason `toEqual`), `coverage` 🟢, `baseline` 🟢 (SHA-256 before/after refusal), `isolation` 🟢 (incl. sibling-prefix and unmapped-key negatives), `ledger` 🟢, `redact` 🟢 (byte scan of all 4 output files), `report` 🟢/🟡 (schema negatives + needle contains), `run-cli` 🟢 (seeded forbidden import, exit 4 without spawn), `runner-fake-backend` 🟢 (exit codes, mutation counts, root removed), `docs` 🟡 (string contains; adequate for AC-68.16). The audit **runner's own** oracles are the subject of F1 (transcript item fetch unasserted). |
| IR-6 | Boundary validation coverage | pass | `parseArgs strict` → `CliError` exit 4 before spawn; `--fixture` unknown key → error; baseline schema `additionalProperties:false`, duplicate/40-hex/schema-id negatives; MCP result shape → `malformed`/`fail`. F2 is the one boundary gap found. |
| IR-7 | Deferral & AC coverage | pass | (a) one `deferred` row → MEU-67 (scheduled, Session 30); `out-of-scope` rows carry a Basis that the cited sources support (05 §Client "built server", 07:246-249, 05 §What this layer must not do). (b) all 18 AC ids present in the handoff table. (c) integration ACs (68.1/4/6/7/8/9/15/16) are backed by the stdio fake-backend suite, the live container/Windows runs, or doc-tests that read real files — none by a unit test alone. F3 notes AC-68.5's baseline clause lacks an automated check. |

### Docs Review (DR)

| # | Check | Result | Evidence |
|---|---|---|---|
| DR-1 | Claim-to-state match | pass | 05 §MCP live audit reconciled (Backend row H-2, Where-it-runs D-8, `ACTION_INDEX` governs); D6 `mcp-audit` row at `commands.md:207`; workflow/skill/READMEs present; `docs` check PASS. |
| DR-2 | Residual old terms | pass | `STALE_SPEC_PATTERNS` fixed-string `rg` → 0 hits (section extracted by `awk`). |
| DR-3 | Downstream references | pass | Both README index rows; skill ↔ workflow cross-links resolve; `docs.test.ts` asserts every cited `npm run` script and `--flag` exists (negative `audit-x`/`--frob` caught). |
| DR-4 | Verification robustness | pass with F4 | `windows-gate-check` rejects all AC-68.15 negatives (probe); census printout is last-wins (F4). |
| DR-5 | Evidence auditability | pass | evidence.v1 blocks in the handoff reproduce (counts 318/96/68/95-1 all re-derived here); summary sha256 bound to the gate result. |
| DR-6 | Cross-reference integrity | pass | Plan single-statement names resolve in `validate-task.sh` (`AUDIT_ACTION_COUNT`, `FILED_FINDINGS_JSON`, `FILED_STEP_FAILURES_JSON`, `STAGES_WINDOWS`, `GATED_PATHS`). |
| DR-7 | Evidence freshness | pass | Fresh typecheck/build/tests/gates reproduced the handoff's numbers on `6c21d54`; `GATED_PATHS` unchanged since `8345599`. |
| DR-8 | Completion vs residual risk | pass with note | Handoff claims all 18 ACs ✅ and lists the filed product defects; it does not claim transcript items were fetched. F1 should be added to the residual-risk record (walkthrough D-18 "observation") because the current wording asserts a cause the evidence does not establish. |

### Post-Implementation Review (PR)

| Check | Result | Command | Exit | Evidence |
|-------|--------|---------|------|----------|
| Evidence bundle complete | pass | `validate_closeout_artifacts.py --handoff … --plan …` | 0 | 9 evidence.v1 records; FAIL_TO_PASS table; Windows run record with observer. |
| FAIL_TO_PASS table present | pass | `grep -n "FAIL_TO_PASS" handoff` | 0 | Red 81 failing assertions / Green 96; typecheck TS2322 probe; stale-spec 3 → 0. |
| Commands independently runnable | pass | see `rev-validate-task` | 0 | All six H1 checks re-run green from a fresh `RECEIPTS_DIR`. |
| Anti-placeholder scan clean | pass | `rg -n "TODO|FIXME|NotImplemented|console\.log" mcp-server/scripts mcp-server/tests/audit` (reviewer) | 1 | No hits in runner or tests; `audit-container` exit-1 message prints via `process.stdout.write`. |

---

## Verdict

`approved` — No finding is High/Critical in Functionality-First priorities 1–4, and no Medium defeats a delivered control in the authoritative evidence, so the Verdict Rule yields `approved` with correction notes. The intent is achieved: the runner drives the built server over stdio against an isolated backend, every one of the 68 actions ran live on Windows with observable-backed verdicts, all 7 destructive refusals held with state unchanged, cleanup was clean, the baseline/report were written by the run and annotated only within `BASELINE_ANNOTATION_RULE`, every non-pass is filed, and the gate scripts reject every negative case AC-68.15 lists. The seven flagged expectation changes are each source-backed and none weakens an oracle. The three Medium notes are real and should be corrected: F1 (the transcript domain's pass does not prove a transcript was fetched; the authoritative baseline certified an empty compile), F2 (`--update-baseline` with a missing baseline silently records a fresh baseline), F3 (AC-68.5's baseline clause lacks an automated check and the handoff mis-cites its evidence). F1 and F2 touch `GATED_PATHS`, so correcting them reopens `WINDOWS_GATE` (attempt 2); the orchestrator should put that trade-off to the human rather than decide it.

**Residual risk statement.** Until F1 is corrected, a regression in transcript item fetching (youtube-transcript-api path, item persistence, compile body) would not fail the audit; every other domain's lifecycle has a content-bearing observable (downloaded media bytes, MP3 header, PNG bytes, conversion output). Until F2 is corrected, a mistyped `--baseline` on a replacement run bypasses `REGRESSION` detection; the committed gate path is unaffected.

### Concrete follow-up actions

1. **F1** — Restore the plan's "≥ 1 item terminal" observable before `transcript.stop` (poll `transcripts_done >= 1` / terminal `last_item_status` on `GET /transcripts/{id}`), make `transcript.compile` fail on a volume with no `## <title>` section, record `transcripts_done` in the step detail; log amendment A11 and correct D-18 to an open question. Reopens `WINDOWS_GATE` (plan.ts ∈ `GATED_PATHS`) — human decides whether now or as a filed known issue against the audit.
2. **F2** — In `run.ts`, reject a missing `--baseline` whenever `--no-baseline` is absent, before `launcher(root)`; add the negative test. Same gate note.
3. **F3** — Add the committed-baseline coverage assertion to `coverage.test.ts`; fix the handoff AC-68.5 evidence cell.
4. **F4** — Worst-of aggregation and `audit.steps` naming in the gate scripts.
5. **F5** — One-line human ratification of D-14's "not MEU-62's surface" classification.
6. Route any corrections through `/execution-corrections`; append the recheck under `## Recheck (YYYY-MM-DD)` in this file (round 2 of 6).

---

## Corrections Applied (2026-10-01)

Applied by the implementer (`/execution-corrections`). The verdict is set to `corrections_applied`; only a reviewer pass may set `approved`.

**Findings resolved:** 4 of 5 in code or tests (F1–F4). F5 is routed to Mat for ratification. One sibling defect, found while verifying, is also fixed.

| # | Finding | Fix Applied | Verification |
|---|---------|-------------|--------------|
| F1 | Transcript oracle never asserts a fetched item | `plan.ts`: `transcriptResume` polls until `transcripts_done ≥ 1` or `last_item_status` is `Failed` (a `Skipped` item keeps polling) and records both. `transcript.compile` requires `transcripts_done ≥ 1` and `## Contents` entries equal to it; otherwise `no transcript fetched`. `transcript.requeue.conflict` added (OOC-3). `census.ts`: `avkit_transcript.compile` member. `run.ts` `captionFetchBlocked`: the proof is the product adapter raising `TranscriptRetryableError` for the source's first video. | `tests/audit/transcript-oracle.test.ts`. Red: 7 AssertionErrors + 1 missing step. Green: 11/11. Container audit: resume `last_item_status Failed`, compile `skip_env` with the proof, both 409 contracts pass. |
| F2 | Missing `--baseline` with `--update-baseline` treated as empty | `run.ts`: one existence check (exit 4) before the launcher, whatever `--update-baseline` says | `run-cli.test.ts` "AC-68.11 --update-baseline with a missing --baseline exits 4, never launches and writes nothing". Red: spy called once. Green: never called, exit 4, file absent (container and win32). |
| F3 | AC-68.5 baseline clause unchecked | `coverage.test.ts`: the committed baseline equals `AUDIT_ACTION_SET`; non-pass entries and findings carry `issue` | Passes. Removing `avkit_tts.voices` from a temporary copy fails it (`expected { …(2) } to deeply equal { missing: [], extra: [] }`); the file was restored from git. |
| F4 | Gate census last-step-wins | `validate-task.sh` aggregates worst-of (`fail < blocked < skip_env < pass`); `validate-task.ps1` writes `audit.steps` | Scratch harness with `download.add.a` forced to fail. Before: `non-pass ['avkit_tts.cancel']`. After: `non-pass ['avkit_download.add', 'avkit_tts.cancel']`. |
| F5 | Stop Condition literal trigger (`tts.*`) | No code change. Mat is asked to ratify D-14's classification. | Pending human |
| S1 | (sibling) A never-ready backend was not killed; node stayed alive until the outer timeout | `backend.ts` `startBackendProcess`: on a ready timeout, stop the child (SIGTERM, then SIGKILL) and name its pid; `spawnBackend` delegates to it | `tests/audit/backend-spawn.test.ts`. Red: missing symbol. Green: rejects with `not ready in 300 ms … (pid N killed)`, and the pid is not alive. |

**Fresh evidence (corrected working tree, before commit):**
- `npm --prefix mcp-server run typecheck` exit 0; `run build` exit 0; `npm --prefix mcp-server test` 332 passed (22 files).
- `validate-task.sh audit-container`: `77/97 pass, 8 discovery finding(s), cleanup ok, exit 1` and `PASS audit-container: 77 pass, 20 tolerated`.

**Gate impact.** `plan.ts`, `run.ts`, `census.ts`, `backend.ts` and `validate-task.ps1` are under `GATED_PATHS`, so `WINDOWS_GATE` attempt 2 is required (plan amendment A11; `task.md` row 11 is `[B]` again). The round-2 review should follow attempt 2, so that it covers the authoritative result of the corrected runner.


---

## Recheck (2026-10-01) — Round 2

**Workflow**: `/execution-critical-review` recheck (round 2 of 6)
**Agent**: `claude-fable-5-1-subagent` (user-authorized, `human-review-decision.md`; did not author the work; wrote only this file)
**Tree**: branch `claude/sweet-goodall-mu69td`, HEAD `1884a85`, `git status` clean before and after. Corrections commit `3c949fc` (A11); attempt-2 request commit `a044446` (walkthrough-only on top of `3c949fc`: `git diff --stat 3c949fc a044446 -- <GATED_PATHS>` empty); attempt-2 result files `0434895`; `GATED_PATHS` unchanged `a044446..HEAD` (enforced by `windows-gate-check`, which passed).

### Intent re-anchor

Unchanged from round 1: the runner must drive the built server over stdio against an isolated backend, pass each of the 68 actions only on an independent observable, hold all 7 refusals, clean up, baseline and report, with an authoritative Windows run. Round 2 asks whether the corrections restore the one oracle gap (F1) without weakening anything, and whether the attempt-2 authoritative evidence proves it. **Answer: yes** (`intent_achieved: yes`).

### Prior Pass Summary

| Finding | Prior Status | Recheck Result | Evidence |
|---|---|---|---|
| F1 — transcript oracle never asserted a fetched item | open → corrections applied | ✅ **Resolved.** | `plan.ts:971-990` `transcriptResume` polls `GET /transcripts/{id}` until `status === "Processing"` and (`transcripts_done >= 1` or `last_item_status === "Failed"`); `Skipped` and `Pending` keep polling; the detail records both fields. `plan.ts:1100-1107` `transcript.compile` returns `ok=false` "no transcript fetched" when `transcripts_done < 1`, otherwise requires `## Contents` entries (`volumeSections`, one `- [` line per Done item, matching `_volume_markdown` at `services/transcript.py:330-334`) **equal** to `transcripts_done` across all volumes. `transcript.requeue.conflict` added (`plan.ts:1082`; closes round-1 OOC-3). Product semantics confirmed: `routes/transcripts.py:25-33` counts `Done` items and reports the most recently processed item's status, so `Failed`/`Skipped`/`Done` are the real terminal values. **Attempt-2 authoritative records**: `transcript.resume` pass, 1,601 ms, `transcripts_done 1, last_item_status Done`; `transcript.compile` pass, `live-rigging-snow_vol1.md 112681 B; 1 section(s), transcripts_done 1`; `requeue.conflict` and `retry.conflict` both pass with `ConflictError: illegal transcript transition Pending -> Pending; REST job Pending`. Attempt 1's 37 B volume is superseded. |
| F1 census member `avkit_transcript.compile` — masking check | — | ✅ **Cannot mask.** | `applyTolerance` (`classify.ts:~130`) tolerates only `mode === "container"`; probe: authoritative + proof → `fail`; container + proof → `skip_env`; container without probe → `fail`. Signature `^no transcript fetched` matches only the `done < 1` branch: a sections/`transcripts_done` mismatch (`"… 0 section(s), transcripts_done 1"`) → `fail`; a resume timeout → `fail` (not a member). The proof (`run.ts:366-386` `captionFetchBlocked`) is gathered only after a signature-matched compile failure, runs the product's `TranscriptAdapter.get_transcript` (`adapter.py:51`) on the source's first video, and holds only on exit 3 (`TranscriptRetryableError`, `errors.py:60`); any other outcome (`uv` failure, missing captions returning `None`, a different exception) → proof false → `fail`. Residual (container-only, see OOC-2). |
| F2 — missing `--baseline` with `--update-baseline` treated as empty | open → corrections applied | ✅ **Resolved.** | `run.ts:420-425`: one unconditional `existsSync` check whenever `!noBaseline && baseline`, thrown as `BaselineError` before `launcher(root)`. Fresh probe (round-1 `probe.mts`, missing path confirmed absent first): container + `--update-baseline` → **exit 4, launcher calls 0, deltas 0**; authoritative (win32 override) + `--update-baseline` → **exit 4, file not created**; control (no `--update-baseline`) → exit 4. Test `run-cli.test.ts:105-137` asserts all three (exit 4, launcher never called, `existsSync(missing) === false`) in both modes — 🟢. |
| F3 — AC-68.5 baseline clause unchecked; handoff mis-cited | open → corrections applied | ✅ **Resolved** (one new note, R2-1) | `coverage.test.ts:81-88` parses the committed baseline with the runner's own `parseBaseline` and asserts `baselineCoverage(entries, ACTION_SET)` `toEqual({missing: [], extra: []})`, plus `issue` on every non-pass entry and every finding. Path resolution verified (`node`: resolves to `/home/user/av-kit/.agent/skills/mcp-tool-audit/resources/baseline-snapshot.json`, exists). Assertion strength verified on a mutated **copy**: dropping `avkit_tts.voices` and adding `avkit_tts.ghost` → `{"missing":["avkit_tts.voices"],"extra":["avkit_tts.ghost"]}`; stripping `issue` from the non-pass entry → `['avkit_tts.cancel']`. Handoff AC-68.5 cell now names this test (`…-MEU-68-handoff.md:45`). |
| F4 — gate census last-step-wins | open → corrections applied | ✅ **Resolved.** | `validate-task.sh:246-254` aggregates worst-of in the runner's `WORST` order (`run.ts:235`). Fresh scratch harness on the attempt-2 files (repo untouched): `download.add.a` forced `fail` → `non-pass ['avkit_download.add', 'avkit_tts.cancel']` (round 1: masked); `models.status` forced `fail` → `non-pass ['avkit_models.status', 'avkit_tts.cancel']` (round 1: masked); `transcript.resume` forced `skip_env` → `FAIL: skip_env is not allowed in authoritative mode`. `validate-task.ps1:120` writes `audit.steps`; `windows-gate-result.json` carries `"steps": 97`. |
| F5 — Stop Condition / D-14 ratification | open (human) | ⏳ **Pending human; unchanged.** | No code change was expected. The Corrections Applied section routes it to Mat; no ratification line exists yet in `human-gate-decision.md` or a reflection. Not resolved by this reviewer (governance item for the human); non-blocking as in round 1. |
| S1 (sibling) — never-ready backend leaked | fixed by implementer | ✅ **Verified.** | `backend.ts:85-115` `startBackendProcess`: on `waitReady` rejection, `stopChild` (SIGTERM, 10 s, then SIGKILL, 5 s) runs before the error is rethrown with `(pid N killed|still running)`; `spawnBackend` delegates and keeps the same argv/env/`mcp-token.txt` provisioning. `backend-spawn.test.ts` uses node itself as a never-ready child with a 300 ms timeout and asserts the message, a parsed pid > 0, and `process.kill(pid, 0)` throwing — 🟢, cross-platform, no product dependency. Fresh run: 1 test, 414 ms. |

### Judgement on the pre-commit refinement of the resume poll

The implementer changed the poll so that a `Skipped` item no longer ends it, and adjusted its own not-yet-committed test to assert `ok === false` for `last_item_status Skipped`. **Legitimate.** The change makes the oracle *stricter* (a no-captions item cannot satisfy "an item terminal" for the purpose of proving a fetch; only `Done` with `transcripts_done >= 1` or an explicit `Failed` ends the poll), it is recorded in amendment A11 before the gate run, the expectation it replaced was never committed or used as Red evidence for a Green claim, and the committed test asserts the stricter behavior. AGENTS §Testing's immutability rule guards against fitting an expectation to broken code; this is the opposite direction. One consequence is noted as OOC-1.

### Attempt-2 authoritative evidence (fresh cross-check)

- `sha256(mcp-audit-summary.json)` = `193F8B9F…92EC` = `windows-gate-result.audit.summary_sha256`. Summary `mode authoritative`, `commit a044446…` = `tested_commit`; stages in order, all exit 0 except `mcp-audit` exit 1; `mcp_tests 332/0/332`; `clean_tree true`; preflight hashes identical to attempt 1.
- Steps **97** (`counts {pass 96, fail 1, skip_env 0, blocked 0}`), **68** distinct actions, pass-without-observable = []. Non-pass: `tts.cancel` `confirmed_no_effect` only. 7 refusal records: `refusal_omit`/`refusal_false` all `isError:true, changed:false`. Cleanup `{ok, residuals [], backend_exited, root_removed}`; isolation 6 keys under the temp root, `ok true`. Discovery 8 × `schema_not_advertised`, 0 new/removed/ghost.
- Schemas: `validate(summary.schema.json)` → `[]` for the Windows, container and pregate summaries; `parseBaseline` OK for both baselines; both `recorded_commit a044446…`.
- Committed baseline ⊖ gate copy: **`issue` keys only** (`strip(issue)(committed) == gate` → `True`; the gate copy has no `issue` keys). Annotations: `avkit_tts.cancel` → `MCP-TTS-GENERATE-SYNCHRONOUS` (1), 8 findings → `MCP-TOOLS-LIST-EMPTY-INPUT-SCHEMA`; both ids exist in `known-issues.yaml` (`:898`, `:933`). 68 entries (67 pass, 1 fail); deltas 68 × `NEW` (first baseline, `--no-baseline`).
- Report header: commit `a044446…`, 8/68, 97 steps, `96 pass, 1 fail, 0 skip_env, 0 blocked`; transcript row 19/19.
- Redaction: no bearer/token/cookie/`X-API-Token` strings in any of the five committed outputs; the 10 UUIDs in the summary/report are job ids (`/tts/9a49…`, `/downloads/ed74…`), not tokens.
- Handoff spot-claims reproduced: `download.get.done` 629,172 B; `tts.generate` MP3 60,044 B in 2,435 ms; `capture.capture` fullscreen PNG 4,631,692 B.

### Deviation: `-QuietMachineConfirmed` omitted from the attempt-2 request block

**Not material.** The switch is the operator's own attestation (`validate-task.ps1:74-75`: `quiet_machine_attested`, and `quiet_machine` also requires the script's own busy-process scan to be empty; `:81` fails preflight without it). The person it attests for is the one who passed it; the result records `quiet_machine true`, `quiet_machine_attested true`, `busy_processes []`. No code identity, stage, or input hash depends on it; the author disclosed the omission (walkthrough §Attempt 2). Clerical.

### New findings

| # | Severity | Blocking | Kind | Finding | File:Line | Recommendation | Status |
|---|---|---|---|---|---|---|---|
| R2-1 | Medium | no | test-rigor | **The F3 test neutralizes itself when the committed baseline is absent.** `if (!existsSync(COMMITTED_BASELINE)) return;` is a silent early return (AGENTS §Testing: "Never neutralize tests with skip/only/todo or silent early returns"). The baseline existed when the test was written (`39de635` predates `3c949fc`) and Part B is now complete, so the guard can only ever hide a regression: delete or relocate the baseline (D-9 path) and `npm test` stays green while asserting nothing. When the file is present the assertions are 🟢 (verified above). No *product* defect false-passes: `windows-gate-check` fails on a missing committed baseline (`validate-task.sh:272`) and the runner exits 4 (F2). | `mcp-server/tests/audit/coverage.test.ts:83` | Replace the `return` with `expect(existsSync(COMMITTED_BASELINE), "committed baseline (AC-68.5, Part B)").toBe(true)`. Test-only, but `mcp-server/**` is in `GATED_PATHS`; on its own this does not warrant reopening `WINDOWS_GATE` — batch it with the next `GATED_PATHS` change (the human decides, as with round-1 F3). | open |

### Out-of-Contract Observations (non-blocking, ≤ 5)

1. The restored transcript contract is "≥ 1 item terminal / ≥ 1 fetched". A run where some items `Failed` and one is `Done` passes the domain (within the approved contract); `transcripts_done`/`last_item_status` are now recorded in the step detail, so a reader can see it. Residual risk, not a finding.
2. `captionFetchBlocked` trusts the product adapter's error class: a product regression that mis-maps *every* fetch error to `TranscriptRetryableError` would be tolerated in **container** mode only; authoritative mode tolerates nothing (probe above). Same boundary as the per-URL network proof.
3. `backend.ts` attaches no `'error'` listener to the spawned child; a spawn-time `ENOENT` would surface as an unhandled `'error'` event rather than a `waitReady` rejection. Pre-existing (not introduced by S1) and mitigated by `resolvePython()` succeeding first.
4. Clerical, handoff: `Changed Files` still says "`AUDIT_PLAN` (96 steps / 68 actions)" and "96 tests" (now 97 steps; audit suite 110 tests, which `Quality Gate Results` states correctly); AC-68.9 and AC-68.11 rows do not cite `backend-spawn.test.ts` / the new `run-cli.test.ts` F2 test. Plan AC-68.13 prose still says "67 actions" (round-1 OOC-4).

### Commands executed (fresh, this round)

```json
{"schema_version":"evidence.v1","check_id":"rev2-mcp-types","command":"npm --prefix mcp-server run typecheck","cwd":"/home/user/av-kit","scope":"src + scripts (tsconfig.scripts.json)","phase":"static","exit_code":0,"result":"pass","tested_state":"1884a85 clean","output":"TYPECHECK_EXIT=0","fresh":true}
```
```json
{"schema_version":"evidence.v1","check_id":"rev2-mcp-build","command":"npm --prefix mcp-server run build","cwd":"/home/user/av-kit","scope":"dist/ for the fake-backend suite","phase":"static","exit_code":0,"result":"pass","tested_state":"1884a85 clean","output":"BUILD_EXIT=0","fresh":true}
```
```json
{"schema_version":"evidence.v1","check_id":"rev2-mcp-tests","command":"npm --prefix mcp-server test","cwd":"/home/user/av-kit","scope":"full MCP Vitest incl. tests/audit (110)","phase":"full","exit_code":0,"result":"pass","tested_state":"1884a85 clean","output":"Test Files 22 passed (22) | Tests 332 passed (332) | backend-spawn 1 (414ms) | run-cli 10 | transcript-oracle 11 | coverage 8 | runner-fake-backend 7 (3576ms, real dist/index.js over stdio) | Duration 5.74s","fresh":true}
```
```json
{"schema_version":"evidence.v1","check_id":"rev2-validate-task","command":"RECEIPTS_DIR=<scratchpad>/receipts/review2 bash docs/execution/plans/2026-10-01-mcp-live-audit/validate-task.sh {task-state,windows-gate-check,findings-check,scope b,docs,api-scope}","cwd":"/home/user/av-kit","scope":"H1 gates on the attempt-2 tree","phase":"static","exit_code":0,"result":"pass","tested_state":"1884a85","output":"PASS task-state: 12 rows done | PASS windows gate @ a044446f134fdb2849463b0c2f08be63d64d64f8: mcp_tests {'passed': 332, 'failed': 0, 'total': 332}; audit 68 actions, non-pass ['avkit_tts.cancel'] | PASS findings: 1 non-pass, all filed | PASS scope b: 63 changed paths, all allowed; PASS AC-68.2 | PASS green: 7 passed; PASS docs | PASS api-scope: no packages/ change vs 0e18fbd…; OpenAPI skip-with-basis","fresh":true}
```
```json
{"schema_version":"evidence.v1","check_id":"rev2-closeout-validator","command":"uv run python tools/validate_closeout_artifacts.py --handoff .agent/context/handoffs/2026-10-01-mcp-live-audit-MEU-68-handoff.md --plan docs/execution/plans/2026-10-01-mcp-live-audit/implementation-plan.md","cwd":"/home/user/av-kit","scope":"handoff structure + AC coverage","phase":"static","exit_code":0,"result":"pass","tested_state":"1884a85","output":"OK: required sections present; 18 AC row(s); 23 decision(s) logged; durable evidence present; plan_source binds; all 1 plan AC(s) present; no [B] rows | reviewer count: handoff AC-68.1…AC-68.18 = 18 distinct ids; plan rows 18","fresh":true}
```
```json
{"schema_version":"evidence.v1","check_id":"rev2-evidence-crosscheck","command":"python3 (reviewer script) over mcp-audit-summary.json, windows-gate-result.json, windows-gate-baseline.json, baseline-snapshot.json, report; npx tsx schemacheck.ts (runner validate()/parseBaseline)","cwd":"/home/user/av-kit","scope":"AC-68.4/5/6/7/9/13/14/15 attempt-2 evidence","phase":"targeted","exit_code":0,"result":"pass","tested_state":"0434895 files at 1884a85","output":"summary sha256 == result (193F8B9F…92EC) | mode authoritative, commit a044446 == tested_commit | 97 steps {pass 96, fail 1, skip_env 0, blocked 0}, 68 distinct actions, pass-without-observable [] | transcript.resume transcripts_done 1 last_item_status Done; transcript.compile 112681 B 1 section(s) transcripts_done 1; requeue/retry conflict 409 pass | 7 refusals isError=true changed=false | cleanup ok, root removed | discovery 8/68, 8 x schema_not_advertised | schema errors [] x3; parseBaseline OK x2; recorded_commit a044446 both | committed ⊖ gate = issue keys only (1 + 8), ids exist in known-issues.yaml | redaction: 0 token/bearer/cookie hits (10 UUIDs are job ids)","fresh":true}
```
```json
{"schema_version":"evidence.v1","check_id":"rev2-f2-probe","command":"npx tsx <scratchpad>/bl-probe/probe.mts (runAudit with fakeLauncher, discovery-only; missing path removed first)","cwd":"/home/user/av-kit/mcp-server","scope":"F2 recheck","phase":"targeted","exit_code":0,"result":"pass","tested_state":"1884a85","output":"baseline exists=false | container+update-baseline+missing: exit 4, launcher calls 0, deltas 0 | authoritative(win32)+update-baseline+missing: exit 4, file not created | control (no update): exit 4","fresh":true}
```
```json
{"schema_version":"evidence.v1","check_id":"rev2-f4-f3-census-probes","command":"scratch copy of validate-task.sh bound to scratch JSON (repo untouched); npx tsx f3probe.ts","cwd":"/home/user/av-kit","scope":"F4 worst-of, F3 assertion strength, census masking","phase":"targeted","exit_code":0,"result":"pass","tested_state":"1884a85; git status clean after","output":"F4: download.add.a fail → non-pass ['avkit_download.add','avkit_tts.cancel']; models.status fail → non-pass ['avkit_models.status','avkit_tts.cancel']; transcript.resume skip_env → FAIL skip_env not allowed | F3: committed {missing:[],extra:[]} 68/68; mutated copy {missing:['avkit_tts.voices'],extra:['avkit_tts.ghost']}; issue stripped → ['avkit_tts.cancel'] | census: auth+proof fail; container+proof skip_env; container no-probe fail; sections-mismatch+proof fail; resume-timeout+proof fail","fresh":true}
```

### Checklist deltas vs round 1

- **IR-4** pass: F2's single check replaced both former branches; F4 applied to the only census consumer in the gate; A11's `requeue.conflict` closes the requeue/retry asymmetry.
- **IR-5** pass with R2-1: `transcript-oracle.test.ts` 🟢 (exact `ok`/detail assertions on both branches, including the Skipped and sections-mismatch negatives; single-evaluation `poll` so the oracle decides on state, not waiting; census negatives incl. authoritative mode and a non-matching signature); `backend-spawn.test.ts` 🟢; `run-cli.test.ts` F2 test 🟢; `coverage.test.ts` committed-baseline test 🟢 when it runs, 🟡 as a whole because of the early return (R2-1).
- **IR-7(b)** pass: 18/18 AC ids present; AC-68.5 evidence cell corrected.
- **DR-1/DR-7** pass: walkthrough §Attempt 2 and handoff numbers (97/96/1/0/0, 332, 112,681 B, 1 section) all re-derived from the committed files.
- **DR-8** pass: D-18 now states the corrected cause ("pause landed before item 0"), replacing the round-1 hypothesis; D-19 documents S1 with the `CLEANUP_PREDICATE` precedent.

### Verdict

`approved` — F1, F2, F3, F4 and S1 are resolved in code and tests and proven live by the attempt-2 authoritative run (`a044446`, 97 steps, 96 pass, 0 skip_env, one filed `fail`); the restored transcript oracle is the plan's approved contract, not a weakening, and the new census member cannot mask an authoritative failure or a real container defect outside the IP-block branch. The one new finding (R2-1) is a weak-test pattern with no product false-pass, so under the Verdict Rule it is a correction note, not a blocker. F5 remains a one-line human ratification outside this reviewer's authority. Open after round 2: F5 (human), R2-1 (Medium, non-blocking).

**Residual risk statement.** Container-mode tolerance of the transcript compile rests on the product adapter raising `TranscriptRetryableError` (OOC-2); authoritative mode is unaffected. A deleted or relocated committed baseline is caught by the gate scripts and the runner, not by `npm test` (R2-1). The `tts.cancel` row stays a filed failure until `MCP-TTS-GENERATE-SYNCHRONOUS` is fixed, as D-14 records.

### Concrete follow-up actions

1. **R2-1** — one-line hard assertion in `coverage.test.ts:83`; take it with the next `GATED_PATHS` change rather than reopening `WINDOWS_GATE` for it alone (human decides).
2. **F5** — Mat ratifies D-14's "not MEU-62's surface" classification in `human-gate-decision.md` or the reflection.
3. Clerical (OOC-4) at H2: handoff `Changed Files` counts and AC-68.9/68.11 test citations.
4. H2 may proceed (`review-check` reads `verdict: "approved"`, round 2 ≤ cap 6). No further review round is required unless `GATED_PATHS` change again.

🕐 Completed: 2026-10-01 20:56 (UTC)

---

## Corrections Applied (2026-10-01, after round 2)

Applied by the implementer. The verdict is set to `corrections_applied`; only a reviewer pass may set `approved`.

| # | Finding | Fix Applied | Verification |
|---|---------|-------------|--------------|
| R2-1 | `coverage.test.ts` returns silently when the committed baseline is missing | `expect(existsSync(COMMITTED_BASELINE), COMMITTED_BASELINE).toBe(true)` replaces the early return | With the baseline file absent: the old test passed 8/8 and the new one fails (`AssertionError: …baseline-snapshot.json: expected false to be true`). The file was restored (byte-identical) and the test passes 8/8. |
| F5 | Stop-Condition literal trigger | Mat ratified D-14 verbatim: "Ratify D-14 (Recommended)" (`human-gate-decision.md` §F5) | Recorded |

**Gate impact.** The test is under `GATED_PATHS`. Mat chose "Fix now + attempt 3", so `WINDOWS_GATE` attempt 3 runs before the round-3 recheck (plan amendment A12).

**Added before attempt 3 (A13).** The `efeee3e` pregate first failed: `download.cancel` showed the container's YouTube wall as `HTTP Error 403: Forbidden`, outside the census signature, and the census refused it. The member now matches the 403. Its proof is the container host **and** a direct yt-dlp test fetch of `download_url_c` failing the same way (`run.ts` `mediaFetchBlocked`), which closes round-1 OOC-2's "host-only proof is weak". Tests: `transcript-oracle.test.ts` "AC-68.12 the download.cancel census member …" (Red: 1 assertion failure; Green: 334 total). Container-only; authoritative mode tolerates nothing.


---

## Recheck (2026-10-01) — Round 3

**Workflow**: `/execution-critical-review` recheck (round 3 of 6)
**Agent**: `claude-fable-5-1-subagent` (user-authorized, `human-review-decision.md`; did not author the work; wrote only this file)
**Tree**: branch `claude/sweet-goodall-mu69td`, HEAD `01f1cc9`, `git status` clean before and after (the one tracked file moved for a probe was restored byte-identical, `sha256sum -c` OK). Corrections `9e186da` (R2-1, A12) and `efeee3e` (A13); request `65bfa42` (walkthrough + this file only); attempt-3 result files `d9e2497`; findings/H1 re-run `01f1cc9`. `git diff --stat 65bfa42 HEAD -- mcp-server packages pyproject.toml uv.lock …/validate-task.ps1` is **empty** (`GATED_PATHS` unchanged since the tested commit; `windows-gate-check` enforces the same and passed).

### Intent re-anchor

Unchanged: the runner drives the built server over stdio against an isolated backend, passes each of the 68 actions only on an independent observable, holds all 7 refusals, cleans up, baselines and reports, with an authoritative Windows run. Round 3 asks whether the R2-1 fix and the A13 census change close their gaps without weakening any oracle, and whether the attempt-3 authoritative evidence still proves the intent. **Answer: yes** (`intent_achieved: yes`).

### Prior Pass Summary

| Finding | Prior Status | Recheck Result | Evidence |
|---|---|---|---|
| R2-1 — `coverage.test.ts` silent early return | open → corrections applied | ✅ **Resolved, no side effects.** | `coverage.test.ts:76` is now `expect(existsSync(COMMITTED_BASELINE), COMMITTED_BASELINE).toBe(true)`; the rest of the test is unchanged. Negative probe (baseline moved to the scratchpad, `npx vitest run tests/audit/coverage.test.ts`): 7 pass, **1 fail** — `AssertionError: /home/user/av-kit/.agent/skills/mcp-tool-audit/resources/baseline-snapshot.json: expected false to be true`; file restored byte-identical, tree clean. With the file present: 8/8 and the full suite 334/334. 🟢. |
| F5 — Stop Condition / D-14 | pending human | ✅ **Closed by the human.** | `human-gate-decision.md` §F5 records the question and the verbatim answer `Ratify D-14 (Recommended)` (`USER_EXPLICIT`, AskUserQuestion); handoff Decision Log `H-5` `chosen: "Ratify D-14 (Recommended)"`, `source_tag: Human-approved`, `human_message_reference` pointing at §F5 — verbatim match. Plan A12 records it. |
| Human decision on R2-1 | — | ✅ **Recorded consistently.** | `human-gate-decision.md` §R2-1 verbatim `Fix now + attempt 3`; handoff `H-6` `chosen: "Fix now + attempt 3"` with the same reference; plan A12 "Human: 'Fix now + attempt 3'"; `task.md` B-11 "Reopened (attempt 3) … Resolved (attempt 3)". |
| Round-1 OOC-2 — `download.cancel` host-only proof | residual | ✅ **Closed by A13** (analysed below). | `census.ts:33` `envProof: platform !== "win32" && networkProbe["avkit_download.cancel"] === false`; `run.ts:366-386` `mediaFetchBlocked`; `run.ts:565-569` gathers the probe only after a signature-matched `download.cancel` failure, container mode only. |
| Round-2 OOC-1/2/3 | residual | unchanged, still residual | Not re-litigated (Materiality Gate #4). |
| Round-2 OOC-4 (clerical) | open | partly corrected | Handoff `Changed Files` now says 97 steps / 112 tests and AC-68.9 / AC-68.11 cite the new tests. Still open: plan prose "67 actions" (`implementation-plan.md:25`, `:214`), see OOC below. |

### A13 analysis — can the widened signature or the new proof mask a defect?

- **What the signature matches.** `download.cancel`'s `error` is the job's own `error_message` when `dl_c` never reaches `Cancelled` (`plan.ts:841-843`: `c never Cancelled; REST c <status>` + `row.error_message`). So the signature can only match text the *backend* recorded for the media fetch. The MCP client renders API failures as `HTTP <status>` (`src/client.ts:32`), not `HTTP Error 403: Forbidden`, and no product source emits the latter string (`rg "HTTP Error"` over `mcp-server/src packages/*/src` → 0) — it is urllib's/yt-dlp's text. Probe: `wall.test("HTTP 403") === false`, `wall.test("c never Cancelled; REST c Downloading") === false`. A broken cancel against a *downloading* job therefore stays `fail` (the error carries no wall text); a cancel against a job the wall already failed is the only tolerated shape, and in that shape cancel's precondition is unreachable, so there is no defect to mask.
- **Proof is fail-closed** (real function, scratch copy of `scripts/audit` with `mediaFetchBlocked` exported and `REPO_ROOT` pinned to the repo — otherwise byte-identical, `diff` verified): local server **200** (fetch succeeds) → `false`; **404** (`HTTP Error 404: Not Found`, exit 3, no match) → `false`; **403** → `true`; `uv` removed from `PATH` (spawn `ENOENT`, `status null`) → `false`; `spawnSync` timeout semantics `status null, signal SIGTERM` → `status === 3` false → `false`. `false` ⇒ `probe[key] = true` ⇒ `envProof` false ⇒ the record stays `fail`.
- **`test: True` is bounded.** Installed yt-dlp 2026.07.04: `downloader/common.py:81 _TEST_FILE_SIZE = 10241`; `http.py:45-46,211-214` caps the range at that size; `fragment.py:361` keeps one fragment. Server log of the 200 case: the media request was `Range: bytes=0-10240`, **10,241 bytes served**, inside a `TemporaryDirectory`. No full download.
- **Tolerance matrix** (`applyTolerance`, real census): container+linux+probe `false` → `skip_env` `{member, signature_matched, env_proof: true}`; probe `true` (fetch works) → `fail`; probe absent / key undefined → `fail`; **win32** + proof → `fail`; **authoritative** + proof → `fail` (`env_proof` recorded true, verdict untouched); error = REST Downloading / `null` / `HTTP 403` → `fail` (`signature_matched: false`). `countedFailures`: steps `blocked` beneath a tolerated cancel are uncounted in container, **counted** in authoritative. Authoritative mode never gathers the probe (`run.ts:553` guard) and never tolerates (`classify.ts:203`).
- **Live, this container.** Direct `mediaFetchBlocked(download_url_c)` → `true` in 2.7 s with `ERROR: unable to download video data: HTTP Error 403: Forbidden` (egress proxy status: `selective: false`, no relay failures — the 403 is the remote's). Fresh `validate-task.sh audit-container` (real spawned backend, real `dist/index.js`, 97 steps): `download.cancel` → `skip_env` with `env_bound` all `true` (this time the bot-text form, proof still the direct fetch), its 9 dependants `blocked` beneath it and tolerated; `capture.capture` `skip_env`; `tts.cancel` filed `fail`. **The run then FAILed**: `transcript.add` → `fail` `{member: true, signature_matched: true, env_proof: false}` — the backend got the wall (`internal_error`) but the direct extract of the playlist succeeded 2.4 s later, so the per-URL proof refused it and `audit_container_assert` reported `FAIL: untolerated results [('avkit_transcript','add','fail')]`. That is the census doing exactly what AC-68.12 requires (no proof → no tolerance); it is recorded as R3-1 below because it makes the non-authoritative pregate flaky, not because anything false-passed.
- **New tests** (`transcript-oracle.test.ts:173-203`, 2 tests): 🟢 — exact `verdict` on both signature forms with proof, and four negatives (no proof, win32, authoritative, non-matching error). They do not exercise `mediaFetchBlocked` itself (a spawn wrapper; covered by the probes above and the container run).

### Attempt-3 authoritative evidence (fresh cross-check)

- `sha256(mcp-audit-summary.json)` = `26C3A3D6…1235` = `windows-gate-result.audit.summary_sha256`. Summary `mode authoritative`, `commit 65bfa42…` = `tested_commit`; stages in order, all exit 0 except `mcp-audit` exit 1; `mcp_tests 334/0/334`; `clean_tree true`; `quiet_machine_attested true` (the `-QuietMachineConfirmed` omission of attempt 2 is gone); `mcp_lockfile_sha256`, `uv_lock_sha256`, `agent_registry_sha256`, `agentic_framework_head` **identical to attempt 2**; `audit.steps 97`.
- Steps **97**, `{pass 96, fail 1, skip_env 0, blocked 0}`, **68** distinct actions, pass-without-observable = []. Non-pass: `tts.cancel` `confirmed_no_effect` only. 7 refusal records: `refusal_omit`/`refusal_false` all `isError:true, changed:false`; 6 confirmed `changed:true`, `tts.cancel` confirmed `changed:false`. Cleanup `{ok, residuals [], backend_exited, root_removed}`; isolation 6 keys under `…\Temp\avkit-mcp-audit-x0idfV\out`, `ok true`. Discovery 8/68, 8 × `schema_not_advertised`, 0 new/removed/ghost.
- Spot claims reproduced: `download.cancel` pass `REST c Cancelled, processor Idle` (1,613 ms); `transcript.resume` `transcripts_done 1, last_item_status Done`; `transcript.compile` `112681 B; 1 section(s)`; `download.get.done` 629,172 B; `tts.generate` MP3 60,044 B in 2,560 ms ("2.6 s"); `capture.capture` PNG 5,992,947 B; both `download_asset` steps pass.
- Committed baseline ⊖ gate copy: `strip(issue)(committed) == gate` → **True**; gate copy has no `issue` keys. 68 entries (67 pass, 1 fail); `recorded_commit 65bfa42` in both; annotations `avkit_tts.cancel → MCP-TTS-GENERATE-SYNCHRONOUS`, 8 findings → `MCP-TOOLS-LIST-EMPTY-INPUT-SCHEMA`; both ids present in `known-issues.yaml`. Deltas 68 × `NEW` (`--no-baseline`).
- Report header: commit `65bfa42…`, 8 / 68, exit 1; transcript row 19/19.
- Redaction: `bearer|x-api-token|cookie|mcp-token|authorization` over the five committed outputs → the only hits are the `download.cookies_test` action name; no token material.
- Handoff: 18/18 AC rows; `s28-windows-gate-run` / `-check` / `h1-verify` / `final-suite` evidence blocks match the files and the fresh re-runs; History row for round 3; Decision Log D-20, H-5, H-6 present and consistent with `human-gate-decision.md` (verbatim `chosen` strings). `meu-status.yaml` MEU-68 `ready_for_review`; `task.md` H1-6 `[/]`, 12 rows done.

### New findings

| # | Severity | Blocking | Kind | Finding | File:Line | Recommendation | Status |
|---|---|---|---|---|---|---|---|
| R3-1 | Low | no | verification-quality (container only) | **The non-authoritative container check is flaky under the per-moment YouTube wall, in the fail-closed direction.** A backend `internal_error` on `transcript.add`/`download.add.*` is tolerated only when the step's own URL also fails a direct extract; the wall is per request, so a direct re-probe that succeeds seconds later (observed: backend 500 at 22:18:56Z, direct extract OK ~2.4 s after) turns an environment block into `FAIL: untolerated results`, blocks the whole domain (26 `blocked` here) and fails `pregate`. No false pass — this is AC-68.12's contract working, and attempt-3's pregate on `efeee3e` happened to pass (84/97) — but each spurious FAIL costs a re-run and could tempt a future operator to loosen the proof. Authoritative mode unaffected (no probe, no tolerance). | `mcp-server/scripts/audit/run.ts:557-564` (per-URL extract probe); `census.ts:22-25,36-39` | Keep the proof per URL and fail-closed, but make it a *sample*, not a single shot: e.g. re-run `youtubeExtractWorks` up to 3× over ~10 s and treat "any attempt blocked" as proof (the wall is the thing being proven; a success among failures still shows it is per-moment), or compare against the backend's own adapter the way `captionFetchBlocked` does. Document in `/mcp-audit` that a container `pregate` FAIL on `transcript.add`/`download.add` with `env_proof:false` is to be re-run once before anything is changed. `run.ts` ∈ `GATED_PATHS`: take it with the next gated change, not now. | open |

### Out-of-Contract Observations (non-blocking, ≤ 3 bookkeeping)

1. Handoff AC-68.12 `Test(s)` cell cites `classify.test.ts; run-cli.test.ts`; the A13 census tests live in `transcript-oracle.test.ts:173-203` (an `AC-68.12` describe). Clerical.
2. Plan prose still says "67 actions" at `implementation-plan.md:25` and `:214` (AC-68.13); the report/tests/baseline say 68 (A7). Carried from rounds 1–2; clerical.
3. The committed `pregate-audit-summary.json` is the `9b38503` pregate (96 steps, pre-A9/A11/A13) and is labelled as such in the walkthrough; the `efeee3e` pregate (84/97) has no committed summary — its durable citation is the handoff's `s28-pregate-final` evidence block, which is what the workflow requires. Informational.

### Commands executed (fresh, this round)

```json
{"schema_version":"evidence.v1","check_id":"rev3-mcp-types","command":"npm --prefix mcp-server run typecheck","cwd":"/home/user/av-kit","scope":"src + scripts (tsconfig.scripts.json)","phase":"static","exit_code":0,"result":"pass","tested_state":"01f1cc9 clean","output":"tsc --noEmit && tsc -p tsconfig.scripts.json | TYPECHECK_EXIT=0","fresh":true}
```
```json
{"schema_version":"evidence.v1","check_id":"rev3-mcp-build","command":"npm --prefix mcp-server run build","cwd":"/home/user/av-kit","scope":"dist/ for the fake-backend suite and the container run","phase":"static","exit_code":0,"result":"pass","tested_state":"01f1cc9 clean","output":"BUILD_EXIT=0","fresh":true}
```
```json
{"schema_version":"evidence.v1","check_id":"rev3-mcp-tests","command":"npm --prefix mcp-server test","cwd":"/home/user/av-kit","scope":"full MCP Vitest incl. tests/audit (112)","phase":"full","exit_code":0,"result":"pass","tested_state":"01f1cc9 clean","output":"Test Files 22 passed (22) | Tests 334 passed (334) | transcript-oracle 13 | coverage 8 | run-cli 10 | backend-spawn 1 (417ms) | runner-fake-backend 7 (3841ms, real dist/index.js over stdio) | Duration 6.35s","fresh":true}
```
```json
{"schema_version":"evidence.v1","check_id":"rev3-validate-task","command":"RECEIPTS_DIR=<scratchpad>/receipts/review3 bash docs/execution/plans/2026-10-01-mcp-live-audit/validate-task.sh {task-state,windows-gate-check,findings-check,scope b,docs,api-scope}","cwd":"/home/user/av-kit","scope":"H1 gates on the attempt-3 tree","phase":"static","exit_code":0,"result":"pass","tested_state":"01f1cc9","output":"PASS task-state: 12 rows done | PASS windows gate @ 65bfa42605a253a46eca92881777c6901da88c98: mcp_tests {'passed': 334, 'failed': 0, 'total': 334}; audit 68 actions, non-pass ['avkit_tts.cancel'] | PASS findings: 1 non-pass, all filed | PASS scope b: 63 changed paths, all allowed; PASS AC-68.2 | PASS green: 7 passed; PASS docs | PASS api-scope: no packages/ change vs 0e18fbd…; OpenAPI skip-with-basis | review-check on the pre-round-3 file: FAIL: verdict corrections_applied (expected before this append)","fresh":true}
```
```json
{"schema_version":"evidence.v1","check_id":"rev3-closeout-validator","command":"uv run python tools/validate_closeout_artifacts.py --handoff .agent/context/handoffs/2026-10-01-mcp-live-audit-MEU-68-handoff.md --plan docs/execution/plans/2026-10-01-mcp-live-audit/implementation-plan.md (and --ac-coverage-only)","cwd":"/home/user/av-kit","scope":"handoff structure + AC coverage","phase":"static","exit_code":0,"result":"pass","tested_state":"01f1cc9","output":"OK: required sections present; 18 AC row(s); 26 decision(s) logged; durable evidence present; plan_source binds; all 1 plan AC(s) present; no [B] rows | OK: all 1 plan AC(s) present | reviewer count: 18 distinct AC-68.x ids in the handoff table","fresh":true}
```
```json
{"schema_version":"evidence.v1","check_id":"rev3-r2-1-negative","command":"mv baseline-snapshot.json <scratchpad>; (cd mcp-server && npx vitest run tests/audit/coverage.test.ts); mv back; git checkout -- <file>; sha256sum -c; git status --short","cwd":"/home/user/av-kit","scope":"R2-1 fix strength","phase":"targeted","exit_code":0,"result":"pass (fails when the file is absent, as required)","tested_state":"01f1cc9; tree clean after","output":"baseline absent: yes | 7 ✓, 1 × 'AC-68.5 the committed baseline's entries equal AUDIT_ACTION_SET …' → AssertionError: /home/user/av-kit/.agent/skills/mcp-tool-audit/resources/baseline-snapshot.json: expected false to be true | restored: sha256 OK | STATUS_LINES=0","fresh":true}
```
```json
{"schema_version":"evidence.v1","check_id":"rev3-a13-probes","command":"npx tsx <scratchpad>/a13probe/probe.mts (scratch copy of scripts/audit with mediaFetchBlocked exported; local HTTP server for 200/404/403; real census + applyTolerance + countedFailures)","cwd":"<scratchpad>/a13probe","scope":"A13 fail-closed proof, test-mode bound, tolerance matrix","phase":"targeted","exit_code":0,"result":"pass","tested_state":"01f1cc9 (copy byte-identical apart from the export and REPO_ROOT pin)","output":"local 200 → false (1691 ms; server log: Range bytes=0-10240, served=10241) | 404 → false | 403 → true | uv missing from PATH → false | spawnSync timeout → status null / SIGTERM → false | sig vs 'HTTP 403' false, vs 'REST c Downloading' false | matrix: container+linux+proof skip_env; probe true fail; probe absent fail; win32 fail; authoritative fail; non-matching error fail | counted beneath tolerated cancel: container [] / authoritative ['download.cancel','download.reset']","fresh":true}
```
```json
{"schema_version":"evidence.v1","check_id":"rev3-a13-live","command":"uv run python -c <mediaFetchBlocked snippet verbatim> https://www.youtube.com/watch?v=aqz-KE-bpKQ; RECEIPTS_DIR=<scratchpad>/receipts/review3-container bash validate-task.sh audit-container","cwd":"/home/user/av-kit","scope":"A13 in this container, end to end (real spawned backend, real dist/index.js, 97 steps)","phase":"targeted","exit_code":1,"result":"fail-closed as designed (see R3-1)","tested_state":"01f1cc9","output":"direct fetch: DownloadError 'ERROR: unable to download video data: HTTP Error 403: Forbidden' in 2.7 s | mcp-audit container: 67/97 pass, 8 discovery finding(s), cleanup ok, exit 1 | download.cancel skip_env {member,signature_matched,env_proof: true} (+9 blocked beneath, tolerated); capture.capture skip_env; tts.cancel fail confirmed_no_effect (filed) | transcript.add fail {member:true, signature_matched:true, env_proof:false} (+26 blocked) → FAIL: untolerated results [('avkit_transcript','add','fail')] | cleanup {ok, residuals [], backend_exited, root_removed}","fresh":true}
```
```json
{"schema_version":"evidence.v1","check_id":"rev3-evidence-crosscheck","command":"python3 (reviewer script) over windows-gate-result.json, mcp-audit-summary.json, windows-gate-baseline.json, baseline-snapshot.json, report, known-issues.yaml; git diff --stat 65bfa42 HEAD -- <GATED_PATHS>; git show 0434895:windows-gate-result.json (hash identity)","cwd":"/home/user/av-kit","scope":"AC-68.4/5/6/7/9/13/14/15 attempt-3 evidence","phase":"targeted","exit_code":0,"result":"pass","tested_state":"d9e2497/01f1cc9 files at 01f1cc9","output":"summary sha256 == result (26C3A3D6…1235) | mode authoritative, commit 65bfa42 == tested_commit | 97 steps {96,1,0,0}, 68 actions, pass-without-observable [] | 7 refusals isError=true changed=false | cleanup ok | discovery 8/68 | committed strip(issue) == gate True; gate has no issue keys; recorded_commit 65bfa42 both; 68 entries 67 pass / 1 fail; issue ids exist | deltas 68 × NEW | preflight hashes identical to attempt 2 | GATED_PATHS diff 65bfa42..HEAD empty | redaction: hits are the download.cookies_test action name only","fresh":true}
```

### Checklist deltas vs round 2

- **IR-4** pass: A13 applies the per-URL proof pattern of A9 to the one remaining host-only member; no other member is host-only except `capture.capture`, whose proof is the platform itself (the capture adapter is Windows-only, `adapter.py:113`), which is the right proof for that member.
- **IR-5** pass (no 🔴, no 🟡 left): `coverage.test.ts` 🟢 end to end (R2-1 closed); `transcript-oracle.test.ts` A13 tests 🟢.
- **IR-6/IR-7** unchanged pass; 18/18 AC ids; no deferred rows added.
- **DR-1/DR-7** pass: walkthrough §Attempt 3 and handoff numbers (97/96/1/0/0, 334, 112,681 B, 1,613 ms, 2.6 s) re-derived from the committed files; `GATED_PATHS` unchanged since `65bfa42`.
- **DR-8** pass: the handoff's residual list (five filed issues) is intact; R3-1 is a container-check property, not a product gap, and does not change "all 18 ACs ✅".

### Verdict

`approved` — R2-1 is closed by a hard assertion whose failure was reproduced with the file absent; F5 is ratified by the human verbatim and recorded consistently in all four places; A13 widens the `download.cancel` signature only to text the backend records for the media fetch, binds tolerance to the container host **and** a direct per-URL reproduction, is fail-closed on a successful fetch, another error, a probe crash and a timeout, reads at most 10,241 bytes of media, and is inert in authoritative mode — all verified on the real function and live in this container; the attempt-3 authoritative run (`65bfa42`, 97 steps, 96 pass, 0 skip_env, one filed `fail`, `download.cancel` passed live) re-derives from the committed files with the summary hash bound to the gate result and the baseline differing from the gate copy by `issue` keys only. The one new item (R3-1) is a Low, non-blocking property of the non-authoritative container check that fails in the safe direction; under the Verdict Rule it is a correction note. Open after round 3: **R3-1 (Low)**. `review-check` may read this file as `approved`, round 3 ≤ cap 6; no `GATED_PATHS` change is required by this round, so no `WINDOWS_GATE` attempt 4 is needed.

**Residual risk statement.** Container-mode tolerance rests on three per-URL/per-adapter reproductions of an intermittent wall (download add, transcript add, transcript compile, download cancel); each can refuse a genuine block when the wall lifts between the backend's call and the probe (R3-1), never the reverse. Authoritative mode tolerates nothing. `tts.cancel` stays a filed failure until `MCP-TTS-GENERATE-SYNCHRONOUS` is fixed (D-14, ratified H-5).

### Concrete follow-up actions

1. **R3-1** — sample the per-URL extract probe (≤ 3 attempts) or route it through the product adapter; add the "re-run once on `env_proof:false`" note to `/mcp-audit`. `run.ts` ∈ `GATED_PATHS`: batch with the next gated change.
2. Clerical at H2 (OOC 1–2): handoff AC-68.12 test citation; plan "67 actions" at `implementation-plan.md:25,214`.
3. H2 may proceed. No further review round is required unless `GATED_PATHS` change again.

🕐 Completed: 2026-10-01 22:19 (UTC)
