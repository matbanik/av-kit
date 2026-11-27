---
date: "2026-11-26"
review_mode: "plan"
target_plan: "docs/execution/plans/2026-11-26-capture-key-inbox-scrollbars/implementation-plan.md"
verdict: "approved"
findings_count: 0
template_version: "2.2"
requested_verbosity: "standard"
agent: "codex-independent-reviewer"
loop_id: "cki-plan-2026-11-26-capture-key-inbox-scrollbars"
round: 2
---

# Critical Review: capture-key-inbox-scrollbars

## Scope

**Intent anchor:** “after this session the Capture page does three things it does not do today.” The plan should make the saved capture key appear throughout the app, make the catalog and selection follow the saved inbox, and add draggable position bars without changing existing zoom and pan gestures.

**Review type:** independent, read-only plan review, PR-1 through PR-9, against the working tree at `c0acc89e8b0eda65dd9dcaa2c008e03af35e33b4`. Author: Claude Code/Anthropic; reviewer: Codex. Both target files were read. Sibling plans were consulted only for the named overlaps. Grouping and triage decisions, D-1413's treatment, and the stated scope limits were accepted as supplied. This verdict is the plan-review gate only; Mat's supplied execution authorization and the Session 104 dependency remain separate.

## Findings

| # | Severity | Blocking | Kind | Finding | File:Line | Recommendation | Status |
|---|----------|----------|------|---------|-----------|----------------|--------|
| F1 | High | yes | behavior | **Row 0 must stop on the actual OpenAPI document.** Its mandatory check requires every by-id capture operation to document 404, but all nine operations lack that response. For example, GET has only 200/422 and DELETE only 204/422. The plan simultaneously forbids changing the document. Consequently execution reaches S8 before any MEU can start, even though runtime `NotFoundError` already maps to 404. This blocks delivery of AC-166.3/AC-166.4 and rests on D-1424's incorrect factual premise. Confidence: High. | `docs/execution/plans/2026-11-26-capture-key-inbox-scrollbars/implementation-plan.md:381`; `task.md:48`; `openapi.committed.json:4876`; `packages/api/src/avkit_api/errors.py:37` | Correct the documented-response claim and replace the impossible prerequisite with proof of the existing runtime 404 mapping/body, retaining AC-166.4's real API test and unchanged reply shape. If documenting responses is desired instead, explicitly reconcile that scope with the byte-identical-document contract before execution. | fixed |
| F2 | High | yes | behavior | **An old-folder operation can select an id permanently exempt from clearing.** Start a crop in A, save inbox B while the crop is running, and let B's catalog answer precede the crop continuation. `crop_shot` captured A before its work; `cropCapture` refreshes the now-current catalog B, then `commitCrop` unconditionally selects its A result. No catalog answer has held that new id, so `INBOX_SELECTION_LEFT` keeps it indefinitely. The detail fetch and every subsequent save/copy action then return 404 under `INBOX_SCOPE_BY_ID`. AC-166.6/AC-166.7 do not cover this interleaving. Confidence: High. | `docs/execution/plans/2026-11-26-capture-key-inbox-scrollbars/implementation-plan.md:170`; `task.md:56`; `packages/core/src/avkit_core/services/capture.py:1884`; `ui/src/renderer/src/features/capture/capture-commands.ts:165`; `CapturePage.tsx:1002` | Bind selection-producing operations and catalog answers to the saved inbox generation. Ignore a late result from a prior inbox; retain the unseen-result exception only within its original inbox. Add a deterministic test that holds a crop response, saves B, returns B's list, then releases the old result and asserts B remains selected with no old-id detail/error. | fixed |
| F3 | Medium | no | behavior | **Exhausted status following has no user-facing unavailable state.** AC-165.6 explicitly tests ten never-matching reads, but only counts them. With saved F9 and status still reporting F2, registered, `inUse=false`, `CAPTURE_KEY_FOLLOW` ends with no key cap and no banner while the empty state says “Press F9” and help says “F9 still works.” This is distinct from a normal collision, which does have a warning. It can mislead users after registration/application failure. Confidence: High for the specified state; its real trigger was not launched in this review. | `docs/execution/plans/2026-11-26-capture-key-inbox-scrollbars/implementation-plan.md:164`; `implementation-plan.md:180`; `implementation-plan.md:261`; `ui/src/main/capture-runtime.ts:70`; `ui/src/main/capture-hotkey.ts:31` | Keep the saved-key policy, but specify and test an unconfirmed/unavailable notice after the bounded follow expires, including a mismatched status and a rejected status read. Do not claim successful registration merely from the saved value. | fixed |
| F4 | Medium | no | behavior | **The first scan loop can still touch an out-of-scope row through a file link.** With inbox A containing a file symlink to a previously cataloged B image, `child.resolve()` produces B's original path. The unchanged first loop probes it and can save refreshed size/dimensions to B's row before the proposed second-loop scope check runs. Thus `INBOX_SCOPE_SCAN` does not fully deliver the stated “rows of other folders ... left alone” promise. Ordinary resolved directory aliases are a different case and work with the proposed equality. Confidence: High from the call chain; no real inbox/link was opened. | `docs/execution/plans/2026-11-26-capture-key-inbox-scrollbars/implementation-plan.md:167`; `task.md:53`; `packages/core/src/avkit_core/services/capture.py:668`; `capture.py:696` | Check the resolved child's parent against the captured inbox before probing or upserting it. Add a link or fake-resolver case proving that an out-of-scope existing row is neither probed nor saved by either scan loop. | fixed |

## Review Summary

**Approved. F1–F4 are fixed in the plan; no new material finding.** This is approval of the corrected design and its planned proof, not certification of unimplemented code or unrun tests. The Findings table retains the prior findings as history; `findings_count: 0` means no surviving open findings.

One clerical correction remains: `task.md:74` says eight AC-166 criteria but its embedded command still has `('166',7)`. Change that literal to `('166',8)` before executing H1-6a. The canonical AC table and both Red/Green rows are unambiguous; this is the stale-number case covered by the Materiality Gate, not a new behavior finding.

## R1 — Do the corrections close their findings?

**F1 accepted.** Row 0 now checks the real runtime mapping, not nonexistent OpenAPI responses (`implementation-plan.md:193`, `:242`, `:384`, `:438`, `:447`, `:526`; `task.md:48`). `errors.py:37` maps `NotFoundError` to 404, and its handler constructs the existing error envelope. All nine by-id OpenAPI operations still omit 404. AC-166.4 tests actual HTTP behavior without requiring a document change. The impossible prerequisite is gone.

**F2 accepted.** `INBOX_SELECTION_LEFT` now binds the selection to its saved inbox, and `INBOX_RESULT_BOUND` governs crop and flatten-to-copy continuations (`implementation-plan.md:171–172`, `:195`). The hook already holds the saved-only `baseline` (`useCaptureSettings.ts:105`); exposing it and maintaining a live saved-inbox reference lets the continuation compare start with current end state. This needs no IPC, route or catalog-hook change. Reading the same closed-over render value twice would not implement the stated end-state contract.

AC-166.8 and row 4 require both response orders; row 5 implements them (`implementation-plan.md:275`; `task.md:55–56`). Today's crop continuation unconditionally selects and announces the result (`CapturePage.tsx:1000–1003`), so the held A crop released after B is an assertion Red. Today's detail catch dispatches an error (`:842–848`), so a held old detail returning 404 before B's list also has an assertion oracle. The same-inbox crop guard preserves normal selection. At Green the described contracts reject the old result and silently clear the old selection. While B's list is held, the clear must also avoid reselecting A from cached items through the newest-shot effect (`:663–670`); the no-error requirement applies throughout that held interval. These are implementation obligations of the AC, not a claim that Green has been run.

**F3 accepted.** The notice now requires no successful confirmation of the saved key, or a refused read, and does not claim registration (`implementation-plan.md:165`, `:182`, `:263`; `task.md:58–59`). A successful read with the saved accelerator and `registered=true` confirms it and stops the follow; expiration cannot then create the notice for that follow. A key that main registered but the renderer could not read can conservatively show “cannot confirm”; that wording remains true about the renderer's knowledge. A new saved key starts its own follow; superseded callbacks must respect that scope. The never-matching and refused-read cases now assert the notice and absent cap, rather than only counting reads. Default confirmed/in-use pins remain compatible.

**F4 accepted.** The first-loop check is explicitly after `child.resolve()` and before `probe`/upsert (`implementation-plan.md:168`, `:192`; `task.md:52–53`). A normal resolved direct child retains the inbox as its parent and proceeds. A file link resolving into B is skipped before B is probed or saved; the second-loop guard independently skips B's row. AC-166.2 now requires the probe spy and unchanged row, and row 2's `--require` names that test. Ordinary in-folder ingestion remains covered by AC-166.1 and the existing service tests.

## R2 — Did the corrections break plan consistency?

Accepted: the AC table contains 10, 8 and 8 criteria; row 4 requires AC-166.8, its guards are named separately, row 5 implements both inbox contracts, and the new notice and linked-file test reach their corresponding Red and Green rows. The Files Modified inventory includes every affected product/test file, and the commit draft still describes the delivered behavior without an incompatible promise. `saved` is needed by row 5, so expose the existing baseline there when implementing the inbox binding; row 7 then reuses it for the key. The later row's repeated mention is not a requirement to postpone that prerequisite.

Not accepted as corrected: H1-6a's executable count is still seven, despite its description saying eight (`task.md:74`). The exact one-literal correction is recorded in Review Summary. No further existing expectation change is required by these corrections.

## Q1 — Goal and proof

Accepted: the saved-key empty state has AC-165.10; the folder switch and filmstrip have AC-166.7 plus the new race oracle AC-166.8; both bars and thumb movement have AC-167.7. Those tests distinguish today's app from the intended behavior. With the four material corrections applied as specified, executing the plan delivers the three stated outcomes. No remaining substantive rejection.

## Q2 — Key texts

Accepted: the current renderer/main literal sweep still finds the eight visible texts, plus defaults, the reserved key and comments. Main/tray adds no missed visible key label. Production importers of the help constants are the two pages and HelpCard; all are covered. The formatter retains chords and supplies F2 for blank input. Default exports preserve rendered pins. The local STE receipt reports no problems for token/default/chord substitutions; the independent in-memory token-to-F2 round trip remains identical, with capture hash `daf13885bb7aeb447c50d4b1e1e41226d27443d7c58923426acfb4339efb5721`. F3's unavailable-state gap is now closed as described under R1. No image retake is required by this change.

## Q3 — Four changed expectations

Accepted: row 6 names the two AC-39.13 topic entries, its empty-state regex and AC-61.16's F2 source scan, with their exact token replacements. The remaining route/help/collapse/startup checks stay. AC-165.3–165.5 and AC-165.8 cover the default and saved-key readings. The current test sweep found no additional incompatible literal pin; other matches are default fixtures/readings, reserved shortcuts or unrelated finding identifiers. The two raw-JSON readers keep expected values while changing their source. No new rejection.

## Q4 — Catalog scope and by-id safety

Accepted: resolved direct-parent equality matches the existing service convention. The public shot-id census still has twelve methods; the direct lookups and callers through get_shot cover them without changing transport. Destructive entry calls can refuse an old-folder id before operating on its files. Name collisions still inspect repository rows rather than the filtered service list. F1 and F4 are closed; no remaining mismatch between runtime 404 behavior and the byte-identical-document requirement. Historical paths are not automatically migrated after a folder rename; the plan does not promise migration.

## Q5 — Saved inbox and selection

Accepted: the PUT precedes query invalidation, key-only saves avoid catalog invalidation, and the new saved-inbox binding closes the stale-operation exception. Unsaved-mark loss is explicit in the user-facing disclosure. AC-166.8 specifically covers the slow-list/early-detail order that ordinary refetch cancellation did not cover. The result guard must inspect current saved state at completion, and selection reset must remain silent while the new list is outstanding. No new rejection beyond those already-enforced AC obligations.

## Q6 — Bars and gestures

Accepted unchanged from round 1: geometry agrees with viewTransform and panBy, with the correct sign, endpoints, one-axis/equal-size/Fit cases and zero-free-track guard. Pointer capture and stopped events isolate a thumb drag from drawing, sampling and history. Existing wheel/Space/middle-drag tests remain pinned. Overlay interception, no keyboard control and no track click are disclosed choices. Fit/zoom-out remains the way to edit extreme covered edge pixels. The theme oracle checks the contrasting fill/edge pair; it does not prove contrast against every possible image. No new rejection or broader accessibility claim.

## Q7 — mini-air Electron evidence

Accepted: exactly four assertion failures are required at Red, and proof requires the four expected results, matching snapshot, no skips/flakes/unexpected results, empty overlap and clean rejection logs. Wait/tool-stop exits never pass. Scratch app data, temp inboxes and closing the owning app isolate saved settings and release its global hotkey registration. No remote command was run in this review.

**Watcher caveat closed by narrowing the claim.** Main still starts its default watcher before its first settings read (`index.ts:601–609`; `capture-inbox-watch.ts:148–150`). AC-165.10 and task row 1 now acknowledge that filename listing and promise only that the test/catalog does not read/store real Pictures images. That is consistent with the launch code and avoids implying a startup change.

**Mixed-byte caveat: no remaining material gap for the supplied overlap.** Session 104's test-id addition is a standalone constant block; it introduces no dependency on its product implementation. S4/content binding protects subsequent edits, while remote-fresh must compare the complete ui/packages tree, including untracked files, before reusing row 10 (`implementation-plan.md:410`, `:425`; `task.md:44`, `:64`, `:69`). A baseline hash alone does not establish byte ownership, and this review does not treat it as doing so. The stronger whole-tree equality rejects reuse when other omitted product bytes differ. Snapshot composition and the actual remote result remain execution checks; neither is certified here.

## Q8 — Order, gate and ownership

Accepted: each behavioral Red precedes its Green, and the added race/link/notice checks stay pinned thereafter. The planned gate includes full pytest/Vitest, types, lint, UI build, OpenAPI and STE. Unchanged MCP transport/mocks do not require a new MCP contract shape. Session 105's HelpCard class change and help-shot retake can preserve the token accessors/optional prop; Session 106's Settings additions can preserve the saved-key help call. Sibling files were inspected only for those overlaps and Session 104's test-id block. The single stale H1-6a count is the clerical note above. No commit, push, tag or release is part of this review.

## Checklist Results

All manual observations below were performed by **codex-independent-reviewer** against the current working-tree files; their exit code is null. They assess the plan, not executed product behavior.

| Check | Result | Observation |
|---|---|---|
| PR-1 plan/task alignment | pass | Manually traced the three MEUs, both inbox contracts, Red/Green requirements and gate. One inferable stale count is recorded above. |
| PR-2 unstarted state | pass | Read all task rows; new product modules remain absent; scoped tracked product/test diff is empty at inspection. |
| PR-3 task contracts | pass | Read the entire task table: owners, outputs, validation, dependencies and unchecked status are present. |
| PR-4 validation realism | pass | Compared scheduled scripts' descriptions with production entry points and negative oracles; F1's impossible prerequisite is removed. Scripts are planned work, not existing executed gates. |
| PR-5 source-backed planning | pass | Compared the three 09 homes, issues, grouping Session 103 and HDP hand-over with the design. |
| PR-6 corrections readiness | pass | Rechecked every prior finding against the corrected contracts and dependent rows; three execution handoffs and rolling review are named. |
| PR-7 scope discipline | pass | Compared exclusions, accepted decisions and sibling overlaps; no required product deliverable is disguised as a deferral. |
| PR-8 reachable behavioral controls | pass | Traced runtime 404 mapping, first scan loop, selection/crop/convert continuations and hotkey status; negative ACs address the four defects. |
| PR-9 governing contracts | pass | Read the named contracts and dependent AC/task references; no unresolved materially different behavior. |
| Product suites and remote execution | n/a | Prohibited by this review's scope; none run. |

```json
{"schema_version":"evidence.v1","check_id":"cki-plan-round2-static-probes","command":"$env:PYTHONDONTWRITEBYTECODE='1'; $env:RECEIPTS_DIR='C:/Temp/av-kit'; rtk proxy python -B C:/Temp/av-kit/2026-11-26-capture-key-inbox-scrollbars/review/round2-probes.py","cwd":"P:/av-kit","scope":"plan AC/row census, source AST, OpenAPI JSON, default-reading round trip and illustrative contract states","phase":"plan-review","exit_code":0,"result":"pass","tested_state":"HEAD c0acc89e8b0eda65dd9dcaa2c008e03af35e33b4; implementation-plan sha256 c6be40849a942af6bebc71b93a6af39a6348a2328e35c12cb39def2b477ec855; task sha256 f2bc1457f97845bcdf145669e03e7da8639e6d7b8366aaf25f4b5fd888781ef2; inspection identity only","output":"AC counts 165=10,166=8,167=8; H1-6a executable literal remains 166=7. Row 4 requires AC-166.8; rows 4/5 carry result binding; row 2 requires linked-file spy; rows 6/7 carry unconfirmed notice. New product modules absent. Twelve public shot-id methods. Runtime NotFoundError maps to 404; nine documented by-id operations omit 404. Direct-parent example accepts normal in-folder path and rejects outside path. Default-reading round trip true; hash daf13885bb7aeb447c50d4b1e1e41226d27443d7c58923426acfb4339efb5721. Illustrative result equality A-to-B false/A-to-A true; exhausted notice confirmed false/mismatched true.","fresh":true}
```

The probe's exit 0 means inspection completed. Its small state examples illustrate the written contracts; they are not execution of a proposed implementation. No repository file was written, no network/SSH used, and no prohibited file, real inbox or user screenshot opened. Unrelated Session 104 work was excluded from findings and from this limited inspection identity.

## Recheck (round 2)

### Prior Pass Summary

| Finding | Prior Status | Recheck Result |
|---|---|---|
| F1 | open | fixed |
| F2 | open | fixed |
| F3 | open | fixed |
| F4 | open | fixed |

### New Findings

| # | Severity | Blocking | Kind | Finding | File:Line | Recommendation | Status |
|---|----------|----------|------|---------|-----------|----------------|--------|

## Verdict

**approved** — the corrected plan delivers the registered intent: “after this session the Capture page does three things it does not do today.” F1–F4 are fixed; there is no new High/Critical finding or surviving blocker. Correct the stale AC-166 count in task H1-6a as noted above. This approval satisfies the plan-review gate only and does not certify execution results or independently authorize any action.
