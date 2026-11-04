---
review_mode: implementation
target_plan: "docs/execution/plans/2026-08-20-p6-gui-downloader/implementation-plan.md"
agent: gpt-5.6-sol
verdict: approved
findings_count: 0
round: 2
---

# Critical Review: p6-gui-downloader — Round 1

## Intent Anchor

Session 8 was supposed to deliver MEU-20 only: a truthful Downloader page at `/` whose queue renders the REST list envelope, whose Add/SABR/cookie/queue controls honor the approved contracts, and whose real-Electron Wave 1 tests prove the primary path without reaching live YouTube. The delivered app is reachable and builds, but it does not yet achieve that intent because the queue can display fabricated or incomplete state and the table omits required user-facing data.

## Findings

| Finding | Severity |
|---------|----------|
| **F1 — Add corrupts the canonical list cache and can display ghost or missing jobs (AC-20.3, AC-20.4, AC-20.21, `RENDER_ALL_ITEMS`).** `DownloaderPage` fabricates a `pending-*` row and writes it into `QUERY_KEY` before URL validation or POST success (`ui/src/renderer/src/features/downloader/DownloaderPage.tsx:199-220`). A blank URL makes `postDownloadCreate` return `{ items: [] }` without a POST or invalidation (`ui/src/renderer/src/features/downloader/download-commands.ts:114-125`), so the fake row remains until a later poll; a rejected POST likewise only sets an error and does not roll back/refetch (`DownloaderPage.tsx:230-233`). On success, `postDownloadCreate` first awaits list invalidation, then the page overwrites that full GET envelope with `DownloadCreateOut.items` (`DownloaderPage.tsx:221-227`), even though POST returns only newly created jobs while GET returns the whole queue (`packages/api/src/avkit_api/routes/downloads.py:71-91`). Existing queue rows can therefore disappear until the next poll. Remove the fabricated cache write or implement a rollback-safe mutation, and make the final canonical state come from the full list refetch without overwriting it with the create envelope. Add tests for blank/rejected Add and adding to a non-empty queue. | High |
| **F2 — The shipped queue table omits required Quality and Size columns.** The Downloader spec shows Status, Title, Quality, Size, Progress, and Speed (`docs/build-plan/06-gui.md:379-390`) and defines `quality` and `file_size` in the row contract (`docs/build-plan/06-gui.md:450-475`). The implementation instead renders queue position, Title, Status, Progress, Speed, and ETA (`ui/src/renderer/src/features/downloader/DownloadQueueTable.tsx:19-35`), while `DownloadListItem` drops `quality` and `file_size` entirely (`ui/src/renderer/src/features/downloader/useDownloadQueue.ts:8-18`). The independent column probe failed in `C:/Temp/av-kit/p6-gui-downloader-exec-r1-probe-table-columns.txt`. Restore the specified columns and add header/value assertions so this cannot remain green. | High |
| **F3 — SABR mutations do not invalidate the download queue required by AC-20.6.** The approved chain says Check/Force/Clear must invalidate both `QUERY_KEY` and the SABR query (`docs/execution/plans/2026-08-20-p6-gui-downloader/implementation-plan.md:258`), because Force/Clear can change item statuses. All three commands invalidate only `['downloads', 'sabr']` (`ui/src/renderer/src/features/downloader/download-commands.ts:173-185`), leaving queue rows, summaries, and enabled controls stale until polling repairs them. Invalidate both queries after each successful mutation and assert the behavior, not just endpoint strings. | Medium |
| **F4 — The two required test files give false confidence on the locked integration surfaces (IR-5).** `downloader-page.test.ts` is **🔴 Weak**: several integration ACs inspect source text or isolated helpers rather than rendering the page and asserting fetch/event behavior—for example CREATE_BODY (`ui/tests/unit/downloader-page.test.ts:141-158`), cookie persistence (`:203-225`), and PALETTE_DELIVER (`:296-305`). `download-queue.test.ts` is also **🔴 Weak for the primary happy path/seam**: it installs `context.route`, never calls the locked `page.route`, checks only that `page.route` is a function (`ui/tests/e2e/download-queue.test.ts:41-77,189`), and its POST handler checks field presence rather than the exact CREATE_BODY key set (`:47-56`). W1-4 can see `queue-row` from the production optimistic cache write before any POST result (`DownloaderPage.tsx:205-220`; `download-queue.test.ts:185-193`), so the happy-path assertion can stay green if the seam or create response handling is broken. Replace grep/helper-only integration claims with rendered interaction tests, install/assert the approved seam, assert exact request keys and no unhandled download request, and make W1-4 wait on backend-stub state rather than a fabricated row. | Medium |
| **F5 — `COOKIE_TEST_BODY` does not enforce its mode-dependent boundary constraints (IR-6).** The approved Boundary Inventory requires a browser when `mode=browser` and a cookie-file path when `mode=file` (`implementation-plan.md:242`). The Zod schema makes both fields independently optional and has no refinement (`ui/src/renderer/src/features/downloader/cookie-bar.ts:34-41`); the test covers only one valid file-mode object and no malformed/mismatched modes (`ui/tests/unit/downloader-page.test.ts:203-225`). Add a discriminated/refined strict schema and negative tests for missing required fields and fields invalid for the selected mode. | Medium |

## Scope Reviewed

- Correlated plan: `docs/execution/plans/2026-08-20-p6-gui-downloader/implementation-plan.md`
- Task state: `docs/execution/plans/2026-08-20-p6-gui-downloader/task.md` through H1-6a; H1-7 remains the active review row.
- Correlated handoff set: exactly one file, `.agent/context/handoffs/2026-08-20-p6-gui-downloader-MEU-20-handoff.md`.
- Spec: `docs/build-plan/06-gui.md` Downloader section and the approved named-set locks.
- Product/test targets listed in the review request, including downloader feature files, shell/router/registry integration, Electron preload build handling, unit tests, Wave 0 supersessions, and Wave 1 E2E.
- SSOT/hub: MEU-20 is `ready_for_review` at the exact plan path; phase `"6"` contains both required plan folders; hub Next is `/create-plan p6-gui-transcript`.
- Workspace is not a git repository (`git_repo=False`), so review used current file state, executable probes, OpenAPI no-drift, and receipts rather than a historical diff. No product, test, plan, MEU handoff, or SSOT file was edited by this reviewer.

## IR-1..IR-7 Checklist

| Check | Result | Evidence |
|-------|--------|----------|
| IR-1 — Live runtime evidence | Pass within the approved no-live boundary | Trusted post-edit real-Electron receipt `C:/Temp/av-kit/e2e-wave1.txt` reports 16 passed; this round captured its timestamp/output in `C:/Temp/av-kit/p6-gui-downloader-exec-r1-read-implementer-e2e.txt`. Network isolation is intentional, but F4 shows the primary assertion is not rigorous enough. |
| IR-2 — Stub behavioral compliance | Pass with caveat | The in-page stub maintains an items array for POST→GET (`download-queue.test.ts:78-128`), but F4 records that the locked `page.route`/exact-body proof is absent. |
| IR-3 — Error mapping completeness | N/A for untouched routes; UI coverage gap | FastAPI routers were outside this MEU and OpenAPI no-drift passed. The UI displays caught `ApiError`, but no rendered test proves 422/409 body behavior; included in F4. |
| IR-4 — Fix generalization | N/A — first implementation review | No prior execution-review finding was under recheck. Cross-surface invalidation scans identified F1 and F3. |
| IR-5 — Test rigor audit | Fail | `downloader-page.test.ts`: 🔴 Weak. `download-queue.test.ts`: 🔴 Weak on its contract-critical happy path/seam. Details and mutation scenarios are in F4. |
| IR-6 — Boundary validation coverage | Fail | CREATE_BODY and settings leaves use strict Zod schemas, but mode-dependent cookie-test constraints and negative tests are missing (F5); exact E2E CREATE_BODY keys are also not asserted (F4). |
| IR-7 — Deferral and AC coverage integrity | Pass | Fresh comparison found 22 plan ACs and all 22 in the handoff. MEU-21–25 all exist and remain pending. Transcript/TTS/Settings/PyInstaller deferrals are scheduled and no disguised Session 8 skip was found. |

## Adversarial Verification Checklist

| Check | Result | Evidence |
|-------|--------|----------|
| AV-1 — Failing-then-passing proof | Pass | Fresh `assert-red-oracle.ps1` recheck: `PASS: RED_ORACLE ui`. |
| AV-2 — No bypass hacks | Fail on evidence quality | No skip/only production bypass was found, but the optimistic queue insertion bypasses the E2E happy-path oracle (F1/F4). |
| AV-3 — Changed paths exercised by assertions | Fail | Create/cache, SABR dual invalidation, table headers/values, cookie PUT, and exact seam requests are not behaviorally asserted. |
| AV-4 — No skipped/xfail masking | Pass | No active skip/only/todo marker was found in the scoped tests. |
| AV-5 — No unresolved placeholders | Pass | Fresh feature-source scan was empty. |
| AV-6 — Source-backed criteria | Pass | AC-20.1–20.22 retain source labels; findings cite the approved plan/spec rather than adding new product requirements. |

## Commands Executed

| Command / probe | Result | This-round receipt |
|-----------------|--------|--------------------|
| `npx tsc --noEmit` from `ui/` | exit 0 | `C:/Temp/av-kit/p6-gui-downloader-exec-r1-ui-tsc.txt` |
| `npx vitest run --allowOnly=false` from `ui/` | exit 0; 51 passed | `C:/Temp/av-kit/p6-gui-downloader-exec-r1-ui-vitest.txt` |
| `npx eslint src/ tests/ --max-warnings 0` from `ui/` | exit 0 | `C:/Temp/av-kit/p6-gui-downloader-exec-r1-ui-eslint.txt` |
| `npm run build` from `ui/` | exit 0 | `C:/Temp/av-kit/p6-gui-downloader-exec-r1-ui-build.txt` |
| H1-2 Python regression set from `task.md` | exit 0; 298 passed, 1 warning | `C:/Temp/av-kit/p6-gui-downloader-exec-r1-pytest-regression.txt` |
| `uv run python tools/export_openapi.py --check openapi.committed.json` | exit 0 | `C:/Temp/av-kit/p6-gui-downloader-exec-r1-openapi-check.txt` |
| `assert-e2e-control-census.ps1` | pass | `C:/Temp/av-kit/p6-gui-downloader-exec-r1-e2e-control-census.txt` |
| Post-edit Playwright receipt inspection | 16 passed | `C:/Temp/av-kit/p6-gui-downloader-exec-r1-read-implementer-e2e.txt` (source receipt: `C:/Temp/av-kit/e2e-wave1.txt`) |
| `assert-red-oracle.ps1 -Kind ui` | pass | `C:/Temp/av-kit/p6-gui-downloader-exec-r1-red-oracle.txt` |
| Handoff marker and AC-set checks | pass; 22/22 | `C:/Temp/av-kit/p6-gui-downloader-exec-r1-handoff-markers.txt`; `C:/Temp/av-kit/p6-gui-downloader-exec-r1-ac-coverage.txt` |
| SSOT/status/hub and render checks | pass | `C:/Temp/av-kit/p6-gui-downloader-exec-r1-ssot-check.txt`; `C:/Temp/av-kit/p6-gui-downloader-exec-r1-ssot-render-check.txt` |
| Required table-column probe | **exit 1**; `quality` and `file_size` missing | `C:/Temp/av-kit/p6-gui-downloader-exec-r1-probe-table-columns.txt` |
| Create/cache, E2E seam, SABR invalidation, and cookie-schema scans | evidence captured | `C:/Temp/av-kit/p6-gui-downloader-exec-r1-probe-create-cache.txt`; `C:/Temp/av-kit/p6-gui-downloader-exec-r1-probe-e2e-seam.txt`; `C:/Temp/av-kit/p6-gui-downloader-exec-r1-sabr-invalidate.txt`; `C:/Temp/av-kit/p6-gui-downloader-exec-r1-cookie-schema.txt` |
| Canonical-path/write-scope pre-edit guard | pass; review absent, one correlated handoff | `C:/Temp/av-kit/p6-gui-downloader-exec-r1-workspace-scope.txt` |

## Open Questions / Assumptions

None block correction. The approved plan and spec determine the required behavior. Because no git metadata exists, “FastAPI/MCP untouched” cannot be proven historically; current-state OpenAPI no-drift and scope inspection found no delivered Session 8 dependency on rewrites.

## Required Follow-up

1. Correct F1 and add rendered tests for blank/rejected Add and successful Add into a non-empty queue.
2. Correct F2 and assert the specified table headers and row values.
3. Correct F3 and assert both query invalidations after all SABR mutations.
4. Strengthen the unit/E2E tests in F4 so CREATE_BODY, COOKIE_SETTINGS_PUT, PALETTE_DELIVER, and E2E_SEAM mutations fail.
5. Correct F5 with mode-dependent strict validation and negative tests.
6. Re-run the registered UI, Python regression, OpenAPI, control-census, and real-Electron Wave 1 gates, then append Round 2 to this same rolling review file.

## Verdict

`changes_required` — two evidence-backed High findings break the approved queue contract and central Downloader UI behavior. Green build/test receipts do not override those file-state failures; F4 explains why the current suite false-passes them.

## Residual Risk

No live YouTube/HF/Kokoro operation was run. The existing E2E seam appears to intercept the current download mutation paths, but until F4 is corrected the receipt does not independently prove that removing or weakening the seam would fail before any live extraction path is reached.

---

# Critical Review Update: p6-gui-downloader — Round 2 (2026-08-20)

## Intent Anchor

MEU-20 is intended to deliver a truthful Downloader page at `/`: Add must converge on the full `{ items, processor }` queue without fabricated rows, the table must expose the specified job data, SABR/cookie/palette controls must honor their locked contracts, and Wave 1 must prove the primary real-Electron flow without reaching live YouTube. Current file state and the reproduced receipts now achieve that intent.

## Findings

| Finding | Severity |
|---------|----------|
| None. No evidence-backed material failure survived Round 2 verification. | — |

## Round 1 Recheck

| Finding | Status | Current-state evidence |
|---------|--------|------------------------|
| F1 — fabricated Add/cache state | **Closed** | `DownloaderPage.tsx:154-173` rejects a blank URL before mutation and never writes an optimistic row. `download-commands.ts:119-136` POSTs, then GETs and stores the complete list envelope before invalidating `QUERY_KEY`; it never stores the create envelope. Rendered tests cover blank Add, rejected Add, and successful Add with an existing row (`downloader-page.behavior.test.ts:145-195`), including an exact cache assertion for both IDs. |
| F2 — missing Quality and Size | **Closed** | `DownloadListItem` carries `quality` and `file_size` (`useDownloadQueue.ts:8-18`); the table renders `Quality` and `Size` (`DownloadQueueTable.tsx:45-46`). The rendered table test asserts both headers and concrete values (`downloader-page.behavior.test.ts:197-212`). |
| F3 — incomplete SABR invalidation | **Closed** | The shared helper invalidates `QUERY_KEY` and `['downloads','sabr']` (`download-commands.ts:114-117`), and Check/Force/Clear all await that helper (`:184-196`). The behavior test spies on both keys through `forceSabr` (`downloader-page.behavior.test.ts:215-225`); direct inspection confirms the other two exports use the same helper. |
| F4 — false-pass integration tests | **Closed** | Rendered tests now exercise blank/rejected/successful Add with exact CREATE_BODY keys, cookie-settings PUT, and AppShell palette delivery (`downloader-page.behavior.test.ts:145-195,227-273`). W1-4 now calls `page.route` (`download-queue.test.ts:276-303`) and waits for the stateful stub/list row with title `E2E` (`:304-307`), not a fabricated cache row. W1-6 exercises off-route palette delivery in real Electron (`:331-343`). The in-page `window.fetch` seam is the effective Electron interceptor; repository-wide search found its activation flag set only by this E2E file, while ordinary `apiFetch` still resolves backend URL/token through IPC (`api.ts:19-35`). |
| F5 — mode-independent cookie-test schema | **Closed** | `COOKIE_TEST_BODY` is a strict discriminated union for `none`, `browser`, and `file` (`cookie-bar.ts:34-53`). Negative tests reject missing required fields, cross-mode fields, and extras (`downloader-page.behavior.test.ts:275-282`). |

## Scope Reviewed

- Correlated plan: `docs/execution/plans/2026-08-20-p6-gui-downloader/implementation-plan.md`
- Correlated work handoff: `.agent/context/handoffs/2026-08-20-p6-gui-downloader-MEU-20-handoff.md`
- Current implementation: `DownloaderPage.tsx`, `download-commands.ts`, `DownloadQueueTable.tsx`, `useDownloadQueue.ts`, `cookie-bar.ts`, and `ui/src/renderer/src/lib/api.ts`
- Current tests: `downloader-page.test.ts`, `downloader-page.behavior.test.ts`, `api-fetch.test.ts`, and `download-queue.test.ts`
- Trusted real-Electron/control receipts and the unchanged 298-test Python regression receipt named by the user
- The workspace is not a git repository, so this review used current file state, executable checks, and receipts rather than historical diffs. No product, test, plan, work-handoff, or SSOT source file was patched by this reviewer.

## IR-1..IR-7 Checklist

| Check | Result | Evidence |
|-------|--------|----------|
| IR-1 — Live runtime evidence | **Pass within the approved no-live boundary** | `C:/Temp/av-kit/e2e-wave1-r2.txt` records 16 passed in real Electron, including W1-4 Add and W1-6 off-route palette delivery. The approved plan deliberately substitutes an isolated seam for live YouTube extraction. |
| IR-2 — Stub behavioral compliance | **Pass** | The in-page seam maintains a list across POST→GET (`download-queue.test.ts:150-191`); W1-4 waits for the GET-backed `E2E` row. The rendered successful-Add test independently verifies that an existing item survives the create/list round trip. |
| IR-3 — Error mapping completeness | **N/A for unchanged FastAPI routes; UI error surface passes** | This MEU did not rewrite API routes. The rendered rejected-Add test supplies a 422 error envelope and asserts the visible error while proving no ghost row (`downloader-page.behavior.test.ts:157-172`). The trusted Python regression receipt includes the API boundary/error tests. |
| IR-4 — Fix generalization | **Pass** | All five Round 1 surfaces were re-searched. The SABR fix is shared by Check/Force/Clear; no production `pending-*` cache write remains; the strict cookie union covers every mode; repository search found no non-E2E activation of the IPC-skipping seam. |
| IR-5 — Test rigor audit | **Pass** | `downloader-page.behavior.test.ts`: 🟢 Strong (rendered positive/negative behavior and exact state/body assertions). `download-queue.test.ts`: 🟢 Strong for its locked real-Electron controls and stateful happy path. `api-fetch.test.ts`: 🟢 Strong on bearer/error/204/form behavior. `downloader-page.test.ts`: 🟡 Adequate as a source/contract census, now supplemented on every Round 1 weak surface by rendered behavior tests. No 🔴 file remains in the recheck scope. |
| IR-6 — Boundary validation coverage | **Pass** | CREATE_BODY and COOKIE_SETTINGS_PUT remain strict; COOKIE_TEST_BODY is mode-discriminated and strict, with malformed/cross-mode negative tests. W1-4 and the rendered Add test assert the exact create key set. |
| IR-7 — Deferral and AC-coverage integrity | **Pass** | Current plan and handoff retain AC-20.1–AC-20.22. MEU-21–25 remain scheduled deferrals; no orphan or disguised MEU-20 deferral was introduced by the corrections. |

## Adversarial Verification Checklist

| Check | Result | Evidence |
|-------|--------|----------|
| AV-1 — Failing-then-passing proof | **Pass with evidence note** | The project RED_ORACLE remains present and current gates are green. The new correction-specific behavior file has no separately retained pre-fix red receipt; this is a non-blocking auditability note because its assertions directly reproduce the Round 1 failures against current runtime behavior. |
| AV-2 — No bypass hacks | **Pass** | `--allowOnly=false` passed; no active skip/only guard or assertion bypass was found. The stateful fetch replacement is the plan-approved E2E seam, not a production behavior shortcut. |
| AV-3 — Changed paths exercised by assertions | **Pass** | F1–F5 each have explicit value/state assertions, including exact keys, both preserved IDs, headers/values, invalidation keys, mode failures, and the real-Electron row title. |
| AV-4 — No skipped/xfail masking | **Pass** | Vitest completed 60/60 with `--allowOnly=false`; scoped scan found no active skip/only marker. |
| AV-5 — No unresolved placeholders | **Pass** | Scoped source/test scan found no product placeholder; the only `TODO`/`pending-` matches were negative assertions in tests. |
| AV-6 — Source-backed criteria | **Pass** | The corrections implement the already-approved AC-20.3/20.4/20.6/20.8/20.13/20.16/20.19/20.21 contracts and add no new product behavior. |

## Commands and This-Round Receipts

| Verification | Result | Receipt |
|--------------|--------|---------|
| `npx tsc --noEmit` | exit 0 | `C:/Temp/av-kit/p6-gui-downloader-exec-r2-ui-tsc.txt` |
| `npx vitest run --allowOnly=false` | exit 0; 60 passed | `C:/Temp/av-kit/p6-gui-downloader-exec-r2-ui-vitest.txt` |
| `npx eslint src/ tests/ --max-warnings 0` | exit 0 | `C:/Temp/av-kit/p6-gui-downloader-exec-r2-ui-eslint.txt` |
| `npm run build` | exit 0 | `C:/Temp/av-kit/p6-gui-downloader-exec-r2-ui-build.txt` |
| Trusted Wave 1 read | 16 passed | `C:/Temp/av-kit/e2e-wave1-r2.txt`; inspection copy `C:/Temp/av-kit/p6-gui-downloader-exec-r2-inspect-e2e-wave1-r2.txt` |
| Trusted control census read | pass | `C:/Temp/av-kit/e2e-control-census-r2.txt`; inspection copy `C:/Temp/av-kit/p6-gui-downloader-exec-r2-inspect-e2e-control-census-r2.txt` |
| Trusted Python regression read | 298 passed, 1 warning | `C:/Temp/av-kit/pytest-p6-regression.txt`; inspection copy `C:/Temp/av-kit/p6-gui-downloader-exec-r2-inspect-pytest-regression.txt` |
| F1–F5 code/test line probes | pass | `C:/Temp/av-kit/p6-gui-downloader-exec-r2-f1-f3-lines.txt`; `...-f2-lines.txt`; `...-f4-f5-lines.txt` |
| Seam/auth activation search | no non-E2E setter found | `C:/Temp/av-kit/p6-gui-downloader-exec-r2-e2e-seam-search.txt` |
| Skip/placeholder and AC-coverage sweeps | pass | `C:/Temp/av-kit/p6-gui-downloader-exec-r2-bypass-placeholder-scan.txt`; `...-ac-occurrences.txt` |
| Canonical-path pre-edit guard | pass | `C:/Temp/av-kit/p6-gui-downloader-exec-r2-pre-edit-guard.txt` |
| Execution-review checker | pass: `PASS: latest execution review approved` | `C:/Temp/av-kit/p6-gui-downloader-exec-r2-review-check.txt` |

## Open Questions / Assumptions

None block approval. The review accepts the user-documented Electron limitation: `page.route` is called as locked, while the in-page `window.fetch` stub provides reliable interception. No ordinary production source sets `__e2eSeamInstalled`; without that test-only flag, `apiFetch` continues through backend/token IPC.

## Verdict

`approved` — F1–F5 are closed against current file state. The reproduced UI gates pass, the trusted real-Electron/control/Python receipts are consistent, and no evidence-backed High/Critical material failure remains.

## Required Follow-up

None for this review. The implementer may continue the workflow’s post-approval closeout; this reviewer does not patch those artifacts.

## Residual Risk

No live YouTube request was made, by approved design. Electron’s reliable interception remains the explicit in-page seam rather than Playwright routing alone; the real-Electron test proves the stateful substitute path, and no non-E2E activation path was found. The correction-specific rendered tests emit React `act(...)` warnings and lack a separately retained correction-red receipt, but neither condition produced a behavioral false-pass in this review.
