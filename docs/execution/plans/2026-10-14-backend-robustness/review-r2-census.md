# Round 2 review corrections: blast-radius census

Plan: `docs/execution/plans/2026-10-14-backend-robustness/implementation-plan.md`. Review: `.agent/context/handoffs/2026-10-14-backend-robustness-plan-critical-review.md` (round 2, `changes_required`, F2 open). Run on 2026-10-15 in `P:/av-kit-wt/backend-robustness`.

Scope: the six plan-local files (`implementation-plan.md`, `task.md`, `validate-task.ps1`, `exec_checks.py`, `plan_checks.py`, `baseline_carry.py`), searched with `rg -n -F` under `MSYS_NO_PATHCONV=1`. The product and test trees were also searched for `wait_idle` and `_current_id`, because the correction changes what `wait_idle` waits on.

## Receipts (regenerated untruncated)

The first version of both receipts was clipped at 200 to 220 characters by a display `cut` in the command. The round 3 attempt (refused by the ledger, no round consumed) rejected them for that under PR-6 (F9). Both are now regenerated with no `cut` and no filter. The longest records are 1,615 and 1,798 characters.

- `C:/Temp/av-kit/census-backend-robustness-r2-before.txt`: every value the correction replaced or re-meant, searched **before** the edit. The edit was the one-shot replacements in a scratchpad script (`fix_r2.py`, each `old` and `new` occurring exactly once). The pre-edit `implementation-plan.md` and `task.md` were rebuilt by applying those replacements in reverse, with each step asserting its exact single match; the four scripts did not change. **Cross-check:** rebuilt plan lines 103, 131, 132, 133, 136 and 301 each appear verbatim in the round 2 reviewer's own event log (`C:/Temp/av-kit/dispatch/s33-plan-r2/events.jsonl.gz`), which recorded the tree that round read. The product and test sweep runs on the current worktree; round 2 changed no product or test file. The receipt's header states all of this.
- `C:/Temp/av-kit/census-backend-robustness-r2-after.txt`: the same old values and every new value, searched after the edit over the current files.

`rg -F` matches substrings, so the `_idle` search also returns every `wait_idle` line; those hits are dispositioned under `wait_idle`.

## Old values

| Old value | Hits before | Disposition | Hits after |
|---|---|---|---|
| ``keeps it for `wait_idle` `` (the default spawn tracked its thread) | `implementation-plan.md:131` (`ASYNC_GENERATE`) | updated: "the thread object is not tracked"; idle is the reservation | none |
| `once no worker is running`, `no worker` (the idle condition) | `implementation-plan.md:131` | updated: `wait_idle` waits on `_idle = threading.Condition(self._lock)` until `_current_id is None` | none |
| `D-8 to D-29` | `implementation-plan.md:103`; `task.md:60` | updated: `D-8 to D-30` | none |
| ``sets `_current_id = None` `` (`_finish`'s critical section) | `implementation-plan.md:133` (`CANCEL_RULE`) | updated: it also calls `self._idle.notify_all()` | `:133` (the updated sentence) |
| `AC-77.9` | `implementation-plan.md:301` (the AC); `:682` (round 1 correction row for F2) | `:301` updated with (e) and (f); the round 1 row (now `:692`) confirmed-consistent: it records what round 1 changed and cites (b)-(d) correctly | `:301`, `:692`, and the new round 2 row `:706` |
| `D-26` | `implementation-plan.md:131, 136, 301, 620, 682` | confirmed-consistent: D-26 (the timeout result and the lifespan skip) still holds; D-30 is added next to it at `:131, 136, 301`. `:620` is D-26's own entry; `:682`/`:692` is the round 1 row | `:131, 136, 301, 620, 692` |

## Values whose meaning changed

`wait_idle` now means "no job is reserved" instead of "no worker thread is running". Every hit was re-read:

| Hit | Disposition |
|---|---|
| `implementation-plan.md:131` (`ASYNC_GENERATE`), `:136` (`SHUTDOWN_STOP`) | updated: these define the new meaning |
| `:141` TA-7, TA-8, TA-9, TA-10 ("`wait_idle`, then the row is `Failed`" or terminal) | confirmed-consistent: the reservation clears only in `_finish`, after the terminal write, so a `True` wait now guarantees a terminal row |
| `:142` `FIXTURE_REPAIRS` (f) (`stack.services.tts.wait_idle(5.0)` after the POST) | confirmed-consistent, same reason |
| `:143` `PY_SYMBOLS` (name list) | confirmed-consistent: `_idle` is private, so no new public name |
| `:144` `BOUNDED_WAIT` | confirmed-consistent: every `wait_idle` in a test still takes at most 5 s |
| `:293` AC-77.1 (`wait_idle(5.0)` is `True` and the job is `Done`) | confirmed-consistent |
| `:665`, `:706` (D-30 `chosen`; the round 2 correction row) | new: they state the new meaning |
| `tests/integration/test_tts_assets.py:155` and its 13 callers (`:225, 269, 284, 377, 405, 413, 426, 478, 511, 529, 582, 762, 769`, `Stack.wait_idle`) | confirmed-consistent: a different method (the test stack's model-runtime poll, returning the runtime state dict), not `TTSService.wait_idle` |

`_current_id` in the product and tests:

| Hit | Disposition |
|---|---|
| `packages/core/src/avkit_core/services/tts.py:88-89, 161, 166, 223` | confirmed-consistent: `_lock` is a `threading.Lock` (`:89`), which `threading.Condition` accepts; `_current_id` is already set under it at admission (`:160-166`), the D-30 precedent |
| `tests/unit/test_services.py:1750` (`service.cancel(service._current_id)` from a progress callback) | confirmed-consistent: under the synchronous spawn of `FIXTURE_REPAIRS` (a) the worker runs inside `spawn`, after `generate` released `_lock`, so `cancel` and `_finish` take the lock normally. The flag is cleared at admission, so the worker's new first flag check does not fire |
| `tests/integration/test_tts_assets.py:639` (comment: "not a 409 overlap: `_current_id` was reset") | confirmed-consistent: this is the TA-9 test; a `Failed` job's `_finish` clears the reservation, so the second POST is admitted |

No script reads `wait_idle`, `_current_id` or `_idle`, so the executable files need no change.

## New values

| Value | Hits after | Note |
|---|---|---|
| `_idle`, `threading.Condition`, `notify_all` | `:131, 133, 136`, D-30 (`:665`) and `:706` (other `_idle` hits are `wait_idle`, above) | product-side names for `services/tts.py`; no script refers to them |
| `reservation` | `:131, 136, 665, 669, 706` | the D-30 term |
| `is not tracked` | `:131` | the default spawn no longer keeps the thread |
| `first action reads the cancel flag`, `last call into any collaborator` | `:132` (`WORKER_RULE`) | tested by AC-77.9 (e); the `:706` row says it as "reads the flag before `prepare`" |
| `deferred `spawn``, AC-77.9 (e) and (f) | `:301` | the new cases |
| `D-30` | defined once (`:660`); cited at `:131, 132, 133, 136, 301, 706`; `D-8 to D-30` at `:103` and `task.md:60` | |

## Receipts after the corrections

`plan_checks.py static` (PASS, 24 rows), `plan_checks.py selftest` (19 of 19), `exec_checks.py selftest` (65 of 65), `lint_task_contract.py` (OK, 24 rows), the ps1 parse and `py_compile` were re-run after the edit and all exited 0.
