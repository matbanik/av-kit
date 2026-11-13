---
date: "2026-11-13"
review_mode: "plan"
target_plan: "docs/execution/plans/2026-11-13-capture-copy-image/implementation-plan.md"
verdict: "approved"
findings_count: 0
template_version: "2.2"
requested_verbosity: "standard"
agent: "codex-independent-reviewer"
loop_id: "s69-plan-canonical-2026-11-13-capture-copy-image"
round: 1
---

# Critical Review: 2026-11-13-capture-copy-image

> **Review Mode:** `plan`
> **Verdict:** `approved`

## Scope

Reviewed the working-tree implementation plan, task table and five plan-local scripts against the MEU-104 spec, grouping, matrix, registry entry and affected production/test contracts at `main` HEAD `b3f3933`. Applied PR-1 through PR-9 and the Materiality Gate. Claude Code/Anthropic authored the plan; Codex is its independent reviewer.

**Intent anchor:** Session 69 lets a user copy the image as they see it, with the current marks, saved or not, through a Copy image button and canvas Ctrl+C. Both go through a new `POST /captures/{id}/render` that bakes the posted marks exactly as Save would and writes no file. The filmstrip's Copy image follows the as-shown rule, and the per-shot actions take the names "Save annotations", "Flatten into image…" and "Restore backup…", with "Save and flatten" in the dirty-flatten confirm.

**Intent assessment:** yes, as a plan: executing its contracts and passing the prescribed behavioral assertions would deliver the registered goal. This does not certify an implementation or authorize execution.

Only scratch Python probes and the three expressly permitted script selftests ran. No repository file was edited. No product suite, baseline/session gate, build, package manager, backend, MCP server, network request or system clipboard operation ran. The private untracked settings file was neither opened nor hashed. The coordinator owns the canonical report copy and ledger recording.

## Findings

| # | Severity | Blocking | Kind | Finding | File:Line | Recommendation | Status |
|---|---|---|---|---|---|---|---|

## Q1 — Goal and end-to-end trace

Accepted: COPY_KEY → the button's copy operation → `renderClipboardPng` → strict `parseAnnotateBody` → `postAuthorizedBlob` → RENDER_ROUTE/`AnnotateIn` → `_annotations_from_in` → `render_marks` → `_clamp_annotation` → `render`/`_bake_canvas` → `_encode_view` → `toClipboardPng` → the recording clipboard fake. The proposed joins are explicit at `implementation-plan.md:149-158,203-208`; AC-104.10 and .11 trace the Python and renderer halves using an unsaved mark, pixels, posted body and returned bytes. Rows 1–3 supply the names, Reds and implementation.

The three spec rules at `docs/build-plan/09-screenshot-capture.md:953-955` map to AC-104.2–.20/.22, with filmstrip coverage in .15 and the no-registry guard in .23 (`implementation-plan.md:278-284`). The button, keyboard, no-write render, text-field exception, filmstrip variant and action names all have work and assertions. No uncovered goal sentence found.

## Q2 — RENDER_BAKE and D-689

Accepted the extraction of precisely the region pass and per-mark drawing loop, leaving open/conversion and PNG/lossy writers in `bake` (`adapter.py:526-547`). Every existing caller keeps the same signature, draw order and RGB conversion. The scratch AST extraction compared the old and proposed bake bodies over three original formats, two mark states and three output formats: **18 byte-identical comparisons**. Six in-memory renders also equaled `bake(..., "png")` bytes and decoded as RGB PNG without changing the scratch files.

“Bakes exactly as Save would” concerns the shared compositing operation. Render deliberately returns lossless PNG even when Save's configured output is JPEG/WebP; it cannot promise identical lossy file bytes, and D-690 explicitly explains that distinction (`implementation-plan.md:245,250,488`). AC-104.2 covers JPEG/WebP originals and the shared RGBA-to-RGB step, with a separate output-format negative. MEU-136 export consumes the already-baked annotated sibling (`services/capture.py:1753-1754`); sharing its upstream bake and MEU-128's encoder fits grouping §9.4 without a third drawing loop or encoder. No conflicting bake contract found.

## Q3 — RENDER_SERVICE, RENDER_ROUTE and D-695

Accepted the lock across lookup/read/clamp/bake. `CAPTURE_FILE_LOCK` is a non-reentrant lock (`services/capture.py:130`), but the proposed direct route call acquires it once and calls no locked service operation. The adapter/helper never acquires it. This matches annotate's lock order (`:1448`) and prevents flatten/revert from replacing the source during render.

The proposed missing-shot/missing-original checks give 404; the fixed unreadable-image refusal gives 422 through `errors.py:33,37`. Request-validation errors discard the refused input (`errors.py:121-128`); domain annotation checks and render use fixed messages. AC-104.3/.4/.6/.7/.10/.14 cover those boundaries and nonmutation. No new path/text disclosure identified in the specified path.

Accepted no 15 MiB response cap: render encodes a catalog image already supported by Save, and the spec imposes no cap. This is not a claim of bounded memory; the existing GET image cap is itself applied after reading bytes (`routes/captures.py:415-431`). The route addition reuses existing schemas. The plan names all four 78-count assertions in `test_api_openapi.py`, ROUTE_INDEX adjacency and `test_api_downloads.py:372`; row 3 regenerates OpenAPI and H1-4 inspects its delta. No missing route/count pin found.

## Q4 — COPY_KEY and D-692

Accepted the branch after history handling and before the remaining mark keys (`CapturePage.tsx:1637-1666`). Recording, text draft, composition and crop return earlier. COPY_KEY adds the modifier/repeat, confirmation, collapsed-selection, editable-target, selected-shot and overlay-ready checks. A C event is not a history chord; Z/Y behavior remains in its existing branch, while paste remains its separate page listener (`:529-561`). No copy listener or registry entry is introduced.

`historyOwnsFocus` deliberately includes the page body and nonexcluded controls within the viewport (`:171-202`), including mark-list buttons and editor tool/action buttons. It excludes the filmstrip, external toolbar/navigation controls, text/color controls and modal/confirm focus. The additional event-target check protects native text copy. On another route CapturePage unmounts (`router.tsx:19-24,53-58`), removing its key listener (`CapturePage.tsx:1738-1743`). This is consistent with D-678's page-owned route and D-692's stated focus choice. No contradictory focus requirement found.

## Q5 — COPY_BUTTON and D-696

Accepted the selected-shot/loaded-overlay/no-text-draft enable rule for copying the defined current annotation list, independently of whether it is saved. On selection/detail changes the overlay effect resets readiness and marks, cancels stale loads, and enables only after valid detail arrives (`CapturePage.tsx:622-698`). The button therefore does not intentionally reuse a previous shot's loaded marks. AC-104.12/.13 cover the unloaded and missing-shot guards and current-mark POST.

Adding the Copy icon after Save preserves crop-button disjointness. The plan schedules the exact ACTIONS/key-order and mounted-order expectations in AC-81.1/.2, the WAVE9 lists and affected source pins (`implementation-plan.md:168-184`). The crop test checks intersection only; icon-hints has no old-name/order pin. No omitted blocking button-map dependency found.

## Q6 — FILMSTRIP_AS_SHOWN and D-677 A

Accepted the nonempty `annotated_path` signal for the catalog's saved baked image (`implementation-plan.md:156`). Save supplies that path; clearing marks and flattening clear it (`services/capture.py:1456-1464,1872-1887`). Revert's rebake keeps it only when saved marks remain (`:1961-1980`). Thus a flattened shot uses its now-baked original, while a saved overlay uses its annotated file.

`toClipboardPng` passes PNG bytes unchanged and decodes/re-encodes JPEG/WebP through `encodePng` (`capture-clipboard.ts:35-78`). AC-104.15 covers the positive path and both null/empty fallbacks. The editor's unsaved-list render and the filmstrip's saved catalog view match the supplied D-677 ruling. No conflicting source selection found.

## Q7 — Labels, dirty flatten and D-693/D-694

Accepted enabling dirty Flatten only with current marks and a savable state, and keeping Restore backup disabled while dirty. SAVE_AND_FLATTEN explicitly checks the live save gate, awaits Save, and stops before flatten on false or exception (`implementation-plan.md:158,265-267`). An empty current list cannot open this dirty-flatten flow. `saveAnnotations` returns success only after the annotate request and invalidation complete (`capture-commands.ts:77-94`); a thrown or incomplete request cannot enter the specified success branch.

The rename inventory covers tooltips/aria names, confirm accepts/text, status lines, Settings, help and the specified docs, while retaining API/MCP/settings keys and the separately scoped palette label. The absence scan targets `ui/src`; its excluded lines are comments, while `tooltip.test.tsx` is outside that source scope. The moved MEU-67/81 expectations, including dirty-enabled behavior and disabled-reason cases, are explicitly scheduled in row 2 (`implementation-plan.md:168-178`). No material label or pin omission found.

## Q8 — Type-only names, Reds and moved pins

Accepted row 1's names and deliberately wrong return stubs, with the bake extraction retaining existing behavior. All Session 69 names in `DECLARED_NEW` are supplied before the Reds. Required tests must assert before patching/calling/indexing; wrong exception classes are caught and asserted, and missing Electron elements fail an expect assertion before a click (`task.md:36-50`). The intended new behavior therefore has assertion-based Red oracles instead of missing-import/setup failures.

The scratch source check confirmed exactly **19 required titles**: Python .2–.8/.10, Vitest .11–.20 and Electron .22. Excluding .1/.9/.21/.23 follows their type/guard/spec-check roles. The separate moved-pin receipt is diagnostic at Red and mandatory Green coverage; it does not pretend that changed route counts or labels pass before implementation. The fresh red-check selftest passed **49 fixtures, 0 wrong**, including declared-name refusal and .1/.10 boundaries; id-length passed **4 cases, 0 wrong**. No impossible Red-to-Green sequence found.

## Q9 — Clipboard isolation and byte hash

Accepted recording clipboard fakes and fake render responses for copy tests, with Electron AC-104.22 limited to mounting, labels and confirmation. Every listed Playwright command selects `capture-inbox.test.ts`; the wrapper forwards that selector (`ui/scripts/playwright-with-outputfile.mjs:18-49`). The full Vitest include patterns exclude `tests/e2e` (`ui/vitest.config.ts:15`). The real-clipboard AC-88.12 at `capture-filmstrip-actions.test.ts:246-267` is outside these commands.

The independently recomputed AC-51.6/AC-81.13 prefix SHA-256 is `6E569F820459EA2BE3264324635C0A9D22FC4AACFA2DAD6A6B54F840870FF454`. A scratch-only additive append after MEU-103 leaves that prefix byte-for-byte unchanged. The plan also requires the action-row check separately after the real edit. No planned system clipboard write or hash change found.

## Q10 — Endings, identity, scope and records

Accepted measured existing endings, byte-preserving edits and LF for the three new test files. The scratch inventory checked all **28 planned product/spec/test paths** against the session gate's allowed set, confirmed the three scheduled new tests are absent, and matched every existing target's stated endings. Project/status/closeout files and plan scripts are also covered by the explicit entries and prefixes (`session-gate.ps1:47-85`). Referenced root tooling exists; task rows remain unstarted.

The identity binds HEAD, product/tests/config/scripts/spec/status inputs and the named runtime/binary inputs, with the declared closeout-artifact exclusions. Its fresh scratch selftest reported **0 failures**. The live whole-tree identity was intentionally not run, because the sandbox sees a private untracked settings file. Row 6 confines status work to MEU-104 and grouping row 45, requires pre-status copies/diffs and `render --check`; H2 repeats affected canon checks after approval changes status (`task.md:70,81,97`).

The pure embedded baseline preconditions were independently exercised without running baseline.ps1: current queue/shapes passed, missing MEU-104 and missing bake shapes were refused, and the current pending-authority Status line was refused as expected. No materially false-passing precondition demonstrated. Mat's execution budget and execute words remain a later human gate, not a review finding.

## Q11 — Safety

Accepted generated images under `tmp_path`, in-process API clients, fake renderer/backend/clipboard collaborators, the scoped Electron seam and ignored build outputs. Nothing new in the planned feature calls YouTube, a live MCP server or an external resource. The actual reviewer probes used `PYTHONDONTWRITEBYTECODE=1` and redirected temporary state under `C:/Temp/av-kit/s69/review`; the bake probe suppressed its process-local path logger. No private file, comparison-report contents or system clipboard was accessed. The existing full suites remain execution-stage validation, not something this review ran or certified.

No rejected proposal or delivery-level safety defect identified. Implementation review must still verify the final test bodies, redacted errors and actual gate evidence.

## Checklist Results

| Check | Result | Procedure / command | Exit | Evidence |
|---|---|---|---|---|
| PR-1 plan/task alignment | pass | Manual comparison of mechanisms, ACs and task rows; observer codex-independent-reviewer | null | Matching scope and order: 0, 1, 2, 3, 5, 6, H1, review, H2. |
| PR-2 unstarted confirmation | pass | Current task/status inspection and scratch source inventory; observer codex-independent-reviewer | null | All task rows unchecked; MEU-104 pending; three new tests absent; HEAD b3f3933. |
| PR-3 task contracts | pass | Manual owner/deliverable/validation/dependency inspection; observer codex-independent-reviewer | null | Concrete rows and ordered validations; supplied task-lint receipt reports OK, 23 rows. |
| PR-4 validation realism | pass | `rtk proxy .venv/Scripts/python.exe C:/Temp/av-kit/s69/review/review-probe.py` | 0 | 18 extraction comparisons, 6 renders, 19 required Red titles and tooling existence checked. |
| PR-5 source-backed planning | pass | Manual trace to 09, grouping, matrix and registry; observer codex-independent-reviewer | null | Three spec rules and D-689–D-697 have explicit mechanisms and ACs. |
| PR-6 corrections readiness | pass | Manual first-round artifact/review-boundary inspection; observer codex-independent-reviewer | null | One target, explicit handoff and independent rolling review; no prior findings to recheck. |
| PR-7 scope discipline | pass | Manual exclusions and allowed-set comparison, plus scratch inventory; observer codex-independent-reviewer | null | No required behavior deferred; MEU-102 is the registered subsequent slice; 28 planned paths allowed. |
| PR-8 reachability and controls | pass | Manual production-chain trace and scratch negative preconditions/selftests; observer codex-independent-reviewer | null | Direct route-to-adapter and key-to-clipboard chains; missing queue ID/shape refused. |
| PR-9 single-statement contracts | pass | Manual comparison of named contracts with task/AC references; observer codex-independent-reviewer | null | No materially conflicting live behavioral statement found. |
| Red detector selftest | pass | `rtk proxy python docs/execution/plans/2026-11-13-capture-copy-image/red-check.py --selftest` | 0 | 49 fixtures: 15 positive, 34 negative; 0 wrong. |
| Identity selftest | pass | `rtk proxy python docs/execution/plans/2026-11-13-capture-copy-image/identity.py --selftest` | 0 | Bound mutations detected, historical evidence refused, artifact exclusions preserved; 0 failures. |
| Pytest-title selftest | pass | `rtk proxy python docs/execution/plans/2026-11-13-capture-copy-image/id-length.py --selftest` | 0 | 4 boundary cases; 0 wrong. |
| Product tests/builds/runtime gate | n/a | Not run under explicit read-only review restrictions | null | Plan review only. |

```json
{"schema_version":"evidence.v1","check_id":"s69-r1-independent-source-probe","command":"rtk proxy .venv/Scripts/python.exe C:/Temp/av-kit/s69/review/review-probe.py","cwd":"P:/av-kit","scope":"in-memory proposed bake extraction, PNG encoding, pure baseline preconditions, path/endings/Red-title inventory and test-ID hash","phase":"plan-review","exit_code":0,"result":"pass","tested_state":"HEAD b3f3933; implementation-plan.md sha256 807ea7e48a3fd8df306b68d6f0535f31943275397e2f8c9a04ba788309613f16; task.md sha256 15d5e4019d9e0d1133564c5e95a07e352b53d0e3509d0fc37bcc8830b36ecf53; scratch source models only","output":"Five precondition expectations true: pending authority refused, current queue/shapes pass, missing MEU-104/bake refused. 18 byte-identical bake comparisons; 6 RGB PNG renders equal bake(PNG), with no model-render file writes. 28 planned paths allowed; 3 new tests absent; existing endings match; 19 required Red titles match; referenced tooling exists. Prefix SHA-256 6E569F820459EA2BE3264324635C0A9D22FC4AACFA2DAD6A6B54F840870FF454 unchanged by additive append.","fresh":true}
```

```json
{"schema_version":"evidence.v1","check_id":"s69-r1-red-check-selftest","command":"rtk proxy python docs/execution/plans/2026-11-13-capture-copy-image/red-check.py --selftest","cwd":"P:/av-kit","scope":"Red detector positive and negative fixtures","phase":"plan-review","exit_code":0,"result":"pass","tested_state":"HEAD b3f3933; current untracked Session 69 plan-local script; PYTHONDONTWRITEBYTECODE=1; TMP/TEMP under C:/Temp/av-kit/s69/review","output":"red-check selftest: 49 fixture(s) (15 positive, 34 negative), 0 wrong: []","fresh":true}
```

```json
{"schema_version":"evidence.v1","check_id":"s69-r1-identity-selftest","command":"rtk proxy python docs/execution/plans/2026-11-13-capture-copy-image/identity.py --selftest","cwd":"P:/av-kit","scope":"Input binding and artifact exclusions in scratch repository","phase":"plan-review","exit_code":0,"result":"pass","tested_state":"HEAD b3f3933; current untracked Session 69 plan-local script; PYTHONDONTWRITEBYTECODE=1; TMP/TEMP under C:/Temp/av-kit/s69/review","output":"Bound product/test/config/spec/status/script/runtime mutations changed identity and refused historical evidence; excluded artifact edits kept identity; identity selftest: 0 failure(s)","fresh":true}
```

```json
{"schema_version":"evidence.v1","check_id":"s69-r1-id-length-selftest","command":"rtk proxy python docs/execution/plans/2026-11-13-capture-copy-image/id-length.py --selftest","cwd":"P:/av-kit","scope":"71/72-character pytest-title boundaries","phase":"plan-review","exit_code":0,"result":"pass","tested_state":"HEAD b3f3933; current untracked Session 69 plan-local script; PYTHONDONTWRITEBYTECODE=1","output":"id-length selftest: 4 case(s), 0 wrong","fresh":true}
```

## Verdict

`approved` — no Critical or High findings and no required corrections. The plan delivers the registered intent with a coherent implementation/test sequence. Scratch models support the design; product behavior and gate success remain to be established during authorized execution and independent execution review.

**Next action:** the coordinator saves this complete report to `.agent/context/handoffs/2026-11-13-capture-copy-image-plan-critical-review.md` and records the structured verdict. Mat then sets the execution review budget and gives the execution authorization required by the plan's human gate. This review makes neither decision for him.
