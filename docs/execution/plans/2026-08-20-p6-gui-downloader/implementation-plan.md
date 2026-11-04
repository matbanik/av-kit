---
project: "2026-08-20-p6-gui-downloader"
date: "2026-08-20"
source: "docs/build-plan/06-gui.md"
meus: ["MEU-20"]
status: "complete"
template_version: "2.0"
---

# Implementation Plan: Phase 6 GUI Downloader

> **Project**: `2026-08-20-p6-gui-downloader`
> **Build Plan Section(s)**: [06-gui.md](../../../build-plan/06-gui.md) §Downloader Page (`/` — Default Route)
> **Status**: `draft`
> **Grouping**: [2026-08-18-build-plan-session-grouping.md](../../../../.agent/context/grouping/2026-08-18-build-plan-session-grouping.md) Session 8 — MEU-20 only

---

## Goal

Replace Session 7 `SHELL_HOME` skeleton at `/` with the Downloader page: SABR panel, URL/quality/audio/cookie form, TanStack Table queue, processor-aware controls, and Query v5 polling of `{ items, processor }`. Prove `apiFetch` against existing MEU-15 routes. Do not rewrite FastAPI routers or MCP tools. Do not start MEU-21–25. Do not invent MEU IDs.

---

## Context Tool Decision

```yaml
context_tool_decision:
  phase: planning_and_execution
  eligible_tools: []
  decision: not_applicable
  eligibility_basis: "graphify-out/graph.json and graphify-out-research/graph.json are absent; Headroom has no approved disposition. Planning and execution use exact-evidence receipts (bypass class)."
  human_message_reference: null
```

Re-evaluate before Step 6. If graphs remain absent and Headroom still has no approved disposition, reuse this record.

---

## Handoff Set

| Scope | Canonical handoff |
|---|---|
| MEU-20 | `.agent/context/handoffs/2026-08-20-p6-gui-downloader-MEU-20-handoff.md` |

Rolling implementation review: `.agent/context/handoffs/2026-08-20-p6-gui-downloader-implementation-critical-review.md`.

The product glob owner is named set `HANDOFF_GLOB`. Expected count is named set `HANDOFF_COUNT`.

---

## Work Packages and Context Lifecycle

`fresh_worker: none` → every non-`shared` row is `compact_continue`. Never emit `isolated`.

| ID | Work | depends_on | context_strategy | durable_outputs |
|---|---|---|---|---|
| WP-20a | MEU-20 Red: AC-20.1–20.22 UI tests **before** `DownloaderPage` production (`RED_TEST_TITLE` + `RED_AC_IDS` + `RED_JSON`). Includes superseding AC-19.11 / AC-19.17 home+palette assertions. Receipt must pass `RED_ORACLE_CHECK` (kind `ui`) — 22 distinct failed JSON tests, not a stuffed title. | — | `compact_continue` | `C:/Temp/av-kit/fail-to-pass-meu-20-ui.txt`; `RED_JSON` |
| WP-20b | Green: `DownloaderPage` + Query hook + table + cookie settings PUT + `PALETTE_DELIVER` (`AppShell` + `DOWNLOAD_COMMANDS`). Do not neutralize tests. Do not edit FastAPI/MCP. | WP-20a | `compact_continue` | `ui/src/renderer/src/features/downloader/`; `AppShell.tsx`; compact then re-read `task.md` |
| WP-20c | Wave 1 E2E **written and wired** (`E2E_WAVE1` + `E2E_CASES` + `E2E_PER_CONTROL` + `E2E_CONTROL_CENSUS`). Update wave0 home test to `DOWNLOADER_HOME`. Run or `[B]` `E2E_SANDBOX`. | WP-20b | `compact_continue` | `ui/tests/e2e/download-queue.test.ts`; `C:/Temp/av-kit/e2e-wave1.txt` |
| WP-20d | `MEU_SCOPED_GATE` after `HANDOFF_SOURCE_READ`, then canonical handoff | WP-20c | `compact_continue` | `.agent/context/handoffs/2026-08-20-p6-gui-downloader-MEU-20-handoff.md` |
| WP-20e | Hub + SSOT: bind MEU-20; keep MEU-19 plan slash; `HUB_NEXT_AFTER`. Grouping Session 8 → complete is **H2 after exec `approved`**, not this row. | WP-20d | `shared` | `.agent/context/meu-status.yaml`; `docs/BUILD_PLAN.md` |

---

## User Review Required

None that block planning. Sourced conflicts are locked below (reviewer confirms; do not invent a third behavior):

1. **Harness gate:** `create-plan.md` §5c Cursor-default `plan_to_exec_gate=human` vs `.agent/context/harness.local.md` `reviewer-auto`. **Override wins.** After Codex `approved`, auto-continue to execution.
2. **`/` owner:** Session 7 locked `SHELL_HOME` (no `url-input`). **Lock `DOWNLOADER_HOME`.** Basis: grouping Session 8; `06-gui.md` 352–353; matrix 6.2. Authorize replacing AC-19.11 negatives and `launch.test.ts` / `shell-home.test.ts` / `command-palette.test.ts` `download:add` forbid. That is contract supersession, not G36 neutralization.
3. **`apply-defaults` / download-path Browse:** `gui-actions-index.md` 30–31 owner is Settings. **Defer MEU-23.** The Downloader REST table lists the route; the button is not on this page layout.
4. **Cookie radios vs settings:** `POST /downloads` has no cookie fields. Service `add_to_queue` reads `downloader.cookie_*` (`download.py` 406–418). **Lock `COOKIE_SETTINGS_PUT`:** page radios persist `PUT /settings/downloader` leaf keys, and Test Cookies uses `COOKIE_TEST_BODY` (paths only).
5. **UX2 vs Spec hide:** Spec 440/445–446 hide Audio Format and cookie browser/file until the visible gate is set. UX2 exception (section header / visible checkbox) applies. **Lock Spec hide** behind those visible gates.
6. **G4 pagination:** MEU-15 `GET /downloads` has no page/search params. Spec summary counts require the full `items` array. **Lock `RENDER_ALL_ITEMS`.** Do not invent a list query API.
7. **4A indexes:** `docs/gui-element-reference.md`, `docs/gui-button-index.md`, `.agent/docs/gui-standards-enforcement.md` remain **absent**. Apply `06-gui.md` + G30–G35 + `gui-actions-index.md`.
8. **Live extract in Wave 1:** Production `add_to_queue` calls `extract_info` before persist (`download.py` 166–175). Wave 1 must not reach that path. **Lock `E2E_SEAM`** (Playwright `page.route`). Happy-path substitute is `E2E_HAPPY_PATH`. Spec 549/1129–1135 require Add→row; they do not themselves forbid live YouTube.

**This section is content for the review loop, NOT a cue to stop now.**

---

## Named sets (PR-9 — define once)

| Name | Value | Owner |
|------|-------|-------|
| `DOWNLOADER_HOME` | route `/` component is `DownloaderPage` (not `ShellHome` / `ModuleSkeleton` as the page). `nav:downloader` still hashes to `/`. | Spec 352–353; grouping Session 8 |
| `PAGE_FILES` | `ui/src/renderer/src/features/downloader/{DownloaderPage,DownloadQueueTable,useDownloadQueue,download-controls,quality-options,sabr-panel,cookie-bar,download-commands}.tsx?ts` + `ui/src/renderer/src/router.tsx` + `ui/src/renderer/src/registry/commandRegistry.ts` + `ui/src/renderer/src/components/layout/AppShell.tsx` | this plan |
| `TABLE_PIN` | `@tanstack/react-table ^8.21.0` (zorivest `ui/package.json` STACK_PINS-only copy) | Local Canon zorivest |
| `QUALITY_WIRE` | `best`, `2160p`, `1440p`, `1080p`, `720p`, `480p`, `360p`, `240p`, `144p`, `lowest` | `DownloadCreateIn`; Spec 439 |
| `AUDIO_WIRE` | `default`, `best`, `lowest`, `low_webm`, `medium_webm`, `standard_webm`, `standard_m4a`, `standard_mp3`, `high_m4a` | `DownloadCreateIn`; Spec 441 |
| `QUALITY_DEFAULT` | `1080p` | Spec 439 |
| `AUDIO_DEFAULT` | `default` | Spec 441 |
| `SABR_QUALITY` | `{360p}` | Spec 421, 448 |
| `SABR_AUDIO` | `{standard_mp3, high_m4a}` | Spec 421, 448 |
| `SABR_MODES` | `inactive` \| `active` \| `checking` | `SABRStatusOut` |
| `LIST_ENVELOPE` | `{ items, processor }` — never a bare array | Spec 571–587; p4 |
| `PROCESSOR_STATES` | `Idle` \| `Processing` \| `Paused` | Spec 492–498 |
| `JOB_STATUSES` | `Pending`, `Downloading`, `Done`, `Failed`, `Skipped`, `QualityBlocked`, `AgeRestricted`, `Cancelled` — **not** `Paused` | Spec 465–478 |
| `POLL_ACTIVE_MS` | `1000` when `processor.state === 'Processing'` | Spec 582–584 |
| `POLL_IDLE_MS` | `5000` otherwise (including no data yet) | Spec 582–584 |
| `QUERY_KEY` | `['downloads']` | Spec 580 |
| `CREATE_BODY` | `{ url: string.min(1), quality: QUALITY_WIRE, audio_only: boolean, audio_format: AUDIO_WIRE }` only | `DownloadCreateIn`; extra forbid |
| `REORDER_BODY` | `{ job_ids: string[] }` permutation of current queue ids | `ReorderIn`; p4 |
| `COOKIE_MODES` | `none` \| `browser` \| `file` | `CookieTestIn` |
| `COOKIE_BROWSERS` | `chrome`, `firefox`, `edge`, `brave`, `opera`, `vivaldi`, `chromium`, `whale`, `safari` | Spec 444 |
| `COOKIE_TEST_BODY` | `{ mode, browser?, profile?, cookie_file? }` — paths only; never cookie bytes | Spec 446; 04 177 |
| `COOKIE_SETTINGS_LEAVES` | `{ cookie_mode, cookie_browser, cookie_browser_profile, cookie_file_path }` | `SettingsPutIn`; `download.py` 406–418 |
| `COOKIE_SETTINGS_PUT` | `PUT /settings/downloader` with only `COOKIE_SETTINGS_LEAVES` present (extra forbid) | p4 settings; this plan lock 4 |
| `ENABLED_WHEN` | Start: pending items ∧ state ≠ Processing; Pause: Processing; Resume: Paused; Cancel: Processing ∨ Paused; Up/Top: selected ∧ not first; Down/Bottom: selected ∧ not last; Reset: selected Failed; Remove: selected; Clear All: items.length > 0 | Spec 507–519 |
| `VOID_204` | `DELETE /downloads/{id}`, `DELETE /downloads` → `apiFetch<void>` | p4; G17/204 |
| `ACCEPTED_202` | start/pause/resume/cancel → 202 empty; start while Processing → 409 `ERROR_ENVELOPE` | downloads.py 143–187 |
| `DOWNLOAD_PALETTE_IDS` | `{download:add, download:start, download:pause, download:resume, download:cancel, download:clear, download:sabr_check}` | `gui-actions-index.md` 16–24 |
| `DOWNLOAD_LOCAL_IDS` | `{download:remove, download:reset, download:reorder, download:sabr_force, download:sabr_clear, download:cookies_test, download:open_file, download:open_folder}` | `gui-actions-index.md` 21–29 |
| `DOWNLOAD_EVENTS` | `av-kit:download:{add,start,pause,resume,cancel,clear,sabr-check}` dispatched from palette and page buttons; **no** `apiFetch` in `commandRegistry` | G11; RULE-1 |
| `DOWNLOAD_COMMANDS` | `ui/src/renderer/src/features/downloader/download-commands.ts` — the single handler set for `DOWNLOAD_PALETTE_IDS` (one fetch path) | G11; this plan |
| `PALETTE_DELIVER` | `AppShell` always-mounted listener is the production owner. It calls `DOWNLOAD_COMMANDS`. Off `/`: navigate `#/` then invoke the same handler (`NAVIGATE_AND_DELIVER`). `download:add` focuses `url-input` (no POST). Page buttons call the same exports. Negative: listener only inside `DownloaderPage` → off-route no-op. | G11 origin (PlanningLayout dead-end); `router.tsx` AppShell-always-mounted |
| `WAVE1_TESTIDS` | `downloader-page`, `url-input`, `add-btn`, `queue-table`, `queue-row`, `start-btn`, `pause-btn`, `resume-btn`, `cancel-btn`, `sabr-status`, `sabr-check-btn` | Spec 1100 |
| `WAVE1_EXTRA_TESTIDS` | `quality-select`, `audio-only`, `audio-format`, `cookie-mode-none`, `cookie-mode-browser`, `cookie-mode-file`, `cookie-browser`, `cookie-profile`, `cookie-file`, `cookie-test-btn`, `sabr-force-btn`, `sabr-clear-btn`, `up-btn`, `down-btn`, `top-btn`, `bottom-btn`, `reset-btn`, `remove-btn`, `clear-all-btn`, `queue-summary`, `processor-indicator`, `open-file-btn`, `open-folder-btn` | E2; §4A |
| `E2E_WAVE1` | `ui/tests/e2e/download-queue.test.ts` (`E2E_CASES`, 6 tests) + `WAVE1_TESTIDS` / `WAVE1_EXTRA_TESTIDS` in `test-ids.ts` | Spec 1100 |
| `E2E_CASES` | `W1-1` `DOWNLOADER_HOME`; `W1-2` nav from `#/transcript`; `W1-3` WAVE1+EXTRA presence; `W1-4` `E2E_HAPPY_PATH` via `E2E_SEAM`; `W1-5` `ENABLED_WHEN` chrome + local/open ids; `W1-6` `PALETTE_DELIVER` off-route `download:add` | Spec 1100; E2; G11 |
| `E2E_LOCATOR_FORM` | Wave 1 locators are literal `getByTestId('<kebab-id>')` (single quotes). Comments and `test-ids.ts` literals do not satisfy `E2E_CONTROL_CENSUS`. | E2 |
| `E2E_PER_CONTROL` | The allowed method must be chained on the same locator expression: `expect(page.getByTestId('id')).toBeVisible()` or `page.getByTestId('id').click()`. W1-3 visual; W1-5 enabled/disabled; W1-4 fill/click/visible; W1-1/W1-6 visible/focused. A nearby method on an unrelated receiver is a fail. Owner: `Test-HasBound`. | E2; r4 R4-1 |
| `E2E_SEAM` | Playwright `page.route` on the Electron page for `/downloads`, `/downloads/sabr`, `/settings/downloader`. Fixtures under `ui/tests/e2e/fixtures/`. POST `/downloads` handler asserts `CREATE_BODY` keys then fulfills `DownloadCreateOut` `{ items }` (not the list envelope). GET `/downloads` fulfills `LIST_ENVELOPE` `{ items, processor }`. Start/Pause/Resume/Cancel fulfill 202. Never an un-mocked request to production extract. | Research-backed: [Playwright network mocking](https://playwright.dev/docs/network#network-mocking); Local Canon: `download.py` 166–175; `DownloadCreateOut` vs `DownloadListOut` |
| `E2E_HAPPY_PATH` | with `E2E_SEAM` active: fill `url-input` → Add click → `queue-row` visible. URL may be `https://example.invalid/watch?v=e2e0001` because extract never runs. | Spec 549 + 06-gui 1129–1135 item 3; `E2E_SEAM` |
| `E2E_NO_LIVE_YT` | Wave 1 must not let Start/Resume/Cancel/Add reach yt-dlp extract. Enforced by `E2E_SEAM`, not by Spec 549. | Local Canon `download.py` 166–175; Research-backed Playwright `page.route` |
| `E2E_CONTROL_CENSUS` | `rtk proxy pwsh -NoProfile -File docs/execution/plans/2026-08-20-p6-gui-downloader/assert-e2e-control-census.ps1` — comment-stripped `E2E_LOCATOR_FORM` + `E2E_PER_CONTROL` (same-expression receiver bind). Empty/skip tests fail. Helper rejects the R4-1 unrelated-receiver snippet. | E2; create-plan §4A.3; r4 R4-1 |
| `RED_AC_IDS` | `AC-20.1` … `AC-20.22` (22). Owner: `assert-red-oracle.ps1` ui kind + `RED_JSON`. | FIC; this plan |
| `RED_TEST_TITLE` | every AC-20.N unit/integration test is a **distinct** Vitest case whose `fullName`/`title` contains exactly one `AC-20.N` (no multi-id titles). | FIC tests-first |
| `RED_JSON` | `C:/Temp/av-kit/fail-to-pass-meu-20-ui.json` from Vitest 3 `--reporter=json --outputFile`. Shape: `testResults[].assertionResults[]` with `fullName`/`title` + `status`. | Vitest 3 json reporter |
| `BUILDER_PIN` | `—` while `fresh_worker: none`. Post-smoke pin in harness.local.md is unused this session. | harness.local.md |
| `GROUPING_FILE` | `.agent/context/grouping/2026-08-18-build-plan-session-grouping.md` | grouping authority |
| `GROUPING_DONE_MARK` | Progress-table row `\| 8 \| \`p6-gui-downloader\` \| ✅ complete \|` and Session 8 heading `✅ complete`; Sessions 9–12 stay `⬜ pending`. Applied at H2 after exec `approved` only. | grouping Progress; DR-3 |
| `REFLECTION_TEMPLATE` | `docs/execution/reflections/TEMPLATE.md` | closeout |
| `REFLECTION_SCHEMA` | `.agent/schemas/reflection.v1.yaml` | closeout |
| `REFLECTION_PEER_RULE` | newest `docs/execution/reflections/*-reflection.md` excluding `TEMPLATE.md`, sorted by `LastWriteTime` descending | AGENTS closeout |
| `REFLECTION_SOURCE_READ` | `C:/Temp/av-kit/reflection-source-read-meu-20.txt` with `TEMPLATE=`, `SCHEMA=`, `PEER=`, `PASS: REFLECTION_SOURCE_READ` | H2-1 |
| `E2E_SANDBOX` | un-run E2E in agent sandbox → `[B]` + CI follow-up. Tests stay written and wired. | known-issue policy |
| `RENDER_ALL_ITEMS` | table rows = `data.items` (no invented page/search API) | Spec 521–536; G3/G4 no list params |
| `STATUS_COLORS` | map `JOB_STATUSES` + processor to CSS `@theme` tokens (no raw hex in `className`) | Spec 527–544; G31–G32 |
| `ERROR_SURFACE` | 422/409/`ApiError` shown in-page (G15); never swallow | G15; `ERROR_ENVELOPE` |
| `REGRESSION_TESTS` | p6-gui-shell H1-2 Python set (do not drop) | p6 carry-forward |
| `SCAN_G36_ARGS` | skip/only/todo markers under `ui/tests/unit` + `ui/tests/e2e` + `tests/` | G36 |
| `SCAN_PLACEHOLDER_ARGS` | `TODO`, `FIXME`, `NotImplementedError` under `ui/src` | anti-placeholder |
| `HANDOFF_COUNT` | `1` | `HANDOFF_GLOB` |
| `HANDOFF_GLOB` | `.agent/context/handoffs/2026-08-20-p6-gui-downloader-MEU-20-handoff.md` | this plan |
| `PLAN_FOLDER` | `docs/execution/plans/2026-08-20-p6-gui-downloader` | MEU `execution_plan` |
| `PLAN_FOLDER_SLASH` | `docs/execution/plans/2026-08-20-p6-gui-downloader/` | phase `"6"` (keep Session 7 slash) |
| `PRIOR_PLAN_SLASH` | `docs/execution/plans/2026-08-19-p6-gui-shell/` | must remain on phase `"6"` |
| `HUB_NEXT_AFTER` | `/create-plan p6-gui-transcript` | grouping pathway #9 |
| `HUB_NEXT_FIELD` | the unique `Next: \`...\`` field in `docs/BUILD_PLAN.md` | p6 pattern |
| `EXEC_REVIEW_FILE` | `.agent/context/handoffs/2026-08-20-p6-gui-downloader-implementation-critical-review.md` | this plan |
| `EXEC_REVIEW_TARGET` | `docs/execution/plans/2026-08-20-p6-gui-downloader/implementation-plan.md` | exact `target_plan` |
| `EXEC_REVIEW_MAX_ROUND` | `6` | execution-review cap |
| `CHECK_EXEC_REVIEW` | `tools/check_exec_review.py` — first YAML frontmatter only; `--expected-mode implementation` | p2 Human-approved |
| `HANDOFF_TEMPLATE` | `.agent/context/handoffs/TEMPLATE.md` | closeout |
| `HANDOFF_SOURCE_READ` | `C:/Temp/av-kit/handoff-source-read-meu-20.txt` written **once** before the MEU-20 handoff | p4 F4 |
| `HANDOFF_BUNDLE_MARKERS` | `Acceptance Criteria`, `CACHE BOUNDARY`, `FAIL_TO_PASS`, `Changed Files`, `Quality Gate Results`, `Commands Executed`, `## Evidence` | TEMPLATE |
| `VITEST_ALLOW_ONLY` | `ui/vitest.config.ts` has `test.allowOnly: false`. Every `npx vitest run` passes `--allowOnly=false`. | G36 |
| `UI_ESLINT` | `npx eslint src/ tests/ --max-warnings 0` | G36 |
| `RED_ORACLE` | UI FAIL_TO_PASS text has allow-marker and no deny-marker **and** `RED_JSON` maps 22 distinct failed `assertionResults` 1:1 onto `RED_AC_IDS` (multi-id titles rejected). | r1 F2; r2 R2-1 |
| `RED_ORACLE_CHECK` | `rtk proxy pwsh -NoProfile -File docs/execution/plans/2026-08-20-p6-gui-downloader/assert-red-oracle.ps1 -Kind ui -Receipt <text> -JsonReceipt RED_JSON` | PR-9 |
| `HANDOFF_MARKER_CHECK` | `rtk proxy pwsh -NoProfile -File docs/execution/plans/2026-08-20-p6-gui-downloader/assert-handoff-markers.ps1` | PR-9 |
| `REFLECTION_MARKERS` | `Friction Log`, `Execution Trace`, `Pattern Extraction`, `Patterns to KEEP`, `Next Session Design Rules`, `RULE-`, `Efficiency Metrics`, `Rule Adherence`, `Instruction Coverage`, `schema: v1`, `sections:`, `loaded:`, `decisive_rules:` | p6 |
| `MEU20_TOUCHED` | `PAGE_FILES` + `ui/package.json` + `ui/tests/unit` downloader + `ui/tests/e2e/download-queue.test.ts` + `test-ids.ts` + superseded shell-home/palette/launch home tests + `AppShell.tsx` | MEU-20 files |
| `MEU_SCOPED_GATE` | `ui`: `npx tsc --noEmit` + `npx vitest run --allowOnly=false` + `UI_ESLINT` + `npm run build`; + `SCAN_PLACEHOLDER` + `SCAN_G36` + `HANDOFF_MARKER_CHECK` + AC-20.* | AGENTS MEU gate |
| `OPENAPI_CHECK` | `packages/api/` is **not** modified → `--check` still run as no-drift proof. `-o` forbidden unless FAIL. | G8 skip-with-proof |
| `SUPERSEDED_19` | `shell-home.test.ts` AC-19.11; `command-palette.test.ts` `not.toContain('download:add')`; `launch.test.ts` “skeleton, not a downloader form” | this plan lock 2 |

---

## G29 wiring checklist

| Layer | Ready? | Evidence |
|-------|--------|----------|
| Domain / DownloadService / FastAPI download routes | YES | MEU-10 + MEU-15 `approved`. Do not rewrite. |
| `{ items, processor }` + SABR + cookies/test + 202/204/409 | YES | `downloads.py` |
| `apiFetch` + IPC + AppShell | YES | MEU-19 `approved` |
| Downloader page at `/` | NO → **this MEU** | grouping Session 8 |
| Transcript/TTS/Settings pages | NO — **later MEUs** | grouping 9–11 |
| MCP tools | YES — do not rewrite | MEU-17/18 `approved` |

---

## create-plan §4A — GUI Element Compliance

**Triggered:** Downloader page creates `<button>`, `<input>`, `<select>`, radios, status badges in `ui/src/renderer/`.

| Check | Result |
|-------|--------|
| `docs/gui-element-reference.md` | **Absent** — G31–G35 + Spec tokens |
| Button/input/output indexes | **Absent** — map via table below |
| E2E written+wired | `E2E_WAVE1` + `E2E_CASES` + `E2E_PER_CONTROL` + `E2E_CONTROL_CENSUS` |
| G30–G35 / E2 | G30 on quality/audio/browser `<select>` (inline theme-aware styles). G31 `bg-accent` only. G32 no raw hex in `className` (`STATUS_COLORS` via `@theme`). G33 duration tokens. G34 variants below. G35 tiers below. E2 = `E2E_WAVE1`. |
| G20 | no `window.confirm` for Clear All — use in-page enabledWhen + G15 errors (no native dialog) |
| G11 | `PALETTE_DELIVER`: `AppShell` always-mounted listener owns reachability; `DOWNLOAD_COMMANDS` is the one fetch path; palette does not call `apiFetch` |
| G16 | existing `CSP_IMG` — do not regress |
| G5 | `POLL_ACTIVE_MS` / `POLL_IDLE_MS` |
| G3 | no client-side search of thousands; queue is `RENDER_ALL_ITEMS` |
| G27 | not used; `openPath` / `showItemInFolder` already allowlisted |

Indexes remain absent. **Local fallback basis:** G34 text in `emerging-standards.md` (5 variants `primary|secondary|outline|ghost|destructive` × 3 sizes `sm|md|lg` × default/hover/focus/disabled/loading). Toolbar actions default `md`; row actions default `sm`. G35 tiers T0–T1 (no dirty-save chain on this page).

| Element | Variant | Size | States | testid | Feedback |
|---------|---------|------|--------|--------|----------|
| URL input | text | md | default/focus/disabled | `url-input` | T0 |
| Add | primary | md | default/hover/focus/disabled/loading | `add-btn` | T1 POST create |
| Quality select | G30 select | md | default/focus/disabled | `quality-select` | T0 |
| Audio only | checkbox | md | default/focus | `audio-only` | T0 reveal audio-format |
| Audio format | G30 select | md | default/focus/disabled; hidden until audio-only | `audio-format` | T0 |
| Cookie none/browser/file | radio | md | default/focus | `cookie-mode-none`, `cookie-mode-browser`, `cookie-mode-file` | T1 `COOKIE_SETTINGS_PUT` |
| Cookie browser | G30 select | md | default/focus; hidden until browser | `cookie-browser` | T0 |
| Cookie profile | text | md | default/focus; hidden until browser | `cookie-profile` | T0 |
| Cookie file | text + browse | md | default/focus; hidden until file | `cookie-file` | T0 path only |
| Test Cookies | secondary | sm | default/hover/focus/disabled/loading | `cookie-test-btn` | T1 POST test |
| SABR Check | secondary | sm | default/hover/focus/loading | `sabr-check-btn` | T1 POST |
| SABR Force | secondary | sm | default/hover/focus/loading | `sabr-force-btn` | T1 POST |
| SABR Clear | secondary | sm | default/hover/focus/loading | `sabr-clear-btn` | T1 POST |
| SABR banner | status | — | hidden when inactive | `sabr-status` | T1 |
| Start | primary | md | default/hover/focus/disabled | `start-btn` | T1 202/409 |
| Pause | secondary | md | default/hover/focus/disabled | `pause-btn` | T1 202 |
| Resume | secondary | md | default/hover/focus/disabled | `resume-btn` | T1 202 |
| Cancel | secondary | md | default/hover/focus/disabled | `cancel-btn` | T1 202 |
| Up / Down / Top / Bottom | secondary | sm | default/hover/focus/disabled | `up-btn`, `down-btn`, `top-btn`, `bottom-btn` | T1 PUT reorder |
| Reset | secondary | sm | default/hover/focus/disabled | `reset-btn` | T1 POST reset |
| Remove | destructive | sm | default/hover/focus/disabled | `remove-btn` | T1 204 |
| Clear All | destructive | md | default/hover/focus/disabled | `clear-all-btn` | T1 204; G20 no `window.confirm` |
| Open file | ghost | sm | default/hover/focus/disabled (null `file_path`) | `open-file-btn` | T1 IPC `open-path` |
| Open folder | ghost | sm | default/hover/focus/disabled (null `file_path`) | `open-folder-btn` | T1 IPC `show-item-in-folder` |
| Queue table / row / summary | output | — | default | `queue-table`, `queue-row`, `queue-summary` | T1 poll |
| Processor indicator | status | — | hidden when Idle | `processor-indicator` | T1 |

---

## MEU-20 — `gui-downloader`

### Boundary Inventory

| Surface | Schema Owner | Field Constraints | Extra-Field Policy | Invalid-input | Create/Update parity | Source |
|---------|-------------|-------------------|--------------------|---------------|----------------------|--------|
| URL Add form → REST | client Zod `.strict()` `CREATE_BODY` then Pydantic `DownloadCreateIn` | `url` min 1; `quality`/`audio_format` wire enums | extra forbid (client + server) | no POST if url blank; 422 `ERROR_SURFACE` | n/a (create only) | Spec 438–441; 04 190–192 |
| Cookie test form → REST | Zod `.strict()` `COOKIE_TEST_BODY` then `CookieTestIn` | mode enum; browser in `COOKIE_BROWSERS` when mode=browser; `cookie_file` path when mode=file | extra forbid | 422; never cookie bytes | test-only | Spec 446 |
| Cookie persist → settings | Zod `.strict()` `COOKIE_SETTINGS_LEAVES` then `SettingsPutIn` | leaf keys only | extra forbid | 422 unknown key | same leaves on every change | lock 4 |
| SABR POSTs | `EmptyIn` / no body | no extra keys | extra forbid | 422 | n/a | downloads.py 102–129 |
| Reorder | Zod `.strict()` `REORDER_BODY` | permutation of current ids | extra forbid | 422 | n/a | 04 183 |
| Queue poll | response `DownloadListOut` | must have `items` + `processor` | ignore unknown out fields; never treat as array | `ERROR_SURFACE` | GET only | Spec 571–587 |
| Row open file/folder | existing IPC Zod | `target` min 1; exe deny remains | `.strict()` | handler reject | n/a | MEU-19 `IPC_SCHEMAS` |

### Acceptance Criteria

| AC | Type | Description | Source | Negative Test |
|----|------|-------------|--------|---------------|
| AC-20.1 | integration | **Control `DOWNLOADER_HOME`.** Observable: hash `#/` + `downloader-page` + `url-input`. Chain: `router.tsx` `/` → `DownloaderPage` → `AppShell` outlet. Negative: `/` still only `ShellHome` / “Connecting to backend…” with `url-input` count 0 → fail. | Spec 352–353; grouping Session 8 | keep Session 7 skeleton as default |
| AC-20.2 | unit | **Control `QUALITY_WIRE` + `AUDIO_WIRE` + defaults.** Observable: option value set. Chain: `quality-options` → form state (`QUALITY_DEFAULT` / `AUDIO_DEFAULT`). Negative: send `P1080` / `1080P` / `Best` as the POST `quality` → fail. | Spec 439–441; 04 190; 06 1146 | domain enum on the wire |
| AC-20.3 | integration | **Control `CREATE_BODY`.** Observable: `fetch` URL `/downloads`, method POST, JSON keys exactly `CREATE_BODY`. Chain: Add click → client `.strict()` → `apiFetch`. Blank url: POST count 0. Extra form field stripped/rejected before fetch. | Spec 549; Boundary | POST `{url, quality, cookies:…}` |
| AC-20.4 | integration | **Control `LIST_ENVELOPE` + `QUERY_KEY`.** Observable: hook return `{ items, processor }`. Chain: `useDownloadQueue` → `apiFetch('/downloads')`. Negative: `data.map` / treat `data` as array → fail; `isProcessing` read before `data` exists → fail. | Spec 571–589 | `const queue = data ?? []` |
| AC-20.5 | unit | **Control `POLL_ACTIVE_MS` / `POLL_IDLE_MS`.** Observable: `refetchInterval(query)` return. Chain: `query.state.data?.processor.state === 'Processing'` → 1000 else 5000 (including `data` undefined). | Spec 582–584; [Query v5 refetchInterval](https://tanstack.com/query/v5/docs/framework/react/reference/useQuery) | v4 `(data, query)` signature |
| AC-20.6 | integration | **Control SABR panel.** Observable: `GET /downloads/sabr` on mount; banner hidden when `inactive`; Check/Force/Clear POST named routes; `checking` shows spinner text. Chain: page mount → GET; buttons → POST → invalidate `QUERY_KEY` + sabr query. Negative: Force only flips local React state → fail. | Spec 404–432, 561–564 | local-only SABR flag |
| AC-20.7 | unit | **Control `SABR_QUALITY` / `SABR_AUDIO`.** Observable: option lists. Chain: sabr `active` → quality options `{360p}` and audio `{standard_mp3, high_m4a}`; inactive → full wires. Negative: `1080p` remains selectable while active → fail. | Spec 420–424, 448 | keep 1080p under SABR |
| AC-20.8 | integration | **Control `COOKIE_SETTINGS_PUT` + `COOKIE_TEST_BODY`.** Observable: PUT leaf JSON + POST test JSON. Chain: radio/browser/profile/file → PUT; Test → POST paths only; file path from `showFileDialog` (not renderer raw path). Negative: cookie file **contents** or `Cookie` header in either body → fail. | Spec 442–446; lock 4 | paste Netscape bytes |
| AC-20.9 | integration | **Control `ENABLED_WHEN` + queue commands.** Observable: button `disabled` + fetch method/path. Chain: selection + `processor.state` → Start/Pause/Resume/Cancel/reorder/reset/remove/clear → `ACCEPTED_202` / `VOID_204` / reset/reorder. Negative: Start while Processing still POSTs (must be disabled **and** handler no-ops); Clear with empty queue POSTs → fail. | Spec 503–519 | always-enabled Start |
| AC-20.10 | unit | **Control `REORDER_BODY`.** Observable: `job_ids` permutation. Chain: Up/Down/Top/Bottom from `getSelectedRowModel()` ([Table v8 row selection](https://tanstack.com/table/v8/docs/guide/row-selection)) → PUT `/downloads/reorder`. Negative: send selected id only (not full permutation) → fail. | Spec 514–517; 04 183 | `{ job_ids: [selected] }` |
| AC-20.11 | integration | **Control summary + processor indicator.** Observable: counts for every `JOB_STATUSES` row always present; processor hidden when Idle, “Processing…” / “Queue Paused” otherwise. `Paused` is **not** a per-item status. | Spec 521–544 | item status `Paused` |
| AC-20.12 | integration | **Control `ERROR_SURFACE`.** Observable: in-page error text. Chain: `apiFetch` throw `ApiError` 422/409 → G15 banner. Negative: `.catch(() => undefined)` on Add/Start → fail. | G15; 04 98 | swallow 409 |
| AC-20.13 | integration | **Control `DOWNLOAD_PALETTE_IDS` + `PALETTE_DELIVER`.** Observable: registry ids + event name + `AppShell` listener + `DOWNLOAD_COMMANDS` (same function as the page button). Off `/` (`#/transcript`): `download:add` navigates to `#/` and focuses `url-input`; `download:start` navigates then invokes the same start export. Negative: listener only inside `DownloaderPage` (off-route no-op); `download:add` as `() => undefined`; palette `apiFetch` second path → fail. | `gui-actions-index.md` 16–24; G11; RULE-1 | leftover AC-19.17 forbid; page-only listener |
| AC-20.14 | integration | **Control `DOWNLOAD_LOCAL_IDS`.** Observable: testids + handler call. Force/Clear/Test/Remove/Reset/Open file/folder exist. `download:apply_quality_pending` and `download:browse_path` **not** on this page. | index 21–31 | Settings Apply button here |
| AC-20.15 | integration | **Control row open.** Observable: IPC `open-path` / `show-item-in-folder` with `file_path`. Chain: row action → existing IPC. Disabled when `file_path` is null. Negative: open `C:/outside/tool.exe` still denied (MEU-19). | index 28–29; MEU-19 F4 | bypass exe deny |
| AC-20.16 | integration | Wave 1 E2E **written and wired** (`E2E_WAVE1`, `E2E_CASES` W1-1…W1-6, `E2E_PER_CONTROL`, `E2E_CONTROL_CENSUS`, `E2E_SEAM`). Isolated `AVKIT_APP_DATA`. `E2E_NO_LIVE_YT` via `E2E_SEAM` + `E2E_HAPPY_PATH`. Sandbox no-display → `[B]` `E2E_SANDBOX`; files still exist. | Spec 1100, 1129–1135; E2; Playwright network mocking | assertion not chained on the required locator, or un-mocked extract |
| AC-20.17 | integration | Wave0 home test updated to `DOWNLOADER_HOME` (url-input visible on `#/`). Nav/hash/transcript wave0 tests remain. | Spec 1098–1100; lock 2 | keep “no url-input” wave0 |
| AC-20.18 | unit | Audio Format control exists but hidden until `audio_only`; cookie browser/profile/file hidden until matching radio. Visible gates: Audio Only checkbox + Cookie Authentication heading. | Spec 440–446; UX2 exception | audio-format always hidden including when checked |
| AC-20.19 | unit | `STATUS_COLORS` / G30–G32: no raw hex in `className`; G30 styles on the three selects. | G30–G32; Spec 527–544 | `className="... #8be9fd"` |
| AC-20.20 | unit | G36 / anti-placeholder on `MEU20_TOUCHED`. No `test.skip` / `.only`. | G36 | skip a Red test to go green |
| AC-20.21 | integration | Playlist/channel Add uses `DownloadCreateOut.items` then invalidate `QUERY_KEY` so multiple rows appear. Do not assume one row per POST. | downloads.py 71–83 | ignore create `items` |
| AC-20.22 | integration | OpenAPI `--check` exit 0 (no `packages/api/` edits). MCP tools untouched. | G8; grouping | regenerate OpenAPI “just in case” |

### Spec Sufficiency Table

| Behavior | Classification | Resolution |
|----------|---------------|------------|
| Layout SABR → URL → table → controls | Spec | `06-gui.md` 352–401 |
| SABR states + three buttons | Spec | 404–432 |
| URL/quality/audio/cookie fields | Spec | 434–448 |
| Queue columns + statuses | Spec | 450–478 |
| Pause is processor-level | Spec | 478–501 |
| Control enablement + REST | Spec | 503–566 |
| `{ items, processor }` poll | Spec | 570–589 |
| Query v5 `refetchInterval(query)` | Research-backed | [useQuery](https://tanstack.com/query/v5/docs/framework/react/reference/useQuery) |
| Table selection | Research-backed | [row selection](https://tanstack.com/table/v8/docs/guide/row-selection) |
| Wire enums / 422 / extra forbid | Local Canon | MEU-15 schemas |
| Cookie persist via settings | Local Canon | `download.py` 406–418 + lock 4 |
| `/` is Downloader now | Local Canon | grouping Session 8 |
| apply-defaults button | Local Canon | index 30 → MEU-23 |
| Hide vs UX2 | Spec + UX2 exception | lock 5 |
| Full queue render | Spec | lock 6 |
| Palette download ids | Spec | index 16–24 |
| E2E wave 1 | Spec | 1100 |
| apiFetch 204 / dual Bearer | Local Canon | MEU-19 |
| No live extract in Wave 1 E2E | Local Canon + Research-backed | `download.py` 166–175 extract-before-persist; Playwright `page.route`; `E2E_SEAM` + `E2E_HAPPY_PATH` |
| 4A indexes absent | Local Canon | G30–G35 |
| RULE-1/2/3 | Local Canon | p6-gui-shell reflection |

### Files Modified

| File | Action | Summary |
|------|--------|---------|
| `ui/package.json` | modify | add `TABLE_PIN` |
| `ui/src/renderer/src/features/downloader/*` | new | page, table, hook, controls, options, `DOWNLOAD_COMMANDS` |
| `ui/src/renderer/src/components/layout/AppShell.tsx` | modify | `PALETTE_DELIVER` always-mounted listener |
| `ui/src/renderer/src/router.tsx` | modify | `/` → `DownloaderPage` |
| `ui/src/renderer/src/registry/commandRegistry.ts` | modify | `DOWNLOAD_PALETTE_IDS` + events (no `apiFetch`) |
| `ui/src/renderer/src/styles.css` | modify | `STATUS_COLORS` tokens |
| `ui/tests/unit/downloader-*.test.ts` | new | AC-20.* |
| `ui/tests/unit/shell-home.test.ts` | modify | `SUPERSEDED_19` → `DOWNLOADER_HOME` |
| `ui/tests/unit/command-palette.test.ts` | modify | allow `DOWNLOAD_PALETTE_IDS` |
| `ui/tests/e2e/test-ids.ts` | modify | WAVE1 + EXTRA |
| `ui/tests/e2e/launch.test.ts` | modify | home is downloader form |
| `ui/tests/e2e/download-queue.test.ts` | new | `E2E_CASES` (6) + `E2E_SEAM` |
| `ui/tests/e2e/fixtures/` | new | `E2E_SEAM` JSON envelopes |
| `docs/BUILD_PLAN.md` | modify via `meu_status.py` | bind MEU-20; `HUB_NEXT_AFTER` |
| `GROUPING_FILE` | modify at H2 | `GROUPING_DONE_MARK` after exec `approved` only |
| `docs/execution/plans/2026-08-20-p6-gui-downloader/assert-*.ps1` | new | `RED_ORACLE_CHECK`, `HANDOFF_MARKER_CHECK`, `E2E_CONTROL_CENSUS` |

---

## Out of Scope

| Item | Kind | Deferred-to MEU | Basis |
|------|------|-----------------|-------|
| Transcript page | deferred | MEU-21 | grouping Session 9; matrix 6.3 |
| TTS / models page | deferred | MEU-22 | grouping Session 10; matrix 6.4 |
| Settings / HelpCards / `download:apply_quality_pending` / `download:browse_path` / cookie-path Settings browse | deferred | MEU-23 | grouping Session 11; `gui-actions-index.md` 30–31, 61 |
| PyInstaller / NSIS | deferred | MEU-24, MEU-25 | grouping Session 12 |
| Rewrite FastAPI routers / OpenAPI routes | out-of-scope | — | grouping Session 8; MEU-15 approved |
| Rewrite MCP tools | out-of-scope | — | MEU-17/18 approved |
| SSE / OCR / multi-file TTS / MCP Guard | out-of-scope | — | `06-gui.md` 1158–1167 |
| Invent new MEU IDs | out-of-scope | — | grouping §4 |
| Live yt-dlp extract in agent E2E | out-of-scope | — | Local Canon `download.py` 166–175; Research-backed Playwright network mocking; substitute `E2E_SEAM` + `E2E_HAPPY_PATH` |
| `boot()` → `resolveBootIdentity` mutation test | out-of-scope | — | p6-gui-shell exec r2 Residual Risk (identity call-site); not in `06-gui.md` §Downloader; optional MEU-19 hardening only |

---

## BUILD_PLAN.md Audit

This project **does** update the hub: bind MEU-20 `execution_plan` to `PLAN_FOLDER`; add `PLAN_FOLDER_SLASH` to phase `"6"` **without removing** `PRIOR_PLAN_SLASH`; rewrite `HUB_NEXT_FIELD` to `HUB_NEXT_AFTER`; preserve Session 1–7 links. Do not hand-edit AUTOGEN tables.

```powershell
rtk proxy uv run python -c "from pathlib import Path; import re; import sys; from tools.meu_status.model import load, get_meu; PLAN='docs/execution/plans/2026-08-20-p6-gui-downloader'; SLASH=PLAN+'/'; PRIOR='docs/execution/plans/2026-08-19-p6-gui-shell/'; NEXT='/create-plan p6-gui-transcript'; MEUS=('MEU-20',); data=load(); p6=next(p for p in data['phases'] if str(p['id'])=='6'); eps=list(p6.get('execution_plans') or []); SLASH not in eps and sys.exit('phase 6 missing PLAN_FOLDER_SLASH'); PRIOR not in eps and sys.exit('phase 6 missing PRIOR_PLAN_SLASH'); miss=next((k for k in MEUS if get_meu(data,k) is None), None); miss is not None and sys.exit('missing '+miss); wrong=next((k for k in MEUS if get_meu(data,k).get('execution_plan')!=PLAN), None); wrong is not None and sys.exit(wrong+' execution_plan='+str(get_meu(data,wrong).get('execution_plan'))); hub=Path('docs/BUILD_PLAN.md').read_text(encoding='utf-8'); hits=re.findall('Next:\\s+'+chr(96)+'([^'+chr(96)+']+)'+chr(96), hub); len(hits)!=1 and sys.exit('hub Next field count='+str(len(hits))); hits[0]!=NEXT and sys.exit('hub Next='+hits[0]); print('PASS: SSOT_PLAN_BOUND')" *> C:/Temp/av-kit/ssot-plan-bound.txt; $code=$LASTEXITCODE; Get-Content C:/Temp/av-kit/ssot-plan-bound.txt; exit $code
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
rtk proxy pwsh -NoProfile -File docs/execution/plans/2026-08-20-p6-gui-downloader/assert-handoff-markers.ps1 *> C:/Temp/av-kit/handoff-check.txt; $code=$LASTEXITCODE; Get-Content C:/Temp/av-kit/handoff-check.txt; exit $code
```

### 5. E2E control census + wave 0 remaining + wave 1
```powershell
rtk proxy pwsh -NoProfile -File docs/execution/plans/2026-08-20-p6-gui-downloader/assert-e2e-control-census.ps1 *> C:/Temp/av-kit/e2e-control-census.txt; $code=$LASTEXITCODE; if ($code -ne 0) { Get-Content C:/Temp/av-kit/e2e-control-census.txt; exit $code }; rtk proxy pwsh -NoProfile -Command { Push-Location ui; npm run build; if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }; npx playwright test launch.test.ts download-queue.test.ts console-panel.test.ts command-palette-nav.spec.ts; exit $LASTEXITCODE } *> C:/Temp/av-kit/e2e-wave1.txt; $code=$LASTEXITCODE; Get-Content C:/Temp/av-kit/e2e-wave1.txt | Select-Object -Last 40; exit $code
```

### Stop conditions

- Plan review cap 3 without `approved`
- Exec review cap 6 without `approved`
- All reviewer rungs rate-limited
- Human-decision gate
- Genuine `[B]` with receipt (E2E no-display is valid `[B]` only for the **run**)

---

## Open Questions

None that block. Locks 2–8 resolve the forks.

| Question | Option | Source | Pros | Cons | Rec |
|----------|--------|--------|------|------|-----|
| Cookie UI persist | `COOKIE_SETTINGS_PUT` | `download.py` 406–418; SettingsPutIn | downloads actually use cookies | Settings page later shows same leaves | ✅ |
| | Test-only, no PUT | index 27 is test-only | thinner page | Start ignores radios | ❌ |
| Audio format visibility | Hide until Audio Only | Spec 440; UX2 exception | matches mockup | hidden until click | ✅ |
| | Always visible disabled | UX2 default | discoverable | contradicts Spec 440 | ❌ |
| Queue paging | `RENDER_ALL_ITEMS` | Spec 521–536; no list params | matches API | G4 25/page unused | ✅ |
| | Client pageSize 25 | G4 | matches trading table rule | hides rows the summary counts | ❌ |

---

## Research References

- [TanStack Query v5 `useQuery` / `refetchInterval`](https://tanstack.com/query/v5/docs/framework/react/reference/useQuery)
- [TanStack Query v5 polling](https://tanstack.com/query/v5/docs/framework/react/guides/polling)
- [TanStack Table v8 row selection](https://tanstack.com/table/v8/docs/guide/row-selection)
- [Playwright network mocking (`page.route`)](https://playwright.dev/docs/network#network-mocking)
- [06-gui.md](../../../build-plan/06-gui.md) §Downloader
- [04-rest-api.md](../../../build-plan/04-rest-api.md) download routes
- [gui-actions-index.md](../../../build-plan/gui-actions-index.md)
- `.agent/docs/emerging-standards.md` G5, G11, G15, G20, G30–G36, E2, UX2
- zorivest `P:/zorivest/ui/package.json` (`@tanstack/react-table ^8.21.0`)
- p6-gui-shell approved plan + reflection RULE-1/2/3
