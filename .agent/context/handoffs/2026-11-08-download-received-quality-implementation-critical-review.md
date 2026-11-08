---
date: "2026-11-08"
review_mode: "execution"
target_plan: "docs/execution/plans/2026-11-08-download-received-quality/implementation-plan.md"
verdict: "approved"
findings_count: 0
template_version: "2.2"
requested_verbosity: "standard"
agent: "codex-independent-reviewer"
loop_id: "s55-execution-2026-11-08-download-received-quality"
round: 1
---

# Critical Review: 2026-11-08-download-received-quality

> **Review Mode:** execution · **Verdict:** approved · **Intent achieved:** yes

## Scope

Independent Codex review of Claude Code's Session 55 / MEU-124 working tree against HEAD `2963efe909efc2201c9dffa29a39a97a6ad44520`. Read the correlated handoff, plan/task, product/test diffs, relevant consumers, installed yt-dlp source, plan-local scripts, records and supplied receipts. Applied IR-1–IR-7, the Materiality Gate and Verdict Rule. Accepted Mat's rulings, D-381–D-392 and the stated old-row/audio-only limits. The other session's capture work and post-review H2 deliverables are excluded.

**Intent anchor:** Session 55 stores the height of the file each download actually received, in a new nullable `received_height` column that an existing database gains through `COLUMN_MIGRATIONS`. The row shows it next to the request only when they differ, and a null shows the request as today. The download add path flattens a bare channel's tabs one level, so it queues the channel's videos. The backend's `engine.created` line stops logging the database path.

No repository file was edited. Reviewer scripts, databases, reports and receipts are under `C:/Temp/av-kit`. No pytest, Vitest, Playwright, session gate, dev app, issue-resolve execution or network request was run. The offline probes called production Python functions directly and evaluated the renderer helper from its actual source. Socket connections were disabled in the behavior probe; the adapter's `YoutubeDL` binding was replaced with a fake. Forbidden configuration/secret files and the fleet hub were not opened.

## Findings

No findings. No Critical or High defect, material false-pass or unfulfilled in-scope AC was demonstrated.

| # | Severity | Blocking | Kind | Finding | File:Line | Recommendation | Status |
|---|----------|----------|------|---------|-----------|----------------|--------|

## Review Questions

### Q1 — Done and the complete received-quality path

**Accepted.** The adapter reads returned info after the download (`youtube/adapter.py:505,532-544`), constructs `DownloadResult.height`, and the successful service save writes `received_height` (`services/download.py:561-580`). The insert/update/read mappings carry it (`database/mappers.py:119,143,165`). `_job_out` and the API list preserve it (`routes/downloads.py:59,92`); MCP's recursive sanitizer retains this key (`toolsets/registry.ts:286-300,365-389`); `parseListEnvelope` retains the API items (`useDownloadQueue.ts:44-46`), and the page passes it to the helper (`DownloaderPage.tsx:497-502`).

The independent real adapter/service/SQLite probe persisted 360 for 1080p channel jobs and serialized 360 through `_job_out`. The actual renderer helper produced `360p (asked 1080p)`, matched-height request alone, and null/absent-height request alone. Speed/ETA order is unchanged; the card's status construction is unchanged (`DownloaderPage.tsx:476-485`). **Not accepted:** none.

### Q2 — RECEIVED_HEIGHT and STORED_ON_DONE

**Accepted.** Installed yt-dlp is `2026.10.26`. Its merge copies the sole video's height (`YoutubeDL.py:2474-2505`), and its returned info is updated from the selected format after processing (`:3100-3153`). The same update handles a muxed format. This supports D-381's selected-format metadata measure.

Independent adapter probes retained integer 360 and returned None without raising for bool, float, zero, negative, string, missing, null, infinity and NaN. Only the Done save assigns the new field. The real-stack probe verified Pending/Failed/reset Pending remain null, successful retry stores 360, and audio-only remains null even with result height 360. Done has no outgoing transition (`domain/download.py:29-58`); reset rejects it and restarting processing does not redownload it. No reachable stale-height retry path was demonstrated. **Not accepted:** none.

### Q3 — COLUMN_UPGRADE and the absent-table guard

**Accepted.** The independent probe compiled HEAD's ORM model and compared its normalized SQLite DDL with both `pre-change-download-jobs.sql` and AC-124.7's literal: they agree. It upgraded two old rows, preserved every original SQL value, appended null to each, matched fresh-database column order and remained stable after another migration pass.

`init_schema` calls `create_all` before `apply_migrations` (`engine.py:115-119`). Migrations execute CREATE statements before collecting `tables` (`migrations.py:124-128`), so the guard cannot overlook a table created earlier in that call. No subsequent statement creates a missing download table. A standalone migrations-only call correctly skips it; a later `init_schema` creates the complete current table. Independent probing verified this sequence and the conversion `gpu_preference` migration. Existing-table ALTER errors still propagate. AC-112.5's unchanged migrations-only branch (`test_ffmpeg_conversion.py:1131-1134`) explains the disclosed first-run failure and the fix. **Not accepted:** none.

### Q4 — WIRE_FIELD and SHOWN_WHEN_DIFFERENT

**Accepted.** API `received_height` is required and nullable (`schemas/downloads.py:64`); the renderer declares `number | null` (`useDownloadQueue.ts:20`). Independent semantic comparison found exactly the OpenAPI property addition and its required-list entry, satisfying S6. MCP does not denylist the field; the queue hook does not reconstruct or discard row fields. Changed fixtures satisfy the new TypeScript member, and saved whole-UI typecheck evidence is clean.

Ten actual-source helper cases passed: null, absent, zero, negative and NaN show the request; equal heights show it once; differing heights, best and lowest show received plus request. A positive non-integer renders its literal number, e.g. `1.5p (asked 1080p)`: that is precisely the accepted D-385 positive-number contract, while the backend supplies only integers. Each case preserves speed and ETA. **Not accepted:** none.

### Q5 — BARE_CHANNEL_FLAT and VIDEO_TARGET

**Accepted.** `_flat_entries` extracts the former transcript loop without changing its filtering; independent comparison with HEAD's `_listed_videos` agreed on six channel/ordinary/duplicate/nested/malformed inputs. The download path uses the same flatten then existing ID deduplication (`adapter.py:158-174,264-275`). Tab and ordinary playlist entries remain intact; nested playlists are dropped. `playlistend` is still supplied to yt-dlp (`:472-473`); it retains its existing enumeration/per-tab semantics, not a newly imposed global deduplicated cap.

The real-stack probe queued three distinct tab videos and observed exactly their three watch URLs through the real adapter download path, with only `YoutubeDL` faked. AC-124.10/.12 cover the larger eight-video recorded shape. Each list row now stores its own URL (`services/download.py:187-189`), while single-video adds retain the typed URL (`:185-186`; AC-124.16). Copy uses that stored URL before output exists (`DownloaderPage.tsx:484`); dedup and archive use video IDs; retry preserves the intended stored video target; the API returns it. The accepted pre-fix-row limit remains. **Not accepted:** none.

### Q6 — Tests, Red and guards

Both saved Red child exits are **1**. Independent use of the actual receipt parser found **10 Python and 2 UI assertion-only failure blocks**, covering every one of the task's 12 required failure IDs. The nine passing Python cases are the intentional guards (.3, .4, six .6 cases, .11). Current expectations agree with the diagnostics; row 4's edit script changes production behavior rather than test expectations.

| AC / tests | Grade | Assessment |
|---|---|---|
| AC-124.1 | Strong | Exact defaults/value and exceptions for both domain fields. |
| AC-124.2–.4 | Strong | Actual worker lifecycle and persisted Done/value/null, including audio-only. |
| AC-124.5–.6 | Strong | Real adapter with fake boundary; exact positive value and six invalid/missing cases. |
| AC-124.7 | Strong | Real pre-change DDL, complete old-row values, fresh order and repeated migration. |
| AC-124.8 | Strong | Real SQLite service lifecycle followed by fresh-unit-of-work read. |
| AC-124.9 | Strong | API list asserts the numeric value and explicit null key. |
| AC-124.10–.11 | Strong | Exact ordered unique IDs, channel/deeper-playlist exclusions and unchanged tab listing. |
| AC-124.12 | Strong | Real add/coordinator/adapter/SQLite; download recording port appends at `:102`; exact ordered URLs and all-Done assertions. It intentionally uses the recording port for dispatch, as the approved AC says. |
| AC-124.13 | Strong | Real production `build_services` order; `_active=None`; stdout engine positive control; stdout/stderr/ring/file marker predicates. |
| AC-124.14–.15 | Strong | Exact helper segments and rendered card text/null fallback; .15 explicitly awaits a macrotask inside `act` (`:1209-1211`). |
| AC-124.16 | Strong | Literal expected watch URLs, actual port recording and all-Done checks; no imported production prefix as oracle. |

The new tests neither skip assertions nor hide setup failures. Joining workers is followed by explicit liveness/completion assertions. Independent negative controls showed the old request-only helper fails the mismatch predicate and a wrong full-gate identity is refused. No concrete material product defect that false-passes the combined AC/guard/gate evidence was demonstrated. The unchanged named guards are covered by the matching full-suite receipts; `ui/tests/e2e/test-ids.ts` is unchanged against HEAD for AC-51.6/AC-81.13. **Not accepted:** none.

### Q7 — STARTUP_NO_PATH and NO_RAW_CONSOLE

**Accepted.** The changed engine event is fieldless (`engine.py:85`); other successful database-startup events contain counts or fixed text. Production constructs the engine before HealthService (`wiring.py:135,205`). The independent real `build_services` probe captured `engine.created` and found no unique app-data marker in stdout/stderr or ring. After startup, real channel add/download/retry probes found no raw URL, marker or output path in stdout/stderr/ring/file, and no height field was logged.

The add call's unchanged `url=` and `info_type=` fields are omitted by `CONSOLE_FIELDS` and cleared before downstream rendering (`health.py:47-56,207-235`). `youtube.download` still logs only ID and SABR flag (`adapter.py:546`). Passing-suite standalone fake stacks are not production startup; their pre-HealthService URL diagnostics in Red are accurately qualified by D-388, not a new production log route. No additional raw-value leak introduced or changed by this delta was demonstrated. **Not accepted:** none.

### Q8 — Evidence freshness and records

**Accepted.** Independently recomputed state, with `ELECTRON_RUN_AS_NODE` unset:

`2963efe909efc2201c9dffa29a39a97a6ad44520+e46f3659e08b07bcec1cb4d436bd1fa996ac2642cbab8dda7c3ed0e7259a70d9`

It equals the handoff and both gate identities. Process-local `core.excludesFile` contained only `.claude/settings.local.json`, reproducing the host exclusion without opening that file; process-local `safe.directory=P:/av-kit` allowed sandbox git access. The first uv attempt encountered its inaccessible home cache. The successful identity command used a temporary UV_CACHE_DIR, offline mode and UV_NO_SYNC=1; no dependency/configuration was changed.

The ten handoff evidence.v1 records agree with their inspected receipts. All **20 gate steps** record exit 0, with no excused baseline failures: **1357 Python, 1176 UI, 470 MCP, 4 standalone integration and 26 Electron tests passed**. Those suites were not rerun here. The durable-evidence validator accepts the current identity and refuses the wrong-state control. The .ps1 row commands, Red children/wrappers and disclosed migration correction are consistent with the artifacts.

Independent before/after register hashes match `s55-resolve.txt`; exactly **19 parsed differences** occur under status/verification/resolution_path of the four requested issues. Their resolution claims match the source and receipts. Spec additions describe delivered behavior; grouping row 55 is executed (`:258`); MEU-124 is deliberately ready_for_review (`meu-status.yaml:3251`). Regenerated status/issue surfaces agree with saved checks. Reversing only MEU-124's state and eight wrap continuations reconstructed the exact **3483-line baseline SHA-256 `12872755251016c79318d4e412c62cbeeac5e207bff9ea1fd1922f3b502625b0`**. Parsed comparison proves the MEU-128–132 rewrap and phase/summary content are unchanged. **Not accepted:** none.

## Checklist Results

| Check | Result | Observation | Exit | Evidence |
|---|---|---|---|---|
| IR-1, IR-2, IR-4: runtime/collaborators/generalization | pass | Independent offline behavior probe and source trace | 0 | Real adapter/service/SQLite/API serialization, upgrade, retry, audio-only and Console observations agree. |
| IR-3, IR-6: mapping/boundaries | pass | Manual source/schema/diff review by codex-independent-reviewer | null | No new request/write input; existing strict inputs/error mappings retained; required-nullable response and adapter/domain checks hold. |
| IR-5, AV-1–AV-5: rigor and bypasses | pass | Independent receipt audit, actual-source UI probe and test diff | 0 | All 12 required Red assertions; exact values/lifecycle; negative controls; no masking or material false-pass demonstrated. |
| IR-7: AC coverage and deferrals | pass | Manual plan/handoff/source comparison by codex-independent-reviewer | null | All 16 ACs accounted for; accepted limits retained; H2 is correctly subsequent to this review. |
| DR: delivered claims, scope and freshness | pass | Identity, evidence/register audit and baseline reconstruction | 0 | Exact full-gate match, 19 confined register changes, only MEU-124 parsed status change. |

### Commands and durable reviewer evidence

Commands ran from `P:/av-kit`, with streams redirected under `C:/Temp/av-kit` and `$LASTEXITCODE` preserved before receipt reads. Python used `-B`/PYTHONDONTWRITEBYTECODE; database probes used TMP/TEMP `C:/Temp/av-kit/s55/review-tmp`. The temporary scripts remain available for audit.

```json
{"schema_version":"evidence.v1","check_id":"s55-review-behavior","command":"rtk proxy .venv/Scripts/python.exe -B C:/Temp/av-kit/s55_review_probe.py","cwd":"P:/av-kit","scope":"independent offline real adapter/service/SQLite/startup/migration probes, with YoutubeDL faked and sockets blocked","phase":"targeted","exit_code":0,"result":"pass","tested_state":"2963efe909efc2201c9dffa29a39a97a6ad44520+e46f3659e08b07bcec1cb4d436bd1fa996ac2642cbab8dda7c3ed0e7259a70d9","output":"Real stack: 3 distinct channel watch URLs -> Done/SQLite/API all 360; invalid heights None; audio-only and failed/reset Pending null; retry Done 360; Done reset refused/no redownload. Startup engine.created captured without marker; request-time stdout/stderr/ring/file omit URL/path/height. HEAD DDL equals saved/test DDL; 2 complete old rows preserved plus null; fresh order/idempotence pass; migrations-only then init_schema pass; 6 HEAD/current transcript listing cases equal."}
```

```json
{"schema_version":"evidence.v1","check_id":"s55-review-renderer","command":"rtk proxy node C:/Temp/av-kit/s55_review_ui.cjs","cwd":"P:/av-kit","scope":"downloadMetaSegments function extracted from actual source, transpiled/evaluated in memory, without test runners or build output","phase":"targeted","exit_code":0,"result":"pass","tested_state":"2963efe909efc2201c9dffa29a39a97a6ad44520+e46f3659e08b07bcec1cb4d436bd1fa996ac2642cbab8dda7c3ed0e7259a70d9","output":"10 cases passed: null, absent, zero, negative, NaN, match, mismatch, best, lowest, positive fraction; speed/ETA preserved. Negative control: old request-only helper fails mismatch expectation."}
```

```json
{"schema_version":"evidence.v1","check_id":"s55-review-identity","command":"rtk proxy uv run python -B docs/execution/plans/2026-11-08-download-received-quality/identity.py --state-only","cwd":"P:/av-kit","scope":"D6 identity, ELECTRON_RUN_AS_NODE unset, UV_OFFLINE=1, UV_NO_SYNC=1, scratch UV_CACHE_DIR and process-local git exclusion/safe.directory as described in Q8","phase":"static","exit_code":0,"result":"pass","tested_state":"2963efe909efc2201c9dffa29a39a97a6ad44520+e46f3659e08b07bcec1cb4d436bd1fa996ac2642cbab8dda7c3ed0e7259a70d9","output":"2963efe909efc2201c9dffa29a39a97a6ad44520+e46f3659e08b07bcec1cb4d436bd1fa996ac2642cbab8dda7c3ed0e7259a70d9"}
```

```json
{"schema_version":"evidence.v1","check_id":"s55-review-records","command":"rtk proxy .venv/Scripts/python.exe -B C:/Temp/av-kit/s55_review_records.py","cwd":"P:/av-kit","scope":"independent Red attribution, receipt totals, register differences, OpenAPI semantic diff, unchanged test IDs and gate identity comparison","phase":"static","exit_code":0,"result":"pass","tested_state":"2963efe909efc2201c9dffa29a39a97a6ad44520+e46f3659e08b07bcec1cb4d436bd1fa996ac2642cbab8dda7c3ed0e7259a70d9","output":"Register before/after hashes exact; 19 confined changes. OpenAPI only received_height + required; test-ids unchanged. Red children exit 1: 10 Python/2 UI assertion blocks; all 12 required IDs found. Ten handoff records; saved totals baseline 1338/1174/470, Green 323/52, full 1357/1176/470/4/26; 20 recorded gate steps exit 0; both identities and handoff equal current state."}
```

```json
{"schema_version":"evidence.v1","check_id":"s55-review-rewrap","command":"rtk proxy .venv/Scripts/python.exe -B C:/Temp/av-kit/s55_review_rewrap.py","cwd":"P:/av-kit","scope":"reconstruct pre-row-6 meu-status bytes and verify parsed change scope against baseline SHA-256","phase":"static","exit_code":0,"result":"pass","tested_state":"2963efe909efc2201c9dffa29a39a97a6ad44520+e46f3659e08b07bcec1cb4d436bd1fa996ac2642cbab8dda7c3ed0e7259a70d9","output":"Joined 8 wrapping continuations; reconstructed 3483-line baseline SHA-256 12872755251016c79318d4e412c62cbeeac5e207bff9ea1fd1922f3b502625b0 exactly. Only MEU-124 differs when parsed; MEU-128..132 and phase/summary data unchanged."}
```

The current-state `tools/durable_evidence.py HANDOFF --require-full --expected-state STATE` check exited 0 with `OK: durable evidence records`. A separate read-only call to `evidence_problems` with a deliberately wrong state confirmed refusal: `final full gate does not match expected_state; no fresh passing full gate for the expected review state`.

## Verdict

**approved** — the registered intent is achieved; no corrections are required by this round. Verification combines independently reproduced offline behavior and matching saved full-suite/Electron evidence. It does not claim a live YouTube/media download or a new Electron run. The coordinator retains responsibility for ledger collection, canonical report copying and authorized H2 closeout; no commit or push is authorized by this verdict.

Completion-preflight re-read the canonical task and review contract. Remaining review collection/H2 rows belong to the coordinator and are not represented as complete here. The verdict JSON passed `review-verdict.schema.v2.json`; goal-anchor, Q1–Q8 and home-path redaction checks passed. `validate_closeout_artifacts.py --review-state-only` exited 0: `review_mode=execution; round 1 of 6; verdict=approved; open findings=0`. A final identity recomputation still matches the state above.

🕐 Completed: 2026-11-08 09:23 (EST)
