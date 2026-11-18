---
date: "2026-11-18"
review_mode: "plan"
target_plan: "docs/execution/plans/2026-11-17-ui-small-fixes/implementation-plan.md"
verdict: "approved"
findings_count: 2
template_version: "2.2"
requested_verbosity: "standard"
agent: "codex-independent-reviewer"
loop_id: "us-plan-2026-11-17-ui-small-fixes"
round: 2
---

# Critical Review: ui-small-fixes

> **Review Mode:** plan  
> **Verdict:** approved  
> **Intent achieved:** yes

## Scope

**Intent anchor:** one F1 pressed while the lazy Convert or Capture page is still loading opens that page's help panel once when it mounts, never toggles another page's panel, and is dropped if the user leaves first; with Advanced collapsed or expanded on the Downloader page the queue starts one standard gap (16 px) below the disclosure at 1280×800 and at 700 px, and Advanced still shows its eight controls in the same order; `npm run preview` with `ELECTRON_RUN_AS_NODE` set clears it, says so on stderr and opens the app window, as `npm run dev` does; each fix is proved by an Electron E2E test or a script proof in the gate, with no network and no manual check.

Reviewed the complete current implementation-plan.md and task.md, Session 94's grouping and three issue records, the MEU-158/159 build-plan homes, HDP §§4a–6, the expert-pass receipt and the cited product/test/helper sources needed for Q1–Q6. Applied PR-1–PR-9 with the Materiality Gate and the user's substance-only review scope. Claude Code/Anthropic authored the plan; Codex/OpenAI is the independent reviewer.

Round 2 rechecks R1-F1 and R1-F2 and examines the changed mode-visibility and stream-separation surfaces for new failures. The original Findings table is retained below with historical assessments and citations; its statuses are updated to fixed. Neither finding blocks this revision. No Critical finding exists and no new material defect was demonstrated.

The target folder contains only the two plan documents. Scripts, tests and implementation work are explicitly scheduled for execution. Only C:/Temp/av-kit was written; the coordinator owns canonical publication and ledger recording.

## Findings

| # | Severity | Blocking | Kind | Finding | File:Line | Recommendation | Status |
|---|---|---|---|---|---|---|---|
| R1-F1 | High | yes | behavior | **The required gap proof asks for DOM states the unchanged page cannot produce.** Confidence: High. Row 3 defines statusEmpty as no add-status/error-banner child, but both children always exist as hidden placeholders on a fresh page (DownloaderPage.tsx:824,831). Its fit predicate therefore rejects all four cases even if the geometric hypothesis is correct. Independently, AC-159.3 and row 3 require all eight IDs in a list of visible elements, although cookie-browser/profile are shown only in browser mode and cookie-file only in file mode (cookie-bar.ts:78-83; DownloaderPage.tsx:719,748,766). A fresh none-mode page supplies only five requested visible IDs; browser supplies seven and file six. Thus row 3 necessarily stops at S9 before STATUS_SLOT, and the expanded Green oracle also cannot pass without changing unrelated cookie behavior. Violates AC-159.1, AC-159.3 and AC-159.4; this prevents delivering MEU-159 and the later preview fix in the dependency sequence. | docs/execution/plans/2026-11-17-ui-small-fixes/task.md:51; docs/execution/plans/2026-11-17-ui-small-fixes/implementation-plan.md:205; ui/src/renderer/src/features/downloader/DownloaderPage.tsx:824; ui/src/renderer/src/features/downloader/cookie-bar.ts:78 | Define empty by absence of displayed message text, allowing the existing hidden slots. Check the eight IDs' DOM presence/order separately from visibility, preserving the existing mode-dependent visibility. If visibility across modes is tested, use isolated local fixtures/seams without real cookie actions. Update the shared row-3/row-3a oracle and AC-159.3/.4 together before Red; retain both widths and both disclosure states. | fixed |
| R1-F2 | Medium | no | control-defeat | **The inherited preview proof cannot establish that the notice was written to stderr.** Confidence: High. mechanism: task-row-completion-predicate. The specified copy merges stderr into stdout at Popen and searches the combined log for the notice. A wrapper that writes the correct notice only to stdout while opening its own window would satisfy this notice oracle and the prescribed unit checks, despite AC-4's stderr claim. The planned wrapper correctly calls for stderr; this is a bounded proof gap, not evidence that the proposed implementation uses the wrong stream. | docs/execution/plans/2026-11-17-ui-small-fixes/implementation-plan.md:329; docs/execution/plans/2026-11-17-test-run-reliability/dev-proof.py:307; docs/execution/plans/2026-11-17-test-run-reliability/dev-proof.py:365 | Keep stdout and stderr in separate scratch logs and inspect only stderr for the notice. Add an adversarial selftest where stdout alone contains the notice and the stderr requirement fails. Preserve the existing PID/creation-time ownership and cleanup checks. | fixed |

## Q1 — Goal

Accepted: AC-158.1–.14 and rows 1/1a/1b/2/7 cover held F1, joining, route isolation, leaving, mounted delivery, StrictMode and Ctrl+O preservation. AC-159.1–.7 and rows 3/3a/4/7 now provide satisfiable, separate status/order/visibility/geometry checks in all four viewport/disclosure cases. AC-1–AC-5 and rows 5/6/H1-2 cover environment clearing, a stderr notice and an owned app window. Proof is automated; no manual-check row exists.

No outstanding rejection. Executing the revised plan would achieve the registered intent. This is approval of the unstarted plan, not evidence that the fixes already work.

## Q2 — Held request

Accepted: HELD_REQUEST preserves token identity, same-key join, replacement, off-route drop, acknowledged/unreceived settle and take-before-delayed-run behavior from convert-commands.ts:354-400. BROWSE_HOLD retains every export, the unchanged unit/page pins and repeated Ctrl+O Electron tests. HELP_HOLD settles synchronously: only a route-matching card acknowledges, and a received toggle is cleared rather than held. HELP_TAKE_ON_MOUNT listens first and takes once, so StrictMode's second effect finds nothing.

No material delivery-design defect found. Unit and Electron proofs remain execution obligations.

## Q3 — Route scope and D-1176

Accepted: HELP_FEATURE_ROUTE matches router.tsx:28-63 and every page's actual HelpCard feature, including `converter` → `/convert`. HELP_ROUTE_SCOPE prevents the retained old page from toggling while a new chunk loads; the fixed map also prevents a late-mounted old card from adopting the current hash. Detail-less events still toggle, preserving help-card.test.ts:56-81; the off-route sessionStorage path remains intact (:109-123).

D-1176 adopts the expert correction and falls within the supplied M-5 hand-over. No new mandatory-human fork or route-scope defect demonstrated.

## Q4 — Downloader gap and D-1177/D-1180

Accepted: the revised status predicate requires empty displayed text and both hidden placeholders (plan:369; task:51-52), matching DownloaderPage.tsx:818-833. DOM order and mode visibility are checked separately: all eight IDs remain in order, with five/seven/six visible in none/browser/file and none collapsed (plan:36-37,204-207,370-372). The checked radio has the mode value (SegmentedControl.tsx:48-54); the visibility functions and ancestors match those sets (cookie-bar.ts:78-83; DownloaderPage.tsx:719,748,766). Selectors now resolve the real form, containing section and panel without new production IDs (plan:360-362).

The exact task-row-3 pure predicate accepted all 12 synthetic mode/case records and rejected 90 corruptions of status, order, inventory, visibility, geometry or expanded mode. These are logical checks, not measured Electron boxes. Row 3 still measures the unchanged Downloader before STATUS_SLOT, and S9 stops on a failed hypothesis. Rows 3a/4 keep separate four-case assertions and the visible-message guard. D-1177 explicitly limits empty-band removal to a fresh page and preserves message placement, children, classes and test IDs. R1-F1 is fixed; no new material defect found.

## Q5 — Preview and Session 90 preservation

Accepted: PREVIEW_WRAPPER shares the existing spawn body while retaining DEV_NOTICE, devEnv, devArgs, isEntry, exitCodeFor, argument/cwd handling, signals, errors and exit behavior (plan:121; electron-vite-dev.mjs:12-79). PINS_NAMED changes only dev-script.test.ts:64, and COMMANDS_DOC updates the actual preview row. AC-3 distinguishes the base defect from a broken window detector; AC-4/AC-5 check preview and dev after the refactor.

The revised copy instructions explicitly replace Session 90's merge with distinct stdout/stderr files, inspect only stderr for `--expect-notice`, and record stdout separately (plan:330-332; task:44,55-56,63). Through run()/simulate(), fake Popen must write into the handles actually passed: stderr-only passes; stdout-only, missing notice and an unexpected stderr notice fail; merged or shared handles fail the selftest. The gate runs that selftest. Root PID/parent/creation-time checks, immutable process identities, post-window owner rechecks and recorded-tree cleanup are retained (dev-proof.py:208-249,325-355). R1-F2 is fixed in the plan. The new preview-proof.py is explicitly assigned row-0 creation and does not exist yet; no claim is made that its future implementation or selftest ran here.

## Q6 — Electron proof, Red honesty and moved HEAD

Accepted: row 1a proves both chunk delays, page absence, eventual mount and absence of chunk/MIME errors before the Red tests use the handler. It copies the working file-protocol pattern and delegates local reads with bypassCustomProtocolHandlers (convert-browse-mount.test.ts:168-185). Race preconditions throw `setup:` errors; Reds must fail by behavior assertions, with passing guards and immutable expectations. Explicit per-title repeat counts, one worker, no retries, rejection checks and host-wait's refusal above 50% make the planned runs meaningful (task:30,47-58; playwright.config.ts:11-23).

Row 0 is sufficient for the preceding sessions' moved tree: it pins current content, re-finds citations, re-reads launch/close/error contracts and requires copied helpers to use that form (plan:274-285,316-335; task:44). Scratch profiles and recorded process identities protect other sessions. New actions require no external network, selected existing suites use their local seams, and the clipboard specs are excluded. No new defect demonstrated. Live geometry, chunk timing, repeats, offline behavior and cleanup are still execution evidence to obtain.

## Checklist Results

Source procedures below were performed by `codex-independent-reviewer`; their exit is null. The probe ran with PYTHONDONTWRITEBYTECODE=1 and wrote only under C:/Temp/av-kit.

| Check | Result | Procedure / command | Exit | Evidence |
|---|---|---|---|---|
| PR-1 / PR-3 Plan and task | pass | Read both complete documents; compare ACs, dependencies, creation assignments and validation cells | null | Same ordered three-fix scope; row 0 creates future checkers; row 3a uses the corrected independent assertions. |
| PR-2 Not started | pass | Target-folder/task/handoff inventory in us-r2-probe.py | 0 | Two documents, 29 unchecked task rows, three implementation handoffs absent. |
| PR-4 / PR-8 Corrected observables | pass | `rtk proxy python C:/Temp/av-kit/ui-small-fixes/review/us-r2-probe.py` | 0 | 12 valid mode/case records accepted; 90 corruptions rejected; revised stderr-only/selftest requirements confirmed in plan and task. |
| PR-5 / PR-7 Source and scope | pass | Compare issue entries, Session 94 grouping, build-plan homes, HDP §§4a–6 and expert receipt | null | Three requested fixes retained; D-1176/D-1177 recommendations adopted; no unauthorized product fork demonstrated. |
| PR-6 Correction substance | pass | Recheck both original findings across changed ACs, task rows, named contracts and gate | null | R1-F1 and R1-F2 corrected throughout their delivery surfaces. Paperwork excluded per the review request. |
| PR-9 Named definitions | pass | Compare named contracts and repeated mode/stream references | null | No materially competing live definition found. |
| Q2 / Q3 / Q5 compatibility | pass | Trace actual help/browse entrypoints, route map, pins and Session 90 ownership/cleanup code | null | Proposed changes preserve the specified existing behavior. |
| Product suites, Electron and future preview-proof selftest | n/a | Not run under this read-only review's restrictions | null | No runtime execution-pass claim. |

Final artifact check: the saved verdict validated against review-verdict.schema.v2.json (exit 0); the reviewed plan/task/Downloader hashes still match the evidence below. A separate Session 74 review artifact appeared concurrently and was left alone.

### Decisive evidence

```json
{"schema_version":"evidence.v1","check_id":"us-plan-r2-recheck","command":"rtk proxy python C:/Temp/av-kit/ui-small-fixes/review/us-r2-probe.py","cwd":"P:/av-kit","scope":"Extracted task-row-3 pure predicates on synthetic case records, source DOM inventory, revised stream-proof requirements and readiness; no app launched","phase":"plan-review","exit_code":0,"result":"pass","tested_state":"implementation-plan sha256 ecfd0ac6afee6835044415bd84b27089b08994b31cf08cc1fb03afe44fbfa5d2; task sha256 07a356d2d2cbc0c57ad74f2d1ec6b2c8c9c2ecf705c0ef3cfed13d20feaf8e94; DownloaderPage sha256 a636ea54d8a7dc2cb6e8e691b1a4cda5d1f63bd0447e7d400baadd7fadfd1127","output":"none/browser/file expanded visible counts 5/7/6; 12 valid case records accepted; 90 single-case corruptions rejected. Both hidden placeholders and DOM order match source. Plan/task require stderr-only notice search and run()/simulate() fake-Popen stream adversaries. Two plan documents, 29 unchecked rows, three implementation handoffs absent. Future preview-proof.py not executed.","fresh":true}
```

The report retains the original two findings above with their original assessments and historical citations; their status is now fixed. Round 1's source contradictions were real at that revision, and are not current defects.

## Recheck (round 2)

**Date:** 2026-11-18. **Workflow:** `/plan-critical-review`. **Agent:** `codex-independent-reviewer`.

### Prior Pass Summary

| Finding | Prior Status | Recheck Result |
|---|---|---|
| R1-F1 | open | fixed |
| R1-F2 | open | fixed |

### Confirmed Fixes

- **R1-F1:** corrected empty-status and separate DOM-order/mode-visibility predicates at implementation-plan.md:36-37,204-207,358-372,410,509 and task.md:51-52. Mode sets agree with source; actual row-3 predicate accepts each valid mode and rejects the exercised counterexamples. Form/disclosure/panel lookups resolve existing elements, without new IDs.
- **R1-F2:** independent stderr log and fake-Popen adversaries at implementation-plan.md:214,330-333,390 and task.md:44,55-56,63. The separate files feed the real run() notice oracle; stdout alone cannot satisfy AC-4. Existing ownership/cleanup safeguards remain required.

### New Findings

| # | Severity | Blocking | Kind | Finding | File:Line | Recommendation | Status |
|---|---|---|---|---|---|---|---|

No new evidence-backed High or Critical defect found. No open findings remain.

## Verdict

**approved** — both prior findings are fixed in the revised plan. The intended fixes and automated proof now form a coherent executable plan. No outstanding rejection under Q1–Q6.

Report: C:/Temp/av-kit/us-plan-review-round-2.md. The coordinator owns the canonical copy and ledger recording. Repository files were not edited; no product suite, Electron launch, npm/uv command or network request was run. Actual Red/Green results, measured boxes, separate-stream selftest results and live preview windows remain execution obligations.
