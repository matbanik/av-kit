---
date: "2026-11-06"
review_mode: "plan"
target_plan: "docs/execution/plans/2026-11-06-tts-build-capability/implementation-plan.md"
verdict: "approved"
findings_count: 0
template_version: "2.2"
requested_verbosity: "standard"
agent: "codex-independent-reviewer"
loop_id: "s51-plan-2026-11-06-tts-build-capability"
round: 1
---

# Critical Review: tts-build-capability

> **Review Mode:** `plan`
> **Verdict:** `approved`

## Scope

**Intent anchor:** Session 51 makes the backend say, for each model variant, whether this build can run it, from whether the variant's runtime imports in this process. A variant it can't run is listed disabled with a reason that names a next step. Its download is refused with a 409 before any job or file exists, and its load keeps its 422 with the same reason. The TTS page can't select it, and the Settings device select offers only the devices that a runnable variant reports. The dev venv, which has torch and kokoro, keeps loading and generating with the PyTorch variant.

**Intent achieved:** `yes`, as plan readiness; implementation and runtime verification remain future work.

**Target:** working-tree plan and task, Session 51, MEU-117 followed by MEU-118. **Reviewer:** Codex / OpenAI, class `avkit_independent_reviewer`; author Claude Code / Anthropic. **Checklist:** PR-1 through PR-9, Materiality Gate and Verdict Rule.

Observed HEAD: `71d0d3a40f9bb2a3ab37ab9c2880d96079ced0b8`. Both plan files are untracked; implementation rows are unchecked and both implementation handoffs are absent. Unrelated state was left alone. Reviewed the residual specs, issue entries by ID, production adapter/service/routes/MCP/renderer paths, affected test seams, packaging tools and Session 50 helper implementations.

Accepted as given: Mat's scope/order and triage rulings, human review of reason text and disabled styling, scheduled helper creation, token estimate, squashed history, absent GUI references and the stated Session 52/distribution exclusions. All writes were under `C:/Temp/av-kit`. No product suite, app/server, package build, smoke program, network request, model constructor, download, repository mutation, commit or push ran. Forbidden secret/fleet paths were not opened.

## Findings

| # | Severity | Blocking | Kind | Finding | File:Line | Recommendation | Status |
|---|---|---|---|---|---|---|---|

No findings meeting the materiality threshold. No High or Critical finding.

## Checklist Results

Observer for manual procedures: `codex-independent-reviewer`; manual exit code: `null`.

### Information Retrieval (IR)

| Check | Result | Procedure | Exit | Evidence |
|---|---|---|---|---|
| PR-1, PR-2, PR-3: scope, readiness, task contracts | pass | Compare plan work packages/ACs with task rows; inspect target status and handoff existence | null | Same two MEUs and order; implementation unstarted; work and checks assigned. |
| PR-5, PR-7: sources and scope boundaries | pass | Compare residual specs and D-217/D-226/D-236/D-237 with ACs and exclusions | null | Capability/refusal/device scope agrees; later load changes and installer gate have named destinations. |
| PR-6: review/correction readiness | pass | Inspect Handoff Set and H1 review rows | null | Two implementation handoffs, independent review and correction loop specified; round-2 census requirement is not applicable. |
| PR-9: shared contracts | pass | Compare named contract definitions, AC tables and task rows | null | Runtime, reasons, device ordering/floor, smoke and snapshot predicates have identifiable governing definitions. |

### Design Review (DR): Q1–Q8

**Q1 — Done and real paths: accepted.** `MODEL_REFUSAL` belongs before `_start_locked`, which creates the runtime/thread (`services/models.py:229`). REST and MCP reach that service; the only production adapter load call is `ModelService.load` (`:156`). Generate requires an already loaded model (`services/tts.py:226`); settings PUT stores leaves rather than loading/fetching (`routes/settings.py:33`); sideload records existing files. Asset downloads fetch vocab, spaCy or voice packs, not model weights/runtime, so they do not bypass the variant refusal. `CAPABILITY_SMOKE` uses the real frozen executable outside the checkout, fresh app data and stub model/config files, then asserts fields, 409/Idle/unchanged files, 422 and logs (plan `:182–193`). The old executable exists, is 28,160,327 bytes and dates from November 4; its missing fields make the specified first-check Red sound without posting a download.

`DEV_CHECK`'s argv matches `buildDevSpawnArgv` (`python-manager.ts:17`), including both tokens, port 0 and app-data. Its 202 fast path also checks vocab/packs, not just the weight. A read-only, network-blocked probe confirmed all three assets READY and all 54 packs present. English `af_heart` needs no eSpeak installation; spaCy READY prevents the load's auto-download and G2P's install fallback. Offline flags and temporary output support a download-free load/generate check. This review did not run load or generate; row 0 establishes the baseline and row 9 proves the strict guard.

**Q2 — Capability source: accepted.** `from kokoro import KModel` is the import the load actually performs (`adapter.py:303`); package discovery alone would miss import/DLL failures. Torch absent short-circuits before kokoro, preserving `IMPORT_HYGIENE`; torch present with failing kokoro yields unavailable. A per-format memo under a lock is appropriate for the single adapter constructed by wiring (`wiring.py:180`); an injected raising probe propagates without caching an invented answer. `FakeTTSPort` gains the port method and `FakeModels` gains the service facade. The first dev import occupies a synchronous route's worker thread (`routes/models.py:57`), not the event loop; warming before the download lock avoids holding that lock for the recorded approximately 3 seconds. The default probe catches `Exception` and logs only format/class name, without exception text, traceback or path. AC-117.2 checks a synthetic marker in all fields; AC-117.5 checks no kokoro import request with torch absent.

**Q3 — Service/API/MCP: accepted, with one clerical clarification below.** The outside-lock warmup followed by locked in-flight check, row re-read, not-found and capability refusal preserves existing conflict precedence while preventing work on an unavailable variant (plan `:153`). Load refuses after not-found and before legacy/vocab checks (`:154`); runnable legacy ONNX still gets `LEGACY_MODEL_409`. `_variant_out` is the sole `ModelVariantOut` constructor and is used for available, downloaded and accepted variant responses (`routes/models.py:42`). `LOAD_ERROR_HTTP` already maps ModelLoadError to 422 (`errors.py:36`). MCP retains parsed fields and envelope code/message through `client.ts:135–148` and `toToolError` (`:63`); its guard correctly expects TOOL_ERROR rather than an HTTP response object. Explicit descriptions and `mcp-build` cover the source change.

**Q4 — Model selection/G30: accepted.** Optional renderer fields preserve older fixtures/backends. Disabled options and reason labels block choosing unavailable rows; chosen/downloaded/first-row selection skips them and an empty runnable set returns null. Retaining the loaded row is consistent with this plan's process-stable runtime memo: the public service cannot load an unavailable format, and capability is not changed live. It is not a general promise to preserve an unavailable loaded row after dynamic runtime replacement. G30's inline pairs stay on both select and options (`SelectInput.tsx:58–60`); AC-94.2–94.4 remain in scope. No new palette or byte-hash input is required.

**Q5 — Device options/seams: accepted.** `DEVICE_OPTIONS` unions the floor with runnable rows only, filters unknown values, deduplicates and orders through `DEVICE_ORDER`. Pending/error retains a recognized stored value; successful reports show unsupported stored choices as auto without a PUT, leaving `DEVICE_RESOLVE` intact. The Settings tests count relevant methods/URLs, with harmless fallback responses for the new GET; theme-selects already returns an empty item list. The Settings Electron seam currently rejects that route (`settings.test.ts:78`), and row 12 explicitly adds its catalog response. Existing uses remain compatible with the optional seam argument. D-317 substitutes the same floor literal at `TTSPage.tsx:274` and still uses the selected row's devices, not Settings' union. AC-118.4 is an independent behavior guard.

**Q6 — Amended tests: accepted.** Adding the port method preserves AC-4.7's exact method/signature check. AC-98.5's two cases retain their absent-runtime/import-cause, resolved-device and unloaded-state assertions. AC-115.9 retains its real-cause/first-line and empty-detail checks, changing only the torch-absent reason. D-312 A aligns the adapter's two unavailable-runtime messages with the service without changing native initialization/load-failure classification. The remaining old wording occurs in those current adapter/tests and historical/problem descriptions; the plan schedules the active expectation/text changes. No additional live UI/MCP promise of a downloadable runtime was found in the reviewed paths.

**Q7 — Red and guards: accepted.** Required new Python names are checked by assertion before use; the new TS module uses a glob assertion, so absence need not become collection/setup failure. The four amended tests are required by full name. The selected files and `-k` expressions match their row's ACs; no later row's tests share those files under a matching prefix. The copied checker rejects required missing-name failures and digit-prefix collisions (`red-check.py:218`). Separate pytest/MCP receipts avoid mixed summaries. AC-117.11 and AC-118.4 are honestly passing guards, with renderer/service unit negatives preceding their E2E checks. A scratch probe extracted row 8's actual Red predicate and demonstrated rejection of exit 0, a reached download check, the wrong failed check and a missing FAIL banner; the intended Red alone was accepted. No materially missing deliverable was shown to false-pass a task control. Actual Red/Green receipts remain execution work.

**Q8 — Order/safety: accepted.** No reviewed public route bypasses the service to fetch PyTorch weights. New tests use temporary files/fakes; the capability phase writes only its isolated models directory and refuses real/repository locations. The dev prerequisites are currently present, offline mode is set, and `MODELS_SNAPSHOT` compares real files after the named rows and gate. The snapshot is detection, not permission to download. Row 0 copies and hashes the old onedir before package rebuild overwrites ignored output; fresh smoke uses an outside-checkout copy. Session 50's resolver holds a Windows handle denying concurrent writers, checks expected SHA-256 and validates staged semantic differences before replacing content (`issue-resolve.py:171–230`); combined with S3 this is suitable for shared main. No row commits or pushes; the installer/build-record and network/YouTube audit exclusions are justified. MEU-118 follows MEU-117's packaged/dev checks without splitting the session.

### Nonblocking clarification

S6's “two 409 texts” should be read as **two source-text edits**, not two OpenAPI string locations (plan `:159`, task row 4 at `task.md:49`). Shared `CONFLICT_409` is registered on both download and load (`routes/models.py:82`, `:99`), so its edit changes both emitted 409 descriptions; the download docstring is a third emitted string. The probe confirmed those three current locations. The intended diff is unambiguous: two new fields/their required declarations and these three text locations. This count clarification does not omit behavior or justify blocking approval.

### Observed evidence

```json
{"schema_version":"evidence.v1","check_id":"s51-readonly-dev-prerequisites","command":"rtk proxy .venv/Scripts/python.exe -B C:/Temp/av-kit/s51_readonly_probe.py","cwd":"P:/av-kit","scope":"asset readiness, pack sizes and committed OpenAPI strings","phase":"targeted","exit_code":0,"result":"pass","tested_state":"main 71d0d3a; working-tree Session 51 draft; local dev venv and existing models","output":"Network connect and fetch callbacks forbidden; HF_HUB_OFFLINE=1; bytecode disabled. asset_states {'tts_onnx_vocab': 'ready', 'tts_spacy_model': 'ready', 'tts_voice_packs': 'ready'}; ready_voice_packs 54 of 54; python_executable P:/av-kit/.venv/Scripts/python.exe. Both download and load have the shared 409 description; download also has its own operation description.","fresh":true}
```

```json
{"schema_version":"evidence.v1","check_id":"s51-smoke-red-negative-oracle","command":"rtk proxy pwsh -NoProfile -File C:/Temp/av-kit/s51_smoke_guard_probe.ps1","cwd":"P:/av-kit","scope":"task row 8 predicate extracted from current task.md; scratch inputs only","phase":"targeted","exit_code":0,"result":"pass","tested_state":"main 71d0d3a; working-tree task row 8","output":"intended-red: reject=False expected=False; unexpected-pass: reject=True expected=True; download-was-reached: reject=True expected=True; wrong-failed-check: reject=True expected=True; missing-fail-banner: reject=True expected=True","fresh":true}
```

```json
{"schema_version":"evidence.v1","check_id":"s51-plan-contract-trace","procedure":"Read plan/task, residual specs, issue IDs, production callers, test seams and copied helper source; compare Q1-Q8 and PR-1 through PR-9 against the registered goal.","observer":"codex-independent-reviewer","cwd":"P:/av-kit","scope":"Session 51 plan readiness","phase":"targeted","exit_code":null,"result":"pass","tested_state":"main 71d0d3a; working-tree Session 51 draft","output":"Refusals precede model worker/adapter side effects; all variant responses share one formatter; Settings consumes runnable catalog devices; packaged/dev checks and genuine Red predicates are scheduled; no blocking delivery defect found.","fresh":true}
```

Commands also executed: bounded numbered source reads through `s51_review_read.py`; targeted `rtk proxy rg` caller/literal/test-seam searches; Git HEAD/status; read-only file metadata/handoff existence checks. Two broad searches initially returned exit 2 for a Windows wildcard argument and a nonexistent composition filename; narrowed successful searches and `wiring.py` inspection replaced them. Neither failed search is used as absence evidence.

## Verdict

`approved` — executing this plan can deliver the registered goal. No blocking finding; no corrections round required. Carry the S6 count clarification into execution, and preserve Mat's reason/style/execution gates. The coordinator can copy this report unchanged to the canonical review path.

**Residual risk:** this is plan approval, not an installed-build or dev generation pass. The new scripts/tests and their real Red/Green/package/dev evidence do not exist yet; they are explicitly scheduled work. Future execution review must inspect those implementations and receipts. Completion-preflight was applied to the review artifact only; no implementation row was marked complete.

🕐 Completed: 2026-11-06 19:14 (EST)
