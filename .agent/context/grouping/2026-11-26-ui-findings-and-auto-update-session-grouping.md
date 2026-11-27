# 2026-11-26 UI findings and in-app update · Session grouping

> **Source:** three messages from Mat on 2026-11-26.
> - A report of eight findings on the Capture, Download and Transcript pages, with a screenshot of the Downloader's Advanced panel and his backend console, ending "Register these issues, create session grouping and start building plans in parallel as orchestrator. Check lastest update in agentic-framework on how to orchestrate planning and executions."
> - "look at p:/zorivest and check how we are planning to do updating of the app there. Create addtional plan for integration of update feature from within the app so the user does not have to go to github realease to download and run the update but it happens automaticly. Also have setting to check updates once a week or once a month."
> - "use fleet member mini air for E2E testing during execution".
> **Generated:** 2026-11-26
> **Method:**
> - Triage (`.agent/workflows/issue-triage.md`), 2026-11-26: ten issues were registered (D-1400 to D-1409), each after the code was read for its cause. The entries were appended by a byte script, `verify --deep`, `triage --output` and `render` were rerun, and the RULE-3 line-ending check left the three register files CRLF. Receipts: `C:/Temp/av-kit/2026-11-26-triage/`.
> - Research: the yt-dlp failure in Mat's console is upstream issue 18123, fixed in stable 2026.11.23 (read 2026-11-26). Zorivest's planned updater is MEU-504 in `P:/zorivest/docs/build-plan/18-first-install-ux.md` §18.12: it is not built, checks only on request, and binds nothing here.
> - Stage A: ten MEUs, MEU-165 to MEU-174, registered through `tools/meu_status/model.py`, with homes in 09, 02, 11 and 07 and ten matrix rows (`stage_a.py`, receipt `stage-a.txt`; `meu_status.py render --check` passes).
> - Stage B: four sessions (D-1410). The triage tool's three buckets are by component; this grouping is by shared files.
> - Orchestration: `P:/agentic-framework` at `b5107b2`, `core/.agent/workflows/session-grouping.md` B2a, read 2026-11-26. D-1412 says what this repository takes from it.
> **Origin:** the 2026-11-22 grouping is fully executed and committed (Session 102, `068d64d`); 0.1.0-rc.5 is at `c0acc89`.
> **Status:** Active. This is a reversible draft, not a gate.
> **Parallel work:** only the `main` worktree exists, at `c0acc89`. The tree holds this pass's files and nothing else. This grouping claims D-1410 to D-1419, Sessions 103 to 106 and MEU-165 to MEU-174. Each plan has its own decision ids: Session 103 D-1420 to D-1459, Session 104 D-1460 to D-1499, Session 105 D-1500 to D-1539, Session 106 D-1540 to D-1599.

---

## 1. MEU / scope summary

| MEU | Slug | Covers (issue) | Layer | Depends on |
|-----|------|----------------|-------|------------|
| MEU-165 | `gui-capture-key-text` | `CAPTURE-HOTKEY-TEXT-HARDCODED` | renderer: Capture page, help texts, quick start | MEU-39, MEU-57, MEU-162 |
| MEU-166 | `svc-capture-inbox-scope` | `CAPTURE-INBOX-CHANGE-KEEPS-OLD-SHOTS` | core service, API route, renderer list | MEU-36, MEU-37, MEU-39 |
| MEU-167 | `gui-capture-zoom-scrollbars` | `CAPTURE-ZOOM-NO-SCROLLBARS` | renderer: Capture viewport | MEU-66 |
| MEU-168 | `infra-ytdlp-challenge-solver` | `YTDLP-CHALLENGE-SOLVE-FAILS` | infrastructure: lock, YouTube adapter | MEU-6, MEU-140, MEU-141 |
| MEU-169 | `cookie-test-outcome` | `DOWNLOADER-COOKIE-TEST-SILENT` | adapter, service, API schema, MCP reply, renderer | MEU-6, MEU-10, MEU-20, MEU-137 |
| MEU-170 | `infra-sabr-check-cookie-scope` | `SABR-CHECK-IGNORES-COOKIES` | adapter, service, renderer status text | MEU-138 |
| MEU-171 | `gui-entry-emphasis` | `GUI-ENTRY-SECTIONS-NO-EMPHASIS` | renderer: theme tokens, Download, Transcript, help card | MEU-20, MEU-21, MEU-23, MEU-126, MEU-162 |
| MEU-172 | `gui-downloader-advanced-affordance` | `DOWNLOADER-ADVANCED-LOOKS-LIKE-TEXT`, `DOWNLOADER-COOKIE-PROFILE-UNLABELED` | renderer: Downloader Advanced panel | MEU-171, MEU-53, MEU-159 |
| MEU-173 | `dist-update-feed` | `APP-NO-IN-APP-UPDATE` (the feed) | packaging: `electron-builder.yml`, release procedure | MEU-25, MEU-110 |
| MEU-174 | `app-in-app-update` | `APP-NO-IN-APP-UPDATE` (the app) | main process, settings in every layer, Settings page | MEU-173, MEU-13, MEU-19, MEU-23, MEU-114 |

Build-plan homes, each a `## Residuals registered 2026-11-26` section:

- [09](../../../docs/build-plan/09-screenshot-capture.md#capture-key-in-texts): MEU-165 to MEU-167, matrix 9.48 to 9.50.
- [02](../../../docs/build-plan/02-infrastructure.md#ytdlp-challenge-solver-residual): MEU-168 to MEU-170, matrix 2.10 to 2.12.
- [11](../../../docs/build-plan/11-page-layout.md#entry-section-emphasis-residual): MEU-171 and MEU-172, matrix 11.15 and 11.16.
- [07](../../../docs/build-plan/07-distribution.md#update-feed-residual): MEU-173 and MEU-174, matrix 7.10 and 7.11.

`APP-NO-IN-APP-UPDATE` is one issue delivered by two MEUs in one session: the feed files a release must carry, then the app that reads them. `MEU-172` closes two issues, both in the Downloader's Advanced panel.

Issue → disposition traceability (the ten new issues, plus every issue open, mitigated or dismissed at the start of this pass):

| Issue | Status · category | Disposition |
|-------|-------------------|-------------|
| `YTDLP-CHALLENGE-SOLVE-FAILS` | open · MEU-NEW P1 (new) | Session 104, MEU-168 (D-1407, D-1410) |
| `DOWNLOADER-COOKIE-TEST-SILENT` | open · MEU-NEW P2 (new) | Session 104, MEU-169 (D-1406, D-1410) |
| `SABR-CHECK-IGNORES-COOKIES` | open · MEU-NEW P3 (new) | Session 104, MEU-170 (D-1408, D-1410) |
| `CAPTURE-INBOX-CHANGE-KEEPS-OLD-SHOTS` | open · MEU-NEW P2 (new) | Session 103, MEU-166 (D-1401, D-1410) |
| `CAPTURE-HOTKEY-TEXT-HARDCODED` | open · MEU-NEW P3 (new) | Session 103, MEU-165 (D-1400, D-1410) |
| `CAPTURE-ZOOM-NO-SCROLLBARS` | open · MEU-NEW P3 (new) | Session 103, MEU-167 (D-1402, D-1410) |
| `APP-NO-IN-APP-UPDATE` | open · MEU-NEW P2 (new) | Session 106, MEU-173 and MEU-174 (D-1409, D-1410) |
| `GUI-ENTRY-SECTIONS-NO-EMPHASIS` | open · MEU-NEW P3 (new) | Session 105, MEU-171 (D-1403, D-1410) |
| `DOWNLOADER-ADVANCED-LOOKS-LIKE-TEXT` | open · MEU-NEW P3 (new) | Session 105, MEU-172 (D-1404, D-1410) |
| `DOWNLOADER-COOKIE-PROFILE-UNLABELED` | open · MEU-NEW P3 (new) | Session 105, MEU-172 (D-1405, D-1410) |
| `TOOLING-RUFF-TOOLS-UNCLEAN` | open · TECH-DEBT P4 | Not grouped (D-1300, D-1371): no session here changes `tools/issue_triage*` or `tools/meu_status*` |
| `CAPTURE-TEXT-PLATE-METRICS-RESIDUAL` | open · TECH-DEBT P4 | Not grouped (D-1260) |
| `CAPTURE-E2E-LAUNCH-TEARDOWN-HANG` | open · MONITORING P4 | Watch item of Session 103, whose E2E is in `capture-inbox.test.ts`. D-1197's reopen rule governs a recurrence |
| `E2E-TRANSCRIPT-SEAM-RELOAD-FLAKE` | open · MONITORING P4 | Watch item of Session 105, which runs `transcript-queue.test.ts` |
| `E2E-CLIPBOARD-PRIMER-EMPTY` | open · MONITORING P4 | Not grouped (D-1301's close bar) |
| `TRANSCRIPT-ADD-CHANNEL-422` | open · MONITORING P4 | Not grouped: not seen again |
| `CAPTURE-JOURNAL-VOLATILE` | open · DEFER P4 | Not grouped: deferred by its own ruling |
| `TTS-JA-ZH-G2P-EXTRAS` | open · DEFER P4 | Not grouped (D-229) |
| `TTS-ESPEAK-LIVE-PATH-UNVERIFIED` | open · BLOCKED P3 | Not grouped: eSpeak NG still absent (D-230; Mat's install) |
| `FFMPEG-LIBDVDCSS-BUNDLED` | open · CLOSE P2 | Not grouped: an accepted risk (D-266) |
| `MCP-ELICITATION-VSCODE-AUTO-DECLINE` | mitigated · UPSTREAM P3 | Not grouped (D-232) |
| `TOOLING-SHARED-REGISTRY-COUPLING` | mitigated · TECH-DEBT P2 | Not grouped (D-912) |
| `TTS-VOICE-SELECT-LAYOUT-JUMP` | dismissed | Not grouped: the dismissal stands. Mat's recheck of 2026-10-09 did not reproduce it (USER_EXPLICIT 2026-10-09 '1. no') |
| `TTS-PYTORCH-RUNTIME-SETTINGS-DOWNLOAD` | dismissed | Not grouped: the dismissal stands. Mat's ruling of 2026-11-04 keeps PyTorch out of installed builds, so the download is not built (D-217, D-236, D-237) |

Mat's two questions that are not defects are answered inside these issues. "I don't think it picked up the youtube cookies since it still detected sabr": Check SABR never reads the cookie settings (`SABR-CHECK-IGNORES-COOKIES`), and the console shows the Firefox cookies were very likely read, because the failure came later, in the challenge solver (`YTDLP-CHALLENGE-SOLVE-FAILS`). That is an inference from the log order, not a measurement; MEU-169 makes the app say which it was.

Items that stay Mat's: D-1200 (the FFmpeg upstream report, M-12), D-1216's host items, and a new release that ships Session 104's yt-dlp fix to installed copies. No session here tags, uploads or publishes.

---

## 2. Dependency graph + critical path

```
MEU-141 (yt-dlp JS runtime) ─► MEU-168 (yt-dlp with the solver fix)
MEU-137 (download failure reason) ─► MEU-169 (cookie test outcome)        Session 104
MEU-138 (SABR check result) ─► MEU-170 (SABR check and cookies)

MEU-162 (help quick start) ─► MEU-165 (capture key in texts)
MEU-36/37 (capture service, API) ─► MEU-166 (catalog follows the inbox)   Session 103
MEU-66 (viewport zoom) ─► MEU-167 (viewport scroll bars)

MEU-25, MEU-110 (installer, release candidate) ─► MEU-173 (update feed)
MEU-173 ─► MEU-174 (in-app update)                                        Session 106

MEU-126 (light accent contrast) ─► MEU-171 (entry section emphasis)
MEU-171 ─► MEU-172 (Downloader Advanced affordance)                       Session 105
```

**Critical path:** every prerequisite outside this grouping is approved. Inside it there are two chains, each within one session: MEU-173 before MEU-174, and MEU-171 before MEU-172. No session depends on another session's MEU.

**MEU-169 and MEU-168:** MEU-169 does not depend on MEU-168. Its tests stub yt-dlp. They are in one session because, until MEU-168 lands, a real Test Cookies run always ends in the third outcome (YouTube's check failed), so the two are proved together.

**Parallel tiers:** see `## Session Ownership`. Sessions 103 and 104 share no product file. Session 106 shares `settings-help-content.ts` with 103 and `openapi.committed.json` with 104. Session 105 shares `DownloaderPage.tsx` with 104, the quick start and help files with 103, and the Settings help images with 106.

**Shared files (every session's closeout):** `known-issues.yaml`, `meu-status.yaml` and its two rendered files, `docs/execution/metrics.md`, `current-focus.md` and this grouping's §6 rows. These are why execution is one session at a time on `main` (D-1412).

---

## 3. Recommended grouping — 4 sessions (103 to 106)

Plans are written in parallel. Execution is one session at a time, in this order: 104, 103, 106, 105. The order is by priority: Session 104 holds the P1 issue, 103 and 106 each hold a P2 issue, and 105 is P3 only and needs Mat's colour choice before it can start.

**E2E route for every session (D-1411):** execution-time Electron E2E runs on the mini-air host through `tools/e2e_remote.py` (run book `.agent/docs/e2e-remote-host.md`), not on the dev PC. Each plan's E2E rows name that command, the receipt folder it prints and the final `e2e-remote:` line as the evidence. Work that is not committed is sent as a snapshot commit that moves no ref (the `snapshot-commit.py` pattern of `docs/execution/plans/2026-11-20-e2e-devpc-clipboard/`); no branch is made. The host is shared with the Zorivest runner: a `host-busy` or `host-locked` refusal is a wait and a rerun, never a pass. Vitest, pytest and the type checks stay on the dev PC.

### Session 103 — `capture-key-inbox-scrollbars` (MEU-165, MEU-166, MEU-167) · P2

- **Layer / files:**
  - `ui/src/renderer/src/features/capture/`: `CapturePage.tsx` (the `EMPTY_STATE` literal, the inbox change handler), `capture-help-content.ts`, `CaptureViewport.tsx`, `capture-fit-map.ts`, `useCaptureCatalog.ts`.
  - `ui/src/renderer/src/features/settings/settings-help-content.ts` and `ui/src/renderer/src/components/help/quick-start.json`: the texts that name the key.
  - `packages/core/src/avkit_core/services/capture.py` (`scan_inbox`, `list_shots`); `packages/api/src/avkit_api/routes/captures.py` if the by-id rule changes.
  - Tests: `tests/unit/test_capture_service.py`, `tests/e2e/test_api_captures.py`, the Capture Vitest files, `ui/tests/e2e/capture-inbox.test.ts`.
  - Docs: 09 (the three homes; the Pan gestures row of §Viewport zoom is rewritten on delivery).
- **Covers:** `CAPTURE-HOTKEY-TEXT-HARDCODED` (D-1400), `CAPTURE-INBOX-CHANGE-KEEPS-OLD-SHOTS` (D-1401), `CAPTURE-ZOOM-NO-SCROLLBARS` (D-1402).
- **Why (value):** all three are on the Capture page and in the same E2E file, so one session reads that code once. After it, the page names the key the user set, lists the folder the user chose, and shows where a zoomed view is.
- **Acceptance direction:** the homes' Tests rows. Unit: each text with a non-default key; two inbox folders; thumb position and length. Electron E2E on mini-air: change the key and read the empty state; change the inbox and see the old shots leave; zoom and drag a thumb.
- **Plan-time choices:** the by-id rule for shots outside the current inbox (MEU-166); drawn bars or a native scroll container (MEU-167).
- **Gate:** no IPC channel, preload surface or MCP tool changes. `GET /captures` keeps its reply shape. Wheel zoom, Space+drag and middle-button drag keep their tests unchanged. `F2` stays the default key.
- **Cloud/local:** local build and unit tests; E2E on mini-air.
- **Token estimate:** calibrate against `2026-11-17-ui-small-fixes` (two GUI MEUs with Electron E2E), plus about half as much again for the service change.
- **Split flag:** no. If the plan sizes MEU-167 over half a context, it moves to its own session.
- **Run parameters:** decisions=hdp · commit_plan=false · exec_after_plan=false · commit_exec=false · push=never · authorization=b1d467ba/baee816b-ed1b-45bd-8408-64a507f3ab88

### Session 104 — `ytdlp-challenge-and-cookie-test` (MEU-168, MEU-169, MEU-170) · P1

- **Layer / files:**
  - `packages/infrastructure/pyproject.toml`, `uv.lock`: the yt-dlp version.
  - `packages/infrastructure/src/avkit_infra/youtube/adapter.py` (cookie test result, extractor arguments, the SABR check); `packages/core/src/avkit_core/services/download.py`.
  - `packages/api/src/avkit_api/schemas/downloads.py`, `routes/downloads.py`, `openapi.committed.json`; `mcp-server/src/toolsets/download.ts`.
  - `ui/src/renderer/src/features/downloader/DownloaderPage.tsx` (the Test Cookies result and busy state) and `sabr-panel.ts` (the status text).
  - Tests: the adapter, client fallback and extract option suites, `tests/e2e/test_api_downloads.py`, `downloader-page.behavior.test.ts`, `ui/tests/e2e/download-queue.test.ts`.
  - Docs: 02 (the three homes, §Cookie test), 04 §Downloads, 06 §Downloader Page.
- **Covers:** `YTDLP-CHALLENGE-SOLVE-FAILS` (D-1407), `DOWNLOADER-COOKIE-TEST-SILENT` (D-1406), `SABR-CHECK-IGNORES-COOKIES` (D-1408).
- **Why (value):** with the installed yt-dlp, extraction with the cookie clients fails for YouTube's current players. This session moves the lock to the fixed release, and makes the two buttons Mat pressed say what happened.
- **Acceptance direction:** the homes' Tests rows. A recorded real extraction of the probe video before and after the version change; a blocked run ends `INCOMPLETE VERIFICATION`. Each cookie test outcome from a stubbed yt-dlp, on the route and in the panel. No live YouTube in CI, and no cookie value in any reply, log or receipt.
- **Plan-time choices:** the version to lock and whether the `tv` variant is needed (MEU-168); the outcome field names (MEU-169); a check that uses the saved cookies or a status text that says it does not (MEU-170, with doing nothing kept as an option).
- **Gate:** the SABR phrase set, Force SABR, Clear SABR and their log lines hold. `ok` keeps its meaning. No real cookie file or browser profile is read by a test or sent to a reviewer.
- **Cloud/local:** local; the recorded extraction needs the network. E2E on mini-air.
- **Token estimate:** calibrate against `2026-11-12-youtube-client-runtime` (Session 66) for MEU-168 and `2026-11-11-download-failure-visibility` for MEU-169 and MEU-170.
- **Split flag:** no.
- **Run parameters:** decisions=hdp · commit_plan=false · exec_after_plan=false · commit_exec=false · push=never · authorization=b1d467ba/baee816b-ed1b-45bd-8408-64a507f3ab88

### Session 105 — `entry-emphasis-and-advanced` (MEU-171, MEU-172) · P3

- **Layer / files:**
  - `docs/proposals/2026-11-26-entry-emphasis-and-advanced-mockup.html`: the colour proposal, written at plan time, a local file.
  - `ui/src/renderer/src/styles.css`: the new emphasis tokens for both themes.
  - `ui/src/renderer/src/features/downloader/DownloaderPage.tsx` (URL section, Advanced trigger, open panel, Profile label), `features/transcript/TranscriptPage.tsx` (channel section), `components/help/HelpCard.tsx`.
  - `ui/src/renderer/src/assets/help/*.webp`: retaken by script.
  - Tests: a contrast test that reads `styles.css`, `downloader-page.test.ts`, `layout-primitives.test.ts` (unchanged), `ui/tests/e2e/downloader-advanced-gap.test.ts`, the help specs.
  - Docs: 11 (the two homes), 06 §Downloader Page.
- **Covers:** `GUI-ENTRY-SECTIONS-NO-EMPHASIS` (D-1403), `DOWNLOADER-ADVANCED-LOOKS-LIKE-TEXT` (D-1404), `DOWNLOADER-COOKIE-PROFILE-UNLABELED` (D-1405).
- **Why (value):** Mat asked for the place where a URL goes, and the How it works card, to draw the eye with a colour that reads for colour-blind users and is not jarring; and for the Advanced control to look like what it is. MEU-172's open panel uses MEU-171's tokens, so they are one session.
- **Acceptance direction:** the homes' Tests rows. The mockup shows each candidate in dark and light with deuteranopia, protanopia, tritanopia and greyscale views and measured contrast. Unit: the token contrast, the trigger and the label. Electron E2E on mini-air in both themes.
- **Plan-time choices:** the colour itself is Mat's, from the mockup (D-1403). The plan recommends one candidate and keeps "no change" as an option.
- **Gate:** the `Disclosure` default (AC-65.6), the queue scroll container's class string, the eight Advanced panel ids and their order, the status slot and the 16 px gap hold. No test id is removed or renamed. No raw colour in a component.
- **Cloud/local:** local; E2E and the help image retake on mini-air if the run book allows the retake there, else on the dev PC by script.
- **Token estimate:** calibrate against `2026-11-08-light-accent-contrast` (Session 56) for MEU-171 and `2026-11-17-ui-small-fixes` for MEU-172.
- **Split flag:** no.
- **Run parameters:** decisions=hdp · commit_plan=false · exec_after_plan=false · commit_exec=false · push=never · authorization=b1d467ba/baee816b-ed1b-45bd-8408-64a507f3ab88

### Session 106 — `app-auto-update` (MEU-173, MEU-174) · P2

- **Layer / files:**
  - `ui/electron-builder.yml` (the `publish` block), `ui/package.json` and its lock (`electron-updater`), the release build script and the publish checklist under `docs/releases/`.
  - `ui/src/main/`: a new updater module, `index.ts`, `ipc.ts`, `preload.ts`.
  - The new setting in every layer: `packages/core/src/avkit_core/services/settings.py`, `domain/wire.py`, `domain/settings.py`; `packages/api/src/avkit_api/schemas/settings.py`, `routes/settings.py`, `openapi.committed.json`; `ui/src/renderer/src/features/settings/settings-schemas.ts`, `SettingsPage.tsx`, `settings-help-content.ts`; `mcp-server/src/toolsets/settings.ts`.
  - Tests: unit with the updater mocked and a fake clock, `tests/unit/test_ci_workflows.py` (unchanged), an Electron E2E against a local feed, a scripted update from one built version to the next.
  - Docs: 07 (the two homes, the Auto-update row, §Goal), 06 §Settings, the README's offline statement.
- **Covers:** `APP-NO-IN-APP-UPDATE` (D-1409).
- **Why (value):** today a user learns of a new version only on the GitHub release page and installs it by hand. Mat asked for the app to do it, on a weekly or monthly check.
- **Acceptance direction:** the homes' Tests rows. The feed files match the built installer by SHA-512. The schedule fires at the set interval and not in a development run. On mini-air, an installed older build finds, downloads and installs a newer one from a local feed, and user data is kept.
- **Plan-time choices (Decision Briefs, each with doing nothing as an option):** which releases the feed offers while every release is a release candidate; the default interval, and whether the check can be turned off; when the download starts and when the app restarts; trust for an unsigned installer (the feed's SHA-512 over HTTPS, no publisher signature); the new outbound request and the offline statement. The last two are M-list items and are flagged for Mat in the plan.
- **Gate:** no tool uploads or publishes; the upload of feed files is Mat's step in the checklist. CI still uploads nothing. The app never restarts while a job runs unless the user chooses it. With no network the app works as before.
- **Cloud/local:** local builds; E2E and the update round trip on mini-air.
- **Token estimate:** calibrate against `2026-11-04-rc2-fetch-uninstall` (Session 49) for the packaging side and `2026-11-20-help-quick-start` (Session 99) for the size of a change that crosses main process, renderer and docs.
- **Split flag:** yes, a candidate. If the plan sizes the two MEUs over half a context, MEU-173 becomes its own session and runs first.
- **Run parameters:** decisions=hdp · commit_plan=false · exec_after_plan=false · commit_exec=false · push=never · authorization=b1d467ba/adec56e1-aaf3-4a5f-afb9-d2709b05614e

---

## Session Ownership

Tiers are from the framework's B2a rule: sessions in one tier share no owned path; sessions in different tiers may. This repository has no `tools/lanes.py`, so the check was done by reading the lists, not by `ownership-check`. The closeout files of §2 are owned by no session and are written by one session at a time.

```yaml
sessions:
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
  capture-key-inbox-scrollbars:
    tier: 1
    owns:
      - ui/src/renderer/src/features/capture/
      - ui/src/renderer/src/features/settings/settings-help-content.ts
      - ui/src/renderer/src/components/help/quick-start.json
      - packages/core/src/avkit_core/services/capture.py
      - packages/api/src/avkit_api/routes/captures.py
      - ui/tests/e2e/capture-inbox.test.ts
      - docs/build-plan/09-screenshot-capture.md
      - docs/execution/plans/2026-11-26-capture-key-inbox-scrollbars/
  app-auto-update:
    tier: 2
    owns:
      - ui/electron-builder.yml
      - ui/package.json
      - ui/src/main/
      - packages/core/src/avkit_core/services/settings.py
      - packages/core/src/avkit_core/domain/wire.py
      - packages/core/src/avkit_core/domain/settings.py
      - packages/api/src/avkit_api/schemas/settings.py
      - packages/api/src/avkit_api/routes/settings.py
      - openapi.committed.json
      - ui/src/renderer/src/features/settings/
      - mcp-server/src/toolsets/settings.ts
      - docs/build-plan/07-distribution.md
      - docs/releases/
      - docs/execution/plans/2026-11-26-app-auto-update/
  entry-emphasis-and-advanced:
    tier: 3
    owns:
      - ui/src/renderer/src/styles.css
      - ui/src/renderer/src/features/downloader/DownloaderPage.tsx
      - ui/src/renderer/src/features/transcript/TranscriptPage.tsx
      - ui/src/renderer/src/components/help/HelpCard.tsx
      - ui/src/renderer/src/assets/help/
      - docs/build-plan/11-page-layout.md
      - docs/proposals/2026-11-26-entry-emphasis-and-advanced-mockup.html
      - docs/execution/plans/2026-11-26-entry-emphasis-and-advanced/
```

`docs/build-plan/06-gui.md` is changed by Sessions 104, 105 and 106 in different sections; they are in different tiers. Each plan copies its `owns` list into a `## Lane Ownership` section.

---

## 4. Plan-creation pathway

Four `/create-plan` runs, written at the same time by four fresh workers, each in its own plan folder and decision-id block:

1. `/create-plan ytdlp-challenge-and-cookie-test` → MEU-168 to MEU-170, `docs/execution/plans/2026-11-26-ytdlp-challenge-and-cookie-test/`, D-1460 to D-1499.
2. `/create-plan capture-key-inbox-scrollbars` → MEU-165 to MEU-167, `docs/execution/plans/2026-11-26-capture-key-inbox-scrollbars/`, D-1420 to D-1459.
3. `/create-plan app-auto-update` → MEU-173 and MEU-174, `docs/execution/plans/2026-11-26-app-auto-update/`, D-1540 to D-1599.
4. `/create-plan entry-emphasis-and-advanced` → MEU-171 and MEU-172, `docs/execution/plans/2026-11-26-entry-emphasis-and-advanced/`, D-1500 to D-1539, plus the mockup in `docs/proposals/`.

A planner writes only inside its plan folder (and, for Session 105, the mockup). It does not change a register, a build-plan doc or another plan. Until the scoping review approves this grouping, the four drafts are provisional and are not plans: D-103 governs the order, and D-1413 was open until Mat ruled it on 2026-11-26 ('drafts stand', §8). After the approval each draft is corrected against the approved grouping, and only then goes to its own independent plan review (Codex, round cap 3). Execution starts only on Mat's word, one session at a time.

---

## 5. Prerequisite gate

- **Can begin now (planning):** all four sessions.
- **Can begin on Mat's go-ahead (execution):** Session 104, then 103, then 106. Session 105 also needs Mat's colour choice from the mockup. Session 106's plan carries two M-list briefs for Mat.
- **Blocked on:** nothing inside the repository. The mini-air host must be reachable and unlocked for E2E; the run book's refusals say when it is not.
- Work stays on `main` only, with no branch or worktree. Commits only on Mat's direction; Mat pushes.

---

## 6. Session summary

| Session | Slug | MEUs | Band | Status | Plan folder |
|---------|------|------|------|--------|-------------|
| 103 | `capture-key-inbox-scrollbars` | MEU-165, MEU-166, MEU-167 | P2 | executed (Session 103) | `docs/execution/plans/2026-11-26-capture-key-inbox-scrollbars/` |
| 104 | `ytdlp-challenge-and-cookie-test` | MEU-168, MEU-169, MEU-170 | P1 | executed (Session 104) | `docs/execution/plans/2026-11-26-ytdlp-challenge-and-cookie-test/` |
| 105 | `entry-emphasis-and-advanced` | MEU-171, MEU-172 | P3 | plan approved (round 2) | `docs/execution/plans/2026-11-26-entry-emphasis-and-advanced/` |
| 106 | `app-auto-update` | MEU-173, MEU-174 | P2 | plan approved (round 3) | `docs/execution/plans/2026-11-26-app-auto-update/` |

---

## 7. Token calibration sources

`metrics.md` has no token column, so these are named sessions, not numbers.

- **Session 103:** `2026-11-17-ui-small-fixes`.
- **Session 104:** `2026-11-12-youtube-client-runtime` (Session 66) and `2026-11-11-download-failure-visibility`.
- **Session 105:** `2026-11-08-light-accent-contrast` (Session 56) and `2026-11-17-ui-small-fixes`.
- **Session 106:** `2026-11-04-rc2-fetch-uninstall` (Session 49) and `2026-11-20-help-quick-start` (Session 99).

---

## 8. Open Decisions

| ID | Question | Resolution | Chosen | Source tag | Reasoning (why this; why the alternatives lost) | Human ref |
|----|----------|------------|--------|------------|--------------------------------------------------|-----------|
| D-1410 | How are the ten issues of 2026-11-26 scheduled? | autonomous | Four sessions, 103 to 106, grouped by shared files; ten MEUs, MEU-165 to MEU-174. Plans are written in parallel; execution is one at a time in the order 104, 103, 106, 105. | Local Canon | Handed to the agent: USER_EXPLICIT 2026-11-18 'make the decisions always the recommenations'. Options: (A) four sessions by shared files; (B) the triage tool's three buckets by component (six UI issues, two core, two infrastructure); (C) register the issues and schedule nothing. A keeps each session to one area of code and one E2E file, and puts the P1 fix first. B puts the Capture texts, the colour proposal and the cookie test in one session of six issues that share no file, and splits the cookie test from the yt-dlp fix that proves it. C leaves the P1 failure in place and does not do what Mat asked. M items: M-8 (it adds sessions). Two-way. | USER_EXPLICIT 2026-11-26 'Register these issues, create session grouping and start building plans in parallel as orchestrator' |
| D-1411 | Where does execution-time Electron E2E run? | human | On the mini-air host, through `tools/e2e_remote.py`, for every session of this grouping. Uncommitted work goes as a snapshot commit that moves no ref. | Human-approved | Mat's instruction. The run book and the snapshot pattern already exist (Sessions 96 to 100), so no new tool is needed. | USER_EXPLICIT 2026-11-26 'use fleet member mini air for E2E testing during execution' |
| D-1412 | What does this repository take from the framework's newest orchestration rules (`agentic-framework` `b5107b2`, session-grouping B2a)? | autonomous | Three things: tiers with an `owns` list per session (`## Session Ownership`), a `Run parameters` line per session, and plans written in parallel by fresh workers. Not taken: lane worktrees, lane branches, `tools/lanes.py`, automatic execution after a plan and automatic commits. | Local Canon | Handed to the agent: USER_EXPLICIT 2026-11-18. Options: (A) take the parts that fit one worktree; (B) adopt the whole lane engine here; (C) take nothing and group as on 2026-11-22. A gives parallel planning with a written record of which sessions share files, and breaks no rule. B needs branches and worktrees, which AGENTS.md §Commits and Mat's standing rule forbid outside `P:/zorivest`, and it would start execution without Mat's go-ahead, which the Claude Code profile's `plan_to_exec_gate: human` forbids. C ignores Mat's instruction to check the framework. The run parameters are therefore `commit_plan=false`, `exec_after_plan=false`, `commit_exec=false`, `push=never`. M items: none. Two-way. | USER_EXPLICIT 2026-11-26 'Check lastest update in agentic-framework on how to orchestrate planning and executions' |
| D-1413 | The four plan drafts were started on 2026-11-26 before the scoping review of this grouping had run. D-103 (Mat, 2026-10-24) puts that review before the first `/create-plan`. Do the drafts stand as inputs, or are they discarded and written again? | human | A: the drafts stand as inputs to the correction against the approved grouping. | Human-approved | Ruled by Mat on 2026-11-26, after the scoping review approved this grouping and round 1 of the four plan reviews: "drafts stand, go for 104 after the reviews finish and then execute rest as you see fit." Each draft was corrected and went to its own plan review: Session 104 approved earlier, Session 103 and Session 105 at round 2, Session 106 at round 3. The text below is the brief as it stood before the ruling, kept unchanged. Mat's to make (M-6: a departure from a Human-approved order). What happened: the agent read Mat's "start building plans in parallel" as covering a start alongside the review, and started the four planners and the review together. Scoping review round 1 (F1) found that no ruling covers that, and the finding is right: plans can be written in parallel after the review as well. Until Mat rules, D-103 governs. The review runs to its verdict first. The four drafts are provisional and are not plans: none goes to plan review or is shown as a plan before the review approves this grouping, and each is then corrected against the approved grouping. Options: (A, recommended) the drafts stand as inputs to that correction; nothing in them binds, and a draft that disagrees with the approved grouping is corrected or dropped. (B) Keep D-103 to the letter: discard the four drafts and run `/create-plan` again from nothing; it costs the planners' work a second time. (C) Change D-103 for later passes, so that drafts may always start with the review; that is a new rule and is not proposed. The review itself is owed whichever is chosen: ten new MEUs is over issue-triage Step 5.5's threshold of three (precedents D-6, D-85, D-234). It is a metered Codex dispatch; round 1 used about 3.2 million tokens, and the cost warning of PROJECT-PROFILE B2 was given in chat first. | Mat, chat, 2026-11-26: "drafts stand, go for 104 after the reviews finish and then execute rest as you see fit. Use HDP for decisions and pick recommendations as expect and do not stop for human decisions on techincal metters that are settled as primary recommendation for any of the 4 executions." |
| D-1414 | Does the pass stop after triage, as issue-triage Step 8 says? | autonomous | No. Triage, grouping and plan drafts run in one pass. The pass stops before execution. | Local Canon | Handed to the agent: USER_EXPLICIT 2026-11-18. Mat's one message ordered all three steps, and the 2026-11-22 pass did the same (D-1364). Options: (A) one pass to plan drafts; (B) stop after triage and wait; (C) register only. B and C stop work Mat asked for in the same message. M items: none. Two-way. | USER_EXPLICIT 2026-11-26 'Register these issues, create session grouping and start building plans in parallel as orchestrator' |
| D-1200 | Send FFmpeg a report on the open `-read_intervals START%` form (Session 93)? | open | | Local Canon | Carried from `2026-11-22-tray-show-and-baseline-fixes-session-grouping.md`, unchanged: Mat's to make (M-12). | — |

Carry-forward: the closeout validator reads every §8 row of this file through `--decision-source`, so a session's reflection does not restate them. Its `### Decisions Log` lists only that session's own reversible autonomous choices (HDP §6).

- Sessions 103 to 106 each carry D-1410 to D-1414.
- The issues' D-1400 to D-1409 are read from `known-issues.yaml`.

---

## 9. Scoping review criteria (D-103)

The independent MEU scoping review checks this proposal against these criteria; a blocking finding cites one of them.

**Status:** round 1 ran on 2026-11-26 (Codex, loop `s103-106-grouping-scoping-2026-11-26`): `changes_required`. F1 (AC-6): no ruling covers starting the plan drafts alongside this review; D-1413 is now open and D-103 governs. F2 (AC-5): the In-app update home's Check row required a check on request under D-1409's label; that is now a Decision Brief of the plan, and MEU-174's description is aligned. F3 (AC-1, not blocking): the two dismissed issues were missing from §1; they are added. Round 2 ran on 2026-11-26: `approved`, F1 to F3 `fixed`, no new finding (receipts `C:/Temp/av-kit/dispatch/s103-106-grouping-scoping-r1/` and `-r2/`). The approval is of this grouping. It is not Mat's ruling on D-1413, which stays open.

- **AC-1** Every open, mitigated or dismissed known issue in `known-issues.yaml` maps to exactly one MEU or a named non-MEU disposition (§1 traceability), with no issue in two MEUs. `APP-NO-IN-APP-UPDATE` is the stated exception: one issue, two MEUs in one session, feed then app.
- **AC-2** Each MEU is one coherent change with its own TDD cycle: not two unrelated changes, and not so large that one plan cannot carry it.
- **AC-3** Every MEU's dependencies are registered MEUs, no session schedules an MEU before its prerequisites, and the critical path in §2 matches `meu-status.yaml`.
- **AC-4** Sessions follow one-project-per-session and shared-file continuity; split candidates are flagged; nothing P2 waits behind P3/P4 work without a stated reason.
- **AC-5** Every build-plan row in the homes has a source label (`Spec` / `Local Canon` / `Research-backed` / `Human-approved`) that matches the recorded decision and does not widen it.
- **AC-6** No Human-approved rule is reversed or amended without a recorded human ruling.
