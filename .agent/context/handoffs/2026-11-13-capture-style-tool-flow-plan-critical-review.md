---
date: "2026-11-14"
review_mode: "plan"
target_plan: "docs/execution/plans/2026-11-13-capture-style-tool-flow/implementation-plan.md"
verdict: "approved"
findings_count: 3
template_version: "2.2"
requested_verbosity: "standard"
agent: "codex-independent-reviewer"
loop_id: "s71-plan-canonical-2026-11-13-capture-style-tool-flow"
round: 3
---

# Critical Review: 2026-11-13-capture-style-tool-flow

> **Review Mode:** `plan`
> **Verdict:** `approved`

## Scope

Round 3, the last permitted ledger round, rechecks F3 and round 2's two numeric notes, then examines only problems the corrections could introduce. Claude Code/Anthropic authored the plan; `codex-independent-reviewer` is its vendor-distinct independent reviewer. HEAD is `5e9ea7c520e02e856babe21d5116677a53bd108e`, on the user-specified `main` working tree. The untracked plan is still unstarted. The only other status path is the disclosed sandbox-only ignore discrepancy, `.claude/settings.local.json`; it was never opened.

**Intent anchor:** Session 71 makes colour apply on click and gives each tool its own remembered style. A swatch applies when it is picked, the hex field applies on Enter or blur, and one click or one scrub is one undo step; the Apply/Cancel gate goes. Arrow, Box, Highlight, Text and Pixelate each keep their own style as an app preference in the `capture` settings namespace, never in mark JSON. With a mark selected, a style control restyles only that mark; with none selected, it sets the active tool's style. The Pixelate block size gets the same scrub as Stroke and Size.

**Intent assessment (round 3): yes, as a plan.** Executing the specified contracts and tests would deliver the retained MEU-105 behaviour. F1 and F2 stay fixed; F3 is fixed by the shared GET filter and the expanded AC-105.32 schedules. No new High or Critical finding exists. This approves the plan, not an implementation or a full product gate.

The Findings table preserves the original defects and recommendations, with current statuses. Q1–Q11 retain prior accepted coverage and historical observations; the current reasoning, schedule evidence and answers to R1–R3 are in Recheck (Round 3). Earlier evidence blocks remain labelled by their original round and are not new execution claims.

All writes were under `C:/Temp/av-kit`. Fresh checks were targeted source reads, an independent in-memory schedule model, a read-only inventory, three explicitly permitted script selftests, and report/schema checks. `PYTHONDONTWRITEBYTECODE=1` was set for every Python probe/selftest. The selftests' scratch directories were under `C:/Temp/av-kit/s71/review`. No product suite, baseline/session gate, backend, MCP server, package manager, network request or clipboard operation ran. No capture inbox, app database, user settings file, prohibited private file or forbidden report content was read. The coordinator owns the canonical copy and ledger record. D-727 remains reserved for Mat's execution-budget and execution ruling.

## Findings

| # | Severity | Blocking | Kind | Finding | File:Line | Recommendation | Status |
|---|----------|----------|------|---------|-----------|----------------|--------|
| F1 | High | yes | behavior | **STYLE_STORE leaves successive commits to one leaf unordered.** The contract updates the cache immediately, sends one partial PUT per commit, and does nothing further on success; D-720 supplies no write queue or ordering mechanism. With Arrow armed and nothing selected, commit one stroke size and then another while the first request is pending. If the newer request reaches `set_namespace` first and the older one finishes afterward, the database retains the older preference while the cache shows the newer one. The next GET/reload therefore changes the tool back. Partial bodies protect different leaves, but cannot prevent this same-leaf overwrite. The existing single-commit AC-105.13/.21 and read-back AC-105.16/.22 can all pass without covering this schedule. The deterministic scratch schedule reproduced that disagreement. This defeats the remembered-style intent and AC-105's Tool style contract. | `docs/execution/plans/2026-11-13-capture-style-tool-flow/implementation-plan.md:169`; `:623`; `packages/api/src/avkit_api/routes/settings.py:41`; `packages/core/src/avkit_core/services/settings.py:230` | Specify ordering for overlapping style writes, such as a shared promise queue that sends each commit after its predecessor settles, retaining immediate local display and one partial PUT per commit. Extend the behavior oracle to make a second commit while the first is held pending and prove that the eventual GET and a remount retain the last choice. | fixed |
| F2 | Medium | no | behavior | **STYLE_API's strict integers expose an unhandled STYLE_SETTINGS overflow.** A proposed `SettingsPutIn` variant accepts a 401-digit JSON integer. It passes the planned `integer` type predicate and existing 4096-character cookie guard, but `_encode` calls `float(value)` before its range checks and raises `OverflowError`. The added integer/pattern checks alone do not turn this into the promised domain validation refusal. The API consequently returns generic 500 for an out-of-range style preference instead of the boundary inventory's 400. The in-memory probe confirmed the exception without opening a store. This affects the extreme-invalid-input cases of AC-105.3/.4; it does not prevent ordinary toolbar use. | `docs/execution/plans/2026-11-13-capture-style-tool-flow/implementation-plan.md:165`; `:166`; `:245`; `packages/core/src/avkit_core/services/settings.py:131` | For `integer=True` rows, check the integer and its bounds before converting to float, or explicitly translate overflow into a key-only `ValidationError`. Add a large-integer service/API case, preserving existing noninteger settings behavior. | fixed |
| F3 | High | yes | behavior | **STYLE_STORE lets a failure-refetch replace a newer commit.** After a failed PUT drains the queue, its GET snapshots the old server style. The user commits a new colour while that GET is pending; `setQueryData` shows it and a new PUT is queued. The old GET then replaces the cache. When the new PUT succeeds, the prescribed success path changes nothing, leaving STYLE_DISPLAY and STYLE_DRAW on the old colour although the server stores the new one. AC-105.32 queues both commits before the first drains and never drives this schedule. The synthetic schedule reproduced the disagreement; installed Query code confirms manual cache writes do not cancel the GET and its completion calls `setData`. This violates the AC-105 Tool style contract, particularly AC-105.13/.14/.15 and STYLE_STORE's immediate-display guarantee. | `docs/execution/plans/2026-11-13-capture-style-tool-flow/implementation-plan.md:169`; `:170`; `:172`; `:294`; `ui/node_modules/@tanstack/query-core/src/queryClient.ts:315`; `ui/node_modules/@tanstack/query-core/src/query.ts:880` | Specify reconciliation that cannot install a pre-commit snapshot over later optimistic leaves: cancel or generation-guard old reads, retain the need to reconcile failed leaves, and fetch authoritative state after the current writes drain. Add a behavior case making a new commit while the drain-time GET is held and assert fields and the next drawn mark retain the new value after its PUT succeeds. | fixed |

## Q1 — Goal and end-to-end traces

The previously accepted selected-mark and single settled tool-style traces are retained. F1's write ordering stays fixed. F3's separate overlap, a GET versus a later commit, is now covered by STYLE_STORE's shared query function and AC-105.32 (`implementation-plan.md:169,294`). Both STYLE_DISPLAY and STYLE_DRAW consume those protected styles (`:170,172`). No accepted goal/split contract was removed.

## Q2 — STYLE_SETTINGS

The opt-in fields, patterns, defaults and legacy paths accepted in round 1 remain. F2's overflow is fixed: compare the bounded `int` before `float()`, preserving the existing bool guard. The fresh in-memory implementation of that prescribed branch refused both signs of `10**400` with exactly `arrow_stroke is out of range`, retained bool refusal, and matched 616 legacy return/error/message outcomes for rows with `integer=False`. This tests the prescribed algorithm on the current encoder, not an implemented production patch.

AC-105.3 now explicitly requires a domain `ValidationError` for the positive huge integer. The negative huge integer is handled by the same lower-bound comparison; no need for a separate plan blocker because the named algorithm is explicit.

## Q3 — STYLE_API and STYLE_MCP

D-717 and the previously accepted API/MCP expansion are unchanged. Round 2's numerical note is fixed: both the boundary inventory (`implementation-plan.md:245`) and AC-105.4 (`:266`) require 422. This matches `DOMAIN_HTTP_MAP[ValidationError]` (`packages/api/src/avkit_api/errors.py:29`). No global handler change is needed or prescribed.

## Q4 — STYLE_MODEL and STYLE_STORE

The previously accepted exhaustive maps, fallbacks and module-scope settling write chain are retained. The new `capture-style-store.ts` also owns the counter and per-leaf latest entries; both hooks use its `fetchCaptureSettings()` (`implementation-plan.md:169`). Success counters distinguish success before GET start from success while GET is in flight; failure deletes only entries still owned by that commit. Recheck (Round 3) walks the requested schedules.

The Capture card keeps `asForm`'s seven-key projection, the separate draft, and its existing Save body (`useCaptureSettings.ts:39-55,76-95`). Only its query function changes. A style overlay cannot become part of the projected form or overwrite an unsaved draft. AC-105.23 remains the caller guard (`implementation-plan.md:285`).

Module state persists within a test file. AC-105.32 now explicitly requires settling every held request and calling `resetCaptureStyleStore()` before the next test. QueryClient clearing alone would not settle the queue; the stated teardown avoids that. No implemented hook exists yet, so these are contract/fixture conclusions.

## Q5 — Color and background commit events

Accepted named-pick commit/reset, hex Enter/blur validation and Escape/invalid-text restoration, separate well previews/native-change commit, background previews/Clear, and equal-value no-ops. AC-105.8-.11 check the visible mark and undo effects, rather than just callbacks.

The installed React DOM code supports the plan's event distinction: `color` is a supported text-input type (`react-dom-client.development.js:28051-28066`), routed through `getTargetInstForInputOrChangeEvent` (`:21270-21272`). Using React `onChange` as the commit would therefore also commit input previews. A native `change` listener and inert controlled-input `onChange` are sound. Actual OS-picker behavior remains execution evidence; it was not run during this review.

## Q6 — Target, display, drawing and text drafts

Accepted selected-mark-only history writes with no preference PUT, unselected-tool writes with no history entry, field display from the current target, drawing from validated tool styles, and the distinction between a new text draft and saved-text re-edit. AC-105.12-.17 cover these paths, and .14 includes Pixelate through Redact mode. No new mark field is required.

**Nonblocking wording correction:** the example at plan line 259 is not today's behavior: `optionGroups('text', arrow)` returns Color and Text, not Color and Stroke (`capture-toolbar.ts:160-163`). Current normal mark selection sets the tool to Select (`CapturePage.tsx:1072-1077`), where the correct groups appear. Correct the example or state the intended reachable case; do not silently broaden this MEU into the armed-selection flow assigned to MEU-143.

## Q7 — Gate removal, Select and hash pins

Accepted removal of the candidate/baseline/dirty checks, Apply/Cancel buttons and viewport gate props; Save and tool changes no longer depend on valid hex text. AC-105.9 and the moved AC-60.8 pins cover the negative case. The pin table moves AC-60.12/.13, MEU65_OPTION_IDS and AC-81.4 consistently.

The scoped `optionGroups('select', null, mode) → []` change is represented in AC-65.1 and AC-105.19; the inspected crop and AC-103.17 pins are compatible. Leaving unused Apply/Cancel constants inside the hashed prefix and appending after MEU-102 preserves the byte guard. Independently computed prefix SHA-256: `6E569F820459EA2BE3264324635C0A9D22FC4AACFA2DAD6A6B54F840870FF454`.

## Q8 — BLOCK_SCRUB

Accepted the optional `min` defaulting to `SCRUB_MIN`, use of the existing scrub math/gesture machinery, preserved input id, added handle id, and block variant of `SizeBurst`. This is sufficient to reuse preview/commit/cancel behavior while limiting block size to 2..100. AC-105.18 observes the selected-mark undo step, bounds, Escape and unselected-tool PUT; .28 keeps Stroke, Size and undo/redo guards. No existing scrub default needs to change.

## Q9 — Type-only names, Reds and filters

Row 1 now provides the store module and both exports with today's plain GET/no-op reset; its style hook still returns defaults and a no-op save (`implementation-plan.md:405-411`; `task.md:53,86`). Row 3 includes AC-105.32 in the behaviour file and its required Red set. Assertion-first rules make the absent initial PUT an assertion failure before any wait (`task.md:52-59,89`).

The two added .32 schedules test the stale-GET filter, beyond the already accepted write-order case. A real queue with a plain GET still loses the optimistic value; the independent model's unfiltered mutation failed its visible-value assertion before and after PUT settlement. Installed future UI code was not executed. `red-check.py` declares the new module and export names (`:65-69`), and its fresh selftest reports 58 fixtures, 0 wrong. H1-6a now counts all 32 ACs (`task.md:101`).

## Q10 — Help, actions index and split records

Accepted the help update, including the Block size sentence, and moved help pins/AC-105.24. The new actions-index rows describe the real selected-mark versus preference-write paths; row 5 retains the existing table shape and runs the actions audit. The split keeps the five spec rows intact, adds MEU-143 with dependencies MEU-87/99/100/105 and matrix row 9.31a, adds MEU-143 to MEU-106, and keeps MEU-107 on MEU-105 only. Row 6 requires copies, scoped diffs, structural checks and `render --check`. P2 in status and P3 in grouping are deliberately preserved.

**Nonblocking wording correction:** SPLIT_GROUPING's blanket statement that the Ctrl+D and Ctrl+C bullets are now MEU-143's (plan line 186/task line 93) should preserve their actual owners. Ctrl+D remains MEU-106's, as D-724 expressly says; Ctrl+C remains MEU-104's delivered D-678 behavior. Reassign the letters/modifier work and retain those bullets as cross-session constraints. The explicit MEU dependency/scope statements already establish the intended ownership, so this is a correctable wording inconsistency, not a missing deliverable.

## Q11 — Endings, identity, scope and safety

The F3 delta is present in every affected inventory: Files Modified (`implementation-plan.md:324-325`), session-gate allowed paths (`session-gate.ps1:58-59`), identity selftest inputs (`identity.py:160-161`), baseline absent names/new files/targets (`baseline.ps1:167,174,236,259`), Red declared names (`red-check.py:67-69`) and row 1's stubs (`task.md:53,86`). The existing hook stays a row-4 CRLF edit; current bytes have 109 CRLF endings, zero lone LF and zero lone CR. The task's per-file byte-preservation rule still applies (`task.md:77`).

The read-only inventory passed all 17 delta checks. The fresh identity selftest detects mutations to both added paths and ends with 0 failures. No scope/identity exclusion was added for these production inputs. The public git status contained only the untracked plan files and the disclosed ignored private-path discrepancy. No repository write, full-tree identity read, product gate, live service, user-data read, network request or clipboard write was performed.

## Checklist Results

These are round-3 observations by `codex-independent-reviewer`. A pass evaluates the plan and its correction delta. Earlier product areas accepted in rounds 1/2 are carried forward, not freshly certified.

| Check | Result | Procedure | Exit | Evidence |
|---|---|---|---|---|
| PR-1 Plan/task alignment | pass | Compare STYLE_STORE, .1/.23/.32 and row 1/3/4/H1-6a | null | Shared query function, stubs, Red and 32-AC coverage agree |
| PR-2 Not started | pass | Read task statuses and public git status paths | null | Product rows remain unchecked; new production store absent |
| PR-3 Task contract | pass | Inspect corrected task rows | null | Existing owners, order and deliverables retained |
| PR-4 Validation realism | pass | Trace .32 assertions against stubs/plain GET and read .23 | null | Initial absent PUT fails by assertion; stale-response mutation fails displayed-value oracle |
| PR-5 Source-backed choices | pass | Reconcile D-720 with retained style and card contracts | null | Shared filter protects all reads without canceling card refetches |
| PR-6 Corrections readiness | pass | Reconcile requested corrections with current files | null | F3 and both notes identifiable and fixed; no reviewer correction to repository |
| PR-7 Scope discipline | pass | Compare correction delta with accepted split | null | No retained rule moved or removed; MEU-143 unchanged |
| PR-8 Reachability/atomicity | pass | Walk requested races through counter/latest/filter/queue | null | Pending and post-start successes survive GET; failure reconciles via drain-time GET |
| PR-9 Named contracts | pass | Read governing STYLE_STORE and its consumers | null | ACs/tasks cite one governing contract |
| Existing caller regression | pass | Inspect card projection/save, source pins and fake GET callers | null | Seven-key form/save retained; no caller requires former inline query function |
| Product implementation/Red-Green/full gate | n/a | Prohibited at this plan review | null | No product runtime result claimed |

### Independently executed evidence

Round-3 fresh evidence and decisive output are embedded in Recheck (Round 3). The original round-2 probes below are retained as history:

Fresh command: `rtk proxy .venv/Scripts/python.exe C:/Temp/av-kit/s71/review/r2-probes.py`, cwd `P:/av-kit`, with `PYTHONDONTWRITEBYTECODE=1`. Exit **0**. Decisive output:

```text
numeric: +/-10**400 -> ValidationError("arrow_stroke is out of range"); bool refused; 616 legacy outcomes/messages identical
HTTP mapping: actual DOMAIN_HTTP_MAP[ValidationError] = 422; AC-105.4 new 400 expectation must be corrected to 422; no HTTP request performed
ordering: 60 two-to-five-commit success/failure schedules retain last successful commit; failures do not poison the chain
read race: A fails -> queue empty -> GET snapshots initial -> commit B -> old GET replaces B -> B succeeds; stored=B, cache/fields=initial, no further invalidation
read-race counterexample confirmed against specified queue algorithm; no production hook exists yet
static: 32 ACs, 21 distinct required Reds including .32; H1-6a stale len(every)!=31 false-fails complete coverage (clerical)
test-ids prefix SHA256: 6E569F820459EA2BE3264324635C0A9D22FC4AACFA2DAD6A6B54F840870FF454
red-check: .32 assertion accepted; .3 cannot match .32; missing-name .32 refused
```

```json
{"schema_version":"evidence.v1","check_id":"s71-r2-contract-probes","command":"rtk proxy .venv/Scripts/python.exe C:/Temp/av-kit/s71/review/r2-probes.py","cwd":"P:/av-kit","scope":"in-memory integer-first encoder/DTO, legacy outcomes, synthetic queued writes/refetch, AC inventory and Red receipts","phase":"targeted","exit_code":0,"result":"pass","tested_state":"main@5e9ea7c; round-2 unstarted working-tree plan; contract simulations, not future production hook","output":"60 write schedules ordered; separate stale-GET schedule leaves stored=B/cache=initial; both huge integer signs refused key-only; 616 noninteger outcomes unchanged; actual domain HTTP status 422; 32 ACs/21 required Reds; .32 assertion accepted/missing-name refused; hash unchanged","fresh":true}
```

The synthetic queue model demonstrates an execution admitted by the written algorithm. It is not an execution of a future hook. Source inspection substantiates its cache step: `setQueryData` reaches manual `setData` with no cancellation (`queryClient.ts:308-317`), whereas the already-running fetch later calls `this.setData(data)` (`query.ts:869-880`). STYLE_DISPLAY and STYLE_DRAW are explicitly tied to that cache-derived style (`implementation-plan.md:170,172`).

Public `git status --short --untracked-files=normal` exited 0 and listed only `?? .claude/settings.local.json` and `?? docs/execution/plans/2026-11-13-capture-style-tool-flow/`. The former is the disclosed sandbox-only ignore discrepancy and was not opened. No repository file was written.

### Round-1 evidence retained

The prior report remains the source for its 58-case Red selftest, identity selftest, four-case id-length selftest and original failure probes. Those results are historical round-1 observations, not fresh round-2 product verification. Their accepted scope conclusions remain; F1/F2 counterexamples are superseded by the fixes above.

All Python commands used `PYTHONDONTWRITEBYTECODE=1`. Selftests set TMP/TEMP under `C:/Temp/av-kit/s71/review`. Output streams were redirected, the native child exit was saved immediately, and the completed receipt read. The order probe is a deterministic simulation of the proposed algorithm, not a claim to execute future UI code. Exit 0 below means the counterexample assertions held.

```json
{"schema_version":"evidence.v1","check_id":"s71-style-store-order","command":"rtk proxy .venv/Scripts/python.exe C:/Temp/av-kit/s71/review/store-order-probe.py","cwd":"P:/av-kit","scope":"synthetic STYLE_STORE commit/transport schedule; no network or database","phase":"targeted","exit_code":0,"result":"pass","tested_state":"main@5e9ea7c; unstarted working-tree plan; contract simulation only","output":"one partial PUT per commit: True; optimistic cache retains latest commit: True; next GET retains latest commit: False; cache and next GET disagree: True; counterexample confirmed: an older successful write can replace the last preference","fresh":true}
```

```json
{"schema_version":"evidence.v1","check_id":"s71-style-numeric-boundary","command":"rtk proxy .venv/Scripts/python.exe C:/Temp/av-kit/s71/review/numeric-probe.py","cwd":"P:/av-kit","scope":"in-memory SettingsPutIn variant with proposed StrictInt leaf and current _encode; no store opened","phase":"targeted","exit_code":0,"result":"pass","tested_state":"main@5e9ea7c; current encoder and proposed DTO leaf","output":"ordinary strict-integer refusals: 4/4; 401-digit integer accepted by DTO and planned integer predicate: True; cookie-length guard permits: True; encoder exception: OverflowError; domain validation refusal: False; counterexample confirmed: conversion fails before bounded-integer validation","fresh":true}
```

```json
{"schema_version":"evidence.v1","check_id":"s71-plan-inventory","command":"rtk proxy .venv/Scripts/python.exe C:/Temp/av-kit/s71/review/inventory.py","cwd":"P:/av-kit","scope":"public planned paths, gate allowlist, endings, Red requirements, tools and test-id prefix","phase":"targeted","exit_code":0,"result":"pass","tested_state":"main@5e9ea7c; unstarted working-tree plan","output":"25 existing Files Modified paths; 6 scheduled absent files; Files Modified outside gate allowed set: []; stated existing ending mismatches: []; 20 distinct required Reds; 6 referenced root tools, none missing; test-ids prefix SHA256 6E569F820459EA2BE3264324635C0A9D22FC4AACFA2DAD6A6B54F840870FF454; branch main","fresh":true}
```

```json
{"schema_version":"evidence.v1","check_id":"s71-red-selftest","command":"rtk proxy .venv/Scripts/python.exe docs/execution/plans/2026-11-13-capture-style-tool-flow/red-check.py --selftest","cwd":"P:/av-kit","scope":"synthetic runner receipts","phase":"targeted","exit_code":0,"result":"pass","tested_state":"current working-tree plan-local script at main@5e9ea7c","output":"red-check selftest: 58 fixture(s) (18 positive, 40 negative), 0 wrong: []","fresh":true}
```

```json
{"schema_version":"evidence.v1","check_id":"s71-identity-selftest","command":"rtk proxy .venv/Scripts/python.exe docs/execution/plans/2026-11-13-capture-style-tool-flow/identity.py --selftest","cwd":"P:/av-kit","scope":"synthetic scratch git repository only","phase":"targeted","exit_code":0,"result":"pass","tested_state":"current working-tree plan-local script at main@5e9ea7c","output":"Bound mutations changed identity and refused historical evidence; project-artifact exclusions retained identity; identity selftest: 0 failure(s).","fresh":true}
```

```json
{"schema_version":"evidence.v1","check_id":"s71-id-length-selftest","command":"rtk proxy .venv/Scripts/python.exe docs/execution/plans/2026-11-13-capture-style-tool-flow/id-length.py --selftest","cwd":"P:/av-kit","scope":"four synthetic title lengths; no pytest collection","phase":"targeted","exit_code":0,"result":"pass","tested_state":"current working-tree plan-local script at main@5e9ea7c","output":"71-character titles accepted; 72-character titles refused; id-length selftest: 4 case(s), 0 wrong.","fresh":true}
```

## Verdict

`approved` — F1, F2 and F3 are fixed as plan contracts. Round 2's HTTP-status and AC-count notes are fixed. No new material regression was found. `intent_achieved: yes` applies to plan sufficiency; implementation and execution evidence remain future work.

The report is saved only to `C:/Temp/av-kit/s71-plan-review-round-3.md`. The coordinator validates/copies the complete rolling report and records the verdict. Plan approval does not authorize execution; Mat has not ruled on D-727.

## Recheck (Round 2)

Historical round-2 reasoning follows. Its F3 status is updated to fixed by round 3 below.

### Prior Pass Summary

| Finding | Prior Status | Recheck Result |
|---|---|---|
| F1 | open | fixed |
| F2 | open | fixed |

### R1 — Queue ordering, recovery and lifetime

**Original F1 is fixed.** STYLE_STORE (`implementation-plan.md:169`) now gives every caller one module-scope settling promise chain. By induction, write n cannot start before write n−1 settles, including a rejection; later successful writes therefore cannot be replaced by an older queued PUT. The 60 synthetic schedules cover two through five commits and every success/failure mask. If the last commit fails, the queue deliberately does not retry it: the server retains the latest successful value and recovery should display that value. "Last commit stored" is necessarily conditional on that commit succeeding.

**AC-105.32 is a meaningful intended Red/Green oracle**, subject to row 3's assertion-first discipline. Assert the first recorded PUT exists before waiting for it. The stub/current page has no immediate preference PUT, so that assertion fails without a timeout. Then hold the first request and assert the second has not arrived; release the first and check both bodies, final storage and remount. The 500-first/second-held branch also proves no premature GET for that batch. Today's tests were not executed; this is plan-level reasoning plus a synthetic matcher probe.

**The single failure invalidate is not safe for all subsequent commits: F3.** Queue emptiness is a point-in-time fact. Once recovery has started a GET, the user can commit again. The query result can then install its pre-commit snapshot while the new write is pending, and the later successful PUT does nothing to repair it. The server can hold the new colour while fields and the next mark use the old colour. AC-105.32 currently tests two commits inside one undrained batch, not this post-drain schedule. A recovery fix must also retain the need to reconcile failed leaves if an obsolete read is canceled; otherwise a failed different leaf could remain optimistic forever.

**Lifetime:** module scope prevents independent queues across remounts. Vitest's file isolation is on and not overridden, so files do not share that module instance. Tests within one file do share it: they must settle all held deferred promises before teardown; clearing the QueryClient does not settle a module-level promise chain. No actual leak has been observed because the new hook/test file are not implemented. This consideration is not an additional finding.

### R2 — Integer-first validation

**Original F2 is fixed.** The prescribed bounds comparisons operate directly on Python integers before any float conversion, so both `10**400` and `-10**400` are refused with exactly the key-only out-of-range message. The existing bool predicate stays ahead of numeric processing. The probe inserted only that opt-in branch into the current encoder in memory; all 616 sampled existing-row outcomes and messages remained identical when `integer=False`.

AC-105.3 now requires the decisive positive-huge-integer `ValidationError` instead of `OverflowError`. AC-105.4 does explicitly require 400, not 500, but **400 is the wrong expected validation status for this unchanged API**: `DOMAIN_HTTP_MAP[ValidationError]` is 422 (`packages/api/src/avkit_api/errors.py:29`), and the route does not translate it. Correct the numeric expectation/boundary prose to 422. This does not reopen the previous feature decisions or warrant changing the global handler. It is nonblocking; the overflow behavior itself is resolved.

### R3 — Effects of the fixes

The new behavior failure is F3. No other material regression was found in the changed paths:

- Row 3 includes .32 as a required Red in the correct behavior file; required Red count is now 21. Guards .1/.27/.28/.30 remain separate. The generic Red matcher accepts .32 assertion failures and refuses missing-name failures or a .3/.32 prefix substitution.
- The plan AC table is exactly .1 through .32. Updated range statements, row 5's Delivered-note check and H1-7 all include .32. **Clerical correction:** H1-6a (`task.md:101`) still uses `len(every)!=31`; with complete 32-row coverage it exits 1. Change that literal to 32 (or compare the derived sets without a stale fixed count). This false-fails; it does not hide a missing deliverable and does not block the verdict.
- The test-id prefix hash is unchanged at `6E569F820459EA2BE3264324635C0A9D22FC4AACFA2DAD6A6B54F840870FF454`; neither fix changes the additive-ID placement or the retained Apply/Cancel constants.
- The Capture card keeps its seven-field projection and unsaved draft. AC-105.23 remains a meaningful caller guard. The queue change does not alter its form or Save body; F3 concerns acceptance of stale data into their shared cache.

### New Findings

| Finding | Severity | Blocking | Contract | Concrete failure | Status |
|---|---|---|---|---|---|
| F3 | High | yes | AC-105; STYLE_STORE / STYLE_DISPLAY / STYLE_DRAW | A drain-time failure GET replaces a new commit; its later successful PUT leaves the old cached style in use (`implementation-plan.md:169,170,172,294`). | fixed |

**At the end of round 2, open blocking findings: 1 (F3); fixed in round 3 below.** No Critical findings. No other new severity-rated finding. Corrections belong to the coordinator; the reviewer edited no repository file.

**Report validation:** `rtk proxy .venv/Scripts/python.exe tools/validate_closeout_artifacts.py --review C:/Temp/av-kit/s71-plan-review-round-2.md --review-state-only --expected-review-mode plan --expected-target-plan docs/execution/plans/2026-11-13-capture-style-tool-flow/implementation-plan.md --max-review-rounds 3 --output C:/Temp/av-kit/s71/review/r2-report-state.json` exited 0. The parser recognized plan mode, this target, round 2 of 3 and `changes_required`. It counts two open table occurrences because the requested rolling Findings table and New Findings table both describe F3; there is one distinct open blocking id. The structured verdict's JSON Schema validation also completed with 0 errors (exit 0). These are artifact checks, not product verification.

🕐 Completed: 2026-11-13 23:39 (EST)


## Recheck (Round 3)

### Prior Pass Summary

| Finding | Prior Status | Recheck Result |
|---|---|---|
| F1 | fixed | fixed |
| F2 | fixed | fixed |
| F3 | open | fixed |

### R1 — F3, read schedules and the card

**F3 is fixed** in STYLE_STORE (`implementation-plan.md:169`; D-720 `:614-628`). Interpret “had not succeeded by then” against the counter captured at GET start: overlay a current leaf if it is pending or its success counter is greater than that start counter. At response time inspect the current `latest` entry, not an entry snapshotted at GET start. Success/failure updates apply only if the entry still belongs to that commit. These are the two timestamps and ownership check the written contract supplies.

| Requested schedule | Counter/latest reasoning and final result |
|---|---|
| Round-2 F3: first PUT fails, recovery GET held, second commit, old GET replies, second PUT succeeds | First failure deletes its own entry. The second commit creates a pending entry before the old GET resolves, so the response is overlaid with the second colour. Success records its counter; fields and STYLE_DRAW retain that colour, and a later GET returns it from storage. |
| Window-refocus refetch while PUT pending | Pending entries are overlaid even when committed before GET start. A commit counter alone would miss this; the separate succeeded state covers it. |
| GET starts before PUT settles, answers after success | The success counter exceeds GET's start counter, so the successful value is still overlaid. A GET started after success accepts the stored value instead. |
| Settings card saves/refetches while style PUT pending | The same query function overlays only style leaves; the card's seven nonstyle keys pass through. Its partial PUT has no style keys. The pending style survives the refetch, and both sets of values survive settlement. |
| Failed older commit followed by a newer commit to the same leaf | The older failure cannot delete the newer entry. The newer pending value survives an old read; success persists it. If the newer commit fails too, its own entry is deleted and the drain-time GET restores the last successful stored value. |
| Failed older commit followed by a commit to another leaf | Failure deletes only its own leaf. Recovery reads that leaf from storage while overlaying the other pending/newly succeeded leaf. A later failure of that other leaf is reconciled by its own drain-time invalidation. |

The shared settling PUT chain accepted for F1 is retained. The failure flag still requests one invalidation after the current queue drains, and the new filter protects a commit made after that GET began. Failed optimistic values can remain visible until recovery responds, as the contract says; after requests settle and recovery completes, the cache agrees with the last successful stored values. No perpetual overlay of failed entries is prescribed.

**AC-105.32 is a meaningful Red/Green contract** (`implementation-plan.md:294,405-429`; `task.md:52-59,86,89`). With the row-1 stub/current page there is no immediate preference PUT: assert the recording fake has received the first PUT before waiting on it, so Red is an assertion rather than a timeout. With write queue/commits implemented but a plain GET retained, the held stale response replaces the colour and fails the fields/next-arrow assertions. Both added schedules therefore distinguish a functioning read filter from the old/plain GET. Tests also settle held requests and reset module state. The scratch model independently exercised response-before-success and response-after-success; both pass with filtering and fail by assertion without it. No future Vitest test was run or claimed to pass here.

**AC-105.23 remains sound** (`implementation-plan.md:285`). `CaptureForm`/`asForm` remain a seven-key projection (`useCaptureSettings.ts:15-23,39-55`); `form = draft ?? baseline` keeps an unsaved edit (`:76-84`); Save serializes `parseSettingsPut('capture', form)` (`:88-95`). `capturePutSchema` remains the strict seven-key schema (`settings-schemas.ts:80-90`). The new query function is a zero-argument replacement for the same GET and does not parse the response with that seven-key schema. Extra style data can stay in cache for the style reader without entering the card's form or Save body.

### R2 — Two round-2 notes

Both are fixed. The API boundary row and AC-105.4 now say 422 (`implementation-plan.md:245,266`), matching `errors.py:29`. H1-6a now requires `len(every)!=32` (`task.md:101`), and the plan contains exactly AC-105.1 through AC-105.32. These corrections require no product-handler change.

### R3 — New-file/query-function integration and callers

The inventory checks all required locations: Files Modified (`implementation-plan.md:324-325`), allowed set (`session-gate.ps1:58-59`), identity (`identity.py:160-161`), baseline absent names/new-file sets/target anchors (`baseline.ps1:167,174,236,259`), Red declared names (`red-check.py:67-69`), signatures (`implementation-plan.md:263`) and row-1 stub plus stub note (`task.md:53,86`). All 17 delta checks pass. Existing `useCaptureSettings.ts` bytes are pure CRLF (109 lines), and both plan/table and task preservation instructions retain that ending.

The caller inspection found no concrete regression from changing only the query function. `SettingsPage.tsx:356` still calls the same hook. `capture-page.test.ts:222,369-379,620-623` pins parsing, endpoint and form leaves; these stay in the hook's Save/projection code. The card tests' fake GET returns still work, including fixtures with missing optional/defaultable fields (`settings-path-fields.test.tsx:53-69`). Existing PUT-count tests exercise card edits with no style commit (`capture-page.behavior.test.ts:373-389,1197-1226`; `capture-inbox.test.ts:691-697`); replacing a GET function emits no new PUT. No test update is needed just for those callers. The actual product suites remain reserved for execution.

### New Findings

None. No Critical or High findings remain open; F1, F2 and F3 are fixed. No new clerical finding is raised. Prior Q6/Q10 wording observations remain historical and do not reopen accepted scope.

| Finding | Severity | Blocking | Contract | Concrete failure | Status |
|---|---|---|---|---|---|

### Fresh round-3 evidence

The schedule model is an independent transcription of the specified algorithm, not the future React hook. It makes no API, database, network or clipboard call. Its conclusions are bounded to plan semantics. The inventory is a source/byte check. Script selftests operate on synthetic fixtures and a synthetic temporary repository only.

```json
{"schema_version": "evidence.v1", "check_id": "s71-r3-schedules", "command": "rtk proxy .venv/Scripts/python.exe C:/Temp/av-kit/s71/review/r3-schedules.py", "cwd": "P:/av-kit", "scope": "in-memory STYLE_STORE schedules and card projection", "phase": "targeted", "exit_code": 0, "result": "pass", "tested_state": "main@5e9ea7c; unstarted round-3 plan sha256=b0d3adb5cf53dac5e97fa9cc46aa89a599713f85ca8f50636f66e62f8aa0cfd0", "output": "STYLE_STORE model: 16 schedules pass; two plain-GET mutations fail by assertion", "fresh": true}
```

```json
{"schema_version": "evidence.v1", "check_id": "s71-r3-inventory", "command": "rtk proxy .venv/Scripts/python.exe C:/Temp/av-kit/s71/review/r3-inventory.py", "cwd": "P:/av-kit", "scope": "round-3 file lists, stubs, API notes, AC count and hook bytes", "phase": "targeted", "exit_code": 0, "result": "pass", "tested_state": "main@5e9ea7c; unstarted round-3 plan sha256=b0d3adb5cf53dac5e97fa9cc46aa89a599713f85ca8f50636f66e62f8aa0cfd0", "output": "inventory: all 17 delta checks pass; 32 ACs; useCaptureSettings.ts CRLF=109, lone-LF=0, lone-CR=0", "fresh": true}
```

```json
{"schema_version": "evidence.v1", "check_id": "s71-r3-red-selftest", "command": "rtk proxy .venv/Scripts/python.exe docs/execution/plans/2026-11-13-capture-style-tool-flow/red-check.py --selftest", "cwd": "P:/av-kit", "scope": "synthetic Red runner receipts", "phase": "targeted", "exit_code": 0, "result": "pass", "tested_state": "main@5e9ea7c; unstarted round-3 plan sha256=b0d3adb5cf53dac5e97fa9cc46aa89a599713f85ca8f50636f66e62f8aa0cfd0", "output": "red-check selftest: 58 fixture(s) (18 positive, 40 negative), 0 wrong: []", "fresh": true}
```

```json
{"schema_version": "evidence.v1", "check_id": "s71-r3-identity-selftest", "command": "rtk proxy .venv/Scripts/python.exe docs/execution/plans/2026-11-13-capture-style-tool-flow/identity.py --selftest", "cwd": "P:/av-kit", "scope": "synthetic scratch git repository under review temp directory", "phase": "targeted", "exit_code": 0, "result": "pass", "tested_state": "main@5e9ea7c; unstarted round-3 plan sha256=b0d3adb5cf53dac5e97fa9cc46aa89a599713f85ca8f50636f66e62f8aa0cfd0", "output": "capture-style-store.ts and useCaptureSettings.ts mutations: state_changed=True historical_refused=True; identity selftest: 0 failure(s)", "fresh": true}
```

```json
{"schema_version": "evidence.v1", "check_id": "s71-r3-idlen-selftest", "command": "rtk proxy .venv/Scripts/python.exe docs/execution/plans/2026-11-13-capture-style-tool-flow/id-length.py --selftest", "cwd": "P:/av-kit", "scope": "four synthetic pytest-title widths, no product collection", "phase": "targeted", "exit_code": 0, "result": "pass", "tested_state": "main@5e9ea7c; unstarted round-3 plan sha256=b0d3adb5cf53dac5e97fa9cc46aa89a599713f85ca8f50636f66e62f8aa0cfd0", "output": "id-length selftest: 4 case(s), 0 wrong", "fresh": true}
```

### Verdict

`approved` — the written plan achieves its registered intent, F3 and both numeric notes are fixed, and the corrections introduce no demonstrated material failure. No execution authorization is inferred. The coordinator saves this complete report to the canonical rolling path; Mat's D-727 ruling remains next.
