---
date: "2026-11-18"
review_mode: "plan"
target_plan: "docs/execution/plans/2026-11-17-video-tail-frame/implementation-plan.md"
verdict: "approved"
findings_count: 1
template_version: "2.2"
requested_verbosity: "standard"
agent: "codex-independent-reviewer"
loop_id: "vtf-plan-2026-11-17-video-tail-frame"
round: 2
---

# Critical Review: video-tail-frame

> **Review Mode:** plan
> **Verdict:** approved

## Scope

**Intent anchor:** `FFmpegAdapter._last_video_ms` asks ffprobe for the packets from `S = max(0, T - 60 s)` with an end (`-read_intervals S%+D`, D = T + 60 s, which ffprobe counts from the keyframe K at or before `S`), not from `S` with no end, so the END_GAP retry finds the clip's last video packet on a host loaded to at least 85 % as on an idle one; 1000 adapter sequences under load give zero empty or short packet reads, and five traced runs of `tests/integration/test_video_real_ffmpeg.py` under load pass with zero failures; a failure that lacks the watched signal is never counted as a pass (Session 90 RULE-3); only `adapter.py:644` and its docstring change in the product, two named unit assertions change their expected interval, and no API route, OpenAPI document, MCP tool, setting or schema changes; scripts and tests prove it, with no manual check.

Complete rolling round-2 review of the working-tree implementation plan, task and six existing plan-local scripts. Claude Code/Anthropic authored the plan; Codex is its independent reviewer. Applied the Materiality Gate and PR-1 through PR-9 within Mat's explicit substance-only scope. No Critical finding or unresolved High finding remains. The Findings table retains the original round-1 finding, its original diagnosis and references, with status updated to fixed; its historical blocking rating is not a current blocker.

The 13 ACs and 24 task rows remain unstarted. Read the source issue and grouping Session 93, the relevant HDP rules, adapter/callers/tests, Phase 9 canon, saved ffprobe source, probes and expert advice. The fresh independent check exercised registration in scratch, the committed-slug fallback and all six existing script selftests. No pytest, Vitest, npm, uv sync/lock, network request, load-worker launch or live registry render ran. All writes were under `C:/Temp/av-kit`; forbidden files were not opened. The coordinator owns canonical publication and ledger recording.

## Findings

| # | Severity | Blocking | Kind | Finding | File:Line | Recommendation | Status |
|---|---|---|---|---|---|---|---|
| R1-F1 | High | yes | behavior | **Successful MEU registration makes the mandatory final gate fail.** Confidence: High. `meu-register.py --selftest` calls `build(REPO, "MEU-160", "9.45", ...)` and requires three successful edits against the current repository. Row 1 creates that exact registration. Consequently H1-2's required selftest refuses the now-correct state with `MEU-160 is already registered`, reports `FAIL the three edits build on the files now`, and exits 1. Reproduced using only scratch copies of the three registration inputs after applying the real `build()` output. The final gate stops at its static selftests even if the adapter fix and every runtime proof succeed. This prevents completion of the AC-160.11 registration work through the mandatory session gate; PR-4 is not satisfied. | docs/execution/plans/2026-11-17-video-tail-frame/meu-register.py:275-279; docs/execution/plans/2026-11-17-video-tail-frame/task.md:83; docs/execution/plans/2026-11-17-video-tail-frame/implementation-plan.md:331 | Make the selftest use an isolated unregistered fixture or row-0 copies for its positive registration case. Keep the second-registration refusal case. Prove the unchanged selftest passes both before and after a valid registration, including after status advances, without modifying the live registry or omitting the gate. | fixed |

## Q1 — Goal and proof coverage

Accepted: AC-160.1–3 and rows 3/4 bind the exact bounded interval and named unit changes; AC-160.4/5 bind reproduced base failure and 1000 clean adapter sequences; AC-160.6/9/10 bind base tracing, five passing traced module runs and RULE-3. AC-160.7/11–13 bind scope, registration, resolution and line endings. Each has an execution row and scripted proof. R1-F1 no longer prevents the mandatory gate. No clause is rejected; this approves the plan's ability to deliver, not an unrun implementation.

## Q2 — BOUNDED_TAIL_READ, TAIL_SAME_ANSWER and TAIL_DOC

Accepted: saved `ffprobe-master.c:3313-3341` sets all duration/end fields for `S%+D`; the open branch at `:3344` does not. The stopping logic at `:1873-1887` measures D from the first selected packet after seeking, giving K + D. D = T + 60 s is a relative duration, not an absolute end timestamp. For the specified END_GAP tail case it retains the last packet of the intended open read.

The saved one-keyframe probe distinguishes the wrong 120 s duration (last 119840 ms) from the selected 209.999 s duration (last 149960 ms). The proposed line in `diff-check.py:42` uses `_seek_text` twice and preserves the 12-space indentation and CRLF. TAIL_DOC avoids a fixed two-minute span. No material objection.

## Q3 — Reproduction, Red honesty and signal tracing

Accepted: row 2 requires base reproduction, rather than treating the historical probe as execution proof. The saved loaded probe found eight empty packet reads with exit 0 and empty stderr; the interval probes and source support the cause. `packet-stress.py:139-143,157-163,194-213` uses the real adapter with independent full-read packet and full-decode pixel references. The two named unit changes and six new cases fail specifically for the missing end; row 3's required Red reader rejects setup/collection failures.

GRAB_TRACE delegates subprocess arguments unchanged and associates records with the test and grab time (`grab_trace.py:186-203,210-231,251-267`). TAIL_SIGNAL distinguishes bad END_GAP reads from other failures. Carry-forward limitation, already recorded in round 1: module partial-read classification uses a modal estimate, not independent ground truth; the stress proof and real pixel assertions supply independent checks. No new blocker.

## Q4 — Load, cleanup and RULE-3

Accepted: the drivers import Session 90's measured CPU sampler and owned-process cleanup; each waits for 85%, samples during work and cleans up in `finally` (`load-run.py:83-151`, `packet-stress.py:178-250`). The peer holds launcher/interpreter handles and verifies ownership before termination (`2026-11-17-test-run-reliability/load-run.py:258-327`). Success requires no surviving busy process.

D-1169 explicitly selects median load at least 85%, with minimum/median/maximum reported; it does not prove every instant exceeded 85%. Row 5 combines the loader and trace exits. RULE-3 branches stop with exit 3 regardless of the diagnostic rerun's result; an unsignalled failure cannot become a pass. Synthetic selftests passed; fresh loaded acceptance remains execution work. No new blocker.

## Q5 — Scope, named assertions and shared main

Accepted: the three source hashes still match the plan's prefixes. `diff-check.py:79-124` permits only the named adapter code replacement plus its docstring, the two named existing assertion replacements and test insertions. S3 freezes test bytes after Red. Its scope check and H1-4's skip hashes cover unrelated product/API/MCP/UI paths.

Row 0 is sufficient for the stated moved-HEAD scenario: it re-reads cited lines and current bytes, validates the old END_GAP bindings, pins actual scope/dirty hashes and copies, and checks free registration slots. S4 binds subsequent work to content and preserves other sessions' changes. Earlier sessions' commits are not a defect. No new scope objection.

## Q6 — Registration and issue resolution

Accepted: the registration edits still use `tools.meu_status.model.load/save`, prove a byte-identical unchanged round trip and limit parsed YAML differences to the entry and P2 range. The phase/matrix edits preserve CRLF, exact insertion points and duplicate refusals. Rows 1/6/H2-2 render/check generated surfaces and now run the corrected selftest after status writes; row 6's narrowly configured resolver supplies `meu_links` and the measured `root_cause`.

R1-F1 is fixed. `meu-register.py:273-296` creates an unregistered git fixture; `:324-336,374-400` use it for positive, taken-matrix and moved-id cases. `:337-352` tests the live tree only for its current registration state. The isolated positive build is no longer invalidated by registration or status advancement. No new material defect in `fixture_rev()` or `--live` was demonstrated. The history fallback was verified against a real committed slug; no new commit was made.

## Checklist Results

Manual observations were performed by `codex-independent-reviewer`; null exits are source review, not executed product tests.

| Check | Result | Command / procedure | Exit | Evidence |
|---|---|---|---|---|
| PR-1 Plan/task alignment | pass | Read complete plan/task; map all ACs to rows | null | Same reproduction → Red → Green → load proof → registration closeout sequence. |
| PR-2 Not started | pass | Inspect task statuses, adapter/test bytes and declared future helpers | null | All 24 task rows unchecked; current adapter still has the open interval and both existing assertions retain old values. |
| PR-3 Task contracts | pass | Read owner/deliverable/validation/dependency cells and creation inventory | null | Existing scripts and scheduled helper creation have concrete sources and rows. |
| PR-4 Validation realism | pass | `rtk proxy .venv/Scripts/python.exe -B C:/Temp/av-kit/video-tail-frame/review/round2_probe.py` | 0 | All four scratch registration states and repository selftest pass; duplicate-acceptance mutation fails as required. |
| PR-5 Source-backed planning | pass | Compare issue/grouping, HDP, product/canon and saved FFmpeg/probe evidence | null | Handed briefs retain their M hits; named assertions and exclusions match scope; no additional mandatory-human hit demonstrated. |
| PR-6 Corrections readiness | pass | Recheck R1-F1, its changed callers and proof sources within Mat's substance-only scope | null | Rows 1, 6 and H2-2 check after their writes; H1-2 retains the selftest. |
| PR-7 Scope discipline | pass | Compare exclusions, production caller chain, row-0/S4 bindings and diff checker | null | No required delivery hidden as a deferral; shared-main baseline is refreshed. |
| PR-8 Observable/control chain | pass | Inspect service → adapter → subprocess → tracer/stress/checkers and negative oracles | null | Real producer paths and refusal exits remain; independent duplicate mutation proves the new live check can fail. |
| PR-9 Named contracts | pass | Compare single-statement contracts, ACs and task references | null | No competing material behavior definition demonstrated. |
| Six existing script selftests | pass | `rtk proxy .venv/Scripts/python.exe -B C:/Temp/av-kit/video-tail-frame/review/round2_probe.py` | 0 | Registration and five other existing scripts pass with zero selftest failures. |
| Runtime acceptance and product suites | n/a | Not run under read-only review scope | null | No fresh 1000-sequence, five-run or full product-gate claim. |

### Durable evidence

Python probes used `-B`, `PYTHONDONTWRITEBYTECODE=1`, UTF-8 and scratch TEMP/TMP. Tested state: plan SHA-256 `92d519473958dd2fb795d504a093cd4b3ecf39ff8bd02e1fc6efa336f9024851`; task `a70b433ffc3bf914252c486b907eb8f4d63edd38be414cd3f8a7386533664ac3`; registration script `a537ea9dae1ccb4a3fcde6b56aab34c0bf4a5eb42c0c1160c2914c75c9b6e4f9`. Watched plan, script, register and product/test hashes were identical before and after the probe.

```json
{"schema_version": "evidence.v1", "check_id": "vtf-r2-registration-regression", "command": "rtk proxy .venv/Scripts/python.exe -B C:/Temp/av-kit/video-tail-frame/review/round2_probe.py", "cwd": "P:/av-kit", "scope": "Six plan-local selftests; isolated registration/status cases; live duplicate negative oracle; real committed-slug fallback; no repository mutation or product suites", "phase": "plan-review", "exit_code": 0, "result": "pass", "tested_state": "plan 92d519473958dd2fb795d504a093cd4b3ecf39ff8bd02e1fc6efa336f9024851; task a70b433ffc3bf914252c486b907eb8f4d63edd38be414cd3f8a7386533664ac3; meu-register a537ea9dae1ccb4a3fcde6b56aab34c0bf4a5eb42c0c1160c2914c75c9b6e4f9", "output": "before, pending, ready_for_review, approved and repository registration selftests each exit 0 with 0 failures. Live duplicate-acceptance mutation is rejected with selftest exit 1. MEU-159 committed-slug fallback selects fc87056fbcb9069682de4406c344cb4df7a1c90f, parent of its first addition, with slug absent and correct YAML LF / document CRLF endings. Five other existing script selftests exit 0. Watched repository hashes unchanged. round2 probe: 0 failure(s).", "fresh": true}
```

## Recheck (round 2)

**Workflow:** `/plan-critical-review` recheck. **Agent:** `codex-independent-reviewer`.

### Prior Pass Summary

| Finding | Prior Status | Recheck Result |
|---|---|---|
| R1-F1 | open | fixed |

### Corrections Applied

- The positive build uses the isolated unregistered fixture, including the taken-matrix and moved-id cases (`meu-register.py:324-336,374-400`). The original second-run and CR refusals remain.
- `fixture_rev()` reads HEAD until registration is committed, then selects the parent of the first slug-addition commit; `write_fixture()` restores YAML LF and phase/matrix CRLF (`:273-296`). Missing/unusable history fails closed.
- The live check tests build success for unregistered input and duplicate refusal for registered input (`:337-352`); `--live` is confined to selftest use (`:416-424`). Independent mutation allowing duplicates was rejected.
- Plan `:170,235,332` and task `:70,72,80,83,96` carry the correction through baseline, post-registration, ready-for-review, final gate and approval. Nine selftests are named; `issue-resolve.py` is correctly excluded because it has none.

### New Findings

| # | Severity | Blocking | Kind | Finding | File:Line | Recommendation | Status |
|---|---|---|---|---|---|---|---|

No new findings. No additional requested change.

### Verdict

**approved** — R1-F1 is independently verified fixed and no evidence-backed High or Critical delivery defect remains. Executing the prescribed rows would deliver the registered intent. Runtime proof remains owed during execution; approval does not claim it has run.

## Open Questions and Residual Risk

None requiring a decision for plan approval. Carry forward the two already-observed limits: the module trace's modal short-read reference and the selected median CPU statistic. The independent full-read/pixel stress oracle and unchanged real module assertions remain the substantive safeguards. Only the scratch report and evidence were written; no repository artifact was changed.
