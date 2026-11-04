---
date: "2026-10-26"
review_mode: "plan"
target_plan: "docs/execution/plans/2026-10-26-tts-sideload-load/implementation-plan.md"
verdict: "approved"
findings_count: 1
template_version: "2.2"
requested_verbosity: "standard"
agent: "codex-independent-reviewer"
loop_id: "s42-plan-2026-10-26-tts-sideload-load"
round: 2
---

# Critical Review: tts-sideload-load

> **Review Mode:** `plan`
> **Verdict:** `changes_required`
> **Intent achieved:** partial. One High blocking finding; three non-blocking findings.

## Intent anchor

> Confirm the Session 42 plan makes a sideloaded TTS model that is listed as downloaded loadable, logs every load failure, swaps the stale spaCy path when the models directory changes, and records the eSpeak live-path evidence, with sound Red/Green proof before execution.

The planned service persistence and failure logging, owned spaCy path swap, and evidence disposition substantially deliver that objective. The mandatory unsupported-format Red/Green proof cannot execute as prescribed.

## Scope

**Worktree:** `P:/av-kit-wt/s42-tts-sideload-load`, branch `s42-tts-sideload-load`. Every shell command used this worktree as cwd. Repository files were read only. The only reads from `P:/av-kit` were the explicitly authorized CPython 3.12 interpreter and its installed spaCy source; no Session 40 working files were inspected or changed.

**Targets:** `docs/execution/plans/2026-10-26-tts-sideload-load/{implementation-plan.md,task.md,session-gate.ps1,red-check.py,identity.py}`.

**Canon and source:** 03 §TTS sideload load, grouping Session 42/D-94–D-103, the three known issues, AC-74.11, models service, adapter/assets/manager/catalog/voices, ports, repository/unit-of-work/seed code, API wiring/health/error paths and named test fixtures. Checklist: PR-1–PR-9 and applicable DR/IR checks. Review template and recent TTS voice-panel peer reviewed before writing.

**Readiness:** all 27 task rows are unchecked. Git status shows only the five untracked plan-folder files. No baseline.sha or MEU-98 implementation handoff exists. All 22 checked executable/test paths exist. Squashed history, Session 40/D-103 prerequisites, absent eSpeak and no GUI change are accepted dispatch constraints.

**Execution/write boundary:** no pytest, Vitest, session gate or Electron execution; no implementation edits. Both expressly permitted selftests ran with scratch TEMP/TMP under `C:/Temp/av-kit` and bytecode writes disabled. Task lint used `RECEIPTS_DIR=C:/Temp/av-kit`. Report and receipts are under that directory. The user's final-JSON and receipt-only write instructions supersede local timestamp-suffix/canonical-write instructions. The coordinator copies this report verbatim to `.agent/context/handoffs/2026-10-26-tts-sideload-load-plan-critical-review.md`.

## Findings

| # | Severity / Confidence | Blocking | Kind / Subject | Finding | File:Line | Recommendation | Status |
|---|---|---|---|---|---|---|---|
| F1 | High / High | yes | behavior / deliverable | AC-98.5(c) prescribes dataclasses.replace(variant, format="TFLite"), but ModelVariant.__post_init__ immediately calls require_enum and raises ValidationError("format must be a ModelFormat"). The adapter is never called. Row 4 therefore produces a rejected bare validation diagnostic, or an assertion about absent logs that cannot turn Green through the permitted adapter edit. This is a concrete defect in the required unsupported-format Red/Green proof. **Violates: AC-98 (AC-98.5).** | docs/execution/plans/2026-10-26-tts-sideload-load/implementation-plan.md:153; docs/execution/plans/2026-10-26-tts-sideload-load/task.md:48; packages/core/src/avkit_core/domain/tts.py:327; packages/core/src/avkit_core/domain/errors.py:225 | Specify an explicit malformed adapter-input fixture that can reach the defensive unsupported-format branch without running ModelVariant construction validation, or amend this unreachable-input test with source-backed justification. Preserve domain validation and require an assertion Red followed by an adapter-driven Green. | open |
| F2 | Medium / High | no | behavior / deliverable | The eSpeak stage equates shutil.which returning None with eSpeak being absent. Production also detects installations under ProgramFiles and ProgramFiles(x86), so a supported installation outside PATH would be recorded as missing and skip AC-74.11. Today's given absent installation still correctly takes [B]; this affects the explicitly allowed case where Mat installs it before row 10. | docs/execution/plans/2026-10-26-tts-sideload-load/implementation-plan.md:123; docs/execution/plans/2026-10-26-tts-sideload-load/task.md:56; packages/infrastructure/src/avkit_infra/tts/espeak.py:146 | Use the production eSpeak status/detection contract, including the Windows fallback locations and version result, for the row-10 branch and its recorded evidence. | open |
| F3 | Low / High | no | clerical / deliverable | The 'one commit' and 'second call commits nothing' claims describe explicit service calls, not actual unit-of-work commits. SqlAlchemyUnitOfWork.__exit__ calls commit on every clean exit; the first scan also explicitly commits, and unchanged scans still auto-commit. The proposed fake's __exit__ does nothing, so its commits counter cannot establish total production commit counts. No duplicate repository write or existing commit-count regression was found. | docs/execution/plans/2026-10-26-tts-sideload-load/implementation-plan.md:115; docs/execution/plans/2026-10-26-tts-sideload-load/implementation-plan.md:116; packages/infrastructure/src/avkit_infra/database/unit_of_work.py:60; tests/unit/test_services.py:296 | Qualify these as explicit service commit calls and retain idempotence assertions on mark_downloaded/database writes; do not broaden scope to change the existing unit-of-work lifecycle. | open |
| F4 | Low / High | no | clerical / deliverable | The statement that the next model list swaps spaCy paths is inaccurate. list_available only checks ONNX_VOCAB, whose state branch never activates spaCy. GET /health/dependencies and a successful load do reach spaCy readiness; the planned AC-98.9 uses the former and remains valid. | docs/execution/plans/2026-10-26-tts-sideload-load/implementation-plan.md:100; packages/core/src/avkit_core/services/models.py:119; packages/infrastructure/src/avkit_infra/tts/assets.py:249 | Describe the trigger as the next spaCy readiness/activation call and remove model listing from the examples, unless that additional trigger is deliberately added to the contract. | open |

### F1: the mandatory Red cannot reach the branch it is meant to prove

This is a source-traced runnable defect, not an executed product test. Python's dataclass replacement reconstructs the object. The prescribed `format="TFLite"` therefore reaches `ModelVariant.__post_init__` and `require_enum` before any `load_model` call. The immediate exception message is `format must be a ModelFormat`, not `unsupported model format: …`.

Row 4 explicitly requires `test_ac_98_5_unsupported_format_logs` to fail by assertion, and row 5 permits only an adapter change. An uncaught construction exception is rejected by red-check; catching it and asserting the requested event/message leaves a test that cannot turn Green by changing the adapter. Specify a reachable defensive-input fixture or source-backed amendment before execution. Do not weaken the domain invariant.

### Findings that do not gate approval

F2 is a supported installation branch missed by the probe, rather than an objection to this machine's given absence. F3 distinguishes explicit service calls from the unchanged automatic transaction lifecycle; no repeated mark_downloaded write is established. F4 is a factual trigger correction: the real Dependencies path used by AC-98.9 does invoke spaCy readiness.

## Checklist Results

Manual checks below were performed by **codex-independent-reviewer**, with null exit code. Command checks preserve actual child exits. Passing checker fixtures are not product execution evidence.

| Check | Result | Command / procedure | Exit | Evidence |
|---|---|---|---|---|
| PR-2: unstarted work and referenced executable existence | pass | Read task status, inspect git status, and check the named scripts/tests plus baseline and implementation-handoff existence from the worktree. | null | Git status lists only the five untracked plan-folder files. All 22 checked scripts/test paths exist; baseline.sha and the implementation handoff are absent. All 27 task rows remain unchecked. |
| Sideload persistence, idempotent writes, AC-12.8/AC-9.8 and census | pass | Trace ModelService, catalog port/adapter, repository and unit-of-work implementations; compare named fake/test expectations and the complete CENSUS_PATTERNS search receipt. | null | Recording existing repository ids before list/load repairs the path; unknown scanned ids remain display-only. Manager persistence prohibition remains intact. Census finds AC-12.8, AC-9.8, commit counters and load-log assertions, and explicitly names test_uow_commit_log.py. F3 qualifies total commit claims. |
| PR-4: intended Red and Green reach the specified branch | fail | Trace AC-98.5(c)'s prescribed dataclasses.replace through ModelVariant.__post_init__/require_enum to the adapter entrypoint and compare row 4's assertion-only Red requirement. | null | F1: construction raises 'format must be a ModelFormat' before KokoroAdapter.load_model. Other planned Red scenarios reach existing public surfaces; domain errors must be caught before outcome assertions as the plan requires. |
| Load failures and production contract stack | partial | Read adapter failure branches, service load path, API mapping, Stack fixture, FakeSession and the planned GET-downloaded/POST-load test. | null | Missing/unset/unreadable paths, missing torch/kokoro and unsupported format are the identified logging gaps. Existing engine/probe failures already log. Stack uses build_services/create_app with real services/repository; AC-98.6 avoids put_weights' pre-recording and checks the scanned path, size, successful load and removed-file error/log. F1 prevents the complete prescribed proof. |
| spaCy path swap and runtime readiness basis | pass | Read assets activation/readiness, health and wiring call chains, isolated_path/_install_spacy fixtures, and installed spaCy util.py is_package source. | null | Installed spaCy is_package uses distribution metadata. Removing owned old entries and invalidating caches therefore addresses the stale readiness path without removing pre-existing foreign entries. AC-98.9 exercises real Dependencies readiness; S4 preserves a runtime stop. No live spaCy or product test was executed. F4 corrects the list-trigger claim. |
| eSpeak evidence closeout | partial | Compare ESPEAK_STAGE, row 10, H2 issue writes, grouping D-100, AC-74.11 and production EspeakCliAdapter detection. | null | Given absence correctly yields exit 3, [B] with linked issue/evidence, fresh verification and an open issue. Present pass/failure disposition follows grouping scope. F2 identifies the narrower PATH-only detection. |
| PR-1/PR-5/PR-7: scope, order, amendments and state writes | pass | Compare plan contracts and all task rows with the session-gate allow-list/stages and canonical spec/grouping; inspect the whole Red checker and identity source. | null | Three production files/four test files, TA-1, S1-S7 and hub/state writes agree. H1-2 follows bound hub edits; H2 rechecks affected state-canon suites. Out-of-scope rows do not hide specified work. Session-40 prerequisites and expected eSpeak [B] are accepted constraints. Node runtime identity is not recorded despite state-canon; no separate blocker is inferred from that limitation. |
| red-check.py selftest | pass | rtk proxy pwsh -NoProfile -Command '$env:PYTHONDONTWRITEBYTECODE="1"; $env:TEMP="C:/Temp/av-kit"; $env:TMP="C:/Temp/av-kit"; & P:/av-kit/.venv/Scripts/python.exe -B docs/execution/plans/2026-10-26-tts-sideload-load/red-check.py --selftest; exit $LASTEXITCODE' | 0 | red-check selftest: 37 fixture(s) (11 positive, 26 negative), 0 wrong: [] |
| identity.py selftest | pass | rtk proxy pwsh -NoProfile -Command '$env:PYTHONDONTWRITEBYTECODE="1"; $env:TEMP="C:/Temp/av-kit"; $env:TMP="C:/Temp/av-kit"; & P:/av-kit/.venv/Scripts/python.exe -B docs/execution/plans/2026-10-26-tts-sideload-load/identity.py --selftest; exit $LASTEXITCODE' | 0 | identity selftest: 0 failure(s). Bound mutations changed identity and refused historical evidence; designated closeout artifacts left identity unchanged. |
| Task contract linter | pass | rtk proxy pwsh -NoProfile -Command '$env:RECEIPTS_DIR="C:/Temp/av-kit"; $env:PYTHONDONTWRITEBYTECODE="1"; & P:/av-kit/.venv/Scripts/python.exe -B tools/lint_task_contract.py --allowed-builder-classes avkit_builder,avkit_coordinator,avkit_verifier --task docs/execution/plans/2026-10-26-tts-sideload-load/task.md; exit $LASTEXITCODE' | 0 | OK: 27 rows; 25 fully checked; dependencies resolve and are acyclic; H1-5 and H2-1 exempt view_file rows. |
| Product suites, session gate and Electron | n/a | Not run per dispatch | — | Not run, as explicitly required by the review dispatch. This is plan/source review, not execution certification. |

### Information Retrieval (IR)

Source labels, named contracts, BUILD_PLAN audit and H1/H2 outputs are present. AC-9.8's manager no-persistence constraint and AC-12.8's display-only unknown id remain intact. The untruncated CENSUS_PATTERNS receipt finds the relevant list/load/mark/commit/log tests; explicitly naming test_uow_commit_log covers its nonmatching content. No additional existing expectation requiring a test amendment was found beyond TA-1.

### Design / Documentation Review (DR)

The root-cause account matches current service and adapter source. RECORD_RULE avoids repeated mark_downloaded calls for the same downloaded path and repairs different persisted paths. F3 limits its production commit claim.

Installed spaCy util.py:993–1003 uses distribution metadata for is_package. The proposed owned-entry removal plus cache invalidation addresses the stale path while preserving entries av-kit did not add. The fixture has both importable package content and dist-info, and AC-98.9 uses the real health/service/assets chain. S4 correctly reserves a runtime stop if the assertion does not hold. This source review does not claim a live readiness measurement.

The contract stack uses build_services and create_app, real services and persistence, with fake engines/downloads. AC-98.6 explicitly drops an unrecorded file instead of using put_weights, which would pre-record it. Its final removed-file log assertion is a valid Red after the row-3 persistence fix. The other new log assertions and TA-1 reach existing missing-path/runtime branches.

### Plan Review (PR)

PR-1/2/3/5/6/7 pass: order, ownership, not-started state, source basis, handoffs and exclusions are consistent. PR-4 fails for F1. PR-8 is partial because that negative oracle stops before the adapter. PR-9 has no materially competing definition requiring a blocker.

Scope tables and session-gate's allow-list agree. Static checks precede the full stages, and later steps become not_run after failure. Only the three baseline-observed packaging ids can be excused. Row 9's bound hub edits precede H1-2; H2 updates approval state and rechecks state-canon. Red-tree ordering permits the earlier dependency fix while prohibiting the current fix. No omitted required product file or missing executable was found.

Task lint confirms syntax/receipt shape and dependency acyclicity; it does not establish semantic executability, as F1 demonstrates. Baseline collection intentionally records failing sets; row 10 intentionally exits 3 when absent and obtains a valid [B] evidence block.

### Durable observed command evidence

The following commands ran from the worktree; the actual invocations redirected all streams to review receipts and immediately preserved the exit before reading the output.

```json
{"schema_version":"evidence.v1","check_id":"review-red-selftest","command":"rtk proxy pwsh -NoProfile -Command '$env:PYTHONDONTWRITEBYTECODE=\"1\"; $env:TEMP=\"C:/Temp/av-kit\"; $env:TMP=\"C:/Temp/av-kit\"; & P:/av-kit/.venv/Scripts/python.exe -B docs/execution/plans/2026-10-26-tts-sideload-load/red-check.py --selftest; exit $LASTEXITCODE'","cwd":"P:/av-kit-wt/s42-tts-sideload-load","scope":"red-check.py selftest","phase":"targeted","exit_code":0,"result":"pass","tested_state":"plan-review-only; unstarted worktree; not a product full-gate identity","output":"red-check selftest: 37 fixture(s) (11 positive, 26 negative), 0 wrong: []","fresh":true}
```

```json
{"schema_version":"evidence.v1","check_id":"review-identity-selftest","command":"rtk proxy pwsh -NoProfile -Command '$env:PYTHONDONTWRITEBYTECODE=\"1\"; $env:TEMP=\"C:/Temp/av-kit\"; $env:TMP=\"C:/Temp/av-kit\"; & P:/av-kit/.venv/Scripts/python.exe -B docs/execution/plans/2026-10-26-tts-sideload-load/identity.py --selftest; exit $LASTEXITCODE'","cwd":"P:/av-kit-wt/s42-tts-sideload-load","scope":"identity.py selftest","phase":"targeted","exit_code":0,"result":"pass","tested_state":"plan-review-only; unstarted worktree; not a product full-gate identity","output":"identity selftest: 0 failure(s). Bound mutations changed identity and refused historical evidence; designated closeout artifacts left identity unchanged.","fresh":true}
```

```json
{"schema_version":"evidence.v1","check_id":"review-task-lint","command":"rtk proxy pwsh -NoProfile -Command '$env:RECEIPTS_DIR=\"C:/Temp/av-kit\"; $env:PYTHONDONTWRITEBYTECODE=\"1\"; & P:/av-kit/.venv/Scripts/python.exe -B tools/lint_task_contract.py --allowed-builder-classes avkit_builder,avkit_coordinator,avkit_verifier --task docs/execution/plans/2026-10-26-tts-sideload-load/task.md; exit $LASTEXITCODE'","cwd":"P:/av-kit-wt/s42-tts-sideload-load","scope":"Task contract linter","phase":"targeted","exit_code":0,"result":"pass","tested_state":"plan-review-only; unstarted worktree; not a product full-gate identity","output":"OK: 27 rows; 25 fully checked; dependencies resolve and are acyclic; H1-5 and H2-1 exempt view_file rows.","fresh":true}
```

The complete search receipt is `C:/Temp/av-kit/s42-review-census.txt`; the existence/status observations and decisive findings are described above rather than treated as product passing evidence. Git status exited 0 with a warning about access to the user's global ignore file; no source conclusion relies on that ignore file.

## Verdict

`changes_required` — correct F1 through `/plan-corrections` before execution. Keep the assertions and domain invariant meaningful. F2–F4 are non-blocking and may be corrected in the same pass.

**Open questions:** none needed to establish this verdict. Session 40/D-103 and execution authorization remain the intended prerequisites.

**Residual risk:** the worktree's future Python 3.12 runtime, Red receipts, real spaCy swap, successful model load and eSpeak outcome still require execution evidence. identity.py records Python/distributions/eSpeak but not Node runtime despite state-canon; no independent product false-pass is asserted from that limitation. No product-suite pass, live audio output or execution approval is claimed.

**Saved report:** `C:/Temp/av-kit/dispatch/s42-plan-review-r1.md`. **Coordinator destination:** `.agent/context/handoffs/2026-10-26-tts-sideload-load-plan-critical-review.md`.

Completion-preflight was consulted for review completeness; it does not authorize execution of the unstarted task table. Review stops here without corrections.

---

## Corrections Applied — 2026-10-26 (round 1, by claude-code-local, the plan author)

The verdict field is set to `corrections_applied`. Approval needs an independent round 2.

| Finding | Change | Where |
|---|---|---|
| F1 (blocking) | AC-98.5(c) no longer uses `dataclasses.replace`. It builds a valid ONNX variant with an existing weight file and forces `object.__setattr__(variant, "format", "TFLite")` on that one frozen instance, so `ModelVariant.__post_init__`/`require_enum` (`domain/tts.py:327`) is untouched. With the probe `lambda fmt: frozenset()` and `DeviceType.CPU`, `_resolve` (`adapter.py:268-279`) returns `cpu` and `load_model` reaches `adapter.py:260-261`. At row 4 the `ValidationError` is raised with no event, so the event-count assertion fails (`AssertionError`, accepted by red-check). The row 5 adapter edit turns it Green. | `implementation-plan.md` AC-98.5 |
| F2 | `ESPEAK_STAGE` and row 10 probe with `EspeakCliAdapter().status()` (PATH, then the `ProgramFiles`/`ProgramFiles(x86)` locations, then `--version`) and print the path and version. Exit 3 iff `available` is False. `identity.py` records the same status. D-130's reasoning names the change. | `implementation-plan.md` `ESPEAK_STAGE`, §Validation stage contract, D-130; `task.md` row 10; `identity.py` `_espeak_identity` |
| F3 | "Commit" is defined once in `RECORD_RULE` as the explicit `uow.commit()` call counted by the fake's `commits`. `SqlAlchemyUnitOfWork.__exit__`'s automatic commit is unchanged and out of scope. AC-98.1 and item 1 of User Review Required now say explicit commit calls and also assert that the second call makes no `mark_downloaded` call. | `implementation-plan.md` §User Review Required item 1, `RECORD_RULE`, AC-98.1, D-123 |
| F4 | Item 5 of User Review Required gives the swap trigger as the next spaCy readiness or activation call (`GET /api/v1/health/dependencies`, or a successful model load). Model listing is removed. | `implementation-plan.md` §User Review Required item 5 |
| Residual (Node identity) | `identity.py` `runtime_identity` adds `node` (`node --version`), and the selftest mutates it. | `identity.py`; plan §Validation stage contract, R-1 |

**Blast-radius census:** 5 values changed. Variants swept in the plan folder (plan, task, `identity.py`, `session-gate.ps1`): `shutil.which`, `TFLite`, `replace(variant`, `commits nothing`, `one commit`, `list or load`, `GET /dependencies`, `espeak-ng absent`. That found 11 sites; 9 were updated and 2 are consistent as they stand: the D-130 reasoning names `shutil.which` on purpose, and AC-98.3's "one commit" now reads under `RECORD_RULE`'s definition.

**Verification (read-only; no product tests were run because the peer session holds the machine's test capacity):**
- `identity.py --selftest`: exit 0, 0 failures (`C:/Temp/av-kit/s42-plan-R-identity.txt`).
- `ruff check --ignore E501 identity.py`: clean. The E501 long lines carry over from Session 40's copy and are outside the gate's `packages/ tests/` ruff scope.
- `lint_task_contract.py`: exit 0, 27 rows (`C:/Temp/av-kit/s42-plan-R-task-lint.txt`).
- Live probe: `_espeak_identity()` = `<absent>`; `node --version` = `v24.19.0`.

`P:/av-kit` porcelain was unchanged across the review run (34 entries before and after).


---

## Recheck (2026-10-26)

**Workflow:** `/plan-critical-review`, round 2 recheck of `/plan-corrections`.
**Agent:** `codex-independent-reviewer` (independent of `claude-code-local`).
**Loop:** `s42-plan-2026-10-26-tts-sideload-load`.
**Intent anchor:** Confirm the Session 42 plan makes a sideloaded TTS model that is listed as downloaded loadable, logs every load failure, swaps the stale spaCy path when the models directory changes, and records the eSpeak live-path evidence, with sound Red/Green proof before execution.

### Prior Pass Summary

| Finding | Prior Status | Recheck Result |
|---|---|---|
| F1 — unreachable unsupported-format Red | open; author reports fixed | **Fixed.** `implementation-plan.md:153` builds a valid instance, then changes only that instance with `object.__setattr__`; `task.md:48-49` retains assertion Red before the adapter-only Green. See source trace below. |
| F2 — PATH-only eSpeak detection | open; author reports fixed | **Fixed.** `implementation-plan.md:123`, `task.md:56` and `identity.py:84-89` call production `EspeakCliAdapter().status()`. The fallback locations and returned fields match `tts/espeak.py:146-174` and `domain/tts.py:194-208`. |
| F3 — ambiguous commit totals | open; author reports fixed | **Fixed.** `implementation-plan.md:96,116,149` explicitly distinguish service calls from the automatic commit at `database/unit_of_work.py:60`; the fake counts explicit calls at `tests/unit/test_services.py:299-300`. AC-98.3's shorthand reads under that definition. D-124's remaining prose at `implementation-plan.md:379` is shorthand for it, not a second transaction policy. |
| F4 — model-list spaCy trigger | open; author reports fixed | **Fixed.** `implementation-plan.md:100` now names spaCy readiness/activation and a successful load. `services/models.py:119` checks only vocab on list; `:151,159` reaches spaCy after load, while `services/health.py:182-193` reaches the readiness path. |
| Node identity residual | disclosed, non-blocking | **Fixed for the identified omission.** `identity.py:98` records `node --version` with `check=True`; `:110` hashes the runtime dictionary. `:193-197` exercises a Node-key mutation, independently reproduced with `state_changed=True`. This does not certify every possible environment input. |

All paths in the table are relative to the reviewed plan folder unless they identify production/tests; production references resolve below `packages/core/src/avkit_core/` or `packages/infrastructure/src/avkit_infra/`, as appropriate.

### Confirmed Fixes

**F1: the corrected Red reaches the defensive branch and the adapter edit can turn it Green.** The existing `_variant` fixture creates the ONNX file and a valid `ModelVariant` (`tests/integration/test_tts_device_resolution.py:134-150`); `_adapter` injects the probe (`:128-131`). `ModelVariant.__post_init__` still validates the enum (`packages/core/src/avkit_core/domain/tts.py:324-331`). The one-instance `object.__setattr__` does not reconstruct it or weaken that domain check. The load unloads first and accepts the existing weight path (`packages/infrastructure/src/avkit_infra/tts/adapter.py:246-247,133-142`). `_resolve` passes the format to the supplied lambda and returns `"cpu"` for `DeviceType.CPU` regardless of the empty probe result (`:268-277`). Both enum identity comparisons fail for `"TFLite"` (`:256-261`), so it raises the expected unsupported-format `ValidationError` before any engine call, without a `tts.load_failed` event. Catching that expected error and asserting exactly one event therefore fails by assertion at row 4. Logging that failure in the row 5 adapter edit satisfies the event assertion with the prescribed cause/device while preserving the raise. No test result is claimed: this is a direct source trace under the no-product-test constraint. The unchanged checker accepts assertions and rejects bare validation diagnostics (`red-check.py:83-84,209-236`).

**F2 and the eSpeak/identity regression check.** Row 10's Python command is syntactically consistent with its production API: `EspeakStatus` has `available`, `path` and `version` (`packages/core/src/avkit_core/domain/tts.py:194-208`); production status locates PATH then Program Files, probes the version and returns either the unavailable sentinel or those fields (`packages/infrastructure/src/avkit_infra/tts/espeak.py:146-174`). The `print` and conditional `sys.exit(0 if s.available else 3)` in `task.md:56` evaluate the status consistently. `_espeak_identity` uses the same source, returns `<absent>` when unavailable and records path/version when available (`identity.py:84-89`); it is not passed through a shell. Node is invoked through an argv list and a failed command raises (`:98`). No new runnable regression was found in these corrections. Neither the production probe nor live audio was run by this reviewer. The given absence still produces row 10's intended missing-dependency `[B]`, leaves the issue open with fresh verification, and permits session closeout; a present installation requires Mat's AC-74.11 result. H2 follows the same issue disposition (`task.md:72`; grouping `:109,166`).

**Persistence, logging and the rider still fit the source.** The missing persistence is visible at `packages/core/src/avkit_core/services/models.py:114-118,141-150`. `SIDELOAD_RECORD` records the scanned path before list/load repository reads (`implementation-plan.md:115-117`), through the existing two-argument port (`packages/core/src/avkit_core/ports/storage.py:99-106`); the repository records size (`packages/infrastructure/src/avkit_infra/database/repositories.py:365-373`). Comparing download state/path avoids repeated `mark_downloaded` writes. Skipping ids without a repository row preserves AC-12.8 (`tests/unit/test_services.py:1862-1888`); keeping persistence in the service preserves AC-9.8 (`tests/integration/test_tts_models.py:565-567`). The current unlogged weight/runtime/format branches are exactly the planned new logging sites (`tts/adapter.py:247,261,282-288`); existing probe/engine/session paths already log (`:250-253,289-292,312-314,332-337`). `LOG_CAUSE` accounts for wrapped errors without requiring duplicate logs. TA-1 retains existing unreadable-file assertions (`tests/integration/test_tts_device_resolution.py:657-677`).

The complete `CENSUS_PATTERNS` sweep was rerun, without truncating its receipt. It reaches the unknown-id test, the unrelated existing commit counter (`tests/unit/test_services.py:2007-2012`), repository-write and log assertions, and spaCy path/order tests; `test_uow_commit_log.py` is explicitly named and concerns UoW log noise, not model-service write counts (`:27-51`). No new required test amendment beyond TA-1 was established. This independent source census does not replace the missing corrector census record in F5.

AC-98.6 deliberately avoids `Stack.put_weights`, which would pre-record the row (`tests/integration/test_tts_assets.py:185-199`). The stack builds the real services/app (`:168-175`), so its downloaded-then-load test reaches real persistence; its removed-file event assertion is a valid Red after the row 3 service fix (`implementation-plan.md:154,247`).

For spaCy, `spacy_ready` activates the directory then requires both metadata readiness and importability (`packages/infrastructure/src/avkit_infra/tts/assets.py:136-149`). The installed runtime's `spacy.util.is_package` uses `importlib_metadata.distribution` (`P:/av-kit/.venv/Lib/site-packages/spacy/util.py:993-1003`, read only). Removing the owned old entry and invalidating caches therefore addresses the stale metadata path even if an imported module retains its spec. `SPACY_PATH_SWAP` preserves foreign/pre-existing entries and append order (`implementation-plan.md:121`); AC-98.8/98.9 cover the path and actual health observable (`:156-157`). The existing wheel fixture supplies both package and dist-info (`tests/integration/test_tts_assets.py:36-45`). Actual runtime readiness remains an execution measurement, with S4 retained (`implementation-plan.md:319`).

### Remaining Findings

| # | Severity / Confidence | Blocking | Kind / Subject | Finding | File:Line | Recommendation | Status |
|---|---|---|---|---|---|---|---|
| F5 | Low / High | no | clerical / review-scaffolding | The correction census gives variants and totals (11 sites, 9 updated, 2 consistent), but names no raw census receipt and assigns no `file:line` disposition to each hit. PR-6's census audit cannot be completed from this correction log. | `.agent/context/handoffs/2026-10-26-tts-sideload-load-plan-critical-review.md:139`; `.agent/workflows/plan-critical-review.md:258` | Name the complete raw old/new-value sweep receipt and list each hit as `updated` or `confirmed-consistent`. | open |

**Instruction precedence for PR-6:** the local workflow would stop round 2 before content review for a missing or undispositioned correction census. The dispatch explicitly requires the substantive recheck and says, "Do not report formatting or process-paperwork nits as blocking" and "Blocking findings must cite an AC id from the plan or a concrete runnable defect." That direct instruction governs this review. F5 is disclosed as non-blocking; it does not establish an AC failure or runnable defect. No PR-6 pass is claimed. The independent sweep receipt is `C:/Temp/av-kit/s42-r2-changed-values.txt`, not a reconstructed author receipt.

### Checklist Results

Manual observations were made by **codex-independent-reviewer**, with null exit code.

| Check | Result | Procedure / observed evidence |
|---|---|---|
| PR-1/PR-3: plan, task and gate alignment | pass | Read plan/task/scripts. Row 4 precedes the adapter edit; row 6 precedes the assets edit. Three production/four test files agree with the gate allow-list. Row 9 hub changes precede H1-2's fresh full gate; H2 rechecks state-canon after approval writes. S1-S7, TA-1 and eSpeak disposition agree. |
| PR-2: not started / referenced paths | pass | Git status shows only the five untracked plan-folder files and rolling plan review; no tracked source diff. All 27 task rows are unchecked; baseline.sha and the implementation handoff are absent. Named Python/tool paths exist; the two Vitest paths resolve under `ui/` via `npm --prefix ui`. |
| PR-4/PR-8: corrected proof and production call chains | pass at plan level | Source traces above establish F1's corrected branch and all revised entrypoints. Checker selftest reproduced; no product execution claimed. |
| PR-5/PR-7: scope and sources | pass | Spec 03 `:507-516`, grouping `:101-112,164-166`, known issues and AC-74.11 agree with retained scope. No GUI change or hidden product deferral introduced. Session 40/D-103 dependency remains accepted. |
| PR-6: correction census | incomplete, non-blocking by dispatch | Correction log `:139` has aggregate counts without the named raw receipt or per-hit dispositions; F5. |
| PR-9 / DR: repeated clauses and source accuracy | pass at plan level | Governed by named contracts; no materially competing live behavior found. F3's remaining shorthand is governed by RECORD_RULE. F4's trigger now matches source. |
| Review completion-preflight | pass for review scope | Canonical task reread; 27 future implementation rows intentionally unexecuted. This review cannot transition to implementation. |
| Product suites / session gate / Electron / live eSpeak | not_run | Explicit dispatch restriction; no runtime/product certification. |

The permitted checks ran from `P:/av-kit-wt/s42-tts-sideload-load`, with `RECEIPTS_DIR`, `TEMP` and `TMP` set to `C:/Temp/av-kit`, `PYTHONDONTWRITEBYTECODE=1`, `PYTHONIOENCODING=utf-8`, and the authorized interpreter. All streams were redirected; child exits were captured immediately. The scratch selftests wrote only under that temp root.

```json
{"schema_version":"evidence.v1","check_id":"r2-red-selftest","command":"rtk proxy P:/av-kit/.venv/Scripts/python.exe -B docs/execution/plans/2026-10-26-tts-sideload-load/red-check.py --selftest","cwd":"P:/av-kit-wt/s42-tts-sideload-load","scope":"Red-checker fixtures only","phase":"targeted","exit_code":0,"result":"pass","tested_state":"round-2 plan/source review; unstarted product; not a full product-gate identity","output":"red-check selftest: 37 fixture(s) (11 positive, 26 negative), 0 wrong: []","fresh":true}
```

```json
{"schema_version":"evidence.v1","check_id":"r2-identity-selftest","command":"rtk proxy P:/av-kit/.venv/Scripts/python.exe -B docs/execution/plans/2026-10-26-tts-sideload-load/identity.py --selftest","cwd":"P:/av-kit-wt/s42-tts-sideload-load","scope":"Identity fixture only","phase":"targeted","exit_code":0,"result":"pass","tested_state":"round-2 plan/source review; unstarted product; not a full product-gate identity","output":"bound runtime node: state_changed=True; bound runtime espeak_ng: state_changed=True; bound file mutations: historical_refused=True; identity selftest: 0 failure(s)","fresh":true}
```

```json
{"schema_version":"evidence.v1","check_id":"r2-task-lint","command":"rtk proxy P:/av-kit/.venv/Scripts/python.exe -B tools/lint_task_contract.py --allowed-builder-classes avkit_builder,avkit_coordinator,avkit_verifier --task docs/execution/plans/2026-10-26-tts-sideload-load/task.md","cwd":"P:/av-kit-wt/s42-tts-sideload-load","scope":"Task contract","phase":"targeted","exit_code":0,"result":"pass","tested_state":"round-2 plan/source review; unstarted product; not a full product-gate identity","output":"OK: 27 row(s); 10-column table (with builder_model); 25 row(s) fully checked: backticked, exit-code re-raised, receipt under RECEIPTS_DIR; dependencies resolve and are acyclic; 2 row(s) exempt (view_file): H1-5, H2-1","fresh":true}
```

### Verdict

**approved — intent achieved: yes, at plan level.** F1-F4 and the Node identity residual are fixed. One Low non-blocking census-record finding remains (F5); no blocking finding remains. The corrected plan can deliver its stated objective, subject to the existing execution prerequisites and gates.

**Residual risk:** actual Red/Green, a real successful sideload load, spaCy readiness after the swap, and the eSpeak stage remain future execution evidence. No pytest, Vitest, session gate, Electron, live probe or GUI run was performed. The two tooling selftests do not prove runtime product behavior. No new open question requires a human decision for this verdict. Session 40 incorporation and explicit human execution authorization remain intended prerequisites, not review findings.

**Saved report:** `C:/Temp/av-kit/dispatch/s42-plan-review-r2.md`. The coordinator copies it verbatim to `.agent/context/handoffs/2026-10-26-tts-sideload-load-plan-critical-review.md`. All existing thread bytes are retained apart from the three requested frontmatter fields. This recheck is the single appended `## Recheck` section, preserving round 2. Only temp artifacts were written. Approval does not authorize implementation, commit or push. The dispatch's JSON-only final and temp-only write boundary supersede the local timestamp-suffix and canonical-write directions.

---

## Coordinator note — F5 census record (2026-10-26, claude-code-local; does not change the round 2 verdict)

Raw old- and new-value sweep over the plan folder (plan, task, `identity.py`, `session-gate.ps1`): `C:/Temp/av-kit/s42-plan-r1-census.txt`. Per-hit disposition:

| Value | Hit | Disposition |
|---|---|---|
| `shutil.which` | `implementation-plan.md:439` (D-130 reasoning) | confirmed-consistent: it names the old probe on purpose |
| `TFLite`, `object.__setattr__` | `implementation-plan.md:153` (AC-98.5(c)) | updated |
| `commits nothing`, `one commit` | `implementation-plan.md:151` (AC-98.3) | confirmed-consistent: it reads under `RECORD_RULE`'s definition |
| `replace(variant`, `list or load`, `GET /dependencies`, `espeak-ng absent` | none | removed |
| `EspeakCliAdapter` | `implementation-plan.md:123`, `:439`, `:472`, `:487`; `task.md:56`; `identity.py:20`, `:86`, `:88` | updated |
| explicit `uow.commit()` | `implementation-plan.md:96`, `:116`, `:149`, `:473` | updated |
| `health/dependencies` | `implementation-plan.md:100` | updated |
| `"node"` | `identity.py:98`, `:193` | updated |
