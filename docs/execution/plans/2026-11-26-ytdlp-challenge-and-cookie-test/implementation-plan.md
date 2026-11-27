---
project: "2026-11-26-ytdlp-challenge-and-cookie-test"
date: "2026-11-26"
source: "Mat's report of the Downloader's Advanced panel and his backend console, 2026-11-26 (USER_EXPLICIT), registered as YTDLP-CHALLENGE-SOLVE-FAILS (triage D-1407), DOWNLOADER-COOKIE-TEST-SILENT (D-1406) and SABR-CHECK-IGNORES-COOKIES (D-1408); homes in docs/build-plan/02-infrastructure.md §Residuals registered 2026-11-26"
grouping_source: ".agent/context/grouping/2026-11-26-ui-findings-and-auto-update-session-grouping.md"
meus: ["MEU-168", "MEU-169", "MEU-170"]
status: "draft"
template_version: "2.3"
---

# Implementation Plan: yt-dlp solves YouTube's challenges again, Test Cookies says what happened, and the SABR status says what its check covers

> **Project**: `2026-11-26-ytdlp-challenge-and-cookie-test` (Session 104)
> **Build Plan Section(s)**: 02 §Residuals registered 2026-11-26 (`docs/build-plan/02-infrastructure.md`): §yt-dlp challenge solver (anchor `ytdlp-challenge-solver-residual`, MEU-168, matrix 2.10), §Cookie test outcome (`cookie-test-outcome-residual`, MEU-169, matrix 2.11), §SABR check and cookies (`sabr-check-and-cookies-residual`, MEU-170, matrix 2.12). Parent canon: 02 §Cookie test, §yt-dlp JS runtime (residual), §SABR check result (residual), §yt-dlp log detail (residual); 04 §Downloads; 06 §Downloader.
> **Source request**: Mat, 2026-11-26: Test Cookies shows nothing; the backend console shows yt-dlp's challenge errors; and 'AlsoI picked firefox but I don't think it picked up the youtube cookies since it still detected sabr.'
> **Known issues**: `YTDLP-CHALLENGE-SOLVE-FAILS` (P1), `DOWNLOADER-COOKIE-TEST-SILENT` (P2), `SABR-CHECK-IGNORES-COOKIES` (P3).
> **Status**: `draft`. `plan_to_exec_gate: human`. The grouping's run parameters for this session are `decisions=hdp · commit_plan=false · exec_after_plan=false · commit_exec=false · push=never`: execution starts only on Mat's word, and nothing is committed or pushed by this plan.

---

## Goal

**Goal anchor:** After this session, a signed-in download works again because yt-dlp can solve YouTube's current challenges; Test Cookies tells the user which of three things happened and why; and the SABR status can no longer be read as a verdict on the cookies.

What the code and the upstream pages show today (read 2026-11-26):

1. **The lock holds a yt-dlp that cannot solve the current players.** `uv.lock:3361-3375` holds yt-dlp 2026.10.26 and yt-dlp-ejs 0.8.0; `packages/infrastructure/pyproject.toml:12-13` asks for `"yt-dlp"` (no floor) and `"yt-dlp-ejs==0.8.0"`. The installed `yt_dlp/extractor/youtube/_video.py:1884-1896` has `_DEFAULT_PLAYER_JS_VARIANT = 'main'`. Upstream issue 18123 is closed as fixed in stable 2026.11.23; pull request 18124 changed that default to `'tv'`.
   The root `pyproject.toml:12` holds `exclude-newer = "7 days"`, and 2026.11.23 was uploaded on 2026-11-23, so until 2026-11-30 the lock command refuses it unless the documented yt-dlp line is added (`docs/distribution/dependency-updates.md` §The 7-day hold; D-1468).
2. **Test Cookies drops its answer twice.** The route (`packages/api/src/avkit_api/routes/downloads.py:133-141`) returns `CookieTestOut(ok=result.ok)` and leaves out `error_message`; the renderer (`ui/src/renderer/src/features/downloader/DownloaderPage.tsx:796-813`) awaits the reply and discards it. The button has no `loading` and stays clickable while the test runs.
3. **A cookie that could not be read looks like a YouTube failure.** `YouTubeAdapter.test_cookies` (`packages/infrastructure/src/avkit_infra/youtube/adapter.py:812-850`) runs one `extract_info` and returns `ok=False` with the raw `str(exc)` for every failure. `CookieTestResult` (`packages/core/src/avkit_core/domain/download.py:429-438`) has only `ok` and `error_message`.
4. **Check SABR never uses cookies, and its text does not say so.** `check_sabr_status` (`adapter.py:798-810`) probes with `SABR_EXTRACTOR_ARGS` and no cookie option. `sabrResultText` (`ui/src/renderer/src/features/downloader/sabr-panel.ts:21-31`) shows `SABR active — quality limited to 360p · checked HH:MM:SS` or `SABR inactive · checked HH:MM:SS`.

## Context Tool Decision

```yaml
context_tool_decision:
  phase: planning_and_execution
  eligible_tools: []
  decision: not_applicable
  eligibility_basis: "graphify-out/ and ui/graphify-out/ are absent (2026-11-26). The change is one adapter method, one dataclass, one route, one schema, one renderer page and one text helper, all read at plan time by file and line; a bypass class."
  human_message_reference: null
```

## Harness, driver and reviewer route

- **Driver:** Claude Code in VSCode on Mat's Windows host (`.agent/context/harness.local.md`, block `### Claude Code`; `fresh_worker: Agent tool + .claude/agents/`). Validation runs through `rtk proxy` with the receipt pattern.
- **Receipts:** `C:/Temp/av-kit/2026-11-26-ytdlp-challenge-and-cookie-test/ycc-*` (called `R` below). Every row runs with `$env:PYTHONIOENCODING='utf-8'`, `$env:RECEIPTS_DIR='C:/Temp/av-kit'` and `$env:ELECTRON_RUN_AS_NODE=$null`.
- **Working directory:** `P:/av-kit` on `main`. No branch, no worktree. Vitest and npm commands for the UI `Set-Location 'P:\av-kit\ui'` in pwsh and return; the Bash tool is not used for Vitest.
- **Electron E2E:** on the mini-air host only, through `uv run python tools/e2e_remote.py run <commit>` (run book `.agent/docs/e2e-remote-host.md`; grouping D-1411). Uncommitted work travels as a snapshot commit that moves no ref (`snapshot-commit.py`, copied from `docs/execution/plans/2026-11-20-e2e-devpc-clipboard/`). Vitest, pytest and the type checks stay on the dev PC.
- **Reviewer:** Codex through `tools/Invoke-CodexDispatch.ps1` (`avkit_independent_reviewer`) with `$env:AGENT_MODEL_REGISTRY_HOME='P:/.agent'`. Ledger loops: `ycc-plan-2026-11-26-ytdlp-challenge-and-cookie-test` and `ycc-execution-2026-11-26-ytdlp-challenge-and-cookie-test`. Caps from `.agent/review-limits.json` (3 plan rounds, 6 execution rounds). The orchestrator dispatches the plan review; this plan's author does not.
- **Never in these rows without Mat's words:** commit, push, tag, release, publish, a change to a known-failures list, a retry or raised timeout on a failing test.
- **Secrets:** no row reads, prints, copies or dispatches a real cookie value, a cookie file or browser profile content, and no receipt holds one. Tests use cookie files that the test itself writes with made-up content. Review prompts forbid opening `P:/av-kit/.mcp.json`, any `mcp-token.txt`, `~/.claude.json`, any `.env`, `.claude/settings.local.json`, any cookie file or browser profile, and anything under `.agent/fleet/hub`.

## Handoff Set

| Scope | Canonical handoff |
|---|---|
| MEU-168 yt-dlp challenge solver | `.agent/context/handoffs/2026-11-26-ytdlp-challenge-and-cookie-test-MEU-168-handoff.md` |
| MEU-169 Cookie test outcome | `.agent/context/handoffs/2026-11-26-ytdlp-challenge-and-cookie-test-MEU-169-handoff.md` |
| MEU-170 SABR check and cookies | `.agent/context/handoffs/2026-11-26-ytdlp-challenge-and-cookie-test-MEU-170-handoff.md` |

Rolling reviews:

- `.agent/context/handoffs/2026-11-26-ytdlp-challenge-and-cookie-test-plan-critical-review.md`
- `.agent/context/handoffs/2026-11-26-ytdlp-challenge-and-cookie-test-implementation-critical-review.md`

## Work Packages and Context Lifecycle

| ID | Work | depends_on | context_strategy | durable_outputs |
|---|---|---|---|---|
| WP-1 | Baseline and plan-local scripts (row 0) | — | shared | `baseline.sha`, `baseline-scope.json`, `baseline-eol.json`, `baseline-pins.json`, the copied scripts, `row-check.py`, `proof-extract.py`, `row-run.ps1`, `canon-edit.py` |
| WP-2 | MEU-168: before-run, lock Red and Green, suites, after-run, the conditional fallback, the proof verdict, packaged checks (rows 1 to 5, 5a, 5b, 5c and 6) | WP-1 | shared | `uv.lock`, `pyproject.toml`, `tests/unit/test_ytdlp_lock.py`, the proof receipts |
| WP-3 | MEU-169 backend: Red, Green, OpenAPI, MCP Red and Green (rows 7, 8, 9, 10a and 10b) | WP-2 | shared | The domain type, the adapter, the service, the schema, the route, `openapi.committed.json`, the MCP description |
| WP-4 | MEU-169 and MEU-170 renderer: Red on the dev PC, the Red run on mini-air, Green, kept check (rows 11, 11a, 11b and 12 to 14) | WP-3 | shared | `cookie-test-result.ts`, `DownloaderPage.tsx`, `sabr-panel.ts`, the unit tests, the E2E spec |
| WP-5 | Electron E2E on mini-air (rows 15 to 17) | WP-4 | shared | The snapshot receipt, the run folder |
| WP-6 | Canon, registers and status (rows 18 and 19) | WP-5 | shared | 01, 02, 04 and 06 text; the three issues; MEU-168 to MEU-170 status; `BUILD_PLAN.md` |
| WP-7 | Closeout (H1, H2) | WP-6 | `compact_continue` | The three handoffs, the review, the reflection, the commit draft |

## Lane Ownership

Copied from the grouping's `## Session Ownership` (D-1412):

```yaml
ytdlp-challenge-and-cookie-test:
  tier: 1
  owns:
    - packages/infrastructure/pyproject.toml
    - uv.lock
    - packages/infrastructure/src/avkit_infra/youtube/
    - packages/core/src/avkit_core/services/download.py
    - packages/api/src/avkit_api/schemas/downloads.py
    - packages/api/src/avkit_api/routes/downloads.py
    - openapi.committed.json
    - mcp-server/src/toolsets/download.ts
    - ui/src/renderer/src/features/downloader/
    - docs/build-plan/02-infrastructure.md
    - docs/build-plan/04-rest-api.md
    - docs/execution/plans/2026-11-26-ytdlp-challenge-and-cookie-test/
```

**Paths this plan changes that the list does not name** (D-1467; none is in another session's `owns` list as read on 2026-11-26, and execution is one session at a time on `main`):

| Path | Why |
|---|---|
| `pyproject.toml` (the root file; one line, and only while the 7-day hold lasts) | `HOLD_OVERRIDE`, D-1468 |
| `packages/core/src/avkit_core/domain/download.py`, `packages/core/src/avkit_core/domain/enums.py` | The outcome is a field of `CookieTestResult` (home Outcome row) |
| `tests/unit/test_ytdlp_lock.py` (new), `tests/unit/test_domain.py`, `tests/unit/test_services.py`, `tests/integration/test_youtube_adapter.py`, `tests/e2e/test_api_downloads.py`, `tests/e2e/api_fakes.py` | The homes' Tests rows |
| `ui/tests/unit/cookie-test-result.test.ts` (new), `ui/tests/unit/sabr-panel.test.ts`, `ui/tests/unit/downloader-page.behavior.test.ts`, `ui/tests/e2e/downloader-cookie-test.test.ts` (new), `ui/tests/e2e/test-ids.ts` | The homes' Tests rows; E2 |
| `mcp-server/tests/download-cookies-test.test.ts` (new) | Home Wire row |
| `docs/build-plan/01-domain-layer.md` (line 444), `docs/build-plan/06-gui.md` (line 475 and §SABR Indicator Panel) | The grouping names 06 in prose only; 01 states the type's shape |
| `.agent/context/known-issues.yaml` and `.md`, `.agent/context/meu-status.yaml`, `.agent/context/meu-registry.md`, `docs/BUILD_PLAN.md`, `docs/execution/metrics.md`, `.agent/context/current-focus.md`, the grouping's §6 row | Shared closeout files (grouping §4) |

`openapi.committed.json` is also in Session 106's list (tier 2); Session 106 executes after this session. `DownloaderPage.tsx` is restyled by Session 105 (tier 3) later. This plan changes only the Test Cookies result and busy state and the SABR status text there. It keeps the eight Advanced panel ids, their order, the status slot and the 16 px gap (`ui/tests/e2e/downloader-advanced-gap.test.ts`).

## User Review Required

> [!IMPORTANT]
> **One question is open for Mat, and it is not this plan's:** D-1413 (grouping §8): do plan drafts started before the grouping's scoping review stand as inputs? Until Mat rules, D-103 governs. This plan is a draft input under that question.
>
> **D-1460 to D-1469 are agent choices** made under Mat's 2026-11-18 hand-over, each with its do-nothing option in §Decision Log. None hits an M item that stays Mat's.
>
> **What changes for you:**
>
> - yt-dlp moves from 2026.10.26 to 2026.11.23, the stable release that upstream names as the fix. Installed copies get it only with a new release, and that release is yours; nothing here tags, uploads or publishes.
> - If execution starts before 2026-11-30, the root `pyproject.toml` gets the line `exclude-newer-package = { yt-dlp = false }`, as the dependency page says to do for yt-dlp. The line is to be removed, and `uv lock` run again, once the release is 7 days old; the handoff and the next session's prompt carry that follow-up.
> - Test Cookies shows a line beside the button: `Cookies read. YouTube answered.`, or `Could not read the cookies: <reason>`, or `Cookies read, but YouTube's check failed: <reason>`. With cookie mode None it says `Cookie mode is None. Nothing to test.` The button is disabled and shows a busy state while the test runs.
> - The SABR status adds ` · Check SABR does not use cookies` to a detected result. Check SABR itself is unchanged: it still probes without cookies (D-1465, option B).
> - The reply of `POST /downloads/cookies/test` gains two fields, `outcome` and `error_message`. `ok` stays.
> - mini-air runs the Electron suite twice, about 40 minutes each: once to show the two new tests failing before the renderer changes, once after (D-1469).
>
> **Existing assertions that change (M-7).** Each is named with its new assertion in §Pins that move and in its task row; none changes unless you approve this plan:
>
> - `tests/e2e/test_api_downloads.py::test_ac_15_7_cookie_test_envelope`
> - `tests/unit/test_domain.py::test_ac_4_4_cookie_test_result_shape`
> - `tests/integration/test_youtube_adapter.py::test_ac_6_13_test_cookies_never_raises_cookie_error`
> - `ui/tests/unit/sabr-panel.test.ts`: `AC-138.8 each snapshot gives its contract text` and `AC-138.8 the time is zero-padded local time`
> - `ui/tests/unit/downloader-page.behavior.test.ts`: `AC-138.8 the SABR panel shows an Inactive and an Active check with their time`
>
> **What may not be proved.** The proof of MEU-168 is a real extraction without cookies. Upstream says the failing player was served by account (yt-dlp/ejs issue 79), so the run before the change may not show the errors on this machine; and one third-party daily check (dennissoftman/ytmini issue 6) still failed on 2026.11.23 today. If the pair is not "errors before, none after", the row ends `[B]` and the handoff says `INCOMPLETE VERIFICATION` (D-1462). No row uses your cookies to get a better proof.

## Proposed Changes

### Single-statement contracts

| Mechanism id | The one statement |
|---|---|
| `YTDLP_LOCK` | `uv.lock` holds yt-dlp 2026.11.23 and yt-dlp-ejs 0.8.0, and `packages/infrastructure/pyproject.toml` requires `yt-dlp>=2026.11.23` and `yt-dlp-ejs==0.8.0`. |
| `HOLD_OVERRIDE` | The root `pyproject.toml` gains the one line `exclude-newer-package = { yt-dlp = false }` under `[tool.uv]` only if `uv lock` refuses 2026.11.23 without it; nothing else in that file changes. |
| `PROOF_PAIR` | `proof-extract.py` runs one extraction of `SABR_PROBE_URL` with the client list of `COOKIE_EXTRACTOR_ARGS` and no cookie option, prints only its fixed outcome lines, and ends with exactly one verdict: `challenge-errors`, `clean` or `blocked`; the proof passes only when the run on 2026.10.26 says `challenge-errors` and the run on 2026.11.23 says `clean`. |
| `VARIANT_FALLBACK` | The adapter sets no `player_js_variant`, unless the after-run says `challenge-errors` and its `variant=` line is not `tv`; only then do rows 5a and 5b make every options dict that the adapter gives yt-dlp for a download, a metadata read or the cookie test carry `player_js_variant` `['tv']`, with the SABR probe's arguments unchanged. |
| `COOKIE_TEST_OUTCOME` | `CookieTestResult.outcome` is `ok`, `unreadable`, `check_failed` or `None`; `None` and `ok` go with `ok=True` and no message, and `unreadable` and `check_failed` go with `ok=False` and a non-empty message; `None` is only Mode None. |
| `COOKIE_TEST_STEPS` | The adapter decides the outcome by where the failure happens: a missing cookie file, or any error raised while yt-dlp builds its object and loads its cookie jar, is `unreadable`; any error raised by the extraction that follows is `check_failed`; no error is `ok`. |
| `COOKIE_TEST_REASON` | The message of a failed outcome is the first line of yt-dlp's text with a leading `ERROR:` dropped, passed through the service's `scrub_line`, with the fixed text `cookie source unreadable` or `cookie probe failed` when that leaves nothing. |
| `COOKIE_TEST_WIRE` | `CookieTestOut` is `{ ok: bool, outcome: "ok", "unreadable", "check_failed" or null, error_message: string or null }`, and the route copies the three values from the service's result. |
| `COOKIE_TEST_SHOWN` | After a reply, the Advanced panel shows `cookieTestResultText(reply)` in a `cookie-test-result` element in the Test Cookies row; the element is absent until a test has finished, and it is removed when a new test starts or a cookie setting changes. |
| `COOKIE_TEST_BUSY` | From the click until the request settles, `cookie-test-btn` has `loading` set, so it is disabled with `aria-busy="true"`. |
| `SABR_CHECK_SCOPE` | For a snapshot with `source: detected` and mode `active` or `inactive`, `sabrResultText` ends with ` · Check SABR does not use cookies`; every other snapshot's text is today's. |
| `SABR_KEPT` | No backend SABR code changes: the source of `SABR_PHRASES`, `SABR_EXTRACTOR_ARGS`, `sabr_phrase`, `check_sabr_status`, `check_sabr`, `force_sabr` and `clear_sabr` equals the baseline copy. |

`cookieTestResultText` gives exactly these four texts:

| Reply | Text |
|---|---|
| `outcome: "ok"` | `Cookies read. YouTube answered.` |
| `outcome: "unreadable"` | `Could not read the cookies: <error_message>` |
| `outcome: "check_failed"` | `Cookies read, but YouTube's check failed: <error_message>` |
| `outcome: null` | `Cookie mode is None. Nothing to test.` |

The outcome is said in words. The element uses the classes of `sabr-status` (`text-sm text-fg-muted`), has `role="status"`, and adds no colour.

### Pins that move

| Row | Test | Today | After |
|---|---|---|---|
| 7 | `tests/e2e/test_api_downloads.py::test_ac_15_7_cookie_test_envelope` | `ok.json() == {"ok": True}` and `"error_message" not in ok.json()` | `ok.json() == {"ok": True, "outcome": "ok", "error_message": None}`; and, with a fake that returns `check_failed` with the message `Sign in to confirm`, the reply is `{"ok": False, "outcome": "check_failed", "error_message": "Sign in to confirm"}`. The `"HTTP_COOKIE" not in ok.text` line and the 422 case stay |
| 7 | `tests/unit/test_domain.py::test_ac_4_4_cookie_test_result_shape` | `_field_names(CookieTestResult) == ("ok", "error_message")` | `_field_names(CookieTestResult) == ("ok", "error_message", "outcome")`. The `"cookies" not in` line stays |
| 7 | `tests/integration/test_youtube_adapter.py::test_ac_6_13_test_cookies_never_raises_cookie_error` | Equality with `CookieTestResult(ok=..., error_message=...)` for the missing file, the ok file and Mode None | `missing == CookieTestResult(ok=False, error_message=missing.error_message, outcome=CookieTestOutcome.unreadable)`; `locked.outcome is CookieTestOutcome.unreadable`; `ok == CookieTestResult(ok=True, error_message=None, outcome=CookieTestOutcome.ok)`; `none_mode == CookieTestResult(ok=True, error_message=None, outcome=None)`. The `"Netscape" not in` line stays |
| 11 | `ui/tests/unit/sabr-panel.test.ts`, `AC-138.8 each snapshot gives its contract text` | `activeChecked` is `ACTIVE · checked 09:05:07`; `inactiveChecked` is `SABR inactive · checked 09:05:07` | Each of the two ends with ` · Check SABR does not use cookies`. The other eight entries stay |
| 11 | `ui/tests/unit/sabr-panel.test.ts`, `AC-138.8 the time is zero-padded local time` | First entry `SABR inactive · checked 00:00:01` | `SABR inactive · checked 00:00:01 · Check SABR does not use cookies`. The forced entry stays |
| 11 | `ui/tests/unit/downloader-page.behavior.test.ts`, `AC-138.8 the SABR panel shows an Inactive and an Active check with their time` | `toBe('SABR inactive · checked 09:05:07')` and `toBe('SABR active — quality limited to 360p · checked 09:05:07')` | Each expected text ends with ` · Check SABR does not use cookies` |

Fixtures that follow the type (not assertions): the fakes in `tests/e2e/test_api_downloads.py:163-173`, `tests/e2e/api_fakes.py:481-483` and `tests/unit/test_services.py:725-734` return results with `outcome`. No other existing assertion changes; a test that fails after a Green row and is not in this table is S5.

### Where values go

| Value | Writers | Readers | Rule |
|---|---|---|---|
| `outcome` | `YouTubeAdapter.test_cookies` only | The service (passes it on), the route, the renderer, the MCP reply | `COOKIE_TEST_STEPS`, `COOKIE_TEST_OUTCOME` |
| `error_message` | The adapter (first line), then the service (`scrub_line`) | The route, the renderer, the MCP reply | `COOKIE_TEST_REASON`; never text from a cookie file |
| The result text | `cookieTestResultText` only | `DownloaderPage.tsx` | `COOKIE_TEST_SHOWN` |
| The SABR scope clause | `sabrResultText` only | `DownloaderPage.tsx` (`sabr-status`) | `SABR_CHECK_SCOPE` |
| The yt-dlp version | `uv.lock` | The app, the packaged build, the licence list | `YTDLP_LOCK` |

### Spec text (row 18)

| File | Line endings | Edit |
|---|---|---|
| `docs/build-plan/01-domain-layer.md:444` | LF | `CookieTestResult` is `{ ok, error_message, outcome }`, with the three outcome values and Mode None |
| `docs/build-plan/02-infrastructure.md` §Cookie test | CRLF | The sentence that says `CookieTestResult` holds `ok` and `error_message` only gains `outcome` and points to §Cookie test outcome (residual) |
| `docs/build-plan/02-infrastructure.md`, the three homes | CRLF | A `Delivered` note under each home: what shipped, the D-ids of this plan, and for MEU-168 which of the two (the version, or the fallback) was needed, or the `INCOMPLETE VERIFICATION` wording |
| `docs/build-plan/04-rest-api.md:177` | CRLF | The reply is `200 { ok, outcome, error_message }`; no cookie bytes back |
| `docs/build-plan/06-gui.md:475` and §SABR Indicator Panel | CRLF | Test Cookies: the result line, its four texts and the busy state; SABR: the scope clause |

`docs/build-plan/gui-actions-index.md:29` (`download:cookies_test`, `specified`) needs no change: the action, its route and its status are the same.

### MEU-168: yt-dlp challenge solver

**Boundary inventory**

| Boundary | Input | Owner of validation | Invalid input |
|---|---|---|---|
| `uv.lock` (dependency set) | The yt-dlp release | `tests/unit/test_ytdlp_lock.py`; `tests/unit/test_fetch_deno.py` (the ejs pin match) | A lock below 2026.11.23, or an ejs version that yt-dlp's `default` extra does not pin, fails a test |
| `proof-extract.py` (a script, outside the suites) | The network and YouTube's reply | The script's verdict rule | A network error, an HTTP 429, a bot check or no player response is `blocked`: `INCOMPLETE VERIFICATION`, exit 4, never a pass |
| The packaged backend | The PyInstaller build | `tools/smoke_packaged_runtime.py`; `tools/generate_third_party_licenses.py` | A missing Deno, a failed solver import or an unlisted licence exits non-zero |

No REST, MCP, UI or file input changes in this MEU.

**Acceptance criteria**

| AC | Type | Description | Source | Negative test |
|---|---|---|---|---|
| AC-168.1 | unit | `YTDLP_LOCK`: `test_ac_168_1_lock_holds_the_fixed_release` reads `uv.lock` and `packages/infrastructure/pyproject.toml` and passes only with yt-dlp 2026.11.23 or later in the lock, yt-dlp-ejs 0.8.0, and the floor `yt-dlp>=2026.11.23`. `row-check.py lock` proves that the lock differs from the baseline only in the yt-dlp package, the infrastructure package's requirement on it and, under `HOLD_OVERRIDE`, the matching options entry | Research-backed: yt-dlp issue 18123 and PyPI metadata of 2026.11.23, read 2026-11-26; home Version row; Local Canon: `docs/distribution/dependency-updates.md` §The 7-day hold; D-1460, D-1468 | The same helper refuses a lock text that holds 2026.10.26 and a pyproject text with no floor; `row-check.py lock` fails on any other changed package (S7) |
| AC-168.2 | unit | The test that fails when yt-dlp and yt-dlp-ejs disagree still runs: `tests/unit/test_fetch_deno.py` passes with the new version installed, and its file hash equals the baseline's | Human-approved: D-640 (the pin rule); home Version row | The file's own fixture with `yt-dlp-ejs==0.0.1` still gives its mismatch text |
| AC-168.3 | integration | With 2026.11.23 installed and before any other product change, `tests/integration/test_youtube_adapter.py`, `tests/integration/test_youtube_client_fallback.py`, `tests/unit/test_extract_options.py` and `tests/integration/test_js_runtime_wiring.py` pass, each at its baseline hash | Local Canon: home Tests row | A failure here is S5, not an edit |
| AC-168.4 | script | `PROOF_PAIR`, the script: its options hold no `cookiefile` and no `cookiesfrombrowser`; it prints only the lines `yt-dlp=`, `yt-dlp-ejs=`, `deno=`, `clients=`, `player=`, `variant=`, `challenge=` (a count per fixed needle), `formats=`, `verdict=`; `--selftest` proves each verdict from canned log lines | Local Canon: home Proof row; D-464 A; D-1462 | `--selftest` feeds a line holding a made-up cookie value and a home path and finds neither in the output; a `blocked` case exits 4 with `INCOMPLETE VERIFICATION` |
| AC-168.5 | script | `PROOF_PAIR`, the pair: the receipt of the run on 2026.10.26 ends `verdict=challenge-errors`, and the receipt of the run on 2026.11.23 ends `verdict=clean` | Local Canon: home Proof row; D-1462 | Any other pair leaves row 5c `[B]` with the receipts, and the MEU-168 handoff says `INCOMPLETE VERIFICATION` |
| AC-168.6 | unit | `VARIANT_FALLBACK`: `test_ac_168_6_adapter_sets_no_player_js_variant` finds no `player_js_variant` key in any extractor arguments the adapter builds; the handoff records which of the two was needed | Research-backed: yt-dlp pull request 18124 and `_video.py` at tag 2026.11.23, read 2026-11-26; home Fallback row; D-1461 | Only when row 5 classifies the pair as `fallback-applies`: row 5a replaces that guard with `test_ac_168_6_adapter_passes_player_js_variant_tv`, which requires `['tv']` in every options dict the adapter gives yt-dlp for a download, a metadata read and the cookie test, leaves the SABR probe's arguments as they are, and fails Red before row 5b changes the adapter |
| AC-168.7 | packaged | The backend built by `tools/package_backend.py` into `packaging/dist/avkit-backend` (git-ignored; the licence tool reads only `packaging/build` and `packaging/dist`) passes `tools/smoke_packaged_runtime.py` (source `bundled`, a parsed Deno version, the solver imports), and the generated licence list names yt-dlp 2026.11.23 | Local Canon: home Packaged row; 02 §yt-dlp JS runtime (residual) `RUNTIME_SMOKE`; 07 `LICENCE_LIST` | The smoke exits 1 on a missing field; the licence tool fails closed |
| AC-168.8 | check | Reach: the session's changed paths hold no version file, no release note and no tag; no row uploads or publishes | Local Canon: home Reach row; D-1407; PROJECT-PROFILE E5 | `row-check.py scope-paths` fails on a path outside §Files Modified |

**Spec sufficiency.** The home names the release, the pin rule, the proof, the fallback and the packaged checks. What it leaves open is decided in D-1460 (how the version is held), D-1461 (when the fallback applies), D-1462 (what a proof that does not show the pair means) and D-1468 (the 7-day hold: the home's Version row points to the documented yt-dlp line, and D-1468 says when it is added and who removes it).

### MEU-169: Cookie test outcome

**Boundary inventory**

| Boundary | Input | Owner of validation | Invalid input |
|---|---|---|---|
| `POST /downloads/cookies/test` body | `CookieTestIn` (`mode`, `browser`, `profile`, `cookie_file`) | Unchanged: the schema (`extra="forbid"`) and the service | Unchanged: an unknown mode is a 422 `ValidationError`; a `CookieTestError` from the service is a 422 |
| The reply | `CookieTestOut` | The schema: `outcome` is a closed set or null | A domain result outside `COOKIE_TEST_OUTCOME` cannot be built (`__post_init__` raises) |
| The cookie source (a file, a browser database) | Read by yt-dlp only | `COOKIE_TEST_STEPS` | Missing, locked, malformed or unknown profile: `unreadable`. No text from the source reaches the reply or the log |
| The MCP `cookies_test` action | Input schema unchanged | `mcp-server/src/toolsets/download.ts` | Unchanged (strict schema) |
| The renderer | The reply JSON | `cookieTestResultText` | A rejected request shows the page error banner and no result line (G15) |

**Input matrix (adapter)**

| Mode | Source | yt-dlp | `ok` | `outcome` | `error_message` |
|---|---|---|---|---|---|
| none | — | Not built | true | `None` | `None` |
| file | Missing file | Not built | false | `unreadable` | `cookie file is missing` |
| file or browser | Jar load raises (`CookieLoadError`, `DownloadError`, `OSError`, another yt-dlp error or a domain error) | `extract_info` not called | false | `unreadable` | First line, or `cookie source unreadable` |
| file or browser | Jar loads; `extract_info` raises | Called once | false | `check_failed` | First line, or `cookie probe failed` |
| file or browser | Jar loads; `extract_info` returns | Called once | true | `ok` | `None` |
| Not a known mode (the service refuses it first) | — | Not built | false | `unreadable` | `unknown cookie mode` |

**Acceptance criteria**

| AC | Type | Description | Source | Negative test |
|---|---|---|---|---|
| AC-169.1 | unit | `COOKIE_TEST_OUTCOME`: `CookieTestOutcome` has exactly `ok`, `unreadable`, `check_failed`; `CookieTestResult` has the fields `("ok", "error_message", "outcome")` | Local Canon: home Outcome row; D-1463 | `ok=True` with `unreadable`, `ok=False` with `ok` or `None`, and a failed outcome with no message each raise |
| AC-169.2 | integration | `COOKIE_TEST_STEPS`, each row of the input matrix from a stubbed yt-dlp, with the count of `extract_info` calls asserted | Local Canon: home Outcome and Tests rows | A stub whose jar load raises and whose `extract_info` would succeed still gives `unreadable` |
| AC-169.3 | integration | With the real yt-dlp class and a cookie file that the test writes with made-up, malformed content, the result is `unreadable` and `extract_info` is never called (it is patched to fail the test) | Local Canon: home Outcome row ("could not be read") | No socket is opened: the test fails on any connection attempt |
| AC-169.4 | unit | `COOKIE_TEST_REASON`: the adapter's message is the first line without `ERROR:`; the service returns `scrub_line` of it; a home-folder path in the text is replaced as for a failed download; an empty line gives the fixed text | Local Canon: home Reason row; 02 §yt-dlp log detail (residual); D-627, D-639 | A marker written into the test's cookie file appears in no reply field and in no captured log record |
| AC-169.5 | API | `COOKIE_TEST_WIRE`: the route returns `ok`, `outcome` and `error_message` for each outcome; a `CookieTestError` is still a 422 with the error envelope | Local Canon: home Wire and Tests rows; 04 §Downloads | The moved pin `test_ac_15_7_cookie_test_envelope`; `HTTP_COOKIE` still absent from the reply text |
| AC-169.6 | contract | `openapi.committed.json` matches the code: `--check` fails before the regeneration and passes after it, and the `CookieTestOut` schema holds the three properties | Local Canon: home Wire row; the OpenAPI drift gate | A stale committed document fails `--check` |
| AC-169.7 | MCP | The `cookies_test` reply carries the API's JSON unchanged, with `outcome` and `error_message`; the action's description names the three outcomes; the input schema is unchanged | Local Canon: home Wire row | An input with an unknown key is still refused |
| AC-169.8 | unit | `cookieTestResultText` gives the four texts of §Single-statement contracts | Local Canon: home Shown row; D-1464 | A failed outcome with a null or empty message gives the text without the colon part |
| AC-169.9 | unit | `COOKIE_TEST_SHOWN` on the page: no `cookie-test-result` before a test; after each outcome its text is shown with `role="status"`; it is removed when a new test starts and when the cookie mode, browser, profile or file changes | Local Canon: home Shown row; G15; D-1464 | A rejected request (422) shows the `error-banner` and leaves no `cookie-test-result` |
| AC-169.10 | unit | `COOKIE_TEST_BUSY`: while the request is pending the button is disabled with `aria-busy="true"`; after it settles the button is enabled | Local Canon: home Shown row; G35; D-1464 | A second click while pending sends no second request |
| AC-169.11 | E2E | On mini-air, with the API routed in the spec: each outcome shows its text beside the button; the button is disabled while a delayed reply is pending; with a result shown the eight Advanced ids keep their order, the tail is at most 1 px and the gap is 16 px within 1 px | Local Canon: home Tests row ("Electron E2E through the API seam"); E2; AC-159.3 to AC-159.5 | `downloader-advanced-gap.test.ts` passes unchanged (its file hash equals the baseline's) |
| AC-169.12 | docs | The spec text of row 18 for 01, 02 §Cookie test, 04 and 06 is in place, each file with its own line endings | Local Canon: AGENTS §Planning Contract (spec follows behaviour) | `eol-check.py` fails on a changed line ending |

**Feedback tier (G35).** Test Cookies changes no saved state. Its feedback is in place: the button's busy state while it runs, then the result line beside it; an API error goes to the page banner (G15). The tier table of `docs/gui-element-reference.md` §4 is not shipped in this repository (`gui-refs-not-shipped`), so the tier is given by this description and not by a T-number.

**Spec sufficiency.** The home names three outcomes, a reason, where they show, the busy state and the wire. The field names, the None-mode reply and the texts are D-1463 and D-1464.

### MEU-170: SABR check and cookies

**Boundary inventory.** No input boundary changes: no route, schema, setting, MCP action or backend function changes. The only change is the text that `sabrResultText` returns for two of its ten snapshots.

**Acceptance criteria**

| AC | Type | Description | Source | Negative test |
|---|---|---|---|---|
| AC-170.1 | unit | `SABR_CHECK_SCOPE`: the two detected texts end with ` · Check SABR does not use cookies` | Local Canon: home Choice and Said rows; D-1465, D-1466 | `SABR not checked`, `Checking…`, the forced text and the cleared text are today's |
| AC-170.2 | unit | On the page, `sabr-status` shows the new text after an Inactive and an Active check | Local Canon: home Said row | The moved pin in `downloader-page.behavior.test.ts` |
| AC-170.3 | check | `SABR_KEPT`: `row-check.py kept` finds the named sources equal to the baseline copies, and `SABRStatusOut` and the SABR paths of `openapi.committed.json` unchanged; the SABR tests of `tests/unit/test_services.py` and `tests/integration/test_youtube_adapter.py` pass with no SABR assertion changed | Local Canon: home Kept row; 02 §SABR check result (residual) | A changed phrase, log line or source fails the check |
| AC-170.4 | E2E | On mini-air, with `/downloads/sabr/check` routed to an Inactive detected reply, `sabr-status` shows the text with the clause | Local Canon: home Tests row; E2 | With a forced reply the clause is absent |
| AC-170.5 | docs | 06 §SABR Indicator Panel and the MEU-170 home's Delivered note say that Check SABR probes without cookies and that the status says so | Local Canon: home Said row | `eol-check.py` |

**Spec sufficiency.** The home asks the plan to research and choose. The research is in §Research References, the choice is D-1465 and the wording is D-1466.

### Files Modified

| Path | Line endings | MEU | Change |
|---|---|---|---|
| `packages/infrastructure/pyproject.toml` | CRLF | 168 | `"yt-dlp"` becomes `"yt-dlp>=2026.11.23"` |
| `pyproject.toml` (root) | LF | 168 | `HOLD_OVERRIDE` only, and only when needed |
| `uv.lock` | LF | 168 | Written by `uv lock --upgrade-package yt-dlp==2026.11.23` only |
| `tests/unit/test_ytdlp_lock.py` | new, LF | 168 | AC-168.1, AC-168.6 |
| `packages/core/src/avkit_core/domain/enums.py` | as measured in row 0 | 169 | `CookieTestOutcome` |
| `packages/core/src/avkit_core/domain/download.py` | CRLF | 169 | `CookieTestResult.outcome` and its checks |
| `packages/infrastructure/src/avkit_infra/youtube/adapter.py` | CRLF | 169 | `test_cookies` per `COOKIE_TEST_STEPS`; nothing else (and rows 5a and 5b only under `VARIANT_FALLBACK`) |
| `packages/core/src/avkit_core/services/download.py` | as measured in row 0 | 169 | `test_cookies` cleans the message |
| `packages/api/src/avkit_api/schemas/downloads.py` | LF | 169 | `CookieTestOut` |
| `packages/api/src/avkit_api/routes/downloads.py` | CRLF | 169 | The route copies the three values |
| `openapi.committed.json` | CRLF | 169 | Regenerated |
| `docs/execution/plans/2026-11-14-capture-shapes-steps/openapi-delta.py` | LF | 169 | AC-106.5's delta: the Session 104 cookie test shapes are set back before the compare (D-1600) |
| `mcp-server/src/toolsets/download.ts` | LF | 169 | The `cookies_test` description |
| `mcp-server/tests/download-cookies-test.test.ts` | new, LF | 169 | AC-169.7 |
| `ui/src/renderer/src/features/downloader/cookie-test-result.ts` | new, LF | 169 | `cookieTestResultText` and the reply type |
| `ui/src/renderer/src/features/downloader/DownloaderPage.tsx` | mixed (761 CRLF, 226 LF); each touched line keeps its ending | 169 | The result element, the busy state |
| `ui/src/renderer/src/features/downloader/sabr-panel.ts` | LF | 170 | The scope clause |
| `ui/tests/e2e/test-ids.ts` | CRLF | 169 | One added block for `cookie-test-result`; no existing byte changes (AC-51.6, AC-81.13) |
| `ui/tests/e2e/downloader-cookie-test.test.ts` | new, LF | 169, 170 | AC-169.11, AC-170.4 |
| `ui/tests/unit/cookie-test-result.test.ts` | new, LF | 169 | AC-169.8 |
| `ui/tests/unit/downloader-page.behavior.test.ts` | mixed (2096 CRLF, 623 LF) | 169, 170 | AC-169.9, AC-169.10; the moved AC-138.8 pin |
| `ui/tests/unit/sabr-panel.test.ts` | LF | 170 | The two moved AC-138.8 pins |
| `tests/unit/test_domain.py`, `tests/unit/test_services.py`, `tests/integration/test_youtube_adapter.py`, `tests/e2e/test_api_downloads.py`, `tests/e2e/api_fakes.py` | CRLF | 169 | §Pins that move; the fakes; the new tests |
| `docs/build-plan/01-domain-layer.md` (LF), `02-infrastructure.md`, `04-rest-api.md`, `06-gui.md` (CRLF) | — | 168 to 170 | §Spec text |
| `.agent/context/known-issues.yaml` and `.md`, `meu-status.yaml`, `meu-registry.md`, `docs/BUILD_PLAN.md`, `current-focus.md`, `docs/execution/metrics.md`, the grouping §6 row | as measured in row 0 | — | Closeout (row 19, H1, H2) |

Read, never changed: `ui/tests/e2e/downloader-advanced-gap.test.ts`, `tests/unit/test_fetch_deno.py`, `tests/integration/test_youtube_client_fallback.py`, `tests/unit/test_extract_options.py`, `tests/integration/test_js_runtime_wiring.py`, `packages/core/src/avkit_core/ports/youtube.py`, `ui/src/renderer/src/features/downloader/cookie-bar.ts`, `ui/src/renderer/src/features/downloader/downloader-help-content.ts`, `docs/build-plan/gui-actions-index.md`.

### Project files

Written in row 0 inside this plan folder. Copies come from `docs/execution/plans/2026-11-22-tray-show-and-baseline-fixes/` with this plan's `PLAN`, receipts folder, scope and AC ids, except where named.

| File | From | Use |
|---|---|---|
| `baseline.ps1` | copy | `HEAD`, `git status`, the dirty list and hashes, the scope hashes, the line endings, the pins |
| `red-check.py` | copy | Red receipts: `--runner pytest`, `vitest` or `playwright`, `--require` |
| `identity.py`, `eol-check.py`, `host-wait.py`, `load-run.py`, `issue-resolve.py`, `crlf.py`, `session-gate.ps1` | copy | As in Session 102 |
| `snapshot-commit.py` | copy of `2026-11-20-e2e-devpc-clipboard/snapshot-commit.py` | The commit object for mini-air; moves no ref |
| `row-check.py` | new, in the shape of Session 102's | Subcommands: `steps`, `red-record`, `red-unchanged`, `pins-unchanged`, `pins-moved`, `scope-paths`, `lock`, `proof-recorded`, `proof-pair`, `variant-gate`, `type-only`, `kept`, `openapi`, `test-ids`, `licence`, `snapshot-paths`, `e2e-red`, `e2e-result`, `canon`, `register`, `status`, `no-deselect`, `metrics`, `commit-draft`, `next-prompt`, `--selftest` |
| `proof-extract.py` | new | `PROOF_PAIR`; `--require-version VERSION`, `--expect VERDICT`, `--out JSON`, `--variant tv` (row 5b only), `--selftest` |
| `row-run.ps1` | new, in the shape of Session 102's `session-gate.ps1` | Runs one row's steps from `task.md` §Row steps, fail-fast, one receipt per step; last line `row <id>: all steps exit 0` |
| `canon-edit.py` | new, in the shape of Session 102's | The §Spec text edits by bytes, each file with its own line endings |

`proof-extract.py` exits 0 when the verdict equals `--expect`, 1 when it differs, and 4 when the verdict is `blocked`. It takes its client list and probe URL from `avkit_infra.youtube.adapter` and resolves Deno as the app does, so the run is the app's extraction without cookies.

## Out of Scope

| Item | Basis |
|---|---|
| A release, a tag, an upload or a published build that ships the fix | Home Reach row; M-1 is Mat's |
| A SABR check that probes with the saved cookies (option A) | D-1465 chose B |
| A new `SABRSource` value that tells a download's detection from the check's | Not in the home; an API shape change (M-4). A download that detects SABR still writes `source: detected`, so the clause also shows there; it is a statement about the check and stays true |
| Any `player_js_variant` other than `tv`, or another solver workaround | The home's Fallback row names `tv` only |
| The client lists (`COOKIE_EXTRACTOR_ARGS`, the retry pin). Upstream took `web` out of its default clients in 2026.11.23 (pull request 18131) | Not in the homes; D-539, D-643 to D-646 govern the lists. Reported to the orchestrator |
| yt-dlp's own stderr line for a skipped cookie-file entry (`yt_dlp/cookies.py:1386` prints the line) | Not the reply and not an av-kit log line; it also happens on a download. Reported to the orchestrator for triage |
| The help popover texts (`downloader-help-content.ts`) | The home's Said row names the SABR status |
| Colours, emphasis and labels of the Advanced panel | Session 105 (MEU-171, MEU-172) |
| Live YouTube in the unit, integration or E2E suites, or in CI | Home Tests rows |
| Using Mat's cookies or browser profile in any row | The secrets rule of this session |
| Bumping `yt-dlp-ejs` or Deno | Home Version row: ejs stays the version the release pins (0.8.0, PyPI metadata read 2026-11-26) |

## BUILD_PLAN.md Audit

`docs/BUILD_PLAN.md` and `.agent/context/meu-registry.md` are rendered from `.agent/context/meu-status.yaml`. Row 19 sets MEU-168, MEU-169 and MEU-170 to `ready_for_review` with `tools/meu_status.py update` and renders; H2-2 sets them to `approved` after the review. The check is `uv run python tools/meu_status.py render --check`. No count or description in `BUILD_PLAN.md` is edited by hand. If row 5c ends `[B]`, MEU-168's status is not raised and the handoff says why.

## Verification Plan

### 1. Baseline (row 0)

`baseline.ps1` prints `HEAD` (recorded, never compared with a pinned commit), `git status`, `git worktree list` and one host-load sample. It writes `baseline.sha`, `baseline-dirty.txt`, `baseline-dirty-hashes.json`, `baseline-scope.json` (each §Files Modified path and each "Read, never changed" path to its SHA-256 or `absent`), `baseline-eol.json` and `baseline-pins.json`, and copies the scope files to `R/baseline-copies/`. It checks the free ids: `AC-168.`, `AC-169.` and `AC-170.` appear nowhere outside this plan folder, and D-1460 to D-1499 only in this plan folder and the grouping. The tree is dirty at plan time with the triage, grouping and proposal files of 2026-11-26 (thirteen paths outside the plan folders being written today); they are recorded, not touched.

### 2. Order

Before-run on 2026.10.26 (row 1), then lock Red and Green (rows 2 and 3), then the suites (row 4), then the after-run, which row 5 records and classifies as `proved`, `incomplete` or `fallback-applies`. Rows 5a and 5b are the fallback's Red and Green; when the pair is not `fallback-applies` each skips its fallback-only steps, and its `variant-gate` step (`--stage red` in row 5a, `--stage green` in row 5b) passes with `not-needed`. Row 5c gives the proof's verdict and is the one row that may end `[B]`. Then type-level and Red rows before each Green. A Red row changes no product file and passes when the named tests fail by assertion (`red-check.py`); the one exception is the type-only step inside row 7, which adds `CookieTestOutcome` and the `outcome` field with a default of `None` and no checks, so that the Red tests can import and fail by assertion and not by import error.

### 3. Dev PC checks

- Python: `uv run pytest` on the named files; `uv run pyright packages/`; `uv run ruff check packages/ tests/` and this plan folder's Python.
- UI: Vitest through pwsh with `Set-Location 'P:\av-kit\ui'`; `npm --prefix ui run typecheck`; `npm --prefix ui run lint`.
- MCP: `npm --prefix mcp-server test`; `npm --prefix mcp-server run typecheck`.
- OpenAPI: `uv run python tools/export_openapi.py --check openapi.committed.json` (fails), `-o openapi.committed.json`, then `--check` (passes).
- Lock: `uv lock --upgrade-package yt-dlp==2026.11.23`, `uv sync --locked --all-packages`, `uv lock --check`. Every later Python step uses `uv run --no-sync`.
- Packaged: `uv run --no-sync python tools/package_backend.py` (it writes the git-ignored `packaging/build` and `packaging/dist` and replaces the build that is there), then `tools/smoke_packaged_runtime.py --backend-dir packaging/dist/avkit-backend --out R/ycc-smoke.json`, then `tools/generate_third_party_licenses.py --out R/ycc-licences.txt` and `pytest tests/unit/test_generate_third_party_licenses.py`.

### 4. Electron E2E (rows 11a and 11b, then 15 to 17)

Electron runs only on mini-air, and `tools/e2e_remote.py run` runs the whole suite, about 40 minutes. There are two runs (D-1469). **The Red run (rows 11a and 11b)** takes a snapshot after row 11, when the tests are written and no renderer file has changed. It passes as a Red only when the tool's last line says `new-failures exit=40` and `row-check.py e2e-red` finds, in the run folder's `summary.json` and `host/report.json`, that the `new` list holds only titles of `downloader-cookie-test.test.ts`, that the four titles row 11 names as failing are in it (the fifth, `AC-170.4 a forced SABR status has no clause`, is a guard and passes), and that each failed by an `expect` assertion and not by a timeout or a launch error. **The Green run (rows 15 to 17)** follows.

`row-check.py snapshot-paths` lists every §Files Modified path that differs from `HEAD`. `snapshot-commit.py --out R/ycc-snapshot.json` builds the commit from them and `--verify` binds it. `tools/e2e_remote.py check`, then `tools/e2e_remote.py run <commit>`. The row's evidence is the tool's last stdout line, `e2e-remote: <reason> exit=<n> run=<run-id> receipts=<folder>`, and that folder. Exit 0 is the only pass. `host-busy` (22) and `host-locked` (23) mean wait and run again; they are never a pass. `new-failures` (40) is a finding. `row-check.py e2e-result` reads the run's `summary.json` and requires the five titles of `downloader-cookie-test.test.ts` and the AC-159 titles of `downloader-advanced-gap.test.ts` as passed, and the `commit` of `summary.json` equal to the snapshot's.

### Session gate (H1-2)

`session-gate.ps1`, fail-fast, later steps printed `not_run`, last line `session-gate: all steps exit 0`: identity before and after; static (`py-types`, `py-lint`, `ui-types`, `ui-lint`, `mcp-types`, `task-contract`, `scope-paths`, `line-endings`, `home-path`, `pins-unchanged`, `red-unchanged`, `kept`, `canon`, `row-steps` (`row-check.py steps`), the script selftests); `openapi`; fresh full (`py-tests` with nothing deselected, `ui-tests`, `mcp-tests`, `ui-build`, `state-render`, `issues-render`); and `e2e-remote`, which checks that row 16's run folder holds exit 0 for a snapshot that `--verify` still binds (a changed snapshot path re-runs rows 15 to 17 once). No step excuses a failing test by name. No step reaches YouTube.

## Stop Conditions

| ID | Condition | Action |
|---|---|---|
| S1 | A `graphify-out` graph appears | Re-decide the context tool |
| S2 | Row 0 finds a free id taken, or a citation anchor of §Goal missing | Stop and bring the receipt to Mat. A moved line is corrected, not a stop |
| S3 | A Red receipt fails `red-check.py`, or a Green row needs a changed expectation | Fix the test setup; never edit an expectation in Green |
| S4 | A path outside this plan's scope and `baseline-dirty.txt` changes, or a scope path changes by another hand | Stop and re-baseline with Mat. Never commit, stash or revert another session's work |
| S5 | An existing test that is not in §Pins that move fails after a Green or after the lock change | Rerun it alone once. If it fails again, stop: an M-7 question, not a fix |
| S6 | Codex is unavailable or the ledger refuses | Mat |
| S7 | `uv lock` changes a package other than yt-dlp, or still refuses 2026.11.23 with the `HOLD_OVERRIDE` line in place | Stop; restore `uv.lock` and the root `pyproject.toml` from the baseline copies and bring the receipt to Mat |
| S13 | `uv sync --all-packages` cannot replace a file that a running process holds | Tell Mat which file. Never stop a process |
| S8 | A proof run says `blocked`, or the pair is not `challenge-errors` then `clean` | Row 5c ends `[B]` with the receipts and a follow-up; continue with MEU-169 and MEU-170 (D-1462). Never rerun in a loop: one rerun after ten minutes for `blocked` only |
| S9 | Any output, receipt or reply is found to hold text from a real cookie source | Stop at once, delete the receipt, tell Mat |
| S10 | `e2e_remote.py` exits 22 or 23 | Wait and run again; after three tries, Mat |
| S11 | `e2e_remote.py` exits 40 in row 16, any other non-zero code in row 16, or anything but the Red result of §Verification Plan 4 in row 11b | A finding. Never edit `tools/e2e_host/known-failures.json`; never retry to green |
| S12 | The jar cannot be loaded apart from the extraction with the public yt-dlp API (`COOKIE_TEST_STEPS` cannot be built as stated) | Stop and route back to the plan (D-1463) |

## Decision Log

> [!NOTE]
> D-1460 to D-1469 are autonomous, made under Mat's hand-over (USER_EXPLICIT 2026-11-18: 'make the decisions always the recommenations'). Each brief keeps a do-nothing option. The M items:
>
> - **M-1 clear.** No push, tag or release. The release that ships the fix is Mat's.
> - **M-2 clear.** No user data or secret is read. Tests write their own made-up cookie files.
> - **M-4.** The reply of `POST /downloads/cookies/test` gains fields. The home's Wire row (triage D-1406) already calls for that; D-1463 only names them. The MCP input schema does not change.
> - **M-5.** D-1464, D-1465 and D-1466 choose user-visible texts and where they show; handed to the agent.
> - **M-6.** D-1461 (the home's Fallback row against upstream's source) and D-1467 (the grouping's `owns` list against the files the homes need); handed to the agent.
> - **M-7.** The assertions in §Pins that move change only by this plan's rows 7 and 11, which name each test and its new assertion.
> - **M-10.** Starting execution is Mat's (`plan_to_exec_gate: human`).
>
> Carried from the grouping §8 and not restated: D-1410 (four sessions, order 104, 103, 106, 105), D-1411 (Human-approved: Electron E2E on mini-air), D-1412 (tiers and `owns` lists; no lanes), D-1413 (**open, Mat's**: do drafts started before the scoping review stand), D-1414 (one pass to plan drafts). Triage D-1406 to D-1408 are read from `known-issues.yaml`. Execution decisions take D-1470 to D-1499.

```yaml
decision_log:
  - id: D-1460
    stage: planning
    question: "Which yt-dlp does the lock hold, and how is it held?"
    resolution: autonomous
    class: two-way
    mandatory: none
    chosen: "A: lock yt-dlp exactly 2026.11.23 with `uv lock --upgrade-package yt-dlp==2026.11.23`, and give packages/infrastructure/pyproject.toml the floor `yt-dlp>=2026.11.23`; yt-dlp-ejs stays `==0.8.0` (YTDLP_LOCK)."
    source_tag: Research-backed
    precedents:
      - "docs/build-plan/02-infrastructure.md §yt-dlp challenge solver (residual), Version row (triage D-1407)"
      - "D-640 (Mat, 2026-11-12): the dependency is yt-dlp plus yt-dlp-ejs at the version yt-dlp's default extra pins"
      - "uv.lock:3361-3375 and packages/infrastructure/pyproject.toml:12-13, read 2026-11-26"
    research:
      engine: github-api-and-pypi-json
      sources:
        - "github.com/yt-dlp/yt-dlp/issues/18123 — closed completed 2026-11-23; maintainer: 'Fixed in stable 2026.11.23'; read 2026-11-26"
        - "pypi.org/pypi/yt-dlp/2026.11.23/json — latest, not yanked, requires yt-dlp-ejs==0.8.0 for the default and pin extras; read 2026-11-26"
    reasoning: "Handed to the agent: USER_EXPLICIT 2026-11-18 'make the decisions always the recommenations'. Options: (A) lock 2026.11.23 and add a floor; (B) lock 2026.11.23 with no floor, as pyproject is today; (C) keep things as they are (2026.10.26). 2026.11.23 is the newest stable and the one upstream names as the fix; no later stable exists today. The floor costs one line and stops a later re-lock from going back below the fix; B leaves that to chance. C leaves signed-in extraction broken. Weakness of A: a third-party daily check (ytmini issue 6) still failed on 2026.11.23 today, so the release may not be the whole fix; D-1462 covers that. Two-way: one lock command."
  - id: D-1461
    stage: planning
    question: "When does the adapter pass `player_js_variant` `tv`?"
    resolution: autonomous
    class: two-way
    mandatory: M-6
    chosen: "A: never when the after-run is clean. When the after-run still shows challenge errors, only if the script's `variant=` line shows a variant other than `tv` (VARIANT_FALLBACK). The handoff records which of the two was needed."
    source_tag: Research-backed
    precedents:
      - "docs/build-plan/02-infrastructure.md §yt-dlp challenge solver (residual), Fallback row: 'If the new release still fails, the adapter passes the YouTube extractor argument player_js_variant tv'"
    research:
      engine: github-api
      sources:
        - "github.com/yt-dlp/yt-dlp/pull/18124 — merged 2026-11-23, +2/-2: _DEFAULT_PLAYER_JS_VARIANT 'main' becomes 'tv'; read 2026-11-26"
        - "yt_dlp/extractor/youtube/_video.py at tag 2026.11.23, lines 1885 and 2121: the default is 'tv', and the argument is read only to override it; read 2026-11-26"
    reasoning: "Handed to the agent: USER_EXPLICIT 2026-11-18 'make the decisions always the recommenations'. Options: (A) add the argument only when it can change something; (B) add it whenever the after-run fails, as the home's row reads; (C) keep things as they are (no argument, whatever the run says). At 2026.11.23 `tv` is already the default, so under B the argument changes nothing and the rerun would fail the same way, while the code would carry an argument that hides a later upstream default. A keeps the home's condition (the new release still fails) and adds one more (the variant in use was not tv), which the proof script prints. C would ignore the home's row in the one case where it helps. Source conflict (M-6): the home's row against upstream's source; handed. Two-way: one dict entry."
  - id: D-1462
    stage: planning
    question: "How is the real extraction recorded without touching a cookie, and what if it does not show 'errors before, none after'?"
    resolution: autonomous
    class: two-way
    mandatory: none
    chosen: "A: a plan-local script, proof-extract.py, runs the extraction with the cookie client list and no cookie option and prints only fixed outcome lines (PROOF_PAIR). The proof passes only on challenge-errors before and clean after. Any other pair, or a blocked run, leaves row 5c [B] with the receipts and the handoff says INCOMPLETE VERIFICATION; the lock change stays; MEU-169 and MEU-170 go on."
    source_tag: Local Canon
    precedents:
      - "docs/build-plan/02-infrastructure.md §yt-dlp challenge solver (residual), Proof row"
      - "D-464 A: a blocked run is not a pass"
      - "The session's secrets rule: no task reads a real cookie value, cookie file or browser profile content"
    research:
      engine: github-api
      sources:
        - "github.com/yt-dlp/ejs/issues/79 — closed 2026-11-25: 'the player depends on the account/cookie, not on the machine'; read 2026-11-26"
        - "github.com/dennissoftman/ytmini/issues/6 — open; its daily check failed again 2026-11-26 on yt-dlp 2026.11.23 with 'a.addOnDisposeCallback is not a function'; read 2026-11-26"
    reasoning: "Handed to the agent: USER_EXPLICIT 2026-11-18 'make the decisions always the recommenations'. Options: (A) a cookie-free script with a strict pair rule; (B) accept 'clean after' alone as the proof; (C) keep things as they are (no recorded extraction). The home asks for the cookie client list, not for cookies, so the script can keep the secrets rule. B would call the fix proved when the run before the change never showed the fault, which upstream says can happen because the bad player was served by account. C drops the home's Proof row. Weakness of A: the proof may end incomplete on this machine through no fault of the change; that is said plainly in the handoff, and Mat's own next signed-in use is then the evidence. Two-way: a script and two receipts."
  - id: D-1463
    stage: planning
    question: "What are the new reply fields called, what values do they take, and what does Mode None reply?"
    resolution: autonomous
    class: two-way
    mandatory: none
    chosen: "A: `outcome` with the values `ok`, `unreadable`, `check_failed`, and null for Mode None; `error_message` for the reason, the name the domain type already uses. `ok` is true for `ok` and for Mode None, as today (COOKIE_TEST_OUTCOME, COOKIE_TEST_WIRE). The adapter decides the outcome by where the failure happens (COOKIE_TEST_STEPS)."
    source_tag: Local Canon
    precedents:
      - "docs/build-plan/02-infrastructure.md §Cookie test outcome (residual), Outcome, Reason and Wire rows (triage D-1406)"
      - "packages/core/src/avkit_core/domain/download.py:429-438 — CookieTestResult.error_message"
      - "packages/infrastructure/src/avkit_infra/youtube/adapter.py:821-822 — Mode None returns ok=True with no probe"
      - "tests/e2e/test_api_downloads.py:294-312 — the pin that names error_message"
    research:
      engine: local-source-read
      sources:
        - ".venv yt_dlp/YoutubeDL.py:4219-4227 and cookies.py:112-113 — the cookie jar loads lazily on first use and reports a load failure there; read 2026-11-26"
    reasoning: "Handed to the agent: USER_EXPLICIT 2026-11-18 'make the decisions always the recommenations'. Options: (A) `outcome` plus `error_message`, null outcome for Mode None; (B) `outcome` plus a new name `reason`, and a fourth value `not_tested` for Mode None; (C) keep things as they are (the reply holds `ok` only). The home says three outcomes, so a fourth value would widen it; null says 'no test ran' without one. `error_message` is already the domain's name and the name the existing pin uses, so A adds one new word to the API and B adds two. Deciding by the step that failed needs no matching of yt-dlp's message texts, which change between releases. C leaves the user's report unanswered. M-4 considered: the home's Wire row already calls for the new fields, so the shape change is not new here; the names can still change before the next release. Weakness of A: `ok: true` for Mode None reads oddly beside 'true only for the first outcome'; the panel text for null says that nothing was tested. Two-way: additive fields."
  - id: D-1464
    stage: planning
    question: "Where and how does the panel show the result and the busy state?"
    resolution: autonomous
    class: two-way
    mandatory: M-5
    chosen: "A: a `cookie-test-result` element in the Test Cookies row, absent until a test has finished, with the four texts of COOKIE_TEST_SHOWN and the classes of `sabr-status`; the button uses the Button component's `loading` while the request is pending (COOKIE_TEST_BUSY); an API error keeps going to the page banner."
    source_tag: Local Canon
    precedents:
      - "docs/build-plan/02-infrastructure.md §Cookie test outcome (residual), Shown row: beside Test Cookies, in words and not by colour alone; disabled and busy while it runs"
      - "ui/src/renderer/src/components/ui/Button.tsx:66-67 — `loading` disables the button and sets aria-busy"
      - "ui/tests/e2e/downloader-advanced-gap.test.ts — the eight Advanced ids, their order, the tail and the 16 px gap; it reads every data-testid in the panel"
      - ".agent/docs/emerging-standards.md G15, G35, E2"
    research: { engine: none, sources: [] }
    reasoning: "Handed to the agent: USER_EXPLICIT 2026-11-18 'make the decisions always the recommenations'. Options: (A) a line beside the button, absent until used; (B) put the result in the page's status slot under the form; (C) keep things as they are (no result shown). The home says 'beside Test Cookies'. An element that is absent until a test has run leaves the gap test's id list and geometry untouched, so Session 105 inherits the panel it planned against. B would put a cookie result where add results go, and the gap test notes that nothing clears a message there. C is the reported fault. Weakness of A: a long reason can wrap the row; the E2E measures the gap with a result shown. User-visible wording with no canon text (M-5); handed. Two-way: one element and one helper."
  - id: D-1465
    stage: planning
    question: "Does Check SABR also probe with the saved cookies, or does it stay cookie-free and say so?"
    resolution: autonomous
    class: two-way
    mandatory: M-5
    chosen: "B: Check SABR stays as it is, without cookies, and the SABR status says what the check covers (SABR_CHECK_SCOPE)."
    source_tag: Research-backed
    precedents:
      - "docs/build-plan/02-infrastructure.md §SABR check and cookies (residual), Choice, Said and Kept rows (triage D-1408)"
      - "packages/infrastructure/src/avkit_infra/youtube/adapter.py:798-810 — check_sabr_status uses SABR_EXTRACTOR_ARGS and no cookie option"
      - "packages/core/src/avkit_core/services/download.py:774-779 — a download that meets SABR sets the status itself, in any cookie mode"
    research:
      engine: github-api-and-readme
      sources:
        - "yt-dlp README at tag 2026.11.23, YouTube extractor arguments: with logged-in cookies the default clients are tv_samsung, web_embedded, web (free) or web_creator, tv_samsung, web (premium); 'Not all clients support authentication via cookies'; read 2026-11-26"
        - "github.com/yt-dlp/yt-dlp/issues/12482 — open since 2025-02-26: web has only SABR formats; reports differ by account; read 2026-11-26"
        - "github.com/yt-dlp/yt-dlp/issues/17666 — open: mweb and web_embedded SABR-only in some signed-in sessions and fine without cookies; read 2026-11-26"
    reasoning: "Handed to the agent: USER_EXPLICIT 2026-11-18 'make the decisions always the recommenations'. Options: (A) the check also probes with the saved cookies and the cookie clients; (B) the check stays cookie-free and the status says what it covers; (C) keep things as they are. The research says a signed-in session does get other clients, players and formats, so a cookie-free check cannot speak for a signed-in download; that supports saying so, not hiding it. A would read the user's cookie source on every check: a locked browser database would fail the check, the check would take on Test Cookies' job, 'Inactive' would mean two different things by cookie mode, and the clients the check uses today (android, ios) take no cookies. A signed-in download already detects SABR itself and sets the status. C leaves the misreading Mat reported. Weakness of B: the user still has no single 'will my signed-in download be limited' answer before downloading; Test Cookies plus the first download give it. User-visible fork with no canon (M-5); handed. Two-way: one text."
  - id: D-1466
    stage: planning
    question: "What exactly does the SABR status say, and on which results?"
    resolution: autonomous
    class: two-way
    mandatory: M-5
    chosen: "A: the clause ` · Check SABR does not use cookies` at the end of the two detected texts (Active and Inactive); the not-checked, checking, forced and cleared texts are unchanged."
    source_tag: Local Canon
    precedents:
      - "ui/src/renderer/src/features/downloader/sabr-panel.ts:21-31 — the ten texts; ui/tests/unit/sabr-panel.test.ts AC-138.8"
      - "docs/build-plan/02-infrastructure.md §SABR check and cookies (residual), Said row: the status says what the check measured"
      - "packages/core/src/avkit_core/services/download.py:774-779 — `source: detected` is also written by a download"
    research: { engine: none, sources: [] }
    reasoning: "Handed to the agent: USER_EXPLICIT 2026-11-18 'make the decisions always the recommenations'. Options: (A) a clause about the check on detected results; (B) change `checked` to `checked without cookies`; (C) keep things as they are (no clause; the choice of D-1465 then has no text). B would be false when a signed-in download wrote the detected status, because the reply cannot tell the two apart. A is a statement about Check SABR, true whoever wrote the status, and it sits on exactly the results Mat misread. A forced or cleared status is the user's own action and needs no clause. Weakness of A: the line is longer and may wrap in a narrow window; the E2E reads it on mini-air. Two-way: one string constant."
  - id: D-1467
    stage: planning
    question: "The homes need files that the grouping's `owns` list for this session does not name. Does the plan change them?"
    resolution: autonomous
    class: two-way
    mandatory: M-6
    chosen: "A: yes. The plan lists each such path in §Lane Ownership with its reason, and row 0 checks that no other open plan folder names them; the grouping file is not edited by this plan."
    source_tag: Local Canon
    precedents:
      - "Grouping §4: a planner writes only inside its plan folder; D-1412: execution is one session at a time on main"
      - "docs/build-plan/02-infrastructure.md §Cookie test outcome (residual), Outcome and Tests rows: the outcome and its tests need the domain type and the test files"
    research: { engine: none, sources: [] }
    reasoning: "Handed to the agent: USER_EXPLICIT 2026-11-18 'make the decisions always the recommenations'. Options: (A) list the extra paths and go on; (B) hold the plan until the grouping's list is amended; (C) keep things as they are and change only listed paths. C cannot deliver the Outcome row (the domain type is not listed) or any test. B stops a plan for a list that names no test file for any session, so the gap is the list's convention and not a clash. None of the extra product paths is in another session's list as read today; the shared register files are closeout files for every session. Source conflict (M-6): the list against the homes; handed, and reported to the orchestrator. Two-way: a table in the plan."
  - id: D-1468
    stage: planning
    question: "The repository holds new releases for 7 days, and 2026.11.23 is 3 days old. How does the lock take it?"
    resolution: autonomous
    class: two-way
    mandatory: none
    chosen: "A: follow the dependency page. If `uv lock --upgrade-package yt-dlp==2026.11.23` refuses the release because of the hold, add `exclude-newer-package = { yt-dlp = false }` under `[tool.uv]` in the root pyproject.toml and lock again (HOLD_OVERRIDE). If execution starts after the hold has ended, no line is added. The handoff and the next session's prompt carry the follow-up: remove the line and run `uv lock` once the release is 7 days old."
    source_tag: Local Canon
    precedents:
      - "docs/distribution/dependency-updates.md §The 7-day hold: 'yt-dlp can skip the hold. YouTube changes can break downloads overnight, and the fix is usually a new yt-dlp.'"
      - "pyproject.toml:12 — exclude-newer = \"7 days\"; uv.lock:9-11 — the hold recorded in the lock's options"
    research:
      engine: pypi-json
      sources:
        - "pypi.org/pypi/yt-dlp/2026.11.23/json — uploaded 2026-11-23; read 2026-11-26"
    reasoning: "Handed to the agent: USER_EXPLICIT 2026-11-18 'make the decisions always the recommenations'. Options: (A) the documented yt-dlp line, when the hold is still on; (B) wait until 2026-11-30 and lock with no line; (C) keep things as they are (2026.10.26). The dependency page names this exact case and gives the line, and it warns against passing the override on the command line because `uv lock --check` then fails in CI. B leaves signed-in downloads broken for the days that the page's exception exists to save, though it becomes A's no-line branch by itself if execution starts late. C is D-1460's do-nothing. Weakness of A: the line must be removed later, and nothing in the repository enforces that; the follow-up is written into the handoff, the issue's resolution text and the next prompt. The root pyproject.toml is not in the grouping's list for this session (D-1467). Two-way: one line."
  - id: D-1469
    stage: planning
    question: "Electron runs only on mini-air and the tool runs the whole suite. How are the two new Electron tests shown to fail before the renderer changes?"
    resolution: autonomous
    class: two-way
    mandatory: none
    chosen: "A: a second mini-air run. Rows 11a and 11b send a snapshot taken after the tests are written and before any renderer file changes; the row passes only when the tool says new-failures (exit 40) and the new list holds only the new spec's titles, each failed by an assertion. Rows 15 to 17 are the run after Green."
    source_tag: Local Canon
    precedents:
      - "AGENTS §Testing & TDD: 'FIC → all AC tests → intended Red → Green'; 'save decisive Red output, not unrelated setup/import failure'"
      - "Grouping D-1411 (Human-approved): Electron E2E runs on mini-air during execution"
      - "tools/e2e_remote.py: its `run` command takes a commit and no spec filter; `.agent/docs/e2e-remote-host.md`: exit 40 names each new failure"
    research: { engine: none, sources: [] }
    reasoning: "Handed to the agent: USER_EXPLICIT 2026-11-18 'make the decisions always the recommenations'. Options: (A) a Red run on mini-air, about 40 more minutes of host time; (B) no Red run for the two Electron tests: their Red is taken from the unit tests of the same texts, and the spec first runs after Green; (C) keep things as they are, the Red on the dev PC as before D-1411, which Mat's word on mini-air rules out. Under B a spec that passes for a wrong reason (a route that never matches, a selector that finds another element) would not be seen, and the contract asks for a saved Red for every AC test. A costs host time only; the four sessions run one at a time, so the host is free. Weakness of A: the run can meet host-busy or host-locked and wait (S10), and an exit 40 has to be read as the expected result in row 11b only. Two-way: one extra run."
  - id: D-1470
    stage: execution
    question: "Which other plan folders does the identity and scope check treat as another session's files?"
    resolution: autonomous
    class: two-way
    mandatory: none
    chosen: "A: OTHER_PLAN matches the plan folders dated 2026-11-16 to 2026-11-26, the open sessions' folders on main at row 0."
    source_tag: Local Canon
    precedents:
      - "identity.py header and row-check.py OTHER_PLAN; the grouping file lists the sessions of 2026-11-26"
    research: { engine: none, sources: [] }
    reasoning: "Handed to the agent: USER_EXPLICIT 2026-11-26 'drafts stand, go for 104 after the reviews finish and then execute rest as you see fit. Use HDP for decisions and pick recommendations'. Options: (A) a dated range that covers every open plan folder; (B) name each folder; (C) do nothing and count them as this session's changes, which fails S4 on files this session never touched. A misses nothing that git status showed at row 0. Weakness: a plan folder created after row 0 with a later date is not covered and would stop the row (S4), which is the safe side. Two-way: one pattern."
  - id: D-1471
    stage: execution
    question: "Does a citation of this plan's slug or the range end in another file count as a use of the free ids D-1460 to D-1499?"
    resolution: autonomous
    class: two-way
    mandatory: none
    chosen: "A: the free-id check reads its own files and ignores a line that only names the range end or cites this plan by its slug."
    source_tag: Local Canon
    precedents:
      - "baseline.ps1 lines 13-15 and 274-277; the first baseline (ycc-baseline-r1.txt) refused on the plan review handoff, which quotes this plan"
    research: { engine: none, sources: [] }
    reasoning: "Handed to the agent: USER_EXPLICIT 2026-11-26 'drafts stand, go for 104 ...'. Options: (A) skip citations of this plan; (B) edit the review handoff, which is another record; (C) do nothing and stop at S2 on a quotation. A keeps S2 for real reuse of the ids. Weakness: a line that cites the slug and also reuses an id would pass; none existed at row 0. Two-way."
  - id: D-1472
    stage: execution
    question: "What does the session gate's scope check bind: HEAD or the files' content?"
    resolution: autonomous
    class: two-way
    mandatory: none
    chosen: "A: scope-paths binds content (hashes against the row 0 copies), not HEAD, so another session's commit on main does not move this session's scope."
    source_tag: Local Canon
    precedents:
      - "session-gate.ps1 line 16; memory rule: parallel sessions share main"
    research: { engine: none, sources: [] }
    reasoning: "Handed to the agent: USER_EXPLICIT 2026-11-26 'drafts stand, go for 104 ...'. Options: (A) content; (B) HEAD; (C) do nothing. B fails whenever another session commits; A checks the bytes this session owns. Weakness: a file that another session changes back to its row 0 bytes is not seen as changed. Two-way."
  - id: D-1473
    stage: execution
    question: "Which distributions may the lock check let change?"
    resolution: autonomous
    class: two-way
    mandatory: none
    chosen: "A: NAMED_DISTRIBUTIONS is yt-dlp and yt-dlp-ejs; any other changed package is S7."
    source_tag: Local Canon
    precedents:
      - "identity.py; AC-168.1 names yt-dlp 2026.11.23 and yt-dlp-ejs 0.8.0"
    research: { engine: none, sources: [] }
    reasoning: "Handed to the agent: USER_EXPLICIT 2026-11-26 'drafts stand, go for 104 ...'. Options: (A) the two the AC names; (B) yt-dlp only, which refuses the ejs pin the AC requires; (C) do nothing. Weakness: none found. Two-way."
  - id: D-1474
    stage: execution
    question: "How are the row commands in row-run.ps1 kept equal to task.md?"
    resolution: autonomous
    class: two-way
    mandatory: none
    chosen: "A: row-run.ps1 is generated by `row-check.py steps --emit`, and `row-check.py steps` proves the two equal."
    source_tag: Local Canon
    precedents:
      - "row-run.ps1 line 13"
    research: { engine: none, sources: [] }
    reasoning: "Handed to the agent: USER_EXPLICIT 2026-11-26 'drafts stand, go for 104 ...'. Options: (A) generate and prove; (B) hand-write; (C) do nothing and run steps one by one. A removes copying errors. Weakness: a task.md cell the parser misreads is copied faithfully; the steps check shows it. Two-way."
  - id: D-1475
    stage: execution
    question: "How is the kept SABR source pinned?"
    resolution: autonomous
    class: two-way
    mandatory: none
    chosen: "A: the kept check compares each named member's source (SABR_PHRASES, SABR_EXTRACTOR_ARGS, sabr_phrase, check_sabr_status, check_sabr, force_sabr, clear_sabr) with its row 0 copy, member by member."
    source_tag: Local Canon
    precedents:
      - "task.md row 14; SABR_KEPT"
    research: { engine: none, sources: [] }
    reasoning: "Handed to the agent: USER_EXPLICIT 2026-11-26 'drafts stand, go for 104 ...'. Options: (A) per member; (B) whole files, which fail on the planned cookie-test edits in the same files; (C) do nothing. Weakness: a change outside the named members is not seen by this check; the pins check of row 14 covers the tests. Two-way."
  - id: D-1476
    stage: execution
    question: "triage-output.yaml is in the CRLF list, but row 19 writes only known-issues.md and triage-output.yaml is another session's dirty file. Is it kept in the list?"
    resolution: autonomous
    class: two-way
    mandatory: none
    chosen: "A: crlf.py drops triage-output.yaml from its list."
    source_tag: Local Canon
    precedents:
      - "crlf.py lines 2-3; git status at row 0 shows triage-output.yaml modified by another session"
    research: { engine: none, sources: [] }
    reasoning: "Handed to the agent: USER_EXPLICIT 2026-11-26 'drafts stand, go for 104 ...'. Options: (A) drop it; (B) keep it and check another session's file; (C) do nothing. A checks only what this session writes. Weakness: none. Two-way."
  - id: D-1477
    stage: execution
    question: "How does scope-paths treat other sessions' artifacts in the dirty tree?"
    resolution: autonomous
    class: two-way
    mandatory: none
    chosen: "A: a path that matches OTHER_PLAN or another session's artifact pattern, or whose content equals its row 0 copy, is a note and not a problem."
    source_tag: Local Canon
    precedents:
      - "row-check.py line 712; ycc-row11a-paths.txt: 69 changed, 54 in scope, 15 notes, 0 problems"
    research: { engine: none, sources: [] }
    reasoning: "Handed to the agent: USER_EXPLICIT 2026-11-26 'drafts stand, go for 104 ...'. Options: (A) notes; (B) problems, which stop every row on the shared tree; (C) do nothing. Weakness: a note is not checked further; the snapshot takes only §Files Modified paths. Two-way."
  - id: D-1478
    stage: execution
    question: "How does the proof script find Deno?"
    resolution: autonomous
    class: two-way
    mandatory: none
    chosen: "A: the way the app resolves it with no setting: `JsRuntimeLocator(None, DENO_BUNDLE)`."
    source_tag: Local Canon
    precedents:
      - "proof-extract.py line 5"
    research: { engine: none, sources: [] }
    reasoning: "Handed to the agent: USER_EXPLICIT 2026-11-26 'drafts stand, go for 104 ...'. Options: (A) the app's locator; (B) PATH; (C) do nothing. A proves what the app runs. Weakness: none. Two-way."
  - id: D-1479
    stage: execution
    question: "When a proof run meets both a block and a challenge error, which verdict wins?"
    resolution: autonomous
    class: two-way
    mandatory: none
    chosen: "A: `blocked` first (network error, HTTP 429, bot check), then challenge-errors, then clean."
    source_tag: Local Canon
    precedents:
      - "proof-extract.py line 13; S8"
    research: { engine: none, sources: [] }
    reasoning: "Handed to the agent: USER_EXPLICIT 2026-11-26 'drafts stand, go for 104 ...'. Options: (A) blocked first; (B) challenge first; (C) do nothing. A never calls a blocked run clean or failed. Weakness: a run with both is not counted as evidence for the pair. Two-way."
  - id: D-1480
    stage: execution
    question: "Which paths does the snapshot take?"
    resolution: autonomous
    class: two-way
    mandatory: none
    chosen: "A: snapshot-paths takes the code, test and lock paths of §Files Modified only; plan and register files stay out."
    source_tag: Local Canon
    precedents:
      - "task.md rows 11a and 15; ycc-row11a-paths.txt"
    research: { engine: none, sources: [] }
    reasoning: "Handed to the agent: USER_EXPLICIT 2026-11-26 'drafts stand, go for 104 ...'. Options: (A) code, test and lock; (B) every changed path, which ships other sessions' files to mini-air; (C) do nothing. Weakness: none. Two-way."
  - id: D-1481
    stage: execution
    question: "When are the canon-edit texts written?"
    resolution: autonomous
    class: two-way
    mandatory: none
    chosen: "A: canon-edit.py's texts are written at row 18 from §Spec, not at row 0."
    source_tag: Local Canon
    precedents:
      - "canon-edit.py lines 1 and 24"
    research: { engine: none, sources: [] }
    reasoning: "Handed to the agent: USER_EXPLICIT 2026-11-26 'drafts stand, go for 104 ...'. Options: (A) at row 18; (B) at row 0; (C) do nothing. A writes the canon from the shipped result. Weakness: none. Two-way."
  - id: D-1482
    stage: execution
    question: "How does scope-paths prove that no tag was added or moved?"
    resolution: autonomous
    class: two-way
    mandatory: none
    chosen: "A: row 0 writes baseline-tags.txt, and scope-paths compares `git tag` with it."
    source_tag: Local Canon
    precedents:
      - "row-check.py line 735"
    research: { engine: none, sources: [] }
    reasoning: "Handed to the agent: USER_EXPLICIT 2026-11-26 'drafts stand, go for 104 ...'. Options: (A) a baseline file; (B) read git history; (C) do nothing. Weakness: none. Two-way."
  - id: D-1483
    stage: execution
    question: "What does a step that a row skips leave behind?"
    resolution: autonomous
    class: two-way
    mandatory: none
    chosen: "A: a skipped step writes its receipt with the reason and a `.exit` of 0."
    source_tag: Local Canon
    precedents:
      - "row-run.ps1 line 9; rows 5a and 5b: not-needed"
    research: { engine: none, sources: [] }
    reasoning: "Handed to the agent: USER_EXPLICIT 2026-11-26 'drafts stand, go for 104 ...'. Options: (A) a receipt with the reason; (B) no receipt; (C) do nothing. A leaves every step with evidence. Weakness: a 0 exit must be read with its reason line. Two-way."
  - id: D-1484
    stage: execution
    question: "Does the baseline run uv sync, and is a host-load reading fatal?"
    resolution: autonomous
    class: two-way
    mandatory: none
    chosen: "A: the baseline skips uv sync (the lock must not move before row 1), and the host-load reading is recorded and not fatal."
    source_tag: Local Canon
    precedents:
      - "task.md row 1: the before-run needs yt-dlp 2026.10.26 still installed"
    research: { engine: none, sources: [] }
    reasoning: "Handed to the agent: USER_EXPLICIT 2026-11-26 'drafts stand, go for 104 ...'. Options: (A) skip sync, record load; (B) sync and fail on load; (C) do nothing. B could move the installed version before the before-run. Weakness: none. Two-way."
  - id: D-1485
    stage: execution
    question: "How does a row stop when the S4 pre-check finds an out-of-scope change?"
    resolution: autonomous
    class: two-way
    mandatory: none
    chosen: "A: the pre-check writes R/ycc-row<N>-s4.txt, and a non-zero exit stops the row with exit 3 before any step."
    source_tag: Local Canon
    precedents:
      - "row-run.ps1 line 11"
    research: { engine: none, sources: [] }
    reasoning: "Handed to the agent: USER_EXPLICIT 2026-11-26 'drafts stand, go for 104 ...'. Options: (A) its own exit before any step; (B) run the steps and report later; (C) do nothing. Weakness: none. Two-way."
  - id: D-1486
    stage: execution
    question: "How does the TypeScript pins-moved check read a moved assertion?"
    resolution: autonomous
    class: two-way
    mandatory: none
    chosen: "A: it checks the new-side lines of each changed hunk: every inserted line holds the clause, and nothing else changed."
    source_tag: Local Canon
    precedents:
      - "M-7 (Mat's word): the six moved assertions of rows 7 and 11; ycc-row11 pins-moved: 0 problems"
    research: { engine: none, sources: [] }
    reasoning: "Handed to the agent: USER_EXPLICIT 2026-11-26 'drafts stand, go for 104 ...'. Options: (A) new-side lines; (B) whole tests; (C) do nothing. A lets only the approved clause move. Weakness: a moved pin must stay on one line. Two-way."
  - id: D-1487
    stage: execution
    question: "How does the step parser read a bare PLAN token?"
    resolution: autonomous
    class: two-way
    mandatory: none
    chosen: "A: `_expand` expands a bare PLAN as well as PLAN/ prefixes."
    source_tag: Local Canon
    precedents:
      - "row-check.py line 372"
    research: { engine: none, sources: [] }
    reasoning: "Handed to the agent: USER_EXPLICIT 2026-11-26 'drafts stand, go for 104 ...'. Options: (A) expand it; (B) edit the task cells; (C) do nothing. Weakness: none. Two-way."
  - id: D-1488
    stage: execution
    question: "What does row-run do for a row with no steps?"
    resolution: autonomous
    class: two-way
    mandatory: none
    chosen: "A: it exits 2 with the row named."
    source_tag: Local Canon
    precedents:
      - "row-run.ps1 line 196"
    research: { engine: none, sources: [] }
    reasoning: "Handed to the agent: USER_EXPLICIT 2026-11-26 'drafts stand, go for 104 ...'. Options: (A) exit 2; (B) exit 0, which passes a mistyped row; (C) do nothing. Weakness: none. Two-way."
  - id: D-1489
    stage: execution
    question: "rtk prints its own banner into a receipt. Does the proof-recorded check count it?"
    resolution: autonomous
    class: two-way
    mandatory: none
    chosen: "A: proof-recorded ignores the rtk banner; it is the harness, not a proof line."
    source_tag: Local Canon
    precedents:
      - "row-check.py line 838"
    research: { engine: none, sources: [] }
    reasoning: "Handed to the agent: USER_EXPLICIT 2026-11-26 'drafts stand, go for 104 ...'. Options: (A) ignore it; (B) run the proof without rtk, against the RTK contract; (C) do nothing. Weakness: none. Two-way."
  - id: D-1490
    stage: execution
    question: "Did the 7-day hold refuse 2026.11.23 at row 3?"
    resolution: autonomous
    class: two-way
    mandatory: none
    chosen: "A: yes. uv's exclude-newer refused it, so D-1468's HOLD_OVERRIDE line was added (ycc-hold.txt: yes); the follow-up is to remove it and run `uv lock` once the release is 7 days old (2026-11-30)."
    source_tag: Local Canon
    precedents:
      - "D-1468; ycc-row3 receipts"
    research: { engine: none, sources: [] }
    reasoning: "Handed to the agent: USER_EXPLICIT 2026-11-26 'drafts stand, go for 104 ...'. This is D-1468's branch A as planned. Options: (A) add the line; (B) wait until 2026-11-30; (C) do nothing. Weakness: the line must be removed later. Two-way."
  - id: D-1491
    stage: execution
    question: "How does the cookie test load the jar apart from the extraction (S12)?"
    resolution: autonomous
    class: two-way
    mandatory: none
    chosen: "A: the adapter loads the jar with yt-dlp's public `load_cookies` into `ydl.cookiejar`; a failure there is `unreadable`, a later failure is `check_failed`."
    source_tag: Research-backed
    precedents:
      - "COOKIE_TEST_STEPS; yt_dlp.cookies.load_cookies"
    research: { engine: none, sources: [] }
    reasoning: "Handed to the agent: USER_EXPLICIT 2026-11-26 'drafts stand, go for 104 ...'. Options: (A) load_cookies; (B) a private yt-dlp helper; (C) do nothing, and S12 stops the session. A is public API, so S12 did not trigger. Weakness: load_cookies is untyped (D-1497). Two-way."
  - id: D-1492
    stage: execution
    question: "A comment in session-gate.ps1 no longer matched the script. Is it reworded?"
    resolution: autonomous
    class: two-way
    mandatory: none
    chosen: "A: the comment is reworded; no behavior changes."
    source_tag: Local Canon
    precedents:
      - "session-gate.ps1 header"
    research: { engine: none, sources: [] }
    reasoning: "Handed to the agent: USER_EXPLICIT 2026-11-26 'drafts stand, go for 104 ...'. Options: (A) reword; (B) do nothing. Weakness: none. Two-way."
  - id: D-1493
    stage: execution
    question: "How is it shown that the browser-mode test never reads a real browser profile?"
    resolution: autonomous
    class: two-way
    mandatory: none
    chosen: "A: the fake YoutubeDL fails at its YDLLogger before any cookie read, and the browser-probe receipt shows no browser cookie reader was reached (ycc-row8-browser-probe.txt: `browser-probe: hits=[] pytest=0`)."
    source_tag: Local Canon
    precedents:
      - "Plan rule: no row reads, prints, copies or dispatches a real cookie value, a cookie file or browser profile content"
    research: { engine: none, sources: [] }
    reasoning: "Handed to the agent: USER_EXPLICIT 2026-11-26 'drafts stand, go for 104 ...'. Options: (A) fail first and record it; (B) patch the browser reader; (C) do nothing. Weakness: the proof rests on the fake's order. Two-way."
  - id: D-1494
    stage: execution
    question: "The route docstring says 'Probe cookies and return `ok` only.' Changing it moves the OpenAPI paths that row 9 freezes. Is it changed?"
    resolution: autonomous
    class: two-way
    mandatory: none
    chosen: "A: keep the docstring, so the paths stay equal; its 'ok only' wording is stale and stays an open item for the next OpenAPI change."
    source_tag: Local Canon
    precedents:
      - "row 9: only the schemas CookieTestOut and CookieTestOutcome change"
    research: { engine: none, sources: [] }
    reasoning: "Handed to the agent: USER_EXPLICIT 2026-11-26 'drafts stand, go for 104 ...'. Options: (A) keep it; (B) change it and break row 9's rule; (C) do nothing (same as A). Weakness: the OpenAPI description understates the reply. Two-way."
  - id: D-1495
    stage: execution
    question: "Does the schema define its own outcome enum?"
    resolution: autonomous
    class: two-way
    mandatory: none
    chosen: "A: the schema uses the domain enum, which OpenAPI shows as the CookieTestOutcome component."
    source_tag: Local Canon
    precedents:
      - "packages/core domain enums; ycc-row9: schemas changed ['CookieTestOut', 'CookieTestOutcome']"
    research: { engine: none, sources: [] }
    reasoning: "Handed to the agent: USER_EXPLICIT 2026-11-26 'drafts stand, go for 104 ...'. Options: (A) the domain enum; (B) a Literal in the schema; (C) do nothing. A keeps one source. Weakness: none. Two-way."
  - id: D-1496
    stage: execution
    question: "Where is the reply for a test that raises with no outcome defined?"
    resolution: autonomous
    class: two-way
    mandatory: none
    chosen: "A: COOKIE_TEST_FALLBACK is defined once, in the service."
    source_tag: Local Canon
    precedents:
      - "packages/core/src/avkit_core/services/download.py"
    research: { engine: none, sources: [] }
    reasoning: "Handed to the agent: USER_EXPLICIT 2026-11-26 'drafts stand, go for 104 ...'. Options: (A) the service; (B) the route; (C) do nothing. Weakness: none. Two-way."
  - id: D-1497
    stage: execution
    question: "pyright rejects the untyped load_cookies arguments. How is it typed?"
    resolution: autonomous
    class: two-way
    mandatory: none
    chosen: "A: `cast(Any, ...)` on the load_cookies arguments, with no ignore comment."
    source_tag: Local Canon
    precedents:
      - "adapter.py; ycc-row8 typecheck clean"
    research: { engine: none, sources: [] }
    reasoning: "Handed to the agent: USER_EXPLICIT 2026-11-26 'drafts stand, go for 104 ...'. Options: (A) cast; (B) a type: ignore; (C) do nothing and fail the gate. Weakness: none. Two-way."
  - id: D-1498
    stage: execution
    question: "How do the row 11 tests route, time out and sit in their files?"
    resolution: autonomous
    class: two-way
    mandatory: none
    chosen: "A: the Electron spec routes with `page.route`, as this repo's Electron specs do, and also routes GET /downloads/sabr because the panel reads it after the check; each test calls `test.setTimeout(240_000)` like downloader-advanced-gap, so a slow launch cannot give 'Test timeout of' at Red; the behavior test's MEU-169 describe is appended at the end of the file with its comment inside, so no line is counted in an existing block."
    source_tag: Local Canon
    precedents:
      - "ui/tests/e2e/downloader-advanced-gap.test.ts; ycc-row11: all steps exit 0, pins-moved 0 problems"
    research: { engine: none, sources: [] }
    reasoning: "Handed to the agent: USER_EXPLICIT 2026-11-26 'drafts stand, go for 104 ...'. Options: (A) as chosen; (B) context.route and the default timeout; (C) do nothing. Under B a Red could fail by a timeout, which e2e-red refuses. Weakness: the spec's per-test timeout is the sibling's, not shorter. Two-way."
  - id: D-1499
    stage: execution
    question: "Mini-air is unreachable at row 11a.4 (exit 10 ssh-failed; ping gets no answer), and row 12's Test Cookies button needs a pending state. How does the session go on, and which state does the button use?"
    resolution: autonomous
    class: two-way
    mandatory: none
    chosen: "A: the Red snapshot 88f00345db0802e048d2b5d00970281704ed2e5f is built and --verify-bound, so its Red run is taken later against that commit. Rows 12, 13 and 14 run now, out of their depends_on order on 11b. When mini-air answers, row 11a's first-attempt receipts are renamed -r1 and only its host step (`tools/e2e_remote.py check`) is taken again, because `snapshot-paths --stage red` would now refuse the Green files; 11a is marked [x] citing the original snapshot receipts and the new check; then 11b against 88f00345, then rows 15 to 17. Rows 15 onward never run without mini-air. The MEU-169 and MEU-170 handoffs note the deviation. Row 12: `cookie-test-btn` takes its `loading` prop from `cookieTesting`, a state of its own set from the click until the request settles, not the shared `busy`, a reply that arrives after the result was cleared is dropped, and a reply with no body (a 204 from an older test's stub) shows no line."
    source_tag: Local Canon
    precedents:
      - "ycc-row11a-host.txt: 'refused: ssh-failed: scp: Connection closed'; ycc-row11a-verify.txt: bound"
      - "D-1469: the Red run is taken on a snapshot made before any renderer change; the commit keeps that property whenever it runs"
      - "AC-53.2: a click right after a cookie setting persists must still act, which the shared busy would block"
    research: { engine: none, sources: [] }
    reasoning: "Handed to the agent: USER_EXPLICIT 2026-11-26 'drafts stand, go for 104 after the reviews finish and then execute rest as you see fit. Use HDP for decisions and pick recommendations as expect and do not stop for human decisions on techincal metters that are settled as primary recommendation for any of the 4 executions.' Coordinator decision; M criteria read: none hit, it changes no assertion and no interface, and is reversible. Options: (A) as chosen; (B) stop at 11a until mini-air answers; (C) do nothing. B idles the session while the Red commit is already fixed; the Red evidence is the same whenever the run is taken, because it runs on that commit and not on the working tree. For the button, the shared busy would disable Test Cookies while a setting persists. Weakness of A: Green is written before its Electron Red is seen, so a wrong-reason pass of the spec is found only at 11b, after Green; the unit Red of row 11 covers the same texts. Two-way."
  - id: D-1600
    stage: execution
    question: "The H1-2 gate's py-tests fails at tests/e2e/test_api_capture_shapes.py::test_ac_106_5_openapi_snapshot_and_delta: Session 72's openapi-delta.py pins the whole OpenAPI document against 5db3623, and AC-169.5 and AC-169.6 change CookieTestOut and add CookieTestOutcome. How does the gate pass?"
    resolution: autonomous
    class: two-way
    mandatory: [M-7, M-8]
    chosen: "A: a narrow exemption in docs/execution/plans/2026-11-14-capture-shapes-steps/openapi-delta.py (COOKIE_TEST_SHAPES): CookieTestOut and CookieTestOutcome must be either both the base's or both exactly this session's committed shapes, and are set back to the base's before the compare, as the rc4 row-7 info.version exemption does; two selftest cases (this session's cookie shape passes, another cookie shape is refused); the path added to §Files Modified and to eol-check.py SCOPE as LF, with its row-0 copy taken from the unchanged file (the c0acc89 blob, sha256 ab68411e..., mtime 2026-11-21) after row 0; the H1-2 gate rerun, run 2's receipts kept as -r2."
    source_tag: Local Canon
    precedents:
      - "docs/execution/plans/2026-11-21-release-rc4/task.md row 7: the release info.version set back to the base's in the same script"
      - "ycc-D6-py-tests-r2.txt: '1 failed, 3357 passed'; the refusal: 'a change AC-106.5 doesn't name: /components/schemas/CookieTestOut/description'"
    research: { engine: none, sources: [] }
    reasoning: "Handed to the agent: USER_EXPLICIT 2026-11-26 'Use HDP for decisions and pick recommendations as expect and do not stop for human decisions on techincal metters that are settled as primary recommendation for any of the 4 executions.' Also Mat's standing instruction USER_EXPLICIT 2026-11-18 'If you do not believe you can make the decisions run HDP and take recommenations from that!', which covers M-hit items; and the rc4 precedent (2026-11-21-release-rc4 task.md row 7). Coordinator decision under that hand-over. Conflict: HDP section 6 lists M-7 (an assertion of another plan changes) outside a hand-over; Mat's explicit instruction is the source relied on, and Mat can overturn it with one line. Options: (A) as chosen; (B) leave CookieTestOut as it was, which drops AC-169.5 and AC-169.6; (C) do nothing, which sends the session to review with a failing gate. The id is D-1600, not D-1555: Session 106 reserves D-1540 to D-1599 and its row 0 checks that they appear nowhere outside its plan folder. Weakness: the scope grew after the plan review, and the row-0 copy of the delta script was made after row 0, from the file unchanged since 2026-11-21. Two-way."
```

## Research References

All read on 2026-11-26. Receipts under `C:/Temp/av-kit/2026-11-26-plans/s104/`.

| Source | What it says today |
|---|---|
| github.com/yt-dlp/yt-dlp/issues/18123 | Closed as completed 2026-11-23. Maintainer: "Fixed in stable 2026.11.23. Update your yt-dlp." The newest comment (2026-11-26) confirms the fix on 2026.11.23 |
| github.com/yt-dlp/yt-dlp/pull/18124 | Merged 2026-11-23 (`fa9a871`): `_DEFAULT_PLAYER_JS_VARIANT` goes from `'main'` to `'tv'`, plus the README |
| github.com/yt-dlp/yt-dlp/issues/18125 | Closed as a duplicate of 18123 |
| github.com/yt-dlp/ejs/issues/79 | Closed as completed 2026-11-25, no comments. The report says the failing player was served only to some accounts. yt-dlp-ejs is still 0.8.0 (no newer release) |
| pypi.org yt-dlp 2026.11.23 | Latest, not yanked; `requires_python >=3.11`; the `default` and `pin` extras require `yt-dlp-ejs==0.8.0`; wheel SHA-256 `e9188e0c559905f7ee05acc1ba0b6fb3f310e7565bf6dea5f62b5300e0775e35` |
| github.com/dennissoftman/ytmini/issues/6 | Still open. Its daily check failed again on 2026-11-26 with yt-dlp 2026.11.23, Deno 2.9.8 and player `b485e332`: `a.addOnDisposeCallback is not a function`. Whether that check uses the `tv` variant is not stated |
| yt-dlp 2026.11.23 changelog | Also: `web` taken out of the default clients for now (pull request 18131), a temporary signature-timestamp workaround (18126), an `ios_producer` client |
| yt-dlp README at 2026.11.23; issues 12482 and 17666 | Signed-in sessions get other default clients, and SABR-only results differ by account and by client (D-1465) |

## Planning receipts

All under `C:/Temp/av-kit/2026-11-26-plans/s104/`, read-only against the repository:

| Receipt | What it shows |
|---|---|
| `up-ytdlp-18123.json`, `up-ytdlp-18123-comments.json`, `up-ytdlp-18124.json`, `up-ytdlp-18124-pr.json`, `up-ytdlp-18125.json`, `up-ejs-79.json`, `up-ytmini-6.json` | The upstream pages as read |
| `up-pypi-ytdlp-2026.11.23.json`, `up-pypi-ejs.json`, `up-ytdlp-releases.json`, `up-ejs-releases.json`, `up-ytdlp-release-2026.11.23.md` | The release and its metadata |
| `up-ytdlp-video-2026.11.23.py`, `up-ytdlp-readme-2026.11.23.md`, `up-ytdlp-12482.json`, `up-ytdlp-17666.json`, `up-ytdlp-18131.json`, `up-ytdlp-18126.json`, `research-sabr-signed-in.json` | The variant default at the tag; the signed-in research |
| `meu-stats.txt` | `tools/meu_status.py stats`: 163 approved, 10 pending |
| `precedent-sweep.txt` | D-539, D-540, D-640 and the other precedents as the build plan and the register word them |
| `task-lint.txt` | `tools/lint_task_contract.py` on `task.md` |

**GUI compliance (create-plan Step 4A).** `docs/gui-element-reference.md`, `docs/gui-button-index.md`, `docs/gui-input-field-index.md`, `docs/gui-output-index.md` and `.agent/docs/gui-standards-enforcement.md` are absent: `gui-refs-not-shipped`, as the step provides. The emerging standards that are shipped were checked: G15 (AC-169.9's negative test), G35 (the feedback note under MEU-169) and E2 (AC-169.11 and AC-170.4, written and wired in row 11, run Red in row 11b and Green in row 16).

## Validation stage contract

| Stage | Checks | Where |
|---|---|---|
| Plan review | This plan and `task.md`, against Mat's report, the three homes in 02, 04 §Downloads, 06 §Downloader and the code reads above | `ycc-plan-2026-11-26-ytdlp-challenge-and-cookie-test` (dispatched by the orchestrator) |
| Row checks | Each row's validation command | `task.md` |
| Session gate | §Session gate | H1-2 |
| Execution review | The delta from `baseline.sha` in the §Files Modified paths, against AC-168.1 to AC-168.8, AC-169.1 to AC-169.12 and AC-170.1 to AC-170.5 | `ycc-execution-2026-11-26-ytdlp-challenge-and-cookie-test` |
