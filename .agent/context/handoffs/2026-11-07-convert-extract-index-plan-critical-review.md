---
date: "2026-11-07"
review_mode: "plan"
target_plan: "docs/execution/plans/2026-11-07-convert-extract-index/implementation-plan.md"
verdict: "approved"
findings_count: 1
template_version: "2.2"
requested_verbosity: "standard"
agent: "codex-independent-reviewer"
loop_id: "s54-plan-2026-11-07-convert-extract-index"
round: 1
---

# Critical Review: 2026-11-07-convert-extract-index

> **Review Mode:** `plan` · **Verdict:** `approved` · **Ledger round:** 1

## Scope

Reviewed the working-tree implementation plan, task and D-373 brief for Session 54 / MEU-123 at HEAD `39ac742d123aa12bcad849f60008818ede359a61`. Applied the Materiality Gate and PR-1 through PR-9 to the requested delivery questions. Claude Code/Anthropic authored the plan; Codex/OpenAI performed this independent review.

**Intent anchor:** Session 54 gives `stream_index` one meaning, the Nth audio stream in ffprobe order, which is the N that FFmpeg's `-map a:N` selects. The service then picks an Extract's extension from that audio stream, plans All audio streams as positions 0 to k-1, and creates no job that asks for a track the file doesn't have. An Extract job saves no encoder. Proof is a real `.mp4` with one audio track and with two, through the real FFmpeg adapter.

**Intent achieved:** yes, as a plan. No High or Critical delivery finding was established. This does not certify implemented changes or unrun product suites.

No repository file was edited. Reviewer artifacts and generated media/databases were confined to `C:/Temp/av-kit`; Python bytecode writing was disabled. No pytest, Vitest, Playwright, session gate, application, network request or download was run. Other sessions' files and D-375 remain outside the review. The coordinator owns saving this complete report to the canonical path.

## Findings

| # | Severity | Blocking | Kind | Finding | File:Line | Recommendation | Status |
|---|----------|----------|------|---------|-----------|----------------|--------|
| F1 | Medium | no | behavior | **NO_RAW_CONSOLE / D-372 needs the HealthService precondition.** The assertion that raw `argv` reaches no stdout is true after HealthService installation. The standalone REAL_FFMPEG stack described for row 1 does not install it. An independent run of that exact service/SQLite/adapter shape printed `convert.finished argv=['-y', '-i', '<scratch input path>']`; database setup also printed its scratch DB path. Required Red failures can therefore expose these values in captured stdout. Production wiring constructs HealthService before the conversion service, and a positive control with HealthService removed the input filename from stdout, ring and file. Confidence: High. | `docs/execution/plans/2026-11-07-convert-extract-index/implementation-plan.md:176`; `:302`; `docs/execution/plans/2026-11-07-convert-extract-index/task.md:50`; `packages/core/src/avkit_core/services/health.py:164`; `packages/api/src/avkit_api/wiring.py:205` | In row 1, account for the logging lifecycle in the standalone fixture and assert the generated path marker is absent from rendered output, using the real health processor where applicable. Any discovered startup logging outside that setup remains subject to S10: fix in the row or obtain Mat's disposition. Qualify the blanket claim. | open |

**S10 escalation to Mat:** F1 is a measured raw-output path, explicitly raised here under the carried rule. It is not filed or accepted as a residual. It does not block the audio-position objective: production conversion logging is protected, the plan already requires action at S10, and the permitted row-1 test setup can address its own logging. Approval does not waive S10.

## Review questions

Paths below are relative to `P:/av-kit`; `plan` means this target's `implementation-plan.md`.

| Question | Assessment |
|---|---|
| **Q1 — Done** | Accepted for newly added jobs. Real `probe` supplies `[video 0, AAC 1, AC3 2]`; AUDIO_POSITION gives `[AAC, AC3]`; AUDIO_PLAN gives positions 0 and 1; EXTRACT_EXT produces `.m4a` and `.ac3`; `_jobs_for_path` saves those positions and names; `_dispatch` passes each saved number into `ExtractOptions`; the adapter selects `a:0` and `a:1` (`services/conversion.py:256-311`, `:549-558`; `media/adapter.py:403-486`, `:625-639`). First mode selects position 0 and `.m4a`. The current real stack reproduced `.mka` in First and wrong positions in All, while direct valid-position extraction produced the expected single audio tracks. No remaining mismatch was found in the proposed path. |
| **Q2 — AUDIO_POSITION** | Accepted. The adapter preserves every ffprobe stream dictionary as StreamInfo, including audio whose codec name is unknown; audio type determines membership, not codec, language, channel count or disposition (`adapter.py:445-458`). FFmpeg's lowercase `a` counts audio streams, including audio that would fail a stronger usability filter; the plan adds no such filter. Sorting by the real stream index gives demuxer stream order. `None` denotes absent position information; a real empty stream list denotes zero known audio tracks. The inspected production adapter always returns a list, and the relevant default fake uses `streams=None`. Moving the service preserves the adapter's existing wire meaning and stored-job dispatch. |
| **Q3 — AUDIO_PLAN / naming** | Accepted. The existing token condition uses All mode and `len(plans) > 1`, so one track remains `<stem>_a.m4a`, while two tracks become `<stem>_a0.m4a` and `<stem>_a1.ac3` (`conversion.py:265-269`, `:359-368`). Distinct positions also distinguish same-codec outputs. Existing existence checks, reservations, numeric collision suffixes and `skip_existing` decisions operate on the resulting path without depending on global stream indices. The unchanged AC-30.13 guards cover the same-codec shape. No collision or skip regression was identified. |
| **Q4 — EXTRACT_EXT** | Accepted. The audio-position lookup selects AAC rather than the leading picture. `audio_codec` describes only the first audio stream (`adapter.py:468-471`), so limiting the fallback to position 0 is correct. A known empty list or a known position past the end must not fall back to the first stream; `.mka` is an appropriate unused output name for the Failed row. AC-123.5 exercises the previously wrong unknown-position-1 fallback with an existing fake. |
| **Q5 — MISSING_TRACK** | Accepted with the stated retry boundary. The Failed-at-add path preserves output resolution/reservation and returns a normal job in the API's 201 items envelope (`routes/conversions.py:149-157`); GUI and MCP already accept job status/error fields. It raises no batch-wide exception, so other probed files continue. Both messages contain only fixed text, position and count. `_next_pending` ignores Failed rows (`conversion.py:448-455`). Retry really clears the error and changes the stored row to Pending without re-probing (`domain/conversion.py:328-337`), so it can reach FFmpeg and fail there; the plan expressly discloses that behavior instead of promising retry-time validation. |
| **Q6 — EXTRACT_NO_ENCODER / LEGACY_JOBS** | Accepted. `_gpu` is initially None and is populated only by `detect_gpu`; Compress still resolves it lazily when required (`conversion.py:140`, `:159-164`, `:487-488`). Nothing requires an Extract to prime the cache. The dispatch save still executes and clears a retried Extract's old label. Additional readers are persistence mappers, API serialization and GUI metadata; none requires a non-null encoder. A stored row retains its existing position/output path and reaches the same adapter argument, so no migration is required to preserve execution. The plan accurately discloses old Done labels and incorrectly planned legacy rows; re-adding is needed to obtain new plans/names. |
| **Q7 — PASS_THROUGH** | Accepted for semantics. The census additionally found database models/mappers/migrations, the queue response type, and `ConvertPage.tsx:544-550` feeding the metadata helper. These preserve the value; they do not translate a global index. API/MCP/UI request validation remains nonnegative and strict at its existing boundaries. Existing schema/MCP descriptions do not assert a conflicting global-index meaning; the GUI already renders `a:N`. Contract 08's other mentions say "Extract audio index" or name the field, which is consistent with the proposed explicit definition. The table can mention these extra storage/display pass-throughs without requiring product changes. |
| **Q8 — REAL_FFMPEG / CI_DESELECT** | Accepted. The pinned pair resolved exactly, and an independent offline lavfi probe generated all three stated stream layouts. A counting FFmpegAdapter subclass, real SQLite UoW, `start_processing` and joined worker ran successfully in the reviewer probe. For a module-scoped media fixture, use pytest's module-capable temporary-directory factory; keep each SQLite service stack function-scoped. AC-123.9 plus S8 pins the picture-first precondition; the no-audio negative counts a real `extract_stream` producer. CI's Tests step is the folded `uv run --locked --no-sync pytest tests/ --tb=short -q` command with its existing exclusions (`ci.yml:58-63`). Reading that string, appending `--collect-only`, and checking the differential with only the new deselect removed tests the real argv. That future collection check was not executed in this review. |
| **Q9 — Red / guards / PR-8** | Accepted as test designs. Every required case can fail by assertion on an existing public call: extension, position, initial status, final status/encoder, GPU-call count or recorded options. None needs either new helper imported. In particular, current no-audio jobs are Pending at add, current software-only Extract fails, and the legacy-label assertion fails. AC-123.8 and .9 are intentional passing guards. The exact row-1 selection contains 16 required case titles, including all three .4 cases, both .6 tests, both .10/.11 fixture ids and both .12 mode ids. A synthetic receipt probe through the copied parser accepted those titles and refused a missing required case and a required NameError; `_1` cannot satisfy `_10`. No materially false-passing task control was demonstrated. S8 and S10 remain real execution stop conditions, not passing-test claims. |
| **Q10 — raw values / order / safety / D-373** | Accepted except F1's unconditional logging claim. The fixed-map extension and MISSING_TRACK text add no raw codec/path/title interpolation. Active HealthService drops `argv`; the standalone lifecycle exception is measured and raised above. Baseline sync is offline, CI collection sets UV_OFFLINE, fixtures use local lavfi inputs, and no row authorizes a network operation or download. The identity copy binds the work tree, tests/config/scripts/registers and both ignored FFmpeg binaries by explicit hashes; later artifact exclusions do not remove those inputs. Files Modified plus project files and D-375's recorded baseline paths cover the stated work. The explicit CRLF preservation requirement is sufficient; `newline=""` must be paired with preserving the original text bytes/endings when reading/editing, not a normalized whole-file rewrite. D-373's underlying Cut defect, three actions, genuine do-nothing path and amendment requirement are supported by the current dispatch/adapter. Its two wording qualifications are below; no preference is decided here. |

## Non-blocking wording clarifications

- **D-373, `human-gate-decision.md:7`, `:14`:** qualify the NVIDIA example by the configured preference, such as Auto/NVIDIA. Software preference can already save `libx265`. Also, accurately labelling today's fixed `libx265` re-encode does not itself decide whether a future Cut should support GPU encoding. The explicit widening action at `:41` changes the saved label and unused detection, not the adapter's actual Cut codec. These are brief corrections, not grounds for another review cycle by themselves.
- **PASS_THROUGH, `plan:159-169`:** the additional persistence and `ConvertPage` pass-throughs identified in Q7 do not introduce another meaning or a missing runtime change.

## Checklist Results

The results assess plan readiness and this review's observations; they are not Green test results.

### Information Retrieval (IR)

| Check | Result | Procedure / decisive evidence |
|---|---|---|
| Source-backed ACs and scope | pass | Mat's brief, issue records looked up by id, contract 08:172-181 / 462-478 / 593-605, FIC and D-364 through D-375 agree on the required audio-position behavior. D-373 remains Mat's preference. |
| Named executable sources / inventory | pass | Read designated Session 53 checker/baseline/gate sources and current production/test callers. Future scripts and integration module have explicit creation rows. No material missing unscheduled executable was identified. |
| Status / identity | pass | HEAD is `39ac742d123aa12bcad849f60008818ede359a61`; target implementation rows remain unchecked; targeted tracked diff lists no changed product/test/CI/spec path. Git emitted the expected inaccessible global-ignore warning; no global status or secret file was read. |

### Design Review (DR)

| Check | Result | Procedure / decisive evidence |
|---|---|---|
| PR-1 Plan/task alignment | pass | Compared all implementation rows, contracts, test selections and gate stages. |
| PR-2 Not started | pass | Working-tree plan is draft; rows 0-4 remain unchecked; source still exhibits both registered defects. |
| PR-3 Task contract | pass | Tasks name owner, deliverable, validation, dependencies and status. |
| PR-4 Validation realism | pass | Ran an independent real-stack probe and checked runner/fixture shapes; future scripts are scheduled, not falsely claimed present. |
| PR-5 Source-backed planning | pass | Compared the FIC with the brief, D-227 and contract 08; disclosed retry/legacy decisions are explicit. |
| PR-6 Handoff/review readiness | pass | One MEU and explicit review/handoff targets; round-2 census requirements are inapplicable. |
| PR-7 Scope discipline | pass | No required First/All/encoder behavior is silently deferred; legacy rows, retry and Cut boundaries are explicit. |
| PR-8 Observable controls | pass | Existing option recorder, counted real adapter method, final stored rows, fixture probes and copied Red parser have reachable producers and negative cases. F1 records the separate logging lifecycle caveat. |
| PR-9 Single-statement contracts | pass | Named contracts govern the behavior; repeated AC/row applications do not present materially competing operative rules. |

### Post-Implementation Review (PR)

| Check | Result | Procedure / decisive evidence |
|---|---|---|
| AV-1 through AV-6 as plan designs | pass | Required Red assertions, unchanged Green expectations, meaningful counters, source labels and explicit CI deselection are specified. Actual future Red/Green receipts are not claimed. |
| Implementation evidence / full gates | n/a | Implementation has not begun. No product suite or CI collection was run here. |
| Report consistency | pass | Report and verdict are bound to this target, loop and round; only temporary artifacts were written. |

### Decisive evidence

```json
{"schema_version":"evidence.v1","check_id":"s54-independent-real-stack-probe","command":"$env:PYTHONDONTWRITEBYTECODE='1'; $env:PYTHONIOENCODING='utf-8'; $env:RECEIPTS_DIR='C:/Temp/av-kit'; rtk proxy .venv/Scripts/python.exe -B C:/Temp/av-kit/s54-review-probe.py","cwd":"P:/av-kit","scope":"Current real ConversionService, SQLite UoW and pinned FFmpegAdapter; generated local MP4s; copied Red parser with synthetic receipts; no test runner","phase":"review","exit_code":0,"result":"pass","tested_state":"39ac742d123aa12bcad849f60008818ede359a61; working-tree plan hashes below; current unchanged conversion source","output":"Fixtures: one_track=[(0,video,mpeg4),(1,audio,aac)], two_track=[(0,video,mpeg4),(1,audio,aac),(2,audio,ac3)], no_audio=[(0,video,mpeg4)]. Current First: position 0, _a.mka, Done with hevc_nvenc for both audio fixtures. Current All: one_track position 1 Failed; two_track positions 1 Done and 2 Failed. Current no_audio: Pending at add, one extract call, Failed after worker. Direct real-adapter a:0 -> AAC on both, a:1 -> AC3 on two_track. All workers joined and stopped. All 16 required case titles accepted by copied parser; missing required case and required NameError refused. Standalone captured stdout contained one_track.mp4 in raw argv (6 argv lines); with real HealthService installed, convert.finished remained in stdout/ring/file and the input filename was absent from all three. Review probe PASS: current defects reproduced and valid positions confirmed."}
```

The standalone example was `convert.finished argv=['-y', '-i', 'C:\\Temp\\av-kit\\s54-review-n9suug6b\\one_track.mp4'] module=convert`. This generated scratch path is the positive control behind F1, not a user-media path copied into the report.

```json
{"schema_version":"evidence.v1","check_id":"s54-plan-source-trace","procedure":"Read the target plan, task and D-373 brief; trace probe/planning/extension/reservation/dispatch/extraction, retry, encoder cache, API/MCP/GUI/persistence and HealthService bootstrap; inspect Session 53 scripts and current CI Tests argv. Apply PR-1 through PR-9 and answer Q1 through Q10.","observer":"codex-independent-reviewer","cwd":"P:/av-kit","scope":"Session 54 MEU-123 working-tree plan","phase":"review","exit_code":null,"result":"pass","tested_state":"39ac742d123aa12bcad849f60008818ede359a61 plus reviewed working-tree plan","output":"Proposed audio-position algorithm, extension lookup, all-track plans and encoder save deliver the registered intent. No evidence-backed High/Critical delivery finding or materially vacuous task guard found. F1 is the measured standalone logging precondition, raised to Mat under S10. D-373's preference is not decided."}
```

Reviewed input hashes:

| Input | SHA-256 |
|---|---|
| `implementation-plan.md` | `70b6d18ade73a1f0ee9fe6c55395aa1d47ee879602e91814622520e317c90e3e` |
| `task.md` | `3f137fdf18b2ba1be5ee47597bbd77270bfe7384fed5db8a18e29da8f013e752` |
| `human-gate-decision.md` | `eba3780c29409d179b5f315ed7833497fd03fa4c40add13787c76b2e088f4a11` |
| `packaging/ffmpeg-win64/ffmpeg.exe` | `c46215f8889634396f0ac0acac738ef2145175e5b6caf28b3daa8ac9a9980c5f` |
| `packaging/ffmpeg-win64/ffprobe.exe` | `b77db2dfcbf08886d6a29bc1fabdceea3dd559751b03087205e3e13ec85c3e15` |

## Verdict

`approved` — the plan delivers the registered audio-position and Extract-encoder intent. One Medium non-blocking observation is explicitly raised under S10; there is no High or Critical delivery finding. Implementation, full-suite/CI results and execution approval remain unmeasured. This approval does not authorize execution, downloads, network requests, commits or pushes; the plan's human gate and D-373 remain in force.

🕐 Completed: 2026-11-07 19:13 (EST)
