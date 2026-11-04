---
date: "2026-10-15"
review_mode: implementation
target_plan: docs/execution/plans/2026-10-14-tts-engine-runtime/implementation-plan.md
verdict: approved
findings_count: 1
round: 1
template_version: "2.2"
requested_verbosity: standard
agent: gpt-6.1-sol
---

# Critical Review: 2026-10-14-tts-engine-runtime

## Intent Anchor

> TTS generates offline in the installed app for every listed language it can honestly support, with no GPL code in the TTS runtime

**Intent achieved: yes**, within the approved D-70/D-71/D-87/D-88 boundary: managed assets provisioned beforehand, frozen ONNX backend, conditional eSpeak CLI availability, Japanese/Mandarin unavailable, separately shipped GPL FFmpeg, and proxy-based network denial. This does not claim a live eSpeak run or a functioning packaged MCP server.

## Findings

No Critical, High or blocking findings.

| ID | Severity | Blocking | Kind | Finding | File:Line | Recommendation | Status |
|---|---|---|---|---|---|---|---|
| F1 | Low | no | clerical | The plan verifiers have stale decision references: static rejects task.md's D-90/D-94, and selftest still injects D-99 although D-99 is now defined. Both permitted verifier commands exit 1; no material product false-pass was demonstrated. | docs/execution/plans/2026-10-14-tts-engine-runtime/task.md:71; docs/execution/plans/2026-10-14-tts-engine-runtime/plan_checks.py:236 | Reconcile the Row 4 decision references and use a genuinely undefined decision in selftest before H2-3; rerun static and selftest. | open |

F1 confidence: High. Subject: review-scaffolding. No control-defeat mechanism or violated product AC is asserted. Materiality Gate 1/5 applies: these are closeout-reference/fixture maintenance defects, not grounds to refuse a working TTS implementation. H2-3 still needs the corrected verifier runs.

## Scope

Independent OpenAI/Codex review of Anthropic/Claude Code's uncommitted implementation. The project overlay names gpt-6.1-sol for avkit_independent_reviewer (.agent/model-registry.local.yaml:33,43).

All repository commands used **P:/av-kit-wt/tts-engine-runtime** as cwd. HEAD and baseline.sha are c72fc4436da8534ef613264620b83c3e84e97631; branch claude/s32-tts-engine-runtime. P:/av-kit was used only for the expressly permitted interpreter and installed upstream package sources. No implementation was read from the dispatcher checkout.

Reviewed:

- Execution-critical-review protocol; AGENTS, GUARDRAILS, PROFILE; REVIEW-TEMPLATE 2.2; reviewer/tester roles and applicable terminal/evidence/completion procedures.
- Approved implementation-plan.md and round-3 plan-review contract; task.md, walkthrough.md, validate-task.ps1, gate_lib.py, plan_checks.py, baseline.sha and both final result JSONs.
- The complete correlated handoff set, in order: MEU-73, MEU-74, MEU-72.
- Tracked diff against the specified HEAD and directly read new product, packaging, tool and test files. Independent PRODUCT_SCOPE observation found **57 changed/new product files, zero unlisted**.
- Named service/distribution canon, changed hub documents, SSOT review state and named known issues; installed misaki/kokoro sources; existing PyInstaller analysis/archive manifests and staged installer support files.

No repository file was written. No project test, build, npm, uv, Playwright, generator, stamp script or validate-task.ps1 check was run. Only the two explicitly permitted Python verifier modes executed. Final report destination is C:/Temp/av-kit/dispatch/s32-exec-review-report.md; dispatcher owns verbatim copying to .agent/context/handoffs/2026-10-14-tts-engine-runtime-implementation-critical-review.md.

## Commands Executed and Decisive Evidence

Commands below ran through rtk proxy, with completed all-stream receipts under C:/Temp/av-kit and preserved native exits. File reads used Get-Content -Encoding UTF8; numbered reads used a line counter. Searches used rg -n; observed file presence used Test-Path/Get-ChildItem. The commands were read-only except receipt/report output.

| Observation | Executed command/procedure | Exit | Decisive output |
|---|---|---|---|
| Baseline and changes | git status --short; git diff --stat c72fc4436da8534ef613264620b83c3e84e97631; git rev-parse HEAD | 0 | HEAD c72fc4436da8534ef613264620b83c3e84e97631; 54 tracked changed files plus listed untracked files |
| Implementation/test comparison | git diff c72fc4436da8534ef613264620b83c3e84e97631 -- packages/core packages/api mcp-server/src; separate diffs for infrastructure, packaging, renderer and each affected existing test group | 0 | Actual production changes and TA edits inspected; new files read directly |
| Plan verifier | rtk proxy P:/av-kit/.venv/Scripts/python.exe docs/execution/plans/2026-10-14-tts-engine-runtime/plan_checks.py static | 1 | FAIL: task.md references D-90 ... no definition site; FAIL: task.md references D-94 ... no definition site |
| Negative verifier fixtures | rtk proxy P:/av-kit/.venv/Scripts/python.exe docs/execution/plans/2026-10-14-tts-engine-runtime/plan_checks.py selftest | 1 | 11 fixtures reported; FAIL selftest undefined decision: not reported; FAIL: selftest cases not reported: ['undefined decision'] |
| Frozen forbidden-module entries | rtk proxy rg -n, with the exact collected-tuple pattern below, over Analysis-00.toc and PYZ-00.toc | 1 | Empty: no collected module tuples or named eSpeak DLL entries. A separate broad search found the four names only in Analysis' excludes list, not collected-module entries. |
| Identity/scope | Independent inline PowerShell/.NET byte hashing of git outputs and file reads, described below; Get-FileHash on three lockfiles | 0 | Both receipts' start/end identities match; all three lock hashes match; PRODUCT_SCOPE changed=57 unlisted=0 |
| Staged contents | Test-Path and Get-ChildItem on packaging/dist and ui/dist/win-unpacked/resources | 0 | num2words/__init__.py exists as source; THIRD_PARTY_NOTICES.md and ffmpeg/LICENSE.txt staged; G2P support directories present |

Exact forbidden-module search (exit 1, empty stdout):

~~~powershell
rtk proxy rg -n "^\s*\('(kokoro|phonemizer|espeakng_loader|misaki\.espeak)(\.|')|libespeak|espeak-ng\.dll" packaging/build/avkit-backend/Analysis-00.toc packaging/build/avkit-backend/PYZ-00.toc
~~~

Absence evidence concerns collected tuples; it deliberately does not mistake the spec's exclusion names for bundled modules.

Independent identity procedure (observer gpt-6.1-sol): read the 21 GATED_PATHS from the plan, compare their executable copy, obtain raw stdout bytes of git rev-parse HEAD, git diff HEAD --binary -- those paths, and git ls-files --others --exclude-standard -z -- those paths. Use redirected process streams, not PowerShell's line serialization. Hash stripped HEAD plus LF, diff bytes, then ordinal-sorted untracked path + NUL + lowercase SHA256(file bytes) + LF. No gate_lib subcommand was executed or imported. Separately compare changed tracked/untracked product paths against exact Files Modified rows.

~~~json
{"schema_version":"evidence.v1","check_id":"s32-review-current-binding","procedure":"Independent PowerShell/.NET SHA256 reconstruction of WORKTREE_IDENTITY from raw git stdout, plus lockfile hashes and exact Files Modified set comparison","observer":"gpt-6.1-sol","cwd":"P:/av-kit-wt/tts-engine-runtime","scope":"21 gated paths; 16 untracked gated files; 57 changed/new product files","phase":"review","exit_code":null,"result":"pass","tested_state":"HEAD c72fc4436da8534ef613264620b83c3e84e97631 plus reviewed working tree","output":"WORKTREE_IDENTITY cd879e6ef3f5f16a7266c0a66afbf19f284baa6863bc2fa17c1bc599f2611e18; windows-gate and package-smoke start_match=True end_match=True; PRODUCT_SCOPE changed=57 unlisted=0","fresh":true}
~~~

~~~text
ui/package-lock.json:
A86D9A42C6CBD98705E1720EDBD7666FED573581C07E21EA0F56379DC7332980
mcp-server/package-lock.json:
D9570466713091B2F67B0BCEFC5FE12050BC8761CCC9532500714898516189A6
uv.lock:
5285FAC845036947C7E7E8F18420B3278CAC7C04A7C10892655C3F992EC5FFF6
~~~

Saved full-gate evidence, **read rather than rerun**:

~~~json
{"schema_version":"evidence.v1","check_id":"s32-review-saved-gates","procedure":"Read both final result JSONs, trace their producer/check predicates, and compare their recorded input identity with the independently reconstructed current identity","observer":"gpt-6.1-sol","cwd":"P:/av-kit-wt/tts-engine-runtime","scope":"WINDOWS_GATE and PACKAGE_SMOKE","phase":"review","exit_code":null,"result":"pass","tested_state":"cd879e6ef3f5f16a7266c0a66afbf19f284baa6863bc2fa17c1bc599f2611e18","output":"WINDOWS_GATE 17 ordered stages, each exit 0; pytest 803 passed/0 failed; UI Vitest 816/816; Electron expected 138, unexpected 0, skipped 0, flaky 0. PACKAGE_SMOKE build/dist/NSIS exits 0, notices_staged=true, ffmpeg_license_staged=true; offline Done, 41400 WAV frames at 24000 Hz, negative_probe Failed with WinError 10061 proxy refusal; packaged MCP unreachable exit 1 ERR_MODULE_NOT_FOUND.","fresh":true}
~~~

The actual static/selftest failures are F1, not passing validation claims. No unchanged product suite was rerun to reproduce saved summaries.

## Checklist Results

Manual observations below were performed by gpt-6.1-sol against current files/diffs and the saved receipts; manual exit_code is null.

| Check | Result | Procedure and evidence |
|---|---|---|
| IR-1 live runtime evidence | pass | Actual frozen backend generates through production API; final smoke JSON and producer code tools/smoke_packaged_tts.py:301,351. The test harness is external; collaborators inside this backend are not dependency-overridden. |
| IR-2 stub compliance | pass | Recording session/voice-pack fakes preserve their contracts; real migrated SQLite cases verify legacy-row list/load/re-download. Fixed synthetic health/voice ports are confined to route tests. |
| IR-3 error mapping | pass | Availability/asset 409 envelopes and absence of job/UoW writes asserted; legacy load 409 asserted; unknown asset 422 retained; runtime subprocess errors are DomainError and become recorded failed jobs. |
| IR-4 generalization | pass | All nine language codes covered; legacy path excluded at scan, list, load and download fast path; common pack/G2P paths serve both model formats. |
| IR-5 rigor | pass | Grades below; no mandatory AC has only a vacuous oracle. |
| IR-6 boundaries | pass | Extra-forbid ApiModel, exactly-one download target, closed asset/reason enums, strict MCP schemas; existing malformed/both/neither/unknown-field cases retained. |
| IR-7 AC/deferral integrity | pass | All 36 detailed ACs accounted for below; optional AC-74.11 explicitly unverified. H2 review/reflection/issue/metrics rows remain pending in the proper sequence. No product work silently deferred. |
| DR-1/2/3 claim/state/references | pass | Actual diffs implement the delivered residual sections; per-MEU intermediate evidence is distinguished from the final H1-2 gate. |
| DR-4/5 verification/auditability | pass | Specific negative oracles, real packaged WAV, proxy-denial diagnostic and independent byte identity; static checker maintenance separately disclosed as F1. |
| DR-6 architecture | pass | Availability stays domain/application-owned via a port; HF fetching stays model_manager-owned; frozen G2P avoids kokoro/phonemizer. |
| DR-7 freshness | pass | Both start/end identities and three lock hashes match the current tree. Saved stage totals meet floors 800/137/655. |
| DR-8 residual disclosure | pass | Optional live eSpeak, packaged MCP, dev PyTorch imports and pre-existing load/path limits remain explicit; approval is not complete H2 closeout. |
| AV-1 to AV-6 | pass | Saved Red-to-Green records plus diff show intended failures, source-backed criteria, no assertion bypass/skip masking, and production assertions. This reviewer did not reproduce Red/Green runs. |

### IR-5 test grading

All new/changed test cases were assessed against their assertions; setup-only files are identified separately. Strong means concrete values/side effects or negative outcomes; Adequate means supplementary structure/presence checks. No Weak case is the sole evidence for a mandatory AC.

| Files/cases | Grade | Basis |
|---|---|---|
| test_tts_voice_packs_service.py, test_tts_voice_packs.py | Strong | Exact order/count/size, wrong-size removal, unchanged legacy hashes, no pre-job writes, runtime state and retained downloaded variant |
| test_api_tts_runtime.py | Strong | Exact wire bodies/reasons/statuses; availability matrix representatives; zero asset calls and zero opened UoWs on unavailable generates |
| test_espeak_adapter.py | Strong for behavior/parity; Adequate for sample-count supplements | Exact argv/stdin, timeout/nonzero failures, mapping-sensitive independent samples, default-table AST parity and detection refresh |
| test_tts_voice_availability.py | Strong; table-inventory supplement Adequate | All 18 language/state combinations, unknown codes, frozen value and closed enum |
| test_tts_g2p.py | Strong | Factory/cache/fallback routing, spaCy guard before construction/download, exact cut preference and 2000-symbol lengths, empty audio and zero session calls |
| test_tts_no_torch.py | Strong for stated import seam | Fresh interpreter blocks forbidden imports and asserts module inventory and finite/clipped audio; real model/G2P execution is supplied by PACKAGE_SMOKE |
| test_tts_models.py / test_tts_assets.py | Strong for amended/new behavior; existing source/layout checks Adequate | Exact token/style/speed feeds, 510+1 split, stub-KModel arguments, failed-job logs, unchanged negative validation and local-path assertions |
| test_packaging_backend.py | Adequate structural AST tests | Required excludes/hiddenimports/data/mode; actual build/import behavior corroborates the structural checks |
| test_packaging_installer.py | Strong archive/error cases; Adequate notice structure | Exact exit 6 without license, exit 0 with staged license; LGPL text equality and six notice sections |
| test_api_auth.py, test_api_health_settings.py, test_api_tts_models.py, test_tts_voice_fixture.py | Strong contract/parity cases; older key-presence probes Adequate | Only approved fake/schema additions; existing auth/envelope/facade and exact fixture parity assertions preserved |
| settings-tts-runtime.test.ts, voice-combobox.test.tsx | Strong behavioral cases; hook source-presence supplement Adequate | Real components and query cache, exact single invalidation, actual Get payload, clipboard value, disabled click/Enter, available selection |
| settings-page.test.ts, tts-generate.test.ts | Strong affected behavior | Retained assertions; new unavailable option verified in real Electron with visible reason |
| models-assets.test.ts | Strong | Exact three-wire inventory, POST body, one fetch for valid and zero fetch for invalid input |
| api_fakes.py, tts_g2p_fakes.py, test-ids.ts, tts-voices.json | Setup/data, no standalone grade | Service pair shape, phoneme/session recording, pack bytes and catalog-layout fixture; not sole runtime availability evidence |

## E1 — AC Coverage

**Yes for every mandatory AC; AC-74.11 is the explicitly optional, unrun manual check.** All 36 ACs appear in their owning handoffs. No mandatory AC's complete test set was found incapable of failing for its stated behavior. Some supplementary inventory/source checks can pass without runtime correctness; they are corroborated by behavioral tests and the package smoke, not used alone.

Current production/test trace: core/ abbreviates packages/core/src/avkit_core/; infra/ abbreviates packages/infrastructure/src/avkit_infra/. Python test basenames are under tests/unit, tests/integration or tests/e2e as named in the plan; renderer tests are under ui/tests. Bare adapter.py/g2p.py references mean infra/tts/.

| AC | Production/evidence | Test/oracle |
|---|---|---|
| AC-73.1 | core/domain/tts.py:111,136 | test_tts_voice_packs_service.py:61,67; exact enum/required-asset order |
| AC-73.2 | infra/tts/assets.py:247 | test_tts_voice_packs.py:68; 53/54/malformed-size transitions |
| AC-73.3 | infra/tts/assets.py:298; model_manager/voice_packs.py:19 | test_tts_voice_packs.py:91,118,130; selective pinned fetch, monotonic progress, deletion/error, no HF import in tts |
| AC-73.4 | core/services/tts.py:155,241 | test_tts_voice_packs_service.py:77,91; exact 409 and zero jobs/generate calls |
| AC-73.5 | infra/tts/adapter.py:251,274 | test_tts_voice_packs.py:167; network trap and concrete style/token arrays |
| AC-73.6 | core/services/models.py:223 | test_tts_voice_packs_service.py:105,124,137; held download, skip and failure persistence |
| AC-73.7 | API models schema, health schema/routes | test_api_tts_runtime.py:44,55,67; 202/three states/422 |
| AC-73.8 | model_manager/manager.py:61 | test_tts_models.py:813; exact repo/revision/local_dir; unchanged PyTorch download |
| AC-73.9 | model_manager/manager.py:96 | test_tts_voice_packs.py:205; legacy skip/log and elsewhere sideload |
| AC-73.10 | useTtsJob.ts:123; SettingsPage.tsx:303 | settings-tts-runtime.test.ts:158,173,184; once on settle, never steady Idle |
| AC-73.11 | tts-assets.ts; SettingsPage Dependencies | settings-tts-runtime.test.ts:199,213; missing Get payload, no Get when ready |
| AC-73.12 | infra/tts/assets.py:120 | test_tts_assets.py:747; sys.path tail/order/idempotence |
| AC-73.13 | mcp-server/src/toolsets/models.ts:5 | models-assets.test.ts:59,64 plus TA-6; exact enum and invalid-wire zero fetch |
| AC-73.14 | openapi.committed.json | saved WINDOWS_GATE openapi stage exit 0 |
| AC-73.15 | core/domain/tts.py:102; services/models.py:105,130 | test_tts_voice_packs.py:274,293; migrated SQLite legacy row, exact 409/no load, unchanged bytes |
| AC-73.16 | services/models.py:253; manager.py:61 | test_tts_voice_packs.py:311; real row replaced with v1 path, fetch once, list/load succeeds, old bytes intact |
| AC-74.1 | core/domain/tts.py:182 | test_tts_voice_availability.py:32,40,49,59,70 |
| AC-74.2 | infra/tts/espeak.py:146,159 | test_espeak_adapter.py:94-185; PATH/ProgramFiles/x86/missing/fail/cache/fresh-install cases |
| AC-74.3 | services/tts.py:95; API routes/tts.py:87 | test_api_tts_runtime.py:221,237; English/Spanish/Japanese/Mandarin exact pairs |
| AC-74.4 | services/tts.py:150 | test_api_tts_runtime.py:256,267; exact 409, zero assets/UoWs, positive path reaches assets |
| AC-74.5 | services/health.py:182; API health mapping | test_api_tts_runtime.py:301,310; exact present/absent output |
| AC-74.6 | infra/tts/espeak.py:108,115,196,202,232 | test_espeak_adapter.py:198-480; CLI/mapping/parity/error oracles |
| AC-74.7 | SettingsPage.tsx:109 | settings-tts-runtime.test.ts:269,280,296; detected/missing/older-backend, copied exact URL, no Get |
| AC-74.8 | VoiceCombobox.tsx:127,147,275 | voice-combobox.test.tsx:216-270; disabled pointer/keyboard, reason/chip, available behavior |
| AC-74.9 | same renderer in built Electron | tts-generate.test.ts:667; aria-disabled and visible exact reason; saved real Electron gate/repeat evidence |
| AC-74.10 | openapi.committed.json | saved WINDOWS_GATE openapi exit 0 |
| AC-74.11 | optional installed eSpeak CLI | walkthrough.md:336; unverified, explicitly not a passed runtime test |
| AC-72.1 | adapter.py; g2p.py; spec exclusions | test_tts_no_torch.py:112; fresh blocked imports, real misaki.en import and fake engine seam; actual package smoke complements |
| AC-72.2 | g2p.py:60,75 | test_tts_g2p.py:84,111,131,145,165 |
| AC-72.3 | g2p.py:103; adapter.py:220,325 | test_tts_g2p.py:188,196,223,236; exact boundaries and empty behavior |
| AC-72.4 | adapter.py:274 | test_tts_models.py:698; independent exact ids/dtypes/style/speed, unknown/drop/empty/max/multi-chunk |
| AC-72.5 | adapter.py:169,226 | test_tts_models.py:758; stub KModel calls/style/chunks and no explicit pipeline import; dev-package caveat below |
| AC-72.6 | packaging/avkit-backend.spec | test_packaging_backend.py:263; AST contract plus saved build and collected-module manifest inspection |
| AC-72.7 | THIRD_PARTY_NOTICES.md; fetch_ffmpeg_windows.ps1; electron-builder.yml | test_packaging_installer.py:207,268,276; six sections/full LGPL text, staged notices and required archive license |
| AC-72.8 | tools/smoke_packaged_tts.py; validate-task.ps1:446 | final package-smoke-result.json; actual WAV, denied download, outside-checkout backend and matching identity |
| AC-72.9 | same installer producer, validate-task.ps1:471 | final installer fields all pass; MCP unreachable recorded without asserting success |

## E2 — TEST_AMENDMENTS and Execution Amendments

**TA-1 through TA-14 match their approved substance. No unapproved pre-existing assertion/expected-value replacement was found in the baseline diff.** The ta-check fence is a removal/range control, not proof by itself: gate_lib.py:362 allows whole-file TA entries and ignores addition-only hunks. The independent diff review is therefore necessary.

| TA | Observed disposition |
|---|---|
| TA-1 | Three ONNX expected repos changed; download assertions additionally pin revision/local_dir; display sizes and PyTorch map preserved. |
| TA-2 | KPipeline-specific fake/setup replaced by shared G2P observable, missing .bin cause and 511 -> [510,1] inference calls; language/feed/error assertions remain meaningful. |
| TA-3a | Inference RuntimeError replaces lazy missing-voice failure. The HTTP expectation changes 201 -> 500 and the expected console text changes to RuntimeError: session boom. These are **expectation changes**, authorized by the inference-failure amendment, not disguised setup repair; job/log/redaction assertions remain. |
| TA-3b | G2P call count replaces pipeline count; obsolete Result-like class/test deleted. AC-72.4 independently retains exact real-token ids, and AC-72.5 covers direct torch calls. |
| TA-4/5 | New health/asset fixtures and absent-row assertion; FakeTTS pair shape correctly follows D-89. |
| TA-6/7 | Three asset wires; 54 catalog-layout voice rows gain true/null; runtime availability is separately service-tested. |
| TA-8 | Existing count assertion retained; new append/order test added. |
| TA-9 | Japanese non-spaCy success example becomes Spanish with eSpeak detection faked present; 409/201 oracles retained. |
| TA-10/11/12/13 | Canonical v1 paths, added asset enum/tuple order, and weight setup changed as specified; no-network and sideload assertions retained. |
| TA-14 | Exact REST voice dict gains available true/reason null; facade count, lang_code ban and route-source controls unchanged. |

D-89 preserves VoiceConfig's five-field contract. D-95/96 are explicit human amendments; D-97 fits the existing DomainError job handling. D-98 is an **authorized assertion amendment**, replacing a contaminated process-wide inventory with an espeak.py import AST scan; fresh-process IMPORT_HYGIENE remains separately asserted. D-99 is a type-only correction. D-100 adds the button/test-id; omitted GUI action-index coverage is disclosed for follow-up rather than claimed complete.

The Row 3 setup wait and Row 8 background-download teardown repair do not weaken their final behavioral expectations. Row 2/9 fence extensions include the intended error assertion or blank separators respectively. The S1 baseline fast-forward is documented and current HEAD matches it. Row 9 provisioning uses an already cached, SHA-verified FFmpeg archive after the pinned URL 404; this changes environment setup, not the failing assertions. Row 12's three smoke changes are examined in E4. Row 13 and H1-1 reconciliation do not alter a product oracle. Static review cannot reconstruct every intermediate uncommitted Red-file revision; these temporal claims rely on the durable Red/amendment records, corroborated by the final diff.

## E3 — GPL Boundary and Notices

**No identified path loads the prohibited GPL G2P stack into the frozen TTS backend.** espeak.py imports standard library/domain code and executes the user-installed CLI. g2p.py imports misaki.en lazily, whose installed imports do not import misaki.espeak. Both mapping tables and post-processing agree with installed misaki 0.9.4's appropriate version=None branch.

The spec excludes kokoro, phonemizer, espeakng_loader and misaki.espeak. Actual collected-module tuples in Analysis/PYZ contain none of them, and no named eSpeak DLL entry was found. num2words is present as replaceable .py source in both backend and staged installer, consistent with D-76. IMPORT_HYGIENE and the saved frozen English generate support the import boundary.

**Dev PyTorch is different:** adapter.py:178 imports KModel from kokoro; installed kokoro/__init__.py:23 also imports its pipeline, which imports misaki.espeak and therefore GPL bindings. AC-72.5's stub-package test proves the direct call contract, not absence of this real upstream side effect. This was already disclosed in the approved plan review. In the frozen backend torch/kokoro are excluded and the torch-absent guard refuses this branch before that import, so it does not violate D-87's frozen-runtime goal.

NOTICES accurately gives the six required entries, LGPL text/replacement instructions and separately shipped GPL FFmpeg. Its spaCy transitive dependency omissions matter for a complete distribution notice inventory, but this is not an exhaustive inventory or license-compliance certification. They do not establish a GPL import or violate AC-72.7's explicit six-component contract; retain the handoff's notice-completeness follow-up.

## E4 — Offline Generation and Registration

**Yes, the final smoke proves the specified frozen-backend WAV generate under D-88's network-denial model.** validate-task.ps1:499 copies the installer stage's backend into C:/Temp/av-kit/s32-smoke-run/avkit-backend. The subprocess runs there, with fresh app-data/HOME/HF/XDG paths and dead upper/lowercase proxies. It loads int8, generates af_heart, and the actual WAV has 41,400 frames at 24 kHz, output inside the requested directory. A subsequent real HF request fails with connection refusal and a Failed download runtime.

The registration POST is legitimate: a new database has no stored weight path, although the provisioned file is discoverable. The production download fast path records that file offline; no fake collaborator or direct DB write is injected. Normal prior provisioning retains the DB path, whereas the smoke deliberately creates a fresh database. This step proves usable production API setup, while honestly exposing the pre-existing discrepancy between sideload listing and loading. It does not prove that selecting an arbitrary sideload in the GUI already works.

Fresh HOME removes a genuine host-profile asset leak and strengthens the proof. Recording one case of each proxy key repairs JSON serialization without changing the environment. Polling Done uses the real domain success wire. These changes do not waive the WAV/denial/identity oracles.

This is staged-installer backend evidence, not an interactive NSIS installation test or firewall/raw-socket denial. No such stronger claim is needed by the approved contract.

## E5 — Honest Availability and Pre-Job Refusals

**The implemented contract is consistent across the service, REST and GUI, with MCP forwarding the same REST result.** a/b are available; j/z always language_unsupported; e/f/h/i/p require current ESPEAK_DETECT and otherwise espeak_missing. The service checks inputs -> loaded model -> known voice -> availability -> assets -> job insertion. Unavailable-voice tests assert exact 409 messages, no asset calls and zero opened UoWs. MCP's existing strict tool schemas/transport do not introduce a generate bypass or strip availability fields.

The picker blocks disabled click/Enter selection, shows per-option and selected-chip reasons, and preserves available choices. The default true/null test catalog is a layout fixture, not the REST runtime availability inventory.

English caches its misaki instance/fallback per British flag, as planned: installing eSpeak after first English use does not enable the optional OOV fallback until restart. A previously captured fallback still probes the CLI when called and may fail after removal. These are disclosed cache/optional-fallback limits; they do not make missing-eSpeak multilingual voices or j/z falsely available. No stronger live English-fallback refresh guarantee was approved.

## E6 — CHUNK_RULE and ONNX_FEEDS

**Correct against the approved contract.** g2p.py:103 chooses sentence punctuation, then clause punctuation, then space, then hard 510; nonempty trimmed chunks preserve symbol order. The adapter phonemizes sentence/line segments before joining and splitting, then sends one inference per chunk.

ONNX drops unknown symbols before constructing int64 [[0,*ids,0]], uses float32 speed [speed], and style pack[max(min(len(ids),510)-1,0)] reshaped (1,256). Tests pin real token ids, unknown/all-unknown input, row 509 at 510, dtypes, shapes and multi-chunk calls. Torch deliberately indexes by phoneme-string length and calls KModel with (1,256) style. Its index can differ when unknown symbols drop; plan TORCH_PATH explicitly approves the differing upstream references. It is not a defect against this contract.

## E7 — Gate Binding

**Yes: both final receipts bind to the current reviewed tree.** Independent current identity:

cd879e6ef3f5f16a7266c0a66afbf19f284baa6863bc2fa17c1bc599f2611e18

Both start/end values match it. The gate's exact 17-stage order and every stage exit 0 are present; source-audit records rg's no-match exit 1 normalized as stage success. Floors 800/137/655 are exceeded by 816/138/803; Electron skipped/flaky/unexpected are all zero. Three lockfile hashes match independently. Recorded environment is Node v24.19.0/Electron 42.9.3; no runtime-version command was run during this static review.

No current GATED_PATHS content drift remains after the receipts. A content identity cannot prove that no transient edit was ever made and reverted, and this review does not claim such historical proof. The excluded H1 handoff/SSOT/Markdown edits do not invalidate the prescribed identity. Earlier row-12 identity 7925c50c is explicitly superseded by H1-2.

## E8 — Unverified LOCAL-ESPEAK

**Enough for approval under the approved conditional/fake-runner contract; not proof of live multilingual synthesis.** The CLI argv/stdin, punctuation, failure handling, both mapping tables, language-specific routing and detection refresh have substantive oracles. The exact live dependency check was explicitly optional and its missing-install disposition was approved before execution. There is no observed real-CLI mismatch to elevate into a blocker.

Keep AC-74.11 unverified and file the planned live-path follow-up at H2-2. When eSpeak NG 1.52 is available, execute the specified Spanish and French WAV checks, including Spanish e and French U+0303 preservation, and record version/detection. Do not describe this round as a live eSpeak validation.

## Out-of-Contract Observations and Residual Risks

- Preserve the already disclosed full notice-inventory work; the six-component TTS notice is not a complete dependency/license audit.
- Preserve separate follow-ups for sideload list/load mismatch and stale spaCy path/cache after models_directory changes.
- The cached FFmpeg archive permits this gate; the pinned download URL 404, extra shipped ZIP, and older fetcher exit-code issues remain distribution follow-ups.
- Packaged MCP remains unreachable (ERR_MODULE_NOT_FOUND); record its actual result as open at H2-2, not resolved. This session's AC requires recording, not repair.
- Live eSpeak and cached English fallback limits remain as described above; D-70's ja/zh follow-up remains required.

## Verdict

**approved — intent achieved: yes.** No evidence-backed High/Critical behavioral, contract, persistence or false-implementation-claim blocker remains within the approved scope. One Low non-blocking scaffolding finding is retained.

This approves the reviewed implementation at the identity above. It does not mark H2 complete, commit the code, resolve outstanding issues, or authorize this reviewer to fix implementation files.

## Follow-up Actions

1. Dispatcher: copy this report verbatim to the canonical implementation-critical-review.md and record the matching round-1 review-verdict.v2 JSON.
2. Author: handle F1 before H2-3 and run its two verifier checks; these task/plan-check edits alone are outside the declared GATED_PATHS. Any later product/gated-input correction requires affected verification and renewed full-gate/smoke binding.
3. Continue the authorized H2 reflection, metrics, SSOT/issue reconciliation and commit-message draft. Include D-89/D-95 to D-100 and all disclosed runtime/distribution follow-ups; do not claim the optional live test passed.
4. Mat retains commit control. No repository edits, corrections, commits or pushes were performed by this reviewer.

## Review Completion

Completion-preflight applied to the review-only deliverable: canonical task read; H1-6 and H2 rows correctly remain pending until dispatch/author closeout. Required report sections and explicit verdict are present. The user-assigned receipt destination takes precedence over direct canonical writes; the requested final JSON takes precedence over the workflow's prose/timestamp ending.
