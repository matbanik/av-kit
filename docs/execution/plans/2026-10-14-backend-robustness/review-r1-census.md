# Round 1 review corrections: blast-radius census

Plan: `docs/execution/plans/2026-10-14-backend-robustness/implementation-plan.md`. Review: `.agent/context/handoffs/2026-10-14-backend-robustness-plan-critical-review.md` (round 1, `changes_required`, F1 to F8). Run on 2026-10-15 in `P:/av-kit-wt/backend-robustness`.

Scope of every search: the six plan-local files (`implementation-plan.md`, `task.md`, `validate-task.ps1`, `exec_checks.py`, `plan_checks.py`, `baseline_carry.py`). Each value was searched with `rg -n -F`, untruncated, under `MSYS_NO_PATHCONV=1`; without that, Git Bash rewrites a pattern that starts with `/`. Receipts:

- `C:/Temp/av-kit/census-backend-robustness-old.txt`: every replaced value, searched after the corrections.
- `C:/Temp/av-kit/census-backend-robustness-new.txt`: every introduced value.

## Old values

Each old value's hits before the correction, and what happened to each hit. "Remaining" is the after-correction receipt.

| Old value (finding) | Hits before | Disposition | Remaining |
|---|---|---|---|
| `{job_id}` (F7) | `implementation-plan.md:140` (`OPENAPI_DIFF`); `exec_checks.py:76` (`OPENAPI_PATHS`) | updated: both now say `/api/v1/tts/{id}`, as `openapi.committed.json:6208` names the route | none |
| `$gated` (F6) | `implementation-plan.md:146` (`GATED_PATHS` parity sentence); `validate-task.ps1:31-34` (the copy); `plan_checks.py:15, 162-163, 280` | updated: the ps1 copy is removed; the plan sentence names `GATE_EXCLUDED` in `exec_checks.py`; `plan_checks.py` compares the plan list with `ec.GATE_EXCLUDED` | `plan_checks.py:16, 165-166, 286`: confirmed-consistent (the new check that refuses a reintroduced `$gated`, and its selftest case) |
| `GATED_PATHS = [` / `ec.GATED_PATHS` / `changed_paths(baseline_sha(), GATED_PATHS)` (F6) | `exec_checks.py:46-51, 306`; `plan_checks.py:162-163` | updated: `GATE_EXCLUDED`, `is_gated`, whole-tree `changed_paths(base)` | none |
| `'docs/proposals', ` (F6 selftest mutation) | `plan_checks.py:280` | updated: the case now mutates the plan's `GATE_EXCLUDED` list ("gate exclusion added") | none |
| `GATED_PATHS` (meaning changed, F6) | `task.md:31, 58`; `implementation-plan.md:146, 147, 622` | `task.md:31` updated (adds `GATE_EXCLUDED`); `implementation-plan.md:146, 147` updated; `task.md:58` ("re-run H1-2/H1-3 after any correction that touches `GATED_PATHS`") and `implementation-plan.md:622` (gate-check binds over `GATED_PATHS`) confirmed-consistent: both read correctly with the whole-tree set | see the new census |
| `audit-fingerprint.txt` (F4) | `validate-task.ps1:326`; `exec_checks.py:509` (`v_gate_check`) | updated: `audit-fingerprint.json {before, after}`, written by `audit-fp`, read by `check_audit_fp` | none |
| `AUDIT_FINGERPRINT` (meaning changed, F4) | `task.md:31, 51`; `implementation-plan.md:148, 384` | `implementation-plan.md:148, 384` and `task.md:51` updated (before and after); `task.md:31` confirmed-consistent (a name list) | see the new census |
| `s33-baseline-prior` (F5) | `validate-task.ps1:296` (the only comparison and carry prior) | updated: it is now only the start-of-check restore copy; the comparison and the carry prior are `s33-baseline-presession.json` | `validate-task.ps1:300`; `implementation-plan.md:151`: confirmed-consistent |
| `wait_idle(10.0)` / ``stop_processing()` sets the cancel flag`` (F2) | `implementation-plan.md:136` | updated: `stop_processing(timeout: float = 10.0) -> bool` and the idle-gated lifespan | none |
| `stop_processing` (signature changed, F2) | `implementation-plan.md:136, 142, 143, 288, 300` | `:136` (`SHUTDOWN_STOP`), `:142` (`FIXTURE_REPAIRS` (e) returns `True`) and `:300` (AC-77.9) updated; `:143` (`PY_SYMBOLS`, a name list) and `:288` (call chain) confirmed-consistent; `main.py` Files Modified row updated | see the new census |
| `_finish_done` / ``Its `finally` clears `_current_id` `` (F1) | `implementation-plan.md:132` (`WORKER_RULE`) | updated: one outcome, then `_finish` exactly once in `finally` | none |
| `cancel flag` (F1) | `implementation-plan.md:132, 133, 136, 353` | `:132, 133, 136` updated (`WORKER_RULE`, `CANCEL_RULE`, `SHUTDOWN_STOP`); `:353` (Out of Scope: persisting the flag across restarts) confirmed-consistent | see the new census |
| ``gains a `precondition` that POSTs`` / `precondition` / `tts_job2` (F3) | `implementation-plan.md:139, 304` | updated: `AUDIT_CANCEL_STEP` (precondition reads `tts_job2`; `reestablish` POSTs; `raceLost`, `attempts: 3`) and AC-77.13 (a)-(d) | none of the old phrase |
| `_cancel` (substring sweep) | `implementation-plan.md:139, 141, 304, 333` | `:139, 304` updated (F3); `:141` (TA-7 `test_ac_12_5_progress_resolution_and_cancel`) and `:333` (`fixtures.ts` `tts_cancel_text` row) confirmed-consistent | see the new census |
| `D-8 to D-24` (new decisions D-25 to D-29) | `implementation-plan.md:103`; `task.md:60` | updated: both now `D-8 to D-29`. The first census pass found `task.md:60`, which the plan edit had missed, and it was fixed before the receipt above was recorded | none |
| `Re-run the doc-reading suites` (F6) | `task.md:61` (H2-2) | updated: "Re-run the suites that read the `GATE_EXCLUDED` files"; `post-review-state` adds `tests/tooling/test_framework_adoption.py` | none |

## New values

Every hit in `census-backend-robustness-new.txt` is one of the corrections above, or a cross-reference to one: the contract rows, the AC rows, the Decision Log entries D-25 to D-29, the §Round 1 Review Corrections table, and their executable copies. Each was read and is confirmed-consistent:

- `GATE_EXCLUDED`: plan `:146` and the D-29 and F6 rows; `exec_checks.py:8, 48-55, 293-294, 821`; `plan_checks.py:15, 161-164`; `validate-task.ps1:31, 515`; `task.md:31, 61`.
- `AUDIT_COMPARISON`, `s33-baseline-presession`, `audit-fingerprint.json`, `audit-fp`: plan `:148, 151, 385` and the F4 and F5 rows; `validate-task.ps1:291-335`; `exec_checks.py:17, 544, 960, 980`; `task.md:31, 51`.
- `raceLost`, `attempts`: plan `:139, 305, 333` and the D-27 and F3 rows. These are product-side names for `plan.ts`; no script refers to them.
- `_closing`, `_finish`, `stop_timeout`, `shutdown_tts_busy`, `stop_processing`: plan `:131-136, 142, 297, 301, 328` and D-25, D-26, F1 and F2. These are product-side names; no script refers to them.
- `/api/v1/tts/{id}`: plan `:140`; `exec_checks.py:81, 845, 855`.
- `same_file`: `exec_checks.py:332, 342`; the F8 row.
- `test_framework_adoption`: plan `:146`, the F6 row; `validate-task.ps1:518-519`.
- `D-25` to `D-29`: each is defined once (`implementation-plan.md:610, 620, 630, 640, 650`) and cited by its contracts, ACs and correction row. `D-8 to D-29` appears at plan `:103` and `task.md:60`.

## Receipts after the corrections

`plan_checks.py static`, `plan_checks.py selftest`, `exec_checks.py selftest`, `lint_task_contract.py`, the ps1 parse and `py_compile` were re-run after the edits. The results are in `implementation-plan.md` §Planning receipt results.
