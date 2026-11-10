# MEU Registry

> **Generated view.** YAML SSOT: `.agent/context/meu-status.yaml`.
> Regenerate with: `python tools/meu_status.py render`
> Never hand-edit content inside AUTOGEN markers.

<!-- BEGIN AUTOGEN:meu-status:registry -->

## Domain (P0)

> Source: docs/build-plan/01-domain-layer.md

| MEU | Slug | Matrix | Build Plan Ref | Description | Status |
|-----|------|:------:|----------------|-------------|:------:|
| MEU-1 | `domain-scaffold` | 1.1 | [Phase 1 §Package layout](../../docs/build-plan/01-domain-layer.md#package-layout) | packages/core layout, root uv/pyproject workspace, pytest/pyright/ruff for core — no domain logic yet | ✅ approved |
| MEU-2 | `domain-enums-vos` | 1.2 | [Phase 1 §Enums + VOs](../../docs/build-plan/01-domain-layer.md#enums-domainenumspy) | domain/enums.py plus session VOs (ProgressSnapshot, SABRStatus, QueueRuntime, ModelDownloadRuntime, CookieTestResult) — no tables | ✅ approved |
| MEU-3 | `domain-entities` | 1.3 | [Phase 1 §Persistable entities](../../docs/build-plan/01-domain-layer.md#persistable-entities) | DownloadJob, DownloadArchiveEntry, TranscriptJob+Item, TTSJob, ModelVariant, Setting; relationships; progress.json conflict (items are SoT) | ✅ approved |
| MEU-4 | `domain-ports-errors` | 1.4 | [Phase 1 §Ports + errors](../../docs/build-plan/01-domain-layer.md#port-protocols) | Canonical ports (YouTube, Transcript, TTS, Media, Filesystem, ModelCatalog, UnitOfWork/repos) plus domain/errors.py including AgeRestrictedError and SABRDetectedError | ✅ approved |


## Infrastructure (P1)

> Source: docs/build-plan/02-infrastructure.md

| MEU | Slug | Matrix | Build Plan Ref | Description | Status |
|-----|------|:------:|----------------|-------------|:------:|
| MEU-5 | `infra-sqlite-uow` | 2.1 | [Phase 2 §Database + ORM](../../docs/build-plan/02-infrastructure.md#database) | SQLite WAL engine, seven tables only, mappers, repositories, SqlAlchemyUnitOfWork, append-only migrations, structlog — no STI jobs table | ✅ approved |
| MEU-6 | `infra-youtube` | 2.2 | [Phase 2 §YouTube adapter](../../docs/build-plan/02-infrastructure.md#youtube-adapter-youtubeadapterpy) | YouTubePort via yt-dlp — extract_info, extract_video_ids, download, formats, SABR detect/check, test_cookies → CookieTestResult, AgeRestrictedError | ✅ approved |
| MEU-7 | `infra-transcript` | 2.3 | [Phase 2 §Transcript adapter](../../docs/build-plan/02-infrastructure.md#transcript-adapter-transcriptadapterpy) | TranscriptPort via youtube-transcript-api — get_transcript returns None for missing/disabled; TranscriptRetryableError for transients | ✅ approved |
| MEU-8 | `infra-filesystem-media` | 2.4 | [Phase 2 §Filesystem + Media](../../docs/build-plan/02-infrastructure.md#filesystem-adapter-filesystemwriterpy) | FilesystemPort (atomic write, compile-only read_text, channel dirs, WAV) and MediaPort (FFmpeg setting→bundle→PATH, convert, probe) | ✅ approved |
| MEU-9 | `infra-tts-models` | 2.5 | [Phase 2 §TTS + Model manager](../../docs/build-plan/02-infrastructure.md#tts-adapter-ttsadapterpy) | TTSPort (Kokoro load/generate/voices) and ModelCatalogPort (HF download + sideload); seed ONNX FP32 catalog row; no ModelFetchJob | ✅ approved |


## Service layer (P1)

> Source: docs/build-plan/03-service-layer.md

| MEU | Slug | Matrix | Build Plan Ref | Description | Status |
|-----|------|:------:|----------------|-------------|:------:|
| MEU-10 | `svc-download` | 3.1 | [Phase 3 §DownloadService](../../docs/build-plan/03-service-layer.md#downloadservice) | DownloadService worker, session QueueRuntime, SABR session + apply_lock, archive skip, apply_defaults_to_pending, AgeRestricted mapping | ✅ approved |
| MEU-11 | `svc-transcript` | 3.2 | [Phase 3 §TranscriptService](../../docs/build-plan/03-service-layer.md#transcriptservice) | TranscriptService resolve/items, start=Pending only, resume=Paused, retry_failed_channel, Stop→Cancelled, compile/zip, progress.json export-only | ✅ approved |
| MEU-12 | `svc-tts-models` | 3.3 | [Phase 3 §TTS + Prepare + Models](../../docs/build-plan/03-service-layer.md#ttsservice) | TextPreparationService, TTSService (text body, source_path metadata), ModelService + session ModelDownloadRuntime — no ModelFetchJob | ✅ approved |
| MEU-13 | `svc-settings-health` | 3.4 | [Phase 3 §Settings + Health](../../docs/build-plan/03-service-layer.md#settingsservice) | SettingsService leaf keys extra=forbid; HealthService sole seq allocator, console ring, dependency probe (yt-dlp/FFmpeg) | ✅ approved |
| MEU-62 | `svc-tts-runtime-assets` | 3.5 | [Phase 3 §TTS runtime assets (residual)](../../docs/build-plan/03-service-layer.md#tts-runtime-assets-residual) | ONNX vocab (config.json) downloaded with each ONNX variant and wired into KokoroAdapter; spaCy en_core_web_sm as a managed download with a readiness row; tts.generate/_failed structured logs; generate fails fast with a named missing asset. Human-approved D-22. | ✅ approved |
| MEU-73 | `svc-tts-voice-assets` | 3.6 | [Phase 3 §TTS voice assets (residual)](../../docs/build-plan/03-service-layer.md#tts-voice-assets-residual) | Kokoro voice packs become managed assets with fail-fast 409 instead of a mid-run Hugging Face fetch; Settings Dependencies refreshes after asset downloads; spaCy dir appended to sys.path. | ✅ approved |
| MEU-74 | `svc-tts-language-runtime` | 3.7 | [Phase 3 §TTS language runtime (residual)](../../docs/build-plan/03-service-layer.md#tts-language-runtime-residual) | espeak-ng never bundled; a user-installed copy is detected as a readiness row; voices report available/reason and the TTS page disables unavailable ones; generate with an unavailable voice is 409. | ✅ approved |
| MEU-75 | `svc-tts-device-fallback` | 3.8 | [Phase 3 §TTS device resolution (residual)](../../docs/build-plan/03-service-layer.md#tts-device-resolution-residual) | PyTorch load on an unavailable device falls back to CPU like ONNX with a logged downgrade; the device list comes from the runtime; unmapped load failures raise ModelLoadError. | ✅ approved |
| MEU-77 | `svc-tts-async-generate` | 3.9 | [Phase 3 §TTS async generation (residual)](../../docs/build-plan/03-service-layer.md#tts-async-generation-residual) | POST /tts/generate queues and returns the job; synthesis runs in the background; DELETE /tts/{id} cancels a running job; MCP returns the job and the audit baseline gains poll/cancel; GUI run bar polls. | ✅ approved |
| MEU-78 | `svc-ffmpeg-resolver` | 3.10 | [Phase 3 §FFmpeg resolution (residual)](../../docs/build-plan/03-service-layer.md#ffmpeg-resolution-residual) | One ffmpeg resolver (configured, bundled, PATH) for Convert, TTS MP3, health and yt-dlp ffmpeg_location; re-resolves on setting change; the Dependencies row reports the resolved binary and checks ffprobe. | ✅ approved |
| MEU-98 | `svc-tts-sideload-load` | 3.11 | [Phase 3 §TTS sideload load (residual)](../../docs/build-plan/03-service-layer.md#tts-sideload-load-residual) | A sideloaded model file found in tts.models_directory is marked downloaded with its path, ModelService.load resolves that path, and a load failure is logged as tts.load_failed like the adapter's other load failures. | ✅ approved |
| MEU-115 | `svc-transcript-failure-reason` | 3.12 | [Phase 3 §Transcript failure reason (residual)](../../docs/build-plan/03-service-layer.md#transcript-failure-reason-residual) | Each transcript failure or skip maps to a short av-kit message that reaches the API, the job card and the Console; the Console keeps the model and the error text. | ✅ approved |
| MEU-116 | `svc-transcript-block-stop` | 3.13 | [Phase 3 §Transcript block stop (residual)](../../docs/build-plan/03-service-layer.md#transcript-block-stop-residual) | A blocked video that exhausts its retries stops the run and pauses the job with the reason; requests_per_hour becomes a rolling cap over real requests. | ✅ approved |
| MEU-117 | `svc-tts-build-capability` | 3.14 | [Phase 3 §TTS build capability (residual)](../../docs/build-plan/03-service-layer.md#tts-build-capability-residual) | A build that can't import a variant's runtime lists it disabled with a reason and refuses its download with a 409; the dev venv keeps working. | ✅ approved |
| MEU-119 | `svc-tts-load-keeps-model` | 3.15 | [Phase 3 §TTS load keeps the current model (residual)](../../docs/build-plan/03-service-layer.md#tts-load-keeps-model-residual) | load_model checks the weight path, the device and the runtime before it unloads, so a failed check keeps the current model. | ✅ approved |
| MEU-121 | `svc-tts-fp16-nonfinite` | 3.16 | [Phase 3 §TTS ONNX FP16 audio (residual)](../../docs/build-plan/03-service-layer.md#tts-onnx-fp16-audio-residual) | A fresh install preselects ONNX INT8 rather than FP16, and the cause of FP16's non-finite audio is looked for with a fixed sentence set. | ✅ approved |
| MEU-122 | `svc-transcript-metadata` | 3.17 | [Phase 3 §Transcript source metadata (residual)](../../docs/build-plan/03-service-layer.md#transcript-source-metadata-residual) | Transcript titles and the channel name come from the flat enumeration add_channel already runs, with the video ID and today's title as fallbacks. | ✅ approved |
| MEU-127 | `svc-tts-fp16-phase-guard` | 3.18 | [Phase 3 §TTS FP16 phase guard (residual)](../../docs/build-plan/03-service-layer.md#tts-fp16-phase-guard-residual) | A spike counts FP16's zero denominators at the decoder's phase Div and tries a guarded phase computation on a copy of the graph; what ships comes back to Mat. | ⬜ pending |


## REST API (P2)

> Source: docs/build-plan/04-rest-api.md

| MEU | Slug | Matrix | Build Plan Ref | Description | Status |
|-----|------|:------:|----------------|-------------|:------:|
| MEU-14 | `api-app-auth` | 4.1 | [Phase 4 §App factory + auth](../../docs/build-plan/04-rest-api.md#app-factory-and-lifespan) | create_app, lifespan, dual Bearer (GUI nonce vs MCP token), ErrorEnvelope, extra=forbid, list {items, processor}, static paths before {id} | ✅ approved |
| MEU-15 | `api-downloads-health-settings` | 4.2 | [Phase 4 §Downloads + Health + Settings](../../docs/build-plan/04-rest-api.md#routes--downloads) | Download/SABR/cookies/apply-defaults routes plus settings and health/console/dependencies; 422/409 mapping | ✅ approved |
| MEU-16 | `api-transcripts-tts-models` | 4.3 | [Phase 4 §Transcripts + TTS + Models](../../docs/build-plan/04-rest-api.md#routes--transcripts) | Transcript start/resume/retry/requeue/compile, TTS generate/prepare, models download-runtime; OpenAPI committed | ✅ approved |
| MEU-76 | `api-error-surface` | 4.4 | [Phase 4 §Unhandled errors (residual)](../../docs/build-plan/04-rest-api.md#unhandled-errors-residual) | Unhandled exceptions are logged with request_id and returned as a CORS-safe internal_error envelope (no more 'Failed to fetch'); yt-dlp extract failures on download add map to a typed DomainError. | ✅ approved |


## MCP server (P2)

> Source: docs/build-plan/05-mcp-server.md

| MEU | Slug | Matrix | Build Plan Ref | Description | Status |
|-----|------|:------:|----------------|-------------|:------:|
| MEU-17 | `mcp-runtime` | 5.1 | [Phase 5 §Runtime](../../docs/build-plan/05-mcp-server.md#runtime) | mcp-server scaffold, discovery (AVKIT_API_BASE optional; else backend.json), AVKIT_API_TOKEN, REST client, no SQLite | ✅ approved |
| MEU-18 | `mcp-tools` | 5.2 | [Phase 5 §Compound tools](../../docs/build-plan/05-mcp-server.md#compound-tools) | Compound avkit_* + action, Zod .strict(), confirm on destructive, REST parity; omit GUI-only console | ✅ approved |
| MEU-68 | `mcp-live-audit` | 5.3 | [Phase 5 §MCP live audit (residual)](../../docs/build-plan/05-mcp-server.md#mcp-live-audit-residual) | /mcp-audit workflow + skill + runner that drives the built server as a real stdio client against the live local API, executes every compound-tool action in dependency order, asserts observable state, diffs a committed baseline, and cleans up. Adapted from the Zorivest skill. | ✅ approved |


## GUI (P2)

> Source: docs/build-plan/06-gui.md

| MEU | Slug | Matrix | Build Plan Ref | Description | Status |
|-----|------|:------:|----------------|-------------|:------:|
| MEU-19 | `gui-shell` | 6.1 | [Phase 6 §Startup + IPC](../../docs/build-plan/06-gui.md#loading--startup-performance-tracked) | Electron splash/main, requestSingleInstanceLock, live-identity orphan reap (no attach), preload IPC, apiFetch 204, AppShell, ConsolePanel seq/ipc | ✅ approved |
| MEU-20 | `gui-downloader` | 6.2 | [Phase 6 §Downloader page](../../docs/build-plan/06-gui.md#downloader-page---default-route) | Downloader page — queue table, SABR, cookies test, start/pause/resume, TanStack Query v5 polling of {items, processor} | ✅ approved |
| MEU-26 | `gui-chrome-zorivest` | 6.2a | [Phase 6 §Main window layout + console chrome](../../docs/build-plan/06-gui.md#main-window-layout) | Zorivest-derived shell chrome — tokens, pinned rail, header Console, right side-sheet console, Settings headings | ✅ approved |
| MEU-27 | `gui-console-polish` | 6.2b | [Phase 6 §Console panel (right side sheet)](../../docs/build-plan/06-gui.md#console-panel-right-side-sheet) | Console polish — Zorivest header-left expand/collapse, contained viewport, exclusive exact-level buttons, black/green output | ✅ approved |
| MEU-21 | `gui-transcript` | 6.3 | [Phase 6 §Transcript page](../../docs/build-plan/06-gui.md#transcript-page-transcript) | Transcript cards bound to video_count/item aggregates; start/resume/retry/requeue; output tree at job.output_dir/raw|compiled | ✅ approved |
| MEU-22 | `gui-tts-models` | 6.4 | [Phase 6 §TTS + Model Manager](../../docs/build-plan/06-gui.md#tts-page-tts) | TTS editor, prepare, generate/cancel, readTextFile dialog-only, tts.output_path ~/Documents; Model Manager download-runtime rows | ✅ approved |
| MEU-23 | `gui-settings-help` | 6.5 | [Phase 6 §Settings + Help + audit](../../docs/build-plan/06-gui.md#settings-page-settings) | Settings cards, Browse actions, copyMcpConfig (no token to renderer), HelpCards, command registry, bidirectional gui-actions-index audit, E2E waves | ✅ approved |
| MEU-61 | `gui-login-item` | 6.6 | [Phase 6 §Startup (login item)](../../docs/build-plan/06-gui.md#startup-login-item) | Per-user Electron login item (Start av-kit when I sign in + Start minimized). OS is SoT. Not a Windows service. Hidden when unpackaged or Linux. NSIS uninstall DeleteRegValue. | ✅ approved |
| MEU-69 | `gui-header-toggle-state` | 6.7 | [Phase 6 §Header toggles (residual)](../../docs/build-plan/06-gui.md#header-toggles-residual) | Console header control becomes an aria-pressed toggle with icon and pressed styling; palette control reads Commands Ctrl+K with an icon; both render as buttons. | ✅ approved |
| MEU-93 | `gui-path-fields` | 6.8 | [Phase 6 §Path fields (residual)](../../docs/build-plan/06-gui.md#path-fields-residual) | Every page field that edits a folder path uses the PathRow primitive with Browse (showDirectoryDialog); Convert Output folder gains Browse, and the TTS output path becomes PathRow readOnly. | ✅ approved |
| MEU-94 | `gui-theme-reactive-selects` | 6.9 | [Phase 6 §Theme-reactive selects (residual)](../../docs/build-plan/06-gui.md#theme-reactive-selects-residual) | G30 select styles follow the live theme — one reactive theme hook behind getG30Styles/SelectInput, the ConsolePanel copy removed, a theme-aware option-menu pair, the persisted theme applied before first paint, and a both-theme Electron test. | ✅ approved |
| MEU-95 | `gui-shortcut-binding` | 6.10 | [Phase 6 §Shortcut binding (residual)](../../docs/build-plan/06-gui.md#shortcut-binding-residual) | The AppShell keydown map is generated from the command registry shortcut field, so Ctrl+1..5, Ctrl+, and Ctrl+B are bound as advertised and a displayed shortcut is always bound. | ✅ approved |
| MEU-96 | `gui-command-palette-curation` | 6.11 | [Phase 6 §Command palette curation (residual)](../../docs/build-plan/06-gui.md#command-palette-curation-residual) | Context-aware palette (global commands plus the current page, unavailable commands hidden, Pause/Resume merged), Appearance Dark and Light commands on Ctrl+Shift+D/L, destructive commands through ConfirmModal, plain labels; gui-actions-index Palette column amended. | ✅ approved |
| MEU-97 | `gui-common-shortcuts` | 6.12 | [Phase 6 §Common shortcuts (residual)](../../docs/build-plan/06-gui.md#common-shortcuts-residual) | Core shortcut set — Ctrl+L focus URL, Ctrl+Enter page primary action, Ctrl+O Convert Browse, Ctrl+S save capture, Ctrl+J console, F1 help, shown in tooltips and aria-keyshortcuts, with no collision with Capture Ctrl+=/-/0 or the F2 hotkey. | ✅ approved |
| MEU-108 | `gui-ready-probe-guard` | 6.13 | [Phase 6 §Ready probe (residual)](../../docs/build-plan/06-gui.md#ready-probe-residual) | The main process queries the backend process only for output that carries a usable AVKIT_READY line, so ordinary backend logging no longer blocks the window. | ✅ approved |
| MEU-118 | `gui-tts-device-options` | 6.14 | [Phase 6 §TTS device options (residual)](../../docs/build-plan/06-gui.md#tts-device-options-residual) | The Settings device select offers only what the backend reports for this build. | ✅ approved |
| MEU-120 | `gui-models-dir-probe` | 6.15 | [Phase 6 §Models folder probe (residual)](../../docs/build-plan/06-gui.md#models-folder-probe-residual) | The first-run probe tests the backend's real models folder and stops creating an empty one; a contract test ties the two defaults together. | ✅ approved |
| MEU-124 | `download-received-quality` | 6.16 | [Phase 6 §Downloader received quality (residual)](../../docs/build-plan/06-gui.md#download-received-quality-residual) | The file's real quality is stored in a new nullable field, and the row shows requested and received together only when they differ. | ✅ approved |
| MEU-126 | `gui-light-accent-contrast` | 6.17 | [Phase 6 §Light accent contrast (residual)](../../docs/build-plan/06-gui.md#light-accent-contrast-residual) | The light theme's accent tokens move to the colours Mat ruled, so button labels reach AA contrast. | ✅ approved |


## Distribution (P2)

> Source: docs/build-plan/07-distribution.md

| MEU | Slug | Matrix | Build Plan Ref | Description | Status |
|-----|------|:------:|----------------|-------------|:------:|
| MEU-24 | `dist-backend` | 7.1 | [Phase 7 §Backend packaging](../../docs/build-plan/07-distribution.md#backend-packaging-pyinstaller) | PyInstaller onedir, backend.json (no secrets), live-identity fields, dual --token/--mcp-token, --port 0, AVKIT_READY | ✅ approved |
| MEU-25 | `dist-installer` | 7.2 | [Phase 7 §NSIS + FFmpeg + MCP](../../docs/build-plan/07-distribution.md#electron-packaging-electron-builder) | NSIS extraResources (avkit-backend, ffmpeg, mcp-server), FFmpeg bundle, Copy MCP omits AVKIT_API_BASE; no CUDA/weights | ✅ approved |
| MEU-71 | `gui-mcp-setup-prompt` | 7.3 | [Phase 7 §MCP setup prompt (residual)](../../docs/build-plan/07-distribution.md#mcp-setup-prompt-residual) | Settings MCP card shows a per-client setup prompt (user scope by default, project option) whose command is the app executable with ELECTRON_RUN_AS_NODE=1 and the server path in args; no token in any block (the server reads mcp-token.txt) but always AVKIT_APP_DATA; backup-and-merge, verify via authenticated avkit_health dependencies, one RESULT line; fixes the mcp-server entry guard. | ✅ approved |
| MEU-72 | `dist-tts-onnx-runtime` | 7.4 | [Phase 7 §Packaged ONNX TTS runtime (residual)](../../docs/build-plan/07-distribution.md#packaged-onnx-tts-runtime-residual) | The ONNX TTS path runs G2P + onnxruntime without kokoro.KPipeline or torch so the packaged app synthesizes; hiddenimports for the G2P stack; packaged smoke generate (also records the shipped MCP entry). | ✅ approved |
| MEU-92 | `dist-mcp-server-bundle` | 7.5 | [Phase 7 §MCP server bundle (residual)](../../docs/build-plan/07-distribution.md#mcp-server-bundle-residual) | Self-contained esbuild bundle of the MCP server (index.mjs plus LICENSES.txt) that the packaged app ships as resources/mcp-server; MCP_ENTRY_PROBE on a freshly built win-unpacked tree is a pass condition. | ✅ approved |
| MEU-110 | `dist-release-candidate` | 7.6 | [Phase 7 §Release candidate packaging (residual)](../../docs/build-plan/07-distribution.md#release-candidate-packaging-residual) | Release candidate 1 packaging with a generated licence list, one version on every surface, a real NSIS installer with packaged checks, release notes and a publish checklist. | ✅ approved |
| MEU-113 | `dist-fetch-exit-codes` | 7.7 | [Phase 7 §Fetch script exit codes (residual)](../../docs/build-plan/07-distribution.md#fetch-exit-codes-residual) | The fetch script returns its documented exit codes 2 to 5, and the tests assert them. | ✅ approved |
| MEU-114 | `dist-uninstall-installer-copy` | 7.8 | [Phase 7 §Uninstall removes the installer copy (residual)](../../docs/build-plan/07-distribution.md#uninstall-installer-copy-residual) | customUnInstall deletes the installer copy electron-builder leaves in av-kit-ui-updater, skipping an in-place update. | ✅ approved |
| MEU-125 | `dist-release-candidate-2` | 7.9 | [Phase 7 §Second release candidate (residual)](../../docs/build-plan/07-distribution.md#second-release-candidate-residual) | The 0.1.0-rc.2 version, clean build, packaged checks, gate, notes and publish checklist; nothing publishes. | ✅ approved |


## Video conversion (P2)

> Source: docs/build-plan/08-video-conversion.md

| MEU | Slug | Matrix | Build Plan Ref | Description | Status |
|-----|------|:------:|----------------|-------------|:------:|
| MEU-28 | `domain-conversion` | 8.1 | [Phase 8 §Domain](../../docs/build-plan/08-video-conversion.md#domain) | ConversionKind/Status/presets, ConversionJob entity, GPUCapabilities VO, additive MediaPort (encode/cut/extract/detect_gpu); TTS/download convert() unchanged | ✅ approved |
| MEU-29 | `infra-conversion` | 8.2 | [Phase 8 §Infrastructure](../../docs/build-plan/08-video-conversion.md#infrastructure) | conversion_jobs eighth table (append-only migration), FFmpegAdapter encode/cut/extract/gpu/progress parse; no wmic | ✅ approved |
| MEU-30 | `svc-conversion` | 8.3 | [Phase 8 §Service layer](../../docs/build-plan/08-video-conversion.md#service-layer) | ConversionService sequential GPU queue, start/pause/resume/cancel, skip-existing, output suffix; not used for TTS MP3 | ✅ approved |
| MEU-31 | `api-conversion` | 8.4 | [Phase 8 §REST API](../../docs/build-plan/08-video-conversion.md#rest-api) | /api/v1/conversions envelope routes, converter settings namespace, extra=forbid, OpenAPI regen | ✅ approved |
| MEU-32 | `mcp-convert` | 8.5 | [Phase 8 §MCP](../../docs/build-plan/08-video-conversion.md#mcp) | Compound avkit_convert + action, Zod .strict(), confirm on remove/clear, REST parity | ✅ approved |
| MEU-33 | `gui-convert` | 8.6 | [Phase 8 §Convert page](../../docs/build-plan/08-video-conversion.md#convert-page-convert) | Convert rail below TTS, Downloader-shaped queue, presets, HelpCard, Wave 8 E2E, action-index audit | ✅ approved |
| MEU-109 | `convert-output-folder` | 8.7 | [Phase 8 §Output folder (residual)](../../docs/build-plan/08-video-conversion.md#output-folder-residual) | Encode, cut and extract create the output folder before FFmpeg starts, so a first Convert job into the default folder succeeds and a folder that cannot be created names the path. | ✅ approved |
| MEU-112 | `convert-job-gpu-preference` | 8.8 | [Phase 8 §Encoder choice per job (residual)](../../docs/build-plan/08-video-conversion.md#job-encoder-choice-residual) | The encoder chosen for one Compress job reaches FFmpeg, survives a re-queue or a restart, and an existing database upgrades in place. The setting still applies when a job sends nothing. | ✅ approved |
| MEU-123 | `convert-extract-stream-index` | 8.9 | [Phase 8 §Extract stream index (residual)](../../docs/build-plan/08-video-conversion.md#extract-stream-index-residual) | stream_index is audio-relative everywhere, so extract picks the right extension and tracks; an Extract job saves no encoder. | ✅ approved |
| MEU-133 | `convert-media-probe` | 8.10 | [Phase 8 §Media probe (residual)](../../docs/build-plan/08-video-conversion.md#media-probe-residual) | POST /conversions/probe and avkit_convert probe return a local video's duration, codecs, size, fps and streams through the existing MediaPort.probe. | ⬜ pending |


## Screenshot capture (P2)

> Source: docs/build-plan/09-screenshot-capture.md

| MEU | Slug | Matrix | Build Plan Ref | Description | Status |
|-----|------|:------:|----------------|-------------|:------:|
| MEU-34 | `domain-capture` | 9.1 | [Phase 9 §Domain](../../docs/build-plan/09-screenshot-capture.md#domain) | CaptureSource/RequestStatus/AnnotationType, CaptureShot + CaptureRequest, ScreenCapturePort + ImageAnnotatePort; no QueueRuntime for captures | ✅ approved |
| MEU-35 | `infra-capture` | 9.2 | [Phase 9 §Infrastructure](../../docs/build-plan/09-screenshot-capture.md#infrastructure) | capture_shots + capture_requests tables, Pillow bake + mss/ImageGrab adapter; append-only migration | ✅ approved |
| MEU-36 | `svc-capture` | 9.3 | [Phase 9 §Service layer](../../docs/build-plan/09-screenshot-capture.md#service-layer) | CaptureService inbox scan/upsert/prune, interactive 409, annotate bake, delete files | ✅ approved |
| MEU-37 | `api-capture` | 9.4 | [Phase 9 §REST API](../../docs/build-plan/09-screenshot-capture.md#rest-api) | /api/v1/captures catalog routes, capture settings namespace, image GET, extra=forbid, OpenAPI regen | ✅ approved |
| MEU-38 | `mcp-capture` | 9.5 | [Phase 9 §MCP](../../docs/build-plan/09-screenshot-capture.md#mcp) | Compound avkit_capture + action, Zod .strict(), confirm on remove (deletes files), image may return PNG | ✅ approved |
| MEU-39 | `gui-capture` | 9.6 | [Phase 9 §Capture page](../../docs/build-plan/09-screenshot-capture.md#capture-page-capture) | Tray + F2 overlay, Capture rail below Convert, filmstrip + four tools, HelpCard, Wave 9 E2E, action-index audit | ✅ approved |
| MEU-40 | `native-region-picker` | 9.7 | [Phase 9 §Native region picker (helper process)](../../docs/build-plan/09-screenshot-capture.md#native-region-picker-helper-process) | Native C# WinForms (.NET 8) region-picker sidecar replaces the Chromium overlay: freeze-before-show GDI capture, Electron lifecycle + collision-safe publication, Chromium overlay deleted with no fallback | ✅ approved |
| MEU-59 | `gui-capture-annotate-arrow-text` | 9.8 | [Phase 9 §Annotation geometry (arrow + text)](../../docs/build-plan/09-screenshot-capture.md#annotation-geometry-arrow-text) | Repair Capture-page arrow pointer and text overlays — fit-to-viewport image-pixel mapping, SVG preview matching Pillow bake, sidecar reload on GET detail, original PNG immutable. No new annotation types. | ✅ approved |
| MEU-60 | `gui-capture-annotate-edit-until-save` | 9.9 | [Phase 9 §Annotation edit until Save](../../docs/build-plan/09-screenshot-capture.md#annotation-edit-until-save) | Select-mode Capture overlay editing until Save — arrow body and independent endpoints, move committed text / box / highlight, compact mark list, Apply/Cancel color plus original-image sampler. No new annotation types. No REST/MCP schema fork. | ✅ approved |
| MEU-65 | `gui-capture-toolbar-icons` | 9.10 | [Phase 9 §Viewport toolbar icons and Options](../../docs/build-plan/09-screenshot-capture.md#viewport-toolbar-icons-and-options) | Capture toolbar becomes icon buttons with tooltips and aria-pressed; per-tool options move to a contextual row; header 'Settings' disclosure becomes an 'Options' button; no horizontal scroll at the default window size. | ✅ approved |
| MEU-66 | `gui-capture-zoom` | 9.11 | [Phase 9 §Viewport zoom](../../docs/build-plan/09-screenshot-capture.md#viewport-zoom) | Wheel and +/-/Fit zoom about the cursor with pan; FIT_MAP extended with scale and offset so MEU-59/60 pointer mapping stays exact; stored annotations unchanged. | ✅ approved |
| MEU-67 | `capture-flatten-backup` | 9.12 | [Phase 9 §Flatten with backup](../../docs/build-plan/09-screenshot-capture.md#flatten-with-backup) | POST /captures/{id}/flatten bakes annotations over the original after copying it to a backup folder; /revert restores; capture.flatten_backup and capture.backup_dir settings; MCP flatten/revert with confirm; GUI Apply-to-image with confirm strip. | ✅ approved |
| MEU-80 | `gui-icon-button-hints` | 9.13 | [Phase 9 §Icon-button hints](../../docs/build-plan/09-screenshot-capture.md#icon-button-hints) | Shared rendered tooltip for icon-only function buttons (hover and focus, including disabled), generalising Session 30 A-10; nav-rail labels out of scope. | ✅ approved |
| MEU-81 | `gui-capture-action-row` | 9.14 | [Phase 9 §Capture action row](../../docs/build-plan/09-screenshot-capture.md#capture-action-row) | Per-shot/per-mark actions as icon buttons; Body/Tail/Head, nudge buttons and Sample original removed; row shrink-0 with no overflow; hotkey status inline in the header (no reserved band). | ✅ approved |
| MEU-82 | `capture-text-baseline` | 9.15 | [Phase 9 §Text preview baseline](../../docs/build-plan/09-screenshot-capture.md#text-preview-baseline) | SVG text on the alphabetic baseline from the bake's Segoe metrics so preview, plate and bake share one anchor; preview-vs-bake pixel test. | ✅ approved |
| MEU-83 | `capture-arrow-geometry` | 9.16 | [Phase 9 §Arrow bake geometry](../../docs/build-plan/09-screenshot-capture.md#arrow-bake-geometry) | Arrow shaft ends at the back of the head in bake and preview; arrows baked at 4x with LANCZOS downscale. | ✅ approved |
| MEU-84 | `capture-file-variant-sync` | 9.17 | [Phase 9 §Annotated file sync and Open file](../../docs/build-plan/09-screenshot-capture.md#annotated-file-sync-and-open-file) | scan_inbox clears missing annotated/sidecar paths; Open file and Open folder follow the viewport's Original/Annotated view. | ✅ approved |
| MEU-85 | `gui-capture-size-scrub` | 9.18 | [Phase 9 §Size scrubbing](../../docs/build-plan/09-screenshot-capture.md#size-scrubbing) | Stroke width and font size scrub by dragging the label, wheel and arrow keys, with live preview and one undo per gesture. | ✅ approved |
| MEU-86 | `gui-capture-color-swatches` | 9.19 | [Phase 9 §Named colour swatches](../../docs/build-plan/09-screenshot-capture.md#named-colour-swatches) | Named colour options show their colour with contrast-picked text, or a swatch popover if the target ignores option backgrounds. | ✅ approved |
| MEU-87 | `gui-capture-tool-lock` | 9.20 | [Phase 9 §Tool lock](../../docs/build-plan/09-screenshot-capture.md#tool-lock) | Auto-Select after drawing stays the default; a visible tool lock keeps the current tool across marks. | ✅ approved |
| MEU-88 | `gui-capture-filmstrip-menu` | 9.21 | [Phase 9 §Filmstrip context menu](../../docs/build-plan/09-screenshot-capture.md#filmstrip-context-menu) | Thumbnail right-click menu: Copy full path, Copy image (main-process clipboard via preload), Delete with the existing confirm. | ✅ approved |
| MEU-89 | `gui-capture-filmstrip-multiselect` | 9.22 | [Phase 9 §Filmstrip multi-select](../../docs/build-plan/09-screenshot-capture.md#filmstrip-multi-select) | Shift-click range selection; batch Delete with one confirm and per-shot failure reporting. | ✅ approved |
| MEU-90 | `capture-pixelate-mark` | 9.23 | [Phase 9 §Pixelate mark](../../docs/build-plan/09-screenshot-capture.md#pixelate-mark) | New pixelate rectangle mark across domain, sidecar, OpenAPI/MCP and editor; bake downscale + nearest-neighbour upscale, default 10 px blocks, live preview. | ✅ approved |
| MEU-91 | `capture-eraser-mark` | 9.24 | [Phase 9 §Eraser mark](../../docs/build-plan/09-screenshot-capture.md#eraser-mark) | New eraser rectangle mark filled with the colour sampled from its border for every format. | ✅ approved |
| MEU-99 | `gui-capture-history-chords` | 9.25 | [Phase 9 §Canvas history chords](../../docs/build-plan/09-screenshot-capture.md#canvas-history-chords) | Ctrl+Z undoes and Ctrl+Y or Ctrl+Shift+Z redoes on the Capture canvas, renderer-local with preventDefault, while text fields keep their native undo; Undo and Redo show the chords. | ✅ approved |
| MEU-100 | `gui-capture-resize-handles` | 9.26 | [Phase 9 §Resize handles](../../docs/build-plan/09-screenshot-capture.md#resize-handles) | A selected box, highlight, pixelate or eraser mark shows 8 screen-constant handles; a handle drag resizes it with the opposite edge fixed, normalized and clamped, as one undo step. | ✅ approved |
| MEU-101 | `gui-capture-text-reedit` | 9.27 | [Phase 9 §Text re-edit and scaling](../../docs/build-plan/09-screenshot-capture.md#text-re-edit-and-scaling) | Double-click or Enter re-opens a committed text mark for editing, Escape restores it, and the text plate's corner handles scale its font size, each as one undo step. | ✅ approved |
| MEU-102 | `capture-text-multiline` | 9.28 | [Phase 9 §Multi-line text](../../docs/build-plan/09-screenshot-capture.md#multi-line-text) | Shift+Enter adds a line to a text mark; newline semantics, multi-line Segoe metrics and bake fixtures keep the preview and the bake in agreement. | ⬜ pending |
| MEU-103 | `capture-redact-mark` | 9.29 | [Phase 9 §Redact mark](../../docs/build-plan/09-screenshot-capture.md#redact-mark) | A new solid redact mark baked in the region pass, a Redact tool with a Solid or Pixelate toggle, the Smart eraser rename and dashed editor-only outlines. | ⬜ pending |
| MEU-104 | `capture-copy-image-actions` | 9.30 | [Phase 9 §Copy image and action names](../../docs/build-plan/09-screenshot-capture.md#copy-image-and-action-names) | Copy image renders the current marks through a render endpoint to the clipboard from a button or canvas Ctrl+C, and the action row reads Save annotations, Flatten into image and Restore backup. | ⬜ pending |
| MEU-105 | `gui-capture-style-tool-flow` | 9.31 | [Phase 9 §Style and tool flow](../../docs/build-plan/09-screenshot-capture.md#style-and-tool-flow) | Colour applies on click, each tool keeps its own persisted style, Lock is on by default, letter shortcuts pick tools, and Shift, Alt and Shift+arrow modify drawing and nudging. | ⬜ pending |
| MEU-106 | `capture-line-ellipse-shapes` | 9.32 | [Phase 9 §Line and ellipse](../../docs/build-plan/09-screenshot-capture.md#line-and-ellipse) | Line as an arrow with no head and Ellipse as a rect shape, with 45 degree snap and Ctrl+D duplicate. | ⬜ pending |
| MEU-107 | `capture-step-mark` | 9.33 | [Phase 9 §Step mark](../../docs/build-plan/09-screenshot-capture.md#step-mark) | A new numbered step mark for how-to screenshots, drawn, moved and baked like the other marks. | ⬜ pending |
| MEU-111 | `mcp-image-fits-stdio` | 9.34 | [Phase 5 §Image size limit (residual)](../../docs/build-plan/05-mcp-server.md#image-size-limit-residual) | avkit_capture image never sends an image the MCP stdio client cannot read. Above 7,800,000 B it returns a tool error that names the file's path and the connection stays up. | ✅ approved |
| MEU-128 | `capture-region-view` | 9.35 | [Phase 9 §Region view](../../docs/build-plan/09-screenshot-capture.md#region-view) | GET image and MCP image take an optional region in original px or fractions, clamp it, fit it inside max_edge (default 1568, upscale capped at 4x) and report the frame; no file is written. | ✅ approved |
| MEU-129 | `capture-image-import` | 9.36 | [Phase 9 §Image import](../../docs/build-plan/09-screenshot-capture.md#image-import) | POST /captures mode import and MCP import copy a local png, jpg, jpeg or webp into the inbox as a new shot (source Import), writing an upright PNG when EXIF rotates it; inbox paths register in place. | ✅ approved |
| MEU-130 | `capture-crop-copy` | 9.37 | [Phase 9 §Crop to a new shot](../../docs/build-plan/09-screenshot-capture.md#crop-to-new-shot) | POST /captures/{id}/crop and MCP crop write the region as a new PNG shot (source Crop) with exact pixels, leave the source untouched, and carry the saved marks translated and clipped. | ⬜ pending |
| MEU-131 | `gui-capture-crop-tool` | 9.38 | [Phase 9 §Crop tool](../../docs/build-plan/09-screenshot-capture.md#crop-tool) | A Crop tool on the Capture page with a full-image box with 8 handles, dimmed outside, aspect presets, X/Y/W/H fields, and Enter or Save as copy writes a new shot through the crop endpoint. | ⬜ pending |
| MEU-132 | `gui-capture-image-import` | 9.39 | [Phase 9 §GUI image import](../../docs/build-plan/09-screenshot-capture.md#gui-image-import) | Drag and drop, an Import image button and Ctrl+V paste bring images into the Capture inbox through the import endpoint or the hotkey publication path. | ⬜ pending |
| MEU-134 | `capture-video-frames` | 9.40 | [Phase 9 §Video frames](../../docs/build-plan/09-screenshot-capture.md#video-frames) | avkit_capture frames and POST /captures/frames grab frames at given times or evenly spaced from a local video as new inbox shots (CaptureSource.Video). | ⬜ pending |
| MEU-135 | `capture-video-sheet` | 9.41 | [Phase 9 §Video sheet](../../docs/build-plan/09-screenshot-capture.md#video-sheet) | avkit_capture sheet and POST /captures/sheet write one labelled grid image of a video span, sized for the vision token budget, as a new shot. | ⬜ pending |
| MEU-136 | `capture-export-copy` | 9.42 | [Phase 9 §Export copy](../../docs/build-plan/09-screenshot-capture.md#export-copy) | avkit_capture export and POST /captures/{id}/export write a resized png, jpeg or webp copy of a shot as a new shot, with no metadata. | ⬜ pending |


## Queue card UI (P2)

> Source: docs/build-plan/10-queue-card-ui.md

| MEU | Slug | Matrix | Build Plan Ref | Description | Status |
|-----|------|:------:|----------------|-------------|:------:|
| MEU-41 | `canon-queue-cards` | 10.1 | [Phase 10 §Scope and non-goals](../../docs/build-plan/10-queue-card-ui.md#scope-and-non-goals) | Phase 10 spec doc (10-queue-card-ui.md), 06-gui.md supersession pointers, --color-age-restricted + --color-bg-selected tokens ported from zorivest, AgeRestricted status-colour Spec-conformance fix | ✅ approved |
| MEU-42 | `svc-requeue-widening` | 10.2 | [Phase 10 §Re-queue contract](../../docs/build-plan/10-queue-card-ui.md#re-queue-contract) | Widen reset_failed from {Failed} to the full re-queueable set (Cancelled, QualityBlocked, AgeRestricted); transition maps; route docstrings; OpenAPI regen | ✅ approved |
| MEU-43 | `gui-queue-primitives` | 10.3 | [Phase 10 §Status token table](../../docs/build-plan/10-queue-card-ui.md#status-token-table) | Shared queue primitives StatusBadge, ProgressBar, SelectionCheckbox, ConfirmModal plus lib/queue/ (deduped formatFileSize, envelope parser, status tokens + contrast oracle, per-feature status configs) | ✅ approved |
| MEU-44 | `gui-queue-card` | 10.4 | [Phase 10 §QueueCard anatomy](../../docs/build-plan/10-queue-card-ui.md#queuecard-anatomy) | QueueCard, QueueList and EmptyDropZone row-card components with testid registration; no page mounts them yet | ✅ approved |
| MEU-45 | `gui-convert-queue` | 10.5 | [Phase 10 §Toolbar reduction](../../docs/build-plan/10-queue-card-ui.md#toolbar-reduction) | Convert queue migration to QueueList; toolbar reduced 13 to 4 + kebab overflow; testid census | ✅ approved |
| MEU-46 | `gui-downloader-queue` | 10.6 | [Phase 10 §Primary action model](../../docs/build-plan/10-queue-card-ui.md#primary-action-model) | Downloader queue migration to QueueList; summary bar; duplicate table deleted | ✅ approved |
| MEU-47 | `gui-queue-bulk` | 10.7 | [Phase 10 §Selection and bulk model](../../docs/build-plan/10-queue-card-ui.md#selection-and-bulk-model) | Selection model (Set<id>), sticky BulkActionBar, shift-click range, Ctrl/Cmd-A, client-side bulk fan-out, Clear finished, G35 partial-result toasts | ✅ approved |
| MEU-48 | `gui-queue-convergence` | 10.8 | [Phase 10 §Supersession of 06-gui.md](../../docs/build-plan/10-queue-card-ui.md#supersession-of-06-guimd) | Transcript ChannelCard onto the shared primitives (fixes the G33 width-percent violation); TTS gets the shared ProgressBar | 🚫 closed |
| MEU-49 | `gui-queue-dnd` | 10.9 | [Phase 10 §Reorder model](../../docs/build-plan/10-queue-card-ui.md#reorder-model) | dnd-kit drag reorder inside QueueList with ARIA live-region announcements; keyboard reorder retained as the equal path. Lands before Phase 11 so Transcript (MEU-55) inherits reorder by adopting QueueList. | ✅ approved |


## Page layout (P2)

> Source: docs/build-plan/11-page-layout.md

| MEU | Slug | Matrix | Build Plan Ref | Description | Status |
|-----|------|:------:|----------------|-------------|:------:|
| MEU-50 | `canon-page-layout` | 11.1 | [Phase 11 §Scope and non-goals](../../docs/build-plan/11-page-layout.md#scope-and-non-goals) | Phase 11 spec doc (11-page-layout.md) authored from the six 2026-09-03 page-layout mockups; resolves every mockup §06 open decision into a locked rule; content-column cap, zone model, form grid, disclosure/segment/chip vocabulary and save-model captions; supersession pointers into 06-gui.md, 08, 09 and 10 | ✅ approved |
| MEU-51 | `gui-layout-primitives` | 11.2 | [Phase 11 §Shared layout primitives](../../docs/build-plan/11-page-layout.md#shared-layout-primitives) | Shared layout primitives Disclosure, SegmentedControl, StatusChip, FormRow and PathRow with testid registration; consumed by five pages, no page mounts them yet | ✅ approved |
| MEU-52 | `gui-queue-header-row` | 11.3 | [Phase 11 §Queue header row](../../docs/build-plan/11-page-layout.md#queue-header-row) | QueueHeaderRow composing QueueSelectionHeader, non-zero status chips, the live processor chip and QueueToolbar into one row; lands on Downloader and Convert in the SAME MEU so the two queues cannot diverge again; queue-summary and processor-indicator ids move onto chips | ✅ approved |
| MEU-53 | `gui-downloader-layout` | 11.4 | [Phase 11 §Downloader page layout](../../docs/build-plan/11-page-layout.md#downloader-page-layout) | Downloader Zone 1 add panel — URL and Add on one row, content-width options row, Advanced disclosure holding the cookie-mode segment and the three SABR controls; SABR chip beside Quality; column cap; add-status and error-banner share one panel status line | ✅ approved |
| MEU-54 | `gui-convert-layout` | 11.5 | [Phase 11 §Convert page layout](../../docs/build-plan/11-page-layout.md#convert-page-layout) | Convert Zone 1 add panel — task segment with encoder chip and Refresh GPU, one-line drop strip with Add carrying the staged count, removable staged-path chips, single task-options row, Advanced override disclosure, output/skip-existing/Save footer | ✅ approved |
| MEU-55 | `gui-transcript-layout` | 11.6 | [Phase 11 §Transcript page layout](../../docs/build-plan/11-page-layout.md#transcript-page-layout) | Transcript Add row, channel cards on the QueueCard anatomy (inherits closed MEU-48: shared primitives plus the G33 width-percent fix), 13-button footer replaced by a three-action header toolbar plus per-card ▲ ▼ and ⋮ menu; single-select model unchanged | ✅ approved |
| MEU-56 | `gui-tts-layout` | 11.7 | [Phase 11 §TTS page layout](../../docs/build-plan/11-page-layout.md#tts-page-layout) | TTS two-column text/voice grid, Cleanup and Manage-models disclosures, one-line voice list, speed slider plus preset segment, and a single run bar (inherits closed MEU-48: TTS adopts the shared ProgressBar) | ✅ approved |
| MEU-57 | `gui-capture-layout` | 11.8 | [Phase 11 §Capture page layout](../../docs/build-plan/11-page-layout.md#capture-page-layout) | Capture header row with the hotkey key cap and a Settings disclosure, 200px thumbnail filmstrip, per-shot viewport toolbar with the tool segment, and inline confirm strips; Phase 10 excluded Capture as a queue, Phase 11 includes it as a layout | ✅ approved |
| MEU-58 | `gui-settings-layout` | 11.9 | [Phase 11 §Settings page layout](../../docs/build-plan/11-page-layout.md#settings-page-layout) | Settings sticky section rail (Pages / App / Setup), 168px label-control form grid, path-plus-Browse rows, per-section save-model captions making the three existing save models visible, and Dependencies/Readiness/MCP rendered as chip lists | ✅ approved |
| MEU-63 | `gui-tts-model-manager` | 11.10 | [Phase 11 §TTS model manager (residual)](../../docs/build-plan/11-page-layout.md#tts-model-manager-residual) | Model picker plus one state-driven Get / Load / Unload button replacing the Manage grid; run bar shows job.error_message for Failed jobs; asset readiness rows from MEU-62 visible in the picker. | ✅ approved |
| MEU-64 | `gui-tts-text-panel` | 11.11 | [Phase 11 §TTS text panel (residual)](../../docs/build-plan/11-page-layout.md#tts-text-panel-residual) | Apply cleanup writes cleaned_text back to the text; preview-raw removed and the cleaned preview shown only after Preview; searchable voice combobox replaces the full-width language select + tall listbox. | ✅ approved |
| MEU-70 | `gui-settings-section-emphasis` | 11.12 | [Phase 11 §Settings section emphasis (residual)](../../docs/build-plan/11-page-layout.md#settings-section-emphasis-residual) | After a target check of MEU-58's rail aria-current, the current section card gets a subtle surface-raised emphasis driven by the same observer state; no layout shift; all section ids kept. | ✅ approved |
| MEU-79 | `gui-tts-voice-panel-layout` | 11.13 | [Phase 11 §TTS voice panel alignment (residual)](../../docs/build-plan/11-page-layout.md#tts-voice-panel-alignment-residual) | Model, Device and the model action share one aligned row and control height with no wrap at the default window; Format, Speed and voice search match; geometry pinned in Electron. Spec in 11 §TTS voice panel alignment (residual). | ✅ approved |

<!-- END AUTOGEN:meu-status:registry -->
