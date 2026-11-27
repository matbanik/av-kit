---
date: "2026-11-26"
review_mode: "plan"
target_plan: "docs/execution/plans/2026-11-26-ytdlp-challenge-and-cookie-test/implementation-plan.md"
verdict: "approved"
findings_count: 0
template_version: "2.2"
requested_verbosity: "standard"
agent: "codex-independent-reviewer"
loop_id: "ycc-plan-2026-11-26-ytdlp-challenge-and-cookie-test"
round: 1
---

# Critical Review: 2026-11-26-ytdlp-challenge-and-cookie-test

> **Review Mode:** `plan`
> **Verdict:** `approved`

## Scope

Independent review of the working-tree implementation plan and task file for Session 104, MEU-168, MEU-169 and MEU-170. Author: Claude Code, Anthropic. Reviewer: Codex, a distinct vendor and not the author. Checklist: PR-1 through PR-9, with relevant source/state checks. The nine absent plan-local scripts are scheduled deliverables, not missing existing executables.

**Intent anchor:** After this session, a signed-in download works again because yt-dlp can solve YouTube's current challenges; Test Cookies tells the user which of three things happened and why; and the SABR status can no longer be read as a verdict on the cookies.

This verdict judges whether the plan is fit to put before Mat. It does not authorize execution or claim implementation success. The signed-in part of the goal remains subject to the expressly accepted cookie-free verification limit. D-1413 is outside this verdict, as instructed.

## Findings

| # | Severity | Blocking | Kind | Finding | File:Line | Recommendation | Status |
|---|----------|----------|------|---------|-----------|----------------|--------|

## Q1 — Goal and truthful completion

Accepted. AC-168.1–168.7 and rows 1–6 cover the dependency, the proof pair, conditional fallback and packaged runtime; AC-169.1–169.11 cover the outcome through the adapter, service, REST, MCP and UI; AC-170.1–170.4 cover the status wording and retained backend. The goal has a concrete delivery and verification path for each scoped clause.

I do not treat a clean cookie-free extraction as proof of a signed-in download. The plan says this expressly in User Review Required. Task row 5c keeps an unsuccessful pair `[B]`; row 19 excludes that issue from resolution and leaves MEU-168's status unchanged; H1-6 carries `INCOMPLETE VERIFICATION`; H2 raises only the MEUs row 19 raised. A green software gate certifies the scoped checks, not a missing live proof. These distinctions are substantive and sufficient under the supplied D-1462 scope limit.

## Q2 — Lock and hold override

Accepted. Current files actually hold yt-dlp 2026.10.26, ejs 0.8.0, an unfloored infrastructure dependency and the relative seven-day hold. The supplied PyPI receipt confirms 2026.11.23 requires ejs 0.8.0 in its `default` extra. Adding the floor without installing the whole extra respects D-640 and leaves `test_fetch_deno.py`'s metadata-based mismatch check useful. The new lock test has an assertion-based Red on today's files.

Rows 3.1–3.4 make the hold branch observable: retain the resolver failure, add the documented package-specific configuration only for the hold refusal, relock, then run `uv lock --check`. An unrelated failure is not authority to add it. The proposed lock comparison permits both the changed yt-dlp package and avkit-infra's requirement metadata, plus the matching options entry in the override branch. It does not permit another dependency upgrade.

No resolver command was run in this review. The branch is supported by the repository's dependency-update instructions, not an independently observed future resolution. Removal is already required by those instructions and carried in the handoff and next prompt; when MEU-168 resolves, row 19 also puts it in the issue's resolution text. I found no contract requiring a separate new issue. Apply the seven-day age to the actual upload time, rather than treating midnight on November 30 as the cutoff.

## Q3 — Proof and conditional fallback

Accepted at the design level. Row 1 uses `uv run --no-sync`, requires 2026.10.26 and precedes all product edits. The after-run requires 2026.11.23. The script takes `COOKIE_EXTRACTOR_ARGS` and `SABR_PROBE_URL` from the adapter, resolves the runtime as the app does, and omits both cookie options. Fixed diagnostic fields and canned-output selftests avoid publishing raw yt-dlp logs, cookie text, home paths or signed media URLs.

The strict pair rule does not turn clean/clean, a blocked run, or a still-failing run into proof. The single delayed retry applies to `blocked` only. The supplied tag source at lines 1885 and 2121 confirms `tv` is already the default and the argument overrides it; D-1461 therefore avoids a no-op fallback. Today's adapter has no `player_js_variant`, so the initial guard is achievable.

The script does not exist yet. Its literal challenge needles and classification precedence must be inspected when built: solver-failure warnings must remain failures even if extraction returns formats, and a generic download failure must not erase observed solver errors. The plan's requirement is absence of the challenge errors, not merely a zero process exit or absence of one stack-trace fragment. I found no instruction authorizing that weaker implementation. No live extraction or signed-in verification was performed here.

## Q4 — Backend outcomes, lazy loading and scrubbing

Accepted. Installed `YoutubeDL.py:4218–4227` exposes the lazy public `cookiejar` property. Constructing the object alone is insufficient, but explicitly accessing that property before `extract_info` implements COOKIE_TEST_STEPS. Its load failures can be caught at that boundary. S12 is an appropriate fallback if the upgraded dependency removes that separation; it is not a known unavoidable stop today.

The input matrix covers None, missing files, jar-load errors, extraction errors, success and an adapter-level unknown mode. Locked databases and unknown profiles can be represented by jar-loading stubs without touching a browser. The real malformed-file case can use JSON or an invalid Netscape header to force loading failure, with patched extraction and socket calls recorded and asserted absent. The type-only step preserves today's defaulted constructions and lets outcome assertions fail rather than imports.

An in-memory synthetic Netscape parse failure confirmed that the first exception line can contain a cookie value. The existing `scrub_line` removed that synthetic value; `_YtDlpLogger.error` also emitted only the scrubbed detail. A separate synthetic home-path probe replaced the home prefix with `~`. Thus the proposed service scrubbing plus today's logger closes the newly exposed result path without requiring a new scrubber. The test must retain its marker assertions. The explicitly disclosed yt-dlp direct-stderr skipped-entry behavior remains outside this work; I did not reclassify it as an in-scope omission.

## Q5 — Wire, readers and existing pins

Accepted. The required independent search across `tests/`, `ui/tests/` and `mcp-server/tests/` found the six moved assertions and the result-bearing fakes named by the plan. The other hits are permissive transport fixtures, request-body checks, ID-presence checks and the existing SABR/Advanced guards. I found no additional exact cookie-response or result-shape assertion requiring an unapproved weakening.

The new AC-15.7 expectations intentionally replace the obsolete absence-of-message assertion while retaining the 422 and no-cookie-material checks. CookieTestResult's appended defaulted field preserves current construction sites; fixtures that represent a successful actual probe must add `outcome: ok`. The renderer currently discards the response; MCP forwards API JSON. Adding the two response fields is compatible with those readers. The MCP action's nested description can change without changing the pinned top-level tool description.

The OpenAPI step first observes drift, regenerates, then restricts the semantic delta to CookieTestOut and its optional enum component. Session 106's later regeneration can accumulate its own schema changes; nothing here requires it to restore this session's baseline document.

## Q6 — Renderer, wording and SABR preservation

Accepted. `Button.tsx:66–67` implements `disabled={disabled || loading}` and `aria-busy={loading}`. The planned request-lifetime loading state must remain tied to this request. AC-169.9 includes clearing on mode, browser, profile and file changes, clearing on a new test, and a 422 banner with no result. Keep that invalidation effective if a setting changes while a reply is pending; an old reply must not reappear as the result of the newly displayed settings.

The success text says only that cookies were read and YouTube answered. It does not promise account authentication or cookie acceptance, which the planned probe does not establish. The failure texts distinguish load and extraction failures accurately. The result stays in the Test Cookies row; the existing Advanced ID order and layout are checked both unchanged and with a result shown. The existing measurement filters to the original eight IDs, so adding the result ID is not intrinsically incompatible.

**Nonblocking wording clarification:** implementation-plan.md:157 and AC-170.1 use a broad source/mode predicate, while the Pins table and task row 11 explicitly retain the other eight snapshots, including detected snapshots with missing/invalid times (`sabr-panel.test.ts:23,28,35,40`). Read “the two detected texts” as the two existing timestamped detected return branches, as Mat's scope and the explicit new assertions require. Say that explicitly in the shorthand contract; this is a trivially resolvable wording inconsistency, not a delivery blocker.

The clause itself is true even when a download wrote the detected status: it describes Check SABR. SABR_KEPT covers the named phrase set, extractor arguments, matcher, check and service actions, including their log statements; the additional schema/path and unchanged-test checks support the required backend preservation.

## Q7 — mini-air Electron Red and Green

Accepted. The existing snapshot helper uses a temporary index and `commit-tree`, checks refs/index/HEAD before and after, and verifies the exact path delta and working-file blobs. It does not move a branch or normal index. The plan copies that implementation and schedules its selftest; this review did not execute it or create a commit.

The tool and run book agree on 22/23 as host refusals and 40 as new failed/flaky/skipped tests. The actual summary has `new`, `unexpected`, `exit` and, for a collected run, `commit`. Passed statuses and failure details are available in `host/report.json`, which both proposed result readers also inspect. The known-failure list is currently empty, so the Green requirement of zero unexpected tests is coherent.

The Red check requires exactly the four new failing titles, assertion failures, and the passing forced-status guard. This distinguishes intended Red from launch errors, timeouts or unrelated regressions. Existing Electron specs demonstrate context-level API interception and scratch app-data with the launch harness; the proposed seams need no YouTube or real cookies. Actual script behavior, test routing and Red/Green results remain execution evidence, not evidence claimed by this review.

## Q8 — Final gate, registers and ownership

Accepted. The described session gate includes static checks, the fresh full Python/UI/MCP suites, types/lint, OpenAPI drift, UI build, state renders, line endings, home-path checks, immutable-test checks and binding of the final mini-air snapshot. Full pytest has no named deselection. Only the separate proof script reaches YouTube. Canon/register edits after the first Green snapshot invalidate that snapshot, so H1-2's specified rebuild/reverification must use the resulting final state.

Issue resolution uses the copied register helper with an expected baseline hash; rendering uses `issue_triage.py`. MEU transitions and generated BUILD_PLAN/registry output use `meu_status.py`. The grouping change uses the narrowly specified canon helper. The grouping ownership lists show no additional collision beyond the disclosed OpenAPI, later Advanced-panel/06-gui work and shared closeout files. Serial execution preserves their order.

Byte measurements matched the checked file-ending declarations, including DownloaderPage.tsx's 761 CRLF/226 LF and its behavior test's 2096 CRLF/623 LF. All named script-copy sources exist. No product file is currently modified against HEAD; tracked dirty paths match the supplied triage/registration/build-plan scope.

## Checklist Results

| Check | Result | Procedure | Observer | Exit | Evidence |
|---|---|---|---|---|---|
| PR-1 Plan/task alignment | pass | Compare both complete files' ACs, contracts and row dependencies | codex-independent-reviewer | null | Same three MEUs, proof branches, backend-to-wire-to-renderer order and closeout conditions |
| PR-2 Not started | pass | Inspect task statuses, planned-script existence and tracked product diff | codex-independent-reviewer | null | Work rows are unchecked; all nine named local scripts absent as disclosed; no product delta |
| PR-3 Task completeness | pass | Inspect task table and exact Row steps | codex-independent-reviewer | null | Tasks have roles, deliverables, validation and status; scripts have creation rows |
| PR-4 Validation realism | pass | Trace AC producers through actual code and proposed checks | codex-independent-reviewer | null | Lazy jar split, reply forwarding, UI feedback, runtime smoke and remote reports support the design |
| PR-5 Sources | pass | Compare FIC and decisions with homes, source requests and supplied upstream receipts | codex-independent-reviewer | null | Release/ejs/default-variant facts confirmed from named receipts; no network research |
| PR-6 Review readiness | pass | Inspect Handoff Set, H1 and H2 dependencies | codex-independent-reviewer | null | Three handoffs precede independent review; approval precedes status advancement; round 1 has no correction census |
| PR-7 Scope discipline | pass | Compare exclusions with grouping, homes and supplied settled decisions | codex-independent-reviewer | null | No omitted required session deliverable; release/user-data/client-list exclusions honored |
| PR-8 Controls | pass | Trace negative cases, proof/status branches and actual reader/report interfaces | codex-independent-reviewer | null | No demonstrated material false pass; blocked proof does not raise MEU-168 |
| PR-9 Single statements | pass | Compare named contracts with repeated AC/task references | codex-independent-reviewer | null | Named contracts govern; timestamp shorthand has the nonblocking clarification recorded under Q6 |
| DR source/state checks | pass | Compare baseline claims, current code, tests and byte counts | codex-independent-reviewer | null | Version, missing feedback and SABR-cookie independence match current source |
| Product suite/build/live extraction execution | n/a | Deliberately not run in this read-only plan review | codex-independent-reviewer | null | No pytest, Vitest, npm, sync, lock, packaging, Electron, SSH or network request executed |

### Decisive command evidence

Commands below ran from `P:/av-kit` through `rtk proxy`, with completed all-stream receipts and preserved child exits. Python ran with bytecode writing disabled. No real cookie file, browser profile, secret file or prohibited configuration was opened. Temporary probe scripts and output are confined to `C:/Temp/av-kit`.

```json
{"schema_version":"evidence.v1","check_id":"ycc-plan-static","command":"rtk proxy .venv/Scripts/python.exe C:/Temp/av-kit/ycc-static.py","cwd":"P:/av-kit","scope":"plan scripts, dependency metadata, selected source byte counts","phase":"plan-review","exit_code":0,"result":"pass","tested_state":"working-tree plan at supplied HEAD c0acc89; exact selected source hashes embedded in static receipt; excludes .claude/settings.local.json","output":"yt-dlp=2026.10.26; yt-dlp-ejs=0.8.0; all 9 named local scripts absent and scheduled; all 11 checked copy sources exist; DownloaderPage.tsx 761 CRLF/226 LF; behavior test 2096 CRLF/623 LF","fresh":true}
```

```json
{"schema_version":"evidence.v1","check_id":"ycc-plan-upstream-receipts","command":"rtk proxy .venv/Scripts/python.exe C:/Temp/av-kit/ycc-research.py","cwd":"P:/av-kit","scope":"only named s104 planning receipts","phase":"plan-review","exit_code":0,"result":"pass","tested_state":"supplied 2026-11-26 upstream snapshots; no network","output":"2026.11.23 is not yanked; default extra requires yt-dlp-ejs==0.8.0; wheel uploaded 2026-11-23T23:50:00.052942Z; maintainer names stable 2026.11.23 as fixed; tagged _DEFAULT_PLAYER_JS_VARIANT='tv'; account-dependent failures and the downstream continuing failure are disclosed","fresh":true}
```

```json
{"schema_version":"evidence.v1","check_id":"ycc-plan-synthetic-scrub","command":"rtk proxy .venv/Scripts/python.exe C:/Temp/av-kit/ycc-probe.py","cwd":"P:/av-kit","scope":"in-memory invented cookie record, first_line/scrub_line and av-kit logger; no files or network as inputs","phase":"plan-review","exit_code":0,"result":"pass","tested_state":"installed yt-dlp 2026.10.26 and current scrubber/logger source","output":"Real Netscape parser exception contains synthetic marker in first line; scrubbed result is 'invalid Netscape format [REDACTED]'; home_path_removed=true; avkit_log_marker_removed=true","fresh":true}
```

```json
{"schema_version":"evidence.v1","check_id":"ycc-plan-pin-census","command":"rtk proxy rg -n 'CookieTestResult|cookies/test|cookies_test|cookie-test-btn|sabrResultText|checked 09:05:07|SABR inactive' tests ui/tests mcp-server/tests","cwd":"P:/av-kit","scope":"existing Python, renderer and MCP pins","phase":"plan-review","exit_code":0,"result":"pass","tested_state":"current working-tree tests inspected together with proposed Pins that move","output":"Exact shape/response/text pins are in test_domain.py, test_youtube_adapter.py, test_api_downloads.py, sabr-panel.test.ts and downloader-page.behavior.test.ts; result-bearing fakes and remaining permissive seam/ID/request-body readers inspected","fresh":true}
```

Other executed commands were bounded source reads, exact searches, and `git --no-optional-locks diff --name-only HEAD` (exit 0). One exploratory search named a nonexistent guessed host-script path and exited 2; the authoritative `tools/e2e_remote.py` and run book were then read directly. Early scratch probes encountered receipt-format/setup errors; the corrected probes above completed with exit 0. These are review-tool observations, not product failures.

## Verdict

`approved` — no evidence-backed High or Critical delivery finding. The plan is fit for Mat's execution decision. Clarify the timestamp predicate as noted under Q6; verify the proof classifier and pending-request invalidation when implementing the existing contracts. Those are not new acceptance criteria or execution authorization.

Residual limits: the proof, generated scripts, rebuilt backend and mini-air runs do not exist as execution evidence yet. A cookie-free pair cannot certify a signed-in download, and an incomplete pair must retain the explicitly planned incomplete status. Report saved to `C:/Temp/av-kit/ycc-plan-review-round-1.md`; the coordinator owns the canonical repository copy.
