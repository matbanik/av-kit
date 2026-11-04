---
date: "2026-10-27"
review_mode: "execution"
target_plan: "docs/execution/plans/2026-10-26-tts-sideload-load/implementation-plan.md"
loop_id: "s42-execution-2026-10-26-tts-sideload-load"
round: 1
verdict: "approved"
findings_count: 0
blocking_findings_count: 0
template_version: "2.2"
requested_verbosity: "standard"
agent: "codex-independent-reviewer"
intent_achieved: "yes"
---

# Critical Review: tts-sideload-load

> **Review Mode:** execution, round 1
> **Verdict:** approved; no blocking findings.

Confirm Session 42's delivered code records a sideloaded model file so a variant listed as downloaded loads from that file, logs every load failure as tts.load_failed, and swaps the spaCy sys.path entry when tts.models_directory changes, with honest Red/Green and gate evidence.

## Scope

Reviewed the MEU-98 handoff, implementation-plan.md, task.md and walkthrough.md; the three product and four test diffs on main above c34866b; relevant repository/UoW, routes, schemas, MCP callers, readiness wiring and fixtures; build-plan/state changes; and Red/Green/full-gate receipts. Checklists applied: IR-1 through IR-7, AV-1 through AV-6, and DR claim verification.

Plan-review round 2 approval, D-132 and the accepted row-10 dependency block are given facts. D-133/ECN-2 and ECN-3 were checked. H2 is the implementer's post-review work. Only this review file was written in the repository. The session gate and full suite were not rerun.

## Findings

No critical or blocking findings. No substantive nonblocking defect was established.

| # | Severity | Blocking | Kind | Finding | File:Line | Recommendation | Status |
|---|----------|----------|------|---------|-----------|----------------|--------|

## Checklist Results

### Information Retrieval / Implementation Review

| Check | Result | Observation |
|-------|--------|-------------|
| IR-1 runtime / contract | pass | AC-98.6 uses production build_services, create_app, routes, ModelService, catalog and SQLite. Engines/network downloads are the declared fakes; no service dependency override. Independent permitted run passed 178 tests. |
| IR-2 collaborator compliance | pass | FakeModelRepo updates the row returned by get; explicit commit counting matches RECORD_RULE. Real SQLite verifies the recorded path and file size. |
| IR-3 errors | pass | NotFoundError remains 404, ConflictError 409, ModelLoadError/ValidationError 422. Removed-file contract checks the real route's 422 message; existing device/error tests remain green. |
| IR-4 generalization | pass | Both list and load record; all four newly logged branches and every existing _log_load_failed caller were inspected. |
| IR-5 test rigor | pass | Grading below. No Weak changed test identified. |
| IR-6 boundaries | pass | No new payload/schema. Existing strict ApiModel and MCP strict objects preserve variant/device validation. |
| IR-7 coverage / deferrals | pass | AC-98.1–.10 appear in the handoff; integration ACs have real adapter/composition tests. B-10 is the accepted dependency outcome with durable evidence and follow-up. |
| AV-1 | pass | Raw Red receipts exit 1 with 4, 7 and 2 assertion failures on persistence, logging and stale readiness respectively; no setup/collection failure substitutes for a Red. |
| AV-2 / AV-3 / AV-4 | pass | No assertion bypass or new skip/xfail masking. Assertions check persisted values, engine paths, event tuples/counts and path/readiness transitions. |
| AV-5 / AV-6 | pass | Completed code has no new placeholder. Added behavior traces to the approved FIC/spec/local canon. |

### Runtime and caller verification

**Sideload record.** packages/core/src/avkit_core/services/models.py:108 and :135 call _record_sideload before reading the rows; :159 records only existing ids with a scanned path. The equality guard prevents mark_downloaded and the explicit commit when already downloaded at that path; the batch commits once if any row changed. The catalog performs the filesystem scan; no new filesystem I/O enters core. The unchanged repository at packages/infrastructure/src/avkit_infra/database/repositories.py:365 records size. tests/integration/test_tts_assets.py:990 proves GET downloaded → POST load uses the dropped file, then deletion produces the existing 422 and exactly one failure event.

MCP's available/downloaded actions still call the same GET routes (mcp-server/src/toolsets/registry.ts:98); status uses get_status without scanning. A first list may persist catalog discovery, as explicitly approved in D-123/RECORD_RULE. It requires the application's existing writable database; no distinct supported read-only repository caller was found. SqlAlchemyUnitOfWork's automatic commit on clean exit is unchanged: the plan's idempotence counts explicit service commits. tests/unit/test_uow_commit_log.py checks suppression of a debug console event, not a prohibition on commits; it passes unchanged. Unknown scanned ids remain display-only and load raises NotFoundError; legacy/vocab conflict tests pass.

**Load failures.** packages/infrastructure/src/avkit_infra/tts/adapter.py:123 unwraps the immediate cause only for ModelLoadError. The weight check at :253 logs cpu and re-raises the same error; unsupported format at :270 logs the resolved target and preserves ValidationError/message. _load_pytorch at :292 logs torch absence and kokoro ImportError exactly once; existing probe/constructor/move/eval/ONNX failures retain their one-event ownership. No outer catch double-logs those branches. LOG_CAUSE was checked against each caller, including raw failures with and without causes. Success logs no tts.load_failed.

**spaCy swap.** packages/infrastructure/src/avkit_infra/tts/assets.py:125 removes only names in its tracked set, and only when not current, under the same lock used for appends/set updates. Existing untracked entries are neither adopted nor removed. Repeated calls append nothing; switching to an empty folder removes old owned paths and makes Dependencies missing. Returning to the install reports ready with one entry. The directory-existence snapshot is computed before acquiring the lock; tracked-set/sys.path mutation is serialized. No concrete contract-breaking race was established within the declared behavior. Already-imported model objects remain cached as the plan explicitly allows.

### IR-5 grading of changed tests

| Tests / locations | Grade | Reason |
|-------------------|-------|--------|
| test_services.py:2257 AC-98.1 list; :2297 AC-98.2 load; :2385 AC-98.3 changed path; :2402 same path | Strong | Exact row/path/downloaded state, port arguments, mark_downloaded calls and explicit commit deltas; repeat-list/load idempotence. |
| test_services.py:2315 side-only id; :2326 vocab/no-scan; :2345 and :2368 legacy branches | Strong | Explicit domain exception/no-port assertions, persisted-path checks, and successful repair where a current file exists. The narrow legacy exception capture ends in an assertion; it cannot swallow an arbitrary failure. |
| test_services.py:2291 no-file-I/O guard | Adequate | Lexical architecture guard checks specified forbidden spellings. Direct source review also confirms the boundary; this is not the behavioral persistence proof. |
| test_tts_device_resolution.py:657 TA-1 | Strong | Prior cause/engine/path/unloaded assertions preserved. Adds exact one-event tuple for PermissionError/cpu, without replacing the adapter's weight check. |
| test_tts_device_resolution.py:809 AC-98.4, :828/.844 AC-98.5 runtime/import, :861 format, :877 success | Strong | Exact exception types/messages/causes, event tuples, no engine construction and unloaded status; success has zero failure events. |
| Unsupported-format frozen-instance setup, :869 | Sound fault injection | object.__setattr__ changes only one instance after valid construction, reaching an otherwise defensive branch. Domain validation and the adapter are not patched. Red reaches the missing-log assertion, not a construction error. |
| test_tts_assets.py:990 AC-98.6 | Strong | Real route/service/SQLite round-trip, exact engine path, persisted size/path, removed-file 422 and one log. |
| test_tts_assets.py:1043/.1066 AC-98.8; :1084 AC-98.9 | Strong | A→B→B→empty and ready→missing→ready; exact absence/order/count checks, including a pre-existing entry equal to A's install path. |
| _reset_tracked_spacy_entries, test_tts_assets.py:1037 | Sound isolation | Replaces/restores ownership bookkeeping via monkeypatch; does not replace activation/readiness or their output. New behavior itself adds and tracks A during the test. Red raising=False→Green strict name lookup is a documented fixture repair, not an expectation amendment. |
| test_tts_models.py:853 AC-98.7 | Strong invariant | Exact equality between scan catalog ids and seed ids; correctly identified as a guard that already passes at Red. |

The existing affected legacy, device-fallback, spaCy ordering/isolation, SQLite and commit-log tests were inspected and passed in the same targeted run. The lock covers mutations of the tracked set. The set tolerates fixture-restored missing sys.path entries; new tests isolate their own ownership set, and background download cleanup completes before fixture teardown. No fresh concurrency stress test is claimed.

### Design Review / Claim Verification

The handoff's file/function/line claims match the diff. The 03-service-layer.md delivered note and its new rule rows describe the actual implementation. MEU-98 is ready_for_review, not prematurely approved; issue resolutions/reflection/metrics follow this verdict. No hidden required implementation was deferred.

D-133/ECN-2 correctly places B-10 where the task validator reads it, preserving the accepted missing-dependency outcome and follow-up. ECN-3 supplies RECEIPTS_DIR in the runner without changing gate predicates. The task validator independently passed with that environment.

### Post-Implementation Review / Gate Evidence

Static reviewer checks passed before targeted tests: Pyright 0 errors/warnings/informations; Ruff all checks passed. Targeted pytest: **178 passed, 1 warning**, exit 0. Handoff validator: 16 AC rows, 2 decisions and all 8 plan AC families. Task validator: 27 rows, 25 command rows checked and two view_file exemptions.

The H1-2 receipt records py-tests **1 failed, 956 passed**; its sole failure is baseline AC-25.7. All remaining gate steps passed, and before/after identity matched. Current raw identity is c34866b116405dcbc2c70e482b5b376e017d5784+ba6f9983b9689676b9acd333bcae12224d77c74d7f55823925979921b4319fce. Omitting only .claude/settings.local.json in a read-only in-memory recomputation yields **c34866b116405dcbc2c70e482b5b376e017d5784+bd4e38d544c2659a719a44abf88831db23b2cfea1396173ff26d5cb7cf8e2c29**, exactly H1-2. This reconciles the local CLI settings addition; it does not assert that the raw fingerprints are equal. The local settings contents were not disclosed. No source/runtime input difference remains in that comparison.

The default uv cache was inaccessible in the reviewer sandbox (exit 2 before checks ran). Successful runs used UV_CACHE_DIR=C:/Temp/av-kit/uv-review-cache and UV_NO_SYNC=1. Bytecode was disabled; Ruff cache and pytest basetemp were under scratch, with pytest's cache provider disabled. Each command's exit was captured before reading its completed receipt.

### Durable reviewer evidence

```json
{"schema_version":"evidence.v1","check_id":"s42-review-1","command":"rtk proxy uv run pytest tests/unit/test_services.py tests/integration/test_tts_device_resolution.py tests/integration/test_tts_assets.py tests/integration/test_tts_models.py tests/integration/test_tts_voice_packs.py tests/integration/test_sqlite_uow.py tests/unit/test_uow_commit_log.py -q","cwd":"P:/av-kit","scope":"Independent targeted tests","phase":"targeted","exit_code":0,"result":"pass","tested_state":"c34866b116405dcbc2c70e482b5b376e017d5784+ba6f9983b9689676b9acd333bcae12224d77c74d7f55823925979921b4319fce","output":"178 passed, 1 Starlette/httpx deprecation warning in 8.67s. Production route/service/SQLite contract tests passed. UV_NO_SYNC=1; uv cache, pytest basetemp and receipts under C:/Temp/av-kit; bytecode and pytest cache disabled.","fresh":true}
```

```json
{"schema_version":"evidence.v1","check_id":"s42-review-2","command":"rtk proxy uv run pyright packages","cwd":"P:/av-kit","scope":"Pyright","phase":"static","exit_code":0,"result":"pass","tested_state":"c34866b116405dcbc2c70e482b5b376e017d5784+ba6f9983b9689676b9acd333bcae12224d77c74d7f55823925979921b4319fce","output":"0 errors, 0 warnings, 0 informations. Scratch uv cache and UV_NO_SYNC=1 used after the sandbox denied the default cache.","fresh":true}
```

```json
{"schema_version":"evidence.v1","check_id":"s42-review-3","command":"rtk proxy uv run ruff check packages tests","cwd":"P:/av-kit","scope":"Ruff","phase":"static","exit_code":0,"result":"pass","tested_state":"c34866b116405dcbc2c70e482b5b376e017d5784+ba6f9983b9689676b9acd333bcae12224d77c74d7f55823925979921b4319fce","output":"All checks passed. Scratch uv/Ruff caches and UV_NO_SYNC=1 used.","fresh":true}
```

```json
{"schema_version":"evidence.v1","check_id":"s42-review-4","command":"rtk proxy uv run python tools/validate_closeout_artifacts.py --handoff .agent/context/handoffs/2026-10-26-tts-sideload-load-MEU-98-handoff.md --plan docs/execution/plans/2026-10-26-tts-sideload-load/implementation-plan.md","cwd":"P:/av-kit","scope":"Handoff and plan binding","phase":"static","exit_code":0,"result":"pass","tested_state":"c34866b116405dcbc2c70e482b5b376e017d5784+ba6f9983b9689676b9acd333bcae12224d77c74d7f55823925979921b4319fce","output":"Required sections, 16 AC rows, 2 decisions, durable evidence and plan binding pass; all 8 plan AC families present. Individual AC-98.1 through AC-98.10 also manually checked.","fresh":true}
```

```json
{"schema_version":"evidence.v1","check_id":"s42-review-5","command":"rtk proxy uv run python tools/lint_task_contract.py --task docs/execution/plans/2026-10-26-tts-sideload-load/task.md --allowed-builder-classes avkit_builder,avkit_coordinator,avkit_verifier","cwd":"P:/av-kit","scope":"Task contract and B-10","phase":"static","exit_code":0,"result":"pass","tested_state":"c34866b116405dcbc2c70e482b5b376e017d5784+ba6f9983b9689676b9acd333bcae12224d77c74d7f55823925979921b4319fce","output":"RECEIPTS_DIR=C:/Temp/av-kit. 27 rows; 25 fully checked command rows; two view_file exemptions; dependencies resolve and are acyclic. D-133/ECN-2 preserve the accepted eSpeak block in task.md; ECN-3 supplies the required receipts environment.","fresh":true}
```

```json
{"schema_version":"evidence.v1","check_id":"s42-review-6","procedure":"Compare the three product diffs, changed tests, repository/UoW, REST mappings and MCP callers against every AC; inspect all three Red receipts and their preserved exit files, then compare with the independent targeted run.","observer":"codex-independent-reviewer","cwd":"P:/av-kit","scope":"Runtime contracts, callers and IR-5 test rigor","phase":"targeted","exit_code":null,"result":"pass","tested_state":"c34866b116405dcbc2c70e482b5b376e017d5784+ba6f9983b9689676b9acd333bcae12224d77c74d7f55823925979921b4319fce","output":"Sideload persistence and explicit-commit idempotence, display-only ids, legacy/vocab conflicts, exactly-one failure logging with device/cause, and spaCy ownership/swap behavior match the contract. Changed behavioral tests are Strong; the lexical no-I/O guard is Adequate. TA-1 preserves prior assertions; the frozen-instance test reaches the defensive format branch; tracked-set monkeypatching isolates state without replacing activation/readiness. Reds exit 1: 4/7/2 assertion failures for the stated defects, without setup failures.","fresh":true}
```

```json
{"schema_version":"evidence.v1","check_id":"s42-review-7","procedure":"Inspect s42-gate-h1.txt and the D6/Red receipts; compute identity.py --state-only, then recompute read-only with only .claude/settings.local.json excluded in memory and compare the entire digest.","observer":"codex-independent-reviewer","cwd":"P:/av-kit","scope":"Recorded fresh full gate and current input identity","phase":"targeted","exit_code":null,"result":"pass","tested_state":"c34866b116405dcbc2c70e482b5b376e017d5784+ba6f9983b9689676b9acd333bcae12224d77c74d7f55823925979921b4319fce","output":"Current raw state ends ba6f9983b9689676b9acd333bcae12224d77c74d7f55823925979921b4319fce. Omitting only local CLI settings reproduces bd4e38d544c2659a719a44abf88831db23b2cfea1396173ff26d5cb7cf8e2c29 exactly, matching H1-2 before/after. Recorded Python result: 1 failed, 956 passed; only baseline AC-25.7 is excused; remaining gate stages passed. No gate/full-suite rerun.","fresh":true}
```

```json
{"schema_version":"evidence.v1","check_id":"s42-review-8","procedure":"Read task.md B-10, the handoff evidence, known-issues.yaml diff and pending H1/H2 task rows against grouping D-100 and the user's given rulings.","observer":"codex-independent-reviewer","cwd":"P:/av-kit","scope":"eSpeak evidence stage and review boundary","phase":"targeted","exit_code":null,"result":"pass","tested_state":"c34866b116405dcbc2c70e482b5b376e017d5784+ba6f9983b9689676b9acd333bcae12224d77c74d7f55823925979921b4319fce","output":"Production probe evidence records exit 3 and 'espeak-ng: <absent> version: -'; AC-74.11 was not run and TTS-ESPEAK-LIVE-PATH-UNVERIFIED remains open. H2 reflection, metrics, resolutions and approved status appropriately follow independent review.","fresh":true}
```

## Verdict

**approved** — intent achieved with no blocking finding. eSpeak NG remains absent under the accepted B-10 outcome; AC-74.11 is not certified. This approval covers the delivered implementation; H2 closeout is still the implementer's next work. No full-suite, session-gate, live model-inference or Electron rerun is claimed.

## Structured Verdict

```json
{
  "schema_version": "review-verdict.v2",
  "date": "2026-10-27",
  "review_mode": "execution",
  "loop_id": "s42-execution-2026-10-26-tts-sideload-load",
  "round": 1,
  "target_plan": "docs/execution/plans/2026-10-26-tts-sideload-load/implementation-plan.md",
  "agent": "codex-independent-reviewer",
  "requested_verbosity": "standard",
  "verdict": "approved",
  "summary": "Intent achieved; no blocking findings. All 178 targeted tests, Pyright, Ruff, and both artifact validators passed. Red receipts support the claimed defects. Full-gate evidence was inspected and its identity reconciled; the full suite was not rerun. The accepted eSpeak dependency block remains open, and H2 closeout follows this verdict.",
  "intent_anchor": "Confirm Session 42's delivered code records a sideloaded model file so a variant listed as downloaded loads from that file, logs every load failure as tts.load_failed, and swaps the spaCy sys.path entry when tts.models_directory changes, with honest Red/Green and gate evidence.",
  "intent_achieved": "yes",
  "findings": [],
  "checklist_results": [
    {
      "check": "Independent targeted tests",
      "result": "pass",
      "command": "rtk proxy uv run pytest tests/unit/test_services.py tests/integration/test_tts_device_resolution.py tests/integration/test_tts_assets.py tests/integration/test_tts_models.py tests/integration/test_tts_voice_packs.py tests/integration/test_sqlite_uow.py tests/unit/test_uow_commit_log.py -q",
      "exit_code": 0,
      "evidence": "178 passed, 1 Starlette/httpx deprecation warning in 8.67s. Production route/service/SQLite contract tests passed. UV_NO_SYNC=1; uv cache, pytest basetemp and receipts under C:/Temp/av-kit; bytecode and pytest cache disabled."
    },
    {
      "check": "Pyright",
      "result": "pass",
      "command": "rtk proxy uv run pyright packages",
      "exit_code": 0,
      "evidence": "0 errors, 0 warnings, 0 informations. Scratch uv cache and UV_NO_SYNC=1 used after the sandbox denied the default cache."
    },
    {
      "check": "Ruff",
      "result": "pass",
      "command": "rtk proxy uv run ruff check packages tests",
      "exit_code": 0,
      "evidence": "All checks passed. Scratch uv/Ruff caches and UV_NO_SYNC=1 used."
    },
    {
      "check": "Handoff and plan binding",
      "result": "pass",
      "command": "rtk proxy uv run python tools/validate_closeout_artifacts.py --handoff .agent/context/handoffs/2026-10-26-tts-sideload-load-MEU-98-handoff.md --plan docs/execution/plans/2026-10-26-tts-sideload-load/implementation-plan.md",
      "exit_code": 0,
      "evidence": "Required sections, 16 AC rows, 2 decisions, durable evidence and plan binding pass; all 8 plan AC families present. Individual AC-98.1 through AC-98.10 also manually checked."
    },
    {
      "check": "Task contract and B-10",
      "result": "pass",
      "command": "rtk proxy uv run python tools/lint_task_contract.py --task docs/execution/plans/2026-10-26-tts-sideload-load/task.md --allowed-builder-classes avkit_builder,avkit_coordinator,avkit_verifier",
      "exit_code": 0,
      "evidence": "RECEIPTS_DIR=C:/Temp/av-kit. 27 rows; 25 fully checked command rows; two view_file exemptions; dependencies resolve and are acyclic. D-133/ECN-2 preserve the accepted eSpeak block in task.md; ECN-3 supplies the required receipts environment."
    },
    {
      "check": "Runtime contracts, callers and IR-5 test rigor",
      "result": "pass",
      "procedure": "Compare the three product diffs, changed tests, repository/UoW, REST mappings and MCP callers against every AC; inspect all three Red receipts and their preserved exit files, then compare with the independent targeted run.",
      "observer": "codex-independent-reviewer",
      "exit_code": null,
      "evidence": "Sideload persistence and explicit-commit idempotence, display-only ids, legacy/vocab conflicts, exactly-one failure logging with device/cause, and spaCy ownership/swap behavior match the contract. Changed behavioral tests are Strong; the lexical no-I/O guard is Adequate. TA-1 preserves prior assertions; the frozen-instance test reaches the defensive format branch; tracked-set monkeypatching isolates state without replacing activation/readiness. Reds exit 1: 4/7/2 assertion failures for the stated defects, without setup failures."
    },
    {
      "check": "Recorded fresh full gate and current input identity",
      "result": "pass",
      "procedure": "Inspect s42-gate-h1.txt and the D6/Red receipts; compute identity.py --state-only, then recompute read-only with only .claude/settings.local.json excluded in memory and compare the entire digest.",
      "observer": "codex-independent-reviewer",
      "exit_code": null,
      "evidence": "Current raw state ends ba6f9983b9689676b9acd333bcae12224d77c74d7f55823925979921b4319fce. Omitting only local CLI settings reproduces bd4e38d544c2659a719a44abf88831db23b2cfea1396173ff26d5cb7cf8e2c29 exactly, matching H1-2 before/after. Recorded Python result: 1 failed, 956 passed; only baseline AC-25.7 is excused; remaining gate stages passed. No gate/full-suite rerun."
    },
    {
      "check": "eSpeak evidence stage and review boundary",
      "result": "pass",
      "procedure": "Read task.md B-10, the handoff evidence, known-issues.yaml diff and pending H1/H2 task rows against grouping D-100 and the user's given rulings.",
      "observer": "codex-independent-reviewer",
      "exit_code": null,
      "evidence": "Production probe evidence records exit 3 and 'espeak-ng: <absent> version: -'; AC-74.11 was not run and TTS-ESPEAK-LIVE-PATH-UNVERIFIED remains open. H2 reflection, metrics, resolutions and approved status appropriately follow independent review."
    }
  ]
}
```

