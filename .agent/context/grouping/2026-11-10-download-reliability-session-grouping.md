# 2026-11-10 Download reliability · Session grouping

> **Source:** [`docs/proposals/2026-11-10-download-logic-divergence-report.md`](../../../docs/proposals/2026-11-10-download-logic-divergence-report.md), the comparison of av-kit's YouTube download path with P:/yt-dlp_GUI. Mat's gKcOjnDJfzk download showed "Failed" with nothing in the logs while the GUI build downloaded it. Mat then reported that Check SABR shows no message and logs nothing, and that the GUI logs far more. Mat asked: "follow the process, file them and add to session grouping".
> **Generated:** 2026-11-10
> **Method:**
> - Triage filed six known issues, D-529 to D-534, each `open`, `MEU-NEW`: `DOWNLOAD-CLIENT-PIN-MISSES-WORKING-CLIENT` (P2), `DOWNLOAD-FAILED-NO-REASON` (P2), `YTDLP-NO-JS-RUNTIME` (P3), `SABR-CHECK-MISSES-CURRENT-MESSAGES` (P3), `YTDLP-LOG-TEXT-DROPPED` (P3) and `DOWNLOAD-MP3-NOT-CONVERTED` (P3). `render --check` is green (`C:/Temp/av-kit/dl-render-check.txt`).
> - Stage A: one MEU per issue, MEU-137 to MEU-142, registered in `meu-status.yaml`. `render --check` is green with 142 MEUs (`C:/Temp/av-kit/dl-meu-check.txt`). The build-plan homes are in 02 §Residuals registered 2026-11-10 and 03 §Download failure reason / §Download audio extract (residual), with matrix rows 2.6 to 2.9, 3.19 and 3.20.
> - Stage B: the MEUs are grouped into Sessions 65 to 67.
> **Origin:** av-kit copied the GUI's pinned YouTube clients. The pins left out the one client that worked for that video on that day. A failed download keeps its reason off the card and out of the Console, so neither Mat nor an agent could see why it failed.
> **Status:** Active. This is a reversible draft, not a gate. Nothing here approves a plan or authorizes execution. Mat ruled D-539 and D-540 on 2026-11-10: option A for both.
> **Parallel work:** none seen. Only the `main` worktree exists, and HEAD is `55d1289` (MEU-131). The highest decision ID in use before this file was D-528. No Session 65 or later, MEU-137 or later, or D-529 or later was claimed anywhere.

---

## 1. MEU / scope summary

| MEU | Slug | Covers (issue, report item) | Layer | Depends on |
|-----|------|-----------------------------|-------|------------|
| MEU-137 | `svc-download-failure-reason` | `DOWNLOAD-FAILED-NO-REASON`: R3, R4, R12 | service, renderer (Downloader card), logging | MEU-10, MEU-15, MEU-46, MEU-115 |
| MEU-138 | `infra-sabr-check-result` | `SABR-CHECK-MISSES-CURRENT-MESSAGES`: R8, R9, R10 | adapter (phrases), API routes (log), renderer (SABR panel) | MEU-6, MEU-10, MEU-20 |
| MEU-139 | `infra-ytdlp-log-detail` | `YTDLP-LOG-TEXT-DROPPED`: R11 | adapter logger, Console redaction, wiring (live setting), Settings switch | MEU-6, MEU-13, MEU-23, MEU-115 |
| MEU-140 | `infra-youtube-client-fallback` | `DOWNLOAD-CLIENT-PIN-MISSES-WORKING-CLIENT`: R1, R5, R7 | adapter (`_cookie_opts`, selector, `extract_info`) | MEU-6, MEU-124, MEU-137 |
| MEU-141 | `infra-ytdlp-js-runtime` | `YTDLP-NO-JS-RUNTIME`: R2 | adapter options, dependencies, `avkit-backend.spec`, Health | MEU-6, MEU-13, MEU-140 |
| MEU-142 | `svc-download-audio-extract` | `DOWNLOAD-MP3-NOT-CONVERTED`: R6 | service (`MediaPort.convert`), wiring | MEU-8, MEU-10, MEU-78, MEU-137 |

Report → MEU traceability:

| Report item | Disposition |
|-------------|-------------|
| R0 do nothing | Kept as the last option in D-539 and D-540. Rejected for the rest in D-535, because the failures are measured and silent. |
| R1 client strategy | MEU-140, decided by D-539 (ruled A) |
| R2 JS runtime and EJS | MEU-141, decided by D-540 (ruled A) |
| R3 card reason, R4 failure log, R12 job start, done and failure lines | MEU-137 |
| R5 catch-all selector | MEU-140 |
| R6 MP3 postprocessor | MEU-142. Uses `MediaPort.convert`, as the spec says, not the GUI's yt-dlp postprocessor (D-542). |
| R7 add-time check uses the download's options | MEU-140 |
| R8 phrases, R9 always show the result, R10 SABR log | MEU-138 |
| R11 debug switch, kept text field, live setting | MEU-139 |
| Report §6b: `app.log_level` is stored and read by nothing | Recorded in `YTDLP-LOG-TEXT-DROPPED`, not given its own MEU. MEU-139's plan says whether it reads the setting or leaves it. |

Build-plan homes, each an anchored section with source-labelled rows:
- [02 §SABR check result](../../../docs/build-plan/02-infrastructure.md#sabr-check-result-residual)
- [§yt-dlp log detail](../../../docs/build-plan/02-infrastructure.md#ytdlp-log-detail-residual)
- [§YouTube client fallback](../../../docs/build-plan/02-infrastructure.md#youtube-client-fallback-residual)
- [§yt-dlp JS runtime](../../../docs/build-plan/02-infrastructure.md#ytdlp-js-runtime-residual)
- [03 §Download failure reason](../../../docs/build-plan/03-service-layer.md#download-failure-reason-residual)
- [§Download audio extract](../../../docs/build-plan/03-service-layer.md#download-audio-extract-residual)

The stale SABR phrases in 02 §SABR and 06 §SABR detection sources now point to MEU-138's section.

---

## 2. Dependency graph + critical path

```
MEU-10, MEU-15, MEU-46, MEU-115 ──► MEU-137 ──┬─► MEU-140 ──► MEU-141 ──── Session 66 (140, 141)
                                              └─► MEU-142 ─────────────── Session 67 (142)
MEU-6, MEU-10, MEU-20 ─────────────► MEU-138 ──────────────────────────── Session 65 (137, 138, 139)
MEU-6, MEU-13, MEU-23, MEU-115 ────► MEU-139
```

Every prerequisite outside the batch is approved.

**Critical path:** MEU-137 → MEU-140 → MEU-141.
- MEU-140's retry has to say which attempt failed and why, through the message and log line that MEU-137 sets up.
- MEU-141 changes which clients yt-dlp picks on its own, so it lands on MEU-140's client rule and is measured against it.

**Parallel tier:** MEU-137, MEU-138 and MEU-139 depend on nothing pending. MEU-142 needs only MEU-137 and can run before or after Session 66.

**Soft order (shared files, not dependencies):**
- `youtube/adapter.py`: MEU-138 (phrases), MEU-139 (logger), MEU-140 (`_cookie_opts`, selector, `extract_info`) and MEU-141 (options).
- `DownloaderPage.tsx`: MEU-137 (card) and MEU-138 (SABR panel).
- `services/download.py`: MEU-137, MEU-138 (log lines) and MEU-142.
- The Console redaction path: MEU-137 and MEU-139.

None of the batch shares a file with Session 61 (renderer capture import) or Sessions 62 to 64 (capture and convert).

---

## 3. Recommended grouping — 3 sessions (65–67)

### Session 65 — `download-failure-visibility` (MEU-137, MEU-138, MEU-139) · P2

- **Layer / files:**
  - Service: `services/download.py`, which gets the per-cause message, the `download.started` / `download.done` / `download.failed` lines and the SABR action lines.
  - API: `api/routes/downloads.py`.
  - Adapter: `youtube/adapter.py`, which gets one phrase constant and logger lines with the text in `detail`.
  - `services/health.py` redaction, if `detail` needs anything more than Session 50 gave it.
  - `api/wiring.py`: the debug setting is read live.
  - Settings: `services/settings.py`.
  - Renderer: the `DownloaderPage.tsx` card mapping and SABR panel, and the Settings → Downloader switch.
  - Tests use a mocked `YoutubeDL` and a captured 2026.10.26 warning line, with no live YouTube.
- **Why grouped:** all three make a download's outcome visible. They share the adapter logger, the Downloader page and Session 50's redaction path. Mat hit all three on 2026-11-10: a silent Failed card, a silent Check SABR and an empty Console. The two later sessions use this session's message and log lines to show their own results.
- **Order:** MEU-137 → MEU-138 → MEU-139.
- **Cloud/local:** local (the Electron renderer tests run on the machine).
- **Token estimate:** calibrate against Session 50 `transcript-failure-reason` (MEU-115 and MEU-116: a failure message per cause through port, API, card and Console, plus the kept Console fields) and Session 55 `download-received-quality` (MEU-124: the adapter, the download service and the Downloader row).
- **Split flag:** yes, candidate. Session 50 carried two MEUs on the same kind of path; this carries three. If MEU-137's handoff passes about 50% of context, MEU-139 runs as 65b.

### Session 66 — `youtube-client-runtime` (MEU-140, MEU-141) · P2

- Adapter and packaging work.
  - The client rule from D-539 (A): yt-dlp's own client choice first, one retry on today's cookie pin, the `/best` catch-all, and the add-time extract with the download's options.
  - The runtime from D-540 (A): Deno shipped in the Windows installer and resolved like ffmpeg, `yt-dlp[default]` so the matching `yt-dlp-ejs` comes with yt-dlp, its scripts collected in `packaging/avkit-backend.spec`, and Health naming the runtime.
- The plan runs a recorded live probe on gKcOjnDJfzk and one other video as a manual check, not as part of the suite. The report's probe scripts are the starting point.
- Calibrate against Session 55 (download adapter options) and Session 51 `tts-build-capability` (a capability that depends on what the build ships, with a packaged onedir smoke).
- **Split flag:** yes. D-540 picked bundling, so MEU-141 carries installer work (fetch script, `extraResources`, `LICENSES.txt`, size check). If the session passes about 50% of context, MEU-141 runs as 66b.
- **Gate:** D-539 and D-540 were ruled on 2026-11-10. The plan probes the two unmeasured D-539 cases (a members-only video and a logged-in account) and measures Deno's size against the 500 MB budget.

### Session 67 — `download-audio-extract` (MEU-142) · P2

- Service and wiring work:
  - `DownloadService` takes `MediaPort` and converts `StandardMp3` jobs to MP3 after the download, in any cookie mode.
  - It creates no `ConversionJob` row.
  - When ffmpeg is missing, the job fails with the `FFmpegNotFoundError` message on the card, using MEU-137's path.
- Tests: one real-ffmpeg integration test on a generated clip, deselected on CI.
- Calibrate against Session 54 `convert-extract-index` (a `MediaPort` service change with real-ffmpeg tests).
- If the plan comes out small it may ride with Session 66. That is decided when Session 66 is planned.

---

## 4. Plan-creation pathway

On Mat's word, run `/create-plan` once per session, in order. Nothing is planned now, because Mat asked for filing and grouping, not a plan. Each plan re-reads the report sections its MEU covers and its 02 or 03 home.

1. `/create-plan download-failure-visibility` → MEU-137, MEU-138, MEU-139
2. `/create-plan youtube-client-runtime` → MEU-140, MEU-141. D-539 and D-540 are ruled (A).
3. `/create-plan download-audio-extract` → MEU-142

---

## 5. Prerequisite gate

- **Queue (D-538):**
  - Session 65 runs after Session 61 and before Sessions 62 to 64, because it fixes a silent failure in the released rc.3.
  - Session 66 follows Session 65.
  - Session 67 can follow Session 65 in any slot.
  - Planning and plan review are not blocked. Execution of any session waits for Mat's explicit message (`plan_to_exec_gate: human`).
- **Session 66:** Session 65 has closed (MEU-137). D-539 and D-540 were ruled on 2026-11-10.
- **Session 67:** Session 65 has closed (MEU-137).
- **Live YouTube:** the suites stay offline (02 §Testing). Any live probe a plan runs is a recorded manual check, and it never prints or stores cookie values.
- No branch or worktree; main only.

---

## 6. Session summary

| Session | Slug | MEUs | Band | Status | Plan folder |
|---------|------|------|------|--------|-------------|
| 65 | `download-failure-visibility` | MEU-137, MEU-138, MEU-139 | P2 | pending | — |
| 66 | `youtube-client-runtime` | MEU-140, MEU-141 | P2 | pending | — |
| 67 | `download-audio-extract` | MEU-142 | P2 | pending | — |

---

## 7. Token calibration sources

`metrics.md` has no token column, so these are named sessions, not numbers.

- **Session 65:** Session 50 `transcript-failure-reason`, a failure reason per cause through every layer plus the Console fields; plan review approved in round 2. Also Session 55 `download-received-quality`, the download adapter, service and Downloader row, 11,637,446 tokens in execution review round 1.
- **Session 66:** Session 55, for the adapter options. Session 51 `tts-build-capability`, for the build-dependent capability and the packaged smoke.
- **Session 67:** Session 54 `convert-extract-index`, a `MediaPort` service change with real-ffmpeg tests; its execution review took 7,859,970 tokens.

---

## 8. Open Decisions

| ID | Question | Resolution | Chosen | Source tag | Reasoning (why this; why the alternatives lost) | Human ref |
|----|----------|------------|--------|------------|--------------------------------------------------|-----------|
| D-535 | File the comparison report's findings and group them? | human | Yes. Six issues filed (D-529 to D-534) and MEU-137 to MEU-142 grouped into Sessions 65 to 67. No plan created yet. | Human-approved | Mat asked for exactly this. Leaving the findings in an untracked proposal (R0) lost: the failures are measured and silent, and a register entry is the only way /create-plan picks them up. | USER_EXPLICIT 2026-11-10 "follow the process, file them and add to session grouping" |
| D-536 | Slicing, homes and phases | autonomous | One MEU per issue. Adapter MEUs go in 02 as phase 2 (matrix 2.6 to 2.9) and service MEUs in 03 as phase 3 (3.19, 3.20), all in band P2. | Local Canon | Each issue is one logical change with its own TDD cycle. MEU-115 put a failure-reason residual in 03 as phase 3, band P2, and this follows it. Merging the card and log fix into the client fix lost: that fix waits on two open decisions, and the visibility fix should not. Two-way. | — |
| D-537 | Which MEUs share a session? | autonomous | 137, 138 and 139 in Session 65; 140 and 141 in Session 66; 142 alone in Session 67, with the option to ride with 66. Split flags on 65 and 66. | Local Canon | Session 65 shares the logger, the Downloader page and the redaction path. Session 66 shares `_cookie_opts`, and its two MEUs must be measured together, because the runtime changes yt-dlp's own client choice. MEU-142 touches only the service and wiring. One session for all six lost: Session 50 carried two MEUs of this kind, and six would be three times that. Two-way. | — |
| D-538 | Queue position | autonomous | Session 65 after Session 61 and before Sessions 62 to 64. Session 66 after 65. Session 67 after 65 in any slot. | Local Canon | These fix a silent failure in the released rc.3, and fixes go ahead of new capability (stills grouping D-503, crop grouping D-405). Session 61 is already queued and doesn't touch these files, so moving it would cost a reshuffle for nothing. Two-way: one message from Mat moves it. | — |
| D-539 | How should a download choose YouTube clients? | human | A: the first attempt sets no `player_client`, so yt-dlp picks its own clients; on a client-side error it retries once with today's cookie pin (`tv`, `web_safari`, `web`), and both attempts log. | Human-approved | Brief below (HDP run 2026-11-10). source-conflict: the copied GUI pin was local canon; the 2026-11-10 measurement and yt-dlp's maintainers contradicted it. B (one mixed list), C (pin first) and D (do nothing) lost for the reasons in the brief. Two-way. | USER_EXPLICIT 2026-11-10 "A", Mat's reply to the D-539 and D-540 briefs, which both recommended A |
| D-540 | How does yt-dlp get a JS runtime in dev and in the installed app? | human | A: ship `deno.exe` in the Windows installer, resolved like ffmpeg (setting, bundled, PATH); `yt-dlp[default]` for the solver, collected into the packaged backend; Health names the runtime; Deno's MIT notice in `LICENSES.txt`. | Human-approved | Brief below (HDP run 2026-11-10). ffmpeg (07-distribution.md:159) is the precedent. B (machine runtime only), C (Electron's Node) and D (do nothing) lost for the reasons in the brief. One-way for the installers that ship it. | USER_EXPLICIT 2026-11-10 "A", Mat's reply to the D-539 and D-540 briefs, which both recommended A |
| D-541 | SABR phrases and the check's visibility | autonomous | Match `sabr`, `missing a url`, `forcing sabr` and `po token`, case-insensitively, from one constant. Show every result with its time. Log each SABR action. | Local Canon | The GUI's own probe uses the first three (`youtube_downloader.py:3717`). `po token` covers the three old phrases. The 2026-11-10 warning line contains `SABR` and `missing a URL`. Hiding Inactive was a page detail, not a ruling. A narrower list keyed to today's exact wording lost, because that is what went stale. Two-way. | — |
| D-542 | MP3: yt-dlp postprocessor or `MediaPort.convert`? | autonomous | `MediaPort.convert` after the download, in any cookie mode. The source file is removed after a good convert, and no `ConversionJob` row is created. | Local Canon | The spec already names this path (02 §Media adapter `convert` row; 03 §Construction `MediaPort` row; 08 forbids a `ConversionJob` row). It uses the one ffmpeg resolver (MEU-78). The GUI's `FFmpegExtractAudio` lost because it is a second ffmpeg path. Removing the source matches what the GUI and yt-dlp's postprocessor do by default (no keepvideo). Two-way. | — |
| D-543 | yt-dlp log lines: what and when | autonomous | Warnings and errors always log, with the text in the kept, redacted `detail` field. Debug lines log only with the setting on. The setting is read per call, and a Settings → Downloader switch controls it. | Local Canon | Session 50 (D-247) made `detail` a kept, redacted field. The ffmpeg setting is already read live (`wiring.py:151`). The spec's Debug row already defines the setting, so a switch adds a control, not a behaviour. Warnings only behind the switch lost: the warning is the evidence a failed job needs. Two-way. | — |

### D-539: How should a download choose YouTube clients?   [source-conflict] [grouping]

**Ruled:** A, by Mat on 2026-11-10 ("A").

**Recommendation:** A. The first attempt sets no `player_client`, in either cookie mode, so yt-dlp picks its own clients. If that attempt fails with a client-side error (the reload page, no formats, SABR-only, requested format not available), av-kit retries once with today's cookie pin (`tv`, `web_safari`, `web`), which keeps the HLS path the GUI was tuned for, and logs both attempts. In the 2026-11-10 probes yt-dlp's own choice was the only setting that downloaded gKcOjnDJfzk every time, with and without Firefox cookies. Upstream moves its defaults as YouTube moves: it dropped `ios` in February 2026 and `android_vr` in August 2026. av-kit's no-cookie pin still asks for `android` and `ios`.

**Why not the others**

| Option | Pros (vs. recommendation) | Cons (vs. recommendation) | Sources |
|---|---|---|---|
| ✅ A: yt-dlp's choice first, today's cookie pin as the one retry | — | — | report §2b–2c; yt-dlp README `player_client`; yt-dlp #15876 |
| ⚠️ B: `player_client=default,web_safari`, one attempt | No retry code; yt-dlp's choice plus the HLS client in one request path | Not measured on any video, members-only included; adds a client request to every extract; mixing a custom list into yt-dlp's choice has produced broken format URLs before (#14419) | yt-dlp README (`default` keyword); yt-dlp #14419 |
| ⚠️ C: today's pin first, yt-dlp's choice as the retry (this grouping's first draft) | Videos that download today keep exactly today's path | Every video like gKcOjnDJfzk pays a failed attempt first; the no-cookie pin stays on `android` and `ios`, which need PO tokens; the pin also hides yt-dlp's "No JS runtime" warning (report §2c) | PO Token Guide; report §2c |
| ❌ D: do nothing | No change | The failure comes back per video and per request, and Check SABR, Force SABR and cookies can't route around it | `DOWNLOAD-CLIENT-PIN-MISSES-WORKING-CLIENT` |

**Precedent:** no av-kit ruling chose the pins. They were copied from P:/yt-dlp_GUI (`youtube_downloader.py:961-977`), and MEU-6 tested only that cookies select `COOKIE_EXTRACTOR_ARGS` and no cookies select `SABR_EXTRACTOR_ARGS` (`2026-08-19-p2-external-adapters-MEU-6-handoff.md:50`, AC-6.16). Adding `visionos` to the pins fixes this one video and was dropped as an option.
**Research:** Pomera (tavily, exa), 2026-11-10.
- yt-dlp README (authority): the defaults are `tv_samsung,visionos,web`, or `web_embedded,tv_samsung,web` for logged-in free accounts, and `web_embedded` is added as a fallback. `default` and `-client` let a list build on yt-dlp's choice. https://github.com/yt-dlp/yt-dlp
- yt-dlp #15876, a maintainer, February 2026 (practice): `ios` was "abandoned as a default because it was unreliable", giving HTTP 403. https://github.com/yt-dlp/yt-dlp/issues/15876
- yt-dlp #14419, a maintainer (practice): "I really have no idea why you're using any extractor args." A custom client list there produced 403 URLs. https://github.com/yt-dlp/yt-dlp/issues/14419
- PO Token Guide (authority): `android` and `ios` need a GVS PO token, and `tv` serves only DRM formats without cookies. https://github.com/yt-dlp/yt-dlp/wiki/PO-Token-Guide
- VRChat feedback on yt-dlp 2026.08.19 (practice): `android_vr` was dropped and `visionos` became a default, and a product's pinned client list had to follow. https://feedback.vrchat.com/feature-requests/p/update-to-yt-dlp-20260819

**Reversibility / risk:** two-way. A wrong choice costs one extra extract, and only on failures. Two cases were not measured: a members-only video that only the pin serves (under A it pays one failed attempt first), and a logged-in account, where yt-dlp's choice for gKcOjnDJfzk would be clients that all failed alone in §2c. The plan probes both.
**Obviousness:** the research and the measurement agree. This stays your call only because the logged-in and members-only paths are not measured, and A overturns the copied canon.
**If you do not answer:** Session 66's plan carries A as a guarded row, and its plan gate asks again.

### D-540: How does yt-dlp get a JS runtime in dev and in the installed app?   [one-way-door] [grouping]

**Ruled:** A, by Mat on 2026-11-10 ("A").

**Recommendation:** A. Ship `deno.exe` in the Windows installer next to ffmpeg, and resolve it the way ffmpeg is resolved: the setting, then the bundled file, then PATH. The dependency becomes `yt-dlp[default]`, so the `yt-dlp-ejs` version yt-dlp pins comes with it, and its scripts are collected into the packaged backend. Health names the runtime in use. yt-dlp's maintainers say the JS runtime relates to yt-dlp as ffmpeg does, and av-kit already settled that question for ffmpeg by bundling it (07-distribution.md:159). Deno is the only runtime yt-dlp enables by default, and it runs YouTube's player code with no file or network access. Without a runtime, yt-dlp keeps only a JS-less path that it says will get worse over time.

**Why not the others**

| Option | Pros (vs. recommendation) | Cons (vs. recommendation) | Sources |
|---|---|---|---|
| ✅ A: bundle Deno, resolve it like ffmpeg, `yt-dlp[default]`, Health line | — | — | yt-dlp #14404 FAQ; EJS wiki; 07-distribution.md:159-164 |
| ⚠️ B: use a runtime already on the machine, plus `yt-dlp[default]` and a Health row with install guidance (this grouping's first draft) | Adds nothing to the installer; the smallest plan | Most Windows machines have no Deno, so most installs stay on the degraded path. Node must be enabled by hand, needs version 22 or later, and yt-dlp still calls it unsandboxed. Bun is deprecated. | EJS wiki; triage D-61 (espeak: detect and guide) |
| ⚠️ C: run the solver on Electron's own Node (`process.execPath` with `ELECTRON_RUN_AS_NODE`, the D-56 pattern) | Adds no bytes; uses a runtime av-kit already ships and updates | Not proven that yt-dlp accepts the Electron executable as `node`. It runs YouTube's JS unsandboxed with the app's rights, and it works only when Electron started the backend. | grouping 2026-10-09 D-56; EJS wiki |
| ❌ D: do nothing | No change | Every extract stays on yt-dlp's JS-less path, which upstream calls deprecated | `YTDLP-NO-JS-RUNTIME`; yt-dlp #15012 |

**Precedent:**
- ffmpeg, the dependency yt-dlp itself compares the runtime to, ships in the Windows installer and is resolved setting → bundled → PATH (07-distribution.md:159-164; MEU-78, triage D-40). Its licence went into the release (D-101, ruled 2026-11-04).
- Triage D-22 (Mat, 2026-09-30) made the TTS model assets (the vocab and spaCy) managed downloads rather than bundled. I weighed that path here: it saves installer bytes but adds a fetch, checks and a UI for a file every YouTube download needs. ffmpeg is the closer precedent.
- D-61 (espeak: detect it and show install guidance) was chosen for its GPL licence. Deno is MIT, so that reason does not apply.
- D-56 already reuses Electron's Node for the MCP server.

**Research:** Pomera (tavily, exa), 2026-11-10.
- yt-dlp #14404 FAQ (authority): "The relationship between yt-dlp and the JS runtime will be analogous to … yt-dlp and ffmpeg". Deno was chosen because it is sandboxed and ships as a single portable executable. https://github.com/yt-dlp/yt-dlp/issues/14404
- EJS wiki (authority):
  - Only Deno is enabled by default, and its minimum version is now 2.3.0.
  - Node needs `--js-runtimes node` and version 22 or later, and Bun is deprecated.
  - `yt-dlp-ejs` must match the version yt-dlp pins, and `yt-dlp[default]` brings that version.
  - https://github.com/yt-dlp/yt-dlp/wiki/EJS
- Parabolic, a yt-dlp front end (practice): its 2026.5.0 release notes say "Updated bundled deno". https://flathub.org/en/apps/org.nickvision.tubeconverter
- dev.to on yt-dlp in Docker (practice): a curl-installed binary missed the EJS scripts, and `yt-dlp[default]` plus Deno fixed it. https://dev.to/nareshipme/fixing-yt-dlp-in-docker-n-challenge-ejs-scripts-deno-2x-and-the-playerclientios-cookie-trap-54d6

**Reversibility / risk:**
- A is one-way for every installer it ships in.
- It adds Deno's size to the installer and Deno's licence to `LICENSES.txt`. I did not measure the size; the plan measures it against the 500 MB budget (07-distribution.md:33, :444).
- Deno's minimum version can rise with a yt-dlp update, so the pinned Deno moves when yt-dlp does, as ffmpeg's pin does.
- B and C are two-way.

**If you do not answer:** Session 66's plan carries A as a guarded row, and its plan gate asks again.

Carry-forward: each row appears in its consuming session's reflection `### Decisions Log` with stage `grouping`. The closeout validator reads every §8 row of the declared grouping, so a session's reflection lists them all. The lines below say which rows bear on each session.

- Session 65 carries D-535, D-536, D-537, D-538, D-541 and D-543.
- Session 66 carries D-535, D-537, D-538, D-539 and D-540.
- Session 67 carries D-535, D-537 and D-542.
