---
date: "2026-10-15"
project: "2026-10-14-backend-robustness"
meu: "MEU-77"
status: "complete"
action_required: "VALIDATE_AND_APPROVE"
template_version: "2.2"
verbosity: "standard"
plan_source: "docs/execution/plans/2026-10-14-backend-robustness/implementation-plan.md"
build_plan_section: "bp03"
agent: "claude-code (Claude Opus 5.5)"
reviewer: "Codex gpt-6.1-sol via local dispatch"
predecessor: "2026-10-14-backend-robustness-MEU-78-handoff"
---

# Handoff: 2026-10-14-backend-robustness-MEU-77-handoff

> **Status**: `complete`
> **Action Required**: `VALIDATE_AND_APPROVE`

---

## Scope

**MEU**: MEU-77 — `svc-tts-async-generate`.
- `ASYNC_GENERATE`: `TTSService.generate` runs today's synchronous checks (text, speed, format, model loaded, voice, assets), then admits one `Generating` row under `_lock`. It sets `_current_id`, clears the cancel flag, and hands the run to `spawn`. The default `spawn` is a daemon thread named `tts-generate`; tests inject their own. It returns the `Generating` row at once, so `POST /tts/generate` answers 201 `Generating`. A `spawn` that raises releases the reservation through `_finish` and re-raises, giving a 500. `generate` counts in-flight callers (`_callers`) so that `wait_idle` and `stop_processing` drain them.
- `WORKER_RULE`: `_work` never raises.
  - A `DomainError` becomes `Failed` with its message.
  - Any other exception becomes `Failed` with `"Type: message"` (or `"Type"`).
  - Both log one `tts.generate_failed` with `exc_info`.
  - The terminal write and the reservation release happen in `_finish`, called from `finally`.
- `CANCEL_RULE`: `cancel(id)` sets the flag only when `id` is the running job. `on_progress` raises `_Cancelled` when the flag is set. The worker also checks the flag before `prepare`, after the WAV write and after the MP3 convert. `_finish` holds `_lock` for the terminal write, so a cancel arriving during the `Done` write waits, and the flag cannot leak to the next job (D-25).
- `PARTIAL_CLEANUP`: a `Cancelled` or `Failed` end unlinks `{id}.wav` and `{id}.mp3`. An unlink `OSError` is logged as `tts.cleanup_failed`.
- `RESTART_RECOVERY`: the lifespan calls `services.tts.recover_stale_processing()`, which marks every `Generating` row `Failed` with `"interrupted by restart"` via the new `TTSJobRepository.list_by_status`.
- `SHUTDOWN_STOP`: `stop_processing(timeout=10.0) -> bool` refuses new jobs (`_closing`), cancels the running job and waits for idle. On a timeout it logs `tts.stop_timeout`. The lifespan unloads models and disposes the engine only when it returns `True`; otherwise it logs `api.shutdown_tts_busy`. `wiring._TTSRuntime` types `AppServices.tts`.
- `PROGRESS_LAZY`: the PyTorch branch iterates the `KPipeline` generator lazily. Progress is `min(0.99, index / estimate)`, where `estimate` is the count of sentence terminators. The final call is 1.0, and a cancel raised from `on_progress` stops before the next chunk.
- `OPENAPI_DIFF`: the generate and cancel route docstrings are updated, and `openapi.committed.json` was regenerated.
- `MCP_TTS_TEXT`: the `avkit_tts` `desc()` and the `SERVER_INSTRUCTIONS` TTS line describe the asynchronous generate, the polling, and the cancel of a running job.
- `AUDIT_CANCEL_STEP`:
  - `destructiveStep` gains `raceLost` and `attempts` (default 1, unchanged behaviour).
  - `tts.cancel` targets a second, long job (`tts_job2`, `AUDIT_FIXTURES.tts_cancel_text`) while it is `Generating`, with up to 3 attempts when the job reaches `Done` first.
- `TEST_AMENDMENTS`: each carries `TA-n (Session 33, MEU-77)`.
  - **TA-5, TA-6:** the TTS repository method lists gain `list_by_status`.
  - **TA-7, TA-8:** an out-of-range progress fraction ends `Failed` after `wait_idle`, instead of raising from `generate`.
  - **TA-9:** a port error answers 201, and the row is `Failed` after `wait_idle`.
  - **TA-10:** both `test_ac_62_16` cases read the finished job with `GET`.
- `FIXTURE_REPAIRS`:
  - **(a):** `_tts_stack` passes `spawn=lambda fn: fn()`.
  - **(b):** `FakeTTSRepo.list_by_status`.
  - **(e) / A-7:** `test_api_auth._services()` passes a separate always-idle TTS fake.
  - **(f):** `_generate` / `_generate_with` wait for idle after the POST.
  - No assertion changed.

**Build Plan Section**: `docs/build-plan/03-service-layer.md` §TTS generation (03:423, 03:476-479)
**Predecessor**: MEU-78. MEU-77 shares `wiring.py`, `openapi.committed.json`, `tests/unit/test_domain.py`, `tests/unit/test_services.py` and `tests/e2e/test_api_auth.py` with MEU-78, in separate hunks.

---

## Acceptance Criteria

| AC | Type | Description | Source | Test(s) | Status |
|----|------|-------------|--------|---------|--------|
| AC-77.1 | unit | `ASYNC_GENERATE`: with the default thread spawn and a blocking port, `generate()` returns `Generating` within 1 s. After release, `wait_idle(5.0)` is `True` and the job is `Done` with its file. | Spec 03:502 | `tests/unit/test_tts_async.py:311` `test_ac_77_1_generate_returns_generating_then_done`, `:329` `…_not_done_while_port_blocks_neg` | ✅ |
| AC-77.2 | unit | One at a time: a second `generate()` during a run raises `ConflictError` and adds no row. After the first finishes, a new one succeeds. | Spec 03:504 | `test_tts_async.py:345`, `:358` `…_neg` | ✅ |
| AC-77.3 | unit | The synchronous checks raise before any row is added and before `spawn` is called. A valid request spawns exactly once. | Local Canon services/tts.py | `test_tts_async.py:371` (parametrized), `:393` `…_neg` | ✅ |
| AC-77.4 | unit | `CANCEL_RULE` + `PARTIAL_CLEANUP` mid-synthesis: no further segment runs, the job is `Cancelled`, and no files remain. Cancelling an unknown or `Done` id changes nothing. | Spec 03:503 | `test_tts_async.py:410`, `:424` `…_neg` | ✅ |
| AC-77.5 | unit | Cancel from the WAV and MP3 hooks leaves no files. The terminal-write barrier makes `cancel` wait, the job ends `Done` with its MP3, and the next job is `Done` (D-25). | Spec 03:477; D-25 | `test_tts_async.py:440` (parametrized), `:458` (parametrized, R1 F1: `tts.output_path` changed mid-job, Cancelled and Failed), `:481`, `:506` `…_neg` | ✅ |
| AC-77.6 | unit | `WORKER_RULE`: a `RuntimeError` gives `Failed` `"RuntimeError: engine died"`, one `tts.generate_failed` with `exc_info`, no partial files, and no thread excepthook. A `ValidationError` also ends `Failed`. | Spec 03:424 (D-19) | `test_tts_async.py:517`, `:540`, `:552` `…_neg` | ✅ |
| AC-77.7 | unit | A raising `spawn` gives a `Failed` row and clears the reservation, and `generate()` re-raises. The next `generate()` succeeds. | `ASYNC_GENERATE` | `test_tts_async.py:565`, `:581` `…_neg` | ✅ |
| AC-77.8 | integration | `RESTART_RECOVERY` through a real lifespan: `Generating` becomes `Failed` `"interrupted by restart"`, and `Done`/`Cancelled` rows are unchanged. | Local Canon main.py | `tests/integration/test_tts_assets.py:914`, `:921` `…_neg` | ✅ |
| AC-77.9 | unit | `SHUTDOWN_STOP` (a)–(h): cancel and idle, timeout `False` plus a log, lifespan order and the busy skip, refusal after stop, reservation before spawn (D-30), spawn failure while stopping, and the caller drain after the worker and before admission (D-31). With nothing running, it returns `True` at once. | Local Canon main.py; D-26, D-30, D-31 | `test_tts_async.py:601`, `:619`, `:659` (parametrized), `:692`, `:701`, `:719`, `:757`, `:795`, `:827` `…_neg` | ✅ |
| AC-77.10 | contract | Real stack with a gated port: POST is 201 `Generating`, GET is `Generating`, DELETE is 204, and GET then reaches `Cancelled`. A second POST during the run is 409 with the envelope. | Spec 03:476-477 | `test_tts_assets.py:952`, `:976` `…_neg` | ✅ |
| AC-77.11 | unit | `PROGRESS_LAZY`: the PyTorch branch stops after one chunk, and values stay ≤ 0.99 until the final 1.0. ONNX calls `_onnx_chunk` once. | Spec 03:503 | `test_tts_async.py:884`, `:903`, `:921` `…_neg` | ✅ |
| AC-77.12 | unit | `MCP_TTS_TEXT`: generate returns the `Generating` JSON in one fetch, and both texts carry the new wording, with no `generate is one job`. | Spec 03:479; 05:275 | `mcp-server/tests/tts.test.ts:26`, `:42`, `:46` `[neg]` | ✅ |
| AC-77.13 | unit | `AUDIT_CANCEL_STEP` (a)–(d), the fixture length, the `precondition_lost` `[neg]`, and the single-attempt `[neg]`. | Spec 03:479; D-27 | `mcp-server/tests/audit/tts-cancel-step.test.ts:77`, `:83`, `:100`, `:112`, `:122`, `:132`, `:140` | ✅ |
| AC-77.14 | e2e (pin) | `RUN_BAR_PIN`: the run bar polls a `Generating` job at least twice, and `last-output` appears only at `Done`. A second run's Cancel sends one DELETE and returns to an enabled Generate. | Spec 03:479; D-22 | `ui/tests/e2e/tts-generate.test.ts:672` | ✅ (pin: passed at Red and Green, 5/5 at the gate) |

### Other plan AC references (not owned by MEU-77)

| AC | Owner | Status in MEU-77 |
|----|-------|------------------|
| AC-76.x | MEU-76 handoff | ✅ gate76; still green in gate77 |
| AC-78.x | MEU-78 handoff | ✅ gate78; still green in gate77 |
| AC-12.5, AC-62.11, AC-62.16, AC-4.x repository lists | existing suites | pass with TA-5 to TA-10 applied, and no other assertion changed |

<!-- CACHE BOUNDARY -->

---

## Evidence

### FAIL_TO_PASS

| Test | Red Output (snippet) | Green Output | File:Line |
|------|----------------------|--------------|-----------|
| pytest AC-77.1 to AC-77.7, AC-77.9 (30 cases) | `AssertionError: TTSService(spawn=...) is missing` (`_require()` presence assertion) | pass | `test_tts_async.py:311-827` |
| pytest AC-77.8 | `AssertionError: assert [('Generating', None)] == [('Failed', '... by restart')]` (the startup row stays `Generating`) | pass | `test_tts_assets.py:914` |
| pytest AC-77.10 | `AssertionError: TTSService.wait_idle is missing` | pass | `test_tts_assets.py:952,976` |
| pytest AC-77.11 | `assert [1, 2, 3] == [1]`; `assert [0.5, 1.0] == approx([0.25 …])` | pass | `test_tts_async.py:884,903` |
| pytest AC-77.5 R1 F1 (4 cases) | `assert ['<id>.wav'] == []` and `assert ['<id>.mp3', '<id>.wav'] == []` (old-root files left after `tts.output_path` changed) | pass | `test_tts_async.py:458` |
| MCP Vitest AC-77.12 | the description and `SERVER_INSTRUCTIONS` lack the asynchronous text | pass | `tts.test.ts:26,42,46` |
| MCP Vitest AC-77.13 | `tts_cancel_text` absent; the step cancels `tts_job1` with no retry | pass | `tts-cancel-step.test.ts:77-132` |

Before any test ran, red-guard confirmed that the 11 MEU-77 product files were unchanged against the `gate78` snapshot. Red counts: pytest failed 36, passed 22 (the `[neg]` cases and the untouched `test_tts_assets.py` tests). MCP failed 9, passed 1. The ONNX `_neg` of AC-77.11 and the single-attempt `[neg]` of AC-77.13 pass at Red, as they need no new behaviour. AC-77.14 is a pin (`RUN_BAR_PIN`): the GUI run bar already polls, and the spec guards it against regression.

### Commands Executed

```json
{"schema_version": "evidence.v1", "check_id": "s33-row8-red77", "command": "pwsh -NoProfile -File docs/execution/plans/2026-10-14-backend-robustness/validate-task.ps1 -Check red77", "cwd": "P:/av-kit-wt/backend-robustness", "scope": "row 8: MEU-77 Red over AC-77.1-77.13 (pytest, MCP Vitest) and the Electron AC-77.14 pin; red-guard first", "phase": "red", "exit_code": 0, "result": "pass", "tested_state": "MEU-78 gate tree plus MEU-77 test edits only; red-guard: 11 MEU-77 product files unchanged vs the row 7 gate78 snapshot", "output": "pytest failed 36, passed 22 | mcp failed 9, passed 1 | electron passed 1 (pin) | PASS red77 (RED_RULE)", "fresh": true}
```

```json
{"schema_version": "evidence.v1", "check_id": "s33-row9-green77-svc", "command": "pwsh -NoProfile -File docs/execution/plans/2026-10-14-backend-robustness/validate-task.ps1 -Check green77-svc", "cwd": "P:/av-kit-wt/backend-robustness", "scope": "row 9: MEU-77 backend (ASYNC_GENERATE, WORKER_RULE, CANCEL_RULE, PARTIAL_CLEANUP, RESTART_RECOVERY, SHUTDOWN_STOP, PROGRESS_LAZY, list_by_status, route docstrings, openapi) with TA-5..TA-10 and repairs (a), (b), (e), (f)", "phase": "green", "exit_code": 0, "result": "pass", "tested_state": "uncommitted worktree on baseline ddd11171: MEU-76, MEU-78 and the MEU-77 backend plus test edits", "output": "pytest PY77+TA77 192 passed | PASS green pytest MEU-77: passed 192 | openapi --check exit 0 | PASS green77-svc", "fresh": true}
```

```json
{"schema_version": "evidence.v1", "check_id": "s33-row10-green77", "command": "pwsh -NoProfile -File docs/execution/plans/2026-10-14-backend-robustness/validate-task.ps1 -Check green77", "cwd": "P:/av-kit-wt/backend-robustness", "scope": "row 10: MEU-77 MCP side (MCP_TTS_TEXT, AUDIT_CANCEL_STEP in plan.ts and fixtures.ts); every MEU-77 AC incl. Electron AC-77.14", "phase": "green", "exit_code": 0, "result": "pass", "tested_state": "uncommitted worktree on baseline ddd11171: MEU-76, MEU-78 and MEU-77 backend plus MCP side; MCP and Electron rebuilt by the check", "output": "PASS green mcp MEU-77: passed 10 | PASS green electron MEU-77: passed 1 | PASS green pytest MEU-77: passed 192 | PASS green77", "fresh": true}
```

```json
{"schema_version": "evidence.v1", "check_id": "s33-row11-gate77", "command": "pwsh -NoProfile -File docs/execution/plans/2026-10-14-backend-robustness/validate-task.ps1 -Check gate77", "cwd": "P:/av-kit-wt/backend-robustness", "scope": "row 11: MEU-77 targeted gate (pyright, ruff, ui typecheck and lint, mcp typecheck, openapi --check, pytest tests/, ui Vitest, MCP Vitest, source audit, Electron tts-generate.test.ts --repeat-each=5, tests/unit/test_tts_async.py five consecutive runs)", "phase": "targeted", "exit_code": 0, "result": "pass", "tested_state": "MEU-77 final working tree (baseline ddd1117 + MEU-76 diff + MEU-78 diff + MEU-77 diff + TA-1 to TA-11 + repairs (a) to (g))", "output": "py-types, py-lint, ui-types, ui-lint, mcp-types, openapi exit 0 | PASS suite pytest: passed 720 | PASS suite vitest: passed 804 | PASS suite mcp: passed 423 | source-audit rg exit 1 (no hits) | PASS suite electron: passed 75 | test_tts_async.py x5: passed 34 each | PASS gate77", "fresh": true}
```

Final evidence on the whole Session 33 tree (walkthrough §Audit, §Windows gate), rerun after the R1 F1 correction and the A-14 plan rewording: the H1-2 MCP audit of record (`s33-h1-2-audit-r3`) passed 99/99 with `tts.cancel` FIXED and every other action unchanged, `AUDIT_FINGERPRINT` 49d577f4bc8c5ea65e22676d96e83050ef41bd5e37f1c7d28efec93f59a56ce7. H1-3 `WINDOWS_GATE` (`s33-h1-3-windows-gate-r2`) passed 17/17 stages: pytest 724/0, Vitest 804/804, Electron 139/0/0/0, MCP 423/423, source audit 0 hits, `GATE_FINGERPRINT` 300cc234644b17997d1e6e7f2c3a7e6ffc3d0a41bb37b9e6252db41799b26f80 before and after. H1-4 `gate-check` (`s33-h1-4-gate-check-r2`) passed. The earlier `s33-h1-2-audit-final` and `s33-h1-3-windows-gate` runs are superseded.

### Quality Gate Results

```
pyright packages/: 0 errors, 0 warnings
ruff check packages/ tests/: All checks passed!
ui typecheck / lint, mcp typecheck: exit 0
openapi --check: exit 0 (generate and cancel descriptions; OPENAPI_DIFF)
pytest tests/: 724 passed
ui Vitest: 804 passed
MCP Vitest: 423 passed
Electron tts-generate.test.ts --repeat-each=5: 75 passed (15 tests x 5)
tests/unit/test_tts_async.py, five consecutive runs: 38 passed each
source audit over the MEU-77 files: 0 hits
```

---

## Changed Files

| File | Action | Lines | Summary |
|------|--------|-------|---------|
| `packages/core/src/avkit_core/services/tts.py` | modified | +189/−37 | `spawn`; `_admit_and_spawn`; `_work` (captures the job's WAV/MP3 paths once, R1 F1); `_finish`; `cancel`, `wait_idle`, `recover_stale_processing`, `stop_processing`; `_remove_partial` (unlinks the captured paths) |
| `packages/core/src/avkit_core/ports/storage.py` | modified | +3/−1 | `TTSJobRepository.list_by_status` |
| `packages/infrastructure/src/avkit_infra/database/repositories.py` | modified | +14/−1 | SQL `list_by_status` (oldest first) |
| `packages/infrastructure/src/avkit_infra/tts/adapter.py` | modified | +8/−6 | `PROGRESS_LAZY` |
| `packages/api/src/avkit_api/main.py` | modified | +21/−6 | lifespan recover and stop; unload/dispose only when idle |
| `packages/api/src/avkit_api/wiring.py` | modified | +7/−1 (MEU-77 hunks) | `_TTSRuntime` |
| `packages/api/src/avkit_api/routes/tts.py` | modified | +5/−2 | generate and cancel docstrings |
| `openapi.committed.json` | modified | +2/−2 (MEU-77 hunks) | regenerated (`OPENAPI_DIFF`) |
| `mcp-server/src/toolsets/tts.ts`, `mcp-server/src/index.ts` | modified | +1/−1 each | `MCP_TTS_TEXT` |
| `mcp-server/scripts/audit/plan.ts` | modified | +85/−48 | `destructiveStep` `raceLost`/`attempts` (body moved into `once`); `tts.cancel` on `tts_job2` |
| `mcp-server/scripts/audit/fixtures.ts` | modified | +3/−1 | `tts_cancel_text`; `tts_text` comment |
| `tests/unit/test_tts_async.py` | new | 1–938 | AC-77.1–77.7, 77.9, 77.11 (incl. the R1 F1 regression at :458) |
| `tests/integration/test_tts_assets.py` | modified | +159/−5 | AC-77.8, 77.10 (append); TA-9, TA-10; repair (f) with `_post_generate` |
| `mcp-server/tests/tts.test.ts` | new | 1–50 | AC-77.12 |
| `mcp-server/tests/audit/tts-cancel-step.test.ts` | new | 1–161 | AC-77.13 |
| `ui/tests/e2e/tts-generate.test.ts` | modified (append only) | +32 | AC-77.14 |
| `tests/unit/test_domain.py` | modified | +9/−1 (MEU-77 hunk) | TA-5 |
| `tests/integration/test_sqlite_uow.py` | modified | +2/−1 | TA-6 |
| `tests/unit/test_services.py` | modified | +29/−20 (MEU-77 hunks) | TA-7, TA-8; repairs (a), (b) |
| `tests/e2e/test_api_auth.py` | modified | +10/−1 (MEU-77 hunk) | repair (e) / A-7 |

```diff
-        self._current_id = job.id
-        try:
-            ...synthesize, write, convert, mark Done...
-        finally:
-            self._current_id = None
+        with self._lock:
+            if self._closing:
+                raise ConflictError("the TTS service is stopping")
+            if self._current_id is not None:
+                raise ConflictError("a TTS generation is already in progress")
+            with self._uow_factory() as uow:
+                uow.tts_jobs.add(job)
+                uow.commit()
+            self._current_id = job.id
+            self._cancel_flag = False
+        ...
+        try:
+            self._spawn(worker)
+        except Exception as exc:
+            # The worker never ran: release the reservation, then re-raise (500).
+            self._finish(job.id, TTSStatus.Failed, error=_error_text(exc))
+            raise
+        return self.get_status(job.id)
```

```diff
-        services.models.unload()
-        dispose = app.state.engine_dispose
-        if dispose is not None:
-            dispose()
+        idle = services.tts.stop_processing()
+        if idle:
+            services.models.unload()
+            dispose = app.state.engine_dispose
+            if dispose is not None:
+                dispose()
+        else:
+            # A TTS worker is still synthesizing: keep its model and database.
+            log.warning("api.shutdown_tts_busy")
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

_pending_

---

## Deferred Items

None. The Spec 03:423 edit ("generate is synchronous; re-raises" → background worker, D-19) and the 05:95 MCP text are row 12, the hub.

---

## Decision Log

```yaml
decision_log:
  - id: D-36
    stage: execution
    question: "The AC-77.10 tests hold the worker on a 5 s gate; how do their POSTs avoid racing it (repair (f))?"
    resolution: autonomous
    class: two-way
    chosen: "A non-waiting _post_generate carries the unchanged body; _generate is _post_generate plus wait_idle(5.0)"
    source_tag: Local Canon
    precedents: ["docs/execution/plans/2026-10-14-backend-robustness/implementation-plan.md:151 — FIXTURE_REPAIRS (f)"]
    research: { engine: none, sources: [] }
    reasoning: "A _generate that waits for idle would deadlock against the gate; splitting the helper changes no assertion and no request body."
  - id: D-37
    stage: execution
    question: "Which log events cover the failure paths the plan did not name?"
    resolution: autonomous
    class: two-way
    chosen: "tts.finish_failed (the terminal write raised, so _work still never raises) and tts.cleanup_failed (an unlink OSError)"
    source_tag: Local Canon
    precedents: ["packages/core/src/avkit_core/services/tts.py:340 — _finish; :371 — _remove_partial"]
    research: { engine: none, sources: [] }
    reasoning: "Both keep the worker's never-raise contract while leaving a trace; neither is emitted on a normal run."
  - id: D-38
    stage: execution
    question: "Does _finish hold _lock across the terminal DB write?"
    resolution: autonomous
    class: two-way
    chosen: "Yes: this is the plan's D-25 barrier, implemented as one critical section around the flag read, the write and the clear"
    source_tag: Local Canon
    precedents: ["docs/execution/plans/2026-10-14-backend-robustness/implementation-plan.md:620 — D-25"]
    research: { engine: none, sources: [] }
    reasoning: "A cancel racing the Done write waits, then finds no current job, so the flag cannot carry into the next run. The write is a single-row update, so the lock is held briefly."
  - id: D-39
    stage: execution
    question: "When is the 'attempt n of N' prefix added to an audit step's detail?"
    resolution: autonomous
    class: two-way
    chosen: "Only when attempts > 1"
    source_tag: Local Canon
    precedents: ["mcp-server/scripts/audit/plan.ts:287 — attempt prefix"]
    research: { engine: none, sources: [] }
    reasoning: "Every other destructive step's detail stays byte-identical, so the baseline carry and AUDIT_EXPECT comparisons are unaffected."
  - id: D-40
    stage: execution
    question: "How does reestablish recreate the tts.cancel precondition?"
    resolution: autonomous
    class: two-way
    chosen: "POST /tts/generate over REST with the generateArgs body minus action; store nothing unless 201, else report precondition_lost"
    source_tag: Local Canon
    precedents: ["mcp-server/scripts/audit/plan.ts:703 — tts.cancel reestablish"]
    research: { engine: none, sources: [] }
    reasoning: "REST is the backend contract the MCP tool wraps; a non-201 must surface as a lost precondition, not as a cancel that passed against nothing."
  - id: D-41
    stage: execution
    question: "Execution review R1 F1: which paths does Cancelled or Failed cleanup unlink?"
    resolution: autonomous
    class: two-way
    chosen: "The WAV and MP3 paths _work built once, before the WAV write; _remove_partial no longer reads tts.output_path"
    source_tag: Local Canon
    precedents: [".agent/context/handoffs/2026-10-14-backend-robustness-implementation-critical-review.md — round 1 F1", "docs/execution/plans/2026-10-14-backend-robustness/implementation-plan.md §Execution Correction Notes"]
    research: { engine: none, sources: [] }
    reasoning: "A mid-job PUT /settings/tts could otherwise redirect cleanup to a directory the job never wrote. Capturing the paths is the only fix that keeps cleanup exact; re-reading settings cannot be made correct."
  - id: D-42
    stage: execution
    question: "Is the on_progress cancel-flag read locked?"
    resolution: autonomous
    class: two-way
    chosen: "No: a single bool read, re-read under _lock by _finish before the terminal write"
    source_tag: Local Canon
    precedents: ["packages/core/src/avkit_core/services/tts.py:281 — on_progress; :340 — _finish"]
    research: { engine: none, sources: [] }
    reasoning: "The read is atomic under the GIL and is only an early-exit hint; the authoritative decision is the locked re-read in _finish (D-38)."
```

---

## History

| Event | Date | Agent | Detail |
|-------|------|-------|--------|
| Created | 2026-10-15 | claude-code | Initial handoff after gate77 |
| Corrected | 2026-10-16 | claude-code | Execution review R1 F1: cleanup uses the job's captured paths; regression `test_tts_async.py:458` (Red then Green); gate77 rerun (`s33-r1f1-gate77`) |
| Corrected | 2026-10-16 | claude-code | Decision Log rewritten as the canonical `decision_log` YAML, one entry per former bullet (D-43); final evidence points at the A-14 reruns (`s33-h1-2-audit-r3`, `s33-h1-3-windows-gate-r2`) |
