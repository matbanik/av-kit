---
date: "2026-08-18"
review_mode: "plan"
target_plan: "docs/BUILD_PLAN.md"
verdict: "approved"
findings_count: 12
template_version: "2.1"
requested_verbosity: "detailed"
agent: "gpt-5.6-sol"
---

# Critical Review: av-kit BUILD_PLAN architecture

> **Review Mode**: `plan` (build-plan / architecture; no execution `task.md` exists)
> **Verdict**: `changes_required`

---

## Scope

**Target**: `docs/BUILD_PLAN.md`, `docs/build-plan/00-overview.md`–`07-distribution.md`, inspiration Markdown, and read-only Zorivest GUI convention sources
**Review Type**: independent build-plan architecture review
**Checklist Applied**: architecture soundness, cross-phase contract consistency, inspiration fidelity, GUI-twin convention adoption

External source dumps under `_inspiration/external_code/` were not reviewed. Named MVP deferrals (Conversion GUI/`ConversionJob`, OCR Part 1, SSE, multi-file TTS, MCP Guard) were treated as intentional.

---

## Findings

| # | Severity | Finding | File:Line | Recommendation | Status |
|---|----------|---------|-----------|----------------|--------|
| A1 | High | Ephemeral backend port is not coherently discoverable by the parallel-start renderer or the static MCP configuration. | `docs/build-plan/06-gui.md:19-51`; `docs/build-plan/07-distribution.md:69-88`; `docs/build-plan/07-distribution.md:164-175` | Define one validated runtime descriptor/discovery contract consumed by Electron and MCP. | open |
| A2 | High | Canonical Phase 1 omits required filesystem/model catalog ports; Phase 3 retrofits them and permits direct audio IO. | `docs/build-plan/01-domain-layer.md:420-495`; `docs/build-plan/03-service-layer.md:42-61`; `docs/build-plan/03-service-layer.md:297-308` | Put all ports/DTOs/errors in Phase 1 before planning implementation. | open |
| A3 | High | GUI `apiFetch` always parses JSON although multiple specified successful mutations return 204. | `docs/build-plan/06-gui.md:90-108`; `docs/build-plan/04-rest-api.md:87-101` | Handle empty/204 responses and decode `ErrorEnvelope`. | open |
| A4 | High | Required ConsolePanel has no backend-to-renderer transport. | `docs/build-plan/06-gui.md:75-87`; `docs/build-plan/06-gui.md:260-279`; `docs/build-plan/04-rest-api.md:316-362` | Define a bounded, redacted Electron relay/IPC log data plane without reintroducing SSE. | open |
| A5 | High | Transcript Stop alternately means parent `Cancelled` or a bare loop exit leaving durable state unchanged. | `docs/build-plan/03-service-layer.md:72-81`; `docs/build-plan/03-service-layer.md:176-222` | Specify and test one durable Stop transition. | open |
| A6 | High | Secure preload omits open-file/folder/ZIP, clipboard, and constrained file-read capabilities required by Phase 6 actions. | `docs/build-plan/06-gui.md:74-87`; `docs/build-plan/06-gui.md:646-653`; `docs/build-plan/06-gui.md:758-767` | Add typed allowlisted IPC plus BrowserWindow navigation/security rules. | open |
| A7 | Medium | Model download is 202/async with per-row progress, but no required in-flight runtime shape or worker semantics exist. | `docs/build-plan/03-service-layer.md:314-325`; `docs/build-plan/04-rest-api.md:266-284` | Define non-persisted `ModelDownloadRuntime`; keep no `ModelFetchJob`. | open |
| A8 | Medium | Phase 6 lacks Zorivest’s command-registry schema/action catalog and HelpCard/help-search contracts. | `docs/build-plan/06-gui.md:252-259`; `docs/build-plan/06-gui.md:1133-1153` | Add typed registry, GUI actions index, help modules, registration audit, and E2E. | open |
| A9 | Medium | FFmpeg probe order differs between Phase 2 and locked Phase 7. | `docs/build-plan/02-infrastructure.md:427-439`; `docs/build-plan/07-distribution.md:104-118` | Use setting → bundle → PATH everywhere and add the missing setting now. | open |
| A10 | Medium | Download polling example uses `isProcessing` before declaration. | `docs/build-plan/06-gui.md:511-527` | Replace with compiling TanStack Query v5 callback form. | open |
| A11 | Low | Phase 1 still leaves dotted-vs-leaf setting keys open after later phases lock leaf keys. | `docs/build-plan/01-domain-layer.md:366-376` | Make Phase 1 leaf-only. | open |
| A12 | Low | Phase 2 prose implies MCP directly shares/hits SQLite despite Phase 5 REST-only prohibition. | `docs/build-plan/02-infrastructure.md:53-64`; `docs/build-plan/05-mcp-server.md:61-66` | Reword WAL rationale; retain REST-only MCP. | open |

---

## Checklist Results

### Information Retrieval (IR)

| Check | Result | Evidence |
|-------|--------|----------|
| All AC have source labels | n/a | This is a build-plan architecture review, not an execution-plan review; no `task.md` or FIC exists. |
| Validation cells are exact commands | partial | Phase specs name target commands; Phase 7 still says packaged exact receipts are TBD (`docs/build-plan/07-distribution.md:248-255`). |
| BUILD_PLAN audit row present | n/a | No execution task table exists. Master-to-phase freshness was reviewed in `final.md`. |
| Post-MEU rows present (handoff, reflection, metrics) | n/a | No MEUs or execution plan exist; IDs were not invented. |

### Design Review (DR)

| Check | Result | Evidence |
|-------|--------|----------|
| Naming convention followed | pass | Required review path and `review-verdict.v1` primary artifact used. |
| Template version present | pass | `template_version: "2.1"`. |
| YAML frontmatter well-formed | pass | Required fields are present above. |

### Post-Implementation Review (PR)

| Check | Result | Evidence |
|-------|--------|----------|
| Evidence bundle complete | n/a | Read-only architecture review; product packages do not exist. |
| FAIL_TO_PASS table present | n/a | No implementation or tests were changed. |
| Commands independently runnable | n/a | No implementation validation was claimed. |
| Anti-placeholder scan clean | n/a | Out of scope for a docs-only architecture review. |

---

## Verdict

`changes_required` — The architecture is `sound-with-revisions`: retain the typed-job/pointer persistence, REST/MCP, auth, and distribution thesis, but resolve A1–A6 before `/session-grouping` or `/create-plan`. The full assessment, ranked Zorivest adoption table, inspiration fidelity table, and ordered planning actions are in `C:/Temp/av-kit/dispatch/build-plan-review-20260818/final.md`.

---

## Recheck (2026-08-18)

**Workflow**: `/planning-corrections` recheck  
**Agent**: `gpt-5.6-sol` (`high`)  
**Architecture**: `sound-with-revisions`

### Prior Pass Summary

| Finding | Prior Severity | Prior Status | Recheck Result | Current evidence |
|---------|----------------|--------------|----------------|------------------|
| A1 | High | open | **partial** | Spawn discovery and async renderer access now exist, but attach cannot authenticate with a spawn-only nonce and the generated MCP config pins the ephemeral port: `docs/build-plan/05-mcp-server.md:51-54`; `docs/build-plan/06-gui.md:52-59`; `docs/build-plan/06-gui.md:1006-1010`; `docs/build-plan/07-distribution.md:95-116`; `docs/build-plan/07-distribution.md:163-175`; `docs/build-plan/07-distribution.md:202-210`. |
| A2 | High | open | **partial** | Phase 1 now defines the ports and error module, and Phase 3 bans direct IO, but Phase 2 still says Phase 1 lacks `test_cookies`/`sabr_detected`, supplies a conflicting cookie-test signature, and asks implementation to add errors: `docs/build-plan/01-domain-layer.md:421-546`; `docs/build-plan/02-infrastructure.md:306-388`; `docs/build-plan/03-service-layer.md:50-60`; `docs/build-plan/03-service-layer.md:313-324`. |
| A3 | High | open | **fixed** | `apiFetch` reads text once, accepts 204/empty bodies, and decodes `ErrorEnvelope`: `docs/build-plan/06-gui.md:107-126`. |
| A4 | High | open | **fixed** | A bounded backend ring, authenticated console poll route, and owned-child stdout IPC are specified: `docs/build-plan/03-service-layer.md:365-376`; `docs/build-plan/04-rest-api.md:312-320`; `docs/build-plan/06-gui.md:302-329`. Sequence ownership remains a new R2 finding below. |
| A5 | High | open | **fixed** | Stop now commits the parent to `Cancelled`, leaves unfinished items `Pending`, clears runtime ownership, and requires requeue: `docs/build-plan/03-service-layer.md:75-80`; `docs/build-plan/03-service-layer.md:185-238`; `docs/build-plan/03-service-layer.md:424-437`. Start-selection behavior remains a new R2 finding below. |
| A6 | High | open | **fixed** | The preload now includes the required file/folder/clipboard/file-read methods and the BrowserWindow security contract: `docs/build-plan/06-gui.md:76-104`. The generic reader's access to `mcp-token.txt` is a new R2 finding below. |
| A7 | Medium | open | **fixed** | Session-only `ModelDownloadRuntime`, one-download ownership, REST polling, and per-row binding are explicit: `docs/build-plan/01-domain-layer.md:357-364`; `docs/build-plan/03-service-layer.md:330-344`; `docs/build-plan/04-rest-api.md:267-289`; `docs/build-plan/06-gui.md:825-836`. |
| A8 | Medium | open | **partial** | The registry, HelpCards, action index, and E2E waves now exist, but the action inventory is not complete or implementable end-to-end: `docs/build-plan/06-gui.md:277-300`; `docs/build-plan/06-gui.md:1079-1108`; `docs/build-plan/gui-actions-index.md:7-62`. See R2-7. |
| A9 | Medium | open | **fixed** | The probe order is setting → bundle → PATH in all owning phases, and `downloader.ffmpeg_path` is a Phase 6 key: `docs/build-plan/02-infrastructure.md:428-440`; `docs/build-plan/06-gui.md:961-969`; `docs/build-plan/07-distribution.md:135-149`. |
| A10 | Medium | open | **fixed** | Polling now uses the TanStack Query v5 callback over `query.state.data`, with no temporal-dead-zone reference: `docs/build-plan/06-gui.md:561-580`. |
| A11 | Low | open | **fixed** | Phase 1 makes `Setting.key` leaf-only: `docs/build-plan/01-domain-layer.md:367-377`. |
| A12 | Low | open | **partial** | The engine and downstream prose now say API request/worker concurrency and REST-only MCP, but the source-decision table still says “SQLite WAL for API + MCP”: `docs/build-plan/02-infrastructure.md:11-16`; `docs/build-plan/02-infrastructure.md:53-64`; `docs/build-plan/02-infrastructure.md:500-510`; `docs/build-plan/05-mcp-server.md:61-66`. |

### Confirmed Fixes

- A3, A4, A5, A6, A7, A9, A10, and A11 are closed at their original failure boundaries. Current evidence is in the disposition table above.
- `POST /transcripts/{id}/requeue`, `GET /models/download-runtime`, and `GET /health/console` are present in the authoritative REST index; MCP includes the first two and explicitly omits the GUI-only console route: `docs/build-plan/04-rest-api.md:325-374`; `docs/build-plan/05-mcp-server.md:71-81`; `docs/build-plan/05-mcp-server.md:136-187`.
- The health split is coherent: only liveness is unauthenticated; dependencies and console require Bearer auth: `docs/build-plan/04-rest-api.md:65-74`; `docs/build-plan/04-rest-api.md:312-321`; `docs/build-plan/07-distribution.md:119`.

### Remaining Findings

| ID | Severity | Finding | Current evidence | Required correction |
|----|----------|---------|------------------|---------------------|
| R2-1 | High | Attach has no usable GUI credential or independently verifiable identity. A backend is spawned with an ephemeral nonce, but an attaching Electron instance exposes only its own “spawn nonce”; the descriptor contains no credential and `instance_id` is only a self-asserted UUID in that file. Attach therefore yields 401 or trusts a descriptor it cannot authenticate. | `docs/build-plan/07-distribution.md:73-90`; `docs/build-plan/07-distribution.md:95-116`; `docs/build-plan/07-distribution.md:163-175` | Lock one workable model: Electron single-instance/reuse and refuse cross-process attach; or define a secure handoff/credential mechanism plus an independently checked process identity. Test fresh spawn, Electron crash + surviving backend, second launch, foreign/stale descriptor, and shutdown ownership. |
| R2-2 | High | “Copy MCP config” writes `AVKIT_API_BASE` from the current descriptor even though `--port 0` changes the port and the MCP client gives that environment override precedence over descriptor discovery. The default copied config becomes stale after restart and disables the corrected dynamic-discovery path. | `docs/build-plan/05-mcp-server.md:47-54`; `docs/build-plan/06-gui.md:1002-1010`; `docs/build-plan/07-distribution.md:198-210` | Default copied config must omit `AVKIT_API_BASE` and set only stable token/app-data discovery inputs. Offer endpoint pinning only as an explicit advanced override with a stale-pin error. |
| R2-3 | High | Transcript `start_processing` says it processes every non-Done parent, and the worker skips only `Done`/`Cancelled`. It therefore converts `Paused` to `Processing` without `resume` and reprocesses terminal `Failed` parents; if all items are terminal, the loop can compile and mark that failed parent `Done`. | `docs/build-plan/03-service-layer.md:185-194`; `docs/build-plan/03-service-layer.md:214-238`; `docs/build-plan/03-service-layer.md:380-392` | Define `start` eligibility (normally `Pending` only), `resume` eligibility (`Paused` only), and an explicit retry/reset path for `Failed`. Clear/request event lifecycle must be stated and tested through Stop → requeue → Start and Pause → Resume. |
| R2-4 | Medium | The console correction asks Electron to deduplicate REST and stdout events by `seq`, but it never says who allocates `seq` or guarantees that the same backend event carries the same sequence on both paths. Independent assignment makes dedup impossible or collision-prone. | `docs/build-plan/03-service-layer.md:365-376`; `docs/build-plan/06-gui.md:323-329` | Make the backend ring processor the sole allocator of monotonic process-local `seq`, emit that enriched event to both ring and stdout, and define restart/instance reset plus IPC-only event namespacing. |
| R2-5 | High | The generic sandbox bridge permits `.txt` reads anywhere under `{app_data}`. That directory contains `mcp-token.txt`, so renderer code can read the stable MCP Bearer, defeating the explicit separation from the ephemeral GUI nonce. The MCP copy card makes this path especially tempting. | `docs/build-plan/06-gui.md:76-104`; `docs/build-plan/06-gui.md:1002-1010`; `docs/build-plan/07-distribution.md:53-57`; `docs/build-plan/07-distribution.md:112-116` | Deny secret files in generic path APIs. Add a dedicated main-process “copy MCP config” operation that reads the token and writes the clipboard without returning the stable token to the renderer; expose only sanitized readiness data. |
| R2-6 | Medium | TTS file-load has two incompatible owners. Phase 1 says `FilesystemPort.read_text` owns constrained TTS file-load, but Phase 6 reads through Electron IPC and sends full `text`; the service flow receives both text and `source_path` without saying whether it re-reads. This permits duplicate/TOCTOU reads and inconsistent path validation. | `docs/build-plan/01-domain-layer.md:476-487`; `docs/build-plan/03-service-layer.md:302-324`; `docs/build-plan/04-rest-api.md:251-259`; `docs/build-plan/06-gui.md:814-820`; `docs/build-plan/06-gui.md:866-883` | Choose one owner. Recommended: Electron reads an explicitly selected file, REST sends the resulting text, `source_path` is metadata only, and backend services never re-read it. Remove the TTS claim from `FilesystemPort.read_text` or define a separately validated backend path flow. |
| R2-7 | Medium | The new GUI action canon is not complete or route-safe. `download:apply_quality_pending` points directly to a service method that has no REST route or Phase 6 control; transcript reorder is a visible action and REST route but has no action-index row; Phase 6 exposes TTS cancel in REST/index without an actual Cancel control; the FFmpeg override key has no corresponding Settings control in the rendered layout. | `docs/build-plan/gui-actions-index.md:7-62`; `docs/build-plan/03-service-layer.md:169-177`; `docs/build-plan/04-rest-api.md:325-374`; `docs/build-plan/06-gui.md:388-390`; `docs/build-plan/06-gui.md:651-724`; `docs/build-plan/06-gui.md:857-883`; `docs/build-plan/06-gui.md:887-1019` | Reconcile the index against every Phase 6 button. Add a REST action for apply-to-pending or remove/defer the GUI action; add missing reorder/browse rows and controls; add the TTS Cancel control; expose the FFmpeg override picker. Add a bidirectional inventory audit, not only a palette-yes audit. |
| R2-8 | Medium | Strict descriptor parsing is sound, but “invalid / extra keys → Spawn” is unsafe for schema evolution: an older Electron can reject a newer live descriptor and start a second backend against the same app-data/database. | `docs/build-plan/07-distribution.md:75-104` | On unsupported schema/extra keys, minimally inspect and verify liveness, then refuse with an upgrade/downgrade message; never spawn solely because a potentially live descriptor is newer. Add forward-version and unknown-key tests. |

### Verdict

`changes_required` — Architecture remains `sound-with-revisions`, but A1 and A2 are still blocking partials and R2-1, R2-2, R2-3, and R2-5 are new High-severity implementation failures. Correct those contracts and recheck again before `/session-grouping` or `/create-plan`.

---

## Recheck (2026-08-18 r3)

**Workflow**: `/plan-critical-review` recheck  
**Agent**: `gpt-5.6-sol` (`high`)  
**Architecture**: `sound-with-revisions`

### Intent Anchor

Executing the canonical Phase 0–7 specs should produce one secure local av-kit application whose Electron, REST, MCP, persistence, and GUI contracts are mutually implementable without inventing missing behavior. The round-3 text is closer, but two prior High surfaces remain materially unresolved.

### R2 Disposition

| Finding | Result | Current evidence |
|---------|--------|------------------|
| R2-1 | **partial** | The detailed contract now says no attach, second-instance focus/exit, fresh nonce after orphan reap, secret-free descriptor, and refuse for foreign/live-unknown descriptors (`docs/build-plan/07-distribution.md:79-107`, `docs/build-plan/07-distribution.md:166-177`). But the orphan-kill predicate still names `executable_path` and `app_data` fields from the descriptor without requiring an independent query of the live PID's image/command line or start identity; a stale descriptor plus PID reuse can therefore be classified as owned and killed. Phase 0 also still directs planners to a `backend.json attach/refuse` pattern (`docs/build-plan/00-overview.md:28-35`), contrary to the no-attach lock. |
| R2-2 | **fixed** | Default Copy MCP omits `AVKIT_API_BASE`; it copies only the stable token and app-data, while endpoint pinning is advanced and mismatch returns a stale-pin error (`docs/build-plan/06-gui.md:97-110`, `docs/build-plan/06-gui.md:1014-1023`, `docs/build-plan/07-distribution.md:201-220`). |
| R2-3 | **fixed** | Transcript start selects `Pending` only, resume selects `Paused` only, retry resets `Failed`, the worker never promotes any failed-item parent to Done, and boot rewrites `Processing` to `Pending` (`docs/build-plan/03-service-layer.md:186-203`, `docs/build-plan/03-service-layer.md:216-245`, `docs/build-plan/03-service-layer.md:435-451`). |
| R2-4 | **fixed** | `HealthService` owns the sole backend sequence counter and emits the same enriched JSON to ring/stdout; stdout-only events use the separate `ipc:{n}` namespace (`docs/build-plan/03-service-layer.md:372-387`, `docs/build-plan/06-gui.md:308-337`). |
| R2-5 | **fixed** | `readTextFile` is dialog-only and denies descriptor/database/token paths; `copyMcpConfig` performs token handling in main and returns `{ ok: true }` only (`docs/build-plan/06-gui.md:74-110`). |
| R2-6 | **partial** | Phase 1, service, REST, and GUI now make TTS `text` the body and `source_path` metadata (`docs/build-plan/01-domain-layer.md:476-487`, `docs/build-plan/03-service-layer.md:309-330`, `docs/build-plan/04-rest-api.md:239-257`, `docs/build-plan/06-gui.md:825-831`, `docs/build-plan/06-gui.md:877-895`). Phase 2 still says `FilesystemPort.read_text` owns "Compile + constrained file-load" (`docs/build-plan/02-infrastructure.md:451-463`), preserving the incompatible second owner. |
| R2-7 | **fixed** | Apply-defaults has service + REST + GUI control, transcript reorder/retry are indexed, TTS Cancel is on the generation bar, FFmpeg Browse is visible/indexed, and the audit is bidirectional (`docs/build-plan/03-service-layer.md:118-124`, `docs/build-plan/04-rest-api.md:165-189`, `docs/build-plan/06-gui.md:709-737`, `docs/build-plan/06-gui.md:794-798`, `docs/build-plan/06-gui.md:909-920`, `docs/build-plan/gui-actions-index.md:30-59`, `docs/build-plan/gui-actions-index.md:67-69`). |
| R2-8 | **fixed** | Unsupported/unknown descriptor plus live PID refuses and never spawns; dead PID permits overwrite (`docs/build-plan/07-distribution.md:98-107`). |

### Remaining Prior-Finding Disposition

| Finding | Result | Current evidence |
|---------|--------|------------------|
| A1 | **partial** | Dynamic discovery/no-attach is now defined, but safe orphan ownership is still not independently proven and Phase 0 retains contradictory attach guidance. Same evidence as R2-1. |
| A2 | **partial** | Phase 1 now owns the ports, `test_cookies`, `sabr_detected`, and most domain errors (`docs/build-plan/01-domain-layer.md:421-546`), and Phase 2 says it implements them. However, Phase 1's canonical error table omits `AgeRestrictedError`, while Phase 2 requires it and Phase 3 catches it (`docs/build-plan/01-domain-layer.md:530-546`, `docs/build-plan/02-infrastructure.md:306-315`, `docs/build-plan/03-service-layer.md:151-158`). Phase 2 also spells `SabrDetectedError` while Phase 1 defines `SABRDetectedError`. The Phase 1-first implementation order therefore still cannot compile the named adapter/service contract without inventing an error type. |
| A8 | **partial** | The registry, HelpCards, named R2-7 actions, and bidirectional audit rule exist. The index still omits explicit Phase 6 controls including the TTS output-directory picker and the Cookie File, Transcript Output Directory, and Models Directory Browse buttons (`docs/build-plan/06-gui.md:868-875`, `docs/build-plan/06-gui.md:909-940`, `docs/build-plan/gui-actions-index.md:55-69`). A generic `settings:save` row does not provide the missing IPC actions/testids required by the audit. |
| A12 | **fixed** | Both the source-decision table and engine rationale now describe WAL for FastAPI request + worker threads in the API process; MCP remains REST-only (`docs/build-plan/02-infrastructure.md:11-16`, `docs/build-plan/02-infrastructure.md:53-64`, `docs/build-plan/05-mcp-server.md:61-81`). |

### New Findings

| ID | Severity | Confidence | Finding | Current evidence | Required correction |
|----|----------|------------|---------|------------------|---------------------|
| R3-1 | Low | High | Transcript output nesting is stated two ways. Phase 1 makes `TranscriptJob.output_dir` the channel-folder root, and Phase 3 sets it to `{transcript.output_dir}/{slug(channel_name)}` before writing `raw/`; the GUI tree adds another `{channel_name}` below `{output_dir}`. | `docs/build-plan/01-domain-layer.md:232-260`; `docs/build-plan/03-service-layer.md:205-214`; `docs/build-plan/03-service-layer.md:247-253`; `docs/build-plan/06-gui.md:642-684` | Make the GUI tree start at `{output_dir}/raw`, `{output_dir}/compiled`, etc. This is clerical because Phases 1 and 3 already agree. |
| R3-2 | Low | High | TTS output-path default is both `~/Desktop` and `~/Documents` in the same canonical GUI spec. | `docs/build-plan/06-gui.md:868-875`; `docs/build-plan/06-gui.md:977-1006` | Choose one source-backed default and use it in both the generation-controls and settings-key tables. |

No new High or Critical finding was introduced. Named deferrals (Conversion GUI, OCR Part 1, SSE, multi-file TTS, MCP Guard) were excluded as instructed.

### Verdict

`changes_required` — `R2-1`/`A1` remain High at the destructive orphan-identity boundary, and prior High `A2` remains partial because the canonical Phase 1 error set still cannot satisfy Phases 2–3. `R2-6` and `A8` also remain partial but are not the blocking threshold; R3-1 and R3-2 are clerical Low corrections. Do not treat `docs/BUILD_PLAN.md:32` as current readiness to begin `/session-grouping` until the High contracts are corrected and independently rechecked.

---

## Recheck (2026-08-18 r4)

**Workflow**: `/plan-critical-review` recheck  
**Agent**: `gpt-5.6-sol` (`high`)  
**Architecture**: `sound`

### Intent Anchor

Executing the canonical Phase 0–7 specs should produce one secure local av-kit application whose Electron, REST, MCP, persistence, and GUI contracts are mutually implementable without inventing missing behavior. The current specs now close every prior High and every carried partial without introducing a new High or Critical defect.

### Disposition

| Finding | Result | Current evidence |
|---------|--------|------------------|
| A1 | **fixed** | Phase 0 now says independently verified orphan reap with no attach, and Phase 7 derives `ours.exe` from Electron `process.resourcesPath`, derives `ours.app_data` independently, requires live OS image/cmdline proof, and refuses on query failure or mismatch (`docs/build-plan/00-overview.md:28-35`; `docs/build-plan/07-distribution.md:96-124`). |
| A2 | **fixed** | Phase 1's canonical table includes `AgeRestrictedError`, `SABRDetectedError`, the `CookieAccessError` alias, `TranscriptsDisabledError`, and `NoTranscriptFoundError`; Phase 2 implements only those types and keeps `test_cookies` on `CookieTestResult` (`docs/build-plan/01-domain-layer.md:530-550`; `docs/build-plan/02-infrastructure.md:306-323`; `docs/build-plan/02-infrastructure.md:376-378`). |
| A8 | **fixed** | The four previously omitted visible actions now have explicit action-index rows tied to their Phase 6 controls: TTS output, cookie file, transcript directory, and models directory Browse (`docs/build-plan/06-gui.md:784-794`; `docs/build-plan/06-gui.md:867-874`; `docs/build-plan/06-gui.md:909-940`; `docs/build-plan/gui-actions-index.md:45-63`). |
| A12 | **fixed** | WAL is justified only by API request and worker threads in the same API process, while MCP is REST-only and never opens SQLite (`docs/build-plan/02-infrastructure.md:11-16`; `docs/build-plan/02-infrastructure.md:53-64`; `docs/build-plan/05-mcp-server.md:61-65`). |
| R2-1 | **fixed** | Owned-orphan termination requires the Electron single-instance lock plus live OS proof that `live.image == ours.exe` and the live command line's `--app-data` equals `ours.app_data`; descriptor values are consistency checks only, and query failure/PID mismatch refuses without SIGTERM (`docs/build-plan/07-distribution.md:96-124`; `docs/build-plan/06-gui.md:30-34`). |
| R2-2 | **fixed** | MCP resolves an unset endpoint through `backend.json`; default Copy MCP omits `AVKIT_API_BASE`, and explicit pinning has a stale-pin error (`docs/build-plan/05-mcp-server.md:47-57`; `docs/build-plan/06-gui.md:1013-1021`; `docs/build-plan/07-distribution.md:218-236`). |
| R2-3 | **fixed** | Transcript Start selects `Pending` only, Resume selects `Paused`, Retry resets `Failed`, the worker cannot promote a failed-item parent to Done, and boot recovery resets only `Processing` (`docs/build-plan/03-service-layer.md:186-203`; `docs/build-plan/03-service-layer.md:216-257`; `docs/build-plan/03-service-layer.md:435-451`). |
| R2-4 | **fixed** | `HealthService` is the sole process-local sequence allocator and emits the same enriched event to ring/stdout; stdout-only events use the separate `ipc:{n}` namespace (`docs/build-plan/03-service-layer.md:372-387`; `docs/build-plan/06-gui.md:329-337`). |
| R2-5 | **fixed** | The renderer cannot submit an arbitrary file path, secret files are denied across generic path APIs, and `copyMcpConfig` handles the token in main while returning only `{ ok: true }` (`docs/build-plan/06-gui.md:74-110`). |
| R2-6 | **fixed** | Phase 1 and Phase 2 constrain `FilesystemPort.read_text` to transcript compile only; TTS file-load is Electron IPC and `source_path` remains metadata that the service never re-reads (`docs/build-plan/01-domain-layer.md:476-487`; `docs/build-plan/02-infrastructure.md:451-463`; `docs/build-plan/03-service-layer.md:309-330`; `docs/build-plan/06-gui.md:824-830`; `docs/build-plan/06-gui.md:876-893`). |
| R2-7 | **fixed** | The service/REST/index/GUI surfaces remain reconciled for apply-defaults, transcript retry/reorder, TTS Cancel, FFmpeg Browse, and the bidirectional audit (`docs/build-plan/03-service-layer.md:100-124`; `docs/build-plan/04-rest-api.md:165-188`; `docs/build-plan/04-rest-api.md:206-223`; `docs/build-plan/06-gui.md:709-737`; `docs/build-plan/06-gui.md:793-798`; `docs/build-plan/gui-actions-index.md:15-73`). |
| R2-8 | **fixed** | Unsupported/unknown descriptors with a live PID refuse and never spawn or kill; only a dead PID permits overwrite, with forward-version coverage required (`docs/build-plan/07-distribution.md:115-124`). |
| R3-1 | **fixed** | The GUI tree now begins directly at `{TranscriptJob.output_dir}/raw|compiled`, matching the Phase 1 channel-root definition and Phase 3 writes (`docs/build-plan/01-domain-layer.md:232-260`; `docs/build-plan/03-service-layer.md:205-214`; `docs/build-plan/03-service-layer.md:247-269`; `docs/build-plan/06-gui.md:669-683`). |
| R3-2 | **fixed** | The rendered TTS control, generation table, and settings key all use `~/Documents` via `tts.output_path` (`docs/build-plan/06-gui.md:784-794`; `docs/build-plan/06-gui.md:867-874`; `docs/build-plan/06-gui.md:972-1005`). |

### New Findings

None. No `R4-*` finding is warranted. Named deferrals (Conversion GUI, OCR Part 1, SSE, multi-file TTS, MCP Guard) remain excluded as instructed.

### Verdict

`approved` — All prior High findings (`A1`/`R2-1`, `A2`, and later Highs R2-2, R2-3, R2-5) are fixed in current text, every carried Medium/Low partial is also fixed, and no new High or Critical finding was introduced. The BUILD_PLAN is ready for the next planning workflow.
