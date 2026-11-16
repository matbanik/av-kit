---
date: "2026-11-15"
review_mode: "plan"
target_plan: "docs/execution/plans/2026-11-15-capture-inbox-probe/implementation-plan.md"
verdict: "approved"
findings_count: 0
template_version: "2.2"
requested_verbosity: "standard"
agent: "codex-independent-reviewer"
loop_id: "cip-plan-2026-11-15-capture-inbox-probe"
round: 3
---

# Critical Review: capture-inbox-probe

> **Review Mode**: plan
> **Verdict**: approved

## Scope

**Intent anchor:** one inbox file that the probe cannot read never fails the capture list: every readable shot still lists through the API and MCP, the bad file is skipped with a fixed, path-free message and one count-only log line, and it is tried again on the next scan. A scanned or registered JPEG, MPO or PNG with an EXIF orientation tag is recorded, viewed, downloaded, copied, marked, cropped, baked and exported in the frame the GUI shows, an annotated copy baked in another frame is rebaked by the next scan, and the user's file is never rewritten.

Independent Codex/OpenAI recheck of Claude Code/Anthropic's working-tree plan and task, all six plan-local scripts, the relevant capture adapter/service/port and API/MCP/GUI call chains, existing pins and fakes, Session 75 grouping, issue records, build-plan rules, supplied Pillow/Chromium and expert-pass receipts, and round 2's report. Applied PR-1 to PR-9 and the Materiality Gate, with the final-round bar specified by Mat.

Intent achieved: **yes**, as a plan-readiness judgment. **R2-F1 is fixed; R1-F1 remains fixed.** No new findings and no unresolved High or Critical defect. The original Findings table and round-2 recheck below are unchanged history; the round-3 dispositions govern. `findings_count` counts current open findings.

All writes were under `C:/Temp/av-kit`. No repository edits, product suites, dependency operations, network access, commits or forbidden-file reads. The new production helpers/tests do not exist yet. The recovery probe models the specified design with real Windows files; it is not an implementation or Electron pass. The coordinator owns the canonical copy.

## Findings

| # | Severity | Blocking | Kind | Finding | File:Line | Recommendation | Status |
|---|---|---|---|---|---|---|---|
| R1-F1 | High | yes | behavior | **Automatic stale rebaking can destroy the previous annotated copy on an unsuccessful scan.** STALE_BAKE calls the existing `_rebake_annotated` before rewriting the sidecar and promises that any failure leaves both files unchanged. That helper bakes directly to the live annotated path. The real PNG and lossy writers overwrite that path and unlink it after an encoding `OSError`; the helper can also delete old-format siblings before the sidecar is safely published. A disk-full/failed write during an ordinary list therefore removes the previously usable copy while the database still points to it. A subsequent in-place sidecar write can also truncate the saved marks before failing. The lock and database unit of work do not undo these filesystem writes. This breaks **AC-146.26**, `STALE_BAKE`, and D-909's safe retry contract. The scratch probe of the existing helper and PNG writer confirms that the old annotated path is absent after the injected encoding failure. | docs/execution/plans/2026-11-15-capture-inbox-probe/implementation-plan.md:130; implementation-plan.md:232; packages/core/src/avkit_core/services/capture.py:2024; packages/infrastructure/src/avkit_infra/capture/adapter.py:841 | Specify staged image and sidecar writes with safe publication/recovery; retain the old image, saved marks and required siblings until replacement succeeds, and restore the prior state on a later failure. Extend AC-146.26 with a bake that writes before raising and failures during sidecar publication, including an annotated-format change. Check original, sidecar, annotated bytes and row paths, then prove a later scan succeeds once and the following scan does not rebake. | open |

## Recheck (round 2)

### Prior Pass Summary

| Finding | Prior Status | Recheck Result |
|---|---|---|
| R1-F1 | open | fixed |

### Confirmed Fixes

- `STAGED_REBAKE` now writes to separate image and sidecar names, keeps the old pair until publication and rolls completed steps back in reverse (`implementation-plan.md:131-135`). It derives the format from the existing copy, preserves the saved annotation payload and never calls the destructive sibling-deleting helper. AC-146.25/.26 require byte/path checks, late-publication failures and a successful retry followed by no second rebake (`:236-237`). Six modeled forward failures preserved the old pair; seven ordinary interruption boundaries retained the saved marks and a recoverable image/marker state.
- The Electron row now explicitly adds `spawnSync` to the existing import (`implementation-plan.md:155`, `task.md:48`). The prior nonblocking import note is resolved.

### New Findings

| # | Severity | Blocking | Kind | Finding | File:Line | Recommendation | Status |
|---|---|---|---|---|---|---|---|
| R2-F1 | High | yes | behavior | **Recovery can make one annotated shot fail every capture list on Windows.** Step 7 permits failed prior-file deletion, but the next scan's recovery unconditionally unlinks the leftovers before RECONCILE. A read-only old copy can be renamed to `.rebake-prior` successfully; its later unlink raises `PermissionError` (WinError 5), including on the next scan even after both new live files were published successfully. A prior file opened without delete sharing likewise makes restoration of a missing live file fail (WinError 32). Recovery is outside the stated stale-pair eligibility check and has no specified failure outcome; allowing the exception out fails API/MCP listing, while catching it and continuing into existing RECONCILE clears the still-missing derived path and loses the row's recovery link. This violates **AC-146.26**'s list-survives/retry/path-preservation contract and `STALE_BAKE`. The native scratch probe reproduced both Windows errors; `_unlink_if_file` itself does not suppress them. Confidence: High. | docs/execution/plans/2026-11-15-capture-inbox-probe/implementation-plan.md:135; implementation-plan.md:133; implementation-plan.md:237; packages/core/src/avkit_core/services/capture.py:645; packages/core/src/avkit_core/services/capture.py:2213 | Define a per-shot recovery failure result before reconciliation: cleanup is best effort, a failed restore retains its prior file and both row links, and the unrecovered shot bypasses derived-path clearing/restaging for that scan. Account for recoverable I/O failures with the fixed count-only failure event and continue listing other shots. Extend AC-146.26 with a read-only prior beside valid live files and a locked prior with a missing live file; assert list success, preserved links/marks, dedup, and restoration plus one rebake after unlocking. | open |

This is a new availability/recovery-state failure introduced by D-910, rather than a further variant of R1-F1's in-place encoding/truncation loss. It needs no new product preference or scope decision. PR-4 and PR-8 are relevant checklist observations; the registered violated contract is **AC-146**.

## Recheck (round 3)

### Prior Pass Summary

| Finding | Prior Status | Recheck Result |
|---|---|---|
| R1-F1 | fixed | fixed |
| R2-F1 | open | fixed |

### Confirmed Fixes

- **R2-F1:** Every discard of a `.rebake-` name now uses `_discard_rebake`, which catches `OSError` and never raises. Recovery runs per shot before RECONCILE and returns `RecoverResult(restored_all, io_failed)`. A failed restore keeps its prior file and both row links and bypasses clearing and rebaking for that shot; failed cleanup alongside valid live files permits normal listing. Recovery and restage failures share the path-free, count-only deduplicated failure event (`implementation-plan.md:130`, `:133`, `:135-138`; `task.md:52`). This closes the two failures identified in round 2 without suppressing other shots' work.
- **R2-F1 tests:** AC-146.26(f) requires both a real read-only prior and a source-specific patched unlink; (g) requires a source-specific patched restore failure with the live copy absent. Both require a second stale shot to rebake, list success, preserved links/marks, one warning followed by none, and a stable retry after release; (g) requires exactly one restore/rebake (`implementation-plan.md:185`, `:240`). The tests explicitly distinguish a simulated lock from a native lock.
- **R1-F1:** Staged image/sidecar writes, old-pair retention, reverse rollback and unchanged destination format remain specified. No regression to baking onto the live copy or deleting siblings (`implementation-plan.md:131-134`, `:239-240`). Catching cleanup failures does not undo a completed publish or discard a prior needed for a failed restore.
- The scratch model reproduced native read-only deletion error 5 and locked-prior restoration error 32 as negative controls. The revised recovery branches passed both and a patched unlink scenario, preserving links and marks, isolating the other shot and deduplicating warnings. This supports the design; execution still must implement and pass the planned ACs.

### New Findings

| # | Severity | Blocking | Kind | Finding | File:Line | Recommendation | Status |
|---|---|---|---|---|---|---|---|

None.

## Q1 — Goal and AC coverage

Accepted: AC-145.1-.15 and rows 2/3 cover SCAN_SKIP, KEEP_ROW, PROBE_FIXED, SKIP_LOG, API listing and next-scan retry; the unchanged MCP list pin reaches that API. AC-146.1-.23/.28 cover shown-frame dimensions, views, downloads, Copy's source bytes, crop, marks, bake, export, flatten and ICC. AC-146.24-.27 cover markers and automatic stale-copy repair, including failures. The automatic scan and orientation paths do not write the original. Explicit user-requested flatten retains its established write/backup behavior.

Not accepted: no remaining contradiction with the goal was demonstrated. Product behavior is to be established during execution, not inferred from passing plan checks.

## Q2 — MEU-145 design

Accepted: the per-child try includes both resolve and probe; adapter file/open/load failures become fixed `InboxPathError` messages, covering OSError, SyntaxError, ValueError and DecompressionBombError. The broad normalization is scoped to file/image operations; repository/upsert operations remain outside that catch. KEEP_ROW preserves an existing unreadable shot while a vanished original follows the existing deletion rule (`implementation-plan.md:118-121`).

SKIP_LOG compares sets per service instance, resets on a clean scan and logs a later recurrence; a new instance has its own dedup lifetime. Count-only arguments expose no bad path, name or Pillow text. Accepted within that boundary; unrelated programming failures are not a reason to widen the service catch. No unresolved MEU-145 defect.

## Q3 — MEU-146, publication and recovery

Accepted: SHOWN_FORMATS reads the EXIF block before load, with a guarded parser and safe tag-1 fallback; it excludes the XMP/raw-profile/late-IDAT/doubled-prefix cases in the supplied Chromium receipts. The tags 2-8 transpose map matches installed Pillow's map; PROBE_SWAP swaps only 5-8. SHOWN_TAG never raises. READ_SHOWN keeps the unchanged cases byte-exact, carries ICC on turned encodes and returns original bytes on header/load failure. The original-image route feeds MCP image and unmarked GUI Copy; pixel operations reach SHOWN_OPEN (`implementation-plan.md:122-128`, `:139-141`).

Accepted: marker comparison catches tags 2-4 even without size changes, successful repair converges after one scan, and saved sidecar annotations remain intact. Temporary names cannot be scanned, writers use explicit formats, staged publication retains the old pair and format, and recovery now isolates Windows I/O errors. Revert may trigger one extra marker repair; crop/convert sidecars describe untagged output. No remaining R1-F1 or R2-F1 failure in the specified branches. Undeletable scratch leftovers and existing explicit-save/revert failure behavior remain disclosed residuals (`implementation-plan.md:330-341`).

## Q4 — Tests and session gate

Accepted: Red tests use catch-then-assert and in-body new-name imports; guards already satisfied run beside changing tagged cases. The two moved existing pins are the only planned assertion changes. The builder's metadata assertions prevent a fixture that lost its tag from silently validating the Chromium premise. AC-146.26 now supplies the missing recovery adversaries as well as partial writes, late publication, format changes, retry and no-repeat checks.

The gate includes Python types/lint/full pytest, UI types/lint/Vitest/build, MCP types/build/tests, OpenAPI --check, comparison of route comment changes with row-0 bytes, registers and the real Electron capture test file. Commands use pwsh, clear ELECTRON_RUN_AS_NODE and run Python tests through uv. The Red parser rejects setup failures and missing required assertion failures; its 71 selftest fixtures passed. The id-length boundary selftest and both PowerShell parser checks passed. No product Red/Green or Electron execution is claimed here.

## Q5 — Order, safety, registers and size

Accepted: baseline shapes precede row-0 copies and refuse a rerun once new names exist. Copies, anchors and dirty-path hashes bind the scope to row-0 content; HEAD movement and other plan folders are reported without requiring a clean tree. Outside-scope dirty bytes are protected, and route comparison uses its row-0 copy. The read-only shapes probe found all required shapes and all five planned new files absent.

CRLF changes require `newline=''` and byte checks. Planned writes stay within the declared files, plan/closeout artifacts, normal build/test outputs and scratch area. MEU updates use `meu_status`; issue resolution uses the issue-triage model, expected register hash, exclusive handle and staged parsed-difference checks. MEU-145 precedes MEU-146 with compaction at that boundary; the related session remains workable. Session 87's preceding commit, existing execution authorization and this session's uncommitted closeout are accepted as supplied. No remaining ordering or safety blocker.

## Checklist Results

Manual observer: **codex-independent-reviewer**. Procedure: compare the entire current plan/task and the six scripts with the named source contracts, actual production call chains, existing tests/fakes and supplied receipts; recheck both prior findings against the new recovery branches and negative ACs. Manual exit: null. Results below judge readiness of the plan, not completion of implementation.

| Check | Result | Evidence |
|---|---|---|
| PR-1 Plan/task alignment | pass | Row 4 names all three new recovery/staging helpers; row 2 owns AC-146.26 cases. |
| PR-2 Not started | pass | Implementation rows unchecked; current shapes probe passes; all five new files absent. |
| PR-3 Task contracts | pass | Deliverables, roles, validation commands and dependencies are present. |
| PR-4 Validation realism | pass | AC-146.26(f/g) now assert both concrete recovery failures, another shot's progress, preserved state, dedup and retry. |
| PR-5 Source-backed planning | pass | Build-plan, local rulings, HDP hand-over and supplied measurements support the choices; no extra mandatory-human hit demonstrated. |
| PR-6 Correction readiness | pass | Both finding ids retained; revised contract and task carry the requested corrections; paperwork excluded per Mat's scope. |
| PR-7 Scope discipline | pass | Residuals are identified and do not waive recovery availability or link preservation. |
| PR-8 Reachability and failure safety | pass | list_shots -> scan_inbox -> recovery before RECONCILE; failed restore bypasses clearing/restaging only for that shot. Native adversaries validate the need for the branches. |
| PR-9 Contract consistency | pass | STAGED_REBAKE governs the revised cases and task row; no materially conflicting live contract found. |
| Product execution | n/a | Plan review only; suites, dependency sync, baseline and session-gate execution prohibited by the review request. |

### Supporting probes

| Probe command (P:/av-kit) | Exit | Decisive observation |
|---|---|---|
| `rtk proxy .venv/Scripts/python.exe -B C:/Temp/av-kit/capture-inbox-probe/review/r3_recovery_probe.py` | 0 | Native negative controls: WinError 5 and 32. Revised recovery model: three scenarios pass; both lists survive; links/marks kept; other shot rebaked; warning once; stable unlock retry. |
| `rtk proxy .venv/Scripts/python.exe -B C:/Temp/av-kit/capture-inbox-probe/review/r2_static_audit.py` | 0 | Four Python scripts parse; `shapes wrong (S7): []`; `actual-baseline-shapes-exit 0`; five new files absent. |
| `rtk proxy .venv/Scripts/python.exe -B docs/execution/plans/2026-11-15-capture-inbox-probe/red-check.py --selftest` | 0 | 71 fixtures: 21 positive, 50 negative; 0 wrong. No pytest invoked. |
| `rtk proxy .venv/Scripts/python.exe -B docs/execution/plans/2026-11-15-capture-inbox-probe/id-length.py --selftest` | 0 | Four boundary cases; 0 wrong. No pytest collection invoked. |
| `rtk proxy pwsh -NoProfile -File C:/Temp/av-kit/capture-inbox-probe/review/r3_parse.ps1` | 0 | `baseline.ps1 errors=0`; `session-gate.ps1 errors=0`. Neither parsed script executed. |

```json
{"schema_version":"evidence.v1","check_id":"cip-r3-recovery-model","command":"rtk proxy .venv/Scripts/python.exe -B C:/Temp/av-kit/capture-inbox-probe/review/r3_recovery_probe.py","cwd":"P:/av-kit","scope":"Revised STAGED_REBAKE recovery model; scratch files only; native Windows negative controls plus patched unlink","phase":"targeted","exit_code":0,"result":"pass","tested_state":"plan SHA256 7c97d19140d3260c4478262fbcc9157f569d0637866b3d54b132cdf79458afe4; task SHA256 bc37286135473125d884f1c27904589618da4834d20348b3dc57a99a7cb36329; design model, not product execution","output":"negative-control readonly native: WinError 5; negative-control locked native: WinError 32; readonly-native, readonly-patched, locked-native: two lists survive; links/marks kept; other rebaked; warning once; unlock retry stable; recovery model: 3 scenarios passed; product code not executed","fresh":true}
```

## Assumptions and residual risk

Accepted as supplied: grouping rulings, authorized default hand-over, execution order, unrelated dirty workstreams, and the coordinator's execution Status update. No new human decision is required by this review. Implementation still must satisfy the planned tests and full gate. Existing lossy re-encoding, MPO-first-frame, imported-file/profile and explicit-save/revert limitations are disclosed in the plan; approval does not claim those residuals are fixed.

## Verdict

**approved** — R2-F1 is fixed and R1-F1 remains fixed. No new blocking defect. This completes final permitted plan-review round 3; it does not certify implementation or authorize a commit/push.

Report: `C:/Temp/av-kit/cip-plan-review-round-3.md`. The coordinator copies it to `.agent/context/handoffs/2026-11-15-capture-inbox-probe-plan-critical-review.md`.
