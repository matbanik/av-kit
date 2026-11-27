---
date: "2026-11-27"
review_mode: "execution"
target_plan: "docs/execution/plans/2026-11-26-ytdlp-challenge-and-cookie-test/implementation-plan.md"
verdict: "approved"
findings_count: 0
template_version: "2.2"
requested_verbosity: "standard"
agent: "codex-independent-reviewer"
loop_id: "ycc-execution-2026-11-26-ytdlp-challenge-and-cookie-test"
round: 1
---

# Critical Review: 2026-11-26-ytdlp-challenge-and-cookie-test

> **Review Mode:** execution
> **Verdict:** approved

## Scope

**Target:** Session 104, MEU-168, MEU-169 and MEU-170: the delta from `baseline.sha` (`c0acc89e8b0eda65dd9dcaa2c008e03af35e33b4`) in the plan's Files Modified paths, against AC-168.1–AC-168.8, AC-169.1–AC-169.12 and AC-170.1–AC-170.5. Includes D-1600's change to Session 72's OpenAPI delta predicate. Read the correlated three MEU handoffs, source requests, residual homes, relevant code/tests/canon, gate and runtime receipts. Other sessions' work and process-paperwork compliance are excluded.

**Review Type:** independent execution review by Codex, class `avkit_independent_reviewer`; Claude Code, vendor Anthropic, authored the plan and implementation. **Checklist Applied:** Q1–Q7, applicable IR-1–IR-7 and AV-1–AV-6.

**tested_state:** `c0acc89e8b0eda65dd9dcaa2c008e03af35e33b4+c567b60166cced52337673de4040a0ec1fa705509e6dfdb24da13d8668083a10`.

The independently obtained value exactly matches the gate before/after values and H1-6b. There is no sandbox identity difference to waive. `identity.py` excludes `.claude/settings.local.json` by name before reading; that file and the user's global git ignore were not opened.

All reviewer writes stayed under `C:/Temp/av-kit`. Python used `PYTHONDONTWRITEBYTECODE=1`, TMP/TEMP under the assigned `exec-review/tmp`, and cleared `ELECTRON_RUN_AS_NODE`. The inaccessible default uv cache was replaced with a scratch `UV_CACHE_DIR`, with `UV_OFFLINE=true`. No sync, install, build, Electron/Playwright run, network request, app/backend launch, real app-data access or repository edit occurred. API tests used their in-process test clients and fakes.

## Intent Anchor

After this session, a signed-in download works again because yt-dlp can solve YouTube's current challenges; Test Cookies tells the user which of three things happened and why; and the SABR status can no longer be read as a verdict on the cookies.

Intent achieved: **yes**, within the approved proof and runtime boundaries. No evidence-backed High or Critical defect, or other substantive in-scope finding, survives review.

## Findings

| # | Severity | Blocking | Kind | Finding | File:Line | Recommendation | Status |
|---|---|---|---|---|---|---|---|

## Q1 — Goal

Accepted: all three goal clauses have corresponding implementation and decisive evidence.

| Goal clause | Acceptance criteria | Implementation and evidence |
|---|---|---|
| Restore extraction past the current YouTube challenges | AC-168.1–AC-168.7 | `uv.lock:3364`, infrastructure dependency floor, unchanged ejs 0.8.0; same player `b485e332`, before `challenge-errors`/0 formats, after `clean`/11 formats; packaged solver smoke and licence verification pass |
| Test Cookies says what happened and why | AC-169.1–AC-169.11 | Domain invariants; distinct jar-load and extraction steps; scrubbed reason; complete API/OpenAPI/MCP reply; four exact renderer texts, reset and busy behavior; backend, renderer and Electron assertions |
| SABR status cannot imply that cookies failed | AC-170.1–AC-170.4 | Detected timed results end with the scope clause; forced/cleared/unavailable texts retain their approved behavior; backend SABR sources and wire shapes equal row 0 |

AC-169.12 and AC-170.5's canon edits are present and agree with the delivered behavior. I accepted the approved cookie-free extraction proof; I did not infer that every account/video combination was tested, perform a signed-in download with real credentials, or treat a release as shipped.

## Q2 — Lock and proof

Accepted `YTDLP_LOCK`, `HOLD_OVERRIDE`, `PROOF_PAIR` and the conditional `VARIANT_FALLBACK`.

The actual diff changes only yt-dlp's package record, its infrastructure requirement and the matching hold option in `uv.lock`. yt-dlp-ejs remains 0.8.0. The root pyproject delta is exactly `exclude-newer-package = { yt-dlp = false }` under `[tool.uv]`; the infrastructure floor is exactly `yt-dlp>=2026.11.23`. The documented seven-day-hold exception fits the recorded refusal. Removal after 2026-11-30 remains the disclosed follow-up.

`proof-extract.py:165` builds one cookie-free extraction with the adapter's probe URL and cookie-client list. Its classifier prioritizes blocking conditions, then challenge needles, then a positive format count, and fails closed otherwise. Its emitter prints fixed fields rather than upstream log text. Independently rerunning `--selftest` passed 11 classifier and four emitter cases.

The before/after receipts show the same player and clients, Deno 2.9.8 and ejs 0.8.0: 2026.10.26/main produces challenge errors and zero formats; 2026.11.23/tv produces no challenge errors and 11 formats. Row 5c says `proved`. No fallback override is present or needed. Row 4 records 139 passing tests before the other product changes. Row 6 records the successful PyInstaller build, `PASS: smoke-runtime source=bundled version=2.9.8 solver=True`, the required yt-dlp/ejs licence titles, and 64 passing licence tests. These establish AC-168.7's packaging contract; I did not rebuild or repeat the network extraction.

## Q3 — Cookie test backend

Accepted `COOKIE_TEST_OUTCOME`, `COOKIE_TEST_STEPS`, `COOKIE_TEST_REASON` and `COOKIE_TEST_WIRE`.

`domain/enums.py:281` closes the outcome set. `domain/download.py:431` enforces success/message/outcome consistency. `adapter.py:823` returns None-mode without building yt-dlp, labels missing files and construction/jar-load errors `unreadable`, assigns the jar through public `load_cookies` at `:860`, then switches to `check_failed` before the single extraction. A clean extraction returns `ok`. The caught exception classes cover the approved input matrix.

`adapter.py:310` obtains the first meaningful error line and drops a leading `ERROR:`. `services/download.py:640` applies `scrub_line` and the outcome-specific empty-message fallback before the result reaches the route. `routes/downloads.py:141` copies all three fields, `schemas/downloads.py:96` uses the same enum, the committed OpenAPI matches the code, and MCP passes the API JSON through unchanged while describing all outcomes. Input strictness and 422 behavior remain intact.

The browser probe receipt says `browser-probe: hits=[] pytest=0`; browser-mode fixtures do not read a real profile. The real-yt-dlp malformed-file test supplies its own fake content and prevents extraction/network access. My additional two malformed-Netscape probes found synthetic content in the raw parser error but **not after the service scrub**: `marker_after_service_scrub=False` for both. Thus that candidate response-leak finding was rejected. Upstream stderr can echo synthetic malformed input, consistent with the disclosed upstream-output limitation; this review used no real cookie source.

Probe-development disclosure: the initial scratch probe also tried a line that yt-dlp skips instead of rejecting. Its explicit extraction-denial stub raised, stopping that scratch run. The final two-case probe targets parser failures and passes; no repository test, expected value or product code was changed.

The independent backend/lock selection passed **22 tests**. The route's stale `{ok}` docstring is the disclosed D-1494 scope limit, not a missing wire field.

## Q4 — Renderer and SABR

Accepted `COOKIE_TEST_SHOWN`, `COOKIE_TEST_BUSY`, `SABR_CHECK_SCOPE` and `SABR_KEPT`.

`cookie-test-result.ts:19` supplies exactly the four plan texts and omits the colon when a failed reply has no reason. `DownloaderPage.tsx:407` clears the old result and advances a generation number. Mode, browser, profile and picked-file changes call it; starting a new test does too. The equality check at `:832` drops a late success reply after a setting change. A rejected request uses the existing page error banner and leaves no result line.

The button's `loading={cookieTesting}` at `:816` spans the pending request and settles in `finally`. The shared Button maps it to `disabled` and `aria-busy`; it is independent of the page's settings-persistence busy state, preserving AC-53.2. The result has `role="status"`, the required text classes and the same row as the button.

`sabr-panel.ts:26` adds the clause to the two detected, timed results. The approved other eight snapshots retain their texts. The SABR phrase set, extractor arguments, check/force/clear sources and four SABR OpenAPI paths are unchanged; the independent `kept` check passed.

The real Electron evidence is appropriately complementary to the seam-based unit/API tests. Red run `r20261127T130256Z-88f0034` on snapshot `88f00345` has exactly four new failures from the new spec, each an expectation failure, and the forced-status guard passes. Green run `r20261127T133531Z-b2f78f8` on snapshot `b2f78f82` has 256 expected tests, zero unexpected, with all five new cases and four AC-159 cases passing. Independent receipt checks confirmed both results. The recovery receipt is for collecting that same Green run, not a retry. The eight Advanced ids/order, status slot, tail and 16 px gap are asserted with the result visible. I accepted recorded Electron evidence bound by the gate; I did not launch Electron here.

## Q5 — D-1600 and AC-106.5

Accepted option A on its merits. It preserves the new cookie wire contract and the original capture regression protection. Option B discards AC-169.5/AC-169.6; option C leaves a known, resolvable cross-feature snapshot conflict as a failing gate.

`openapi-delta.py:58` pins the complete two cookie schemas, including required fields, enum values, nullability and descriptions. At `:166`, the pair must equal either both old schemas or both exact Session 104 schemas. Mixed pairs and further cookie-schema changes are refused. At `:184`, only those two schemas are restored before the existing comparison. The original capture-addition checks and remaining whole-document comparison are preserved. The pre-existing release-version exception remains unchanged.

The two added selftest cases prove acceptance of the exact pair and refusal of an extra enum member. Independently, all 11 selftest cases passed, the current document passed, and four further mutations were refused: mixed old/new cookie schemas, optional outcome, unrelated route-description drift, and a changed capture text type. The independent `-k ac_106_5` selection passed 11 tests. No new route/capture exemption or blanket ignore was introduced.

The rc4 task's row 7 is a fitting normalization precedent; this exemption is stricter because its replacement schemas are exact. The M-7 conflict, reliance on Mat's explicit hand-over, post-plan-review scope growth and later baseline-copy timing are honestly disclosed. The old script's baseline is the unchanged HEAD blob. I did not treat this as ordinary HDP authority overriding M-7; Mat's supplied explicit direction and this independent review of the actual changed predicate are the basis for acceptance.

## Q6 — Gate and pins

Accepted gate run 3 as the fresh gate of record. `session-gate.ps1:39` registers identity, static checks, OpenAPI, full Python/UI/MCP tests, UI build, SSOT renders, snapshot binding, recorded remote E2E and final identity in the declared order. Its first-failure behavior preserves the earlier failed runs. Run 3 ends `session-gate: all steps exit 0`; every registered step reports exit 0.

| Gate evidence | Observed result |
|---|---|
| Python | 3358 passed, 37 warnings; no deselection |
| UI | 152 files, 1684 tests passed |
| MCP | 40 files, 557 tests passed |
| Build and renders | UI build and both SSOT checks pass |
| Remote E2E | Snapshot bound; 256 tests; required new cases and AC-159 guards pass |
| Identity | Gate before = gate after = independently derived current state |

The independent `pins-unchanged`, `red-unchanged`, `test-ids`, `canon`, `register` and `no-deselect` checks all passed. The diffs move only the six approved existing assertions plus their named fakes/setup; unrelated existing expectations remain. `test-ids.ts` is byte-for-byte the row-0 file plus the two-line CRLF block. AC-51.6, AC-81.13 and AC-159.3–AC-159.5 remain guarded; AC-138.8 changes only by the scope clause. I did not mistake this review's deliberately targeted pytest selections for deselections in the full gate.

## Q7 — Safety and fidelity

Accepted the scoped delta and correspondence between the handoffs, receipts and current state. Independent line-ending checking reports `46 scope path(s), 0 problem(s)`, including preservation of touched mixed-ending lines. The tracked modified paths all belong to scope or the recorded row-0 dirty set. Current branch is `main`, HEAD is the baseline, the index is empty and there are zero stash entries. Recent reflog entries show earlier sessions' commits, with no Session 104 ref movement; the deliberate snapshot commit objects move no branch/ref. These observations support the disclosed uncommitted state, rather than proving every historical filesystem operation.

There is one disclosed write outside the repository/temp scope: the environment-only mini-air SSH HostName correction. I accepted that disclosure and did not inspect forbidden SSH/fleet paths. Other sessions' changes were not attributed to this implementation.

The bounded safety scan found **no actual home path in the 46 scoped repository files**. Raw local receipts do contain home paths: `ycc-row6-package.txt:8` and nearby lines identify the Python installation under `<HOME>`; `ycc-row7-red.txt:18` shows the intended Red failure before home scrubbing worked. The generated `ycc-licences.txt` also contains upstream copyright/contact email strings. No such address is reproduced here; no non-noreply email candidate was found in scoped repository files or other session text receipts. These are local diagnostic/licence contents, not demonstrated product-response leakage, and are disclosed rather than promoted to product findings. No real-cookie content was observed or sought. The synthetic-content and boundary checks support that conclusion; arbitrary historical source-content absence cannot be proven without reading sources that this review correctly never opened.

The handoffs' passing counts, proof verdict, run ids and state match the inspected records. H2 reflection/metrics/commit-draft work remains with the coordinator after this review; approval here certifies the reviewed implementation, not that those later rows have run.

## Checklist Results

All manual observations below were made by `codex-independent-reviewer`. `P` means `docs/execution/plans/2026-11-26-ytdlp-challenge-and-cookie-test`; `R` means `C:/Temp/av-kit/2026-11-26-ytdlp-challenge-and-cookie-test`. Python commands below ran through `rtk proxy uv run --no-sync`, with the environment described in Scope. Each command's exit was captured before reading its completed receipt.

| Check | Result | Command or observed procedure | Exit | Decisive evidence |
|---|---|---|---|---|
| Identity | pass | `uv run --no-sync python P/identity.py --state-only` | 0 | Exact gate/current equality to the tested_state above |
| Targeted backend and lock behavior | pass | `uv run --no-sync pytest -q --tb=short -p no:cacheprovider tests/unit/test_ytdlp_lock.py tests/unit/test_domain.py tests/unit/test_services.py tests/integration/test_youtube_adapter.py tests/e2e/test_api_downloads.py -k "ac_168 or ac_169 or cookie"` | 0 | 22 passed, 220 deselected |
| Capture OpenAPI guard | pass | `uv run --no-sync pytest -q --tb=short -p no:cacheprovider tests/e2e/test_api_capture_shapes.py -k ac_106_5` | 0 | 11 passed, 2 deselected |
| OpenAPI parity | pass | `uv run --no-sync python tools/export_openapi.py --check openapi.committed.json` | 0 | Empty output, preserved exit 0 |
| D-1600 selftest/current | pass | `uv run --no-sync python docs/execution/plans/2026-11-14-capture-shapes-steps/openapi-delta.py --selftest`, then without arguments | 0 each | 11 cases, 0 wrong; current `openapi-delta: pass` |
| D-1600 independent negative cases | pass | `uv run --no-sync python R/exec-review/probe_delta.py` | 0 | Current accepted; four independent mutations refused |
| Cookie reason boundary | pass | `uv run --no-sync python R/exec-review/probe_cookie_reason.py` | 0 | Two synthetic parser failures; marker absent after service scrub |
| Proof classifier | pass | `uv run --no-sync python P/proof-extract.py --selftest` | 0 | 11 classify cases, 4 emit cases, 0 failures |
| Preservation and runtime records | pass | `uv run --no-sync python P/row-check.py CHECK` for `kept`, `openapi`, `test-ids`, `pins-unchanged`, `red-unchanged`, `e2e-red`, `e2e-result`, `canon`, `no-deselect`, `register` | 0 each | Each reports 0 problems; Red new 4; Green 256/AC-159 4 |
| Line endings | pass | `uv run --no-sync python P/eol-check.py` | 0 | 46 scope paths, 0 problems |
| Fresh full-gate acceptance | pass | Manually compare gate source, all-step receipt, decisive suite outputs and before/after/current identities | null | 3358 Python, 1684 UI, 557 MCP; all gate steps exit 0; unchanged inputs |
| Safety inspection/disclosure | pass | `uv run --no-sync python R/exec-review/probe_safety.py` plus scoped diff/receipt inspection | 0 | Baseline HEAD/main, no staged paths/stashes, no tracked out-of-scope delta; local raw path/licence occurrences disclosed in Q7 |
| New persistent write boundary | n/a | No new persistent write API/input surface | null | Existing request schema remains strict; this session extends the response |

### Assertion strength audit

Reviewed the changed/new assertions rather than assigning a fresh review to unchanged historical tests.

| Test file | Grade | Assessment |
|---|---|---|
| `tests/unit/test_ytdlp_lock.py` | Strong | Current lock/floor plus negative helper fixture; recorded adapter option dictionaries |
| `tests/unit/test_domain.py` | Strong | Closed enum/field shape and eight invalid result combinations |
| `tests/unit/test_services.py` | Strong | Exact scrubbed result, independent home absence, both fixed fallbacks |
| `tests/integration/test_youtube_adapter.py` | Strong | Step counts/outcomes, exception matrix, real malformed parser, network isolation and synthetic leak assertions |
| `tests/e2e/test_api_downloads.py` | Strong | Exact three-field replies for all outcomes; retained 422/error envelope |
| `tests/e2e/api_fakes.py` | Adequate | Collaborator supplies the extended response contract; route assertions test it |
| `mcp-server/tests/download-cookies-test.test.ts` | Strong | Registered description, exact passthrough/request, rejection before fetch |
| `ui/tests/unit/cookie-test-result.test.ts` | Strong | Exact four texts and missing-reason negatives |
| `ui/tests/unit/downloader-page.behavior.test.ts` | Strong | Real component, each result, all setting handlers, rejection, pending and duplicate-click behavior; late-reply guard additionally inspected in source |
| `ui/tests/unit/sabr-panel.test.ts` | Strong | Two changed snapshots and unchanged alternatives/local clock formatting |
| `ui/tests/e2e/downloader-cookie-test.test.ts` | Strong | Real Electron DOM, routed API, pending request, geometry/order, detected and forced statuses |
| `openapi-delta.py` selftests | Adequate | Exact allowed pair and an invalid pair; supplemented by independent capture/route/mixed-pair mutations |

AV-1–AV-6 pass for the scoped change: decisive assertion-based Red evidence precedes Green; final Red-file hashes are preserved; meaningful positive/negative assertions cover the changes; no added skip/xfail, assertion bypass or unfinished product placeholder was found. IR-1 uses the approved recorded network proof, real parser and real Electron evidence. IR-2–IR-7 are satisfied where applicable by the contract fakes, retained error mapping, complete AC coverage and unchanged strict request boundaries. No weak changed test justified a substantive finding.

```json
{"schema_version":"evidence.v1","check_id":"ycc-review-round1-targeted","command":"rtk proxy uv run --no-sync pytest -q --tb=short -p no:cacheprovider tests/unit/test_ytdlp_lock.py tests/unit/test_domain.py tests/unit/test_services.py tests/integration/test_youtube_adapter.py tests/e2e/test_api_downloads.py -k \"ac_168 or ac_169 or cookie\"","cwd":"P:/av-kit","scope":"Independent lock/domain/adapter/service/API cookie behavior","phase":"targeted","exit_code":0,"result":"pass","tested_state":"c0acc89e8b0eda65dd9dcaa2c008e03af35e33b4+c567b60166cced52337673de4040a0ec1fa705509e6dfdb24da13d8668083a10","output":"22 passed, 220 deselected in 3.34s"}
```

```json
{"schema_version":"evidence.v1","check_id":"ycc-review-round1-full-evidence","procedure":"Read session-gate.ps1, ycc-gate-h1.txt and decisive D6 suite receipts; compare the gate's before/after identity with independently run identity.py --state-only and current scoped diffs; inspect bound Electron Red/Green records.","observer":"codex-independent-reviewer","cwd":"P:/av-kit","scope":"Acceptance of the existing fresh full gate; the reviewer did not rerun the full gate","phase":"full","exit_code":null,"result":"pass","tested_state":"c0acc89e8b0eda65dd9dcaa2c008e03af35e33b4+c567b60166cced52337673de4040a0ec1fa705509e6dfdb24da13d8668083a10","output":"Gate run 3: session-gate: all steps exit 0. Python 3358 passed, UI 1684 passed, MCP 557 passed; UI build and renders pass. Remote run r20261127T133531Z-b2f78f8: 256 expected, 0 unexpected. Current identity exactly equals gate before and after."}
```

## Verdict

**approved**, with zero findings and `intent_achieved: yes`. The reviewed work delivers all three goal clauses and preserves the cited guards. D-1600 is accepted as a narrow, independently tested accommodation of the intended cookie response change.

Residual limits are the already disclosed upstream stderr/client-list items, future upstream/account variability, removal of the temporary hold exception and delivery through a future release. Local raw diagnostic paths and upstream licence contact addresses are disclosed in Q7; they are not copied into this report. No commit or push is authorized by this review.

Output compatibility note: the checked-in `review-verdict.schema.v2.json` forbids extra properties and defines no top-level `tested_state`. The returned JSON therefore records the exact requested value in its summary and identity checklist evidence; this report also labels it explicitly above. No schema or repository artifact was edited.
