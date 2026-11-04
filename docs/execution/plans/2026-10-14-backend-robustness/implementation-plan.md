---
project: "2026-10-14-backend-robustness"
date: "2026-10-14"
source: "docs/build-plan/04-rest-api.md#unhandled-errors-residual; docs/build-plan/03-service-layer.md#ffmpeg-resolution-residual; docs/build-plan/03-service-layer.md#tts-async-generation-residual"
meus: ["MEU-76", "MEU-78", "MEU-77"]
status: "draft"
template_version: "2.2"
---

# Implementation Plan: Backend robustness (Session 33)

> **Project:** `2026-10-14-backend-robustness`
> **Build plan:**
> - `docs/build-plan/04-rest-api.md` §Unhandled errors (residual) (`:427-439`, MEU-76, registry 4.4)
> - `docs/build-plan/03-service-layer.md` §FFmpeg resolution (residual) (`:485-496`, MEU-78, registry 3.10)
> - `docs/build-plan/03-service-layer.md` §TTS async generation (residual) (`:468-481`, MEU-77, registry 3.9)
> - `docs/build-plan/05-mcp-server.md` `DESTRUCTIVE_ACTIONS` (`:95`) and server instructions (`:275`) as text this plan corrects
>
> **Grouping:** `.agent/context/grouping/2026-10-09-triage-residuals-session-grouping.md`, Session 33 (`:103-110`), decisions D-1 to D-7 (`:215-221`).
> **Status:** `draft`, awaiting the independent plan review (Codex `gpt-6.1-sol`, loop `s33-plan-2026-10-14-backend-robustness`).

## Goal

Three backend contract faults surfaced in the 2026-10-09 triage (`known-issues.yaml` `API-UNHANDLED-ERROR-OPAQUE`, `FFMPEG-RESOLUTION-DIVERGENCE`, `MCP-TTS-GENERATE-SYNCHRONOUS`):

- An unexpected exception in any route returns a 500 that is logged nowhere and carries no CORS header, so the GUI shows "Failed to fetch". A yt-dlp extract failure on download add is the common trigger, and its text never reaches the user.
- FFmpeg is resolved once at startup and latched. Convert, TTS and the health check share that one result, the Downloader never receives it, and the Dependencies card shows the raw setting instead of the binary in use.
- `POST /tts/generate` synthesizes inline. MCP gives up after 30 s while the job keeps running, and nothing can cancel a running job because no client holds its id.

Goal anchor (registered verbatim with the review ledger):

Session 33 delivers MEU-76 (logged, CORS-safe unhandled errors and a typed extract error), MEU-78 (one live ffmpeg resolver for Convert, TTS, health and yt-dlp) and MEU-77 (TTS generate returns the job at once, synthesizes in the background and can be cancelled), with an OpenAPI diff limited to those contracts and an MCP audit in which tts.cancel passes.

- **MEU-76 `api-error-surface`.** Every unhandled exception is logged once with its request id, route and traceback, and becomes the `internal_error` envelope inside the CORS layer. yt-dlp extract failures become `ExtractError` (422) whose text reaches the client. The GUI names the request id.
- **MEU-78 `svc-ffmpeg-resolver`.** One resolver (configured → bundled → PATH), re-run on every use, so a settings change applies without a restart. It feeds Convert, TTS MP3, the health check and yt-dlp's `ffmpeg_location`. The Dependencies card shows the resolved binary and whether ffprobe is beside it.
- **MEU-77 `svc-tts-async-generate`.** `POST /tts/generate` validates, creates the job and returns it as `Generating`. A background worker synthesizes. `DELETE /tts/{id}` stops it between segments and removes partial output. Restart and shutdown never leave a job `Generating`. MCP returns the job at once, and the audit's `tts.cancel` step cancels a genuinely running job.

Order: MEU-76 → MEU-78 → MEU-77 (grouping `:106`). MEU-77's background failures are only visible through MEU-76's logging, and MEU-78 changes the `MediaPort` that MEU-77's worker calls.

Planning started from `7861020` (Session 30 closeout) on `claude/backend-robustness`, in the worktree `P:/av-kit-wt/backend-robustness`. Row 0 records the HEAD at execution start in `baseline.sha`. Treat the live files as the baseline and reset nothing.

## Context Tool Decision

```yaml
context_tool_decision:
  phase: planning
  eligible_tools: []
  decision: not_applicable
  eligibility_basis: "graphify-out/ and graphify-out-research/ are absent in the worktree (ls, 2026-10-14); headroom is not on PATH. Scope is about 20 named Python/TS files plus tests, where .agent/docs/context-tool-decision-gate.md routes to direct file/search."
  human_message_reference: null
```

```yaml
context_tool_decision:
  phase: execution
  eligible_tools: []
  decision: not_applicable
  eligibility_basis: "Re-evaluated at row 0 (2026-10-15). graphify-out/ and graphify-out-research/ are still absent. headroom.exe is now on PATH (C:/Users/Mat/AppData/Roaming/Python/Python313/Scripts), but the repo has no active approved Headroom disposition, the user-headroom MCP is not connected in this harness, and the execution payloads are source, test output and exact evidence (bypass classes). Confirmed by Mat 2026-10-15 (walkthrough A-2)."
  human_message_reference: null
```

Task row 0 re-evaluates this before execution (create-plan §5f). `prereq` refuses if a graph directory has appeared.

## Harness, driver and reviewer route

- **Driver:** Claude Code, local on Windows (VS Code extension; `.agent/context/harness.local.md` §Claude Code, `.agent/docs/harness-profiles.md`):
  - `native_shell: pwsh` for gates; Git Bash for read-only inspection;
  - `rtk` on PATH: every tool call in `validate-task.ps1` runs through `rtk proxy`;
  - `plan_to_exec_gate: human`;
  - `fresh_worker` is the Agent tool (`.claude/agents/av-kit-builder`, `av-kit-verifier`); rows keep `compact_continue` as the fallback.
- **Reviewer:** Codex CLI (`avkit_independent_reviewer`, vendor OpenAI), model `gpt-6.1-sol`, effort `high`, dispatched by the driver through `tools/Invoke-CodexDispatch.ps1` with the review ledger. It is vendor-distinct from the author (Anthropic). Caps: plan 3 rounds, execution 6 (PROFILE B5). Each dispatch is metered; the driver warns before each one (D-12).
- **Gate location:** the whole session is local (D-8). There is no container pre-gate and no `.sh`. The driver runs `WINDOWS_GATE` and the authoritative MCP audit itself; nothing waits for a human run.
- **No commits.** The driver never commits or pushes (GUARDRAILS). Every gate result is bound to the working tree by `GATE_FINGERPRINT`, not to a commit, and no check requires a clean tree.
- **Receipts:** `C:/Temp/av-kit/` (`$env:RECEIPTS_DIR`), prefix `s33-`.

## Handoff Set

| Scope | Canonical handoff |
|---|---|
| `MEU-76` | `.agent/context/handoffs/2026-10-14-backend-robustness-MEU-76-handoff.md` |
| `MEU-78` | `.agent/context/handoffs/2026-10-14-backend-robustness-MEU-78-handoff.md` |
| `MEU-77` | `.agent/context/handoffs/2026-10-14-backend-robustness-MEU-77-handoff.md` |

Rolling reviews:
- plan: `.agent/context/handoffs/2026-10-14-backend-robustness-plan-critical-review.md`
- execution: `.agent/context/handoffs/2026-10-14-backend-robustness-implementation-critical-review.md`

## Work Packages and Context Lifecycle

| ID | Work | depends_on | context_strategy | durable_outputs |
|---|---|---|---|---|
| WP-0 | Prerequisites, installs, baseline, overlap check, `TEST_AMENDMENTS` census (rows 0–1) | — | `shared` | `walkthrough.md` §Baseline, §Census; `baseline.sha`; `baseline-counts.json` |
| WP-1 | MEU-76 TDD and handoff (rows 2–4) | WP-0 | `compact_continue` | MEU-76 handoff; compact, then re-read `task.md` and the handoff |
| WP-2 | MEU-78 TDD and handoff (rows 5–7) | WP-1 | `compact_continue` | MEU-78 handoff; compact, then re-read |
| WP-3 | MEU-77 TDD and handoff (rows 8–11) | WP-2 | `compact_continue` | MEU-77 handoff; compact, then re-read. Split point for 33b (D-11) |
| WP-4 | Hub reconciliation (row 12) | WP-3 | `shared` | `docs/build-plan/02/03/04/05/07` |
| WP-5 | H1 closeout (audit, `WINDOWS_GATE`), execution review, H2 | WP-4 | `compact_continue` | handoffs, gate and audit JSON, walkthrough, rolling review, reflection |

---

## User Review Required

> [!IMPORTANT]
> These items are for the plan-review loop and for the user's execution message. They are not a pause point before review.
>
> 1. **Execution authorization** (`plan_to_exec_gate: human`). After the reviewer approves, execution starts only on a direct user message, recorded in `walkthrough.md` §Execution authorization by row 0.
> 2. **Eleven test amendments, TA-1 to TA-11** (`TEST_AMENDMENTS`; TA-11 was added during execution by A-10). Each existing expectation pins behaviour the Spec rows above replace: a synchronous `generate` that returns `Done` or re-raises (03:423, 03:476), a latched ffmpeg probe (02:428, 03:494), and closed method/type lists that a new port method or error type extends. AGENTS §Testing & TDD allows such a correction only with a source-backed amendment and independent review. They apply only if the plan review approves them and the execution message does not veto them (Stop condition S8). TA-11 was not in the reviewed plan: Mat approved it under S2 at the MEU-78 gate (A-10), and the execution review covers it.
> 3. **Behaviour you will notice.**
>    - A failing download add (for example YouTube's "Sign in to confirm you're not a bot") now shows yt-dlp's message as a 422 instead of "Internal server error" (D-15).
>    - Cancelling a TTS run now **removes** its partial WAV/MP3. `05-mcp-server.md:95` said "files already written stay"; row 12 corrects it (D-17).
>    - The Dependencies card shows the ffmpeg binary actually in use and an FFprobe line. An `ffmpeg_path` setting that points at a missing file is no longer shown as if it were used.
> 4. **Decisions D-8 to D-31** (§Decision Log) are resolved autonomously and logged. The user may veto any of them in the execution message.
> 5. **Merge risk with Session 31.** Session 31 is executing in `P:/av-kit` and edits `SettingsPage.tsx` and `ui/tests/e2e/settings.test.ts`, which MEU-78 also edits (different regions: the Dependencies card and a new spec). Row 0 records the overlap. Whichever session merges second resolves it (D-10).

---

## Proposed Changes

### Single-statement contracts

Each name below is defined once here. ACs, task rows and scripts refer to these names and never restate the values (PR-9).

| Name | Definition | Source |
|---|---|---|
| `PRODUCT_SCOPE` | The product files this plan may change are exactly the "Files Modified" rows below, plus `openapi.committed.json`. `ui/src/main/` and `tools/` stay byte-identical to `baseline.sha`. `validate-task.ps1 -Check api-scope` proves this. | grouping `:105`; AGENTS §Scope |
| `ERROR_EVENT` | One structlog event `api.unhandled_error` on `structlog.get_logger(module="api")` with fields `request_id`, `route` (the matched route path template, else the raw URL path), `method`, `error` (`"<Type>: <message>"`, or `<Type>` when the message is empty) and `exc_info=True`. It is emitted **exactly once** per failing request: by `request_id_middleware`'s `except Exception` (main.py), or by the `Exception` handler backstop (errors.py) when the exception never passed through the middleware, or by the `DomainError` handler when an **unmapped** `DomainError` becomes a 500. A mapped status (any `DOMAIN_HTTP_MAP` entry, including the 503s) is never logged by this event. | Spec 04:435; Local Canon AGENTS §Code Quality |
| `CORS_SAFE_500` | `request_id_middleware` (main.py:73-84) wraps `call_next` in `try/except Exception`. On an exception it emits `ERROR_EVENT` and returns `internal_error_response(request_id)` (errors.py, new): status 500, body `_envelope("internal_error", "Internal server error", {"request_id": id})`, header `X-Request-ID`. The middleware runs inside `CORSMiddleware` (added after it, main.py:86), so the response carries `Access-Control-Allow-Origin` for an allowed origin. The `Exception` handler (errors.py:97-106) returns the same `internal_error_response` and stays as the backstop. No body ever contains a traceback or the exception text. | Spec 04:436; Starlette middleware order (local probe 2026-10-09, 04:431) |
| `CONSOLE_FIELDS_NEW` | `CONSOLE_FIELDS` (services/health.py:37) becomes `("job_id", "error", "request_id", "route")`, so the Console line for `ERROR_EVENT` shows `request_id=` and `route=` after the event text, after redaction, in that order. | Spec 04:435 (request id in the log); plan D-13 of Session 27 (CONSOLE_FIELDS) |
| `EXTRACT_STATUS` | `class ExtractError(DomainError)` in `avkit_core/domain/errors.py`. `DOMAIN_HTTP_MAP[ExtractError] = 422`. The envelope is `{"code": "ExtractError", "message": <yt-dlp text>}`. It is raised only at the three `YouTubeAdapter._run_extract` sites (youtube/adapter.py:393, 395, 397), with the same messages they raise today. `download()` (`:447-455`) keeps plain `DomainError`, so a failing media download still fails its job, not a request. | Spec 04:437 ("status chosen at plan time against §Status mapping"); 04 §Status mapping (422 = the request cannot be processed as given); D-15 |
| `GUI_ERROR_TEXT` | In `apiFetch` (`ui/src/renderer/src/lib/api.ts:79-82`), when `res.ok` is false, `env.code === 'internal_error'` and `env.details.request_id` is a non-empty string, the thrown `ApiError` message is `Internal server error (request id <id>)`. Every other error keeps today's message. | Spec 04:436 ("the GUI shows the message and request id") |
| `CENSUS_SIGNATURE` | In `mcp-server/scripts/audit/census.ts`, `avkit_download.add` and `avkit_transcript.add` use `BOT_WALL = /confirm you.re not a bot/i` instead of `MASKED_500`, because the bot wall now surfaces as `ExtractError` text. `avkit_capture.capture` keeps `MASKED_500`. The comment at `:8` names `ExtractError`. Authoritative mode never consults the census. | Local Canon census.ts:1-5; EXTRACT_STATUS |
| `RESOLVER_ORDER` | `FFmpegAdapter.ffmpeg_binaries() -> FFmpegBinaries \| None` resolves on **every** call, with no cache and no `_probed` latch: (1) the configured path, if it is a file; (2) the bundled path, if it is a file; (3) `shutil.which("ffmpeg")`; else `None`. The configured path is `configured_source()` when the constructor received `configured_source: Callable[[], Path \| None]`, else the fixed `configured_path`. Passing both raises `ValueError`. Every adapter method that runs ffmpeg or ffprobe (`convert`, `probe`, `is_available`, `ffmpeg_version`, `detect_gpu`, `_require_ffmpeg`) goes through it. `detect_gpu()` keeps no cache: every call probes the ffmpeg resolved at that call, so `POST /conversions/gpu/refresh` still re-probes (A-8). | Spec 03:491-492; 02:428 (order locked); D-16 |
| `FFPROBE_RULE` | `FFmpegBinaries.ffprobe` is the sibling `ffprobe.exe`/`ffprobe` beside the resolved ffmpeg when it is a file, else `shutil.which("ffprobe")`, else `None`. `probe()` raises `FFmpegNotFoundError("ffprobe binary was not found")` when it is `None`. | Spec 03:493 ("checks ffprobe beside it") |
| `FFMPEG_BINARIES` | `@dataclass(frozen=True) class FFmpegBinaries: ffmpeg: Path; ffprobe: Path \| None` in `avkit_core/domain/conversion.py`. `MediaPort` (ports/media.py) gains `def ffmpeg_binaries(self) -> FFmpegBinaries \| None: ...`. | Local Canon ports/media.py |
| `FFMPEG_LOCATION` | `YouTubeAdapter.__init__` gains `ffmpeg_location: Callable[[], Path \| None] \| None = None`. `_base_opts` (youtube/adapter.py:335) calls it on every call and sets `opts["ffmpeg_location"] = str(path.parent)` when it returns a path; otherwise the key is absent (yt-dlp then searches PATH, today's behaviour). `build_services` builds `FFmpegAdapter` before `YouTubeAdapter` and passes `ffmpeg_location=lambda: (b.ffmpeg if (b := media.ffmpeg_binaries()) else None)`. | Spec 03:491; yt-dlp `ffmpeg_location` option (a directory or a binary path) |
| `LIVE_SOURCE` | `build_services` passes `configured_source=lambda: _ffmpeg_configured(settings.get("downloader", "ffmpeg_path"))` (wiring.py:112, 160-161) and no `configured_path`. A `PUT /settings/downloader` therefore applies to the next ffmpeg use without a restart. | Spec 03:492 |
| `DEPS_FFMPEG` | `DependencyHealth` (domain/health.py:40) gains defaulted fields `ffmpeg_path: str \| None = None` and `ffprobe_available: bool = False`, filled by `HealthService.dependencies()` from one `media.ffmpeg_binaries()` call. `routes/health.py` drops `_ffmpeg_path` (`:26-33`) and its `get_settings_service` dependency and reports `ffmpeg.path = deps.ffmpeg_path`. `FfmpegDependencyOut` (schemas/health.py:25) gains `ffprobe_available: bool`. | Spec 03:493 |
| `DEPS_CARD` | The Settings Dependencies card (`SettingsPage.tsx:1001-1019`) renders the FFmpeg row from `ffmpeg.path` (now the resolved path) as today, plus one new row `li data-testid="deps-ffprobe-row"` labelled `FFprobe` with a `StatusChip` from `ffmpeg.ffprobe_available` (`available` / `missing`). The `DependenciesOut` type (`SettingsPage.tsx:65`) gains `ffprobe_available?: boolean`. | Spec 03:493; Local Canon G32 (StatusChip tokens) |
| `DEPS_REFRESH` | `flushPut` (`useSettingsPage.ts:67-83`) also invalidates `QUERY_HEALTH_DEPENDENCIES` after a successful `downloader` PUT whose body contains `ffmpeg_path`. No other namespace or key invalidates it. | Spec 03:492 (live setting) |
| `ASYNC_GENERATE` | `TTSService.generate` first **enters** (D-31): under `_lock` it raises `ConflictError("the TTS service is stopping")` when `_closing` is set, before any collaborator call, and otherwise increments `_callers`. Everything after entry runs inside a `try` whose `finally` takes `_idle`, decrements `_callers` and calls `self._idle.notify_all()`, so the count falls only after the call's last collaborator access (the `get_status` read on success, or the spawn failure's `_finish`). It then keeps every synchronous check it has today (services/tts.py:113-142: text, speed, format, model loaded, voice, `_require_assets`). Then, in one critical section under `_lock`, it raises `ConflictError("the TTS service is stopping")` when `_closing` is set (`SHUTDOWN_STOP`; a stop can begin after entry), raises today's 409 when `_current_id` is set, and otherwise adds the job row as `Generating`, sets `_current_id` and clears the cancel flag. `_current_id` is the job's **reservation** (D-30): it is published inside this critical section, before `_lock` is released, and only `_finish` clears it. It then calls `self._spawn(worker)` outside the lock (a synchronous spawn runs the worker, whose `_finish` takes `_lock`) and returns `self.get_status(job.id)` (the row as stored). `spawn: Callable[[Callable[[], None]], None] \| None = None` is a constructor keyword; the default starts a daemon `threading.Thread(name="tts-generate")`; the thread object is not tracked. If `spawn` raises, `_finish(job.id, Failed("<Type>: <message>"))` runs (`CANCEL_RULE`) and the exception propagates (`ERROR_EVENT`). `wait_idle(timeout: float) -> bool` is `with self._idle: return self._idle.wait_for(lambda: self._current_id is None and self._callers == 0, timeout)`, where `_idle = threading.Condition(self._lock)`. It returns `True` once no job is reserved and no `generate` call is between entry and return, and `False` when `timeout` passes first. An admitted job that has not been spawned, or whose thread has not started, therefore counts as busy. So does a caller still in its synchronous checks, or one whose worker has finished but which has not yet read the stored row. `_lock` is never held across `spawn`. | Spec 03:476; Local Canon download/transcript/conversion queues; D-18, D-26, D-30, D-31 |
| `WORKER_RULE` | The worker runs today's body (prepare → `self._tts.generate` → WAV write → MP3 convert) and **never raises**. Its first action reads the cancel flag; when it is set (a stop or cancel that came before the thread started), the outcome is `Cancelled` and no port, filesystem or media method is called. It computes one outcome: `Done` with the output path; `Cancelled` from `_Cancelled`; or `Failed`, whose message is the error's message for a `ValidationError` or any other `DomainError` and `"<Type>: <message>"` for any other `Exception`. A `Failed` outcome logs `tts.generate_failed` with `job_id`, `error` and `exc_info=True`. Its `finally` calls `_finish(job_id, outcome)` exactly once; an exception that escapes before an outcome is set counts as `Failed`. `_current_id` and the cancel flag therefore always clear (`CANCEL_RULE`). `_finish` is the worker's last call into any collaborator; nothing after it touches the model, the database or the files. The generating caller's own last access (the `get_status` read) is covered by `_callers` (`ASYNC_GENERATE`). | Spec 03:423 (every Failed job has a message), amended by D-19; D-25, D-30, D-31 |
| `CANCEL_RULE` | `_lock` is the single linearization point between `cancel` and the terminal write. `cancel(job_id)` takes `_lock` and sets the cancel flag only when `job_id == _current_id`; otherwise it does nothing. The route keeps 204 in every case. `on_progress` raises the private `_Cancelled` when the flag is set, so the adapter stops before its next segment. The worker also checks the flag after the WAV write and after the MP3 convert; these early exits read it without the lock. The terminal step `_finish(job_id, outcome)` runs entirely under `_lock`. When the flag is set or the outcome is `Cancelled`, it applies `PARTIAL_CLEANUP` and writes `Cancelled`. Otherwise it writes `Done`, or `Failed` after `PARTIAL_CLEANUP`. In the same critical section it sets `_current_id = None`, clears the flag and calls `self._idle.notify_all()` (D-30). A `cancel` that takes the lock before `_finish` therefore always ends `Cancelled` with no output file. One that takes it after `_finish` finds `_current_id` no longer equal to its id and changes nothing, so the job stays `Done` and the flag never reaches the next job. | Spec 03:477; D-25 |
| `PARTIAL_CLEANUP` | Before the worker writes `Cancelled` or `Failed`, it unlinks `{root}/{id}.wav` and `{root}/{id}.mp3` when each is a file (`_unlink_if_file`, as `capture.py:900` does), and logs and ignores an `OSError` from the unlink. A `Done` job keeps its output; the WAV of a Done MP3 job is kept as today. | Spec 03:477 ("no partial output file remains"); Local Canon `services/capture.py:900` |
| `RESTART_RECOVERY` | `TTSService.recover_stale_processing()` marks every `Generating` row `Failed` with `error_message = "interrupted by restart"`, through the new `TTSJobRepository.list_by_status(status) -> list[TTSJob]` (ports/storage.py:73; SQL repository in `database/repositories.py`). `Pending`, `Done`, `Failed` and `Cancelled` rows are untouched. | Local Canon `TranscriptService.recover_stale_processing`; domain/tts.py:36 (`Generating → Failed` is allowed) |
| `SHUTDOWN_STOP` | `TTSService.stop_processing(timeout: float = 10.0) -> bool` takes `_lock`, sets `_closing = True` and, when `_current_id` is set, the cancel flag. It then releases the lock and returns `wait_idle(timeout)`, which waits on the reservation, not on a thread: a job admitted before stop began but not yet spawned keeps `stop_processing` from returning `True` until its `_finish` (worker or spawn failure) has run. It also waits on the callers (D-31): a `generate` call that entered before stop began keeps `stop_processing` from returning `True` until that call has made its last collaborator access and left; on `False` it logs `tts.stop_timeout` with `job_id` and `timeout`. `_closing` stays set, so a `generate` after stop began raises `ConflictError` before any row is added (`ASYNC_GENERATE`). `AppServices.tts` is typed `_TTSRuntime`, a Protocol with `recover_stale_processing()` and `stop_processing(timeout: float = 10.0) -> bool` (wiring.py:41-56). `_lifespan` (main.py:36-50) calls `services.tts.recover_stale_processing()` after the transcript one. On shutdown it calls `idle = services.tts.stop_processing()` after `services.transcript.stop_processing()`. Only when `idle` is true does it then call `services.models.unload()` and `app.state.engine_dispose()`. When `idle` is false it logs `api.shutdown_tts_busy` and skips both, so a worker still inside synthesis never has its model or database torn down under it. The daemon thread ends with the process, and `RESTART_RECOVERY` fails the row at the next start. | Local Canon main.py:36-50; D-26, D-30, D-31 |
| `PROGRESS_LAZY` | `KokoroAdapter.generate` PyTorch branch (tts/adapter.py:272-284) iterates `pipeline(...)` lazily instead of `list(...)`. After chunk *i* it reports `min(0.99, i / est)`, where `est = max(1, len(re.findall(r"[.!?\n]+", text)))`, and reports `1.0` after the loop. The ONNX branch (`:293-306`) already synthesizes per chunk and is unchanged apart from the cancel exception passing through. | Spec 03:477 ("between segments") |
| `MCP_TTS_TEXT` | `desc()` in `mcp-server/src/toolsets/tts.ts:5-12` says `generate returns the job at once (status Generating); poll get until Done/Failed/Cancelled; cancel stops a running job`. The TTS line of `SERVER_INSTRUCTIONS` (`index.ts:9`) becomes `TTS: load a model first; prepare is preview only; generate returns the job at once; poll get; cancel stops a running job.` | Spec 03:479; 05:275 |
| `AUDIT_CANCEL_STEP` | `destructiveStep` (`scripts/audit/plan.ts:206-265`) gains two optional spec fields: `raceLost?: (ctx: StepContext) => Promise<boolean>` and `attempts?: number`. `attempts` defaults to 1, so every other destructive step behaves exactly as today. A retry happens only when all of these hold: the confirmed call returned no error and had no effect, both refusals held (and the declined one, when present), `raceLost(ctx)` is true, and attempts remain. The step then runs its precondition block again (precondition; `reestablish` once if it is not `ok`; else `precondition_lost`) and repeats the whole refusal sequence. The result's `detail` records `attempt n/<attempts>`, and its refusal record is the last attempt's. An attempt whose refusals did not hold is returned at once and never retried. The `tts.cancel` step (`:667-678`) uses both fields. `precondition` is `ok` only when `state "tts_job2"` is set and `GET /tts/{tts_job2}` is `Generating`. `reestablish` POSTs `/tts/generate` with `generateArgs`'s body and `AUDIT_FIXTURES.tts_cancel_text`, registers the id with `ctx.ledger.register("tts_job", id)` and stores it as `state "tts_job2"`. `args` and `probe` use `tts_job2`, and the probe is `status === "Cancelled"`. `raceLost` is true only when `tts_job2` is `Done`, and `attempts` is 3. A job that is `Failed`, or still `Generating` after the effect poll, is a real failure (`confirmed_no_effect`, no retry). `depends_on` stays `["tts.generate"]`. The comment at `:667-670` is replaced by one naming this rule. `AUDIT_FIXTURES` gains `tts_cancel_text`: 60 copies of the sentence `"The audit keeps this job running long enough to cancel it."` joined by spaces (about 3,500 characters). The `tts_text` comment (`fixtures.ts:20`) drops "generate is synchronous". | Spec 03:479; Local Canon plan.ts:206-265 (`destructiveStep` precondition and reestablish), run.ts:321 (tts_job cleanup); D-27 |
| `OPENAPI_DIFF` | `openapi.committed.json` is regenerated with `tools/export_openapi.py`. Compared with `baseline.sha`: no path is added or removed; the changed paths are a subset of `{/api/v1/tts/generate, /api/v1/tts/{id}}` (the committed template, `openapi.committed.json:6208`); the changed component schemas are a subset of `{FfmpegDependencyOut, TTSJobOut}`. `api-scope` asserts it. | Spec 03:480, 04 §OpenAPI |
| `TEST_AMENDMENTS` | Each edit carries the comment `# TA-n (Session 33, MEU-xx)` (`// TA-n …` in TS). **TA-1** `tests/unit/test_domain.py` `DOMAIN_ERROR_TYPE_NAMES` (about `:206`) gains `"ExtractError"`. **TA-2** `tests/integration/test_filesystem_media.py` `test_ac_8_6…`: the probe counter `count["n"] == 1` becomes `== 2` (two resolutions, no latch). **TA-3** `tests/unit/test_domain.py` `MEDIA_PORT_METHODS` (`:1153`) gains `"ffmpeg_binaries"`. **TA-4** the same list in `tests/integration/test_filesystem_media.py:196`. **TA-5** `tests/unit/test_domain.py` TTSJobRepository method tuple (about `:1407`) gains `"list_by_status"`. **TA-6** `tests/integration/test_sqlite_uow.py:313` `TTS_REPO_METHODS` gains `"list_by_status"`. **TA-7** `tests/unit/test_services.py` `test_ac_12_5_progress_resolution_and_cancel`: its last block becomes `bad = service.generate(…)`, `service.wait_idle(5.0)`, and asserts the job is `Failed` instead of `pytest.raises`. **TA-8** `test_ac_12_5_invalid_progress_marks_failed`: drop `pytest.raises(ValidationError)`; assert `Failed` after `wait_idle`. **TA-9** `tests/integration/test_tts_assets.py` `test_ac_62_11…`: the expected 500 becomes 201, then `wait_idle`, then the row is `Failed`; the second call is 201. **TA-10** `test_tts_assets.py` `test_ac_62_16…` (both cases): after the POST and `wait_idle`, read `GET /api/v1/tts/{id}` for `status == "Done"` and `output_path`. **TA-11** `tests/unit/test_domain_conversion.py` `test_ac_28_7_mediaport_additive_requires_cancel_hook` (`:177`): the ordered `keep` tuple gains `"ffmpeg_binaries"` after `"ffmpeg_version"` (A-10). Nothing else in those tests changes. | Spec 03:423, 03:476-477, 02:428 (amended by D-16); AGENTS §Testing & TDD |
| `FIXTURE_REPAIRS` | Test-double updates that change no assertion: (a) `_tts_stack` in `tests/unit/test_services.py` passes `spawn=lambda fn: fn()` (synchronous worker); (b) the fake TTS repositories gain `list_by_status`; (c) the media fakes gain `ffmpeg_binaries`; (d) `dependencies()` fakes that build a real `DependencyHealth` need nothing (defaulted fields), and the SimpleNamespace fakes in `tests/e2e/test_api_health_settings.py` and `tests/e2e/test_api_auth.py` gain `ffmpeg_path=None, ffprobe_available=False` (A-6); (e) every test `AppServices(...)` whose `tts` fake lacks them gains no-op `recover_stale_processing` and `stop_processing` (the latter returns `True`), and `tests/e2e/test_api_auth.py` `_services()` passes `tts=` a separate such fake instead of the shared `_Spy` (A-7); (f) `test_tts_assets.py` `_generate` / `_generate_with` call `stack.services.tts.wait_idle(5.0)` after the POST; (g) `test_ac_29_4` (`tests/unit/test_ffmpeg_conversion.py`) and `test_ac_8_10` (`tests/integration/test_filesystem_media.py`) write a sibling fake `ffprobe.exe` beside their fake ffmpeg (A-5). Row 1 lists every site. | Local Canon (fakes follow ports) |
| `PY_SYMBOLS` | The new Python names: `ExtractError`, `internal_error_response`, `FFmpegBinaries`, `ffmpeg_binaries`, `configured_source`, `ffmpeg_location`, `ffprobe_available`, `list_by_status`, `spawn`, `wait_idle`, `recover_stale_processing`, `stop_processing`. `PRESENCE_GUARD`: a Red test that uses one first asserts it exists (`assert hasattr(module, "ExtractError")`, `assert "spawn" in inspect.signature(TTSService).parameters`, and so on) before any use, and imports it inside the test body. Its absence is therefore an `AssertionError`, never an `ImportError`, a `TypeError` or a collection error. TS tests do the same with `expect(typeof …).toBe('function')` or `expect(… in …).toBe(true)`. | AGENTS §Testing & TDD (assertion-level Red); Session 31 (`typeof` guard) |
| `BOUNDED_WAIT` | Every blocking wait in a test or test fake (`Event.wait`, `Thread.join`, `wait_idle`, a polling loop) takes a timeout of at most 5 s, and the test asserts the wait's result. On today's synchronous `generate` a gated port fake therefore releases after its timeout, `POST /tts/generate` returns `Done`, and the test fails on its `Generating` assertion instead of hanging (the repository has no `pytest-timeout`). | `RED_RULE` item 2 |
| `RED_RULE` | A Red check passes only when all of these hold. (1) Every test whose name carries an AC tag of the MEU (`ac_76_1_` in pytest names; `AC-76.1` followed by a non-digit in Vitest/Playwright titles) fails, except a test whose name also carries `NEG_MARK` (`_neg` in pytest, `[neg]` in titles), which holds only a negative oracle and may pass. (2) Every failure of a tagged test is an assertion failure: pytest `AssertionError` (`assert`, `pytest.raises … DID NOT RAISE`); Vitest `AssertionError`/`expected`; Playwright `expect(`. (3) Every AC of the MEU whose Type names that tier has at least one such failure in that tier. (4) No untagged test fails or errors, and no file fails to collect or load. (5) An AC typed **pin** is excluded from (1)–(3): its tests must **pass** in the same Red run (they prove existing behaviour the MEU relies on). There is no environment tolerance; everything runs on the target machine. | AGENTS §Testing & TDD; Session 30 `vitest_red`/`pytest_red` |
| `GATED_PATHS` | Every working-tree path except a `GATE_EXCLUDED` match. The whole tree is gated, so every gate input is bound without being listed: plan directories, `.agent/workflows`, `.agent/docs`, `.agent/schemas`, `.agent/roles`, templates, groupings, proposals, `packaging/` and the rest. `GATE_EXCLUDED` holds `fnmatch` patterns, in which `*` also crosses `/`. `plan_checks.py static` asserts the executable copy (`GATE_EXCLUDED` in `exec_checks.py`) equals this list: `.agent/context/meu-status.yaml .agent/context/meu-registry.md .agent/context/current-focus.md .agent/context/known-issues.yaml .agent/context/known-issues.md .agent/context/grouping/2026-10-09-triage-residuals-session-grouping.md .agent/context/handoffs/2026-10-14-backend-robustness-* .agent/context/MCP/mcp-tool-audit-report.md docs/BUILD_PLAN.md docs/execution/metrics.md docs/execution/reflections/2026-10-14-backend-robustness-* docs/execution/plans/2026-10-14-backend-robustness/task.md docs/execution/plans/2026-10-14-backend-robustness/walkthrough.md docs/execution/plans/2026-10-14-backend-robustness/baseline.sha docs/execution/plans/2026-10-14-backend-robustness/*.json docs/execution/plans/2026-10-14-backend-robustness/*.txt`. These are the files that rows after the gate write: SSOT renders, known issues, this session's handoffs, reflection and metrics, the audit report, and this plan's own evidence. They change only at H1-2, H1-5, H1-8 and H2-1 to H2-3. `post-review-state` (H2-2) re-runs every suite that reads one of them: `layout-canon`, `queue-canon` and `gui-actions-audit` (Vitest), the MCP `docs` test, and `tests/tooling/test_framework_adoption.py`, which copies `current-focus.md` through the adoption manifest. Ignored paths (`.venv`, `node_modules`, `mcp-server/dist`, `ui/out`, `test-results`) are outside what git reports. | cloud-local §3.3 item 2, §3.4; D-29 |
| `GATE_FINGERPRINT` | SHA-256 over the sorted lines `<path>\t<sha256 of the working-tree file, or "deleted">` for every `GATED_PATHS` path that differs from `baseline.sha` (`git diff --name-only <baseline>`, the whole tree) or is untracked (`git ls-files --others --exclude-standard`). `windows-gate` records it before stage 1 and again after the last stage; the two must be equal. `gate-check` recomputes it and refuses any difference, so any edit after the gate needs a new attempt. | cloud-local §3.4 (no commit to bind to) |
| `AUDIT_FINGERPRINT` | `GATE_FINGERPRINT` computed without `.agent/skills/mcp-tool-audit/resources/baseline-snapshot.json`. `-Check audit` measures it before the prep (`uv sync`) and again after `baseline_carry.py` and `AUDIT_EXPECT`. It refuses when the two differ (restoring the baseline, `AUDIT_COMPARISON`) and records both in `audit-fingerprint.json` as `{before, after}`. `gate-check` requires `before == after ==` the value it recomputes. The code the audit ran is therefore the code the gate ran and the code under review. | cloud-local §3.4; D-29 |
| `COUNT_FLOORS` | pytest failed 0 and passed ≥ 655; Vitest total ≥ 773 and failed 0; Electron expected ≥ 133, unexpected 0 and flaky 0 (Session 30 `windows-gate-result.json`, attempt of record). MCP Vitest failed 0 and passed ≥ the `mcp_passed` value in row 0's `baseline-counts.json`. Each floor is also raised to row 0's measured count where row 0 measured one. The executable copy is `FLOORS` in `exec_checks.py`; `plan_checks.py static` asserts it equals 655 / 773 / 133. | cloud-local §3.3; reflection 2026-09-30 RULE-3 |
| `AUDIT_EXPECT` | The authoritative audit (`-Check audit`) ends with exit 0: all 70 actions pass; `avkit_tts.cancel` has delta `FIXED`; no delta is `REGRESSION` or `REMOVED`; `cleanup.ok` is true. The rewritten baseline then has no non-pass entry and no finding, so `baseline_carry.py` carries nothing. | Spec 03:479; `.agent/skills/mcp-tool-audit/SKILL.md` BASELINE_UPDATE_RULE |
| `AUDIT_COMPARISON` | Every `-Check audit` attempt compares against the pre-session baseline. Before the runner it writes `git show <baseline.sha>:.agent/skills/mcp-tool-audit/resources/baseline-snapshot.json` to `C:/Temp/av-kit/s33-baseline-presession.json` and over the baseline file, then runs `--update-baseline`; `baseline_carry.py --prior` is that pre-session copy. A rerun after a passing attempt therefore still reports `avkit_tts.cancel` `FIXED` against the pre-session `fail` (`classify.ts` `computeDelta`). On any failure the check restores the start-of-check copy (`C:/Temp/av-kit/s33-baseline-prior.json`) and deletes this attempt's `mcp-audit-summary.json` and `audit-fingerprint.json` from the plan folder, so no stale evidence survives a failed attempt. | `.agent/skills/mcp-tool-audit/SKILL.md` BASELINE_UPDATE_RULE; `mcp-server/scripts/audit/classify.ts` `computeDelta`; D-28 |

### MEU-76 — `api-error-surface`

#### Boundary Inventory

| Boundary | Input | Output | Owner |
|---|---|---|---|
| HTTP → FastAPI app | any request through `create_app` | `internal_error` envelope + CORS headers on an unhandled exception | `main.py` `request_id_middleware`, `errors.py` |
| Domain → HTTP | `DomainError` subclasses | `DOMAIN_HTTP_MAP` status; `ExtractError` → 422 | `errors.py` |
| yt-dlp → domain | `DownloadError`, `OSError`, non-dict info in `_run_extract` | `ExtractError` / `AgeRestrictedError` | `youtube/adapter.py` |
| HTTP → renderer | 500 `internal_error` with `details.request_id` | `ApiError` message naming the request id | `ui/src/renderer/src/lib/api.ts` |
| REST → MCP audit census | bot-wall text in a 422 body | `BOT_WALL` signature | `mcp-server/scripts/audit/census.ts` |

#### Acceptance Criteria

Call chain: renderer `apiFetch` / MCP client → `create_app` (main.py) → `CORSMiddleware` → `request_id_middleware` → route → service → `YouTubeAdapter._run_extract` → `errors.py` handlers. Every AC below drives a production route of `create_app` with service fakes or the real stack; no test calls a handler function directly.

| AC | Type | Description | Source | Negative Test |
|---|---|---|---|---|
| AC-76.1 | contract (pytest, `tests/e2e/test_api_error_surface.py`) | `CORS_SAFE_500`: `GET /api/v1/health/dependencies` whose health fake raises `RuntimeError("boom secret")`, sent with an `Origin` that `CORS_ORIGIN_REGEX` accepts (the test asserts the regex matches it first), returns 500 with `access-control-allow-origin` equal to that origin, `X-Request-ID` set, and the body exactly `{"error": {"code": "internal_error", "message": "Internal server error", "details": {"request_id": <X-Request-ID>}}}`. | Spec 04:436 | The body contains neither `boom secret` nor `Traceback`; an origin the regex rejects gets no `access-control-allow-origin`. |
| AC-76.2 | contract (pytest, same file) | `ERROR_EVENT`: the AC-76.1 request emits exactly one `api.unhandled_error` event (`structlog.testing.capture_logs`) with `request_id` equal to the response header, `route == "/api/v1/health/dependencies"`, `method == "GET"`, `error == "RuntimeError: boom secret"` and `exc_info` set. | Spec 04:435 | A 404 (`NotFoundError`) and a 422 (`RequestValidationError`) request emit zero `api.unhandled_error` events. |
| AC-76.3 | unit (pytest, `tests/unit/test_console_level.py`, appended) | `CONSOLE_FIELDS_NEW`: the Console text of an `api.unhandled_error` record carries `request_id=<id>` and `route=<route>` after the event text, in `CONSOLE_FIELDS` order. | Spec 04:435 | A record without those keys renders as today (no empty `request_id=`). |
| AC-76.4 | contract (pytest, `test_api_error_surface.py`) | An **unmapped** `DomainError("x")` from a route returns the masked 500 envelope and emits one `api.unhandled_error`. | Spec 04:435 | A mapped `FFmpegNotFoundError` returns 503 masked and emits **no** `api.unhandled_error`. |
| AC-76.5 | unit (pytest, `test_api_error_surface.py`) | `EXTRACT_STATUS`: `ExtractError` subclasses `DomainError`, `DOMAIN_HTTP_MAP[ExtractError] == 422`, and a route raising `ExtractError("yt-dlp says no")` returns 422 `{"code": "ExtractError", "message": "yt-dlp says no"}`. | Spec 04:437 | `ExtractError` is not a subclass of `ValidationError`, so `except ValidationError` sites do not catch it. |
| AC-76.6 | integration (pytest, `tests/integration/test_youtube_adapter.py`, appended) | `_run_extract` raises `ExtractError` for a non-age `DownloadError` (message preserved), an `OSError` (`"yt-dlp IO failed"`) and a non-dict info (`"yt-dlp returned no info"`), through the public `extract_info`. | Spec 04:437 | An age-gate `DownloadError` still raises `AgeRestrictedError`; a failing `download()` raises a plain `DomainError` (`type(exc) is DomainError`). |
| AC-76.7 | contract (pytest, `test_api_error_surface.py`) | Download add and transcript add, with a coordinator fake raising `ExtractError("ERROR: [youtube] x: Sign in to confirm you're not a bot")`, return 422 with code `ExtractError` and that message. | Spec 04:437-438 | Neither returns `internal_error`, and neither emits `api.unhandled_error`. |
| AC-76.8 | unit (Vitest, `ui/tests/unit/api-fetch.test.ts`, appended) | `GUI_ERROR_TEXT`: a 500 `internal_error` with `details.request_id: "rid-1"` throws `ApiError` with message `Internal server error (request id rid-1)`. | Spec 04:436 | Without `request_id` the message stays `Internal server error`; a 422 keeps its envelope message. |
| AC-76.9 | unit (MCP Vitest, `mcp-server/tests/audit/census-signature.test.ts`, new) | `CENSUS_SIGNATURE`: the `avkit_download.add` and `avkit_transcript.add` signatures match `ExtractError: ERROR: [youtube] x: Sign in to confirm you're not a bot` with either apostrophe (`'` and `’`). | Local Canon census.ts | Neither matches a bare `internal_error`; `avkit_capture.capture` still matches `internal_error`. |

#### Spec Sufficiency Table

| Spec rule | Sufficient? | Resolution |
|---|---|---|
| "logged once with request_id, route and traceback" (04:435) | Partly: no event name or field list | `ERROR_EVENT` (D-13) |
| "converted inside the CORS layer" (04:436) | Yes; mechanism open | `CORS_SAFE_500`: the existing HTTP middleware, which already runs inside CORS (D-14) |
| "status code chosen at plan time" (04:437) | No | 422 (`EXTRACT_STATUS`, D-15) |
| "Tests: … writes one log line" (04:438) | Yes | AC-76.1, AC-76.2 |
| "GUI shows the message and request id" (04:436) | Partly: no text | `GUI_ERROR_TEXT` |

#### Files Modified

| File | Action | Summary |
|---|---|---|
| `packages/core/src/avkit_core/domain/errors.py` | modify | `ExtractError(DomainError)` |
| `packages/api/src/avkit_api/errors.py` | modify | `ExtractError: 422`; `internal_error_response`; `ERROR_EVENT` in the backstop and for unmapped `DomainError` 500s |
| `packages/api/src/avkit_api/main.py` | modify | `request_id_middleware` `except Exception` (`CORS_SAFE_500`) |
| `packages/core/src/avkit_core/services/health.py` | modify | `CONSOLE_FIELDS_NEW` |
| `packages/infrastructure/src/avkit_infra/youtube/adapter.py` | modify | `_run_extract` raises `ExtractError` (MEU-78 also edits this file) |
| `ui/src/renderer/src/lib/api.ts` | modify | `GUI_ERROR_TEXT` |
| `mcp-server/scripts/audit/census.ts` | modify | `CENSUS_SIGNATURE` |
| `tests/e2e/test_api_error_surface.py` | create | AC-76.1, 76.2, 76.4, 76.5, 76.7 |
| `tests/unit/test_console_level.py` | modify | AC-76.3 (append) |
| `tests/integration/test_youtube_adapter.py` | modify | AC-76.6 (append) |
| `tests/unit/test_domain.py` | modify | TA-1 (MEU-77 adds TA-5; MEU-78 adds TA-3) |
| `ui/tests/unit/api-fetch.test.ts` | modify | AC-76.8 (append) |
| `mcp-server/tests/audit/census-signature.test.ts` | create | AC-76.9 |

### MEU-78 — `svc-ffmpeg-resolver`

#### Boundary Inventory

| Boundary | Input | Output | Owner |
|---|---|---|---|
| Settings → resolver | `downloader.ffmpeg_path` (live) | configured candidate | `wiring.py` `LIVE_SOURCE` |
| Filesystem/PATH → resolver | configured, bundled, `PATH` | `FFmpegBinaries \| None` | `media/adapter.py` |
| Resolver → yt-dlp | resolved ffmpeg | `ffmpeg_location` option | `youtube/adapter.py` |
| Resolver → health → REST | `FFmpegBinaries` | `ffmpeg.path`, `ffmpeg.ffprobe_available` | `services/health.py`, `routes/health.py`, `schemas/health.py` |
| REST → renderer | dependencies JSON; settings PUT | Dependencies card rows; refetch | `SettingsPage.tsx`, `useSettingsPage.ts` |

#### Acceptance Criteria

Call chain: `PUT /api/v1/settings/downloader` → `SettingsService` → `LIVE_SOURCE` lambda → `FFmpegAdapter.ffmpeg_binaries()` → {`ConversionService`, `TTSService` MP3, `HealthService.dependencies` → `GET /api/v1/health/dependencies` → Settings Dependencies card, `YouTubeAdapter._base_opts`}.

| AC | Type | Description | Source | Negative Test |
|---|---|---|---|---|
| AC-78.1 | unit (pytest, `tests/unit/test_ffmpeg_resolver.py`, new) | `RESOLVER_ORDER`: with real temp files and `shutil.which` patched, a configured file beats the bundle and PATH; a missing configured path falls to the bundle; both missing fall to PATH. | Spec 03:491; 02:428 | Nothing found → `ffmpeg_binaries()` is `None` and `convert` raises `FFmpegNotFoundError`. |
| AC-78.2 | unit (pytest, same file) | No latch: with `configured_source` returning a missing path, `ffmpeg_binaries()` falls back; after the file is created the next call returns it; after it is removed the call falls back again. | Spec 03:492 | A fixed `configured_path` adapter (today's constructor) never consults a source; passing both arguments raises `ValueError`. |
| AC-78.3 | unit (pytest, same file) | `FFPROBE_RULE`: a sibling ffprobe file is reported; with no sibling, `shutil.which("ffprobe")` is reported. | Spec 03:493 | No sibling and none on PATH → `ffprobe is None`, and `probe()` raises `FFmpegNotFoundError` naming ffprobe. |
| AC-78.4 | unit (pytest, same file) | `detect_gpu()` probes the ffmpeg resolved at each call: after `configured_source` changes to another file, the next call runs the new binary (fake runner records argv) (A-8). | `RESOLVER_ORDER` | Two calls with an unchanged path probe twice (no cache, so Refresh re-probes). |
| AC-78.5 | integration (pytest, `tests/integration/test_youtube_adapter.py`, appended) | `FFMPEG_LOCATION`: `_base_opts` sets `ffmpeg_location` to the directory of the callable's path, re-reading the callable on every call. | Spec 03:491 | A callable returning `None`, or no callable, leaves the key absent. |
| AC-78.6 | integration (pytest, `tests/integration/test_api_wiring.py`, appended) | `LIVE_SOURCE` + `FFMPEG_LOCATION` wiring: `build_services(app_data=tmp)` with a spy on `YouTubeAdapter.__init__`; after `settings.set("downloader", "ffmpeg_path", <tmp fake ffmpeg>)`, `services.health.dependencies().ffmpeg_path` and the captured `ffmpeg_location()` both name the tmp file, with no rebuild. | Spec 03:491-492 | Clearing the setting makes both fall back (bundle/PATH, patched), never the old path. |
| AC-78.7 | contract (pytest, `tests/e2e/test_api_ffmpeg_resolution.py`, new) | `DEPS_FFMPEG`: `GET /api/v1/health/dependencies` reports `ffmpeg.path` as the resolved binary and `ffmpeg.ffprobe_available` from `FFPROBE_RULE`. | Spec 03:493 | With `ffmpeg_path` set to a missing file and an ffmpeg on the patched PATH, `ffmpeg.path` is the PATH binary, never the raw setting. |
| AC-78.8 | unit (Vitest, `ui/tests/unit/settings-deps-refresh.test.ts`, new) | `DEPS_REFRESH`: `flushPut('downloader', {ffmpeg_path})` invalidates `QUERY_HEALTH_DEPENDENCIES` after the PUT resolves. | Spec 03:492 | `flushPut('downloader', {quality})` and a `ui` PUT do not invalidate it; a failed PUT does not either. |
| AC-78.9 | e2e (Electron, `ui/tests/e2e/settings.test.ts`, new spec titled `AC-78.9`, using the file's `installSettingsSeam`, whose `/health/dependencies` answer gains `ffprobe_available: true`) | `DEPS_CARD` + `DEPS_REFRESH` in the app: `deps-ffprobe-row` is visible and shows `available`; choosing a path with the FFmpeg Browse button (`browse-ffmpeg-btn`; the path field is read-only) and waiting for the flushed `PUT /settings/downloader` (seam ledger, `bodyKeys` contains `ffmpeg_path`) is followed by one more `GET /health/dependencies` than before the PUT (A-9). | Spec 03:492-493 | A theme change (`PUT /settings/ui`) adds no `GET /health/dependencies`. The resolved-path rule itself is a backend property and is proven by AC-78.7, not here (the seam answers for the backend). |

#### Spec Sufficiency Table

| Spec rule | Sufficient? | Resolution |
|---|---|---|
| "One resolver … feeds … yt-dlp (`ffmpeg_location`)" (03:491) | Yes; yt-dlp value form open | directory of the resolved binary (`FFMPEG_LOCATION`) |
| "re-resolves … a missing binary is not latched" (03:492) | Yes; cache policy open | no cache at all (D-16) |
| "reports the resolved path and version, and checks ffprobe" (03:493) | Partly: no field for ffprobe | `ffprobe_available` (`DEPS_FFMPEG`) |
| 02:428 "Probe binary once; cache" | Conflicts with 03:492 | 03:492 wins (later, Triage D-40); row 12 edits 02:428 (D-16) |
| 07:159/164 bundle path `resources/extra/ffmpeg` | Drift | Real path is `resources/ffmpeg` (`electron-builder.yml:30-31`, `wiring.py:105-109`); row 12 edits 07 |

#### Files Modified

| File | Action | Summary |
|---|---|---|
| `packages/core/src/avkit_core/domain/conversion.py` | modify | `FFmpegBinaries` |
| `packages/core/src/avkit_core/ports/media.py` | modify | `ffmpeg_binaries()` |
| `packages/infrastructure/src/avkit_infra/media/adapter.py` | modify | `RESOLVER_ORDER`, `FFPROBE_RULE`, `configured_source`, GPU cache per path |
| `packages/infrastructure/src/avkit_infra/youtube/adapter.py` | modify | `FFMPEG_LOCATION` |
| `packages/api/src/avkit_api/wiring.py` | modify | media before youtube; `LIVE_SOURCE`; `ffmpeg_location` (MEU-77 also edits it) |
| `packages/core/src/avkit_core/domain/health.py` | modify | `DependencyHealth` fields |
| `packages/core/src/avkit_core/services/health.py` | modify | fill `ffmpeg_path`, `ffprobe_available` |
| `packages/api/src/avkit_api/routes/health.py` | modify | drop `_ffmpeg_path` |
| `packages/api/src/avkit_api/schemas/health.py` | modify | `ffprobe_available` |
| `ui/src/renderer/src/features/settings/SettingsPage.tsx` | modify | `DEPS_CARD` |
| `ui/src/renderer/src/features/settings/useSettingsPage.ts` | modify | `DEPS_REFRESH` |
| `ui/tests/e2e/test-ids.ts` | modify | `DEPS_FFPROBE_ROW = 'deps-ffprobe-row'`, appended at the end in a `// MEU-78` block (after the MEU-51 hash marker for criterion 51.6) |
| `tests/unit/test_ffmpeg_resolver.py` | create | AC-78.1–78.4 |
| `tests/integration/test_youtube_adapter.py` | modify | AC-78.5 (append) |
| `tests/integration/test_api_wiring.py` | modify | AC-78.6 (append) |
| `tests/e2e/test_api_ffmpeg_resolution.py` | create | AC-78.7 |
| `tests/integration/test_filesystem_media.py` | modify | TA-2, TA-4; fake repair (c) |
| `tests/unit/test_domain_conversion.py` | modify | TA-11 (A-10) |
| `ui/tests/unit/settings-deps-refresh.test.ts` | create | AC-78.8 |
| `ui/tests/e2e/settings.test.ts` | modify | AC-78.9 (append) |
| `openapi.committed.json` | modify | `FfmpegDependencyOut.ffprobe_available` (`OPENAPI_DIFF`; regenerated in row 6 so the MEU-78 gate's `--check` holds; MEU-77 regenerates it again) |

### MEU-77 — `svc-tts-async-generate`

#### Boundary Inventory

| Boundary | Input | Output | Owner |
|---|---|---|---|
| REST → service | `POST /tts/generate` body | job row, status `Generating`, 201 | `routes/tts.py` (docstring only), `services/tts.py` |
| Service → worker thread | `_spawn(worker)` | background synthesis; never raises | `services/tts.py` |
| Worker → adapter | `on_progress` | progress rows; `_Cancelled` stops the adapter | `services/tts.py`, `tts/adapter.py` |
| REST → service | `DELETE /tts/{id}` | 204; flag for the current job | `services/tts.py` |
| Lifespan → service | startup, shutdown | `RESTART_RECOVERY`, `SHUTDOWN_STOP` | `main.py`, `wiring.py` |
| Repository | `list_by_status` | rows by status | `ports/storage.py`, `database/repositories.py` |
| MCP | `avkit_tts.generate` | the job JSON at once; text | `toolsets/tts.ts`, `index.ts` |
| Audit | `tts.cancel` step | cancel of a running job | `scripts/audit/plan.ts`, `fixtures.ts` |

#### Acceptance Criteria

Call chain: MCP `avkit_tts.generate` / renderer `tts-commands.ts:168` → `POST /api/v1/tts/generate` → `TTSService.generate` → `_spawn(worker)` → `KokoroAdapter.generate(on_progress)` → `FilesystemPort.write_audio_wav` → `MediaPort.convert` → `TTSJobRepository`; `DELETE /api/v1/tts/{id}` → `TTSService.cancel`; `create_app` lifespan → `recover_stale_processing` / `stop_processing`.

| AC | Type | Description | Source | Negative Test |
|---|---|---|---|---|
| AC-77.1 | unit (pytest, `tests/unit/test_tts_async.py`, new) | `ASYNC_GENERATE`: with the default thread spawn and a TTS port fake that blocks on an `Event`, `generate()` returns within 1 s a job with status `Generating`; after the event is set, `wait_idle(5.0)` is `True` and the job is `Done` with its output file. | Spec 03:476 | While the port blocks, `get_status` is `Generating`, not `Done`. |
| AC-77.2 | unit (same file) | One at a time: a second `generate()` while the first runs raises `ConflictError`, and no second row exists. | Spec 03:478 | After the first finishes, a new `generate()` succeeds. |
| AC-77.3 | unit (same file) | Synchronous checks stay synchronous: empty text, bad speed, no model loaded and a missing asset raise before any row is added and before `spawn` is called (spy). | Local Canon services/tts.py:113-142 | A valid request calls `spawn` exactly once. |
| AC-77.4 | unit (same file) | `CANCEL_RULE` + `PARTIAL_CLEANUP` mid-synthesis: a fake port that calls `on_progress` per segment and blocks between segments; `cancel(id)` after segment 1 → the port runs no further segment, the job is `Cancelled`, and `{id}.wav` / `{id}.mp3` do not exist. | Spec 03:477 | `cancel()` of an unknown id or of a `Done` job changes no row and returns `None`. |
| AC-77.5 | unit (same file) | Cancel after synthesis, and the terminal-write race (`CANCEL_RULE`). (a) The flag is set from the WAV-write hook (filesystem fake), and in a second case from the MP3-convert hook (media fake): the job is `Cancelled` and both files are absent. (b) Barrier: the repository fake blocks the worker's terminal `Done` save on an `Event` (≤ 5 s, `BOUNDED_WAIT`) while `_finish` holds `_lock`. `cancel(id)`, called from a helper thread, is still blocked after `join(0.2)`. After the event is set and the helper joins (≤ 5 s), the job is `Done` with its MP3 kept, and the next `generate()` ends `Done` (the flag did not leak). | Spec 03:477; D-25 | A job not cancelled keeps its MP3 and ends `Done`. |
| AC-77.6 | unit (same file) | `WORKER_RULE`: a port raising `RuntimeError("engine died")` → `Failed` with `"RuntimeError: engine died"`, one `tts.generate_failed` event with `exc_info`, partial files removed, `_current_id` cleared; the worker thread raises nothing (`threading.excepthook` spy not called). | Spec 03:423 (D-19) | A port raising `ValidationError` also ends `Failed`, never an exception out of `generate()`. |
| AC-77.7 | unit (same file) | A `spawn` that raises `RuntimeError` → the row is `Failed`, `_current_id` is cleared and `generate()` re-raises. | `ASYNC_GENERATE` | The next `generate()` with a working spawn succeeds (no stuck 409). |
| AC-77.8 | integration (pytest, `tests/integration/test_tts_assets.py`, appended) | `RESTART_RECOVERY`: a `Generating` row in the real SQLite store becomes `Failed` "interrupted by restart" when `create_app(...)` starts under `with TestClient(app):`, so the lifespan runs. The module's `Stack` builds `TestClient(app)` without entering it, so its lifespan never runs; this test does not use `Stack.client`. | Local Canon main.py:36-50 | `Done` and `Cancelled` rows in the same store are unchanged. |
| AC-77.9 | unit (pytest, `tests/unit/test_tts_async.py`) | `SHUTDOWN_STOP`. (a) `stop_processing()` during a blocked run cancels it and returns `True` once idle (job `Cancelled`). (b) With a port fake that never releases, `stop_processing(timeout=0.2)` returns `False` and logs `tts.stop_timeout`. (c) Lifespan through `create_app` + `TestClient` exit, with spies: when `stop_processing` returns `True`, the calls are `stop_processing`, `models.unload`, then the engine dispose, in that order; when it returns `False`, neither `models.unload` nor the dispose is called and `api.shutdown_tts_busy` is logged. (d) A `generate()` after `stop_processing` began raises `ConflictError` and adds no row. (e) Reservation before spawn (D-30): a deferred `spawn` fake stores the worker and returns without running it. `generate()` returns `Generating`; `stop_processing(timeout=0.2)` returns `False` with the row still `Generating`. The stored worker is then run on a helper thread (join ≤ 5 s): the job ends `Cancelled`, the TTS port fake's `prepare` and `generate` spies were never called, and a second `stop_processing(timeout=0.2)` returns `True`. (f) Spawn failure while stopping: a `spawn` fake blocks on an `Event` (≤ 5 s) and then raises `RuntimeError`. With `generate()` on helper thread A blocked inside `spawn`, `stop_processing(timeout=5.0)` on helper thread B is still running after `join(0.2)`. After the event is set, A's `generate()` re-raises `RuntimeError`, B returns `True` (join ≤ 5 s), the row is `Cancelled` (the stop's flag, `CANCEL_RULE`) and `_current_id` is `None`. (g) Caller drain after the worker (D-31): a `spawn` fake runs the worker to completion (its `_finish` writes `Done` and clears `_current_id`) and then blocks on an `Event` (≤ 5 s) before returning. The unit-of-work factory is wrapped in a spy that appends `uow` to an ordered, lock-guarded event list each time it opens. With `generate()` on helper thread A blocked inside `spawn` and `_current_id` already `None`, `stop_processing(timeout=5.0)` on helper thread B is still running after `join(0.2)`. After the event is set, A's `generate()` returns the `Done` row, B returns `True` (join ≤ 5 s) and then appends `stopped`, and the last `uow` entry comes before `stopped`. (h) Caller drain before admission (D-31): the TTS port fake's `list_voices` blocks on an `Event` (≤ 5 s). With `generate()` on helper thread A blocked in `list_voices`, `stop_processing(timeout=5.0)` on helper thread B is still running after `join(0.2)`. After the event is set, A's `generate()` raises `ConflictError` at the admission check, no row is added, and B returns `True` (join ≤ 5 s). A `generate()` called after that raises `ConflictError`, and the port fake's `get_model_status` spy records no call from it. | Local Canon main.py:44-48; D-26, D-30, D-31 | With no run in progress, `stop_processing()` returns `True` at once and changes no row. |
| AC-77.10 | contract (pytest, `tests/integration/test_tts_assets.py`, appended) | Through the real stack with a gated port fake: `POST /api/v1/tts/generate` → 201 with `status: "Generating"`; `GET /api/v1/tts/{id}` → `Generating`; `DELETE /api/v1/tts/{id}` → 204, then `GET` reaches `Cancelled`. | Spec 03:476-477 | A second POST during the run → 409 with the existing envelope. |
| AC-77.11 | unit (pytest, `tests/unit/test_tts_async.py`) | `PROGRESS_LAZY`: with `KPipeline` patched to a generator that records how many chunks it produced, an `on_progress` that raises after chunk 1 stops the PyTorch branch with exactly one chunk produced; reported values are ≤ 0.99 until the final 1.0. | Spec 03:477 | The ONNX branch with the same raising callback calls `_onnx_chunk` exactly once. |
| AC-77.12 | unit (MCP Vitest, `mcp-server/tests/tts.test.ts`, new) | `MCP_TTS_TEXT`: `avkit_tts.generate` against a fake fetch returning a `Generating` job returns that JSON on the first call (one fetch); the generate description and `SERVER_INSTRUCTIONS` carry the new text. | Spec 03:479; 05:275 | Neither text contains `generate is one job`. |
| AC-77.13 | unit (MCP Vitest, `mcp-server/tests/audit/tts-cancel-step.test.ts`, new) | `AUDIT_CANCEL_STEP`, with a stub context that scripts the REST and MCP replies. (a) The POST returns `Generating` and the confirmed cancel makes it `Cancelled`: pass on attempt 1, `tts_job` registered, `tts_job2` set, `args` use `tts_job2`. (b) The first job turns `Done` before the confirmed call and the second is cancelled: pass, `attempt 2/3`, two POSTs. (c) Every job turns `Done` first: `confirmed_no_effect` after exactly 3 POSTs. (d) A job still `Generating` after the effect poll: `confirmed_no_effect` after one POST (no retry). `AUDIT_FIXTURES.tts_cancel_text` is at least 1,500 characters. | Spec 03:479; D-27 | A stub POST returning `Done` gives `precondition_lost`. A `destructiveStep` without `attempts` runs one attempt and calls `raceLost` never. |
| AC-77.14 | **pin** — e2e (Electron, `ui/tests/e2e/tts-generate.test.ts`, new spec titled `AC-77.14`, using the file's `installTtsSeam`, whose `POST /tts/generate` already answers `Generating`) | `RUN_BAR_PIN`: after Generate, `segment-progress` is visible and the seam ledger records at least two `GET /tts/{id}` calls while the seam job stays `Generating`; after the seam job is set to `Done`, `last-output` appears. A second run: Cancel sends one `DELETE /tts/{id}`, and once the next poll returns `Cancelled`, `segment-progress` is hidden and `generate-btn` is enabled. | Spec 03:479 ("the GUI run bar polls the job"); D-22 | `last-output` is not visible while the seam job is `Generating`. |

#### Spec Sufficiency Table

| Spec rule | Sufficient? | Resolution |
|---|---|---|
| "returns it at once (`Queued`/`Running`)" (03:476) | No: TTS statuses are `Pending`/`Generating`/… (domain/tts.py:35-36) | `Generating` (D-18) |
| "stops a running job between segments … no partial output" (03:477) | Yes; file set open | `CANCEL_RULE`, `PARTIAL_CLEANUP` |
| "keeps the existing 409" (03:478) | Yes | AC-77.2 |
| "the audit baseline gains the poll and cancel steps" (03:479) | Partly: a poll step exists (`tts.generate` polls, plan.ts:649) | `AUDIT_CANCEL_STEP`; `AUDIT_EXPECT` |
| "the GUI run bar polls the job" (03:479) | Already true (`useTtsJob.ts:64-78`; seam specs W2-4, W2-5) | No GUI code change; AC-77.14 pins it (D-22); AC-77.10 proves the backend half |
| 03:423 "is then re-raised (500)" | Conflicts with background synthesis | `WORKER_RULE`: the worker records and logs, never re-raises (D-19); row 12 edits 03:423 |
| Restart / shutdown | Not in the spec | `RESTART_RECOVERY`, `SHUTDOWN_STOP` (Local Canon transcript) |

#### Files Modified

| File | Action | Summary |
|---|---|---|
| `packages/core/src/avkit_core/services/tts.py` | modify | `ASYNC_GENERATE`, `WORKER_RULE`, `CANCEL_RULE`, `PARTIAL_CLEANUP`, `RESTART_RECOVERY`, `SHUTDOWN_STOP` |
| `packages/core/src/avkit_core/ports/storage.py` | modify | `TTSJobRepository.list_by_status` |
| `packages/infrastructure/src/avkit_infra/database/repositories.py` | modify | SQL `list_by_status` |
| `packages/infrastructure/src/avkit_infra/tts/adapter.py` | modify | `PROGRESS_LAZY` |
| `packages/api/src/avkit_api/main.py` | modify | lifespan calls; unload and dispose only when `stop_processing` returns `True` (`SHUTDOWN_STOP`; MEU-76 also edits it) |
| `packages/api/src/avkit_api/wiring.py` | modify | `_TTSRuntime`; `AppServices.tts` type |
| `packages/api/src/avkit_api/routes/tts.py` | modify | generate and cancel docstrings (OpenAPI description) |
| `mcp-server/src/toolsets/tts.ts` | modify | `MCP_TTS_TEXT` |
| `mcp-server/src/index.ts` | modify | `MCP_TTS_TEXT` (instructions line) |
| `mcp-server/scripts/audit/plan.ts` | modify | `AUDIT_CANCEL_STEP` (`destructiveStep` `raceLost` / `attempts`; the `tts.cancel` step) |
| `mcp-server/scripts/audit/fixtures.ts` | modify | `tts_cancel_text`; comment |
| `.agent/skills/mcp-tool-audit/resources/baseline-snapshot.json` | modify | rewritten only by `-Check audit` (`AUDIT_EXPECT`) |
| `openapi.committed.json` | modify | `OPENAPI_DIFF` |
| `tests/unit/test_tts_async.py` | create | AC-77.1–77.7, 77.9, 77.11 |
| `tests/integration/test_tts_assets.py` | modify | AC-77.8, 77.10; TA-9, TA-10; repair (f) |
| `tests/unit/test_services.py` | modify | TA-7, TA-8; repairs (a), (b), (e) |
| `tests/unit/test_domain.py` | modify | TA-5 |
| `tests/integration/test_sqlite_uow.py` | modify | TA-6 |
| `mcp-server/tests/tts.test.ts` | create | AC-77.12 |
| `mcp-server/tests/audit/tts-cancel-step.test.ts` | create | AC-77.13 |
| `ui/tests/e2e/tts-generate.test.ts` | modify | AC-77.14 (append) |

Repairs (b), (c) and (e) may touch further test fakes (for example `tests/e2e/api_fakes.py`). Row 1 lists every site in `walkthrough.md` §Census with the disposition `repair (x)`; each must be a fake-surface addition with no assertion change, or Stop condition S2 applies. `api-scope` accepts a changed `tests/` file outside the Files Modified tables only when §Census lists it with `repair (`.

## Out of Scope

| Item | Kind | Deferred-to MEU | Basis |
|---|---|---|---|
| MCP client timeout (`mcp-server/src/client.ts:14`, 30 s) | out-of-scope | — | With `ASYNC_GENERATE` no call waits for synthesis (D-21) |
| Unloading the model while a job is generating | out-of-scope | — | The 409 rules for load/unload are unchanged; `SHUTDOWN_STOP` covers shutdown only (D-20) |
| Persisting the cancel flag across restarts | out-of-scope | — | `RESTART_RECOVERY` fails the job instead |
| TTS page layout, device list, Format/Speed controls | deferred | MEU-75, MEU-79 | Session 35 (grouping `:117-121`, D-5) |
| TTS asset plumbing, no-torch ONNX path | deferred | MEU-72–74 | Session 32 |
| `MCP-AUDIT-CENSUS-PROBE-SINGLE-SHOT` and the other tech-debt rows | out-of-scope | — | grouping D-3 |
| A REST route to delete TTS output files | out-of-scope | — | `PARTIAL_CLEANUP` removes only partial output of the job itself |

## BUILD_PLAN.md Audit

The D3 hub is `docs/BUILD_PLAN.md` + `docs/build-plan/`. Row 12 makes these edits (`-Check hub` asserts each string):

1. `04-rest-api.md` §Unhandled errors (residual): the "Extractor failures" row names `ExtractError` → 422, tagged "Session 33 plan D-15".
2. `03-service-layer.md`:
   - `:422` (`error_message` row): "is then re-raised (500)" becomes "the background worker marks the job `Failed`; nothing is re-raised (Session 33 plan D-19)".
   - §TTS async generation: one row "Status" (`Generating` refines `Queued`/`Running`, D-18), one row "Restart" (`RESTART_RECOVERY`, `SHUTDOWN_STOP`).
   - §FFmpeg resolution: one row "No cache" (D-16).
3. `02-infrastructure.md:430`: "Probe binary once; cache" becomes "Resolve on every use; no cache (Session 33 plan D-16)", and the bundle path becomes `{install}/resources/ffmpeg/ffmpeg.exe`.
4. `07-distribution.md:159,164`: `resources/extra/ffmpeg` becomes `resources/ffmpeg`.
5. `05-mcp-server.md:95`: "(stops a run; files already written stay)" becomes "(stops a running job; its partial output is removed)"; `:275` matches `MCP_TTS_TEXT`.
6. `docs/BUILD_PLAN.md` and `.agent/context/meu-registry.md`: the AUTOGEN status regions are re-rendered by `tools/meu_status.py render` (H1-5 / H2-2) and checked with `render --check`.

Row 12 then re-runs the doc-reading Vitest suites (`layout-canon`, `queue-canon`, `gui-actions-audit`) and `mcp-server/tests/audit/docs.test.ts`.

## Verification Plan

Every command is a `validate-task.ps1 -Check <name>`. It runs each tool through `rtk proxy` into `C:/Temp/av-kit/s33-*` receipts, and `exec_checks.py` (stdlib) evaluates the files the tools wrote.

0. **Plan-local static verifier.** `python docs/execution/plans/2026-10-14-backend-robustness/plan_checks.py static` and `selftest`. It runs no product code.
1. **Row 0 `prereq`.** It checks the context-tool gate, that MEU-76/77/78 are `pending`, that the plan review is `approved` and the execution authorization is recorded, and that `P:/agentic-framework` and the registry are readable. It then runs the installs (`uv sync --frozen --all-packages`, `npm --prefix ui ci` plus `install.js`, `npm --prefix mcp-server ci`), writes `baseline.sha` and the overlap list, and measures the MCP suite into `baseline-counts.json`.
2. **Row 1 `census`.** `rg` sweeps for every pinned expectation this design changes. Each hit must map to one TA, one repair or "unaffected" in `walkthrough.md` §Census (S2 otherwise).
3. **Red/Green/Gate per MEU** (rows 2–11). `RED_RULE` for Red. Green: the MEU's targeted files pass with zero failures. Gate: the MEU's targeted files, the touched packages' suites and `py-types`/`ui-types`/`mcp-types` for that MEU.
4. **Row 12 `hub`.** String assertions over the edits above, `meu_status render --check`, and the doc suites.
5. **H1-2 `audit`.** The authoritative `/mcp-audit` against the pre-session baseline (`AUDIT_COMPARISON`) with `--update-baseline`, then `baseline_carry.py`; `AUDIT_EXPECT`; `AUDIT_FINGERPRINT` measured before and after, equal, and recorded in `audit-fingerprint.json`.
6. **H1-3 `windows-gate`.** The full PROFILE D6 set (stage list in `validate-task.ps1`, Session 30 order), `GATE_FINGERPRINT` before and after.
7. **H1-4 `gate-check`.** Stage order, exits, `COUNT_FLOORS`, both fingerprints, and the audit summary (`audit-check`).
8. **Closeout.** `ssot-review`, `api-scope` (`PRODUCT_SCOPE`, `OPENAPI_DIFF`), `handoff-ac`, `review-check`, `post-review-state`.

### Planning receipts

Run at plan time (2026-10-15, local, before the dispatch; the plan folder keeps its 2026-10-14 date). Each command's output is in `C:/Temp/av-kit/s33-plan-*.txt`:

```text
$ python docs/execution/plans/2026-10-14-backend-robustness/plan_checks.py static
$ python docs/execution/plans/2026-10-14-backend-robustness/plan_checks.py selftest
$ uv run python tools/lint_task_contract.py --allowed-builder-classes avkit_builder,avkit_coordinator,avkit_verifier --task docs/execution/plans/2026-10-14-backend-robustness/task.md
$ pwsh -NoProfile -Command "[ScriptBlock]::Create((Get-Content -Raw docs/execution/plans/2026-10-14-backend-robustness/validate-task.ps1)) | Out-Null"
$ python -m py_compile docs/execution/plans/2026-10-14-backend-robustness/exec_checks.py docs/execution/plans/2026-10-14-backend-robustness/plan_checks.py docs/execution/plans/2026-10-14-backend-robustness/baseline_carry.py
$ python docs/execution/plans/2026-10-14-backend-robustness/exec_checks.py selftest
```

The results are in §Planning receipt results at the end of this file.

## GUI Element Compliance Check

The §4A reference files are not shipped: `docs/gui-element-reference.md`, `docs/gui-button-index.md`, `docs/gui-input-field-index.md`, `docs/gui-output-index.md` and `.agent/docs/gui-standards-enforcement.md` are absent (`gui-refs-not-shipped`, create-plan §4A note). The applicable canon is used instead:

| Element | Variant / size | States | Standard | E2E |
|---|---|---|---|---|
| Dependencies FFprobe row (`deps-ffprobe-row`) | not a control; `StatusChip` | available / missing / loading (no chip until loaded) | G32 tokens; same row markup as yt-dlp/FFmpeg | AC-78.9 |
| FFmpeg row detail | unchanged markup | resolved path shown | unchanged | AC-78.9 |
| Error toasts / inline errors fed by `apiFetch` | unchanged | text now names the request id | G15 (error text actionable) | AC-76.8 (unit) |
| TTS run bar | unchanged | `Generating` → Done via polling | unchanged (MEU-62) | AC-77.14; existing `tts-generate.test.ts` |

`source-audit` enforces G32/G33 (no raw hex, no `transition-all`) on the touched UI files. The one new element has a registered test id and an Electron assertion (E2).

## Stop Conditions

| ID | Condition | Action |
|---|---|---|
| S1 | `prereq` refuses: a graph directory appeared, an MEU is not `pending`, the plan review is not `approved`, the execution message is not recorded, or an install fails | Stop and report. |
| S2 | The census finds an existing expectation this design contradicts, other than TA-1 to TA-11, or a fake repair that would change an assertion | Stop for the human with a Decision Brief naming the test and the minimal amendment. No test edit. |
| S3 | A Red fails `RED_RULE` (a collection or load error, a non-assertion failure, or an AC with no decisive failure) | Fix the test setup only, then re-prove Red. |
| S4 | Row 0 finds Session 31 (or any other branch) merged into this branch's base with a conflicting change to a Files Modified path, or `P:/av-kit` work that this session's files would overwrite | Stop; rebase only on the user's instruction. |
| S5 | `AUDIT_EXPECT` fails (an action other than `tts.cancel` changes verdict, a `REGRESSION`/`REMOVED`, cleanup not ok) | Stop. `-Check audit` restores the prior baseline; present a Decision Brief. Never edit the baseline by hand. |
| S6 | A gate failure that is not a product defect (environment, external input drift) | Decision Brief and an `A-n` row in `walkthrough.md` §Gate decisions. No self-authorized test change. |
| S7 | Review cap (plan 6 since A-3, execution 6), or the reviewer is unavailable | HARD STOP with TL;DR (create-plan §5d). |
| S8 | A TA is not authorized (the plan review rejects it, or the execution message vetoes it) | Do not edit that test. Stop before the Green row that needs it and present a Decision Brief. |
| S9 | The context passes about 50 % before row 8 | Close out MEU-76 and MEU-78 as Session 33 and carry MEU-77 to 33b (D-11). |

## Decision Log

Carried from the grouping (stage `grouping`, reflection carry-forward): **D-1, D-3, D-4, D-6** are the rows the grouping names for Sessions 32–39 (`:223`). The H2-1 reflection still carries **every** grouping §8 row, D-1 to D-7, with stage `grouping`, because `validate_closeout_artifacts.py` requires the whole §8 table when the grouping is a decision source (Session 27 Review R2-1). The triage decisions (D-40, D-44, D-45, D-67) are cited in prose only, because their ids collide with plan ids.

Planning decisions:

```yaml
decision_log:
  - id: D-8
    stage: planning
    question: "Where do the gates run, given the driver is local Claude Code on Windows?"
    resolution: autonomous
    class: two-way
    chosen: "Everything local: one validate-task.ps1, no .sh, no container pre-gate; the driver runs WINDOWS_GATE and the authoritative MCP audit"
    source_tag: Local Canon
    precedents: [".agent/context/harness.local.md §Claude Code (local driver, pwsh, rtk)", "grouping :107 — the MCP audit re-baseline and WINDOWS_GATE are local stages", "docs/execution/plans/2026-10-02-capture-flatten-backup/validate-task.ps1 — the audit and gate checks this plan reuses"]
    research: { engine: none, sources: [] }
    reasoning: "The grouping's container/local split assumed a cloud driver. Here the driver is on the target machine, so a container rehearsal adds a round trip and no evidence. The authoritative gate runs on the same Windows host either way."
  - id: D-9
    stage: planning
    question: "Is the grouping's §9 scoping review (not yet run) a prerequisite for this plan?"
    resolution: autonomous
    class: two-way
    chosen: "No; this plan's own independent review covers the three MEUs' scope"
    source_tag: Local Canon
    precedents: [".agent/context/grouping/2026-10-09-triage-residuals-session-grouping.md:231 — status 'not yet run', fallback reviewer Mat", "docs/execution/plans/2026-10-02-capture-flatten-backup/implementation-plan.md — Session 30 executed with the same §9 review pending"]
    research: { engine: none, sources: [] }
    reasoning: "§9's criteria (traceability, one coherent change per MEU, dependencies) are checkable on this plan; the plan review receives the grouping as canon. Waiting would block every P2 session on an unrelated registry problem."
  - id: D-10
    stage: planning
    question: "How is the overlap with Session 31 (executing in P:/av-kit) handled?"
    resolution: autonomous
    class: two-way
    chosen: "Work in the separate worktree; row 0 records the overlapping paths; whichever session merges second resolves; S4 stops on a real conflict"
    source_tag: Local Canon
    precedents: ["git -C P:/av-kit log -1 — 0cfa40a, Session 31 R1 fixes on claude/vigilant-volta-f04tvs", "Session 31 plan Files Modified — SettingsPage.tsx, ui/tests/e2e/settings.test.ts"]
    research: { engine: none, sources: [] }
    reasoning: "The shared files are edited in different regions (Session 31: section frames and rail; Session 33: the Dependencies card and a new spec). A rebase now would pull unreviewed Session 31 code into this gate."
  - id: D-11
    stage: planning
    question: "Split MEU-77 to Session 33b?"
    resolution: autonomous
    class: two-way
    chosen: "Not up front; split at row 8 only if context passes about 50 % (S9)"
    source_tag: Local Canon
    precedents: ["grouping :109 — split flag 'candidate'", "Session 30 execution — one plan carried REST+MCP+audit work"]
    research: { engine: none, sources: [] }
    reasoning: "The three MEUs share one OpenAPI diff, one audit and one gate. Splitting up front doubles the gate cost; S9 keeps the escape."
  - id: D-12
    stage: planning
    question: "Dispatch the plan review to Codex without asking first?"
    resolution: autonomous
    class: two-way
    chosen: "Yes, with a metered-dispatch warning before each dispatch"
    source_tag: Local Canon
    precedents: [".agent/workflows/create-plan.md §5 — auto-dispatch with a correction loop", "PROFILE B2 — metered reviewer"]
    research: { engine: none, sources: [] }
    reasoning: "The workflow mandates the dispatch; the warning keeps the cost visible."
  - id: D-13
    stage: planning
    question: "Which event and fields carry the unhandled-error log?"
    resolution: autonomous
    class: two-way
    chosen: "ERROR_EVENT: api.unhandled_error with request_id, route, method, error, exc_info; mapped statuses are not logged"
    source_tag: Spec
    precedents: ["docs/build-plan/04-rest-api.md:433", "packages/core/src/avkit_core/services/tts.py — tts.generate_failed (event + job_id + error) pattern", "packages/core/src/avkit_core/services/health.py:37 — CONSOLE_FIELDS"]
    research: { engine: none, sources: [] }
    reasoning: "The spec asks for request id, route and traceback. Mapped 503s are expected states (ffmpeg missing, capture unsupported) that already have their own messages; logging them as unhandled would bury real faults."
  - id: D-14
    stage: planning
    question: "How does the 500 get CORS headers?"
    resolution: autonomous
    class: two-way
    chosen: "Catch in the existing request_id_middleware, which already runs inside CORSMiddleware"
    source_tag: Research-backed
    precedents: ["packages/api/src/avkit_api/main.py:73-90 — middleware order", "docs/build-plan/04-rest-api.md:431 — local probe on Starlette 1.6.0"]
    research: { engine: native, sources: ["https://www.starlette.io/middleware/ — ServerErrorMiddleware is always outermost; exception handlers for Exception/500 run there", "https://github.com/encode/starlette/issues/1175 — 500 responses from the Exception handler lack CORS headers"] }
    reasoning: "No new middleware and no ordering change. Re-ordering CORS or a second CORS layer would affect every response; catching where the request id is already bound also gives the log its id."
  - id: D-15
    stage: planning
    question: "Which status does a yt-dlp extract failure map to?"
    resolution: autonomous
    class: two-way
    chosen: "ExtractError -> 422 with yt-dlp's message"
    source_tag: Spec
    precedents: ["docs/build-plan/04-rest-api.md §Status mapping — 422 for a request that cannot be processed as given (AgeRestrictedError, CookieTestError are 422)", "packages/api/src/avkit_api/errors.py:25-38"]
    research: { engine: none, sources: [] }
    reasoning: "The URL was well-formed but YouTube refused it; the user must act (cookies, another URL). 422 matches AgeRestrictedError, the closest existing case. 502 was rejected: av-kit is not a gateway, and a 5xx would be masked."
  - id: D-16
    stage: planning
    question: "Cache the ffmpeg resolution at all?"
    resolution: autonomous
    class: two-way
    chosen: "No cache: resolve on every use (a few stat calls); only GPU capabilities stay cached, per path"
    source_tag: Spec
    precedents: ["docs/build-plan/03-service-layer.md:492 — 'a missing binary is not latched'", "docs/build-plan/02-infrastructure.md:430 — 'Probe binary once; cache' (superseded)"]
    research: { engine: none, sources: [] }
    reasoning: "A cache needs an invalidation signal from settings; resolving costs less than one ffmpeg spawn. GPU capability probing spawns ffmpeg, so it keeps a cache keyed by the binary."
  - id: D-17
    stage: planning
    question: "Does cancel remove partial output, against 05:95 'files already written stay'?"
    resolution: autonomous
    class: two-way
    chosen: "Yes: remove the job's .wav and .mp3 on Cancelled and Failed; correct 05:95"
    source_tag: Spec
    precedents: ["docs/build-plan/03-service-layer.md:475 — 'no partial output file remains'", "packages/core/src/avkit_core/services/capture.py:900 — _unlink_if_file"]
    research: { engine: none, sources: [] }
    reasoning: "03:477 is the later, MEU-specific rule (Triage D-44). Under synchronous generation 05:95 was moot because nothing could cancel a running job."
  - id: D-18
    stage: planning
    question: "Which status does generate return, given the spec says Queued/Running?"
    resolution: autonomous
    class: two-way
    chosen: "Generating (the TTS enum's running state); Pending is never returned"
    source_tag: Local Canon
    precedents: ["packages/core/src/avkit_core/domain/tts.py:35-36 — Pending -> Generating -> Done/Failed/Cancelled", "ui/src/renderer/src/features/tts/useTtsJob.ts:64 — polling keys on Generating"]
    research: { engine: none, sources: [] }
    reasoning: "Generic queue words in 03:476; TTS runs one job, so the job is running from the moment it is accepted. Returning Generating keeps the GUI's polling unchanged."
  - id: D-19
    stage: planning
    question: "What happens to the 03:423 rule that an unexpected exception is re-raised (500)?"
    resolution: autonomous
    class: two-way
    chosen: "The worker records Failed with the exception type and message ('Type: message'), logs with exc_info and never re-raises; amend 03:423"
    source_tag: Spec
    precedents: ["docs/build-plan/03-service-layer.md:422", "docs/build-plan/03-service-layer.md:474 — synthesis runs in the background"]
    research: { engine: none, sources: [] }
    reasoning: "There is no request left to fail once generate has returned. The message rule (every Failed job carries one) is kept; only the re-raise is gone. TA-7, TA-8 and TA-9 follow from this."
  - id: D-20
    stage: planning
    question: "Guard model unload while a job is generating?"
    resolution: autonomous
    class: two-way
    chosen: "Out of scope; the adapter's existing errors mark the job Failed"
    source_tag: Local Canon
    precedents: ["packages/infrastructure/src/avkit_infra/tts/adapter.py:263-264 — 'no model is loaded' raises ModelLoadError"]
    research: { engine: none, sources: [] }
    reasoning: "WORKER_RULE turns that error into a Failed job with a message. A new 409 on unload is a separate contract change."
  - id: D-21
    stage: planning
    question: "Change the MCP client timeout?"
    resolution: autonomous
    class: two-way
    chosen: "No; client.ts is unchanged"
    source_tag: Local Canon
    precedents: ["mcp-server/src/client.ts:14 — 30 s"]
    research: { engine: none, sources: [] }
    reasoning: "Generate now returns in milliseconds, so the timeout no longer bites. The grouping lists client.ts as a candidate file only."
  - id: D-22
    stage: planning
    question: "Does the TTS run bar need a GUI change?"
    resolution: autonomous
    class: two-way
    chosen: "No code change; AC-77.14 is a pin (RED_RULE item 5) over the existing polling and cancel"
    source_tag: Local Canon
    precedents: ["ui/src/renderer/src/features/tts/useTtsJob.ts:64-78 — refetchInterval while Generating", "ui/src/renderer/src/features/tts/tts-controls.ts:23-24 — Generating blocks generate and enables cancel"]
    research: { engine: none, sources: [] }
    reasoning: "The run bar already polls a Generating job (W2-4) and cancels (W2-5) against the seam, which answers Generating. Under a synchronous backend it never saw one in production. The Electron suite runs on renderer fetch seams, so it cannot observe the backend; the backend contract is AC-77.10. AC-77.14 pins the GUI half so a later GUI change cannot drop it."
  - id: D-23
    stage: planning
    question: "Where are the H2-2 known issues resolved?"
    resolution: autonomous
    class: two-way
    chosen: "H2-2 resolves API-UNHANDLED-ERROR-OPAQUE, FFMPEG-RESOLUTION-DIVERGENCE and MCP-TTS-GENERATE-SYNCHRONOUS with evidence files under the plan directory"
    source_tag: Local Canon
    precedents: ["docs/execution/plans/2026-10-02-capture-flatten-backup/task.md H2-2", ".agent/context/known-issues.yaml:1102,1181,1892"]
    research: { engine: none, sources: [] }
    reasoning: "Same closeout path as Session 30."
  - id: D-24
    stage: planning
    question: "What does generate return: the in-memory job or the stored row?"
    resolution: autonomous
    class: two-way
    chosen: "get_status(id): the row as stored, after the worker was spawned"
    source_tag: Local Canon
    precedents: ["packages/core/src/avkit_core/services/tts.py:103-108 — get_status"]
    research: { engine: none, sources: [] }
    reasoning: "With a synchronous test spawn the row may already be Done; returning the stored row keeps the REST answer truthful in both modes."
  - id: D-25
    stage: planning
    question: "How are cancel and the worker's terminal write ordered (plan review R1 F1)?"
    resolution: autonomous
    class: two-way
    chosen: "_lock is the single linearization point: cancel sets the flag under it only for the current job; _finish reads the flag, writes the terminal row and clears _current_id and the flag in one critical section"
    source_tag: Local Canon
    precedents: ["packages/core/src/avkit_core/services/tts.py — _lock already guards the 409 check and _current_id"]
    research: { engine: none, sources: [] }
    reasoning: "With only unlocked flag checks, a cancel between the last check and the Done write leaves a Done row while the route answers 204, and its flag can cancel the next job. One lock around the decision and the write makes each cancel either fully before (Cancelled, no output) or fully after (no-op)."
  - id: D-26
    stage: planning
    question: "What happens at shutdown when the TTS worker does not stop within the timeout (R1 F2)?"
    resolution: autonomous
    class: two-way
    chosen: "stop_processing returns the wait result; the lifespan skips models.unload and the engine dispose when it is False; _closing refuses new generate calls"
    source_tag: Local Canon
    precedents: ["packages/api/src/avkit_api/main.py:39-50 — _lifespan", "TTSService.recover_stale_processing — RESTART_RECOVERY"]
    research: { engine: none, sources: [] }
    reasoning: "Tearing the model and database down under a live worker turns a slow stop into a crash path. Skipping both is safe because the process is exiting; the daemon thread dies with it and the next start fails the row."
  - id: D-27
    stage: planning
    question: "How does the audit's tts.cancel step avoid racing a job that finishes first (R1 F3)?"
    resolution: autonomous
    class: two-way
    chosen: "destructiveStep gains optional raceLost and attempts; tts.cancel retries up to 3 times only when its job turned Done before the confirmed call"
    source_tag: Local Canon
    precedents: ["mcp-server/scripts/audit/plan.ts:206-265 — destructiveStep precondition and reestablish"]
    research: { engine: none, sources: [] }
    reasoning: "A long text makes the race unlikely but not impossible on a fast machine. Retrying only on Done keeps a real failure (still Generating, or Failed) a failure, and the default of one attempt leaves every other step unchanged."
  - id: D-28
    stage: planning
    question: "What does a rerun of the audit compare against (R1 F5)?"
    resolution: autonomous
    class: two-way
    chosen: "The pre-session baseline from baseline.sha, written over the baseline file before every attempt; failure restores the start-of-check copy and deletes the attempt's plan-folder evidence"
    source_tag: Local Canon
    precedents: ["mcp-server/scripts/audit/classify.ts — computeDelta (pass→pass is UNCHANGED)", "mcp-server/scripts/audit/run.ts — --baseline is the comparison and the update target"]
    research: { engine: none, sources: [] }
    reasoning: "After one passing attempt the baseline already holds tts.cancel pass, so a rerun would report UNCHANGED and AUDIT_EXPECT would refuse. Comparing every attempt with the committed pre-session file keeps FIXED reproducible."
  - id: D-29
    stage: planning
    question: "Which paths do GATE_FINGERPRINT and AUDIT_FINGERPRINT bind (R1 F4, F6)?"
    resolution: autonomous
    class: two-way
    chosen: "The whole working tree minus GATE_EXCLUDED (the files rows after the gate write); the audit fingerprint is measured before the prep and after the carry"
    source_tag: Local Canon
    precedents: ["docs/execution/plans/2026-09-26-framework-update-adoption/adoption-manifest.json — gate tests read files far outside the code dirs", ".agent/workflows/mcp-audit.md — read by the audit"]
    research: { engine: none, sources: [] }
    reasoning: "An include-list misses gate inputs (other plan dirs, workflows, schemas, templates). Excluding only the files later rows write binds everything else, and the post-review rerun covers the tests that read the excluded files."
  - id: D-30
    stage: planning
    question: "How does shutdown see a TTS job that was admitted but whose worker has not started (R2 F2)?"
    resolution: autonomous
    class: two-way
    chosen: "_current_id is the reservation, published under _lock at admission and cleared only by _finish; wait_idle waits on a Condition over _lock until it is None; the worker checks the flag before prepare"
    source_tag: Local Canon
    precedents: ["packages/core/src/avkit_core/services/tts.py:89,160-166 — _lock (threading.Lock) already guards _current_id at admission", "TTSService._finish — CANCEL_RULE (D-25)"]
    research: { engine: none, sources: [] }
    reasoning: "Waiting on a thread misses the interval between admission and spawn. The reservation already exists and is cleared on every path (worker finally and spawn failure), so waiting on it makes accepted work busy until its terminal write. Spawn stays outside the lock because a synchronous spawn re-enters _lock in _finish."
  - id: D-31
    stage: planning
    question: "How does shutdown see a generate caller that still touches a collaborator after the reservation clears, or before admission (R3 F2)?"
    resolution: autonomous
    class: two-way
    chosen: "generate enters under _lock (refused when _closing, before any collaborator call) and increments _callers; a finally decrements it under _idle and notifies; wait_idle waits until _current_id is None and _callers == 0"
    source_tag: Local Canon
    precedents: ["packages/core/src/avkit_core/services/tts.py:103-108 — get_status opens a unit of work", "packages/core/src/avkit_core/services/tts.py:131-139 — get_model_status, list_voices and _require_assets run before admission", "D-24 — generate returns the stored row after spawn"]
    research: { engine: none, sources: [] }
    reasoning: "The reservation covers the worker but not the caller: a fast or synchronous worker clears it before the caller's get_status read, and the synchronous checks call the model port before admission. Counting each call from entry to return covers both without holding the non-reentrant _lock across spawn and keeps the stored-row return (D-24) for a synchronous spawn."
```

## Research References

- Starlette middleware and `ServerErrorMiddleware`: https://www.starlette.io/middleware/
- Starlette issue 1175 (500 without CORS headers): https://github.com/encode/starlette/issues/1175
- yt-dlp `ffmpeg_location` option (YoutubeDL params): https://github.com/yt-dlp/yt-dlp/blob/master/yt_dlp/YoutubeDL.py
- structlog testing (`capture_logs`): https://www.structlog.org/en/stable/testing.html

## Validation stage contract

The stages bind to PROFILE D6 (`.agent/docs/commands.md` §D6): static (`py-types`, `py-lint`, `ui-types`, `ui-lint`, `mcp-types`, `plan_checks.py static`, `lint_task_contract.py`), targeted (`red*`, `green*`, `gate*`), and one fresh full gate (`WINDOWS_GATE`, authoritative). Each check writes `C:/Temp/av-kit/s33-*` receipts through `rtk proxy` and is blocking. `windows-gate` records argv, exit, duration and receipt for each stage in `windows-gate-result.json`.

Input identity is obtained independently of the run: `git rev-parse HEAD`, `baseline.sha`, `GATE_FINGERPRINT`, the three lockfile hashes, the Node and Electron versions, and the two external inputs (`P:/agentic-framework` HEAD, `P:/.agent/model-registry.json` hash) in the preflight. `gate-check` binds the result to the reviewed tree over `GATED_PATHS`. Any change to those paths after the gate invalidates it, and a new attempt is required. Intermediate evidence is never reused for the final review; the handoffs carry `evidence.v1` records from the fresh gate.

## Round 1 Review Corrections

The round 1 plan review (`.agent/context/handoffs/2026-10-14-backend-robustness-plan-critical-review.md`, Codex `gpt-6.1-sol`, `changes_required`, 8 findings) is answered here. The blast-radius census and the per-hit dispositions are in `review-r1-census.md`.

| Finding | Severity | Correction | Contract / AC | Decision |
|---|---|---|---|---|
| F1 cancel vs terminal write race | High | `_lock` linearizes `cancel` and the terminal write; `_finish` decides and writes under the lock and clears `_current_id` and the flag | `CANCEL_RULE`, `WORKER_RULE`, `ASYNC_GENERATE`; AC-77.5 (b) barrier | D-25 |
| F2 shutdown ignores the wait result | High | `stop_processing` returns `bool`; the lifespan skips unload and dispose on `False`; `_closing` refuses new runs | `SHUTDOWN_STOP`, `ASYNC_GENERATE`, `FIXTURE_REPAIRS` (e); AC-77.9 (b)-(d) | D-26 |
| F3 audit cancel can race a finished job | High | `destructiveStep` `raceLost` / `attempts`; `tts.cancel` retries up to 3 times only on `Done` | `AUDIT_CANCEL_STEP`; AC-77.13 (a)-(d) | D-27 |
| F4 audit fingerprint measured only after the run | High | measured before the prep and after the carry; `audit-fingerprint.json {before, after}`; `gate-check` requires both equal to the current tree | `AUDIT_FINGERPRINT`; `exec_checks.py` `audit-fp`, `check_audit_fp` | D-29 |
| F5 a rerun reports UNCHANGED, not FIXED | Medium | every attempt compares with the pre-session baseline; failure restores the start-of-check copy and deletes the attempt's evidence | `AUDIT_COMPARISON` (new) | D-28 |
| F6 GATED_PATHS omits real gate inputs | Medium | the whole tree minus `GATE_EXCLUDED`; `post-review-state` also re-runs `test_framework_adoption.py` | `GATED_PATHS`, `GATE_FINGERPRINT`; `plan_checks.py` parity on `GATE_EXCLUDED` | D-29 |
| F7 OpenAPI path template | Low | `/api/v1/tts/{id}`, as `openapi.committed.json` names it | `OPENAPI_DIFF`; `exec_checks.OPENAPI_PATHS` | — |
| F8 `review-check` compares `target_plan` as a string | Low | `target_plan` is resolved as a path against this checkout; another checkout's path fails | `exec_checks.py` `check_review`, `same_file` | — |

## Round 2 Review Corrections

Round 2 (same canonical file, `changes_required`, 1 finding) closed F1 and F3 to F8 and kept F2 open on the interval between admission and worker registration. The census is in `review-r2-census.md`.

| Finding | Severity | Correction | Contract / AC | Decision |
|---|---|---|---|---|
| F2 (R2) shutdown can observe idle between admission and spawn | High | `_current_id` is the reservation, published under `_lock` before release and cleared only by `_finish`; `wait_idle` waits on `_idle` (a `Condition` over `_lock`) until it is `None`; `_finish` notifies; the worker reads the flag before `prepare`; spawn stays outside the lock | `ASYNC_GENERATE`, `WORKER_RULE`, `CANCEL_RULE`, `SHUTDOWN_STOP`; AC-77.9 (e)-(f) | D-30 |

## Round 3 Review Corrections

Round 3 (same canonical file, `changes_required`, 1 finding) closed F1 and F3 to F8 again and kept F2 open on the generate caller's own database read after the worker reservation clears. The census is in `review-r3-census.md`.

| Finding | Severity | Correction | Contract / AC | Decision |
|---|---|---|---|---|
| F2 (R3) the admitted generate caller is not drained | High | `generate` enters under `_lock` (refused when `_closing`, before any collaborator call) and increments `_callers`; a `finally` decrements it under `_idle` and notifies; `wait_idle` waits until `_current_id is None and _callers == 0`; spawn stays outside the lock and the stored-row return is kept | `ASYNC_GENERATE`, `WORKER_RULE`, `SHUTDOWN_STOP`; AC-77.9 (g)-(h) | D-31 |

## Planning receipt results

Run 2026-10-15 from the worktree root at HEAD `78610200`, after the round 3 corrections and before the round 4 plan review dispatch. Every command exited 0.

| Receipt | Command | Result |
|---------|---------|--------|
| `s33-plan-static.txt` | `plan_checks.py static` | `PASS static: 24 task rows; script, exec_checks, plan contracts, references and file targets agree` |
| `s33-plan-selftest.txt` | `plan_checks.py selftest` | 19 of 19 injected defects reported; `PASS selftest` |
| `s33-plan-lint.txt` | `tools/lint_task_contract.py` | `OK: 24 row(s); 10-column table (with builder_model); 24 row(s) fully checked` |
| `s33-plan-ps1parse.txt` | `[ScriptBlock]::Create(validate-task.ps1)` | parsed, no errors |
| `s33-plan-pycompile.txt` | `py_compile` on `exec_checks.py`, `plan_checks.py`, `baseline_carry.py` | compiled, no errors |
| `s33-plan-exec-selftest.txt` | `exec_checks.py selftest` | 65 of 65 cases; `PASS selftest` |

**§4A GUI reference check:** the five reference files are still absent (re-checked 2026-10-15; `gui-refs-not-shipped`). The applicable canon (G15, G32) is used instead, as §GUI Element Compliance Check records.

**Canon line citations:** re-measured against this worktree at plan time. The drifted citations were corrected to 02:428, 03:423, 03:476-480 and 04:435-438.

## Execution Correction Notes

Recorded during execution so that no plan-level contract changes silently. Each item is visible to the execution review.

| Item | Change | Evidence |
|---|---|---|
| Execution review R1 F1 (`PARTIAL_CLEANUP`, AC-77.4 / AC-77.5 / AC-77.6) | The independent execution review (round 1, High) found that `_remove_partial` re-read `tts.output_path` at cleanup time, while `_work` had written the WAV and MP3 under the root it read before the write. A `PUT /settings/tts` that changed the output directory mid-job therefore made Cancelled and Failed cleanup miss the real files. `{root}` in `PARTIAL_CLEANUP` now means the root the job itself captured: `_work` builds both paths once, before the WAV write, and passes them to `_finish`, which unlinks exactly those paths. `CANCEL_RULE`, the `_lock` linearization (D-25) and the Done path are unchanged. One appended parametrized test in `tests/unit/test_tts_async.py` (WAV-write and MP3-convert hooks, Cancelled and Failed; Red first: all 4 cases left the old-root files) and one additive `_Stack.settings` field. | `.agent/context/handoffs/2026-10-14-backend-robustness-implementation-critical-review.md` F1; `walkthrough.md` §Execution review corrections |
| Closeout validator wording (A-14, plan D-17 and D-19) | `tools/validate_closeout_artifacts.py` reads `{id}` and `<message>` as unfilled template markers (`PLACEHOLDER`), so H2-1 refused two filled decisions. D-17's chosen text now says "the job's .wav and .mp3" and D-19's says "the exception type and message ('Type: message')". Meaning unchanged; no AC, contract or test changes. | `walkthrough.md` §Gate decisions A-14 |
