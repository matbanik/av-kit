---
date: "2026-11-10"
review_mode: "plan"
target_plan: "docs/execution/plans/2026-11-10-gui-capture-image-import/implementation-plan.md"
verdict: "approved"
findings_count: 0
template_version: "2.2"
requested_verbosity: "standard"
agent: "codex-independent-reviewer"
loop_id: "s61-plan-canonical-2026-11-10-gui-capture-image-import"
round: 3
---

# Critical Review: 2026-11-10-gui-capture-image-import

> **Review Mode:** plan. **Verdict:** changes_required. **Intent achieved:** partial.

## Intent Anchor

Session 61 lets a person bring images into the Capture inbox three ways. Image files dropped on the Capture page are imported one by one through the import endpoint. An **Import image…** button with the lucide `ImagePlus` icon opens a file dialog in main, filtered to png, jpg, jpeg and webp, with multi-select, and imports each file the same way. Ctrl+V with an image on the clipboard has main write it to the inbox as `{yyyy-MM-dd_HH-mm-ss}.png` and register it as `gui` through the hotkey's publication path, while text fields keep their native paste. One toast reports each run, and a file that isn't an image is named in it with a fixed reason.

## Scope

Reviewed the working-tree plan/task, all nine plan-local executables, the cited renderer/main/server boundaries, affected test pins and harnesses, design §7.2, 09's import/publication contracts, grouping and MEU-132 by id. HEAD independently reads `55d1289`; implementation rows 0–7 remain unchecked. Claude/Anthropic authored the plan; this report is independent Codex review.

Applied PR-1 through PR-9 and the Materiality Gate. Sessions 58–60 and their decisions are accepted dependencies. The named unrelated proposal, credentials/configuration secrets and fleet hub were not opened. Repository files were not edited. No product suite, application, network request or live clipboard operation was run. All reviewer writes are under `C:/Temp/av-kit`.

## Findings

Both findings have **High confidence**. Neither is a control-defeat finding.

| # | Severity | Blocking | Kind | Finding | File:Line | Recommendation | Status |
|---|---|---|---|---|---|---|---|
| F1 | High | yes | behavior | `IMPORT_RUN` treats every `ApiError.message` as a trusted server refusal. However, `apiFetch` also wraps a thrown fetch error as `ApiError(503, 'FETCH_FAILED', originalMessage)`, and backend-resolution errors are wrapped similarly. A thrown `Error('EACCES C:/private/red.png')` therefore becomes that exact toast reason, instead of `the import could not be completed`. Even an ordinary fetch rejection misses the promised generic message. This violates AC-132.4 and AC-132.15's error/fallback and path-free contracts; testing only a direct fake `importOne` rejection misses the real wrapper. | `docs/execution/plans/2026-11-10-gui-capture-image-import/implementation-plan.md:121`; `ui/src/renderer/src/lib/api.ts:52`; `ui/src/renderer/src/lib/api.ts:75` | Distinguish allowed server refusal messages from transport/backend-readiness errors. Give unrecognized errors the fixed fallback. Add a page-level fetch rejection containing a path through the real `importCapture`/`apiFetch` chain, alongside the legitimate 422 message case. | fixed |
| F2 | High | yes | behavior | `PASTE_IPC` passes main's cached `captureInboxDir` directly to the new writer, but main initializes it to `~/Pictures/av-kit` and only adopts the configured inbox asynchronously. `IMPORT_GATE` has no settings-readiness condition. If Ctrl+V arrives before a successful settings poll, or the backend is still unavailable, `PASTE_MAIN` creates/writes the PNG in that default folder and only then attempts registration. In D-561 A this can write outside the seeded look root into `<HOME>/Pictures/av-kit`; in normal use it can save outside the person's configured inbox. The process recorder waits for process roles, not settings adoption. This violates AC-132.6's inbox-save contract and the isolated paste proof behind AC-132.23. This finding concerns the new paste writer, without reopening the existing hotkey implementation. | `docs/execution/plans/2026-11-10-gui-capture-image-import/implementation-plan.md:127`; `implementation-plan.md:128`; `ui/src/main/index.ts:226`; `ui/src/main/index.ts:590`; `ui/src/main/capture-runtime.ts:10`; `docs/execution/plans/2026-11-10-gui-capture-image-import/dev-app-procs.py:193` | Make the paste dependency obtain/confirm the configured inbox before writing, or refuse safely until main has loaded it. Add a delayed/unavailable-settings case proving no default-folder creation/write, then a successful save into a distinct configured inbox. Make the Electron/look readiness procedure confirm the main-side inbox as well. | fixed |

## Q1 — Goal and the three runs

The ordinary journeys are covered. A drop maps Explorer files through `getPathForFile`, filters `notes.txt`, awaits the red and green import POSTs, calls the existing `CaptureImportIn` route/service, reconciles once explicitly and renders the one summary. AC-132.3/.14/.15/.19/.22 cover that run and retained marks. The button uses the existing main dialog's filters/multi-select, then the same runner (AC-132.13). Paste flows through the page listener, new no-payload IPC, exclusive stage, pixel guard, timestamp claim, settle and `finalizeCapturedPng(..., 'gui', ...)`, then its toast (AC-132.6–.12/.16/.17/.23).

Every sentence of the goal and 09's GUI import rows has a row and AC. F1 breaks the stated error contract. F2 means the paste is not reliably saved to the configured inbox, despite the normal-path coverage.

## Q2 — Types and display names

Accepted D-558. The server checks the input path's suffix against `('.png', '.jpg', '.jpeg', '.webp')`; the renderer's described rule agrees. The read-only source probe checked twelve names, including `.png` false, `a.` false, `a.png.txt` false and `A.PNG` true, with no mismatch. This is suffix compatibility, not a promise that corrupt image contents pass the server.

`IMPORT_NAME` takes the last component across both separator styles, so Windows drive, UNC and forward-slash paths lose their directory portion. Empty/trailing-separator input becomes `(unnamed file)`; controls and lone surrogates are replaced without destroying valid surrogate pairs. Using that helper for both dialog paths and drop names is sound.

## Q3 — Sequential runs, toasts and errors

Accepted the awaited loop, continuation after an individual failure, and one explicit reconciliation after any attempted server call, even if all calls fail. All rejected extensions cause no request/refetch. The formula gives `Imported 0 of N. N failed: ...`, `Imported 0 of 1. 1 failed: ...` and `Imported 1 of 1.` correctly. A cancelled dialog produces no run/toast. Existing catalog polling/watch invalidations remain separate from that explicit reconciliation.

`BulkResult` contains arrays, not a unique-name map; repeated basenames can remain repeated entries and contribute separate counts/reasons. `BulkResultToast` renders `message` and does not deduplicate them. It fits the dismissible, single-run summary. Accepted fixed MEU-129 refusals, but not the claim that all `ApiError` text is server text: F1.

## Q4 — Drop routing and navigation

Accepted D-551 and P2 as supplied evidence. Preload calls `webUtils.getPathForFile` inside the real isolated bridge; P2 records actual paths both directly and inside the drop, with an empty path for a synthetic `File`. Preventing default on file `dragover` and `drop`, including gated drops, is the right cancellation for navigation within the section. A file drop on its viewport, filmstrip or input bubbles there. Targeted child-handler inspection found pointer/key propagation stops, not a competing drop handler that consumes these drops. Text-only drags remain native.

## Q5 — Paste events and editable targets

Accepted D-550. P1 records one native paste event for body, pointer-focused button, Tab-focused button and input. It supports event delivery in this app/menu configuration without taking reserved Ctrl+V from the registry. P1 does not separately record an Enter activation; AC-132.16 and the new Electron AC-132.23 explicitly add that focus sequence.

The editable predicate covers the inbox text field, default-type text-mark editor, textarea, inherited contenteditable state and crop X/Y/W/H inputs (which have `inputMode="numeric"` with default text type). Explicit number inputs are also covered. Checkbox/non-text controls remain false. The editable check runs before the modal gate, preserving native field paste even during crop. Unmount cleanup is specified.

## Q6 — Publication, staging and logs

The shared publisher/wrapper design is viable: preserving the wrapper's true notification/path-log flags and clipboard option preserves picker/hotkey behavior; existing picker/lifecycle/interactive guards cover publication, collisions, registration failure, notifications and watcher suppression. They are regression evidence, not a proof that every log byte is pinned. Reusing the staged image's `inspectNativeImagePixels` preserves empty/black refusal. Exclusive `wx` creation with a fresh collision name preserves another writer's staging file; a finally-held paste flag can span the whole asynchronous publication/register run.

Implementation must apply `PASTE_LOG` and error mapping transitively: `claimInboxName` currently logs full paths (`capture-picker.ts:446,450`), `removeStaging` swallows unlink failures (`:175`), and `finalizeCapturedPng` has its own log sink (`capture-register.ts:186`). Merely editing log statements in the extracted body is insufficient. The plan already assigns the path-free/error-mapping outcome and AC-132.10/.11; verify real helper/sink behavior rather than mocking it away. F2 is the separate, concrete missing prerequisite before staging starts.

## Q7 — IPC, pins and action audit

Accepted the four moved 21→22 count pins, the shared channel list, strict census entries and unchanged users such as `web-prefs-ipc`. The targeted full unit-source sweep found no additional count/last-key pin requiring a move. Row 1's dep-present handler intentionally returning `failed` gives AC-132.12 an assertion Red when the fake dep returns a different outcome. Main already unwraps successful IPC `value` before preload returns it (`index.ts:452–457`).

The one-line preload requirement is real: `preloadChannelFor` matches `key: ...ipcRenderer.invoke('channel')` on one line, and the exact `IPC pasteCaptureImage` cell resolves to the new channel. The separate MEU-132 audit avoids changing unrelated AC-23 inputs.

## Q8 — Modal gates and selection

Accepted crop/confirm/running gates and current refs for the once-mounted paste listener. All three entries are governed by the gate; the button is disabled and file drops still cancel navigation. The unsaved-mark exception is sound for an additive import: selection is an id, not a filmstrip index. The range effect removes only missing ids. Detail/mark reset depends on `selectedId`/`detailRevision` (`CapturePage.tsx:602`), so inserting a newer image cannot reset unsaved marks. The image-fetch effect also depends on the selected item's `updated_at` (`:524`), but a normal additive import does not update that existing shot. Notice identity remains stable. F2 adds a main-side readiness concern beyond these renderer modal refs.

## Q9 — Electron proof and D-560

Accepted the hidden-input/DataTransfer route: P2 already demonstrates the retained real disk paths, and AC-132.22 asserts their exact ordered POST bodies. This proves real Electron file-path/drop plumbing against the specified stub backend; MEU-129's accepted real-stack tests own actual copying/validation.

D-560 A saves/restores Electron's supported text/HTML/RTF/image projections and compares them plus format availability. It is not a byte-for-byte Windows clipboard snapshot. The brief explicitly discloses custom/file-list formats and Win+V history loss; S13 correctly stops on a failed restoration/format comparison rather than silently rerunning. B accurately leaves the actual `clipboard.readImage` read unproven by Electron; C deliberately leaves the test image. These remain Mat's choices. No clipboard operation was performed in this review.

Both planned Electron Reds assert toast visibility before body/file inspection. The parser distinguishes locator-expectation failure from action/test timeout and supports its nested `element(s) not found` detail. Its independent selftest passed. Readiness for the Green paste additionally needs F2's correction.

## Q10 — Look launch and process ownership

Accepted fresh-root refusal, seeded backend settings/data, detached launch with `AVKIT_APP_DATA`, and record/stop ownership by pid plus creation time. MCP server roles are excluded, foreign processes are only listed, and stop rechecks creation time. The independent process-classifier selftest passed. `look-check` requires a quoted human reference and a completed launch/cleanup under A; `no` deliberately passes the checker because row 6 then requires fixes. B requires `not-run` and no launch record. Its selftest passed all positive/negative fixtures.

The literal real-inbox isolation claim is not established by `AVKIT_APP_DATA` alone: main's initial capture runtime still names `<HOME>/Pictures/av-kit` and starts its watcher before the asynchronous settings adoption. F2 addresses the new paste writer's concrete ability to write there. The seeded database/Electron settings location and the process cleanup design otherwise remain accepted. Neither look script was executed.

## Q11 — Reds, endings, identity, scope and safety

The required sets are appropriate: .1–.12 for module/main; .13–.20/.22/.23 for page/Electron; .21 is a passing characterization guard. The needed runtime names are assigned before Reds. `PublishOutcome` is declared by the planned extraction; it need not be imported by a Red. For AC-132.10, a constant `failed` stub already has the expected outcome: the fault-injection test must also assert that its intended filesystem call was reached. The required-Red checker will refuse an accidentally passing test, so this is an implementation obligation rather than a demonstrated false pass.

Accepted existing CRLF/LF preservation and new LF files. All nine plan-local executable paths exist. Scope includes the listed changes, project prefix, shared status files and grouping. Identity binds source/tests/config/scripts, registers/grouping and runtime inputs while excluding the session's post-gate prose; its scratch-only selftest passed with zero failures. S14 shares the look ruling parser; supplied baseline probes show unruled exit 1 and queue/shapes/anchors exit 0. Source reads confirm actual id lookup and named producer checks; no material false pass was demonstrated there.

`hotkey-free --selftest` never opens the clipboard. Its live implementation opens/closes without EmptyClipboard/SetClipboardData, so successful probing does not replace contents/ownership; the live probe was not run. Test images/fetches are local fixtures, stubs or loopback services, with no proposed image upload. F2 is the concrete exception to the promised seeded-root write isolation. No new Python production, route, schema or MCP work is requested.

## Checklist Results

### Plan review

| Check | Result | Procedure / observer | Exit | Evidence |
|---|---|---|---|---|
| PR-1 plan/task alignment | pass | Read both artifacts and trace rows/ACs; codex-independent-reviewer | null | Both assign one MEU and the same type-only → module/main → page/Electron → look → closeout sequence. |
| PR-2 unstarted | pass | Source probe and target reads; codex-independent-reviewer | null | Rows 0–7 unchecked; MEU-132 pending; new product names absent in supplied shape receipt. |
| PR-3 task contract | pass | Read task table; codex-independent-reviewer | null | Owners, deliverables, dependencies, exact commands and status cells present. |
| PR-4 validation realism | fail | Trace production error and settings boundaries; codex-independent-reviewer | null | F1's wrapper changes error class; F2's cached main inbox is not readiness-bound by the planned cases. |
| PR-5 source-backed planning | pass | Read spec/design/grouping and decisions; codex-independent-reviewer | null | Scope matches MEU-132; autonomous choices and two human questions are identified. |
| PR-6 correction/handoff readiness | pass | Read H1/H2 and review routing; codex-independent-reviewer | null | Single handoff and rolling review targets; round-2 census not applicable yet. |
| PR-7 scope discipline | pass | Compare exclusions to 09/design/grouping; codex-independent-reviewer | null | No required entry point is silently deferred; named prior issues remain excluded as instructed. |
| PR-8 reachability/totality | fail | Trace imports and paste writer through current sources; codex-independent-reviewer | null | F1/F2 are concrete behavior failures; no control-defeat mechanism asserted. |
| PR-9 single-statement contracts | pass | Compare named contracts, ACs and task rows; codex-independent-reviewer | null | Named mechanisms govern the same intended behavior; no unresolved competing behavior set found. |
| DR / execution certification | n/a | Plan-only review | null | No completed implementation, suite pass or execution approval is claimed. |

### Commands and observed evidence

With `PYTHONDONTWRITEBYTECODE=1` and scratch temp paths set under `C:/Temp/av-kit`, ran the following independently. The script name in each command expands from PLAN = `docs/execution/plans/2026-11-10-gui-capture-image-import`.

| Command | Exit | Decisive output |
|---|---|---|
| `rtk proxy git rev-parse --short HEAD` | 0 | `55d1289` |
| `rtk proxy .venv/Scripts/python.exe C:/Temp/av-kit/s61-review-source-probe.py` | 0 | Twelve suffix comparisons agree; eight unstarted rows; nine executables exist; static Error→ApiError→toast counterexample confirmed. |
| `rtk proxy .venv/Scripts/python.exe PLAN/red-check.py --selftest` | 0 | `41 fixture(s) (12 positive, 29 negative), 0 wrong: []` |
| `rtk proxy .venv/Scripts/python.exe PLAN/identity.py --selftest` | 0 | `identity selftest: 0 failure(s)` |
| `rtk proxy .venv/Scripts/python.exe PLAN/dev-app-procs.py --selftest` | 0 | `dev-app-procs selftest: 0 failure(s)` |
| `rtk proxy .venv/Scripts/python.exe PLAN/hotkey-free.py --selftest` | 0 | `hotkey-free selftest: 0 wrong` |
| `rtk proxy .venv/Scripts/python.exe PLAN/look-check.py --selftest` | 0 | `look-check selftest: 0 wrong` |

The completed report was parsed with `tools/validate_closeout_artifacts.py --review C:/Temp/av-kit/s61-plan-review-round-1.md --review-state-only --expected-review-mode plan --expected-target-plan docs/execution/plans/2026-11-10-gui-capture-image-import/implementation-plan.md --max-review-rounds 3 --output C:/Temp/av-kit/s61-review-state-r1.json`: exit 0, `round 1 of 3; verdict=changes_required; open findings=2`. The saved JSON verdict was independently validated against `.agent/schemas/review-verdict.schema.v2.json` using `jsonschema.Draft202012Validator`: exit 0, `review-verdict.v2 schema: PASS; findings: 2`.

```json
{"schema_version":"evidence.v1","check_id":"s61-plan-source-traces","procedure":"Read IMPORT_RUN/PASTE_IPC/PASTE_MAIN and follow apiFetch error construction plus main capture runtime initialization/adoption in the current working tree; compare the specified counterexamples to AC-132.4/.6/.15/.23.","observer":"codex-independent-reviewer","cwd":"P:/av-kit","scope":"Session 61 plan and cited production boundaries","phase":"plan-review","exit_code":null,"result":"fail","tested_state":"55d1289-working-tree-targeted-source-review","output":"apiFetch wraps the original fetch message as FETCH_FAILED ApiError; IMPORT_RUN exposes every ApiError.message. Main initializes captureInboxDir from ~/Pictures/av-kit before asynchronous refreshCaptureRuntime; the planned paste writes with that cached value without a readiness condition.","fresh":true}
```

```json
{"schema_version":"evidence.v1","check_id":"s61-plan-red-parser-selftest","command":"rtk proxy .venv/Scripts/python.exe docs/execution/plans/2026-11-10-gui-capture-image-import/red-check.py --selftest","cwd":"P:/av-kit","scope":"plan-local parser fixture selftest only","phase":"plan-review","exit_code":0,"result":"pass","tested_state":"55d1289-working-tree-targeted-source-review","output":"red-check selftest: 41 fixture(s) (12 positive, 29 negative), 0 wrong: []","fresh":true}
```

## Verdict

`changes_required` — correct F1's error provenance handling and F2's configured-inbox readiness before execution. The three-entry design and remaining autonomous decisions are otherwise accepted. D-560 and D-561 remain open for Mat; this review does not choose either.

Route corrections through `/plan-corrections`, then request the complete rolling round-2 report. No implementation fix was made by this reviewer. Runtime behavior and clipboard restoration remain future execution evidence, not fresh reviewer passes.

## Corrections Applied (2026-11-10)

Written by the plan's author acting as the corrections agent (`claude-opus-claude-code-coordinator`), not by a reviewer, for round 1 of loop `s61-plan-canonical-2026-11-10-gui-capture-image-import`. The frontmatter verdict is now `corrections_applied`. Only the round-2 independent recheck can approve.

### Findings verified

2 confirmed, 0 refuted.

| # | Evidence | Result |
|---|---|---|
| F1 | `ui/src/renderer/src/lib/api.ts:52`, `:75`; `packages/api/src/avkit_api/errors.py:33`, `:121-160`; `packages/core/src/avkit_core/services/capture.py:504-543` | Confirmed. `apiFetch` re-throws a thrown fetch as `ApiError(503, 'FETCH_FAILED', <thrown text>)` and backend resolution as `BACKEND_NOT_READY` with the thrown text appended. MEU-129's refusals reach the renderer as 422 with envelope code `InboxPathError` and fixed, path-free text (D-416). Validation errors are `validation_error` with a fixed text, and mapped 5xx errors are `internal_error`. |
| F2 | `ui/src/main/index.ts:226-228`, `:559-592`; `ui/src/main/capture-runtime.ts:10`, `:64-82` | Confirmed. `captureInboxDir` starts as `~/Pictures/av-kit` and is replaced only when `fetchCaptureRuntime()` answers non-null. That needs a published backend-ready and a successful `GET /settings/capture`, polled every second. |

### Changes made

- **F1**, in `implementation-plan.md`:
  - `IMPORT_RUN`: only an `ApiError` with status 422 and code `InboxPathError` shows its own message. Every other error gets `the import could not be completed`: `FETCH_FAILED`, `BACKEND_NOT_READY`, an envelope-less `HTTP_ERROR`, `validation_error`, `http_error`, any 5xx and any non-`ApiError` throw.
  - AC-132.4 lists each of those error shapes, with a path in the thrown text where one can occur.
  - AC-132.15 drives a rejected `fetch` holding a path through the real `importCapture` and `apiFetch`, and keeps the 422 `InboxPathError` envelope case.
  - D-553's reasoning records why.
- **F2**, in `implementation-plan.md`:
  - `PASTE_IPC`: the `index.ts` dep keeps a `captureRuntimeAdopted` flag, set on the first non-null `fetchCaptureRuntime()`. Its `resolveInboxDir` runs `refreshCaptureRuntime()` once while the flag is false, then answers the configured inbox, or `null`. The hotkey, picker and tray are unchanged.
  - `PASTE_MAIN` takes `resolveInboxDir` in place of `inboxDir`. A `null` answer or a rejection gives the new outcome `{kind: 'not-ready'}`, before the clipboard read and before any filesystem call.
  - `PASTE_LOG` adds `paste not ready`. `PASTE_MESSAGES` adds `The inbox isn't ready yet, so nothing was saved. Try again in a moment.` The Boundary Inventory row now reads six kinds.
  - AC-132.6 saves into a configured temp inbox and checks that a stand-in default path is still absent. AC-132.7 adds the `null` and rejecting `resolveInboxDir` cases. AC-132.23 asserts the pasted file is in the stub's `/settings/capture` `inbox_dir`.
  - `LOOK_LAUNCH` states that a paste before adoption writes nothing. D-556's reasoning records why.
- **Q6 note** (helper logs, same path-free category), in `implementation-plan.md`:
  - `PASTE_LOG` now reaches `claimInboxName` and `finalizeCapturedPng` through trailing defaulted parameters, `logPaths = true` and `logFailure = true`, so every existing caller's lines stay byte for byte.
  - AC-132.11 records the log from the real helpers. It asserts `could not claim a name (EACCES)` with no path, and no `register failed:` line on a paste.
- **Q11 note**: AC-132.10 asserts each injected filesystem call was reached. Its Red cell now says the row 1 stub answers `failed` without reaching it, which replaces the inaccurate "the stub rejects".
- `task.md`: row 1's caller grep adds `claimInboxName`. Row 3 names `resolveInboxDir`, `not-ready`, the two defaulted helper parameters and `captureRuntimeAdopted`.

### Verification

- Blast-radius census, `C:/Temp/av-kit/s61-plan-census-r1.txt`: 7 values changed, 16 variants swept across both plan files. Every hit is updated or consistent:
  - `five kinds` is gone.
  - `captureInboxDir` appears only in `PASTE_IPC`'s description of main.
  - `kind: 'failed'` at task.md:36 and :61 and plan :326 describes the row 1 stub, which still answers `failed`, so each Red still fails on its value.
- Line endings: `implementation-plan.md` and `task.md` hold 0 CRLF.
- Decision probe, `C:/Temp/av-kit/s61-plan-decision-probe-c1.txt`: exit 0, 23 decisions. No `{…}` slot entered the decision log.
- Task lint, `C:/Temp/av-kit/s61-plan-task-lint-c1.txt`: exit 0, 25 rows, 23 fully checked.
- Round-1 review: validated under C:/Temp/av-kit and copied byte for byte (SHA-256 `f0b3ccd1…1fbc` on both). State receipt: `C:/Temp/av-kit/s61-plan-review-state-r1.json`.


## Recheck (Round 2)

**Date:** 2026-11-10. **Agent:** codex-independent-reviewer. **Verdict:** changes_required. **Intent achieved:** partial.

This section is the current assessment. The original Findings prose, Q1 to Q11, round-1 evidence and verdict remain historical; only F1's status cell has changed. The author's Corrections Applied section above is preserved verbatim. Claude/Anthropic authored both the plan and corrections. No repository file was edited by this reviewer.

### Recheck Result

| Finding | Recheck result | Evidence |
|---|---|---|
| F1 | fixed | `implementation-plan.md:121,204,215,443`: IMPORT_RUN now admits only 422/InboxPathError text, and AC-132.15 rejects fetch through the real importCapture/apiFetch chain. `api.ts:40-95` and `errors.py:28-43,106-160` confirm the distinction. |
| F2 | partial | `implementation-plan.md:127-128,206-207,223`: startup/no-first-settings writes are prevented. However, PASTE_IPC refreshes only while captureRuntimeAdopted is false. After adoption of A and a successful settings save to B, a paste before the next successful poll still writes A. `useCaptureSettings.ts:88-96` saves only through the API/query cache; `index.ts:559-592` updates main on its separate poll. Registration then refuses the A path against B (`capture.py:494-499,1214-1234`). AC-132.6/.7 inject the resolver and .23 uses a stable inbox, so they do not exercise this sequence. F2 remains High, blocking, behavior, deliverable, violates AC-132 (specifically AC-132.6/.23 and PASTE_MAIN's configured-inbox promise). |

**Required correction for F2:** bind the new paste resolver to the current configured inbox for that invocation, rather than treating a first successful adoption as permanent freshness. A paste-specific settings read can fail closed without changing the hotkey, picker or tray. If sharing refresh machinery, preserve the existing runtime equality/hook behavior and prevent an older in-flight poll from determining the paste's destination. Add an assertion test of the real resolver wiring: adopt A, successfully save distinct B, withhold the scheduled poll, then paste; only B may receive the PNG and gui registration, or the call must answer not-ready before clipboard/filesystem access. Also exercise a failed refresh after the change. This carries F2 forward rather than introducing a new finding for the same configured-inbox defect.

### New Findings

| # | Severity | Blocking | Kind | Finding | File:Line | Recommendation | Status |
|---|---|---|---|---|---|---|---|
| None | — | — | — | None | — | — | — |

### R1 — Error provenance and Reds

F1 is fixed in the plan. The API maps InboxPathError to 422 and emits the exception's class name as the envelope code. MEU-129's fixed import refusals use that class, including the size message (`capture.py:535-539`); the numeric MB substitution adds no path. No legitimate MEU-129 file refusal identified in the reviewed source loses its text under this predicate. FETCH_FAILED, BACKEND_NOT_READY, raw HTTP_ERROR, validation_error, http_error, all 5xx and non-ApiError exceptions fall back. A failed response read or JSON parse also falls into the non-ApiError fallback. This conclusion assumes the accepted local API contract; it does not require adding a second catalog of server messages to the renderer.

AC-132.4 pins the permitted envelope and representative rejected shapes; AC-132.15 importantly runs the fetch rejection through the real wrappers. Both can fail by assertion on their respective planned Red trees: row 1's importFiles returns an empty result instead of the required error summary; the unwired page produces no toast. These are plan/test-design observations, not executed product tests.

### R2 — Inbox readiness, polling and proof

Startup is corrected: before adoption, a null settings result or a rejection maps to not-ready before reading the clipboard or touching the filesystem. A successful adoption can use the configured inbox even when it equals the defaults; set the flag on that non-null path as well as the changed-runtime path. A backend failure after adoption, without a settings change, can safely keep the last configured folder and produce the already-specified saved-but-unregistered result.

The settings-change case is still wrong: a successful PUT changes the server's inbox immediately, but the true flag makes the resolver skip refresh and return the previous cached folder. A normal sub-second paste after Save can publish outside the current inbox; the real server rejects registration with `path is outside the capture inbox`, leaving a PNG where the person no longer expects captures. Failed subsequent polls prolong the stale destination. This concerns only the new paste path; the hotkey's existing cache use remains out of scope.

Calling refresh beside the poll does not inherently apply identical settings twice: JavaScript continuations compare against the then-current captureRuntime, and the equality branch avoids hooks; applyCaptureRuntime also changes the watcher only when inbox_dir differs (`capture-runtime.ts:39-62`). If responses contain different settings, completion order can still roll the cache back; a first-adoption flag is not an ordering or freshness guarantee. No separate finding is counted for that variant.

AC-132.6/.7 now specify meaningful saved/not-ready outcomes and preserve assertion Reds. They test a supplied resolver, not index.ts's actual adoption/cache logic. The existing Electron stub really returns its mutable inbox via /settings/capture (`capture-picker.test.ts:80-88`), so AC-132.23's configured-root assertion is meaningful and would catch the original default-root leak in that run. Its unchanged-inbox run does not prove the save-B-before-poll case. F2 is therefore partial, not closed.

### R3 — Helper logs and fault reachability

The trailing defaults in PASTE_LOG (`implementation-plan.md:130`) preserve existing caller semantics by design: logPaths=true must retain both exact original claim log templates; logFailure=true must retain finalizeCapturedPng's original register-failure line before its callback. The paste explicitly supplies false and records its own path-free failure. Source inspection found these are the relevant helper sinks (`capture-picker.ts:432-453`; `capture-register.ts:174-190`).

The named unchanged guards support publication, notifications, failures and path-bearing legacy logs, but they do not assert every log byte. For example, `capture-lifecycle.test.ts:471-499` checks that a log includes dest, rather than equaling the complete original line; `capture-main.behavior.test.ts:60-100` exercises settings application, not log snapshots. Byte-for-byte retention remains an implementation/diff obligation already stated by the plan, not something those tests alone certify. AC-132.11 now records the real helper logs for the new paste, which addresses the transitive-sink concern.

AC-132.10's added reached-call assertions fix Q11's vacuous failure-outcome case: row 1 can return failed but cannot satisfy the injected filesystem call assertion. The mkdir/path-is-a-file case also needs an observed filesystem call, as the AC's each-case wording requires. Passing requires reaching fault handling and checking the result and cleanup. No product Red/Green was run in this review.

### R4 — Regression, scope and identity

No separate new finding was established. The six outcome kinds, not-ready text, task row 3 and D-556 agree; IMPORT_RUN, AC-132.4/.15 and D-553 agree. Q6/Q11 corrections are technically sound within the limits above. The outstanding issue is the existing F2 configured-inbox requirement, now only partly met.

The target source diff was empty at HEAD 55d1289. Both corrected plan documents have zero CRLF sequences; no tracked CRLF source conversion appears in the reviewed diff. All nine plan-local executables exist. The identity/parser selftests pass; those are checks of plan tooling, not product certification. Existing scope/identity exclusions, D-550 to D-565 and D-560/D-561's human choices remain as supplied. No Python production, route, schema or MCP change is requested. No network, live clipboard, product suite, app, baseline or look launcher was used.

### Round-2 observed checks

All Python commands used PYTHONDONTWRITEBYTECODE=1 and scratch temp directories. PLAN below is `docs/execution/plans/2026-11-10-gui-capture-image-import`.

| Command / procedure | Exit | Observed result |
|---|---|---|
| `rtk proxy git rev-parse --short HEAD` | 0 | 55d1289 |
| `rtk proxy git diff --numstat --` followed by the explicitly reviewed source/plan/review paths (exact argv in s61-r2-target-diff receipt command) | 0 | Empty tracked diff for those paths; untracked plan content read directly. |
| `rtk proxy .venv/Scripts/python.exe C:/Temp/av-kit/s61-r2-source-probe.py` | 0 | Source-bound symbolic replay: adopted A; saved B; resolve=A; current=B; refresh calls during paste=0. Source-extracted real registration guard rejects A against B. No file was published. Both plan documents CRLF=0; nine executables exist. |
| `rtk proxy .venv/Scripts/python.exe PLAN/red-check.py --selftest` | 0 | 41 fixtures, 12 positive and 29 negative, 0 wrong. |
| `rtk proxy .venv/Scripts/python.exe PLAN/identity.py --selftest` | 0 | 0 failures. |
| `rtk proxy .venv/Scripts/python.exe PLAN/dev-app-procs.py --selftest` | 0 | 0 failures. |
| `rtk proxy .venv/Scripts/python.exe PLAN/hotkey-free.py --selftest` | 0 | 0 wrong; fixtures only, no key registration or clipboard access. |
| `rtk proxy .venv/Scripts/python.exe PLAN/look-check.py --selftest` | 0 | 0 wrong. |

```json
{"schema_version":"evidence.v1","check_id":"s61-r2-inbox-recheck","procedure":"Trace the proposed PASTE_IPC flag/conditional refresh against main refreshCaptureRuntime, the actual Capture settings save hook, and CaptureService register_shot/_inbox/_require_inbox_file. Replay adoption A, successful save B and paste before the next poll; compare AC-132.6/.7/.23 coverage.","observer":"codex-independent-reviewer","cwd":"P:/av-kit","scope":"Session 61 configured-inbox paste contract","phase":"plan-review","exit_code":null,"result":"fail","tested_state":"55d1289; plan sha256 87309f75c1b7aa57973e34e8d77c7daebd77c5deb98cbe6bfbbe929f882f3b93; task sha256 c9a7f78a1ab7952468d9cbc563ee2213753c6550a33ea26badb9b1d870fda271; targeted tracked diff empty","output":"First-adoption gate fixes startup. After A is adopted and B is saved, true captureRuntimeAdopted skips refresh and resolves A; the API reads B and refuses registration of the outside-inbox A file. Planned cases supply a fake resolver or keep a stable E2E inbox.","fresh":true}
```

```json
{"schema_version":"evidence.v1","check_id":"s61-r2-source-probe","command":"rtk proxy .venv/Scripts/python.exe C:/Temp/av-kit/s61-r2-source-probe.py","cwd":"P:/av-kit","scope":"read-only symbolic plan replay, source-extracted registration guard and file-byte inventory","phase":"plan-review","exit_code":0,"result":"pass","tested_state":"55d1289; plan sha256 87309f75c1b7aa57973e34e8d77c7daebd77c5deb98cbe6bfbbe929f882f3b93; task sha256 c9a7f78a1ab7952468d9cbc563ee2213753c6550a33ea26badb9b1d870fda271","output":"F2 symbolic replay: adopted A; saved B; resolve=A; current=B; refresh calls during paste=0. Actual source-extracted registration guard: path is outside the capture inbox. Both plan documents CRLF=0. Nine plan-local executable paths exist. No product runtime or publication was performed.","fresh":true}
```

### Verdict

`changes_required` — F1 is fixed; F2 remains High and blocking until the new paste confirms the current inbox after a settings change. No new finding ids. D-560 and D-561 remain Mat's decisions. The full rolling report is saved at `C:/Temp/av-kit/s61-plan-review-round-2.md`; the coordinator owns copying it to the canonical path after validation.

Report validation: `rtk proxy .venv/Scripts/python.exe tools/validate_closeout_artifacts.py --review C:/Temp/av-kit/s61-plan-review-round-2.md --review-state-only --expected-review-mode plan --expected-target-plan docs/execution/plans/2026-11-10-gui-capture-image-import/implementation-plan.md --max-review-rounds 6 --output C:/Temp/av-kit/s61-review-state-r2.json` exited 0: `round 2 of 6; verdict=changes_required; open findings=1`. The six-round allowance is the supplied Mat continuation receipt; no new ledger was opened. The saved JSON verdict validated against the current repository v2 schema with `jsonschema.Draft202012Validator`, exit 0: `schema errors: 0`.

## Corrections Applied (Round 2, 2026-11-10)

Written by the plan's author, acting as the corrections agent (`claude-opus-claude-code-coordinator`), not by a reviewer. This covers round 2 of loop `s61-plan-canonical-2026-11-10-gui-capture-image-import`. The frontmatter verdict is now `corrections_applied`. Only the round-3 independent recheck can approve.

### Findings verified

1 confirmed (F2, partial), 0 refuted. F1 is fixed per the round-2 recheck and is unchanged.

| # | Evidence | Result |
|---|---|---|
| F2 | `ui/src/main/index.ts:559-592`, `ui/src/main/capture-runtime.ts:65-82`, `ui/tests/e2e/capture-picker.test.ts:41-47` | Confirmed. `refreshCaptureRuntime` is the only writer of `captureInboxDir`, on the 1-second poll. With the round-1 flag already true, a paste after a Save in Settings and before the next successful poll would resolve the old folder. `fetchCaptureRuntime` answers `null` when the backend isn't ready, on a non-ok status and on a thrown request (logging `settings poll failed`). The E2E stub has `setInbox`. |

### Changes made

- **F2, `PASTE_IPC`** (`implementation-plan.md`):
  - The adoption flag is gone. The `index.ts` dep passes `resolveInboxDir: () => resolvePasteInbox(fetchCaptureRuntime)`.
  - `resolvePasteInbox(readSettings)` in `capture-picker.ts` reads the settings once on every call. It answers that reply's `inbox_dir`, or `null` when the read answers `null` or rejects.
  - It never reads or writes `captureRuntime`, `captureInboxDir`, the runtime hooks or the watcher. So it can't race the poll, apply a runtime twice or roll the cache back.
  - `refreshCaptureRuntime`, the poll, the hotkey, the picker and the tray are unchanged.
- **AC-132.6:** the call runs through the real `resolvePasteInbox` over a fake settings read.
  - After a paste saved in A, the read switches to B with no other call between, as a Save in Settings does.
  - The second paste is saved in B, and its register body names the B file. A still holds exactly one PNG.
  - The read is called once per paste.
- **AC-132.7:** after the switch to B, a read that answers `null` and one that rejects each give `not-ready`, and nothing new appears in A or B.
- **AC-132.23:** before the second Electron paste, the stub's `setInbox` switches `inbox_dir` to a second folder under the test root. With no wait for main's poll, Ctrl+V saves into that folder, and its register body names the file. The first folder still holds one PNG.
- **`PASTE_LOG`:** a thrown settings read keeps `fetchCaptureRuntime`'s existing `settings poll failed: {message}` line (`capture-runtime.ts:80`). Its message comes from a request to the local API, not from a file.
- **`LOOK_LAUNCH`:** each paste reads the seeded inbox, and a failed read writes nothing.
- **D-556's reasoning:** records why a paste-only read replaces the first-adoption flag (rounds 1 and 2, F2).
- **`task.md`:**
  - Row 1 adds a `resolvePasteInbox` stub that answers `null` without calling its read.
  - Row 3 writes `resolvePasteInbox` and wires the dep, leaving `refreshCaptureRuntime` and the poll unchanged.

### Verification

- No `captureRuntimeAdopted` or "adopted" wording is left in either plan file.
- Line endings: `implementation-plan.md` and `task.md` hold 0 CRLF.
- Decision probe, `C:/Temp/av-kit/s61-plan-decision-probe-c2.txt`: exit 0.
- Task lint, `C:/Temp/av-kit/s61-plan-task-lint-c2.txt`: exit 0, 25 rows.
- Round-2 review: validated under C:/Temp/av-kit (`s61-plan-review-validate-r2.txt`) and copied byte for byte (SHA-256 `6c59bffb…150c` on both). State receipt: `C:/Temp/av-kit/s61-plan-review-state-r2.json`.

## Recheck (Round 3)

**Date:** 2026-11-10. **Agent:** codex-independent-reviewer. **Verdict:** approved. **Intent achieved:** yes (plan adequacy, not implemented product behavior).

This section is the current assessment. All earlier sections, including both author's Corrections Applied sections and the round-2 assessment, remain historical and unchanged, except F2's original finding status cell is now fixed. Claude/Anthropic authored the plan and corrections; Codex independently reviewed them. No repository file was edited.

### Prior Pass Summary

| Finding | Prior Status | Recheck Result | Evidence |
|---|---|---|---|
| F1 | fixed | fixed | `implementation-plan.md:121,204,215,443`: IMPORT_RUN still admits only 422/InboxPathError text; AC-132.4 covers rejected error shapes and AC-132.15 uses the real importCapture/apiFetch chain. The round-2 correction is retained. |
| F2 | partial | fixed | `implementation-plan.md:127-128,206-207,223,490`; `task.md:61,64`: PASTE_IPC now supplies resolvePasteInbox(fetchCaptureRuntime) for each paste, with no adoption flag or cached-inbox read. AC-132.6 switches A to B through the real resolver, .7 fails closed after the switch, and .23 exercises index/IPC wiring against the mutable Electron backend. |

### New Findings

| # | Severity | Blocking | Kind | Finding | File:Line | Recommendation | Status |
|---|---|---|---|---|---|---|---|
| None | — | — | — | None | — | — | — |

### R1 — Current inbox, failures, isolation and assertion Reds

**Yes, F2 is resolved.** PASTE_IPC binds the new writer to the inbox from that invocation's settings reply. It does not substitute the last poll result. PASTE_MAIN must acquire its pasteInFlight flag before awaiting the resolver and release it after the whole run, including failure/not-ready outcomes; this follows its explicit second-call-while-running contract (`implementation-plan.md:128,207`).

| Situation | Planned observable result and source |
|---|---|
| Startup before main adopts settings | A successful paste-specific read supplies its configured inbox even if main still holds the default. A null read gives not-ready before clipboard or filesystem access. No fallback to the default (`implementation-plan.md:127-128`). |
| Backend down/not yet ready | `fetchCaptureRuntime` returns null before readiness, for a non-ok response, or after catching a request/JSON error (`capture-runtime.ts:65-82`). The resolver returns null; nothing is read from the clipboard, created or written. This also holds after an earlier successful paste. |
| Save changes A to B immediately before paste | The next invocation reads again and uses B, without waiting for or applying main's poll. AC-132.6 asserts B's bytes and register body, one settings read per paste, and exactly one remaining PNG in A (`implementation-plan.md:206`). |
| Failed or throwing settings read | A null reply or rejection becomes not-ready. AC-132.7 repeats both after A/B and checks neither folder gains another file. The existing fetch helper catches failures and retains its settings-poll diagnostic; PASTE_LOG explicitly accounts for that line (`implementation-plan.md:130,207`). |
| Two close pastes | The active call retains the flag while awaiting registration; the second answers busy and writes nothing; a third runs after settlement (`implementation-plan.md:128,207`). Busy is not a new run and produces no toast (`:131`). |

**Main's runtime, hooks and watcher stay untouched by the paste read.** The existing fetch helper reads backend readiness and settings, parses a reply and optionally logs a failure; it does not apply runtime (`capture-runtime.ts:65-82`). The proposed resolver only awaits that read and returns inbox_dir/null. `refreshCaptureRuntime` remains the owner of captureRuntime/captureInboxDir and hook application (`index.ts:559-574`), with the existing startup/interval calls (`:590-593`). No paste-triggered refresh is added. PASTE_PUBLISH receives the resolved inbox and retains the existing explicit-inbox claim/settle/register chain (`capture-picker.ts:456-529`). The previously existing hotkey/picker/tray cache use remains outside this change.

**The ACs now reach the corrected boundary.** AC-132.6 and .7 pass the real resolvePasteInbox over a fake settings reader rather than replacing the resolver with a fixed destination. The A/B sequence, read count, register body, missing default directory and folder inventories distinguish per-call resolution from a first-adoption cache. AC-132.7 additionally demands no clipboard read on a null/rejecting dependency. AC-132.23 goes through the actual Electron page/preload/IPC/index dep and uses the backend stub's mutable inbox (`capture-picker.test.ts:41-52,78-85`); setInbox changes it before the second paste, with no wait for main's poll. The unit sequence provides the deterministic resolver proof; the Electron case covers the real wiring. These are sufficient planned checks, not claims that unimplemented tests have run.

**Assertion Reds remain possible.** Row 1 exports resolvePasteInbox as a null-returning stub, exports pasteClipboardImage returning failed, and wires a failed-answering IPC handler (`task.md:61`). AC-132.6 must first assert saved, so failed cannot satisfy it. AC-132.7 first asserts not-ready/empty/busy outcomes before inspecting a file or waiting for a register that the stub never makes; each differs from failed. Row 2 imports names row 1 already exports (`task.md:63`), avoiding a missing-export Red. AC-132.23's scheduled Red is row 4, after main Green but before page handlers: its first missing-toast expectation is an assertion, before register/file inspection (`task.md:36,64,66`; `implementation-plan.md:326-331`). It would also fail on row-1 page/IPC stubs. The intended Electron failure is the absent page behavior, not a launch failure or a later wait on a call the stub cannot produce.

### R2 — Correction regressions, scope and identity

No new behavior defect or material contradiction was found. PASTE_IPC, PASTE_MAIN, PASTE_LOG, LOOK_LAUNCH, AC-132.6/.7/.23, D-556 and task rows 1/3 agree on a fresh read per accepted invocation and not-ready on failure. F1's IMPORT_RUN predicate and real-wrapper negative case are intact. The goal's drop/button sequence, gui publication, editable-field native paste and single toast remain covered by their existing contracts and ACs. No new production Python, route, schema or MCP work was introduced.

HEAD independently reads `55d1289`; the targeted tracked diff is empty. Both corrected plan documents have zero CRLF sequences. The two tracked CRLF canon files retain pure CRLF (09: 1313; gui-actions-index: 127) and match HEAD after Git checkout newline normalization. The reviewed input hashes were captured independently and rechecked before hand-back. Other sessions' files, the excluded proposal and secret paths were not opened. No network, system clipboard, product suite, app, baseline, session gate, look seed or launcher was used.

D-560 and D-561 remain Mat's open decisions, as supplied. This approves plan adequacy only and does not execute the plan or decide those questions.

### Round-3 observed checks

All Python commands used PYTHONDONTWRITEBYTECODE=1. The parser selftest additionally used TMP/TEMP under C:/Temp/av-kit. Source reads and report writes were confined to the authorized paths.

| Check | Command or manual procedure | Exit | Result | Decisive evidence |
|---|---|---|---|---|
| F2 and regression recheck | Manual source/contract trace by codex-independent-reviewer: compare PASTE_IPC/MAIN/LOG, AC-132.6/.7/.23, D-556 and task rows 1–4 against fetchCaptureRuntime, refreshCaptureRuntime, explicit-inbox publisher and mutable E2E settings stub | null | pass | Every accepted paste reads once; null/rejection refuses before clipboard/filesystem; runtime mutation is absent from the read path; A/B unit cases and Electron wiring are named. |
| Current source/plan identity and line endings | `rtk proxy .venv/Scripts/python.exe C:/Temp/av-kit/s61-r3-source-probe.py` | 0 | pass | HEAD=55d1289; targeted tracked diff empty; plan/task CRLF=0; both canon files retain pure CRLF and normalized HEAD contents; per-call resolver, row-1 stub and row-3 wiring assertions pass. This is a static plan/source probe, not execution of proposed product code. |
| Assertion-Red parser negative oracles | `rtk proxy .venv/Scripts/python.exe docs/execution/plans/2026-11-10-gui-capture-image-import/red-check.py --selftest` | 0 | pass | 41 fixtures: 12 positive, 29 negative, 0 wrong. Assertion receipts accepted; missing-name required tests, launch/action timeouts, unhandled errors and exit-0 Reds refused. |
| Product tests/runtime | Not run by explicit review scope | null | n/a | Vitest, Playwright, pytest, the app and clipboard remain execution-stage evidence. |

```json
{"schema_version":"evidence.v1","check_id":"s61-r3-paste-inbox-recheck","procedure":"Trace the proposed per-paste resolvePasteInbox(fetchCaptureRuntime) dependency against capture-runtime.ts:65-82 and index.ts:559-593; inspect the explicit-inbox publisher, A/B resolver unit cases, failure/busy cases, Electron mutable-settings wiring and row-1/row-4 assertion Reds.","observer":"codex-independent-reviewer","cwd":"P:/av-kit","scope":"Session 61 plan F2 recheck and round-2 correction regressions","phase":"plan-review","exit_code":null,"result":"pass","tested_state":"55d1289; plan sha256 48944a886c75c4dec99e9d22d8fe8ae125f1915384abd9de04fab71b0f7bc61a; task sha256 50248e339615cd894d869ec7996a614bcd44dca5aacde12546801ad3e78eb3d6; targeted tracked diff empty","output":"No adoption flag or cached inbox in paste resolution. Each accepted invocation reads settings once, returns that reply's inbox_dir or null, and makes no runtime/hook/watcher mutation. AC-132.6/.7 test real resolver A/B and failure sequences; .23 tests Electron wiring. Failed-answering stubs produce assertion mismatches; page Red asserts a missing toast before file/register reads. F1 remains fixed; no new delivery defect found.","fresh":true}
```

```json
{"schema_version":"evidence.v1","check_id":"s61-r3-red-parser","command":"rtk proxy .venv/Scripts/python.exe docs/execution/plans/2026-11-10-gui-capture-image-import/red-check.py --selftest","cwd":"P:/av-kit","scope":"plan-local assertion-Red parser fixtures only","phase":"plan-review","exit_code":0,"result":"pass","tested_state":"55d1289; current untracked Session 61 plan tooling","output":"red-check selftest: 41 fixture(s) (12 positive, 29 negative), 0 wrong: []","fresh":true}
```

The scratch inventory probe was corrected during review: its first draft required a literal B in AC-132.23 (which says second folder), then compared CRLF checkout bytes directly with an LF Git blob. Those were reviewer-probe assumptions, not plan defects. The final invocation above exited 0; no product result is inferred from it.

### Verdict

`approved` — F1 remains fixed, F2 is fixed, and there are no new findings. The per-paste settings read removes both the startup/default-folder write and the Save-to-B-before-poll stale-folder write without changing shared runtime application. The complete rolling report is `C:/Temp/av-kit/s61-plan-review-round-3.md`. The coordinator owns canonical publication and ledger recording; this reviewer has made no repository edits or execution transition.
