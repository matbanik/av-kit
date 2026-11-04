---
project: "2026-08-20-p6-gui-transcript"
date: "2026-08-20"
source: "docs/build-plan/06-gui.md"
meus: ["MEU-21"]
status: "draft"
template_version: "2.0"
---

# Implementation Plan: Phase 6 GUI Transcript

> **Project**: `2026-08-20-p6-gui-transcript`
> **Build Plan Section(s)**: [06-gui.md](../../../build-plan/06-gui.md) §Transcript Page (`/transcript`)
> **Status**: `draft`
> **Grouping**: [2026-08-18-build-plan-session-grouping.md](../../../../.agent/context/grouping/2026-08-18-build-plan-session-grouping.md) Session 9 — MEU-21 only

---

## Goal

Replace the `/transcript` `LazyPlaceholder` with the Transcript page: channel URL add, persisted queue **cards** (not a table), processor Start/Pause/Resume/Stop, card reorder/remove/requeue/retry/compile, and an output tree rooted at `{TranscriptJob.output_dir}/raw|compiled` (R3-1). Poll `GET /transcripts` as `{ items, processor }` the same way as downloads. Do not rewrite FastAPI routers or MCP tools. Do not start MEU-22–25. Do not invent MEU IDs. Do not rewind MEU-26 chrome.

---

## Context Tool Decision

```yaml
context_tool_decision:
  phase: planning_and_execution
  eligible_tools: []
  decision: not_applicable
  eligibility_basis: "graphify-out/graph.json and graphify-out-research/graph.json are absent (Glob 0). Headroom has no approved disposition. Planning and execution use file reads + P0 exact-evidence receipts (bypass class)."
  human_message_reference: null
```

Re-evaluate before Step 6. If graphs remain absent and Headroom still has no approved disposition, reuse this record.

---

## Handoff Set

| Scope | Canonical handoff |
|---|---|
| MEU-21 | `.agent/context/handoffs/2026-08-20-p6-gui-transcript-MEU-21-handoff.md` |

Rolling implementation review: `.agent/context/handoffs/2026-08-20-p6-gui-transcript-implementation-critical-review.md`.

The product glob owner is named set `HANDOFF_GLOB`. Expected count is named set `HANDOFF_COUNT`.

---

## Work Packages and Context Lifecycle

`fresh_worker: none` → every non-`shared` row is `compact_continue`. Never emit `isolated`.

| ID | Work | depends_on | context_strategy | durable_outputs |
|---|---|---|---|---|
| WP-21a | MEU-21 Red: AC-21.1–21.22 UI tests **before** `TranscriptPage` production (`RED_TEST_TITLE` + `RED_AC_IDS` + `RED_JSON`). Receipt must pass `RED_ORACLE_CHECK` (kind `ui`) — 22 distinct failed JSON tests, not a stuffed title. | — | `compact_continue` | `C:/Temp/av-kit/fail-to-pass-meu-21-ui.txt`; `RED_JSON` |
| WP-21b | Green: `TRANSCRIPT_HOME` + Query hook + cards + `OUTPUT_TREE` + `ENABLED_WHEN` + `PALETTE_DELIVER` (`AppShell` + `TRANSCRIPT_COMMANDS`). Do not neutralize tests. Do not edit FastAPI/MCP. Do not import TTS page. | WP-21a | `compact_continue` | `ui/src/renderer/src/features/transcript/`; `AppShell.tsx`; compact then re-read `task.md` |
| WP-21c | Wave 2 E2E **written and wired** (`E2E_WAVE2` + `E2E_CASES` + `E2E_PER_CONTROL` + `E2E_ACTUATE` + `E2E_ATTACHED_FIRST` + `E2E_CONTROL_CENSUS` + `E2E_SEAM_GATE` + `E2E_SEAM_PROOF`). Isolated `AVKIT_APP_DATA`. Honor `E2E_NO_LIVE_YT` via `E2E_SEAM` + `E2E_HAPPY_PATH`. Run or `[B]` `E2E_SANDBOX`. | WP-21b | `compact_continue` | `ui/tests/e2e/transcript-queue.test.ts`; `C:/Temp/av-kit/e2e-wave2.txt` |
| WP-21d | `MEU_SCOPED_GATE` after `HANDOFF_SOURCE_READ`, then canonical handoff | WP-21c | `compact_continue` | `.agent/context/handoffs/2026-08-20-p6-gui-transcript-MEU-21-handoff.md` |
| WP-21e | Hub + SSOT: bind MEU-21; keep prior phase-6 slashes; `HUB_NEXT_AFTER`. Grouping Session 9 → complete is **H2 after exec `approved`**, not this row. | WP-21d | `shared` | `.agent/context/meu-status.yaml`; `docs/BUILD_PLAN.md` |

---

## User Review Required

None that block planning. Sourced conflicts are locked below (reviewer confirms; do not invent a third behavior):

1. **Harness gate:** `create-plan.md` §5c Cursor-default `plan_to_exec_gate=human` vs `.agent/context/harness.local.md` `reviewer-auto`. **Override wins.** After Codex `approved`, auto-continue to execution.
2. **Cards vs table:** Spec 599–641 is a **card** queue. Downloader's TanStack table is not reused. **Lock `CARD_QUEUE`.**
3. **Paused is a job status:** `TranscriptStatus` includes `Paused` (`enums.py` 21–29). Downloader forbids item `Paused`. **Lock `JOB_STATUSES` includes Paused.** Processor `Paused` still drives Resume.
4. **Stop, not Cancel:** Spec 636–637 / index `transcript:stop` → `POST /transcripts/stop` (parent → Cancelled). **Lock `STOP_VERB`.** Do not ship a `cancel-btn` on this page.
5. **Live extract on Add:** `TranscriptService.add_channel` calls `extract_info` before persist (`transcript.py` 121–186). Wave 2 must not reach that path. **Lock `E2E_SEAM`** (renderer `fetch` override + `E2E_SEAM_GATE` + fail-closed `E2E_SEAM_UNHANDLED`). Do not treat Playwright `page.route` as proof (downloader RULE-2).
6. **Batch N/M omitted:** Spec 656 says batch progress is optional on `GET /transcripts/{id}` if present. `TranscriptJobOut` has no batch fields (`schemas/transcripts.py` 22–39). **Lock `BATCH_OMIT`.** Do not invent a second store. Rate + ETA use `RATE_ETA`.
7. **Remove confirm:** Spec 718 “Confirmation dialog; does not delete files.” G20 requires a themed portaled modal, not `window.confirm`. **Lock `IN_PAGE_CONFIRM`.**
8. **Output tree root:** R3-1 / Spec 674–684 — tree starts at `{output_dir}/raw` and `{output_dir}/compiled`, not a nested `{channel_name}` under that root. **Lock `OUTPUT_TREE`.**
9. **4A indexes:** `docs/gui-element-reference.md`, `docs/gui-button-index.md`, `.agent/docs/gui-standards-enforcement.md` remain **absent**. Apply `06-gui.md` + G30–G35 + `gui-actions-index.md`.
10. **Settings leaves:** Rate/ETA **read** `GET /settings/transcript`. Browse / write of `transcript.output_dir` stays MEU-23 (`settings:browse_transcript_dir`).

**This section is content for the review loop, NOT a cue to stop now.**

---

## Named sets (PR-9 — define once)

| Name | Value | Owner |
|------|-------|-------|
| `TRANSCRIPT_HOME` | route `/transcript` component is `TranscriptPage` (not `LazyPlaceholder` / `ModuleSkeleton`). `nav:transcript` hashes to `/transcript`. | Spec 189–192, 264, 595 |
| `PAGE_FILES` | `ui/src/renderer/src/features/transcript/{TranscriptPage,ChannelCard,ChannelQueue,useTranscriptQueue,transcript-controls,transcript-commands,output-tree,rate-eta}.tsx?ts` + `ui/src/renderer/src/router.tsx` + `ui/src/renderer/src/registry/commandRegistry.ts` + `ui/src/renderer/src/components/layout/AppShell.tsx` | this plan |
| `CARD_QUEUE` | queue is a list of `channel-card` nodes bound to `items[]`; not `queue-table` / TanStack | Spec 611–633 |
| `CHANNEL_URL_HINT` | visible helper text listing `/@handle`, `/c/name`, `/channel/UCxxx`, `/user/name` | Spec 608, 668 |
| `CREATE_BODY` | `{ channel_url: string.min(1) }` only | `TranscriptCreateIn`; extra forbid |
| `LIST_ENVELOPE` | `{ items, processor }` — never a bare array | Spec 725, 737, 1147 |
| `PROCESSOR_STATES` | `Idle` \| `Processing` \| `Paused` | Spec 737; p4 |
| `JOB_STATUSES` | `Pending`, `Processing`, `Paused`, `Done`, `Failed`, `Cancelled` | `TranscriptStatus`; Spec 650 |
| `ITEM_STATUSES` | `Pending`, `Done`, `Skipped`, `Failed` | `TranscriptItemStatus` |
| `POLL_ACTIVE_MS` | `1000` when `processor.state === 'Processing'` | Spec 737; MEU-20 cadence |
| `POLL_IDLE_MS` | `5000` otherwise (including no data yet) | Spec 737; MEU-20 cadence |
| `QUERY_KEY` | `['transcripts']` | this plan; Spec 737 “same way as downloads” |
| `CARD_FIELDS` | `{ channel_name, status, video_count, transcripts_done, word_count, output_dir, last_title, last_item_status }` — never `video_ids` / `processed_ids` / `progress.json` | Spec 647–659, 1149 |
| `OUTPUT_TREE` | card tree labels `{output_dir}/raw` and `{output_dir}/compiled` (R3-1). Open Folder IPC target is `output_dir`. | Spec 674–684; grouping R3-1 |
| `RATE_ETA` | Rate text `1 req/{delay}s` from `GET /settings/transcript` leaf `delay_between_requests`. ETA seconds = `max(0, video_count - transcripts_done) * delay`. Missing/non-finite delay → hide rate+eta (fail closed). | Spec 655, 657; settings GET |
| `BATCH_OMIT` | do not render “Batch N/M”; `TranscriptJobOut` has no batch fields | Spec 656; schemas/transcripts.py 22–39 |
| `REORDER_BODY` | `{ job_ids: string[] }` permutation of current queue ids | `TranscriptReorderIn` |
| `ENABLED_WHEN` | Start: pending-or-paused jobs ∧ state ≠ Processing; Pause: Processing; Resume: Paused; Stop: Processing ∨ Paused; Up: selected ∧ not first; Down: selected ∧ not last; Remove: selected; Requeue: selected ∧ status Cancelled; Retry: selected ∧ status Failed; Compile: selected ∧ `transcripts_done > 0`; View Compiled: selected ∧ compiled path known; Open ZIP: selected ∧ `zip_path` non-null; Open Folder: selected ∧ `output_dir` non-empty | Spec 711–737; index 32–44 |
| `VOID_204` | `DELETE /transcripts/{id}` → `apiFetch<void>` | transcripts.py 141–145 |
| `ACCEPTED_202` | start/pause/resume/stop → 202 empty; start while Processing → 409 `ERROR_ENVELOPE`; duplicate `channel_url` → 409 | transcripts.py 77–118; transcript.py 128, 191 |
| `STOP_VERB` | control id `stop-btn` / action `transcript:stop`. Page has no `cancel-btn`. | Spec 637; index 36 |
| `IN_PAGE_CONFIRM` | G20 full contract: `createPortal(..., document.body)`; theme tokens `--color-bg-elevated` / `--color-fg` / `--color-border`; Confirm `remove-confirm-btn` + Cancel `remove-confirm-cancel`; backdrop click and Escape dismiss with DELETE count 0; Confirm → exactly one `DELETE /transcripts/{id}`; files stay. No `window.confirm` / `alert` / `prompt`. | Spec 718; G20 |
| `TRANSCRIPT_PALETTE_IDS` | `{transcript:add, transcript:start, transcript:pause, transcript:resume, transcript:stop}` | `gui-actions-index.md` 32–36 |
| `TRANSCRIPT_LOCAL_IDS` | `{transcript:requeue, transcript:retry, transcript:reorder, transcript:compile, transcript:remove, transcript:open_compiled, transcript:open_zip, transcript:open_folder}` | index 37–44 |
| `TRANSCRIPT_EVENTS` | `av-kit:transcript:{add,start,pause,resume,stop}` dispatched from palette and page buttons; **no** `apiFetch` in `commandRegistry` | G11 |
| `TRANSCRIPT_COMMANDS` | `ui/src/renderer/src/features/transcript/transcript-commands.ts` — the single handler set for `TRANSCRIPT_PALETTE_IDS` | G11 |
| `PALETTE_DELIVER` | `AppShell` always-mounted listener is the production owner. It calls `TRANSCRIPT_COMMANDS`. Off `/transcript`: navigate `#/transcript` then invoke the same handler. `transcript:add` focuses `channel-input` (no POST). Page buttons call the same exports. Negative: listener only inside `TranscriptPage` → off-route no-op. | G11; MEU-20 pattern |
| `WAVE2_TESTIDS` | `transcript-page`, `channel-input`, `channel-card`, `compile-btn`, `channel-progress` | Spec 1103 |
| `WAVE2_EXTRA_TESTIDS` | `add-btn`, `start-btn`, `pause-btn`, `resume-btn`, `stop-btn`, `up-btn`, `down-btn`, `remove-btn`, `requeue-btn`, `retry-btn`, `view-compiled-btn`, `open-zip-btn`, `open-folder-btn`, `processor-indicator`, `output-tree`, `rate-display`, `eta-display`, `last-title`, `channel-url-hint`, `remove-confirm-btn`, `remove-confirm-cancel` | E2; §4A |
| `E2E_WAVE2` | `ui/tests/e2e/transcript-queue.test.ts` (`E2E_CASES`, 6 tests) + `WAVE2_TESTIDS` / `WAVE2_EXTRA_TESTIDS` in `test-ids.ts` | Spec 1103; E2 |
| `E2E_CASES` | `W2-1` `TRANSCRIPT_HOME`; `W2-2` nav from `#/` ; `W2-3` page-chrome EXTRA presence (`toBeVisible` on input/hint/add/toolbar; `E2E_ATTACHED_FIRST` on Idle `processor-indicator`; no per-card nodes required); `W2-4` `E2E_HAPPY_PATH` via `E2E_SEAM` + `E2E_SEAM_PROOF` plus card-level visibles; `W2-5` `E2E_ACTUATE` + `IN_PAGE_CONFIRM` + Processing `processor-indicator` `toBeVisible`; `W2-6` `PALETTE_DELIVER` off-route `transcript:add` | Spec 1103; E2; G11; G20 |
| `E2E_LOCATOR_FORM` | Wave 2 locators are literal `getByTestId('<kebab-id>')` (single quotes). Comments and `test-ids.ts` literals do not satisfy `E2E_CONTROL_CENSUS`. | E2 |
| `E2E_PER_CONTROL` | The allowed method must be chained on the same locator expression: `expect(page.getByTestId('id')).toBeVisible()` or `page.getByTestId('id').click()`. Owner: `Test-HasBound`. | E2; MEU-20 R4-1 |
| `E2E_ATTACHED_FIRST` | Playwright `toBeHidden` passes when the locator matches **no DOM node**. Before any intentional hidden-state assertion, require `toBeAttached` or `toHaveCount(1)`. Presence oracles for required controls are `toBeVisible` / `toBeAttached` / `toHaveCount(1)`, never `toBeHidden` alone. | E2; [Playwright `toBeHidden`](https://playwright.dev/docs/api/class-locatorassertions#locator-assertions-to-be-hidden) |
| `E2E_SEAM_GATE` | `window.__e2eSeamInstalled === true` set in the pre-app `addInitScript` **before** any Transcript `apiFetch`. Live `resolveBackend` (`api.ts` 21–27) skips `getBackendUrl`/`getToken` IPC only when this flag is true. Without it the fetch override is unreachable (IPC hang or live backend). | Local Canon: `api.ts` 21–27; downloader RULE-2; `download-queue.test.ts` 145–158 |
| `E2E_SEAM_LEDGER` | `window.__e2eCalls` — `{ url, method, bodyKeys }` appended on every intercepted `fetch` | downloader RULE-2 |
| `E2E_IPC_LEDGER` | `window.__e2eIpc` — `{ channel, target }` appended on `openPath` / `showItemInFolder` stubs | MEU-19 IPC |
| `E2E_SEAM_UNHANDLED` | HTTP 599 JSON/text body `E2E_SEAM_UNHANDLED` for any `/transcripts*` or `/settings/transcript*` request the override does not explicitly fulfill. Must not call original `fetch` for those prefixes. | downloader RULE-2; `transcript.py` 121–186 |
| `E2E_SEAM` | Production-effective renderer seam: `page.addInitScript` sets `E2E_SEAM_GATE` and installs a `window.fetch` override **before** app load, then `page.reload()`. Fulfills GET `/transcripts` as `LIST_ENVELOPE`; POST `/transcripts` after asserting `CREATE_BODY` keys then `TranscriptJobOut`; start/pause/resume/stop 202; reorder 202; DELETE 204; compile/requeue/retry fixtures; GET `/settings/transcript` delay leaf. Records `E2E_SEAM_LEDGER`. Fail-closed via `E2E_SEAM_UNHANDLED`. Happy-path card id/title equals the POST fulfill payload. `page.route` is optional and is **not** the proof. Fixtures under `ui/tests/e2e/fixtures/`. | Local Canon: `transcript.py` 121–186; `api.ts` 21–27; downloader RULE-2; [Playwright `addInitScript`](https://playwright.dev/docs/api/class-page#page-add-init-script) |
| `E2E_SEAM_PROOF` | Helper (not `page.route`) requires W2-4 source to contain `addInitScript`, `__e2eSeamInstalled`, `__e2eCalls`, `E2E_SEAM_UNHANDLED`, `channel_url`, and `reload`. Card must be asserted from the seam payload (`toContainText` or matching `e2e-` id). | E2; downloader RULE-2; `api.ts` 21–27 |
| `E2E_ACTUATE` | W2-5 clicks each interactive control and asserts the production observable: Start→`POST /transcripts/start`; Pause→`POST /transcripts/pause`; Resume→`POST /transcripts/resume`; Stop→`POST /transcripts/stop`; Up/Down→`PUT /transcripts/reorder`; Compile→`POST /transcripts/{id}/compile`; View Compiled→`E2E_IPC_LEDGER` compiled path; Open ZIP→zip path; Open Folder→`output_dir`; Remove→both confirm buttons `toBeVisible`; Cancel/backdrop/Escape→DELETE count 0; Confirm→exactly one DELETE; Requeue (Cancelled fixture) `toBeVisible`+click→POST requeue; Retry (Failed fixture) `toBeVisible`+click→POST retry; Processing fixture → `processor-indicator` `toBeVisible`. | E2; create-plan §4A.3 |
| `E2E_HAPPY_PATH` | with `E2E_SEAM` active: fill `channel-input` → Add click → `channel-card` visible and traceable to the seam POST payload. URL may be `https://www.youtube.com/@e2e-invalid` because extract never runs. | Spec 668, 1129–1135 |
| `E2E_NO_LIVE_YT` | Wave 2 must not let Add/Start/Resume/Stop reach yt-dlp extract. Enforced by `E2E_SEAM` + `E2E_SEAM_GATE` + `E2E_SEAM_PROOF`, not by `page.route`. | Local Canon `transcript.py` 121–186; `api.ts` 21–27; downloader RULE-2 |
| `E2E_CONTROL_CENSUS` | `rtk proxy pwsh -NoProfile -File docs/execution/plans/2026-08-20-p6-gui-transcript/assert-e2e-control-census.ps1` — comment-stripped `E2E_LOCATOR_FORM` + `E2E_PER_CONTROL` + `E2E_SEAM_PROOF` + `E2E_SEAM_GATE` + `E2E_ACTUATE` + `E2E_ATTACHED_FIRST`. Empty/skip tests fail. Helper rejects the R4-1 unrelated-receiver snippet. `toBeHidden` is not a presence oracle. | E2; create-plan §4A.3 |
| `RED_AC_IDS` | `AC-21.1` … `AC-21.22` (22). Owner: `assert-red-oracle.ps1` ui kind + `RED_JSON`. | FIC |
| `RED_TEST_TITLE` | every AC-21.N unit/integration test is a **distinct** Vitest case whose `fullName`/`title` contains exactly one `AC-21.N`. | FIC tests-first |
| `RED_JSON` | `C:/Temp/av-kit/fail-to-pass-meu-21-ui.json` from Vitest 3 `--reporter=json --outputFile`. | Vitest 3 json reporter |
| `BUILDER_PIN` | `—` while `fresh_worker: none`. | harness.local.md |
| `GROUPING_FILE` | `.agent/context/grouping/2026-08-18-build-plan-session-grouping.md` | grouping authority |
| `GROUPING_DONE_MARK` | Progress-table row `\| 9 \| \`p6-gui-transcript\` \| ✅ complete \|` and Session 9 heading `✅ complete`; Sessions 10–12 stay `⬜ pending`. Applied at H2 after exec `approved` only. | grouping Progress |
| `REFLECTION_TEMPLATE` | `docs/execution/reflections/TEMPLATE.md` | closeout |
| `REFLECTION_SCHEMA` | `.agent/schemas/reflection.v1.yaml` | closeout |
| `REFLECTION_PEER_RULE` | newest `docs/execution/reflections/*-reflection.md` excluding `TEMPLATE.md`, sorted by `LastWriteTime` descending | AGENTS closeout |
| `REFLECTION_SOURCE_READ` | `C:/Temp/av-kit/reflection-source-read-meu-21.txt` with `TEMPLATE=`, `SCHEMA=`, `PEER=`, `PASS: REFLECTION_SOURCE_READ` | H2-1 |
| `E2E_SANDBOX` | un-run E2E in agent sandbox → `[B]` + CI follow-up. Tests stay written and wired. Isolated `AVKIT_APP_DATA` (chrome RULE-1). | known-issue policy; chrome RULE-1 |
| `RENDER_ALL_ITEMS` | cards = `data.items` (no invented page/search API) | Spec 661–668; G4 no list params |
| `STATUS_COLORS` | map `JOB_STATUSES` + processor to CSS `@theme` tokens (no raw hex in `className`) | Spec 650; G31–G32 |
| `ERROR_SURFACE` | 422/409/`ApiError` shown in-page (G15); never swallow | G15 |
| `REGRESSION_TESTS` | p6-gui-downloader H1-2 Python set (do not drop) | p6 carry-forward |
| `SCAN_G36_ARGS` | skip/only/todo markers under `ui/tests/unit` + `ui/tests/e2e` + `tests/` | G36 |
| `SCAN_PLACEHOLDER_ARGS` | `TODO`, `FIXME`, `NotImplementedError` under `ui/src` | anti-placeholder |
| `HANDOFF_COUNT` | `1` | `HANDOFF_GLOB` |
| `HANDOFF_GLOB` | `.agent/context/handoffs/2026-08-20-p6-gui-transcript-MEU-21-handoff.md` | this plan |
| `PLAN_FOLDER` | `docs/execution/plans/2026-08-20-p6-gui-transcript` | MEU `execution_plan` |
| `PLAN_FOLDER_SLASH` | `docs/execution/plans/2026-08-20-p6-gui-transcript/` | phase `"6"` |
| `PRIOR_PLAN_SLASHES` | `docs/execution/plans/2026-08-19-p6-gui-shell/`; `docs/execution/plans/2026-08-20-p6-gui-downloader/`; `docs/execution/plans/2026-08-20-p6-gui-zorivest-chrome/` | must remain on phase `"6"` |
| `HUB_NEXT_AFTER` | `/create-plan p6-gui-tts-models` | grouping pathway #10 |
| `HUB_NEXT_FIELD` | the unique `Next: \`...\`` field in `docs/BUILD_PLAN.md` | p6 pattern |
| `EXEC_REVIEW_FILE` | `.agent/context/handoffs/2026-08-20-p6-gui-transcript-implementation-critical-review.md` | this plan |
| `EXEC_REVIEW_TARGET` | `docs/execution/plans/2026-08-20-p6-gui-transcript/implementation-plan.md` | exact `target_plan` |
| `EXEC_REVIEW_MAX_ROUND` | `6` | execution-review cap |
| `CHECK_EXEC_REVIEW` | `tools/check_exec_review.py` — first YAML frontmatter only; `--expected-mode implementation` | p2 Human-approved |
| `HANDOFF_TEMPLATE` | `.agent/context/handoffs/TEMPLATE.md` | closeout |
| `HANDOFF_SOURCE_READ` | `C:/Temp/av-kit/handoff-source-read-meu-21.txt` written **once** before the MEU-21 handoff | p4 F4 |
| `HANDOFF_BUNDLE_MARKERS` | `Acceptance Criteria`, `CACHE BOUNDARY`, `FAIL_TO_PASS`, `Changed Files`, `Quality Gate Results`, `Commands Executed`, `## Evidence` | TEMPLATE |
| `VITEST_ALLOW_ONLY` | `ui/vitest.config.ts` has `test.allowOnly: false`. Every `npx vitest run` passes `--allowOnly=false`. | G36 |
| `UI_ESLINT` | `npx eslint src/ tests/ --max-warnings 0` | G36 |
| `RED_ORACLE` | UI FAIL_TO_PASS text has allow-marker and no deny-marker **and** `RED_JSON` maps 22 distinct failed `assertionResults` 1:1 onto `RED_AC_IDS`. | MEU-20 r2 |
| `RED_ORACLE_CHECK` | `rtk proxy pwsh -NoProfile -File docs/execution/plans/2026-08-20-p6-gui-transcript/assert-red-oracle.ps1 -Kind ui -Receipt <text> -JsonReceipt RED_JSON` | PR-9 |
| `HANDOFF_MARKER_CHECK` | `rtk proxy pwsh -NoProfile -File docs/execution/plans/2026-08-20-p6-gui-transcript/assert-handoff-markers.ps1` | PR-9 |
| `REFLECTION_MARKERS` | `Friction Log`, `Execution Trace`, `Pattern Extraction`, `Patterns to KEEP`, `Next Session Design Rules`, `RULE-`, `Efficiency Metrics`, `Rule Adherence`, `Instruction Coverage`, `schema: v1`, `sections:`, `loaded:`, `decisive_rules:` | p6 |
| `MEU21_TOUCHED` | `PAGE_FILES` + `ui/tests/unit` transcript + `ui/tests/e2e/transcript-queue.test.ts` + `test-ids.ts` + `AppShell.tsx` + `commandRegistry.ts` + `router.tsx` | MEU-21 files |
| `MEU_SCOPED_GATE` | `ui`: `npx tsc --noEmit` + `npx vitest run --allowOnly=false` + `UI_ESLINT` + `npm run build`; + `SCAN_PLACEHOLDER` + `SCAN_G36` + `HANDOFF_MARKER_CHECK` + AC-21.* | AGENTS MEU gate |
| `OPENAPI_CHECK` | `packages/api/` is **not** modified → `--check` still run as no-drift proof. `-o` forbidden unless FAIL. | G8 skip-with-proof |
| `CHROME_RULES` | RULE-1 `AVKIT_APP_DATA` userData isolation; RULE-2 closed console must not hide `main`; RULE-3 reactive breadcrumb. Consume; do not rewind chrome. | p6-gui-zorivest-chrome reflection |

---

## G29 wiring checklist

| Layer | Ready? | Evidence |
|-------|--------|----------|
| Domain / TranscriptService / FastAPI transcript routes | YES | MEU-11 + MEU-16 `approved`. Do not rewrite. |
| `{ items, processor }` + start/pause/resume/stop + compile/requeue/retry | YES | `transcripts.py` |
| `apiFetch` + IPC + AppShell + chrome | YES | MEU-19/20/26 `approved` |
| Transcript page at `/transcript` | NO → **this MEU** | grouping Session 9 |
| TTS / Settings leaf writes | NO — **later MEUs** | grouping 10–11 |
| MCP tools | YES — do not rewrite | MEU-17/18 `approved` |

---

## create-plan §4A — GUI Element Compliance

**Triggered:** Transcript page creates `<button>`, `<input>`, status badges, and output tree in `ui/src/renderer/`.

| Check | Result |
|-------|--------|
| `docs/gui-element-reference.md` | **Absent** — G31–G35 + Spec tokens |
| Button/input/output indexes | **Absent** — map via table below |
| E2E written+wired | `E2E_WAVE2` + `E2E_CASES` + `E2E_PER_CONTROL` + `E2E_ACTUATE` + `E2E_ATTACHED_FIRST` + `E2E_SEAM_GATE` + `E2E_SEAM_PROOF` + `E2E_CONTROL_CENSUS` |
| G30–G35 / E2 | No new `<select>` (G30 n/a). G31 `bg-accent` only. G32 no raw hex in `className`. G33 duration tokens. G34 variants below. G35 tiers below. E2 = `E2E_WAVE2`. |
| G20 | `IN_PAGE_CONFIRM` — portal to `document.body`, theme tokens, Confirm/Cancel, backdrop + Escape, no `window.confirm` |
| G11 | `PALETTE_DELIVER`: `AppShell` owns reachability; `TRANSCRIPT_COMMANDS` is the one fetch path |
| G16 | existing `CSP_IMG` — do not regress |
| G5 | `POLL_ACTIVE_MS` / `POLL_IDLE_MS` |
| G3 | no client-side search of thousands; queue is `RENDER_ALL_ITEMS` |
| G27 | not used; `openPath` already allowlisted (MEU-19) |

Indexes remain absent. **Local fallback basis:** G34 text in `emerging-standards.md` (5 variants × 3 sizes). Toolbar `md`; card actions `sm`. G35 tiers T0–T1.

| Element | Variant | Size | States | testid | Feedback |
|---------|---------|------|--------|--------|----------|
| Channel URL | text | md | default/focus/disabled | `channel-input` | T0 |
| URL hint | output | — | default | `channel-url-hint` | T0 |
| Add | primary | md | default/hover/focus/disabled/loading | `add-btn` | T1 POST create |
| Channel card | output | — | default/selected | `channel-card` | T1 poll |
| Progress bar | output | — | hidden when `video_count===0` | `channel-progress` | T1 |
| Output tree | output | — | default | `output-tree` | T0 |
| Rate / ETA / last title | output | — | hidden when `RATE_ETA` fail-closed / no last | `rate-display`, `eta-display`, `last-title` | T1 |
| Start | primary | md | default/hover/focus/disabled | `start-btn` | T1 202/409 |
| Pause | secondary | md | default/hover/focus/disabled | `pause-btn` | T1 202 |
| Resume | secondary | md | default/hover/focus/disabled | `resume-btn` | T1 202 |
| Stop | secondary | md | default/hover/focus/disabled | `stop-btn` | T1 202 |
| Up / Down | secondary | sm | default/hover/focus/disabled | `up-btn`, `down-btn` | T1 PUT reorder |
| Requeue | secondary | sm | hidden unless Cancelled | `requeue-btn` | T1 POST |
| Retry | secondary | sm | hidden unless Failed | `retry-btn` | T1 POST |
| Compile | secondary | sm | default/hover/focus/disabled | `compile-btn` | T1 POST compile |
| View Compiled | ghost | sm | default/hover/focus/disabled | `view-compiled-btn` | T1 IPC |
| Open ZIP | ghost | sm | default/hover/focus/disabled | `open-zip-btn` | T1 IPC |
| Open Folder | ghost | sm | default/hover/focus/disabled | `open-folder-btn` | T1 IPC |
| Remove | destructive | sm | default/hover/focus/disabled | `remove-btn` | T1 opens confirm |
| Confirm remove | destructive | sm | default/hover/focus | `remove-confirm-btn` | T1 204 |
| Cancel remove | outline | sm | default/hover/focus | `remove-confirm-cancel` | T0 |
| Processor indicator | status | — | hidden when Idle | `processor-indicator` | T1 |

---

## MEU-21 — `gui-transcript`

### Boundary Inventory

| Surface | Schema Owner | Field Constraints | Extra-Field Policy | Invalid-input | Create/Update parity | Source |
|---------|-------------|-------------------|--------------------|---------------|----------------------|--------|
| Channel Add form → REST | client Zod `.strict()` `CREATE_BODY` then Pydantic `TranscriptCreateIn` | `channel_url` min 1 | extra forbid (client + server) | no POST if blank; 422 `ERROR_SURFACE`; duplicate URL 409 | n/a (create only) | Spec 724; 04 transcripts |
| Queue poll | response `TranscriptListOut` | must have `items` + `processor` | ignore unknown out fields; never treat as array | `ERROR_SURFACE` | GET only | Spec 725, 737 |
| Detail GET | `TranscriptJobOut` | aggregates only; no transcript text | ignore unknown | 404/422 `ERROR_SURFACE` | GET only | Spec 726 |
| Reorder | Zod `.strict()` `REORDER_BODY` | permutation of current ids | extra forbid | 422 | n/a | Spec 728 |
| Processor POSTs | `EmptyIn` / no body | no extra keys | extra forbid | 422; start-while-Processing 409 | n/a | transcripts.py 77–118 |
| Requeue / retry / compile | `EmptyIn` | id in path | extra forbid | 422; wrong-status transition → domain error `ERROR_SURFACE` | n/a | Spec 733–735 |
| Remove | no body | 204 void | n/a | 404 `ERROR_SURFACE` | n/a | Spec 727 |
| Settings read (rate) | `GET /settings/transcript` | leaf map | ignore unknown leaves | missing delay → `RATE_ETA` hide | read-only this MEU | lock 10 |
| Open compiled/zip/folder | existing IPC Zod | `target` min 1; exe/URL deny remains | `.strict()` | handler reject | n/a | MEU-19 `IPC_SCHEMAS` |

### Acceptance Criteria

| AC | Type | Description | Source | Negative Test |
|----|------|-------------|--------|---------------|
| AC-21.1 | integration | **Control `TRANSCRIPT_HOME`.** Observable: hash `#/transcript` + `transcript-page` + `channel-input`. Chain: `router.tsx` `/transcript` → `TranscriptPage` → `AppShell` outlet. Negative: route still `LazyPlaceholder` / “Connecting…” with `channel-input` count 0 → fail. | Spec 189–192, 595; grouping Session 9 | keep placeholder as the page |
| AC-21.2 | integration | **Control `CREATE_BODY`.** Observable: `fetch` URL `/transcripts`, method POST, JSON keys exactly `{ channel_url }`. Chain: Add click → client `.strict()` → `apiFetch`. Blank url: POST count 0. Extra form field stripped/rejected before fetch. | Spec 724; Boundary | POST `{channel_url, cookies:…}` |
| AC-21.3 | integration | **Control `LIST_ENVELOPE` + `QUERY_KEY`.** Observable: hook return `{ items, processor }`. Chain: `useTranscriptQueue` → `apiFetch('/transcripts')`. Negative: `data.map` / treat `data` as array → fail; `isProcessing` read before `data` exists → fail. | Spec 725, 737, 1147 | `const queue = data ?? []` |
| AC-21.4 | unit | **Control `POLL_ACTIVE_MS` / `POLL_IDLE_MS`.** Observable: `refetchInterval(query)` return. Chain: `query.state.data?.processor.state === 'Processing'` → 1000 else 5000 (including `data` undefined). | Spec 737; [Query v5 refetchInterval](https://tanstack.com/query/v5/docs/framework/react/reference/useQuery) | v4 `(data, query)` signature |
| AC-21.5 | integration | **Control `CARD_FIELDS` + `CARD_QUEUE`.** Observable: each `channel-card` shows name, status badge, `video_count`, `transcripts_done/video_count`, `word_count`, `output_dir`. Chain: list `items[]` → `ChannelCard`. Negative: read `video_ids` / `progress.json` / `processed_ids` in `PAGE_FILES` → fail; render a `queue-table` as the queue → fail. | Spec 647–659, 1149 | bind `video_ids.length` |
| AC-21.6 | unit | **Control `OUTPUT_TREE`.** Observable: `output-tree` text contains `{output_dir}/raw` and `{output_dir}/compiled` and does **not** append an extra `/{channel_name}` under that root. Chain: `output_dir` from job → tree labels. | Spec 674–684; R3-1 | `{output_dir}/{channel_name}/raw` |
| AC-21.7 | integration | **Control `ENABLED_WHEN` + `STOP_VERB`.** Observable: button `disabled` + fetch method/path. Chain: selection + `processor.state` → Start/Pause/Resume/Stop → `ACCEPTED_202`. Negative: Start while Processing still POSTs; page contains `cancel-btn` / `download:cancel` → fail. | Spec 636–637, 729–732; lock 4 | always-enabled Start; Cancel label |
| AC-21.8 | unit | **Control `REORDER_BODY`.** Observable: `job_ids` permutation. Chain: Up/Down from selected card → PUT `/transcripts/reorder`. Negative: send selected id only → fail. | Spec 665, 728 | `{ job_ids: [selected] }` |
| AC-21.9 | unit | **Control Requeue/Retry visibility.** Observable: `requeue-btn` in DOM only when selected/card status is `Cancelled`; `retry-btn` only when `Failed`. Chain: card status → conditional render (hide, not merely disable). Negative: both always visible → fail. | Spec 716–717 | always-shown Requeue |
| AC-21.10 | integration | **Control compile + completed opens.** Observable: POST `/transcripts/{id}/compile` returns `{ compiled_paths }`; View Compiled IPC `open-path` first path; Open ZIP uses `zip_path`; Open Folder uses `output_dir`. Chain: button → `TRANSCRIPT_COMMANDS` / card handler → `apiFetch` or `window.api.openPath`. Negative: compile body includes transcript text; open `C:/outside/tool.exe` still denied (MEU-19). | Spec 711–715, 735; MEU-19 F4 | POST compile with `{ text: … }` |
| AC-21.11 | integration | **Control `IN_PAGE_CONFIRM` + `VOID_204`.** Observable: first Remove click → portaled confirm (`createPortal(..., document.body)`, theme CSS vars); Confirm → exactly one DELETE `/transcripts/{id}` 204; Cancel, backdrop click, and Escape → DELETE count 0 and modal unmounts. Chain: `remove-btn` → portal → `apiFetch<void>` only after Confirm. Negative: `window.confirm`/`alert`/`prompt` in `PAGE_FILES`; inline (non-portaled) confirm; DELETE on first click; files deleted → fail. | Spec 718; G20 | native confirm; clip-prone inline dialog; delete files claim |
| AC-21.12 | integration | **Control `ERROR_SURFACE`.** Observable: in-page error text. Chain: `apiFetch` throw `ApiError` 422/409 → G15 banner. Negative: `.catch(() => undefined)` on Add/Start → fail. | G15; transcript.py 128, 191 | swallow 409 |
| AC-21.13 | integration | **Control `TRANSCRIPT_PALETTE_IDS` + `PALETTE_DELIVER`.** Observable: registry ids + event name + `AppShell` listener + `TRANSCRIPT_COMMANDS` (same function as the page button). Off `/transcript` (`#/`): `transcript:add` navigates to `#/transcript` and focuses `channel-input`; `transcript:start` navigates then invokes the same start export. Negative: listener only inside `TranscriptPage`; palette `apiFetch` second path → fail. | index 32–36; G11 | page-only listener |
| AC-21.14 | integration | **Control `TRANSCRIPT_LOCAL_IDS`.** Observable: testids + handler call. Requeue/Retry/Reorder/Compile/Remove/Open compiled/zip/folder exist. `settings:browse_transcript_dir` **not** on this page. | index 37–44, 62 | Settings Browse here |
| AC-21.15 | integration | **Control row/card open.** Observable: IPC `open-path` with compiled path / `zip_path` / `output_dir`. Disabled when the path is null/empty. Negative: open URL or exe still denied. | index 42–44; MEU-19 | bypass exe deny |
| AC-21.16 | integration | Wave 2 E2E **written and wired** (`E2E_WAVE2`, `E2E_CASES` W2-1…W2-6, `E2E_PER_CONTROL`, `E2E_ACTUATE`, `E2E_ATTACHED_FIRST`, `E2E_CONTROL_CENSUS`, `E2E_SEAM`, `E2E_SEAM_GATE`, `E2E_SEAM_PROOF`). Isolated `AVKIT_APP_DATA`. `E2E_NO_LIVE_YT` via `E2E_SEAM` + `E2E_HAPPY_PATH`. Sandbox no-display → `[B]` `E2E_SANDBOX`; files still exist. Spec 1103’s “4 tests” is the wave **minimum testids**; six cases are the E2 per-control bind (same expansion as MEU-20 W1). | Spec 1103, 1129–1135; E2; downloader RULE-2; `api.ts` 21–27 | unbound locator; `page.route`-only seam; missing `__e2eSeamInstalled`; `toBeHidden` as presence |
| AC-21.17 | unit | **Control `RATE_ETA` + `BATCH_OMIT`.** Observable: rate/eta strings from delay leaf + remaining; source has no “Batch ” renderer. Chain: `GET /settings/transcript` → `RATE_ETA` helper → `rate-display` / `eta-display`. Negative: invent `batch_index` from a second store; render Batch N/M → fail. Non-finite delay → both hidden. | Spec 655–657; lock 6 | `progress.json` rate; Batch 6/11 without API field |
| AC-21.18 | unit | `STATUS_COLORS` / G31–G32 + `JOB_STATUSES` includes `Paused` (job badge). No raw hex in `className`. No new raw `<select>` (G30 n/a). | G31–G32; Spec 650; lock 3 | `className="... #50fa7b"`; omit Paused badge |
| AC-21.19 | unit | G36 / anti-placeholder on `MEU21_TOUCHED`. No `test.skip` / `.only`. | G36 | skip a Red test to go green |
| AC-21.20 | integration | Add uses returned `TranscriptJobOut` then invalidate `QUERY_KEY` so the new card appears. Do not assume the POST returns `LIST_ENVELOPE`. | transcripts.py 58–64 | treat create as `{ items, processor }` |
| AC-21.21 | integration | OpenAPI `--check` exit 0 (no `packages/api/` edits). MCP tools untouched. Chrome `CHROME_RULES` not rewound. | G8; grouping | regenerate OpenAPI “just in case” |
| AC-21.22 | unit | `CHANNEL_URL_HINT` visible; blank `channel-input` leaves Add disabled **and** handler no-ops (POST count 0). | Spec 608, 668 | Add posts `""` |

### Spec Sufficiency Table

| Behavior | Classification | Resolution |
|----------|---------------|------------|
| Layout input → cards → processor bar | Spec | `06-gui.md` 599–641 |
| Card fields / no `video_ids` / no `progress.json` | Spec | 647–659, 1149 |
| Output tree at `output_dir/raw\|compiled` | Spec + Local Canon | 674–684; R3-1 review lock |
| Channel URL formats | Spec | 608, 668 — helper text; server extract validates |
| Queue persist / reorder / remove | Spec | 661–668, 718 |
| Completed actions + compile | Spec | 709–735 |
| `{ items, processor }` poll | Spec | 737, 1147 |
| Query v5 `refetchInterval(query)` | Research-backed | [useQuery](https://tanstack.com/query/v5/docs/framework/react/reference/useQuery) |
| Wire / 422 / extra forbid | Local Canon | MEU-16 schemas |
| Paused as job status | Local Canon | `TranscriptStatus` |
| Stop → Cancelled | Spec + Local Canon | 732; `stop_processing` |
| Rate/ETA from settings; no batch field | Spec + Local Canon | 655–657; `TranscriptJobOut` |
| In-page confirm | Spec + G20 | 718; emerging-standards G20 (portal, tokens, backdrop, Escape) |
| Palette transcript ids | Spec | index 32–36 |
| E2E wave 2 | Spec + E2 | 1103; six cases; `E2E_ACTUATE` + `E2E_ATTACHED_FIRST` |
| No live extract in Wave 2 | Local Canon + Research-backed | `transcript.py` 121–186; downloader RULE-2; Playwright `addInitScript` fetch override |
| 4A indexes absent | Local Canon | G30–G35 |
| Chrome RULE-1/2/3 | Local Canon | p6-gui-zorivest-chrome reflection |
| Settings Browse | Local Canon | index 62 → MEU-23 |

### Files Modified

| File | Action | Summary |
|------|--------|---------|
| `ui/src/renderer/src/features/transcript/*` | new | page, cards, hook, controls, `TRANSCRIPT_COMMANDS`, tree, rate/eta |
| `ui/src/renderer/src/components/layout/AppShell.tsx` | modify | `PALETTE_DELIVER` listeners for `TRANSCRIPT_EVENTS` (keep download listeners) |
| `ui/src/renderer/src/router.tsx` | modify | `/transcript` → `TranscriptPage` |
| `ui/src/renderer/src/registry/commandRegistry.ts` | modify | `TRANSCRIPT_PALETTE_IDS` + events (no `apiFetch`) |
| `ui/src/renderer/src/styles.css` | modify | `STATUS_COLORS` tokens for transcript badges if missing |
| `ui/tests/unit/transcript-*.test.ts` | new | AC-21.* |
| `ui/tests/e2e/test-ids.ts` | modify | WAVE2 + EXTRA |
| `ui/tests/e2e/transcript-queue.test.ts` | new | `E2E_CASES` (6) + `E2E_SEAM` |
| `ui/tests/e2e/fixtures/` | modify | transcript envelopes |
| `docs/BUILD_PLAN.md` | modify via `meu_status.py` | bind MEU-21; `HUB_NEXT_AFTER` |
| `GROUPING_FILE` | modify at H2 | `GROUPING_DONE_MARK` after exec `approved` only |
| `docs/execution/plans/2026-08-20-p6-gui-transcript/assert-*.ps1` | new | `RED_ORACLE_CHECK`, `HANDOFF_MARKER_CHECK`, `E2E_CONTROL_CENSUS` |

---

## Out of Scope

| Item | Kind | Deferred-to MEU | Basis |
|------|------|-----------------|-------|
| TTS / models page | deferred | MEU-22 | grouping Session 10; matrix 6.4 |
| Settings leaf writes / Browse transcript dir / HelpCards / action audit | deferred | MEU-23 | grouping Session 11; `gui-actions-index.md` 62 |
| PyInstaller / NSIS | deferred | MEU-24, MEU-25 | grouping Session 12 |
| Rewrite FastAPI routers / OpenAPI routes | out-of-scope | — | grouping Session 9; MEU-16 approved |
| Rewrite MCP tools | out-of-scope | — | MEU-17/18 approved |
| Rewind / restyle MEU-26 chrome | out-of-scope | — | chrome reflection Next Day Outline item 2 |
| SSE / OCR / multi-file TTS / MCP Guard | out-of-scope | — | `06-gui.md` 1158–1167 |
| Invent new MEU IDs | out-of-scope | — | grouping §4 |
| Live yt-dlp extract in agent E2E | out-of-scope | — | Local Canon `transcript.py` 121–186; downloader RULE-2; `E2E_SEAM` + `E2E_SEAM_PROOF` + `E2E_HAPPY_PATH` |
| Render Batch N/M | out-of-scope | — | Spec 656 optional-if-present; `TranscriptJobOut` omits the field (`BATCH_OMIT`) |
| In-app Markdown preview of compiled text | out-of-scope | — | Spec 711 View Compiled is IPC `openPath`; GET job has no transcript text (726) |
| `progress.json` as resume/card SoT | out-of-scope | — | Spec 682, 737, 1149 |

---

## BUILD_PLAN.md Audit

This project **does** update the hub: bind MEU-21 `execution_plan` to `PLAN_FOLDER`; add `PLAN_FOLDER_SLASH` to phase `"6"` **without removing** `PRIOR_PLAN_SLASHES`; rewrite `HUB_NEXT_FIELD` to `HUB_NEXT_AFTER`; preserve Session 1–8b links. Do not hand-edit AUTOGEN tables.

```powershell
rtk proxy uv run python -c "from pathlib import Path; import re; import sys; from tools.meu_status.model import load, get_meu; PLAN='docs/execution/plans/2026-08-20-p6-gui-transcript'; SLASH=PLAN+'/'; PRIORS=('docs/execution/plans/2026-08-19-p6-gui-shell/','docs/execution/plans/2026-08-20-p6-gui-downloader/','docs/execution/plans/2026-08-20-p6-gui-zorivest-chrome/'); NEXT='/create-plan p6-gui-tts-models'; MEUS=('MEU-21',); data=load(); p6=next(p for p in data['phases'] if str(p['id'])=='6'); eps=list(p6.get('execution_plans') or []); SLASH not in eps and sys.exit('phase 6 missing PLAN_FOLDER_SLASH'); miss_prior=next((p for p in PRIORS if p not in eps), None); miss_prior is not None and sys.exit('phase 6 missing '+miss_prior); miss=next((k for k in MEUS if get_meu(data,k) is None), None); miss is not None and sys.exit('missing '+miss); wrong=next((k for k in MEUS if get_meu(data,k).get('execution_plan')!=PLAN), None); wrong is not None and sys.exit(wrong+' execution_plan='+str(get_meu(data,wrong).get('execution_plan'))); hub=Path('docs/BUILD_PLAN.md').read_text(encoding='utf-8'); hits=re.findall('Next:\\s+'+chr(96)+'([^'+chr(96)+']+)'+chr(96), hub); len(hits)!=1 and sys.exit('hub Next field count='+str(len(hits))); hits[0]!=NEXT and sys.exit('hub Next='+hits[0]); print('PASS: SSOT_PLAN_BOUND')" *> C:/Temp/av-kit/ssot-plan-bound.txt; $code=$LASTEXITCODE; Get-Content C:/Temp/av-kit/ssot-plan-bound.txt; exit $code
```

---

## Verification Plan

Classify every command through [`.agent/docs/output-evidence-policy.md`](../../../../.agent/docs/output-evidence-policy.md).

### 1. UI type / unit / lint / build
```powershell
rtk proxy pwsh -NoProfile -Command { Push-Location ui; npx tsc --noEmit; if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }; npx vitest run --allowOnly=false; if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }; npx eslint src/ tests/ --max-warnings 0; if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }; npm run build; exit $LASTEXITCODE } *> C:/Temp/av-kit/ui-verify.txt; $code=$LASTEXITCODE; Get-Content C:/Temp/av-kit/ui-verify.txt | Select-Object -Last 40; exit $code
```

### 2. Python regression (no API edits expected)
```powershell
rtk proxy uv run pytest tests/unit/test_backend_cli.py tests/integration/test_backend_spawn.py tests/e2e tests/integration/test_api_wiring.py tests/unit/test_domain.py tests/unit/test_services.py tests/integration/test_sqlite_uow.py tests/integration/test_filesystem_media.py tests/integration/test_youtube_adapter.py tests/integration/test_transcript_adapter.py tests/integration/test_tts_models.py -x --tb=short -v *> C:/Temp/av-kit/pytest-p6-regression.txt; $code=$LASTEXITCODE; Get-Content C:/Temp/av-kit/pytest-p6-regression.txt | Select-Object -Last 40; exit $code
```

### 3. OpenAPI no-drift
```powershell
rtk proxy uv run python tools/export_openapi.py --check openapi.committed.json *> C:/Temp/av-kit/openapi-check.txt; $code=$LASTEXITCODE; Get-Content C:/Temp/av-kit/openapi-check.txt; exit $code
```

### 4. `HANDOFF_MARKER_CHECK`
```powershell
rtk proxy pwsh -NoProfile -File docs/execution/plans/2026-08-20-p6-gui-transcript/assert-handoff-markers.ps1 *> C:/Temp/av-kit/handoff-check.txt; $code=$LASTEXITCODE; Get-Content C:/Temp/av-kit/handoff-check.txt; exit $code
```

### 5. E2E control census + prior waves + wave 2
```powershell
rtk proxy pwsh -NoProfile -File docs/execution/plans/2026-08-20-p6-gui-transcript/assert-e2e-control-census.ps1 *> C:/Temp/av-kit/e2e-control-census.txt; $code=$LASTEXITCODE; if ($code -ne 0) { Get-Content C:/Temp/av-kit/e2e-control-census.txt; exit $code }; rtk proxy pwsh -NoProfile -Command { Push-Location ui; npm run build; if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }; npx playwright test launch.test.ts download-queue.test.ts transcript-queue.test.ts console-panel.test.ts console-chrome.test.ts command-palette-nav.spec.ts; exit $LASTEXITCODE } *> C:/Temp/av-kit/e2e-wave2.txt; $code=$LASTEXITCODE; Get-Content C:/Temp/av-kit/e2e-wave2.txt | Select-Object -Last 40; exit $code
```

### Stop conditions

- Plan review cap 3 without `approved`
- Exec review cap 6 without `approved`
- All reviewer rungs rate-limited
- Human-decision gate
- Genuine `[B]` with receipt (E2E no-display is valid `[B]` only for the **run**)

---

## Open Questions

None that block. Locks 2–10 resolve the forks.

| Question | Option | Source | Pros | Cons | Rec |
|----------|--------|--------|------|------|-----|
| Queue widget | `CARD_QUEUE` | Spec 611–633 | matches mockup + MEU description | cannot reuse table selection model | ✅ |
| | Reuse TanStack table | MEU-20 | shared selection | contradicts Spec cards | ❌ |
| Processor stop control | `STOP_VERB` | Spec 637; index 36 | matches Cancelled parent | name differs from downloader Cancel | ✅ |
| | Reuse `cancel-btn` | MEU-20 | shared testid | wrong action id / wrong verb | ❌ |
| Batch progress | `BATCH_OMIT` | Spec 656; `TranscriptJobOut` | no invented store | mockup shows Batch 6/11 | ✅ |
| | Client-compute from `batch_size` | settings leaf | looks like mockup | invents a field the API omitted | ❌ |
| Remove confirm | `IN_PAGE_CONFIRM` | Spec 718; G20 | portal + tokens + Escape/backdrop; files stay | extra chrome | ✅ |
| | `window.confirm` | Spec word “dialog” | thinner | G20 / Electron dialog | ❌ |

---

## Research References

- [TanStack Query v5 `useQuery` / `refetchInterval`](https://tanstack.com/query/v5/docs/framework/react/reference/useQuery)
- [TanStack Query v5 polling](https://tanstack.com/query/v5/docs/framework/react/guides/polling)
- [Playwright `page.addInitScript`](https://playwright.dev/docs/api/class-page#page-add-init-script)
- [Playwright `toBeHidden` (absent node passes)](https://playwright.dev/docs/api/class-locatorassertions#locator-assertions-to-be-hidden)
- [06-gui.md](../../../build-plan/06-gui.md) §Transcript
- [04-rest-api.md](../../../build-plan/04-rest-api.md) transcript routes
- [gui-actions-index.md](../../../build-plan/gui-actions-index.md)
- `.agent/docs/emerging-standards.md` G5, G11, G15, G20, G30–G36, E2
- p6-gui-downloader approved implementation + reflection RULE-2 (renderer fetch seam; `page.route` is not proof)
- p6-gui-zorivest-chrome reflection RULE-1/2/3
