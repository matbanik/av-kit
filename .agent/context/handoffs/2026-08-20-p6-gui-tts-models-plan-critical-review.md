---
date: "2026-08-20"
review_mode: "plan"
round: 4
review_round: 4
target_plan: "docs/execution/plans/2026-08-20-p6-gui-tts-models/implementation-plan.md"
verdict: "approved"
findings_count: 0
findings: []
summary: "Round 4 approved. The complete Round-3 census is dispositioned, live quoted-token probes now fail, executable installer/gate probes pass, and F2-F4 remain closed."
template_version: "2.1"
requested_verbosity: "standard"
agent: "Codex GPT-5.6-sol"
---

# Critical Review: p6-gui-tts-models

> **Review Mode**: `plan`
> **Latest Round**: 4
> **Latest Verdict**: `approved`

## Round 1 Review (2026-08-20)

## Intent Anchor

Executing this plan is supposed to deliver the complete MEU-22 `/tts` page and Model Manager while keeping Wave 2 isolated from live Hugging Face/Kokoro work and preserving the approved FastAPI, MCP, and chrome surfaces. The product slice is correctly scoped, but the current plan can pass its own E2E gates without proving the live-adapter barrier or several control bindings, and its file-load chain cannot produce the required basename metadata.

## Findings

| # | Severity | Confidence | Finding | File:Line | Recommendation | Status |
|---|----------|------------|---------|-----------|----------------|--------|
| F1 | High | High | **PR-4/PR-8 — `E2E_SEAM_PROOF` can pass without installing the production-effective, fail-closed renderer seam.** The plan requires a pre-app `window.fetch` override, `__e2eSeamInstalled`, and 599 fail-closed handling for every unfulfilled `/tts*`, `/models*`, and `/settings/tts*` request without calling original `fetch`. The sole helper verifies only that the W2-4 source contains six tokens (`addInitScript`, `__e2eSeamInstalled`, `__e2eCalls`, `E2E_SEAM_UNHANDLED`, `enabled_steps`, `reload`). It never requires `window.fetch` assignment, any protected prefix, the 599 response, or the no-original-fetch branch. A W2-4 test can therefore place those strings in constants/assertions, exercise the UI against a live backend, and satisfy both the census and Playwright while Generate/Get/Load still reach Kokoro or Hugging Face. This is the concrete false-pass prohibited by downloader RULE-2 and the Materiality Gate. | `implementation-plan.md:147-155`, `implementation-plan.md:305`; `assert-e2e-control-census.ps1:116-126`; `ui/src/renderer/src/lib/api.ts:21-27`, `:60-72`; `docs/execution/reflections/2026-08-20-p6-gui-downloader-reflection.md:22-31`, `:96-99` | Make the helper validate the executable seam shape: a pre-app `window.fetch = ...` override, all three protected prefix classifiers, 599 `E2E_SEAM_UNHANDLED`, and a branch that never delegates protected requests to original fetch. Add a negative runtime oracle that issues an unhandled protected request and asserts 599 plus zero live-backend/adaptor calls; keep `page.route` non-probative. | open |
| F2 | High | High | **PR-4/PR-8 — `E2E_CONTROL_CENSUS` does not enforce its named `E2E_ACTUATE` contract.** The helper requires Load File, Paste, Open File, and Open Folder clicks but only checks for a generic `__e2eIpc` token; any one unrelated ledger entry can satisfy all four. It checks `/models/download` and `/models/load` as free strings with no bound Get/Load actuation, and it never requires a `voice-card` locator or any W2-5 locator/assertion for language, format, or device. Those three select IDs need only appear in `test-ids.ts`; the required voice-card is absent from the helper's ID census entirely. The test suite can therefore pass with Paste still disconnected from `readClipboardText`, model Get/Load unbound, or the voice/select controls missing, materially under-delivering the TTS page and Model Manager. | `implementation-plan.md:141-143`, `implementation-plan.md:149`, `implementation-plan.md:153`, `implementation-plan.md:220-221`, `implementation-plan.md:240-241`; `assert-e2e-control-census.ps1:53-66`, `:129-153` | Bind each W2-5 control to its own observable in the same case block: per-channel IPC ledger checks, Get/Load clicks tied to their exact REST entries, a voice-card click tied to `PUT /settings/tts { voice }`, and positive locator/interaction checks for language, format, and device. Add `voice-card` to the registered/censused IDs. | open |
| F3 | High | High | **PR-8 / Boundary Input Contract — `FILE_LOAD` has no producer for the required basename.** AC-22.3 correctly forbids a renderer-supplied path and requires `source_path` to be the selected file's basename. In current production code, main receives the dialog path but returns only the sliced file body; the renderer contract is `Promise<string>`. The plan names no safe response schema carrying `{ text, basename }`, does not list `env.d.ts`/preload contract updates, and its negative oracle checks only the request payload and generated `source_path`. The trace therefore ends before any component can know the actual basename: execution must either invent a filename, leak/use a full path, or silently omit the required metadata. | `implementation-plan.md:74`, `implementation-plan.md:115`, `implementation-plan.md:275`, `implementation-plan.md:286`, `implementation-plan.md:340-352`; `ui/src/main/ipc.ts:297-310`; `ui/src/main/index.ts:272-279`; `ui/src/renderer/src/env.d.ts:25`; `docs/build-plan/06-gui.md:106`, `:894` | Define the existing `read-text-file` channel's safe success response (for example, text plus basename only), update the renderer/preload type surface and affected tests, and add a negative oracle proving the full selected path never crosses IPC while the exact basename reaches `TTSGenerateIn.source_path`. No new channel is needed. | open |
| F4 | Low | High | **PR-5/PR-7/PR-9 — the three-ONNX catalog statement is stale and repeated.** Current `SEED_VARIANTS` and the GUI spec both include PyTorch FP32 plus three ONNX rows. The plan repeatedly cites only `engine.py:25-27` and labels a PyTorch row invented. This is clerical rather than blocking because the operative `CATALOG_ITEMS` rule says to render `/models/available` items as-is, which yields the correct generic behavior. | `implementation-plan.md:76`, `implementation-plan.md:126`, `implementation-plan.md:299`, `implementation-plan.md:326`, `implementation-plan.md:371`; `packages/infrastructure/src/avkit_infra/database/engine.py:23-28`; `docs/build-plan/06-gui.md:845` | Make `CATALOG_ITEMS` the sole statement: render every API item as-is and never hardcode/filter rows. Remove the three-ONNX and “PyTorch is invented” restatements; fixtures should include the current four seeded rows or explicitly test arbitrary API rows. | open |

## Scope

**Targets reviewed**:

- `docs/execution/plans/2026-08-20-p6-gui-tts-models/implementation-plan.md`
- `docs/execution/plans/2026-08-20-p6-gui-tts-models/task.md`
- `docs/execution/plans/2026-08-20-p6-gui-tts-models/assert-red-oracle.ps1`
- `docs/execution/plans/2026-08-20-p6-gui-tts-models/assert-handoff-markers.ps1`
- `docs/execution/plans/2026-08-20-p6-gui-tts-models/assert-e2e-control-census.ps1`

**Canonical authority sampled**: `docs/build-plan/06-gui.md` TTS/Model Manager/Settings/deferred sections; `docs/build-plan/04-rest-api.md` TTS/models routes and DTOs; `docs/build-plan/gui-actions-index.md`; grouping Session 10; MEU registry; current TTS/models routes and schemas; current IPC/preload/renderer API surfaces; model seeds and voice labels; G30 `SelectInput`; downloader/transcript seam carry-forward evidence.

**Mode confirmation**: plan review. Every task row is unchecked; `TTSPage.tsx`, `tts-generate.test.ts`, the MEU-22 implementation handoff, and the rolling implementation review are absent. The three plan-local helper scripts are planning artifacts, not implementation evidence. This workspace snapshot has no `.git` directory, so PR-2 used direct file state rather than a git diff.

**Out of scope for this review**: product implementation, MEU-23-25, FastAPI/MCP rewrites, chrome changes, and runtime execution of planned UI/E2E tests.

## Requested Contract Confirmations

| Contract | Result | Evidence |
|----------|--------|----------|
| `E2E_NO_LIVE_HF` uses renderer fetch seam, gate, and fail-closed prefixes; `page.route` is not proof | fail | The plan states the right contract (`implementation-plan.md:147-155`), but F1 demonstrates that the executable proof can pass without it. |
| `CLIPBOARD_READ` completes the existing channel and AC-22.4 has negative oracles | pass | Current handler is the empty stub (`ipc.ts:289-290`); plan adds `IpcDeps.readClipboard` → `clipboard.readText()` and explicitly rejects both the stub and `navigator.clipboard` (`implementation-plan.md:75`, `:116`, `:287`, `:345-346`). |
| `JOB_POLL` does not invent a TTS list envelope | pass | Live router exposes only `GET /tts/{id}`; plan consistently polls that job and rejects `GET /tts`/`{ items, processor }` (`implementation-plan.md:72`, `:99`, `:291`; `routes/tts.py:54-96`). |
| `CATALOG_ITEMS` does not hardcode/invent product rows | pass with clerical correction | Operative rule is API items-as-is; F4 corrects the stale assertion that current seeds exclude PyTorch. |
| `LANG_FILTER` uses `VoiceOut.language` and exposes no `lang_code` control | pass | `VoiceOut` has language but no lang_code; plan derives unique server labels and rejects a user-set field (`implementation-plan.md:77`, `:124`, `:294`; `schemas/tts.py:58-70`; `voices.py:68-78`). |
| `SETTINGS_LEAVES` excludes MEU-23 editors | pass | Writable leaves are limited to input/voice/speed/format/output/device; `chunk_max_chars` is read-only here and `models_directory`/chunk editing is deferred to scheduled MEU-23 (`implementation-plan.md:78`, `:130-131`, `:363-364`; `meu-status.yaml:673-684`). |
| Cancel uses `DELETE /tts/{id}` and no transcript-style Stop control | pass | Plan, action index, API canon, and live router agree on `cancel-btn`/`tts:cancel`/DELETE 204 (`implementation-plan.md:73`, `:120`, `:292`; `gui-actions-index.md:50`; `routes/tts.py:92-96`). |
| File load is dialog-only and renderer sends no path | fail | The request-side rule is correct, but F3 shows the response chain cannot produce basename-only metadata. |
| G30 selects use `SelectInput` | pass at plan-contract level | Language/format/device consistently name `SelectInput` (`implementation-plan.md:79`, `:221`, `:240`, `:244`, `:255`, `:295`, `:300`, `:307`); F2 separately blocks the E2E reachability proof. |
| PR-7 Out of Scope control C2 | pass with F4 Low note | MEU-23-25 are scheduled; MEU-16-18 are approved; deferred SSE/MCP Guard bases exist. The PyTorch basis is stale but the no-hardcoding scope is still inferable. |
| Sweep 8 invoked helper/tool existence | pass | All three `assert-*.ps1` scripts plus `tools/check_exec_review.py`, `tools/export_openapi.py`, `tools/meu_status.py`, and `tools/Invoke-CodexDispatch.ps1` exist. `tools/validate_closeout_artifacts.py` is absent exactly as the plan states and is not invoked. |
| Sweep 9 named-set discipline | fail (Low only) | Most repeated controls reference named owners; F4 is the surviving stale restatement cluster. |

## Commands Executed

Only read-only file inspection, `rg`, `Test-Path`, and line-count/census commands were used. Canonical receipts under `C:/Temp/av-kit/` include:

- `p6-plan-1.txt`, `p6-plan-2.txt`, `p6-plan-230-339.txt`, `p6-plan-340-459.txt`, `p6-task-1.txt`, `p6-task-2.txt`
- `p6-red-oracle-full.txt`, `p6-handoff-markers-full.txt`, `p6-e2e-census-full.txt`
- `p6-sweep8-test-path.txt`, `p6-sweep8-all-invoked-paths.txt`, `p6-sweep9-literals.txt`
- `p6-ipc-source-context.txt`, `p6-api-source-context.txt`, `p6-canon-source-context.txt`
- `p6-file-load-trace.txt`, `p6-file-load-producer-context.txt`, `p6-catalog-trace.txt`, `p6-seam-trace.txt`, `p6-clipboard-trace.txt`
- `p6-c2-meu-schedule.txt`, `p6-c2-deferred-basis.txt`, `p6-final-line-census.txt`

The plan-local helpers and product test suites were not executed because their planned TTS product/E2E/handoff inputs are correctly absent before implementation. Two optional shell probes failed safely and changed nothing: `git status` found no `.git` repository, and one redundant alignment command had a PowerShell quoting error; neither is used as verdict evidence.

## Checklist Results

### Information Retrieval (IR)

| Check | Result | Evidence |
|-------|--------|----------|
| Full explicit target set read | pass | Plan, task, and all three requested helper scripts were read in full. |
| All AC have source labels | pass | AC-22.1 through AC-22.24 use Spec, Local Canon, Research-backed, or named prior-rule sources. |
| Validation cells are exact commands | pass | Every task row has an explicit PowerShell command/receipt; F1-F2 concern material false-pass semantics, not missing command text. |
| BUILD_PLAN audit and post-MEU rows present | pass | SSOT/hub row 5 and H1/H2 handoff, independent review, reflection, metrics, and closeout rows are present and ordered. |
| Not-started state | pass | All task rows `[ ]`; TTS production/E2E/handoff/review outputs are absent. |

### Design Review (DR)

| Check | Result | Evidence |
|-------|--------|----------|
| DR-1 Claim-to-state match | fail | F4's catalog state claim contradicts current seeds and spec. |
| DR-2 Residual old terms | pass | Job/Cancel/language/settings terms consistently avoid transcript/list/lang_code/MEU-23 behavior. |
| DR-3 Downstream references | pass | Hub, registry, grouping completion, next command, handoff, review, reflection, and metrics updates are explicit. |
| DR-4 Verification robustness | fail | F1-F2 demonstrate material E2E false-passes. |
| DR-5 Evidence auditability | fail | F1's phrase-only source check is not proof that protected fetches are intercepted/fail-closed. |
| DR-6 Cross-reference integrity | fail | F3 omits the IPC response contract needed to reconcile dialog-only loading with basename metadata. |
| DR-7 Evidence freshness | pass | Live routes, schemas, IPC, seeds, voices, registry, grouping, and planned file absence were checked directly. |
| DR-8 Completion vs residual risk | pass | The plan makes no implementation-complete claim. |

### Plan Review (PR-1 through PR-9)

| Check | Result | Evidence |
|-------|--------|----------|
| PR-1 Plan/task alignment | pass | Same MEU-22-only scope, Red→Green→E2E→gate→handoff/review/H2 order, and exclusions. |
| PR-2 Not-started confirmation | pass | Direct file state and unchecked rows confirm implementation has not begun. |
| PR-3 Task contract completeness | pass | Every actionable row has task, owner, deliverable, validation, dependency/context, durable output, model, and status fields. |
| PR-4 Validation realism | fail | F1-F2 are demonstrated false-passing gates for materially missing safety/control behavior. |
| PR-5 Source-backed planning | fail | Most rules are sourced; F4 misstates its cited live canon, and F3 leaves a sourced behavior without a realizable boundary contract. |
| PR-6 Handoff/corrections readiness | pass | One MEU handoff and one rolling implementation review path are explicit. Round-2 blast-radius gate is not applicable to Round 1. |
| PR-7 Scope discipline C2 | pass with Low note | Scheduled deferrals and sourced exclusions pass; F4 is a clerical basis correction, not disguised missing work. |
| PR-8 Control reachability/totality | fail | F1-F3 identify a vacuous seam proof, unbound controls, and a dead-end basename chain. |
| PR-9 Single-statement discipline | fail (Low) | F4 repeats the stale catalog value around the otherwise-canonical `CATALOG_ITEMS` owner. |

## Out-of-Contract Observations

None.

## Open Questions / Assumptions

No human product decision is required. The corrections are determined by current local canon: preserve the existing IPC channel, return only safe basename metadata, render the available-model API envelope generically, and make the E2E helper prove the already-stated seam/control contracts.

## Follow-up Actions

1. Use `/plan-corrections` to make `E2E_SEAM_PROOF` validate the real renderer override, protected-prefix totality, 599 fail-closed behavior, and no-original-fetch branch.
2. Bind every W2-5 interactive control to its own REST/IPC/settings observable, including Paste, model Get/Load, voice selection, and all three selects.
3. Define and test the existing `read-text-file` success response carrying file text plus basename only; update the renderer type surface and file inventory.
4. Canonicalize `CATALOG_ITEMS` as API-items-as-is and remove the stale three-ONNX/PyTorch-invented restatements.
5. Re-submit the same plan folder for Round 2 with the required untruncated blast-radius census and per-hit dispositions.

## Verdict

`changes_required` — F1-F3 are evidence-backed High findings under PR-4/PR-8. As written, the plan can pass while live Hugging Face/Kokoro paths remain reachable, required TTS/Model Manager controls are unbound or absent, and file-origin basename metadata cannot be produced without violating the dialog-only boundary.

## Residual Risk

This was a static, findings-only plan review. Runtime product behavior remains unproven by design, and no product code or tests were changed. F4 is non-blocking under the Materiality Gate; the verdict is driven only by F1-F3.

## Corrections Applied (2026-08-20) — after Round 1

**Workflow**: `/plan-corrections` inside `/create-plan` §5b (parent loop wins over `plan-corrections.md` HARD STOP). Plan/task + plan-folder helper scripts only. No product code.
**Agent**: coordinator (implementer) — `corrections_applied`, never `approved`.
**Conflict flagged**: `plan-corrections.md` Step 7 / HARD STOP say timestamp-and-stop and do not chain into re-review; `create-plan.md` §5b requires blast-radius census then re-dispatch. Parent create-plan loop is followed. `harness.local.md` `plan_to_exec_gate: reviewer-auto` remains the execution gate after a later `approved`.

Round-1 findings F1–F4 addressed. None refuted. `task.md` frontmatter set to `status: "draft"` (unstarted convention).

| # | Sev | Status | Fix |
|---|-----|--------|-----|
| F1 | High | fixed | `E2E_SEAM_PROOF` now requires executable `window.fetch =`, prefixes `/tts` `/models` `/settings/tts`, status `599`, `new Response`, and rejects original-fetch on a protected-prefix line. Added `E2E_SEAM_NEG` (W2-4 token + `__e2e-unhandled` + 599). `page.route` stays non-probative. |
| F2 | High | fixed | `E2E_ACTUATE` binds each W2-5 control to its own IPC channel or REST path. Helper IDs add `voice-card`, `model-get-btn`, `model-load-btn`. Per-channel IPC (`readTextFile` / `readClipboardText` / `openPath` / `showItemInFolder` / `showDirectoryDialog`). Voice card click + `PUT /settings/tts` + `voice` key. G30 selects `toBeVisible`. |
| F3 | High | fixed | Named `FILE_LOAD_OUT` `{ text, basename }` on the existing `read-text-file` channel. Files Modified + WP-22b + task row 2 include `env.d.ts` and `preload.ts`. AC-22.3 negatives: path key, separators in success value, string-only IPC value. |
| F4 | Low | fixed | `CATALOG_ITEMS` is the sole catalog rule (API items as-is). Removed three-ONNX / “invent PyTorch” restatements. `SEED_VARIANTS` line range lives only on the named set. Spec-sufficiency “Catalog 3 vs mockup 4” replaced. |

### Declared variants swept

Old: `three ONNX`, `Invent a PyTorch catalog row`, `invent a PyTorch`, `invent PyTorch`, `engine.py 25-27`, `engine.py 25–27`, `status: "in_progress"`, `Promise<string>`, `Catalog 3 vs mockup 4`.
New / semantic: `FILE_LOAD_OUT`, `E2E_SEAM_NEG`, `window.fetch`, `model-get-btn`, `model-load-btn`, `voice-card`, `{ text, basename }`, `{ text: string, basename: string }`, `env.d.ts`, `preload.ts`, `__e2e-unhandled`, `engine.py 23`, `engine.py 23–28`, `status: "draft"`, `hardcode or filter`, `never hardcode`, `Hardcode or filter`, `SEED_VARIANTS`, `four rows`, `Catalog rows as-is`.
Remain (intentional “not the proof”): `page.route`.

Manifests: `C:/Temp/av-kit/census-p6-tts-r1-manifest.txt`, `C:/Temp/av-kit/census-p6-tts-r1b-manifest.txt`, `C:/Temp/av-kit/census-p6-tts-r1c-manifest.txt`.
Runners: `C:/Temp/av-kit/census-p6-tts-r1-run.txt`, `C:/Temp/av-kit/census-p6-tts-r1b-run.txt`, `C:/Temp/av-kit/census-p6-tts-r1c-run.txt`.

Blast-radius census: 9 old + 21 new + 1 remain = 31 sweeps. Zero-hit old receipts: 9. Nonzero raw `file:line` hits: 63 (r1) + 12 (r1b) + 2 (r1c) = 77. Each hit dispositioned below. No truncated `Select-Object -First` / `head`.

### Zero-hit old receipts (stale gone)

| Receipt | Hits | Disposition |
|---------|------|-------------|
| `C:/Temp/av-kit/census-p6-tts-r1-old-three-onnx.txt` | 0 | no three-ONNX claim |
| `C:/Temp/av-kit/census-p6-tts-r1-old-invent-pytorch-row.txt` | 0 | no Invent-a-PyTorch out-of-scope row |
| `C:/Temp/av-kit/census-p6-tts-r1-old-invent-a-pytorch.txt` | 0 | no invent-a-PyTorch prose |
| `C:/Temp/av-kit/census-p6-tts-r1-old-engine-25-en.txt` | 0 | no ASCII `engine.py 25-27` |
| `C:/Temp/av-kit/census-p6-tts-r1-old-engine-25-em.txt` | 0 | no en-dash `engine.py 25–27` |
| `C:/Temp/av-kit/census-p6-tts-r1-old-status-in-progress.txt` | 0 | no unstarted `in_progress` |
| `C:/Temp/av-kit/census-p6-tts-r1-old-promise-string.txt` | 0 | no `Promise<string>` file-load type |
| `C:/Temp/av-kit/census-p6-tts-r1-old-invent-pytorch-row-neg.txt` | 0 | no `invent PyTorch` |
| `C:/Temp/av-kit/census-p6-tts-r1b-old-catalog-3-vs-4.txt` | 0 | no Catalog-3-vs-mockup-4 sufficiency row |

### Per-hit disposition — `FILE_LOAD_OUT` (10)

Receipt: `C:/Temp/av-kit/census-p6-tts-r1-new-file-load-out.txt`

| # | file:line | Disposition |
|---|-----------|-------------|
| 1 | `task.md:45` | updated — Green row names `FILE_LOAD_OUT` + types |
| 2 | `implementation-plan.md:59` | updated — WP-22b |
| 3 | `implementation-plan.md:74` | updated — lock 5 |
| 4 | `implementation-plan.md:115` | updated — named-set definition |
| 5 | `implementation-plan.md:116` | confirmed-consistent — `FILE_LOAD` consumes the set |
| 6 | `implementation-plan.md:277` | updated — boundary inventory |
| 7 | `implementation-plan.md:288` | updated — AC-22.3 |
| 8 | `implementation-plan.md:347` | updated — `ipc.ts` Files Modified |
| 9 | `implementation-plan.md:348` | updated — `preload.ts` Files Modified |
| 10 | `implementation-plan.md:349` | updated — `env.d.ts` Files Modified |

### Per-hit disposition — `E2E_SEAM_NEG` (9)

Receipt: `C:/Temp/av-kit/census-p6-tts-r1-new-e2e-seam-neg.txt`

| # | file:line | Disposition |
|---|-----------|-------------|
| 1 | `assert-e2e-control-census.ps1:137` | updated — helper requires token |
| 2 | `task.md:46` | updated — row 3 |
| 3 | `implementation-plan.md:60` | updated — WP-22c |
| 4 | `implementation-plan.md:144` | updated — `E2E_CASES` W2-4 |
| 5 | `implementation-plan.md:154` | updated — named-set definition |
| 6 | `implementation-plan.md:157` | confirmed-consistent — `E2E_NO_LIVE_HF` |
| 7 | `implementation-plan.md:158` | confirmed-consistent — census owners |
| 8 | `implementation-plan.md:222` | confirmed-consistent — §4A |
| 9 | `implementation-plan.md:307` | updated — AC-22.22 |

### Per-hit disposition — `window.fetch` (4)

Receipt: `C:/Temp/av-kit/census-p6-tts-r1-new-window-fetch.txt`

| # | file:line | Disposition |
|---|-----------|-------------|
| 1 | `assert-e2e-control-census.ps1:120` | updated — executable assignment required |
| 2 | `implementation-plan.md:152` | confirmed-consistent — `E2E_SEAM` |
| 3 | `implementation-plan.md:153` | updated — `E2E_SEAM_PROOF` |
| 4 | `implementation-plan.md:307` | confirmed-consistent — AC-22.22 negative |

### Per-hit disposition — `model-get-btn` (6)

Receipt: `C:/Temp/av-kit/census-p6-tts-r1-new-model-get-btn.txt`

| # | file:line | Disposition |
|---|-----------|-------------|
| 1 | `assert-e2e-control-census.ps1:60` | updated — ID census |
| 2 | `assert-e2e-control-census.ps1:151` | updated — W2-5 REST bind |
| 3 | `implementation-plan.md:142` | updated — `WAVE2_EXTRA_TESTIDS` |
| 4 | `implementation-plan.md:155` | updated — `E2E_ACTUATE` |
| 5 | `implementation-plan.md:255` | updated — §4A Get testid |
| 6 | `implementation-plan.md:301` | updated — AC-22.16 |

### Per-hit disposition — `model-load-btn` (5)

Receipt: `C:/Temp/av-kit/census-p6-tts-r1-new-model-load-btn.txt`

| # | file:line | Disposition |
|---|-----------|-------------|
| 1 | `assert-e2e-control-census.ps1:60` | updated — ID census |
| 2 | `assert-e2e-control-census.ps1:152` | updated — W2-5 REST bind |
| 3 | `implementation-plan.md:142` | confirmed-consistent — EXTRA list |
| 4 | `implementation-plan.md:155` | confirmed-consistent — `E2E_ACTUATE` |
| 5 | `implementation-plan.md:255` | confirmed-consistent — §4A Load testid |

### Per-hit disposition — `voice-card` (6)

Receipt: `C:/Temp/av-kit/census-p6-tts-r1-new-voice-card.txt`

| # | file:line | Disposition |
|---|-----------|-------------|
| 1 | `implementation-plan.md:142` | updated — EXTRA list |
| 2 | `implementation-plan.md:155` | updated — `E2E_ACTUATE` PUT voice |
| 3 | `implementation-plan.md:243` | confirmed-consistent — §4A voice card |
| 4 | `assert-e2e-control-census.ps1:61` | updated — ID census |
| 5 | `assert-e2e-control-census.ps1:170` | updated — W2-5 click |
| 6 | `assert-e2e-control-census.ps1:171` | updated — PUT `/settings/tts` |

### Per-hit disposition — `{ text, basename }` (2)

Receipt: `C:/Temp/av-kit/census-p6-tts-r1-new-text-basename.txt`

| # | file:line | Disposition |
|---|-----------|-------------|
| 1 | `task.md:45` | updated — Green success schema |
| 2 | `implementation-plan.md:288` | updated — AC-22.3 observable |

### Per-hit disposition — `env.d.ts` (4)

Receipt: `C:/Temp/av-kit/census-p6-tts-r1-new-env-d-ts.txt`

| # | file:line | Disposition |
|---|-----------|-------------|
| 1 | `task.md:45` | updated — durable outputs + prose |
| 2 | `implementation-plan.md:59` | updated — WP-22b outputs |
| 3 | `implementation-plan.md:116` | updated — `FILE_LOAD` type surface |
| 4 | `implementation-plan.md:349` | updated — Files Modified |

### Per-hit disposition — `preload.ts` (3)

Receipt: `C:/Temp/av-kit/census-p6-tts-r1-new-preload-ts.txt`

| # | file:line | Disposition |
|---|-----------|-------------|
| 1 | `task.md:45` | updated — durable outputs + prose |
| 2 | `implementation-plan.md:59` | updated — WP-22b outputs |
| 3 | `implementation-plan.md:348` | updated — Files Modified |

### Per-hit disposition — `__e2e-unhandled` (2)

Receipt: `C:/Temp/av-kit/census-p6-tts-r1-new-e2e-unhandled.txt`

| # | file:line | Disposition |
|---|-----------|-------------|
| 1 | `assert-e2e-control-census.ps1:138` | updated — helper URL token |
| 2 | `implementation-plan.md:154` | updated — `E2E_SEAM_NEG` |

### Per-hit disposition — `engine.py 23–28` / `engine.py 23` (1)

Receipts: `C:/Temp/av-kit/census-p6-tts-r1-new-engine-23-28.txt`, `C:/Temp/av-kit/census-p6-tts-r1b-new-engine-py-23.txt`

| # | file:line | Disposition |
|---|-----------|-------------|
| 1 | `implementation-plan.md:127` | updated — sole line-range cite on `CATALOG_ITEMS` |

### Per-hit disposition — `status: "draft"` (2)

Receipt: `C:/Temp/av-kit/census-p6-tts-r1-new-status-draft.txt`

| # | file:line | Disposition |
|---|-----------|-------------|
| 1 | `task.md:5` | updated — unstarted convention |
| 2 | `implementation-plan.md:6` | confirmed-consistent — plan still draft |

### Per-hit disposition — `hardcode or filter` (2)

Receipt: `C:/Temp/av-kit/census-p6-tts-r1-new-hardcode-or-filter.txt` (r1b duplicate same two lines)

| # | file:line | Disposition |
|---|-----------|-------------|
| 1 | `implementation-plan.md:76` | updated — lock 7 |
| 2 | `implementation-plan.md:127` | confirmed-consistent — `CATALOG_ITEMS` |

### Per-hit disposition — `never hardcode` (1)

Receipt: `C:/Temp/av-kit/census-p6-tts-r1-new-never-hardcode.txt`

| # | file:line | Disposition |
|---|-----------|-------------|
| 1 | `implementation-plan.md:127` | confirmed-consistent — `CATALOG_ITEMS` wording |

### Per-hit disposition — remain `page.route` (6)

Receipt: `C:/Temp/av-kit/census-p6-tts-r1-remain-page-route.txt`

| # | file:line | Disposition |
|---|-----------|-------------|
| 1 | `assert-e2e-control-census.ps1:140` | confirmed-consistent — rejects route-only |
| 2 | `implementation-plan.md:80` | confirmed-consistent — lock 11 not-proof |
| 3 | `implementation-plan.md:152` | confirmed-consistent — `E2E_SEAM` not-proof |
| 4 | `implementation-plan.md:153` | confirmed-consistent — `E2E_SEAM_PROOF` not-proof |
| 5 | `implementation-plan.md:157` | confirmed-consistent — `E2E_NO_LIVE_HF` not-proof |
| 6 | `implementation-plan.md:307` | confirmed-consistent — AC-22.22 negative |

### Per-hit disposition — r1b/r1c catalog follow-up (12+2)

| Receipt | file:line | Disposition |
|---------|-----------|-------------|
| `census-p6-tts-r1b-new-catalog-rows-as-is.txt` | `implementation-plan.md:328` | updated — sufficiency row |
| `census-p6-tts-r1b-new-seed-variants.txt` | `implementation-plan.md:76` | updated — lock 7 cites current seed count |
| | `implementation-plan.md:127` | confirmed-consistent — named-set source |
| | `implementation-plan.md:328` | confirmed-consistent — sufficiency |
| | `implementation-plan.md:442` | updated — open-question rec |
| `census-p6-tts-r1b-new-four-rows.txt` | `implementation-plan.md:76` | confirmed-consistent — seed count, not a hardcoded UI list |
| | `implementation-plan.md:328` | confirmed-consistent |
| | `implementation-plan.md:442` | confirmed-consistent |
| `census-p6-tts-r1b-new-text-basename-typed.txt` | `implementation-plan.md:115` | updated — typed `FILE_LOAD_OUT` schema |
| `census-p6-tts-r1c-new-Hardcode-or-filter.txt` | `implementation-plan.md:375` | updated — out-of-scope C2 |
| | `implementation-plan.md:443` | updated — rejected hardcode option |

Scripts exist: `assert-red-oracle.ps1`, `assert-e2e-control-census.ps1`, `assert-handoff-markers.ps1`. Ready for Round 2 `/plan-critical-review`.

## Round 2 Review (2026-08-20)

**Workflow**: `/plan-critical-review`
**Agent**: Codex GPT-5.6-sol
**Review mode**: `plan`

### Intent Anchor

Executing this plan is supposed to deliver the complete MEU-22 TTS page and Model Manager while ensuring Wave 2 never reaches live Kokoro or Hugging Face adapters. The corrected plan now supplies the file-load producer, per-control bindings, and API-items-as-is catalog contract, but its no-live-adapter verification still has a concrete false-pass and therefore does not yet establish that objective.

### Findings

| # | Severity | Confidence | Finding | File:Line | Recommendation | Status |
|---|----------|------------|---------|-----------|----------------|--------|
| R2-F1 | High | High | **PR-4/PR-8 — Round-1 F1 remains materially open: `E2E_CONTROL_CENSUS` still accepts a phrase-only seam and does not require the seam in the independently launched W2-5 case.** `Get-StrippedSource` removes comments but preserves string literals, and every W2-4 seam check is a raw `Assert-Contains` regex. A W2-4 test can therefore put `addInitScript`, `window.fetch =`, the three prefixes, `599`, `new Response`, `E2E_SEAM_NEG`, and `__e2e-unhandled` in one string or `toContain` proof without ever calling `page.addInitScript` or assigning `window.fetch`; that contradicts the plan's explicit “phrase-only constants do not satisfy” rule. Separately, W2-5 is required to click Generate, model Get, and model Load, but its helper block contains no `addInitScript`, `window.fetch`, `__e2eSeamInstalled`, fail-closed, or 599 requirement. Existing Wave 1/2 tests launch a fresh Electron app and install their seam per case, so W2-4's seam cannot be assumed to protect W2-5. The helper can consequently pass while W2-5 reaches `TTSService.generate`/Kokoro or `hf_hub_download`, violating `E2E_NO_LIVE_HF`. This is the same delivery-level false-pass class as F1, not a predicate-shape nit. | `assert-e2e-control-census.ps1:4-8`, `:31-35`, `:112-142`, `:144-183`; `implementation-plan.md:60`, `:144`, `:148-158`, `:307`; `ui/tests/e2e/transcript-queue.test.ts:220-291`; `packages/core/src/avkit_core/services/tts.py:188-190`; `packages/core/src/avkit_core/services/models.py:110-126`; `packages/infrastructure/src/avkit_infra/model_manager/manager.py:65-71` | Make the helper reject a W2-4 token-only/string-literal seam and prove an executable seam call/assignment (for example, bind the case to an invoked seam installer and inspect/execute that installer rather than free tokens). Require W2-5 to install/invoke the same fail-closed seam before Generate/Get/Load. Add helper negative self-probes for (a) all seam tokens in a string with no executable assignment and (b) dangerous W2-5 actuation with no seam; both must fail. | open |

### Prior Pass Summary

| Finding | Prior Status | Round 2 Result |
|---------|--------------|----------------|
| F1 — executable, fail-closed renderer seam | corrections_applied | ❌ Still open — tokens and prefixes were added, but the helper remains source-token-only and W2-5 is not seam-gated. |
| F2 — per-control W2-5 observables | corrections_applied | ✅ Fixed at the plan/materiality level — IPC channels, model Get/Load, voice card, and G30 selects are named and bound in W2-5. |
| F3 — basename-only file-load producer | corrections_applied | ✅ Fixed — the existing `read-text-file` channel now has a planned `{ text, basename }` producer plus `ipc.ts`, `preload.ts`, and `env.d.ts` updates and path-leak negatives. |
| F4 — stale three-ONNX catalog claim | corrections_applied | ✅ Fixed — stale phrases are absent; `CATALOG_ITEMS` renders API `items` as-is and current canon confirms four seeds including PyTorch FP32. |

### Scope

**Targets reviewed in full**:

- `docs/execution/plans/2026-08-20-p6-gui-tts-models/implementation-plan.md`
- `docs/execution/plans/2026-08-20-p6-gui-tts-models/task.md`
- `docs/execution/plans/2026-08-20-p6-gui-tts-models/assert-red-oracle.ps1`
- `docs/execution/plans/2026-08-20-p6-gui-tts-models/assert-handoff-markers.ps1`
- `docs/execution/plans/2026-08-20-p6-gui-tts-models/assert-e2e-control-census.ps1`

**Authority checked**: TTS/Model Manager/Settings/E2E sections of `06-gui.md`; TTS/models/settings contracts in `04-rest-api.md`; `gui-actions-index.md`; MEU registry/grouping; live TTS/model routes and schemas; current IPC/preload/renderer-fetch chain; current four-row `SEED_VARIANTS`; G30/E2; prior downloader/transcript seam rules and E2E case structure.

**Mode confirmation**: plan review. All task rows remain unchecked. `TTSPage.tsx`, `tts-generate.test.ts`, the MEU-22 handoff, and the implementation review are absent. No product code was edited.

### PR-6 Blast-Radius Gate

| Check | Result | Evidence |
|-------|--------|----------|
| Three manifests and three runner receipts read in full | pass | All exist and end in successful census output. |
| Every manifest-named raw receipt read untruncated | pass | 31 receipt entries; zero missing files; raw line counts equal manifest `HITS`. |
| Per-hit dispositions | pass | 77 raw `file:line` hits; every hit maps to an `updated` or `confirmed-consistent` correction-log row. |
| Procedural gate result | pass | `C:/Temp/av-kit/pr6-census-integrity-r2.txt`: `FAILURES=0`, `PASS: PR6_CENSUS_GATE`. |

### Requested Contract Confirmations

| Contract | Result | Evidence |
|----------|--------|----------|
| `E2E_NO_LIVE_HF` executable override + fail-closed prefixes + negative | fail | R2-F1 demonstrates token-only W2-4 acceptance and no seam requirement around dangerous W2-5 actuation. `page.route` remains correctly non-probative. |
| `E2E_ACTUATE` per-control observables | pass | Helper binds per-channel IPC and exact REST paths for Get/Load/voice/select/control rows (`assert-e2e-control-census.ps1:144-183`). |
| `FILE_LOAD_OUT` producer | pass | Plan changes existing handler to `{ text, basename }`, updates both type surfaces, and forbids renderer path input/full-path output (`implementation-plan.md:115-116`, `:277`, `:288`, `:347-349`). |
| `CATALOG_ITEMS` / four current seeds | pass | Live `SEED_VARIANTS` has PyTorch FP32 plus three ONNX rows; UI rule is API-items-as-is, not hardcoded IDs (`engine.py:23-28`; `implementation-plan.md:76`, `:127`, `:301`). |
| `CLIPBOARD_READ` existing channel | pass | Planned `IpcDeps.readClipboard` completes `read-clipboard-text`; no new IPC name or `navigator.clipboard` (`implementation-plan.md:117`, `:289`, `:347`, `:350`). |
| `JOB_POLL` | pass | Only `GET /tts/{id}` after 201; no list envelope (`implementation-plan.md:99`, `:293`; `04-rest-api.md:243-247`). |
| `SETTINGS_LEAVES` vs MEU-23 | pass | No models-directory browse or chunk editor; those remain scheduled to MEU-23 (`implementation-plan.md:131-132`, `:367-368`; `meu-status.yaml:673-696`). |
| `CANCEL_VERB` | pass | `cancel-btn` → `DELETE /tts/{id}`; no shipped Stop control (`implementation-plan.md:121`, `:294`; `gui-actions-index.md:50`). |
| G30 selects | pass | Language, format, and device use `SelectInput` and W2-5 requires positive visibility (`implementation-plan.md:223`, `:242-257`; helper `:176-178`). |
| Sweep 8 invoked scripts | pass | Seven invoked scripts/tools exist; the explicitly absent `validate_closeout_artifacts.py` is not invoked. Receipt: `C:/Temp/av-kit/sweep8-and-not-started-r2.txt`. |
| Sweep 9 named-set discipline | pass with non-blocking note | All stale three-ONNX / invented-PyTorch / old line-range phrases have zero hits. The repeated current “four rows” statements are mutually consistent and do not instruct UI hardcoding. |

### Checklist Results

#### Plan Review (PR-1 through PR-9)

| Check | Result | Evidence |
|-------|--------|----------|
| PR-1 Plan/task alignment | pass | Same MEU-22-only scope and Red → Green → E2E → H1/review/H2 order. |
| PR-2 Not-started confirmation | pass | All rows `[ ]`; planned production/E2E/handoff artifacts absent. |
| PR-3 Task contract completeness | pass | Every actionable row has owner, deliverable, exact validation, dependency/context, durable output, and status. |
| PR-4 Validation realism | fail | R2-F1 is a demonstrated false-pass for a materially missing no-live-adapter guarantee. |
| PR-5 Source-backed planning | pass | AC-22.1–22.24 and locks are tied to Spec, Local Canon, Research-backed, or prior named rules. |
| PR-6 Corrections readiness | pass | Census gate passed with complete raw receipts and per-hit dispositions. |
| PR-7 Scope discipline C2 | pass | MEU-23–25 deferrals are scheduled; FastAPI/MCP/chrome and named P2 exclusions have real bases. |
| PR-8 Reachability/totality | fail | W2-5 reaches dangerous controls without a required seam producer; W2-4 can satisfy proof using inert source strings. |
| PR-9 Single-statement discipline | pass | No stale materially divergent catalog spelling remains; operative behavior is owned by `CATALOG_ITEMS`. |

#### Docs Review (DR-1 through DR-8)

| Check | Result | Evidence |
|-------|--------|----------|
| DR-1 Claim-to-state match | fail | The correction log calls F1 fixed, but the live helper remains token-only and does not gate W2-5. |
| DR-2 Residual old terms | pass | Declared old F1-F4 phrases are absent; intentional negative-only terms are dispositioned. |
| DR-3 Downstream references | pass | Plan/task/helper/correction log use the canonical Session 10 slug and MEU-22 scope. |
| DR-4 Verification robustness | fail | R2-F1 demonstrates the material seam false-pass. |
| DR-5 Evidence auditability | pass | PR-6 manifests, raw receipts, correction log, and review receipts are reproducible. |
| DR-6 Cross-reference integrity | pass | Live API/IPC/schema/catalog/scheduling sources agree with F2-F4 corrections. |
| DR-7 Evidence freshness | pass | Review used live files and current receipts, not the corrections summary. |
| DR-8 Completion vs residual risk | pass | Plan remains `draft`; no implementation-complete claim is made. |

### Commands Executed

Read-only inspection and exact-evidence checks only. Key receipts:

- `C:/Temp/av-kit/read-census-gate-r2.txt`
- `C:/Temp/av-kit/read-census-raw-r2.txt`
- `C:/Temp/av-kit/pr6-census-integrity-r2.txt`
- `C:/Temp/av-kit/read-plan-r2-001-170.txt`, `read-plan-r2-171-340.txt`, `read-plan-r2-341-end.txt`
- `C:/Temp/av-kit/read-review-targets-r2.txt`, `read-task-r2-050-end.txt`
- `C:/Temp/av-kit/sweep8-and-not-started-r2.txt`
- `C:/Temp/av-kit/sweep9-literals-r2.txt`
- `C:/Temp/av-kit/w2-5-seam-gap-r2.txt`
- `C:/Temp/av-kit/read-live-contracts-r2.txt`, `read-api-contracts-r2.txt`, `read-build-canon-r2.txt`

The plan-local helpers and product test suites were not executed because their planned TTS product/E2E/handoff inputs correctly do not exist before implementation.

### Open Questions / Assumptions

No human product decision is required. The correction is determined by the existing `E2E_NO_LIVE_HF`, E2, downloader RULE-2, and the repository's per-test Electron launch/seam pattern.

### Follow-up Actions

1. Use `/plan-corrections` to close R2-F1 only: make token-only W2-4 proof fail and require the fail-closed seam in W2-5 before Generate/Get/Load.
2. Re-run the same rolling plan review as Round 3 with the required fresh blast-radius census and per-hit dispositions.

### Verdict

`changes_required` — PR-6 passed and F2-F4 are fixed, but R2-F1 is an evidence-backed High finding under PR-4/PR-8. Executing the plan can still produce a green Wave 2 census while the renderer seam is inert or absent from the case that actuates live Kokoro/Hugging Face paths.

### Residual Risk

This was a static, findings-only plan review. No product code, tests, plan files, or prior handoffs were modified. The sole write was this canonical rolling review file.

## Corrections Applied (2026-08-20) — after Round 2

**Workflow**: `/plan-corrections` inside `/create-plan` §5b. Plan/task + plan-folder helper only. No product code.
**Agent**: coordinator (implementer) — `corrections_applied`, never `approved`.
**Scope**: R2-F1 only. F2–F4 stay closed.

| # | Sev | Status | Fix |
|---|-----|--------|-----|
| R2-F1 | High | fixed | Named `E2E_SEAM_INSTALL` = file-level `async function installTtsSeam(page)`. Helper extracts that body and requires `addInitScript(`, `window.fetch =`, `new Response`, `reload(` **outside string literals**. Every W2-1…W2-6 must call `installTtsSeam(`. W2-5 also asserts `__e2eSeamInstalled`. W2-4 keeps runtime `E2E_SEAM_NEG`. Self-probes reject (a) token-only W2-4 blob, (b) W2-5 clicks without installer, (c) string-only installer body. |

### Declared variants swept

Old: `W2-4 missing E2E_SEAM addInitScript`, `W2-4 missing executable window.fetch`.
New: `installTtsSeam`, `E2E_SEAM_INSTALL`, `token-only`, `string-only installer`, `outside strings`.
Remain: `page.route`.

Manifest: `C:/Temp/av-kit/census-p6-tts-r2-manifest.txt`. Runner: `C:/Temp/av-kit/census-p6-tts-r2-run.txt`.
Blast-radius census: 2 old + 5 new + 1 remain = 8 sweeps. Zero-hit old: 2. Nonzero raw hits: 13+13+3+1+4+6 = 40. Each hit dispositioned below.

### Zero-hit old receipts

| Receipt | Hits | Disposition |
|---------|------|-------------|
| `C:/Temp/av-kit/census-p6-tts-r2-old-w2-4-missing-addInitScript.txt` | 0 | case-level token check removed |
| `C:/Temp/av-kit/census-p6-tts-r2-old-w2-4-missing-window-fetch.txt` | 0 | case-level fetch-token check removed |

### Per-hit disposition — `installTtsSeam` (13)

Receipt: `C:/Temp/av-kit/census-p6-tts-r2-new-install-tts-seam.txt`

| # | file:line | Disposition |
|---|-----------|-------------|
| 1 | `assert-e2e-control-census.ps1:58` | updated — `Test-CallsInstaller` |
| 2 | `assert-e2e-control-census.ps1:63` | updated — per-case call error |
| 3 | `assert-e2e-control-census.ps1:133` | updated — W2-5 no-installer self-probe |
| 4 | `assert-e2e-control-census.ps1:136` | updated — string-only installer fixture |
| 5 | `assert-e2e-control-census.ps1:137` | updated — extract fixture body |
| 6 | `assert-e2e-control-census.ps1:202` | updated — extract live installer |
| 7 | `assert-e2e-control-census.ps1:204` | updated — missing-function error |
| 8 | `assert-e2e-control-census.ps1:223` | updated — route-only still requires installer call |
| 9 | `task.md:46` | updated — row 3 |
| 10 | `implementation-plan.md:144` | updated — `E2E_CASES` |
| 11 | `implementation-plan.md:152` | updated — named-set definition |
| 12 | `implementation-plan.md:154` | confirmed-consistent — `E2E_SEAM_PROOF` |
| 13 | `implementation-plan.md:308` | updated — AC-22.22 negative |

### Per-hit disposition — `E2E_SEAM_INSTALL` (13)

Receipt: `C:/Temp/av-kit/census-p6-tts-r2-new-e2e-seam-install.txt`

| # | file:line | Disposition |
|---|-----------|-------------|
| 1 | `assert-e2e-control-census.ps1:63` | confirmed-consistent — call error text |
| 2 | `assert-e2e-control-census.ps1:139` | updated — string-only self-probe |
| 3 | `assert-e2e-control-census.ps1:204` | confirmed-consistent — missing function |
| 4 | `assert-e2e-control-census.ps1:207` | updated — body executable check |
| 5 | `task.md:46` | updated — row 3 |
| 6 | `implementation-plan.md:60` | updated — WP-22c |
| 7 | `implementation-plan.md:144` | confirmed-consistent — `E2E_CASES` |
| 8 | `implementation-plan.md:152` | updated — named set |
| 9 | `implementation-plan.md:153` | confirmed-consistent — `E2E_SEAM` |
| 10 | `implementation-plan.md:158` | updated — `E2E_NO_LIVE_HF` |
| 11 | `implementation-plan.md:159` | updated — census owners |
| 12 | `implementation-plan.md:223` | updated — §4A |
| 13 | `implementation-plan.md:308` | updated — AC-22.22 |

### Per-hit disposition — `token-only` (3)

Receipt: `C:/Temp/av-kit/census-p6-tts-r2-new-token-only.txt`

| # | file:line | Disposition |
|---|-----------|-------------|
| 1 | `assert-e2e-control-census.ps1:122` | updated — self-probe (a) |
| 2 | `implementation-plan.md:159` | confirmed-consistent — census text |
| 3 | `implementation-plan.md:308` | confirmed-consistent — AC negative |

### Per-hit disposition — `string-only installer` (1)

Receipt: `C:/Temp/av-kit/census-p6-tts-r2-new-string-only-installer.txt`

| # | file:line | Disposition |
|---|-----------|-------------|
| 1 | `assert-e2e-control-census.ps1:139` | updated — self-probe (c) |

### Per-hit disposition — `outside strings` (4)

Receipt: `C:/Temp/av-kit/census-p6-tts-r2-new-outside-strings.txt`

| # | file:line | Disposition |
|---|-----------|-------------|
| 1 | `assert-e2e-control-census.ps1:82` | updated — `addInitScript(` |
| 2 | `assert-e2e-control-census.ps1:83` | updated — `window.fetch =` |
| 3 | `assert-e2e-control-census.ps1:84` | updated — `new Response` |
| 4 | `assert-e2e-control-census.ps1:85` | updated — `reload(` |

### Per-hit disposition — remain `page.route` (6)

Receipt: `C:/Temp/av-kit/census-p6-tts-r2-remain-page-route.txt`

| # | file:line | Disposition |
|---|-----------|-------------|
| 1 | `assert-e2e-control-census.ps1:224` | confirmed-consistent — rejects route-only |
| 2 | `implementation-plan.md:80` | confirmed-consistent — lock 11 not-proof |
| 3 | `implementation-plan.md:153` | confirmed-consistent — `E2E_SEAM` not-proof |
| 4 | `implementation-plan.md:154` | confirmed-consistent — `E2E_SEAM_PROOF` not-proof |
| 5 | `implementation-plan.md:158` | confirmed-consistent — `E2E_NO_LIVE_HF` not-proof |
| 6 | `implementation-plan.md:308` | confirmed-consistent — AC-22.22 negative |

Ready for Round 3 `/plan-critical-review`.

## Round 3 Review (2026-08-20)

**Workflow**: `/plan-critical-review`
**Agent**: Codex GPT-5.6-sol
**Review mode**: `plan`

### Intent Anchor

Executing this plan is supposed to deliver the complete MEU-22 TTS page and Model Manager while ensuring every Wave 2 case is isolated from live Kokoro and Hugging Face adapters. The corrected plan retains the product contract and F2-F4 fixes, but its per-case installer detector still has a reproduced quoted-token false-pass, so executing the plan does not yet reliably prove the no-live-adapter objective.

### Findings

| # | Severity | Confidence | Finding | File:Line | Recommendation | Status |
|---|----------|------------|---------|-----------|----------------|--------|
| R3-F1 | High | High | **PR-4/PR-8 — R2-F1 remains materially open: the helper strips strings when checking the installer body, but not when proving that each W2 case actually calls that installer.** `Test-CallsInstaller` applies `installTtsSeam\s*\(` directly to raw case text. The Round-2 token-only W2-4 and no-installer W2-5 self-probes omit the `installTtsSeam(` token entirely, so they pass without testing the quoted-token adversary. An in-memory fixture placed `installTtsSeam(`, W2-4's `E2E_SEAM_NEG` / `__e2e-unhandled` / `599` tokens, and W2-5's `__e2eSeamInstalled` token only inside quoted assertions while retaining the required bound UI actions and REST/IPC observables. The helper's relevant W2-4 and W2-5 branches both passed, while `Get-CodeWithoutStrings` proved neither case had an executable installer call. W2-5 can therefore actuate Generate/Get/Load without installing the fail-closed renderer seam, allowing live Kokoro/Hugging Face paths while `E2E_CONTROL_CENSUS` is green. This is the original delivery-level R2-F1 false-pass, not a new predicate-shape variant. | `assert-e2e-control-census.ps1:57-64`, `:113-139`, `:208-226`, `:228-271`; `implementation-plan.md:144`, `:152-159`, `:308`; `task.md:46` | Apply `Get-CodeWithoutStrings` (or an equivalent executable-call parser) inside the per-case installer-call proof; make the W2-4 and W2-5 self-probes include quoted `installTtsSeam(` and gate tokens while containing no executable call, and require those fixtures to fail. | open |

### Prior Pass Summary

| Finding | Prior Status | Round 3 Result |
|---------|--------------|----------------|
| R2-F1 — executable fail-closed seam in every Wave 2 case | corrections_applied | ❌ Still open — the file-level body is checked outside strings, but raw quoted text satisfies the per-case installer-call proof. |
| F2 — per-control W2-5 observables | fixed | ✅ Remains closed — 16 REST/IPC/control bindings remain present and individually named. |
| F3 — basename-only file-load producer | fixed | ✅ Remains closed — `FILE_LOAD_OUT`, IPC producer, preload type, and renderer type remain intact. |
| F4 — API-items-as-is catalog | fixed | ✅ Remains closed — `CATALOG_ITEMS` still renders all API `items` without hardcoding/filtering. |

### Scope

**Targets reviewed in full**:

- `docs/execution/plans/2026-08-20-p6-gui-tts-models/implementation-plan.md`
- `docs/execution/plans/2026-08-20-p6-gui-tts-models/task.md`
- `docs/execution/plans/2026-08-20-p6-gui-tts-models/assert-red-oracle.ps1`
- `docs/execution/plans/2026-08-20-p6-gui-tts-models/assert-handoff-markers.ps1`
- `docs/execution/plans/2026-08-20-p6-gui-tts-models/assert-e2e-control-census.ps1`

**Additional evidence**: the complete Round-2 PR-6 manifest, runner, all eight manifest-named raw receipts, and the rolling review's `Corrections Applied (2026-08-20) — after Round 2` section.

**Mode confirmation**: plan review. All 18 actionable task rows remain unchecked. `TTSPage.tsx`, `tts-generate.test.ts`, the MEU-22 handoff, and the implementation review remain absent. No product code was edited.

### PR-6 Blast-Radius Gate

| Check | Result | Evidence |
|-------|--------|----------|
| Named manifest and runner | pass | Both files exist; the runner ends with `PASS: CENSUS_MANIFEST`. |
| Every manifest-named raw receipt read untruncated | pass | 8 receipts: 2 zero-hit old sweeps and 6 nonzero sweeps. |
| Raw hit counts | pass | Manifest counts reproduce exactly: 40 nonzero raw hits total. |
| Per-hit dispositions | pass | Every raw `file:line` hit maps to at least one `updated` or `confirmed-consistent` row in the Round-2 correction log. |
| Procedural gate result | pass | `C:/Temp/av-kit/pr6-census-integrity-r3.txt`: `MANIFEST_ENTRIES=8`, `RAW_HITS=40`, `PASS: PR6_R2_CENSUS_GATE`. |

### Requested Contract Confirmations

| Contract | Result | Evidence |
|----------|--------|----------|
| File-level `E2E_SEAM_INSTALL` | pass | Helper extracts `async function installTtsSeam(page)` and checks `addInitScript(`, `window.fetch =`, `new Response`, and `reload(` after `Get-CodeWithoutStrings` (`assert-e2e-control-census.ps1:37-55`, `:66-97`, `:202-207`). |
| Every W2-1…W2-6 calls `installTtsSeam(` | fail | `Test-CallsInstaller` scans raw source, so a quoted token passes without an executable call (`:57-64`, `:208-211`). Reproduced in `r3-w4-w5-helper-branch-false-pass.txt`. |
| W2-5 seam gate before Generate/Get/Load | fail | `__e2eSeamInstalled` is also a raw `Assert-Contains`; a quoted gate token plus quoted installer token passes while Generate/Get/Load clicks remain executable (`:228-271`). |
| W2-4 negative seam tokens | structurally intact but non-probative | `E2E_SEAM_NEG`, `__e2e-unhandled`, and `599` remain required, but raw quoted tokens satisfy all three (`:213-226`). |
| Installer-body quoted-token defense | pass | `Get-CodeWithoutStrings` is applied to the extracted body, and the string-only body self-probe is rejected (`:66-97`, `:136-140`). |
| `page.route` | pass | It remains explicitly non-probative; no review credit was given for it (`:223-226`; plan `:153-158`). |
| `FILE_LOAD_OUT` / `CATALOG_ITEMS` / `E2E_ACTUATE` | pass | `C:/Temp/av-kit/f2-f4-invariants-r3.txt`: file-load and catalog contracts pass; 16 per-control bindings remain present. |

### Checklist Results

#### Plan Review (PR-1 through PR-9)

| Check | Result | Evidence |
|-------|--------|----------|
| PR-1 Plan/task alignment | pass | Same MEU-22-only scope and Red → Green → E2E → H1/review/H2 order. |
| PR-2 Not-started confirmation | pass | 18 actionable rows are `[ ]`; planned production/E2E/handoff artifacts are absent. |
| PR-3 Task contract completeness | pass | Every actionable row retains owner, deliverable, exact validation, dependency, context strategy, durable outputs, and status. |
| PR-4 Validation realism | fail | R3-F1 demonstrates a green helper branch with materially missing per-case seam installation. |
| PR-5 Source-backed planning | pass | AC-22.1–22.24 and operative locks remain tied to Spec, Local Canon, Research-backed, or named prior rules. |
| PR-6 Corrections readiness | pass | Fresh Round-2 census gate passed with all 8 raw receipts and all 40 hit dispositions. |
| PR-7 Scope discipline C2 | pass | MEU-23–25 deferrals remain scheduled; out-of-scope rows retain concrete bases. |
| PR-8 Reachability/totality | fail | W2-5's dangerous production entrypoints are reachable without an executable call to the seam producer, while the helper still passes. |
| PR-9 Single-statement discipline | pass | Operative behavior remains owned by named sets; no materially divergent live spelling was found. |

#### Docs Review (DR-1 through DR-8)

| Check | Result | Evidence |
|-------|--------|----------|
| DR-1 Claim-to-state match | fail | The Round-2 correction log marks R2-F1 fixed, but the live per-case detector remains quote-blind. |
| DR-2 Residual old terms | pass | Both declared old receipt variants have zero hits. |
| DR-3 Downstream references | pass | Plan, task, helper, and rolling review retain the canonical slug and MEU-22 scope. |
| DR-4 Verification robustness | fail | `r3-w4-w5-helper-branch-false-pass.txt` reproduces the material false-pass. |
| DR-5 Evidence auditability | pass | Manifest, runner, all raw receipts, correction log, and adversarial receipts are reproducible. |
| DR-6 Cross-reference integrity | pass | F2-F4 contracts remain mutually consistent across plan, task, and helper. |
| DR-7 Evidence freshness | pass | Round 3 used live files and current Round-2 receipts, not the coordinator summary alone. |
| DR-8 Completion vs residual risk | pass | Plan remains `draft`; no implementation-complete claim is made. |

### Commands Executed

Read-only inspection, exact-evidence checks, and in-memory adversarial probes only. Key receipts:

- `C:/Temp/av-kit/read-census-r2-manifest-r3.txt`
- `C:/Temp/av-kit/read-census-r2-run-r3.txt`
- `C:/Temp/av-kit/read-r2-raw-1-r3.txt` through `read-r2-raw-8-r3.txt`
- `C:/Temp/av-kit/pr6-census-integrity-r3.txt`
- `C:/Temp/av-kit/read-plan-101-200-r3.txt`, `read-plan-201-300-r3.txt`, `read-plan-301-400-r3.txt`, `read-plan-401-end-r3.txt`
- `C:/Temp/av-kit/read-task-r3.txt`, `read-red-oracle-r3.txt`, `read-handoff-markers-r3.txt`, `read-e2e-helper-r3-1.txt`, `read-e2e-helper-r3-2.txt`
- `C:/Temp/av-kit/not-started-and-artifacts-r3.txt`
- `C:/Temp/av-kit/f2-f4-invariants-r3.txt`
- `C:/Temp/av-kit/r3-quoted-installer-false-pass.txt`
- `C:/Temp/av-kit/r3-w4-w5-helper-branch-false-pass.txt`

The plan-local E2E helper was not run end-to-end because its planned `tts-generate.test.ts` and test-ID inputs correctly do not exist before implementation. Its function definitions and relevant W2-4/W2-5 branches were executed in memory against adversarial fixtures.

### Open Questions / Assumptions

No product decision is required. The required behavior is already fixed by `E2E_NO_LIVE_HF`, R2-F1, and the user's Round-3 contract.

### Follow-up Actions

1. Round 3 is the plan-review cap. Stop and obtain direct human direction before any further correction/review action.
2. If directed to correct, close R3-F1 only; F2-F4 remain closed.

### Verdict

`changes_required` — PR-6 passed and F2-F4 remain closed, but R3-F1 is an evidence-backed High finding under PR-4/PR-8. Executing the plan can still produce a green Wave 2 census while W2-4 and W2-5 omit the executable seam call that prevents live Kokoro/Hugging Face access. The Round-3 plan-review cap is reached.

### Residual Risk

This was a static, findings-only plan review. No product code, tests, plan files, or implementation handoffs were modified. The sole repository write was this canonical rolling review file. Because the cap is reached with `changes_required`, the workflow is now at a human-decision HARD STOP.

## Corrections Applied (2026-08-20) — after Round 3

**Workflow**: `/plan-corrections` inside `/create-plan` §5b after USER_EXPLICIT "continue review loop" (cap-3 HARD STOP resume option a). Plan/task + plan-folder helper only. No product code.
**Agent**: coordinator (implementer) — `corrections_applied`, never `approved`.
**Scope**: R3-F1 only. F2–F4 stay closed.

| # | Sev | Status | Fix |
|---|-----|--------|-----|
| R3-F1 | High | fixed | `Test-CallsInstaller` and `Test-GateOutsideStrings` both run `Get-CodeWithoutStrings` before matching. W2-5 gate uses `Test-GateOutsideStrings` (not raw `Assert-Contains`). Self-probes (d): quoted `installTtsSeam(` in W2-4/W2-5 and quoted `__e2eSeamInstalled` in W2-5 must fail; executable `await installTtsSeam(page)` and `window.__e2eSeamInstalled` must pass. Plan/task name the outside-strings rule. Probe receipt: `C:/Temp/av-kit/r3-self-probe-verify.txt` → `PASS: R3_SELF_PROBES`. |

### Declared variants swept

Old: raw `$Src -match 'installTtsSeam\s*\('`, raw `Assert-Contains $w5 '__e2eSeamInstalled'`.
New: `Get-CodeWithoutStrings`, `Test-GateOutsideStrings`, quoted W2-4/W2-5/gate probe messages, `outside string literals`, `R3-F1`.
Remain: `page.route`.

Manifest: `C:/Temp/av-kit/census-p6-tts-r3-manifest.txt`. Runner: `C:/Temp/av-kit/census-p6-tts-r3-run.txt`.
Blast-radius census: 2 old + 7 new + 1 remain = 10 sweeps. Zero-hit old: 2. Nonzero raw hits: 6+4+1+1+1+3+7+6 = 29. Each hit dispositioned below.

### Zero-hit old receipts

| Receipt | Hits | Disposition |
|---------|------|-------------|
| `C:/Temp/av-kit/census-p6-tts-r3-old-raw-calls-installer.txt` | 0 | raw `$Src -match` installer proof gone |
| `C:/Temp/av-kit/census-p6-tts-r3-old-w25-raw-gate-assert.txt` | 0 | raw W2-5 gate Assert-Contains gone |

### Per-hit disposition — `Get-CodeWithoutStrings` (6)

Receipt: `C:/Temp/av-kit/census-p6-tts-r3-new-get-code-without-strings.txt`

| # | file:line | Disposition |
|---|-----------|-------------|
| 1 | `assert-e2e-control-census.ps1:58` | updated — `Test-CallsInstaller` |
| 2 | `assert-e2e-control-census.ps1:63` | updated — `Test-GateOutsideStrings` |
| 3 | `assert-e2e-control-census.ps1:73` | updated — function definition |
| 4 | `assert-e2e-control-census.ps1:81` | confirmed-consistent — body executable check |
| 5 | `assert-e2e-control-census.ps1:86` | confirmed-consistent — `Assert-ExecutableSeamBody` |
| 6 | `implementation-plan.md:154` | updated — `E2E_SEAM_PROOF` cites stripper |

### Per-hit disposition — `Test-GateOutsideStrings` (4)

Receipt: `C:/Temp/av-kit/census-p6-tts-r3-new-test-gate-outside.txt`

| # | file:line | Disposition |
|---|-----------|-------------|
| 1 | `assert-e2e-control-census.ps1:62` | updated — function |
| 2 | `assert-e2e-control-census.ps1:169` | updated — quoted-gate self-probe |
| 3 | `assert-e2e-control-census.ps1:173` | updated — positive gate self-probe |
| 4 | `assert-e2e-control-census.ps1:270` | updated — live W2-5 gate |

### Per-hit disposition — quoted probes (1+1+1)

| Receipt | file:line | Disposition |
|---------|-----------|-------------|
| `census-p6-tts-r3-new-quoted-w24-probe.txt` | `assert-e2e-control-census.ps1:154` | updated — self-probe (d) W2-4 |
| `census-p6-tts-r3-new-quoted-w25-probe.txt` | `assert-e2e-control-census.ps1:166` | updated — self-probe (d) W2-5 |
| `census-p6-tts-r3-new-quoted-gate-probe.txt` | `assert-e2e-control-census.ps1:170` | updated — self-probe (d) gate |

### Per-hit disposition — `outside string literals` (3)

Receipt: `C:/Temp/av-kit/census-p6-tts-r3-new-outside-string-literals.txt`

| # | file:line | Disposition |
|---|-----------|-------------|
| 1 | `task.md:46` | updated — row 3 |
| 2 | `implementation-plan.md:152` | updated — `E2E_SEAM_INSTALL` |
| 3 | `implementation-plan.md:154` | confirmed-consistent — `E2E_SEAM_PROOF` |

### Per-hit disposition — `R3-F1` (7)

Receipt: `C:/Temp/av-kit/census-p6-tts-r3-new-r3-f1.txt`

| # | file:line | Disposition |
|---|-----------|-------------|
| 1–3 | helper `:154`, `:166`, `:170` | updated — probe error labels |
| 4–6 | `implementation-plan.md:152`, `:154`, `:159` | updated — named sets cite R3-F1 |
| 7 | `implementation-plan.md:308` | updated — AC-22.22 negatives |

### Per-hit disposition — remain `page.route` (6)

Receipt: `C:/Temp/av-kit/census-p6-tts-r3-remain-page-route.txt`

| # | file:line | Disposition |
|---|-----------|-------------|
| 1 | `assert-e2e-control-census.ps1:265` | confirmed-consistent — rejects route-only |
| 2–6 | plan lock 11 / `E2E_SEAM` / `E2E_SEAM_PROOF` / `E2E_NO_LIVE_HF` / AC-22.22 | confirmed-consistent — not-proof |

Ready for Round 4 `/plan-critical-review`.

## Round 4 Review (2026-08-20)

**Workflow**: `/plan-critical-review`
**Agent**: Codex GPT-5.6-sol
**Review mode**: `plan`
**Round authority**: USER_EXPLICIT continuation beyond the plan-review cap of 3

### Intent Anchor

Executing this plan is supposed to deliver the complete MEU-22 TTS page and Model Manager while preventing every Wave 2 case from reaching live Kokoro or Hugging Face adapters. The corrected plan now binds all six cases to the outside-string installer proof, binds W2-5 to the outside-string seam-gate proof, retains the fail-closed protected-prefix negative, and preserves the product contracts needed to deliver that objective.

### Findings

No blocking findings.

Structured findings remain empty because the verdict is `approved`.

### Prior Pass Summary

| Finding | Prior Status | Round 4 Result |
|---------|--------------|----------------|
| R3-F1 — quoted tokens could satisfy per-case installer/gate proofs | corrections_applied | ✅ Fixed — live quoted installer and gate fixtures return `False`; executable forms return `True`. |
| F2 — per-control W2-5 observables | fixed | ✅ Remains closed — 16 distinct control IDs retain their REST, IPC, visibility, or progress observables. |
| F3 — basename-only file-load producer | fixed | ✅ Remains closed — `FILE_LOAD_OUT` still owns `{ text, basename }` across main, preload, renderer type, task, and AC. |
| F4 — API-items-as-is catalog | fixed | ✅ Remains closed — all four seeded variants remain API-owned and `CATALOG_ITEMS` still forbids hardcoding/filtering. |

### Scope

**Targets reviewed in full**:

- `docs/execution/plans/2026-08-20-p6-gui-tts-models/implementation-plan.md`
- `docs/execution/plans/2026-08-20-p6-gui-tts-models/task.md`
- `docs/execution/plans/2026-08-20-p6-gui-tts-models/assert-red-oracle.ps1`
- `docs/execution/plans/2026-08-20-p6-gui-tts-models/assert-handoff-markers.ps1`
- `docs/execution/plans/2026-08-20-p6-gui-tts-models/assert-e2e-control-census.ps1`

**Additional evidence**: `06-gui.md` TTS/E2E/deferred canon; `04-rest-api.md` TTS/models contracts; `gui-actions-index.md`; live API schemas/routes; current UI IPC/preload/router state; MEU registry/grouping; the Round-3 manifest, runner, all ten manifest-named raw receipts, correction log, and self-probe receipt.

**Mode confirmation**: plan review. All 18 actionable task rows remain unchecked. `TTSPage.tsx`, `tts-generate.test.ts`, the MEU-22 handoff, implementation review, and reflection remain absent. This workspace has no `.git` directory, so not-started confirmation used the task state and planned-artifact census rather than a Git diff.

### PR-6 Blast-Radius Gate

| Check | Result | Evidence |
|-------|--------|----------|
| Named manifest and runner | pass | Both exist; runner ends with `PASS: CENSUS_MANIFEST`. |
| Every manifest-named raw receipt read untruncated | pass | 10 receipts: 2 zero-hit old sweeps and 8 nonzero sweeps. |
| Raw hit counts | pass | Manifest counts reproduce exactly: 29 nonzero raw hits total. |
| Per-hit dispositions | pass | Every raw `file:line` hit maps to `updated` or `confirmed-consistent` in `Corrections Applied (2026-08-20) — after Round 3`. |
| Self-probe receipt | pass | `C:/Temp/av-kit/r3-self-probe-verify.txt` contains `PASS: R3_SELF_PROBES`. |
| Procedural gate result | pass | `C:/Temp/av-kit/r4-pr6-entry-gate.txt`, `r4-r3-raw-receipts.txt`, and `r4-r3-correction-log.txt`. |

### Requested Contract Confirmations

| Contract | Result | Evidence |
|----------|--------|----------|
| Live `Test-CallsInstaller` quoted-token fixture | pass | `QUOTED_INSTALLER=False`; executable `await installTtsSeam(page)` returns `True`; all W2-1…W2-6 quoted-only fixtures are rejected (`r4-live-r3-probes.txt`). |
| Live `Test-GateOutsideStrings` quoted-token fixture | pass | `QUOTED_GATE=False`; executable `window.__e2eSeamInstalled` returns `True` (`r4-live-r3-probes.txt`). |
| Every W2-1…W2-6 outside-string installer requirement | pass | The live loop calls `Assert-CallsInstaller(Get-CaseBlock(...))` for all six cases after `Get-CodeWithoutStrings` (`assert-e2e-control-census.ps1:249-251`, `:57-59`, `:73-77`). |
| W2-5 Generate/Get/Load outside-string gate | pass | The live W2-5 branch calls `Test-GateOutsideStrings` before accepting the case; quoted gate text fails (`assert-e2e-control-census.ps1:269-272`). |
| `page.route` | pass | It remains explicitly non-probative in the plan and helper; no review credit was given for it (`implementation-plan.md:80`, `:153-159`; helper `:264-266`). |
| `FILE_LOAD_OUT` / `CATALOG_ITEMS` / per-control `E2E_ACTUATE` | pass | All nine fresh invariants pass in `r4-f2-f4-no-live-invariants-final.txt`; the actuation set contains 16 distinct control IDs. |
| No-live-adapter intent | pass | Every case is installer-bound; installer body requires `addInitScript`, executable `window.fetch =`, `new Response`, reload, protected prefixes, 599, and `E2E_SEAM_UNHANDLED`; W2-4 retains the fail-closed negative. |

### Checklist Results

#### Plan Review (PR-1 through PR-9)

| Check | Result | Evidence |
|-------|--------|----------|
| PR-1 Plan/task alignment | pass | Same MEU-22-only scope and Red → Green → Wave 2 → H1/review/H2 order. |
| PR-2 Not-started confirmation | pass | 18/18 actionable rows are `[ ]`; all five planned implementation/closeout artifacts checked are absent. |
| PR-3 Task contract completeness | pass | Every actionable row retains task, owner, deliverable, exact validation, dependency, context strategy, durable outputs, and status. |
| PR-4 Validation realism | pass | The three plan-local validators exist; all required executable dependencies exist; live R3 probes reject the prior concrete false-pass. |
| PR-5 Source-backed planning | pass | AC-22.1–22.24 and operative locks remain tied to Spec, Local Canon, Research-backed, Human-approved, or named prior rules. |
| PR-6 Corrections readiness | pass | Fresh Round-3 census gate passed with all 10 raw receipts and all 29 nonzero hit dispositions. |
| PR-7 Scope discipline C2 | pass | MEU-23–25 are registered/scheduled; every out-of-scope row retains a concrete canon or prior-MEU basis. |
| PR-8 Reachability/totality | pass | Named controls retain observables, production chains, and negative oracles; the corrected Wave 2 seam proof reaches every case and fails closed on protected prefixes. |
| PR-9 Single-statement discipline | pass | Operative sets remain centrally owned and referenced by name; no materially divergent live spelling was found. |

#### Docs Review (DR-1 through DR-8)

| Check | Result | Evidence |
|-------|--------|----------|
| DR-1 Claim-to-state match | pass | The Round-3 correction claims match the live helper and plan/task state. |
| DR-2 Residual old terms | pass | Both declared old receipt variants have zero hits. |
| DR-3 Downstream references | pass | Plan, task, helpers, registry/grouping, and rolling review retain the canonical slug and MEU-22 scope. |
| DR-4 Verification robustness | pass | Live AST-loaded helper probes reproduce and reject the exact R3 quoted-token adversary. |
| DR-5 Evidence auditability | pass | Manifest, runner, all raw receipts, correction log, source reads, existence census, and adversarial probes are reproducible. |
| DR-6 Cross-reference integrity | pass | TTS/models endpoints, IPC changes, catalog contract, action IDs, and deferred MEUs agree across canon and plan. |
| DR-7 Evidence freshness | pass | Round 4 used live files plus current Round-3 receipts; raw counts and dispositions reproduce. |
| DR-8 Completion vs residual risk | pass | The plan remains `draft`; this verdict approves the plan and does not claim implementation completion. |

### Non-Blocking Correction Note

- Clerical only: `implementation-plan.md:334` says “E2E wave 3”; the canonical named set and all executable/task references are Wave 2. Under the Materiality Gate this does not block approval.

### Commands Executed

Read-only inspection, exact-evidence checks, and in-memory adversarial probes only. Key receipts:

- `C:/Temp/av-kit/r4-pr6-entry-gate.txt`
- `C:/Temp/av-kit/r4-r3-raw-receipts.txt`
- `C:/Temp/av-kit/r4-r3-correction-log.txt`
- `C:/Temp/av-kit/r4-plan-lines-1-240.txt`, `r4-plan-lines-241-end.txt`
- `C:/Temp/av-kit/r4-task-red-handoff-full.txt`
- `C:/Temp/av-kit/r4-e2e-script-1-180.txt`, `r4-e2e-script-181-end.txt`
- `C:/Temp/av-kit/r4-live-r3-probes.txt`
- `C:/Temp/av-kit/r4-not-started-python.txt`
- `C:/Temp/av-kit/r4-local-canon-ranges-utf8.txt`, `r4-live-source-ranges.txt`
- `C:/Temp/av-kit/r4-referenced-artifact-existence.txt`
- `C:/Temp/av-kit/r4-scope-registry.txt`
- `C:/Temp/av-kit/r4-f2-f4-no-live-invariants-final.txt`
- `C:/Temp/av-kit/r4-pre-edit-guard.txt`

The plan-local E2E helper was not run end-to-end because its planned `tts-generate.test.ts` and Wave 2 test-ID inputs correctly do not exist before implementation. Its live function definitions and the corrected R3 branches were executed in memory against the required adversarial fixtures.

### Open Questions / Assumptions

No product decision is required. The review treats the plan’s named behavior and source-backed locks as the execution contract and applies the Materiality Gate against deeper same-surface predicate variants.

### Follow-up Actions

No `/plan-corrections` cycle is required. This review workflow stops after recording the verdict; execution remains a separate workflow action by the coordinator.

### Verdict

`approved` — the Round-3 PR-6 census is complete, R3-F1’s concrete quoted-token false-pass is closed against the live functions, F2–F4 remain closed, all required validation executables exist or are explicitly scheduled outputs, and no High/Critical delivery defect survives PR-1–PR-9 plus the Materiality Gate. Executing the plan as written is sufficient to deliver the TTS page and Model Manager without live Hugging Face/Kokoro access in Wave 2.

### Residual Risk

This is a static, findings-only plan review. The helper is a lexical PowerShell census rather than a TypeScript control-flow proof; the required execution review must still run the generated Wave 2 Playwright suite and inspect its fail-closed ledger evidence. No product code, tests, plan files, or implementation handoffs were modified; the sole repository write was this canonical rolling review file. Git-based diff evidence was unavailable because this workspace copy has no `.git` directory.
