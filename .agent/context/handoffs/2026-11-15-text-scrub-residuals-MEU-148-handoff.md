---
date: "2026-11-15"
project: "2026-11-15-text-scrub-residuals"
meu: "MEU-148"
status: "complete"
action_required: "VALIDATE_AND_APPROVE"
template_version: "2.2"
verbosity: "standard"
plan_source: "docs/execution/plans/2026-11-15-text-scrub-residuals/implementation-plan.md"
build_plan_section: "bp03"
agent: "claude-code-local (Claude Opus 5.5)"
reviewer: "codex (H1-7 execution review)"
predecessor: "MEU-147 (2026-11-15-text-scrub-residuals-MEU-147-handoff.md)"
---

# Handoff: 2026-11-15-text-scrub-residuals-MEU-148-handoff

> **Status**: `complete`
> **Action Required**: `VALIDATE_AND_APPROVE`

---

## Scope

**MEU**: MEU-148 `svc-console-home-short-form` (issue `CONSOLE-HOME-SCRUB-SHORT-FORM`, triage D-805, Mat's D-337). On Windows a Console field and a download log line also turn the home folder's 8.3 short form into `~`. The short form is read once per home value and cached, and a failed lookup keeps today's long-form-only result.
**Build Plan Section**: [03 §Console home short form (residual)](../../../docs/build-plan/03-service-layer.md#console-home-short-form-residual) (matrix 3.23), with the Delivered (Session 77) note under it (`03-service-layer.md:777`).
**Predecessor**: MEU-147 (same session; `2026-11-15-text-scrub-residuals-MEU-147-handoff.md`).

- **D-337 as applied.** Mat's ruling (Session 52, `docs/execution/plans/2026-11-06-tts-load-fp16/closeout-decisions.md:55-88`) is carried out as given: the short form comes from `GetShortPathNameW`, Windows only, read once and cached, faked in tests, and when the call fails only the long form is matched. This MEU makes no new ruling on it.
- **SHORT_FORM_LOOKUP (D-926).** A module flag, `sys.platform == "win32"`, beside `HOME_IGNORES_CASE` (`packages/core/src/avkit_core/services/health.py:68`), read at call time.
- **SHORT_PATH_API (D-927).** `_short_path_api()` (`health.py:118`) returns the native `GetShortPathNameW` callable, loaded through `ctypes` inside an `if sys.platform == "win32":` block with `argtypes` `[LPCWSTR, LPWSTR, DWORD]` and `restype` `DWORD` (the `avkit_api/cli.py:28-55` shape). It returns `None` off Windows and when loading raises `OSError` or `AttributeError`. It does no lookup; it is the seam AC-148.8 and AC-148.9 replace.
- **SHORT_PATH_NAME (D-337, D-926, D-927).** `short_path_name(path)` (`health.py:137`) makes the size query, allocates `ctypes.create_unicode_buffer(size)` and fills it; it returns `buffer.value` only when the size is non-zero and the fill returns `0 < written < size`, and `""` otherwise, including on an `OSError` or `ValueError`.
- **SHORT_FORM_CACHE (D-337, D-926).** `home_forms()` (`health.py:161`) returns the home folder without trailing separators, then its short form when that is non-empty and differs in casefold. The lookup runs at most once per home value per process; the result, `""` included, is kept in `_SHORT_FORMS` (`:114`), keyed by the long form, under `_SHORT_FORMS_LOCK` (`:115`, used at `:174`). With `SHORT_FORM_LOOKUP` false no lookup runs; an empty home gives `()`.
- **SHORT_FORM_SCRUB (D-337).** `scrub_home` (`health.py:183`) applies its existing pattern to each form of `home_forms()`, long form first, with the same boundary and case rules (D-335). A form with no separator is skipped, as before.
- **SHORT_FORM_SPLIT (D-925).** `download._scrub_split_home` (`packages/core/src/avkit_core/services/download.py:107`) applies its existing split-aware pattern to each form of `health.home_forms()`, read through the module at each call, so `scrub_line` (`:135`) matches a short form split by a tab, a control character or an ANSI sequence.
- **The native-callable proof and its mutant (D-927).** AC-148.8 runs the real `short_path_name` over a fake native callable and checks the two calls in order and that the result reaches `console_field`. The plan-local plugin `mutant_empty_lookup.py` replaces `short_path_name` with `lambda _path: ""`; under it both AC-148.8 tests fail by assertion (`tsr-148-mutant.txt`: `2 failed, 16 deselected in 0.06s`, with `assert '' == 'C:\\Users\\SYNTHE~1'`), and `tsr-148-mutant-check.txt` reads `red-check: 1 receipt(s), 1 required test(s), 0 problem(s)`. So an always-empty helper cannot pass (plan review R1-F1).
- **AC-148.1's real lookup on this PC, as booleans only** (`tsr-148-real-lookup.txt`): `api loads: True`; `home has a distinct short form: False`; `home_forms count: 1`. So on this PC the home folder has no 8.3 short form, and the real call returns without breaking. No real home path, long or short, is written in this handoff or in any receipt it quotes.
- **Spec text and records (row 5).** The Delivered (Session 77) note in 03; the issue resolved through the plan's `issue-resolve.py` (`tsr-issue-resolve.txt`: `issue-resolve: 0 problem(s)`); MEU-148 `ready_for_review` (`tsr-status-148.txt`).

**Where values go (D-421, `NO_RAW_CONSOLE`).** The tests use the synthetic home `C:\Users\SYNTHETIC_HOME_USER` (the D-335 fixture, `test_services.py:3308`) and the synthetic short form `C:\Users\SYNTHE~1`; no test reads or writes the real home folder. AC-148.1 uses a folder under `tmp_path` and a missing synthetic path.

**Plan:** [implementation-plan.md](../../../docs/execution/plans/2026-11-15-text-scrub-residuals/implementation-plan.md) §MEU-148. **Execution authorization:** `USER_EXPLICIT`, 2026-11-15, "proceed with planning and execution for P:\av-kit\.agent\context\grouping\2026-11-15-post-rc3-triage-residuals-session-grouping.md like we did here. But use the new HDP process. Continue orchestrating the sessions." The plan review approved at round 2 ([plan-critical-review.md](2026-11-15-text-scrub-residuals-plan-critical-review.md)); `plan_to_exec_gate: human`. The coordinator wrote these words into the plan's Status line (line 15) before row 0; that is a plan-text edit made after the plan was approved, disclosed here.

**Receipts.** A receipt named by its file name alone is in the session's receipts folder (`RECEIPTS_DIR`, the plan's `text-scrub-residuals` folder under it). Full paths appear only in the evidence records' `command` fields.

---

## Acceptance Criteria

| AC | Type | Description | Source | Test(s) | Status |
|----|------|-------------|--------|---------|--------|
| AC-148.1 | unit | The real native path, without any fake. On Windows, `_short_path_api()` returns a callable; for a folder under `tmp_path` named `LongFolderNameForShortForm`, `short_path_name` returns `""` or a path for which `os.path.samefile` holds; for a missing synthetic path it returns `""`. Off Windows (`sys.platform` patched to `linux` in `health`'s view), `_short_path_api()` returns `None` and `short_path_name` returns `""`. No skip. | Research-backed (`GetShortPathNameW`; plan-time probe); Human-approved (D-337 "Windows only") | `tests/unit/test_console_home_short_form.py:102` | ✅ |
| AC-148.2 | unit | With the fake returning the synthetic short form, `console_field` turns it into `~` when it starts a path joined by `\`, `/` and a doubled `\\`, and in lower case. `C:\Users\SYNTHE~10\a` and `X:\Users\SYNTHE~1` with a word character before it are kept (the D-335 boundary). `scrub_home` gives the same results. | Human-approved (D-337) | `tests/unit/test_console_home_short_form.py:133` | ✅ |
| AC-148.3 | unit | The lookup is read once and cached: across several `console_field`, `scrub_home` and `scrub_line` calls the fake runs once, with the long home; a fake that returns `""` also runs once; a second home value runs its own lookup once. | Human-approved (D-337 "read once and cached"); Local Canon (D-926) | `tests/unit/test_console_home_short_form.py:141` | ✅ |
| AC-148.4 | unit | A failed lookup (`""`), and a lookup that returns the long form in another case, leave `scrub_home` output equal to the long-form-only result for a fixed corpus of five lines; a short-form path in that corpus is kept. | Human-approved (D-337: "only the long form is matched") | `tests/unit/test_console_home_short_form.py:183` | ✅ |
| AC-148.5 | unit | With `SHORT_FORM_LOOKUP` false, the fake never runs, the short form is kept and the long form still becomes `~`. | Human-approved (D-337 "Windows only") | `tests/unit/test_console_home_short_form.py:192` | ✅ |
| AC-148.6 | unit | One line that names the long form and the short form gives `~` for both, and the existing AC-119.10 tests pass unchanged (`pytest tests/unit/test_services.py -k ac_119_10`). | Local Canon (AC-119.10, D-335) | `tests/unit/test_console_home_short_form.py:200`; `tests/unit/test_services.py:3322`, `:3344`, `:3355` (`tsr-148-ac119.txt`) | ✅ |
| AC-148.7 | unit | `scrub_line` turns the short form into `~` when it is plain, and when a tab, a control character (U+0001) or an ANSI CSI sequence splits the short name (D-627's shape). With a failed lookup the split short form is kept exactly as today's `scrub_line` keeps it. | Local Canon (03 §Console home short form: Reach; D-627; D-925) | `tests/unit/test_console_home_short_form.py:220` | ✅ |
| AC-148.8 | unit | The real `short_path_name` over a fake native callable: the default script gives `short_path_name(long) == "C:\Users\SYNTHE~1"`, with exactly two calls in order, `(long, None, 0)` then `(long, buffer, len(alias) + 1)`; with the same fake, `SHORT_FORM_LOOKUP` true and a fresh `_SHORT_FORMS`, `home_forms()` is `(long, alias)` and `console_field` turns `C:\Users\SYNTHE~1\a` into `~\a`. Under the empty-lookup mutant every AC-148.8 test fails by assertion. | Research-backed (`GetShortPathNameW` contract); Human-approved (D-337: faked in tests); Local Canon (D-927; review R1-F1) | `tests/unit/test_console_home_short_form.py:229`, `:239`; mutant `tsr-148-mutant.txt` | ✅ |
| AC-148.9 | unit | The real `short_path_name` over failing fake native callables; each gives `""`, and with it `console_field` keeps `C:\Users\SYNTHE~1\a`: size query 0 (one call, no fill), fill 0, fill equal to `size`, an `OSError` from the callable, and `_short_path_api()` returning `None` (no call at all). | Research-backed (the same contract); Human-approved (D-337: "when the call fails … only the long form is matched") | `tests/unit/test_console_home_short_form.py:281` | ✅ |
| AC-119.10 (cross-ref) | guard | The long-form scrub (D-335): the AC-119.10 tests pass unchanged with no fake lookup, since a synthetic home does not exist and the real call returns `""`; they are the regression half of AC-148.6 | MEU-119 | `tests/unit/test_services.py:3322`, `:3344`, `:3355`, `:3368`, `:3383`, `:3393` | ✅ |
| AC-147 (sibling) | sibling MEU | AC-147.1, AC-147.2, AC-147.3, AC-147.4, AC-147.5, AC-147.6: the transcript title cleaning, evidenced in the MEU-147 handoff, which also carries the AC-122 cross-reference | MEU-147 | `2026-11-15-text-scrub-residuals-MEU-147-handoff.md` | ✅ |

<!-- CACHE BOUNDARY -->

---

## Evidence

### FAIL_TO_PASS

| Test | Red Output (hash/snippet) | Green Output | File:Line |
|------|---------------------------|--------------|-----------|
| AC-148.1 | `AssertionError: assert False` / `where False = hasattr(health, 'home_forms')` (`tsr-148-red.txt`) | Row 4: pass (`tsr-148-green.txt`) | `test_console_home_short_form.py:102` |
| AC-148.2, AC-148.3 | the same assertion | Row 4: pass | `test_console_home_short_form.py:133`, `:141` |
| AC-148.4 | the same assertion (2 cases: `failed-lookup`, `long-form-other-case`) | Row 4: pass | `test_console_home_short_form.py:183` |
| AC-148.5, AC-148.6 | the same assertion | Row 4: pass | `test_console_home_short_form.py:192`, `:200` |
| AC-148.7 | the same assertion (4 cases: `plain`, `tab`, `control`, `ansi`) | Row 4: pass | `test_console_home_short_form.py:220` |
| AC-148.8 | the same assertion (2 tests) | Row 4: pass | `test_console_home_short_form.py:229`, `:239` |
| AC-148.9 | the same assertion (5 cases: `size-query-zero`, `fill-zero`, `fill-does-not-fit`, `os-error`, `no-api`) | Row 4: pass | `test_console_home_short_form.py:281` |

- **Row 3 Red** (`tsr-148-red.txt`): `18 failed in 0.26s`; each case fails at its first line, `hasattr(health, 'home_forms')`, before any patch, so Red is by assertion and never by `AttributeError` in setup (Session 52 RULE-4). `tsr-148-red-check.txt`: `red-check: 1 receipt(s), 9 required test(s), 0 problem(s)`. `tsr-148-mutant-file.txt`: `mutant plugin present: True`.
- **The mutant run is a second negative, not a Red case:** at row 4, with Green code, `-p mutant_empty_lookup -k ac_148_8` gives `2 failed, 16 deselected in 0.06s` (`tsr-148-mutant.txt`; its `.exit` is `1`) and the red-check on it reads `0 problem(s)` (`tsr-148-mutant-check.txt`). The gate repeats it (`meu-148-mutant`, `meu-148-mutant-check`).
- **Not in FAIL_TO_PASS:** the AC-119.10 tests run unchanged (`tsr-148-ac119.txt`: `10 passed, 108 deselected in 0.14s`), and so do the scrub callers (`tsr-148-callers.txt`: `84 passed in 0.93s`).

### Commands Executed

```json
{"schema_version": "evidence.v1", "cwd": "P:/av-kit", "check_id": "tsr-0-baseline", "command": "pwsh -NoProfile -File C:/Temp/av-kit/text-scrub-residuals/run-row0.ps1 (task.md row 0's Validation cell: rtk proxy pwsh -NoProfile -File docs/execution/plans/2026-11-15-text-scrub-residuals/baseline.ps1 *> C:/Temp/av-kit/text-scrub-residuals/tsr-baseline.txt, with ELECTRON_RUN_AS_NODE unset); receipts tsr-baseline.txt, tsr-base-py.txt", "scope": "Row 0: baseline.sha, baseline-dirty.txt, baseline-scope.json, baseline-dirty-hashes.json and baseline-eol.json; the row-0 copies of red-check.py, identity.py and issue-resolve.py; the base Python suite; the red-check and identity selftests; the S4 scope check for row 1 and the line-ending check", "phase": "static", "exit_code": 0, "result": "pass", "tested_state": "HEAD ab761dd (baseline.sha), before row 1", "output": "tsr-baseline.txt: baseline-dirty.txt 51 paths; baseline-scope.json 14 paths; 2 absent; baseline-dirty-hashes.json 6 paths outside this scope; red-check selftest: 37 fixture(s) (12 positive, 25 negative), 0 wrong: []; identity selftest: 0 failure(s); scope-check: ok; baseline: all steps exit 0. tsr-base-py.txt: 2945 passed, 37 warnings in 297.28s (0:04:57)"}
```

```json
{"schema_version": "evidence.v1", "cwd": "P:/av-kit", "check_id": "tsr-3-red-148", "command": "pwsh -NoProfile -File C:/Temp/av-kit/text-scrub-residuals/run-row3.ps1 (task.md row 3's Validation cell: uv run pytest tests/unit/test_console_home_short_form.py --tb=short -q *> C:/Temp/av-kit/text-scrub-residuals/tsr-148-red.txt, its exit code to tsr-148-red.txt.exit, red-check.py --require test_ac_148_1 to test_ac_148_9, then the mutant-plugin check); receipts tsr-148-red.txt, tsr-148-red-check.txt, tsr-148-mutant-file.txt, tsr-s4-row3.txt", "scope": "MEU-148 Red: AC-148.1 to AC-148.9 against the row-0 product code, after the S4 check, and the mutant plugin written", "phase": "red", "exit_code": 0, "result": "pass", "tested_state": "HEAD ab761dd plus rows 0 to 3", "output": "tsr-s4-row3.txt: scope-check: ok. tsr-148-red.txt: 18 failed in 0.26s, each AssertionError: assert False where False = hasattr(health, 'home_forms'); tsr-148-red.txt.exit 1. tsr-148-red-check.txt: red-check: 1 receipt(s), 9 required test(s), 0 problem(s). tsr-148-mutant-file.txt: mutant plugin present: True"}
```

```json
{"schema_version": "evidence.v1", "cwd": "P:/av-kit", "check_id": "tsr-4-green-148", "command": "pwsh -NoProfile -File C:/Temp/av-kit/text-scrub-residuals/run-row4.ps1 (task.md row 4's Validation cell: uv run pytest tests/unit/test_console_home_short_form.py -rs with a SKIPPED refusal, uv run pytest tests/unit/test_services.py -k ac_119_10, the scrub callers test_download_failure_visibility.py and test_download_audio_extract.py, then with PYTHONPATH at the plan folder uv run pytest -p mutant_empty_lookup tests/unit/test_console_home_short_form.py -k ac_148_8 > tsr-148-mutant.txt with its .exit, red-check.py --require test_ac_148_8 on it, and the line-ending check); receipts tsr-148-green.txt, tsr-148-ac119.txt, tsr-148-callers.txt, tsr-148-mutant.txt, tsr-148-mutant-check.txt, tsr-148-eol.txt, tsr-s4-row4.txt", "scope": "MEU-148 Green: SHORT_FORM_LOOKUP, SHORT_PATH_API, SHORT_PATH_NAME, SHORT_FORM_CACHE, SHORT_FORM_SCRUB and SHORT_FORM_SPLIT, with AC-119.10 and the scrub callers unchanged and the empty-lookup mutant refused", "phase": "green", "exit_code": 0, "result": "pass", "tested_state": "HEAD ab761dd plus rows 0 to 4", "output": "tsr-s4-row4.txt: scope-check: ok. tsr-148-green.txt: 18 passed in 0.16s (no SKIPPED); tsr-148-ac119.txt: 10 passed, 108 deselected in 0.14s; tsr-148-callers.txt: 84 passed in 0.93s; tsr-148-mutant.txt: 2 failed, 16 deselected in 0.06s (assert '' == 'C:\\\\Users\\\\SYNTHE~1'), .exit 1; tsr-148-mutant-check.txt: red-check: 1 receipt(s), 1 required test(s), 0 problem(s); tsr-148-eol.txt: line-ending drift: []"}
```

```json
{"schema_version": "evidence.v1", "cwd": "P:/av-kit", "check_id": "tsr-4-real-lookup", "command": "PYTHONIOENCODING=utf-8 uv run --no-sync python -c (prints whether health._short_path_api() is not None, whether short_path_name of the home folder is non-empty and differs from it in casefold, and len(health.home_forms())) > C:/Temp/av-kit/text-scrub-residuals/tsr-148-real-lookup.txt 2>&1", "scope": "AC-148.1's real lookup on this PC, recorded as booleans and a count only, so no home path is written", "phase": "runtime", "exit_code": 0, "result": "pass", "tested_state": "HEAD ab761dd plus rows 0 to 4", "output": "tsr-148-real-lookup.txt: api loads: True; home has a distinct short form: False; home_forms count: 1. The receipt's first line is a SyntaxWarning (invalid escape sequence) from the probe's own -c string, not from the product code"}
```

```json
{"schema_version": "evidence.v1", "cwd": "P:/av-kit", "check_id": "tsr-5-close", "command": "pwsh -NoProfile -File C:/Temp/av-kit/text-scrub-residuals/run-row5.ps1 (task.md row 5's Validation cell: issue-resolve.py --issue TRANSCRIPT-UNCLEANED-TITLE-FALLBACKS --issue CONSOLE-HOME-SCRUB-SHORT-FORM --set-file C:/Temp/av-kit/text-scrub-residuals/issue-resolve-set.json --expect-sha256 <row-0 hash>, issue_triage.py render and render --check, meu_status.py update MEU-147 and MEU-148 ready_for_review, meu_status.py render, then the row-5 check); receipts tsr-issue-resolve.txt, tsr-issues-render.txt, tsr-issues-render-check.txt, tsr-status-147.txt, tsr-status-148.txt, tsr-status-render.txt, tsr-row5-check.txt, tsr-s4-row5.txt", "scope": "Row 5: the two Delivered (Session 77) notes in 03 (CRLF), both issues resolved, both MEUs ready_for_review, grouping row 77 executed", "phase": "static", "exit_code": 0, "result": "pass", "tested_state": "HEAD ab761dd plus rows 0 to 5", "output": "tsr-issue-resolve.txt: issue-resolve: 0 problem(s); tsr-issues-render.txt: Rendered known-issues.md: 60 lines; tsr-issues-render-check.txt: OK: known-issues.md is up-to-date; tsr-status-148.txt: Updated MEU-148 to ready_for_review (updated: 2026-11-15); tsr-status-render.txt: Loaded 153 MEUs across 12 phases; tsr-row5-check.txt: row 77 executed (Session 77), grouping LF: True 03 CRLF: True notes: 2"}
```

```json
{"schema_version": "evidence.v1", "cwd": "P:/av-kit", "check_id": "tsr-h1-1-unchecked", "command": "pwsh -NoProfile -File C:/Temp/av-kit/text-scrub-residuals/run-h1-1.ps1 (task.md H1-1's Validation cell) *> C:/Temp/av-kit/text-scrub-residuals/task-unchecked.txt", "scope": "H1-1: no implementation row of task.md is unchecked", "phase": "static", "exit_code": 0, "result": "pass", "tested_state": "HEAD ab761dd plus rows 0 to 5", "output": "task-unchecked.txt: unchecked implementation rows: []"}
```

```json
{"schema_version": "evidence.v1", "cwd": "P:/av-kit", "check_id": "tsr-gate-h1-2", "command": "pwsh -NoProfile -File C:/Temp/av-kit/text-scrub-residuals/run-h1-2.ps1 (task.md H1-2's Validation cell: rtk proxy pwsh -NoProfile -File docs/execution/plans/2026-11-15-text-scrub-residuals/session-gate.ps1 *> C:/Temp/av-kit/text-scrub-residuals/tsr-gate-h1.txt, with ELECTRON_RUN_AS_NODE unset); receipts tsr-gate-h1.txt and the tsr-D6-*.txt step receipts", "scope": "H1-2 session gate for MEU-147 and MEU-148: identity before and after, ruff check and format, pyright, the task contract, scope paths, line endings, the red-check selftest, the MEU-147 tests and the MEU-122 adapter tests, the MEU-148 tests with no skip, AC-119.10, the empty-lookup mutant and its red-check, the scrub callers, the full Python suite, the state and issue renders and the UI canon", "phase": "full", "fresh": true, "snapshot": false, "exit_code": 0, "result": "pass", "tested_state": "ab761ddd5cc47cb014e80450be1e80c0825c984f+e7c60e3a25531c47ba7e950292591af393053446561e32e97d1731d07e2e0e4d", "output": "tsr-gate-h1.txt: session-gate: all steps exit 0; tested_state before = after (tsr-D6-identity-before.txt, tsr-D6-identity-after.txt). py-lint All checks passed!; py-format 7 files already formatted; py-types 0 errors, 0 warnings, 0 informations; task-contract OK: 23 row(s), 21 fully checked, 2 view_file exempt (H1-5, H2-1); scope-paths scope-check: ok (other-session-plan 39, plan-or-closeout 15, baseline-dirty-hashes checked 6); line-endings scope-check: ok; red-check-selftest 37 fixture(s) (12 positive, 25 negative), 0 wrong; meu-147-tests 35 passed in 2.64s; meu-147-adapter 6 passed, 31 deselected in 0.82s; meu-148-tests 18 passed in 1.12s; meu-148-ac119 10 passed, 108 deselected in 0.37s; meu-148-mutant must fail: pytest exit=1, 2 failed, 16 deselected in 0.07s; meu-148-mutant-check red-check: 1 receipt(s), 1 required test(s), 0 problem(s); scrub-callers 100 passed in 3.08s; py-tests (tsr-D6-py-tests.txt) 2982 passed, 37 warnings in 527.72s (0:08:47), the row-0 base 2945 plus 19 MEU-147 and 18 MEU-148 tests; state-render Drift check passed (153 MEUs, 12 phases); issues-render-check OK: known-issues.md is up-to-date; ui-canon Test Files 2 passed (2), Tests 14 passed (14). Attempt 1 (tsr-gate-h1-attempt1.txt) stopped at meu-148-mutant-check: no readable child exit code in tsr-D6-meu-148-mutant.txt.exit, a gate-script defect fixed in session-gate.ps1's MustFail block before the rerun"}
```

```json
{"schema_version": "evidence.v1", "cwd": "P:/av-kit", "check_id": "tsr-h1-3-status", "command": "pwsh -NoProfile -File C:/Temp/av-kit/text-scrub-residuals/run-h1-3.ps1 (task.md H1-3's Validation cell: meu_status.py render --check, meu_status.py get MEU-147 and MEU-148, then the ready_for_review check); receipts tsr-render-check.txt, tsr-h13-status-147.txt, tsr-h13-status-148.txt, tsr-h13-check.txt", "scope": "H1-3: row 5's status writes hold, with no new write after the gate; the current-focus paragraph", "phase": "static", "exit_code": 0, "result": "pass", "tested_state": "the gate's tested_state (current-focus.md is an identity artifact)", "output": "tsr-render-check.txt: Drift check passed (153 MEUs, 12 phases); tsr-h13-status-147.txt and tsr-h13-status-148.txt: status ready_for_review; tsr-h13-check.txt: MEU-147 and MEU-148 ready_for_review: True. The Session 77 paragraph heads current-focus.md, which stays CRLF (179 CRLF, 0 bare LF)"}
```

```json
{"schema_version": "evidence.v1", "cwd": "P:/av-kit", "check_id": "tsr-h1-4-openapi", "command": "pwsh -NoProfile -File C:/Temp/av-kit/text-scrub-residuals/run-h1-4.ps1 (task.md H1-4's Validation cell) *> C:/Temp/av-kit/text-scrub-residuals/openapi-check.txt", "scope": "H1-4: packages/api has no change since baseline.sha, so the OpenAPI check is skipped on that basis", "phase": "static", "exit_code": 0, "result": "pass", "tested_state": "the gate's tested_state", "output": "openapi-check.txt: packages/api changes: []"}
```

### Quality Gate Results

- **Last line** (`tsr-gate-h1.txt`): `session-gate: all steps exit 0`.
- **Identity:** tested_state `ab761ddd5cc47cb014e80450be1e80c0825c984f+e7c60e3a25531c47ba7e950292591af393053446561e32e97d1731d07e2e0e4d` before and after the gate (`tsr-D6-identity-before.txt`, `tsr-D6-identity-after.txt`).
- **Static:** ruff check `All checks passed!`; ruff format `7 files already formatted`; pyright `0 errors, 0 warnings, 0 informations`; the task contract `OK: 23 row(s); 21 fully checked; 2 view_file exempt (H1-5, H2-1)`; scope paths and line endings `scope-check: ok`; the red-check selftest `37 fixture(s) (12 positive, 25 negative), 0 wrong`.
- **Suites:** MEU-147 `35 passed`; the MEU-122 adapter tests `6 passed, 31 deselected`; MEU-148 `18 passed` with no skip; AC-119.10 `10 passed, 108 deselected`; the empty-lookup mutant fails as it must (`2 failed, 16 deselected`, exit 1) and its red-check reports `0 problem(s)`; the scrub callers `100 passed` (84 callers and 16 metadata); the full Python suite `2982 passed, 37 warnings in 527.72s` (`tsr-D6-py-tests.txt`), which is the row-0 base of 2945 plus the 19 MEU-147 and 18 MEU-148 tests; the state render `Drift check passed`; the issue render `OK: known-issues.md is up-to-date`; the UI canon `Tests 14 passed (14)`.
- **Skipped, with basis:** ui-lint, ui-types and ui-tests (nothing under `ui/` changes); the MCP steps (no MCP change); E2E (no renderer change); OpenAPI (no `packages/api` change, H1-4 `openapi-check.txt`); build-record (no build).
- **Baseline failures excused:** 0.
- **First attempt:** `tsr-gate-h1-attempt1.txt` stopped at `meu-148-mutant-check` (`no readable child exit code in tsr-D6-meu-148-mutant.txt.exit`). The mutant itself had failed as required; the gate's MustFail block wrote no `.exit` file. That is a defect in the plan-local `session-gate.ps1`, not a flake, and the block now writes it (`Set-Content "$receipt.exit" $code`). The attempt's receipts are kept as `*-attempt1.txt`; the rerun above passed every step.
- **After the gate:** H1-3 added the current-focus paragraph, task.md rows were marked, and these handoffs were written. `identity.py` excludes all three, so no product, test or tracked record changed after the gate; H1-6b checks that the expected state still equals the gate's.

---

## Changed Files

All counts are `git diff ab761dd --numstat`; line endings were measured as bytes before and after (`tsr-eol-final.txt`: `line-ending drift: []` over 20 files).

| File | Change | Added / removed | Line endings |
|------|--------|-----------------|--------------|
| `packages/core/src/avkit_core/domain/download.py` | MEU-147: `_UNCLEAN_CATEGORIES` and `clean_text` (D-922) | +20 / -0 | CRLF kept |
| `packages/infrastructure/src/avkit_infra/youtube/adapter.py` | MEU-147: imports `clean_text`; the copy, its categories and `import unicodedata` removed; two D-930 layout hunks | +6 / -29 | CRLF kept |
| `packages/core/src/avkit_core/services/transcript.py` | MEU-147: the channel and result-title fallbacks (D-923) | +7 / -6 | LF kept |
| `packages/core/src/avkit_core/services/health.py` | MEU-148: `short_path_name`, `home_forms` and its cache and lock, the short form in `scrub_home` (D-926, D-927, D-337) | +87 / -10 | CRLF kept |
| `packages/core/src/avkit_core/services/download.py` | MEU-148: `_scrub_split_home` loops over `home_forms` (D-925); four D-930 layout hunks | +16 / -21 | CRLF kept |
| `tests/unit/test_transcript_title_cleaning.py` | new: AC-147.1 to AC-147.5 | +250 (new) | LF |
| `tests/unit/test_console_home_short_form.py` | new: AC-148.1 to AC-148.9 | +291 (new) | LF |
| `docs/build-plan/03-service-layer.md` | the two Delivered (Session 77) notes (`:757`, `:777`) | +14 / -0 | CRLF kept |
| `docs/BUILD_PLAN.md` | the rendered MEU status | +1 / -1 | LF kept |
| `.agent/context/meu-status.yaml` | MEU-147 and MEU-148 `ready_for_review` (through `tools/meu_status.py`) | +8 / -8 | LF kept |
| `.agent/context/meu-registry.md` | the rendered registry | +2 / -2 | LF kept |
| `.agent/context/known-issues.yaml` | both issues resolved (through the plan's `issue-resolve.py`) | +10 / -5 | LF kept |
| `.agent/context/known-issues.md` | the rendered issue list (`tools/issue_triage.py render`) | +3 / -5 | LF kept |
| `.agent/context/grouping/2026-11-15-post-rc3-triage-residuals-session-grouping.md` | row 77 `executed` | +1 / -1 | LF kept |
| `.agent/context/current-focus.md` | the Session 77 paragraph (H1-3) | +3 / -0 | CRLF kept |

Plan-local files (in the plan folder): `mutant_empty_lookup.py` (16 lines, the AC-148.6 mutant plugin), `scope-check.py` (D-929), the row-0 records (`baseline.sha`, `baseline-dirty.txt`, `baseline-scope.json`, `baseline-dirty-hashes.json`, `baseline-eol.json`) and the row-0 copies of `red-check.py`, `identity.py` and `issue-resolve.py`; `session-gate.ps1` gained the MustFail `.exit` line. These two handoffs are new. Nothing is committed or staged.

---

## Codex Validation Report

### Recheck Protocol

1. Read Scope + AC table
2. Verify each AC against Evidence section (file:line, not memory)
3. Independently probe the claimed behavior and compare decisive output
4. Verify the full gate is fresh and matches current D6 inputs; rerun if changed or unproven
5. Record findings below

### Findings

| # | Severity | Blocking | Finding | Fix | Status |
|---|----------|----------|---------|-----|--------|

Round 1 (dispatch `tsr-exec-r1`) approved with no finding: `findings_count: 0`, intent achieved `yes`, and the ledger recorded `blocking=0`. The reviewer's tested_state is `ab761ddd5cc47cb014e80450be1e80c0825c984f+e7c60e3a25531c47ba7e950292591af393053446561e32e97d1731d07e2e0e4d`, the gate's exactly; it reproduced the host's ignore of `.claude/settings.local.json` with a temp-only exclude file and never opened that file. It accepted D-922 to D-927 as fixed, and D-928 to D-930 against their code and receipts (for D-930, a whole-module AST comparison shows the six extra hunks are layout only). Its IR-5 audit rates 17 of the 18 new test functions Strong and AC-148.1's native-volume smoke Adequate, with no Weak test. For this MEU the reviewer accepted Q2 and Q3 (AC-148.1 to AC-148.9), with 16-thread probes recording exactly one lookup, and the empty-lookup mutant failing at `test_console_home_short_form.py:232` and `:243`. It names one residual risk, not a finding: the first short-path lookup is synchronous and runs under `_SHORT_FORMS_LOCK` with no timeout, so a concurrent scrub waits for it; no indefinite lookup or lock cycle was reproduced. It also notes that a volume may expose no distinct 8.3 alias, so success is proven over a fake native callable beside the real temp-folder smoke. The canonical rolling report is `.agent/context/handoffs/2026-11-15-text-scrub-residuals-implementation-critical-review.md`, byte-equal to the round-1 report.

```json
{"schema_version": "evidence.v1", "cwd": "P:/av-kit", "check_id": "tsr-h1-7a-review-state", "command": "rtk proxy uv run python tools/validate_closeout_artifacts.py --review .agent/context/handoffs/2026-11-15-text-scrub-residuals-implementation-critical-review.md --review-state-only --expected-review-mode execution --expected-target-plan docs/execution/plans/2026-11-15-text-scrub-residuals/implementation-plan.md --max-review-rounds 6 --output C:/Temp/av-kit/text-scrub-residuals/review-state.json *> C:/Temp/av-kit/text-scrub-residuals/review-state-check.txt", "scope": "H1-7a: the canonical execution review parsed to its target-bound state", "phase": "static", "exit_code": 0, "result": "pass", "tested_state": "ab761ddd5cc47cb014e80450be1e80c0825c984f+e7c60e3a25531c47ba7e950292591af393053446561e32e97d1731d07e2e0e4d", "output": "review-state-check.txt: OK: review_mode=execution; round 1 of 6; verdict=approved; open findings=0; state receipt written to review-state.json"}
```

```json
{"schema_version": "evidence.v1", "cwd": "P:/av-kit", "check_id": "tsr-h1-7b-approval", "command": "rtk proxy uv run python tools/validate_closeout_artifacts.py --review .agent/context/handoffs/2026-11-15-text-scrub-residuals-implementation-critical-review.md --approved-state-only --review-state-receipt C:/Temp/av-kit/text-scrub-residuals/review-state.json --expected-review-mode execution --expected-target-plan docs/execution/plans/2026-11-15-text-scrub-residuals/implementation-plan.md --max-review-rounds 6 *> C:/Temp/av-kit/text-scrub-residuals/exec-review.txt", "scope": "H1-7b: an approved current review state and a matching ledger verdict, cap 6", "phase": "static", "exit_code": 0, "result": "pass", "tested_state": "ab761ddd5cc47cb014e80450be1e80c0825c984f+e7c60e3a25531c47ba7e950292591af393053446561e32e97d1731d07e2e0e4d", "output": "exec-review.txt: OK: approved at round 1 of 6, 0 open blocking findings"}
```

### Verdict

`approved` at round 1 of 6 (ledger loop `tsr-execution-2026-11-15-text-scrub-residuals`), with 0 open blocking findings (`review-state-check.txt`, `exec-review.txt`). The review grants no commit or push authorization.

---

## Deferred Items

| Item | Kind | Deferred-to | Basis |
|------|------|-------------|-------|
| A home folder that `Path.home()` already gives in short form, so the long form is never matched | out-of-scope | none | D-337 rules on the short form only, and rejected `GetLongPathNameW` (`docs/execution/plans/2026-11-06-tts-load-fp16/closeout-decisions.md:55-88`) |
| A home folder whose short form appears after the process has cached `""` for it (8.3 names turned on later) | out-of-scope | none | D-337: read once and cached; a restart reads it again |
| The renderer, the API, MCP and E2E | out-of-scope | none | No shape changes (plan §Boundary Inventory) |
| Commit and push | out-of-scope | — | Only on Mat's explicit words (H2-5) |

### Departures and their basis

- **Status line 15.** The coordinator wrote Mat's authorizing words into the plan's Status line after the plan review approved it. It is a plan-text edit made after approval; no AC, task row or contract changed.
- **Execution decisions D-928 to D-930** (HDP v2, `resolution: autonomous`, recorded in the plan's decision YAML; none hit an M item, each `mandatory: none`): D-928, the DECLARED_NEW list follows task row 0; D-929, the plan-local `scope-check.py`; D-930, `ruff format` on `adapter.py` and `services/download.py`, six layout-only hunks. Per H1-6 (Session 65 RULE-2) they live in the plan YAML, so the Decision Log below is `None.`.
- **Early test write.** The MEU-147 test file was written while row 0's base suite was still running; that suite had already collected, and `baseline-scope.json` records the file absent. The file was moved to the receipts folder's `staged` folder and restored at row 1 after the S4 check (`tsr-s4-row1.txt`: `scope-check: ok`). The base 2945 exclude it. The MEU-148 test was first written into `staged` and placed at row 3.
- **Row 2's first Green attempt** failed 2 of 35 in the test's own `_front` helper (CRLF on read-back); the fix is in the helper only (`test_transcript_title_cleaning.py:52`). Receipt `tsr-147-green-attempt1.txt`.
- **U+200B in the test source.** A literal zero-width space was replaced by the `\u200b` escape, so the file holds no invisible character; the case is unchanged.
- **`_SHORT_FORMS_LOCK`.** `health.py` guards the short-form cache with a lock beyond the plan text, so "looked up at most once per process" holds when logging threads scrub at the same time.
- **Scratch wrappers.** Each row ran through a `run-*.ps1` wrapper of its task cell in the receipts folder, with `ELECTRON_RUN_AS_NODE` unset; helper scripts there (`delivered-notes.py`, `green-147.py`, `green-148.py`, `focus-h13.py`, `mark-row.py`, `fill-handoffs.py`, `eol-final.py`) are not tracked. One wrapper's `Set-Location` line first carried a BEL where a backslash was meant and was corrected before it ran a row.
- **D-919 red-check regex** (`red-check.py:87`, `^_+ (.+?) _+\s*$`) was applied to the row-0 copy, as the plan directs; the row-0 copies carry 4 (red-check), 6 (identity) and 2 (issue-resolve) edits.
- **Gate attempt 1** stopped on a gate-script defect (the missing mutant `.exit` file), fixed in `session-gate.ps1`; the rerun passed. This is not the one flake rerun the brief allows.
- **`tsr-148-real-lookup.txt`** begins with a Python `SyntaxWarning` from the probe's `-c` string; the probe's results follow it and are unaffected.
- **AC-147.5** is an integration AC whose test sits in the `tests/unit` file under `@pytest.mark.integration` (`:187`), where the plan placed it.

---

## Decision Log

None.

---

## History

| Event | Date | Agent | Detail |
|-------|------|-------|--------|
| Created | 2026-11-15 | claude-code-local (Claude Opus 5.5) | Initial MEU-148 handoff after the H1-2 gate, H1-3 and H1-4 |
| Reviewed | 2026-11-15 | codex-independent-reviewer | H1-7 execution review approved at round 1 of 6, 0 findings |
| Updated | 2026-11-15 | claude-code-local (Claude Opus 5.5) | Codex Validation Report filled from the canonical review (H2) |
