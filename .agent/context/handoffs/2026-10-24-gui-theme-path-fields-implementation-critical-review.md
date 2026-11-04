---
date: "2026-10-26"
review_mode: "execution"
target_plan: "docs/execution/plans/2026-10-24-gui-theme-path-fields/implementation-plan.md"
loop_id: "s40-execution-2026-10-24-gui-theme-path-fields"
round: 2
verdict: "approved"
findings_count: 1
blocking_findings_count: 0
template_version: "2.2"
requested_verbosity: "standard"
agent: "codex-independent-reviewer"
intent_achieved: "yes"
---

# Critical Review: gui-theme-path-fields

> **Review Mode:** execution, round 1  
> **Verdict:** changes_required  
> **Intent achieved:** partial

## Intent Anchor

Confirm Session 40's delivered code makes Settings, TTS and Convert selects follow the theme live and on cold boot, and gives Convert, TTS and Settings one Browse path field, with honest Red/Green and gate evidence.

The live-theme and path-field changes work in the reviewed normal/error cases. One new startup failure can indefinitely withhold all routes.

## Scope

**Target:** Session 40's uncommitted change set in `P:/av-kit` over root commit `7b29fcd`. Reviewed both correlated MEU-94/MEU-93 handoffs, implementation-plan.md, task.md, walkthrough.md, production/test diffs and new files, the two residual source-spec sections, related routing/API code, and recorded Red/Green/gate evidence.

**Review Type:** independent execution review, applying IR-1–IR-7, AV-1–AV-6 and relevant DR checks. Claude/Anthropic authored the implementation; this Codex/OpenAI reviewer did not. REVIEW-TEMPLATE v2.2 supplied the structure; the Session 35 and Session 31b reviews supplied layout calibration only.

**Verification boundary:** only permitted targeted Vitest, typecheck, handoff/task validators and read-only inspection. No full suite, session gate, Electron, build, dependency sync or generator was run. D-120, D-118, D-119 and the history squash are accepted. H2 artifacts/status changes remain subsequent implementer work. Only this report and scratch receipts were written by the reviewer.

## Findings

| # | Severity | Blocking | Kind | Finding | File:Line | Recommendation | Status |
|---|----------|----------|------|---------|-----------|----------------|--------|
| F1 | High | yes | behavior | A pending boot-theme request has no deadline, so the new gate can permanently withhold every route. The 60-second retry check executes only after rejection. | `ui/src/renderer/src/lib/theme.ts:111`, `:125`; `ui/src/renderer/src/lib/api.ts:72`, `:77`; `ui/src/renderer/src/components/layout/AppShell.tsx:295` | Bound the complete boot operation, release the gate on expiry, and cancel/ignore late answers; test a permanently pending request and cleanup. | open |

**F1:** confidence High; subject deliverable; finding_kind behavior; ledger `violates: AC-94` (THEME_GATE/BOOT_RETRY, related leaves AC-94.6 and AC-94.11). This is a concrete runtime failure under the user's explicit no-stuck-gate review requirement. The existing leaf tests pass their stated status-error and held-then-released cases; no claim is made that they already test an unresolved HTTP request.

### F1: concrete control-flow trace

1. Backend URL/token discovery succeeds. Its 10-second timeout has finished and been cleared (`lib/api.ts:42`, `:53`).
2. `GET /settings/ui` connects but never returns, or headers arrive and `response.text()` remains pending (`lib/api.ts:72`, `:77`). Neither wait has a request/body deadline.
3. `useSyncDocumentTheme` has initialized `settled=false`. Both paths that release it depend on that promise fulfilling or rejecting (`lib/theme.ts:103`, `:117`, `:119`).
4. `BOOT_RETRY_WINDOW_MS` is only examined in the rejection continuation. It is a retry scheduling limit, not a deadline for a pending attempt (`lib/theme.ts:125`).
5. Even after arbitrarily more than 60 seconds, `AppShell` substitutes `RouteThemePending` for every route (`AppShell.tsx:295`). Its 3-second timer only changes the text to “Still loading…” (`AppShell.tsx:35`); navigation cannot mount a recovery/settings route.

This is established by source inspection, not an Electron reproduction. The API's unbounded HTTP wait predates this session, but withholding every route until it completes is new. The existing deferred-request test (`theme-selects.test.tsx:491`) explicitly resolves its promise; the retry tests reject immediately. Consequently their green results do not exclude this state.

Keep the established cold-boot semantics while the boot operation is within its bound. On expiry, use the same current-document fallback already used by terminal failures, log once, and prevent late/unmounted answers from changing state. This finding does not revoke D-120 or request a full-gate rerun.

## Checklist Results

### Commands independently executed

All command receipts preserve native exits. Cwd is `P:/av-kit`, except UI commands use `P:/av-kit/ui`. Validator retries used process-local `RECEIPTS_DIR=C:/Temp/av-kit`, `UV_CACHE_DIR=C:/Temp/av-kit/uv-review-cache`, `UV_NO_SYNC=1`, and `PYTHONDONTWRITEBYTECODE=1`. Initial validator attempts exited 2 because the default uv cache was denied; retries below actually ran the validators.

| Check | Result | Exit | Decisive output |
|-------|--------|------|-----------------|
| Nine permitted targeted Vitest files | pass | 0 | Test Files 9 passed (9); Tests 165 passed (165); duration 15.99 s. Existing Convert reorder tests emitted React act warnings. |
| `npm run typecheck` | pass | 0 | `tsc --noEmit`, no diagnostics. |
| MEU-94 handoff validator with plan | pass | 0 | Required sections; 16 AC rows; 2 decisions; durable evidence; bound plan; all 14 plan AC families. |
| MEU-93 handoff validator with plan | pass | 0 | Required sections; 19 AC rows; 2 decisions; durable evidence; bound plan; all 14 plan AC families. |
| Task contract linter with the three allowed classes | pass | 0 | 24 rows; 22 command rows checked; 2 view_file exemptions; dependency graph acyclic. |

Exact commands and manual observations appear in the structured verdict below. Scratch receipts include `s40-review-vitest.txt`, `s40-review-typecheck.txt`, and `s40-review-{h94,h93,task}-validation-retry.txt`; the decisive results above are embedded here rather than relying solely on those paths.

### Information Retrieval / Implementation Review

| Check | Result | Observed evidence |
|-------|--------|-------------------|
| IR-1 runtime evidence | pass within authorized boundary | Recorded Electron Red/Green and gate evidence inspected; reviewer independently ran targeted jsdom/runtime assertions, not Electron. |
| IR-2 collaborator/seam compliance | pass | Theme probe answers GET, updates its answer on theme PUT, and passes unrelated requests to the original seam. Path tests observe actual request bodies/counts. |
| IR-3 error mappings | n/a | No REST route/schema implementation changed. Existing API error mapping inspected for the gate trace. |
| IR-4 generalization | pass | One `classList.contains('dark')` read (`lib/theme.ts:83`) and one G30 pair definition (`SelectInput.tsx:16`). Console, Capture Named, Settings raw selects and SelectInput consumers use the shared reactive hook. |
| IR-5 assertion strength | partial | Behavioural checks are strong; source checks are adequate. Missing permanently pending request coverage permits F1. See audit below. |
| IR-6 boundaries | pass | No new REST/IPC boundary; Convert retains Save-only PUT, TTS uses its existing PUT helper, dialog cancellation is explicitly handled. |
| IR-7 AC/deferral integrity | pass | Both delivered MEUs and leaf ACs mapped across handoffs; no hidden product deferral found. Waived gate rows and pending H2 are accepted as instructed. |

### Test rigor audit

| File / changed tests | Rating | Reason |
|----------------------|--------|--------|
| `theme-selects.test.tsx`: AC-94.1, .2, .4 and storage cases in .5 | Strong | Mounted hooks/DOM nodes, every option's pair, caller width, listener removal, storage denial and event delivery are asserted. |
| Same file: AC-94.3 and boot source case in .5 | Adequate | Source constraints supplement runtime assertions; they do not independently prove Chromium first paint. |
| Same file: AC-94.6(a)–(e), .11 | Adequate | Timing, counts, logs, state, child first-render theme and 599 handling are asserted. Every pending request is ultimately resolved/rejected; F1 is uncovered. |
| `settings-path-fields.test.tsx` | Strong runtime / adequate source | Real Settings render, placeholder, label/row containment, Browse and cancel; EC-2 checker includes positive and negative fixtures. Actual four helper references were also inspected. |
| `layout-primitives.test.ts`: AC-93.1 | Strong | Disabled click cannot call handler; omitted/false props preserve enabled behaviour. |
| `convert-page.behavior.test.ts`: AC-93.2 and adjacent regression tests | Strong | Labelled field, same-row Browse, dirty state, no early PUT, one Save PUT, cancel no-op and typed-edit regression. |
| `tts-page.behavior.test.ts`: AC-93.3 and adjacent regressions | Strong | Read-only typing, unchanged cancel value, zero/one PUT, run-bar containment and busy disabled/enabled transition. |
| `gui-actions-audit.test.ts`: AC-93.5/.6 | Adequate | Index row uniqueness/order, actual IPC registration/preload and ID registry are checked. |
| `console-polish.test.ts`, `chrome-zorivest.test.ts`, `tts-page.test.ts`: amendments | Adequate | D-118 keeps the component/named-import ban; TA-1/TA-2 move ownership to the shared hook rather than require removed code. |
| `settings.test.ts`: AC-94.7/.8(a)–(d) | Strong | Literal computed-colour oracle, live toggle, held/released request counts, no/stale/agreed mirror, and shared-app-data persistence. |
| `tts-generate.test.ts`: AC-94.9 and existing Browse/run-bar regressions | Strong | Observed inserted/current colours and actual Browse flow; pre-existing AC-64.6 protects geometry. |
| `convert-queue.test.ts`: AC-94.10, AC-93.7 | Strong | Cold-boot hold/release, select colours, real Browse geometry and dialog value. The null-box returns follow throwing non-null assertions and do not suppress failure. |
| `theme-probe.ts` helper | Adequate | Registers before the seam's one reload; request-time lookup avoids init-script ordering dependence. MutationObserver records inserted selects; selected-option computed styles are checked. Unit tests separately check every option. No manufactured colour results. |
| `test-ids.ts` | n/a | Additive registry, exercised by the audit tests. |

**Red/Green:** Saved raw Red excerpts match the stated assertions: missing new exports, stale Settings colours, no gate/mirror, missing PathRow/Browse and index entry. These are not setup/import failures. Some new-export checks fail before deeper assertions at Red; Electron/behavioural evidence separately demonstrates the underlying defects. Documented initially passing regressions are not presented as Red failures.

**EC-4:** `TTSPage.tsx:64`, `:112` and `:166` already use `OUTPUT_DEFAULT='~/Documents'` when the setting is empty. Comparing to the captured initial value at `tts-page.behavior.test.ts:819` preserves “typing/cancel does not change it.” Zero-PUT and exact one-PUT checks remain. This is an accurate expectation repair, not a weakening to accept a changed product output.

### Gate and claim assessment

D-120 stands. No run passed whole. Runs 1, 3 and 4 reached Electron and recorded 170 passes plus one failure each; run 2 stopped at AC-19.17 before Electron. Thus the unit evidence spans all four runs, while Electron AC support comes from the runs that reached Electron and the earlier Green runs.

The F2 registration failure occurs in an external hotkey fixture; AC-19.17's timeout occurs during dynamic module import. The capture hangs have no recorded failing assertion/locator and also passed other runs/isolated probes. AC-67.24 does exercise the changed Settings backup field, which the independent targeted tests support. The evidence does not establish that Session 40 caused those hangs, and this review does not assert F1 caused them. It also does not turn the implementer's host-load explanation into a proved causal diagnosis.

File/behaviour claims match the inspected diff: shared reactive select and option styles; boot module first import; route gating for all root routes; Convert form-only Browse; TTS read-only one-PUT Browse; Settings PathRow backup and directory helper origins. The substantive limit is F1: the retry scheduling window does not bound an in-flight theme request.

AV-1/AV-2/AV-4/AV-5/AV-6 pass for the reviewed change set; AV-3 is partial because the new gate's permanently pending request path has no assertion. No unrelated formatting or process-paperwork blocker is raised. No H2 completion is claimed.

## Verdict

`changes_required` — fix F1 through the implementation correction phase and provide a targeted regression. Preserve D-120's no-rerun ruling. No repository correction was made by this reviewer.

## Structured Verdict

```json
{
  "schema_version": "review-verdict.v2",
  "date": "2026-10-26",
  "review_mode": "execution",
  "loop_id": "s40-execution-2026-10-24-gui-theme-path-fields",
  "round": 1,
  "target_plan": "docs/execution/plans/2026-10-24-gui-theme-path-fields/implementation-plan.md",
  "agent": "codex-independent-reviewer",
  "requested_verbosity": "standard",
  "verdict": "changes_required",
  "summary": "Live theme updates and path fields are delivered, but a pending boot-theme request can indefinitely withhold every route. Independent checks passed: 165 tests across nine files, typecheck, both handoff validators and the task linter. D-120's gate waiver is respected.",
  "intent_anchor": "Confirm Session 40's delivered code makes Settings, TTS and Convert selects follow the theme live and on cold boot, and gives Convert, TTS and Settings one Browse path field, with honest Red/Green and gate evidence.",
  "intent_achieved": "partial",
  "findings": [
    {
      "id": "F1",
      "severity": "High",
      "confidence": "High",
      "blocking": true,
      "subject": "deliverable",
      "finding_kind": "behavior",
      "finding": "The new route gate can remain closed indefinitely when GET /settings/ui never settles. BOOT_RETRY_WINDOW_MS is checked only inside catch; no deadline runs while apiFetch is pending. After backend discovery succeeds, either fetch or response.text() can remain pending, leaving settled=false and every route replaced by Still loading…. The API's 10-second timeout covers backend discovery only. This is a source-traced runtime regression introduced by gating all route children; the existing tests release every held request and therefore miss it.",
      "file_line": "ui/src/renderer/src/lib/theme.ts:111; ui/src/renderer/src/lib/theme.ts:125; ui/src/renderer/src/lib/api.ts:72; ui/src/renderer/src/lib/api.ts:77; ui/src/renderer/src/components/layout/AppShell.tsx:295",
      "recommendation": "Bound the entire boot-theme operation independently of promise rejection. On expiry, log once, release the route using the current fallback theme, and cancel or ignore late responses. Add a fake-timer regression for a never-resolving request, including unmount cleanup; retain the existing cold-boot hold/release and status-error assertions.",
      "status": "open",
      "violates": "AC-94"
    }
  ],
  "checklist_results": [
    {
      "check": "Independent targeted UI tests",
      "result": "pass",
      "command": "rtk proxy npx vitest run tests/unit/theme-selects.test.tsx tests/unit/settings-path-fields.test.tsx tests/unit/layout-primitives.test.ts tests/unit/convert-page.behavior.test.ts tests/unit/tts-page.behavior.test.ts tests/unit/gui-actions-audit.test.ts tests/unit/console-polish.test.ts tests/unit/chrome-zorivest.test.ts tests/unit/tts-page.test.ts",
      "exit_code": 0,
      "evidence": "P:/av-kit/ui: 9 files passed; 165 tests passed. React act warnings occurred in existing Convert reorder tests."
    },
    {
      "check": "TypeScript",
      "result": "pass",
      "command": "rtk proxy npm run typecheck",
      "exit_code": 0,
      "evidence": "P:/av-kit/ui: tsc --noEmit completed without diagnostics."
    },
    {
      "check": "MEU-94 handoff",
      "result": "pass",
      "command": "rtk proxy uv run python tools/validate_closeout_artifacts.py --handoff .agent/context/handoffs/2026-10-24-gui-theme-path-fields-MEU-94-handoff.md --plan docs/execution/plans/2026-10-24-gui-theme-path-fields/implementation-plan.md",
      "exit_code": 0,
      "evidence": "16 AC rows; 2 decisions; durable evidence; plan binding and all 14 AC families present. UV_NO_SYNC=1, UV_CACHE_DIR=C:/Temp/av-kit/uv-review-cache, PYTHONDONTWRITEBYTECODE=1; initial attempt exited 2 on denied default uv cache."
    },
    {
      "check": "MEU-93 handoff",
      "result": "pass",
      "command": "rtk proxy uv run python tools/validate_closeout_artifacts.py --handoff .agent/context/handoffs/2026-10-24-gui-theme-path-fields-MEU-93-handoff.md --plan docs/execution/plans/2026-10-24-gui-theme-path-fields/implementation-plan.md",
      "exit_code": 0,
      "evidence": "19 AC rows; 2 decisions; durable evidence; plan binding and all 14 AC families present. Same scratch-cache/read-only uv environment as MEU-94."
    },
    {
      "check": "Task contract",
      "result": "pass",
      "command": "rtk proxy uv run python tools/lint_task_contract.py --task docs/execution/plans/2026-10-24-gui-theme-path-fields/task.md --allowed-builder-classes avkit_builder,avkit_coordinator,avkit_verifier",
      "exit_code": 0,
      "evidence": "24 rows; 22 command rows checked; 2 view_file exemptions; dependencies acyclic. RECEIPTS_DIR=C:/Temp/av-kit; same scratch-cache/read-only uv environment."
    },
    {
      "check": "Theme and path behavior; IR-4/IR-6/IR-7",
      "result": "pass",
      "procedure": "Inspect production diffs, new files, router, all G30 consumers and path handlers; compare plan ACs to tests and both handoffs.",
      "observer": "codex-independent-reviewer",
      "exit_code": null,
      "evidence": "One dark-class read and one G30 pair definition. Shared reactive select/options, boot import order and all-route gate wiring are correct. Convert Browse patches form only; TTS is read-only, disables Browse while busy and sends one PUT; Settings directory dialogs originate from PathRow onBrowse. No API/IPC schema change."
    },
    {
      "check": "IR-5 and Red/Green evidence",
      "result": "partial",
      "procedure": "Audit changed unit/Electron assertions and THEME_PROBE; inspect saved Red/Green receipts and compare EC-4 with TTSPage's default.",
      "observer": "codex-independent-reviewer",
      "exit_code": null,
      "evidence": "Strong behavioral colour/path assertions; adequate source checks. Probe observes colours without substituting style results, and request-time lookup avoids init-script ordering dependency. D-118/D-119 retain their intent. EC-4 correctly asserts unchanged initial value instead of empty string; PUT assertions remain. Missing permanently pending request coverage is F1."
    },
    {
      "check": "Boot gate failure path",
      "result": "fail",
      "procedure": "Trace useSyncDocumentTheme with successful backend discovery followed by a permanently pending fetch or response body; inspect every setSettled and timer site, and AppShell's route conditional.",
      "observer": "codex-independent-reviewer",
      "exit_code": null,
      "evidence": "No independent deadline is installed. Neither then nor catch runs; the retry window is never evaluated; only the placeholder's text timer fires. All routes remain withheld indefinitely. Static control-flow finding; no Electron reproduction was run."
    },
    {
      "check": "D-120 session-gate assessment",
      "result": "pass",
      "procedure": "Inspect walkthrough Session gate/Gate ruling, both handoffs and retained run-3/run-4 receipts; compare failing tests with changed code.",
      "observer": "codex-independent-reviewer",
      "exit_code": null,
      "evidence": "No whole run passed. Runs 1/3/4 record 170 Electron passes and one failure each; run 2 stopped at UI AC-19.17 before Electron. ShareX and load/hang failures do not demonstrate a regression from this diff; AC-67.24 does exercise the changed backup field. F1 is a separate source-traced startup failure, not an asserted cause of those hangs. No fresh gate, full suite or Electron run requested or executed; H2 remains post-review work."
    }
  ]
}
```


## Recheck (2026-10-26) — Round 2

**Workflow:** /execution-critical-review  
**Agent:** codex-independent-reviewer (OpenAI; independent of the Claude/Anthropic author)  
**Verdict:** approved  
**Intent achieved:** yes

### Scope

Rechecked both MEU-94/MEU-93 handoffs, implementation-plan.md, task.md and walkthrough.md for Session 40's uncommitted work on main over 7b29fcd. The round 2 correction is EC-6 in theme.ts and theme-selects.test.tsx. Inspected the complete production diff, new boot/theme-test/probe files, changed tests, residual build-plan contracts and relevant API/router code. The prior round remains below its original headings; this recheck is the current decision.

Verification remained within the authorized boundary: the nine permitted Vitest files, typecheck, handoff/task validators and read-only source/receipt inspection. No full suite, session gate, Electron, build, install, generator or ledger mutation was run. D-118, D-119, D-120 and the squash are accepted. H2 reflection, metrics, issue resolution and approved statuses remain later implementer work. This reviewer changed only this report and scratch files.

### Prior Pass Summary

| Finding | Prior Status | Recheck Result |
|---------|-------------|----------------|
| F1 | open | fixed |

### Confirmed Fixes

F1 (High, AC-94; leaves AC-94.6 and AC-94.11) is closed.

- theme.ts:125 installs the 60,000 ms deadline independently of the API promise. Pending backend discovery, fetch or response-body waits therefore cannot hold the route gate indefinitely.
- theme.ts:116 defines finish(): set finished, clear the retry timer, clear the deadline, settle. Success first applies the resolved document theme (theme.ts:139), then finishes. A terminal error logs once, then finishes (theme.ts:157). The deadline logs once and finishes (theme.ts:129).
- Both continuations return when cancelled or finished (theme.ts:136, :143). If success runs first it clears the deadline; if the deadline runs first the late success is ignored. Timer callbacks and promise continuations run sequentially, so neither order can apply a late theme or produce a second terminal log.
- Unmount cancels the retry timer and deadline (theme.ts:164). The cancelled guard also ignores a pending request's later fulfillment or rejection.
- No reachable boot-request outcome inspected leaves the gate permanently closed: success, 500/599 and other terminal errors release it; FETCH_FAILED releases it while bounded retries continue; BACKEND_NOT_READY remains gated until success, final failure or the deadline; a request that never settles reaches the same fallback at the deadline. AppShell.tsx:295 substitutes a visible status while pending and renders the current root route once settled.

The fallback retains the current document theme. An unavailable backend cannot prove its stored theme; release after 60 seconds deliberately favors a usable route, as requested in F1. This does not claim that an unanswered backend supplied a persisted theme.

### Findings

| # | Severity | Blocking | Kind | Finding | File:Line | Recommendation | Status |
|---|----------|----------|------|---------|-----------|----------------|--------|
| F1 | High | no | behavior | Closed: complete-operation deadline releases the gate and ignores late answers; cleanup cancels both timers. | ui/src/renderer/src/lib/theme.ts:116; :125; :136; :143; :164; ui/tests/unit/theme-selects.test.tsx:465; :489; :580 | Retain the regression tests. | fixed |

### Remaining Findings

None. No new blocking or non-blocking finding was identified. Round 1 passes were checked for regressions without reopening their accepted decisions.

### Checklist Results

All independent executable checks preserved native exits and completed on the inspected working tree. UI cwd was P:/av-kit/ui; validators used P:/av-kit with RECEIPTS_DIR=C:/Temp/av-kit, UV_CACHE_DIR=C:/Temp/av-kit/uv-review-cache, UV_NO_SYNC=1 and PYTHONDONTWRITEBYTECODE=1.

| Check | Result | Exit | Decisive output |
|-------|--------|------|-----------------|
| Nine permitted Vitest files | pass | 0 | 9 files passed; 168 tests passed; 16.58 s. All 18 theme tests passed. React act warnings were emitted, without failures. |
| npm run typecheck | pass | 0 | tsc --noEmit; no diagnostics. |
| MEU-94 handoff validator with plan | pass | 0 | 16 AC rows; 2 decisions; durable evidence; matching plan_source; all 14 plan AC families. |
| MEU-93 handoff validator with plan | pass | 0 | 19 AC rows; 2 decisions; durable evidence; matching plan_source; all 14 plan AC families. |
| Task contract linter | pass | 0 | 24 rows; 22 command rows fully checked; dependencies acyclic; H1-5/H2-1 view_file exemptions. |

The structured verdict below records each exact executable command and manual observation. Scratch receipts are s40-r2-vitest.txt, s40-r2-typecheck.txt and s40-r2-{h94,h93,task}-validate.txt; these paths supplement the decisive output embedded here.

### IR, DR and Adversarial Verification

| Checks | Result | Evidence |
|--------|--------|----------|
| IR-1 runtime evidence | pass within authorized boundary | Independently passing rendered-component/API tests plus inspected author Electron receipts; no fresh reviewer Electron claim. |
| IR-2 seams | pass | THEME_PROBE answers/holds GET and updates its answer on PUT; unrelated requests pass through the page seam. Path tests inspect request bodies and counts. |
| IR-3 error mapping | n/a | No REST implementation or schema changed. API error behavior was traced through the boot gate. |
| IR-4 generalization | pass | One renderer dark-class read at theme.ts:86, one G30 pair definition at SelectInput.tsx:16; all listed consumers use the shared reactive hook. |
| IR-5 assertion strength | pass | New deadline, late-answer, unmount and actual AppShell route assertions close the missing behavior. Behavioral tests are Strong; source checks and the shared probe are Adequate. Details below. |
| IR-6 boundaries | pass | Existing settings and directory-dialog boundaries preserved; no new REST/IPC schema. Browse cancellation and Save-only/one-PUT behavior are asserted. |
| IR-7 AC coverage/deferral | pass | Both MEUs and their ACs remain mapped; no new missing product work. D-120's waived rows and pending H2 remain explicit. |
| DR claim verification | pass | Claimed production edits and EC-6 evidence agree with the inspected diff and tests. No whole-gate pass or reviewer Electron run is inferred. |
| AV-1–AV-6 | pass | Attributed mutation Red, independently passing Green, explicit behavior assertions, no new skip/only/xfail bypass, no unfinished product placeholder, source-backed contracts and human rulings. |

### Test Rigor and Recorded Red/Green

The F1 regressions are Strong:

- AC-94.6(f), theme-selects.test.tsx:465: a deferred request stays unsettled at 59,999 ms, settles with one log at 60,000 ms, preserves the current theme, then ignores a late Light answer without retrying or logging twice.
- AC-94.6(g), :489: unmount while pending; advancing beyond the deadline produces no theme log, and a later Light answer changes neither the theme nor call count.
- AC-94.11, :580: real AppShell plus real apiFetch with a never-answering fetch; the child is absent and the status present before the bound, then the child mounts and the status disappears at the bound. This proves the route release rather than only a hook boolean.

These tests use literal times and observable state/DOM/log counts, rather than copying the timer's implementation. The saved s40-f1-red-theme.txt shows exactly two AssertionError failures with the deadline delayed out of reach: :476 expected false to be true, and :598 expected null not to be null. Sixteen other tests passed. The cleanup case passed on both trees and is correctly described as a regression, not Red proof. The saved Green shows 18/18; this reviewer independently reran all 18 among the 168 passing tests. No reviewer mutation was made.

Existing AC-94.6(a)–(e) and AC-94.11 held-success/599 assertions remain unchanged and pass. The saved corrected-tree UI receipt shows 103 files / 1043 tests passed. The row-3 receipt records exit 0 and Electron 61 passed (2.7m). Those are inspected implementer evidence, not independently rerun full or Electron suites.

The rest of the round 1 IR-5 audit still applies after source reinspection:

| Tests | Rating | Round 2 observation |
|-------|--------|---------------------|
| theme-selects runtime color/hook/storage/retry/gate cases | Strong | Exact colors, identity without remount, option pairs, timing, errors, logs, late replies and DOM release. |
| theme-selects source cases; amended chrome/console/tts source assertions | Adequate | Supplement runtime proof; D-118 bans the component/named import while permitting the shared module path. |
| settings-path-fields and layout-primitives new cases | Strong behavior / Adequate source | Placeholder, same-row Browse, cancel, readOnly and disabled clicks; EC-2 checker has positive/negative fixtures, and actual helper callers are PathRow onBrowse. |
| Convert/TTS behavioral additions | Strong | Convert sends zero PUTs on Browse and one on Save; cancel leaves it clean. TTS cancel/typing retain initial value, chosen path sends exactly one PUT, and job activity disables Browse. |
| gui-actions-audit/test-ids additions | Adequate | Exact unique index row, registered/invoked IPC channel and production ID binding. |
| Settings/TTS/Convert Electron additions and THEME_PROBE | Strong assertions / Adequate shared helper | Literal computed-color oracles, held/released requests, no/stale/agreed mirror and persistence; Convert Browse also asserts geometry/value. No style result is fabricated. |

THEME_PROBE only registers an init script; the page seam owns its single reload. Request-time lookup avoids script-order dependence. Its MutationObserver samples actual inserted selects and its visible-color helper samples selected options; unit tests separately assert every option. No assertion is replaced by a manufactured color, and no early return suppresses a failed assertion.

EC-4 keeps its intent: TTSPage.tsx:64 defines the existing ~/Documents display fallback. Capturing the field's initial value in tts-page.behavior.test.ts:819 correctly asserts that typing/cancel preserves it; readOnly, zero-PUT and exact one-PUT checks remain. D-119's helper exception still requires every reference to originate in onBrowse, which the actual Settings source satisfies.

### Behavior and Gate Assessment

Live styles remain shared and reactive for Settings raw selects/options, TTS and VoiceCombobox SelectInput consumers, Convert, Capture Named and ConsolePanel's search input. boot-theme.ts runs as main.tsx's first import before createRoot; router.tsx:21 places the root Outlet inside AppShell, so every route shares the gate. The shell remains available during the wait.

PathRow's optional placeholder and browseDisabled remain additive. Convert patches only output_dir in its form; TTS preserves readOnly/busy/one-PUT behavior; Settings backup uses the shared primitive with the default placeholder. All Settings directory-dialog calls were traced to direct PathRow onBrowse handlers or the four browse-only helpers accepted by D-119.

D-120 stands. No whole run passed. Run 2 stopped at AC-19.17 before Electron; runs 1/3/4 and the recorded Green runs supply Electron AC support. AC-25.7 is baseline. ShareX's F2 reservation is external. The import timeout and capture hangs do not establish a regression from this change set; host-load causation remains unproved. AC-67.24 does exercise the changed backup field, supported here by targeted behavior checks and recorded passing runs. EC-6 specifically bounds the only product failure identified in round 1; no evidence establishes it caused the historic hangs.

No session-gate rerun is required or requested. H1-2/H1-6b remain waived. Approval is of the delivered implementation under those rulings, with the stated evidence limits; H2 is still subsequent work.

### Verdict

approved — F1 is fixed, the stated intent is achieved, and no blocking finding remains. The implementer can collect this target-bound round 2 verdict and continue the planned H2 closeout. This reviewer performs no correction, status/issue mutation or commit.

### Durable Command Evidence

```json
{"schema_version": "evidence.v1", "check_id": "s40-review-r2-1", "command": "rtk proxy npx vitest run tests/unit/theme-selects.test.tsx tests/unit/settings-path-fields.test.tsx tests/unit/layout-primitives.test.ts tests/unit/convert-page.behavior.test.ts tests/unit/tts-page.behavior.test.ts tests/unit/gui-actions-audit.test.ts tests/unit/console-polish.test.ts tests/unit/chrome-zorivest.test.ts tests/unit/tts-page.test.ts", "cwd": "P:/av-kit/ui", "scope": "Independent targeted UI tests", "phase": "targeted", "exit_code": 0, "result": "pass", "tested_state": "P:/av-kit main over 7b29fcd; uncommitted Session 40 including EC-6; observed 2026-10-26 round 2; no full-gate identity claim", "output": "P:/av-kit/ui: 9 files passed; 168 tests passed, including all 18 theme tests. Duration 16.58 s. React act warnings were emitted; no test failed.", "fresh": true}
```

```json
{"schema_version": "evidence.v1", "check_id": "s40-review-r2-2", "command": "rtk proxy npm run typecheck", "cwd": "P:/av-kit/ui", "scope": "TypeScript", "phase": "static", "exit_code": 0, "result": "pass", "tested_state": "P:/av-kit main over 7b29fcd; uncommitted Session 40 including EC-6; observed 2026-10-26 round 2; no full-gate identity claim", "output": "P:/av-kit/ui: tsc --noEmit completed without diagnostics.", "fresh": true}
```

```json
{"schema_version": "evidence.v1", "check_id": "s40-review-r2-3", "command": "rtk proxy uv run python tools/validate_closeout_artifacts.py --handoff .agent/context/handoffs/2026-10-24-gui-theme-path-fields-MEU-94-handoff.md --plan docs/execution/plans/2026-10-24-gui-theme-path-fields/implementation-plan.md", "cwd": "P:/av-kit", "scope": "MEU-94 handoff", "phase": "static", "exit_code": 0, "result": "pass", "tested_state": "P:/av-kit main over 7b29fcd; uncommitted Session 40 including EC-6; observed 2026-10-26 round 2; no full-gate identity claim", "output": "16 AC rows, 2 decisions, durable evidence, matching plan_source and all 14 plan AC families. Process-local RECEIPTS_DIR, UV_CACHE_DIR under C:/Temp/av-kit; UV_NO_SYNC=1; PYTHONDONTWRITEBYTECODE=1.", "fresh": true}
```

```json
{"schema_version": "evidence.v1", "check_id": "s40-review-r2-4", "command": "rtk proxy uv run python tools/validate_closeout_artifacts.py --handoff .agent/context/handoffs/2026-10-24-gui-theme-path-fields-MEU-93-handoff.md --plan docs/execution/plans/2026-10-24-gui-theme-path-fields/implementation-plan.md", "cwd": "P:/av-kit", "scope": "MEU-93 handoff", "phase": "static", "exit_code": 0, "result": "pass", "tested_state": "P:/av-kit main over 7b29fcd; uncommitted Session 40 including EC-6; observed 2026-10-26 round 2; no full-gate identity claim", "output": "19 AC rows, 2 decisions, durable evidence, matching plan_source and all 14 plan AC families. Same scratch-cache/read-only uv environment.", "fresh": true}
```

```json
{"schema_version": "evidence.v1", "check_id": "s40-review-r2-5", "command": "rtk proxy uv run python tools/lint_task_contract.py --task docs/execution/plans/2026-10-24-gui-theme-path-fields/task.md --allowed-builder-classes avkit_builder,avkit_coordinator,avkit_verifier", "cwd": "P:/av-kit", "scope": "Task contract", "phase": "static", "exit_code": 0, "result": "pass", "tested_state": "P:/av-kit main over 7b29fcd; uncommitted Session 40 including EC-6; observed 2026-10-26 round 2; no full-gate identity claim", "output": "24 rows; 22 command rows fully checked; dependencies acyclic; H1-5/H2-1 view_file exemptions. Same process-local environment.", "fresh": true}
```

### Structured Verdict



```json
{
  "schema_version": "review-verdict.v2",
  "date": "2026-10-26",
  "review_mode": "execution",
  "loop_id": "s40-execution-2026-10-24-gui-theme-path-fields",
  "round": 2,
  "target_plan": "docs/execution/plans/2026-10-24-gui-theme-path-fields/implementation-plan.md",
  "agent": "codex-independent-reviewer",
  "requested_verbosity": "standard",
  "verdict": "approved",
  "summary": "F1 is fixed; no blocking findings remain. Independent checks passed: 168 tests across nine files, typecheck, both handoff validators and the task linter. D-120 is respected; no full suite, session gate or Electron was run by this reviewer.",
  "intent_anchor": "Confirm Session 40's delivered code makes Settings, TTS and Convert selects follow the theme live and on cold boot, and gives Convert, TTS and Settings one Browse path field, with honest Red/Green and gate evidence.",
  "intent_achieved": "yes",
  "findings": [
    {
      "id": "F1",
      "severity": "High",
      "confidence": "High",
      "blocking": false,
      "subject": "deliverable",
      "finding_kind": "behavior",
      "finding": "Closed: the mount-time deadline releases the route gate at 60 seconds even when GET /settings/ui never settles. finish() clears both timers; finished/cancelled guards ignore late fulfillment and rejection. No regression from round 1 was identified.",
      "file_line": "ui/src/renderer/src/lib/theme.ts:116; ui/src/renderer/src/lib/theme.ts:125; ui/src/renderer/src/lib/theme.ts:136; ui/src/renderer/src/lib/theme.ts:143; ui/src/renderer/src/lib/theme.ts:164; ui/tests/unit/theme-selects.test.tsx:465; ui/tests/unit/theme-selects.test.tsx:489; ui/tests/unit/theme-selects.test.tsx:580",
      "recommendation": "No further correction required; retain the deadline, late-answer and unmount regressions.",
      "status": "fixed",
      "violates": "AC-94"
    }
  ],
  "checklist_results": [
    {
      "check": "Independent targeted UI tests",
      "result": "pass",
      "command": "rtk proxy npx vitest run tests/unit/theme-selects.test.tsx tests/unit/settings-path-fields.test.tsx tests/unit/layout-primitives.test.ts tests/unit/convert-page.behavior.test.ts tests/unit/tts-page.behavior.test.ts tests/unit/gui-actions-audit.test.ts tests/unit/console-polish.test.ts tests/unit/chrome-zorivest.test.ts tests/unit/tts-page.test.ts",
      "exit_code": 0,
      "evidence": "P:/av-kit/ui: 9 files passed; 168 tests passed, including all 18 theme tests. Duration 16.58 s. React act warnings were emitted; no test failed."
    },
    {
      "check": "TypeScript",
      "result": "pass",
      "command": "rtk proxy npm run typecheck",
      "exit_code": 0,
      "evidence": "P:/av-kit/ui: tsc --noEmit completed without diagnostics."
    },
    {
      "check": "MEU-94 handoff",
      "result": "pass",
      "command": "rtk proxy uv run python tools/validate_closeout_artifacts.py --handoff .agent/context/handoffs/2026-10-24-gui-theme-path-fields-MEU-94-handoff.md --plan docs/execution/plans/2026-10-24-gui-theme-path-fields/implementation-plan.md",
      "exit_code": 0,
      "evidence": "16 AC rows, 2 decisions, durable evidence, matching plan_source and all 14 plan AC families. Process-local RECEIPTS_DIR, UV_CACHE_DIR under C:/Temp/av-kit; UV_NO_SYNC=1; PYTHONDONTWRITEBYTECODE=1."
    },
    {
      "check": "MEU-93 handoff",
      "result": "pass",
      "command": "rtk proxy uv run python tools/validate_closeout_artifacts.py --handoff .agent/context/handoffs/2026-10-24-gui-theme-path-fields-MEU-93-handoff.md --plan docs/execution/plans/2026-10-24-gui-theme-path-fields/implementation-plan.md",
      "exit_code": 0,
      "evidence": "19 AC rows, 2 decisions, durable evidence, matching plan_source and all 14 plan AC families. Same scratch-cache/read-only uv environment."
    },
    {
      "check": "Task contract",
      "result": "pass",
      "command": "rtk proxy uv run python tools/lint_task_contract.py --task docs/execution/plans/2026-10-24-gui-theme-path-fields/task.md --allowed-builder-classes avkit_builder,avkit_coordinator,avkit_verifier",
      "exit_code": 0,
      "evidence": "24 rows; 22 command rows fully checked; dependencies acyclic; H1-5/H2-1 view_file exemptions. Same process-local environment."
    },
    {
      "check": "F1 closure and retry preservation",
      "result": "pass",
      "procedure": "Trace deadline, retry, success, rejection and cleanup paths against AC-94.6(a)-(g) and AC-94.11; inspect the independently passing assertions.",
      "observer": "codex-independent-reviewer",
      "exit_code": null,
      "evidence": "theme.ts:116-169 bounds the complete operation, clears both timers on completion, and ignores late answers. Tests assert false at 59,999 ms, true and one log at 60,000 ms, no late theme flip or duplicate log, clean unmount, and actual AppShell route release. Existing 500, FETCH_FAILED, BACKEND_NOT_READY, backoff and 599 cases pass. Success clears the deadline before it can log; sequential callbacks and finished guards prevent competing terminal actions."
    },
    {
      "check": "IR-5 Red/Green and THEME_PROBE",
      "result": "pass",
      "procedure": "Inspect saved F1 Red/Green/full-UI/row-3 receipts, changed assertions and the Electron theme helper; compare EC-4 and D-118/D-119 with their contracts.",
      "observer": "codex-independent-reviewer",
      "exit_code": null,
      "evidence": "Saved deadline-disabled Red: 2 assertion failures, 16 passes, at settled=true and route-child presence; Green: 18/18. Recorded corrected-tree full UI: 1043/1043; row 3 exit 0, Electron 61 passed. These are author receipts, not reviewer reruns. New regressions assert behavior using literal times, not timer internals. THEME_PROBE records computed colors and held/released requests; it does not synthesize style results. EC-4 retains typing/cancel invariance and exact PUT checks; D-118/D-119 retain intent."
    },
    {
      "check": "Live themes, cold boot and path contracts",
      "result": "pass",
      "procedure": "Compare production/test diffs and new files with both handoffs, plan ACs, source residual specifications, router and API behavior.",
      "observer": "codex-independent-reviewer",
      "exit_code": null,
      "evidence": "One dark-class read (theme.ts:86), one pair definition (SelectInput.tsx:16), shared reactive select/options and all listed consumers. boot-theme is main.tsx's first import; the root Outlet is inside AppShell's gate. Convert Browse patches only the form and Save PUTs; cancel is inert. TTS remains read-only, disables Browse while busy and PUTs once. Settings backup keeps its placeholder/Browse; all directory-dialog callers originate from PathRow onBrowse. Round 1 passes remain supported."
    },
    {
      "check": "D-120 gate and residual risk",
      "result": "pass",
      "procedure": "Assess walkthrough gate runs 1-4, their failing tests and retained summaries alongside the correction evidence; apply the supplied human rulings.",
      "observer": "codex-independent-reviewer",
      "exit_code": null,
      "evidence": "No whole gate run passed. Run 2 stopped before Electron; runs 1/3/4 and recorded Green runs supply Electron AC evidence. AC-25.7 is baseline; ShareX F2 failure is external. AC-19.17 timeout and AC-67.24/.35 hangs do not establish a change-set regression; host-load causation remains unproved. D-120 waives H1-2/H1-6b and forbids rerunning the gate. H2 remains implementer work after this verdict."
    }
  ]
}
```

🕐 Completed: 2026-10-26 17:01 (EDT)
