---
date: "2026-10-15"
review_mode: plan
target_plan: docs/execution/plans/2026-10-14-tts-engine-runtime/implementation-plan.md
verdict: approved
findings_count: 0
round: 3
template_version: "2.2"
requested_verbosity: standard
agent: gpt-6.1-sol
---

# Critical Review: 2026-10-14-tts-engine-runtime

> **Review Mode:** plan  
> **Verdict:** changes_required  
> **Round:** 1. Independent OpenAI reviewer; author: Claude Code / Anthropic.

## Intent Anchor

> TTS generates offline in the installed app for every listed language it can honestly support, with no GPL code shipped

Executing the plan would substantially repair provisioning and the frozen ONNX path, but achieves this intent only **partially** as written: the installer still ships GPL FFmpeg, existing persisted model paths can retain the incompatible graph, and the smoke can certify generation while network access remains available.

## Scope

**Worktree:** `P:/av-kit-wt/tts-engine-runtime`, branch `claude/s32-tts-engine-runtime`, HEAD `78610200ea2e7efd52318ea95c3e48b6df4993ba`. All repository reads and command working directories used this checkout. The other checkout was used only for the expressly permitted Python interpreter and installed upstream package sources.

**Targets:** `docs/execution/plans/2026-10-14-tts-engine-runtime/{implementation-plan.md,task.md,validate-task.ps1,gate_lib.py,plan_checks.py}`. References below are relative to this worktree; bare plan filenames mean that plan folder.

**Canon sampled:** 03 service-layer voice/runtime residuals; 07 packaged runtime residual; grouping Session 32 and §8; the five named issues in `known-issues.yaml`; current adapter/assets/voices, model/TTS services, REST model entrypoints and database model persistence; packaging spec, electron-builder configuration and FFmpeg fetcher; existing amended tests; Session 30 gate result and named gated paths; p7 NSIS assertion and named sets. Inspected installed kokoro/misaki source and package metadata, plus the three cited planning receipts. Loaded the workflow, local instructions/profile/guardrails, review template 2.2 and latest peer review.

**Mode:** unstarted plan. All 23 task rows remain unchecked; `baseline.sha` and all three MEU implementation handoffs are absent. Git status reports only the untracked plan folder. No tests, builds, npm, uv, generators, `validate-task.ps1` checks or runtime probes were executed. Only the two authorized read-only verifier modes were executed.

## Findings

No Critical findings. F1–F3 block; F4 does not. Severity follows delivery impact, not paperwork completeness.

| # | Severity / Confidence | Blocking | Kind | Finding | File:Line | Recommendation | Status |
|---|---|---|---|---|---|---|---|
| F1 | High / High | yes | behavior | INSTALLER_STAGE ships GPL FFmpeg: its default fetch selects a win64-gpl archive, and electron-builder copies that payload into the app. The TTS import exclusions and forbidden-directory check cannot detect this shipped GPL binary. Contract: PR-8. Subject: deliverable. | implementation-plan.md:144; validate-task.ps1:466-475; tools/fetch_ffmpeg_windows.ps1:3-6; ui/electron-builder.yml:30-31 | Use a pinned non-GPL FFmpeg build and verify the actual staged binaries and build configuration, including pre-existing vendor payloads, before asserting the registered no-GPL goal. | open |
| F2 | High / High | yes | behavior | LEGACY_ONNX_DIR only excludes directory-scan results. Persisted v0.19 model rows still feed ModelService.load directly, and ModelCatalogAdapter.download can return variant.path before using the new repository or revision. Existing users can therefore keep loading the mismatched graph or bypass the promised re-download. Contract: PR-8. Subject: deliverable. | implementation-plan.md:125,207-208,234; packages/core/src/avkit_core/services/models.py:88-131,157-167; packages/infrastructure/src/avkit_infra/model_manager/manager.py:59-64 | Define legacy-path handling for persisted catalog rows, direct load and download cache hits. Refuse legacy loads with a re-download instruction, fetch into ONNX_LOCAL_DIR despite an old persisted path, update the row after success, and test an upgraded database while preserving the old files. | open |
| F3 | High / High | yes | control-defeat | PACKAGE_SMOKE provisions and generates in one network-enabled run. It never denies outbound access or repeats generation from a fresh offline process. A lazy network dependency in the real G2P factory can pass this smoke because the other generation tests replace that factory or G2P seam. **mechanism: online-smoke-certifies-offline** Contract: PR-8. Subject: committable-tooling. | implementation-plan.md:135-143,204,352-359; validate-task.ps1:445-485; gate_lib.py:509-511 | Separate online provisioning from a fresh frozen-process load/generate phase with outbound traffic denied and verified by a negative probe. Run from outside the checkout with an isolated cache and make the offline result a required smoke field checked by windows-gate-check. | open |
| F4 | Medium / High | no | behavior | TEST_AMENDMENTS is incomplete for existing contradictory expectations: test_ac_9_9 still expects the old ONNX cache path, and test_ac_62_9 expects Japanese generation to succeed or report a missing spaCy model. TA-3b describes only seam changes for that latter range; its deletion fence also ends before the Result-shape test ends. Correct implementation will encounter these failures or ta-check refusals. Contract: AGENTS Testing & TDD; non-blocking verification quality. Subject: committable-tooling. | implementation-plan.md:159-162; tests/integration/test_tts_models.py:590-595; tests/integration/test_tts_assets.py:569-578,796-839; task.md:80 | Add narrow source-backed amendments for the legacy-cache and Japanese expectations; preserve the no-spaCy-required intent using a supported non-English voice with an explicit espeak fake. Correct TA-3b's deletion range and row ownership. Keep unchanged assertions intact. | open |

### Decisive static traces

**F1 — shipped bytes, not an import-policy objection.** The plan's `INSTALLER_STAGE` calls `tools/fetch_ffmpeg_windows.ps1` without a non-GPL override. Its default URL explicitly selects `ffmpeg-n8.1.2-44-g7c533d0f86-win64-gpl-8.1.zip`; the script copies `ffmpeg.exe` and `ffprobe.exe` into `packaging/ffmpeg-win64`. `ui/electron-builder.yml:30-31` copies that directory into installer resources. The backend's four-name directory scan and NSIS size assertion both permit this payload. An already existing vendor directory skips even the fetch. This is within the registered whole-app no-GPL goal, although it predates the TTS rewrite. The subprocess separation proposed for espeak does not change the fact that these other GPL binaries are distributed.

**F2 — the scan is not the load authority.** `POST /models/load` → `ModelService.load` → `uow.models.get` → `TTSPort.load_model` does not consult `sideload`. `SqlAlchemyModelRepository.mark_downloaded` persists the path and downloaded flag (`database/repositories.py:352-360`); the mapper restores both. Thus a row already pointing to `{models_dir}/onnx/model_quantized.onnx` survives ignoring the file during a later scan. `POST /models/download` also reads that persisted row; the catalog adapter's existing `variant.path.is_file()` fast path returns it before any HF call. AC-73.9 exercises a scan, while AC-73.8 does not specify this upgraded-database case. Preserve files, but invalidate their use as the official v1.0 variant across these entrypoints.

**F3 — a concrete missing negative oracle.** PACKAGE_SMOKE steps 5–7 download and generate in the same process with network still available. Nothing asserts that outbound access is blocked. A first-use fetch in the default English G2P construction can succeed there and still fail offline. AC-73.5's network-patched generation goes through G2P_SEAM, which substitutes the G2P producer; AC-72.1 also substitutes `misaki_factory`, and AC-72.2 tests factory wiring/guarding with fakes. Those tests therefore do not reject this defect in the real factory. The final checker accepts only `passed`, sample count and forbidden directories; no offline observable exists. This demonstrates the false-pass against the specific offline requirement, rather than demanding more predicate-shape checks.

**F4 — false failures are not delivery false-passes.** `test_tts_models.py:590-595` still requires reuse of the old ONNX path. `test_tts_assets.py:569-578` requires a Japanese request to report missing spaCy and then succeed without chunking, contrary to the new availability-first contract. Those assertions need expressly described amendments, not just seam replacements. TA-3b's deletion range stops at 830, while the Result-shape test continues through 839 (the helper begins at 772). Row 2 also names TA-3b before its table's row-9 ownership. The existing full gate/ta-check will refuse these cases; that is why F4 is non-blocking under this review's materiality rule.

## Checklist Results

Manual checks below were performed by **gpt-6.1-sol** through static reads and cross-file tracing; their exit is null. Command results preserve actual exits.

### Information Retrieval

| Check | Result | Procedure / evidence |
|---|---|---|
| AC source labels | pass | Read every AC/source cell and decision basis; numbered ACs map to spec, canon or sourced decisions. |
| Exact validation cells | pass | Read all 23 task rows and runner dispatch labels; authorized static verifier agrees. |
| BUILD_PLAN audit | pass | Plan lines 395–404 and task row 13 identify concrete hub changes. |
| Handoffs/reflection/metrics | pass | Three handoffs, H1 review and H2 rows are explicit; none are claimed complete. |

### Plan Review Checklist

| Check | Result | Procedure / decisive evidence |
|---|---|---|
| PR-1 Plan/task alignment | partial | MEU-73 → 74 → 72 and all WPs align; F4's TA row ownership needs correction. |
| PR-2 Not started | pass | Status/readiness sweep: 23 unchecked rows, absent baseline/handoffs, only plan folder untracked. |
| PR-3 Task contract | pass | All rows have owner, deliverable, validation, dependency, durable output and status; static reports 23 rows. |
| PR-4 Validation realism | fail | Traced package-smoke and gate-check; offline generation lacks an enforced offline phase (F3). |
| PR-5 Source-backed planning | pass | D-70 human choice, D-71/76 package-source evidence, D-73 comparison receipt and grouped ownership are traceable. Approval of the plan does not follow merely from those labels. |
| PR-6 Handoff/corrections readiness | pass | Three durable handoffs and rolling review destinations are named. Round 1; no correction census prerequisite applies. |
| PR-7 Scope discipline / C2 | pass | UI/device follow-ups name registered MEUs; ja/zh is explicitly D-70; remaining exclusions have real build-plan/decision bases. F1 is not an invented new feature: it conflicts with the registered goal. |
| PR-8 Control reachability/totality | fail | Actual FFmpeg distribution path escapes the exclusion checks; persisted legacy paths bypass scan policy; no offline smoke observable (F1–F3). |
| PR-9 Single-statement discipline | pass | Contract table is the authority; executable GATED_PATHS/floors are cross-checked. Repeated explanatory values do not introduce competing material behavior. |

### Docs Review Checklist

| Check | Result | Procedure / decisive evidence |
|---|---|---|
| DR-1 Claim/state match | pass | Draft plan claims future work; no implementation completion is represented. |
| DR-2 Residual terms | partial | Old-repo references are explained as legacy; existing old-cache assertions remain contradictory (F4). |
| DR-3 Downstream references | pass | Hub audit, OpenAPI, SSOT and handoff paths are scheduled explicitly. |
| DR-4 Verification robustness | fail | F3's online smoke can pass the offline defect; F1's binary is outside the named checks. |
| DR-5 Evidence auditability | pass | Actual verifier commands/exits/output below; existing planning receipts read directly, not represented as new experiments. |
| DR-6 Canon integrity | partial | Scope/order match the residual specs; claimed whole-app no-GPL outcome conflicts with installer provenance. |
| DR-7 Evidence freshness | pass | Current worktree verifier outputs reproduced; 773/133/655 match Session 30's committed authoritative result. |
| DR-8 Completion/residual risk | pass | This report withholds approval; optional LOCAL-ESPEAK remains disclosed as unverified, not a proven runtime pass. |

### Required sweeps and adversarial checklist

- **Path existence:** all named modified-file targets and existing validation dependencies were checked; absent new suites and `tools/smoke_packaged_tts.py` are explicitly scheduled for creation. Package-relative UI/MCP paths were resolved at their real roots, and the `.tsx` suffix was checked rather than treating a regex prefix as a missing `.ts` file. p7 `assert-nsis-pack.ps1` and its `named-sets.json` both exist. No materially missing unscheduled executable found.
- **Dependencies/roles:** grouped MEU ordering, per-MEU TDD/handoffs and H1/H2 continuation are coherent. F2 adds missing upgrade behavior rather than changing that order.
- **Literal sweep:** checked named sets, floors and old-repo vocabulary against runner and prior canon. No ambiguous competing threshold blocks delivery.
- **AV-1/AV-3:** partial at plan time: per-AC Red and feed assertions are prescribed; real offline smoke proof is missing (F3). **AV-2/AV-4:** no planned skip/only/early-return bypass; **AV-5:** absent future implementation files are inventoried, not claimed done; **AV-6:** source labels present. Executed Red/Green and implementation anti-placeholder certification are n/a in this review.

### Commands executed

All shell working directories were `P:/av-kit-wt/tts-engine-runtime`; output was redirected under `C:/Temp/av-kit/s32-review-*.txt`, with LASTEXITCODE captured before reading the receipt. These are the substantive command bodies; redirect/read/exit wrappers did not alter the command results.

| Command / read group | Exit | Observation |
|---|---:|---|
| `rtk proxy git status --short --branch` | 0 | Correct branch; only the plan folder untracked. Git also warned that the user-level ignore file was inaccessible. |
| `git rev-parse HEAD`, `git log -1 --oneline`, `git diff --stat` inside the recorded `rtk proxy pwsh` read batch | 0 | HEAD 78610200ea2e7efd52318ea95c3e48b6df4993ba; no tracked diff. |
| `rtk proxy rg -n '^' docs/execution/plans/2026-10-14-tts-engine-runtime/implementation-plan.md` | 0 | Entire plan read with line references. |
| Same `rg -n '^'` for `task.md`, `gate_lib.py`, `validate-task.ps1`, `plan_checks.py` | 0 each | Entire task/runner/parser/verifier read; receipt rereads were used to avoid truncated views. |
| `rtk proxy rg -n '^' packages/infrastructure/src/avkit_infra/model_manager/manager.py` | 0 | Persisted-path early return and scan implementation. |
| `rtk proxy rg -n '^' packages/core/src/avkit_core/services/tts.py packages/core/src/avkit_core/services/models.py` | 0 | Job ordering and model service paths; relevant complete sections reread. |
| `rtk proxy rg -n '^' packages/infrastructure/src/avkit_infra/tts/adapter.py packages/infrastructure/src/avkit_infra/tts/voices.py` | 0 | Model feeds, 510 guard, catalog and sideload naming. |
| `rtk proxy rg -n '^' P:/av-kit/.venv/Lib/site-packages/misaki/espeak.py P:/av-kit/.venv/Lib/site-packages/kokoro/__init__.py P:/av-kit/.venv/Lib/site-packages/kokoro/model.py` | 0 | Real import chain, conversion tables and model token contract. |
| Targeted `rtk proxy rg` sweeps over upstream English/pipeline, metadata, plan/prior literals, production entrypoints and amended tests | 0 on resolved paths | Confirmed fallback API, licensing metadata, counts and contradictory pins. Two initial persistence-path guesses returned 2; actual `database/repositories.py` and `mappers.py` were then found and read. |
| `rtk proxy pwsh -NoProfile -Command "Get-Content …"` and Test-Path batches | 0 on completed reads | Protocol, instructions, template/peer, canon, packaging, existing tests and planning receipts inspected; future artifact and relative-path results resolved above. |
| Authorized `plan_checks.py static` command below | 0 | 23 rows; static agreement. |
| Authorized `plan_checks.py selftest` command below | 0 | All 12 injected defects reported. |

Two bootstrap attempts to run PowerShell's `Get-Content` directly through RTK failed with exit 1 (`Get-Content` is a cmdlet, not a PATH executable); reads were repeated successfully through `rtk proxy pwsh`. No evidence relies on those failed reads.

```json
{"schema_version":"evidence.v1","check_id":"s32-review-plan-static","command":"rtk proxy P:/av-kit/.venv/Scripts/python.exe docs/execution/plans/2026-10-14-tts-engine-runtime/plan_checks.py static","cwd":"P:/av-kit-wt/tts-engine-runtime","scope":"plan-local static verification only","phase":"planning","exit_code":0,"result":"pass","tested_state":"78610200ea2e7efd52318ea95c3e48b6df4993ba plus the untracked Session 32 plan folder","output":"PASS static: 23 task rows; scripts, plan cross-references and file targets agree","fresh":true}
```

```json
{"schema_version":"evidence.v1","check_id":"s32-review-plan-selftest","command":"rtk proxy P:/av-kit/.venv/Scripts/python.exe docs/execution/plans/2026-10-14-tts-engine-runtime/plan_checks.py selftest","cwd":"P:/av-kit-wt/tts-engine-runtime","scope":"in-memory negative cases of the plan-local verifier","phase":"planning","exit_code":0,"result":"pass","tested_state":"78610200ea2e7efd52318ea95c3e48b6df4993ba plus the untracked Session 32 plan folder","output":"PASS selftest duplicate row id: [\"duplicate row ids: ['0', '0', '1', '2', '3', '4', '5', '6', '7', '8', '9', '10', '11', '12', '13', 'H1-1', 'H1-2', 'H1-3', 'H1-4', 'H1-5', 'H1-6', 'H2-1', 'H2-2', 'H2-3']\"]\r\nPASS selftest unknown check: [\"task.md invokes validate-task.ps1 -Check 'no-such-check', not a switch label\"]\r\nPASS selftest swapped stage: [\"stage order differs: gate_lib ORDER=['npm-ci', 'mcp-npm-ci', 'py-lint', 'py-types', 'ui-types', 'ui-lint', 'mcp-types', 'py-tests', 'ui-tests', 'ui-build', 'ui-harness-build', 'mcp-build', 'mcp-tests', 'openapi', 'state-render', 'ui-electron', 'source-audit'] ps1 $stages=['npm-ci', 'mcp-npm-ci', 'py-types', 'py-lint', 'ui-types', 'ui-lint', 'mcp-types', 'py-tests', 'ui-tests', 'ui-build', 'ui-harness-build', 'mcp-build', 'mcp-tests', 'openapi', 'state-render', 'ui-electron', 'source-audit']\"]\r\nPASS selftest changed floor: [\"COUNT_FLOORS differ: plan=('773', '133', '655') ps1=('700', '133', '655')\"]\r\nPASS selftest dropped GATED path: [\"GATED_PATHS differ: plan=['ui', 'packages', 'mcp-server', 'tests', 'tools', 'packaging', 'pyproject.toml', 'uv.lock', 'openapi.committed.json', 'docs/build-plan', 'docs/proposals', '.agent/docs', '.agent/schemas', '.agent/roles', '.agent/templates', '.agent/skills', '.agent/workflows', '.agent/model-registry.local.json', '.agent/model-registry.local.yaml', 'docs/execution/plans/2026-10-14-tts-engine-runtime/validate-task.ps1', 'docs/execution/plans/2026-10-14-tts-engine-runtime/gate_lib.py'] ps1=['ui', 'packages', 'mcp-server', 'tests', 'tools', 'pyproject.toml', 'uv.lock', 'openapi.committed.json', 'docs/build-plan', 'docs/proposals', '.agent/docs', '.agent/schemas', '.agent/roles', '.agent/templates', '.agent/skills', '.agent/workflows', '.agent/model-registry.local.json', '.agent/model-registry.local.yaml', 'docs/execution/plans/2026-10-14-tts-engine-runtime/validate-task.ps1', 'docs/execution/plans/2026-10-14-tts-engine-runtime/gate_lib.py']\"]\r\nPASS selftest undefined AC: ['task.md references AC-73.99, which has no definition site (AC table row, decision_log id, ### heading, or grouping §8 row)']\r\nPASS selftest undefined decision: ['task.md references D-99, which has no definition site (AC table row, decision_log id, ### heading, or grouping §8 row)']\r\nPASS selftest missing modify target: [\"Files Modified 'modify' row names a missing file: ui/no/such/file.ts\"]\r\nPASS selftest existing new target: [\"Files Modified 'new' row names a file that already exists: pyproject.toml\"]\r\nPASS selftest glob row: ['Files Modified row uses a brace or glob pattern: tests/unit/test_*.py']\r\nPASS selftest AC test outside every set: ['AC-73.98 test file tests/unit/test_nowhere.py is in no validate-task.ps1 test set']\r\nPASS selftest missing goal anchor: ['review-prompt-plan.md does not contain the goal anchor (INTENT_BINDING)']\r\nPASS selftest: every injected defect was reported","fresh":true}
```

These are verifier passes, not product validation or independent approval of the implementation.

## Answers to Q1–Q8

### Q1 — D-71 / D-76 and GPL imports

**The proposed frozen ONNX TTS route can exclude the identified GPL components; the whole shipped-app claim is false as written (F1).** Real `misaki.en` imports num2words/spaCy without importing `misaki.espeak`; the local probe records only misaki, data, en and token loaded with the forbidden packages blocked. Upstream `misaki.espeak:1-4` imports phonemizer and espeakng_loader, whose exclusion is therefore necessary. Excluding kokoro as well as these modules and invoking a separately user-installed CLI avoids distributing that espeak/phonemizer code on the proposed ONNX route. `collect_data_files("misaki")` is not a request to collect its Python source modules.

**There is a real import path the fake PyTorch test would miss:** installed `kokoro/__init__.py:22-23` imports both model and pipeline; `pipeline.py:5` imports misaki.espeak. Even `from kokoro.model import KModel` first initializes that package. A stub kokoro exposing only KModel in AC-72.5 cannot establish the equivalent property for the real package. This concerns the retained development PyTorch route, since kokoro is expressly excluded from the installed bundle; it is not a separate installed-app blocker.

num2words' installed metadata identifies LGPL, not GPL. External replaceable Python source is consistent with D-76's technical approach, but a five-name notices check is not a complete licensing-compliance audit. Carry its copyright and COPYING/license text alongside the replacement instructions. This review establishes package provenance and import paths; it does not grant legal clearance.

### Q2 — D-73 and legacy files

**Mismatch supported; upgrade handling incomplete.** The supplied comparison receipt reports old tokenizer 177 entries, new 115, hexgrad vocab 114; 83 hexgrad symbols differ or are missing in the old tokenizer, while the new tokenizer agrees on all 114 with only `$` extra. It records source SHA256s, including hexgrad config `5abb01e2403b072bf03d04fde160443e209d7a0dad49a423be15196b9b43c17f`. The HF listing identifies revision `1939ad2a8e416c0acfeecc08a694d14ef25f2231` and the three named model files plus all catalog voice filenames.

Those observations support the switch; they are not a new graph inference run. Keeping legacy files untouched is data-safe. Ignoring them only during sideload does not prevent loading/reusing the persisted old path (F2). Re-pinning hexgrad's vocab is a separately disclosed exclusion; do not overstate the receipt as a guarantee about future upstream changes.

### Q3 — D-70 / VOICE_REASON / ASSET_409_ORDER

**Yes, the declared rules are checkable.** AC-74.1 covers all nine language codes in both espeak states, rejects unknown codes, and fixes j/z unavailable, e/f/h/i/p conditional, a/b available. AC-74.3–74.5 connect the status/reason to REST; AC-74.8–74.9 cover disabled choices. AC-74.4 asserts 409, no job and no asset-port call, so availability precedes asset readiness. Asset/model readiness remains separately checked before creating a job; “available” is a G2P capability flag, not a promise that assets are already downloaded. F4 identifies existing expectations that conflict with this new order.

### Q4 — CHUNK_RULE / ONNX_FEEDS

**The size/shape rules are sound:** 510 payload symbols leave two sentinel positions in a 512-token input; filtered ids cannot exceed that payload. A 510-row pack supports rows 0–509, and the explicit empty-id special case avoids negative indexing. int64 input ids, float32 style `(1,256)` and float32 speed `(1,)` agree with the existing feed boundary. Upstream KPipeline uses `pack[len(ps)-1]`, supporting the unpadded-length indexing convention.

AC-72.3 states invariants, not only a short example: nonempty/bounded chunks, preservation/order, preference hierarchy, hard split and empty input. AC-72.4 states observable feed relationships on a recording session. Implement those over varying lengths, distinct style rows, mixed unknown symbols and boundary cuts. No implemented property tests were run or observed. Note explicitly during implementation that ONNX indexes by filtered ids while TORCH_PATH indexes raw phoneme length; unknown-containing input can select different rows. Also preserve the real misaki return/fallback contracts when replacing the fake.

### Q5 — TA-1 to TA-8 approval

**This review approves the narrowly described assertion amendments below as source-backed changes; it does not approve the plan for execution or authorize unlisted expectation changes.** F4 means the amendment inventory/fences are not yet execution-ready.

| Amendment | Assessment |
|---|---|
| TA-1 | Approved: replacing the old HF map with the pinned compatible export is supported by D-73's receipt. Display-size assertions can remain. |
| TA-2 | Approved as described: replace KPipeline-specific plumbing with the equivalent G2P observable, managed-pack error and chunked 511-symbol result. Preserve language, feed and failure-cause assertions. The old-cache pin is an additional amendment still needed. |
| TA-3a | Approved: an inference failure can test a failed job after a missing pack becomes a pre-job refusal. Retain meaningful console error propagation. |
| TA-3b | Approved in intent: seam call counts replace pipeline counts; remove the obsolete Result-shape test only while its real-token assertion is retained in AC-72.4. Fix the incomplete line fence and row ownership. Japanese expectations are not covered by the described seam-only change. |
| TA-4 | Approved: extend health fakes to the new schema fields; no unrelated expectations change. |
| TA-5 | Approved: add the new rows to fixtures and extend the absent-row assertion. |
| TA-6 | Approved: extend the accepted enum cases while retaining unknown-wire rejection. |
| TA-7 | Approved: extend catalog-fixture parity to the two new fields. Its default true/null fixture is a catalog/layout fixture, not a claim that j/z is available through the service. |
| TA-8 | Approved: retain the count assertion and add a separate position/idempotence assertion. |

ta-check does enforce allowed **removed/replaced baseline lines** and append-only declarations. It does not prove semantic minimality, constrain added assertions, or narrow files whose TA entry has no line range. Review still owns those properties.

### Q6 — PACKAGE_SMOKE / INSTALLER_STAGE / WORKTREE_IDENTITY

**Not enough to prove the goal (F1–F3).** A real backend build without stub permission, a real API-generated WAV with >8000 samples, and successful NSIS packaging are useful. They do not prove offline generation while network remains open, and a directory-name check is not an inventory of all frozen/installer code. The smoke uses the backend build output before installer assembly; use the staged resource copy for the final isolated phase where practical. MCP_ENTRY_PROBE is correctly recorded rather than used to block this TTS outcome.

**Code identity binding itself is sound for its declared paths.** One implementation hashes HEAD, the binary diff and sorted untracked file content; both runners record start/end identities, and gate-check compares all four to current identity. This binds both JSONs to the same source tree without a commit, including the runner/parser. It is a source-tree identity, not a hash of downloaded models or installed binary contents. Floors match Session 30 (773/133/655); the final full stages require exit zero. The deliberate closeout exclusions are documented.

### Q7 — Red / Green parsers

**They are useful but not absolute; the final full gate is stricter.**

- **pytest-red:** absent JUnit or unexplained errors fail. A collection error preventing required AC tests from appearing normally triggers missing-AC rejection. Declared-symbol import/attribute failures are explicitly tolerated, even as error elements; this is not a blanket ban on collection errors. Untagged assertion/domain failures inside any TA-listed file are also tolerated. Required AC coverage is checked by tags for the selected files, not by proving each assertion's semantic purpose.
- **vitest-red:** suite-load messages and pending/todo tests fail; untagged failures outside TA files fail; required selected-file AC tags must have an assertion-like failure. TA-file failures and the specified new-symbol call failure are deliberate exceptions.
- **electron-red:** requires at least one failed matching-tag result containing an expect/Expected diagnostic and rejects top-level errors. It ignores other untagged specs and does not reject every other non-assertion result once one decisive result exists. Therefore “every GUI Red fails on expect” is stronger than this parser.
- **Green:** targeted pytest compares failure node identifiers; targeted Vitest compares only fullName and Electron compares displayed file/title/status strings. In particular, a new Vitest failure in another file with the same fullName as a baseline failure can be tolerated. This is a real limitation of targeted baseline tolerance, not proof that the final all-zero gate passes it.
- **ta-check / api-scope:** the former constrains baseline removals, with whole-file exceptions noted above; the latter rejects changed/untracked product files missing from the plan's exact path inventory, including changes committed since baseline. Neither proves test semantics or implementation completeness.

No new blocking parser-shape finding is asserted: the required full gate uses raw tool exit codes with zero tolerated failures and rejects these actual test failures before review. Static/selftest passes validate their stated cross-file predicates, not the Red/Green parsers' entire behavior.

### Q8 — Session 32b boundary

**No essential state is carried only in context.** Row 8 writes the MEU-74 handoff and walkthrough Split record. The fresh session reads task, plan and both earlier handoffs; it uses the same persisted source/test files, baseline.sha, receipts, fixture seam and runner. The execution review consumes all three final handoffs plus walkthrough. Session 32b is not a new ledger or reset. Keep the baseline/census/authorization records in walkthrough and preserve receipt files on this same workstation; later rows already refer to those disk artifacts.

## Verdict

**changes_required** — intent achieved: **partial**. F1–F3 are evidence-backed High findings against PR-8's observable/production-chain/negative-oracle contract and the registered goal. F4 is a non-blocking false-failure/amendment-completeness issue. Passing both plan-local verifier modes does not cure the delivery gaps.

## Follow-up Actions

1. Route corrections through `/plan-corrections`; do not implement product changes under this review.
2. Replace or explicitly resolve the GPL FFmpeg distribution path against the exact registered goal, with a staged-payload negative check.
3. Extend legacy handling through persisted database rows, load and download fast paths; add upgrade-case ACs/tests without deleting user files.
4. Require an independently verified offline frozen-generation phase and bind its result to gate-check.
5. Complete the narrowly sourced amendment proposals/fences and correct TA row ownership. Preserve all unaffected assertions.
6. Re-submit this same plan/loop for round 2 with the required correction census and per-hit dispositions.

**Report output:** `C:/Temp/av-kit/dispatch/s32-plan-review-report.md`. The dispatcher may copy it verbatim to `.agent/context/handoffs/2026-10-14-tts-engine-runtime-plan-critical-review.md`. No repository file was written by this reviewer.

## Corrections Applied (2026-10-14)

Applied by Claude Code (`/plan-corrections`, inline in `/create-plan`). This section records changes; it is not a verdict. The next round is independent (Codex).

### Plan summary

Session 32 (MEU-73 → MEU-74 → MEU-72) repairs TTS provisioning, availability and the frozen ONNX path, so the installed app generates offline. The plan is `docs/execution/plans/2026-10-14-tts-engine-runtime/implementation-plan.md` with `task.md`, `validate-task.ps1`, `gate_lib.py` and `plan_checks.py`.

### Ledger status of round 1

The review ledger refused the round-1 verdict, so loop `s32-plan-2026-10-14-tts-engine-runtime` recorded no round. It refused for two reasons: F1 cites `PR-8`, which is outside the loop's citable set (AC-9, AC-62, AC-72, AC-73, AC-74), and F3 names a mechanism that is not in the closed vocabulary. Neither the verdict nor the vocabulary was edited to force it through. The findings were applied on their merits, and the round stays on record in this file.

### Goal anchor change (D-87, Human-approved)

For F1 the user chose "Scope anchor + notice (Recommended)" (USER_EXPLICIT 2026-10-14). The anchor is now:

> TTS generates offline in the installed app for every listed language it can honestly support, with no GPL code in the TTS runtime

The ledger has no way to amend an anchor, so round 2 runs under a new loop, `s32-plan-2026-10-14-tts-engine-runtime-v2`. **Round cap:** this file already holds round 1 and `review-check` caps it at 3 rounds, so loop v2 gets at most two dispatches (file rounds 2 and 3).

### Changes by finding

| Finding | Change | Where |
|---|---|---|
| F1 (GPL FFmpeg shipped) | • The anchor and a "Scope of 'no GPL'" paragraph limit the claim to the TTS runtime: the frozen backend and everything it loads in process.<br>• FFmpeg stays a GPL build that ships as a separate program: User Review item 6, D-87, Out of Scope, and follow-up `FFMPEG-GPL-BUILD` filed at H2-2.<br>• `NOTICES` now lists six components: FFmpeg (GPL-3.0, BtbN build id, source and build URLs, `resources/ffmpeg/LICENSE.txt`) and num2words with its LGPL-2.1 text.<br>• `fetch_ffmpeg_windows.ps1` copies the archive's `LICENSE.txt`, and exits 6 when it is missing.<br>• `INSTALLER_STAGE` asserts `notices_staged` and `ffmpeg_license_staged`, and `windows-gate-check` refuses either one being false.<br>• AC-72.7 and AC-72.9 extended. Stop condition S8 added. | `implementation-plan.md:21-25, 118, 147, 152, 381, 383, 397, 417, 487, 666-676`; `validate-task.ps1:470-491`; `gate_lib.py:478-531` |
| F2 (legacy v0.19 path still loadable) | • New contract `LEGACY_ONNX_PATH` with the pure `is_legacy_onnx_path(path, models_dir)`.<br>• For a legacy row, `list_available` reports it as not downloaded, and `load` raises 409 `LEGACY_MODEL_409` without calling the port.<br>• The `download` fast path is skipped for a legacy row. The fetch goes to `ONNX_LOCAL_DIR` at `ONNX_REVISION`, and `mark_downloaded` updates the row.<br>• User files are never written, moved or deleted.<br>• One path helper, `variant_local_path`, added to `avkit_infra.tts.voices`.<br>• New AC-73.15 tests list and load on an upgraded real SQLite file, with an unchanged sha256. New AC-73.16 tests the re-download.<br>• User Review item 3 and D-73 updated. | `implementation-plan.md:111, 130, 234-235, 249-256, 269`; `validate-task.ps1` `PY_SYMBOLS['73']` |
| F3 (smoke never denies network) | • `PACKAGE_SMOKE` now runs in three steps: `ONLINE_PROVISION` → `INSTALLER_STAGE` → `OFFLINE_SMOKE`.<br>• `OFFLINE_SMOKE` runs the installer's own `resources/avkit-backend`, copied to `C:/Temp/av-kit/s32-smoke-run`.<br>• It runs in a fresh process, with its cwd outside the checkout, fresh app-data, HF and XDG caches, and every proxy variable set to `http://127.0.0.1:9`. It generates a WAV of more than 8000 samples.<br>• `NEGATIVE_PROBE` then shows that a real download in the same environment ends `Failed`.<br>• `windows-gate-check` refuses the result if any offline field is missing or wrong: schema `s32-package-smoke.v2`, the backend dir must be outside the checkout, and the proxies must be dead.<br>• Residual stated in D-88 and User Review item 7: the network is denied at the proxy level, so a raw socket that ignores the proxies is not covered. | `implementation-plan.md:119, 148-152, 194-195, 382, 396, 445, 677-686`; `validate-task.ps1:445-506`; `gate_lib.py:478-531` |
| F4 (TEST_AMENDMENTS incomplete) | • TA-9: in `test_ac_62_9`, `jf_alpha` becomes `ef_dora`, with espeak reported available.<br>• TA-10: `test_ac_9_9` expects the `variant_local_path` destination.<br>• TA-3b fence widened to `test_tts_assets.py:25, 556-582, 772-839`. | `implementation-plan.md:166-180` |
| Census siblings of F2/F4 | • TA-11: the `TtsAsset` value list gains `tts_voice_packs`, and the ordering tuples include it.<br>• TA-12: `put_weights` uses `variant_local_path`.<br>• TA-13: the `test_ac_9_10` sideload goes under `kokoro-v1.0-onnx/onnx/`.<br>• Recorded as unaffected, with reasons: `test_sqlite_uow.py:828-840`, and five renderer and MCP voice-row fixtures. The fixtures stay valid because `VoiceOut.available`/`reason` are optional in the renderer type; MEU-74's `tts-voices.ts` row says so. | `implementation-plan.md:178-188, 338` |

The task rows (2, 3, 5, 9, 10, 12, H2-2) and the `task.md` exit criteria were updated to match. That includes "TA-1 to TA-13 (with TA-3a and TA-3b)".

### Census receipts

`C:/Temp/av-kit/census-s32-*.txt`:
- stale-string sweeps for the old anchor, `TA-1..TA-8`, `five components`, `s32-package-smoke.v1` and the `smoke.*` fields: 0 live hits, apart from the quoted D-87 decision;
- `legacy-onnx-tests`: TA-10 to TA-13;
- `jz-voices` and `espeak-voices`: TA-9;
- `voice-rows`: the unaffected fixtures;
- `gpl-buildplan`: `03-service-layer.md:449` "Never bundle espeak-ng", which is consistent with the plan.

### Verification

| Check | Result | Receipt |
|---|---|---|
| `plan_checks.py static` | PASS (23 task rows; scripts, cross-references and file targets agree; every D-id and AC is defined) | `C:/Temp/av-kit/s32-plan-static.txt` |
| `plan_checks.py selftest` | PASS (every injected defect reported, including a missing goal anchor) | same |
| `lint_task_contract.py --allowed-builder-classes avkit_builder,avkit_coordinator,avkit_verifier` | OK (23 rows fully checked) | `C:/Temp/av-kit/s32-plan-lint.txt` |
| `validate-task.ps1` PowerShell parse | 0 errors | — |
| `gate_lib.py` `py_compile` | ok | — |

No production code and no test file was edited. Only plan artifacts changed, as the planning write scope requires.

🕐 Completed: 2026-10-15 00:00 (EDT)

## Recheck (2026-10-15)

**Rolling report round:** 2. **Ledger:** `s32-plan-2026-10-14-tts-engine-runtime-v2`, round 1. **Reviewer:** `gpt-6.1-sol` / OpenAI, project-overlay class `avkit_independent_reviewer`; author Claude Code / Anthropic. No plan, product, test, canonical review or ledger file was edited by this reviewer.

### Intent Anchor

> TTS generates offline in the installed app for every listed language it can honestly support, with no GPL code in the TTS runtime

Executing the revised plan achieves this intent **partially**: the provisioning, managed legacy upgrade, packaging exclusions and offline smoke are substantially specified, but the non-English G2P conversion contract copies the wrong upstream mapping. The verdict concerns delivery of that language behavior. FFmpeg's GPL build is excluded from this goal by the user's D-87 decision; its disclosure and staged licence remain in scope.

### Round-2 Findings

No Critical findings. F5 alone blocks. The surviving F4 remainder is now Low/clerical: the intended fence endpoint is trivially inferable, and it is not escalated into a delivery blocker. Neither finding is classified as control-defeat, so neither invents a mechanism outside the closed vocabulary.

| # | Severity / Confidence | Blocking | Kind / Subject | Finding | File:Line | Recommendation | Status |
|---|---|---|---|---|---|---|---|
| F5 | High / High | yes | behavior; deliverable | ESPEAK_G2P applies English EspeakFallback.E2M to the supported non-English languages. That table changes e to A and removes nasalization, whereas upstream EspeakG2P uses a different multilingual mapping. AC-74.6 can validate the wrong table and the mandatory smoke generates only English, so incorrectly converted Spanish, French, Hindi, Italian or Portuguese can pass the gates. Contract: AC-74. | docs/execution/plans/2026-10-14-tts-engine-runtime/implementation-plan.md:139; docs/execution/plans/2026-10-14-tts-engine-runtime/implementation-plan.md:305; P:/av-kit/.venv/Lib/site-packages/misaki/espeak.py:14-29,71-107 | Define separate source-backed multilingual and English-fallback conversion contracts. Preserve the multilingual EspeakG2P mapping and normalization, and require distinguishing fake-runner assertions such as non-English e remaining e and nasalization being preserved. Keep GPL imports excluded. | open |
| F4 | Low / High | no | clerical; committable-tooling | The F4 amendment correction is partial: TA-2 still fences the 511-symbol case only through baseline line 690, but its generate call is line 691. Replacing the raises assertion with the prescribed two-chunk success case normally changes that line, and ta-check rejects the correct test edit. Contract: AC-72. | docs/execution/plans/2026-10-14-tts-engine-runtime/implementation-plan.md:168; tests/integration/test_tts_models.py:687-691; docs/execution/plans/2026-10-14-tts-engine-runtime/gate_lib.py:353-380 | Extend only TA-2's final range through baseline line 691. Preserve the source-backed two-chunk assertions and all unrelated expectations. | open |

**F5 decisive source comparison.** Installed `misaki/espeak.py` has two deliberately different conversion paths:

- `EspeakFallback.E2M`, lines 14-29, is the English fallback table. Among its rules are `e -> A`, `r -> ɹ`, `x -> k` and removal of the combining nasal tilde.
- `EspeakG2P.e2m`, lines 71-85, is used for the non-English languages. Its v1.0/default rules include `o^ʊ -> O`, `ə^ʊ -> Q`, `d^z -> ʣ` and `t^s -> ʦ`; ordinary `e` and nasalization are preserved. Its additional normalization is at lines 87-107.

The plan explicitly ports the uppercase `E2M` table (lines 105, 139, 330) and tests one sample per rule (305). Applied literally to a multilingual segment containing `e`, it produces `A` where the upstream multilingual path produces `e`; a nasal vowel loses its nasalization. This is a new language-delivery defect, not a deeper version of F1-F3. Unit tests that merely reproduce that same table agree with the defect. The required frozen smoke uses `af_heart`; LOCAL-ESPEAK is optional and tests only Spanish. Thus the final gates need not reject this wrong-language conversion. The solution can remain entirely Apache source plus the user's CLI; restoring GPL imports is unnecessary.

### Prior Pass Summary and Confirmed Fixes

“Fixed” below means the **plan correction** closes the prior planning finding; no future product implementation is certified.

| Finding | Recheck result | Current evidence |
|---|---|---|
| F1 — whole-installer no-GPL claim | **fixed under the revised scope** | Plan:21-25 and :118 preserve the user's scope change. NOTICES at :147 names separately shipped GPL-3.0 FFmpeg, build/source locations and its licence path. AC-72.7/:381 prescribes the fetcher's missing-licence exit-6 test and successful copy. Runner:470-491 fetches when any payload/licence file is missing and checks staged notice content and a nonempty licence. Parser:514-517 requires both booleans. :417 and task H2-2 preserve the follow-up. The FFmpeg build itself is not reopened. |
| F2 — persisted legacy ONNX bypass | **fixed for the managed v0.19 upgrade paths** | LEGACY_ONNX_PATH at plan:130 covers list, load before the port, and the persisted-path download fast path. AC-73.15/:234 and AC-73.16/:235 require an upgraded real SQLite file, zero load calls, fetch revision/local-dir arguments, updated persistence and unchanged legacy-file sha256. Files Modified:249-256 assign the actual owners. This addresses the real ModelService.load -> stored row -> TTSPort.load_model and catalog.download early-return paths. |
| F3 — online smoke certifies offline | **fixed, with D-88's explicit residual** | Plan:148-152 separates online provisioning from a new offline process, copies the staged installer backend outside the checkout, isolates caches/app-data, sets dead proxies, and requires both a WAV and a failing real download. Runner:445-507 wires those phases; parser:506-530 requires v2, matching identities, offline success/samples, failed negative probe with an error, an external backend path and dead uppercase proxies. D-88/:677-686 accurately limits this to proxy-honoring clients. This closes the missing offline observable without claiming OS-level isolation. |
| F4 — contradictory old expectations/fences | **partially fixed** | TA-9/:176 preserves the no-spaCy non-English intent with `ef_dora` and a present-espeak fake; TA-10/:177 moves the cache fixture to the canonical destination; TA-3b/:170 now covers baseline :772-839; task rows 2/5/9 and :80 assign the amendments coherently. Census siblings TA-11/:178, TA-12/:179 and TA-13/:180 cover asset tuples, weight setup and sideload destinations. The remaining TA-2 endpoint is documented in the round-2 F4 row. |

### Correction Census Recheck

Read every `C:/Temp/av-kit/census-s32-*.txt` receipt, the canonical Corrections Applied section (:235-254), and plan:165-188. The receipts are not terminal-tail truncations. The TA table and unchanged-sibling prose provide the substantive dispositions, rather than merely a hit count:

| Census hit / sibling | Disposition checked against current source |
|---|---|
| `test_tts_models.py:590,592` | updated by TA-10; cache fast path remains tested. |
| `test_tts_models.py:605-608` | updated by TA-13; sideload metadata assertions remain unchanged. |
| `test_tts_assets.py:253` | updated tuple through TA-11; j/z here test the pure asset selector, not generate availability. |
| `test_tts_assets.py:569,577` | updated by TA-9; Spanish with espeak replaces Japanese. |
| `test_tts_models.py:99,103-110` | confirmed-consistent catalog-ID literals: D-70 keeps j/z listed; no expected ID is removed. |
| `test_tts_assets.py:163-171` | updated by TA-12; persistence setup remains intact. |
| `test_sqlite_uow.py:828-840` | confirmed-consistent; repository persistence at a root-level arbitrary path does not exercise the managed legacy-dir policy (plan:184). |
| `voice-combobox.test.tsx:20-30,88,157,170` | confirmed-consistent; optional renderer fields preserve old rows and French matching. |
| `tts-page.behavior.test.ts:43-45`, `tts-page.test.ts:245-251`, `tts-generate.test.ts:167`, `tools-parity.test.ts:126` | confirmed-consistent under plan:186,338; API availability fields still mandatory. |
| `tts-voices.json` and `test_tts_voice_fixture.py` | updated by TA-7, retaining catalog parity. |
| Renderer `tts-voices.ts` / `VoiceCombobox.tsx` filenames in the voice-row inventory | updated by MEU-74 Files Modified:337-338. |
| `03-service-layer.md:449` | confirmed-consistent: espeak-ng is never bundled. |

**Audit note:** three stale-string receipts (`PACKAGE_SMOKE_passes_`, `package_smoke_smoke_`, `steps_1_8_`) contain an invalid Windows wildcard-path diagnostic, not successful zero-hit evidence. I did not count those diagnostics as zero hits. The live plan/task/runner/parser literal sweep was repeated independently; the old broad goal occurs only in the historical D-87 explanation, and no v1 smoke-schema contract remains. The meaningful corrections and impacted test siblings are observable directly above. These receipt/disposition-label details do not supply a delivery-level blocker under the user's goal-scoped materiality instruction.

### Answers to Q1-Q8

**Q1 — licensing and disclosure.** The proposed **frozen ONNX route** keeps the identified GPL packages out of process: direct `misaki.en` does not import `misaki.espeak`; the installed source and import-probe receipt agree. SPEC_BUNDLE excludes kokoro, phonemizer, espeakng_loader and misaki.espeak; IMPORT_HYGIENE blocks the first four imports and inspects loaded modules. The user-installed espeak CLI remains a separate program. num2words 0.5.14's actual COPYING begins “GNU Lesser General Public License / Version 2.1”; collecting replaceable .py files plus that text is consistent with the plan's LGPL exception. This is a source/package review, not certification of a future built archive. The FFmpeg disclosure and licence-copy checks are enforceable as traced under F1.

There **is** a distinct import trap in the retained dev PyTorch path: real `kokoro/__init__.py:22-23` imports both KModel and KPipeline, and `kokoro/pipeline.py:5` imports misaki.espeak, which imports GPL phonemizer and espeakng_loader. Importing `kokoro.model` normally still initializes the parent package. AC-72.5's stub kokoro package does not model this. This does not demonstrate GPL code in the frozen backend, because SPEC_BUNDLE excludes kokoro and torch there; it is a disclosed limit of the broader “KPipeline is never imported” dev-path claim, not a new blocker against the scoped installed-app goal.

**Q2 — catalog/version and legacy paths.** The cited comparison receipt records 83 differing/missing old-tokenizer symbols, all 114 hexgrad vocab symbols matching v1.0-ONNX, one extra pad symbol, and source hashes. The HF listing records the exact pinned revision and required model/voice filenames. This supports D-73; I did not rerun the network comparison. The new named helper plus list/load/download ACs closes the specific managed upgrade bypass F2 identified while preserving user files. It is **not** a content-authentication guarantee for any arbitrary user-sideloaded ONNX file: the plan deliberately accepts sideloads elsewhere. Claims that absolutely no relocated v0.19 file can load would exceed this path-based contract.

**Q3 — honest availability and 409 ordering.** Yes, the enumerated policy is checkable: plan:137 and AC-74.1/:300 require all 9 codes × 2 espeak states, including invalid-code rejection. AC-74.3/:302 checks wire values; AC-74.4/:303 checks pre-asset/pre-job refusal. ASSET_409_ORDER/:135 identifies the production `TtsService.generate` point before the existing job insertion (`services/tts.py:163-165`). Thus j/z are unavailable always, e/f/h/i/p require espeak, and a/b are available independent of espeak **subject to the separate model/asset prerequisites**. Correct flags do not rescue F5's incorrect phoneme conversion once a voice is enabled.

The English fallback also needs the real upstream callback shape during implementation: `misaki/en.py:665,700` passes an MToken and unpacks `(phonemes, rating)`; a text/locale CLI method is not directly that callback. A small bridge must read `token.text`, bind a/b, return the tuple and apply English-specific normalization. AC-72.2's fake factory only checks fallback wiring. This is an implementation obligation behind the plan's `<ESPEAK_G2P for a/b>` notation, not a separate finding asserting that an otherwise evident wrapper cannot be written.

**Q4 — chunks and feeds.** The 510-symbol cap is appropriate: the existing adapter admits at most 510 mapped IDs before the two pad tokens, and upstream KModel checks `len(input_ids)+2 <= context_length` (`kokoro/model.py:128-131`). For a (510,256) raw pack, lengths 1 and 510 select rows 0 and 509; empty mapped IDs explicitly select row 0. Filtering unknown symbols before ONNX style selection is stated consistently; the intentional PyTorch string-length difference is documented. AC-72.3 specifies invariants (nonempty, bounded, order preservation), precedence, hard split and empty input, not just one sample. AC-72.4 specifies recorded feed observables and chunk multiplicity; it does not promise a property-testing framework or exhaustive generated inputs. These are future tests, not existing passed properties. Boundary trimming must follow the named concatenation rule. F4 is a fence issue in changing the old 511-symbol regression, not evidence that the 510 rule is wrong.

**Q5 — amendment approval.** I approve the **substantive expectation changes** TA-1, TA-2, TA-3a, TA-3b and TA-4 through TA-13 as source-backed and appropriately narrow. This is approval of those described amendments, **not approval of the plan as a whole** and not blanket permission for other expectation changes. TA-2's mechanical range remains incomplete (F4); extend it through 691 before applying the prescribed test rewrite.

| Amendment | Basis / minimality recheck |
|---|---|
| TA-1 | D-73 changes the official repository/revision/destination; preserves PyTorch and display-size expectations. |
| TA-2 | Replaces a removed pipeline seam, retains language/feed/missing-file observables, and replaces the old 511 rejection with D-78's two chunks. Final fence endpoint needs F4's correction. |
| TA-3a | A missing managed pack now fails before job creation; a session failure preserves the failed-job logging test. Keep the unchanged console-field assertions (including the chosen fake error text) rather than weakening them. |
| TA-3b | Removed Result-unpacking subject may be deleted; AC-72.4 retains the original non-pad phoneme-feed oracle. Range now covers the whole helper/test through 839. |
| TA-4 | New health fields need fixture additions; old field/error/auth behavior remains. |
| TA-5 | New Settings rows need fixture additions plus the absent-row assertion; old row assertions remain. |
| TA-6 | Adds only the new managed-asset wire to parity enumeration. |
| TA-7 | Catalog fixture gains default availability/reason without removing voice IDs or parity. Runtime API availability is tested separately. |
| TA-8 | Existing count assertion is unchanged; new append-position assertion strengthens it. |
| TA-9 | D-70 makes Japanese unsuitable for this test; Spanish with present espeak preserves the original “non-English without chunk needs no spaCy” behavior and 409/201 assertions. |
| TA-10 | D-73 moves the official offline cache; the no-HF-call assertion remains. |
| TA-11 | Adds VOICE_PACKS in declaration order; invalid-voice checks remain. |
| TA-12 | Fixture setup uses the same destination as production; persisted downloaded state remains. |
| TA-13 | Official sideload fixture moves out of the intentionally ignored legacy dir; original metadata assertions remain. |

`ta-check` parses these baseline ranges and refuses removed/changed old lines outside them; append-only files cannot remove old lines. It is a **range fence**, not a semantic proof of minimal edits: new lines are unrestricted and some declared fixture files are whole-file allowances. The actual diff and Red/Green evidence still need independent execution review.

**Q6 — frozen offline smoke and identity.** The revised producer contract tests the correct deliverable: the staged installer's frozen backend, copied outside the worktree, a new process, isolated app-data/HF/XDG caches, managed assets provisioned first, dead HTTP proxies, a >8000-sample WAV, then a real download failure. D-88 is honest about proxy-level denial; this does not assert firewall isolation or exercise every supported CLI language.

The checker rejects missing/wrong required fields for schema, online success/forbidden directories, installer exits/notices/licence, offline success/samples, negative-probe state/error, external backend path, and the three uppercase proxies. **No, it does not refuse every descriptive offline field's absence:** `offline.cwd`, lowercase proxy entries and NO_PROXY are not read at `gate_lib.py:518-530`; fresh-cache paths are producer obligations rather than independently hashed evidence. Record that limit once; it is not a new escalating F3 blocker. Both result JSONs must carry the same start/end identity as the current reviewed source tree (:479-510). That hash includes HEAD, the full gated diff and untracked gated bytes (:105-113), so no commit is required. It binds source inputs; it does not independently hash provisioned external cache contents or every tool installation.

**Q7 — Red/Green parsers and fences.** They reject ordinary collection/launch errors, missing run-set ACs and newly failing test identities, but an unconditional “no false-pass” claim would be too strong:

- `pytest-red` requires nonzero exit plus JUnit and a failing assertion or declared-symbol failure for each AC whose test file is in that run. It rejects unrecognized failures. However :170-172 tolerates a declared-symbol ImportError even when its JUnit element is a collection `error`; no separate suite/collection rejection exists. Assertion failures anywhere in a TA-listed module are also tolerated and require human disposition. Those allowances are not proof that every failure was the intended Red.
- `vitest-red` rejects suite messages and pending/todo tests, then requires tagged AC failures. TA-file failures may be untagged; matching failure-message words are a heuristic, not stack-origin validation. `Unable to find` is deliberately accepted for renderer tests.
- `electron-red` rejects top-level errors and needs a tagged expect failure. It does not iterate other failures to reject them; one decisive tagged failure can coexist with an additional timeout in the result. The actual runner limits this to the named AC-74.9 spec.
- Green parsers compare current failure identities to the captured baseline and reject new ones; nonzero exit with no recognized failure is rejected. A changed failure cause inside an already failing baseline identity is not distinguished. Final windows-gate separately requires every native stage to exit zero and zero failure counts.
- `ta-check` and `api-scope` enforce line-removal ranges and exact changed-file inventory, respectively. They do not prove assertions are meaningful, and additions are allowed. No parser probes or synthesized parser inputs were executed in this static review.

These are bounded evidence limitations, not a demonstrated full-gate certification of a materially missing product deliverable. I do not turn them into new blocking predicate mutations.

**Q8 — Session 32b.** No required contract is carried only in conversation. Plan:85-95 and task row 8 name the same plan/task, both completed MEU handoffs, the split/context entry and receipt locations. Baseline SHA, census dispositions, immutable-assertion amendments, G2P_SEAM's switch and decisions have durable owners. Row 9 resumes MEU-72 against those files; it does not reset the plan, review cap or evidence identity. No product handoffs exist yet because execution has not started.

### Checklist Results

Observer for all manual procedures below: **gpt-6.1-sol**; exit code **null**. Commands executed separately are recorded in the evidence blocks below.

| Check | Result | Observed procedure / decisive evidence |
|---|---|---|
| PR-1 Plan/task alignment | partial | Read all 23 rows against the MEU contracts and runner dispatch; substantive order matches, F4 remains. |
| PR-2 Not started | pass | Current status is only the untracked rolling report and plan folder; baseline.sha, three implementation handoffs and future smoke tool are absent. |
| PR-3 Task contract | pass | All rows carry owner/deliverable/validation/status and dependencies; static reports 23 rows. |
| PR-4 Validation realism | partial | Existing executables exist; future smoke is inventoried. Gates run the named tests, but wrong multilingual expectations can pass (F5). |
| PR-5 Source-backed planning | partial | Sources and D-87 are explicit; the multilingual mapping claim does not match its cited upstream source. |
| PR-6 Corrections readiness / census | partial | Raw hit inventories and substantive impacted/unaffected dispositions inspected above; erroneous wildcard “zero-hit” receipts excluded. No absent correction package is inferred from their diagnostic text. |
| PR-7 Scope discipline / C2 | pass | Grouping names the deferred MEUs; D-70 and the user's D-87 support ja/zh and FFmpeg exclusions; other exclusions cite actual residual specs. |
| PR-8 Reachability / negative oracles | partial | Legacy services, pre-job checks and new offline negative observable have named callers. Multilingual conversion negative oracle is wrong (F5). |
| PR-9 Single-statement discipline | pass | Named contracts govern repeated values; static confirms runner stage/floor/path agreement. No material conflicting live enumeration found. |
| DR-1 Claim/state match | pass | Plan remains draft/unstarted, with corrections described as planning only. |
| DR-2 Old terms | pass | Old ONNX source and old whole-app anchor remain only as explicitly historical/migration context. |
| DR-3 Downstream references | pass | Concrete build-plan/OpenAPI/SSOT updates are assigned, not claimed already completed. |
| DR-4 Verification robustness | partial | F1-F3 corrections are enforceable; F5's expected conversions can still certify wrong language behavior. |
| DR-5 Evidence auditability | partial | Authorized verifier outputs reproduced; failed read/glob diagnostics excluded from positive evidence. |
| DR-6 Canon integrity | partial | Scope matches the registered residuals, but ESPEAK_G2P diverges from the upstream non-English path. |
| DR-7 Freshness | pass | Current static/selftest results reproduced; Session 30 result contains Vitest 773/0, Electron 133/0/0 and pytest 655/0. |
| DR-8 Completion / residual risk | pass | No implementation completion is asserted; LOCAL-ESPEAK and proxy-denial limits are explicit. |
| IR source labels / exact cells / hub / closeout rows | pass | Read AC tables, decision log, task rows and BUILD_PLAN audit; all are explicit. |
| AV-1 / AV-3 | partial | Future TDD and observable assertions are specified; F5's conversion oracle is incorrect. |
| AV-2 / AV-4 / AV-5 | n/a | No product implementation or executed Red/Green to certify; the plan does not authorize skip/only/placeholder completion. |
| AV-6 | partial | Source labels exist; F5 identifies the concrete source mismatch. |

**Nine sweeps performed:** plan/task agreement; unstarted status; roles/ownership; command specificity; dependency ordering; source traceability; evidence-backed exclusions; path existence; repeated literal census. The existing tools invoked by the runner, p7 assertion/named sets, package lockfiles and packaging spec exist. `tools/smoke_packaged_tts.py` and new test suites are scheduled as new files; baseline and handoffs are execution outputs. No missing unscheduled material executable was found. No project tests, builds, package managers, generators or validate-task checks were run.

### Commands Executed and Evidence

All shell working directories were `P:/av-kit-wt/tts-engine-runtime`. Each shell process used `rtk proxy`, all-stream scratch receipts under `C:/Temp/av-kit/`, and preserved LASTEXITCODE before receipt display. Reads used `pwsh -NoProfile -Command` (the bootstrap used legacy powershell for Get-Content only). The sole other-checkout accesses were the authorized interpreter and installed upstream packages.

| Actual command / operation | Exit / observation |
|---|---|
| `rtk proxy P:/av-kit/.venv/Scripts/python.exe docs/execution/plans/2026-10-14-tts-engine-runtime/plan_checks.py static` | 0; exact output below. |
| Same command with `selftest` | 0; all 12 named negative cases below. |
| `git status --short --branch`, `git log -1 --format="%H %s"` inside the rtk-proxied pwsh read batch | Native commands completed; HEAD `78610200ea2e7efd52318ea95c3e48b6df4993ba`, branch `claude/s32-tts-engine-runtime`; only the untracked review/plan. Git warned that the user-level ignore file was inaccessible. |
| Numbered UTF-8 Get-Content reads of all five targets, prior rolling review/template, instructions, role, harness, current focus/issues, schema/vocabulary/overlay | Manual source observations with the read receipts; no product execution. |
| Get-Content of `C:/Temp/av-kit/census-s32-*`, the three named planning receipts and HF listing | Reviewed existing artifacts as data; no old claim substituted for a new run. |
| Numbered reads of installed misaki/espeak.py, misaki/en.py, kokoro init/model/pipeline, metadata and num2words COPYING | Actual upstream contracts and licence identifiers inspected. |
| Targeted rg over upstream imports/fallback/model-limit, current model/TTS/asset paths, known issue IDs and Session 30 gate contracts; Test-Path of named runner dependencies | Read-only traces and existence sweep described above. |
| `rg -n -F -e "510" -e "TA-1" -e "LEGACY_ONNX" -e "no GPL code shipped" -e "s32-package-smoke.v1"` with the four current plan/task/runner/parser paths | Completed live repeated-literal sweep; no v1 smoke contract; old broad anchor only in D-87's historical explanation. |

Two exploratory `rg` operands containing Windows filename wildcards were rejected with os error 123; exact metadata paths were then resolved/read. An attempted Session-31 peer review read and a guessed `licenses/COPYING` path were absent; the actual latest available peer (Session 30) and `num2words-0.5.14.dist-info/COPYING` were read instead. PowerShell nonterminating read diagnostics are not treated as successful evidence merely because a later command returned zero.

```json
{"schema_version":"evidence.v1","check_id":"s32-r2-plan-static","command":"rtk proxy P:/av-kit/.venv/Scripts/python.exe docs/execution/plans/2026-10-14-tts-engine-runtime/plan_checks.py static","cwd":"P:/av-kit-wt/tts-engine-runtime","scope":"plan-local read-only verification","phase":"planning","exit_code":0,"result":"pass","tested_state":"HEAD 78610200ea2e7efd52318ea95c3e48b6df4993ba plus current untracked Session 32 plan artifacts","output":"PASS static: 23 task rows; scripts, plan cross-references and file targets agree","fresh":true}
```

```json
{"schema_version":"evidence.v1","check_id":"s32-r2-plan-selftest","command":"rtk proxy P:/av-kit/.venv/Scripts/python.exe docs/execution/plans/2026-10-14-tts-engine-runtime/plan_checks.py selftest","cwd":"P:/av-kit-wt/tts-engine-runtime","scope":"in-memory negative cases of the plan verifier","phase":"planning","exit_code":0,"result":"pass","tested_state":"HEAD 78610200ea2e7efd52318ea95c3e48b6df4993ba plus current untracked Session 32 plan artifacts","output":"PASS selftest duplicate row id; unknown check; swapped stage; changed floor; dropped GATED path; undefined AC; undefined decision; missing modify target; existing new target; glob row; AC test outside every set; missing goal anchor. PASS selftest: every injected defect was reported","fresh":true}
```

Decisive exact verifier output:

```text
PASS static: 23 task rows; scripts, plan cross-references and file targets agree
PASS selftest: every injected defect was reported
```

### Verdict

**changes_required. Intent achieved: partial.** Correct F5's multilingual conversion contract and its negative examples before execution. F4 is a nonblocking fence repair. F1-F3 are closed at plan level within the user's revised goal, with the stated sideload/proxy/dev-PyTorch limitations; they must not be silently rewritten into stronger claims.

### Follow-up Actions

1. Use `/plan-corrections` to separate multilingual conversion from English fallback and add source-distinguishing expected outputs. No product changes were made in this review.
2. Extend TA-2 through baseline line 691, preserving unrelated expectations and the new two-chunk behavior.
3. Preserve F1-F3's fixed contracts and explicitly stated limits. Correct failed census receipt claims when updating the correction log; no new blocking predicate mutations are requested.
4. Resubmit this rolling report's round 3 under the existing v2 loop; do not reset caps or author approval. Execution remains behind Mat's human gate.
5. Dispatcher copies this complete report verbatim to the canonical rolling review. Reviewer output is only `C:/Temp/av-kit/dispatch/s32-plan-review-report.md`.

### Structured Ledger Verdict (loop round 1; rolling report round 2)

```json
{
  "schema_version": "review-verdict.v2",
  "date": "2026-10-15",
  "review_mode": "plan",
  "loop_id": "s32-plan-2026-10-14-tts-engine-runtime-v2",
  "round": 1,
  "target_plan": "docs/execution/plans/2026-10-14-tts-engine-runtime/implementation-plan.md",
  "agent": "gpt-6.1-sol",
  "requested_verbosity": "standard",
  "verdict": "changes_required",
  "summary": "One blocking language-conversion defect remains; F1-F3 are fixed within the revised scope and F4 is partially fixed. Static and all 12 verifier selftests passed. Complete rolling report: C:/Temp/av-kit/dispatch/s32-plan-review-report.md.",
  "intent_anchor": "TTS generates offline in the installed app for every listed language it can honestly support, with no GPL code in the TTS runtime",
  "intent_achieved": "partial",
  "findings": [
    {
      "id": "F5",
      "severity": "High",
      "confidence": "High",
      "blocking": true,
      "subject": "deliverable",
      "finding_kind": "behavior",
      "finding": "ESPEAK_G2P applies English EspeakFallback.E2M to the supported non-English languages. That table changes e to A and removes nasalization, whereas upstream EspeakG2P uses a different multilingual mapping. AC-74.6 can validate the wrong table and the mandatory smoke generates only English, so incorrectly converted Spanish, French, Hindi, Italian or Portuguese can pass the gates.",
      "file_line": "docs/execution/plans/2026-10-14-tts-engine-runtime/implementation-plan.md:139; docs/execution/plans/2026-10-14-tts-engine-runtime/implementation-plan.md:305; P:/av-kit/.venv/Lib/site-packages/misaki/espeak.py:14-29,71-107",
      "recommendation": "Define separate source-backed multilingual and English-fallback conversion contracts. Preserve the multilingual EspeakG2P mapping and normalization, and require distinguishing fake-runner assertions such as non-English e remaining e and nasalization being preserved. Keep GPL imports excluded.",
      "status": "open",
      "violates": "AC-74"
    },
    {
      "id": "F4",
      "severity": "Low",
      "confidence": "High",
      "blocking": false,
      "subject": "committable-tooling",
      "finding_kind": "clerical",
      "finding": "The F4 amendment correction is partial: TA-2 still fences the 511-symbol case only through baseline line 690, but its generate call is line 691. Replacing the raises assertion with the prescribed two-chunk success case normally changes that line, and ta-check rejects the correct test edit.",
      "file_line": "docs/execution/plans/2026-10-14-tts-engine-runtime/implementation-plan.md:168; tests/integration/test_tts_models.py:687-691; docs/execution/plans/2026-10-14-tts-engine-runtime/gate_lib.py:353-380",
      "recommendation": "Extend only TA-2's final range through baseline line 691. Preserve the source-backed two-chunk assertions and all unrelated expectations.",
      "status": "open",
      "violates": "AC-72"
    }
  ],
  "checklist_results": [
    {
      "check": "Plan-local static verifier",
      "result": "pass",
      "command": "rtk proxy P:/av-kit/.venv/Scripts/python.exe docs/execution/plans/2026-10-14-tts-engine-runtime/plan_checks.py static",
      "exit_code": 0,
      "evidence": "PASS static: 23 task rows; scripts, plan cross-references and file targets agree"
    },
    {
      "check": "Plan-local verifier negative cases",
      "result": "pass",
      "command": "rtk proxy P:/av-kit/.venv/Scripts/python.exe docs/execution/plans/2026-10-14-tts-engine-runtime/plan_checks.py selftest",
      "exit_code": 0,
      "evidence": "All 12 injected defects reported; PASS selftest: every injected defect was reported"
    },
    {
      "check": "Language G2P contract against installed upstream",
      "result": "fail",
      "procedure": "Compare ESPEAK_G2P and AC-74.6 with EspeakFallback.E2M and EspeakG2P.e2m in installed misaki 0.9.4; manually trace e and nasalized vowels through each mapping.",
      "observer": "gpt-6.1-sol",
      "exit_code": null,
      "evidence": "The uniquely named E2M table is English-specific: e -> A and combining tilde -> empty; multilingual EspeakG2P preserves these. F5 blocks AC-74."
    },
    {
      "check": "Prior-round correction recheck",
      "result": "partial",
      "procedure": "Read F1-F4 and the correction census, then trace the revised plan contracts through validate-task.ps1, gate_lib.py, current model services, packaging and amended baseline tests.",
      "observer": "gpt-6.1-sol",
      "exit_code": null,
      "evidence": "F1 fixed under D-87; F2 fixed for the managed legacy upgrade paths; F3 fixed with D-88 residual disclosed; F4 partially fixed because TA-2 omits baseline line 691."
    }
  ]
}
```

## Corrections Applied (2026-10-15, after round 2)

Applied by Claude Code (`/plan-corrections`, inline). This section records changes; it is not a verdict.

### Ledger status

Loop `s32-plan-2026-10-14-tts-engine-runtime-v2` recorded round 1 (rolling round 2): `changes_required`, 1 blocking, `intent_achieved: partial`, about 8.54M tokens. The ledger then **refused the next round on its token budget**: 8.54M spent plus 8.54M reserved exceeds the 10.5M budget. Another round needs a named human `continue --tokens`. The rolling file's cap allows one more round (round 3).

### Changes by finding

| Finding | Change | Where |
|---|---|---|
| F5 (English `E2M` applied to non-English) | **New contract `ESPEAK_MAP`.** It holds two ported tables that are never mixed. Each keeps its upstream post-processing at misaki's `version=None`, which kokoro 0.9.4 passes (`kokoro/pipeline.py:108,134`).<br><br>**`MULTI_E2M`** is `EspeakG2P`'s default 11-rule `e2m` (`espeak.py:71-85`), followed by removing `^` and `-` (`:96-104`). Plain `e`, `r`, `x` and U+0303 stay unchanged. The v2.0 nasal table is not ported.<br><br>**`EN_E2M`** is `EspeakFallback.E2M` (`:14-29`), followed by the U+0329, US/British, `o→ɔ`, `ɾ→T` and `ʔ→t` steps (`:49-58`). It is used only by `ESPEAK_EN_FALLBACK(british)`, which returns `(ps, 2)` or `(None, None)`.<br><br>**`ESPEAK_G2P`** applies the language's map and re-joins `«` `»` as `“` `”` (`:89`).<br><br>**`ESPEAK_MAP_PARITY`** reads the installed `misaki/espeak.py` as text with `ast`, without importing it. It asserts that both ported tables equal the upstream dict literals. So a test can no longer pass just by copying a wrong table.<br><br>**AC-74.6** now has samples that tell the two tables apart:<br>• Spanish `ˈeste` stays `ˈeste`.<br>• `t^s`/`d^z` become `ʦ`/`ʣ`.<br>• French `bɔ̃` keeps U+0303.<br>• A multilingual call never applies an `EN_E2M`-only rule.<br>• The English fallback maps `e→A`, `ɚ→əɹ`, `ɾ→T`, US `o^ʊ→O` and British `ə^ʊ→Q`, and returns rating 2.<br><br>**Other updates:**<br>• AC-72.2 (1)/(2) name the map each route uses.<br>• The optional AC-74.11 LOCAL-ESPEAK check adds French `ff_siwis` and checks the real CLI keeps `e` and U+0303.<br>• D-71 and D-72 `chosen`, the D-71 research note, User Review item 1, NOTICES, MEU-74 Files Modified (`espeak.py`), task row 6, and `validate-task.ps1` `PY_SYMBOLS['74']` (`MULTI_E2M`, `EN_E2M`, `ESPEAK_EN_FALLBACK`) are updated to match.<br><br>No GPL import is added. | `implementation-plan.md:105, 139-140, 148, 306, 311, 331, 377, 512, 515, 522`; `task.md:42`; `validate-task.ps1:40` |
| F4 remainder (TA-2 fence one line short) | The TA-2 final range is now `670-691`. Baseline line 691 is the `adapter.generate` call inside the 511-symbol `pytest.raises` block. Line 692, the unaffected `catalog.py` scan, stays outside the fence. | `implementation-plan.md:169`; `tests/integration/test_tts_models.py:687-692` |
| Audit note (three stale-string receipts held a wildcard-path diagnostic) | Acknowledged. The reviewer repeated the sweep independently and found no live stale string. The new `E2M` census uses a plain path list. | `C:/Temp/av-kit/census-s32-e2m.txt` |

### Census

`census-s32-e2m.txt` lists every `E2M`/`e2m` reference in the plan folder. After the edit, the only `E2M` tokens left are the intended `EspeakFallback.E2M` source references in `ESPEAK_MAP` and D-71.

`s32-r2-parity-feasibility.txt` shows that `ast` finds `EspeakFallback`'s 20-key and `EspeakG2P`'s 11-key dict literals with neither `misaki.espeak` nor `phonemizer` imported. The 8-key v2.0 `update` dict is the one the contract excludes by naming the default `self.e2m` assignment.

### Verification

| Check | Result | Receipt |
|---|---|---|
| `plan_checks.py static` / `selftest` | PASS / PASS | `C:/Temp/av-kit/s32-plan-static.txt` |
| `lint_task_contract.py` | OK (23 rows) | `C:/Temp/av-kit/s32-plan-lint.txt` |
| `validate-task.ps1` parse; decision-log YAML `safe_load` | 0 errors; ok | — |

Line endings: an earlier `sed -i` had converted `implementation-plan.md` to LF, and it is CRLF again. `.gitattributes` (`* text=auto`) normalizes the file in the repository either way. Only plan artifacts changed.

🕐 Completed: 2026-10-15 00:14 (EDT)


---

## Recheck (2026-10-15)

**Round:** 3 of the rolling report (last permitted round); round 2 of ledger loop `s32-plan-2026-10-14-tts-engine-runtime-v2`.
**Workflow:** /plan-critical-review.
**Agent:** gpt-6.1-sol, independent OpenAI reviewer; plan author Claude Code / Anthropic. The worktree overlay binds avkit_independent_reviewer to this slug.

### Intent Anchor

> TTS generates offline in the installed app for every listed language it can honestly support, with no GPL code in the TTS runtime

**Intent achieved: yes, at plan-review level.** Executing the corrected plan would deliver the scoped objective, subject to its explicitly disclosed provisioning, optional live-espeak and proxy-denial limits. This is prospective plan approval, not evidence that implementation or a packaged build has passed.

### Findings

No new Critical, High, Medium or Low delivery findings. **Round-3 findings count: 0; blocking findings: 0.** F5 and F4 are closed below. F1-F3 remain fixed under the previously reviewed scope; no correction reopened them.

| ID | Severity | Blocking | Kind | Finding | File:Line | Recommendation | Status |
|---|---|---|---|---|---|---|---|
| — | — | no | — | No new round-3 findings | — | — | — |

### Scope and Review Boundaries

All repository reads and command working directories used `P:/av-kit-wt/tts-engine-runtime`, branch `claude/s32-tts-engine-runtime`, HEAD `78610200ea2e7efd52318ea95c3e48b6df4993ba`. The other checkout was used only for the expressly authorized interpreter and installed upstream sources.

The five targets were read completely: implementation-plan.md, task.md, validate-task.ps1, gate_lib.py and plan_checks.py in `docs/execution/plans/2026-10-14-tts-engine-runtime/`. Bare plan/script names below mean that folder. Canon sampled: service-layer residuals, distribution runtime residual, Session-32 grouping/decisions, the five named issues, current adapter/assets/voices, model and TTS services, model manager, packaging spec, electron-builder and FFmpeg fetcher, Session-30 gate/floors, P7 NSIS assertion, existing amended tests, and installed misaki/kokoro/num2words sources and metadata.

**Write scope:** only this dispatch report and command receipts under C:/Temp/av-kit. No repository file, plan, product source or test was edited. No project tests, builds, generators, package-manager commands or validate-task.ps1 checks ran. The only executed plan verifier commands were the two expressly permitted modes.

**Protocol precedence:** the workflow's PR-6 literal procedural exception would stop on the clipped census receipt. The user's direct scope says process paperwork matters only where it would let a broken result pass. I apply that higher-priority scope here: disclose the deficient receipts, inspect the complete current sources and reproduce the raw sweep independently, rather than refuse the last round solely on that paperwork. This is an explicit scoped override of PR-6's procedural stop, not a claim that the original receipt met its untruncated-output requirement. REVIEW-TEMPLATE 2.2 and the requested v2 verdict supersede the workflow's obsolete empty-findings/v1 wording; the final response is the requested JSON, with no timestamp-script execution.

### Prior-Round Recheck

| Finding | Result | Current file:line evidence |
|---|---|---|
| F5 — English table applied to non-English | **fixed** | Plan:139-140 defines MULTI_E2M from EspeakG2P's default 11-rule dictionary, sorted application, then tie/hyphen removal. EN_E2M is restricted to the English fallback with its own post-processing and tuple result. Installed `P:/av-kit/.venv/Lib/site-packages/misaki/espeak.py:14-60` defines the different English path; :71-107 defines the multilingual path. Installed `kokoro/pipeline.py:108,134` passes neither constructor a version, so excluding misaki's version-2.0 nasal rewrite matches upstream. AC-74.6 at plan:306 now checks Spanish plain e, multilingual r/x/nasalization preservation, affricates, every table rule, English-specific outputs and source-AST parity. These distinguish the former wrong oracle from the intended behavior. |
| F4 — TA-2 ends one line early | **fixed** | Plan:169 now fences 670-691. Current `tests/integration/test_tts_models.py:687-691` contains the 511-symbol setup, raises block and generate call; :692 begins the unrelated catalog-source scan. `gate_lib.py:353-380` checks removed/changed baseline lines, so the prescribed two-chunk replacement is now inside the fence without widening into the unrelated scan. |

The requested sibling check found no new material contradiction:

- AC-72.2 (plan:377) explicitly routes English through ESPEAK_EN_FALLBACK/EN_E2M and e/f/h/i/p through MULTI_E2M.
- AC-74.11 (:311) names Spanish and French live samples and preservation of e/U+0303. Task row 12's shorter Spanish description does not remove that canonical optional AC.
- D-71 chosen/research (:512,515), D-72 (:522), User Review item 1 (:105), NOTICES (:148), Files Modified (:331), task row 6 (:42), and PY_SYMBOLS in validate-task.ps1:40 name the separated mappings/wrapper. No GPL import was introduced.
- G2P_ROUTE (:141) retains shorthand for the English fallback; the explicit callable contract (:140), D-72 and AC-72.2 resolve it. At implementation the callable must accept misaki's MToken and return the pair: installed misaki/en.py:665,700 invokes it that way.
- F1-F3's disclosure, managed legacy guards and staged offline-smoke contracts were not materially changed by the mapping correction, so they are not reopened.

### Correction Census and Receipt Audit

The correction section identifies a census receipt and substantive changes to every original hit. I inspected its actual contents, rather than accepting the log's success claims. `C:/Temp/av-kit/census-s32-e2m.txt` inventories nine old hits, but several long source lines are clipped at roughly 220 characters. The separate parity feasibility receipt ends in `KeyError: 'e^ɪ'`; its preceding printed counts do not establish successful completion of the probe.

The independent unfiltered current-source sweep was:

`rtk proxy rg -n 'E2M|e2m|ESPEAK_EN_FALLBACK|670-691' docs/execution/plans/2026-10-14-tts-engine-runtime/implementation-plan.md docs/execution/plans/2026-10-14-tts-engine-runtime/task.md docs/execution/plans/2026-10-14-tts-engine-runtime/validate-task.ps1`

Exit 0; full raw output is in `C:/Temp/av-kit/s32-r3-e2m-full.txt`. Every hit was read without treating a terminal rendering limit as source truncation. The correction table's substantive dispositions resolve as follows:

| Original census hit | Disposition confirmed against current files |
|---|---|
| validate-task.ps1:40 | updated: separate MULTI_E2M, EN_E2M and ESPEAK_EN_FALLBACK are in the MEU-74 declared-symbol list |
| task.md:42 | updated: row 6 owns both mappings, wrapper, attribution and parity |
| implementation-plan.md:105 | updated: two tables and their different roles |
| implementation-plan.md:139 | updated: non-English/English routes separated |
| implementation-plan.md:147 → :148 | updated: NOTICES attributes both ported mappings |
| implementation-plan.md:305 → :306 | updated: distinguishing negative cases plus per-rule/source parity |
| implementation-plan.md:330 → :331 | updated: new espeak module owns both tables and wrapper |
| implementation-plan.md:511 → :512 | updated: D-71 chosen states each table's role and exclusions |
| implementation-plan.md:514 → :515 | updated: D-71 source note distinguishes the upstream classes |

New explicit definition :140, router AC :377 and D-72 :522 were also read and confirmed consistent. TA-2 :169 was compared with the actual baseline test, not inferred from the correction prose.

**Nonblocking audit note:** replace the clipped census with unfiltered output, and correct the claim that the parity feasibility receipt succeeded. I did not run that probe; direct source inspection establishes the dictionary/post-processing comparison, while the future AST-parity test remains an execution obligation. No materially missing deliverable is shown to pass by these receipt defects. No further review round is requested solely for them.

### Answers to Q1-Q8

**Q1 — licensing and FFmpeg disclosure.** Yes for the proposed frozen ONNX runtime. Installed misaki/en.py:1-11 imports num2words/spaCy/data/token, without the GPL bridge; misaki/espeak.py:1-8 is the bridge importing phonemizer and loading espeak-ng through espeakng_loader. Direct English G2P plus the user-installed CLI avoids that bridge. Plan:146-148 and AC-72.1/:376, AC-72.6/:381 connect blocked fresh-process imports, real misaki.en import, module inspection and spec exclusions to tests. num2words 0.5.14's COPYING:1-3 is LGPL 2.1; source collection and full text/replacement instructions implement the plan's explicit LGPL exception. This is a technical import/package assessment, not certification of an unbuilt distribution or all legal obligations.

There remains the already-disclosed **dev PyTorch** import trap: installed kokoro/__init__.py:22-23 imports pipeline, and pipeline.py:5 imports misaki.espeak. The fake KModel package in AC-72.5 does not catch this real parent-package side effect. The frozen spec excludes kokoro and torch, so it is outside the scoped installed-runtime path; do not claim every development runtime is GPL-free.

FFmpeg stays separately shipped GPL code by D-87. NOTICES (:148), AC-72.7/:382 and task row 10 require honest disclosure, source location, full LGPL text and FFmpeg's own LICENSE.txt. validate-task.ps1:470-491 fetches when any binary/licence is missing, builds the installer and asserts staged notice content plus a nonempty staged licence; gate_lib.py:514-517 requires both assertions true. AC-72.7 adds negative/positive archive licence tests. The actual current fetcher lacks that copy until execution, as expected for this unstarted plan. The FFmpeg build choice itself is not reopened.

**Q2 — ONNX v1.0 and legacy paths.** D-73 is supported by the cited local receipt: old vocab 177 symbols, new 115, hexgrad 114; all 114 hexgrad entries match the new tokenizer, with extra pad symbol $, while 83 old entries differ or are missing. The receipt records source SHA256s; the saved HF listing records the pinned revision and required model/voice filenames. No network comparison was rerun.

LEGACY_ONNX_PATH (:130), AC-73.15/:235 and AC-73.16/:236 cover the actual managed upgrade paths: scan, persisted-row listing, load before the TTS port, and download fast path. Current services/models.py:124-131 and manager.py:59-71 demonstrate why both persisted load and download need guards. The tests require a migrated real SQLite database, no load-port call, correct revision/destination, updated row and unchanged legacy-file SHA256. **It is not an absolute ban on every v0.19 file:** a user can relocate/sideload an arbitrary ONNX file outside the legacy directory, which the plan expressly permits. No content-authentication guarantee is claimed for those arbitrary files. The fixed managed-upgrade finding remains closed.

**Q3 — availability and refusal ordering.** Yes. VOICE_REASON (:137) and AC-74.1/:301 require all nine language codes in both espeak states, plus unknown-code rejection. j/z remain unavailable; e/f/h/i/p depend on a successful espeak detection; a/b do not. ASSET_409_ORDER (:135), AC-74.3/:303 and AC-74.4/:304 connect API flags to unavailable-generate 409, no asset-port call and no job row. The existing insertion is services/tts.py:163-165, after the named checks. Available describes G2P capability; model and managed assets are separate preconditions. The documented no-espeak English out-of-dictionary omission remains a quality trade-off, not an undisclosed fallback download.

**Q4 — chunking and feeds.** The 510-symbol ceiling is consistent with two pad tokens and upstream model.py:128-131's context guard; a 510-symbol bound also bounds mapped IDs after unknown symbols are dropped. For a 510×256 pack, mapped lengths 1 and 510 choose rows 0 and 509; empty IDs explicitly choose row 0. ONNX token-count indexing and PyTorch phoneme-string indexing are intentionally distinguished (:144-145; upstream pipeline.py:232 uses pack[len(ps)-1]). No off-by-one defect is introduced by the correction.

AC-72.3/:378 requires nonempty bounded chunks, concatenation/order preservation, boundary precedence, hard splitting and empty input. AC-72.4/:379 asserts recorded feed values, dtypes/shapes, unknown-symbol handling, meaningful IDs and one inference per chunk. These are property contracts rather than only one example; they do not prescribe a property-testing framework or prove those future tests already pass. The model graph and real audio remain PACKAGE_SMOKE's responsibility.

**Q5 — TEST_AMENDMENTS.** **This verdict approves the described TA-1 through TA-13, including TA-3a/TA-3b, as source-backed, bounded expectation amendments under AGENTS Testing & TDD.** It gives no blanket authorization for other changed expectations. Existing source ranges were read directly.

| Amendment | Source-backed correction and retained oracle |
|---|---|
| TA-1 | D-73 repository/revision/local-dir switch; PyTorch mapping and display-size assertions remain |
| TA-2 | Removed pipeline seam becomes G2P_SEAM; language choice, feed values and missing-file cause stay tested; the 511 case becomes the specified two chunks; final fence now includes :691 |
| TA-3a | Missing pack now refuses before a job; fake inference failure preserves the failed-job/console test, including its unchanged error assertions |
| TA-3b | Removed Result-unpacking subject may be deleted through baseline :839; AC-72.4 retains its real-phoneme-ID intent |
| TA-4 | Health fixtures gain new fields; auth/error and old health behavior stay |
| TA-5 | Settings fixtures gain rows and the absent-pack assertion; existing behavior stays |
| TA-6 | Adds only the third managed-asset wire to parity enumeration |
| TA-7 | Catalog fixture gains availability/reason defaults and preserves voice IDs/catalog parity |
| TA-8 | Keeps the existing sys.path count assertion and adds append-position/order coverage |
| TA-9 | Spanish with detected espeak replaces unavailable Japanese, retaining the original non-English/no-chunk/no-spaCy intent and 409/201 assertions |
| TA-10 | Moves the official offline cache fixture while retaining the no-download-call oracle |
| TA-11 | Adds VOICE_PACKS in declaration order; invalid-input expectations remain |
| TA-12 | Seeds the production destination through variant_local_path; downloaded-state setup remains |
| TA-13 | Moves official sideload fixtures outside the intentionally ignored legacy directory; metadata assertions remain |

ta-check (:362-389) enforces removed/changed baseline line ranges and append-only files. It permits additions and declared whole-file fixture allowances; it is a range fence, not semantic proof that every edit is minimal. The final execution diff still needs independent review.

**Q6 — packaged offline evidence and identity.** Yes to the specified producer chain: ONLINE_PROVISION → INSTALLER_STAGE → OFFLINE_SMOKE, with validate-task.ps1:495-500 copying the staged installer's backend outside the checkout. Plan:150-153 requires the fresh process, empty app-data/HF/XDG caches, managed provisioning, dead proxies, actual WAV >8000 samples and failed real download with an error. D-88 accurately discloses that a client ignoring proxies is outside this denial; the positive smoke uses English and does not independently prove all CLI languages.

**No, windows-gate-check does not reject absence of every descriptive offline field.** gate_lib.py:518-530 reads passed/samples, negative state/error, external backend directory and the three uppercase dead proxies; it does not require offline.cwd, lowercase proxy fields or NO_PROXY. Those remain explicit smoke-producer obligations. This was already recorded in round 2 and is not escalated into another variant of fixed F3. The checker does require both JSONs' start/end identity to equal the current identity (:479-510). HEAD, the gated diff and untracked gated file bytes are hashed (:105-113), so no commit is needed. The hash binds source, not arbitrary external cache bytes or every installed tool version. Do not infer stronger guarantees from it.

**Q7 — Red/Green parsers.** An unconditional “Red cannot false-pass” answer would be wrong; these unchanged limitations were already documented:

- pytest-red (:152-195) requires nonzero status, JUnit and failed coverage for run-set ACs. It rejects unrecognized errors, but declared-symbol ImportError/AttributeError is tolerated even for an XML error element; there is no separate collection-error ban. Untagged assertion failures in TA-listed modules are also tolerated. A missing AC in its invoked file set fails.
- vitest-red (:227-257) rejects suite-load messages and pending/todo tests, then requires failed tagged ACs; TA-file assertions may be untagged, and assertion-origin detection uses message heuristics.
- electron-red (:293-310) requires a tagged expect failure and rejects top-level errors, but does not reject every coexisting other result failure. The runner selects AC-74.9.
- Green parsers reject newly failing test identities and nonzero exits with no recognized failure, while tolerating captured baseline identities. A new cause inside an old failing identity can be hidden by that identity comparison.
- ta-check and api-scope (:362-402) enforce baseline removal ranges and exact changed-file inventory, including untracked files; neither proves assertion meaning.
- The final windows-gate separately requires every native stage to exit zero and zero failed counts. No new material way for the final full gate to certify a missing deliverable was demonstrated. No parser probes, product tests or synthetic parser runs were executed.

**Q8 — Session 32b.** No essential requirement is carried only in context. Plan:85-95/:617-626 and task row 8 require the same plan/task, both MEU-73/74 handoffs, split entry, baseline/census/receipts and stable seam contract before row 9. The split preserves the existing plan, gates and review history. Handoffs/walkthrough do not yet exist because execution is unstarted.

### Checklist Results

All manual observations below were performed by **gpt-6.1-sol** on the current worktree; manual exit_code is null. “Pass” describes plan adequacy within the explicit review scope, not future product execution.

| Check | Result | Observed procedure / evidence |
|---|---|---|
| PR-1 Plan/task alignment | pass | Read all 23 rows against the three MEU contracts and runner sets; order 73 → 74 → 72 and H1/H2 matches |
| PR-2 Not started | pass | git status shows only the untracked plan directory and rolling review; Test-Path finds no baseline.sha, walkthrough or three product handoffs |
| PR-3 Task contract | pass | Each task has owner, deliverable, exact validation, dependencies and status; all 23 task rows remain unchecked |
| PR-4 Validation realism | pass | Existing runner dependencies exist; smoke/new tests are inventoried deliverables; static verifier succeeds |
| PR-5 Sources | pass | Read source columns and D-70–D-88; current mapping now agrees with installed source |
| PR-6 Correction readiness | partial | Named handoffs and substantive hit dispositions exist; original census is clipped and parity receipt errored. Explicit scope override and independent raw/source recheck documented above |
| PR-7 Scope discipline | pass | Deferred MEUs exist; ja/zh and FFmpeg decisions are human-approved; remaining exclusions match cited residual specs |
| PR-8 Reachability/negative oracle | pass | Current entrypoints, pre-job ordering, managed legacy guard, mapping negatives and staged offline producer/checker traced; no new material false-pass |
| PR-9 Single statements | pass | Named canonical contracts govern siblings; explicit repeated-literal sweep found no materially different live mapping/fence contract |
| DR-1 Claim/state | pass | Both claimed corrections are visible in current plan/runner and baseline source |
| DR-2 Old terms | pass | Broad no-GPL-shipped anchor remains only historical; old standalone mapping replaced; TA-2 now 670-691 |
| DR-3 Downstream references | pass | Requested AC/decision/NOTICES/task/PY_SYMBOLS siblings agree |
| DR-4 Robustness | pass | Distinguishing multilingual negative cases and source parity cure F5's wrong oracle; unchanged parser limits disclosed |
| DR-5 Auditability | partial | Current commands/outputs and file hashes preserved; original census/parity receipt claims need correction |
| DR-6 Canon consistency | pass | Managed assets, unavailable voices, no-torch bundle and honest FFmpeg scope align with canon/human decisions |
| DR-7 Fresh evidence | pass | Re-executed both allowed verifier modes; inspected actual receipts instead of relying on the claimed parity success |
| DR-8 Completion/risk | pass | Prospective approval only; optional real CLI, dev import and proxy/checker limits remain explicit |
| AV-1 / AV-3 | pass | Required future Red/Green and observable assertions are specified; no product execution claim made |
| AV-2 / AV-4 / AV-5 | pass | Plan does not authorize skip/only/todo or silent early success; fake collaborators have defined contract assertions |
| AV-6 | pass | Corrected source-backed FIC, negative cases and amendment basis inspected |

### Commands Executed and Durable Evidence

Every shell call used the worktree cwd, rtk proxy, all-stream scratch receipts, immediate child status capture, completed-receipt read and exit propagation. Shell read batches use Get-Content with numbered ranges; their outer status is not proof that every embedded search succeeded. Git emitted a warning that the user-level ignore file was inaccessible; repository status/HEAD/branch were still returned. No such warning was treated as a clean product gate.

| Command / manual procedure | Result |
|---|---|
| `rtk proxy P:/av-kit/.venv/Scripts/python.exe docs/execution/plans/2026-10-14-tts-engine-runtime/plan_checks.py static` | exit 0; PASS static: 23 task rows; scripts, plan cross-references and file targets agree |
| `rtk proxy P:/av-kit/.venv/Scripts/python.exe docs/execution/plans/2026-10-14-tts-engine-runtime/plan_checks.py selftest` | exit 0; all 12 injected defects reported; PASS selftest: every injected defect was reported |
| `git status --short`, `git log -3 --oneline`, `git rev-parse HEAD`, `git branch --show-current`, through receipt-wrapped rtk proxy pwsh read batches | HEAD/branch above; only existing untracked review/plan artifacts |
| `rtk proxy rg -n 'E2M|e2m|ESPEAK_EN_FALLBACK|670-691'` with the three full target paths listed in the census section | exit 0; complete sibling census, rechecked against source |
| `rg -n -F -e '510' -e '670-690' -e 'E2M' -e 'no GPL code shipped' -e 's32-package-smoke.v1'` with the plan/task/runner/parser paths, through rtk proxy pwsh | repeated-literal/source-shorthand sweep; decisive current outputs described above |
| Get-Content of all five targets, protocol/AGENTS/GUARDRAILS/PROFILE/template, canon, current production entrypoints, amended test ranges and installed sources; Test-Path of named dependencies and planned artifacts; Get-FileHash of targets | manual source traces recorded above; 12 existing gate dependencies found; future smoke/test files are scheduled in Files Modified; no execution artifacts yet |

Verifier negative cases observed: duplicate row ID, unknown check, swapped stage, changed floor, dropped gated path, undefined AC, undefined decision, missing modify target, existing new target, glob row, AC test outside every set, missing goal anchor.

```json
{"schema_version":"evidence.v1","check_id":"s32-r3-plan-static","command":"rtk proxy P:/av-kit/.venv/Scripts/python.exe docs/execution/plans/2026-10-14-tts-engine-runtime/plan_checks.py static","cwd":"P:/av-kit-wt/tts-engine-runtime","scope":"plan-local read-only static verification","phase":"planning","exit_code":0,"result":"pass","tested_state":"HEAD 78610200ea2e7efd52318ea95c3e48b6df4993ba plus target hashes below","output":"PASS static: 23 task rows; scripts, plan cross-references and file targets agree","fresh":true}
```

```json
{"schema_version":"evidence.v1","check_id":"s32-r3-plan-selftest","command":"rtk proxy P:/av-kit/.venv/Scripts/python.exe docs/execution/plans/2026-10-14-tts-engine-runtime/plan_checks.py selftest","cwd":"P:/av-kit-wt/tts-engine-runtime","scope":"12 in-memory negative cases of the plan verifier","phase":"planning","exit_code":0,"result":"pass","tested_state":"HEAD 78610200ea2e7efd52318ea95c3e48b6df4993ba plus target hashes below","output":"All 12 named injected defects reported; PASS selftest: every injected defect was reported","fresh":true}
```

```json
{"schema_version":"evidence.v1","check_id":"s32-r3-upstream-recheck","procedure":"Compare both mappings, ordering and post-processing with installed misaki/espeak.py, version defaults with kokoro/pipeline.py, and TA-2 with baseline test_tts_models.py:687-692; trace named siblings and gate callers by source read.","observer":"gpt-6.1-sol","cwd":"P:/av-kit-wt/tts-engine-runtime","scope":"F5/F4 and goal-scoped behavior/gates","phase":"planning","exit_code":null,"result":"pass","tested_state":"Target hashes below; installed misaki/kokoro 0.9.4 sources read only","output":"F5 fixed; F4 fixed; separate multilingual/English maps, distinguishing negative samples and AST parity specified; TA-2 ends at 691; no new material sibling contradiction.","fresh":true}
```

Reviewed SHA256s (exact bytes, before report write):

| File | SHA256 |
|---|---|
| implementation-plan.md | DBBFC63AC2C48FBD335EC6FA23819CBAF511248677FC18AAADCF04AEAF58AC8F |
| task.md | 88AC083BB316553650A56305E9F0D7ED1D50445B993B830550F3D3A1F6F0026C |
| validate-task.ps1 | BB05843E2EB4A5D67B4AFD48F7B87CD5B490ACA6CA8DC4B9395359ACC5176D9A |
| gate_lib.py | 703EADA8676773D90D45376C809BC4CFBDE1857FF9735F8A1DD2B5BB3CD5A604 |
| plan_checks.py | F8559E416ED4F9E678361DE5FC076ED6686CB2AC1493544BB1F4EDA5C309848D |

### Verdict and Follow-up Actions

**approved — intent achieved: yes at plan level.** F5 and F4 are fixed. No new evidence-backed delivery blocker remains within the registered goal. Previously documented parser, dev-PyTorch, arbitrary-sideload and proxy-denial limits are retained without reopening fixed surfaces. The receipt audit defects are nonblocking under the explicit user scope.

1. Dispatcher copies this complete rolling report verbatim to the canonical review file and validates/records the separate v2 verdict as **ledger round 2**, preserving the earlier history and continuation authorization.
2. Correct the clipped-census/parity-success claims as an audit note; no fourth rolling review is requested.
3. The plan's Claude Code execution gate still requires Mat's explicit execution authorization. This review neither starts execution nor authorizes a commit/push.
4. During execution, implement the approved amendments and mapping parity tests, run the full gate and actual packaged smoke, and carry disclosed live-espeak/proxy/dev-runtime limits into the handoffs. Preserve the same plan/task/baseline/loop across a 32b split.

Completion-preflight was applied to the authorized review scope: the 23 implementation rows are intentionally unstarted, not silently omitted; the only review deliverable is this receipt report plus the final verdict. Product closeout validators and timestamp script were not run under the user's static-only command restriction.

### Structured Ledger Verdict (loop round 2; rolling report round 3)

```json
{
  "schema_version": "review-verdict.v2",
  "date": "2026-10-15",
  "review_mode": "plan",
  "loop_id": "s32-plan-2026-10-14-tts-engine-runtime-v2",
  "round": 2,
  "target_plan": "docs/execution/plans/2026-10-14-tts-engine-runtime/implementation-plan.md",
  "agent": "gpt-6.1-sol",
  "requested_verbosity": "standard",
  "verdict": "approved",
  "summary": "F5 and F4 are fixed; no blocking delivery findings remain. Static verification and all 12 verifier negative cases passed. Census/parity receipt defects and previously disclosed runtime/gate limitations remain nonblocking under the user's goal-scoped materiality instruction. Complete rolling round-3 report: C:/Temp/av-kit/dispatch/s32-plan-review-report.md.",
  "intent_anchor": "TTS generates offline in the installed app for every listed language it can honestly support, with no GPL code in the TTS runtime",
  "intent_achieved": "yes",
  "findings": [],
  "checklist_results": [
    {
      "check": "Plan-local static verifier",
      "result": "pass",
      "command": "rtk proxy P:/av-kit/.venv/Scripts/python.exe docs/execution/plans/2026-10-14-tts-engine-runtime/plan_checks.py static",
      "exit_code": 0,
      "evidence": "PASS static: 23 task rows; scripts, plan cross-references and file targets agree"
    },
    {
      "check": "Plan-local verifier negative cases",
      "result": "pass",
      "command": "rtk proxy P:/av-kit/.venv/Scripts/python.exe docs/execution/plans/2026-10-14-tts-engine-runtime/plan_checks.py selftest",
      "exit_code": 0,
      "evidence": "All 12 injected defects were reported; PASS selftest: every injected defect was reported"
    },
    {
      "check": "F5 and F4 correction recheck",
      "result": "pass",
      "procedure": "Compare the current mapping and sibling contracts against installed misaki/espeak.py and kokoro/pipeline.py; compare TA-2's range with baseline test_tts_models.py:687-692 and gate_lib.py's removed-line fence.",
      "observer": "gpt-6.1-sol",
      "exit_code": null,
      "evidence": "F5 fixed: separate source-backed MULTI_E2M and EN_E2M routes, distinguishing negative samples and AST parity contract. F4 fixed: TA-2 ends at baseline line 691. No new material contradiction in the named siblings."
    },
    {
      "check": "Goal-scoped delivery and gate reachability",
      "result": "pass",
      "procedure": "Read the five target files and trace managed asset/model/voice refusal, frozen-runtime exclusions, installer disclosure, offline smoke phases and source identity through the current production entrypoints and cited canon.",
      "observer": "gpt-6.1-sol",
      "exit_code": null,
      "evidence": "No new material false-pass or delivery omission found. F1-F3 remain closed within D-87/D-88's explicit limits. Approval evaluates the unstarted plan; no product test, build or validate-task check was executed."
    }
  ]
}
```

## Audit Note Response (2026-10-15, after round 3)

Claude Code (author). This section answers follow-up 2 of the round-3 verdict. It does not change the verdict, and the approved plan was not edited.

- **Clipped census.** `census-s32-e2m.txt` was cut at 220 characters per line. It is replaced by `C:/Temp/av-kit/census-s32-e2m-full.txt`: an unfiltered `rg -n 'E2M|e2m'` over the plan folder, 13 lines, rg exit 0.
- **Parity probe claim.** The round-2 Corrections Applied section said the feasibility probe showed both tables. That claim was wrong: `s32-r2-parity-feasibility.txt` ended in `KeyError: 'e^ɪ'`, because the probe also read the v2.0 `update` dict. A corrected probe now selects the class-level `E2M` assignment and the default `self.e2m` assignment by name. It passes with exit 0 (`C:/Temp/av-kit/s32-r3-parity-feasibility.txt`):
  - neither `misaki.espeak` nor `phonemizer` is imported;
  - `EN_E2M` has 20 rules and maps `e` → `A`;
  - `MULTI_E2M` has 11 rules, has no plain `e` rule, and its keys equal the 11 rules in the plan's `ESPEAK_MAP`.

  The real `ESPEAK_MAP_PARITY` test is still an execution obligation (MEU-74).

🕐 Completed: 2026-10-15 00:26 (EDT)
