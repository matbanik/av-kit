# av-kit — Master Build Plan

> **Architecture**: Electron + React + FastAPI + MCP (same stack as Zorivest)
> **Strategy**: Layer-by-layer build, hexagonal dependency order
> **Spec refresh**: 2026-09-30 — nine GUI-walkthrough residuals registered (MEU-62 TTS runtime assets; MEU-63/64 TTS page; MEU-65–67 Capture toolbar, zoom, flatten-with-backup; MEU-68 MCP live audit; MEU-69 header toggles; MEU-70 Settings emphasis) from the 2026-09-30 issue triage. 2026-09-20 — Phase 6 residual MEU-61 login item registered. Phase 11 Page layout registered 2026-09-03 from the six page-layout mockups. Phase 10 Queue card UI 2026-08-28. Phase 9 Capture 2026-08-26. Phase 8 Convert 2026-08-24. Phase 1–7 remain the 2026-08-18 r4 YouTube-toolkit specs plus the 2026-09-20 login-item residual.

---

## Design thesis

av-kit is a **unified YouTube media toolkit** (download, channel transcripts, local Kokoro TTS, **local file conversion**, **local screenshot inbox**). It does **not** upload to YouTube.

SQLite stores **work records and file pointers**. Transcript bodies, audio, video, and screenshot PNGs live on disk. Typed tables (download, transcript, tts, conversion, **capture shots**) — not one STI `jobs` table. Pause on downloads is **queue-level**; transcript `Paused` is the parent-channel badge. Capture is a **catalog**, not a processor queue. `progress.json` is an optional export — resume is `TranscriptItem` rows.

Canonical field lists and “do not persist” rules: [build-plan/01-domain-layer.md](build-plan/01-domain-layer.md). This file does not win over a phase spec if they disagree.

---

## Build Phases

| Phase | Layer | Purpose | Dependencies | Spec |
|-------|-------|---------|--------------|------|
| 0 | Overview | Diagram, golden rules, entity **summary** | None | [00-overview.md](build-plan/00-overview.md) |
| 1 | Domain | Jobs, catalogs, ports, invariants | Phase 0 | [01-domain-layer.md](build-plan/01-domain-layer.md) |
| 2 | Infrastructure | Seven SQLite tables (Phase 2) + Phase 8 `conversion_jobs` + Phase 9 capture tables | Phase 1 | [02-infrastructure.md](build-plan/02-infrastructure.md) |
| 3 | Services | Queues, SABR session, compile/zip, prepare | Phase 1 + 2 | [03-service-layer.md](build-plan/03-service-layer.md) |
| 4 | REST API | `/api/v1` routes, envelopes, dual Bearer | Phase 3 | [04-rest-api.md](build-plan/04-rest-api.md) |
| 5 | MCP | Compound tools → those routes | Phase 4 | [05-mcp-server.md](build-plan/05-mcp-server.md) |
| 6 | GUI | Electron + React; **polls Phase 4 wire shapes** | Phase 4 | [06-gui.md](build-plan/06-gui.md) |
| 7 | Distribution | NSIS + onedir backend + bundled FFmpeg | Phase 4 + 5 + 6 | [07-distribution.md](build-plan/07-distribution.md) |
| 8 | Conversion | Compress / cut / extract queue; GPU FFmpeg; Convert page | Phase 1–6 (ports, chrome) | [08-video-conversion.md](build-plan/08-video-conversion.md) |
| 9 | Screenshot capture | F2 native region picker (WinForms sidecar), inbox filmstrip, annotate; tray + MCP | Phase 1–6 (ports, chrome) | [09-screenshot-capture.md](build-plan/09-screenshot-capture.md) |
| 10 | Queue card UI | Row-card queues: shared primitives, QueueCard/QueueList, re-queue widening, bulk model | Phase 6 + 8 (queue pages) | [10-queue-card-ui.md](build-plan/10-queue-card-ui.md) |
| 11 | Page layout | Page composition around the queues: shared layout primitives, queue header row, per-page zone layouts for all six pages | Phase 10 | [11-page-layout.md](build-plan/11-page-layout.md) |

Status of **code**: YouTube toolkit + Convert + Capture implemented through GUI; distribution pending. Status of **specs**: Phase 0–7 independent Codex r4 **`approved`**. Phase 8 Convert spec executed (MEU-28–33). Phase 9 Capture executed (MEU-34–40). Phase 10 queue cards executed through MEU-49 — the phase is complete. The Session 23 baseline was: “Phase 11 page layout spec exists; page composition remains scheduled for MEU-52–58.” MEU-52–56 page composition is independently approved, with MEU-57–58 still scheduled. Session 8c / MEU-27 console polish is **complete**.

## Phase Status Tracker

<!-- BEGIN AUTOGEN:meu-status:phase-tracker -->

| Phase | Status | Last Updated |
|-------|--------|--------------|
| 0 — Overview | ⚪ Not Started (Spec-only overview; no code MEUs.) | 2026-08-18 |
| 1 — Domain | ✅ Completed (MEU-1–4 approved — Session 1 p1-domain-foundation complete.) | 2026-08-19 |
| 2 — Infrastructure | ✅ Completed (MEU-5+8 persistence-io approved; MEU-6/7/9 external-adapters approved.) | 2026-08-19 |
| 3 — Service layer | 🟡 In Progress (MEU-10–13 bound to p3-services — ready_for_review pending H1. MEU-62 residual (TTS runtime assets) registered 2026-09-30. MEU-73/74/75/77/78 residuals (TTS voice assets, language runtime, device fallback, async generate, ffmpeg resolver) registered 2026-10-09. MEU-75 delivered by Session 35 tts-voice-panel. MEU-98 residual (TTS sideload load) registered 2026-10-17. MEU-115/116 (transcript failure reason, block stop), MEU-117/119/121 (TTS build capability, load order, FP16 audio) and MEU-122 (transcript source metadata) residuals registered 2026-11-04.) | 2026-11-04 |
| 4 — REST API | ✅ Completed (MEU-14–16 bound to p4-rest-api. MEU-76 residual (unhandled errors) registered 2026-10-09.) | 2026-10-09 |
| 5 — MCP server | ✅ Completed (MEU-17–18 bound to p5-mcp-server. MEU-68 approved 2026-10-01 (MCP live audit, 2026-10-01-mcp-live-audit).) | 2026-10-01 |
| 6 — GUI | 🟡 In Progress (MEU-19 p6-gui-shell; MEU-20 p6-gui-downloader; MEU-26 p6-gui-zorivest-chrome; MEU-21 p6-gui-transcript; MEU-22 p6-gui-tts-models; MEU-23 p6-gui-settings-help. MEU-61 bound to p6-gui-login-item (login-item residual). MEU-69 residual (header toggles) registered 2026-09-30. MEU-93–97 residuals (path fields, theme-reactive selects, shortcut binding, palette curation, common shortcuts) registered 2026-10-17. MEU-108 residual (ready probe guard) registered 2026-11-03. MEU-118/120/124/126 residuals (TTS device options, models folder probe, received quality, light accent contrast) registered 2026-11-04.) | 2026-11-04 |
| 7 — Distribution | 🟡 In Progress (MEU-24–25 bound to p7-distribution. MEU-71/72 residuals (MCP setup prompt, packaged ONNX TTS runtime) registered 2026-10-09. MEU-110 residual (release candidate packaging) registered 2026-11-03. MEU-113/114/125 residuals (fetch exit codes, uninstall installer copy, second release candidate) registered 2026-11-04.) | 2026-11-04 |
| 8 — Video conversion | 🟡 In Progress (MEU-28–30 bound to p8-conversion-engine. MEU-31–32 approved p8-conversion-api-mcp. MEU-33 bound to p8-conversion-gui. MEU-109 residual (output folder) registered 2026-11-03. MEU-123 residual (extract stream index) registered 2026-11-04.) | 2026-11-04 |
| 9 — Screenshot capture | 🟡 In Progress (MEU-34–36 bound to p9-capture-engine. MEU-37–38 bound to p9-capture-api-mcp. MEU-39 bound to p9-capture-gui. MEU-40 bound to p9-capture-native-picker. MEU-59 bound to p9-capture-annotate-arrow-text (arrow+text geometry residual). MEU-60 bound to p9-capture-annotate-edit (edit-until-Save residual). Session 8c / MEU-27 approved. MEU-65–67 residuals (toolbar icons, zoom, flatten-with-backup) registered 2026-09-30. MEU-80–91 residuals (icon hints, action row, text baseline, arrow geometry, file sync, size scrub, swatches, tool lock, filmstrip menu/multi-select, pixelate, eraser) registered 2026-10-09. MEU-82–84 bound to capture-render-fidelity. MEU-85–87 bound to capture-editor-options. MEU-90–91 bound to capture-new-marks. MEU-99–107 residuals (canvas history chords, resize handles, text re-edit, multi-line text, redact, copy image, style and tool flow, line and ellipse, step mark) registered 2026-10-29. MEU-111 residual (image size limit over MCP) registered 2026-11-03.) | 2026-11-03 |
| 10 — Queue card UI | ✅ Completed (MEU-41–44 bound to p10-queue-card-foundations. MEU-45–47 bound to p10-queue-card-migration. MEU-48 closed (superseded by MEU-55/MEU-56). MEU-49 bound to p10-queue-card-dnd.) | 2026-09-16 |
| 11 — Page layout | ✅ Completed (MEU-50–51 approved in Session 23 p11-layout-canon; MEU-52–54 approved in Session 24 p11-queue-pages after independent Round 3 review; Sessions 25–26 remain pending for MEU-55–58. Spec doc authored by MEU-50. MEU-63/64/70 residuals (TTS model manager, TTS text panel, Settings section emphasis) registered 2026-09-30. MEU-79 residual (TTS voice panel alignment) registered 2026-10-09; spec section and delivery by Session 35 tts-voice-panel.) | 2026-10-09 |

<!-- END AUTOGEN:meu-status:phase-tracker -->

## MEU Summary

<!-- BEGIN AUTOGEN:meu-status:summary -->

| Priority | MEU Range | Count | Completed |
|----------|-----------|:-----:|:---------:|
| P0 | MEU-1–4 (Phase 1 domain) | 4 | 4 |
| P1 | MEU-5–13 (Phases 2–3) | 9 | 9 |
| P2 | MEU-14–126 (Phases 4–11 + Phase 9 annotation residuals + Phase 6 login-item residual + 2026-09-30 walkthrough residuals MEU-62–70; 2026-10-09 triage residuals MEU-71–91; Session 31b MEU-92; 2026-10-17 triage residuals MEU-93–98; 2026-10-29 capture editor residuals MEU-99–107; 2026-11-03 release candidate residuals MEU-108–112; 2026-11-04 rc.2 triage residuals MEU-113–126) | 113 | 93 |
| **Total** | | **126** | **105 + 1🚫** |

<!-- END AUTOGEN:meu-status:summary -->

MEU-1–25 and MEU-28–33 are registered. MEU-34–36 bound to p9-capture-engine. MEU-37–38 bound to p9-capture-api-mcp. MEU-39 bound to p9-capture-gui. Session 8c / MEU-27 approved. Grouping: [.agent/context/grouping/2026-08-18-build-plan-session-grouping.md](../.agent/context/grouping/2026-08-18-build-plan-session-grouping.md). Phase 8 grouping: [2026-08-24-p8-video-conversion-session-grouping.md](../.agent/context/grouping/2026-08-24-p8-video-conversion-session-grouping.md). Phase 9 grouping: [2026-08-26-p9-screenshot-capture-session-grouping.md](../.agent/context/grouping/2026-08-26-p9-screenshot-capture-session-grouping.md). Phase 10 grouping: [2026-08-28-p10-queue-card-ui-session-grouping.md](../.agent/context/grouping/2026-08-28-p10-queue-card-ui-session-grouping.md). Phase 11 grouping: [2026-09-03-p11-page-layout-session-grouping.md](../.agent/context/grouping/2026-09-03-p11-page-layout-session-grouping.md). Phase 6 login-item residual grouping: [2026-09-20-p6-gui-login-item-session-grouping.md](../.agent/context/grouping/2026-09-20-p6-gui-login-item-session-grouping.md). MEU-41–44 bound to p10-queue-card-foundations. MEU-45–47 bound to p10-queue-card-migration. MEU-48 **closed** (superseded by MEU-55/MEU-56). MEU-49 bound to p10-queue-card-dnd. Next: No pending MEU. All 61 registered MEUs are complete (60 approved, MEU-48 closed), and `tools/meu_status.py next` is empty. Phase 11 closed with Session 26 p11-capture-settings (MEU-57–58). New work starts from triage or a new phase plan. Matrix: [build-priority-matrix.md](build-plan/build-priority-matrix.md).

---

## Locked decisions (2026-08-18)

| Topic | Decision | Spec |
|-------|----------|------|
| Persistence | Job + pointer rows; no media/transcript blobs | Phase 1 |
| Tables | Seven Phase 2 tables **plus** Phase 8 `conversion_jobs` **plus** Phase 9 `capture_shots` / `capture_requests` (no STI `jobs` table) | Phase 2 / 8 / 9 |
| Settings keys | `namespace` + leaf `key` (not dotted column) | Phase 2 / 4 / 6 |
| Pause | Download = `QueueRuntime`; transcript parent may be `Paused` | Phase 1 / 3 |
| Resume (transcripts) | `TranscriptItem` SoT; `progress.json` export only | Phase 1 / 6 |
| List APIs | `{ items, processor }` envelopes | Phase 4 / 6 |
| Auth | GUI ephemeral Bearer + stable MCP token | Phase 4 / 5 / 7 |
| Discovery | `{app_data}/backend.json` after `--port 0`; **no Electron attach**; orphan kill only after **live PID image + `--app-data` cmdline** match Electron-resolved paths; MCP reads descriptor; Copy MCP omits `AVKIT_API_BASE` | Phase 5 / 6 / 7 |
| Transcript Stop | Parent `Cancelled`; items stay `Pending`; `requeue` to retry | Phase 3 / 4 |
| Console | Ring + `GET /health/console` + stdout IPC; **no SSE** | Phase 3 / 4 / 6 |
| Ports | Canonical set in Phase 1 (incl. Filesystem, ModelCatalog, test_cookies, errors) | Phase 1 |
| MCP | Compound tools + `action`; no second URL space; no SQLite. Phase 8 adds `avkit_convert`. Phase 9 adds `avkit_capture` (`image` may return PNG bytes) | Phase 5 / 8 / 9 |
| Models | Catalog rows; `ModelDownloadRuntime` session; no `ModelFetchJob` | Phase 1 / 3 |
| FFmpeg | Bundled on Windows; setting → bundle → PATH | Phase 2 / 6 / 7 |
| Installer | NSIS; PyInstaller **onedir**; no Kokoro weights / CUDA / torch | Phase 7 |
| GUI canon | [gui-actions-index.md](build-plan/gui-actions-index.md), HelpCards, command registry | Phase 6 / 8 / 9 |
| Convert GUI | Rail **Convert** below TTS (`/convert`, Ctrl+4); Downloader-shaped queue; preset-first | Phase 8 |
| Capture GUI | Rail **Capture** below Convert (`/capture`, Ctrl+5); filmstrip + viewport; tray + F2 region picker | Phase 9 |
| Page layout | Composition only — no API, mutation or enablement change; every test id kept as keep / move / change; Capture is in scope as a **layout** even though Phase 10 excluded it as a **queue** | Phase 11 |
| Login item | Per-user `app.setLoginItemSettings` (HKCU Run + StartupApproved). Not a Windows service. OS is SoT. Default **off**. Hidden unpackaged/Linux. Pinned name `com.avkit.app`. | Phase 6 / 7 |
| Deferred | SSE, OCR Part 1, multi-file TTS, MCP Guard, Convert timeline/2-pass/size-target/Downloader handoff, Capture window/GIF/upload/macOS | Phase 6 / 7 / 8 / 9 |

---

## Phase Specs

| File | What it now specifies |
|------|------------------------|
| [00-overview.md](build-plan/00-overview.md) | Diagram, golden rules, **summary** entity/enum table |
| [01-domain-layer.md](build-plan/01-domain-layer.md) | Persist vs session, entities, ports, UoW contracts |
| [02-infrastructure.md](build-plan/02-infrastructure.md) | Columns, repos, yt-dlp/SABR/transcript/Kokoro/HF |
| [03-service-layer.md](build-plan/03-service-layer.md) | Workers, rate limits, compile/zip, prepare steps |
| [04-rest-api.md](build-plan/04-rest-api.md) | Full route index, 422/409, wire enums |
| [05-mcp-server.md](build-plan/05-mcp-server.md) | `avkit_download` / `_transcript` / `_tts` / `_models` / `_settings` / `_health` |
| [06-gui.md](build-plan/06-gui.md) | Pages, E2E waves, discovery/IPC, **API wiring** |
| [07-distribution.md](build-plan/07-distribution.md) | NSIS, onedir, `backend.json`, dual tokens, bundled FFmpeg |
| [08-video-conversion.md](build-plan/08-video-conversion.md) | ConversionJob, GPU FFmpeg, `/conversions`, `avkit_convert`, Convert page |
| [09-screenshot-capture.md](build-plan/09-screenshot-capture.md) | CaptureShot, tray/F2 region picker, `/captures`, `avkit_capture`, Capture page |
| [10-queue-card-ui.md](build-plan/10-queue-card-ui.md) | QueueCard/QueueList, status token table, kebab + bulk model, re-queue contract |
| [11-page-layout.md](build-plan/11-page-layout.md) | Zone model, shared layout primitives, queue header row, per-page composition for all six pages, locked mockup decisions |
| [gui-actions-index.md](build-plan/gui-actions-index.md) | Every button/action id, palette flag, REST/IPC |

---

## Golden Rules

1. **Never import infrastructure from domain** — ports in core; adapters in infra
2. **TDD** — tests first; do not neutralize tests
3. **No placeholders** — no `TODO` / `NotImplementedError` on `[x]` rows
4. **Same framework as Zorivest** — Electron spawn, UoW, ErrorEnvelope, toolset registry; **check Zorivest before inventing GUI chrome** (command palette, help, button/action tracking)
5. **Inspiration is intent, not code** — rewrite against the FIC; do not paste source-app GUI code
6. **Job records, not a media library** — Phase 1 persistence rules
7. **Phase spec wins** — if `BUILD_PLAN.md` or DESIGN_PROPOSAL §5 disagrees with Phase 1–7, update the summary; do not silently re-widen the schema

---

## Inspiration Files

Functional intent (not copy-paste). Phase specs must still cover these behaviors unless a spec **explicitly defers** them.

| File | Module | Intent still owed |
|------|--------|-------------------|
| [APPLICATION_PURPOSE.md](_inspiration/APPLICATION_PURPOSE.md) | All | Three modules + MCP; &lt;3s UI; &lt;500MB without models |
| [DESIGN_PROPOSAL.md](_inspiration/DESIGN_PROPOSAL.md) | All | Hexagonal + SQLite; archive table (now `DownloadArchiveEntry`) |
| [_downloader_pseudo_logic.md](_inspiration/_downloader_pseudo_logic.md) | Downloader | URL types, SABR, cookies, 8 statuses, archive skip |
| [_transcript_pseudo_logic.md](_inspiration/_transcript_pseudo_logic.md) | Transcript | Channel batch, rate limits, compile, zip, resume |
| [_tts_pseudo_logic.md](_inspiration/_tts_pseudo_logic.md) | TTS | Voices, speed, model browse/download/load |
| [_text_cleanup_pseudo_logic.md](_inspiration/_text_cleanup_pseudo_logic.md) | TTS | 10-step normalize; **OCR Part 1 deferred** |
| [_kokoro_production_settings.md](_inspiration/_kokoro_production_settings.md) | TTS | lang_code from voice prefix; number/acronym rules |
| [_shared_patterns.md](_inspiration/_shared_patterns.md) | All | Console, start/pause/resume, FFmpeg, settings namespaces |
| [_video_conversion_pseudo_logic.md](_inspiration/_video_conversion_pseudo_logic.md) | Convert | Queue + GPU compress + cut + extract; GUI in Phase 8 |
| [09-screenshot-capture.md](build-plan/09-screenshot-capture.md) ShareX source map | Capture | Tray + F2 + native region picker sidecar + save-to-folder; rewrite, do not paste GPL-3.0 C# |

---

## Open spec tensions (do not ignore in planning)

1. DESIGN_PROPOSAL §5 still mentions transcript `video_ids` and model `loaded` — **Phase 1 supersedes**.
2. APPLICATION_PURPOSE still says “three modules” — Phase 8 adds Convert; Phase 9 adds Capture; update that inspiration doc when convenient (phase specs win).
3. GUI E2E in the agent sandbox may be `[B]` + CI (`E2E-SANDBOX-NODISPLAY`).
4. DirectML / independent voice-pack UX from `_tts_pseudo_logic.md` remains out of MVP (catalog now includes ONNX FP32; load still uses DeviceType Auto/CUDA/MPS/CPU).
5. Bundled FFmpeg may lack NVENC; Convert must software-fallback (not a Phase 7 ship-gate while p7 is in flight).
