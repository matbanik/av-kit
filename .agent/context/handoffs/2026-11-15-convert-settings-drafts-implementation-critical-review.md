---
date: "2026-11-17"
review_mode: "execution"
target_plan: "docs/execution/plans/2026-11-15-convert-settings-drafts/implementation-plan.md"
verdict: "approved"
findings_count: 0
template_version: "2.2"
requested_verbosity: "standard"
agent: "codex-independent-reviewer"
loop_id: "cs81-execution-2026-11-15-convert-settings-drafts"
round: 2
tested_state: "b6b124ab3e8882afaf02a7f493a7259237571758+9c4a723cc008d20e80d5b16772dac5f28cf523a36dd173ff9756230062f9b509"
---

# Critical Review: 2026-11-15-convert-settings-drafts

**Current round 2 verdict: approved. Intent achieved: yes. Open findings: 0.**

The round 1 record below is retained as history, including its then-failing observations and verdict. CS81-R1-F1's table status is updated to `fixed`. The current assessment, evidence and verdict are in **Recheck (round 2)** at the end.

> **Review Mode:** execution
> **Verdict:** changes_required

## Scope

Session 81, MEU-151 and MEU-152, including amendments A1 and A2. Reviewed the plan/task, plan-local scripts and row-0 data, both handoffs, human-check records, scoped product/test/document deltas, all six new test files, and recorded Red, Green, Electron and full-gate evidence. Applied the execution-review contract, relevant IR/DR checks and AV-1–AV-6. Codex is independent of the Anthropic author. Sessions 82 and 83 remain outside this review.

**Intent anchor:** "an open capture settings edit keeps only what the user changed, follows every other saved value and saves only the changed fields; a Convert Advanced edit (CQ, scale, audio) or preset pick survives settings arriving or changing; and a Convert queue card shows a Cut's in and out points as time codes, a waiting job's current place in the queue, and, for a Cut, the encoder it really runs; and two Adds of the same file never queue the same output file (amendment A1)."

**Intent achieved:** partial. Convert choices, queue labels and A1 satisfy their reviewed contracts. The capture draft retains a key after a refetch makes it equal to the saved value; a subsequent refetch can then be hidden and overwritten on Save. One High finding; no Critical finding established.

## Findings

| # | Severity | Blocking | Kind | Finding | File:Line | Recommendation | Status |
|---|---|---|---|---|---|---|---|
| CS81-R1-F1 | High | yes | behavior | A capture draft key that becomes equal to the saved baseline during a refetch never leaves draft state. With an inbox edit still open, edit hotkey F2→F9, receive saved F9, then receive saved F3 without another edit or Save. The form still shows F9 and Save sends both inbox_dir and hotkey F9, overwriting F3. This breaks CAPTURE_DRAFT_CHANGED_ONLY and the AC-151.3 rule that a no-longer-differing edit leaves the draft. | ui/src/renderer/src/features/capture/useCaptureSettings.ts:106 | Permanently remove equal-to-baseline draft keys when saved settings change, preserving other differing edits. Extend AC-151.3 with two successive refetches before Save and require the form to show F3 and the PUT to contain only inbox_dir. | fixed |

## Q1 — Capture drafts

Accepted the partial overlay, whole-form validation before any PUT, ordered changed-key selection, no PUT when nothing differs, and draft clearing after a successful Save. `patchForm` at `useCaptureSettings.ts:110–114` removes keys explicitly edited back to the current baseline. `save` at `:118–130` filters differing keys in `CAPTURE_KEYS` order; validation refusal precedes that write. Existing tests meaningfully check these paths.

Not accepted: permanent removal when a refetch makes an edited key equal to saved data. `changedOnly` is called only by `patchForm`; baseline changes at `:105` never update draft state at `:104`. The merge at `:106` therefore resurrects an already-saved edit after the next baseline change. The AC-151.3 refetch-equality test at `capture-settings-draft.behavior.test.ts:231` immediately calls Save, which clears the retained key and hides this failure.

An independent scratch Node probe transpiled the unchanged production hook in memory and rendered it with real React/testing-library. Query answers, schema validation and transport were stubbed; no app, backend or network request was started. The two rendered baseline changes produced:

```text
refetch 1: baseline.hotkey=F9 form.hotkey=F9 inbox edit still open
refetch 2: baseline.hotkey=F3 form.hotkey=F9 expected=F3
Save body=[{"inbox_dir":"X","hotkey":"F9"}] expected=[{"inbox_dir":"X"}]
CONFIRMED: equal-to-baseline key resurrects and overwrites newer saved value
```

This is CS81-R1-F1, not a separate test-paperwork finding. The D-1066 tests are substantive: their bodies require a nonempty recorded PUT, exact `['inbox_dir']` keys and the edited value. AC-105.23 retains style/refetch/color assertions; AC-143.30 retains the `tool_lock` GET assertion. The two capture-page pins use exact `toEqual` bodies. None passes vacuously because of the changed constants.

## Q2 — Convert controls

Accepted CONVERT_FIELD_CHOICE and CONVERT_PRESET_PICK. `ConvertPage.tsx:191–202` derives each field from its nullable choice or the current preset; settings updates have no setter that can replace a choice. Untouched fields follow the current preset. `selectPreset` at `:315–320` clears all three field choices, providing the existing way to restore preset values. Choices equal to a preset value remain intentional choices, as approved D-967 requires.

The snapshot dependencies include the resolved preset/CQ/scale/audio; Add uses the same resolved values. AC-151.10 checks controls, snapshot and Add after late settings; AC-151.11 checks changed defaults and Add; AC-151.12 checks untouched defaults, preset reset and preservation of the picked preset. No additional stuck/reset defect was established. These Advanced-field checks are unit behavior tests; no Electron coverage of these fields is claimed.

## Q3 — Queue cards and Cut encoder

Accepted CONVERT_TIMECODE, CUT_SEGMENT_TIMECODE, QUEUE_ROW_NUMBER, WAITING_POSITION and CUT_NO_GPU_ENCODER. The formatter rejects nonintegers, including NaN and infinities, negatives and values over 359999999; its divisions and zero-padding match Python `format_timecode` for the permitted range. An invalid/missing endpoint drops the Cut segment. The helper derives row numbers from array order and waiting rank from Pending statuses only; finished/removed/moved entries therefore affect the appropriate number.

`ConvertPage` passes those values to its cards. The optional QueueCard branch leaves the previous Pending text unchanged when `waitingPosition` is absent. The slot-baseline file is byte-identical to row 0, and recorded unchanged queue-card tests pass. No other page supplies the new property in this delta.

`conversion.py:573–578` saves None for Fast Copy/missing mode and libx265 for Reencode, without either GPU-resolution call. The unchanged adapter uses stream copy or libx265 respectively. Compress retains its previous resolution branch; Extract retains None. New tests check real service dispatch, stored values, zero detect calls, missing-mode normalization, unavailable software capability and retry of a legacy label. No failure found.

## Q4 — Output reservations

Accepted QUEUE_OUTPUT_RESERVED, QUEUE_ADD_SERIAL and ACTIVE_WRITER_RESERVED within the approved single-service/process boundary. Pending, Processing, Failed and Cancelled rows hold their names. `_add_lock` covers queue read through commit; `_writer_lock` protects the active path set and is released before database/media work. The worker never acquires `_add_lock`, so the two added locks create no circular wait.

`_run_one` reserves before rereading the row and releases in the outer finally, including absent/non-Pending rows, dispatch errors, cancellation and successful completion. A job starting after Add's queue snapshot was already held as Pending; a previously running removed job remains in the active set. Removing a waiting row frees its name; removing a writer's row does not. Failed/Cancelled retry preserves a reserved path.

The suffix loop checks disk, current-call reservations and held paths. AC-30.2's existing-file Skip remains; `allow_skip=error is None` prevents a probe/track failure from becoming a retryable alias of another output. Done/Skipped names depend on files on disk as approved. The new tests call the actual service, including a SQLite stack, concurrent Add barrier and event-controlled writers. They assert distinct names/statuses and, for overwrite routes, original and later output bytes. Their original A1 Red shows 13 assertion failures and six passing guards; Green shows 83 passing affected tests. No second collision route was established within the approved boundary.

## Q5 — Red, Green, A2 and gate

Accepted the recorded failing-then-passing proofs. Independently replaying the four original Red receipts through `red-check.check` finds no setup/unattributed failure. Preserved child exits are 1. MEU-151: 12 failed/199 passed; MEU-152 UI: 10 failed/67 passed; Cut encoder: five assertion failures; A1: 13 failed/six passed. MEU-151's validation, successful-save and preset-reset guards are absent from the complete failure list and are in the collected tests; A1's six passing cases are the AC-152.15/AC-152.20 guards. Green receipts report 299 UI tests, 131 UI tests/five encoder tests/eight service guards, and 83 A1 affected tests respectively. The checker selftest independently passes 45 fixtures, including 30 negative controls. D-974's one-or-more-underscore pytest header is sound for these actual long parametrized titles.

A2 is accepted as a meaningful replacement for HC-1–HC-5, with the disclosed absence of an Electron Red. Its assertions require:

| Former check | Actual observation required |
|---|---|
| HC-1 / AC-152.21 | Exact Cut timecode segment while Pending and after Done |
| HC-2 / AC-152.22 | Exact ordered card identities and 1..n numbers, waiting text after Remove, and Done/Processing/Pending state with the remaining card next |
| HC-3 / AC-152.23 | Recorded Fast Copy meta text without encoder tokens, null stored encoder, and libx265 for Reencode |
| HC-4 / AC-151.14 | Exactly one inbox-only PUT, saved backend/field hotkey unchanged, and Capture page showing the new folder |
| HC-5 / AC-152.24 | Distinct exact waiting output paths, both real files, expected different durations, distinct hashes, and matching Open file targets |

These checks cannot pass merely by reaching a route or observing a nonempty queue. D-976's seams use each launch's scratch profile/backend and replace only that app's picker IPC handler; backend cleanup checks recorded PID/start time and Electron cleanup uses the launch handle. D-973's dev-app checker also binds process ownership to recorded PID/creation time and excludes MCP/foreign processes. The recorded close timeout and handle kill in row-5 r3 are disclosed; no product behavior is mocked by that cleanup.

The initial A2 expectation correction agrees with D-970: removing the third waiting row leaves the first still next. The timeout/bounded-wait changes and the earlier failed gate are preserved. Final row-5 evidence is three runs of five passes, followed by another five passes in the gate. No human round-2 pass was invented.

The passing full gate has all 22 registered steps at exit 0, matching before/after identity: 3032 Python tests, 1569 UI tests in 135 files, UI build, renders, 23 existing Convert Electron tests, three selected capture Electron tests and five A2 Electron tests. The first gate stopped at its four UI failures and printed later stages as not_run; the second ran from the beginning. API/MCP skip hashes independently match all 107 baseline files. Build-record means no distribution build; the UI build did run. No shipped GUI reference image required a comparison. No baseline failure was excused.

| Test surface | Rigor assessment |
|---|---|
| Capture hook/page/card tests | Strong assertions for their sequences; AC-151.3 lacks the second-refetch case exposed by F1 |
| Convert choices/snapshot/Add tests | Strong: concrete field values and submitted bodies, plus reset guards |
| Formatter/positions/QueueCard tests | Strong: boundaries, exact ordering/text and old optional-property behavior |
| Cut encoder tests | Strong: real service, stored result and call/options checks |
| A1 reservation tests | Strong: SQLite, controlled concurrency and overwrite bytes |
| A2 Electron tests | Strong for the five stated behaviors; no Advanced-field proof claimed |

Existing assertion changes stay within AC-151.9/D-1066 and the named AC-152.3 timecode pin. Other existing assertions and the four read-never-changed files are preserved. No skip/only/xfail or weakened assertion was introduced in the reviewed delta. AV-1–AV-6 otherwise pass; F1 is an uncovered behavior failure, not a claim that the recorded suites failed.

## Q6 — Registers, status and documentation

Accepted the scoped tool updates: the issue-add receipt names CONVERT-OUTPUT-NAME-REUSED; issue-resolve reports zero problems and only the six issues' permitted resolution fields. The current diff agrees. Independent `issue_triage.py render --check` exits 0 with `OK: known-issues.md is up-to-date`. Both MEUs are ready_for_review; generated registry/BUILD_PLAN changes agree. The grouping diff is exactly section 6 row 81.

The 06 note retains CRLF and the 08 note retains LF; both accurately describe the implemented Convert/A1/A2 behavior and coverage limits. The capture draft's delivered claim is incomplete for F1 and should be considered subject to that correction. This is the same behavior finding, not a separate documentation blocker.

## Q7 — Safety and evidence fidelity

Independent byte/hash inspection confirms scoped line-ending kinds, the MIXED file's eight bare-LF lines, all four read-never-changed hashes, and the row-0 copy hashes. Copies agree with HEAD after Git line-ending normalization. All 21 modified tracked paths are scoped; sibling planning artifacts remain excluded. New product/test/document lines contain no literal home-folder path or personal email address. HEAD remains b6b124ab3e8882afaf02a7f493a7259237571758 on main. This reviewer performed no repository write, commit, stash, revert, network request, process start of the app/backend, or process stop.

**Tested state:** `b6b124ab3e8882afaf02a7f493a7259237571758+12188abab1f9189a4f14382192b0e13f355e3c81bf39f29c59088f9fb40c41ce`.

The sandbox cannot read `~/.config/git/ignore`; listing names confirms `.claude/settings.local.json` appears as an additional untracked path. Its contents were never opened. To avoid identity.py reading that prohibited file, I supplied a process-local `core.excludesFile` pointing to a scratch ignore containing only that path, preserving the harness's existing Git config entries. Running the unchanged plan `identity.py --state-only`, with ELECTRON_RUN_AS_NODE unset, then reproduces the gate value exactly. Thus there is no substantive tested-state difference after reproducing that one host ignore rule; no additional path exclusion was needed. The unadjusted secret-reading identity was not run.

Handoff gate counts, human-check wording and failure disclosures match the inspected receipts. Passing evidence remains valid for the observed tests, while F1 demonstrates an additional behavior they do not cover. The reviewer did not rerun product suites or Electron. Completion-preflight was applied to this review artifact and the canonical task state: H1 review and H2 remain coordinator work, and this report does not claim implementation DONE.

## Checklist Results

| Check | Result | Observation | Exit | Evidence |
|---|---|---|---|---|
| Q1 capture baseline retirement | fail | Independent React hook probe | 0 | Baseline F9→F3 leaves form F9; PUT includes stale hotkey |
| Q2–Q4 controls, labels and reservations | pass | Independent source/test/receipt inspection | null | Contracts and negative cases as described above |
| Red proof and checker | pass | Scratch audit calling red-check.check; red-check.py --selftest | 0 | Four Reds accepted; 45 fixtures, zero wrong |
| Recorded full gate and identity | pass | Inspected gate plus independently executed identity.py --state-only with the single host ignore reproduced | 0 | Exact state match; 22 gate steps exit 0 |
| Issue render / OpenAPI | pass | Independent offline, no-sync check commands | 0 | Render up-to-date; OpenAPI check empty output at exit 0 |
| Scope, unchanged files and endings | pass | Scratch byte/hash/diff audit | 0 | Four unchanged hashes, 107 skip hashes, line endings and scoped tracked changes accepted |
| Fresh reviewer product-suite/Electron run | n/a | Forbidden by review scope | null | Recorded matching evidence inspected instead |

```json
{"schema_version":"evidence.v1","check_id":"cs81-review-capture-two-refetches","command":"rtk proxy node C:/Temp/av-kit/convert-settings-drafts/exec-review/capture-probe.cjs","cwd":"P:/av-kit","scope":"Production useCaptureSettings hook, React render with controlled query answers and mocked transport/validation","phase":"targeted","exit_code":0,"result":"fail","tested_state":"b6b124ab3e8882afaf02a7f493a7259237571758+12188abab1f9189a4f14382192b0e13f355e3c81bf39f29c59088f9fb40c41ce","output":"refetch 1: baseline.hotkey=F9 form.hotkey=F9 inbox edit still open; refetch 2: baseline.hotkey=F3 form.hotkey=F9 expected=F3; Save body=[{\"inbox_dir\":\"X\",\"hotkey\":\"F9\"}] expected=[{\"inbox_dir\":\"X\"}]; CONFIRMED: equal-to-baseline key resurrects and overwrites newer saved value. Exit 0 means the probe confirmed the defect, not that the contract passed."}
```

```json
{"schema_version":"evidence.v1","check_id":"cs81-review-identity","command":"rtk proxy pwsh -NoProfile -Command { $env:PYTHONDONTWRITEBYTECODE='1'; $env:TMP='C:/Temp/av-kit/convert-settings-drafts/exec-review/tmp'; $env:TEMP=$env:TMP; $env:ELECTRON_RUN_AS_NODE=$null; $n=0; if ($env:GIT_CONFIG_COUNT) { $n=[int]$env:GIT_CONFIG_COUNT }; [Environment]::SetEnvironmentVariable('GIT_CONFIG_KEY_'+$n,'core.excludesFile'); [Environment]::SetEnvironmentVariable('GIT_CONFIG_VALUE_'+$n,'C:/Temp/av-kit/convert-settings-drafts/exec-review/reviewer.ignore'); $env:GIT_CONFIG_COUNT=[string]($n+1); .venv/Scripts/python.exe docs/execution/plans/2026-11-15-convert-settings-drafts/identity.py --state-only; exit $LASTEXITCODE }","cwd":"P:/av-kit","scope":"Current D6 identity with only the prohibited local settings path ignored as on host","phase":"static","exit_code":0,"result":"pass","tested_state":"b6b124ab3e8882afaf02a7f493a7259237571758+12188abab1f9189a4f14382192b0e13f355e3c81bf39f29c59088f9fb40c41ce","output":"b6b124ab3e8882afaf02a7f493a7259237571758+12188abab1f9189a4f14382192b0e13f355e3c81bf39f29c59088f9fb40c41ce"}
```

```json
{"schema_version":"evidence.v1","check_id":"cs81-review-scope-red-audit","command":"rtk proxy .venv/Scripts/python.exe C:/Temp/av-kit/convert-settings-drafts/exec-review/audit.py","cwd":"P:/av-kit","scope":"Row-0 hashes, unchanged paths, line endings, scoped diff, original Red receipts and recorded gate/Green/A2 summaries","phase":"static","exit_code":0,"result":"pass","tested_state":"b6b124ab3e8882afaf02a7f493a7259237571758+12188abab1f9189a4f14382192b0e13f355e3c81bf39f29c59088f9fb40c41ce","output":"All existing row-0 copies match baseline hashes and normalized HEAD. Four read-never-changed hashes and 107 skip-input hashes match. Line endings correct across 30 scoped paths including context. All 21 modified tracked paths scoped; no new sensitive literal offenders. Four original Red receipts have child exit 1 and zero checker problems. Full handoff records carry the matching state. AUDIT PASS."}
```

```json
{"schema_version":"evidence.v1","check_id":"cs81-review-render","command":"rtk proxy uv run --no-sync --offline python tools/issue_triage.py render --check","cwd":"P:/av-kit","scope":"Generated known-issues.md","phase":"static","exit_code":0,"result":"pass","tested_state":"b6b124ab3e8882afaf02a7f493a7259237571758+12188abab1f9189a4f14382192b0e13f355e3c81bf39f29c59088f9fb40c41ce","output":"OK: known-issues.md is up-to-date"}
```

```json
{"schema_version":"evidence.v1","check_id":"cs81-review-openapi","command":"rtk proxy uv run --no-sync --offline python tools/export_openapi.py --check openapi.committed.json","cwd":"P:/av-kit","scope":"Current exported OpenAPI against committed schema","phase":"static","exit_code":0,"result":"pass","tested_state":"b6b124ab3e8882afaf02a7f493a7259237571758+12188abab1f9189a4f14382192b0e13f355e3c81bf39f29c59088f9fb40c41ce","output":"No output; exit 0. The initial invocation without a --check path exited 2 with 'expected one argument'; corrected to the command recorded here."}
```

```json
{"schema_version":"evidence.v1","check_id":"cs81-review-red-check-selftest","command":"rtk proxy .venv/Scripts/python.exe docs/execution/plans/2026-11-15-convert-settings-drafts/red-check.py --selftest","cwd":"P:/av-kit","scope":"Read-only checker fixtures, temporary files under review TMP/TEMP","phase":"static","exit_code":0,"result":"pass","tested_state":"b6b124ab3e8882afaf02a7f493a7259237571758+12188abab1f9189a4f14382192b0e13f355e3c81bf39f29c59088f9fb40c41ce","output":"red-check selftest: 45 fixture(s) (15 positive, 30 negative), 0 wrong: []"}
```

## Verdict

`changes_required` — fix CS81-R1-F1 and add the two-refetch regression before approval. The passing recorded gate is acknowledged; it does not cover retirement of a draft key made equal by a refetch. No additional blocker was established. Approved plan/A1 decisions and Mat's A2/D-1066 rulings remain accepted. Commit still awaits clearance, and push remains outside authorization.

## Recheck (round 2)

**Date:** 2026-11-17. **Agent:** codex-independent-reviewer. **Workflow:** `/execution-critical-review`. **Verdict:** approved. **Intent achieved:** yes. No open High or Critical finding, and no new finding established.

The registered goal anchor quoted in Scope remains the intent of this round. This recheck reviewed D-1067, its new AC-151.3 sequence, D-1068 and gate run 5, and the updated plan/task/handoffs/current focus. The earlier Q2–Q4 and unchanged portions of Q5–Q7 analysis remain accepted; their full analysis above is retained rather than repeated. Current product/test/document diffs and the six new test files were inspected, and the scope/hash/line-ending audit was repeated. All reviewer writes were under `C:/Temp/av-kit`; no product suite, build, Electron app, backend or network request was started.

### Prior Pass Summary

| Finding | Prior Status | Recheck Result |
|---|---|---|
| CS81-R1-F1 | open | fixed |

### New Findings

| # | Severity | Blocking | Kind | Finding | File:Line | Recommendation | Status |
|---|---|---|---|---|---|---|---|

### Corrections Applied

- D-1067 adds the guarded render-time prune at `ui/src/renderer/src/features/capture/useCaptureSettings.ts:110`. A new saved baseline is recorded once; equal draft leaves are removed with `changedOnly`, unequal edits survive, and an empty draft becomes null. `baseline` is memoized against stable query data, so the state adjustment terminates before commit.
- The new test at `ui/tests/unit/capture-settings-draft.behavior.test.ts:243` retains an inbox edit, edits F2 to F9, refetches F9 and then F3 before Save, and requires F3 plus exactly `[{ inbox_dir: 'X' }]`. This directly catches the prior defect without changing an existing expected value.
- The plan's AC-151.3 text, D-1067/D-1068 entries, task H1-2, both handoffs and current focus disclose the correction, failed reruns and passing fifth gate. They agree on the delivered behavior. No other behavioral contract or AC was changed by the correction; approved A1/A2 and D-1066 remain as reviewed in round 1.

### Q1 — Capture drafts

Accepted **CAPTURE_DRAFT_CHANGED_ONLY** and **CAPTURE_SAVE_CHANGED_ONLY**, including permanent retirement of a key made equal by a refetch. The prior F9→F3 failure is fixed. An independent scratch probe transpiled the current production hook and settings schema in memory, used real React, StrictMode and React Query, and supplied controlled query answers and transport. Unrelated namespace enum imports were supplied only to load the actual capture schema. No assertion or production hook logic was replaced.

| Probe | Observed result |
|---|---|
| Two refetches while inbox X remains edited | F9 retires; second answer F3 reaches every committed render; Save sends only inbox_dir X; dirty label remains while X differs |
| Refetch consumes the sole edit | isDirty false, saveLabel Save, saveClass undefined; later F3 follows; Save sends no PUT |
| User edits F9 to F8 while a refetch returning F9 is in flight | F8 survives response and Save sends inbox_dir X and hotkey F8 |
| User makes a new F8 edit after retirement, then saved F3 arrives | F8 remains and Save sends hotkey F8 |
| Invalid annotated_format gif | Actual SettingsValidationError, no PUT |
| Multiple keys patched in reverse order | Save order is inbox_dir, hotkey, backup_dir, annotated_format |
| Twenty successive saved answers under StrictMode | 60 renders, bounded; no render loop |

The guard compares `prunedFor` with the memoized baseline, and updates both in the same component's render. React retries before commit; a later user event uses the committed callback and current draft. The deferred-query probe specifically checks that a newer user edit is not replaced by the response. The existing AC-151.4 covers editing before the initial answer. Save still validates the merged form first and selects only remaining differing keys in CAPTURE_KEYS order (`useCaptureSettings.ts:129`). The D-1066 bodies still require an actual recorded inbox PUT, exact keys and the edited path; the two capture-page bodies use exact equality. Nothing passes vacuously. No capture behavior remains unaccepted.

### Q2 — Convert controls

Accepted the round 1 analysis of **CONVERT_FIELD_CHOICE** and **CONVERT_PRESET_PICK**. Current diff retains the four nullable choices, resolved Add/snapshot values and preset reset. D-1067 changes only the capture hook. Existing assertions for late defaults, changed defaults, untouched fields and reset remain substantive. No newly stuck field was established. Advanced-field coverage remains unit behavior coverage; no Electron coverage of those fields is claimed.

### Q3 — Queue cards and Cut encoder

Accepted the round 1 analysis of **CONVERT_TIMECODE**, **CUT_SEGMENT_TIMECODE**, **QUEUE_ROW_NUMBER**, **WAITING_POSITION** and **CUT_NO_GPU_ENCODER**. Current source retains the finite-integer/range refusal, rendered-order row numbers, Pending-only ranks, optional-property fallback for other pages, and Cut-specific encoder branch without GPU detection/resolution. Compress and Extract retain their earlier paths. The slot baseline and four read-never-changed files still match row 0. No new failure established.

### Q4 — Output names

Accepted the round 1 analysis of **QUEUE_OUTPUT_RESERVED**, **QUEUE_ADD_SERIAL** and **ACTIVE_WRITER_RESERVED**, within the approved single-service/process boundary. Current service diff still reserves unfinished and retryable jobs, serializes Adds through commit, copies active writers after the queue read and releases writers in the outer finally. The worker does not take the Add lock; the writer lock is not held during media/database work. `allow_skip` remains conditional on absence of probe/track error; genuine Skipped behavior is preserved. Tests use the real service, SQLite, controlled simultaneous Adds and writer bytes, as previously reviewed. No additional overwrite or deadlock established.

### Q5 — Red, Green, E2E proofs and gate

Accepted D-1067's Red as the intended assertion failure: `expected 'F9' to be 'F3'`, one failed and nine passed, preserved child exit 1. The unchanged read-only checker independently accepts that receipt with the specific two-refetch title required: one receipt, one required test, zero problems, exit 0. Green reports six files and 301 tests passing; recorded typecheck and ESLint succeed. Original Red/guard evidence was re-audited and remains accepted.

Accepted the prior A2 assessment and the current tests for HC-1–HC-5: exact Cut timecodes, ordered identities and changed waiting ranks, observed Fast Copy text plus stored encoder values, one inbox-only request with backend/field agreement, and distinct output paths/files/durations/hashes. These observe behavior rather than mere navigation. Scratch profiles, the one native-picker IPC seam, backend PID/start-time checks and the launch's Electron handle remain confined to each test's app/backend. The disclosed absence of A2 Red and corrected test expectation remain as accepted in round 1.

D-1068 is sound as a full rerun without weakening tests or excusing failures. Runs 3 and 4 stop at their nonzero py-tests result and mark subsequent steps not_run; neither is presented as a pass. Their unrelated timing failures and the coordinator's post-commit registration are disclosed; that given deferral is not a finding. Run 5 runs all required stages afresh and passes at the same current identity before and after:

| Gate evidence independently inspected | Result |
|---|---|
| Registered steps and child receipts | 22 steps, all exit 0; every named child receipt exists |
| Targeted MEU-151 / MEU-152 | 301 UI / 38 UI / 83 Python passes |
| Full Python | 3032 passed, 37 warnings |
| Full UI | 135 files, 1570 tests passed |
| UI build and state/issue render checks | exit 0 |
| Existing Convert / selected Capture / A2 Electron | 23 / 3 / 5 passed |
| Before/after/current identity | identical |

The API/MCP skips remain supported by 107 unchanged input hashes. Build-record concerns a distribution build; the required UI build ran. No shipped GUI reference is claimed. Current existing-test diffs stay within AC-151.9/D-1066 and AC-152.3 plus the approved new assertions/helpers; S5 has no new unresolved failure. The added two-refetch test and all newly inspected cases have strong behavior assertions. Prior AV-1–AV-6 assessment remains accepted. No fresh reviewer suite/Electron pass is claimed.

### Q6 — Registers, MEU status and docs

Accepted the prior named-tool provenance and the current scoped register delta. Independently rerunning `issue_triage.py render --check` offline with no sync exits 0: `OK: known-issues.md is up-to-date`. Both MEUs remain ready_for_review. The grouping delta is still only §6 row 81. The Delivered notes describe the shipped behavior and coverage limits; 06 retains CRLF and 08 LF. The capture delivered behavior now also holds for the two-refetch case. No new contract or register discrepancy established.

### Q7 — Safety and evidence fidelity

Repeated byte/hash/diff inspection passes: 21 modified tracked paths are scoped; row-0 copies match their recorded hashes and normalized HEAD; all four read-never-changed hashes and 107 API/MCP skip hashes match; 30 audited paths retain their required line-ending kinds, including eight bare-LF lines in convert-controls.ts. The inspected new product/test/document delta contains no literal home-folder path or personal email address. Sibling Sessions 82/83 remain excluded. HEAD is still b6b124ab3e8882afaf02a7f493a7259237571758 on main. No reviewer repository write, commit, stash, revert, network request or app/backend start/stop occurred.

**Current tested_state:** `b6b124ab3e8882afaf02a7f493a7259237571758+9c4a723cc008d20e80d5b16772dac5f28cf523a36dd173ff9756230062f9b509`.

The unadjusted sandbox lists `.claude/settings.local.json` because it cannot read `~/.config/git/ignore`. Its contents were never opened. As in round 1, a process-local Git core.excludesFile reproduces only that single host ignore rule, preserving inherited Git config entries. Running the unchanged plan `identity.py --state-only` with ELECTRON_RUN_AS_NODE unset then yields exactly the gate's value above. There is no substantive difference and no additional exclusion. The unadjusted identity, which would read the prohibited file, was deliberately not executed. The historical round 1 identity differs because the reviewed capture code/test changed; it is not substituted for current evidence.

Both handoffs' fresh full records and updated counts match run 5 and current state. Plan/task disclosures match D-1067/D-1068 and the receipts. Completion-preflight was applied within this read-only reviewer role: implementation rows are complete, while H1-7 acceptance and H2 remain coordinator work. This report clears the independent review; it does not claim overall implementation closeout DONE or execute the authorized future commit. Push remains unauthorized.

### Checklist Results (round 2)

| Check | Result | Command or procedure | Exit | Evidence |
|---|---|---|---|---|
| CS81-R1-F1 and prune regressions | pass | node capture-r2-probe.cjs, production hook/schema in memory | 0 | Seven scenarios above pass with real React/QueryClient and controlled IO |
| Correction Red | pass | red-check.py with specific two-refetch title required | 0 | Preserved exit 1, one assertion failure, nine passes; zero checker problems |
| Gate and handoff fidelity | pass | evidence-r2.py and direct source/receipt inspection | 0 | 22 gate steps and both fresh full handoff records match current state |
| Scope, hashes, endings, original Reds | pass | audit.py | 0 | AUDIT PASS; decisive observations under Q5 and Q7 |
| Identity | pass | identity.py --state-only with single host ignore rule reproduced | 0 | Exact run-5 match |
| Issue render / OpenAPI | pass | offline no-sync check commands | 0 | Render up-to-date; OpenAPI emits no output, exit 0 |
| Fresh product suites/Electron | n/a | Prohibited by this read-only review scope | null | Recorded evidence reviewed; no suite/app launched |

```json
{"schema_version": "evidence.v1", "check_id": "cs81-r2-capture-probe", "command": "rtk proxy node C:/Temp/av-kit/convert-settings-drafts/exec-review/capture-r2-probe.cjs", "cwd": "P:/av-kit", "scope": "Production hook/schema, real React StrictMode and QueryClient, controlled IO; seven refetch/draft/save probes", "phase": "targeted", "exit_code": 0, "result": "pass", "tested_state": "b6b124ab3e8882afaf02a7f493a7259237571758+9c4a723cc008d20e80d5b16772dac5f28cf523a36dd173ff9756230062f9b509", "output": "PASS two refetches: F9 retires, F3 paints, Save={inbox_dir:X}, other edit remains dirty\nPASS empty prune: clean label/class, later F3 follows, Save sends no PUT\nPASS edit while refetch in flight: F8 survives F9 response and is saved\nPASS edit after refetch: new F8 choice survives later F3\nPASS production validation refusal: zero PUT\nPASS Save key order: inbox_dir,hotkey,backup_dir,annotated_format\nPASS StrictMode repeated saved answers: 20 updates, 60 renders, no render loop\nCAPTURE R2 PROBE PASS: 7 scenarios, real React + QueryClient, production hook/schema, mocked IO only; no network/app/backend/suite."}
```

```json
{"schema_version": "evidence.v1", "check_id": "cs81-r2-evidence", "command": "rtk proxy .venv/Scripts/python.exe C:/Temp/av-kit/convert-settings-drafts/exec-review/evidence-r2.py", "cwd": "P:/av-kit", "scope": "Run-5 gate and child receipts, both handoff full records, D-1067 Red", "phase": "static", "exit_code": 0, "result": "pass", "tested_state": "b6b124ab3e8882afaf02a7f493a7259237571758+9c4a723cc008d20e80d5b16772dac5f28cf523a36dd173ff9756230062f9b509", "output": "RUN5: 22 steps exit 0; each child receipt exists; decisive counts and both identities match.\nMEU-151: fresh full evidence matches run 5 and current identity.\nMEU-152: fresh full evidence matches run 5 and current identity.\nD1067 Red: one assertion failure, F9 vs F3, 9 passing guards, preserved child exit 1.\nEVIDENCE R2 PASS"}
```

```json
{"schema_version": "evidence.v1", "check_id": "cs81-r2-red-check", "command": "rtk proxy .venv/Scripts/python.exe docs/execution/plans/2026-11-15-convert-settings-drafts/red-check.py --require 'AC-151.3 an edit that a refetch makes equal leaves the draft for good' C:/Temp/av-kit/convert-settings-drafts/cs81-d1067-red.txt", "cwd": "P:/av-kit", "scope": "Correction Red assertion and required title", "phase": "static", "exit_code": 0, "result": "pass", "tested_state": "b6b124ab3e8882afaf02a7f493a7259237571758+9c4a723cc008d20e80d5b16772dac5f28cf523a36dd173ff9756230062f9b509", "output": "red-check: 1 receipt(s), 1 required test(s), 0 problem(s)"}
```

```json
{"schema_version": "evidence.v1", "check_id": "cs81-r2-render", "command": "rtk proxy uv run --no-sync --offline python tools/issue_triage.py render --check", "cwd": "P:/av-kit", "scope": "Generated issue register", "phase": "static", "exit_code": 0, "result": "pass", "tested_state": "b6b124ab3e8882afaf02a7f493a7259237571758+9c4a723cc008d20e80d5b16772dac5f28cf523a36dd173ff9756230062f9b509", "output": "OK: known-issues.md is up-to-date"}
```

```json
{"schema_version": "evidence.v1", "check_id": "cs81-r2-openapi", "command": "rtk proxy uv run --no-sync --offline python tools/export_openapi.py --check openapi.committed.json", "cwd": "P:/av-kit", "scope": "Current exported OpenAPI against committed schema", "phase": "static", "exit_code": 0, "result": "pass", "tested_state": "b6b124ab3e8882afaf02a7f493a7259237571758+9c4a723cc008d20e80d5b16772dac5f28cf523a36dd173ff9756230062f9b509", "output": "No output; exit 0."}
```

```json
{"schema_version": "evidence.v1", "check_id": "cs81-r2-identity", "command": "rtk proxy .venv/Scripts/python.exe docs/execution/plans/2026-11-15-convert-settings-drafts/identity.py --state-only", "cwd": "P:/av-kit", "scope": "Current D6 identity; PYTHONDONTWRITEBYTECODE=1; TMP/TEMP in exec-review/tmp; ELECTRON_RUN_AS_NODE unset; process-local core.excludesFile reproduces only .claude/settings.local.json host ignore while preserving inherited Git config", "phase": "static", "exit_code": 0, "result": "pass", "tested_state": "b6b124ab3e8882afaf02a7f493a7259237571758+9c4a723cc008d20e80d5b16772dac5f28cf523a36dd173ff9756230062f9b509", "output": "b6b124ab3e8882afaf02a7f493a7259237571758+9c4a723cc008d20e80d5b16772dac5f28cf523a36dd173ff9756230062f9b509"}
```

```json
{"schema_version": "evidence.v1", "check_id": "cs81-r2-scope-audit", "command": "rtk proxy .venv/Scripts/python.exe C:/Temp/av-kit/convert-settings-drafts/exec-review/audit.py", "cwd": "P:/av-kit", "scope": "Row-0 copies, read-never-changed and skip hashes, scoped tracked diffs, line endings, original Reds and current receipt/handoff summaries", "phase": "static", "exit_code": 0, "result": "pass", "tested_state": "b6b124ab3e8882afaf02a7f493a7259237571758+9c4a723cc008d20e80d5b16772dac5f28cf523a36dd173ff9756230062f9b509", "output": "AUDIT PASS. 21 modified tracked paths scoped; 4 read-never-changed and 107 skip hashes match; 30 scoped line-ending kinds correct, MIXED keeps eight bare-LF lines; new product/test/document sensitive literal offenders []; four original Reds: zero checker problems and preserved child exit 1; both fresh full handoff records match current state."}
```

### Verdict

`approved` — CS81-R1-F1 is fixed. The delivered work achieves the registered intent, including A1. No new finding was established. Prior approved plan decisions and Mat's rulings remain accepted. The coordinator may continue H1 acceptance and H2 closeout; this reviewer made no repository change.
