---
date: "2026-11-12"
review_mode: "plan"
target_plan: "docs/execution/plans/2026-11-12-youtube-client-runtime/implementation-plan.md"
verdict: "approved"
findings_count: 0
template_version: "2.2"
requested_verbosity: "standard"
agent: "codex-independent-reviewer"
loop_id: "s66-plan-canonical-2026-11-12-youtube-client-runtime"
round: 5
---

# Critical Review: 2026-11-12-youtube-client-runtime

> **Review Mode:** plan. **Verdict:** changes_required. **Intent achieved:** partial, assessed as a plan.

## Intent Anchor

Session 66 lets yt-dlp choose its own YouTube clients, with one retry on today's cookie pin, and gives yt-dlp a JavaScript runtime and its challenge solver in dev and in the installed app. A download's first attempt sets no `player_client` in any cookie mode; a client-side failure retries once with `tv`, `web_safari`, `web`, and the Console shows each failed attempt. A video selector at a fixed height falls back to `/best`. The add-time extract uses the download's cookie and client options. Deno ships in the Windows installer and is found the way ffmpeg is (the setting, the bundled file, PATH); yt-dlp gets it through `js_runtimes`, the solver scripts ship in the backend, and Health names the runtime or says none was found and what that costs.

## Scope

Reviewed the working-tree plan, task and five plan-local scripts; relevant adapter, core, API, UI, MCP and packaging producers; the cited build-plan sections and grouping; the two issues and MEUs by id; existing callers and test pins; and installed yt-dlp 2026.10.26 source and metadata. Applied PR-1 to PR-9, the Materiality Gate and Verdict Rule. Observed HEAD `055377999828ea759315fcdd8d6c7b488110b67c`. Implementation rows remain unchecked, and the new product files are absent. Claude Code/Anthropic authored the plan; this Codex reviewer did not.

Accepted the carried rulings and approved Sessions 50–65. D-640, D-641 and D-642 remain Mat's decisions; no option is selected by this report. D-643–D-654 were judged on their substance. Other sessions' dirty paths were excluded. No repository file was edited, no forbidden file was opened, and no network request, Deno executable, backend, MCP server, product suite, baseline/session gate, package manager or build was run. Read-only probes and the two expressly permitted selftests wrote only under `C:/Temp/av-kit`; the probe/selftest scratch area was `C:/Temp/av-kit/s66/review`. These are plan-review observations, not implementation test passes.

## Findings

| # | Severity | Blocking | Kind | Finding | File:Line | Recommendation | Status |
|---|---|---|---|---|---|---|---|
| F1 | High | yes | behavior | `CLIENT_SIDE` admits errors that AC-140.4 expressly excludes. Its final `or sabr_matched` makes a later `DownloadError("unable to open for writing")`, DPAPI error or bot check retry whenever the attempt previously logged SABR. A multiline format-plus-cookie error also retries because the positive substring wins. The offline evaluation returned True for all four cases. This spends a second run on a non-client failure and changes the promised final error path. Violates AC-140, specifically AC-140.4 and `RETRY_ONCE`. Confidence: High. | `docs/execution/plans/2026-11-12-youtube-client-runtime/implementation-plan.md:116`; `:117`; `:189`; `:435` | Define exclusion precedence explicitly: preserve age handling first, then refuse bot, cookie and write failures across the complete text before considering positive client needles or the logger signal. Test mixed text and SABR-log-plus-excluded-error cases, retaining the genuine SABR-only retry. | fixed |
| F2 | High | yes | behavior | Row 1 adds `options` to `YouTubePort.extract_info` and immediately runs `test_domain.py`, whose exact parameter pin still requires `["self", "url", "flat"]`. The resulting four-parameter signature cannot pass that check. This test is absent from the moved-pin inventory, Files Modified and gate scope, so fixing it is also outside the written permitted edits. Row 1 cannot finish and `ADD_OPTS` cannot reach Green. Violates AC-140, specifically AC-140.9. Confidence: High. | `docs/execution/plans/2026-11-12-youtube-client-runtime/task.md:59`; `implementation-plan.md:137`; `tests/unit/test_domain.py:1355`; `session-gate.ps1:79` | Schedule the source-backed signature-pin update in row 1, assert the new optional parameter/default, preserve the other port checks, and include `tests/unit/test_domain.py` with its measured ending in the inventories and allowed set. | fixed |
| F3 | High | yes | behavior | Row 2a requires `test_ac_140_4` to fail by assertion, although its contract is exactly the existing one-run/no-retry behavior and row 1 leaves download behavior unchanged. An offline fake-YoutubeDL probe confirmed one run and the existing mapped exception for all eight listed classes. A faithful AC-140.4 test therefore passes before Green; `red-check.py` rejects a required test with no failure block, preventing row 3 from starting. Violates AC-140's AC-140.4 delivery sequence. Confidence: High. | `docs/execution/plans/2026-11-12-youtube-client-runtime/task.md:38`; `:61`; `implementation-plan.md:189`; `red-check.py:280`; `packages/infrastructure/src/avkit_infra/youtube/adapter.py:608` | Keep AC-140.4's negative behavior assertions and run them as passing characterizations, like AC-140.12; remove the already-satisfied contract from `--require`. Preserve the Red requirements for genuinely new retry behavior and exercise F1's exclusions after Green. | fixed |
| F4 | High | yes | behavior | H1-4 only accepts `changed == ['DependenciesOut']`, but row 5 and AC-141.1 require adding `deno_path` to `SettingsPutIn`, which is already exported in the committed OpenAPI schema. The required final change necessarily also changes `SettingsPutIn`. The offline schema-delta simulation reported `['DependenciesOut', 'SettingsPutIn']`, so a correct runtime implementation fails this mandatory gate. Violates AC-141, specifically AC-141.1/.8. Confidence: High. | `docs/execution/plans/2026-11-12-youtube-client-runtime/task.md:67`; `:75`; `packages/api/src/avkit_api/schemas/settings.py:12`; `implementation-plan.md:218` | Permit and precisely verify `SettingsPutIn.deno_path` as well as `JsRuntimeOut` and `DependenciesOut.js_runtime`; retain the unchanged-paths and no-unrelated-schema-change checks. Update the stated expected delta consistently. | fixed |
| F5 | High | yes | behavior | The promised MEU-140-only execution path is not executable. The split note leaves MEU-141 pending and supplies only the first issue, but row 6 still passes both `--issue` ids and requires both issues resolved, both MEUs ready and two Delivered notes. The resolver's exact-key precondition rejects that one-issue payload. Even after correcting row 6, the gate unconditionally lints `tools/smoke_packaged_runtime.py`, which deferred row 2b never creates. H1/H2 also unconditionally require both handoffs/status changes. D-641 B is offered but has no split branch in the task's decision logic. Thus choosing the split, offline or no-solver options cannot deliver the advertised independently reviewed MEU-140-only closeout. Violates AC-141's declared deferral/package boundary, including AC-141.12. Confidence: High. | `docs/execution/plans/2026-11-12-youtube-client-runtime/task.md:52`; `:69`; `:77`; `:86`; `session-gate.ps1:205`; `issue-resolve.py:115`; `implementation-plan.md:616` | Resolve one explicit active-MEU set from the rulings and split result. Apply it to rows 6/H1/H2, resolver arguments, status/spec expectations, handoff loops and gate paths. Handle D-641 B explicitly. Keep MEU-141 pending/open when deferred and omit absent runtime tooling from that session's checks. Prove the full and deferred paths with scratch fixtures. | fixed |

## Q1 — Goal and four calls

The intended ordinary browser trace is sound: default-client attempt → requested-format error → scrubbed attempt warning → pinned retry → its result/received height → service commits Done → `GET /downloads` reports Done, while the Console retains the failed-attempt detail. `SABR_ACROSS` feeds the existing service SABR lock. F1 prevents accepting the full failure partition; F2–F5 prevent completing the written execution sequence.

File-cookie add uses the shared options helper before insertion; `_cookie_opts` raises `CookieTestError`, `errors.py:31` maps it to 422, and no transaction creates jobs first. Browser add forwards browser/profile and follows the same client sequence. The cache tuple distinguishes cookie mode, browser, profile and file; no-options transcript calls retain `(url, flat)`.

The dev trace has the needed producers: empty setting/off-PATH → no explicit runtime; PUT → fresh `LIVE_SOURCE` lookup → next `_base_opts` and Health read. Installed layout is `resources/avkit-backend/avkit-backend.exe` plus sibling `resources/deno/deno.exe`, matching `parent.parent / 'deno'`. Solver dependency, data collection, runtime smoke and Health/UI all have rows and ACs. No residual-section feature is silently omitted, subject to Mat's dependency ruling and the explicitly allowed split. The final OpenAPI assertion is nevertheless impossible as written (F4).

## Q2 — CLIENT_SIDE

Accepted reuse of the three approved `no_format` needles and the whole-word SABR matcher. Installed `YoutubeDL.py:1191` and `:3093` contain the no-formats/requested-format strings. The reload, bot and image wording may be extractor/server text rather than literal constants in these installed source files; I did not make a network claim about those responses. Their use is carried Session 65/D-539 canon.

Empty text with no SABR match is False; multiline positive text matches as specified; age handling remains before retry classification. The material error is exclusion precedence (F1): with `sabr_matched=True`, even plain bot/cookie/write text is True. The logger signal is useful for a genuine SABR-only failure, but cannot override a prohibited cause.

## Q3 — Attempts, logging and SABR

Accepted the two-run cap, explicit stop between attempts, unchanged final `DownloadFailedError` → `download.failed` path, reuse of `scrub_line`, and OR across attempts for the result. Cancellation, `CookieTestError`, age and `OSError` remain outside the retrying `DownloadError` branch. No exact `youtube.download` field-set pin was found in the test census; adding `attempt` does not invalidate a named pin.

AC-140.3 requires the passing second run's `DownloadResult`, so a first-run payload cannot satisfy it. The plan does not expressly specify fresh per-attempt loggers or progress-clock reset; make those details explicit when implementing the shared attempt helper. Existing throttled progress is adapter state, while the result is built from returned info/path. No concrete partial-file/result leak was established in this plan-only review. F1 is the demonstrated retry defect; F3 is the no-retry characterization scheduling defect. Existing Console field filtering preserves `detail`; it does not automatically display arbitrary structured attempt/client/cause keys.

## Q4 — Add-time options and cache

The full `extract_info(` census found the production port, adapter, coordinator, download service, transcript service and adapter `get_formats`, plus the fakes named in the plan. yt-dlp's own fake `extract_info(url, download=...)` methods are a different boundary and need no port keyword. Conditional forwarding preserves the transcript fake and its flat/full cache behavior. The cookie cache tuple is complete for the named option changes; include cookie-file changes in the tests as well as cookie-mode changes.

Accepted the 422/no-row add contract and the shared options helper. The missed contract is an exact signature assertion rather than an unnamed caller (F2). No endpoint, downstream exception remapping or transcript-options expansion is needed.

## Q5 — Catch-all

Accepted. `bestvideo[height<=N]+bestaudio/best[height<=N]/best` adds the requested fallback after the bounded combined-format choice. `Best`, `Lowest` and audio selectors remain whole-string guards. Existing received-height handling records the successful retry/fallback height, so the UI can show the difference. AC-6.6 and AC-6.16 are correctly identified as moved pins.

## Q6 — Lookup, setting and audit

Accepted setting → bundled file → PATH, per-call reads, and placing every setting filesystem operation inside the fallthrough mapping. The input matrix covers empty/missing/folder, NUL, controls, lone surrogate and raised `is_file`. The frozen sibling path agrees with electron-builder's existing backend resource layout.

Installed yt-dlp documents and consumes `{'deno': {'path': ...}}` at `YoutubeDL.py:544–550,886–891`. Its Deno minimum is 2.3.0 (`utils/_jsruntime.py:90`); an older discovered runtime has `supported=False`, and EJS refuses it (`jsc/_builtin/ejs.py:312`). The FIC's Health `available` denotes discovery, not proof that an arbitrary configured binary is supported. The shipped pin is newer; no Deno executable was run here.

Appending the setting within downloader preserves existing relative order. `AUDIT_INPUT` is necessary because `PATH_LIKE` matches `deno_path`; adding it to the input exclusions preserves the seven isolation outputs and AC-68.8. Its moved input-list pin is named correctly.

## Q7 — Health, wire and UI

Accepted the 5-second version subprocess bound, parsed-version-only output, and `None` on timeout, vanished path, empty or garbage output. Defaults preserve existing `DependencyHealth`/`DependenciesOut` constructions. Authenticated runtime wire, none-found cost/fix text, read-only Browse field and dependencies refresh have explicit behavior ACs/tests.

The exact OpenAPI delta is not just the two health additions: it also includes the new request setting (F4). An in-memory append of the proposed CRLF test-id block preserved both guarded prefixes. Existing hash tests check historical prefixes; the added values are distinct. No Vitest/Electron run was claimed. The existing Electron settings spec is a regression gate; new runtime rendering/refresh assertions are scheduled in the renderer unit file, not in that unchanged Electron file.

## Q8 — Packaging and decisions

Accepted D-640's underlying conflict as an actual repository gate policy: installed METADATA pins EJS 0.8.0 and includes mutagen, brotli, pycryptodomex and websockets in `default`; the licence generator derives owners from the shipped build and refuses GPL-class owners outside `GPL_ALLOWED`. A preserves the solver pin with a guard; B requires the offered mutagen exclusion; C requires the offered allow-list change. This report makes no licence-law ruling. D leaves the issue open and must use the corrected deferred path (F5). D-642's PyPI authorization should be read together with the selected dependency option; B/C necessarily fetch their extra packages too.

`SOLVER_SPEC` includes both submodules and JS data, matching EJS's packaged solver use. The hash-before-extract/run rule and no-exe-after-mismatch negative are sound; release asset/sum availability remains an execution-time fact and a stop condition, not a fact verified offline. The resource filter excludes the zip and retains executable/licence. Fresh app data plus PATH removal and an asserted `source == 'bundled'` make the smoke's origin test meaningful.

The pre-session backend exists (28,174,901 bytes); a missing `js_runtime` field is a behavior Red, distinct from a launch/setup error. I did not run it. The NSIS output override is forwarded to electron-builder by the current dist script, protecting `ui/dist` and its rc.2 installer; the wrapper still rebuilds the existing UI/picker/MCP bundle outputs. Installer size remains measured work, not an estimate accepted here.

## Q9 — Pins

F2 is the material missed pin: `test_ac_4_7_port_method_sets_and_signatures` requires the old exact parameter list. Adapter port/implementation signature equality can stay intact if both sides change together. The quality/client pins and MCP input-exclusion pin are correctly scheduled; named packaging guards check subsets, so additive solver/data/notices entries need not rewrite them.

The census also covered settings keys/order/count/adjacency, dependency DTO fields, notices and licence lists. No further concrete incompatible exact pin was established. The row-1 sweep remains useful, but cannot substitute for scheduling the already-visible F2 change before its own required checks.

## Q10 — Red rules

Wrong stubs cover the declared session names; `deno_path` correctly remains absent until row 5. Assertion-first, membership-before-indexing and recorded exception-class helpers prevent setup errors from masquerading as Red. AC-140.12 and AC-141.11 are correctly outside `--require`, with separate passing checks. AC-141.11 follows the solver fetch.

AC-140.4 is another already-satisfied characterization and is incorrectly required Red (F3). Independent `red-check.py --selftest` returned **49 fixtures (15 positive, 34 negative), 0 wrong**. That proves its fixture parser, not that the plan's chosen tests can all fail. All actual product Reds remain unrun.

## Q11 — Endings, identity, scope and records

Accepted measured endings, byte-preserving edits and stated endings for new files. `identity.py` binds the dirty code/test/config tree, installed distribution names/versions including yt-dlp/EJS, and hashes the ignored Deno executable/licence; its selftest returned **0 failures**. It does not execute Deno. The missing domain-test path must be added with F2. Other listed product/project outputs are covered by scope or project prefixes.

MEU-141 status is a sensible single package-step selector, but the deferred path never consistently reaches the promised pending state (F5). Row 6's pre-status copy/diff and render checks appropriately protect concurrent entries on the full path. Its split invocation contradicts the resolver's exact issue-key rule. OpenAPI's required setting change causes F4.

Extracted read-only queue and shape blocks each exited 0 at this HEAD: 139 approved; 140/141 pending; the required shapes present; all declared new files/names absent. The unruled-decision stop is expected, not a finding. The anchors block records hashes/endings and treats the comparison report as hash-only; it was inspected, not executed here. No concrete material false-pass was established in these baseline controls.

## Q12 — Safety

Accepted the explicit mocked-YoutubeDL requirement, real-service Console traces with a patched extractor, runtime subprocess mocks, fixture-zip `-ExtractOnly` tests, pinned packaging destinations, and no installed-avkit-MCP calls. Named dependency/Deno/installer fetches wait on D-642, while every live probe separately waits on Mat's words and writes beneath the named temporary probe directory. There is no authorization-by-timeout or automatic YouTube probe path.

The planned packaged smoke necessarily uses its own localhost backend; its health request is distinct from external egress. No live probe, cookie read, external request or runtime process was performed in this review. No secret or home-folder value was included in the probe fixtures. Current full suites and build/network outcomes were not certified.

## Checklist Results

| Check | Result | Procedure / Command | Exit | Evidence |
|---|---|---|---|---|
| PR-1 plan/task alignment | fail | Manual trace of decision branches, task rows 52/69/77/86 and gate 205 by codex-independent-reviewer | null | F5: deferred scope is not propagated into commands and closeout. |
| PR-2 unstarted confirmation | pass | Offline probe and task read | 0 | HEAD 0553779; product additions absent; implementation rows unchecked. |
| PR-3 task contract completeness | pass | Manual task table inspection by codex-independent-reviewer | null | Rows name owners, deliverables, dependencies, commands and statuses. |
| PR-4 validation realism | fail | Offline probe plus manual exact-check trace | 0 | F2/F3/F4/F5 demonstrate checks that cannot pass their required state. |
| PR-5 source-backed planning | pass | Manual AC, spec and decision cross-check by codex-independent-reviewer | null | All 28 ACs have source bases; open rulings remain open. |
| PR-6 handoff/correction readiness | pass | Manual named-path and workflow inspection by codex-independent-reviewer | null | Both handoff/review destinations named; corrections belong to coordinator. Round-2 census is n/a. |
| PR-7 scope discipline | pass | Manual comparison with grouping/spec/MEU entries by codex-independent-reviewer | null | Stated exclusions match user scope; MEU-142 exists in Session 67. |
| PR-8 producer reachability and outcome partition | fail | Offline probe and source trace | 0 | F1's SABR signal overrides excluded errors; all major producers otherwise named. |
| PR-9 single-statement discipline | pass | Manual named-contract and repeated-literal inspection by codex-independent-reviewer | null | Named mechanisms centralize product rules; no additional ambiguous product literal was established. |
| Red-check selftest | pass | `rtk proxy .venv/Scripts/python.exe -B docs/execution/plans/2026-11-12-youtube-client-runtime/red-check.py --selftest` | 0 | 49 fixtures, 0 wrong. |
| Identity selftest | pass | `rtk proxy .venv/Scripts/python.exe -B docs/execution/plans/2026-11-12-youtube-client-runtime/identity.py --selftest` | 0 | 0 failures; ignored-Deno mutation changed state. |
| Product suites, builds, Deno and live probes | n/a | Not run under the review's explicit read-only/offline restrictions | null | No implementation pass claimed. |

### Decisive offline evidence

The probe evaluates `CLIENT_SIDE` literally from the written rule; that function is not yet implemented. It invokes the existing adapter only through an in-memory `_ydl` fake, never `YoutubeDL`. The OpenAPI check uses a copy of the committed JSON with the required additive changes. Queue/shapes are extracted Python blocks, not execution of `baseline.ps1`. Resolver evidence uses only its AST-extracted key-set precondition, not its Windows handle or file writer.

```json
{"schema_version":"evidence.v1","check_id":"s66-plan-offline-probe","command":"rtk proxy .venv/Scripts/python.exe -B C:/Temp/av-kit/s66/review/probe.py","cwd":"P:/av-kit","scope":"plan contracts, baseline adapter with fake, schema simulation, read-only queue/shapes, split preconditions","phase":"targeted","exit_code":0,"result":"pass","tested_state":"055377999828ea759315fcdd8d6c7b488110b67c working-tree plan inspected on 2026-11-12; not full-gate identity","output":"CLIENT_SIDE write_failed/cookies/bot with sabr_matched=True: retry True; mixed format plus DPAPI: retry True. AC-140.4 eight baseline cases: one run each. Port pin after options: False. Required OpenAPI changed=['DependenciesOut','SettingsPutIn']; H1-4 accepts=False. Split resolver refuses first-issue-only payload with both --issue ids. Split smoke exists=False; unconditional lint references it=True. Queue exit 0; shapes exit 0. Both test-id historical prefixes unchanged.","fresh":true}
```

```json
{"schema_version":"evidence.v1","check_id":"s66-redcheck-selftest","command":"rtk proxy .venv/Scripts/python.exe -B docs/execution/plans/2026-11-12-youtube-client-runtime/red-check.py --selftest","cwd":"P:/av-kit","scope":"plan-local receipt parser fixture selftest; TMP/TEMP=C:/Temp/av-kit/s66/review; PYTHONDONTWRITEBYTECODE=1","phase":"targeted","exit_code":0,"result":"pass","tested_state":"055377999828ea759315fcdd8d6c7b488110b67c working-tree red-check.py","output":"red-check selftest: 49 fixture(s) (15 positive, 34 negative), 0 wrong: []","fresh":true}
```

```json
{"schema_version":"evidence.v1","check_id":"s66-identity-selftest","command":"rtk proxy .venv/Scripts/python.exe -B docs/execution/plans/2026-11-12-youtube-client-runtime/identity.py --selftest","cwd":"P:/av-kit","scope":"scratch input-binding fixtures; TMP/TEMP=C:/Temp/av-kit/s66/review; PYTHONDONTWRITEBYTECODE=1","phase":"targeted","exit_code":0,"result":"pass","tested_state":"055377999828ea759315fcdd8d6c7b488110b67c working-tree identity.py","output":"bound packaging/deno-win64/deno.exe (ignored): absent=<absent> present_differs=True; identity selftest: 0 failure(s)","fresh":true}
```

## Verdict

`changes_required` — five High-confidence, High-severity delivery findings. The plan covers the intended feature surfaces, but it retries prohibited failures and cannot complete its own required sequence or deferred path as written. There are no formatting/process-paperwork findings and no Critical finding.

Correct F1–F5 through `/plan-corrections`, preserve the three open decisions for Mat, and resubmit the complete plan/task/scripts for ledger round 2. This report is saved only at `C:/Temp/av-kit/s66-plan-review-round-1.md`; the coordinator owns canonical copying and ledger transition. Completion-preflight was consulted in review scope: the unstarted implementation rows remain unmodified and do not authorize execution.

## Corrections Applied — 2026-11-12

Plan summary: the two MEUs, their 28 ACs (AC-140.1 to AC-140.12, AC-141.1 to AC-141.16), the mechanism ids and D-640 to D-654 are unchanged in number. Round 1's five findings are corrected in the plan folder only: `implementation-plan.md`, `task.md`, `session-gate.ps1`, `baseline.ps1`, and a new plan-local script `active-set.py`. No production code or test was written. Authority: `/plan-corrections` (doc-only corrections in the plan folder are reversible and proceed without a separate gate). The round 2 recheck waits for Mat's ledger `continue`, because the ledger refused round 2 for tokens.

Changes made, by finding:

- F1 (`CLIENT_SIDE` admitted excluded errors):
  - `CLIENT_SIDE` now decides in two steps over the whole case-folded text. First it is False on an `AGE_GATE_NEEDLES` needle, either bot-check needle of `FAILURE_CAUSE_NEEDLES`, a `cookies` needle or a `write_failed` needle, whatever the text or the log also holds. Only then is it True on a `no_format` needle, the reload-page needle, `sabr_phrase(text)` or `sabr_matched`.
  - D-643's `chosen` and `reasoning` say the same.
  - MEU-140's input matrix lists the precedence cases under no retry.
  - AC-140.4 carries them: a SABR phrase in attempt 1's log followed by a bot, cookie or write error, and a multiline text holding a format error and a cookie error, each one run. Its negative column keeps AC-140.3's SABR-only retry.
  - `task.md` row 2a writes these cases.
- F2 (the port signature pin):
  - §Pins that move gains `tests/unit/test_domain.py:1355` `test_ac_4_7_port_method_sets_and_signatures` (CRLF), moved in row 1 to `["self", "url", "flat", "options"]` with `options` defaulting to None and its other checks unchanged.
  - Files Modified lists `tests/unit/test_domain.py` (CRLF, MEU-140).
  - `session-gate.ps1`'s allowed paths include it.
  - `baseline.ps1` checks that the pin reads `["self", "url", "flat"]` at baseline.
  - `task.md` row 1 moves it and runs `test_domain.py`.
- F3 (AC-140.4 already holds at baseline):
  - AC-140.4 is now a `guard`. It passes where row 2a writes it, and row 3 runs it again once the retry exists.
  - `task.md` drops it from row 2a's `--require` and lists it with AC-140.12 as passing on that tree.
- F4 (H1-4 refused `SettingsPutIn`):
  - `RUNTIME_WIRE` and AC-141.8 name the full delta against `baseline.sha`: `JsRuntimeOut` added, nothing removed, `DependenciesOut` gaining `js_runtime` and `SettingsPutIn` gaining `deno_path`, each equal to its base without that property, and the paths unchanged.
  - `active-set.py openapi BASE` checks it, and H1-4 runs it.
  - Row 1b's snapshot gains `JsRuntimeOut` and `DependenciesOut.js_runtime` only; row 5 adds `SettingsPutIn.deno_path`.
- F5 (the split path could not run):
  - One active-MEU set, `active-meus.txt`, is written at a new row 3s from the rulings. It holds `MEU-140 MEU-141` or `MEU-140`.
  - `active-set.py` refuses a set the rulings don't allow. D-640 D, D-641 B or D-642 D allow only `MEU-140`. Otherwise D-641 D allows only both, and D-641 A allows either.
  - It also refuses task rows that disagree with the set: rows 4, 1b, 2b and 5 are `[B]` exactly when MEU-141 is deferred, each with its `### B-` block, `Reason: human-decision` and the ruling's link.
  - MEU-141's type-only names moved from row 1 to a new row 1b after row 4, so a split leaves no MEU-141 name, setting or OpenAPI change.
  - Row 6's records, issue ids and Delivered notes follow the set (`active-set.py records`). So do H1-3, H1-4, H1-6 to H1-7, H2-2, H2-5 and H2-6, and the next-prompt choice (Session 67 or 66b).
  - The gate reads the set and MEU-141's status and stops if they disagree (exit 2). It runs the package build, the Deno copy, the runtime smoke and the licences, and lints `tools/smoke_packaged_runtime.py`, only when MEU-141 is active. It adds an `active-set` check step.
  - D-641 B (split now) is handled by the same set.
  - D-641's recommendation moved from A to D, "do nothing" (one session, no split measured by context). This follows Mat's standing instruction of 2026-11-06 not to let context stop or shape a session, and Session 65's D-625 B. A and B stay as options.
- Round 1's Q8 note: D-642's summary and brief say that under D-640 B or C, `uv lock` also fetches the `default` extra's packages that are not already locked.

Verification results:

- The plan edits ran from `C:/Temp/av-kit/s66/plan_fix.py` (34 edits after a dry run) and `plan_fix2.py` (2 census follow-ups). Each edit replaces its old text exactly once. All five plan-folder files are still LF only.
- `lint_task_contract.py`: `OK: 28 row(s)` on the real task (`C:/Temp/av-kit/s66-plan-task-lint-r1fix.txt`).
- The split path was simulated on a scratch copy with rows 4, 1b, 2b and 5 set `[B]` and their blocks written. The lint gave `OK: 28 row(s)` (`C:/Temp/av-kit/s66-plan-task-lint-split.txt`).
- `active-set.py`'s row check passes on that copy under the split set and on the real task under the full set. It refuses the real task under the split set.
- The selftests:
  - `active-set.py --selftest`: 57 fixtures, 0 wrong;
  - `red-check.py --selftest`: 49 fixtures (15 positive, 34 negative), 0 wrong;
  - `identity.py --selftest`: 0 failures.
  - Receipts: `C:/Temp/av-kit/s66-plan-*-selftest-r1fix.txt`.
- `active-set.py check` on the real plan refuses with `D-640 is unruled (S14)`, as intended before the gate.
- `session-gate.ps1` and `baseline.ps1` parse with 0 errors. `baseline.ps1`'s shapes block, run alone, finds the pin at `test_domain.py:1355` and no `active-meus.txt` (`shapes wrong (S11): []`).
- Blast-radius census: 22 values swept as text in both plan files, covering the F1 to F5 terms and their variants; 138 sites found (`C:/Temp/av-kit/s66/census-r1.txt`). Two stale sites were found and updated: D-642's do-nothing row list now includes row 1b, and MEU-140's input matrix now lists the precedence cases. The rest were confirmed consistent (`census-r1b.txt`).

Status: corrections_applied. An independent recheck (round 2) follows; this section does not approve.

## Recheck (Round 2)

**Date:** 2026-11-12. **Agent:** codex-independent-reviewer. **Workflow:** `/plan-critical-review`. **Verdict:** `changes_required`. **Intent achieved:** partial, assessed as an unstarted plan. F1–F5 are fixed as originally reported; one additional incompatible port pin remains (F6). No Critical finding. The verdict and Checklist Results above this recheck are historical round 1 results.

### Recheck Result

| Finding | Recheck Result | Evidence |
|---|---|---|
| F1 | fixed | `implementation-plan.md:116-117,190,439-447`; `task.md:61-62`. Whole-text exclusions precede positives and `sabr_matched`; the offline literal-rule probe passed all 11 cases, including both bot apostrophes and mixed format/cookie text. |
| F2 | fixed | `task.md:59`, `implementation-plan.md:144,272`, `session-gate.ps1:81`, `baseline.ps1` shapes. The originally reported domain-test pin, default-None check, CRLF ending, allowed path and baseline shape are now scheduled. A separate existing pin found by the requested fresh sweep is F6 below. |
| F3 | fixed | `implementation-plan.md:190`; `task.md:36,61-62`. AC-140.4 is a passing guard, absent from every `--require`, run separately in row 2a and again in row 3's complete module. |
| F4 | fixed | `implementation-plan.md:128,226`; `active-set.py:188-214`; `task.md:66,68,76`. The actual-baseline simulation accepts the full additive delta and the unchanged split snapshot, rejecting all seven unrelated/missing-change mutations. |
| F5 | fixed | `active-set.py:85-106,112-159`; `task.md:52,63-91`; `session-gate.ps1:143-161,181-184,209-247`. All 72 ruling/set combinations behaved as specified; the actual full-task and scratch blocked-row task agree with their sets, and a mismatched task is refused. All later scope consumers use that set. F6 independently blocks either route's full suite. |

### New Findings

| # | Severity | Blocking | Kind | Finding | File:Line | Recommendation | Status |
|---|---|---|---|---|---|---|---|
| F6 | High | yes | behavior | `ADD_OPTS`/AC-140.9 adds `options`, but a second existing test pins both the old exact annotations and the old three-parameter port signature. The in-memory AST probe made **both** equalities false. This LF file is absent from the moved-pin inventory, row 1 and the gate allowance. Both active sets therefore fail the full Python gate, and an unscheduled test edit also fails scope-paths. Violates AC-140 (AC-140.9). Confidence: High. | `tests/unit/test_transcript_metadata.py:143`; `:144`; `docs/execution/plans/2026-11-12-youtube-client-runtime/task.md:59`; `session-gate.ps1:224` | Schedule the LF file in row 1, its affected checks and all relevant inventories/allowed paths. Amend both exact expectations for `options: DownloadOptions` followed by `None` as an allowed value and default, preserving playlist fields, return type and `flat=False`. | open |

### R1 — Retry precedence

All requested exclusions now evaluate False: write failure, DPAPI and straight/curly bot checks with `sabr_matched=True`, plus multiline format+cookie text. `no_format`, reload-page, a SABR phrase in the error, and other text with the SABR log signal evaluate True. `RETRY_ONCE` still excludes/maps the age gate before calling `CLIENT_SIDE`; the predicate redundantly refuses age needles too. “Other text” in AC-140.4 is the no-positive-signal case; a SABR-only signal is expressly AC-140.3's positive case and is not an exclusion. AC-140.4 requires separate parametrize ids for its log-plus-exclusion and mixed-text cases; row 2a writes those cases and row 3 reruns them. This is a probe of the written predicate, not a test of unimplemented retry code.

### R2 — Port pins and fakes

The reported `test_domain.py:1355` update now preserves its other checks and explicitly adds `options` with default None, CRLF, inventory, allowance and baseline coverage. The fresh `rg` sweep found F6: `test_transcript_metadata.py:143` also compares the entire type-hint map, and `:144` compares the entire parameter list. Both break, not just the parameter assertion. `git show HEAD:tests/unit/test_transcript_metadata.py` contains these pins and the working-tree diff for that file is empty. The generic adapter/port signature-equality check remains valid when both change together; the listed add-path fakes are scheduled to accept options, and the transcript fake remains usable because no-options forwarding stays unchanged. No further coordinator/fake signature pin was established by this sweep.

### R3 — Red feasibility

AC-140.4 and AC-140.12 pass where row 2a writes them; row 3 runs both again. The ten remaining required MEU-140 AC prefixes each have a new-behavior assertion Red available: .1 client opts, .2 selector, .3 retry, .5 cancellation after failure, .6 attempt warning, .7 that warning's scrubbed Console detail, .8 success across SABR/retry, .9 forwarded add options, .10 option-sensitive cache and .11 add-time missing-cookie rejection. The two moved selector/client pins also fail by assertion. The assertion-first and exception-class-recording instructions allow these Reds without indexing None, leaking a missing-name exception or requiring a setup failure. `red-check.py` rejects a required missing-name failure; its 49-fixture selftest passed. Actual product Reds remain unrun.

### R4 — OpenAPI delta

`active-set.py openapi BASE` delegates to the probed `openapi_problems`: only `JsRuntimeOut` is added, no schema is removed, and only `DependenciesOut.js_runtime` and `SettingsPutIn.deno_path` change, with their pre-existing content equal after removing the new property (and its optional required-list entry). All non-schema components, paths and other top-level parts are equal. Against the real baseline snapshot, unrelated schema/property changes, deletion of an old property, added paths, changed info, an extra schema and missing deno_path all refuse. Without MEU-141, only complete snapshot equality passes. Row 1b supplies Health's type-only delta; row 5 supplies the setting; H1-4 checks their final combined delta.

### R5 — Active routes

| Route | Active set at row 3s | Runtime rows | Records and next prompt |
|---|---|---|---|
| D-640 D | MEU-140 | 4, 1b, 2b, 5 blocked | Only download issue resolved/MEU ready then approved; runtime issue open/MEU pending; Session 66b |
| D-641 B | MEU-140 | same | same |
| D-642 D | MEU-140 | same | same |
| D-641 A after about half context | MEU-140 | same | same; context reading recorded in MEU-140 handoff |
| D-641 D, D-640 and D-642 not D | MEU-140 MEU-141 | all run: 4 → 1b → 2b → 5 | Both issues resolved/MEUs ready then approved; Session 67 |

The resolver receives exactly the active issue ids and matching payload keys; its exact-key precondition is preserved. Row 6 writes only the active Delivered notes and statuses, leaves a deferred runtime pending/open and adds 66b. `records` checks these results; H1-3 rechecks them. H1-4 branches its snapshot delta. H1-6/6a/6b create/check only active handoffs and 12 or 28 dotted ACs; H1-7 scopes the review accordingly; H2-2 approves only active MEUs while retaining the carried decision sources. H2-5 selects the matching commit draft and H2-6 the matching prompt. The gate's set/status condition stops with exit 2 unless full/ready_for_review or split/pending agree; package build, Deno copy, runtime smoke, licences and the smoke-script lint path are all conditional on that same flag. This condition and step-list construction were inspected; the session gate itself was not executed.

No MEU-141 production name, deno_path setting or snapshot change is added before row 3s: row 1b moved after row 4 and is blocked under every split. The full route still fetches, adds runtime types, writes Reds, implements runtime/settings/packaging and runs package verification. The active-set file intentionally cannot infer context usage itself under D-641 A; row 3s records and applies that reading. F6 is a common prerequisite repair for either route, not an active-set defect.

### R6 — Neighbours, decisions, binding and count

The pre-correction/current diff confines the material edits to F1–F5 and the offered D-641 recommendation. D-641's YAML and brief agree on A (conditional split), B (split now), D (one session without a context-measured split) and the no-solver/no-fetch overrides; D-643 agrees with the two-step `CLIENT_SIDE` rule. This review selects no ruling. D-642's summary/brief now include the extra unlocked packages under D-640 B/C. Order `0 → 1 → 2a → 3 → 3s → 4 → 1b → 2b → 5 → 6` leaves the new names available before their own Reds. `DECLARED_NEW` includes names from both type rows and only excuses non-required diagnostic blocks; its old “row 1 adds every one” comment is stale but does not affect that behavior. The copied lint receipts report `OK: 28 row(s)` for the actual task and blocked-row scratch task; these receipts were read, not regenerated here. The baseline shapes excerpt independently passed, with the domain pin present and active-meus.txt absent.

The real identity pathspec binds both new `active-set.py` and `active-meus.txt`, as independent scratch-repository mutations confirmed; a domain-test mutation also changes identity. The identity selftest passes. There are exactly 28 unique AC table rows (12 + 16), unchanged. The only new material obstacle established by this recheck is F6, found in the expressly requested additional port-signature sweep.

### Round 2 Checklist Results

| Check | Result | Command / procedure | Exit | Evidence |
|---|---|---|---|---|
| R1, R3 retry partition and Red sequence | pass | Literal-rule probe plus manual trace of task rows 1/2a/3 by codex-independent-reviewer | null | 11 predicate cases matched; AC-140.4 is never required Red and is rerun after retry. |
| R2 compatibility blast radius | fail | In-memory port AST amendment and fresh signature/type-hint census | 0 | F6: both old exact expectations in test_transcript_metadata.py become false; file not scheduled/allowed. |
| R4 strict OpenAPI delta | pass | `rtk proxy .venv/Scripts/python.exe -B C:/Temp/av-kit/s66/review/recheck_round2.py` | 0 | Actual baseline full/split positives pass; all seven mutation negatives refuse. |
| R5 route coverage | pass | Same probe plus manual inspection of task rows 3s/6/H1/H2 and gate conditions by codex-independent-reviewer | null | 72 ruling/set combinations; full and split row checks pass, wrong-set rows refuse; conditional package steps retained. |
| R6 input identity and AC inventory | pass | `rtk proxy .venv/Scripts/python.exe -B C:/Temp/av-kit/s66/review/recheck_round2.py` | 0 | active-set.py, active-meus.txt and domain-test mutation each changes scratch identity; 28 unique ACs; shapes wrong=[] (exit 0). |
| Active-set selftest | pass | `rtk proxy .venv/Scripts/python.exe -B docs/execution/plans/2026-11-12-youtube-client-runtime/active-set.py --selftest` | 0 | 57 fixtures, 0 wrong. |
| Red-check selftest | pass | `rtk proxy .venv/Scripts/python.exe -B docs/execution/plans/2026-11-12-youtube-client-runtime/red-check.py --selftest` | 0 | 49 fixtures (15 positive, 34 negative), 0 wrong. |
| Identity selftest | pass | `rtk proxy .venv/Scripts/python.exe -B docs/execution/plans/2026-11-12-youtube-client-runtime/identity.py --selftest` | 0 | 0 failures. |
| AV-1 to AV-6 | pass | Manual application in plan-review scope by codex-independent-reviewer | null | Required new behaviors have assertion Red paths and negative fixtures; no test weakening/skip is prescribed; wrong stubs are temporary type-row inputs; criteria retain source labels. Product Red/Green proof is execution work. |
| Product suites/builds, network and Deno | n/a | Not run under the explicit read-only/offline review boundary | null | No runtime/product-suite success is claimed. |

### Round 2 decisive evidence

```json
{"schema_version":"evidence.v1","check_id":"s66-plan-recheck-round2","command":"rtk proxy .venv/Scripts/python.exe -B C:/Temp/av-kit/s66/review/recheck_round2.py","cwd":"P:/av-kit","scope":"literal corrected CLIENT_SIDE rule; in-memory port amendment; actual-baseline OpenAPI mutation fixtures; ruling/set and task fixtures; scratch identity binding; AC census; read-only shapes excerpt","phase":"targeted","exit_code":0,"result":"pass","tested_state":"055377999828ea759315fcdd8d6c7b488110b67c working-tree plan recheck on 2026-11-12; not full-gate identity","output":"CLIENT_SIDE: 11 requested positive/negative cases matched. ADDITIONAL_PIN test_transcript_metadata.py:143 old-hints-survive=False; line144 old-parameters-survive=False; new_options_default=None. OPENAPI valid-full=True valid-split=True; seven unrelated/missing-delta mutations refused. ACTIVE_SET 72 ruling/set combinations pass; actual full/scratch split row checks pass; wrong-set rows refused. IDENTITY binds active-set.py, active-meus.txt and test_domain.py. ACS 28 unique; AC-140.4 not required Red. BASELINE shapes exit 0; shapes wrong (S11): []. No network, Deno, product suite or repository write.","fresh":true}
```

```json
{"schema_version":"evidence.v1","check_id":"s66-activeset-selftest-round2","command":"rtk proxy .venv/Scripts/python.exe -B docs/execution/plans/2026-11-12-youtube-client-runtime/active-set.py --selftest","cwd":"P:/av-kit","scope":"plan-local active-set scratch fixtures","phase":"targeted","exit_code":0,"result":"pass","tested_state":"0553779 working-tree active-set.py on 2026-11-12","output":"active-set selftest: 57 fixture(s), 0 wrong: []","fresh":true}
```

```json
{"schema_version":"evidence.v1","check_id":"s66-redcheck-selftest-round2","command":"rtk proxy .venv/Scripts/python.exe -B docs/execution/plans/2026-11-12-youtube-client-runtime/red-check.py --selftest","cwd":"P:/av-kit","scope":"plan-local receipt parser scratch fixtures","phase":"targeted","exit_code":0,"result":"pass","tested_state":"0553779 working-tree red-check.py on 2026-11-12","output":"red-check selftest: 49 fixture(s) (15 positive, 34 negative), 0 wrong: []","fresh":true}
```

```json
{"schema_version":"evidence.v1","check_id":"s66-identity-selftest-round2","command":"rtk proxy .venv/Scripts/python.exe -B docs/execution/plans/2026-11-12-youtube-client-runtime/identity.py --selftest","cwd":"P:/av-kit","scope":"scratch input-binding and evidence-reuse fixtures; TMP/TEMP under C:/Temp/av-kit/s66/review","phase":"targeted","exit_code":0,"result":"pass","tested_state":"0553779 working-tree identity.py on 2026-11-12","output":"bound inputs changed state and refused historical evidence; ignored Deno mutation changed state; project-artifact exclusions stayed unchanged; identity selftest: 0 failure(s)","fresh":true}
```

### Round 2 Verdict

`changes_required` — one High, High-confidence blocking deliverable finding (F6); F1–F5 are fixed. Add the missing transcript port annotation/signature pin amendment to the plan, preserving the existing playlist/return/default invariants, and recheck that correction. No other material regression was established. D-640–D-642 remain Mat's open gate decisions; this review neither rules them nor authorizes execution. Runtime, packaging and live outcomes remain execution-time facts.

Saved to `C:/Temp/av-kit/s66-plan-review-round-2.md` for the coordinator's canonical copy and ledger handling. Completion-preflight was consulted within review scope: canonical task.md remains an unstarted implementation plan, all 28 rows remain unchecked, and no repository edits or ledger mutations were made. The explicit JSON-only response contract supersedes the workflow's timestamp chat-line convention.

## Corrections Applied — 2026-11-12 (round 2)

Plan summary: unchanged in scope. The 28 ACs, the mechanism ids and D-640 to D-654 are the same. Round 2's one finding, F6, is corrected in the plan folder only (`implementation-plan.md`, `task.md`, `session-gate.ps1`, `baseline.ps1`). No production code or test was written. Authority: `/plan-corrections` (doc-only corrections in the plan folder), within Mat's ledger continue of 2026-11-12 ("add 30M tokens and continue the review corretion loop").

Changes made:

- F6 (the AC-122.6 port pin):
  - §Pins that move gains `tests/unit/test_transcript_metadata.py:142-145` `test_ac_122_6_playlist_info_and_extract_info_unchanged` (AC-122.6, LF), moved in row 1. Its type hints gain `"options": DownloadOptions | None` and its parameters become `["self", "url", "flat", "options"]` with `options` defaulting to None. `PlaylistInfo`'s fields, the return type `VideoInfo | PlaylistInfo` and `flat`'s default False stay pinned as written.
  - The move keeps the guard's purpose. Session 53's reflection says AC-122.6 "stops a later change from widening the download type (D-346)". D-346 kept `PlaylistInfo` and the download paths as they were for the transcript enumeration. The return type and `PlaylistInfo` stay pinned, and the new parameter is the add-time options that the session brief asks for (grouping D-539 A, MEU-140's "an add-time extract with the download's options").
  - Files Modified lists `tests/unit/test_transcript_metadata.py` (LF, MEU-140).
  - `session-gate.ps1`'s allowed paths include it.
  - `baseline.ps1`'s shapes block checks that both old lines are present at baseline (`:143` the hints, `:144` the parameters).
  - `task.md` row 1 moves it and runs the file. Row 3's Green run also runs it.
  - MEU-140's Guards paragraph, the type-only paragraph, the Verification Plan's baseline item, WP-2 and §Planning receipts name both port pins.
  - The plan's Status note records round 2.
- A fresh sweep of `tests/`, `ui/tests/`, `mcp-server/tests/` and `packages/` for `extract_info` signature, annotation and parameter pins found only `tests/unit/test_domain.py:1354-1355` (already scheduled) and `tests/unit/test_transcript_metadata.py:142-145`.

Verification results:

- The edits ran from `C:/Temp/av-kit/s66/plan_fix3.py` (12 edits, after a dry run) and `plan_fix4.py` (2 census follow-ups: WP-2's wording and row 3's run). Each edit replaces its old text exactly once. All four files are still LF only. Pre-correction copies: `C:/Temp/av-kit/s66/*.pre-r2fix`.
- `lint_task_contract.py`: `OK: 28 row(s)` (`C:/Temp/av-kit/s66-plan-task-lint-r2fix.txt`).
- `session-gate.ps1` and `baseline.ps1` parse with 0 errors (`s66-plan-ps-parse-r2fix.txt`).
- `baseline.ps1`'s shapes block, run alone on the working tree, exits 0 with `shapes wrong (S11): []`, so both AC-122.6 lines are found (`C:/Temp/av-kit/s66-plan-baseline-dry-shapes-r2fix.txt`).
- The selftests:
  - `active-set.py --selftest`: 57 fixtures, 0 wrong;
  - `red-check.py --selftest`: 49 fixtures (15 positive, 34 negative), 0 wrong;
  - `identity.py --selftest`: 0 failures.
  - Receipts: `C:/Temp/av-kit/s66-plan-*-selftest-r2fix.txt`.
- Census: 6 values (`test_transcript_metadata`, `AC-122.6`, `test_domain`, `port signature pin`, `moved port pin`, `F6`), 38 sites, in `C:/Temp/av-kit/s66/verify-r2fix.txt`. Two stale sites were updated by `plan_fix4.py`, and the rest are consistent.

Status: corrections_applied. An independent recheck (round 3) follows; this section does not approve.


## Recheck (Round 3)

**Date:** 2026-11-12. **Workflow:** `/plan-critical-review`, read-only recheck. **Agent:** codex-independent-reviewer (Codex, class `avkit_independent_reviewer`), independent of Claude Code/Anthropic, the plan and correction author. **Verdict:** `approved`. **Intent achieved:** yes, assessed as a plan. No new High or Critical finding.

The frontmatter and this section give the current round-3 result. Earlier rounds, their verdicts and checklists, and both Corrections Applied sections are retained as historical evidence. F1–F5 remain fixed; the round-2 correction did not reopen them. This review selects no ruling on D-640–D-642 and does not authorize execution.

### Recheck Result

| Finding | Recheck Result | Evidence |
|---|---|---|
| F6 | fixed | `implementation-plan.md:145,201,274,311,320`; `task.md:59,62`; `session-gate.ps1:82`; `baseline.ps1:104-105`. The planned AC-122.6 amendment passes against the in-memory port with `options: DownloadOptions \| None = None`. Separate wider-return, changed-playlist-fields and changed-flat-default mutations still fail at the original assertions; a changed options default also fails the new check. Both pytest rows include the file; inventories, LF ending, allowance and both baseline pin checks agree. |

### New Findings

| Finding | Severity | Blocking | Kind | Finding details | File:Line | Recommendation | Status |
|---|---|---|---|---|---|---|---|
| none | — | no | — | None. | — | — | fixed |

### R1 — F6 and the guard's purpose

Fixed. The probe AST-extracts only AC-122.6's function, adds the stated hints/parameter/default expectations, and supplies an in-memory amended port. It does not import or run the test module or pytest. The amendment passes; the unchanged old guard rejects the amended port at `test_transcript_metadata.py:143`. The amended guard still rejects a wider return type at `:143`, an extra `PlaylistInfo` field at `:137`, and `flat=True` at `:145`; `options` must default to None. `PlaylistInfo`'s exact field list and `VideoInfo | PlaylistInfo` return type remain pinned.

The file is present in every requested location, including row 1's and row 3's pytest argv. Both new baseline regexes independently match the actual old pin lines. The measured file and all four corrected plan files remain LF. Session 53's reflection (`docs/execution/reflections/2026-11-07-transcript-metadata-reflection.md:55,94`) states D-346's purpose: prevent widening the download type when adding transcript metadata. `ADD_OPTS` changes an optional input for AC-140.9 and leaves that output guard intact.

### R2 — Other signature pins and fakes

The fresh `extract_info` census across `tests/`, `packages/`, `tools/`, `ui/tests/` and `mcp-server/tests/` contains 49 hits. A separate introspection census and AST inspection find three relevant pin functions: the scheduled exact pins in `test_domain.py:1336` and `test_transcript_metadata.py:129`, and `test_youtube_adapter.py:233`'s port/adapter equality check. The equality check remains valid when row 1 changes both declarations together; it does not hard-code the old signature. No further unscheduled signature, annotation or parameter-list pin was established for the port, coordinator, adapter or a fake.

All five add-path fake sites remain scheduled in `implementation-plan.md:143` and row 1. The transcript fake (`test_transcript_flat_extract.py:24`) stays compatible because `ADD_OPTS` forwards `options=` only when given (`implementation-plan.md:121,196`). The three fake yt-dlp methods accepting `download=` represent yt-dlp's boundary and need no port `options` argument.

### R3 — Correction blast radius and prior fixes

Compared each of the four complete files against its `.pre-r2fix` copy, with surrounding lines. Changes are confined to F6's amendment, inventories, run lists, baseline checks and explanatory text. Only task rows 1 and 3 change; row 3's sole change is adding `tests/unit/test_transcript_metadata.py` to pytest. All 28 task rows remain unstarted. The 28 AC table rows are byte-for-byte unchanged (12 MEU-140 + 16 MEU-141). F1's exclusion precedence, F2's first port pin, F3's passing guard, F4's precise OpenAPI delta and F5's active-set routes are preserved.

The correction's lint receipt was read: `OK: 28 row(s); 10-column table (with builder_model); 26 row(s) fully checked ... dependencies resolve and are acyclic; 2 row(s) exempt (view_file): H1-5, H2-1`. It was not regenerated and no task command was executed. Fresh parse-only checks report zero errors for both PowerShell files. Fresh permitted selftests pass: active-set 57 fixtures, red-check 49 fixtures (15 positive, 34 negative), identity 0 failures. The census follow-ups are reflected in the actual WP-2 text and row 3 run list. No material regression from the round-2 correction was established.

### Round 3 Checklist Results

| Check | Result | Command / procedure | Exit | Evidence |
|---|---|---|---|---|
| R1 F6 amended guard and negative oracles | pass | `rtk proxy .venv/Scripts/python.exe -B C:/Temp/av-kit/s66/review/recheck_round3.py` | 0 | Planned guard passes; old guard rejects new port; wider return, changed fields, changed flat and changed options default are rejected. All requested schedule/inventory/baseline sites agree. |
| R2 signature/fake sweep | pass | Manual inspection by codex-independent-reviewer of the fresh `rg` extract-info and introspection receipts, with the probe's AST census | null | 49 extract-info hits; 3 relevant pin functions; exact pins scheduled, equality check compatible, 5 add-path fake sites scheduled; no additional unscheduled pin found. |
| R3 four-file diff and AC/row preservation | pass | `rtk proxy .venv/Scripts/python.exe -B C:/Temp/av-kit/s66/review/read_round3.py diff`, then the round-3 probe and manual neighbour/row-argv inspection by codex-independent-reviewer | 0 | Only F6-related changes; 28 identical AC rows; only task rows 1/3 differ; both include the file. Lint receipt reports 28 rows. |
| PowerShell parse only | pass | `[System.Management.Automation.Language.Parser]::ParseFile` on `session-gate.ps1` and `baseline.ps1` under `rtk proxy pwsh -NoProfile -Command` | 0 | 0 parse errors for each file; neither script executed. |
| Active-set selftest | pass | `rtk proxy .venv/Scripts/python.exe -B docs/execution/plans/2026-11-12-youtube-client-runtime/active-set.py --selftest` | 0 | 57 fixtures, 0 wrong. |
| Red-check selftest | pass | `rtk proxy .venv/Scripts/python.exe -B docs/execution/plans/2026-11-12-youtube-client-runtime/red-check.py --selftest` | 0 | 49 fixtures (15 positive, 34 negative), 0 wrong. |
| Identity selftest | pass | `rtk proxy .venv/Scripts/python.exe -B docs/execution/plans/2026-11-12-youtube-client-runtime/identity.py --selftest` | 0 | 0 failures; scratch fixtures only under C:/Temp/av-kit/s66/review. |
| AV-1 to AV-6, correction scope | pass | Manual application to the plan-only amendment by codex-independent-reviewer | null | Source-backed input amendment keeps output/default assertions; concrete negative oracles still fail; no skipped assertion, early return or weakened download type is prescribed. Product Red/Green remains execution work. |
| Read-only/offline review scope | pass | Reviewed command history and compared SHA-256 values for 20 reviewed inputs before/after probes, observer codex-independent-reviewer | null | HEAD 055377999828ea759315fcdd8d6c7b488110b67c; reviewed input hashes unchanged. Only C:/Temp/av-kit outputs written. Forbidden files, network and Deno were not accessed. |
| Product suites/builds and live runtime | n/a | Not run under the explicit review boundary | null | No pytest, Vitest, session gate, baseline, backend, MCP server, npm/npx/tsx, packaging or uv lock/sync. No implementation pass claimed. |

### Round 3 decisive evidence

```json
{"schema_version": "evidence.v1", "check_id": "s66-plan-recheck-round3", "command": "rtk proxy .venv/Scripts/python.exe -B C:/Temp/av-kit/s66/review/recheck_round3.py", "cwd": "P:/av-kit", "scope": "in-memory AC-122.6 amendment and negative oracles; correction inventories/pytest argv; baseline regexes; unchanged AC/task rows; AST pin/fake census", "phase": "targeted", "exit_code": 0, "result": "pass", "tested_state": "055377999828ea759315fcdd8d6c7b488110b67c working-tree round-3 plan correction on 2026-11-12; reviewed-input hashes saved in reviewed-inputs-round3.json; not full-gate identity", "output": "AC1226 old-guard-rejects-new-port pass=False assertion_line=143\nAC1226 planned-amendment pass=True assertion_line=None\nAC1226 wider-return-type pass=False assertion_line=143\nAC1226 changed-playlist-fields pass=False assertion_line=137\nAC1226 changed-flat-default pass=False assertion_line=145\nAC1226 changed-options-default pass=False assertion_line=1\nSIGNATURE planned-options, exact return, flat=False and options=None retained\nSCHEDULE row1 pytest includes tests/unit/test_transcript_metadata.py\nSCHEDULE row3 pytest includes tests/unit/test_transcript_metadata.py\nINVENTORY moved pin, Files Modified LF, gate allowance all present; source file LF\nBASELINE transcript old-hints/old-parameters regexes: 2/2 match\nREGRESSION AC rows byte-for-byte equal: 28 (12+16); task rows: 28, all unstarted; only rows 1 and 3 changed\nREGRESSION gate only adds allowed path; baseline only adds two transcript pin checks\nENDINGS all four corrected plan files remain LF\nCENSUS extract_info hits: 49\nEXTRACT_DEF tests/e2e/real_stack.py 66 self, url: str\nEXTRACT_DEF tests/e2e/test_api_error_surface.py 174 self, url: str, flat: bool=False\nEXTRACT_DEF tests/integration/test_download_received_quality.py 98 self, url: str, flat: bool=False\nEXTRACT_DEF tests/integration/test_download_received_quality.py 125 self, url: str, download: bool=False\nPIN_FUNCTION tests/integration/test_youtube_adapter.py 233 test_ac_6_2_youtube_port_signatures_match\nEXTRACT_DEF tests/integration/test_youtube_adapter.py 194 self, url: str, download: bool=False\nEXTRACT_DEF tests/integration/test_youtube_adapter_visibility.py 354 self, url: str, download: bool=False\nPIN_FUNCTION tests/unit/test_domain.py 1336 test_ac_4_7_port_method_sets_and_signatures\nEXTRACT_DEF tests/unit/test_services.py 384 self, url: str, flat: bool=False\nEXTRACT_DEF tests/unit/test_services.py 671 self, url: str, flat: bool=False\nEXTRACT_DEF tests/unit/test_transcript_flat_extract.py 24 self, url: str, flat: bool=False\nPIN_FUNCTION tests/unit/test_transcript_metadata.py 129 test_ac_122_6_playlist_info_and_extract_info_unchanged\nREAD_ONLY reviewed-input hashes unchanged: 20\nround3 probe: pass; no pytest, product process, network, Deno or repository write", "fresh": true}
```

```json
{"schema_version": "evidence.v1", "check_id": "s66-activeset-selftest-round3", "command": "rtk proxy .venv/Scripts/python.exe -B docs/execution/plans/2026-11-12-youtube-client-runtime/active-set.py --selftest", "cwd": "P:/av-kit", "scope": "plan-local scratch fixtures only; PYTHONDONTWRITEBYTECODE=1; TMP/TEMP=C:/Temp/av-kit/s66/review", "phase": "targeted", "exit_code": 0, "result": "pass", "tested_state": "0553779 working-tree active-set.py on 2026-11-12; not product full-gate identity", "output": "active-set selftest: 57 fixture(s), 0 wrong: []", "fresh": true}
```

```json
{"schema_version": "evidence.v1", "check_id": "s66-redcheck-selftest-round3", "command": "rtk proxy .venv/Scripts/python.exe -B docs/execution/plans/2026-11-12-youtube-client-runtime/red-check.py --selftest", "cwd": "P:/av-kit", "scope": "plan-local scratch fixtures only; PYTHONDONTWRITEBYTECODE=1; TMP/TEMP=C:/Temp/av-kit/s66/review", "phase": "targeted", "exit_code": 0, "result": "pass", "tested_state": "0553779 working-tree red-check.py on 2026-11-12; not product full-gate identity", "output": "red-check selftest: 49 fixture(s) (15 positive, 34 negative), 0 wrong: []", "fresh": true}
```

```json
{"schema_version": "evidence.v1", "check_id": "s66-identity-selftest-round3", "command": "rtk proxy .venv/Scripts/python.exe -B docs/execution/plans/2026-11-12-youtube-client-runtime/identity.py --selftest", "cwd": "P:/av-kit", "scope": "plan-local scratch fixtures only; PYTHONDONTWRITEBYTECODE=1; TMP/TEMP=C:/Temp/av-kit/s66/review", "phase": "targeted", "exit_code": 0, "result": "pass", "tested_state": "0553779 working-tree identity.py on 2026-11-12; not product full-gate identity", "output": "identity selftest: 0 failure(s)", "fresh": true}
```

### Round 3 Verdict

`approved` — F6 is fixed, F1–F5 remain fixed, and this recheck found no new material delivery defect. Executing the corrected plan can deliver the registered goal, subject to Mat's still-open D-640–D-642 rulings and explicit execution authorization. Runtime, packaging and live behavior remain unimplemented and unmeasured here.

Completion-preflight was consulted within the authorized plan-review scope: the canonical task was reread, all 28 implementation rows remain unchecked, and no implementation or closeout claim is made. The coordinator owns the canonical copy and ledger transition. Complete rolling report saved to `C:/Temp/av-kit/s66-plan-review-round-3.md`.


## Recheck (Round 4)

This round re-issues round 3's approved result with the New Findings table in the template shape and no other change.

### Recheck Result

| Finding | Recheck Result | Evidence |
|---|---|---|
| F6 | fixed | Round 3's result is unchanged; this is a format-only re-issue. |

### New Findings

| Finding | Severity | Blocking | Kind | Finding details | File:Line | Recommendation | Status |
|---|---|---|---|---|---|---|---|
| none | — | no | — | None. | — | — | fixed |

## Recheck (Round 5)

This round re-issues round 4's result with each Recheck Result table's middle column named `Recheck Result`, and no other change.

### Recheck Result

| Finding | Recheck Result | Evidence |
|---|---|---|
| F6 | fixed | Round 3's result is unchanged; this is a format-only re-issue. |

### New Findings

| Finding | Severity | Blocking | Kind | Finding details | File:Line | Recommendation | Status |
|---|---|---|---|---|---|---|---|
| none | — | no | — | None. | — | — | fixed |
