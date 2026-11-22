---
project: "2026-11-21-transcript-job-resume"
date: "2026-11-21"
source: "Mat's request, 2026-11-21 (USER_EXPLICIT): 'can we add resume as action on the job in the 3 dot menu where the remove, open folder and compile options are?'; registered as MEU-163 in docs/build-plan/10-queue-card-ui.md §Per-job resume (residual) (triage D-1350, grouping D-1351); widened by Mat the same day (USER_EXPLICIT): 'also make adjustments to the defaults to make them these setting by default. Than add them to the review' (D-1355)"
meus: ["MEU-163"]
status: "draft"
template_version: "2.3"
---

# Implementation Plan: a Resume item in the Transcript job card's menu, and Mat's transcript defaults

> **Project**: `2026-11-21-transcript-job-resume`
> **Build Plan Section(s)**: 10 §Per-job resume (residual) (`docs/build-plan/10-queue-card-ui.md`, anchor `transcript-job-resume-residual`), matrix 10.12, registered at triage. Parent canon: 10 §Kebab menu (anchor `kebab-menu`), 11 TR1 and TR4, 03 §`TranscriptService` (`03-service-layer.md:878`).
> **Status**: `draft`. `plan_to_exec_gate: human`. Mat's two 2026-11-21 requests (the card Resume and the defaults), read with his 2026-11-18 hand-over ('make the decisions always the recommenations') and D-1351 ("run now through plan, execution and both Codex reviews"), is the execution approval once the Codex plan review approves and no stop item is open. The plan review approved at round 1 of loop `tjr-plan2-2026-11-21-transcript-job-resume` with no findings (2026-11-21), and no stop item is open, so execution is approved. Its one wording note is applied as D-1358. Nothing commits or pushes without Mat's words.

---

## Goal

**Goal anchor:** when a transcript job is `Paused` and no job is running, the job's card offers **Resume** first in its three-dot menu. A click sends the existing bodyless `POST /transcripts/resume`, and the job runs to the end. This works after an app restart, when the processor is `Idle`, which is the case the page cannot handle today. While a job runs, no card offers Resume, and the service refuses a resume (409), so a Paused job never becomes a second running job. The shipped transcript defaults become Mat's values: 20 requests an hour, 120 s between requests, 1 attempt, a 7 s retry delay, batches of 5 and 500 s between batches, in the core settings table, the MCP settings schema and the 06 defaults table. The toolbar, Start, the API routes, OpenAPI and the MCP tools stay as they are. Vitest, pytest and Electron tests prove it, one Electron test on the real backend with a seeded database. There is no manual check.

**Why.**

- **Mat hit it on 2026-11-21.** YouTube blocked caption requests from a VPN, and MEU-116 paused the job, as designed. After an app restart the job stayed `Paused` and the page had no way to resume it. Mat resumed it through the MCP tool `avkit_transcript resume`. The only other way out in the app is Remove, which drops the job's progress.
- **Mat, 2026-11-21:** "can we add resume as action on the job in the 3 dot menu where the remove, open folder and compile options are?"
- **Mat, 2026-11-16:** "This should be done with framework and scripts!" So the proof is tests in the gate.
- **Mat, 2026-11-21, after the plan's first review round:** he sent a screenshot of the Transcript settings (Requests Per Hour 20, Delay Between Requests 120, Max Retries 1, Retry Delay 7, Batch Size 5, Playlist End 0, Pause Between Batches 500, Max Words Per Pdf 490000), asked "can you configure these settings in av-kit now?", and then: "also make adjustments to the defaults to make them these setting by default. Than add them to the review". His own install already holds those values: they were set through `avkit_settings set` that day, and `output_dir` was not touched. This plan changes the shipped defaults (D-1355).

**What the code shows (plan-time reads at `HEAD` `159e178`, one worktree, `tjr99-probe.txt`):**

- **Root cause.** The processor state lives in memory (`TranscriptService._runtime`), and job status is stored. After a restart the job is `Paused` and the processor is `Idle`.
  - The toolbar shows Resume only while the processor is `Paused` (`TranscriptToolbar.tsx:47`; `controlEnabled('resume')` at `transcript-controls.ts:66`).
  - Start skips Paused jobs (`03-service-layer.md:878`; `test_ac_11_2_start_pending_only`, `test_services.py:1256`).
  - The card menu has no resume (`TRANSCRIPT_MENU_ORDER`, `transcript-card.ts:24`).
- **The service already resumes from Idle.** `resume_processing` (`transcript.py:239-273`) takes the first `Paused` job in queue order, moves it to `Processing` and starts the worker. It refuses only when the runtime is not Paused and no job is Paused. A plan-time probe seeded a Paused job with one Done item into a scratch `avkit.db`, built the real services with `build_services(app_data=…)`, and resumed from Idle. The job reached `Done` and wrote `probe-channel_raw.zip` and `compiled/probe-channel_vol1.md` (`plan-probe-seed.txt`).
- **The worker needs no network for that job.** `add_channel` enumerates the channel (`transcript.py:158-159`). The worker fetches only `Pending` items (`transcript.py:515-534`), then writes the volumes and the raw ZIP (`:560-562`). A Paused job whose items are all `Done` therefore reaches `Done` with no request.
- **The gap while a job runs.** With a job `Processing` and another job `Paused`, `resume_processing` finds the Paused job and moves it to `Processing` too, because the guard checks only "runtime not Paused and no Paused job". 03 already says resume is a 409 unless Paused (`03-service-layer.md:878`). A plan-time probe applied the guard of `RESUME_GUARD` in memory through a pytest plugin, and the transcript and API transcript tests passed 3 runs of 3, "34 passed, 88 deselected". Every call they make resumes from a runtime `Paused` (9 calls) or `Idle` (3 calls), never from `Processing` (`plan-guard-probe-r1.txt` to `-r3.txt`).
- **Renderer.**
  - `controlEnabled(control, ctx)` (`transcript-controls.ts:57`) switches over `QueueControl` (`:13-24`), with a `never` default.
  - `cardActionAvailable` (`transcript-card.ts:87`) sends `compile` to `down` through `controlEnabled` with `selectedId: card.id`. `cardMenuActions` filters `TRANSCRIPT_MENU_ORDER` by it. `CARD_ACTION_TESTIDS` (`:37`) is a full `Record`, so a new action needs its own test id. `LINK_CANDIDATES.Paused` is `[]`.
  - `TranscriptPage.tsx`: `ACTION_LABELS` (`:94`), `runCardAction` (`:320`, a `never` default that throws), and the menu map (`:383`, `disabled: busy`).
  - `transcript-commands.ts`: `queueContext()` (`:88`) and `resumeTranscripts()` (`:144`), which rechecks `controlEnabled('resume')` and then posts.
- **The API and MCP.** `POST /transcripts/resume` takes an optional empty body and returns 202 (`routes/transcripts.py:105-113`). `ConflictError` maps to 409 (`avkit_api/errors.py:38`). The MCP tool posts to the same route (`mcp-server/src/toolsets/transcript.ts:18`). None of them changes.
- **Tests to copy in shape.**
  - Vitest page harness: `ui/tests/unit/transcript-page.behavior.test.ts` (`item()`, `mockApi`, the fetch ledger, `renderPage`, `openMenu`; AC-55.3 at `:231-266`, AC-55.5 at `:334`).
  - Electron seam: `installTranscriptSeam` in `ui/tests/e2e/transcript-queue.test.ts:56-187`. It is not exported, so the new file carries its own small seam of the same shape.
  - Electron real backend: `ui/tests/e2e/queue-cancel-paused.test.ts` (`launch`, `readBackendPid`, `startTime`, `stopRecordedBackend`, `closeBounded`, `api`, the `live` set with `test.afterEach`).
  - A Python fixture run from Playwright: `capture-inbox.test.ts:3668` (`uv run --no-sync python -m tests.orientation_fixtures`).
  - pytest: `_transcript_stack` (`test_services.py:1197`) and `test_ac_11_2_start_pending_only` (`:1256`).
- **Startup.** `recover_stale_processing` (`transcript.py:361`, called at `avkit_api/main.py:46-47`) resets `Processing` jobs to `Pending`. `Paused` jobs stay `Paused`.
- **The defaults (D-1355).**
  - **Where they live.** The core table is `SETTINGS_KEY_TABLE` (`packages/core/src/avkit_core/services/settings.py:69-76`, CRLF; today 300, 6, 3, 30, 50, 300, 0, 490000). The MCP settings schema is `SETTINGS_SCHEMA.namespaces.transcript` (`mcp-server/src/toolsets/settings.ts:32-42`, CRLF; the same numbers). That schema is served as the `avkit://settings/schema` resource, and `mcp-server/tests/audit/fake-backend.ts` `defaults()` reads it. The canon is the 06 defaults table (`docs/build-plan/06-gui.md:1055-1062`, CRLF) and 03's MEU-116 rate-cap row (`docs/build-plan/03-service-layer.md:577`, CRLF), which reads "Default behaviour doesn't change: 6 s apart with a 300 s pause after 50 is already about 300 an hour."
  - **Not affected.** `openapi.committed.json` holds no setting default; its transcript schema is `number \| null` per leaf. The renderer's Settings page reads values from the API and holds no default.
  - **Existing installs.** `SettingsService.get` (`settings.py:221-229`) returns the table default only when no row is stored. So an install takes the new value for each key it never saved and keeps every value it saved.
  - **How the worker reads them.** `max_retries` counts attempts in total (`transcript.py:607`, `:614`), so 1 means the first block pauses the job after `retry_delay` (7 s) with no second request. The worker sleeps `delay_between_requests` before each item after the first, and adds `pause_between_batches` before every `batch_size`th item (`:525-528`). A simulation of that loop over 400 items gives at most 18 request starts in any rolling hour, about 16 an hour over a long run (`plan-defaults-rate.txt`). The cap of 20 therefore delays nothing with the defaults, and with 1 attempt there are no retries. 03:256 ("With the defaults and no retries the cap delays nothing") stays true. A 100-video channel takes about 6 hours.
  - **Tests that read the defaults.** A full pytest run with the six values applied in memory by a plugin (`plan-defaults-probe.txt`, mapped to test ids through `plan-collect.txt`, 3339 of 3339 positions) and a targeted run over `-k "transcript or settings or ac_11_ or ac_116"` (`plan-defaults-probe-targeted.txt`: 3 failed, 198 passed) found the same three:
    - `test_ac_116_5_default_cap_delays_nothing_without_retries` (`test_services.py:3085`) asserts the run's sleeps are within `{0.0, 6.0, 300.0}`. With the new defaults they are `{0, 120.0, 500.0}`.
    - `test_ac_116_9_a_retry_makes_the_default_cap_wait` (`:3091`) needs a retry and a cap of 300. With 1 attempt, the job pauses instead.
    - `test_ac_122_12_no_extra_request_per_video[50]` (`test_transcript_metadata.py:264`) uses a recording sleep but the real monotonic clock, so 50 requests meet a cap of 20 in real time. It sits in the cap wait past its 20 s join, and the worker thread then holds the process open (the full run hung after 100 %).
  - **The rest of the full run.** Its other failures, in `test_closeout_record_once.py` and `test_closeout_register_grammar.py`, came from running without `PYTHONIOENCODING=utf-8`. Without it, those two files fail alone too (`plan-closeout-noplugin.txt`: 45 failed). With it set and no plugin, they pass (`plan-closeout-utf8.txt`: 101 passed). Every row sets it.
  - **MCP tests.** None pins a transcript default by value: a grep of `mcp-server/tests` for the six keys and for 300 and 490000 finds only `backend-spawn.test.ts`'s 300 ms timeouts.
  - **The planned test edits, probed.** `test_defaults_rewrites_probe.py` (scratch) holds the planned forms: the new defaults test, 116.5 with the new literals, 116.9 with MEU-116's pacing set, and 122.12 with the cap off. Under the new defaults all five pass (`plan-defaults-rewrites-probe.txt`: 5 passed). Under today's defaults the defaults test and the new 116.5 fail by assertion, and the other three pass (`plan-defaults-rewrites-probe-old.txt`).

## Context Tool Decision

```yaml
context_tool_decision:
  phase: planning_and_execution
  eligible_tools: []
  decision: not_applicable
  eligibility_basis: "graphify-out/ and ui/graphify-out/ are absent (tjr99-probe.txt, 2026-11-21). The change is four renderer modules, one service method, new test files and docs, all read at plan time; a bypass class."
  human_message_reference: null
```

## Harness, driver and reviewer route

- **Driver:** Claude Code in the VSCode extension on Mat's Windows host. See `.agent/docs/harness-profiles.md` and the Claude Code block of `.agent/context/harness.local.md`.
  - Validation goes through `rtk proxy` with the receipt pattern. Task-cell commands run in pwsh.
  - Receipts go to `C:/Temp/av-kit/2026-11-21-transcript-job-resume/`. Execution receipts start `tjr-`; planning receipts start `tjr99-` or `plan-`.
  - Every row sets `RECEIPTS_DIR=C:/Temp/av-kit` and `PYTHONIOENCODING=utf-8`, and clears `ELECTRON_RUN_AS_NODE`.
  - Vitest runs from pwsh after `Set-Location 'P:\av-kit\ui'`, never from the Bash tool, and returns to `P:\av-kit`.
  - Playwright runs with `ELECTRON_RUN_AS_NODE` cleared and with `TMP` and `TEMP` set to `C:/Temp/av-kit/2026-11-21-transcript-job-resume/tmp`. Each Electron launch uses a scratch `AVKIT_APP_DATA` under that folder. No row stops a process by image name.
  - Before each Electron step, the host-load probe must read 50 % or less. A receipt that holds `unhandled rejection:` is a failure.
- **Working directory:** `P:/av-kit` on `main`. Use no branch and no worktree. Leave `.agent/fleet/hub` alone.
- **Cloud-local contract:** local, because the work runs Electron.
- **Reviewer:** Codex runs through `tools/Invoke-CodexDispatch.ps1` (`avkit_independent_reviewer`), with `AGENT_MODEL_REGISTRY_HOME=P:/.agent`.
  - Ledger loops: `tjr-plan2-2026-11-21-transcript-job-resume` and `tjr-execution-2026-11-21-transcript-job-resume`. The first plan loop, `tjr-plan-2026-11-21-transcript-job-resume`, ran one round of three and returned `changes_required` with one finding (F1, the stale cache in `CARD_RESUME_COMMAND`). Mat then widened the scope, and that loop's registered goal says MCP stays as it is, which no longer holds. So the plan review continues in `tjr-plan2-…` with the amended goal anchor. Its first prompt discloses loop 1, its round and F1, and asks for F1 to be rechecked (D-1357). Loop 1 gets no further round.
  - Caps come from `.agent/review-limits.json`: 3 plan rounds and 6 execution rounds. This plan carries no `review_limits` block.
  - Claude wrote the plan, so the reviewer is from a different vendor. The fallback is Mat.
  - The dispatch console goes to its own console file, never into the run log.
- **Never in these rows without Mat's words:** commit, push, or writing an `approved` verdict. Mat pushes himself.

## Handoff Set

| Scope | Canonical handoff |
|---|---|
| MEU-163 Transcript job resume | `.agent/context/handoffs/2026-11-21-transcript-job-resume-MEU-163-handoff.md` |

Rolling reviews:

- `.agent/context/handoffs/2026-11-21-transcript-job-resume-plan-critical-review.md`
- `.agent/context/handoffs/2026-11-21-transcript-job-resume-implementation-critical-review.md`

## Work Packages and Context Lifecycle

| ID | Work | depends_on | context_strategy | durable_outputs |
|---|---|---|---|---|
| WP-1 | Baseline and plan-local scripts (row 0) | — | shared | `baseline.sha`, `baseline-scope.json`, `baseline-eol.json`, `baseline-pins.json`, `red-check.py`, `identity.py`, `eol-check.py`, `host-wait.py`, `row-check.py` |
| WP-2 | All Reds: pytest, Vitest, Electron and the fixture (rows 1, 2 and 3) | WP-1 | shared | The two pytest tests, `transcript-job-resume.test.tsx`, `transcript-job-resume.test.ts`, `tests/transcript_paused_fixture.py`, the Red hashes |
| WP-2a | Defaults Red (row 3a) | WP-2 | shared | `test_transcript_defaults.py`, `transcript-defaults.test.ts`, the three named test edits, their Red hashes |
| WP-3 | Service Green (row 4) | WP-2a | shared | `transcript.py` `RESUME_GUARD` |
| WP-3a | Defaults Green (row 4a) | WP-3 | shared | `settings.py` and `settings.ts` per `TRANSCRIPT_DEFAULTS`; the MCP build |
| WP-4 | Renderer Green (row 5) | WP-3a | shared | `transcript-controls.ts`, `transcript-card.ts`, `transcript-commands.ts`, `TranscriptPage.tsx` |
| WP-5 | Electron proof (row 6) | WP-4 | shared | The run receipts |
| WP-6 | Canon, register and status (row 7) | WP-5 | shared | Index row, 10 Delivered note, the 06 defaults table and the 03 rate-cap row, the issue resolved, MEU-163 `ready_for_review` |
| WP-7 | Closeout (H1, H2) | WP-6 | `compact_continue` | The handoff, the review, the reflection, the commit draft |

## User Review Required

> [!IMPORTANT]
> **No question is open for Mat.** D-1352 to D-1354, D-1356 and D-1357 are reversible agent choices made under Mat's 2026-11-18 hand-over. D-1355 is Mat's own ruling on 2026-11-21: "also make adjustments to the defaults to make them these setting by default". It covers the M items the defaults touch, which are the MCP schema's default values (M-4) and the three named test edits (M-7) (§Decision Log). The do-nothing option for each decision is written in its entry.
>
> **What changes for you:**
>
> - A Paused transcript job shows **Resume** at the top of its ⋮ menu, above Compile, Open folder and Remove, when no job is running. Click it and the job continues from where it stopped. This works after a restart too.
> - If several jobs are Paused, only the first one in the queue offers Resume. When it is done or running, the next one offers it. The service resumes the first Paused job, so a Resume on another card would start the wrong job.
> - While a job runs, no card shows Resume. The toolbar is unchanged: Start, Pause or Resume, Stop. Start still skips Paused jobs.
> - A resume sent through the API or MCP while a job runs now gets a 409 instead of starting a second job.
> - **The shipped transcript defaults become your values:** 20 requests an hour, 120 s between requests, 1 attempt, a 7 s retry delay, batches of 5 and 500 s between batches. Playlist end (0) and max words per document (490000) already match.
>   - An install takes a new default only for a key it never saved. A value saved in Settings stays as it is, and nothing is migrated. Your install already holds these values, saved on 2026-11-21.
>   - With 1 attempt, the first block pauses the job after 7 s, with no retry. Resume continues it.
>   - The pace is about 16 videos an hour, at most 18 in any hour, so the cap of 20 never waits. A 100-video channel takes about 6 hours; with the old defaults it took about 15 minutes.
>   - The MCP server's settings schema shows the same defaults. Your MCP client runs the built `mcp-server/dist/`, so row 4a rebuilds it, and the running server shows the new defaults after a reconnect.

## Proposed Changes

### Single-statement contracts

- **`CARD_RESUME_RULE`.** `controlEnabled('resume-job', ctx)` is true only when the selected item's status is `'Paused'`, it is the first item with status `'Paused'` in `ctx.items` order, and `ctx.processorState !== 'Processing'`. It is false for no selection and for an id that is not in `ctx.items`.
- **`CARD_RESUME_MENU`.** `'resume-job'` is the first entry of `TRANSCRIPT_MENU_ORDER`, before `'requeue'`. `CARD_ACTION_TESTIDS['resume-job']` is `'resume-job-btn'`, so it never clashes with the toolbar's `resume-btn`. `ACTION_LABELS['resume-job']` is `'Resume'`. The item is not destructive. `cardActionAvailable` sends `'resume-job'` to `controlEnabled` with `selectedId: card.id`, like `compile`. `LINK_CANDIDATES.Paused` stays `[]`, so the card has no Resume link.
- **`CARD_RESUME_COMMAND`.** `resumeTranscriptJob(id)` in `transcript-commands.ts` never decides on cached data: it always sends `GET /transcripts`, parses the answer with `parseListEnvelope`, writes it into the query cache with `queryClient.setQueryData(QUERY_KEY, envelope)`, and evaluates `controlEnabled('resume-job', { items, processorState, selectedId: id })` on that fresh envelope. When the rule is false it sends nothing more. Otherwise it sends `apiFetch('/transcripts/resume', { method: 'POST' })` with no body. It invalidates the transcript query in a `finally`, so a refused POST (a 409 if a job started in the moment between the two requests) still refreshes the page, and the error still reaches `run`, which shows it. The toolbar commands and `queueContext()` do not change. `runCardAction`'s new `'resume-job'` case calls it through `run`, like `requeue`. (Plan review round 1, F1: `queueContext()` returns any cached envelope without a request, so a stale cache could resume a job other than the clicked one, or hide a valid Resume.)
- **`RESUME_GUARD`.** In `TranscriptService.resume_processing`, the first statement inside `with self._lock:` raises `ConflictError("resume_processing requires Paused")` when `self._runtime.state is QueueProcessorState.Processing`. Nothing is read or written before it. The rest of the method is unchanged.
- **`PAUSED_FIXTURE`.** `tests/transcript_paused_fixture.py` (LF), run as `uv run --no-sync python -m tests.transcript_paused_fixture <app_data>`, builds the real services with `build_services(app_data=<app_data>)`. It writes one raw file at `<app_data>/out/resume-fixture/raw/vid00000001.md` and stores one `TranscriptJob`: channel name `Resume Fixture`, status `Paused`, `error_message` "Paused: YouTube blocked caption requests.", `video_count` 1, `transcripts_done` 1, `zip_path` None, `queue_position` 0 and `output_dir` `<app_data>/out/resume-fixture`. It stores one `TranscriptItem` with status `Done`, that path and a word count. It writes through `services.transcript._uow_factory()` (`add_job`, `replace_items`, `commit`), disposes the services, and prints `fixture: paused job <id>`. It refuses an `<app_data>` outside the system temp folder and `C:/Temp`, and it uses no network.

- **`TRANSCRIPT_DEFAULTS`.** The defaults of six keys change, and only on these lines:
  - **Core** (`settings.py:69-74`): `requests_per_hour` 300 → 20, `delay_between_requests` 6 → 120, `max_retries` 3 → 1, `retry_delay` 30 → 7, `batch_size` 50 → 5, `pause_between_batches` 300 → 500. Each line keeps its type and `min_number=0`.
  - **MCP** (`settings.ts:34-39`): the same six values.
  - **Unchanged:** `output_dir`, `playlist_end` (0), `max_words_per_document` (490000), every other namespace, the zod input schema at `settings.ts:122-127` and the OpenAPI document.
  - **Edits:** byte replacements of the one number on each line. Both files stay CRLF.
- **`DEFAULTS_CANON`.** In `06-gui.md`, rows 1055 to 1060 (CRLF) change in two cells:
  - The third cell takes the new default.
  - The fourth cell becomes `Mat 2026-11-21 (D-1355); was <old> per [Transcript §3](../../_inspiration/_transcript_pseudo_logic.md)`, with the row's old value.
  - Rows 1061 and 1062 do not change.

  In `03-service-layer.md:577` (CRLF), the middle cell becomes "`transcript.requests_per_hour` is enforced as a rolling cap over real requests. The defaults do not reach it: 120 s apart with a 500 s pause after each 5 requests, before the next, is at most 18 starts in any hour, under the cap of 20, and `max_retries` 1 makes no retry (Mat 2026-11-21, D-1355). Until Session 101 the defaults were 6 s apart with a 300 s pause after 50, about 300 an hour." The third cell becomes `Local Canon: triage D-220; D-1355`. 03:256 and 03:570 do not change. 570 is the 2026-11-04 registration note, calculated from the defaults of that time.
- **`MEU_116_PACING`.** A module constant in `test_services.py`, placed just before `def _four_hundred`. It holds the six values above with which MEU-116 was proved: `{"requests_per_hour": 300, "delay_between_requests": 6, "max_retries": 3, "retry_delay": 30, "batch_size": 50, "pause_between_batches": 300}`.
- **`DEFAULTS_TEST_EDITS`.** Exactly three existing tests change, and only as follows. The probe `test_defaults_rewrites_probe.py` holds each form (§What the code shows).
  - **`_four_hundred`.** It gains the keyword `pacing: dict[str, int] | None = None`. In its unpacking, `_settings` becomes `settings`. After that line, `for key, value in (pacing or {}).items():` / `settings.set("transcript", key, value)` applies it.
  - **AC-116.5.** In `test_ac_116_5_default_cap_delays_nothing_without_retries`, the literal `{0.0, 6.0, 300.0}` becomes `{0.0, 120.0, 500.0}`. Its call and the rest of its body stay as they are.
  - **AC-116.9.** `test_ac_116_9_a_retry_makes_the_default_cap_wait` is renamed `test_ac_116_9_a_retry_makes_a_300_an_hour_cap_wait`. Its call becomes `_four_hundred(tmp_path, retries=1, pacing=MEU_116_PACING)`, and its five assertions do not change. No register or doc cites either function name (`git grep`, 2026-11-21).
  - **AC-122.12.** In `test_ac_122_12_no_extra_request_per_video` (`test_transcript_metadata.py`, LF), `_settings` becomes `settings` in the unpacking. After the `_listed_stack(...)` call, the new line `settings.set("transcript", "requests_per_hour", 0)` turns the cap off. Its assertions do not change.
  - **Why each changes.** 116.5 checks that the defaults' sleeps are only the pacing sleeps; the literal names those sleeps. 116.9 checks the cap under a retry at 300 an hour, which the new defaults cannot reach. 122.12 counts requests per video, not pacing, and it runs on the real clock.

### MEU-163: Per-job resume

1. **Rule.** Add `| 'resume-job'` to `QueueControl` and a `case 'resume-job':` to `controlEnabled` per `CARD_RESUME_RULE` (`transcript-controls.ts`, LF).
2. **Menu.** Add `'resume-job'` first in `TRANSCRIPT_MENU_ORDER`, its test id in `CARD_ACTION_TESTIDS` and its case in `cardActionAvailable` per `CARD_RESUME_MENU` (`transcript-card.ts`, CRLF).
3. **Command.** Add `resumeTranscriptJob(id)` per `CARD_RESUME_COMMAND` (`transcript-commands.ts`, LF).
4. **Page.** Add `ACTION_LABELS['resume-job']` and the `runCardAction` case (`TranscriptPage.tsx`, CRLF). The menu map needs no change.
5. **Service.** Add `RESUME_GUARD` (`transcript.py`, LF).
6. **Index.** Add the row `` | `transcript:resume_job` | Card menu Resume (first Paused job) | no | `POST /transcripts/resume` | specified | 10 / 06 | `` after `transcript:resume` in `gui-actions-index.md` (CRLF).
7. **Defaults.** Apply `TRANSCRIPT_DEFAULTS` to `settings.py` and `settings.ts`, then rebuild `mcp-server/dist/` with `npm run build` (row 4a). Apply `DEFAULTS_CANON` to 06 and 03 (row 7).

### Test pins

Row 0 records each pin file's SHA-256 in `baseline-pins.json`, and the gate checks that each one is unchanged.

| Pin | What it checks | After this change |
|---|---|---|
| `ui/tests/unit/transcript-page.behavior.test.ts` (CRLF) AC-55.3 (`:231-266`) | Three-action toolbar; no `resume-btn` while Idle; the Pause/Resume swap | Unchanged. The toolbar is untouched |
| `ui/tests/unit/transcript-page.behavior.test.ts` AC-55.5 (`:334`) | Menu ids per card in `TRANSCRIPT_MENU_ORDER` | Unchanged. Its `SEED` has no Paused card, so no list gains `resume-job-btn` |
| `ui/tests/unit/transcript-page.test.ts` (LF) | `controlEnabled` and the page rules | Unchanged |
| `ui/tests/unit/gui-actions-audit.test.ts` (CRLF) | Index ids and the test ids that reach them | Unchanged. It lists no transcript card ids |
| `ui/tests/unit/layout-primitives.test.ts` AC-51.6 and `ui/tests/e2e/test-ids.ts` | The test-id registry prefix hash | Unchanged. `test-ids.ts` is not edited; the E2E file names `resume-job-btn` itself |
| `ui/tests/e2e/transcript-queue.test.ts` (LF) | The seam E2E of the page, the kebab (AC-55.7) and the toolbar | Unchanged; runs once in row 6 and in the gate |
| `tests/unit/test_services.py` AC-11 and AC-116 tests | Start skips Paused; resume only from Paused; the block pause; the rate cap | The file gains two tests in row 1. Row 0 records the source text of every `test_ac_11_` and `test_ac_116_` function in `baseline-pins.json`. Every one except AC-116.5 and AC-116.9 stays unchanged, and the gate compares them. Those two and `_four_hundred` change only per `DEFAULTS_TEST_EDITS` (D-1355, D-1356), and `row-check.py named-edits` checks that |
| `tests/unit/test_transcript_metadata.py` (LF) | The metadata listing; one request per video | Only `test_ac_122_12_no_extra_request_per_video` changes, per `DEFAULTS_TEST_EDITS`. Every other top-level node keeps its row-0 source (`named-edits`) |
| `mcp-server/tests/` (every file) | The MCP tools and the settings resource | Unchanged. The only new file is `transcript-defaults.test.ts`. `fake-backend.ts` derives its defaults from `SETTINGS_SCHEMA`, so it follows the change |
| `tests/unit/test_transcript_pause_wake.py` | Pause wakes a sleep | Unchanged. It sets its own pacing |

Any other existing test that fails after a Green is S5: an M-7 question, not a fix. The three named edits are M-7 rows approved by D-1355: each names the test and its new form.

### Boundary Inventory

| Surface | Schema Owner | Field Constraints | Extra-Field Policy |
|---|---|---|---|
| `POST /transcripts/resume` | `routes/transcripts.py` (`EmptyIn \| None`) | No body, or `{}`; 202, or 409 per `RESUME_GUARD` | Unchanged: `EmptyIn` refuses extra keys |
| Card menu | `transcript-card.ts` | `resume-job` only when `CARD_RESUME_RULE` holds | — |
| `tests/transcript_paused_fixture.py` | `PAUSED_FIXTURE` | One positional `app_data` under the temp folder | Any other argument is refused |
| `SETTINGS_KEY_TABLE` transcript defaults | `settings.py` | `TRANSCRIPT_DEFAULTS`; types and `min_number=0` unchanged | Unchanged: an unknown key is still refused |
| MCP `avkit://settings/schema` resource | `settings.ts` `SETTINGS_SCHEMA` | `TRANSCRIPT_DEFAULTS`; key set and types unchanged | Unchanged |

No API route, request body, OpenAPI document, MCP tool shape or database schema changes. No stored setting is written or migrated. Two published values do change: the defaults of six settings, in the core table and in the MCP settings schema. That is an M-4 item, and Mat's ruling D-1355 covers it. Outside the renderer, the other behaviour change is the 409 that 03 already specifies.

### Acceptance Criteria

- **Family.** MEU-163 uses AC-163.1 to AC-163.10. Vitest and Playwright titles start `AC-163.<n> ` with a space after. The pytest names start `test_ac_163_6_` and `test_ac_163_10_`.
- **New names fail by assertion at Red.** The Vitest file imports `transcript-commands` as a namespace and asserts `typeof mod.resumeTranscriptJob === 'function'` before it calls it. At Red, `controlEnabled('resume-job', …)` and `cardActionAvailable('resume-job', …)` return the string `'resume-job'` from their `never` defaults, so `toBe(true)` and `toBe(false)` both fail by assertion.
- **Guards** pass at Red: `test_ac_163_6_idle_resume_done`.

| AC | Type | Description | Source | Negative Test |
|----|------|-------------|--------|---------------|
| AC-163.1 | unit | `controlEnabled('resume-job', ctx)` per `CARD_RESUME_RULE`, over items `[a Paused, b Paused, c Done]`: true for `a` with the processor `Idle` and with it `Paused`; false for `a` while `Processing`, for `b`, for `c`, for `selectedId: null` and for an unknown id. With items `[x Pending, a Paused]`, true for `a`. | Human-approved (Mat 2026-11-21); D-1352 | Each false case above is a negative |
| AC-163.2 | unit | `TRANSCRIPT_MENU_ORDER` equals `['resume-job', 'requeue', 'retry', 'compile', 'view-compiled', 'open-zip', 'open-folder', 'remove']`. `CARD_ACTION_TESTIDS['resume-job']` is `'resume-job-btn'`. `cardMenuActions` gives `resume-job` first for the first Paused card while `Idle`, and no `resume-job` for the second Paused card. `cardLinkActions` for a Paused card is `[]`. | D-1352 | The second Paused card and the `Processing` state give no `resume-job` |
| AC-163.3 | unit | The page, rendered with `[Alpha Paused, Bravo Paused, Charlie Done]` and the processor `Idle`: Alpha's menu items' test ids start with `resume-job-btn`, whose text is `Resume`. Bravo's menu has no `resume-job-btn`. A click on Alpha's Resume sends exactly one `POST /transcripts/resume` with no body, and no other mutation. The toolbar's buttons are still `start-btn`, `pause-btn` and `stop-btn`, with no `resume-btn`. Rendered again with Alpha `Paused`, Bravo `Processing` and the processor `Processing`: no menu holds `resume-job-btn`. | Human-approved; 11 TR1; D-1352 | The `Processing` render and Bravo's menu |
| AC-163.4 | unit | `resumeTranscriptJob`, with the mocked `GET /transcripts` as the backend's truth and every case counting the ledger's GETs and POSTs: (a) cache and backend `[a Paused, b Paused]`/`Idle`, click `b`: one GET, no POST; (b) backend `Processing`, click `a`: one GET, no POST; (c) backend `Idle`, click `a`: one GET, then one bodyless `POST /transcripts/resume`; (d) cache `[a Paused, b Paused]`/`Idle` but backend `[b Paused, a Paused]`/`Idle`, click `a`: one GET, no POST, and the cache afterwards holds the backend's order; (e) cache `[a Paused]`/`Processing` but backend `[a Paused]`/`Idle`, click `a`: one GET, then one bodyless POST; (f) the POST answers 409: the call rejects with an `ApiError` of status 409 and the query is invalidated. | `CARD_RESUME_COMMAND` | The first two cases |
| AC-163.5 | check | The §Test pins pass with their row-0 hashes and source text: the unit pins in row 5 and the gate, `transcript-queue.test.ts` in row 6 and the gate, and the AC-11 and AC-116 pytest tests in rows 4 and 4a and the gate. The exceptions are AC-116.5, AC-116.9 and AC-122.12, which pass in their `DEFAULTS_TEST_EDITS` forms. | Local Canon; D-1355 | A failure is S5 |
| AC-163.6 | unit (pytest) | `test_ac_163_6_refused_while_processing`: a Paused job first and a Pending job second; `captions.hold = True`; `start_processing()`; after `captions.entered`, `resume_processing()` raises `ConflictError`, the Paused job is still `Paused` and the Pending job is `Processing`. Clean-up: `stop_processing()`, `captions.release.set()`, a bounded thread join. `test_ac_163_6_idle_resume_done` (guard): a Paused job whose items are all Done, resumed from `Idle`, reaches `Done`. | 03-service-layer.md:878; D-1353 | Without the guard the first test fails with "DID NOT RAISE" |
| AC-163.7 | integration | Electron with the new file's seam, which answers like the service: the first `Paused` job moves to `Processing` and the processor to `Processing`, with 202. Seed `[Alpha Paused, Bravo Paused, Charlie Done]`, processor `Idle`. Alpha's menu shows `resume-job-btn` first, with the text `Resume`; Bravo's menu has none. A click on it gives exactly one `POST /transcripts/resume` with no body in the seam's call list. After the refresh, Alpha's and Bravo's menus have no `resume-job-btn`, and the toolbar has no `resume-btn`. | D-1354 | Bravo's menu and the menus after the resume |
| AC-163.8 | integration | Electron on the real backend. `PAUSED_FIXTURE` seeds a scratch `AVKIT_APP_DATA`, and the app launches on it. The card `Resume Fixture` shows `Paused`, and the processor is `Idle` (`GET /transcripts`). A click on the card's menu Resume brings the job to `Done` within 30 s (polled through `GET /transcripts`), with `transcripts_done` 1 and a `zip_path`. The files `<out>/resume-fixture_raw.zip` and `<out>/compiled/resume-fixture_vol1.md` exist. The card shows `open-zip-link`. The test stops only the backend it started. | Human-approved (Mat 2026-11-21, 2026-11-16); D-1354 | At Red the menu has no Resume, and the job stays `Paused` |
| AC-163.9 | check | `gui-actions-index.md` holds the `transcript:resume_job` row of step 6 exactly once, after `transcript:resume`, and stays CRLF. | Local Canon (index rule: every user-visible action) | A missing or doubled row fails row 7 |
| AC-163.10 | unit (pytest and MCP Vitest) | `TRANSCRIPT_DEFAULTS`. `test_ac_163_10_transcript_defaults_are_mats_values` (`tests/unit/test_transcript_defaults.py`) asserts that `SETTINGS_KEY_TABLE[("transcript", key)].default` for the eight number keys equals `{requests_per_hour: 20, delay_between_requests: 120, max_retries: 1, retry_delay: 7, batch_size: 5, pause_between_batches: 500, playlist_end: 0, max_words_per_document: 490000}`. `test_ac_163_10_unsaved_key_reads_the_default` builds a `SettingsService` on a fresh `FakeUnitOfWork` through `SharedFakeFactory`, as `test_capture_service.py` `_stack` does. It asserts that `get("transcript", "requests_per_hour")` is 20, and that after `set(…, 42)` it reads 42 (`plan-defaults-unsaved-probe.txt` shows 300, then 42, today). `mcp-server/tests/transcript-defaults.test.ts`, titled `AC-163.10 …`, asserts that `SETTINGS_SCHEMA.namespaces.transcript` maps the same eight keys to `{ type: "number", default: <value> }` with the same values. Row 7's `defaults-canon` checks the 06 cells and the 03:577 text of `DEFAULTS_CANON`. | Human-approved (Mat 2026-11-21); D-1355 | At Red each value test fails by assertion with today's 300, 6, 3, 30, 50 and 300 |

#### Spec Sufficiency Table

| Behavior | Classification | Resolution |
|----------|---------------|------------|
| Resume in the job card's menu | Human-approved | Mat 2026-11-21; D-1350 |
| Which card offers it | Local Canon + agent decision | The service resumes the first Paused job, so only that card offers it (D-1352) |
| Toolbar and Start unchanged | Local Canon | 11 TR1; 03-service-layer.md:878 |
| Resume while a job runs | Local Canon | 409 (03-service-layer.md:878); D-1353 |
| Proof on the real backend | Human-approved | Mat 2026-11-16 ("framework and scripts"); D-1354 |
| The shipped transcript defaults | Human-approved | Mat 2026-11-21, with his Settings screenshot ("make them these setting by default"); D-1355 |
| How the three default-reading tests change | Agent decision | `DEFAULTS_TEST_EDITS`; D-1356 |

#### Files Modified

| File | Action | Summary |
|---|---|---|
| `ui/src/renderer/src/features/transcript/transcript-controls.ts` | modify (LF) | `resume-job` in `QueueControl`; `CARD_RESUME_RULE` |
| `ui/src/renderer/src/features/transcript/transcript-card.ts` | modify (CRLF) | `CARD_RESUME_MENU` |
| `ui/src/renderer/src/features/transcript/transcript-commands.ts` | modify (LF) | `resumeTranscriptJob` |
| `ui/src/renderer/src/features/transcript/TranscriptPage.tsx` | modify (CRLF) | Label and `runCardAction` case |
| `packages/core/src/avkit_core/services/transcript.py` | modify (LF) | `RESUME_GUARD` |
| `tests/unit/test_services.py` | modify (CRLF) | Two AC-163.6 tests, appended after `test_ac_11_3_resume_only_from_paused`; `MEU_116_PACING` and the `_four_hundred`, AC-116.5 and AC-116.9 edits of `DEFAULTS_TEST_EDITS` |
| `tests/unit/test_transcript_metadata.py` | modify (LF) | The AC-122.12 edit of `DEFAULTS_TEST_EDITS` |
| `tests/unit/test_transcript_defaults.py` | create (LF) | The two AC-163.10 pytest tests |
| `packages/core/src/avkit_core/services/settings.py` | modify (CRLF) | `TRANSCRIPT_DEFAULTS`, core |
| `mcp-server/src/toolsets/settings.ts` | modify (CRLF) | `TRANSCRIPT_DEFAULTS`, MCP |
| `mcp-server/tests/transcript-defaults.test.ts` | create (LF) | AC-163.10, MCP |
| `docs/build-plan/06-gui.md` | modify (CRLF) | `DEFAULTS_CANON`, rows 1055 to 1060 |
| `docs/build-plan/03-service-layer.md` | modify (CRLF) | `DEFAULTS_CANON`, line 577 |
| `tests/transcript_paused_fixture.py` | create (LF) | `PAUSED_FIXTURE` |
| `ui/tests/unit/transcript-job-resume.test.tsx` | create (LF) | AC-163.1 to AC-163.4 |
| `ui/tests/e2e/transcript-job-resume.test.ts` | create (LF) | AC-163.7 and AC-163.8 |
| `docs/build-plan/gui-actions-index.md` | modify (CRLF) | AC-163.9 row |
| `docs/build-plan/10-queue-card-ui.md` | modify (CRLF) | `> **Delivered (Session 101).**` note in §Per-job resume (residual) |
| `.agent/context/known-issues.yaml`, `.agent/context/known-issues.md` | modify (CRLF) | The issue resolved; the `.md` re-rendered |
| `.agent/context/meu-status.yaml`, `.agent/context/meu-registry.md`, `docs/BUILD_PLAN.md` | modify (LF) | MEU-163 status through `meu_status.py` |
| `.agent/context/grouping/2026-11-21-transcript-job-resume-session-grouping.md` | modify (LF) | §6 row 101 `executed (Session 101)` |
| `.agent/context/current-focus.md`, `docs/execution/metrics.md` | modify (CRLF) | Closeout |

The registration edits made before this plan (the grouping file, the issue, MEU-163 in `meu-status.yaml`, `meu-registry.md`, `BUILD_PLAN.md`, the 10 section, matrix row 10.12, `current-focus.md`, `triage-output.yaml`) are this session's own work. Row 0 lists them in `baseline-dirty.txt`, and they are committed with it.

### Project files

- **Plan-local scripts** live in this plan folder. Row 0 copies `baseline.ps1`, `red-check.py`, `identity.py`, `eol-check.py`, `host-wait.py` and `load-run.py` from `2026-11-20-help-quick-start/`, and `issue-resolve.py` from `2026-11-20-e2e-devpc-clipboard/`, and writes `row-check.py`. Row 4a writes `defaults-edit.py` and row 7 writes `canon-edit.py`. Both edit by bytes and refuse when a target line is not found exactly once. H1-2 writes `session-gate.ps1` from the help-quick-start copy.
- **Row 0 data:** `baseline.sha`, `baseline-dirty.txt`, `baseline-dirty-hashes.json`, `baseline-scope.json`, `baseline-eol.json`, `baseline-mcp-hashes.json` (every tracked and untracked file under `mcp-server/` outside `node_modules/` and `dist/`) and `baseline-pins.json`.
- **Read, never changed:** `TranscriptToolbar.tsx`, `useTranscriptQueue.ts`, `routes/transcripts.py`, `openapi.committed.json`, every `mcp-server/` file except `src/toolsets/settings.ts` and the new `tests/transcript-defaults.test.ts`, `packages/api/src/avkit_api/schemas/settings.py`, the renderer's `features/settings/`, `ui/tests/e2e/electron-app.ts`, `ui/tests/e2e/test-ids.ts`, `tests/orientation_fixtures.py`, `_inspiration/_transcript_pseudo_logic.md` and the §Test pins files.
- **State:** `docs/execution/metrics.md` (CRLF), `.agent/context/current-focus.md` (CRLF), the handoff, the rolling reviews and the reflection.
- **New names (`DECLARED_NEW`):** `resume-job`, `resume-job-btn`, `resumeTranscriptJob`, `transcript:resume_job`, `transcript_paused_fixture`, `test_transcript_defaults`, `transcript-defaults.test`, `MEU_116_PACING`, `test_ac_116_9_a_retry_makes_a_300_an_hour_cap_wait`.

## Out of Scope

| Item | Kind | Deferred-to MEU | Basis |
|---|---|---|---|
| A per-job resume route (`POST /transcripts/{id}/resume`) so any Paused card can resume | out-of-scope | — | D-1352: an API change (M-4) for a case the first-Paused rule covers |
| A toolbar Resume while the processor is `Idle` | out-of-scope | — | 11 TR1 keeps three actions; D-1350 |
| Start resuming Paused jobs | out-of-scope | — | 03-service-layer.md:878; D-1350 |
| Job order after a resume: an earlier `Pending` job can run before the resumed job finishes (`_next_job`) | out-of-scope | — | Existing worker order; Mat did not ask; no report of harm |
| Rewording the Transcript help topic `blocked` ("…then Resume.") | out-of-scope | — | Pinned word for word (`failure-reason-copy.test.ts:40-42`); the card now gives the Resume it names |
| A Resume link on the Paused card face | out-of-scope | — | Mat asked for the menu; `LINK_CANDIDATES.Paused` stays `[]` |
| Rewriting stored settings to the new defaults | out-of-scope | — | D-1355 changes defaults, not saved values; a saved value is the user's choice |
| Editing `_inspiration/_transcript_pseudo_logic.md` §3 | out-of-scope | — | Reference input, not canon; 06's source cell records the old value and its source |
| A Settings "reset to default" control | out-of-scope | — | Mat did not ask |

## BUILD_PLAN.md Audit

MEU-163 (`gui-transcript-job-resume`, phase 10, matrix 10.12) was registered as `pending` at triage. Row 7 sets it to `ready_for_review` with this plan's `execution_plan`, and H2-2 sets it to `approved`, both through `tools/meu_status.py update`. `meu-registry.md` and `docs/BUILD_PLAN.md` are regenerated by `tools/meu_status.py render`, never by hand:

```powershell
rtk proxy uv run python tools/meu_status.py render --check > C:/Temp/av-kit/2026-11-21-transcript-job-resume/tjr-render-check.txt 2>&1; $code=$LASTEXITCODE; Get-Content C:/Temp/av-kit/2026-11-21-transcript-job-resume/tjr-render-check.txt; exit $code
```

## Verification Plan

> [!IMPORTANT]
> Classify every command through `.agent/docs/output-evidence-policy.md`. Use `rtk proxy` for exact evidence.

### 1. Baseline (row 0)

`baseline.ps1` has the shape of `2026-11-20-help-quick-start/baseline.ps1`:

1. **Tree and host.** It prints `HEAD`, `git status --porcelain --untracked-files=all`, `git worktree list` and one host-load sample, and records `baseline.sha`, `baseline-dirty.txt` and `baseline-dirty-hashes.json`.
2. **Scope binding.** It records `baseline-scope.json`: the SHA-256 of each §Files Modified path and each "Read, never changed" path, or `absent`. Every new path must be `absent`. `current-focus.md`, `metrics.md` and `known-issues.yaml` and `.md` are recorded as `shared` with their hash, because another session may write them; the row that writes one re-reads it just before the edit. It also records `baseline-eol.json`, `baseline-mcp-hashes.json` and byte copies of the scope files under `C:/Temp/av-kit/2026-11-21-transcript-job-resume/baseline-copies/`.
3. **Pins.** `baseline-pins.json` holds the SHA-256 of each §Test pins file except `test_services.py` and `test_transcript_metadata.py`. For those two files it holds the source text, read with `ast`, of every top-level node, keyed by name. `pins-unchanged` compares every `test_ac_11_` and `test_ac_116_` function except AC-116.5 and AC-116.9.
4. **Citations.** It finds by text, once each, and records the current line of: `| 'open-folder'` and `case 'resume':` (`transcript-controls.ts`), `export const TRANSCRIPT_MENU_ORDER`, `export const CARD_ACTION_TESTIDS`, `export function cardActionAvailable`, `Paused: [],` (`transcript-card.ts`), `async function queueContext` and `export async function resumeTranscripts`, `const ACTION_LABELS` and `function runCardAction`, `def resume_processing` and `with self._lock:` inside it, `def test_ac_11_3_resume_only_from_paused`, the `transcript:resume` index row, `function installTranscriptSeam`, `async function launch(` (`queue-cancel-paused.test.ts`), `os.environ.get("AVKIT_APP_DATA"` in `packages/infrastructure/src/avkit_infra/database/engine.py` (`resolve_app_data`: the backend reads the fixture's app data; D-1359), the six `("transcript", "<key>"): SettingSpec("number", <old>, min_number=0),` lines (`settings.py`), the six `<key>: { type: "number", default: <old> },` lines (`settings.ts`), the six 06 rows of `DEFAULTS_CANON`, the 03 `| Rate cap |` row, `def _four_hundred`, `def test_ac_116_5_default_cap_delays_nothing_without_retries`, `def test_ac_116_9_a_retry_makes_the_default_cap_wait` and `def test_ac_122_12_no_extra_request_per_video`. A missing or doubled anchor is S2; a moved line is recorded.
5. **Free ids.** Every `DECLARED_NEW` name and `AC-163.` occur nowhere in the tree. D-1358 to D-1399 are unclaimed.
6. **Base receipts.** The full Vitest suite (`tjr-base-ui.txt`), the full pytest suite (`tjr-base-py.txt`, with `PYTHONIOENCODING=utf-8`) and the MCP suite (`tjr-base-mcp.txt`, `npm test` in `mcp-server/`). Their failures are recorded, not fatal, and the gate excuses only those ids.
7. **Plan-local scripts.** It copies the scripts of §Project files with this plan's `PLAN`, receipts folder, artifacts and `DECLARED_NEW`. `red-check.py`'s fixtures use AC-163 (it must refuse `AC-163.1` matching `AC-163.10`). `row-check.py` has the subcommands `red-record --row N FILE…`, `red-unchanged`, `pins-unchanged`, `red-reason RECEIPT --id ID --needle TEXT` (each failing test of that id has `TEXT` in its error block), `e2e-count RECEIPT N [--plain RECEIPT…]`, `index-row` (AC-163.9: the `transcript:resume_job` row occurs exactly once, on the line after the `transcript:resume` row, and `gui-actions-index.md` stays CRLF), `register` (by key with `yaml.safe_load`, every other issue in `known-issues.yaml` equals its row 0 copy and `TRANSCRIPT-PAUSED-JOB-NO-RESUME-AFTER-RESTART` differs only in `status`, `verification` and `resolution_path`; in the grouping file only §6 row 101 changed), `named-edits` (`DEFAULTS_TEST_EDITS`, by top-level `ast` node against `baseline-pins.json`: in `test_services.py` the changed or new nodes are exactly `MEU_116_PACING`, `_four_hundred`, AC-116.5, the renamed AC-116.9 in place of the old name, and the two `test_ac_163_6_` tests; in `test_transcript_metadata.py` only AC-122.12; and each changed node's source equals the form the script holds), `defaults-values` (`TRANSCRIPT_DEFAULTS`: by bytes against the row-0 copies, `settings.py` and `settings.ts` differ only in the six numbers on their six lines, and both stay CRLF) and `defaults-canon` (`DEFAULTS_CANON`: the six 06 rows and 03:577 hold the exact new text, no other line of either file changed, and both stay CRLF), each with a `--selftest`. It runs every selftest and `ruff format --check` and `ruff check` on the plan folder's Python.
8. **Secrets and the fleet hub.** The scope walk drops `.mcp.json`, `mcp-token.txt`, `.claude.json`, `.env`, `.claude/settings.local.json` and `.agent/fleet/hub` before any stat or read.

If any step except the base receipts fails, the row fails and nothing else runs.

### 2. Red, then Green

- **Every Red comes before any product change.** Rows 1, 2, 3 and 3a change no product file. Row 3 builds the unchanged app.
- **Each Red receipt holds an assertion failure, never a setup failure.** `red-check.py --require` names `test_ac_163_6_refused_while_processing` (row 1, pytest; "DID NOT RAISE" counts), AC-163.1 to AC-163.4 (row 2, Vitest), AC-163.7 and AC-163.8 (row 3, Playwright), and in row 3a both `test_ac_163_10_` tests and `test_ac_116_5_default_cap_delays_nothing_without_retries` (pytest) and AC-163.10 (MCP Vitest). In row 3a the renamed AC-116.9 and AC-122.12 pass, which proves their new setup works on today's defaults. Row 3 first runs `PAUSED_FIXTURE` on its own and requires `fixture: paused job`, and `row-check.py red-reason` requires `resume-job-btn` in each failing E2E test's error block, so a launch or seed failure is never a Red.
- **Expectations stay the same in Green** (S3). Rows 1, 2, 3 and 3a record the hashes of the test-side files they write, and rows 4 to 6 check them.
- **Green order.** Row 4 makes AC-163.6 pass. Its pytest selection leaves out AC-116.5, which stays Red until row 4a. Row 4a makes AC-163.10 and AC-116.5 pass, keeps the renamed AC-116.9 and AC-122.12 passing, and rebuilds `mcp-server/dist/`. Row 5 makes AC-163.1 to AC-163.4 pass. Row 6 makes AC-163.7 and AC-163.8 pass. Row 7 applies `DEFAULTS_CANON`.
- **Line endings** are checked by `eol-check.py` after each Green.
- **`test_services.py` is written twice before any Green**, in rows 1 and 3a. Row 3a records its hash again, and that record supersedes row 1's for `red-unchanged`.

### 3. Electron proof (row 6)

- `transcript-job-resume.test.ts` runs 3 times (`--repeat-each 3`): 6 `AC-163.` ok lines.
- `transcript-queue.test.ts` runs once (AC-163.5).
- `row-check.py e2e-count` requires the ok count and the `N passed` lines, and no `failed`, `flaky` or `unhandled rejection:` line.

### Session gate (H1-2)

`session-gate.ps1` has the shape of `2026-11-20-help-quick-start/session-gate.ps1`: one receipt per step, `tjr-D6-<step>`, fail-fast, later steps printed `not_run`, last line `session-gate: all steps exit 0`.

| Stage | Steps |
|---|---|
| Identity | `identity.py` before and after the run; the two must match |
| Static | `ui-types`, `ui-lint` (pwsh in `ui/`); `py-types` (`uv run pyright packages/`); `py-lint` (`uv run ruff check packages/ tests/`); `py-format` (`ruff format --check` on `tests/transcript_paused_fixture.py`, `tests/unit/test_transcript_defaults.py` and this plan folder's Python); `mcp-types` (`npm run typecheck`, pwsh in `mcp-server/`); `task-contract`; `scope-paths`; `line-endings`; `home-path` (`tools/check_home_path.py`); `pins-unchanged`; `named-edits`; `defaults-values`; `defaults-canon`; `red-unchanged`; the selftests |
| Targeted | `py-resume` (`uv run pytest tests/unit/test_services.py -k "ac_11_ or ac_116 or ac_163"`); `py-defaults` (`uv run pytest tests/unit/test_transcript_defaults.py "tests/unit/test_transcript_metadata.py::test_ac_122_12_no_extra_request_per_video"`); `ui-resume` (`transcript-job-resume.test.tsx` and the unit pins) |
| Host load | `host-load` before every Electron step (limit 50 %) |
| Fresh full | `ui-tests` (full Vitest); `py-tests` (`uv run pytest tests/ -x --tb=short -q`, with `PYTHONIOENCODING=utf-8`); `mcp-tests` (`npm test` in `mcp-server/`); `mcp-build` (`npm run build` in `mcp-server/`); `openapi` (`uv run python tools/export_openapi.py --check openapi.committed.json`); `ui-build`; `e2e-transcript-job-resume`; `e2e-transcript-queue`; `state-render` (`meu_status.py render --check`) |
| Skipped, with reason | The rest of `test:e2e`: only the Transcript card, one service method and six default values changed. The Transcript suites run, and the Settings page reads values from the API and holds no default. `mcp-server` `npm run audit`: it drives a fake backend whose defaults come from `SETTINGS_SCHEMA`, and `mcp-tests` runs its unit tests |

## Stop Conditions

| ID | Condition | Action |
|---|---|---|
| S1 | A `graphify-out` graph appears | Re-decide the context tool |
| S2 | Row 0 finds a citation anchor missing or doubled, or a free id taken | Stop and bring the receipt to Mat. A moved line is corrected, not a stop |
| S3 | A Red receipt fails `red-check.py` or `red-reason`, or a Green row needs a changed expectation | Fix the test setup; never edit an expectation in Green |
| S4 | A path outside this plan's scope and `baseline-dirty.txt` changes, or a scope path changes by another hand | Stop and re-baseline with Mat. Never commit, stash or revert another session's work |
| S5 | An existing test fails after a Green | Rerun it alone once. If it fails again, stop: an M-7 question, not a fix |
| S6 | Codex is unavailable or the ledger refuses | Mat |
| S7 | An Electron test fails in any of row 6's runs, or a receipt holds `unhandled rejection:` | Stop and bring the receipts to Mat. Never raise a timeout or add a retry |
| S8 | The seeded job does not reach `Done` on the real backend without the network, or the backend does not read the fixture's app data | Stop and route back to the plan |
| S9 | After row 4a, a test outside `DEFAULTS_TEST_EDITS` fails or hangs because of the new defaults | Stop: an M-7 question for Mat. Never add a fourth edit without a plan row |

## Decision Log

> [!NOTE]
> D-1352 to D-1354, D-1356 and D-1357 are autonomous, with `mandatory: none`, made under Mat's hand-over (USER_EXPLICIT 2026-11-18: 'make the decisions always the recommenations'). Each passed the §4a list and the §4 test. D-1355 is `resolution: human`: Mat's own ruling (USER_EXPLICIT 2026-11-21). D-1350 (triage) and D-1351 (grouping) are read from `known-issues.yaml` and the grouping file. The M items:
>
> - **M-4.** No API route, body, OpenAPI document or MCP tool shape changes. The 409 of D-1353 is the one 03 already specifies. The default values in the MCP settings schema do change, and D-1355 rules that: Mat asked for exactly these defaults.
> - **M-2 clear.** No user data is read or written. Every Electron launch uses scratch app data, and no stored setting is migrated.
> - **M-7.** Three existing tests change, each named with its new form in `DEFAULTS_TEST_EDITS`. They are the M-7 rows that D-1355 needs, and D-1356 chose how they change. No other assertion changes.
> - **M-8.** The scope widened at Mat's word (D-1355), and the plan review restarts in a disclosed loop (D-1357).
>
> Execution decisions take D-1358 to D-1399.

```yaml
decision_log:
  - id: D-1352
    stage: planning
    question: "Which Paused job card offers Resume, and what does it send?"
    resolution: autonomous
    class: two-way
    mandatory: none
    chosen: "A: only the first Paused job in queue order offers Resume, and only while the processor is not Processing (CARD_RESUME_RULE); it sends the existing bodyless POST /transcripts/resume, which resumes that same job."
    source_tag: Local Canon
    precedents:
      - "packages/core/src/avkit_core/services/transcript.py:239-273 — resume_processing takes the first Paused job in list_jobs_ordered()"
      - "docs/build-plan/10-queue-card-ui.md §Kebab menu — an unavailable action is omitted"
      - "docs/build-plan/10-queue-card-ui.md §Per-job resume (residual) — the Card resume and Request rows (D-1350)"
      - "ui/src/renderer/src/features/transcript/transcript-commands.ts:144 — resumeTranscripts rechecks controlEnabled before the POST"
    research: { engine: none, sources: [] }
    reasoning: "Handed to the agent: USER_EXPLICIT 2026-11-18 'make the decisions always the recommenations'. Options: (A) the first Paused card only, existing route; (B) every Paused card, with a new POST /transcripts/:id/resume; (C) every Paused card, existing route; (D) do nothing and keep the MCP tool as the way out. A gives Mat's case (one job paused by a block) with no API change, and the card that offers Resume is the job that resumes. B is an API, OpenAPI and MCP change (M-4) for the rare case of several Paused jobs. C would resume a different job than the one clicked when two are Paused. D leaves the dead end Mat hit. Weakness of A: with two Paused jobs, the second shows Resume only after the first runs. Two-way: the rule is one switch case."
  - id: D-1353
    stage: planning
    question: "What does resume_processing do while a job is running?"
    resolution: autonomous
    class: two-way
    mandatory: none
    chosen: "A: refuse with ConflictError (409) when the runtime state is Processing, before any read or write (RESUME_GUARD)."
    source_tag: Local Canon
    precedents:
      - "docs/build-plan/03-service-layer.md:878 — resume is a 409 unless Paused"
      - "packages/core/src/avkit_core/services/transcript.py:250 — the current check lets a Paused job become a second Processing job while one runs"
      - "C:/Temp/av-kit/2026-11-21-transcript-job-resume/plan-guard-probe-r1.txt to -r3.txt — the guard applied in memory: 34 passed, 88 deselected, 3 runs of 3; no existing call resumes from Processing"
    research: { engine: none, sources: [] }
    reasoning: "Handed to the agent: USER_EXPLICIT 2026-11-18 'make the decisions always the recommenations'. Options: (A) the guard; (B) no service change, relying on the card rule; (C) do nothing. The card rule hides Resume while a job runs, but the API and the MCP tool can still post a resume, and the service then runs two jobs at once, which 03 forbids. A is one statement that matches 03 and no existing test calls resume while Processing. B and C leave that hole open to the MCP tool Mat used today."
  - id: D-1354
    stage: planning
    question: "How is the card Resume proved in Electron?"
    resolution: autonomous
    class: two-way
    mandatory: none
    chosen: "A: a new file ui/tests/e2e/transcript-job-resume.test.ts with two tests: AC-163.7 with its own small seam (the shape of installTranscriptSeam) for the menu rule and the one bodyless POST, and AC-163.8 on the real backend with a Paused job seeded into a fresh AVKIT_APP_DATA by tests/transcript_paused_fixture.py, run to Done with no network."
    source_tag: Local Canon
    precedents:
      - "ui/tests/e2e/transcript-queue.test.ts:56-187 — installTranscriptSeam, not exported"
      - "ui/tests/e2e/queue-cancel-paused.test.ts — the real-backend launch and teardown helpers"
      - "ui/tests/e2e/capture-inbox.test.ts:3668 — a Python fixture module run from Playwright with uv run --no-sync"
      - "C:/Temp/av-kit/2026-11-21-transcript-job-resume/plan-probe-seed.txt — the seeded Paused job resumed from Idle reached Done with the ZIP and the volume"
      - "Mat 2026-11-16: 'This should be done with framework and scripts!'"
    research: { engine: none, sources: [] }
    reasoning: "Handed to the agent: USER_EXPLICIT 2026-11-18 'make the decisions always the recommenations'. Options: (A) a new file with a seam test and a real-backend test; (B) add the seam test to transcript-queue.test.ts and export its seam; (C) seam only; (D) unit tests only. Only a real backend after a fresh launch shows Mat's case end to end: stored Paused, runtime Idle. A leaves transcript-queue.test.ts and its seam unchanged, which keeps the E2E-TRANSCRIPT-SEAM-RELOAD-FLAKE watch item out of this session. B edits a pinned file. C and D do not prove the restart case."
  - id: D-1355
    stage: planning
    question: "What are the shipped transcript defaults?"
    resolution: human
    class: product-preference
    mandatory: [M-4, M-7, M-8]
    chosen: "Mat's values (TRANSCRIPT_DEFAULTS): requests_per_hour 20, delay_between_requests 120, max_retries 1, retry_delay 7, batch_size 5, pause_between_batches 500; playlist_end 0 and max_words_per_document 490000 unchanged. In the core table, the MCP settings schema and the 06 defaults table, with 03:577 reworded (DEFAULTS_CANON) and the three named test edits (DEFAULTS_TEST_EDITS) as the M-7 rows."
    source_tag: Human-approved
    precedents:
      - "Mat 2026-11-21, with a screenshot of his Settings Configuration panel: 'can you configure these settings in av-kit now?'"
      - "Mat 2026-11-21: 'also make adjustments to the defaults to make them these setting by default. Than add them to the review'"
      - "packages/core/src/avkit_core/services/settings.py:221-229 — an unsaved key reads its table default"
      - "C:/Temp/av-kit/2026-11-21-transcript-job-resume/plan-defaults-rate.txt — at most 18 starts in any hour under the new defaults"
    research: { engine: none, sources: [] }
    reasoning: "Mat named the values and asked for them as the defaults, in his own words. The do-nothing option (keep 300/6/3/30/50/300 and leave his values as saved settings only) is what he ruled out. Reversible: six numbers in two files and six table cells."
    human_message_reference: "USER_EXPLICIT 2026-11-21 'also make adjustments to the defaults to make them these setting by default. Than add them to the review'"
  - id: D-1356
    stage: planning
    question: "How do the three tests that read the old defaults change?"
    resolution: autonomous
    class: two-way
    mandatory: none
    chosen: "A (DEFAULTS_TEST_EDITS): AC-116.5 keeps checking the defaults with the new sleep literal {0.0, 120.0, 500.0}; AC-116.9 sets MEU_116_PACING in its setup, keeps its assertions and is renamed for what it now checks; AC-122.12 turns the cap off in its setup."
    source_tag: Local Canon
    precedents:
      - "C:/Temp/av-kit/2026-11-21-transcript-job-resume/plan-defaults-probe.txt and plan-defaults-probe-targeted.txt — only these three fail or hang under the new defaults"
      - "C:/Temp/av-kit/2026-11-21-transcript-job-resume/plan-defaults-rewrites-probe.txt — the planned forms: 5 passed on the new defaults"
      - "C:/Temp/av-kit/2026-11-21-transcript-job-resume/plan-defaults-rewrites-probe-old.txt — on today's defaults the new defaults test and 116.5 fail by assertion, the rest pass"
      - "docs/build-plan/03-service-layer.md:256 — 'With the defaults and no retries the cap delays nothing'"
    research: { engine: none, sources: [] }
    reasoning: "Handed to the agent: USER_EXPLICIT 2026-11-18 'make the decisions always the recommenations'. Options: (A) per test: 116.5 keeps testing the defaults, 116.9 and 122.12 set the values they test; (B) set the old values in the setup of all three; (C) rewrite 116.9 for the new defaults; (D) do nothing, which fails two tests and hangs the suite. A keeps 116.5 a test of the shipped defaults (03:256 stays true and checked) and keeps 116.9's proof that the cap holds under retries at 300 an hour. B turns 116.5 into a test of old numbers, which proves nothing about the shipped defaults. C loses the retry case, because with 1 attempt there is no retry and 18 an hour never reaches the cap. Weakness of A: 116.9's name changes; no doc cites it."
  - id: D-1357
    stage: planning
    question: "Where does the plan review continue after the scope widened?"
    resolution: autonomous
    class: two-way
    mandatory: none
    chosen: "A: a new disclosed plan loop, tjr-plan2-2026-11-21-transcript-job-resume, with the amended goal anchor. Its first prompt discloses loop 1 (one round, changes_required, F1), shows F1's fix for recheck, and names the defaults addition. Loop 1 gets no further round."
    source_tag: Local Canon
    precedents:
      - ".agent/docs/model-routing.md:24 — a new loop must not evade a stop; loop 1 used 1 of 3 rounds and is at no stop"
      - "Loop 1's goal anchor says MCP stays as it is, and every prompt and verdict must contain the anchor"
    research: { engine: none, sources: [] }
    reasoning: "Handed to the agent: USER_EXPLICIT 2026-11-18 'make the decisions always the recommenations'. Options: (A) a new disclosed loop with the amended anchor; (B) round 2 in loop 1 under the old anchor; (C) do nothing and keep reviewing only the resume, with the defaults reviewed in a later session. B would review a plan against a goal it no longer has. C ignores Mat's 'add them to the review'. A carries F1 forward, so nothing loop 1 found is lost, and the loop is not at a stop."
  - id: D-1358
    stage: execution
    question: "How does DEFAULTS_CANON describe where the batch pause falls?"
    resolution: autonomous
    class: two-way
    mandatory: none
    chosen: "A: the 03 rate-cap text says 'a 500 s pause after each 5 requests, before the next', as the plan review's Q5 note asked."
    source_tag: Local Canon
    precedents:
      - "C:/Temp/av-kit/tjr-plan2-review-round-1.md §Q5 — first starts 0, 120, 240, 360, 480, 1100: the pause comes before request 6, then 11, not before every 5th"
      - "packages/core/src/avkit_core/services/transcript.py — inside `if index > 0:`, the pause applies when `index % batch_size == 0`"
    research: { engine: none, sources: [] }
    reasoning: "Handed to the agent: USER_EXPLICIT 2026-11-18 'make the decisions always the recommenations'. Options: (A) apply the reviewer's wording; (B) do nothing and keep 'before every 5th request'. B writes canon that misstates the worker's timing. The reviewer marked the note non-blocking with no further round, and the numbers do not change."
  - id: D-1359
    stage: execution
    question: "Row 0 finds no AVKIT_APP_DATA in packages/api/src/avkit_api/, the folder §Verification Plan 1 step 4 names. What does the anchor cite?"
    resolution: autonomous
    class: two-way
    mandatory: none
    chosen: "A: cite os.environ.get(\"AVKIT_APP_DATA\" in packages/infrastructure/src/avkit_infra/database/engine.py (resolve_app_data), found once, and continue row 0."
    source_tag: Local Canon
    precedents:
      - "packages/infrastructure/src/avkit_infra/database/engine.py:35-39 — resolve_app_data returns AVKIT_APP_DATA when it is set; the api package has no reference to it (git grep, 2026-11-21)"
      - "ui/src/main/index.ts:151 and :224 — the Electron main process reads AVKIT_APP_DATA for the backend it starts"
    research: { engine: none, sources: [] }
    reasoning: "Handed to the agent: USER_EXPLICIT 2026-11-18 'make the decisions always the recommenations'. S2 says a missing anchor goes to Mat; the hand-over decides it here. Options: (A) correct the citation to the file that reads the variable; (B) do nothing and stop at S2 until Mat answers. The anchor exists to show that the backend reads the fixture's app data, and it does, in the infrastructure package the api package imports. Only the cited folder was wrong; no behaviour, AC or row changes. The execution review sees this entry."
  - id: D-1360
    stage: execution
    question: "The gate's py-tests runs pytest with -x, and row 0's tjr-base-py.txt holds two failures this plan does not touch. How does the gate excuse only those ids?"
    resolution: autonomous
    class: two-way
    mandatory: none
    chosen: "A: py-tests keeps -x and passes --deselect for exactly the two row-0 failing node ids (tests/tooling/test_framework_adoption.py::test_evidence_contract_real_cli_selftests[validate_closeout_artifacts.py] and tests/unit/test_capture_adapter.py::test_ac_130_10_cmyk_icc_to_srgb[AC-130.10]). The gate prints them on an 'excused' line, and the handoff names them as baseline failures."
    source_tag: Local Canon
    precedents:
      - "C:/Temp/av-kit/2026-11-21-transcript-job-resume/tjr-base-py.txt — '2 failed, 3337 passed' at baseline.sha, before any product change"
      - "implementation-plan.md §Verification Plan 1 step 6 — 'Their failures are recorded, not fatal, and the gate excuses only those ids'"
      - "docs/execution/plans/2026-11-20-help-quick-start/session-gate.ps1:65 — the peer gate prints its excused baseline failures"
    research: { engine: none, sources: [] }
    reasoning: "Handed to the agent: USER_EXPLICIT 2026-11-18 'make the decisions always the recommenations'. Options: (A) deselect the two ids and keep -x; (B) drop -x and compare the failure list with the baseline set; (C) do nothing and keep the plain -x command, so the gate stops at the first baseline failure and never runs the rest of the suite. A excuses exactly the named ids, so any other failure still stops the gate, and it is one argument per id. B needs a parser for the summary and runs on after a new failure. C cannot pass. Weakness of A: a deselected test is not run at all, so a fix to it would go unseen; neither file is in this plan's scope."
open_decisions: []
```

## Research References

- None outside the repository. The behaviour is set by av-kit canon (10 §Kebab menu, 11 TR1, 03 §`TranscriptService`) and the code reads above.

## Planning receipts

All under `C:/Temp/av-kit/2026-11-21-transcript-job-resume/`, read-only against the repository:

| Receipt | What it shows |
|---|---|
| `tjr99-probe.py`, `tjr99-probe.txt` | `HEAD` `159e178`, one worktree, the triage edits as the only dirty paths; no `graphify-out`; line endings and SHA-256 prefixes of the scope; the new paths absent; the code anchors cited above; no `resume-job`, `transcript:resume_job` or `AC-163.` in the tree |
| `plan-probe-seed.txt` | A Paused job with one Done item seeded into a scratch `avkit.db`, resumed from `Idle` through the real services: `final Done`, the raw ZIP and `probe-channel_vol1.md` |
| `plan-guard-probe-r1.txt` to `-r3.txt` | `RESUME_GUARD` applied in memory by a pytest plugin over `-k "transcript or resume or ac_11_ or ac_116"` in `test_services.py` and `test_api_transcripts.py`: 34 passed, 88 deselected, each run; every logged call resumed from `Paused` or `Idle`. `plan-guard-probe.txt` is a failed first attempt with `--count`, which this host's pytest lacks |
| `plan-collect.txt` | The pytest collection, 3339 ids, used to map the full probe's progress lines to test ids |
| `plan-defaults-probe.txt`, `plan-defaults-probe-targeted.txt` | The six new defaults applied in memory by a pytest plugin. The full run hung after 100 % on AC-122.12's real-clock cap wait and was stopped; its failures map to AC-116.5, AC-116.9 and AC-122.12 plus the encoding-only closeout failures. The targeted run: 3 failed, 198 passed |
| `plan-closeout-noplugin.txt`, `plan-closeout-utf8.txt` | The two closeout test files with no plugin: 45 failed without `PYTHONIOENCODING`, 101 passed with it |
| `plan-defaults-rewrites-probe.txt`, `plan-defaults-rewrites-probe-old.txt` | `DEFAULTS_TEST_EDITS` in a scratch file: 5 passed on the new defaults; on today's defaults the defaults test and 116.5 fail by assertion |
| `plan-defaults-rate.txt` | The worker's pacing loop simulated over 400 items: at most 18 starts in any hour, 16.44 an hour on average, 5.94 h for 100 |
| `plan-defaults-unsaved-probe.txt` | An unsaved key reads the table default (300 today); a saved 42 reads 42 |
| `plan-mcp-base.txt` | `npm test` in `mcp-server/` today: 38 files, 553 tests passed, in about 6 s |
| `tjr99-task-lint.txt` | `tools/lint_task_contract.py` on `task.md` |

## Validation stage contract

| Stage | Checks | Where |
|---|---|---|
| Plan review | This plan and `task.md`, against Mat's two requests, 10 §Per-job resume (residual), 03:878, 03:256, 03:577, 06's defaults table, 11 TR1 and the code reads above | `tjr-plan2-2026-11-21-transcript-job-resume` |
| Row checks | Each row's validation command | `task.md` |
| Session gate | §Session gate | H1-2 |
| Execution review | The delta from `baseline.sha` in the §Files Modified paths, against AC-163.1 to AC-163.10 | `tjr-execution-2026-11-21-transcript-job-resume` |
