---
date: "2026-11-04"
review_mode: "execution"
target_plan: "docs/execution/plans/2026-11-03-release-rc1/implementation-plan.md"
verdict: "approved"
findings_count: 0
template_version: "2.2"
requested_verbosity: "standard"
agent: "Codex (avkit_independent_reviewer, OpenAI)"
loop_id: "s44-execution-2026-11-03-release-rc1"
round: 4
intent_achieved: "yes"
---

# Critical Review: 2026-11-03-release-rc1

> **Review Mode**: execution, multi-MEU / multi-handoff
> **Verdict**: approved

## Intent Anchor

Session 44 prepares release candidate 1 of av-kit: MIT licence, the two first-run bug fixes (MEU-108, MEU-109), RC packaging and a real installer with packaged checks (MEU-110), release notes, a publish checklist and the D-101 brief, stopping before every outward step.

The reviewed scope also includes Mat's addition of MEU-111 (D-185) and the revised audit gate (D-186), as recorded in the plan's Differences from the registered goal. Intent achieved: **yes**, for preparation with the declared publication gates and verification limits.

## Scope

**Target**: the four Session 44 MEU-108/109/110/111 handoffs; implementation-plan.md and task.md; the three release artifacts; changed product, tests, packaging and plan-local tools against HEAD `24e27354e35eccc0cfa7d7e76357e673a6e38c23`; build, install, audit and gate receipts.

**Review Type**: independent multi-MEU execution review, ledger round 1 of 6. Claude Code / Anthropic authored the work; this reviewer is Codex / OpenAI and did not implement it.

**Checklist Applied**: IR, implementation/adversarial verification, and substantive public-claim review. No paperwork-format findings were sought. Earlier repository recreation, visibility changes, workflows and dependency batch are baseline context, not deliverables of this plan. Reflection, metrics and the remaining H1/H2 review/closeout rows follow this review and are not missing implementation.

Only scratch probes, test receipts and this report were written. No build, installer, live audit, YouTube operation, commit, push, tag, release or machine-settings change was performed. No prohibited secret file or real app-data content was opened.

## Findings

| # | Severity | Blocking | Kind | Finding | File:Line | Recommendation | Status |
|---|----------|----------|------|---------|-----------|----------------|--------|

No findings. No Critical or blocking defect was established. The limits below are retained explicitly rather than described as verified behavior.

## Checklist Results

### Information Retrieval (IR)

| Check | Result | Procedure / command | Exit | Evidence |
|---|---|---|---|---|
| Scope, intent and author independence | pass | Manual: Codex read the supplied request, plan, four handoffs, baseline diff and review contract | null | Correct four-MEU target; vendor-distinct review; no outward step authorized by this verdict |
| AC implementation and evidence coverage | pass | Reviewer AC-set comparison plus manual tracing of each AC to implementation, assertions or packaged procedures | 0 | 32 primary ACs: 4 + 5 + 19 + 4; none absent from its owning handoff; regression families AC-24/25/68/71/72/92 also traced |
| Current gate inputs | pass | Identity script; in-memory exclusion diagnostic; independent read-only build-input reconstruction | 0 | Exact historical state reproduced after accounting for one pre-existing local settings file newly visible to this sandbox; product identity and installer match independently |
| Deferrals and exclusions | pass | Manual: Codex compared plan Out of Scope, handoff Deferred Items, delivered residual specs and known-issues changes | null | Clean-machine/F2/model-first-download, D-101, signing, auto-update, other defects and other clients remain explicit; no required implementation was quietly dropped |
| Later closeout | n/a | H1-7 onward and H2 belong to the coordinator after review | null | No session-DONE or publication approval is implied |

### Design Review (DR)

| Check | Result | Procedure / command | Exit | Evidence |
|---|---|---|---|---|
| READY publication and conversion error behavior | pass | Baseline/current READY probe; Python and UI targeted tests; source tracing | 0 | Publication outcomes unchanged; process query removed from ordinary output; all three conversion paths create parents and blocked-path failure reaches the service |
| Image refusal and independent audit oracle | pass | Real SDK transport tests, actual audit-step/classifier tests and unchanged forbidden-import check | 0 | Exact cap succeeds; both oversize cases refuse without losing connection; smaller-image refusal and lost connection fail the audit |
| Build identity, shipped notices and actual install | pass | Read-only identity/installer/DLL hashes, in-memory licence regeneration; manual inspection of installed-root scripts and receipts | 0 | Installer hash and 1,102,016-byte licence list match; installed app, backend and uninstall were exercised |
| Public claims and D-101 brief | pass | Manual: Codex compared release text, checklist, implementation, receipts and primary upstream sources | null | Incomplete Transcript, unsigned build, clean-machine gap and source obligations remain explicit |

### Post-Implementation Review (PR)

| Check | Result | Procedure / command | Exit | Evidence |
|---|---|---|---|---|
| Independent targeted Python tests | pass | `.venv/Scripts/python.exe -B -m pytest -p no:cacheprovider --basetemp C:/Temp/av-kit/s44-review-py-tmp-1 tests/unit/test_ffmpeg_conversion.py tests/unit/test_conversion_service.py tests/unit/test_release_packaging.py tests/unit/test_generate_third_party_licenses.py -q` | 0 | 123 passed |
| Independent MCP tests | pass | `npx vitest run tests/image-over-stdio.test.ts tests/audit/capture-image-step.test.ts tests/audit/run-cli.test.ts tests/capture.test.ts` from mcp-server | 0 | Four files, 47 passed |
| Independent UI tests | pass | `npx vitest run tests/unit/ready-probe-guard.test.ts tests/unit/dev-spawn.test.ts` from ui | 0 | Two files, seven passed |
| Correction/rebuild/fresh gate evidence | pass | Manual: Codex compared attempt-1 receipts with current build, rows 11/12/13 and H1-2 receipts | null | Old installer superseded; corrected MCP suite has 466 passes; fresh gate matches rebuilt product inputs |
| Recorded full-audit evidence and verification limits | pass | Manual: Codex read the saved summary/report, gate and rule receipt; ran only offline structural checks | null | Evidence review completed; audit remains 98/99, exit 1, non-pass; only transcript.compile fails and Transcript verification remains incomplete; no fresh live audit run by reviewer |
| Required behavior/assertion integrity | pass | Manual: Codex inspected changed test files and probe assertions | null | No introduced skip/only/xfail masking or product placeholder; limitations distinguished from passes |

### Q1 — MEU-108: READY guard

Accepted. `python-manager.ts:90` defines the one non-global regex, and `usableReadyPort` is used by both `publishIfReady` (`:138`) and `confirmReadyAndPublish` (`:106`). There is no divergent guard predicate or regex state. `index.ts` passes both process-query and descriptor-read callbacks behind the guard. Non-READY and port-zero chunks return before either callback.

The independent probe compiled the current module and the actual HEAD module and compared their publication arrays. Ordinary output changed from two queries to zero; a log/READY/log sequence changed from three to one. Published address/token values remained identical.

The edge cases do **not** gain new semantics: a READY marker split between chunks, or split before `instance`, can still be missed; two complete READY chunks still publish twice; a failed live query still does not veto READY from the owned child's pipe. The probe reproduced all three on both versions. The existing publisher deliberately treats the child's pipe as ownership proof and does not use CIM identity as a veto. This MEU preserves that boundary; it does not implement stream buffering, deduplication or new liveness enforcement. I did not certify those stronger properties or treat unchanged behavior as a regression introduced here.

### Q2 — MEU-109: first conversion and errors

Accepted. `_ensure_output_parent` (`adapter.py:65`) calls recursive, idempotent mkdir. `encode:559`, `cut:586` and `extract_stream:624` invoke it before spawning FFmpeg. The tests record parent existence at spawn, preserve an existing sentinel file, and require a blocked parent to raise with its path and spawn nothing. The service-level test uses the real adapter path and checks `Failed`, path-bearing error and no spawn. `conversion.py:468` saves the exception text through `_finish`.

Skipping `FFmpegAdapter.convert` is sound for this contract. A product-wide call-site search found its one media caller at `services/tts.py:337`; `wav_path` and `mp3_path` share `root`, and `write_audio_wav` creates that parent first (`filesystem/writer.py:84`). This leaves no equivalent first-run hole in the other current media caller. Both saved packaged smokes also show an initially absent Convert directory, a Done job and a real duration-probed output.

### Q3 — MEU-111: stdio arithmetic and refusal

Accepted. `ceil(7,800,000 / 3) * 4 = 10,400,000` base64 bytes. Against 10,485,760 bytes, 85,760 remain; a measured 98-byte envelope leaves 85,662. The test additionally reserves 65,536 and compares against the SDK's actual exported limit. The saved 7,860,000/7,880,000-byte break is consistent with that arithmetic.

The independently rerun real-client/built-server tests prove intact bytes at the cap, a `payload_too_large` tool error mentioning both path fields at 7,800,001 and 8,059,548 bytes, and a later successful tools/list on the same connection. The refusal gives a usable next action: get the capture and open its original or annotated path. It does not claim to provide a downscaled image.

`plan.ts:178` recognizes an error with the server's exact refusal prefix, not any error. `:183` separately requires REST 200 and a body over the cap. Both image steps retain byte parity for normal images. The real step/classifier tests reject refusal at exactly the cap, missing REST image and a lost connection even with oversized REST bytes. Thus the new expected-error branch does not turn those failures into a pass.

D-189's independent literal is a fair correction to AC-68.2: the runner no longer imports server code, its ceiling cannot silently follow a raised server ceiling, and a separate test pins both to the agreed literal. The forbidden-import test remains unchanged and passes. The live audit's 335,031/335,073-byte images prove only the ordinary branch; refusal is established by AC-111.2's transport tests and AC-111.4's classifier tests, not attributed to that live run.

### Q4 — MEU-110: identity and installed app

Accepted. The independent read-only reconstruction produced `build_inputs 617f92d1bb0b9358a3cf6f95407cba86b5875e862acc0b424e57fe6ff73019e5`. The installer is **328,403,592 bytes**, SHA-256 **532663ea4c0040d81d2127193a19e156d1ff39dea932d1ec7ec797f0ec025df1**. Both packaged FFmpeg hashes and all 48 recorded Windows-runtime DLL hashes also match.

The build-input hash is not itself a hash of every resulting byte. It covers repository inputs by default, including specs, Vite/MCP build configuration, licence overrides, locks and the re-included build script; excluded root artwork is not the separate UI asset imported by Header. Docs/tests/agent material are excluded from this build identity. Machine/runtime/generated payloads are not all repository blobs. The separate installer size/hash binds the actual artifact and detects changed shipped bytes; this is not a claim of reproducible builds. Source inspection found no excluded source input used by this build that defeats that binding.

Row 11 exercises win-unpacked and a copied packaged backend for offline TTS. Row 12 reads the real install location from the Uninstall entry, tests that root with `smoke_packaged_rc.py`, and launches that root's `av-kit.exe` through Playwright. The app script checks isPackaged, execPath, userData and version, then requires Settings' own health request and rendered FFmpeg readiness, beyond its initial injected health probe (`packaged-app-smoke.mjs:91,103,123,126`). The saved installed-app result reports the real installed executable, HTTP 200, Settings, nine app responses and no API/page errors. It is not a dev-server substitution.

The uninstall claim is supported for the specified surfaces: saved snapshots show no new/lost uninstall names, Run/StartupApproved values, shortcuts, app-data top-level entries or matching local/roaming folders; the script also checks removal of the install directory and install key. It waits for the NSIS relaunched copy and detects installed-process survivors. This does not establish byte-for-byte preservation of real app data or absence of all Windows traces. The process wait is bounded and may finish before 30 seconds; the handoff already discloses that wording limit. No fresh installer or real app-data inspection was performed here.

### Q5 — MEU-110: licences and D-101

Accepted. Regenerating the complete list in memory against the real TOCs, exe archive, installed metadata, runtime versions and .NET packs succeeded and was byte-identical to both the generated and packaged list: **1,102,016 bytes**, SHA-256 **afb638f2750dcf5a7cb637cacf2abfc3c04cffffc2ac44fd40ca1ef747b83dfc**. The archive ban probe found no banned package; the retained negative control did expose espeakng_loader, kokoro, misaki.espeak and phonemizer.

Python ownership includes PYZ-only owners and every recognized RECORD notice, including dist-info/licenses contents irrespective of filename. Missing RECORD notices and unowned payloads refuse; TOC/disk and PYZ/exe name-set disagreement refuse. CPython terms, incorporated software, reviewed native-library texts and PyInstaller's exception are covered separately. npm's installed non-dev lock closure and the MCP bundle's own licence list cover their respective payloads. The two actual .NET 8.0.33 packs contain the three licence/notice files the generator requires; the Desktop pack does not contain an ignored additional notices file. The refusal fixtures exercise missing texts, unknown owners/packs, unexpected GPL, stale TOCs and stale output removal. No silently missing required notice was found in this build. This is coverage of the specified build and available provenance, not an automated legal opinion about all future payloads.

The MIT file and manifest metadata are consistent. The reviewed override texts use versioned upstream provenance. In particular HACL uses the vendored file's MIT header, libffi uses the cited CPython dependency source, type-fest elects its published CC0 alternative, and SQLite/xz describe the relevant library portions. Upstream attribution text remains intact; no personal address is reproduced in this report.

D-101 is a fair decision brief: it identifies current source-distribution inadequacy, gives GPL/minimal-build/LGPL/no-bundle alternatives, exposes the encoder changes required by LGPL, marks source-set estimates and assembly cost as uncertain, and holds distribution for Mat. The primary texts support the separate-aggregate distinction and the continuing corresponding-source requirement; this review does not rule on D-101. Sources checked: [GPLv3 text in GCC's upstream repository](https://raw.githubusercontent.com/gcc-mirror/gcc/master/COPYING3), [FFmpeg's own legal-page source](https://raw.githubusercontent.com/FFmpeg/web/master/src/legal), and [BtbN's retention and variant documentation](https://raw.githubusercontent.com/BtbN/FFmpeg-Builds/master/README.md). The tagged BtbN README was unavailable to this browser, so its exact historical counts/provenance remain supported by the supplied static-research receipt rather than independently re-enumerated upstream. The counts and unparsed conditions match that receipt.

### Q6 — MEU-110: public claims and outward steps

Accepted. Notes and checklist carry the independently checked installer size/hash. The testing section distinguishes installed-app checks from unpacked MCP and copied-backend TTS, explicitly excludes the clean-machine/real-F2/first-model-download checks, and retains a clean-machine result-or-waiver marker. Transcript's unverified end-to-end state has its own section and step 7 acceptance/recheck. The D-101 marker remains. Those markers are appropriate unpublished material; checklist step 8 refuses to publish with either unresolved.

Disclosing `CONVERT-JOB-GPU-PREFERENCE-IGNORED` is fair within the approved RC scope: default conversion still works, the saved GPU setting controls selection, and the notes explicitly withdraw any expectation that the per-job selector works. The smoke did not claim software encoding; its hevc_nvenc result is disclosed. This is not evidence that CPU-only clean-machine conversion was tested.

The checklist sequences D-101 and any necessary source/rebuild work, commit/push and CI, record verification against the pushed commit, tag, draft asset, clean-machine check or waiver, Transcript recheck or actual acceptance, publication and the later README edit. Source assets must follow the ruling; current GPL binaries cannot be uploaded first. Its opening instruction requires Mat's go-ahead for each step. Commands printed in a checklist, including a future tag push, are not present authorization to execute them.

### Q7 — corrected gate and incomplete verification

Accepted as the plan's **incomplete-verification** gate, not a clean audit. Current handoffs, current-focus and the audit report plainly carry the gap. The saved gate has Python 1,100, UI 1,111, MCP 466 and Electron 181 passes; zero excused baseline failures; audit 98/99 with discovery clean and cleanup/isolation true. Only transcript.compile is hollow, with the disclosed 37-byte output. The offline structural rule accepts that summary, and the saved rule receipt records the direct-fetch block. No current caption-block proof was repeated here.

Attempt 1 is preserved with 1 failed/464 passed at AC-68.2 and later stages not_run. The correction removed the server import without changing that control. The current build receipt has a different input identity and installer hash from attempt 1; fresh smoke, packaged probes, installed-app/uninstall and row-13 record checks follow the rebuilt artifact. The final gate has 466 MCP passes and matches that current build record. This supports the claimed S8 rebuild and rows 10–13 rerun, not reuse of the earlier installer.

The normal reviewer-side D6 identity is `24e27354e35eccc0cfa7d7e76357e673a6e38c23+fbe52f1ec29ccc3541ff4a965e129a79e9412064d49ff2879c3bc103eeaad421`, whereas the recorded gate is `24e27354e35eccc0cfa7d7e76357e673a6e38c23+7eba916b505e4b57972e18b490a2188bfd8f45355de54518bc51b05105fdc876`. Git reports the user's global ignore file inaccessible in this sandbox, and exposes the pre-existing untracked `.claude/settings.local.json` (metadata dates it to October 10). Adding only that path to PROJECT_ARTIFACTS **in memory**, with no file change, reproduces the recorded gate hash exactly. All recorded runtime/lock identities match. This is an observed local-file visibility distinction, not unexplained product drift; the independent product-input/installer checks also match. I have not called the unadjusted D6 hashes equal.

### Q8 — coverage and remaining boundaries

All 32 primary ACs were traced. New tests and runtime procedures cover the three fixes, versions, package metadata, licence refusal and attribution, packaged bans/layout, actual first conversion, MCP startup, cached-model TTS, installed app and uninstall, public materials and record integrity. Regression families AC-24/25/68/71/72/92 remain represented and were included in the saved full gate. Read the actual delivered residual sections and known-issues changes, not only handoff summaries.

No required product feature is hidden in the exclusion/deferral tables. The downscaled preview and other clients were not part of the agreed MEU-111 delivery. The clean-machine, D-101 and outward actions are explicit later human gates. Newly discovered GPU-preference and environmental-validator issues are filed; release-note defects correspond to filed issues. Fixed-issue/MEU lifecycle closeout is for the coordinator after this verdict, not evidence that those fixes are absent.

IR-5 grades: READY tests **Strong** (specific zero/one query counts and exact publication); conversion tests **Strong** (spawn-time state, persisted failure and real packaged conversion); transport and audit-step tests **Strong** (real connection survival and wrong-refusal negatives); licence fixtures **Strong** (one isolated fault per refusal and exact text assertions); release-metadata tests **Adequate** (static contracts, supplemented by direct licence/config inspection and actual packaged artifacts); packaged procedures **Strong within their declared scope**. The generator's initial Red was a missing-new-module failure, not behavioral Red; its Green fault fixtures were independently rerun and genuinely exercise the refusal behavior. No claim of a historical assertion failure was invented for it.

### Durable reviewer evidence

The commands below ran through `rtk proxy` with completed all-stream receipts and preserved native exits. Scratch paths are working records; the decisive results are embedded here.

```json
{"schema_version":"evidence.v1","check_id":"s44-review-python","command":"rtk proxy .venv/Scripts/python.exe -B -m pytest -p no:cacheprovider --basetemp C:/Temp/av-kit/s44-review-py-tmp-1 tests/unit/test_ffmpeg_conversion.py tests/unit/test_conversion_service.py tests/unit/test_release_packaging.py tests/unit/test_generate_third_party_licenses.py -q","cwd":"P:/av-kit","scope":"affected conversion, release metadata and licence-generator tests; PYTHONDONTWRITEBYTECODE=1; fresh isolated temp directory","phase":"targeted","exit_code":0,"result":"pass","tested_state":"HEAD 24e27354e35eccc0cfa7d7e76357e673a6e38c23; unchanged reviewed product tree; build_inputs 617f92d1bb0b9358a3cf6f95407cba86b5875e862acc0b424e57fe6ff73019e5","output":"123 passed in 5.87s. Earlier attempt: 27 passed, 96 setup errors because existing pytest-of-Mat temp directory was inaccessible; fresh --basetemp resolved the access limitation without code changes.","fresh":true}
```

```json
{"schema_version":"evidence.v1","check_id":"s44-review-mcp","command":"rtk proxy npx vitest run tests/image-over-stdio.test.ts tests/audit/capture-image-step.test.ts tests/audit/run-cli.test.ts tests/capture.test.ts","cwd":"P:/av-kit/mcp-server","scope":"built MCP server and real SDK transport, capture handler and actual audit steps/classifier; no YouTube requests","phase":"targeted","exit_code":0,"result":"pass","tested_state":"same reviewed product tree; SDK 1.32.2; build_inputs 617f92d1bb0b9358a3cf6f95407cba86b5875e862acc0b424e57fe6ff73019e5","output":"Test Files 4 passed (4); Tests 47 passed (47). Both oversize refusals preserve the connection; cap image is byte-identical; audit rejection negatives and AC-68.2 pass.","fresh":true}
```

```json
{"schema_version":"evidence.v1","check_id":"s44-review-ui","command":"rtk proxy npx vitest run tests/unit/ready-probe-guard.test.ts tests/unit/dev-spawn.test.ts","cwd":"P:/av-kit/ui","scope":"READY guard and existing Python spawn/publish tests; ELECTRON_RUN_AS_NODE unset","phase":"targeted","exit_code":0,"result":"pass","tested_state":"same reviewed product tree","output":"Test Files 2 passed (2); Tests 7 passed (7).","fresh":true}
```

```json
{"schema_version":"evidence.v1","check_id":"s44-review-ready-adversarial","command":"rtk proxy node C:/Temp/av-kit/s44-review-ready-probe.cjs","cwd":"P:/av-kit","scope":"actual HEAD and current python-manager modules transpiled in memory; publication equivalence under seven inputs","phase":"targeted","exit_code":0,"result":"pass","tested_state":"HEAD 24e2735 compared with current reviewed python-manager.ts","output":"Publication arrays equal in all seven cases. ordinary-output queries 2->0; port-zero 1->0; log/READY/log 3->1. Split marker and split before instance: zero publications both versions. Second READY: two publications both. Failed live query: one publication both. No actual process query ran.","fresh":true}
```

```json
{"schema_version":"evidence.v1","check_id":"s44-review-build-binding","command":"rtk proxy .venv/Scripts/python.exe -B C:/Temp/av-kit/s44-review-probes.py identity","cwd":"P:/av-kit","scope":"read-only reconstruction using Git tree/blob hashes without object/index writes; installer and packaged external DLL hashes","phase":"targeted","exit_code":0,"result":"pass","tested_state":"build_inputs 617f92d1bb0b9358a3cf6f95407cba86b5875e862acc0b424e57fe6ff73019e5","output":"Reconstructed build_inputs matches record. Installer 328403592 B, SHA-256 532663ea4c0040d81d2127193a19e156d1ff39dea932d1ec7ec797f0ec025df1. Both packaged FFmpeg hashes and all 48 Windows runtime hashes match.","fresh":true}
```

```json
{"schema_version":"evidence.v1","check_id":"s44-review-real-licences","command":"rtk proxy .venv/Scripts/python.exe -B C:/Temp/av-kit/s44-review-probes.py licences","cwd":"P:/av-kit","scope":"real-build licence generation in memory; generated/shipped byte comparison; actual exe archive bans and historical negative control","phase":"targeted","exit_code":0,"result":"pass","tested_state":"same product tree, Python 3.12.12, .NET runtime packs 8.0.33","output":"Regenerated 1102016 bytes, SHA-256 afb638f2750dcf5a7cb637cacf2abfc3c04cffffc2ac44fd40ca1ef747b83dfc; generated and shipped byte-identical True. Packaged archive bans []; negative control [espeakng_loader, kokoro, misaki.espeak, phonemizer].","fresh":true}
```

```json
{"schema_version":"evidence.v1","check_id":"s44-review-recorded-gate","procedure":"Codex read both saved H1-2 identity receipts, the gate's step exits and child summaries, archived attempt-1 build/failure, current build record and rows 11/12/13 results, and recomputed current runtime/product identities. No full gate or live audit was executed by reviewer.","observer":"Codex independent reviewer","cwd":"P:/av-kit","scope":"historical gate/build/install evidence and its applicability to reviewed product inputs","phase":"targeted","exit_code":null,"result":"pass","tested_state":"recorded D6 state 24e27354e35eccc0cfa7d7e76357e673a6e38c23+7eba916b505e4b57972e18b490a2188bfd8f45355de54518bc51b05105fdc876; reviewer visibility distinction explained in Q7","output":"Attempt 2: Python 1100, UI 1111, MCP 466, Electron 181 pass. Audit 98/99, exit 1, only transcript.compile hollow; discovery clean, isolation/cleanup true; saved rule exit 0. Gate wrapper exit 0 with INCOMPLETE VERIFICATION. Installed-app Settings/backend 200, isPackaged true, installed execPath, errors []; uninstall named surfaces new/lost []. Attempt 1 failed AC-68.2 and later stages did not run. This observation accepts the disclosed incomplete verification and does not call it a clean audit."}
```

```json
{"schema_version":"evidence.v1","check_id":"s44-review-audit-rule","command":"rtk proxy .venv/Scripts/python.exe -B docs/execution/plans/2026-11-03-release-rc1/audit-rule.py --selftest","cwd":"P:/av-kit","scope":"offline rule fixtures and simulated direct-fetch results only","phase":"targeted","exit_code":0,"result":"pass","tested_state":"same reviewed audit-rule.py","output":"audit-rule selftest: 31 of 31 passed. Separate offline problems() check of the actual saved summary returned []; only transcript.compile was non-pass. No caption fetch was executed.","fresh":true}
```

## Verdict

**approved** — all eight substantive questions were reached; no blocking defect was established. The work achieves RC1 preparation within the approved scope. The built installer, three fixes, packaged checks, licence list and unpublished release materials are supported by implementation, receipts and independent targeted checks.

This approves the implementation review, not release readiness without conditions. Transcript remains unverified end to end; the clean-machine, real F2 and first-model-provisioning checks remain pending or require Mat's explicit waiver; D-101 and corresponding-source availability remain publication gates. No commit, push, tag, upload, release, visibility change, FFmpeg re-pin or D-101 ruling is authorized by this verdict. H2 remains the coordinator's work after recording this verdict.

Report checks: durable evidence validation passes; the review-state and approved-state validators recognize execution round 1 of 6, approved, with zero open findings. The coordinator must save the report unedited and record the structured verdict in the existing ledger; these local report checks do not themselves record a ledger round.

## Recheck (2026-11-04)

**Workflow:** `/execution-critical-review`, multi-MEU execution, round 2 of 6; amendment since round 1 only.
**Agent:** Codex / OpenAI, class `avkit_independent_reviewer`, independent of Claude Code / Anthropic, the author.
**Verdict:** **changes_required**. Intent achieved: **partial**. Two Medium blocking behavior findings; no Critical finding. Round 1 had no findings to close, and its acceptance stands for untouched work.

### Intent Anchor

Session 44 prepares release candidate 1 of av-kit: MIT licence, the two first-run bug fixes (MEU-108, MEU-109), RC packaging and a real installer with packaged checks (MEU-110), release notes, a publish checklist and the D-101 brief, stopping before every outward step.

ECN-6/7 and D-202 through D-206 add MEU-112, implement the GPL re-pin/source decision, waive the named checks until publication, retain upstream attribution and select one session commit. This review assesses that amendment without reopening the closed plan loop or treating later H2 artifacts as missing work.

### Findings

| # | Severity | Blocking | Kind | Finding | File:Line | Recommendation | Status |
|---|----------|----------|------|---------|-----------|----------------|--------|
| F1 | Medium | yes | behavior | The settings initialization effect overwrites an explicit per-job encoder selection when settings arrive late or change. Reproduced: choose Software, release the pending settings response, then Add; the dropdown becomes Auto and the POST has no `gpu_preference`. A later saved-setting change similarly changes Software to Nvidia and omits the choice. On the NVIDIA machine this queues a hardware job despite the user's Software selection. Contract: AC-112.6 and 08's per-job Page rule. | `ui/src/renderer/src/features/converter/ConvertPage.tsx:269`, `:278`, `:727`; tests `ui/tests/unit/convert-page.behavior.test.ts:255` | Track whether the encoder itself was edited and preserve that value across settings initialization/refetch. Handle submission before the settings baseline is known. Add delayed-settings and subsequent-settings-change cases for Add and the command snapshot. | open |
| F2 | Medium | yes | behavior | The amended post-publication Transcript procedure still tests the development checkout, yet its success tells Mat to remove the public warning about this release build. Step 7 launches the default local audit, which resolves a development Python interpreter and starts `python -m avkit_api`, plus the locally built MCP server. It never exercises the downloaded installer's Transcript path. Following it can withdraw the warning without doing the published-release recheck specified in D-204/the amendment. Contract: AC-110, specifically AC-110.16's truthful verification/recheck instructions as amended by D-204. | `docs/releases/publish-checklist-v0.1.0-rc.1.md:160`, `:173`; `mcp-server/scripts/audit/backend.ts:135`, `:142`; `mcp-server/scripts/audit/run.ts:55`, `:411` | Keep the development audit as supplementary evidence. Require an actual fetch and compile through the app installed from the published asset, with an observed result, before removing the release-build warning. Preserve the warning if that packaged check remains waived or blocked. | open |

**Ledger constraint:** F1 honestly cites **AC-112.6**. Neither AC-112 nor its detailed criteria are in this loop's frozen permitted list; no registered family truly describes that UI behavior. Do not disguise it as AC-110 or a review mechanism to make recording pass. The supplied ledger rules therefore require Mat's decision when this verdict is submitted. F2 uses the registered family **AC-110**. Both are deliverable behavior findings, with no control-defeat mechanism; none of the three catalogued mechanism counts should increase.

### Prior Pass Summary

Round 1: approved, zero findings. Nothing to close. Its unchanged product-code acceptance remains in place. The rolling review, reflection, metrics and digest are allowed to predate the rulings and are not findings here.

### Scope and verification limits

Read the ECNs, amended plan/task, MEU-112 and changed MEU-110 handoff, the other three handoffs' refreshed gate records, the specified code/tests, source collector and cached recipe, release text, and saved row/build/install/gate evidence. Reviewed actual file contents where the cumulative HEAD diff could not isolate round 2.

Only scratch probes/receipts and the assigned report were written. No product, test, plan, registry or handoff was edited. No full gate, source fetch/pack, build, installation, live audit, caption request, commit or outward operation was run. YouTube traffic was zero. The prohibited secrets, hub and real app-data contents were not opened. Reading the source archive was limited to hashing its bytes and reading its first README member; no archive listing, unpacking or downloaded-code execution occurred.

### Checklist Results

| Check | Result | Observed command / procedure | Exit | Evidence |
|---|---|---|---|---|
| IR: amended scope, intent and independence | pass | Manual, Codex: compare request, ECN-6/7, D-202 to D-206, plan/task and five handoffs | null | Correct amendment and author/reviewer separation; untouched round 1 work retained |
| IR/PR: affected Python behavior and refusal tests | pass | `.venv/Scripts/python.exe -B -m pytest -p no:cacheprovider --basetemp C:/Temp/av-kit/s44-r2-py-tmp tests/unit/test_conversion_service.py tests/unit/test_ffmpeg_conversion.py tests/unit/test_assemble_ffmpeg_source.py tests/unit/test_packaging_installer.py tests/integration/test_sqlite_uow.py -q` | 0 | 157 passed in 6.28s |
| PR: submitted Convert behavior suite | pass | `npx vitest run tests/unit/convert-page.behavior.test.ts` from `ui/` | 0 | 44 passed; these cases do not cover settings timing |
| DR/PR: encoder selection across settings timing | fail | `node C:/Temp/av-kit/s44-r2-ui-node.cjs` | 1 | Actual ConvertPage and collaborators bundled into a scratch jsdom probe: two overwritten choices; normal loaded-settings control preserves and sends Software |
| DR/PR: persistence through restart and requeue dispatch | pass | `.venv/Scripts/python.exe -B C:/Temp/av-kit/s44-r2-restart-probe.py` | 0 | New service and new engine over the same scratch SQLite DB run the stored Software choice as libx265 with setting Nvidia; reset and second execution also libx265 |
| DR: source selection against cached recipe/manifest | pass | `.venv/Scripts/python.exe -B C:/Temp/av-kit/s44-r2-source-probe.py` | 0 | 134 scripts, 739 manifest rows, no missing declared primary source, requested direct submodule, DEPS item, locked crate or requested wrap; no network or recipe execution |
| DR/PR: artifact and pin binding | pass | Asset probe and read-only build-input reconstruction, commands embedded below | 0 | Current installer, source archive, pin ZIP, packaged binaries, build identity and records match; no source rebuild claimed |
| DR: public claims and amended follow-up target | fail | Manual, Codex: trace checklist step 7 through actual audit launcher and compare D-204 | null | F2; order exception and current incomplete-verification wording are otherwise clear |
| IR: D-205 condition | pass | Manual, Codex: read convention report, count addresses without printing them in shipped notices, inspect primary upstream notices | null | Conventional upstream attribution retention supported; counts are not a universal survey |
| PR: recorded gate and evidence freshness | pass | Manual, Codex: compare five handoffs with child receipts, build record and independent identities | null | Python 1186, UI 1115, MCP 466, Electron 181; audit remains 98/99 and non-pass; wrapper remains INCOMPLETE VERIFICATION |
| H2 refresh and outward actions | n/a | Coordinator/Mat follow-up after this review | null | No implementation completion, ledger acceptance, commit or publication is authorized by this report |

### Q1 — Encoder paths

Accepted on the service side. `_jobs_for_path` stores the request preference only for Compress (`services/conversion.py:306`). `_worker` reloads pending rows; `_run_one` passes its freshly loaded Processing job through the sole `_dispatch` path; `:488` supplies `job.gpu_preference` to `_resolve_encoder`. Null alone calls `_preference`, so explicit Auto correctly selects `caps.recommended_encoder` over a non-auto setting. Nvidia/AMD/Intel retain the existing unavailable-hardware fallback, and Software retains the libx265/libx264 fallback. Cut and Extract store null and do not acquire the Compress override.

The existing requeue and SQLite assertions are meaningful, although separate rather than a whole restart execution. My additional probe closed that combination: queue Software, dispose the database engine, construct a new engine and service, change the setting to Nvidia, then start. Both `gpu_encoder` and the media port's actual codec were libx265; a subsequent reset/reexecution also passed. No surviving setting-only Compress dispatch was found.

### Q2 — Upgrade and page

Accepted for the database. `init_schema` creates absent tables, then `apply_migrations` creates its guarded DDL, applies the existing table-guarded download backfill, and adds the column only if PRAGMA says it is absent. The nullable last column leaves old rows intact. AC-112.5 really creates the old schema with a row, loads that row with null preference, applies migrations again, and compares fresh/upgraded column order; the integration suite also passed. There is no observed collision with the existing data migrations.

The comparison in both Add and `snapshotCreateInput` correctly handles Auto versus a loaded non-auto setting, and equal values remain omitted so those jobs read the setting when run. **Not accepted across settings timing (F1).** The encoder's onChange never marks it touched; the effect guards only `presetTouched`. My probe reproduced Software→Auto on late settings and Software→Nvidia on a changed saved setting, with the preference absent from both POSTs. The unchanged-loaded-setting control sent Software. Existing AC-112.6 tests await initialization or directly supply a snapshot, so all 44 can pass while this behavior is broken. This is one underlying defect, not separate findings for each timing variant.

### Q3 — Source set, refusals and disclosure

Accepted for the frozen pin on the static evidence examined; no missing shipped dependency was established. The collector reads enabled recipe scripts without executing them, fetches pinned primary trees, recursively follows requested Git submodules, adds shaderc DEPS entries, registry crates for rav1e/librsvg, the Opus model, GLib's requested Meson wrap, SVN sources and the selected toolchain archives. The actual recipe uses only the three SCRIPT_REPO suffixes the parser handles. My cached-tree/manifest probe found no missing declared item. GLib's GVDB is included as a submodule; its proxy-libintl is present as the requested wrap. Pango/GLib use nodownload and satisfied supplied libraries, HarfBuzz disables tests/docs/utilities and its optional GLib/Cairo paths, libaribcaption disables embedded FreeType, Kvazaar's CMake file is not its selected build system, VMAF disables tests, and dav1d's checkasm is test tooling. The 88 hints are candidate fetching files, including documentation, not 88 demonstrated missing runtime dependencies.

The binary configuration test is a useful independent cross-check, **not a general proof of every transitive build input**: it compares enable-flag coverage and the FFmpeg revision, while collection/manifest checks establish the source presence. The recipe may contain spare sources; the only unused explained enable flag here is OpenSSL. The packed README is the first member, matches the current generator byte for byte, and names the unpinned crosstool-NG revision, Rust/cargo-c/Meson/Ubuntu tools, rav1e's cc update, and internal Meson/CMake fetches including checkasm. This disclosure is easy for a recipient to encounter. The archive has not been rebuilt into FFmpeg, and I do not certify reproducibility or give a legal opinion.

The tests came after the tool; they prove present refusal behavior, not a historical tests-first sequence. They exercise unknown fetch steps, bad hashes/pins, unavailable sources, moved toolchains, unexplained binary flags, missing documents, incorrect archive counts and oversize assets. The separate pax-header mutation receipt reports **2 failed, 8 passed, 67 deselected**, specifically losing the long-path member from the archive root. That supports a sensitive regression test even though the first fix preceded its initial test. No historical Red is invented.

### Q4 — Re-pin and compatibility

Accepted. Collector constants, fetch defaults, notices, README, build record and actual packaged `ffmpeg.exe -version` agree on BtbN `autobuild-2026-10-31-12-59`, FFmpeg `n8.1.3-27-g8dca1586f4-20261031`, commit `8dca1586f468bfcbb78ae3ed618af1361d9f140a`. The cached ZIP SHA-256 is `401dffcf14c301082e1fc03b0bc876b92ea676bfc521fc56e80a1537d137034f`; the fetch script hashes even in ExtractOnly mode before extraction. The build script clears URL/hash overrides. Both packaged executable hashes match the build record.

The actual rebuilt smokes run hevc_nvenc and libx265 with this pin; conversion tests pass. No changed encoder name, used argument or version-parsing incompatibility was established. This is not a fresh CPU-only, AMD or Intel machine test; the notes and MEU-112 handoff disclose the NVIDIA-only runtime evidence.

### Q5 — Rebuild, S8 and exclusions

Accepted. Independent read-only blob reconstruction gives `build_inputs 8f277206d5ef50086cec92e628dafb88579c77c3cae4fc42b97a4153b5c71663`. The current installer is **340,346,916 B**, SHA-256 **67e6614e9ba4388bc52c28c5c59584843b3b0f01d9cda7a26cce3a17d1546887**. Public and local build records are equal; both packaged FFmpeg hashes and all 48 recorded Windows runtime hashes match. Build and rows 10–13 receipts follow the amendment and each has exit 0; both saved packaged/installed smokes contain the second Software job (Done, libx265). This supports S8's rerun rather than reuse of the round 1 installer. No later build-input drift was found.

The unadjusted reviewer D6 state is `24e27354e35eccc0cfa7d7e76357e673a6e38c23+d0b8513aa0c075719f37319a166f6f8089bd2e32d24755846649b1ff4031f177`. As in round 1, this sandbox cannot read the user's global ignore file and exposes the pre-existing October 10 `.claude/settings.local.json`. Excluding **only that path in memory**, without editing any file, reproduces the exact recorded state `24e27354e35eccc0cfa7d7e76357e673a6e38c23+f52fc9d6226055938aa173331a14c5cdb4b9f3ccc9b90fc6499bf2e0e4cf0708`; runtime and lock identities agree. A normal uv invocation was blocked by cache permissions, so this was recomputed with the same `.venv` interpreter directly; no install or dependency change was made.

ECN-7 adds exact allowed paths rather than a broad new scope prefix. The digest is a closeout output, not a product build input; the scoped tests/tools search found its only reference in the gate's allowed-path list. `.agent/fleet.json` is ignored locally and is not in the builder's `out/**/*` or explicit extraResources inputs. Its exclusion does not hide shipped product code. Neither adjustment was used to suppress the UI defect reproduced above.

### Q6 — Public claims and outward steps

Accepted for current artifact values, explicit waivers and operation ordering; **not accepted for step 7's verification target (F2)**. Source archive: **992,681,460 B**, SHA-256 **953a62373693e388a853ee2c6dbfadf4ce12e7f4aeb13b86e26f179b48d07284**, independently rehashed. Installer values match. Source and installer are uploaded together in step 5, and step 8 refuses publication without the named source asset. The opening exception explicitly runs steps 6 and 7 after step 10, so their retained numbering does not force a prepublication test or create a circular wait. The reminder after publication is present. README's installer note remains pending as directed.

The current release notes plainly distinguish backend API Software encoding from an installed-dropdown run, existing-PC install/uninstall from a clean machine, cached-model offline TTS from first-model download, and stub picker startup from a real F2 capture. They do not claim a no-NVENC machine was exercised. Transcript remains explicitly unverified; no existing receipt is represented as a clean audit.

F2 concerns the **new published-release follow-up**, not a re-review of the accepted development audit itself: the revised checklist says the waived checks will run from the public release, but its Transcript success branch still removes a release-build warning using a checkout-only result. The launcher trace is decisive without network execution. Add the actual downloaded-app Transcript procedure; no new audit subsystem is necessary. The GPL source material includes libdvdcss, which the handoff explicitly notes for Mat; this review makes no legal determination about it.

Every outward step still requires Mat. No commit, push, tag, upload, release, README-note removal, repository setting change or worktree removal occurred or is authorized here.

### Q7 — D-205 condition

Accepted as evidence of established practice for upstream-authored notices. The report records occurrence counts of 168 addresses in Electron/Chromium, 5 in Node, 2 in VS Code and 2 in zlib; CPython/Rust examples with none do not contradict the practice. My actual shipped Chromium and generated-notice scans confirm many upstream addresses without reproducing them here; unique-address counts are a different measure from the report's occurrence counts. zlib's primary notice itself retains author contact details and says the notice may not be removed or altered. See [zlib's upstream licence](https://raw.githubusercontent.com/madler/zlib/master/LICENSE); [Node's upstream licence collection](https://raw.githubusercontent.com/nodejs/node/main/LICENSE) and [VS Code's third-party notices](https://raw.githubusercontent.com/microsoft/vscode/main/ThirdPartyNotices.txt) also illustrate preserving component notices.

This supports retention in the actual shipped third-party texts and source trees. It is not proof that every project retains every address or that none ever removes one. No personal or gmail-form address is quoted in this report. The archive's saved old-address scan is accepted as the existing measurement bound by its independently matched hash; that scan was not rerun.

### Q8 — Gate, coverage and Mat's five rulings

Accepted for evidence honesty and counts. All five handoffs carry attempt 3's **1186 Python, 1115 UI, 466 MCP, 181 Electron passes**, matching the child receipts. The audit still reports **98/99**, exit 1, with only transcript.compile failing, and the wrapper ends **INCOMPLETE VERIFICATION**. No baseline failure was excused. The 37-byte compile artifact is not meaningful Transcript content; the gate and release text retain that limitation. Attempt 2 is clearly historical and superseded, with its earlier state and counts retained in prose. Removing its passing full JSON record to satisfy the current-state validator does not claim it never ran or erase attempt 1's failure; it is honest in this context.

AC-112.1–.5 have meaningful codec, field-retention, validation and migration assertions; AC-112.7 has a real packaged API receipt. AC-112.6 covers loaded-setting comparisons but misses the timing failure in F1. AC-110.20–.22 have actual refusal/collection/archive fixtures and real source measurements; their evidence is not misrepresented as tests-first. IR-5: service and migration tests **Strong**; source refusal/archive tests **Strong within the declared pin and static collection model**; page tests **Adequate for initialized settings, incomplete for F1**; packaged Software checks **Strong for the backend API and this NVIDIA PC**, not evidence of an installed UI or no-NVENC run. No new skip/only/xfail masking or incomplete product stub was found.

Ruling 1: GPL retained, re-pinned, archive prepared and paired with the installer; no publication occurred. Ruling 2: service/persistence fix delivered, UI still needs F1. Ruling 3: waivers and reminder implemented, but published-app Transcript follow-up needs F2. Ruling 4: upstream attribution retained with convention evidence. Ruling 5: single-commit instruction and draft plan recorded; the actual commit appropriately remains unexecuted until its authorized next step. No other required work was quietly deferred.

### Durable reviewer evidence

All commands ran through `rtk proxy`, with completed all-stream receipts and preserved exits. The decisive observations below are durable; scratch paths alone are not the evidence.

```json
{"schema_version":"evidence.v1","check_id":"s44-r2-python","command":"rtk proxy .venv/Scripts/python.exe -B -m pytest -p no:cacheprovider --basetemp C:/Temp/av-kit/s44-r2-py-tmp tests/unit/test_conversion_service.py tests/unit/test_ffmpeg_conversion.py tests/unit/test_assemble_ffmpeg_source.py tests/unit/test_packaging_installer.py tests/integration/test_sqlite_uow.py -q","cwd":"P:/av-kit","scope":"amended conversion, migration, source-tool and packaging behavior","phase":"targeted","exit_code":0,"result":"pass","tested_state":"build_inputs 8f277206d5ef50086cec92e628dafb88579c77c3cae4fc42b97a4153b5c71663; reviewed round 2 tree","output":"157 passed in 6.28s","fresh":true}
```

```json
{"schema_version":"evidence.v1","check_id":"s44-r2-ui-suite","command":"rtk proxy npx vitest run tests/unit/convert-page.behavior.test.ts","cwd":"P:/av-kit/ui","scope":"actual submitted Convert behavior suite","phase":"targeted","exit_code":0,"result":"pass","tested_state":"same reviewed round 2 tree","output":"Test Files 1 passed (1); Tests 44 passed (44). Settings-timing cases are absent.","fresh":true}
```

```json
{"schema_version":"evidence.v1","check_id":"s44-r2-ui-adversarial","command":"rtk proxy node C:/Temp/av-kit/s44-r2-ui-node.cjs","cwd":"P:/av-kit","scope":"actual ConvertPage and collaborators bundled without source changes; jsdom, controlled settings fetch/cache, real Add request construction","phase":"targeted","exit_code":1,"result":"fail","tested_state":"same reviewed round 2 tree","output":"Late settings: before software, after auto, POST {paths:[C:/probe.mp4],kind:compress,preset:balanced}, preference absent. Saved setting changes: before software, after nvidia, same omitted preference. Loaded-settings/no-change control: before software, after software, POST includes gpu_preference:software. choice preserved false false true. This is a behavioral reproduction; earlier scratch Vitest attempts could not resolve cross-drive modules and were not counted as product failures.","fresh":true}
```

```json
{"schema_version":"evidence.v1","check_id":"s44-r2-restart","command":"rtk proxy .venv/Scripts/python.exe -B C:/Temp/av-kit/s44-r2-restart-probe.py","cwd":"P:/av-kit","scope":"real scratch SQLite engine/UoW, new service after disposal, existing RecordingMedia collaborator; no app data or FFmpeg process","phase":"targeted","exit_code":0,"result":"pass","tested_state":"same reviewed round 2 tree","output":"restart: stored Software, setting Nvidia, persisted encoder and actual options libx265; Done. requeue execution: stored Software survives reset and second dispatch; libx265; Done.","fresh":true}
```

```json
{"schema_version":"evidence.v1","check_id":"s44-r2-build-binding","command":"rtk proxy .venv/Scripts/python.exe -B C:/Temp/av-kit/s44-review-probes.py identity","cwd":"P:/av-kit","scope":"read-only Git blob reconstruction; no temporary index/object writes; installer and packaged external hashes","phase":"targeted","exit_code":0,"result":"pass","tested_state":"build_inputs 8f277206d5ef50086cec92e628dafb88579c77c3cae4fc42b97a4153b5c71663","output":"read-only build_inputs matches True; installer 340346916 B, sha256 67e6614e9ba4388bc52c28c5c59584843b3b0f01d9cda7a26cce3a17d1546887; packaged FFmpeg hashes match record; packaged Windows runtime hashes match 48.","fresh":true}
```

```json
{"schema_version":"evidence.v1","check_id":"s44-r2-source-and-state","command":"rtk proxy .venv/Scripts/python.exe -B C:/Temp/av-kit/s44-r2-assets-probe.py","cwd":"P:/av-kit","scope":"source archive hash and first README only; trusted packaged FFmpeg -version; cached ZIP hash; in-memory D6 visibility adjustment; public/local record comparison","phase":"targeted","exit_code":0,"result":"pass","tested_state":"24e27354e35eccc0cfa7d7e76357e673a6e38c23+f52fc9d6226055938aa173331a14c5cdb4b9f3ccc9b90fc6499bf2e0e4cf0708 after the sole documented in-memory visibility adjustment","output":"source archive 992681460 B, sha256 953a62373693e388a853ee2c6dbfadf4ce12e7f4aeb13b86e26f179b48d07284; first README equals current tool True and names disclosed gaps; packaged binary n8.1.3-27-g8dca1586f4-20261031; unexplained enable flags none, unused explained OpenSSL; pin ZIP hash matches True; public/local build records equal True.","fresh":true}
```

```json
{"schema_version":"evidence.v1","check_id":"s44-r2-source-selection","command":"rtk proxy .venv/Scripts/python.exe -B C:/Temp/av-kit/s44-r2-source-probe.py","cwd":"P:/av-kit","scope":"read-only cached recipe and manifest comparison; no downloaded scripts executed and no fetch/pack","phase":"targeted","exit_code":0,"result":"pass","tested_state":"same reviewed source tool, recipe commit 5031c6f1082414e53688d39e521849905071070d and current manifest","output":"rows 739; recipe scripts 134; missing direct/declared transitive []; GLib GVDB and proxy-libintl present. This is static coverage, not a rebuilt binary or a universal transitive-completeness oracle.","fresh":true}
```

```json
{"schema_version":"evidence.v1","check_id":"s44-r2-public-transcript-procedure","procedure":"Codex compared the amended published-release follow-up with checklist lines 148-175 and traced the exact no-override audit command through run.ts DEFAULT_SERVER/default launcher, client.ts buildLaunch, and backend.ts resolvePython/spawnBackend. No process or network request was launched for this check.","observer":"Codex independent reviewer","cwd":"P:/av-kit","scope":"D-204 and AC-110.16 public verification instructions","phase":"targeted","exit_code":null,"result":"fail","tested_state":"same reviewed release checklist and existing audit runner","output":"Step 7 builds local MCP and runs the default audit. Default server is mcp-server/dist/index.js; client launches node; backend resolves uv's Python and starts -m avkit_api. Checklist line 173 nevertheless tells Mat to remove this release build's unverified section on audit exit 0. No downloaded/installed RC Transcript check is in that procedure."}
```

### Verdict

**changes_required**, round **2**. All eight questions were reached. Preserve the accepted service/persistence/migration, re-pin/source evidence, rebuilt artifacts, waivers, attribution and incomplete-gate disclosure. Correct F1's lost encoder selection and F2's published-release verification instruction, then rerun the affected checks and apply S8 if product build inputs change. Do not spend another round on the unchanged round 1 work or later H2 paperwork.

The report's frozen-AC mismatch is disclosed above and must not be silently coerced. This review does not record a ledger round, authorize outward actions or claim session DONE.


## Recheck (2026-11-04)

**Workflow:** `/execution-critical-review`, multi-MEU execution, changes since the preceding verdict. **Report round 3; intended ledger round 2 of 6:** the previous verdict was refused for its honest AC-112 citation and consumed no ledger round; D-210 authorizes re-dispatch in the same loop.
**Agent:** Codex / OpenAI, class `avkit_independent_reviewer`, independent of the author, Claude Code / Anthropic.
**Verdict:** **changes_required**. **Intent achieved: partial.** F2 is fixed. F1's original reproductions pass, but a verified settings-draft path still silently omits the user's encoder choice.

### Intent Anchor

Session 44 prepares release candidate 1 of av-kit: MIT licence, the two first-run bug fixes (MEU-108, MEU-109), RC packaging and a real installer with packaged checks (MEU-110), release notes, a publish checklist and the D-101 brief, stopping before every outward step.

The anchor predates MEU-111, MEU-112 and Mat's D-101 ruling. Their accepted additions remain in scope. This recheck covers ECN-8/9, D-207 through D-210, the affected tests, fifth build and attempt-5 records. Prior acceptance of the service, persistence, migration/restart, source set, re-pin and D-205 stands. H2 reflection, metrics and digest refreshes follow review and are not missing work at this boundary.

### Findings

| # | Severity | Blocking | Kind | Finding | File:Line | Recommendation | Status |
|---|----------|----------|------|---------|-----------|----------------|--------|

No additional finding ID is introduced; **F1 is carried open**, as the Prior findings table records. **Severity: Medium; blocking: yes; kind: behavior; subject: deliverable; confidence: High; status: open.** The encoder comparison still uses a settings draft as the saved setting. With saved Software, explicitly choose Auto then Software, edit Output folder without saving, then refetch settings after the saved GPU preference changes to Nvidia. The query cache correctly contains Nvidia and the dropdown still shows Software, but both Add and the command snapshot omit gpu_preference. The backend therefore follows Nvidia, silently ignoring the displayed explicit Software choice. The identical refetch without the Output folder draft sends Software correctly. This is the remaining F1 behavior through a verified stale-baseline cause, rather than an effect overwriting encoderChoice. **Violates AC-112**, specifically AC-112.6 and AC-112.8.

**File:line:** `ui/src/renderer/src/features/converter/ConvertPage.tsx:196`, `:297`, `:342`, `:727`, `:807`; `useConverterSettings.ts:63-69`; `convert-commands.ts:174`. **Recommendation:** expose/use the current saved query baseline independently of the editable output/skip draft. Compare both submission paths against that saved GPU value, and use it for an untouched dropdown. Add a dirty Output folder or Skip existing → saved GPU update/refetch regression, with both display and Add/snapshot assertions.

**Ledger constraint:** the honest blocking citation is **AC-112**. That family is absent from this loop's frozen registry. Under Mat's D-210 ruling, submission must be refused and return to Mat; do not remap this to AC-110 or a review mechanism. This is a deliverable behavior finding, not control-defeat; no mechanism count increases.

### Prior findings

| Finding | Recheck result | Evidence |
|---|---|---|
| F1 | open | Original late-settings and later-settings-change reproductions now pass. However, the actual-page dirty Output folder plus settings-refetch reproduction still drops explicit Software in both submission paths while displaying Software. The same refetch with no draft is a passing control. Details and decisive output below. |
| F2 | fixed | `publish-checklist-v0.1.0-rc.1.md:150-173` makes the installed published app and real spoken words decisive. The supplementary development audit at `:175-207` cannot remove the release warning, including on exit 0. |

### Scope and verification limits

Read current source/tests, amended plan/task, the changed sections across all five handoffs, release materials and decisive saved receipts. HEAD remains `24e27354e35eccc0cfa7d7e76357e673a6e38c23`; the work is intentionally uncommitted. Reviewer writes are confined to this report and scratch artifacts under `C:/Temp/av-kit`. No product/test/plan/handoff correction, full gate, rebuild, install, live audit or YouTube request was performed.

The fresh reviewer Electron invocation exited **1** at `electronApplication.firstWindow: Target page, context or browser has been closed` (`backend-output-after-close.test.ts:18`). It reached no handler assertion. That is a reviewer runtime limitation, not a fresh crash-fix pass or evidence that the handler failed. The saved real-Electron Red/Green and matching attempt-5 records remain the runtime evidence. No installed-copy close-with-logging interaction was reproduced by hand.

### Checklist Results

| Check | Result | Command or observed procedure | Exit | Evidence |
|---|---|---|---|---|
| IR-1 / original F1 reproduction | pass | `rtk proxy node C:/Temp/av-kit/s44-r2-ui-node.cjs` | 0 | Current page rebundled; delayed settings, later saved-setting change and unchanged-setting control retain Software and send it. `choice preserved true true true`. |
| IR-4 / encoder generalization | fail | `rtk proxy node C:/Temp/av-kit/s44-r3-ui.cjs` | 1 | Eleven cases pass; dirty Output folder plus saved GPU refetch fails. Current cache Nvidia, visible Software, actual POST and snapshot both omit gpu_preference. Identical no-draft refetch passes. |
| IR-5 / submitted affected tests | pass | `rtk proxy npx vitest run tests/unit/convert-page.behavior.test.ts tests/unit/ready-probe-guard.test.ts` from `ui/` | 0 | Two files, 62 passed. Encoder timing assertions are meaningful but do not cover the settings-draft baseline. Log unit tests are Strong, including live-send and both caller sites. Real-Electron regression is Strong for its direct-handler scenario; saved Red fails at the intended assertion. |
| IR-1 / fresh reviewer Electron | n/a | `rtk proxy npm --prefix ui run test:e2e -- tests/e2e/backend-output-after-close.test.ts`, ELECTRON_RUN_AS_NODE unset | 1 | Closed before firstWindow; no runtime assertion reached. Saved Green has 1 passed and attempt 5 includes the case among 182 passes. |
| IR-2 / IR-3 / IR-6 | pass | Codex inspected request serializers, query/draft ownership, log/READY wiring and adjacent main-process callers | null | Production page/hook/serializer exercised with controlled fetch responses. No changed route/error schema. Existing validated GPU enums and backend null-versus-explicit semantics remain accepted. |
| F2 / release instructions | pass | Codex traced step 7 against TranscriptPage controls and service failure status | null | Failed/no-content paths retain the warning without needing error text; development success cannot clear it. No fetch was executed. |
| PR / fifth build binding | pass | `rtk proxy .venv/Scripts/python.exe -B C:/Temp/av-kit/s44-review-probes.py identity`; read-only ASAR byte comparison | 0 | Current build_inputs, installer size/hash, packaged FFmpeg and 48 runtime hashes match. Packaged main and Convert bundles equal gate output byte for byte. |
| IR-7 / gate and handoff evidence | pass | Independent D6 recomputation; `durable_evidence.evidence_problems(..., require_full=True, expected_state=current)` on all five handoffs; child-receipt comparison | 0 | Five matching current passing full records, zero evidence problems. Audit remains 98/99, exit 1; wrapper says INCOMPLETE VERIFICATION. Historical failed attempt 1 is retained separately. |
| DR / unchanged and later-stage work | n/a | User-defined scope | null | No formatting findings sought. Unchanged accepted work and post-review H2 refreshes were not reopened. |

### Q1 — Encoder paths and the remaining F1

**Accepted:** storing `encoderChoice` separately closes the original effect-overwrite cases. Untouched dropdowns omit an override; explicit Auto before settings arrive is sent; presets do not overwrite encoderChoice. Both Add and the command snapshot use the same `perJobGpuPreference` function. My own original reproduction passes all three cases. Eleven further actual-page cases also pass, including preset-before-settings, preset-after-pick, changed saved settings, equal picks and an equal pick followed by a different setting.

**Not accepted:** the value called `savedEncoder` is `converter.form.gpu_preference` (`ConvertPage.tsx:196`). That form is `draft ?? baseline`, and editing Output folder or Skip existing snapshots the entire baseline into the draft (`useConverterSettings.ts:63-69`). A subsequent successful settings fetch updates baseline but cannot update the draft's GPU value. Add and the palette therefore agree on the same stale comparison.

The independent probe drives actual page events: load saved Software; select Auto then Software; edit Output folder to `C:/edited-output` without Save; change the mocked server's saved GPU to Nvidia and invalidate/refetch the settings query; Browse and Add. It observes:

```text
command: rtk proxy node C:/Temp/av-kit/s44-r3-ui.cjs
exit: 1
control, no draft:
  displayed software; cachedSaved nvidia; outputDir C:/probe
  snapshot and POST: paths [C:/probe.mp4], kind compress, preset balanced, gpu_preference software
dirty Output folder:
  displayed software; cachedSaved nvidia; outputDir C:/edited-output
  snapshot and POST: paths [C:/probe.mp4], kind compress, preset balanced
  gpu_preference absent; ok false
Error: probe failed explicit Software with dirty output then saved Nvidia refetch
```

Only GPU preference changes in that refetch; no default-preset change is needed. This is not relying on a dropdown reselecting its already-selected option, a direct call to the helper, or a fetch that never reaches the page. A saved setting can change through another supported client; the existing AC explicitly covers settings changing afterwards. With no per-job value the accepted backend deliberately reads that setting at execution, so an NVIDIA-capable user gets hardware encoding despite explicitly selecting Software. No backend behavior needs to be reopened to establish that consequence.

AC-112.8's tests wait for query notifications and contain real value/body assertions. Their kept Red has seven behavioral assertion failures plus the declared-new helper failure, with one untouched-setting control passing. Earlier false passes were repaired before Green. However, the new tests never dirty the page's settings form before refetch. The fresh **53 Convert plus 9 READY/log tests all pass while the reproduction above fails**. Their existing scenario coverage is useful; it is insufficient to close F1.

### Q2 — D-208

**Accepted as a disclosed pre-existing limitation, not fixed.** My actual-page probe sets CQ 31, Scale 480 and Audio copy before settings arrive; the fields then visibly become **25, 0, aac_128**, and Add/snapshot use those displayed defaults. `v0.1.0-rc.1.md:133-134` describes that snap-back accurately. Calling it cosmetic understates the possible inconvenience, but the replacement is visible and D-208's narrow, low-priority RC deferral is reasonable. F1 above is materially different: Software remains displayed while the request silently follows Nvidia. It is not an escalation of the disclosed CQ/Scale/Audio reset.

### Q3 — Published-app Transcript recheck

**Accepted; F2 fixed.** Step 7 downloads the named published asset, checks its hash and uses the step-6 installation. Channel URL, Add, Start, Compile and View compiled exist. The example count is illustrative. The positive branch requires actual spoken words in the file, avoiding a heading-only success.

The service makes the parent Failed after failed fetching (`services/transcript.py:432-436`), and the page shows status/counts without the item error text. The revised step explicitly accommodates this: no transcripts or Failed keeps the warning and requests supplementary investigation; contentless compile stops for Mat; an unrun check leaves the warning. Development audit exit 0 still leaves the warning and requires another installed-app check. Refusal goes to Mat. No checkout result can clear the statement about this release build, and this review generated no network traffic.

### Q4 — Crash fix and regression

**Accepted.** `forwardConsoleLines` checks null/destroyed windows before touching webContents and contains a send/access exception (`python-manager.ts:133-144`). The handler appends each line to the in-memory log first, then forwards; its additional READY note uses the same helper (`index.ts:273-290`). Both stdout and stderr register the same handler. `publishBackendReady` stores state/resolves waiters and does not access a window. No other backend-output route to the window was found.

The adjacent inbox notifier checks window destruction, capture publication contains announcement errors, and fireRegion catches capture rejection. Startup reveal uses ready-to-show; second-instance handling selects current windows. No additional demonstrated automatic destroyed-window failure was established. The tray's Show window still holds an unguarded reference; D-209 deliberately leaves the separate user-click-during-shutdown race. That bounded residual does not defeat this handler fix.

The new E2E loads the real compiled main, destroys its actual BrowserWindow, locates streams with the actual named onChildOutput listener and emits a nonempty line. It asserts destruction and **streams > 0** before accepting an empty thrown list. No matching handle therefore fails; it cannot silently pass without exercising a handler. The kept Red reaches its final assertion with **two Object has been destroyed exceptions**, rather than failing setup. Saved Green has **1 passed**; attempt 5 includes the unchanged test. Live-send unit assertions also reject a no-op helper. This proves the direct-handler scenario, not natural pipe timing or every main-process path.

The release note's conditional Close-to-tray-off explanation follows the shared packaged window lifecycle; it does not claim an installed-copy manual reproduction. The handoff explicitly distinguishes inference from measurement. My fresh Electron limitation remains as disclosed above.

### Q5 — Attempt 4

**Accepted with causes unresolved.** Archived output says **2 failed, 179 passed**. AC-66.14 timed out at 60 seconds without a failed behavioral assertion in its diagnostic: a dialog holding app.close() fits, but is not proved. AC-88.12's primer read an empty clipboard for five seconds before the app's Copy action. Desktop clipboard interference while Mat used the PC is a candidate, not an established cause.

Both tests subsequently passed **8/8 each**, then attempt 5. An exact diff from HEAD for both tests, Playwright config and its output wrapper is empty apart from Git's ignore-permission warning. The gate still runs the whole Electron suite; the added regression raises the total from 181 to 182. No weakened assertion, omitted test, relaxed timeout or retry masking was found. Fixing the separately reproduced crash and obtaining a complete new run is an honest basis for proceeding. The generic main-process-exception watcher gap and unreproduced primer failure do not establish a remaining RC product defect requiring more than low severity.

### Q6 — Rebuilds, counts and records

**Accepted.** S8 was applied after F1's UI edit (fourth build) and after the crash fix (fifth). Current row exits and timestamps place the fifth build, unpacked probes, install/uninstall and release-material refresh before attempt 5. Independent read-only blob reconstruction matches **build_inputs 19e2e519beffd64d754428fea9f1c04cc889bf13e38f82576b678a441db57c0e**. Installer: **340,347,542 bytes**, SHA-256 **aabc4ae145e7f26f976e11263fd85936027473fe99b361390c30eb0fcbff1b50**. Public/local records are equal; packaged FFmpeg and all 48 runtime DLL hashes match.

The main entry in app.asar hashes to **9ca29d78071b8608d32dce8b231578fd051a5e1dbab216e21c513734c9f437da**; Convert's packaged chunk hashes to **6c5fd3b36e4564581db49819912cf4672a0875addbd7b9187f2a3e1af9f6446b**. Both equal the gate's current ui/out files byte for byte. Fifth-build saved smokes contain default hevc_nvenc and explicit Software/libx265; the round trip reports no added leftovers and preserved app-data entries. This binds the artifact to what was tested; it does not make F1's missing test pass.

The uv identity invocation was blocked by cache access (exit 2). Using the same `.venv` Python and runtime metadata with VIRTUAL_ENV/ELECTRON_RUN_AS_NODE unset, and the same previously documented visibility adjustment, independently reproduces **tested_state 24e27354e35eccc0cfa7d7e76357e673a6e38c23+08022c054eb41b157c87a42c3c5a708fd1a44826a8e24e05e9f21f7b4a7cd5b0**. The sandbox cannot read the global ignore file and exposes the existing `.claude/settings.local.json`; only that extra path was excluded in memory, without opening it or changing ignores. The before/after gate identities match.

Child receipts and all five handoffs agree on **Python 1186, UI 1129, MCP 466, Electron 182**, and one matching current passing full record per handoff. Their history distinguishes attempt 2 before Mat's rulings, attempt 3 before the prior findings, and failed attempt 4, superseded by attempt 5. Historical failed attempt 1 remains recorded. Release notes/checklist carry the current installer's size/hash; they do not publish suite totals or claim a clean audit.

The authoritative audit is still **98/99**, exit **1**, with transcript.compile non-pass. The rule tolerates that specific blocked condition; it does not establish actual caption content. The last gate line still says **INCOMPLETE VERIFICATION**, and handoffs/release text preserve that limitation plainly. No full Transcript pass is inferred from wrapper exit 0.

### Durable reviewer evidence

```json
{"schema_version":"evidence.v1","check_id":"s44-r3-original-f1","command":"rtk proxy node C:/Temp/av-kit/s44-r2-ui-node.cjs","cwd":"P:/av-kit","scope":"current production page, original independent F1 reproduction","phase":"targeted","exit_code":0,"result":"pass","tested_state":"24e27354e35eccc0cfa7d7e76357e673a6e38c23+08022c054eb41b157c87a42c3c5a708fd1a44826a8e24e05e9f21f7b4a7cd5b0","output":"Delayed settings, changed setting and loaded control all preserve Software and POST gpu_preference software; choice preserved true true true.","fresh":true}
```

```json
{"schema_version":"evidence.v1","check_id":"s44-r3-draft-refetch","command":"rtk proxy node C:/Temp/av-kit/s44-r3-ui.cjs","cwd":"P:/av-kit","scope":"actual ConvertPage/hook/serializer, controlled settings fetch/refetch, real Add body and command snapshot","phase":"targeted","exit_code":1,"result":"fail","tested_state":"same independently matched attempt-5 tree","output":"Eleven cases pass. No-draft control: displayed software, cachedSaved nvidia, outputDir C:/probe, POST and snapshot include gpu_preference software. Dirty-output case: displayed software, cachedSaved nvidia, outputDir C:/edited-output, POST and snapshot both {paths:[C:/probe.mp4],kind:compress,preset:balanced}, gpu_preference absent; ok false. Error: probe failed explicit Software with dirty output then saved Nvidia refetch.","fresh":true}
```

```json
{"schema_version":"evidence.v1","check_id":"s44-r3-ui-tests","command":"rtk proxy npx vitest run tests/unit/convert-page.behavior.test.ts tests/unit/ready-probe-guard.test.ts","cwd":"P:/av-kit/ui","scope":"submitted affected renderer/main tests","phase":"targeted","exit_code":0,"result":"pass","tested_state":"same independently matched attempt-5 tree","output":"Test Files 2 passed (2); Tests 62 passed (62), 11.32s. These tests omit the dirty-settings baseline case reproduced separately.","fresh":true}
```

```json
{"schema_version":"evidence.v1","check_id":"s44-r3-electron-attempt","command":"rtk proxy npm --prefix ui run test:e2e -- tests/e2e/backend-output-after-close.test.ts (ELECTRON_RUN_AS_NODE unset)","cwd":"P:/av-kit","scope":"fresh reviewer AC-108.7 attempt","phase":"targeted","exit_code":1,"result":"fail","tested_state":"same independently matched attempt-5 tree","output":"electronApplication.firstWindow: Target page, context or browser has been closed at backend-output-after-close.test.ts:18. No handler assertion reached; no fresh reviewer runtime pass claimed.","fresh":true}
```

```json
{"schema_version":"evidence.v1","check_id":"s44-r3-build-binding","command":"rtk proxy .venv/Scripts/python.exe -B C:/Temp/av-kit/s44-review-probes.py identity","cwd":"P:/av-kit","scope":"read-only build input reconstruction, installer and packaged external hashes","phase":"targeted","exit_code":0,"result":"pass","tested_state":"build_inputs 19e2e519beffd64d754428fea9f1c04cc889bf13e38f82576b678a441db57c0e","output":"build_inputs matches True; installer 340347542 B, aabc4ae145e7f26f976e11263fd85936027473fe99b361390c30eb0fcbff1b50; packaged FFmpeg hashes match; packaged Windows runtime hashes match 48.","fresh":true}
```

```json
{"schema_version":"evidence.v1","check_id":"s44-r3-d6-state","command":"rtk proxy .venv/Scripts/python.exe -B C:/Temp/av-kit/s44-r3-identity.py","cwd":"P:/av-kit","scope":"current D6 state, sole documented visibility adjustment, unset VIRTUAL_ENV/ELECTRON_RUN_AS_NODE","phase":"targeted","exit_code":0,"result":"pass","tested_state":"24e27354e35eccc0cfa7d7e76357e673a6e38c23+08022c054eb41b157c87a42c3c5a708fd1a44826a8e24e05e9f21f7b4a7cd5b0","output":"Only .claude/settings.local.json excluded in memory without reading it. Python 3.12.12, Node v26.13.0, Electron 42.11.18, Playwright 1.64.1; matches gate attempt 5 True.","fresh":true}
```

### Verdict and boundaries

**changes_required**, report round **3**, intent achieved **partial**, **one open Medium blocking behavior finding (F1)**. All six questions were reached. F2, the crash fix, D-208's disclosed limit, attempt-4 uncertainty, the rebuilds and records are accepted. F1 is not closed by the passing original reproductions or by Add/snapshot agreement: both can use the same stale draft and omit the explicit choice.

The honest AC-112 blocker must return to Mat under D-210 when the ledger refuses it. No commit, tag, GitHub release, upload, README installer-note change, repository-description change or worktree removal is authorized here. H2 remains the coordinator's post-review work. This report neither patches the finding nor claims session DONE.

## Recheck (2026-11-04)

**Workflow:** `/execution-critical-review`, multi-MEU execution, limited to the D-211/D-212 fix and its rebuilt artifact/evidence. **Reviewer:** Codex, `avkit_independent_reviewer` (OpenAI), independent of Claude Code (Anthropic). **Verdict:** `approved`. **Intent achieved:** `yes`. **Open findings:** 0.

**Intent anchor:** Session 44 prepares release candidate 1 of av-kit: MIT licence, the two first-run bug fixes (MEU-108, MEU-109), RC packaging and a real installer with packaged checks (MEU-110), release notes, a publish checklist and the D-101 brief, stopping before every outward step.

That registered anchor predates MEU-111/112, Mat's D-101 ruling and the later outward-step authorization. This recheck accepts the previously reviewed work and judges only the remaining fix, its effects on the two settings forms, the nine tests and sixth-build binding. Outward authorization is outside this verdict. **Report round 4; ledger round 2 of 6:** neither refused verdict consumed a ledger round. No ledger mutation was performed by this reviewer.

### Findings

| # | Severity | Blocking | Kind | Finding | File:Line | Recommendation | Status |
|---|----------|----------|------|---------|-----------|----------------|--------|

No new findings. No Critical, High or Medium defect was established in the reviewed change.

### Prior findings

| Finding | Recheck result | Evidence |
|---------|----------------|----------|
| F1 | fixed | The draft contains only edited fields; the current baseline supplies every untouched field (`useConverterSettings.ts:63-71`). My rerun of `s44-r3-ui.cjs` exits 0. With saved Software, an explicit Software pick, an open Output folder edit and a refetch changing saved GPU to Nvidia, the dropdown stays Software and both Add and the snapshot include `gpu_preference: software`. Additional actual-page cases prove the Skip existing path and untouched dropdowns too. |

### Q1 — F1 closure

**Accepted.** D-212 closes the mechanism despite differing from the earlier recommendation's shape. Convert never patches `gpu_preference`: its only settings patches are Output folder and Skip existing (`ConvertPage.tsx:807`, `:815`, `:826`). Consequently `converter.form.gpu_preference` now follows the saved query for this page, including while another settings field is dirty. Its uses at `:196` and `:727` are consistent with that contract.

I ran the original independent script myself. All **12 emitted cases** report `ok: true`; its old final summary still says 10. The formerly failing dirty-output case now preserves the edit and sends Software in both bodies. A scratch extension adds three actual-page cases: explicit Software with dirty Skip existing, and an untouched encoder with dirty Output folder or Skip existing. All **15 cases** pass; each compares the complete Add body with the command snapshot. Explicit Software stays displayed and is sent over saved Nvidia. An untouched dropdown displays Nvidia and both bodies omit an override. No Electron launch is needed for this renderer regression, and none was attempted.

### Q2 — Partial draft on both pages

**Accepted.** `useConverterSettings.ts:63-71` merges the baseline with the edited properties without mutating either. Refetch updates untouched fields; it cannot replace an explicitly edited property. Save validates the merged form and sends it (`:75-83`), then clears the draft only after a successful PUT and invalidates the shared query. A rejected PUT leaves the draft intact. The change therefore prevents the frozen-encoder write and the before-load defaults capture as well as fixing F1.

The real Settings page owns its own hook instance (`SettingsPage.tsx:317`) and patches the individual output, preset, skip and GPU fields (`:874-915`). Its explicit GPU/preset edits remain authoritative; other fields follow refetch. The submitted Settings-page test exercises the real page and confirms that its output edit survives while untouched Skip existing updates.

My additional probe imports the production hook, uses a real QueryClient and controlled HTTP responses, and asserts:

- Output edit survives refetch; Save sends that output with the new saved Nvidia and Skip existing values, and becomes clean.
- Editing Skip existing and returning it to the saved value makes `isDirty` false. Dirty state compares effective values, not merely the presence of a draft.
- Explicit GPU and preset edits survive another refetch; a rejected Save keeps them and remains dirty; retry sends those choices with the latest untouched output.
- Unmount/remount drops the unsaved local draft and restores the saved values, clean. The hook has no separate reset/discard operation whose behavior was changed here.

The new before-load page test also verifies the saved Software value arrives without replacing the output edit. No newly introduced path losing an edit or writing an unchosen frozen value was demonstrated. The existing full-PUT concurrency behavior during an in-flight Save was not redesigned or claimed fixed.

The Capture sibling still has `draft ?? baseline` (`useCaptureSettings.ts:76-85`). Its separately filed `SETTINGS-DRAFT-STALE-BASELINE` is code-inspected and unreproduced, as disclosed; this narrow correction does not claim to fix it.

### Q3 — AC-112.9 test rigor

**Accepted; Strong for the nine added tests.** `convert-page.behavior.test.ts:443-531` drives the actual pages and hook with real DOM events and controlled settings fetch/refetch. Tests assert the explicit GPU in Add and snapshot, untouched dropdown value and absent override, the exact relevant Save fields, before-load behavior and Settings-page preservation. The refetch helper waits for query notifications; tests do not merely inspect a cache that never reaches the page.

The kept Red contains **7 assertion failures, 2 passes, 53 excluded by the AC-112.9 name filter**. Failures show missing `gpu_preference: software` on both submission paths and dirty Skip existing, stale dropdown Software instead of Nvidia, stale Save Software instead of Nvidia, default Auto instead of loaded Software and unchanged checked Skip existing on Settings. These are behavioral failures, not setup errors. My fresh whole-file run passes **62/62**, including all nine additions, with no test-name filter.

The two guards at `:519` and `:526` are meaningful: one requires an explicit pick equal to the unchanged saved setting to remain omitted even with another dirty field; the other requires the user's output edit to survive refetch. They would reject an always-send override workaround or a fix that discarded the draft. Passing before and after is the intended preservation contract. The snapshot-only test isolates the GPU comparison; my page probe additionally proves complete snapshot/Add agreement with staged input.

### Q4 — Sixth build, gate attempt 6 and records

**Accepted.** On `main`, HEAD is still `24e27354e35eccc0cfa7d7e76357e673a6e38c23`. Independent read-only blob reconstruction matches **build_inputs `08ade695aadca286cd671168389227671ec1b163d81132344d38269ab2cde573`**. Rehashing the actual installer yields **340,348,020 bytes**, SHA-256 **`beabc50990e10c30afe8895170fd7fa3deedf622b182b5d343cc5f3aa09768a7`**. The public and local JSON records are equal; release notes and publish checklist carry that same size/hash. Packaged FFmpeg hashes and all **48** recorded runtime DLL hashes also match.

The main entry and both affected renderer bundles extracted in memory from packaged `app.asar` equal the gate-built `ui/out` files byte for byte:

| Packaged entry | SHA-256 |
|---|---|
| `out/main/index.js` | `9ca29d78071b8608d32dce8b231578fd051a5e1dbab216e21c513734c9f437da` |
| `out/renderer/assets/ConvertPage-DJaKNBBN.js` | `386f53e19ea6d00964281be856578e321f6f71e2d9042f1ecae384279a486d4b` |
| `out/renderer/assets/index-uqFWpwAr.js` | `512616b9fa774726f93e3e6fbc894273f9dcadf978f1d68e28ceb59e6751a13c` |

Row 10-13 receipts exit 0 and precede H1-2 attempt 6. The build log reports that installer/input identity. Saved unpacked and installed smokes pass, including default `hevc_nvenc` and explicit Software `libx265`; the installed app reports packaged mode, no errors and successful closure. The roundtrip records no new leftovers or lost entries. These are inspected coordinator runtime receipts, not new reviewer install/GUI runs.

The requested `uv run python .../identity.py`, with both named variables unset, exits **2** because the sandbox cannot open the uv cache's `sdists-v9/.git`. Using the same virtualenv Python and the same documented prior-round visibility adjustment reproduces **tested_state `24e27354e35eccc0cfa7d7e76357e673a6e38c23+025862f4f8e1a5c5b6d9023835d17014eabdac94e0785551cb7cc778a4bbd382`**, matching both gate identities. Only the sandbox-visible `.claude/settings.local.json` path is excluded in memory; its contents were not opened and no ignore file was edited.

Child receipts, the attempt-6 gate log and every one of the **five** handoffs agree on **Python 1186, UI 1138 (108 files), MCP 466 (34 files), Electron 182**. Each handoff has exactly one current passing full-gate evidence record with that tested state, build input and limitation. Prior attempts remain explicitly superseded. Release materials retain the installer numbers and do not claim a clean audit.

The audit itself remains **98/99, exit 1**; its specific tolerated Transcript failure does not become a runtime pass. The gate's actual last line is:

> session-gate: INCOMPLETE VERIFICATION: every other step exits 0, but the authoritative audit stays non-pass. Transcript is not verified end to end while YouTube blocks captions (YOUTUBE-CAPTIONS-IP-BLOCK).

This review generated **zero YouTube traffic** and did not rerun the gate, packaging, installation or audit.

### Checklist results and durable reviewer evidence

| Check | Result | Observation | Limit |
|---|---|---|---|
| Q1 / IR-1, IR-4: F1 and dropdown/submission agreement | pass | Original script exit 0; expanded actual-page probe 15/15 | Controlled renderer HTTP responses, not an installed-window run |
| Q2 / IR-2, IR-3, IR-6: form preservation and Save | pass | Production-hook assertions and actual Settings-page test pass | No redesign of concurrent in-flight full PUTs |
| Q3 / IR-5, IR-7: regression strength | pass | Seven decisive kept Red assertions; fresh whole file 62/62; both guards preserve behavior | Nine new cases audited; previously accepted tests not reopened |
| Q4: installer/current-state/full-gate binding | pass | Installer/build inputs, packaged bundles, five handoffs and child totals match | Coordinator runtime receipts inspected; identity uses disclosed sandbox fallback |
| Unchanged accepted work, new live Electron/audit runs and outward steps | n/a | Outside D-211's narrow recheck | No fresh 99/99 Transcript claim; H2 belongs to the coordinator |

```json
{"schema_version":"evidence.v1","check_id":"s44-r4-original-f1","command":"rtk proxy node C:/Temp/av-kit/s44-r3-ui.cjs","cwd":"P:/av-kit","scope":"production ConvertPage, settings hook, Add body and command snapshot; original reviewer reproduction","phase":"targeted","exit_code":0,"result":"pass","tested_state":"24e27354e35eccc0cfa7d7e76357e673a6e38c23+025862f4f8e1a5c5b6d9023835d17014eabdac94e0785551cb7cc778a4bbd382","output":"12 emitted cases all ok true. Formerly failing dirty-output case: display software, cachedSaved nvidia, outputDir C:/edited-output; snapshot and POST both include gpu_preference software.","fresh":true}
```

```json
{"schema_version":"evidence.v1","check_id":"s44-r4-extra-page-cases","command":"rtk proxy node C:/Temp/av-kit/s44-r4-ui-extra.cjs","cwd":"P:/av-kit","scope":"original actual-page probe plus dirty-Skip explicit choice and dirty-Output/Skip untouched dropdowns","phase":"targeted","exit_code":0,"result":"pass","tested_state":"24e27354e35eccc0cfa7d7e76357e673a6e38c23+025862f4f8e1a5c5b6d9023835d17014eabdac94e0785551cb7cc778a4bbd382","output":"15 actual-page cases pass; snapshot equals Add in every case. Dirty Skip plus explicit Software over refetched Nvidia sends software. Untouched dirty Output/Skip show nvidia and omit gpu_preference from both bodies.","fresh":true}
```

```json
{"schema_version":"evidence.v1","check_id":"s44-r4-hook-contract","command":"rtk proxy node C:/Temp/av-kit/s44-r4-hook.cjs","cwd":"P:/av-kit","scope":"production useConverterSettings, real QueryClient, controlled HTTP; Save/refetch/revert/failure/remount","phase":"targeted","exit_code":0,"result":"pass","tested_state":"24e27354e35eccc0cfa7d7e76357e673a6e38c23+025862f4f8e1a5c5b6d9023835d17014eabdac94e0785551cb7cc778a4bbd382","output":"Latest untouched values reach Save; output edit survives refetch; success becomes clean; edit back to saved is clean; explicit GPU/preset survive refetch; failed Save retains draft; retry sends choices with latest untouched output; remount drops unsaved draft. All assertions passed.","fresh":true}
```

```json
{"schema_version":"evidence.v1","check_id":"s44-r4-unit-tests","command":"rtk proxy npx vitest run tests/unit/convert-page.behavior.test.ts","cwd":"P:/av-kit/ui","scope":"whole affected unit test file including all nine AC-112.9 cases","phase":"targeted","exit_code":0,"result":"pass","tested_state":"24e27354e35eccc0cfa7d7e76357e673a6e38c23+025862f4f8e1a5c5b6d9023835d17014eabdac94e0785551cb7cc778a4bbd382","output":"Test Files 1 passed (1); Tests 62 passed (62); duration 16.43s.","fresh":true}
```

```json
{"schema_version":"evidence.v1","check_id":"s44-r4-build-binding","command":"rtk proxy .venv/Scripts/python.exe -B C:/Temp/av-kit/s44-review-probes.py identity","cwd":"P:/av-kit","scope":"read-only source build identity, actual installer and packaged external hashes","phase":"targeted","exit_code":0,"result":"pass","tested_state":"build_inputs 08ade695aadca286cd671168389227671ec1b163d81132344d38269ab2cde573","output":"build_inputs matches True; installer 340348020 bytes, SHA256 beabc50990e10c30afe8895170fd7fa3deedf622b182b5d343cc5f3aa09768a7; packaged FFmpeg matches; packaged runtime hashes match 48.","fresh":true}
```

```json
{"schema_version":"evidence.v1","check_id":"s44-r4-packaged-renderer","command":"rtk proxy node C:/Temp/av-kit/s44-r4-asar.cjs","cwd":"P:/av-kit","scope":"in-memory extraction of packaged main, ConvertPage and shared renderer bundles versus gate-built ui/out","phase":"targeted","exit_code":0,"result":"pass","tested_state":"build_inputs 08ade695aadca286cd671168389227671ec1b163d81132344d38269ab2cde573","output":"All three packaged entries equal ui/out; main 9ca29d78071b8608d32dce8b231578fd051a5e1dbab216e21c513734c9f437da; ConvertPage 386f53e19ea6d00964281be856578e321f6f71e2d9042f1ecae384279a486d4b; shared renderer 512616b9fa774726f93e3e6fbc894273f9dcadf978f1d68e28ceb59e6751a13c.","fresh":true}
```

```json
{"schema_version":"evidence.v1","check_id":"s44-r4-d6-state","command":"rtk proxy .venv/Scripts/python.exe -B C:/Temp/av-kit/s44-r4-identity.py","cwd":"P:/av-kit","scope":"independent current D6 identity with prior-round documented sandbox visibility adjustment; VIRTUAL_ENV and ELECTRON_RUN_AS_NODE unset","phase":"targeted","exit_code":0,"result":"pass","tested_state":"24e27354e35eccc0cfa7d7e76357e673a6e38c23+025862f4f8e1a5c5b6d9023835d17014eabdac94e0785551cb7cc778a4bbd382","output":"matches gate attempt 6 True. Python 3.12.12, Node v26.13.0, Electron 42.11.18, Playwright 1.64.1. Only .claude/settings.local.json excluded in memory without opening it; no repository mutation. uv invocation independently failed exit 2 on cache access, as disclosed.","fresh":true}
```

### Verdict and boundaries

**approved**, report round **4**, intent achieved **yes**, **zero findings**. F1 is fixed. All four requested questions were reached. Accepted: D-212's implementation, effects on both converter forms, AC-112.9's regression/preservation tests, the sixth build and attempt-6 records. Prior accepted work remains accepted without reopening it.

Not certified here: a new installed-window F1 run, a clean-machine install, a fresh live audit or successful end-to-end Transcript content. The saved runtime evidence and the already accepted limitations remain explicitly bounded above. Outward authorization was not assessed. Reflection, metrics, digest, recorded-verdict consumption and subsequent closeout remain the coordinator's work; this review does not claim session DONE or perform any outward step.
