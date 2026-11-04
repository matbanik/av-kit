---
review_mode: implementation
target_plan: "docs/execution/plans/2026-08-20-p6-gui-tts-models/implementation-plan.md"
agent: gpt-5.6-sol
verdict: approved
findings: []
findings_count: 0
round: 2
---

## Intent Anchor

MEU-22 was intended to replace the `/tts` placeholder with a working TTS editor and Model Manager that consume the existing FastAPI contracts as-is, preserve text/file/paste semantics, prepare and generate through strict request bodies, expose valid generate/cancel state transitions, persist the approved settings leaves, deliver palette actions from AppShell, and prove those behaviors in compiled Electron without entering MEU-23–25 or rewriting FastAPI/MCP. The delivered page and receipts establish substantial UI wiring, but three High runtime/contract failures mean the implementation does not yet achieve that intent.

## Scope Reviewed

- Primary target: `.agent/context/handoffs/2026-08-20-p6-gui-tts-models-MEU-22-handoff.md`, correlated by the exact `2026-08-20-p6-gui-tts-models` plan slug and the plan's single-handoff declaration (`implementation-plan.md:40-46`).
- Secondary contract: `docs/execution/plans/2026-08-20-p6-gui-tts-models/{implementation-plan.md,task.md}`, `docs/build-plan/06-gui.md` TTS/Settings sections, and the established TTS/model wire schemas in `docs/build-plan/04-rest-api.md:239-291` and `packages/api/src/avkit_api/schemas/models.py:12-65`.
- Product surfaces: `ui/src/renderer/src/features/tts/`, `router.tsx`, `AppShell.tsx`, `commandRegistry.ts`, `ui/src/main/{ipc,index,preload}.ts`, and `env.d.ts`.
- Test surfaces: `ui/tests/unit/tts-page.test.ts`, `ui/tests/unit/secret-paths.test.ts`, `ui/tests/e2e/tts-generate.test.ts`, `ui/tests/e2e/test-ids.ts`, and `assert-e2e-control-census.ps1`.
- User scope override applied: MEU-22 only. MEU-23–25, FastAPI/MCP rewrites, and chrome rewinds were not reviewed as new implementation work.
- `git diff` was unavailable because `P:/av-kit` is not a Git repository. Review therefore used numbered current-file reads, current API schema state, and the named receipts.

## Findings

| Finding | Severity |
|---|---|
| **F1 — The Model Manager consumes a response shape that the real `/models/available` endpoint never returns, and the Electron seam repeats the invented shape.** The API's `ModelVariantOut` fields are `id`, `name`, `format`, `precision`, `size_bytes`, `path`, and `is_downloaded` (`packages/api/src/avkit_api/schemas/models.py:25-40`; `docs/build-plan/04-rest-api.md:281-287`). The renderer instead declares `variant_id`, `label`, and `installed` (`ui/src/renderer/src/features/tts/useTtsJob.ts:43-49`) and converts `item.variant_id` to a string (`TTSPage.tsx:291-305`). With a real catalog row, every row therefore gets the identifier string `"undefined"`; Get/Load send that value and runtime progress can never bind to the real id. The controls also ignore `is_downloaded`, current loaded id, and download state—their only disable condition is `busy` (`TTSPage.tsx:298-323`), contrary to `ENABLED_WHEN`. The E2E seam masks the defect by returning `{ variant_id, label }` rows (`ui/tests/e2e/tts-generate.test.ts:153-169`), while the unit oracle merely searches for the token `variant_id` (`ui/tests/unit/tts-page.test.ts:295-304`). This violates AC-22.15–22.17, `CATALOG_ITEMS`, `RUNTIME_BIND`, and the plan-review lock to consume catalog items as-is. **Required correction:** type and render the real wire fields (`item.id`, `item.name`, `item.is_downloaded`, status `memory_bytes`), enforce the named Get/Load enablement, validate the download body through its strict schema, and make the seam/tests use the canonical API shape. | High |
| **F2 — Paste does not implement the required caret insertion or empty-clipboard no-op.** The click handler always appends clipboard text to the end (`setText(prev => prev + clip)`), never reads `selectionStart`/`selectionEnd`, and always calls `PUT /settings/tts` even when `clip === ''` (`ui/src/renderer/src/features/tts/TTSPage.tsx:179-191`). AC-22.4 and `PASTE` require insertion at the textarea caret (append only when no selection) and an empty clipboard to cause no settings write (`implementation-plan.md:117-119,289-290`). The unit test checks only that the IPC channel exists (`ui/tests/unit/tts-page.test.ts:129-139`), and W2-5 checks only the IPC ledger (`ui/tests/e2e/tts-generate.test.ts:294-320`), so both pass while the user-visible behavior is wrong. **Required correction:** insert/replace at the current selection, update the caret deterministically, clear file metadata only for nonempty paste, make empty clipboard a true no-op, and assert text plus exact settings-write behavior. | High |
| **F3 — The Generate/Cancel state machine omits the valid `Pending` state.** `JOB_STATUSES` does not include `Pending`; Generate is blocked only for `Generating`, and Cancel is enabled only for `Generating` (`ui/src/renderer/src/features/tts/tts-controls.ts:1-31`). The approved `ENABLED_WHEN` contract blocks Generate for both `Pending` and `Generating` and enables Cancel for both (`implementation-plan.md:98-100,120-123,295-296`); `Pending` is a real domain status (`packages/core/src/avkit_core/domain/enums.py:41-48`). A Pending response therefore re-enables Generate and disables Cancel, allowing a duplicate request that the backend rejects while withholding the valid cancel action. The tests assert only Generating/Idle (`ui/tests/unit/tts-page.test.ts:207-220`), and the E2E seam forces the create response directly to `Generating` (`ui/tests/e2e/tts-generate.test.ts:130-142`). **Required correction:** include Pending in the status/control contract and add unit plus Electron assertions for both enablement states. | High |
| **F4 — Preview never forwards the persisted `chunk_max_chars` setting.** The plan makes `chunk_max_chars` a read-only TTS setting for this MEU and requires it in `PREPARE_BODY` when present (`implementation-plan.md:94-95,119,131-134,268-269,292`). `useTtsSettings` omits the field (`ui/src/renderer/src/features/tts/useTtsJob.ts:107-119`), and the page always calls `postPrepare(text, enabledSteps)` with no third argument (`TTSPage.tsx:236-249`). A non-default saved chunk size is consequently ignored. AC-22.6 tests only the two-key default body, and the E2E settings fixture omits the leaf (`ui/tests/unit/tts-page.test.ts:154-165`; `ui/tests/e2e/tts-generate.test.ts:102-111`). **Required correction:** hydrate the existing setting, pass it to preview, and test both absent/default and explicit non-default values. | Medium |
| **F5 — Editor persistence is immediate per keystroke instead of debounced.** The textarea's `onChange` invokes `persistLeaf` on every input event (`ui/src/renderer/src/features/tts/TTSPage.tsx:143-155`), although `RESUME_TEXT` requires a debounced `PUT { input_text }` (`implementation-plan.md:134,300`). Rapid typing can create overlapping writes and allow an older request to finish last, leaving stale persisted text. The AC-22.14 test only searches source text for `/settings/tts` and `input_text` (`ui/tests/unit/tts-page.test.ts:279-284`), so it does not exercise persistence timing or final-value round trip. **Required correction:** debounce/cancel superseded writes and assert the final persisted body after rapid edits, file load, and paste. | Medium |
| **F6 — The 204 E2E stubs throw before the success continuation, while W2-5 asserts only pre-response ledgers.** Both DELETE TTS and model unload construct `new Response('', { status: 204 })` (`ui/tests/e2e/tts-generate.test.ts:147-152,186-189`). The platform rejects a body on 204; a focused semantic check reproduced `TypeError: Response constructor: Invalid response status code 204` (`C:/Temp/av-kit/review-r1-response-204.txt`). W2-5 then checks only that matching requests appeared in `__e2eCalls` (`tts-generate.test.ts:309-332`), so it remains green even though `cancelJob`/`postUnload` never reach invalidation. **Required correction:** use `new Response(null, { status: 204 })` and assert the post-success UI/query outcome, not only request issuance. | Medium |

## Contract Verification

| Contract | Result | Evidence |
|---|---|---|
| AC-22.1 `TTS_HOME` | Pass | `/tts` maps to `TTSPage` (`ui/src/renderer/src/router.tsx:39-42`); W2-1/W2-2 reached the compiled Electron page (`tts-generate.test.ts:202-219`; six-test receipt). |
| AC-22.2 text statistics | Pass | Exact word/sentence/duration helpers use 150 WPM and speed (`tts-stats.ts:1-16`), with value assertions (`tts-page.test.ts:101-110`). |
| AC-22.3 `FILE_LOAD_OUT` | Pass | Main IPC returns `{ text, basename }` after dialog/extension/size checks (`ui/src/main/ipc.ts:303-316`); renderer stores basename metadata (`TTSPage.tsx:159-175`). |
| AC-22.4 paste/clipboard | **Fail — F2** | IPC reads Electron clipboard, but page append/empty semantics violate `PASTE` (`TTSPage.tsx:179-191`). |
| AC-22.5 prepare steps/defaults | Pass | Eleven steps exist and only `chapter_markers` is excluded by default (`tts-prepare.ts:1-19`); page renders all steps (`TTSPage.tsx:206-223`). |
| AC-22.6 prepare body/preview | **Fail — F4** | Strict body and split preview exist, but `chunk_max_chars` is never read or passed (`tts-commands.ts:24-30,72-88,123-136`; `TTSPage.tsx:236-249`). |
| AC-22.7 generate body/job output | Pass | Strict body excludes `output_path`/`lang_code`; job type contains preview/hash rather than full text (`tts-commands.ts:32-42,138-151`; `useTtsJob.ts:12-27`). |
| AC-22.8 polling | Pass | Query v5 callback reads `query.state.data`; job/runtime use 1000/5000 ms and no list route is introduced (`useTtsJob.ts:52-74,98-104`). |
| AC-22.9 enablement/cancel | **Fail — F3** | DELETE path is correct, but Pending enablement is absent (`tts-controls.ts:1-31`; `tts-commands.ts:138-160`). |
| AC-22.10 segment progress | Pass | Page binds `segments_done/segments_total` from the polled job (`TTSPage.tsx:490-494`). |
| AC-22.11 voices/language | Pass | `{ items }` is unwrapped, languages derive from `VoiceOut.language`, and voice settings writes omit `lang_code` (`useTtsJob.ts:77-81`; `tts-voices.ts:1-17`; `TTSPage.tsx:334-362`). |
| AC-22.12 speed/format | Pass | Slider uses 0.5/2.0/0.1 and MP3/WAV uses `SelectInput` (`TTSPage.tsx:365-411`). |
| AC-22.13 output default/browse | Pass | `~/Documents` fallback, directory IPC, and isolated `{ output_path }` PUT are present; Generate omits the path (`TTSPage.tsx:33-34,102-106,421-458`). |
| AC-22.14 resume text | **Fail — F5** | GET hydration exists, but required debounced persistence does not (`TTSPage.tsx:85-111,143-155`). |
| AC-22.15 model status/unload | **Fail — F1/F6** | Status/unload calls exist, but renderer names `memory_mb` instead of canonical `memory_bytes`, does not display memory, and the E2E 204 success path throws (`useTtsJob.ts:29-34`; `TTSPage.tsx:255-290`). |
| AC-22.16 catalog/runtime bind | **Fail — F1** | Real catalog uses `id`/`is_downloaded`; renderer and seam use `variant_id`/invented fields. |
| AC-22.17 load body/device | **Fail — F1** | Load body schema/device enum is strict, but the id supplied from real catalog rows is `"undefined"` and Load enablement ignores download/loaded state (`tts-commands.ts:44-49,94-99`; `TTSPage.tsx:291-323`). |
| AC-22.18 error surface | Pass for action paths | `run` and persisted-leaf paths render caught `ApiError`/`Error` in-page; palette errors dispatch the shared error event (`TTSPage.tsx:75-83,113-131,137-141`; `tts-commands.ts:224-260`). |
| AC-22.19 palette delivery | Pass | Registry dispatches TTS events without its own fetch path, and always-mounted AppShell calls `TTS_COMMANDS` (`commandRegistry.ts:219-235`; `AppShell.tsx:100-105`). |
| AC-22.20 local controls/scope | Pass | Required page-local control IDs exist; Settings models-directory Browse is not introduced in the TTS feature. |
| AC-22.21 output opens | Pass | Open file/folder call the existing allowlisted IPC methods and are disabled without a target (`tts-commands.ts:195-203`; `TTSPage.tsx:498-530`). |
| AC-22.22 Wave 2 E2E | **Fail in lifecycle rigor — F1/F2/F6** | Six compiled-Electron cases and the census pass, but the seam's catalog contract is false and several action assertions prove only request issuance. |
| AC-22.23 G36/scope/no placeholders | Pass | Named anti-placeholder and G36 receipts are empty apart from the RTK notice; OpenAPI no-drift is clean and Python regression reports 298 passed. |
| AC-22.24 tokens/presets/selects | Pass | Status classes use theme tokens, presets are exactly 0.8/1.0/1.1, and new selects use `SelectInput` (`tts-controls.ts:11-19`; `TTSPage.tsx:262-277,334-344,382-411`). |

## IR-5 Test Rigor Audit

| Test file | Grade | Rationale |
|---|---|---|
| `ui/tests/unit/tts-page.test.ts` | 🔴 Weak | Several helper tests assert exact values, but most integration ACs are source-token searches. The suite remains green with the real catalog mismatch, incorrect paste behavior, missing Pending state, missing chunk setting, and missing debounce (`:112-139,154-165,207-220,269-304`). |
| `ui/tests/e2e/tts-generate.test.ts` | 🔴 Weak | It launches real compiled Electron, but the seam invents the model response shape, Paste is checked only through an IPC ledger, and invalid 204 responses plus ledger-only checks allow action continuations to fail invisibly (`:53-190,271-333`). |
| `ui/tests/unit/secret-paths.test.ts` | 🟢 Strong | It invokes the real IPC handler and asserts exact denials, zero side effects, max-byte truncation, and the exact `{ text, basename }` success value (`:4-63`). |
| `ui/tests/e2e/test-ids.ts` | n/a | Registry data rather than an executable test; the required identifiers are present and the census passes. |

## Checklist Results

| Check | Result | Evidence |
|---|---|---|
| IR-1 Live runtime evidence | **Fail at the GUI/API integration seam** | Compiled Electron ran six tests, but every TTS/model/settings request is overridden. The separate 298-test Python receipt proves backend regression stability, not renderer compatibility; F1 demonstrates the untested wire mismatch. |
| IR-2 Stub behavioral compliance | N/A | MEU-22 adds no repository/UoW stub. The E2E seam is reviewed as a test double under IR-5 and fails contract fidelity in F1/F6. |
| IR-3 Error mapping completeness | Pass / unchanged backend | FastAPI routes were scope-locked and OpenAPI no-drift is clean. UI action failures are surfaced through the in-page banner/shared error event. |
| IR-4 Fix generalization | N/A, round 1 | No prior execution-review correction exists. Direct reads covered all TTS feature files, main/preload IPC, routing/palette wiring, scoped tests, and current API schemas. |
| IR-5 Test rigor audit | **Fail** | Both primary MEU-22 suites are 🔴 because they demonstrably permit the High failures to pass green; see the file-level audit. |
| IR-6 Boundary validation coverage | **Fail** | Prepare/generate/load/settings schemas are strict, but `postDownload` builds `{ variant_id }` without the planned strict download schema (`tts-commands.ts:162-168`), and the catalog response is not validated against its real shape (F1). IPC boundaries remain strict. |
| IR-7 Deferral and AC integrity | **Fail in lifecycle evidence; pass in IDs/scheduling** | Handoff rows cover AC-22.1–22.24 and MEU-23–25 are registered. Integration AC-22.4, .6, .9, .15–.17, and .22 are nevertheless marked complete despite false-green or missing lifecycle proof. |

## Adversarial Verification

| Check | Result | Evidence |
|---|---|---|
| AV-1 Failing-then-passing proof | Pass | Saved JSON contains 24 total/failed tests with 24 distinct AC-22.* names; the current helper independently returned `PASS: RED_ORACLE ui` (`C:/Temp/av-kit/review-r1-red-oracle-check.txt`). |
| AV-2 No bypass hacks | Pass for skip/only; fail for oracle safety nets | G36 is clean, but the fictional seam and request-ledger-only assertions are functional bypasses for F1/F2/F6. |
| AV-3 Changed paths exercised by assertions | **Fail** | Real catalog parsing/gating, caret/empty paste, Pending controls, chunk setting propagation, debounce/final persistence, and 204 success continuations lack discriminating assertions. |
| AV-4 No skipped/xfail masking | Pass | Named G36 receipt is clean; no scoped test is skipped or `.only`. |
| AV-5 No unresolved placeholders | Pass | Named anti-placeholder receipt is clean for the scoped product sources. |
| AV-6 Source-backed criteria | Pass | Findings cite the approved plan/named sets and existing REST/domain contracts; no MEU-23–25 behavior was pulled forward. |

## Evidence and Commands

- Read the complete review workflow/template, peer exemplar, roles, architecture/testing canon, plan, task, MEU-22 handoff, all TTS feature sources, scoped IPC/routing/palette sources, scoped tests, census helper, model schemas/routes, and relevant build-plan/SSOT state.
- Hash/inventory audit confirmed all user-named receipts exist. The saved results report:
  - FAIL_TO_PASS JSON: 24 total, 24 failed, 24 distinct AC-22.* assertion names; independent `RED_ORACLE` helper pass.
  - `ui-green-meu-22.txt` and `ui-verify.txt`: 25 files / 141 Vitest tests passed and Electron build completed; the command chain's tsc/eslint stages produced no failure output.
  - `e2e-control-census.txt`: `PASS: E2E_CONTROL_CENSUS`.
  - `e2e-wave2.txt`: W2-1…W2-6, 6 passed in compiled Electron.
  - `pytest-p6-regression.txt`: 298 passed, 1 warning.
  - `openapi-check.txt`, `anti-placeholder-meu-22.txt`, and `g36-meu-22.txt`: canonical empty output apart from the RTK notice.
- Ran focused read-only contract searches comparing renderer types/fixtures to current FastAPI schemas and settings/domain state; receipts: `C:/Temp/av-kit/review-r1-model-contract-numbered.txt`, `review-r1-gap-census.txt`, and `review-r1-routing-palette.txt`.
- Ran a read-only Node semantic check proving the invalid 204 response constructor (`C:/Temp/av-kit/review-r1-response-204.txt`).
- Did not relaunch Electron; the user-designated Playwright receipt was sufficient to establish what ran, and source/API comparison proved why those tests false-pass the reported defects.

## Out-of-Contract Observations

None.

## Verdict

`changes_required` — F1, F2, and F3 are evidence-backed High Functionality-First failures of AC-22.4, AC-22.9, and AC-22.15–22.17. The genuine 141-test and six-Electron-test green receipts do not override the current file/API mismatch because their oracles reproduce or omit the failing cases. F4–F6 are additional Medium contract/test-rigor gaps that should be corrected in the same MEU-22 correction pass.

## Follow-Up

- Route corrections through `/execution-corrections` for MEU-22 only; do not start MEU-23–25 or rewrite FastAPI/MCP.
- Correct the renderer to the established API contracts and add discriminating unit/Electron assertions for every finding.
- Re-run the scoped UI gate, census, TTS Playwright wave, Python regression, and OpenAPI check, then append Round 2 to this same rolling review file for independent recheck.

## Round 2 Recheck — 2026-08-20

### Intent Anchor

This recheck verifies that the six Round 1 defects no longer prevent the TTS editor and Model Manager from honoring the approved REST/UI contracts in compiled Electron. The current implementation closes every High runtime defect and the three Medium runtime defects; the remaining weakness is non-blocking test rigor around post-action state and several integration-only behaviors.

### Prior Finding Closure

| Finding | Recheck result | Evidence |
|---|---|---|
| F1 — catalog contract, enablement, and memory | ✅ Closed | The renderer consumes canonical `id`, `name`, `format`, `precision`, `size_bytes`, `path`, and `is_downloaded` fields (`useTtsJob.ts:45-53`); renders `memory_bytes` (`TTSPage.tsx:307-314`); derives Get/Load enablement from download/loaded state (`tts-controls.ts:38-50`; `TTSPage.tsx:345-390`); and validates download input through a strict Zod body (`tts-commands.ts:51-55,107-109,172-178`). The Electron seam now uses the same catalog and status shapes (`tts-generate.test.ts:29-80,180-203`). |
| F2 — caret paste and empty no-op | ✅ Runtime closed; coverage note | Nonempty clipboard text replaces the current selection, restores the caret after the inserted text, clears file metadata, and schedules persistence; an empty string returns before any state or settings write (`TTSPage.tsx:219-240`). The unit oracle still checks source tokens rather than the rendered text/caret and exact PUT count (`tts-page.test.ts:129-139`). |
| F3 — Pending enablement | ✅ Closed | `Pending` is a declared job status; Generate blocks and Cancel enables for both `Pending` and `Generating` (`tts-controls.ts:1-35`). Exact unit assertions cover both Pending transitions (`tts-page.test.ts:211-221`). |
| F4 — `chunk_max_chars` prepare propagation | ✅ Runtime closed; coverage note | The settings query and hydration include the read-only leaf (`useTtsJob.ts:110-123`; `TTSPage.tsx:97-126`), Preview forwards it (`TTSPage.tsx:286-298`), and the strict prepare body includes it only when supplied (`tts-commands.ts:24-30,78-94`). Unit assertions cover absent and explicit `500` bodies (`tts-page.test.ts:155-168`), although the Electron fixture still omits the non-default leaf. |
| F5 — debounced `input_text` persistence | ✅ Runtime closed; coverage note | Editor edits, file loads, and nonempty paste all route through one 300 ms timer; superseded timers are cleared and unmount cleanup is present (`TTSPage.tsx:43,51-52,128-163,185-208,219-240`). The unit oracle remains source-token based and does not assert the final PUT body after rapid edits (`tts-page.test.ts:286-291`). |
| F6 — valid 204 responses and continuation | ✅ Runtime defect closed; coverage note | Both Electron stubs now construct `Response(null, { status: 204 })` and mutate their backing state before returning (`tts-generate.test.ts:171-178,211-213`); the shared client treats 204 as void before returning (`api.ts:77-86`). A focused Node check confirms null-body 204 succeeds while an empty-string body throws (`C:/Temp/av-kit/review-r2-response-204.txt`). W2-5 still proves request issuance only and does not assert the post-cancel `Cancelled` or post-unload `No model loaded` UI/query outcome (`tts-generate.test.ts:296-358`). |

### Round 2 Findings

No blocking findings. The structured findings array is empty.

### Test Rigor Recheck

| Test file | Grade | Round 2 result |
|---|---|---|
| `ui/tests/unit/tts-page.test.ts` | 🔴 Weak for the corrected integration paths | Pending and prepare-body helpers now have discriminating value assertions, but paste behavior, page-level chunk propagation, debounce/final persistence, and model rendering remain guarded mainly by source-token searches (`:129-139,155-168,286-314`). This is a Medium test-rigor correction note, not evidence of a current High runtime failure. |
| `ui/tests/e2e/tts-generate.test.ts` | 🟡 Adequate | The seam now matches the canonical model contracts and the supplied receipt proves six cases in compiled Electron. W2-5 remains ledger-oriented and does not assert the cancel/unload success state (`:296-358`). |
| `ui/tests/unit/secret-paths.test.ts` | 🟢 Strong | Unchanged from Round 1; it invokes the real IPC handler and asserts exact success and denial behavior. |

### Checklist Results

| Check | Result | Evidence |
|---|---|---|
| IR-1 Live runtime evidence | Pass within the approved Wave 2 boundary | `e2e-wave2.txt` is newer than the E2E source and records a compiled Electron build plus W2-1…W2-6, 6 passed. Live HF/Kokoro remains intentionally outside the seam boundary. |
| IR-2 Stub behavioral compliance | Pass with note | The model catalog/status/download and 204 seams now honor the relevant REST shapes and state mutations; post-action UI state is not asserted. |
| IR-3 Error mapping completeness | Pass / unchanged | Backend routes were scope-locked; renderer action failures continue to surface through `ApiError` handling. |
| IR-4 Fix generalization | Pass | The recheck covered production code, both scoped test files, the current API contract cited by Round 1, and all six prior finding classes. |
| IR-5 Test rigor audit | Pass for approval with correction note | No false API shape or invalid Electron 204 constructor remains. Source-token and ledger-only assertions leave the non-blocking weaknesses recorded above. |
| IR-6 Boundary validation coverage | Pass | Prepare, generate, load, download, and settings writes use strict Zod schemas; Round 1's missing strict download body is closed (`tts-commands.ts:24-66,96-109`). |
| IR-7 Deferral and AC integrity | Pass with lifecycle note | All AC IDs remain represented and no scope deferral changed. Corrected runtime paths are present; the noted assertions should be strengthened without reopening a High product defect. |

### Adversarial Verification

| Check | Result | Evidence |
|---|---|---|
| AV-1 Failing-then-passing proof | Pass | Existing Red evidence remains intact; the fresh `ui-verify.txt` reports 25 files / 141 tests passed after the correction timestamps. |
| AV-2 No bypass hacks | Pass | The fictional catalog shape and invalid 204 constructors identified in Round 1 are gone from the Electron seam. |
| AV-3 Changed paths exercised by assertions | Partial, non-blocking | Pending and prepare-body changes have exact assertions; F2/F5 and post-204 UI continuation retain the test-rigor notes above. |
| AV-4 No skipped/xfail masking | Pass | The supplied scoped verification remains green and no Round 2 evidence indicates skip/only masking. |
| AV-5 No unresolved placeholders | Pass | No placeholder was introduced on the reviewed correction paths. |
| AV-6 Source-backed criteria | Pass | Every closure maps directly to Round 1 F1–F6 and the approved named contracts (`PASTE`, `ENABLED_WHEN`, `CATALOG_ITEMS`, `PREPARE_BODY`, `RESUME_TEXT`, `VOID_204`). |

### Evidence and Commands

- Preferred the user-named receipts and did not relaunch Electron: `C:/Temp/av-kit/ui-verify.txt` (25 files / 141 tests passed), `e2e-wave2.txt` (compiled Electron, 6 passed), and `e2e-control-census.txt` (`PASS: E2E_CONTROL_CENSUS`). Receipt timestamps are later than the correction source timestamps.
- Read the corrected TTS renderer sources, unit/E2E tests, Round 1 review, correction handoff section, plan contracts, and current API client behavior with numbered exact-evidence receipts under `C:/Temp/av-kit/review-r2-*.txt`.
- Ran a focused, non-Electron Node semantic check for null-body versus empty-body 204 construction: `C:/Temp/av-kit/review-r2-response-204.txt`.
- `git diff` remains unavailable because `P:/av-kit` is not a Git repository. A before/after SHA-256 comparison was used to prove the protected plan, handoff, product, and test files were not modified during this review.

### Non-Blocking Correction Notes

- Add discriminating rendered-behavior assertions for caret/empty paste and the final debounced `{ input_text }` body.
- Make W2-5 assert the post-204 cancel and unload UI/query outcomes, not only request-ledger entries.
- Exercise a non-default `chunk_max_chars` through the Electron settings fixture and assert the prepare request body.

### Verdict

`approved` — F1–F6 no longer expose a High/Critical runtime or contract failure. The surviving assertion gaps are Medium test-rigor notes and therefore do not meet this workflow's blocking threshold; frontmatter findings are intentionally `[]`.

### Residual Risk

The current source implements the reviewed behaviors and the supplied receipts are fresh, but W2-5 could still false-pass a future regression after a successful cancel/unload response because it does not observe the resulting UI/query state. No live HF/Kokoro integration was run, consistent with the approved Wave 2 seam boundary.
