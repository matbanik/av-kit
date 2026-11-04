---
project: "2026-08-21-p6-gui-settings-help"
date: "2026-08-21"
source: "docs/build-plan/06-gui.md"
meus: ["MEU-23"]
status: "approved"
template_version: "2.0"
---

# Implementation Plan: Phase 6 GUI Settings + Help

> **Project**: `2026-08-21-p6-gui-settings-help`
> **Build Plan Section(s)**: [06-gui.md](../../../build-plan/06-gui.md) §Settings (`/settings`) + §Help + Wave 4/6 E2E; [gui-actions-index.md](../../../build-plan/gui-actions-index.md) settings/help rows
> **Status**: `draft`
> **Grouping**: [2026-08-18-build-plan-session-grouping.md](../../../../.agent/context/grouping/2026-08-18-build-plan-session-grouping.md) Session 11 — MEU-23 only

---

## Goal

Replace the `/settings` `SettingsChrome` stub with a full `SettingsPage`: vertical section cards (download, transcript, TTS, console & logging, appearance, dependencies, setup readiness, MCP), leaf-key `PUT /settings/{namespace}` with client Zod `.strict()` subsets of `SettingsPutIn`, browse IPC flows, apply-to-pending, dependencies check, MCP copy/pin without token in renderer, shared `HelpCard` + four help-content modules mounted on feature pages, bidirectional `gui-actions-index` audit, and Wave 4/6 E2E. Do not rewrite FastAPI routers or MCP tools. Do not start MEU-24–25. Do not invent MEU IDs. Do not rewind MEU-26 chrome.

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
| MEU-23 | `.agent/context/handoffs/2026-08-21-p6-gui-settings-help-MEU-23-handoff.md` |

Rolling implementation review: `.agent/context/handoffs/2026-08-21-p6-gui-settings-help-implementation-critical-review.md`.

The product glob owner is named set `HANDOFF_GLOB`. Expected count is named set `HANDOFF_COUNT`.

---

## Work Packages and Context Lifecycle

`fresh_worker: none` → every non-`shared` row is `compact_continue`. Never emit `isolated`.

| ID | Work | depends_on | context_strategy | durable_outputs |
|---|---|---|---|---|
| WP-23a | MEU-23 Red (tests first): (1) AC-23.1–23.20 Vitest (`RED_TEST_TITLE` + `RED_AC_IDS` + `RED_JSON`) must pass `RED_ORACLE_CHECK` (kind `ui`) — **20** distinct failed JSON tests; (2) write `E2E_WAVE4` + `E2E_WAVE6` Playwright specs **before** Green and capture failing `E2E_RED` receipt (files exist; cases W4-* / W6-* present). Do not implement SettingsPage/HelpCard yet. | — | `compact_continue` | `C:/Temp/av-kit/fail-to-pass-meu-23-ui.txt`; `RED_JSON`; `C:/Temp/av-kit/e2e-red-meu-23.txt`; `ui/tests/e2e/settings.test.ts`; `ui/tests/e2e/help-search.spec.ts` |
| WP-23b | Green: `SETTINGS_HOME` + namespace cards + browse/apply/deps/`SETUP_READINESS`/`MCP_STATUS` + debounced leaf PUT + `HelpCard` + four `*-help-content.ts` + `HELP_PALETTE_DELIVER` + `AUDIT_*`. Add IPC `getSetupReadiness` + `getMcpAccessStatus`. Do not neutralize tests. Do not edit `packages/api/` or `mcp-server/`. Do not rewind chrome. | WP-23a | `compact_continue` | `ui/src/renderer/src/features/settings/`; `ui/src/renderer/src/components/help/`; `ui/src/main/ipc.ts`; `ui/src/main/preload.ts`; `ui/src/renderer/src/env.d.ts`; `AppShell.tsx`; `commandRegistry.ts`; feature pages; compact then re-read `task.md` |
| WP-23c | Wave 4 + Wave 6 E2E **verify green** (`E2E_CONTROL_CENSUS` enforces full `WAVE4_TESTIDS`+`WAVE4_EXTRA_TESTIDS`+`WAVE6_TESTIDS` + W4-3 `installSettingsSeam` + `__e2eSeamInstalled`; then Playwright pass or `[B]` `E2E_SANDBOX`). Isolated `AVKIT_APP_DATA`. Stub Electron dialogs when `AVKIT_E2E=1` (TTS RULE-2). | WP-23b | `compact_continue` | `C:/Temp/av-kit/e2e-control-census.txt`; `C:/Temp/av-kit/e2e-wave4-wave6.txt` |
| WP-23d | `MEU_SCOPED_GATE` after `HANDOFF_SOURCE_READ`, then canonical handoff | WP-23c | `compact_continue` | `.agent/context/handoffs/2026-08-21-p6-gui-settings-help-MEU-23-handoff.md` |
| WP-23e | Hub + SSOT: bind MEU-23; keep prior phase-6 slashes; `HUB_NEXT_AFTER`. Grouping Session 11 → complete is **H2 after exec `approved`**, not this row. | WP-23d | `shared` | `.agent/context/meu-status.yaml`; `docs/BUILD_PLAN.md` |

---

## User Review Required

None that block planning. Sourced conflicts are locked below (reviewer confirms; do not invent a third behavior):

1. **Harness gate:** `create-plan.md` §5c Cursor-default `plan_to_exec_gate=human` vs `.agent/context/harness.local.md` `reviewer-auto`. **Override wins.** After Codex `approved`, auto-continue to execution.
2. **Stub replacement:** MEU-26 shipped `SettingsChrome` (card shells, no fetch). **Lock `SETTINGS_HOME`:** route `/settings` → `SettingsPage`, not chrome-only stub. Reuse section `data-testid`s from stub where they match Spec 1105.
3. **Leaf-key PUT:** body is `{ "quality": "1080p" }` at `PUT /settings/downloader`, not dotted keys. Client Zod `.strict()` subset per namespace; extra keys → 422 `ERROR_SURFACE`. **Lock `LEAF_PUT`.**
4. **Debounce:** TTS page uses `INPUT_DEBOUNCE_MS = 300`. **Lock `DEBOUNCE_MS = 300`** for settings auto-save. Blank/unchanged leaf → no PUT.
5. **Cookie visibility:** when `cookie_mode === 'browser'`, show browser + profile fields; when `file`, show cookie file path + browse; when `none`, hide browser/profile/file rows. **Lock `COOKIE_VISIBILITY`.**
6. **MCP token never in renderer:** `copyMcpConfig` already returns `{ ok: true }` only. **Lock `MCP_STATUS`:** IPC `getMcpAccessStatus` → `{ tokenPresent: boolean }` only. Copy/pin stay on existing channel.
7. **Setup readiness producer:** Spec 1022 requires four observations. **Lock `SETUP_READINESS`:** new IPC `getSetupReadiness` → `{ descriptorPresent: boolean, portOk: boolean, modelsDirWritable: boolean }` from main (`descriptorPath` exists + parseable non-tombstone; ready `apiBase` port > 0; `fs` write probe of current `tts.models_directory` or default under app-data — never return paths/tokens). **Lock `FFMPEG_READINESS`:** FFmpeg row binds exclusively to `DEPS_GET` `ffmpeg.available` (no FastAPI rewrite). Deep-link scroll/focus to failing card. Negatives: missing descriptor ⇒ `descriptorPresent===false`; models path pointing at a non-directory file ⇒ `modelsDirWritable===false`.
8. **HelpCard collapse key:** G26 localStorage pattern `av-kit:{feature}-help:{tabKey}:state`. **Lock `HELP_COLLAPSE_KEY`.** First visit expanded; ARIA disclosure on toggle.
9. **Palette delivery:** `settings:check_deps` and `help:toggle` are Palette=yes (index 57, 72). **Lock `HELP_PALETTE_DELIVER`:** `AppShell` always-mounted listener + `SETTINGS_COMMANDS` / `HELP_COMMANDS`; no second `apiFetch` path in `commandRegistry`.
10. **4A indexes:** `docs/gui-element-reference.md`, `docs/gui-button-index.md`, `.agent/docs/gui-standards-enforcement.md` remain **absent**. Apply `06-gui.md` + G26/G30–G35 + `gui-actions-index.md`.
11. **E2E seam + census:** settings mutations that reach `apiFetch` require `__e2eSeamInstalled` fail-closed pattern. **Lock `E2E_SEAM`.** **Lock `E2E_CONTROL_CENSUS`:** `assert-e2e-control-census.ps1` enforces **all** `WAVE4_TESTIDS` + `WAVE4_EXTRA_TESTIDS` + `WAVE6_TESTIDS` and W4-3 `installSettingsSeam` + `__e2eSeamInstalled` outside string literals.
12. **E2E Red-before-Green:** Playwright `settings.test.ts` + `help-search.spec.ts` are authored in WP-23a with a failing `E2E_RED` receipt **before** Green. WP-23c is green verification + census, not first authorship.
13. **AVKIT_E2E dialogs:** extend main-process stubs so directory browse ≠ file browse when `AVKIT_E2E=1` (TTS RULE-2). Renderer seam still owns PUT proof.

**This section is content for the review loop, NOT a cue to stop now.**

---

## Named sets (PR-9 — define once)

| Name | Value | Owner |
|------|-------|-------|
| `SETTINGS_HOME` | route `/settings` component is `SettingsPage` (not `SettingsChrome` stub). `nav:settings` hashes to `/settings`. | Spec 898, 1105; AC-23.1 |
| `PAGE_FILES` | `ui/src/renderer/src/features/settings/{SettingsPage,useSettingsPage,settings-schemas,settings-commands,DownloadSettingsCard,TranscriptSettingsCard,TtsSettingsCard,ConsoleSettingsCard,AppearanceSettingsCard,DependenciesCard,SetupReadinessCard,McpAccessCard}.tsx` + `ui/src/renderer/src/components/help/{HelpCard,help-search}.tsx` + `ui/src/renderer/src/features/{downloader,transcript,tts,settings}/*-help-content.ts` + `router.tsx` + `commandRegistry.ts` + `AppShell.tsx` + `ui/src/main/{ipc.ts,preload.ts,index.ts}` + `env.d.ts` | this plan |
| `NAMESPACES` | `downloader`, `transcript`, `tts`, `app`, `ui` | Spec 973–1013 |
| `DOWNLOADER_LEAVES` | `path`, `ffmpeg_path`, `quality`, `audio_only`, `audio_format`, `cookie_mode`, `cookie_browser`, `cookie_browser_profile`, `cookie_file_path`, `archive_tracking`, `yt_dlp_debug` | Spec 979–989 |
| `TRANSCRIPT_LEAVES` | `output_dir`, `requests_per_hour`, `delay_between_requests`, `max_retries`, `retry_delay`, `batch_size`, `pause_between_batches`, `playlist_end`, `max_words_per_document` | Spec 990–998 |
| `TTS_LEAVES` | `models_directory`, `voice`, `speed`, `output_format`, `output_path`, `device`, `chunk_max_chars` (settings card only; `input_text` remains TTS-page resume) | Spec 999–1006 |
| `APP_LEAVES` | `log_level`, `log_to_file`, `console_visible` | Spec 1007–1009 |
| `UI_LEAVES` | `theme` (writable this MEU on Appearance card) | Spec 1010 |
| `LEAF_PUT` | `PUT /settings/{namespace}` body = single leaf or small strict subset; Zod `.strict()` mirrors `SettingsPutIn` fields for that namespace | Spec 975; `settings.py` |
| `QUERY_DOWNLOADER` | `['settings', 'downloader']` | this plan |
| `QUERY_TRANSCRIPT` | `['settings', 'transcript']` | this plan |
| `QUERY_TTS` | `['settings', 'tts']` | this plan |
| `QUERY_APP` | `['settings', 'app']` | this plan |
| `QUERY_UI` | `['settings', 'ui']` | this plan |
| `DEBOUNCE_MS` | `300` — shared auto-save debounce (Local Canon from TTS `INPUT_DEBOUNCE_MS`) | TTSPage.tsx; AC-23.13 |
| `BROWSE_DOWNLOAD_PATH` | action `download:browse_path` → IPC `showDirectoryDialog` → `PUT /settings/downloader` `{ path }` | index 31 |
| `BROWSE_FFMPEG` | action `settings:ffmpeg_browse` → IPC `showFileDialog` → `PUT /settings/downloader` `{ ffmpeg_path }` | index 60 |
| `BROWSE_COOKIE_FILE` | action `settings:browse_cookie_file` → IPC `showFileDialog` → `PUT /settings/downloader` `{ cookie_file_path }` | index 61 |
| `BROWSE_TRANSCRIPT_DIR` | action `settings:browse_transcript_dir` → IPC `showDirectoryDialog` → `PUT /settings/transcript` `{ output_dir }` | index 62 |
| `BROWSE_MODELS_DIR` | action `settings:browse_models_dir` → IPC `showDirectoryDialog` → `PUT /settings/tts` `{ models_directory }` | index 63 |
| `APPLY_DEFAULTS` | action `download:apply_quality_pending` → `POST /downloads/apply-defaults` (no body) | index 30; Spec 1031 |
| `COOKIE_MODES` | `none`, `browser`, `file` | Spec 915–918 |
| `COOKIE_VISIBILITY` | browser/profile visible iff `cookie_mode === 'browser'`; cookie file + browse iff `file`; all hidden iff `none` | Spec 915–918; AC-23.5 |
| `LOG_LEVELS` | `DEBUG`, `INFO`, `WARNING`, `ERROR`, `CRITICAL` | Spec 951 |
| `THEME_VALUES` | `dark`, `light` | Spec 959; `ui.theme` |
| `DEPS_GET` | `GET /health/dependencies` → yt-dlp + FFmpeg version/path rows | Spec 1021, 1032 |
| `CHECK_DEPS` | action `settings:check_deps` (Palette yes) → refetch `DEPS_GET` | index 57 |
| `READINESS_CHECKS` | four booleans: `descriptorPresent`, `portOk`, `modelsDirWritable`, `ffmpegAvailable` — deep-link scroll/focus to failing card; no secrets/paths/tokens in UI copy | Spec 1022; AC-23.11 |
| `SETUP_READINESS` | IPC `get-setup-readiness` / preload `getSetupReadiness()` → `{ descriptorPresent: boolean, portOk: boolean, modelsDirWritable: boolean }` only. Main: `existsSync(descriptorPath(appData))` + parseable non-tombstone; ready `apiBase` URL port > 0; write-probe models dir (settings leaf or default) without returning the path string. | Spec 1022; lock 7 |
| `FFMPEG_READINESS` | `ffmpegAvailable` binds to `DEPS_GET` `ffmpeg.available` only (no new REST; no FastAPI rewrite) | Spec 1021–1032; lock 7 |
| `MCP_COPY` | action `settings:copy_mcp` → `window.api.copyMcpConfig()` → `{ ok: true }` only | index 58; Spec 1023 |
| `MCP_PIN` | action `settings:pin_mcp` → `copyMcpConfig({ pinEndpoint: true })` | index 59 |
| `MCP_STATUS` | IPC channel `get-mcp-access-status` / preload `getMcpAccessStatus()` → `{ tokenPresent: boolean }` — never token value | Spec 1023; AC-23.12 |
| `MCP_MASK` | UI shows “Token present: yes/no” or equivalent masked label; never render token substring | Spec 1023; AC-23.12 negative |
| `ERROR_SURFACE` | 422/409/`ApiError` shown in-card (G15); never swallow; extra leaf → 422 not 500 | G15; AC-23.14 |
| `SETTINGS_PALETTE_IDS` | `{settings:check_deps}` | index 57 |
| `HELP_PALETTE_IDS` | `{help:toggle}` | index 72 |
| `SETTINGS_EVENTS` | `av-kit:settings:{check_deps}` | G11 |
| `HELP_EVENTS` | `av-kit:help:toggle` | G11 |
| `SETTINGS_COMMANDS` | `ui/src/renderer/src/features/settings/settings-commands.ts` | G11 |
| `HELP_COMMANDS` | handler toggles HelpCard on active route / navigates then toggles off-route | G11 |
| `HELP_PALETTE_DELIVER` | `AppShell` listener calls `HELP_COMMANDS`; same as page Help toggle button | G11; AC-23.17 |
| `HELP_CARD` | shared `HelpCard` component: ARIA disclosure + `HELP_COLLAPSE_KEY` localStorage | G26; AC-23.15 |
| `HELP_COLLAPSE_KEY` | `av-kit:{feature}-help:{tabKey}:state` where `feature` ∈ `{downloader,transcript,tts,settings}` | G26 |
| `HELP_MODULES` | `downloader-help-content.ts`, `transcript-help-content.ts`, `tts-help-content.ts`, `settings-help-content.ts` | Spec 299–304 |
| `HELP_TOPICS_MIN` | Downloader: URL types, SABR, cookies, archive, pause vs cancel. Transcript: resume, Stop→Cancelled+requeue, compile/zip, rate limits. TTS: prepare steps, voices/lang_code, model download vs load, file/paste. Settings: leaf keys, FFmpeg probe, MCP config, console | Spec 299–304; AC-23.16 |
| `AUDIT_PALETTE` | every index row with `Palette = yes` id ∈ `commandRegistry` ids | index 290; AC-23.18 |
| `AUDIT_TESTIDS` | every Phase 6 settings/help interactive control `data-testid` has index row | index 74; AC-23.19 |
| `AUDIT_REST_IPC` | every REST/IPC cell in index resolves to known FastAPI route or preload allowlist channel | index 76; AC-23.20 |
| `AUDIT_SCRIPT` | optional `ui/tests/unit/gui-actions-audit.test.ts` + required unit assertions in AC-23.18–20 | this plan |
| `WAVE4_TESTIDS` | `settings-page`, `download-settings`, `transcript-settings`, `tts-settings`, `console-settings`, `appearance-settings`, `dependencies-section` | Spec 1105 |
| `WAVE4_EXTRA_TESTIDS` | `browse-download-path-btn`, `apply-defaults-btn`, `browse-ffmpeg-btn`, `browse-cookie-file-btn`, `browse-transcript-dir-btn`, `browse-models-dir-btn`, `check-deps-btn`, `copy-mcp-btn`, `pin-mcp-btn`, `theme-dark-btn`, `theme-light-btn`, `readiness-card`, `mcp-access-card`, `mcp-token-present` | §4A; census |
| `WAVE6_TESTIDS` | `help-card`, `help-search` | Spec 1107 |
| `E2E_WAVE4` | `ui/tests/e2e/settings.test.ts` (`E2E_WAVE4_CASES`, 3 tests) | Spec 1105 |
| `E2E_WAVE6` | `ui/tests/e2e/help-search.spec.ts` (`E2E_WAVE6_CASES`, 2 tests) | Spec 1107 |
| `E2E_WAVE4_CASES` | `W4-1` `SETTINGS_HOME` nav `#/settings` + `settings-page`; `W4-2` section cards `toBeVisible` on all `WAVE4_TESTIDS`; `W4-3` `E2E_ACTUATE` browse/apply/check-deps after `E2E_SEAM_INSTALL` | Spec 1105; census |
| `E2E_WAVE6_CASES` | `W6-1` `help-card` visible on downloader (or transcript) after mount; `W6-2` `help-search` `fill` filters visible section count | Spec 1107 |
| `E2E_LOCATOR_FORM` | literal `getByTestId('<kebab-id>')` (single quotes) | E2 |
| `E2E_PER_CONTROL` | allowed method chained on same locator: `expect(page.getByTestId('id')).toBeVisible()` or `.click()` / `.fill()` | E2 |
| `E2E_SEAM_GATE` | `window.__e2eSeamInstalled === true` before settings `apiFetch` | Local Canon `api.ts` 21–27 |
| `E2E_SEAM_INSTALL` | file-level `installSettingsSeam(page)` in `settings.test.ts` — sole owner of `addInitScript`, `window.fetch =`, protected `/settings*`, `/downloads/apply-defaults`, `/health/dependencies` fulfill + 599 unhandled | downloader RULE-2 |
| `E2E_SEAM_UNHANDLED` | HTTP 599 body `E2E_SEAM_UNHANDLED` for unhandled protected URLs | downloader RULE-2 |
| `E2E_IPC_LEDGER` | `window.__e2eIpc` append on dialog/browse/copy MCP stubs | MEU-19 pattern |
| `E2E_CONTROL_CENSUS` | `assert-e2e-control-census.ps1` enforces **all** `WAVE4_TESTIDS` + `WAVE4_EXTRA_TESTIDS` + `WAVE6_TESTIDS` (**23** ids) plus W4-1/2/3 and W6-1/2 case titles; W4-3 must call `installSettingsSeam(` and reference `__e2eSeamInstalled` outside string literals | E2; §4A; lock 11 |
| `E2E_RED` | Playwright run of `settings.test.ts` + `help-search.spec.ts` **before** Green must exit nonzero (missing page controls). Receipt `C:/Temp/av-kit/e2e-red-meu-23.txt` | FIC TDD; lock 12 |
| `RED_AC_IDS` | AC-23.1–AC-23.20 (Vitest). AC-23.21–23.22 proven by E2E Red→Green, not Vitest oracle. Owner: `assert-red-oracle.ps1` ui kind + `RED_JSON`. | this plan; FIC |
| `RED_TEST_TITLE` | every AC-23.N test is a **distinct** Vitest case whose title contains exactly one `AC-23.N` | FIC tests-first |
| `RED_JSON` | `C:/Temp/av-kit/fail-to-pass-meu-23-ui.json` | Vitest json reporter |
| `BUILDER_PIN` | `—` while `fresh_worker: none` | harness.local.md |
| `GROUPING_FILE` | `.agent/context/grouping/2026-08-18-build-plan-session-grouping.md` | grouping authority |
| `GROUPING_DONE_MARK` | Progress-table row `\| 11 \| \`p6-gui-settings-help\` \| ✅ complete \|` and Session 11 heading `✅ complete`; Session 12 stays `⬜ pending`. Applied at H2 after exec `approved` only. | grouping Progress |
| `PLAN_FOLDER` | `docs/execution/plans/2026-08-21-p6-gui-settings-help` | MEU `execution_plan` |
| `PLAN_FOLDER_SLASH` | `docs/execution/plans/2026-08-21-p6-gui-settings-help/` | phase `"6"` |
| `PRIOR_PLAN_SLASHES` | `docs/execution/plans/2026-08-19-p6-gui-shell/`; `docs/execution/plans/2026-08-20-p6-gui-downloader/`; `docs/execution/plans/2026-08-20-p6-gui-zorivest-chrome/`; `docs/execution/plans/2026-08-20-p6-gui-transcript/`; `docs/execution/plans/2026-08-20-p6-gui-tts-models/` | must remain on phase `"6"` |
| `HUB_NEXT_AFTER` | `/create-plan p7-distribution` | grouping pathway #12 |
| `HUB_NEXT_FIELD` | the unique `Next: \`...\`` field in `docs/BUILD_PLAN.md` | p6 pattern |
| `EXEC_REVIEW_FILE` | `.agent/context/handoffs/2026-08-21-p6-gui-settings-help-implementation-critical-review.md` | this plan |
| `EXEC_REVIEW_TARGET` | `docs/execution/plans/2026-08-21-p6-gui-settings-help/implementation-plan.md` | exact `target_plan` |
| `EXEC_REVIEW_MAX_ROUND` | `6` | execution-review cap |
| `CHECK_EXEC_REVIEW` | `tools/check_exec_review.py` — first YAML frontmatter only; `--expected-mode implementation` | p2 Human-approved |
| `HANDOFF_TEMPLATE` | `.agent/context/handoffs/TEMPLATE.md` | closeout |
| `HANDOFF_SOURCE_READ` | `C:/Temp/av-kit/handoff-source-read-meu-23.txt` written **once** before MEU-23 handoff | p4 F4 |
| `HANDOFF_BUNDLE_MARKERS` | `Acceptance Criteria`, `CACHE BOUNDARY`, `FAIL_TO_PASS`, `Changed Files`, `Quality Gate Results`, `Commands Executed`, `## Evidence` | TEMPLATE |
| `HANDOFF_COUNT` | `1` | `HANDOFF_GLOB` |
| `HANDOFF_GLOB` | `.agent/context/handoffs/2026-08-21-p6-gui-settings-help-MEU-23-handoff.md` | this plan |
| `HANDOFF_MARKER_CHECK` | `rtk proxy pwsh -NoProfile -File docs/execution/plans/2026-08-21-p6-gui-settings-help/assert-handoff-markers.ps1` | PR-9 |
| `REFLECTION_MARKERS` | `Friction Log`, `Execution Trace`, `Pattern Extraction`, `Patterns to KEEP`, `Next Session Design Rules`, `RULE-`, `Efficiency Metrics`, `Rule Adherence`, `Instruction Coverage`, `schema: v1`, `sections:`, `loaded:`, `decisive_rules:` | p6 |
| `MEU23_TOUCHED` | `PAGE_FILES` + `ui/tests/unit` settings/help/audit + `ui/tests/e2e/settings.test.ts` + `help-search.spec.ts` + `test-ids.ts` | MEU-23 files |
| `MEU_SCOPED_GATE` | `ui`: `npx tsc --noEmit` + `npx vitest run --allowOnly=false` + `UI_ESLINT` + `npm run build`; + `SCAN_PLACEHOLDER` + `SCAN_G36` + `HANDOFF_MARKER_CHECK` + AC-23.* | AGENTS MEU gate |
| `OPENAPI_CHECK` | `packages/api/` is **not** modified → `--check` still run as no-drift proof. `-o` forbidden unless FAIL. | G8 skip-with-proof |
| `VITEST_ALLOW_ONLY` | `ui/vitest.config.ts` has `test.allowOnly: false` | G36 |
| `UI_ESLINT` | `npx eslint src/ tests/ --max-warnings 0` | G36 |
| `RED_ORACLE` | UI FAIL_TO_PASS text has allow-marker and no deny-marker **and** `RED_JSON` maps **20** distinct failed `assertionResults` 1:1 onto `RED_AC_IDS` (AC-23.1–23.20). | this plan |
| `RED_ORACLE_CHECK` | `rtk proxy pwsh -NoProfile -File docs/execution/plans/2026-08-21-p6-gui-settings-help/assert-red-oracle.ps1 -Kind ui -Receipt <text> -JsonReceipt RED_JSON` | PR-9 |
| `E2E_SANDBOX` | un-run E2E in agent sandbox → `[B]` + CI follow-up. Tests stay written and wired. Isolated `AVKIT_APP_DATA`. | known-issue policy |
| `CHROME_RULES` | RULE-1 `AVKIT_APP_DATA`; RULE-2 console/main; RULE-3 breadcrumb. Consume; do not rewind. | chrome reflection |
| `TTS_RULES` | RULE-2 stub Electron dialogs when `AVKIT_E2E=1`; RULE-3 do not rewind chrome. | tts reflection |

---

## G29 wiring checklist

| Layer | Ready? | Evidence |
|-------|--------|----------|
| FastAPI settings / apply-defaults / health dependencies | YES | MEU-16 `approved`. Do not rewrite. |
| `apiFetch` + IPC + AppShell + chrome | YES | MEU-19/20/21/22/26 `approved` |
| Settings page at `/settings` | NO → **this MEU** | grouping Session 11 |
| HelpCards on feature pages | NO → **this MEU** | grouping Session 11 |
| Bidirectional action audit | NO → **this MEU** | index 290–76 |
| PyInstaller / NSIS | NO — **later MEU** | grouping Session 12 |
| MCP server tools | YES — do not rewrite | MEU-17/18 `approved` |

---

## create-plan §4A — GUI Element Compliance

**Triggered:** Settings page + HelpCard create `<button>`, `<input>`, `<select>`, radio groups, and status rows in `ui/src/renderer/`.

| Check | Result |
|-------|--------|
| `docs/gui-element-reference.md` | **Absent** — G31–G35 + Spec tokens |
| Button/input/output indexes | **Absent** — map via table below |
| E2E written+wired | `E2E_WAVE4` + `E2E_WAVE6` + `E2E_CASES` + `E2E_PER_CONTROL` + `E2E_CONTROL_CENSUS` + `E2E_SEAM_INSTALL` + `E2E_SEAM_GATE` |
| G26–G35 / E2 | G26 **applies**: shared `HelpCard` ARIA + localStorage. G30 **applies**: quality/format/voice/device/log selects use `SelectInput`. G31 `bg-accent` only. G32 no raw hex in `className`. G34/G35 variants below. E2 = Wave 4 + 6 files. |
| G11 | `HELP_PALETTE_DELIVER` + `settings:check_deps` via `AppShell` + command modules |
| G16 | existing `CSP_IMG` — do not regress |
| G27 | Learn-more links in help content use preload external open |

Indexes remain absent. **Local fallback basis:** G34 text in `emerging-standards.md`. Card actions `md`; inline ghost `sm`. G35 tiers T0–T1.

| Element | Variant | Size | States | testid | Feedback |
|---------|---------|------|--------|--------|----------|
| Section cards | output | — | default | `download-settings`, … | T0 |
| Browse buttons | secondary | md | default/hover/focus | `browse-*-btn` | T1 IPC + PUT |
| Apply to pending | secondary | md | default/hover/disabled | `apply-defaults-btn` | T1 POST |
| Cookie mode radios | radio | sm | none/browser/file | `cookie-mode-*` | T1 PUT |
| Quality / audio / voice / format / device / log | `SelectInput` | md | G30 | per-field ids | T1 PUT |
| Theme toggle | secondary | md | dark/light selected | `theme-dark-btn`, `theme-light-btn` | T1 PUT `ui` |
| Check dependencies | secondary | md | default/loading | `check-deps-btn` | T1 GET |
| MCP copy / pin | secondary | sm | default | `copy-mcp-btn`, `pin-mcp-btn` | T1 IPC |
| Token present | output | — | yes/no masked | `mcp-token-present` | T0 IPC status |
| Readiness rows | output + link | sm | pass/fail | `readiness-card`, `readiness-*-link` | T1 scroll |
| HelpCard toggle | secondary | md | expanded/collapsed | `help-card` | T0 ARIA |
| Help search | input | md | default/focus | `help-search` | T0 filter |

---

## MEU-23 — `gui-settings-help`

### Boundary Inventory

| Surface | Schema Owner | Field Constraints | Extra-Field Policy | Invalid-input | Create/Update parity | Source |
|---------|-------------|-------------------|--------------------|---------------|----------------------|--------|
| Downloader settings PUT | client Zod `.strict()` `DOWNLOADER_LEAVES` → `SettingsPutIn` | `cookie_mode` ∈ `COOKIE_MODES`; paths strings | extra forbid | unknown leaf 422 `ERROR_SURFACE`; blank unchanged no PUT | GET hydrate same leaves | Spec 975–989 |
| Transcript settings PUT | client Zod `.strict()` `TRANSCRIPT_LEAVES` | numeric leaves ≥ 0 where applicable | extra forbid | 422 | GET/PUT parity | Spec 990–998 |
| TTS settings PUT | client Zod `.strict()` `TTS_LEAVES` | speed 0.5–2.0; format MP3/WAV; device auto/cuda/cpu/mps | extra forbid | 422 | GET/PUT parity | Spec 999–1006 |
| App settings PUT | client Zod `.strict()` `APP_LEAVES` | `log_level` ∈ `LOG_LEVELS` | extra forbid | 422 | GET/PUT parity | Spec 1007–1009 |
| UI theme PUT | client Zod `.strict()` `{ theme }` | `theme` ∈ `THEME_VALUES` | extra forbid | 422 | GET/PUT parity | Spec 1010 |
| Apply defaults | no body | 200/204 per API | n/a | `ERROR_SURFACE` on failure | n/a | Spec 1031 |
| Dependencies GET | `DependenciesOut` (committed OpenAPI) | unwrap version/path/status | ignore unknown | `ERROR_SURFACE` | GET only | Spec 1032 |
| Browse download path | IPC `show-directory-dialog` | cancel → no PUT | `.strict()` payload | deny paths unchanged (MEU-19) | n/a | index 31 |
| Browse FFmpeg / cookie file | IPC `show-file-dialog` | cancel → no PUT | `.strict()` filters | deny paths | n/a | index 60–61 |
| Browse transcript / models dir | IPC `show-directory-dialog` | cancel → no PUT | `.strict()` | deny paths | n/a | index 62–63 |
| MCP copy / pin | IPC `copy-mcp-config` | `{ pinEndpoint?: boolean }` | `.strict()` | never return token to renderer | n/a | index 58–59; ipc.ts 318–330 |
| MCP access status | IPC `get-mcp-access-status` | `{ tokenPresent: boolean }` only | `.strict()` | no token field in success value | n/a | AC-23.12 |
| Setup readiness | IPC `get-setup-readiness` | `{ descriptorPresent, portOk, modelsDirWritable }` booleans only | `.strict()` | missing descriptor → `descriptorPresent=false`; non-dir models path → `modelsDirWritable=false`; never return paths/tokens | n/a | Spec 1022; AC-23.11 |
| FFmpeg readiness | `GET /health/dependencies` | `ffmpeg.available` | OpenAPI | `ERROR_SURFACE` on GET fail | GET only | Spec 1021; `FFMPEG_READINESS` |
| Help toggle | local + optional palette event | no REST | n/a | n/a | n/a | index 72 |
| Help search | local filter over registered sections | no REST | n/a | n/a | n/a | Spec 306 |

### Acceptance Criteria

| AC | Type | Description | Source | Negative Test |
|----|------|-------------|--------|---------------|
| AC-23.1 | integration | **Control `SETTINGS_HOME`.** Observable: hash `#/settings` + `settings-page` + populated section cards (not empty stub h2-only). Chain: `router.tsx` `/settings` → `SettingsPage` → cards mount Query hooks. Negative: route still `SettingsChrome` with no `apiFetch` / PUT on edit → fail. | Spec 898, 1105; grouping Session 11 | keep stub as production page |
| AC-23.2 | integration | **Control `BROWSE_DOWNLOAD_PATH` + downloader leaves.** Observable: `browse-download-path-btn` → `showDirectoryDialog` → debounced `PUT /settings/downloader` `{ path }`; quality/audio/cookie/archive/debug leaves persist via `LEAF_PUT`. Chain: card input → Zod → `apiFetch`. Negative: dotted key `{ "downloader.path": "…" }`; browse cancel still PUTs → fail. | Spec 909–921; index 31 | dotted keys; cancel PUT |
| AC-23.3 | integration | **Control `APPLY_DEFAULTS`.** Observable: `apply-defaults-btn` → `POST /downloads/apply-defaults` exactly once per click; in-page success or `ERROR_SURFACE`. Chain: button → `apiFetch`. Negative: POST includes quality body (wrong route) → fail. | index 30; Spec 1031 | POST with `{ quality }` body |
| AC-23.4 | integration | **Control `BROWSE_FFMPEG`.** Observable: `browse-ffmpeg-btn` → `showFileDialog` → `PUT /settings/downloader` `{ ffmpeg_path }` only. Chain: IPC → debounced PUT. Negative: writes `path` leaf instead; file dialog on download path browse → fail. | index 60; Spec 913 | `{ path: … }` on ffmpeg browse |
| AC-23.5 | integration | **Control `COOKIE_VISIBILITY` + `BROWSE_COOKIE_FILE`.** Observable: mode `browser` shows `cookie-browser` + `cookie-profile`; `file` shows path + `browse-cookie-file-btn`; `none` hides all three. File browse → PUT `{ cookie_file_path }`. Chain: radio → conditional render → PUT. Negative: file fields visible when `none`; profile visible when `file` only → fail. | Spec 915–918; index 61 | wrong conditional rows |
| AC-23.6 | integration | **Control transcript leaves + `BROWSE_TRANSCRIPT_DIR`.** Observable: numeric leaves PUT to `/settings/transcript`; browse → `{ output_dir }`. Chain: `transcript-settings` card. Negative: PUT to `/settings/downloader` for `output_dir` → fail. | Spec 924–936; index 62 | wrong namespace |
| AC-23.7 | integration | **Control TTS settings + `chunk_max_chars` + `BROWSE_MODELS_DIR`.** Observable: `chunk_max_chars` editor PUT `{ chunk_max_chars }`; `browse-models-dir-btn` → `{ models_directory }`; voice/speed/format/device/output_path leaves editable. Chain: `tts-settings` card. Negative: omit chunk editor; models browse on TTS page only → fail. | Spec 938–946; index 63 | chunk only on `/tts` |
| AC-23.8 | integration | **Control `APP_LEAVES`.** Observable: log level select PUT `{ log_level }`; toggles PUT `{ log_to_file }` / `{ console_visible }`. Chain: `console-settings` card. Negative: invalid level string POSTs → fail. | Spec 949–953 | `log_level: 'TRACE'` |
| AC-23.9 | integration | **Control appearance theme.** Observable: `theme-dark-btn` / `theme-light-btn` → `PUT /settings/ui` `{ theme: 'dark'\|'light' }`; document root class updates. Chain: Appearance card. Negative: PUT `{ ui.theme: 'dark' }` dotted key → fail. | Spec 957–960 | dotted theme key |
| AC-23.10 | integration | **Control `CHECK_DEPS` + `DEPS_GET`.** Observable: `check-deps-btn` or palette `settings:check_deps` triggers `GET /health/dependencies`; rows render yt-dlp + FFmpeg status. Chain: button → Query refetch. Negative: hardcoded version strings without GET → fail. | Spec 963–967; index 57 | static version text |
| AC-23.11 | integration | **Control `SETUP_READINESS` + `FFMPEG_READINESS`.** Observable: `readiness-card` binds four rows to `getSetupReadiness()` booleans + `DEPS_GET.ffmpeg.available`; failing row deep-links to target card. Chain: `SetupReadinessCard` → preload `getSetupReadiness` → main `get-setup-readiness` (`descriptorPath` + ready port + models write probe) + Query `DEPS_GET` for FFmpeg. Negative: delete/missing descriptor ⇒ `descriptorPresent===false`; models path set to a regular file ⇒ `modelsDirWritable===false`; DOM must not contain token / `mcp-token.txt` contents / raw `backend.json` path. | Spec 1022; lock 7 | missing descriptor still shows pass; unwritable models still pass; expose secrets |
| AC-23.12 | integration | **Control MCP card + `MCP_STATUS`.** Observable: `mcp-token-present` shows masked yes/no from `getMcpAccessStatus()`; `copy-mcp-btn` / `pin-mcp-btn` invoke IPC; clipboard payload stays main-process only. Chain: status IPC + copy IPC. Negative: token string in React state/props/DOM; `copyMcpConfig` return includes token → fail. | Spec 1023; index 58–59; AC-23.12 | token in renderer state |
| AC-23.13 | integration | **Control debounced `LEAF_PUT`.** Observable: edit → wait `DEBOUNCE_MS` → single PUT with changed leaf only; blur with unchanged value → PUT count 0; empty string cleared to default may PUT once. Chain: debounce timer → Zod.strict → `apiFetch`. Negative: PUT on every keystroke; send `{}` → fail. | Local Canon `DEBOUNCE_MS`; Spec 975 | no debounce; empty PUT |
| AC-23.14 | unit | **Control `ERROR_SURFACE` for extra leaf.** Observable: client Zod rejects before fetch OR server 422 → G15 banner text; never HTTP 500 for `{ unknown_leaf: 1 }`. Chain: strict schema. Negative: silent drop of extra keys → fail. | Spec 975; G15 | strip unknown keys |
| AC-23.15 | unit | **Control shared `HelpCard` ARIA + `HELP_COLLAPSE_KEY`.** Observable: toggle sets `aria-expanded`; `aria-controls` targets panel id; localStorage key matches `av-kit:{feature}-help:{tabKey}:state`; reload restores collapse. Chain: HelpCard component. Negative: missing `aria-expanded`; key without feature prefix → fail. | G26; AC-23.15 | no ARIA; volatile key |
| AC-23.16 | unit | **Control four `HELP_MODULES`.** Observable: each module exports minimum topics from Spec Help table (≥1 assertion per topic group); mounted on downloader/transcript/tts/settings pages. Chain: content module import. Negative: settings page without `settings-help-content`; empty topics array → fail. | Spec 299–304 | missing module/topics |
| AC-23.17 | integration | **Control `help:toggle` + `HELP_PALETTE_DELIVER`.** Observable: `help:toggle` registered; palette dispatches `HELP_EVENTS`; `AppShell` listener toggles same handler as page control; off-route navigates then toggles. Negative: handler only inside one page with no AppShell listener → fail. | index 72; G11 | page-only listener |
| AC-23.18 | unit | **Control `AUDIT_PALETTE`.** Observable: unit test loads index Palette=yes ids; every id ∈ `commandRegistry` export set. Chain: static audit test. Negative: omit `settings:check_deps` or `help:toggle` → fail. | index 290; AC-23.18 | unregistered palette id |
| AC-23.19 | unit | **Control `AUDIT_TESTIDS`.** Observable: unit test maps Phase 6 settings/help testids (from `test-ids.ts` + page files) to index `id` rows. Chain: static audit. Negative: `browse-download-path-btn` without index row → fail. | index 74; AC-23.19 | orphan testid |
| AC-23.20 | unit | **Control `AUDIT_REST_IPC`.** Observable: unit test resolves each index REST/IPC cell to OpenAPI path prefix or `preload.ts` allowlist channel. Chain: static audit. Negative: invented IPC name not in allowlist → fail. | index 76; AC-23.20 | fake channel name |
| AC-23.21 | integration | Wave 4 E2E authored in Red (`E2E_RED`) then verified green (`E2E_WAVE4`, `E2E_WAVE4_CASES` W4-1…W4-3, `E2E_PER_CONTROL`, `E2E_CONTROL_CENSUS` full **23**-id enforce + W4-3 seam). Isolated `AVKIT_APP_DATA`. Sandbox no-display → `[B]` `E2E_SANDBOX`; files still exist. | Spec 1105; census script; lock 11–12 | unbound locator; census false-pass; no seam |
| AC-23.22 | integration | Wave 6 E2E authored in Red (`E2E_RED`) then verified green (`E2E_WAVE6`, `E2E_WAVE6_CASES` W6-1…W6-2, census). Help visible on feature page; search filters content. | Spec 1107; lock 12 | missing help-search actuation |

### Spec Sufficiency Table

| Behavior | Classification | Resolution |
|----------|---------------|------------|
| Settings vertical cards + leaf keys | Spec | `06-gui.md` 898–1013 |
| Dependencies / readiness / MCP cards | Spec | 1015–1023 |
| Browse + apply-defaults actions | Spec + index | index 30–31, 60–63 |
| Help per-page modules + search | Spec | 295–306 |
| Leaf PUT extra forbid → 422 | Spec + Local Canon | 975; MEU-16 `SettingsPutIn` |
| Debounce 300ms | Local Canon | TTS `INPUT_DEBOUNCE_MS` → `DEBOUNCE_MS` |
| MCP token masked + copy IPC | Spec + Local Canon | 1023; existing `copy-mcp-config` |
| Setup readiness IPC producer | Spec + Local Canon | Spec 1022; `SETUP_READINESS` + `FFMPEG_READINESS` named sets |
| `getMcpAccessStatus` boolean only | Spec + Local Canon | Spec 1023 masked yes/no; IPC returns `{ tokenPresent }` only |
| Cookie conditional fields | Spec | 915–918 |
| Palette settings/help ids | Spec | index 57, 72 |
| Bidirectional audit gate | Spec + index | 290–76 |
| Wave 4/6 E2E testids | Spec | 1105, 1107 |
| E2E fetch seam | Local Canon | downloader/TTS RULE-2; `api.ts` |
| AVKIT_E2E dialog stubs | Local Canon | TTS RULE-2; `index.ts` 276–281 |
| 4A indexes absent | Local Canon | G26/G30–G35 |
| No FastAPI/MCP rewrite | Local Canon | grouping Session 11 |

### Files Modified

| File | Action | Summary |
|------|--------|---------|
| `ui/src/renderer/src/features/settings/*` | new/modify | `SettingsPage`, cards, schemas, commands, hooks |
| `ui/src/renderer/src/components/help/*` | new | `HelpCard`, help search wiring |
| `ui/src/renderer/src/features/*/downloader-help-content.ts` (etc.) | new | four content modules |
| `ui/src/renderer/src/features/downloader/DownloaderPage.tsx` | modify | mount `HelpCard` |
| `ui/src/renderer/src/features/transcript/TranscriptPage.tsx` | modify | mount `HelpCard` |
| `ui/src/renderer/src/features/tts/TTSPage.tsx` | modify | mount `HelpCard` |
| `ui/src/renderer/src/router.tsx` | modify | `/settings` → `SettingsPage` |
| `ui/src/renderer/src/registry/commandRegistry.ts` | modify | `SETTINGS_PALETTE_IDS`, `HELP_PALETTE_IDS`, events |
| `ui/src/renderer/src/components/layout/AppShell.tsx` | modify | palette listeners for settings/help |
| `ui/src/main/ipc.ts` | modify | `get-mcp-access-status` + `get-setup-readiness` channels + schemas |
| `ui/src/main/preload.ts` | modify | `getMcpAccessStatus` + `getSetupReadiness` expose |
| `ui/src/main/index.ts` | modify | wire readiness deps (descriptorPath, models write probe); AVKIT_E2E dir vs file dialog stubs |
| `ui/src/renderer/src/env.d.ts` | modify | MCP status + setup readiness IPC typing |
| `ui/tests/unit/settings-*.test.ts` | new | AC-23.* unit/integration |
| `ui/tests/unit/help-*.test.ts` | new | AC-23.15–17 |
| `ui/tests/unit/gui-actions-audit.test.ts` | new | AC-23.18–20 |
| `ui/tests/e2e/test-ids.ts` | modify | Wave 4/6 extras |
| `ui/tests/e2e/settings.test.ts` | new | W4-1…W4-3 |
| `ui/tests/e2e/help-search.spec.ts` | new | W6-1…W6-2 |
| `docs/BUILD_PLAN.md` | modify via `meu_status.py` | bind MEU-23; `HUB_NEXT_AFTER` |
| `GROUPING_FILE` | modify at H2 | `GROUPING_DONE_MARK` after exec `approved` only |
| `docs/execution/plans/2026-08-21-p6-gui-settings-help/assert-*.ps1` | exist | `RED_ORACLE_CHECK`, `HANDOFF_MARKER_CHECK`, `E2E_CONTROL_CENSUS` |

---

## Out of Scope

| Item | Kind | Deferred-to MEU | Basis |
|------|------|-----------------|-------|
| PyInstaller / NSIS distribution | deferred | MEU-24, MEU-25 | grouping Session 12 `p7-distribution` |
| Rewrite FastAPI routers / OpenAPI routes | out-of-scope | — | grouping Session 11; MEU-16 approved |
| Rewrite MCP server tools | out-of-scope | — | MEU-17/18 approved |
| Rewind / restyle MEU-26 chrome | out-of-scope | — | chrome reflection Next Day Outline |
| Session 8c console polish | out-of-scope | — | grouping Session 8c pending |
| Invent new MEU IDs (MEU-24–25 in this session) | out-of-scope | — | grouping §4; user lock |
| Wave 7 palette-only E2E expansion | out-of-scope | — | Session 11 grouping limits E2E to Waves 4/6; Wave 7 already exists from prior sessions (`command-palette-nav.spec.ts`) |
| `gui-element-reference.md` / button index / enforcement doc | out-of-scope | — | files absent; §4A Local Canon G30–G35 |
| Live yt-dlp/FFmpeg probe in agent E2E | out-of-scope | — | `E2E_SEAM` + `[B]` sandbox policy |
| Display or edit MCP token in UI | out-of-scope | — | Spec 1023 “Never display the token” |

---

## BUILD_PLAN.md Audit

This project **does** update the hub: bind MEU-23 `execution_plan` to `PLAN_FOLDER`; add `PLAN_FOLDER_SLASH` to phase `"6"` **without removing** `PRIOR_PLAN_SLASHES`; rewrite `HUB_NEXT_FIELD` to `HUB_NEXT_AFTER`; preserve Session 1–10 links. Do not hand-edit AUTOGEN tables.

```powershell
rtk proxy uv run python -c "from pathlib import Path; import re; import sys; from tools.meu_status.model import load, get_meu; PLAN='docs/execution/plans/2026-08-21-p6-gui-settings-help'; SLASH=PLAN+'/'; PRIORS=('docs/execution/plans/2026-08-19-p6-gui-shell/','docs/execution/plans/2026-08-20-p6-gui-downloader/','docs/execution/plans/2026-08-20-p6-gui-zorivest-chrome/','docs/execution/plans/2026-08-20-p6-gui-transcript/','docs/execution/plans/2026-08-20-p6-gui-tts-models/'); NEXT='/create-plan p7-distribution'; MEUS=('MEU-23',); data=load(); p6=next(p for p in data['phases'] if str(p['id'])=='6'); eps=list(p6.get('execution_plans') or []); SLASH not in eps and sys.exit('phase 6 missing PLAN_FOLDER_SLASH'); miss_prior=next((p for p in PRIORS if p not in eps), None); miss_prior is not None and sys.exit('phase 6 missing '+miss_prior); miss=next((k for k in MEUS if get_meu(data,k) is None), None); miss is not None and sys.exit('missing '+miss); wrong=next((k for k in MEUS if get_meu(data,k).get('execution_plan')!=PLAN), None); wrong is not None and sys.exit(wrong+' execution_plan='+str(get_meu(data,wrong).get('execution_plan'))); hub=Path('docs/BUILD_PLAN.md').read_text(encoding='utf-8'); hits=re.findall('Next:\\s+'+chr(96)+'([^'+chr(96)+']+)'+chr(96), hub); len(hits)!=1 and sys.exit('hub Next field count='+str(len(hits))); hits[0]!=NEXT and sys.exit('hub Next='+hits[0]); print('PASS: SSOT_PLAN_BOUND')" *> C:/Temp/av-kit/ssot-plan-bound.txt; $code=$LASTEXITCODE; Get-Content C:/Temp/av-kit/ssot-plan-bound.txt; exit $code
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
rtk proxy pwsh -NoProfile -File docs/execution/plans/2026-08-21-p6-gui-settings-help/assert-handoff-markers.ps1 *> C:/Temp/av-kit/handoff-check.txt; $code=$LASTEXITCODE; Get-Content C:/Temp/av-kit/handoff-check.txt; exit $code
```

### 5. E2E control census + prior waves + wave 4/6
```powershell
rtk proxy pwsh -NoProfile -File docs/execution/plans/2026-08-21-p6-gui-settings-help/assert-e2e-control-census.ps1 *> C:/Temp/av-kit/e2e-control-census.txt; $code=$LASTEXITCODE; if ($code -ne 0) { Get-Content C:/Temp/av-kit/e2e-control-census.txt; exit $code }; rtk proxy pwsh -NoProfile -Command { Push-Location ui; npm run build; if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }; npx playwright test launch.test.ts download-queue.test.ts transcript-queue.test.ts tts-generate.test.ts settings.test.ts help-search.spec.ts console-panel.test.ts console-chrome.test.ts command-palette-nav.spec.ts; exit $LASTEXITCODE } *> C:/Temp/av-kit/e2e-wave4-wave6.txt; $code=$LASTEXITCODE; Get-Content C:/Temp/av-kit/e2e-wave4-wave6.txt | Select-Object -Last 40; exit $code
```

### Stop conditions

- Plan review cap 3 without `approved`
- Exec review cap 6 without `approved`
- All reviewer rungs rate-limited
- Human-decision gate
- Genuine `[B]` with receipt (E2E no-display is valid `[B]` only for the **run**)

---

## Open Questions

None that block. Locks 1–11 resolve the forks.

| Question | Option | Source | Pros | Cons | Rec |
|----------|--------|--------|------|------|-----|
| Replace stub vs extend | `SettingsPage` replaces `SettingsChrome` | user lock 2 | full spec surface | deletes stub component | ✅ |
| | Keep stub wrapper | MEU-26 | less churn | violates AC-23.1 | ❌ |
| MCP status IPC | `getMcpAccessStatus` boolean | user lock 6 | no token leak | new channel | ✅ |
| | Reuse `getToken()` in renderer | preload exists | fewer IPC | token in renderer | ❌ |
| E2E dialog stubs | Extend AVKIT_E2E dir/file paths | TTS RULE-2 | realistic browse tests | touches main | ✅ |
| | Single `sample.txt` for all | current index.ts | unchanged | wrong semantics | ❌ |

---

## Research References

- [06-gui.md](../../../build-plan/06-gui.md) §Settings, §Help, E2E Waves 4/6
- [gui-actions-index.md](../../../build-plan/gui-actions-index.md)
- [04-rest-api.md](../../../build-plan/04-rest-api.md) settings + health routes
- `.agent/docs/emerging-standards.md` G11, G15, G26, G30–G36, E2
- p6-gui-tts-models approved plan (debounce, E2E seam, palette delivery)
- p6-gui-downloader reflection RULE-2 (renderer fetch seam)
- [Playwright `page.addInitScript`](https://playwright.dev/docs/api/class-page#page-add-init-script)
- [TanStack Query v5 `useQuery`](https://tanstack.com/query/v5/docs/framework/react/reference/useQuery)
