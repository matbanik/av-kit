# Round 3 review corrections: blast-radius census

Plan: `docs/execution/plans/2026-10-14-backend-robustness/implementation-plan.md`. Review: `.agent/context/handoffs/2026-10-14-backend-robustness-plan-critical-review.md` (round 3, `changes_required`, F2 open). Run on 2026-10-15 in `P:/av-kit-wt/backend-robustness`.

Scope: the six plan-local files (`implementation-plan.md`, `task.md`, `validate-task.ps1`, `exec_checks.py`, `plan_checks.py`, `baseline_carry.py`), searched with `rg -n -F` under `MSYS_NO_PATHCONV=1`. The product and test trees were also searched for `get_status` (the read the correction now covers) and `_callers` (the new name). The before receipt also sweeps the callers that use `generate`'s return value.

## Receipts (untruncated)

Both receipts are raw `rg` output with no `cut` and no filter.

- `C:/Temp/av-kit/census-backend-robustness-r3-before.txt`: every value the correction replaced, extended or re-meant, searched **before** the edit over the live files. Pre-edit copies of `implementation-plan.md` and `task.md` are in `C:/Temp/av-kit/s33-plan-pre-r3-snapshot/`, with `sha256.txt` covering every plan-folder file at that point.
- `C:/Temp/av-kit/census-backend-robustness-r3-after.txt`: the same old values plus every new value, searched after the edit.

The edit is the one-shot replacements in a scratchpad script (`fix_r3.py`; each `old` occurs exactly once, and the script writes nothing on any mismatch). A follow-up `sed` corrected one precedent range in D-31 from `tts.py:131-138` to `131-139`. No script file changed.

## Old values

| Old value | Hits before | Disposition | Hits after |
|---|---|---|---|
| `lambda: self._current_id is None, timeout` (the idle predicate) | `implementation-plan.md:131` (`ASYNC_GENERATE`) | updated: `... is None and self._callers == 0, timeout` | none |
| `once no job is reserved` | `:131` | extended: "and no `generate` call is between entry and return" | `:131` |
| `counts as busy` | `:131` | extended: a caller still in its synchronous checks, or one whose worker has finished but which has not yet read the stored row, is also busy; `_lock` is never held across `spawn` | `:131` |
| `waits on the reservation, not on a thread` | `:136` (`SHUTDOWN_STOP`) | kept and extended: "It also waits on the callers (D-31) ..." | `:136` |
| ``returns `self.get_status(job.id)` (the row as stored)`` | `:131` | confirmed-consistent: the stored-row return (D-24) is kept. It now runs inside the caller count, so the read happens before the count falls | `:131` |
| `D-8 to D-30` | `implementation-plan.md:103`; `task.md:60` | updated: `D-8 to D-31` | none |
| `AC-77.9` | `:301` (the AC); `:692` (round 1 row); `:706` (round 2 row) | `:301` updated with (g) and (h). The round 1 row (now `:702`) and the round 2 row (now `:716`) are confirmed-consistent: they record what those rounds changed | `:301`, `:702`, `:716`, and the new round 3 row `:724` |
| `D-30` | `:103` (as `D-8 to D-30`), `:131, 132, 133, 136, 301, 660, 706`; `task.md:60` | confirmed-consistent: the reservation (D-30) still holds; D-31 is added next to it at `:131, 132, 136, 301`. `:133` (`CANCEL_RULE`) is unchanged because `_finish` already notifies and the caller's `finally` makes its own notify. `:660` is D-30's own entry; `:716` is the round 2 row | `:131, 132, 133, 136, 301, 660, 716` |
| `notify_all` | `:133` | confirmed-consistent; the second notifier is the caller's `finally` | `:131` (new), `:133` |
| `_current_id is None` | `:131` | updated within the new predicate | `:131`, `:675` (D-31 `chosen`), `:724` |

## Values whose meaning changed

`wait_idle` now means "no job is reserved **and** no `generate` call is between entry and return". Every hit was re-read:

| Hit | Disposition |
|---|---|
| `implementation-plan.md:131` (`ASYNC_GENERATE`), `:136` (`SHUTDOWN_STOP`) | updated: these define the new meaning |
| `:141` TA-7 to TA-10 (`wait_idle` after the POST, then a terminal row) | confirmed-consistent: the POST has returned before the wait, so its caller count has already fallen. A `True` wait still means the reservation is clear, which happens only after the terminal write |
| `:142` `FIXTURE_REPAIRS` (f) (`stack.services.tts.wait_idle(5.0)` after the POST) | confirmed-consistent, same reason |
| `:143` `PY_SYMBOLS` | confirmed-consistent: `_callers` is private, so there is no new public name |
| `:144` `BOUNDED_WAIT` | confirmed-consistent: (g) and (h) bound every `Event.wait` and `join` at 5 s |
| `:293` AC-77.1 (`generate()` returns, then `wait_idle(5.0)` is `True`) | confirmed-consistent: the wait starts after `generate` returned |
| `:665` (D-30 `chosen`, "until it is None") | confirmed-consistent: the Decision Log keeps D-30 as decided; D-31 (`:670-679`) extends the predicate |
| `:716` (round 2 row) | confirmed-consistent: historical record |
| `:675`, `:724` | new: D-31 `chosen` and the round 3 row |
| `tests/integration/test_tts_assets.py:155` `Stack.wait_idle` and its callers | confirmed-consistent: a different method (the test stack's model-runtime poll), unchanged since round 2 |

`generate` now refuses a stopping service **at entry**, before the synchronous checks:

| Hit | Disposition |
|---|---|
| `:131` (the admission re-check, "a stop can begin after entry") | updated: the admission check stays, for a stop that begins between entry and admission (AC-77.9 (h)) |
| `:136` ("`_closing` stays set, so a `generate` after stop began raises `ConflictError` before any row is added") | confirmed-consistent: entry raises earlier still, before any collaborator call |
| `:301` AC-77.9 (d) | confirmed-consistent; (h) adds that the entry refusal makes no `get_model_status` call |
| existing tests that expect `ValidationError` or the model-not-loaded `ConflictError` (`tests/unit/test_services.py` TTS tests, `tests/integration/test_tts_assets.py`) | confirmed-consistent: none of them stops the service first, so `_closing` is `False` and the check order they see is unchanged |

## `get_status` in the plan, product and tests

| Hit | Disposition |
|---|---|
| `implementation-plan.md:131` | the read the caller count now covers |
| `:132` (`WORKER_RULE`, new sentence) | new: the caller's own last access is covered by `_callers` |
| `:293` AC-77.1 ("While the port blocks, `get_status` is `Generating`") | confirmed-consistent: a poll from the test, not the generate caller |
| `:605`, `:607` (D-24) | confirmed-consistent: the stored-row return is kept |
| `:677`, `:679` (D-31 precedent and reasoning) | new |
| `packages/core/src/avkit_core/services/tts.py:103` | confirmed-consistent: `get_status` opens a unit of work (`:104`), which is exactly the access that must come before the count falls |
| `packages/api/src/avkit_api/routes/tts.py:68` (`job = tts.generate(...)`) | confirmed-consistent: the route maps the returned row and makes no further service call |
| `packages/api/src/avkit_api/routes/tts.py:98` (`GET /tts/{id}`) | confirmed-consistent: a separate poll request, not part of a `generate` call. Like every other read route, it is outside the TTS drain |
| `tests/unit/test_services.py:1706, 1736, 1757, 1793, 1919` (`generate` return values) | confirmed-consistent: under the synchronous spawn of `FIXTURE_REPAIRS` (a) the caller count rises and falls inside each call. No test stops the service, and the `_lock` is free during `spawn`, so `cancel` from a progress callback (`:1750`) still takes it normally |
| `tests/unit/test_services.py:1915-1922` (`test_ac_12_10_get_status`) | confirmed-consistent: it reads after `generate` returned |
| `tests/unit/test_services.py:1866`, `packages/core/src/avkit_core/services/models.py:85`, `packages/api/src/avkit_api/routes/models.py:83, 107`, `tests/e2e/api_fakes.py:375` | not affected: `ModelsService.get_status` and its fake, a different method |
| `tests/e2e/api_fakes.py:326, 333` | not affected: the e2e fake TTS service, which has no threads and no shutdown |

## New values

| Value | Hits after | Note |
|---|---|---|
| `_callers` | `:131, 132, 675, 724`; product and tests: none | private name, added to `services/tts.py` in execution |
| `enters` (entry) | `:131`, `:675`, `:724` | the D-31 term. `:669` is a substring match on D-30's "re-enters `_lock`", unchanged |
| `a stop can begin after entry` | `:131` | why the admission re-check stays |
| `never held across` | `:131` | spawn stays outside `_lock` |
| `Caller drain`, AC-77.9 (g) and (h) | `:301` | the new cases |
| `R3` | `:672` (D-31 question), `:724` | |
| `D-31` | defined once (`:670`); cited at `:131, 132, 136, 301, 724`; `D-8 to D-31` at `:103` and `task.md:60` | |

No script reads `wait_idle`, `_current_id`, `_callers` or `get_status`, so the executable files need no change.

## Receipts after the corrections

`plan_checks.py static` (PASS, 24 rows), `plan_checks.py selftest` (19 of 19), `exec_checks.py selftest` (65 of 65), `lint_task_contract.py` (OK, 24 rows), the ps1 parse and `py_compile` were re-run after the edit and all exited 0. `plan_checks.py static` was run again after the precedent-range fix and exited 0.
