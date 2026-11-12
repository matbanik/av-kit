---
date: "2026-11-12"
review_mode: "execution"
target_plan: "docs/execution/plans/2026-11-12-youtube-client-runtime/implementation-plan.md"
verdict: "approved"
findings_count: 0
template_version: "2.2"
requested_verbosity: "standard"
agent: "codex-independent-reviewer"
loop_id: "s66-execution-2026-11-12-youtube-client-runtime"
round: 1
---

# Critical Review: 2026-11-12-youtube-client-runtime

> **Review Mode:** execution. **Verdict:** approved. **Intent achieved:** yes. Zero findings.

## Intent Anchor

Session 66 lets yt-dlp choose its own YouTube clients, with one retry on today's cookie pin, and gives yt-dlp a JavaScript runtime and its challenge solver in dev and in the installed app. A download's first attempt sets no `player_client` in any cookie mode; a client-side failure retries once with `tv`, `web_safari`, `web`, and the Console shows each failed attempt. A video selector at a fixed height falls back to `/best`. The add-time extract uses the download's cookie and client options. Deno ships in the Windows installer and is found the way ffmpeg is (the setting, the bundled file, PATH); yt-dlp gets it through `js_runtimes`, the solver scripts ship in the backend, and Health names the runtime or says none was found and what that costs.

## Scope

Reviewed Session 66, MEU-140 and MEU-141, on `main` at `055377999828ea759315fcdd8d6c7b488110b67c`: the working-tree implementation, new files and tests, both execution handoffs, authoritative plan/task, scoped records, packaging inputs/outputs and supplied receipts. Applied `/execution-critical-review`, its Intent Anchor, Materiality Gate, Verdict Rule and IR-1 through IR-7. Author: Claude Code / Anthropic. Reviewer: Codex / OpenAI, independently.

All reviewer writes are under `C:/Temp/av-kit`. No repository file was edited. No test runner, session gate, network call, real yt-dlp instance, app/API launch, packaging command, process termination or Git mutation ran. All adapter probes patched `YoutubeDL` for the entire call. Forbidden sources and private probe files were not opened. The protected local settings file was excluded before identity enumeration could read it. The coordinator owns canonical report adoption, ledger recording and H2.

## Findings

| # | Severity | Blocking | Kind | Finding | File:Line | Recommendation | Status |
|---|----------|----------|------|---------|-----------|----------------|--------|

## Q1 — Client choice and retry

Accepted `ATTEMPT_OPTS`, `CLIENT_SIDE`, `RETRY_ONCE`, `ATTEMPT_LOG` and `SABR_ACROSS`. Independently drove 33 download cases across none/browser/file: format, reload, SABR-plus-format, both retry and refusal classes, age, unknown, and SABR-plus-bot/cookie/write. Attempt 1 omitted `extractor_args`; the single retry used the exact cookie pin and retained cookie options. Additional per-mode checks proved cancellation prevents attempt 2, a successful first attempt logs no attempt warning, and attempt 2 uses its own cause even after attempt 1 logged SABR. Add-time retries also passed with the queue stop flag set, consistent with D-656.

The implementation is at `adapter.py:606`, `:621`, `:648`, `:748` and `:797`. The real-stack Console tests at `tests/e2e/test_api_client_fallback.py:107` onward cover warning/final-error order and structured fields; D-655 deliberately retains only the event/detail in Console rows. Non-DownloadError propagation is preserved by the narrow catch and characterized by AC-140.4. No first-half goal sentence lacks implementation and substantive coverage. No behavior rejected.

## Q2 — Precedence and redaction

Accepted the two whole-text steps at `adapter.py:401`. Eighteen independent mixed-case/multiline cases placed every refusing needle after a format line, with and without a SABR log match; all refused retry. Both bot apostrophes are included. `sabracadabra` did not match; mixed-case `missing a url` did.

Six independent adapter-warning probes covered split synthetic cookie/link/home markers, a lone surrogate, controls and empty text. All retried once, produced UTF-8-safe detail, and retained no planted marker or link. `adapter.py:660` passes the classifier's unjoined first line through `scrub_line`; the real adapter → service → Console regressions at `tests/e2e/test_api_client_fallback.py:193` onward assert exact safe rows and absence from captured streams. No redaction defect found.

## Q3 — Selectors and add-time extraction

Accepted all height selectors and unchanged Best/Lowest/audio selectors (`adapter.py:151`, `:162`), including the download's actual `format` option. `_download_options` is shared by add and queued download (`services/download.py:265`, `:543`); it reads cookie settings per call. The coordinator forwards options only when supplied and distinguishes all four cookie fields (`services/extract.py:37`). Independent probes confirmed cache misses for each changed field and hits for identical options; the transcript key and keyword-free port call remain intact.

The missing-file API regression asserts the complete 422 body, zero jobs and zero yt-dlp constructions (`tests/e2e/test_api_client_fallback.py:310`). The caller receipt, current production callers and changed fake signatures agree; transcript fakes retain their original call contract. No caller or add-time contract gap found. The API test was inspected and its matching recorded run verified, not rerun here.

## Q4 — Runtime lookup and options

Accepted setting → bundle → PATH lookup and fresh setting reads (`js_runtime.py:46`, `:79`; `wiring.py:163`). Thirty-nine independent fallback cases covered missing/folder/empty/non-string/NUL/control/surrogate/long/relative-missing settings against bundle, PATH and neither. A real relative fixture file, a raising reader and a changing setting also behaved as specified, without value logging.

All builders, including both download/add attempts, no-options extract, listings, Check SABR and cookie test, passed independent checks with a runtime, no runtime and a raising source (`adapter.py:553`, `:571`). Installed yt-dlp 2026.10.26's `YoutubeDL.py:863` and `:885` validate `{runtime: {config}}` and read `config.get('path')`, confirming the supplied shape offline. No lookup/options defect found.

## Q5 — Health, Settings and MCP

Accepted all six Health fields, one five-second version subprocess, parsed-version-only output, bearer protection and live wiring. Independent timeout/OSError/garbage/empty-output probes kept `available=True` with `version=None`; successful output yielded only `2.9.8`. The route's unknown source serialized as null. API tests assert the six-field body and unauthorized response; UI tests exercise the real component and hook for found/missing copy, read-only Browse, cancellation, dependency invalidation and quality's non-invalidation.

MCP accepts `deno_path` and excludes it from output isolation. The exact OpenAPI comparison added only `JsRuntimeOut`, `DependenciesOut.js_runtime` and `SettingsPutIn.deno_path`, preserving paths and all other schemas. A fresh `export_openapi.py --check openapi.committed.json` passed. No wire/UI/schema defect found; no GUI or API process was launched by this reviewer.

## Q6 — Solver, bundle and installer

Accepted installed metadata's `yt-dlp-ejs==0.8.0` default-extra pin and the lock's solver-only addition. Independently hashed the archive, published sum, licence and extracted runtime; they match the pins and recorded values. Source/bundle copies of Deno and its licence hash identically. The backend contains both `yt_dlp_ejs/yt/solver/core.min.js` and `lib.min.js`. The spec collects the module and data; electron-builder filters archive/sum from the runtime resource; the frozen sibling calculation matches its layout.

Fetch validation refuses bad inputs before extraction; fresh-output archive/licence mismatch tests assert exit 3 and no executable. The smoke removes PATH entries holding Deno, uses fresh app data/home, checks bundled source/version/solver and stops its recorded subprocess. Its recorded Red and fresh Green results support AC-141.12. Notices and licence evidence include Deno and the solver without adding a GPL-class dependency.

Accepted the recorded 371,477,462-byte NSIS measurement, versus 340,362,828 bytes for rc.2. D-660 records the 243-file Nov 9 picker copy; the builder receipt records Deno in `C:/Temp/av-kit/s66/nsis/win-unpacked/resources/deno` and `exit_builder=0`. `ui/dist/win-unpacked` is the older picker source, not that output. No online fetch, picker rebuild, installer launch or packaged smoke was rerun here; these accepted checks are receipt-backed.

## Q7 — Pins, callers and test rigor

Accepted the moved exhaustive-selector/client pins, optional port parameter/default pins, exact transcript type/return/PlaylistInfo guards and audit input/output pins. D-658 adds only the unavailable runtime namespace to three dependency fakes; their assertions are unchanged. The current D-659 tests assert invalidation call order and do not depend on the removed unused counter. The dedicated test-id receipt confirms both prefix guards passed: 28 tests. Unchanged packaging and dependency-refresh guards remain in the matching full run.

Independent `red-check.py` calls with the exact task row requirements passed: row 2a, 12 required IDs; row 2b, 16 required IDs; zero problems. No missing AC, weak replacement assertion, skip or unimplemented contract found. AC-141.15 appropriately uses a real installer measurement. Existing tests modified only for signatures/fixtures retain their behavioral assertions.

| Test scope | IR-5 rating | Observation |
|---|---|---|
| `test_youtube_client_fallback.py` | Strong | Exact options, counts, error identities/causes, cancellation and SABR results |
| `test_extract_options.py` | Strong | Service/port values, both extract branches, each cookie cache field and legacy key |
| `test_api_client_fallback.py` | Strong | Real-stack Console/error/DB behavior with only yt-dlp scripted |
| `test_js_runtime.py` | Strong | Source order, unusable input matrix, no value logs, bounded probe argv and parsed output |
| `test_js_runtime_wiring.py` | Strong | Real wiring, settings update, builder options and complete Health values |
| `test_api_js_runtime.py` | Strong overall | Round trip, complete body and auth; field-existence helpers are Adequate and supplemented by behavioral assertions |
| `test_fetch_deno.py` | Strong | Spec/config values, smoke refusal matrix, offline child exits, binary bytes and licence refusal |
| `settings-runtime.test.ts` in UI/MCP; audit isolation tests | Strong | Real rendered component/hook behavior, accepted/rejected schema inputs and exact output-key exclusion |
| Modified existing Python tests/fakes and `test-ids.ts` | Retained strength | Only approved pins/signature/fixture additions; existing assertions and guarded prefix preserved |

## Q8 — Evidence freshness and records

Accepted the freshly recomputed state:

`055377999828ea759315fcdd8d6c7b488110b67c+4fd745a936fbc9857749819533559d04f37a8de662c832365be61a1232e08c30`

It equals the handoffs and both gate identities. `ELECTRON_RUN_AS_NODE` was unset. A process-only `core.excludesFile` pointing to a temp ignore file excluded the protected local settings path; existing harness Git configuration was preserved. The material evidence.v1 claims agree with the underlying receipts: Python 2309/37 warnings, UI 1293/121 files, MCP 525/36 files, Electron 24, package build, bundled-runtime smoke and licences all passed.

Pre-status comparisons confine MEU fields to 140/141, issue resolution fields to the two named issues, registry changes to the two rows, BUILD_PLAN to Total and grouping to row 66. Parsed status equals D-661's tool dump. All 43 files with pre-edit line-ending anchors retain their recorded style; no modified tracked file has mixed endings. Spec notes match the implementation. Fresh `meu_status.py render --check` passed.

The six safe live-probe records all report bundled Deno 2.9.8 and solver true; four downloads passed attempt 1, two membership refusals report `other`. They do not establish a live retry, and the handoffs explicitly say so. No private probe media/log was read. H2 remains pending by design. No stale/full-gate or concealed-deferral finding remains.

## Checklist Results

| Check | Result | Procedure / command | Exit | Evidence |
|---|---|---|---|---|
| IR-1 runtime evidence | pass | Codex compared real-stack tests, six safe live records and packaged smoke receipts against current code | null | Full gate and manual probes are evidenced; no fresh reviewer runtime launch claimed |
| IR-2 stub compliance | pass | Codex traced scripted outcomes and inspected changed collaborator fakes | null | Exact attempt options/counts and unchanged service fake behavior |
| IR-3 error mapping | pass | Codex inspected missing-file route test, adapter raises and API error mapping | null | Exact 422 body and no job/yt-dlp run; final attempt cause preserved |
| IR-4 generalization | pass | Codex inspected every builder/caller and ran independent source/error matrices | null | Shared attempt and runtime option builders cover all affected public calls |
| IR-5 test rigor | pass | Codex audited new tests and changed pin/fixture assertions; grades above | null | Strong behavioral coverage, supplemented adequate field-existence helpers |
| IR-6 boundaries | pass | Codex inspected schemas, invalid/unknown input tests, auth and runtime setting fallback | null | Strict existing boundaries preserved; unusable runtime settings fail through safely |
| IR-7 coverage/deferrals | pass | Codex mapped all 28 ACs, decisions, handoffs and recorded checks | null | No silent omission; accepted limits remain disclosed |
| Independent behavior probes | pass | `rtk proxy uv run --no-sync python -B C:/Temp/av-kit/s66-review-probe.py` | 0 | 33 download, 18 precedence, six adapter-redaction and 39 locator fallback cases, plus builder/cache/Health checks |
| Evidence and Red verification | pass | `rtk proxy uv run --no-sync python -B C:/Temp/av-kit/s66-review-evidence.py` | 0 | Both exact required-ID Red checks pass; hashes, OpenAPI delta, records, counts and 43 line-ending anchors verified |
| OpenAPI | pass | `rtk proxy uv run --no-sync python -B tools/export_openapi.py --check openapi.committed.json` | 0 | Empty output, no drift |
| MEU renders | pass | `rtk proxy uv run --no-sync python -B tools/meu_status.py render --check` | 0 | 142 MEUs, 12 phases; on-disk regions match |
| Reflection/metrics/commit/push | n/a | H2 follows this independent review | null | Explicitly outside this round |

All manual procedures above were observed by `codex-independent-reviewer`; null exits are manual observations, not command passes. Probe commands used `PYTHONDONTWRITEBYTECODE=1`, `UV_OFFLINE=1`, and temp/cache paths under `C:/Temp/av-kit/s66/exec-review-tmp`. Initial reviewer setup errors (uv cache access, cross-drive relative-path fixture, uppercase published checksum, Git normalization comparison and omitted OpenAPI check argument) were corrected in temp scripts/argv; the final checks above completed successfully. They were not product failures or substituted suite evidence.

```json
{"schema_version":"evidence.v1","check_id":"s66-review-r1-behavior","command":"rtk proxy uv run --no-sync python -B C:/Temp/av-kit/s66-review-probe.py","cwd":"P:/av-kit","scope":"Patched yt-dlp attempts; classification/redaction; cache; runtime lookup/options/version/wire","phase":"targeted","exit_code":0,"result":"pass","tested_state":"055377999828ea759315fcdd8d6c7b488110b67c+4fd745a936fbc9857749819533559d04f37a8de662c832365be61a1232e08c30","output":"PASS download matrix: 33 cases; PASS whole-text precedence: 18 cases; PASS adapter attempt warning redaction: six cases; PASS locator: 39 fallback cases; runtime options across all builders passed; yt-dlp 2026.10.26, solver 0.8.0; bundled Deno version 2.9.8; unknown runtime wire source null"}
```

```json
{"schema_version":"evidence.v1","check_id":"s66-review-r1-freshness","command":"rtk proxy uv run --no-sync python -B docs/execution/plans/2026-11-12-youtube-client-runtime/identity.py --state-only","cwd":"P:/av-kit","scope":"Current D6 identity with ELECTRON_RUN_AS_NODE unset and protected local settings excluded through a temporary process-only Git ignore file","phase":"static","exit_code":0,"result":"pass","tested_state":"055377999828ea759315fcdd8d6c7b488110b67c+4fd745a936fbc9857749819533559d04f37a8de662c832365be61a1232e08c30","output":"055377999828ea759315fcdd8d6c7b488110b67c+4fd745a936fbc9857749819533559d04f37a8de662c832365be61a1232e08c30; exact equality with handoff gate record and identity-before/after"}
```

```json
{"schema_version":"evidence.v1","check_id":"s66-review-r1-evidence","command":"rtk proxy uv run --no-sync python -B C:/Temp/av-kit/s66-review-evidence.py","cwd":"P:/av-kit","scope":"Required Red IDs, baseline OpenAPI comparison, Deno hashes, packaged solver files, record scope, line endings and full-gate receipt counts","phase":"static","exit_code":0,"result":"pass","tested_state":"055377999828ea759315fcdd8d6c7b488110b67c+4fd745a936fbc9857749819533559d04f37a8de662c832365be61a1232e08c30","output":"red-check: 1 receipt(s), 12 required test(s), 0 problem(s); red-check: 3 receipt(s), 16 required test(s), 0 problem(s); Deno archive/published sum/licence pins match; source and copied runtime SHA256 924397800533d3eb0ed0c889b20ad70e18b970d93acd8135bc043f425e528266; packaged solver core.min.js and lib.min.js present; status equals parsed tool dump; 43 pre-edit line-ending anchors preserved; counts Python 2309, UI 1293/121 files, MCP 525/36 files, Electron 24"}
```

## Verdict

`approved` — the delivered behavior achieves the registered intent within the approved scope. No evidence-backed High or Critical failure, or other actionable finding, was established. No execution correction is requested. The coordinator may validate/adopt this report and continue the authorized H2 sequence; this review neither performs nor judges commit/push.
