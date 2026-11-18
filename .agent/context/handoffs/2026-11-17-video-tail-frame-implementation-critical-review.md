---
date: "2026-11-18"
review_mode: "execution"
target_plan: "docs/execution/plans/2026-11-17-video-tail-frame/implementation-plan.md"
verdict: "approved"
findings_count: 0
template_version: "2.2"
requested_verbosity: "standard"
agent: "codex-independent-reviewer"
loop_id: "vtf-execution-2026-11-17-video-tail-frame"
round: 1
tested_state: "9c655bdf6ac2436308e20d4b889268e051d4e19d+6b06b8a25e513a5e2073813d4eedf4a659e77acd4f791ec51559a8dec0331ea2"
---

# Critical Review: 2026-11-17-video-tail-frame

> **Review Mode:** execution
> **Verdict:** approved

## Scope

Independent Codex review of Anthropic-authored Session 93, MEU-160. Reviewed the delta from `baseline.sha` in the plan's Files Modified paths, its scripts and baseline records, the MEU-160 handoff, and the execution receipts against AC-160.1 through AC-160.13. Sessions 91 and 94 are excluded. The coordinator publishes this report and completes subsequent closeout; this verdict does not certify H2 or authorize a push. No repository file was written by this reviewer.

**Intent anchor:** `FFmpegAdapter._last_video_ms` asks ffprobe for the packets from `S = max(0, T - 60 s)` with an end (`-read_intervals S%+D`, D = T + 60 s, which ffprobe counts from the keyframe K at or before `S`), not from `S` with no end, so the END_GAP retry finds the clip's last video packet on a host loaded to at least 85 % as on an idle one; 1000 adapter sequences under load give zero empty or short packet reads, and five traced runs of `tests/integration/test_video_real_ffmpeg.py` under load pass with zero failures; a failure that lacks the watched signal is never counted as a pass (Session 90 RULE-3); only `adapter.py:644` and its docstring change in the product, two named unit assertions change their expected interval, and no API route, OpenAPI document, MCP tool, setting or schema changes; scripts and tests prove it, with no manual check.

**Intent achieved:** yes. The independently measured state exactly equals the gate's state. The sandbox's inaccessible global ignore and the sibling plan folders cause no discrepancy: `identity.py` explicitly excludes secret names and the applicable foreign untracked plans. No state adjustment was needed.

## Findings

| # | Severity | Blocking | Kind | Finding | File:Line | Recommendation | Status |
|---|---|---|---|---|---|---|---|

## Q1 — Goal

Accepted all goal clauses. Current code, saved raw evidence and independent probes support the following coverage.

| Goal clause | ACs | Decisive evidence |
|---|---|---|
| Bounded read and accurate explanation | AC-160.1–3, AC-160.7 | `adapter.py:623`, `:646`; only the docstring and named argument change. Six boundary cases and both named argv assertions pass. |
| Fault reproduced on base | AC-160.4, AC-160.6 | `vtf-stress-bad.txt`: 5 bad / 400, each with TAIL_SIGNAL; load samples all 100%. Raw log independently confirms sequences 64, 239, 318, 343 and 392. |
| 1000 clean sequences under load | AC-160.5 | `vtf-stress-clean.txt`: 1000 / 1000 correct; 138 samples, min/median/max 100%. Independent log probe confirms 1000 distinct sequences, exactly one packet read each, correct bounded arguments, 75 packet times and last=2960 each. |
| Five traced module runs, zero failures | AC-160.8–9 | Five `vtf-load-run-green-N.txt` receipts: 22 passed each; 40 load samples, all 100%. Each trace has 22 armed tests and three bounded packet reads with reference last times. |
| Failure without signal never passes | AC-160.10 | Independent fixtures return exit 3 in both modes; selftests exercise signalled and unsignalled failures. Task rows preserve failure/stop handling. |
| Exact product/test scope; unchanged public surfaces | AC-160.7, AC-160.11–13 | Current diff and passing diff/eol checks; 629 skip-basis hashes and complete path membership match row 0. Read-only core, route, port and conftest hashes match. |

Not claimed: a fresh reviewer load run or full-suite rerun. The matching saved gate and load proofs are accepted; the reviewer ran only lightweight checks and evidence-reading probes.

## Q2 — The fix

Accepted BOUNDED_TAIL_READ, TAIL_DOC and TAIL_SAME_ANSWER. `adapter.py:646` constructs the approved exact expression using `_seek_text` for both S and D. The lookback, selected stream, deadline, subprocess options, packet decoding and single fallback remain unchanged.

The saved FFmpeg source confirms that a `+` end is added to the first selected packet timestamp (`ffprobe-master.c:1874–1887`), and parsing the bounded duration initializes the previously unset end fields (`:3308–3345`). Thus the end is K + T + 60 s, not S + a fixed two-minute span. For the tail case on the clips' nonnegative timeline, the worst early keyframe is K=0; even then the end lies beyond T and therefore beyond the last video packet. An arbitrarily long GOP cannot shorten that window. For T below 60 s, S=0 and the same argument applies.

The observed last times are 2960 ms for the two short clips and 149960 ms for the one-keyframe clip, matching full-read references. Idle Green and the targeted gate both pass their pixel comparisons. The docstring accurately says the duration is past the first packet read. It makes no fixed-span claim.

Not accepted as a universal promise: EOF for an arbitrary invocation well inside a longer file. The approved TAIL_SAME_ANSWER contract explicitly conditions equality on the last packet fitting inside this bound. That limitation does not weaken the delivered tail fallback.

## Q3 — Tests

Accepted ARGV_NAMED. The only changed existing test lines are `test_media_adapter_frames.py:289` and `:313`; both change only the expected interval. `diff-check.py` and direct diff inspection agree. The new unit test at `:330` covers six requested times, including both sides of 60 s. Both test-file hashes still equal `red-hashes.json`.

The actual Red receipt has eight assertion failures and 30 passes, with the differing values explicitly showing the missing `+D`. Its saved child exit is 1; the Red checker accepts all eight required titles. No setup, import or collection failure substitutes for the intended Red. Reviewer unit execution passes all 38 cases.

AC-160.8 (`test_video_real_ffmpeg.py:285`) generates a local 150 s, 25 fps clip with one keyframe, exercises the real service and adapter at 149999 ms, and compares decoded pixels with full-decode frame 3749. Its trace proves END_GAP ran. This is a meaningful guard against the shorter `T - S + 60 s` duration, which would stop around 120 s after seeking to K=0.

It is deliberately not a deterministic regression test for the old open-read flake: it passed at Red. The argv assertions and base/green stress comparison supply that proof. No claim that AC-160.8 alone reliably rejects the old behavior is accepted.

| Test file | Assertion strength | Basis |
|---|---|---|
| `tests/unit/test_media_adapter_frames.py` | Strong | Exact argv, return values, retry locations, call counts, errors and remaining deadlines; the new assertions directly pin the changed contract. |
| `tests/integration/test_video_real_ffmpeg.py` | Strong | Real pinned binaries and generated clips; exact decoded pixels, times, dimensions, negative cases and source-file preservation. |

## Q4 — Load proofs

Accepted GRAB_TRACE, TAIL_SIGNAL and NO_RETRY. The trace proxy delegates the original subprocess arguments and results and patches only the adapter module's subprocess name. Thread-local grab times bind worker-thread calls to the records. Reference decodes use the real subprocess module independently.

The base raw log contains four empty reads and one short read (1560 versus 2960 ms). Each has exit 0 and empty stderr, directly explaining both missing frames and an earlier-frame retry. The base module itself passed 21 tests; this is disclosed and is not presented as the reproduction.

After the fix, the independent probe confirms all 1000 bounded stress reads reach 2960 ms, and all 15 module packet reads have the expected bounded arguments and last times: 2960 for the short clips and 149960 for the long-GOP clip. The stress driver additionally compares every returned frame's pixels with an independently decoded reference. Each green module receipt has 22 passes and no FAILED/ERROR line. Recorded load minima, medians and maxima are all 100%, exceeding the approved 85% median threshold.

The trace checker returns exit 3 for a failed test without the signal; independent three-packet fixtures verify both modes. A signalled green failure or bad green packet read fails. Task row 5 preserves the load-run exit, checks the traces, and cannot turn its diagnostic rerun into success. No diagnostic rerun or 800-sequence reproduction retry was triggered. No timeout, tolerance or END_GAP constant changed.

Both drivers clean up in `finally`, using Session 90's unchanged Busy implementation: owned launcher handles and interpreter handles validated by parent/creation identity. The four proof receipts report zero launchers and interpreters left; before/after snapshots for rows 2 and 5 also show zero. No process-name kill is used. The reviewer started no load children.

## Q5 — Registers and records

Accepted the registration and resolution. `vtf-meu-register.txt` records MEU-160 at 9.45; `vtf-status-160-1.txt` shows `pending`. The registration script uses `tools.meu_status.model.load/save`; row 6 uses `tools/meu_status.py update` to reach `ready_for_review` with the plan. Its selftest passes after registration and currently. Generated surfaces pass the independent render check (160 MEUs, 12 phases).

`vtf-issue-resolve.txt` binds the write to row 0's register hash and reports seven leaf differences. Independent parsed comparison confirms only the target issue changed, in the five authorized fields: status, verification, resolution_path, meu_links and root_cause. It is resolved, links MEU-160 and records the measured cause. `issue_triage.py render --check` independently passes.

The grouping diff changes only row 93 at line 165. The Phase 9 section, Delivered note, MEUs row, matrix 9.45 and rendered summary match the plan's file scope. No unrelated issue or grouping row was changed.

## Q6 — Gate

Accepted the fresh gate. `vtf-gate-h1.txt` lists 24 steps, all exit 0, with nonempty individual receipts and equal before/after identities. The reviewer obtained that same identity independently.

| Check | Actual recorded result |
|---|---|
| Full Python suite | 3119 passed, 37 warnings in 253.47 s; `py-tests: D6 argv exit 0` |
| Targeted frames | 60 passed, 16 warnings in 8.98 s |
| UI canon | 2 test files, 14 tests passed |
| Format/lint/types | 13 files formatted; lint clean; pyright 0 errors, 0 warnings |
| Selftests | All nine exit 0; Red grammar: 81 fixtures, 0 wrong |
| Scope/eol/renders | All pass; 18 eol scope paths |

The base full suite had 3112 passes; the seven added cases explain the final total. The baseline failure excuse set is empty, and the final full suite passed its first D6 invocation. No failure was waived or hidden by the wrapper's fallback branch.

The omitted UI, OpenAPI and MCP gates have a sound scope basis: all 629 recorded files and path membership remain unchanged. UI canon still ran because it consumes the changed registers. Running it from `ui/` preserves the intended test selection. No full-gate rerun was needed for this read-only review.

## Q7 — Safety and fidelity

Accepted byte preservation and scope. The eol check passes; product/doc files retain the named CRLF and both test files and YAML retain LF. Both Red hashes, the three baseline-copy hashes, nine read-only/pinned hashes and eight foreign-file hashes independently match. The untracked plan folder is included in the reviewed state; foreign plans remain outside this review. Every nonsecret dirty path is within declared scope, closeout paths, the plan folder or the original foreign list. HEAD remains baseline.sha on main and the index has no staged delta. Executed row cells contain no commit/stash/revert; evidence shows no such operation for this work.

New/changed text contains no absolute home path or personal email. Secret files were never opened. Test clips come from lavfi; services use fake units of work and explicitly temporary inboxes. The new tests and load proofs use no network or real application data. This reviewer made no network requests, started no app/backend, and wrote only beneath `C:/Temp/av-kit`.

All disclosed departures are sound: the stale plan queue sentence is superseded by D-1142; the Status sentence does not alter behavior; the extracted row scripts preserve their validation cells verbatim (independently checked for rows 0–6 and H1-2); byte edits preserve anchors and line endings; the extra waits, scope checks and busy snapshots add observations without replacing the cell checks; the full S4 check ran before row 2 completed; CRLF in `red-hashes.json` does not affect its parsed hashes; actual execution dates are correct; `ui-canon` has the right cwd; moved citations are mapped accurately. None weakens an acceptance check.

Not inferred: a lifetime guarantee against every future media format or environment. These finite load proofs establish the approved threshold on the pinned binaries, supported by the source-level fix and unchanged deadline behavior. No required gap remains in this review's scope.

## Checklist Results

The commands below were executed with `PYTHONDONTWRITEBYTECODE=1`, `ELECTRON_RUN_AS_NODE` unset, offline uv with its cache under the review directory, and TMP/TEMP at `C:/Temp/av-kit/video-tail-frame/exec-review/tmp`. `PLAN` in explanatory prose means the reviewed plan directory; recorded command fields use actual paths.

### Information Retrieval (IR)

| Check | Result | Procedure | Exit | Evidence |
|---|---|---|---|---|
| IR-1, IR-4: implementation and regression scope | pass | Codex compared current diff with FIC, baseline copies and read-only consumers | null | Exact one-line product change plus docstring; all 13 ACs accounted for above |
| IR-2, IR-3, IR-6: public boundary changes | n/a | No new route, public input, schema or persistence operation | null | Existing API/core/port hashes unchanged |
| IR-5: test rigor | pass | Codex audited both complete test files, fixtures and reference decodes | null | Strong ratings above; genuine assertion Red and independent 38-test Green |
| IR-7: coverage and deferrals | pass | Codex mapped all AC rows to source and receipts | null | No dropped acceptance criterion; H2 and upstream follow-up retain their supplied scope |

### Design Review (DR)

| Check | Result | Procedure | Exit | Evidence |
|---|---|---|---|---|
| DR-1–8: claim/state, references, robustness and freshness | pass | Codex compared handoff claims with raw receipts, current files and independent probe results | null | Counts agree; exact tested_state match; disclosures do not weaken checks |

### Post-Implementation Review (PR)

```json
{"schema_version":"evidence.v1","check_id":"review-lightweight-checks","command":"rtk proxy pwsh -NoProfile -File C:/Temp/av-kit/video-tail-frame/exec-review/run-checks.ps1","cwd":"P:/av-kit","scope":"identity; diff/eol checks; nine plan-script selftests; unit frames file; both register render checks","phase":"targeted","exit_code":0,"result":"pass","tested_state":"9c655bdf6ac2436308e20d4b889268e051d4e19d+6b06b8a25e513a5e2073813d4eedf4a659e77acd4f791ec51559a8dec0331ea2","output":"38 passed in 0.17s; diff-check: 0 problem(s); eol-check: 18 scope path(s), 0 problem(s); all nine selftests exit 0; known-issues.md up-to-date; SSOT 160 MEUs, 12 phases, rendered regions match; identity exactly matches gate."}
```

```json
{"schema_version":"evidence.v1","check_id":"review-independent-evidence-probe","command":"rtk proxy uv run --no-sync python C:/Temp/av-kit/video-tail-frame/exec-review/probe.py","cwd":"P:/av-kit","scope":"existing stress/module logs, baseline/Red/pinned/foreign hashes, skip membership, extracted validation cells, RULE-3 fixtures, parsed issue delta and safety scan","phase":"targeted","exit_code":0,"result":"pass","tested_state":"9c655bdf6ac2436308e20d4b889268e051d4e19d+6b06b8a25e513a5e2073813d4eedf4a659e77acd4f791ec51559a8dec0331ea2","output":"400 base sequences: 5 bad; 1000 green sequences: 0 bad; every interval correct; five green modules: 22 armed/passed each and 3 correct packet reads each; 629 skip hashes and membership unchanged; 8 foreign hashes unchanged; both independent RULE-3 fixtures exit 3; gate 24 steps all exit 0; only target issue/five allowed fields changed; no absolute home path or personal email detected; PROBE PASS."}
```

The first uv attempt could not access the default user cache (exit 2). The reviewer moved UV_CACHE_DIR under the permitted review directory and reran successfully with UV_OFFLINE=1. That was review setup, before any product test, and does not alter the product environment identity or count as an execution-proof retry.

## Verdict

`approved` — the delivered work achieves the registered intent; no findings. The coordinator may validate and publish this report, record round 1, and continue the already authorized closeout. No corrections are requested. No push is authorized.

🕐 Completed: 2026-11-18 10:59 (EST)
